#!/usr/bin/env python3
"""Esquema funcional da placa PARAGON 50 (68000) - v1. 4 folhas A3 paisagem -> Paragon50_Esquema_v1.pdf + PNGs.
Baseado em medicoes, fotos e firmware. Itens marcados com [?] ainda precisam de confirmacao na placa."""
import sys, textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['text.parse_math'] = False
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.backends.backend_pdf import PdfPages

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
VERSAO = 'v1'
DATA = '12/11/2026'
C = dict(cpu='#d9e8fb', mem='#fff2cc', io='#e2f0d9', dec='#fce4d6', conn='#ededed', clk='#e8def8',
         bus='#1f4e79', out='#2f6fd0', out2='#e07b00', inp='#2e9d4f', gnd='#555555', free='#f4f4f4', ext='#fdf6e3')

def novo(titulo, folha):
    fig = plt.figure(figsize=(16.54, 11.69))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 420); ax.set_ylim(0, 297); ax.axis('off')
    ax.add_patch(Rectangle((4, 4), 412, 289, fill=False, lw=1.2, ec='k'))
    # carimbo
    ax.add_patch(Rectangle((250, 4), 166, 22, fill=False, lw=1, ec='k'))
    ax.text(254, 20, 'PARAGON 50 - placa CPU 68000 (Heraeus Surgical)', fontsize=10, weight='bold', va='center')
    ax.text(254, 14.5, titulo, fontsize=9, va='center')
    ax.text(254, 9, f'Tabajara Labs - esquema funcional {VERSAO} - {DATA} - folha {folha}/4', fontsize=7.5, va='center', color='#333')
    ax.text(412, 8, '[?] = a confirmar na placa', fontsize=6.5, ha='right', va='center', color='#a00')
    return fig, ax

def caixa(ax, x, y, w, h, titulo, linhas, cor, fs=6.6, tfs=8, wrap=None, ls='-'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=1.5', fc=cor, ec='#222', lw=1, ls=ls))
    ax.text(x + 2, y + h - 3.2, titulo, fontsize=tfs, weight='bold', va='top')
    yy = y + h - 8.5
    for ln in linhas:
        for sub in (textwrap.wrap(ln, wrap) if wrap else [ln]):
            ax.text(x + 2, yy, sub, fontsize=fs, va='top', family='DejaVu Sans'); yy -= 3.4

def linha(ax, pts, cor='#222', lw=1.2, seta=False, ls='-'):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=cor, lw=lw, ls=ls, solid_capstyle='butt')
    if seta:
        ax.annotate('', xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle='-|>', color=cor, lw=lw, mutation_scale=9))

def ponto(ax, x, y, cor='#222'): ax.plot([x], [y], 'o', ms=3.5, color=cor)

