import math, random
import gen, gen_ff as gf, gen_porek as gp, gen_cibule as gc
from gen import INK, YEL, star, wrap, drop, chip, card
ROOT="/mnt/user-data/outputs/artifacts/0c045be6-49f0-4f56-9475-27d367f93a14/project"
RED="#E0483F"; CANDY="#FBF3EE"; STICK="#D6D3CC"; SYR="#E8424A"

def spiral(cx,cy,R,turns=2.6,w=15,col=RED):
    pts=[]
    for k in range(120):
        t=k/119; a=t*turns*2*math.pi; r=4+t*(R-6)
        pts.append(f"{cx+math.cos(a)*r:.1f},{cy+math.sin(a)*r:.1f}")
    return f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
def candy(cx,cy,R,rot=0,w=None):
    w=w or R*0.2
    return (f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{CANDY}"/>'
            f'<g transform="rotate({rot} {cx} {cy})">{spiral(cx,cy,R,2.6,w)}</g>'
            f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{RED}" stroke-width="{w*0.7:.1f}" opacity=".85"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{INK}" stroke-width="{max(3,R*0.065):.1f}"/>'
            f'<path d="M{cx-R*0.6:.1f},{cy-R*0.45:.1f} Q{cx-R*0.35:.1f},{cy-R*0.75:.1f} {cx+R*0.05:.1f},{cy-R*0.78:.1f}" stroke="#FFFFFF" stroke-width="{max(3,R*0.1):.1f}" fill="none" stroke-linecap="round" opacity=".9"/>')
def mini(x,y,ang,R=24,rot=0):
    # small lollipop held in hand: stick from hand outward, candy at the end
    dx,dy=math.cos(math.radians(ang)),math.sin(math.radians(ang)); L=46
    ex,ey=x+dx*L,y+dy*L; cx,cy=x+dx*(L+R-2),y+dy*(L+R-2)
    return (f'<path d="M{x-dx*6:.1f},{y-dy*6:.1f} L{ex:.1f},{ey:.1f}" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>'
            f'<path d="M{x-dx*6:.1f},{y-dy*6:.1f} L{ex:.1f},{ey:.1f}" stroke="{STICK}" stroke-width="5" stroke-linecap="round"/>'+candy(cx,cy,R,rot))
