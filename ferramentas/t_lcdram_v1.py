import sys; sys.path.insert(0,'.')
import m68kasm_v3 as M
src=open('t_lcd40_v1.py').read(); exec(src[:src.index('for addr7,label')])
img=open('../fontes/lcd_i2c/lcd_i2c_ram_v1_img.bin','rb').read()
c=Bus(0x27)
a=M.Asm(); a.assemble(open('../programas/lcd40_stubs_v1.asm').read())
for st,b in a.segs: c.mem[st:st+len(b)]=b
c.mem[0x2000:0x2000+len(img)]=img
c.pc=0x2000; c.a[7]=0x7000; c.sr=0x2700; c.rx=[]; steps=0
while steps<30_000_000 and c.a[7]!=0x7004:
    c.step(); steps+=1
    if steps==2_000_000: print('antes da tecla:',[c.ctrl[k].line(j) for k in (0,1) for j in (0,1)]); c.rx=[ord('x')]
print(bytes(c.tx).decode('latin1')); print('passos',steps,'apos tecla (apagado?)',repr(c.ctrl[0].line(0)))
