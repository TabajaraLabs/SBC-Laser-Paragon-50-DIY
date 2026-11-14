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
#define A_DU_IP     0xFA001BUL
#define A_DU_SOPR   0xFA001CUL
#define A_DU_ROPR   0xFA001EUL
#define ADC_CONVST  0x08U        /* OP3 do DUART = disparo do A/D */
#define ADC_RDY     0x10U        /* IP4 do DUART = A/D pronto (nivel 1) */

/* ---- DS1302 no barramento do cartao SD.  PINOS PROVISORIOS: ajustar aqui quando o hardware for definido ---------------------
 *  SCLK = SCK do SD   (latch $020018 bit 0, J1-28)
 *  I/O  = MOSI do SD  (bit 1, J1-26) ligado ao pino I/O do DS1302 por um resistor de ~1 kohm; o mesmo pino I/O vai direto a
 *         MISO ($020028 bit 0, J1-7; o 74LS240 inverte).  O cartao SD solta o MISO quando seu CS esta em nivel alto.
 *  CE   = PROVISORIO: bit 10 do latch $020018 (J2-37), ativo em nivel ALTO (RST/CE do DS1302).  Troque RTC_CE se usar outro pino.
 *  O CS do SD (bit 2) fica sempre em 1 (cartao desselecionado) durante o acesso ao relogio.                                */
#define RTC_SCK     0x0001U
#define RTC_IO      0x0002U
#define RTC_CE      0x0400U      /* <<< ROTULO TEMPORARIO do CE do DS1302 */
#define RTC_IDLE    0x0004U      /* CS do SD em 1, todo o resto em 0 */

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

