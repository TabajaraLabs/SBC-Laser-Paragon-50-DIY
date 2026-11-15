# gera Paragon50_Pinos_J1_J2_J7_CIs_v1.pdf (folhas de mapeamento com multimetro)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
W, H = A4
OUT = 'Paragon50_Pinos_J1_J2_J7_CIs_v1.pdf'
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
    c.drawString(30, 12, 'Tabajara Labs - PARAGON 50 - 14/Nov/2026 - v1. Colunas em branco = para anotar com o multimetro (placa DESLIGADA, teste de continuidade).')
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
J2 = {23: (*lat(15), 'medido', ''), 24: (*lat(14), 'medido', ''), 27: (*lat(13), 'medido', ''), 28: (*lat(12), 'medido', ''),
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
conn_page('J2', J2, 2, 'Em J2 so se conhecem as saidas dos bits 8-15 de $020018 (74LS273 do byte alto). As entradas $020028 b8-15 sao a chave SW2 (nao vao ao conector).')
c.showPage()

# ---------- J7 ----------
head('J7 - conector de 50 pinos (IDC macho)', ['Quase nada mapeado ainda. Unico pino conhecido: 48.', 'Hipotese de trabalho: J7 leva sinais de selecao/estado do laser; as perguntas abaixo orientam o que procurar.'])
J7 = {48: ('Selecao C do decodificador U4 (U4_C_SEL)', 'U4 (74LS138) pino 3 / U19 pino 8', 'medido', 'liga A19-A23 -> U4 entrada C')}
rows = []; fills = []
for p in range(1, 51):
    d = J7.get(p)
    if d: rows.append([p, d[0], '?', d[1], d[3], '']); fills.append(GREEN)
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
      (13, 'OP3', 'SAI', '? (A/D?)', 'FIRMWARE: pulso = CONVST do AD7875 (inferido)'), (14, 'OP5', 'SAI', '?', 'usado pelo firmware original (funcao desconhecida)'),
      (15, 'OP7', 'SAI', '?', 'usado pelo firmware original (funcao desconhecida)'), (16, 'D1', 'barramento', 'D1', ''), (17, 'D3', 'barramento', 'D3', ''),
      (18, 'D5', 'barramento', 'D5', ''), (19, 'D7', 'barramento', 'D7', ''), (20, 'GND', 'GND', 'GND', ''),
      (21, '/INTRN', 'saida', '/IRQ68681 -> CPU', ''), (22, 'D6', 'barramento', 'D6', ''), (23, 'D4', 'barramento', 'D4', ''), (24, 'D2', 'barramento', 'D2', ''),
      (25, 'D0', 'barramento', 'D0', ''), (26, 'OP6', 'SAI', '?', 'usado pelo firmware original (funcao desconhecida)'), (27, 'OP4', 'SAI', '?', 'nao usado pelo firmware conhecido'),
      (28, 'OP2', 'SAI', 'U11 pino 7 (/ST do watchdog)', 'STROBE do watchdog (monitor mexe so aqui e em OP3)'),
      (29, 'OP0 (RTSA)', 'SAI', 'U43 pino 10 (A3)', 'RTSA'), (30, 'TxDA', 'SAI', 'U43 pinos 12/13', 'console 57600 bps'), (31, 'RxDA', 'ENT', 'U36 pino 3 (Y1)', 'console'),
      (32, 'X1/CLK', 'cristal', 'XO1/cristal 3,6864 MHz', ''), (33, 'X2', 'cristal', '', ''), (34, '/RESET', 'ENT', '/RESET', ''), (35, '/CS', 'ENT', 'DUART_CS (decodificador)', ''),
      (36, 'IP2', 'ENT', '?', 'livre?'), (37, '/IACK', 'ENT', '?', 'normalmente a VCC'), (38, 'IP5', 'ENT', '?', 'livre?'),
      (39, 'IP4', 'ENT', '? (BUSY do A/D)', 'FIRMWARE: 1 = A/D pronto (inferido)'), (40, 'VCC', 'VCC', '+5 V', '')]
cols = [('Pino', 26), ('Sinal', 70), ('E/S', 45), ('Ligado a', 140), ('Observacao', 170), ('ANOTAR', 84)]
rows = []; fills = []
for p, s, io, lig, ob in DU:
    rows.append([p, s, io, lig, ob, '']); 
    fills.append(BLUE if io in ('GND', 'VCC') else (GREY if io == 'barramento' else (YEL if '?' in lig or io in ('ENT', 'SAI') and lig.startswith('?') else YEL)))
y = table(cols, rows, H-84, rh=12.3, fs=6.6, fills=fills)
c.setFont('Helvetica', 7); c.setFillColor(colors.black)
c.drawString(30, y-8, 'Candidatos a E/S livres para teste: OP3, OP4, OP5, OP6, OP7 (saidas) e IP2, IP3, IP4, IP5 (entradas). Neste teste de bancada nao ha laser conectado.')
footer(4); c.showPage()

# ---------- AD7875 e multiplexador ----------
head('A/D AD7875 (24 pinos DIP) e multiplexador analogico (U38)', [
    'AD7875: 12 bits, 0 a +5 V, 1 LSB = 1,22 mV, 100 kHz. Pinagem do datasheet Analog Devices (DIP/SOIC-24). Resultado lido em $020000 (palavra, 12 bits baixos).',
    'Hipoteses do firmware original: disparo = pulso em OP3 (CONVST); pronto = IP4 (BUSY); canal = $020020 bits 14-12; bit 15 = habilita o mux.'])
