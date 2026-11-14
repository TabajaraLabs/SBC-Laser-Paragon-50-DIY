#!/usr/bin/env python3
"""conv_eforth_v1.py - converte FORTHASM.TXT (eForth 68000, sintaxe Motorola de campos) para o dialeto do m68kasm_v3.
Aplica os remendos para o PARAGON 50 (DUART em $FA0003/$FA0007, mapa de memoria, BYE)."""
import re, sys
src = open(sys.argv[1], encoding='latin-1').read().split('\n')
out = []
def split_fields(line):
    # devolve (label, mnemonico, operandos) respeitando aspas simples
    line = line.replace('\t', ' ')
    label = ''
    if line[0] != ' ':
        m = re.match(r'(\S+)', line); label = m.group(1); line = line[m.end():]
    line = line.strip()
    if not line: return label, '', ''
    m = re.match(r'(\S+)\s*', line); mn = m.group(1); rest = line[m.end():]
    ops = ''; q = False; i = 0
    while i < len(rest):
        ch = rest[i]
        if ch == "'": q = not q
        elif ch == ' ' and not q: break
        ops += ch; i += 1
    return label, mn, ops
def conv_str(ops):
    # 'abc' -> numeros ; '' dentro da string = apostrofo
    res = []; i = 0
    while i < len(ops):
        if ops[i] == "'":
            j = i + 1; s = ''
            while j < len(ops):
                if ops[j] == "'":
                    if j + 1 < len(ops) and ops[j+1] == "'": s += "'"; j += 2; continue
                    break
                s += ops[j]; j += 1
            res += [str(ord(c)) for c in s]; i = j + 1
            if i < len(ops) and ops[i] == ',': i += 1
        else:
            j = ops.find(',', i)
            if j < 0: j = len(ops)
            res.append(ops[i:j]); i = j + 1
    return ','.join(res)
for ln in src:
    if not ln.strip() or ln[0] == '*': continue
    label, mn, ops = split_fields(ln)
    label = label.rstrip(':').replace('$', 'S')
    ops = ops.replace('char$', 'charS')
    m = mn.lower()
    if m == 'equ' and ops == '*': out.append(label + ':'); continue
    if m in ('equ', 'set'): out.append('%s %s %s' % (label, m, ops)); continue
    if label: out.append(label + ':')
    if not mn: continue
    if m in ('dc.b',): ops = conv_str(ops)
    out.append('        %s %s' % (mn, ops))
txt = '\n'.join(out)
open(sys.argv[2], 'w').write(txt + '\n')
print(len(out), 'linhas')
