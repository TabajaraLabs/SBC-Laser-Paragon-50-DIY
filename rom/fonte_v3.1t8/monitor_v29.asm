; ==========================================================================
;  PARAGON 50 - MONITOR 68000  v2.2          (Tabajara Labs)
;  Placa CPU 68000 @ 8 MHz reaproveitada como computador standalone.
;
;  Mapa de memoria conhecido:
;     $000000-$0003FF  tabela de vetores (copiada da ROM no reset)
;     $000400-$0004FF  variaveis do monitor
;     $000500-$0005FF  buffer de linha
;     $000600-$001EFF  pilha (SSP inicial = $1F00, cresce para baixo)
;     $002000-...      RAM livre para programas (carregados com L)
;     $F80000-$F8FFFF  ROM (2 x 27C256)
;     $FA0000-$FA001F  68681 DUART (canal A = console, canal B inicializado)
;
;  Comandos (maiusculas ou minusculas, numeros em hexadecimal):
;     D [ini [fim]]    dump de memoria        P ini b b b ...   grava bytes
;     F ini fim b      preenche               T ini fim         teste de RAM
;     L                carrega S-records      G [end]           executa
;     I                informacoes            ?                 ajuda
; ==========================================================================

DUART_SRA   equ $FA0003        ; status canal A  (bit0 RxRDY, bit2 TxRDY)
DUART_THRA  equ $FA0006        ; dado canal A (escrita em palavra, par)
DUART_RHRA  equ $FA0007        ; dado canal A (leitura em byte, impar)
DUART_SOPR  equ $FA001C        ; set output port bits   (OP = nivel BAIXO)
DUART_ROPR  equ $FA001E        ; reset output port bits (OP = nivel ALTO)
DUART_IP    equ $FA001B        ; input port (byte)

LASTADR     equ $0400          ; ultimo endereco usado (long)
ENTRY       equ $0404          ; ponto de entrada do ultimo S-record (long)
RECCNT      equ $0408          ; contador de registros S (word)
BUF         equ $0500          ; buffer de linha (256 bytes)
TETRIS      equ $F81C00         ; Tetris em ROM (entrada; volta com RTS)
RAMUSER     equ $2000          ; inicio da RAM de usuario / limite de protecao
RAMEND      equ $040C          ; ULTIMO byte de RAM detectada (long): $FFFF, $1FFFF, $3FFFF...
RAMMAGIC    equ $0430          ; 'RAM1' ($52414D31): RAMEND valido (le o CP/M)
RPBUF       equ $0410          ; 16 palavras salvas pela sondagem de RAM ($0410-$042F; marca em $0430)
RPQ         equ $FFE0          ; posicao sondada dentro de cada bloco de 64 KB
LSTART      equ $0434          ; v2.4: menor endereco gravado pelo L (long)
LSIZE       equ $0438          ; v2.4: total de bytes gravados pelo L (long)
BPLOOP      equ 7500            ; v2.6: iteracoes de DBRA por 10 ms (calibrar no osciloscopio)
BKMENU      equ $F833F8         ; v2.4: menu de bancos (modulo bancos_v1, org $F833F8)
LSTAT       equ $F833FE         ; v2.4: imprime inicio/tamanho do L
LATCH       equ $020018         ; v2.6: latch de saidas (bit2 = CS do SD, bit9 = buzzer)
FLCHK       equ $F83404
BKSYS       equ $F833F8+18       ; v2.8: inicia o sistema no banco 1 (d0.l = entrada); BASIC $F84000, CP/M $F88000
SDREC       equ $F84000          ; v2.8: leitor FAT16 do cartao SD + gravador de bancos (rotina; volta com RTS)         ; v2.5: reconhece o comando FLASH (so volta se a linha nao for FLASH)
RPMAX       equ 2              ; blocos de 64 KB sondados: so $0-$1FFFF ($20000+ e E/S do laser: NUNCA gravar)

; --------------------------------------------------------------------------
;  Tabela de vetores (256 entradas de 4 bytes), copiada para a RAM em $0
; --------------------------------------------------------------------------
        org $F80000
        dc.l $00001F00          ; vetor 0: SSP inicial
        dc.l reset              ; vetor 1: PC inicial
{{VEC}}
; --------------------------------------------------------------------------
;  Pequenos tratadores de excecao: empilham o numero do vetor e vao ao comum
; --------------------------------------------------------------------------
        org $F80400
{{STUBS}}

; --------------------------------------------------------------------------
;  v2.6: buzzer (ativo, no bit 9 do latch $020018) - avisos sonoros e comando BEEP
;  beep     d0.w = duracao em unidades de 10 ms (1..500); preserva todos os registradores
;  beep_err dois bipes curtos (erro de comando, erro de L, excecao)
;  Mantem o watchdog alimentado (strobe a cada 10 ms). O latch volta a $0004 (CS do SD alto, resto 0).
; --------------------------------------------------------------------------
        org $F80500
beep:   movem.l d0-d2,-(sp)
        andi.l  #$FFFF,d0
        beq     bp_x
        cmpi.w  #500,d0
        bls     bp_g
        move.w  #500,d0
bp_g:   move.w  #$0204,LATCH
bp_u:   move.w  #BPLOOP,d1
bp_d:   dbra    d1,bp_d
        bsr     strobe
        subq.w  #1,d0
        bne     bp_u
        move.w  #$0004,LATCH
bp_x:   movem.l (sp)+,d0-d2
        rts
beep_err:
        move.l  d0,-(sp)
        moveq   #7,d0
        bsr     beep
        moveq   #7,d0
        bsr     pausa
        moveq   #7,d0
        bsr     beep
        move.l  (sp)+,d0
        rts
berr_main:
        bsr     beep_err
        bra     main_loop
berr_rst:
        bsr     beep_err
        bra     restart
pausa:  movem.l d0-d2,-(sp)              ; d0.w = pausa em unidades de 10 ms (latch inalterado)
ps_u:   move.w  #BPLOOP,d1
ps_d:   dbra    d1,ps_d
        bsr     strobe
        subq.w  #1,d0
        bne     ps_u
        movem.l (sp)+,d0-d2
        rts
