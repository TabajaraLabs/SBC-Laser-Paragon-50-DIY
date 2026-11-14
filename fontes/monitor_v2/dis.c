/* Disassembler 68000 (sintaxe Motorola) - portatil: no alvo le a memoria direto; no PC le de um buffer.
 *   int dis68k(u32 addr, char *out)  ->  devolve o tamanho da instrucao em bytes, texto em out */
typedef unsigned char  u8;
typedef unsigned short u16;
#ifdef NATIVE
typedef unsigned int   u32;
#else
typedef unsigned long  u32;
#endif

extern u16 rd16(u32 a);          /* fornecida pelo ambiente */

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

static char *o;
static u32 cur;
static int bad;

static u16 nw(void) { u16 w = rd16(cur); cur += 2; return w; }
static void pc_(int c) { *o++ = (char)c; }
static void ps(const char *s) { while (*s) *o++ = *s++; }
static void phex(u32 v, int min)
{
    char b[9]; int n = 0, i;
    do { b[n++] = "0123456789ABCDEF"[v & 15]; v >>= 4; } while (v);
    while (n < min) b[n++] = '0';
    pc_('$');
    for (i = n - 1; i >= 0; i--) pc_(b[i]);
}
static void pdec(long v)
{
    char b[12]; int n = 0;
    u32 u;
    if (v < 0) { pc_('-'); u = (u32)(-v); } else u = (u32)v;
    do { b[n++] = (char)('0' + u % 10); u /= 10; } while (u);
    while (n) pc_(b[--n]);
}
static void pdisp(long v)            /* deslocamento com sinal, em hexa */
{
    if (v == 0) { pc_('0'); return; }
    if (v < 0) { pc_('-'); v = -v; }
    phex((u32)v, 1);
}
static void preg(int an, int n) { pc_(an ? 'a' : 'd'); pc_('0' + n); }
static void pan(int n) { if (n == 7) ps("sp"); else preg(1, n); }
static void pa24(u32 v) { phex(v & 0xFFFFFF, 6); }

static const char *const cc[16] = {"t", "f", "hi", "ls", "cc", "cs", "ne", "eq", "vc", "vs", "pl", "mi", "ge", "lt", "gt", "le"};
static const char szc[4] = {'b', 'w', 'l', '?'};

static void psize(int s) { pc_('.'); pc_(szc[s]); }

/* imprime o operando EA; size 0/1/2 (b/w/l); allow = mascara de modos validos. Marca bad se invalido */
static void ea(int mode, int reg, int size, int allow)
{
    int idx = mode < 7 ? mode : 7 + reg;
    u16 w; long d; u32 l;
    if (idx > 11 || !((allow >> idx) & 1)) { bad = 1; return; }
    switch (mode) {
    case 0: preg(0, reg); return;
    case 1: pan(reg); return;
    case 2: pc_('('); pan(reg); pc_(')'); return;
    case 3: pc_('('); pan(reg); ps(")+"); return;
    case 4: ps("-("); pan(reg); pc_(')'); return;
    case 5: d = (short)nw(); pdisp(d); pc_('('); pan(reg); pc_(')'); return;
    case 6:
        w = nw(); d = (signed char)(w & 0xFF);
        pdisp(d); pc_('('); pan(reg); pc_(',');
        preg((w >> 15) & 1, (w >> 12) & 7); ps((w & 0x800) ? ".l" : ".w"); pc_(')');
        return;
    }
    switch (reg) {
    case 0: w = nw(); phex((u32)w, 4); ps(".w"); return;
    case 1: l = (u32)nw() << 16; l |= nw(); phex(l & 0xFFFFFF, 6); ps(".l"); return;
    case 2: l = cur; d = (short)nw(); pa24(l + d); ps("(pc)"); return;
    case 3: l = cur; w = nw(); d = (signed char)(w & 0xFF); pa24(l + d); ps("(pc,");
            preg((w >> 15) & 1, (w >> 12) & 7); ps((w & 0x800) ? ".l" : ".w"); pc_(')'); return;
    case 4:
        pc_('#');
        if (size == 2) { l = (u32)nw() << 16; l |= nw(); phex(l, 2); }
        else { w = nw(); phex(size == 0 ? (u32)(w & 0xFF) : (u32)w, 2); }
        return;
    }
    bad = 1;
}

static void mn(const char *m, int size)        /* mnemonico + .tam + espacos ate a coluna 8 */
{
    char *s = o; ps(m);
    if (size >= 0) psize(size);
    while (o - s < 8) pc_(' ');
}

