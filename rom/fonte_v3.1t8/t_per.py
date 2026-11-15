"""t_per.py - testa os comandos ADC ADL DAC RTC (modulo PER1) e os textos de I/Q no emulador, com modelos do AD7875, dos DACs e do DS1302.
uso: python3 t_per.py imagem.bin [rtc_presente=1]"""
import sys, struct
sys.path.insert(0, '.')
from emu68k import CPU, Illegal, Halt
from t_fv4 import Flash

IMG = sys.argv[1]
RTC_PRESENT = (sys.argv[2] != '0') if len(sys.argv) > 2 else True
B0 = open(IMG, 'rb').read()


class DS1302:
    def __init__(s):
        s.regs = [0x80, 0, 0, 0, 0, 0, 0, 0]      # relogio parado, WP = 0
        s.ram = [0] * 31
        s.ce = 0; s.sck = 0; s.io = 0; s.reset(); s.out = 1; s.nwr = 0
    def reset(s):
        s.cnt = 0; s.cmd = None; s.shift = 0; s.ridx = 0; s.rbit = 0; s.wbits = 0; s.wval = 0; s.windex = 0
    def target(s):
        return ('ram' if s.cmd & 0x40 else 'ck'), (s.cmd >> 1) & 0x1F, s.cmd & 1
    def byte_at(s, k):                      # k-esimo byte da transferencia
        kind, a, rd = s.target()
        if a == 31:
            return (s.ram if kind == 'ram' else s.regs)[k] if k < (31 if kind == 'ram' else 8) else 0xFF
        arr = s.ram if kind == 'ram' else s.regs
        return arr[a] if (k == 0 and a < len(arr)) else 0xFF
    def write(s, v):
        ce = (v >> 10) & 1; sck = v & 1; io = (v >> 1) & 1
        if not ce:
            if s.ce: s.reset()
            s.ce = 0; s.sck = sck; s.out = 1; return
        s.ce = 1
        rising = (not s.sck) and sck; falling = s.sck and (not sck)
        s.sck = sck
        if rising:
            if s.cmd is None:
                s.shift |= io << s.cnt; s.cnt += 1
                if s.cnt == 8:
                    s.cmd = s.shift; assert s.cmd & 0x80, 'comando sem bit 7: %02X' % s.cmd
                    s.cnt = 0; s.shift = 0; s.ridx = 0; s.rbit = 0
            elif not (s.cmd & 1):           # escrita
                s.wval |= io << s.wbits; s.wbits += 1
                if s.wbits == 8:
                    kind, a, _ = s.target(); arr = s.ram if kind == 'ram' else s.regs
                    idx = s.windex if a == 31 else a
                    wp = s.regs[7] & 0x80
                    if kind == 'ck' and idx == 7 and a != 31: wp = 0 if True else wp
                    if (not wp) or (kind == 'ck' and idx == 7):
                        if idx < len(arr): arr[idx] = s.wval
                    s.nwr += 1
                    s.windex += 1; s.wbits = 0; s.wval = 0
        if falling and s.cmd is not None and (s.cmd & 1):
            b = s.byte_at(s.ridx)
            s.out = (b >> s.rbit) & 1
            s.rbit += 1
            if s.rbit == 8: s.rbit = 0; s.ridx += 1
    def pin(s):                              # nivel do pino I/O visto pelo MISO
        if not s.ce: return 1
        if s.cmd is not None and (s.cmd & 1): return s.out
        return s.io_drv if hasattr(s, 'io_drv') else 1


cpu = CPU(); fl = Flash([B0] + [bytes([255]) * 0x20000] * 7)
rtc = DS1302() if RTC_PRESENT else None
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
        if rtc is None: return 0                  # pino em nivel alto (pull-up) -> 74LS240 inverte -> bit 0 = 0
        lv = rtc.pin() if rtc.ce else 1
        # se o programa dirige MOSI alto e o chip nao dirige, o nivel e o de MOSI
        return 0 if lv else 1                     # 74LS240: nivel alto no pino -> 0 lido
    return orr(a, s)


def wr(a, s, v):
    a &= 0xFFFFFF
    if 0xF80000 <= a < 0xFA0000: return fl.wr(a - 0xF80000, s, v & (0xFFFF if s == 2 else 0xFF))
    if a == 0xFC0000: fl.bank = v & 7; return
    if a in (0x02000A, 0x02000C): log['dac'].append((a, v & 0xFFFF)); return
    if a == 0x020020: log['l20'].append(v & 0xFFFF); log['chan'] = (v >> 12) & 7; return
    if a == 0xFA001C and s == 2:
        if v & 8: log['sopr'] = 1
        return
    if a == 0xFA001E and s == 2:
        if v & 8 and log['sopr']:
            log['sopr'] = 0; log['pulses'] += 1; log['val'] = adcval(log['chan'])
        return
    if a == 0x020018 and s == 2:
        log['l18'].append(v & 0xFFFF)
        if rtc: rtc.write(v & 0xFFFF)
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
    '? ADC', '? RTC', 'RTC', 'RTC TESTE', 'RTC SET 26 11 14 12 30 00', 'RTC', 'RTC RAW', 'ADL 2 5 1',
    'Q', 'I',
]
if len(sys.argv) > 3: tests = sys.argv[3:]
for t in tests:
    print('>>>', t, flush=True)
    print(cmd(t, 20000 if t.startswith(('RTC', 'ADL')) else 6000).rstrip()[:2500], flush=True)
print('DAC writes:', [(hex(a), hex(v)) for a, v in log['dac']])
print('pulsos A/D:', log['pulses'], ' latch20 final:', hex(log['l20'][-1]) if log['l20'] else None)
ram2 = bytes(cpu.mem[0x40000:0x40100]).split(b'\x00')[0]
print('RAM2 inicio:', ram2[:200])
