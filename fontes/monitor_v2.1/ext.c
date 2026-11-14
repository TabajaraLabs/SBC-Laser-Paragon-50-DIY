/* PARAGON 50 - Monitor v2: modulo de extensao ($F90000, so na ROM 27C512)
 * Comandos: U (desassembla) A (assembla) E (edita) R (registradores) N/O (passo) K (breakpoints) X (executa) e ajuda por topico.
 */
#include "../dis.c"
#define nw asm_nw
#include "../asm.c"
#undef nw

extern void x_putc(int c);
extern int  x_getc(void);
extern void x_puts(const char *s);
extern void x_strobe(void);
extern char *x_getline(void);
extern int  x_kbhit(void);
extern int  dbg_resume(void);
extern void dbg_vecs(int on);

/* ---- estado persistente (fixo em $0800; zerado no reset do monitor) ---- */
struct X {
    u32 d[8]; u32 a[7]; u32 sp; u32 pc; u16 sr; u16 vec; u32 fa; u32 monsp;   /* offsets usados pelo assembly */
    u32 bpa[8]; u16 bpo[8];
    u32 tmp; u16 tmpo;
    u32 lastu, lasta;
    u16 inited, rc, werr, pad;
    u32 laste;
};
#define G (*(struct X *)0x800)
#define RAMLO 0x2000UL
#define RAMHI (*(volatile u32 *)0x40CUL)   /* ultimo byte da RAM, detectado pelo monitor no reset */

/* ---- E/S ---- */
u16 rd16(u32 a) { return *(volatile u16 *)a; }
void wr16(u32 a, u16 v) { if (a < RAMLO || a > RAMHI - 1) { G.werr = 1; return; } *(volatile u16 *)a = v; }
void wr8(u32 a, u8 v) { if (a < RAMLO || a > RAMHI) { G.werr = 1; return; } *(volatile u8 *)a = v; }

static void nl(void) { x_putc(13); x_putc(10); }
static void prs(const char *s) { while (*s) { if (*s == '\n') x_putc(13); x_putc(*s); s++; } }
static void hexn(u32 v, int n) { int i, d; for (i = n - 1; i >= 0; i--) { d = (int)((v >> (i * 4)) & 15); x_putc(d < 10 ? '0' + d : 'A' + d - 10); } }
static void spc(int n) { while (n-- > 0) x_putc(' '); }
static void prrange(void) { prs("$002000-$"); hexn(RAMHI & 0xFFFFFF, 6); }
static int  up(int c) { return (c >= 'a' && c <= 'z') ? c - 32 : c; }
static char *skp(char *p) { while (*p == ' ') p++; return p; }
static int num(char **pp, u32 *v)
{
    char *p = skp(*pp); u32 r = 0; int n = 0, c;
    if (*p == '$') p++;
    for (;;) {
        c = *p;
        if (c >= '0' && c <= '9') c -= '0';
        else if (up(c) >= 'A' && up(c) <= 'F') c = up(c) - 'A' + 10;
        else break;
        r = (r << 4) | (u32)c; p++; n++;
    }
    *pp = p; *v = r;
    return n;
}
static int streq(const char *a, const char *b) { while (*a && *b) { if (up(*a) != up(*b)) return 0; a++; b++; } return *a == *b; }
static char lbuf[84];
/* le uma linha com eco; ESC cancela (devolve 0); BackSpace edita */
static char *rdl(void)
{
    int n = 0, c;
    for (;;) {
        c = x_getc();
        if (c == 27) { x_putc(13); x_putc(10); return 0; }
        if (c == 13) { x_putc(13); x_putc(10); lbuf[n] = 0; return lbuf; }
        if (c == 8 || c == 127) { if (n) { n--; x_putc(8); x_putc(' '); x_putc(8); } continue; }
        if (c < 32) continue;
        if (n < 80) { lbuf[n++] = (char)c; x_putc(c); }
    }
}
static void decout(u32 v);
static int abort_key(void) { if (x_kbhit()) { x_getc(); return 1; } return 0; }

static void ginit(void)
{
    if (G.inited) return;
    G.inited = 1; G.rc = 0x4AFC;
    G.sp = 0xFF00UL; G.sr = 0x2700;
    G.pc = *(volatile u32 *)0x404; if (G.pc == 0) G.pc = RAMLO;
    G.lastu = RAMLO; G.lasta = RAMLO; G.laste = RAMLO;
}

/* ================================================================ U : desassembla */
static int disline(u32 a)
{
    char b[80]; int l, i;
    l = dis68k(a, b);
    if (l < 2) l = 2;
    hexn(a & 0xFFFFFF, 6); spc(2);
    for (i = 0; i < 5; i++) { if (i < l / 2) { hexn(rd16(a + 2 * (u32)i), 4); x_putc(' '); } else spc(5); }
    spc(1); prs(b); nl();
    return l;
}
static void cmd_u(char *p)
{
    u32 a = G.lastu, e = 0, v; int n = 16;
    if (num(&p, &v)) { a = v & ~1UL; if (num(&p, &v)) { if (v > a) e = v; else n = (int)v; } }
    if (e) { while (a <= e) { a += (u32)disline(a); if (abort_key()) break; } }
    else { while (n-- > 0) { a += (u32)disline(a); if (abort_key()) break; } }
    G.lastu = a;
}

/* ================================================================ A : assembla */
static void cmd_a(char *p)
{
    u32 pc = G.lasta, v, start; char *ln, err[64], line[84]; int r, tot = 0, i;
    p = skp(p);
    if (*p == '-') { asm_reset(); prs("Rotulos apagados.\n"); return; }
    if (num(&p, &v)) pc = v & ~1UL;
    if (pc < RAMLO || pc > RAMHI) { prs("Endereco fora da RAM de usuario ("); prrange(); prs(")\n"); return; }
    start = pc;
    prs("Montando em "); hexn(pc, 6); prs("\n[.], linha vazia ou [ESC] retorna ao monitor\n");
    for (;;) {
        hexn(pc & 0xFFFFFF, 6); prs("> ");
        ln = rdl();
        if (!ln) break;
        for (i = 0; i < 80 && ln[i]; i++) line[i] = ln[i];
        line[i] = 0;
        ln = skp(line);
        if (*ln == 0 || (*ln == '.' && ln[1] == 0)) break;
        G.werr = 0;
        r = asm_line(&pc, line, err);
        if (r < 0) { prs("  ^ erro: "); prs(err); nl(); continue; }
        if (G.werr) { prs("  ^ erro: escrita fora da RAM de usuario ("); prrange(); prs(")\n"); continue; }
        tot += r;
    }
    G.lasta = pc; G.lastu = start;
    prs("Montados "); hexn((u32)tot, 4); prs(" bytes; fim em "); hexn(pc & 0xFFFFFF, 6); nl();
    if ((i = asm_unresolved()) != 0) {
        prs("ATENCAO: "); hexn((u32)i, 2); prs(" referencia(s) a simbolo(s) nao definido(s): ");
        asm_list_unresolved(err); prs(err); nl();
    }
}

