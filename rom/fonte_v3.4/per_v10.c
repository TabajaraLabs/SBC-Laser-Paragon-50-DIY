/* PARAGON 50 - modulo de PERIFERICOS PER1 ($F88000, banco 0): ADC, ADL, DAC, RTC.
 * Chamado pelo FLCHK (bancos) antes do despacho do monitor.  Compilar com build_per.sh.
 * Descoberto no firmware original do laser (desmontado em 2026-11-14):
 *   A/D  AD7875 de 12 bits: $020000 (leitura de palavra, bits 11-0). A conversao e disparada por um pulso no pino OP3 do DUART
 *        (SOPR $FA001C = $08, depois ROPR $FA001E = $08). IP4 do DUART ($FA001B bit 4) = 1 quando o conversor esta pronto.
 *        Entrada selecionada por 3 bits de $020020 (bits 14-12 = canal 0-7); o firmware mantem tambem o bit 15 em 1.
 *   D/A  12 bits, escrita de palavra: DAC A = $02000A (firmware: mV 10..5000, codigo = mV*4095/5000),
 *        DAC C = $02000C (firmware: 0..125000 unidades, codigo = valor*4095/125000).  Sem leitura de volta.
 */
typedef unsigned char  u8;
typedef unsigned short u16;
typedef unsigned long  u32;

extern void x_putc(int c);
extern int  x_getc(void);
extern void x_strobe(void);
extern int  x_kbhit(void);
extern void ext_init(void);
extern void x_lcd_at(long linha, long coluna, const char *texto);
extern void per_tickentry(void);

struct X {
    u32 d[8]; u32 a[7]; u32 sp; u32 pc; u16 sr; u16 vec; u32 fa; u32 monsp;   /* offsets usados pelo assembly */
    u32 bpa[8]; u16 bpo[8];
    u32 tmp; u16 tmpo;
    u32 lastu, lasta;
    u16 inited, rc, werr, pad;
    u32 laste;
    u16 dg0, dg1, dg2, dg3, forced;   /* v2.2d diagnostico */
    u32 ram2;      /* v2.2: ultimo byte da RAM adicional em $040000 (0 = ausente) */
};
#define G (*(struct X *)0x800)
#define RAM2LO 0x040000UL
#define PV ((volatile u16 *)0x1700)        /* PV[0] = $600D se valido, PV[1] = ultimo DAC A, PV[2] = ultimo DAC C */

#define IO16(a)     (*(volatile u16 *)(a))
#define A_ADC       0x020000UL
#define A_DACA      0x02000AUL
#define A_DACC      0x02000CUL
#define A_L20       0x020020UL
#define A_L18       0x020018UL
#define A_PORTB     0x020028UL
#define A_PORTA     0x020030UL
#define RTC_RD      0x0100U      /* v2: leitura do I/O em J2-29 = porta A bit 8 ($020030) */
#define A_DU_IP     0xFA001BUL
#define A_DU_SOPR   0xFA001CUL
#define A_DU_ROPR   0xFA001EUL
#define ADC_CONVST  0x08U        /* OP3 do DUART = disparo do A/D */
#define ADC_RDY     0x10U        /* IP4 do DUART = A/D pronto (nivel 1) */

/* ---- RTC I2C (DS3231 / DS1307, endereco $68) soldado na placa -------------------------------------------------------------
 *  SCL  = J1-30 : saida $020020 bit 10, via latch (INVERTIDA: bit = 1 puxa a linha para BAIXO)
 *  SDA  = J1-48 : saida $020020 bit 7,  via latch (idem).  Leitura do SDA: J1-23 = porta B bit 6 ($020028; o 74LS240 inverte).
 *  Os pull-ups de 4,7 kohm para +5 V vem no modulo (se nao tiver, ponha 2 resistores).  +5 V no J7-19, GND no J1-9.
 *  $020020 tambem seleciona o canal do A/D (bits 12-15): o relogio deixa o latch em 0 ao terminar (como o ADC).           */
#define I2C_SDA     0x0080U
#define I2C_SCL     0x0400U
#define I2C_RD      0x0040U
#define RTC_ADDR    0x68U

