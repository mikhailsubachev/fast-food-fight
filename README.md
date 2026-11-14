# Fast Food Fight

Tower defense pro děti od 7 let: zdravá zelenina brání pusu před fast foodem. Webová hra v Three.js + TypeScript (Vite), pro Android a iOS zabalená přes Capacitor.

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

Stav: **šedý prototyp 1. úrovně** (postavy jsou zatím jednoduché tvary, tutoriál a zvuk chybí).

## Struktura projektu

```
docs/                  plány a požadavky
kresby/                originální fotky dětských kreseb (vstup pro grafiku)
src/
  core/                herní smyčka, stav hry, voda, životy pusy, ukládání postupu
  scene/               Three.js: renderer, pevná kamera, mapa, cesta, políčka, toon materiály
  entities/
    obranci/           mrkev, pórek (růst, útok, vylepšení, ztuhnutí)
    utocnici/          hamburger, hranolky, velký hamburger (chůze, zásah, útěk)
  ui/                  horní lišta, kruhové menu, tutoriál, pauza, obrazovky výhry a prohry
  data/                čísla jednotek, vlny úrovní, všechny texty hry (jeden soubor kvůli překladu)
  audio/               přehrávání hudby a zvukových efektů
public/assets/
  postavy/             ořezané díly postav z kreseb (papírové loutky, max. 1024 × 1024 px)
  prostredi/           textury prostředí (záhon, stůl, prostírání)
  zvuky/               hudba a efekty (licence CC0)
tests/                 automatické testy (např. odehrání vlny)
tools/                 pomocné skripty (zpracování nafocených kreseb na díly postav)
```
