# Fast Food Fight: plán první úrovně

Stav: **finální plán v4** (14. 11. 2026, všechny odpovědi od Mika zapracované). Čísla jsou výchozí odhad pro první playtest a doladí se podle hraní s dětmi. Body označené „(návrh)“ jsou moje doporučení, která na otázkách nezávisí a dají se kdykoli změnit.

**Rozhodnuto:**

- Hra je pro děti od 7 let.
- Ovládání myší i dotykem.
- Žádný zoom, žádné posouvání ani skrolování: celá úroveň je vidět na jedné obrazovce.
- Voda se sbírá automaticky s pěknou animací.
- V 1. úrovni jsou mrkev i pórek, hamburger i hranolky.
- Hru bude programovat Claude Code → webová technologie (Three.js), viz kapitola 2.
- Pusa snese 3 kousnutí, čtvrté znamená prohru.
- Utíkající fast food zmizí úplně a vlna pokračuje dál.
- Cíl je jen pusa (nepatří konkrétní postavě).
- Postavy nakreslí dítě, Claude Code podle kreseb udělá grafiku do hry a animace (viz kapitola 6).
- Vylepšení má úrovně 1, 2, (3). V 1. úrovni hry jde vylepšit jen na úroveň 2 a co úroveň 2 přináší, určuje hra, ne hráč.
- V 1. úrovni se zelenina neprodává ani nepřesazuje. Přesazování přijde v dalších úrovních.
- Texty jsou zatím jen psané, česky, bez namluvení.
- Hra je zatím zdarma, bez reklam a bez nákupů.

Zdroj: [Úvodní požadavky.md](Úvodní%20požadavky.md)

---

## 1. Shrnutí hry v jedné větě

Tower defense, ve kterém zdravá zelenina brání pusu před fast foodem. Fast food neumírá, ale po několika zásazích se otočí, uteče pryč z mapy a nechá za sebou vodu, za kterou hráč sází další zeleninu.

## 2. Technologie

**Rozhodnutí: webová hra v Three.js + TypeScript (sestavení přes Vite), do obchodů zabalená přes Capacitor.** Hru bude psát Claude Code.

Proč právě tohle, když programuje Claude Code:

- **Všechno je kód v textových souborech.** Claude Code nemusí klikat v grafickém editoru (což by u Godotu nebo Unity potřeboval), mapu, vlny i animace popisuje přímo v kódu a datových souborech.
- **Claude Code si hru umí sám spustit a vyzkoušet.** Pustí ji v prohlížeči, udělá snímek obrazovky, odehraje vlnu automatickým testem a zkontroluje, že se nic nerozbilo.
- **Jedna verze pro všechny tři cíle:** prohlížeč (stačí poslat odkaz), Android a iOS (stejná hra zabalená přes Capacitor do aplikace).
- **Malé stažení a rychlé spuštění** v mobilním prohlížeči, zdarma, bez licenčních poplatků.

| Kritérium                               | Three.js + Capacitor (zvoleno)  | Godot 4                        | Unity                        |
| --------------------------------------- | ------------------------------- | ------------------------------ | ---------------------------- |
| Vhodné pro Claude Code                  | výborné, vše v kódu             | střední, část práce v editoru  | slabé, hodně práce v editoru |
| Prohlížeč                               | nejlehčí a nejrychlejší         | ano, větší stažení (~30–40 MB) | těžké, na mobilu slabší      |
| Android / iOS                           | přes Capacitor                  | nativně                        | nativně                      |
| 3D komiksový styl (toon shader, obrysy) | ano (MeshToonMaterial + obrysy) | ano                            | ano                          |
| Cena                                    | zdarma                          | zdarma                         | zdarma do limitu             |

Co to znamená prakticky:

- **Postavy** vzniknou z dětských kreseb (postup v kapitole 6). Pro šedý prototyp stačí jednoduché tvary z kódu.
- **Android:** sestavení přes Android Studio. **iOS:** sestavení přes Xcode na Macu a účet Apple Developer (99 USD/rok), Google Play jednorázově 25 USD. To jsou kroky pro člověka, ne pro Claude Code.
- Kód bude v repozitáři na GitHubu, aby se dal sledovat a vracet zpět.

Technické zásady:

- Orientace na šířku (landscape). Ovládání myší i dotykem stejně: vše se dělá jedním kliknutím / ťuknutím, nic se netáhne a nic nezávisí na najetí myší (hover), protože na dotyku neexistuje.
- Cíl 60 fps na střední třídě Androidu (např. 3 roky starý telefon), minimálně 30 fps.
- Low-poly modely (do ~3 000 trojúhelníků na postavu), toon shader + obrysy, žádné dynamické stíny kromě jednoduchého „blob“ stínu pod postavou.
- Kamera: pevný šikmý pohled shora a z boku (asi 50–60°), bez otáčení, bez zoomu a bez posouvání. Celá mapa se vejde na obrazovku.
- Různé poměry stran (telefon 20:9, tablet 4:3, monitor 16:9): mapa se vždy celá vejde, na širších obrazovkách se po stranách jen doplní dekorace pozadí.