/* ================================================================ E : edita memoria */
static void edit_loop(u32 a)
{
    u32 v; char *ln; int n;
    prs("Digite o novo valor em hexadecimal e Enter.\n");
    prs("[.] ou [ESC] retorna ao monitor   [CR] avanca um byte   [~] volta um byte\n");
    for (;;) {
        hexn(a & 0xFFFFFF, 6); prs(": "); hexn(*(volatile u8 *)a, 2); prs(" > ");
        ln = rdl();
        if (!ln || *skp(ln) == '.') { G.laste = a; break; }
        ln = skp(ln);
        if (*ln == '~' || *ln == '-') { a--; continue; }
        if (*ln) {
            n = num(&ln, &v);
            if (!n) { prs("  ^ valor invalido\n"); continue; }
            if (a < RAMLO || a > RAMHI) { prs("  ^ protegido (so "); prrange(); prs(")\n"); a++; continue; }
            *(volatile u8 *)a = (u8)v;
            if (*(volatile u8 *)a != (u8)v) prs("  ^ nao gravou (ROM?)\n");
        }
        a++;
    }
}
static void cmd_e(char *p)
{
    u32 a;
    if (!num(&p, &a)) a = G.laste;
    edit_loop(a);
}


/* ================================================================ P F M V S W : memoria, todos com argumentos opcionais */
static u32 lastaddr(void) { return *(volatile u32 *)0x400; }
static void setlast(u32 a) { *(volatile u32 *)0x400 = a; }
static int askn(const char *q, u32 *v) { char *ln; prs(q); ln = rdl(); if (!ln) return 0; return num(&ln, v); }
static int prot(u32 a, u32 e) { if (a < RAMLO || e > RAMHI || e < a) { prs("Endereco protegido: so e permitido gravar de "); prrange(); prs(".\n"); return 1; } return 0; }

static void cmd_p(char *p)
{
    u32 a, v, n = 0;
    if (!num(&p, &a)) a = lastaddr();
    if (*skp(p) == 0) { edit_loop(a); return; }
    while (num(&p, &v)) {
        if (prot(a, a)) break;
        *(volatile u8 *)a = (u8)v;
        if (*(volatile u8 *)a != (u8)v) { prs("Nao gravou em "); hexn(a, 6); prs(" (ROM?)\n"); break; }
        a++; n++;
    }
    setlast(a);
    prs("Gravados "); decout(n); prs(" byte(s); proximo endereco "); hexn(a, 6); nl();
}
static void cmd_f(char *p)
{
    u32 a = RAMLO, e = RAMHI, b = 0, v, i;
    if (num(&p, &v)) { a = v; e = RAMHI; if (num(&p, &v)) { e = v; if (num(&p, &v)) b = v; } }
    if (prot(a, e)) return;
    for (i = a; i <= e; i++) { *(volatile u8 *)i = (u8)b; if ((i & 255) == 0) x_strobe(); }
    setlast(e + 1);
    prs("Preenchidos "); hexn(a, 6); prs(" ate "); hexn(e, 6); prs(" com "); hexn(b, 2); nl();
}
static void cmd_m(char *p)
{
    u32 a = lastaddr(), e, d, v, n, i;
    if (num(&p, &v)) a = v;
    e = a + 0x7F;
    if (num(&p, &v)) e = v;
    if (e < a) { prs("Fim menor que inicio.\n"); return; }
    if (!num(&p, &d) && !askn("Destino da copia (hexadecimal)? ", &d)) { prs("Destino invalido.\n"); return; }
    n = e - a + 1;
    if (prot(d, d + n - 1)) return;
    if (d > a) { for (i = n; i > 0; i--) { *(volatile u8 *)(d + i - 1) = *(volatile u8 *)(a + i - 1); if ((i & 255) == 0) x_strobe(); } }
    else { for (i = 0; i < n; i++) { *(volatile u8 *)(d + i) = *(volatile u8 *)(a + i); if ((i & 255) == 0) x_strobe(); } }
    setlast(d + n);
    prs("Copiados "); decout(n); prs(" byte(s) de "); hexn(a, 6); prs(" para "); hexn(d, 6); nl();
}
static void cmd_v(char *p)
{
    u32 a = lastaddr(), e, b, v, i, bad = 0; int x, y;
    if (num(&p, &v)) a = v;
    e = a + 0x7F;
    if (num(&p, &v)) e = v;
    if (e < a) { prs("Fim menor que inicio.\n"); return; }
    if (!num(&p, &b) && !askn("Endereco do outro bloco (hexadecimal)? ", &b)) { prs("Endereco invalido.\n"); return; }
    for (i = 0; i <= e - a; i++) {
        x = *(volatile u8 *)(a + i); y = *(volatile u8 *)(b + i);
        if (x != y) { bad++; if (bad <= 16) { hexn(a + i, 6); prs(": "); hexn((u32)x, 2); prs("   "); hexn(b + i, 6); prs(": "); hexn((u32)y, 2); nl(); } }
        if ((i & 255) == 255) { x_strobe(); if (abort_key()) { prs("Interrompido.\n"); return; } }
    }
    if (bad) { prs("Diferencas: "); decout(bad); nl(); } else prs("Blocos iguais.\n");
}
static void cmd_s(char *p)
{
    u32 a = RAMLO, e = RAMHI, v, i, hits = 0; u8 pat[8]; int n = 0, k;
    if (num(&p, &v)) { a = v; e = RAMHI; if (num(&p, &v)) e = v; }
    while (n < 8 && num(&p, &v)) pat[n++] = (u8)v;
    if (n == 0) {
        char *ln; prs("Bytes a procurar (hexadecimal, ate 8)? "); ln = rdl(); if (!ln) return;
        while (n < 8 && num(&ln, &v)) pat[n++] = (u8)v;
        if (n == 0) { prs("Nada a procurar.\n"); return; }
    }
    if (e < a) { prs("Fim menor que inicio.\n"); return; }
    for (i = a; i + (u32)n - 1 <= e; i++) {
        for (k = 0; k < n; k++) if (*(volatile u8 *)(i + (u32)k) != pat[k]) break;
        if (k == n) { hits++; hexn(i, 6); nl(); if (hits >= 64) { prs("(64 ocorrencias; parando)\n"); return; } }
        if ((i & 255) == 255) { x_strobe(); if (abort_key()) { prs("Interrompido.\n"); return; } }
    }
    if (hits == 0) prs("Nao encontrado.\n"); else { decout(hits); prs(" ocorrencia(s).\n"); }
}
static void cmd_w(char *p)
{
    u32 a = lastaddr(), e, v, n, i, sum; int k;
    if (num(&p, &v)) a = v;
    e = a + 0xFF;
    if (num(&p, &v)) e = v;
    if (e < a) { prs("Fim menor que inicio.\n"); return; }
    while (a <= e) {
        n = e - a + 1; if (n > 16) n = 16;
        sum = n + 4 + ((a >> 16) & 255) + ((a >> 8) & 255) + (a & 255);
        prs("S2"); hexn(n + 4, 2); hexn(a & 0xFFFFFF, 6);
        for (i = 0; i < n; i++) { k = *(volatile u8 *)(a + i); sum += (u32)k; hexn((u32)k, 2); }
        hexn(~sum & 255, 2); nl();
        a += n;
        if (abort_key()) break;
    }
    prs("S804000000FB\n");
}