; BEEP [n]: reconhece o comando no inicio da linha (a1 = texto sem espacos iniciais).
; Se nao for BEEP volta com a1 e registradores intactos; se for, bipa e volta ao laco principal.
bpchk:  movem.l d0-d2/a0/a2,-(sp)
        movea.l a1,a2
        lea     s_beep(pc),a0
bk_l:   move.b  (a0)+,d0
        beq     bk_end
        move.b  (a2)+,d1
        cmpi.b  #'a',d1
        blo     bk_c
        cmpi.b  #'z',d1
        bhi     bk_c
        subi.b  #32,d1
bk_c:   cmp.b   d0,d1
        beq     bk_l
bk_no:  movem.l (sp)+,d0-d2/a0/a2
        rts
bk_end: move.b  (a2),d1
        beq     bk_def
        cmpi.b  #' ',d1
        bne     bk_no
bk_sp:  cmpi.b  #' ',(a2)
        bne     bk_n
        addq.l  #1,a2
        bra     bk_sp
bk_n:   moveq   #0,d2
bk_dg:  moveq   #0,d1
        move.b  (a2)+,d1
        subi.b  #'0',d1
        cmpi.b  #9,d1
        bhi     bk_nd
        move.w  d2,d0
        lsl.w   #3,d2
        add.w   d0,d2
        add.w   d0,d2
        add.w   d1,d2
        bra     bk_dg
bk_nd:  tst.w   d2
        bne     bk_go
bk_def: moveq   #10,d2                  ; padrao: 100 ms
bk_go:  move.w  d2,d0
        bsr     beep
        movem.l (sp)+,d0-d2/a0/a2
        addq.l  #4,sp                   ; descarta o endereco de retorno: volta direto ao laco principal
        bra     main_loop
s_beep: dc.b "BEEP",0
        dc.b 0
; --------------------------------------------------------------------------
;  Tabela de servicos para programas de usuario (enderecos FIXOS):
;     $F80800 putc   d0.b = caractere
;     $F80806 getc   -> d0.b (espera)
;     $F8080C puts   a1 = texto terminado em 0
;     $F80812 hexb   d0.b      $F80818 hexw d0.w     $F8081E hexl d0.l
;     $F80824 crlf             $F8082A strobe (alimenta o watchdog!)
;     $F80830 gethex a1 -> d0 (d1 = no. de digitos)   $F80836 getline (BUF)   $F8083C restart (volta ao prompt)
;  Programas de usuario rodam em modo supervisor e DEVEM chamar strobe
;  pelo menos a cada 100 ms, a menos que o watchdog esteja inibido (JP6).
; --------------------------------------------------------------------------
        org $F80800
        jmp putc
        jmp getc
        jmp puts
        jmp hexb
        jmp hexw
        jmp hexl
        jmp crlf
        jmp strobe
        jmp gethex
        jmp getline
        jmp restart                     ; $F8083C v2.5: volta ao prompt do monitor (usado pelo MONITOR do EhBASIC)

; ==========================================================================
;  RESET  (endereco $F84000, o mesmo do firmware original)
; ==========================================================================
        org $F80900
reset:
        move.w  #$2700,sr               ; supervisor, interrupcoes mascaradas
        movea.l #$1F00,sp               ; pilha
        movea.l #0,a1                   ; destino: RAM $0
        movea.l #$F80000,a2             ; origem : ROM (tabela de vetores)
        move.w  #255,d1                 ; 256 palavras longas
rst_cp: move.l  (a2)+,(a1)+
        dbra    d1,rst_cp
        movea.l #$800,a1                ; zera $0800-$1BFF (estado do modulo v2: depurador e assembler)
        move.w  #1279,d1
rst_z:  clr.l   (a1)+
        dbra    d1,rst_z
        bsr     ramprobe                        ; detecta o tamanho da RAM -> RAMEND
        bsr     duart_init
        jsr     $F87EE0                 ; v2.7: splash no LCD (modulo em $F87EE0; usa o servico de LCD de $F80614)
        move.w  #4,LATCH                ; v2.6: buzzer calado, CS do SD alto, resto em 0
        move.l  #RAMUSER,LASTADR
        clr.l   ENTRY
        lea     m_cls(pc),a1                    ; limpa a tela (ANSI) antes do menu
        bsr     puts
        lea     m_menu(pc),a1
        bsr     puts
        moveq   #8,d0                   ; v2.6: um bipe no boot
        bsr     beep
        moveq   #15,d7                  ; espera ~5 s por uma tecla; sem tecla -> monitor
rm_o:   move.w  #$FFFF,d6
rm_i:   btst    #0,DUART_SRA
        bne     rm_key
        dbra    d6,rm_i
        bsr     strobe
        dbra    d7,rm_o
        bra     rm_mon
rm_key: move.b  DUART_RHRA,d0
        bsr     upper
        cmpi.b  #'B',d0
        beq     cmd_b
        cmpi.b  #'C',d0
        beq     cmd_c
        cmpi.b  #'A',d0
        beq     rm_ban
        cmpi.b  #'T',d0
        beq     rm_tet
        cmpi.b  #'R',d0
        beq     rm_rec
rm_mon: lea     m_banner(pc),a1         ; M (ou outra tecla / sem tecla): monitor
        bsr     puts
        bra     main_loop
rm_ban: jmp     BKMENU                  ; menu de bancos da flash (nao volta: RESET)
rm_tet: jsr     TETRIS                  ; Q no jogo volta ao menu
        bra     reset
rm_rec: jsr     SDREC                   ; v2.8: shell do cartao SD (Q volta)
        bra     reset

; ---- laco principal --------------------------------------------------------
main_loop:
        lea     m_prompt(pc),a1
        bsr     puts
        bsr     getline                 ; texto em BUF
        movea.l #BUF,a1
        bsr     skipsp
        jsr     FLCHK                   ; v2.5: FLASH [banco]
        bsr     bpchk                   ; v2.6: BEEP [n]
        move.b  (a1)+,d0
        beq     main_loop               ; linha vazia
        bsr     upper
        cmpi.l  #$45585431,$F90000      ; 'EXT1' = modulo v2 presente (27C512)? ele tem prioridade
        bne     ml_base
        move.l  a1,-(sp)
        move.l  d0,-(sp)
        andi.l  #$FF,d0
        jsr     $F90004                 ; d0 = comando, a1 = argumentos; devolve d0 = 0 se tratou
        move.l  d0,d1
        move.l  (sp)+,d0
        movea.l (sp)+,a1
        tst.l   d1
        beq     main_loop
