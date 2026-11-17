import math, random
import gen
from gen import INK, YEL, star, wrap, drop, chip, card
GREY="#4A4540"; BUN="#D9A55B"; BUND="#B9853F"
ROOT="/mnt/user-data/outputs/artifacts/0c045be6-49f0-4f56-9475-27d367f93a14/project"

def path_tile():
    return ('<polygon points="78,364 232,364 258,412 52,412" fill="#F4F1E8" stroke="#2B2118" stroke-width="4" stroke-linejoin="round"/>'
            '<path d="M86,372 L224,372 M64,402 L246,402" stroke="#D86B5A" stroke-width="4" stroke-dasharray="10 8"/>'
            '<polygon points="52,412 258,412 258,422 52,422" fill="#D8D2C2" stroke="#2B2118" stroke-width="4" stroke-linejoin="round"/>')
def blob(rx=56,op=.2): return f'<ellipse cx="150" cy="388" rx="{rx}" ry="12" fill="#3A2210" opacity="{op}"/>'
def ground(rx=56): return path_tile()+blob(rx)
def g(inner,t): return f'<g transform="{t}">{inner}</g>'

def water_drop(cx,cy,s=1.0):
    return g(f'<path d="M0,-30 C0,-30 -20,-4 -20,8 A20,20 0 0 0 20,8 C20,-4 0,-30 0,-30 Z" fill="#3D9BE0" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
             f'<path d="M-9,4 Q-9,-6 -3,-14" stroke="#CDEBFF" stroke-width="4" fill="none" stroke-linecap="round"/>',f'translate({cx},{cy}) scale({s})')
def sparkle(cx,cy,r=10,c="#FFFFFF"):
    return f'<path d="M{cx},{cy-r} Q{cx},{cy} {cx+r},{cy} Q{cx},{cy} {cx},{cy+r} Q{cx},{cy} {cx-r},{cy} Q{cx},{cy} {cx},{cy-r} Z" fill="{c}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
def puff(cx,cy,s=1.0):
    cs=[(-34,8,26),(0,-10,32),(34,6,26),(-12,20,24),(16,22,24)]
    a="".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFFFFF" stroke="{INK}" stroke-width="7"/>' for x,y,r in cs)
    b="".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFFFFF"/>' for x,y,r in cs)
    return g(a+b+'<path d="M-30,4 q8,-8 16,0 M8,-14 q8,-8 16,0" stroke="#D8D2C2" stroke-width="4" fill="none" stroke-linecap="round"/>',f'translate({cx},{cy}) scale({s})')
def stick_arm(x1,y1,x2,y2,c=INK,w=4.5):
    dx,dy=x2-x1,y2-y1; L=math.hypot(dx,dy); px,py=-dy/L*12,dx/L*12; tx,ty=x2-dx/L*8,y2-dy/L*8
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/><path d="M{tx-px:.1f},{ty-py:.1f} L{tx+px:.1f},{ty+py:.1f}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>'
def leg(pts): return f'<path d="M{" L".join(f"{x},{y}" for x,y in pts)}" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
def txt(x,y,t,c,size=34,rot=-8): return f'<text x="{x}" y="{y}" font-family="Bangers, Baloo 2, sans-serif" font-size="{size}" fill="{c}" stroke="{INK}" stroke-width="1.5" transform="rotate({rot} {x} {y})">{t}</text>'
def sweat(x,y): return f'<path d="M{x},{y} q-6,10 0,14 q6,-4 0,-14 Z" fill="#9AD4F5" stroke="{INK}" stroke-width="2.5"/>'

# ================= HAMBURGER =================
def speck(x0,x1,y0,y1,n,seed,c):
    r=random.Random(seed); return "".join(f'<circle cx="{r.uniform(x0,x1):.1f}" cy="{r.uniform(y0,y1):.1f}" r="{r.uniform(1,2):.1f}" fill="{c}" opacity=".7"/>' for _ in range(n))