/* ================================================================ R : registradores */
static void showregs(void)
{
    int i;
    for (i = 0; i < 8; i++) { prs("D"); x_putc('0' + i); x_putc('='); hexn(G.d[i], 8); x_putc(' '); if ((i & 3) == 3) nl(); }
    for (i = 0; i < 8; i++) {
        prs("A"); x_putc('0' + i); x_putc('=');
        hexn(i < 7 ? G.a[i] : G.sp, 8); x_putc(' ');
        if ((i & 3) == 3) nl();
    }
    prs("PC="); hexn(G.pc & 0xFFFFFF, 6); prs("  SR="); hexn(G.sr, 4);
    prs("  T="); x_putc('0' + ((G.sr >> 15) & 1)); prs(" S="); x_putc('0' + ((G.sr >> 13) & 1));
    prs(" IPL="); x_putc('0' + ((G.sr >> 8) & 7)); prs("  X N Z V C = ");
    for (i = 4; i >= 0; i--) { x_putc('0' + ((G.sr >> i) & 1)); x_putc(' '); }
    nl();
    disline(G.pc);
}
static u32 *regptr(char **pp)
{
    char *p = skp(*pp); int c1 = up(p[0]), c2 = up(p[1]);
    if ((c1 == 'D' || c1 == 'A') && c2 >= '0' && c2 <= '7') {
        *pp = p + 2;
        if (c1 == 'D') return &G.d[c2 - '0'];
        return c2 == '7' ? &G.sp : &G.a[c2 - '0'];
    }
    if (c1 == 'S' && c2 == 'P') { *pp = p + 2; return &G.sp; }
    if (c1 == 'P' && c2 == 'C') { *pp = p + 2; return &G.pc; }
    return 0;
}
static void cmd_r(char *p)
{
    u32 *r, v; char *q;
    p = skp(p);
    if (*p == 0) { showregs(); return; }
    if (up(p[0]) == 'S' && up(p[1]) == 'R') {
        q = p + 2;
        if (!num(&q, &v)) { prs("uso: R SR valor\n"); return; }
        G.sr = (u16)v; showregs(); return;
    }
    q = p; r = regptr(&q);
    if (!r) { prs("Registrador desconhecido. Use D0-D7, A0-A7, SP, PC ou SR\n"); return; }
    if (!num(&q, &v)) { prs("uso: R reg valor\n"); return; }
    *r = v;
    showregs();
}

/* ================================================================ K / X / N / O : depurador */
static int bpfind(u32 a) { int i; for (i = 0; i < 8; i++) if (G.bpa[i] == a) return i; return -1; }
static void bp_insert(void)
{
    int i;
    for (i = 0; i < 8; i++) if (G.bpa[i]) { G.bpo[i] = rd16(G.bpa[i]); *(volatile u16 *)G.bpa[i] = 0x4AFC; }
    if (G.tmp) { G.tmpo = rd16(G.tmp); *(volatile u16 *)G.tmp = 0x4AFC; }
}
static void bp_remove(void)
{
    int i;
    if (G.tmp) *(volatile u16 *)G.tmp = G.tmpo;
    for (i = 7; i >= 0; i--) if (G.bpa[i]) *(volatile u16 *)G.bpa[i] = G.bpo[i];
}
static void cmd_k(char *p)
{
    u32 a; int i, neg = 0;
    p = skp(p);
    if (*p == 0) {
        prs("Breakpoints:\n");
        for (i = 0; i < 8; i++) if (G.bpa[i]) { x_putc(' '); x_putc('0' + i); prs(": "); disline(G.bpa[i]); }
        return;
    }
    if (*p == '-') { neg = 1; p++; p = skp(p); if (*p == 0) { for (i = 0; i < 8; i++) G.bpa[i] = 0; prs("Todos removidos.\n"); return; } }
    if (!num(&p, &a)) { prs("uso: K [endereco | -endereco | -]\n"); return; }
    a &= ~1UL;
    i = bpfind(a);
    if (neg) { if (i >= 0) { G.bpa[i] = 0; prs("Removido.\n"); } else prs("Nao ha breakpoint ali.\n"); return; }
    if (a < RAMLO || a > RAMHI - 1) { prs("Breakpoint so em RAM de usuario ("); prrange(); prs(")\n"); return; }
    if (i >= 0) { prs("Ja existe.\n"); return; }
    for (i = 0; i < 8 && G.bpa[i]; i++) ;
    if (i == 8) { prs("Tabela cheia (8)\n"); return; }
    G.bpa[i] = a;
    prs("Breakpoint "); x_putc('0' + i); prs(" em "); hexn(a, 6); nl();
}

static int exec(int step)
{
    int v;
    G.sr &= 0x7FFF;
    if (step) G.sr |= 0x8000;
    else bp_insert();
    dbg_vecs(1); x_strobe();
    v = dbg_resume();
    dbg_vecs(0);
    if (!step) bp_remove();
    G.sr &= 0x7FFF;
    if (v == 4 && !step) {                      /* PC empilhado aponta o ILLEGAL; por seguranca aceita PC-2 */
        if (bpfind(G.pc) < 0 && G.pc != G.tmp && G.pc != (u32)&G.rc) {
            if (bpfind(G.pc - 2) >= 0 || G.pc - 2 == G.tmp || G.pc - 2 == (u32)&G.rc) G.pc -= 2;
        }
    }
    return v;
}
/* continua ate breakpoint/excecao; tmp = parada temporaria (passar por cima de JSR) */
static int go(u32 tmp)
{
    int v;
    G.tmp = tmp;
    if (bpfind(G.pc) >= 0 || (tmp && G.pc == tmp)) {      /* sai de cima do breakpoint com um passo */
        v = exec(1);
        if (v != 9) { G.tmp = 0; return v; }
        if (bpfind(G.pc) >= 0 || G.pc == tmp) { G.tmp = 0; return 4; }
    }
    v = exec(0);
    G.tmp = 0;
    return v;
}
static const char *vecname(int v)
{
    if (v == 2) return "Erro de barramento";
    if (v == 3) return "Erro de endereco";
    if (v == 4) return "Instrucao ilegal";
    if (v == 5) return "Divisao por zero";
    if (v == 6) return "CHK";
    if (v == 7) return "TRAPV";
    if (v == 8) return "Violacao de privilegio";
    if (v == 10) return "Line-A";
    if (v == 11) return "Line-F";
    return "Excecao";
}
static void stopmsg(int v)
{
    if (v == 9) return;
    if (v == 4 && G.pc == (u32)&G.rc) { prs("Programa terminou (RTS).\n"); G.pc = RAMLO; }
    else if (v == 4 && (bpfind(G.pc) >= 0)) { prs("Breakpoint "); x_putc('0' + bpfind(G.pc)); prs(" em "); hexn(G.pc, 6); nl(); }
    else if (v == 4 && G.tmp == 0 && 0) { }
    else { prs("*** "); prs(vecname(v)); prs(" (vetor "); hexn((u32)v, 2); prs(") em PC="); hexn(G.pc & 0xFFFFFF, 6);
           if (v <= 3) { prs(" end.="); hexn(G.fa, 8); prs("\n  (o PC salvo pelo 68000 nesse erro pode estar ate 10 bytes alem da instrucao que falhou)"); } nl(); }
}
static void cmd_x(char *p)
{
    u32 v; int r;
    if (num(&p, &v)) {                                    /* partida nova */
        G.pc = v & ~1UL; G.sp = 0xFF00UL - 4;
        *(volatile u32 *)G.sp = (u32)&G.rc;               /* RTS do programa cai no ILLEGAL de retorno */
        G.sr = 0x2700;
    }
    prs("Executando em "); hexn(G.pc & 0xFFFFFF, 6); prs(" (o teclado nao interrompe o programa)\n");
    r = go(0);
    stopmsg(r);
    showregs();
}
static void cmd_n(char *p, int over)
{
    u32 n = 1, v, op; int r, l, i;
    char b[80];
    if (num(&p, &v) && v) n = v;
    for (i = 0; (u32)i < n; i++) {
        op = rd16(G.pc);
        if (over && ((op & 0xFFC0) == 0x4E80 || (op & 0xFF00) == 0x6100)) {
            l = dis68k(G.pc, b);
            r = go(G.pc + (u32)l);
            if (r == 4 && G.pc == G.tmp) r = 9;
        } else r = exec(1);
        if (r != 9) { stopmsg(r); showregs(); return; }
        if (n > 1 && i + 1 < (int)n) { disline(G.pc); if (abort_key()) break; }
    }
    showregs();
}

