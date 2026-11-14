; ==========================================================================
;  FLASH.ASM v5c - apaga e grava UM BANCO das duas Am29F040B - PARAGON 50
;  v4 (14/11/2026): RECEBE A IMAGEM INTEIRA NA RAM ($40000-$5FFFF), CONFERE O CRC32 e SO ENTAO apaga e grava.
;  Uma transferencia com erro (byte a mais, byte perdido, banco errado) e RECUSADA e NADA e apagado.
;  Arquivo a enviar: imagem de 128 KB + 256 bytes de rodape ("FL4", banco, CRC32), feito por mkfl4.py (#sendbin ARQ.fl4 256 = 513 blocos).
;  Carregar com L e executar com G 2000.  AUTONOMO: depois do apagamento a ROM some,
;  entao este programa usa SO a RAM e a propria serial (68681 canal A).
;
;  Os dados chegam pela serial em blocos de 256 bytes (a ponte serial v5, diretiva
;  #sendbin). Protocolo: o programa mostra a barra e manda o byte ACK ($06);
;  a ponte entao manda os 256 bytes seguintes. 128 KB = 512 blocos.
;
;  BANCO DE DESTINO (v2): P 301C 00 0n  (n = 1..7; padrao = 0 = nao grava).
;  O banco 0 e o de boot: so grava se tambem P 301E 0B A0. Ao terminar volta ao banco 0.
;
;  v5 (14/11/2026): COPIAR de outro banco: P 3024 00 0n  e  P 3026 C0 DE  (n = banco de origem 1..7).
;     A imagem e lida do banco n para a RAM, relida e conferida (duas leituras iguais) e so entao segue o fluxo normal
;     (modo COMPARAR = ensaio, modo GRAVAR = apaga e grava o banco de destino). Sem SCONF = $C0DE a imagem vem pela serial.
;
;  MODO (padrao = COMPARAR: nao altera a flash; serve de ensaio):
;     P 3000 00 01   e   P 3002 A5 5A    -> modo GRAVAR (apaga o setor e grava!)
;  Os dois valores precisam estar certos ao mesmo tempo, senao e o modo COMPARAR.
;  No modo COMPARAR o fluxo e exatamente o mesmo, mas so le a ROM e conta diferencas.
; ==========================================================================
UARTSR  equ $FA0003
UARTD   equ $FA0007
CMD1    equ $F80AAA
CMD2    equ $F80554
ROMB    equ $F80000
SIZE    equ $20000
MODE    equ $3000
CONF    equ $3002
OFS     equ $3004
NERR    equ $3008
FIRST   equ $300C
IDA     equ $3010
IDB     equ $3012
RUN     equ $3014
SPSAVE  equ $3018
BANK    equ $301C
BCONF   equ $301E
SRC     equ $3024          ; v5: banco de ORIGEM (1..7) para COPIAR; vale so com SCONF = $C0DE
SCONF   equ $3026
BANKR   equ $FC0000
RETB    equ $3028          ; v5b: banco para onde VOLTAR ao terminar (o banco que chamou o flasher)
RCONF   equ $302A          ; vale so com RCONF = $C0DE; senao volta ao banco 0
MAXIT   equ 30000000
BUF     equ $40000          ; imagem recebida (128 KB de RAM, como no teste de RAM)
CRCT    equ $4000           ; tabela do CRC32 (1 KB)
TRL     equ $3100           ; rodape recebido (256 bytes)
RCRC    equ $3020           ; CRC32 calculado
TMO1    equ 60000000        ; espera pelo 1o byte (~3 min): nada foi apagado ainda
TMO2    equ 4000000         ; espera entre bytes (~15 s)

        org $2000
start:  move.w  #$2700,sr
        move.l  sp,SPSAVE
        move.l  #0,OFS
        move.w  #0,NERR
        move.l  #$FFFFFFFF,FIRST
; --- ID das duas flash (antes de qualquer coisa) ---
        move.w  #$AAAA,CMD1
        move.w  #$5555,CMD2
        move.w  #$9090,CMD1
        move.w  $F80000,d0
        move.w  d0,IDA
        move.w  $F80002,d0
        move.w  d0,IDB
        move.w  #$F0F0,$F80000
        move.l  #50,d1
dly0:   subq.l  #1,d1
        bne     dly0
        lea     m_t(pc),a1
        bsr     puts
        cmpi.w  #7,BANK
        bhi     badbk                   ; banco > 7 (inclui lixo da RAM)
        lea     m_bk(pc),a1
        bsr     puts
        moveq   #0,d0
        move.w  BANK,d0
        bsr     puthex16
        lea     m_crlf(pc),a1
        bsr     puts
        cmpi.w  #$0101,IDA
        bne     badid
        cmpi.w  #$A4A4,IDB
        bne     badid
; --- modo ---
        move.w  #0,RUN
        cmpi.w  #1,MODE
        bne     md
        cmpi.w  #$A55A,CONF
        bne     md
        move.w  #1,RUN
md:     tst.w   RUN
        beq     mcomp
        tst.w   BANK
        bne     bkok
        cmpi.w  #$0BA0,BCONF
        bne     bk0
bkok:   bsr     getimg                    ; v4: recebe + confere CRC32 ANTES de apagar
        tst.w   d4
        bne     rcvbad
        lea     m_grav(pc),a1
        bsr     puts
        move.w  BANK,d0
        move.w  d0,BANKR
        bsr     erase
        lea     m_gr2(pc),a1
        bsr     puts
        bra     doprog
mcomp:  lea     m_comp(pc),a1
        bsr     puts
        bsr     getimg
        tst.w   d4
        bne     rcvbad
doprog: move.w  BANK,d0
        move.w  d0,BANKR                ; seleciona o banco (A16-A18 das duas flash)
 bsr     prog
        move.w  #$F0F0,$F80000          ; garante o modo de leitura
        move.l  #50,d1
dly1:   subq.l  #1,d1
        bne     dly1
        lea     m_fim(pc),a1
        bsr     puts
        moveq   #0,d0
        move.w  NERR,d0
        bsr     puthex16
        lea     m_fim2(pc),a1
        bsr     puts
        cmpi.l  #$FFFFFFFF,FIRST
        beq     nof
        lea     m_prim(pc),a1
        bsr     puts
        move.l  FIRST,d0
        bsr     puthex24
        lea     m_crlf(pc),a1
        bsr     puts
nof:    tst.w   NERR
        bne     fimr
        lea     m_ok(pc),a1
        bsr     puts
fimr:   bsr     rbank               ; volta ao banco 0 (boot)
        tst.w   BANK
        bne     fm_rts                  ; bancos 1..7: volta ao monitor com RTS
        tst.w   RUN
        beq     fm_rts                  ; ensaio (comparar): nada foi alterado, volta com RTS
        tst.w   NERR
        bne     fm_bad0
        jmp     $F80900                 ; v4: o banco 0 foi REescrito: o RTS voltaria para o codigo ANTIGO. Reinicia pelo reset da ROM nova
fm_rts: rts
fm_bad0: lea    m_b0e(pc),a1
        bsr     puts
        move.l  #3000000,d1
fm_d:   subq.l  #1,d1
        bne     fm_d
        move.l  SPSAVE,sp
        bra     start                   ; recomeca: espera a imagem de novo (NAO desligue)
rbank:   tst.w   BANK
        beq     rbank0                   ; gravando o banco 0: sempre volta ao banco 0
        cmpi.w  #$C0DE,RCONF
        bne     rbank0
        move.w  RETB,BANKR
        rts
rbank0:  move.w  #0,BANKR
        rts
rcvbad: bsr     rbank               ; v4: transferencia recusada, NADA foi apagado
        rts
badid:  lea     m_bid(pc),a1
        bsr     puts
        bsr     rbank
        rts
badbk:  lea     m_bbk(pc),a1
        bsr     puts
        bsr     rbank
        rts
bk0:    lea     m_b0(pc),a1
        bsr     puts
        bsr     rbank
        rts

; ---------------- apagamento do setor (banco 0) das duas flash ----------------
erase:  move.l  #0,OFS
        move.w  #$AAAA,CMD1
        move.w  #$5555,CMD2
        move.w  #$8080,CMD1
        move.w  #$AAAA,CMD1
        move.w  #$5555,CMD2
        move.w  #$3030,ROMB             ; endereco do setor = banco 0
        move.l  #0,d6
        movea.l #ROMB,a0
        moveq   #0,d0
        bsr     bar
el:     move.w  (a0),d1
        andi.w  #$8080,d1
        cmpi.w  #$8080,d1
        beq     edone
        addq.l  #1,d6
        move.l  d6,d0
        andi.l  #$1FFF,d0
        bne     el
        move.l  d6,d0                   ; estimativa: cada 8192 voltas = 2 %
        lsr.l   #8,d0
        lsr.l   #5,d0
        add.w   d0,d0
        cmpi.w  #99,d0
        bcs     eok
        move.w  #99,d0
eok:    bsr     bar
        cmpi.l  #MAXIT,d6
        bcs     el
        bra     fatal
edone:  moveq   #100,d0
        bsr     bar
        lea     m_crlf(pc),a1
        bsr     puts
        rts

; ---------------- recebe a imagem em blocos e grava/compara ----------------
prog:   move.l  #0,OFS
pg1:    cmpi.l  #SIZE,OFS
        bcc     pgend
        bsr     pctofs
        bsr     bar
        movea.l #BUF,a2                 ; v4: a palavra vem do buffer na RAM
        adda.l  OFS,a2
        movea.l #ROMB,a0
        adda.l  OFS,a0
        moveq   #127,d7
pg2:    move.w  (a2)+,d5                ; d5.w = palavra (byte alto = flash HI)
        tst.w   RUN
        beq     pgc
        bsr     pw
        tst.w   d4
        bne     fatal
pgc:    move.w  (a0),d1
        cmp.w   d5,d1
        beq     pg3
        addq.w  #1,NERR
        cmpi.l  #$FFFFFFFF,FIRST
        bne     pg3
        move.l  a0,FIRST
pg3:    addq.l  #2,a0
        dbra    d7,pg2
        addi.l  #256,OFS
        bra     pg1
pgend:  moveq   #100,d0
        bsr     bar
        lea     m_crlf(pc),a1
        bsr     puts
        rts

; pw: grava a palavra d5 em (a0) e espera o DQ7 das duas flash. d4 = 0 ok, 1 tempo esgotado
pw:     move.w  #$AAAA,CMD1
        move.w  #$5555,CMD2
        move.w  #$A0A0,CMD1
        move.w  d5,(a0)
        move.l  #4000,d3
pl:     move.w  (a0),d1
        move.w  d1,d2
        eor.w   d5,d2
        andi.w  #$8080,d2
        beq     pok
        subq.l  #1,d3
        bne     pl
        moveq   #1,d4
        rts
pok:    moveq   #0,d4
        rts

; ---------------- v4: recebe a imagem + rodape na RAM e confere o CRC32 ----------------
; saida: d4 = 0 ok, 1 recusada (mensagem ja impressa; nada foi apagado)
recv:   movem.l d0-d3/d5-d7/a0-a3,-(sp)
        movea.l #BUF,a0                 ; a RAM do buffer existe?
        move.w  #$5AA5,(a0)
        move.w  #$A55A,$5FFFE
        cmpi.w  #$5AA5,(a0)
        bne     rc_nr
        cmpi.w  #$A55A,$5FFFE
        bne     rc_nr
        lea     m_rx(pc),a1
        bsr     puts
rc_dr:  btst    #0,UARTSR               ; esvazia lixo ja recebido (ex.: Enter digitado)
        beq     rc_d2
        move.b  UARTD,d0
        move.l  #20000,d1
rc_dw:  subq.l  #1,d1
        bne     rc_dw
        bra     rc_dr
rc_d2:  move.l  #0,OFS
        moveq   #0,d6                   ; d6 = numero do bloco (0..512; o 512 e o rodape)
rc_blk: cmpi.w  #512,d6
        beq     rc_tr
        move.l  d6,d0
        lsl.l   #8,d0
        move.l  d0,OFS
        bsr     pctofs
        bsr     bar
        movea.l #BUF,a2
        adda.l  OFS,a2
        bra     rc_go
rc_tr:  movea.l #TRL,a2
rc_go:  moveq   #6,d0                   ; ACK: manda o proximo bloco
        bsr     putc
        move.w  #255,d7
        move.l  #TMO1,d3                ; so o 1o byte do arquivo tem a espera longa
        tst.w   d6
        beq     rc_by
        move.l  #TMO2,d3
rc_by:  move.l  d3,d2
        cmpi.w  #255,d7                 ; 1o byte do bloco 0? reenvia o ACK a cada ~1,5 s (o ACK pode ter sido perdido)
        bne     rc_w
        tst.w   d6
        bne     rc_w
rc_wa:  btst    #0,UARTSR
        bne     rc_g
        move.l  d2,d1
        andi.l  #$3FFFF,d1
        bne     rc_wb
        moveq   #6,d0
        bsr     putc
rc_wb:  subq.l  #1,d2
        bne     rc_wa
        bra     rc_to
rc_w:   btst    #0,UARTSR
        bne     rc_g
        subq.l  #1,d2
        bne     rc_w
        bra     rc_to
rc_g:   move.b  UARTD,(a2)+
        move.l  #TMO2,d3                ; depois do 1o byte, 15 s no maximo entre bytes
        dbra    d7,rc_by
        addq.w  #1,d6
        cmpi.w  #513,d6
        bne     rc_blk
; --- conferencia do rodape e do CRC32
        lea     TRL,a0
        cmpi.b  #'F',(a0)
        bne     rc_tb
        cmpi.b  #'L',1(a0)
        bne     rc_tb
        cmpi.b  #'4',2(a0)
        bne     rc_tb
        move.b  3(a0),d0
        andi.w  #$FF,d0
        cmp.w   BANK,d0
        bne     rc_tb
        bsr     crcinit
        bsr     crcbuf
        move.l  d0,RCRC
        move.l  TRL+4,d1                ; CRC32 esperado (big-endian, 4 bytes alinhados)
        cmp.l   d0,d1
        bne     rc_cb
        lea     m_cok(pc),a1
        bsr     puts
        move.l  RCRC,d0
        bsr     puthex32
        lea     m_cok2(pc),a1
        bsr     puts
        moveq   #0,d4
        bra     rc_x
rc_cb:  lea     m_cbad(pc),a1
        bsr     puts
        move.l  RCRC,d0
        bsr     puthex32
        lea     m_cbd2(pc),a1
        bsr     puts
        move.l  TRL+4,d0
        bsr     puthex32
        lea     m_cbd3(pc),a1
        bsr     puts
        bra     rc_bad
rc_tb:  lea     m_trl(pc),a1
        bsr     puts
        bra     rc_bad
rc_to:  lea     m_tmo(pc),a1
        bsr     puts
        bra     rc_bad
rc_nr:  lea     m_nram(pc),a1
        bsr     puts
rc_bad: moveq   #1,d4
rc_x:   movem.l (sp)+,d0-d3/d5-d7/a0-a3
        rts


; ---------------- v5: getimg - origem da imagem: banco da flash (COPIAR) ou serial ----------------
getimg: cmpi.w  #$C0DE,SCONF
        bne     recv                    ; sem a confirmacao: serial (rts de recv volta ao chamador)
        move.w  SRC,d0
        beq     recv
        cmpi.w  #8,d0
        beq     sdimg                   ; v5c: imagem ja carregada em BUF pelo leitor do cartao SD
        cmpi.w  #7,d0
        bhi     recv
        cmp.w   BANK,d0
        bne     cpybank
        lea     m_same(pc),a1
        bsr     puts
        moveq   #1,d4
        rts
; cpybank: copia o banco SRC para BUF, relê e compara; mostra o CRC32. d4 = 0 ok, 1 recusada (nada foi apagado)
cpybank: movem.l d0-d3/d5-d7/a0-a3,-(sp)
        movea.l #BUF,a0
        move.w  #$5AA5,(a0)
        move.w  #$A55A,$5FFFE
        cmpi.w  #$5AA5,(a0)
        bne     cp_nr
        cmpi.w  #$A55A,$5FFFE
        bne     cp_nr
        lea     m_cp(pc),a1
        bsr     puts
        moveq   #0,d0
        move.w  SRC,d0
        bsr     puthex16
        lea     m_crlf(pc),a1
        bsr     puts
        move.w  SRC,BANKR               ; janela $F80000 = banco de origem (este codigo roda na RAM)
        movea.l #ROMB,a0
        movea.l #BUF,a2
        move.w  #32767,d7
cp_l:   move.l  (a0)+,(a2)+
        dbra    d7,cp_l
        movea.l #ROMB,a0                ; segunda leitura: tem de ser igual a primeira
        movea.l #BUF,a2
        move.w  #32767,d7
cp_v:   move.l  (a0)+,d0
        cmp.l   (a2)+,d0
        bne     cp_bad
        dbra    d7,cp_v
        bsr     rbank
        bsr     crcinit
        bsr     crcbuf
        move.l  d0,RCRC
        lea     m_cpok(pc),a1
        bsr     puts
        move.l  RCRC,d0
        bsr     puthex32
        lea     m_cok2(pc),a1
        bsr     puts
        moveq   #0,d4
        bra     cp_x
cp_bad: bsr     rbank
        lea     m_cpbad(pc),a1
        bsr     puts
        bra     cp_e
cp_nr:  lea     m_nram(pc),a1
        bsr     puts
cp_e:   moveq   #1,d4
cp_x:   movem.l (sp)+,d0-d3/d5-d7/a0-a3
        rts

; crcinit: tabela do CRC32 (polinomio $EDB88320) em CRCT
crcinit: movem.l d0-d2/a0,-(sp)
        movea.l #CRCT,a0
        moveq   #0,d1
ci_n:   move.l  d1,d0
        moveq   #7,d2
ci_b:   lsr.l   #1,d0
        bcc     ci_s
        eori.l  #$EDB88320,d0
ci_s:   dbra    d2,ci_b
        move.l  d0,(a0)+
        addq.w  #1,d1
        cmpi.w  #256,d1
        bne     ci_n
        movem.l (sp)+,d0-d2/a0
        rts
; crcbuf: d0.l = CRC32 (igual ao zlib) dos 128 KB em BUF
crcbuf: movem.l d1-d3/a0-a2,-(sp)
        movea.l #BUF,a0
        movea.l #BUF+SIZE,a1
        moveq   #-1,d0
cb_l:   moveq   #0,d1
        move.b  (a0)+,d1
        eor.b   d0,d1
        lsl.w   #2,d1
        lsr.l   #8,d0
        movea.l #CRCT,a2
        adda.w  d1,a2
        move.l  (a2),d2
        eor.l   d2,d0
        cmpa.l  a1,a0
        bne     cb_l
        not.l   d0
        movem.l (sp)+,d1-d3/a0-a2
        rts
; ---- v5c: sdimg - a imagem de 128 KB ja esta em BUF (veio do cartao SD). Exige cabecalho AB e CRC32 do cabecalho correto.
sdimg:  movem.l d0-d3/d5-d7/a0-a3,-(sp)
        lea     m_sd(pc),a1
        bsr     puts
        cmpi.w  #$4142,BUF+$7C0
        bne     sd_nh
        bsr     crcinit
        movea.l #BUF,a0
        moveq   #-1,d0
        move.l  #$7C0,d3
        bsr     crcrun
        move.l  BUF+$7C8,d3             ; fim da imagem (como no mkbanco: o CRC vai ate o ultimo byte != $FF)
        cmpi.l  #$F9FFFF,d3
        bhi     sd_cr
        subi.l  #$F807FF,d3             ; bytes de $F80800 ate o fim
        ble     sd_n2
        movea.l #BUF+$800,a0
        bsr     crcrun
sd_n2:
        not.l   d0
        move.l  d0,RCRC
        move.l  BUF+$7E8,d1
        cmp.l   d1,d0
        bne     sd_cr
        lea     m_sdok(pc),a1
        bsr     puts
        movea.l #BUF+$7D0,a0
        moveq   #16,d3
        bsr     ptx
        lea     m_sdv(pc),a1
        bsr     puts
        movea.l #BUF+$7E0,a0
        moveq   #8,d3
        bsr     ptx
        lea     m_cok2(pc),a1
        bsr     puts
        moveq   #0,d4
        bra     sd_x
sd_nh:  lea     m_sdnh(pc),a1
        bra     sd_e
sd_cr:  lea     m_sdcr(pc),a1
sd_e:   bsr     puts
        moveq   #1,d4
sd_x:   movem.l (sp)+,d0-d3/d5-d7/a0-a3
        rts
; crcrun: d0 = CRC corrente, a0 = dados, d3.l = quantidade (>0). Usa d1,d2,a2
crcrun: moveq   #0,d1
        move.b  (a0)+,d1
        eor.b   d0,d1
        lsl.w   #2,d1
        lsr.l   #8,d0
        movea.l #CRCT,a2
        adda.w  d1,a2
        move.l  (a2),d2
        eor.l   d2,d0
        subq.l  #1,d3
        bne     crcrun
        rts
; ptx: imprime d3 bytes de (a0), nao imprimivel vira espaco
ptx:    move.b  (a0)+,d0
        cmpi.b  #32,d0
        bcs     ptx_s
        cmpi.b  #127,d0
        bcs     ptx_o
ptx_s:  moveq   #32,d0
ptx_o:  bsr     putc
        subq.l  #1,d3
        bne     ptx
        rts
puthex32: move.l d0,-(sp)
        swap    d0
        bsr     puthex16
        move.l  (sp)+,d0
        bsr     puthex16
        rts

fatal:  lea     m_fat(pc),a1
        bsr     puts
        move.l  OFS,d0
        addi.l  #ROMB,d0
        bsr     puthex24
        lea     m_fat2(pc),a1
        bsr     puts
        move.l  #3000000,d1             ; pausa (~10 s) para dar tempo de ler
fdl:    subq.l  #1,d1
        bne     fdl
        move.w  #0,BANKR
        move.l  SPSAVE,sp
        bra     start                   ; recomeca: confere o ID, apaga de novo e espera a imagem

; ---------------- serial propria ----------------
putc:   btst    #2,UARTSR
        beq     putc
        move.b  d0,UARTD
        rts
getb:   btst    #0,UARTSR
        beq     getb
        move.b  UARTD,d0
        rts
puts:   movem.l d0/a1,-(sp)
ps1:    move.b  (a1)+,d0
        beq     ps2
        bsr     putc
        bra     ps1
ps2:    movem.l (sp)+,d0/a1
        rts
puthex24: movem.l d0-d3,-(sp)
        move.l  d0,d3
        lsl.l   #8,d3
        moveq   #5,d1
        bra     phx
puthex16: movem.l d0-d3,-(sp)
        move.l  d0,d3
        swap    d3
        moveq   #3,d1
phx:    rol.l   #4,d3
        move.b  d3,d0
        andi.b  #15,d0
        addi.b  #48,d0
        cmpi.b  #58,d0
        bcs     ph1
        addq.b  #7,d0
ph1:    bsr     putc
        dbra    d1,phx
        movem.l (sp)+,d0-d3
        rts
; putpct: d0.w = 0..100, escreve 3 colunas
putpct: movem.l d0-d4,-(sp)
        andi.l  #$FFFF,d0
        divu    #100,d0
        move.w  d0,d2
        swap    d0
        andi.l  #$FFFF,d0
        divu    #10,d0
        move.w  d0,d3
        swap    d0
        move.w  d0,d4
        tst.w   d2
        beq     pp1
        move.b  d2,d0
        addi.b  #48,d0
        bsr     putc
        bra     pp2
pp1:    moveq   #32,d0
        bsr     putc
pp2:    tst.w   d2
        bne     pp3
        tst.w   d3
        beq     pp4
pp3:    move.b  d3,d0
        addi.b  #48,d0
        bsr     putc
        bra     pp5
pp4:    moveq   #32,d0
        bsr     putc
pp5:    move.b  d4,d0
        addi.b  #48,d0
        bsr     putc
        movem.l (sp)+,d0-d4
        rts
; pctofs: d0.w = percentual de OFS (0..100)
pctofs: move.l  OFS,d0
        lsr.l   #8,d0
        mulu    #100,d0
        lsr.l   #8,d0
        lsr.l   #1,d0
        rts
; bar: d0.w = percentual. Escreve  [...........#...........] 50%    F80100  (sobrescreve a linha)
bar:    movem.l d0-d7/a0-a1,-(sp)
        move.w  d0,d6
        moveq   #13,d0
        bsr     putc
        moveq   #91,d0
        bsr     putc
        move.w  d6,d0
        andi.l  #$FFFF,d0
        mulu    #22,d0
        divu    #100,d0
        move.w  d0,d5
        moveq   #0,d4
bl:     moveq   #46,d0
        cmp.w   d5,d4
        bne     bp
        moveq   #35,d0
bp:     bsr     putc
        addq.w  #1,d4
        cmpi.w  #23,d4
        bne     bl
        moveq   #93,d0
        bsr     putc
        moveq   #32,d0
        bsr     putc
        move.w  d6,d0
        bsr     putpct
        moveq   #37,d0
        bsr     putc
        moveq   #3,d4
bsp:    moveq   #32,d0
        bsr     putc
        dbra    d4,bsp
        move.l  OFS,d0
        addi.l  #ROMB,d0
        bsr     puthex24
        movem.l (sp)+,d0-d7/a0-a1
        rts

m_t:    dc.b 13,10,"FLASH v4 - banco de destino das duas Am29F040B",13,10,0
m_bk:   dc.b "Banco de destino: $",0
m_bbk:  dc.b "ERRO: banco invalido (use P 301C 00 0n, n = 0..7). Nada foi feito.",13,10,0
m_b0:   dc.b "RECUSADO: banco 0 e o de boot. Para gravar nele: P 301E 0B A0. Nada foi feito.",13,10,0
m_comp: dc.b "MODO COMPARAR (ensaio): NAO altera a flash. COMPARANDO:",13,10,0
m_grav: dc.b "MODO GRAVAR: APAGANDO a ROM (percentual estimado):",13,10,0
m_gr2:  dc.b "GRAVANDO:",13,10,0
m_fim:  dc.b "CONCLUIDO. Palavras diferentes: $",0
m_fim2: dc.b 13,10,0
m_prim: dc.b "Primeira diferenca em $",0
m_ok:   dc.b "Tudo igual a imagem recebida.",13,10,0
m_bid:  dc.b "ERRO: ID das flash diferente de 01/A4. Nada foi feito.",13,10,0
m_fat:  dc.b 13,10,"ERRO FATAL em $",0
m_fat2: dc.b " - a ROM esta incompleta. NAO desligue: o programa recomeca em 10 s e espera a imagem de novo (reenvie).",13,10,0
m_rx:   dc.b "RECEBENDO a imagem na RAM (nada e apagado antes de conferir o CRC32):",13,10,0
m_cok:  dc.b 13,10,"CRC32 conferido: $",0
m_cok2: dc.b " - imagem integra, prosseguindo.",13,10,0
m_cbad: dc.b 13,10,"ERRO: CRC32 DIFERENTE (calculado $",0
m_cbd2: dc.b ", esperado $",0
m_cbd3: dc.b "). NADA foi apagado. Reenvie.",13,10,0
m_tmo:  dc.b 13,10,"ERRO: tempo esgotado esperando a imagem. NADA foi apagado.",13,10,0
m_trl:  dc.b 13,10,"ERRO: rodape invalido (use mkfl4.py; magic FL4 e banco). NADA foi apagado.",13,10,0
m_nram: dc.b "ERRO: sem RAM em $40000-$5FFFF. NADA foi feito.",13,10,0
m_b0e: dc.b 13,10,"ERRO: banco 0 com diferencas apos gravar! NAO desligue nem de RESET: o programa recomeca em 10 s - reenvie a imagem.",13,10,0
m_cp:   dc.b 13,10,"COPIANDO a imagem do banco $",0
m_cpok: dc.b "Leituras iguais. CRC32 da imagem: $",0
m_cpbad: dc.b "ERRO: duas leituras do banco de origem DIFEREM. NADA foi apagado.",13,10,0
m_sd:   dc.b 13,10,"Imagem do cartao SD em $40000: conferindo cabecalho AB e CRC32...",13,10,0
m_sdok: dc.b "Cabecalho OK. Nome: ",0
m_sdv:  dc.b "  versao: ",0
m_sdnh: dc.b "ERRO: a imagem nao tem cabecalho AB. Nada foi feito.",13,10,0
m_sdcr: dc.b "ERRO: CRC32 do cabecalho nao confere (arquivo errado ou corrompido). Nada foi feito.",13,10,0
m_same: dc.b "ERRO: banco de origem = banco de destino. Nada foi feito.",13,10,0
m_crlf: dc.b 13,10,0
        even
