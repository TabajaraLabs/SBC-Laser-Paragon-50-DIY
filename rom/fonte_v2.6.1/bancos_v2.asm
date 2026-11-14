; bancos_v1.asm - menu de bancos da flash (cabecalho "AB") + estatistica do comando L
; Monta em $F833F8 (area livre da ROM v2.3.1, ate $F83FFF). Usa so a tabela de servicos fixa do monitor.
; Entradas (tabela no inicio):  $F833F8 BKMENU (nao volta: boot de banco ou RESET)   $F833FE LSTAT (rts)
; Cabecalho de banco (64 bytes em $F807C0, big-endian): 'AB' | tipo | inicio | fim | partida | nome[16] | versao[8] | CRC32
; Rotinas que trocam de banco rodam na RAM ($2000...), porque a troca muda toda a janela $F80000-$F9FFFF.

PUTC    equ $F80800
GETC    equ $F80806
GETHEX  equ $F80830
GETLINE equ $F80836
RESTART equ $F8083C
BUF     equ $0500
FLBANK  equ $301C
FLBCONF equ $301E
FLSTUB  equ $27F0
PUTS    equ $F8080C
HEXB    equ $F80812
HEXL    equ $F8081E
CRLF    equ $F80824
STROBE  equ $F8082A
RESETV  equ $F80900
BANKR   equ $FC0000
LSTART  equ $0434
LSIZE   equ $0438

RAMRT   equ $2000          ; copia da rotina de troca de banco (rc_ini..rc_fim)
HDRS    equ $2100          ; 8 cabecalhos x 64 bytes ($2100-$22FF)
CRCT    equ $2300          ; tabela CRC32 (1 KB)
CHK     equ $2700          ; buffer de 4 KB para verificar o CRC
SCR     equ $26F0          ; rascunho (SP de ROM completa)
HDR_OFF equ $7C0
CHUNK   equ $1000

        org $F833F8
        jmp bk_menu                      ; +0
        jmp lstat                        ; +6
        jmp flchk                        ; +12 ($F83404)

; ---- LSTAT: " inicio=XXXXXXXX tamanho=XXXXXXXX bytes" -----------------------
lstat:  movem.l d0/a1,-(sp)
        lea     s_ini(pc),a1
        jsr     PUTS
        move.l  LSTART,d0
        jsr     HEXL
        lea     s_tam(pc),a1
        jsr     PUTS
        move.l  LSIZE,d0
        jsr     HEXL
        lea     s_byt(pc),a1
        jsr     PUTS
        movem.l (sp)+,d0/a1
        rts

; ---- rotinas que vao para a RAM (posicao independente) ----------------------
; rc_copy: d0.w = banco, a0 = origem (ROM), a1 = destino (RAM), d1.w = palavras-1. Volta ao banco 0.
; rc_boot: d0.w = banco, d1.l = SP, a0 = entrada: seleciona o banco e salta (nao volta).
rc_ini:
        move.w  d0,BANKR
rc_l:   move.w  (a0)+,(a1)+
        dbra    d1,rc_l
        move.w  #0,BANKR
        rts
rc_boot:
        move.w  d0,BANKR
        movea.l d1,sp
        jmp     (a0)
rc_fim:
RC_BOOT equ RAMRT+(rc_boot-rc_ini)

; ---- utilitarios ---------------------------------------------------------------
; bcopy: d0 = banco, a0 = origem ROM, a1 = destino RAM, d1 = bytes (par, 2..65534). Preserva d0-d7/a0-a1.
bcopy:  movem.l d0-d2/a0-a1,-(sp)
        lsr.w   #1,d1
        subq.w  #1,d1
        jsr     RAMRT
        movem.l (sp)+,d0-d2/a0-a1
        rts

; pstr: a1 = texto 0-terminado
pstr:   jsr     PUTS
        rts

; ptxt: imprime d1 bytes de (a0) trocando nao-imprimivel por espaco; a0 avanca
ptxt:   movem.l d0-d1,-(sp)
        subq.w  #1,d1
pt_l:   move.b  (a0)+,d0
        cmpi.b  #32,d0
        blo     pt_s
        cmpi.b  #126,d0
        bls     pt_o
pt_s:   moveq   #32,d0
pt_o:   jsr     PUTC
        dbra    d1,pt_l
        movem.l (sp)+,d0-d1
        rts

; ---- menu ------------------------------------------------------------------------
bk_menu:
        move.w  #$2700,sr
        movea.l #$1F00,sp
        lea     rc_ini(pc),a0            ; instala a rotina de troca de banco na RAM
        lea     RAMRT,a1
        move.w  #(rc_fim-rc_ini)/2-1,d1
