# gera Paragon50_Pinos_J1_J2_J7_CIs_v1.pdf (folhas de mapeamento com multimetro)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
W, H = A4
OUT = 'Paragon50_Pinos_J1_J2_J7_CIs_v13.pdf'
c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle('PARAGON 50 - Pinos de J1, J2, J7 e dos CIs de E/S analogica')
GREEN = colors.Color(.85, .95, .85); YEL = colors.Color(1, .96, .8); GREY = colors.Color(.9, .9, .9); BLUE = colors.Color(.86, .92, 1)

def head(title, sub=None):
    c.setFont('Helvetica-Bold', 13); c.drawString(30, H-28, title)
    c.setFont('Helvetica', 7.5)
    if sub:
        k = 0
        for s_ in sub:
            for ln in simpleSplit(s_, 'Helvetica', 7.5, W-72):
                c.drawString(30, H-42-k*9.5, ln); k += 1

def table(cols, rows, y0, rh=13.2, fs=7, fills=None):
    """cols: [(titulo, largura)], rows: lista de listas; fills: lista de cores por linha"""
    x0 = 30; y = y0
    c.setFont('Helvetica-Bold', fs); c.setFillColor(colors.Color(.2, .2, .3))
    c.rect(x0, y-rh+3, sum(w for _, w in cols), rh, fill=1, stroke=0); c.setFillColor(colors.white)
    x = x0
    for t, w in cols: c.drawString(x+2, y-rh+6.5, t); x += w
    y -= rh
    for i, r in enumerate(rows):
        f = fills[i] if fills and fills[i] else None
        if f is not None: c.setFillColor(f); c.rect(x0, y-rh+3, sum(w for _, w in cols), rh, fill=1, stroke=0)
        c.setFillColor(colors.black); c.setFont('Helvetica', fs); x = x0
        for (t, w), v in zip(cols, r):
            c.drawString(x+2, y-rh+6.5, str(v)[:int(w/(fs*0.5))]); x += w
        c.setStrokeColor(colors.Color(.7, .7, .7)); c.setLineWidth(.3)
        c.line(x0, y-rh+3, x0+sum(w for _, w in cols), y-rh+3)
        y -= rh
    # linhas verticais
    x = x0; c.setStrokeColor(colors.Color(.6, .6, .6))
    for t, w in cols:
        c.line(x, y0+3, x, y+3); x += w
    c.line(x, y0+3, x, y+3)
    return y

def footer(n, legenda=True):
    c.setFont('Helvetica', 6.5); c.setFillColor(colors.black)
    if legenda:
        c.setFillColor(GREEN); c.rect(30, 22, 8, 7, fill=1, stroke=1); c.setFillColor(colors.black); c.drawString(41, 23.5, 'medido na placa')
        c.setFillColor(YEL); c.rect(110, 22, 8, 7, fill=1, stroke=1); c.setFillColor(colors.black); c.drawString(121, 23.5, 'inferido / a confirmar')
        c.setFillColor(BLUE); c.rect(210, 22, 8, 7, fill=1, stroke=1); c.setFillColor(colors.black); c.drawString(221, 23.5, 'GND / alimentacao')
    c.drawString(30, 12, 'Tabajara Labs - PARAGON 50 - 15/Nov/2026 - v13. Colunas em branco = para anotar com o multimetro (placa DESLIGADA, teste de continuidade).')
    c.drawRightString(W-30, 12, 'pag. %d' % n)

