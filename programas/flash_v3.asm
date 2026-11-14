; ==========================================================================
;  FLASH.ASM v2 - apaga e grava UM BANCO das duas Am29F040B - PARAGON 50
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
BANKR   equ $FC0000
MAXIT   equ 30000000

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
bkok:
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
fimr:   move.w  #0,BANKR               ; volta ao banco 0 (boot)
        tst.w   BANK
        bne     fimr_r
        jmp     $F80900                 ; v3: gravou o banco 0 -> o monitor antigo sumiu: reinicia pelo vetor fixo $F80900
fimr_r: rts
badid:  lea     m_bid(pc),a1
        bsr     puts
        move.w  #0,BANKR
        rts
badbk:  lea     m_bbk(pc),a1
        bsr     puts
        move.w  #0,BANKR
        rts
bk0:    lea     m_b0(pc),a1
        bsr     puts
        move.w  #0,BANKR
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
        moveq   #6,d0                   ; ACK: manda o proximo bloco
        bsr     putc
        movea.l #ROMB,a0
        adda.l  OFS,a0
        moveq   #127,d7
pg2:    bsr     getb
        move.b  d0,d5
        lsl.w   #8,d5
        bsr     getb
        move.b  d0,d5                   ; d5.w = palavra (byte alto = flash HI)
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

m_t:    dc.b 13,10,"FLASH v3 - banco de destino das duas Am29F040B",13,10,0
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
m_crlf: dc.b 13,10,0
        even
