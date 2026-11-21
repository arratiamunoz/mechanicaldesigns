#!/usr/bin/env python3
"""NeoLattice detector holder. All dimensions mm; executable parametric CadQuery 2.7 source."""
import cadquery as cq
from pathlib import Path
import argparse, json, math
from dataclasses import dataclass, asdict
O=Path(__file__).resolve().parent
@dataclass(frozen=True)
class Spec:
    tube_od: float=101.60
    tube_wall: float=3.175
    tube_l: float=609.60
    tube_accept_min_id: float=93.50
    board_l: float=443.0
    board_w: float=49.10
    board_t: float=1.60
    board_front: float=122.60
    front_shift: float=54.60
    cap_t: float=3.175
    upper_board_top: float=10.00
    lower_board_top: float=-27.00
    tile_mech_w: float=48.80
    tile_mech_l: float=48.80
    tile_h_allowance: float=7.00
    guide_od: float=91.00
    guide_id: float=82.00
    collar_od: float=92.50
    collar_id: float=81.00
    jacket_max_d: float=6.0
    plug_height_from_pcb: float=28.0
    # conservative hard keep-out, centered on the actual vertical mating locations
    plug_keepout_half_y: float=7.0
P=Spec()
V=cq.Vector
X=V(1,0,0); Z=V(0,0,1)
MOUNT=((36.2,-18.65),(438.0,-0.15))
TILES=tuple((67.0+48.8*i,-(0.20 if i==0 else 0.15)) for i in range(8))
JACK_Y=(14.969201,-3.530799)
JACK_X=11.006101
COLORS={'shell':(0.59,0.70,0.79),'metal':(0.62,0.72,0.79),'rail':(0.29,0.45,0.56),'poly':(0.22,0.27,0.30),'pcb':(0.10,0.40,0.30),'tile':(0.65,0.47,0.26),'jack':(0.65,0.69,0.73),'boot':(0.26,0.33,0.37),'orange':(0.90,0.35,0.13),'bronze':(0.80,0.62,0.28),'dark':(0.10,0.16,0.19)}
def b(dx,dy,dz,x,y,z):return cq.Solid.makeBox(dx,dy,dz,V(x,y,z))
def c(r,l,x,y,z,axis=X):return cq.Solid.makeCylinder(r,l,V(x,y,z),axis)
def ann(ro,ri,length,x):return c(ro,length,x,0,0).cut(c(ri,length+2,x-1,0,0))
def comp(seq):return cq.Compound.makeCompound(list(seq))
def sphere(r,x,y,z):return cq.Solid.makeSphere(r,V(x,y,z),angleDegrees1=-90,angleDegrees2=90)
parts={}
ROUTES=[]
def item(name,shape,mat,group,*,render=True):
    if not shape.isValid():raise ValueError(name+" failed OCCT shape check")
    parts[name]=(shape,mat,group,render)
    return shape
def mk_shell():
    ro,ri=P.tube_od/2,P.tube_od/2-P.tube_wall
    sh=ann(ro,ri,P.tube_l,0)
    for x in [7,P.tube_l-7]:
        for i in range(4):
            t=i*math.pi/2; d=V(0,math.cos(t),math.sin(t))
            sh=sh.cut(c(2.25,13,x,(ri-4)*math.cos(t),(ri-4)*math.sin(t),d))
    return sh
def collar(x,t=12):
    u=ann(P.collar_od/2,P.collar_id/2,t,x)
    for y,z in CAPFAST:
        u=u.cut(c(1.25,t+2,x-1,y,z))
    if x==0:
        # Keep vendor fastener tip access when outer diagonal screws intersect collar.
        for y,z in PORT_JACKS:
            for yy,zz in port_screws(y,z):
                if math.hypot(yy,zz)+2.75>P.collar_id/2:
                    u=u.cut(c(2.75,6,-.1,yy,zz))
    for i in range(4):
        a=i*math.pi/2; u=u.cut(c(1.65,10,x+(7 if x==0 else 5),44*math.cos(a),44*math.sin(a),V(0,math.cos(a),math.sin(a))))
    return u
