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
BL='#1f5fbf'; RD='#b00000'; K='#111111'; GR='#777777'
fig, ax = plt.subplots(figsize=(10, 7.6)); ax.set_xlim(0, 100); ax.set_ylim(0, 76); ax.axis('off')
ax.text(50, 74, 'Registrador de banco: 74LS175 em $FC0000 (passo 3)', ha='center', fontsize=11, weight='bold')
# --- porta 4 do 74LS32
ax.add_patch(Rectangle((10, 58), 12, 9, fc='#fdf6d8', ec='k', lw=1.4, zorder=2)); ax.text(16, 62.5, '>=1', ha='center', va='center', fontsize=12, weight='bold')
ax.text(16, 70.4, '74LS32  porta 4 (a que sobrou)', ha='center', fontsize=8, color='#555555')
ax.plot([1, 10], [65, 65], BL, lw=1.6); ax.text(0.8, 67.6, 'U4 pino 13 (Y2 = $FC0000)', ha='left', fontsize=8, color=BL); ax.text(9.6, 63.4, 'pino 12', ha='right', fontsize=7, color=GR)
ax.plot([1, 10], [60, 60], BL, lw=1.6); ax.text(0.8, 56.6, 'R/W (CPU pino 9)', ha='left', fontsize=8, color=BL); ax.text(9.6, 58.4, 'pino 13', ha='right', fontsize=7, color=GR)
ax.text(1, 53.2, '(tirar os pinos 12 e 13 do GND)', ha='left', fontsize=7.5, color=RD)
ax.plot([22, 36], [62.5, 62.5], K, lw=1.6); ax.text(22.4, 64, 'pino 11', ha='left', fontsize=7, color=GR); ax.text(29, 60.8, 'CLK', ha='center', fontsize=8, weight='bold')
ax.plot([36, 36], [62.5, 49.5], K, lw=1.6); ax.plot([36, 41], [49.5, 49.5], K, lw=1.6)
# --- 74LS175
ax.add_patch(Rectangle((41, 12), 24, 44, fc='#e9f1ff', ec='k', lw=1.5, zorder=2)); ax.text(53, 52.5, '74LS175', ha='center', fontsize=11, weight='bold'); ax.text(53, 49.8, '4 flip-flops D', ha='center', fontsize=8)
pins_l = [('/CLR', 1, 44, '/RESET da placa (CPU pino 18)'), ('1D', 4, 38, 'D0  (CPU pino 5)'), ('2D', 5, 32, 'D1  (CPU pino 4)'), ('3D', 12, 26, 'D2  (CPU pino 3)'), ('4D', 13, 20, 'GND')]
for nm, p, y, src in pins_l:
    ax.plot([29, 41], [y, y], BL, lw=1.5); ax.text(41.8, y+0.6, nm, ha='left', fontsize=8.5, weight='bold'); ax.text(40.6, y-2.0, f'pino {p}', ha='right', fontsize=7, color=GR)
    ax.text(28.6, y, src, ha='right', va='center', fontsize=8, color=BL)
ax.text(41.8, 49.5+0.6, 'CLK', ha='left', fontsize=8.5, weight='bold'); ax.text(40.6, 47.5, 'pino 9', ha='right', fontsize=7, color=GR)
for nm, p, y, dst, tag in [('1Q', 2, 38, 'rede A16', 'pino 2 de cada flash'), ('2Q', 7, 32, 'rede A17', 'pino 30 de cada flash'), ('3Q', 10, 26, 'rede A18', 'pino 1 de cada flash')]:
    ax.plot([65, 78], [y, y], K, lw=1.6); ax.text(64.2, y+0.6, nm, ha='right', fontsize=8.5, weight='bold'); ax.text(65.4, y-2.0, f'pino {p}', ha='left', fontsize=7, color=GR)
    ax.text(79, y+0.8, dst, ha='left', fontsize=9, weight='bold', color=RD); ax.text(79, y-1.6, tag, ha='left', fontsize=7.5, color=RD)
    ax.text(71.5, y+1.3, '+ 10 k ao GND', ha='center', fontsize=7, color=GR)
