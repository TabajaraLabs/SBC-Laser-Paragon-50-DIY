; ==========================================================================
;  PERIF.ASM - perifericos do PARAGON 50: SD (SPI) + buzzer + LCD 20x4 (HD44780)
;  Placa RepRapDiscount Smart Controller ligada a J1/J2.  Carregar com L, executar com G 2000.
;  Latch de saida $020018 (so escrita) => copia-sombra LSH em RAM; todos os drivers alteram LSH.
;    bit0 SCK (J1-28)   bit1 MOSI (J1-26)   bit2 CS (J1-24)   bit3 LCD_E (J1-20)  bit4 LCD_RS (J1-18)
;    bit5 LCD_D4 (J1-15) bit6 D5 (J1-14) bit7 D6 (J1-10) bit8 D7 (J2-47)  bit9 BUZZER (J2-40)
;  Entrada MISO: porta B $020028 bit 0 (J1-7), invertida pelo 74LS240.
;  Comandos:  I inicializa SD   R le setor   B escala de notas   A tom de 440 Hz (3 s)
;             K calibra o buzzer   L teste do LCD   Q sai
; ==========================================================================
LATCH   equ $020018
MPORT   equ $020028
MMASK   equ $0001
PUTC    equ $F80800
PUTS    equ $F8080C
HEXB    equ $F80812
HEXW    equ $F80818
HEXL    equ $F8081E
CRLF    equ $F80824
STROBE  equ $F8082A
GETHEX  equ $F80830
GETLINE equ $F80836
GETC    equ $F80806
BUFLIN  equ $0500
SDHC    equ $2F12
HCSARG  equ $2F14
SARG    equ $2F18
SCRC    equ $2F1C
SECN    equ $2F1E
CSD     equ $2F30
LSH     equ $2F40                ; copia-sombra do latch (word)
TK      equ $2F42                ; calibracao do buzzer (word, 256 = nominal)
SDOK    equ $2F44                ; word: 1 = cartao inicializado
SDMB    equ $2F46                ; long: capacidade em MB (SDHC)
SECBUF  equ $4000

        org $2000
start:  move.w  #4,LSH                  ; CS alto, todo o resto em 0
        move.w  #4,LATCH
        move.w  #256,TK
        move.w  #0,SDOK
        lea     m_title(pc),a1
        jsr     PUTS
        bsr     lcd_init
        bsr     lcd_banner
        bsr     sdinit
        bsr     lcd_status
main:   lea     m_prompt(pc),a1
        jsr     PUTS
        jsr     GETC
        andi.b  #$DF,d0                 ; maiuscula
        cmpi.b  #81,d0                  ; Q
        beq     quit
        cmpi.b  #73,d0                  ; I
        beq     cmd_i
        cmpi.b  #82,d0                  ; R
        beq     cmd_r
        cmpi.b  #66,d0                  ; B
        beq     cmd_b
        cmpi.b  #65,d0                  ; A
        beq     cmd_a
        cmpi.b  #75,d0                  ; K
        beq     cmd_k
        cmpi.b  #76,d0                  ; L
        beq     cmd_l
        bra     main
quit:   jsr     CRLF
        rts
cmd_i:  jsr     CRLF
        bsr     sdinit
        bsr     lcd_status
        bra     main
cmd_r:  jsr     CRLF
        lea     m_setor(pc),a1
        jsr     PUTS
        jsr     GETLINE
        movea.l #BUFLIN,a1
        jsr     GETHEX
        move.l  d0,SECN
        bsr     sdread
        tst.w   d0
        bne     cr_err
        lea     m_lido(pc),a1
        jsr     PUTS
        move.b  SECBUF+510,d0
        jsr     HEXB
        move.b  #32,d0
        jsr     PUTC
        move.b  SECBUF+511,d0
        jsr     HEXB
        jsr     CRLF
        bra     main
cr_err: lea     m_erro(pc),a1
        jsr     PUTS
        bra     main
cmd_b:  jsr     CRLF
        lea     m_notas(pc),a1
        jsr     PUTS
        lea     tab_notas(pc),a2
        moveq   #7,d5
cb_l:   move.w  (a2)+,d0
        move.w  (a2)+,d1
        bsr     tone
        move.l  #4000,d0
        bsr     dly
        dbra    d5,cb_l
        bra     main
cmd_a:  jsr     CRLF
        lea     m_440(pc),a1
        jsr     PUTS
        move.w  #502,d0
        move.w  #2640,d1
        bsr     tone
        bra     main
