import os, zlib
img=open('PARAGON50_F80000_v2.6.bin','rb').read(); assert len(img)==131072
old=open('rom231.bin','rb').read()
def ca(x):
    b=(x>>1)&0x1FFF; b|=(((x>>14)&1)^1)<<13; b|=(((x>>15)&1)^1)<<14; b|=(((x>>16)&1)^1)<<15; return b
hi=bytearray(65536); lo=bytearray(65536)
for x in range(131072):
    c=ca(x); (hi if x%2==0 else lo)[c]=img[x]
D='out/ROM_V2.6.1_AM29F040B'; os.makedirs(D,exist_ok=True)
open(D+'/PARAGON_V2.6.1_F80000_128K.bin','wb').write(img)
open(D+'/PARAGON_V2.6.1_HI_AM29F040B_512K_x8copias.bin','wb').write(bytes(hi)*8)
open(D+'/PARAGON_V2.6.1_LO_AM29F040B_512K_x8copias.bin','wb').write(bytes(lo)*8)
for n,d in (('HI',hi),('LO',lo),('TOTAL',img)): print(n,'CRC32 %08X'%(zlib.crc32(bytes(d))&0xFFFFFFFF))
