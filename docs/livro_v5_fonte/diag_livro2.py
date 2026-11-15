import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon, Arc
from matplotlib import font_manager as fm
for f in ('DejaVuSans.ttf','DejaVuSans-Bold.ttf','DejaVuSansMono.ttf'): fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/'+f)
plt.rcParams['font.family']='DejaVu Sans'; plt.rcParams['text.parse_math']=False
AZUL='#12355b'; LARA='#d9731a'; CINZA='#eef1f5'; CINZA2='#c9d1dc'; VERDE='#2f7d4f'; VERM='#b3362d'; TXT='#1d2733'
exec(''.join(open('diagramas.py').read().split('\n')[10:19]).replace('\n','\n') if False else '\n'.join(open('diagramas.py').read().split('\n')[10:19]))
def salva(fig,n): fig.savefig('img/'+n+'.png',dpi=200,bbox_inches='tight',facecolor='white'); plt.close(fig)
def fio(ax,pts,cor=AZUL,lw=1.5,ls='-'): ax.plot([p[0] for p in pts],[p[1] for p in pts],color=cor,lw=lw,ls=ls,solid_capstyle='round')
def pino(ax,x,y,t,lado='l',fs=7.4,cor=TXT):
    ax.text(x,y,t,fontsize=fs,color=cor,ha='right' if lado=='l' else 'left',va='center')
def porta_or(ax,x,y,w=0.9,h=0.7,cor=AZUL,rot=''):
    ax.add_patch(Polygon([[x,y],[x+w*0.55,y],[x+w,y+h/2],[x+w*0.55,y+h],[x,y+h],[x+w*0.22,y+h/2]],closed=True,fc='#e9eff7',ec=cor,lw=1.5))
    ax.text(x+w*0.46,y+h/2,rot,fontsize=7,ha='center',va='center',color=cor,fontweight='bold')

# ---------- A. registrador de banco ----------
fig,ax=novo(10,5.6)
caixa(ax,0.2,0.9,1.9,3.8,'',fc='#f4f6f9',ec=AZUL)
ax.text(1.15,4.45,'CPU 68000',ha='center',fontsize=10,fontweight='bold',color=AZUL)
for i,(n,p) in enumerate([('D0','5'),('D1','4'),('D2','3')]):
    y=3.7-i*0.55; fio(ax,[(2.1,y),(4.4,y),(4.4,3.45-i*0.4),(5.0,3.45-i*0.4)]); ax.text(2.2,y+0.1,n+'  (pino '+p+')',fontsize=7.4,color=TXT)
ax.text(1.15,2.0,'R/W  pino 9',ha='center',fontsize=7.8); fio(ax,[(2.1,2.0),(3.3,2.0)],cor=LARA)
ax.text(1.15,1.5,'/RESET  pino 18',ha='center',fontsize=7.8); fio(ax,[(2.1,1.5),(5.0,1.5)],cor=VERM)
caixa(ax,0.2,0.1,1.9,0.55,'U4 Y2 = $FC0000',fc='#fff3e6',ec=LARA,fs=7.4)
fio(ax,[(2.1,0.37),(3.1,0.37),(3.1,2.3),(3.3,2.3)],cor=LARA)
porta_or(ax,3.3,1.75,0.9,0.7,LARA,'OR')
ax.text(3.25,1.0,'74LS32 porta 4:\nCLK = Y2 OU R/W',fontsize=7,color=LARA,ha='left')
fio(ax,[(4.2,2.1),(4.7,2.1),(4.7,3.9),(5.0,3.9)],cor=LARA)
caixa(ax,5.0,1.2,1.9,3.4,'',fc='#e9eff7',ec=AZUL); ax.text(5.95,4.3,'74LS175',ha='center',fontsize=10,fontweight='bold',color=AZUL); ax.text(5.95,4.02,'registrador de 4 bits',ha='center',fontsize=7.4)
for t,y in (('CLK  9',3.9),('/CLR  1',1.5)): ax.text(5.1,y,t,fontsize=7.4,va='center')
for i,t in enumerate(('1D  4','2D  5','3D  12')): ax.text(5.1,3.45-i*0.4,t,fontsize=7.2,va='center')
for i,t in enumerate(('1Q  2','2Q  7','3Q  10')): ax.text(6.8,3.45-i*0.4,t,fontsize=7.2,va='center',ha='right')
for i,(a,pn) in enumerate((('A16','p.2'),('A17','p.30'),('A18','p.1'))):
    y=3.45-i*0.4; fio(ax,[(6.9,y),(7.1,y)],cor=VERDE,lw=2); ax.text(7.15,y,a+'  ('+pn+')',fontsize=7.6,va='center',color=VERDE); fio(ax,[(8.2,y),(8.7,y)],cor=VERDE)