static void nl(void) { x_putc(13); x_putc(10); }
static void prs(const char *s) { while (*s) { if (*s == '\n') x_putc(13); x_putc(*s); s++; } }
static void hexn(u32 v, int n) { int i, d; for (i = n - 1; i >= 0; i--) { d = (int)((v >> (i * 4)) & 15); x_putc(d < 10 ? '0' + d : 'A' + d - 10); } }
static void decout(u32 v) { char b[12]; int i = 0; if (!v) { x_putc('0'); return; } while (v) { b[i++] = (char)('0' + v % 10); v /= 10; } while (i) x_putc(b[--i]); }
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
static int dnum(char **pp, u32 *v)
{
    char *p = skp(*pp); u32 r = 0; int n = 0;
    while (*p >= '0' && *p <= '9') { r = r * 10 + (u32)(*p - '0'); p++; n++; }
    *pp = p; *v = r; return n;
}
static int word(char *p, const char *w)       /* palavra inteira, sem distinguir caixa */
{
    while (*w) { if (up(*p) != *w) return 0; p++; w++; }
    return (*p == 0 || *p == ' ');
}
static char *after(char *p, const char *w) { while (*w) { p++; w++; } return p; }
static int abort_key(void) { if (x_kbhit()) { x_getc(); return 1; } return 0; }
static void udelay(u32 n) { volatile u32 d; for (d = 0; d < n; d++) ; }

/* ================================================================ A/D */
static u16 adc_read(int ch, int *rdy)
{
    u16 v; int tent = 0;
    IO16(A_L20) = (u16)(0x8000U | ((u16)(ch & 7) << 12));
    udelay(200);                                   /* assentamento do multiplexador (~ms) */
    while (!(*(volatile u8 *)A_DU_IP & ADC_RDY) && tent < 2) { (void)IO16(A_ADC); tent++; }
    *rdy = (*(volatile u8 *)A_DU_IP & ADC_RDY) ? 1 : 0;
    IO16(A_DU_SOPR) = ADC_CONVST; IO16(A_DU_ROPR) = ADC_CONVST;      /* pulso de disparo (igual ao firmware original) */
    udelay(8);
    v = (u16)(IO16(A_ADC) & 0x0FFFU);
    return v;
}
static void adc_done(void) { IO16(A_L20) = 0; }
static u32 adc_mv(u16 raw) { return ((u32)raw * 5000UL) / 4096UL; }
static void adc_line(int ch, u16 v, int rdy)
{
    prs("canal "); x_putc('0' + ch); prs(": $"); hexn(v, 3); prs("  ("); decout(v); prs(")  ~"); decout(adc_mv(v)); prs(" mV");
    if (!rdy) prs("   [IP4=0: A/D nao estava pronto]");
    nl();
}
static void cmd_adc(char *p)
{
    u32 c; int ch, rdy; u16 v;
    p = skp(p);
    if (*p == 0) {
        prs("A/D AD7875 (12 bits, $020000): 1 leitura de cada canal (mV supondo 0-5 V, a confirmar)\n");
        for (ch = 0; ch < 8; ch++) { v = adc_read(ch, &rdy); adc_line(ch, v, rdy); }
        adc_done(); return;
    }
    if (!dnum(&p, &c) || c > 7) { prs("Uso: ADC [canal 0-7]   (sem canal le os 8)\n"); return; }
    ch = (int)c;
    v = adc_read(ch, &rdy); adc_done();
    adc_line(ch, v, rdy);
}

/* ================================================================ D/A */
static void dac_show(void)
{
    if (PV[0] != 0x600D) { prs("DAC A ($02000A) e DAC C ($02000C): nada gravado desde o reset (nao podem ser lidos de volta)\n"); return; }
    prs("Ultimo valor gravado (os DACs nao podem ser lidos de volta):\n");
    prs("  DAC A ($02000A): $"); hexn(PV[1], 3); prs("  ("); decout(PV[1]); prs(")  ~"); decout(((u32)PV[1] * 5000UL) / 4095UL); prs(" mV (escala 5000 do firmware)\n");
    prs("  DAC C ($02000C): $"); hexn(PV[2], 3); prs("  ("); decout(PV[2]); prs(")  = "); decout(((u32)PV[2] * 125000UL) / 4095UL); prs(" un. (escala 125000 do firmware)\n");
}
static void cmd_dac(char *p)
{
    u32 v; int w, mv = 0;
    p = skp(p);
    if (*p == 0) { dac_show(); return; }
    w = up(*p);
    if (w != 'A' && w != 'C') { prs("Uso: DAC [A|C [valor_hex | M milivolts]]   (sem argumentos mostra os valores)\n"); return; }
    p = skp(p + 1);
    if (up(*p) == 'M') { mv = 1; p++; if (!dnum(&p, &v)) { prs("Uso: DAC A M 2500\n"); return; } }
    else if (!num(&p, &v)) { prs("Uso: DAC A|C valor_hex   ou   DAC A|C M valor_decimal\n"); return; }
    if (mv) v = (v * 4095UL) / (w == 'A' ? 5000UL : 125000UL);
    if (v > 0xFFFUL) { prs("Valor fora da faixa: o DAC tem 12 bits (000-FFF)\n"); return; }
    if (PV[0] != 0x600D) { PV[0] = 0x600D; PV[1] = 0; PV[2] = 0; }
    if (w == 'A') { IO16(A_DACA) = (u16)v; PV[1] = (u16)v; } else { IO16(A_DACC) = (u16)v; PV[2] = (u16)v; }
    prs("DAC "); x_putc(w); prs(" <- $"); hexn(v, 3); prs("  ("); decout(v); prs(")\n");
}