static void movem_list(u16 mask, int rev)      /* rev: mascara de -(An) (bit0 = A7) */
{
    int i, first = 1, run, j, start;
    u16 m = mask;
    if (rev) { u16 r = 0; for (i = 0; i < 16; i++) r |= (u16)(((m >> i) & 1) << (15 - i)); m = r; }
    for (i = 0; i < 16; ) {
        if (!(m & (1 << i))) { i++; continue; }
        start = i; run = 1;
        while (i + run < 16 && (m & (1 << (i + run))) && ((i + run) & 7) != 0) run++;
        if (!first) pc_('/');
        first = 0;
        if (start < 8) preg(0, start); else pan(start - 8);
        if (run > 1) { pc_('-'); j = start + run - 1; if (j < 8) preg(0, j); else pan(j - 8); }
        i += run;
    }
    if (first) ps("{}");
}

static void strcpy_(char *d, const char *s) { while ((*d++ = *s++)) ; }

static void branch(u32 addr, int op, const char *name)
{
    int d8 = op & 0xFF;
    long d;
    char *s = o;
    if (d8 == 0) { d = (short)nw(); ps(name); ps(".w"); }
    else if (d8 == 0xFF) { bad = 1; return; }
    else { d = (signed char)d8; ps(name); ps(".s"); }
    while (o - s < 8) pc_(' ');
    pa24(addr + 2 + d);
}

