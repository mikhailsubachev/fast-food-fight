"""
Představení postav: jedna karta pro každou postavu, která se ve hře ukáže, když postava
přijde poprvé. V okénku karty běží krátká animace dokola (postava ukáže, co umí),
vedle je jméno, jedna věta, schopnost, ukazatele a tip.

Každý artboard má tři části:
  1. herní obrazovku 16 : 9 s kartou (animace v okénku běží dokola),
  2. rozkres animace do 4 kroků (stejná scéna zastavená ve 4 okamžicích),
  3. popisky.

Obrázky postav bere z public/assets/postavy (export z generátorů postav), takže sedí
přesně na postavičky ve hře.

Spuštění z kořene repozitáře:  python3 design/generator/gen_predstaveni.py
Zapíše design/zdroj/Predstaveni*.dc.html, design/artboardy/17–25-predstaveni-*.html
a doplní je do design/zdroj/canvas.json (stránka „Postavy“, pod listy postav).
"""
from __future__ import annotations

import base64
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / "public" / "assets" / "postavy"
ZDROJ = ROOT / "design" / "zdroj"
ARTBOARDY = ROOT / "design" / "artboardy"

INK = "#2B2118"
CREAM = "#FFFBF2"
GREEN = "#4E9A3A"
RED = "#C8402F"
YELLOW = "#F7C744"

# ---------------------------------------------------------------- scéna ----------

S = 640  # okénko se scénou je 640 × 640 px
VEG_H = 270  # výška obrázku zeleniny (celý obrázek 330 × 450 jednotek)
FF_H = round(VEG_H * 1.73 / 1.56)  # fast food je ve hře o kousek vyšší
FOOT_X = 0.515  # kde v obrázku postavy jsou nohy
FOOT_Y = 0.965
VEG_Y = 400  # nohy zeleniny (na políčku nad cestou)
PATH_Y = 540  # nohy fast foodu (na cestě)

EPS = 0.0006


@dataclass
class Key:
    t: float  # v sekundách
    x: float
    y: float
    r: float = 0.0
    s: float = 1.0


@dataclass
class El:
    """Jeden obrázek nebo kousek HTML ve scéně, s drahou a časy, kdy je vidět."""

    html: str
    w: float
    h: float
    ax: float  # kotva (poloha drahy) v obrázku, zlomek šířky a výšky
    ay: float
    path: list[Key]
    vis: list[tuple[float, float]]  # intervaly (od, do) v sekundách
    fade: float = 0.0  # plynulé objevení a zmizení (s)
    z: int = 0

    def at(self, t: float) -> tuple[float, float, float, float, float]:
        p = self.path
        if t <= p[0].t:
            k = p[0]
            pos = (k.x, k.y, k.r, k.s)
        elif t >= p[-1].t:
            k = p[-1]
            pos = (k.x, k.y, k.r, k.s)
        else:
            for a, b in zip(p, p[1:]):
                if a.t <= t <= b.t:
                    u = 0 if b.t == a.t else (t - a.t) / (b.t - a.t)
                    pos = (
                        a.x + (b.x - a.x) * u,
                        a.y + (b.y - a.y) * u,
                        a.r + (b.r - a.r) * u,
                        a.s + (b.s - a.s) * u,
                    )
                    break
        return (*pos, self.opacity(t))

    def intervals(self) -> list[tuple[float, float]]:
        """Intervaly viditelnosti seřazené a sloučené (navazující snímky bez mezery)."""
        out: list[list[float]] = []
        for a, b in sorted(self.vis):
            if b <= a:
                continue
            if out and a <= out[-1][1] + 1e-9:
                out[-1][1] = max(out[-1][1], b)
            else:
                out.append([a, b])
        return [(a, b) for a, b in out]

    def opacity(self, t: float) -> float:
        for a, b in self.intervals():
            if a <= t < b or (self.fade and a <= t <= b):
                if not self.fade:
                    return 1.0
                return max(0.0, min(1.0, (t - a) / self.fade, (b - t) / self.fade))
        return 0.0


def sprite(name: str, h: float) -> tuple[str, float, float]:
    return f'<div class="sp sp-{name}"></div>', h * 330 / 450, h


def char(frames: dict[str, list[tuple[float, float]]], path: list[Key], h: float, z: int = 0) -> list[El]:
    """Postava z několika obrázků (snímků) na jedné dráze; ukáže se vždy jeden snímek."""
    out = []
    for name, vis in frames.items():
        html, w, hh = sprite(name, h)
        out.append(El(html, w, hh, FOOT_X, FOOT_Y, path, vis, z=z))
    return out


def walk(t0: float, t1: float, step: float, a: str, b: str, frames: dict, holes=()) -> None:
    """Střídá dva snímky chůze mezi t0 a t1; v místech `holes` (od, do) se chůze přeruší."""
    t = t0
    i = 0
    while t < t1 - 1e-9:
        e = min(t + step, t1)
        segs = [(t, e)]
        for h0, h1 in holes:
            nxt = []
            for s0, s1 in segs:
                if h1 <= s0 or h0 >= s1:
                    nxt.append((s0, s1))
                else:
                    if s0 < h0:
                        nxt.append((s0, h0))
                    if h1 < s1:
                        nxt.append((h1, s1))
            segs = nxt
        frames.setdefault(a if i % 2 == 0 else b, []).extend(segs)
        t = e
        i += 1


def rest(t0: float, t1: float, base: str, frames: dict) -> None:
    """Základní snímek ve všech chvílích mezi t0 a t1, kdy neběží jiný snímek."""
    busy = sorted(iv for k, ivs in frames.items() for iv in ivs if k != base)
    t = t0
    out = []
    for a, b in busy:
        if b <= t:
            continue
        if a > t:
            out.append((t, min(a, t1)))
        t = max(t, b)
        if t >= t1:
            break
    if t < t1:
        out.append((t, t1))
    frames.setdefault(base, []).extend(out)


def line(t0: float, x0: float, t1: float, x1: float, y: float = PATH_Y, r: float = 0) -> list[Key]:
    return [Key(t0, x0, y, r), Key(t1, x1, y, r)]


def arc(t0: float, p0: tuple, t1: float, p1: tuple, peak: float, n: int = 10, spin: float = 0.0) -> list[Key]:
    """Let obloukem; obrázek se natáčí po směru letu (nebo se točí, když je `spin`)."""
    keys = []
    for i in range(n + 1):
        u = i / n
        x = p0[0] + (p1[0] - p0[0]) * u
        y = p0[1] + (p1[1] - p0[1]) * u - 4 * peak * u * (1 - u)
        dx = p1[0] - p0[0]
        dy = (p1[1] - p0[1]) - 4 * peak * (1 - 2 * u)
        r = spin * u if spin else math.degrees(math.atan2(dy, dx))
        keys.append(Key(t0 + (t1 - t0) * u, x, y, r))
    return keys


def fixed(x: float, y: float, s: float = 1.0, r: float = 0) -> list[Key]:
    return [Key(0, x, y, r, s)]


# ---- drobné obrázky (efekty) ----

DROP = (
    '<svg viewBox="0 0 24 24"><path d="M12 2 C12 2 4.5 11 4.5 15.5 A7.5 7.5 0 0 0 19.5 15.5 C19.5 11 12 2 12 2 Z" '
    f'fill="#3D9BE0" stroke="{INK}" stroke-width="1.8"/><path d="M8.5 15 Q8.5 11.5 10.5 9" stroke="#CDEBFF" '
    'stroke-width="1.6" fill="none" stroke-linecap="round"/></svg>'
)


def star_svg(color: str = "#FFE14D") -> str:
    pts = []
    for i in range(16):
        r = 46 if i % 2 == 0 else 22
        a = math.pi * 2 * i / 16 - math.pi / 2
        pts.append(f"{50 + r * math.cos(a):.1f},{50 + r * math.sin(a):.1f}")
    return (
        f'<svg viewBox="0 0 100 100"><polygon points="{" ".join(pts)}" fill="{color}" stroke="{INK}" '
        'stroke-width="4" stroke-linejoin="round"/></svg>'
    )


def bum(t: float, x: float, y: float, dur: float = 0.18) -> El:
    return El(star_svg(), 84, 84, 0.5, 0.5, [Key(t, x, y, 0, 0.6), Key(t + dur, x, y, 25, 1.15)], [(t, t + dur)], z=30)


def reward(t: float, x: float, y: float, n: int) -> El:
    html = (
        f'<div class="fx-reward"><span class="fx-drop">{DROP}</span>+{n}</div>'
    )
    return El(html, 120, 56, 0.5, 1, [Key(t, x, y), Key(t + 0.9, x, y - 90)], [(t, t + 0.9)], fade=0.15, z=40)


def bubble(t0: float, t1: float, x: float, y: float, text: str, tail: str = "left") -> El:
    html = f'<div class="fx-bubble fx-tail-{tail}">{text}</div>'
    return El(html, 190, 64, 0.5, 1, [Key(t0, x, y + 10, 0, 0.7), Key(t0 + 0.15, x, y, 0, 1)], [(t0, t1)], fade=0.1, z=45)


