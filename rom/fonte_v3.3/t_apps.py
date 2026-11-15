import sys
sys.path.insert(0,'.')
from t_menu import run
stub=open('ROM_stub_b0_GRAVADO_v3.2s.bin','rb').read(); img=open('ROM_img_b1_v33j.bin','rb').read(); ap=open('PARAGON50_F80000_apps_v33a.bin','rb').read(); ff=b'\xff'*0x20000
bk=[stub,img,ff,ff,ff,ff,ff,ap]
o=run(stub,bk,[("Ou aguarde 5 segundos para entrar","B"),("Ok","FILES\r"),("Ok\r\n","MONITOR\r"),("(imagem do banco 1)\r\n[B]","")][:2]+[("Erro","MONITOR\r"),("banco 1)","")],1_500_000)
print(o[-900:])
