from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer,PageBreak,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
d='/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('S',d+'DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('SB',d+'DejaVuSans-Bold.ttf'))
AZ=colors.HexColor('#12355b');LA=colors.HexColor('#d9731a')
P=ParagraphStyle('p',fontName='S',fontSize=9.4,leading=13.2,spaceAfter=3)
B=ParagraphStyle('b',parent=P,leftIndent=10,bulletIndent=0)
H=ParagraphStyle('h',fontName='SB',fontSize=13.5,leading=17,textColor=AZ,spaceBefore=10,spaceAfter=4)
T=ParagraphStyle('t',fontName='SB',fontSize=18,leading=22,textColor=AZ)
C=ParagraphStyle('c',fontName='S',fontSize=8.6,leading=11)
HC=ParagraphStyle('hh',parent=C,fontName='SB',textColor=colors.white)
def tab(rows,w):
    r=[[Paragraph(str(c),HC if k==0 else C) for c in row] for k,row in enumerate(rows)]
    t=Table(r,colWidths=[x*mm for x in w],repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),AZ),('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#b8c2cf')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),2.5),('BOTTOMPADDING',(0,0),(-1,-1),2.5)]))
    return t
def bl(items): return [Paragraph(i,B,bulletText='•') for i in items]
def caixa(t):
    x=Table([[Paragraph(t,P)]],colWidths=[175*mm]); x.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#fff3e6')),('BOX',(0,0),(-1,-1),1,LA),('LEFTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),4)])); return x
