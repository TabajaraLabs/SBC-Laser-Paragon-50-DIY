"""t_per.py - testa os comandos ADC ADL DAC RTC (modulo PER1) e os textos de I/Q no emulador, com modelos do AD7875, dos DACs e do DS1302.
uso: python3 t_per.py imagem.bin [rtc_presente=1]"""
import sys, struct
sys.path.insert(0, '.')
from emu68k import CPU, Illegal, Halt
from t_fv4 import Flash

IMG = sys.argv[1]
RTC_PRESENT = (sys.argv[2] != '0') if len(sys.argv) > 2 else True
B0 = open(IMG, 'rb').read()


class I2C:
    def __init__(s):
        s.regs = bytearray(19); s.ptr = 0; s.sdam = 1; s.sdas = 1; s.scl = 1
        s.mode = 'idle'; s.nb = 0; s.sh = 0; s.rw = 0; s.first = True; s.out = 0; s.mack = 0; s.after = 'idle'
    def line(s): return s.sdam & s.sdas
    def load(s):
        s.out = s.regs[s.ptr] if s.ptr < 19 else 0xFF; s.sdas = (s.out >> 7) & 1
    def update(s, v):
        nsda = 0 if v & 0x80 else 1; nscl = 0 if v & 0x400 else 1
        if nsda != s.sdam:
            old = s.line(); s.sdam = nsda; l = s.line()
            if s.scl and old != l:
                if l == 0: s.mode = 'addr'; s.nb = 0; s.sh = 0; s.sdas = 1       # START
                else: s.mode = 'idle'; s.sdas = 1                                   # STOP
        if nscl != s.scl:
            s.scl = nscl
            if nscl: s.rising()
            else: s.falling()
    def rising(s):
        bit = s.line()
        if s.mode == 'idle': return
        if s.nb < 8:
            if s.mode in ('addr', 'wdata'): s.sh = ((s.sh << 1) | bit) & 0xFF
            s.nb += 1
        else:
            if s.mode == 'rdata': s.mack = (bit == 0)
            s.nb = 9
    def falling(s):
        m = s.mode
        if m == 'idle': return
        if s.nb == 8 and m in ('addr', 'wdata'):
            b = s.sh; s.sh = 0
            if m == 'addr':
                if (b >> 1) == 0x68: s.rw = b & 1; s.sdas = 0; s.after = 'rdata' if s.rw else 'wdata'; s.first = True
                else: s.mode = 'idle'
            else:
                if s.first: s.ptr = b; s.first = False
                else:
                    if s.ptr < 19: s.regs[s.ptr] = b
                    s.ptr += 1
                s.sdas = 0; s.after = 'wdata'
            return
        if s.nb == 9:
            s.sdas = 1; s.nb = 0
            if m == 'addr': s.mode = s.after; (s.load() if s.mode == 'rdata' else None)
            elif m == 'rdata':
                if s.mack: s.ptr += 1; s.load()
                else: s.mode = 'idle'
            return
        if m == 'rdata':
            s.sdas = (s.out >> (7 - s.nb)) & 1 if s.nb < 8 else 1


cpu = CPU(); fl = Flash([B0] + [bytes([255]) * 0x20000] * 7)
rtc = I2C() if RTC_PRESENT else None
orr = cpu.rd; owr = cpu.wr
log = {'dac': [], 'l20': [], 'pulses': 0, 'adc_reads': 0, 'chan': 0, 'val': 0, 'sopr': 0, 'l18': []}
state = {'io': 1}


def adcval(ch): return (0x123 + ch * 0x111) & 0xFFF


def rd(a, s):
    a &= 0xFFFFFF
    if 0xF80000 <= a < 0xFA0000: return fl.rd(a - 0xF80000, s)
    if a == 0x020000 and s == 2: log['adc_reads'] += 1; return 0xF000 | log['val']        # bits altos de lixo: o modulo mascara
    if a == 0xFA001B: return 0x10
    if a == 0x020028 and s == 2:
        if rtc is None: return 0
        return 0x40 if rtc.line() == 0 else 0       # 74LS240 inverte: linha baixa -> bit 1
    return orr(a, s)


def wr(a, s, v):
    a &= 0xFFFFFF
    if 0xF80000 <= a < 0xFA0000: return fl.wr(a - 0xF80000, s, v & (0xFFFF if s == 2 else 0xFF))
    if a == 0xFC0000: fl.bank = v & 7; return
    if a in (0x02000A, 0x02000C): log['dac'].append((a, v & 0xFFFF)); return
    if a == 0x020020:
        log['l20'].append(v & 0xFFFF); log['chan'] = (v >> 12) & 7
        if rtc: rtc.update(v & 0xFFFF)
        return
    if a == 0xFA001C and s == 2:
        if v & 8: log['sopr'] = 1
        return
    if a == 0xFA001E and s == 2:
        if v & 8 and log['sopr']:
            log['sopr'] = 0; log['pulses'] += 1; log['val'] = adcval(log['chan'])
        return
    if a == 0x020018 and s == 2:
        log['l18'].append(v & 0xFFFF)
        return
    return owr(a, s, v)


cpu.rd = rd; cpu.wr = wr
cpu.sr = 0x2700; cpu.a[7] = struct.unpack('>I', B0[0:4])[0]; cpu.pc = struct.unpack('>I', B0[4:8])[0]
out = bytearray(); cpu.on_tx = lambda b: out.append(b)
pos = [0]


def run(until, limit=4000):
    n = 0
    while n < limit:
        cpu.run(20000); n += 1
        if until in out.decode('latin-1')[pos[0]:]: break
    pos[0] = len(out)


def cmd(line, limit=4000):
    start = len(out)
    for ch in line + '\r': cpu.rx.append(ord(ch))
    run('> ', limit)
    t = out[start:].decode('latin-1').replace('\r', '')
    return t


run('Digite ?', 3000); run('> ')
res = {}
for c in sys.argv[3:] if len(sys.argv) > 3 else []:
    pass
tests = [
    'ADC 3', 'ADC', 'DAC', 'DAC A 800', 'DAC C M 62500', 'DAC', 'DAC A FFFF', 'DAC A 1000',
    '? ADC', '? RTC', 'RTC TESTE', 'RTC SET 26 11 15 12 30 45', 'RTC', 'RTC RAW',
    ]
if len(sys.argv) > 3: tests = sys.argv[3:]
for t in tests:
    print('>>>', t, flush=True)
    print(cmd(t, 20000 if t.startswith(('RTC', 'ADL')) else 6000).rstrip()[:2500], flush=True)
print('DAC writes:', [(hex(a), hex(v)) for a, v in log['dac']])
print('pulsos A/D:', log['pulses'], ' latch20 final:', hex(log['l20'][-1]) if log['l20'] else None)
ram2 = bytes(cpu.mem[0x40000:0x40100]).split(b'\x00')[0]
print('RAM2 inicio:', ram2[:200])
