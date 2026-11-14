# -*- coding: utf-8 -*-
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, PageBreak

# 27C512 DIP-28 -> nome do sinal; flash = pino socket + 2 (1..27), VCC 28 -> 32
n27 = {1:'A15',2:'A12',3:'A7',4:'A6',5:'A5',6:'A4',7:'A3',8:'A2',9:'A1',10:'A0',11:'D0',12:'D1',13:'D2',14:'GND',
       15:'D3',16:'D4',17:'D5',18:'D6',19:'D7',20:'/CE',21:'A10',22:'/OE',23:'A11',24:'A9',25:'A8',26:'A13',27:'A14',28:'VCC'}
nfl = {1:'A18',2:'A16',3:'A15',4:'A12',5:'A7',6:'A6',7:'A5',8:'A4',9:'A3',10:'A2',11:'A1',12:'A0',13:'DQ0',14:'DQ1',15:'DQ2',16:'VSS',
       17:'DQ3',18:'DQ4',19:'DQ5',20:'DQ6',21:'DQ7',22:'CE#',23:'A10',24:'OE#',25:'A11',26:'A9',27:'A8',28:'A13',29:'A14',30:'A17',31:'WE#',32:'VDD'}
# ---- figura: adaptador ----
fig, ax = plt.subplots(figsize=(10, 7.4)); ax.set_xlim(0, 100); ax.set_ylim(0, 74); ax.axis('off')
ax.text(50, 71.5, 'Adaptador: plugue 28 pinos (vai no soquete da ROM)  ->  Am29F040B em DIP-32', ha='center', fontsize=10, weight='bold')
# flash no centro
ax.add_patch(Rectangle((38, 8), 24, 58, fc='#fdf6d8', ec='k', lw=1.3)); ax.text(50, 67, 'Am29F040B-90 (DIP-32)', ha='center', fontsize=9, weight='bold')
y0 = 63.0; dy = 3.4
def col(p): return y0 - (p-1)*dy if p <= 16 else y0 - (32-p)*dy
for p in range(1, 33):
    y = col(p); left = p <= 16
    x = 38 if left else 62
    ex = {1:'#1f5fbf',2:'#1f5fbf',30:'#1f5fbf',31:'#b00000',32:'#b00000',16:'k'}.get(p)
    c = ex or '#555555'
    ax.plot([x-6, x] if left else [x, x+6], [y, y], color=c, lw=1.6 if ex else 0.9)
    if left: ax.text(x+1, y, f'{p} {nfl[p]}', va='center', fontsize=7.5, color=c)
    else: ax.text(x-1, y, f'{nfl[p]} {p}', va='center', ha='right', fontsize=7.5, color=c)
# rotulos de origem (socket n -> flash n+2)
for p in range(3, 30):
    s = p-2
    y = col(p); left = p <= 16
    if left: ax.text(31, y, f'soq.{s} {n27[s]}', ha='right', va='center', fontsize=6.8, color='#333333')
    else: ax.text(69, y, f'soq.{s} {n27[s]}', ha='left', va='center', fontsize=6.8, color='#333333')
ax.text(31, col(1), 'A18 -> GND (banco)', ha='right', va='center', fontsize=7.2, color='#1f5fbf', weight='bold')
ax.text(31, col(2), 'A16 -> GND (banco)', ha='right', va='center', fontsize=7.2, color='#1f5fbf', weight='bold')
ax.text(69, col(30), 'A17 -> GND (banco)', ha='left', va='center', fontsize=7.2, color='#1f5fbf', weight='bold')
ax.text(69, col(31), 'WE# -> +5 V (passo 1)', ha='left', va='center', fontsize=7.2, color='#b00000', weight='bold')
ax.text(69, col(32), 'VDD <- soq.28 VCC  + 100 nF', ha='left', va='center', fontsize=7.2, color='#b00000', weight='bold')
ax.text(31, col(16), 'soq.14 GND', ha='right', va='center', fontsize=6.8)
ax.text(50, 3.5, 'Regra: pino do soquete n  =  pino da flash n+2 (n = 1 a 27).  Só o VCC foge da regra: soquete 28 -> flash 32.', ha='center', fontsize=8.5, style='italic')
ax.text(50, 0.6, 'Atenção: a flash 30 (A17) fica na mesma coluna do soquete 28 (VCC): NÃO ligue em linha reta, use fios.', ha='center', fontsize=8.5, color='#b00000')
fig.savefig('adaptador_am29f040b_v2.png', dpi=170, bbox_inches='tight'); plt.close(fig)

