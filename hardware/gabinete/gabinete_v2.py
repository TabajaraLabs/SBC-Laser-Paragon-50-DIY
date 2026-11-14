#!/usr/bin/env python3
"""
GABINETE EM CUNHA PARA A PLACA PARAGON 50 - VERSAO v2 (fiel ao croqui: duas cascas, paredes inclinadas, bisel e painel rebaixado)

Pecas:  base_v2.stl  (casca inferior, impressa de pe)
        tampa_v2.stl (casca superior com bisel e janela, impressa DE CABECA PARA BAIXO sobre a face inclinada)
        montagem_v2.stl (so para conferir, nao imprimir)
Construcao: cada peca e a UNIAO de solidos fechados (prismas convexos e tubos) que se sobrepoem;
o fatiador faz a uniao. Nao ha operacoes booleanas, entao nao ha rasgos nem buracos na malha.

Eixos do gabinete: X = comprimento da placa (esq: bloco de parafusos; dir: J4); Y = da frente (J1/J2) para o fundo; Z = para cima.
Perfil lateral (Y,Z) segue o croqui: frente 10 graus, topo 15 graus, linha de juncao inclinada, base com paredes 25/15 graus.
Uso: python3 gab2.py [pasta_saida]
"""
import math, sys, os, struct
import numpy as np
from scipy.spatial import ConvexHull

# ======================= MEDIDAS (mm) =======================
L, W   = 274.0, 144.8        # placa (medida: L perfeito, W corrigido apos teste)
FUROS  = [(33.8, 5.6), (36.7, 107.0), (141.0, 58.0), (241.5, 4.7), (243.0, 102.0)]   # (u,v) a partir do canto frontal esquerdo da placa
ENTALHES = [(42.0, 129.0), (142.0, 218.0)]       # faixas em u onde o bisel frontal e aberto (conectores J2 e J1 passam da borda)
FOLGA  = 0.4                 # folga da placa no rebaixo
ESP    = 4.5                 # espessura do bisel
REB    = 1.2                 # profundidade do rebaixo (plano de assento da placa em w = ESP-REB)
LEDGE  = 2.0                 # apoio da placa (resto e janela)
MX     = 9.0                 # largura do bisel nas laterais (croqui: 9,4)
SF     = 6.0                 # largura do bisel frente/fundo, medida ao longo da inclinacao
ANG    = 15.0                # inclinacao do painel
Z_FP   = 12.0                # altura da linha de juncao na frente (croqui 12,0)
Z_TOPF = 32.9                # altura da borda frontal do painel (croqui 32,9)
LEAN_F = 10.0                # inclinacao da frente da tampa (croqui 10)
PART_S = 24.2 / 184.0        # inclinacao da linha de juncao (croqui: sobe 24,2 em 184)
LEAN_BF, LEAN_BR = 25.0, 15.0    # inclinacao das paredes frontal e traseira da base (croqui 25 e 15)
TW     = 2.4                 # parede das cascas
TB     = 3.0                 # fundo da base
R_COL, R_PIL, R_FURO_BASE, R_FURO_PIL = 4.5, 4.0, 1.7, 1.3     # raios: colunas da placa, pilares, furo passante M3, furo de rosca M3 (autorrosqueante)
PROF_FURO = 14.0             # profundidade do furo de rosca nas colunas da placa
N = 36
# ============================================================
c, s = math.cos(math.radians(ANG)), math.sin(math.radians(ANG))
Lx = L + 2*MX
S  = W + 2*SF                                   # comprimento do painel ao longo da inclinacao
Y_TF = (Z_TOPF - Z_FP) * math.tan(math.radians(LEAN_F))
Y_R  = Y_TF + S*c                               # fundo (sem a faixa plana do croqui, que exigiria suporte na impressao)
Z_R  = Z_TOPF + S*s
Z_PR = Z_FP + PART_S*Y_R                        # altura da juncao no fundo
def z_part(y): return Z_FP + PART_S*y
Y_BB = Y_R - Z_PR*math.tan(math.radians(LEAN_BR))        # fundo da base (y no chao, parede traseira)
Y_FB = Z_FP*math.tan(math.radians(LEAN_BF))              # frente da base (y no chao)
ev = np.array([c, s]); nv = np.array([-s, c])             # (y,z): ao longo da inclinacao / normal para fora
P0 = np.array([Y_TF, Z_TOPF])