# NE8FDP-B-TOP front-mounted review envelopes based on Neutrik 20004014.
# Rotate the bottom row 180° so sealing covers open away from one another.
ROW_Z=(-18.0,18.0)
PORT_Y=(16.0,-16.0)
PORT_JACKS=[(y,z) for z in ROW_Z for y in PORT_Y]
CAPFAST=((10,42.2),(-10,42.2),(42.63,8),(-42.63,8),(19,-39.02),(-19,-39.02))
PORT_FRONT_X=-P.cap_t
CAP_BORE_R=12.10
GEOM_COLORS={}
def port_screws(y,z):
    return ((y+9.5,z+12.0),(y-9.5,z-12.0))
def end_caps():
    x0=PORT_FRONT_X
    blank=c(P.tube_od/2,P.cap_t,x0,0,0)
    for y,z in CAPFAST:blank=blank.cut(c(1.70,8,x0-1,y,z))
    for i,(y,z) in enumerate(PORT_JACKS):
        blank=blank.cut(c(CAP_BORE_R,8,x0-1,y,z))
        for yy,zz in port_screws(y,z):
            blank=blank.cut(c(1.65,8,x0-1,yy,zz))
        # Closed flange/gasket footprint; height asymmetric about socket center.
        lo=z-(15.45 if z>0 else 17.55)
        front=b(5.05,25.9,33.00,x0-5.05,y-12.95,lo)
        front=front.cut(b(6,12.2,9.1,x0-5.5,y-6.1,z-4.55))
        for yy,zz in port_screws(y,z):
            front=front.cut(c(1.58,8,x0-6,yy,zz))
        item(f'Panel port {i+1} TOP flange and closed-cover envelope',front,'jack','coupler')
        body=c(11.75,P.cap_t+2,x0,y,z).fuse(b(28,15.9,25.9,0,y-7.95,z-12.95))
        body=body.cut(b(34,12.2,9.1,-4,y-6.1,z-4.55))
        item(f'Panel port {i+1} rear receptacle envelope',body,'boot','coupler')
        mate=b(25,13.8,13,28,y-6.9,z-6.5)
        item(f'Panel port {i+1} internal mated boot envelope',mate,'dark','coupler')
    item('Four-port aluminum patch endcap, 3.175 mm',blank,'metal','cap')
    # Thin nominal face seal, inside its uncompressed height budget. Rim gasket only.
    item('Endcap rim gasket envelope',ann(P.tube_od/2-0.10,P.tube_od/2-1.8,.2,-.15),'poly','gasket')
    rear=c(P.tube_od/2,6,P.tube_l,0,0)
    for y,z in CAPFAST:rear=rear.cut(c(1.70,8,P.tube_l-1,y,z))
    item('Blind end cap',rear,'metal','rear')
def s_route(x0,x1,y0,z0,y1,z1,rad=3.0):
    # Symmetric planar biarc gives axially tangent entry/exit and an actual BREP sweep.
    L=x1-x0;d=math.hypot(y1-y0,z1-z0)
    R=(L*L+d*d)/(4*d); angle=2*math.atan2(d,L)
    ew=V(0,(y1-y0)/d,(z1-z0)/d)
    q=V(x0,y0,z0)
    end=V(x1,y1,z1)
    en=lambda dv:ew.multiply(dv)
    arc0=lambda a:q+V(R*math.sin(a),0,0)+en(R*(1-math.cos(a)))
    arc1=lambda a:end-V(R*math.sin(a),0,0)-en(R*(1-math.cos(a)))
    m=arc0(angle)
    w=cq.Wire.assembleEdges([cq.Edge.makeThreePointArc(q,arc0(angle/2),m),
          cq.Edge.makeThreePointArc(m,arc1(angle/2),end)])
    sec=cq.Wire.makeCircle(rad,q,X)
    return cq.Solid.sweep(sec,[],w,makeSolid=True,isFrenet=False),R,2*R*angle
def end_spider(x):
    # Replaceable synthetic guide: opening and rail shoe relief; cable paths clear Ø82 aperture.
    q=ann(P.guide_od/2,P.guide_id/2,7,x)
    for side in [-1,1]:
        yc=side*26.6
        q=q.cut(b(9,3.0,46,x-1,yc-1.5,-35))
    return q