# ---------- dados J1 / J2 ----------
Q273 = {0: 2, 1: 5, 2: 6, 3: 9, 4: 12, 5: 15, 6: 16, 7: 19}
def lat(b): return 'Saida $020018 b%d' % b, '74LS273 %s pino %d (Q%d)' % ('U45 baixo?' if b < 8 else 'U39 alto?', Q273[b % 8], b % 8)
J1 = {1: ('GND', '', 'medido', ''), 2: ('GND', '', 'medido', ''), 9: ('GND', '', 'medido', ''), 50: ('GND', '', 'medido', ''),
      4: ('Entrada porta A b3 ($020030)', '74LS240 U44/U37 (pino ?)', 'medido', ''),
      7: ('Entrada porta B b0 ($020028)', '74LS240 U42/U48 (pino ?)', 'medido', 'MISO do SD'),
      10: (*lat(7), 'medido', 'LCD D6'), 14: (*lat(6), 'inferido', 'LCD D5; CONFERIR: medido U45 pino 2 (esperado pino 16)'), 15: (*lat(5), 'medido', 'LCD D4'),
      18: (*lat(4), 'medido', 'LCD RS'), 20: (*lat(3), 'medido', 'LCD E'), 24: (*lat(2), 'medido', 'CS do SD (nivel: bit=1 -> CS alto)'),
      26: (*lat(1), 'medido', 'MOSI (SD / I-O do DS1302)'), 28: (*lat(0), 'medido', 'SCK (SD / SCLK do DS1302)'),
      23: ('Entrada porta B b6', '74LS240 U42/U48 (pino ?)', 'medido', ''), 25: ('Entrada porta B b5', '74LS240 U42/U48 (pino ?)', 'medido', ''),
      27: ('Entrada porta B b4', '74LS240 U42/U48 (pino ?)', 'medido', 'SD_DET'), 31: ('Entrada porta B b3', '74LS240 U42/U48 (pino ?)', 'medido', 'botao do encoder'),
      33: ('Entrada porta B b2', '74LS240 U42/U48 (pino ?)', 'medido', 'botao EN1'), 35: ('Entrada porta B b1', '74LS240 U42/U48 (pino ?)', 'medido', 'botao EN2'),
      34: ('Entrada porta B b7', '74LS240 U42/U48 (pino ?)', 'medido', 'medido 15/Nov (330 ohm ao GND)'),
      48: ('Saida $020020 b7 (coletor aberto, INVERTIDA)', '74LS06 U47 pino 8 (4Y)', 'medido', 'precisa de pull-up'),
      11: ('Saida OUT2 do 8254 (U25)', 'U25 pino 17', 'medido', 'timer 2'),
      12: ('Entrada do inversor livre do 7406 (2A)', 'U41 pino 3', 'medido', 'saida em J1-32'),
      32: ('Saida do inversor livre do 7406 (2Y, col. aberto)', 'U41 pino 4', 'medido', 'inverte J1-12'),
      30: ('Saida $020020 b10 (coletor aberto, INVERTIDA)', 'U41 pino 6 (3Y)', 'medido', 'precisa de pull-up'),
      38: ('Entrada IP3 do DUART', 'U27 pino 2', 'medido', 'bit 3 de $FA001B'),
      40: ('Saida de inversor do U10 (3Y)', 'U10 pino 6', 'medido', 'entrada (pino 5) a achar'),
      13: ('so ruido (nao conectado)', '', 'medido', ''), 17: ('so ruido (nao conectado)', '', 'medido', ''), 29: ('sem resposta como entrada', '', 'medido', 'riscado na folha')}
J2 = {2: ('AGND', 'AGND (retorno do par 1)', 'medido', ''), 4: ('AGND', 'AGND (retorno do par 3)', 'medido', ''), 6: ('AGND', 'AGND (retorno do par 5)', 'medido', ''), 8: ('AGND', 'AGND (retorno do par 7)', 'medido', ''), 10: ('AGND', 'AGND (retorno do par 9)', 'medido', ''), 12: ('AGND', 'AGND (retorno do par 11)', 'medido', ''), 14: ('AGND', 'AGND (retorno do par 13)', 'medido', ''), 16: ('AGND', 'AGND (retorno do par 15)', 'medido', ''), 18: ('AGND', 'AGND (retorno do par 17)', 'medido', ''), 20: ('AGND', 'AGND (retorno do par 19)', 'medido', ''), 22: ('AGND', 'AGND (retorno do par 21)', 'medido', ''), 49: ('GND', '', 'medido', ''), 50: ('GND', '', 'medido', ''),
      11: ('sem sinal (livre; so o retorno AGND no pino 12)', '', 'medido', ''), 17: ('sem sinal (livre; so o retorno AGND no pino 18)', '', 'medido', ''),
      1: ('Entrada analogica S1 (mux U38)', 'RN6 p8-1k-p9; U38 p13', 'medido', '1 kohm em serie'),
      3: ('Entrada analogica S2 (mux U38)', 'RN6 p7-1k-p10; U38 p11', 'medido', '1 kohm em serie'),
      5: ('Entrada analogica S3 (mux U38)', 'RN6 p6-1k-p11; U38 p10', 'medido', '1 kohm em serie'),
      7: ('Entrada analogica S4 (mux U38)', 'RN6 p5-1k-p12; U38 p9', 'medido', '1 kohm em serie'),
      9: ('Entrada analogica S5 (mux U38)', 'RN6 p4-1k-p13; U38 p8', 'medido', '1 kohm em serie'),
      13: ('Entrada analogica S7 (mux U38)', 'RN6 p2-1k-p15; U38 p6', 'medido', '1 kohm em serie'),
      15: ('Entrada analogica S8 (mux U38)', 'RN6 p1-1k-p16; U38 p5', 'medido', '1 kohm em serie'),
      21: ('Saida DAC B do U24 (U31 pino 6) + entrada S6 do mux', 'U31 pino 6; RN6 p3-1k-p14; U38 p7', 'medido', 'DAC B com leitura de volta pelo A/D (S6)'),
      19: ('Saida DAC A do U24 (U32 pino 6)', 'U32 pino 6 (OP07CP)', 'medido', 'sem leitura de volta conhecida'),
      23: (*lat(15), 'medido', ''), 24: (*lat(14), 'medido', ''), 27: (*lat(13), 'medido', ''), 28: (*lat(12), 'medido', ''),
      30: (*lat(11), 'medido', ''), 37: (*lat(10), 'medido', 'CE do DS1302 (provisorio)'), 40: (*lat(9), 'medido', 'buzzer'),
      47: (*lat(8), 'medido', 'LCD D7')}
