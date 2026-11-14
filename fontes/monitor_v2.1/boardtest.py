import sys
sys.path.insert(0,'/tmp/claude-0/-home-claude/93617e9f-8b52-5410-9afb-5edd9ad3194e/scratchpad/cpm')
from emu68k import CPU, Illegal, Halt
ROM='/tmp/claude-0/-home-claude/93617e9f-8b52-5410-9afb-5edd9ad3194e/scratchpad/rom21/27C512/PARAGON512_F80000.bin'
class AddrErr(Exception):
    def __init__(s,a,r): s.addr=a; s.read=r
class BusErr(Exception):
    def __init__(s,a,r): s.addr=a; s.read=r
class Board(CPU):
    """Modelo da placa: kind 'old' = RAM 64 KB espelhada em $0-$1FFFF; 'new' = RAM 128 KB reais em $0-$1FFFF.
    $20000-$3FFFF = E/S 16 bits (leitura variavel, escritas registradas em iowrites),
    $40000-$5FFFF = E/S 8 bits (le FF), $60000-$7FFFF = SEM DTACK (acesso => Halt).
    $80000-$F7FFFF repete a parte baixa. $FC0000-$FDFFFF barramento aberto ($6100), $FE0000+ = FF.
    $E00000-$E0FFFF so existe no teste: gera ERRO DE BARRAMENTO (a placa real nao tem; /BERR fixo em Vcc)."""
    def __init__(s,kind):
        super().__init__(); s.kind=kind; s.bus=0xFF; s.iowrites=[]; s.ioreads=0; s.inpA=0x0000; s.inpB=0x0000
    def ram(s,a):
        if s.kind=='old': return a&0xFFFF
        if s.kind=='fault' and a>=0x18000: return a-0x10000   # falha simulada: $18000-$1FFFF espelha $08000-$0FFFF
        return a&0x1FFFF
    def rb(s,a):
        if 0xE00000<=a<0xE10000: raise BusErr(a,True)
        if a>=0xFC0000 and a<0xFE0000: return 0x61 if not a&1 else 0x00
        if a>=0xFE0000: return 0xFF
        a&=0x7FFFF
        if a<0x20000: return s.mem[s.ram(a)]
        if 0x20028<=a<=0x20029: return (s.inpB>>(8 if a==0x20028 else 0))&0xFF
        if 0x20030<=a<=0x20031: return (s.inpA>>(8 if a==0x20030 else 0))&0xFF
        if a<0x40000: s.ioreads+=1; return (0xF0+(s.ioreads&3)) if not a&1 else 0
        if a<0x60000: return 0xFF
        raise Halt('SEM DTACK em %06X'%a)
    def wb(s,a,v):
        if 0xE00000<=a<0xE10000: raise BusErr(a,False)
        if a>=0xFC0000: return
        a2=a&0x7FFFF
        if a2<0x20000: s.mem[s.ram(a2)]=v; return
        if a2<0x60000: s.iowrites.append((a,v)); return
        raise Halt('SEM DTACK (escrita) em %06X'%a)
    def rd(s,addr,size):
        a=addr&0xFFFFFF
        if 0xF80000<=a<0xFC0000:
            v=CPU.rd(s,a,size); s.bus=v&0xFF; return v
        if size>1 and a&1: raise AddrErr(a,True)
        v=0
        for i in range(size):
            b=s.rb(a+i); s.bus=b; v=(v<<8)|b
        return v
    def wr(s,addr,size,v):
        a=addr&0xFFFFFF
        if 0xF80000<=a<0xFC0000: return CPU.wr(s,a,size,v)
        if size>1 and a&1: raise AddrErr(a,False)
        for i in range(size):
            b=(v>>(8*(size-1-i)))&0xFF; s.bus=b; s.wb(a+i,b)
    def group0(s,vec,addr,read):
        sr=s.sr
        s.sr|=0x2000; s.sr&=~0x8000
        s.push32(s.pc); s.push16(sr); s.push16(0); s.push32(addr); s.push16((0x10 if read else 0)|5)
        s.pc=CPU.rd(s,vec*4,4)
    def step(s):
        try: CPU.step(s)
        except AddrErr as e: s.group0(3,e.addr,e.read)
        except BusErr as e: s.group0(2,e.addr,e.read)
def run(kind,script,romfile=ROM,maxsteps=400_000_000,board=None):
    cpu=board or Board(kind); rom=open(romfile,'rb').read()
    cpu.mem[0xF80000:0xF80000+len(rom)]=rom
    out=bytearray()
    cpu.on_tx=lambda b: out.append(b)
    cpu.ssp=CPU.rd(cpu,0xF80000,4); cpu.a[7]=cpu.ssp; cpu.pc=CPU.rd(cpu,0xF80004,4); cpu.sr=0x2700
    pos=0;i=0;steps=0
    try:
        while steps<maxsteps:
            cpu.run(20000); steps+=20000
            txt=out.decode('latin-1')
            while i<len(script) and script[i][0] in txt[pos:]:
                k=txt.index(script[i][0],pos)+len(script[i][0]); pos=k
                for ch in script[i][1]: cpu.rx.append(ord(ch))
                i+=1
            if i>=len(script):
                cpu.run(3_000_000); break
    except (Illegal,Halt) as e: print('EMU STOP',e)
    run.cpu=cpu
    return bytes(out)
def session(kind,cmds):
    script=[('[T]etris','m')]+[('> ',c+'\r') for c in cmds]+[('> ','\r')]
    out=run(kind,script)
    return out.decode('latin-1').replace('\r',''), run.cpu
if __name__=='__main__':
    kind=sys.argv[1]
    t,cpu=session(kind,['i','q','p 3010 77','d 3010 301f','d 13010 1301f','a 2000','move.b #$11,$10010','move.b #$22,$1FFF0','rts','','g 2000','d 10010 1001f','d 1fff0 1ffff','p 20000 11','d 10 1f'])
    print(t); print('RAMEND %X'%CPU.rd(cpu,0x40C,4),'escritas em E/S:',cpu.iowrites)
