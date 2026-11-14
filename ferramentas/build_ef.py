import sys
sys.path.insert(0,'.')
from m68kasm_v3 import Asm
a=Asm()
try:
    a.assemble(open(sys.argv[1] if len(sys.argv)>1 else 'ef_paragon.asm').read())
except Exception as e:
    print('ERRO',e); sys.exit(1)
for o,b in a.segs: print(hex(o),len(b),'ate',hex(o+len(b)))
