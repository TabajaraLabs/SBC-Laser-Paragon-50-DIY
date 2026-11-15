import sys,glob
sys.path.insert(0,'.')
from t_menu import run
stub=open('ROM_stub_b0_GRAVADO_v3.2s.bin','rb').read(); img=open('ROM_img_b1_v33.bin','rb').read(); ff=b'\xff'*0x20000
ef=glob.glob('**/eforth_bank_v4.bin',recursive=True); ef=open(ef[0],'rb').read() if ef else ff
def t(n,banks,script,tail=1_500_000):
    o=run(stub,banks,script,tail); print('=====',n); print(o[-520:])
bk=[stub,img,ff,ff,ff,ef,ff,img]
t('menu e timeout->monitor',bk,[("Digite ? para ajuda","")])
t('B -> banco 7 $F84000',bk,[("Ou aguarde 5 segundos para entrar","B"),("FAT>","")])
t('F -> eforth banco 5',bk,[("Ou aguarde 5 segundos para entrar","F"),("Iniciando","")],3_000_000)
t('T tetris',bk,[("Ou aguarde 5 segundos para entrar","T")],800_000)
