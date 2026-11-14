#!/usr/bin/env python3
"""patch_eforth_v2.py - ef_raw.asm -> ef_paragon.asm (remendos PARAGON 50). Uso: patch_eforth_v2.py entrada saida [rom]"""
import sys, re
t = open(sys.argv[1]).read()
def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (a, t.count(a))
    t = t.replace(a, b)
rep("EM equ $00008000", "EM equ $00020000")
rep("COLD68 equ $00001000", "COLD68 equ $00004000")
rep("        ORG COLDD\n        JMP ORIG\n", "")
# ORIG guarda o SP do monitor para o BYE
rep("ORIG:\n        LEA.L SPP,SP", "ORIG:\n        MOVE.L SP,$3F00\n        MOVE.W #$2700,SR\n        LEA.L SPP,SP")
# BYE: volta ao monitor (G = JSR)
ROM = len(sys.argv) > 3 and sys.argv[3] == 'rom'
if ROM:   # BYE em modo banco: volta ao banco 0 e reinicia a ROM de la (roda da RAM, entao e seguro trocar o banco)
    rep("        MOVE.B #229,D7\n        TRAP #14\n", "        MOVE.W #$2700,SR\n        MOVE.W #0,$FC0000\n        MOVEA.L $F80000,SP\n        MOVEA.L $F80004,A0\n        JMP (A0)\n")
else:     # BYE em modo RAM (L/G): volta ao monitor
    rep("        MOVE.B #229,D7\n        TRAP #14\n", "        MOVEA.L $3F00,SP\n        RTS\n")
# DUART do PARAGON 50
rep("$00010040", "$FA0003", 2)
rep("$00010042", "$FA0007", 2)
rep("TXSTO2:\n        BTST #1,$FA0003", "TXSTO2:\n        BTST #2,$FA0003")
open(sys.argv[2], 'w').write(t)
