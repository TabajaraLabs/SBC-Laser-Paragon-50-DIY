# mkrom2.py - gera as ROMs finais v2.0
import os
os.makedirs('rom21/27C256_unused',exist_ok=True); os.makedirs('rom21/27C512',exist_ok=True)
mon=bytearray(open('mon21/MONITOR_F80000.bin','rb').read())
tet=open('cpm/dt/tetris_rom.bin','rb').read(); basic=open('eh/eh_rom21.bin','rb').read(); cpm=open('cpm/build/cpm_rom.bin','rb').read()
ext=open('v21/ext/out/ext.bin','rb').read()
assert set(mon[0x1C00:])=={0xFF}, 'monitor invadiu a area do Tetris'
assert 0x1C00+len(tet)<=0x4000 and len(basic)<=0x4000 and 0x8000+len(cpm)<=0x10000 and len(ext)<=0x10000
rom=bytearray(mon); rom[0x1C00:0x1C00+len(tet)]=tet
rom[0x4000:0x4000+len(basic)]=basic; rom[0x8000:0x8000+len(cpm)]=cpm
per=open('prog/perif_rom.bin','rb').read(); assert 0x8000+len(cpm)<=0xF000 and 0xF000+len(per)<=0x10000; rom[0xF000:0xF000+len(per)]=per
assert len(rom)==65536
def split256(l):
    qs=[l[i*0x4000:(i+1)*0x4000] for i in range(4)]
    il=b''.join(qs[i] for i in (3,2,1,0)); return il[0::2],il[1::2]
h,l=split256(bytes(rom))
open('rom21/27C256_unused/PARAGON_F80000.bin','wb').write(rom); open('rom21/27C256_unused/PARAGON_HI.bin','wb').write(h); open('rom21/27C256_unused/PARAGON_LO.bin','wb').write(l)
L=bytearray(b'\xff'*131072); L[:65536]=rom; L[65536:65536+len(ext)]=ext
def ca(x):
    b=(x>>1)&0x1FFF; b|=(((x>>14)&1)^1)<<13; b|=(((x>>15)&1)^1)<<14; b|=(((x>>16)&1)^1)<<15; return b
hi=bytearray(65536); lo=bytearray(65536)
for x in range(131072):
    c=ca(x); (hi if x%2==0 else lo)[c]=L[x]
open('rom21/27C512/PARAGON512_F80000.bin','wb').write(L); open('rom21/27C512/PARAGON512_HI.bin','wb').write(hi); open('rom21/27C512/PARAGON512_LO.bin','wb').write(lo)
# confere: remontar a imagem logica a partir de HI/LO
R=bytearray(131072)
for x in range(131072):
    c=ca(x); R[x]=(hi if x%2==0 else lo)[c]
assert bytes(R)==bytes(L)
import zlib
for f in ['rom21/27C256_unused/PARAGON_HI.bin','rom21/27C256_unused/PARAGON_LO.bin','rom21/27C512/PARAGON512_HI.bin','rom21/27C512/PARAGON512_LO.bin']:
    d=open(f,'rb').read(); print(f,len(d),'CRC32 %08X'%zlib.crc32(d))
print('monitor ate',hex(0xF80000+max(i for i,b in enumerate(mon) if b!=0xFF)),'tetris',hex(0xF81C00),'-',hex(0xF81C00+len(tet)-1),'basic',len(basic),'cpm',len(cpm),'ext',len(ext),hex(0xF90000+len(ext)-1))