/* ================================================================ RTC I2C */
static void sda_scl(int sda, int scl) { IO16(A_L20) = (u16)((sda ? 0 : I2C_SDA) | (scl ? 0 : I2C_SCL)); udelay(4); }   /* 1 = solta (alto) */
static int  sda_in(void) { return (IO16(A_PORTB) & I2C_RD) ? 0 : 1; }       /* 1 = linha em nivel alto (74LS240 inverte) */
static void i2c_start(void) { sda_scl(1, 1); sda_scl(0, 1); sda_scl(0, 0); }
static void i2c_stop(void)  { sda_scl(0, 0); sda_scl(0, 1); sda_scl(1, 1); IO16(A_L20) = 0; }
static int  i2c_wbyte(u8 v)                          /* devolve 1 se houve ACK */
{
    int i, ack;
    for (i = 7; i >= 0; i--) { int b = (v >> i) & 1; sda_scl(b, 0); sda_scl(b, 1); sda_scl(b, 0); }
    sda_scl(1, 0); sda_scl(1, 1); ack = !sda_in(); sda_scl(1, 0);
    return ack;
}
static u8 i2c_rbyte(int ack)
{
    int i; u8 r = 0;
    sda_scl(1, 0);
    for (i = 7; i >= 0; i--) { sda_scl(1, 1); if (sda_in()) r |= (u8)(1 << i); sda_scl(1, 0); }
    sda_scl(ack ? 0 : 1, 0); sda_scl(ack ? 0 : 1, 1); sda_scl(ack ? 0 : 1, 0); sda_scl(1, 0);
    return r;
}
static int rtc_read(u8 reg, u8 *d, int n)            /* 1 = ok */
{
    int i;
    i2c_start();
    if (!i2c_wbyte((u8)(RTC_ADDR << 1)) || !i2c_wbyte(reg)) { i2c_stop(); return 0; }
    i2c_start();
    if (!i2c_wbyte((u8)((RTC_ADDR << 1) | 1))) { i2c_stop(); return 0; }
    for (i = 0; i < n; i++) d[i] = i2c_rbyte(i + 1 < n);
    i2c_stop();
    return 1;
}
static int rtc_write(u8 reg, const u8 *d, int n)
{
    int i, ok;
    i2c_start();
    ok = i2c_wbyte((u8)(RTC_ADDR << 1)) && i2c_wbyte(reg);
    for (i = 0; ok && i < n; i++) ok = i2c_wbyte(d[i]);
    i2c_stop();
    return ok;
}
static int bcdok(u8 v) { return (v & 15) <= 9 && (v >> 4) <= 9; }
static u8 tobcd(u32 v) { return (u8)(((v / 10) << 4) | (v % 10)); }
static u32 frombcd(u8 v) { return (u32)((v >> 4) * 10 + (v & 15)); }
static void p2(u32 v) { x_putc('0' + (int)(v / 10)); x_putc('0' + (int)(v % 10)); }
static const char DOW[] = "segterquaquisexsabdom";
static int dow_of(u32 y, u32 m, u32 d)               /* 1=segunda ... 7=domingo (y = ano completo) */
{
    static const int t[12] = { 0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4 };
    int dw; u32 yy = y;
    if (m < 3) yy--;
    dw = (int)((yy + yy / 4 - yy / 100 + yy / 400 + (u32)t[m - 1] + d) % 7);   /* 0 = domingo */
    return dw == 0 ? 7 : dw;
}
static int rtc_valid(const u8 *r)       /* valores de calendario possiveis e chip rodando (CH = 0, modo 24 h) */
{
    u32 s, mi, h, d, mo;
    if ((r[0] & 0x80) || (r[2] & 0x40)) return 0;
    if (!bcdok(r[0] & 0x7F) || !bcdok(r[1]) || !bcdok(r[2] & 0x3F) || !bcdok(r[4]) || !bcdok(r[5]) || !bcdok(r[6])) return 0;
    s = frombcd(r[0] & 0x7F); mi = frombcd(r[1]); h = frombcd(r[2] & 0x3F); d = frombcd(r[4]); mo = frombcd(r[5]);
    return s <= 59 && mi <= 59 && h <= 23 && d >= 1 && d <= 31 && mo >= 1 && mo <= 12 && r[3] >= 1 && r[3] <= 7;
}
static int rtc_get(u8 *r)           /* r[0..6]; devolve 1 se leu e os valores sao validos */
{
    if (!rtc_read(0x00, r, 7)) return 0;
    return rtc_valid(r);
}
static void cmd_rtc(char *p)
{
    u8 r[19]; u32 a[6]; int i, n = 0, ok;
    p = skp(p);
    if (word(p, "TESTE") || word(p, "SCAN")) {
        int sda0, ach = 0, ack;
        sda_scl(1, 1); sda0 = sda_in();
        prs("Linha SDA em repouso (J1-23): "); prs(sda0 ? "ALTA (ok)\n" : "BAIXA (falta pull-up, curto ou modulo ausente)\n");
        prs("Dispositivos I2C que respondem (varredura $08-$77):");
        for (i = 8; i < 0x78; i++) { i2c_start(); ack = i2c_wbyte((u8)(i << 1)); i2c_stop(); if (ack) { prs(" $"); hexn((u32)i, 2); ach++; } }
        if (!ach) prs(" nenhum");
        nl();
        prs(rtc_read(0x00, r, 7) ? "RTC em $68: RESPONDE\n" : "RTC em $68: SEM RESPOSTA (confira SCL J1-30, SDA J1-48 e leitura J1-23, +5 V, GND)\n");
        return;
    }
    if (word(p, "RAW")) {
        if (!rtc_read(0x00, r, 19)) { prs("sem resposta do RTC\n"); return; }
        prs("Registradores $00-$12:"); for (i = 0; i < 19; i++) { if (i % 8 == 0) prs("\n  "); hexn(r[i], 2); x_putc(' '); } nl();
        return;
    }
    if (word(p, "SET")) {
        u8 w[7];
        p = skp(after(p, "SET"));
        while (n < 6) { p = skp(p); if (!dnum(&p, &a[n])) break; n++; while (*p && !(*p >= '0' && *p <= '9')) p++; }
        if (n != 6) { prs("Uso: RTC SET aa mm dd hh mm ss   (decimal; ex.: RTC SET 26 11 15 12 30 00)\n"); return; }
        if (a[0] >= 2000) a[0] -= 2000;
        if (a[0] > 99 || a[1] < 1 || a[1] > 12 || a[2] < 1 || a[2] > 31 || a[3] > 23 || a[4] > 59 || a[5] > 59) { prs("Data/hora invalida\n"); return; }
        w[0] = tobcd(a[5]); w[1] = tobcd(a[4]); w[2] = tobcd(a[3]); w[3] = (u8)dow_of(2000 + a[0], a[1], a[2]); w[4] = tobcd(a[2]); w[5] = tobcd(a[1]); w[6] = tobcd(a[0]);
        if (!rtc_write(0x00, w, 7)) { prs("sem ACK do RTC ao gravar\n"); return; }
        prs("Relogio gravado. Conferindo...\n");
    } else if (*p) { prs("Uso: RTC | RTC SET aa mm dd hh mm ss | RTC TESTE | RTC RAW   (? RTC)\n"); return; }
    ok = rtc_get(r);
    if (!ok) { prs("RTC sem resposta valida (bytes: "); for (i = 0; i < 7; i++) { hexn(r[i], 2); x_putc(' '); } prs(")\n  Use RTC TESTE para ver a linha SDA e os dispositivos presentes.\n"); return; }
    prs("RTC I2C: "); p2(frombcd(r[4] & 0x3F)); x_putc('/'); p2(frombcd(r[5] & 0x1F)); prs("/20"); p2(frombcd(r[6]));
    x_putc(' ');
    if (r[3] >= 1 && r[3] <= 7) { int d = (r[3] - 1) * 3; x_putc(DOW[d]); x_putc(DOW[d + 1]); x_putc(DOW[d + 2]); }
    x_putc(' '); p2(frombcd(r[2] & 0x3F)); x_putc(':'); p2(frombcd(r[1] & 0x7F)); x_putc(':'); p2(frombcd(r[0] & 0x7F)); nl();
    if (r[0] & 0x80) prs("  AVISO: bit CH=1: o relogio esta PARADO (DS1307): use RTC SET.\n");
    if (r[2] & 0x40) prs("  (modo 12 horas)\n");
}

