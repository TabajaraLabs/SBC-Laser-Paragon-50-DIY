; ==========================================================================
;  FATSH v5 (banco 0) - leitor FAT16 (SOMENTE LEITURA) + driver SD para o PARAGON 50
;  Carregar com L e executar com G 2000.   (versao de desenvolvimento em RAM)
;  Comandos:  I  inicia o cartao e monta o FAT16      D [pasta]  lista a pasta
;             T arquivo  mostra um arquivo de texto   L arquivo enderecoHex  carrega na RAM
;             S  espaco (usado/livre)                 ? ajuda      Q sai
;  Aceita setor 0 como boot sector (superfloppy) ou MBR com 1a particao FAT16.
;  Nomes: 8.3 e nomes longos (LFN) sem distinguir maiusculas; caminho com '/'.
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
GETC    equ $F80806
GETLINE equ $F80836
GETHEX  equ $F80830
BUFLIN  equ $0500
; ---- RAM do driver SD (igual ao sd.asm)
CSB     equ $3910
SDHC    equ $3912
HCSARG  equ $3914
SARG    equ $3918
SCRC    equ $391C
SECN    equ $391E
CSD     equ $3930
RDST    equ $3950
; ---- RAM do FAT
FATSEC  equ $3800
ROOTSEC equ $3804
ROOTSZ  equ $3808
DATASEC equ $380C
SPC     equ $3810
SPCSH   equ $3814
NCLU    equ $3818
PART    equ $381C
TOTSEC  equ $3820
FATSZ   equ $3824
FATCS   equ $3828
MOUNT   equ $382C
LABEL   equ $3830             ; 12 bytes
CS_CL   equ $3840
CS_IX   equ $3844
FCL     equ $3848
FSZ     equ $384C
FATT    equ $3850
DCL     equ $3854
LRST    equ $3858
COMPP   equ $385C
COMPL   equ $3860
NMOK    equ $3864
LFNV    equ $3866
NAME    equ $3868             ; 12 bytes
DECBUF  equ $3878             ; 12 bytes
FREEC   equ $3884
LADDR   equ $3888
LFNBUF  equ $3890             ; 64 bytes
LSH     equ $3960
LCDOK   equ $3962
STAR    equ $3964
FLBK    equ $3968
SECBUF  equ $4000
FATBUF  equ $4200
; ---- v8: variaveis da gravacao (vindas do fatsh_v7): $4A00-$4A4F e buffer de 512 bytes em $4C00
CS_SEC  equ $4A00
DSEC    equ $4A04
DOFF    equ $4A08
WST     equ $4A0A
FATD    equ $4A0E
NXTFRE  equ $4A10
WCL     equ $4A14
WIX     equ $4A18
WPOS    equ $4A1C
WSIZE   equ $4A20
WFIRST  equ $4A24
WDSEC   equ $4A28
WDOFF   equ $4A2C
DTIME   equ $4A30
DDATE   equ $4A32
CWD     equ $4A34
WNAME   equ $4A38
SAVA    equ $4A48
SAVL    equ $4A4C
WBUF    equ $4C00
        org SHORG
start:  move.l  #0,CWD
        move.w  #$5D6E,DDATE
        move.w  #$6000,DTIME
        move.l  #2,NXTFRE
        move.w  #0,FATD
        move.w  #4,LSH
        move.w  #4,LATCH
        move.w  #0,STAR
        move.w  #0,LCDOK
        lea     m_title(pc),a1
        jsr     PUTS
        bsr     lcd_init
        move.w  #1,LCDOK
        bsr     lcd_banner
        bsr     do_init
main:   bsr     actv_off
        lea     m_prompt(pc),a1
        jsr     PUTS
        jsr     GETLINE
        movea.l #BUFLIN,a1
        bsr     skipsp
        move.b  (a1)+,d0
        beq     main
        andi.b  #$DF,d0
        cmpi.b  #'Q',d0
        beq     quit
        cmpi.b  #'I',d0
        beq     c_init
        cmpi.b  #'D',d0
        beq     c_dir
        cmpi.b  #'T',d0
        beq     c_type
        cmpi.b  #'L',d0
        beq     c_load
        cmpi.b  #'S',d0
        beq     c_space
        cmpi.b  #'W',d0
        beq     c_save
        cmpi.b  #'K',d0
        beq     c_kill
        cmpi.b  #'C',d0
        beq     c_cd
        cmpi.b  #'F',d0
        beq     c_flash
        lea     m_help(pc),a1
        jsr     PUTS
        bra     main
quit:   rts
c_init: bsr     do_init
        bra     main

; ---- D [pasta]
c_dir:  bsr     skipsp
        move.l  CWD,DCL
        tst.b   (a1)
        beq     cd_go
        bsr     fat_open
        tst.w   d0
        bne     c_nf
        move.l  FATT,d0
        btst    #4,d0
        beq     c_nd
        move.l  FCL,DCL
cd_go:  bsr     dir_list
        bra     main
c_nf:   lea     m_nf(pc),a1
        jsr     PUTS
        bra     main
c_nd:   lea     m_nd(pc),a1
        jsr     PUTS
        bra     main

; ---- T arquivo
c_type: bsr     skipsp
        bsr     fat_open
        tst.w   d0
        bne     c_nf
        move.l  FATT,d0
        btst    #4,d0
        bne     c_ndir
        move.l  FCL,d0
        bsr     cs_open
        move.l  FSZ,LRST
ct_l:   tst.l   LRST
        beq     ct_x
        bsr     cs_read
        tst.w   d0
        bne     c_rerr
        move.l  #512,d3
        cmp.l   LRST,d3
        bcs     ct_n                    ; 512 < restante: usa 512
        move.l  LRST,d3
ct_n:   sub.l   d3,LRST
        lea     SECBUF,a0
        subq.w  #1,d3
ct_c:   move.b  (a0)+,d0
        cmpi.b  #10,d0
        beq     ct_p
        cmpi.b  #13,d0
        beq     ct_p
        cmpi.b  #32,d0
        bcs     ct_s
        cmpi.b  #127,d0
        bcc     ct_s
ct_p:   jsr     PUTC
        bra     ct_k
ct_s:   moveq   #46,d0
        jsr     PUTC
ct_k:   dbra    d3,ct_c
        bra     ct_l
ct_x:   jsr     CRLF
        bra     main
c_ndir: lea     m_isdir(pc),a1
        jsr     PUTS
        bra     main
c_rerr: lea     m_rerr(pc),a1
        jsr     PUTS
        bra     main

; ---- L arquivo enderecoHex   (o ultimo item da linha e o endereco)
c_load: bsr     skipsp
        movea.l a1,a2
cl_e:   tst.b   (a2)+
        bne     cl_e
        subq.l  #1,a2                   ; a2 = fim da linha
cl_b:   cmpa.l  a1,a2
        beq     cl_bad
        subq.l  #1,a2
        cmpi.b  #32,(a2)
        bne     cl_b
        move.b  #0,(a2)                 ; corta o caminho
        addq.l  #1,a2
        movea.l a1,a3                   ; a3 = caminho
        movea.l a2,a1
        jsr     GETHEX
        move.l  d0,d6
        tst.w   d1
        beq     cl_bad
        movea.l a3,a1
        move.l  d6,LADDR
        bsr     fat_open
        tst.w   d0
        bne     c_nf
        move.l  FATT,d0
        btst    #4,d0
        bne     c_ndir
        movea.l LADDR,a0
        bsr     fat_load
        tst.w   d0
        bne     c_rerr
        lea     m_ld(pc),a1
        jsr     PUTS
        move.l  FSZ,d0
        bsr     putdec
        lea     m_ld2(pc),a1
        jsr     PUTS
        move.l  LADDR,d0
        jsr     HEXL
        jsr     CRLF
        bra     main
cl_bad: lea     m_use(pc),a1
        jsr     PUTS
        bra     main

