import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib import font_manager as fm
for f in ('DejaVuSans.ttf','DejaVuSans-Bold.ttf','DejaVuSansMono.ttf'):
    fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/'+f)
plt.rcParams['font.family']='DejaVu Sans'
plt.rcParams['text.parse_math']=False
AZUL='#12355b'; LARA='#d9731a'; CINZA='#eef1f5'; CINZA2='#c9d1dc'; VERDE='#2f7d4f'; VERM='#b3362d'; TXT='#1d2733'
def caixa(ax,x,y,w,h,txt,fc=CINZA,ec=AZUL,fs=9,bold=False,tc=TXT,lw=1.4,r=0.04):
    p=FancyBboxPatch((x,y),w,h,boxstyle=f"round,pad=0.0,rounding_size={r}",fc=fc,ec=ec,lw=lw); ax.add_patch(p)
    ax.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=fs,color=tc,fontweight='bold' if bold else 'normal',linespacing=1.25)
def seta(ax,x1,y1,x2,y2,cor=AZUL,txt=None,fs=8,off=(0,0.06),lw=1.6,ls='-'):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=13,color=cor,lw=lw,linestyle=ls))
    if txt: ax.text((x1+x2)/2+off[0],(y1+y2)/2+off[1],txt,ha='center',va='bottom',fontsize=fs,color=cor)
def novo(w,h):
    fig,ax=plt.subplots(figsize=(w,h)); ax.set_xlim(0,w); ax.set_ylim(0,h); ax.axis('off'); return fig,ax

# ---------- 1. fluxo de boot ----------
fig,ax=novo(9.2,6.4)
caixa(ax,3.1,5.6,3.0,0.6,'RESET\n(banco 0 da flash, vetores)',fc=AZUL,tc='white',bold=True,fs=9)
caixa(ax,2.35,4.45,4.5,0.8,'STUB DO BANCO 0 (nunca regravado)\nSBC Paragon 50 – Tabajara Labs\n“Aperte R … aguarde 5 s”',fc='#fff3e6',ec=LARA,fs=8.6)
seta(ax,4.6,5.6,4.6,5.25)
caixa(ax,0.05,2.6,3.4,1.4,'Tecla R: RECUPERAÇÃO\n[M] monitor  [A] bancos\n[S] cartão SD\n[U] gravar pela serial\n[N] autoload  [T] Tetris',fc='#fdeceb',ec=VERM,fs=8)
caixa(ax,5.9,2.75,3.1,1.1,'Sem tecla (5 s):\nAUTOLOAD\nprimeiro banco 1…7 com\ncabeçalho AB e CRC32 corretos',fc='#e8f3ec',ec=VERDE,fs=8)
seta(ax,3.7,4.45,2.1,3.85,VERM,'R',off=(-0.15,0.0)); seta(ax,5.5,4.45,7.4,3.85,VERDE,'5 s',off=(0.2,0.0))
caixa(ax,5.9,1.35,3.1,0.95,'BANCO 1: MONITOR v3.4+\nMenu: [B]asic [C]P/M [F]orth\n[T]etris [A]plic. [R] SD [M]onitor',fc=CINZA,ec=AZUL,fs=8)
seta(ax,7.45,2.75,7.45,2.3,VERDE)
caixa(ax,5.6,0.2,1.7,0.6,'Prompt  >\n(monitor)',fc='white',fs=8); caixa(ax,7.5,0.2,1.5,0.6,'BASIC / CP/M\n(banco 7)',fc='white',fs=8)
caixa(ax,3.7,0.2,1.7,0.6,'eForth\n(banco 5)',fc='white',fs=8)
seta(ax,6.9,1.35,6.4,0.8); seta(ax,8.0,1.35,8.2,0.8); seta(ax,6.6,1.35,4.6,0.8)
ax.text(0.2,1.7,'RESET em qualquer ponto volta ao\nbanco 0 (o 74LS175 zera no reset).\nSe nenhum banco 1…7 for válido,\no stub mostra a lista de bancos.',fontsize=7.8,color=TXT,va='center')
fig.savefig('img/fluxo_boot.png',dpi=220,bbox_inches='tight',facecolor='white'); plt.close(fig)

