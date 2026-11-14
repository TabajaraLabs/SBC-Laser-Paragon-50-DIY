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
# FIO 1: chip 32 -> pad soq.28 (por dentro)
ax.plot([6, 4.9, 4.9, 6], [ychip(32), ychip(32), ychip(30)-0.62, ychip(30)-0.62], Rd, lw=2.2, zorder=5); tag(4.9, ychip(31), '1', Rd)
G = '#0a6bd0'
def stub(p, xe, t, col=G):
    x, y = xchip(p), ychip(p)
    ax.plot([x, xe], [y, y], col, lw=2.0, zorder=5)
    ax.text(xe, y, t, ha='center', va='center', fontsize=7.5, color='white', weight='bold', bbox=dict(boxstyle='round,pad=0.25', fc=col, ec=col), zorder=8)
stub(1, 1.9, 'A18'); stub(2, 1.9, 'A16'); stub(30, 4.1, 'A17'); stub(31, 4.1, 'WE#', '#a0006a')
tag(3.0, ychip(8), '2', G)
# legenda
LY = YT-18.0
leg = [('1', Rd, 'FIO 1  vermelho: chip 32 (VCC da flash) -> pino 28 do soquete (VCC). Mais um ceramico de 100 nF entre chip 32 e chip 16.'),
       ('2', G, 'FIOS 2  azuis (4 fios finos longos para a PLACA DO CIRCUITO): chip 1 = A18, chip 2 = A16, perna levantada do chip 30 = A17, e chip 31 = WE# (lilas).'),
       ('3', '#555555', 'Nada mais ao GND nem ao +5 V no adaptador: pull-downs (A16 a A18) e pull-up (WE#) ficam na placa do circuito (pagina 3).')]
for i, (t, c, txt) in enumerate(leg):
    y = LY-i*2.6; tag(-10.0, y, t, c); ax.text(-9.1, y, txt, ha='left', va='center', fontsize=8)
ax.text(-10.3, LY-3*2.6-0.4, 'Perna do chip 30: dobrar para fora SEM encostar no soquete (o soquete 28 e o VCC da placa).', ha='left', va='center', fontsize=8.4, color='#cc0000', weight='bold')
fig.savefig('adaptador_flash_sobreposto_v2.png', dpi=170, bbox_inches='tight'); plt.close(fig)


fig, ax = plt.subplots(figsize=(10, 7.2)); ax.set_xlim(0, 100); ax.set_ylim(-3, 68); ax.axis('off')
ax.text(50, 66, 'Placa do circuito, versao base (so resistores): mantem banco 0 e flash somente leitura', ha='center', fontsize=10.5, weight='bold')
ax.add_patch(Rectangle((6, 4), 28, 56, fc='#fdf6d8', ec='k', lw=1.4)); ax.text(20, 61.2, 'adaptador HI + adaptador LO', ha='center', fontsize=8.5, weight='bold')
nets = [('A18', 54, '#0a6bd0', 'pino 1 de cada flash', 'R1  10 k para GND', 'k'), ('A16', 40, '#0a6bd0', 'pino 2 de cada flash', 'R2  10 k para GND', 'k'), ('A17', 26, '#0a6bd0', 'pino 30 de cada flash', 'R3  10 k para GND', 'k'), ('WE#', 12, '#a0006a', 'pino 31 de cada flash', 'R4  4,7 k para +5 V', '#b00000')]
for nm, y, c, src, rr, gc in nets:
    ax.plot([34, 62], [y, y], c, lw=2); ax.text(20, y, nm + '\n(' + src + ')', ha='center', va='center', fontsize=8, color=c, weight='bold'); ax.plot([48], [y], 'o', color=c, ms=5)
    ax.plot([48, 48], [y, y-2], c, lw=1.4); ax.add_patch(Rectangle((47, y-5.4), 2, 3.4, fc='white', ec='k', lw=1.1)); ax.text(50.5, y-3.7, rr, fontsize=7.8, va='center')
    ax.plot([48, 48], [y-5.4, y-7.0], c, lw=1.4); ax.plot([46.4, 49.6], [y-7.0, y-7.0], gc, lw=2); ax.text(52, y-7.0, '+5 V' if nm == 'WE#' else 'GND', ha='left', va='center', fontsize=7.5, color=gc)
    ax.add_patch(Rectangle((62, y-1.3), 5, 2.6, fc='#eeeeee', ec='k', lw=1.1)); ax.text(68, y, 'ponto de ligacao futuro', fontsize=7.6, va='center')