/* ================================================================ DS1302 */
static void rtc_w(u16 sck, int io, int ce) { IO16(A_L18) = (u16)(RTC_IDLE | sck | (io ? RTC_IO : 0) | (ce ? RTC_CE : 0)); }
static void rtc_begin(void) { rtc_w(0, 0, 0); udelay(2); rtc_w(0, 0, 1); udelay(2); }
static void rtc_end(void)   { rtc_w(0, 0, 0); udelay(2); IO16(A_L18) = RTC_IDLE; }
static void rtc_wbyte(u8 v)
{
    int i, b;
    for (i = 0; i < 8; i++) { b = (v >> i) & 1; rtc_w(0, b, 1); rtc_w(RTC_SCK, b, 1); rtc_w(0, b, 1); }   /* sobe = grava; termina com SCK baixo */
}
static u8 rtc_rbyte(int more)
{
    int i; u8 r = 0;
    for (i = 0; i < 8; i++) {
        if (i) { rtc_w(RTC_SCK, 1, 1); rtc_w(0, 1, 1); }
        udelay(1);
        if (!(IO16(A_PORTB) & 1)) r |= (u8)(1 << i);        /* 74LS240 inverte: 0 lido = nivel alto no pino */
    }
    if (more) { rtc_w(RTC_SCK, 1, 1); rtc_w(0, 1, 1); }      /* proximo byte do burst */
    return r;
}
static u8 rtc_rd1(u8 cmd) { u8 r; rtc_begin(); rtc_wbyte(cmd); r = rtc_rbyte(0); rtc_end(); return r; }
static void rtc_wr1(u8 cmd, u8 v) { rtc_begin(); rtc_wbyte(cmd); rtc_wbyte(v); rtc_end(); }
static void rtc_burst_rd(u8 cmd, u8 *d, int n) { int i; rtc_begin(); rtc_wbyte(cmd); for (i = 0; i < n; i++) d[i] = rtc_rbyte(i + 1 < n); rtc_end(); }
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
static int rtc_get(u8 *r)           /* r[0..7]; devolve 1 se os valores parecem validos */
{
    int i, ok = 1; u8 v;
    rtc_burst_rd(0xBF, r, 8);
    for (i = 0; i < 7; i++) {
        v = r[i]; if (i == 0) v &= 0x7F; if (i == 2) v &= 0x3F;
        if (!bcdok(v)) ok = 0;
    }
    return ok;
}
static void cmd_rtc(char *p)
{
    u8 r[8]; u32 a[6]; int i, n = 0, ok;
    p = skp(p);
    if (word(p, "TESTE")) {
        static const u8 pat[3] = { 0xA5, 0x5A, 0x00 };
        u8 sv = rtc_rd1(0xC1), lido; int bad = 0;
        prs("Teste da interface DS1302 pela RAM do chip (CE provisorio = bit 10 de $020018):\n");
        for (i = 0; i < 3; i++) {
            rtc_wr1(0xC0, pat[i]); lido = rtc_rd1(0xC1);
            prs("  gravou $"); hexn(pat[i], 2); prs("  leu $"); hexn(lido, 2); if (lido != pat[i]) { prs("  <-- ERRO"); bad = 1; } nl();
        }
        rtc_wr1(0xC0, sv);
        prs(bad ? "FALHA: sem resposta do DS1302 (ligacao, CE, resistor de I/O, alimentacao?)\n" : "OK: o DS1302 responde (escrita e leitura da RAM conferem)\n");
        return;
    }
    if (word(p, "RAW")) {
        u8 ram[31];
        rtc_burst_rd(0xBF, r, 8); rtc_burst_rd(0xFF, ram, 31);
        prs("Registradores 0-7: "); for (i = 0; i < 8; i++) { hexn(r[i], 2); x_putc(' '); } nl();
        prs("RAM 0-30:         "); for (i = 0; i < 31; i++) { hexn(ram[i], 2); x_putc(' '); if (i == 15) prs("\n                   "); } nl();
        return;
    }
    if (word(p, "SET")) {
        p = skp(after(p, "SET"));
        while (n < 6) { p = skp(p); if (!dnum(&p, &a[n])) break; n++; while (*p && !(*p >= '0' && *p <= '9')) p++; }
        if (n != 6) { prs("Uso: RTC SET aa mm dd hh mm ss   (decimal; ex.: RTC SET 26 11 14 12 30 00)\n"); return; }
        if (a[0] >= 2000) a[0] -= 2000;
        if (a[0] > 99 || a[1] < 1 || a[1] > 12 || a[2] < 1 || a[2] > 31 || a[3] > 23 || a[4] > 59 || a[5] > 59) { prs("Data/hora invalida\n"); return; }
        rtc_wr1(0x8E, 0x00);                                   /* desprotege */
        rtc_begin(); rtc_wbyte(0xBE);                          /* burst de escrita: s min h dia mes dow ano wp */
        rtc_wbyte(tobcd(a[5])); rtc_wbyte(tobcd(a[4])); rtc_wbyte(tobcd(a[3])); rtc_wbyte(tobcd(a[2])); rtc_wbyte(tobcd(a[1]));
        rtc_wbyte((u8)dow_of(2000 + a[0], a[1], a[2])); rtc_wbyte(tobcd(a[0])); rtc_wbyte(0x00);
        rtc_end();
        prs("Relogio gravado. Conferindo...\n");
    } else if (*p) { prs("Uso: RTC | RTC SET aa mm dd hh mm ss | RTC TESTE | RTC RAW   (? RTC)\n"); return; }
    ok = rtc_get(r);
    if (!ok) { prs("DS1302 sem resposta valida (bytes: "); for (i = 0; i < 8; i++) { hexn(r[i], 2); x_putc(' '); } prs(")\n  Confira a ligacao (CE provisorio = bit 10 de $020018, J2-37) e use RTC TESTE.\n"); return; }
    prs("RTC DS1302: "); p2(frombcd(r[3] & 0x3F)); x_putc('/'); p2(frombcd(r[4] & 0x1F)); prs("/20"); p2(frombcd(r[6]));
    x_putc(' ');
    if (r[5] >= 1 && r[5] <= 7) { int d = (r[5] - 1) * 3; x_putc(DOW[d]); x_putc(DOW[d + 1]); x_putc(DOW[d + 2]); }
    x_putc(' '); p2(frombcd(r[2] & 0x3F)); x_putc(':'); p2(frombcd(r[1] & 0x7F)); x_putc(':'); p2(frombcd(r[0] & 0x7F)); nl();
    if (r[0] & 0x80) prs("  AVISO: bit CH=1: o relogio esta PARADO (use RTC SET).\n");
    if (r[2] & 0x80) prs("  (modo 12 horas)\n");
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
    "RTC [SET aa mm dd hh mm ss | TESTE | RAW]  -  RELOGIO DS1302 (codigo pronto, sem hardware ainda)\n"
    "\n"
    "  RTC           mostra data e hora.            RTC SET 26 11 14 12 30 00  acerta (decimal).\n"
    "  RTC TESTE     escreve/le a RAM de 31 bytes do chip para provar a ligacao.\n"
    "  RTC RAW       despeja os registradores e a RAM do chip.\n"
    "  Ligacao provisoria: SCLK = SCK do SD (bit 0 de $020018); I/O = MOSI (bit 1) via\n"
    "  resistor de ~1k e direto a MISO ($020028 bit 0); CE (ativo alto) = bit 10 de $020018\n"
    "  (J2-37) - ROTULO TEMPORARIO RTC_CE no fonte per_v1.c, mude quando o pino for definido.\n";

int per_main(char *line)
{
    char *w = skp(line);
    if (*w == '?' || up(*w) == 'H') {
        char *t = skp(w + 1);
        if (word(t, "ADC") || word(t, "ADL")) { prs(H_ADC); return 1; }
        if (word(t, "DAC")) { prs(H_DAC); return 1; }
        if (word(t, "RTC")) { prs(H_RTC); return 1; }
        return 0;
    }
    if (word(w, "ADC")) { cmd_adc(after(w, "ADC")); return 1; }
    if (word(w, "ADL")) { cmd_adl(after(w, "ADL")); return 1; }
    if (word(w, "DAC")) { cmd_dac(after(w, "DAC")); return 1; }
    if (word(w, "RTC")) { cmd_rtc(after(w, "RTC")); return 1; }
    return 0;
}
