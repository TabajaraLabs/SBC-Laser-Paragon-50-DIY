# -*- coding: utf-8 -*-
"""Modelo v6 (13/11/2026: inclui a modificacao de RAM 256 KB: A18 nas RAMs, AND 74LS08 Y4xY6 no /CS1, U5 pino 2 levantado).
Modelo da placa PARAGON 50: componentes, pinos e redes.
Confianca de cada ligacao: 'M' medido/confirmado, 'I' inferido (padrao de datasheet / funcao / firmware), '?' desconhecido (a rastrear).
Coordenadas em mm, y para BAIXO (como no KiCad), grade de 2,54."""
P = 2.54
COMPS = []   # lista de dicts
SHEETS = {1: 'CPU, clock e reset', 2: 'Memoria: ROM e RAM', 3: 'Decodificacao de enderecos', 4: 'Saidas digitais ($020018 e $020020)',
          5: 'Entradas digitais e serial', 6: 'Conectores J1/J2 e RepRapDiscount'}

def ic(sheet, ref, value, x, y, left, right, w=25.4, note=''):
    """left/right: listas (numero, nome, rede, conf) de cima para baixo."""
    COMPS.append(dict(sheet=sheet, ref=ref, value=value, x=x, y=y, left=left, right=right, w=w, note=note))

def dip(sheet, ref, value, x, y, n, pins, w=25.4, note=''):
    half = n // 2
    L = []; R = []
    for p in range(1, half + 1):
        nm, net, cf = pins.get(p, ('', None, 'I')); L.append((str(p), nm, net, cf))
    for p in range(n, half, -1):
        nm, net, cf = pins.get(p, ('', None, 'I')); R.append((str(p), nm, net, cf))
    ic(sheet, ref, value, x, y, L, R, w, note)

def hdr(sheet, ref, value, x, y, n, pins, w=17.78, note=''):
    """cabecalho IDC: impares a esquerda, pares a direita"""
    L = []; R = []
    for p in range(1, n + 1, 2):
        nm, net, cf = pins.get(p, ('', None, 'I')); L.append((str(p), nm, net, cf))
    for p in range(2, n + 1, 2):
        nm, net, cf = pins.get(p, ('', None, 'I')); R.append((str(p), nm, net, cf))
    ic(sheet, ref, value, x, y, L, R, w, note)

def A(n): return f'A{n}'
def D(n): return f'D{n}'

# ============================================================ FOLHA 1: CPU, clock, reset
cpu_L = []; cpu_R = []
Dpins = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 64, 6: 63, 7: 62, 8: 61, 9: 60, 10: 59, 11: 58, 12: 57, 13: 56, 14: 55, 15: 54}
for k in range(16): cpu_L.append((str(Dpins[k]), f'D{k}', D(k), 'C'))
cpu_L += [('6', '/AS', '/AS', 'C'), ('7', '/UDS', '/UDS', 'C'), ('8', '/LDS', '/LDS', 'C'), ('9', 'R/W', 'R/W', 'C'), ('10', '/DTACK', 'DTACK_GER', '?'), ('15', 'CLK', 'CLK8M', 'I'),
          ('18', '/RESET', '/RESET', 'I'), ('17', '/HALT', '/HALT', 'I'), ('14', 'VCC', 'VCC', 'C'), ('49', 'VCC', 'VCC', 'C'), ('16', 'GND', 'GND', 'C'), ('53', 'GND', 'GND', 'C')]
apin = {n: 28 + n for n in range(1, 21)}; apin.update({21: 50, 22: 51, 23: 52})
for n in range(1, 24): cpu_R.append((str(apin[n]), f'A{n}', A(n), 'C'))
cpu_R += [('22', '/BERR', 'VCC', 'I'), ('13', '/BR', 'VCC', 'I'), ('11', '/BG', '', 'I'), ('12', '/BGACK', 'VCC', 'I'), ('21', '/VPA', '', 'I'), ('19', '/VMA', '', 'I'), ('20', 'E', '', 'I'),
          ('25', '/IPL0', '/IRQ68681', 'I'), ('24', '/IPL1', '/IRQ68681', 'I'), ('23', '/IPL2', '/IRQ68681', 'I'), ('28', 'FC0', '', 'I'), ('27', 'FC1', '', 'I'), ('26', 'FC2', '', 'I')]
