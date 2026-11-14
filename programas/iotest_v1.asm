; ==========================================================================
;  IOTEST v1 - teste das portas de E/S do PARAGON 50 (J1, J2, J7)
;  Carregar com L (S-record) e executar com G 2000.   Nada e gravado na flash.
;
;  Menu:
;    1  SAIDAS $020018 (2 latches, J1/J2 conhecidos): anda UM bit por vez; tecla = proximo bit, Q = sai
;    2  SAIDAS $020020 (U40/U46; mapa de pinos ainda a descobrir): idem. Bits 0-7 passam por 74LS06
;       (coletor aberto, INVERTIDO: o pino fica em nivel BAIXO quando o bit vale 1)
;    I  ENTRADAS: mostra todas as portas e avisa (BEL) cada bit que muda. Ate uma tecla
;    R  le todas as entradas uma vez
;    Q  sai (restaura $020018 = $0004 e $020020 = $0000)
;
;  Entradas lidas ($020000, $020028, $020030 de 16 bits; $040180 $04018A $040194 $04019C de 8 bits).
;  Os 74LS240 INVERTEM: pino aterrado = bit 1 (pull-up de 4,7k).  So le; as saidas so mexem em $020018/$020020.
;  Enderecos sem DTACK ($060000-$07FFFF) NUNCA sao acessados (a CPU travaria).
; ==========================================================================
PUTC    equ $F80800
GETC    equ $F80806
PUTS    equ $F8080C
HEXB    equ $F80812
HEXW    equ $F80818
CRLF    equ $F80824
STROBE  equ $F8082A
UARTSR  equ $FA0003
UARTD   equ $FA0007
LAT18   equ $020018
LAT20   equ $020020
OLDV    equ $2F00          ; 7 palavras: ultimo valor de cada entrada
NPORT   equ 7

        org $2000
start:  lea     m_title(pc),a1
        jsr     PUTS
menu:   lea     m_menu(pc),a1
        jsr     PUTS
mk:     bsr     key_wait
        cmpi.b  #'1',d0
        beq     c_w18
        cmpi.b  #'2',d0
        beq     c_w20
        andi.b  #$DF,d0
        cmpi.b  #'I',d0
        beq     c_mon
        cmpi.b  #'R',d0
        beq     c_read
        cmpi.b  #'Q',d0
        beq     quit
        bra     mk
quit:   move.w  #4,LAT18
        move.w  #0,LAT20
        lea     m_fim(pc),a1
        jsr     PUTS
        rts

key_wait:
        jsr     STROBE
        btst    #0,UARTSR
        beq     key_wait
        move.b  UARTD,d0
        andi.l  #$FF,d0
        rts
key_poll:
        btst    #0,UARTSR
        beq     kp_no
        move.b  UARTD,d0
        andi.l  #$FF,d0
        rts
kp_no:  moveq   #0,d0
        rts

; ---- 1 / 2 : andar um bit por vez --------------------------------------
c_w18:  movea.l #LAT18,a3
        lea     lab18(pc),a4
        move.w  #4,d5               ; valor seguro ao sair
        lea     m_w18(pc),a1
        bra     walk
c_w20:  movea.l #LAT20,a3
        lea     lab20(pc),a4
        move.w  #0,d5
        lea     m_w20(pc),a1
walk:   jsr     PUTS
        moveq   #0,d3
wl:     moveq   #1,d0
        lsl.w   d3,d0
        move.w  d0,(a3)
        lea     m_bit(pc),a1
        jsr     PUTS
        move.w  d3,d0
        jsr     HEXB
        lea     m_arr(pc),a1
        jsr     PUTS
        move.w  d3,d1
        lsl.w   #3,d1
        movea.l a4,a1
        adda.w  d1,a1
        jsr     PUTS
        jsr     CRLF
        bsr     key_wait
        andi.b  #$DF,d0
        cmpi.b  #'Q',d0
        beq     wl_x
        addq.w  #1,d3
        cmpi.w  #16,d3
        blt     wl