# ----------------------------------------------------------------------------------------------- folha 1
def folha1():
    fig, ax = novo('Folha 1 - Diagrama funcional do sistema (barramento, memoria, E/S)', 1)
    # CPU
    caixa(ax, 10, 128, 52, 112, 'U? MC68000P10', [
        'DIP-64, 10 MHz nominal', 'clock: modulo 8 MHz (XO-43B)', 'A1-A23 / D0-D15', '/AS /UDS /LDS R/W', '/DTACK  (/BERR em Vcc:',
        '   sem timeout de barramento)', 'FC0-FC2', '/RESET /HALT <- DS1232', 'IPL <- IRQ do 68681', '   (vetor $1F)', '',
        'Pinos: A16=44 A17=45 A18=46', 'A19=47 A20=48 A21=50 A22=51', 'A23=52  VCC=14,49  GND=16,53'], C['cpu'], wrap=30)
    # barramento
    ax.add_patch(Rectangle((62, 176), 340, 5, fc=C['bus'], ec=C['bus']))
    ax.text(66, 178.5, 'BARRAMENTO DO 68000:  A1-A23  .  D0-D15  .  /AS  /UDS  /LDS  R/W  /DTACK  /RESET', fontsize=7.5, color='w', va='center', weight='bold')
    linha(ax, [(62, 178.5), (62, 178.5)])
    # linha liga CPU -> barramento
    ax.add_patch(Rectangle((58, 176), 6, 5, fc=C['bus'], ec=C['bus']))
    # fileira superior
    topo = [
        ('ROM (EPROM HI U8 + LO U7)', ['2 x 27C512 (128 KB)', '$F80000-$F9FFFF', 'HI = bytes pares (D8-D15)', 'LO = bytes impares (D0-D7)', '/CE /OE <- decodificador', 'A14,A13,pino 1 <- 74LS14 U26',
                                      '(A15,A14,A16 invertidos)', 'EPROMs -15 (150 ns)'], C['mem']),
        ('RAM 128 KB (2 adaptadores)', ['2 x KM681000BLP-5 em soquetes', 'U13 (D0-D7) e U14 (D8-D15)', '$000000-$01FFFF', '/CE <- U4 pino 11 (Y4)', '/WE <- U28 (3 baixo, 11 alto)',
                                        'A16 -> KM pino 31; KM pino 2=GND', 'sem bateria (volatil)', 'antes: 2 x DS1230Y 64 KB'], C['mem']),
        ('MC68681P  DUART', ['$FA0000-$FA001F (bytes impares)', 'cristal proprio 3,6864 MHz', 'canais A e B -> 1488/1489', '   -> conector J4', 'OP2 -> strobe do DS1232', 'IP3 = condicao de seguranca',
                             'IRQ -> IPL do 68000 (vetor $1F)', 'monitor: 57600 bps (38400 ok)'], C['io']),
        ('Intel 8254  (temporizador)', ['$020010-$020016', 'A1/A0 invertidos (ctrl em $020010)', '3 contadores de 16 bits', 'C0 modo1, C1 modo2, C2 modo0/1', 'pulso e duty do laser',
                                        'clock do 8254: medir [?]', 'nao usado no uso standalone'], C['io']),
        ('DAC8212 + AD584 + CD4051/OP07', ['DAC_A $02000A  (0..5000 mV)', 'DAC_B $02000C', 'referencia AD584', 'mux CD4051 + OP07:', 'medida analogica (potencia,', '   sensores)', 'AD7501 U38 <- bits 12-15 de $020020'], C['io']),
    ]
    x = 70
    for t, ln, cor in topo:
        caixa(ax, x, 205, 64, 52, t, ln, cor, wrap=34)
        for dx in (14, 50):
            linha(ax, [(x + dx, 205), (x + dx, 181)], C['bus'], 2.4); ponto(ax, x + dx, 181, C['bus'])
        x += 68
    # fileira inferior
    base = [
        ('Decodificador de enderecos', ['74LS138 U4: A=A17 (pino 1), B=A18 (pino 2)', ' Y4 (p.11) -> RAM  $00000-$1FFFF', ' Y5 (p.10) -> E/S 16 bits $20000-$3FFFF',
                                        ' Y6 [?] -> E/S 8 bits $40000-$5FFFF', ' Y7 (p.7)  -> $60000-$7FFFF sem /DTACK',
                                        'U19: A19-A23 (pinos 2-6) [?]', '74LS138 U6: sub-decodifica E/S ($0200xx)', 'Y3 (p.12) -> clock de $020020',
                                        'sem PAL/GAL (logica discreta)'], C['dec']),
        ('Saidas $020018', ['2 x 74LS273 (U39, U45)', 'escrita de 16 bits (so escrita)', 'push-pull TTL 0-4,3 V', 'bits 0-7  -> J1 (28,26,24,20,18,15,14,10)', 'bits 8-15 -> J2 (47,40,37,30,28,27,24,23)',
                            'medido com DSO-X 2002A', 'USO: SPI/SD + LCD + buzzer'], C['io']),
        ('Saidas $020020', ['2 x 74LS273 (U40 alto, U46 baixo)', 'clock: U6 Y3 -> U10 (74LS14)', 'bits 0-7: via 74LS06 (U41/U47),', ' coletor aberto, INVERTIDO', ' bit 7 -> J1-48 (U47 pino 8)', 'bits 8-11: ver folha 3 (U41)',
                           'bits 12-15 -> AD7501 U38', 'resto do roteamento a medir [?]'], C['io']),
        ('Entradas 16 bits', ['4 x 74LS240 (inversores)', 'pull-up 4,7 k; aterrar = bit 1', 'porta B $020028: U42 + U48', '   U48 recebe SW2 (bits 8-15)', 'porta A $020030: U44 + U37',
                              'leitura XOR $FF34 / $1BD3 (laser)', 'J1: B0..B6, A3 medidos (folha 3)'], C['io']),
        ('E/S 8 bits  $040000-$05FFFF', ['saidas $040180, $04018A', 'entradas $040194, $04019C', 'lido $FF se nada ligado', 'uso original: laser', '[?] pinos nos conectores',
                                        'nao medidos ainda'], C['io']),
    ]
    x = 70
    for t, ln, cor in base:
        caixa(ax, x, 106, 64, 62, t, ln, cor, wrap=34)
        for dx in (14, 50):
            linha(ax, [(x + dx, 176), (x + dx, 168)], C['bus'], 2.4); ponto(ax, x + dx, 176, C['bus'])
        x += 68
    # conectores
    conn = [(70, 'J1  IDC-50', 'saidas $020018 b0-b7, $020020 b7;\nentradas B0-B6, A3; GND 1,2,9,50'), (138, 'J2  IDC-50', 'saidas $020018 b8-b15'),
            (206, 'J4  IDC-20 (serial)', 'canais A/B: RX, TX, CTS, RTS, GND\n(ver folha 4 e DE-9)'), (274, 'TB1 / SW1 / SW2 / JP6', 'TB1: GND, +12 V, -12 V\nSW1 = RESET, SW2 = DIP 8 (U48)\nJP6 WATCHDOG INHIBIT: nao instalado')]
    for x, t, s in conn:
        ax.add_patch(FancyBboxPatch((x, 40), 64, 30, boxstyle='round,pad=0,rounding_size=1.5', fc=C['conn'], ec='#222', lw=1.4))
        ax.text(x + 2, 67, t, fontsize=8.5, weight='bold', va='top')
        yy = 61
        for l in s.split('\n'):
            ax.text(x + 2, yy, l, fontsize=6.6, va='top'); yy -= 3.6
    # setas dos latches para J1/J2 / entradas
    linha(ax, [(152, 106), (152, 88), (102, 88), (102, 70)], C['out'], 1.6, True)      # 273 $020018 -> J1
    linha(ax, [(152, 88), (170, 88), (170, 70)], C['out'], 1.6, True)                 # -> J2
    linha(ax, [(220, 106), (220, 82), (112, 82), (112, 70)], C['out2'], 1.6, True)    # $020020 -> J1-48
    linha(ax, [(288, 106), (288, 94), (92, 94), (92, 70)], C['inp'], 1.6)              # entradas <- J1
    ax.annotate('', xy=(288, 106), xytext=(288, 100), arrowprops=dict(arrowstyle='-|>', color=C['inp'], lw=1.6, mutation_scale=9))
    ax.text(154, 91, '$020018 -> J1 / J2', fontsize=6.5, color=C['out'])
    ax.text(222, 85, '$020020 b7 -> J1-48', fontsize=6.5, color=C['out2'])
    ax.text(160, 97, 'entradas B/A <- J1 / J2 (240)', fontsize=6.5, color=C['inp'])
    # DUART -> J4 por rede nomeada
    ax.text(207, 72.5, '<-- DUART (U36 1489 / U43 1488)', fontsize=6.5, color='#444')
    # clock / reset
    caixa(ax, 10, 40, 52, 82, 'Clock / Reset / Fonte', ['modulo oscilador 8 MHz', ' (XO-43B) -> CLK do 68000', 'DS1232: reset + watchdog',
         ' strobe = OP2 do 68681', ' JP6 (inibe): NAO instalado', 'SW1 = botao RESET', 'TB1: GND, +12 V, -12 V', '+5 V: entrada a confirmar [?]',
         'sem /BERR: endereco sem', ' /DTACK trava; o watchdog', ' reinicia a placa'], C['clk'], wrap=30)
    # periferico externo
    ax.add_patch(FancyBboxPatch((344, 40), 66, 60, boxstyle='round,pad=0,rounding_size=1.5', fc=C['ext'], ec='#222', lw=1.2, ls='--'))
    ax.text(346, 97, 'FORA DA PLACA (projeto)', fontsize=8, weight='bold', va='top')
    for i, l in enumerate(['RepRapDiscount Smart Controller:', ' LCD 20x4 (HD44780, 4 bits),', ' slot SD (SPI), buzzer, encoder', 'ligado a J1/J2 por placa de', ' interligacao -> EXP1/EXP2', '(folha 4)',
                           'Interposer CPLD EPM7128S no', ' soquete da CPU (futuro):', ' RAM 1 MB, TMS9118, LCD/SD', 'Fonte externa +5 V p/ o painel']):
        ax.text(346, 91.5 - i * 3.9, l, fontsize=5.9, va='top')
    # legenda
    ax.text(10, 30, 'Legenda:', fontsize=7.5, weight='bold')
    for i, (cor, t) in enumerate([(C['cpu'], 'CPU'), (C['mem'], 'memoria'), (C['io'], 'E/S'), (C['dec'], 'decodificacao'), (C['clk'], 'clock/reset'), (C['conn'], 'conectores')]):
        ax.add_patch(Rectangle((30 + i * 38, 28), 5, 4, fc=cor, ec='#222')); ax.text(36.5 + i * 38, 30, t, fontsize=6.8, va='center')
    ax.text(10, 22, 'Mapa (blocos de 128 KB; o decodificador usa so A17/A18 em baixo, tudo se repete a cada $80000 ate $F7FFFF):', fontsize=6.8)
    ax.text(10, 17.5, '$000000 RAM  |  $020000 E/S 16 bits  |  $040000 E/S 8 bits  |  $060000 SEM /DTACK (trava)  |  $F80000 ROM 128 KB  |  $FA0000 DUART  |  $FC0000 vazio  |  $FE0000 le $FF', fontsize=6.8)
    ax.text(10, 12.5, 'Esquema reconstruido de fotos, firmware e medicoes (multimetro/osciloscopio); nao ha esquematico original.', fontsize=6.8)
    return fig