def range_ring(x: float, y: float, rx: float, color: str, t0: float = 0, t1: float = 99) -> El:
    ry = rx * 0.9
    html = (
        f'<svg viewBox="0 0 {2 * rx + 8} {2 * ry + 8}"><ellipse cx="{rx + 4}" cy="{ry + 4}" rx="{rx}" ry="{ry}" '
        f'fill="{color}" fill-opacity=".16" stroke="#FFFFFF" stroke-width="5" stroke-dasharray="16 12"/></svg>'
    )
    return El(html, 2 * rx + 8, 2 * ry + 8, 0.5, 0.5, fixed(x, y), [(t0, t1)], z=-5)


HEART = "M12 21 C12 21 2 14.6 2 8.2 A5 5 0 0 1 12 5.6 A5 5 0 0 1 22 8.2 C22 14.6 12 21 12 21 Z"


def pips(t_hits: list[float], n: int, track: El, t0: float, t1: float, dy: float, color: str = "#E2463A") -> list[El]:
    """Zbývající životy nad hlavou fast foodu: řada srdíček, s každým zásahem jedno zhasne (zprava)."""
    out = []
    size = 24
    gap = 4
    width = n * size + (n - 1) * gap
    bar_keys = [Key(k.t, k.x, k.y - dy, 0, 1) for k in track.path]
    out.append(El('<div class="lifebar"></div>', width + 16, size + 12, 0.5, 0.5, bar_keys, [(t0, t1)], z=34))
    full = (
        f'<svg class="heart" viewBox="0 0 24 24"><path d="{HEART}" fill="{color}" stroke="{INK}" stroke-width="2.4" '
        f'stroke-linejoin="round"/><path d="M6.6 8.6 Q7 6.9 8.9 6.6" stroke="#FFFFFF" stroke-width="1.8" fill="none" '
        f'stroke-linecap="round"/></svg>'
    )
    lost = (
        f'<svg class="heart" viewBox="0 0 24 24"><path d="{HEART}" fill="#FFFFFF" stroke="#A39A8E" stroke-width="2.4" '
        f'stroke-linejoin="round" stroke-dasharray="3 2.4"/></svg>'
    )
    for i in range(n):
        off = -width / 2 + i * (size + gap) + size / 2
        keys = [Key(k.t, k.x + off, k.y - dy, 0, 1) for k in track.path]
        j = n - 1 - i  # zásahy berou srdíčka zprava
        hit = t_hits[j] if j < len(t_hits) else None
        out.append(El(full, size, size, 0.5, 0.5, keys, [(t0, hit if hit is not None else t1)], z=35))
        if hit is not None:
            out.append(El(lost, size, size, 0.5, 0.5, keys, [(hit, t1)], z=36))
    return out


def hexslot(x: float, y: float) -> El:
    w, h = 210, 104
    html = (
        f'<svg viewBox="0 0 {w} {h}"><polygon points="{w * .25},2 {w * .75},2 {w - 2},{h / 2} {w * .75},{h - 2} '
        f'{w * .25},{h - 2} 2,{h / 2}" fill="#B9DC86" stroke="#7FA84A" stroke-width="3"/></svg>'
    )
    return El(html, w, h, 0.5, 0.5, fixed(x, y - 6), [(0, 99)], z=-10)


def puddle(t0: float, t1: float, x: float, grow: float = 0.18, dry: float = 0.5) -> El:
    html = '<div class="sp sp-louze"></div>'
    return El(
        html,
        150,
        55,
        0.5,
        0.5,
        [Key(t0, x, PATH_Y - 6, 0, 0.2), Key(t0 + grow, x, PATH_Y - 6, 0, 1), Key(t1 - dry, x, PATH_Y - 6, 0, 1), Key(t1, x, PATH_Y - 6, 0, 0.8)],
        [(t0, t1)],
        fade=dry,
        z=-2,
    )


# ---------------------------------------------------------------- postavy --------


@dataclass
class Card:
    key: str  # název souboru
    sheet: str  # list postavy na plátně
    name: str
    side: str  # 'obrance' | 'utocnik'
    paper: str
    sentence: str
    skill: tuple[str, str, str]  # (obrázek schopnosti, název, věta)
    meters: list[tuple[str, int, int, str]]  # (popisek, hodnota, z kolika, poznámka)
    cost: int | None
    extra: tuple[str, str]  # ('Vylepšení' / 'Tip', text)
    loop: float
    scene: list[El]
    steps: list[tuple[float, str, str]]  # rozkres: (čas, nadpis, popis)
    note: str
    level: str
    icon_size: float = 72.0
    # řádek „Zbraň“ nad ukazateli: (obrázek, název, poznámka, barva názvu nebo "")
    # obrázek: "sp:<jméno obrázku postavy>", vlastní <svg>, nebo "" (bez zbraně)
    weapon: tuple[str, str, str, str] | None = None


def lunge(vx: float, hits: list[float], target_x, reach: float = 105, drop: float = 55) -> list[Key]:
    """
    Výpad mrkve jako ve hře (View.lunge): při každém seku rychle doskočí k fast foodu, aby se
    ho mrkvomeč opravdu dotkl, a pomaleji se vrátí na své políčko. Cestou nahoru poskočí.
    target_x(t) je poloha fast foodu v čase t; mrkev se zastaví `reach` px před ním.
    """
    keys = [Key(0, vx, VEG_Y)]
    for h in hits:
        tx = target_x(h) + reach
        keys += [
            Key(h - 0.12, vx, VEG_Y),
            Key(h - 0.06, (vx + tx) / 2, VEG_Y + drop / 2 - 34, -6),
            Key(h, tx, VEG_Y + drop, -10),
            Key(h + 0.08, tx, VEG_Y + drop, -6),
            Key(h + 0.2, vx, VEG_Y),
        ]
    return keys


def slash(h: float, x: float, y: float) -> El:
    """Krátké švihnutí mrkvomečem přímo u fast foodu (v okamžiku zásahu)."""
    return El(SVIH, 132, 64, 0.5, 0.5, [Key(h - 0.04, x, y, -30, 0.6), Key(h + 0.1, x, y, 10, 1.1)], [(h - 0.04, h + 0.1)], fade=0.04, z=22)


def scene_mrkev() -> list[El]:
    T = 4.5
    vx = 330
    # hamburger má 5 životů; Pan Mrkev k němu při každém seku doskočí (jako ve hře) a vrátí se
    hx = lambda t: -150 + 150 * t  # noqa: E731
    hits = [1.5, 1.85, 2.2, 2.55, 2.9]
    m: dict = {"mrkev-sek": [(h - 0.06, h + 0.12) for h in hits], "mrkev-radost": [(3.25, 4.1)], "mrkev-mrk": [(4.25, 4.4)]}
    rest(0, T, "mrkev-klid", m)
    hb: dict = {"hamburger-zasah": [(h, h + 0.12) for h in hits]}
    t_flee = 3.02
    walk(0, t_flee, 0.25, "hamburger-krok1", "hamburger-krok2", hb, holes=[(h, h + 0.12) for h in hits])
    walk(t_flee, 3.8, 0.15, "hamburger-utek1", "hamburger-utek2", hb)
    x_end = hx(t_flee)
    hpath = line(0, -150, t_flee, x_end) + line(t_flee, x_end, 3.8, -200)
    els = [hexslot(vx, VEG_Y), range_ring(vx, VEG_Y - 10, 250, GREEN)]
    els += char(m, lunge(vx, hits, hx), VEG_H, z=6)
    ham = char(hb, hpath, FF_H, z=5)
    els += ham
    els += pips(hits, 5, ham[0], 0, t_flee, FF_H * 0.74)
    els += [slash(h, hx(h) + 40, PATH_Y - 150) for h in hits]
    els += [bum(h, hx(h) + 10, PATH_Y - 140) for h in hits]
    els.append(reward(t_flee, x_end, PATH_Y - 290, 15))
    return els


SVIH = (
    '<svg viewBox="0 0 132 64" style="width:100%;height:100%;display:block">'
    '<path d="M4,58 Q48,2 128,30 Q56,22 4,58 Z" fill="#FFFFFF" fill-opacity=".85" stroke="#F08A24" stroke-width="4" stroke-linejoin="round"/>'
    '<path d="M20,46 Q56,16 104,26" stroke="#F08A24" stroke-width="3" fill="none" stroke-linecap="round" stroke-dasharray="10 8"/>'
    '</svg>'
)


def scene_porek() -> list[El]:
    T = 4.0
    vx = 500
    shots = [(1.0, 1.35), (1.9, 2.2)]
    p: dict = {
        "porek-miri": [(0.75, 1.0), (1.65, 1.9)],
        "porek-vystrel": [(1.0, 1.2), (1.9, 2.1)],
        "porek-radost": [(2.5, 3.3)],
        "porek-mrk": [(3.6, 3.75)],
    }
    rest(0, T, "porek-klid", p)
    hx = lambda t: -150 + 200 * t  # noqa: E731
    hit_t = [b for _, b in shots]
    hb: dict = {"hamburger-zasah": [(h, h + 0.15) for h in hit_t]}
    walk(0, 2.35, 0.25, "hamburger-krok1", "hamburger-krok2", hb, holes=[(h, h + 0.15) for h in hit_t])
    walk(2.35, 3.1, 0.15, "hamburger-utek1", "hamburger-utek2", hb)
    hpath = line(0, -150, 2.35, hx(2.35)) + line(2.35, hx(2.35), 3.1, -200)
    els = [hexslot(vx, VEG_Y), range_ring(vx, VEG_Y - 10, 470, GREEN)]
    els += char(p, fixed(vx, VEG_Y), VEG_H)
    ham = char(hb, hpath, FF_H, z=5)
    els += ham
    # hamburger přichází už pocuchaný: zbývají mu 2 z 5 životů a dva šípy ho dorazí
    els += pips([0, 0, 0] + hit_t, 5, ham[0], 0, 2.35, FF_H * 0.74)
    for a, b in shots:
        tx, ty = hx(b) + 20, PATH_Y - 120
        keys = arc(a, (vx - 40, VEG_Y - 150), b, (tx, ty), 40)
        els.append(El('<div class="sp sp-porkosip"></div>', 114, 48, 0.85, 0.5, keys, [(a, b)], z=20))
        els.append(bum(b, tx, ty))
    els.append(reward(2.35, hx(2.35), PATH_Y - 290, 15))
    return els