# ---------- 2. mapa dos bancos ----------
fig,ax=novo(9.2,5.0)
bancos=[('0','STUB DE BOOT','v3.2s','protegido: só com PROSSIGA0',LARA,'#fff3e6'),
        ('1','MONITOR','v3.5a','autoload; menu e comandos',AZUL,'#e9eff7'),
        ('2','(livre / teste LCD 2.9t)','','',CINZA2,'white'),
        ('3','BOOT+MONITOR','v3.0','backup do banco 0 antigo',VERDE,'#e8f3ec'),
        ('4','BOOT+MONITOR','v3.1t8','teste (v3.1t8)',CINZA2,'white'),
        ('5','eForth','v1.1+P2','aplicativo (tecla F / FORTH)',AZUL,'#e9eff7'),
        ('6','PARAGON 50','v2.5.1','antigo',CINZA2,'white'),
        ('7','BASIC+CP/M+SD','v3.3a','EhBASIC, CP/M-68K, driver SDFS',AZUL,'#e9eff7')]
for i,(n,nome,ver,desc,ec,fc) in enumerate(bancos):
    y=4.45-i*0.6
    caixa(ax,0.2,y,0.7,0.5,n,fc=ec if ec!=CINZA2 else CINZA2,ec=ec,tc='white' if ec not in (CINZA2,) else TXT,bold=True,fs=13,r=0.05)
    caixa(ax,1.0,y,7.9,0.5,'',fc=fc,ec=ec,r=0.05)
    ax.text(1.2,y+0.25,nome,fontsize=10,fontweight='bold',va='center',color=TXT)
    ax.text(4.3,y+0.25,ver,fontsize=9.5,va='center',color=TXT,family='DejaVu Sans Mono')
    ax.text(5.5,y+0.25,desc,fontsize=8.6,va='center',color=TXT)
ax.text(0.2,0.05,'8 bancos de 128 KB (2 × Am29F040B), visíveis em $F80000–$F9FFFF; seleção por escrita em $FC0000 (74LS175).',fontsize=8,color=TXT)
fig.savefig('img/mapa_bancos.png',dpi=220,bbox_inches='tight',facecolor='white'); plt.close(fig)

# ---------- 3. mapa de memória ----------
fig,ax=novo(10.2,6.0)
regs=[('$000000–$01FFFF','RAM 64 KB (ou 128 KB)',CINZA,AZUL,'programas em $2000+; pilha $1F00'),
      ('$020000–$03FFFF','E/S de 16 bits',  '#fff3e6',LARA,'A/D, DACs, 8254, latches\ne entradas (ver cap. 5)'),
      ('$040000–$05FFFF','RAM2 de 128 KB (hardware extra)', CINZA,AZUL,'buffer do gravador e do ADL ($040000)'),
      ('$060000–$07FFFF','SEM /DTACK — NUNCA ACESSAR','#fdeceb',VERM,'a CPU trava e o watchdog reinicia'),
      ('$080000–$F7FFFF','espelhos dos blocos acima',  '#f6f6f6',CINZA2,'A16 e A19–A23 são ignorados'),
      ('$F80000–$F9FFFF','ROM: banco ativo (128 KB)','#e9eff7',AZUL,'8 bancos; seleção em $FC0000'),
      ('$FA0000–$FBFFFF','DUART 68681','#e8f3ec',VERDE,'console canal A 57600 bps; canal B 9600'),
      ('$FC0000–$FDFFFF','registrador de banco (só escrita)', CINZA,AZUL,'74LS175 — lê lixo'),
      ('$FE0000–$FFFFFF','lê $FF', '#f6f6f6',CINZA2,'')]
for i,(ad,nome,fc,ec,nota) in enumerate(regs):
    y=5.45-i*0.6
    caixa(ax,0.2,y,2.2,0.5,ad,fc='white',ec=ec,fs=8.6,r=0.04); ax.texts[-1].set_family('DejaVu Sans Mono')
    caixa(ax,2.5,y,3.9,0.5,nome,fc=fc,ec=ec,fs=8.6,bold=True,r=0.04)
    ax.text(6.55,y+0.25,nota,fontsize=7.2,va='center',color=TXT,wrap=True)
fig.savefig('img/mapa_memoria.png',dpi=220,bbox_inches='tight',facecolor='white'); plt.close(fig)

