import math, random
import gen, gen_ff as gf, gen_cibule as gc
from gen import INK, YEL, star, wrap, drop, chip, card
ROOT="/mnt/user-data/outputs/artifacts/0c045be6-49f0-4f56-9475-27d367f93a14/project"
DG="#2E7D32"; DG2="#1B5E20"; LG="#4CAF50"; STALK="#CFE6A8"; ARMG="#7CB342"
CR=[(70,132,44),(98,84,46),(150,64,50),(202,82,46),(232,132,42),(206,168,40),(150,174,46),(94,168,40)]
STALKP="M122,176 L174,176 L190,352 L116,352 Z"

CL=[(76,118,40),(110,72,42),(160,54,44),(208,76,40),(236,124,36),(154,112,46)]
def cluster(cx,cy,R,col=DG,sw=6):
    bumps=[(cx+math.cos(math.radians(a))*R*0.78, cy+math.sin(math.radians(a))*R*0.72, R*0.36) for a in range(0,360,30)]
    a_="".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}" stroke="{INK}" stroke-width="{sw}"/>' for x,y,r in bumps)
    b_="".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}"/>' for x,y,r in bumps)+f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R*0.8:.1f}" fill="{col}"/>'
    return a_,b_
def buds(cx,cy,R,seed,s=1.0):
    r=random.Random(seed); out=[]
    for _ in range(int(14*s+4)):
        a=r.uniform(0,2*math.pi); d=r.uniform(0,R*0.85)
        x,y=cx+math.cos(a)*d, cy+math.sin(a)*d*0.9
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r.uniform(2.2,4.2)*s:.1f}" fill="{r.choice([LG,"#66BB6A",DG2])}"/>')
    for k in range(5):
        a=math.radians(200+k*30); x,y=cx+math.cos(a)*R*0.5, cy+math.sin(a)*R*0.45
        out.append(f'<path d="M{x-R*0.18:.1f},{y:.1f} q{R*0.18:.1f},{-R*0.16:.1f} {R*0.36:.1f},0" stroke="{DG2}" stroke-width="{3*s:.1f}" fill="none" stroke-linecap="round"/>')
    return "".join(out)
def branches(dx=0,dy=0,s=1.0):
    out=[]
    base=(150+dx,186+dy)
    for i,(x,y,R) in enumerate(CL):
        if i==5: continue
        tx,ty=150+(x-150)*s+dx, 120+(y+R*0.5-120)*s+dy
        out.append(f'<path d="M{base[0]:.0f},{base[1]:.0f} Q{(base[0]+tx)/2:.0f},{base[1]-10:.0f} {tx:.0f},{ty:.0f}" stroke="{INK}" stroke-width="{20*s:.1f}" fill="none" stroke-linecap="round"/>'
                   f'<path d="M{base[0]:.0f},{base[1]:.0f} Q{(base[0]+tx)/2:.0f},{base[1]-10:.0f} {tx:.0f},{ty:.0f}" stroke="{STALK}" stroke-width="{12*s:.1f}" fill="none" stroke-linecap="round"/>')
    return "".join(out)
def crown(dx=0,dy=0,s=1.0,tint=None):
    order=[5,0,4,1,3,2]
    A="";B="";T=""
    for i in order:
        x,y,R=CL[i]; cx,cy=150+(x-150)*s+dx,120+(y-120)*s+dy
        a_,b_=cluster(cx,cy,R*s,DG if i!=5 else "#276B2B",6*s)
        A+=a_+b_+buds(cx,cy,R*s,i,s)
    ice=""
    if tint=="ice": ice="".join(f'<circle cx="{150+(x-150)*s+dx:.1f}" cy="{120+(y-120)*s+dy:.1f}" r="{R*s:.1f}" fill="#8FD0F2" opacity=".5"/>' for x,y,R in CL)
    return branches(dx,dy,s)+A+ice