def burger_body():
    s=[]
    s.append(f'<path d="M92,296 Q150,306 208,296 Q214,352 150,354 Q86,352 92,296 Z" fill="{BUN}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'+speck(100,200,310,345,18,1,BUND))
    s.append(f'<path d="M88,274 Q150,284 212,274 Q220,286 210,296 Q150,306 90,296 Q80,286 88,274 Z" fill="#7A3B22" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/><path d="M102,286 Q150,294 198,286" stroke="#A3573A" stroke-width="3" fill="none" stroke-linecap="round"/>')
    s.append(f'<path d="M92,256 Q150,266 208,256 L210,270 q-8,8 -16,2 q-8,8 -16,2 q-8,8 -16,2 q-8,8 -16,2 q-8,8 -16,2 q-8,8 -16,2 q-8,6 -14,0 Z" fill="#8CC63F" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>')
    s.append(f'<path d="M90,240 Q150,250 210,240 Q214,248 210,256 Q150,266 90,256 Q86,248 90,240 Z" fill="#D9342B" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>')
    s.append(f'<path d="M86,222 Q150,232 214,222 L216,236 L222,252 L206,240 Q150,250 88,240 Q82,232 86,222 Z" fill="#FFD23F" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>')
    s.append(f'<path d="M84,224 Q82,120 150,116 Q218,120 216,224 Q150,236 84,224 Z" fill="{BUN}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'+speck(100,200,140,215,22,2,BUND))
    s.append('<ellipse cx="150" cy="134" rx="40" ry="10" fill="#EBC27F" opacity=".9"/>')
    return "".join(s)
def burger_face(kind="angry"):
    if kind=="angry":
        return (f'<path d="M114,148 L140,162 M186,148 L160,162" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
                f'<circle cx="132" cy="178" r="11" fill="#E9C27F" stroke="{INK}" stroke-width="4"/><circle cx="168" cy="178" r="11" fill="#E9C27F" stroke="{INK}" stroke-width="4"/>'
                f'<circle cx="134" cy="180" r="4" fill="{INK}"/><circle cx="166" cy="180" r="4" fill="{INK}"/><circle cx="150" cy="194" r="3.5" fill="{INK}"/>')
    if kind=="hit":
        return (f'<path d="M122,170 l18,16 M140,170 l-18,16 M160,170 l18,16 M178,170 l-18,16" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
                f'<path d="M138,204 Q150,194 162,204" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round"/>')
    if kind=="scared":
        return (f'<path d="M116,150 Q128,138 142,148 M158,148 Q172,138 184,150" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round"/>'
                f'<circle cx="132" cy="176" r="14" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/><circle cx="168" cy="176" r="14" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/>'
                f'<circle cx="132" cy="178" r="4" fill="{INK}"/><circle cx="168" cy="178" r="4" fill="{INK}"/>'
                f'<ellipse cx="150" cy="206" rx="9" ry="11" fill="#5A1E14" stroke="{INK}" stroke-width="4"/>')
def burger(face="angry", arms="up", legs_="stand", extra=""):
    a={"up":stick_arm(90,190,50,146)+stick_arm(210,190,252,144),
       "flail":stick_arm(90,190,46,168)+stick_arm(210,190,250,120),
       "down":stick_arm(90,200,52,226)+stick_arm(210,200,248,226)}[arms]
    l={"stand":leg([(128,352),(124,388),(106,390)])+leg([(172,352),(176,388),(194,388)]),
       "step":leg([(128,352),(118,374),(100,372)])+leg([(172,352),(178,388),(196,388)]),
       "run":leg([(128,352),(104,378),(90,370)])+leg([(172,352),(196,384),(214,388)])}[legs_]
    return l+a+burger_body()+burger_face(face)+extra
motion=f'<path d="M70,300 l-8,30 M60,296 l-8,30 M230,300 l8,30 M240,296 l8,30" stroke="{BUND}" stroke-width="3.5" stroke-linecap="round"/>'

