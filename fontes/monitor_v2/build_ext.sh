#!/bin/bash
# build_ext.sh : compila o modulo v2 (ext.c + ext_a.s) -> ext/ext.bin ($F90000)
set -e
D=/tmp/claude-0/-home-claude/93617e9f-8b52-5410-9afb-5edd9ad3194e/scratchpad
cd $D/cpm
CC_OPT=Oz ./cc.sh $D/v2/ext/ext.c $D/v2/ext/ext.S
python3 asm68k.py --flagfix --idxlong --ram 0x0900 -b 0xF90000 -o $D/v2/ext/ext.bin -m $D/v2/ext/ext.map $D/v2/ext/ext_a.s $D/v2/ext/ext.S rtl.s
awk '/^\tbtst/{getline n; if(n !~ /^\t(beq|bne)/) {print "BTST RISCO linha " NR ": " n}}' $D/v2/ext/ext.S
