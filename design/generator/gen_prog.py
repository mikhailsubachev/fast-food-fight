import math, curve
import gen_level as G
OB={k:(x,z) for k,x,z,_ in G.OBST}
def hexm(wx,wz,k=G.HK*1.1):
    return ' '.join(f"{X(wx)+k*G.HR/G.SX*S*math.cos(math.radians(60*i)):.1f},{Y(wz)+k*G.HR/G.SX*S*math.sin(math.radians(60*i)):.1f}" for i in range(6))
L2=[(4.45,5.3,1.25),(13.0,5.0,1.9),(1.1,1.7,1.0),(8.4,4.9,1.5),(8.5,7.4,1.3)]
L3=[(3.5,3.7,5.5,4.7),(3.5,5.7,5.5,6.9),(7.1,3.7,9.6,4.7),(7.5,6.3,9.6,7.4),(11.4,5.4,13.3,6.5),(0.5,4.4,2.0,5.6)]
def free(level):
    out=[]
    for c in G.CELLS:
        if level==1 and c in G.OBCELLS: continue
        if level==2 and any(math.hypot(c[0]-x,c[1]-z)<r for x,z,r in L2): continue
        if level==3 and not any(x0-0.6<=c[0]<=x1+0.6 and z0-0.6<=c[1]<=z1+0.6 for x0,z0,x1,z1 in L3): continue
        out.append(c)
    return out
INK="#2B2118"
path=[(-1,2.5),(8,2.5),(8,5),(2.5,5),(2.5,7.5),(9.5,7.5)]
B=dict(minX=0,maxX=16,minZ=0,maxZ=10)
S=32; OX=12; OY=12
def X(x): return OX+(x-B['minX'])*S
def Y(z): return OY+(z-B['minZ'])*S
def pathd():
    L,R=curve.edges(); pts=L+R[::-1]
    return "M"+" L".join(f"{X(x):.1f},{Y(z):.1f}" for x,z in pts)+" Z"