bm_i:   move.w  (a0)+,(a1)+
        dbra    d1,bm_i
        moveq   #0,d2                    ; le os 8 cabecalhos
bm_r:   move.w  d2,d0
        lea     $F807C0,a0
        move.l  d2,d3
        lsl.w   #6,d3
        lea     HDRS,a1
        adda.w  d3,a1
        moveq   #64,d1
        bsr     bcopy
        addq.w  #1,d2
        cmpi.w  #8,d2
        blo     bm_r
        lea     s_tit(pc),a1
        bsr     pstr
        moveq   #0,d2                    ; lista
bm_l:   lea     s_sp2(pc),a1
        bsr     pstr
        move.w  d2,d0
        addi.b  #'0',d0
        jsr     PUTC
        lea     s_sp2(pc),a1
        bsr     pstr
        move.l  d2,d3
        lsl.w   #6,d3
        lea     HDRS,a0
        adda.w  d3,a0
        cmpi.w  #$4142,(a0)              ; 'AB'
        bne     bm_na
        movea.l a0,a3                    ; a3 = cabecalho
        lea     16(a3),a0
        moveq   #16,d1
        bsr     ptxt
        lea     s_sp1(pc),a1
        bsr     pstr
        lea     32(a3),a0
        moveq   #8,d1
        bsr     ptxt
        lea     s_sp1(pc),a1
        bsr     pstr
        lea     s_rom(pc),a1
        cmpi.w  #0,2(a3)
        beq     bm_t
        lea     s_app(pc),a1
        cmpi.w  #1,2(a3)
        beq     bm_t
        lea     s_int(pc),a1
bm_t:   bsr     pstr
        lea     s_fim(pc),a1
        bsr     pstr
        move.l  8(a3),d0
        jsr     HEXL
        bra     bm_nx
bm_na:  cmpi.w  #$FFFF,(a0)
        bne     bm_ns
        lea     s_vaz(pc),a1
        bra     bm_pp
bm_ns:  lea     s_sem(pc),a1
bm_pp:  bsr     pstr
bm_nx:  jsr     CRLF
        addq.w  #1,d2
        cmpi.w  #8,d2
        blo     bm_l
bm_ask: lea     s_ask(pc),a1
        bsr     pstr
bm_k:   jsr     GETC
        cmpi.b  #'0',d0
        blo     bm_k0
        cmpi.b  #'7',d0
        bhi     bm_k0
        move.b  d0,d4
        jsr     PUTC
        jsr     CRLF
        andi.w  #$F,d4
        beq     bm_rst                   ; 0 = menu principal
        bra     bm_sel
bm_k0:  andi.b  #$DF,d0                  ; maiuscula
        cmpi.b  #'M',d0
        beq     bm_rst
        cmpi.b  #27,d0
        beq     bm_rst
        bra     bm_k
bm_rst: jmp     RESETV

; ---- seleciona o banco d4 -----------------------------------------------------------------
bm_sel: move.w  d4,d3
        lsl.w   #6,d3
        lea     HDRS,a3
        adda.w  d3,a3                    ; a3 = cabecalho do banco d4
        cmpi.w  #$4142,(a3)
        beq     bs_ok
        lea     s_nohdr(pc),a1
        bsr     pstr
        bra     bm_ask
bs_ok:  move.l  4(a3),d0                 ; inicio deve ser $F80000, fim dentro de $F80000-$F9FFFF
        cmpi.l  #$F80000,d0
        bne     bs_bad
        move.l  8(a3),d0
        cmpi.l  #$F9FFFF,d0
        bhi     bs_bad
        cmpi.l  #$F807FF,d0
        bhi     bs_crc
bs_bad: lea     s_badh(pc),a1
        bsr     pstr
        bra     bm_ask
; --- CRC32 (reflexo, poly $EDB88320) sobre [inicio..$F807BF]+[$F80800..fim] ------------------
bs_crc: lea     s_ver(pc),a1
        bsr     pstr
        lea     CRCT,a0                  ; tabela
        moveq   #0,d2
bt_i:   move.l  d2,d0
        moveq   #7,d1
bt_b:   lsr.l   #1,d0
        bcc     bt_n
        eori.l  #$EDB88320,d0
bt_n:   dbra    d1,bt_b
        move.l  d0,(a0)+
        addq.w  #1,d2
        cmpi.w  #256,d2
        blo     bt_i
        moveq   #-1,d6                   ; d6 = CRC corrente
        move.l  8(a3),d7
        subi.l  #$F80000-1,d7            ; d7 = bytes totais a ler (fim-inicio+1)
        moveq   #0,d5                    ; d5 = deslocamento do bloco
