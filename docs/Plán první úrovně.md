# Fast Food Fight: plán první úrovně

Stav: **finální plán v7** (v7: sází se do viditelné šestihranné mřížky; 14. 11. 2026, všechny odpovědi od Mika zapracované; v5 doplnila automatické spouštění vln, v6 mění sázení: v 1. úrovni se sází téměř kamkoliv, v dalších úrovních místa ubývá). Čísla jsou výchozí odhad pro první playtest a doladí se podle hraní s dětmi. Body označené „(návrh)“ jsou moje doporučení, která na otázkách nezávisí a dají se kdykoli změnit.

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
- Mezi vlnami je krátká pauza a další vlna se spustí sama. Celá 1. úroveň trvá do 5 minut.
- Sází se do viditelné šestihranné mřížky, jedna zelenina na šestihran. V 1. úrovni jsou volné skoro všechny šestihrany (ne ty na cestě a pod pár malými překážkami). V dalších úrovních bude místa na zeleninu míň a míň.

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

- Orientace na šířku (landscape). Na telefonu na výšku hra poprosí o otočení. Ovládání myší i dotykem stejně: vše se dělá jedním kliknutím / ťuknutím, nic se netáhne a nic nezávisí na najetí myší (hover), protože na dotyku neexistuje.
- Cíl 60 fps na střední třídě Androidu (např. 3 roky starý telefon), minimálně 30 fps.
- Prostředí a případné 3D modely postav jsou low-poly (do ~3 000 trojúhelníků na model). Papírové loutky z kreseb mají místo toho limit na obrázek: nejvýš 1024 × 1024 px na postavu, aby se hra na telefonu rychle načetla. Toon shader + obrysy, žádné dynamické stíny kromě jednoduchého „blob“ stínu pod postavou.
- Kamera: pevný šikmý pohled shora a z boku podle návrhu úrovně na plátně: pravoúhlý, bez perspektivy (postavy mají všude stejnou velikost), sklon asi 64°, bez otáčení, bez zoomu a bez posouvání. Na obrazovce je celý záhon 16 × 9 políček. Cesta z návrhu vstupuje zleva, klikatí se dolů, nahoru kolem kaluže, znovu dolů a nahoru a končí vpravo u pusy (asi 26 políček). Fast food, který zakrývá zeleninu, zprůhlední; zelenina je vidět vždy.
- Celá obrazovka: na telefonu a tabletu se hra při prvním ťuknutí přepne na celou obrazovku (Android navíc zamkne otočení na šířku), v horní liště je tlačítko pro zapnutí a vypnutí. iPhone to u webových stránek neumí; tam tlačítko poradí „Sdílet → Přidat na plochu“ a hra z plochy běží přes celou obrazovku.
- Různé poměry stran (telefon 20:9, tablet 4:3, monitor 16:9): mapa se vždy celá vejde, na širších obrazovkách se po stranách jen doplní dekorace pozadí.

## 3. Základní herní smyčka

1. Úroveň začne s rozpočtem vody.
2. Hráč ťukne na volný šestihran na záhoně → vybere zeleninu → zelenina se „zasadí“ a několik vteřin roste.
3. Po vyrostení zelenina sama útočí na fast food v dosahu. Zásah se počítá až ve chvíli, kdy zbraň doletí nebo dosekne. Když se cíl mezitím otočí k útěku, letící pórek dopadne na zem, udělá „puf“ a zmizí. Nikdy se nezapočítá víc zásahů, než je potřeba k útěku.
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
- **Sázení:** do šestihranných políček podle návrhu úrovně, jedna zelenina na políčko. Volná políčka jsou světle zelená, osázená hnědá, vybrané bílé. Políčka jsou skoro po celém záhonu, kromě cesty, 4 malých překážek (pařez, kámen, kaluž, krtina) a místa u pusy. Ťuknutí kousek vedle políčka ho také vybere a zelenina se zasadí doprostřed. „Políčko“ jako jednotka vzdálenosti (dosah, rychlost) dál platí. Mrkev se vyplatí sázet do políček u cesty, pórek dál, mimo dosah hranolek. Zelenina zasáhne fast food, jakmile se kruh jejího dosahu dotkne okraje jeho těla. K dohrání stačí asi 6 až 10 rostlin.
- **Pusa (cíl):** jen velká komiksová pusa na konci cesty, bez obličeje kolem (případně jen náznak tváří). Má vlastní výrazy: klid, strach (fast food je blízko), kousnutí, zelená (3 stupně), vyzvracení, úsměv. Dítě kreslí 5 z nich (klid, strach, kousnutí, zelená, úsměv); stupně zelenosti a vyzvracení udělá Claude Code v kódu ze „zelené“ kresby.