def stalk(tint=None, shine=False):
    r=random.Random(9)
    sp="".join(f'<circle cx="{r.uniform(128,180):.0f}" cy="{r.uniform(190,345):.0f}" r="{r.uniform(1,2.2):.1f}" fill="#9CCC65" opacity=".9"/>' for _ in range(36))
    s=f'<path d="{STALKP}" fill="{STALK}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'+sp+'<path d="M164,180 L178,350 L188,350 L172,180 Z" fill="#B5D98A" opacity=".9"/>'
    if tint=="ice": s+=f'<path d="{STALKP}" fill="#8FD0F2" opacity=".55"/><path d="M130,200 L126,330" stroke="#fff" stroke-width="5" opacity=".85" stroke-linecap="round"/>'
    if shine: s+='<path d="M132,196 L128,334" stroke="#FFFFFF" stroke-width="6" opacity=".9" stroke-linecap="round"/>'
    return s
def face(kind="smile"):
    e=lambda x,y: f'<circle cx="{x}" cy="{y}" r="4.6" fill="{INK}"/>'
    if kind=="smile": return e(140,214)+e(162,212)+f'<path d="M140,230 Q152,248 166,229 Z" fill="#3A1410" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'
    if kind=="closed": return f'<path d="M134,215 Q140,220 146,215 M156,213 Q162,218 168,213" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M144,232 Q152,238 160,231" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/>'
    if kind=="aim": return (f'<path d="M132,204 L146,210 M172,202 L158,208" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/>'+e(141,216)+e(162,214)
                            +f'<path d="M140,232 L166,230" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/><path d="M158,231 q4,8 10,2" fill="#E86A6A" stroke="{INK}" stroke-width="2.5"/>')
    if kind=="frozen": return f'<path d="M134,214 L146,214 M156,212 L168,212" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/><path d="M137,234 l5,-4 l5,4 l5,-4 l5,4 l5,-4" stroke="{INK}" stroke-width="3.5" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
    if kind=="joy": return f'<path d="M134,217 L140,208 L146,217 M156,215 L162,206 L168,215" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M138,226 Q152,254 168,225 Z" fill="#8A2B1E" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
def arm(x1,y1,x2,y2):
    dx,dy=x2-x1,y2-y1; L=math.hypot(dx,dy); px,py=-dy/L*15,dx/L*15; tx,ty=x2-dx/L*10,y2-dy/L*10
    return (f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{INK}" stroke-width="11" stroke-linecap="round"/><path d="M{x1},{y1} L{x2},{y2}" stroke="{ARMG}" stroke-width="6" stroke-linecap="round"/>'
            f'<path d="M{tx-px:.1f},{ty-py:.1f} L{tx+px:.1f},{ty+py:.1f}" stroke="{INK}" stroke-width="12" stroke-linecap="round"/><path d="M{tx-px:.1f},{ty-py:.1f} L{tx+px:.1f},{ty+py:.1f}" stroke="{ARMG}" stroke-width="7" stroke-linecap="round"/>')
