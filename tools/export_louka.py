#!/usr/bin/env python3
"""Vyexportuje zem úrovní z návrhu do hry.

Čte obrazovky úrovní z plátna s celou mřížkou (design/zdroj/Uroven1D.dc.html
a Uroven2D.dc.html, 1920 × 1080 px) a zapíše:

- public/assets/prostredi/louka.svg – trávník (skvrny trávy), cesta s okrajem a kamínky, šipka startu, kaluž
  a obrysy celé mřížky šestihranů (na trávě zelené, na cestě hnědé, u překážek šedé).
  Obrázek se ve hře natáhne na zem: 120 px návrhu = 1 políčko v ose x, 108 px = 1 políčko
  v ose z (pohled kamery pod úhlem asi 64°). Kolem výřezu návrhu je okraj louky pro
  širší obrazovky.
- public/assets/prostredi/louka-2.svg – totéž pro 2. úroveň „Školní svačina“; místo kaluže na
  louce leží školní věci (svačinový box, láhev, penál, sešit, pastelky, guma), které jsou ploché,
  a proto patří do obrázku země.
- public/assets/prostredi/louka-ozdoby.svg a louka-2-ozdoby.svg – drobné ozdoby trávníku a ploché
  předměty zvlášť, aby se ve hře kreslily nad políčky na sázení (šestihrany jsou vždy vespod).
- public/assets/prostredi/motyl-modry.svg, motyl-ruzovy.svg, vcela.svg – poletující ozdoby.

Políčka na sázení (volná, osázená, vybraná), postavy, překážky nad zemí (pařez, kámen,
krtina) a ovládání se kreslí ve hře zvlášť.

Spuštění: python3 tools/export_louka.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'design', 'zdroj', '{}')
# (zdroj, výstup, ploché překážky ležící na louce v px návrhu: x × 120, z × 108)
LEVELS = [
    ('Uroven1D.dc.html', 'louka.svg', []),
    (
        'Uroven2D.dc.html',
        'louka-2.svg',
        [(1.6, 8.6), (8.9, 8.9), (8.6, 3.9), (13.4, 2.9), (5.0, 1.4), (15.2, 5.9)],
    ),
]
OUT = os.path.join(ROOT, 'public', 'assets', 'prostredi')

# Výřez obrázku země v pixelech návrhu (o 4 políčka víc do stran, o 2,5 nahoru a dolů).
VIEW = (-480, -270, 2880, 1620)
TEXTURE_W, TEXTURE_H = 4096, 2304

GRASS = ('#9CC768', '#7FAE4E', '#94C262', '#5E8F38', '#6E9C45', '#4E7F2E')
PATH = ('fill="#C9965A"', 'fill="#DDB27A"', 'stroke="#B9844B"', 'fill="#9C7244"', 'stroke="#4E8A2E"', 'fill="#E0574F"')
# Obrysy celé mřížky (varianta D): tenčí tah 2,5 px.
GRID = 'stroke-width="2.5"'
PUDDLE = ('fill="#7CC4EE"', 'fill="#A8DBF7"', 'fill="#4E9A3A" stroke="#2B2118"')


def children(svg: str) -> list[str]:
    """Prvky přímo uvnitř skupiny (bez vnořených)."""
    out, depth, start = [], 0, 0
    for m in re.finditer(r'<(/?)([a-zA-Z]+)[^>]*?(/?)>', svg):
        close, _tag, selfclose = m.groups()
        if close:
            if depth == 0:
                break
            depth -= 1
            if depth == 0:
                out.append(svg[start:m.end()])
        else:
            if depth == 0:
                start = m.start()
            if selfclose:
                if depth == 0:
                    out.append(svg[start:m.end()])
            else:
                depth += 1
    return out


def center(el: str) -> tuple[float, float]:
    m = re.match(r'<g transform="translate\(([\d.\-]+),([\d.\-]+)\)', el)
    if m:
        return float(m.group(1)), float(m.group(2))
    pts = [tuple(map(float, p)) for p in re.findall(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', el)]
    if pts:
        return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    m = re.search(r'cx="([\d.\-]+)" cy="([\d.\-]+)"', el)
    return (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)


def shift(el: str, dx: float, dy: float) -> str:
    return f'<g transform="translate({dx:g},{dy:g})">{el}</g>'


def export_level(source: str, out_name: str, flat: list[tuple[float, float]]) -> list[str]:
    src = open(SRC.format(source), encoding='utf-8').read()
    start = src.index('<g transform="translate(1060,800) scale(')
    items = children(src[src.index('>', start) + 1:])

    first_hex = next(i for i, el in enumerate(items) if 'fill="#D9F2A6"' in el)
    # items[0] je jednobarevné pozadí. Velké skvrny trávy patří pod mřížku, drobné ozdoby
    # (stébla, kytičky, houby, jetel, kamínky, beruška, šnek) se kreslí nad políčka.
    ground = [el for el in items[1:first_hex] if el.startswith('<polygon')]
    decor = [el for el in items[1:first_hex] if not el.startswith('<polygon')]

    # Okraj louky pro širší obrazovky: skvrny a stébla trávy z levého a horního pásu zopakovat vpravo a dole.
    grass = [el for el in ground if any(c in el for c in GRASS) and el.startswith(('<polygon', '<path'))]
    margin = []
    for el in grass:
        x, y = center(el)
        if 0 <= x < 480:
            margin.append(shift(el, 1920, 0))
        if 100 <= y < 370:
            margin.append(shift(el, 0, 1080))

    rest = items[first_hex:]
    path = [el for el in rest if el.startswith(('<polygon', '<polyline', '<ellipse', '<path')) and any(k in el for k in PATH)]
    grid = [el for el in rest if el.startswith('<polygon') and GRID in el and len(re.search(r'points="([^"]+)"', el).group(1).split()) == 6]
    puddle = []
    for i, el in enumerate(rest):
        if any(k in el for k in PUDDLE):
            puddle.append(el)
        elif puddle and el.startswith('<path') and 'stroke="#FFFFFF"' in el:
            puddle.append(el)  # odlesky na vodě
    # Ploché předměty na louce (2. úroveň): skupina posunutá přesně na místo předmětu a natočená.
    spots = {(round(x * 120), round(z * 108)) for x, z in flat}
    things = []
    for el in rest:
        m = re.match(r'<g transform="translate\((-?\d+),(-?\d+)\) rotate\(-?\d+\)">', el)
        if m and (int(m.group(1)), int(m.group(2))) in spots:
            things.append(el)
    assert len(things) == len(flat), f'{out_name}: nalezeno {len(things)} z {len(flat)} předmětů'

    x0, y0, w, h = VIEW
    head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{TEXTURE_W}" height="{TEXTURE_H}">'
    svg = (
        head + f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#8BB85A"/>'
        + ''.join(margin) + ''.join(ground) + ''.join(path) + ''.join(puddle) + ''.join(grid) + '</svg>'
    )
    # Ozdoby nad políčky: v návrhu je zakrývá cesta a kaluž, proto se tam ořežou maskou.
    cover = ''.join(re.sub(r'(fill|stroke)="#[0-9A-Fa-f]+"', r'\1="#000"', el) for el in path + puddle)
    top = (
        head + f'<defs><mask id="m" maskUnits="userSpaceOnUse" x="{x0}" y="{y0}" width="{w}" height="{h}">'
        f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#fff"/>{cover}</mask></defs>'
        f'<g mask="url(#m)">' + ''.join(decor) + '</g>' + ''.join(things) + '</svg>'
    )
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, out_name), 'w', encoding='utf-8') as f:
        f.write(svg)
    with open(os.path.join(OUT, out_name.replace('.svg', '-ozdoby.svg')), 'w', encoding='utf-8') as f:
        f.write(top)
    print(f'{out_name}: {len(ground)} skvrn trávy, {len(decor)} ozdob, {len(margin)} na okraji, {len(path)} prvků cesty, {len(puddle)} kaluž, {len(grid)} šestihranů mřížky, {len(things)} předmětů')
    return rest


def main() -> None:
    rest = []
    for source, out_name, flat in LEVELS:
        r = export_level(source, out_name, flat)
        if not rest:
            rest = r

    critters = {
        'motyl-modry': lambda el: 'fill="#9FD3F5"' in el,
        'motyl-ruzovy': lambda el: 'fill="#F6B0D0"' in el,
        'vcela': lambda el: 'fill-opacity=".85"' in el and '#FFC93C' in el,
    }
    for name, match in critters.items():
        el = next(el for el in rest if el.startswith('<g') and match(el))
        pos = re.match(r'<g transform="translate\(([\d.\-]+),([\d.\-]+)\)', el)
        print(f'{name}: px {pos.group(1)}, {pos.group(2)}')
        # Bez posunu na místo v návrhu: ve hře se postavička kreslí kolem svého středu.
        el = re.sub(r'^<g transform="translate\([\d.\-]+,[\d.\-]+\)\s*', '<g transform="', el, count=1)
        el = el.replace('<g transform="">', '<g>')
        with open(os.path.join(OUT, f'{name}.svg'), 'w', encoding='utf-8') as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-26 -26 52 52" width="208" height="208">{el}</svg>')



if __name__ == '__main__':
    main()