J1.update({p: ('nao conectado (confirmado)', '', 'medido', 'testado 15/Nov: sem resposta') for p in [3, 5, 6, 8, 16, 19, 21, 22, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 49]})
J2.update({p: ('Entrada porta A b%d ($020030)' % b, '74LS240 U44/U37 (pino ?)', 'medido', 'testado 15/Nov') for p, b in {39: 0, 42: 1, 41: 2, 43: 4, 45: 5, 46: 6, 48: 7, 29: 8, 32: 9, 31: 10, 34: 11, 33: 12, 35: 13, 36: 14, 38: 15}.items()})
J2.update({p: ('sem resposta como entrada', '', 'medido', 'testado 15/Nov: sem resposta') for p in (25, 26, 44)})
COLS = [('Pino', 26), ('Funcao / sinal', 150), ('E/S', 28), ('Pino do integrado', 120), ('Obs.', 112), ('ANOTAR: CI + pino', 99)]
def conn_page(name, data, n, extra):
    head('%s - conector de 50 pinos (IDC macho)' % name, [
        'Pinos IMPARES na coluna esquerda, PARES na direita (1-2 na mesma linha). Mapa por pino abaixo em ordem numerica.', extra])
    rows = []; fills = []
    for p in range(1, 51):
        d = data.get(p)
        if d:
            fn, ci, conf, obs = d
            io = 'GND' if conf == 'medido' and fn in ('GND', 'AGND') else ('E' if fn.startswith('Entrada') else ('S' if fn.startswith('Saida') else '-'))
            fills.append(BLUE if fn in ('GND', 'AGND') else (GREEN if conf == 'medido' else YEL))
            rows.append([p, fn, io, ci, obs, ''])
        else:
            fills.append(None); rows.append([p, '', '', '', '', ''])
    table(COLS, rows, H-84, rh=12.6, fs=6.6, fills=fills); footer(n)

conn_page('J1', J1, 1, 'Saidas dos latches $020018 (74LS273 push-pull; U45 = byte baixo? e U39 = byte alto? a confirmar) e entradas 74LS240 (invertem; pull-up 4,7k: pino aterrado = bit 1). Muitos pinos estao em VCC (nao identificados).')
c.showPage()
conn_page('J2', J2, 2, 'J2: pinos pares 2-22 = AGND (retorno de cada sinal analogico); 49 e 50 = GND. J2: saidas dos bits 8-15 de $020018 (74LS273 do byte alto) e as 8 entradas analogicas do multiplexador (pinos 1,3,5,7,9,13,15,21; caminho pelo RN6 medido) e as saidas dos 2 D/A (J2-21 = DAC B e J2-19 = DAC A). As entradas $020028 b8-15 sao a chave SW2.')
c.showPage()

# ---------- J7 ----------
head('J7 - conector de 50 pinos (IDC macho): conector de EXPANSAO DE BARRAMENTO', ['J7-1 a 16 = barramento local de dados de 16 bits (buffers 74LS645 U17/U18; compartilhado com AD7875 e, provavelmente, DAC8212). Alimentacoes, GND, linhas de endereco e selecoes de decodificador abaixo. Medido na bancada em 14/Nov/2026.'])
DB = {1:(16,17,2),2:(15,17,3),3:(14,17,4),4:(13,17,5),5:(11,17,6),6:(10,17,7),7:(9,17,8),8:(8,17,9),9:(7,18,9),10:(6,18,8),11:(5,18,7),12:(4,18,6)}
J7 = {}
for p, (ad, u, up) in DB.items():
    J7[p] = ('Barramento local bit %d (A/D DB%d)' % (p-1, p-1), 'AD7875 (U23) pino %d; U%d pino %d' % (ad, u, up), 'g', 'compartilhado com A/D (e DAC?)')
for p, up in {13: 5, 14: 4, 15: 3, 16: 2}.items():
    J7[p] = ('Barramento local bit %d (sem A/D)' % (p-1), 'U18 pino %d (74LS645)' % up, 'g', 'bits 12-15 (A/D tem so 12 bits)')
for p in (17, 18, 40, 41, 43): J7[p] = ('GND', 'GND', 'b', '')
for p in (19, 20): J7[p] = ('VCC (+5 V)', 'VCC', 'b', '')
for p in (38, 39): J7[p] = ('+5 V', 'VCC', 'b', '')
J7[42] = ('+12 V', '+12 V', 'b', ''); J7[45] = ('-12 V', '-12 V', 'b', '')
J7[21] = ('/RESET do sistema (ativo em BAIXO)', 'U11 DS1232 pino 6 (/RST); U12 pino 11 (2A1)', 'g', 'U12 p11>p9>p8>p12 -> /RESET do DUART (U27 p34)')
J7[22] = ('Saida do U28 (74LS00 4Y) = WE_H', 'U28 pino 11', 'g', 'escrita byte alto')
for p, up, nm in [(23, 14, '1Y3'), (24, 7, '2Y2'), (25, 16, '1Y2'), (26, 5, '2Y3'), (27, 18, '1Y1'), (28, 3, '2Y4')]:
    J7[p] = ('Saida bufferizada do U12 (74LS240 %s)' % nm, 'U12 pino %d' % up, 'g', 'INVERTE; entrada a rastrear (A1-A6?)')
