; ==========================================================================
;  FATSH v1 - leitor FAT16 (SOMENTE LEITURA) + driver SD para o PARAGON 50
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
CSB     equ $3510
SDHC    equ $3512
HCSARG  equ $3514
SARG    equ $3518
SCRC    equ $351C
SECN    equ $351E
CSD     equ $3530
RDST    equ $3550
; ---- RAM do FAT
FATSEC  equ $3400
ROOTSEC equ $3404
ROOTSZ  equ $3408
DATASEC equ $340C
SPC     equ $3410
SPCSH   equ $3414
NCLU    equ $3418
PART    equ $341C
TOTSEC  equ $3420
FATSZ   equ $3424
FATCS   equ $3428
MOUNT   equ $342C
LABEL   equ $3430             ; 12 bytes
CS_CL   equ $3440
CS_IX   equ $3444
FCL     equ $3448
FSZ     equ $344C
FATT    equ $3450
DCL     equ $3454
LRST    equ $3458
COMPP   equ $345C
COMPL   equ $3460
NMOK    equ $3464
LFNV    equ $3466
NAME    equ $3468             ; 12 bytes
DECBUF  equ $3478             ; 12 bytes
FREEC   equ $3484
LADDR   equ $3488
LFNBUF  equ $3490             ; 64 bytes
SECBUF  equ $4000
FATBUF  equ $4200

        org $2000
start:  lea     m_title(pc),a1
        jsr     PUTS
        bsr     do_init
main:   lea     m_prompt(pc),a1
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
        lea     m_help(pc),a1
        jsr     PUTS
        bra     main
quit:   rts
c_init: bsr     do_init
        bra     main

; ---- D [pasta]
c_dir:  bsr     skipsp
        move.l  #0,DCL
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
        bra     main
c_nomnt:
        lea     m_nomnt(pc),a1
        jsr     PUTS
        bra     main

; ---------------------------------------------------------------- inicia + monta
do_init:
        bsr     sdinit
        tst.w   d0
        bne     di_x
        bsr     fat_mount
        tst.w   d0
        beq     di_ok
        cmpi.w  #1,d0
        beq     di_e1
        lea     m_nofat(pc),a1
        jsr     PUTS
        rts
di_e1:  lea     m_rerr(pc),a1
        jsr     PUTS
        rts
di_ok:  lea     m_vol(pc),a1
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
        jsr     PUTS
        movem.l (sp)+,d0-d3/a0-a1
        rts

; ---------------------------------------------------------------- SPI (modo 0)
spi_xfer:
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
sdread: move.l  SECN,d1
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
        move.l  #0,DCL
        cmpi.b  #'/',(a1)
        bne     fo_l
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

m_title: dc.b 13,10,"FATSH v1 - leitor FAT16 (so leitura) - PARAGON 50",13,10
         dc.b "Comandos: I D [pasta] T arq L arq endHex S ? Q",13,10,0
m_prompt: dc.b "FAT> ",0
m_help:  dc.b "I inicia/monta  D [pasta] lista  T arq mostra texto  L arq endHex carrega  S espaco  Q sai",13,10,0
m_nf:    dc.b "Nao encontrado.",13,10,0
m_nd:    dc.b "Nao e uma pasta.",13,10,0
m_isdir: dc.b "E uma pasta.",13,10,0
m_rerr:  dc.b "ERRO de leitura do cartao.",13,10,0
m_nofat: dc.b "Cartao sem FAT16 suportado (nem boot sector nem MBR+FAT16).",13,10,0
m_fail:  dc.b "FALHA ao inicializar o cartao (encaixe, fiacao, 3,3 V).",13,10,0
m_nomnt: dc.b "Cartao nao montado (use I).",13,10,0
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
