# gera Paragon50_Pinos_J1_J2_J7_CIs_v1.pdf (folhas de mapeamento com multimetro)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
W, H = A4
OUT = 'Paragon50_Pinos_J1_J2_J7_CIs_v5.pdf'
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
    c.drawString(30, 12, 'Tabajara Labs - PARAGON 50 - 14/Nov/2026 - v5. Colunas em branco = para anotar com o multimetro (placa DESLIGADA, teste de continuidade).')
    c.drawRightString(W-30, 12, 'pag. %d' % n)

# ---------- dados J1 / J2 ----------
Q273 = {0: 2, 1: 5, 2: 6, 3: 9, 4: 12, 5: 15, 6: 16, 7: 19}
def lat(b): return 'Saida $020018 b%d' % b, '74LS273 %s pino %d (Q%d)' % ('baixo' if b < 8 else 'alto', Q273[b % 8], b % 8)
J1 = {1: ('GND', '', 'medido', ''), 2: ('GND', '', 'medido', ''), 9: ('GND', '', 'medido', ''), 50: ('GND', '', 'medido', ''),
      4: ('Entrada porta A b3 ($020030)', '74LS240 U44/U37 (pino ?)', 'medido', ''),
      7: ('Entrada porta B b0 ($020028)', '74LS240 U42/U48 (pino ?)', 'medido', 'MISO do SD'),
      10: (*lat(7), 'medido', 'LCD D6'), 14: (*lat(6), 'medido', 'LCD D5'), 15: (*lat(5), 'medido', 'LCD D4'),
      18: (*lat(4), 'medido', 'LCD RS'), 20: (*lat(3), 'medido', 'LCD E'), 24: (*lat(2), 'medido', 'CS do SD (nivel: bit=1 -> CS alto)'),
      26: (*lat(1), 'medido', 'MOSI (SD / I-O do DS1302)'), 28: (*lat(0), 'medido', 'SCK (SD / SCLK do DS1302)'),
      23: ('Entrada porta B b6', '74LS240 U42/U48 (pino ?)', 'medido', ''), 25: ('Entrada porta B b5', '74LS240 U42/U48 (pino ?)', 'medido', ''),
      27: ('Entrada porta B b4', '74LS240 U42/U48 (pino ?)', 'medido', 'SD_DET'), 31: ('Entrada porta B b3', '74LS240 U42/U48 (pino ?)', 'medido', 'botao do encoder'),
      33: ('Entrada porta B b2', '74LS240 U42/U48 (pino ?)', 'medido', 'botao EN1'), 35: ('Entrada porta B b1', '74LS240 U42/U48 (pino ?)', 'medido', 'botao EN2'),
      36: ('Entrada porta B b7 (?)', '74LS240 U42/U48 (pino ?)', 'inferido', 'numero ilegivel na folha: confirmar'),
      48: ('Saida $020020 b7 (coletor aberto, INVERTIDA)', '74LS06 U47 pino 8 (4Y)', 'medido', 'precisa de pull-up'),
      13: ('so ruido (nao conectado)', '', 'medido', ''), 17: ('so ruido (nao conectado)', '', 'medido', ''), 29: ('sem resposta como entrada', '', 'medido', 'riscado na folha')}
J2 = {1: ('Entrada analogica S1 (mux U38)', 'RN6 p8-1k-p9; U38 p13', 'medido', '1 kohm em serie'),
      3: ('Entrada analogica S2 (mux U38)', 'RN6 p7-1k-p10; U38 p11', 'medido', '1 kohm em serie'),
      5: ('Entrada analogica S3 (mux U38)', 'RN6 p6-1k-p11; U38 p10', 'medido', '1 kohm em serie'),
      7: ('Entrada analogica S4 (mux U38)', 'RN6 p5-1k-p12; U38 p9', 'medido', '1 kohm em serie'),
      9: ('Entrada analogica S5 (mux U38)', 'RN6 p4-1k-p13; U38 p8', 'medido', '1 kohm em serie'),
      13: ('Entrada analogica S7 (mux U38)', 'RN6 p2-1k-p15; U38 p6', 'medido', '1 kohm em serie'),
      15: ('Entrada analogica S8 (mux U38)', 'RN6 p1-1k-p16; U38 p5', 'medido', '1 kohm em serie'),
      21: ('Entrada analogica S6 (mux U38)', 'RN6 p3-1k-p14; U38 p7', 'medido', '1 kohm em serie'),
      23: (*lat(15), 'medido', ''), 24: (*lat(14), 'medido', ''), 27: (*lat(13), 'medido', ''), 28: (*lat(12), 'medido', ''),
      30: (*lat(11), 'medido', ''), 37: (*lat(10), 'medido', 'CE do DS1302 (provisorio)'), 40: (*lat(9), 'medido', 'buzzer'),
      47: (*lat(8), 'medido', 'LCD D7')}
