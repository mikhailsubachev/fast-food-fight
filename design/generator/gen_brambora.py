"""
Pan Brambora – list postavy (podle dětské kresby kresby/obranci/Brambora.png a popisu v Brambora.md).

Brambora s hnědými očky (bez klíčků), malými nožičkami a velkým štítem z bramborové slupky.
Jako jediný se staví přímo na cestu: fast food do jeho štítu naráží a nemůže projít, dokud
Panu Bramborovi nedojdou srdíčka. Pak se rozpadne na malé hranolky. Nekupuje se za vodu:
hráč má na začátku 2 brambory a další dostane, když mu na konci úrovně zbyde přes 1000 kapek.

Kreslí ve stejném rámečku jako ostatní postavy (300 × 430, chodidla na 150, 388), takže
ho tools/export_postavy.py může vyexportovat jako obrázky pro hru.

Spuštění z kořene repozitáře:  python3 design/generator/gen_brambora.py
Zapíše design/zdroj/Brambora.dc.html (list pro plátno) a design/artboardy/26-brambora.html.
"""
import builtins
import io
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))


def _quiet_import():
    """gen a gen_ff při načtení zapisují své listy jinam; tady se ty zápisy zahodí."""
    real_open, real_makedirs, out = builtins.open, os.makedirs, sys.stdout

    def quiet_open(file, mode="r", *a, **k):
        if any(m in mode for m in "wax"):
            return io.StringIO()
        return real_open(file, mode, *a, **k)

    builtins.open, os.makedirs, sys.stdout = quiet_open, (lambda *a, **k: None), io.StringIO()
    sys.path.insert(0, HERE)
    try:
        import gen as g0
        import gen_ff as g1
    finally:
        builtins.open, os.makedirs, sys.stdout = real_open, real_makedirs, out
    return g0, g1


gen, gf = _quiet_import()
INK, YEL, star, wrap, drop, chip, card = gen.INK, gen.YEL, gen.star, gen.wrap, gen.drop, gen.chip, gen.card

SKIN = "#E6C48A"
SKIN2 = "#D2A464"
SPOT = "#9A6234"
SHIELD = "#C98B57"
SHIELD2 = "#E8B08A"
FRY = "#FFD54A"
BODY = (
    "M164,146 C214,148 240,206 238,264 C236,328 206,362 162,362 "
    "C118,362 90,330 88,266 C86,206 112,144 164,146 Z"
)
SPOTS = [(140, 176), (176, 170), (204, 206), (120, 214), (212, 262), (130, 290), (176, 300),
         (204, 318), (112, 252), (150, 334)]


# ---------------------------------------------------------------- díly ----------

def sprouts():
    """Tři klíčky navrchu (na kresbě hnědé čárky)."""
    return "".join(
        f'<path d="M{x},{y} q{dx * 0.4:.0f},-12 {dx},-26" stroke="#B88A4A" stroke-width="5" fill="none" stroke-linecap="round"/>'
        f'<circle cx="{x + dx}" cy="{y - 26}" r="4.5" fill="#A8D46A" stroke="{INK}" stroke-width="2.5"/>'
        for x, y, dx in [(148, 150, -8), (164, 146, 2), (180, 150, 10)]
    )


