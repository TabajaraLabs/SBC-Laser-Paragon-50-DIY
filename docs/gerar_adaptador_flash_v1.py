# -*- coding: utf-8 -*-
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, PageBreak

n27 = {1:'A15',2:'A12',3:'A7',4:'A6',5:'A5',6:'A4',7:'A3',8:'A2',9:'A1',10:'A0',11:'D0',12:'D1',13:'D2',14:'GND',
       15:'D3',16:'D4',17:'D5',18:'D6',19:'D7',20:'/CE',21:'A10',22:'/OE',23:'A11',24:'A9',25:'A8',26:'A13',27:'A14',28:'VCC'}
nfl = {1:'A18',2:'A16',3:'A15',4:'A12',5:'A7',6:'A6',7:'A5',8:'A4',9:'A3',10:'A2',11:'A1',12:'A0',13:'DQ0',14:'DQ1',15:'DQ2',16:'VSS',
       17:'DQ3',18:'DQ4',19:'DQ5',20:'DQ6',21:'DQ7',22:'CE#',23:'A10',24:'OE#',25:'A11',26:'A9',27:'A8',28:'A13',29:'A14',30:'A17',31:'WE#',32:'VCC'}
YT = 31.0
def ychip(p): return YT-(p-1) if p <= 16 else YT-(32-p)
def xchip(p): return 0.0 if p <= 16 else 6.0
fig, ax = plt.subplots(figsize=(10, 12.2)); ax.set_xlim(-11, 15); ax.set_ylim(-9.5, 34.5); ax.axis('off')
ax.add_patch(Rectangle((-0.8, YT-15.6), 7.6, 16.6, fc='#fdf6d8', ec='#c98a00', lw=1.6, zorder=0))
ax.add_patch(Rectangle((-0.45, YT-14.5), 6.9, 13.9, fc='none', ec='#1f5fbf', lw=1.2, ls='--', zorder=1))
ax.text(3, YT+2.0, 'Am29F040B  DIP-32 (laranja)  sobre  soquete da ROM DIP-28 (azul tracejado)', ha='center', fontsize=10, weight='bold', color='#444444')
ax.text(3, YT+1.0, 'vista de cima, entalhe (pinos 1 e 17) para cima. O pino 1 do soquete cai sob o pino 3 da flash.', ha='center', fontsize=8, color='#666666')
for p in range(1, 33):
    x, y = xchip(p), ychip(p)
    left = p <= 16
    over = p in (1, 2, 31, 32); lift = (p == 30)
    c = '#cc0000' if lift else ('#7a3db8' if over else '#222222')
    ax.add_patch(Rectangle((x-0.3, y-0.3), 0.6, 0.6, fc='white' if lift else ('#e6d6f5' if over else '#cfe0ff'), ec=c, lw=1.4, zorder=3))
    if lift:
        ax.plot([x-0.38, x+0.38], [y-0.38, y+0.38], c, lw=2, zorder=4); ax.plot([x-0.38, x+0.38], [y+0.38, y-0.38], c, lw=2, zorder=4)
    s = p-2
    if over: lab = f'{nfl[p]}  (chip {p}, fora do soquete)'
    elif lift: lab = f'{nfl[p]}  (chip {p})  LEVANTAR a perna'
    else: lab = f'{nfl[p]}  (chip {p} = soq.{s})'
    if left: ax.text(x-0.8, y, lab, ha='right', va='center', fontsize=7.6, color=c, weight='bold' if (over or lift) else 'normal')
    else: ax.text(x+0.8, y, lab, ha='left', va='center', fontsize=7.6, color=c, weight='bold' if (over or lift) else 'normal')
for n in range(1, 29):
    p = n+2; x, y = xchip(p), ychip(p)
    if p == 30: continue
    if p <= 16: ax.text(x+0.55, y, str(n), ha='left', va='center', fontsize=6, color='#1f5fbf')
    else: ax.text(x-0.55, y, str(n), ha='right', va='center', fontsize=6, color='#1f5fbf')
