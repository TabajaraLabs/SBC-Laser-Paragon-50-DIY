#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PONTE SERIAL - PARAGON 50
=========================
Roda no Windows. Faz tres coisas ao mesmo tempo:
  1. Mostra na tela tudo o que a placa envia (como um terminal) e tudo o que
     voce digitar vai para a placa.
  2. Grava tudo em  <pasta>\\serial.log  (com hora), para o Claude poder ler.
  3. Observa a pasta  <pasta>\\envio\\ :
        arquivo .s19 / .srec -> carrega na placa (comando L) e depois executa
                                se o nome terminar em _run  (ex.: teste_run.s19)
        arquivo .txt         -> cada linha e enviada como comando ao monitor;
                                a ponte espera o prompt "> " entre as linhas.
                                Diretivas:  #wait 60   (segundos de espera por
                                comando, valido para as linhas seguintes)
     Depois de processado, o arquivo vai para  envio\\enviados\\  com a hora.

Uso:   py -3 ferramentas\\paragon_bridge.py --port COM9
Requer:  pip install pyserial        (feche o RealTerm antes: a porta so abre uma vez)
Sair:  Ctrl+C
"""
import argparse, os, sys, time, threading, shutil, datetime, re

try:
    import serial
except ImportError:
    serial = None
try:
    import msvcrt
except ImportError:
    msvcrt = None

def ts():
    return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]

class Bridge:
    def __init__(self, ser, base, log_path):
        self.ser = ser; self.base = base
        self.envio = os.path.join(base, "envio"); self.done = os.path.join(self.envio, "enviados")
        os.makedirs(self.done, exist_ok=True)
        self.log = open(log_path, "a", encoding="utf-8", errors="replace", buffering=1)
        self.rxbuf = ""; self.lock = threading.Lock(); self.linebuf = ""; self.last_rx = time.time()
        self.busy = False; self.running = True
        self.event("ponte iniciada, porta %s" % getattr(ser, "port", "?"))

    # ---- log -----------------------------------------------------------
    def event(self, msg):
        line = "[%s] [ponte] %s" % (ts(), msg)
        self.log.write(line + "\n")
        sys.stdout.write("\n" + line + "\n"); sys.stdout.flush()

    def _log_rx(self, text):
        for ch in text:
            if ch == "\n":
                self.log.write("[%s] %s\n" % (ts(), self.linebuf.rstrip("\r"))); self.linebuf = ""
            else:
                self.linebuf += ch

    # ---- recepcao ------------------------------------------------------
    def rx_loop(self):
        while self.running:
            try:
                n = self.ser.in_waiting
                data = self.ser.read(n if n else 1)
            except Exception as e:
                self.event("erro de leitura: %s" % e); time.sleep(1); continue
            if data:
                text = data.decode("latin-1")
                sys.stdout.write(text.replace("\r\n", "\n").replace("\r", "\n") if False else text)
                sys.stdout.flush()
                with self.lock:
                    self.rxbuf += text; self.last_rx = time.time()
                    self._log_rx(text)
            else:
                if self.linebuf and time.time() - self.last_rx > 0.4:
                    with self.lock:
                        self.log.write("[%s] %s\n" % (ts(), self.linebuf)); self.linebuf = ""

    def send(self, text, delay=0.0):
        for ch in text:
            self.ser.write(ch.encode("latin-1")); self.ser.flush()
            if delay: time.sleep(delay)

    def clear_rx(self):
        with self.lock: self.rxbuf = ""

    def wait_for(self, patterns, timeout):
        """espera ate que rxbuf contenha algum dos padroes (regex); devolve o texto ou None"""
        t0 = time.time()
        while time.time() - t0 < timeout:
            with self.lock: buf = self.rxbuf
            for p in patterns:
                if re.search(p, buf): return buf
            time.sleep(0.05)
        return None

    def wait_prompt(self, timeout):
        return self.wait_for([r"> $"], timeout)

    def sync(self):
        """garante que o monitor esta no prompt"""
        for _ in range(3):
            self.clear_rx(); self.send("\r")
            if self.wait_prompt(1.5) is not None: return True
        return False

    # ---- processamento da pasta envio -----------------------------------
    def stable(self, path):
        try:
            s1 = os.path.getsize(path); time.sleep(0.5); return s1 == os.path.getsize(path) and s1 > 0
        except OSError:
            return False

    def archive(self, path):
        dest = os.path.join(self.done, datetime.datetime.now().strftime("%Y%m%d_%H%M%S_") + os.path.basename(path))
        shutil.move(path, dest)

    def do_srec(self, path):
        name = os.path.basename(path); run = os.path.splitext(name)[0].lower().endswith("_run")
        self.event("carregando %s%s" % (name, " (e executa)" if run else ""))
        if not self.sync(): self.event("monitor nao respondeu com prompt; abortado"); return
        self.clear_rx(); self.send("L\r")
        if self.wait_for([r"Envie"], 3) is None: self.event("sem resposta ao comando L"); return
        with open(path, "r", errors="replace") as f: lines = [l.strip() for l in f if l.strip()]
        self.clear_rx()
        for l in lines:
            self.send(l + "\r"); time.sleep(0.03)
        res = self.wait_for([r"OK registros=\w+ entrada=\w+", r"ERRO"], 15)
        if res is None: self.event("sem confirmacao do carregamento"); return
        m = re.search(r"OK registros=\w+ entrada=\w+", res)
        if not m: self.event("falha no carregamento (ver log)"); return
        self.event("carga concluida: " + m.group(0))
        self.wait_prompt(3)
        if run:
            self.clear_rx(); self.send("G\r"); self.wait_prompt(10)
            self.event("G executado")

    def do_txt(self, path):
        self.event("executando comandos de %s" % os.path.basename(path))
        if not self.sync(): self.event("monitor nao respondeu com prompt; abortado"); return
        wait = 10.0
        with open(path, "r", errors="replace") as f: lines = [l.rstrip("\r\n") for l in f]
        for l in lines:
            if not l.strip(): continue
            if l.startswith("#"):
                m = re.match(r"#wait\s+([\d.]+)", l)
                if m: wait = float(m.group(1))
                continue
            self.clear_rx(); self.event("envio: " + l); self.send(l + "\r")
            if self.wait_prompt(wait) is None: self.event("sem prompt apos '%s' em %.0f s" % (l, wait))
        self.event("fim de %s" % os.path.basename(path))

    def scan(self):
        for fn in sorted(os.listdir(self.envio)):
            p = os.path.join(self.envio, fn)
            if not os.path.isfile(p) or fn.startswith("_"): continue
            ext = os.path.splitext(fn)[1].lower()
            if ext not in (".s19", ".srec", ".s28", ".s37", ".txt"): continue
            if not self.stable(p): continue
            self.busy = True
            try:
                if ext == ".txt": self.do_txt(p)
                else: self.do_srec(p)
            except Exception as e:
                self.event("erro: %s" % e)
            finally:
                self.busy = False
            self.archive(p)

    # ---- teclado ---------------------------------------------------------
    def kbd_loop(self):
        if msvcrt is None: return
        while self.running:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ("\x00", "\xe0"): msvcrt.getwch(); continue
                if ch == "\r": out = "\r"
                elif ch == "\x08": out = "\x08"
                elif ch == "\x03": self.running = False; break
                else: out = ch
                if not self.busy:
                    try: self.ser.write(out.encode("latin-1", "replace"))
                    except Exception: pass
            else:
                time.sleep(0.02)

    def run(self):
        threading.Thread(target=self.rx_loop, daemon=True).start()
        threading.Thread(target=self.kbd_loop, daemon=True).start()
        print("Ponte ativa. Digite para falar com a placa; arquivos em %s sao enviados sozinhos. Ctrl+C sai." % self.envio)
        try:
            while self.running:
                self.scan(); time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        self.running = False; self.event("ponte encerrada"); self.log.close()

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="COM9"); ap.add_argument("--baud", type=int, default=9600)
    ap.add_argument("--dir", default=os.path.dirname(here))
    a = ap.parse_args()
    if serial is None:
        print("Falta o pyserial. Instale com:  py -3 -m pip install pyserial"); sys.exit(1)
    ser = serial.Serial(a.port, a.baud, bytesize=8, parity="N", stopbits=1, timeout=0.05, rtscts=False, xonxoff=False)
    Bridge(ser, a.dir, os.path.join(a.dir, "serial.log")).run()

if __name__ == "__main__":
    main()
