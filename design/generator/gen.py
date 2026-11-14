import math, random
INK="#2B2118"; OR="#F08A24"; ORD="#D9701A"; G1="#2F9E44"; G2="#1E7A33"; YEL="#FFC93C"
def lx(y): return 92+(y-148)*61/200
def rx(y): return 208-(y-148)*51/200
BODY="M90,150 A60,17 0 0 0 210,150 L159,347 Q155,354 151,347 Z"
TOP='<ellipse cx="150" cy="150" rx="60" ry="17" fill="#C9631A" stroke="#2B2118" stroke-width="5"/><ellipse cx="150" cy="152" rx="44" ry="10" fill="#B4560F"/>'

def leaves():
    r=random.Random(7); out=[]
    for i in range(15):
        bx=118+i*4.6+r.uniform(-2,2); by=150+r.uniform(-4,5)
        ang=math.radians(-62+i*8.8+r.uniform(-4,4)); L=r.uniform(88,122)
        ex=bx+math.sin(ang)*L; ey=by-math.cos(ang)*L
        cx=(bx+ex)/2+r.uniform(-10,10); cy=(by+ey)/2
        c=G1 if i%2 else G2
        out.append(f'<path d="M{bx:.1f},{by} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}" stroke="{c}" stroke-width="{r.choice([7,8,9])}" fill="none" stroke-linecap="round"/>')
    return "".join(out)