/* ================================================================ D : dump hexadecimal + ASCII */
static void cmd_d(char *p)
{
    u32 a = *(volatile u32 *)0x400, e, v, i; int c;
    e = a + 0x7F;
    if (num(&p, &v)) { a = v; e = a + 0x7F; if (num(&p, &v)) e = (v > a) ? v : a + v - 1; }
    prs("          00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  0123456789ABCDEF\n");
    while (a <= e) {
        hexn(a, 8); spc(2);
        for (i = 0; i < 16; i++) { hexn(*(volatile u8 *)(a + i), 2); x_putc(' '); }
        spc(1);
        for (i = 0; i < 16; i++) { c = *(volatile u8 *)(a + i); x_putc(c >= 32 && c < 127 ? c : '.'); }
        nl();
        a += 16;
        if (abort_key()) break;
    }
    *(volatile u32 *)0x400 = a;
}

/* ================================================================ = : calculadora hexadecimal */
static void decout(u32 v) { char b[12]; int i = 0; if (!v) { x_putc('0'); return; } while (v) { b[i++] = (char)('0' + v % 10); v /= 10; } while (i) x_putc(b[--i]); }
static int ishexc(int c) { return (c >= '0' && c <= '9') || (up(c) >= 'A' && up(c) <= 'F'); }
static void cmd_calc(char *p)
{
    char o[100]; int i = 0, j, k, allhex; long r; int u; u32 v; char *q = skp(p);
    if (*q == 0) { prs("Expressao (ex.: 2000+40*2   FF&0F   #100+1   'A'+1)? "); q = rdl(); if (!q) return; q = skp(q); if (*q == 0) return; }
    while (*q && i < 90) {
        if (*q == '\'') { o[i++] = *q++; while (*q && i < 90) { o[i++] = *q; if (*q++ == '\'') break; } continue; }
        if (*q == '$' || *q == '%') { o[i++] = *q++; if (q[-1] == '%' && !(i >= 2 && (o[i-2] == '+' || o[i-2] == '-' || o[i-2] == '*' || o[i-2] == '/' || o[i-2] == '(' || o[i-2] == '<' || o[i-2] == '>' || o[i-2] == '&' || o[i-2] == '|' || o[i-2] == '^'))) { if (i == 1) { } } continue; }
        if (*q == '#') { q++; while (*q >= '0' && *q <= '9' && i < 90) o[i++] = *q++; continue; }   /* #123 = decimal */
        if (ishexc(*q) || (up(*q) >= 'A' && up(*q) <= 'Z') || *q == '_') {
            for (j = 0; ishexc(q[j]) || (up(q[j]) >= 'A' && up(q[j]) <= 'Z') || q[j] == '_' || (q[j] >= '0' && q[j] <= '9'); j++) ;
            allhex = 1; for (k = 0; k < j; k++) if (!ishexc(q[k])) allhex = 0;
            if (allhex) o[i++] = '$';
            for (k = 0; k < j && i < 94; k++) o[i++] = q[k];
            q += j; continue;
        }
        o[i++] = *q++;
    }
    o[i] = 0;
    errmsg = 0;
    r = evaltext(o, &u);
    if (errmsg) { prs("  erro: "); prs(errmsg); nl(); return; }
    if (u) { prs("  erro: simbolo nao definido (rotulos vem do comando A; numeros sao hexadecimais; use # para decimal)\n"); return; }
    v = (u32)r;
    prs("  Hexadecimal : $"); hexn(v, 8); nl();
    prs("  Decimal     : "); decout(v); nl();
    prs("  Com sinal   : "); if ((long)v < 0) { x_putc('-'); decout((u32)(-(long)v)); } else decout(v); nl();
    prs("  Binario     : ");
    for (i = 31; i >= 0; i--) { x_putc('0' + (int)((v >> i) & 1)); if ((i & 3) == 0 && i) x_putc(' '); }
    nl();
    prs("  ASCII       : ");
    for (i = 24; i >= 0; i -= 8) { k = (int)((v >> i) & 255); x_putc(k >= 32 && k < 127 ? k : '.'); }
    nl();
}

/* ================================================================ Y : checksum / CRC de uma faixa */
static void cmd_y(char *p)
{
    u32 a, e, v, crc32 = 0xFFFFFFFFUL, n = 0, s8 = 0, s16 = 0, x8 = 0; u16 crc16 = 0xFFFF; int b, c;
    u32 w = 0; volatile u32 ea, en;
    if (!num(&p, &a)) { a = 0xF80000UL; e = 0xF8FFFFUL; }
    else if (!num(&p, &e)) e = a + 255;
    else if (e <= a) e = a + e - 1;
    if (e < a) { prs("Faixa invalida.\n"); return; }
    ea = e;
    for (v = a; v <= e; v++) {
        c = *(volatile u8 *)v;
        s8 += (u32)c; x8 ^= (u32)c;
        if (n & 1) { s16 += (w << 8) | (u32)c; } else w = (u32)c;
        crc32 ^= (u32)c;
        for (b = 0; b < 8; b++) crc32 = (crc32 & 1) ? (crc32 >> 1) ^ 0xEDB88320UL : crc32 >> 1;
        crc16 ^= (u16)(c << 8);
        for (b = 0; b < 8; b++) crc16 = (crc16 & 0x8000) ? (u16)((crc16 << 1) ^ 0x1021) : (u16)(crc16 << 1);
        n++;
        if ((n & 255) == 0) { x_strobe(); if (abort_key()) { prs("Interrompido.\n"); return; } }
        if (v == 0xFFFFFFFFUL) break;
    }
    prs("  Faixa            : "); hexn(a, 6); prs(" ate "); hexn(ea, 6); prs("  ("); decout(n); prs(" bytes)\n");
    prs("  Soma de bytes    : "); hexn(s8 & 0xFF, 2); prs("  (8 bits)   total completo "); hexn(s8, 8); nl();
    prs("  Soma de palavras : "); hexn(s16 & 0xFFFF, 4); prs("  (16 bits, big-endian)\n");
    prs("  XOR dos bytes    : "); hexn(x8, 2); nl();
    prs("  CRC-16 (CCITT)   : "); hexn(crc16, 4); prs("  (polinomio 1021, inicio FFFF)\n");
    prs("  CRC-32 (zip)     : "); hexn(~crc32, 8); prs("  (igual ao zlib.crc32 / crc32 do Python)\n");
}

