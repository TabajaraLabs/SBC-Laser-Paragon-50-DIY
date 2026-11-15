import sys
sys.path.insert(0,'.')
from t_menu import run
stub=open('ROM_stub_b0_GRAVADO_v3.2s.bin','rb').read(); img=open('ROM_img_b1_v35a.bin','rb').read(); ap=open('PARAGON50_F80000_apps_v33a.bin','rb').read(); ff=b'\xff'*0x20000
bk=[stub,img,ff,ff,ff,ff,ff,ap]
for cmd,esp in (("B","Memory size"),("C","Disk select")):
    o=run(stub,bk,[("Digite ? para ajuda.\r\n> ",cmd+"\r"),(esp,"")],1_000_000)
    print('=====',cmd); print(o[-350:])
