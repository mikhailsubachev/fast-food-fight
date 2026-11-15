# Plán druhé úrovně: Školní svačina

Podle návrhu na plátně „Úroveň 2 – Školní svačina“ (`design/zdroj/Uroven2D.dc.html`, generátor `design/generator/gen_level2.py`) a listů postav Pan Cibule a Lízátko. Čísla jsou návrh pro první playtest.

## Mapa

- Stejná louka, cesta a celá mřížka šestihranů jako v 1. úrovni.
- Místo pařezu, kamene, kaluže a krtiny leží na louce školní věci: svačinový box, láhev, penál, sešit, pastelky a guma. Jsou větší, takže zaberou víc políček (šedá v mřížce) a míst na sázení je méně (41 místo 48, stejně jako v návrhu).
- Úroveň se odemkne výhrou v 1. úrovni. Na konci 1. úrovně je tlačítko „Úroveň 2“, v pauze se dá přepnout na jinou odemčenou úroveň.

## Nový obránce: Pan Cibule

- Cena 50 vody, roste 4 s, vylepšení 40 vody.
- Sám nikoho nezasáhne. Jednou za 6 s, jen když je fast food v dosahu, se naježí a vypustí oblak smradu asi 2 políčka kolem sebe.
- Fast food v oblaku kýchá a dusí se a jde poloviční rychlostí, dokud oblak po 3 s nevyvětrá. Mrkve a pórky tak mají víc času.
- Úroveň 2: větší oblak (2,5 políčka), vydrží 4,5 s.
- Odemkne se před 2. vlnou.

## Nový útočník: Lízátko

- 6 zásahů do útěku, chodí asi 1 políčko/s, za odražení 25 vody.
- Jednou za 6 s (poprvé 3 s po vstupu na mapu, a jen když je zelenina blízko) se zastaví a roztočí. Všechna vyrostlá zelenina do 1,5 políčka se oblepí sladkou šťávou a 3 s nebojuje; šťáva z ní postupně stéká.
- Rostoucí zelenina je schovaná v zemi a oblepit nejde.

## Vlny

| Vlna | Kdo přijde | Rychlost |
| ---- | ---------- | -------- |
| 1 | jen hamburgery (6) | normální |
| 2 | jen hranolky (9) | o 10 % rychlejší |
| 3 | jen lízátka (12) | o 20 % rychlejší |
| 4 | jen velké hamburgery (8) | o 30 % rychlejší |
| 5 (finále) | všechno smíchané ve třech hustých náporech | o 50 % rychlejší |

Každá z prvních čtyř vln ukáže jen jeden druh fast foodu, aby se ho hráč naučil. Na začátku je 150 vody, k dispozici mrkev a pórek. Obtížnost ověřená simulací v testech (`tests/level2.test.ts`): plná zahrádka (6 mrkví, 4 pórky, 2 cibule) s vylepšením vyhraje na 3 hvězdy; bez vylepšení se úroveň prohraje.