ic(1, 'CPU', 'MC68000P10 (DIP-64)', 150.0, 25.4, cpu_L, cpu_R, w=38.1, note='U? - referencia na placa a anotar')
dip(1, 'XO1', 'modulo oscilador 8 MHz (DIP-14)', 30.0, 40.0, 14, {7: ('GND', 'GND', 'C'), 8: ('OUT', 'CLK8M', 'I'), 14: ('VCC', 'VCC', 'C'), 1: ('NC', None, 'I')}, w=22.86)
dip(1, 'U11', 'DS1232 (reset + watchdog) - serigrafia U11, JP1=TD, JP2=TOL', 30.0, 100.0, 8, {1: ('/PBRST', 'SW1_RST', 'I'), 2: ('TD', 'JP1_TD', 'I'), 3: ('TOL', 'JP2_TOL', 'I'), 4: ('GND', 'GND', 'C'), 5: ('RST', '', 'I'), 6: ('/RST', '/RESET', 'M'),
                                           7: ('/ST', 'OP2_STROBE', 'M'), 8: ('VCC', 'VCC', 'C')}, w=22.86, note='JP1 escolhe o tempo (150 ms...), JP2 a tolerancia (5%/10%); JP6 WATCHDOG INHIBIT nao instalado')
ic(1, 'SW1', 'botao RESET', 30.0, 160.0, [('1', '', 'SW1_RST', 'I')], [('2', '', 'GND', 'I')], w=17.78)
ic(1, 'TB1', 'bornes de alimentacao', 30.0, 190.0, [('1', 'GND', 'GND', 'C'), ('2', '+12V', '+12V', 'C'), ('3', '-12V', '-12V', 'C')], [('4', '+5V ?', 'VCC', '?')], w=19.0, note='entrada do +5 V a confirmar')

# ============================================================ FOLHA 2: memoria
romA = {10: 1, 9: 2, 8: 3, 7: 4, 6: 5, 5: 6, 4: 7, 3: 8, 25: 9, 24: 10, 21: 11, 23: 12, 2: 13}   # pino da ROM -> A(n) da CPU (direto, inferido)
def rom(ref, x, y, dbase, desc):
    pins = {}
    names = {1: 'A15', 2: 'A12', 3: 'A7', 4: 'A6', 5: 'A5', 6: 'A4', 7: 'A3', 8: 'A2', 9: 'A1', 10: 'A0', 11: 'D0', 12: 'D1', 13: 'D2', 14: 'GND', 15: 'D3', 16: 'D4', 17: 'D5', 18: 'D6', 19: 'D7',
             20: '/CE', 21: 'A10', 22: '/OE', 23: 'A11', 24: 'A9', 25: 'A8', 26: 'A13', 27: 'A14', 28: 'VCC'}
    for p, nm in names.items(): pins[p] = (nm, None, 'I')
    ad = {10: 1, 9: 2, 8: 3, 7: 4, 6: 5, 5: 6, 4: 7, 3: 8, 25: 9, 24: 10, 21: 11, 23: 12, 2: 13}
    for p, a in ad.items(): pins[p] = (names[p], A(a), 'I')
    pins[1] = ('A15', 'A16_N', 'M'); pins[26] = ('A13', 'A14_N', 'M'); pins[27] = ('A14', 'A15_N', 'M')
    dm = {11: 0, 12: 1, 13: 2, 15: 3, 16: 4, 17: 5, 18: 6, 19: 7}
    for p, d in dm.items(): pins[p] = (names[p], D(dbase + d), 'C')
    pins[14] = ('GND', 'GND', 'C'); pins[28] = ('VCC', 'VCC', 'C'); pins[20] = ('/CE', 'ROM_CE', 'M'); pins[22] = ('/OE', 'ROM_OE', 'M')
    dip(2, ref, desc, x, y, 28, pins)
rom('U7', 50.8, 25.4, 0, '27C512 ROM LO (bytes impares, D0-D7)')
rom('U8', 190.5, 25.4, 8, '27C512 ROM HI (bytes pares, D8-D15)')
dip(2, 'U26', '74LS14 (3 inversores; pinos usados a anotar)', 330.2, 25.4, 14, {1: ('1A', 'A15', 'M'), 2: ('1Y', 'A15_N', 'M'), 3: ('2A', 'A14', 'M'), 4: ('2Y', 'A14_N', 'M'), 5: ('3A', 'A16', 'M'), 6: ('3Y', 'A16_N', 'M'),
                                                                                  7: ('GND', 'GND', 'C'), 14: ('VCC', 'VCC', 'C')}, w=22.86, note='A15, A14 e A16 da CPU invertidos para a ROM')
