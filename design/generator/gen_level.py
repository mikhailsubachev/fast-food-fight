import math, json
import gen, gen_porek as gp, gen_ff as gf, curve
from gen import INK, star
W,H=1920,1080; HUD=104
# ---- level data (src/data/level1.ts)
path=[(-1,2.5),(8,2.5),(8,5),(2.5,5),(2.5,7.5),(9.5,7.5)]
slots=[(1,1.25),(6,1.25),(3.5,3.75),(5.5,3.75),(9.25,3.75),(1.25,6.25),(5,6.25),(7,6.25),(10.5,0.5),(10.8,4),(-0.3,5.5),(12.2,6)]
board=dict(minX=-1,maxX=12.7,minZ=-0.1,maxZ=8.6); mouth=(10.4,7.5)
# ---- camera like stage.ts: tilt 55°, fov 35, fit board
tilt=math.radians(55); fov=math.radians(35)
tx=(board['minX']+board['maxX'])/2; tz=(board['minZ']+board['maxZ'])/2
def make_proj(d,ox=0,oy=0,f=None):
    cy_,cz_=math.sin(tilt)*d, math.cos(tilt)*d
    # camera basis: forward = target - cam
    fwd=(0,-cy_,-cz_); n=math.hypot(*fwd); fwd=tuple(c/n for c in fwd)
    right=(1,0,0); up=(0,fwd[2]*-1*-1, 0)  # compute up = right x fwd
    up=(right[1]*fwd[2]-right[2]*fwd[1], right[2]*fwd[0]-right[0]*fwd[2], right[0]*fwd[1]-right[1]*fwd[0])
    pass
    foc=(H/2)/math.tan(fov/2) if f is None else f
    def P(x,y,z):
        v=(x-tx, y-cy_, z-tz-cz_)
        cx=sum(a*b for a,b in zip(v,right)); cyv=sum(a*b for a,b in zip(v,up)); cz=sum(a*b for a,b in zip(v,fwd))
        return (W/2+foc*cx/cz+ox, H/2-foc*cyv/cz+oy)
    return P
corners=[(x,y,z) for x in (board['minX'],board['maxX']) for z in (board['minZ'],board['maxZ']) for y in (0,1.4)]
lo,hi=2,400
availW=W*0.94; availH=(H-HUD)*0.94
for _ in range(50):
    mid=(lo+hi)/2; P=make_proj(mid); pts=[P(*c) for c in corners]
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    if max(xs)-min(xs)<=availW and max(ys)-min(ys)<=availH: hi=mid
    else: lo=mid
P=make_proj(hi); pts=[P(*c) for c in corners]
xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
P=make_proj(hi, W/2-(min(xs)+max(xs))/2, HUD+(H-HUD)/2-(min(ys)+max(ys))/2+6)
def pg(pts3): return " ".join(f"{P(*p)[0]:.1f},{P(*p)[1]:.1f}" for p in pts3)
def ground_poly(pts2,y=0): return pg([(x,y,z) for x,z in pts2])

# ---- table & bed
out=[]
out.append(f'<rect x="-400" y="-400" width="{W+800}" height="{H+800}" fill="#8BB85A"/>')
b=board; t=0.12
top=[(b['minX'],b['minZ']),(b['maxX'],b['minZ']),(b['maxX'],b['maxZ']),(b['minX'],b['maxZ'])]
front=[(b['minX'],0,b['maxZ']),(b['maxX'],0,b['maxZ']),(b['maxX'],-t,b['maxZ']),(b['minX'],-t,b['maxZ'])]
import random; r=random.Random(2)
import curve as _cv
OBST=[('stump',7.6,0.9,0.6),('rock',12.0,5.0,0.7),('puddle',3.6,6.3,0.85),('mole',10.4,2.2,0.6)]
def onpath(x,z,m=0.75): return _cv.dist(x,z)<m or any(math.hypot(x-ox,z-oz)<orr for _,ox,oz,orr in OBST)
def unit(x,z):
    a=P(x,0,z); b_=P(x,0.1,z); return a,(a[1]-b_[1])/6.0   # px per "decor unit"
# lighter / darker grass patches (irregular blobs)
for _ in range(46):
    cx,cz=r.uniform(-4,16),r.uniform(-3,11); rad=r.uniform(0.5,1.3)
    pts=[(cx+rad*(1+0.25*math.sin(k*1.7+cx))*math.cos(k/14*2*math.pi), cz+rad*0.8*(1+0.25*math.cos(k*1.3+cz))*math.sin(k/14*2*math.pi)) for k in range(14)]
    out.append(f'<polygon points="{ground_poly(pts)}" fill="{r.choice(["#9CC768","#7FAE4E","#94C262"])}" opacity=".7"/>')