/* ================================================================ Z : teste de RAM */
static void cmd_z(char *p)
{
    u32 a, e, v, bad = 0; u16 pat, got; int pass, k;
    if (!num(&p, &a)) { a = RAMLO; e = RAMHI - 1; }
    else if (!num(&p, &e)) e = RAMHI - 1;
    a &= ~1UL; e &= ~1UL;
    if (a < RAMLO || e < a || e > RAMHI - 1) { prs("Faixa invalida: use $002000 a $"); hexn((RAMHI - 1) & 0xFFFFFF, 6); nl(); return; }
    for (pass = 0; pass < 5; pass++) {
        prs("  Passada "); x_putc('1' + pass); prs(pass == 0 ? " (0000)" : pass == 1 ? " (FFFF)" : pass == 2 ? " (5555)" : pass == 3 ? " (AAAA)" : " (endereco+bits altos)"); nl();
        for (k = 0; k < 2; k++) {
            for (v = a; v <= e; v += 2) {
                pat = (u16)(pass == 0 ? 0 : pass == 1 ? 0xFFFF : pass == 2 ? 0x5555 : pass == 3 ? 0xAAAA : ((u16)v ^ (u16)((v >> 16) * 0x9E37UL)));
                if (k == 0) *(volatile u16 *)v = pat;
                else {
                    got = *(volatile u16 *)v;
                    if (got != pat) { bad++; if (bad <= 10) { prs("  ERRO em "); hexn(v, 6); prs(" esperado="); hexn(pat, 4); prs(" lido="); hexn(got, 4); nl(); } }
                }
                if ((v & 0x1FE) == 0) x_strobe();
            }
        }
        if (abort_key()) { prs("Interrompido.\n"); return; }
    }
    if (bad) { prs("RAM COM ERROS, total="); decout(bad); nl(); } else prs("RAM OK\n");
}

/* ================================================================ I : informacoes */
static void cmd_i(void)
{
    prs("\nPARAGON 50 - Monitor 68000 v2.1 (Tabajara Labs) - modulo estendido presente\n");
    prs("\n  ROM  Monitor $F80000   Tetris $F81C00   EhBASIC $F84000   CP/M-68K $F88000   Perifericos $F8F000\n");
    prs("       Modulo v2.1 (ajuda, U A E R N O K X D P F M V S W = Y Z Q J @) em $F90000\n");
    prs("\n  RAM  detectada no reset: $000000-$"); hexn(RAMHI & 0xFFFFFF, 6); prs("  ("); decout((RAMHI + 1) >> 10); prs(" KB)\n");
    prs("       $0000-$1FFF monitor (vetores, variaveis, pilha, depurador)\n");
    prs("       "); prrange(); prs(" livre para programas\n");
    prs("\n  Serial  console no canal A a 57600 bps; canal B a 9600 bps\n");
    prs("\n  Porta de entrada (IP) = "); hexn(*(volatile u8 *)0xFA001B, 2); nl();
}

/* ================================================================ Q : mapa de memoria */
static void qline(u32 a, u32 e, const char *t)
{
    prs("  $"); hexn(a, 6); prs("-$"); hexn(e, 6); spc(2); prs(t); nl();
}
static void qamostra(u32 a)     /* le 16 palavras espalhadas pela faixa de 128 KB (so leitura) */
{
    u16 v0 = rd16(a), v; int i, igual = 1;
    for (i = 1; i < 16; i++) { v = rd16(a + (u32)i * 0x2000UL); if (v != v0) igual = 0; }
    prs("                     amostra de leitura: ");
    if (igual) { prs("sempre $"); hexn(v0, 4); } else prs("valores variados");
    nl();
}
static void cmd_q(void)
{
    u32 kb = (RAMHI + 1) >> 10;
    prs("MAPA DE MEMORIA DO PARAGON 50 (blocos de 128 KB; so leitura, nada e gravado)\n");
    prs("A16 e A19-A23 nao entram na decodificacao da parte baixa: o mapa se repete a cada $80000 ate $F7FFFF.\n\n");
    qline(0x000000UL, 0x01FFFFUL, "RAM (unica memoria de leitura e escrita da placa)");
    prs("                     "); decout(kb); prs(" KB reais detectados no reset");
    if (kb < 128) prs("; o resto da faixa repete a RAM (espelho)");
    nl();
    qline(0x020000UL, 0x03FFFFUL, "E/S de 16 bits do laser (entradas, DACs, 8254, latches $020018 e $020020)"); qamostra(0x020000UL);
    qline(0x040000UL, 0x05FFFFUL, "E/S de 8 bits (normalmente le $FF)"); qamostra(0x040000UL);
    qline(0x060000UL, 0x07FFFFUL, "SEM /DTACK: nao e acessado aqui (a CPU travaria)");
    qline(0x080000UL, 0xF7FFFFUL, "repete a parte baixa ($000000-$07FFFF) a cada $80000");
    qline(0xF80000UL, 0xF9FFFFUL, "ROM de 128 KB (monitor, Tetris, EhBASIC, CP/M-68K, modulo estendido)"); qamostra(0xF80000UL);
    qline(0xFA0000UL, 0xFBFFFFUL, "68681 DUART (nao lido: ler consome caracteres da serial)");
    qline(0xFC0000UL, 0xFDFFFFUL, "responde sem dispositivo (barramento aberto)"); qamostra(0xFC0000UL);
    qline(0xFE0000UL, 0xFFFFFFUL, "le $FF"); qamostra(0xFE0000UL);
    prs("\nFonte: varredura medida em 2026-11-10 (docs\\Mapa_enderecos.txt) e RAM detectada neste reset.\n");
}

/* ================================================================ J : monitor das entradas (J1/J2) */
static void jbits(const char *nome, u16 antes, u16 agora)
{
    int i;
    for (i = 0; i < 16; i++) {
        if (((antes ^ agora) >> i) & 1) { prs("  "); prs(nome); prs(" bit "); decout((u32)i); prs(" -> "); x_putc('0' + ((agora >> i) & 1)); }
    }
}
static void cmd_j(void)
{
    u16 a0 = rd16(0x020030UL), b0 = rd16(0x020028UL), a, b;
    prs("MONITOR DAS ENTRADAS (74LS240): porta A = $020030, porta B = $020028. Qualquer tecla sai.\n");
    prs("Aterre um pino de J1/J2 por um resistor de 330 ohms: o bit correspondente deve subir (240 inversor).\n");
    prs("Inicial:  A=$"); hexn(a0, 4); prs("  B=$"); hexn(b0, 4); nl();
    while (!abort_key()) {
        x_strobe();
        a = rd16(0x020030UL); b = rd16(0x020028UL);
        if (a != a0 || b != b0) {
            prs("A=$"); hexn(a, 4); prs("  B=$"); hexn(b, 4); prs("  mudou:");
            jbits("A", a0, a); jbits("B", b0, b); nl();
            a0 = a; b0 = b;
            { volatile u32 d; for (d = 0; d < 3000; d++) ; }      /* filtro simples contra ruido */
        }
    }
    prs("Fim.\n");
}