## 3. Základní herní smyčka

1. Úroveň začne s rozpočtem vody.
2. Hráč ťukne na volné políčko u cesty → vybere zeleninu → zelenina se „zasadí“ a několik vteřin roste.
3. Po vyrostení zelenina sama útočí na fast food v dosahu.
4. Fast food jde po cestě k puse. Po určitém počtu zásahů upustí kapku vody, otočí se a utíká zpět po cestě. Utíkající už nikomu neškodí, nedá se zasáhnout a po opuštění mapy zmizí úplně (nevrací se). Vlna mezitím pokračuje dál.
5. Voda se sbírá sama: kapka vyskočí z utíkajícího fast foodu, chvilku se zatřpytí a obloukem odletí do počítadla vody nahoře (počítadlo poskočí a „žbluňkne“). Hráč za ni sází nebo vylepšuje.
6. Když fast food dojde do pusy, kousne (pusa ztratí jeden ze 3 životů) a zmizí. Výhra: všechny vlny odraženy a pusa má aspoň jeden život. Prohra: čtvrté kousnutí → pusa se vyzvrací → opakovat úroveň.

## 4. První úroveň: „Snídaňová cesta“ (pracovní název)

### Cíl úrovně

Naučit hráče sázet, vylepšovat a poznat obě zeleniny a oba fast foody. Pro sedmileté dítě, které poslouchá tutoriál, má být úroveň dobře hratelná napoprvé.

### Obsah

- **Obránci:** **Mrkev** (blízko, levná) a **Pórek** (lučišník, daleko, dražší). Pórek se odemkne během úrovně, až si hráč osahá mrkev.
- **Útočníci:** **Hamburger** a **Hranolky**. Hranolky přijdou až ve 3. vlně, protože umí na chvilku zmrazit obránce a hráč na to musí být připravený.
- **Mapa:** celá na jedné obrazovce, žádné posouvání. Jedna cesta tvaru „S“ od okraje obrazovky k puse, chůze hamburgeru po celé cestě ~20 s.
- **Políčka na sázení:** 12 políček podél cesty, k dohrání stačí asi 6. Hodně místa, jak říkají požadavky. Část políček je blízko cesty (dobrá pro mrkev), část dál (dobrá pro pórek, mimo dosah hranolek).
- **Pusa (cíl):** jen velká komiksová pusa na konci cesty, bez obličeje kolem (případně jen náznak tváří). Má vlastní výrazy: klid, strach, kousnutí, zezelenání, úsměv.

### Výchozí čísla (k playtestu)

| Položka               | Mrkev                                                | Pórek                                                |
| --------------------- | ---------------------------------------------------- | ---------------------------------------------------- |
| Cena                  | 40                                                   | 60                                                   |
| Doba růstu            | 3 s                                                  | 4 s                                                  |
| Dosah                 | jen sousední úsek cesty (~1,5 políčka)               | ~3,5 políčka                                         |
| Útok                  | 1 zásah za 1 s (mrkvomeč)                            | 1 zásah za 1,5 s (malý pórek)                        |
| Vylepšení na úroveň 2 | 30 vody: o 40 % rychlejší sek, trochu větší mrkvomeč | 45 vody: dosah +1 políčko a o 20 % rychlejší střelba |

| Položka          | Hamburger             | Hranolky                                                                              |
| ---------------- | --------------------- | ------------------------------------------------------------------------------------- |
| Zásahů do útěku  | 4                     | 5                                                                                     |
| Rychlost chůze   | pomalá (~1 políčko/s) | o něco rychlejší (~1,3 políčka/s)                                                     |
| Schopnost        | žádná, jen ťapká      | jednou za 5 s hodí hranolku na nejbližšího obránce do ~2,5 políčka, ten na 2 s ztuhne |
| Voda za odražení | 15                    | 20                                                                                    |

Startovní voda: **120** (stačí na 3 mrkve nebo 2 mrkve a pórek po odemčení).

### Vlny

| Vlna       | Obsah                                                                  | Co se hráč naučí                                         |
| ---------- | ---------------------------------------------------------------------- | -------------------------------------------------------- |
| 1          | 3 hamburgery, rozestup 4 s                                             | sázet mrkev, voda se sbírá sama                          |
| 2          | 6 hamburgerů, rozestup 3 s                                             | odemkne se pórek: střílí z dálky                         |
| 3          | 4 hamburgery + 2 hranolky                                              | hranolky zmrazí obránce, pórek dál od cesty je v bezpečí |
| 4 (finále) | 8 hamburgerů + 4 hranolky, na konci jeden „velký“ hamburger (7 zásahů) | vylepšení, kombinace mrkve a pórku                       |

