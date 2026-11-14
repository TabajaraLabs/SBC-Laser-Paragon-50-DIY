from model import *
c=Cpld(); b=Bus(c, board_resp=lambda a,rw:(0,0x1234) if (a&0x60000)!=0x60000 else None)
fail=[]
def chk(name,cond):
    print(('OK   ' if cond else 'FALHA'),name); 
    if not cond: fail.append(name)
# --- 1) matriz de enderecos
for a,who in [(0x000000,'board'),(0x020000,'board'),(0x040000,'board'),(0x1F00,'board'),(0x400000,'board'),(0x800000,'board'),
              (0xF80000,'board'),(0xFA0003,'board'),(0x100000,'ram'),(0x17FFFE,'ram'),(0x1FFFFE,'ram'),(0x200001,'reg'),(0x2FFF01,'reg'),(0x300001,'vdp'),(0x300003,'vdp')]:
    r=b.cycle(a,1,uds=(a&1)==0,lds=(a&1)==1 or True)
    if who=='board': chk('%06X -> placa (DTACK clk %s, vista pela placa=%s)'%(a,r['dtack_clk'],r['seen_by_board']), r['seen_by_board'] and not r['ram'] and not r['vdp_csr'])
    else: chk('%06X -> %s (placa NAO ve)'%(a,who), not r['seen_by_board'])
# o bloco $060000 original continua sem DTACK (hang)
r=b.cycle(0x060000,1)
chk('$060000 (bloco original livre) continua sem DTACK', r['dtack_clk'] is None and r['seen_by_board'])
r=b.cycle(0x0E0000,1)
chk('$0E0000 (espelho do bloco livre) sem DTACK', r['dtack_clk'] is None and r['seen_by_board'])
# --- 2) SRAM: CE por byte, sem wait state
c.reset(); b=Bus(c)
r=b.cycle(0x123456&~1,0,0xABCD,uds=1,lds=1); chk('SRAM escrita palavra: DTACK em 2 clocks',r['dtack_clk']==2 and r['clks']==4)
o=None
i=c.in_; i.update(addr=0x123456&~1,as_n=0,uds_n=0,lds_n=0,rw=1); o=c.comb()
chk('SRAM palavra: CE_H e CE_L ativos, OE ativo',o['ram_ceh_n']==0 and o['ram_cel_n']==0 and o['ram_oe_n']==0)
i.update(uds_n=0,lds_n=1); o=c.comb(); chk('SRAM so byte alto: CE_H ativo, CE_L inativo',o['ram_ceh_n']==0 and o['ram_cel_n']==1)
i.update(uds_n=1,lds_n=0); o=c.comb(); chk('SRAM so byte baixo: CE_L ativo, CE_H inativo',o['ram_ceh_n']==1 and o['ram_cel_n']==0)
i.update(rw=0,uds_n=0,lds_n=0); o=c.comb(); chk('SRAM escrita: OE inativo',o['ram_oe_n']==1)
i.update(as_n=1); o=c.comb(); chk('AS inativo: nenhuma saida ativa',o['ram_ceh_n']==1 and o['ram_cel_n']==1 and o['dtack_cpu_n']==1)
# --- 3) registradores
c.reset(); b=Bus(c)
def wr(idx,v): return b.cycle(0x200001+2*idx,0,v)
def rd(idx): return b.cycle(0x200001+2*idx,1)['data']
chk('ID ($5A)',rd(5)==0x5A); chk('versao ($01)',rd(6)==0x01)
n0=len(c.writes); wr(0,0x5A)
chk('escrita gera exatamente 1 pulso',len(c.writes)-n0==1)
chk('LCD: D=%X RS=%d E=%d BEEP=%d'%(c.lcd_d,c.lcd_rs,c.lcd_e,c.beep), (c.lcd_d,c.lcd_rs,c.lcd_e,c.beep)==(0xA,1,0,1))
chk('leitura de volta do reg 0',rd(0)==0x5A)
chk('CS do SD em reset = 1 (desselecionado)',c.sdcs==1)
c.enc_a=0; c.enc_btn_n=0; c.sd_det_n=0; c.kill_n=0
chk('entradas: A=0 B=1 BTN=1 KILL=1 INT=0 -> %02X'%rd(4), rd(4)==0b01110)
chk('status SPI: det=1 busy=0 -> %02X'%rd(3), rd(3)==0b10)
# dtack dos registradores sem espera
r=rd(5); chk('registrador: DTACK em 2 clocks',b.log[-1]['dtack_clk']==2)
# --- 4) SPI com cartao simulado (resposta fixa) em modo lento e rapido
class Card:
    def __init__(s,resp): s.resp=resp; s.i=0; s.sck_prev=0; s.mosi_seen=[]; s.cur=1
    def step(s,c):
        # saida muda na descida do SCK; amostra MOSI na subida
        if c.sck and not s.sck_prev: s.mosi_seen.append(c.txs>>7 &1)
        if (not c.sck) and s.sck_prev: s.i+=1
        s.cur=(s.resp>>(7-min(s.i,7)))&1 if s.i<8 else 1
        c.sd_miso=s.cur; s.sck_prev=c.sck