# anel do pad do soquete 28 (sob a perna levantada)
ax.add_patch(plt.Circle((6, ychip(30)), 0.5, fc='none', ec='#1f5fbf', lw=1.6, zorder=2))
ax.text(5.35, ychip(30)-0.55, 'soq.28 (VCC)', ha='right', va='top', fontsize=6.5, color='#1f5fbf')
Rd = '#cc0000'; Kk = '#111111'
def tag(x, y, t, c): ax.text(x, y, t, ha='center', va='center', fontsize=8, color='white', weight='bold', bbox=dict(boxstyle='circle,pad=0.25', fc=c, ec=c), zorder=8)
# FIO 1: chip 32 -> pad soq.28
ax.plot([6, 4.9, 4.9, 5.55], [ychip(32), ychip(32), ychip(30), ychip(30)], Rd, lw=2.2, zorder=5); tag(4.9, ychip(31), '1', Rd)
# FIO 2: chip 31 -> chip 32
ax.plot([6, 5.45, 5.45, 6], [ychip(31), ychip(31), ychip(32), ychip(32)], Rd, lw=1.4, zorder=5); tag(5.45, ychip(31)+0.5, '2', '#e06060')
# FIO 3: chip 1 e 2 -> GND (chip 16), por dentro
ax.plot([0, 3, 3, 0.3], [ychip(2), ychip(2), ychip(16), ychip(16)], Kk, lw=1.8, zorder=5)
ax.plot([0, -0.62, -0.62, 0], [ychip(1), ychip(1), ychip(2), ychip(2)], Kk, lw=1.8, zorder=5); tag(3, ychip(10), '3', Kk)
# FIO 4: chip 30 (perna levantada) -> fio 3
ax.plot([6, 3], [ychip(30), ychip(30)], Kk, lw=1.4, zorder=4, ls=(0, (4, 2))); ax.plot([3], [ychip(30)], 'o', color=Kk, ms=4, zorder=6); tag(4.5, ychip(30)+0.55, '4', Kk)
# legenda
LY = YT-18.0
leg = [('1', Rd, 'FIO 1  vermelho: chip 32 (VCC da flash) -> pino 28 do soquete (VCC). Mais um ceramico de 100 nF entre chip 32 e chip 16.'),
       ('2', '#e06060', 'FIO 2  vermelho fino: chip 31 (WE#) -> chip 32 (+5 V). So no passo 1; no passo 2 sai daqui e vai para a saida WE# do circuito de escrita.'),
       ('3', Kk, 'FIO 3  preto: chip 1 e chip 2 (A18, A16) -> chip 16 (GND). Passo 3: sai do GND e vai ao registrador de banco.'),
       ('4', Kk, 'FIO 4  preto tracejado: perna LEVANTADA do chip 30 (A17) -> FIO 3 (GND). Passo 3: vai ao registrador de banco.')]
for i, (t, c, txt) in enumerate(leg):
    y = LY-i*2.6; tag(-10.0, y, t, c); ax.text(-9.1, y, txt, ha='left', va='center', fontsize=8)
ax.text(-10.3, LY-4*2.6-0.4, 'Perna do chip 30: dobrar para fora SEM encostar no soquete (o soquete 28 e o VCC da placa).', ha='left', va='center', fontsize=8.4, color='#cc0000', weight='bold')
fig.savefig('adaptador_flash_sobreposto_v1.png', dpi=170, bbox_inches='tight'); plt.close(fig)

