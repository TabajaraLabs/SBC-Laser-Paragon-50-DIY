; Programa de teste para o comando L do monitor: imprime uma mensagem e volta.
        org $2000
start:  lea     msg(pc),a1
        jsr     $F8080C             ; servico puts do monitor
        moveq   #7,d3               ; conta de 7 a 0 usando hexb
cnt:    move.b  d3,d0
        jsr     $F80812             ; servico hexb
        moveq   #32,d0
        jsr     $F80800             ; servico putc
        dbra    d3,cnt
        jsr     $F80824             ; servico crlf
        rts
msg:    dc.b 13,10,"Ola! Este programa foi carregado pela serial via S-record.",13,10,0