caixa(ax,8.7,1.2,1.25,3.4,'2 × Am29F040B\n(HI e LO)\n\nA16..A18 =\nbanco\n\nA0..A15 =\nCPU A1..A16',fc='#e8f3ec',ec=VERDE,fs=6.9)
ax.text(5.0,0.65,'Reset zera o registrador: o computador sempre parte do banco 0.\nEscrever em $FC0000 (move.w #n,$FC0000) escolhe o banco n (0–7).',fontsize=8.2,color=TXT)
salva(fig,'c_banco175')

# ---------- B. circuito de escrita /WE ----------
fig,ax=novo(10,5.2)
ax.text(0.15,4.95,'Sinais da CPU (nível baixo = ativo)',fontsize=8.5,fontweight='bold',color=AZUL)
sig=[('R/W  (CPU pino 9)',4.4),('ROM_CE  (U5 pino 8)',3.9),('/UDS  (CPU pino 7)',2.75),('/LDS  (CPU pino 8)',1.55)]
for t,y in sig: ax.text(0.15,y,t,fontsize=8,va='center'); fio(ax,[(2.2,y),(2.9,y)])
porta_or(ax,2.9,3.75,1.0,0.8,AZUL,'OR'); fio(ax,[(2.9,4.4),(2.9+0.1,4.4)]); 
fio(ax,[(2.2,4.4),(2.95,4.4)]); fio(ax,[(2.2,3.9),(2.95,3.9)])
fio(ax,[(3.9,4.15),(4.4,4.15),(4.4,2.75+0.2),(4.9,2.95)]); fio(ax,[(4.4,4.15),(4.4,1.55+0.2),(4.9,1.75)])
ax.text(4.45,3.5,'X',fontsize=9,fontweight='bold',color=LARA)
porta_or(ax,4.9,2.6,1.0,0.8,AZUL,'OR'); fio(ax,[(2.2,2.75),(4.9,2.75)])
porta_or(ax,4.9,1.4,1.0,0.8,AZUL,'OR'); fio(ax,[(2.2,1.55),(4.9,1.55)])
for y0,nome,pn in ((3.0,'WE# HI','pino 6'),(1.8,'WE# LO','pino 8')):
    fio(ax,[(5.9,y0),(6.5,y0)]); ax.text(5.95,y0+0.12,pn,fontsize=6.8)
    ax.add_patch(Rectangle((6.5,y0-0.12),0.5,0.24,fc='white',ec=LARA,lw=1.4)); ax.text(6.75,y0+0.28,'jumper',fontsize=6.8,ha='center',color=LARA)
    fio(ax,[(7.0,y0),(8.3,y0)]); ax.text(8.25,y0+0.12,nome,fontsize=7.6,ha='right')
    sg=1 if y0>2.5 else -1
    ya=y0+sg*0.35; yb=y0+sg*0.95
    ax.add_patch(Rectangle((7.55,min(ya,yb)),0.2,0.6,fc='#f4f6f9',ec=TXT,lw=1)); ax.text(7.85,(ya+yb)/2,'4,7 kΩ',fontsize=6.8,va='center')
    fio(ax,[(7.65,y0),(7.65,ya)]); fio(ax,[(7.65,yb),(7.65,yb+sg*0.15)]); ax.text(7.65,yb+sg*0.3,'+5 V',fontsize=7,ha='center',va='center')
caixa(ax,8.3,1.5,1.5,2.1,'pino 31\nWE#\nda flash\n(HI / LO)',fc='#e8f3ec',ec=VERDE,fs=8)
ax.text(0.15,0.15,'WE# = R/W OU ROM_CE OU /UDS (ou /LDS): só cai quando os três estão baixos. Sem jumper, o pull-up mantém a flash sem escrita.',fontsize=7.8,color=TXT)
salva(fig,'c_escrita_we')

