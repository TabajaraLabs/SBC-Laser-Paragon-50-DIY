#!/usr/bin/env python3
"""
PLACA DE TESTE (calibre) do gabinete Paragon 50  -  v6 (metade da espessura, furos/ posicoes corrigidos pelo teste da v3)

Chapa plana fina com o REBAIXO da placa, os 5 FUROS passantes e uma GRADE no lugar da janela
da tampa (so a moldura, os ressaltos em volta dos furos e as nervuras ficam; o resto e vazado).

Como a malha e feita: triangulacao de Delaunay (scipy) de pontos amostrados sobre todos os contornos;
cada triangulo recebe uma altura (mapa de alturas). Topo, fundo e paredes saem da mesma triangulacao,
entao nao ha juncoes em T nem rasgos: o STL e fechado (cada aresta aparece em exatamente 2 faces).

Uso: python3 placa_teste.py [pasta_de_saida]
"""
import sys, os, math, struct, itertools, collections
import numpy as np
from scipy.spatial import Delaunay

# ---------------- medidas (mm) - as mesmas de gabinete.py ----------------
L, W   = 274.0, 142.6      # v5: W = 145,6 (rebaixo da v3) - 3,0 (folga medida atras da placa, encostada na frente) = 142,6
# v4: posicoes corrigidas pelas fotos da v3 (ponto de caneta = furo real). u pela medida de cada furo; v +0,4 (placa encostada na frente) + desvio medido; furo 5 limitado (leitura ruim)
# v6: correcao pelas fotos da v5 (furo impresso vs furo da PCB): RESET -> (+0,4;+0,2), J1/SW2 -> (0;-0,5), U16 -> (0;+2,0)
FUROS  = [(32.1, 6.2), (32.5, 107.1), (137.3, 59.0), (240.9, 6.3), (241.4, 106.0)]
ESP    = 2.25     # espessura total (borda) - v4: metade da v3 (4,5)
REB    = 1.2      # profundidade do rebaixo da placa
FOLGA  = 0.4      # folga em volta da placa
MARG   = 6.0      # margem em volta do rebaixo
LEDGE  = 2.0      # apoio da placa (igual a tampa); o resto e janela vazada
D_FURO = 4.0      # furo passante p/ M3
RBOSS  = 6.0      # meio-lado do ressalto quadrado em volta de cada furo
H_NERV = 1.05     # altura das nervuras da grade
W_NERV = 2.0      # largura das nervuras
ENTALHES = [(42.0, 129.0), (142.0, 218.0)]       # faixas X onde a margem frontal e aberta (J2, J1)
NERV_X = [40.0, 90.0, 145.5, 190.0, 245.0]       # nervuras ao longo de Y (x constante); 40/145,5/245 tocam os ressaltos
NERV_Y = [9.0, 35.0, 60.0, 80.0, 105.0, 130.0]   # nervuras ao longo de X (y constante); 9/105 tocam os ressaltos
PASSO  = 1.0      # espacamento dos pontos nos contornos
NC     = 48       # lados do poligono dos furos
# ---------------------------------------------------------------------------
x0, x1, y0, y1 = -FOLGA - MARG, L + FOLGA + MARG, -FOLGA - MARG, W + FOLGA + MARG
R = D_FURO / 2
H_LEDGE = ESP - REB
LEVELS = sorted({0.0, H_NERV, H_LEDGE, ESP})

def in_boss(x, y, strict=True):
    e = -1e-7 if strict else 1e-7
    return any(abs(x-u) < RBOSS+e and abs(y-v) < RBOSS+e for u, v in FUROS)

def altura(x, y):
    if x < x0 or x > x1 or y < y0 or y > y1: return 0.0
    if any(math.hypot(x-u, y-v) < R for u, v in FUROS): return 0.0
    if y < -FOLGA and any(a < x < b for a, b in ENTALHES): return 0.0
    if not (-FOLGA < x < L+FOLGA and -FOLGA < y < W+FOLGA): return ESP
    if not (LEDGE < x < L-LEDGE and LEDGE < y < W-LEDGE): return H_LEDGE
    if in_boss(x, y, False): return H_LEDGE
    if any(abs(x-c) < W_NERV/2 for c in NERV_X) or any(abs(y-c) < W_NERV/2 for c in NERV_Y): return H_NERV
    return 0.0

# ---------- contornos (retangulos) ----------
def ret(a, b, c, d): return [((a, c), (b, c)), ((b, c), (b, d)), ((b, d), (a, d)), ((a, d), (a, c))]
segs = []
segs += ret(x0, x1, y0, y1)
segs += ret(-FOLGA, L+FOLGA, -FOLGA, W+FOLGA)
segs += ret(LEDGE, L-LEDGE, LEDGE, W-LEDGE)
for a, b in ENTALHES: segs += ret(a, b, y0, -FOLGA)
for u, v in FUROS: segs += ret(u-RBOSS, u+RBOSS, v-RBOSS, v+RBOSS)
for c in NERV_X: segs += ret(c-W_NERV/2, c+W_NERV/2, LEDGE, W-LEDGE)
for c in NERV_Y: segs += ret(LEDGE, L-LEDGE, c-W_NERV/2, c+W_NERV/2)