COLS = [('Pino', 26), ('Funcao / sinal', 150), ('E/S', 28), ('Pino do integrado', 120), ('Obs.', 112), ('ANOTAR: CI + pino', 99)]
def conn_page(name, data, n, extra):
    head('%s - conector de 50 pinos (IDC macho)' % name, [
        'Pinos IMPARES na coluna esquerda, PARES na direita (1-2 na mesma linha). Mapa por pino abaixo em ordem numerica.', extra])
    rows = []; fills = []
    for p in range(1, 51):
        d = data.get(p)
        if d:
            fn, ci, conf, obs = d
            io = 'GND' if conf == 'medido' and fn == 'GND' else ('E' if fn.startswith('Entrada') else ('S' if fn.startswith('Saida') else '-'))
            fills.append(BLUE if fn == 'GND' else (GREEN if conf == 'medido' else YEL))
            rows.append([p, fn, io, ci, obs, ''])
        else:
            fills.append(None); rows.append([p, '', '', '', '', ''])
    table(COLS, rows, H-84, rh=12.6, fs=6.6, fills=fills); footer(n)

conn_page('J1', J1, 1, 'Saidas dos latches $020018 (74LS273 push-pull, 0-4,3 V) e entradas 74LS240 (invertem; pull-up 4,7k: pino aterrado = bit 1). Muitos pinos estao em VCC (nao identificados).')
c.showPage()
conn_page('J2', J2, 2, 'J2: saidas dos bits 8-15 de $020018 (74LS273 do byte alto) e as 8 entradas analogicas do multiplexador (pinos 1,3,5,7,9,13,15,21; o lado RN6 pinos 1-8 e deduzido). As entradas $020028 b8-15 sao a chave SW2.')
c.showPage()

# ---------- J7 ----------
head('J7 - conector de 50 pinos (IDC macho)', ['Pinos 1-12: os 12 bits de dados do A/D (mesma rede que os buffers U17/U18 de $020000). Pino 48: U4_C_SEL. O resto ainda por mapear.', 'Os pinos 13-47 e 49-50 ainda nao foram mapeados.'])
J7 = {1: ('A/D DB0 / $020000 bit 0', 'AD7875 (U23) pino 16; U17 pino 2', 'medido', 'compartilhado com o A/D'), 2: ('A/D DB1 / $020000 bit 1', 'AD7875 (U23) pino 15; U17 pino 3', 'medido', 'compartilhado com o A/D'), 3: ('A/D DB2 / $020000 bit 2', 'AD7875 (U23) pino 14; U17 pino 4', 'medido', 'compartilhado com o A/D'), 4: ('A/D DB3 / $020000 bit 3', 'AD7875 (U23) pino 13; U17 pino 5', 'medido', 'compartilhado com o A/D'), 5: ('A/D DB4 / $020000 bit 4', 'AD7875 (U23) pino 11; U17 pino 6', 'medido', 'compartilhado com o A/D'), 6: ('A/D DB5 / $020000 bit 5', 'AD7875 (U23) pino 10; U17 pino 7', 'medido', 'compartilhado com o A/D'), 7: ('A/D DB6 / $020000 bit 6', 'AD7875 (U23) pino 9; U17 pino 8', 'medido', 'compartilhado com o A/D'), 8: ('A/D DB7 / $020000 bit 7', 'AD7875 (U23) pino 8; U17 pino 9', 'medido', 'compartilhado com o A/D'), 9: ('A/D DB8 / $020000 bit 8', 'AD7875 (U23) pino 7; U18 pino 9', 'medido', 'compartilhado com o A/D'), 10: ('A/D DB9 / $020000 bit 9', 'AD7875 (U23) pino 6; U18 pino 8', 'medido', 'compartilhado com o A/D'), 11: ('A/D DB10 / $020000 bit 10', 'AD7875 (U23) pino 5; U18 pino 7', 'medido', 'compartilhado com o A/D'), 12: ('A/D DB11 / $020000 bit 11', 'AD7875 (U23) pino 4; U18 pino 6', 'medido', 'compartilhado com o A/D'), 48: ('Selecao C do decodificador U4 (U4_C_SEL)', 'U4 (74LS138) pino 3 / U19 pino 8', 'medido', 'liga A19-A23 -> U4 entrada C')}
rows = []; fills = []
for p in range(1, 51):
    d = J7.get(p)
    if d: rows.append([p, d[0], 'E' if p <= 12 else '?', d[1], d[3], '']); fills.append(GREEN)
    else: rows.append([p, '', '', '', '', '']); fills.append(None)
