#!/usr/bin/env python3
"""mksrec_segs_v1.py entrada.asm saida.s19 simbolo_entrada  -> S-record (S2) com todos os segmentos"""
import sys
sys.path.insert(0,'.')
from m68kasm_v3 import Asm
import srec
a=Asm(); a.assemble(open(sys.argv[1]).read())
out=srec.rec(0,0,b"EFORTH",2)
for base,data in a.segs:
    for i in range(0,len(data),16): out+=srec.rec(2,base+i,data[i:i+16],3)
out+=srec.rec(8,a.sym[sys.argv[3].upper()],b"",3)
open(sys.argv[2],'w',newline='').write(out)
print(len(out),'bytes de S-record; entrada $%X'%a.sym[sys.argv[3].upper()])