# ---- PDF ----
ss = getSampleStyleSheet()
H = ParagraphStyle('h', parent=ss['Title'], fontSize=15, spaceAfter=2)
H2 = ParagraphStyle('h2', parent=ss['Heading2'], fontSize=11, spaceBefore=7, spaceAfter=3)
P = ParagraphStyle('p', parent=ss['BodyText'], fontSize=8.8, leading=11.4)
C = ParagraphStyle('c', parent=P, fontSize=8.3, leading=10.2)
W = ParagraphStyle('w', parent=P, backColor=colors.HexColor('#fff1d6'), borderPadding=4, borderColor=colors.HexColor('#d99a2b'), borderWidth=0.6, spaceBefore=4, spaceAfter=4)
def tbl(rows, w):
    data = [[Paragraph(str(c), C) for c in r] for r in rows]
    t = Table(data, colWidths=[x*mm for x in w], repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dbe4f0')), ('GRID', (0,0), (-1,-1), 0.4, colors.grey), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    return t
doc = SimpleDocTemplate('Paragon50_Guia_ROM_Flash_Am29F040B_v2.pdf', pagesize=A4, leftMargin=14*mm, rightMargin=14*mm, topMargin=12*mm, bottomMargin=12*mm, title='PARAGON 50 - ROM em flash Am29F040B-90, passo 1 (v2)')
S = [Paragraph('PARAGON 50 &ndash; ROM em flash Am29F040B-90, passo 1', H),
Paragraph('Tabajara Labs &middot; guia v2 &middot; 13/11/2026. Troca as duas 27C512 (a ROM HI, byte alto, e a ROM LO, byte baixo) por duas Am29F040B-90 em adaptadores, <b>sem nenhuma outra mudança na placa</b>. Neste passo a flash só imita uma 27C512 maior: o computador roda igual ao de hoje, e o adaptador fica pronto para as etapas seguintes (escrita no circuito e troca de bancos). Pinagem, comandos e tempos conferidos no datasheet AMD/Spansion Am29F040B (pub. 21445). A pinagem DIP-32 é a mesma da SST39SF040, que também serviria neste passo. O texto do datasheet que consegui ler veio com o diagrama embaralhado, então <b>confira o pino 1 (A18), o 30 (A17) e o 31 (WE#) no PDF do seu fabricante</b> antes de soldar.', P),
Paragraph('<b>Segurança:</b> neste passo o WE# (pino 31) vai fixo em +5 V, então <b>nada escreve na flash</b> e a placa não tem como estragá-la. As 27C512 originais ficam guardadas: desfazer é só trocar os chips.', W),
Image('adaptador_am29f040b_v2.png', width=150*mm, height=150*mm*7.4/10*1.0),
Paragraph('Tabela de ligações (um adaptador; faça dois iguais)', H2),
tbl([['Soquete 27C512', 'Flash Am29F040B', 'Sinais', 'Observação'],
['1 a 13', '3 a 15', 'A15, A12, A7...A0, D0, D1, D2', 'pino do soquete + 2'],
['14', '16', 'GND', ''],
['15 a 27', '17 a 29', 'D3...D7, /CE, A10, /OE, A11, A9, A8, A13, A14', 'pino do soquete + 2'],
['28', '32', 'VCC / VDD', 'capacitor de 100 nF entre 32 e 16, bem perto da flash'],
['&ndash;', '1, 2, 30', 'A18, A16, A17 (bits de banco)', '<b>GND</b>, cada um por um pad ou jumper, para ligar à placa depois'],
['&ndash;', '31', 'WE#', '<b>+5 V</b>, por um pad ou jumper (passo 2 troca por /WE vindo da lógica)']], [32, 32, 62, 56])]
S += [PageBreak(), Paragraph('Passo a passo', H2),
Paragraph('<b>1. Montar.</b> Os dois encapsulamentos têm 600 mil entre as fileiras, então servem na mesma placa. Use uma placa perfurada de pontos individuais: um <b>plugue de 28 pinos</b> (pinos torneados) em uma face e um <b>soquete DIP-32</b> na outra, deslocado de 2 furos, de modo que o pino n do plugue fique na mesma coluna do pino n+2 do soquete. Ligue as linhas retas da tabela, depois o VCC em fio (28 do plugue ao 32 da flash) e os quatro pads de banco e WE#.', P),
Paragraph('<b>2. Testar o adaptador sem a flash.</b> Multímetro em continuidade: cada pino do plugue ao pino certo do soquete, VCC e GND sem curto, A18, A16, A17 em GND e WE# em +5 V.', P),
Paragraph('<b>3. Gravar.</b> Escolha a Am29F040B no gravador (o ID é 01 / A4). Os arquivos prontos têm 512 KB e repetem a imagem v2.3 oito vezes: <b>PARAGON_V2.3_HI_AM29F040B_512K_x8copias.bin</b> para a posição HI e <b>PARAGON_V2.3_LO_AM29F040B_512K_x8copias.bin</b> para a posição LO. Com A16, A17 e A18 em GND só o banco 0 aparece, mas com as oito cópias a placa continua certa mesmo que um desses pinos fique solto ou mal ligado. Confira o CRC lido de volta: HI = imagem de 64 KB com CRC32 DF01811B, LO = 74CB7559 (cada cópia).', P),
Paragraph('<b>4. Instalar.</b> Desligada a placa, tire as duas 27C512 e coloque cada adaptador (cada um na posição que tinha a ROM de mesmo nome, HI ou LO, pino 1 do plugue no mesmo lado do pino 1 do soquete). Ligue: tem que aparecer a mesma mensagem de boot de antes. Teste <b>CP/M</b>, <b>EhBASIC</b> e <b>Tetris</b>.', P),
Paragraph('<b>5. Se não subir:</b> primeiro VCC e GND no adaptador, depois a ordem HI/LO (invertidos dão lixo), depois os pinos 1, 2 e 30 realmente em GND.', P),
Paragraph('O que vem depois', H2),
tbl([['Passo', 'O que muda', 'Pré-requisito'],
['2 &ndash; escrever no circuito', 'WE# de cada flash vem de uma porta OR: /WE = R/W + ROM_CE + /UDS (alto) ou /LDS (baixo), com um jumper que mantém o WE# em +5 V no uso normal', 'rastrear o /DTACK de escrita na região da ROM'],
['3 &ndash; trocar de banco', 'A16, A17 e A18 passam a ser saídas de um latch com limpeza no reset. Na Am29F040B esses três bits são o endereço do setor: <b>1 banco = 1 setor de 64 KB por chip</b>', 'achar bits livres, ou usar um 74LS175 com reset'],
['4 &ndash; programa de atualização', 'rotina que roda da RAM: ID, apagar setor (cerca de 1 s), gravar byte; <b>o banco 0 fica reservado ao boot e nunca é apagado</b>', 'passos 2 e 3']], [38, 98, 46]),
Paragraph('Comandos da Am29F040B (datasheet, endereços de 11 bits baixos)', H2),
tbl([['Comando', 'Sequência (endereço da flash / dado)'],
['Reset (volta a ler)', 'qualquer endereço / F0'],
['ID (autoselect)', '555/AA, 2AA/55, 555/90; ler X00 = 01 (AMD) e X01 = A4; depois reset com F0'],
['Gravar byte', '555/AA, 2AA/55, 555/A0, endereço/dado (típico 7 us; até 300 us)'],
['Apagar setor de 64 KB', '555/AA, 2AA/55, 555/80, 555/AA, 2AA/55, setor/30 (típico 1 s; até 8 s; A16 a A18 escolhem o setor)'],
['Apagar chip', '555/AA, 2AA/55, 555/80, 555/AA, 2AA/55, 555/10 (típico 8 s; até 64 s)'],
['Fim de operação', 'polling de DQ7 (lê o complemento do dado até terminar); DQ5 = 1 indica falha: dar reset (F0)']], [38, 144]),
Paragraph('Esses endereços são da flash. No Paragon as linhas A13, A14 e A15 passam por inversores (74LS14 U26) antes de chegar à ROM, então o endereço do 68000 que cai em 555H da flash é outro; o ID (autoselect) lido de volta confirma o mapeamento antes de qualquer apagamento.', P),
Paragraph('Fonte: AMD/Spansion Am29F040B, pub. 21445 (pinagem DIP-32, comandos, ID, tempos); velocidade -90: tACC e tCE 90 ns, tOE 35 ns, tDF 20 ns. Nada neste passo foi testado na placa.', C)]
doc.build(S)