J7[29] = ('Saida do U10 (inversor?)', 'U10 pino 12', 'g', 'a identificar')
J7[30] = ('Selecao Y6 do U4 (74LS138)', 'U4 pino 9', 'g', 'Y6_SEL')
J7[31] = ('Clock/fase do U1 (U1_9)', 'U1 pino 9', 'g', 'liga U4 /G2B')
J7[32] = ('R/W', 'U2 pino 10', 'g', '3B do U2')
J7[33] = ('Selecao Y0 do U6 (74LS138)', 'U6 pino 15', 'g', 'decodificador de E/S')
J7[44] = ('A8 (barramento de endereco)', 'A8', 'g', ''); J7[46] = ('A17 (barramento de endereco)', 'A17 (U4 pino 1)', 'g', '')
J7[47] = ('A18 (U4 pino 2, entrada B)', 'U4 pino 2', 'g', '')
J7[48] = ('Selecao C do U4 (U4_C_SEL)', 'U4 pino 3 / U19 pino 8', 'g', 'A19-A23 -> U4 entrada C')
J7[49] = ('4Q do U1 (U1_15)', 'U1 pino 15', 'g', 'G1 do U4 (pino 6)')
J7[50] = ('/G2A do U4 (U21_5)', 'U4 pino 4', 'g', '')
rows = []; fills = []
for p in range(1, 51):
    d = J7.get(p)
    if d:
        io = 'GND' if d[0] == 'GND' else ('VCC' if d[1] in ('VCC', '+12 V', '-12 V') else ('E/S' if p <= 16 else '?'))
        rows.append([p, d[0], io, d[1], d[3], '']); fills.append(BLUE if d[2] == 'b' else GREEN)
    else: rows.append([p, '', '', '', '', '']); fills.append(None)

table(COLS, rows, H-84, rh=12.6, fs=6.6, fills=fills); footer(3)
c.showPage()

# ---------- 68681 ----------
head('MC68681P DUART (U27, DIP-40) - pinos candidatos a entrada / saida', [
    'Pinagem do datasheet Philips SCN68681 (DIP-40). Conferir com a marcacao do chip. O DUART esta em $FA0000 (bytes em enderecos impares).',
    'Entradas IP: ler em $FA001B (IP4 = bit 4). Saidas OP: SOPR $FA001C poe o pino em nivel BAIXO, ROPR $FA001E poe em nivel ALTO (OPCR $FA001A = 0 -> todos OP comuns).'])
DU = [(1, 'A1', 'barramento', 'A1', ''), (2, 'IP3', 'ENT', 'ligado a ? (IP3? no netlist)', 'nao usado pelo firmware conhecido'), (3, 'A2', 'barramento', '', ''),
      (4, 'IP1 (CTSB)', 'ENT', 'U36 pino 8 (Y3) - RS-232 B', 'CTSB'), (5, 'A3', 'barramento', '', ''), (6, 'A4', 'barramento', '', ''),
      (7, 'IP0 (CTSA)', 'ENT', 'U36 pino 6 (Y2) - RS-232 A', 'CTSA'), (8, 'R/W', 'barramento', 'R/W', ''), (9, '/DTACK', 'saida', 'gerador DTACK', ''),
      (10, 'RxDB', 'ENT', 'U36 pino 11 (Y4)', 'canal B 9600 bps'), (11, 'TxDB', 'SAI', 'U43 pinos 4/5', 'canal B'), (12, 'OP1 (RTSB)', 'SAI', 'U43 pino 2', 'RTSB'),
      (13, 'OP3', 'SAI', 'AD7875 U23 pino 23 (CONVST)', 'confirmado; pulso inicia a conversao'), (14, 'OP5', 'SAI', '?', 'usado pelo firmware original (funcao desconhecida)'),
      (15, 'OP7', 'SAI', '?', 'usado pelo firmware original (funcao desconhecida)'), (16, 'D1', 'barramento', 'D1', ''), (17, 'D3', 'barramento', 'D3', ''),
      (18, 'D5', 'barramento', 'D5', ''), (19, 'D7', 'barramento', 'D7', ''), (20, 'GND', 'GND', 'GND', ''),
      (21, '/INTRN', 'saida', '/IRQ68681 -> CPU', ''), (22, 'D6', 'barramento', 'D6', ''), (23, 'D4', 'barramento', 'D4', ''), (24, 'D2', 'barramento', 'D2', ''),
      (25, 'D0', 'barramento', 'D0', ''), (26, 'OP6', 'SAI', '?', 'usado pelo firmware original (funcao desconhecida)'), (27, 'OP4', 'SAI', '?', 'nao usado pelo firmware conhecido'),
      (28, 'OP2', 'SAI', 'U11 pino 7 (/ST do watchdog)', 'STROBE do watchdog (monitor mexe so aqui e em OP3)'),
      (29, 'OP0 (RTSA)', 'SAI', 'U43 pino 10 (A3)', 'RTSA'), (30, 'TxDA', 'SAI', 'U43 pinos 12/13', 'console 57600 bps'), (31, 'RxDA', 'ENT', 'U36 pino 3 (Y1)', 'console'),
      (32, 'X1/CLK', 'cristal', 'XO1/cristal 3,6864 MHz', ''), (33, 'X2', 'cristal', '', ''), (34, '/RESET', 'ENT', 'U12 pino 12 (<- J7-21 = /RST do DS1232 U11 p6)', 'medido; ativo em baixo (2 inversores)'), (35, '/CS', 'ENT', 'DUART_CS (decodificador)', ''),
      (36, 'IP2', 'ENT', '?', 'livre?'), (37, '/IACK', 'ENT', '?', 'normalmente a VCC'), (38, 'IP5', 'ENT', '?', 'livre?'),
      (39, 'IP4', 'ENT', 'AD7875 U23 pino 2 (BUSY)', 'confirmado; 1 = A/D pronto'), (40, 'VCC', 'VCC', '+5 V', '')]
