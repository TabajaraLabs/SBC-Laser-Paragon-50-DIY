#!/usr/bin/env python3
"""gen_sdblob_v3.py - extrai do sdfs_v4.asm a camada SD (SPI, init, leitura/escrita de setor) e gera
sd_blob.s (GNU as, para o BIOS do CP/M) com as variaveis na RAM alta ($5F010..).
Entradas (bra.w): sd_init, sd_rd(setor, buf), sd_wr(setor, buf) - convencao C (args na pilha, retorno d0)."""
import sys
sys.path.insert(0,'/home/claude/rom24/v26')
import m68kasm_v3, json
LCDACTV=json.load(open('/home/claude/cpmw/sdb/lcd_sym.json'))['ACTV']
L=open('/home/claude/rom24/v26/sdfs_v4.asm').read().split('\n')
def lab(n): 
    for i,l in enumerate(L):
        if l.startswith(n+':'): return i
    raise KeyError(n)
a=lab('spi_xfer')-1            # ; comentario antes
while not L[a].startswith(';'): a-=1
# ate o fim de sdread_i (rd_f ... rts)
b=lab('rd_f')+3
spi_part=L[lab('spi_xfer'):b]
# remove o desvio para spi_rd e a propria spi_rd (leitura rapida de 1 byte): redundante com o caminho geral de spi_xfer
i0=next(i for i,l in enumerate(spi_part) if 'cmpi.b  #$FF,d0' in l); assert 'beq     spi_rd' in spi_part[i0+1]
del spi_part[i0:i0+2]
j0=next(i for i,l in enumerate(spi_part) if l.startswith('spi_rd:')); j1=next(i for i,l in enumerate(spi_part) if l.startswith('sel:'))
del spi_part[j0:j1]
w0=lab('sdwrite'); w1=lab('fat_flush')
wr_part=L[w0:w1]
# remover o corpo de sdinit duplicado? (sdinit esta dentro de spi_part)
EQ="""LATCH   equ $020018
MPORT   equ $020028
MMASK   equ $1
CSB     equ $5F010
SDHC    equ $5F012
HCSARG  equ $5F014
SARG    equ $5F018
SCRC    equ $5F01C
SECN    equ $5F020
RDST    equ $5F024
WST     equ $5F028
"""
EQ=("LCDACTV equ $%X\n"%LCDACTV)+EQ
ENTRY="""        org $0
sd_init: bra.w  i_init
sd_rd:   bra.w  i_rd
sd_wr:   bra.w  i_wr
i_init:  movem.l d2-d7/a2-a6,-(sp)
        bsr     sdinit
        movem.l (sp)+,d2-d7/a2-a6
        rts
i_rd:   movem.l d2-d7/a2-a6,-(sp)
        move.l  48(sp),SECN
        move.l  52(sp),RDST
        bsr     sdread
        movem.l (sp)+,d2-d7/a2-a6
        rts
i_wr:   movem.l d2-d7/a2-a6,-(sp)
        move.l  48(sp),SECN
        move.l  52(sp),WST
        bsr     sdwrite
        movem.l (sp)+,d2-d7/a2-a6
        rts
actv:   jmp     LCDACTV
actv_off: rts
"""
src=EQ+ENTRY+'\n'.join(spi_part)+'\n'+'\n'.join(wr_part)+'\n'
for bad in ('        move.w  #0,MOUNT\n','        lea     m_fail(pc),a1\n        jsr     PUTS\n','rdsec:  move.l  #SECBUF,RDST\n'):
    assert bad in src, bad
    src=src.replace(bad,'')

def asm(org):
    s=src.replace('org $0','org $%X'%org,1)
    m=m68kasm_v3.Asm(); m.assemble(s); return m
m0=asm(0); m1=asm(0x10000)
b0=bytes(m0.segs[0][1]); b1=bytes(m1.segs[0][1])
assert len(b0)==len(b1)
# posicao independente? diferencas so podem ser 'bra/bsr' relativos (nao mudam); qualquer diferenca = ref absoluta
diff=[i for i in range(len(b0)) if b0[i]!=b1[i]]
print('blob %d bytes; diferencas entre org 0 e org $10000: %d'%(len(b0),len(diff)))
assert not diff, diff[:10]
out=['| sd_blob.s - gerado por gen_sdblob_v3.py (camada SD do driver SDFS, independente de posicao)',
     '\t.text','\t.globl\tsd_init','\t.globl\tsd_rd','\t.globl\tsd_wr']
def emit(lo,hi):
    for i in range(lo,hi,16):
        out.append('\t.byte\t'+','.join('0x%02X'%x for x in b0[i:min(i+16,hi)]))
out.append('sd_init:'); emit(0,4); out.append('sd_rd:'); emit(4,8); out.append('sd_wr:'); emit(8,12); emit(12,len(b0))
open('/home/claude/cpmw/sd_blob.s','w').write('\n'.join(out)+'\n')
open('/home/claude/cpmw/sdb/sd_blob.bin','wb').write(b0)
import json; json.dump({k:v for k,v in m0.sym.items()},open('/home/claude/cpmw/sdb/blob_sym.json','w'))
print('ok')