; ---- F banco arquivo : le o arquivo (imagem de 128 KB com cabecalho AB) para $40000 e grava no banco 1..7 com o flasher v5c
c_flash: bsr    skipsp
        jsr     GETHEX                  ; d0 = banco, d1 = no. de digitos, a1 avanca
        tst.l   d1
        beq     fl_use
        tst.l   d0
        beq     fl_b0
        cmpi.l  #7,d0
        bhi     fl_use
        move.w  d0,FLBK
        bsr     skipsp
        tst.b   (a1)
        beq     fl_use
        bsr     fat_open
        tst.w   d0
        bne     c_nf
        move.l  FATT,d0
        btst    #4,d0
        bne     c_ndir
        cmpi.l  #$20000,FSZ
        bne     fl_sz
        movea.l #$40000,a0
        bsr     fat_load
        tst.w   d0
        bne     c_rerr
        lea     m_flq(pc),a1
        jsr     PUTS
        jsr     GETLINE
        lea     BUFLIN,a0
        lea     s_pros(pc),a1
fl_p:   move.b  (a1)+,d0
        beq     fl_pe
        cmp.b   (a0)+,d0
        bne     fl_cmp
        bra     fl_p
fl_pe:  tst.b   (a0)
        bne     fl_cmp
        moveq   #1,d5                   ; gravar
        lea     m_flw(pc),a1
        bra     fl_go
fl_cmp: moveq   #0,d5                   ; so comparar
        lea     m_flc(pc),a1
fl_go:  jsr     PUTS
        lea     FLIMG,a0                ; copia o flasher para $2000
        lea     $2000,a1
        move.w  #FLLEN-1,d1
fl_c:   move.b  (a0)+,(a1)+
        dbra    d1,fl_c
        lea     $3000,a0                ; zera as variaveis do flasher ($3000-$302F)
        moveq   #11,d1
fl_z:   clr.l   (a0)+
        dbra    d1,fl_z
        move.w  FLBK,$301C              ; banco de destino
        move.w  #RCBANK,$3028           ; banco de retorno do flasher (0 no banco 0 definitivo)
        move.w  #$C0DE,$302A
        move.w  #8,$3024                ; origem 8 = imagem ja em $40000
        move.w  #$C0DE,$3026
        tst.w   d5
        beq     fl_run
        move.w  #1,$3000                ; MODE = gravar
        move.w  #$A55A,$3002
fl_run: jsr     $2000
        bsr     do_init                 ; o flasher usou $4000...: remonta o cartao
        bra     main
fl_use: lea     m_fuse(pc),a1
        jsr     PUTS
        bra     main
fl_b0:  lea     m_fb0(pc),a1
        jsr     PUTS
        bra     main
fl_sz:  lea     m_fsz(pc),a1
        jsr     PUTS
        bra     main

; ---- S : espaco
c_space:
        tst.w   MOUNT
        beq     c_nomnt
        bsr     fat_free
        lea     m_tot(pc),a1
        jsr     PUTS
        move.l  NCLU,d0
        move.l  SPCSH,d2
        lsl.l   d2,d0
        lsr.l   #1,d0                   ; setores/2 = KB
        move.l  d0,d4
        bsr     putdec
        lea     m_kb(pc),a1
        jsr     PUTS
        lea     m_liv(pc),a1
        jsr     PUTS
        move.l  FREEC,d0
        move.l  SPCSH,d2
        lsl.l   d2,d0
        lsr.l   #1,d0
        move.l  d0,d5
        bsr     putdec
        lea     m_kb(pc),a1
        jsr     PUTS
        lea     m_usa(pc),a1
        jsr     PUTS
        move.l  d4,d0
        sub.l   d5,d0
        bsr     putdec
        lea     m_kb(pc),a1
        jsr     PUTS
        jsr     CRLF
        bsr     lcd_free
        bra     main
c_nomnt:
        lea     m_nomnt(pc),a1
        jsr     PUTS
        bra     main

; ---------------------------------------------------------------- inicia + monta
do_init:
        bsr     sdinit
        tst.w   d0
        bne     di_nc
        bsr     fat_mount
        tst.w   d0
        beq     di_ok
        cmpi.w  #1,d0
        beq     di_e1
        lea     m_nofat(pc),a1
        jsr     PUTS
        lea     l_nofat(pc),a1
        bsr     lcd_l1
        rts
di_nc:  lea     l_sdno(pc),a1
        bsr     lcd_l1
        rts
di_e1:  lea     m_rerr(pc),a1
        jsr     PUTS
        rts
di_ok:  bsr     find_label
        bsr     lcd_show
        lea     m_vol(pc),a1
        jsr     PUTS
        lea     LABEL,a1
        jsr     PUTS
        lea     m_fs(pc),a1
        jsr     PUTS
        move.l  TOTSEC,d0
        lsr.l   #1,d0
        lsr.l   #8,d0
        lsr.l   #2,d0                   ; setores/2048 = MB
        bsr     putdec
        lea     m_mb(pc),a1
        jsr     PUTS
        move.l  SPC,d0
        lsr.l   #1,d0
        bsr     putdec
        lea     m_kcl(pc),a1
        jsr     PUTS
di_x:   rts

skipsp: cmpi.b  #32,(a1)
        bne     ss_x
        addq.l  #1,a1
        bra     skipsp
ss_x:   rts

; ---------------------------------------------------------------- utilitarios
ld16:   moveq   #0,d0
        move.b  1(a0),d0
        lsl.w   #8,d0
        move.b  (a0),d0
        rts
ld32:   moveq   #0,d0
        move.b  3(a0),d0
        lsl.l   #8,d0
        move.b  2(a0),d0
        lsl.l   #8,d0
        move.b  1(a0),d0
        lsl.l   #8,d0
        move.b  (a0),d0
        rts

; putdec: d0.l em decimal
putdec: movem.l d0-d3/a0-a1,-(sp)
        bsr     dec2str
        jsr     PUTS
        movem.l (sp)+,d0-d3/a0-a1
        rts
; dec2str: d0.l -> a1 = texto decimal em DECBUF
dec2str: movem.l d0-d3/a0,-(sp)
        lea     DECBUF+11,a0
        move.b  #0,(a0)
pd_l:   move.l  d0,d1
        swap    d1
        andi.l  #$FFFF,d1
        divu    #10,d1                  ; d1 = resto:quociente (alto)
        moveq   #0,d3
        move.w  d1,d3
        swap    d3
        move.l  d1,d2
        clr.w   d2
        move.w  d0,d2
        divu    #10,d2
        move.w  d2,d3                   ; d3 = quociente de 32 bits
        swap    d2
        addi.b  #48,d2
        move.b  d2,-(a0)
        move.l  d3,d0
        bne     pd_l
        movea.l a0,a1
        movem.l (sp)+,d0-d3/a0
        rts


; find_label: procura na RAIZ a entrada de rotulo de volume (atributo $08); senao fica o rotulo do BPB. Apara espacos.
find_label:
        moveq   #0,d0
        bsr     cs_open
fb_s:   bsr     cs_read
        tst.w   d0
        bne     fb_t
        lea     SECBUF,a0
        moveq   #15,d7
fb_e:   move.b  (a0),d0
        beq     fb_t
        cmpi.b  #$E5,d0
        beq     fb_n
        move.b  11(a0),d1
        andi.b  #$3F,d1
        cmpi.b  #8,d1
        bne     fb_n
        lea     LABEL,a1
        moveq   #10,d0
fb_c:   move.b  (a0)+,(a1)+
        dbra    d0,fb_c
        move.b  #0,(a1)
        bra     fb_t
fb_n:   lea     32(a0),a0
        dbra    d7,fb_e
        bra     fb_s
fb_t:   lea     LABEL+10,a0
        moveq   #10,d0
fb_tl:  cmpi.b  #32,(a0)
        bne     fb_x
        move.b  #0,(a0)
        subq.l  #1,a0
        dbra    d0,fb_tl
fb_x:   rts

; ------------------------------------------------------------ LCD 20x4 (HD44780, 4 bits) - rotinas do perif_v2
dly:    subq.l  #1,d0
        bne     dly
        rts
lcd_nib: andi.w #15,d0
        lsl.w   #5,d0
        or.w    d2,d0
        move.w  LSH,d1
        andi.w  #$FE07,d1
        or.w    d0,d1
        move.w  d1,LSH
        move.w  d1,LATCH
        ori.w   #8,d1
        move.w  d1,LATCH
        moveq   #8,d3
ln_w:   dbra    d3,ln_w
        andi.w  #$FFF7,d1
        move.w  d1,LATCH
        move.w  d1,LSH
        rts
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
lcd_puts: move.b (a1)+,d0
        beq     lps_x
        bsr     lcd_chr
        bra     lcd_puts
