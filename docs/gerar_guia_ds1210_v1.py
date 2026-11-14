# -*- coding: utf-8 -*-
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image, PageBreak

# ---------------- figura ----------------
fig, ax = plt.subplots(figsize=(10, 4.9)); ax.set_xlim(0, 100); ax.set_ylim(0, 49); ax.axis('off')
def box(x, y, w, h, t, fc='#fdf6d8'):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec='k', lw=1.2)); ax.text(x+w/2, y+h+1.2, t, ha='center', fontsize=9, weight='bold')
def pin(x, y, side, n, name):
    if side == 'L': ax.plot([x-5, x], [y, y], 'k', lw=1); ax.text(x+1, y, f'{n} {name}', va='center', fontsize=8)
    else: ax.plot([x, x+5], [y, y], 'k', lw=1); ax.text(x-1, y, f'{name} {n}', va='center', ha='right', fontsize=8)
# DS1210
box(34, 12, 18, 30, 'DS1210 (DIP-8)')
for i, (n, nm, y) in enumerate([(8, 'VCCI', 38), (3, 'TOL', 32), (5, 'CE', 26), (4, 'GND', 16)]): pin(34, y, 'L', n, nm)
for n, nm, y in [(1, 'VCCO', 38), (6, 'CEO', 26), (2, 'VBAT1', 20), (7, 'VBAT2', 14)]: pin(52, y, 'R', n, nm)
# fontes e fios a esquerda
ax.text(21, 38, '+5 V da placa', ha='right', va='center', fontsize=8, color='#b00000'); ax.plot([22, 29], [38, 38], '#b00000', lw=1.4)
ax.text(21, 32, 'GND  (trip 4,50 a 4,74 V)', ha='right', va='center', fontsize=8); ax.plot([22, 29], [32, 32], 'k', lw=1)
ax.text(21, 26, 'U_AND pino 3 (RAM_CS_MOD)', ha='right', va='center', fontsize=8, color='#1f5fbf'); ax.plot([22, 29], [26, 26], '#1f5fbf', lw=1.4)
ax.text(21, 16, 'GND', ha='right', va='center', fontsize=8); ax.plot([22, 29], [16, 16], 'k', lw=1)
# a direita: RAMs
box(74, 26, 22, 18, 'U13 e U14  KM681000BLP-5')
ax.text(85, 40, 'pino 32  VCC', ha='center', fontsize=8); ax.text(85, 31, 'pino 22  /CS1', ha='center', fontsize=8); ax.text(85, 28.2, '(pino 30 CS2 junto do pino 32)', ha='center', fontsize=7)
ax.plot([57, 74], [38, 38], '#b00000', lw=1.6); ax.plot([57, 74], [26, 26], '#1f5fbf', lw=1.6)
ax.text(66, 39.2, 'VCCO', ha='center', fontsize=8, color='#b00000'); ax.text(66, 24.4, 'CEO', ha='center', fontsize=8, color='#1f5fbf')
ax.plot([74, 74], [38, 26], 'none')
# bateria
ax.plot([57, 62], [20, 20], 'k', lw=1.2); ax.plot([62, 62], [17.5, 22.5], 'k', lw=2.2); ax.plot([64.5, 64.5], [19, 21], 'k', lw=2.2); ax.plot([64.5, 64.5], [20, 12], 'k', lw=1.2)
ax.text(67, 20, '+  pilha de lítio 3 V (CR2032)', fontsize=8, va='center'); ax.plot([64.5, 64.5], [12, 10], 'k', lw=1.2); ax.text(64.5, 8.8, 'GND', ha='center', fontsize=8)
ax.plot([57, 59], [14, 14], 'k', lw=1); ax.text(60, 14, 'VBAT2 em GND (não usado)', fontsize=8, va='center')
ax.text(50, 3.5, 'Um DS1210 serve às duas RAMs, desde que a retenção das duas somadas fique abaixo de 50 uA (ver passo 5).', ha='center', fontsize=8.5, style='italic')
fig.savefig('liga_ds1210_v1.png', dpi=170, bbox_inches='tight'); plt.close(fig)