def f(u, v, w):
    """coordenadas locais da tampa -> gabinete. w=ESP e a face externa do painel."""
    yz = P0 + (v + SF)*ev + (w - ESP)*nv
    return np.array([MX + u, yz[0], yz[1]])

# ---------- primitivas ----------
def hull(pts):
    pts = np.array(pts, float); h = ConvexHull(pts); T = []
    for sp, eq in zip(h.simplices, h.equations):
        a, b, cc = pts[sp]
        if np.cross(b-a, cc-a) @ eq[:3] < 0: b, cc = cc, b
        T.append((a, b, cc))
    return T
def prisma_x(poly_yz, x0, x1):
    return hull([(x, y, z) for (y, z) in poly_yz for x in (x0, x1)])
def caixa_local(u0, u1, v0, v1, w0, w1, fn=f):
    return hull([fn(u, v, w) for u in (u0, u1) for v in (v0, v1) for w in (w0, w1)])
def tubo(r_out, r_in, zlo, zhi, hole_bottom=None, n=N, cx=0.0, cy=0.0):
    """Tubo vertical. zlo/zhi: numeros ou funcoes (x,y)->z. Furo passante, ou cego a partir do topo (hole_bottom)."""
    zl = zlo if callable(zlo) else (lambda x, y: zlo)
    zh = zhi if callable(zhi) else (lambda x, y: zhi)
    ang = [2*math.pi*i/n for i in range(n)]
    po = [(cx+r_out*math.cos(a), cy+r_out*math.sin(a)) for a in ang]
    pi_ = [(cx+r_in*math.cos(a), cy+r_in*math.sin(a)) for a in ang]
    V = lambda p, z: np.array([p[0], p[1], z])
    T = []
    for i in range(n):
        j = (i+1) % n
        a, b, ai, bi = po[i], po[j], pi_[i], pi_[j]
        # parede externa
        T += [(V(a, zl(*a)), V(b, zl(*b)), V(b, zh(*b))), (V(a, zl(*a)), V(b, zh(*b)), V(a, zh(*a)))]
        # topo (anel)
        T += [(V(a, zh(*a)), V(b, zh(*b)), V(bi, zh(*bi))), (V(a, zh(*a)), V(bi, zh(*bi)), V(ai, zh(*ai)))]
        if hole_bottom is None:
            # parede do furo (normal para o eixo) e anel inferior
            T += [(V(ai, zl(*ai)), V(bi, zh(*bi)), V(bi, zl(*bi))), (V(ai, zl(*ai)), V(ai, zh(*ai)), V(bi, zh(*bi)))]
            T += [(V(a, zl(*a)), V(bi, zl(*bi)), V(b, zl(*b))), (V(a, zl(*a)), V(ai, zl(*ai)), V(bi, zl(*bi)))]
        else:
            hb = hole_bottom
            T += [(V(ai, hb), V(bi, zh(*bi)), V(bi, hb)), (V(ai, hb), V(ai, zh(*ai)), V(bi, zh(*bi)))]
            T += [(np.array([cx, cy, hb]), V(ai, hb), V(bi, hb))]                        # piso do furo (+z)
            T += [(np.array([cx, cy, zl(cx, cy)]), V(b, zl(*b)), V(a, zl(*a)))]           # fundo fechado (-z)
    return T
def transforma(T, fn):
    return [tuple(fn(p) for p in t) for t in T]
def verifica(T, nome):
    ed = {}
    for a, b, cc in T:
        for p, q in ((a, b), (b, cc), (cc, a)):
            k = (tuple(np.round(p, 4)), tuple(np.round(q, 4))); ed[k] = ed.get(k, 0)+1
    sem = sum(1 for (p, q), v in ed.items() if ed.get((q, p), 0) != v)
    vol = sum(np.dot(a, np.cross(b, cc)) for a, b, cc in T)/6
    assert sem == 0 and vol > 0, (nome, sem, vol)
    return vol

# ---------- perfil ----------
def inter(l1, l2):
    (p1, d1), (p2, d2) = l1, l2
    A = np.array([d1, -d2]).T; t = np.linalg.solve(A, p2-p1); return p1 + t[0]*d1
def reta(p, q, off=0.0):          # reta de p para q, deslocada 'off' para a esquerda (interior, perfil anti-horario)
    p, q = np.array(p, float), np.array(q, float); d = (q-p)/np.linalg.norm(q-p); n = np.array([-d[1], d[0]])
    return (p + off*n, d)

