; BANKHOLD v1 - seleciona o banco dado em $3000 (word), segura ~8 s e volta ao banco 0.
;   P 3000 00 07  -> banco 7 (A16, A17 e A18 altos).  Roda na RAM.
        org $2000
start:  move.w  #$2700,sr
        move.w  $3000,d0
        move.w  d0,$FC0000
        move.l  #3500000,d3
lp:     subq.l  #1,d3
        bne     lp
        move.w  #0,$FC0000
        rts