def body(tint=None, shine=False):
    s=[f'<path d="{BODY}" fill="{OR}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>']
    for y in [182,206,232,258,284,310]:
        a,b=lx(y)+2,rx(y)-2
        s.append(f'<path d="M{a:.1f},{y} Q{(a+b)/2:.1f},{y+15} {b:.1f},{y}" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    if tint=="ice":
        s.append(f'<path d="{BODY}" fill="#8FD0F2" opacity=".62"/>')
        s.append('<path d="M112,170 L132,318" stroke="#fff" stroke-width="6" opacity=".8" stroke-linecap="round"/><path d="M124,168 L130,210" stroke="#fff" stroke-width="3" opacity=".8" stroke-linecap="round"/>')
    if shine:
        s.append('<path d="M110,170 Q118,240 140,320" stroke="#FFE1B0" stroke-width="7" fill="none" opacity=".9" stroke-linecap="round"/>')
    return "".join(s)

def face(kind="smile"):
    if kind=="smile":
        return f'<circle cx="138" cy="190" r="5" fill="{INK}"/><circle cx="168" cy="188" r="5" fill="{INK}"/><path d="M133,206 Q152,224 174,204" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
    if kind=="closed":
        return f'<path d="M131,191 Q138,196 145,191" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M161,189 Q168,194 175,189" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M143,207 Q152,214 162,206" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/>'
    if kind=="fight":
        return f'<path d="M130,180 L145,186" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/><path d="M176,178 L161,185" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/><circle cx="139" cy="192" r="4.5" fill="{INK}"/><circle cx="167" cy="190" r="4.5" fill="{INK}"/><path d="M136,206 Q153,226 172,205 Z" fill="#8A2B1E" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
    if kind=="frozen":
        return f'<path d="M131,191 L145,191" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/><path d="M161,189 L175,189" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/><path d="M135,210 l6,-5 l6,5 l6,-5 l6,5 l6,-5 l6,5" stroke="{INK}" stroke-width="4" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
    if kind=="joy":
        return f'<path d="M131,193 L138,184 L145,193" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M161,191 L168,182 L175,191" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M134,203 Q153,232 174,202 Z" fill="#8A2B1E" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/><path d="M143,214 Q153,222 164,213" stroke="#E86A6A" stroke-width="5" fill="none" stroke-linecap="round"/>'

def arm(x1,y1,x2,y2):
    dx,dy=x2-x1,y2-y1; L=math.hypot(dx,dy); px,py=-dy/L*13,dx/L*13
    tx,ty=x2-dx/L*6,y2-dy/L*6
    return (f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{OR}" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M{tx-px:.1f},{ty-py:.1f} L{tx+px:.1f},{ty+py:.1f}" stroke="{OR}" stroke-width="6" stroke-linecap="round"/>')

def legs():
    return (f'<path d="M146,338 L141,384 L122,386" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M162,338 L168,384 L188,384" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')

def sword_local():
    r=random.Random(3); s=[]
    for i in range(7):
        a=math.radians(-40+i*13); L=r.uniform(20,30)
        s.append(f'<path d="M{-9+i*3},0 Q{-9+i*3+math.sin(a)*8:.1f},{L*.5:.1f} {(-9+i*3)+math.sin(a)*L*.7:.1f},{L:.1f}" stroke="{G1 if i%2 else G2}" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
    s.append(f'<path d="M-16,-2 L16,-2 L1,-74 Z" fill="{OR}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    for y in [-14,-28,-42,-56]:
        w=16*(74+y)/72
        s.append(f'<path d="M{-w+2:.1f},{y} L{w-2:.1f},{y-2}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
    return "".join(s)

def sword(x,y,ang,sc=1.0):
    return f'<g transform="translate({x},{y}) rotate({ang}) scale({sc})">{sword_local()}</g>'

def star(cx,cy,r,fill=YEL):
    pts=[]
    for i in range(10):
        rr=r if i%2==0 else r*.45; a=math.radians(-90+i*36)
        pts.append(f"{cx+math.cos(a)*rr:.1f},{cy+math.sin(a)*rr:.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'

def tile():
    return ('<polygon points="78,364 232,364 258,412 52,412" fill="#B87A45" stroke="#2B2118" stroke-width="4" stroke-linejoin="round"/>'
            '<path d="M84,378 L226,378 M70,394 L240,394" stroke="#8E5A2E" stroke-width="3" stroke-linecap="round"/>'
            '<polygon points="52,412 258,412 258,422 52,422" fill="#7A4A24" stroke="#2B2118" stroke-width="4" stroke-linejoin="round"/>')
def shadow(rx_=58,op=.18): return tile()+f'<ellipse cx="155" cy="388" rx="{rx_}" ry="13" fill="#3A2210" opacity="{op}"/>'

n=[0]
def wrap(inner, vb="0 0 300 430", w=None, h=None, label="Pan Mrkev"):
    n[0]+=1; fid=f"wob{n[0]}"
    size=(f'width="{w}" ' if w else '')+(f'height="{h}"' if h else '')
    return (f'<svg viewBox="{vb}" {size} role="img" aria-label="{label}" style="display:block;overflow:visible">'
            f'<defs><filter id="{fid}" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="{n[0]}"/><feDisplacementMap in="SourceGraphic" scale="3.2"/></filter></defs>'
            f'<g filter="url(#{fid})">{inner}</g></svg>')

def carrot(face_="smile", pose="rest", tint=None, shine=False, sc=1.0, extra_back="", extra_front=""):
    arms={"rest":[(101,200,46,212),(199,200,250,198)],
          "slash":[(101,200,50,222),(199,196,246,150)],
          "up":[(101,195,60,138),(199,195,244,136)]}[pose]
    sw={"rest":(250,198,0),"slash":(246,150,62),"up":(244,136,18)}[pose]
    return (extra_back+legs()+arm(*arms[0])+body(tint,shine)+TOP+leaves()+face(face_)+arm(*arms[1])
            +sword(sw[0],sw[1],sw[2],sc)+extra_front)

# --- poses
hero=wrap(shadow()+carrot("smile"), w=380, h=507)

grow_inner=(tile().replace('364','214').replace('378','228').replace('394','244').replace('412','262').replace('422','272')
    +'<ellipse cx="155" cy="238" rx="64" ry="16" fill="#3A2210" stroke="#2B2118" stroke-width="4"/>'
    +'<defs><clipPath id="gclip"><path d="M0,-60 L300,-60 L300,238 L219,238 A64,16 0 0 1 91,238 L0,238 Z"/></clipPath></defs>'
    '<g clip-path="url(#gclip)"><g transform="translate(5,112)">'+body()+TOP+leaves()+face("closed")+'</g></g>'
    +f'<path d="M91,238 A64,16 0 0 0 219,238" stroke="{INK}" stroke-width="4" fill="none"/>'
    +f'<circle cx="74" cy="226" r="6" fill="#8B5A2B" stroke="{INK}" stroke-width="3"/><circle cx="236" cy="224" r="7" fill="#8B5A2B" stroke="{INK}" stroke-width="3"/><circle cx="222" cy="204" r="4" fill="#8B5A2B" stroke="{INK}" stroke-width="3"/>'
    +f'<path d="M58,190 l-14,-8 M250,186 l14,-9 M62,160 l-12,-2 M248,158 l12,-3" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>')
grow=wrap(grow_inner, vb="0 -40 300 330")

slash_front=(f'<path d="M222,96 Q320,120 300,232" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round" stroke-dasharray="2 10"/>'
             f'<path d="M236,82 Q340,112 318,240" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round" opacity=".5"/>'
             f'<text x="258" y="300" font-family="Bangers, Baloo 2, sans-serif" font-size="38" fill="{OR}" stroke="{INK}" stroke-width="1.6" transform="rotate(-10 258 300)">ŠVIH!</text>')
slash=wrap(shadow()+'<g transform="rotate(-6 155 300)">'+carrot("fight","slash",extra_front=slash_front)+'</g>', vb="0 0 340 430")

fry=(f'<g transform="translate(176,232) rotate(-28)"><rect x="-6" y="-34" width="12" height="54" rx="3" fill="#FFD25A" stroke="{INK}" stroke-width="3.5"/><path d="M-2,-26 L-2,8" stroke="#E8A93A" stroke-width="2.5"/></g>')
ice_bits="".join(f'<g transform="translate({x},{y})" stroke="#4BA6D6" stroke-width="3.5" stroke-linecap="round"><path d="M-9,0 L9,0 M-5,-8 L5,8 M5,-8 L-5,8"/></g>' for x,y in [(60,150),(250,120),(40,270),(262,300),(86,96)])
shake=f'<path d="M28,200 l-10,4 M28,214 l-12,0 M282,196 l10,-4 M282,210 l12,0" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>'
frozen=wrap(shadow()+carrot("frozen",tint="ice",extra_front=fry+ice_bits+shake))

joy_front=star(48,120,18)+star(262,92,14)+star(34,236,11)+star(280,230,16)
joy=wrap(shadow(40,.12)+'<g transform="translate(0,-26)">'+carrot("joy","up",extra_front=joy_front)+'</g>', vb="0 -20 300 450")

badge=(star(250,60,30,YEL)+f'<text x="250" y="70" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="28" fill="{INK}">2</text>')
glow=f'<path d="{BODY}" fill="none" stroke="#FFD447" stroke-width="22" stroke-linejoin="round" opacity=".7"/>'
lvl2=wrap(shadow()+carrot("fight",shine=True,sc=1.35,extra_back=glow,extra_front=badge))

idle_front=f'<path d="M58,140 q-10,-6 -4,-16 M250,262 q12,4 8,14" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round" opacity=".55"/>'
idle=wrap(shadow()+'<g transform="rotate(3 155 380)">'+carrot("smile",extra_front=idle_front)+'</g>')

parts=[("Nať","pohupuje se zvlášť",wrap(leaves(),vb="55 15 200 140",label="Nať")),
       ("Tělo","zmáčkne se při seku",wrap(body()+TOP,vb="84 128 132 228",label="Tělo")),
       ("Obličej","5 výrazů",wrap(face("smile"),vb="124 172 58 60",label="Obličej")),
       ("Ruka","2×, otáčí se v rameni",wrap(arm(101,200,46,212),vb="36 184 74 44",label="Ruka")),
       ("Nohy","ťap ťap při radosti",wrap(legs(),vb="114 330 82 64",label="Nohy")),
       ("Mrkvomeč","zbraň, kořínky = rukojeť",wrap(sword_local(),vb="-26 -82 52 118",label="Mrkvomeč"))]

poses=[("Vyrůstání","3 s, ze záhonu vykoukne nať, pak celé tělo",grow),
       ("Klid","pohupování a mrkání",idle),
       ("Sek mrkvomečem","1 sek za 1 s, dosah ~1,5 políčka",slash),
       ("Ztuhnutí","po zásahu hranolkou 2 s modrý a kmitá",frozen),
       ("Radost","výskok, když fast food uteče",joy),
       ("Úroveň 2","za 30 vody: o 40 % rychlejší, větší meč",lvl2)]

def drop():
    return '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M12 3 C12 3 5 11 5 15.5 A7 7 0 0 0 19 15.5 C19 11 12 3 12 3 Z" fill="#2D8CD6" stroke="#2B2118" stroke-width="1.6"/></svg>'

chip=lambda k,v: f'<div style="display:flex;flex-direction:column;gap:2px;padding:10px 18px;background:#FFFFFF;border:3px solid {INK};border-radius:16px;box-shadow:4px 4px 0 {INK}"><span style="font-size:13px;font-weight:700;color:#6B5B4B;text-transform:uppercase;letter-spacing:.06em">{k}</span><span style="font-family:\'Baloo 2\',sans-serif;font-size:24px;font-weight:800;line-height:1;display:flex;align-items:center;gap:6px">{v}</span></div>'

card="background:#FFFFFF;border:3px solid #2B2118;border-radius:22px;box-shadow:6px 6px 0 #2B2118"
html=f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>Pan Mrkev – list postavy</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&amp;family=Bangers&amp;family=Nunito:wght@500;700;800&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#B4530F}}a:hover{{color:#8A3E0B}}
</style>
</helmet>
<div style="width:1680px;height:1280px;box-sizing:border-box;padding:48px 56px;background:{{{{paper}}}};font-family:Nunito,sans-serif;color:{INK};display:flex;flex-direction:column;gap:32px">
<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:32px">
<div style="display:flex;flex-direction:column;gap:6px">
<span style="font-size:16px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:{ORD}">Fast Food Fight · obránce · 1. úroveň</span>
<h1 style="margin:0;font-family:'Baloo 2',sans-serif;font-size:76px;font-weight:800;line-height:.95">Pan Mrkev</h1>
<p style="margin:0;font-size:19px;font-weight:600;color:#5A4A3A;max-width:620px">Úplně základní obránce. Seká mrkvomečem jen v bezprostřední blízkosti cesty. Papírová loutka podle dětské kresby.</p>
</div>
<div style="display:flex;gap:16px">
{chip("Cena", drop()+"40")}
{chip("Růst","3 s")}
{chip("Dosah","~1,5 políčka")}
{chip("Útok","1 sek / 1 s")}
</div>
</div>
<div style="display:flex;gap:28px;height:540px">
<div style="{card};width:330px;box-sizing:border-box;padding:20px;display:flex;flex-direction:column;gap:12px">
<span style="font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Předloha</span>
<div style="flex:1;border-radius:12px;overflow:hidden;background:#EEE">
<img src="/_blob/7a2250a57a5c3b438dd99ad55c0011b3" alt="Dětská kresba: Pan Mrkev a zbraň mrkvoměč" style="width:100%;height:100%;object-fit:cover;object-position:50% 72%;display:block">
</div>
<span style="font-size:15px;color:#5A4A3A;font-weight:600">kresby/mrkev.png</span>
</div>
<div style="{card};flex:1;position:relative;display:flex;align-items:center;justify-content:center;background:{{{{stage}}}};overflow:hidden">
<svg viewBox="0 0 800 540" preserveAspectRatio="none" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%"><polygon points="150,150 650,150 800,540 0,540" fill="#E9C99A"/><polygon points="540,150 640,150 790,540 590,540" fill="#F4F1E8" stroke="#2B2118" stroke-width="3"/><path d="M556,150 L622,540 M624,150 L758,540" stroke="#D86B5A" stroke-width="5" stroke-dasharray="14 10"/><path d="M123,220 L677,220" stroke="#C9A06C" stroke-width="2"/><path d="M90,306 L710,306" stroke="#C9A06C" stroke-width="2"/><path d="M51,407 L749,407" stroke="#C9A06C" stroke-width="2"/><path d="M150,150 L650,150" stroke="#2B2118" stroke-width="3"/><polygon points="60,330 200,330 176,430 10,430" fill="#B87A45" stroke="#2B2118" stroke-width="3" opacity=".55"/><polygon points="180,190 300,190 292,250 158,250" fill="#B87A45" stroke="#2B2118" stroke-width="3" opacity=".55"/><polygon points="390,190 510,190 520,250 386,250" fill="#B87A45" stroke="#2B2118" stroke-width="3" opacity=".55"/></svg>
<div style="position:relative;margin-top:-10px">{hero}</div>
<span style="position:absolute;top:20px;left:24px;font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Ve hře</span>
<span style="position:absolute;top:24px;right:24px;font-size:15px;font-weight:700;color:#5A4A3A">kamera shora a z boku (~55°), loutka natočená ke kameře</span>
</div>
<div style="{card};width:440px;box-sizing:border-box;padding:20px;display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Díly loutky</span>
<div style="display:grid;grid-template-columns:repeat(2, minmax(0, 1fr));gap:12px;flex:1">
'''
for t,d,s in parts:
    html+=f'''<div style="border:2px dashed #BFAE98;border-radius:14px;padding:10px;display:flex;flex-direction:column;align-items:center;gap:6px">
<div style="height:78px;width:100%;display:flex;align-items:center;justify-content:center">{s.replace('<svg ','<svg height="74" style="max-width:100%" ',1).replace('style="display:block;overflow:visible"','',1)}</div>
<span style="font-weight:800;font-size:16px">{t}</span>
<span style="font-size:13px;color:#5A4A3A;font-weight:600;text-align:center">{d}</span>
</div>
'''
html+=f'''</div>
</div>
</div>
<div style="display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:26px;font-weight:800">Stavy a animace</span>
<div style="display:grid;grid-template-columns:repeat(6, minmax(0, 1fr));gap:20px">
'''
for i,(t,d,s) in enumerate(poses):
    bg = "#E7F4FB" if t=="Ztuhnutí" else ("#FFF4D6" if t=="Úroveň 2" else "#FFFFFF")
    html+=f'''<div style="{card};background:{bg};padding:14px 14px 16px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{s.replace('<svg ','<svg height="240" ',1)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800;line-height:1.1">{i+1}. {t}</span>
<span style="font-size:14px;font-weight:600;color:#5A4A3A;line-height:1.3">{d}</span>
</div>
'''
html+='''</div>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{"paper":{"editor":"color","default":"#FBF6EC","options":["#FBF6EC","#FFFFFF","#EAF4E4"]},"stage":{"editor":"color","default":"#DDF0F7"},"$preview":{"width":1680,"height":1280}}'>
class Component extends DCLogic {
renderVals() {
return { paper: this.props.paper ?? '#FBF6EC', stage: this.props.stage ?? '#DDF0F7' };
}
}
</script>
</body>
</html>
'''
import os, json, datetime
root="/mnt/user-data/outputs/artifacts/0c045be6-49f0-4f56-9475-27d367f93a14/project"
os.makedirs(root,exist_ok=True)
open(root+"/Main.dc.html","w").write(html)
idx={"v":3,"createdOnFiles":{"v":1,"at":datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")},"title":"Fast Food Fight – Pan Mrkev","launch":{"view":"canvas"},"pages":[],"boards":{"Main.dc.html":{"x":0,"y":0,"w":1680,"h":1280,"title":"Pan Mrkev – list postavy"}},"order":["Main.dc.html"],"notes":{},"designSystems":[]}
json.dump(idx,open(root+"/canvas.json","w"),ensure_ascii=False)
print(len(html))