# ---------------- PDF ----------------
ss = getSampleStyleSheet()
H = ParagraphStyle('h', parent=ss['Title'], fontSize=15, spaceAfter=2)
H2 = ParagraphStyle('h2', parent=ss['Heading2'], fontSize=11, spaceBefore=7, spaceAfter=3)
P = ParagraphStyle('p', parent=ss['BodyText'], fontSize=8.8, leading=11.4)
C = ParagraphStyle('c', parent=P, fontSize=8.3, leading=10.2)
W = ParagraphStyle('w', parent=P, backColor=colors.HexColor('#fff1d6'), borderPadding=4, borderColor=colors.HexColor('#d99a2b'), borderWidth=0.6, spaceBefore=4, spaceAfter=4)
def tbl(rows, w):
    data = [[Paragraph(str(c), C) for c in r] for r in rows]
    t = Table(data, colWidths=[x*mm for x in w], repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dbe4f0')), ('GRID', (0, 0), (-1, -1), 0.4, colors.grey), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
    return t
doc = SimpleDocTemplate('Paragon50_Guia_Bateria_RAM_DS1210_v1.pdf', pagesize=A4, leftMargin=14*mm, rightMargin=14*mm, topMargin=12*mm, bottomMargin=12*mm, title='PARAGON 50 - bateria de backup das RAMs (DS1210) v1')
S = [Paragraph('PARAGON 50 &ndash; bateria de backup das RAMs com DS1210', H),
Paragraph('Tabajara Labs &middot; guia v1 &middot; 13/11/2026. Faz as duas SRAMs KM681000BLP-5 (U13 e U14) guardarem o conteúdo com a placa desligada: a RAM2 mantém o disco P: do CP/M, e a RAM1 também retém o que tinha. Pinagens e limites do DS1210 e da KM681000 conferidos nos datasheets (fontes no fim).', P),
Paragraph('<b>Atenção ao limite do DS1210:</b> em modo bateria ele só garante <b>50 uA</b> de corrente de saída (VCCO). A KM681000 (versão L) tem corrente de standby de até 100 uA <i>por chip</i> pelo datasheet (valor típico não informado no datasheet). Por isso o passo 5 é <b>medir</b> a retenção real das duas RAMs antes de instalar.', W),
Image('liga_ds1210_v1.png', width=182*mm, height=182*mm*4.9/10*0.99),
Paragraph('Ligações', H2),
tbl([['DS1210', 'Nome', 'Liga em', 'Observação'],
['8', 'VCCI', '+5 V da placa', 'alimentação normal; perto do pino 32 das RAMs'],
['4', 'GND', 'GND', ''],
['1', 'VCCO', 'pino 32 (VCC) de U13 e U14', 'tira o +5 V direto desses pinos; máx. 80 mA médios (datasheet)'],
['5', 'CE', 'saída do 74LS08 (RAM_CS_MOD, U_AND pino 3)', 'é a entrada de /CS1 que hoje vai às RAMs'],
['6', 'CEO', 'pino 22 (/CS1) de U13 e U14', 'segue o CE em 20 ns no máximo; vai a nível alto na queda'],
['2', 'VBAT1', '+ da pilha de lítio 3 V', 'faixa aceita de 2,0 a 4,0 V; não usar pilha recarregável'],
['7', 'VBAT2', 'GND', 'entrada não usada tem que ir a GND (datasheet)'],
['3', 'TOL', 'GND', 'disparo em 4,50 a 4,74 V: protege antes do reset da CPU. Com VCCO seria 4,25 a 4,49 V'],
['&ndash;', 'CS2 (pino 30 das RAMs)', 'junto do pino 32 (VCCO)', 'deve ficar em nível alto ou abaixo de 0,2 V na retenção']], [17, 28, 60, 77])]
S += [PageBreak(), Paragraph('Passo a passo', H2),
Paragraph('<b>1. Montar o DS1210.</b> Soquete DIP-8 em placa perfurada e suporte para a pilha (CR2032). Capacitor de 100 nF entre VCCI e GND, junto do chip. Marque o pino 1. <b>Ainda sem a pilha.</b>', P),
Paragraph('<b>2. Tirar o +5 V dos pinos 32 das RAMs.</b> Levante a ligação do pino 32 em U13 e U14 e ligue os dois ao VCCO (pino 1 do DS1210). O pino 30 (CS2) já vai junto do 32 nos adaptadores; confirme com o multímetro.', P),
Paragraph('<b>3. Interceptar o /CS1.</b> Levante o fio que vai da saída do 74LS08 (pino 3) aos pinos 22 de U13 e U14. Esse fio passa a ir ao CE (pino 5) do DS1210, e o CEO (pino 6) vai aos dois pinos 22.', P),
Paragraph('<b>4. Conferir sem a pilha.</b> Ligue a placa: tem que funcionar como antes (ROM v2.3, comando <b>I</b> do monitor e <b>T 42000 5FFFF</b> na RAM2). Só siga se estiver tudo igual.', P),
Paragraph('<b>5. Medir a retenção (placa desligada).</b> No lugar da pilha, ligue 3,0 V de uma fonte (a 66332A serve) ao VBAT1 e ao GND, com o <b>34401A em série na faixa de uA</b>. Antes de medir, ligue a placa uma vez e desligue, para o DS1210 entrar em modo bateria. A leitura é a retenção das duas RAMs somada (mais, no máximo, 100 nA do chip). <b>Abaixo de 50 uA:</b> o DS1210 serve com folga. <b>Entre 50 e 100 uA:</b> fora da garantia do chip (pode funcionar, sem garantia). <b>Acima disso:</b> não use o DS1210; me avise e eu proponho uma chave de bateria com mais corrente.', P),
Paragraph('<b>6. Instalar a pilha</b> (confira a polaridade) e fazer o teste de retenção: no monitor, <b>P 42000 A5</b> e <b>D 42000 4200F</b> (vê o A5). Desligue por um minuto, ligue de novo e repita o <b>D</b>: o A5 tem que continuar lá. No CP/M, crie um arquivo em P:, desligue e veja o <b>DIR P:</b> depois. Se perder, meça a tensão em VCCO com a placa desligada (perto de VBAT menos 0,3 V).', P),
Paragraph('Cuidados', H2),
Paragraph('&bull; <b>Corrente do VCCO:</b> o datasheet dá 80 mA médios em operação; duas RAMs em acessos de 55 ns ficam longe disso no Paragon (barramento a 8 MHz), mas se aquecer, use um DS1210 por RAM.<br/>'
          '&bull; <b>Zerar a RAM2 apaga o disco P:</b> o comando <b>Z</b> e o teste <b>T</b> em $04xxxx continuam destrutivos mesmo com a bateria.<br/>'
          '&bull; <b>O disparo do DS1210</b> (4,50 a 4,74 V com TOL em GND) não foi comparado com o limiar do supervisor da placa (DS1232), que não foi medido. Se a placa reiniciar com o 5 V estável perto de 4,7 V, troque TOL para VCCO.<br/>'
          '&bull; <b>Desfazer:</b> religar os pinos 32 ao +5 V e os pinos 22 à saída do 74LS08, e retirar o DS1210.<br/>'
          '&bull; A pilha de lítio não deve ficar em curto nem ser soldada por quem não a trate como pilha: use suporte.', P),
Paragraph('Fontes', H2),
Paragraph('DS1210 Nonvolatile Controller Chip (Dallas Semiconductor): manualmachine.com/datasheet/ds1210s/3913280-datasheet-dallas-semiconductor (pinagem, TOL, 80 mA, 50 uA em bateria, 20 ns). '
          'KM681000B Family (Samsung): manualmachine.com/samsung/km681000blt7l/4244748-datasheet (VDR 2 V, ISB1 L = 100 uA, condição de CS1/CS2). Valores a reconferir no datasheet original antes de soldar.', C)]
doc.build(S)
