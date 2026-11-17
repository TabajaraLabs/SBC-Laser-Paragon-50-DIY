"""t_lcdblob_v1.py - testa o servico de LCD I2C (gen_lcdblob_i2c_v1) no emulador: backpack em $27, em $3F e ausente."""
import sys; sys.path.insert(0,'.')
import m68kasm_v3 as M
src=open('t_lcd40_v1.py').read(); exec(src[:src.index('for addr7,label')])
BASE='../fontes/lcd_i2c/'
ent=open(BASE+'lcd_i2c_blob_v1_ent.bin','rb').read(); body=open(BASE+'lcd_i2c_blob_v1.bin','rb').read()
prog="""        org $2000
        jsr $F80614
        moveq #0,d1
        lea t1(pc),a0
        bsr at
        lea t2(pc),a0
        moveq #1,d1
        bsr at
        lea t3(pc),a0
        moveq #2,d1
        bsr at
        lea t4(pc),a0
        moveq #3,d1
        bsr at
        jsr $F8%s
        jsr $F8061C
        rts
at:     move.l a0,-(sp)
        move.l #0,-(sp)
        move.l d1,-(sp)
        jsr $F80618
        add.l #12,sp
        rts
t1:     dc.b "PARAGON via I2C",0
t2:     dc.b "1234567890123456789012345678901234567890",0
t3:     dc.b "Linha 3 E2",0
t4:     dc.b "Relogio 12h34",0
"""
import json
sym=json.load(open(BASE+'lcd_i2c_blob_v1_sym.json'))
for addr7,label in ((0x27,'LCD em $27'),(0x3F,'LCD em $3F'),(0x50,'sem LCD')):
    c=Bus(addr7)
    for fn,org in (('lcd40_stubs_v1.asm',None),):
        a=M.Asm(); a.assemble(open('../programas/lcd40_stubs_v1.asm').read())
        for st,b in a.segs: c.mem[st:st+len(b)]=b
    c.mem[0xF80614:0xF80614+len(ent)]=ent; c.mem[0xF87400:0xF87400+len(body)]=body
    a=M.Asm(); d=a.assemble(prog % ('%06X'%sym['ACTV'])[2:]) if False else a.assemble(prog.replace('$F8%s','$%X'%sym['ACTV']))
    c.mem[0x2000:0x2000+len(d)]=d
    c.pc=0x2000; c.a[7]=0x7000; c.sr=0x2700; c.rx=[]
    steps=0
    try:
        while steps<20_000_000:
            c.step(); steps+=1
            if c.pc==0x2000+len(d)-0 and False: break
            if c.a[7]==0x7000 and steps>50 and c.pc<0x3000 and c.mem[c.pc:c.pc+2]==b'Nu' and steps>1000 and False: break
            if steps>50 and c.a[7]==0x7004: break
    except Exception as ex: print('parou:',ex,'pc=%06X'%c.pc)
    print('==',label,'passos',steps,'bytes I2C',c.nbytes)
    for k in (0,1): print(' E%d:'%(k+1),repr(c.ctrl[k].line(0)),repr(c.ctrl[k].line(1)))