# ---------- C. temporização de escrita ----------
fig,ax=plt.subplots(figsize=(9,3.1)); ax.axis('off'); ax.set_xlim(0,12); ax.set_ylim(0,6)
def onda(y,pts,cor=AZUL,n=''):
    xs=[];ys=[]
    for x,v in pts: xs+= [x]; ys+=[y+v*0.55]
    ax.step(xs,ys,where='post',color=cor,lw=1.8); ax.text(-0.1,y+0.28,n,ha='right',va='center',fontsize=8)
onda(5,[(0,1),(2,0),(9,1),(12,1)],n='R/W')
onda(4,[(0,1),(2.2,0),(8.8,1),(12,1)],n='ROM_CE')
onda(3,[(0,1),(3.2,0),(7.6,1),(12,1)],n='/UDS')
onda(2,[(0,1),(3.2,0),(7.6,1),(12,1)],LARA,'WE# (HI)')
ax.add_patch(Rectangle((2.4,0.95),6.4,0.55,fc='#e9eff7',ec=AZUL,lw=1.4)); ax.text(5.6,1.22,'dado válido na D8–D15',ha='center',va='center',fontsize=8); ax.text(-0.1,1.22,'dado',ha='right',va='center',fontsize=8)
ax.annotate('',xy=(3.2,0.3),xytext=(7.6,0.3),arrowprops=dict(arrowstyle='<->',color=LARA)); ax.text(5.4,-0.15,'pulso de WE#: centenas de ns (flash: mín. dezenas)',ha='center',fontsize=8,color=LARA)
ax.plot([3.2,3.2],[0.3,5.5],color=LARA,ls=':',lw=1); ax.plot([7.6,7.6],[0.3,5.5],color=LARA,ls=':',lw=1)
ax.text(3.25,5.7,'flash trava o endereço',fontsize=7.4,color=LARA); ax.text(7.65,5.7,'trava o dado',fontsize=7.4,color=LARA)
salva(fig,'c_tempo_we')

# ---------- D. latch $020018 e $020020 ----------
fig,ax=novo(10,4.4)
def bits(y,titulo,itens,cores):
    ax.text(0.1,y+0.95,titulo,fontsize=9.5,fontweight='bold',color=AZUL)
    for i in range(16):
        b=15-i; x=0.3+i*0.6
        t,c=itens.get(b,('',None))
        ax.add_patch(Rectangle((x,y),0.57,0.7,fc=cores.get(c,'white'),ec=CINZA2 if c is None else AZUL,lw=1.2))
        ax.text(x+0.285,y+0.78,str(b),ha='center',fontsize=7,color='#566475')
        ax.text(x+0.285,y+0.35,t,ha='center',va='center',fontsize=6.3,color=TXT,linespacing=1.1)
cor={'lcd':'#e9eff7','sd':'#e8f3ec','bz':'#fff3e6','j2':'#f1f1f1','rtc':'#fdeaea','ad':'#fff9e0'}
bits(2.7,'Latch $020018  (saídas 74LS273 ×2)',{0:('SCK','sd'),1:('MOSI','sd'),2:('CS','sd'),3:('LCD\nE','lcd'),4:('LCD\nRS','lcd'),5:('D4','lcd'),6:('D5','lcd'),7:('D6','lcd'),8:('D7','lcd'),9:('beep','bz'),10:('J2\n37','j2'),11:('J2\n30','j2'),12:('J2\n28','j2'),13:('J2\n27','j2'),14:('J2\n24','j2'),15:('J2\n23','j2')},cor)
bits(0.9,'Latch $020020  (E/S auxiliar)',{7:('SDA\nRTC','rtc'),10:('SCL\nRTC','rtc'),12:('canal\nA/D','ad'),13:('canal\nA/D','ad'),14:('canal\nA/D','ad'),15:('A/D\nliga','ad')},cor)
ax.text(0.3,0.25,'azul: LCD · verde: cartão SD · laranja: buzzer · vermelho: relógio I²C · amarelo: conversor A/D · cinza: pinos livres em J2',fontsize=7.8,color=TXT)
salva(fig,'c_latches')