def hb_sheet():
    hero=wrap(blob(60,.22)+burger(extra=motion), w=354, h=507, label="Hamburger")
    walk=wrap(ground()+g(burger(legs_="step",extra=motion),"rotate(-5 150 388)")+txt(200,110,"ŤAP","#B5651D",26,8), label="Hamburger jde")
    hit=wrap(ground()+g(burger("hit","down"),"translate(150,388) scale(1.12,.86) translate(-150,-388)")
             +f'<path d="M226,236 q14,-24 30,-10 q10,16 -12,24 Z" fill="#D9342B" stroke="{INK}" stroke-width="3.5"/><path d="M238,206 q6,-10 12,0 q-6,8 -12,0 Z" fill="#D9342B" stroke="{INK}" stroke-width="3"/>'
             +star(62,140,18,"#FFFFFF")+txt(40,96,"AU!","#D9342B",38,-10), label="Hamburger dostal zásah")
    run=wrap(ground()+g(burger("scared","flail","run",extra=sweat(220,150)+sweat(236,180)),"translate(300,0) scale(-1,1) rotate(6 150 388)")
             +f'<path d="M232,250 l40,0 M236,280 l48,0 M228,310 l40,0" stroke="{INK}" stroke-width="3.5" stroke-linecap="round" opacity=".6"/>', label="Hamburger utíká")
    dropc=wrap(ground(40)+g(burger("scared","flail","run"),"translate(60,250) scale(.42)")
               +f'<path d="M120,320 Q170,120 250,70" stroke="#3D9BE0" stroke-width="3.5" fill="none" stroke-dasharray="3 10" stroke-linecap="round"/>'
               +water_drop(196,170,2.0)+sparkle(240,130,12)+sparkle(150,120,9)+sparkle(232,226,8)
               +f'<text x="226" y="58" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="36" fill="#2D8CD6" stroke="{INK}" stroke-width="1.2">+15</text>', label="Kapka vody")
    pf=wrap(path_tile()+puff(150,300,1.6)+star(70,200,14)+star(240,190,12)+star(220,350,10)+txt(118,170,"PUF!","#FFFFFF",44,-6), label="Hamburger zmizí v obláčku")
    big=wrap(path_tile()+blob(80,.22)+g(burger(),"translate(150,388) scale(1.3) translate(-150,-388)")
             +f'<g opacity=".35">{g(burger(),"translate(268,388) scale(.45) translate(-150,-388)")}</g>', vb="-20 -40 340 470", label="Velký hamburger")
    parts=[("Horní houska","s obočím a očima",wrap(burger_body().split('<path d="M84,224')[0][:0]+f'<path d="M84,224 Q82,120 150,116 Q218,120 216,224 Q150,236 84,224 Z" fill="{BUN}" stroke="{INK}" stroke-width="5"/>'+burger_face(),vb="78 110 144 130",label="Horní houska")),
           ("Sýr","s kapkou na boku",wrap(f'<path d="M86,222 Q150,232 214,222 L216,236 L222,252 L206,240 Q150,250 88,240 Q82,232 86,222 Z" fill="#FFD23F" stroke="{INK}" stroke-width="4.5"/>',vb="78 214 150 44",label="Sýr")),
           ("Rajče","",wrap(f'<path d="M90,240 Q150,250 210,240 Q214,248 210,256 Q150,266 90,256 Q86,248 90,240 Z" fill="#D9342B" stroke="{INK}" stroke-width="4.5"/>',vb="80 232 140 40",label="Rajče")),
           ("Salát","vlnitý okraj",wrap(f'<path d="M92,256 Q150,266 208,256 L210,270 q-8,8 -16,2 q-8,8 -16,2 q-8,8 -16,2 q-8,8 -16,2 q-8,8 -16,2 q-8,8 -16,2 q-8,6 -14,0 Z" fill="#8CC63F" stroke="{INK}" stroke-width="4.5"/>',vb="82 248 136 36",label="Salát")),
           ("Maso","",wrap(f'<path d="M88,274 Q150,284 212,274 Q220,286 210,296 Q150,306 90,296 Q80,286 88,274 Z" fill="#7A3B22" stroke="{INK}" stroke-width="5"/>',vb="76 266 150 46",label="Maso")),
           ("Spodní houska","",wrap(f'<path d="M92,296 Q150,306 208,296 Q214,352 150,354 Q86,352 92,296 Z" fill="{BUN}" stroke="{INK}" stroke-width="5"/>',vb="82 288 136 72",label="Spodní houska")),
           ("Ruka","2×, mává nad hlavou",wrap(stick_arm(90,190,50,146),vb="40 136 60 64",label="Ruka")),
           ("Nohy","ťap ťap",wrap(leg([(128,352),(124,388),(106,390)])+leg([(172,352),(176,388),(194,388)]),vb="98 346 104 50",label="Nohy")),
           ("Kapka vody","upustí při útěku",wrap(water_drop(0,0,1.0),vb="-26 -36 52 66",label="Kapka vody"))]
    poses=[("Chůze","ťap ťap, ~1 políčko za 1 s",walk),("Zásah","zmáčkne se, cákne kečup, „au“",hit),
           ("Útěk","po 4 zásazích se otočí a utíká",run),("Kapka vody","+15 vody, sama odletí do počítadla",dropc),
           ("Puf","na okraji mapy zmizí v obláčku",pf),("Velký hamburger","konec vlny 4: 1,5× větší, 7 zásahů, +40",big)]
    return dict(file="Hamburger.dc.html",title="Hamburger",kicker="Fast Food Fight · útočník · 1. úroveň",accent="#9A5416",
        desc="Úplně základní útočník. Na nikoho neútočí, jen ťapká po cestě k puse. Po 4 zásazích se otočí, uteče a nechá kapku vody.",
        chips=[("Zásahů do útěku","4"),("Rychlost","~1 políčko/s"),("Útok","žádný"),("Voda", drop()+"15")],
        img="/_blob/542a4b7ffafb2973f26697e63f3bcc6c",alt="Dětská kresba: naštvaný hamburger se zdviženýma rukama",src="kresby/utocnici/hamburger.png",
        hero=hero,parts=parts,poses=poses,paper="#FBF1E4",stage_extra="")