def ram(ref, x, y, dbase, we, desc):
    names = {1: 'NC', 2: 'A16', 3: 'A14', 4: 'A12', 5: 'A7', 6: 'A6', 7: 'A5', 8: 'A4', 9: 'A3', 10: 'A2', 11: 'A1', 12: 'A0', 13: 'IO1', 14: 'IO2', 15: 'IO3', 16: 'GND', 17: 'IO4', 18: 'IO5', 19: 'IO6',
             20: 'IO7', 21: 'IO8', 22: '/CS1', 23: 'A10', 24: '/OE', 25: 'A11', 26: 'A9', 27: 'A8', 28: 'A13', 29: '/WE', 30: 'CS2', 31: 'A15', 32: 'VCC'}
    pins = {p: (nm, None, 'I') for p, nm in names.items()}
    ad = {3: 15, 4: 13, 5: 8, 6: 7, 7: 6, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1, 23: 11, 25: 12, 26: 10, 27: 9, 28: 14, 31: 16}
    for p, a in ad.items(): pins[p] = (names[p], A(a), 'M' if p == 31 else 'I')
    for p, d in {13: 0, 14: 1, 15: 2, 17: 3, 18: 4, 19: 5, 20: 6, 21: 7}.items(): pins[p] = (names[p], D(dbase + d), 'C')
    pins[2] = ('A16', 'A18', 'M'); pins[16] = ('GND', 'GND', 'C'); pins[32] = ('VCC', 'VCC', 'C'); pins[22] = ('/CS1', 'RAM_CS_MOD', 'M'); pins[30] = ('CS2', 'VCC', 'M')
    pins[24] = ('/OE', 'ROM_OE', 'M'); pins[29] = ('/WE', we, 'M')
    dip(2, ref, desc, x, y, 32, pins, note='adaptador 28->32 (soquete DS1230Y). MOD 256 KB: pino 2 = A18 (CPU 46), pino 22 = saida do 74LS08 (RAM_CS_MOD), pino 31 = A16 da CPU')
ram('U13', 50.8, 165.1, 0, 'WE_L', 'KM681000BLP-5 RAM (D0-D7)')
ram('U14', 190.5, 165.1, 8, 'WE_H', 'KM681000BLP-5 RAM (D8-D15)')

dip(2, 'U_AND', '74LS08 (MOD RAM 256 KB, soldado em cima da placa): /CS1 = Y4 AND Y6', 330.2, 100.0, 14, {1: ('1A', 'RAM_CS', 'M'), 2: ('1B', 'Y6_SEL', 'M'), 3: ('1Y', 'RAM_CS_MOD', 'M'),
    4: ('2A', 'GND', 'M'), 5: ('2B', 'GND', 'M'), 9: ('3A', 'GND', 'M'), 10: ('3B', 'GND', 'M'), 12: ('4A', 'GND', 'M'), 13: ('4B', 'GND', 'M'), 7: ('GND', 'GND', 'C'), 14: ('VCC', 'VCC', 'C')}, w=22.86,
    note='/CS1 ativo quando Y4=0 (RAM1) ou Y6=0 (RAM2); livres em GND')
ic(3, 'R_MOD', 'resistor 1 kohm (MOD: U5 pino 2 preso a +5 V)', 230.0, 165.0, [('1', '', 'U5_2_FIXO', 'M')], [('2', '', 'VCC', 'M')], w=19.0, note='perna 2 do U5 levantada (fora do soquete)')

# ============================================================ FOLHA 3: decodificacao
dip(3, 'U19', '74LS30 NAND de 8 entradas (detecta topo da memoria)', 40.0, 30.0, 14, {1: ('in', 'U19_1?', '?'), 2: ('in', 'A19', 'M'), 3: ('in', 'A20', 'M'), 4: ('in', 'A21', 'M'), 5: ('in', 'A22', 'M'), 6: ('in', 'A23', 'M'),
    7: ('GND', 'GND', 'C'), 8: ('Y', 'U4_C_SEL', 'I'), 11: ('in', 'U19_11?', '?'), 12: ('in', 'U19_12?', '?'), 14: ('VCC', 'VCC', 'C')}, w=22.86,
    note='SAIDA (pino 8) = 0 so se todas as entradas = 1 (A19-A23 = 11111, endereco >= $F80000). CONFLITO: medido U4-3 -> U19 p7 (GND num 74LS30) e A18 -> U19 p8 (saida). Reconferir numeracao.')