pts = set()
def add(x, y): pts.add((round(x, 6), round(y, 6)))
for (ax, ay), (bx, by) in segs:
    n = max(1, math.ceil(math.hypot(bx-ax, by-ay) / PASSO))
    for i in range(n+1):
        x, y = ax+(bx-ax)*i/n, ay+(by-ay)*i/n
        if not in_boss(x, y, True): add(x, y)
V = [s for s in segs if abs(s[0][0]-s[1][0]) < 1e-9]; Hh = [s for s in segs if abs(s[0][1]-s[1][1]) < 1e-9]
for (p, q) in V:
    for (r, s) in Hh:
        xv, yh = p[0], r[1]
        if min(r[0], s[0])-1e-9 <= xv <= max(r[0], s[0])+1e-9 and min(p[1], q[1])-1e-9 <= yh <= max(p[1], q[1])+1e-9 and not in_boss(xv, yh, True):
            add(xv, yh)
for u, v in FUROS:
    for i in range(NC):
        a = 2*math.pi*i/NC; add(u+R*math.cos(a), v+R*math.sin(a))
P = np.array(sorted(pts))
tri = Delaunay(P).simplices
H = []
for t in tri:
    c = P[t].mean(axis=0); H.append(altura(c[0], c[1]))
# orienta todos os triangulos no sentido anti-horario
T = []
for t, h in zip(tri, H):
    a, b, c = P[t]
    if (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]) < 0: t = t[[0, 2, 1]]
    T.append((tuple(t), h))

# ---------- verificacao: os contornos existem como arestas ----------
E = set()
for t, h in T:
    for i in range(3): E.add(frozenset((t[i], t[(i+1) % 3])))
idx = {tuple(p): i for i, p in enumerate(np.round(P, 6))}
falta = 0
for (ax, ay), (bx, by) in segs:
    on = sorted([p for p in pts if abs((bx-ax)*(p[1]-ay)-(by-ay)*(p[0]-ax)) < 1e-6 and min(ax, bx)-1e-6 <= p[0] <= max(ax, bx)+1e-6 and min(ay, by)-1e-6 <= p[1] <= max(ay, by)+1e-6],
                key=lambda p: (p[0]-ax)**2+(p[1]-ay)**2)
    for p, q in zip(on, on[1:]):
        if in_boss((p[0]+q[0])/2, (p[1]+q[1])/2, True): continue
        if frozenset((idx[p], idx[q])) not in E: falta += 1
print('contornos faltando na triangulacao:', falta)

# ---------- malha 3D ----------
tris3 = []   # (p,q,r) coordenadas 3D, sentido anti-horario visto de fora
def v3(i, z): return (float(P[i][0]), float(P[i][1]), z)
viz = collections.defaultdict(list)
for k, (t, h) in enumerate(T):
    for i in range(3): viz[frozenset((t[i], t[(i+1) % 3]))].append(k)
for k, (t, h) in enumerate(T):
    if h <= 0: continue
    tris3.append((v3(t[0], h), v3(t[1], h), v3(t[2], h)))
    tris3.append((v3(t[0], 0), v3(t[2], 0), v3(t[1], 0)))
    for i in range(3):
        a, b = t[i], t[(i+1) % 3]
        o = [j for j in viz[frozenset((a, b))] if j != k]
        hb = T[o[0]][1] if o else 0.0
        if hb < h:
            zs = [hb] + [z for z in LEVELS if hb < z < h] + [h]
            for z0, z1 in zip(zs, zs[1:]):
                A0, B0, B1, A1 = v3(a, z0), v3(b, z0), v3(b, z1), v3(a, z1)
                tris3.append((A0, B0, B1)); tris3.append((A0, B1, A1))

# ---------- checagens ----------
def key(p): return tuple(round(c, 5) for c in p)
ed = collections.Counter()
for a, b, c in tris3:
    for p, q in ((a, b), (b, c), (c, a)): ed[(key(p), key(q))] += 1
nao_pareadas = sum(1 for (p, q), n in ed.items() if ed.get((q, p), 0) != n)
vol = 0.0
for a, b, c in tris3:
    vol += np.dot(a, np.cross(b, c)) / 6
print('triangulos', len(tris3), '| arestas sem par:', nao_pareadas, '| volume %.1f cm3 (~%.0f g de PLA)' % (vol/1000, vol/1000*1.24))
assert nao_pareadas == 0 and falta == 0 and vol > 0

out = sys.argv[1] if len(sys.argv) > 1 else 'out'
os.makedirs(out, exist_ok=True)
with open(out + '/placa_teste_v6.stl', 'wb') as f:
    f.write(b'placa_teste Paragon50 v2'.ljust(80, b' ')); f.write(struct.pack('<I', len(tris3)))
    for a, b, c in tris3:
        n = np.cross(np.subtract(b, a), np.subtract(c, a)); l = np.linalg.norm(n); n = n/l if l > 0 else n
        f.write(struct.pack('<12fH', *n, *a, *b, *c, 0))
np.save(out + '/_pts.npy', P)
import pickle; pickle.dump((P, T), open(out + '/_tri.pkl', 'wb'))