def scene_cibule() -> list[El]:
    T = 5.0
    vx = 300
    c: dict = {"cibule-nalez": [(1.2, 1.6)], "cibule-smrad": [(1.6, 2.3)], "cibule-radost": [(2.6, 3.4)], "cibule-mrk": [(4.2, 4.35)]}
    rest(0, T, "cibule-klid", c)
    # hamburger: normálně 180 px/s, v oblaku poloviční rychlostí
    k1 = 1.6
    x1 = -150 + 180 * k1
    k2 = 4.0
    x2 = x1 + 90 * (k2 - k1)
    hpath = [Key(0, -150, PATH_Y), Key(k1, x1, PATH_Y), Key(k2, x2, PATH_Y), Key(T, x2 + 180, PATH_Y)]
    hb: dict = {}
    walk(0, k1, 0.25, "hamburger-krok1", "hamburger-krok2", hb)
    walk(k1, k2, 0.5, "hamburger-krok1", "hamburger-krok2", hb)
    walk(k2, T, 0.25, "hamburger-krok1", "hamburger-krok2", hb)
    hb = {k: [(a, b) for a, b in v] for k, v in hb.items()}
    els = [hexslot(vx, VEG_Y), range_ring(vx, VEG_Y - 10, 300, GREEN)]
    els += char(c, fixed(vx, VEG_Y), VEG_H)
    ham = char(hb, hpath, FF_H, z=5)
    for e in ham:
        e.fade = 0.0
    # na konci smyčky hamburger odejde ze scény
    for e in ham:
        e.vis = [(a, min(b, 4.7)) for a, b in e.vis if a < 4.7]
    els += ham
    els += pips([], 5, ham[0], 0, 4.7, FF_H * 0.74)
    cloud = El(
        '<div class="sp sp-oblak" style="opacity:.8"></div>',
        448,
        264,
        0.5,
        0.5,
        [Key(1.65, vx - 20, PATH_Y - 110, 0, 0.3), Key(2.1, vx - 20, PATH_Y - 110, 0, 1.0), Key(4.0, vx + 10, PATH_Y - 120, 4, 1.1)],
        [(1.65, 4.0)],
        fade=0.35,
        z=3,
    )
    els.append(cloud)
    els.append(bubble(2.4, 3.3, x1 + 90 * 0.8 + 40, PATH_Y - 300, "Hepčí!", "left"))
    return els


def scene_brokolice() -> list[El]:
    T = 4.5
    vx = 540
    b: dict = {"brokolice-mir": [(1.0, 1.4)], "brokolice-hod": [(1.4, 1.75)], "brokolice-radost": [(2.6, 3.4)], "brokolice-mrk": [(3.9, 4.05)]}
    rest(0, T, "brokolice-klid", b)
    hit = 2.4
    hb: dict = {"hamburger-zasah": [(hit, hit + 0.2)]}
    walk(0, T, 0.25, "hamburger-krok1", "hamburger-krok2", hb, holes=[(hit, hit + 0.2)])
    fr: dict = {"hranolky-zasah": [(hit, hit + 0.2)]}
    walk(0, T, 0.2, "hranolky-krok1", "hranolky-krok2", fr, holes=[(hit, hit + 0.2)])
    ham = char(hb, line(0, -110, T, -110 + 150 * T), FF_H, z=6)
    fri = char(fr, line(0, -250, T, -250 + 150 * T), FF_H * 1.58 / 1.73, z=5)
    for e in ham + fri:
        e.vis = [(a, min(bb, 4.1)) for a, bb in e.vis if a < 4.1]
    target = (-180 + 150 * hit, PATH_Y - 250)
    els = [hexslot(vx, VEG_Y), range_ring(vx, VEG_Y - 10, 560, GREEN)]
    els += char(b, fixed(vx, VEG_Y), VEG_H)
    els += fri + ham
    els += pips([hit + 0.05], 5, ham[0], 0, 4.1, FF_H * 0.74)
    els += pips([hit + 0.05], 6, fri[0], 0, 4.1, FF_H * 1.58 / 1.73 * 0.74)
    rocket = arc(1.45, (vx - 30, VEG_Y - 190), hit, target, 130)
    els.append(El('<div class="sp sp-raketa"></div>', 136, 80, 0.7, 0.5, rocket, [(1.45, hit)], z=20))
    els.append(
        El(
            '<div class="sp sp-destnik"></div>',
            300,
            300,
            0.5,
            0.45,
            [Key(hit, target[0], target[1] + 40, 0, 0.3), Key(hit + 0.35, target[0], target[1] + 60, 0, 1.0)],
            [(hit, hit + 0.7)],
            fade=0.2,
            z=30,
        )
    )
    els += [bum(hit + 0.05, -110 + 150 * hit, PATH_Y - 140), bum(hit + 0.05, -250 + 150 * hit, PATH_Y - 130)]
    return els


def scene_hamburger() -> list[El]:
    T = 4.6
    vx = 430
    hx = lambda t: -150 + 150 * t  # noqa: E731
    hits = [1.6, 1.95, 2.3, 2.65, 3.0]
    m: dict = {"mrkev-sek": [(h - 0.06, h + 0.12) for h in hits], "mrkev-radost": [(3.35, 4.2)]}
    rest(0, T, "mrkev-klid", m)
    hb: dict = {"hamburger-zasah": [(h, h + 0.12) for h in hits]}
    t_flee = 3.12
    walk(0, t_flee, 0.25, "hamburger-krok1", "hamburger-krok2", hb, holes=[(h, h + 0.12) for h in hits])
    walk(t_flee, 3.9, 0.15, "hamburger-utek1", "hamburger-utek2", hb)
    x_end = hx(t_flee)
    hpath = line(0, -150, t_flee, x_end) + line(t_flee, x_end, 3.9, -200)
    els = [hexslot(vx, VEG_Y)]
    els += char(m, lunge(vx, hits, hx), VEG_H, z=6)
    ham = char(hb, hpath, FF_H, z=5)
    els += ham
    els += pips(hits, 5, ham[0], 0, t_flee, FF_H * 0.74)
    els += [slash(h, hx(h) + 40, PATH_Y - 150) for h in hits]
    els += [bum(h, hx(h) + 10, PATH_Y - 140) for h in hits]
    els.append(reward(t_flee, x_end, PATH_Y - 290, 15))
    return els


def scene_hranolky() -> list[El]:
    T = 4.0
    vx = 380
    f: dict = {"hranolky-naprah": [(0.85, 1.05)], "hranolky-hod": [(1.05, 1.3)]}
    walk(0, T, 0.18, "hranolky-krok1", "hranolky-krok2", f, holes=[(0.85, 1.3)])
    fx = lambda t: -150 + 250 * t  # noqa: E731
    fpath = [Key(0, -150, PATH_Y), Key(0.85, fx(0.85), PATH_Y), Key(1.3, fx(0.85), PATH_Y), Key(T, fx(0.85) + 250 * (T - 1.3), PATH_Y)]
    fri = char(f, fpath, FF_H * 1.58 / 1.73, z=5)
    for e in fri:
        e.vis = [(a, min(b, 3.4)) for a, b in e.vis if a < 3.4]
    m: dict = {"mrkev-ztuhla": [(1.45, 3.45)], "mrkev-mrk": [(3.6, 3.75)]}
    rest(0, T, "mrkev-klid", m)
    els = [hexslot(vx, VEG_Y)]
    els += char(m, fixed(vx, VEG_Y), VEG_H)
    els += fri
    throw = arc(1.05, (fx(0.85) + 40, PATH_Y - 200), 1.45, (vx, VEG_Y - 150), 90, spin=540)
    els += pips([], 6, fri[0], 0, 3.4, FF_H * 1.58 / 1.73 * 0.74)
    els.append(El('<div class="sp sp-hranolka"></div>', 28, 116, 0.5, 0.5, throw, [(1.05, 1.45)], z=20))
    els.append(bum(1.45, vx, VEG_Y - 150))
    els.append(bubble(1.55, 3.3, vx + 125, VEG_Y - 205, "Ztuhla!", "left"))
    return els