lps_x:  rts
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
        moveq   #2,d0
        bsr     lcd_nib
        move.l  #300,d0
        bsr     dly
        move.b  #$28,d0
        bsr     lcd_cmd
        move.b  #$0C,d0
        bsr     lcd_cmd
        move.b  #$06,d0
        bsr     lcd_cmd
        bsr     lcd_clr
        rts
; lcd_goto: d0 = linha 0..3, d1 = coluna
lcd_goto:
        movem.l d0-d5,-(sp)
        move.w  d1,d5
        tst.b   d0
        beq     lg0
        cmpi.b  #1,d0
        beq     lg1
        cmpi.b  #2,d0
        beq     lg2
        move.b  #$D4,d0
        bra     lgx
lg0:    move.b  #$80,d0
        bra     lgx
lg1:    move.b  #$C0,d0
        bra     lgx
lg2:    move.b  #$94,d0
lgx:    add.b   d5,d0
        bsr     lcd_cmd
        movem.l (sp)+,d0-d5
        rts
; lcd_blank: apaga a linha d0 (20 espacos) e deixa o cursor no inicio
lcd_blank:
        movem.l d0-d5/a1,-(sp)
        moveq   #0,d1
        bsr     lcd_goto
        moveq   #19,d6
lb_l:   moveq   #32,d0
        bsr     lcd_chr
        dbra    d6,lb_l
        movem.l (sp)+,d0-d5/a1
        movem.l d0-d5/a1,-(sp)
        moveq   #0,d1
        bsr     lcd_goto
        movem.l (sp)+,d0-d5/a1
        rts
; lcd_l1: a1 = texto -> linha 1 (apaga antes)
lcd_l1: movem.l d0-d6/a1,-(sp)
        moveq   #1,d0
        bsr     lcd_blank
        bsr     lcd_puts
        movem.l (sp)+,d0-d6/a1
        rts
lcd_banner:
        movem.l d0-d6/a1,-(sp)
        moveq   #0,d0
        bsr     lcd_blank
        lea     t_b0(pc),a1
        bsr     lcd_puts
        movem.l (sp)+,d0-d6/a1
        rts
; lcd_show: linhas 1 a 3 com o cartao montado
lcd_show:
        movem.l d0-d7/a0-a1,-(sp)
        moveq   #1,d0
        bsr     lcd_blank
        lea     l_sd(pc),a1
        bsr     lcd_puts
        lea     LABEL,a1
        bsr     lcd_puts
        moveq   #2,d0
        bsr     lcd_blank
        move.l  TOTSEC,d0
        lsr.l   #8,d0
        lsr.l   #3,d0                   ; setores/2048 = MB
        bsr     dec2str
        bsr     lcd_puts
        lea     l_mb(pc),a1
        bsr     lcd_puts
        move.l  SPC,d0
        lsr.l   #1,d0
        bsr     dec2str
        bsr     lcd_puts
        lea     l_kcl(pc),a1
        bsr     lcd_puts
        moveq   #3,d0
        bsr     lcd_blank
        lea     l_sdsc(pc),a1
        tst.w   SDHC
        beq     ls_t
        lea     l_sdhc(pc),a1
ls_t:   bsr     lcd_puts
        movem.l (sp)+,d0-d7/a0-a1
        rts
; lcd_free: linha 3 = usado/livre em KB (FREEC/NCLU ja calculados)
lcd_free:
        movem.l d0-d7/a0-a1,-(sp)
        moveq   #3,d0
        bsr     lcd_blank
        lea     l_liv(pc),a1
        bsr     lcd_puts
        move.l  FREEC,d0
        move.l  SPCSH,d2
        lsl.l   d2,d0
        lsr.l   #1,d0
        lsr.l   #8,d0
        lsr.l   #2,d0                   ; KB -> MB (>>10)
        bsr     dec2str
        bsr     lcd_puts
        lea     l_mbl(pc),a1
        bsr     lcd_puts
        movem.l (sp)+,d0-d7/a0-a1
        rts
; star: pisca o '*' (linha 1, coluna 19). Chamada com o CS do cartao alto, no inicio de cada leitura.
actv:   tst.w   LCDOK
        beq     st_x
        tst.w   STAR
        bne     st_x
        movem.l d0-d6/a1,-(sp)
        move.w  #1,STAR
        moveq   #1,d0
        moveq   #19,d1
        bsr     lcd_goto
        moveq   #42,d0
        bsr     lcd_chr
        movem.l (sp)+,d0-d6/a1
st_x:   rts
actv_off:
        tst.w   LCDOK
        beq     so_x
        tst.w   STAR
        beq     so_x
        movem.l d0-d6/a1,-(sp)
        move.w  #0,STAR
        moveq   #1,d0
        moveq   #19,d1
        bsr     lcd_goto
        moveq   #32,d0
        bsr     lcd_chr
        movem.l (sp)+,d0-d6/a1
so_x:   rts

; ---------------------------------------------------------------- SPI (modo 0)
spi_xfer:
        cmpi.b  #$FF,d0
        beq     spi_rd                  ; v2: leitura pura (MOSI=1) usa a rotina rapida
        moveq   #7,d4
        move.w  CSB,d3
        moveq   #0,d2
sx_l:   move.w  d3,d1
        btst    d4,d0
        beq     sx_0
        ori.w   #2,d1
sx_0:   move.w  d1,LATCH
        ori.w   #1,d1
        move.w  d1,LATCH
        move.w  MPORT,d1
        andi.w  #MMASK,d1
        add.w   d2,d2
        tst.w   d1
        bne     sx_n
        addq.w  #1,d2
sx_n:   dbra    d4,sx_l
        move.w  d3,LATCH
        move.w  d2,d0
        andi.w  #255,d0
        rts

; spi_rd (v2): recebe 1 byte com MOSI=1. Rapida: registradores de endereco, sem acessos absolutos. Destroi d1-d4,a0,a1.
spi_rd: move.w  CSB,d3
        move.w  d3,d4
        ori.w   #2,d3                   ; d3 = SCK baixo, MOSI alto
        ori.w   #3,d4                   ; d4 = SCK alto,  MOSI alto
        lea     LATCH,a0
        lea     MPORT,a1
        moveq   #0,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        move.w  CSB,(a0)
        eori.w  #$FF,d2                 ; o 74LS240 inverte o MISO
        move.w  d2,d0
        andi.w  #255,d0
        rts
sel:    move.w  #0,CSB
        move.w  #0,LATCH
        rts
desel:  move.w  #4,CSB
        move.w  #4,LATCH
        move.b  #$FF,d0
        bsr     spi_xfer
        rts
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

; sdinit: d0 = 0 ok, 1 falha
sdinit: move.w  #4,CSB
        move.w  #4,LATCH
        moveq   #9,d6
si_c:   move.b  #$FF,d0
        bsr     spi_xfer
        dbra    d6,si_c
        move.w  #0,SDHC
        move.w  #0,MOUNT
        moveq   #9,d7
si_0:   bsr     sel
        move.b  #$40,d0
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
        move.b  #$48,d0
        move.l  #$1AA,d1
        move.b  #$87,d2
        bsr     sd_cmd
        cmpi.b  #1,d0
        bne     si_v1
        move.l  #$40000000,HCSARG
        moveq   #3,d6
si_r7:  move.b  #$FF,d0
        bsr     spi_xfer
        dbra    d6,si_r7
si_v1:  bsr     desel
        move.w  #3000,d7
si_a:   bsr     sel
        move.b  #$77,d0
        moveq   #0,d1
        move.b  #$65,d2
        bsr     sd_cmd
        bsr     desel
        bsr     sel
        move.b  #$69,d0
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
        move.b  #$7A,d0
        moveq   #0,d1
        move.b  #$FD,d2
        bsr     sd_cmd
        tst.b   d0
        bne     si_f2
        move.b  #$FF,d0
        bsr     spi_xfer
        andi.b  #$40,d0
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
        move.b  #$50,d0
        move.l  #512,d1
        move.b  #$FF,d2
        bsr     sd_cmd
        bsr     desel
si_ok:  moveq   #0,d0
        rts
si_f2:  bsr     desel
si_fail:
        lea     m_fail(pc),a1
        jsr     PUTS
        moveq   #1,d0
        rts