# ================= HRANOLKY =================
def fries_back():
    r=random.Random(4); s=[]
    xs=[96,110,124,138,152,166,180,194]
    for i,x in enumerate(xs):
        top=r.uniform(100,140); a=r.uniform(-6,6)
        s.append(f'<g transform="rotate({a:.1f} {x+7} 220)"><rect x="{x}" y="{top:.0f}" width="15" height="{220-top:.0f}" fill="#FFD54A" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/><path d="M{x+4},{top+8:.0f} L{x+4},{top+40:.0f}" stroke="#FFF1A8" stroke-width="3" stroke-linecap="round"/></g>')
    return "".join(s)
def box(tint=None):
    r=random.Random(8)
    sp="".join(f'<circle cx="{r.uniform(100,200):.1f}" cy="{r.uniform(220,335):.1f}" r="{r.uniform(1,2):.1f}" fill="#B52A22" opacity=".7"/>' for _ in range(28))
    return (f'<path d="M88,188 Q150,236 212,188 L202,342 Q150,354 98,342 Z" fill="#E2453A" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'+sp
            +f'<path d="M190,214 L184,340" stroke="#C0352C" stroke-width="10" opacity=".6" stroke-linecap="round"/>')
def fries_face(kind="angry"):
    eye=lambda x: f'<ellipse cx="{x}" cy="264" rx="10" ry="13" fill="#FFFFFF" stroke="{INK}" stroke-width="3.5"/><circle cx="{x}" cy="265" r="6" fill="#3A7CC2"/><circle cx="{x}" cy="266" r="2.6" fill="{INK}"/>'
    if kind=="angry":
        return f'<path d="M120,238 L144,250 M180,238 L156,250" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'+eye(134)+eye(166)+f'<circle cx="150" cy="282" r="3.2" fill="{INK}"/><path d="M138,298 Q150,308 162,298 Z" fill="#3A1410" stroke="{INK}" stroke-width="3"/>'
    if kind=="throw":
        return f'<path d="M118,236 L144,252 M182,236 L156,252" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'+eye(134)+eye(166)+f'<circle cx="150" cy="282" r="3.2" fill="{INK}"/><path d="M134,296 L166,296 L160,308 L140,308 Z" fill="#FFFFFF" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/><path d="M142,296 L142,308 M150,296 L150,308 M158,296 L158,308" stroke="{INK}" stroke-width="2"/>'
    if kind=="hit":
        return f'<path d="M124,256 l18,16 M142,256 l-18,16 M158,256 l18,16 M176,256 l-18,16" stroke="{INK}" stroke-width="5" stroke-linecap="round"/><path d="M138,302 Q150,292 162,302" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
    if kind=="scared":
        return (f'<path d="M120,240 Q130,230 144,238 M156,238 Q170,230 180,240" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round"/>'
                f'<circle cx="134" cy="264" r="14" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/><circle cx="166" cy="264" r="14" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/><circle cx="134" cy="266" r="4" fill="{INK}"/><circle cx="166" cy="266" r="4" fill="{INK}"/>'
                f'<ellipse cx="150" cy="300" rx="9" ry="11" fill="#3A1410" stroke="{INK}" stroke-width="4"/>')
