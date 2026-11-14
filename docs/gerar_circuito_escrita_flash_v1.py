# -*- coding: utf-8 -*-
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, PageBreak
from PIL import Image as PI

BL = '#1f5fbf'; RD = '#b00000'; K = '#111111'
def gate(ax, x, y, w, h, a, b, o, pa, pb, po, name):
    ax.add_patch(Rectangle((x, y), w, h, fc='#fdf6d8', ec='k', lw=1.4, zorder=2))
    ax.text(x+w/2, y+h/2, '>=1', ha='center', va='center', fontsize=12, weight='bold')
    ax.text(x+w/2, y+h+0.7, name, ha='center', fontsize=8, color='#555555')
    ya, yb, yo = y+h*0.72, y+h*0.28, y+h/2
    ax.text(x-0.4, ya+0.5, f'pino {pa}', ha='right', fontsize=7, color='#777777'); ax.text(x-0.4, yb-1.1, f'pino {pb}', ha='right', fontsize=7, color='#777777')
    ax.text(x+w+0.4, yo+0.6, f'pino {po}', ha='left', fontsize=7, color='#777777')
    return ya, yb, yo

# ---------- figura 1: circuito de escrita ----------
fig, ax = plt.subplots(figsize=(10, 7.4)); ax.set_xlim(0, 100); ax.set_ylim(-14, 74); ax.axis('off')
ax.text(50, 72, 'Circuito de escrita da flash (passo 2): um 74LS32 gera o /WE de cada flash', ha='center', fontsize=10.5, weight='bold')
# G1: X = R/W + ROM_CE
ya1, yb1, yo1 = gate(ax, 30, 52, 11, 9, 1, 2, 3, 1, 2, 3, 'porta 1  (X)')
ax.plot([8, 30], [ya1, ya1], BL, lw=1.6); ax.text(7.5, ya1, 'R/W  (CPU pino 9)', ha='right', va='center', fontsize=8.5, color=BL)
ax.plot([8, 30], [yb1, yb1], BL, lw=1.6); ax.text(7.5, yb1, 'ROM_CE  (soquete da ROM, pino 20)', ha='right', va='center', fontsize=8.5, color=BL)
ax.plot([41, 50], [yo1, yo1], K, lw=1.6); ax.text(45.5, yo1+1.0, 'X', ha='center', fontsize=9, weight='bold')
# G2: WE_H = X + /UDS
ya2, yb2, yo2 = gate(ax, 58, 34, 11, 9, 4, 5, 6, 4, 5, 6, 'porta 2  (HI)')
ax.plot([50, 50], [yo1, ya2], K, lw=1.6); ax.plot([50, 58], [ya2, ya2], K, lw=1.6); ax.plot([50], [yo1], 'o', color=K, ms=4)
ax.plot([8, 58], [yb2, yb2], BL, lw=1.6); ax.text(7.5, yb2, '/UDS  (CPU pino 7)', ha='right', va='center', fontsize=8.5, color=BL)
# G3: WE_L = X + /LDS
ya3, yb3, yo3 = gate(ax, 58, 12, 11, 9, 9, 10, 8, 9, 10, 8, 'porta 3  (LO)')
ax.plot([50, 50], [ya2, ya3], K, lw=1.6); ax.plot([50, 58], [ya3, ya3], K, lw=1.6); ax.plot([50], [ya2], 'o', color=K, ms=4)
ax.plot([8, 58], [yb3, yb3], BL, lw=1.6); ax.text(7.5, yb3, '/LDS  (CPU pino 8)', ha='right', va='center', fontsize=8.5, color=BL)
# saidas -> jumper -> WE# com pull-up
for (yo, nm, tag) in ((yo2, 'WE# da flash HI (D8-D15)', 'JP-H'), (yo3, 'WE# da flash LO (D0-D7)', 'JP-L')):
    ax.plot([69, 78], [yo, yo], K, lw=1.6)
    ax.add_patch(Rectangle((78, yo-1.1), 4, 2.2, fc='white', ec='k', lw=1.3, zorder=3)); ax.text(80, yo+2.0, tag, ha='center', fontsize=8, weight='bold')
    ax.plot([82, 92], [yo, yo], K, lw=1.6); ax.plot([86], [yo], 'o', color=K, ms=4)
    ax.text(92.6, yo, nm + '\n(pino 31 do adaptador)', ha='left', va='center', fontsize=8, color=RD)
    ax.plot([86, 86], [yo, yo+7], K, lw=1.2); ax.add_patch(Rectangle((85, yo+7), 2, 4, fc='white', ec='k', lw=1.1)); ax.text(88, yo+9, '4,7 k', fontsize=7.5, va='center')
    ax.plot([86, 86], [yo+11, yo+13.5], K, lw=1.2); ax.plot([84.5, 87.5], [yo+13.5, yo+13.5], RD, lw=2); ax.text(86, yo+14.6, '+5 V', ha='center', fontsize=7.5, color=RD)