/* ================================================================ AJUDA */
static const char H_LIST[] =
    "\n"
    "Comandos do Monitor PARAGON 50 v2.1 (numeros em hexadecimal)\n"
    "\n"
    "MEMORIA\n"
    "D [inicio [fim]]              dump hexadecimal + ASCII\n"
    "P [inicio [byte ...]]         grava bytes (sem bytes: edita)\n"
    "E [endereco]                  edita a memoria byte a byte\n"
    "F [inicio [fim [byte]]]       preenche a faixa com o byte\n"
    "M [inicio [fim [destino]]]    copia um bloco de memoria\n"
    "V [inicio [fim [outro]]]      compara dois blocos de memoria\n"
    "S [inicio [fim [byte ...]]]   procura ate 8 bytes na faixa\n"
    "Z [inicio [fim]]              teste de RAM (padrao: toda a RAM de usuario)\n"
    "Y [inicio [fim]]              checksum e CRC-16/CRC-32 (padrao: a ROM)\n"
    "Q                             mapa de memoria (RAM, E/S, ROM, DUART)\n"
    "J                             monitor das entradas de J1/J2 (acha pinos de entrada)\n"
    "@                             perifericos: SD, buzzer e LCD 20x4 (tambem: G F8F000)\n"
    "= [expressao]                 calculadora hexadecimal\n"
    "\n"
    "PROGRAMAS\n"
    "L                             carrega arquivo S-record (S19/S28/S37)\n"
    "W [inicio [fim]]              despeja a faixa em S-records (S2)\n"
    "G [endereco]                  executa o programa (JSR)\n"
    "\n"
    "DESASSEMBLAR E ASSEMBLAR\n"
    "U [inicio [fim]]              desassembla instrucoes da memoria\n"
    "A [endereco | -]             assembla instrucoes digitadas\n"
    "\n"
    "DEPURACAO\n"
    "R [registrador [valor]]       mostra ou altera os registradores\n"
    "N [quantidade]                executa instrucao por instrucao\n"
    "O [quantidade]                igual ao N, mas passa por cima de JSR/BSR\n"
    "K [endereco | -endereco | -]  lista, poe ou tira breakpoints\n"
    "X [endereco]                  executa sob o depurador\n"
    "\n"
    "SISTEMA\n"
    "B                             EhBASIC\n"
    "C                             CP/M-68K\n"
    "T                             Tetris\n"
    "I                             informacoes\n"
    "? [comando]                   ajuda detalhada (ex.: ? A, ? ASM, ? DEBUG)\n";

static const char H_U[] =
    "U [inicio [fim]]  -  DESASSEMBLADOR\n"
    "\n"
    "  Mostra, em cada linha, o endereco, as palavras hexadecimais da\n"
    "  instrucao e o texto dela na sintaxe Motorola.\n"
    "\n"
    "     U 2000          desassembla 16 instrucoes a partir de $2000\n"
    "     U 2000 2040     desassembla tudo de $2000 ate $2040\n"
    "     U 2000 8        se o segundo valor for menor ou igual ao primeiro,\n"
    "                     ele e a QUANTIDADE (aqui: 8 instrucoes)\n"
    "     U               continua de onde o ultimo U ou A parou\n"
    "\n"
    "  Qualquer tecla interrompe a listagem.\n"
    "  Palavras que nao sao instrucao aparecem como  dc.w $XXXX.\n"
    "  Funciona tambem na ROM:  U F80900  mostra o inicio do reset do monitor.\n";

static const char H_A[] =
    "A [endereco | -]  -  ASSEMBLADOR LINHA A LINHA      (A -  apaga os rotulos)\n"
    "\n"
    "  O prompt mostra o endereco atual. Digite uma instrucao por linha:\n"
    "\n"
    "     002000> move.l #$1234,d0\n"
    "     002006> loop: addq.l #1,d0\n"
    "     002008> bra.s loop\n"
    "     00200A> .                    <- [.], linha vazia ou [ESC] termina\n"
    "\n"
    "  Rotulos (nome:) podem ser usados antes de serem definidos: o monitor\n"
    "  resolve a referencia quando o rotulo aparecer e avisa no final se\n"
    "  alguma ficar pendente. Os rotulos ficam guardados ate o reset.\n"
    "  So escreve na RAM de usuario: de $2000 ate o fim da RAM detectada (comando I).\n"
    "  Sintaxe completa e instrucoes aceitas:  ? ASM\n";

static const char H_ASM[] =
    "SINTAXE DO ASSEMBLADOR (Motorola 68000)\n"
    "\n"
    "  Numeros     $FF hexadecimal   %1010 binario   123 decimal   'A' caractere\n"
    "              * = endereco da instrucao atual (PC)\n"
    "  Operadores  + - * / % << >> & | ^ ~ e parenteses\n"
    "  Comentario  tudo depois de ';' e ignorado\n"
    "  Tamanho     .b .w .l (o padrao e .w); desvios aceitam .s (curto) e .w\n"
    "\n"
    "  Modos de enderecamento:\n"
    "     Dn   An   (An)   (An)+   -(An)   d(An)   d(An,Xn.w)   d(An,Xn.l)\n"
    "     endereco.w   endereco.l   d(PC)   d(PC,Xn)   #imediato   SR  CCR  USP\n"
    "     listas de registradores (MOVEM):  d0-d3/a0/a2-a4\n"
    "\n"
    "  Diretivas:\n"
    "     org endereco                 muda o endereco de montagem\n"
    "     even                         alinha em endereco par\n"
    "     nome equ valor               define uma constante\n"
    "     dc.b / dc.w / dc.l lista     grava dados  (dc.b \"texto\",13,10,0)\n"
    "     ds.b / ds.w / ds.l n         reserva n posicoes zeradas\n"
    "\n"
    "  Instrucoes: todo o conjunto do 68000:\n"
    "     move movea movem movep lea pea exg ext swap link unlk\n"
    "     add sub and or eor cmp (com formas a, i, q, x)  mulu muls divu divs\n"
    "     neg negx not clr tst tas chk  asl asr lsl lsr rol ror roxl roxr\n"
    "     btst bchg bclr bset  abcd sbcd nbcd  Bcc DBcc Scc  bra bsr jmp jsr\n"
    "     trap trapv rte rts rtr stop reset nop illegal\n"
    "\n"
    "  Rotulos:  nome:   no inicio da linha; podem ser usados antes de definidos.\n"
    "\n"
    "  Exemplo:\n"
    "            org $2000\n"
    "     msg:   dc.b \"Ola\",13,10,0\n"
    "            even\n"
    "     start: lea msg(pc),a1\n"
    "            jsr $F8080C         ; puts do monitor\n"
    "            rts\n";

static const char H_E[] =
    "E [endereco]  -  EDITA A MEMORIA BYTE A BYTE\n"
    "\n"
    "  Sem endereco continua de onde o ultimo E terminou.\n"
    "  Mostra  ENDERECO: VALOR >  e espera o novo valor em hexadecimal.\n"
    "  Digite o byte e Enter: ele e gravado e o editor avanca um endereco.\n"
    "\n"
    "     [CR] Enter     avanca um byte sem alterar\n"
    "     [~]             volta um byte\n"
    "     [.] ou [ESC]    retorna ao monitor\n"
    "\n"
    "  So grava na RAM de usuario, de $2000 ate o fim da RAM detectada (comando I);\n  ROM, vetores e pilha ficam protegidos.\n";