def big_fry(): return f'<rect x="-9" y="-104" width="18" height="108" fill="#FFD54A" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/><path d="M-3,-94 L-3,-50" stroke="#FFF1A8" stroke-width="3.5" stroke-linecap="round"/>'
def fries(face="angry", pose="stand", extra=""):
    l={"stand":leg([(128,346),(128,382),(110,384)])+leg([(172,346),(174,382),(192,382)]),
       "hop":leg([(128,346),(122,370),(106,366)])+leg([(172,346),(180,370),(196,372)]),
       "run":leg([(128,346),(106,372),(92,364)])+leg([(172,346),(194,380),(212,384)])}[pose if pose in("stand","hop","run") else "stand"]
    if pose in("stand","hop"):
        a=stick_arm(90,262,48,262,GREY,5)+stick_arm(210,262,252,258,GREY,5)+g(big_fry(),"translate(48,262)")
    elif pose=="windup":
        a=stick_arm(90,262,48,266,GREY,5)+stick_arm(210,258,236,196,GREY,5)+g(big_fry(),"translate(236,196) rotate(-60)")
    elif pose=="thrown":
        a=stick_arm(90,262,48,266,GREY,5)+stick_arm(210,258,256,250,GREY,5)
    elif pose=="hit":
        a=stick_arm(90,262,52,286,GREY,5)+stick_arm(210,262,248,286,GREY,5)
    else:
        a=stick_arm(90,262,46,220,GREY,5)+stick_arm(210,262,254,214,GREY,5)
    return l+fries_back()+box()+fries_face(face)+a+extra

