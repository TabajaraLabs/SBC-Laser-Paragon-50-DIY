from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer,PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import glob
d='/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('S',d+'DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('SB',d+'DejaVuSans-Bold.ttf'))
AZ=colors.HexColor('#12355b')
P=ParagraphStyle('p',fontName='S',fontSize=9,leading=12.5)
H=ParagraphStyle('h',fontName='SB',fontSize=13,leading=17,textColor=AZ,spaceBefore=6,spaceAfter=4)
T=ParagraphStyle('t',fontName='SB',fontSize=17,leading=21,textColor=AZ)
C=ParagraphStyle('c',fontName='S',fontSize=8.2,leading=10.2)
def tab(rows,w,hl=()):
    HC=ParagraphStyle('hh',parent=C,fontName='SB',textColor=colors.white)
    r=[[Paragraph(str(c),HC if k==0 else C) for c in row] for k,row in enumerate(rows)]
    t=Table(r,colWidths=[x*mm for x in w],repeatRows=1)
    st=[('BACKGROUND',(0,0),(-1,0),AZ),('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#b8c2cf')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2)]
    for i,row in enumerate(rows):
        if i==0: st.append(('TEXTCOLOR',(0,0),(-1,0),colors.white))
        elif row[1].strip()=='GND': st.append(('BACKGROUND',(0,i),(-1,i),colors.HexColor('#eceff3')))
    t.setStyle(TableStyle(st))
    return t
