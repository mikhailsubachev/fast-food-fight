import math, random, json
import gen
from gen import INK, YEL, star, tile, wrap, drop, chip, card
GL="#E4F1C6"; G1="#3FA34D"; G2="#6CBF45"; ARMC="#4A4540"
BODYP="M128,172 L128,330 Q152,342 176,330 L176,172 Z"

def leaves():
    tops=[(92,70),(116,48),(140,34),(164,44),(190,64),(214,82)]
    s=[]
    for i in range(5):
        b0=128+i*9.6; b1=b0+9.6
        (t0x,t0y),(t1x,t1y)=tops[i],tops[i+1]
        c=G1 if i%2==0 else G2
        s.append(f'<path d="M{b0:.1f},180 L{t0x},{t0y} Q{(t0x+t1x)/2},{min(t0y,t1y)-8} {t1x},{t1y} L{b1:.1f},180 Z" fill="{c}" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>')
        s.append(f'<path d="M{(b0+b1)/2:.1f},176 L{(t0x+t1x)/2:.1f},{(t0y+t1y)/2+10:.1f}" stroke="#A8DB7A" stroke-width="2.5" opacity=".8" stroke-linecap="round"/>')
    return "".join(s)

def body(tint=None, shine=False):
    r=random.Random(11)
    dots="".join(f'<circle cx="{r.uniform(132,172):.1f}" cy="{r.uniform(200,326):.1f}" r="{r.uniform(1,2.2):.1f}" fill="#9BCB6A" opacity=".8"/>' for _ in range(40))
    s=[f'<path d="{BODYP}" fill="{GL}" stroke="none"/>',dots,
       '<path d="M164,176 L164,334 Q172,332 176,330 L176,176 Z" fill="#C9E0A0" opacity=".9"/>',
       f'<path d="{BODYP}" fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>']
    if tint=="ice":
        s.append(f'<path d="{BODYP}" fill="#8FD0F2" opacity=".6"/><path d="M136,190 L136,318" stroke="#fff" stroke-width="5" opacity=".85" stroke-linecap="round"/>')
    if shine:
        s.append('<path d="M138,190 L138,318" stroke="#FFFFFF" stroke-width="6" opacity=".9" stroke-linecap="round"/>')
    return "".join(s)

def roots():
    r=random.Random(5)
    return "".join(f'<path d="M{140+i*4},334 q{r.uniform(-6,6):.1f},8 {r.uniform(-8,8):.1f},{r.uniform(12,20):.1f}" stroke="#B9D98F" stroke-width="2" fill="none" stroke-linecap="round"/>' for i in range(7))

def face(kind="smile"):
    e=lambda x,y: f'<circle cx="{x}" cy="{y}" r="4.2" fill="{INK}"/>'
    if kind=="smile": return e(143,200)+e(162,199)+f'<path d="M141,212 Q152,224 165,211" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/>'
    if kind=="closed": return f'<path d="M137,201 Q143,205 149,201 M156,200 Q162,204 168,200" stroke="{INK}" stroke-width="3.6" fill="none" stroke-linecap="round"/><path d="M145,213 Q152,218 159,213" stroke="{INK}" stroke-width="3.6" fill="none" stroke-linecap="round"/>'
    if kind=="aim": return f'<path d="M137,200 L149,202" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'+e(163,199)+f'<path d="M156,190 L170,192" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/><path d="M142,213 Q150,210 160,214" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M158,214 q4,7 9,2" fill="#E86A6A" stroke="{INK}" stroke-width="2.5"/>'
    if kind=="frozen": return f'<path d="M137,200 L149,200 M156,199 L168,199" stroke="{INK}" stroke-width="4" stroke-linecap="round"/><path d="M139,215 l5,-4 l5,4 l5,-4 l5,4 l5,-4" stroke="{INK}" stroke-width="3.5" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
    if kind=="joy": return f'<path d="M137,203 L143,195 L149,203 M156,202 L162,194 L168,202" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M140,210 Q152,234 166,209 Z" fill="#8A2B1E" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'
    if kind=="fight": return e(143,201)+e(162,200)+f'<path d="M136,191 L149,195 M169,190 L156,194" stroke="{INK}" stroke-width="4" stroke-linecap="round"/><path d="M142,212 Q152,220 164,211" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/>'