/* ================================================================ RELOGIO NO LCD (linha 4), atualizado so no laco ocioso do monitor
 * O monitor (getline, linha vazia) zera o contador RLC = RLFIRST ($1714 -> $1710, negativo) e chama per_tick a cada volta do laco de espera.
 * So depois de ~2 s de silencio total (contador chega a 0) o relogio le o RTC; depois repete a cada RL_EVERY voltas (~10 s).
 * Le so o registrador de MINUTOS (1 byte, ~1 ms) e so redesenha quando o minuto muda.  Nunca roda com texto chegando pela serial. */
#define RL_MARK     0xC10CU
#define RL_FIRST    8000L                     /* ~2 s: medido com RELOGIO CAL em 15/Nov: 0,24 ms por volta (4170 voltas/s) */
#define RL_EVERY    20000L                    /* ~5 s entre leituras */
#define RLC         (*(volatile long *)0x1710)
#define RLF         (*(volatile long *)0x1714)
#define rl_txt ((char *)0x1720)                 /* 24 bytes de RAM livre ($1720-$1737): variavel estatica cairia na flash */
static void rl_init(void) { PV[4] = RL_MARK; PV[3] = 1; PV[6] = 0xFFFF; RLF = -RL_FIRST; RLC = -RL_FIRST; }
static void rl_draw(const u8 *r)               /* r[0..6] do DS1307: "dd/mm/aa  hh:mm        " */
{
    int i = 0;
    rl_txt[i++] = (char)('0' + (r[4] >> 4 & 3)); rl_txt[i++] = (char)('0' + (r[4] & 15)); rl_txt[i++] = '/';
    rl_txt[i++] = (char)('0' + (r[5] >> 4 & 1)); rl_txt[i++] = (char)('0' + (r[5] & 15)); rl_txt[i++] = '/';
    rl_txt[i++] = (char)('0' + (r[6] >> 4 & 15)); rl_txt[i++] = (char)('0' + (r[6] & 15)); rl_txt[i++] = ' '; rl_txt[i++] = ' ';
    rl_txt[i++] = (char)('0' + (r[2] >> 4 & 3)); rl_txt[i++] = (char)('0' + (r[2] & 15)); rl_txt[i++] = ':';
    rl_txt[i++] = (char)('0' + (r[1] >> 4 & 7)); rl_txt[i++] = (char)('0' + (r[1] & 15));
    while (i < 20) rl_txt[i++] = ' ';
    rl_txt[i] = 0;
    x_lcd_at(3, 0, rl_txt);
}
void per_tick(void)
{
    u8 r[7];
    if (PV[4] != RL_MARK) { rl_init(); return; }
    if (!PV[3]) return;
    if (++RLC < 0) return;                      /* ainda dentro dos ~2 s de silencio */
    RLC = -RL_EVERY;
    if (!rtc_read(0x01, r, 1)) return;
    if (PV[6] == (u16)(r[0] & 0x7F)) return;     /* o minuto nao mudou */
    if (!rtc_read(0x00, r, 7)) return;
    PV[6] = (u16)(r[1] & 0x7F);
    if (rtc_valid(r)) rl_draw(r); else x_lcd_at(3, 0, "ACERTAR RELOGIO     ");
}
static void cmd_relogio(char *p)
{
    p = skp(p);
    if (PV[4] != RL_MARK) rl_init();
    if (word(p, "CAL")) {
        u32 i; prs("RELOGIO CAL: 100000 voltas do laco ocioso. Meca o tempo entre as duas linhas.\nINICIO\n");
        for (i = 0; i < 100000UL; i++) { x_strobe(); if (x_kbhit()) break; per_tickentry(); }
        prs("FIM\n"); return;
    }
    if (word(p, "ON")) { PV[3] = 1; RLC = -1L; PV[6] = 0xFFFF; }
    else if (word(p, "OFF")) PV[3] = 0;
    else if (*p) { prs("Uso: RELOGIO [ON | OFF | CAL]\n"); return; }
    prs("Relogio no LCD (linha 4): "); prs(PV[3] ? "LIGADO" : "DESLIGADO"); prs("  (so atualiza com o monitor ocioso no prompt, de minuto em minuto)\n");
}

