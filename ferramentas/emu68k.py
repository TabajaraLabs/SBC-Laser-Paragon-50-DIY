#!/usr/bin/env python3
"""emu68k.py - emulador minimo de 68000 (sem tempo/ciclos) para testar o CP/M-68K no sandbox."""
import sys

M32 = 0xFFFFFFFF
MASK = {1: 0xFF, 2: 0xFFFF, 4: 0xFFFFFFFF}
MSB = {1: 0x80, 2: 0x8000, 4: 0x80000000}

def sx(v, size):
    v &= MASK[size]
    return v - (MASK[size] + 1) if v & MSB[size] else v

class Halt(Exception): pass
class Illegal(Exception): pass

class CPU:
    def __init__(self):
        self.mem = bytearray(1 << 24)
        self.d = [0] * 8
        self.a = [0] * 8
        self.usp = 0
        self.pc = 0
        self.sr = 0x2700
        self.steps = 0
        self.rx = []          # bytes que a placa vai ler
        self.tx = bytearray() # bytes que a placa escreveu
        self.on_tx = None
        self.watch = {}       # pc -> callback
        self.trace = False

    # ---------------- memoria
    def rd(self, addr, size):
        addr &= 0xFFFFFF
        if 0xFA0000 <= addr < 0xFA0020: return self.duart_rd(addr, size)
        if size == 1: return self.mem[addr]
        if addr & 1: raise Illegal('address error read %06X pc=%06X' % (addr, self.pc))
        if size == 2: return (self.mem[addr] << 8) | self.mem[addr + 1]
        return (self.mem[addr] << 24) | (self.mem[addr + 1] << 16) | (self.mem[addr + 2] << 8) | self.mem[addr + 3]

    def wr(self, addr, size, v):
        addr &= 0xFFFFFF
        v &= MASK[size]
        if 0xFA0000 <= addr < 0xFA0020: return self.duart_wr(addr, size, v)
        if addr >= 0xF80000: raise Illegal('write to ROM %06X pc=%06X' % (addr, self.pc))
        if size == 1: self.mem[addr] = v; return
        if addr & 1: raise Illegal('address error write %06X pc=%06X' % (addr, self.pc))
        if size == 2:
            self.mem[addr] = v >> 8; self.mem[addr + 1] = v & 0xFF
        else:
            self.mem[addr] = v >> 24; self.mem[addr + 1] = (v >> 16) & 0xFF
            self.mem[addr + 2] = (v >> 8) & 0xFF; self.mem[addr + 3] = v & 0xFF

    def duart_rd(self, addr, size):
        if addr == 0xFA0003:
            return (1 if self.rx else 0) | 4 | 8
        if addr == 0xFA0007:
            return self.rx.pop(0) if self.rx else 0
        return 0

    def duart_wr(self, addr, size, v):
        if addr in (0xFA0006, 0xFA0007):
            b = v & 0xFF
            self.tx.append(b)
            if self.on_tx: self.on_tx(b)

    # ---------------- busca
    def f16(self):
        v = self.rd(self.pc, 2); self.pc += 2; return v
    def f32(self):
        v = self.rd(self.pc, 4); self.pc += 4; return v

    # ---------------- flags
    def flag(self, bit): return (self.sr >> bit) & 1
    def setf(self, bit, v):
        if v: self.sr |= 1 << bit
        else: self.sr &= ~(1 << bit)
    C, V, Z, N, X = 0, 1, 2, 3, 4

    def nz(self, r, size):
        self.setf(self.N, r & MSB[size]); self.setf(self.Z, (r & MASK[size]) == 0)

    def logic_flags(self, r, size):
        self.nz(r, size); self.setf(self.V, 0); self.setf(self.C, 0)

    def add(self, s, d, size, x=0, keepz=False):
        m = MASK[size]; s &= m; d &= m
        t = s + d + x; r = t & m
        c = t > m
        v = ((s ^ r) & (d ^ r) & MSB[size]) != 0
        self.setf(self.C, c); self.setf(self.X, c); self.setf(self.V, v)
        self.setf(self.N, r & MSB[size])
        if keepz:
            if r: self.setf(self.Z, 0)
        else: self.setf(self.Z, r == 0)
        return r

    def sub(self, s, d, size, x=0, keepz=False, store_x=True):
        m = MASK[size]; s &= m; d &= m
        r = (d - s - x) & m
        c = (s + x) > d
        v = ((s ^ d) & (r ^ d) & MSB[size]) != 0
        self.setf(self.C, c)
        if store_x: self.setf(self.X, c)
        self.setf(self.V, v)
        self.setf(self.N, r & MSB[size])
        if keepz:
            if r: self.setf(self.Z, 0)
        else: self.setf(self.Z, r == 0)
        return r

    def cond(self, cc):
        c, v, z, n = self.flag(0), self.flag(1), self.flag(2), self.flag(3)
        return [True, False, (not c) and (not z), c or z, not c, bool(c), not z, bool(z),
                not v, bool(v), not n, bool(n), n == v, n != v, (not z) and n == v, bool(z) or n != v][cc]

    # ---------------- stack / modos
    def push32(self, v):
        self.a[7] = (self.a[7] - 4) & M32; self.wr(self.a[7], 4, v)
    def push16(self, v):
        self.a[7] = (self.a[7] - 2) & M32; self.wr(self.a[7], 2, v)
    def pop32(self):
        v = self.rd(self.a[7], 4); self.a[7] = (self.a[7] + 4) & M32; return v
    def pop16(self):
        v = self.rd(self.a[7], 2); self.a[7] = (self.a[7] + 2) & M32; return v

    def set_sr(self, v):
        old_s = self.sr & 0x2000
        new_s = v & 0x2000
        if old_s != new_s:
            if old_s: self.ssp = self.a[7]; self.a[7] = self.usp
            else: self.usp = self.a[7]; self.a[7] = getattr(self, 'ssp', 0)
        self.sr = v & 0xFFFF

    def exception(self, vec, pcval=None):
        sr = self.sr
        if not (sr & 0x2000):
            self.usp = self.a[7]; self.a[7] = getattr(self, 'ssp', self.a[7])
            self.sr |= 0x2000
        self.sr &= ~0x8000
        self.push32(self.pc if pcval is None else pcval)
        self.push16(sr)
        self.pc = self.rd(vec * 4, 4)

    def ea(self, mode, reg, size):
        if mode == 0: return ('d', reg)
        if mode == 1: return ('a', reg)
        if mode == 2: return ('m', self.a[reg])
        if mode == 3:
            ad = self.a[reg]; self.a[reg] = (ad + (2 if size == 1 and reg == 7 else size)) & M32
            return ('m', ad)
        if mode == 4:
            self.a[reg] = (self.a[reg] - (2 if size == 1 and reg == 7 else size)) & M32
            return ('m', self.a[reg])
        if mode == 5:
            return ('m', (self.a[reg] + sx(self.f16(), 2)) & M32)
        if mode == 6:
            e = self.f16()
            return ('m', (self.a[reg] + sx(e & 0xFF, 1) + self.idx(e)) & M32)
        if reg == 0: return ('m', sx(self.f16(), 2) & M32)
        if reg == 1: return ('m', self.f32())
        if reg == 2:
            base = self.pc; return ('m', (base + sx(self.f16(), 2)) & M32)
        if reg == 3:
            base = self.pc; e = self.f16()
            return ('m', (base + sx(e & 0xFF, 1) + self.idx(e)) & M32)
        if reg == 4:
            if size == 4: return ('i', self.f32())
            v = self.f16()
            return ('i', v & MASK[size])
        raise Illegal('bad ea %d %d pc=%06X' % (mode, reg, self.pc))

    def idx(self, e):
        r = (e >> 12) & 7
        v = self.a[r] if e & 0x8000 else self.d[r]
        return sx(v, 4) if e & 0x800 else sx(v, 2)

    def get(self, loc, size):
        k, n = loc
        if k == 'd': return self.d[n] & MASK[size]
        if k == 'a': return self.a[n] & MASK[size]
        if k == 'i': return n & MASK[size]
        return self.rd(n, size)

    def put(self, loc, size, v):
        k, n = loc
        v &= MASK[size]
        if k == 'd':
            self.d[n] = (self.d[n] & ~MASK[size] & M32) | v
        elif k == 'a':
            self.a[n] = sx(v, size) & M32
        elif k == 'm':
            self.wr(n, size, v)
        else: raise Illegal('write to immediate')

    # ---------------- execucao
    def step(self):
        pc0 = self.pc
        if pc0 in self.watch:
            self.watch[pc0](self)
        t0 = self.sr & 0x8000
        op = self.f16()
        self.steps += 1
        if self.trace: print('%06X %04X' % (pc0, op), file=sys.stderr)
        g = op >> 12
        try:
            getattr(self, 'g%X' % g)(op)
        except Illegal:
            raise
        except KeyError:
            raise
        if t0: self.exception(9)
        return

    def run(self, maxsteps):
        n = 0
        while n < maxsteps:
            self.step(); n += 1
        return n

    # ---- group 0
    def g0(self, op):
        mode = (op >> 3) & 7; reg = op & 7
        if op & 0x100:  # bit ops dynamic / movep
            if mode == 1: raise Illegal('movep')
            self.bitop((op >> 6) & 3, self.d[(op >> 9) & 7], mode, reg); return
        t = (op >> 9) & 7
        if t == 4:
            n = self.f16() & 0xFF
            self.bitop((op >> 6) & 3, n, mode, reg); return
        size = {0: 1, 1: 2, 2: 4}.get((op >> 6) & 3)
        if size is None: raise Illegal('g0 %04X' % op)
        if (op & 0x3F) == 0x3C:   # to CCR / SR
            if size == 1:
                v = self.f16() & 0xFF; cur = self.sr & 0xFF
                nv = {0: cur | v, 1: cur & v, 5: cur ^ v}[t]
                self.sr = (self.sr & 0xFF00) | (nv & 0xFF)
            else:
                v = self.f16(); cur = self.sr
                nv = {0: cur | v, 1: cur & v, 5: cur ^ v}[t]
                self.set_sr(nv)
            return
        imm = self.f32() if size == 4 else (self.f16() & MASK[size])
        loc = self.ea(mode, reg, size)
        dv = self.get(loc, size)
        if t == 0: r = dv | imm; self.logic_flags(r, size); self.put(loc, size, r)
        elif t == 1: r = dv & imm; self.logic_flags(r, size); self.put(loc, size, r)
        elif t == 2: r = self.sub(imm, dv, size); self.put(loc, size, r)
        elif t == 3: r = self.add(imm, dv, size); self.put(loc, size, r)
        elif t == 5: r = dv ^ imm; self.logic_flags(r, size); self.put(loc, size, r)
        elif t == 6: self.sub(imm, dv, size, store_x=False)
        else: raise Illegal('g0 %04X' % op)

    def bitop(self, kind, n, mode, reg):
        if mode == 0:
            size = 4; n &= 31
        else:
            size = 1; n &= 7
        loc = self.ea(mode, reg, size)
        v = self.get(loc, size)
        self.setf(self.Z, ((v >> n) & 1) == 0)
        if kind == 1: v ^= 1 << n
        elif kind == 2: v &= ~(1 << n)
        elif kind == 3: v |= 1 << n
        if kind: self.put(loc, size, v)

    # ---- MOVE
    def move(self, op, size):
        src = self.ea((op >> 3) & 7, op & 7, size)
        v = self.get(src, size)
        dmode = (op >> 6) & 7; dreg = (op >> 9) & 7
        if dmode == 1:
            self.a[dreg] = sx(v, size) & M32; return
        dst = self.ea(dmode, dreg, size)
        self.logic_flags(v, size)
        self.put(dst, size, v)
    def g1(self, op): self.move(op, 1)
    def g2(self, op): self.move(op, 4)
    def g3(self, op): self.move(op, 2)

    # ---- group 4
    def g4(self, op):
        mode = (op >> 3) & 7; reg = op & 7
        if op == 0x4E71: return
        if op == 0x4E75: self.pc = self.pop32(); return
        if op == 0x4E73:
            sr = self.pop16(); pc = self.pop32(); self.set_sr(sr); self.pc = pc; return
        if op == 0x4E77:
            c = self.pop16(); self.sr = (self.sr & 0xFF00) | (c & 0xFF); self.pc = self.pop32(); return
        if op == 0x4E70: return
        if op == 0x4AFC:
            if getattr(self, 'illegal_exc', False): self.exception(4, self.pc - 2); return
            raise Illegal('ILLEGAL pc=%06X' % (self.pc - 2))
        if op == 0x4E72:
            self.f16(); raise Halt('STOP')
        if (op & 0xFFF0) == 0x4E40:
            self.exception(32 + (op & 15)); return
        if (op & 0xFFF8) == 0x4E50:
            v = sx(self.f16(), 2)
            self.push32(self.a[reg]); self.a[reg] = self.a[7]; self.a[7] = (self.a[7] + v) & M32; return
        if (op & 0xFFF8) == 0x4E58:
            self.a[7] = self.a[reg]; self.a[reg] = self.pop32(); return
        if (op & 0xFFF8) == 0x4E60:
            self.usp = self.a[reg]; return
        if (op & 0xFFF8) == 0x4E68:
            self.a[reg] = self.usp; return
        if (op & 0xFFC0) == 0x4EC0:
            self.pc = self.ea(mode, reg, 4)[1]; return
        if (op & 0xFFC0) == 0x4E80:
            a = self.ea(mode, reg, 4)[1]; self.push32(self.pc); self.pc = a; return
        if (op & 0xF1C0) == 0x41C0:
            self.a[(op >> 9) & 7] = self.ea(mode, reg, 4)[1]; return
        if (op & 0xFFC0) == 0x4840 and mode != 0:
            self.push32(self.ea(mode, reg, 4)[1]); return
        if (op & 0xFFF8) == 0x4840:
            v = self.d[reg]; self.d[reg] = ((v << 16) | (v >> 16)) & M32; self.logic_flags(self.d[reg], 4); return
        if (op & 0xFFF8) == 0x4880: self.put(('d', reg), 2, sx(self.d[reg], 1)); self.logic_flags(self.d[reg], 2); return
        if (op & 0xFFF8) == 0x48C0:
            self.d[reg] = sx(self.d[reg], 2) & M32; self.logic_flags(self.d[reg], 4); return
        if (op & 0xFB80) == 0x4880:       # MOVEM
            size = 4 if op & 0x40 else 2
            mask = self.f16()
            if op & 0x400:   # mem -> reg
                loc = self.ea(mode, reg, size)
                ad = loc[1]
                for i in range(16):
                    if mask & (1 << i):
                        v = self.rd(ad, size)
                        val = sx(v, size) & M32
                        if i < 8: self.d[i] = val
                        else: self.a[i - 8] = val
                        ad += size
                if mode == 3: self.a[reg] = ad & M32
            else:
                if mode == 4:
                    ad = self.a[reg]
                    for i in range(16):
                        if mask & (1 << i):
                            r = 15 - i
                            v = self.d[r] if r < 8 else self.a[r - 8]
                            ad -= size; self.wr(ad, size, v)
                    self.a[reg] = ad & M32
                else:
                    ad = self.ea(mode, reg, size)[1]
                    for i in range(16):
                        if mask & (1 << i):
                            v = self.d[i] if i < 8 else self.a[i - 8]
                            self.wr(ad, size, v); ad += size
            return
        if (op & 0xFFC0) == 0x40C0:   # move from SR
            self.put(self.ea(mode, reg, 2), 2, self.sr); return
        if (op & 0xFFC0) == 0x44C0:
            self.sr = (self.sr & 0xFF00) | (self.get(self.ea(mode, reg, 2), 2) & 0xFF); return
        if (op & 0xFFC0) == 0x46C0:
            self.set_sr(self.get(self.ea(mode, reg, 2), 2)); return
        if (op & 0xFFC0) == 0x4AC0:   # TAS
            loc = self.ea(mode, reg, 1); v = self.get(loc, 1)
            self.logic_flags(v, 1); self.put(loc, 1, v | 0x80); return
        sz = {0: 1, 1: 2, 2: 4}.get((op >> 6) & 3)
        top = op & 0xFF00
        if sz and top in (0x4200, 0x4400, 0x4600, 0x4A00, 0x4000):
            loc = self.ea(mode, reg, sz)
            if top == 0x4200:
                self.put(loc, sz, 0); self.setf(self.Z, 1); self.setf(self.N, 0); self.setf(self.V, 0); self.setf(self.C, 0)
            elif top == 0x4400:
                v = self.get(loc, sz); r = self.sub(v, 0, sz); self.put(loc, sz, r)
            elif top == 0x4000:
                v = self.get(loc, sz); r = self.sub(v, 0, sz, x=self.flag(self.X), keepz=True); self.put(loc, sz, r)
            elif top == 0x4600:
                r = ~self.get(loc, sz) & MASK[sz]; self.logic_flags(r, sz); self.put(loc, sz, r)
            else:
                self.logic_flags(self.get(loc, sz), sz)
            return
        raise Illegal('g4 %04X pc=%06X' % (op, self.pc - 2))

    # ---- group 5
    def g5(self, op):
        mode = (op >> 3) & 7; reg = op & 7
        if (op & 0xC0) == 0xC0:
            cc = (op >> 8) & 15
            if mode == 1:    # DBcc
                disp = sx(self.f16(), 2); base = self.pc - 2
                if not self.cond(cc):
                    v = (self.d[reg] - 1) & 0xFFFF
                    self.d[reg] = (self.d[reg] & 0xFFFF0000) | v
                    if v != 0xFFFF: self.pc = (base + disp) & M32
                return
            loc = self.ea(mode, reg, 1)
            self.put(loc, 1, 0xFF if self.cond(cc) else 0); return
        size = {0: 1, 1: 2, 2: 4}[(op >> 6) & 3]
        q = (op >> 9) & 7 or 8
        loc = self.ea(mode, reg, size)
        if loc[0] == 'a':
            self.a[reg] = (self.a[reg] - q if op & 0x100 else self.a[reg] + q) & M32; return
        dv = self.get(loc, size)
        r = self.sub(q, dv, size) if op & 0x100 else self.add(q, dv, size)
        self.put(loc, size, r)

    # ---- Bcc
    def g6(self, op):
        cc = (op >> 8) & 15; d8 = op & 0xFF
        base = self.pc
        disp = sx(self.f16(), 2) if d8 == 0 else sx(d8, 1)
        if cc == 1:
            self.push32(self.pc); self.pc = (base + disp) & M32; return
        if self.cond(cc) if cc else True:
            self.pc = (base + disp) & M32

    def g7(self, op):
        v = sx(op & 0xFF, 1) & M32
        self.d[(op >> 9) & 7] = v; self.logic_flags(v, 4)

    # ---- arithmetic groups
    def alu(self, op, kind):
        mode = (op >> 3) & 7; reg = op & 7; r = (op >> 9) & 7
        opm = (op >> 6) & 7
        if opm in (3, 7):   # ADDA/SUBA/CMPA, MULU/DIVU etc handled by caller
            return False
        size = {0: 1, 1: 2, 2: 4, 4: 1, 5: 2, 6: 4}[opm]
        if opm < 4:
            loc = self.ea(mode, reg, size)
            s = self.get(loc, size); d = self.get(('d', r), size)
            if kind == 'add': res = self.add(s, d, size)
            elif kind == 'sub': res = self.sub(s, d, size)
            elif kind == 'and': res = d & s; self.logic_flags(res, size)
            elif kind == 'or': res = d | s; self.logic_flags(res, size)
            elif kind == 'cmp': self.sub(s, d, size, store_x=False); return True
            self.put(('d', r), size, res)
        else:
            if kind in ('add', 'sub') and mode in (0, 1):   # ADDX/SUBX
                x = self.flag(self.X)
                if mode == 0:
                    s = self.get(('d', reg), size); d = self.get(('d', r), size)
                    res = self.add(s, d, size, x, True) if kind == 'add' else self.sub(s, d, size, x, True)
                    self.put(('d', r), size, res)
                else:
                    self.a[reg] -= size; self.a[r] -= size
                    s = self.rd(self.a[reg], size); d = self.rd(self.a[r], size)
                    res = self.add(s, d, size, x, True) if kind == 'add' else self.sub(s, d, size, x, True)
                    self.wr(self.a[r], size, res)
                return True
            loc = self.ea(mode, reg, size)
            s = self.get(('d', r), size); d = self.get(loc, size)
            if kind == 'add': res = self.add(s, d, size)
            elif kind == 'sub': res = self.sub(s, d, size)
            elif kind == 'and': res = d & s; self.logic_flags(res, size)
            elif kind == 'or': res = d | s; self.logic_flags(res, size)
            elif kind == 'eor': res = d ^ s; self.logic_flags(res, size)
            self.put(loc, size, res)
        return True

    def g8(self, op):
        mode = (op >> 3) & 7; reg = op & 7; r = (op >> 9) & 7
        if (op & 0x1F0) == 0x100: raise Illegal('sbcd')
        if (op & 0xC0) == 0xC0:   # DIVU / DIVS
            s = self.get(self.ea(mode, reg, 2), 2)
            dv = self.d[r]
            if s == 0:
                self.exception(5); return
            if op & 0x100:
                a = sx(dv, 4); b = sx(s, 2)
                q = abs(a) // abs(b); rem = abs(a) % abs(b)
                if (a < 0) != (b < 0): q = -q
                if a < 0: rem = -rem
                if q < -32768 or q > 32767: self.setf(self.V, 1); return
            else:
                q = dv // s; rem = dv % s
                if q > 0xFFFF: self.setf(self.V, 1); return
            self.d[r] = ((rem & 0xFFFF) << 16) | (q & 0xFFFF)
            self.nz(q, 2); self.setf(self.V, 0); self.setf(self.C, 0); return
        self.alu(op, 'or')

    def g9(self, op):
        if (op & 0xC0) == 0xC0:
            size = 4 if op & 0x100 else 2
            mode = (op >> 3) & 7; reg = op & 7
            s = sx(self.get(self.ea(mode, reg, size), size), size)
            r = (op >> 9) & 7
            self.a[r] = (self.a[r] - s) & M32; return
        self.alu(op, 'sub')

    def gD(self, op):
        if (op & 0xC0) == 0xC0:
            size = 4 if op & 0x100 else 2
            mode = (op >> 3) & 7; reg = op & 7
            s = sx(self.get(self.ea(mode, reg, size), size), size)
            r = (op >> 9) & 7
            self.a[r] = (self.a[r] + s) & M32; return
        self.alu(op, 'add')

    def gB(self, op):
        mode = (op >> 3) & 7; reg = op & 7; r = (op >> 9) & 7
        opm = (op >> 6) & 7
        if opm in (3, 7):    # CMPA
            size = 4 if opm == 7 else 2
            s = sx(self.get(self.ea(mode, reg, size), size), size) & M32
            self.sub(s, self.a[r], 4, store_x=False); return
        if opm >= 4:
            if mode == 1:    # CMPM
                size = {4: 1, 5: 2, 6: 4}[opm]
                s = self.rd(self.a[reg], size); self.a[reg] += size
                d = self.rd(self.a[r], size); self.a[r] += size
                self.sub(s, d, size, store_x=False); return
            self.alu(op, 'eor'); return
        self.alu(op, 'cmp')

    def gC(self, op):
        mode = (op >> 3) & 7; reg = op & 7; r = (op >> 9) & 7
        if (op & 0xC0) == 0xC0:   # MULU/MULS
            s = self.get(self.ea(mode, reg, 2), 2)
            if op & 0x100: p = (sx(s, 2) * sx(self.d[r], 2)) & M32
            else: p = (s * (self.d[r] & 0xFFFF)) & M32
            self.d[r] = p; self.nz(p, 4); self.setf(self.V, 0); self.setf(self.C, 0); return
        if (op & 0x1F8) == 0x140: self.d[r], self.d[reg] = self.d[reg], self.d[r]; return
        if (op & 0x1F8) == 0x148: self.a[r], self.a[reg] = self.a[reg], self.a[r]; return
        if (op & 0x1F8) == 0x188: self.d[r], self.a[reg] = self.a[reg], self.d[r]; return
        if (op & 0x1F0) == 0x100: raise Illegal('abcd')
        self.alu(op, 'and')

    # ---- shifts
    def gE(self, op):
        reg = op & 7
        if (op & 0xC0) == 0xC0:    # memory shift
            t = (op >> 9) & 3; left = (op >> 8) & 1
            loc = self.ea((op >> 3) & 7, reg, 2)
            v = self.get(loc, 2)
            r = self.shift(t, left, v, 1, 2)
            self.put(loc, 2, r); return
        size = {0: 1, 1: 2, 2: 4}[(op >> 6) & 3]
        t = (op >> 3) & 3; left = (op >> 8) & 1
        cnt = (op >> 9) & 7
        if op & 0x20: cnt = self.d[cnt] & 63
        else: cnt = cnt or 8
        v = self.d[reg] & MASK[size]
        r = self.shift(t, left, v, cnt, size)
        self.put(('d', reg), size, r)

    def shift(self, t, left, v, cnt, size):
        m = MASK[size]; bits = size * 8
        c = None; vflag = 0
        if cnt == 0:
            self.nz(v, size); self.setf(self.V, 0)
            self.setf(self.C, self.flag(self.X) if t == 2 else 0); return v
        for _ in range(cnt):
            if t == 0:   # AS
                if left:
                    c = (v >> (bits - 1)) & 1; nv = (v << 1) & m
                    if (nv ^ v) & MSB[size]: vflag = 1
                    v = nv
                else:
                    c = v & 1; v = (v >> 1) | (v & MSB[size])
            elif t == 1:  # LS
                if left: c = (v >> (bits - 1)) & 1; v = (v << 1) & m
                else: c = v & 1; v >>= 1
            elif t == 2:  # ROX
                x = self.flag(self.X)
                if left: c = (v >> (bits - 1)) & 1; v = ((v << 1) | x) & m
                else: c = v & 1; v = (v >> 1) | (x << (bits - 1))
                self.setf(self.X, c)
            else:         # RO
                if left: c = (v >> (bits - 1)) & 1; v = ((v << 1) | c) & m
                else: c = v & 1; v = (v >> 1) | (c << (bits - 1))
        self.setf(self.C, c)
        if t != 3 and t != 2: self.setf(self.X, c)
        self.setf(self.V, vflag if t == 0 else 0)
        self.nz(v, size)
        return v

    def gA(self, op): raise Illegal('line A %04X' % op)
    def gF(self, op): raise Illegal('line F %04X' % op)
