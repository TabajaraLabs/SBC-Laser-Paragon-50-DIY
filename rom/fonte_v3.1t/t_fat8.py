import sys, struct
sys.path.insert(0,'.')
from emu68k import CPU, Illegal, Halt
import m68kasm_v3
import t_fat
from t_fat import make_card

def fat_read(card):
    """leitor independente: devolve {caminho: bytes} e valida a consistencia"""
    b=card.read(0); bps,spc,res,nf,rootent=struct.unpack_from('<HBHBH',b,11); fatsz=struct.unpack_from('<H',b,22)[0]
    total=struct.unpack_from('<I',b,32)[0]
    fats=[b''.join(card.read(res+k*fatsz+j) for j in range(fatsz)) for k in range(nf)]
    assert all(f==fats[0] for f in fats), 'FAT1 != FAT2'
    fat=fats[0]; rootsec=res+nf*fatsz; rootsz=rootent*32//512; data=rootsec+rootsz
    seen={}
    def chain(c):
        out=[]
        while 2<=c<0xFFF8:
            assert c not in seen, 'cluster %d usado duas vezes'%c
            seen[c]=1; out.append(c); c=struct.unpack_from('<H',fat,c*2)[0]
        return out
    def cdata(cl): return b''.join(card.read(data+(c-2)*spc+j) for c in cl for j in range(spc))
    files={}
    def walk(raw,prefix):
        for i in range(0,len(raw),32):
            e=raw[i:i+32]
            if e[0]==0: break
            if e[0]==0xE5 or e[11]&0x0F==0x0F or e[11]&8: continue
            nm=e[0:8].decode('latin-1').rstrip()+('.'+e[8:11].decode('latin-1').rstrip() if e[8:11].strip() else '')
            cl=struct.unpack_from('<H',e,26)[0]; sz=struct.unpack_from('<I',e,28)[0]
            if e[11]&0x10:
                if nm in('.','..'): continue
                ch=chain(cl); walk(cdata(ch),prefix+nm+'/')
            else:
                ch=chain(cl) if cl else []
                assert len(ch)==-(-sz//(spc*512)), (nm,len(ch),sz)
                files[prefix+nm]=cdata(ch)[:sz]
    walk(b''.join(card.read(rootsec+j) for j in range(rootsz)),'')
    return files

def run(card, cmds, maxsteps=2_000_000_000):
    asm=m68kasm_v3.Asm(); asm.assemble('RCBANK equ 0\nSHORG equ $F84000\nFLIMG equ $F86400\nFLLEN equ 4072\n'+open('fatsh_v8.asm').read()); ad,img=asm.segs[0]; img=bytes(img); sym=asm.sym
    cpu=CPU(); rom=open('PARAGON50_F80000_v2.6.bin','rb').read(); cpu.mem[0xF80000:0xF80000+len(rom)]=rom
    cpu.mem[ad:ad+len(img)]=img
    out=bytearray(); cpu.on_tx=lambda b: out.append(b)
    def sdinit_hook(c):
        c.pc=c.pop32(); c.d[0]=0; c.mem[sym['SDHC']:sym['SDHC']+2]=b'\x00\x01'
    def sdread_hook(c):
        secn=struct.unpack('>I',c.mem[sym['SECN']:sym['SECN']+4])[0]; dst=struct.unpack('>I',c.mem[sym['RDST']:sym['RDST']+4])[0]
        c.mem[dst:dst+512]=card.read(secn); c.stats[0]+=1; c.pc=c.pop32(); c.d[0]=0
        for k in range(1,7): c.d[k]=0xDEAD0000+k
        for k in range(0,3): c.a[k]=0xBAD00000+k
    def sdwrite_hook(c):
        secn=struct.unpack('>I',c.mem[sym['SECN']:sym['SECN']+4])[0]; src=struct.unpack('>I',c.mem[sym['WST']:sym['WST']+4])[0]
        card.sec[secn]=bytes(c.mem[src:src+512]); c.stats[1]+=1; c.pc=c.pop32(); c.d[0]=0
    cpu.stats=[0,0]
    cpu.watch[sym['SDINIT']]=sdinit_hook; cpu.watch[sym['SDREAD_I']]=sdread_hook; cpu.watch[sym['SDWRITE']]=sdwrite_hook
    cpu.a[7]=0x1F00-4; cpu.mem[0x1F00-4:0x1F00]=struct.pack('>I',0x7000); cpu.mem[0x7000:0x7002]=b'\x60\xFE'
    cpu.pc=ad; cpu.sr=0x2700
    i=0; steps=0
    try:
        while steps<maxsteps:
            cpu.run(20000); steps+=20000
            txt=out.decode('latin-1')
            while i<len(cmds) and txt.count('FAT> ')>i:
                for ch in cmds[i]+'\r': cpu.rx.append(ord(ch))
                i+=1
            if i>=len(cmds) and txt.count('FAT> ')>=len(cmds)+1: break
            if cpu.pc==0x7000: break
    except (Illegal,Halt) as e: out+=('\nEMU STOP %s pc=%06X'%(e,cpu.pc)).encode()
    return out.decode('latin-1').replace('\r',''), cpu

if __name__=='__main__':
    card,files=make_card()
    base=fat_read(card); print('antes:',sorted(base))
    cmds=['I','L FORTH/forth_bank_v1.bin 40000','W COPIA.BIN 40000 20000','W peq.txt 40000 100','W FORTH/NOVO.BIN 40000 3000','D','D FORTH',
          'W peq.txt 40001 50','K TESTE.TXT','C FORTH','W rel.bin 40000 10','C /','D','W nome_muito_longo.bin 40000 10','W nada/x.bin 40000 10']
    t,cpu=run(card,cmds)
    print(t[-2600:])
    after=fat_read(card)
    print('depois:',sorted(after))
    mem=lambda a,n: bytes(cpu.mem[a:a+n])
    forth=files['FORTH/forth_bank_v1.bin']
    assert after['COPIA.BIN']==forth, 'COPIA diferente'
    assert after['PEQ.TXT']==mem(0x40001,0x50)
    assert after['FORTH/NOVO.BIN']==forth[:0x3000]
    assert 'TESTE.TXT' not in after
    assert after['FORTH/REL.BIN']==forth[:16]
    assert after['PRELUDE.FS']==base['PRELUDE.FS']
    print('TUDO OK; setores lidos',cpu.stats[0],'gravados',cpu.stats[1])