Mezi vlnami pauza, dokud hráč neklikne na „Další vlna“ (bez časového tlaku). Celá úroveň trvá zhruba 4 až 6 minut.

### Tutoriál (krok za krokem)

Krátké věty (do 8 slov), velké písmo a obrázky, protože sedmileté dítě ještě čte pomalu. Texty jsou jen psané a česky. Všechny texty budou v jednom souboru, aby se později daly snadno přeložit nebo namluvit. Text zmizí až po kliknutí, aby si ho dítě stihlo přečíst.

1. Cesta se rozsvítí od startu k puse (kamera se nehýbe). Text: „Fast food chce do pusy. Zastav ho!“
2. Bliká první políčko → „Klikni sem a zasaď mrkev.“
3. Mrkev roste (ukazatel růstu). → „Mrkev chvilku roste, pak začne bránit.“
4. Přijde vlna 1. Po prvním odraženém hamburgeru: „Hamburger utíká! A nechal ti vodu.“ (kapka sama odletí do počítadla)
5. Před vlnou 2: velká animace „Nová zelenina: Pórek!“ → „Pórek střílí z dálky. Zasaď ho dál od cesty.“
6. Před vlnou 3: představení hranolek → „Pozor! Hranolky házejí hranolky a zelenina na chvilku ztuhne. Pórek je daleko, tam nedohodí.“
7. Před vlnou 4: „Klikni na zeleninu a vylepši ji.“
8. Konec: oslava zeleniny, hodnocení hvězdičkami podle zbylých životů pusy (3 = ⭐⭐⭐, návrh), odemknutí úrovně 2.

### Prohra

Pusa má **3 životy** (zobrazené jako 3 zoubky nebo srdíčka nahoře). Každý fast food, který dojde do pusy, jednou kousne: pusa se zašklebí, trochu zezelená a ubude jeden život. Fast food pak zmizí. Po každém kousnutí je pusa zelenější.

Čtvrté kousnutí = prohra: animace „zelená tvář, vyzvracení“ (komiksově a vtipně, ne nechutně, kvůli věku 7+) → obrazovka „Zkusit znovu“.

Vlna končí, když na mapě nezbývá žádný fast food (všechny buď utekly, nebo kously).

## 5. Ovládání a obrazovka

- Funguje stejně myší i dotykem: jedno kliknutí / ťuknutí na všechno.
- Horní lišta: voda 💧, životy pusy (3 zoubky), číslo vlny (1/4), pauza.
- Klik na volné políčko → malé kruhové menu se zeleninou a cenou (na co není voda, je zašedlé).
- Klik na zasazenou zeleninu → zobrazí dosah + tlačítko Vylepšit s cenou. Po vylepšení na úroveň 2 tlačítko zmizí (v 1. úrovni hry víc nejde). Prodej ani přesazení v 1. úrovni nejsou.
- Při výběru zeleniny se na mapě ukáže její dosah ještě před zasazením, aby dítě vidělo, kam dosáhne.
- Tlačítko „Rychle ×2“ v 1. úrovni nebude (návrh). Mezi vlnami je pauza, takže hráč nemusí čekat. Dá se přidat později.
- Všechny klikací cíle minimálně 48 dp (pohodlné pro dětské prsty).
- Žádný zoom, žádné posouvání mapy.

## 6. Grafika a animace pro 1. úroveň

### Styl

Svět (záhon, cesta, pusa, pozadí) je 3D s pevnou kamerou shora a z boku, komiksově nasvícený, s obrysy. Postavy vycházejí z dětských kreseb, takže hra bude vypadat jako dětský obrázek, který ožil. Humor pro děti od 7 let.

### Jak z kresby udělat postavu (doporučený postup)

**Doporučení: „papírové loutky“ ve 3D světě.** Každá kresba se nafotí, ořízne a rozdělí na díly (tělo, ruce, nohy, zbraň, oči, pusa). Díly stojí ve 3D scéně jako ploché loutky natočené ke kameře a Claude Code je rozpohybuje v kódu: pohupování, skákání, zmáčknutí při zásahu, máchnutí mrkvomečem, mrkání.

- Výhody: zůstane přesně kresba dítěte (čáry, barvy, styl). Claude Code to zvládne celé sám. Nová postava = nová kresba, bez modelování.
- Alternativa: Claude Code podle kresby postaví jednoduchý 3D model z tvarů (koule, válce) a kresbu použije jako předlohu barev. Je to víc „3D“, ale méně podobné kresbě. Dá se zkusit na jedné postavě a porovnat.