def scene_velky() -> list[El]:
    T = 5.0
    vx = 420
    H = FF_H * 1.5
    hits = [2.6, 3.0, 3.4, 3.8]
    m: dict = {"mrkev-sek": [(h - 0.06, h + 0.12) for h in hits]}
    rest(0, T, "mrkev-klid", m)
    hb: dict = {"hamburger-zasah": [(h, h + 0.12) for h in hits]}
    walk(0, T, 0.35, "hamburger-krok1", "hamburger-krok2", hb, holes=[(h, h + 0.12) for h in hits])
    hpath = []
    # těžké kroky: při každém kroku se trochu zhoupne
    t = 0.0
    i = 0
    while t <= T + 1e-9:
        hpath.append(Key(t, -260 + 120 * t, PATH_Y + 8, 2.5 if i % 2 else -2.5))
        t += 0.35
        i += 1
    big = char(hb, hpath, H, z=5)
    for e in big:
        e.vis = [(a, min(b, 4.6)) for a, b in e.vis if a < 4.6]
    els = [hexslot(vx, VEG_Y)]
    els += char(m, lunge(vx, hits, lambda t: -260 + 120 * t, reach=150), VEG_H, z=6)
    els += big
    els += pips(hits, 8, big[0], 0, 4.6, H * 0.74)
    els += [slash(h, -260 + 120 * h + 60, PATH_Y - 200) for h in hits]
    els += [bum(h, -260 + 120 * h + 30, PATH_Y - 200) for h in hits]
    return els


def scene_lizatko() -> list[El]:
    T = 4.6
    xs = (200, 470)
    stop = 1.9
    lx = -150 + 260 * stop
    lz: dict = {"lizatko-naprah": [(stop, stop + 0.15)], "lizatko-toci": [(stop + 0.15, stop + 1.0)]}
    walk(0, stop, 0.25, "lizatko-krok1", "lizatko-krok2", lz)
    walk(stop + 1.0, T, 0.25, "lizatko-krok1", "lizatko-krok2", lz)
    lpath = [Key(0, -150, PATH_Y), Key(stop, lx, PATH_Y), Key(stop + 1.0, lx, PATH_Y), Key(T, lx + 220 * (T - stop - 1.0), PATH_Y)]
    liz = char(lz, lpath, FF_H, z=5)
    for e in liz:
        e.vis = [(a, min(b, 4.1)) for a, b in e.vis if a < 4.1]
    hit = stop + 0.45
    m: dict = {"mrkev-lepkava": [(hit, hit + 1.0)], "mrkev-lepkava2": [(hit + 1.0, hit + 1.8)]}
    rest(0, T, "mrkev-klid", m)
    p: dict = {"porek-lepkavy": [(hit, hit + 1.0)], "porek-lepkavy2": [(hit + 1.0, hit + 1.8)]}
    rest(0, T, "porek-klid", p)
    els = [hexslot(xs[0], VEG_Y), hexslot(xs[1], VEG_Y)]
    els += char(m, fixed(xs[0], VEG_Y), VEG_H)
    els += char(p, fixed(xs[1], VEG_Y), VEG_H)
    els += liz
    els += pips([], 6, liz[0], 0, 4.1, FF_H * 0.74)
    ring = (
        '<svg viewBox="0 0 400 360"><ellipse cx="200" cy="180" rx="190" ry="171" fill="#FF7FB0" fill-opacity=".18" '
        'stroke="#E8558E" stroke-width="10" stroke-dasharray="4 18" stroke-linecap="round"/></svg>'
    )
    els.append(
        El(ring, 400, 360, 0.5, 0.5, [Key(stop + 0.15, lx, PATH_Y - 120, 0, 0.3), Key(hit + 0.1, lx, PATH_Y - 120, 90, 1.05)], [(stop + 0.15, hit + 0.25)], fade=0.12, z=-3)
    )
    els.append(bubble(hit + 0.1, hit + 1.1, xs[1] + 75, VEG_Y - 205, "Lepí!", "left"))
    return els


def scene_kecup() -> list[El]:
    T = 5.6
    stop = 1.4
    kx = -150 + 200 * stop
    k: dict = {"kecup-nastvani": [(stop, stop + 0.4)], "kecup-prsk": [(stop + 0.4, stop + 1.0)]}
    walk(0, stop, 0.25, "kecup-krok1", "kecup-krok2", k)
    walk(stop + 1.0, T, 0.25, "kecup-krok1", "kecup-krok2", k)
    p0, p1 = 230, 530
    t_slide0 = stop + 1.0 + (p0 - kx) / 200
    t_slide1 = t_slide0 + (p1 - p0) / 400
    kpath = [
        Key(0, -150, PATH_Y),
        Key(stop, kx, PATH_Y),
        Key(stop + 0.2, kx, PATH_Y - 40),
        Key(stop + 0.4, kx, PATH_Y),
        Key(stop + 1.0, kx, PATH_Y),
        Key(t_slide0, p0, PATH_Y, 0),
        Key(t_slide0 + 0.1, p0 + 40, PATH_Y, -9),
        Key(t_slide1, p1, PATH_Y, -9),
        Key(t_slide1 + 0.1, p1 + 20, PATH_Y, 0),
        Key(T, p1 + 20 + 200 * (T - t_slide1 - 0.1), PATH_Y),
    ]
    kec = char(k, kpath, FF_H, z=6)
    for e in kec:
        e.vis = [(a, min(b, 4.0)) for a, b in e.vis if a < 4.0]
    # hamburger za ním: dojde ke kečupu a sjede po něm 2× rychleji
    h_in = 3.7
    hx0 = p0 - 200 * h_in
    h_s1 = h_in + (p1 - p0) / 400
    hpath = [
        Key(0, hx0, PATH_Y),
        Key(h_in, p0, PATH_Y, 0),
        Key(h_in + 0.1, p0 + 40, PATH_Y, -9),
        Key(h_s1, p1, PATH_Y, -9),
        Key(h_s1 + 0.1, p1 + 20, PATH_Y, 0),
        Key(T, p1 + 20 + 200 * (T - h_s1 - 0.1), PATH_Y),
    ]
    hb: dict = {}
    walk(0, h_in, 0.25, "hamburger-krok1", "hamburger-krok2", hb)
    hb["hamburger-krok1"].append((h_in, h_s1 + 0.1))
    walk(h_s1 + 0.1, T, 0.25, "hamburger-krok1", "hamburger-krok2", hb)
    ham = char(hb, hpath, FF_H, z=5)
    for e in ham:
        e.vis = [(a, min(b, 5.0)) for a, b in e.vis if a < 5.0]
    els = list(kec) + ham
    els += pips([], 5, kec[0], 0, 4.0, FF_H * 0.74)
    els += pips([], 5, ham[0], 0, 5.0, FF_H * 0.74)
    dry = 5.3
    for i, x in enumerate((p0 + 20, p0 + 150, p0 + 280)):
        els.append(puddle(stop + 0.5 + 0.12 * i, dry, x))
    els.append(bubble(stop + 0.4, stop + 1.0, kx + 30, PATH_Y - 300, "Prsk!", "left"))
    els.append(bubble(h_in + 0.15, h_s1 + 0.2, (p0 + p1) / 2 + 40, PATH_Y - 300, "Jíha!", "left"))
    return els


def scene_brambora() -> list[El]:
    """Pan Brambora stojí na cestě, hamburger naráží do štítu, až se Brambora rozpadne na hranolky."""
    T = 6.0
    vx = 410
    stop_x = 268  # hamburger stojí těsně před štítem
    bumps = [1.8, 2.4, 3.0, 3.6]
    crash = 3.7
    b: dict = {
        "brambora-naraz": [(1.6, 2.4)],
        "brambora-pocuchany": [(2.4, crash)],
        "brambora-rozpad": [(crash, 5.3)],
    }
    rest(0, 1.6, "brambora-klid", b)
    potato = char(b, fixed(vx, PATH_Y), VEG_H, z=4)
    for e in potato:
        e.vis = [(a, bb) for a, bb in e.vis if a < 5.3]
    # hamburger dojde ke štítu, při každém nárazu cukne zpátky, po rozpadu jde dál
    hpath = [Key(0, -150, PATH_Y), Key(1.6, stop_x, PATH_Y)]
    for t in bumps:
        hpath += [Key(t - 0.12, stop_x - 26, PATH_Y, -6), Key(t, stop_x, PATH_Y, 4), Key(t + 0.12, stop_x - 10, PATH_Y, 0)]
    hpath += [Key(crash + 0.2, stop_x - 10, PATH_Y), Key(T, stop_x - 10 + 200 * (T - crash - 0.2), PATH_Y)]
    hb: dict = {"hamburger-zasah": [(t - 0.12, t + 0.06) for t in bumps]}
    walk(0, 1.6, 0.25, "hamburger-krok1", "hamburger-krok2", hb)
    hb.setdefault("hamburger-krok1", []).extend([(1.6, bumps[0] - 0.12)] + [(a + 0.06, bb - 0.12) for a, bb in zip(bumps, bumps[1:])] + [(bumps[-1] + 0.06, crash + 0.2)])
    walk(crash + 0.2, T, 0.25, "hamburger-krok1", "hamburger-krok2", hb)
    ham = char(hb, hpath, FF_H, z=5)
    for e in ham:
        e.vis = [(a, min(bb, 5.6)) for a, bb in e.vis if a < 5.6]
    els = list(potato) + ham
    # srdíčka Pana Brambory: má jich 10, přichází už se 4, každý náraz vezme jedno
    els += pips([0] * 6 + bumps, 10, potato[0], 0, crash, VEG_H * 0.98)
    els += pips([], 5, ham[0], 0, 5.6, FF_H * 0.74)
    els += [bum(t, vx - 62, PATH_Y - 130) for t in bumps]
    els.append(bubble(1.65, 2.5, vx + 40, PATH_Y - 300, "Stop!", "left"))
    return els


