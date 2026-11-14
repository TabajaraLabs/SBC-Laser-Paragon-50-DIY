/* BIOS do CP/M-68K para a PARAGON 50 (Tabajara Labs)
 * console = 68681 canal A ($FA0000), disco = servidor na ponte serial (PC)
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
#define NDISK   2
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
static u8 alv0[40], alv1[40];

/* 512 KB: 256 blocos de 2 KB, 256 entradas de diretorio */
static struct dpb dpb0 = { SPT, 4, 15, 1, 0, 255, 255, 0xF0, 0x00, 0, 0 };

static struct dph dphtab[NDISK];

static struct { u16 count; u32 low; u32 len; } __attribute__((packed)) memtab;

static u16 settrk, setsec, curdsk;
static u32 setdma;
static u16 iobyte;
static volatile u32 * volatile vectbase = (volatile u32 *)0;

/* ----- protocolo de disco pela serial:
 *  placa -> PC : ESC 01 'D' cmd drv lba2 lba1 lba0 [128 bytes se 'W'] chk
 *  PC -> placa : A5 status [128 bytes se 'R' e status=0] chk
 *  chk = (-soma) dos bytes apos ESC 01 'D'  (resp.: apos A5)
 */
static int rx_byte(long limit)
{
    long n = 0;
    for (;;) {
        if (SRA & 1) return RHRA;
        if ((++n & 0xFF) == 0) strobe();
        if (n > limit) return -1;
    }
}

static void drain(void)
{
    int k;
    for (k = 0; k < 4000; k++) {
        if (SRA & 1) { (void)RHRA; k = 0; }
    }
}

static long rxfirst = RXFIRST;
static int net_io(int write, int drv, u32 lba, u8 *buf)
{
    int tries, i, c;
    u8 sum;
    for (tries = 0; tries < 4; tries++) {
        u8 hdr[5];
        drain();
        con_put(0x1B); con_put(0x01); con_put('D');
        hdr[0] = write ? 'W' : 'R';
        hdr[1] = (u8)drv;
        hdr[2] = (u8)(lba >> 16);
        hdr[3] = (u8)(lba >> 8);
        hdr[4] = (u8)lba;
        sum = 0;
        for (i = 0; i < 5; i++) { con_put(hdr[i]); sum += hdr[i]; }
        if (write)
            for (i = 0; i < 128; i++) { con_put(buf[i]); sum += buf[i]; }
        con_put((u8)(0 - sum));

        /* espera sincronismo A5 */
        do {
            c = rx_byte(rxfirst);
        } while (c >= 0 && c != 0xA5);
        if (c < 0) continue;
        c = rx_byte(300000L);
        if (c < 0) continue;
        sum = (u8)c;
        {
            u8 status = (u8)c;
            if (!write && status == 0) {
                for (i = 0; i < 128; i++) {
                    c = rx_byte(300000L);
                    if (c < 0) break;
                    buf[i] = (u8)c; sum += (u8)c;
                }
                if (i < 128) continue;
            }
            c = rx_byte(300000L);
            if (c < 0) continue;
            sum += (u8)c;
            if (sum != 0) continue;
            return status;          /* 0 = ok */
        }
    }
    return 1;
}

static u32 lba_of(void)
{
    return (u32)settrk * SPT + setsec;
}


/* ----- troca de velocidade da serial (57600 bps por padrao; volta a 9600 se falhar) ----- */
#ifndef FASTBAUD
#define FASTBAUD 3          /* 1=19200 2=38400 3=57600 (4=115200 nao funcionou na placa) */
#endif
#define ACR    (*(volatile u16 *)0xFA0008)
#define CSRA   (*(volatile u16 *)0xFA0002)
#define CTUR   (*(volatile u16 *)0xFA000C)
#define CTLR   (*(volatile u16 *)0xFA000E)
#define CSTART (*(volatile u8  *)0xFA001F)
static const u8 nval[5] = {12, 6, 3, 2, 1};
static u32 baudmagic;
static void wait_tx(void) { while (!(SRA & 8)) ; }
static void slow(int n) { volatile long i; int k; for (k = 0; k < n; k++) for (i = 0; i < 100000L; i++) ; }
static void bcmd(int code) { con_put(0x1B); con_put(0x01); con_put('B'); con_put(code); wait_tx(); }
static void uart_rate(int idx)
{
    wait_tx();
    if (idx == 0) { ACR = 0; CSRA = 0xBB; return; }
    ACR = 0x60; CTUR = 0; CTLR = nval[idx]; (void)CSTART; CSRA = 0xDD;
}
static void try_fast(void)
{
    static u8 sec[128];
    bcmd('0' + FASTBAUD);
    slow(1);
    uart_rate(FASTBAUD);
    slow(1);
    rxfirst = 100000L;
    if (net_io(0, 0, 0, sec) == 0) { rxfirst = RXFIRST; bcmd('K'); return; }
    rxfirst = RXFIRST;
    uart_rate(0);
    slow(24);                    /* a ponte volta sozinha a 9600 em 8 s */
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
        dphtab[i].dpb = (u32)&dpb0;
        dphtab[i].csv = 0;
        dphtab[i].alv = (u32)(i ? alv1 : alv0);
    }
    memtab.count = 1;
    memtab.low = low;
    {   /* monitor v2.1: RAMEND ($40C) + marca 'RAM1' ($430); sem a marca usa TPA_TOP fixo */
        u32 top = TPA_TOP, re = *(volatile u32 *)0x40CUL;
        if (*(volatile u32 *)0x430UL == 0x52414D31UL && (re & 0xFFFFUL) == 0xFFFFUL && re >= 0xFFFFUL && re < 0x100000UL) top = re + 1UL;
        memtab.len = top - low;
    }
    settrk = setsec = curdsk = 0;
    iobyte = 0;
    #ifdef TRYFAST
    if (baudmagic != 0xBA0DBA0DUL) { baudmagic = 0xBA0DBA0DUL; try_fast(); }
#endif
    prs("\r\n\r\nCP/M-68K  -  PARAGON 50 (Tabajara Labs)\r\n");
}

void biosinit_entry(void) { biosinit(); }

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
        if (p1 >= NDISK) return 0;
        curdsk = (u16)p1;
        return (u32)&dphtab[p1];
    case 10: settrk = (u16)p1; return 0;
    case 11: setsec = (u16)p1; return 0;
    case 12: setdma = p1; return 0;
    case 13:
        if (settrk >= NTRK || setsec >= SPT) return 1;
        return (u32)net_io(0, curdsk, lba_of(), (u8 *)setdma);
    case 14:
        if (settrk >= NTRK || setsec >= SPT) return 1;
        return (u32)net_io(1, curdsk, lba_of(), (u8 *)setdma);
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
