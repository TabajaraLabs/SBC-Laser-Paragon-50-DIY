import sys, struct, zlib
sys.path.insert(0,'.')
from emu68k import CPU, Illegal, Halt
ROM=open('PARAGON50_F80000_v2.6.bin','rb').read()
FV4=open('flash_v4.bin','rb').read()

class Flash:
    """Modelo minimo de duas Am29F040B em paralelo: 8 bancos de 128 KB (janela $F80000-$F9FFFF)."""
    def __init__(s, banks):
        s.b=[bytearray(x) for x in banks]; s.bank=0; s.state=0; s.mode='read'; s.erases=0; s.progs=0
    def rd(s, off, size):
        m=s.b[s.bank]
        if s.mode=='id':
            return {0:0x0101,2:0xA4A4}.get(off&~1,0) if size==2 else 0
        if size==1: return m[off]
        if size==2: return (m[off]<<8)|m[off+1]
        return (m[off]<<24)|(m[off+1]<<16)|(m[off+2]<<8)|m[off+3]
    def wr(s, off, size, v):
        assert size==2, 'flash so aceita palavra'
        if s.state==10:    # programacao: AND
            m=s.b[s.bank]; old=(m[off]<<8)|m[off+1]; new=old&v
            m[off]=new>>8; m[off+1]=new&255; s.state=0; s.progs+=1; return
        if v==0xF0F0: s.state=0; s.mode='read'; return
        seq=[(0xAAA,0xAAAA),(0x554,0x5555)]
        if s.state in (0,1,5,6) and (off,v)==seq[s.state%5 if s.state<5 else s.state-5]:
            s.state+=1; return
        if s.state==2 and off==0xAAA:
            if v==0x9090: s.mode='id'; s.state=0; return
            if v==0xA0A0: s.state=10; return
            if v==0x8080: s.state=5; return
        if s.state==7 and v==0x3030:
            s.b[s.bank]=bytearray(b'\xff'*131072); s.erases+=1; s.state=0; return
        s.state=0

def fl4(img,bank):
    tr=b'FL4'+bytes([bank])+struct.pack('>I',zlib.crc32(img)&0xFFFFFFFF); tr+=b'\xff'*(256-len(tr)); return img+tr
def run(stream, bank=1, mode=0, maxsteps=140_000_000, give=None, banks=None):
    cpu=CPU(); cpu.mem[0xF80000:0xF80000+len(ROM)]=ROM
    fl=Flash(banks if banks else [ROM]*8); cpu.fl=fl
    orig_rd=cpu.rd; orig_wr=cpu.wr
    def rd(a,size):
        a&=0xFFFFFF
        if 0xF80000<=a<0xFA0000: return fl.rd(a-0xF80000,size)
        return orig_rd(a,size)
    def wr(a,size,v):
        a&=0xFFFFFF
        if 0xF80000<=a<0xFA0000: return fl.wr(a-0xF80000,size,v&(0xFFFF if size==2 else 0xFF))
        if a==0xFC0000: fl.bank=v&7; return
        return orig_wr(a,size,v)
    cpu.rd=rd; cpu.wr=wr
    cpu.mem[0x2000:0x2000+len(FV4)]=FV4
    def w16(a,v): cpu.mem[a]=v>>8; cpu.mem[a+1]=v&255
    w16(0x3000,mode); w16(0x3002,0xA55A if mode==1 else 0); w16(0x301C,bank); w16(0x301E,0x0BA0 if bank==0 else 0)
    cpu.mem[0x2FF0:0x2FF2]=b'\x60\xFE'
    cpu.a[7]=0x1F00-4; cpu.mem[0x1F00-4:0x1F00]=struct.pack('>I',0x2FF0)
    cpu.pc=0x2000; cpu.sr=0x2700
    out=bytearray(); pos=[0]; nblk=[0]
    limit=len(stream) if give is None else give
    def on_tx(b):
        out.append(b)
        if b==6 and pos[0]<limit:
            chunk=stream[pos[0]:pos[0]+256]; pos[0]+=256
            for x in chunk: cpu.rx.append(x)
            nblk[0]+=1
    cpu.on_tx=on_tx
    steps=0
    cpu.mem[0xF80000:0xFA0000]=b'\xff'*0x20000   # a RAM do emulador nao e usada para a janela; so o modelo
    try:
        while steps<maxsteps:
            cpu.run(20000); steps+=20000
            if cpu.pc==0x2FF0 or cpu.pc==0x2FF2: break
    except (Illegal,Halt) as e: out+=('\nEMU STOP %s'%e).encode()
    t=out.decode('latin-1').replace('\r','')
    t=t[t.find('FLASH v4'):]
    # esconde as barras de progresso
    import re
    t=re.sub(r'\[[.#]+\]\s+\d+%\s+F[89][0-9A-F]{4}\x06?','',t)
    return t, cpu
if __name__=='__main__':
    good=ROM
    def corrupt(img,i): return img[:i]+bytes([img[i]^0x40])+img[i+1:]
    cases=[('1 boa, comparar, banco 1',fl4(good,1),None,1,0),
           ('2 byte a mais no inicio, GRAVAR banco 1',b'\x0d'+fl4(good,1),None,1,1),
           ('3 dado corrompido, GRAVAR banco 1',corrupt(good,70000)+fl4(good,1)[131072:],None,1,1),
           ('4 rodape de outro banco, GRAVAR banco 1',fl4(good,3),None,1,1),
           ('5 envio interrompido, GRAVAR banco 1',fl4(good,1),100*256,1,1),
           ('6 imagem boa, GRAVAR banco 1',fl4(good,1),None,1,1),
           ('7 byte a mais, GRAVAR banco 0',b'\x0d'+fl4(good,0),None,0,1),
           ('8 imagem boa, GRAVAR banco 0',fl4(good,0),None,0,1)]
    for nome,stream,give,bank,mode in cases:
        banks=[bytes(good)]*8
        t,cpu=run(stream,bank=bank,mode=mode,give=give,banks=banks)
        fl=cpu.fl
        print('=== ',nome); print(t.strip()[-420:]); 
        print('>> apagamentos=%d gravacoes=%d  banco%d igual ao original: %s  PC final=%X'%(fl.erases,fl.progs,bank,bytes(fl.b[bank])==bytes(good),cpu.pc)); print()
