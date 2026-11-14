/* BIOS do CP/M-68K para a PARAGON 50 (Tabajara Labs)
 * console = 68681 canal A ($FA0000), discos A:-D: = imagens \\CPM\\A.DSK.. no cartao SD (FAT16), P: = disco RAM
 */
typedef unsigned char  u8;
typedef unsigned short u16;
typedef unsigned long  u32;

#ifndef RXFIRST
#define RXFIRST 1500000L
#endif
#ifndef TPA_TOP
#define TPA_TOP 0x10000UL
#endif

#define SRA   (*(volatile u8  *)0xFA0003)
#define RHRA  (*(volatile u8  *)0xFA0007)
#define THRA  (*(volatile u16 *)0xFA0006)
#define SOPR  (*(volatile u16 *)0xFA001C)
#define ROPR  (*(volatile u16 *)0xFA001E)

extern char _end[];
extern void wboot_asm(void);

/* ------------------------------------------------------------ hardware */
static void strobe(void)
{
    volatile int i;
    ROPR = 4;
    SOPR = 4;
    for (i = 0; i < 20; i++) ;
    ROPR = 4;
}

static void con_put(int c)
{
    strobe();
    while (!(SRA & 4)) ;
    THRA = (u16)(c & 0xFF);
}

static void prs(const char *s) { while (*s) con_put(*s++); }

/* ------------------------------------------------------------ disco */
#define NSD     4           /* A:-D: = imagens no cartao SD */
#define NDISK   5           /* indice 4 = P: disco RAM (RAM2) */
#define SPT     32          /* setores de 128 bytes por trilha */
#define NTRK    128

struct dpb {
    u16 spt;
    u8  bsh, blm, exm, pad;
    u16 dsm, drm;
    u8  al0, al1;
    u16 cks, off;
};

struct dph {
    u32 xlt;
    u16 s0, s1, s2;
    u32 dirbuf;
    u32 dpb;
    u32 csv;
    u32 alv;
};

static u8 dirbuf[128];
static u8 alv0[40], alv1[40], alv2[40], alv3[40], alv4[40];

/* 512 KB: 256 blocos de 2 KB, 256 entradas de diretorio */
static struct dpb dpb0 = { SPT, 4, 15, 1, 0, 255, 255, 0xF0, 0x00, 0, 0 };

/* P: disco RAM em $040000, 124 KB: 124 blocos de 1 KB, 64 entradas de diretorio.
 * Os 4 KB finais ($05F000-$05FFFF) guardam a marca 'CPMR' (o disco sobrevive ao reset). */
#define RD_BASE  0x040000UL
#define RD_TRK   31
#define RD_MARK  (*(volatile u32 *)0x05F000UL)
#define RD_MAGIC 0x43504D52UL
static struct dpb dpb2 = { SPT, 3, 7, 0, 0, 123, 63, 0xC0, 0x00, 0, 0 };
static u8 ramdisk_ok;

static struct dph dphtab[NDISK];

static struct { u16 count; u32 low; u32 len; } __attribute__((packed)) memtab;

static u16 settrk, setsec, curdsk;
static u32 setdma;
static u16 iobyte;
static volatile u32 * volatile vectbase = (volatile u32 *)0;

extern int rdinit(void);
extern void rdcopy(u8 *dst, u8 *src);
#define ramdisk_init() (ramdisk_ok = (u8)rdinit())

/* ------------------------------------------------------------ cartao SD (camada de baixo nivel em sd_blob.s)
 * Todas as variaveis do SD ficam na RAM alta ($5F010-$5FAFF), sem gastar a RAM baixa do CP/M.
 * Cada disco e um arquivo \CPM\A.DSK .. D.DSK (imagem crua de 512 KB, setores de 128 bytes, sem cabecalho).
 * Na montagem guardamos a lista de clusters de cada imagem (a imagem nao precisa ser contigua).     */
extern int sd_init(void);
extern int sd_rd(u32 sector, u8 *buf);
extern int sd_wr(u32 sector, u8 *buf);

#define IMG_SECS   1024UL        /* 512 KB / 512 */
#define MAXCL      128           /* clusters por imagem (cluster >= 4 KB) */
struct sdv {
    u32 fatsec, rootsec, datasec, cursec, fbsec;
    u16 rootsz, spc, spcsh, mounted;
};
#define V      ((struct sdv *)0x5F040UL)
#define TAB(d) ((u16 *)(0x5F100UL + ((u32)(d) << 8)))   /* 4 x 128 x 2 bytes: $5F100-$5F4FF */
#define SDBUF  ((u8 *)0x5F500UL)                         /* setor de dados (cache de 1 setor) */
#define TBUF   ((u8 *)0x5F700UL)                         /* varredura de diretorio */
#define FBUF   ((u8 *)0x5F900UL)                         /* setor da FAT */