/* ================================================================ ADL: registra amostras do A/D em texto (CSV) na RAM2 */
static u32 putdec(volatile char *w, u32 len, u32 q)
{
    char b[12]; int k = 0;
    if (!q) b[k++] = '0';
    while (q) { b[k++] = (char)('0' + q % 10); q /= 10; }
    while (k) w[len++] = b[--k];
    return len;
}
static void cmd_adl(char *p)
{
    u32 c, n, ms = 100, i, t, len, mv; int ch, rdy, j; u16 v; volatile char *w = (volatile char *)RAM2LO; const char *s;
    ext_init();
    if (!G.ram2) { prs("ADL precisa da RAM2 ($040000)\n"); return; }
    p = skp(p);
    if (!dnum(&p, &c) || c > 7 || !dnum(&p, &n)) { prs("Uso: ADL canal(0-7) amostras [intervalo_ms]   (decimal; ex.: ADL 2 600 100)\n  Guarda texto CSV em $040000 (RAM2) e diz como gravar no cartao SD.\n"); return; }
    ch = (int)c;
    if (dnum(&p, &t)) ms = t;
    if (n < 1) n = 1;
    if (n > 6000) n = 6000;                                    /* ate ~100 KB de texto */
    prs("Registrando "); decout(n); prs(" amostras do canal "); x_putc('0' + ch); prs(" a cada ~"); decout(ms); prs(" ms (qualquer tecla aborta)...\n");
    len = 0;
    s = "amostra;canal;bruto;mV\r\n"; while (*s) w[len++] = *s++;
    for (i = 0; i < n; i++) {
        if (abort_key()) { prs("Interrompido.\n"); n = i; break; }
        x_strobe();
        v = adc_read(ch, &rdy); mv = adc_mv(v);
        len = putdec(w, len, i); w[len++] = ';'; w[len++] = (char)('0' + ch); w[len++] = ';';
        len = putdec(w, len, v); w[len++] = ';'; len = putdec(w, len, mv); w[len++] = 13; w[len++] = 10;
        for (j = 0; j < (int)ms; j++) { udelay(180); if ((j & 15) == 0) x_strobe(); }
    }
    adc_done();
    prs("Pronto: "); decout(n); prs(" linhas, "); decout(len); prs(" bytes ($"); hexn(len, 5); prs(") em $040000.\n");
    prs("Gravar no cartao SD:  G F84000  (shell do cartao), depois:  W ADL.CSV 40000 "); hexn(len, 5); prs("\n");
}

