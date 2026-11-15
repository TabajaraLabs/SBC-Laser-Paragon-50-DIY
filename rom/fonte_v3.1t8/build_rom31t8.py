#!/usr/bin/env python3
"""build_rom31t.py - BANCO 0 (pre-bootloader) v3.1t: monitor v2.8 + Tetris + bancos_v4 (hook PER1) + recuperacao SD (fatsh_v7, com gravacao W/K/C) + flasher v5d + LCD + splash + ext v2.7 + perifericos PER1 ($F88000: ADC ADL DAC RTC).
BASIC e CP/M ficam no banco 1 (teclas B e C iniciam o banco 1)."""
import sys, subprocess, datetime
sys.path.insert(0,'.')
from m68kasm import Asm as OldAsm
import m68kasm_v3
VER=sys.argv[1] if len(sys.argv)>1 else '3.1t'; OUT=sys.argv[2] if len(sys.argv)>2 else 'PARAGON50_F80000_v3.1t.bin'
NAME=sys.argv[3] if len(sys.argv)>3 else 'BOOT+MONITOR'; RCB=int(sys.argv[4]) if len(sys.argv)>4 else 0
old=open('rom231.bin','rb').read(); assert len(old)==131072
# --- monitor
src=open('monitor_v29.asm').read(); vec=[]; stubs=[]
for v in range(2,32):
    vec.append("        dc.l    stub_%d"%v); stubs.append("stub_%d: move.w  #%d,-(sp)\n        bra     exc_common"%(v,v))
for v in range(32,256): vec.append("        dc.l    stub_gen")
stubs.append("stub_gen: move.w #255,-(sp)\n        bra     exc_common")
mes=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']; d=datetime.date.today()
src=src.replace('{{DATE}}','%02d/%s/%d'%(d.day,mes[d.month-1],d.year)).replace('{{VEC}}','\n'.join(vec)).replace('{{STUBS}}','\n'.join(stubs))
a=OldAsm(); mon=a.assemble(src); assert a.org==0xF80000
print('monitor ate $%X (limite $F81C00)'%(0xF80000+len(mon))); assert len(mon)<=0x1C00
# --- flasher v5c (em $2000) guardado em $F86000
fl=open('flash_v5d.bin','rb').read(); FLIMG=0xF86400; FLLEN=len(fl); assert 0x2000+FLLEN<=0x3000
# --- shell do cartao SD em $F84000
pre="RCBANK equ %d\nSHORG equ $F84000\nFLIMG equ $%X\nFLLEN equ %d\n"%(RCB,FLIMG,FLLEN)
sh=m68kasm_v3.Asm(); sh.assemble(pre+open('fatsh_v8.asm').read()); sa,simg=sh.segs[0]; assert sa==0xF84000 and len(simg)<=FLIMG-0xF84000, len(simg)
print('shell SD $F84000-$%X (%d bytes)'%(sa+len(simg)-1,len(simg)))
# --- modulo bancos_v3
pre="RCBANK equ %d\nFL_LEN1 equ %d\nFL_IMG1 equ $%X\n"%(RCB,FLLEN,FLIMG)
m=m68kasm_v3.Asm(); m.assemble(pre+open('bancos_v4.asm').read()); assert len(m.segs)==1
addr,code=m.segs[0]; assert addr==0xF833F8 and addr+len(code)<=0xF84000, hex(addr+len(code))
print('bancos $%X-$%X (%d bytes)'%(addr,addr+len(code)-1,len(code)))
assert m.sym['BK_SYS'] if 'BK_SYS' in m.sym else True
print('bk_sys em $%X (esperado $F83410 = entrada +18 do modulo)'%m.sym['bk_sys'] if 'bk_sys' in m.sym else '')
rom=bytearray(b'\xff'*0x20000)
rom[0:len(mon)]=mon
rom[0x1C00:0x33F8]=old[0x1C00:0x33F8]                       # Tetris
rom[addr-0xF80000:addr-0xF80000+len(code)]=code
rom[0x4000:0x4000+len(simg)]=bytes(simg)
rom[FLIMG-0xF80000:FLIMG-0xF80000+FLLEN]=fl
ext=bytearray(open('ext_v27.bin','rb').read()); assert len(ext)==0x10000
rom[0x10000:0x20000]=ext
per=open('per_v6.bin','rb').read(); assert len(per)<=0x8000 and set(rom[0x8000:0x8000+len(per)])=={0xff}; rom[0x8000:0x8000+len(per)]=per   # PER1 em $F88000
print('PER1 $F88000-$%X (%d bytes)'%(0xF88000+len(per)-1,len(per)))
sp=open('splash_v1.bin','rb').read(); assert set(rom[0x7EE0:0x7EE0+len(sp)])=={0xff}; rom[0x7EE0:0x7EE0+len(sp)]=sp
lcd=open('lcd_blob_v1.bin','rb').read(); assert set(rom[0x612:0x614+len(lcd)])=={0xff}
rom[0x612:0x614]=b'\x4E\x75'; rom[0x614:0x614+len(lcd)]=lcd
open('rom31_sem_cab.bin','wb').write(rom)
subprocess.check_call([sys.executable,'mkbanco_v2.py','rom31_sem_cab.bin',OUT,NAME,VER,'--tipo','0'])