# grass blades
for _ in range(420):
    x=r.uniform(-4,16); z=r.uniform(-3,11)
    p=P(x,0,z); out.append(f'<path d="M{p[0]:.0f},{p[1]:.0f} l-3,-9 M{p[0]:.0f},{p[1]:.0f} l1,-11 M{p[0]:.0f},{p[1]:.0f} l4,-8" stroke="{r.choice(["#5E8F38","#6E9C45","#4E7F2E"])}" stroke-width="2.4" stroke-linecap="round"/>')
decor=[]
def daisy(x,z,col="#FFFFFF"):
    p,u=unit(x,z); s_=u*1.0
    pet="".join(f'<ellipse cx="{p[0]+math.cos(k/6*2*math.pi)*5*s_:.1f}" cy="{p[1]-6*s_+math.sin(k/6*2*math.pi)*3*s_:.1f}" rx="{3.2*s_:.1f}" ry="{2.2*s_:.1f}" fill="{col}" stroke="{INK}" stroke-width="1.4"/>' for k in range(6))
    return f'<path d="M{p[0]:.1f},{p[1]:.1f} l0,{-6*s_:.1f}" stroke="#3F7A2A" stroke-width="2"/>'+pet+f'<circle cx="{p[0]:.1f}" cy="{p[1]-6*s_:.1f}" r="{2.6*s_:.1f}" fill="#FFC93C" stroke="{INK}" stroke-width="1.2"/>'
def clover(x,z):
    p,u=unit(x,z); s_=u
    return "".join(f'<circle cx="{p[0]+dx*s_:.1f}" cy="{p[1]+dy*s_:.1f}" r="{3.4*s_:.1f}" fill="#4E9A3A" stroke="#2F6B24" stroke-width="1.2"/>' for dx,dy in [(-3,-1),(3,-1),(0,-5)])
def mushroom(x,z):
    p,u=unit(x,z); s_=u*1.3
    return (f'<rect x="{p[0]-2.5*s_:.1f}" y="{p[1]-9*s_:.1f}" width="{5*s_:.1f}" height="{9*s_:.1f}" rx="{2*s_:.1f}" fill="#FFF4E0" stroke="{INK}" stroke-width="1.6"/>'
            f'<path d="M{p[0]-10*s_:.1f},{p[1]-8*s_:.1f} Q{p[0]:.1f},{p[1]-22*s_:.1f} {p[0]+10*s_:.1f},{p[1]-8*s_:.1f} Z" fill="#E0484F" stroke="{INK}" stroke-width="1.8"/>'
            f'<circle cx="{p[0]-3*s_:.1f}" cy="{p[1]-13*s_:.1f}" r="{1.8*s_:.1f}" fill="#FFFFFF"/><circle cx="{p[0]+4*s_:.1f}" cy="{p[1]-11*s_:.1f}" r="{1.5*s_:.1f}" fill="#FFFFFF"/>')
def stone(x,z):
    p,u=unit(x,z); s_=u*1.4
    return f'<ellipse cx="{p[0]:.1f}" cy="{p[1]-2*s_:.1f}" rx="{7*s_:.1f}" ry="{4*s_:.1f}" fill="#B9B3A6" stroke="{INK}" stroke-width="1.8"/><path d="M{p[0]-3*s_:.1f},{p[1]-4*s_:.1f} q3,-2 6,0" stroke="#E2DED5" stroke-width="2" fill="none"/>'
def ladybug(x,z):
    p,u=unit(x,z); s_=u*1.1
    return (f'<ellipse cx="{p[0]:.1f}" cy="{p[1]-3*s_:.1f}" rx="{6*s_:.1f}" ry="{4.6*s_:.1f}" fill="#E0484F" stroke="{INK}" stroke-width="1.6"/><path d="M{p[0]:.1f},{p[1]-7.5*s_:.1f} L{p[0]:.1f},{p[1]+1.5*s_:.1f}" stroke="{INK}" stroke-width="1.4"/>'
            f'<circle cx="{p[0]+6*s_:.1f}" cy="{p[1]-3*s_:.1f}" r="{2.4*s_:.1f}" fill="{INK}"/><circle cx="{p[0]-2.6*s_:.1f}" cy="{p[1]-4*s_:.1f}" r="{1.3*s_:.1f}" fill="{INK}"/><circle cx="{p[0]+2.4*s_:.1f}" cy="{p[1]-1.6*s_:.1f}" r="{1.3*s_:.1f}" fill="{INK}"/>')
def snail(x,z):
    p,u=unit(x,z); s_=u*1.3
    return (f'<path d="M{p[0]-12*s_:.1f},{p[1]:.1f} L{p[0]+10*s_:.1f},{p[1]:.1f} q4,-2 4,-7 l2,-5 M{p[0]+13*s_:.1f},{p[1]-7*s_:.1f} l4,-5" stroke="{INK}" stroke-width="1.6" fill="#E9D3A8"/>'
            f'<circle cx="{p[0]-2*s_:.1f}" cy="{p[1]-7*s_:.1f}" r="{7*s_:.1f}" fill="#C98A4A" stroke="{INK}" stroke-width="1.8"/><path d="M{p[0]-2*s_:.1f},{p[1]-7*s_:.1f} m-3,0 a3,3 0 1,1 3,3" stroke="{INK}" stroke-width="1.4" fill="none"/>')