MRKVOMEC = (
    '<svg viewBox="-30 -20 108 40" style="width:100%;height:100%;display:block">'
    '<path d="M0,-9 L-22,-17 M0,-4 L-26,-8 M0,0 L-28,0 M0,4 L-26,8 M0,9 L-22,17" stroke="#2F9E44" stroke-width="4" stroke-linecap="round"/>'
    f'<path d="M2,-14 L2,14 L74,1 Z" fill="#F08A24" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'
    f'<path d="M16,-9 L18,9 M32,-6 L34,6 M48,-3 L50,4" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/></svg>'
)


STIT = (
    '<svg viewBox="-28 -128 56 256" style="width:100%;height:100%;display:block">'
    f'<rect x="-18" y="-118" width="36" height="236" rx="18" fill="#C98B57" stroke="{INK}" stroke-width="8"/>'
    '<rect x="-9" y="-100" width="18" height="200" rx="9" fill="#E8B08A" opacity=".85"/>'
    '<path d="M-4,-84 Q-6,-20 -4,40" stroke="#FFFFFF" stroke-width="5" fill="none" opacity=".6" stroke-linecap="round"/></svg>'
)


LEPKAVA_SAVA = (
    '<svg viewBox="0 0 86 40" style="width:100%;height:100%;display:block">'
    f'<path d="M14,8 Q40,2 70,10 Q78,14 72,20 Q66,24 66,30 Q66,37 61,37 Q56,37 57,29 Q58,22 48,22 Q40,22 40,30 Q40,34 36,34 Q32,34 33,27 Q34,20 22,20 Q8,20 8,14 Q8,9 14,8 Z" fill="#F07AA8" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
    '<path d="M20,12 Q34,9 46,11" stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round"/>'
    '</svg>'
)


CARDS: list[Card] = [
    Card(
        "Mrkev", "Main.dc.html", "Pan Mrkev", "obrance", "#FBF6EC",
        "Seká mrkvomečem všechno, co jde po cestě kolem něj.",
        ("mrkev-sek", "Mrkvomeč", "Ostrý mrkvomeč. Seká jen zblízka, zato hodně rychle."),
        [("Dosah", 1, 5, "jen vedle cesty"), ("Útok", 5, 5, "1 sek za sekundu")],
        40, ("Vylepšení", "Seká ještě rychleji a trochu dál."), 4.5, scene_mrkev(),
        [
            (1.0, "Hamburger jde po cestě", "Přerušovaný kruh ukazuje, kam Pan Mrkev dosáhne."),
            (1.5, "Hop a sek!", "Pan Mrkev doskočí k hamburgeru a sekne. Každý sek vezme srdíčko."),
            (3.3, "Hamburger utíká", "Bez srdíček uteče a hráč dostane kapky vody."),
            (3.75, "Radost", "Pan Mrkev je zpátky na políčku a raduje se."),
        ],
        "Ukáže se na začátku 1. úrovně.", "1. úroveň",
        weapon=(MRKVOMEC, "Mrkvomeč", "ostrý, seká zblízka", "#E07A1F"),
    ),
    Card(
        "Porek", "Porek.dc.html", "Pórek", "obrance", "#F3F8EA",
        "Střílí pórkové šípy na fast food daleko na cestě.",
        ("porkosip", "Pórkošíp", "Letí obloukem a trefí i fast food, který je ještě daleko."),
        [("Dosah", 3, 5, "3,5 políčka"), ("Útok", 4, 5, "šíp za 1,5 s")],
        60, ("Vylepšení", "Dostřelí dál a střílí rychleji."), 4.0, scene_porek(),
        [
            (0.85, "Míří", "Hamburger je ještě daleko, ale už je v kruhu."),
            (1.18, "Pfff!", "Pórkový šíp letí přes louku."),
            (1.36, "Zásah", "Šíp trefí hamburger i na druhém konci kruhu a vezme mu srdíčko."),
            (2.6, "Utíká", "Další šíp mu vezme poslední srdíčko a hamburger uteče."),
        ],
        "Odemkne se v 1. vlně 1. úrovně.", "1. úroveň",
        weapon=("sp:porkosip", "Pórkošíp", "letí obloukem daleko", ""),
    ),
    Card(
        "Cibule", "Cibule.dc.html", "Pan Cibule", "obrance", "#F6F8EC",
        "Jednou za čas se naježí a vypustí oblak smradu. Fast food v něm kýchá a dusí se.",
        ("oblak", "Smradlavá mlha", "Nikoho nezraní, ale všechny v mlze zpomalí."),
        [("Dosah", 2, 5, "2 políčka kolem"), ("Zpomalí", 4, 5, "na polovinu, 3 s")],
        50, ("Vylepšení", "Větší oblak, který zpomalí na déle."), 5.0, scene_cibule(),
        [
            (1.4, "Naježí se", "Fast food se blíží k Panu Cibulovi."),
            (1.9, "Pfuj!", "Vypustí oblak smradu přes cestu."),
            (2.8, "Hepčí!", "Hamburger v oblaku kýchá a jde pomalu."),
            (4.3, "Oblak zmizí", "Když oblak zmizí, fast food zase chodí normálně."),
        ],
        "Odemkne se ve 2. úrovni.", "2. úroveň",
        weapon=("sp:oblak", "Smradlavá mlha", "nezraní, jen zpomalí", ""),
    ),
    Card(
        "Brokolice", "Brokolice.dc.html", "Pan Brokolice", "obrance", "#F1F8EC",
        "Má velký dostřel. Hodí růžičku vysoko do vzduchu a ta se nad cestou roztříští.",
        ("raketa", "Brokolicová raketa", "Letí vysoko a nad cestou se rozevře v deštník. Zasáhne víc fast foodu naráz."),
        [("Dosah", 5, 5, "nejdál ze všech"), ("Útok", 2, 5, "1 hod za 2,5 s")],
        80, ("Vylepšení", "Růžička se roztříští do většího deštníku."), 4.5, scene_brokolice(),
        [
            (1.2, "Utrhne růžičku", "Fast food je ještě daleko na cestě."),
            (1.9, "Hod!", "Růžička letí vysokým obloukem."),
            (2.55, "Prásk!", "Nad cestou se roztříští jako deštník a zasáhne oba."),
            (3.0, "Radost", "Pan Brokolice se raduje."),
        ],
        "Odemkne se ve 3. úrovni.", "3. úroveň",
        weapon=("sp:raketa", "Brokolicová raketa", "nahoře se rozevře v deštník", ""),
    ),
    Card(
        "Brambora", "Brambora.dc.html", "Pan Brambora", "obrance", "#FBF3E6",
        "Jako jediný se postaví přímo na cestu. Fast food přes něj nemůže projít.",
        ("brambora-naraz", "Bramborový štít", "Fast food do něj naráží a nemůže dál. Každý náraz vezme jedno srdíčko."),
        [("Životy", 5, 5, "10 srdíček"), ("Zdrží", 4, 5, "dokud má srdíčka")],
        None, ("Kde ho vzít", "Na začátku máš 2 brambory. Další dostaneš, když ti na konci úrovně zbyde přes 1000 kapek."),
        6.0, scene_brambora(),
        [
            (1.0, "Na cestě", "Pan Brambora stojí přímo na cestě se štítem."),
            (1.82, "Bum!", "Hamburger narazí do štítu a nemůže projít. Brambora přijde o srdíčko."),
            (3.0, "Drží", "Každý náraz vezme jedno srdíčko. Ostatní zelenina má čas fast food zasáhnout."),
            (4.2, "Krach!", "Bez srdíček se rozpadne na malé hranolky a hamburger jde dál."),
        ],
        "Hráč má na začátku 2 brambory.", "Nový obránce",
        weapon=(STIT, "Bramborový štít", "zastaví fast food", "#8A5530"),
        icon_size=80,
    ),
    Card(
        "Hamburger", "Hamburger.dc.html", "Hamburger", "utocnik", "#FBF1E4",
        "Jde po cestě k puse. Když ho zelenina zasáhne pětkrát, uteče.",
        ("hamburger-krok1", "Bez zbraně", "Sám nic neumí, ale chodí ve velkých skupinách."),
        [("Životy", 5, 8, "5 zásahů"), ("Rychlost", 3, 5, "1 políčko za sekundu")],
        None, ("Tip", "Postav k cestě Pana Mrkve – seká nejrychleji."), 4.6, scene_hamburger(),
        [
            (0.8, "Jde k puse", "Nad hlavou má 5 srdíček – tolik životů mu zbývá."),
            (1.95, "Zásahy", "Pan Mrkev doskočí a sekne. Každý sek vezme jedno srdíčko."),
            (3.0, "Pátý zásah", "Nezbylo mu žádné srdíčko."),
            (3.35, "Utíká", "Hamburger uteče a hráč dostane kapky vody."),
        ],
        "Přijde v 1. vlně 1. úrovně.", "1. úroveň",
        weapon=("", "Žádná", "jde rovnou k puse", ""),
    ),
    Card(
        "Hranolky", "Hranolky.dc.html", "Hranolky", "utocnik", "#FFF1EC",
        "Běhají rychle a házejí hranolku na zeleninu.",
        ("hranolka", "Hranolka", "Hodí ji po zelenině a ta na 2 sekundy ztuhne a nebojuje."),
        [("Životy", 6, 8, "6 zásahů"), ("Rychlost", 4, 5, "nejrychlejší")],
        None, ("Tip", "Dej zeleninu vedle sebe: když jedna ztuhne, ostatní bojují dál."), 4.0, scene_hranolky(),
        [
            (0.7, "Běží", "Rychlejší než hamburger, nad hlavou 6 srdíček."),
            (1.0, "Nápřah", "Zastaví se a napřáhnou se."),
            (1.3, "Hod!", "Hranolka letí na Pana Mrkve."),
            (2.2, "Ztuhla!", "Pan Mrkev na chvíli ztuhne a hranolky proběhnou."),
        ],
        "Přijdou ve 3. vlně 1. úrovně.", "1. úroveň",
        weapon=("sp:hranolka", "Hranolka", "hozená zelenina ztuhne", ""),
    ),
    Card(
        "VelkyHamburger", "Hamburger.dc.html", "Velký hamburger", "utocnik", "#FBF1E4",
        "Je obrovský a pomalý. Než uteče, vydrží osm zásahů!",
        ("hamburger-zasah", "Bez zbraně", "Spoléhá na to, kolik vydrží. Musí ho zasáhnout hodně zeleniny."),
        [("Životy", 8, 8, "8 zásahů"), ("Rychlost", 2, 5, "pomalý")],
        None, ("Tip", "Vylepši zeleninu u cesty, ať seká a střílí rychleji."), 5.0, scene_velky(),
        [
            (1.2, "Dupe po cestě", "Je o polovinu větší a pomalu se kolébá."),
            (2.6, "První sek", "Pan Mrkev doskočí a sekne. Má 8 srdíček – vydrží skoro dvakrát víc."),
            (3.85, "Čtvrtý zásah", "Zbývá mu polovina srdíček a jde dál."),
            (4.4, "Pořád jde!", "Na velký hamburger je potřeba víc zeleniny."),
        ],
        "Přijde ve 4. vlně 1. úrovně.", "1. úroveň",
        icon_size=86,
        weapon=("", "Žádná", "spoléhá na to, kolik vydrží", ""),
    ),
    Card(
        "Lizatko", "Lizatko.dc.html", "Lízátko", "utocnik", "#FFF3F1",
        "Jednou za čas se roztočí a oblepí sladkou šťávou zeleninu kolem sebe.",
        ("lizatko-toci", "Lepkavá šťáva", "Roztočí se a oblepí zeleninu kolem. Ta nebojuje, dokud šťáva nesteče."),
        [("Životy", 6, 8, "6 zásahů"), ("Rychlost", 3, 5, "1 políčko za sekundu")],
        None, ("Tip", "Pórek a brokolice ho trefí z dálky, kam se lízátko nedotočí."), 4.6, scene_lizatko(),
        [
            (1.0, "Jde po cestě", "Lízátko se blíží k zelenině, nad hlavou 6 srdíček."),
            (2.2, "Roztočí se", "Zastaví se a točí se dokola."),
            (2.9, "Lepí!", "Pan Mrkev i Pórek jsou oblepení a nebojují."),
            (3.7, "Šťáva stéká", "Až šťáva steče, zelenina zase bojuje."),
        ],
        "Přijde ve 2. úrovni.", "2. úroveň",
        weapon=(LEPKAVA_SAVA, "Lepkavá šťáva", "oblepí zeleninu", ""),
    ),
    Card(
        "Kecup", "Kecup.dc.html", "Pan Kečup", "utocnik", "#FFF3F1",
        "Naštve se, poskočí a vyprskne spoustu kečupu na cestu.",
        ("louze", "Kečupová louže", "Fast food po ní klouže 2× rychleji. Kečup brzy zaschne."),
        [("Životy", 5, 8, "5 zásahů"), ("Rychlost", 3, 5, "1 políčko za sekundu")],
        None, ("Tip", "Odraz ho dřív, než doprská."), 5.6, scene_kecup(),
        [
            (1.6, "Naštve se", "Zastaví se a poskočí."),
            (2.1, "Prsk!", "Vyprskne kečup na cestu před sebe."),
            (4.0, "Jíha!", "Hamburger za ním po kečupu sjede 2× rychleji."),
            (4.9, "Zasychá", "Kečup po chvíli zaschne a zmizí."),
        ],
        "Přijde ve 3. úrovni.", "3. úroveň",
        icon_size=96,
        weapon=("sp:louze", "Kečupová louže", "fast food po ní klouže", ""),
    ),
]

