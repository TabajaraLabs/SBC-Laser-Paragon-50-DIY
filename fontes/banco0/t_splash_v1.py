import sys, struct
sys.path.insert(0,'.')
from emu68k import CPU, Illegal, Halt
ROM=sys.argv[1] if len(sys.argv)>1 else 'PARAGON50_F80000_v2.9t.bin'
cpu=CPU(); r=open(ROM,'rb').read(); cpu.mem[0xF80000:0xF80000+len(r)]=r
out=bytearray(); cpu.on_tx=lambda b: out.append(b)
lcdlog=[]; _wr=cpu.wr
def wr(addr,size,v):
    if addr==0x20018 and size==2: lcdlog.append(v)
    return _wr(addr,size,v)
cpu.wr=wr
cpu.a[7],cpu.pc=struct.unpack('>II',r[:8]); cpu.sr=0x2700
try:
    for i in range(300): cpu.run(20000)
except (Illegal,Halt) as e: print('EMU STOP',e)
def lcd_screen():
    nibs=[]; prev=0
    for v in lcdlog:
        if (prev&8) and not (v&8): nibs.append(((((v>>5)&7)|(((v>>8)&1)<<3)),(v>>4)&1))
        prev=v
    res=[]; i=0
    while i+1<len(nibs):
        (h,rs),(l,_)=nibs[i],nibs[i+1]; i+=2; res.append((rs,(h<<4)|l))
    scr={}; pos=0
    for rs,b in res:
        if not rs:
            if b&0x80: pos=b&0x7F
            elif b==1: scr={}
        else: scr[pos]=chr(b); pos+=1
    base=[0x00,0x40,0x14,0x54]
    return [''.join(scr.get(base[r]+c,' ') for c in range(20)) for r in range(4)]
print(out.decode('latin-1').replace('\r','')[:420]); print('LCD:'); [print('  |'+l+'|') for l in lcd_screen()]