def arm(x1,y1,x2,y2,tick=True):
    dx,dy=x2-x1,y2-y1; L=math.hypot(dx,dy); px,py=-dy/L*12,dx/L*12
    t=f'<path d="M{x2-px:.1f},{y2-py:.1f} L{x2+px:.1f},{y2+py:.1f}" stroke="{ARMC}" stroke-width="5.5" stroke-linecap="round"/>' if tick else ''
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{ARMC}" stroke-width="6" stroke-linecap="round"/>'+t

def legs():
    return roots()+(f'<path d="M142,336 L138,384 L116,386" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M163,336 L169,384 L192,385" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')

def bow_local(pull=0, gold=False, sc=1.0):
    h=56*sc; b=24*sc
    col="#F2C230" if gold else G1
    s=(f'<path d="M0,{-h} Q{b*2},0 0,{h}" stroke="{INK}" stroke-width="11" fill="none" stroke-linecap="round"/>'
       f'<path d="M0,{-h} Q{b*2},0 0,{h}" stroke="{col}" stroke-width="5.5" fill="none" stroke-linecap="round"/>'
       f'<path d="M-2,{-h} L{-pull},0 L-2,{h}" stroke="{INK}" stroke-width="2" fill="none"/>'
       f'<path d="M-4,{-h-2} q-6,-8 2,-12 M-4,{h+2} q-6,8 2,12" stroke="{G1}" stroke-width="3" fill="none" stroke-linecap="round"/>')
    return s