items=[]
for _ in range(90):
    x=r.uniform(-3,15.5); z=r.uniform(-2,10)
    if onpath(x,z): continue
    k=r.random()
    if k<0.38: items.append((z,daisy(x,z)))
    elif k<0.5: items.append((z,daisy(x,z,"#FFE36A")))
    elif k<0.75: items.append((z,clover(x,z)))
    elif k<0.9: items.append((z,stone(x,z)))
    else: items.append((z,mushroom(x,z)))
for x,z,f in [(11.8,2.2,ladybug),(0.2,3.9,snail),(12.0,8.0,mushroom),(-0.5,0.4,mushroom),(6.2,8.2,ladybug)]:
    items.append((z,f(x,z)))
items.sort(key=lambda t:t[0])
out.extend(i for _,i in items)

# ---- path: irregular dirt track across the field
Lc,Rc=curve.edges()
out.append(f'<polygon points="{ground_poly(Lc+Rc[::-1])}" fill="#C9965A" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>')
Li,Ri=curve.edges(0.72)
out.append(f'<polygon points="{ground_poly(Li+Ri[::-1])}" fill="#DDB27A"/>')
for off in (0.24,-0.24):
    rut=[]
    for i,p in enumerate(curve.CENTER):
        a_=curve.CENTER[max(0,i-1)]; b_=curve.CENTER[min(len(curve.CENTER)-1,i+1)]
        dx,dz=b_[0]-a_[0],b_[1]-a_[1]; l=math.hypot(dx,dz) or 1
        rut.append((p[0]-dz/l*off,p[1]+dx/l*off))
    out.append(f'<polyline points="{ground_poly(rut)}" fill="none" stroke="#B9844B" stroke-width="5" stroke-linecap="round" stroke-dasharray="40 14 22 10"/>')
rr=random.Random(9)
for i in range(0,len(curve.CENTER),2):
    p=curve.CENTER[i]
    for _ in range(2):
        q=P(p[0]+rr.uniform(-0.35,0.35),0,p[1]+rr.uniform(-0.35,0.35))
        out.append(f'<ellipse cx="{q[0]:.0f}" cy="{q[1]:.0f}" rx="{rr.uniform(3,6):.1f}" ry="{rr.uniform(2,4):.1f}" fill="#9C7244" opacity=".8"/>')
for side in (Lc,Rc):
    for i in range(1,len(side),3):
        q=P(side[i][0],0,side[i][1])
        out.append(f'<path d="M{q[0]:.0f},{q[1]:.0f} l-5,-12 M{q[0]:.0f},{q[1]:.0f} l1,-14 M{q[0]:.0f},{q[1]:.0f} l7,-11" stroke="#4E8A2E" stroke-width="3" stroke-linecap="round"/>')
c0=curve.nearest(-1.4,2.45)
out.append(f'<polygon points="{ground_poly([(c0[0]-0.25,c0[1]-0.32),(c0[0]+0.45,c0[1]),(c0[0]-0.25,c0[1]+0.32)])}" fill="#E0574F" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')

# ---- free planting: plants anywhere on the bed (no fixed slots)
plants=[("mrkev",3.3,3.6),("mrkev_slash",5.4,3.65),("mrkev_frozen",9.65,3.9),("mrkev",1.1,6.7),("mrkev",5.0,6.15),("mrkev_grow",7.2,6.2),("porek_aim",10.8,4.0),("porek",-0.3,5.5),("porek",4.6,0.9)]
def mound(x,z,rad=0.36):
    pts=[(x+rad*math.cos(a/18*2*math.pi), z+rad*0.75*math.sin(a/18*2*math.pi)) for a in range(18)]
    return f'<polygon points="{ground_poly(pts)}" fill="#6B4A2E" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
for k,x,z in plants: out.append(mound(x,z))
# range ring of the selected leek (slot 9)
lx_,lz_=10.8,4.0
ring=[(lx_+3.5*math.cos(a/40*2*math.pi), lz_+3.5*math.sin(a/40*2*math.pi)) for a in range(40)]
out.append(f'<polygon points="{ground_poly(ring)}" fill="#2D8CD6" fill-opacity=".10" stroke="#2D8CD6" stroke-width="4" stroke-dasharray="14 10"/>')

# ---- figures (depth sorted)
def blob(x,z,rad=0.32):
    pts=[(x+rad*math.cos(a/16*2*math.pi), z+rad*0.8*math.sin(a/16*2*math.pi)) for a in range(16)]
    return f'<polygon points="{ground_poly(pts)}" fill="#2A1A0C" opacity=".22"/>'
