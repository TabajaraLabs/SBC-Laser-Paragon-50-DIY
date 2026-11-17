; ==========================================================================
;  LCD40_TESTE_V3.ASM - teste do LCD 40x4 (WH4004A) pelo backpack I2C PCF8574
;  Carregar com L (S-record) e executar com G 2000.  Roda so na RAM; nao grava flash.
;
;  Ligacao (backpack em $27 -> escrita $4E):  SCL = J1-30 ($020020 b10), SDA saida = J1-48 ($020020 b7),
;  SDA leitura = J1-23 (porta B b6 = $020028 bit $40).  Linhas INVERTIDAS: bit = 1 puxa a linha para baixo.
;  Bits do PCF8574:  P0=RS  P1=E2  P2=E1  P3=luz  P4-P7 = D4-D7.   R/W do LCD no GND.
;  Linhas 1 e 2 = controlador 1 (E1); linhas 3 e 4 = controlador 2 (E2).
; ==========================================================================
IOL20   equ $020020
PORTB   equ $020028
PUTC    equ $F80800
PUTS    equ $F8080C
CRLF    equ $F80824
STROBE  equ $F8082A
EMASK   equ $2F00           ; palavra: mascara do Enable em uso
LBYTE   equ $2F02           ; byte em transmissao
ADDRW   equ $4E             ; endereco $27, escrita
BL      equ $08             ; luz de fundo ligada

        org $2000
start:  lea     m_title(pc),a1
        jsr     PUTS
        ; ---- 1) o backpack responde?
        bsr     i2c_start
        moveq   #ADDRW,d0
        bsr     i2c_wbyte
        move.w  d0,d7
        bsr     i2c_stop
        tst.w   d7
        bne     ack_ok
        lea     m_noack(pc),a1
        jsr     PUTS
        rts
ack_ok: lea     m_ack(pc),a1
        jsr     PUTS
        ; ---- 2) inicializa os dois controladores
        bsr     lcd_init
        lea     m_init(pc),a1
        jsr     PUTS
        ; ---- 3) escreve as 4 linhas
        moveq   #0,d0
        bsr     lcd_line
        lea     t1(pc),a1
        bsr     lcd_puts
        moveq   #1,d0
        bsr     lcd_line
        lea     t2(pc),a1
        bsr     lcd_puts
        lea     m_e1(pc),a1
        jsr     PUTS
        moveq   #2,d0
        bsr     lcd_line
        lea     t3(pc),a1
        bsr     lcd_puts
        moveq   #3,d0
        bsr     lcd_line
        lea     t4(pc),a1
        bsr     lcd_puts
        lea     m_e2(pc),a1
        jsr     PUTS
        ; ---- 4) espera uma tecla e apaga a tela
wk:     jsr     STROBE
        btst    #0,$FA0003
        beq     wk
        move.b  $FA0007,d0
        move.w  #6,EMASK
        moveq   #1,d0
        bsr     lcd_cmd
        move.w  #3,d0
        bsr     delay_ms
        lea     m_fim(pc),a1
        jsr     PUTS
        rts

; ------------------------------------------------------------------ atraso (ms aproximados; lento e seguro)
delay_ms:                       ; d0.w = ms (faz d0+1 voltas)
        jsr     STROBE
        move.w  #899,d3
dm1:    dbra    d3,dm1
        dbra    d0,delay_ms
        rts

; ------------------------------------------------------------------ I2C bit-bang (igual ao do RTC)
sdascl: move.w  d0,IOL20        ; d0 = valor do latch
        moveq   #3,d3
sd1:    dbra    d3,sd1
        rts
i2c_start:
        moveq   #0,d0
        bsr     sdascl
        move.w  #$0080,d0
        bsr     sdascl
        move.w  #$0480,d0
        bsr     sdascl
        rts
i2c_stop:
        move.w  #$0480,d0
        bsr     sdascl
        move.w  #$0080,d0
        bsr     sdascl
        moveq   #0,d0
        bsr     sdascl
        move.w  #0,IOL20
        rts
i2c_wbyte:                      ; d0.b = byte; devolve d0.w = 1 se houve ACK
        move.b  d0,d2
        moveq   #7,d1
wb1:    move.w  #$0480,d5       ; SDA baixo, SCL baixo
        btst    d1,d2
        beq     wb2
        move.w  #$0400,d5       ; SDA solto, SCL baixo
wb2:    move.w  d5,d0
        bsr     sdascl
        move.w  d5,d0
        andi.w  #$0080,d0       ; SCL solto (alto)
        bsr     sdascl
        move.w  d5,d0
        bsr     sdascl
        dbra    d1,wb1
        move.w  #$0400,d0       ; SDA solto, SCL baixo
        bsr     sdascl
        moveq   #0,d0           ; SCL alto
        bsr     sdascl
        move.w  PORTB,d4
        andi.w  #$0040,d4       ; bit = 1 -> linha em nivel baixo -> ACK
        move.w  #$0400,d0
        bsr     sdascl
        moveq   #0,d0
        tst.w   d4
        beq     wb3
        moveq   #1,d0