; rdsec: le SECN em SECBUF. sdread: le SECN em (RDST). d0 = 0 ok
rdsec:  move.l  #SECBUF,RDST
sdread: movem.l d1-d7/a0-a6,-(sp)
        bsr     sdread_i
        movem.l (sp)+,d1-d7/a0-a6
        rts
sdread_i: bsr     actv
        move.l  SECN,d1
        tst.w   SDHC
        bne     rd_a
        lsl.l   #8,d1
        lsl.l   #1,d1
rd_a:   bsr     sel
        move.b  #$51,d0
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
rd_g:   movea.l RDST,a2
        lea     LATCH,a0                ; v4: os 512 bytes numa rotina so (CS ja esta baixo, CSB = 0)
        lea     MPORT,a1
        move.w  CSB,d3
        move.w  d3,d4
        ori.w   #2,d3                   ; SCK baixo, MOSI alto
        ori.w   #3,d4                   ; SCK alto,  MOSI alto
        move.w  #511,d6
rd_l:   moveq   #0,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        move.w  d3,(a0)
        move.w  d4,(a0)
        move.w  (a1),d1
        andi.w  #1,d1
        add.w   d2,d2
        or.w    d1,d2
        eori.b  #$FF,d2                 ; o 74LS240 inverte o MISO
        move.b  d2,(a2)+
        dbra    d6,rd_l
        move.w  CSB,(a0)
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

; ---------------------------------------------------------------- FAT16: montagem
; d0 = 0 ok, 1 erro de leitura, 2 nao e FAT16 suportado
fat_mount:
        move.w  #0,MOUNT
        move.l  #0,PART
        move.l  #0,SECN
        bsr     rdsec
        tst.w   d0
        bne     fm_e1
        bsr     chk55
        tst.w   d0
        bne     fm_e2
        move.b  SECBUF,d0
        cmpi.b  #$EB,d0
        beq     fm_bpb
        cmpi.b  #$E9,d0
        beq     fm_bpb
        lea     SECBUF+454,a0           ; MBR: 1a particao, LBA inicial em +8
        bsr     ld32
        move.l  d0,PART
        move.l  d0,SECN
        bsr     rdsec
        tst.w   d0
        bne     fm_e1
        bsr     chk55
        tst.w   d0
        bne     fm_e2
fm_bpb: lea     SECBUF+11,a0
        bsr     ld16
        cmpi.w  #512,d0
        bne     fm_e2
        moveq   #0,d0
        move.b  SECBUF+13,d0
        beq     fm_e2
        move.l  d0,SPC
        moveq   #0,d1
fm_l2:  lsr.w   #1,d0
        beq     fm_l2x
        addq.w  #1,d1
        bra     fm_l2
fm_l2x: move.l  d1,SPCSH
        lea     SECBUF+14,a0
        bsr     ld16
        move.l  d0,d7                   ; setores reservados
        moveq   #0,d6
        move.b  SECBUF+16,d6            ; numero de FATs
        lea     SECBUF+17,a0
        bsr     ld16
        move.l  d0,d5                   ; entradas da raiz
        lea     SECBUF+19,a0
        bsr     ld16
        move.l  d0,d4
        tst.l   d4
        bne     fm_t
        lea     SECBUF+32,a0
        bsr     ld32
        move.l  d0,d4
fm_t:   move.l  d4,TOTSEC
        lea     SECBUF+22,a0
        bsr     ld16
        move.l  d0,FATSZ
        tst.l   d0
        beq     fm_e2                   ; FAT32: nao suportado
        move.l  PART,d0
        add.l   d7,d0
        move.l  d0,FATSEC
        move.l  FATSZ,d1
        mulu    d6,d1
        add.l   d1,d0
        move.l  d0,ROOTSEC
        addi.l  #15,d5
        lsr.l   #4,d5
        move.l  d5,ROOTSZ
        add.l   d5,d0
        move.l  d0,DATASEC
        sub.l   PART,d0
        move.l  TOTSEC,d1
        sub.l   d0,d1
        move.l  SPCSH,d2
        lsr.l   d2,d1
        move.l  d1,NCLU
        cmpi.l  #4085,d1
        bcs     fm_e2
        cmpi.l  #65525,d1
        bcc     fm_e2
        lea     SECBUF+43,a0
        lea     LABEL,a1
        moveq   #10,d0
fm_lb:  move.b  (a0)+,(a1)+
        dbra    d0,fm_lb
        move.b  #0,(a1)
        move.l  #$FFFFFFFF,FATCS
        move.w  #1,MOUNT
        moveq   #0,d0
        rts
fm_e1:  moveq   #1,d0
        rts
fm_e2:  moveq   #2,d0
        rts
chk55:  moveq   #1,d0
        cmpi.b  #$55,SECBUF+510
        bne     c55_x
        cmpi.b  #$AA,SECBUF+511
        bne     c55_x
        moveq   #0,d0
c55_x:  rts

; ---------------------------------------------------------------- cadeia de clusters
; fat_next: d0 = cluster -> d0 = proximo ($FFF8..$FFFF = fim; $FFFF tambem = erro)
fat_next:
        movem.l d1-d2/a0,-(sp)
        move.l  d0,d1
        lsr.l   #8,d1
        add.l   FATSEC,d1
        cmp.l   FATCS,d1
        beq     fn_h
        bsr     fat_flush
        move.l  d1,SECN
        move.l  #FATBUF,RDST
        movem.l d0-d1,-(sp)
        bsr     sdread
        move.w  d0,d2
        movem.l (sp)+,d0-d1
        tst.w   d2
        bne     fn_err
        move.l  d1,FATCS
fn_h:   andi.l  #255,d0
        add.w   d0,d0
        lea     FATBUF,a0
        adda.w  d0,a0
        bsr     ld16
        bra     fn_x
fn_err: move.l  #$FFFFFFFF,FATCS
        move.l  #$FFFF,d0
fn_x:   movem.l (sp)+,d1-d2/a0
        rts

; cs_open: d0 = primeiro cluster (0 = diretorio raiz)
cs_open:
        move.l  d0,CS_CL
        move.l  #0,CS_IX
        rts
; cs_read: carrega o proximo setor da cadeia em SECBUF. d0 = 0 ok, 1 fim/erro
cs_read:
        move.l  CS_CL,d1
        bne     cr_f
        move.l  CS_IX,d2
        cmp.l   ROOTSZ,d2
        bcc     cr_end
        move.l  ROOTSEC,d0
        add.l   d2,d0
        addq.l  #1,CS_IX
        move.l  d0,SECN
        move.l  d0,CS_SEC
        bra     rdsec
cr_f:   cmpi.l  #2,d1
        bcs     cr_end
        cmpi.l  #$FFF8,d1
        bcc     cr_end
        subq.l  #2,d1
        move.l  SPCSH,d3
        lsl.l   d3,d1
        move.l  DATASEC,d0
        add.l   d1,d0
        add.l   CS_IX,d0
        move.l  d0,SECN
        move.l  d0,CS_SEC
        bsr     rdsec
        tst.w   d0
        bne     cr_x
        addq.l  #1,CS_IX
        move.l  CS_IX,d1
        cmp.l   SPC,d1
        bne     cr_ok
        move.l  #0,CS_IX
        move.l  CS_CL,d0
        bsr     fat_next
        move.l  d0,CS_CL
cr_ok:  moveq   #0,d0
cr_x:   rts
cr_end: moveq   #1,d0
        rts

; ---------------------------------------------------------------- nomes
; mkname: a1 = componente. Monta NAME (8.3, 11 bytes), NMOK, COMPP/COMPL. a1 avanca ate '/' ou fim.
mkname: movem.l d0-d3/a0,-(sp)
        move.l  a1,COMPP
        move.w  #1,NMOK
        lea     NAME,a0
        moveq   #10,d1
mk_f:   move.b  #32,(a0)+
        dbra    d1,mk_f
        lea     NAME,a0
        cmpi.b  #'.',(a1)
        bne     mk_n
        move.b  #'.',(a0)+
        addq.l  #1,a1
        cmpi.b  #'.',(a1)
        bne     mk_x
        move.b  #'.',(a0)
        addq.l  #1,a1
        bra     mk_x
