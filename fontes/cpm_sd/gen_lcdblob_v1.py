#!/usr/bin/env python3
"""gen_lcdblob_v1.py - modulo minimo de LCD 20x4 (HD44780, 4 bits) para o BIOS do CP/M, montado em $F80614
(vao livre do monitor, 426 bytes). Entradas (bra.w): +0 lcd_start(), +4 lcd_at(linha,col,texto), +8 lcd_hold(), (actv/actv_off: enderecos em lcd_sym.json).
Variaveis na RAM alta: LSH $5F02E, STAR $5F030, LCDOK $5F032."""
import sys, json
sys.path.insert(0,'/home/claude/rom24/v26')
import m68kasm_v3
ORG=0xF80614
src="""LATCH   equ $020018
LSH     equ $5F02E
STAR    equ $5F030
        org $F80614
        bra.w   i_start
        bra.w   i_at
        bra.w   i_hold
i_start: movem.l d2-d7/a2-a6,-(sp)
        move.w  #4,LSH
        move.w  #0,STAR
        bsr     lcd_init
        movem.l (sp)+,d2-d7/a2-a6
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
        move.l  #90000,d0
        bsr     dly
        bsr     actv_off
ih_x:   rts
dly:    subq.l  #1,d0
        bne     dly
        rts
lcd_nib: andi.w #15,d0
        lsl.w   #5,d0
        or.w    d2,d0
        move.w  LSH,d1
        andi.w  #$FE07,d1
        or.w    d0,d1
        move.w  d1,LSH
        move.w  d1,LATCH
        ori.w   #8,d1
        move.w  d1,LATCH
        moveq   #8,d3
ln_w:   dbra    d3,ln_w
        andi.w  #$FFF7,d1
        move.w  d1,LATCH
        move.w  d1,LSH
        rts
lcd_byte: move.w d0,d4
        lsr.w   #4,d0
        bsr     lcd_nib
        move.w  d4,d0
        bsr     lcd_nib
        move.l  #60,d0
        bra     dly
lcd_cmd: moveq  #0,d2
        bra     lcd_byte
lcd_chr: moveq  #16,d2
        bra     lcd_byte
lcd_puts: move.b (a1)+,d0
        beq     lps_x
        bsr     lcd_chr
        bra     lcd_puts
lps_x:  rts
lcd_init: move.l #20000,d0
        bsr     dly
        moveq   #0,d2
        moveq   #2,d6
li_3:   moveq   #3,d0
        bsr     lcd_nib
        move.l  #6000,d0
        bsr     dly
        dbra    d6,li_3
        moveq   #2,d0
        bsr     lcd_nib
        move.l  #300,d0
        bsr     dly
        move.b  #$28,d0
        bsr     lcd_cmd
        move.b  #$0C,d0
        bsr     lcd_cmd
        move.b  #$06,d0
        bsr     lcd_cmd
        move.b  #1,d0
        bsr     lcd_cmd
        move.l  #2500,d0
        bra     dly
lcd_goto: andi.w #3,d0
        lea     ltab(pc),a0
        adda.w  d0,a0
        move.b  (a0),d0
        add.b   d1,d0
        bra     lcd_cmd
ltab:   dc.b    $80,$C0,$94,$D4
actv:   tst.w   STAR
        bne     st_x
        movem.l d0-d6/a1,-(sp)
        move.w  #1,STAR
        moveq   #42,d5
        bra     st_w
actv_off: tst.w STAR
        beq     st_x
        movem.l d0-d6/a1,-(sp)
        move.w  #0,STAR
        moveq   #32,d5
st_w:   moveq   #1,d0
        moveq   #19,d1
        bsr     lcd_goto
        move.b  d5,d0
        bsr     lcd_chr
        movem.l (sp)+,d0-d6/a1
st_x:   rts
"""
m=m68kasm_v3.Asm(); m.assemble(src); a,b=m.segs[0]; b=bytes(b)
assert a==ORG, hex(a)
print('lcd blob %d bytes (limite 426)'%len(b)); assert len(b)<=426
open('/home/claude/cpmw/sdb/lcd_blob.bin','wb').write(b)
json.dump(m.sym,open('/home/claude/cpmw/sdb/lcd_sym.json','w'))