# ---------- E. SPI bit-bang ----------
fig,ax=plt.subplots(figsize=(9,3.4)); ax.axis('off'); ax.set_xlim(-1.2,17); ax.set_ylim(-0.3,7)
def clk(y,n,x0=0,per=2,cyc=8):
    xs=[x0];ys=[y]
    for i in range(cyc): xs+=[x0+i*per+per/2,x0+i*per+per/2,x0+(i+1)*per]; ys+=[y,y+0.6,y+0.6]; 
    # simple: build step
    pts=[];
    for i in range(cyc): pts+=[(x0+i*per,0),(x0+i*per+per/2,1)]
    pts+=[(x0+cyc*per,0)]
    ax.step([p[0] for p in pts],[y+p[1]*0.6 for p in pts],where='post',color=VERDE,lw=1.8); ax.text(-0.3,y+0.3,n,ha='right',va='center',fontsize=8)
ax.step([0,0.0,16.3,17],[6.6,6.0,6.6,6.6],where='post',color=AZUL,lw=1.8); ax.text(-0.3,6.3,'CS',ha='right',va='center',fontsize=8)
clk(4.7,'SCK')
bitsv=[1,0,1,0,0,1,0,1]
for nome,y,cor in (('MOSI',3.2,AZUL),('MISO',1.6,LARA)):
    pts=[(0,1)]; 
    for i,b in enumerate(bitsv): pts.append((i*2,b))
    pts.append((16,1))
    ax.step([p[0] for p in pts],[y+p[1]*0.6 for p in pts],where='post',color=cor,lw=1.8); ax.text(-0.3,y+0.3,nome,ha='right',va='center',fontsize=8)
    for i,b in enumerate(bitsv): ax.text(i*2+1,y+0.8 if nome=='MOSI' else y-0.35,str(b),ha='center',fontsize=7.4,color=cor)
for i in range(8): ax.plot([i*2+1,i*2+1],[1.5,5.6],color=VERDE,ls=':',lw=0.9)
ax.text(8,-0.25,'o 68000 gera cada transição escrevendo no latch $020018; o MISO é lido pela porta B ($020028)',ha='center',fontsize=7.8,color=TXT)
ax.text(1,5.45,'dado lido na subida do SCK (modo 0)',fontsize=7.2,color=VERDE)
salva(fig,'c_spi')

# ---------- F. LCD/RepRap ligação ----------
fig,ax=novo(10,5.5)
caixa(ax,0.2,0.05,2.6,5.3,'',fc='#f4f6f9',ec=AZUL); ax.text(1.5,5.05,'Placa PARAGON 50',ha='center',fontsize=10,fontweight='bold',color=AZUL)
caixa(ax,7.2,0.05,2.6,5.3,'',fc='#e9eff7',ec=AZUL); ax.text(8.5,5.05,'RepRapDiscount',ha='center',fontsize=10,fontweight='bold',color=AZUL)
ligs=[('J2-40','beep',LARA,'EXP1-1 BEEPER'),('J1-31','btn',VERDE,'EXP1-2 BTN_ENC'),('J1-20','b3',AZUL,'EXP1-3 LCD_EN'),('J1-18','b4',AZUL,'EXP1-4 LCD_RS'),('J1-15','b5',AZUL,'EXP1-5 LCD_D4'),('J1-14','b6',AZUL,'EXP1-6 LCD_D5'),('J1-10','b7',AZUL,'EXP1-7 LCD_D6'),('J2-47','b8',AZUL,'EXP1-8 LCD_D7'),
 ('J1-7','MISO',VERDE,'EXP2-1 MISO'),('J1-28','SCK',VERDE,'EXP2-2 SCK'),('J1-24','CS',VERDE,'EXP2-4 SD_CS'),('J1-26','MOSI',VERDE,'EXP2-6 MOSI')]
for i,(a,_,c,b) in enumerate(ligs):
    y=4.6-i*0.34
    ax.text(0.3,y,a,fontsize=7.6,va='center',color=TXT,fontweight='bold'); fio(ax,[(1.2,y),(7.2,y)],cor=c,lw=1.3); ax.text(7.3,y,b,fontsize=7.3,va='center',color=TXT)
