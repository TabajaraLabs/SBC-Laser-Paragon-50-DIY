/* Mini-assembler 68000 (sintaxe Motorola) para o monitor da PARAGON 50.
 *   int asm_line(u32 *pc, const char *line, char *err)
 *      monta uma linha (rotulo opcional, instrucao ou diretiva) em *pc, grava na memoria por wr16/wr8,
 *      avanca *pc e devolve o numero de bytes gerados (>= 0) ou -1 com a mensagem em err.
 *   Referencias a rotulos ainda nao definidos sao resolvidas quando o rotulo for definido.
 *   Diretivas: org, even, equ, dc.b/w/l, ds.b/w/l.
 */
typedef unsigned char  u8;
typedef unsigned short u16;
#ifdef NATIVE
typedef unsigned int   u32;
#else
typedef unsigned long  u32;
#endif

extern void wr16(u32 a, u16 v);
extern void wr8(u32 a, u8 v);
extern u16 rd16(u32 a);

#define M_DN   0x001
#define M_AN   0x002
#define M_IND  0x004
#define M_POST 0x008
#define M_PRE  0x010
#define M_D16  0x020
#define M_IDX  0x040
#define M_ABSW 0x080
#define M_ABSL 0x100
#define M_PCD  0x200
#define M_PCX  0x400
#define M_IMM  0x800
#define S_ALL  0xFFF
#define S_DATA 0xFFD
#define S_ALT  0x1FD
#define S_MEM  0x1FC
#define S_CTRL 0x7E4
#define S_BTS  0x7FD

/* tipos de operando */
enum { K_NONE, K_DN, K_AN, K_IND, K_POST, K_PRE, K_D16, K_IDX, K_ABSW, K_ABSL, K_PCD, K_PCX,
       K_IMM, K_SR, K_CCR, K_USP, K_EXPR, K_LIST };

struct opn {
    int kind, reg, xreg, xlong;      /* xreg: 0-7 Dn, 8-15 An */
    long val;
    int unres;
    char text[44];                   /* texto da expressao, para fixups */
    int mask;                        /* lista de registradores */
};
static struct opn P[2];
static int nop_;

/* ----------------------------------------------------------------- simbolos / fixups */
#define NSYM 48
#define NFIX 24
static char symname[NSYM][12];
static long symval[NSYM];
static int nsym;
struct fix { u32 at; int kind; u32 base; char expr[44]; };
static struct fix fx[NFIX];
static int nfix;
static u32 curpc;
static const char *errmsg;
static const char *ep;               /* ponteiro do avaliador */
static int e_unres;