static const char H_R[] =
    "R [registrador [valor]]  -  REGISTRADORES DO PROGRAMA DEPURADO\n"
    "\n"
    "     R               mostra D0-D7, A0-A7, PC, SR (T, S, IPL, X N Z V C)\n"
    "                     e a proxima instrucao\n"
    "     R D3 1234       altera D3\n"
    "     R PC 2000       escolhe onde X, N e O continuam\n"
    "     R SP FF00       altera a pilha\n"
    "     R SR 2700       altera o registrador de status\n"
    "\n"
    "  Os valores sao os do ultimo ponto em que o programa parou.\n";

static const char H_N[] =
    "N [quantidade]  e  O [quantidade]  -  PASSO A PASSO (bit Trace do 68000)\n"
    "\n"
    "     N               executa 1 instrucao e mostra registradores e a proxima\n"
    "     N 10            executa 10 instrucoes (lista cada uma; tecla interrompe)\n"
    "     O               igual ao N, mas JSR e BSR rodam por inteiro, sem\n"
    "                     entrar na subrotina\n"
    "\n"
    "  Para escolher o ponto de partida use  R PC endereco  ou  X endereco.\n";

static const char H_K[] =
    "K [endereco | -endereco | -]  -  BREAKPOINTS (ate 8, na RAM de usuario)\n"
    "\n"
    "     K               lista os breakpoints\n"
    "     K 2010          poe um breakpoint em $2010\n"
    "     K -2010         tira o breakpoint de $2010\n"
    "     K -             tira todos\n"
    "\n"
    "  Durante o X a instrucao e trocada por ILLEGAL; ao parar, o monitor\n"
    "  restaura o original. O programa na memoria nunca fica alterado.\n";

static const char H_X[] =
    "X [endereco]  -  EXECUTA SOB O DEPURADOR\n"
    "\n"
    "     X 2000          comeca em $2000 (pilha nova em $FEFC; o RTS final do\n"
    "                     programa volta ao depurador)\n"
    "     X               continua de onde parou (apos breakpoint, N, O ou R PC)\n"
    "\n"
    "  Para em: breakpoint, RTS final do programa ou excecao (erro de barramento\n"
    "  ou de endereco, instrucao ilegal, divisao por zero...). Mostra o motivo,\n"
    "  os registradores e a proxima instrucao.\n"
    "\n"
    "  O teclado nao interrompe o programa em execucao: ele precisa terminar ou\n"
    "  ter um breakpoint. Se o watchdog da placa estiver ativo, o programa deve\n"
    "  chamar  jsr $F8082A  periodicamente.\n";

static const char H_DEBUG[] =
    "ROTEIRO DE DEPURACAO\n"
    "\n"
    "  1) A 2000          digite o programa (termine com rts)\n"
    "  2) U 2000          confira o desassemblado\n"
    "  3) K 2008          breakpoint na instrucao que interessa\n"
    "  4) X 2000          executa ate parar; veja os registradores\n"
    "  5) N ou O          passo a passo;  R D0 5 altera um registrador\n"
    "  6) D 2000          confere a memoria;  X continua;  K - limpa breakpoints\n"
    "\n"
    "  Programas carregados com L (S-record) funcionam do mesmo jeito:\n"
    "  X endereco_de_entrada.\n";

static const char H_D[] =
    "D [inicio [fim]]  -  DUMP HEXADECIMAL + ASCII\n"
    "\n"
    "  16 bytes por linha, com cabecalho de colunas. Sem fim, mostra 128 bytes.\n"
    "  Se o segundo valor for menor ou igual ao primeiro, ele e a quantidade.\n"
    "  Sem argumentos continua de onde o ultimo D, P ou L parou.\n"
    "  Qualquer tecla interrompe. Le tambem a ROM e os registradores do 68681.\n";
static const char H_P[] =
    "P [inicio [byte ...]]  -  GRAVA BYTES\n"
    "\n"
    "  P 2000 4E 71 4E 75   grava os bytes (hexadecimal) a partir de $2000\n"
    "  P 2000               sem bytes, abre o editor interativo (igual ao E)\n"
    "  P                    sem argumentos, continua do ultimo endereco usado\n"
    "\n"
    "  So grava na RAM de usuario ($2000 ate o fim da RAM; ver comando I).\n";
static const char H_F[] =
    "F [inicio [fim [byte]]]  -  PREENCHE UMA FAIXA\n"
    "\n"
    "  F 2000 2FFF AA   preenche $2000 a $2FFF com AA\n"
    "  F 2000 2FFF      sem byte, usa 00\n"
    "  F 2000           sem fim, vai ate o fim da RAM\n"
    "  F                sem argumentos, apaga toda a RAM de usuario ($2000 ate o fim)\n"
    "\n"
    "  So grava na RAM de usuario ($2000 ate o fim da RAM; ver comando I).\n";
static const char H_G[] =
    "G [endereco]  -  executa o programa com JSR, sem depurador; sem endereco usa a\n"
    "  entrada do ultimo L.\n"
    "  O programa volta ao monitor com RTS. Para depurar use o comando X.\n";
static const char H_L[] =
    "L  -  carrega S-records (S1, S2 e S3); o ponto de entrada (S7/S8/S9) fica\n"
    "  guardado para G e X.\n"
    "  Envie o arquivo pela ponte (ponte.bat) ou pelo terminal (enviar arquivo de\n"
    "    texto).\n";
static const char H_M[] =
    "M [inicio [fim [destino]]]  -  COPIA UM BLOCO DE MEMORIA\n"
    "\n"
    "  M 2000 20FF 3000   copia $2000-$20FF para $3000 (aceita sobreposicao)\n"
    "  Sem inicio usa o ultimo endereco; sem fim copia 128 bytes.\n"
    "  Se o destino faltar, o monitor pergunta.\n"
    "  O destino precisa estar na RAM de usuario ($2000 ate o fim da RAM).\n";
static const char H_S[] =
    "S [inicio [fim [byte ...]]]  -  PROCURA BYTES\n"
    "\n"
    "  S 2000 3000 4E 75   lista os enderecos de $2000-$3000 com 4E 75\n"
    "  Sem inicio procura desde $2000; sem fim vai ate o fim da RAM.\n"
    "  Aceita ate 8 bytes; se faltarem, o monitor pergunta.\n"
    "  Mostra ate 64 ocorrencias. Qualquer tecla interrompe.\n";
static const char H_Y[] =
    "Y [inicio [fim]]  -  CHECKSUM E CRC\n"
    "\n"
    "  Sem argumentos calcula sobre a ROM do monitor ($F80000 a $F8FFFF);\n"
    "  so com inicio, sobre 256 bytes. Soma de bytes\n"
    "  (8 bits), soma de palavras (16 bits), XOR, CRC-16 CCITT e CRC-32.\n"
    "  Util para conferir uma ROM ou um programa carregado:\n"
    "\n"
    "     Y F80000 F8FFFF     CRC-32 da ROM, comparavel com o do arquivo .bin\n"
    "\n"
    "  O CRC-32 e o mesmo do zlib/zip/Python (zlib.crc32).\n";
