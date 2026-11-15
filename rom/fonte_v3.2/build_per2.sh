#!/bin/bash
# build_per.sh [fonte.c] [saida.bin] : compila o modulo de perifericos PER1 para $F88000
set -e
D=/tmp/claude-0/-home-claude/93617e9f-8b52-5410-9afb-5edd9ad3194e/scratchpad
SRC=${1:-per_v1.c}; OUT=${2:-per_v1.bin}
H=$(pwd)
mkdir -p $D/per/out
cp $H/$SRC $D/per/per.c; cp $H/per_a2.s $D/per/per_a2.s
cd $D/cpm
CC_OPT=Oz ./cc.sh $D/per/per.c $D/per/out/per.S
python3 asm68k.py --flagfix --idxlong -b 0xF88000 -o $D/per/out/per.bin -m $D/per/out/per.map $D/per/per_a2.s $D/per/out/per.S rtl.s
cp $D/per/out/per.bin $H/$OUT; cp $D/per/out/per.map $H/${OUT%.bin}.map