ss = getSampleStyleSheet()
H = ParagraphStyle('h', parent=ss['Title'], fontSize=15, spaceAfter=2)
H2 = ParagraphStyle('h2', parent=ss['Heading2'], fontSize=11, spaceBefore=7, spaceAfter=3)
P = ParagraphStyle('p', parent=ss['BodyText'], fontSize=8.8, leading=11.4)
C = ParagraphStyle('c', parent=P, fontSize=8.3, leading=10.2)
W_ = ParagraphStyle('w', parent=P, backColor=colors.HexColor('#fff1d6'), borderPadding=4, borderColor=colors.HexColor('#d99a2b'), borderWidth=0.6, spaceBefore=4, spaceAfter=4)
def tbl(rows, w):
    data = [[Paragraph(str(c), C) for c in r] for r in rows]
    t = Table(data, colWidths=[x*mm for x in w], repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dbe4f0')), ('GRID', (0,0), (-1,-1), 0.4, colors.grey), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    return t
doc = SimpleDocTemplate('Paragon50_Adaptador_Flash_Am29F040B_Pinagem_v1.pdf', pagesize=A4, leftMargin=12*mm, rightMargin=12*mm, topMargin=10*mm, bottomMargin=10*mm, title='PARAGON 50 - adaptador Am29F040B sobre soquete 28 pinos (v1)')
from PIL import Image as PI
_w,_h = PI.open('adaptador_flash_sobreposto_v1.png').size
IMG = Image('adaptador_flash_sobreposto_v1.png', width=186*mm, height=186*mm*_h/_w)
S = [Paragraph('PARAGON 50 &ndash; adaptador da Am29F040B (DIP-32 sobre o soquete DIP-28)', H),
Paragraph('Tabajara Labs &middot; v1 &middot; 13/11/2026. A flash de 32 pinos é encaixada sobre o soquete de 28 pinos <b>deslocada de dois furos</b>: o pino 3 da flash fica sobre o pino 1 do soquete. Assim, <b>os pinos 3 a 29 da flash coincidem com os pinos 1 a 27 do soquete e têm exatamente a mesma função</b> (conferido um a um na tabela da página 2). Só sobram quatro pinos de fora (1, 2, 31 e 32) e um pino que cai no lugar errado (o 30).', P),
IMG]
S += [PageBreak(), Paragraph('O que fazer, pino por pino', H2),
tbl([['Pino da flash', 'Função', 'Cai sobre', 'O que fazer'],
['3 a 15, 17 a 29', 'A15, A12...A0, DQ0 a DQ2, DQ3 a DQ7, CE#, A10, OE#, A11, A9, A8, A13, A14', 'soquete 1 a 13 e 15 a 27 (mesma função)', '<b>Nada.</b> Ligam direto ao soquete.'],
['16', 'VSS (GND)', 'soquete 14 (GND)', 'Nada. É o GND da flash.'],
['<font color="#cc0000"><b>30</b></font>', 'A17 (bit de banco)', 'soquete 28 (<b>VCC</b>)', '<b>LEVANTAR</b> a perna (dobrar para fora, sem encostar no soquete). Se encostar no VCC do soquete, A17 vai a +5 V. Liga-se depois por fio ao GND (FIO 4).'],
['32', 'VCC da flash', 'fora do soquete (acima do pino 28)', '<b>FIO 1:</b> ligar ao pino 28 do soquete (VCC).'],
['31', 'WE# (habilita escrita)', 'fora do soquete', '<b>FIO 2:</b> ligar ao pino 32 (+5 V). Passo 1: a flash fica só de leitura.'],
['1 e 2', 'A18 e A16 (bits de banco)', 'fora do soquete', '<b>FIO 3:</b> ligar os dois ao GND (pino 16 da flash).'],
['30 (perna levantada)', 'A17', 'ar', '<b>FIO 4:</b> ligar ao pino 2 da flash (que já vai ao GND).']], [28, 48, 38, 74]),
Paragraph('Fios, na ordem de soldar', H2),
tbl([['Fio', 'De', 'Para', 'Cor sugerida', 'Passo 2 (escrita): o que muda'],
['1', 'flash 32', 'soquete 28 (VCC)', 'vermelho', 'nada'],
['2', 'flash 31 (WE#)', 'flash 32 (+5 V)', 'vermelho fino', '<b>retirar</b> e ligar à saída WE# do circuito de escrita (HI ou LO)'],
['3', 'flash 1 e 2', 'flash 16 (GND)', 'preto', 'passo 3: A18 e A16 vêm do registrador de banco (retirar do GND)'],
['4', 'flash 30 (perna levantada)', 'flash 2 (GND)', 'preto fino', 'passo 3: A17 vem do registrador de banco']], [10, 36, 40, 26, 74]),
Paragraph('Capacitor: um ceramico de 100 nF entre o pino 32 e o pino 16 da flash, pelo caminho mais curto (por cima do chip). Faça <b>dois adaptadores iguais</b>, um para a ROM HI e outro para a ROM LO.', P),
Paragraph('Conferência com o multímetro, sem a flash ou com ela fora do soquete', H2),
Paragraph('1. Continuidade soquete 28 (VCC) a flash 32; soquete 14 (GND) a flash 16, 1 e 2; flash 31 ao +5 V (flash 32).<br/>2. <b>Sem continuidade</b> entre a perna levantada do pino 30 e o soquete 28.<br/>3. Sem curto entre VCC e GND em nenhum ponto (com o adaptador fora da placa).<br/>4. Só então gravar (as imagens da v2.3, oito cópias) e instalar. Pino 1 do soquete do mesmo lado do entalhe da ROM antiga.', P),
Paragraph('Os fios 3 e 4 poderão ser aproveitados no passo 3 (troca de banco): basta retirá-los do GND e ligar os bits A16, A17 e A18 ao registrador.', C)]
doc.build(S)
