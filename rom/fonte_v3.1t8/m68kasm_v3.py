#!/usr/bin/env python3
# Montador 68000 minimo (subconjunto), dois passos, sintaxe Motorola.
# v2 (13/11/2026): acrescenta DIVU. Uso: m68kasm.py fonte.asm -> objeto (bytes), simbolos, listagem.
import re, struct, sys

CC = {'t':0,'f':1,'hi':2,'ls':3,'cc':4,'hs':4,'cs':5,'lo':5,'ne':6,'eq':7,'vc':8,'vs':9,'pl':10,'mi':11,'ge':12,'lt':13,'gt':14,'le':15}
SZ = {'b':0,'w':1,'l':2}

class AsmError(Exception): pass

def split_ops(s):
    out=[]; depth=0; cur=''; q=None
    for ch in s:
        if q:
            cur+=ch
            if ch==q: q=None
            continue
        if ch in '"\'': q=ch; cur+=ch; continue
        if ch=='(': depth+=1
        if ch==')': depth-=1
        if ch==',' and depth==0: out.append(cur.strip()); cur=''
        else: cur+=ch
    if cur.strip(): out.append(cur.strip())
    return out

class Asm:
    def __init__(s):
        s.sym={}; s.pc=0; s.out=bytearray(); s.org=None; s.listing=[]; s.pass_no=1
    # ---------- expressoes
    def ev(s,e):
        e=e.strip()
        def chr_sub(m): return str(ord(m.group(1)))
        e=re.sub(r"'(.)'",chr_sub,e)
        e=re.sub(r'\$([0-9A-Fa-f]+)',lambda m:'0x'+m.group(1),e)
        e=re.sub(r'%([01]+)',lambda m:'0b'+m.group(1),e)
        def sub(m):
            n=m.group(0)
            if n.startswith('0x') or n.startswith('0b') or n[0].isdigit(): return n
            if n=='*': return str(s.pc)
            if n.upper() in s.sym: return str(s.sym[n.upper()])
            if s.pass_no==1: return '0'
            raise AsmError('simbolo indefinido: '+n)
        e2=re.sub(r'0[xb][0-9A-Fa-f]+|[A-Za-z_.][A-Za-z_0-9.]*|\d+',sub,e).replace('/','//')
        return int(eval(e2,{'__builtins__':{}}))&0xFFFFFFFF if False else int(eval(e2,{'__builtins__':{}}))
    # ---------- EA
    def parse_ea(s,op):
        """retorna dict(kind=..., ...) kinds: dn an ind post pre disp pcrel absl absw imm sr ccr list"""
        o=op.strip(); ol=o.lower()
        if re.fullmatch(r'd[0-7]',ol): return dict(k='dn',r=int(ol[1]))
        if re.fullmatch(r'a[0-7]|sp',ol): return dict(k='an',r=7 if ol=='sp' else int(ol[1]))
        if ol=='sr': return dict(k='sr')
        if ol=='ccr': return dict(k='ccr')
        if o.startswith('#'): return dict(k='imm',v=o[1:])
        m=re.fullmatch(r'\((a[0-7]|sp)\)\+',ol)
        if m: return dict(k='post',r=7 if m.group(1)=='sp' else int(m.group(1)[1]))
        m=re.fullmatch(r'-\((a[0-7]|sp)\)',ol)
        if m: return dict(k='pre',r=7 if m.group(1)=='sp' else int(m.group(1)[1]))
        m=re.fullmatch(r'\((a[0-7]|sp)\)',ol)
        if m: return dict(k='ind',r=7 if m.group(1)=='sp' else int(m.group(1)[1]))
        m=re.fullmatch(r'(.*)\((a[0-7]|sp)\)',o,re.I)
        if m: return dict(k='disp',v=m.group(1) or '0',r=7 if m.group(2).lower()=='sp' else int(m.group(2)[1]))
        m=re.fullmatch(r'\((.*),(a[0-7]|sp)\)',o,re.I)
        if m: return dict(k='disp',v=m.group(1),r=7 if m.group(2).lower()=='sp' else int(m.group(2)[1]))
        m=re.fullmatch(r'(.*)\(pc\)',o,re.I)
        if m: return dict(k='pcrel',v=m.group(1))
        m=re.fullmatch(r'\((.*),pc\)',o,re.I)
        if m: return dict(k='pcrel',v=m.group(1))
        if '/' in o or re.fullmatch(r'[da][0-7]-[da][0-7]',ol): return dict(k='list',v=o)
        if ol.endswith('.w'): return dict(k='absw',v=o[:-2])
        if ol.endswith('.l'): return dict(k='absl',v=o[:-2])
        return dict(k='absl',v=o)
    def ea_bits(s,ea,size,extpos):
        """retorna (modo,reg,[palavras ext]) ; extpos = endereco da primeira palavra de extensao"""
        k=ea['k']
        if k=='dn': return 0,ea['r'],[]
        if k=='an': return 1,ea['r'],[]
        if k=='ind': return 2,ea['r'],[]
        if k=='post': return 3,ea['r'],[]
        if k=='pre': return 4,ea['r'],[]
        if k=='disp':
            v=s.ev(ea['v'])
            if s.pass_no==2 and not -32768<=v<=32767: raise AsmError('deslocamento fora de faixa')
            return 5,ea['r'],[v&0xFFFF]
        if k=='pcrel':
            t=s.ev(ea['v']); d=t-extpos
            if s.pass_no==2 and not -32768<=d<=32767: raise AsmError('pcrel fora de faixa')
            return 7,2,[d&0xFFFF]
        if k=='absw': return 7,0,[s.ev(ea['v'])&0xFFFF]
        if k=='absl':
            v=s.ev(ea['v'])&0xFFFFFFFF; return 7,1,[v>>16,v&0xFFFF]
        if k=='imm':
            v=s.ev(ea['v'])
            if size=='l': v&=0xFFFFFFFF; return 7,4,[v>>16,v&0xFFFF]
            if size=='b': return 7,4,[v&0xFF]
            return 7,4,[v&0xFFFF]
        raise AsmError('modo de enderecamento invalido: '+str(ea))
    def emit(s,words):
        for w in words: s.out+=struct.pack('>H',w&0xFFFF)
        s.pc+=2*len(words)
    # ---------- reg list
    def reglist(s,txt,predec):
        mask=0
        for part in txt.lower().split('/'):
            m=re.fullmatch(r'([da])([0-7])(?:-([da])([0-7]))?',part)
            if not m: raise AsmError('lista de registradores: '+txt)
            a=(0 if m.group(1)=='d' else 8)+int(m.group(2))
            b=a if not m.group(3) else (0 if m.group(3)=='d' else 8)+int(m.group(4))
            for i in range(a,b+1):
                mask|=(1<<(15-i)) if predec else (1<<i)
        return mask
    # ---------- instrucao
    def instr(s,mn,ops):
        mn=mn.lower(); size=None
        if '.' in mn:
            mn,suf=mn.split('.'); size=suf if suf in SZ else ('s' if suf=='s' else None)
            if size is None: raise AsmError('sufixo invalido')
        def E(i,sz=None):
            return s.parse_ea(ops[i])
        def pos_ext(n_before): return s.pc+2+2*n_before
        # sem operandos
        simple={'rts':0x4E75,'rte':0x4E73,'nop':0x4E71,'illegal':0x4AFC,'reset':0x4E70,'rtr':0x4E77}
        if mn in simple: s.emit([simple[mn]]); return
        # branches
        if mn in ('bra','bsr') or (mn[0]=='b' and mn[1:] in CC and mn not in ('btst','bset','bclr','bchg')):
            c = 0 if mn=='bra' else 1 if mn=='bsr' else CC[mn[1:]]
            t=s.ev(ops[0])
            if size in ('s','b'):
                d=t-(s.pc+2)
                if s.pass_no==2 and (not -128<=d<=127 or d==0): raise AsmError('desvio curto fora de faixa')
                s.emit([0x6000|(c<<8)|(d&0xFF)])
            else:
                d=t-(s.pc+2)
                if s.pass_no==2 and not -32768<=d<=32767: raise AsmError('desvio fora de faixa')
                s.emit([0x6000|(c<<8),d&0xFFFF])
            return
        if mn[:2]=='db' and mn[2:] in CC or mn=='dbra':
            c = 1 if mn=='dbra' else CC[mn[2:]]
            r=int(ops[0][1]); t=s.ev(ops[1]); d=t-(s.pc+2)
            if s.pass_no==2 and not -32768<=d<=32767: raise AsmError('dbcc fora de faixa')
            s.emit([0x50C8|(c<<8)|r,d&0xFFFF]); return
        if mn in ('jsr','jmp'):
            ea=E(0); m,r,ext=s.ea_bits(ea,'l',pos_ext(0))
            s.emit([(0x4E80 if mn=='jsr' else 0x4EC0)|(m<<3)|r]+ext); return
        if mn=='lea':
            ea=E(0); an=E(1); m,r,ext=s.ea_bits(ea,'l',pos_ext(0))
            s.emit([0x41C0|(an['r']<<9)|(m<<3)|r]+ext); return
        if mn=='moveq':
            v=s.ev(ops[0].lstrip('#')); d=E(1)
            if v>=0xFFFFFF80: v-=1<<32
            if s.pass_no==2 and not -128<=v<=255: raise AsmError('moveq fora de faixa')
            s.emit([0x7000|(d['r']<<9)|(v&0xFF)]); return
        if mn in ('move','movea'):
            if size is None: size='w'
            src=E(0); dst=E(1)
            if src['k']=='sr' or dst['k'] in ('sr','ccr'):
                if dst['k']=='sr':
                    m,r,ext=s.ea_bits(src,'w',pos_ext(0)); s.emit([0x46C0|(m<<3)|r]+ext); return
                if src['k']=='sr':
                    m,r,ext=s.ea_bits(dst,'w',pos_ext(0)); s.emit([0x40C0|(m<<3)|r]+ext); return
                raise AsmError('move sr')
            if src['k']=='list' or dst['k']=='list': raise AsmError('use movem')
            sz={'b':1,'w':3,'l':2}[size]
            sm,sr_,sext=s.ea_bits(src,size,pos_ext(0))
            dm,dr,dext=s.ea_bits(dst,size,pos_ext(len(sext)))
            if dst['k']=='an' and size=='b': raise AsmError('movea.b')
            s.emit([(sz<<12)|(dr<<9)|(dm<<6)|(sm<<3)|sr_]+sext+dext); return
        if mn=='movem':
            if size is None: size='w'
            sbit=1 if size=='l' else 0
            if ops[0].lower().startswith(('d','a')) and ('/' in ops[0] or '-' in ops[0]) or (s.parse_ea(ops[0])['k']=='list'):
                ea=E(1); m,r,ext=s.ea_bits(ea,size,pos_ext(1))
                mask=s.reglist(ops[0],ea['k']=='pre')
                s.emit([0x4880|(sbit<<6)|(m<<3)|r,mask]+ext)
            else:
                ea=E(0); m,r,ext=s.ea_bits(ea,size,pos_ext(1))
                mask=s.reglist(ops[1],False)
                s.emit([0x4C80|(sbit<<6)|(m<<3)|r,mask]+ext)
            return
        # ULA: add sub and or eor cmp (+a forms)
        base={'add':0xD000,'sub':0x9000,'and':0xC000,'or':0x8000,'cmp':0xB000,'eor':0xB000}
        if mn in base or mn in ('adda','suba','cmpa'):
            if size is None: size='w'
            src=E(0); dst=E(1)
            if mn in ('adda','suba','cmpa') or (dst['k']=='an' and mn in ('add','sub','cmp')):
                b={'adda':0xD000,'add':0xD000,'suba':0x9000,'sub':0x9000,'cmpa':0xB000,'cmp':0xB000}[mn]
                om=3 if size=='w' else 7
                m,r,ext=s.ea_bits(src,size,pos_ext(0))
                s.emit([b|(dst['r']<<9)|(om<<6)|(m<<3)|r]+ext); return
            sc=SZ[size]
            if mn=='cmp':
                m,r,ext=s.ea_bits(src,size,pos_ext(0)); s.emit([0xB000|(dst['r']<<9)|(sc<<6)|(m<<3)|r]+ext); return
            if mn=='eor':
                m,r,ext=s.ea_bits(dst,size,pos_ext(0)); s.emit([0xB000|(src['r']<<9)|((4+sc)<<6)|(m<<3)|r]+ext); return
            if dst['k']=='dn':
                m,r,ext=s.ea_bits(src,size,pos_ext(0)); s.emit([base[mn]|(dst['r']<<9)|(sc<<6)|(m<<3)|r]+ext); return
            if src['k']=='dn':
                m,r,ext=s.ea_bits(dst,size,pos_ext(0)); s.emit([base[mn]|(src['r']<<9)|((4+sc)<<6)|(m<<3)|r]+ext); return
            raise AsmError(mn+': operandos')
        imm={'addi':0x0600,'subi':0x0400,'cmpi':0x0C00,'andi':0x0200,'ori':0x0000,'eori':0x0A00}
        if mn in imm:
            if size is None: size='w'
            src=E(0); dst=E(1)
            if dst['k'] in ('sr','ccr'): raise AsmError('andi sr nao suportado')
            sm,sr_,sext=s.ea_bits(src,size,pos_ext(0)); m,r,ext=s.ea_bits(dst,size,pos_ext(len(sext)))
            s.emit([imm[mn]|(SZ[size]<<6)|(m<<3)|r]+sext+ext); return
        if mn in ('addq','subq'):
            if size is None: size='w'
            n=s.ev(ops[0].lstrip('#')); dst=E(1)
            if s.pass_no==2 and not 1<=n<=8: raise AsmError('addq fora de faixa')
            m,r,ext=s.ea_bits(dst,size,pos_ext(0))
            s.emit([0x5000|((n&7)<<9)|(0x100 if mn=='subq' else 0)|(SZ[size]<<6)|(m<<3)|r]+ext); return
        one={'clr':0x4200,'tst':0x4A00,'not':0x4600,'neg':0x4400}
        if mn in one:
            if size is None: size='w'
            ea=E(0); m,r,ext=s.ea_bits(ea,size,pos_ext(0)); s.emit([one[mn]|(SZ[size]<<6)|(m<<3)|r]+ext); return
        if mn=='ext':
            d=E(0); s.emit([(0x4880 if size in (None,'w') else 0x48C0)|d['r']]); return
        if mn=='swap':
            d=E(0); s.emit([0x4840|d['r']]); return
        if mn in ('btst','bset','bclr','bchg'):
            t={'btst':0,'bchg':1,'bclr':2,'bset':3}[mn]
            src=E(0); dst=E(1)
            if src['k']=='dn':
                m,r,ext=s.ea_bits(dst,'b',pos_ext(0)); s.emit([0x0100|(src['r']<<9)|(t<<6)|(m<<3)|r]+ext)
            else:
                n=s.ev(src['v']); m,r,ext=s.ea_bits(dst,'b',pos_ext(1)); s.emit([0x0800|(t<<6)|(m<<3)|r,n&0xFF]+ext)
            return
        sh={'as':0,'ls':1,'rox':2,'ro':3}
        m=re.fullmatch(r'(as|ls|rox|ro)([lr])',mn)
        if m:
            if size is None: size='w'
            tt=sh[m.group(1)]; d=1 if m.group(2)=='l' else 0
            src=E(0)
            if len(ops)==1:
                raise AsmError('shift de memoria nao suportado')
            dst=E(1)
            if src['k']=='dn': w=0xE000|(src['r']<<9)|(d<<8)|(SZ[size]<<6)|0x20|(tt<<3)|dst['r']
            else:
                n=s.ev(src['v']); 
                if s.pass_no==2 and not 1<=n<=8: raise AsmError('contagem de deslocamento')
                w=0xE000|((n&7)<<9)|(d<<8)|(SZ[size]<<6)|(tt<<3)|dst['r']
            s.emit([w]); return
        if mn=='addx':
            if size is None: size='w'
            src=E(0); dst=E(1); s.emit([0xD100|(dst['r']<<9)|(SZ[size]<<6)|src['r']]); return
        if mn=='divu':
            src=E(0); dst=E(1); m,r,ext=s.ea_bits(src,'w',pos_ext(0)); s.emit([0x80C0|(dst['r']<<9)|(m<<3)|r]+ext); return
        if mn=='mulu':
            src=E(0); dst=E(1); m,r,ext=s.ea_bits(src,'w',pos_ext(0)); s.emit([0xC0C0|(dst['r']<<9)|(m<<3)|r]+ext); return
        raise AsmError('mnemonico nao suportado: '+mn)
    # ---------- montagem
    def assemble_pass(s,lines):
        s.pc=0; s.out=bytearray(); s.org=None; s.listing=[]; s.segs=[]; s.seg0=0
        for ln,raw in enumerate(lines,1):
            line=raw.split(';')[0] if "'" not in raw.split(';')[0] and '"' not in raw.split(';')[0] else s.strip_comment(raw)
            line=line.rstrip()
            if not line.strip(): continue
            start_pc=s.pc; start_len=len(s.out)
            try:
                m=re.match(r'^([A-Za-z_.][A-Za-z_0-9.]*):\s*(.*)$',line)
                if m:
                    s.sym[m.group(1).upper()]=s.pc; line=m.group(2)
                else:
                    m=re.match(r'^([A-Za-z_.][A-Za-z_0-9.]*)\s+equ\s+(.*)$',line,re.I)
                    if m: s.sym[m.group(1).upper()]=s.ev(m.group(2)); continue
                    m=re.match(r'^([A-Za-z_.][A-Za-z_0-9.]*)\s+set\s+(.*)$',line,re.I)
                    if m: s.sym[m.group(1).upper()]=s.ev(m.group(2)); continue
                line=line.strip()
                if not line: continue
                parts=line.split(None,1); mn=parts[0]; rest=parts[1] if len(parts)>1 else ''
                ml=mn.lower()
                if ml=='org':
                    nv=s.ev(rest)
                    if s.org is None: s.org=nv; s.pc=nv; s.seg0=nv
                    else:
                        s.segs.append((s.seg0,bytes(s.out))); s.out=bytearray(); s.seg0=nv; s.pc=nv; start_len=0
                elif ml=='even':
                    if s.pc&1: s.out+=b'\0'; s.pc+=1
                elif ml in ('dc.b','dc.w','dc.l'):
                    for it in split_ops(rest):
                        if it.startswith('"') and it.endswith('"'):
                            b=it[1:-1].encode('latin-1')
                            if ml=='dc.b': s.out+=b; s.pc+=len(b)
                            else: raise AsmError('string so em dc.b')
                        else:
                            v=s.ev(it)
                            if ml=='dc.b': s.out+=bytes([v&0xFF]); s.pc+=1
                            elif ml=='dc.w': s.out+=struct.pack('>H',v&0xFFFF); s.pc+=2
                            else: s.out+=struct.pack('>I',v&0xFFFFFFFF); s.pc+=4
                elif ml in ('ttl','opt','end','list','nolist','page'): pass
                elif ml.startswith('dcb.'):
                    a=split_ops(rest); n=s.ev(a[0]); v=s.ev(a[1]); sz=ml[-1]
                    for _ in range(n):
                        if sz=='b': s.out+=bytes([v&0xFF]); s.pc+=1
                        elif sz=='w': s.out+=struct.pack('>H',v&0xFFFF); s.pc+=2
                        else: s.out+=struct.pack('>I',v&0xFFFFFFFF); s.pc+=4
                elif ml=='ds.l' and s.ev(rest)==0:
                    while s.pc&3: s.out+=b'\0'; s.pc+=1
                elif ml=='ds.b': n=s.ev(rest); s.out+=bytes(n); s.pc+=n
                elif ml=='ds.w': n=s.ev(rest)*2; s.out+=bytes(n); s.pc+=n
                elif ml=='ds.l': n=s.ev(rest)*4; s.out+=bytes(n); s.pc+=n
                elif ml=='fill':   # fill n, byte : preenche ate endereco
                    a=split_ops(rest); n=s.ev(a[0])-s.pc; 
                    if n<0: raise AsmError('fill: passou do endereco')
                    s.out+=bytes([s.ev(a[1])&0xFF])*n; s.pc+=n
                else:
                    s.instr(mn,split_ops(rest))
                s.listing.append((ln,start_pc,bytes(s.out[start_len:]),raw.rstrip()))
            except AsmError as e:
                raise AsmError('linha %d: %s  [%s]'%(ln,e,raw.strip()))
    def strip_comment(s,raw):
        q=None; out=''
        for ch in raw:
            if q:
                out+=ch
                if ch==q: q=None
                continue
            if ch in '"\'': q=ch; out+=ch; continue
            if ch==';': break
            out+=ch
        return out
    def assemble(s,text):
        lines=text.split('\n')
        s.pass_no=1; s.assemble_pass(lines)
        s.pass_no=2; s.assemble_pass(lines)
        s.segs.append((s.seg0,bytes(s.out)))
        return bytes(s.out)
if __name__=='__main__':
    a=Asm(); text=open(sys.argv[1]).read(); data=a.assemble(text)
    print(len(data),'bytes', 'org',hex(a.org or 0))
