import sys, struct
sys.path.insert(0,'.')
import emu68k
img=open(sys.argv[1],'rb').read()
cpu=emu68k.CPU(); cpu.mem[0xF80000:0xF80000+len(img)]=img
cpu.a[7],cpu.pc=struct.unpack('>II',img[:8])
cpu.rx=list(sys.argv[2].replace('\\r','\r').encode('latin-1'))
n=0
try:
    while n<int(sys.argv[3]): cpu.step(); n+=1
except Exception as e: print('EXC',e)
print(bytes(cpu.tx).decode('latin-1'))
