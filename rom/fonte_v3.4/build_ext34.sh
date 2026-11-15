#!/bin/bash
# build_ext34.sh : compila o modulo estendido (ext_v34.c + ext_a.s) -> ext_v34.bin (64 KB em $F90000)
set -e
D=/tmp/claude-0/-home-claude/93617e9f-8b52-5410-9afb-5edd9ad3194e/scratchpad
H=$(pwd)
mkdir -p $D/ext34/ext/out; cp $H/ext_v34.c $D/ext34/ext/ext.c; cp $H/ext_a.s $D/ext34/ext/ext_a.s
[ -f $D/ext34/dis.c ] || cp $D/v22/dis.c $D/v22/asm.c $D/ext34/
cd $D/cpm
CC_OPT=Oz ./cc.sh $D/ext34/ext/ext.c $D/ext34/ext/out/ext.S
python3 asm68k.py --flagfix --idxlong --ram 0x0900 -b 0xF90000 -o $D/ext34/ext/out/ext.bin -m $D/ext34/ext/out/ext.map $D/ext34/ext/ext_a.s $D/ext34/ext/out/ext.S rtl.s
cp $D/ext34/ext/out/ext.bin $H/ext_v34.bin
