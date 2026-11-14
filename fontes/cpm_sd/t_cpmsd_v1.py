import sys, struct, json
sys.path.insert(0,'/home/claude/rom24/v26'); sys.path.insert(0,'.')
from emu68k import CPU, Illegal, Halt
from t_fat import Fat16, dent
import cpmfs
BIN=sys.argv[1] if len(sys.argv)>1 else 'build/cpm_rom.bin'
ORG=0xF88000
MAP={l.split()[1]:int(l.split()[0],16) for l in open(BIN.replace('.bin','.map')) if len(l.split())==2}
SYM=json.load(open('sdb/blob_sym.json')); base=MAP['sd_init']
H=lambda n: base+SYM[n]
# ---- cartao: \CPM\A.DSK (fragmentada) e B.DSK, mais um arquivo qualquer
f=Fat16(spc=32)
imgs={'A':bytearray(open('/tmp/cpmt/A.dsk','rb').read()),'B':bytearray(b'\xE5'*524288)}
def put_frag(data, interleave):
    cl=[]; 
    for i in range(0,len(data),f.spc*512):
        c=f.next; f.next+=1; cl.append(c)
        chunk=data[i:i+f.spc*512].ljust(f.spc*512,b'\0'); b=f.data+(c-2)*f.spc
        for j in range(f.spc): f.sec[b+j]=chunk[j*512:(j+1)*512]
        if interleave: f.next+=1          # deixa um buraco: imagem fragmentada
    for i,c in enumerate(cl): f.fat[c]=cl[i+1] if i+1<len(cl) else 0xFFFF
    return cl[0]
a_first=put_frag(bytes(imgs['A']),True); b_first=put_frag(bytes(imgs['B']),False)
cpmdir=[dent(b'.          ',0x10,0,0),dent(b'..         ',0x10,0,0),dent(b'A       DSK',0x20,a_first,524288),dent(b'B       DSK',0x20,b_first,524288)]
dc=f.alloc(b''.join(cpmdir))
f.root=[dent(b'CARTAOTL   ',0x08,0,0),dent(b'CPM        ',0x10,dc,0)]
f.finish(); card=f
print('A.DSK cluster inicial',a_first,'B',b_first,'dir',dc)
cpu=CPU(); d=open(BIN,'rb').read(); cpu.mem[ORG:ORG+len(d)]=d
out=bytearray(); cpu.on_tx=lambda b: out.append(b)
stat={'rd':0,'wr':0}
def rd32(a): return struct.unpack('>I',cpu.mem[a:a+4])[0]
def h_init(c): c.pc=c.pop32(); c.d[0]=0
def h_rd(c):
    s=rd32(0x5F020); dst=rd32(0x5F024); c.mem[dst:dst+512]=card.read(s); c.pc=c.pop32(); c.d[0]=0; stat['rd']+=1
    for k in range(1,7): c.d[k]=0xDEAD0000+k
    for k in range(0,3): c.a[k]=0xBAD00000+k
def h_wr(c):
    s=rd32(0x5F020); src=rd32(0x5F028); card.sec[s]=bytes(c.mem[src:src+512]); c.pc=c.pop32(); c.d[0]=0; stat['wr']+=1
cpu.watch[H('SDINIT')]=h_init; cpu.watch[H('SDREAD_I')]=h_rd; cpu.watch[H('SDWRITE')]=h_wr
cpu.mem[0xF80100:0xF80102]=b'\x4A\xFC'
for v in range(256):
    cpu.mem[v*4:v*4+4]=(0xF80200+2*v).to_bytes(4,'big'); cpu.mem[0xF80200+2*v:0xF80202+2*v]=b'\x4A\xFC'
cpu.mem[0:4]=(0x1F00).to_bytes(4,'big')
cpu.ssp=0x1F00; cpu.a[7]=0x1F00; cpu.sr=0x2700; cpu.pc=MAP.get('romstart',ORG)
script=[("A>","DIR\r"),("A>","TYPE LEIAME.TXT\r"),("A>","PIP B:COPIA.TXT=A:LEIAME.TXT\r"),("A>","DIR B:\r"),("A>","TYPE B:COPIA.TXT\r"),("A>","ERA A:DUMP.68K\r"),("A>","DIR\r"),("A>","B:\r"),("B>","DIR\r"),("B>","")]
pos=0;i=0;steps=0
try:
    while steps<400_000_000:
        cpu.run(20000); steps+=20000
        txt=out.decode('latin-1')
        if steps%10_000_000==0: open('/tmp/cpmsd_prog.txt','w').write('%d i=%d pc=%06X rd=%d wr=%d\n'%(steps,i,cpu.pc,stat['rd'],stat['wr'])+txt.replace('\r','')[-1200:])
        while i<len(script) and script[i][0] in txt[pos:]:
            k=txt.index(script[i][0],pos)+len(script[i][0]); pos=k
            cpu.run(300000); steps+=300000
            for ch in script[i][1]: cpu.rx.append(ord(ch))
            i+=1
        if i>=len(script): cpu.run(2_000_000); break
except (Illegal,Halt) as e: print('EMU STOP',e,'pc=%06X'%cpu.pc)
print(out.decode('latin-1').replace('\r',''))
print('steps',steps,stat)
# ---- remonta as imagens a partir do cartao (seguindo a FAT) e confere com cpmfs
def image_of(first):
    data=b''; c=first
    while c<0xFFF0:
        b=f.data+(c-2)*f.spc
        data+=b''.join(card.read(b+j) for j in range(f.spc)); c=f.fat[c]
    return bytearray(data[:524288])
A=image_of(a_first); B=image_of(b_first)
print('A.DSK:',sorted(cpmfs.ls(A))); print('B.DSK:',sorted(cpmfs.ls(B)))
print('COPIA.TXT igual ao LEIAME.TXT:', 'COPIA.TXT' in cpmfs.ls(B) and cpmfs.get(B,'COPIA.TXT')==cpmfs.get(bytearray(imgs['A']),'LEIAME.TXT'))
