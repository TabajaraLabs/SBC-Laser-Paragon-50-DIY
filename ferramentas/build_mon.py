import sys,struct
sys.path.insert(0,'.')
from m68kasm import Asm
src=open('monitor.asm').read()
vec=[]; stubs=[]
for v in range(2,32):
    vec.append("        dc.l    stub_%d"%v)
    stubs.append("stub_%d: move.w  #%d,-(sp)\n        bra     exc_common"%(v,v))
for v in range(32,256): vec.append("        dc.l    stub_gen")
stubs.append("stub_gen: move.w #255,-(sp)\n        bra     exc_common")
src=src.replace('{{VEC}}','\n'.join(vec)).replace('{{STUBS}}','\n'.join(stubs))
a=Asm(); data=a.assemble(src)
base=a.org; assert base==0xF80000, hex(base)
rom=bytearray(b'\xff'*65536); rom[:len(data)]=data
assert len(data)<=0xFFFE, len(data)
# listagem
with open('monitor.lst','w') as f:
    for ln,pc,b,raw in a.listing:
        f.write("%08X  %-24s %s\n"%(pc,b[:8].hex(),raw))
open('MONITOR_F80000.bin','wb').write(rom)
def split(l):
    qs=[l[i*0x4000:(i+1)*0x4000] for i in range(4)]
    il=b''.join(qs[i] for i in (3,2,1,0)); return il[0::2],il[1::2]
h,l=split(bytes(rom))
open('MONITOR_HI.bin','wb').write(h); open('MONITOR_LO.bin','wb').write(l)
print('codigo ate',hex(base+len(data)),'bytes',len(data))
for k in ['reset','putc','getc','puts','hexb','hexw','hexl','crlf','strobe','gethex','getline','main_loop']: print(k,hex(a.sym[k]))
# confere vetores iniciais
print('SSP',rom[0:4].hex(),'PC',rom[4:8].hex(), 'reset em $F84000?', a.sym['reset']==0xF84000)