# ----------------------------------------------------------------------------------------------- folha 2
def folha2():
    fig, ax = novo('Folha 2 - Decodificacao de enderecos e memoria', 2)
    # mapa de enderecos
    ax.text(10, 285, 'MAPA DE ENDERECOS (varredura 10/11/2026)', fontsize=8.5, weight='bold')
    blocos = [(0, 'RAM 128 KB (U13/U14)', C['mem'], '$000000-$01FFFF'), (1, 'E/S 16 bits (laser)', C['io'], '$020000-$03FFFF'), (2, 'E/S 8 bits', C['io'], '$040000-$05FFFF'),
              (3, 'SEM /DTACK -> trava', '#f8cbad', '$060000-$07FFFF')]
    y0 = 268
    for i, (k, t, cor, a) in enumerate(blocos):
        ax.add_patch(Rectangle((10, y0 - 16 * (i + 1)), 78, 15, fc=cor, ec='#222'))
        ax.text(12, y0 - 16 * i - 5, a, fontsize=7.5, family='DejaVu Sans Mono', weight='bold'); ax.text(12, y0 - 16 * i - 11, t, fontsize=7.5)
    ax.add_patch(Rectangle((10, y0 - 84), 78, 12, fc='#eee', ec='#222', ls='--'))
    ax.text(12, y0 - 79, '$080000-$F7FFFF: repete o bloco acima\na cada $80000 (A19-A23 ignorados)', fontsize=6.8, va='center')
    topo = [('ROM 128 KB (27C512)', C['mem'], '$F80000-$F9FFFF'), ('DUART 68681', C['io'], '$FA0000-$FBFFFF'), ('vazio: DTACK sem dispositivo', '#eee', '$FC0000-$FDFFFF'), ('le $FF', '#eee', '$FE0000-$FFFFFF')]
    for i, (t, cor, a) in enumerate(topo):
        yy = y0 - 100 - 13 * i
        ax.add_patch(Rectangle((10, yy), 78, 12, fc=cor, ec='#222'))
        ax.text(12, yy + 8, a, fontsize=7.5, family='DejaVu Sans Mono', weight='bold'); ax.text(12, yy + 3, t, fontsize=7)
    ax.text(10, y0 - 156, 'Detalhes de E/S ($02xxxx):\n$020000 entradas 16 bits   $02000A DAC_A   $02000C DAC_B\n$020010-$020016 8254\n$020018 saidas A (J1/J2)   $020020 saidas B\n$020028 entradas B   $020030 entradas A\nDUART: registradores em enderecos IMPARES (reg n = $FA0000+2n+1)', fontsize=6.8, va='top')
    # decodificador
    ax.text(100, 285, 'DECODIFICADOR (74LS138 U4)  [pinos a confirmar]', fontsize=8.5, weight='bold')
    ax.add_patch(Rectangle((126, 195), 44, 78, fc=C['dec'], ec='#222', lw=1.4))
    ax.text(128, 270, '74LS138  U4', fontsize=8.5, weight='bold', va='top')
    ent = [('A', 'A17 (CPU 45)', 1), ('B', 'A18 (CPU 46)', 2), ('C', 'Vcc [?]', 3), ('/G2A,/G2B,G1', 'A19-A23 via U19 [?]', 0)]
    ys = [255, 245, 235, 222]
    for (n, s, p), yy in zip(ent, ys):
        linha(ax, [(96, yy), (126, yy)], '#222', 1.2); ax.text(128, yy, f'{n}' + (f' (p.{p})' if p else ''), fontsize=6.8, va='center')
        ax.text(97, yy + 1.4, s, fontsize=6.4, ha='left')
    saidas = [('Y4 (p.11)', 'RAM /CE  ($00000-$1FFFF)', 262), ('Y5 (p.10)', 'E/S 16 bits ($20000-$3FFFF) -> U6', 248), ('Y6 (p.9) [?]', 'E/S 8 bits ($40000-$5FFFF)', 234), ('Y7 (p.7)', 'sem /DTACK ($60000-$7FFFF)', 220)]
    for s, t, yy in saidas:
        linha(ax, [(170, yy), (182, yy)], '#222', 1.2, True); ax.text(172, yy + 1.8, s, fontsize=6.6); ax.text(183, yy, t, fontsize=6.8, va='center')
    ax.text(104, 189, 'U6 (74LS138): sub-decodifica $0200xx: Y3 (p.12) -> clock dos latches\n$020020 (via 74LS14 U10 pinos 1 -> 2 -> 11 de U40/U46).\nLogica livre: U10 74LS14 (2-4 inversores), U41 74LS06 (2A), U35 74LS11, U34 74LS74.', fontsize=6.6, va='top')
    # ROM
    ax.text(100, 148, 'ROM: ligacao dos enderecos (explica a ordem embaralhada dos dumps)', fontsize=9, weight='bold')
    rows = [('CPU A15 (pino 43)', '74LS14 U26', 'EPROM pino 27 (A14)'), ('CPU A14 (pino 42)', '74LS14 U26', 'EPROM pino 26 (A13)'), ('CPU A16 (pino 44)', '74LS14 U26', 'EPROM pino 1  (A15 na 27C512)'),
            ('CPU A1..A13', 'direto', 'EPROM A0..A12'), ('EPROM HI U8', 'bytes PARES (D8-D15)', '27C512 em $F80000-$F9FFFF'), ('EPROM LO U7', 'bytes IMPARES (D0-D7)', 'idem')]
    for i, (a, b, c) in enumerate(rows):
        yy = 140 - i * 8
        ax.add_patch(Rectangle((100, yy - 6), 136, 7, fc='#fff', ec='#888'))
        ax.text(102, yy - 2.5, a, fontsize=7, va='center'); ax.text(140, yy - 2.5, '-> ' + b + ' ->', fontsize=7, va='center'); ax.text(188, yy - 2.5, c, fontsize=7, va='center')
    ax.text(100, 90, 'Os 3 sinais invertidos trocam os 4 blocos de 16 KB: no arquivo, endereco_ROM = $F80000 + (offset XOR $C000).\nCom a 27C512, a imagem de 128 KB e gerada pela ferramenta mkrom21.py; fallback 27C256 nao e mais usado.', fontsize=6.8, va='top')
    # RAM
    ax.text(250, 285, 'RAM 128 KB: adaptador 28 -> 32 pinos (x2)', fontsize=9, weight='bold')
    pares = [('soquete 1-14', 'KM 3-16', 'A14,A12,A7..A0 (CPU A15,A13,A8..A1), D0/D8..D2/D10, GND'), ('soquete 15-19', 'KM 17-21', 'D3..D7 (ou D11..D15)'), ('soquete 20 (/CE)', 'KM 22', '/CS1 <- U4 pino 11 (Y4)'),
             ('soquete 21-26', 'KM 23-28', 'A10, /OE (22 -> 24), A11, A9, A8, A13'), ('soquete 27 (/WE)', 'KM 29', 'U28 pino 3 (byte baixo) / 11 (alto)'), ('soquete 28 (Vcc)', 'KM 32', '+5 V + 100 nF para o pino 16'),
             ('FIO NOVO: CPU pino 44 (A16)', 'KM 31 (A15)', 'duas KM'), ('FIO NOVO: GND', 'KM 2 (A16)', 'sempre 0: Y4 so cobre 128 KB'), ('FIO NOVO: Vcc', 'KM 30 (CS2)', 'ativo em 1'), ('KM pino 1', 'NC', 'solto')]
    for i, (a, b, c) in enumerate(pares):
        yy = 277 - i * 8
        cor = '#fff2cc' if a.startswith('FIO') else '#fff'
        ax.add_patch(Rectangle((250, yy - 6), 160, 7, fc=cor, ec='#888'))
        ax.text(252, yy - 2.5, a, fontsize=6.8, va='center'); ax.text(296, yy - 2.5, '-> ' + b, fontsize=6.8, va='center'); ax.text(322, yy - 2.5, c, fontsize=6.2, va='center')
    ax.text(250, 190, 'Resultado: cada KM usa metade (64K x 8); juntas formam 64K palavras = 128 KB em $000000-$01FFFF.\nDados: o chip em U13 faz D0-D7 (impares), o de U14 faz D8-D15 (pares). Se os bytes vierem trocados,\ninverta os chips. A DS1230Y tinha bateria; a KM681000 e volatil (dumps das NVRAMs originais guardados).\nTestes do monitor v2.1: comandos I (RAM detectada), Q (mapa), Z (teste de RAM) e P/D em $13010 (nao espelha).', fontsize=6.8, va='top')
    # DTACK
    ax.text(250, 150, '/DTACK e RESET', fontsize=9, weight='bold')
    ax.text(250, 144, '- /DTACK: gerado por logica discreta (U35 74LS11, U1, U33 [?]); cada janela de E/S gera o proprio.\n- $060000-$07FFFF nao tem /DTACK -> a CPU espera para sempre ate o DS1232 reiniciar.\n- /BERR esta em Vcc: nao existe erro de barramento por hardware (o monitor trata os vetores 2 e 3).\n- Reset: DS1232 (~150 ms) + SW1; watchdog alimentado por OP2 do 68681; JP6 inibe (nao instalado).\n- A CPU e P10 (10 MHz) com modulo de 8 MHz; overclock a 12 MHz foi considerado (EPROMs -15 = 150 ns;\n  podem ser trocadas por flash de 100/120 ns).\n- Interposer (futuro): CPLD EPM7128S bloqueia /AS /UDS /LDS para a placa em janelas novas\n  ($100000 SRAM 1 MB, $200000 registradores LCD/SD, $300000 TMS9118).', fontsize=6.8, va='top')
    return fig

