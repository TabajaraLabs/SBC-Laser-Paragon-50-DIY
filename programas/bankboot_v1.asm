; ==========================================================================
;  BANKBOOT v1 - "boot" a partir de outro banco da flash (PARAGON 50)
;  Carregar com L e executar com G 2000.  Numero do banco: P 3000 00 0n (n = 0..7).
;  Roda na RAM (a ROM muda de lugar quando o banco troca). Seleciona o banco em
;  $FC0000 e entra na ROM dele como num reset: SP = longo em $F80000, PC = longo em $F80004.
;  NAO volta ao monitor do banco 0: para voltar, aperte o RESET da placa (zera o registrador).
; ==========================================================================
BANKV   equ $3000
BANKR   equ $FC0000
        org $2000
start:  move.w  #$2700,sr
        move.w  BANKV,d0
        andi.w  #7,d0
        move.w  d0,BANKR
        move.l  $F80000,d1
        movea.l d1,sp
        move.l  $F80004,d2
        movea.l d2,a0
        jmp     (a0)
