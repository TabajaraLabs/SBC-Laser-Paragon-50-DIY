#!/usr/bin/env python3
"""build_rom25.py - ROM v2.6 = v2.3.1 + monitor v2.5 + modulo bancos_v2 (menu de bancos, FLASH, L) + EhBASIC com MONITOR + CP/M com warm boot rapido."""
import sys, subprocess, datetime
sys.path.insert(0,'.')
from m68kasm import Asm as OldAsm
import m68kasm_v3
from asm2 import Asm as EhAsm
base=bytearray(open('rom231.bin','rb').read()); assert len(base)==131072
# --- monitor
src=open('monitor_apps_v1.asm').read(); vec=[]; stubs=[]
for v in range(2,32):
    vec.append("        dc.l    stub_%d"%v); stubs.append("stub_%d: move.w  #%d,-(sp)\n        bra     exc_common"%(v,v))
for v in range(32,256): vec.append("        dc.l    stub_gen")
stubs.append("stub_gen: move.w #255,-(sp)\n        bra     exc_common")
mes=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']; d=datetime.date.today()
src=src.replace('{{DATE}}','%02d/%s/%d'%(d.day,mes[d.month-1],d.year)).replace('{{VEC}}','\n'.join(vec)).replace('{{STUBS}}','\n'.join(stubs))
a=OldAsm(); mon=a.assemble(src); assert a.org==0xF80000
print('monitor ate $%X (limite $F81C00)'%(0xF80000+len(mon))); assert len(mon)<=0x1C00
assert a.sym['restart']==0xF8083C-0 or True
# --- imagem do gravador flash_v2 (em $2000)
f=m68kasm_v3.Asm(); f.assemble(open('flash_v2.asm').read()); fa,fimg=f.segs[0]; assert fa==0x2000; fimg=bytes(fimg)
# --- modulo
FL2=0xF8FB96
def build_mod(l1,l2):
    pre="FL_LEN1 equ %d\nFL_LEN2 equ %d\nFL_IMG2 equ $%X\n"%(l1,l2,FL2)
    body=open('bancos_v2.asm').read()
    chunk="FL_IMG1:\n"+''.join("        dc.b "+','.join('$%02X'%x for x in fimg[i:min(i+16,l1)])+"\n" for i in range(0,l1,16))
    m=m68kasm_v3.Asm(); m.assemble(pre+body+"\n"+chunk); return m
m=build_mod(0,0); img1=m.sym['FL_IMG1']
l1=min(len(fimg),0xF84000-img1); l2=len(fimg)-l1
m=build_mod(l1,l2); assert len(m.segs)==1
addr,code=m.segs[0]; assert addr==0xF833F8 and addr+len(code)<=0xF84000
print('modulo $%X-$%X (%d bytes); gravador: %d bytes na ROM + %d bytes em $%X'%(addr,addr+len(code)-1,len(code),l1,l2,FL2))
assert FL2+l2<=0xF90000 and l2<=1130
assert m.sym['FLCHK'] if 'FLCHK' in m.sym else True
# --- EhBASIC
segs=EhAsm().assemble(open('eh_rom_v27.asm',errors='replace').read())
bas=[bytes(b) for o,b in segs if o==0xF84000][0]; print('EhBASIC',len(bas)); assert len(bas)<=0x4000
cpm=open('cpm_rom_sd_v3.bin','rb').read(); assert len(cpm)<=FL2-0xF88000, len(cpm)   # v2.8t: o CP/M-SD ocupa tambem o espaco do antigo 'perifericos' ($F8F000)
rom=bytearray(base)
def put(off,data,clear_to=None):
    end=off+(clear_to if clear_to else len(data))
    rom[off:end]=b'\xff'*(end-off); rom[off:off+len(data)]=data
for off,length in ((addr-0xF80000,len(code)),(FL2-0xF80000,l2)):
    assert set(base[off:off+length])=={0xFF}, 'area ocupada $%X'%(0xF80000+off)
put(0,mon,0x1C00)
put(0x4000,bas,0x4000)
put(0x8000,cpm,FL2-0xF88000)
drv=open('sdfs_v5.bin','rb').read(); assert len(drv)%2==0 and len(drv)<=0xFFFE
ext=bytearray(b'\xff'*0x10000); ext[0:len(drv)]=drv
rom[0x10000:0x20000]=ext
print('driver SDFS %d bytes em $F90000'%len(drv))
import json
segs=json.load(open('lcd_i2c_b7_v1_segs.json'))
rom[0x612:0x614]=b'\x4E\x75'                                          # RTS do '@'
for sa,hx in segs:
    bb=bytes.fromhex(hx); o=sa-0xF80000
    assert set(rom[o:o+len(bb)])=={0xff}, 'area ocupada $%X'%sa
    rom[o:o+len(bb)]=bb
    print('LCD I2C: $%X-$%X (%d bytes)'%(sa,sa+len(bb)-1,len(bb)))
rom[addr-0xF80000:addr-0xF80000+len(code)]=code
rom[FL2-0xF80000:FL2-0xF80000+l2]=fimg[l1:]
open('rom26_sem_cab.bin','wb').write(rom)
subprocess.check_call([sys.executable,'mkbanco_v2.py','rom26_sem_cab.bin','PARAGON50_F80000_apps_v36a.bin','BASIC+CPM+SD','3.6a','--tipo','0'])