cols = [('Pino', 26), ('Sinal', 70), ('E/S', 45), ('Ligado a', 140), ('Observacao', 170), ('ANOTAR', 84)]
rows = []; fills = []
for p, s, io, lig, ob in DU:
    rows.append([p, s, io, lig, ob, '']); 
    fills.append(BLUE if io in ('GND', 'VCC') else (GREY if io == 'barramento' else (GREEN if ('confirmado' in ob or 'medido' in ob) else YEL)))
y = table(cols, rows, H-84, rh=12.3, fs=6.6, fills=fills)
c.setFont('Helvetica', 7); c.setFillColor(colors.black)
c.drawString(30, y-8, 'Candidatos a E/S livres para teste: OP3, OP4, OP5, OP6, OP7 (saidas) e IP2, IP3, IP4, IP5 (entradas). Neste teste de bancada nao ha laser conectado.')
footer(4); c.showPage()

# ---------- AD7875 e multiplexador ----------
head('A/D AD7875 (24 pinos DIP) e multiplexador analogico (U38)', [
    'AD7875 = U23. 12 bits, 0 a +5 V, 1 LSB = 1,22 mV, 100 kHz. Pinagem do datasheet Analog Devices (DIP-24), conferida na placa (pino 18 AGND etc.). Resultado lido em $020000 (palavra, 12 bits baixos).',
    'Confirmado na bancada: disparo = pulso em OP3 (CONVST); pronto = IP4 (BUSY); canal = $020020 bits 14-12; bit 15 = habilita o mux.'])
AD = [(1, '/RD', 'ENT', 'U2 pino 8 (ROM_OE: strobe de leitura comum)', 'medido'), (2, '/BUSY-INT', 'SAI', 'DUART IP4 (pino 39)', 'medido'),
      (3, 'CLK', 'ENT', 'pino 21 (VSS) = clock interno', 'medido'),
      (4, 'DB11/HBEN', 'SAI', 'U18 p6 | J7-12', 'medido'), (5, 'DB10/SSTRB', 'SAI', 'U18 p7 | J7-11', 'medido'), (6, 'DB9/SCLK', 'SAI', 'U18 p8 | J7-10', 'medido'),
      (7, 'DB8/SDATA', 'SAI', 'U18 p9 | J7-9', 'medido'), (8, 'DB7/LOW', 'SAI', 'U17 p9 | J7-8', 'medido'), (9, 'DB6/LOW', 'SAI', 'U17 p8 | J7-7', 'medido'),
      (10, 'DB5/LOW', 'SAI', 'U17 p7 | J7-6', 'medido'), (11, 'DB4/LOW', 'SAI', 'U17 p6 | J7-5', 'medido'), (12, 'DGND', 'GND', 'GND', 'medido'),
      (13, 'DB3/DB11', 'SAI', 'U17 p5 | J7-4', 'medido'), (14, 'DB2/DB10', 'SAI', 'U17 p4 | J7-3', 'medido'), (15, 'DB1/DB9', 'SAI', 'U17 p3 | J7-2', 'medido'),
      (16, 'DB0/DB8', 'SAI', 'U17 p2 | J7-1', 'medido'),
      (17, 'VDD', 'VCC', '+5 V', 'medido'), (18, 'AGND', 'GND', 'U38 pino 2; separado do GND (jumper aberto)', '680R ate GND por via a achar'),
      (19, 'REF OUT', 'SAI', 'a medir com a placa ligada', 'esperado ~3 V, ate 500 uA'),
      (20, 'VIN', 'ENT', 'U29 pino 6 (saida do OP07CP)', 'medido'),
      (21, 'VSS', 'VCC', 'pino 3 (CLK); NAO vai ao U30 pino 4; origem ?', 'a medir: 675R AGND, 685R GND, 575R +5V'),
      (22, '12/8/CLK', 'ENT', '+5 V (saida paralela de 12 bits)', 'medido'),
      (23, 'CONVST', 'ENT', 'DUART OP3 (pino 13)', 'medido'), (24, '/CS', 'ENT', 'U6 pino 7 (Y7 do 74LS138)', 'medido')]
