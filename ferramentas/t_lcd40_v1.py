import sys; sys.path.insert(0,'.')
from emu68k import CPU
import m68kasm_v3 as M

class HD:
    def __init__(s): s.four=False; s.hi=None; s.ddr=0; s.ram=[bytearray(b' '*0x80)]; s.ram=bytearray(b' '*0x80); s.on=False; s.log=[]
    def nib(s,n,rs):
        if not s.four:
            if n==2 and not rs: s.four=True
            return
        if s.hi is None: s.hi=n; return
        b=(s.hi<<4)|n; s.hi=None
        if rs: s.ram[s.ddr&0x7F]=b; s.ddr+=1
        else:
            if b==1: s.ram=bytearray(b' '*0x80); s.ddr=0
            elif b&0x80: s.ddr=b&0x7F
            elif b==0x0C: s.on=True
            elif b==0x08: s.on=False
    def line(s,k): return bytes(s.ram[0x40*k:0x40*k+40]).decode('latin1')

class Bus(CPU):
    def __init__(s,addr7=0x27):
        super().__init__(); s.addr7=addr7; s.lat=0; s.scl=1; s.msda=1; s.ssda=1
        s.state='idle'; s.bits=0; s.nb=0; s.cur=0; s.first=True; s.ctrl=[HD(),HD()]; s.pe=[0,0]; s.out=0xFF; s.nbytes=0
    def line_sda(s): return s.msda & s.ssda
    def latch(s,v):
        oscl,osda=s.scl,s.line_sda()
        s.lat=v; s.scl=0 if v&0x400 else 1; s.msda=0 if v&0x80 else 1
        sda=s.msda & s.ssda
        if s.scl==1 and oscl==1:
            if osda==1 and s.msda==0 and s.ssda==1: s.state='addr'; s.nb=0; s.cur=0; s.first=True; s.ssda=1; return   # START
            if osda==0 and s.msda==1 and s.state!='idle': s.state='idle'; s.ssda=1; return                       # STOP
        if oscl==0 and s.scl==1 and s.state in('addr','data'):      # borda de subida: amostra bit
            if s.nb<8: s.cur=(s.cur<<1)|s.msda; s.nb+=1
        if oscl==1 and s.scl==0 and s.state in('addr','data'):      # borda de descida
            if s.nb==8:
                if s.state=='addr':
                    if (s.cur>>1)==s.addr7 and not (s.cur&1): s.ssda=0; s.state='data'; s.nb=9
                    else: s.state='idle'
                else: s.ssda=0; s.nb=9; s.got(s.cur)
            elif s.nb==9: s.ssda=1; s.nb=0; s.cur=0
    def got(s,b):
        s.nbytes+=1
        e1=(b>>2)&1; e2=(b>>1)&1; rs=b&1; n=b>>4
        for i,e in enumerate((e1,e2)):
            if s.pe[i]==1 and e==0: s.ctrl[i].nib(n,rs)
            s.pe[i]=e
    def wr(s,addr,size,v):
        a=addr&0xFFFFFF
        if a==0x020020: self.latch(v) if False else s.latch(v&0xFFFF); return
        if a==0x020000+0x30: return
        return super().wr(addr,size,v)
    def rd(s,addr,size):
        a=addr&0xFFFFFF
        if a==0x020028: return 0x40 if s.line_sda()==0 else 0
        return super().rd(addr,size)

for addr7,label in ((0x27,'LCD em $27'),(0x3F,'sem LCD em $27')):
    c=Bus(addr7)
    a=M.Asm(); a.assemble(open('../programas/lcd40_stubs_v1.asm').read())
    for st,b in a.segs: c.mem[st:st+len(b)]=b
    a=M.Asm(); d=a.assemble(open('../programas/lcd40_teste_v1.asm').read())
    c.mem[0x2000:0x2000+len(d)]=d
    c.pc=0x2000; c.a[7]=0x7000; c.sr=0x2700
    c.rx=[]
    steps=0
    try:
        while steps<6_000_000 and not (c.pc==0x2000 and steps>10):
            c.step(); steps+=1
            if steps>20 and len(c.rx)==0 and c.ctrl[1].ram[0x40:0x44]!=b'    ' and not c.rx and steps%1==0 and c.ctrl[0].ram[0:4]!=b'    ' and c.ctrl[1].ram[0:4]!=b'    ' and 'Tab' in c.ctrl[1].line(1) and not c.rx:
                c.rx=[ord('x')]; c.snap=[(k,c.ctrl[k].line(0),c.ctrl[k].line(1)) for k in (0,1)]
            if c.pc==c.a[7]: pass
    except Exception as ex:
        print('parou:',ex,'pc=%06X'%c.pc)
    print('==',label,'passos',steps,'bytes I2C ao PCF',c.nbytes)
    print(bytes(c.tx).decode('latin1'))
    for k,l0,l1 in getattr(c,'snap',[]): print('E%d: '%(k+1),repr(l0),repr(l1))
    print('apos limpar:',repr(c.ctrl[0].line(0)))
