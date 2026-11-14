# Návrhy grafiky

Artboardy z plátna „Fast Food Fight – Pan Mrkev“ (Claude Design), stav k 14. 11. 2026.

- `artboardy/` – samostatné HTML stránky, otevřou se rovnou v prohlížeči. Předlohy kreseb se načítají z `../../kresby/`.
  - `1-mrkev.html`, `2-porek.html`, `3-hamburger.html`, `4-hranolky.html` – listy postav (předloha, postava ve hře, díly loutky, stavy a animace)
  - `5-uroven-1.html` – herní obrazovka 1. úrovně (1920 × 1080)
  - `6-misto-na-zeleninu.html` – jak ubývá místa na sázení v dalších úrovních
- `zdroj/` – původní soubory artboardů (`.dc.html`) a rozložení plátna (`canvas.json`) pro případné nahrání zpět do plátna
- `generator/` – Python skripty, které vygenerovaly listy postav a první verzi úrovně (kresba postav v SVG, projekce kamery 55°, tvar cesty)

Obrazovka 1. úrovně a místo na zeleninu jsou ve verzi z plátna k 14. 11. 2026 večer: pravoúhlý pohled bez perspektivy (sklon asi 64°, 120 px na políčko), klikatá cesta, šestihranná políčka na sázení a ozdoby louky (houby, kytičky, motýli, včelka). Generátor k této verzi na plátně není; hra přebírá polohy cesty, překážek, mřížku šestihranů a velikosti postav přímo z SVG (`src/data/level1.ts`, `src/scene/meshes.ts`) a zem s ozdobami exportuje skriptem `tools/export_louka.py`. Nové postavy z plátna (cibule, brokolice, lízátko, kečup) zatím ve hře nejsou.
