; ==========================================================================
;  BANKMARK.ASM v1 (variante banco 4) - grava a palavra $1234 em $F9FFFC com o BANCO 1 selecionado e le essa
;  posicao em cada banco 0..7. Se os bancos funcionam, so o banco 1 mostra 1234
;  (12 = flash HI, 34 = flash LO). Roda na RAM. So grava se a posicao estiver em $FFFF.
; ==========================================================================
PUTC    equ $F80800
PUTS    equ $F8080C
HEXW    equ $F80818
CRLF    equ $F80824
CMD1    equ $F80AAA
CMD2    equ $F80554
ALVO    equ $F9FFF8
DADO    equ $4444
TAB     equ $3010
STAT    equ $3004
PRE     equ $3006
IDX     equ $3030
        org $2000
start:  move.w  #$2700,sr
        move.w  #4,$FC0000
        movea.l #ALVO,a0
        move.w  (a0),d0
        move.w  d0,PRE
        move.w  #9,STAT
        cmpi.w  #$FFFF,d0
        bne     rd
        move.w  #DADO,d5
        bsr     pw
        move.w  d4,STAT
        tst.w   d4
        beq     rd
        move.w  #$F0F0,$F80000
        move.l  #50,d1
dl:     subq.l  #1,d1
        bne     dl
rd:     movea.l #TAB,a1
        moveq   #0,d2
rb:     move.w  d2,$FC0000
        move.w  ALVO,d0
        move.w  d0,(a1)+
        addq.w  #1,d2
        cmpi.w  #8,d2
        bne     rb
        move.w  #0,$FC0000
        lea     m_t(pc),a1
        jsr     PUTS
        move.w  PRE,d0
        jsr     HEXW
        lea     m_s(pc),a1
        jsr     PUTS
        move.w  STAT,d0
        jsr     HEXW
        jsr     CRLF
        move.w  #0,IDX
pr:     lea     m_b(pc),a1
        jsr     PUTS
        move.w  IDX,d0
        addi.b  #48,d0
        jsr     PUTC
        lea     m_c(pc),a1
        jsr     PUTS
        move.w  IDX,d0
        add.w   d0,d0
        movea.l #TAB,a2
        adda.w  d0,a2
        move.w  (a2),d0
        jsr     HEXW
        jsr     CRLF
        move.w  IDX,d0
        addq.w  #1,d0
        move.w  d0,IDX
        cmpi.w  #8,d0
        bne     pr
        rts
pw:     move.w  #$AAAA,CMD1
        move.w  #$5555,CMD2
        move.w  #$A0A0,CMD1
        move.w  d5,(a0)
        move.l  #4000,d3
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
m_t:    dc.b 13,10,"BANKMARK v1 - $4444 em $F9FFF8 (gravado com o banco 4). Antes: $",0
m_s:    dc.b "  Estado da gravacao (0=ok, 9=nao gravou): $",0
m_b:    dc.b "  banco ",0
m_c:    dc.b ": $",0
        even