ml_base:
        cmpi.b  #'D',d0
        beq     cmd_d
        cmpi.b  #'P',d0
        beq     cmd_p
        cmpi.b  #'F',d0
        beq     cmd_f
        cmpi.b  #'T',d0
        beq     cmd_t
        cmpi.b  #'G',d0
        beq     cmd_g
        cmpi.b  #'L',d0
        beq     cmd_l
        cmpi.b  #'I',d0
        beq     cmd_i
        cmpi.b  #'?',d0
        beq     cmd_h
        cmpi.b  #'H',d0
        beq     cmd_h
        cmpi.b  #'B',d0
        beq     cmd_b
        cmpi.b  #'C',d0
        beq     cmd_c
        cmpi.b  #'M',d0
        beq     cmd_m
        cmpi.b  #'V',d0
        beq     cmd_v
        cmpi.b  #'S',d0
        beq     cmd_s
        cmpi.b  #'W',d0
        beq     cmd_w
cmd_err:
        lea     m_err(pc),a1
        bsr     puts
        bra     berr_main

restart:                                 ; volta ao monitor (apos excecao/G)
        move.w  #$2700,sr
        movea.l #$1F00,sp
        bra     main_loop

; ==========================================================================
;  COMANDOS
; ==========================================================================
cmd_h:
        lea     m_help(pc),a1
        bsr     puts
        bra     main_loop

cmd_i:
        lea     m_info(pc),a1
        bsr     puts
        move.b  DUART_IP,d0
        bsr     hexb
        bsr     crlf
        lea     m_iram(pc),a1                   ; RAM: $000000-$xxxxxx (nnn KB)
        bsr     puts
        move.l  RAMEND,d0
        bsr     hexl
        lea     m_ikb(pc),a1
        bsr     puts
        move.l  RAMEND,d0
        addq.l  #1,d0
        moveq   #10,d1
        lsr.l   d1,d0                           ; bytes -> KB
        bsr     decw
        lea     m_ikb2(pc),a1
        bsr     puts
        lea     m_ifree(pc),a1                  ; livre para programas
        bsr     puts
        move.l  RAMEND,d0
        bsr     hexl
        bsr     crlf
        lea     m_irom(pc),a1
        bsr     puts
        bra     main_loop

; ---- decw: imprime d0.w em decimal (sem zeros a esquerda) --------------------
decw:   andi.l  #$FFFF,d0
        moveq   #0,d2                   ; d2 = 1 depois do primeiro digito
        move.w  #1000,d3
        bsr     dw_d
        move.w  #100,d3
        bsr     dw_d
        move.w  #10,d3
        bsr     dw_d
        addi.b  #'0',d0                 ; unidades
        bra     putc
dw_d:   moveq   #0,d1
dw_s:   cmp.w   d3,d0
        blo     dw_o
        sub.w   d3,d0
        addq.w  #1,d1
        bra     dw_s
dw_o:   tst.w   d1
        bne     dw_p
        tst.w   d2
        beq     dw_r                    ; zero a esquerda: nao imprime
dw_p:   move.w  d0,-(sp)
        move.b  d1,d0
        addi.b  #'0',d0
        bsr     putc
        move.w  (sp)+,d0
        moveq   #1,d2
dw_r:   rts

; ---- ramprobe: mede a RAM em blocos de 64 KB (ATENCAO: o decodificador so da RAM em $0-$1FFFF;
;      $20000-$3FFFF e E/S da placa do laser, $60000-$7FFFF nao gera /DTACK: nao sondar alem de RPMAX) ---------------------------------
;  Em cada bloco grava uma assinatura propria na palavra $xFFE0, limpa o
;  barramento lendo a ROM (um barramento sem dispositivo "lembra" o ultimo
;  valor) e confere se o valor voltou E se as assinaturas dos blocos
;  anteriores continuam la (isso detecta espelhos: a RAM de 64 KB repete-se).
;  O conteudo original de todas as palavras sondadas e restaurado.
;  Saida: RAMEND = ultimo byte da RAM contigua a partir de $0 (minimo $FFFF).
ramprobe:
        moveq   #0,d4                   ; d4 = bloco em teste
rp_nx:  cmpi.w  #RPMAX,d4
        beq     rp_full
        move.w  d4,d1
        bsr     rp_adr                  ; a0 = endereco do bloco d4
        move.w  d4,d1
        add.w   d1,d1
        movea.w #RPBUF,a1
        adda.w  d1,a1
        move.w  (a0),(a1)               ; salva o original
        move.w  d4,d1
        bsr     rp_sig
        move.w  d0,d5                   ; d5 = assinatura do bloco d4
        move.w  d5,(a0)
        move.w  $F80000,d2              ; leituras da ROM limpam o barramento
        move.w  $F80002,d2
        cmp.w   (a0),d5
        bne     rp_end                  ; nao voltou: nao ha RAM aqui
        moveq   #0,d3                   ; confere os blocos anteriores
rp_ck:  cmp.w   d4,d3
        bhs     rp_ok
        move.w  d3,d1
        bsr     rp_adr
        move.w  d3,d1
        bsr     rp_sig
        cmp.w   (a0),d0
        bne     rp_end                  ; um bloco anterior foi sobrescrito: espelho
        addq.w  #1,d3
        bra     rp_ck
rp_ok:  addq.w  #1,d4
        bra     rp_nx
rp_full:
        move.w  d4,d7                   ; d7 = numero de blocos bons
        move.w  d4,d5
        subq.w  #1,d5                   ; ultimo indice salvo
        bra     rp_rest
rp_end: move.w  d4,d7                   ; blocos bons = indice que falhou
        move.w  d4,d5                   ; o que falhou tambem foi salvo
        tst.w   d7
        bne     rp_rest
        moveq   #1,d7                   ; minimo: 1 bloco (a RAM do monitor)
