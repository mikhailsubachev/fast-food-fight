// 3. úroveň „Oběd v Mekáči“ podle návrhu na plátně (design/zdroj/Uroven3D.dc.html): stejná louka,
// cesta a mřížka jako v 1. a 2. úrovni, ale na louce leží zbytky oběda z fast foodu a místa na sázení
// je ještě míň. Přibývá brokolice (obránce) a kečup (útočník).
import { catmullRom, clipStartAtX } from '../core/path';
import { BOARD, HEX_GRID, MOUTH, PATH_CONTROL, SLOT_RULES, VIEW, seq, type LevelData } from './level1';
import type { AttackerType } from './units';

const H: AttackerType = 'hamburger';
const F: AttackerType = 'hranolky';
const B: AttackerType = 'velkyHamburger';
const L: AttackerType = 'lizatko';
const K: AttackerType = 'kecup';

/** Pauza `first` sekund před prvním fast foodem náporu. */
const burst = (types: AttackerType[], gap: number, first: number) => seq(types, gap, first);

export const LEVEL3: LevelData = {
  id: 3,
  name: 'Oběd v Mekáči',
  ground: 'louka-3.svg',
  path: clipStartAtX(catmullRom(PATH_CONTROL), BOARD.minX),
  // Polohy a poloměry z generátoru návrhu (design/generator/gen_level3.py); políčka pod nimi jsou šedá.
  obstacles: [
    { kind: 'tac', x: 1.5, z: 8.6, r: 1.5 },
    { kind: 'kelimek', x: 8.9, z: 8.9, r: 1.15 },
    { kind: 'ubrousky', x: 8.7, z: 3.9, r: 1.15 },
    { kind: 'omacky', x: 5.0, z: 1.4, r: 1.05 },
    { kind: 'uctenka', x: 13.4, z: 2.9, r: 1.35 },
    { kind: 'krabicka', x: 15.2, z: 6.0, r: 0.8 },
    { kind: 'papir', x: 0.9, z: 5.2, r: 1.0 },
    { kind: 'kelimek', x: 11.9, z: 1.2, r: 1.1 },
    { kind: 'ubrousky', x: 4.75, z: 4.9, r: 1.0 },
  ],
  board: BOARD,
  hexGrid: HEX_GRID,
  slotRules: SLOT_RULES,
  view: VIEW,
  mouth: MOUTH,
  // V návrhu má hráč na začátku 180 vody a 6 vln.
  startWater: 180,
  startDefenders: ['mrkev', 'porek', 'cibule'],
  unlocks: [{ wave: 1, type: 'brokolice' }],
  waveSpeed: [1, 1.25, 1.45, 1.6, 1.75, 1.95],
  // Za odražený fast food je jen polovina vody: zahrádka se plní pomaleji a záleží na tom, co a kam
  // hráč zasadí (plná zahrádka by jinak porazila cokoliv).
  rewardScale: 0.5,
  waves: [
    // 1. vlna: rozehřátí známým fast foodem.
    seq([H, H, F, H, H, F, H, F], 2.4),
    // 2. vlna: jen kečupy – prskají louže a fast food po nich klouže.
    seq(Array(12).fill(K), 1.05),
    // 3. vlna: kečupy rozlijí cestu a hamburgery po ní sjedou k puse.
    [
      ...seq([K, H, H, K, H, H, K, H, H, K, H], 0.55),
      ...burst([K, K, H, H, H, H, K, H, H, K, H, H], 0.5, 2.4),
    ],
    // 4. vlna: lízátka lepí zeleninu, kečupy je posílají rychleji.
    [
      ...seq([L, K, L, L, K, L, F, L, K, L, F], 0.55),
      ...burst([L, L, K, F, L, K, L, F, L, K, L, K], 0.5, 2.4),
    ],
    // 5. vlna: velké hamburgery na kečupové klouzačce.
    [...seq([K, B, K, B, B, K, B, B, K], 0.65), ...burst([K, K, B, B, K, B, B, K, B, B, K], 0.55, 2.4)],
    // 6. vlna (finále): všechno najednou ve čtyřech náporech.
    [
      ...seq([H, K, F, L, H, K, B, L, F, K, B, H, K, L], 0.4),
      ...burst([K, L, F, B, K, H, L, F, B, K, L, H, F, K, B], 0.36, 2),
      ...burst([B, K, L, F, B, K, L, B, F, K, L, B, K, F, B], 0.36, 2),
      ...burst([K, B, B, L, K, F, B, K, L, B, B, K, B, L], 0.36, 2),
    ],
  ],
};