def tray(z,lab):
    # Simplified engineering envelopes for fit checks. Excluded from CAD exports.
    x0=P.board_front
    s=b(P.board_l,P.board_w,P.board_t,x0,-P.board_w/2,z-P.board_t)
    for x,y in MOUNT:s=s.cut(c(1.6,P.board_t+2,x0+x,y,z-P.board_t-1,Z))
    item(lab+' board envelope',s,'pcb','pcb')
    for i,y in enumerate(JACK_Y):
        s=b(15.8,16.2,13.1,x0+JACK_X-7.9,y-8.1,z).cut(b(11.8,12.2,7,x0+JACK_X-5.9,y-6.1,z+7))
        item(f'{lab} connector {i+1} envelope',s,'jack','pcb')
    for i,(x,y) in enumerate(TILES):
        tx=P.tile_mech_l
        s=cq.Workplane("XY").box(tx,P.tile_mech_w,5).edges("|Z").fillet(1.4).val().translate(V(x0+x,y,z+4.5))
        item(f'{lab} scintillator {i+1} worst-case stack',s,'tile','pcb')
    support_z=z-P.board_t-7
    for mi,(xp,yp) in enumerate(MOUNT):
        xx=x0+xp
        cross=b(12,55.7,3,xx-6,-27.85,support_z)
        if mi==0:
            cut=c(1.8,5,xx,yp,support_z-1,Z)
        else:
            # One round datum + one floating slot accommodate cumulative pitch tolerance or expansion.
            cut=b(5,3.6,5,xx-2.5,yp-1.8,support_z-1)
            for dx in [-2.5,2.5]:cut=cut.fuse(c(1.8,5,xx+dx,yp,support_z-1,Z))
        cross=cross.cut(cut)
        item(f'{lab} slotted crossmember {mi+1}',cross,'rail','carrier')
        s=c(3.5,4,xx,yp,z-P.board_t-4,Z).cut(c(1.6,6,xx,yp,z-P.board_t-5,Z))
        item(f'{lab} insulating spacer {mi+1}',s,'poly','carrier')
        s=c(2.75,1.65,xx,yp,z,Z).fuse(c(1.4,10.0,xx,yp,z-10,Z))
        item(f'{lab} M3 locating fastener {mi+1}',s,'metal','hardware')
    # Mask-safe selectable edge support; use washers/shims to tune to actual PCB.
    for i,xx in enumerate([x0+148,x0+282,x0+382]):
        item(f'{lab} cross support {i+1}',b(7,55.7,3,xx-3.5,-27.85,support_z),'rail','carrier')
        for j,y in enumerate([-21.2,21.2]):
            item(f'{lab} insulating pad {i+1}.{j+1}',b(7,5,4,xx-3.5,y-2.5,z-P.board_t-4),'poly','carrier')
    for i,y in enumerate(JACK_Y):
        # Shape encodes reserved low-profile plug geometry and axial harness, not a selected connector.
        sh=b(20,2*P.plug_keepout_half_y,15,
             x0+JACK_X-16,y-P.plug_keepout_half_y,z+13)
        sh=sh.fuse(c(3.0,19,x0+JACK_X-28,y,z+22))
        item(f'{lab} right-angle plug envelope {i+1}',sh,'boot','harness')
        port_z=ROW_Z[1 if lab=='Upper' else 0]
        yp=PORT_Y[i]
        lx=x0+JACK_X-23
        cable,radius,length=s_route(52.5,lx,yp,port_z,y,z+22)
        ROUTES.append(dict(board=lab,connector=f'J{i+2}',port_y=yp,port_z=port_z,radius_mm=radius,length_mm=length,x_start=52.5,x_end=lx))
        item(f'{lab} internal detector jumper {i+1}',cable,'orange' if lab=='Upper' else 'bronze','harness')