# ---------------------------------------------------------------- HTML ----------

SPRITE_NAMES = sorted(
    {
        n
        for c in CARDS
        for n in [c.skill[0]]
        + [e.html.split("sp-")[1].split('"')[0] for e in c.scene if 'class="sp sp-' in e.html]
    }
)


# Obrázky nahrané na plátno (Claude Design nedovolí obrázky vložené jako data:).
BLOBS_PATH = ZDROJ / "platno-obrazky.json"


def sprite_css(names: set[str], canvas: bool, game: bool = False) -> str:
    """
    Obrázky postav: na plátně odkazy na nahrané soubory, ve hře odkazy na assets/postavy
    (relativně k adrese hry), v samostatných stránkách vložené.
    """
    out = [".sp{width:100%;height:100%;background:center/contain no-repeat}"]
    blobs = json.loads(BLOBS_PATH.read_text()) if canvas else {}
    for n in sorted(names):
        if game:
            url = f"assets/postavy/{n}.svg"
        elif canvas:
            if n not in blobs:
                raise SystemExit(f"obrázek {n} není nahraný na plátno (doplň {BLOBS_PATH.name})")
            url = blobs[n]
        else:
            url = "data:image/svg+xml;base64," + base64.b64encode((SPRITES / f"{n}.svg").read_bytes()).decode()
        out.append(f".sp-{n}{{background-image:url({url})}}")
    return "\n".join(out)


def transform(e: El, x: float, y: float, r: float, s: float) -> str:
    return f"translate({x - e.ax * e.w:.1f}px,{y - e.ay * e.h:.1f}px) rotate({r:.1f}deg) scale({s:.3f})"


def keyframes(name: str, e: El, T: float) -> str:
    times = {k.t for k in e.path} | {0.0, T}
    for a, b in e.intervals():
        if e.fade:
            times |= {a, b, a + min(e.fade, (b - a) / 2), b - min(e.fade, (b - a) / 2)}
        else:
            times |= {a - EPS, a, b - EPS, b}
    rows = []
    for t in sorted(x for x in times if 0 <= x <= T):
        x, y, r, s, o = e.at(t)
        rows.append(f"{100 * t / T:.3f}%{{transform:{transform(e, x, y, r, s)};opacity:{o:.2f}}}")
    return f"@keyframes {name}{{\n" + "\n".join(rows) + "\n}"


def stage_bg(path_color: str = "#D8B47E") -> str:
    """Louka s kouskem cesty (stejné barvy jako zem ve hře)."""
    tufts = ""
    for i, (x, y) in enumerate([(60, 90), (180, 60), (330, 120), (520, 80), (600, 240), (90, 300), (560, 620), (300, 610), (40, 600), (450, 300)]):
        tufts += f'<path d="M{x},{y} q4,-12 8,0 q4,-14 8,0" stroke="#6E9A3E" stroke-width="3" fill="none" stroke-linecap="round"/>'
    flowers = "".join(
        f'<circle cx="{x}" cy="{y}" r="6" fill="{c}" stroke="{INK}" stroke-width="2"/><circle cx="{x}" cy="{y}" r="2" fill="#F7C744"/>'
        for x, y, c in [(120, 180, "#FFFFFF"), (590, 150, "#F6A6C8"), (250, 620, "#FFFFFF"), (470, 600, "#F6A6C8")]
    )
    return (
        f'<svg class="stage-bg" viewBox="0 0 {S} {S}" preserveAspectRatio="none">'
        f'<rect width="{S}" height="{S}" fill="#9CC765"/>'
        f'<path d="M-10,{PATH_Y - 68} C160,{PATH_Y - 82} 300,{PATH_Y - 56} 450,{PATH_Y - 72} S620,{PATH_Y - 62} 660,{PATH_Y - 70} '
        f'L660,{PATH_Y + 44} C500,{PATH_Y + 56} 330,{PATH_Y + 36} 180,{PATH_Y + 50} S20,{PATH_Y + 40} -10,{PATH_Y + 46} Z" '
        f'fill="{path_color}" stroke="#8C6A3E" stroke-width="5"/>'
        f'<path d="M-10,{PATH_Y - 10} C200,{PATH_Y - 22} 420,{PATH_Y + 2} 660,{PATH_Y - 12}" stroke="#E6C795" stroke-width="10" fill="none" stroke-dasharray="2 26" stroke-linecap="round"/>'
        f"{tufts}{flowers}</svg>"
    )