# ----------------------------------------------------------------------------------------------- folha 3
def folha3():
    fig, ax = novo('Folha 3 - Portas de E/S ($020018, $020020, $020028, $020030)', 3)
    def tabela(x, y, titulo, cab, linhas, larg, cor_cab, cores=None, fs=6.8):
        ax.text(x, y + 4, titulo, fontsize=8.5, weight='bold')
        xx = x
        for w, c in zip(larg, cab):
            ax.add_patch(Rectangle((xx, y - 5), w, 5.5, fc=cor_cab, ec='#222')); ax.text(xx + 1, y - 2.2, c, fontsize=fs, weight='bold', va='center'); xx += w
        for i, ln in enumerate(linhas):
            xx = x; yy = y - 5 - (i + 1) * 5.5
            fc = (cores[i] if cores else '#fff')
            for w, c in zip(larg, ln):
                ax.add_patch(Rectangle((xx, yy + 0.5), w, 5.5, fc=fc, ec='#999')); ax.text(xx + 1, yy + 3.2, str(c), fontsize=fs, va='center'); xx += w
    saidas = [(0, 'J1-28', '108 kHz', 'SCK'), (1, 'J1-26', '54,1 kHz', 'MOSI'), (2, 'J1-24', '27,06 kHz', 'CS do SD'), (3, 'J1-20', '13,51 kHz', 'LCD_E'), (4, 'J1-18', '6,757 kHz', 'LCD_RS'),
              (5, 'J1-15', '3,378 kHz', 'LCD_D4'), (6, 'J1-14', '1,689 kHz', 'LCD_D5'), (7, 'J1-10', '845 Hz', 'LCD_D6'), (8, 'J2-47', '422 Hz', 'LCD_D7'), (9, 'J2-40', '211 Hz', 'BUZZER'),
              (10, 'J2-37', '105 Hz', 'livre'), (11, 'J2-30', '52 Hz', 'livre'), (12, 'J2-28', '26 Hz', 'livre'), (13, 'J2-27', '13 Hz', 'livre'), (14, 'J2-24', '6 Hz', 'livre'), (15, 'J2-23', '~3 Hz', 'livre')]
    tabela(10, 275, 'SAIDAS $020018  (2 x 74LS273 U39/U45, escrita de 16 bits)', ['bit', 'pino', 'freq. medida', 'uso atual (RepRap)'],
           [(b, p, f, u) for b, p, f, u in saidas], [10, 16, 26, 36], '#cfe2f7', ['#eaf2fc' if u != 'livre' else '#fff' for *_, u in saidas])
    ax.text(10, 176, 'Medido com o DSO-X 2002A rodando um contador (bit 0 = 108 kHz, cada bit seguinte na\nmetade): TTL 0 a ~4,3 V, duty 50%, sem drivers (os drivers de potencia ficavam na\noutra placa). Registrador so de ESCRITA: o software mantem uma copia-sombra (LSH, $2F40).', fontsize=6.6, va='top')
    # $020020
    s20 = [(0, '74LS06 U41 p1 -> p2', 'a medir'), (1, 'U41 p13 -> p12', 'a medir'), (2, 'U47 p1 -> p2', 'a medir'), (3, 'U47 p13 -> p12', 'a medir'), (4, 'U47 p3 -> p4', 'a medir'),
           (5, 'U47 p11 -> p10', 'a medir'), (6, 'U47 p5 -> p6', 'a medir'), (7, 'U47 p9 -> p8', 'J1-48'), (8, 'U39 p8 (D3 de um 273)', 'interno'), (9, 'U41 p11 -> p10', 'a medir'),
           (10, 'U41 p5 -> p6', 'a medir'), (11, 'U41 p9 -> p8', 'a medir'), (12, 'AD7501 U38 p16', 'interno'), (13, 'AD7501 U38 p1', 'interno'), (14, 'AD7501 U38 p4', 'interno'), (15, 'AD7501 U38 p3', 'interno')]
    tabela(140, 275, 'SAIDAS $020020  (U46 bits 0-7 via 74LS06 invertido; U40 bits 8-15)', ['bit', 'caminho medido', 'conector'], s20, [10, 56, 24], '#fbe5cc',
           ['#fdf1e3' if c == 'J1-48' else '#fff' for *_, c in s20])
    ax.text(140, 176, 'Bits 0-7: coletor aberto e INVERTIDOS (74LS06); precisam de pull-up externo.\nBits 8-15: push-pull direto do 273 (U40). Pinos do 273 (bit -> Q): 0:9 1:12 2:6 3:15\n4:5 5:16 6:2 7:19 (igual nos dois CIs). Clock: U6 Y3 (p.12) -> U10 74LS14 (p.1 -> p.2)\n-> p.11 de U40 e U46. Nao escrever nestes bits sem saber o destino.', fontsize=6.6, va='top')
    # entradas
    ent = [('B0', '$020028', 'J1-7', 'MISO do SD'), ('B1', '$020028', 'J1-35', 'BTN_EN2'), ('B2', '$020028', 'J1-33', 'BTN_EN1'), ('B3', '$020028', 'J1-31', 'BTN_ENC'), ('B4', '$020028', 'J1-27', 'SD_DETECT (opc.)'),
           ('B5', '$020028', 'J1-25', 'livre'), ('B6', '$020028', 'J1-23', 'livre'), ('B7', '$020028', 'J1-36 [?]', 'livre'), ('A3', '$020030', 'J1-4', 'livre'), ('J1-29', '-', 'sem resposta', '-')]
    tabela(272, 275, 'ENTRADAS (74LS240: aterrar o pino = bit 1)', ['bit', 'porta', 'pino', 'uso'], ent, [14, 20, 42, 36], '#d9f0df', ['#eef8f1' if u not in ('livre', '-') else '#fff' for *_, u in ent])
    ax.text(272, 211, 'Medido em 12/11/2026 com o programa entradas_bip e resistor de 330 ohms ao GND.\n74LS240 invertem; pull-up de 4,7 k. Porta B = U42 (+ U48, que leva o DIP SW2 nos\nbits 8-15). Porta A = U44 + U37. O software le $020028 (B) e $020030 (A) em 16 bits.\nOutros bits de A e B: pinos ainda nao localizados em J1/J2 (muitos pinos estao a Vcc).', fontsize=6.6, va='top')
    # diagrama de caminho de dados
    ax.text(10, 150, 'CAMINHO DE DADOS (por porta)', fontsize=9, weight='bold')
    def seta(x1, x2, y, t, cor='#222'):
        linha(ax, [(x1, y), (x2, y)], cor, 1.6, True); ax.text((x1 + x2) / 2, y + 1.8, t, fontsize=6.5, ha='center', color=cor)
    ys = [136, 116, 96]
    # saida 020018
    for y, nm in zip(ys, ['$020018', '$020020', 'entradas']): ax.text(10, y + 6, nm, fontsize=7.5, weight='bold')
    caixa(ax, 28, 128, 28, 14, 'D0-D15 (CPU)', [], '#d9e8fb', tfs=7); seta(56, 76, 135, 'MOVE.W', C['out'])
    caixa(ax, 76, 126, 40, 18, '2 x 74LS273', ['U39 / U45 (16 bits)', 'clock = /WR + Y($020018)'], C['io'], fs=6.4, tfs=7.5); seta(116, 146, 135, 'push-pull', C['out'])
    caixa(ax, 146, 128, 24, 14, 'J1 / J2', [], C['conn'], tfs=7.5)
    caixa(ax, 28, 108, 28, 14, 'D0-D15 (CPU)', [], '#d9e8fb', tfs=7); seta(56, 76, 115, 'MOVE.W', C['out2'])
    caixa(ax, 76, 106, 40, 18, '2 x 74LS273', ['U46 (bits 0-7) U40 (8-15)', 'clock: U6 Y3 -> U10'], C['io'], fs=6.4, tfs=7.5); seta(116, 134, 115, '7406 inv.', C['out2'])
    caixa(ax, 134, 108, 20, 14, '74LS06', ['U41/U47'], C['io'], fs=6.4, tfs=7.5); seta(154, 170, 115, '', C['out2'])
    caixa(ax, 170, 108, 24, 14, 'J1-48 / AD7501', [], C['conn'], fs=6, tfs=6.6)
    caixa(ax, 28, 88, 28, 14, 'D0-D15 (CPU)', [], '#d9e8fb', tfs=7)
    linha(ax, [(76, 95), (56, 95)], C['inp'], 1.6, True); ax.text(66, 97, 'MOVE.W', fontsize=6.5, ha='center', color=C['inp'])
    caixa(ax, 76, 86, 40, 18, '4 x 74LS240', ['U42+U48 ($020028)', 'U44+U37 ($020030)'], C['io'], fs=6.4, tfs=7.5)
    linha(ax, [(146, 95), (116, 95)], C['inp'], 1.6, True); ax.text(130, 97, 'inversor', fontsize=6.5, ha='center', color=C['inp'])
    caixa(ax, 146, 88, 24, 14, 'J1 / J2 / SW2', [], C['conn'], fs=6, tfs=7.5)
    # ROM services
    ax.text(214, 150, 'SERVICOS DA ROM v2.1 (tabela de saltos; JSR a partir de programas)', fontsize=9, weight='bold')
    serv = [('$F80800', 'PUTC', 'escreve o caractere em D0'), ('$F80806', 'GETC', 'espera uma tecla; retorna em D0'), ('$F8080C', 'PUTS', 'imprime texto terminado em 0 (A1)'),
            ('$F80812', 'HEXB', 'imprime D0.B em hexa'), ('$F80818', 'HEXW', 'imprime D0.W em hexa'), ('$F8081E', 'HEXL', 'imprime D0.L em hexa'), ('$F80824', 'CRLF', 'nova linha'),
            ('$F8082A', 'STROBE', 'pulsa o watchdog (OP2)'), ('$F80830', 'GETHEX', 'le numero hexa da linha (A1) -> D0'), ('$F80836', 'GETLINE', 'le uma linha para o buffer $0500')]
    tabela(214, 144, '', ['endereco', 'nome', 'funcao'], serv, [22, 20, 78], '#e7e6e6', fs=6.6)
    ax.text(214, 78, 'Programas de usuario: carregar com L (S-record), executar com G 2000; RAM livre de $2000 ate RAMEND ($1FFFF com 128 KB).\nPeriferico incluido na ROM: comando @ (G F8F000) = SD (SPI) + buzzer + LCD 20x4 da RepRapDiscount.', fontsize=6.8, va='top')
    return fig