CP = [(0, Z_FP), (Y_R, Z_PR), (Y_R, Z_R), (Y_TF, Z_TOPF)]                  # perfil externo da tampa (anti-horario)
BP = [(Y_FB, 0), (Y_BB, 0), (Y_R, Z_PR), (0, Z_FP)]                         # perfil externo da base
partline = reta((0, Z_FP), (Y_R, Z_PR))

def clip_y(poly, ya, yb):
    out = poly
    for lim, keep_ge in ((ya, True), (yb, False)):
        res = []
        for i in range(len(out)):
            p, q = out[i], out[(i+1) % len(out)]
            ip = (p[0] >= lim) if keep_ge else (p[0] <= lim); iq = (q[0] >= lim) if keep_ge else (q[0] <= lim)
            if ip: res.append(p)
            if ip != iq:
                t = (lim-p[0])/(q[0]-p[0]); res.append((lim, p[1]+t*(q[1]-p[1])))
        out = res
    return out

def parte_base():
    sh = []
    bot = reta(BP[0], BP[1], TB); rear = reta(BP[1], BP[2], TW); front = reta(BP[3], BP[0], TW)
    cr, cf = inter(bot, rear), inter(bot, front)
    rp, fp = inter(rear, partline), inter(front, partline)
    CORTE = 3.6                                                              # meio-lado do recorte quadrado p/ cabeca do parafuso
    cortes = [(x-CORTE, x+CORTE, y-CORTE, y+CORTE) for (x, y) in PIL]
    xs = sorted({0, Lx} | {v for k in cortes for v in k[:2]})
    quad = [BP[0], BP[1], cr, cf]
    for xa, xb in zip(xs, xs[1:]):
        cs = [k for k in cortes if k[0] <= xa+1e-9 and k[1] >= xb-1e-9]
        if not cs: sh.append(prisma_x(quad, xa, xb)); continue
        for (ya, yb) in [(-1e3, cs[0][2]), (cs[0][3], 1e3)]:
            q = clip_y(quad, ya, yb)
            if len(q) >= 3: sh.append(prisma_x(q, xa, xb))                       # fundo (com recortes)
    sh.append(prisma_x([BP[1], BP[2], rp, cr], 0, Lx))                       # parede traseira
    sh.append(prisma_x([BP[3], BP[0], cf, fp], 0, Lx))                       # parede frontal
    sh.append(prisma_x(BP, 0, TW)); sh.append(prisma_x(BP, Lx-TW, Lx))       # laterais
    return sh

def parte_tampa():
    sh = []
    rear = reta(CP[1], CP[2], TW); front = reta(CP[3], CP[0], TW); slope = reta(CP[2], CP[3], ESP)
    rp, fp = inter(rear, partline), inter(front, partline)
    r2, f3 = inter(rear, slope), inter(front, slope)
    sh.append(prisma_x([CP[1], CP[2], r2, rp], 0, Lx))                       # parede traseira
    sh.append(prisma_x([CP[3], CP[0], fp, f3], 0, Lx))                       # frente
    sh.append(prisma_x(CP, 0, TW)); sh.append(prisma_x(CP, Lx-TW, Lx))       # laterais
    # moldura do painel: bisel (ESP) e apoio (ESP-REB), em coordenadas locais
    U0, U1 = -MX, L + MX; V0, V1 = -SF, W + SF
    def corta(a, b, cortes):
        out, x = [], a
        for (c0, c1) in sorted(cortes):
            if c1 <= a or c0 >= b: continue
            if c0 > x: out.append((x, c0))
            x = max(x, c1)
        if x < b: out.append((x, b))
        return out
    notch = [(a-0.5, b+0.5) for a, b in ENTALHES]
    raios_corte = [(u-4.9, u+4.9) for (u, v) in FUROS if v < 12.0]           # colunas da placa atravessam o apoio frontal
    for (a, b) in corta(U0, U1, notch): sh.append(caixa_local(a, b, V0, -FOLGA, 0, ESP))        # bisel frontal (com entalhes)
    sh.append(caixa_local(U0, U1, W+FOLGA, V1, 0, ESP))                                         # bisel traseiro
    sh.append(caixa_local(U0, -FOLGA, -FOLGA, W+FOLGA, 0, ESP)); sh.append(caixa_local(L+FOLGA, U1, -FOLGA, W+FOLGA, 0, ESP))
    for (a, b) in corta(-FOLGA, L+FOLGA, notch + raios_corte): sh.append(caixa_local(a, b, -FOLGA, LEDGE, 0, ESP-REB))   # apoio frontal
    sh.append(caixa_local(-FOLGA, L+FOLGA, W-LEDGE, W+FOLGA, 0, ESP-REB))                                              # apoio traseiro
    sh.append(caixa_local(-FOLGA, LEDGE, -FOLGA, W+FOLGA, 0, ESP-REB)); sh.append(caixa_local(L-LEDGE, L+FOLGA, -FOLGA, W+FOLGA, 0, ESP-REB))
    return sh