def face(kind="angry"):
    if kind=="angry":
        return (f'<path d="M116,96 L140,110 M184,94 L160,108" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
                f'<circle cx="134" cy="122" r="6" fill="{INK}"/><circle cx="166" cy="120" r="6" fill="{INK}"/>'
                f'<path d="M124,150 Q148,170 176,146" stroke="{INK}" stroke-width="6" fill="none" stroke-linecap="round"/>')
    if kind=="spin":
        return (f'<path d="M114,98 L140,112 M186,96 L160,110" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
                f'<circle cx="134" cy="124" r="7" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/><circle cx="135" cy="125" r="3" fill="{INK}"/><circle cx="166" cy="122" r="7" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/><circle cx="167" cy="123" r="3" fill="{INK}"/>'
                f'<path d="M126,146 Q150,174 178,144 Z" fill="#7A1E14" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/><path d="M134,148 L170,147" stroke="#FFFFFF" stroke-width="4"/>')
    if kind=="hit":
        return (f'<path d="M122,112 l18,16 M140,112 l-18,16 M158,110 l18,16 M176,110 l-18,16" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
                f'<path d="M134,156 Q150,144 166,156" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    if kind=="scared":
        return (f'<path d="M118,98 Q130,86 144,96 M156,96 Q170,86 182,98" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round"/>'
                f'<circle cx="134" cy="122" r="13" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/><circle cx="166" cy="120" r="13" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/><circle cx="134" cy="124" r="4" fill="{INK}"/><circle cx="166" cy="122" r="4" fill="{INK}"/>'
                f'<ellipse cx="150" cy="154" rx="9" ry="11" fill="#5A1E14" stroke="{INK}" stroke-width="4"/>')
def stick_body():
    r=random.Random(6)
    sp="".join(f'<circle cx="{r.uniform(136,164):.1f}" cy="{r.uniform(214,344):.1f}" r="{r.uniform(1,2):.1f}" fill="#A8A49B" opacity=".8"/>' for _ in range(26))
    return (f'<rect x="132" y="200" width="36" height="152" rx="5" fill="{STICK}" stroke="{INK}" stroke-width="5"/>'+sp
            +'<rect x="156" y="206" width="8" height="140" rx="3" fill="#BDB9B0" opacity=".8"/>')
def lolli(face_="angry", pose="rest", legs_="stand", rot=0, extra=""):
    l={"stand":gf.leg([(142,350),(140,386),(120,388)])+gf.leg([(160,350),(164,386),(184,386)]),
       "hop":gf.leg([(142,350),(134,372),(118,368)])+gf.leg([(160,350),(170,374),(186,376)]),
       "run":gf.leg([(142,350),(120,376),(106,368)])+gf.leg([(160,350),(184,380),(202,384)])}[legs_]
    if pose=="rest": a=gf.stick_arm(132,252,84,238,INK,5)+gf.stick_arm(168,252,216,238,INK,5)
    elif pose=="weapons": a=gf.stick_arm(132,250,86,250,INK,5)+gf.stick_arm(168,250,214,250,INK,5)+mini(86,250,180,24,30)+mini(214,250,0,24,-40)
    elif pose=="up": a=gf.stick_arm(132,246,90,196,INK,5)+gf.stick_arm(168,246,210,196,INK,5)
    elif pose=="down": a=gf.stick_arm(132,256,96,286,INK,5)+gf.stick_arm(168,256,204,286,INK,5)
    return l+stick_body()+a+candy(150,128,80,rot)+face(face_)+extra

def syrup(top_y, bottom_y, x0=88, x1=222, seed=1, gloss=True):
    # sticky red syrup blob covering the upper part of a figure, with drips running down
    r=random.Random(seed); n=7; d=f"M{x0},{top_y+30} Q{(x0+x1)/2:.0f},{top_y-30} {x1},{top_y+30}"
    xs=[x1-(x1-x0)*k/(n-1) for k in range(n)]
    for i,x in enumerate(xs):
        y=bottom_y if i%2==0 else bottom_y-r.uniform(30,60)
        y+=r.uniform(-14,14)
        d+=f" L{x+8:.0f},{y-30:.0f} Q{x+8:.0f},{y+10:.0f} {x:.0f},{y+10:.0f} Q{x-8:.0f},{y+10:.0f} {x-8:.0f},{y-30:.0f}"
    d+=" Z"
    s=f'<path d="{d}" fill="{SYR}" fill-opacity=".72" stroke="#A3202A" stroke-width="3.5" stroke-linejoin="round"/>'
    if gloss: s+=f'<path d="M{x0+18},{top_y+26} Q{(x0+x1)/2-10:.0f},{top_y-6} {x1-40},{top_y+14}" stroke="#FFFFFF" stroke-width="6" fill="none" stroke-linecap="round" opacity=".75"/>'
    return s
def drips_ground(n=4,seed=2):
    r=random.Random(seed)
    return "".join(f'<ellipse cx="{r.uniform(100,210):.0f}" cy="{r.uniform(384,404):.0f}" rx="{r.uniform(8,16):.0f}" ry="{r.uniform(3,5):.0f}" fill="{SYR}" fill-opacity=".8" stroke="#A3202A" stroke-width="2"/>' for _ in range(n))
def falling(x,y,s=1.0): return f'<path d="M{x},{y} q-6,10 0,14 q6,-4 0,-14 Z" transform="scale({s})" fill="{SYR}" stroke="#A3202A" stroke-width="2"/>'

ground=gf.ground
# ----- states
hero=wrap(gf.blob(60,.22)+lolli(), w=354, h=507, label="Lízátko")
walk=wrap(ground(48)+gf.g(lolli(legs_="hop"),"translate(0,-14) rotate(5 150 388)")+f'<path d="M100,404 q-10,-6 -18,0 M204,404 q10,-6 18,0" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round" opacity=".6"/>', label="Lízátko jde")
windup=wrap(ground()+lolli("spin","weapons",rot=0)+f'<path d="M40,170 q-14,40 6,80 M262,170 q14,40 -6,80" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round" stroke-dasharray="2 8"/>', vb="-30 0 360 430", label="Lízátko vytahuje lízátka")
def ghost_mini(ang):
    x=150+math.cos(math.radians(ang))*128; y=250+math.sin(math.radians(ang))*44
    return f'<g opacity=".35">{candy(x,y,22,ang)}</g>'
spin_fx=('<ellipse cx="150" cy="250" rx="140" ry="50" fill="none" stroke="#2B2118" stroke-width="4" stroke-dasharray="4 12" opacity=".7"/>'
         +"".join(ghost_mini(a) for a in (40,90,140,220,320))
         +f'<path d="M40,214 q-20,36 0,72 M262,214 q20,36 0,72" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round"/>'
         +gf.txt(178,58,"VŽUUUM!","#E0483F",36,8))
spin=wrap(ground(70)+gf.g(lolli("spin","weapons",rot=140),"rotate(-8 150 388)")+spin_fx, vb="-30 0 360 430", label="Lízátko se roztočí")
hit=wrap(ground()+gf.g(lolli("hit","down"),"translate(150,388) scale(1.1,.88) translate(-150,-388)")+star(250,90,16,"#FFFFFF")+gf.txt(30,90,"AU!","#D9342B",38,-10)
         +f'<path d="M190,82 l14,-14 M206,104 l18,-4" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>', label="Lízátko dostalo zásah")
run=wrap(ground()+gf.g(lolli("scared","up","run",extra=gf.sweat(236,110)+gf.sweat(248,140)),"translate(300,0) scale(-1,1) rotate(6 150 388)")
         +f'<path d="M232,250 l40,0 M236,280 l48,0 M228,310 l40,0" stroke="{INK}" stroke-width="3.5" stroke-linecap="round" opacity=".6"/>', label="Lízátko utíká")
dp=wrap(gf.path_tile()+gf.puff(98,320,1.0)+star(40,262,10)+star(150,262,8)
        +f'<path d="M110,290 Q160,120 240,80" stroke="#3D9BE0" stroke-width="3.5" fill="none" stroke-dasharray="3 10" stroke-linecap="round"/>'
        +gf.water_drop(196,176,2.0)+gf.sparkle(244,136,12)+gf.sparkle(150,130,9)
        +f'<text x="232" y="62" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="36" fill="#2D8CD6" stroke="{INK}" stroke-width="1.2">+25</text>', label="Kapka vody a puf")
# ----- defenders covered in syrup
tile_shadow=lambda: gen.tile()+'<ellipse cx="155" cy="388" rx="56" ry="12" fill="#3A2210" opacity=".18"/>'
def carrot_syrup(stage):
    if stage==0: return gen.carrot("frozen", extra_front=syrup(10,300,70,240,3)+falling(130,330)+falling(200,348))
    if stage==1: return gen.carrot("frozen", extra_front=syrup(150,320,96,214,5,False)+drips_ground(3)+falling(120,356))
    return gen.carrot("fight","slash")
def leek_syrup(stage):
    if stage==0: return gp.leek("frozen", front=syrup(30,300,82,224,7)+falling(104,330)+falling(196,344))
    return gp.leek("frozen", front=syrup(200,322,112,192,8,False)+drips_ground(3,4))
sy_full=wrap(tile_shadow()+carrot_syrup(0)+gf.txt(176,64,"PLÁC!","#E8424A",34,8)+'<path d="M40,120 l-16,-10 M258,120 l16,-10" stroke="#2B2118" stroke-width="4" stroke-linecap="round"/>', label="Mrkev oblepená šťávou")
sy_half=wrap(tile_shadow()+carrot_syrup(1)+f'<path d="M70,200 q-8,14 0,20 M236,220 q8,14 0,20" stroke="#A3202A" stroke-width="3" fill="none" stroke-linecap="round"/>', label="Šťáva stéká")
sy_done=wrap(tile_shadow()+drips_ground(5,9)+carrot_syrup(2)+gf.txt(190,78,"HOTOVO!","#F08A24",28,-6), vb="0 0 330 430", label="Mrkev zase bojuje")
leek_full=wrap(tile_shadow()+leek_syrup(0), label="Pórek oblepený šťávou")

parts=[("Hlava","bonbon se spirálou",wrap(candy(150,128,80)+face("angry"),vb="64 42 172 172",label="Hlava")),
       ("Obličej","4 výrazy",wrap(face("angry"),vb="108 86 84 86",label="Obličej")),
       ("Tyčka","tělo",wrap(stick_body(),vb="124 192 52 166",label="Tyčka")),
       ("Ruka","2×, paličková",wrap(gf.stick_arm(168,252,216,238,INK,5),vb="160 226 64 36",label="Ruka")),
       ("Nohy","krátké, poskakují",wrap(gf.leg([(142,350),(140,386),(120,388)])+gf.leg([(160,350),(164,386),(184,386)]),vb="112 344 80 50",label="Nohy")),
       ("Malá lízátka","zbraň při roztočení",wrap(mini(0,0,0,24,20),vb="-10 -30 100 60",label="Malé lízátko")),
       ("Sladká šťáva","oblepí obránce, stéká",wrap(syrup(30,150,0,140,2),vb="-10 -10 160 190",label="Sladká šťáva"))]
poses=[("Chůze","poskakuje, ~1 políčko/s",walk),("Nápřah","vytáhne malá lízátka",windup),
       ("Roztočení","1× za 6 s, zasáhne všechny obránce do ~1,5 políčka",spin),("Zásah","zmáčkne se, „au“",hit),
       ("Útěk","po 6 zásazích se otočí a utíká",run),("Kapka a puf","+25 vody, na okraji mapy puf",dp)]

# ----- in-game stage (top-down field, hex plots, the spin ring)
stage_over=('<ellipse cx="400" cy="335" rx="230" ry="138" fill="#E8424A" fill-opacity=".08" stroke="#E0483F" stroke-width="4" stroke-dasharray="14 10"/>'
            '<path d="M270,300 q-16,30 4,60 M530,300 q16,30 -4,60" stroke="#2B2118" stroke-width="5" fill="none" stroke-linecap="round"/>')
def page():
    psvg=lambda s,h=236: s.replace('<svg ',f'<svg height="{h}" style="max-width:100%" ',1).replace('style="display:block;overflow:visible"','',1)
    small=lambda svgsrc,left,top,w,h: f'<div style="position:absolute;left:{left}%;top:{top}px;width:{w}px;transform:translateX(-50%)">{psvg(svgsrc,h)}</div>'
    stage=(f'<svg viewBox="0 0 800 540" preserveAspectRatio="xMidYMid slice" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%">{gc.stage_svg()}</svg>'
           f'<svg viewBox="0 0 800 540" preserveAspectRatio="xMidYMid slice" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none">{stage_over}</svg>'
           + small(sy_full,28,70,150,190) + small(leek_full,72,40,150,200)
           + small(spin,50,220,260,280))
    chips="".join(chip(k,v) for k,v in [("Zásahů do útěku","6"),("Rychlost","~1 políčko/s"),("Roztočení","1× za 6 s"),("Voda",drop()+"25")])
    h=f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>Lízátko – list postavy</title>
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
<h1 style="margin:0;font-family:'Baloo 2',sans-serif;font-size:76px;font-weight:800;line-height:.95">Lízátko</h1>
<p style="margin:0;font-size:19px;font-weight:600;color:#5A4A3A;max-width:660px">Jednou za čas se roztočí s malými lízátky v rukou a zasáhne víc obránců najednou. Zasažená zelenina se oblepí sladkou šťávou a nebojuje, dokud z ní všechna šťáva neskape.</p>
</div>
<div style="display:flex;gap:16px">
{chips}
</div>
</div>
<div style="display:flex;gap:28px;height:540px">
<div style="{card};width:330px;box-sizing:border-box;padding:20px;display:flex;flex-direction:column;gap:12px">
<span style="font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Předloha</span>
<div style="flex:1;border-radius:12px;overflow:hidden;background:#EFE6DA">
<img src="/_blob/49cc33675ba0235d83ef42b01ef7c31d" alt="Dvě dětské kresby lízátka: v klidu a s malými lízátky v rukou" style="width:100%;height:100%;object-fit:contain;display:block">
</div>
<span style="font-size:15px;color:#5A4A3A;font-weight:600">kresby/utocnici/lizatko-zaklad.png a lizatko-utok.png · popis v „Lízátko.md“</span>
</div>
<div style="{card};flex:1;position:relative;overflow:hidden;background:#8BB85A">
{stage}
<span style="position:absolute;top:18px;left:22px;padding:4px 12px;background:rgba(255,255,255,.92);border:3px solid {INK};border-radius:12px;font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Ve hře</span>
<span style="position:absolute;top:22px;right:22px;padding:4px 10px;background:rgba(255,255,255,.92);border:2px solid {INK};border-radius:10px;font-size:14px;font-weight:800;color:#8A1A22">čárkovaně: dosah roztočení</span>
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
<div style="display:grid;grid-template-columns:repeat(6, minmax(0, 1fr));gap:20px">
'''
    for i,(t,ds,s) in enumerate(poses):
        bg="#FDECEC" if t in ("Nápřah","Roztočení") else "#FFFFFF"
        h+=f'''<div style="{card};background:{bg};padding:14px 12px 16px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{psvg(s)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800;line-height:1.1">{i+1}. {t}</span>
<span style="font-size:14px;font-weight:600;color:#5A4A3A;line-height:1.3">{ds}</span>
</div>
'''
    h+=f'''</div>
</div>
<div style="display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:26px;font-weight:800">Schopnost: sladká šťáva</span>
<div style="display:grid;grid-template-columns:repeat(5, minmax(0, 1fr));gap:20px">
'''
    fx=[("Oblepená","„Plác!“ celá v šťávě, nemůže sekat ani střílet",sy_full),("Šťáva stéká","kape dolů, zbývá jen spodní část",sy_half),("Zase bojuje","šťáva skapala, zůstaly jen loužičky",sy_done),("Pórek taky","oblepit jde každá vyrostlá zelenina v dosahu",leek_full)]
    for t,ds,s in fx:
        h+=f'''<div style="{card};background:#FDECEC;padding:14px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{psvg(s,240)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">{t}</span>
<span style="font-size:14px;font-weight:600;color:#5A4A3A;line-height:1.3">{ds}</span>
</div>
'''
    h+=f'''<div style="{card};padding:20px 22px;display:flex;flex-direction:column;gap:12px">
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Jak to funguje</span>
<span style="font-size:15px;font-weight:700;line-height:1.4">1× za 6 s se lízátko zastaví a roztočí. Všechna vyrostlá zelenina do ~1,5 políčka se oblepí.</span>
<span style="font-size:15px;font-weight:700;line-height:1.4">Šťáva stéká 3 s. Pak zelenina zase bojuje.</span>
<span style="font-size:15px;font-weight:700;line-height:1.4">Rostoucí zelenina je schovaná v zemi a oblepit nejde.</span>
<span style="font-size:13px;font-weight:700;color:#5A4A3A;line-height:1.35;margin-top:auto">Čísla jsou návrh pro první playtest.</span>
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
    open(f'{ROOT}/Lizatko.dc.html','w').write(h); print(len(h))
page()
