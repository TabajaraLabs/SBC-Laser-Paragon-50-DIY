import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams['text.parse_math']=False
AZ='#12355b';LA='#d9731a';VE='#2f7d4f';VM='#b3362d';TX='#1d2733'
fig,ax=plt.subplots(figsize=(13,8.2)); ax.set_xlim(0,13); ax.set_ylim(0,8.2); ax.axis('off')
def cx(x,y,w,h,t,fc='#e9eff7',ec=AZ,fs=9.5,b=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=0.08',fc=fc,ec=ec,lw=1.6))
    ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=fs,color=TX,fontweight='bold' if b else 'normal')
def ln(xs,ys,c=AZ,lw=2.2): ax.plot(xs,ys,color=c,lw=lw,solid_capstyle='round')
def ar(x0,y0,x1,y1,c=AZ): ax.annotate('',xy=(x1,y1),xytext=(x0,y0),arrowprops=dict(arrowstyle='-|>',color=c,lw=2.2))
def mp(x,y,t):
    ax.plot([x],[y],'o',ms=13,color=LA); ax.text(x,y,t,ha='center',va='center',fontsize=8,color='white',fontweight='bold')
ax.text(0.2,7.85,'PARAGON 50 — alimentação por USB-C (5 V) com +12 V e −12 V gerados a bordo',fontsize=14,fontweight='bold',color=AZ)
ax.text(0.2,7.5,'Estimativa: 5 V a 1,3–1,9 A (placa + LCD + SD) · +12 V ≈ 50–100 mA · −12 V ≈ 10–30 mA. Valores a confirmar na bancada.',fontsize=9,color=TX)
# carregador
cx(0.2,5.3,1.9,1.4,'Carregador\nUSB-C\n5 V / 3 A\n(cabo C–C)',fc='#fff3e6',ec=LA,b=True)
# conector
cx(2.6,5.3,2.2,1.4,'Breakout USB-C\nVBUS · GND\nCC1 e CC2: cada um\ncom 5,1 kΩ ao GND',fc='#eef1f5')
ar(2.1,6.0,2.6,6.0,LA)
# protecao + capacitores
cx(5.3,5.3,2.1,1.4,'Fusível / PTC 3 A\n+ 470–1000 µF\n+ 100 nF\n(perto do conector)',fc='#eef1f5')
ar(4.8,6.0,5.3,6.0)
# barramento 5V
ln([7.4,12.2],[6.0,6.0],VM,3.2); ax.text(12.25,6.0,'+5 V',fontsize=10,color=VM,fontweight='bold',va='center')
ln([7.4,7.4],[6.0,6.0]) 
# derivacoes
cx(7.9,3.6,2.0,0.95,'Boost 12 V\n(MT3608 ou similar)\n+ LC / LDO 12 V',fc='#e8f3ec',ec=VE,fs=9)
ln([8.9,8.9],[6.0,4.55],VM,2.4)
cx(10.4,3.6,2.0,0.95,'Inversor −12 V\n(já existente)',fc='#e8f3ec',ec=VE,fs=9)
ln([11.4,11.4],[6.0,4.55],VM,2.4)
cx(7.9,1.9,4.5,1.1,'PLACA PARAGON 50\n+5 V: J7-19 (fios curtos e grossos) · GND: J1-9\n+12 V e −12 V: conferir o pino nos conectores',fc='#e9eff7',fs=9)
ar(8.9,3.6,8.9,3.0,VE); ar(11.4,3.6,11.4,3.0,VE)
ax.text(9.1,3.22,'+12 V',fontsize=9,color=VE,fontweight='bold'); ax.text(11.6,3.22,'−12 V',fontsize=9,color=VE,fontweight='bold')
# 5V para placa e trilho do LCD/SD
ln([7.6,7.6],[6.0,2.45],VM,3.2); ar(7.6,2.45,7.9,2.45,VM)
ln([1.8,7.6],[4.9,4.9],VM,2.4)
cx(0.2,3.55,3.2,1.0,'LCD 40×4 + backpack PCF8574\nlógica 3–6 mA · luz de fundo 200–500 mA\n(fio próprio e grosso ao +5 V)',fc='#fff3e6',ec=LA,fs=8.3)
cx(3.8,3.55,3.0,1.0,'Cartão SD (RepRap) + buzzer\nparado ≈ 1 mA · em acesso 30–100 mA\nbuzzer ≈ 20–30 mA',fc='#fff3e6',ec=LA,fs=8.3)
ln([1.8,1.8],[4.9,4.55],VM,2.4); ln([5.3,5.3],[4.9,4.55],VM,2.4)
mp(5.0,6.0,'M1'); mp(7.6,3.9,'M2'); mp(8.9,3.3,'M3'); mp(11.4,3.3,'M4')
ax.text(0.2,3.05,'Pontos de medição (um de cada vez, placa rodando o monitor):',fontsize=9.6,color=AZ,fontweight='bold')
for i,t in enumerate(['M1  saída do conector: 5,0 V ± 0,1 V sem carga',
                      'M2  +5 V na placa (J7-19 × GND): ≥ 4,85 V sob carga',
                      'M3  +12 V na placa: ripple baixo (A/D e DACs)',
                      'M4  −12 V na placa: sobe junto com o +5 V?  (datasheet)']):
    ax.text(0.2,2.7-i*0.33,t,fontsize=8.8,color=TX)
ax.text(0.2,0.7,'Regras: nunca ligar a placa em porta USB de PC (500 mA) · carregador ≥ 3 A com cabo C–C ·',fontsize=8.6,color=VM)
ax.text(0.2,0.4,'fusível/PTC antes do boost e do inversor · medir a corrente real antes de fechar o projeto.',fontsize=8.6,color=VM)
fig.savefig('img/alimentacao_usbc.png',dpi=200,bbox_inches='tight',facecolor='white')
fig.savefig('Paragon50_Alimentacao_USBC_v1.pdf',bbox_inches='tight',facecolor='white')