### Místo na zeleninu v dalších úrovních (návrh)

- **1. úroveň:** všechny šestihrany kromě cesty a 4 malých překážek (pařez, kámen, kaluž, krtina), hráč se učí, kam se co hodí.
- **2. úroveň:** na stole a záhonu leží překážky (hrnek, solnička, ubrousek, kaluž od mléka), kam sázet nejde. Volného místa ubude zhruba na polovinu.
- **3. úroveň a dál:** zbydou jen menší záhonky podél cesty a nakonec jen pár pevných míst, takže každé zasazení je důležité rozhodnutí.

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
| Zásahů do útěku  | 5                     | 6                                                                                     |
| Rychlost chůze   | pomalá (~1 políčko/s) | o něco rychlejší (~1,3 políčka/s)                                                     |
| Schopnost        | žádná, jen ťapká      | jednou za 5 s hodí hranolku na nejbližšího vyrostlého obránce do ~1,6 políčka, ten na 2 s ztuhne (rostoucí zelenina je ještě schovaná v zemi a hranolky ji netrefí) |
| Voda za odražení | 15                    | 20                                                                                    |

**Velký hamburger** (jen na konci vlny 4): o polovinu větší, vydrží 8 zásahů, chodí pomaleji (~0,8 políčka/s), aby ho hráč stihl odrazit, za odražení dá 40 vody. Když dojde do pusy, kousne jen jednou jako ostatní.

Startovní voda: **120** (stačí na 3 mrkve nebo 2 mrkve a pórek po odemčení).

### Vlny

| Vlna       | Obsah                                                                  | Co se hráč naučí                                         |
| ---------- | ---------------------------------------------------------------------- | -------------------------------------------------------- |
| 1          | 3 hamburgery, rozestup 4 s                                             | sázet mrkev, voda se sbírá sama                          |
| 2          | 6 hamburgerů, rozestup 3 s                                             | odemkne se pórek: střílí z dálky                         |
| 3          | 8 hamburgerů + 6 hranolek, rozestup 1,3 s, fast food o 30 % rychlejší | hranolky zmrazí obránce, pórek dál od cesty je v bezpečí |
| 4 (finále) | 4 husté nápory: 9 hamburgerů + 19 hranolek + 16 „velkých“ hamburgerů (8 zásahů), o 50 % rychlejší | vylepšení, kombinace mrkve a pórku |

Mezi vlnami pauza, pár sekund na oddechnutí. Další vlna se spouští automaticky. Celá úroveň je do 5 min.

Obtížnost (ověřeno simulací v testech): 3. a 4. vlna jsou záměrně těžké. Hráč, který sází i vylepšuje, vyhraje (na delší cestě i na ⭐⭐⭐); se 3 mrkvemi a 4 pórky bez vylepšení prohraje.

- Pauza mezi vlnami trvá **8 s**, aby dítě stihlo zasadit nebo vylepšit zeleninu.
- Odpočet je vidět velkými čísly (poslední 3 s jako 3-2-1). Tlačítko „Hned!“ odpočet přeskočí.
- Když je na obrazovce text tutoriálu, odpočet stojí a rozběhne se až po jeho zavření kliknutím.
- Odhad délky: vlny samotné asi 3 minuty, k tomu 3 pauzy a tutoriál, celkem do 5 minut.

### Tutoriál (krok za krokem)