mk_n:   moveq   #7,d2
mk_nl:  move.b  (a1),d0
        beq     mk_x
        cmpi.b  #'/',d0
        beq     mk_x
        cmpi.b  #'.',d0
        beq     mk_ex
        bsr     upper
        cmpi.b  #32,d0
        beq     mk_bad
        tst.w   d2
        bmi     mk_bad
        move.b  d0,(a0)+
        subq.w  #1,d2
        bra     mk_nx
mk_bad: move.w  #0,NMOK
mk_nx:  addq.l  #1,a1
        bra     mk_nl
mk_ex:  addq.l  #1,a1
        lea     NAME+8,a0
        moveq   #2,d2
mk_el:  move.b  (a1),d0
        beq     mk_x
        cmpi.b  #'/',d0
        beq     mk_x
        cmpi.b  #'.',d0
        beq     mk_eb
        bsr     upper
        cmpi.b  #32,d0
        beq     mk_eb
        tst.w   d2
        bmi     mk_eb
        move.b  d0,(a0)+
        subq.w  #1,d2
        bra     mk_en
mk_eb:  move.w  #0,NMOK
mk_en:  addq.l  #1,a1
        bra     mk_el
mk_x:   move.l  a1,d0
        sub.l   COMPP,d0
        move.l  d0,COMPL
        movem.l (sp)+,d0-d3/a0
        rts
upper:  cmpi.b  #'a',d0
        bcs     up_x
        cmpi.b  #'z',d0
        bhi     up_x
        subi.b  #32,d0
up_x:   rts

; lfn_collect: a0 = entrada LFN (atributo $0F). Monta o nome em LFNBUF (so o byte baixo).
lfn_collect:
        movem.l d0-d3/a0-a3,-(sp)
        move.b  (a0),d0
        btst    #6,d0
        beq     lc_n
        lea     LFNBUF,a1
        moveq   #15,d1
lc_z:   move.l  #0,(a1)+
        dbra    d1,lc_z
lc_n:   andi.w  #$1F,d0
        subq.w  #1,d0
        bmi     lc_x
        cmpi.w  #4,d0
        bcc     lc_x
        mulu    #13,d0
        lea     LFNBUF,a1
        adda.w  d0,a1
        lea     lc_tab(pc),a2
        moveq   #12,d2
lc_l:   moveq   #0,d0
        move.b  (a2)+,d0
        movea.l a0,a3
        adda.w  d0,a3
        move.b  (a3),d3
        tst.b   1(a3)
        beq     lc_c
        moveq   #63,d3                  ; '?': caractere fora do ASCII
lc_c:   cmpi.b  #$FF,d3
        bne     lc_s
        moveq   #0,d3
lc_s:   move.b  d3,(a1)+
        dbra    d2,lc_l
        move.w  #1,LFNV
lc_x:   movem.l (sp)+,d0-d3/a0-a3
        rts
lc_tab: dc.b 1,3,5,7,9,14,16,18,20,22,24,28,30
        even

; lfn_match: compara LFNBUF com o componente (COMPP/COMPL), sem distinguir maiusculas. d0 = 0 igual
lfn_match:
        movem.l d1-d3/a0-a1,-(sp)
        movea.l COMPP,a0
        lea     LFNBUF,a1
        move.l  COMPL,d1
lm_l:   tst.l   d1
        beq     lm_e
        move.b  (a0)+,d0
        bsr     upper
        move.b  d0,d2
        move.b  (a1)+,d0
        bsr     upper
        cmp.b   d0,d2
        bne     lm_ne
        subq.l  #1,d1
        bra     lm_l
lm_e:   tst.b   (a1)
        bne     lm_ne
        moveq   #0,d0
        bra     lm_x
lm_ne:  moveq   #1,d0
lm_x:   movem.l (sp)+,d1-d3/a0-a1
        rts

; ---------------------------------------------------------------- diretorios
; dir_find: d0 = cluster do diretorio (0 = raiz). Procura o componente (NAME/NMOK/COMPP).
; d0 = 0 achou (FCL, FSZ, FATT); 1 nao achou
dir_find:
        bsr     cs_open
        move.w  #0,LFNV
df_s:   bsr     cs_read
        tst.w   d0
        bne     df_nf
        lea     SECBUF,a0
        moveq   #15,d7
df_e:   move.b  (a0),d0
        beq     df_nf
        cmpi.b  #$E5,d0
        beq     df_d
        move.b  11(a0),d1
        andi.b  #$3F,d1
        cmpi.b  #$0F,d1
        bne     df_sf
        bsr     lfn_collect
        bra     df_n
df_d:   move.w  #0,LFNV
        bra     df_n
df_sf:  btst    #3,d1                   ; rotulo de volume
        bne     df_n
        tst.w   NMOK
        beq     df_l
        lea     NAME,a1
        movea.l a0,a2
        moveq   #10,d6
df_c:   move.b  (a1)+,d2
        cmp.b   (a2)+,d2
        bne     df_l
        dbra    d6,df_c
        bra     df_ok
df_l:   tst.w   LFNV
        beq     df_n2
        bsr     lfn_match
        tst.w   d0
        beq     df_ok
df_n2:  move.w  #0,LFNV
df_n:   lea     32(a0),a0
        dbra    d7,df_e
        bra     df_s
df_ok:  movea.l a0,a3
        move.l  CS_SEC,DSEC
        move.l  a3,d0
        subi.l  #SECBUF,d0
        move.w  d0,DOFF
        lea     26(a3),a0
        bsr     ld16
        move.l  d0,FCL
        lea     28(a3),a0
        bsr     ld32
        move.l  d0,FSZ
        moveq   #0,d0
        move.b  11(a3),d0
        move.l  d0,FATT
        moveq   #0,d0
        rts
df_nf:  moveq   #1,d0
        rts

; fat_open: a1 = caminho ("PASTA/ARQ.EXT"). d0 = 0 achou; 1 nao achou; 3 componente nao e pasta
fat_open:
        move.l  CWD,DCL
        cmpi.b  #'/',(a1)
        bne     fo_l
        move.l  #0,DCL
        addq.l  #1,a1
fo_l:   bsr     mkname
        move.l  a1,-(sp)
        move.l  DCL,d0
        bsr     dir_find
        movea.l (sp)+,a1
        tst.w   d0
        bne     fo_x
        cmpi.b  #'/',(a1)
        bne     fo_done
        addq.l  #1,a1
        move.l  FATT,d0
        btst    #4,d0
        beq     fo_nd
        move.l  FCL,DCL
        bra     fo_l
fo_done:
        moveq   #0,d0
fo_x:   rts
fo_nd:  moveq   #3,d0
        rts

; fat_load: arquivo aberto (FCL, FSZ) -> a0. d0 = 0 ok
fat_load:
        movea.l a0,a4
        move.l  FCL,d0
        bsr     cs_open
        move.l  FSZ,LRST
fl_l:   tst.l   LRST
        beq     fl_ok
        bsr     cs_read
        tst.w   d0
        bne     fl_err
        move.l  #512,d3
        cmp.l   LRST,d3
        bcs     fl_n
        move.l  LRST,d3
fl_n:   sub.l   d3,LRST
        lea     SECBUF,a0
        subq.w  #1,d3
fl_c:   move.b  (a0)+,(a4)+
        dbra    d3,fl_c
        bra     fl_l
fl_ok:  moveq   #0,d0
        rts
fl_err: moveq   #1,d0
        rts

; fat_free: conta os clusters livres (varre a FAT). FREEC = numero
fat_free:
        move.l  #0,FREEC
        move.l  #2,d7
ff_l:   move.l  d7,d0
        bsr     fat_next
        tst.w   d0
        bne     ff_n
        addq.l  #1,FREEC
ff_n:   addq.l  #1,d7
        move.l  NCLU,d1
        addq.l  #2,d1
        cmp.l   d1,d7
        bcs     ff_l
        rts

; dir_list: lista o diretorio DCL
dir_list:
        move.l  DCL,d0
        bsr     cs_open
        move.w  #0,LFNV
dl_s:   bsr     cs_read
        tst.w   d0
        bne     dl_x
        lea     SECBUF,a0
        moveq   #15,d7
dl_e:   move.b  (a0),d0
        beq     dl_x
        cmpi.b  #$E5,d0
        beq     dl_d
        move.b  11(a0),d1
        andi.b  #$3F,d1
        cmpi.b  #$0F,d1
        bne     dl_sf
        bsr     lfn_collect
        bra     dl_n
