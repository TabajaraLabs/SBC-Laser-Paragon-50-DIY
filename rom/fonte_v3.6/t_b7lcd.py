import sys, struct, json; sys.path.insert(0,'.')
src=open('/home/claude/sbc-laser-paragon-50-diy/ferramentas/t_lcd40_v1.py').read(); exec(src[:src.index('for addr7,label')])
import m68kasm_v3 as M
img=open('PARAGON50_F80000_apps_v36a.bin','rb').read()
def mk(addr7):
    c=Bus(addr7); c.mem[0xF80000:0xFA0000]=img; return c
def call(c,pc,max=40_000_000,regs=None):
    c.a[7]=0x7000; c.mem[0x7000:0x7004]=struct.pack('>I',0x1000); c.mem[0x1000:0x1002]=b'\x60\xFE'   # retorno -> laco
    c.sr=0x2700; c.pc=pc
    for k,v in (regs or {}).items(): c.d[k]=v
    n=0
    while c.pc!=0x1000 and n<max: c.step(); n+=1
    assert c.pc==0x1000, 'nao voltou %06X'%c.pc
    return n
def lines(c): return [c.ctrl[k].line(j).rstrip() for k in (0,1) for j in (0,1)]
# --- 1) caminho CP/M: entradas $F80614/18/1C + actv em $F80766 (endereco antigo)
c=mk(0x27)
call(c,0xF80614)
for ln,txt in ((0,b'CP/M-68K PARAGON 50 '),(1,b'A: 12345 KB livres'),(2,b'linha 3'),(3,b'linha 4')):
    c.mem[0x2000:0x2000+len(txt)+1]=txt+b'\0'
    c.a[7]=0x7000; sp=0x7000-12
    c.mem[sp:sp+12]=struct.pack('>III',ln,0,0x2000)
    c.a[7]=sp; c.mem[sp-4:sp]=struct.pack('>I',0x1000); c.a[7]=sp-4; c.sr=0x2700; c.pc=0xF80618
    n=0
    while c.pc!=0x1000 and n<40_000_000: c.step(); n+=1
print('CP/M lcd_at:',lines(c))
call(c,0xF80766); print('actv ($F80766):',repr(c.ctrl[0].line(1)[15:25]))
call(c,0xF8061C); print('hold apaga *:',repr(c.ctrl[0].line(1)[15:25]))
c2=mk(0x50); n=call(c2,0xF80614); print('sem LCD: passos',n,'bytes I2C',c2.nbytes)
# --- 2) driver SDFS v5 em RAM
m=M.Asm(); m.assemble(open('sdfs_v5.asm').read()); ad,im=m.segs[0]; sym=m.sym
for addr7 in (0x27,0x3F):
    c=mk(addr7); c.mem[ad:ad+len(im)]=bytes(im)
    call(c,sym['LCD_INIT'])
    call(c,sym['LCD_BANNER'])
    c.d[0]=0
    call(c,sym['LCD_GOTO'],regs={0:2,1:3}); c.a[0]=0
    s=b'terceira linha E2\0'; c.mem[0x2000:0x2000+len(s)]=s; c.a[1]=0x2000; call(c,sym['LCD_PUTS'])
    c.mem[sym['LCDOK']:sym['LCDOK']+2]=b'\x00\x01'; call(c,sym['ACTV'])
    print('SDFS v5 em $%02X:'%addr7,lines(c),'*' in c.ctrl[0].line(1))