def hr_sheet():
    hero=wrap(blob(60,.22)+fries(), w=354, h=507, label="Hranolky")
    walk=wrap(ground(48)+g(fries(pose="hop"),"translate(0,-18) rotate(4 150 388)")+f'<path d="M100,404 q-10,-6 -18,0 M204,404 q10,-6 18,0" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round" opacity=".6"/>', label="Hranolky jdou")
    wind=wrap(ground()+fries("throw","windup")+f'<path d="M206,120 q30,-6 44,18" stroke="{INK}" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-dasharray="3 8"/>', label="Hranolky se napřahují")
    throw=wrap(ground()+fries("throw","thrown")
               +f'<path d="M256,240 Q320,110 392,250" stroke="{INK}" stroke-width="3.5" fill="none" stroke-dasharray="3 10" stroke-linecap="round"/>'
               +g(big_fry(),"translate(320,150) rotate(60) scale(.8)")
               +f'<path d="M370,262 l-12,-12 M392,256 l0,-18 M412,264 l12,-12 M372,282 l-16,4 M412,282 l16,4" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>'
               +txt(330,316,"PLESK!","#FFD54A",32,-6), vb="0 0 440 430", label="Hranolky hází hranolku")
    hit=wrap(ground()+g(fries("hit","hit"),"translate(150,388) scale(1.12,.86) translate(-150,-388)")
             +g(f'<rect x="0" y="0" width="13" height="50" fill="#FFD54A" stroke="{INK}" stroke-width="3.5"/>',"translate(70,70) rotate(-30)")
             +g(f'<rect x="0" y="0" width="13" height="46" fill="#FFD54A" stroke="{INK}" stroke-width="3.5"/>',"translate(222,60) rotate(28)")
             +star(250,150,16,"#FFFFFF")+txt(36,170,"AU!","#D9342B",38,-10), label="Hranolky dostaly zásah")
    run=wrap(ground()+g(fries("scared","run",extra=sweat(214,226)+sweat(226,256)),"translate(300,0) scale(-1,1) rotate(6 150 388)")
             +f'<path d="M234,250 l40,0 M238,280 l48,0 M230,310 l40,0" stroke="{INK}" stroke-width="3.5" stroke-linecap="round" opacity=".6"/>', label="Hranolky utíkají")
    dp=wrap(path_tile()+puff(98,320,1.0)+star(40,262,10)+star(150,262,8)
            +f'<path d="M110,290 Q160,120 240,80" stroke="#3D9BE0" stroke-width="3.5" fill="none" stroke-dasharray="3 10" stroke-linecap="round"/>'
            +water_drop(196,176,2.0)+sparkle(244,136,12)+sparkle(150,130,9)
            +f'<text x="232" y="62" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="36" fill="#2D8CD6" stroke="{INK}" stroke-width="1.2">+20</text>', label="Kapka vody a puf")
    parts=[("Krabička","s obličejem",wrap(box()+fries_face(),vb="80 180 140 180",label="Krabička")),
           ("Hranolky","8 kusů, poskakují",wrap(fries_back(),vb="86 92 128 132",label="Hranolky")),
           ("Obličej","4 výrazy",wrap(fries_face(),vb="110 228 80 86",label="Obličej")),
           ("Ruka","2×, šedá paličková",wrap(stick_arm(210,262,252,258,GREY,5),vb="200 236 64 44",label="Ruka")),
           ("Nohy","krátké, poskakují",wrap(leg([(128,346),(128,382),(110,384)])+leg([(172,346),(174,382),(192,382)]),vb="102 340 98 52",label="Nohy")),
           ("Hranolka na hod","letí a „plesk“",wrap(big_fry(),vb="-16 -110 32 120",label="Hranolka na hod"))]
    poses=[("Chůze","krabička poskakuje, ~1,3 políčka/s",walk),("Nápřah","jednou za 5 s, cíl do ~2,5 políčka",wind),
           ("Hod","plesk! obránce na 2 s ztuhne",throw),("Zásah","zmáčknutí, vypadnou hranolky",hit),
           ("Útěk","po 5 zásazích se otočí a utíká",run),("Kapka a puf","+20 vody, na okraji mapy puf",dp)]
    return dict(file="Hranolky.dc.html",title="Hranolky",kicker="Fast Food Fight · útočník · od 3. vlny",accent="#C0352C",
        desc="Útočník se schopností: hází hranolkou po nejbližším vyrostlém obránci a ten na chvilku ztuhne. Po 5 zásazích uteče a nechá kapku vody.",
        chips=[("Zásahů do útěku","5"),("Rychlost","~1,3 políčka/s"),("Hod","1× za 5 s"),("Voda", drop()+"20")],
        img="/_blob/ad67a1a011c8fbd672b015af4898c1d7",alt="Dětská kresba: naštvaná krabička hranolek s velkou hranolkou v ruce",src="kresby/utocnici/hranolky.png",
        hero=hero,parts=parts,poses=poses,paper="#FFF1EC",
        stage_extra='<ellipse cx="400" cy="455" rx="260" ry="62" fill="#E2453A" fill-opacity=".07" stroke="#E2453A" stroke-width="3" stroke-dasharray="12 9"/>')

def page(d):
    stage_bg=('<svg viewBox="0 0 800 540" preserveAspectRatio="none" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%">'
      '<polygon points="150,150 650,150 800,540 0,540" fill="#E9C99A"/>'
      + "".join(f'<path d="M{150-150*t:.0f},{150+390*t:.0f} L{650+150*t:.0f},{150+390*t:.0f}" stroke="#C9A06C" stroke-width="2"/>' for t in [0.18,0.4,0.66])
      + '<path d="M150,150 L650,150" stroke="#2B2118" stroke-width="3"/>'
      '<polygon points="340,150 460,150 610,540 190,540" fill="#F4F1E8" stroke="#2B2118" stroke-width="3"/>'
      '<path d="M360,150 L232,540 M440,150 L568,540" stroke="#D86B5A" stroke-width="5" stroke-dasharray="14 10"/>'
      + d["stage_extra"] +
      '<path d="M385,190 L400,205 L415,190 M380,232 L400,252 L420,232" stroke="#2B2118" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity=".35"/>'
      '<polygon points="80,300 240,300 222,400 30,400" fill="#B87A45" stroke="#2B2118" stroke-width="3" opacity=".55"/>'
      '<polygon points="560,300 720,300 770,400 578,400" fill="#B87A45" stroke="#2B2118" stroke-width="3" opacity=".55"/>'
      '</svg>')
    chips="".join(chip(k,v) for k,v in d["chips"])
    h=f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>{d["title"]} – list postavy</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&amp;family=Bangers&amp;family=Nunito:wght@500;700;800&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#9A5416}}a:hover{{color:#6E3A0E}}
