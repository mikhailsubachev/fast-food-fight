# Plán třetí úrovně: Oběd v Mekáči

Podle návrhu na plátně „Úroveň 3 – Oběd v Mekáči“ (`design/zdroj/Uroven3D.dc.html`) a listů postav Pan Brokolice a Pan Kečup. Čísla jsou návrh pro první playtest.

## Mapa

- Stejná louka, cesta a celá mřížka šestihranů jako v 1. a 2. úrovni.
- Na louce leží zbytky oběda z fast foodu: tác, dva kelímky, dva štůsky ubrousků, sáčky s omáčkou, účtenka, krabička od hranolek a papír od burgeru. Zaberou stejná (šedá) políčka jako v návrhu, místa na sázení je ještě méně (36).
- Úroveň se odemkne výhrou ve 2. úrovni.

## Nový obránce: Pan Brokolice

- Cena 80 vody, roste 5 s, vylepšení 60 vody. Nejdražší a nejpomalejší obránce, ale nejdál dostřelí (5 políček).
- Jednou za 2,5 s si utrhne z korunky růžičku a vystřelí ji jako raketu vysokým obloukem. Nad cílem se rozprskne do deštníku a každý fast food do 1 políčka dostane jeden zásah.
- Úroveň 2: dosah 5,5 políčka, větší deštník (1,4 políčka).
- Odemkne se před 2. vlnou.

## Nový útočník: Pan Kečup

- 5 zásahů do útěku, chodí asi 1 políčko/s, za odražení 20 vody (v této úrovni polovina, viz níže).
- Jednou za 7 s (poprvé 3 s po vstupu na mapu) se naštve, poskočí a vyprskne kečup na 3 políčka cesty před sebe. Na louži klouže každý fast food (i Pan Kečup sám) 2× rychleji k puse. Po 5 s louže zaschne.
- Hráč se mu brání tím, že ho odrazí dřív, než doprská.

## Vlny

| Vlna | Kdo přijde | Rychlost |
| ---- | ---------- | -------- |
| 1 | hamburgery a hranolky na rozehřátí (8) | normální |
| 2 | jen kečupy (12) | o 25 % rychlejší |
| 3 | kečupy s hamburgery ve dvou náporech (23) | o 45 % rychlejší |
| 4 | lízátka s kečupy a hranolkami ve dvou náporech (23) | o 60 % rychlejší |
| 5 | velké hamburgery na kečupové klouzačce (20) | o 75 % rychlejší |
| 6 (finále) | všechno najednou ve čtyřech náporech (58) | o 95 % rychlejší |

Na začátku je 180 vody, k dispozici mrkev, pórek a cibule.

## Obtížnost

Ve 2. úrovni přicházelo za odražený fast food tolik vody, že si hráč brzy zaplnil celou zahrádku a plná zahrádka porazila cokoliv. Proto je ve 3. úrovni za odražení jen polovina vody (`rewardScale` v datech úrovně): záleží na tom, co a kam hráč zasadí.

Ověřeno simulací v testech (`tests/level3.test.ts`):

- 8 mrkví, 6 pórků, 3 cibule a 4 brokolice s vylepšením vyhraje na 3 hvězdy.
- Stejná zahrádka bez brokolice vyhraje nanejvýš na 1 hvězdu.
- Bez vylepšení nebo s malou zahrádkou (6 + 4 + 2 + 2) se úroveň prohraje.
