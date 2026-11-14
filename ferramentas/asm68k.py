# Mini-montador 68000 (subconjunto) para o teste serial do Paragon 50
import struct
class A:
    def __init__(s,org): s.org=org; s.items=[]; s.labels={}
    def pc(s): return s.org+sum(i[1] for i in s.items)
    def label(s,n): s.labels[n]=s.pc()
    def w(s,*v): s.items.append(('w',2*len(v),list(v)))
    def l(s,v): s.items.append(('l',4,[v]))
    def raw(s,b): s.items.append(('b',len(b),bytes(b)))
    # ---- instrucoes
    def move_w_imm_d16an(s,imm,d,an): s.w(0x317C|(an<<9),imm&0xffff,d&0xffff)      # move.w #imm,d(an)
    def move_w_imm_abs(s,imm,addr): s.w(0x33FC,imm&0xffff); s.l(addr)              # move.w #imm,abs.l
    def move_b_d16an_dn(s,d,an,dn): s.w(0x1028|(dn<<9)|an,d&0xffff)               # move.b d(an),dn
    def move_b_abs_dn(s,addr,dn): s.w(0x1039|(dn<<9)); s.l(addr)                   # move.b abs.l,dn
    def move_w_dn_d16an(s,dn,d,an): s.w(0x3140|(an<<9)|dn,d&0xffff)                # move.w dn,d(an)
    def move_w_dn_dm(s,dn,dm): s.w(0x3000|(dm<<9)|dn)                              # move.w dn,dm
    def move_b_postinc_dn(s,an,dn): s.w(0x1018|(dn<<9)|an)                         # move.b (an)+,dn
    def move_l_imm_dn(s,imm,dn): s.w(0x203C|(dn<<9)); s.l(imm)
    def move_w_imm_sr(s,imm): s.w(0x46FC,imm)
    def moveq(s,imm,dn): s.w(0x7000|(dn<<9)|(imm&0xff))
    def addq_w(s,n,dn): s.w(0x5040|((n&7)<<9)|dn)
    def subq_l(s,n,dn): s.w(0x5180|((n&7)<<9)|dn)
    def addi_w(s,imm,dn): s.w(0x0640|dn,imm&0xffff)
    def andi_w(s,imm,dn): s.w(0x0240|dn,imm&0xffff)
    def cmpi_w(s,imm,dn): s.w(0x0C40|dn,imm&0xffff)
    def lsr_w4(s,dn): s.w(0xE848|dn)
    def btst(s,n,dn): s.w(0x0800|dn,n)
    def lea_abs(s,addr,an): s.w(0x41F9|(an<<9)); s.l(addr)
    def lea_pc(s,lab,an): s.w(0x41FA|(an<<9)); s.items.append(('rel',2,lab))        # disp rel. ao word de extensao
    def br(s,cc,lab): s.w(0x6000|(cc<<8)); s.items.append(('rel',2,lab))            # bcc.w
    def bra(s,lab): s.br(0x0,lab)
    def bsr(s,lab): s.br(0x1,lab)
    def beq(s,lab): s.br(0x7,lab)
    def bne(s,lab): s.br(0x6,lab)
    def ble(s,lab): s.br(0xF,lab)
    def dbra(s,dn,lab): s.w(0x51C8|dn); s.items.append(('rel',2,lab))
    def rts(s): s.w(0x4E75)
    def nop(s): s.w(0x4E71)
    def align2(s):
        if s.pc()&1: s.raw(b'\x00')
    def build(s):
        out=bytearray(); pc=s.org
        for k,n,v in s.items:
            if k=='w':
                for x in v: out+=struct.pack('>H',x)
            elif k=='l': out+=struct.pack('>I',v[0])
            elif k=='b': out+=v
            elif k=='rel':
                tgt=s.labels[v]; ext=pc            # endereco do word de extensao = pc atual
                d=tgt-ext
                assert -32768<=d<=32767
                out+=struct.pack('>h',d)
            pc+=n
        return bytes(out)
