#!/bin/bash
# build_ext27.sh : compila o modulo estendido (ext_v27.c + ext_a.s) -> ext_v27.bin (64 KB em $F90000)
set -e
D=/tmp/claude-0/-home-claude/93617e9f-8b52-5410-9afb-5edd9ad3194e/scratchpad
H=$(pwd)
mkdir -p $D/ext27/ext/out; cp $H/ext_v27.c $D/ext27/ext/ext.c; cp $H/ext_a.s $D/ext27/ext/ext_a.s
[ -f $D/ext27/dis.c ] || cp $D/v22/dis.c $D/v22/asm.c $D/ext27/
cd $D/cpm
CC_OPT=Oz ./cc.sh $D/ext27/ext/ext.c $D/ext27/ext/out/ext.S
python3 asm68k.py --flagfix --idxlong --ram 0x0900 -b 0xF90000 -o $D/ext27/ext/out/ext.bin -m $D/ext27/ext/out/ext.map $D/ext27/ext/ext_a.s $D/ext27/ext/out/ext.S rtl.s
cp $D/ext27/ext/out/ext.bin $H/ext_v27.bin