cols2 = [('Pino', 26), ('Mnemonico', 78), ('E/S', 32), ('Ligado a (hipotese)', 150), ('Observacao', 150), ('ANOTAR', 109)]
rows = []; fills = []
for p, s, io, lig, ob in AD:
    rows.append([p, s, io, lig, ob, '']); fills.append(BLUE if io in ('GND', 'VCC') else (YEL if ('medir' in lig or 'confirmar' in lig) else GREEN))
y = table(cols2, rows, H-84, rh=12.3, fs=6.6, fills=fills)
y -= 10
c.setFont('Helvetica-Bold', 8); c.drawString(30, y, 'Multiplexador analogico U38 (16 pinos, 8 canais; tipo ainda nao identificado) - anotado na bancada em 14/Nov'); y -= 4
cols3 = [('Pino U38', 44), ('Sinal', 50), ('Ligado a', 215), ('Caminho ate o J2 (1 kohm no RN6)', 160), ('ANOTAR', 55)]
rows = [[1, 'endereco A1', '$020020 bit 13 (U40 Q5, pino 15)', '', ''], [2, 'AGND', 'U23 pino 18 (AGND do A/D, se U23 = AD7875)', '', ''],
        [3, 'EN', 'U40 pino 19 = $020020 bit 15', '', ''], [4, 'endereco A2', '$020020 bit 14 (U40 Q6, pino 16)', '', ''],
        [5, 'S8', 'RN6 pino 16 -> 1k -> RN6 pino 1', 'J2-15', ''], [6, 'S7', 'RN6 pino 15 -> 1k -> RN6 pino 2', 'J2-13', ''],
        [7, 'S6', 'RN6 pino 14 -> 1k -> RN6 pino 3', 'J2-21', ''], [8, 'S5', 'RN6 pino 13 -> 1k -> RN6 pino 4', 'J2-9', ''],
        [9, 'S4', 'RN6 pino 12 -> 1k -> RN6 pino 5', 'J2-7', ''], [10, 'S3', 'RN6 pino 11 -> 1k -> RN6 pino 6', 'J2-5', ''],
        [11, 'S2', 'RN6 pino 10 -> 1k -> RN6 pino 7', 'J2-3', ''], [12, 'OUT', 'U29 pino 3 (OP07CP, entrada nao inversora)', '', ''],
        [13, 'S1', 'RN6 pino 9 -> 1k -> RN6 pino 8', 'J2-1', ''], [14, 'VDD', '+12 V', '', ''], [15, 'VSS', '-12 V', '', ''],
        [16, 'endereco A0', '$020020 bit 12 (U40 Q4, pino 12)', '', '']]
fl = []
for r in rows:
    fl.append(BLUE if r[1] in ('VDD', 'VSS', 'AGND') else (YEL if r[1] in ('?',  'endereco A0', 'endereco A1', 'endereco A2') else GREEN))
y = table(cols3, rows, y, rh=12.0, fs=6.6, fills=fl)
c.setFont('Helvetica', 6.6)
TX = ['OK: caminhos S1-S8 ate o J2, VIN no U29 pino 6, CLK no VSS (pino 21 e 3) medidos. Rotulos A0/A1/A2 e ordem dos bits do canal do mux ainda sao hipotese. U29 (OP07CP): pino 3 = saida do mux (OUT, U38 p12), pino 6 -> VIN do A/D, pino 7 = +12 V e pino 4 = -12 V (comuns com U31 e U32).', 'Pendente (placa ligada): tensao no pino 21 e no pino 19 (REF OUT, ~3 V) do AD7875; tensao DC entre AGND e GND (jumper A/D ground aberto, 680 ohm entre eles por via a achar). A rede do pino 21 mede 675R ao AGND, 685R ao GND e 575R ao +5 V; sem continuidade com U30 pino 4.', 'Chips: U23 = AD7875; U17/U18 = 74LS645 (transceptores bidirecionais, lado A = barramento local do A/D/J7); U6 = 74LS138 (Y7 = /CS do A/D); U2 pino 8 = ROM_OE (/RD).']
k = 0
for t in TX:
    for ln in simpleSplit(t, 'Helvetica', 6.6, W-60):
        c.drawString(30, y-8-k*8.5, ln); k += 1
footer(5); c.showPage()

# ---------- D/A ----------
head('D/A: DAC8212 (U24), referencia AD584 (U30) e amplificadores U31/U32', [
    'U24 = PMI DAC8212GP: DAC DUPLO de 12 bits, BUFFERED, MULTIPLICADOR CMOS, SAIDA EM CORRENTE (IOUT + RFB). Pinagem do datasheet (DIP-24). Firmware: DAC A = $02000A, DAC C = $02000C (provavelmente DAC A e DAC B do chip, escolhidos pelo pino 18).',
    'Saidas em corrente: U32 (IOUT A) e U31 (IOUT B), OP07CP, sao conversores corrente-tensao (medido: IOUT no pino 2). Em verde = medido; em amarelo = hipotese a medir (RFB e dados/controle).'])