dip(3, 'U4', '74LS138 decodificador de blocos de 128 KB', 120.0, 30.0, 16, {1: ('A', 'A17', 'M'), 2: ('B', 'A18', 'M'), 3: ('C', 'U4_C_SEL', 'M'), 4: ('/G2A', 'U21_5', 'M'), 5: ('/G2B', 'U1_9', 'M'), 6: ('G1', 'U1_15', 'M'),
        7: ('Y7', 'Y7_SEL', 'M'), 8: ('GND', 'GND', 'M'), 9: ('Y6', 'Y6_SEL', 'M'), 10: ('Y5', 'IO16_SEL', 'M'), 11: ('Y4', 'RAM_CS', 'M'), 12: ('Y3', 'Y3_SEL', 'M'), 13: ('Y2', '', 'M'), 14: ('Y1', 'Y1_SEL', 'M'), 15: ('Y0', 'Y0_SEL', 'M'),
        16: ('VCC', 'VCC', 'C')}, w=25.4)
dip(3, 'U6', '74LS138 sub-decodificador de E/S ($0200xx)', 230.0, 30.0, 16, {1: ('A', 'U6_A?', '?'), 2: ('B', 'U6_B?', '?'), 3: ('C', 'U6_C?', '?'), 4: ('/G2A', 'IO16_SEL', 'I'), 5: ('/G2B', 'U6_ENB?', '?'),
        6: ('G1', 'U6_ENC?', '?'), 7: ('Y7', 'U6_Y7?', '?'), 8: ('GND', 'GND', 'C'), 9: ('Y6', 'U6_Y6?', '?'), 10: ('Y5', 'U6_Y5?', '?'), 11: ('Y4', 'U6_Y4?', '?'), 12: ('Y3', 'WR_Y3', 'M'), 13: ('Y2', 'U6_Y2?', '?'),
        14: ('Y1', 'U6_Y1?', '?'), 15: ('Y0', 'U6_Y0?', '?'), 16: ('VCC', 'VCC', 'C')}, w=25.4, note='Y de $020018 / $020028 / $020030 a localizar')
dip(3, 'U10', '74LS14 (clock de $020020)', 330.2, 30.0, 14, {1: ('1A', 'WR_Y3', 'M'), 2: ('1Y', 'CLK_020020', 'M'), 7: ('GND', 'GND', 'C'), 14: ('VCC', 'VCC', 'C')}, w=22.86, note='2 a 4 inversores livres')
dip(3, 'U28', 'U28 74LS00 (gera /WE da RAM)', 40.0, 120.0, 14, {3: ('3Y', 'WE_L', 'M'), 11: ('4Y', 'WE_H', 'M'), 13: ('4B', 'WR_ACTIVE', 'M'), 7: ('GND', 'GND', 'C'), 14: ('VCC', 'VCC', 'C')}, w=22.86,
    note='nenhum pino de entrada medido vai ao /CS da RAM (WE nao depende do endereco)')
dip(3, 'U22', 'U22 74LS00 (strobes e R/W)', 40.0, 200.0, 14, {4: ('2A', '/UDS', 'M'), 5: ('2B', '/LDS', 'M'), 6: ('2Y', 'STROBE_ANY', 'M'), 12: ('4A', 'R/W', 'M'), 13: ('4B', 'R/W', 'M'), 11: ('4Y', 'WR_ACTIVE', 'M'), 7: ('GND', 'GND', 'C'), 14: ('VCC', 'VCC', 'C')}, w=22.86,
    note='gate2: strobe ativo (UDS ou LDS); gate4: inversor do R/W = escrita')
dip(3, 'U2', 'U2 74LS00 (gera /OE de ROM e RAM)', 150.0, 200.0, 14, {8: ('3Y', 'ROM_OE', 'M'), 9: ('3A', 'STROBE_ANY', 'M'), 10: ('3B', 'R/W', 'M'), 7: ('GND', 'GND', 'C'), 14: ('VCC', 'VCC', 'C')}, w=22.86,
    note='/OE = NAND(strobe, R/W): ativo em toda leitura, sem depender de endereco')
