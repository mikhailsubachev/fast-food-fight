import math
import gen_level as G, gen_ff as gf, gen_porek as gp, gen
from gen import INK
ROOT="/mnt/user-data/outputs/artifacts/0c045be6-49f0-4f56-9475-27d367f93a14/project"
W,H=1920,1080
import sys
HR=int(sys.argv[1]) if len(sys.argv)>1 else 72; HH=HR*math.sqrt(3); X0=40; Y0=150
LETTER=sys.argv[2] if len(sys.argv)>2 else 'B'; OUTF=sys.argv[3] if len(sys.argv)>3 else 'MapaSestihranyMale.dc.html'
def hexp(px,py,k=0.97): return " ".join(f"{px+k*HR*math.cos(math.radians(60*i)):.1f},{py+k*HR*math.sin(math.radians(60*i)):.1f}" for i in range(6))
OB=[(k,x*G.SX,z*G.SZ,r) for k,x,z,r in G.OBST]
cells=[]
for row in range(-1,9):
    for col in range(-1,20):
        px=X0+col*HR*1.5; py=Y0+row*HH+(HH/2 if col%2 else 0)
        if px<-HR or px>W+HR or py<-HH or py>H+HH: continue
        wx,wz=px/G.SX,py/G.SZ
        if any(math.hypot(px-ox,py-oy)<max(HR*0.95,r*G.SX*0.9) for _,ox,oy,r in OB): k="obst"
        elif G._cv.dist(wx,wz)<0.78: k="path"
        elif G.MOUTHBOX[0]<px and py>G.MOUTHBOX[1]: k="mouth"
        elif not (40<px<W-40) or py>1030 or py<130: k="edge"
        else: k="free"
        cells.append((k,px,py))
cnt={k:sum(1 for c in cells if c[0]==k) for k in ("free","path","obst","mouth","edge")}
STY={"free":('#C6E88E','.85','#3E6B25'),"path":('#DDB27A','.8','#8A5A2E'),"obst":(f'url(#hatchO{LETTER})','1','#5A5550'),"mouth":('#F4A6A0','.8','#B8323A'),"edge":('#9DB27E','.55','#5E7A45')}
s=[f'<defs><pattern id="hatchO{LETTER}" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="12" height="12" fill="#BDBAB2"/><rect width="4" height="12" fill="#8E8A82"/></pattern></defs>',
   f'<rect width="{W}" height="{H}" fill="#8BB85A"/>']
