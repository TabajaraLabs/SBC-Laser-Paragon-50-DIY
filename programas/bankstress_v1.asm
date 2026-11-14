; ==========================================================================
;  BANKSTRESS.ASM v1 - 20000 voltas por 8 bancos (160000 trocas) lendo em cada banco o valor esperado:
;  marcadores: banco 1 = $1234 em $F9FFFC, banco 2 = $2222 em $F9FFFA, banco 4 = $4444 em $F9FFF8;
;  bancos 0,3,5,6,7 = $FFFF em $F9FFFE.  Ordem 0,7,1,6,2,5,4,3 (cobre todas as combinacoes de bits).
;  So le. Roda na RAM. Termina no banco 0 e imprime o numero de erros.
; ==========================================================================
PUTS    equ $F8080C
HEXW    equ $F80818
CRLF    equ $F80824
ERRL    equ $3004
        org $2000
start:  move.w  #$2700,sr
        move.l  #0,d4
        move.l  #20000,d3
outer:  lea     tab(pc),a1
        moveq   #7,d2
inner:  movea.l (a1)+,a0
        move.w  (a1)+,d0
        move.w  (a1)+,d1
        move.w  d0,$FC0000
        move.w  (a0),d5
        cmp.w   d1,d5
        beq     ok
        addq.l  #1,d4
ok:     dbra    d2,inner
        subq.l  #1,d3
        bne     outer
        move.w  #0,$FC0000
        move.l  d4,ERRL
        lea     m_t(pc),a1
        jsr     PUTS
        move.w  ERRL,d0
        jsr     HEXW
        move.w  ERRL+2,d0
        jsr     HEXW
        jsr     CRLF
        rts
tab:    dc.l $F9FFFE
        dc.w 0,$FFFF
        dc.l $F9FFFE
        dc.w 7,$FFFF
        dc.l $F9FFFC
        dc.w 1,$1234
        dc.l $F9FFFE
        dc.w 6,$FFFF
        dc.l $F9FFFA
        dc.w 2,$2222
        dc.l $F9FFFE
        dc.w 5,$FFFF
        dc.l $F9FFF8
        dc.w 4,$4444
        dc.l $F9FFFE
        dc.w 3,$FFFF
m_t:    dc.b 13,10,"BANKSTRESS v1 - erros em 160000 trocas de banco (esperado 00000000): $",0
        even