DA = [(1, 'AGND', 'GND', 'AGND', ''), (2, 'IOUT A', 'SAI', 'U32 pino 2', 'medido; -> U32 pino 6 -> J2-19'), (3, 'RFB A', 'ENT', 'U32 pino 6 ?', 'a medir (realimentacao interna)'),
      (4, 'VREF A', 'ENT', 'U30 pino 4 (AD584 Common, referencia negativa)', 'medido'), (5, 'DGND', 'GND', 'GND', ''),
      (6, 'DB11', 'ENT', 'J7-12 (rede U17/U18) ?', ''), (7, 'DB10', 'ENT', 'J7-11 ?', ''), (8, 'DB9', 'ENT', 'J7-10 ?', ''), (9, 'DB8', 'ENT', 'J7-9 ?', ''),
      (10, 'DB7', 'ENT', 'J7-8 ?', ''), (11, 'DB6', 'ENT', 'J7-7 ?', ''), (12, 'DB5', 'ENT', 'J7-6 ?', ''),
      (13, 'DB4', 'ENT', 'J7-5 ?', ''), (14, 'DB3', 'ENT', 'J7-4 ?', ''), (15, 'DB2', 'ENT', 'J7-3 ?', ''), (16, 'DB1', 'ENT', 'J7-2 ?', ''), (17, 'DB0', 'ENT', 'J7-1 ?', ''),
      (18, '/DAC A / DAC B', 'ENT', 'bit de endereco? (A=1, B=0 ou inverso)', 'escolhe qual DAC recebe o dado'),
      (19, '/CS', 'ENT', 'decodificador U6 ?', 'ativo em 0'), (20, '/WR', 'ENT', 'strobe de escrita ?', 'ativo em 0; dados transparentes com /CS e /WR em 0'),
      (21, 'VDD', 'VCC', '+5 V a +15 V ?', ''), (22, 'VREF B', 'ENT', 'U30 pino 4 (AD584 Common, referencia negativa)', 'medido'), (23, 'RFB B', 'ENT', 'U31 pino 6 ?', 'a medir'), (24, 'IOUT B', 'SAI', 'U31 pino 2', 'medido; -> U31 pino 6 -> J2-21 e S6')]
cols4 = [('Pino U24', 40), ('Sinal', 80), ('E/S', 28), ('Ligado a (hipotese)', 190), ('Observacao', 140), ('ANOTAR', 55)]
rows = [[p, sg, io, lg, ob, ''] for p, sg, io, lg, ob in DA]
fl = [BLUE if io in ('GND', 'VCC') else (GREEN if p in (2, 4, 22, 24) else YEL) for p, sg, io, lg, ob in DA]
y = table(cols4, rows, H-98, rh=11.6, fs=6.4, fills=fl)
y -= 10
c.setFont('Helvetica-Bold', 8); c.drawString(30, y, 'U30 (AD584, referencia) e U31/U32 (OP07CP, DIP-8) - medido na bancada'); y -= 4
cols6 = [('CI / pino', 78), ('Funcao (datasheet)', 140), ('Ligado a (medido na bancada)', 215), ('ANOTAR', 74)]
r6 = [['U30 pino 1', 'AD584: saida 10 V', 'AGND (so este pino do U30 vai ao AGND)', ''],
      ['U30 pino 2 / 3 / 8', 'AD584: 5 V / 2,5 V / +VIN', 'NAO vao ao AGND', ''],
      ['U30 pino 4', 'AD584: Common (no modo de ref. negativa = saida)', '-12 V por resistor ~1k; VREF A e B do U24 (pinos 4 e 22)', ''],
      ['U30 pinos 5 / 6 / 7', 'Strobe / VBG / CAP', 'a anotar', ''],
      ['U31 e U32 pino 3', 'OP07CP entrada nao inversora', 'AGND por resistor ~1k (1,00k 1%) em cada', ''],
      ['U31 pino 2', 'entrada inversora (IOUT B)', 'U24 pino 24 (IOUT B)', ''], ['U32 pino 2', 'entrada inversora (IOUT A)', 'U24 pino 2 (IOUT A)', ''],
      ['U31 pino 6', 'saida (DAC B)', 'RN6 pino 3 (-> 1k -> mux S6) e J2-21', ''], ['U32 pino 6', 'saida (DAC A)', 'J2-19', ''],
      ['U29/U31/U32 pino 7', 'V+ (+12 V)', 'ligados entre si (U29 = buffer do mux)', ''], ['U29/U31/U32 pino 4', 'V- (-12 V)', '-12 V nos tres (medido)', '']]
y = table(cols6, r6, y, rh=11.6, fs=6.4, fills=[GREEN]*11)
c.setFont('Helvetica', 6.5)
for k, t in enumerate(simpleSplit('Resistores marrons de precisao (RN55D, 1001F = 1,00 kohm 1%) perto do U24/U30. Referencia NEGATIVA (AD584 no pino 4): com o conversor inversor a saida fica positiva. Hipotese: so o pino 1 (10 V) no AGND => VREF = -10 V (medir o pino 4 ligado). Cuidado: a saida do DAC B vai tambem ao A/D (0-5 V) pelo S6; comecar com valores pequenos. Firmware: DAC A = $02000A (0-5000), DAC C = $02000C (0-125000); provavel DAC C = DAC B do chip (U31, J2-21, com leitura de volta) - testar com ADC.', 'Helvetica', 6.5, W-60)):
    c.drawString(30, y-9-k*8.5, t)
