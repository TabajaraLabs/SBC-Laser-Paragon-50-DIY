"""Mini CSG (BSP) em Python puro, porta do csg.js de Evan Wallace. Poligonos convexos; STL binario."""
import math, struct, sys
sys.setrecursionlimit(1000000)
EPS = 1e-6
def sub(a,b): return (a[0]-b[0],a[1]-b[1],a[2]-b[2])
def add(a,b): return (a[0]+b[0],a[1]+b[1],a[2]+b[2])
def mul(a,k): return (a[0]*k,a[1]*k,a[2]*k)
def dot(a,b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def unit(a):
    l=math.sqrt(dot(a,a)); return (a[0]/l,a[1]/l,a[2]/l)
def lerp(a,b,t): return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t)
class Plane:
    __slots__=('n','w')
    def __init__(s,n,w): s.n=n; s.w=w
    @staticmethod
    def from_points(a,b,c):
        n=unit(cross(sub(b,a),sub(c,a))); return Plane(n,dot(n,a))
    def flipped(s): return Plane(mul(s.n,-1),-s.w)
    def split(s,poly,cf,cb,f,b):
        COP,FR,BK,SP=0,1,2,3
        pt=0; types=[]
        for v in poly.v:
            t=dot(s.n,v)-s.w
            ty=BK if t<-EPS else (FR if t>EPS else COP)
            pt|=ty; types.append(ty)
        if pt==COP:
            (cf if dot(s.n,poly.plane.n)>0 else cb).append(poly)
        elif pt==FR: f.append(poly)
        elif pt==BK: b.append(poly)
        else:
            fv=[];bv=[]; n=len(poly.v)
            for i in range(n):
                j=(i+1)%n; ti=types[i]; tj=types[j]; vi=poly.v[i]; vj=poly.v[j]
                if ti!=BK: fv.append(vi)
                if ti!=FR: bv.append(vi)
                if (ti|tj)==SP:
                    t=(s.w-dot(s.n,vi))/dot(s.n,sub(vj,vi)); v=lerp(vi,vj,t); fv.append(v); bv.append(v)
            if len(fv)>=3: f.append(Poly(fv,poly.plane))
            if len(bv)>=3: b.append(Poly(bv,poly.plane))
class Poly:
    __slots__=('v','plane')
    def __init__(s,v,plane=None):
        s.v=v; s.plane=plane or Plane.from_points(v[0],v[1],v[2])
    def flip(s): s.v=s.v[::-1]; s.plane=s.plane.flipped()
class Node:
    def __init__(s,polys=None):
        s.plane=None; s.front=None; s.back=None; s.polys=[]
        if polys: s.build(polys)
    def clone(s):
        n=Node(); n.plane=s.plane; n.front=s.front.clone() if s.front else None
        n.back=s.back.clone() if s.back else None; n.polys=[Poly(list(p.v),p.plane) for p in s.polys]; return n
    def invert(s):
        for p in s.polys: p.flip()
        if s.plane: s.plane=s.plane.flipped()
        if s.front: s.front.invert()
        if s.back: s.back.invert()
        s.front,s.back=s.back,s.front
    def clip(s,polys):
        if not s.plane: return list(polys)
        f=[];b=[]
        for p in polys: s.plane.split(p,f,b,f,b)
        if s.front: f=s.front.clip(f)
        b=s.back.clip(b) if s.back else []
        return f+b
    def clipTo(s,bsp):
        s.polys=bsp.clip(s.polys)
        if s.front: s.front.clipTo(bsp)
        if s.back: s.back.clipTo(bsp)
    def all(s):
        r=list(s.polys)
        if s.front: r+=s.front.all()
        if s.back: r+=s.back.all()
        return r
    def build(s,polys):
        if not polys: return
        if not s.plane: s.plane=polys[0].plane
        f=[];b=[]
        for p in polys: s.plane.split(p,s.polys,s.polys,f,b)
        if f:
            if not s.front: s.front=Node()
            s.front.build(f)
        if b:
            if not s.back: s.back=Node()
            s.back.build(b)
class Solid:
    def __init__(s,polys): s.p=polys
    def clone(s): return Solid([Poly(list(p.v),p.plane) for p in s.p])
    def union(s,o):
        a=Node(s.clone().p); b=Node(o.clone().p)
        a.clipTo(b); b.clipTo(a); b.invert(); b.clipTo(a); b.invert(); a.build(b.all()); return Solid(a.all())
    def sub(s,o):
        a=Node(s.clone().p); b=Node(o.clone().p)
        a.invert(); a.clipTo(b); b.clipTo(a); b.invert(); b.clipTo(a); b.invert(); a.build(b.all()); a.invert(); return Solid(a.all())
    def inter(s,o):
        a=Node(s.clone().p); b=Node(o.clone().p)
        a.invert(); b.clipTo(a); b.invert(); a.clipTo(b); b.clipTo(a); a.build(b.all()); a.invert(); return Solid(a.all())
    def tf(s,fn):
        out=[]
        for p in s.p:
            out.append(Poly([fn(v) for v in p.v]))
        return Solid(out)
    def tris(s):
        T=[]
        for p in s.p:
            v=p.v
            for i in range(1,len(v)-1): T.append((v[0],v[i],v[i+1]))
        return T
    def volume(s):
        V=0
        for a,b,c in s.tris(): V+=dot(a,cross(b,c))/6
        return V
    def stl(s,fn,name='solid'):
        T=s.tris(); T=[t for t in T if dot(cross(sub(t[1],t[0]),sub(t[2],t[0])),cross(sub(t[1],t[0]),sub(t[2],t[0])))>1e-14]
        with open(fn,'wb') as f:
            f.write(name.encode()[:80].ljust(80,b' ')); f.write(struct.pack('<I',len(T)))
            for a,b,c in T:
                n=unit(cross(sub(b,a),sub(c,a))); f.write(struct.pack('<12fH',*n,*a,*b,*c,0))
        return len(T)
def box(x0,x1,y0,y1,z0,z1):
    P=[]
    def q(a,b,c,d): P.append(Poly([a,b,c,d]))
    A=(x0,y0,z0);B=(x1,y0,z0);C=(x1,y1,z0);D=(x0,y1,z0);E=(x0,y0,z1);F=(x1,y0,z1);G=(x1,y1,z1);H=(x0,y1,z1)
    q(D,C,B,A); q(E,F,G,H); q(A,B,F,E); q(C,D,H,G); q(D,A,E,H); q(B,C,G,F)
    return Solid(P)
def cyl(cx,cy,z0,z1,r,n=48):
    P=[]; top=[];bot=[]
    for i in range(n):
        a0=2*math.pi*i/n; a1=2*math.pi*(i+1)/n
        p0=(cx+r*math.cos(a0),cy+r*math.sin(a0)); p1=(cx+r*math.cos(a1),cy+r*math.sin(a1))
        P.append(Poly([(p0[0],p0[1],z0),(p1[0],p1[1],z0),(p1[0],p1[1],z1),(p0[0],p0[1],z1)]))
        top.append((p0[0],p0[1],z1)); bot.append((p0[0],p0[1],z0))
    P.append(Poly(top)); P.append(Poly(bot[::-1]))
    return Solid(P)