cmd_k:  jsr     CRLF
        lea     m_k(pc),a1
        jsr     PUTS
        jsr     GETLINE
        movea.l #BUFLIN,a1
        jsr     GETHEX
        tst.w   d0
        beq     main
        move.w  d0,TK
        lea     m_kok(pc),a1
        jsr     PUTS
        bra     main
cmd_l:  jsr     CRLF
        lea     m_lcdt(pc),a1
        jsr     PUTS
        moveq   #0,d0
        bsr     lcd_pos
        lea     t_l0(pc),a1
        bsr     lcd_puts
        moveq   #1,d0
        bsr     lcd_pos
        lea     t_l1(pc),a1
        bsr     lcd_puts
        moveq   #2,d0
        bsr     lcd_pos
        lea     t_l2(pc),a1
        bsr     lcd_puts
        moveq   #3,d0
        bsr     lcd_pos
        lea     t_l3(pc),a1
        bsr     lcd_puts
        bra     main

; ------------------------------------------------------------ latch com copia-sombra
; lset: liga os bits de d0.w ; lclr: desliga os bits de d0.w.  Destroem d0, d1.
lset:   move.w  LSH,d1
        or.w    d0,d1
        move.w  d1,LSH
        move.w  d1,LATCH
        rts
lclr:   not.w   d0
        move.w  LSH,d1
        and.w   d0,d1
        move.w  d1,LSH
        move.w  d1,LATCH
        rts
; dly: espera d0.l voltas de laco (cerca de 2,25 us por volta a 8 MHz)
dly:    subq.l  #1,d0
        bne     dly
        rts

; ------------------------------------------------------------ buzzer
; tone: d0.w = meio periodo (voltas de laco, valor nominal), d1.w = numero de meios ciclos (>=1)
tone:   move.w  TK,d3
        mulu.w  d3,d0
        lsr.l   #8,d0
        bne     t_ok
        moveq   #1,d0
t_ok:   move.l  d0,d7
        move.w  d1,d6
t_l:    move.w  LSH,d1
        eori.w  #$0200,d1
        move.w  d1,LSH
        move.w  d1,LATCH
        move.l  d7,d0
t_d:    subq.l  #1,d0
        bne     t_d
        subq.w  #1,d6
        bne     t_l
        move.w  #$0200,d0
        bsr     lclr
        rts
tab_notas:
        dc.w 422,314, 375,352, 334,395, 315,419, 280,470, 249,528, 222,593, 209,628

; ------------------------------------------------------------ LCD 20x4 (HD44780, 4 bits, RW no GND)
; lcd_nib: d0 = nibble, d2 = $10 (dado) ou 0 (comando). Destroi d0, d1, d3.
lcd_nib: andi.w #15,d0
        lsl.w   #5,d0
        or.w    d2,d0
        move.w  LSH,d1
        andi.w  #$FE07,d1               ; limpa E, RS, D4-D7 (bits 3 a 8)
        or.w    d0,d1
        move.w  d1,LSH
        move.w  d1,LATCH                ; dados no lugar, E = 0
        ori.w   #8,d1
        move.w  d1,LATCH                ; E = 1
        moveq   #8,d3
ln_w:   dbra    d3,ln_w
        andi.w  #$FFF7,d1
        move.w  d1,LATCH                ; E = 0: o LCD le na borda de descida
        move.w  d1,LSH
        rts
; lcd_byte: d0.b = byte, d2 = $10/0. Destroi d0, d1, d3, d4.
lcd_byte: move.w d0,d4
        lsr.w   #4,d0
        bsr     lcd_nib
        move.w  d4,d0
        bsr     lcd_nib
        move.l  #60,d0
        bsr     dly
        rts
lcd_cmd: moveq  #0,d2
        bra     lcd_byte
lcd_chr: moveq  #16,d2
        bra     lcd_byte
lcd_clr: move.b #1,d0
        bsr     lcd_cmd
        move.l  #2500,d0
        bsr     dly
        rts
; lcd_pos: d0 = linha 0 a 3
lcd_pos: tst.b  d0
        beq     lp0
        cmpi.b  #1,d0
        beq     lp1
        cmpi.b  #2,d0
        beq     lp2
        move.b  #$D4,d0
        bra     lcd_cmd
lp0:    move.b  #$80,d0
        bra     lcd_cmd
lp1:    move.b  #$C0,d0
        bra     lcd_cmd
lp2:    move.b  #$94,d0
        bra     lcd_cmd
lcd_puts: move.b (a1)+,d0
        beq     lps_x
        bsr     lcd_chr
        bra     lcd_puts