FIG=1.8
def place(inner,x,z,hw=1.25,flip=False,feet=(150,388),lift=0):
    hw=hw*FIG
    g0=P(x,lift,z); g1=P(x,lift+hw,z); s=(g0[1]-g1[1])/360
    fl=" scale(-1,1)" if flip else ""
    return f'<g transform="translate({g0[0]:.1f},{g0[1]:.1f}) scale({s:.4f}){fl} translate({-feet[0]},{-feet[1]})">{inner}</g>'
figs=[]
def add(z,svg): figs.append((z,svg))
C=gen
for kind,x,z in plants:
    if kind=="mrkev":
        add(z, place(C.carrot("smile"),x,z))
    elif kind=="mrkev_slash":
        add(z, place(C.carrot("fight","slash"),x,z,flip=True))
    elif kind=="mrkev_frozen":
        add(z, place(C.carrot("frozen",tint="ice",extra_front=C.ice_bits),x,z))
    elif kind=="mrkev_grow":
        g0=P(x,0,z); g1=P(x,1.25*FIG,z); sc=(g0[1]-g1[1])/360
        inner=('<defs><clipPath id="lgclip"><rect x="0" y="-80" width="300" height="318"/></clipPath></defs><g clip-path="url(#lgclip)"><g transform="translate(5,150)">'+C.body()+C.TOP+C.leaves()+C.face("closed")+'</g></g>'
               +f'<path d="M95,238 A60,15 0 0 0 215,238" stroke="{INK}" stroke-width="5" fill="#3A2210"/>')
        bar=(f'<rect x="80" y="262" width="140" height="18" rx="9" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/><rect x="84" y="266" width="70" height="10" rx="5" fill="#6CBF45"/>')
        add(z, f'<g transform="translate({g0[0]:.1f},{g0[1]:.1f}) scale({sc:.4f}) translate(-150,-250)">{inner}{bar}</g>')
    elif kind.startswith("porek"):
        aim=kind=="porek_aim"
        add(z, place(gp.leek("aim" if aim else "smile","draw" if aim else "rest"),x,z,1.35,flip=aim))
# placement preview: ghost carrot, its reach and the radial menu
GX,GZ=6.9,3.75
ring2=[(GX+1.5*math.cos(a/32*2*math.pi), GZ+1.5*math.sin(a/32*2*math.pi)) for a in range(32)]
out.append(f'<polygon points="{ground_poly(ring2)}" fill="#F08A24" fill-opacity=".12" stroke="#F08A24" stroke-width="4" stroke-dasharray="12 9"/>')
foot=[(GX+0.42*math.cos(a/24*2*math.pi), GZ+0.42*0.75*math.sin(a/24*2*math.pi)) for a in range(24)]
out.append(f'<polygon points="{ground_poly(foot)}" fill="#FFFFFF" fill-opacity=".55" stroke="#3FA34D" stroke-width="5"/>')
add(GZ, f'<g opacity=".5">{place(C.carrot("smile"),GX,GZ)}</g>')
# obstacles: no planting here
def ell(x,z,rx,rz,y=0,n=28,a0=0,a1=2*math.pi):
    return [P(x+rx*math.cos(a0+(a1-a0)*k/(n-1)),y,z+rz*math.sin(a0+(a1-a0)*k/(n-1))) for k in range(n)]
def pts(l): return " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in l)
def stump(x,z):
    R=0.42; H_=0.38
    front=ell(x,z,R,R,0,20,0,math.pi); topf=ell(x,z,R,R,H_,20,math.pi,0)
    side=f'<polygon points="{pts(front+topf)}" fill="#8A5A30" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
    bark="".join(f'<path d="M{P(x+R*math.cos(a),0,z+R*math.sin(a))[0]:.0f},{P(x+R*math.cos(a),0,z+R*math.sin(a))[1]:.0f} L{P(x+R*math.cos(a),H_,z+R*math.sin(a))[0]:.0f},{P(x+R*math.cos(a),H_,z+R*math.sin(a))[1]:.0f}" stroke="#6B4222" stroke-width="3"/>' for a in [0.5,1.1,1.6,2.1,2.6])
    top=f'<polygon points="{pts(ell(x,z,R,R,H_))}" fill="#E9C48A" stroke="{INK}" stroke-width="4"/>'
    rings="".join(f'<polygon points="{pts(ell(x,z,R*k,R*k,H_))}" fill="none" stroke="#C49A60" stroke-width="2.5"/>' for k in (0.7,0.45,0.2))
    sp=P(x+R*0.9,H_*0.5,z+R*0.5)
    sprout=f'<path d="M{sp[0]:.0f},{sp[1]:.0f} q10,-14 22,-10 q-10,10 -22,10 Z" fill="#6CBF45" stroke="{INK}" stroke-width="2"/>'
    roots=f'<path d="M{P(x-R,0,z+0.1)[0]:.0f},{P(x-R,0,z+0.1)[1]:.0f} q-14,6 -24,4 M{P(x+R,0,z+0.1)[0]:.0f},{P(x+R,0,z+0.1)[1]:.0f} q14,6 26,2" stroke="#8A5A30" stroke-width="7" stroke-linecap="round" fill="none"/>'
    return roots+side+bark+top+rings+sprout
