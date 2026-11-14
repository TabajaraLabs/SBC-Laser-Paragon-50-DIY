#!/usr/bin/env python3
"""bin2srec.py  arquivo.bin  endereco_hex  [entrada_hex]  -> arquivo.s19  (registros de 16 bytes)"""
import sys
def rec(t,addr,data,alen):
    body=bytes([len(data)+alen+1])+addr.to_bytes(alen,'big')+data
    ck=(~sum(body))&0xFF
    return "S%d%s%02X\r\n"%(t,(body).hex().upper(),ck)
def make(data,base,entry=None,name=b"PARAGON"):
    out=rec(0,0,name,2)
    alen,t,te=(2,1,9) if base+len(data)<=0x10000 else (3,2,8) if base+len(data)<=0x1000000 else (4,3,7)
    for i in range(0,len(data),16): out+=rec(t,base+i,data[i:i+16],alen)
    out+=rec(te,base if entry is None else entry,b"",alen)
    return out
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read(); base=int(sys.argv[2],16)
    ent=int(sys.argv[3],16) if len(sys.argv)>3 else None
    open(sys.argv[1].rsplit('.',1)[0]+'.s19','w',newline='').write(make(d,base,ent))