def body(cracks=0, tint=None, shine=False):
    s = [f'<path d="{BODY}" fill="{SKIN}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>',
         '<path d="M206,180 C232,220 236,266 230,304 C222,342 196,356 172,360 C208,328 222,260 206,180 Z" fill="#D2A464" opacity=".6"/>']
    r = random.Random(4)
    s.append("".join(f'<path d="M{r.uniform(100, 226):.0f},{r.uniform(170, 346):.0f} l{r.uniform(-3, 3):.0f},9" stroke="#C99E5E" stroke-width="2.2" stroke-linecap="round"/>' for _ in range(22)))
    s.append("".join(f'<ellipse cx="{x}" cy="{y}" rx="7.5" ry="6" fill="none" stroke="{SPOT}" stroke-width="3.5"/>' for x, y in SPOTS))
    if cracks >= 1:
        s.append(f'<path d="M206,186 l-14,18 l10,8 l-16,22" stroke="{INK}" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    if cracks >= 2:
        s.append(f'<path d="M104,292 l18,-6 l-6,14 l20,-4" stroke="{INK}" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                 f'<path d="M178,350 l-6,-16 l12,-6" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round"/>')
    if tint == "ice":
        s.append(f'<path d="{BODY}" fill="#8FD0F2" opacity=".5"/>')
    if shine:
        s.append('<path d="M108,212 Q98,262 114,312" stroke="#FFFFFF" stroke-width="7" fill="none" opacity=".85" stroke-linecap="round"/>')
    return "".join(s)


def face(kind="smile"):
    e = lambda x, y, r=8.5: f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INK}"/>'  # noqa: E731
    if kind == "smile":
        return e(152, 228) + e(186, 224) + f'<path d="M150,258 Q170,274 192,252" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    if kind == "closed":
        return (f'<path d="M142,229 Q152,236 162,229 M176,225 Q186,232 196,225" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
                f'<path d="M154,258 Q170,268 188,256" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round"/>')
    if kind == "brace":  # zapře se: odhodlané obočí, zaťaté zuby
        return (f'<path d="M138,210 L162,220 M200,206 L178,216" stroke="{INK}" stroke-width="5.5" stroke-linecap="round"/>'
                + e(152, 230, 7.5) + e(186, 226, 7.5)
                + f'<rect x="150" y="250" width="40" height="15" rx="6" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/>'
                f'<path d="M160,250 v15 M170,250 v15 M180,250 v15" stroke="{INK}" stroke-width="2.5"/>')
    if kind == "ouch":
        return (f'<path d="M142,222 l16,8 l-16,8 M196,218 l-16,8 l16,8" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                f'<ellipse cx="170" cy="260" rx="11" ry="9" fill="#5A1E14" stroke="{INK}" stroke-width="4"/>')
    if kind == "worried":
        return (f'<path d="M140,214 L160,210 M180,206 L200,210" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/>'
                + e(152, 230, 7) + e(186, 226, 7)
                + f'<path d="M152,264 Q170,252 190,262" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round"/>'
                + gf.sweat(212, 204))
    if kind == "joy":
        return (f'<path d="M142,232 L152,220 L162,232 M176,228 L186,216 L196,228" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                f'<path d="M148,250 Q170,282 194,248 Z" fill="#8A2B1E" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    if kind == "frozen":
        return (f'<path d="M142,228 L162,228 M176,224 L196,224" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
                f'<path d="M150,258 l6,-5 l6,5 l6,-5 l6,5 l6,-5 l6,5" stroke="{INK}" stroke-width="3.5" fill="none" stroke-linejoin="round"/>')
    return ""


def legs(wide=False):
    if wide:
        return gf.leg([(142, 358), (126, 384), (108, 388)]) + gf.leg([(186, 356), (200, 384), (218, 386)])
    return gf.leg([(146, 360), (140, 386), (124, 389)]) + gf.leg([(180, 358), (184, 386), (200, 387)])


def shield_local():
    """Štít z bramborové slupky: vysoký ovál s rukojetí, střed (0, 0)."""
    return (f'<rect x="-18" y="-118" width="36" height="236" rx="18" fill="{SHIELD}" stroke="{INK}" stroke-width="6"/>'
            f'<rect x="-9" y="-100" width="18" height="200" rx="9" fill="{SHIELD2}" opacity=".85"/>'
            f'<path d="M-4,-84 Q-6,-20 -4,40" stroke="#FFFFFF" stroke-width="4" fill="none" opacity=".6" stroke-linecap="round"/>'
            + "".join(f'<ellipse cx="{x}" cy="{y}" rx="4" ry="3.5" fill="none" stroke="#8A5530" stroke-width="2.2"/>' for x, y in [(4, -60), (-3, 10), (5, 70)]))


def shield(x, y, rot=0, sc=1.0):
    return f'<g transform="translate({x},{y}) rotate({rot}) scale({sc})">{shield_local()}</g>'


def arm(x1, y1, x2, y2):
    return gf.stick_arm(x1, y1, x2, y2, "#3A3530", 5)


def potato(face_="smile", pose="rest", cracks=0, tint=None, shine=False, front="", back=""):
    """
    Celý Pan Brambora. pose: rest (štít vedle sebe), brace (štít před sebou, zapřený),
    up (ruce nahoře, štít zvednutý), hit (zakymácí se).
    """
    if pose == "rest":
        sh = shield(70, 262, -4)
        handle = f'<ellipse cx="88" cy="250" rx="10" ry="18" fill="none" stroke="{INK}" stroke-width="5"/>'
        a = arm(98, 252, 84, 252) + arm(234, 262, 262, 230)
        return back + legs() + sh + handle + body(cracks, tint, shine) + face(face_) + a + front
    if pose == "brace":
        sh = shield(70, 270, -10)
        a = arm(100, 236, 80, 228) + arm(100, 286, 82, 296)
        return back + legs(wide=True) + body(cracks, tint, shine) + face(face_) + a + sh + front
    if pose == "up":
        sh = shield(52, 170, -22, 0.9)
        a = arm(100, 236, 70, 196) + arm(232, 236, 266, 176)
        return back + legs() + sh + body(cracks, tint, shine) + face(face_) + a + front
    if pose == "hit":
        sh = shield(66, 270, -16)
        a = arm(98, 252, 84, 256) + arm(232, 250, 262, 222)
        return back + legs() + '<g transform="rotate(8 160 380)">' + sh + body(cracks, tint, shine) + face(face_) + a + "</g>" + front
    return ""


def small_fry(x, y, rot, L=46):
    return (f'<g transform="translate({x},{y}) rotate({rot})"><rect x="-6" y="{-L / 2:.0f}" width="12" height="{L}" rx="3" fill="{FRY}" stroke="{INK}" stroke-width="3.5"/>'
            f'<path d="M-1,{-L / 2 + 6:.0f} L-1,{L / 2 - 8:.0f}" stroke="#FFF1A8" stroke-width="2.5" stroke-linecap="round"/></g>')


def crumble():
    """Rozpad: hromádka malých hranolek, kousky slupky, spadlý štít a obláček."""
    fries = [(110, 360, -30), (132, 372, 12), (156, 354, -6), (178, 370, 28), (200, 356, -18), (124, 340, 58),
             (170, 336, -44), (214, 374, 74), (146, 382, 86), (190, 384, -80)]
    peel = "".join(f'<path d="M{x},{y} q10,-8 20,0 q-10,6 -20,0 Z" fill="{SKIN2}" stroke="{INK}" stroke-width="3"/>' for x, y in [(96, 384), (226, 344), (236, 384)])
    return (gf.puff(160, 300, 1.25) + shield(150, 392, -86, 0.5) + "".join(small_fry(*f) for f in fries) + peel
            + gf.txt(176, 214, "KRACH!", "#E07A1F", 40, 8))


def path_tile():
    return gf.path_tile() + gf.blob(66)


# ---------------------------------------------------------------- pózy ----------

hero = wrap(path_tile() + potato("smile"), w=354, h=507, label="Pan Brambora")
dust = (gf.puff(84, 378, 0.55) + gf.puff(228, 380, 0.5)
        + f'<path d="M150,60 l0,40 M136,66 l6,26 M164,66 l-6,26" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
place = wrap(path_tile() + '<g transform="translate(0,-14)">' + potato("joy", "up") + "</g>" + dust,
             vb="0 30 300 410", label="Pan Brambora skočí na cestu")
idle = wrap(path_tile() + '<g transform="rotate(-2 150 380)">' + potato("smile") + "</g>", label="Pan Brambora v klidu")
bump = (gen.star(48, 230, 26) + gf.txt(14, 160, "BUM!", "#E07A1F", 38, -10)
        + f'<path d="M22,280 l-14,4 M22,300 l-16,0 M24,320 l-14,-4" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
brace = wrap(path_tile() + potato("brace", "brace", front=bump), vb="-20 0 320 430", label="Pan Brambora drží štít")
hit = wrap(path_tile() + potato("ouch", "hit", cracks=1, front=small_fry(36, 214, -40) + gen.star(70, 236, 16)),
           vb="-10 0 310 430", label="Zásah hranolkou")
cracked = wrap(path_tile() + potato("worried", "brace", cracks=2), vb="-20 0 320 430", label="Pan Brambora je pocuchaný")
crumbled = wrap(path_tile() + crumble(), vb="0 140 300 290", label="Pan Brambora se rozpadne na hranolky")
joy = wrap(path_tile().replace('rx="66"', 'rx="44"') + '<g transform="translate(0,-24)">'
           + potato("joy", "up", front=star(268, 124, 14) + star(276, 300, 12) + star(30, 300, 10)) + "</g>",
           vb="0 -10 300 440", label="Pan Brambora se raduje")

parts = [("Tělo", "brambora s hnědými očky", wrap(body(), vb="80 136 166 234", label="Tělo")),
         ("Obličej", "5 výrazů", wrap(face("smile"), vb="136 210 64 72", label="Obličej")),
         ("Štít", "ze slupky, drží ho v ruce", wrap(shield_local(), vb="-28 -128 56 256", label="Štít")),
         ("Nohy", "krátké, při nárazu se rozkročí", wrap(legs(), vb="116 352 92 42", label="Nohy")),
         ("Praskliny", "čím míň srdíček, tím víc", wrap(body(2), vb="80 136 166 234", label="Praskliny")),
         ("Hranolky", "na ně se rozpadne", wrap("".join(small_fry(*f) for f in [(20, 40, -20), (44, 44, 14), (68, 38, -8)]),
                                               vb="0 0 90 80", label="Malé hranolky"))]
poses = [("Na cestu", "hráč ho postaví přímo na cestu, „hop!“", place),
         ("Klid", "stojí na cestě se štítem", idle),
         ("Náraz", "fast food narazí do štítu: „BUM!“, Brambora se zapře", brace),
         ("Zásah", "hranolka ho trefí, přijde o srdíčko", hit),
         ("Pocuchaný", "málo srdíček: praskliny a pot", cracked),
         ("Rozpad", "bez srdíček se rozpadne na malé hranolky", crumbled),
         ("Radost", "výskok, když fast food uteče", joy)]


# ---------------------------------------------------------------- schopnost ----------

def hearts(x, y, n, full, s=1.0):
    path = "M12 21 C12 21 2 14.6 2 8.2 A5 5 0 0 1 12 5.6 A5 5 0 0 1 22 8.2 C22 14.6 12 21 12 21 Z"
    w = n * 26 + 10
    out = [f'<rect x="{-w / 2}" y="-4" width="{w}" height="32" rx="10" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/>']
    for i in range(n):
        on = i < full
        dash = "" if on else 'stroke-dasharray="3 2.4"'
        out.append(f'<path transform="translate({-w / 2 + 6 + i * 26},0)" d="{path}" fill="{"#E2463A" if on else "#FFFFFF"}" '
                   f'stroke="{INK if on else "#A39A8E"}" stroke-width="2.4" {dash}/>')
    return f'<g transform="translate({x},{y}) scale({s})">{"".join(out)}</g>'


burger_push = gf.burger("angry", "up", "stand")
fx_bump = wrap(gf.ground() + gf.g(burger_push, "translate(-70,0)") + gf.g(potato("brace", "brace"), "translate(80,0)")
               + gen.star(118, 250, 22) + gf.txt(70, 140, "BUM!", "#E07A1F", 40, -8) + hearts(232, 96, 10, 7, 0.8),
               vb="-30 40 400 390", label="Hamburger narazí do štítu")
fx_crumble = wrap(gf.ground() + crumble() + gf.g(gf.burger("angry", "up", "stand"), "translate(250,150) scale(0.62)"),
                  vb="0 140 420 290", label="Pan Brambora se rozpadne na hranolky")


def stage_svg():
    W_, H_ = 800, 540
    s = [f'<rect width="{W_}" height="{H_}" fill="#8BB85A"/>']
    r = random.Random(11)
    for _ in range(90):
        x, y = r.uniform(0, W_), r.uniform(0, H_)
        s.append(f'<path d="M{x:.0f},{y:.0f} l-3,-9 M{x:.0f},{y:.0f} l1,-11 M{x:.0f},{y:.0f} l4,-8" stroke="#5E8F38" stroke-width="2.4" stroke-linecap="round"/>')
    pth = "M-20,400 C160,380 300,430 420,410 C560,388 660,340 820,350"
    s.append(f'<path d="{pth}" stroke="{INK}" stroke-width="96" fill="none" stroke-linecap="round"/>'
             f'<path d="{pth}" stroke="#C9965A" stroke-width="88" fill="none" stroke-linecap="round"/>'
             f'<path d="{pth}" stroke="#DDB27A" stroke-width="60" fill="none" stroke-linecap="round"/>')
    return "".join(s)


def page():
    psvg = lambda s, h=236: s.replace("<svg ", f'<svg height="{h}" style="max-width:100%" ', 1).replace('style="display:block;overflow:visible"', "", 1)  # noqa: E731
    ff = lambda src, x, b=40, w=150, h=200: f'<div style="position:absolute;left:{x}%;bottom:{b}px;width:{w}px;transform:translateX(-50%)">{psvg(src, h)}</div>'  # noqa: E731
    burger_small = gen.wrap(gf.ground() + gf.burger("angry", "up", "stand"), label="Hamburger")
    fries_small = gen.wrap(gf.ground() + gf.fries("angry", "stand"), label="Hranolky")
    stage = (f'<svg viewBox="0 0 800 540" preserveAspectRatio="xMidYMid slice" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%">{stage_svg()}</svg>'
             + ff(fries_small, 14, 60, 120, 170) + ff(burger_small, 28, 52, 140, 190) + ff(burger_small, 42, 46, 150, 200)
             + f'<div style="position:absolute;left:60%;bottom:30px;width:200px;transform:translateX(-50%)">{psvg(hero, 280)}</div>'
             # srdíčka Pana Brambory: malý štítek těsně nad jeho hlavou
             + f'<svg viewBox="-138 -8 276 40" width="150" aria-hidden="true" style="position:absolute;left:61.5%;bottom:244px;transform:translateX(-50%)">{hearts(0, 0, 10, 6)}</svg>'
             + f'<svg viewBox="0 0 800 540" preserveAspectRatio="xMidYMid slice" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none">'
             f'{gen.star(378, 360, 20)}{gf.txt(330, 300, "BUM!", "#E07A1F", 34, -8)}'
             f'<path d="M560,250 q40,-30 80,-10" stroke="{INK}" stroke-width="4" fill="none" stroke-dasharray="8 8" stroke-linecap="round"/>'
             f'{gf.txt(600, 230, "STOP!", "#C8402F", 34, 6)}</svg>')
    chips = "".join(chip(k, v) for k, v in [("Brambor", "2 na začátku"), ("Další", "+1 za " + drop() + "1000"),
                                             ("Životy", "10 srdíček"), ("Místo", "na cestě")])
    h = f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>Pan Brambora – list postavy</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&amp;family=Bangers&amp;family=Nunito:wght@500;700;800&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#8A5530}}a:hover{{color:#6A3E1E}}
</style>
</helmet>
<div style="width:1680px;height:1760px;box-sizing:border-box;padding:48px 56px;background:{{{{paper}}}};font-family:Nunito,sans-serif;color:{INK};display:flex;flex-direction:column;gap:32px">
<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:32px">
<div style="display:flex;flex-direction:column;gap:6px">
<span style="font-size:16px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#8A5530">Fast Food Fight · obránce · nový</span>
<h1 style="margin:0;font-family:'Baloo 2',sans-serif;font-size:76px;font-weight:800;line-height:.95">Pan Brambora</h1>
<p style="margin:0;font-size:19px;font-weight:600;color:#5A4A3A;max-width:660px">Jako jediný může stát přímo na cestě. Postaví se tam se svým štítem a fast food přes něj nemůže projít. Hamburgery do něj narážejí a hranolky ho mlátí, až mu dojdou srdíčka. Pak se rozpadne na malé hranolky.</p>
</div>
<div style="display:flex;gap:16px">
{chips}
</div>
</div>
<div style="display:flex;gap:28px;height:540px">
<div style="{card};width:330px;box-sizing:border-box;padding:20px;display:flex;flex-direction:column;gap:12px">
<span style="font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Předloha</span>
<div style="flex:1;border-radius:12px;overflow:hidden;background:#EFE6DA">
<img src="{PREDLOHA}" alt="Dětská kresba: brambora s hnědými očky, nožičkami a velkým štítem v ruce" style="width:100%;height:100%;object-fit:contain;display:block">
</div>
<span style="font-size:15px;color:#5A4A3A;font-weight:600">kresby/obranci/Brambora.png · popis v „Brambora.md“</span>
</div>
<div style="{card};flex:1;position:relative;overflow:hidden;background:#8BB85A">
{stage}
<span style="position:absolute;top:18px;left:22px;padding:4px 12px;background:rgba(255,255,255,.92);border:3px solid {INK};border-radius:12px;font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Ve hře</span>
<span style="position:absolute;top:22px;right:22px;padding:4px 10px;background:rgba(255,255,255,.92);border:2px solid {INK};border-radius:10px;font-size:14px;font-weight:800;color:#6A3E1E">stojí na cestě, fast food čeká</span>
</div>
<div style="{card};width:440px;box-sizing:border-box;padding:20px;display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">Díly loutky</span>
<div style="display:grid;grid-template-columns:repeat(3, minmax(0, 1fr));gap:10px;flex:1">
'''
    for t, ds, s in parts:
        h += f'''<div style="border:2px dashed #BFAE98;border-radius:14px;padding:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px">
<div style="height:70px;width:100%;display:flex;align-items:center;justify-content:center">{psvg(s, 64)}</div>
<span style="font-weight:800;font-size:15px;text-align:center">{t}</span>
<span style="font-size:12px;color:#5A4A3A;font-weight:600;text-align:center;line-height:1.25">{ds}</span>
</div>
'''
    h += f'''</div>
</div>
</div>
<div style="display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:26px;font-weight:800">Stavy a animace</span>
<div style="display:grid;grid-template-columns:repeat(7, minmax(0, 1fr));gap:18px">
'''
    for i, (t, ds, s) in enumerate(poses):
        bg = "#FFF4D6" if t in ("Náraz", "Zásah") else ("#FBE9D8" if t in ("Pocuchaný", "Rozpad") else "#FFFFFF")
        h += f'''<div style="{card};background:{bg};padding:14px 12px 16px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{psvg(s)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:19px;font-weight:800;line-height:1.1">{i + 1}. {t}</span>
<span style="font-size:13.5px;font-weight:600;color:#5A4A3A;line-height:1.3">{ds}</span>
</div>
'''
    steps = [("Na cestu", "hráč vybere bramboru a ťukne na cestu; nekupuje se za vodu"),
             ("Stop!", "fast food se zastaví u štítu a nemůže projít; ostatní zelenina ho zatím bije"),
             ("Bum, bum", "každý náraz hamburgeru nebo hozená hranolka vezme 1 srdíčko z 10"),
             ("Krach!", "bez srdíček se rozpadne na malé hranolky a fast food jde dál")]
    h += f'''</div>
</div>
<div style="display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:26px;font-weight:800">Schopnost: zátaras na cestě</span>
<div style="display:grid;grid-template-columns:repeat(4, minmax(0, 1fr));gap:20px">
<div style="{card};background:#FFF4D6;padding:14px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{psvg(fx_bump, 250)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Hamburger narazí</span>
<span style="font-size:14px;font-weight:600;color:#5A4A3A">„Bum!“ odrazí se od štítu, Brambora přijde o srdíčko</span>
</div>
<div style="{card};background:#FBE9D8;padding:14px;display:flex;flex-direction:column;gap:6px">
<div style="height:250px;display:flex;align-items:center;justify-content:center">{psvg(fx_crumble, 250)}</div>
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Rozpad na hranolky</span>
<span style="font-size:14px;font-weight:600;color:#5A4A3A">poslední srdíčko: „Krach!“ a cesta je zase volná</span>
</div>
<div style="{card};grid-column:span 2;padding:22px 24px;display:flex;flex-direction:column;gap:14px">
<span style="font-family:'Baloo 2',sans-serif;font-size:20px;font-weight:800">Jak to funguje</span>
'''
    for i, (t, d) in enumerate(steps):
        h += f'''<div style="display:flex;align-items:center;gap:14px">
<span style="flex:none;width:44px;height:44px;border-radius:50%;background:{SHIELD2};border:3px solid {INK};display:flex;align-items:center;justify-content:center;font-family:'Baloo 2',sans-serif;font-size:22px;font-weight:800">{i + 1}</span>
<span style="font-size:17px;font-weight:700"><b style="font-family:'Baloo 2',sans-serif;font-size:19px">{t}</b> · {d}</span>
</div>
'''
    h += f'''<p style="margin:4px 0 0;font-size:14px;font-weight:700;color:#5A4A3A;line-height:1.35">Brambory se nekupují za vodu: každý hráč jich má na začátku 2 a další dostane jen tehdy, když mu na konci úrovně zbyde víc než 1000 kapek (nejvýš 1 za úroveň). Čísla (10 srdíček, 1 srdíčko za náraz) jsou návrh pro první playtest.</p>
</div>
</div>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"paper":{{"editor":"color","default":"#FBF3E6"}},"$preview":{{"width":1680,"height":1760}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{ paper: this.props.paper ?? '#FBF3E6' }};
}}
}}
</script>
</body>
</html>
'''
    return h


# Předloha: na plátně nahraná dětská kresba, v samostatné stránce cesta ke kresbě v repozitáři.
PREDLOHA = "/_blob/bfa36c84c7bfb3d76e94e45b12c1d17b"
PREDLOHA_LOKALNE = "../../kresby/obranci/Brambora.png"

if __name__ == "__main__":
    html = page()
    with open(os.path.join(REPO, "design", "zdroj", "Brambora.dc.html"), "w") as f:
        f.write(html)
    plain = (html.replace('<script src="./support.js"></script>\n', "").replace("<x-dc>\n<helmet>\n", "").replace("</helmet>\n", "")
             .replace("{{paper}}", "#FBF3E6").replace(PREDLOHA, PREDLOHA_LOKALNE).split("</x-dc>")[0] + "</body>\n</html>\n")
    with open(os.path.join(REPO, "design", "artboardy", "26-brambora.html"), "w") as f:
        f.write(plain)
    print("hotovo:", len(html), "znaků")
