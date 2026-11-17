        org $F80800
        move.b  d0,$FA0006
        rts
        org $F8080C
pu1:    move.b  (a1)+,d0
        tst.b   d0
        beq     pu2
        move.b  d0,$FA0006
        bra     pu1
pu2:    rts
        org $F80824
        rts
        org $F8082A
        rts
