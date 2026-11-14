import math, random
import gen, gen_ff as gf
from gen import INK, YEL, star, wrap, drop, chip, card
ROOT="/mnt/user-data/outputs/artifacts/0c045be6-49f0-4f56-9475-27d367f93a14/project"
SKIN="#EFDDB2"; SKIN2="#E2C58E"; LINE="#6B5A4A"; G1="#3FA34D"; G2="#2E7D32"; STINK="#8BC34A"
BODY="M150,118 C186,150 246,214 240,290 C236,346 200,364 150,366 C100,364 64,346 60,290 C54,214 114,150 150,118 Z"

def sprouts(straight=False):
    r=random.Random(3); s=[]
    for i in range(9):
        a=math.radians((-55+i*12) if not straight else (-22+i*5.5)); L=r.uniform(70,96)*(1.12 if straight else 1)
        ex=150+math.sin(a)*L; ey=112-math.cos(a)*L
        s.append(f'<path d="M150,112 Q{150+math.sin(a)*L*0.45+r.uniform(-6,6):.1f},{112-math.cos(a)*L*0.5:.1f} {ex:.1f},{ey:.1f}" stroke="{G1 if i%2 else "#5DB85A"}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    s.append(f'<circle cx="150" cy="116" r="10" fill="{G2}" stroke="{INK}" stroke-width="3"/>')
    return "".join(s)
def body(tint=None, shine=False, spikes=False):
    s=[]
    if spikes:
        pts=[]
        for k in range(15):
            t=k/14; a=math.radians(-200+t*220)
            pts.append(a)
        for k in range(16):
            ang=math.radians(-90-115+k*(230/15))
            cx,cy=150+math.cos(ang)*96, 262+math.sin(ang)*110
            ox,oy=math.cos(ang)*30, math.sin(ang)*30
            px,py=-math.sin(ang)*13, math.cos(ang)*13
            s.append(f'<path d="M{cx-px:.1f},{cy-py:.1f} L{cx+ox:.1f},{cy+oy:.1f} L{cx+px:.1f},{cy+py:.1f} Z" fill="{SKIN2}" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')
    s.append(f'<path d="{BODY}" fill="{SKIN}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    s.append('<path d="M196,170 C232,214 238,262 232,300 C226,340 196,358 166,362 C200,330 214,250 196,170 Z" fill="#E2C58E" opacity=".75"/>')
    for t in [-0.78,-0.5,-0.22,0.06,0.34,0.62]:
        s.append(f'<path d="M150,124 Q{150+t*110:.1f},{236:.1f} {150+t*78:.1f},{360-abs(t)*22:.1f}" stroke="{LINE}" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
    r=random.Random(5)
    s.append("".join(f'<path d="M{r.uniform(80,220):.0f},{r.uniform(200,340):.0f} l{r.uniform(-4,4):.0f},8" stroke="#CDB07A" stroke-width="2" stroke-linecap="round"/>' for _ in range(26)))
    if tint=="ice":
        s.append(f'<path d="{BODY}" fill="#8FD0F2" opacity=".55"/><path d="M96,220 Q90,280 112,330" stroke="#fff" stroke-width="6" opacity=".85" fill="none" stroke-linecap="round"/>')
    if shine:
        s.append('<path d="M98,214 Q88,270 108,326" stroke="#FFFFFF" stroke-width="7" fill="none" opacity=".9" stroke-linecap="round"/>')
    return "".join(s)
def roots(): return "".join(f'<path d="M{142+i*4},364 q{(-1)**i*4},6 {(-1)**i*3},12" stroke="#B9A27A" stroke-width="2" fill="none" stroke-linecap="round"/>' for i in range(5))
def face(kind="smile"):
    e=lambda x,y: f'<circle cx="{x}" cy="{y}" r="4.6" fill="{INK}"/>'
    if kind=="smile": return e(138,236)+e(164,234)+f'<path d="M136,252 Q151,266 168,250" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
    if kind=="closed": return f'<path d="M131,237 Q138,242 145,237 M157,235 Q164,240 171,235" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M143,253 Q151,259 160,252" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/>'
    if kind=="bristle": return (f'<path d="M128,222 L146,230 M174,220 L156,228" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'+e(139,238)+e(163,236)
                                +f'<ellipse cx="151" cy="258" rx="12" ry="7" fill="#5A1E14" stroke="{INK}" stroke-width="3.5"/><ellipse cx="118" cy="252" rx="12" ry="8" fill="#F4A6A0" opacity=".9"/><ellipse cx="186" cy="250" rx="12" ry="8" fill="#F4A6A0" opacity=".9"/>')
    if kind=="puff": return (f'<path d="M131,236 L144,240 M171,234 L158,238" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/>'
                             +f'<path d="M138,254 Q151,248 164,254 Q151,262 138,254 Z" fill="#5A1E14" stroke="{INK}" stroke-width="3"/>')
    if kind=="frozen": return f'<path d="M132,236 L146,236 M157,234 L171,234" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/><path d="M135,256 l6,-5 l6,5 l6,-5 l6,5 l6,-5" stroke="{INK}" stroke-width="3.5" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
    if kind=="joy": return f'<path d="M131,240 L138,231 L145,240 M157,238 L164,229 L171,238" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M134,250 Q151,278 170,249 Z" fill="#8A2B1E" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
def arm(x1,y1,x2,y2): return gf.stick_arm(x1,y1,x2,y2,"#3A3530",5)
def legs(): return roots()+gf.leg([(134,362),(130,390),(110,392)])+gf.leg([(168,362),(174,390),(194,391)])
def squiggle(x,y,w=46,rot=0,c=STINK,sw=4):
    return f'<path d="M{x},{y} q{w/6:.1f},-10 {w/3:.1f},0 t{w/3:.1f},0 t{w/3:.1f},0" stroke="{c}" stroke-width="{sw}" fill="none" stroke-linecap="round" transform="rotate({rot} {x} {y})"/>'
def stink_lines(n=6,seed=1,spread=1.0):
    r=random.Random(seed); out=[]
    for i in range(n):
        a=math.radians(-160+i*(320/max(1,n-1))); R=r.uniform(140,170)*spread
        out.append(squiggle(150+math.cos(a)*R-20,260+math.sin(a)*R*0.9,r.uniform(36,52),r.uniform(-25,25)))
    return "".join(out)
def onion(face_="smile", pose="rest", tint=None, shine=False, spikes=False, straight=False, front="", back=""):
    if pose=="rest": a=arm(70,268,26,252)+arm(230,258,262,206)
    elif pose=="up": a=arm(72,252,34,196)+arm(228,250,266,194)
    elif pose=="clench": a=arm(70,270,34,292)+arm(230,270,266,292)
    return back+legs()+sprouts(straight)+body(tint,shine,spikes)+face(face_)+a+front
def cloud(cx,cy,s=1.0,op=.78):
    cs=[(-60,10,40),(-24,-16,46),(26,-18,44),(62,8,38),(-34,26,36),(10,30,40),(46,30,30)]
    a="".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#B5DD7A" stroke="{INK}" stroke-width="7"/>' for x,y,r in cs)
    b="".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#B5DD7A"/>' for x,y,r in cs)
    hl='<path d="M-40,-4 q10,-12 22,-4 M14,-26 q12,-10 24,0" stroke="#DDF2B5" stroke-width="6" fill="none" stroke-linecap="round"/>'
    return f'<g transform="translate({cx},{cy}) scale({s})" opacity="{op}">{a}{b}{hl}</g>'
def fly(x,y): return f'<g transform="translate({x},{y})"><ellipse cx="-5" cy="-6" rx="6" ry="4" fill="#FFFFFF" fill-opacity=".85" stroke="{INK}" stroke-width="1.6"/><ellipse cx="5" cy="-6" rx="6" ry="4" fill="#FFFFFF" fill-opacity=".85" stroke="{INK}" stroke-width="1.6"/><circle r="5" fill="{INK}"/></g>'
def ground(): return gen.tile()+'<ellipse cx="150" cy="390" rx="62" ry="12" fill="#3A2210" opacity=".18"/>'
def snail_icon(x,y,s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})"><path d="M-22,10 L18,10 q8,-2 8,-12 l3,-10 M24,-2 l8,-9" stroke="{INK}" stroke-width="3" fill="#E9D3A8" stroke-linecap="round"/>'
            f'<circle cx="-4" cy="-4" r="14" fill="#C98A4A" stroke="{INK}" stroke-width="3.5"/><path d="M-4,-4 m-6,0 a6,6 0 1,1 6,6" stroke="{INK}" stroke-width="2.5" fill="none"/></g>')
# --- fast food reacting to the stink
def sneeze_face_burger():
    return (f'<path d="M118,170 l16,8 l-16,8 M182,170 l-16,8 l16,8" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="150" cy="192" r="4" fill="{INK}"/><ellipse cx="150" cy="210" rx="16" ry="11" fill="#5A1E14" stroke="{INK}" stroke-width="4"/>'
            +"".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#9AD4F5" stroke="{INK}" stroke-width="2"/>' for x,y,r in [(126,232,5),(112,222,4),(178,232,5),(192,220,4),(150,240,4)]))
def choke_face_fries():
    return (f'<path d="M122,256 l16,8 l-16,8 M178,256 l-16,8 l16,8" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="150" cy="282" r="3.2" fill="{INK}"/><path d="M136,298 Q150,292 164,298 L160,306 Q150,302 140,306 Z" fill="#3A1410" stroke="{INK}" stroke-width="3"/><path d="M146,304 q4,14 12,4" fill="#F07A86" stroke="{INK}" stroke-width="2.5"/>')
burger_src=gf.burger("angry","flail","stand")
burger_sneeze=burger_src.replace(gf.burger_face("angry"),sneeze_face_burger())
fries_src=gf.fries("angry","run")
fries_choke=fries_src.replace(gf.fries_face("angry"),choke_face_fries())
green_wash=lambda: '<rect x="40" y="90" width="220" height="300" fill="#8BC34A" opacity=".0"/>'

# ---------- pieces
hero=wrap(ground()+onion("smile",front=stink_lines(5,2,0.95)), w=354, h=507, label="Pan Cibule")
grow_inner=(gen.tile().replace('364','214').replace('378','228').replace('394','244').replace('412','262').replace('422','272')
    +'<ellipse cx="155" cy="238" rx="60" ry="15" fill="#3A2210" stroke="#2B2118" stroke-width="4"/>'
    +'<defs><clipPath id="cclip"><path d="M0,-60 L300,-60 L300,238 L215,238 A60,15 0 0 1 95,238 L0,238 Z"/></clipPath></defs>'
    '<g clip-path="url(#cclip)"><g transform="translate(5,70)">'+sprouts()+body()+face("closed")+'</g></g>'
    +f'<path d="M95,238 A60,15 0 0 0 215,238" stroke="{INK}" stroke-width="4" fill="none"/>'
    +f'<path d="M58,190 l-14,-8 M252,186 l14,-9 M62,150 l-12,-2 M248,148 l12,-3" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>')
grow=wrap(grow_inner, vb="0 -30 300 320", label="Pan Cibule vyrůstá")
idle=wrap(ground()+'<g transform="rotate(-2 150 380)">'+onion("smile",front=squiggle(232,300,40,-10)+squiggle(40,320,36,15))+'</g>', label="Pan Cibule v klidu")
shake=f'<path d="M22,250 l-12,4 M22,270 l-14,0 M22,290 l-12,-4 M278,250 l12,4 M278,270 l14,0 M278,290 l12,-4" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
bristle=wrap(ground()+onion("bristle","clench",spikes=True,straight=True,front=shake), vb="-10 0 320 430", label="Pan Cibule se naježí")
burst=(cloud(150,330,1.55,.82)+stink_lines(8,4,1.15)+fly(52,150)+fly(262,170)+gf.txt(176,104,"PŠŠŠ!","#8BC34A",38,8))
puffc=wrap(ground()+onion("puff","up",back="")+burst, vb="-20 0 340 430", label="Oblak smradu")
fry=f'<g transform="translate(176,282) rotate(-30)"><rect x="-6" y="-34" width="12" height="54" rx="3" fill="#FFD25A" stroke="{INK}" stroke-width="3.5"/></g>'
frozen=wrap(ground()+onion("frozen",tint="ice",front=fry+gen.ice_bits), label="Pan Cibule ztuhl")
joy=wrap(ground().replace('rx="62"','rx="42"')+'<g transform="translate(0,-24)">'+onion("joy","up",front=star(40,150,16)+star(268,124,13)+star(36,280,10)+star(272,290,14))+'</g>', vb="0 -10 300 440", label="Pan Cibule se raduje")
badge=star(254,96,30)+f'<text x="254" y="106" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="28" fill="{INK}">2</text>'
glow=f'<path d="{BODY}" fill="none" stroke="#FFD447" stroke-width="22" stroke-linejoin="round" opacity=".7"/>'
lvl2=wrap(ground()+onion("smile",shine=True,back=glow,front=stink_lines(8,6,1.05)+badge), vb="-10 0 320 430", label="Pan Cibule úroveň 2")

parts=[("Nať","9 stébel, při naježení se postaví",wrap(sprouts(),vb="60 18 180 112",label="Nať")),
       ("Tělo","cibule se slupkami",wrap(body(),vb="50 108 200 266",label="Tělo")),
       ("Obličej","5 výrazů",wrap(face("smile"),vb="124 222 56 46",label="Obličej")),
       ("Ruka","2×, jedna mává",wrap(arm(230,258,262,206),vb="222 194 52 72",label="Ruka")),
       ("Nohy","s kořínky",wrap(legs(),vb="102 356 100 42",label="Nohy")),
       ("Slupky","naježení: odstávají",wrap(body(spikes=True),vb="20 110 260 300",label="Naježené slupky")),
       ("Oblak smradu","zelený mrak + vlnky",wrap(cloud(0,0,1.0,1.0)+squiggle(-70,-56,40,-10)+squiggle(40,-60,40,12),vb="-112 -90 224 160",label="Oblak smradu"))]
poses=[("Vyrůstání","4 s, nejdřív vykoukne nať",grow),("Klid","pohupuje se, kolem trochu voní",idle),
       ("Naježení","1× za 6 s: slupky odstávají, třese se",bristle),("Oblak smradu","„Pšššš!“ zelený mrak kolem cibule",puffc),
       ("Ztuhnutí","po zásahu hranolkou 2 s modrý",frozen),("Radost","výskok, když fast food uteče",joy),
       ("Úroveň 2","větší oblak, zpomalení déle",lvl2)]

# ability cards: fast food in the cloud
fx_burger=wrap(gf.ground()+cloud(150,300,1.45,.55)+gf.g(burger_sneeze,"rotate(-8 150 388)")
               +gf.txt(176,96,"HAPČÍ!","#8BC34A",40,10)+snail_icon(70,120,1.3)+f'<text x="70" y="170" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="26" fill="{INK}">× ½</text>'
               +squiggle(220,240,40,-14)+squiggle(40,280,36,10), vb="0 30 300 400", label="Hamburger kýchá ve smradu")
fx_fries=wrap(gf.ground()+cloud(150,310,1.45,.55)+gf.g(fries_choke,"translate(0,-6)")
              +gf.txt(166,104,"KCH KCH!","#8BC34A",34,8)+snail_icon(64,128,1.3)+f'<text x="64" y="178" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="26" fill="{INK}">× ½</text>'
              +squiggle(232,236,40,-14)+squiggle(36,300,36,10), vb="0 30 300 400", label="Hranolky se dusí ve smradu")

# stage: top-down field with hex plots, path and the cloud ring
def stage_svg():
    W_,H_=800,540
    s=[f'<rect width="{W_}" height="{H_}" fill="#8BB85A"/>']
    r=random.Random(7)
    for _ in range(90):
        x,y=r.uniform(0,W_),r.uniform(0,H_); s.append(f'<path d="M{x:.0f},{y:.0f} l-3,-9 M{x:.0f},{y:.0f} l1,-11 M{x:.0f},{y:.0f} l4,-8" stroke="#5E8F38" stroke-width="2.4" stroke-linecap="round"/>')
    pth="M-20,410 C120,360 220,470 360,420 C500,370 600,300 820,330"
    s.append(f'<path d="{pth}" stroke="{INK}" stroke-width="86" fill="none" stroke-linecap="round"/><path d="{pth}" stroke="#C9965A" stroke-width="78" fill="none" stroke-linecap="round"/><path d="{pth}" stroke="#DDB27A" stroke-width="54" fill="none" stroke-linecap="round"/>')
    HR=46
    def hx(cx,cy,k=0.64,fill="#D9F2A6",op=".45",sw=2.5,st="#4E7F2E"):
        p=" ".join(f"{cx+k*HR*math.cos(math.radians(60*i)):.1f},{cy+k*HR*math.sin(math.radians(60*i)):.1f}" for i in range(6))
        return f'<polygon points="{p}" fill="{fill}" fill-opacity="{op}" stroke="{st}" stroke-width="{sw}" stroke-linejoin="round"/>'
    for col in range(12):
        for row in range(4):
            cx=40+col*HR*1.5; cy=60+row*HR*math.sqrt(3)+(HR*math.sqrt(3)/2 if col%2 else 0)
            if cy>300: continue
            s.append(hx(cx,cy))
    return "".join(s)

stage_over=(cloud(400,350,2.6,.42)
            +'<ellipse cx="400" cy="300" rx="230" ry="150" fill="none" stroke="#6E9B2E" stroke-width="4" stroke-dasharray="14 10"/>'
            +"".join(squiggle(x,y,46,rot) for x,y,rot in [(220,250,-10),(560,230,12),(300,440,6),(520,430,-8),(250,350,14),(560,340,-12)]))

def page():
    psvg=lambda s,h=236: s.replace('<svg ',f'<svg height="{h}" style="max-width:100%" ',1).replace('style="display:block;overflow:visible"','',1)
    ff_small=lambda svgsrc,x: f'<div style="position:absolute;left:{x}%;bottom:58px;width:150px;transform:translateX(-50%)">{psvg(svgsrc,180)}</div>'
    stage=(f'<svg viewBox="0 0 800 540" preserveAspectRatio="xMidYMid slice" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%">{stage_svg()}</svg>'
           f'<div style="position:absolute;left:50%;top:44px;transform:translateX(-50%);width:230px">{psvg(hero,310)}</div>'
           f'<svg viewBox="0 0 800 540" preserveAspectRatio="xMidYMid slice" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none">{stage_over}</svg>'
           + ff_small(fx_burger,30)+ff_small(fx_fries,72))
    chips="".join(chip(k,v) for k,v in [("Cena",drop()+"50"),("Růst","4 s"),("Oblak","~2 políčka"),("Smrad","1× za 6 s")])
    h=f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>Pan Cibule – list postavy</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&amp;family=Bangers&amp;family=Nunito:wght@500;700;800&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#5C7F1F}}a:hover{{color:#3F5A12}}
</style>
</helmet>
<div style="width:1680px;height:1700px;box-sizing:border-box;padding:48px 56px;background:{{{{paper}}}};font-family:Nunito,sans-serif;color:{INK};display:flex;flex-direction:column;gap:32px">
<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:32px">
<div style="display:flex;flex-direction:column;gap:6px">
<span style="font-size:16px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#5C7F1F">Fast Food Fight · obránce · nový</span>
<h1 style="margin:0;font-family:'Baloo 2',sans-serif;font-size:76px;font-weight:800;line-height:.95">Pan Cibule</h1>
<p style="margin:0;font-size:19px;font-weight:600;color:#5A4A3A;max-width:660px">Jednou za čas se naježí a vypustí oblak smradu. Fast food v oblaku kýchá, dusí se a na chvíli zpomalí. Sám nikoho nezasáhne, ale mrkve a pórky pak mají víc času.</p>
</div>
<div style="display:flex;gap:16px">
{chips}
</div>
</div>
<div style="display:flex;gap:28px;height:540px">
<div style="{card};width:330px;box-sizing:border-box;padding:20px;display:flex;flex-direction:column;gap:12px">
<span style="font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Předloha</span>
<div style="flex:1;border-radius:12px;overflow:hidden;background:#EFE6DA">
<img src="/_blob/dfd40d40fc4d1201dea6028b44dafdbc" alt="Dětská kresba: cibule s natí, rukama, nohama a zelenými vlnkami smradu kolem" style="width:100%;height:100%;object-fit:contain;display:block">
</div>
<span style="font-size:15px;color:#5A4A3A;font-weight:600">kresby/pan-cibule.png · popis v „Pan cibule.md“</span>
</div>
<div style="{card};flex:1;position:relative;overflow:hidden;background:#8BB85A">
{stage}
<span style="position:absolute;top:18px;left:22px;padding:4px 12px;background:rgba(255,255,255,.92);border:3px solid {INK};border-radius:12px;font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Ve hře</span>
<span style="position:absolute;top:22px;right:22px;padding:4px 10px;background:rgba(255,255,255,.92);border:2px solid {INK};border-radius:10px;font-size:14px;font-weight:800;color:#3F5A12">čárkovaně: dosah oblaku</span>
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
        bg="#E7F4FB" if t=="Ztuhnutí" else ("#FFF4D6" if t=="Úroveň 2" else ("#EEF7DC" if t in ("Naježení","Oblak smradu") else "#FFFFFF"))
        h+=f'''<div style="{card};background:{bg};padding:14px 12px 16px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{psvg(s)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:19px;font-weight:800;line-height:1.1">{i+1}. {t}</span>
<span style="font-size:13.5px;font-weight:600;color:#5A4A3A;line-height:1.3">{ds}</span>
</div>
'''
    steps=[("Naježí se","každých 6 s, jen když je fast food v dosahu"),("Pšššš!","kolem cibule se nafoukne zelený oblak, asi 2 políčka"),("Kýchání","fast food v oblaku kýchá a dusí se, jde 2× pomaleji"),("Vyvětrá se","po 3 s oblak zmizí a fast food zase zrychlí")]
    h+=f'''</div>
</div>
<div style="display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:26px;font-weight:800">Schopnost: oblak smradu</span>
<div style="display:grid;grid-template-columns:repeat(4, minmax(0, 1fr));gap:20px">
<div style="{card};background:#EEF7DC;padding:14px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{psvg(fx_burger,250)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Hamburger kýchá</span>
<span style="font-size:14px;font-weight:600;color:#5A4A3A">„Hapčí!“ zavře oči, prská, nad hlavou šnek: jde 2× pomaleji</span>
</div>
<div style="{card};background:#EEF7DC;padding:14px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{psvg(fx_fries,250)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Hranolky se dusí</span>
<span style="font-size:14px;font-weight:600;color:#5A4A3A">„Kch kch!“ vyplázne jazyk, taky 2× pomaleji</span>
</div>
<div style="{card};grid-column:span 2;padding:22px 24px;display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Jak to funguje</span>
'''
    for i,(t,d) in enumerate(steps):
        h+=f'''<div style="display:flex;align-items:center;gap:14px">
<span style="flex:none;width:44px;height:44px;border-radius:50%;background:#B5DD7A;border:3px solid {INK};display:flex;align-items:center;justify-content:center;font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">{i+1}</span>
<span style="font-size:17px;font-weight:700"><b style="font-family:'Baloo 2',sans-serif;font-size:19px">{t}</b> · {d}</span>
</div>
'''
    h+=f'''<p style="margin:4px 0 0;font-size:14px;font-weight:700;color:#5A4A3A;line-height:1.35">Čísla (cena 50, oblak ~2 políčka, 1× za 6 s, zpomalení na polovinu na 3 s) jsou návrh pro první playtest. Oblak nikoho nezasáhne, takže fast food kvůli němu neuteče.</p>
</div>
</div>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"paper":{{"editor":"color","default":"#F6F8EC"}},"$preview":{{"width":1680,"height":1700}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{ paper: this.props.paper ?? '#F6F8EC' }};
}}
}}
</script>
</body>
</html>
'''
    open(f'{ROOT}/Cibule.dc.html','w').write(h); print(len(h))
page()
