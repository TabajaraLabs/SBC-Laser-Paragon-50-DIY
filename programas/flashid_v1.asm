; ==========================================================================
;  FLASHID.ASM v1 - le o ID das duas Am29F040B (PARAGON 50)
;  Carregar com L (S-record) e executar com G 2000.
;  Fecha-se JP-H e JP-L ANTES de executar (senao o /WE nao chega nas flash).
;  Envia a sequencia de desbloqueio + comando 90 (autoselect), le o ID,
;  manda F0 (volta ao modo de leitura) e so entao usa a ROM para imprimir.
;  NAO apaga nem grava nada: o comando 90 so troca o modo de leitura.
;  Esperado: fabricante $0101 (01 em cada chip), dispositivo $A4A4.
;  Se vier $0000 e $1F00 (primeiras palavras da ROM), o /WE nao chegou (jumper aberto).
; ==========================================================================
PUTS    equ $F8080C
HEXW    equ $F80818
CRLF    equ $F80824
RES0    equ $3000
RES1    equ $3002
RES2    equ $3004

; Enderecos da CPU que viram os enderecos de comando 555 e 2AA da flash:
; A0..A10 da flash = A1..A11 da CPU. 555h -> $AAA, 2AAh -> $554 (A12 em diante: "don't care").
CMD1    equ $F80AAA
CMD2    equ $F80554

        org $2000
start:  move.w  #$2700,sr               ; sem interrupcoes enquanto a ROM esta fora do ar
        move.w  #$AAAA,CMD1
        move.w  #$5555,CMD2
        move.w  #$9090,CMD1             ; autoselect
        move.w  $F80000,d0              ; X00: fabricante (01) em HI e LO
        move.w  d0,RES0
        move.w  $F80002,d0              ; X01: dispositivo (A4) em HI e LO
        move.w  d0,RES1
        move.w  #$F0F0,$F80000          ; reset: volta ao modo de leitura
        move.l  #50,d1                  ; pequena pausa (tRH)
dly:    subq.l  #1,d1
        bne     dly
        move.w  $F80000,d0              ; primeira palavra da ROM (prova que voltou a ler)
        move.w  d0,RES2

        lea     m_t(pc),a1
        jsr     PUTS
        lea     m_f(pc),a1
        jsr     PUTS
        move.w  RES0,d0
        jsr     HEXW
        lea     m_d(pc),a1
        jsr     PUTS
        move.w  RES1,d0
        jsr     HEXW
        lea     m_r(pc),a1
        jsr     PUTS
        move.w  RES2,d0
        jsr     HEXW
        jsr     CRLF
        cmpi.w  #$0101,RES0
        bne     bad
        cmpi.w  #$A4A4,RES1
        bne     bad
        lea     m_ok(pc),a1
        jsr     PUTS
        rts
bad:    lea     m_bad(pc),a1
        jsr     PUTS
        move.w  RES0,d0
        andi.w  #$FF00,d0
        cmpi.w  #$0100,d0
        beq     bad_l
        lea     m_h(pc),a1              ; byte alto nao veio 01
        jsr     PUTS
bad_l:  move.w  RES0,d0
        andi.w  #$00FF,d0
        cmpi.w  #$0001,d0
        beq     bad_e
        lea     m_l(pc),a1              ; byte baixo nao veio 01
        jsr     PUTS
bad_e:  jsr     CRLF
        rts

m_t:    dc.b 13,10,"FLASHID v1 - ID das flash Am29F040B (HI = D8-D15, LO = D0-D7)",13,10,0
m_f:    dc.b "Fabricante: $",0
m_d:    dc.b "  Dispositivo: $",0
m_r:    dc.b "  1a palavra da ROM apos reset: $",0
m_ok:   dc.b "OK: as duas flash responderam 01/A4 (Am29F040B). Escrita de comandos funciona.",13,10,0
m_bad:  dc.b "ERRO: ID inesperado. Esperado $0101 e $A4A4.",13,10,"Dicas: jumper JP-H/JP-L aberto? ",0
m_h:    dc.b "[HI nao respondeu] ",0
m_l:    dc.b "[LO nao respondeu] ",0
        even
