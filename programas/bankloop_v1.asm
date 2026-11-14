; BANKLOOP v1 - escreve 1 e 0 em $FC0000 por ~12 s (para medir com o osciloscopio); termina no banco 0
        org $2000
start:  move.w  #$2700,sr
        move.l  #2000000,d3
lp:     move.w  #1,$FC0000
        move.w  #0,$FC0000
        subq.l  #1,d3
        bne     lp
        rts
