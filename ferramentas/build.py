import struct, sys
sys.path.insert(0,'.')
from asm68k import A
BASE=0xF8E000; DU=0xFA0000
a=A(BASE)
def strobe_inline():
    a.move_w_imm_d16an(4,0x1E,0); a.move_w_imm_d16an(4,0x1C,0)
    a.moveq(19,7)
    return
# ---- entry
a.move_w_imm_sr(0x2700)
a.lea_abs(DU,0)
a.move_w_imm_d16an(0,8,0)      # ACR=0
a.move_w_imm_d16an(0,0xA,0)    # IMR=0
a.move_w_imm_d16an(0,0x1A,0)   # OPCR=0
a.move_w_imm_d16an(4,0x1E,0)   # ROPR OP2 (watchdog pin high)
a.lea_abs(DU,3);      a.bsr('initch')
a.lea_abs(DU+0x10,3); a.bsr('initch')
a.moveq(0,6)                    # d6 = contador de voltas
a.label('main')
a.lea_abs(DU,3);      a.lea_pc('banA',1); a.bsr('putstr'); a.bsr('status')
a.lea_abs(DU+0x10,3); a.lea_pc('banB',1); a.bsr('putstr'); a.bsr('status')
# OP0 = bit0 de d6, OP1 = bit1 de d6  (SOPR=pino em nivel BAIXO, ROPR=pino ALTO)
a.btst(0,6); a.beq('c0'); a.move_w_imm_d16an(1,0x1C,0); a.bra('t1')
a.label('c0'); a.move_w_imm_d16an(1,0x1E,0)
a.label('t1'); a.btst(1,6); a.beq('c1'); a.move_w_imm_d16an(2,0x1C,0); a.bra('t2')
a.label('c1'); a.move_w_imm_d16an(2,0x1E,0)
a.label('t2')
a.move_l_imm_dn(30000,5)
a.label('ech')
a.lea_abs(DU,3);      a.bsr('rxecho')
a.lea_abs(DU+0x10,3); a.bsr('rxecho')
a.bsr('strobe')
a.dbra(5,'ech')
a.addq_w(1,6)
a.bra('main')
# ---- strobe: pulso baixo em OP2 (DS1232)
a.label('strobe')
a.move_w_imm_d16an(4,0x1E,0); a.move_w_imm_d16an(4,0x1C,0)
a.moveq(19,7); a.label('sd'); a.dbra(7,'sd')
a.move_w_imm_d16an(4,0x1E,0); a.rts()
# ---- initch (a3 = base do canal)
a.label('initch')
for off,val in [(4,0x1A),(0,0x13),(0,0x07),(2,0xBB),(4,0x20),(4,0x30),(4,0x05),(4,0x40)]:
    a.move_w_imm_d16an(val,off,3)
a.rts()
# ---- putc: d0 = byte, a3 = canal
a.label('putc')
a.bsr('strobe')
a.label('pw'); a.move_b_d16an_dn(3,3,1); a.btst(2,1); a.beq('pw')
a.move_w_dn_d16an(0,6,3); a.rts()
# ---- putstr: a1 = string (0 final)
a.label('putstr')
a.move_b_postinc_dn(1,0); a.beq('ps9'); a.bsr('putc'); a.bra('putstr')
a.label('ps9'); a.rts()
# ---- hexdig_put: d0 = nibble (baixo)
a.label('hexput')
a.andi_w(0xF,0); a.cmpi_w(9,0); a.ble('hx'); a.addq_w(7,0)
a.label('hx'); a.addi_w(0x30,0); a.bra('putc')
# ---- puthex: d2 = byte
a.label('puthex')
a.move_w_dn_dm(2,0); a.lsr_w4(0); a.bsr('hexput')
a.move_w_dn_dm(2,0); a.bsr('hexput'); a.rts()
# ---- status: imprime "IP=hh N=hh\r\n" no canal a3
a.label('status')
a.lea_pc('sIP',1); a.bsr('putstr')
a.move_b_d16an_dn(0x1B,0,2); a.bsr('puthex')      # d2 = IP (le do a0)
a.lea_pc('sN',1); a.bsr('putstr')
a.move_w_dn_dm(6,2); a.bsr('puthex')
a.lea_pc('sCR',1); a.bsr('putstr'); a.rts()
# ---- rxecho: se RxRDY, le e devolve
a.label('rxecho')
a.move_b_d16an_dn(3,3,1); a.btst(0,1); a.beq('rx9')
a.move_b_d16an_dn(7,3,0); a.bsr('putc')
a.label('rx9'); a.rts()
# ---- strings
a.label('banA'); a.raw(b'\r\n=== PARAGON50 TESTE SERIAL === canal A ===\r\n'+b'\x00')
a.label('banB'); a.raw(b'\r\n=== PARAGON50 TESTE SERIAL === canal B ===\r\n'+b'\x00')
a.label('sIP'); a.raw(b'IP=\x00')
a.label('sN');  a.raw(b' N=\x00')
a.label('sCR'); a.raw(b'  (OP0=bit0 de N, OP1=bit1; bit=1 -> pino BAIXO)\r\n\x00')
a.align2()
# ---- excecao: '!' sem parar nos dois canais
a.label('exc')
a.move_w_imm_sr(0x2700); a.lea_abs(DU,0)
a.label('e1')
a.move_w_imm_d16an(4,0x1E,0); a.move_w_imm_d16an(4,0x1C,0); a.moveq(19,7)
a.label('e2'); a.dbra(7,'e2'); a.move_w_imm_d16an(4,0x1E,0)
a.move_b_d16an_dn(3,0,1); a.btst(2,1); a.beq('e4'); a.move_w_imm_d16an(0x21,6,0)
a.label('e4'); a.move_b_d16an_dn(0x13,0,1); a.btst(2,1); a.beq('e1'); a.move_w_imm_d16an(0x21,0x16,0); a.bra('e1')
code=a.build()
lin=bytearray(open('/mnt/attach/outputs/Paragon50_ROM_F80000.bin','rb').read())
orig=bytes(lin)
assert all(b==0 for b in lin[BASE-0xF80000:BASE-0xF80000+len(code)])
lin[BASE-0xF80000:BASE-0xF80000+len(code)]=code
assert lin[0x4022:0x4028]==bytes.fromhex('4eb900f8d99e')
lin[0x4022:0x4028]=bytes.fromhex('4ef9')+struct.pack('>I',BASE)
exc=a.labels['exc']
for v in range(2,201): lin[v*4:v*4+4]=struct.pack('>I',exc)
open('test.lin','wb').write(lin); open('code.bin','wb').write(code)
print(len(code),hex(BASE),'exc',hex(exc), {k:hex(v) for k,v in a.labels.items()})
# split
def split(l):
    qs=[l[i*0x4000:(i+1)*0x4000] for i in range(4)]
    il=b''.join(qs[i] for i in (3,2,1,0))
    return il[0::2], il[1::2]
h0,l0=split(orig)
assert h0==open('/mnt/user-data/uploads/Paragon_50_HI.BIN','rb').read() and l0==open('/mnt/user-data/uploads/Paragon_50_LO.BIN','rb').read()
h,l=split(bytes(lin))
open('TESTE_SERIAL_HI.bin','wb').write(h); open('TESTE_SERIAL_LO.bin','wb').write(l)
print('split ok, validado contra originais')
