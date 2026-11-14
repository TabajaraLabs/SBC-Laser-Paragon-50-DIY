import sys, struct
sys.path.insert(0,'.')
from emu68k import CPU, Illegal, Halt
def run(img, banks, script, tail=3_000_000):
    cpu=CPU(); cpu.mem[0xF80000:0xFA0000]=banks[0]
    out=bytearray(); cpu.on_tx=lambda b: out.append(b)
    orig=cpu.wr
    def wr(addr,size,v):
        if (addr&0xFFFFFF)==0xFC0000:
            cpu.mem[0xF80000:0xFA0000]=banks[v&7]; return
        return orig(addr,size,v)
    cpu.wr=wr
    cpu.a[7],cpu.pc=struct.unpack('>II',banks[0][:8]); cpu.sr=0x2700
    pos=0;i=0;steps=0
    try:
        while steps<400_000_000:
            cpu.run(20000); steps+=20000
            txt=out.decode('latin-1')
            while i<len(script) and script[i][0] in txt[pos:]:
                pos=txt.index(script[i][0],pos)+len(script[i][0])
                for ch in script[i][1]: cpu.rx.append(ord(ch))
                i+=1
            if i>=len(script): cpu.run(tail); break
    except (Illegal,Halt) as e: print('EMU STOP',e)
    return out.decode('latin-1').replace('\r','')
if __name__=='__main__':
    img=open(sys.argv[1],'rb').read()
    if len(sys.argv)>2:  # controle: reverte a correcao do strobe
        b=bytearray(img); i=b.find(bytes.fromhex('2F07')); print('ctl'); 
    banks=[img]*8
    t=run(img,banks,[("Ou aguarde","A"),("iniciar mesmo","")] if False else [("Ou aguarde","A"),("menu principal: ","2")])
    print(t[-600:])