/* ================================================================ ajuda */
static const char H_ADC[] =
    "ADC [canal]  /  ADL canal amostras [ms]  -  CONVERSOR A/D AD7875 (12 bits)\n"
    "\n"
    "  ADC           le uma vez cada um dos 8 canais e mostra o valor bruto ($000-$FFF),\n"
    "                em decimal e em mV supondo 0-5 V (a confirmar na bancada).\n"
    "  ADC 2         le so o canal 2.\n"
    "  ADL 2 600 100 registra 600 amostras do canal 2, uma a cada ~100 ms, como texto\n"
    "                CSV em $040000 (RAM2). Ao fim mostra o tamanho e o comando para gravar\n"
    "                no cartao SD:  G F84000  e depois  W ADL.CSV 40000 <tamanho>\n"
    "  Origem: firmware original. Disparo por pulso no pino OP3 do DUART; canal nos bits\n"
    "  14-12 de $020020 (o bit 15 fica ligado durante a leitura); resultado em $020000.\n"
    "  Ao terminar $020020 volta a 0. Os outros pinos de saida do DUART nao sao tocados.\n";
static const char H_DAC[] =
    "DAC [A|C [valor | M milivolts]]  -  CONVERSORES D/A DE 12 BITS\n"
    "\n"
    "  DAC           mostra os ultimos valores gravados (os DACs nao podem ser lidos).\n"
    "  DAC A 800     grava o codigo $800 (metade da escala) no DAC A ($02000A).\n"
    "  DAC A M 2500  grava o codigo equivalente a 2500 mV (escala do firmware: 5000 mV).\n"
    "  DAC C ...     idem para o DAC C ($02000C); escala do firmware: 125000 unidades.\n"
    "  CUIDADO: a saida analogica vai para o conector do laser/placa de potencia.\n";