rp_rest:                                ; restaura de d5 ate 0
        move.w  d5,d1
        bsr     rp_adr
        move.w  d5,d1
        add.w   d1,d1
        movea.w #RPBUF,a1
        adda.w  d1,a1
        move.w  (a1),(a0)
        subq.w  #1,d5
        bpl     rp_rest
        andi.l  #$FFFF,d7
        swap    d7                      ; d7 = blocos * $10000
        subq.l  #1,d7
        move.l  d7,RAMEND
        move.l  #$52414D31,RAMMAGIC
        rts
rp_adr: moveq   #0,d0                   ; d1.w = bloco -> a0 = bloco*$10000+RPQ
        move.w  d1,d0
        swap    d0
        addi.l  #RPQ,d0
        movea.l d0,a0
        rts
rp_sig: move.w  d1,d0                   ; d1.w = bloco -> d0.w = $5AA5 + bloco*$0111
        move.w  d1,d6
        lsl.w   #4,d6
        add.w   d6,d0
        lsl.w   #4,d6
        add.w   d6,d0
        addi.w  #$5AA5,d0
        rts

; ---- D [ini [fim]] : dump -----------------------------------------------
cmd_d:
        bsr     gethex
        tst.l   d1
        beq     cd_noadr
        move.l  d0,d4                   ; d4 = inicio
        bsr     gethex
        tst.l   d1
        beq     cd_defend
        move.l  d0,d5                   ; d5 = fim
        bra     cd_go
cd_noadr:
        move.l  LASTADR,d4
cd_defend:
        move.l  d4,d5
        addi.l  #$7F,d5                 ; 128 bytes por padrao
cd_go:
cd_line:
        move.l  d4,d0
        bsr     hexl
        move.b  #32,d0
        bsr     putc
        move.b  #32,d0
        bsr     putc
        movea.l d4,a2
        moveq   #15,d6
cd_h:   move.b  (a2)+,d0
        bsr     hexb
        move.b  #32,d0
        bsr     putc
        dbra    d6,cd_h
        movea.l d4,a2
        moveq   #15,d6
cd_a:   move.b  (a2)+,d0
        cmpi.b  #32,d0
        blt     cd_dot
        cmpi.b  #126,d0
        bgt     cd_dot
        bra     cd_p
cd_dot: move.b  #46,d0
cd_p:   bsr     putc
        dbra    d6,cd_a
        bsr     crlf
        addi.l  #16,d4
        cmp.l   d4,d5
        bhs     cd_line
        move.l  d4,LASTADR
        bra     main_loop

; ---- P ini b b b ... : grava bytes ----------------------------------------
cmd_p:
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        movea.l d0,a2
cp_l:   bsr     gethex
        tst.l   d1
        beq     cp_done
        move.b  d0,(a2)+
        bra     cp_l
cp_done:
        move.l  a2,LASTADR
        lea     m_ok(pc),a1
        bsr     puts
        bra     main_loop

; ---- F ini fim b : preenche -----------------------------------------------
cmd_f:
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        move.l  d0,d4
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        move.l  d0,d5
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        move.l  d0,d3
        movea.l d4,a2
        moveq   #0,d6
cf_l:   move.b  d3,(a2)+
        addq.b  #1,d6
        bne     cf_n
        bsr     strobe                  ; a cada 256 bytes alimenta o watchdog
cf_n:   cmp.l   a2,d5
        bhs     cf_l
        lea     m_ok(pc),a1
        bsr     puts
        bra     main_loop

; ---- T ini fim : teste de RAM (palavras; fim = ultima palavra) ---------------
cmd_t:
        bsr     skipsp
        tst.b   (a1)
        beq     ct_tet                  ; T sem argumentos = Tetris
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        move.l  d0,d4
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        move.l  d0,d5
        cmpi.l  #RAMUSER,d4
        blo     t_prot
        andi.l  #$FFFFFFFE,d4
        andi.l  #$FFFFFFFE,d5
        cmp.l   d4,d5
        blo     cmd_err
        moveq   #0,d6                   ; contador de erros
        moveq   #0,d3                   ; passada 0,1,2
        moveq   #0,d2                   ; contador para o watchdog
t_pass: movea.l d4,a2
t_w:    bsr     t_pat
        move.w  d0,(a2)+
        addq.b  #1,d2
        bne     t_w2
        bsr     strobe
t_w2:   cmp.l   a2,d5
        bhs     t_w
        movea.l d4,a2
t_v:    bsr     t_pat
        cmp.w   (a2)+,d0
        beq     t_ok
        bsr     t_report
t_ok:   addq.b  #1,d2
        bne     t_v2
        bsr     strobe
t_v2:   cmp.l   a2,d5
        bhs     t_v
        move.b  #46,d0                  ; '.' ao fim de cada passada
        bsr     putc
        addq.w  #1,d3
        cmpi.w  #3,d3
        blt     t_pass
        bsr     crlf
        tst.l   d6
        bne     t_bad
        lea     m_tok(pc),a1
        bsr     puts
        bra     main_loop
t_bad:  lea     m_tbad(pc),a1
        bsr     puts
        move.l  d6,d0
        bsr     hexl
        bsr     crlf
        bra     main_loop
t_prot: lea     m_prot(pc),a1
        bsr     puts
        bra     main_loop

t_pat:                                   ; d3 = passada, a2 = end. -> d0.w
        tst.w   d3
        bne     tp1
        move.w  #$5555,d0
        rts
tp1:    cmpi.w  #1,d3
        bne     tp2
        move.w  #$AAAA,d0
        rts
tp2:    move.l  a2,d0                   ; passada 2: depende do endereco
        lsr.l   #1,d0
        move.l  d0,d1
        swap    d1
        eor.w   d1,d0
        rts