def make():
    item('6061-T6 standard tube',mk_shell(),'shell','shell')
    item('Removable front collar',collar(0),'metal','cap')
    item('Distal collar',collar(P.tube_l-12),'metal','rear')
    end_caps()
    # Nylon stop spacers are captive under the removable collars. Shim at installation.
    for i,z in enumerate((-43,43)):
        item(f'Front removable pull bridge {i+1}',b(30+P.front_shift,8,3,11.8,-4,z-1.5),'rail','cap')
        item(f'Rear spacer insulating tip {i+1}',b(1.8,8,3,529.2+P.front_shift,-4,z-1.5),'poly','rear')
        # Stock length adds 54.60 mm to the blind end. Straight removable
        # metal extensions preserve the original rear datum without pruning tube.
        item(f'Rear locator extension {i+1}',b(P.tube_l-12-531.0-P.front_shift+0.2,8,3,531.0+P.front_shift,-4,z-1.5),'metal','rear')
    for end,x in [('Service',42),('Distal',522)]:
        item(end+' low-friction guide ring',end_spider(x+P.front_shift),'poly','carrier')
    for j,y in enumerate([-26.6,26.6]):
        # Pair of flat 6061 side rails, clear the full 49.1-mm tile width.
        item('Carrier longitudinal rail '+str(j+1),b(495,2.5,45,40+P.front_shift,y-1.25,-34.8),'rail','carrier')
    # Removable pair of insulating cable saddles. Wide (Ø8) saddles are not
    # modeled as tight ferrules; shim an elastomer pad against actual cable.
    for k,sgn in enumerate((-1,1),1):
        low=-44.5 if sgn<0 else 12
        saddle=b(3,48,32.5,57,-24,low).intersect(c(44.7,7,55,0,0))
        for yy in PORT_Y:
            saddle=saddle.cut(c(4.05,7,55,yy,sgn*18))
        # Cut into removable body and saddle lip at the cable centerline.
        for j,(lo,hi) in enumerate(((low,sgn*18-.1),(sgn*18+.1,low+32.5)),1):
            ss=saddle.intersect(b(6,50,hi-lo,55,-25,lo))
            item(f'Insulating strain-relief saddle {k}.{j}',ss,'poly','cap')
    tray(P.lower_board_top,'Lower')
    tray(P.upper_board_top,'Upper')