bc_blk: move.l  d7,d3
        sub.l   d5,d3                    ; restante
        ble     bc_done
        cmpi.l  #CHUNK,d3
        bls     bc_n
        move.l  #CHUNK,d3
bc_n:   move.l  d3,d1
        addq.l  #1,d1
        andi.w  #$FFFE,d1                ; bytes lidos (par)
        move.w  d4,d0
        movea.l #$F80000,a0
        adda.l  d5,a0
        lea     CHK,a1
        bsr     bcopy
        jsr     STROBE
        move.b  #'.',d0
        jsr     PUTC
        lea     CHK,a0                   ; a0 = ponteiro, d3 = bytes uteis
        move.l  d5,d0                    ; deslocamento absoluto do primeiro byte
        move.l  d3,d1                    ; d1 = contador
        subq.l  #1,d1
bc_by:  cmpi.l  #HDR_OFF,d0              ; pula $7C0-$7FF
        blo     bc_do
        cmpi.l  #HDR_OFF+64,d0
        blo     bc_sk
bc_do:  moveq   #0,d2
        move.b  (a0),d2
        eor.b   d6,d2
        lsl.w   #2,d2
        lsr.l   #8,d6
        lea     CRCT,a2
        adda.w  d2,a2
        move.l  (a2),d2
        eor.l   d2,d6
bc_sk:  addq.l  #1,a0
        addq.l  #1,d0
        dbra    d1,bc_by
        add.l   d3,d5
        bra     bc_blk
bc_done:
        not.l   d6
        jsr     CRLF
        cmp.l   40(a3),d6
        beq     bc_ok
        lea     s_cbad(pc),a1
        bsr     pstr
bc_q:   jsr     GETC
        andi.b  #$DF,d0
        cmpi.b  #'S',d0
        beq     bc_go
        cmpi.b  #'N',d0
        bne     bc_q
        jsr     CRLF
        bra     bm_ask
bc_ok:  lea     s_cok(pc),a1
        bsr     pstr
bc_go:  lea     s_boot(pc),a1
        bsr     pstr
        movea.l 12(a3),a4                ; partida
        move.l  #$1F00,d6                ; SP padrao (aplicativo)
        tst.w   2(a3)
        bne     bg_go
        move.w  d4,d0                    ; ROM completa: SP vem do vetor 0 do banco
        movea.l #$F80000,a0
        lea     SCR,a1
        moveq   #4,d1
        bsr     bcopy
        move.l  SCR,d6
bg_go:  move.w  d4,d0
        move.l  d6,d1
        movea.l a4,a0
        jmp     RC_BOOT


; ===================== comando FLASH [banco] (v2.5) ==========================
; Reconhece "FLASH" no inicio da linha (a1 aponta o texto, sem espacos iniciais). Se nao for, volta com a1 intacto.
; Se for: copia o gravador flash_v2 (2 pedacos na ROM) para a RAM $2000, pergunta PROSSIGA e executa.
flchk:  movem.l d0-d1/a0/a2,-(sp)
        movea.l a1,a2
        lea     s_flash(pc),a0
fc_l:   move.b  (a0)+,d0
        beq     fc_end
        move.b  (a2)+,d1
        cmpi.b  #'a',d1
        blo     fc_c
        cmpi.b  #'z',d1
        bhi     fc_c
        subi.b  #32,d1
fc_c:   cmp.b   d0,d1
        beq     fc_l
fc_no:  movem.l (sp)+,d0-d1/a0/a2
        rts
fc_end: move.b  (a2),d1
        beq     fc_yes
        cmpi.b  #' ',d1
        bne     fc_no
fc_yes:                                  ; nao volta: a pilha e refeita em fl_go
        movea.l a2,a1
        moveq   #1,d4                    ; banco padrao = 1 (o banco 0 so por pedido explicito)
fl_sp:  cmpi.b  #' ',(a1)
        bne     fl_a
        addq.l  #1,a1
        bra     fl_sp
fl_a:   tst.b   (a1)
        beq     fl_go
        jsr     GETHEX
        tst.w   d1
        beq     fl_bad
        cmpi.l  #7,d0
        bhi     fl_bad
        move.w  d0,d4