### Návod pro malého kreslíře

- Každá postava na samostatný bílý papír, zepředu, přes velkou část papíru.
- Silné černé obrysy (fix), vybarvit pastelkami nebo fixy, nic přes okraj postavy.
- Ideálně zvlášť nakreslit to, co se hýbe: ruce, nohy, zbraň (mrkvomeč, luk pórku, hranolka na hod).
- Výrazy navíc na samostatný papír: vyděšený hamburger a hranolky (útěk), zmrzlý obránce, pusa ve 4 výrazech (klid, kousnutí, zelená, úsměv).
- Vyfotit za denního světla, kolmo shora, bez stínu, a obrázky dát do složky projektu (např. `Fast Food Fight/kresby/`).

Potřebné kresby pro 1. úroveň: mrkev, pórek, hamburger, hranolky, pusa (4 výrazy), kapka vody. Vylepšené verze (úroveň 2) můžou být kresba s doplňkem (helma, větší meč), nebo je Claude Code udělá z původní kresby barevným odleskem a hvězdičkou.

### Seznam animací

- **Mrkev:** vyrůstání ze země, klid (pohupování), sek mrkvomečem, ztuhnutí po zásahu hranolkou (namodrání, kmitání), radost po odražení, vylepšená verze.
- **Pórek:** vyrůstání, klid, natažení a výstřel malého pórku (let obloukem), ztuhnutí, radost, vylepšená verze.
- **Hamburger:** chůze „ťap ťap“, zásah (zmáčknutí, kapka kečupu), otočení a útěk s vyděšeným výrazem, upuštění kapky vody.
- **Hranolky:** chůze (krabička poskakuje), hod hranolkou (let + „plesk“ na obránci), zásah, útěk, upuštění kapky.
- **Utíkající fast food:** na okraji mapy „pufne“ v obláčku a zmizí, aby bylo jasné, že se nevrátí.
- **Voda:** kapka vyskočí, zatřpytí se, obloukem odletí do počítadla nahoře, počítadlo poskočí.
- **Pusa:** klid, nervózní pohled při blízkém fast foodu, kousnutí (zašklebení, 3 stupně zelenosti), vyzvracení (prohra, komiksově), úsměv (výhra).
- **Prostředí (návrh):** zeleninový záhon na kuchyňském stole, cesta z prostírání vede k puse, částice kapek a hvězdiček při zásahu.

Zvuk: veselá smyčka hudby, zvuky zasazení, seknutí, výstřelu pórku, hodu hranolkou, „au“ fast foodu, letící kapky vody, výhry a prohry. (Zvuky se dají vzít z volných knihoven s licencí CC0.)

## 7. Co postavit a v jakém pořadí

1. **Šedý prototyp** (krabičky místo postav; mezitím dítě kreslí postavy, Three.js v prohlížeči): mapa na jedné obrazovce, políčka, mrkev, pórek, hamburger, hranolky se zmrazením, automatický sběr vody, 3 životy pusy, výhra/prohra. Vyzkoušet na telefonu i s myší v prohlížeči.
2. **Tutoriál a vlny**: skripty tutoriálu, 4 vlny, vylepšení.
3. **Grafika a animace**: nafocené kresby převést na postavy do hry, animace, prostředí, UI.
4. **Zvuk a doladění**: hudba, efekty, vyvážení čísel podle playtestu s dětmi.
5. **Vydání** (zdarma): webová verze na odkaz, pak Android (Capacitor, APK pro testery) a iOS (Capacitor, TestFlight).

## 8. Kdy je 1. úroveň hotová

- Hraje se plynule na telefonu s Androidem, v mobilním prohlížeči (iOS Safari, Android Chrome) i na počítači s myší.
- Celá mapa je vidět bez posouvání na telefonu, tabletu i monitoru.
- Sedmileté dítě projde tutoriál bez vysvětlování od dospělého.
- Úroveň trvá 4 až 6 minut.
- Výhra i prohra mají vlastní animaci a obrazovku.
- Po výhře se odemkne úroveň 2 a stav se uloží v zařízení.

---

## Další krok

Plán je hotový a připravený k programování. Navrhované pořadí:

1. Dítě začne kreslit postavy podle návodu v kapitole 6.
2. Souběžně Claude Code postaví šedý prototyp 1. úrovně v Three.js (kapitola 7, krok 1), aby se dal co nejdřív vyzkoušet na telefonu.
3. Až budou kresby, přidá se grafika a animace.

Pro programování je potřeba repozitář na GitHubu (např. `fast-food-fight`), do kterého bude Claude Code ukládat kód.
