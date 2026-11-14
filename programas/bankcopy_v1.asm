; BANKCOPY v1 - copia 256 bytes de $F88000 de cada banco (0..7) para a RAM em $4000 + n*256; termina no banco 0
        org $2000
start:  move.w  #$2700,sr
        moveq   #0,d2
bk:     move.w  d2,$FC0000
        movea.l #$F88000,a0
        movea.l #$4000,a1
        move.w  d2,d0
        lsl.w   #8,d0
        adda.w  d0,a1
        move.w  #127,d1
cp:     move.w  (a0)+,(a1)+
        dbra    d1,cp
        addq.w  #1,d2
        cmpi.w  #8,d2
        bne     bk
        move.w  #0,$FC0000
        rts