static u16 le16(const u8 *p) { return (u16)(p[0] | (p[1] << 8)); }
static u32 le32(const u8 *p) { return (u32)le16(p) | ((u32)le16(p + 2) << 16); }

static u16 fat_next(u16 cl)
{
    u32 s = V->fatsec + (cl >> 8);
    if (V->fbsec != s) {
        if (sd_rd(s, FBUF)) return 0xFFFF;
        V->fbsec = s;
    }
    return le16(FBUF + ((cl & 255) << 1));
}

/* procura 'name' (11 bytes) em nsec setores a partir de first; devolve 1 e o cluster/tamanho se achar */
static int find_ent(u32 first, u32 nsec, const char *name, u16 *cl, u32 *size)
{
    u32 s; int i, k;
    for (s = 0; s < nsec; s++) {
        if (sd_rd(first + s, TBUF)) return 0;
        for (i = 0; i < 16; i++) {
            u8 *e = TBUF + (i << 5);
            if (e[0] == 0) return 0;
            if (e[0] == 0xE5 || (e[11] & 0x0F) == 0x0F) continue;
            for (k = 0; k < 11 && e[k] == (u8)name[k]; k++) ;
            if (k == 11) { *cl = le16(e + 26); *size = le32(e + 28); return 1; }
        }
    }
    return 0;
}

static u32 clsec(u16 cl) { return V->datasec + ((u32)(cl - 2) << V->spcsh); }

/* devolve 0 = ok; 1 = sem cartao; 2 = nao e FAT16; 3 = sem a pasta CPM */
static int sd_mount(void)
{
    u8 *b = TBUF; u32 part = 0, rootent; u16 cl, rsvd, fatsz; u32 size; int d;
    V->mounted = 0;
    if (sd_init()) return 1;
    if (sd_rd(0, b)) return 1;
    if (le16(b + 11) != 512) {                       /* MBR: usa a primeira particao */
        if (b[510] != 0x55 || b[511] != 0xAA) return 2;
        part = le32(b + 0x1C6);
        if (!part || sd_rd(part, b) || le16(b + 11) != 512) return 2;
    }
    V->spc = b[13]; rsvd = le16(b + 14); rootent = le16(b + 17); fatsz = le16(b + 22);
    if (!V->spc || !fatsz || !rootent || (V->spc & (V->spc - 1))) return 2;
    for (V->spcsh = 0; (1 << V->spcsh) < V->spc; V->spcsh++) ;
    V->fatsec = part + rsvd;
    V->rootsec = V->fatsec + (u32)b[16] * fatsz;
    V->rootsz = (u16)(rootent >> 4);
    V->datasec = V->rootsec + V->rootsz;
    V->fbsec = 0xFFFFFFFFUL; V->cursec = 0xFFFFFFFFUL;
    if (!find_ent(V->rootsec, V->rootsz, "CPM        ", &cl, &size)) return 3;
    {
        u32 dir = clsec(cl);
        char nm[12]; int k;
        for (d = 0; d < NSD; d++) {
            u16 *tab = TAB(d), n, ncl;
            for (k = 0; k < 11; k++) nm[k] = ' ';
            nm[0] = (char)('A' + d); nm[8] = 'D'; nm[9] = 'S'; nm[10] = 'K'; nm[11] = 0;
            if (!find_ent(dir, V->spc, nm, &cl, &size)) continue;
            if (size < IMG_SECS * 512UL) continue;
            ncl = (u16)((IMG_SECS + V->spc - 1) >> V->spcsh);
            if (ncl > MAXCL) continue;
            for (n = 0; n < ncl; n++) {
                if (cl < 2 || cl >= 0xFFF0) break;
                tab[n] = cl;
                cl = fat_next(cl);
            }
            if (n == ncl) V->mounted |= (u16)(1 << d);
        }
    }
    return 0;
}

static __attribute__((noinline)) u32 dio_sd(int w)
{
    u32 rec = ((u32)settrk << 5) + setsec;          /* registro de 128 bytes, 0..4095 */
    u32 s = rec >> 2;
    u32 abs = clsec(TAB(curdsk)[s >> V->spcsh]) + (s & (V->spc - 1));
    u8 *p = SDBUF + ((rec & 3) << 7);
    if (V->cursec != abs) {
        V->cursec = 0xFFFFFFFFUL;
        if (sd_rd(abs, SDBUF)) return 1;
        V->cursec = abs;
    }
    if (w) {
        rdcopy(p, (u8 *)setdma);
        if (sd_wr(abs, SDBUF)) { V->cursec = 0xFFFFFFFFUL; return 1; }   /* write-through */
    } else
        rdcopy((u8 *)setdma, p);
    return 0;
}

