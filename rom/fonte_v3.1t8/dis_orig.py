import sys, struct
sys.path.insert(0,'.')
from emu68k import CPU, Illegal, Halt
from t_fv4 import Flash
B0=open('PARAGON50_F80000_v3.0.bin','rb').read()
import os
_d=os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_d,'..','original'), '/home/claude/sbc-laser-paragon-50-diy/rom/original'):
    if os.path.exists(os.path.join(_p,'Paragon_50_HI.BIN')): break
_hi=open(os.path.join(_p,'Paragon_50_HI.BIN'),'rb').read(); _lo=open(os.path.join(_p,'Paragon_50_LO.BIN'),'rb').read()
orig=bytes(b for h,l in zip(_hi,_lo) for b in (h,l))      # ROM original de 64 KB intercalada, copiada para $040000 antes de desmontar
# uso: python3 dis_orig.py "U 46512 20" ...  (enderecos = $40000 + deslocamento na ROM original; o monitor v3.0 faz o U)
cpu=CPU(); fl=Flash([B0]+[bytes([255])*0x20000]*7)
orr=cpu.rd; owr=cpu.wr
def rd(a,s):
    a&=0xFFFFFF
    if 0xF80000<=a<0xFA0000: return fl.rd(a-0xF80000,s)
    return orr(a,s)
def wr(a,s,v):
    a&=0xFFFFFF
    if 0xF80000<=a<0xFA0000: return fl.wr(a-0xF80000,s,v&(0xFFFF if s==2 else 0xFF))
    if a==0xFC0000: fl.bank=v&7; return
    return owr(a,s,v)
cpu.rd=rd; cpu.wr=wr
for i,b in enumerate(orig): owr(0x40000+i,1,b)
cpu.sr=0x2700; cpu.a[7]=struct.unpack('>I',B0[0:4])[0]; cpu.pc=struct.unpack('>I',B0[4:8])[0]
out=bytearray(); cpu.on_tx=lambda b: out.append(b)
cmds=sys.argv[1:]
def run(until,limit=400):
    n=0
    while n<limit:
        cpu.run(20000); n+=1
        if until in out.decode('latin-1')[run.pos:]: break
    run.pos=len(out.decode('latin-1'))
run.pos=0
run('Digite ?',limit=3000)
run('>')
for c in cmds:
    for ch in c+'\r': cpu.rx.append(ord(ch))
    run('\n>' if False else '>' ,limit=2000)
print(out.decode('latin-1').replace('\r','').split('Monitor',1)[-1][-int(1e9):])