lps_x:  rts
; lcd_hexw: escreve d0.w em 4 digitos hexadecimais
lcd_hexw: move.w d0,d5
        moveq   #3,d6
lh_l:   move.w  d5,d0
        lsr.w   #8,d0
        lsr.w   #4,d0
        andi.w  #15,d0
        cmpi.w  #10,d0
        blt     lh_d
        addq.w  #7,d0
lh_d:   addi.w  #48,d0
        bsr     lcd_chr
        lsl.w   #4,d5
        dbra    d6,lh_l
        rts
lcd_init: move.l #20000,d0
        bsr     dly
        moveq   #0,d2
        moveq   #3,d0
        bsr     lcd_nib
        move.l  #6000,d0
        bsr     dly
        moveq   #3,d0
        bsr     lcd_nib
        move.l  #300,d0
        bsr     dly
        moveq   #3,d0
        bsr     lcd_nib
        move.l  #300,d0
        bsr     dly
        moveq   #2,d0                   ; passa para 4 bits
        bsr     lcd_nib
        move.l  #300,d0
        bsr     dly
        move.b  #$28,d0                 ; 4 bits, 2 linhas (20x4 usa este modo)
        bsr     lcd_cmd
        move.b  #$0C,d0                 ; display ligado, sem cursor
        bsr     lcd_cmd
        move.b  #$06,d0                 ; cursor avanca
        bsr     lcd_cmd
        bsr     lcd_clr
        rts
lcd_banner: moveq #0,d0
        bsr     lcd_pos
        lea     t_b0(pc),a1
        bsr     lcd_puts
        moveq   #1,d0
        bsr     lcd_pos
        lea     t_b1(pc),a1
        bsr     lcd_puts
        rts
lcd_status: moveq #2,d0
        bsr     lcd_pos
        tst.w   SDOK
        beq     st_no
        tst.w   SDHC
        bne     st_hc
        lea     l_sdsc(pc),a1
        bsr     lcd_puts
        moveq   #3,d0
        bsr     lcd_pos
        lea     l_blank(pc),a1
        bsr     lcd_puts
        rts
st_hc:  lea     l_sdhc(pc),a1
        bsr     lcd_puts
        moveq   #3,d0
        bsr     lcd_pos
        lea     l_cap(pc),a1
        bsr     lcd_puts
        move.l  SDMB,d0
        bsr     lcd_hexw
        lea     l_sp2(pc),a1
        bsr     lcd_puts
        rts
st_no:  lea     l_sdno(pc),a1
        bsr     lcd_puts
        moveq   #3,d0
        bsr     lcd_pos
        lea     l_blank(pc),a1
        bsr     lcd_puts
        rts

; ---------------------------------------------------------------- SPI (modo 0)
; spi_xfer: d0.b = byte a enviar; devolve d0.b = byte recebido. Destroi d1-d4.
spi_xfer:
        moveq   #7,d4
        move.w  LSH,d3
        andi.w  #$FFFC,d3               ; SCK e MOSI em 0, demais bits preservados
        moveq   #0,d2
sx_l:   move.w  d3,d1
        btst    d4,d0
        beq     sx_0
        ori.w   #2,d1                   ; MOSI = 1
sx_0:   move.w  d1,LATCH                ; SCK baixo, dado no lugar
        ori.w   #1,d1
        move.w  d1,LATCH                ; SCK alto: o cartao amostra MOSI
        move.w  MPORT,d1
        andi.w  #MMASK,d1
        add.w   d2,d2
        tst.w   d1
        bne     sx_n                    ; bit lido = 1 -> pino em nivel baixo -> MISO = 0
        addq.w  #1,d2                   ; bit lido = 0 -> MISO = 1
sx_n:   dbra    d4,sx_l
        move.w  d3,LATCH                ; SCK baixo
        move.w  d3,LSH
        move.w  d2,d0
        andi.w  #255,d0
        rts

sel:    move.l  d1,-(sp)                ; preserva d1 (argumento do comando)
        move.w  #4,d0
        bsr     lclr
        move.l  (sp)+,d1
        rts
desel:  move.w  #4,d0
        bsr     lset
        move.b  #$FF,d0                 ; 8 clocks extras
        bsr     spi_xfer
        rts

; sd_cmd: d0.b = comando ($40+n), d1.l = argumento, d2.b = CRC; devolve d0 = R1 ($FF = sem resposta)
sd_cmd: move.l  d1,SARG
        move.b  d2,SCRC
        bsr     spi_xfer
        move.b  SARG,d0
        bsr     spi_xfer
        move.b  SARG+1,d0
        bsr     spi_xfer
        move.b  SARG+2,d0
        bsr     spi_xfer
        move.b  SARG+3,d0
        bsr     spi_xfer
        move.b  SCRC,d0
        bsr     spi_xfer
        moveq   #15,d5