static const char H_RTC[] =
    "RTC [SET aa mm dd hh mm ss | TESTE | RAW]  -  RELOGIO I2C (DS1307; o DS3231 tambem serve; endereco $68)\n"
    "\n"
    "  RTC                         mostra data e hora.\n"
    "  RTC SET aa mm dd hh mm ss   acerta, em decimal (ex.: RTC SET 26 11 15 12 30 00); calcula o dia da semana.\n"
    "  RTC TESTE                   mostra o nivel da linha SDA em repouso e varre o barramento I2C ($08-$77); RTC SCAN faz o mesmo.\n"
    "  RTC RAW                     despeja os registradores $00-$12 do chip.\n"
    "  Ligacao: SCL = J1-30 ($020020 bit 10); SDA = J1-48 (saida, $020020 bit 7) emendado com J1-23 (leitura, porta B bit 6).\n"
    "  As duas saidas sao bits do latch $020020 (nivel baixo = puxa a linha; o modulo traz os pull-ups). +5 V no J7-19, GND no J1-9.\n"
    "\n"
    "  RELOGIO [ON | OFF | CAL]    hora na linha 4 do LCD (detalhes: ? RELOGIO)\n\n";
static const char H_REL[] =
    "RELOGIO [ON | OFF | CAL]  -  hora na linha 4 do LCD (dd/mm/aa  hh:mm)\n"
    "\n"
    "  RELOGIO           mostra se esta LIGADO ou DESLIGADO (padrao: LIGADO a cada reset).\n"
    "  RELOGIO ON | OFF  liga ou desliga.   RELOGIO CAL  mede o laco de espera (100000 voltas; o tempo sai no log da ponte).\n"
    "  So atualiza com o monitor parado no prompt (~2 s sem digitar, depois a cada ~5 s); nunca durante SD, A/D ou gravacao.\n"
    "  Com o chip parado ou com valores impossiveis aparece ACERTAR RELOGIO: use RTC SET.\n\n";

extern void x_basic(void), x_cpm(void), x_forth(void);
static const char H_APP[] =
    "BASIC | CPM | FORTH  -  inicia a aplicacao sem passar pelo menu do banco 1\n"
    "\n"
    "  BASIC   EhBASIC com SDFS (banco 7; copia o driver para a RAM $50000)\n"
    "  CPM     CP/M-68K com discos no cartao SD (banco 7)\n"
    "  FORTH   eForth (banco 5; confere o CRC32 antes)\n"
    "  RESET volta ao stub do banco 0 e ao menu do banco 1.\n\n";

int per_main(char *line)
{
    char *w = skp(line);
    if (*w == '?' || up(*w) == 'H') {
        char *t = skp(w + 1);
        if (word(t, "ADC") || word(t, "ADL")) { prs(H_ADC); return 1; }
        if (word(t, "DAC")) { prs(H_DAC); return 1; }
        if (word(t, "RTC")) { prs(H_RTC); return 1; }
        if (word(t, "RELOGIO")) { prs(H_REL); return 1; }
        if (word(t, "BASIC") || word(t, "CPM") || word(t, "FORTH")) { prs(H_APP); return 1; }
        return 0;
    }
    if (word(w, "ADC")) { cmd_adc(after(w, "ADC")); return 1; }
    if (word(w, "ADL")) { cmd_adl(after(w, "ADL")); return 1; }
    if (word(w, "DAC")) { cmd_dac(after(w, "DAC")); return 1; }
    if (word(w, "RTC")) { cmd_rtc(after(w, "RTC")); return 1; }
    if (word(w, "RELOGIO")) { cmd_relogio(after(w, "RELOGIO")); return 1; }
    if (word(w, "BASIC")) { prs("Iniciando o BASIC...\n"); x_basic(); return 1; }
    if (word(w, "CPM")) { prs("Iniciando o CP/M-68K...\n"); x_cpm(); return 1; }
    if (word(w, "FORTH")) { prs("Iniciando o eForth...\n"); x_forth(); return 1; }
    return 0;
}