S=[]
S.append(Paragraph('PARAGON 50 — Roteiro: LCD 20×4 via backpack I²C (PCF8574), já preparado para o 40×4',T))
S.append(Paragraph('Versão 1 · 16/11/2026',P))
S.append(Spacer(1,3*mm))
S.append(Paragraph('1. Ideia central',H))
S.append(Paragraph('O LCD sai dos 6 fios paralelos de hoje (J1/J2) e passa a ser escrito pelo mesmo barramento I²C do relógio DS1307 (SCL = J1-30, SDA de saída = J1-48, SDA de leitura = J1-23). Para que a troca por um 40×4 seja só uma configuração, o driver nasce com três parâmetros: <b>número de colunas</b> (20 ou 40), <b>número de controladores</b> (1 ou 2) e <b>qual bit do PCF8574 faz o Enable de cada linha</b>. O 20×4 usa um controlador e o Enable E1 (P2). O 40×4 usa dois controladores: as linhas 1 e 2 em E1 (P2) e as linhas 3 e 4 em E2 (P1, que no 40×4 fica livre porque o R/W do LCD vai ao GND).',P))
S.append(caixa('<b>Regra de ouro:</b> o serviço de LCD que o monitor e os programas já usam (entrada $F80614 e o relógio da linha 4) <b>não muda de interface</b>. Só troca o que está por trás dele: ou o caminho paralelo antigo ou o novo I²C. Nada do que já funciona precisa ser reescrito.'))
S.append(Paragraph('2. O que juntar antes (lista de verificação)',H))
S+=bl(['LCD 20×4 com controlador HD44780 (módulo 2004A ou equivalente), de 5 V.',
'Backpack com PCF8574 (endereço $20 a $27) ou PCF8574A ($38 a $3F). O mais comum vem em $27 ou $3F.',
'4 fios curtos (até uns 30 cm): +5 V, GND, SCL e SDA. Uma alimentação de 5 V decente para a luz de fundo (100 a 250 mA).',
'Paquímetro: medir o seu módulo (contorno, área visível, furos) antes de fechar a moldura do gabinete.',
'Fio fino, ferro de solda e estilete, para o futuro fio E2 do 40×4. Não precisa mexer nisso agora.',
'Fotos das duas faces do backpack e da traseira do LCD. Com elas eu confiro a ordem dos bits antes de você ligar.'])
S.append(Paragraph('3. Fase 0 — Conferir o backpack (placa desligada)',H))
S.append(tab([['O que olhar','Esperado','Por que importa'],
['Marcação do chip','PCF8574 ou PCF8574A','define a faixa de endereços'],
['Jumpers A0, A1, A2','abertos = 1 (pull-up) na maioria','define o endereço exato'],
['Ordem dos bits (P0 a P7 → pinos do LCD)','P0=RS, P1=R/W, P2=E, P3=luz, P4–P7=D4–D7','é a ordem do backpack mais comum; há variantes'],
['Pull-ups no SDA e SCL','4,7 kΩ ou 10 kΩ','somam em paralelo com os do módulo do relógio'],
['Pino R/W do LCD','ligado ao P1 (ou ao GND)','o driver só escreve; P1 será o E2 no 40×4']],[58,60,57]))
S.append(Paragraph('4. Fase 1 — Ligação e primeiro teste',H))
S.append(tab([['Backpack','Placa PARAGON 50','Observação'],
['GND','J1-9','mesmo GND do relógio'],['VCC','+5 V (J7-19)','luz de fundo exige fio decente'],
['SCL','J1-30','paralelo com o DS1307'],['SDA','J1-48 e J1-23','os dois emendados, como no relógio']],[40,45,90]))
S.append(Paragraph('Teste de varredura: com a placa no prompt do monitor, rodo o comando <b>RTC TESTE</b> (ou RTC SCAN), que já existe e varre o barramento I²C de $08 a $77. Esperado: <b>$68</b> (relógio) e o endereço do backpack. Se só aparecer o $68, as causas prováveis são: SDA ou SCL invertidos, GND sem ligar, ou backpack com o chip em outra faixa. Eu assumo o controle dessa parte e só te peço onde encostar a ponta de prova, um passo por vez, conferindo antes de cada medição que o programa da placa continua rodando.',P))
S.append(Paragraph('5. Fase 2 — Software (feito no emulador antes de tocar a placa)',H))
S+=bl(['<b>Driver I²C do LCD</b> com parâmetros no topo do arquivo: LCD_COLS (20/40), LCD_CTRL (1/2), tabela de endereços de linha (20×4: $00, $40, $14, $54; 40×4: $00 e $40 em cada controlador), máscaras de bits (RS, E1, E2, luz).',
'<b>Transação em lote:</b> cada caractere vai em um único START/STOP com 4 bytes (nibble alto com E=1 e E=0, nibble baixo com E=1 e E=0). Estimativa: cerca de 0,4 ms por caractere no bit-bang; a tela cheia do 20×4 fica em torno de 35 ms e a do 40×4 em torno de 70 ms.',
'<b>Inicialização de 4 bits</b> com os tempos do HD44780: $3, $3, $3, $2, depois $28, $0C, $06, $01 (limpar), com espera de 2 ms após o limpar. No 40×4, repetir para o segundo controlador.',
'<b>Autodetecção:</b> na partida, procurar $27 e $3F. Se achar, usa o caminho I²C; se não achar, mantém o caminho paralelo antigo. Assim a placa continua funcionando com o LCD da RepRap enquanto você monta.',
'<b>Compatibilidade:</b> o relógio da linha 4, o menu de bancos e as mensagens do monitor continuam usando o serviço $F80614. A linha 4 do 20×4 passa a ser a última do 40×4, sem mudar o código do relógio.',
'<b>Comando de configuração:</b> LCD [20|40] escolhe a geometria sem recompilar; sem o argumento mostra a configuração atual e o endereço detectado.',
'<b>Modelo no emulador:</b> estender o emu68k.py com um PCF8574 + HD44780 simulados (mostrando o texto no terminal) para validar a lógica antes de gravar.'])
S.append(Paragraph('6. Fase 3 — Gravação e verificação na placa',H))
S+=bl(['Gravar em um banco de teste (2 a 7), nunca no banco 0, e só promover ao banco 1 depois de passar em tudo.',
'Se algo travar: reset e tecla R para o menu de recuperação (o banco 0 continua intacto).',
'Sequência de testes: (1) varredura I²C; (2) texto nas 4 linhas; (3) luz de fundo liga e desliga; (4) contraste no trimpot; (5) relógio na linha 4 por 10 minutos; (6) menu de bancos e mensagens de boot; (7) ler o cartão SD enquanto o LCD atualiza; (8) aquecer: 30 minutos ligado e conferir se o I²C do relógio continua respondendo.'])
S.append(Paragraph('7. Gabinete do 20×4 pensado para receber o 40×4',H))
S+=bl(['Faça a <b>moldura da janela (bisel) como peça separada</b>, presa à tampa por parafusos ou encaixe. Trocar para o 40×4 passa a ser reimprimir só o bisel (e talvez o suporte do LCD), e não o gabinete inteiro.',
'Dimensões típicas para conferir com o paquímetro: LCD 20×4 com contorno de cerca de 98×60 mm, área visível de cerca de 76×26 mm e furos de fixação de cerca de 93×55 mm. LCD 40×4 com contorno de cerca de 190×54 mm (conferir no datasheet do módulo que você comprar).',
'Reserve na tampa a <b>profundidade</b> do LCD com o backpack (módulo + placa I²C, perto de 20 a 25 mm). O backpack fica atrás e não pode encostar na placa-mãe nem nos furos de montagem.',
'A janela do 40×4 é bem mais larga que a do 20×4: veja na planta do gabinete v2 se o painel superior comporta 190 mm de largura útil e a altura necessária, para saber de antemão se o 40×4 cabe no mesmo gabinete.',
'Deixe uma abertura para o cabo flat de 4 fios do backpack e para o fio de 5 V da luz de fundo.'])
S.append(Paragraph('8. Fase 4 — Migração para o 40×4 (quando achar o módulo)',H))
S.append(tab([['Passo','O que fazer'],
['1','Achar o código do módulo (WH4004, LCD4004…) e o datasheet: confirmar qual pino é o E2 e onde ficam os pinos da luz de fundo'],
['2','R/W do LCD ao GND; cortar ou isolar a trilha do P1 ao R/W na backpack (ou ligar tudo por fio, sem o conector da backpack)'],
['3','Fio do P1 ao E2 do LCD'],
['4','Luz de fundo com alimentação própria (200 a 500 mA), com transistor se o seu módulo usar o P3'],
['5','No monitor: LCD 40; reiniciar; refazer os testes da fase 3'],
['6','Trocar o bisel impresso e o suporte do LCD no gabinete']],[15,160]))
S.append(Paragraph('9. Pontos em aberto',H))
S+=bl(['Modelo exato do backpack e do módulo 20×4 que você vai usar (para fechar a ordem dos bits e as medidas do bisel).',
'Corrente real da luz de fundo do módulo (medir na bancada com a fonte).',
'Comportamento do relógio e do LCD compartilhando o barramento com cabos mais longos (se precisar, reduzo a velocidade do bit-bang).',
'Se o SD e o encoder continuarão na placa RepRap ou irão para módulos separados: isso decide o que sai de J1 e J2 e como fica o gabinete.'])
SimpleDocTemplate('Paragon50_Roteiro_LCD_I2C_v1.pdf',pagesize=A4,leftMargin=17*mm,rightMargin=17*mm,topMargin=15*mm,bottomMargin=15*mm,title='PARAGON 50 - Roteiro LCD I2C v1').build(S)
