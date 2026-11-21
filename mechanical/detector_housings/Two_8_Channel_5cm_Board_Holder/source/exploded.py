"""CAD-derived open, exploded, board-hidden geometry; native OCP solids and curves."""
import json
from pathlib import Path
import math
import cadquery as cq
import holder as H
H.make()
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=Path('holder_build'))
OUT=parser.parse_args().output
OUT.mkdir(parents=True,exist_ok=True)
all=[]
assy=cq.Assembly(name="Exploded mechanics | PCB hidden")
def edge_points(e):
    n=2 if e.geomType()=='LINE' else max(7,min(280,math.ceil(e.Length()/.9)+1))
    return [v.toTuple() for v in e.positions([i/(n-1) for i in range(n)])]
for n,(s,m,g,_) in H.parts.items():
    if g in {'pcb','harness'}:continue
    dx,dy,dz=0.0,0.0,0.0
    if g=='shell':
        cut=H.b(H.P.tube_l+16,65,65,-8,-65,0)
        s=s.cut(cut)
        dz=-116
    if g in {'cap','gasket','coupler'}:
        if 'pull bridge' not in n and 'saddle' not in n:dx=-48
        if 'pull bridge' in n:dz=3
    if g=='rear':dx=38; dz=-8
    if 'longitudinal rail' in n:
        dy=-14 if '1' in n else 14
    if 'guide ring' in n:dx=-9 if 'Service' in n else 11
    if n.startswith('Upper') and g in ['carrier','hardware']:dz=23
    s=s.translate(H.V(dx,dy,dz))
    assy.add(s,name=n,color=cq.Color(*H.COLORS[m]))
    vv,ff=s.tessellate(.52,.2)
    edges=[]
    for e in s.Edges():
        if e.Length()>.5: edges.append(edge_points(e))
    all.append({'name':n,'vertices':[v.toTuple() for v in vv],'faces':ff,'edge_lines':edges,'mat':m,'group':g})
assy.save(str(OUT/'Mechanical_Exploded_View.step'))
(OUT/'cad_exploded_mesh.json').write_text(json.dumps({'mesh':all,'colors':H.COLORS},separators=(',',':')))