fl_go:  move.w  #$2700,sr
        movea.l #$1F00,sp
        lea     s_fl1(pc),a1
        jsr     PUTS
        move.w  d4,d0
        addi.b  #'0',d0
        jsr     PUTC
        jsr     CRLF
        lea     FL_IMG1(pc),a0           ; copia o gravador para $2000
        lea     $2000,a1
        move.w  #FL_LEN1-1,d1
fl_c1:  move.b  (a0)+,(a1)+
        dbra    d1,fl_c1
        lea     FL_IMG2,a0
        move.w  #FL_LEN2-1,d1
fl_c2:  move.b  (a0)+,(a1)+
        dbra    d1,fl_c2
        lea     $3000,a0                 ; zera as variaveis do gravador ($3000-$301F)
        moveq   #7,d1
fl_z:   clr.l   (a0)+
        dbra    d1,fl_z
        move.w  d4,FLBANK
        lea     fs_ini(pc),a0            ; rotina de retorno na RAM (o banco 0 pode ter sido regravado)
        lea     FLSTUB,a1
        moveq   #(fs_fim-fs_ini)/2-1,d1
fl_s:   move.w  (a0)+,(a1)+
        dbra    d1,fl_s
        lea     s_fl2(pc),a1
        jsr     PUTS
        jsr     GETLINE
        lea     BUF,a0
        lea     s_pros(pc),a1
fl_p:   move.b  (a1)+,d0
        beq     fl_pe
        cmp.b   (a0)+,d0
        bne     fl_cmp
        bra     fl_p
fl_pe:  tst.b   (a0)
        bne     fl_cmp
        move.w  #1,$3000                 ; MODE = gravar
        move.w  #$A55A,$3002             ; CONF
        tst.w   d4
        bne     fl_wr
        move.w  #$0BA0,FLBCONF           ; banco 0 confirmado
fl_wr:  lea     s_flw(pc),a1
        bra     fl_run
fl_cmp: lea     s_flc(pc),a1
fl_run: jsr     PUTS
        move.l  #FLSTUB,-(sp)
        jmp     $2000                    ; o gravador termina com RTS -> FLSTUB
fl_bad: lea     s_flbad(pc),a1
        jsr     PUTS
        jmp     RESTART

fs_ini: tst.w   $301C
        bne.s   fs_m
        jmp     RESETV                   ; gravou o banco 0: o monitor antigo sumiu, reinicia
fs_m:   jmp     RESTART
fs_fim:

s_flash: dc.b "FLASH",0
s_pros: dc.b "PROSSIGA",0
s_fl1:  dc.b 13,10,"Gravador de flash (flash_v2) - banco de destino ",0
s_fl2:  dc.b "Normalmente isto so COMPARA. Se voce REALMENTE quer atualizar a flash e sabe o que esta fazendo,",13,10
        dc.b "digite PROSSIGA (em maiusculas); qualquer outra coisa = so comparar: ",0
s_flw:  dc.b 13,10,"Modo GRAVAR (apaga e grava o banco). Envie agora a imagem de 128 KB (#sendbin arquivo 256).",13,10,0
s_flc:  dc.b 13,10,"Modo COMPARAR (a flash nao e alterada). Envie agora a imagem de 128 KB (#sendbin arquivo 256).",13,10,0
s_flbad: dc.b 13,10,"?? uso: FLASH [banco 0-7]  (padrao 1; o banco 0 e o de boot)",13,10,0

s_tit:  dc.b 13,10,"Bancos da flash (cabecalho AB em $F807C0):",13,10
        dc.b "  N  NOME             VERSAO   TIPO  FIM",13,10,0
s_sp2:  dc.b "  ",0
s_sp1:  dc.b " ",0
s_rom:  dc.b "ROM  ",0
s_app:  dc.b "APP  ",0
s_int:  dc.b "?    ",0
s_fim:  dc.b "$",0
s_vaz:  dc.b "(vazio)",0
s_sem:  dc.b "(sem cabecalho AB)",0
s_ask:  dc.b "Banco 1-7 para iniciar, 0 ou M = menu principal: ",0
s_nohdr: dc.b "Esse banco nao tem cabecalho AB.",13,10,0
s_badh: dc.b "Cabecalho invalido (inicio/fim).",13,10,0
s_ver:  dc.b "Verificando CRC32 ",0
s_cok:  dc.b "CRC OK.",13,10,0
s_cbad: dc.b "CRC DIFERENTE do cabecalho! Iniciar mesmo assim? (S/N) ",0
s_boot: dc.b "Iniciando... (RESET volta ao banco 0)",13,10,0
s_ini:  dc.b " inicio=",0
s_tam:  dc.b " tamanho=",0
s_byt:  dc.b " bytes",0
        dc.b 0
