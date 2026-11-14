#!/usr/bin/env python3
"""mkbank_eforth_v1.py - monta a imagem de banco (128 KB) do eForth: vetores SP/PC, stub de copia para a RAM,
segmentos do eForth. Depois use mkbanco_v2.py --tipo 1 para por o cabecalho "AB".
Uso: mkbank_eforth_v1.py ef_paragon_rom.asm saida.bin"""
import sys, struct
sys.path.insert(0, '.')
from m68kasm_v3 import Asm
a = Asm(); a.assemble(open(sys.argv[1]).read())
BASE, STUB, DATA = 0xF80000, 0xF80800, 0xF80900
segs = []; off = DATA
for dst, data in a.segs:
    data = data + b'\0' * (-len(data) % 4)
    segs.append((off, dst, data)); off += len(data)
code = ['        org $%X' % STUB, '        move.w #$2700,sr']
for src, dst, data in segs:
    code += ['        movea.l #$%X,a0' % src, '        movea.l #$%X,a1' % dst, '        move.l #%d,d0' % (len(data)//4),
             'cp%X: move.l (a0)+,(a1)+' % src, '        subq.l #1,d0', '        bne cp%X' % src]
code += ['        jmp $%X' % a.sym['ORIG']]
s = Asm(); stub = s.assemble('\n'.join(code) + '\n')
assert len(stub) < DATA - STUB
img = bytearray(b'\xff' * 0x20000)
img[0:8] = struct.pack('>II', 0x1F00, STUB)
img[STUB-BASE:STUB-BASE+len(stub)] = stub
for src, dst, data in segs: img[src-BASE:src-BASE+len(data)] = data
assert off - BASE <= 0x20000
open(sys.argv[2], 'wb').write(img)
print('imagem: %d bytes usados, stub %d bytes, entrada ORIG=$%X' % (off - BASE, len(stub), a.sym['ORIG']))
