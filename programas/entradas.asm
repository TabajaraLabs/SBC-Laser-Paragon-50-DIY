; ==========================================================================
;  ENTRADAS.ASM - monitor das entradas de J1/J2 (PARAGON 50)
;  Programa para carregar com L (S-record) e executar com G 2000.
;  Le sem parar $020030 (porta A) e $020028 (porta B) e imprime cada bit que
;  muda. Aterre um pino de J1/J2 por um resistor de 330 ohms: o bit sobe
;  (os 74LS240 invertem). Qualquer tecla termina. So le; nada e gravado.
; ==========================================================================
PORTA   equ $020030
PORTB   equ $020028
PUTC    equ $F80800
PUTS    equ $F8080C
HEXW    equ $F80818
CRLF    equ $F80824
STROBE  equ $F8082A
OLDA    equ $2F00
OLDB    equ $2F02
NEWA    equ $2F04
NEWB    equ $2F06
BMASK   equ $2F08
BNEW    equ $2F0A
BLET    equ $2F0C
BIDX    equ $2F0E

        org $2000
start:  lea     m_title(pc),a1
        jsr     PUTS
        move.w  PORTA,d0
        move.w  d0,OLDA
        move.w  PORTB,d0
        move.w  d0,OLDB
        lea     m_ini(pc),a1
        jsr     PUTS
        move.w  OLDA,d0
        jsr     HEXW
        lea     m_b(pc),a1
        jsr     PUTS
        move.w  OLDB,d0
        jsr     HEXW
        jsr     CRLF
loop:   jsr     STROBE
        btst    #0,$FA0003
        beq     nokey
        move.b  $FA0007,d0
        lea     m_fim(pc),a1
        jsr     PUTS
        rts
nokey:  move.w  PORTA,d0
        move.w  d0,NEWA
        move.w  PORTB,d0
        move.w  d0,NEWB
        move.w  NEWA,d0
        cmp.w   OLDA,d0
        bne     chg
        move.w  NEWB,d0
        cmp.w   OLDB,d0
        bne     chg
        bra     loop
chg:    lea     m_a(pc),a1
        jsr     PUTS
        move.w  NEWA,d0
        jsr     HEXW
        lea     m_b(pc),a1
        jsr     PUTS
        move.w  NEWB,d0
        jsr     HEXW
        lea     m_mud(pc),a1
        jsr     PUTS
        move.w  NEWA,d0                 ; bits que mudaram na porta A
        move.w  OLDA,d1
        eor.w   d1,d0
        move.w  d0,BMASK
        move.w  NEWA,d0
        move.w  d0,BNEW
        move.b  #65,d0                  ; 'A'
        move.b  d0,BLET
        bsr     bits
        move.w  NEWB,d0                 ; bits que mudaram na porta B
        move.w  OLDB,d1
        eor.w   d1,d0
        move.w  d0,BMASK
        move.w  NEWB,d0
        move.w  d0,BNEW
        move.b  #66,d0                  ; 'B'
        move.b  d0,BLET
        bsr     bits
        jsr     CRLF
        move.w  NEWA,d0
        move.w  d0,OLDA
        move.w  NEWB,d0
        move.w  d0,OLDB
        move.l  #4000,d6                ; pequena pausa contra ruido
dly:    subq.l  #1,d6
        bne     dly
        bra     loop

; imprime "  X bit n -> v" para cada bit ligado em BMASK (valores em BNEW, letra em BLET)
bits:   move.w  #0,BIDX
bt_l:   move.w  BIDX,d2
        move.w  BMASK,d0
        btst    d2,d0
        beq     bt_n
        lea     m_sp(pc),a1
        jsr     PUTS
        move.b  BLET,d0
        jsr     PUTC
        lea     m_bit(pc),a1
        jsr     PUTS
        move.w  BIDX,d0
        cmpi.w  #10,d0
        blt     bt_1
        move.b  #49,d0                  ; '1'
        jsr     PUTC
        move.w  BIDX,d0
        subi.w  #10,d0
bt_1:   addi.b  #48,d0
        jsr     PUTC
        lea     m_arr(pc),a1
        jsr     PUTS
        move.w  BIDX,d2
        move.w  BNEW,d0
        btst    d2,d0
        beq     bt_z
        move.b  #49,d0
        bra     bt_p
bt_z:   move.b  #48,d0
bt_p:   jsr     PUTC
bt_n:   move.w  BIDX,d0
        addq.w  #1,d0
        move.w  d0,BIDX
        cmpi.w  #16,d0
        blt     bt_l
        rts

m_title: dc.b 13,10,"ENTRADAS - porta A = $020030, porta B = $020028. Qualquer tecla sai.",13,10
         dc.b "Aterre um pino de J1/J2 por 330 ohms: o bit correspondente sobe (240 inversor).",13,10,0
m_ini:   dc.b "Inicial:  A=$",0
m_b:     dc.b "  B=$",0
m_a:     dc.b "A=$",0
m_mud:   dc.b "  mudou:",0
m_sp:    dc.b "  ",0
m_bit:   dc.b " bit ",0
m_arr:   dc.b " -> ",0
m_fim:   dc.b 13,10,"Fim.",13,10,0