sc_p:   move.b  #$FF,d0
        bsr     spi_xfer
        btst    #7,d0
        beq     sc_ok
        dbra    d5,sc_p
sc_ok:  andi.w  #255,d0
        rts

; ---------------------------------------------------------------- inicializacao
sdinit: move.w  #0,SDOK
        move.w  #4,d0
        bsr     lset
        moveq   #9,d6                   ; 80 clocks com CS alto
si_c:   move.b  #$FF,d0
        bsr     spi_xfer
        dbra    d6,si_c
        move.w  #0,SDHC
        moveq   #9,d7
si_0:   bsr     sel
        move.b  #$40,d0                 ; CMD0
        moveq   #0,d1
        move.b  #$95,d2
        bsr     sd_cmd
        cmpi.b  #1,d0
        beq     si_0k
        bsr     desel
        dbra    d7,si_0
        bra     si_fail
si_0k:  bsr     desel
        move.l  #0,HCSARG
        bsr     sel
        move.b  #$48,d0                 ; CMD8
        move.l  #$1AA,d1
        move.b  #$87,d2
        bsr     sd_cmd
        cmpi.b  #1,d0
        bne     si_v1
        move.l  #$40000000,HCSARG       ; cartao v2: pede HCS
        moveq   #3,d6                   ; descarta R7 (4 bytes)
si_r7:  move.b  #$FF,d0
        bsr     spi_xfer
        dbra    d6,si_r7
si_v1:  bsr     desel
        move.w  #3000,d7                ; ACMD41 ate ficar pronto
si_a:   bsr     sel
        move.b  #$77,d0                 ; CMD55
        moveq   #0,d1
        move.b  #$65,d2
        bsr     sd_cmd
        bsr     desel
        bsr     sel
        move.b  #$69,d0                 ; ACMD41
        move.l  HCSARG,d1
        move.b  #$77,d2
        bsr     sd_cmd
        move.w  d0,d6
        bsr     desel
        tst.b   d6
        beq     si_rdy
        subq.w  #1,d7
        bne     si_a
        bra     si_fail
si_rdy: bsr     sel
        move.b  #$7A,d0                 ; CMD58 (OCR)
        moveq   #0,d1
        move.b  #$FD,d2
        bsr     sd_cmd
        tst.b   d0
        bne     si_f2
        move.b  #$FF,d0
        bsr     spi_xfer
        andi.b  #$40,d0                 ; CCS
        beq     si_s
        move.w  #1,SDHC
si_s:   moveq   #2,d6
si_o:   move.b  #$FF,d0
        bsr     spi_xfer
        dbra    d6,si_o
        bsr     desel
        tst.w   SDHC
        bne     si_ok
        bsr     sel
        move.b  #$50,d0                 ; CMD16: bloco de 512 bytes (cartao padrao)
        move.l  #512,d1
        move.b  #$FF,d2
        bsr     sd_cmd
        bsr     desel
si_ok:  move.w  #1,SDOK
        lea     m_ok(pc),a1
        jsr     PUTS
        tst.w   SDHC
        bne     si_h
        lea     m_sd(pc),a1
        bra     si_p
si_h:   lea     m_sdhc(pc),a1
si_p:   jsr     PUTS
        bsr     sdcap
        rts
si_f2:  bsr     desel
si_fail:
        lea     m_fail(pc),a1
        jsr     PUTS
        rts

; capacidade (so cartoes SDHC/SDXC: CSD versao 2)
sdcap:  tst.w   SDHC
        beq     sdcap_x
        bsr     sel
        move.b  #$49,d0                 ; CMD9
        moveq   #0,d1
        move.b  #$FF,d2
        bsr     sd_cmd
        tst.b   d0
        bne     sdcap_e
        move.w  #20000,d5
sdc_w:  move.b  #$FF,d0
        bsr     spi_xfer
        cmpi.b  #$FE,d0
        beq     sdc_g
        subq.w  #1,d5
        bne     sdc_w
        bra     sdcap_e
sdc_g:  movea.l #CSD,a2
        moveq   #15,d6