footer(6); c.showPage()
head('Saidas de $020020 e timers 8254', ['Latches $020020: 74LS273 U46 (byte baixo) e U40 (byte alto). Os bits 12-15 vao ao mux U38 (ver folha 5).'])
y = H-70
c.setFont('Helvetica-Bold', 8); c.drawString(30, y, 'Saidas de $020020 (74LS273 U46 byte baixo, U40 byte alto)'); y -= 4
cols5 = [('Bit', 28), ('Saida do 273', 78), ('Inversor', 120), ('Destino conhecido', 175), ('ANOTAR', 132)]
S = [[0, 'U46 Q0 pino 2', 'U41 (7406) 1Y pino 2', 'pino de conector a descobrir', ''], [1, 'U46 Q1 pino 5', 'U41 6Y pino 12', 'a descobrir', ''],
     [2, 'U46 Q2 pino 6', 'U47 (7406) 1Y pino 2', 'a descobrir', ''], [3, 'U46 Q3 pino 9', 'U47 6Y pino 12', 'a descobrir', ''],
     [4, 'U46 Q4 pino 12', 'U47 2Y pino 4', 'a descobrir', ''], [5, 'U46 Q5 pino 15', 'U47 5Y pino 10', 'a descobrir', ''],
     [6, 'U46 Q6 pino 16', 'U47 3Y pino 6', 'a descobrir', ''], [7, 'U46 Q7 pino 19', 'U47 4Y pino 8', 'J1-48 (coletor aberto)', ''],
     [8, 'U40 Q0 pino 2', 'U39? D3 pino 8 (?)', 'a descobrir', ''], [9, 'U40 Q1 pino 5', 'U41 5Y pino 10', 'a descobrir', ''],
     [10, 'U40 Q2 pino 6', 'U41 3Y pino 6', 'a descobrir', ''], [11, 'U40 Q3 pino 9', 'U41 4Y pino 8', 'a descobrir', ''],
     [12, 'U40 Q4 pino 12', 'direto', 'U38 pino 16 (mux)', ''], [13, 'U40 Q5 pino 15', 'direto', 'U38 pino 1 (mux)', ''],
     [14, 'U40 Q6 pino 16', 'direto', 'U38 pino 4 (mux)', ''], [15, 'U40 Q7 pino 19', 'direto', 'U38 pino 3 (mux)', '']]
fl = [YEL if r[3] == 'a descobrir' else GREEN for r in S]
y = table(cols5, S, y, rh=11.2, fs=6.4, fills=fl)
c.setFont('Helvetica', 6.6); c.drawString(30, y-8, 'Timers 8254 (firmware em $020010-$020016): ainda sem CI identificado; escritas de controle em dois enderecos sugerem 2 chips. Ver Firmware_original_AD_DA_v1.txt.')
footer(7); c.showPage()

# ---------- mapa das entradas ----------
head('Mapa das entradas digitais de J1/J2 (medido em 15/Nov/2026)', ['Aterrando o pino por 330 ohm com o comando J do monitor v3.1t4. Porta A = $020030, porta B = $020028 (74LS240 inversor, pull-up 4,7k: pino aterrado = bit 1).'])
PA = {0:'J2-39',1:'J2-42',2:'J2-41',3:'J1-4',4:'J2-43',5:'J2-45',6:'J2-46',7:'J2-48',8:'J2-29',9:'J2-32',10:'J2-31',11:'J2-34',12:'J2-33',13:'J2-36',14:'J2-35',15:'J2-38'}
PB = {0:'J1-7',1:'J1-35',2:'J1-33',3:'J1-31',4:'J1-27',5:'J1-25',6:'J1-23',7:'J1-34'}
rows = [['A', b, '$%04X' % (1 << b), PA[b]] for b in range(16)] + [['B', b, '$%04X' % (1 << b), PB[b]] for b in range(8)]
colsm = [('Porta', 40), ('Bit', 40), ('Valor lido', 70), ('Pino', 70)]
y = table(colsm, rows, H-70, rh=13, fs=8, fills=[GREEN]*24)
c.setFont('Helvetica', 7.5); c.setFillColor(colors.black)
for i, t in enumerate(['Sem resposta como entrada: J2-25, J2-26, J2-44 e J1-29.',
  'J1 nao conectado (testado pino a pino): 3, 5, 6, 8, 16, 19, 21, 22, 36, 37, 39, 41-47 e 49 (J1-13 e J1-17: so ruido).',
  'Entradas do DUART (IP2, IP3, IP5) nao sao lidas pelo comando J: ficam para a ROM v3.1t5.']):
    c.drawString(30, y-14-i*11, t)
footer(8); c.showPage()
c.save()
print('ok')