static const char H_CALC[] =
    "= [expressao]  -  CALCULADORA HEXADECIMAL\n"
    "\n"
    "  Sem expressao, o monitor pergunta.\n"
    "  Numeros sem prefixo sao hexadecimais. Use # para decimal (#100),\n"
    "  % para binario (%1010) e 'A' para caractere.\n"
    "  Operadores: + - * / % << >> & | ^ ~ e parenteses.\n"
    "  Rotulos criados com o comando A tambem valem.\n"
    "\n"
    "     = 2000+40*2      = FF&0F      = #100+1      = 1<<10      = F80000-1\n"
    "\n"
    "  Mostra o resultado em hexadecimal, decimal, decimal com sinal, binario\n"
    "  e ASCII.\n";
static const char H_Z[] =
    "Z [inicio [fim]]  -  TESTE DE RAM (padrao: toda a RAM de usuario)\n"
    "\n"
    "  Sem argumentos testa toda a RAM de usuario (apaga o que estiver nela).\n"
    "\n"
    "  Cinco passadas: 0000, FFFF, 5555, AAAA e endereco-como-dado. Na ultima o\n  valor depende tambem dos bits altos do endereco (A16 e acima), entao dois\n  enderecos que se espelham a cada 64 KB recebem valores diferentes e o erro aparece.\n"
    "  Mostra ate 10 erros (endereco, esperado, lido) e o total.\n"
    "  Qualquer tecla interrompe entre as passadas.\n";
static const char H_V[] =
    "V [inicio [fim [outro]]]  -  COMPARA DOIS BLOCOS\n"
    "\n"
    "  V 2000 20FF 3000   compara $2000-$20FF com os bytes a partir de $3000\n"
    "  Lista ate 16 diferencas (endereco e valor de cada lado) e o total.\n"
    "  Sem inicio usa o ultimo endereco; sem fim compara 128 bytes.\n"
    "  Se o outro bloco faltar, o monitor pergunta.\n";
static const char H_W[] =
    "W [inicio [fim]]  -  DESPEJA S-RECORDS\n"
    "\n"
    "  W 2000 20FF   envia a faixa em S-records (S2, 16 bytes por linha) e\n"
    "                termina com S8, para guardar ou enviar a outro computador.\n"
    "  Sem inicio usa o ultimo endereco; sem fim despeja 256 bytes.\n";
static const char H_Q[] =
    "Q  -  MAPA DE MEMORIA\n"
    "\n"
    "  Mostra os blocos de 128 KB do espaco de enderecos: RAM (com o tamanho\n"
    "  detectado no reset), E/S de 16 e 8 bits do laser, a faixa que nao gera\n"
    "  /DTACK (nunca acessada), ROM, DUART e os blocos sem dispositivo.\n"
    "  Nos blocos seguros mostra uma amostra de 16 leituras. Nada e gravado.\n"
    "  O DUART e o bloco sem /DTACK nao sao lidos.\n";
static const char H_J[] =
    "J  -  MONITOR DAS ENTRADAS (portas $020030 e $020028)\n"
    "\n"
    "  Le sem parar as quatro entradas de 8 bits (74LS240) e escreve uma linha\n"
    "  sempre que algum bit muda, dizendo qual porta (A=$020030, B=$020028), o\n"
    "  numero do bit (0 a 15) e o novo valor. Serve para descobrir qual pino de\n"
    "  J1 ou J2 chega a cada bit: aterre o pino por um resistor de 330 ohms.\n"
    "  Como os 240 invertem, aterrar uma entrada faz o bit subir para 1.\n"
    "  Qualquer tecla termina. So le; nada e gravado.\n";
static const char H_SYS[] =
    "B  inicia o EhBASIC.   C  inicia o CP/M-68K.   T  jogo Tetris (Q sai).   I \n"
    "  mostra informacoes da placa.\n"
    "Esses quatro tambem estao no menu de inicializacao (bootloader).\n";

static int help(char *p)
{
    char t[10]; int i = 0;
    p = skp(p);
    if (*p == 0) { prs(H_LIST); return 0; }
    if (*p == '=') { prs(H_CALC); return 0; }
    while (*p && *p != ' ' && i < 9) t[i++] = (char)up(*p++);
    t[i] = 0;
    if (streq(t, "U")) prs(H_U);
    else if (streq(t, "A")) prs(H_A);
    else if (streq(t, "ASM")) prs(H_ASM);
    else if (streq(t, "E")) prs(H_E);
    else if (streq(t, "R")) prs(H_R);
    else if (streq(t, "N") || streq(t, "O")) prs(H_N);
    else if (streq(t, "K")) prs(H_K);
    else if (streq(t, "X")) prs(H_X);
    else if (streq(t, "DEBUG")) prs(H_DEBUG);
    else if (streq(t, "D")) prs(H_D);
    else if (streq(t, "P")) prs(H_P);
    else if (streq(t, "F")) prs(H_F);
    else if (streq(t, "G")) prs(H_G);
    else if (streq(t, "L")) prs(H_L);
    else if (streq(t, "M")) prs(H_M);
    else if (streq(t, "V")) prs(H_V);
    else if (streq(t, "S")) prs(H_S);
    else if (streq(t, "W")) prs(H_W);
    else if (streq(t, "Y")) prs(H_Y);
    else if (streq(t, "Z")) prs(H_Z);
    else if (streq(t, "Q")) prs(H_Q);
    else if (streq(t, "J")) prs(H_J);
    else if (streq(t, "B") || streq(t, "C") || streq(t, "T") || streq(t, "I")) prs(H_SYS);
    else { prs("Sem ajuda detalhada para esse assunto. Digite ? para a lista de comandos.\n"); }
    return 0;
}

/* ================================================================ entrada */
int ext_main(int c, char *p)
{
    ginit();
    if (c == '?' || c == 'H') return help(p);
    if (c == 'D') { cmd_d(p); return 0; }
    if (c == 'P') { cmd_p(p); return 0; }
    if (c == 'F') { cmd_f(p); return 0; }
    if (c == 'M') { cmd_m(p); return 0; }
    if (c == 'V') { cmd_v(p); return 0; }
    if (c == 'S') { cmd_s(p); return 0; }
    if (c == 'W') { cmd_w(p); return 0; }
    if (c == '=') { cmd_calc(p); return 0; }
    if (c == 'Y') { cmd_y(p); return 0; }
    if (c == 'Z') { cmd_z(p); return 0; }
    if (c == 'Q') { cmd_q(); return 0; }
    if (c == 'J') { cmd_j(); return 0; }
    if (c == '@') { ((void (*)(void))0xF8F000UL)(); return 0; }
    if (c == 'I') { cmd_i(); return 0; }
    if (c == 'U') { cmd_u(p); return 0; }
    if (c == 'A') { cmd_a(p); return 0; }
    if (c == 'E') { cmd_e(p); return 0; }
    if (c == 'R') { cmd_r(p); return 0; }
    if (c == 'K') { cmd_k(p); return 0; }
    if (c == 'X') { cmd_x(p); return 0; }
    if (c == 'N') { cmd_n(p, 0); return 0; }
    if (c == 'O') { cmd_n(p, 1); return 0; }
    return 1;
}