t_report:                                ; d0 = esperado, -2(a2) = lido
        addq.l  #1,d6
        cmpi.l  #16,d6
        bhi     tr_x
        move.w  d0,-(sp)
        move.w  -2(a2),-(sp)
        lea     m_terr(pc),a1
        bsr     puts
        move.l  a2,d0
        subq.l  #2,d0
        bsr     hexl
        lea     m_texp(pc),a1
        bsr     puts
        move.w  2(sp),d0
        bsr     hexw
        lea     m_tgot(pc),a1
        bsr     puts
        move.w  (sp),d0
        bsr     hexw
        bsr     crlf
        addq.l  #4,sp
tr_x:   rts


ct_tet: jsr     TETRIS
        bra     restart

; ---- B : EhBASIC (ROM em $F84000) ; C : CP/M-68K (ROM em $F88000) -----------
cmd_b:
        move.w  #$2700,sr
        movea.l #$1F00,sp
        move.l  #$F84000,d0
        jmp     BKSYS                   ; v2.8: BASIC esta no banco 1 (nao volta)
cmd_c:
        move.w  #$2700,sr
        movea.l #$1F00,sp
        move.l  #$F88000,d0
        jmp     BKSYS                   ; v2.8: CP/M esta no banco 1

; ---- M ini fim dest : copia memoria (trata sobreposicao) ----------------------
cmd_m:
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        move.l  d0,d4
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        move.l  d0,d5
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        move.l  d0,d3
        cmp.l   d4,d5
        blo     cmd_err
        cmpi.l  #RAMUSER,d3
        blo     t_prot
        movea.l d4,a2
        movea.l d3,a3
        cmp.l   d4,d3
        bls     cm_fw                   ; destino <= origem: copia para a frente
        cmp.l   d5,d3
        bhi     cm_fw                   ; destino depois do fim: sem sobreposicao
        move.l  d5,d0
        sub.l   d4,d0
        addq.l  #1,d0                   ; d0 = tamanho
        adda.l  d0,a2
        adda.l  d0,a3
        moveq   #0,d6
cm_bk:  move.b  -(a2),-(a3)
        addq.b  #1,d6
        bne     cm_b2
        bsr     strobe
cm_b2:  cmp.l   a2,d4
        bne     cm_bk
        bra     cm_ok
cm_fw:  moveq   #0,d6
cm_f1:  move.b  (a2)+,(a3)+
        addq.b  #1,d6
        bne     cm_f2
        bsr     strobe
cm_f2:  cmp.l   a2,d5
        bhs     cm_f1
cm_ok:  lea     m_ok(pc),a1
        bsr     puts
        bra     main_loop

; ---- V ini fim outro : compara dois blocos, lista ate 16 diferencas ----------
cmd_v:
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        move.l  d0,d4
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        move.l  d0,d5
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        movea.l d0,a3
        cmp.l   d4,d5
        blo     cmd_err
        movea.l d4,a2
        moveq   #0,d6                   ; numero de diferencas
        moveq   #0,d2
cv_l:   move.b  (a2),d0
        cmp.b   (a3),d0
        beq     cv_n
        addq.l  #1,d6
        cmpi.l  #16,d6
        bhi     cv_n
        move.l  a2,d0
        bsr     hexl
        move.b  #58,d0
        bsr     putc
        move.b  (a2),d0
        bsr     hexb
        move.b  #32,d0
        bsr     putc
        move.l  a3,d0
        bsr     hexl
        move.b  #58,d0
        bsr     putc
        move.b  (a3),d0
        bsr     hexb
        bsr     crlf
cv_n:   addq.l  #1,a2
        addq.l  #1,a3
        addq.b  #1,d2
        bne     cv_m
        bsr     strobe
cv_m:   cmp.l   a2,d5
        bhs     cv_l
        tst.l   d6
        bne     cv_bad
        lea     m_same(pc),a1
        bsr     puts
        bra     main_loop
cv_bad: lea     m_diff(pc),a1
        bsr     puts
        move.l  d6,d0
        bsr     hexl
        bsr     crlf
        bra     main_loop

; ---- S ini fim b [b b b b b b b] : procura sequencia de bytes (ate 8) ---------
cmd_s:
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        move.l  d0,d4
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        move.l  d0,d5
        lea     $0420,a6                ; padrao (ate 8 bytes) em $0420
        moveq   #0,d3                   ; d3 = tamanho do padrao
cs_p:   bsr     gethex
        tst.l   d1
        beq     cs_pd
        cmpi.w  #8,d3
        bhs     cs_pd
        move.b  d0,(a6)+
        addq.w  #1,d3
        bra     cs_p
cs_pd:  tst.w   d3
        beq     cmd_err
        cmp.l   d4,d5
        blo     cmd_err
        movea.l d4,a2
        moveq   #0,d6                   ; achados
        moveq   #0,d2
cs_l:   movea.l a2,a5
        lea     $0420,a4
        move.w  d3,d0
        subq.w  #1,d0
cs_c:   move.b  (a5)+,d1
        cmp.b   (a4)+,d1
        bne     cs_no
        dbra    d0,cs_c
        move.l  a2,d0                   ; achou
        bsr     hexl
        bsr     crlf
        addq.l  #1,d6
        cmpi.l  #32,d6
        bhs     cs_end
cs_no:  addq.l  #1,a2
        addq.b  #1,d2
        bne     cs_m
        bsr     strobe
cs_m:   cmp.l   a2,d5
        bhs     cs_l
cs_end: tst.l   d6
        bne     main_loop
        lea     m_none(pc),a1
        bsr     puts
        bra     main_loop

; ---- W ini fim : despeja a memoria como S-records S2 (para salvar no PC) --------
cmd_w:
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        move.l  d0,d4
        bsr     gethex
        tst.l   d1
        beq     cmd_err
        move.l  d0,d5
        cmp.l   d4,d5
        blo     cmd_err
cw_l:   move.l  d5,d2
        sub.l   d4,d2
        addq.l  #1,d2                   ; restante
        cmpi.l  #16,d2
        bls     cw_n
        moveq   #16,d2