dl_d:   move.w  #0,LFNV
        bra     dl_n
dl_sf:  btst    #3,d1
        bne     dl_n
        bsr     pname
        btst    #4,d1
        beq     dl_f
        lea     m_dir(pc),a1
        jsr     PUTS
        bra     dl_lf
dl_f:   movea.l a0,a2
        lea     28(a2),a0
        bsr     ld32
        movea.l a2,a0
        bsr     putdec
dl_lf:  tst.w   LFNV
        beq     dl_cr
        move.b  #32,d0
        jsr     PUTC
        lea     LFNBUF,a1
        jsr     PUTS
dl_cr:  jsr     CRLF
        move.w  #0,LFNV
dl_n:   lea     32(a0),a0
        dbra    d7,dl_e
        bra     dl_s
dl_x:   rts

; pname: a0 = entrada; escreve NOME.EXT preenchido a 14 colunas. Preserva a0, d1.
pname:  movem.l d0-d3/a0-a2,-(sp)
        movea.l a0,a2
        moveq   #0,d3
        moveq   #7,d1
pn_a:   move.b  (a0)+,d0
        cmpi.b  #32,d0
        beq     pn_e
        jsr     PUTC
        addq.w  #1,d3
        dbra    d1,pn_a
pn_e:   lea     8(a2),a0
        cmpi.b  #32,(a0)
        beq     pn_p
        moveq   #46,d0
        jsr     PUTC
        addq.w  #1,d3
        moveq   #2,d1
pn_x:   move.b  (a0)+,d0
        cmpi.b  #32,d0
        beq     pn_p
        jsr     PUTC
        addq.w  #1,d3
        dbra    d1,pn_x
pn_p:   cmpi.w  #14,d3
        bcc     pn_z
        moveq   #32,d0
        jsr     PUTC
        addq.w  #1,d3
        bra     pn_p
pn_z:   movem.l (sp)+,d0-d3/a0-a2
        rts


; ======================================================================= ESCRITA (v5)
; sdwrite: grava SECN com 512 bytes de (WST). d0 = 0 ok. Preserva os demais registradores.
sdwrite:
        movem.l d1-d6/a0-a2,-(sp)
        bsr     actv
        move.l  SECN,d1
        tst.w   SDHC
        bne     wr_a
        lsl.l   #8,d1
        lsl.l   #1,d1
wr_a:   bsr     sel
        move.b  #$58,d0
        move.b  #$FF,d2
        bsr     sd_cmd
        tst.b   d0
        bne     wr_f
        move.b  #$FF,d0
        bsr     spi_xfer
        move.b  #$FE,d0
        bsr     spi_xfer
        movea.l WST,a2
        lea     LATCH,a0
        moveq   #0,d1
        moveq   #1,d3
        moveq   #2,d2
        moveq   #3,d4
        move.w  #511,d6
wr_l:   move.b  (a2)+,d0
        add.b   d0,d0
        bcs     wb0a
        move.w  d1,(a0)
        move.w  d3,(a0)
        bra     wb0b
wb0a: move.w  d2,(a0)
        move.w  d4,(a0)
wb0b:
        add.b   d0,d0
        bcs     wb1a
        move.w  d1,(a0)
        move.w  d3,(a0)
        bra     wb1b
wb1a: move.w  d2,(a0)
        move.w  d4,(a0)
wb1b:
        add.b   d0,d0
        bcs     wb2a
        move.w  d1,(a0)
        move.w  d3,(a0)
        bra     wb2b
wb2a: move.w  d2,(a0)
        move.w  d4,(a0)
wb2b:
        add.b   d0,d0
        bcs     wb3a
        move.w  d1,(a0)
        move.w  d3,(a0)
        bra     wb3b
wb3a: move.w  d2,(a0)
        move.w  d4,(a0)
wb3b:
        add.b   d0,d0
        bcs     wb4a
        move.w  d1,(a0)
        move.w  d3,(a0)
        bra     wb4b
wb4a: move.w  d2,(a0)
        move.w  d4,(a0)
wb4b:
        add.b   d0,d0
        bcs     wb5a
        move.w  d1,(a0)
        move.w  d3,(a0)
        bra     wb5b
wb5a: move.w  d2,(a0)
        move.w  d4,(a0)
wb5b:
        add.b   d0,d0
        bcs     wb6a
        move.w  d1,(a0)
        move.w  d3,(a0)
        bra     wb6b
wb6a: move.w  d2,(a0)
        move.w  d4,(a0)
wb6b:
        add.b   d0,d0
        bcs     wb7a
        move.w  d1,(a0)
        move.w  d3,(a0)
        bra     wb7b
wb7a: move.w  d2,(a0)
        move.w  d4,(a0)
wb7b:
        dbra    d6,wr_l
        move.w  CSB,(a0)
        move.b  #$FF,d0
        bsr     spi_xfer
        move.b  #$FF,d0
        bsr     spi_xfer
        move.b  #$FF,d0
        bsr     spi_xfer
        andi.b  #$1F,d0
        cmpi.b  #5,d0
        bne     wr_f
        move.l  #60000,d5
wr_b:   move.b  #$FF,d0
        bsr     spi_xfer
        cmpi.b  #$FF,d0
        beq     wr_d
        subq.l  #1,d5
        bne     wr_b
        bra     wr_f
wr_d:   bsr     desel
        movem.l (sp)+,d1-d6/a0-a2
        moveq   #0,d0
        rts
wr_f:   bsr     desel
        movem.l (sp)+,d1-d6/a0-a2
        moveq   #1,d0
        rts

; fat_flush: grava o setor de FAT em cache (nas duas copias) se estiver sujo.
fat_flush:
        tst.w   FATD
        beq     ffl_x
        movem.l d0-d1,-(sp)
        move.w  #0,FATD
        move.l  #FATBUF,WST
        move.l  FATCS,SECN
        bsr     sdwrite
        move.l  FATCS,d0
        add.l   FATSZ,d0
        move.l  d0,SECN
        bsr     sdwrite
        movem.l (sp)+,d0-d1
ffl_x:  rts

; fat_set: d0 = cluster, d1.w = valor. Devolve d0 = 0 ok. Preserva d1-d3,a0.
fat_set:
        movem.l d1-d3/a0,-(sp)
        move.l  d0,d2
        lsr.l   #8,d2
        add.l   FATSEC,d2
        cmp.l   FATCS,d2
        beq     fs_h
        bsr     fat_flush
        move.l  d2,SECN
        move.l  #FATBUF,RDST
        movem.l d0-d2,-(sp)
        bsr     sdread
        move.w  d0,d3
        movem.l (sp)+,d0-d2
        tst.w   d3
        bne     fs_err
        move.l  d2,FATCS
fs_h:   andi.l  #255,d0
        add.w   d0,d0
        lea     FATBUF,a0
        adda.w  d0,a0
        move.b  d1,(a0)
        lsr.w   #8,d1
        move.b  d1,1(a0)
        move.w  #1,FATD
        moveq   #0,d0
        bra     fs_x
fs_err: move.l  #$FFFFFFFF,FATCS
        moveq   #1,d0
fs_x:   movem.l (sp)+,d1-d3/a0
        rts

; fat_alloc: aloca um cluster livre (marcado fim de cadeia). d0 = cluster, 0 = cheio
fat_alloc:
        movem.l d1-d4,-(sp)
        move.l  NCLU,d4
        addq.l  #2,d4
        move.l  NXTFRE,d2
        cmpi.l  #2,d2
        bcc     fa_c
        moveq   #2,d2
fa_c:   cmp.l   d4,d2
        bcs     fa_s
        moveq   #2,d2
fa_s:   move.l  NCLU,d3
fa_l:   move.l  d2,d0
        bsr     fat_next
        tst.l   d0
        beq     fa_f
        addq.l  #1,d2
        cmp.l   d4,d2
        bcs     fa_n
        moveq   #2,d2
fa_n:   subq.l  #1,d3
        bne     fa_l
        moveq   #0,d0
        bra     fa_x
fa_f:   move.l  d2,d0
        move.l  #$FFFF,d1
        bsr     fat_set
        tst.l   d0
        bne     fa_e
        move.l  d2,d0
        addq.l  #1,d2
        move.l  d2,NXTFRE
        bra     fa_x
