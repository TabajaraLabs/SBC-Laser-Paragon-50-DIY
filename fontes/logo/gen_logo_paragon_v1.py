#!/usr/bin/env python3
"""gen_logo_paragon_v1.py - logotipo PARAGON 50 (palavra unica; um feixe de laser atravessa o O e o N; "50" ao lado).
Gera: SVG (vetor), STL (uma peca so, para colar na frente do gabinete) e PNG de previa.
Camadas do STL (z): aba/base 0..0,8 mm | feixe 0,8..1,6 | letras 0,8..2,4. Altura das maiusculas = CAP mm (padrao 12).
Uso: gen_logo_paragon_v1.py [CAP_mm] [prefixo_saida]"""
import sys, math, struct
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from skimage import measure
from matplotlib.path import Path as MPath

CAP = float(sys.argv[1]) if len(sys.argv) > 1 else 12.0
OUT = sys.argv[2] if len(sys.argv) > 2 else 'logo_paragon_v1'
U = CAP / 100.0                      # mm por unidade (altura das maiusculas = 100 u)
Z_BASE, Z_BEAM, Z_LET = 0.8, 1.6, 2.4
MARGIN_MM = 1.0                      # aba ao redor
P_MM = 0.04 * CAP / 12.0             # passo da grade final
K = U / P_MM                         # px por unidade (final)
SS = 4                               # supersampling
S = K * SS                           # px por unidade (supersampled)
X0u, X1u, Y0u, Y1u = -36.0, 856.0, -36.0, 136.0
W = int(round((X1u - X0u) * S)); H = int(round((Y1u - Y0u) * S))
img = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(img)
def px(x, y): return ((x - X0u) * S, (Y1u - y) * S)
def line(pts, w, joint=None):
    """traço com pontas redondas: carimba discos ao longo da polilinha (sem artefatos de juncao)"""
    r = w * S / 2.0
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) * S / max(1.0, r * 0.35)))
        for i in range(n + 1):
            cx, cy = px(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n)
            dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
def arc(cx, cy, r, a0, a1, n=None):
    n = n or max(8, int(abs(a1 - a0) / 3))
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
ST = 16.0                            # espessura do traco (u)
# ---- letras (x0 = canto esquerdo; larguras w)
def P_(x0):
    line([(x0 + 11, -5), (x0 + 11, 105)], ST)
    line([(x0 + 11, 89), (x0 + 31, 89)] + arc(x0 + 31, 69, 20, 90, -90) + [(x0 + 11, 49)], ST, 'curve')
def A_(x0):
    line([(x0 + 12.5, -5), (x0 + 40, 107.5)], ST); line([(x0 + 67.5, -5), (x0 + 40, 107.5)], ST)
    line([(x0 + 22, 30), (x0 + 58, 30)], 14)
def R_(x0):
    P_(x0 + 0); 
    line([(x0 + 11, 89), (x0 + 33, 89)] + arc(x0 + 33, 69, 20, 90, -90) + [(x0 + 11, 49)], ST, 'curve')
    line([(x0 + 33, 50), (x0 + 57, -8)], ST)
def ring(cx, cy, r, a0=0, a1=360): line(arc(cx, cy, r, a0, a1, 120), ST, 'curve')
def G_(x0):
    ring(x0 + 50, 50, 39)
    wedge = [px(x0 + 50, 50)] + [px(x0 + 50 + 80 * math.cos(math.radians(a)), 50 + 80 * math.sin(math.radians(a))) for a in (12, 20, 30, 45)]
    dr.polygon(wedge, fill=0)
    line([(x0 + 52, 50), (x0 + 100, 50)], ST)
def O_(x0): ring(x0 + 50, 50, 39)
def N_(x0):
    line([(x0 + 11, -5), (x0 + 11, 105)], ST); line([(x0 + 65, -5), (x0 + 65, 105)], ST)
    line([(x0 + 11, 105), (x0 + 65, -5)], ST)
def FIVE(x0):
    line([(x0 + 11, 89), (x0 + 60, 89)], ST); line([(x0 + 11, 100), (x0 + 11, 52)], ST)
    line(arc(x0 + 30, 36, 25, 130, -130, 80), ST, 'curve')
def ZERO(x0):
    pts = [(x0 + 35 + 24 * math.cos(math.radians(a)), 50 + 39 * math.sin(math.radians(a))) for a in range(0, 361, 3)]
    line(pts, ST, 'curve')
