# Návrhy grafiky

Artboardy z plátna „Fast Food Fight – Pan Mrkev“ (Claude Design), stav k 14. 11. 2026.

- `artboardy/` – samostatné HTML stránky, otevřou se rovnou v prohlížeči. Předlohy kreseb se načítají z `../../kresby/`.
  - `1-mrkev.html`, `2-porek.html`, `3-hamburger.html`, `4-hranolky.html` – listy postav (předloha, postava ve hře, díly loutky, stavy a animace)
  - `5-uroven-1.html` – herní obrazovka 1. úrovně (1920 × 1080)
  - `6-misto-na-zeleninu.html` – jak ubývá místa na sázení v dalších úrovních
- `zdroj/` – původní soubory artboardů (`.dc.html`) a rozložení plátna (`canvas.json`) pro případné nahrání zpět do plátna
- `generator/` – Python skripty, které vygenerovaly listy postav a první verzi úrovně (kresba postav v SVG, projekce kamery 55°, tvar cesty)

Hra je podle obrazovky 1. úrovně ve variantě D (`zdroj/Uroven1D.dc.html`, `artboardy/14-uroven-1-varianta-d.html`): pravoúhlý pohled bez perspektivy (120 px na políčko v ose x, 108 px v ose z), klikatá cesta, celá mřížka šestihranů přes mapu a ozdoby louky. Hra přebírá mřížku a pravidla políček z `generator/gen_level.py` a polohy cesty a velikosti postav přímo z SVG (`src/data/level1.ts`, `src/scene/meshes.ts`); zem s mřížkou a ozdobami exportuje skript `tools/export_louka.py`. Ve hře jsou i cibule a lízátko (2. úroveň, `zdroj/Uroven2D.dc.html`) a brokolice a kečup (3. úroveň, `zdroj/Uroven3D.dc.html`); obrázky postav exportuje `tools/export_postavy.py` přímo z generátorů v `generator/`.