def legs():
    return (f'<path d="M140,352 L136,386 q-14,8 -22,-2" stroke="#5E5A55" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M168,352 L174,386 L194,386" stroke="#5E5A55" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
def floret(x,y,s=1.0,rot=0):
    st=(f'<path d="M0,26 L0,6 M0,10 L-11,-2 M0,10 L11,-2" stroke="{INK}" stroke-width="10" fill="none" stroke-linecap="round"/>'
        f'<path d="M0,26 L0,6 M0,10 L-11,-2 M0,10 L11,-2" stroke="{STALK}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    heads=""
    for cx,cy,R in [(-13,-8,11),(13,-8,11),(0,-16,13)]:
        a_,b_=cluster(cx,cy,R,DG,3.5); heads+=a_+b_+buds(cx,cy,R,int(cx+cy+40),0.45)
    return f'<g transform="translate({x},{y}) rotate({rot}) scale({s})">{st}{heads}</g>'
def rocket(x,y,rot=0,s=1.0):
    # floret flying like a ballistic rocket: nose first, puffy green trail behind
    trail="".join(f'<circle cx="{-26-i*16}" cy="0" r="{9-i*2}" fill="#C5E1A5" stroke="{INK}" stroke-width="2.5" opacity="{0.9-i*0.2:.1f}"/>' for i in range(4))
    lines=f'<path d="M-30,-12 l-30,-4 M-30,12 l-30,4" stroke="{INK}" stroke-width="3" stroke-linecap="round" opacity=".55"/>'
    return f'<g transform="translate({x},{y}) rotate({rot}) scale({s})">{trail}{lines}{floret(0,0,1.0,90)}</g>'
def burst(cx,cy,s=1.0):
    # bursts downward in the shape of an umbrella: a canopy on top, ribs fanning down, small florets at the tips
    out=[f'<path d="M{cx-92*s:.0f},{cy+22*s:.0f} Q{cx:.0f},{cy-70*s:.0f} {cx+92*s:.0f},{cy+22*s:.0f}" fill="#A5D67A" fill-opacity=".35" stroke="{INK}" stroke-width="{4*s:.1f}" stroke-dasharray="6 8"/>',
         star(cx,cy,26*s,"#FFF4D6")]
    for k in range(7):
        t=k/6; ex=cx+(-92+184*t)*s; ey=cy+(70+34*math.sin(t*math.pi))*s
        out.append(f'<path d="M{cx:.0f},{cy:.0f} Q{cx+(-92+184*t)*0.75*s:.0f},{cy+4*s:.0f} {ex:.0f},{ey-18*s:.0f}" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round" stroke-dasharray="2 6"/>')
        out.append(floret(ex,ey,0.5*s,180+(-40+80*t)))
    return "".join(out)
def broc(face_="smile", pose="rest", tint=None, shine=False, back="", front=""):
    if pose=="rest": a=arm(122,262,70,270)+arm(178,258,232,246)
    elif pose=="pluck": a=arm(122,262,72,276)+arm(178,252,214,164)+floret(220,150,1.0,-10)
    elif pose=="throw": a=arm(122,262,72,276)+arm(178,252,240,214)
    elif pose=="up": a=arm(122,256,82,200)+arm(178,252,222,196)
    return back+legs()+stalk(tint,shine)+crown(tint=tint)+face(face_)+a+front

ground=lambda: gen.tile()+'<ellipse cx="155" cy="390" rx="62" ry="12" fill="#3A2210" opacity=".18"/>'
hero=wrap(ground()+broc(), w=354, h=507, label="Pan Brokolice")
grow_inner=(gen.tile().replace('364','214').replace('378','228').replace('394','244').replace('412','262').replace('422','272')
    +'<ellipse cx="155" cy="238" rx="64" ry="15" fill="#3A2210" stroke="#2B2118" stroke-width="4"/>'
    +'<defs><clipPath id="bclip"><path d="M0,-60 L300,-60 L300,238 L219,238 A64,15 0 0 1 91,238 L0,238 Z"/></clipPath></defs>'
    '<g clip-path="url(#bclip)"><g transform="translate(5,58)">'+stalk()+crown()+face("closed")+'</g></g>'
    +f'<path d="M91,238 A64,15 0 0 0 219,238" stroke="{INK}" stroke-width="4" fill="none"/>'
    +f'<path d="M50,190 l-14,-8 M258,186 l14,-9" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>')
grow=wrap(grow_inner, vb="0 -10 300 300", label="Pan Brokolice vyrůstá")
idle=wrap(ground()+'<g transform="rotate(-2 150 380)">'+broc()+'</g>', label="Pan Brokolice v klidu")
pluck=wrap(ground()+broc("aim","pluck",front=f'<path d="M236,120 l10,-12 M248,140 l14,-4" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>'), vb="0 0 300 430", label="Pan Brokolice si utrhne růžičku")
throw_fx=(f'<path d="M244,206 Q330,10 420,170" stroke="{INK}" stroke-width="3.5" fill="none" stroke-dasharray="3 11" stroke-linecap="round"/>'
          +rocket(326,64,-28,0.9)
          +gf.txt(232,300,"ŠVUNG!","#4CAF50",32,-8))
throw=wrap(ground()+broc("aim","throw",front=throw_fx), vb="0 0 430 430", label="Pan Brokolice hází růžičku")
fry=f'<g transform="translate(176,282) rotate(-30)"><rect x="-6" y="-34" width="12" height="54" rx="3" fill="#FFD25A" stroke="{INK}" stroke-width="3.5"/></g>'
frozen=wrap(ground()+broc("frozen",tint="ice",front=fry+gen.ice_bits), label="Pan Brokolice ztuhl")
joy=wrap(ground().replace('rx="62"','rx="42"')+'<g transform="translate(0,-24)">'+broc("joy","up",front=star(36,250,14)+star(272,240,13)+star(30,330,10)+star(276,320,12))+'</g>', vb="0 -10 300 440", label="Pan Brokolice se raduje")
badge=star(262,52,30)+f'<text x="262" y="62" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="28" fill="{INK}">2</text>'
glow=f'<path d="{STALKP}" fill="none" stroke="#FFD447" stroke-width="22" stroke-linejoin="round" opacity=".7"/>'+"".join(f'<circle cx="{x}" cy="{y}" r="{r+8}" fill="#FFD447" opacity=".45"/>' for x,y,r in CL)
lvl2=wrap(ground()+broc("smile",shine=True,back=glow,front=badge), vb="-10 0 320 430", label="Pan Brokolice úroveň 2")

parts=[("Korunka","růžičky na větvičkách",wrap(crown(),vb="20 0 270 210",label="Korunka")),
       ("Košťál","tělo, světle zelený",wrap(stalk(),vb="108 170 90 190",label="Košťál")),
       ("Obličej","5 výrazů",wrap(face("smile"),vb="128 200 52 54",label="Obličej")),
       ("Ruka","2×, zelená s dlaní",wrap(arm(178,258,232,246),vb="170 226 76 46",label="Ruka")),
       ("Nohy","šedé, zatočené",wrap(legs(),vb="104 346 96 50",label="Nohy")),
       ("Růžička","střela",wrap(floret(0,0,1.4),vb="-34 -46 68 86",label="Růžička")),
       ("Deštník","rozprsk dolů",wrap(burst(0,0,0.8),vb="-84 -50 168 140",label="Roztříštění do deštníku"))]
poses=[("Vyrůstání","5 s, nejdřív vykoukne korunka",grow),("Klid","pohupuje korunkou",idle),
       ("Nápřah","utrhne si z korunky růžičku",pluck),("Výstřel","letí jako raketa vysokým obloukem, 1× za 2,5 s",throw),
       ("Ztuhnutí","po zásahu hranolkou 2 s modrý",frozen),("Radost","výskok, když fast food uteče",joy),
       ("Úroveň 2","větší roztříštění",lvl2)]

# ability cards
def mini_ff(svgsrc,x,y,s): return f'<g transform="translate({x},{y}) scale({s}) translate(-150,-388)">{svgsrc}</g>'
hb_hit=gf.burger("hit","down"); fr_hit=gf.fries("hit","hit")
air=wrap(f'<rect x="-40" y="300" width="380" height="140" fill="#F4ECD8"/><path d="M-40,300 L340,300" stroke="{INK}" stroke-width="4"/>'
         +f'<path d="M-10,250 Q60,30 150,110" stroke="{INK}" stroke-width="3.5" fill="none" stroke-dasharray="3 11" stroke-linecap="round"/>'
         +rocket(70,150,-50,0.8)+burst(150,120,1.25)+gf.txt(196,66,"BUM!","#4CAF50",42,8)
         +"", vb="-30 20 360 400", label="Růžička se ve vzduchu roztříští")
multi=wrap(f'<ellipse cx="150" cy="376" rx="160" ry="44" fill="#4CAF50" fill-opacity=".12" stroke="#2E7D32" stroke-width="4" stroke-dasharray="12 9"/>'
           +mini_ff(hb_hit,60,380,0.55)+mini_ff(fr_hit,150,396,0.55)+mini_ff(hb_hit,240,382,0.55)
           +burst(150,120,1.15)
           +gf.txt(18,110,"AU!","#D9342B",30,-10)+gf.txt(226,100,"AU!","#D9342B",30,8)+star(150,110,14,"#FFFFFF"), vb="-30 40 360 400", label="Zásah víc útočníků naráz")

def stage_over():
    s=['<ellipse cx="180" cy="230" rx="560" ry="330" fill="none" stroke="#2D8CD6" stroke-width="4" stroke-dasharray="14 10" opacity=".7"/>',
       f'<path d="M210,180 Q420,-60 600,240" stroke="{INK}" stroke-width="4" fill="none" stroke-dasharray="3 12" stroke-linecap="round"/>',rocket(470,70,30,0.8),
       '<ellipse cx="600" cy="350" rx="110" ry="46" fill="#4CAF50" fill-opacity=".14" stroke="#2E7D32" stroke-width="4" stroke-dasharray="12 9"/>',
       burst(600,240,1.0)]
    return "".join(s)

def page():
    psvg=lambda s,h=236: s.replace('<svg ',f'<svg height="{h}" style="max-width:100%" ',1).replace('style="display:block;overflow:visible"','',1)
    small=lambda svgsrc,left,top,w,h: f'<div style="position:absolute;left:{left}%;top:{top}px;width:{w}px;transform:translateX(-50%)">{psvg(svgsrc,h)}</div>'
    ff=lambda svg_: wrap(gf.blob(56,.2)+svg_, label="")
    stage=(f'<svg viewBox="0 0 800 540" preserveAspectRatio="xMidYMid slice" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%">{gc.stage_svg()}</svg>'
           + small(hero,24,30,220,280)
           + small(ff(gf.burger("hit","down")),66,300,110,150)+small(ff(gf.fries("hit","hit")),76,280,110,150)+small(ff(gf.burger("hit","down")),86,262,110,150)
           + f'<svg viewBox="0 0 800 540" preserveAspectRatio="xMidYMid slice" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none">{stage_over()}</svg>')
    chips="".join(chip(k,v) for k,v in [("Cena",drop()+"80"),("Růst","5 s"),("Dosah","~5 políček"),("Výstřel","1× za 2,5 s")])
    h=f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>Pan Brokolice – list postavy</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&amp;family=Bangers&amp;family=Nunito:wght@500;700;800&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#2E7D32}}a:hover{{color:#1B5E20}}
</style>
</helmet>
<div style="width:1680px;height:1700px;box-sizing:border-box;padding:48px 56px;background:{{{{paper}}}};font-family:Nunito,sans-serif;color:{INK};display:flex;flex-direction:column;gap:32px">
<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:32px">
<div style="display:flex;flex-direction:column;gap:6px">
<span style="font-size:16px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#2E7D32">Fast Food Fight · obránce · nový</span>
<h1 style="margin:0;font-family:'Baloo 2',sans-serif;font-size:76px;font-weight:800;line-height:.95">Pan Brokolice</h1>
<p style="margin:0;font-size:19px;font-weight:600;color:#5A4A3A;max-width:660px">Má velký dostřel. Utrhne si z korunky růžičku a vystřelí ji jako raketu vysokým obloukem. Nad cílem se rozprskne dolů do tvaru deštníku a drobné růžičky zasáhnou víc útočníků naráz.</p>
</div>
<div style="display:flex;gap:16px">
{chips}
</div>
</div>
<div style="display:flex;gap:28px;height:540px">
<div style="{card};width:330px;box-sizing:border-box;padding:20px;display:flex;flex-direction:column;gap:12px">
<span style="font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Předloha</span>
<div style="flex:1;border-radius:12px;overflow:hidden;background:#EFE6DA">
<img src="/_blob/BLOBID" alt="Dětská kresba: brokolice s velkou zelenou korunkou, rukama a nohama" style="width:100%;height:100%;object-fit:contain;display:block">
</div>
<span style="font-size:15px;color:#5A4A3A;font-weight:600">kresby/obranci/brokolice.png · popis v „Pan Brokolice.md“</span>
</div>
<div style="{card};flex:1;position:relative;overflow:hidden;background:#8BB85A">
{stage}
<span style="position:absolute;top:18px;left:22px;padding:4px 12px;background:rgba(255,255,255,.92);border:3px solid {INK};border-radius:12px;font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Ve hře</span>
<span style="position:absolute;top:22px;right:22px;padding:4px 10px;background:rgba(255,255,255,.92);border:2px solid {INK};border-radius:10px;font-size:14px;font-weight:800;color:#1B5E20">modře dosah, zeleně kam dopadne deštník</span>
</div>
<div style="{card};width:440px;box-sizing:border-box;padding:20px;display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Díly loutky</span>
<div style="display:grid;grid-template-columns:repeat(3, minmax(0, 1fr));gap:10px;flex:1">
'''
    for t,ds,s in parts:
        h+=f'''<div style="border:2px dashed #BFAE98;border-radius:14px;padding:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px">
<div style="height:70px;width:100%;display:flex;align-items:center;justify-content:center">{psvg(s,64)}</div>
<span style="font-weight:800;font-size:15px;text-align:center">{t}</span>
<span style="font-size:12px;color:#5A4A3A;font-weight:600;text-align:center;line-height:1.25">{ds}</span>
</div>
'''
    h+=f'''</div>
</div>
</div>
<div style="display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:26px;font-weight:800">Stavy a animace</span>
<div style="display:grid;grid-template-columns:repeat(7, minmax(0, 1fr));gap:18px">
'''
    for i,(t,ds,s) in enumerate(poses):
        bg="#E7F4FB" if t=="Ztuhnutí" else ("#FFF4D6" if t=="Úroveň 2" else ("#EAF5E1" if t in ("Nápřah","Výstřel") else "#FFFFFF"))
        h+=f'''<div style="{card};background:{bg};padding:14px 12px 16px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{psvg(s)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:19px;font-weight:800;line-height:1.1">{i+1}. {t}</span>
<span style="font-size:13.5px;font-weight:600;color:#5A4A3A;line-height:1.3">{ds}</span>
</div>
'''
    steps=[("Utrhne","si z korunky růžičku (korunka hned doroste)"),("Vystřelí","jako raketu, vysokým obloukem až ~5 políček daleko"),("Bum!","nad cílem se rozprskne dolů jako deštník"),("Zásah","drobné růžičky zasáhnou všechny do ~1 políčka")]
    h+=f'''</div>
</div>
<div style="display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:26px;font-weight:800">Schopnost: brokolicová raketa</span>
<div style="display:grid;grid-template-columns:repeat(4, minmax(0, 1fr));gap:20px">
<div style="{card};background:#EAF5E1;padding:14px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{psvg(air,250)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Rozprsk jako deštník</span>
<span style="font-size:14px;font-weight:600;color:#5A4A3A">„Bum!“ a malé růžičky letí šikmo dolů</span>
</div>
<div style="{card};background:#EAF5E1;padding:14px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{psvg(multi,250)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Víc útočníků naráz</span>
<span style="font-size:14px;font-weight:600;color:#5A4A3A">každý v zeleném kruhu dostane jeden zásah</span>
</div>
<div style="{card};grid-column:span 2;padding:22px 24px;display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Jak to funguje</span>
'''
    for i,(t,d) in enumerate(steps):
        h+=f'''<div style="display:flex;align-items:center;gap:14px">
<span style="flex:none;width:44px;height:44px;border-radius:50%;background:#A5D67A;border:3px solid {INK};display:flex;align-items:center;justify-content:center;font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">{i+1}</span>
<span style="font-size:17px;font-weight:700"><b style="font-family:'Baloo 2',sans-serif;font-size:19px">{t}</b> · {d}</span>
</div>
'''
    h+=f'''<p style="margin:4px 0 0;font-size:14px;font-weight:700;color:#5A4A3A;line-height:1.35">Čísla (cena 80, růst 5 s, dosah ~5 políček, 1 hod za 2,5 s, roztříštění ~1 políčko) jsou návrh pro první playtest. Nejdražší a nejpomalejší obránce, ale nejdál dostřelí a trefí víc fast foodu najednou.</p>
</div>
</div>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"paper":{{"editor":"color","default":"#F1F8EC"}},"$preview":{{"width":1680,"height":1700}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{ paper: this.props.paper ?? '#F1F8EC' }};
}}
}}
</script>
</body>
</html>
'''
    return h
if __name__=="__main__":
    import sys
    open(f'{ROOT}/Brokolice.dc.html','w').write(page().replace("BLOBID",sys.argv[1])); print("ok")