ic(3, 'J7', 'J7 pino 48 (conector a identificar; talvez J1?)', 330.0, 120.0, [('48', 'U4_C_SEL', 'U4_C_SEL', 'M')], [], w=19.0, note='liga a U4-3 e U19-7')
ic(3, 'LOGICA?', 'logica a rastrear (U35 74LS11, U34 74LS74, U1, U33 ...)', 120.0, 120.0, [('', 'R/W', 'R/W', 'C'), ('', '/UDS', '/UDS', 'C'), ('', '/LDS', '/LDS', 'C'), ('', '/AS', '/AS', 'C'),
   ('', 'RAM_CS', 'RAM_CS', 'M'), ('', 'IO16_SEL', 'IO16_SEL', 'M'), ('', 'IO8_SEL', 'IO8_SEL', 'I')],
   [('', 'DTACK_GER', 'DTACK_GER', '?'), ('', 'ROM_CE', 'ROM_CE', '?'), ('', 'DUART_CS', 'DUART_CS', '?'), ('', 'U4_ENA?', 'U4_ENA?', '?'),
    ('', 'U4_ENB?', 'U4_ENB?', '?'), ('', 'U4_ENC?', 'U4_ENC?', '?')], w=40.64, note='caixa de interrogacao: o que ainda nao foi rastreado')

# ============================================================ FOLHA 4: saidas
q273 = {0: 2, 1: 5, 2: 6, 3: 9, 4: 12, 5: 15, 6: 16, 7: 19}   # bit -> pino Q do 74LS273
d273 = {2: 3, 5: 4, 6: 7, 9: 8, 12: 13, 15: 14, 16: 17, 19: 18}  # pino Q -> pino D
def latch273(ref, x, y, dbase, nets, desc, clk):
    pins = {1: ('/MR', 'VCC', '?'), 10: ('GND', 'GND', 'C'), 11: ('CLK', clk[0], clk[1]), 20: ('VCC', 'VCC', 'C')}
    qn = {2: 'Q0', 5: 'Q1', 6: 'Q2', 9: 'Q3', 12: 'Q4', 15: 'Q5', 16: 'Q6', 19: 'Q7'}; dn = {3: 'D0', 4: 'D1', 7: 'D2', 8: 'D3', 13: 'D4', 14: 'D5', 17: 'D6', 18: 'D7'}
    for bit in range(8):
        qp = q273[bit]; dp = d273[qp]
        pins[qp] = (qn[qp], nets[bit][0], nets[bit][1]); pins[dp] = (dn[dp], D(dbase + bit), 'I')
    dip(4, ref, desc, x, y, 20, pins)
latch273('U46', 140.0, 30.0, 0, [(f'O20_{b}', 'M') for b in range(8)], '74LS273 $020020 byte BAIXO (U46)', ('CLK_020020', 'M'))
latch273('U40', 140.0, 120.0, 8, [(f'O20_{b}', 'M') for b in range(8, 16)], '74LS273 $020020 byte ALTO (U40)', ('CLK_020020', 'M'))
def lsa06(ref, x, y, m, note=''):
    dip(4, ref, '74LS06 inversor coletor aberto', x, y, 14, m, w=22.86, note=note)
lsa06('U41', 230.0, 30.0, {1: ('1A', 'O20_0', 'M'), 2: ('1Y', 'O20_0N', '?'), 3: ('2A', '', 'M'), 4: ('2Y', '', 'M'), 5: ('3A', 'O20_10', 'M'), 6: ('3Y', 'O20_10N', '?'), 7: ('GND', 'GND', 'C'),
    8: ('4Y', 'O20_11N', '?'), 9: ('4A', 'O20_11', 'M'), 10: ('5Y', 'O20_9N', '?'), 11: ('5A', 'O20_9', 'M'), 12: ('6Y', 'O20_1N', '?'), 13: ('6A', 'O20_1', 'M'), 14: ('VCC', 'VCC', 'C')}, '2A livre; saidas ate o conector a rastrear')
lsa06('U47', 230.0, 100.0, {1: ('1A', 'O20_2', 'M'), 2: ('1Y', 'O20_2N', '?'), 3: ('2A', 'O20_4', 'M'), 4: ('2Y', 'O20_4N', '?'), 5: ('3A', 'O20_6', 'M'), 6: ('3Y', 'O20_6N', '?'), 7: ('GND', 'GND', 'C'),
    8: ('4Y', 'J1_48', 'M'), 9: ('4A', 'O20_7', 'M'), 10: ('5Y', 'O20_5N', '?'), 11: ('5A', 'O20_5', 'M'), 12: ('6Y', 'O20_3N', '?'), 13: ('6A', 'O20_3', 'M'), 14: ('VCC', 'VCC', 'C')}, 'bit 7 invertido vai ao J1-48')