def arrow_local(sc=1.0):
    # tail (leaves) at x=0, head (roots) at x=62
    s=[]
    for dy,c in [(-7,G1),(0,G2),(7,G1)]:
        s.append(f'<path d="M14,{dy*0.3:.1f} L0,{dy*1.6:.1f} L-4,{dy*1.6+3:.1f} L16,{dy*0.3+2:.1f} Z" fill="{c}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
    s.append(f'<rect x="14" y="-5" width="40" height="10" rx="4" fill="{GL}" stroke="{INK}" stroke-width="3"/>')
    for k in range(4):
        s.append(f'<path d="M54,{-3+k*2} q5,{-2+k*1.3:.1f} 10,{-4+k*2.6:.1f}" stroke="#B9D98F" stroke-width="2" fill="none" stroke-linecap="round"/>')
    return f'<g transform="scale({sc})">{"".join(s)}</g>'

def place(inner,x,y,a=0): return f'<g transform="translate({x},{y}) rotate({a})">{inner}</g>'

def leek(face_="smile", pose="rest", tint=None, shine=False, gold=False, bsc=1.0, back="", front=""):
    if pose=="rest":
        a1=arm(128,222,80,218); a2=arm(176,222,226,218)
        bow=place(bow_local(0,gold,bsc),226,218,0)
        return back+legs()+a1+body(tint,shine)+leaves()+face(face_)+a2+bow+front
    if pose=="draw":
        a_bow=arm(176,214,240,206,tick=False)
        a_pull=arm(128,220,196,207,tick=False)
        bow=place(bow_local(44*bsc/1.0 if bsc>1 else 44,gold,bsc),240,206,0)
        arr=place(arrow_local(),196,206)
        return back+legs()+body(tint,shine)+leaves()+face(face_)+a_bow+bow+arr+a_pull+front
    if pose=="shot":
        a_bow=arm(176,214,240,206,tick=False)
        a_pull=arm(128,220,160,232)
        bow=place(bow_local(0,gold,bsc),240,206,0)
        return back+legs()+body(tint,shine)+leaves()+face(face_)+a_bow+bow+a_pull+front
    if pose=="up":
        a1=arm(128,214,84,160); a2=arm(176,214,222,156)
        bow=place(bow_local(0,gold,bsc),222,156,-20)
        return back+legs()+a1+body(tint,shine)+leaves()+face(face_)+a2+bow+front

def shadow(rx_=50,op=.18): return tile()+f'<ellipse cx="155" cy="388" rx="{rx_}" ry="12" fill="#3A2210" opacity="{op}"/>'

# hero
hero=wrap(shadow()+leek("smile"), w=354, h=507, label="Pórek")

# poses
grow_inner=(tile().replace('364','214').replace('378','228').replace('394','244').replace('412','262').replace('422','272')
    +'<ellipse cx="155" cy="238" rx="56" ry="15" fill="#3A2210" stroke="#2B2118" stroke-width="4"/>'
    +'<defs><clipPath id="pclip"><path d="M0,-60 L300,-60 L300,238 L211,238 A56,15 0 0 1 99,238 L0,238 Z"/></clipPath></defs>'
    '<g clip-path="url(#pclip)"><g transform="translate(3,40)">'+body()+leaves()+face("closed")+'</g></g>'
    +f'<path d="M99,238 A56,15 0 0 0 211,238" stroke="{INK}" stroke-width="4" fill="none"/>'
    +f'<circle cx="74" cy="226" r="6" fill="#8B5A2B" stroke="{INK}" stroke-width="3"/><circle cx="236" cy="224" r="7" fill="#8B5A2B" stroke="{INK}" stroke-width="3"/>'
    +f'<path d="M58,190 l-14,-8 M250,186 l14,-9 M62,150 l-12,-2 M248,148 l12,-3" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>')
grow=wrap(grow_inner, vb="0 -20 300 310", label="Pórek vyrůstá")

idle=wrap(shadow()+'<g transform="rotate(-2 155 380)">'+leek("smile",front=f'<path d="M70,120 q-10,-6 -4,-16 M244,110 q10,-4 12,6" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round" opacity=".55"/>')+'</g>', label="Pórek v klidu")

tension=f'<path d="M262,180 l8,-6 M266,206 l10,0 M262,232 l8,6" stroke="{INK}" stroke-width="3" stroke-linecap="round" opacity=".7"/>'
draw=wrap(shadow()+leek("aim","draw",front=tension), vb="0 0 320 430", label="Pórek natahuje luk")

flight=(f'<path d="M262,206 Q330,110 400,170" stroke="{INK}" stroke-width="3.5" fill="none" stroke-dasharray="3 10" stroke-linecap="round"/>'
        +place(arrow_local(1.1),352,128,8)
        +f'<path d="M332,122 l-18,-4 M334,134 l-20,2" stroke="{INK}" stroke-width="3" stroke-linecap="round" opacity=".6"/>'
        +f'<text x="250" y="300" font-family="Bangers, Baloo 2, sans-serif" font-size="36" fill="{G1}" stroke="{INK}" stroke-width="1.5" transform="rotate(-8 250 300)">ŠUP!</text>'
        +f'<path d="M238,170 q6,-4 4,-12 M248,248 q8,2 10,10" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round"/>')
shot=wrap(shadow()+leek("fight","shot",front=flight), vb="0 0 410 430", label="Pórek vystřelil pórkošíp")

fry=f'<g transform="translate(166,262) rotate(-30)"><rect x="-6" y="-34" width="12" height="54" rx="3" fill="#FFD25A" stroke="{INK}" stroke-width="3.5"/></g>'
ice=gen.ice_bits+f'<path d="M30,200 l-10,4 M30,214 l-12,0 M282,196 l10,-4 M282,210 l12,0" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>'
frozen=wrap(shadow()+leek("frozen",tint="ice",front=fry+ice), label="Pórek ztuhl")

joy=wrap(shadow(36,.12)+'<g transform="translate(0,-26)">'+leek("joy","up",front=star(46,120,17)+star(270,80,14)+star(36,250,11)+star(272,250,15))+'</g>', vb="0 -10 300 440", label="Pórek se raduje")

badge=star(254,60,30)+f'<text x="254" y="70" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="28" fill="{INK}">2</text>'
glow=f'<path d="{BODYP}" fill="none" stroke="#FFD447" stroke-width="22" stroke-linejoin="round" opacity=".7"/>'
lvl2=wrap(shadow()+leek("fight","rest",shine=True,gold=True,bsc=1.2,back=glow,front=badge), label="Pórek úroveň 2")

parts=[("Nať","5 listů, vlají při výstřelu",wrap(leaves(),vb="86 28 134 156",label="Nať")),
       ("Tělo","zmáčkne se při výstřelu",wrap(body(),vb="122 166 60 180",label="Tělo")),
       ("Obličej","míří jedním okem",wrap(face("smile"),vb="132 186 42 42",label="Obličej")),
       ("Ruka","2×, otáčí se v rameni",wrap(arm(128,222,80,218),vb="70 200 66 36",label="Ruka")),
       ("Nohy","s kořínky",wrap(legs(),vb="110 330 90 64",label="Nohy")),
       ("Luk","z pórkového listu",wrap(bow_local(),vb="-12 -76 70 152",label="Luk")),
       ("Pórkošíp","malý pórek, letí kořínky napřed",wrap(arrow_local(),vb="-8 -16 80 32",label="Pórkošíp"))]

poses=[("Vyrůstání","4 s, nejdřív vykouknou listy"),("Klid","pohupování, luk u boku"),
       ("Natažení","míří jedním okem na nejbližší fast food"),("Výstřel","1 pórkošíp za 1,5 s, letí obloukem"),
       ("Ztuhnutí","po zásahu hranolkou 2 s modrý"),("Radost","výskok, když fast food uteče"),
       ("Úroveň 2","za 45 vody: dosah +1 políčko, o 20 % rychlejší")]
psvg=[grow,idle,draw,shot,frozen,joy,lvl2]

stage_bg=('<svg viewBox="0 0 800 540" preserveAspectRatio="none" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%">'
 '<polygon points="150,150 650,150 800,540 0,540" fill="#E9C99A"/>'
 + "".join(f'<path d="M{150-150*t:.0f},{150+390*t:.0f} L{650+150*t:.0f},{150+390*t:.0f}" stroke="#C9A06C" stroke-width="2"/>' for t in [0.18,0.4,0.66])
 + '<path d="M150,150 L650,150" stroke="#2B2118" stroke-width="3"/>'
 '<polygon points="560,150 660,150 800,470 800,540 610,540" fill="#F4F1E8" stroke="#2B2118" stroke-width="3"/>'
 '<path d="M578,150 L640,540 M644,150 L790,500" stroke="#D86B5A" stroke-width="5" stroke-dasharray="14 10"/>'
 '<ellipse cx="400" cy="455" rx="340" ry="70" fill="#2D8CD6" fill-opacity=".08" stroke="#2D8CD6" stroke-width="3" stroke-dasharray="12 9"/>'
 '<polygon points="60,250 190,250 170,330 20,330" fill="#B87A45" stroke="#2B2118" stroke-width="3" opacity=".55"/>'
 '</svg>')
flight_stage=('<svg viewBox="0 0 800 540" preserveAspectRatio="none" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none">'
 '<path d="M500,250 Q600,120 690,330" stroke="#2B2118" stroke-width="3.5" fill="none" stroke-dasharray="3 11" stroke-linecap="round"/>'
 +place(arrow_local(1.2),598,182,22)+'</svg>')

html=f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>Pórek – list postavy</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&amp;family=Bangers&amp;family=Nunito:wght@500;700;800&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#2F7A2A}}a:hover{{color:#1E5A1C}}
</style>
</helmet>
<div style="width:1680px;height:1280px;box-sizing:border-box;padding:48px 56px;background:{{{{paper}}}};font-family:Nunito,sans-serif;color:{INK};display:flex;flex-direction:column;gap:32px">
<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:32px">
<div style="display:flex;flex-direction:column;gap:6px">
<span style="font-size:16px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#2F7A2A">Fast Food Fight · obránce · 1. úroveň</span>
<h1 style="margin:0;font-family:'Baloo 2',sans-serif;font-size:76px;font-weight:800;line-height:.95">Pórek</h1>
<p style="margin:0;font-size:19px;font-weight:600;color:#5A4A3A;max-width:640px">Lučišník. Z dálky střílí pórkošípy, malé pórky, které letí obloukem. Odemkne se ve 2. vlně; nejlépe stojí dál od cesty, kam hranolky nedohodí.</p>
</div>
<div style="display:flex;gap:16px">
{chip("Cena", drop()+"60")}
{chip("Růst","4 s")}
{chip("Dosah","~3,5 políčka")}
{chip("Útok","1 šíp / 1,5 s")}
</div>
</div>
<div style="display:flex;gap:28px;height:540px">
<div style="{card};width:330px;box-sizing:border-box;padding:20px;display:flex;flex-direction:column;gap:12px">
<span style="font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Předloha</span>
<div style="flex:1;border-radius:12px;overflow:hidden;background:#EEE">
<img src="/_blob/4c7370532aa413c6ae56e3f6ae93bcf1" alt="Dětská kresba: pórek s rukama a nohama" style="width:100%;height:100%;object-fit:cover;object-position:50% 40%;display:block">
</div>
<span style="font-size:15px;color:#5A4A3A;font-weight:600">kresby/porek.png · luk a pórkošíp dokreslené</span>
</div>
<div style="{card};flex:1;position:relative;display:flex;align-items:center;justify-content:center;background:{{{{stage}}}};overflow:hidden">
{stage_bg}
<div style="position:relative;margin-top:-10px;margin-left:-120px">{hero}</div>
{flight_stage}
<span style="position:absolute;top:20px;left:24px;font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Ve hře</span>
<span style="position:absolute;top:24px;right:24px;font-size:15px;font-weight:700;color:#5A4A3A">kamera shora a z boku (~55°), modře dosah</span>
</div>
<div style="{card};width:440px;box-sizing:border-box;padding:20px;display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Díly loutky</span>
<div style="display:grid;grid-template-columns:repeat(3, minmax(0, 1fr));gap:10px;flex:1">
'''
for t,d,s in parts:
    html+=f'''<div style="border:2px dashed #BFAE98;border-radius:14px;padding:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px">
<div style="height:70px;width:100%;display:flex;align-items:center;justify-content:center">{s.replace('<svg ','<svg height="66" style="max-width:100%" ',1).replace('style="display:block;overflow:visible"','',1)}</div>
<span style="font-weight:800;font-size:15px">{t}</span>
<span style="font-size:12px;color:#5A4A3A;font-weight:600;text-align:center;line-height:1.25">{d}</span>
</div>
'''
html+=f'''</div>
</div>
</div>
<div style="display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:26px;font-weight:800">Stavy a animace</span>
<div style="display:grid;grid-template-columns:repeat(7, minmax(0, 1fr));gap:18px">
'''
for i,((t,d),s) in enumerate(zip(poses,psvg)):
    bg = "#E7F4FB" if t=="Ztuhnutí" else ("#FFF4D6" if t=="Úroveň 2" else "#FFFFFF")
    html+=f'''<div style="{card};background:{bg};padding:14px 12px 16px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{s.replace('<svg ','<svg height="236" style="max-width:100%" ',1).replace('style="display:block;overflow:visible"','',1)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:19px;font-weight:800;line-height:1.1">{i+1}. {t}</span>
<span style="font-size:13.5px;font-weight:600;color:#5A4A3A;line-height:1.3">{d}</span>
</div>
'''
html+='''</div>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{"paper":{"editor":"color","default":"#F3F8EA","options":["#F3F8EA","#FBF6EC","#FFFFFF"]},"stage":{"editor":"color","default":"#DDF0F7"},"$preview":{"width":1680,"height":1280}}'>
class Component extends DCLogic {
renderVals() {
return { paper: this.props.paper ?? '#F3F8EA', stage: this.props.stage ?? '#DDF0F7' };
}
}
</script>
</body>
</html>
'''
root="/mnt/user-data/outputs/artifacts/0c045be6-49f0-4f56-9475-27d367f93a14/project"
open(root+"/Porek.dc.html","w").write(html)
print(len(html))