cw_n:   move.b  #'S',d0
        bsr     putc
        move.b  #'2',d0
        bsr     putc
        move.l  d2,d3
        addq.b  #4,d3                   ; contador = dados + 3 (endereco) + 1 (checksum)
        move.b  d3,d7
        move.b  d3,d0
        bsr     hexb
        move.l  d4,d0
        swap    d0
        add.b   d0,d7
        bsr     hexb
        move.l  d4,d0
        lsr.l   #8,d0
        add.b   d0,d7
        bsr     hexb
        move.l  d4,d0
        add.b   d0,d7
        bsr     hexb
        movea.l d4,a2
        subq.w  #1,d2
cw_b:   move.b  (a2)+,d0
        add.b   d0,d7
        bsr     hexb
        dbra    d2,cw_b
        move.b  d7,d0
        not.b   d0
        bsr     hexb
        bsr     crlf
        move.l  a2,d4
        cmp.l   d4,d5
        bhs     cw_l
        lea     m_s8(pc),a1
        bsr     puts
        bra     main_loop

; ---- G [end] : executa (JSR); o programa volta com RTS --------------------
cmd_g:
        bsr     gethex
        tst.l   d1
        bne     cg_have
        move.l  ENTRY,d0
        beq     cmd_err
cg_have:
        movea.l d0,a2
        lea     m_run(pc),a1
        bsr     puts
        move.l  a2,d0
        bsr     hexl
        bsr     crlf
        jsr     (a2)
        lea     m_ret(pc),a1
        bsr     puts
        bra     restart

; ---- L : carrega S-records (S1/S2/S3 dados; S7/S8/S9 fim) -------------------
cmd_l:
        lea     m_l(pc),a1
        bsr     puts
        clr.l   ENTRY
        clr.w   RECCNT
        clr.l   LSIZE
        moveq   #-1,d0
        move.l  d0,LSTART
l_next: bsr     getrec                  ; linha em BUF, sem eco
        movea.l #BUF,a1
        move.b  (a1)+,d0
        cmpi.b  #'S',d0
        bne     l_err
        moveq   #0,d3
        move.b  (a1)+,d3
        subi.w  #'0',d3                 ; d3 = tipo (0..9)
        bsr     hex2
        tst.l   d0
        bmi     l_err
        move.l  d0,d5                   ; d5 = soma de verificacao
        move.l  d0,d4                   ; d4 = contador n
        moveq   #2,d6                   ; bytes de endereco
        cmpi.w  #2,d3
        beq     l_a3
        cmpi.w  #8,d3
        beq     l_a3
        cmpi.w  #3,d3
        beq     l_a4
        cmpi.w  #7,d3
        beq     l_a4
        bra     l_aok
l_a3:   moveq   #3,d6
        bra     l_aok
l_a4:   moveq   #4,d6
l_aok:  sub.w   d6,d4                   ; bytes de dados + checksum
        subq.w  #1,d4                   ; so dados
        blt     l_err
        moveq   #0,d2                   ; endereco
        subq.w  #1,d6
l_ad:   bsr     hex2
        tst.l   d0
        bmi     l_err
        add.l   d0,d5
        lsl.l   #8,d2
        add.l   d0,d2
        dbra    d6,l_ad
        moveq   #0,d7                   ; d7 = 1 se for registro de dados
        cmpi.w  #1,d3
        blt     l_nodat
        cmpi.w  #3,d3
        bgt     l_nodat
        moveq   #1,d7
        cmpi.l  #RAMUSER,d2
        blo     l_prot
l_nodat:
        movea.l d2,a2
        tst.w   d4
        beq     l_cks
l_db:   bsr     hex2
        tst.l   d0
        bmi     l_err
        add.l   d0,d5
        tst.w   d7
        beq     l_nst
        move.b  d0,(a2)+
l_nst:  subq.w  #1,d4
        bne     l_db
l_cks:  bsr     hex2
        tst.l   d0
        bmi     l_err
        add.l   d0,d5
        andi.l  #$FF,d5
        cmpi.l  #$FF,d5
        bne     l_err
        tst.w   d7
        beq     l_ctl
        addq.w  #1,RECCNT
        move.l  a2,d0                   ; v2.4: acumula tamanho e menor endereco
        sub.l   d2,d0
        add.l   d0,LSIZE
        move.l  LSTART,d0
        cmp.l   d0,d2
        bhs     l_ns
        move.l  d2,LSTART
l_ns:   move.b  #46,d0                  ; '.' = registro de dados gravado
        bsr     putc
        bra     l_next
l_ctl:  cmpi.w  #7,d3
        blt     l_next                  ; S0/S5 etc.: ignora
        cmpi.w  #9,d3
        bgt     l_next
        move.l  d2,ENTRY                ; S7/S8/S9: fim, guarda a entrada
        lea     m_lok(pc),a1
        bsr     puts
        moveq   #0,d0
        move.w  RECCNT,d0
        bsr     hexw
        lea     m_lent(pc),a1
        bsr     puts
        move.l  ENTRY,d0
        bsr     hexl
        jsr     LSTAT                   ; v2.4: inicio= tamanho=
        bsr     crlf
        bra     main_loop
l_prot: bsr     drain
        lea     m_lprot(pc),a1
        bsr     puts
        bra     berr_main
l_err:  bsr     drain
        lea     m_lerr(pc),a1
        bsr     puts
        moveq   #0,d0
        move.w  RECCNT,d0
        bsr     hexw
        bsr     crlf
        bra     berr_main

; ==========================================================================
;  EXCECOES
; ==========================================================================
exc_common:
        move.w  #$2700,sr
        lea     m_exc(pc),a1
        bsr     puts
        move.w  (sp),d0
        bsr     hexb
        move.w  (sp),d2
        cmpi.w  #3,d2
        bgt     exc_g1
        lea     m_eadr(pc),a1           ; erro de barramento/endereco: 14 bytes
        bsr     puts
        move.l  4(sp),d0
        bsr     hexl
        lea     m_epc(pc),a1
        bsr     puts
        move.l  12(sp),d0
        bsr     hexl
        bra     exc_g2
exc_g1: lea     m_epc(pc),a1
        bsr     puts
        move.l  4(sp),d0
        bsr     hexl
exc_g2: bsr     crlf
        bra     berr_rst