wl_x:   move.w  d5,(a3)
        bra     menu

; ---- R : le tudo uma vez ---------------------------------------------------
c_read: bsr     snap
        bsr     show_all
        bra     menu

; leitura da entrada d4: a0 = entrada da tabela, d0 = valor
rd_port:
        lea     tbl(pc),a0
        move.w  d4,d1
        lsl.w   #4,d1
        adda.w  d1,a0               ; entradas de 16 bytes
        movea.l (a0),a2
        cmpi.w  #2,4(a0)
        bne     rp_b
        moveq   #0,d0
        move.w  (a2),d0
        rts
rp_b:   moveq   #0,d0
        move.b  (a2),d0
        rts

snap:   moveq   #0,d4
sn_l:   bsr     rd_port
        lea     OLDV,a5
        move.w  d4,d1
        add.w   d1,d1
        adda.w  d1,a5
        move.w  d0,(a5)
        addq.w  #1,d4
        cmpi.w  #NPORT,d4
        blt     sn_l
        rts

show_all:
        moveq   #0,d4
sa_l:   lea     tbl(pc),a0
        move.w  d4,d1
        lsl.w   #4,d1
        adda.w  d1,a0
        movea.l 8(a0),a1            ; nome
        jsr     PUTS
        lea     OLDV,a5
        move.w  d4,d1
        add.w   d1,d1
        adda.w  d1,a5
        move.w  (a5),d0
        jsr     HEXW
        jsr     CRLF
        addq.w  #1,d4
        cmpi.w  #NPORT,d4
        blt     sa_l
        rts

; ---- I : monitora mudancas ---------------------------------------------------
c_mon:  lea     m_mon(pc),a1
        jsr     PUTS
        bsr     snap
        bsr     show_all
ml:     jsr     STROBE
        bsr     key_poll
        tst.l   d0
        bne     mon_x
        moveq   #0,d4
mi:     bsr     rd_port             ; d0 = novo valor, a0 = entrada
        lea     OLDV,a5
        move.w  d4,d1
        add.w   d1,d1
        adda.w  d1,a5
        move.w  (a5),d6             ; antigo
        cmp.w   d6,d0
        beq     nochg
        move.w  d0,d7               ; novo
        move.b  #7,d0               ; BEL
        jsr     PUTC
        movea.l 8(a0),a1
        jsr     PUTS
        move.w  d6,d0
        jsr     HEXW
        lea     m_to(pc),a1
        jsr     PUTS
        move.w  d7,d0
        jsr     HEXW
        move.w  d7,(a5)             ; guarda o novo
        movea.l 12(a0),a3           ; tabela de rotulos (ou 0)
        bsr     bitlist             ; d6 = antigo, d7 = novo, a3 = rotulos
        jsr     CRLF
nochg:  addq.w  #1,d4
        cmpi.w  #NPORT,d4
        blt     mi
        bra     ml
mon_x:  lea     m_fim2(pc),a1
        jsr     PUTS
        bra     menu

; bitlist: lista os bits que diferem. d6 = valor antigo, d7 = valor novo, a3 = tabela de rotulos (ou 0)
bitlist:
        movem.l d0-d3/a1,-(sp)
        move.w  d7,d2
        eor.w   d6,d2               ; bits que mudaram
        moveq   #0,d3
bl_l:   btst    d3,d2
        beq     bl_n
        lea     m_b(pc),a1
        jsr     PUTS
        move.w  d3,d0
        jsr     HEXB
        move.b  #'=',d0
        jsr     PUTC
        btst    d3,d7
        beq     bl_0
        move.b  #'1',d0
        bra     bl_p
bl_0:   move.b  #'0',d0
bl_p:   jsr     PUTC
        move.l  a3,d0
        beq     bl_n
        movea.l a3,a1
        move.w  d3,d0
        lsl.w   #3,d0
        adda.w  d0,a1
        move.b  #' ',d0
        jsr     PUTC
        jsr     PUTS
