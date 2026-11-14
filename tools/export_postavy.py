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
        import gen, gen_porek, gen_ff, gen_level  # noqa: E401
    finally:
        builtins.open = real_open
        os.makedirs = real_makedirs
        sys.stdout = stdout
    return gen, gen_porek, gen_ff, gen_level


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
    gen, gp, gf, gl = load_generator()
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

    # --- Pusa (z návrhu úrovně) ---
    frames["pusa"] = gl.mouth_svg()

    os.makedirs(OUT, exist_ok=True)
    for i, (name, inner) in enumerate(frames.items(), start=1):
        with open(os.path.join(OUT, f"{name}.svg"), "w", encoding="utf-8") as fh:
            fh.write(svg(inner, i))

    # Střely: pórkošíp (vodorovně, hrot vpravo) a hranolka (svisle).
    with open(os.path.join(OUT, "porkosip.svg"), "w", encoding="utf-8") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-8 -16 76 32" width="152" height="64">{gp.arrow_local()}</svg>')
    with open(os.path.join(OUT, "hranolka.svg"), "w", encoding="utf-8") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-14 -108 28 116" width="56" height="232">{gf.big_fry()}</svg>')

    print(f"{len(frames) + 2} obrázků v {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