int dis68k(u32 addr, char *out)
{
    int op, size, m, r, dn, t, mode2, reg2;
    u16 w, mask;
    u32 l;
    char *start;
    char nm[8];

    o = out; cur = addr; bad = 0;
    op = nw();
    m = (op >> 3) & 7; r = op & 7; dn = (op >> 9) & 7; size = (op >> 6) & 3;

    switch (op >> 12) {
    case 0:
        if (op & 0x0100) {
            if (m == 1) {                                     /* MOVEP */
                t = (op >> 6) & 7;
                if (t < 4) { bad = 1; break; }
                mn("movep", (t & 1) ? 2 : 1);
                if (t < 6) { pdisp((short)nw()); pc_('('); pan(r); ps("),"); preg(0, dn); }
                else { preg(0, dn); pc_(','); pdisp((short)nw()); pc_('('); pan(r); pc_(')'); }
                break;
            }
            t = size;
            { static const char *const bn[4] = {"btst", "bchg", "bclr", "bset"};
              mn(bn[t], m == 0 ? 2 : 0); }
            preg(0, dn); pc_(',');
            ea(m, r, 0, t == 0 ? S_DATA : S_ALT);
            break;
        }
        t = (op >> 9) & 7;
        if (t == 4) {                                         /* bit estatico */
            static const char *const bn[4] = {"btst", "bchg", "bclr", "bset"};
            mn(bn[size], m == 0 ? 2 : 0);
            w = nw(); pc_('#'); pdec(w & 0xFF); pc_(',');
            ea(m, r, 0, size == 0 ? S_BTS : S_ALT);
            break;
        }
        if (t == 7 || size == 3) { bad = 1; break; }
        { static const char *const in[7] = {"ori", "andi", "subi", "addi", 0, "eori", "cmpi"};
          if ((op & 0x00BF) == 0x003C && (t == 0 || t == 1 || t == 5)) {       /* para CCR / SR */
              mn(in[t], -1); w = nw(); pc_('#');
              if (op & 0x40) { phex(w, 4); ps(",sr"); } else { phex(w & 0xFF, 2); ps(",ccr"); }
              break;
          }
          mn(in[t], size);
          pc_('#');
          if (size == 2) { l = (u32)nw() << 16; l |= nw(); phex(l, 2); }
          else { w = nw(); phex(size == 0 ? (u32)(w & 0xFF) : (u32)w, 2); }
          pc_(',');
          ea(m, r, size, S_ALT);
        }
        break;

    case 1: case 2: case 3:
        size = (op >> 12) == 1 ? 0 : ((op >> 12) == 3 ? 1 : 2);
        mode2 = (op >> 6) & 7; reg2 = (op >> 9) & 7;
        if (mode2 == 1) { if (size == 0) { bad = 1; break; } mn("movea", size); }
        else mn("move", size);
        ea(m, r, size, (size == 0 && m == 1) ? 0 : S_ALL);
        pc_(',');
        ea(mode2, reg2, size, mode2 == 1 ? M_AN : S_ALT);
        break;

    case 4:
        if (op == 0x4AFC) { mn("illegal", -1); break; }
        if (op == 0x4E70) { mn("reset", -1); break; }
        if (op == 0x4E71) { mn("nop", -1); break; }
        if (op == 0x4E72) { mn("stop", -1); w = nw(); pc_('#'); phex(w, 4); break; }
        if (op == 0x4E73) { mn("rte", -1); break; }
        if (op == 0x4E75) { mn("rts", -1); break; }
        if (op == 0x4E76) { mn("trapv", -1); break; }
        if (op == 0x4E77) { mn("rtr", -1); break; }
        if ((op & 0xFFF0) == 0x4E40) { mn("trap", -1); pc_('#'); pdec(op & 15); break; }
        if ((op & 0xFFF8) == 0x4E50) { mn("link", -1); pan(r); ps(",#"); pdisp((short)nw()); break; }
        if ((op & 0xFFF8) == 0x4E58) { mn("unlk", -1); pan(r); break; }
        if ((op & 0xFFF8) == 0x4E60) { mn("move", 2); pan(r); ps(",usp"); break; }
        if ((op & 0xFFF8) == 0x4E68) { mn("move", 2); ps("usp,"); pan(r); break; }
        if ((op & 0xFFC0) == 0x4E80) { mn("jsr", -1); ea(m, r, 2, S_CTRL); break; }
        if ((op & 0xFFC0) == 0x4EC0) { mn("jmp", -1); ea(m, r, 2, S_CTRL); break; }
        if ((op & 0x01C0) == 0x01C0) { mn("lea", -1); ea(m, r, 2, S_CTRL); pc_(','); pan(dn); break; }
        if ((op & 0x01C0) == 0x0180) { mn("chk", 1); ea(m, r, 1, S_DATA); pc_(','); preg(0, dn); break; }
        if ((op & 0xFB80) == 0x4880) {
            if (m == 0) { if (op & 0x0400) { bad = 1; break; } mn("ext", (op & 0x40) ? 2 : 1); preg(0, r); break; }
            mask = nw();
            if (op & 0x0400) {                                /* memoria -> registradores */
                mn("movem", (op & 0x40) ? 2 : 1);
                ea(m, r, 2, M_IND | M_POST | M_D16 | M_IDX | M_ABSW | M_ABSL | M_PCD | M_PCX);
                pc_(','); movem_list(mask, 0);
            } else {
                mn("movem", (op & 0x40) ? 2 : 1);
                movem_list(mask, m == 4); pc_(',');
                ea(m, r, 2, M_IND | M_PRE | M_D16 | M_IDX | M_ABSW | M_ABSL);
            }
            break;
        }
        if ((op & 0xFFF8) == 0x4840) { mn("swap", -1); preg(0, r); break; }
        if ((op & 0xFFC0) == 0x4840) { mn("pea", -1); ea(m, r, 2, S_CTRL); break; }
        if ((op & 0xFFC0) == 0x4800) { mn("nbcd", -1); ea(m, r, 0, S_ALT); break; }
        if ((op & 0xFFC0) == 0x40C0) { mn("move", 1); ps("sr,"); ea(m, r, 1, S_ALT); break; }
        if ((op & 0xFFC0) == 0x44C0) { mn("move", 1); ea(m, r, 1, S_DATA); ps(",ccr"); break; }
        if ((op & 0xFFC0) == 0x46C0) { mn("move", 1); ea(m, r, 1, S_DATA); ps(",sr"); break; }
        if ((op & 0xFFC0) == 0x4AC0) { mn("tas", -1); ea(m, r, 0, S_ALT); break; }
        if (size == 3) { bad = 1; break; }
        { static const char *const un[8] = {"negx", 0, "clr", 0, "neg", 0, "not", 0};
          t = (op >> 8) & 15;
          if (t == 0) mn("negx", size);
          else if (t == 2) mn("clr", size);
          else if (t == 4) mn("neg", size);
          else if (t == 6) mn("not", size);
          else if (t == 10) mn("tst", size);
          else { bad = 1; break; }
          ea(m, r, size, S_ALT);
        }
        break;

    case 5:
        t = (op >> 8) & 15;
        if (size == 3) {
            if (m == 1) {                                     /* DBcc */
                u32 base = cur; long d;
                { const char *c = t == 1 ? "ra" : cc[t]; char *s = o; ps("db"); ps(c); while (o - s < 8) pc_(' '); }
                preg(0, r); pc_(','); d = (short)nw(); pa24(base + d);
            } else {
                char *s = o; ps("s"); ps(cc[t]); while (o - s < 8) pc_(' ');
                ea(m, r, 0, S_ALT);
            }
            break;
        }
        mn((op & 0x100) ? "subq" : "addq", size);
        pc_('#'); pdec(dn ? dn : 8); pc_(',');
        ea(m, r, size, size == 0 ? S_ALT : (S_ALT | M_AN));
        break;

    case 6:
        t = (op >> 8) & 15;
        if (t == 0) strcpy_(nm, "bra"); else if (t == 1) strcpy_(nm, "bsr");
        else { nm[0] = 'b'; nm[1] = cc[t][0]; nm[2] = cc[t][1]; nm[3] = 0; }
        branch(addr, op, nm);
        break;

    case 7:
        if (op & 0x100) { bad = 1; break; }
        mn("moveq", -1); pc_('#'); pdec((signed char)(op & 0xFF)); pc_(','); preg(0, dn);
        break;

    case 8: case 12:
        t = (op >> 6) & 7;
        if (t == 3 || t == 7) {
            if ((op >> 12) == 8) mn(t == 3 ? "divu" : "divs", 1); else mn(t == 3 ? "mulu" : "muls", 1);
            ea(m, r, 1, S_DATA); pc_(','); preg(0, dn); break;
        }
        if ((op & 0x01F0) == 0x0100) {                        /* SBCD / ABCD */
            mn((op >> 12) == 8 ? "sbcd" : "abcd", -1);
            if (m & 1) { ps("-("); pan(r); ps("),-("); pan(dn); pc_(')'); } else { preg(0, r); pc_(','); preg(0, dn); }
            break;
        }
        if ((op >> 12) == 12 && (t == 5 || t == 6 || t == 4) && ((op & 0x0130) == 0x0100)) {  /* EXG */
            mn("exg", 2);
            if (t == 5 && m == 0) { preg(0, dn); pc_(','); preg(0, r); }
            else if (t == 5 && m == 1) { preg(1, dn); pc_(','); preg(1, r); }
            else if (t == 6 && m == 1) { preg(0, dn); pc_(','); preg(1, r); }
            else bad = 1;
            break;
        }
        mn((op >> 12) == 8 ? "or" : "and", t & 3);
        if (t < 3) { ea(m, r, t, S_DATA); pc_(','); preg(0, dn); }
        else { preg(0, dn); pc_(','); ea(m, r, t & 3, S_MEM); }
        break;

    case 9: case 13:
        t = (op >> 6) & 7;
        if (t == 3 || t == 7) {
            mn((op >> 12) == 9 ? "suba" : "adda", t == 3 ? 1 : 2);
            ea(m, r, t == 3 ? 1 : 2, S_ALL); pc_(','); pan(dn); break;
        }
        if (t >= 4 && m < 2) {                                /* SUBX / ADDX */
            mn((op >> 12) == 9 ? "subx" : "addx", t & 3);
            if (m) { ps("-("); pan(r); ps("),-("); pan(dn); pc_(')'); } else { preg(0, r); pc_(','); preg(0, dn); }
            break;
        }
        mn((op >> 12) == 9 ? "sub" : "add", t & 3);
        if (t < 3) { ea(m, r, t, (t == 0) ? (S_ALL & ~M_AN) : S_ALL); pc_(','); preg(0, dn); }
        else { preg(0, dn); pc_(','); ea(m, r, t & 3, S_MEM); }
        break;

    case 11:
        t = (op >> 6) & 7;
        if (t == 3 || t == 7) { mn("cmpa", t == 3 ? 1 : 2); ea(m, r, t == 3 ? 1 : 2, S_ALL); pc_(','); pan(dn); break; }
        if (t < 3) { mn("cmp", t); ea(m, r, t, t == 0 ? (S_ALL & ~M_AN) : S_ALL); pc_(','); preg(0, dn); break; }
        if (m == 1) { mn("cmpm", t & 3); pc_('('); pan(r); ps(")+,("); pan(dn); ps(")+"); break; }
        mn("eor", t & 3); preg(0, dn); pc_(','); ea(m, r, t & 3, S_ALT);
        break;

    case 14: {
        static const char *const sh[4] = {"as", "ls", "rox", "ro"};
        if (size == 3) {
            if (op & 0x0800) { bad = 1; break; }
            { char *s = o; ps(sh[(op >> 9) & 3]); pc_((op & 0x100) ? 'l' : 'r'); psize(1); while (o - s < 8) pc_(' '); }
            ea(m, r, 1, S_MEM);
            break;
        }
        { char *s = o; ps(sh[(op >> 3) & 3]); pc_((op & 0x100) ? 'l' : 'r'); psize(size); while (o - s < 8) pc_(' '); }
        if (op & 0x20) preg(0, dn); else { pc_('#'); pdec(dn ? dn : 8); }
        pc_(','); preg(0, r);
        break; }

    default:
        bad = 1;
    }
    if (bad) {
        o = out; cur = addr + 2;
        ps("dc.w    "); phex((u32)op, 4);
    }
    *o = 0;
    return (int)(cur - addr);
}