; ==========================================================================
;  ROTINAS DE ENTRADA E SAIDA (canal A)
; ==========================================================================
duart_init:
        move.w  #0,$FA0008              ; ACR = 0  (conjunto 1 de baud rates)
        move.w  #0,$FA000A              ; IMR = 0  (sem interrupcoes)
        move.w  #0,$FA001A              ; OPCR = 0 (OP0-OP7 = saidas comuns)
        move.w  #4,$FA001E              ; OP2 (strobe do watchdog) em nivel alto
        movea.l #$FA0000,a3
        bsr     chinit
        movea.l #$FA0010,a3
        bsr     chinit
        ; canal A a 57600 bps pelo timer (115200/N com N=2); canal B fica em 9600
        move.w  #$60,$FA0008            ; ACR: timer, clock = cristal 3,6864 MHz
        move.w  #0,$FA000C              ; CTUR
        move.w  #2,$FA000E              ; CTLR = 2  -> 57600 bps
        tst.b   $FA001F                 ; inicia o timer
        move.w  #$DD,$FA0002            ; CSRA: RX e TX pelo timer
        rts
chinit:                                  ; a3 = base do canal (A=$FA0000, B=$FA0010)
        move.w  #$1A,4(a3)              ; CR: desliga TX/RX, ponteiro MR -> MR1
        move.w  #$13,0(a3)              ; MR1: 8 bits, sem paridade
        move.w  #$07,0(a3)              ; MR2: 1 stop bit
        move.w  #$BB,2(a3)              ; CSR: 9600 bps (cristal 3,6864 MHz)
        move.w  #$20,4(a3)              ; CR: reset receptor
        move.w  #$30,4(a3)              ; CR: reset transmissor
        move.w  #$05,4(a3)              ; CR: habilita TX e RX
        move.w  #$40,4(a3)              ; CR: reset erros
        rts

strobe:                                  ; pulso baixo em OP2 (DS1232)
        move.l  d7,-(sp)                ; v2.7: d7 inteiro (antes so a palavra baixa)
        move.w  #4,DUART_ROPR
        move.w  #4,DUART_SOPR
        moveq   #19,d7
st_d:   dbra    d7,st_d
        move.w  #4,DUART_ROPR
        move.l  (sp)+,d7
        rts

putc:                                    ; d0.b = caractere
        bsr     strobe
pc_w:   btst    #2,DUART_SRA            ; espera TxRDY
        beq     pc_w
        move.w  d0,DUART_THRA
        rts

getc:                                    ; -> d0.b (espera, alimenta o watchdog)
        bsr     strobe
        btst    #0,DUART_SRA            ; RxRDY?
        beq     getc
        move.b  DUART_RHRA,d0
        rts

puts:                                    ; a1 = texto terminado em 0
        move.b  (a1)+,d0
        beq     puts_x
        bsr     putc
        bra     puts
puts_x: rts

crlf:
        moveq   #13,d0
        bsr     putc
        moveq   #10,d0
        bsr     putc
        rts

hexb:                                    ; d0.b em hexadecimal (2 digitos)
        move.l  d1,-(sp)
        moveq   #2,d1
        bsr     hexn
        move.l  (sp)+,d1
        rts
hexw:
        move.l  d1,-(sp)
        moveq   #4,d1
        bsr     hexn
        move.l  (sp)+,d1
        rts
hexl:
        move.l  d1,-(sp)
        moveq   #8,d1
        bsr     hexn
        move.l  (sp)+,d1
        rts
hexn:                                    ; d0 = valor, d1 = no. de digitos (1..8)
        movem.l d0-d3,-(sp)
        move.l  d0,d2
        move.l  d1,d3
        moveq   #8,d0
        sub.l   d3,d0
        lsl.l   #2,d0
        rol.l   d0,d2                   ; alinha o digito mais significativo
        subq.w  #1,d3
hx_l:   rol.l   #4,d2
        move.b  d2,d0
        andi.b  #$0F,d0
        cmpi.b  #9,d0
        ble     hx_d
        addq.b  #7,d0
hx_d:   addi.b  #'0',d0
        bsr     putc
        dbra    d3,hx_l
        movem.l (sp)+,d0-d3
        rts

idle_hook:                               ; espera RxRDY chamando o tick do PER1 ($F8800A) se o modulo existir
        movem.l d0-d7/a0-a6,-(sp)
        move.l  $1714,$1710              ; reinicia o contador de silencio do relogio (RLF -> RLC)
ih_l:   bsr     strobe
        btst    #0,DUART_SRA
        bne     ih_x
        cmpi.l  #$50455231,$F88000
        bne     ih_l
        jsr     $F8800A
        bra     ih_l
ih_x:   movem.l (sp)+,d0-d7/a0-a6
        rts

getline:                                 ; le uma linha editavel em BUF (com eco)
        movea.l #BUF,a1
        moveq   #0,d2
gl_l:   tst.w   d2
        bne     gl_g
        bsr     idle_hook                ; v2.9: so com a linha vazia (nada digitado): relogio no LCD (PER1+10)
gl_g:   bsr     getc
        cmpi.b  #13,d0
        beq     gl_done
        cmpi.b  #8,d0
        beq     gl_bs
        cmpi.b  #127,d0
        beq     gl_bs
        cmpi.b  #32,d0
        blt     gl_l                    ; ignora LF e outros controles
        cmpi.w  #78,d2
        bge     gl_l
        move.b  d0,(a1)+
        addq.w  #1,d2
        bsr     putc
        bra     gl_l
gl_bs:  tst.w   d2
        beq     gl_l
        subq.l  #1,a1
        subq.w  #1,d2
        moveq   #8,d0
        bsr     putc
        moveq   #32,d0
        bsr     putc
        moveq   #8,d0
        bsr     putc
        bra     gl_l
gl_done:
        clr.b   (a1)
        bsr     crlf
        rts

getrec:                                  ; linha de S-record em BUF, sem eco
        movea.l #BUF,a1
        moveq   #0,d2
gr_l:   bsr     getc
        cmpi.b  #13,d0
        beq     gr_e
        cmpi.b  #10,d0
        beq     gr_e
        cmpi.w  #250,d2
        bhs     gr_l
        move.b  d0,(a1)+
        addq.w  #1,d2
        bra     gr_l