bl_n:   addq.w  #1,d3
        cmpi.w  #16,d3
        blt     bl_l
        movem.l (sp)+,d0-d3/a1
        rts

; ---- tabela das entradas (16 bytes cada): endereco.l, tamanho.w, pad.w, nome.l, rotulos.l ------
tbl:    dc.l $020000
        dc.w 2,0
        dc.l n_e0
        dc.l 0
        dc.l $020028
        dc.w 2,0
        dc.l n_pb
        dc.l labB
        dc.l $020030
        dc.w 2,0
        dc.l n_pa
        dc.l labA
        dc.l $040180
        dc.w 1,0
        dc.l n_80
        dc.l 0
        dc.l $04018A
        dc.w 1,0
        dc.l n_8a
        dc.l 0
        dc.l $040194
        dc.w 1,0
        dc.l n_94
        dc.l 0
        dc.l $04019C
        dc.w 1,0
        dc.l n_9c
        dc.l 0

n_e0:   dc.b "E0 $020000 ",0
n_pb:   dc.b "B  $020028 ",0
n_pa:   dc.b "A  $020030 ",0
n_80:   dc.b "   $040180 ",0
n_8a:   dc.b "   $04018A ",0
n_94:   dc.b "   $040194 ",0
n_9c:   dc.b "   $04019C ",0

; rotulos: 16 entradas de 8 bytes
lab18:  dc.b "J1-28",0,0,0
        dc.b "J1-26",0,0,0
        dc.b "J1-24",0,0,0
        dc.b "J1-20",0,0,0
        dc.b "J1-18",0,0,0
        dc.b "J1-15",0,0,0
        dc.b "J1-14",0,0,0
        dc.b "J1-10",0,0,0
        dc.b "J2-47",0,0,0
        dc.b "J2-40",0,0,0
        dc.b "J2-37",0,0,0
        dc.b "J2-30",0,0,0
        dc.b "J2-28",0,0,0
        dc.b "J2-27",0,0,0
        dc.b "J2-24",0,0,0
        dc.b "J2-23",0,0,0
lab20:  dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
labB:   dc.b "J1-7",0,0,0,0
        dc.b "J1-35",0,0,0
        dc.b "J1-33",0,0,0
        dc.b "J1-31",0,0,0
        dc.b "J1-27",0,0,0
        dc.b "J1-25",0,0,0
        dc.b "J1-23",0,0,0
        dc.b "J1-?",0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
labA:   dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "J1-4",0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0
        dc.b "?",0,0,0,0,0,0,0

m_title: dc.b 13,10,"IOTEST v1 - portas de E/S do PARAGON 50 (J1, J2, J7)",13,10,0
m_menu: dc.b "1 saidas $020018 (bit a bit)   2 saidas $020020 (bit a bit)   I monitora entradas   R le entradas   Q sai",13,10,"> ",0
m_w18:  dc.b 13,10,"Saidas $020018: um bit por vez. Qualquer tecla = proximo bit, Q = voltar.",13,10,0
m_w20:  dc.b 13,10,"Saidas $020020 (bits 0-7 INVERTIDOS pelo 74LS06): qualquer tecla = proximo bit, Q = voltar.",13,10,0
m_bit:  dc.b "bit ",0
m_arr:  dc.b " -> ",0
m_mon:  dc.b 13,10,"Entradas: aterre um pino de J1/J2/J7 (resistor de 330 ohms); o bit sobe para 1. Tecla = sair.",13,10,0
m_to:   dc.b " -> ",0
m_b:    dc.b "  b",0
m_fim:  dc.b 13,10,"Saidas restauradas ($020018=0004, $020020=0000). Fim.",13,10,0
m_fim2: dc.b 13,10,"Fim do monitor.",13,10,0
