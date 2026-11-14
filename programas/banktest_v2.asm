; ==========================================================================
;  BANKTEST.ASM v2 - testa o registrador de banco 74LS175 em $FC0000 (PARAGON 50)
;  Carregar com L e executar com G 2000.  So le a flash; nao grava nada.
;  1) seleciona cada banco 0..7 e le $F80000 (banco 0 = 00F8; bancos 1-7 ainda tem copias da v2.3 = 0000)
;  2) 20000 trocas banco 0 <-> banco 1 lendo cada vez (testa o tempo de retencao do dado)
;  3) volta ao banco 0 e imprime.  O codigo roda na RAM; a ROM so e usada depois de voltar ao banco 0.
; ==========================================================================
PUTC    equ $F80800
PUTS    equ $F8080C
HEXW    equ $F80818
CRLF    equ $F80824
TAB     equ $3010
ERRL    equ $3004
IDX     equ $3030
        org $2000
start:  move.w  #$2700,sr
        movea.l #TAB,a1
        moveq   #0,d2
b1:     move.w  d2,$FC0000
        move.w  $F88006,d0
        move.w  d0,(a1)+
        addq.w  #1,d2
        cmpi.w  #8,d2
        bne     b1
        move.w  #0,$FC0000
        move.l  #0,d4
        move.l  #20000,d3
st:     move.w  #1,$FC0000
        move.w  $F88006,d0
        cmpi.w  #$0000,d0
        beq     s1
        addq.l  #1,d4
s1:     move.w  #0,$FC0000
        move.w  $F88006,d0
        cmpi.w  #$00F8,d0
        beq     s2
        addq.l  #1,d4
s2:     subq.l  #1,d3
        bne     st
        move.w  #0,$FC0000
        move.l  d4,ERRL
        lea     m_t(pc),a1
        jsr     PUTS
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
        lea     m_e(pc),a1
        jsr     PUTS
        move.w  ERRL,d0
        jsr     HEXW
        move.w  ERRL+2,d0
        jsr     HEXW
        jsr     CRLF
        rts
m_t:    dc.b 13,10,"BANKTEST v2 - palavra em $F88006 de cada banco (banco 0 = 00F8 na v2.3.1; copias antigas = 0000):",13,10,0
m_b:    dc.b "  banco ",0
m_c:    dc.b ": $",0
m_e:    dc.b "Erros em 20000 trocas 0<->1 (esperado 00000000): $",0
        even
