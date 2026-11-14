#!/usr/bin/env python3
"""mkbanco_v2.py - coloca o cabecalho de banco (64 bytes, "AB") em $F807C0 (offset $7C0) de uma imagem de 128 KB.
 (a ROM v2.3.1 usa o banco inteiro; $F804F8-$F807FF e a area livre depois dos vetores)
Uso: mkbanco_v2.py entrada.bin saida.bin NOME VERSAO [--tipo 0|1] [--partida HEX]
 - entrada.bin: imagem em ordem de enderecos a partir de $F80000 (ate 128 KB-64 bytes de dados)
 - tipo 0 (padrao): ROM completa, partida = PC do vetor em +4
 - CRC32 cobre [inicio..$F807BF] + [$F80800..fim] (pula so a area do cabecalho); fim = ultimo byte != $FF
Formato (big-endian) em $F807C0: +0 'AB' | +2 tipo | +4 inicio | +8 fim | +12 partida |
 +16 nome[16] | +32 versao[8] | +40 CRC32 | +44..+63 = $FF"""
import sys, zlib, struct, argparse
ap = argparse.ArgumentParser()
ap.add_argument('entrada'); ap.add_argument('saida'); ap.add_argument('nome'); ap.add_argument('versao')
ap.add_argument('--tipo', type=int, default=0); ap.add_argument('--partida', default=None)
a = ap.parse_args()
BASE, SIZE, HDR, OFF = 0xF80000, 0x20000, 64, 0x7C0
d = bytearray(open(a.entrada, 'rb').read().ljust(SIZE, b'\xff'))
if len(d) != SIZE:
    sys.exit('imagem maior que 128 KB')
if d[OFF:OFF+HDR] != b'\xff' * HDR:
    sys.exit('a area do cabecalho ($F807C0-$F807FF) nao esta livre na imagem')
n = len(bytes(d).rstrip(b'\xff'))
partida = a.partida and int(a.partida, 16) or struct.unpack('>I', bytes(d[4:8]))[0]
crc = zlib.crc32(bytes(d[OFF+HDR:n]), zlib.crc32(bytes(d[:OFF]))) & 0xFFFFFFFF
h = b'AB' + struct.pack('>HIII', a.tipo, BASE, BASE + n - 1, partida)
h += a.nome.encode('ascii')[:16].ljust(16) + a.versao.encode('ascii')[:8].ljust(8)
h += struct.pack('>I', crc)
d[OFF:OFF+HDR] = h.ljust(HDR, b'\xff')
open(a.saida, 'wb').write(d)
print('OK %s: fim $%06X, partida $%08X, CRC32 %08X' % (a.saida, BASE + n - 1, partida, crc))