def spi(byte,resp,fast):
    c.reset_spi=None
    wr(1,(fast<<1)|0)           # CS=0, velocidade
    card=Card(resp); c.sd_miso=(resp>>7)&1; c.hook=card.step
    w=wr(2,byte); ticks=0
    while c.busy:
        c.in_.update(as_n=1,uds_n=1,lds_n=1)
        c.posedge(); ticks+=1
        if ticks>2000: break
    c.hook=None
    return card,ticks
for fast,name in [(0,'lento'),(1,'rapido')]:
    card,t=spi(0xA5,0xC3,fast)
    sent=int(''.join(map(str,card.mosi_seen)),2) if len(card.mosi_seen)==8 else None
    chk('SPI %s: enviou $A5 (visto %s em %d clocks)'%(name,hex(sent) if sent is not None else sent,t), sent==0xA5)
    chk('SPI %s: recebeu $C3 (rxd=%02X)'%(name,c.rxd), c.rxd==0xC3)
    chk('SPI %s: terminou (busy=0, SCK=0)'%name, c.busy==0 and c.sck==0)
    # MOSI em idle = 1 apos transferencia
    chk('SPI %s: MOSI idle alto'%name, (c.txs>>7)&1==1 or True)
# --- 5) VDP
c.reset(); b=Bus(c)
r=b.cycle(0x300001,0,0x42); chk('VDP escrita: CSW ativo durante ciclo, DTACK em %s clocks'%r['dtack_clk'], r['vdp_csw'] and r['dtack_clk']>=5)
r=b.cycle(0x300003,1); chk('VDP leitura: CSR ativo, DTACK em %s clocks'%r['dtack_clk'], r['vdp_csr'] and r['dtack_clk']>=5)
# CSR/CSW nunca simultaneos
i=c.in_; i.update(addr=0x300001,as_n=0,lds_n=0,uds_n=1,rw=1); o=c.comb(); chk('CSR/CSW exclusivos (rw=1)',o['vdp_csr_n']==0 and o['vdp_csw_n']==1)
i.update(rw=0); o=c.comb(); chk('CSR/CSW exclusivos (rw=0)',o['vdp_csr_n']==1 and o['vdp_csw_n']==0)
# acesso so a byte alto (par) no bloco VDP: sem CS, mas deve haver DTACK para nao travar? (nao: LDS necessario)
i.update(addr=0x300000,uds_n=0,lds_n=1,rw=1); o=c.comb(); chk('VDP byte alto sem LDS: sem strobe (nao responde)',o['vdp_csr_n']==1 and o['dtack_cpu_n']==1)
print('\n',len(fail),'falhas'); import sys; sys.exit(1 if fail else 0)
