# Fast Food Fight

Tower defense pro děti od 7 let: zdravá zelenina brání pusu před fast foodem. Webová hra v Three.js + TypeScript (Vite), pro Android a iOS zabalená přes Capacitor.

**▶ [Hrát v prohlížeči](https://mikhailsubachev.github.io/fast-food-fight/)** (GitHub Pages, nová verze se zveřejní po každém nahrání do `main`)

- [Úvodní požadavky](docs/Úvodní%20požadavky.md)
- [Plán první úrovně](docs/Plán%20první%20úrovně.md)

## Spuštění

Potřeba je Node.js 20 nebo novější.

```bash
npm install
npm run dev        # hra na http://localhost:5173
npm run dev:lan    # hra i pro telefon ve stejné Wi-Fi (adresu vypíše terminál)
npm test           # automatické testy včetně odehrání celé úrovně
npm run build      # kontrola typů a sestavení do dist/
```

Stav: **hratelná 1. úroveň** s postavami z dětských kreseb (papírové loutky podle návrhu v `design/`). Chybí tutoriál a zvuk.

Postavy se z návrhu znovu vyexportují příkazem `python3 tools/export_postavy.py` (zapíše SVG do `public/assets/postavy/`).

## Struktura projektu

```
docs/                  plány a požadavky
design/                návrhy grafiky z plátna (listy postav, obrazovka 1. úrovně)
kresby/                originální fotky dětských kreseb (vstup pro grafiku)
src/
  core/                herní smyčka, stav hry, voda, životy pusy, ukládání postupu
  scene/               Three.js: renderer, pevná kamera, záhon, cesta, překážky, papírové loutky
  entities/
    obranci/           mrkev, pórek (růst, útok, vylepšení, ztuhnutí)
    utocnici/          hamburger, hranolky, velký hamburger (chůze, zásah, útěk)
  ui/                  horní lišta, kruhové menu, tutoriál, pauza, obrazovky výhry a prohry
  data/                čísla jednotek, vlny úrovní, všechny texty hry (jeden soubor kvůli překladu)
  audio/               přehrávání hudby a zvukových efektů
public/assets/
  postavy/             obrázky postav ve všech stavech (SVG z tools/export_postavy.py)
  prostredi/           textury prostředí (záhon, stůl, prostírání)
  zvuky/               hudba a efekty (licence CC0)
tests/                 automatické testy (např. odehrání vlny)
tools/                 pomocné skripty (export postav z návrhu do hry)
```