def rock(x,z):
    g=P(x,0,z); w=abs(P(x+0.6,0,z)[0]-g[0]); h=g[1]-P(x,0.75,z)[1]
    return (f'<ellipse cx="{g[0]:.0f}" cy="{g[1]:.0f}" rx="{w*1.05:.0f}" ry="{w*0.3:.0f}" fill="#2A1A0C" opacity=".2"/>'
            f'<path d="M{g[0]-w:.0f},{g[1]:.0f} C{g[0]-w*1.05:.0f},{g[1]-h*0.7:.0f} {g[0]-w*0.4:.0f},{g[1]-h*1.05:.0f} {g[0]+w*0.1:.0f},{g[1]-h:.0f} C{g[0]+w*0.7:.0f},{g[1]-h*0.95:.0f} {g[0]+w*1.05:.0f},{g[1]-h*0.5:.0f} {g[0]+w:.0f},{g[1]:.0f} Q{g[0]:.0f},{g[1]+w*0.18:.0f} {g[0]-w:.0f},{g[1]:.0f} Z" fill="#A7A196" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>'
            f'<path d="M{g[0]-w*0.5:.0f},{g[1]-h*0.6:.0f} Q{g[0]-w*0.2:.0f},{g[1]-h*0.9:.0f} {g[0]+w*0.2:.0f},{g[1]-h*0.85:.0f}" stroke="#D9D4CA" stroke-width="6" fill="none" stroke-linecap="round"/>'
            f'<path d="M{g[0]+w*0.35:.0f},{g[1]-h*0.45:.0f} l{w*0.15:.0f},{h*0.25:.0f} l{-w*0.1:.0f},{h*0.2:.0f}" stroke="{INK}" stroke-width="3" fill="none"/>'
            f'<path d="M{g[0]-w*0.7:.0f},{g[1]-h*0.15:.0f} q{w*0.15:.0f},{-h*0.18:.0f} {w*0.3:.0f},0" stroke="#6E9C45" stroke-width="7" stroke-linecap="round" fill="none"/>')
def puddle(x,z):
    pts_=[(x+0.8*(1+0.18*math.sin(k*2.1))*math.cos(k/16*2*math.pi), z+0.5*(1+0.2*math.cos(k*1.7))*math.sin(k/16*2*math.pi)) for k in range(16)]
    hl1=P(x-0.35,0,z-0.12); hl2=P(x+0.15,0,z+0.15)
    return (f'<polygon points="{ground_poly(pts_)}" fill="#7CC4EE" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
            f'<polygon points="{ground_poly([(px*0.8+x*0.2,pz*0.8+z*0.2) for px,pz in pts_])}" fill="#A8DBF7"/>'
            f'<path d="M{hl1[0]:.0f},{hl1[1]:.0f} q22,-6 44,0" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" fill="none"/><path d="M{hl2[0]:.0f},{hl2[1]:.0f} q14,-4 28,0" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" fill="none"/>'
            f'<polygon points="{pts(ell(x+0.45,z-0.05,0.12,0.08,0))}" fill="#4E9A3A" stroke="{INK}" stroke-width="2"/>')
def mole(x,z):
    g=P(x,0,z); w=abs(P(x+0.55,0,z)[0]-g[0]); h=g[1]-P(x,0.4,z)[1]
    hd=(g[0],g[1]-h*0.95)
    return (f'<path d="M{g[0]-w:.0f},{g[1]:.0f} Q{g[0]-w*0.6:.0f},{g[1]-h*1.2:.0f} {g[0]:.0f},{g[1]-h:.0f} Q{g[0]+w*0.6:.0f},{g[1]-h*1.2:.0f} {g[0]+w:.0f},{g[1]:.0f} Q{g[0]:.0f},{g[1]+w*0.2:.0f} {g[0]-w:.0f},{g[1]:.0f} Z" fill="#6B4A2E" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
            + "".join(f'<circle cx="{g[0]+dx*w:.0f}" cy="{g[1]-dy*h:.0f}" r="4" fill="#8B5A2B" stroke="{INK}" stroke-width="1.5"/>' for dx,dy in [(-0.5,0.4),(0.4,0.3),(-0.1,0.2),(0.65,0.1)])
            + f'<ellipse cx="{hd[0]:.0f}" cy="{hd[1]:.0f}" rx="{w*0.32:.0f}" ry="{w*0.26:.0f}" fill="#5A4A4A" stroke="{INK}" stroke-width="3"/>'
            f'<circle cx="{hd[0]-w*0.1:.0f}" cy="{hd[1]-w*0.06:.0f}" r="2.6" fill="{INK}"/><circle cx="{hd[0]+w*0.1:.0f}" cy="{hd[1]-w*0.06:.0f}" r="2.6" fill="{INK}"/>'
            f'<ellipse cx="{hd[0]:.0f}" cy="{hd[1]+w*0.08:.0f}" rx="{w*0.09:.0f}" ry="{w*0.06:.0f}" fill="#F07A86" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M{hd[0]-w*0.3:.0f},{hd[1]+w*0.2:.0f} q-6,4 -10,2 M{hd[0]+w*0.3:.0f},{hd[1]+w*0.2:.0f} q6,4 10,2" stroke="#F0C6B0" stroke-width="5" stroke-linecap="round" fill="none"/>')