dip(4, 'U38', 'AD7501 chave analogica (pinos nao identificados)', 320.0, 30.0, 16, {16: ('ctl', 'O20_12', 'M'), 1: ('ctl', 'O20_13', 'M'), 4: ('ctl', 'O20_14', 'M'), 3: ('ctl', 'O20_15', 'M')}, w=22.86, note='comandada por $020020 bits 12-15')
dip(4, 'U39?', '74LS273 (U39) - so o pino 8 foi medido', 320.0, 100.0, 20, {8: ('D3', 'O20_8', '?'), 11: ('CLK', '', '?'), 10: ('GND', 'GND', 'C'), 20: ('VCC', 'VCC', 'C')}, w=22.86,
    note='CONFLITO: U39 tambem e citado como latch de $020018. Verificar.')
lat18 = [('', f'D{b}', D(b), 'I') for b in range(16)]
j18 = {0: 'J1_28', 1: 'J1_26', 2: 'J1_24', 3: 'J1_20', 4: 'J1_18', 5: 'J1_15', 6: 'J1_14', 7: 'J1_10', 8: 'J2_47', 9: 'J2_40', 10: 'J2_37', 11: 'J2_30', 12: 'J2_28', 13: 'J2_27', 14: 'J2_24', 15: 'J2_23'}
ic(4, 'LATCH18', 'U39/U45 2x74LS273 $020018 (pinos Q a anotar)', 40.0, 30.0, lat18 + [('', 'CLK', 'CLK_020018?', '?')], [('', f'b{b}', j18[b], 'M') for b in range(16)], w=30.48,
   note='push-pull TTL 0-4,3 V, so escrita')

# ============================================================ FOLHA 5: entradas e serial
ic(5, 'PORTB', 'U42+U48 74LS240 x2 - porta B $020028 (inversora, pull-up 4,7k)', 40.0, 30.0,
   [('', f'b{b}', ({0: 'J1_7', 1: 'J1_35', 2: 'J1_33', 3: 'J1_31', 4: 'J1_27', 5: 'J1_25', 6: 'J1_23', 7: 'J1_36'}.get(b, f'SW2_{b - 7}') if b < 8 else f'SW2_{b - 7}'), 'M' if b < 7 else 'I') for b in range(16)] + [('', '/OE', 'RD_020028?', '?')],
   [('', f'D{b}', D(b), 'I') for b in range(16)], w=30.48, note='B0-B6 medidos; B7 provavel J1-36; bits 8-15 = DIP SW2 (U48)')
ic(5, 'PORTA', 'U44+U37 74LS240 x2 - porta A $020030', 40.0, 125.0,
   [('', f'b{b}', ('J1_4' if b == 3 else f'INA{b}?'), 'M' if b == 3 else '?') for b in range(16)] + [('', '/OE', 'RD_020030?', '?')], [('', f'D{b}', D(b), 'I') for b in range(16)], w=30.48, note='so A3 localizado (J1-4)')
dip(5, 'SW2', 'DIP de 8 chaves (bits 8-15 da porta B)', 40.0, 220.0, 16, {**{i: (f'S{i}', f'SW2_{i}', 'I') for i in range(1, 9)}, **{17 - i: (f'S{i}', 'GND', 'I') for i in range(1, 9)}}, w=22.86)
ic(5, 'DUART', 'MC68681P DUART (pinos nao numerados: a anotar)', 150.0, 30.0,
   [('', f'D{b}', D(b), 'I') for b in range(8)] + [('', 'A1-A4', 'A1..A4', 'I'), ('', '/CS', 'DUART_CS', '?'), ('', 'R/W', 'R/W', 'C'), ('', '/DTACK', 'DTACK_GER', '?'), ('', '/RESET', '/RESET', 'I'), ('', 'X1/X2', 'XTAL3M68', 'I')],
   [('', 'RxDA', 'RXA_L', 'I'), ('', 'TxDA', 'TXA_L', 'I'), ('', 'RxDB', 'RXB_L', 'I'), ('', 'TxDB', 'TXB_L', 'I'), ('', 'IP0 (CTSA)', 'CTSA_L', 'I'), ('', 'IP1 (CTSB)', 'CTSB_L', 'I'), ('', 'OP0 (RTSA)', 'RTSA_L', 'I'),
    ('', 'OP1 (RTSB)', 'RTSB_L', 'I'), ('', 'OP2', 'OP2_STROBE', 'M'), ('', 'IP3', 'IP3?', '?'), ('', 'IRQ', '/IRQ68681', 'I')], w=30.48, note='cristal proprio 3,6864 MHz; usa D0-D7 (bytes impares)')
