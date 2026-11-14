; ==========================================================================
;  FLASHW.ASM v1 - grava UMA palavra de teste na flash (PARAGON 50)
;  Carregar com L e executar com G 2000.
;  Grava $5AA5 em $F9FFFE (ultima palavra da ROM, ainda apagada = $FFFF) e le de volta.
;  So grava se a posicao estiver em $FFFF. NAO apaga nada. Depois, essa palavra
;  so volta a $FFFF quando o setor for apagado (o que sera feito mais adiante).
;  Roda na RAM: durante a gravacao a flash nao pode ser lida como ROM.
; ==========================================================================
PUTS    equ $F8080C
HEXW    equ $F80818
CRLF    equ $F80824
PRE     equ $3000
POST    equ $3002
STAT    equ $3004
CMD1    equ $F80AAA
CMD2    equ $F80554
ALVO    equ $F9FFFE
DADO    equ $5AA5

        org $2000
start:  move.w  #$2700,sr
        movea.l #ALVO,a0
        move.w  (a0),d0
        move.w  d0,PRE
        move.w  #0,STAT
        cmpi.w  #$FFFF,d0
        bne     fim
        move.w  #DADO,d5
        bsr     pw
        move.w  d4,STAT
        tst.w   d4
        beq     lei
        move.w  #$F0F0,$F80000          ; timeout: volta ao modo de leitura
        move.l  #50,d1
d0l:    subq.l  #1,d1
        bne     d0l
lei:    movea.l #ALVO,a0
        move.w  (a0),d0
        move.w  d0,POST
fim:    lea     m_t(pc),a1
        jsr     PUTS
        move.w  PRE,d0
        jsr     HEXW
        cmpi.w  #$FFFF,PRE
        beq     gravou
        lea     m_nao(pc),a1
        jsr     PUTS
        rts
gravou: lea     m_pos(pc),a1
        jsr     PUTS
        move.w  POST,d0
        jsr     HEXW
        jsr     CRLF
        tst.w   STAT
        beq     semto
        lea     m_to(pc),a1
        jsr     PUTS
        rts
semto:  cmpi.w  #DADO,POST
        bne     difer
        lea     m_ok(pc),a1
        jsr     PUTS
        rts
difer:  lea     m_dif(pc),a1
        jsr     PUTS
        rts

; pw: grava a palavra d5 no endereco a0 e espera o fim (DQ7 de cada chip).
;     devolve d4 = 0 ok, 1 timeout
pw:     move.w  #$AAAA,CMD1
        move.w  #$5555,CMD2
        move.w  #$A0A0,CMD1
        move.w  d5,(a0)
        move.l  #3000,d3
pl:     move.w  (a0),d1
        move.w  d1,d2
        eor.w   d5,d2
        andi.w  #$8080,d2
        beq     pok
        subq.l  #1,d3
        bne     pl
        moveq   #1,d4
        rts
pok:    moveq   #0,d4
        rts

m_t:    dc.b 13,10,"FLASHW v1 - grava $5AA5 em $F9FFFE",13,10,"Antes: $",0
m_nao:  dc.b "  (nao esta em $FFFF: NAO gravei nada)",13,10,0
m_pos:  dc.b "  Depois: $",0
m_ok:   dc.b "OK: a gravacao deu certo nas duas flash.",13,10,0
m_dif:  dc.b "ERRO: o valor lido e diferente do gravado.",13,10,0
m_to:   dc.b "ERRO: tempo esgotado esperando DQ7 (flash resetada).",13,10,0
        even