OBJ={'stump':stump,'rock':rock,'puddle':puddle,'mole':mole}
for k,ox,oz,_ in OBST:
    if k=='puddle': out.append(puddle(ox,oz))
    else: add(oz, OBJ[k](ox,oz))
# attackers on path
add(2.5, blob(6.4,2.4,0.36)+place(gf.burger("angry","up","step",extra=gf.motion),6.4,2.4,1.2))
add(3.78, blob(8.51,3.78,0.34)+place(gf.fries("throw","windup"),8.51,3.78,1.2))
add(4.88, blob(4.61,4.88,0.36)+place(gf.burger("hit","down"),4.61,4.88,1.1))
add(2.36, blob(1.45,2.36,0.34)+place(gf.burger("scared","flail","run",extra=gf.sweat(220,150)),1.45,2.36,1.2,flip=True))
add(6.84, blob(2.39,6.84,0.36)+place(gf.burger("angry","up","stand"),2.39,6.84,1.2))
# mouth
def mouth_svg():
    # original mouth, slightly turned towards the end of the path (to the left)
    face=(f'<ellipse cx="62" cy="250" rx="34" ry="22" fill="#F4A6A0" opacity=".85"/><ellipse cx="238" cy="250" rx="34" ry="22" fill="#F4A6A0" opacity=".85"/>'
      f'<path d="M30,230 Q150,100 270,230 Q150,400 30,230 Z" fill="#E0484F" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
      f'<path d="M62,232 Q150,170 238,232 Q150,350 62,232 Z" fill="#5A1220" stroke="{INK}" stroke-width="5"/>'
      f'<path d="M80,224 Q150,184 220,224 L214,244 L188,236 L184,252 L160,238 L150,254 L140,238 L116,252 L112,236 L86,244 Z" fill="#FFFFFF" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
      f'<path d="M104,290 Q150,250 196,290 Q150,326 104,290 Z" fill="#F07A86" stroke="{INK}" stroke-width="4"/>'
      f'<path d="M150,276 L150,300" stroke="#C9515F" stroke-width="4" stroke-linecap="round"/>'
      f'<path d="M72,196 Q150,140 228,196" stroke="#FF9AA0" stroke-width="8" fill="none" stroke-linecap="round" opacity=".8"/>'
      f'<path d="M40,150 l-16,-14 M262,150 l16,-14 M150,104 l0,-20" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
      f'<path d="M238,300 q8,14 0,20 q-8,-6 0,-20 Z" fill="#9AD4F5" stroke="{INK}" stroke-width="3"/>')
    depth=f'<path d="M44,230 Q164,100 284,230 Q164,400 44,230 Z" fill="#A82C34" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
    return (f'<ellipse cx="150" cy="392" rx="120" ry="20" fill="#2A1A0C" opacity=".2"/>'
            f'<g transform="translate(150,250) rotate(-6) scale(0.86,1) translate(-150,-250)">{depth}{face}</g>')
add(7.5, place(mouth_svg(),mouth[0]+0.3,mouth[1],2.6))

figs.sort(key=lambda t:t[0])
fid="lvw"
out.append(f'<defs><filter id="{fid}" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="4"/><feDisplacementMap in="SourceGraphic" scale="2.4"/></filter></defs>')
out.append(f'<g filter="url(#{fid})">'+"".join(f for _,f in figs)+'</g>')

# flying friends above the field
def butterfly(cx,cy,c1,c2,rot=0):
    return (f'<g transform="translate({cx:.0f},{cy:.0f}) rotate({rot})"><ellipse cx="-9" cy="-6" rx="10" ry="8" fill="{c1}" stroke="{INK}" stroke-width="2.5"/><ellipse cx="9" cy="-6" rx="10" ry="8" fill="{c1}" stroke="{INK}" stroke-width="2.5"/>'
            f'<ellipse cx="-7" cy="7" rx="7" ry="6" fill="{c2}" stroke="{INK}" stroke-width="2.5"/><ellipse cx="7" cy="7" rx="7" ry="6" fill="{c2}" stroke="{INK}" stroke-width="2.5"/><rect x="-2.5" y="-10" width="5" height="22" rx="2.5" fill="{INK}"/><path d="M-1,-10 q-4,-8 -8,-9 M1,-10 q4,-8 8,-9" stroke="{INK}" stroke-width="2" fill="none"/></g>')