dip(5, 'U36', 'MC1489 receptores RS-232', 250.0, 30.0, 14, {1: ('A1', 'RXA_232', 'M'), 3: ('Y1', 'RXA_L', 'I'), 4: ('A2', 'CTSA_232', 'M'), 6: ('Y2', 'CTSA_L', 'I'), 10: ('A3', 'CTSB_232', 'M'), 8: ('Y3', 'CTSB_L', 'I'),
    13: ('A4', 'RXB_232', 'M'), 11: ('Y4', 'RXB_L', 'I'), 7: ('GND', 'GND', 'C'), 14: ('VCC', 'VCC', 'C')}, w=22.86)
dip(5, 'U43', 'DS1488 drivers RS-232', 250.0, 95.0, 14, {11: ('Y4', 'TXA_232', 'M'), 12: ('A4a', 'TXA_L', 'I'), 13: ('A4b', 'TXA_L', 'I'), 6: ('Y2', 'TXB_232', 'M'), 4: ('A2a', 'TXB_L', 'I'), 5: ('A2b', 'TXB_L', 'I'),
    3: ('Y1', 'RTSB_232', 'M'), 2: ('A1', 'RTSB_L', 'I'), 8: ('Y3', 'RTSA_232', 'M'), 9: ('A3a', 'RTSA_L', 'I'), 10: ('A3b', 'RTSA_L', 'I'), 7: ('GND', 'GND', 'C'), 1: ('VEE', '-12V', 'I'), 14: ('VCC', '+12V', 'I')}, w=22.86)
hdr(5, 'J4', 'J4 IDC-20 serial (DE-9 femea)', 330.0, 30.0, 20, {1: ('GND', 'GND', 'M'), 2: ('GND', 'GND', 'M'), 3: ('RXA', 'RXA_232', 'M'), 4: ('RXB', 'RXB_232', 'M'), 5: ('TXA', 'TXA_232', 'M'), 6: ('TXB', 'TXB_232', 'M'),
    7: ('CTSA', 'CTSA_232', 'M'), 8: ('CTSB', 'CTSB_232', 'M'), 9: ('RTSB', 'RTSB_232', 'M'), 11: ('RTSA', 'RTSA_232', 'M'), 12: ('GND', 'GND', 'M'), 13: ('GND', 'GND', 'M'), 15: ('=11', 'RTSA_232', 'M')}, w=17.78, note='10,14,16-20 sem conexao')

# ============================================================ FOLHA 6: J1, J2, RepRap
J1 = {1: 'GND', 2: 'GND', 4: 'IN_A3', 7: 'J1_7', 9: 'GND', 10: 'J1_10', 14: 'J1_14', 15: 'J1_15', 18: 'J1_18', 20: 'J1_20', 23: 'J1_23', 24: 'J1_24', 25: 'J1_25', 26: 'J1_26', 27: 'J1_27', 28: 'J1_28', 29: '', 31: 'J1_31',
      33: 'J1_33', 35: 'J1_35', 36: 'J1_36', 48: 'J1_48', 50: 'GND'}
J1 = {k: v for k, v in J1.items() if v}
J1['4'] = None
j1pins = {}
for p in range(1, 51):
    net = {4: 'J1_4'}.get(p, J1.get(p))
    cf = 'M'
    if p == 36: cf = 'I'
    nm = {7: 'B0', 35: 'B1', 33: 'B2', 31: 'B3', 27: 'B4', 25: 'B5', 23: 'B6', 36: 'B7?', 4: 'A3', 28: 'b0', 26: 'b1', 24: 'b2', 20: 'b3', 18: 'b4', 15: 'b5', 14: 'b6', 10: 'b7', 48: '$20020 b7', 1: 'GND', 2: 'GND', 9: 'GND', 50: 'GND', 29: 'sem resposta', 13: 'ruido', 17: 'ruido'}.get(p, '')
    j1pins[p] = (nm, net, cf)
