; ==========================================================================
;  SD.ASM - driver de cartao SD (modo SPI) para o PARAGON 50, so leitura
;  Carregar com L e executar com G 2000.
;  Fiacao (bit-banging, sem hardware novo):
;    SCK  = latch $020018 bit 0 -> J1-28        CS = latch $020018 bit 2 -> J1-24
;    MOSI = latch $020018 bit 1 -> J1-26        MISO = porta B $020028 bit 0 <- J1-7
;  (os 74LS240 invertem: o bit lido e 0 quando o pino MISO esta em nivel alto)
;  Comandos:  I  inicializa o cartao       R  le um setor (numero em hexadecimal)
;             Q  volta ao monitor          Depois de R use  D 4000 41FF  para ver o setor.
; ==========================================================================
LATCH   equ $020018
MPORT   equ $020028              ; porta B
MMASK   equ $0001                ; bit 0
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
CSB     equ $2F10                ; word: 4 = CS alto (cartao solto), 0 = CS baixo (selecionado)
SDHC    equ $2F12                ; word: 1 = SDHC/SDXC (enderecamento por bloco)
HCSARG  equ $2F14                ; long: argumento do ACMD41
SARG    equ $2F18                ; long: argumento do comando
SCRC    equ $2F1C                ; byte
SECN    equ $2F1E                ; long: numero do setor
CSD     equ $2F30                ; 16 bytes do CSD
SECBUF  equ $4000

        org $2000
start:  lea     m_title(pc),a1
        jsr     PUTS
        bsr     sdinit
main:   lea     m_prompt(pc),a1
        jsr     PUTS
        jsr     GETC
        andi.b  #$DF,d0                 ; maiuscula
        cmpi.b  #81,d0                  ; 'Q'
        beq     quit
        cmpi.b  #73,d0                  ; 'I'
        beq     cmd_i
        cmpi.b  #82,d0                  ; 'R'
        beq     cmd_r
        bra     main
quit:   jsr     CRLF
        rts
cmd_i:  jsr     CRLF
        bsr     sdinit
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

; ---------------------------------------------------------------- SPI (modo 0)
; spi_xfer: d0.b = byte a enviar; devolve d0.b = byte recebido. Destroi d1-d4.
spi_xfer:
        moveq   #7,d4
        move.w  CSB,d3
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
        move.w  d2,d0
        andi.w  #255,d0
        rts

sel:    move.w  #0,CSB
        move.w  #0,LATCH
        rts
desel:  move.w  #4,CSB
        move.w  #4,LATCH
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
sdinit: move.w  #4,CSB
        move.w  #4,LATCH
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
si_ok:  lea     m_ok(pc),a1
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

m_title:  dc.b 13,10,"SD (SPI) - PARAGON 50.  SCK=J1-28  MOSI=J1-26  CS=J1-24  MISO=J1-7",13,10
          dc.b "Comandos: I inicializa, R le um setor (hexadecimal), Q sai.",13,10,0
m_prompt: dc.b "SD> ",0
m_setor:  dc.b "Setor (hexadecimal)? ",0
m_lido:   dc.b "Lido em $004000-$0041FF (use D 4000 41FF). Bytes 510-511: ",0
m_erro:   dc.b "ERRO na leitura do setor",13,10,0
m_ok:     dc.b "Cartao inicializado: ",0
m_sd:     dc.b "SD padrao (enderecamento por byte)",13,10,0
m_sdhc:   dc.b "SDHC/SDXC (enderecamento por bloco)",13,10,0
m_cap:    dc.b "Capacidade: $",0
m_mb:     dc.b " MB",13,10,0
m_fail:   dc.b "FALHA ao inicializar o cartao (confira fiacao, alimentacao de 3,3 V e o MISO)",13,10,0