def rv(y,z):return math.hypot(y,z)
def validate():
    delta=P.upper_board_top-P.lower_board_top
    rail=rv(30,-37)
    plug= max(rv(y+s*P.plug_keepout_half_y,z+P.plug_height_from_pcb) for y in JACK_Y for s in (-1,1) for z in [P.lower_board_top,P.upper_board_top])
    gland=max(rv(y,z)+CAP_BORE_R for y,z in PORT_JACKS)
    cable=max(max(rv(y,z) for y,z in PORT_JACKS),max(rv(y,z+22) for y in JACK_Y for z in [-27,10]))+P.jacket_max_d/2
    # Make the controlling rail corners safe by clipping the bottom edges, not by just intersecting nominal shell.
    # Report CAD-computed radius after relief.
    yz=[]
    for name,(s,mat,g,rr) in parts.items():
        if g=='carrier' and 'longitudinal' in name:
            yz.extend(rv(v.Y,v.Z) for v in s.Vertices())
    rail=max(yz)
    tg= (P.tube_accept_min_id-P.guide_od)/2
    clearance=delta-P.plug_height_from_pcb-P.board_t
    assert tg>=1.0 and rail<P.guide_od/2 and plug<P.tube_accept_min_id/2-1 and cable < P.guide_id/2-1.0 and gland<P.tube_od/2 and clearance>5, (tg,rail,plug,cable,gland,clearance)
    axial_lig=min(min(rv(y,z)-P.collar_id/2,P.collar_od/2-rv(y,z))-1.5 for y,z in CAPFAST)
    assert axial_lig>1.0,axial_lig
    shell=parts['6061-T6 standard tube'][0]
    slide_radius=0.0; slide_at=None
    for name,(s,m,g,r) in parts.items():
        if g not in ['carrier','pcb','harness','hardware']:continue
        bound=max((rv(v.Y,v.Z) for v in s.Vertices()), default=0)
        if 'guide ring' in name:bound=max(bound,P.guide_od/2)
        if bound>slide_radius:slide_radius,slide_at=bound,name
    assert slide_radius <= P.tube_accept_min_id/2-1.0,(slide_radius,slide_at)
    overlaps={}
    for name,(s,m,g,r) in parts.items():
        if g in ['carrier','pcb','harness','hardware'] and 'detector cable' not in name:
            vs=shell.intersect(s).Volume()
            if vs>0.002:overlaps[name]=round(vs,4)
    assert not overlaps,overlaps
    assert min(p['radius_mm'] for p in ROUTES)>26.4
    panel=parts['Four-port aluminum patch endcap, 3.175 mm'][0]
    collar=parts['Removable front collar'][0]
    couplers=[(n,ss) for n,(ss,m,g,re) in parts.items() if g=='coupler']
    cerrors={}
    for n,ss in couplers:
        for ref,body in [('panel',panel),('collar',collar)]:
            vol=ss.intersect(body).Volume()
            if vol>0.005:cerrors[n+' vs '+ref]=round(vol,4)
    assert not cerrors,cerrors
    return {
      'board_geometry': 'Mechanical interface envelopes used for checks only', 'specification':asdict(P),
      'stock_extra_rear_length_mm': round(P.tube_l-555.0,2),
      'rear_locator_total_span_mm': round(P.tube_l-12+0.2-529.2-P.front_shift,2),
      'board_xy_coincident':True,'plane_top_separation_mm':delta,
      'tube_nominal_id_mm':round(P.tube_od-2*P.tube_wall,3),
      'guide_min_radial_clearance_mm':tg,'slide_min_radial_mm':round(P.tube_accept_min_id/2-slide_radius,3),'slide_limiting_item':slide_at,
      'plug_min_wall_radial_clearance_mm':round(P.tube_accept_min_id/2-plug,3),
      'lower_plug_to_upper_pcb_nominal_clearance_mm':round(clearance,3),
      'plug_envelope_includes_jack_mm':P.plug_height_from_pcb,
      'rail_max_radial_mm':round(rail,3),'M3_axial_min_collar_ligament_mm':round(axial_lig,3),
      'cable_min_ring_radial_clearance_mm':round(P.guide_id/2-cable,3),
      'mount_x_y_mm':MOUNT,'rj45_jack_y_mm':JACK_Y,'patch_ports_y_z_mm':PORT_JACKS,'jumper_routes':ROUTES,
      'shell_solid_interference':overlaps,'panel_and_collar_coupler_interference':cerrors,'first_article_fit_check':'Place insulating pads only at designated edge support points.'
    }
def relief():
    # Rails are eased below the lower plane to fit the same 91 mm carriage envelope.
    # The lowest original corner otherwise had radius 47.63 mm.
    for name,(s,mat,grp,ren) in list(parts.items()):
        if 'longitudinal rail' in name:
            candidate=s.intersect(c(44.8,600,-10,0,0))
            # Preserve 4-mm width up to the lower crossmember z; remove taper only past its footprint.
            parts[name]=(candidate,mat,grp,ren)
def save(out):
    out.mkdir(parents=True,exist_ok=True)
    assy=cq.Assembly(name='Two 8-channel 5 cm board holder | Rev 02')
    groups={}
    for name,(shape,color,group,_) in parts.items():
        if group in {'pcb','harness'}:
            continue
        assy.add(shape,name=name,color=cq.Color(*COLORS[color]))
        groups.setdefault(group,[]).append(shape)
    assy.save(str(out/'Mechanical_Only.step'))
    for name, shapes in [
        ('Tube', groups['shell']),
        ('Carrier_Assembly', groups['carrier']+groups['hardware']),
        ('Service_Endcap_Assembly', groups['cap']),
        ('Blind_End_Assembly', groups['rear']),
    ]:
        cq.exporters.export(comp(shapes),str(out/f'{name}.step'))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path('holder_build'))
    args=parser.parse_args()
    make()
    qa=validate()
    print(json.dumps(qa,indent=2))
    save(args.output)
    (args.output/'envelope_fit_check.json').write_text(json.dumps(qa,indent=2)+'\n')