Krátké věty (do 8 slov), velké písmo a obrázky, protože sedmileté dítě ještě čte pomalu. Texty jsou jen psané a česky. Všechny texty budou v jednom souboru, aby se později daly snadno přeložit nebo namluvit. Text zmizí až po kliknutí, aby si ho dítě stihlo přečíst. Dokud je text vidět, odpočet do další vlny stojí.

1. Cesta se rozsvítí od startu k puse (kamera se nehýbe). Text: „Fast food chce do pusy. Zastav ho!“
2. Bliká místo u cesty → „Klikni sem a zasaď mrkev.“
3. Mrkev roste (ukazatel růstu). → „Mrkev chvilku roste, pak začne bránit.“
4. Přijde vlna 1. Po prvním odraženém hamburgeru: „Hamburger utíká! A nechal ti vodu.“ (kapka sama odletí do počítadla)
5. Před vlnou 2: velká animace „Nová zelenina: Pórek!“ → „Pórek střílí z dálky. Zasaď ho dál od cesty.“
6. Před vlnou 3: představení hranolek → „Pozor! Hranolky házejí hranolky a zelenina na chvilku ztuhne. Pórek je daleko, tam nedohodí.“
7. Před vlnou 4: „Klikni na zeleninu a vylepši ji.“
8. Konec: oslava zeleniny, hodnocení hvězdičkami podle zbylých životů pusy (3 = ⭐⭐⭐, návrh), odemknutí úrovně 2: animace odemčeného zámku a obrazovka „Úroveň 2 – brzy!“ (úroveň 2 zatím neexistuje). Odemčení se uloží v zařízení.

### Prohra

Pusa má **3 životy** (zobrazené jako 3 zoubky nebo srdíčka nahoře). Každý fast food, který dojde do pusy, jednou kousne: pusa se zašklebí, trochu zezelená a ubude jeden život. Fast food pak zmizí. Po každém kousnutí je pusa zelenější.

Čtvrté kousnutí = prohra: animace „zelená tvář, vyzvracení“ (komiksově a vtipně, ne nechutně, kvůli věku 7+) → obrazovka „Zkusit znovu“.

Vlna končí, když na mapě nezbývá žádný fast food (všechny buď utekly, nebo kously).

## 5. Ovládání a obrazovka

- Funguje stejně myší i dotykem: jedno kliknutí / ťuknutí na všechno.
- Horní lišta: voda 💧, životy pusy (3 zoubky), číslo vlny (1/4), pauza.
- Pauza zastaví celou hru a ukáže 3 velká tlačítka: Pokračovat, Začít znovu, Zvuk zap/vyp. Hra se pozastaví i sama, když se telefon přepne do jiné aplikace nebo se zamkne.
- Klik na volný šestihran (rozsvítí se) → malé kruhové menu se zeleninou a cenou (na co není voda, je zašedlé). Kde sázet nejde (cesta, překážka, obsazený šestihran), ukáže se krátký červený křížek.
- Klik na zasazenou zeleninu → zobrazí dosah + tlačítko Vylepšit s cenou. Po vylepšení na úroveň 2 tlačítko zmizí (v 1. úrovni hry víc nejde). Prodej ani přesazení v 1. úrovni nejsou.
- Při výběru zeleniny se na mapě ukáže její dosah ještě před zasazením, aby dítě vidělo, kam dosáhne.
- Tlačítko „Rychle ×2“ v 1. úrovni nebude (návrh). Pauzy mezi vlnami jsou krátké a dají se přeskočit tlačítkem „Hned!“, takže hráč nemusí čekat. Dá se přidat později.
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
- Výrazy navíc na samostatný papír: vyděšený hamburger a hranolky (útěk), zmrzlý obránce, pusa v 5 výrazech (klid, strach, kousnutí, zelená, úsměv). Vyzvracení dítě kreslit nemusí, udělá ho Claude Code.
- Vyfotit za denního světla, kolmo shora, bez stínu, a obrázky dát do složky projektu (např. `Fast Food Fight/kresby/`).