ax.text(80, yo2-4.2, 'jumper ABERTO = WE# em +5 V (so leitura)', ha='center', fontsize=7.6, style='italic')
# porta 4 e alimentacao
ax.text(4, 4, 'Porta 4 sem uso: pinos 12 e 13 ao GND (pino 7), saida 11 solta.', fontsize=8.3)
ax.text(4, 0.5, '74LS32: pino 14 = +5 V, pino 7 = GND, 100 nF entre eles junto do chip.', fontsize=8.3)
ax.text(4, -3, 'Nivel ativo: WE# fica BAIXO so quando R/W, ROM_CE e /UDS (ou /LDS) estao todos baixos', fontsize=8.3)
ax.text(4, -6, '= escrita (R/W baixo) na regiao da ROM ($F80000-$F9FFFF) no byte alto (UDS) ou baixo (LDS).', fontsize=8.3)
ax.text(4, -9, 'A flash recebe o endereco e o dado do barramento e usa ROM_CE como CE#.', fontsize=8.3)
ax.text(4, -12, 'Lembrete: HI = ROM do byte alto (D8-D15, /UDS), LO = byte baixo (D0-D7, /LDS).', fontsize=8.3, color=RD)
fig.savefig('circuito_escrita_flash_v1.png', dpi=170, bbox_inches='tight'); plt.close(fig)

# ---------- figura 2: registrador de banco (proposta) ----------
fig, ax = plt.subplots(figsize=(10, 5.6)); ax.set_xlim(0, 100); ax.set_ylim(0, 56); ax.axis('off')
ax.text(50, 54, 'Passo 3 (proposta, nao montar ainda): registrador de banco em $FC0000', ha='center', fontsize=10.5, weight='bold')
ax.add_patch(Rectangle((10, 36), 22, 9, fc='#fdf6d8', ec='k', lw=1.4)); ax.text(21, 40.5, '74LS32 (2o chip)\nCLK = Y2 + R/W + /LDS', ha='center', va='center', fontsize=8)
ax.plot([2, 10], [43, 43], BL, lw=1.5); ax.text(1.5, 43, 'U4 pino 13 (Y2 = $FC0000)', ha='right', va='center', fontsize=7.8, color=BL)
ax.plot([2, 10], [40.5, 40.5], BL, lw=1.5); ax.text(1.5, 40.5, 'R/W', ha='right', va='center', fontsize=7.8, color=BL)
ax.plot([2, 10], [38, 38], BL, lw=1.5); ax.text(1.5, 38, '/LDS', ha='right', va='center', fontsize=7.8, color=BL)
ax.add_patch(Rectangle((48, 20), 20, 24, fc='#e9f1ff', ec='k', lw=1.4)); ax.text(58, 41, '74LS175', ha='center', fontsize=9, weight='bold'); ax.text(58, 38.5, '4 flip-flops D com /CLR', ha='center', fontsize=7.5)
ax.plot([32, 48], [40.5, 40.5], K, lw=1.5); ax.text(40, 41.7, '/BANK_WR', ha='center', fontsize=7.5)
ax.text(46.5, 40.5, 'CLK', ha='right', fontsize=7)
for i, (d, q, nm) in enumerate((('D0', 'Q0', 'A16  (pino 2 de cada flash)'), ('D1', 'Q1', 'A17  (pino 30)'), ('D2', 'Q2', 'A18  (pino 1)'))):
    y = 34-i*4.5
    ax.plot([40, 48], [y, y], BL, lw=1.4); ax.text(39.5, y, f'{d} da CPU', ha='right', va='center', fontsize=7.8, color=BL)
    ax.plot([68, 80], [y, y], K, lw=1.4); ax.text(80.8, y, f'{q} -> {nm}', ha='left', va='center', fontsize=7.8, color=RD)