/* ------------------------------------------------------------ BIOS */
static void biosinit(void)
{
    int i;
    u32 low = ((u32)_end + 255UL) & ~255UL;
    for (i = 0; i < NDISK; i++) {
        dphtab[i].xlt = 0;
        dphtab[i].s0 = dphtab[i].s1 = dphtab[i].s2 = 0;
        dphtab[i].dirbuf = (u32)dirbuf;
        dphtab[i].dpb = (u32)(i == 4 ? &dpb2 : &dpb0);
        dphtab[i].csv = 0;
        dphtab[i].alv = (u32)(i == 4 ? alv4 : i == 3 ? alv3 : i == 2 ? alv2 : i ? alv1 : alv0);
    }
    memtab.count = 1;
    memtab.low = low;
    {   /* monitor v2.1: RAMEND ($40C) + marca 'RAM1' ($430); sem a marca usa TPA_TOP fixo */
        u32 top = TPA_TOP, re = *(volatile u32 *)0x40CUL;
        if (*(volatile u32 *)0x430UL == 0x52414D31UL && (re & 0xFFFFUL) == 0xFFFFUL && re >= 0xFFFFUL && re < 0x100000UL) top = re + 1UL;
        memtab.len = top - low;
    }
    ramdisk_init();
    prs("\r\nCP/M-68K PARAGON 50 (Tabajara Labs)\r\n");
    V->mounted = 0;
    if (!ramdisk_ok) prs("SD: precisa da RAM em $40000\r\n");
    else {
        static const char *const em[4] = { "", "sem cartao", "cartao nao e FAT16", "falta a pasta \\CPM" };
        int r = sd_mount(), d;
        if (r) { prs("SD: "); prs(em[r]); prs("\r\n"); }
        else {
            prs("SD:");
            for (d = 0; d < NSD; d++)
                if (V->mounted & (1 << d)) { con_put(' '); con_put('A' + d); con_put(':'); }
            if (!V->mounted) prs(" nenhuma imagem A.DSK em \\CPM");
            prs("\r\n");
        }
    }
}

void biosinit_entry(void) { if (!memtab.count) biosinit(); }   /* v2.4.1: warm boot (count!=0) nao reinicializa: sem banner nem sondagem do disco */

static __attribute__((noinline)) u32 dio(int w)
{
    u8 *buf = (u8 *)setdma;
    if (setsec >= SPT || settrk >= (curdsk == 4 ? RD_TRK : NTRK)) return 1;
    if (curdsk != 4) return dio_sd(w);
    {
        u8 *m = (u8 *)(RD_BASE + (((u32)settrk << 5 | setsec) << 7));
        if (w) rdcopy(m, buf); else rdcopy(buf, m);
        return 0;
    }
}

u32 cbios(u32 fn, u32 p1, u32 p2)
{
    switch (fn) {
    case 0:  biosinit(); return 0;
    case 1:  wboot_asm(); return 0;
    case 2:  return (SRA & 1) ? 0xFFFFFFFFUL : 0;
    case 3:
        for (;;) {
            if (SRA & 1) return (u32)(RHRA & 0xFF);
            strobe();
        }
    case 4:  con_put((int)(p1 & 0xFF)); return 0;
    case 5:  return 0;
    case 6:  return 0;
    case 7:  return 0x1A;
    case 8:  settrk = 0; return 0;
    case 9:
        if (p1 == 15 && ramdisk_ok) p1 = 4;
        else if (p1 >= NSD || !(V->mounted & (1 << p1))) return 0;
        curdsk = (u16)p1;
        return (u32)&dphtab[p1];
    case 10: settrk = (u16)p1; return 0;
    case 11: setsec = (u16)p1; return 0;
    case 12: setdma = p1; return 0;
    case 13:
    case 14: return dio(fn == 14);
    case 15: return 0xFFFFFFFFUL;
    case 16: return (u32)(u16)p1;            /* sem traducao */
    case 18: return (u32)&memtab;
    case 19: return iobyte;
    case 20: iobyte = (u16)p1; return 0;
    case 21: return 0;
    case 22: {
        volatile u32 *tbl = vectbase;      /* base 0: tabela de vetores */
        u32 old = tbl[p1 & 0xFF];
        tbl[p1 & 0xFF] = p2;
        return old;
    }
    }
    return 0;
}
