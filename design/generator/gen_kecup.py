import math, random
import gen, gen_ff as gf, gen_cibule as gc
from gen import INK, YEL, star, wrap, drop, chip, card
ROOT="/mnt/user-data/outputs/artifacts/0c045be6-49f0-4f56-9475-27d367f93a14/project"
RED="#E0483F"; RED2="#B8323A"; KET="#D92B2B"; CAP="#CFCFCF"
BODYP="M100,196 L200,196 L214,346 Q214,358 202,358 L98,358 Q86,358 86,346 Z"
def cap():
    return (f'<path d="M96,200 Q98,170 128,156 L140,122 L160,122 L172,156 Q202,170 204,200 Z" fill="{CAP}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M116,180 L184,180 M124,168 L176,168" stroke="#A9A9A9" stroke-width="3" stroke-linecap="round"/>'
            f'<rect x="141" y="106" width="18" height="18" rx="3" fill="#8E8E8E" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M200,176 L214,160 Q226,158 224,170 L212,182" fill="{CAP}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
def body(angry=False):
    r=random.Random(3)
    sp="".join(f'<circle cx="{r.uniform(100,200):.0f}" cy="{r.uniform(206,350):.0f}" r="{r.uniform(1,2.2):.1f}" fill="{RED2}" opacity=".7"/>' for _ in range(34))
    s=f'<path d="{BODYP}" fill="{RED}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'+sp
    s+='<path d="M106,214 L100,340" stroke="#FF9A8A" stroke-width="7" stroke-linecap="round" opacity=".8"/>'
    if angry: s+=f'<path d="{BODYP}" fill="#8A0F14" opacity=".25"/>'
    return s
def face(kind="angry"):
    eye=lambda x,y,r=13: f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFFFFF" stroke="{INK}" stroke-width="3.5"/><circle cx="{x}" cy="{y+1}" r="{r*0.6:.1f}" fill="#3A7CC2"/><circle cx="{x}" cy="{y+2}" r="{r*0.26:.1f}" fill="{INK}"/>'
    # a big tomato instead of a nose: bright red, lobed, with a green calyx and a shine
    nose=('<path d="M150,262 C134,258 128,270 130,280 C132,292 142,296 150,295 C158,296 168,292 170,280 C172,270 166,258 150,262 Z" fill="#FF3B22" stroke="#2B2118" stroke-width="4" stroke-linejoin="round"/>'
          '<path d="M141,266 Q138,280 143,292 M159,266 Q162,280 157,292" stroke="#C4220F" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
          '<ellipse cx="141" cy="272" rx="4.5" ry="6" fill="#FFFFFF" opacity=".85"/>'
          '<path d="M150,264 L143,256 L149,259 L150,251 L152,259 L158,255 L153,263 L161,264 L152,266 Z" fill="#3FA34D" stroke="#2B2118" stroke-width="2" stroke-linejoin="round"/>'
          '<path d="M150,252 q1,-6 4,-8" stroke="#2E7D32" stroke-width="3" fill="none" stroke-linecap="round"/>')
    if kind=="angry":
        return f'<path d="M116,214 L142,230 M184,214 L158,230" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'+eye(128,248)+eye(172,248)+nose+f'<path d="M124,298 Q150,318 176,298" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    if kind=="furious":
        return (f'<path d="M112,208 L144,232 M188,208 L156,232" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'+eye(128,250,12)+eye(172,250,12)+nose
                +f'<path d="M122,300 L178,300 L170,316 L130,316 Z" fill="#FFFFFF" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/><path d="M132,300 L132,316 M142,300 L142,316 M152,300 L152,316 M162,300 L162,316" stroke="{INK}" stroke-width="2"/>')
    if kind=="squirt":
        return f'<path d="M116,216 L142,232 M184,216 L158,232" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'+eye(128,250)+eye(172,250)+nose+f'<ellipse cx="150" cy="306" rx="16" ry="12" fill="#5A1220" stroke="{INK}" stroke-width="4"/>'
    if kind=="hit":
        return f'<path d="M116,238 l22,18 M138,238 l-22,18 M162,238 l22,18 M184,238 l-22,18" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'+nose+f'<path d="M132,306 Q150,292 168,306" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    if kind=="scared":
        return (f'<path d="M114,222 Q126,208 142,218 M158,218 Q174,208 186,222" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round"/>'+eye(128,250,16)+eye(172,250,16)+nose
                +f'<ellipse cx="150" cy="306" rx="10" ry="13" fill="#5A1220" stroke="{INK}" stroke-width="4"/>')
def squirt(big=True):
    if not big: return f'<path d="M150,106 q-4,-14 4,-22 q8,10 -4,22 Z" fill="{KET}" stroke="{INK}" stroke-width="3"/>'
    p="M150,106 C130,6 236,-34 272,64"
    return (f'<path d="{p}" stroke="{INK}" stroke-width="26" fill="none" stroke-linecap="round"/><path d="{p}" stroke="{KET}" stroke-width="18" fill="none" stroke-linecap="round"/>'
            f'<path d="M150,90 C140,30 200,-4 236,14" stroke="#FF8A7A" stroke-width="5" fill="none" stroke-linecap="round" opacity=".8"/>'
            +"".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{KET}" stroke="{INK}" stroke-width="2.5"/>' for x,y,r in [(284,92,9),(266,104,6),(296,70,5),(120,40,5),(132,18,4)]))
def puddle(cx,cy,w=1.0,seed=1):
    r=random.Random(seed); pts=[]
    for k in range(18):
        a=k/18*2*math.pi; rr=(1+0.28*math.sin(k*2.3+seed)+r.uniform(-0.12,0.12))
        pts.append(f"{cx+math.cos(a)*60*w*rr:.1f},{cy+math.sin(a)*20*w*rr:.1f}")
    drops="".join(f'<circle cx="{cx+r.uniform(-80,80)*w:.0f}" cy="{cy+r.uniform(-26,26)*w:.0f}" r="{r.uniform(3,6)*w:.1f}" fill="{KET}" stroke="{INK}" stroke-width="1.6"/>' for _ in range(5))
    return (f'<polygon points="{" ".join(pts)}" fill="{KET}" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'
            f'<path d="M{cx-30*w:.0f},{cy-6*w:.0f} q20,-8 40,-2" stroke="#FF9A8A" stroke-width="{4*w:.1f}" fill="none" stroke-linecap="round"/>'+drops)
def kecup(face_="angry", pose="rest", legs_="stand", angry=False, big=False, extra=""):
    l={"stand":gf.leg([(126,358),(122,392),(102,394)])+gf.leg([(176,358),(180,392),(200,392)]),
       "jump":gf.leg([(126,358),(112,378),(122,392)])+gf.leg([(176,358),(190,378),(180,392)]),
       "hop":gf.leg([(126,358),(118,376),(102,372)])+gf.leg([(176,358),(184,380),(200,382)]),
       "run":gf.leg([(126,358),(104,382),(90,374)])+gf.leg([(176,358),(198,386),(216,390)])}[legs_]
    a={"rest":gf.stick_arm(92,236,44,230,INK,5)+gf.stick_arm(208,236,256,230,INK,5),
       "fists":gf.stick_arm(92,240,58,268,INK,5)+gf.stick_arm(208,240,242,268,INK,5),
       "up":gf.stick_arm(92,232,52,184,INK,5)+gf.stick_arm(208,232,248,184,INK,5),
       "down":gf.stick_arm(92,242,58,280,INK,5)+gf.stick_arm(208,242,242,280,INK,5)}[pose]
    return l+body(angry)+cap()+squirt(big)+face(face_)+a+extra
def steam(): return "".join(f'<g opacity=".9">{gf.puff(x,y,s)}</g>' for x,y,s in [(96,96,0.32),(206,88,0.36),(80,62,0.22)])

hero=wrap(gf.blob(60,.22)+kecup(), w=354, h=507, label="Pan Kečup")
walk=wrap(gf.ground(48)+gf.g(kecup(legs_="hop"),"translate(0,-14) rotate(5 150 388)")+f'<path d="M96,404 q-10,-6 -18,0 M208,404 q10,-6 18,0" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round" opacity=".6"/>', label="Pan Kečup jde")
mad=wrap(gf.ground()+kecup("furious","fists",angry=True,extra=steam()+f'<path d="M40,240 l-14,-4 M40,262 l-16,0 M260,240 l14,-4 M260,262 l16,0" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')+gf.txt(186,60,"GRRR!","#B8323A",32,8), vb="0 20 300 410", label="Pan Kečup se naštve")
jump=wrap(gf.path_tile()+'<ellipse cx="150" cy="390" rx="40" ry="9" fill="#3A2210" opacity=".14"/>'+gf.g(kecup("furious","up","jump",angry=True),"translate(0,-60)")+f'<path d="M110,370 l-8,14 M150,374 l0,16 M190,370 l8,14" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'+gf.txt(20,140,"HOP!","#E0483F",34,-10), vb="0 -50 300 480", label="Pan Kečup poskočí")
spray=wrap(gf.path_tile()+puddle(150,396,1.2,2)+puddle(270,382,0.6,5)+gf.g(kecup("squirt","up",big=True),"translate(0,-10)")+gf.txt(196,170,"PRSK!","#D92B2B",36,10), vb="0 -40 330 470", label="Pan Kečup vyprskne kečup")
hit=wrap(gf.ground()+gf.g(kecup("hit","down"),"translate(150,388) scale(1.1,.88) translate(-150,-388)")+star(250,130,16,"#FFFFFF")+gf.txt(30,120,"AU!","#D9342B",38,-10), label="Pan Kečup dostal zásah")
run=wrap(gf.ground()+gf.g(kecup("scared","up","run",extra=gf.sweat(232,190)+gf.sweat(246,220)),"translate(300,0) scale(-1,1) rotate(6 150 388)")+f'<path d="M232,260 l40,0 M236,290 l48,0 M228,320 l40,0" stroke="{INK}" stroke-width="3.5" stroke-linecap="round" opacity=".6"/>', label="Pan Kečup utíká")
dp=wrap(gf.path_tile()+gf.puff(98,320,1.0)+star(40,262,10)+star(150,262,8)+f'<path d="M110,290 Q160,120 240,80" stroke="#3D9BE0" stroke-width="3.5" fill="none" stroke-dasharray="3 10" stroke-linecap="round"/>'
        +gf.water_drop(196,176,2.0)+gf.sparkle(244,136,12)+gf.sparkle(150,130,9)+f'<text x="232" y="62" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="36" fill="#2D8CD6" stroke="{INK}" stroke-width="1.2">+20</text>', label="Kapka vody a puf")

# ability: fast food sliding on ketchup
def slide(svg_, txt_):
    return (f'<rect x="-40" y="330" width="420" height="100" fill="#F4ECD8"/><path d="M-40,330 L380,330" stroke="{INK}" stroke-width="4"/>'
            +puddle(110,388,1.6,3)+puddle(260,392,1.2,8)
            +gf.g(svg_,"translate(186,0) rotate(14 150 388)")
            +f'<path d="M40,250 l90,0 M20,290 l110,0 M50,330 l80,0" stroke="{INK}" stroke-width="5" stroke-linecap="round" opacity=".55"/>'
            +gf.txt(170,96,txt_,"#D92B2B",34,8))
happy_b=gf.burger("angry","up","run").replace(gf.burger_face("angry"),
    f'<path d="M120,176 L132,166 L144,176 M156,176 L168,166 L180,176" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M128,192 Q150,222 172,192 Z" fill="#5A1E14" stroke="{INK}" stroke-width="4"/>')
happy_f=gf.fries("angry","run").replace(gf.fries_face("angry"),
    f'<path d="M124,262 L134,252 L144,262 M156,262 L166,252 L176,262" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M132,286 Q150,314 168,286 Z" fill="#3A1410" stroke="{INK}" stroke-width="3.5"/>')
slide_b=wrap(slide(happy_b,"VÍÍÍ!"), vb="0 40 400 400", label="Hamburger klouže po kečupu")
slide_f=wrap(slide(happy_f,"JUCHŮ!"), vb="0 40 400 400", label="Hranolky kloužou po kečupu")
pud=wrap(f'<rect x="-40" y="120" width="420" height="200" fill="#F4ECD8" stroke="{INK}" stroke-width="4"/>'+puddle(80,220,1.2,1)+puddle(190,206,1.4,4)+puddle(300,224,1.1,7)
         +f'<path d="M20,290 L340,290" stroke="{INK}" stroke-width="4" stroke-dasharray="4 10" opacity=".5"/><text x="180" y="280" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="24" fill="{INK}">~3 políčka cesty</text>', vb="-20 90 400 260", label="Kečupová louže na cestě")

def stage_over():
    s=['<path d="M420,428 C470,412 520,392 560,376" stroke="#D92B2B" stroke-width="40" fill="none" stroke-linecap="round" opacity=".9"/>',
       f'<path d="M420,428 C470,412 520,392 560,376" stroke="{INK}" stroke-width="3" fill="none" stroke-dasharray="6 8" stroke-linecap="round"/>',
       f'<path d="M560,370 l70,-18 m-14,-8 l14,8 l-10,12" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>']
    return "".join(s)
def page(blob):
    psvg=lambda s,h=236: s.replace('<svg ',f'<svg height="{h}" style="max-width:100%" ',1).replace('style="display:block;overflow:visible"','',1)
    small=lambda svgsrc,left,top,w,h: f'<div style="position:absolute;left:{left}%;top:{top}px;width:{w}px;transform:translateX(-50%)">{psvg(svgsrc,h)}</div>'
    stage=(f'<svg viewBox="0 0 800 540" preserveAspectRatio="xMidYMid slice" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%">{gc.stage_svg()}</svg>'
           f'<svg viewBox="0 0 800 540" preserveAspectRatio="xMidYMid slice" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none">{stage_over()}</svg>'
           + small(spray,30,110,240,310) + small(slide_b,66,240,200,190))
    chips="".join(chip(k,v) for k,v in [("Zásahů do útěku","5"),("Rychlost","~1 políčko/s"),("Kečup","1× za 7 s"),("Voda",drop()+"20")])
    poses=[("Chůze","poskakuje, ~1 políčko/s",walk),("Naštvání","zrudne, z víčka mu jde pára",mad),("Poskok","vyskočí do vzduchu",jump),
           ("Vyprsknutí","„Prsk!“ kečup na cestu před sebe",spray),("Zásah","zmáčkne se, „au“",hit),("Útěk","po 5 zásazích se otočí a utíká",run),("Kapka a puf","+20 vody, na okraji mapy puf",dp)]
    parts=[("Lahev","červené tělo",wrap(body(),vb="78 188 144 178",label="Lahev")),
           ("Víčko","se zobáčkem a klapkou",wrap(cap(),vb="88 98 144 108",label="Víčko")),
           ("Obličej","5 výrazů, rajče místo nosu",wrap(face("angry"),vb="108 204 84 120",label="Obličej")),
           ("Ruka","2×, paličková",wrap(gf.stick_arm(208,236,256,230,INK,5),vb="200 216 64 34",label="Ruka")),
           ("Nohy","poskakují",wrap(gf.leg([(126,358),(122,392),(102,394)])+gf.leg([(176,358),(180,392),(200,392)]),vb="94 352 114 48",label="Nohy")),
           ("Prsk kečupu","oblouk z víčka",wrap(squirt(True),vb="130 -42 182 160",label="Prsk kečupu")),
           ("Louže","klouzačka na cestě",wrap(puddle(0,0,1.0,2),vb="-90 -32 180 64",label="Kečupová louže"))]
    h=f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>Pan Kečup – list postavy</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&amp;family=Bangers&amp;family=Nunito:wght@500;700;800&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#B4232D}}a:hover{{color:#8A1A22}}
</style>
</helmet>
<div style="width:1680px;height:1700px;box-sizing:border-box;padding:48px 56px;background:{{{{paper}}}};font-family:Nunito,sans-serif;color:{INK};display:flex;flex-direction:column;gap:32px">
<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:32px">
<div style="display:flex;flex-direction:column;gap:6px">
<span style="font-size:16px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#B4232D">Fast Food Fight · útočník · nový</span>
<h1 style="margin:0;font-family:'Baloo 2',sans-serif;font-size:76px;font-weight:800;line-height:.95">Pan Kečup</h1>
<p style="margin:0;font-size:19px;font-weight:600;color:#5A4A3A;max-width:660px">Jednou za čas se naštve, poskočí a vyprskne spoustu kečupu na cestu. Ostatní fast food po něm klouže a dostane se rychleji k puse. Kečup po chvíli zaschne.</p>
</div>
<div style="display:flex;gap:16px">
{chips}
</div>
</div>
<div style="display:flex;gap:28px;height:540px">
<div style="{card};width:330px;box-sizing:border-box;padding:20px;display:flex;flex-direction:column;gap:12px">
<span style="font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Předloha</span>
<div style="flex:1;border-radius:12px;overflow:hidden;background:#EFE6DA">
<img src="/_blob/{blob}" alt="Dětská kresba: červená lahev kečupu s šedým víčkem, ze kterého stříká kečup" style="width:100%;height:100%;object-fit:contain;display:block">
</div>
<span style="font-size:15px;color:#5A4A3A;font-weight:600">kresby/Kecup.png · popis v „Kečup.md“</span>
</div>
<div style="{card};flex:1;position:relative;overflow:hidden;background:#8BB85A">
{stage}
<span style="position:absolute;top:18px;left:22px;padding:4px 12px;background:rgba(255,255,255,.92);border:3px solid {INK};border-radius:12px;font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Ve hře</span>
<span style="position:absolute;top:22px;right:22px;padding:4px 10px;background:rgba(255,255,255,.92);border:2px solid {INK};border-radius:10px;font-size:14px;font-weight:800;color:#8A1A22">červeně kečup na cestě, šipka k puse</span>
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
        bg="#FDECEC" if t in ("Naštvání","Poskok","Vyprsknutí") else "#FFFFFF"
        h+=f'''<div style="{card};background:{bg};padding:14px 12px 16px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{psvg(s)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:19px;font-weight:800;line-height:1.1">{i+1}. {t}</span>
<span style="font-size:13.5px;font-weight:600;color:#5A4A3A;line-height:1.3">{ds}</span>
</div>
'''
    steps=[("Naštve se","1× za 7 s zrudne a z víčka mu jde pára"),("Poskočí","vyskočí do vzduchu"),("Prsk!","vyprskne kečup na ~3 políčka cesty před sebou"),("Klouzačka","fast food na kečupu jede 2× rychleji, po 5 s kečup zaschne")]
    h+=f'''</div>
</div>
<div style="display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:26px;font-weight:800">Schopnost: kečupová klouzačka</span>
<div style="display:grid;grid-template-columns:repeat(5, minmax(0, 1fr));gap:20px">
<div style="{card};background:#FDECEC;padding:14px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{psvg(pud,180)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Louže na cestě</span>
<span style="font-size:14px;font-weight:600;color:#5A4A3A">kečup pokryje kus cesty před Panem Kečupem</span>
</div>
<div style="{card};background:#FDECEC;padding:14px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{psvg(slide_b,230)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Hamburger klouže</span>
<span style="font-size:14px;font-weight:600;color:#5A4A3A">„Víííí!“ jede 2× rychleji k puse</span>
</div>
<div style="{card};background:#FDECEC;padding:14px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{psvg(slide_f,230)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Hranolky taky</span>
<span style="font-size:14px;font-weight:600;color:#5A4A3A">klouže každý fast food, i Pan Kečup sám</span>
</div>
<div style="{card};grid-column:span 2;padding:22px 24px;display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Jak to funguje</span>
'''
    for i,(t,d) in enumerate(steps):
        h+=f'''<div style="display:flex;align-items:center;gap:14px">
<span style="flex:none;width:44px;height:44px;border-radius:50%;background:#F4A6A0;border:3px solid {INK};display:flex;align-items:center;justify-content:center;font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">{i+1}</span>
<span style="font-size:17px;font-weight:700"><b style="font-family:'Baloo 2',sans-serif;font-size:19px">{t}</b> · {d}</span>
</div>
'''
    h+=f'''<p style="margin:4px 0 0;font-size:14px;font-weight:700;color:#5A4A3A;line-height:1.35">Čísla (5 zásahů, 1× za 7 s, louže ~3 políčka, 2× rychleji, zaschne za 5 s, 20 vody) jsou návrh pro první playtest. Hráč se mu brání tím, že Pana Kečupa odrazí dřív, než doprská.</p>
</div>
</div>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"paper":{{"editor":"color","default":"#FFF3F1"}},"$preview":{{"width":1680,"height":1700}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{ paper: this.props.paper ?? '#FFF3F1' }};
}}
}}
</script>
</body>
</html>
'''
    return h
if __name__=="__main__":
    import sys
    open(f'{ROOT}/Kecup.dc.html','w').write(page(sys.argv[1])); print("ok")
