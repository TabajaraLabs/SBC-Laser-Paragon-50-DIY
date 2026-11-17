import sys, json; sys.path.insert(0,'/home/claude/sbc-laser-paragon-50-diy/ferramentas')
import m68kasm_v3 as M, srec
sym=json.load(open('lcd_i2c_ram_v1_sym.json')); blob=open('lcd_i2c_ram_v1.bin','rb').read()
prog="""PUTS equ $F8080C
STROBE equ $F8082A
        org $2000
        lea tm(pc),a1
        jsr PUTS
        jsr $3000
        tst.b $5F034
        bne ok
        lea tn(pc),a1
        jsr PUTS
        rts
ok:     lea tk(pc),a1
        jsr PUTS
        moveq #0,d1
        lea t1(pc),a0
        bsr at
        moveq #1,d1
        lea t2(pc),a0
        bsr at
        moveq #2,d1
        lea t3(pc),a0
        bsr at
        moveq #3,d1
        lea t4(pc),a0
        bsr at
        jsr $%X
        lea tw(pc),a1
        jsr PUTS
wk:     jsr STROBE
        btst #0,$FA0003
        beq wk
        move.b $FA0007,d0
        jsr $3008
        lea tf(pc),a1
        jsr PUTS
        rts
at:     move.l a0,-(sp)
        move.l #0,-(sp)
        move.l d1,-(sp)
        jsr $3004
        add.l #12,sp
        rts
tm:     dc.b "LCD_I2C_RAM v1 - servico de LCD I2C (corpo em $3000), so RAM.",13,10,0
tn:     dc.b "Sem ACK em $27 nem $3F: nenhum LCD.",13,10,0
tk:     dc.b "LCD achado e inicializado (endereco I2C gravado em $5F034).",13,10,0
tw:     dc.b "Linhas escritas pelo servico (+ asterisco no fim da linha 2). Tecla para sair.",13,10,0
tf:     dc.b "Fim.",13,10,0
t1:     dc.b "PARAGON 50 - servico de LCD I2C v1",0
t2:     dc.b "1234567890123456789012345678901234567890",0
t3:     dc.b "Linha 3 pelo controlador 2 (E2)",0
t4:     dc.b "Tabajara Labs 2026 - 40x4 via I2C",0
""" % sym['ACTV']
a=M.Asm(); d=a.assemble(prog)
segs=[(0x2000,bytes(d)),(0x3000,blob)]
assert 0x2000+len(d)<0x3000
print(len(d),len(blob))
img=bytes(d)+b'\0'*(0x1000-len(d))+blob
open('../../programas/lcd_i2c_ram_v1_run.s19','w',newline='').write(srec.make(img,0x2000,0x2000))
open('lcd_i2c_ram_v1_img.bin','wb').write(img)
print('s19 gerado',len(img))