</style>
</helmet>
<div style="width:1680px;height:1280px;box-sizing:border-box;padding:48px 56px;background:{{{{paper}}}};font-family:Nunito,sans-serif;color:{INK};display:flex;flex-direction:column;gap:32px">
<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:32px">
<div style="display:flex;flex-direction:column;gap:6px">
<span style="font-size:16px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:{d["accent"]}">{d["kicker"]}</span>
<h1 style="margin:0;font-family:'Baloo 2',sans-serif;font-size:76px;font-weight:800;line-height:.95">{d["title"]}</h1>
<p style="margin:0;font-size:19px;font-weight:600;color:#5A4A3A;max-width:640px">{d["desc"]}</p>
</div>
<div style="display:flex;gap:16px">
{chips}
</div>
</div>
<div style="display:flex;gap:28px;height:540px">
<div style="{card};width:330px;box-sizing:border-box;padding:20px;display:flex;flex-direction:column;gap:12px">
<span style="font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Předloha</span>
<div style="flex:1;border-radius:12px;overflow:hidden;background:#EEE">
<img src="{d["img"]}" alt="{d["alt"]}" style="width:100%;height:100%;object-fit:contain;display:block;background:#EFE6DA">
</div>
<span style="font-size:15px;color:#5A4A3A;font-weight:600">{d["src"]}</span>
</div>
<div style="{card};flex:1;position:relative;display:flex;align-items:center;justify-content:center;background:{{{{stage}}}};overflow:hidden">
{stage_bg}
<div style="position:relative;margin-top:-10px">{d["hero"]}</div>
<span style="position:absolute;top:20px;left:24px;font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Ve hře</span>
<span style="position:absolute;top:24px;right:24px;font-size:15px;font-weight:700;color:#5A4A3A">kamera shora a z boku (~55°), jde po cestě k puse</span>
</div>
<div style="{card};width:440px;box-sizing:border-box;padding:20px;display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Díly loutky</span>
<div style="display:grid;grid-template-columns:repeat(3, minmax(0, 1fr));gap:10px;flex:1">
'''
    for t,ds,s in d["parts"]:
        h+=f'''<div style="border:2px dashed #BFAE98;border-radius:14px;padding:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px">
<div style="height:70px;width:100%;display:flex;align-items:center;justify-content:center">{s.replace('<svg ','<svg height="62" style="max-width:100%" ',1).replace('style="display:block;overflow:visible"','',1)}</div>
<span style="font-weight:800;font-size:15px;text-align:center">{t}</span>
{f'<span style="font-size:12px;color:#5A4A3A;font-weight:600;text-align:center;line-height:1.25">{ds}</span>' if ds else ''}
</div>
'''
    h+=f'''</div>
</div>
</div>
<div style="display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:26px;font-weight:800">Stavy a animace</span>
<div style="display:grid;grid-template-columns:repeat({len(d["poses"])}, minmax(0, 1fr));gap:20px">
'''
    for i,(t,ds,s) in enumerate(d["poses"]):
        h+=f'''<div style="{card};padding:14px 12px 16px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{s.replace('<svg ','<svg height="236" style="max-width:100%" ',1).replace('style="display:block;overflow:visible"','',1)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800;line-height:1.1">{i+1}. {t}</span>
<span style="font-size:14px;font-weight:600;color:#5A4A3A;line-height:1.3">{ds}</span>
</div>
'''
    h+=f'''</div>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"paper":{{"editor":"color","default":"{d["paper"]}"}},"stage":{{"editor":"color","default":"#DDF0F7"}},"$preview":{{"width":1680,"height":1280}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{ paper: this.props.paper ?? '{d["paper"]}', stage: this.props.stage ?? '#DDF0F7' }};
}}
}}
</script>
</body>
</html>
'''
    open(f'{ROOT}/{d["file"]}','w').write(h); print(d["file"],len(h))

page(hb_sheet()); page(hr_sheet())
