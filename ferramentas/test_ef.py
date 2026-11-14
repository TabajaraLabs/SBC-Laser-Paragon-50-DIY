import sys
sys.path.insert(0,'.')
from m68kasm_v3 import Asm
import emu68k
def run(asmfile, inputs, maxsteps=3_000_000, verbose=True):
    a=Asm(); a.assemble(open(asmfile).read())
    cpu=emu68k.CPU()
    for o,b in a.segs: cpu.mem[o:o+len(b)]=b
    cpu.a[7]=0x1F00; cpu.pc=a.sym['ORIG']
    cpu.rx=list(inputs.encode('latin-1'))
    n=0
    try:
        while n<maxsteps:
            cpu.step(); n+=1
            if not cpu.rx and n>maxsteps//2 and False: break
    except Exception as e:
        print('EXCECAO:',type(e).__name__,e,'pc=%06X'%cpu.pc,'steps',n)
    out=bytes(cpu.tx).decode('latin-1')
    return out,cpu
if __name__=='__main__':
    out,cpu=run(sys.argv[1], sys.argv[2].replace('\\r','\r'), int(sys.argv[3]) if len(sys.argv)>3 else 3_000_000)
    print(repr(out))
