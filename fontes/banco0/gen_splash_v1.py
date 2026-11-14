#!/usr/bin/env python3
"""gen_splash_v1.py - rotina de splash do LCD ($F87EE0): limpa o LCD e escreve 2 linhas. Chamada pelo reset do monitor v2.7.
Usa o servico de LCD em $F80614 (lcd_start / lcd_at, convencao C: argumentos na pilha)."""
import sys; sys.path.insert(0,'/home/claude/rom24/v26')
import m68kasm_v3
ORG=0xF87EE0
src="""        org $F87EE0
splash: jsr     $F80614
        lea     s1(pc),a0
        move.l  a0,-(sp)
        clr.l   -(sp)
        clr.l   -(sp)
        jsr     $F80618
        lea     12(sp),sp
        lea     s2(pc),a0
        move.l  a0,-(sp)
        clr.l   -(sp)
        move.l  #1,-(sp)
        jsr     $F80618
        lea     12(sp),sp
        rts
s1:     dc.b    "PARAGON 50  68000   ",0
s2:     dc.b    "Tabajara Labs       ",0
"""
m=m68kasm_v3.Asm(); m.assemble(src); a,b=m.segs[0]; b=bytes(b); assert a==ORG
print('splash: %d bytes em $%X' % (len(b),a)); assert ORG+len(b)<=0xF88000
open('splash_v1.bin','wb').write(b)