# ----------------------------------------------------------------------------------------------- folha 4
def folha4():
    fig, ax = novo('Folha 4 - Conectores J1, J2, J4 e ligacao da RepRapDiscount Smart Controller', 4)
    cor = {'o1': ('#cfe2f7', C['out']), 'o2': ('#fbe5cc', C['out2']), 'in': ('#d9f0df', C['inp']), 'gnd': ('#cccccc', '#444'), 'nc': ('#ffffff', '#888'), 'ruido': ('#f7f7a8', '#a60')}
    J1 = {28: ('o1', 'b0 SCK'), 26: ('o1', 'b1 MOSI'), 24: ('o1', 'b2 CS-SD'), 20: ('o1', 'b3 LCD_E'), 18: ('o1', 'b4 LCD_RS'), 15: ('o1', 'b5 LCD_D4'), 14: ('o1', 'b6 LCD_D5'), 10: ('o1', 'b7 LCD_D6'),
          48: ('o2', '$020020 b7 (OC inv.)'), 7: ('in', 'B0 MISO'), 35: ('in', 'B1 BTN_EN2'), 33: ('in', 'B2 BTN_EN1'), 31: ('in', 'B3 BTN_ENC'), 27: ('in', 'B4 SD_DET'), 25: ('in', 'B5'), 23: ('in', 'B6'), 36: ('in', 'B7 [?]'), 4: ('in', 'A3'),
          1: ('gnd', 'GND'), 2: ('gnd', 'GND'), 9: ('gnd', 'GND (RRD)'), 50: ('gnd', 'GND'), 13: ('ruido', 'ruido (nc)'), 17: ('ruido', 'ruido (nc)'), 29: ('nc', 'sem resposta')}
    J2 = {47: ('o1', 'b8 LCD_D7'), 40: ('o1', 'b9 BUZZER'), 37: ('o1', 'b10'), 30: ('o1', 'b11'), 28: ('o1', 'b12'), 27: ('o1', 'b13'), 24: ('o1', 'b14'), 23: ('o1', 'b15')}
    def conector(x, nome, mapa):
        ax.text(x, 285, nome, fontsize=9.5, weight='bold')
        ax.text(x, 280.5, 'visto de cima do conector: pinos impares a esquerda, pares a direita', fontsize=6.2, color='#555')
        for r in range(25):
            yy = 275 - r * 8.5
            for lado, p in ((0, 2 * r + 1), (1, 2 * r + 2)):
                k, t = mapa.get(p, ('nc', ''))
                fc, ec = cor[k]
                xx = x + lado * 57
                ax.add_patch(Rectangle((xx, yy - 6), 7, 6.2, fc=fc, ec='#222')); ax.text(xx + 3.5, yy - 2.9, str(p), fontsize=6, ha='center', va='center', weight='bold')
                if lado == 0: ax.text(xx - 1, yy - 2.9, t, fontsize=6, ha='right', va='center', color=ec)
                else: ax.text(xx + 8, yy - 2.9, t, fontsize=6, ha='left', va='center', color=ec)
    conector(70, 'J1  (IDC 50 pinos)', J1)
    conector(235, 'J2  (IDC 50 pinos)', J2)
    # legenda
    ax.text(352, 285, 'Legenda', fontsize=9, weight='bold')
    for i, (k, t) in enumerate([('o1', 'saida $020018 (push-pull)'), ('o2', 'saida $020020 (OC, invertida)'), ('in', 'entrada (74LS240)'), ('gnd', 'GND'), ('ruido', 'so ruido acoplado'), ('nc', 'nao medido / sem funcao')]):
        ax.add_patch(Rectangle((352, 277 - i * 7), 7, 5, fc=cor[k][0], ec='#222')); ax.text(361, 279.5 - i * 7, t, fontsize=6.5, va='center')
    ax.text(352, 241, 'Os demais pinos de J1/J2 nao responderam\nnos testes; muitos estao a Vcc (nao\nidentificados). J1 nao tem Vcc util:\no +5 V do painel vem de fonte externa.', fontsize=6.4, va='top')
    # J4
    ax.text(352, 218, 'J4  (IDC 20, serial)', fontsize=9, weight='bold')
    j4 = [('1,2,12,13', 'GND', '5'), ('3', 'RX canal A (U36-1)', '3 (A)'), ('4', 'RX canal B (U36-13)', '3 (B)'), ('5', 'TX canal A (U43-11)', '2 (A)'), ('6', 'TX canal B (U43-6)', '2 (B)'),
          ('7', 'CTS A (U36-4)', '7 (A)'), ('8', 'CTS B (U36-10)', '7 (B)'), ('9', 'RTS B (U43-3)', '8 (B)'), ('11', 'RTS A (U43-8)', '8 (A)'), ('15', 'ligado ao 11', '-'), ('10,14,16-20', 'sem conexao', '-')]
    ax.text(352, 212.5, 'pino        sinal / CI-pino         DE-9 femea', fontsize=6, color='#555')
    for i, (p, s, d) in enumerate(j4):
        yy = 208 - i * 5.2
        ax.add_patch(Rectangle((352, yy - 4.5), 62, 4.8, fc='#fff', ec='#aaa')); ax.text(353, yy - 2, p, fontsize=6, va='center'); ax.text(366, yy - 2, s, fontsize=6, va='center'); ax.text(405, yy - 2, d, fontsize=6, va='center')
    ax.text(352, 148, 'Drivers 1488 (TX) / 1489 (RX), +/-12 V. Serial do\nmonitor: 57600 bps, 8N1 (CP/M tenta passar a\n57600 sozinho; 115200 nao funciona com o cristal\nde 3,6864 MHz; 38400 funciona).', fontsize=6.3, va='top')
    # RepRap
    ax.text(352, 128, 'RepRapDiscount Smart Controller', fontsize=8.5, weight='bold')
    rr = [('EXP1-1 BEEPER', 'J2-40  (b9)'), ('EXP1-2 BTN_ENC', 'J1-31  (B3)'), ('EXP1-3 LCD_EN', 'J1-20  (b3)'), ('EXP1-4 LCD_RS', 'J1-18  (b4)'), ('EXP1-5 LCD_D4', 'J1-15  (b5)'), ('EXP1-6 LCD_D5', 'J1-14  (b6)'),
          ('EXP1-7 LCD_D6', 'J1-10  (b7)'), ('EXP1-8 LCD_D7', 'J2-47  (b8)'), ('EXP2-1 MISO', 'J1-7   (B0)'), ('EXP2-2 SCK', 'J1-28  (b0)'), ('EXP2-3 BTN_EN1', 'J1-33  (B2)'), ('EXP2-4 SD_CS', 'J1-24  (b2)'),
          ('EXP2-5 BTN_EN2', 'J1-35  (B1)'), ('EXP2-6 MOSI', 'J1-26  (b1)'), ('EXP2-7 SD_DET', 'J1-27  (B4)'), ('EXP1-9/EXP2-9 GND', 'J1-9 e GND ext.'), ('EXP1-10 +5 V', 'fonte externa'), ('KILL, EXP2-10', 'sem ligacao')]
    for i, (a, b) in enumerate(rr):
        yy = 123 - i * 4.7
        ax.add_patch(Rectangle((352, yy - 4.0), 62, 4.5, fc='#fff' if i % 2 else '#f3f8ff', ec='#ccc')); ax.text(353, yy - 1.8, a, fontsize=5.9, va='center'); ax.text(392, yy - 1.8, b, fontsize=5.9, va='center')
    ax.text(10, 50, 'Ordem dos pinos EXP1/EXP2 de memoria (padrao RAMPS): confirmar na serigrafia da placa antes de ligar. J1-23 (B6), J1-25 (B5), J1-36 (B7) [?] e J1-4 (A3) ficam livres.\nO buzzer e passivo (toque por software, ~440 Hz de teste); o encoder e dispensavel. Programa em $F8F000 (comando @ do monitor).', fontsize=6.6, va='top')
    return fig

if __name__ == '__main__':
    figs = [folha1(), folha2(), folha3(), folha4()]
    with PdfPages(f'{OUT}/Paragon50_Esquema_{VERSAO}.pdf') as pdf:
        for i, f in enumerate(figs, 1):
            pdf.savefig(f)
            f.savefig(f'{OUT}/Paragon50_Esquema_{VERSAO}_folha{i}.png', dpi=110)
    print('ok')