ax.text(1.5,0.3,'GND comum J1-9 · +5 V externo',ha='center',fontsize=6.6,color=VERM)
ax.text(5.0,-0.2,'11 sinais + GND + 5 V · o D7 do LCD e o buzzer saem de J2; o resto de J1',ha='center',fontsize=8,color=TXT)
salva(fig,'c_rrd')

# ---------- G. cadeia A/D ----------
fig,ax=novo(10,3.9)
caixa(ax,0.1,1.2,1.5,1.9,'J2\nS1…S8\n(8 entradas)',fc='#fff9e0',ec=LARA,fs=8.5)
caixa(ax,2.1,1.2,1.4,1.9,'RN6\n8 × 1 kΩ',fc='#f4f6f9',fs=8.5)
caixa(ax,4.0,1.2,1.7,1.9,'Multiplexador\nAD7501\n(U38)',fc='#e9eff7',fs=8.5)
caixa(ax,6.2,1.2,1.7,1.9,'Conversor A/D\nAD7875\n12 bits (U23)',fc='#e9eff7',fs=8.5)
caixa(ax,8.4,1.2,1.5,1.9,'Leitura\n$020000\n(12 bits)',fc='#e8f3ec',ec=VERDE,fs=8.5)
for x1,x2 in ((1.6,2.1),(3.5,4.0),(5.7,6.2),(7.9,8.4)): seta(ax,x1,2.15,x2,2.15)
caixa(ax,3.5,0.1,2.7,0.7,'$020020 b14–12 = canal',fc='#fff3e6',ec=LARA,fs=7.8); seta(ax,4.85,0.8,4.85,1.2,cor=LARA)
caixa(ax,5.9,3.3,2.3,0.55,'OP3 do DUART = disparo',fc='#fff3e6',ec=LARA,fs=7.8); seta(ax,7.05,3.3,7.05,3.1,cor=LARA)
caixa(ax,8.2,0.1,1.7,0.7,'bit 15 = liga',fc='#fff3e6',ec=LARA,fs=7.8)
salva(fig,'c_adc')

# ---------- H. trampolim de troca de banco ----------
fig,ax=novo(10,4.6)
cols=[('1) Monitor no banco 1',0.1,'#e9eff7',AZUL,['pede "BASIC"','(driver bk_drv em $50000)','salta para bk_sys']),
      ('2) Rotina na RAM',3.4,'#fff3e6',LARA,['copia vetores do banco 7','para a RAM ($0000..)','escreve 7 em $FC0000','jmp $F84000 (entrada)']),
      ('3) EhBASIC no banco 7',6.7,'#e8f3ec',VERDE,['executa de $F84000','vetores já estão na RAM','MONITOR volta ao banco 1'])]
for t,x,fc,ec,ls in cols:
    caixa(ax,x,0.5,3.0,3.3,'',fc=fc,ec=ec); ax.text(x+1.5,3.5,t,ha='center',fontsize=9,fontweight='bold',color=ec)
    for i,l in enumerate(ls): ax.text(x+0.2,2.85-i*0.55,'• '+l,fontsize=7.8,va='center',color=TXT)
seta(ax,3.1,2.1,3.4,2.1); seta(ax,6.4,2.1,6.7,2.1)
ax.text(5,0.1,'A troca de banco muda a flash “debaixo dos pés” do código: por isso a rotina precisa estar na RAM.',ha='center',fontsize=8.2)
salva(fig,'c_trampolim')

# ---------- I. fluxo do gravador ----------
fig,ax=novo(10,4.2)
st=[('FLASH n\n(ou origem\n→ destino)',0.1),('Imagem 128 KB\npara a RAM2',2.1),('CRC32 confere?',4.1),('PROSSIGA?',6.1),('Apaga setor\ngrava e verifica',8.1)]
for t,x in st: caixa(ax,x,2.6,1.7,1.0,t,fc='#e9eff7',fs=7.8)
for x in (1.8,3.8,5.8,7.8): seta(ax,x,3.1,x+0.3,3.1)
caixa(ax,4.1,0.9,1.7,0.9,'não: aborta,\nnada é apagado',fc='#fdeaea',ec=VERM,fs=7.6); seta(ax,4.95,2.6,4.95,1.8,cor=VERM)
caixa(ax,6.1,0.9,1.7,0.9,'outra coisa:\nsó compara',fc='#fff9e0',ec=LARA,fs=7.6); seta(ax,6.95,2.6,6.95,1.8,cor=LARA)
caixa(ax,8.1,0.9,1.7,0.9,'volta ao banco de\nretorno (via RAM)',fc='#e8f3ec',ec=VERDE,fs=7.6); seta(ax,8.95,2.6,8.95,1.8,cor=VERDE)
ax.text(5,0.3,'Banco 0 só com a senha PROSSIGA0 (qualquer outra coisa vira “só comparar”).',ha='center',fontsize=8.2)
salva(fig,'c_gravador')

