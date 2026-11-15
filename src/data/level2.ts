// 2. úroveň „Školní svačina“ podle návrhu na plátně (design/zdroj/Uroven2D.dc.html,
// generátor design/generator/gen_level2.py): stejná louka, cesta a mřížka jako v 1. úrovni,
// ale místo pařezu a spol. na ní leží školní věci. Přibývá cibule (obránce) a lízátko (útočník).
import { catmullRom, clipStartAtX } from '../core/path';
import { BOARD, HEX_GRID, MOUTH, PATH_CONTROL, SLOT_RULES, VIEW, seq, type LevelData } from './level1';
import type { AttackerType } from './units';

const H: AttackerType = 'hamburger';
const F: AttackerType = 'hranolky';
const B: AttackerType = 'velkyHamburger';
const L: AttackerType = 'lizatko';

export const LEVEL2: LevelData = {
  id: 2,
  name: 'Školní svačina',
  ground: 'louka-2.svg',
  path: clipStartAtX(catmullRom(PATH_CONTROL), BOARD.minX),
  // Školní věci z návrhu leží naplocho na louce; zaberou víc políček než pařez nebo kámen.
  obstacles: [
    { kind: 'box', x: 1.6, z: 8.6, r: 1.3 },
    { kind: 'lahev', x: 8.9, z: 8.9, r: 1.2 },
    { kind: 'penal', x: 8.6, z: 3.9, r: 1.1 },
    { kind: 'sesit', x: 13.4, z: 2.9, r: 1.2 },
    { kind: 'pastelky', x: 5.0, z: 1.4, r: 1.0 },
    { kind: 'guma', x: 15.2, z: 5.9, r: 0.6 },
  ],
  board: BOARD,
  hexGrid: HEX_GRID,
  slotRules: SLOT_RULES,
  view: VIEW,
  mouth: MOUTH,
  // V návrhu má hráč na začátku 150 vody a 5 vln.
  startWater: 150,
  startDefenders: ['mrkev', 'porek'],
  unlocks: [{ wave: 1, type: 'cibule' }],
  waveSpeed: [1, 1.1, 1.2, 1.3, 1.5],
  waves: [
    // 1. vlna: hamburgery a hranolky na rozehřátí.
    seq([H, H, H, H, H], 3.5),
    // 2. vlna: první lízátka.
    seq([H, L, H, H, F, L, H, L], 2.2),
    // 3. vlna: lízátka chodí ve dvojicích a lepí zeleninu, hranolky ji zmrazí.
    seq([L, L, H, F, H, L, L, F, H, H, F, L, L, H], 1.3),
    // 4. vlna: velké hamburgery za hradbou lízátek.
    [...seq([L, H, L, F, B, L, F, H, B, L], 1.0), ...seq([F, L, B, H, L, F, B, L, L], 0.9, 4)],
    // 5. vlna (finále): tři husté nápory.
    [
      ...seq([H, L, F, H, L, F, B, L, F, B], 0.7),
      ...seq([L, L, F, B, H, L, F, B, L, F, H, B], 0.65, 3.5),
      ...seq([B, L, F, B, L, L, F, B, L, B, F, B], 0.6, 3.5),
    ],
  ],
};
