#!/usr/bin/env python3
"""gen_sdfs_v5.py - sdfs_v4.asm (driver do cartao SD para o BASIC, $50000) com o LCD paralelo 20x4 trocado pelo LCD I2C 40x4 (PCF8574).
Troca so as rotinas de baixo nivel (lcd_nib/lcd_byte/lcd_cmd/lcd_chr/lcd_clr/lcd_init/lcd_goto); o resto (lcd_puts, lcd_blank, lcd_show, actv...) continua igual.
RAM: LSH ($58960) = mascara do E em uso; LCDADR ($58966) = endereco I2C de escrita ($4E/$7E; 0 = sem LCD)."""
import sys; sys.path.insert(0,'.')
import m68kasm_v3
s=open('sdfs_v4.asm').read()
a=s.index("lcd_nib: andi.w #15,d0"); b=s.index("; lcd_blank: apaga a linha")
new='''XSTROBE equ $F8082A
LCDADR  equ $58966
xsc:    move.w  d0,$020020
        moveq   #3,d3
xsc1:   dbra    d3,xsc1
        rts
xstart: moveq   #0,d0
        bsr     xsc
        move.w  #$0080,d0
        bsr     xsc
        move.w  #$0480,d0
        bra     xsc
xstop:  move.w  #$0480,d0
        bsr     xsc
        move.w  #$0080,d0
        bsr     xsc
        moveq   #0,d0
        bra     xsc
xwb:    move.b  d0,d4
        moveq   #7,d1
xwb1:   move.w  #$0480,d5
        btst    d1,d4
        beq     xwb2
        move.w  #$0400,d5
xwb2:   move.w  d5,d0
        bsr     xsc
        move.w  d5,d0
        andi.w  #$0080,d0
        bsr     xsc
        move.w  d5,d0
        bsr     xsc
        dbra    d1,xwb1
        move.w  #$0400,d0
        bsr     xsc
        moveq   #0,d0
        bsr     xsc
        move.w  $020028,d1
        move.w  #$0400,d0
        bsr     xsc
        moveq   #0,d0
        andi.w  #$0040,d1
        beq     xwb3
        moveq   #1,d0
xwb3:   rts
xdms:   jsr     XSTROBE
        move.w  #899,d3
xdm1:   dbra    d3,xdm1
        dbra    d0,xdms
        rts
xprobe: bsr     xstart
        move.b  LCDADR,d0
        bsr     xwb
        move.w  d0,-(sp)
        bsr     xstop
        move.w  (sp)+,d0
        tst.w   d0
        rts
lcd_nib: tst.b  LCDADR
        beq     xln_x
        ori.b   #8,d0
        move.b  d0,d7
        bsr     xstart
        move.b  LCDADR,d0
        bsr     xwb
        move.b  d7,d0
        bsr     xwb
        move.w  LSH,d0
        or.b    d7,d0
        bsr     xwb
        move.b  d7,d0
        bsr     xwb
        bra     xstop
xln_x:  rts
lcd_byte: movem.l d1-d7,-(sp)
        move.b  d0,d6
        andi.b  #$F0,d0
        or.b    d2,d0
        bsr     lcd_nib
        move.b  d6,d0
        lsl.b   #4,d0
        or.b    d2,d0
        bsr     lcd_nib
        moveq   #1,d0
        bsr     xdms
        movem.l (sp)+,d1-d7
        rts
lcd_cmd: moveq  #0,d2
        bra     lcd_byte
lcd_chr: moveq  #1,d2
        bra     lcd_byte
lcd_clr: movem.l d0-d2,-(sp)
        move.w  #4,LSH
        moveq   #1,d0
        bsr     lcd_cmd
        move.w  #2,LSH
        moveq   #1,d0
        bsr     lcd_cmd
        moveq   #2,d0
        bsr     xdms
        movem.l (sp)+,d0-d2
        rts
lcd_puts: move.b (a1)+,d0
        beq     lps_x
        bsr     lcd_chr
        bra     lcd_puts
lps_x:  rts
lcd_init: movem.l d0-d7/a1-a2,-(sp)
        move.b  #$4E,LCDADR
        bsr     xprobe
        bne     xli_ok
        move.b  #$7E,LCDADR
        bsr     xprobe
        bne     xli_ok
        clr.b   LCDADR
        bra     xli_x
xli_ok: moveq   #100,d0
        bsr     xdms
        move.w  #4,LSH
        bsr     xinit1
        move.w  #2,LSH
        bsr     xinit1
xli_x:  movem.l (sp)+,d0-d7/a1-a2
        rts
xinit1: moveq   #20,d0
        bsr     xdms
        moveq   #2,d6
xi13:   moveq   #$38,d0
        bsr     lcd_nib
        moveq   #10,d0
        bsr     xdms
        dbra    d6,xi13
        moveq   #$28,d0
        bsr     lcd_nib
        moveq   #5,d0
        bsr     xdms
        lea     xitab(pc),a2
xi1c:   move.b  (a2)+,d0
        beq     xi1x
        bsr     lcd_cmd
        moveq   #3,d0
        bsr     xdms
        bra     xi1c
xi1x:   rts
xitab:  dc.b    $28,$08,$01,$06,$0C,0
; lcd_goto: d0 = linha 0..3, d1 = coluna (40x4: linhas 0-1 = controlador 1 (E1), 2-3 = controlador 2 (E2))
lcd_goto:
        movem.l d0-d5,-(sp)
        move.w  #4,LSH
        cmpi.b  #2,d0
        blt     xlg1
        move.w  #2,LSH
xlg1:   andi.w  #1,d0
        lsl.w   #6,d0
        add.b   d1,d0
        ori.b   #$80,d0
        bsr     lcd_cmd
        movem.l (sp)+,d0-d5
        rts
'''
s=s[:a]+new+s[b:]
assert "moveq  #19,d6" not in s
s=s.replace("        moveq   #19,d6\nlb_l:","        moveq   #39,d6\nlb_l:")
s=s.replace("; ------------------------------------------------------------ LCD 20x4 (HD44780, 4 bits) - rotinas do perif_v2","; ------------------------------------------------------------ LCD 40x4 por I2C (PCF8574 em $27/$3F) - v5")
open('sdfs_v5.asm','w').write(s)
m=m68kasm_v3.Asm(); m.assemble(s); ad,img=m.segs[0]; print(hex(ad),len(img),hex(ad+len(img)))
open('sdfs_v5.bin','wb').write(bytes(img))