sdc_l:  move.b  #$FF,d0
        bsr     spi_xfer
        move.b  d0,(a2)+
        dbra    d6,sdc_l
        move.b  #$FF,d0
        bsr     spi_xfer
        move.b  #$FF,d0
        bsr     spi_xfer
        bsr     desel
        moveq   #0,d0                   ; C_SIZE = CSD[7]&$3F, CSD[8], CSD[9]
        move.b  CSD+7,d0
        andi.l  #$3F,d0
        lsl.l   #8,d0
        move.b  CSD+8,d1
        andi.l  #255,d1
        or.l    d1,d0
        lsl.l   #8,d0
        move.b  CSD+9,d1
        andi.l  #255,d1
        or.l    d1,d0
        addq.l  #1,d0                   ; (C_SIZE+1) * 512 KB
        lsr.l   #1,d0                   ; em MB
        move.l  d0,SDMB
        move.l  d0,d6
        lea     m_cap(pc),a1
        jsr     PUTS
        move.l  d6,d0
        jsr     HEXL
        lea     m_mb(pc),a1
        jsr     PUTS
sdcap_x:
        rts
sdcap_e:
        bsr     desel
        rts

; ---------------------------------------------------------------- leitura de setor
; sdread: le SECN para SECBUF ($4000..$41FF). Devolve d0 = 0 se OK.
sdread: move.l  SECN,d1
        tst.w   SDHC
        bne     rd_a
        lsl.l   #8,d1                   ; cartao padrao: endereco em bytes (x512)
        lsl.l   #1,d1
rd_a:   bsr     sel
        move.b  #$51,d0                 ; CMD17
        move.b  #$FF,d2
        bsr     sd_cmd
        tst.b   d0
        bne     rd_f
        move.w  #20000,d5
rd_w:   move.b  #$FF,d0
        bsr     spi_xfer
        cmpi.b  #$FE,d0
        beq     rd_g
        subq.w  #1,d5
        bne     rd_w
        bra     rd_f
rd_g:   movea.l #SECBUF,a2
        move.w  #511,d6
rd_l:   move.b  #$FF,d0
        bsr     spi_xfer
        move.b  d0,(a2)+
        dbra    d6,rd_l
        move.b  #$FF,d0
        bsr     spi_xfer
        move.b  #$FF,d0
        bsr     spi_xfer
        bsr     desel
        moveq   #0,d0
        rts
rd_f:   bsr     desel
        moveq   #1,d0
        rts


m_title:  dc.b 13,10,"PERIFERICOS - PARAGON 50 (SD + buzzer + LCD 20x4)",13,10
          dc.b "Comandos: I SD, R setor, B notas, A tom 440 Hz, K calibra, L teste LCD, Q sai.",13,10,0
m_prompt: dc.b "PER> ",0
m_setor:  dc.b "Setor (hexadecimal)? ",0
m_lido:   dc.b "Lido em $004000-$0041FF (use D 4000 41FF). Bytes 510-511: ",0
m_erro:   dc.b "ERRO na leitura do setor",13,10,0
m_ok:     dc.b "Cartao inicializado: ",0
m_sd:     dc.b "SD padrao (enderecamento por byte)",13,10,0
m_sdhc:   dc.b "SDHC/SDXC (enderecamento por bloco)",13,10,0
m_cap:    dc.b "Capacidade: $",0
m_mb:     dc.b " MB",13,10,0
m_fail:   dc.b "FALHA ao inicializar o cartao (confira fiacao, 3,3 V, MISO com 330 ohms)",13,10,0
m_notas:  dc.b "Tocando a escala de DO5 a DO6...",13,10,0
m_440:    dc.b "Tom de 440 Hz por 3 s (se desafinado use K)...",13,10,0
m_k:      dc.b "Calibracao (hexadecimal; 100 = nominal, maior = mais grave)? ",0
m_kok:    dc.b "Calibracao gravada. Use A para ouvir o 440 Hz.",13,10,0
m_lcdt:   dc.b "LCD: quatro linhas de 20 colunas.",13,10,0
t_b0:     dc.b "PARAGON 50  68000   ",0
t_b1:     dc.b "Tabajara Labs       ",0
t_l0:     dc.b "01234567890123456789",0
t_l1:     dc.b "ABCDEFGHIJKLMNOPQRST",0
t_l2:     dc.b "abcdefghijklmnopqrst",0
t_l3:     dc.b "Fim do teste LCD  OK",0
l_sdhc:   dc.b "SD OK  SDHC         ",0
l_sdsc:   dc.b "SD OK  padrao       ",0
l_sdno:   dc.b "SD: sem cartao      ",0
l_blank:  dc.b "                    ",0
l_cap:    dc.b "Capac MB hex $",0
l_sp2:    dc.b "  ",0
