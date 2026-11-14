#!/usr/bin/env python3
"""
GABINETE EM CUNHA PARA A PLACA PARAGON 50 (68000 CPU BOARD, LaserSurf 1994)
Gera base.stl, tampa.stl (moldura, impressa deitada) e montagem.stl.
A placa fica POR CIMA da tampa, num rebaixo de 1,2 mm, e e parafusada em colunas da base.

Eixos do gabinete: X = comprimento da placa (esquerda: bloco de parafusos; direita: J4),
Y = frente (J1/J2) -> fundo, Z = altura.  Medidas em milimetros.
Dependencias: nenhuma (so Python 3). Execute:  python3 gabinete.py
"""
import math, sys
sys.path.insert(0, '.')
from csg import *

# ======================= MEDIDAS (ajuste aqui) =======================
L, W   = 274.0, 147.0        # placa: comprimento (X) e largura (Y) - valores do v1 (W real mede 144,8; ver v2)
FUROS  = [(33.8, 5.6), (36.7, 107.0), (141.0, 58.0), (241.5, 4.7), (243.0, 102.0)]   # (X, Y) a partir do canto frontal esquerdo da placa (CONFIRMAR)
D_FURO_PLACA = 4.0           # diametro dos furos da placa (aprox.)
ANG    = 15.0                # inclinacao do painel (graus)
HF0    = 18.0                # altura da frente (parte de baixo da tampa) acima da mesa
T      = 4.0                 # espessura da tampa
REB    = 1.2                 # profundidade do rebaixo da placa
FOLGA  = 0.4                 # folga em volta da placa no rebaixo
BORDA  = 3.0                 # largura da borda externa da tampa
LEDGE  = 2.0                 # largura do apoio da placa (resto e janela aberta p/ as pontas de solda)
PAREDE = 3.0                 # paredes e fundo da base
R_COL  = 4.2                 # raio das colunas de parafuso
R_REC  = 4.7                 # raio do recorte da tampa em volta de cada coluna
D_PARAF = 2.6                # furo nas colunas (parafuso M3 autorrosqueante)
N = 48                       # facetas dos cilindros
# =====================================================================
th = math.radians(ANG); c, s_ = math.cos(th), math.sin(th)
M = FOLGA + BORDA
D = (W + 2*M) * c                       # profundidade da base em planta
XMIN, XMAX = -M, L + M

def f(p):   # coordenadas locais da tampa (u,v,w) -> mundo
    u, v, w = p
    return (u, (v + M)*c - w*s_, HF0 + (v + M)*s_ + w*c)
def zplane(y): return HF0 + y*math.tan(th)
def finv(p):   # mundo -> coordenadas locais da tampa
    x, y, z = p; q = y*c + (z - HF0)*s_
    return (x, q - M, -y*s_ + (z - HF0)*c)
def prisma(pts, z0, z1):   # prisma convexo a partir de um poligono 2D (sentido anti-horario)
    n = len(pts); P = [Poly([(x, y, z1) for x, y in pts])] + [Poly([(x, y, z0) for x, y in pts[::-1]])]
    for i in range(n):
        a, b = pts[i], pts[(i+1) % n]
        P.append(Poly([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)]))
    return Solid(P)
def barra(p0, p1, larg, z0, z1):
    dx, dy = p1[0]-p0[0], p1[1]-p0[1]; l = math.hypot(dx, dy); nx, ny = -dy/l*larg/2, dx/l*larg/2
    return prisma([(p0[0]-nx, p0[1]-ny), (p1[0]-nx, p1[1]-ny), (p1[0]+nx, p1[1]+ny), (p0[0]+nx, p0[1]+ny)], z0, z1)

# ---- tampa (moldura), em coordenadas locais ----
placa = box(XMIN, XMAX, -M-4, W+M+4, 0, T)
rebaixo = box(-FOLGA, L+FOLGA, -FOLGA, W+FOLGA, T-REB, T+1)
janela = box(LEDGE, L-LEDGE, LEDGE, W-LEDGE, -1, T+1)
tampa_l = placa.sub(rebaixo).sub(janela)
for (u, v) in FUROS:
    tampa_l = tampa_l.sub(cyl(u, v, -1, T+1, R_REC, N))
def recorte_planta():
    return box(XMIN, XMAX, 0, D, -5, 200)
tampa_mundo = tampa_l.tf(f).inter(recorte_planta())

# ---- base ----
Zmax = HF0 + D*math.tan(th) + 2
externo = box(XMIN, XMAX, 0, D, 0, Zmax)
interno = box(XMIN+PAREDE, XMAX-PAREDE, PAREDE, D-PAREDE, PAREDE, Zmax+5)
acima = box(XMIN-5, XMAX+5, -M-8, W+M+60, 0, 80).tf(f)       # tudo acima do plano da parte de baixo da tampa
base = externo.sub(interno).sub(acima)
abaixo_placa = box(XMIN-5, XMAX+5, -M-60, W+M+60, -120, T-REB).tf(f)   # abaixo do plano do fundo da placa
chao = box(XMIN-5, XMAX+5, -5, D+5, PAREDE-0.5, 300)
for (u, v) in FUROS:
    col = cyl(u, v, -120, T-REB, R_COL, N).tf(f).inter(chao)
    base = base.union(col)
for (u, v) in FUROS:
    base = base.sub(cyl(u, v, -14, T-REB+1, D_PARAF/2, 24).tf(f))
# rebaixos para pes de borracha (D 14 x 1 mm)
for (x, y) in [(25, 18), (XMAX-M-25+M, 18), (25, D-18), (XMAX-25, D-18)]:
    base = base.sub(cyl(x, y, -1, 1.0, 7.0, 32))

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    print('base   tri', base.stl(out+'/base.stl', 'base'), 'vol cm3 %.1f' % (base.volume()/1000))
    # tampa para imprimir: deitada (rebaixo para cima); as pontas ficam inclinadas 15 graus para alinhar com as paredes da base
    tampa_imp = tampa_mundo.tf(finv)
    print('tampa  tri', tampa_imp.stl(out+'/tampa.stl', 'tampa'), 'vol cm3 %.1f' % (tampa_imp.volume()/1000))
    # gabarito: barras com 5 pinos para conferir a posicao dos furos da placa antes de imprimir a base
    h = FUROS; g = None
    for a, b in [(0,1),(3,4),(0,3),(1,4),(2,0),(2,4)]:
        bar = barra(h[a], h[b], 7.0, 0, 2.0); g = bar if g is None else g.union(bar)
    for (u, v) in h: g = g.union(cyl(u, v, 0, 6.0, (D_FURO_PLACA-0.4)/2, 32))
    print('gabarito tri', g.stl(out+'/gabarito_furos.stl', 'gabarito'), 'vol cm3 %.1f' % (g.volume()/1000))
    mont = Solid(base.clone().p + tampa_mundo.clone().p)
    print('montagem tri', mont.stl(out+'/montagem.stl', 'montagem'))
    print('Planta da base: %.1f x %.1f mm, altura frente %.1f / fundo %.1f mm' % (XMAX-XMIN, D, HF0, HF0 + D*math.tan(th) + T/c))