AD = [(1, '/RD', 'ENT', 'leitura de $020000 (decodificador)', ''), (2, '/BUSY-INT', 'SAI', 'IP4 do DUART (pino 39)?', 'conferir'), (3, 'CLK', 'ENT', '?', 'a VSS = clock interno'),
      (4, 'DB11/HBEN', 'SAI', 'D11 ?', 'conferir ordem do barramento'), (5, 'DB10/SSTRB', 'SAI', 'D10 ?', ''), (6, 'DB9/SCLK', 'SAI', 'D9 ?', ''), (7, 'DB8/SDATA', 'SAI', 'D8 ?', ''),
      (8, 'DB7/LOW', 'SAI', 'D7 ?', ''), (9, 'DB6/LOW', 'SAI', 'D6 ?', ''), (10, 'DB5/LOW', 'SAI', 'D5 ?', ''), (11, 'DB4/LOW', 'SAI', 'D4 ?', ''), (12, 'DGND', 'GND', 'GND', ''),
      (13, 'DB3/DB11', 'SAI', 'D3 ?', ''), (14, 'DB2/DB10', 'SAI', 'D2 ?', ''), (15, 'DB1/DB9', 'SAI', 'D1 ?', ''), (16, 'DB0/DB8', 'SAI', 'D0 ?', ''),
      (17, 'VDD', 'VCC', '+5 V', ''), (18, 'AGND', 'GND', 'AGND (JP?AD pino 1?)', 'verificar se separa de GND'), (19, 'REF OUT', 'SAI', '?', '3 V interna, ate 500 uA'),
      (20, 'VIN', 'ENT', 'saida do multiplexador?', 'entrada analogica 0-5 V'), (21, 'VSS', 'VCC', '-5 V ou GND', 'tem -5 V na placa? (so +12/-12 vistos)'),
      (22, '12/8/CLK', 'ENT', '?', 'alto = saida paralela de 12 bits'), (23, 'CONVST', 'ENT', 'OP3 do DUART (pino 13)?', 'borda de subida inicia a conversao'), (24, '/CS', 'ENT', 'selecao de $020000 (decodificador)', '')]
cols2 = [('Pino', 26), ('Mnemonico', 78), ('E/S', 32), ('Ligado a (hipotese)', 150), ('Observacao', 150), ('ANOTAR', 109)]
rows = []; fills = []
for p, s, io, lig, ob in AD:
    rows.append([p, s, io, lig, ob, '']); fills.append(BLUE if io in ('GND', 'VCC') else YEL)
y = table(cols2, rows, H-84, rh=12.3, fs=6.6, fills=fills)
y -= 10
c.setFont('Helvetica-Bold', 8); c.drawString(30, y, 'Multiplexador analogico - U38 (16 pinos; tipo ainda nao identificado)'); y -= 4
cols3 = [('Pino U38', 50), ('Funcao', 150), ('Ligado a', 190), ('ANOTAR', 155)]
rows = [[16, 'controle (canal bit 0)', '$020020 bit 12 (U40 Q4, pino 12)', ''], [1, 'controle (canal bit 1)', '$020020 bit 13 (U40 Q5, pino 15)', ''],
        [4, 'controle (canal bit 2)', '$020020 bit 14 (U40 Q6, pino 16)', ''], [3, 'controle (habilita?)', '$020020 bit 15 (U40 Q7, pino 19)', '']]
table(cols3, rows, y, rh=12.4, fs=6.6, fills=[GREEN]*4)
c.setFont('Helvetica', 6.8)
c.drawString(30, 70, 'Os outros pinos de U38 (entradas dos 8 canais, saida comum, alimentacao +-12 V ou +-5 V) ainda nao foram anotados. Ordem dos bits de canal a confirmar.')
c.drawString(30, 60, 'U40 = 74LS273 do byte alto de $020020 (push-pull). Fontes: Paragon50_Netlist_v6.csv e Firmware_original_AD_DA_v1.txt.')
footer(5); c.showPage()

# ---------- DACs, 8254 , $020020 ----------
head('Conversores D/A, 8254 e saidas de $020020', [
    'Os integrados D/A ainda NAO foram identificados na placa. Firmware: palavras de 12 bits escritas em $02000A (DAC A) e $02000C (DAC C); nao ha DAC B nem leitura de volta.',
    'Procure integrados de 16-20 pinos com entradas D0-D11 ligadas ao barramento de dados e um /WR (ou /CS + /WR) vindo do decodificador U6.'])
cols4 = [('Item', 150), ('Pino / nome', 90), ('Ligado a (a descobrir)', 180), ('ANOTAR (CI e pino)', 113)]
items = [('DAC A - CI (nome/marcacao)', '', '$02000A', ''), ('DAC A - entradas de dados (12)', 'D0..D11', 'barramento de dados?', ''),
         ('DAC A - /CS ou /WR', '', 'saida do decodificador U6 (74LS138)?', ''), ('DAC A - saida analogica', 'OUT/VOUT', 'conector? (J7?)', ''), ('DAC A - referencia', 'VREF', '', ''),
         ('DAC C - CI (nome/marcacao)', '', '$02000C', ''), ('DAC C - entradas de dados (12)', 'D0..D11', 'barramento de dados?', ''),
         ('DAC C - /CS ou /WR', '', 'saida do decodificador U6?', ''), ('DAC C - saida analogica', 'OUT/VOUT', 'conector?', ''), ('DAC C - referencia', 'VREF', '', '')]
rows = [list(i) for i in items]
y = table(cols4, rows, H-92, rh=12.4, fs=6.6, fills=[YEL]*10)
y -= 12
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
footer(6); c.showPage()
c.save()
print('ok')