ax.text(66, 18, 'Cada rede tem um pull-down de 10 k ao GND\n(placa-base do adaptador v2): sem o 175,\na placa fica no banco 0.', ha='left', fontsize=7.4, style='italic')
ax.text(53, 8.6, 'Soltos: pinos 3, 6, 11, 14 e 15.   Pino 16 = +5 V (com 100 nF ao GND), pino 8 = GND.', ha='center', fontsize=8.2)
ax.text(53, 5.2, 'Reset: /CLR baixo zera o registrador, e a placa parte sempre do banco 0.', ha='center', fontsize=8.2)
ax.text(53, 1.8, 'Os mesmos tres fios A16/A17/A18 vao as DUAS flash (HI e LO).', ha='center', fontsize=8.2, color=RD, weight='bold')
fig.savefig('banco_74ls175_v1.png', dpi=170, bbox_inches='tight'); plt.close(fig)
ss = getSampleStyleSheet()
H = ParagraphStyle('h', parent=ss['Title'], fontSize=15, spaceAfter=2)
H2 = ParagraphStyle('h2', parent=ss['Heading2'], fontSize=11, spaceBefore=7, spaceAfter=3)
P = ParagraphStyle('p', parent=ss['BodyText'], fontSize=8.8, leading=11.4)
C = ParagraphStyle('c', parent=P, fontSize=8.3, leading=10.2)
def tbl(rows, w):
    data = [[Paragraph(str(c), C) for c in r] for r in rows]
    t = Table(data, colWidths=[x*mm for x in w], repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dbe4f0')), ('GRID', (0,0), (-1,-1), 0.4, colors.grey), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    return t
def img(n, wmm):
    w, h = PI.open(n).size; return Image(n, width=wmm*mm, height=wmm*mm*h/w)
doc = SimpleDocTemplate('Paragon50_Banco_Flash_74LS175_v1.pdf', pagesize=A4, leftMargin=13*mm, rightMargin=13*mm, topMargin=11*mm, bottomMargin=11*mm, title='PARAGON 50 - registrador de banco 74LS175 (v1)')
S = [Paragraph('PARAGON 50 &ndash; registrador de banco da flash (74LS175)', H),
Paragraph('Tabajara Labs &middot; v1 &middot; 13/11/2026. Escolhe qual dos 8 bancos de 128 KB (setor de 64 KB em cada chip) aparece em $F80000-$F9FFFF. Aproveita a <b>porta 4 do 74LS32</b> do circuito de escrita (sem segundo chip) e a saída <b>Y2 do U4</b> ($FC0000), que já responde com /DTACK. <b>Montar com a placa desligada.</b>', P),
img('banco_74ls175_v1.png', 182),
Paragraph('Tabela de ligações (confira pino a pino)', H2),
tbl([['Origem', 'Destino', 'Observação'],
['U4 pino 13 (Y2)', '74LS32 pino 12', 'tirar o pino 12 do GND'],
['R/W (CPU pino 9)', '74LS32 pino 13', 'mesmo ponto do pino 1 do 74LS32; tirar o pino 13 do GND'],
['74LS32 pino 11', '74LS175 pino 9 (CLK)', 'clock = Y2 OU R/W: sobe no fim de uma <b>escrita</b> em $FC0000; leitura não clocka'],
['/RESET (CPU pino 18)', '74LS175 pino 1 (/CLR)', 'reset zera o banco'],
['D0, D1, D2 (CPU pinos 5, 4, 3)', '74LS175 pinos 4, 5, 12', 'bits 0, 1, 2 do número do banco'],
['74LS175 pino 13 (4D)', 'GND', 'entrada não usada'],
['74LS175 pinos 2, 7, 10 (1Q, 2Q, 3Q)', 'redes A16, A17, A18', 'pino 2, 30 e 1 das duas flash (as mesmas redes que já têm os 10 k)'],
['+5 V / GND', '74LS175 pinos 16 / 8', '100 nF entre eles, junto do chip']], [58, 46, 78]),
PageBreak(),
Paragraph('Mapa de bancos', H2),
tbl([['Escrever em $FC0000', 'A18 A17 A16', 'Banco', 'Papel proposto'],
['0', '0 0 0', '0', 'boot (o que já está gravado); reservado'],
['1', '0 0 1', '1', 'ensaio de apagamento e gravação; depois ROM de uso'],
['2 a 7', '0 1 0 ... 1 1 1', '2 a 7', 'livres (monitor, CP/M, imagens de teste...)']], [42, 38, 22, 80]),
Paragraph('Como usar: <b>move.w #n,$FC0000</b> (n = 0 a 7), sempre de código na RAM, porque a ROM visível muda debaixo do programa. Reset volta ao banco 0.', P),
Paragraph('O que eu verifico depois que você montar (pelas pontes)', H2),
tbl([['#', 'Verificação', 'Esperado'],
['4', 'U4 pino 13 durante um laço de escrita em $FC0000 (e durante leituras do monitor)', 'pulso baixo só nas escritas e nos acessos a $FC0000; alto no resto. Confirma que o pino está livre e responde com /DTACK.'],
['5', 'Saída do 74LS32 pino 11 (CLK): escrita contra leitura em $FC0000', 'sobe uma vez ao fim de cada escrita; parada nas leituras'],
['6', 'Troca de banco: escrever 0, 1, 2... e ler $F80000 em cada banco (depois que houver dados distintos)', 'cada banco mostra o seu conteúdo; reset volta ao banco 0'],
['7', 'Margem de tempo: 1000 trocas seguidas de banco 5 e 2, lendo de volta', 'sem erro. Se falhar, o atraso do 74LS32 estraga o tempo de retenção do dado: plano B abaixo.']], [8, 85, 89]),
Paragraph('Pontos de atenção', H2),
Paragraph('&bull; <b>Tempo de retenção do dado:</b> o clock sobe ~15 ns (74LS32) mais o atraso do U4 depois do fim do ciclo, e o dado do 68000 precisa ainda estar válido nesse instante (o 74LS175 pede 5 ns de retenção). É o arranjo usual para registradores em 68000 e deve funcionar. Plano B se falhar: usar /AS no lugar de Y2 como segundo termo do clock, ou um 74LS373 no lugar do 175 com latch fechando na descida do enable.<br/>&bull; <b>Escritas em byte:</b> escrever em $FC0000 só com /UDS (byte alto) também clocka o registrador, com D0-D2 sem sentido. Para trocar de banco use sempre <b>palavra</b> (move.w) ou byte em $FC0001.<br/>&bull; <b>Primeiro uso:</b> o banco 1 está vazio (todo $FF): um salto para ele trava a CPU. Por isso a primeira troca é feita por um programa de teste na RAM que volta ao banco 0 antes de qualquer coisa.<br/>&bull; <b>Antes de ligar:</b> sem curto entre +5 V e GND, pinos 12 e 13 do 74LS32 fora do GND, e as três redes A16/A17/A18 sem curto com +5 V.', P)]
doc.build(S)
