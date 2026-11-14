import sys, struct
sys.path.insert(0,'.')
from emu68k import CPU, Illegal, Halt
import m68kasm_v3

def lfn_entries(longname, sfn11):
    chk=0
    for c in sfn11: chk=(((chk&1)<<7)+(chk>>1)+c)&0xFF
    u=longname.encode('utf-16-le'); n=len(longname)+1
    chars=[u[i]|(u[i+1]<<8) for i in range(0,len(u),2)]+[0]
    while len(chars)%13: chars.append(0xFFFF)
    parts=[chars[i:i+13] for i in range(0,len(chars),13)]
    out=[]
    for k,p in enumerate(parts):
        seq=k+1|(0x40 if k==len(parts)-1 else 0)
        e=bytearray(32); e[0]=seq; e[11]=0x0F; e[13]=chk
        offs=[1,3,5,7,9,14,16,18,20,22,24,28,30]
        for o,c in zip(offs,p): e[o]=c&255; e[o+1]=c>>8
        out.append(bytes(e))
    return out[::-1]
def sfn(name):
    n,_,e=name.partition('.'); return (n.upper().ljust(8)+e.upper().ljust(3)).encode()
def dent(s11,attr,cl,size):
    e=bytearray(32); e[0:11]=s11; e[11]=attr; e[26:28]=struct.pack('<H',cl&0xFFFF); e[28:32]=struct.pack('<I',size); return bytes(e)