ax.plot([40, 48], [21.5, 21.5], BL, lw=1.4); ax.text(39.5, 21.5, '/RESET da placa -> /CLR', ha='right', va='center', fontsize=7.8, color=BL)
ax.text(5, 14, 'Escrever 0 a 7 em $FC0000 escolhe o banco; no reset o registrador zera e a placa sempre parte do banco 0.', fontsize=8.3)
ax.text(5, 10.5, 'Y2 ja gera /DTACK (medido no mapa de enderecos: $FC0000 responde sem dispositivo), entao nao precisa de gerador novo.', fontsize=8.3)
ax.text(5, 7, 'A troca de banco deve ser feita por codigo que roda na RAM: ao trocar, a ROM visivel muda debaixo do programa.', fontsize=8.3, color=RD)
ax.text(5, 3.5, 'Pino 13 do U4 precisa ser conferido (livre?) antes: no netlist v6 as saidas Y2 e Y3 constam como sem uso.', fontsize=8.3)
fig.savefig('banco_flash_v1.png', dpi=170, bbox_inches='tight'); plt.close(fig)

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
def img(n, wmm):
    w, h = PI.open(n).size; return Image(n, width=wmm*mm, height=wmm*mm*h/w)
doc = SimpleDocTemplate('Paragon50_Circuito_Escrita_Flash_v1.pdf', pagesize=A4, leftMargin=13*mm, rightMargin=13*mm, topMargin=11*mm, bottomMargin=11*mm, title='PARAGON 50 - circuito de escrita da flash, passo 2 (v1)')
S = [Paragraph('PARAGON 50 &ndash; circuito de escrita da flash (passo 2)', H),
Paragraph('Tabajara Labs &middot; v1 &middot; 13/11/2026. Faz a CPU conseguir <b>gravar e apagar</b> as duas Am29F040B instaladas nos adaptadores do passo 1. Baseado nas medições de hoje: o /DTACK vem do U35 (74LS11) e <b>não depende do R/W</b> (escritas na região da ROM terminam normalmente), então não se mexe no gerador de /DTACK. Só se acrescenta um 74LS32 numa plaquinha perfurada.', P),
img('circuito_escrita_flash_v1.png', 182),
Paragraph('Ligações', H2),
tbl([['Sinal', 'De onde tirar', 'Observação'],
['R/W', 'CPU pino 9 (ou qualquer ponto da mesma rede)', 'baixo = escrita'],
['/UDS', 'CPU pino 7', 'seleciona o byte alto (D8 a D15)'],
['/LDS', 'CPU pino 8', 'seleciona o byte baixo (D0 a D7)'],
['ROM_CE', 'pino 20 de qualquer soquete da ROM (mesma rede dos dois; saída U5 pino 8)', 'baixo durante acesso à região da ROM'],
['+5 V e GND', 'pino 16 e pino 8 do U6, ou qualquer 74LS próximo', '100 nF no 74LS32'],
['WE# HI e WE# LO', 'saídas dos pinos 6 e 8 do 74LS32, <b>pelos jumpers JP-H e JP-L</b>', 'ligam no fio 2 (pino 31) do adaptador correspondente (retirar a ligação ao +5 V)']], [34, 90, 58]),
PageBreak(),
Paragraph('Por que funciona (temporização)', H2),
Paragraph('No ciclo de escrita do 68000 o dado fica válido antes de /UDS ou /LDS descerem, e permanece até depois de subirem. O /WE da flash é a <b>OR</b> de R/W, ROM_CE e /UDS (ou /LDS): ele só desce quando os três estão baixos, e sobe quando /UDS ou /LDS sobem, <b>com o dado ainda no barramento</b>. A flash trava o endereço na descida do /WE e o dado na subida. Como cada ciclo da placa dura cerca de 1 us (4 estados de espera, medido), o pulso de /WE fica na casa de centenas de ns, muito acima do mínimo da Am29F040B (algumas dezenas de ns). Nenhuma mudança de /DTACK é necessária.', P),
Paragraph('Proteções', H2),
Paragraph('&bull; <b>Jumpers abertos no uso normal:</b> sem jumper o /WE fica em +5 V por 4,7 k e nada escreve. Só feche JP-H e JP-L para atualizar.<br/>&bull; <b>A própria flash exige sequência de desbloqueio</b> (AA em 555, 55 em 2AA e o comando), então uma escrita perdida, sozinha, não altera nada.<br/>&bull; <b>Banco 0 reservado ao boot:</b> o programa de atualização nunca apaga o setor do banco 0.<br/>&bull; A rotina de atualização roda <b>na RAM</b>, porque a flash não pode ser lida durante apagamento ou gravação.', P),
Paragraph('Três medições antes de ligar (eu faço pelas pontes, com você só movendo a ponta)', H2),
tbl([['#', 'Verificar', 'Esperado', 'Por quê'],
['1', 'ROM_OE (U2 pino 8) durante o laço de escrita em $F80000', 'ALTO durante a escrita', 'Se o /OE da flash ficar ativo na escrita, ela e a CPU empurram o barramento ao mesmo tempo. A flash exige OE# alto durante a escrita.'],
['2', 'ROM_CE (U5 pino 8) durante o laço de escrita', 'BAIXO durante a escrita', 'É o CE# da flash; só mediu-se a leitura até agora.'],
['3', 'Saídas do 74LS32 com o jumper aberto, no laço de escrita', 'pulsos baixos só nas portas certas (HI e LO) e nada no jumper aberto', 'Confirma a lógica antes de a flash ser ligada.']], [8, 62, 38, 74]),
Paragraph('A sequência de gravação, depois de montado', H2),
Paragraph('1. Código na RAM: ID (555/AA, 2AA/55, 555/90; ler X00 = 01 e X01 = A4 nas duas flash; reset com F0). O endereço do 68000 que cai em 555H da flash passa pelos inversores de A13 a A15 do U26: <b>o ID lido de volta confirma o mapeamento</b> antes de qualquer apagamento.<br/>2. Fechar os jumpers, apagar o setor de um banco que não seja o 0 e gravar byte a byte com verificação por DQ7.<br/>3. Abrir os jumpers.', P)]
S += [PageBreak(), Paragraph('Passo 3 &ndash; troca de banco (proposta para depois)', H2),
Paragraph('Para escolher entre os 8 bancos (um banco = um setor de 64 KB por chip, 128 KB em palavras), três bits A16, A17 e A18 vão às duas flash. A proposta aproveita a saída <b>Y2 do U4 ($FC0000)</b>, que já responde com /DTACK, e um 74LS175 com /CLR ligado ao /RESET, para o computador sempre partir do banco 0.', P),
img('banco_flash_v1.png', 182),
Paragraph('Estado: <b>proposta</b>. Falta conferir se o pino 13 do U4 está mesmo livre e se o /RESET da placa serve para o /CLR. O passo 2 é independente e pode ser montado antes.', C)]
doc.build(S)