# ---------- J. decodificação simplificada ----------
fig,ax=novo(10,4.6)
caixa(ax,0.1,1.4,1.7,2.0,'CPU 68000\nA1..A23\n/AS /UDS /LDS\nR/W',fc='#f4f6f9',fs=8.5)
caixa(ax,2.6,1.4,2.0,2.0,'Decodificação\ndiscreta\n74LS138 (U4)\n74LS11 · 74LS14\n(sem PAL/GAL)',fc='#fff3e6',ec=LARA,fs=8.3)
seta(ax,1.8,2.4,2.6,2.4)
dest=[('ROM / flash  $F80000','#e8f3ec',VERDE,3.9),('DUART 68681  $FA0000','#e9eff7',AZUL,3.2),('Registr. de banco  $FC0000','#fff3e6',LARA,2.5),('E/S 16 bits  $020000','#e9eff7',AZUL,1.8),('RAM  $000000 · RAM2  $040000','#e9eff7',AZUL,1.1)]
for t,fc,ec,y in dest:
    caixa(ax,6.0,y-0.3,3.9,0.55,t,fc=fc,ec=ec,fs=8.2); seta(ax,4.6,2.4,6.0,y,cor=ec,lw=1.2)
ax.text(5,0.45,'$060000–$07FFFF: nenhuma saída gera /DTACK. O acesso trava o barramento — nunca usar.',ha='center',fontsize=8,color=VERM)
ax.text(3.6,3.7,'/DTACK gerado\npor U35 (74LS11)',ha='center',fontsize=7.6,color=TXT)
salva(fig,'c_decod')

# ---------- K. I2C frame ----------
fig,ax=plt.subplots(figsize=(9,3)); ax.axis('off'); ax.set_xlim(-1,18); ax.set_ylim(0,5.5)
seq=[('S',1),('1',0),('1',1),('0',0),('1',0),('0',1),('0',0),('0',1),('W',0),('A',0)]
x=1; 
# SCL
pts=[(0,1),(1.5,1)]
for i in range(9): pts+=[(2+i*1.6,0),(2.8+i*1.6,1)]
pts+=[(16.4,1),(18,1)]
ax.step([p[0] for p in pts],[3.3+p[1]*0.7 for p in pts],where='post',color=VERDE,lw=1.8); ax.text(-0.2,3.65,'SCL (J1-30)',ha='right',fontsize=8,va='center')
bitsv=[1,1,0,1,0,0,0,0,0]
pts=[(0,1),(1.0,0)]
for i,b in enumerate(bitsv): pts.append((2+i*1.6,1-b if False else (1 if b==1 else 0)))
pts+=[(16.4,0),(17.2,1)]
ax.step([p[0] for p in pts],[1.6+p[1]*0.7 for p in pts],where='post',color=AZUL,lw=1.8); ax.text(-0.2,1.95,'SDA (J1-48 / J1-23)',ha='right',fontsize=8,va='center')
for i,t in enumerate(['1','1','0','1','0','0','0','W=0','ACK']):
    ax.text(2.4+i*1.6,1.3,t,ha='center',fontsize=7.6,color=AZUL)
ax.text(0.5,2.5,'START',fontsize=7.6,color=VERM,ha='center'); ax.text(17.2,2.5,'',fontsize=7)
ax.text(8,4.6,'endereço do DS1307 = 1101000 (= $68), depois bit de escrita e ACK do chip',ha='center',fontsize=8.4,color=TXT)
ax.text(8,0.3,'cada nível é produzido escrevendo bits do latch $020020 (coletor aberto: 1 = linha puxada para baixo)',ha='center',fontsize=7.8,color=TXT)
ax.set_ylim(0,5.1)
salva(fig,'c_i2c')
print('ok')
