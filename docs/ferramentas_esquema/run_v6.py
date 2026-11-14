import sys
import modelo_v6; sys.modules['modelo']=modelo_v6
import render_sch, export_kicad
import os; os.makedirs('out6',exist_ok=True)
render_sch.main('out6','v6')