ic(6, 'J1', 'J1 IDC-50 (saidas $020018 b0-b7, entradas, GND)', 30.0, 25.4, [(str(p), *j1pins[p]) for p in range(1, 51)], [], w=20.32)
j2 = {47: ('b8', 'J2_47'), 40: ('b9', 'J2_40'), 37: ('b10', 'J2_37'), 30: ('b11', 'J2_30'), 28: ('b12', 'J2_28'), 27: ('b13', 'J2_27'), 24: ('b14', 'J2_24'), 23: ('b15', 'J2_23')}
ic(6, 'J2', 'J2 IDC-50 (saidas $020018 b8-b15)', 60.0, 25.4, [(str(p), *(j2[p] if p in j2 else ('', None)), 'M') for p in range(1, 51)], [], w=20.32)
exp1 = [('1', 'BEEPER', 'J2_40'), ('2', 'BTN_ENC', 'J1_31'), ('3', 'LCD_EN', 'J1_20'), ('4', 'LCD_RS', 'J1_18'), ('5', 'LCD_D4', 'J1_15'), ('6', 'LCD_D5', 'J1_14'), ('7', 'LCD_D6', 'J1_10'), ('8', 'LCD_D7', 'J2_47'),
        ('9', 'GND', 'GND'), ('10', '+5V', '+5V_EXT')]
exp2 = [('1', 'MISO', 'J1_7'), ('2', 'SCK', 'J1_28'), ('3', 'BTN_EN1', 'J1_33'), ('4', 'SD_CS', 'J1_24'), ('5', 'BTN_EN2', 'J1_35'), ('6', 'MOSI', 'J1_26'), ('7', 'SD_DET', 'J1_27'), ('8', 'KILL', ''), ('9', 'GND', 'GND'), ('10', '', '')]
ic(6, 'EXP1', 'RepRapDiscount EXP1 (ordem a confirmar na serigrafia)', 330.0, 40.0, [(a, b, c, 'I') for a, b, c in exp1], [], w=20.32, note='LCD 20x4 + buzzer + encoder')
ic(6, 'EXP2', 'RepRapDiscount EXP2 (ordem a confirmar na serigrafia)', 330.0, 110.0, [(a, b, c, 'I') for a, b, c in exp2], [], w=20.32, note='SD (SPI) + botoes')

ic(6, 'JP?AD', 'jumper A/D GROUND (2 furos, serigrafia sem referencia)', 150.0, 160.0, [('1', '', 'AGND?', '?')], [('2', '', 'GND', '?')], w=19.0, note='liga terra analogico ao digital; a confirmar')

dip(3, 'U5', '74LS11 (3 portas AND de 3 entradas)', 230.0, 120.0, 14, {1: ('1A', 'IO16_SEL', 'M'), 2: ('1B', 'U5_2_FIXO', 'M'), 13: ('1C', 'Y1_SEL', 'M'), 12: ('1Y', 'U5_1Y?', '?'),
    3: ('2A', '', '?'), 4: ('2B', 'Y7_SEL', 'M'), 5: ('2C', 'Y3_SEL', 'M'), 6: ('2Y', 'U5_2Y?', '?'),
    9: ('3A', '', '?'), 10: ('3B', 'Y0_SEL', 'M'), 11: ('3C', '', '?'), 8: ('3Y', 'ROM_CE', 'M'), 7: ('GND', 'GND', 'C'), 14: ('VCC', 'VCC', 'C')}, w=22.86,
    note='porta 1: entradas = Y5 (E/S, U4-10), Y6 (U4-9, DESLIGADO na modificacao: perna 2 levantada e presa a +5 V por 1k) e Y1 (DUART, U4-14). Saida 1Y (pino 12) a rastrear. 3Y vai ao /CE das EPROMs')
dip(3, 'U1', '74LS175 (4 flip-flops D - temporizacao?)', 330.0, 120.0, 16, {9: ('CLK', 'U1_9', 'M'), 15: ('4Q', 'U1_15', 'M'), 8: ('GND', 'GND', 'C'), 16: ('VCC', 'VCC', 'C')}, w=22.86,
    note='4Q habilita o U4 (G1); pino 9 vai ao /G2B do U4')
ic(3, 'U21', 'U21 (CI a identificar)', 330.0, 200.0, [('5', '', 'U21_5', 'M')], [], w=19.0, note='pino 5 vai ao /G2A do U4')