def bee(cx,cy):
    return (f'<g transform="translate({cx:.0f},{cy:.0f})"><ellipse cx="-4" cy="-10" rx="7" ry="9" fill="#FFFFFF" fill-opacity=".85" stroke="{INK}" stroke-width="2"/><ellipse cx="6" cy="-10" rx="7" ry="9" fill="#FFFFFF" fill-opacity=".85" stroke="{INK}" stroke-width="2"/>'
            f'<ellipse cx="0" cy="0" rx="13" ry="9" fill="#FFC93C" stroke="{INK}" stroke-width="2.5"/><path d="M-4,-8 L-4,8 M4,-8 L4,8" stroke="{INK}" stroke-width="3"/><circle cx="9" cy="-2" r="1.8" fill="{INK}"/></g>')
for (wx,wy,wz,c1,c2,rot) in [(0.6,1.8,1.5,"#9FD3F5","#6CB6E8",-12),(11.6,1.9,6.9,"#F6B0D0","#E77FB0",14)]:
    q=P(wx,wy,wz); out.append(f'<path d="M{q[0]-70:.0f},{q[1]+30:.0f} q30,-40 60,-8" stroke="{INK}" stroke-width="2" fill="none" stroke-dasharray="2 7" opacity=".6"/>'+butterfly(q[0],q[1],c1,c2,rot))
q=P(9.0,1.6,1.0); out.append(f'<path d="M{q[0]-60:.0f},{q[1]+10:.0f} q20,-30 40,0 q20,30 40,0" stroke="{INK}" stroke-width="2" fill="none" stroke-dasharray="2 7" opacity=".6"/>'+bee(q[0]+28,q[1]))
# radial menu above the ghost
mp=P(GX,1.6*FIG,GZ)
def mbtn(cx,cy,icon,price,sel=False):
    return (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="40" fill="{"#FFF4D6" if sel else "#FFFFFF"}" stroke="{INK}" stroke-width="4"/>'
            +icon+f'<g transform="translate({cx:.0f},{cy+40:.0f})"><rect x="-30" y="-14" width="60" height="28" rx="14" fill="#2D8CD6" stroke="{INK}" stroke-width="3"/><text x="0" y="7" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="20" fill="#FFFFFF">{price}</text></g>')