def mapsvg(level, uid):
    w=X(B['maxX'])+OX; h=Y(B['maxZ'])+OY
    s=[f'<defs><pattern id="hatch{uid}" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="14" height="14" fill="#A9D46F"/><rect width="6" height="14" fill="#C3E38F"/></pattern>'
       f'<clipPath id="bed{uid}"><rect x="{X(B["minX"])}" y="{Y(B["minZ"])}" width="{(B["maxX"]-B["minX"])*S}" height="{(B["maxZ"]-B["minZ"])*S}" rx="14"/></clipPath></defs>']
    bed=f'<rect x="{X(B["minX"])}" y="{Y(B["minZ"])}" width="{(B["maxX"]-B["minX"])*S}" height="{(B["maxZ"]-B["minZ"])*S}" rx="14"'
    s.append(bed+f' fill="#8FA873" stroke="{INK}" stroke-width="4"/>')
    s.append(f'<g clip-path="url(#bed{uid})">')
    for c in free(level): s.append(f'<polygon points="{hexm(*c)}" fill="#C6E88E" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>')
    if level==1:
        s.append(f'<circle cx="{X(OB['stump'][0])}" cy="{Y(OB['stump'][1])}" r="15" fill="#E9C48A" stroke="{INK}" stroke-width="3.5"/><circle cx="{X(OB['stump'][0])}" cy="{Y(OB['stump'][1])}" r="8" fill="none" stroke="#C49A60" stroke-width="2"/>')
        s.append(f'<path d="M{X(OB['rock'][0]-0.5)},{Y(OB['rock'][1]+0.35)} q-4,-24 22,-26 q24,2 20,26 q-20,8 -42,0 Z" fill="#A7A196" stroke="{INK}" stroke-width="3.5"/>')
        s.append(f'<path d="M{X(OB['puddle'][0]-0.95)},{Y(OB['puddle'][1])} q8,-20 32,-18 q30,0 30,18 q-4,18 -30,18 q-30,0 -32,-18 Z" fill="#7CC4EE" stroke="{INK}" stroke-width="3.5"/>')
        s.append(f'<circle cx="{X(OB['mole'][0])}" cy="{Y(OB['mole'][1])}" r="14" fill="#6B4A2E" stroke="{INK}" stroke-width="3.5"/><circle cx="{X(OB['mole'][0])}" cy="{Y(OB['mole'][1])}" r="5" fill="#5A4A4A"/>')
    if level==2:
        # plantable = bed minus obstacles: draw hatch everywhere, then obstacles on top
        # mug
        s.append(f'<circle cx="{X(4.45)}" cy="{Y(5.3)}" r="30" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/><circle cx="{X(4.45)}" cy="{Y(5.3)}" r="20" fill="#7A4A2A" stroke="{INK}" stroke-width="3"/><path d="M{X(4.45)+30},{Y(5.3)-12} q24,12 0,24" stroke="{INK}" stroke-width="8" fill="none"/>')
        # napkin
        s.append(f'<g transform="rotate(-10 {X(13)} {Y(5)})"><rect x="{X(11.7)}" y="{Y(3.9)}" width="{2.6*S}" height="{2.2*S}" fill="#F6D6E0" stroke="{INK}" stroke-width="4"/><path d="M{X(11.7)},{Y(3.9)} L{X(14.3)},{Y(6.1)}" stroke="#E2A9BB" stroke-width="3"/></g>')
        # salt shaker
        s.append(f'<circle cx="{X(1.1)}" cy="{Y(1.7)}" r="26" fill="#EEF2F5" stroke="{INK}" stroke-width="4"/>'+"".join(f'<circle cx="{X(10.6)+dx}" cy="{Y(1.2)+dy}" r="3" fill="{INK}"/>' for dx,dy in [(-7,-6),(7,-6),(0,4),(-7,10),(7,10)]))
        # milk puddle
        s.append(f'<path d="M{X(7.2)},{Y(4.3)} q30,-30 70,-6 q36,-10 44,24 q16,40 -30,44 q-40,20 -70,-6 q-36,-20 -14,-56 Z" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/>')
        s.append(f'<path d="M{X(7.6)},{Y(7.0)} q22,-24 60,-8 q30,4 26,34 q-8,30 -50,22 q-46,-6 -36,-48 Z" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/>')
    if level==3:
        pass
    s.append('</g>')
    s.append(f'<path d="{pathd()}" fill="#D4A86A" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    mx,my=X(14.4),Y(8.0)
    s.append(f'<path d="M{mx-24},{my} Q{mx},{my-26} {mx+24},{my} Q{mx},{my+24} {mx-24},{my} Z" fill="#E0484F" stroke="{INK}" stroke-width="4"/><path d="M{mx-14},{my-4} L{mx+14},{my-4}" stroke="#FFFFFF" stroke-width="5"/>')
    return f'<svg viewBox="0 0 {w:.0f} {h:.0f}" width="100%" role="img" aria-label="Plánek úrovně {level}" style="display:block">{"".join(s)}</svg>'

cards=[("1. úroveň","Skoro celý záhon","Sází se do šestihranů, jedna zelenina na políčko. Volná jsou skoro všechna, kromě cesty a 4 překážek.",mapsvg(1,"a")),
       ("2. úroveň","Překážky na stole","Hrnek, ubrousek, solnička a kaluže mléka zaberou asi polovinu místa.",mapsvg(2,"b")),
       ("3. úroveň a dál","Jen pár políček","Zbyde jen pár šestihranů u cesty. Každé zasazení je důležité rozhodnutí.",mapsvg(3,"c"))]
card="background:#FFFFFF;border:3px solid #2B2118;border-radius:22px;box-shadow:6px 6px 0 #2B2118"
html=f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>Místo na zeleninu podle úrovní</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&amp;family=Nunito:wght@600;700;800&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#9A5416}}a:hover{{color:#6E3A0E}}
</style>
</helmet>
<div style="width:1920px;height:760px;box-sizing:border-box;padding:48px 56px;background:#FBF6EC;font-family:Nunito,sans-serif;color:{INK};display:flex;flex-direction:column;gap:28px">
<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:32px">
<div style="display:flex;flex-direction:column;gap:6px">
<span style="font-size:16px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#3B7A2A">Fast Food Fight · pravidlo sázení</span>
<h1 style="margin:0;font-family:'Baloo 2',sans-serif;font-size:60px;font-weight:800;line-height:1">Místa na zeleninu ubývá</h1>
</div>
<div style="display:flex;gap:22px;align-items:center;font-weight:800;font-size:17px">
<span style="display:flex;align-items:center;gap:8px"><span style="width:30px;height:22px;border:3px solid {INK};border-radius:6px;background:#C6E88E"></span>sem jde sázet</span>
<span style="display:flex;align-items:center;gap:8px"><span style="width:30px;height:22px;border:3px solid {INK};border-radius:6px;background:#8FA873"></span>sem ne</span>
<span style="display:flex;align-items:center;gap:8px"><span style="width:30px;height:22px;border:3px solid {INK};border-radius:6px;background:#D4A86A"></span>cesta</span>
</div>
</div>
<div style="display:grid;grid-template-columns:repeat(3, minmax(0, 1fr));gap:32px">
'''
for t,sub,d,svg in cards:
    html+=f'''<div style="{card};padding:22px;display:flex;flex-direction:column;gap:12px">
<div style="display:flex;align-items:baseline;gap:12px"><span style="font-family:'Baloo 2',sans-serif;font-size:30px;font-weight:800">{t}</span><span style="font-size:18px;font-weight:800;color:#5A4A3A">{sub}</span></div>
<div style="border-radius:14px;overflow:hidden;background:#D9B98C;padding:6px">{svg}</div>
<p style="margin:0;font-size:17px;font-weight:700;color:#5A4A3A;line-height:1.35">{d}</p>
</div>
'''
html+='''</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{"$preview":{"width":1920,"height":760}}'>
class Component extends DCLogic {
renderVals() {
return {};
}
}
</script>
</body>
</html>
'''
open("/mnt/user-data/outputs/artifacts/0c045be6-49f0-4f56-9475-27d367f93a14/project/MistoNaZeleninu.dc.html","w").write(html); print(len(html))
