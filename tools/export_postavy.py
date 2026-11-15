"""Vyexportuje postavy z generátoru návrhu (design/generator) jako SVG obrázky pro hru.

Každý obrázek je jeden stav papírové loutky (klid, sek, ztuhnutí, útěk…) ve stejném
rámečku 330 × 450: chodidla postavy jsou vždy na bodě (150, 388) generátoru.

Spuštění z kořene projektu:
    python3 tools/export_postavy.py

Generátor při načtení zapisuje své HTML do vlastní cesty; tady se ty zápisy
zahodí, používají se jen jeho kreslicí funkce.
"""

import builtins
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "design", "generator")
OUT = os.path.join(ROOT, "public", "assets", "postavy")

# Rámeček všech obrázků (v souřadnicích generátoru). Chodidla jsou na (150, 388).
VB_X, VB_Y, VB_W, VB_H = -15, -50, 330, 450
FEET = (150, 388)


def load_generator():
    real_open = builtins.open
    real_makedirs = os.makedirs

    def quiet_open(file, mode="r", *args, **kwargs):
        if any(m in mode for m in "wax"):
            return io.StringIO()
        return real_open(file, mode, *args, **kwargs)

    builtins.open = quiet_open
    os.makedirs = lambda *a, **k: None
    sys.path.insert(0, GEN)
    stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        import gen, gen_porek, gen_ff, gen_level, gen_cibule, gen_lizatko, gen_brokolice, gen_kecup  # noqa: E401
    finally:
        builtins.open = real_open
        os.makedirs = real_makedirs
        sys.stdout = stdout
    return gen, gen_porek, gen_ff, gen_level, gen_cibule, gen_lizatko, gen_brokolice, gen_kecup


def svg(inner: str, seed: int, wobble: bool = True) -> str:
    """Samostatný SVG soubor; `wobble` je ručně kreslené chvění čar jako v návrhu."""
    body = inner
    defs = ""
    if wobble:
        fid = f"wob{seed}"
        defs = (
            f'<defs><filter id="{fid}" x="-10%" y="-10%" width="120%" height="120%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="{seed}"/>'
            f'<feDisplacementMap in="SourceGraphic" scale="3.2"/></filter></defs>'
        )
        body = f'<g filter="url(#{fid})">{inner}</g>'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VB_X} {VB_Y} {VB_W} {VB_H}" '
        f'width="{VB_W * 2}" height="{VB_H * 2}">{defs}{body}</svg>'
    )


