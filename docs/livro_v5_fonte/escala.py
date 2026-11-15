import sys, matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
import matplotlib.text as mt
F=float(sys.argv[1]); script=sys.argv[2]
orig=Figure.savefig
def sv(self,fn,*a,**k):
    for t in self.findobj(mt.Text):
        t.set_fontsize(t.get_fontsize()*F)
    return orig(self,fn.replace('img/','img5/'),*a,**k)
Figure.savefig=sv
exec(compile(open(script,encoding='utf-8').read(),script,'exec'))