fa_e:   moveq   #0,d0
fa_x:   movem.l (sp)+,d1-d4
        rts

; fat_freechain: d0 = primeiro cluster. Libera a cadeia inteira (preserva d0).
fat_freechain:
        movem.l d0-d3,-(sp)
        move.l  d0,d2
fc_l:   cmpi.l  #2,d2
        bcs     fc_x
        cmpi.l  #$FFF8,d2
        bcc     fc_x
        move.l  d2,d0
        bsr     fat_next
        move.l  d0,d3
        move.l  d2,d0
        moveq   #0,d1
        bsr     fat_set
        move.l  d3,d2
        bra     fc_l
fc_x:   bsr     fat_flush
        move.l  #2,NXTFRE
        movem.l (sp)+,d0-d3
        rts

; dir_slot: acha entrada livre em DCL. d0 = 0 ok (DSEC, DOFF), 1 = pasta cheia
dir_slot:
        move.l  DCL,d0
        bsr     cs_open
ds_s:   bsr     cs_read
        tst.w   d0
        bne     ds_full
        lea     SECBUF,a0
        moveq   #15,d7
ds_e:   move.b  (a0),d0
        beq     ds_ok
        cmpi.b  #$E5,d0
        beq     ds_ok
        lea     32(a0),a0
        dbra    d7,ds_e
        bra     ds_s
ds_ok:  move.l  CS_SEC,DSEC
        move.l  a0,d0
        subi.l  #SECBUF,d0
        move.w  d0,DOFF
        moveq   #0,d0
        rts
ds_full:
        moveq   #1,d0
        rts

; put_dent: a0 = entrada de 32 bytes. Usa WNAME, WFIRST, WSIZE, DDATE, DTIME.
put_dent:
        movem.l d0-d1/a0-a1,-(sp)
        lea     WNAME,a1
        moveq   #10,d1
pd_n:   move.b  (a1)+,(a0)+
        dbra    d1,pd_n
        move.b  #$20,(a0)+              ; atributo: arquivo
        moveq   #19,d1
pd_z:   move.b  #0,(a0)+                ; +12..+31 zerados
        dbra    d1,pd_z
        movea.l 8(sp),a0                ; a0 original (3o registrador salvo)
        move.w  DTIME,d0
        move.b  d0,14(a0)
        move.b  d0,22(a0)
        lsr.w   #8,d0
        move.b  d0,15(a0)
        move.b  d0,23(a0)
        move.w  DDATE,d0
        move.b  d0,16(a0)
        move.b  d0,18(a0)
        move.b  d0,24(a0)
        lsr.w   #8,d0
        move.b  d0,17(a0)
        move.b  d0,19(a0)
        move.b  d0,25(a0)
        move.l  WFIRST,d0
        move.b  d0,26(a0)
        lsr.w   #8,d0
        move.b  d0,27(a0)
        move.l  WSIZE,d0
        move.b  d0,28(a0)
        lsr.l   #8,d0
        move.b  d0,29(a0)
        lsr.l   #8,d0
        move.b  d0,30(a0)
        lsr.l   #8,d0
        move.b  d0,31(a0)
        movem.l (sp)+,d0-d1/a0-a1
        rts

; fw_create: a1 = caminho. Cria (ou zera) o arquivo e deixa-o aberto para escrita.
; d0 = 0 ok; 1 nome/caminho invalido (use 8.3); 2 pasta cheia; 3 erro de cartao; 4 e pasta; 5 nao montado
fw_create:
        tst.w   MOUNT
        beq     fcr_nm
        move.l  CWD,DCL
        cmpi.b  #'/',(a1)
        bne     fcr_l
        move.l  #0,DCL
        addq.l  #1,a1
fcr_l:  bsr     mkname
        move.l  a1,-(sp)
        move.l  DCL,d0
        bsr     dir_find
        movea.l (sp)+,a1
        tst.w   d0
        bne     fcr_nf
        cmpi.b  #'/',(a1)
        bne     fcr_fin
        addq.l  #1,a1
        move.l  FATT,d0
        btst    #4,d0
        beq     fcr_bad
        move.l  FCL,DCL
        bra     fcr_l
fcr_nf: cmpi.b  #'/',(a1)
        beq     fcr_bad
        tst.w   NMOK
        beq     fcr_bad
        tst.b   (a1)
        bne     fcr_bad
        bsr     dir_slot
        tst.w   d0
        bne     fcr_full
        lea     NAME,a0
        lea     WNAME,a1
        moveq   #10,d1
fcr_c0: move.b  (a0)+,(a1)+
        dbra    d1,fcr_c0
        bra     fcr_go
fcr_fin:
        move.l  FATT,d0
        btst    #4,d0
        bne     fcr_isd
        lea     SECBUF,a0               ; SECBUF ainda guarda o setor do diretorio
        move.w  DOFF,d0
        adda.w  d0,a0
        lea     WNAME,a1
        moveq   #10,d1
fcr_c1: move.b  (a0)+,(a1)+
        dbra    d1,fcr_c1
        move.l  FCL,d0
        bsr     fat_freechain           ; sobrescreve: libera os clusters antigos
fcr_go: move.l  #0,WCL
        move.l  #0,WIX
        move.w  #0,WPOS
        move.l  #0,WSIZE
        move.l  #0,WFIRST
        move.l  DSEC,WDSEC
        move.w  DOFF,WDOFF
        move.l  DSEC,SECN
        bsr     rdsec
        tst.w   d0
        bne     fcr_io
        lea     SECBUF,a0
        move.w  DOFF,d0
        adda.w  d0,a0
        bsr     put_dent
        move.l  #SECBUF,WST
        move.l  DSEC,SECN
        bsr     sdwrite
        tst.w   d0
        bne     fcr_io
        moveq   #0,d0
        rts
fcr_nm: moveq   #5,d0
        rts
fcr_bad:
        moveq   #1,d0
        rts
fcr_full:
        moveq   #2,d0
        rts
fcr_io: moveq   #3,d0
        rts
fcr_isd:
        moveq   #4,d0
        rts

; fw_flush: grava WBUF (WPOS bytes, completado com zeros) como proximo setor do arquivo. d0 = 0 ok
fw_flush:
        movem.l d1-d4/a0,-(sp)
        move.w  WPOS,d2
        andi.l  #$FFFF,d2
        lea     WBUF,a0
        adda.l  d2,a0
fwf_p:  cmpi.w  #512,d2
        bcc     fwf_c
        move.b  #0,(a0)+
        addq.w  #1,d2
        bra     fwf_p
fwf_c:  move.l  WCL,d0
        beq     fwf_new
        move.l  WIX,d1
        cmp.l   SPC,d1
        bne     fwf_have
fwf_new:
        bsr     fat_alloc
        tst.l   d0
        beq     fwf_full
        move.l  d0,d3
        move.l  WCL,d0
        beq     fwf_first
        move.l  d3,d1
        bsr     fat_set
        bra     fwf_n2
fwf_first:
        move.l  d3,WFIRST
fwf_n2: move.l  d3,WCL
        move.l  #0,WIX
fwf_have:
        move.l  WCL,d0
        subq.l  #2,d0
        move.l  SPCSH,d1
        lsl.l   d1,d0
        add.l   DATASEC,d0
        add.l   WIX,d0
        move.l  d0,SECN
        move.l  #WBUF,WST
        bsr     sdwrite
        tst.w   d0
        bne     fwf_e
        addq.l  #1,WIX
        move.w  #0,WPOS
        moveq   #0,d0
        bra     fwf_x
fwf_full:
        moveq   #2,d0
        bra     fwf_x
fwf_e:  moveq   #3,d0
fwf_x:  movem.l (sp)+,d1-d4/a0
        rts

; fw_write: a0 = origem, d1 = bytes. d0 = 0 ok; 2 = cartao cheio; 3 = erro
fw_write:
        movem.l d1-d3/a0-a2,-(sp)
        move.l  d1,d3
        movea.l a0,a2
fww_l:  tst.l   d3
        beq     fww_ok
        move.w  WPOS,d0
        andi.l  #$FFFF,d0
        lea     WBUF,a0
        adda.l  d0,a0
        move.b  (a2)+,(a0)
        addq.w  #1,WPOS
        addq.l  #1,WSIZE
        subq.l  #1,d3
        cmpi.w  #512,WPOS
        bne     fww_l
        bsr     fw_flush
        tst.w   d0
        beq     fww_l
        bra     fww_x