static int lc(int c) { return (c >= 'A' && c <= 'Z') ? c + 32 : c; }
static int isid(int c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_' || c == '.' || (c >= '0' && c <= '9'); }
static int isdig(int c) { return c >= '0' && c <= '9'; }
static int hexv(int c) { c = lc(c); if (isdig(c)) return c - '0'; if (c >= 'a' && c <= 'f') return c - 'a' + 10; return -1; }
static int seq(const char *a, const char *b)       /* igual ignorando maiusculas */
{ while (*a && *b) { if (lc(*a) != lc(*b)) return 0; a++; b++; } return *a == *b; }
static void scpy(char *d, const char *s, int n) { int i = 0; while (s[i] && i < n - 1) { d[i] = s[i]; i++; } d[i] = 0; }
static int slen(const char *s) { int n = 0; while (s[n]) n++; return n; }

static int findsym(const char *n, int len)
{
    int i, j;
    for (i = 0; i < nsym; i++) {
        for (j = 0; j < len; j++) if (lc(symname[i][j]) != lc(n[j])) break;
        if (j == len && symname[i][len] == 0) return i;
    }
    return -1;
}

/* ----------------------------------------------------------------- expressoes */
static long expr0(void);
static void skipws(void) { while (*ep == ' ' || *ep == '\t') ep++; }
static long atom(void)
{
    long v = 0; int c, n, i;
    skipws();
    c = *ep;
    if (c == '(') { ep++; v = expr0(); skipws(); if (*ep == ')') ep++; else errmsg = "falta )"; return v; }
    if (c == '-') { ep++; return -atom(); }
    if (c == '+') { ep++; return atom(); }
    if (c == '~') { ep++; return ~atom(); }
    if (c == '$') { ep++; n = 0; while (hexv(*ep) >= 0) { v = v * 16 + hexv(*ep); ep++; n++; } if (!n) errmsg = "hexa invalido"; return v; }
    if (c == '%') { ep++; while (*ep == '0' || *ep == '1') { v = v * 2 + (*ep - '0'); ep++; } return v; }
    if (c == '\'') { ep++; v = (unsigned char)*ep; if (*ep) ep++; if (*ep == '\'') ep++; return v; }
    if (c == '*') { ep++; return (long)curpc; }
    if (isdig(c)) {
        if (c == '0' && lc(ep[1]) == 'x') { ep += 2; while (hexv(*ep) >= 0) { v = v * 16 + hexv(*ep); ep++; } return v; }
        while (isdig(*ep)) { v = v * 10 + (*ep - '0'); ep++; }
        return v;
    }
    if (isid(c)) {
        const char *s = ep;
        while (isid(*ep)) ep++;
        n = (int)(ep - s);
        i = findsym(s, n);
        if (i >= 0) return symval[i];
        e_unres = 1;
        return 0;
    }
    errmsg = "expressao invalida";
    return 0;
}
static long term(void)
{
    long v = atom(), w;
    for (;;) {
        skipws();
        if (*ep == '*' ) { ep++; v = v * atom(); }
        else if (*ep == '/') { ep++; w = atom(); if (w == 0) { errmsg = "divisao por zero"; w = 1; } v = v / w; }
        else if (*ep == '%' && !(hexv(ep[1]) >= 0 && 0)) { ep++; w = atom(); if (w == 0) { errmsg = "divisao por zero"; w = 1; } v = v % w; }
        else if (*ep == '<' && ep[1] == '<') { ep += 2; v = v << atom(); }
        else if (*ep == '>' && ep[1] == '>') { ep += 2; v = (long)((unsigned long)v >> atom()); }
        else if (*ep == '&') { ep++; v = v & atom(); }
        else return v;
    }
}
static long expr0(void)
{
    long v = term();
    for (;;) {
        skipws();
        if (*ep == '+') { ep++; v += term(); }
        else if (*ep == '-') { ep++; v -= term(); }
        else if (*ep == '|') { ep++; v |= term(); }
        else if (*ep == '^') { ep++; v ^= term(); }
        else return v;
    }
}
/* avalia texto completo; marca *unres se houver simbolo indefinido */
static long evaltext(const char *s, int *unres)
{
    long v;
    ep = s; e_unres = 0;
    v = expr0();
    skipws();
    if (*ep) errmsg = "lixo apos a expressao";
    *unres = e_unres;
    return v;
}

/* ----------------------------------------------------------------- operandos */
static int regname(const char *s, int len)       /* 0-7 Dn, 8-15 An (sp=15), -1 senao */
{
    if (len == 2 && lc(s[0]) == 'd' && s[1] >= '0' && s[1] <= '7') return s[1] - '0';
    if (len == 2 && lc(s[0]) == 'a' && s[1] >= '0' && s[1] <= '7') return 8 + s[1] - '0';
    if (len == 2 && lc(s[0]) == 's' && lc(s[1]) == 'p') return 15;
    return -1;
}
static int trimlen(const char *s, int n) { while (n > 0 && (s[n - 1] == ' ' || s[n - 1] == '\t')) n--; return n; }

/* "an" ou "xn.w"/"xn.l": devolve reg (0-15) e long */
static int idxreg(const char *s, int len, int *lng)
{
    int r;
    *lng = 0;
    if (len >= 4 && s[len - 2] == '.' ) {
        if (lc(s[len - 1]) == 'l') *lng = 1; else if (lc(s[len - 1]) != 'w') return -1;
        len -= 2;
    }
    r = regname(s, len);
    return r;
}

static int parse_list(const char *s, int len)    /* d0-d3/a0-a2 -> mascara (bit0=D0..bit15=A7), -1 se nao for lista */
{
    int i = 0, mask = 0, a, b, k;
    while (i < len) {
        a = regname(s + i, 2);
        if (a < 0) return -1;
        i += 2; b = a;
        if (i < len && s[i] == '-') { b = regname(s + i + 1, 2); if (b < 0) return -1; i += 3; }
        if (b < a) return -1;
        for (k = a; k <= b; k++) mask |= 1 << k;
        if (i < len) { if (s[i] != '/') return -1; i++; }
    }
    return mask;
}

static void setexpr(struct opn *p, const char *s, int len)
{
    int u;
    scpy(p->text, s, len + 1 > 44 ? 44 : len + 1);
    p->val = evaltext(p->text, &u);
    p->unres = u;
}

static int parse_op(const char *s, int n, struct opn *p)
{
    int i, r, lng, depth, open_, k, ntok, tl[4]; const char *tk[4];
    while (n > 0 && (*s == ' ' || *s == '\t')) { s++; n--; }
    n = trimlen(s, n);
    p->kind = K_NONE; p->reg = 0; p->xreg = 0; p->xlong = 0; p->val = 0; p->unres = 0; p->text[0] = 0; p->mask = 0;
    if (n == 0) return 0;
    if (s[0] == '#') { p->kind = K_IMM; setexpr(p, s + 1, n - 1); return 1; }
    if (n == 2 && (r = regname(s, 2)) >= 0) { p->kind = r < 8 ? K_DN : K_AN; p->reg = r & 7; return 1; }
    if (n == 2 && lc(s[0]) == 's' && lc(s[1]) == 'r') { p->kind = K_SR; return 1; }
    if (n == 3 && seq("ccr", "ccr") && lc(s[0]) == 'c' && lc(s[1]) == 'c' && lc(s[2]) == 'r') { p->kind = K_CCR; return 1; }
    if (n == 3 && lc(s[0]) == 'u' && lc(s[1]) == 's' && lc(s[2]) == 'p') { p->kind = K_USP; return 1; }
    if ((k = parse_list(s, n)) > 0 && (k & (k - 1)) != 0 || (k > 0 && n > 2)) { p->kind = K_LIST; p->mask = k; return 1; }
    if (n >= 5 && s[0] == '-' && s[1] == '(' && s[n - 1] == ')' && (r = regname(s + 2, n - 3)) >= 8) { p->kind = K_PRE; p->reg = r & 7; return 1; }
    if (n >= 5 && s[0] == '(' && s[n - 2] == ')' && s[n - 1] == '+' && (r = regname(s + 1, 2)) >= 8) { p->kind = K_POST; p->reg = r & 7; return 1; }
    if (s[n - 1] == ')') {
        depth = 0; open_ = -1;
        for (i = n - 1; i >= 0; i--) { if (s[i] == ')') depth++; else if (s[i] == '(') { depth--; if (depth == 0) { open_ = i; break; } } }
        if (open_ >= 0) {
            /* separa o conteudo dos parenteses por virgulas */
            ntok = 0; tk[0] = s + open_ + 1; k = 0;
            for (i = open_ + 1; i < n - 1; i++) {
                if (s[i] == ',') { tl[ntok] = trimlen(tk[ntok], (int)(s + i - tk[ntok])); ntok++; if (ntok > 3) return -1; tk[ntok] = s + i + 1; while (*tk[ntok] == ' ') tk[ntok]++; }
            }
            tl[ntok] = trimlen(tk[ntok], (int)(s + n - 1 - tk[ntok])); ntok++;
            {   /* alguem e' registrador de base? */
                int base = -1, bi = -1, pc = 0, ex = -1;
                for (i = 0; i < ntok; i++) {
                    r = regname(tk[i], tl[i]);
                    if (i == 0 && tl[i] == 2 && lc(tk[i][0]) == 'p' && lc(tk[i][1]) == 'c') { pc = 1; bi = i; break; }
                    if (r >= 8 && base < 0 && (i == 0 || i == 1)) { base = r & 7; bi = i; break; }
                }
                if (bi < 0) {
                    for (i = 0; i < ntok; i++) if (tl[i] == 2 && lc(tk[i][0]) == 'p' && lc(tk[i][1]) == 'c') { pc = 1; bi = i; break; }
                }
                if (bi >= 0) {
                    int hasx = 0;
                    /* prefixo (antes do parentese) ou primeiro token (estilo (d,an)) e' o deslocamento */
                    if (open_ > 0) { setexpr(p, s, open_); ex = 1; if (bi != 0) return -1; }
                    else if (bi == 1) { setexpr(p, tk[0], tl[0]); ex = 1; }
                    if (bi + 1 < ntok) {
                        p->xreg = idxreg(tk[bi + 1], tl[bi + 1], &lng);
                        if (p->xreg < 0) return -1;
                        p->xlong = lng; hasx = 1;
                    }
                    if (pc) p->kind = hasx ? K_PCX : K_PCD;
                    else { p->reg = base; p->kind = hasx ? K_IDX : (ex > 0 ? K_D16 : K_IND); }
                    return 1;
                }
            }
        }
    }
    /* expressao simples, com sufixo .w / .l opcional */
    if (n > 2 && s[n - 2] == '.' && (lc(s[n - 1]) == 'w' || lc(s[n - 1]) == 'l')) {
        p->kind = lc(s[n - 1]) == 'w' ? K_ABSW : K_ABSL; setexpr(p, s, n - 2); return 1;
    }
    p->kind = K_EXPR; setexpr(p, s, n);
    return 1;
}

/* ----------------------------------------------------------------- saida da instrucao */
static u16 ew[12];
static int nw;
static int pend_n;
static struct { int idx; int kind; u32 base; char text[44]; } pend[6];

static void put(u16 w) { if (nw < 12) ew[nw++] = w; }
static void put32(u32 v) { put((u16)(v >> 16)); put((u16)v); }

static void addfix(int wordidx, int kind, u32 base, const char *text)   /* aplicado depois que *pc for conhecido */
{
    if (pend_n < 6) { pend[pend_n].idx = wordidx; pend[pend_n].kind = kind; pend[pend_n].base = base; scpy(pend[pend_n].text, text, 44); pend_n++; }
}

/* kinds de fixup: 1 = abs32, 2 = abs16, 3 = pcrel16 (val - base), 4 = imm8 (palavra), 5 = imm16, 6 = imm32, 7 = pcrel8 index? nao usado */

static int modeidx(int kind)
{
    switch (kind) {
    case K_DN: return 0; case K_AN: return 1; case K_IND: return 2; case K_POST: return 3; case K_PRE: return 4;
    case K_D16: return 5; case K_IDX: return 6; case K_ABSW: return 7; case K_ABSL: return 8;
    case K_PCD: return 9; case K_PCX: return 10; case K_IMM: return 11;
    case K_EXPR: return 8;
    }
    return 99;
}

/* codifica o EA do operando; devolve (modo<<3)|reg ou -1; size: 0/1/2; allow = mascara; extaddr relativo ao inicio da instrucao */
static int eaenc(struct opn *p, int size, int allow, u32 ipc)
{
    int k = p->kind, m = 0, r = 0, d, idx;
    long v = p->val;
    if (k == K_EXPR) k = K_ABSL;
    idx = modeidx(k);
    if (idx == 99) { errmsg = "modo de enderecamento invalido"; return -1; }
    /* abs.l que cabe em palavra (resolvido, valor 0..$7FFF ou >= $FFFF8000) vira abs.w so se pedido com .w */
    if (!((allow >> idx) & 1)) { errmsg = "modo de enderecamento nao permitido aqui"; return -1; }
    switch (k) {
    case K_DN: return p->reg;
    case K_AN: return 8 | p->reg;
    case K_IND: return 16 | p->reg;
    case K_POST: return 24 | p->reg;
    case K_PRE: return 32 | p->reg;
    case K_D16:
        if (p->unres) addfix(nw + 1, 2, 0, p->text); else if (v < -32768L || v > 65535L) { errmsg = "deslocamento fora de faixa"; return -1; }
        put((u16)v); return 40 | p->reg;
    case K_IDX:
        if (!p->unres && (v < -128 || v > 127)) { errmsg = "deslocamento do indice fora de faixa (-128..127)"; return -1; }
        d = (int)(v & 0xFF) | (p->xreg << 12) | (p->xlong ? 0x800 : 0);
        put((u16)d); return 48 | p->reg;
    case K_ABSW:
        if (p->unres) addfix(nw + 1, 2, 0, p->text);
        put((u16)v); return 56;
    case K_ABSL:
        if (p->unres) addfix(nw + 1, 1, 0, p->text);
        put32((u32)v); return 57;
    case K_PCD:
        d = (int)(v - (long)(ipc + 2 + 2 * (u32)nw));
        if (p->unres) addfix(nw + 1, 3, ipc + 2 + 2 * (u32)nw, p->text); else if (d < -32768 || d > 32767) { errmsg = "pc-relativo fora de faixa"; return -1; }
        put((u16)d); return 58;
    case K_PCX:
        d = (int)(v - (long)(ipc + 2 + 2 * (u32)nw));
        if (!p->unres && (d < -128 || d > 127)) { errmsg = "pc-relativo com indice fora de faixa"; return -1; }
        put((u16)((d & 0xFF) | (p->xreg << 12) | (p->xlong ? 0x800 : 0))); return 59;
    case K_IMM:
        if (size == 2) { if (p->unres) addfix(nw + 1, 1, 0, p->text); put32((u32)v); }
        else if (size == 1) { if (p->unres) addfix(nw + 1, 2, 0, p->text); else if (v < -32768L || v > 65535L) { errmsg = "imediato fora de faixa (word)"; return -1; } put((u16)v); }
        else { if (p->unres) addfix(nw + 1, 4, 0, p->text); else if (v < -128 || v > 255) { errmsg = "imediato fora de faixa (byte)"; return -1; } put((u16)(v & 0xFF)); }
        return 60;
    }
    errmsg = "operando invalido"; return -1;
    (void)m; (void)r;
}

/* ----------------------------------------------------------------- mnemonicos */
static const char *const ccn[16] = {"t", "f", "hi", "ls", "cc", "cs", "ne", "eq", "vc", "vs", "pl", "mi", "ge", "lt", "gt", "le"};
static int ccidx(const char *s)
{
    int i;
    for (i = 0; i < 16; i++) if (seq(s, ccn[i])) return i;
    if (seq(s, "hs")) return 4;
    if (seq(s, "lo")) return 5;
    return -1;
}

static int bad_(const char *m) { errmsg = m; return -1; }
#define NEED(n_) do { if (nop_ != (n_)) return bad_("numero de operandos incorreto"); } while (0)

static int is_ea_dn(struct opn *p) { return p->kind == K_DN; }

static int assemble_insn(char *mn, int sz, u32 ipc)
{
    int i, c, m, a, b, t, size, d;
    long v;
    struct opn *s = &P[0], *dd = &P[1];
    nw = 0; pend_n = 0;
    size = sz < 0 ? 1 : sz;                       /* tamanho padrao: word */

    /* --- sem operandos --- */
    if (seq(mn, "nop")) { NEED(0); put(0x4E71); return 0; }
    if (seq(mn, "rts")) { NEED(0); put(0x4E75); return 0; }
    if (seq(mn, "rte")) { NEED(0); put(0x4E73); return 0; }
    if (seq(mn, "rtr")) { NEED(0); put(0x4E77); return 0; }
    if (seq(mn, "trapv")) { NEED(0); put(0x4E76); return 0; }
    if (seq(mn, "reset")) { NEED(0); put(0x4E70); return 0; }
    if (seq(mn, "illegal")) { NEED(0); put(0x4AFC); return 0; }
    if (seq(mn, "stop")) { NEED(1); if (s->kind != K_IMM) return bad_("stop precisa de #imediato"); put(0x4E72); put((u16)s->val); return 0; }
    if (seq(mn, "trap")) { NEED(1); if (s->kind != K_IMM || s->val < 0 || s->val > 15) return bad_("trap #0..15"); put((u16)(0x4E40 | s->val)); return 0; }
    if (seq(mn, "link")) { NEED(2); if (s->kind != K_AN || dd->kind != K_IMM) return bad_("link An,#disp"); put((u16)(0x4E50 | s->reg)); put((u16)dd->val); return 0; }
    if (seq(mn, "unlk")) { NEED(1); if (s->kind != K_AN) return bad_("unlk An"); put((u16)(0x4E58 | s->reg)); return 0; }
    if (seq(mn, "swap")) { NEED(1); if (s->kind != K_DN) return bad_("swap Dn"); put((u16)(0x4840 | s->reg)); return 0; }
    if (seq(mn, "ext")) { NEED(1); if (s->kind != K_DN || sz == 0) return bad_("ext.w/.l Dn"); put((u16)((sz == 2 ? 0x48C0 : 0x4880) | s->reg)); return 0; }

    /* --- desvios --- */
    if (mn[0] == 'b' || mn[0] == 'B') {
        c = -1;
        if (seq(mn, "bra")) c = 0; else if (seq(mn, "bsr")) c = 1;
        else if (!(seq(mn, "btst") || seq(mn, "bchg") || seq(mn, "bclr") || seq(mn, "bset"))) { c = ccidx(mn + 1); if (c == 0 || c == 1) c = -1; }
        if (c >= 0) {
            long off; int u;
            NEED(1);
            if (s->kind != K_EXPR && s->kind != K_ABSL && s->kind != K_ABSW) return bad_("destino do desvio");
            u = s->unres; v = s->val; off = v - (long)(ipc + 2);
            if (sz == 0 || (sz < 0 && !u && off >= -128 && off <= 127 && off != 0)) {
                if (u) return bad_("desvio curto com destino indefinido");
                if (off < -128 || off > 127 || off == 0) return bad_("desvio curto fora de faixa");
                put((u16)(0x6000 | (c << 8) | (off & 0xFF)));
            } else {
                if (!u && (off < -32768L || off > 32767L)) return bad_("desvio fora de faixa");
                put((u16)(0x6000 | (c << 8))); if (u) addfix(1, 3, ipc + 2, s->text);
                put((u16)off);
            }
            return 0;
        }
    }
    if ((mn[0] == 'd' || mn[0] == 'D') && (mn[1] == 'b' || mn[1] == 'B')) {
        c = seq(mn, "dbra") ? 1 : ccidx(mn + 2);
        if (c >= 0) {
            long off;
            NEED(2);
            if (s->kind != K_DN || (dd->kind != K_EXPR && dd->kind != K_ABSL)) return bad_("dbcc Dn,destino");
            off = dd->val - (long)(ipc + 2);
            if (!dd->unres && (off < -32768L || off > 32767L)) return bad_("dbcc fora de faixa");
            put((u16)(0x50C8 | (c << 8) | s->reg));
            if (dd->unres) addfix(1, 3, ipc + 2, dd->text);
            put((u16)off); return 0;
        }
    }
    /* --- Scc --- */
    if ((mn[0] == 's' || mn[0] == 'S') && mn[1] && !seq(mn, "sub") && !seq(mn, "suba") && !seq(mn, "subi") && !seq(mn, "subq") && !seq(mn, "subx") && !seq(mn, "swap") && !seq(mn, "stop") && !seq(mn, "sbcd")) {
        c = ccidx(mn + 1);
        if (c >= 0) { NEED(1); m = eaenc(s, 0, S_ALT, ipc); if (m < 0) return -1; 
            { int k; for (k = nw; k > 0; k--) ew[k] = ew[k - 1]; ew[0] = (u16)(0x50C0 | (c << 8) | m); nw++; }
            return 0; }
    }

    /* funcao auxiliar local: monta "opcode | ea" com extensoes depois */
#define EMIT_OP(opw, ea_) do { int k_; for (k_ = nw; k_ > 0; k_--) ew[k_] = ew[k_ - 1]; ew[0] = (u16)((opw) | (ea_)); nw++; } while (0)

    if (seq(mn, "jmp") || seq(mn, "jsr")) { NEED(1); m = eaenc(s, 2, S_CTRL, ipc); if (m < 0) return -1; EMIT_OP(seq(mn, "jmp") ? 0x4EC0 : 0x4E80, m); return 0; }
    if (seq(mn, "pea")) { NEED(1); m = eaenc(s, 2, S_CTRL, ipc); if (m < 0) return -1; EMIT_OP(0x4840, m); return 0; }
    if (seq(mn, "lea")) { NEED(2); if (dd->kind != K_AN) return bad_("lea ea,An"); m = eaenc(s, 2, S_CTRL, ipc); if (m < 0) return -1; EMIT_OP(0x41C0 | (dd->reg << 9), m); return 0; }
    if (seq(mn, "chk")) { NEED(2); if (dd->kind != K_DN) return bad_("chk ea,Dn"); m = eaenc(s, 1, S_DATA, ipc); if (m < 0) return -1; EMIT_OP(0x4180 | (dd->reg << 9), m); return 0; }
    if (seq(mn, "tas")) { NEED(1); m = eaenc(s, 0, S_ALT, ipc); if (m < 0) return -1; EMIT_OP(0x4AC0, m); return 0; }
    if (seq(mn, "nbcd")) { NEED(1); m = eaenc(s, 0, S_ALT, ipc); if (m < 0) return -1; EMIT_OP(0x4800, m); return 0; }
    {
        static const char *const un[5] = {"negx", "clr", "neg", "not", "tst"};
        static const u16 unop[5] = {0x4000, 0x4200, 0x4400, 0x4600, 0x4A00};
        for (i = 0; i < 5; i++) if (seq(mn, un[i])) {
            NEED(1); m = eaenc(s, size, S_ALT, ipc); if (m < 0) return -1; EMIT_OP(unop[i] | (size << 6), m); return 0;
        }
    }
    if (seq(mn, "moveq")) {
        NEED(2); if (s->kind != K_IMM || dd->kind != K_DN) return bad_("moveq #n,Dn");
        if (!s->unres && (s->val < -128 || s->val > 255)) return bad_("moveq fora de faixa");
        put((u16)(0x7000 | (dd->reg << 9) | (s->val & 0xFF))); if (s->unres) addfix(0, 4, 0, s->text); return 0;
    }
    if (seq(mn, "mulu") || seq(mn, "muls") || seq(mn, "divu") || seq(mn, "divs")) {
        NEED(2); if (dd->kind != K_DN) return bad_("mul/div ea,Dn");
        m = eaenc(s, 1, S_DATA, ipc); if (m < 0) return -1;
        EMIT_OP(seq(mn, "mulu") ? 0xC0C0 : seq(mn, "muls") ? 0xC1C0 : seq(mn, "divu") ? 0x80C0 : 0x81C0 | 0, 0);
        ew[0] |= (u16)((dd->reg << 9) | m); return 0;
    }
    if (seq(mn, "exg")) {
        NEED(2);
        if (s->kind == K_DN && dd->kind == K_DN) put((u16)(0xC140 | (s->reg << 9) | dd->reg));
        else if (s->kind == K_AN && dd->kind == K_AN) put((u16)(0xC148 | (s->reg << 9) | dd->reg));
        else if (s->kind == K_DN && dd->kind == K_AN) put((u16)(0xC188 | (s->reg << 9) | dd->reg));
        else if (s->kind == K_AN && dd->kind == K_DN) put((u16)(0xC188 | (dd->reg << 9) | s->reg));
        else return bad_("exg Rx,Ry");
        return 0;
    }
    if (seq(mn, "abcd") || seq(mn, "sbcd") || seq(mn, "addx") || seq(mn, "subx")) {
        int base = seq(mn, "abcd") ? 0xC100 : seq(mn, "sbcd") ? 0x8100 : seq(mn, "addx") ? 0xD100 : 0x9100;
        int bcd = seq(mn, "abcd") || seq(mn, "sbcd");
        NEED(2);
        if (bcd) size = 0;
        if (s->kind == K_DN && dd->kind == K_DN) put((u16)(base | (dd->reg << 9) | (bcd ? 0 : size << 6) | s->reg));
        else if (s->kind == K_PRE && dd->kind == K_PRE) put((u16)(base | (dd->reg << 9) | (bcd ? 0 : size << 6) | 8 | s->reg));
        else return bad_("operandos: Dy,Dx ou -(Ay),-(Ax)");
        return 0;
    }
    if (seq(mn, "cmpm")) {
        NEED(2); if (s->kind != K_POST || dd->kind != K_POST) return bad_("cmpm (Ay)+,(Ax)+");
        put((u16)(0xB108 | (dd->reg << 9) | (size << 6) | s->reg)); return 0;
    }
    if (seq(mn, "movep")) {
        NEED(2);
        if (s->kind == K_D16 && dd->kind == K_DN) { t = 4 + (sz == 2 ? 1 : 0); put((u16)(0x0008 | (dd->reg << 9) | (t << 6) | s->reg)); put((u16)s->val); }
        else if (s->kind == K_DN && dd->kind == K_D16) { t = 6 + (sz == 2 ? 1 : 0); put((u16)(0x0008 | (s->reg << 9) | (t << 6) | dd->reg)); put((u16)dd->val); }
        else return bad_("movep d(Ay),Dx / movep Dx,d(Ay)");
        return 0;
    }
    if (seq(mn, "movem")) {
        int mask;
        NEED(2); if (sz == 0) return bad_("movem.w ou .l");
        if (dd->kind == K_LIST || dd->kind == K_DN || dd->kind == K_AN) {         /* memoria -> registradores */
            mask = dd->kind == K_LIST ? dd->mask : (1 << (dd->reg + (dd->kind == K_AN ? 8 : 0)));
            m = eaenc(s, 2, M_IND | M_POST | M_D16 | M_IDX | M_ABSW | M_ABSL | M_PCD | M_PCX, ipc + 2); if (m < 0) return -1;
            { int k; for (k = nw; k > 0; k--) ew[k] = ew[k - 1]; ew[0] = (u16)mask; nw++; for (k = 0; k < pend_n; k++) pend[k].idx++; }
            EMIT_OP(0x4C80 | ((sz == 2) ? 0x40 : 0), m); return 0;
        }
        if (s->kind == K_LIST || s->kind == K_DN || s->kind == K_AN) {
            mask = s->kind == K_LIST ? s->mask : (1 << (s->reg + (s->kind == K_AN ? 8 : 0)));
            m = eaenc(dd, 2, M_IND | M_PRE | M_D16 | M_IDX | M_ABSW | M_ABSL, ipc + 2); if (m < 0) return -1;
            if ((m >> 3) == 4) { int r = 0, k; for (k = 0; k < 16; k++) r |= ((mask >> k) & 1) << (15 - k); mask = r; }
            { int k; for (k = nw; k > 0; k--) ew[k] = ew[k - 1]; ew[0] = (u16)mask; nw++; for (k = 0; k < pend_n; k++) pend[k].idx++; }
            EMIT_OP(0x4880 | ((sz == 2) ? 0x40 : 0), m); return 0;
        }
        return bad_("movem lista,ea / movem ea,lista");
    }
    if (seq(mn, "move") || seq(mn, "movea")) {
        int sm, dm;
        NEED(2);
        if (s->kind == K_SR) { m = eaenc(dd, 1, S_ALT, ipc); if (m < 0) return -1; EMIT_OP(0x40C0, m); return 0; }
        if (dd->kind == K_CCR) { m = eaenc(s, 1, S_DATA, ipc); if (m < 0) return -1; EMIT_OP(0x44C0, m); return 0; }
        if (dd->kind == K_SR) { m = eaenc(s, 1, S_DATA, ipc); if (m < 0) return -1; EMIT_OP(0x46C0, m); return 0; }
        if (s->kind == K_USP && dd->kind == K_AN) { put((u16)(0x4E68 | dd->reg)); return 0; }
        if (s->kind == K_AN && dd->kind == K_USP) { put((u16)(0x4E60 | s->reg)); return 0; }
        if (sz < 0) size = 1;
        if (dd->kind == K_AN) { if (size == 0) return bad_("movea.b nao existe"); }
        sm = eaenc(s, size, (size == 0) ? (S_ALL & ~M_AN) : S_ALL, ipc); if (sm < 0) return -1;
        dm = eaenc(dd, size, dd->kind == K_AN ? M_AN : S_ALT, ipc); if (dm < 0) return -1;
        { int k, ne = nw; (void)ne; for (k = nw; k > 0; k--) ew[k] = ew[k - 1]; nw++; }
        ew[0] = (u16)(((size == 0 ? 1 : size == 1 ? 3 : 2) << 12) | ((dm & 7) << 9) | ((dm >> 3) << 6) | sm);
        return 0;
    }
    if (seq(mn, "addq") || seq(mn, "subq")) {
        NEED(2); if (s->kind != K_IMM) return bad_("addq #1..8,ea");
        if (s->unres || s->val < 1 || s->val > 8) return bad_("addq/subq: 1..8");
        m = eaenc(dd, size, size == 0 ? S_ALT : (S_ALT | M_AN), ipc); if (m < 0) return -1;
        EMIT_OP(0x5000 | (seq(mn, "subq") ? 0x100 : 0) | (((int)s->val & 7) << 9) | (size << 6), m); return 0;
    }
    /* ULA: add sub and or eor cmp (+ formas a e i) */
    {
        static const char *const nm[6] = {"add", "sub", "and", "or", "eor", "cmp"};
        static const u16 base[6] = {0xD000, 0x9000, 0xC000, 0x8000, 0xB000, 0xB000};
        static const u16 imm[6] = {0x0600, 0x0400, 0x0200, 0x0000, 0x0A00, 0x0C00};
        for (i = 0; i < 6; i++) {
            int len = slen(nm[i]); char suf = mn[len];
            if (!(seq(nm[i], mn) || (mn[len] && !mn[len + 1] && (suf == 'a' || suf == 'A' || suf == 'i' || suf == 'I') && lc(mn[0]) == nm[i][0] && ((mn[len - 1] == nm[i][len - 1]) ) && seq(mn, nm[i]) == 0 && (int)slen(mn) == len + 1))) continue;
            /* confere o prefixo exato */
            { int j, okp = 1; for (j = 0; j < len; j++) if (lc(mn[j]) != nm[i][j]) okp = 0; if (!okp) continue; }
            a = lc(suf) == 'a' && slen(mn) == len + 1;
            b = lc(suf) == 'i' && slen(mn) == len + 1;
            if (a && (i == 2 || i == 3 || i == 4)) continue;     /* anda/ora/eora nao existem */
            NEED(2);
            if ((i == 2 || i == 3 || i == 4) && (b || (s->kind == K_IMM && dd->kind != K_DN) || (i == 4 && s->kind == K_IMM)) ) {
                /* ORI/ANDI/EORI (inclui CCR/SR) */
                if (s->kind != K_IMM) return bad_("operando imediato esperado");
                if (dd->kind == K_CCR || dd->kind == K_SR) {
                    put((u16)(imm[i] | (dd->kind == K_SR ? 0x7C : 0x3C))); put((u16)(dd->kind == K_SR ? s->val : (s->val & 0xFF))); return 0;
                }
                if (sz < 0) size = 1;
                if (eaenc(s, size, M_IMM, ipc) < 0) return -1;
                m = eaenc(dd, size, S_ALT, ipc); if (m < 0) return -1;
                EMIT_OP(imm[i] | (size << 6), m); return 0;
            }
            if (b || ((i == 0 || i == 1 || i == 5) && s->kind == K_IMM && dd->kind != K_DN && dd->kind != K_AN)) {      /* ADDI SUBI CMPI */
                if (s->kind != K_IMM) return bad_("operando imediato esperado");
                if (eaenc(s, size, M_IMM, ipc) < 0) return -1;
                m = eaenc(dd, size, S_ALT, ipc); if (m < 0) return -1;
                EMIT_OP(imm[i] | (size << 6), m); return 0;
            }
            if (a || ((i == 0 || i == 1 || i == 5) && dd->kind == K_AN)) {                                          /* ADDA SUBA CMPA */
                if (dd->kind != K_AN) return bad_("destino deve ser An");
                if (size == 0) return bad_("tamanho .w ou .l");
                m = eaenc(s, size, S_ALL, ipc); if (m < 0) return -1;
                EMIT_OP(base[i] | (dd->reg << 9) | (size == 1 ? 0xC0 : 0x1C0), m); return 0;
            }
            if (i == 4) {                                                                                          /* EOR Dn,ea */
                if (s->kind != K_DN) return bad_("eor Dn,ea");
                m = eaenc(dd, size, S_ALT, ipc); if (m < 0) return -1;
                EMIT_OP(0xB100 | (s->reg << 9) | (size << 6), m); return 0;
            }
            if (dd->kind == K_DN) {                                                                                 /* <ea>,Dn */
                m = eaenc(s, size, (size == 0) ? (S_ALL & ~M_AN) : ((i == 2 || i == 3) ? S_DATA : S_ALL), ipc); if (m < 0) return -1;
                if ((i == 2 || i == 3) && s->kind == K_AN) return bad_("An nao permitido");
                EMIT_OP(base[i] | (dd->reg << 9) | (size << 6), m); return 0;
            }
            if (s->kind == K_DN && i != 5) {                                                                        /* Dn,<ea> */
                m = eaenc(dd, size, S_MEM, ipc); if (m < 0) return -1;
                EMIT_OP(base[i] | (s->reg << 9) | ((4 + size) << 6), m); return 0;
            }
            return bad_("combinacao de operandos invalida");
        }
    }
    /* bits */
    {
        static const char *const bn[4] = {"btst", "bchg", "bclr", "bset"};
        for (i = 0; i < 4; i++) if (seq(mn, bn[i])) {
            NEED(2);
            if (s->kind == K_DN) { m = eaenc(dd, 0, i == 0 ? S_DATA : S_ALT, ipc); if (m < 0) return -1; EMIT_OP(0x0100 | (s->reg << 9) | (i << 6), m); return 0; }
            if (s->kind == K_IMM) {
                put((u16)(s->val & 0xFF));
                m = eaenc(dd, 0, i == 0 ? S_BTS : S_ALT, ipc); if (m < 0) return -1;
                EMIT_OP(0x0800 | (i << 6), m); return 0;
            }
            return bad_("bit: Dn ou #n como origem");
        }
    }
    /* deslocamentos */
    {
        static const char *const sn[8] = {"asr", "asl", "lsr", "lsl", "roxr", "roxl", "ror", "rol"};
        for (i = 0; i < 8; i++) if (seq(mn, sn[i])) {
            int type = i >> 1, dir = i & 1;
            if (nop_ == 1) {
                if (s->kind == K_DN) { put((u16)(0xE000 | (1 << 9) | (dir << 8) | (size << 6) | (type << 3) | s->reg)); return 0; }
                m = eaenc(s, 1, S_MEM, ipc); if (m < 0) return -1;
                if (size != 1) return bad_("deslocamento de memoria so .w");
                EMIT_OP(0xE0C0 | (type << 9) | (dir << 8), m); return 0;
            }
            NEED(2); if (dd->kind != K_DN) return bad_("destino deve ser Dn");
            if (s->kind == K_DN) { put((u16)(0xE020 | (s->reg << 9) | (dir << 8) | (size << 6) | (type << 3) | dd->reg)); return 0; }
            if (s->kind == K_IMM) {
                if (s->unres || s->val < 1 || s->val > 8) return bad_("contagem 1..8");
                put((u16)(0xE000 | (((int)s->val & 7) << 9) | (dir << 8) | (size << 6) | (type << 3) | dd->reg)); return 0;
            }
            return bad_("contagem: #n ou Dn");
        }
    }
    (void)v; (void)d; (void)is_ea_dn;
    return bad_("mnemonico desconhecido");
}

/* ----------------------------------------------------------------- linha */
static void resolve_all(void)
{
    int i, u, again;
    long v;
    do {
        again = 0;
        for (i = 0; i < nfix; i++) {
            if (!fx[i].expr[0]) continue;
            v = evaltext(fx[i].expr, &u);
            if (u) continue;
            switch (fx[i].kind) {
            case 1: wr16(fx[i].at, (u16)((u32)v >> 16)); wr16(fx[i].at + 2, (u16)v); break;
            case 2: wr16(fx[i].at, (u16)v); break;
            case 3: wr16(fx[i].at, (u16)(v - (long)fx[i].base)); break;
            case 4: wr16(fx[i].at, (u16)((rd16(fx[i].at) & 0xFF00) | ((u16)v & 0xFF))); break;
            }
            fx[i].expr[0] = 0; again = 0;
        }
    } while (again);
}

int asm_unresolved(void)
{
    int i, n = 0;
    for (i = 0; i < nfix; i++) if (fx[i].expr[0]) n++;
    return n;
}
void asm_reset(void) { nsym = 0; nfix = 0; }
void asm_list_unresolved(char *out)                  /* texto dos simbolos pendentes */
{
    int i, j; char *o = out; *o = 0;
    for (i = 0; i < nfix; i++) if (fx[i].expr[0]) { for (j = 0; fx[i].expr[j] && j < 20; j++) *o++ = fx[i].expr[j]; *o++ = ' '; }
    *o = 0;
}

int asm_define(const char *name, long v)
{
    int i = findsym(name, slen(name));
    if (i < 0) { if (nsym >= NSYM) return -1; i = nsym++; scpy(symname[i], name, 12); }
    symval[i] = v;
    resolve_all();
    return 0;
}

static int split_ops(char *s)                         /* separa por virgula fora de parenteses/aspas; devolve n; guarda em P */
{
    int n = 0, depth = 0, i = 0, start = 0, q = 0;
    char *e;
    nop_ = 0;
    while (*s == ' ' || *s == '\t') s++;
    if (!*s) return 0;
    for (e = s; ; e++) {
        if (*e == '\'' ) q = !q;
        if (!q) { if (*e == '(') depth++; else if (*e == ')') depth--; }
        if ((*e == ',' && depth == 0 && !q) || *e == 0) {
            if (n >= 2) { errmsg = "operandos demais"; return -1; }
            if (parse_op(s + start, (int)(e - s) - start, &P[n]) < 0) { errmsg = errmsg ? errmsg : "operando invalido"; return -1; }
            n++; start = (int)(e - s) + 1;
            if (*e == 0) break;
        }
        i++;
    }
    nop_ = n;
    return n;
}

int asm_line(u32 *pc, const char *line, char *err)
{
    char buf[100], *p, *mn, *ops, *dot;
    int n, sz = -1, i, bytes = 0, u;
    u32 ipc = *pc;
    long v;

    errmsg = 0; curpc = ipc;
    scpy(buf, line, sizeof buf);
    for (p = buf; *p; p++) if (*p == ';') { *p = 0; break; }          /* comentario */
    p = buf; while (*p == ' ' || *p == '\t') p++;
    if (!*p) return 0;
    /* rotulo: identificador seguido de ':' */
    { char *q = p; while (isid(*q) && *q != '.') q++;
      if (*q == ':' && q > p) {
          *q = 0; if (asm_define(p, (long)ipc) < 0) { scpy(err, "tabela de simbolos cheia", 60); return -1; }
          p = q + 1; while (*p == ' ' || *p == '\t') p++;
          if (!*p) return 0;
      } }
    mn = p; while (*p && *p != ' ' && *p != '\t') p++;
    if (*p) { *p++ = 0; }
    ops = p;
    /* "nome equ expr" (sem dois pontos) */
    { char *q = ops; while (*q == ' ' || *q == '\t') q++;
      if (seq("equ", "equ") && lc(q[0]) == 'e' && lc(q[1]) == 'q' && lc(q[2]) == 'u' && (q[3] == ' ' || q[3] == '\t')) {
          v = evaltext(q + 4, &u);
          if (errmsg) { scpy(err, errmsg, 60); return -1; }
          if (u) { scpy(err, "equ com simbolo indefinido", 60); return -1; }
          asm_define(mn, v); return 0;
      } }
    /* tamanho */
    dot = 0; for (p = mn; *p; p++) if (*p == '.') { dot = p; break; }
    if (dot) { *dot = 0; if (lc(dot[1]) == 'b' || lc(dot[1]) == 's') sz = 0; else if (lc(dot[1]) == 'w') sz = 1; else if (lc(dot[1]) == 'l') sz = 2; else { scpy(err, "sufixo de tamanho invalido", 60); return -1; }
        if (lc(dot[1]) == 's' && !(mn[0] == 'b' || mn[0] == 'B')) { scpy(err, "sufixo .s so em desvios", 60); return -1; } }

    /* diretivas */
    if (seq(mn, "org")) { v = evaltext(ops, &u); if (errmsg || u) { scpy(err, errmsg ? errmsg : "org precisa de valor definido", 60); return -1; } *pc = (u32)v; return 0; }
    if (seq(mn, "even")) { if (ipc & 1) { wr8(ipc, 0); *pc = ipc + 1; return 1; } return 0; }
    if (seq(mn, "dc") || seq(mn, "ds")) {
        int isdc = seq(mn, "dc"), w = sz < 0 ? 1 : sz;
        char *q = ops;
        if (!isdc) {
            v = evaltext(q, &u); if (errmsg || u) { scpy(err, errmsg ? errmsg : "ds precisa de valor definido", 60); return -1; }
            { long k; for (k = 0; k < v * (w == 0 ? 1 : w == 1 ? 2 : 4); k++) wr8(ipc + (u32)bytes++, 0); }
            *pc = ipc + (u32)bytes; return bytes;
        }
        for (;;) {
            char *e;
            while (*q == ' ' || *q == '\t') q++;
            if (!*q) break;
            if (*q == '"') {
                q++; while (*q && *q != '"') { if (w != 0) { scpy(err, "string so em dc.b", 60); return -1; } wr8(ipc + (u32)bytes++, (u8)*q++); }
                if (*q == '"') q++;
            } else {
                int dep = 0; e = q; while (*e && !(*e == ',' && dep == 0)) { if (*e == '(') dep++; if (*e == ')') dep--; e++; }
                { char sv = *e; *e = 0; v = evaltext(q, &u); *e = sv; }
                if (errmsg) { scpy(err, errmsg, 60); return -1; }
                if (u) {
                    if (nfix >= NFIX) { scpy(err, "muitas referencias pendentes", 60); return -1; }
                    if (w != 2 && w != 1) { scpy(err, "referencia futura so em dc.w/dc.l", 60); return -1; }
                    fx[nfix].at = ipc + (u32)bytes + 0; fx[nfix].kind = (w == 2) ? 1 : 2; fx[nfix].base = 0;
                    { char sv2 = *e; *e = 0; scpy(fx[nfix].expr, q, 44); *e = sv2; }
                    nfix++;
                }
                if (w == 0) wr8(ipc + (u32)bytes++, (u8)v);
                else if (w == 1) { wr16(ipc + (u32)bytes, (u16)v); bytes += 2; }
                else { wr16(ipc + (u32)bytes, (u16)((u32)v >> 16)); wr16(ipc + (u32)bytes + 2, (u16)v); bytes += 4; }
                q = e;
            }
            while (*q == ' ' || *q == '\t') q++;
            if (*q == ',') q++; else break;
        }
        *pc = ipc + (u32)bytes; return bytes;
    }

    /* instrucao */
    errmsg = 0;
    n = split_ops(ops);
    if (n < 0) { scpy(err, errmsg ? errmsg : "operando invalido", 60); return -1; }
    if (assemble_insn(mn, sz, ipc) < 0) { scpy(err, errmsg ? errmsg : "erro", 60); return -1; }
    if (errmsg) { scpy(err, errmsg, 60); return -1; }
    if (ipc & 1) { scpy(err, "instrucao em endereco impar", 60); return -1; }
    for (i = 0; i < nw; i++) wr16(ipc + 2 * (u32)i, ew[i]);
    for (i = 0; i < pend_n; i++) {
        if (nfix >= NFIX) { scpy(err, "muitas referencias pendentes", 60); return -1; }
        fx[nfix].at = ipc + 2 * (u32)pend[i].idx; fx[nfix].kind = pend[i].kind; fx[nfix].base = pend[i].base;
        scpy(fx[nfix].expr, pend[i].text, 44); nfix++;
    }
    *pc = ipc + 2 * (u32)nw;
    return 2 * nw;
}
