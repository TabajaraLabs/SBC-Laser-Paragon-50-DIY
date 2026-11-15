exec(open('diagramas.py').read().split('# ---------- 1.')[0]) if False else None
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['text.parse_math']=False
AZUL='#12355b'; LARA='#d9731a'; VERDE='#2f7d4f'; VERM='#b3362d'; TXT='#1d2733'
ev=[('27C256','ROM única\nmonitor+BASIC\n+CP/M',AZUL),('27C512','128 KB\nmonitor v2',AZUL),('RAM','128 KB\nSRAM 28→32',AZUL),('v2.3','CP/M com\ndisco RAM P:',AZUL),
    ('flash','Am29F040B\n8 bancos',LARA),('v2.5','FLASH no\nmonitor',LARA),('v3.0','banco 0 =\npré-boot',LARA),('v3.2s','STUB\n+ autoload',VERDE),('v3.4','BASIC/CPM/\nFORTH',VERDE),('v3.5a','menu B/C\nrestaurado',VERDE)]
fig,ax=plt.subplots(figsize=(10,3.4)); ax.set_xlim(0,10); ax.set_ylim(-0.6,3.4); ax.axis('off')
ax.plot([0.3,9.7],[1.7,1.7],color='#c9d1dc',lw=4,zorder=0)
for i,(t,d,c) in enumerate(ev):
    x=0.55+i*0.97; up=(i%2==0)
    ax.scatter([x],[1.7],s=190,color=c,zorder=3,edgecolor='white',lw=2)
    ax.plot([x,x],[1.7,2.25 if up else 1.15],color=c,lw=1.4)
    ax.text(x,2.38 if up else 1.02,t,ha='center',va='bottom' if up else 'top',fontsize=10,fontweight='bold',color=c)
    ax.text(x,2.95 if up else 0.62,d,ha='center',va='bottom' if up else 'top',fontsize=7.6,color=TXT,linespacing=1.15)
ax.text(0.3,-0.55,'azul: base e memória · laranja: flash em bancos · verde: bootloader e aplicativos',fontsize=8,color=TXT)
fig.savefig('img/linha_tempo.png',dpi=220,bbox_inches='tight',facecolor='white')