Lc,Rc=G.curve.edges()
s.append(f'<polygon points="{G.ground_poly(Lc+Rc[::-1])}" fill="#C9965A" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
for k,px,py in cells:
    f,op,st=STY[k]
    s.append(f'<polygon points="{hexp(px,py)}" fill="{f}" fill-opacity="{op}" stroke="{st}" stroke-width="2.5" stroke-linejoin="round"/>')
cp=" ".join(f"{x*G.SX:.0f},{z*G.SZ:.0f}" for x,z in G.curve.CENTER)
s.append(f'<polyline points="{cp}" fill="none" stroke="#7A4A24" stroke-width="5" stroke-dasharray="16 12" stroke-linecap="round"/>')
for i in range(8,len(G.curve.CENTER)-4,22):
    a=G.curve.CENTER[i]; b=G.curve.CENTER[i+2]; ang=math.degrees(math.atan2((b[1]-a[1])*G.SZ,(b[0]-a[0])*G.SX))
    s.append(f'<g transform="translate({a[0]*G.SX:.0f},{a[1]*G.SZ:.0f}) rotate({ang:.0f})"><path d="M-12,-14 L10,0 L-12,14" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></g>')
for k,ox,oz,_ in G.OBST:
    s.append(G.puddle(ox,oz) if k=='puddle' else G.OBJ[k](ox,oz))
s.append(G.place(G.mouth_svg(),G.mouth[0]+0.3,G.mouth[1],1.6))
c0=G.curve.nearest(0.3,3.0)
s.append(f'<g transform="translate({c0[0]*G.SX+20:.0f},{c0[1]*G.SZ:.0f})"><circle r="30" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/><text y="6" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="15" fill="{INK}">START</text></g>')
# size samples: vegetables scaled so a plant is as tall as the hex pitch (no overlap), fast food at today's size
free=[c for c in cells if c[0]=="free"]
def near(x,y): return min(free,key=lambda c:(c[1]-x)**2+(c[2]-y)**2)
def put(svg,px,py,h,flip=False):
    sc=h/360; fl=" scale(-1,1)" if flip else ""
    return f'<g transform="translate({px:.0f},{py+HR*0.45:.0f}) scale({sc:.4f}){fl} translate(-150,-388)">{svg}</g>'
plant_h=HH*0.98
samples=[]
for (tx,ty),svg in [((560,520),gen.carrot("smile")),((760,640),gp.leek("smile")),((1000,860),gen.carrot("fight","slash")),((300,700),gp.leek("smile"))]:
    k,px,py=near(tx,ty)
    samples.append((py,f'<polygon points="{hexp(px,py,0.72)}" fill="#7A5433" stroke="{INK}" stroke-width="3"/>'+put(svg,px,py,plant_h)))
ff_h=1.2*G.FIG*120*0.85
for wx,wz,svg in [(6.2,5.3,gf.burger("angry","up","step")),(10.5,5.7,gf.fries("angry","stand"))]:
    p=G.curve.nearest(wx,wz); samples.append((p[1]*G.SZ,put(svg,p[0]*G.SX,p[1]*G.SZ-HR*0.45,ff_h)))
samples.sort()
s.append('<g>'+"".join(x for _,x in samples)+'</g>')
mapsvg=f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Nákres mapy 1. úrovně, varianta {LETTER}" style="display:block">{"".join(s)}</svg>'
def sw(fill,st,op="1"): return f'<span style="width:34px;height:30px;flex:none;clip-path:polygon(25% 0,75% 0,100% 50%,75% 100%,25% 100%,0 50%);background:{st};display:flex;align-items:center;justify-content:center"><span style="width:28px;height:24px;clip-path:polygon(25% 0,75% 0,100% 50%,75% 100%,25% 100%,0 50%);background:{fill};opacity:{op}"></span></span>'
leg=[(sw("#C6E88E","#3E6B25"),"sem jde sázet",cnt["free"]),(sw("#DDB27A","#8A5A2E"),"cesta",cnt["path"]),(sw("repeating-linear-gradient(45deg,#BDBAB2 0 6px,#8E8A82 6px 10px)","#5A5550"),"překážka",cnt["obst"]),
     (sw("#F4A6A0","#B8323A"),"pusa",cnt["mouth"]),(sw("#9DB27E","#5E7A45",".7"),"okraj (pod lištou / mimo obrazovku)",cnt["edge"])]
items="".join(f'<div style="display:flex;align-items:center;gap:10px">{a}<span style="font-size:18px;font-weight:800">{b}</span><span style="font-size:16px;font-weight:800;color:#5A4A3A;background:#F3EEE4;border-radius:999px;padding:2px 10px">{n}</span></div>' for a,b,n in leg)
html=f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>Nákres mapy 1. úrovně – varianta {LETTER}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&amp;family=Nunito:wght@600;700;800&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#3B7A2A}}a:hover{{color:#2A5A1E}}
</style>
</helmet>
<div style="width:1920px;height:1260px;background:#FBF6EC;font-family:Nunito,sans-serif;color:{INK};display:flex;flex-direction:column">
<div style="height:180px;box-sizing:border-box;padding:28px 48px;display:flex;justify-content:space-between;align-items:center;gap:40px">
<div style="display:flex;flex-direction:column;gap:6px;max-width:860px">
<span style="font-size:15px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#3B7A2A">Fast Food Fight · 1. úroveň · nákres {LETTER}</span>
<h1 style="margin:0;font-family:'Baloo 2',sans-serif;font-size:52px;font-weight:800;line-height:1">{'Menší šestihrany' if LETTER=='B' else 'Střední šestihrany'}</h1>
<span style="font-size:16px;font-weight:700;color:#5A4A3A;line-height:1.35">Šestihran {round(HR*2)} × {round(HH)} px (předtím {round(G.HR*2)} × {round(G.HH)}). Aby se sousední rostliny nepřekrývaly, zelenina je vysoká nejvýš jako rozestup šestihranů, tedy {'asi o třetinu' if LETTER=='B' else 'asi o šestinu'} menší než teď. Fast food zůstává stejně velký.</span>
</div>
<div style="display:grid;grid-template-columns:repeat(2, minmax(0, auto));gap:10px 34px">{items}</div>
</div>
<div style="position:relative;width:1920px;height:1080px;overflow:hidden">{mapsvg}</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1920,"height":1260}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
open(f"{ROOT}/{OUTF}","w").write(html); print(len(html), cnt)