ax.text(6, -1.8, 'Passo 2: o ponto WE# recebe o 74LS32 (e o jumper). Passo 3: os pontos A16, A17 e A18 recebem o 74LS175.', fontsize=8.3)
fig.savefig('placa_base_flash_v2.png', dpi=170, bbox_inches='tight'); plt.close(fig)

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
doc = SimpleDocTemplate('Paragon50_Adaptador_Flash_Am29F040B_Pinagem_v2.pdf', pagesize=A4, leftMargin=12*mm, rightMargin=12*mm, topMargin=10*mm, bottomMargin=10*mm, title='PARAGON 50 - adaptador Am29F040B sobre soquete 28 pinos (v1)')
from PIL import Image as PI
_w,_h = PI.open('adaptador_flash_sobreposto_v2.png').size
IMG = Image('adaptador_flash_sobreposto_v2.png', width=186*mm, height=186*mm*_h/_w)
S = [Paragraph('PARAGON 50 &ndash; adaptador da Am29F040B (DIP-32 sobre o soquete DIP-28)', H),
Paragraph('Tabajara Labs &middot; v2 &middot; 13/11/2026. A flash de 32 pinos é encaixada sobre o soquete de 28 pinos <b>deslocada de dois furos</b>: o pino 3 da flash fica sobre o pino 1 do soquete. Assim, <b>os pinos 3 a 29 da flash coincidem com os pinos 1 a 27 do soquete e têm exatamente a mesma função</b> (conferido um a um na tabela da página 2). Só sobram quatro pinos de fora (1, 2, 31 e 32) e um pino que cai no lugar errado (o 30).', P),
IMG]
S += [PageBreak(), Paragraph('O que fazer, pino por pino', H2),
tbl([['Pino da flash', 'Função', 'Cai sobre', 'O que fazer'],
['3 a 15, 17 a 29', 'A15, A12...A0, DQ0 a DQ2, DQ3 a DQ7, CE#, A10, OE#, A11, A9, A8, A13, A14', 'soquete 1 a 13 e 15 a 27 (mesma função)', '<b>Nada.</b> Ligam direto ao soquete.'],
['16', 'VSS (GND)', 'soquete 14 (GND)', 'Nada. É o GND da flash.'],
['<font color="#cc0000"><b>30</b></font>', 'A17 (bit de banco)', 'soquete 28 (<b>VCC</b>)', '<b>LEVANTAR</b> a perna (dobrar para fora, sem encostar no soquete) e ligar um fio fino a ela: <b>A17</b> para a placa do circuito.'],
['32', 'VCC da flash', 'fora do soquete (acima do pino 28)', '<b>FIO 1:</b> ligar ao pino 28 do soquete (VCC).'],
['31', 'WE# (habilita escrita)', 'fora do soquete', 'fio fino para a placa do circuito: <b>WE#</b>. Lá ele fica em +5 V por um pull-up (só leitura).'],
['2', 'A16 (bit de banco)', 'fora do soquete', 'fio fino para a placa do circuito: <b>A16</b>.'],
['1', 'A18 (bit de banco)', 'fora do soquete', 'fio fino para a placa do circuito: <b>A18</b>.']], [28, 48, 38, 74]),
Paragraph('Resumo dos fios de cada adaptador', H2),
tbl([['Fio', 'De', 'Para', 'Observação'],
['1', 'flash 32', 'soquete 28 (VCC)', 'vermelho; mais 100 nF entre os pinos 32 e 16 da flash'],
['A16', 'flash 2', 'placa do circuito', 'fio fino, curto (até uns 15 cm)'],
['A17', 'flash 30 (perna levantada)', 'placa do circuito', 'idem'],
['A18', 'flash 1', 'placa do circuito', 'idem'],
['WE#', 'flash 31', 'placa do circuito', 'idem']], [14, 46, 42, 80]),
Paragraph('Os dois adaptadores (HI e LO) vão aos <b>mesmos</b> quatro pontos da placa do circuito: A16 com A16, A17 com A17, A18 com A18 e WE# com WE#. Fazer dois adaptadores iguais.', P),
Paragraph('Conferência com o multímetro, sem a flash ou com ela fora do soquete', H2),
Paragraph('1. Continuidade soquete 28 (VCC) a flash 32; soquete 14 (GND) a flash 16.<br/>2. <b>Sem continuidade</b> entre a perna levantada do pino 30 e o soquete 28, e entre os fios A16, A17, A18, WE# e qualquer outro ponto.<br/>3. Sem curto entre VCC e GND em nenhum ponto (com o adaptador fora da placa).<br/>4. Só então gravar (as imagens da v2.3, oito cópias) e instalar. Pino 1 do soquete do mesmo lado do entalhe da ROM antiga.', P),
Paragraph('Os fios A16, A17 e A18 já ficam prontos para o passo 3: lá, o registrador de banco só precisa ser ligado à placa do circuito.', C)]
from PIL import Image as PI2
_w2,_h2 = PI2.open('placa_base_flash_v2.png').size
S += [PageBreak(), Paragraph('Placa do circuito &ndash; versão base (para montar já)', H2),
Paragraph('Monte numa plaquinha perfurada pequena, com 4 pontos de entrada (A16, A17, A18, WE#) para os fios dos dois adaptadores, e só estes quatro resistores. Com ela, a placa funciona como hoje: os <b>pull-downs de 10 k</b> mantêm A16, A17 e A18 em nível baixo (banco 0) e o <b>pull-up de 4,7 k</b> mantém o WE# em +5 V (a flash só lê). Como a imagem v2.3 está gravada nos oito bancos, mesmo se um fio soltar nada muda.', P),
Image('placa_base_flash_v2.png', width=182*mm, height=182*mm*_h2/_w2),
Paragraph('Alimentação: o +5 V e o GND vêm de qualquer ponto próximo da placa. Cada ponto de ligação futuro é onde o circuito de escrita (74LS32) e o registrador de banco (74LS175) serão ligados depois, sem mexer mais nos adaptadores. A saída do 74LS32 ou do 74LS175 passa a empurrar a linha contra o resistor; os valores acima aguentam isso com folga.', C)]
doc.build(S)