wb3:    rts

; ------------------------------------------------------------------ LCD
lcd_nib:                        ; d0.b = nibble em 7-4 + luz/RS em 3-0 (sem E); manda com E=1 e depois E=0
        move.b  d0,d7
        bsr     i2c_start
        moveq   #ADDRW,d0
        bsr     i2c_wbyte
        move.b  d7,d0               ; v2: primeiro RS/dados com E=0 (tempo de preparacao antes do E)
        bsr     i2c_wbyte
        move.w  EMASK,d0
        or.b    d7,d0
        bsr     i2c_wbyte           ; E=1
        move.b  d7,d0
        bsr     i2c_wbyte           ; E=0 (o LCD captura na descida)
        bsr     i2c_stop
        rts
lcd_byte:                       ; d0.b = valor, d6 = RS (0 comando, 1 dado)
        move.b  d0,LBYTE
        andi.b  #$F0,d0
        ori.b   #BL,d0
        or.b    d6,d0
        bsr     lcd_nib
        move.b  LBYTE,d0
        lsl.b   #4,d0
        ori.b   #BL,d0
        or.b    d6,d0
        bsr     lcd_nib
        moveq   #1,d0
        bsr     delay_ms
        rts
lcd_cmd:
        moveq   #0,d6
        bra     lcd_byte
lcd_dat:
        moveq   #1,d6
        bra     lcd_byte
lcd_init:                       ; v3: cada controlador e inicializado separadamente, com esperas longas
        moveq   #100,d0
        bsr     delay_ms
        move.w  #4,EMASK            ; controlador 1 (E1)
        bsr     init1
        move.w  #2,EMASK            ; controlador 2 (E2)
        bsr     init1
        rts
init1:  moveq   #20,d0
        bsr     delay_ms
        moveq   #$38,d0             ; reset por instrucao: tres vezes $3 (modo 8 bits)
        bsr     lcd_nib
        moveq   #10,d0
        bsr     delay_ms
        moveq   #$38,d0
        bsr     lcd_nib
        moveq   #5,d0
        bsr     delay_ms
        moveq   #$38,d0
        bsr     lcd_nib
        moveq   #5,d0
        bsr     delay_ms
        moveq   #$28,d0             ; passa para 4 bits
        bsr     lcd_nib
        moveq   #5,d0
        bsr     delay_ms
        moveq   #$28,d0             ; 4 bits, 2 linhas, 5x8
        bsr     lcd_cmd
        moveq   #$08,d0             ; display off
        bsr     lcd_cmd
        moveq   #$01,d0             ; limpa
        bsr     lcd_cmd
        moveq   #5,d0
        bsr     delay_ms
        moveq   #$06,d0             ; incrementa, sem deslocar
        bsr     lcd_cmd
        moveq   #$0C,d0             ; display on, sem cursor
        bsr     lcd_cmd
        rts
lcd_line:                       ; d0 = linha 0..3
        move.w  #4,EMASK        ; linhas 0 e 1 -> E1
        btst    #1,d0
        beq     ll1
        move.w  #2,EMASK        ; linhas 2 e 3 -> E2
ll1:    move.b  #$80,d1
        btst    #0,d0
        beq     ll2
        move.b  #$C0,d1
ll2:    move.b  d1,d0
        bra     lcd_cmd
lcd_puts:                       ; a1 = texto terminado em 0
lp1:    move.b  (a1)+,d0
        tst.b   d0
        beq     lp2
        bsr     lcd_dat
        bra     lp1
lp2:    rts

t1:     dc.b "PARAGON 50 - teste LCD 40x4 via I2C",0
t2:     dc.b "1234567890123456789012345678901234567890",0
t3:     dc.b "Controlador 2 (E2): linhas 3 e 4 OK",0
t4:     dc.b "Tabajara Labs 2026 - PCF8574 em $27",0
m_title: dc.b 13,10,"LCD40_TESTE v3 - WH4004A + PCF8574 ($27) - so RAM, nada e gravado.",13,10,0
m_ack:   dc.b "PCF8574 em $27: ACK ok.",13,10,0
m_noack: dc.b "SEM ACK em $27 (confira SCL J1-30, SDA J1-48 e J1-23, +5 V e GND). Fim.",13,10,0
m_init:  dc.b "Controladores inicializados (E1 + E2).",13,10,0
m_e1:    dc.b "Linhas 1 e 2 escritas (E1 = pino 9 do LCD, P2).",13,10,0
m_e2:    dc.b "Linhas 3 e 4 escritas (E2 = pino 15 do LCD, P1).",13,10,"Tecla para apagar a tela e sair.",13,10,0
m_fim:   dc.b "Tela apagada. Fim.",13,10,0