class Fat16:
    def __init__(s, spc=32, total=1987335, fatsz=243, label=b'CARTAOTL   '):
        s.spc=spc; s.total=total; s.fatsz=fatsz; s.res=1; s.nf=2; s.rootent=512
        s.fat={0:0xFFF8,1:0xFFFF}; s.next=2; s.sec={}
        s.rootsec=s.res+s.nf*fatsz; s.rootsz=(s.rootent*32)//512; s.data=s.rootsec+s.rootsz
        b=bytearray(512); b[0:3]=b'\xEB\x3C\x90'; b[3:11]=b'MSWIN4.1'; struct.pack_into('<HBHBHHBHHHII',b,11,512,spc,s.res,s.nf,s.rootent,0,0xF8,fatsz,63,32,0,total)
        b[36]=0x80; b[38]=0x29; b[39:43]=b'\xAB\xFF\xBA\x4E'; b[43:54]=label; b[54:62]=b'FAT16   '; b[510]=0x55; b[511]=0xAA
        s.sec[0]=bytes(b)
        s.root=[]
    def alloc(s,data):
        n=max(1,-(-len(data)//(s.spc*512))) if data else 0
        if n==0: return 0
        first=s.next
        for i in range(n):
            c=s.next; s.next+=1; s.fat[c]=c+1 if i<n-1 else 0xFFFF
            chunk=data[i*s.spc*512:(i+1)*s.spc*512].ljust(s.spc*512,b'\0')
            base=s.data+(c-2)*s.spc
            for j in range(s.spc): s.sec[base+j]=chunk[j*512:(j+1)*512]
        return first
    def dirdata(s,entries): return b''.join(entries)
    def finish(s):
        import itertools
        rd=b''.join(s.root).ljust(s.rootsz*512,b'\0')
        for j in range(s.rootsz): s.sec[s.rootsec+j]=rd[j*512:(j+1)*512]
        fatbytes=bytearray(s.fatsz*512)
        for c,v in s.fat.items(): struct.pack_into('<H',fatbytes,c*2,v)
        for k in range(2):
            for j in range(s.fatsz): s.sec[s.res+k*s.fatsz+j]=bytes(fatbytes[j*512:(j+1)*512])
        return s
    def read(s,n): return s.sec.get(n,b'\0'*512)

def make_card():
    f=Fat16(); files={}
    files['TESTE.TXT']=b'Isso\r\ne um\r\nteste\r\ncom \r\nalgumas \r\nlinhas \r\nde texto'
    files['PRELUDE.FS']=bytes((i*7+3)&0xFF if (i*7+3)&0xFF>=32 else 65 for i in range(6104))
    forth=bytes((i*31+i//251)&0xFF for i in range(131072)); files['FORTH/forth_bank_v1.bin']=forth
    meu=bytes((i*13)&0xFF for i in range(3000)); files['Meu Programa Teste.bas']=meu
    root=[]
    root.append(dent(b'OLD     TXT',0x20,0,0)[:0]+bytes([0xE5])+dent(b'OLD     TXT',0x20,0,0)[1:])  # apagado
    # System Volume Information (hidden dir)
    svi=f.alloc(b'\0'*100)
    root+=lfn_entries('System Volume Information',b'SYSTEM~1   ')+[dent(b'SYSTEM~1   ',0x16,svi,0)]
    c=f.alloc(files['TESTE.TXT']); root.append(dent(b'TESTE   TXT',0x20,c,len(files['TESTE.TXT'])))
    c=f.alloc(files['PRELUDE.FS']); root.append(dent(b'PRELUDE FS ',0x20,c,len(files['PRELUDE.FS'])))
    # pasta FORTH
    fc=f.alloc(forth); sub=[dent(b'.          ',0x10,0,0),dent(b'..         ',0x10,0,0)]
    # dir cluster dedicado
    fdir_first=f.next
    sub+=lfn_entries('forth_bank_v1.bin',b'EFORTH~1BIN')+[dent(b'EFORTH~1BIN',0x20,fc,len(forth))]
    dcl=f.alloc(b''.join(sub)); 
    # corrige '.' com o cluster da propria pasta
    sub[0]=dent(b'.          ',0x10,dcl,0); f.sec[f.data+(dcl-2)*f.spc]=(b''.join(sub)).ljust(512,b'\0')[:512] if len(b''.join(sub))<=512 else f.sec[f.data+(dcl-2)*f.spc]
    root.append(dent(b'FORTH      ',0x10,dcl,0))
    c=f.alloc(meu); root+=lfn_entries('Meu Programa Teste.bas',b'MEUPRO~1BAS')+[dent(b'MEUPRO~1BAS',0x20,c,len(meu))]
    f.root=root
    return f.finish(), files

def run_shell(card, cmds, maxsteps=300_000_000):
    asm=m68kasm_v3.Asm(); asm.assemble(open('fatsh_v1.asm').read()); ad,img=asm.segs[0]; img=bytes(img)
    sym=asm.sym
    cpu=CPU(); rom=open('PARAGON50_F80000_v2.6.bin','rb').read(); cpu.mem[0xF80000:0xF80000+len(rom)]=rom
    cpu.mem[ad:ad+len(img)]=img
    out=bytearray(); cpu.on_tx=lambda b: out.append(b)
    def sdinit_hook(c):
        c.pc=c.pop32(); c.d[0]=0
        c.mem[sym['SDHC']:sym['SDHC']+2]=b'\x00\x01'
    def sdread_hook(c):
        secn=struct.unpack('>I',c.mem[sym['SECN']:sym['SECN']+4])[0]
        dst=struct.unpack('>I',c.mem[sym['RDST']:sym['RDST']+4])[0]
        c.mem[dst:dst+512]=card.read(secn); c.stats[0]+=1
        c.pc=c.pop32(); c.d[0]=0
    cpu.stats=[0]
    cpu.watch[sym['SDINIT']]=sdinit_hook; cpu.watch[sym['SDREAD']]=sdread_hook
    cpu.a[7]=0x1F00-4; cpu.mem[0x1F00-4:0x1F00]=struct.pack('>I',0x3E00); cpu.mem[0x3E00:0x3E02]=b'\x60\xFE'
    cpu.pc=ad; cpu.sr=0x2700
    pos=0; i=0; steps=0
    try:
        while steps<maxsteps:
            cpu.run(20000); steps+=20000
            txt=out.decode('latin-1')
            while i<len(cmds) and txt.count('FAT> ')>i:
                for ch in cmds[i]+'\r': cpu.rx.append(ord(ch))
                i+=1
            if i>=len(cmds) and txt.count('FAT> ')>=len(cmds)+1: break
            if cpu.pc in (0x3E00,): break
    except (Illegal,Halt) as e: out+=('\nEMU STOP %s pc=%06X'%(e,cpu.pc)).encode()
    return out.decode('latin-1').replace('\r',''), cpu, sym
if __name__=='__main__':
    card,files=make_card()
    cmds=['I','D','D FORTH','T TESTE.TXT','T prelude.fs','D nada','L FORTH/forth_bank_v1.bin 40000','L Meu Programa Teste.bas 60000','T FORTH/EFORTH~1.BIN','S']
    t,cpu,sym=run_shell(card,cmds)
    print(t[:3000] if len(t)<6000 else t[:2500]+'\n...\n'+t[-1500:])
    def mem(a,n): return bytes(cpu.mem[a:a+n])
    print('forth ok:',mem(0x40000,131072)==files['FORTH/forth_bank_v1.bin'])
    print('meu ok:',mem(0x60000,3000)==files['Meu Programa Teste.bas'])
    print('setores lidos',cpu.stats[0])
