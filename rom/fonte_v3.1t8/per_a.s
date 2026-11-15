| per_a.s - cola em assembly do modulo de perifericos PER1 (PARAGON 50). Colocado em $F88000.
	.globl	per_hdr
	.globl	x_putc
	.globl	x_getc
	.globl	x_strobe
	.globl	x_kbhit
	.globl	ext_init
	.text
per_hdr:
	.long	0x50455231		| 'PER1'
	jmp	per_entry
| chamada pelo FLCHK do banco 0: a1 = inicio da linha. Devolve d0 = 1 se a linha era comando do modulo (ja executado), 0 se nao.
per_entry:
	movem.l	%d2-%d7/%a2-%a6,-(%sp)
	move.l	%a1,-(%sp)
	jsr	per_main
	addq.l	#4,%sp
	movem.l	(%sp)+,%d2-%d7/%a2-%a6
	rts
x_putc:
	move.l	4(%sp),%d0
	jsr	0xF80800
	rts
x_getc:
	jsr	0xF80806
	andi.l	#255,%d0
	rts
x_strobe:
	jsr	0xF8082A
	rts
x_kbhit:
	moveq	#0,%d0
	btst	#0,0xFA0003
	beq	kb_no
	moveq	#1,%d0
kb_no:
	rts
| garante que o modulo estendido ($F90000) inicializou seu estado (RAM2 etc.): executa um comando inexistente (d0 = 0)
ext_init:
	movem.l	%d2-%d7/%a2-%a6,-(%sp)
	cmpi.l	#0x45585431,0xF90000
	bne	ei_x
	moveq	#0,%d0
	lea	ei_nul(%pc),%a1
	jsr	0xF90004
ei_x:
	movem.l	(%sp)+,%d2-%d7/%a2-%a6
	rts
ei_nul:	.byte	0,0
	.even
