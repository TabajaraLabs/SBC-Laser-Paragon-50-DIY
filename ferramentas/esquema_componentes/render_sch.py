# -*- coding: utf-8 -*-
"""Renderiza o esquema com componentes (modelo.py) -> PNG/PDF por folha + netlist CSV."""
import sys, csv, collections
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
plt.rcParams['text.parse_math'] = False
plt.rcParams['font.family'] = 'DejaVu Sans Mono'
import modelo

TAG = 'v?'
P = 3.81; FS = 5.6; CW = 1.22       # passo de pino (mm), fonte (pt), largura de caractere (mm)
COR = {'M': '#1a8a2e', 'C': '#1a8a2e', 'I': '#1f5fbf', '?': '#d02020'}
POWER = {'VCC', 'GND', '+12V', '-12V', '+5V_EXT'}

# --- indice de redes ---
rede = collections.defaultdict(list)
for c in modelo.COMPS:
    for lado in ('left', 'right'):
        for (num, nm, net, cf) in c[lado]:
            if net: rede[net].append((c['ref'], num or nm, c['sheet']))

def hint(net, ref, num):
    if net in POWER: return net
    outros = [f'{r}.{n}' for r, n, sh in rede[net] if not (r == ref and n == num)]
    if not outros: return net
    # prefere destinos distintos por componente
    vistos = []; 
    for o in outros:
        if o.split('.')[0] not in [v.split('.')[0] for v in vistos]: vistos.append(o)
    txt = ', '.join(vistos[:3]) + (f' +{len(vistos)-3}' if len(vistos) > 3 else '')
    return f'{net} > {txt}'

def layout(sheet):
    comps = [c for c in modelo.COMPS if c['sheet'] == sheet]
    cols = collections.OrderedDict()
    for c in sorted(comps, key=lambda c: (round(c['x']), c['y'])): cols.setdefault(round(c['x']), []).append(c)
    pos = {}; xcur = 10.0
    for key, lst in cols.items():
        info = []
        for c in lst:
            lab = lambda L, side: max([len(hint(n, c['ref'], num or nm)) for num, nm, n, cf in L if n] + [0]) * CW + 7
            lw = lab(c['left'], 'l'); rw = lab(c['right'], 'r')
            nl = max([len(nm) for _, nm, _, _ in c['left']] + [0]); nr = max([len(nm) for _, nm, _, _ in c['right']] + [0])
            w = max(c['w'], (nl + nr) * CW + 6, len(c['value']) * 1.4 * 0 + 10)
            info.append((c, lw, rw, w))
        lmax = max(i[1] for i in info); wmax = max(i[3] for i in info)
        rmax = max(max(i[2] for i in info), max(len(i[0]['ref'])*2.3+2+len(i[0]['value'])*1.1+4 - i[3] for i in info), max(len(i[0]['note'])*1.0 - i[3] for i in info))
        xb = xcur + lmax
        y = 38.0
        for c, lw, rw, w in info:
            n = max(len(c['left']), len(c['right']), 1)
            h = n * P + 2
            pos[c['ref']] = (xb, y, w, h)
            y += h + 16 + (4 if c['note'] else 0)
        xcur = xb + wmax + rmax + 10
    H = max([p[1] + p[3] for p in pos.values()] + [100]) + 25
    return comps, pos, xcur + 5, H

def desenha(sheet):
    comps, pos, Wm, Hm = layout(sheet)
    Wm = max(Wm, 200); Hm = max(Hm, 120)
    fig = plt.figure(figsize=(Wm / 25.4, Hm / 25.4)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, Wm); ax.set_ylim(Hm, 0); ax.axis('off')
    ax.add_patch(plt.Rectangle((2, 2), Wm - 4, Hm - 4, fill=False, lw=1.0, ec='#444'))
    ax.text(6, 8, f'PARAGON 50 - Folha {sheet}/6: {modelo.SHEETS[sheet]}', fontsize=11, weight='bold', va='center')
    ax.text(6, 14, 'Esquema com componentes - levantado por medicao (' + TAG + '). Cada fio e uma etiqueta de rede: "REDE > destino.pino".', fontsize=6.2, va='center', color='#333')
    for k, (cf, tx) in enumerate([('M', 'verde = medido / confirmado'), ('I', 'azul = inferido (datasheet, funcao)'), ('?', 'vermelho = desconhecido, a rastrear')]):
        ax.plot([6, 12], [20 + 4 * k] * 2, color=COR[cf], lw=1.6); ax.text(14, 20 + 4 * k, tx, fontsize=5.6, va='center', color=COR[cf])
    for c in comps:
        x, y, w, h = pos[c['ref']]
        ax.add_patch(plt.Rectangle((x, y), w, h, fc='#fffbe8', ec='#222', lw=1.0, zorder=2))
        ax.text(x, y - 5, c['ref'], fontsize=8.5, weight='bold', va='bottom')
        ax.text(x + len(c['ref']) * 2.3 + 2, y - 5, c['value'], fontsize=5.8, va='bottom', color='#333')
        if c['note']: ax.text(x, y + h + 3, c['note'], fontsize=5.2, va='top', color='#7a4a00', style='italic')
        for side, L in (('left', c['left']), ('right', c['right'])):
            for i, (num, nm, net, cf) in enumerate(L):
                py = y + 1 + P * (i + 0.5)
                col = COR.get(cf, '#333')
                if side == 'left':
                    x0, x1 = x - 5, x; ha, xn, xl = 'left', x + 1.0, x - 6.5; hal = 'right'
                else:
                    x0, x1 = x + w, x + w + 5; ha, xn, xl = 'right', x + w - 1.0, x + w + 6.5; hal = 'left'
                ax.text(xn, py, nm, fontsize=FS, ha=ha, va='center', zorder=3)
                ax.text((x0 + x1) / 2 if False else (x - 2.5 if side == 'left' else x + w + 2.5), py - 1.35, num, fontsize=4.2, ha='center', va='bottom', color='#555')
                if net:
                    ax.plot([x0, x1], [py, py], color=col, lw=1.0, zorder=1)
                    ax.text(xl, py, hint(net, c['ref'], num or nm), fontsize=FS, ha=hal, va='center', color=col)
                else:
                    ax.plot([x0 + 2.5, x1] if side == 'left' else [x0, x1 - 2.5], [py, py], color='#aaa', lw=0.6, zorder=1)
    return fig

def main(outdir, tag):
    global TAG; TAG = tag
    with PdfPages(f'{outdir}/Paragon50_Esquema_componentes_{tag}.pdf') as pdf:
        for sh in sorted(modelo.SHEETS):
            fig = desenha(sh)
            fig.savefig(f'{outdir}/Paragon50_Esquema_componentes_{tag}_folha{sh}.png', dpi=130)
            pdf.savefig(fig); plt.close(fig)
    with open(f'{outdir}/Paragon50_Netlist_{tag}.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['rede', 'componente', 'pino', 'nome_do_pino', 'confianca', 'folha'])
        for net in sorted(rede):
            for c in modelo.COMPS:
                for lado in ('left', 'right'):
                    for (num, nm, n, cf) in c[lado]:
                        if n == net: w.writerow([net, c['ref'], num, nm, {'M': 'medido', 'C': 'confirmado', 'I': 'inferido', '?': 'desconhecido'}[cf], c['sheet']])
if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