def scene_html(c: Card, prefix: str, t: float | None) -> str:
    """Scéna: buď animovaná (t = None), nebo zastavená v čase t (rozkres)."""
    parts = [stage_bg()]
    for i, e in enumerate(sorted(c.scene, key=lambda e: e.z)):
        base = f"position:absolute;left:0;top:0;width:{e.w:.1f}px;height:{e.h:.1f}px;transform-origin:{e.ax * e.w:.1f}px {e.ay * e.h:.1f}px;"
        if t is None:
            # bez běžící animace (zastavené plátno) je vidět záběr z kroku 2, ne prázdné okénko
            x, y, r, s, o = e.at(c.steps[1][0])
            still = f"transform:{transform(e, x, y, r, s)};opacity:{o:.2f}" if o > 0.001 else "opacity:0"
            style = base + f"animation:{prefix}-{i} {c.loop}s linear -{c.steps[1][0]:.2f}s infinite;{still}"
        else:
            x, y, r, s, o = e.at(t)
            if o <= 0.001:
                continue
            style = base + f"transform:{transform(e, x, y, r, s)};opacity:{o:.2f}"
        parts.append(f'<div style="{style}">{e.html}</div>')
    return "\n".join(parts)


def scene_css(c: Card, prefix: str) -> str:
    return "\n".join(keyframes(f"{prefix}-{i}", e, c.loop) for i, e in enumerate(sorted(c.scene, key=lambda e: e.z)))


def meter(label: str, val: int, of: int, note: str, color: str) -> str:
    cells = "".join(
        f'<span class="cell{" on" if i < val else ""}" style="{"background:" + color if i < val else ""}"></span>' for i in range(of)
    )
    return (
        f'<div class="meter"><span class="m-label">{label}</span><span class="cells">{cells}</span>'
        f'<span class="m-note">{note}</span></div>'
    )


def weapon_icon(c: Card) -> str:
    """Obrázek zbraně ve čtverci schopnosti: kresba z řádku Zbraň, jinak obrázek postavy či efektu."""
    ico = c.weapon[0] if c.weapon else ""
    if ico and not ico.startswith("sp:"):
        return f'<span class="w-big">{ico}</span>'
    name = ico[3:] if ico else c.skill[0]
    return f'<span class="sp sp-{name}" style="width:{c.icon_size}px;height:{c.icon_size}px"></span>'


def card_html(c: Card, screen: bool = True) -> str:
    color = GREEN if c.side == "obrance" else RED
    ribbon = "Nová zelenina!" if c.side == "obrance" else "Pozor, nový fast food!"
    tag = "Zelenina · obránce" if c.side == "obrance" else "Fast food · útočník"
    meters = "".join(meter(l, v, o, n, color) for l, v, o, n in c.meters)
    cost = ""
    if c.cost is not None:
        cost = f'<div class="meter"><span class="m-label">Cena</span><span class="cost"><span class="drop">{DROP}</span>{c.cost}</span><span class="m-note">kapek vody</span></div>'
    card = f"""
  <div class="card">
    <div class="ribbon" style="background:{color}">{ribbon}</div>
    <div class="stage">
{scene_html(c, "a" + c.key, None)}
    </div>
    <div class="info">
      <span class="tag" style="color:{color};border-color:{color}">{tag}</span>
      <h2 class="name">{c.name}</h2>
      <p class="sentence">{c.sentence}</p>
      <div class="skill">
        <span class="skill-ico" style="border-color:{color}">{weapon_icon(c)}</span>
        <span><span class="skill-kicker" style="color:{color}">Zbraň</span><br><b>{c.skill[1]}</b><br>{c.skill[2]}</span>
      </div>
      <div class="meters">{meters}{cost}</div>
      <p class="extra"><b style="color:{color}">{c.extra[0]}:</b> {c.extra[1]}</p>
      <div class="bottom"><span class="level">{c.level}</span><button type="button" class="btn">Jdeme na to! ▶</button></div>
    </div>
  </div>"""
    if not screen:
        return card
    return f"""
<div class="screen">
  <div class="screen-bg"></div>
  <div class="hud"><span class="pill">{DROP}<b>180</b></span><span class="pill pill-wave">Vlna 1</span><span class="pill pill-round">II</span></div>
  <div class="dim"></div>{card}
</div>"""


def steps_html(c: Card) -> str:
    color = GREEN if c.side == "obrance" else RED
    out = []
    for i, (t, title, text) in enumerate(c.steps, 1):
        out.append(
            f"""<div class="step">
  <div class="mini"><div class="mini-in">{scene_html(c, "s", t)}</div></div>
  <div class="step-text"><span class="num" style="background:{color}">{i}</span><span><b>{title}</b> · {text}<br><i>{t:.2f} s</i></span></div>
</div>"""
        )
    return "\n".join(out)


BOARD_W = 1680
BOARD_H = 1560

BASE_CSS = f"""
.board{{width:{BOARD_W}px;height:{BOARD_H}px;box-sizing:border-box;padding:44px 40px;font-family:Nunito,sans-serif;color:{INK};display:flex;flex-direction:column;gap:26px;overflow:hidden}}
.head{{display:flex;justify-content:space-between;align-items:flex-end;gap:32px}}
.head h1{{margin:0;font-family:'Baloo 2',sans-serif;font-size:60px;font-weight:800;line-height:.95}}
.kicker{{font-size:16px;font-weight:800;letter-spacing:.14em;text-transform:uppercase}}
.head p{{margin:0;font-size:18px;font-weight:600;color:#5A4A3A;max-width:700px}}
.screen{{position:relative;width:1600px;height:900px;border:4px solid {INK};border-radius:24px;overflow:hidden;box-shadow:6px 6px 0 {INK};flex:none}}
.screen-bg{{position:absolute;inset:0;background-color:#8BB85A;background-image:radial-gradient(circle at 20% 30%,#9CC765 0 12%,transparent 13%),radial-gradient(circle at 70% 70%,#9CC765 0 15%,transparent 16%),radial-gradient(circle at 85% 20%,#A5CF6E 0 9%,transparent 10%)}}
.screen-bg::after{{content:'';position:absolute;left:-40px;right:-40px;top:420px;height:110px;background:#D8B47E;border-top:6px solid #8C6A3E;border-bottom:6px solid #8C6A3E;transform:rotate(-4deg)}}
.hud{{position:absolute;top:18px;left:22px;right:22px;display:flex;justify-content:space-between}}
.pill{{display:flex;align-items:center;gap:8px;height:52px;padding:0 18px;background:#fff;border:3px solid {INK};border-radius:26px;font-family:'Baloo 2',sans-serif;font-size:26px;font-weight:800;color:#3D7FC0}}
.pill svg{{width:28px;height:28px}}
.pill-wave{{color:{INK}}}
.pill-round{{width:52px;padding:0;justify-content:center;color:{INK}}}
.dim{{position:absolute;inset:0;background:rgba(43,33,24,.5)}}
.card{{position:absolute;left:110px;top:92px;width:1380px;height:740px;box-sizing:border-box;padding:46px 46px 40px;background:{CREAM};border:5px solid {INK};border-radius:38px;box-shadow:10px 10px 0 {INK};display:flex;gap:44px}}
.ribbon{{position:absolute;left:50%;top:-30px;transform:translateX(-50%) rotate(-2deg);padding:8px 40px;border:4px solid {INK};border-radius:18px;box-shadow:4px 4px 0 {INK};color:#fff;font-family:'Baloo 2',sans-serif;font-size:34px;font-weight:800;white-space:nowrap}}
.stage{{position:relative;flex:none;width:{S}px;height:{S}px;border:4px solid {INK};border-radius:30px;overflow:hidden;box-sizing:content-box;margin-top:4px}}
.stage-bg{{position:absolute;inset:0;width:100%;height:100%}}
.info{{flex:1;display:flex;flex-direction:column;gap:11px;min-width:0;padding-top:6px}}
.tag{{align-self:flex-start;font-size:15px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;border:3px solid;border-radius:999px;padding:4px 14px;background:#fff}}
.name{{margin:0;font-family:'Baloo 2',sans-serif;font-size:76px;font-weight:800;line-height:.9}}
.sentence{{margin:0;font-size:25px;font-weight:700;line-height:1.3}}
.skill{{display:flex;align-items:center;gap:16px;padding:12px 16px;background:#fff;border:3px solid {INK};border-radius:20px;font-size:20px;font-weight:600;line-height:1.3}}
.skill b{{font-family:'Baloo 2',sans-serif;font-size:25px}}
.skill-ico{{flex:none;width:92px;height:92px;border:4px solid;border-radius:50%;background:#FFF6DC;display:flex;align-items:center;justify-content:center;overflow:hidden}}
.skill-ico .sp{{flex:none}}
.w-big{{display:flex;width:80%;height:80%;align-items:center;justify-content:center}}
.w-big svg{{width:100%;height:100%}}
.skill-kicker{{font-size:14px;font-weight:800;letter-spacing:.12em;text-transform:uppercase}}
.meters{{display:flex;flex-direction:column;gap:6px;margin-top:2px}}
.meter{{display:flex;align-items:center;gap:14px}}
.weapon{{font-family:'Baloo 2',sans-serif;font-size:26px;font-weight:800;white-space:nowrap}}
.w-ico{{flex:none;width:86px;height:34px;display:flex;align-items:center;justify-content:center}}
.w-ico .sp{{width:100%;height:100%}}
.w-none{{font-family:'Baloo 2',sans-serif;font-size:28px;font-weight:800;color:#A39A8E}}
.m-label{{width:108px;font-family:'Baloo 2',sans-serif;font-size:24px;font-weight:800}}
.cells{{display:flex;gap:6px}}
.cell{{width:30px;height:24px;border:3px solid {INK};border-radius:8px;background:#EFE6D4}}
.m-note{{font-size:18px;font-weight:700;color:#6B5B4B}}
.cost{{display:flex;align-items:center;gap:6px;font-family:'Baloo 2',sans-serif;font-size:30px;font-weight:800;color:#3D7FC0}}
.cost svg,.drop svg{{width:30px;height:30px;display:block}}
.extra{{margin:2px 0 0;font-size:20px;font-weight:700;line-height:1.3}}
.bottom{{margin-top:auto;display:flex;justify-content:space-between;align-items:center}}
.level{{font-size:17px;font-weight:800;color:#6B5B4B;letter-spacing:.06em;text-transform:uppercase}}
.btn{{cursor:pointer;color:{INK};padding:12px 30px;background:{YELLOW};border:4px solid {INK};border-radius:22px;box-shadow:4px 4px 0 {INK};font-family:'Baloo 2',sans-serif;font-size:32px;font-weight:800}}
.fx-reward{{display:flex;align-items:center;justify-content:center;gap:4px;height:100%;font-family:'Baloo 2',sans-serif;font-size:36px;font-weight:800;color:#2F7BC6;-webkit-text-stroke:1px #fff}}
.fx-drop svg{{width:34px;height:34px;display:block}}
.fx-bubble{{position:relative;height:100%;box-sizing:border-box;display:flex;align-items:center;justify-content:center;background:#fff;border:4px solid {INK};border-radius:28px;font-family:'Baloo 2',sans-serif;font-size:32px;font-weight:800}}
.fx-bubble::after{{content:'';position:absolute;bottom:-16px;left:30px;width:22px;height:22px;background:#fff;border-right:4px solid {INK};border-bottom:4px solid {INK};transform:rotate(45deg) skew(10deg,10deg)}}
.heart{{width:100%;height:100%;display:block}}
.lifebar{{width:100%;height:100%;box-sizing:border-box;background:rgba(255,255,255,.9);border:3px solid {INK};border-radius:14px}}
.steps{{display:flex;gap:24px}}
.step{{flex:1;display:flex;flex-direction:column;gap:12px}}
.mini{{position:relative;width:382px;height:300px;border:3px solid {INK};border-radius:18px;overflow:hidden;background:#9CC765}}
.mini-in{{position:absolute;left:0;top:-66px;width:{S}px;height:{S}px;transform:scale(.597);transform-origin:0 0}}
.step-text{{display:flex;gap:12px;font-size:17px;font-weight:600;line-height:1.35}}
.step-text b{{font-family:'Baloo 2',sans-serif;font-size:19px}}
.step-text i{{color:#6B5B4B;font-style:normal;font-weight:700;font-size:15px}}
.num{{flex:none;width:36px;height:36px;border-radius:50%;border:3px solid {INK};color:#fff;display:flex;align-items:center;justify-content:center;font-family:'Baloo 2',sans-serif;font-size:19px;font-weight:800}}
.foot{{font-size:16px;font-weight:700;color:#5A4A3A;line-height:1.4;margin:0}}
"""


