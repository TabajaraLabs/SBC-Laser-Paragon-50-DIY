| ext_a.s - cola em assembly do modulo v2 do monitor (PARAGON 50). Colocado em $F90000.
	.globl	ext_hdr
	.globl	ext_entry
	.globl	x_putc
	.globl	x_getc
	.globl	x_puts
	.globl	x_strobe
	.globl	x_getline
	.globl	x_kbhit
	.globl	dbg_resume
	.globl	dbg_vecs
	.text
ext_hdr:
	.long	0x45585431
	jmp	ext_entry
| chamada pelo monitor: d0 = letra do comando (maiuscula), a1 = argumentos. Devolve d0 = 0 se tratou.
ext_entry:
	movem.l	%d2-%d7/%a2-%a6,-(%sp)
	move.l	%a1,-(%sp)
	move.l	%d0,-(%sp)
	jsr	ext_main
	addq.l	#8,%sp
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
x_puts:
	move.l	4(%sp),%a1
	jsr	0xF8080C
	rts
x_strobe:
	jsr	0xF8082A
	rts
x_getline:
	move.l	%d2,-(%sp)
	jsr	0xF80836
	move.l	(%sp)+,%d2
	move.l	#0x500,%d0
	move.l	%d0,%a0		| ponteiros voltam em a0 no ABI do LLVM m68k
	rts
x_kbhit:
	moveq	#0,%d0
	btst	#0,0xFA0003
	beq	kb_no
	moveq	#1,%d0
kb_no:
	rts

| ---- depurador -------------------------------------------------------
| estado em $0800: d[8] +0, a0-a6 +0x20, sp +0x3C, pc +0x40, sr +0x44, vec +0x46, fa +0x48, monsp +0x4C
dbg_vecs:
	tst.l	4(%sp)
	beq	dv_off
	lea	dbg_vtab,%a0
	bra	dv_go
dv_off:
	movea.l	#0xF80008,%a0
dv_go:
	movea.l	#8,%a1
	moveq	#9,%d1
dv_l:
	move.l	(%a0)+,(%a1)+
	dbra	%d1,dv_l
	rts

dbg_resume:
	movem.l	%d2-%d7/%a2-%a6,-(%sp)
	move.l	%sp,0x84C
	movea.l	0x83C,%a1
	move.l	0x840,-(%a1)
	move.w	0x844,-(%a1)
	movea.l	%a1,%sp
	movem.l	0x800,%d0-%d7
	movem.l	0x820,%a0-%a6
	rte

dbg_common:
	movem.l	%d0-%d7,0x800
	movem.l	%a0-%a6,0x820
	cmpi.w	#3,0x846
	ble	dc_g0
	move.w	(%sp),0x844
	move.l	2(%sp),0x840
	lea	6(%sp),%a0
	bra	dc_fin
dc_g0:
	move.l	2(%sp),0x848
	move.w	8(%sp),0x844
	move.l	10(%sp),0x840
	lea	14(%sp),%a0
dc_fin:
	move.l	%a0,0x83C
	movea.l	0x84C,%sp
	movem.l	(%sp)+,%d2-%d7/%a2-%a6
	move.w	#0x2700,%sr
	moveq	#0,%d0
	move.w	0x846,%d0
	rts

dbg_v2:  move.w #2,0x846
	bra	dbg_common
dbg_v3:  move.w #3,0x846
	bra	dbg_common
dbg_v4:  move.w #4,0x846
	bra	dbg_common
dbg_v5:  move.w #5,0x846
	bra	dbg_common
dbg_v6:  move.w #6,0x846
	bra	dbg_common
dbg_v7:  move.w #7,0x846
	bra	dbg_common
dbg_v8:  move.w #8,0x846
	bra	dbg_common
dbg_v9:  move.w #9,0x846
	bra	dbg_common
dbg_v10: move.w #10,0x846
	bra	dbg_common
dbg_v11: move.w #11,0x846
	bra	dbg_common

dbg_vtab:
	.long	dbg_v2,dbg_v3,dbg_v4,dbg_v5,dbg_v6,dbg_v7,dbg_v8,dbg_v9,dbg_v10,dbg_v11
