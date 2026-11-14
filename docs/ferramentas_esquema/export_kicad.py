# -*- coding: utf-8 -*-
"""Exporta modelo.py para arquivos .kicad_sch (KiCad 7, formato 20230121) - EXPERIMENTAL, NAO VALIDADO (sem kicad-cli aqui).
Um arquivo por folha. Cada componente e um simbolo retangular com os pinos do modelo; cada pino ligado recebe um global_label com o nome da rede."""
import sys, uuid, re, math
import modelo
G = 2.54
def u(): return str(uuid.uuid4())
def q(s): return '"' + str(s).replace('\\', '\\\\').replace('"', "'") + '"'
def netname(n): return re.sub(r'[\s"]', '_', n)
def snap(v): return round(v / 1.27) * 1.27
def f(v): return ('%.3f' % v).rstrip('0').rstrip('.')

def numerar(c):
    L = []; R = []; k = 1
    for lst, out in ((c['left'], L), (c['right'], R)):
        for (num, nm, net, cf) in lst:
            if not num:
                num = f'x{k}'
            out.append((num, nm or '~', net)); k += 1
    return L, R

def lib_symbol(c, libname):
    L, R = numerar(c); n = max(len(L), len(R), 1)
    halfw = math.ceil((c['w'] / 2) / G) * G
    top = G / 2 * 0 + 1.27
    pins = []
    for side, lst, x, ang in (('l', L, -(halfw + 5.08), 0), ('r', R, halfw + 5.08, 180)):
        for i, (num, nm, net) in enumerate(lst):
            y = -i * G
            pins.append(f'(pin passive line (at {f(x)} {f(y)} {ang}) (length 5.08) (name {q(nm)} (effects (font (size 1.016 1.016)))) (number {q(num)} (effects (font (size 1.016 1.016)))))')
    ybot = -(n - 1) * G - 1.27
    s = f'''(symbol {q('paragon:' + libname)} (pin_names (offset 0.5)) (in_bom yes) (on_board yes)
  (property "Reference" "U" (at 0 {f(1.27 + 2.5)} 0) (effects (font (size 1.27 1.27))))
  (property "Value" {q(c['value'][:40])} (at 0 {f(ybot - 2.5)} 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
  (symbol {q(libname + '_0_1')} (rectangle (start {f(-halfw)} 1.27) (end {f(halfw)} {f(ybot)}) (stroke (width 0.254) (type default)) (fill (type background))))
  (symbol {q(libname + '_1_1')}
    ''' + '\n    '.join(pins) + '))'
    return s, halfw, L, R

def sheet(sh):
    comps = [c for c in modelo.COMPS if c['sheet'] == sh]
    root = u(); libs = []; body = []
    # layout simples em colunas: 120 mm por componente em x, empilhando em y
    x = 100.0; y = 40.0; ymax = 0
    cols = {}
    for c in sorted(comps, key=lambda c: (round(c['x']), c['y'])): cols.setdefault(round(c['x']), []).append(c)
    for key, lst in cols.items():
        y = 40.0; wmax = 0
        for c in lst:
            lib = re.sub(r'[^A-Za-z0-9_]', '_', c['ref'])
            ls, halfw, L, R = lib_symbol(c, lib); libs.append(ls)
            n = max(len(L), len(R), 1)
            X = snap(x + halfw + 30); Y = snap(y + 10)
            body.append(f'''(symbol (lib_id {q('paragon:' + lib)}) (at {f(X)} {f(Y)} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {u()})
  (property "Reference" {q(c['ref'])} (at {f(X)} {f(Y - 3.8)} 0) (effects (font (size 1.27 1.27))))
  (property "Value" {q(c['value'][:40])} (at {f(X)} {f(Y - (n - 1) * G - 4)} 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at {f(X)} {f(Y)} 0) (effects (font (size 1.27 1.27)) hide))
  (property "Datasheet" "" (at {f(X)} {f(Y)} 0) (effects (font (size 1.27 1.27)) hide))
  ''' + ' '.join(f'(pin {q(p[0])} (uuid {u()}))' for p in L + R) + f'''
  (instances (project "paragon50" (path "/{root}" (reference {q(c['ref'])}) (unit 1)))))''')
            for side, lst2, px, ang, just in (('l', L, -(halfw + 5.08), 180, 'right'), ('r', R, halfw + 5.08, 0, 'left')):
                for i, (num, nm, net) in enumerate(lst2):
                    if not net: continue
                    body.append(f'(global_label {q(netname(net))} (shape passive) (at {f(X + px)} {f(Y + i * G)} {ang}) (effects (font (size 1.27 1.27)) (justify {just})) (uuid {u()}) (property "Intersheet References" "${{INTERSHEET_REFS}}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)))')
            y += n * G + 25; wmax = max(wmax, 2 * halfw + 10.16 + 70)
        x += wmax + 30
    txt = f'(text {q("PARAGON 50 - Folha " + str(sh) + ": " + modelo.SHEETS[sh] + " (EXPERIMENTAL, gerado por script; ver CSV da netlist)")} (at 30 20 0) (effects (font (size 2.5 2.5))) (uuid {u()}))'
    out = f'(kicad_sch (version 20230121) (generator "paragon_export") (uuid {root}) (paper "A1")\n(lib_symbols\n' + '\n'.join(libs) + '\n)\n' + txt + '\n' + '\n'.join(body) + '\n(sheet_instances (path "/" (page "1")))\n)\n'
    return out

def balanced(s):
    d = 0; instr = False; prev = ''
    for ch in s:
        if ch == '"' and prev != '\\': instr = not instr
        elif not instr:
            d += (ch == '(') - (ch == ')')
            if d < 0: return False
        prev = ch
    return d == 0 and not instr

if __name__ == '__main__':
    outdir, tag = sys.argv[1], sys.argv[2]
    for sh in sorted(modelo.SHEETS):
        s = sheet(sh); fn = f'{outdir}/Paragon50_{tag}_folha{sh}.kicad_sch'
        open(fn, 'w', encoding='utf-8').write(s); print(fn, len(s), 'parenteses OK' if balanced(s) else 'PARENTESES DESBALANCEADOS')
