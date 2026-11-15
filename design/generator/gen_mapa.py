import math
import gen_level as G
from gen import INK
ROOT="/mnt/user-data/outputs/artifacts/0c045be6-49f0-4f56-9475-27d367f93a14/project"
W,H=1920,1080
HR,HH=G.HR,G.HH
def hexp(px,py,k=0.97): return " ".join(f"{px+k*HR*math.cos(math.radians(60*i)):.1f},{py+k*HR*math.sin(math.radians(60*i)):.1f}" for i in range(6))
cells=[]
for row in range(-1,8):
    for col in range(-1,15):
        px=G.HX0+col*HR*1.5; py=G.HY0+row*HH+(HH/2 if col%2 else 0)
        if px<-HR or px>W+HR or py<-HH or py>H+HH: continue
        wx,wz=px/G.SX,py/G.SZ
        if any(abs(wx-c[0])<1e-6 and abs(wz-c[1])<1e-6 for c in G.OBCELLS): k="obst"
        elif G._cv.dist(wx,wz)<1.0 and not any(abs(px-fx)<2 and abs(py-fy)<2 for fx,fy in G.FORCE_FREE): k="path"
        elif G.MOUTHBOX[0]<px and py>G.MOUTHBOX[1]: k="mouth"
        elif not (50<px<W-50) or py>1010 or py<150: k="edge"
        else: k="free"
        cells.append((k,px,py))
cnt={k:sum(1 for c in cells if c[0]==k) for k in ("free","path","obst","mouth","edge")}
STY={"free":('#C6E88E','.85','#3E6B25'),"path":('#DDB27A','.8','#8A5A2E'),"obst":('url(#hatchO)','1','#5A5550'),"mouth":('#F4A6A0','.8','#B8323A'),"edge":('#9DB27E','.55','#5E7A45')}
s=[f'<defs><pattern id="hatchO" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="14" height="14" fill="#BDBAB2"/><rect width="5" height="14" fill="#8E8A82"/></pattern></defs>',
   f'<rect width="{W}" height="{H}" fill="#8BB85A"/>']
Lc,Rc=G.curve.edges()
s.append(f'<polygon points="{G.ground_poly(Lc+Rc[::-1])}" fill="#C9965A" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
for k,px,py in cells:
    f,op,st=STY[k]
    s.append(f'<polygon points="{hexp(px,py)}" fill="{f}" fill-opacity="{op}" stroke="{st}" stroke-width="3" stroke-linejoin="round"/>')
# centre path line + direction arrows
cp=" ".join(f"{x*G.SX:.0f},{z*G.SZ:.0f}" for x,z in G.curve.CENTER)
s.append(f'<polyline points="{cp}" fill="none" stroke="#7A4A24" stroke-width="5" stroke-dasharray="16 12" stroke-linecap="round"/>')
for i in range(8,len(G.curve.CENTER)-4,22):
    a=G.curve.CENTER[i]; b=G.curve.CENTER[i+2]; ang=math.degrees(math.atan2((b[1]-a[1])*G.SZ,(b[0]-a[0])*G.SX))
    s.append(f'<g transform="translate({a[0]*G.SX:.0f},{a[1]*G.SZ:.0f}) rotate({ang:.0f})"><path d="M-12,-14 L10,0 L-12,14" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></g>')
# obstacles and mouth drawn small on their cells
for k,ox,oz,_ in G.OBST:
    if k=='puddle': s.append(G.puddle(ox,oz))
    else: s.append(G.OBJ[k](ox,oz))
s.append(G.place(G.mouth_svg(),G.mouth[0]+0.3,G.mouth[1],1.6))
# start
c0=G.curve.nearest(0.3,3.0)
s.append(f'<g transform="translate({c0[0]*G.SX+20:.0f},{c0[1]*G.SZ:.0f})"><circle r="30" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/><text y="9" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="24" fill="{INK}">START</text></g>'.replace('font-size="24"','font-size="15"'))
mapsvg=f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Nákres mapy 1. úrovně vyplněné šestihrany" style="display:block">{"".join(s)}</svg>'
def sw(fill,st,op="1"): return f'<span style="width:34px;height:30px;flex:none;clip-path:polygon(25% 0,75% 0,100% 50%,75% 100%,25% 100%,0 50%);background:{st};display:flex;align-items:center;justify-content:center"><span style="width:28px;height:24px;clip-path:polygon(25% 0,75% 0,100% 50%,75% 100%,25% 100%,0 50%);background:{fill};opacity:{op}"></span></span>'
leg=[(sw("#C6E88E","#3E6B25"),"sem jde sázet",cnt["free"]),(sw("#DDB27A","#8A5A2E"),"cesta",cnt["path"]),(sw("repeating-linear-gradient(45deg,#BDBAB2 0 6px,#8E8A82 6px 10px)","#5A5550"),"překážka",cnt["obst"]),
     (sw("#F4A6A0","#B8323A"),"pusa",cnt["mouth"]),(sw("#9DB27E","#5E7A45",".7"),"okraj (pod lištou / mimo obrazovku)",cnt["edge"])]
items="".join(f'<div style="display:flex;align-items:center;gap:10px">{a}<span style="font-size:18px;font-weight:800">{b}</span><span style="font-size:16px;font-weight:800;color:#5A4A3A;background:#F3EEE4;border-radius:999px;padding:2px 10px">{n}</span></div>' for a,b,n in leg)
html=f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>Nákres mapy 1. úrovně</title>
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
<div style="height:180px;box-sizing:border-box;padding:32px 48px;display:flex;justify-content:space-between;align-items:center;gap:40px">
<div style="display:flex;flex-direction:column;gap:6px">
<span style="font-size:15px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#3B7A2A">Fast Food Fight · 1. úroveň · nákres</span>
<h1 style="margin:0;font-family:'Baloo 2',sans-serif;font-size:52px;font-weight:800;line-height:1">Mapa vyplněná šestihrany</h1>
<span style="font-size:16px;font-weight:700;color:#5A4A3A">Celá obrazovka 1920 × 1080 pokrytá mřížkou. Jedna zelenina na šestihran, šestihran {round(HR*2)} × {round(HH)} px.</span>
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
open(f"{ROOT}/MapaSestihrany.dc.html","w").write(html); print(len(html), cnt)