gr_e:   tst.w   d2
        beq     gr_l                    ; ignora linhas vazias
        clr.b   (a1)
        rts

drain:                                   ; descarta a entrada ate 0,4 s de silencio
        move.l  #8000,d2
dr_l:   btst    #0,DUART_SRA
        beq     dr_n
        move.b  DUART_RHRA,d0
        move.l  #8000,d2
        bra     dr_l
dr_n:   bsr     strobe
        subq.l  #1,d2
        bne     dr_l
        rts

; ---- utilitarios de texto ---------------------------------------------------
upper:                                   ; d0.b minuscula -> maiuscula
        cmpi.b  #'a',d0
        blt     up_x
        cmpi.b  #'z',d0
        bgt     up_x
        subi.b  #32,d0
up_x:   rts

skipsp:                                  ; a1 avanca sobre espacos
        cmpi.b  #32,(a1)
        bne     ss_x
        addq.l  #1,a1
        bra     skipsp
ss_x:   rts

gethex:                                  ; le numero hex em (a1): d0 = valor, d1 = no. digitos
        bsr     skipsp
        moveq   #0,d0
        moveq   #0,d1
gh_l:   move.b  (a1),d2
        cmpi.b  #'0',d2
        blt     gh_x
        cmpi.b  #'9',d2
        ble     gh_dg
        andi.b  #$DF,d2                 ; minuscula -> maiuscula
        cmpi.b  #'A',d2
        blt     gh_x
        cmpi.b  #'F',d2
        bgt     gh_x
        subq.b  #7,d2
gh_dg:  subi.b  #'0',d2
        andi.l  #$0F,d2
        lsl.l   #4,d0
        add.l   d2,d0
        addq.l  #1,d1
        addq.l  #1,a1
        bra     gh_l
gh_x:   rts

hex1:                                    ; (a1)+ -> d0 = 0..15, ou -1 se invalido
        moveq   #0,d0
        move.b  (a1)+,d0
        cmpi.b  #'0',d0
        blt     h1_bad
        cmpi.b  #'9',d0
        ble     h1_ok
        andi.b  #$DF,d0
        cmpi.b  #'A',d0
        blt     h1_bad
        cmpi.b  #'F',d0
        bgt     h1_bad
        subq.b  #7,d0
h1_ok:  subi.b  #'0',d0
        rts
h1_bad: moveq   #-1,d0
        rts

hex2:                                    ; (a1)+ 2 digitos -> d0 = byte, ou -1
        bsr     hex1
        tst.l   d0
        bmi     h2_x
        move.l  d0,d1
        bsr     hex1
        tst.l   d0
        bmi     h2_x
        lsl.l   #4,d1
        add.l   d1,d0
        andi.l  #$FF,d0
        rts
h2_x:   moveq   #-1,d0
        rts

; ==========================================================================
;  TEXTOS
; ==========================================================================
; m_cls = ESC [ 2 J  ESC [ H : limpa a tela e leva o cursor ao canto
m_cls:    dc.b 27,91,50,74,27,91,72,0
m_banner: dc.b 13,10,"Digite ? para ajuda.",13,10,0
m_menu:   dc.b 13,10,13,10
          dc.b "PARAGON 50 - Monitor 68000 v2.8 (Tabajara Labs) 57600 bps - {{DATE}}",13,10
          dc.b "====================",13,10
          dc.b "Bootloader:",13,10
          dc.b "   [B]asic        (banco 1)",13,10
          dc.b "   [C]P/M 68K     (banco 1)",13,10
          dc.b "   [A]plicativos (bancos da flash)",13,10
          dc.b "   [R]ecuperacao (cartao SD)",13,10
          dc.b "   [M]onitor",13,10
          dc.b "   [T]etris",13,10
          dc.b "====================",13,10
          dc.b "Ou aguarde 5 segundos para entrar no Monitor",13,10,0
m_same:   dc.b "IGUAIS",13,10,0
m_diff:   dc.b "DIFERENCAS: ",0
m_none:   dc.b "nao encontrado",13,10,0
m_s8:     dc.b "S804000000FB",13,10,0
m_prompt: dc.b "> ",0
m_err:    dc.b "?? comando ou argumento invalido (? = ajuda)",13,10,0
m_ok:     dc.b "OK",13,10,0
m_info:   dc.b "ROM v2.8 IP=",0
m_iram:   dc.b "RAM:  $000000-$",0
m_ikb:    dc.b "  (",0
m_ikb2:   dc.b " KB, detectada no reset)",13,10,0
m_ifree:  dc.b "Livre para programas: $002000-$",0
m_irom:   dc.b "ROM:  $F80000-$F9FFFF  (monitor, Tetris, bancos, recuperacao SD, modulo estendido)",13,10
          dc.b "DUART 68681: $FA0000   (console canal A, 57600 bps)",13,10,0
m_help:   dc.b 13,10,"Monitor PARAGON 50 v2.8 (hex). D P F M V S T G L W B C I ?",13,10
          dc.b "(ajuda completa no modulo estendido: ? ou H nome)",13,10,0
m_tok:    dc.b "RAM OK",13,10,0
m_tbad:   dc.b "RAM COM ERROS, total=",0
m_terr:   dc.b "ERRO em ",0
m_texp:   dc.b " esperado=",0
m_tgot:   dc.b " lido=",0
m_prot:   dc.b "Endereco protegido (< $2000: vetores, variaveis e pilha)",13,10,0
m_run:    dc.b "Executando em ",0
m_ret:    dc.b "Retornou ao monitor.",13,10,0
m_l:      dc.b "Envie o arquivo S-record (pontos = registros gravados)...",13,10,0
m_lok:    dc.b 13,10,"OK registros=",0
m_lent:   dc.b " entrada=",0
m_lerr:   dc.b 13,10,"ERRO no S-record, registros gravados=",0
m_lprot:  dc.b 13,10,"ERRO: endereco < $2000 protegido",13,10,0
m_exc:    dc.b 13,10,"*** EXCECAO vetor=",0
m_eadr:   dc.b " end.=",0
m_epc:    dc.b " PC=",0
          dc.b 0