Potřebné kresby pro 1. úroveň: mrkev, pórek, hamburger, hranolky, pusa (5 výrazů), kapka vody. Velký hamburger je zvětšený hamburger, samostatnou kresbu nepotřebuje. Vylepšené verze (úroveň 2) můžou být kresba s doplňkem (helma, větší meč), nebo je Claude Code udělá z původní kresby barevným odleskem a hvězdičkou.

### Seznam animací

- **Mrkev:** vyrůstání ze země, klid (pohupování), sek mrkvomečem, ztuhnutí po zásahu hranolkou (namodrání, kmitání), radost po odražení, vylepšená verze.
- **Pórek:** vyrůstání, klid, natažení a výstřel malého pórku (let obloukem), ztuhnutí, radost, vylepšená verze.
- **Hamburger:** chůze „ťap ťap“, zásah (zmáčknutí, kapka kečupu), otočení a útěk s vyděšeným výrazem, upuštění kapky vody.
- **Hranolky:** chůze (krabička poskakuje), hod hranolkou (let + „plesk“ na obránci), zásah, útěk, upuštění kapky.
- **Utíkající fast food:** na okraji mapy „pufne“ v obláčku a zmizí, aby bylo jasné, že se nevrátí.
- **Voda:** kapka vyskočí, zatřpytí se, obloukem odletí do počítadla nahoře, počítadlo poskočí.
- **Pusa:** klid, nervózní pohled při blízkém fast foodu, kousnutí (zašklebení, 3 stupně zelenosti přebarvením „zelené“ kresby), vyzvracení (prohra, komiksový zelený proud s hvězdičkami, nic nechutného), úsměv (výhra).
- **Pórek, který mine:** dopadne na zem, „puf“ a zmizí.
- **Odpočet mezi vlnami:** velká čísla 3-2-1, tlačítko „Hned!“.
- **Výhra:** odemčený zámek úrovně 2.
- **Prostředí (návrh):** zeleninový záhon na kuchyňském stole, cesta z prostírání vede k puse, částice kapek a hvězdiček při zásahu.

Zvuk: veselá smyčka hudby, zvuky zasazení, seknutí, výstřelu pórku, hodu hranolkou, „au“ fast foodu, letící kapky vody, výhry a prohry. (Zvuky se dají vzít z volných knihoven s licencí CC0.)

## 7. Co postavit a v jakém pořadí

1. **Šedý prototyp** (krabičky místo postav; mezitím dítě kreslí postavy, Three.js v prohlížeči): mapa na jedné obrazovce, sázení kamkoliv na záhon, mrkev, pórek, hamburger, hranolky se zmrazením, automatický sběr vody, 3 životy pusy, výhra/prohra. Vyzkoušet na telefonu i s myší v prohlížeči.
2. **Tutoriál a vlny**: skripty tutoriálu, 4 vlny, vylepšení.
3. **Grafika a animace**: nafocené kresby převést na postavy do hry, animace, prostředí, UI.
4. **Zvuk a doladění**: hudba, efekty, vyvážení čísel podle playtestu s dětmi.
5. **Vydání** (zdarma): webová verze na odkaz, pak Android (Capacitor, APK pro testery) a iOS (Capacitor, TestFlight).

## 8. Kdy je 1. úroveň hotová

- Hraje se plynule na telefonu s Androidem, v mobilním prohlížeči (iOS Safari, Android Chrome) i na počítači s myší.
- Celá mapa je vidět bez posouvání na telefonu, tabletu i monitoru.
- Sedmileté dítě projde tutoriál bez vysvětlování od dospělého.
- Úroveň trvá do 5 minut.
- Výhra i prohra mají vlastní animaci a obrazovku.
- Po výhře se odemkne úroveň 2 a stav se uloží v zařízení.

---

## Další krok

Plán je hotový a připravený k programování. Navrhované pořadí:

1. Dítě začne kreslit postavy podle návodu v kapitole 6.
2. Souběžně Claude Code postaví šedý prototyp 1. úrovně v Three.js (kapitola 7, krok 1), aby se dal co nejdřív vyzkoušet na telefonu.
3. Až budou kresby, přidá se grafika a animace.

Pro programování je potřeba repozitář na GitHubu (např. `fast-food-fight`), do kterého bude Claude Code ukládat kód.
