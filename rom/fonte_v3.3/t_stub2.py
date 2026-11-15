import sys
sys.path.insert(0,'.')
from t_menu import run
stub=open('ROM_stub_b0.bin','rb').read(); img=open('ROM_img_b1.bin','rb').read(); ff=b'\xff'*0x20000
bad=bytes(img[:0x5000])+b'\x00'+bytes(img[0x5001:])
def t(n,banks,script,tail=1_500_000):
    o=run(stub,banks,script,tail); print('=====',n); print(o[-420:])
t('autoload b1',[stub,img]+[ff]*6,[("Digite ? para ajuda","")])
t('b1 vazio -> b2',[stub,ff,img]+[ff]*5,[("Digite ? para ajuda","")])
t('b1 CRC ruim -> b2',[stub,bad,img]+[ff]*5,[("Digite ? para ajuda","")])
t('protecao b0',[stub,img]+[ff]*6,[("Aguarde 5","R"),("[N] autoload","M"),("ajuda.\r\n> ","FLASH 0\r"),("(em maiusculas)","PROSSIGA\r"),("PROTEGIDO","")])