S=[]
S.append(Paragraph('PARAGON 50 — E/S livres e distribuição em dois DB-25 (v1)',T))
S.append(Paragraph('Premissas: LCD 40×4 via backpack PCF8574 (usa o barramento I²C que já existe), cartão SD, buzzer, DS1307 e encoder permanecem; nada de barramento de dados, endereços ou seleções (Yx). Tudo baseado nos mapas medidos de J1 e J2 (docs/Mapa_J1_J2_porta_020018.txt, Mapa_entradas_J1.txt e pins.json).',P))
S.append(Paragraph('1. O que continua ocupado',H))
S.append(tab([['Função','Sinal','Conector-pino','Origem'],
['SD','SCK','J1-28','$020018 b0'],['SD','MOSI','J1-26','$020018 b1'],['SD','CS','J1-24','$020018 b2'],
['SD','MISO','J1-7','porta B b0 ($020028)'],['SD','detecção do cartão (opcional)','J1-27','porta B b4'],
['Buzzer','BEEPER','J2-40','$020018 b9'],
['Encoder','botão','J1-31','porta B b3'],['Encoder','EN1','J1-33','porta B b2'],['Encoder','EN2','J1-35','porta B b1'],
['I²C (DS1307 + PCF8574)','SCL','J1-30','$020020 b10 (coletor aberto, invertida)'],
['I²C','SDA (saída)','J1-48','$020020 b7 (coletor aberto, invertida)'],
['I²C','SDA (leitura)','J1-23','porta B b6'],
['Analógico','S1–S8 e DACs A/B','J2-1 a J2-21 (ímpares), retornos AGND nos pares','não faz parte da expansão digital'],
['Terra','GND','J1-1, 2, 9, 50; J2-49, 50','']],[38,38,45,60]))
S.append(Paragraph('2. O que o backpack libera',H))
S.append(Paragraph('Os 6 bits que ligavam o LCD (E, RS, D4–D7) deixam de ser usados: $020018 b3 a b8 (J1-20, 18, 15, 14, 10 e J2-47). O DS1302 provisório que usava J2-37 também já saiu (substituído pelo DS1307 em I²C).',P))
S.append(Paragraph('3. Total disponível',H))
S.append(tab([['Tipo','Quantidade','Pinos'],
['Saídas TTL push-pull ($020018)','12','b3–b8: J1-20, 18, 15, 14, 10, J2-47 · b10–b15: J2-37, 30, 28, 27, 24, 23'],
['Entradas porta A ($020030, 16 bits)','16','J2-39, 42, 41, J1-4, J2-43, 45, 46, 48, 29, 32, 31, 34, 33, 36, 35, 38 (b0 a b15)'],
['Entradas porta B ($020028)','2','B5 = J1-25 · B7 = J1-34'],
['Entrada IP3 do DUART','1','J1-38 (direta, sem inversão)'],
['Saída OUT2 do timer 8254','1','J1-11'],
['Inversor livre do 74LS06 (coletor aberto)','1','entrada J1-12, saída J1-32 (precisa de pull-up)']],[55,22,100]))
S.append(Paragraph('Total: 12 saídas + 19 entradas + 3 pinos auxiliares. Observações elétricas: as saídas do $020018 são TTL sem driver (nível alto ≈ 4,3 V, LS: 8 mA em baixa, 0,4 mA em alta); as portas A e B passam por 74LS240 inversores com pull-up de 4,7 kΩ, então pino aterrado = bit 1; o IP3 do DUART e o OUT2 do 8254 são diretos.',P))
S.append(PageBreak())
S.append(Paragraph('4. DB-25 nº 1 — SAÍDAS (conector macho)',H))
o=[['Pino DB-25','Sinal','Origem','Pino na placa'],
['1','GND','',''],['2','OUT0','$020018 b3','J1-20'],['3','OUT1','$020018 b4','J1-18'],['4','OUT2','$020018 b5','J1-15'],['5','OUT3','$020018 b6','J1-14'],['6','OUT4','$020018 b7','J1-10'],['7','OUT5','$020018 b8','J2-47'],
['8','GND','',''],['9','OUT6','$020018 b10','J2-37'],['10','OUT7','$020018 b11','J2-30'],['11','OUT8','$020018 b12','J2-28'],['12','OUT9','$020018 b13','J2-27'],
['13','GND','',''],['14','OUT10','$020018 b14','J2-24'],['15','OUT11','$020018 b15','J2-23'],['16','TIMER2','OUT2 do 8254','J1-11'],
['17','GND','',''],['18','INV_IN','74LS06 livre (entrada)','J1-12'],['19','INV_OUT','74LS06 livre (coletor aberto)','J1-32'],
['20','GND','',''],['21','+5 V (opcional)','via PTC de 200 mA, do trilho de 5 V',''],['22','reserva','',''],['23','reserva','',''],['24','reserva','',''],['25','GND','','']]
S.append(tab(o,[24,32,60,40]))
S.append(PageBreak())
S.append(Paragraph('5. DB-25 nº 2 — ENTRADAS (conector fêmea)',H))
i=[['Pino DB-25','Sinal','Origem','Pino na placa'],
['1','GND','',''],['2','IN0','porta A b0','J2-39'],['3','IN1','porta A b1','J2-42'],['4','IN2','porta A b2','J2-41'],['5','IN3','porta A b3','J1-4'],['6','IN4','porta A b4','J2-43'],['7','IN5','porta A b5','J2-45'],
['8','GND','',''],['9','IN6','porta A b6','J2-46'],['10','IN7','porta A b7','J2-48'],['11','IN8','porta A b8','J2-29'],['12','IN9','porta A b9','J2-32'],
['13','GND','',''],['14','IN10','porta A b10','J2-31'],['15','IN11','porta A b11','J2-34'],['16','IN12','porta A b12','J2-33'],['17','IN13','porta A b13','J2-36'],
['18','GND','',''],['19','IN14','porta A b14','J2-35'],['20','IN15','porta A b15','J2-38'],['21','IN16','porta B b5','J1-25'],['22','IN17','porta B b7','J1-34'],['23','IN18','IP3 do DUART','J1-38'],
['24','+5 V (opcional)','via PTC de 200 mA',''],['25','GND','','']]
S.append(tab(i,[24,32,60,40]))
S.append(Paragraph('6. Recomendações para a placa adaptadora',H))
S.append(Paragraph('• Saídas: buffer 74HCT541 ou 74LS244 entre o latch e o DB-25, com resistor de 100–330 Ω em série; as saídas do latch não aguentam carga real. • Entradas: resistor em série de 470 Ω–1 kΩ e diodos de proteção (clamp para +5 V e GND) ou TVS; lembrar que o nível lógico é invertido nas portas A/B. • Macho nas saídas e fêmea nas entradas, e etiquetas bem visíveis: DB-25 também é porta paralela e serial, e ligar um desses por engano é a causa mais comum de estragos. • Tudo é TTL de 5 V: nada de 12 V, RS-232 nem sinal analógico nesses conectores. • Pinos de J1/J2 não listados não estão conectados (confirmado nos testes de 15/11). • J1-11 (OUT2 do 8254): confirmar que nada da placa depende dele antes de expor.',P))
SimpleDocTemplate('Paragon50_Expansao_DB25_v1.pdf',pagesize=A4,leftMargin=15*mm,rightMargin=15*mm,topMargin=14*mm,bottomMargin=14*mm,title='PARAGON 50 - Expansao DB-25 v1').build(S)
