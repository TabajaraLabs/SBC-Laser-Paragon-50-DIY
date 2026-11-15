import sys
sys.path.insert(0,'.')
from t_menu import run
stub=open('ROM_stub_b0.bin','rb').read(); img=open('ROM_img_b1.bin','rb').read(); ff=b'\xff'*0x20000
def t(name,banks,script,tail=2_000_000):
    print('=====',name); print(run(stub,banks,script,tail)[-900:])
t('6 protecao banco 0',[stub,img]+[ff]*6,[("Aguarde 5","R"),("[N] autoload","M"),("ajuda.\r\n> ","FLASH 0\r"),("(em maiusculas)","PROSSIGA\r"),("PROTEGIDO","")])
t('7 U 5',[stub,img]+[ff]*6,[("Aguarde 5","R"),("[N] autoload","U"),("destino (1-7): ","5"),("(em maiusculas)","")])
