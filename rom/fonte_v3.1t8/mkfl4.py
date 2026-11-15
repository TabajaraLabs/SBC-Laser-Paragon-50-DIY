#!/usr/bin/env python3
"""mkfl4.py IMAGEM_128K.bin BANCO [saida.fl4] - acrescenta o rodape de 256 bytes ("FL4", banco, CRC32) para o flash_v4."""
import sys, zlib, struct, os
img=open(sys.argv[1],'rb').read(); bank=int(sys.argv[2]); assert len(img)==131072 and 0<=bank<=7
out=sys.argv[3] if len(sys.argv)>3 else os.path.splitext(sys.argv[1])[0]+'_b%d.fl4'%bank
tr=b'FL4'+bytes([bank])+struct.pack('>I',zlib.crc32(img)&0xFFFFFFFF); tr+=b'\xff'*(256-len(tr))
open(out,'wb').write(img+tr); print(out,'CRC32 %08X'%(zlib.crc32(img)&0xFFFFFFFF))
