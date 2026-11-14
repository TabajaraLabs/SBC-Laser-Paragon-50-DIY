#!/usr/bin/env python3
"""build_forth_v2.py asm prelude.fs saida_bank_raw.bin
Compila o prelude dentro do eForth no emulador e CONGELA o dicionario na imagem do banco (stub de copia + segmentos)."""
import sys, struct
sys.path.insert(0, '.')
from m68kasm_v3 import Asm
import emu68k
asmf, prel, outf = sys.argv[1:4]
a = Asm(); a.assemble(open(asmf).read())
cpu = emu68k.CPU()
for o, b in a.segs: cpu.mem[o:o+len(b)] = b
cpu.a[7] = 0x1F00; cpu.pc = a.sym['ORIG']
text = ''.join(l + '\r' for l in open(prel).read().split('\n') if l.strip())
cpu.rx = list(text.encode('latin-1'))
n = 0
try:
    while cpu.rx and n < 200_000_000: cpu.step(); n += 1
    for _ in range(400_000): cpu.step()
except Exception as e:
    print('EXCECAO', e, '%06X' % cpu.pc)
out = bytes(cpu.tx).decode('latin-1')
print(out[-1500:])
errs = out.count('?')
UPP = a.sym['UPP']; UZ = a.sym['UZERO']; ULAST = a.sym['ULAST']
rd = lambda ad: struct.unpack('>I', bytes(cpu.mem[ad:ad+4]))[0]
cp, np_, last = rd(UPP + ULAST - UZ - 12), rd(UPP + ULAST - UZ - 8), rd(UPP + ULAST - UZ - 4)
print('CP=$%X NP=$%X LAST=$%X  passos=%d  "?"=%d' % (cp, np_, last, n, errs))
CODEE = a.sym['CODEE']; NAMEE = a.sym['NAMEE']
C68 = a.sym['COLD68']
seg0 = bytearray(cpu.mem[C68:ULAST])
seg0[-12:] = struct.pack('>III', cp, np_, last)
cp_a = (cp + 3) & ~3
segs = [(C68, bytes(seg0)), (CODEE, bytes(cpu.mem[CODEE:cp_a])), (np_, bytes(cpu.mem[np_:NAMEE]))]
BASE, STUB, DATA = 0xF80000, 0xF80800, 0xF80900
placed = []; off = DATA
for dst, data in segs:
    data = data + b'\0' * (-len(data) % 4); placed.append((off, dst, data)); off += len(data)
code = ['        org $%X' % STUB, '        move.w #$2700,sr']
for src, dst, data in placed:
    code += ['        movea.l #$%X,a0' % src, '        movea.l #$%X,a1' % dst, '        move.l #%d,d0' % (len(data)//4),
             'cp%X: move.l (a0)+,(a1)+' % src, '        subq.l #1,d0', '        bne cp%X' % src]
code += ['        jmp $%X' % a.sym['ORIG']]
stub = Asm().assemble('\n'.join(code) + '\n')
assert len(stub) < DATA - STUB and off - BASE <= 0x20000
img = bytearray(b'\xff' * 0x20000)
img[0:8] = struct.pack('>II', 0x1F00, STUB)
img[STUB-BASE:STUB-BASE+len(stub)] = stub
for src, dst, data in placed: img[src-BASE:src-BASE+len(data)] = data
open(outf, 'wb').write(img)
print('imagem: %d bytes usados' % (off - BASE))
