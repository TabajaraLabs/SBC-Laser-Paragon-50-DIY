# Modelo em Python do paragon_x.v (mesmas equacoes) + testes de ciclo de barramento do 68000
class Cpld:
    VDP_WAIT=4
    def __init__(s):
        s.reset()
    def reset(s):
        s.vcnt=0; s.wr_d=0
        s.lcd_d=0; s.lcd_rs=0; s.lcd_e=0; s.beep=0; s.sdcs=1; s.fast=0
        s.busy=0; s.sck=0; s.cnt=0; s.bits=0; s.txs=0xFF; s.rxs=0; s.rxd=0
        # entradas externas
        s.sd_miso=1; s.sd_det_n=1; s.enc_a=1; s.enc_b=1; s.enc_btn_n=1; s.kill_n=1; s.vdp_int_n=1
        s.in_=dict(as_n=1,uds_n=1,lds_n=1,rw=1,addr=0,dtack_brd_n=1,d=0)
        s.writes=[]  # log de escritas em regs
    # ---- combinacional
    def comb(s):
        i=s.in_; a=i['addr']
        a1=(a>>1)&1; a2=(a>>2)&1; a3=(a>>3)&1
        a20=(a>>20)&1; a21=(a>>21)&1; a22=(a>>22)&1; a23=(a>>23)&1
        o={}
        blk_ram=(not a23) and (not a22) and (not a21) and a20
        blk_reg=(not a23) and (not a22) and a21 and (not a20)
        blk_vdp=(not a23) and (not a22) and a21 and a20
        blk_new=blk_ram or blk_reg or blk_vdp
        o['as_brd_n']=int(i['as_n'] or blk_new); o['uds_brd_n']=int(i['uds_n'] or blk_new); o['lds_brd_n']=int(i['lds_n'] or blk_new)
        ds=(not i['uds_n']) or (not i['lds_n']); cyc=(not i['as_n']) and ds
        ram_cyc=blk_ram and not i['as_n']
        o['ram_ceh_n']=int(not (ram_cyc and not i['uds_n'])); o['ram_cel_n']=int(not (ram_cyc and not i['lds_n']))
        o['ram_oe_n']=int(not (ram_cyc and i['rw']))
        reg_cyc=blk_reg and (not i['as_n']) and (not i['lds_n'])
        vdp_cyc=blk_vdp and (not i['as_n']) and (not i['lds_n'])
        o['vdp_csr_n']=int(not (vdp_cyc and i['rw'])); o['vdp_csw_n']=int(not (vdp_cyc and not i['rw']))
        vdp_ack=vdp_cyc and s.vcnt>=s.VDP_WAIT
        our_ack=(((blk_ram or blk_reg) and cyc) or vdp_ack)
        o['dtack_cpu_n']=int(i['dtack_brd_n'] and not our_ack)
        idx=(a3<<2)|(a2<<1)|a1
        wr_act=reg_cyc and not i['rw']; wr_pulse=wr_act and not s.wr_d
        rdata={0:(s.beep<<6)|(s.lcd_e<<5)|(s.lcd_rs<<4)|s.lcd_d,1:(s.fast<<1)|s.sdcs,2:s.rxd,
               3:((1-s.sd_det_n)<<1)|s.busy,
               4:((1-s.vdp_int_n)<<4)|((1-s.kill_n)<<3)|((1-s.enc_btn_n)<<2)|(s.enc_b<<1)|s.enc_a,5:0x5A,6:0x01}.get(idx,0)
        o['d_drive']=rdata if (reg_cyc and i['rw']) else None
        o.update(vdp_cyc=vdp_cyc,reg_cyc=reg_cyc,idx=idx,wr_act=wr_act,wr_pulse=wr_pulse,blk_ram=blk_ram,blk_reg=blk_reg,blk_vdp=blk_vdp,vdp_ack=vdp_ack)
        o['sd_cs_n']=s.sdcs; o['sd_sck']=s.sck; o['sd_mosi']=(s.txs>>7)&1
        return o
    # ---- posedge clk (usa os valores pre-borda)
    def posedge(s):
        o=s.comb(); i=s.in_
        vcnt=(min(7,s.vcnt+1) if o['vdp_cyc'] else 0)
        wr_pulse=o['wr_pulse']; idx=o['idx']; d=i['d']
        if wr_pulse:
            s.writes.append((idx,d))
            if idx==0: s.lcd_d=d&15; s.lcd_rs=(d>>4)&1; s.lcd_e=(d>>5)&1; s.beep=(d>>6)&1
            elif idx==1: s.sdcs=d&1; s.fast=(d>>1)&1
        half=1 if s.fast else 15
        if wr_pulse and idx==2 and not s.busy:
            s.txs=d; s.bits=0; s.cnt=0; s.sck=0; s.busy=1
        elif s.busy:
            if s.cnt==half:
                s.cnt=0
                if not s.sck:
                    s.sck=1; s.rxs=((s.rxs<<1)&0xFF)|s.sd_miso; s.bits+=1
                else:
                    s.sck=0
                    if s.bits==8: s.busy=0; s.rxd=s.rxs
                    else: s.txs=((s.txs<<1)&0xFF)|1
            else: s.cnt+=1
        s.wr_d=int(o['wr_act']); s.vcnt=vcnt
        if getattr(s,'hook',None): s.hook(s)

class Bus:
    """68000 @ 8 MHz: ciclo minimo de 4 clocks; DTACK amostrado no clock 2; mantem DS ate o fim."""
    def __init__(s,cpld,board_resp=None):
        s.c=cpld; s.board_resp=board_resp or (lambda addr,rw: None)  # None = nao responde; (dtack_delay, data)
        s.log=[]
    def cycle(s,addr,rw,wdata=0,uds=0,lds=1):
        c=s.c; i=c.in_
        i.update(addr=addr,rw=rw,d=wdata if not rw else 0)
        i['as_n']=0; i['uds_n']=0 if uds else 1; i['lds_n']=0 if lds else 1
        # a placa so responde se enxerga o ciclo
        o=c.comb(); brd_seen=(o['as_brd_n']==0)
        resp=s.board_resp(addr,rw) if brd_seen else None
        clk=0; data=None; dtack_clk=None
        while True:
            clk+=1
            i['dtack_brd_n']=1
            if resp is not None and clk>resp[0]: i['dtack_brd_n']=0
            # escrita: dado so valido apos clock 1 (DS na escrita ocorre depois); simplificacao: valido
            o=c.comb()
            if o['dtack_cpu_n']==0 and clk>=2:
                dtack_clk=clk
                if rw: data = o['d_drive'] if o['d_drive'] is not None else (resp[1] if resp else None)
                break
            c.posedge()
            if clk>64: dtack_clk=None; break  # travou: watchdog
        # termina o ciclo: mais clocks ate completar 4
        while clk<4: c.posedge(); clk+=1
        c.posedge()
        i['as_n']=1; i['uds_n']=1; i['lds_n']=1; i['dtack_brd_n']=1
        c.posedge(); c.posedge()
        r=dict(addr=addr,rw=rw,seen_by_board=brd_seen,dtack_clk=dtack_clk,data=data,clks=clk, ram=(o['ram_ceh_n']==0 or o['ram_cel_n']==0),vdp_csr=o['vdp_csr_n']==0,vdp_csw=o['vdp_csw_n']==0)
        s.log.append(r); return r
