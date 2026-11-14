#!/bin/bash
set -e
D=/tmp/claude-0/-home-claude/93617e9f-8b52-5410-9afb-5edd9ad3194e/scratchpad
cd $D/cpm
mkdir -p $D/v21/ext/out
CC_OPT=Oz ./cc.sh $D/v21/ext/ext.c $D/v21/ext/out/ext.S
python3 asm68k.py --flagfix --idxlong --ram 0x0900 -b 0xF90000 -o $D/v21/ext/out/ext.bin -m $D/v21/ext/out/ext.map $D/v21/ext/ext_a.s $D/v21/ext/out/ext.S rtl.s
awk '/^\tbtst/{getline n; if(n !~ /^\t(beq|bne)/) {print "BTST RISCO linha " NR ": " n}}' $D/v21/ext/out/ext.S
