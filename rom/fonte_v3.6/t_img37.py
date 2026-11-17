import sys, struct; sys.path.insert(0,'.')
src=open('/home/claude/sbc-laser-paragon-50-diy/ferramentas/t_lcd40_v1.py').read(); exec(src[:src.index('for addr7,label')])
from emu68k import Illegal, Halt
def go(imgf, addr7, steps_total=60_000_000):
    img=open(imgf,'rb').read(); c=Bus(addr7); c.mem[0xF80000:0xFA0000]=img
    out=bytearray(); c.on_tx=lambda b: out.append(b)
    c.a[7],c.pc=struct.unpack('>II',img[:8]); c.sr=0x2700
    try:
        n=0
        while n<steps_total:
            c.run(20000); n+=20000
            if b'Digite ?' in out and n>steps_total//2: break
    except (Illegal,Halt) as e: print('EMU STOP',e,hex(c.pc))
    print('== LCD em $%02X: passos %d, bytes I2C %d'%(addr7,n,c.nbytes))
    for k in (0,1):
        for j in (0,1): print('  E%d linha%d: %r'%(k+1,j,c.ctrl[k].line(j)))
    t=out.decode('latin-1').replace('\r',''); print(t[-260:])
go(sys.argv[1],0x27)
go(sys.argv[1],0x50,25_000_000)