# ---------- 4. diagrama de blocos ----------
fig,ax=novo(9.2,6.2)
caixa(ax,3.4,2.6,2.4,1.1,'MC68000\n(CPU)',fc=AZUL,tc='white',bold=True,fs=11)
caixa(ax,0.2,4.6,2.5,0.9,'FLASH 2×Am29F040B\n8 bancos × 128 KB\n$F80000–$F9FFFF',fs=8)
caixa(ax,3.35,4.6,2.5,0.9,'74LS175\nregistrador de banco\n$FC0000',fs=8)
caixa(ax,6.5,4.6,2.5,0.9,'RAM 64 KB\n+ RAM2 128 KB\n$0 / $040000',fs=8)
caixa(ax,0.2,2.6,2.5,1.1,'DUART 68681\n$FA0000\ncanal A: console (J4)',fs=8)
caixa(ax,6.5,2.6,2.5,1.1,'Decodificador de E/S\n$020000–$03FFFF\n(74LS645 U17/U18)',fs=8)
caixa(ax,0.2,0.2,2.0,1.3,'Latch $020018\n74LS273 (U45/U39)\nLCD · SD · buzzer',fs=7.8,fc='#fff3e6',ec=LARA)
caixa(ax,2.35,0.2,2.0,1.3,'Latch $020020\n74LS273\nI²C RTC · mux A/D',fs=7.8,fc='#fff3e6',ec=LARA)
caixa(ax,4.5,0.2,2.0,1.3,'Entradas 74LS240\nporta A $020030\nporta B $020028',fs=7.8,fc='#e8f3ec',ec=VERDE)
caixa(ax,6.65,0.2,2.35,1.3,'A/D AD7875 · 2 DACs\n8254 (3 timers)\n→ J2 (analógico)',fs=7.8,fc='#e9eff7')
for x in (1.45,2.6,3.75,5.2,7.75): pass
seta(ax,4.6,3.7,4.6,4.6); seta(ax,3.4,3.7,2.0,4.6); seta(ax,5.8,3.7,7.7,4.6)
seta(ax,3.4,3.15,2.7,3.15); seta(ax,5.8,3.15,6.5,3.15)
# barramento de E/S: do decodificador para os 4 blocos
ax.plot([7.75,7.75],[2.6,2.0],color=AZUL,lw=1.8); ax.plot([1.2,7.75],[2.0,2.0],color=AZUL,lw=1.8)
for xx in (1.2,3.35,5.5,7.75): seta(ax,xx,2.0,xx,1.5)
ax.text(4.5,2.06,'barramento de E/S ($020000–$03FFFF)',fontsize=7.5,ha='center',color=AZUL)
ax.text(4.6,5.75,'barramento de endereços/dados',fontsize=7.5,ha='center',color=AZUL)
ax.text(4.6,0.0,'J1 e J2 (IDC 50 pinos) levam esses sinais para fora; J7 = alimentação; J4 = serial',fontsize=8,ha='center',color=TXT)
fig.savefig('img/diagrama_blocos.png',dpi=220,bbox_inches='tight',facecolor='white'); plt.close(fig)

# ---------- 5. I2C RTC ----------
fig,ax=novo(8.6,3.6)
caixa(ax,0.2,0.6,2.7,2.4,'PLACA PARAGON 50\n\nLatch $020020\n bit 10 → SCL\n bit 7  → SDA\nPorta B bit 6 ← SDA',fs=8.6,bold=False)
caixa(ax,5.6,0.6,2.8,2.4,'MÓDULO DS1307\n(endereço I²C $68)\n\n5 V · GND · SCL · SDA\npull-ups 4,7 kΩ no módulo\nCR2032 de backup',fs=8.6,fc='#e8f3ec',ec=VERDE)
seta(ax,2.9,2.55,5.6,2.55,LARA,'J1-30   SCL',off=(0,0.05)); ax.add_patch(FancyArrowPatch((2.9,2.55),(5.6,2.55),arrowstyle='-',color=LARA,lw=2))
seta(ax,2.9,1.85,5.6,1.85,AZUL,'J1-48 (saída)  ⇄  SDA',off=(0,0.05))
seta(ax,5.6,1.2,2.9,1.2,VERDE,'J1-23 (leitura SDA)',off=(0,0.05))
ax.text(4.25,0.2,'+5 V: J7-19 · GND: J1-9 · nível 1 no bit do latch = linha puxada para baixo',fontsize=7.8,ha='center',color=TXT)
fig.savefig('img/i2c_rtc.png',dpi=220,bbox_inches='tight',facecolor='white'); plt.close(fig)
print('ok')