fww_ok: moveq   #0,d0
fww_x:  movem.l (sp)+,d1-d3/a0-a2
        rts

; fw_close: grava o resto, descarrega a FAT e atualiza a entrada de diretorio. d0 = 0 ok
fw_close:
        tst.w   WPOS
        beq     fwc_d
        bsr     fw_flush
        tst.w   d0
        bne     fwc_x
fwc_d:  bsr     fat_flush
        move.l  WDSEC,SECN
        bsr     rdsec
        tst.w   d0
        bne     fwc_e
        lea     SECBUF,a0
        move.w  WDOFF,d0
        adda.w  d0,a0
        bsr     put_dent
        move.l  #SECBUF,WST
        move.l  WDSEC,SECN
        bsr     sdwrite
        tst.w   d0
        bne     fwc_e
        moveq   #0,d0
        rts
fwc_e:  moveq   #3,d0
fwc_x:  rts

; fw_delete: a1 = caminho. d0 = 0 ok; 1 nao achou; 3 erro; 4 e pasta
fw_delete:
        bsr     fat_open
        tst.w   d0
        bne     fwd_x
        move.l  FATT,d0
        btst    #4,d0
        bne     fwd_d
        move.l  FCL,d0
        bsr     fat_freechain
        move.l  DSEC,SECN
        bsr     rdsec
        tst.w   d0
        bne     fwd_e
        lea     SECBUF,a0
        move.w  DOFF,d0
        adda.w  d0,a0
        move.b  #$E5,(a0)
        move.l  #SECBUF,WST
        move.l  DSEC,SECN
        bsr     sdwrite
        tst.w   d0
        bne     fwd_e
        moveq   #0,d0
        rts
fwd_x:  rts
fwd_d:  moveq   #4,d0
        rts
fwd_e:  moveq   #3,d0
        rts

; ---- W arquivo endHex lenHex : grava memoria em arquivo
c_save: bsr     skipsp
        movea.l a1,a3
        movea.l a1,a2
cs_e:   tst.b   (a2)+
        bne     cs_e
        subq.l  #1,a2
        bsr     lasttok
        beq     cs_bad
        movea.l a2,a1
        subq.l  #1,a2
        move.l  a2,-(sp)
        jsr     GETHEX
        movea.l (sp)+,a2
        tst.w   d1
        beq     cs_bad
        move.l  d0,SAVL
        bsr     lasttok
        beq     cs_bad
        movea.l a2,a1
        jsr     GETHEX
        tst.w   d1
        beq     cs_bad
        move.l  d0,SAVA
        movea.l a3,a1
        bsr     fw_create
        tst.w   d0
        bne     cs_err
        movea.l SAVA,a0
        move.l  SAVL,d1
        bsr     fw_write
        tst.w   d0
        bne     cs_err
        bsr     fw_close
        tst.w   d0
        bne     cs_err
        lea     m_gr(pc),a1
        jsr     PUTS
        move.l  SAVL,d0
        bsr     putdec
        lea     m_gr2(pc),a1
        jsr     PUTS
        bra     main
cs_bad: lea     m_usew(pc),a1
        jsr     PUTS
        bra     main
cs_err: move.w  d0,d7
        lea     m_werr(pc),a1
        jsr     PUTS
        move.w  d7,d0
        add.b   #'0',d0
        jsr     PUTC
        jsr     CRLF
        bra     main

; lasttok: a2 = fim da linha (no 0), a3 = inicio. Isola o ultimo item: a2 = inicio dele, o separador vira 0.
; Z=1 se nao ha mais separador (nada a isolar).
lasttok:
lt_l:   cmpa.l  a3,a2
        beq     lt_no
        subq.l  #1,a2
        cmpi.b  #32,(a2)
        bne     lt_l
        move.b  #0,(a2)
        addq.l  #1,a2
        moveq   #1,d0
        rts
lt_no:  moveq   #0,d0
        rts

; ---- K arquivo : apaga
c_kill: bsr     skipsp
        bsr     fw_delete
        tst.w   d0
        beq     ck_ok
        cmpi.w  #1,d0
        bne     cs_err
        bra     c_nf
ck_ok:  lea     m_ap(pc),a1
        jsr     PUTS
        bra     main

; ---- C pasta : muda a pasta atual ("/" = raiz)
c_cd:   bsr     skipsp
        cmpi.b  #'/',(a1)
        bne     cc_r
        tst.b   1(a1)
        bne     cc_r
        move.l  #0,CWD
        bra     main
cc_r:   bsr     fat_open
        tst.w   d0
        bne     c_nf
        move.l  FATT,d0
        btst    #4,d0
        beq     c_nd
        move.l  FCL,CWD
        bra     main

m_gr:   dc.b "Gravados ",0
m_gr2:  dc.b " bytes.",13,10,0
m_usew: dc.b "Uso: W caminho enderecoHex tamanhoHex",13,10,0
m_werr: dc.b "ERRO de gravacao (1 nome/caminho, 2 cheio, 3 cartao, 4 pasta, 5 nao montado): ",0
m_ap:   dc.b "Apagado.",13,10,0
        even

t_b0:    dc.b "PARAGON 50  FATSH v4 ",0
l_sd:    dc.b "SD: ",0
l_sdno:  dc.b "SD: sem cartao",0
l_nofat: dc.b "SD: sem FAT16",0
l_mb:    dc.b " MB FAT16 ",0
l_kcl:   dc.b "K/cl",0
l_sdsc:  dc.b "Cartao SD padrao",0
l_sdhc:  dc.b "Cartao SDHC/SDXC",0
l_liv:   dc.b "Livre: ",0
l_mbl:   dc.b " MB",0
m_title: dc.b 13,10,"FATSH v8 - FAT16 leitura/escrita + gravador de bancos - PARAGON 50",13,10
         dc.b "Comandos: I D T L S W K C F ? Q",13,10,0
m_prompt: dc.b "FAT> ",0
m_help:  dc.b "I inicia/monta  D [pasta] lista  T arq mostra texto  L arq endHex carrega  S espaco  W arq endHex lenHex grava  K arq apaga  C pasta muda  F banco arq grava banco 1-7  Q sai",13,10,0
m_nf:    dc.b "Nao encontrado.",13,10,0
m_nd:    dc.b "Nao e uma pasta.",13,10,0
m_isdir: dc.b "E uma pasta.",13,10,0
m_rerr:  dc.b "ERRO de leitura do cartao.",13,10,0
m_nofat: dc.b "Cartao sem FAT16 suportado (nem boot sector nem MBR+FAT16).",13,10,0
m_fail:  dc.b "FALHA ao inicializar o cartao (encaixe, fiacao, 3,3 V).",13,10,0
m_nomnt: dc.b "Cartao nao montado (use I).",13,10,0
s_pros:  dc.b "PROSSIGA",0
m_flq:   dc.b "Gravar no banco? Digite PROSSIGA (apaga o banco!); outra coisa = so comparar: ",0
m_flw:   dc.b 13,10,"Modo GRAVAR.",13,10,0
m_flc:   dc.b 13,10,"Modo COMPARAR (nada sera alterado).",13,10,0
m_fuse:  dc.b "Uso: F banco(1-7) arquivo   (imagem de 128 KB com cabecalho AB)",13,10,0
m_fb0:   dc.b "O banco 0 nao pode ser gravado por aqui.",13,10,0
m_fsz:   dc.b "O arquivo precisa ter exatamente 131072 bytes (128 KB).",13,10,0
m_use:   dc.b "Uso: L caminho enderecoHex",13,10,0
m_vol:   dc.b "Volume: ",0
m_fs:    dc.b "  FAT16  ",0
m_mb:    dc.b " MB, cluster ",0
m_kcl:   dc.b " KB",13,10,0
m_dir:   dc.b "<DIR>",0
m_ld:    dc.b "Carregados ",0
m_ld2:   dc.b " bytes em $",0
m_tot:   dc.b "Total: ",0
m_liv:   dc.b "   Livre: ",0
m_usa:   dc.b "   Usado: ",0
m_kb:    dc.b " KB",0
         even