XP, XA1, XR, XA2, XG, XO, XN, X5, X0_ = 0, 74, 166, 244, 336, 448, 560, 672, 750
for f, x in ((P_, XP), (A_, XA1), (R_, XR), (A_, XA2), (G_, XG), (O_, XO), (N_, XN), (FIVE, X5), (ZERO, X0_)): f(x)
# faixa 0..100 u
dr.rectangle([0, 0, W, px(0, 100)[1] - 1], fill=0); dr.rectangle([0, px(0, 0)[1] + 1, W, H], fill=0)
SLOT = 9.0                           # meia altura do corte (u): feixe 4 + folga 5
def rect(x0, y0, x1, y1, fill):
    a, b = px(x0, y1), px(x1, y0); dr.rectangle([a[0], a[1], b[0], b[1]], fill=fill)
rect(XO - 3, 50 - SLOT, XO + 100 + 3, 50 + SLOT, 0)     # fenda no O
rect(XN - 3, 50 - SLOT, XN + 76 + 3, 50 + SLOT, 0)      # fenda no N
letters_ss = np.asarray(img, dtype=np.uint8).copy()
BEAM0, BEAM1 = 442.0, 660.0
beam_img = Image.new('L', (W, H), 0); bd = ImageDraw.Draw(beam_img)
bd.polygon([px(BEAM0, 50), px(BEAM0 + 16, 54), px(BEAM1, 54), px(BEAM1, 46), px(BEAM0 + 16, 46)], fill=255)
beam_ss = np.asarray(beam_img, dtype=np.uint8)
def down(a):
    h, w = (a.shape[0] // SS) * SS, (a.shape[1] // SS) * SS
    return a[:h, :w].reshape(h // SS, SS, w // SS, SS).mean(axis=(1, 3)) / 255.0
cov_let, cov_beam = down(letters_ss), down(beam_ss)
# aba: dilatacao circular de (letras + feixe + fendas)
slot_mask = np.zeros_like(cov_let, dtype=bool)
def ucol(x): return int(round((x - X0u) * K))
def urow(y): return int(round((Y1u - y) * K))
for xa, xb in ((XO - 3, XO + 103), (XN - 3, XN + 79)): slot_mask[urow(50 + SLOT):urow(50 - SLOT), ucol(xa):ucol(xb)] = True
base = (cov_let > 0.5) | (cov_beam > 0.5) | slot_mask
dist = ndimage.distance_transform_edt(~base) * P_MM          # mm ate o conjunto
field_skirt = (MARGIN_MM - dist) / P_MM                      # >0 dentro da aba
def contours(field, level, tol_mm=0.012):
    out = []
    for c in measure.find_contours(np.pad(field, 1, constant_values=-1e3 if level == 0 else 0), level):
        c = c - 1.0
        c = measure.approximate_polygon(c, tolerance=tol_mm / P_MM)
        if len(c) < 5: continue
        pts = [(X0u * U + (col + 0.5) * P_MM, Y1u * U - (row + 0.5) * P_MM) for row, col in c[:-1]]
        out.append(pts)
    return out
rings_skirt = contours(field_skirt, 0.0)
rings_let = contours(cov_let, 0.5)
rings_beam = contours(cov_beam, 0.5)
print('aneis: aba %d, letras %d, feixe %d' % (len(rings_skirt), len(rings_let), len(rings_beam)))
# ----- geometria 2D utilitaria
def area(r): return 0.5 * sum(r[i][0] * r[(i + 1) % len(r)][1] - r[(i + 1) % len(r)][0] * r[i][1] for i in range(len(r)))
def depths(rings):
    paths = [MPath(np.array(r + [r[0]])) for r in rings]
    d = []
    for i, r in enumerate(rings):
        n = 0
        for j, pj in enumerate(paths):
            if i != j and abs(area(rings[j])) > abs(area(r)) and pj.contains_point(r[0]): n += 1
        d.append(n)
    return d
def orient(rings):
    """aneis de profundidade par = antihorario, impar = horario"""
    d = depths(rings); out = []
    for r, k in zip(rings, d):
        a = area(r)
        if (k % 2 == 0) != (a > 0): r = r[::-1]
        out.append(r)
    return out, d
def seg_inter(p, q, a, b):
    def cr(o, u, v): return (u[0] - o[0]) * (v[1] - o[1]) - (u[1] - o[1]) * (v[0] - o[0])
    d1, d2, d3, d4 = cr(p, q, a), cr(p, q, b), cr(a, b, p), cr(a, b, q)
    return (d1 * d2 < -1e-12) and (d3 * d4 < -1e-12)
def triangulate(outer, holes):
    """outer antihorario, buracos horarios -> lista de triangulos (indices em pts)"""
    holes = sorted(holes, key=lambda h: -max(p[0] for p in h))
    poly = list(outer)
    for h in holes:
        mi = max(range(len(h)), key=lambda i: h[i][0]); M = h[mi]
        cand = sorted(range(len(poly)), key=lambda i: (poly[i][0] - M[0]) ** 2 + (poly[i][1] - M[1]) ** 2)
        other = [hh for hh in holes if hh is not h]
        ok = None
        for ci in cand:
            V = poly[ci]; bad = False
            for i in range(len(poly)):
                a, b = poly[i], poly[(i + 1) % len(poly)]
                if a in (V, M) or b in (V, M): continue
                if seg_inter(M, V, a, b): bad = True; break
            if not bad:
                for hh in other + [h]:
                    for i in range(len(hh)):
                        a, b = hh[i], hh[(i + 1) % len(hh)]
                        if a in (V, M) or b in (V, M): continue
                        if seg_inter(M, V, a, b): bad = True; break
                    if bad: break
            if not bad: ok = ci; break
        assert ok is not None, 'sem ponte para o buraco'
        hr = h[mi:] + h[:mi]
        poly = poly[:ok + 1] + hr + [hr[0]] + [poly[ok]] + poly[ok + 1:]
    n = len(poly); xs = np.array([p[0] for p in poly]); ys = np.array([p[1] for p in poly])
    nxt = list(range(1, n)) + [0]; prv = [n - 1] + list(range(0, n - 1)); alive = n; tris = []; i = 0; guard = 0
    def cross(a, b, c): return (xs[b] - xs[a]) * (ys[c] - ys[a]) - (ys[b] - ys[a]) * (xs[c] - xs[a])
    idx = np.arange(n)
    while alive > 3:
        found = False; start = i; first = True
        while first or i != start:
            first = False
            a, b, c = prv[i], i, nxt[i]
            if cross(a, b, c) > 1e-14:
                # nenhum outro vertice vivo dentro do triangulo
                alv = np.ones(n, bool); 
                px_, py_ = xs, ys
                d1 = (xs[b] - xs[a]) * (py_ - ys[a]) - (ys[b] - ys[a]) * (px_ - xs[a])
                d2 = (xs[c] - xs[b]) * (py_ - ys[b]) - (ys[c] - ys[b]) * (px_ - xs[b])
                d3 = (xs[a] - xs[c]) * (py_ - ys[c]) - (ys[a] - ys[c]) * (px_ - xs[c])
                inside = (d1 >= -1e-12) & (d2 >= -1e-12) & (d3 >= -1e-12)
                for v in (a, b, c): inside[v] = False
                same = ((xs == xs[a]) & (ys == ys[a])) | ((xs == xs[b]) & (ys == ys[b])) | ((xs == xs[c]) & (ys == ys[c]))
                inside &= ~same
                if dead_mask_any(inside, nxt, prv, i): pass
                if not np.any(inside & alive_mask(n, nxt, i)):
                    tris.append((a, b, c)); nxt[a] = c; prv[c] = a; alive -= 1; found = True; i = c; break
            i = nxt[i]
        if not found:
            # remove vertice degenerado (colinear) para destravar
            i = start; a, b, c = prv[i], i, nxt[i]; tris.append((a, b, c)); nxt[a] = c; prv[c] = a; alive -= 1; i = c
    a = nxt[i]; tris.append((prv[i], i, a))
    return poly, tris
def dead_mask_any(*_): return False
def alive_mask(n, nxt, i):
    m = np.zeros(n, bool); j = i
    while True:
        m[j] = True; j = nxt[j]
        if j == i: break
    return m
def region_triangles(rings_o):
    """rings_o: aneis orientados; devolve triangulos [(p,q,r)] cobrindo (paridade par) as regioes"""
    d = depths(rings_o); tris = []
    for i, r in enumerate(rings_o):
        if d[i] % 2: continue
        holes = [rings_o[j] for j in range(len(rings_o)) if d[j] == d[i] + 1 and MPath(np.array(r + [r[0]])).contains_point(rings_o[j][0])]
        poly, t = triangulate(r, holes)
        for a, b, c in t: tris.append((poly[a], poly[b], poly[c]))
    return tris
# ----- malha
mesh = []
def add(tri, z, up=True):
    a, b, c = tri
    if not up: b, c = c, b
    mesh.append(((a[0], a[1], z), (b[0], b[1], z), (c[0], c[1], z)))
def walls(rings_o, z0, z1):
    for r in rings_o:
        for i in range(len(r)):
            a, b = r[i], r[(i + 1) % len(r)]
            A0, B0, B1, A1 = (a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)
            mesh.append((A0, B0, B1)); mesh.append((A0, B1, A1))
sk, _ = orient(rings_skirt); le, _ = orient(rings_let); be, _ = orient(rings_beam)
# fundo e topo da aba
t_bottom = region_triangles(sk)
for t in t_bottom: add(t, 0.0, up=False)
walls(sk, 0.0, Z_BASE)
t_top = region_triangles(orient(rings_skirt + rings_let + rings_beam)[0])
for t in t_top: add(t, Z_BASE, up=True)
for t in region_triangles(le): add(t, Z_LET, up=True)
walls(le, Z_BASE, Z_LET)
for t in region_triangles(be): add(t, Z_BEAM, up=True)
walls(be, Z_BASE, Z_BEAM)
M = np.array(mesh, dtype=np.float64)
print('triangulos:', len(M))
# ----- verificacao: arestas pareadas e volume
def key(p): return (round(p[0], 5), round(p[1], 5), round(p[2], 5))
from collections import Counter
E = Counter()
for t in M:
    for i in range(3):
        a, b = key(t[i]), key(t[(i + 1) % 3])
        E[(a, b)] += 1
unp = sum(1 for (a, b), n in E.items() if E.get((b, a), 0) != n)
vol = sum(np.dot(t[0], np.cross(t[1], t[2])) for t in M) / 6.0
print('arestas sem par: %d | volume %.1f mm3 (positivo = normais para fora)' % (unp, vol))
# ----- STL binario
def write_stl(path, M):
    with open(path, 'wb') as f:
        f.write(b'PARAGON 50 logotipo v1 - Tabajara Labs'.ljust(80, b' ')); f.write(struct.pack('<I', len(M)))
        for t in M:
            n = np.cross(t[1] - t[0], t[2] - t[0]); l = np.linalg.norm(n); n = n / l if l > 0 else n
            f.write(struct.pack('<12fH', *n, *t[0], *t[1], *t[2], 0))
# origem: canto inferior esquerdo da aba em (0,0)
allp = M.reshape(-1, 3); mn = allp.min(axis=0); mx = allp.max(axis=0)
M2 = M - np.array([mn[0], mn[1], 0.0])
write_stl(OUT + '.stl', M2)
print('STL: %.1f x %.1f x %.1f mm -> %s.stl' % (mx[0] - mn[0], mx[1] - mn[1], mx[2], OUT))
# ----- SVG (vetor, letras e feixe), em mm, y para baixo
def path_d(rings, ox, oy, ymax):
    return ' '.join('M' + ' L'.join('%.3f,%.3f' % (p[0] - ox, ymax - (p[1] - oy)) for p in r) + ' Z' for r in rings)
lx = [p[0] for r in rings_let + rings_beam for p in r]; ly = [p[1] for r in rings_let + rings_beam for p in r]
ox, oy, ox1, oy1 = min(lx), min(ly), max(lx), max(ly); wmm, hmm = ox1 - ox, oy1 - oy
dl = path_d(le, ox, oy, hmm); db = path_d(be, ox, oy, hmm)
open(OUT + '_letras.svgpath', 'w').write(dl); open(OUT + '_feixe.svgpath', 'w').write(db)
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.3f %.3f" width="%.3fmm" height="%.3fmm">'
       '<path d="%s" fill="#141A21" fill-rule="evenodd"/><path d="%s" fill="#E63B1B"/></svg>') % (wmm, hmm, wmm, hmm, dl, db)
open(OUT + '.svg', 'w').write(svg)
print('letras+feixe: %.1f x %.1f mm' % (wmm, hmm))
# ----- previa com sombreamento (mapa de alturas)
hmap = np.zeros(cov_let.shape)
hmap[field_skirt > 0] = Z_BASE; hmap[cov_beam > 0.5] = Z_BEAM; hmap[cov_let > 0.5] = Z_LET
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
gy, gx = np.gradient(ndimage.gaussian_filter(hmap, 1.2))
shade = np.clip(0.5 + 2.2 * (-gx - gy) * 1.0, 0, 1)
rgb = np.zeros(hmap.shape + (3,)); rgb[:] = (0.07, 0.08, 0.1)
sk_m = hmap > 0
base_col = np.array([0.80, 0.78, 0.74])
for k, col in ((Z_BASE, (0.55, 0.55, 0.55)), (Z_BEAM, (0.93, 0.33, 0.20)), (Z_LET, (0.93, 0.92, 0.88))):
    m = np.isclose(hmap, k); rgb[m] = col
rgb[sk_m] *= (0.55 + 0.9 * shade[sk_m])[:, None]
rgb = np.clip(rgb, 0, 1)
plt.imsave(OUT + '_previa.png', rgb[::1, ::1])