table(COLS, rows, H-84, rh=12.6, fs=6.6, fills=fills); footer(3)
c.showPage()

# ---------- 68681 ----------
head('MC68681 DUART (U? , DIP-40) - pinos candidatos a entrada / saida', [
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
      (32, 'X1/CLK', 'cristal', 'XO1/cristal 3,6864 MHz', ''), (33, 'X2', 'cristal', '', ''), (34, '/RESET', 'ENT', '/RESET', ''), (35, '/CS', 'ENT', 'DUART_CS (decodificador)', ''),
      (36, 'IP2', 'ENT', '?', 'livre?'), (37, '/IACK', 'ENT', '?', 'normalmente a VCC'), (38, 'IP5', 'ENT', '?', 'livre?'),
      (39, 'IP4', 'ENT', 'AD7875 U23 pino 2 (BUSY)', 'confirmado; 1 = A/D pronto'), (40, 'VCC', 'VCC', '+5 V', '')]
cols = [('Pino', 26), ('Sinal', 70), ('E/S', 45), ('Ligado a', 140), ('Observacao', 170), ('ANOTAR', 84)]
rows = []; fills = []
for p, s, io, lig, ob in DU:
    rows.append([p, s, io, lig, ob, '']); 
    fills.append(BLUE if io in ('GND', 'VCC') else (GREY if io == 'barramento' else (GREEN if 'confirmado' in ob else YEL)))
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
      (20, 'VIN', 'ENT', 'U29 pino 6 (saida do OP07CP) - confirmar', 'anotado como "pino 21"; assumido 20'),
      (21, 'VSS', 'VCC', 'pino 3 (CLK); tensao a medir', 'GND ou -5 V? so ha +-12 V'),
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
TX = ['(*) OK: caminhos S1-S8 ate o J2 confirmados na bancada (14/Nov). Rotulos A0/A1/A2 e ordem dos bits do canal ainda sao hipotese.', 'Pendente: VIN (pino 20) ao U29 pino 6 (confirmar que e 20, nao 21); tensao do VSS (pino 21, ligado ao CLK); REF OUT (esperado ~3 V); tensao DC entre AGND e GND; onde esta o resistor de 680 ohm entre AGND e GND (jumper A/D ground aberto).', 'Chips: U23 = AD7875; U17/U18 = buffers de $020000 (74LS245?, a confirmar); U6 = 74LS138 (Y7 = /CS do A/D); U2 pino 8 = ROM_OE.']
k = 0
for t in TX:
    for ln in simpleSplit(t, 'Helvetica', 6.6, W-60):
        c.drawString(30, y-8-k*8.5, ln); k += 1
footer(5); c.showPage()

# ---------- D/A ----------
head('D/A: DAC8212 (U24), referencia AD584 (U30) e amplificadores U31/U32', [
    'U24 = PMI DAC8212GP: DAC DUPLO de 12 bits, BUFFERED, MULTIPLICADOR CMOS, SAIDA EM CORRENTE (IOUT + RFB). Pinagem do datasheet (DIP-24). Firmware: DAC A = $02000A, DAC C = $02000C (provavelmente DAC A e DAC B do chip, escolhidos pelo pino 18).',
    'Como as saidas sao em corrente, U31 e U32 (OP07CP) sao conversores corrente-tensao: IOUT -> pino 2, RFB do chip <- pino 6 (saida). Tudo abaixo em amarelo e hipotese a medir, exceto o que esta em verde.'])
DA = [(1, 'AGND', 'GND', 'AGND', ''), (2, 'IOUT A', 'SAI', 'U31 pino 2 ?', 'corrente de saida do DAC A'), (3, 'RFB A', 'ENT', 'U31 pino 6 ?', 'resistor de realimentacao interno'),
      (4, 'VREF A', 'ENT', 'U30 (AD584) saida ?', 'referencia'), (5, 'DGND', 'GND', 'GND', ''),
      (6, 'DB11', 'ENT', 'J7-12 (rede U17/U18) ?', ''), (7, 'DB10', 'ENT', 'J7-11 ?', ''), (8, 'DB9', 'ENT', 'J7-10 ?', ''), (9, 'DB8', 'ENT', 'J7-9 ?', ''),
      (10, 'DB7', 'ENT', 'J7-8 ?', ''), (11, 'DB6', 'ENT', 'J7-7 ?', ''), (12, 'DB5', 'ENT', 'J7-6 ?', ''),
      (13, 'DB4', 'ENT', 'J7-5 ?', ''), (14, 'DB3', 'ENT', 'J7-4 ?', ''), (15, 'DB2', 'ENT', 'J7-3 ?', ''), (16, 'DB1', 'ENT', 'J7-2 ?', ''), (17, 'DB0', 'ENT', 'J7-1 ?', ''),
      (18, '/DAC A / DAC B', 'ENT', 'bit de endereco? (A=1, B=0 ou inverso)', 'escolhe qual DAC recebe o dado'),
      (19, '/CS', 'ENT', 'decodificador U6 ?', 'ativo em 0'), (20, '/WR', 'ENT', 'strobe de escrita ?', 'ativo em 0; dados transparentes com /CS e /WR em 0'),
      (21, 'VDD', 'VCC', '+5 V a +15 V ?', ''), (22, 'VREF B', 'ENT', 'U30 (AD584) saida ?', ''), (23, 'RFB B', 'ENT', 'U32 pino 6 ?', ''), (24, 'IOUT B', 'SAI', 'U32 pino 2 ?', 'corrente de saida do DAC B')]
cols4 = [('Pino U24', 40), ('Sinal', 80), ('E/S', 28), ('Ligado a (hipotese)', 190), ('Observacao', 140), ('ANOTAR', 55)]
rows = [[p, sg, io, lg, ob, ''] for p, sg, io, lg, ob in DA]
fl = [BLUE if io in ('GND', 'VCC') else YEL for p, sg, io, lg, ob in DA]
y = table(cols4, rows, H-98, rh=11.6, fs=6.4, fills=fl)
y -= 10
c.setFont('Helvetica-Bold', 8); c.drawString(30, y, 'U30 (AD584, referencia) e U31/U32 (OP07CP, DIP-8) - medido na bancada'); y -= 4
cols6 = [('CI / pino', 70), ('Funcao (datasheet / hipotese)', 150), ('Ligado a', 210), ('ANOTAR', 77)]
r6 = [['U30 pino 4', 'AD584 (a conferir no datasheet)', '-12 V atraves de resistor ~1k (1,00k 1%?)', ''],
      ['U31 pino 3', 'OP07CP entrada nao inversora', 'AGND por resistor ~1k (1,00k 1%)', ''], ['U32 pino 3', 'OP07CP entrada nao inversora', 'AGND por resistor ~1k (1,00k 1%)', ''],
      ['U31 pino 2 / 6', 'entrada inversora / saida', 'IOUT A / RFB A do U24 ? (a medir)', ''], ['U32 pino 2 / 6', 'entrada inversora / saida', 'IOUT B / RFB B do U24 ? (a medir)', ''],
      ['U31 / U32 pinos 4 e 7', 'V- e V+', '-12 V e +12 V ? (a medir)', ''], ['U31 / U32 pino 6', 'saida analogica', 'vai a um conector? qual pino? (a medir)', '']]
y = table(cols6, r6, y, rh=11.6, fs=6.4, fills=[GREEN, GREEN, GREEN, YEL, YEL, YEL, YEL])
c.setFont('Helvetica', 6.5)
for k, t in enumerate(simpleSplit('Resistores marrons de precisao (RN55D, 1001F = 1,00 kohm 1%, filme metalico) ao lado do U24/U30. Saida em corrente: Vout = -Vref x codigo/4096 x (Rfb/R) com o conversor inversor; a polaridade e o fundo de escala dependem do AD584 (2,5/5/7,5/10 V) e de eventuais resistores de ganho. Firmware: DAC A fundo de escala 5000 (mV?), DAC C 125000 (12,5 V em 0,1 mV?) - a confirmar medindo a saida.', 'Helvetica', 6.5, W-60)):
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
c.save()
print('ok')