def board_body(c: Card, paper: str) -> str:
    color = GREEN if c.side == "obrance" else RED
    side = "obránce" if c.side == "obrance" else "útočník"
    return f"""<div class="board" style="background:{paper}">
<div class="head">
<div style="display:flex;flex-direction:column;gap:6px">
<span class="kicker" style="color:{color}">Fast Food Fight · představení · {side}</span>
<h1>{c.name} – představení</h1>
</div>
<p>Karta se ukáže, když {c.name} přijde do hry poprvé, a hra se zatím zastaví. V okénku běží animace dokola ({c.loop:g} s, na artboardu začíná krokem 2), tlačítko kartu zavře. {c.note}</p>
</div>
{card_html(c)}
<div class="steps">
{steps_html(c)}
</div>
<p class="foot">Ve hře karta vyjede zdola (0,35 s) a stuha spadne shora. Ukazatele jsou z čísel ve hře (src/data/units.ts), obrázky postav z listu postavy ({c.sheet.replace(".dc.html", "")}).</p>
</div>"""


FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&amp;family=Bangers&amp;family=Nunito:wght@500;700;800&amp;display=swap" rel="stylesheet">'
)


def styles(c: Card, canvas: bool, game: bool = False) -> str:
    names = {c.skill[0]} | {e.html.split("sp-")[1].split('"')[0] for e in c.scene if 'class="sp sp-' in e.html}
    if c.weapon and c.weapon[0].startswith("sp:"):
        names.add(c.weapon[0][3:])
    css = "body{margin:0}\n" + BASE_CSS + "\n" + sprite_css(names, canvas, game) + "\n" + scene_css(c, "a" + c.key)
    # šablona plátna používá {{…}}: v CSS se nesmí objevit dvě složené závorky za sebou
    while "}}" in css or "{{" in css:
        css = css.replace("}}", "} }").replace("{{", "{ {")
    return css


def dc_html(c: Card) -> str:
    body = board_body(c, "{{paper}}")
    title = f"{c.name} – představení"
    props = json.dumps(
        {"paper": {"editor": "color", "default": c.paper}, "$preview": {"width": BOARD_W, "height": BOARD_H}},
        ensure_ascii=False,
    )
    return f"""<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{FONTS}
<style>
{styles(c, True)}
</style>
</helmet>
{body}
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{props}'>
class Component extends DCLogic {{
renderVals() {{
return {{ paper: this.props.paper ?? '{c.paper}' }};
}}
}}
</script>
</body>
</html>
"""


def plain_html(c: Card) -> str:
    return f"""<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>{c.name} – představení</title>
{FONTS}
<style>
{styles(c, False)}
</style>
</head>
<body>
{board_body(c, c.paper)}
</body>
</html>
"""


# Karta ve hře: jen karta (bez herní obrazovky a rozkresu), vložená do stínového DOM.
GAME_DIR = ROOT / "public" / "assets" / "predstaveni"
GAME_TYPE = {
    "Mrkev": "mrkev",
    "Porek": "porek",
    "Cibule": "cibule",
    "Brokolice": "brokolice",
    "Brambora": "brambora",
    "Hamburger": "hamburger",
    "Hranolky": "hranolky",
    "VelkyHamburger": "velkyHamburger",
    "Lizatko": "lizatko",
    "Kecup": "kecup",
}
GAME_CSS = f"""
:host{{all:initial;display:block}}
.card{{position:relative;left:auto;top:auto;margin:36px 10px 0;font-family:Nunito,sans-serif;color:{INK};text-align:left}}
.btn:hover{{filter:brightness(1.05)}}
.btn:active{{transform:translate(2px,2px);box-shadow:2px 2px 0 {INK}}}
"""


def game_fragment(c: Card) -> str:
    """Karta pro hru (public/assets/predstaveni/<typ>.html): styl a karta 1380 × 740 px."""
    return f"<style>\n{styles(c, False, True)}\n{GAME_CSS}</style>\n{card_html(c, screen=False)}\n"


def slug(c: Card) -> str:
    return {
        "Mrkev": "mrkev",
        "Porek": "porek",
        "Cibule": "cibule",
        "Brokolice": "brokolice",
        "Brambora": "brambora",
        "Hamburger": "hamburger",
        "Hranolky": "hranolky",
        "VelkyHamburger": "velky-hamburger",
        "Lizatko": "lizatko",
        "Kecup": "kecup",
    }[c.key]


def main() -> None:
    canvas_path = ZDROJ / "canvas.json"
    canvas = json.loads(canvas_path.read_text())
    y_def = 4160
    y_att = y_def + BOARD_H + 300
    defenders = [c for c in CARDS if c.side == "obrance"]
    attackers = [c for c in CARDS if c.side == "utocnik"]
    # Čísla artboardů v design/artboardy (Brambora přibyl později, proto 27).
    number = {"Mrkev": 17, "Porek": 18, "Cibule": 19, "Brokolice": 20, "Hamburger": 21, "Hranolky": 22,
              "VelkyHamburger": 23, "Lizatko": 24, "Kecup": 25, "Brambora": 27}
    for c in CARDS:
        i = number[c.key]
        fname = f"Predstaveni{c.key}.dc.html"
        (ZDROJ / fname).write_text(dc_html(c))
        (ARTBOARDY / f"{i}-predstaveni-{slug(c)}.html").write_text(plain_html(c))
        GAME_DIR.mkdir(parents=True, exist_ok=True)
        (GAME_DIR / f"{GAME_TYPE[c.key]}.html").write_text(game_fragment(c))
        row = defenders if c.side == "obrance" else attackers
        canvas["boards"][fname] = {
            "h": BOARD_H,
            "page": "page-1",
            "title": f"{c.name} – představení",
            "w": BOARD_W,
            "x": row.index(c) * 1760,
            "y": y_def if c.side == "obrance" else y_att,
        }
        if fname not in canvas["order"]:
            canvas["order"].append(fname)
    canvas["notes"]["predstaveni"] = {
        "x": 0,
        "y": y_def - 260,
        "text": "Představení postav – animace",
        "kind": "title1",
        "maxW": 8720,
        "page": "page-1",
    }
    canvas_path.write_text(json.dumps(canvas, ensure_ascii=False, indent=2) + "\n")
    print("hotovo:", ", ".join(c.key for c in CARDS))


if __name__ == "__main__":
    main()