def main() -> None:
    gen, gp, gf, gl, gc, gz, gb, gk = load_generator()
    star = gen.star
    frames: dict[str, str] = {}

    # --- Pan Mrkev ---
    c = gen.carrot
    badge = star(250, 60, 30, gen.YEL)
    glow = f'<path d="{gen.BODY}" fill="none" stroke="#FFD447" stroke-width="22" stroke-linejoin="round" opacity=".7"/>'
    frames["mrkev-klid"] = c("smile")
    frames["mrkev-mrk"] = c("closed")
    frames["mrkev-sek"] = '<g transform="rotate(-6 155 300)">' + c("fight", "slash") + "</g>"
    frames["mrkev-ztuhla"] = c("frozen", tint="ice")
    frames["mrkev-radost"] = '<g transform="translate(0,-26)">' + c("joy", "up") + "</g>"
    frames["mrkev2-klid"] = c("fight", shine=True, sc=1.35, extra_back=glow, extra_front=badge)
    frames["mrkev2-mrk"] = c("closed", shine=True, sc=1.35, extra_back=glow, extra_front=badge)
    frames["mrkev2-sek"] = (
        '<g transform="rotate(-6 155 300)">' + c("fight", "slash", shine=True, sc=1.35, extra_back=glow, extra_front=badge) + "</g>"
    )
    frames["mrkev2-radost"] = (
        '<g transform="translate(0,-26)">' + c("joy", "up", shine=True, sc=1.35, extra_back=glow, extra_front=badge) + "</g>"
    )

    # --- Pórek ---
    lk = gp.leek
    gold = dict(shine=True, gold=True, bsc=1.2, front=star(250, 60, 30, gen.YEL))
    frames["porek-klid"] = lk("smile")
    frames["porek-mrk"] = lk("closed")
    frames["porek-miri"] = lk("aim", "draw")
    frames["porek-vystrel"] = lk("fight", "shot")
    frames["porek-ztuhl"] = lk("frozen", tint="ice")
    frames["porek-radost"] = '<g transform="translate(0,-26)">' + lk("joy", "up") + "</g>"
    frames["porek2-klid"] = lk("smile", **gold)
    frames["porek2-mrk"] = lk("closed", **gold)
    frames["porek2-miri"] = lk("aim", "draw", **gold)
    frames["porek2-vystrel"] = lk("fight", "shot", **gold)
    frames["porek2-radost"] = '<g transform="translate(0,-26)">' + lk("joy", "up", **gold) + "</g>"

    # --- Hamburger ---
    b = gf.burger
    frames["hamburger-krok1"] = b(legs_="step")
    frames["hamburger-krok2"] = b(legs_="stand")
    frames["hamburger-zasah"] = '<g transform="translate(150,388) scale(1.12,.86) translate(-150,-388)">' + b("hit", "down") + "</g>"
    frames["hamburger-utek1"] = b("scared", "flail", "run", extra=gf.sweat(220, 150))
    frames["hamburger-utek2"] = b("scared", "flail", "step", extra=gf.sweat(236, 180))

    # --- Hranolky ---
    f = gf.fries
    frames["hranolky-krok1"] = '<g transform="translate(0,-18)">' + f(pose="hop") + "</g>"
    frames["hranolky-krok2"] = f(pose="stand")
    frames["hranolky-naprah"] = f("throw", "windup")
    frames["hranolky-hod"] = f("throw", "thrown")
    frames["hranolky-zasah"] = '<g transform="translate(150,388) scale(1.12,.86) translate(-150,-388)">' + f("hit", "hit") + "</g>"
    frames["hranolky-utek1"] = f("scared", "run", extra=gf.sweat(214, 226))
    frames["hranolky-utek2"] = f("scared", "hop", extra=gf.sweat(226, 256))

    # --- Pan Cibule (2. úroveň) ---
    o = gc.onion
    shake = (
        f'<path d="M22,250 l-12,4 M22,270 l-14,0 M22,290 l-12,-4 M278,250 l12,4 M278,270 l14,0 M278,290 l12,-4" '
        f'stroke="{gen.INK}" stroke-width="4" stroke-linecap="round"/>'
    )
    onion_glow = f'<path d="{gc.BODY}" fill="none" stroke="#FFD447" stroke-width="22" stroke-linejoin="round" opacity=".7"/>'
    onion_badge = star(254, 96, 30)
    onion_syrup = gz.syrup(165, 330, 62, 238, 5) + gz.falling(120, 340) + gz.falling(196, 352)
    for prefix, extra in (("cibule", {}), ("cibule2", dict(shine=True, back=onion_glow))):
        badge_ = onion_badge if prefix == "cibule2" else ""
        frames[f"{prefix}-klid"] = o("smile", front=badge_, **extra)
        frames[f"{prefix}-mrk"] = o("closed", front=badge_, **extra)
        frames[f"{prefix}-nalez"] = o("bristle", "clench", spikes=True, straight=True, front=shake + badge_, **extra)
        frames[f"{prefix}-smrad"] = o("puff", "up", front=badge_, **extra)
        frames[f"{prefix}-radost"] = '<g transform="translate(0,-24)">' + o("joy", "up", front=badge_, **extra) + "</g>"
    frames["cibule-ztuhla"] = o("frozen", tint="ice", front=gen.ice_bits)

    # --- Zelenina oblepená šťávou z lízátka (stejné jako v listu lízátka) ---
    frames["mrkev-lepkava"] = gz.carrot_syrup(0)
    frames["mrkev-lepkava2"] = gz.carrot_syrup(1)
    frames["porek-lepkavy"] = gz.leek_syrup(0)
    frames["porek-lepkavy2"] = gz.leek_syrup(1)
    frames["cibule-lepkava"] = o("frozen", front=onion_syrup)
    frames["cibule-lepkava2"] = o("frozen", front=gz.syrup(240, 340, 80, 220, 6, False) + gz.drips_ground(3))

    # --- Lízátko (2. úroveň) ---
    lo = gz.lolli
    frames["lizatko-krok1"] = '<g transform="translate(0,-14) rotate(5 150 388)">' + lo(legs_="hop") + "</g>"
    frames["lizatko-krok2"] = lo(legs_="stand")
    frames["lizatko-naprah"] = lo("spin", "weapons", rot=0)
    frames["lizatko-toci"] = '<g transform="rotate(-8 150 388)">' + lo("spin", "weapons", rot=140) + "</g>"
    frames["lizatko-zasah"] = '<g transform="translate(150,388) scale(1.1,.88) translate(-150,-388)">' + lo("hit", "down") + "</g>"
    frames["lizatko-utek1"] = lo("scared", "up", "run", extra=gf.sweat(236, 110) + gf.sweat(248, 140))
    frames["lizatko-utek2"] = lo("scared", "up", "hop", extra=gf.sweat(236, 110))

    # --- Pusa (z návrhu úrovně) ---
    frames["pusa"] = gl.mouth_svg()

    # --- Pan Brokolice (3. úroveň) ---
    br = gb.broc
    broc_glow = f'<path d="{gb.STALKP}" fill="none" stroke="#FFD447" stroke-width="22" stroke-linejoin="round" opacity=".7"/>' + "".join(
        f'<circle cx="{x}" cy="{y}" r="{r + 8}" fill="#FFD447" opacity=".45"/>' for x, y, r in gb.CL
    )
    broc_badge = star(262, 52, 30)
    for prefix, extra in (("brokolice", {}), ("brokolice2", dict(shine=True, back=broc_glow))):
        badge_ = broc_badge if prefix == "brokolice2" else ""
        frames[f"{prefix}-klid"] = br("smile", front=badge_, **extra)
        frames[f"{prefix}-mrk"] = br("closed", front=badge_, **extra)
        frames[f"{prefix}-mir"] = br("aim", "pluck", front=badge_, **extra)
        frames[f"{prefix}-hod"] = br("aim", "throw", front=badge_, **extra)
        frames[f"{prefix}-radost"] = '<g transform="translate(0,-24)">' + br("joy", "up", front=badge_, **extra) + "</g>"
    frames["brokolice-ztuhla"] = br("frozen", tint="ice", front=gen.ice_bits)
    frames["brokolice-lepkava"] = br("frozen", front=gz.syrup(238, 340, 104, 204, 5) + gz.falling(110, 340) + gz.falling(200, 352))
    frames["brokolice-lepkava2"] = br("frozen", front=gz.syrup(240, 340, 100, 210, 6, False) + gz.drips_ground(3))

    # --- Pan Kečup (3. úroveň) ---
    ke = gk.kecup
    frames["kecup-krok1"] = '<g transform="translate(0,-14) rotate(5 150 388)">' + ke(legs_="hop") + "</g>"
    frames["kecup-krok2"] = ke()
    frames["kecup-nastvani"] = ke("furious", "fists", angry=True, extra=gk.steam())
    frames["kecup-prsk"] = '<g transform="translate(0,-10)">' + ke("squirt", "up", big=True) + "</g>"
    frames["kecup-zasah"] = '<g transform="translate(150,388) scale(1.1,.88) translate(-150,-388)">' + ke("hit", "down") + "</g>"
    frames["kecup-utek1"] = ke("scared", "up", "run", extra=gf.sweat(232, 190) + gf.sweat(246, 220))
    frames["kecup-utek2"] = ke("scared", "up", "hop", extra=gf.sweat(232, 190))

    os.makedirs(OUT, exist_ok=True)
    for i, (name, inner) in enumerate(frames.items(), start=1):
        with open(os.path.join(OUT, f"{name}.svg"), "w", encoding="utf-8") as fh:
            fh.write(svg(inner, i))

    # Střely: pórkošíp (vodorovně, hrot vpravo) a hranolka (svisle).
    with open(os.path.join(OUT, "porkosip.svg"), "w", encoding="utf-8") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-8 -16 76 32" width="152" height="64">{gp.arrow_local()}</svg>')
    with open(os.path.join(OUT, "hranolka.svg"), "w", encoding="utf-8") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-14 -108 28 116" width="56" height="232">{gf.big_fry()}</svg>')

    # Oblak smradu cibule (při pohledu shora se natáhne na zem kolem cibule).
    with open(os.path.join(OUT, "oblak.svg"), "w", encoding="utf-8") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-112 -66 224 132" width="448" height="264">{gc.cloud(0, 0, 1.0, 1.0)}</svg>')

    # Brokolicová raketa (letí doprava) a rozprsk do deštníku nad cílem.
    with open(os.path.join(OUT, "raketa.svg"), "w", encoding="utf-8") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-96 -40 136 80" width="272" height="160">{gb.rocket(0, 0, 0, 1.0)}</svg>')
    with open(os.path.join(OUT, "destnik.svg"), "w", encoding="utf-8") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-110 -80 220 220" width="440" height="440">{gb.burst(0, 0, 1.0)}</svg>')
    # Kečupová louže na cestě (při pohledu shora se natáhne na zem).
    with open(os.path.join(OUT, "louze.svg"), "w", encoding="utf-8") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-92 -34 184 68" width="368" height="136">{gk.puddle(0, 0, 1.0, 2)}</svg>')

    print(f"{len(frames) + 6} obrázků v {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
