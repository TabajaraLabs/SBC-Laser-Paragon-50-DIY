#!/bin/bash
# build.sh [org] [tpa_top]  -> build/cpm.bin / build/cpm.map / build/cpm.lst
cd "$(dirname "$0")"
ORG=${1:-0x2000}; TOP=${2:-0x10000UL}
# ROM=1: codigo em ROM em $ORG, dados em RAM a partir de $RAMBASE (padrao $2000), saida build/cpm_rom.bin
RAMBASE=${RAMBASE:-0x2000}
if [ -n "$ROM" ]; then export CC_OPT=Oz; fi
S=/home/claude/roman65536/cp-m-m68k
mkdir -p build
# patch: TPA vem da tabela de memoria do BIOS (func 18) em vez de constantes fixas
cp $S/*.h build/ 2>/dev/null
sed -e 's|tpa_lt = tpa_lp = (char \*) 0xff008000;|tpa_lt = tpa_lp = (char *) *(long *)((char *)segp + 2);|' \
    -e 's|tpa_ht = tpa_hp = tpa_lp + 0x100000;|tpa_ht = tpa_hp = tpa_lp + *(long *)((char *)segp + 6);|' $S/bdosmisc.c > build/bdosmisc_p.c
grep -q 'segp + 6' build/bdosmisc_p.c || { echo patch falhou; exit 1; }
for f in bdosmain bdosrw conbdos dskutil fileio iosys ccp; do ./cc.sh $S/$f.c build/$f.S || exit 1; done 2>&1 | grep -v '^launder'
./cc.sh build/bdosmisc_p.c build/bdosmisc.S -I$S 2>&1 | grep -v '^launder'
./cc.sh ${BIOSC:-bios.c} build/bios.S -DTPA_TOP=$TOP 2>&1 | grep -v '^launder'
for f in bdosif ccpbdos ccpif ccpload exceptn filetyps pgmld2 stack; do cp $S/$f.s build/g_$f.s; done
# LLVM devolve ponteiros em A0; a cola BIOS da DRI so devolve em D0 -> copia D0 para A0 antes dos rts
python3 - <<'PY'
import re
p='build/g_bdosif.s'; t=open(p).read()
t=t.replace("\tmove.l (%sp)+,%d2\n\trts","\tmove.l (%sp)+,%d2\n\tmove.l %d0,%a0\n\trts")
t=t.replace("\tmovem.l\t(%sp)+,%d3-%d7/%a3-%a6\n\trts","\tmovem.l\t(%sp)+,%d3-%d7/%a3-%a6\n\tmove.l %d0,%a0\n\trts")
open(p,'w').write(t)
print('glue a0 patches:', t.count('move.l %d0,%a0'))
PY
if [ -n "$ROM" ]; then
python3 -I asm68k.py --flagfix --idxlong --ram $RAMBASE -b $ORG -o build/cpm_rom.bin -m build/cpm_rom.map --list build/cpm_rom.lst \
  rom0.s build/g_ccpif.s build/bdosmain.S build/bdosmisc.S build/bdosrw.S build/conbdos.S build/dskutil.S build/fileio.S build/iosys.S build/ccp.S build/bios.S \
  build/g_bdosif.s build/g_ccpbdos.s build/g_ccpload.s build/g_exceptn.s build/g_filetyps.s build/g_pgmld2.s build/g_stack.s bios_a.s sd_blob.s rtl.s
exit
fi
python3 -I asm68k.py --flagfix -b $ORG -o build/cpm.bin -m build/cpm.map --list build/cpm.lst \
  build/g_ccpif.s build/bdosmain.S build/bdosmisc.S build/bdosrw.S build/conbdos.S build/dskutil.S build/fileio.S build/iosys.S build/ccp.S build/bios.S \
  build/g_bdosif.s build/g_ccpbdos.s build/g_ccpload.s build/g_exceptn.s build/g_filetyps.s build/g_pgmld2.s build/g_stack.s bios_a.s sd_blob.s rtl.s