# pilares de fixacao entre as cascas (parafusos M3 pela base) - verticais
PIL = [(MX-1.8, 15.0), (Lx-MX+1.8, 15.0), (MX-1.8, 85.0), (Lx-MX+1.8, 85.0)]   # 2 na frente e 2 no meio das laterais
def z_sub(y):    # plano inferior do painel (w=0), no gabinete
    return Z_TOPF - ESP/c + (y - Y_TF)*math.tan(math.radians(ANG))
def pecas():
    base = parte_base(); tampa = parte_tampa()
    for (x, y) in PIL:
        base.append(tubo(R_PIL+0.5, R_FURO_BASE, TB, lambda X, Y: z_part(Y), cx=x, cy=y))              # coluna da base (topo cortado pela juncao)
        tampa.append(tubo(R_PIL, R_FURO_PIL, lambda X, Y: z_part(Y), lambda X, Y: z_sub(Y) + 1.0, cx=x, cy=y))   # pilar da tampa
    # colunas da placa: na base, perpendiculares ao painel (inclinadas), furo cego para M3 autorrosqueante
    for (u, v) in FUROS:
        top = f(u, v, ESP-REB)                                       # centro do furo no plano de assento da placa
        Lt = (top[2] - TB)/c                                         # comprimento ate o chao
        T = tubo(R_COL, R_FURO_PIL, -Lt, 0.0, hole_bottom=-PROF_FURO)
        ex = np.array([1.0, 0, 0]); ey = np.array([0, ev[0], ev[1]]); en = np.array([0, nv[0], nv[1]])
        base.append(transforma(T, lambda p: top + p[0]*ex + p[1]*ey + p[2]*en))
    # recortes quadrados no fundo para a cabeca do parafuso: o fundo e uma grade de caixas sem a celula do furo
    return base, tampa

def montar():
    base, tampa = pecas()
    return base, tampa
def para_impressao_tampa(tampa):
    ey = np.array([0, ev[0], ev[1]]); en = np.array([0, nv[0], nv[1]])
    def g(p):
        d = p - np.array([0, P0[0], P0[1]]); return np.array([d[0], -(d @ ey), -(d @ en)])
    T = [tuple(g(p) for p in t) for sh in tampa for t in sh_tris(sh)]
    ymin = min(p[1] for t in T for p in t)
    return [tuple(p - np.array([0, ymin, 0]) for p in t) for t in T]
def sh_tris(sh): return sh
def achata(shells): return [t for sh in shells for t in sh]

def salva(T, fn, nome):
    with open(fn, 'wb') as fh:
        fh.write(nome.encode().ljust(80, b' ')[:80]); fh.write(struct.pack('<I', len(T)))
        for a, b, cc in T:
            n = np.cross(b-a, cc-a); l = np.linalg.norm(n); n = n/l if l > 0 else n
            fh.write(struct.pack('<12fH', *n, *a, *b, *cc, 0))

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'out_v2'; os.makedirs(out, exist_ok=True)
    base, tampa = pecas()
    for nome, sh in (('base', base), ('tampa', tampa)):
        v = sum(verifica(t, nome) for t in sh); print(nome, 'solidos', len(sh), 'volume somado (com sobreposicoes) %.0f cm3' % (v/1000))
    salva(achata(base), out+'/base_v2.stl', 'base')
    salva(para_impressao_tampa(tampa), out+'/tampa_v2.stl', 'tampa')
    salva(achata(base)+achata(tampa), out+'/montagem_v2.stl', 'montagem')
    print('externo: %.1f x %.1f (base) | altura frente %.1f, fundo %.1f' % (Lx, Y_R, Z_TOPF, Z_R))
    print('juncao frente %.1f, fundo %.1f | base chao y=%.1f..%.1f' % (Z_FP, Z_PR, Y_FB, Y_BB))