lx1,ly1=mp[0]-52,mp[1]-46; lx2,ly2=mp[0]+52,mp[1]-46
ic1=f'<g transform="translate({lx1:.0f},{ly1+30:.0f}) scale(.17) translate(-155,-388)">{C.carrot("smile")}</g>'
ic2=f'<g transform="translate({lx2:.0f},{ly2+30:.0f}) scale(.16) translate(-152,-388)">{gp.leek("smile")}</g>'
out.append(f'<path d="M{mp[0]:.0f},{mp[1]+28:.0f} L{mp[0]:.0f},{mp[1]-6:.0f}" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
out.append(mbtn(lx1,ly1,ic1,"40",True)+mbtn(lx2,ly2,ic2,"60"))
# a "can't plant here" cross on the path
xp=P(3.6,0,5.0)
out.append(f'<g transform="translate({xp[0]:.0f},{xp[1]:.0f})"><circle r="20" fill="#FFFFFF" stroke="#D9342B" stroke-width="5"/><path d="M-9,-9 L9,9 M9,-9 L-9,9" stroke="#D9342B" stroke-width="5" stroke-linecap="round"/></g>')
# ---- projectiles (screen space from projected points)
lp=P(10.8,1.4,4); tp=P(8.76,1.3,3.78)
mid=((lp[0]+tp[0])/2,min(lp[1],tp[1])-120)
out.append(f'<path d="M{lp[0]-30:.0f},{lp[1]:.0f} Q{mid[0]:.0f},{mid[1]:.0f} {tp[0]:.0f},{tp[1]:.0f}" stroke="{INK}" stroke-width="3.5" fill="none" stroke-dasharray="3 11" stroke-linecap="round"/>')
ap=( (lp[0]-30+2*mid[0]+tp[0])/4, (lp[1]+2*mid[1]+tp[1])/4 )
out.append(f'<g transform="translate({ap[0]:.0f},{ap[1]:.0f}) rotate(180) scale(1.1)">{gp.arrow_local()}</g>')
fp=P(8.51,1.9,3.78); cp=P(9.65,1.0,3.9)
m2=((fp[0]+cp[0])/2,min(fp[1],cp[1])-90)
out.append(f'<path d="M{fp[0]:.0f},{fp[1]:.0f} Q{m2[0]:.0f},{m2[1]:.0f} {cp[0]:.0f},{cp[1]:.0f}" stroke="#C0352C" stroke-width="3.5" fill="none" stroke-dasharray="3 11" stroke-linecap="round"/>')
cp2=P(9.65,1.3,3.9); out.append(f'<path d="M{cp2[0]-34:.0f},{cp2[1]-22:.0f} l-12,-10 M{cp2[0]+34:.0f},{cp2[1]-22:.0f} l12,-10 M{cp2[0]:.0f},{cp2[1]-40:.0f} l0,-16" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
out.append(gf.txt(cp2[0]-40,cp2[1]-60,"PLESK!","#FFD54A",30,-6))
# carrot slash text
sp=P(5.4,2.3,3.65); out.append(gf.txt(sp[0]+20,sp[1]-10,"ŠVIH!","#F08A24",30,-10))
hp=P(4.61,2.1,4.88); out.append(gf.txt(hp[0]-20,hp[1]-6,"AU!","#D9342B",34,-8))
# water drop flying to HUD from runner
Z=1.3; ZCX,ZCY=1060,800
zout=out; out=[]
_r=P(1.45,2.0,2.36); rp=(ZCX+Z*(_r[0]-ZCX), ZCY+Z*(_r[1]-ZCY))
out.append(f'<path d="M{rp[0]:.0f},{rp[1]:.0f} Q{rp[0]-40:.0f},{HUD+40} 150,62" stroke="#3D9BE0" stroke-width="4" fill="none" stroke-dasharray="3 11" stroke-linecap="round"/>')
dp=( (rp[0]+2*(rp[0]-40)+150)/4, (rp[1]+2*(HUD+40)+62)/4 )
out.append(gf.water_drop(dp[0],dp[1],1.0)+gf.sparkle(dp[0]+28,dp[1]-24,9)+gf.sparkle(dp[0]-26,dp[1]+8,7))
out.append(f'<text x="{dp[0]+30:.0f}" y="{dp[1]+30:.0f}" font-family="Baloo 2, sans-serif" font-weight="800" font-size="32" fill="#2D8CD6" stroke="{INK}" stroke-width="1.2">+15</text>')

scene_svg=f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Úroveň 1: zelenina brání pusu u cesty ve tvaru S" style="position:absolute;left:0;top:0;display:block"><g transform="translate({ZCX},{ZCY}) scale({Z}) translate({-ZCX},{-ZCY})">{"".join(zout)}</g>{"".join(out)}</svg>'

drop_ic='<svg viewBox="0 0 24 24" width="34" height="34" aria-hidden="true"><path d="M12 2 C12 2 4.5 11 4.5 15.5 A7.5 7.5 0 0 0 19.5 15.5 C19.5 11 12 2 12 2 Z" fill="#3D9BE0" stroke="#2B2118" stroke-width="1.8"/><path d="M8.5 15 Q8.5 11.5 10.5 9" stroke="#CDEBFF" stroke-width="1.6" fill="none" stroke-linecap="round"/></svg>'
tooth='<svg viewBox="0 0 30 34" width="34" height="38" aria-hidden="true"><path d="M4 6 Q4 2 9 2 Q15 4 21 2 Q26 2 26 6 Q27 16 23 30 Q21 34 19 28 L17 20 Q15 17 13 20 L11 28 Q9 34 7 30 Q3 16 4 6 Z" fill="#FFFFFF" stroke="#2B2118" stroke-width="2.4" stroke-linejoin="round"/></svg>'
pill="display:flex;align-items:center;gap:10px;height:64px;box-sizing:border-box;padding:0 22px;background:#FFFFFF;border:4px solid #2B2118;border-radius:999px;box-shadow:0 5px 0 #2B2118"
html=f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>Úroveň 1 – Snídaňová cesta</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&amp;family=Bangers&amp;family=Nunito:wght@600;800&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#9A5416}}a:hover{{color:#6E3A0E}}
</style>
</helmet>
<div style="width:1920px;height:1080px;position:relative;overflow:hidden;font-family:'Baloo 2',sans-serif;color:#2B2118;background:#8BB85A">
{scene_svg}
<div style="position:absolute;left:28px;right:28px;top:20px;display:flex;align-items:center;justify-content:space-between;gap:20px">
<div style="{pill};min-width:170px">{drop_ic}<span style="font-size:38px;font-weight:800;line-height:1">135</span></div>
<div style="display:flex;align-items:center;gap:16px">
<div style="{pill};gap:6px" aria-label="Pusa má 3 životy">{tooth}{tooth}{tooth}</div>
<div style="{pill}"><span style="font-size:32px;font-weight:800;line-height:1">Vlna 3/4</span></div>
</div>
<button aria-label="Pauza" style="width:68px;height:68px;border-radius:50%;background:#FFFFFF;border:4px solid #2B2118;box-shadow:0 5px 0 #2B2118;display:flex;align-items:center;justify-content:center;gap:8px;padding:0;cursor:pointer"><span style="width:9px;height:26px;background:#2B2118;border-radius:3px"></span><span style="width:9px;height:26px;background:#2B2118;border-radius:3px"></span></button>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1920,"height":1080}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
ROOT="/mnt/user-data/outputs/artifacts/0c045be6-49f0-4f56-9475-27d367f93a14/project"
open(ROOT+"/Uroven1.dc.html","w").write(html); print(len(html))
