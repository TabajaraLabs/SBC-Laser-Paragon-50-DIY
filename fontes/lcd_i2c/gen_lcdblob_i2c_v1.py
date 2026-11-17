#!/usr/bin/env python3
"""gen_lcdblob_i2c_v1.py - servico de LCD por I2C (backpack PCF8574, $27 ou $3F) para o BIOS/monitor do PARAGON 50.
Substitui o gen_lcdblob_v1 (LCD paralelo 20x4) com as MESMAS entradas: +0 lcd_start(), +4 lcd_at(linha,col,texto), +8 lcd_hold(); actv/actv_off.
Convencao C: argumentos na pilha (linha, coluna, texto), como no modulo antigo. As 3 entradas ($F80614/18/1C, bra.w) saltam para o corpo em $F87400 (area livre $F873E8-$F87EE0 da imagem; 426 bytes no vao original nao bastam).
Uso:  gen_lcdblob_i2c_v1.py [ORG hex] [CTRL 1|2] [saida.bin]
  CTRL=2 : LCD 40x4 (WH4004A, 2 controladores: linhas 1-2 em E1=P2, linhas 3-4 em E2=P1)
  CTRL=1 : LCD 20x4 comum (um controlador, E=P2)
Variaveis na RAM alta: STAR $5F030 (marca '*'), EM $5F032 (mascara do E), ADDR $5F034 (endereco I2C de escrita; 0 = sem LCD)."""
import sys, json
sys.path.insert(0,'/home/claude/sbc-laser-paragon-50-diy/ferramentas')
import m68kasm_v3
ORG=int(sys.argv[1],16) if len(sys.argv)>1 else 0xF87400     # corpo; as 3 entradas ficam em $F80614 (bra.w) so se ENT for dado
ENT=int(sys.argv[4],16) if len(sys.argv)>4 else (0xF80614 if ORG==0xF87400 else None)
CTRL=int(sys.argv[2]) if len(sys.argv)>2 else 2
OUT=sys.argv[3] if len(sys.argv)>3 else 'lcd_i2c_blob_v1.bin'
if CTRL==2:
    goto="""lcd_goto: move.w #4,EM
        cmpi.w  #2,d0
        blt     lg1
        move.w  #2,EM
lg1:    andi.w  #1,d0
        lsl.w   #6,d0
        add.w   d1,d0
        ori.b   #$80,d0
        bra     lcd_cmd
"""
    inits="""        move.w  #4,EM
        bsr     init1
        move.w  #2,EM
        bsr     init1
"""
else:
    goto="""lcd_goto: move.w #4,EM
        andi.w  #3,d0
        lea     ltab(pc),a0
        adda.w  d0,a0
        move.b  (a0),d0
        add.b   d1,d0
        bra     lcd_cmd
ltab:   dc.b    $80,$C0,$94,$D4
"""
    inits="""        move.w  #4,EM
        bsr     init1
"""
src="""IOL20   equ $020020
PORTB   equ $020028
STROBE  equ $F8082A
STAR    equ $5F030
EM      equ $5F032
ADDR    equ $5F034
%s        org $%X
%si_start: movem.l d2-d7/a2-a6,-(sp)
        move.w  #0,STAR
        move.b  #$4E,ADDR
        bsr     probe
        bne     is_ok
        move.b  #$7E,ADDR
        bsr     probe
        bne     is_ok
        clr.b   ADDR
        bra     is_x
is_ok:  bsr     lcd_init
is_x:   movem.l (sp)+,d2-d7/a2-a6
        rts
probe:  bsr     i2c_start
        move.b  ADDR,d0
        bsr     wb
        move.w  d0,-(sp)
        bsr     i2c_stop
        move.w  (sp)+,d0
        tst.w   d0
        rts
i_at:   movem.l d2-d7/a2-a6,-(sp)
        move.l  48(sp),d0
        move.l  52(sp),d1
        movea.l 56(sp),a1
        bsr     lcd_goto
        bsr     lcd_puts
        movem.l (sp)+,d2-d7/a2-a6
        rts
i_hold: tst.w   STAR
        beq     ih_x
        moveq   #100,d0
        bsr     dms
        bsr     actv_off
ih_x:   rts
dms:    jsr     STROBE
        move.w  #899,d3
dm1:    dbra    d3,dm1
        dbra    d0,dms
        rts
sc:     move.w  d0,IOL20
        moveq   #3,d3
sc1:    dbra    d3,sc1
        rts
i2c_start: moveq #0,d0
        bsr     sc
        move.w  #$0080,d0
        bsr     sc
        move.w  #$0480,d0
        bra     sc
i2c_stop: move.w #$0480,d0
        bsr     sc
        move.w  #$0080,d0
        bsr     sc
        moveq   #0,d0
        bra     sc
wb:     move.b  d0,d4
        moveq   #7,d1
wb1:    move.w  #$0480,d5
        btst    d1,d4
        beq     wb2
        move.w  #$0400,d5
wb2:    move.w  d5,d0
        bsr     sc
        move.w  d5,d0
        andi.w  #$0080,d0
        bsr     sc
        move.w  d5,d0
        bsr     sc
        dbra    d1,wb1
        move.w  #$0400,d0
        bsr     sc
        moveq   #0,d0
        bsr     sc
        move.w  PORTB,d1
        move.w  #$0400,d0
        bsr     sc
        moveq   #0,d0
        andi.w  #$0040,d1
        beq     wb3
        moveq   #1,d0
wb3:    rts
lcd_nib: tst.b  ADDR
        beq     ln_x
        ori.b   #8,d0
        move.b  d0,d7
        bsr     i2c_start
        move.b  ADDR,d0
        bsr     wb
        move.b  d7,d0
        bsr     wb
        move.w  EM,d0
        or.b    d7,d0
        bsr     wb
        move.b  d7,d0
        bsr     wb
        bra     i2c_stop
ln_x:   rts
lcd_byte: move.b d0,d6
        andi.b  #$F0,d0
        or.b    d2,d0
        bsr     lcd_nib
        move.b  d6,d0
        lsl.b   #4,d0
        or.b    d2,d0
        bsr     lcd_nib
        moveq   #1,d0
        bra     dms
lcd_cmd: moveq  #0,d2
        bra     lcd_byte
lcd_chr: moveq  #1,d2
        bra     lcd_byte
lcd_puts: move.b (a1)+,d0
        beq     lps_x
        bsr     lcd_chr
        bra     lcd_puts
lps_x:  rts
lcd_init: moveq #100,d0
        bsr     dms
%s        rts
init1:  moveq   #20,d0
        bsr     dms
        moveq   #2,d6
i13:    moveq   #$38,d0
        bsr     lcd_nib
        moveq   #10,d0
        bsr     dms
        dbra    d6,i13
        moveq   #$28,d0
        bsr     lcd_nib
        moveq   #5,d0
        bsr     dms
        lea     itab(pc),a2
i1c:    move.b  (a2)+,d0
        beq     i1x
        bsr     lcd_cmd
        moveq   #3,d0
        bsr     dms
        bra     i1c
i1x:    rts
itab:   dc.b    $28,$08,$01,$06,$0C,0
%s
actv:   tst.w   STAR
        bne     st_x
        movem.l d0-d6/a1,-(sp)
        move.w  #1,STAR
        bra     st_w
actv_off: tst.w STAR
        beq     st_x
        movem.l d0-d6/a1,-(sp)
        move.w  #0,STAR
st_w:   moveq   #1,d0
        moveq   #19,d1
        bsr     lcd_goto
        moveq   #32,d0
        tst.w   STAR
        beq     st_b
        moveq   #42,d0
st_b:   bsr     lcd_chr
        movem.l (sp)+,d0-d6/a1
st_x:   rts
""" % (('        org $%X\n        bra.w   i_start\n        bra.w   i_at\n        bra.w   i_hold\n'%ENT) if ENT else '', ORG, '' if ENT else '        bra.w   i_start\n        bra.w   i_at\n        bra.w   i_hold\n', inits, goto)
m=m68kasm_v3.Asm(); m.assemble(src)
for a,b in m.segs: print('segmento $%X: %d bytes'%(a,len(b)))
a,b=m.segs[-1]; b=bytes(b); assert a==ORG, hex(a)
print('lcd i2c corpo %d bytes (area livre $F873E8-$F87EE0 = 2784), CTRL=%d, ORG=$%X'%(len(b),CTRL,ORG))
open(OUT,'wb').write(b)
if ENT: open(OUT.replace('.bin','_ent.bin'),'wb').write(bytes(m.segs[0][1]))
json.dump(m.sym,open(OUT.replace('.bin','_sym.json'),'w'))
