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
  waveSpeed: [1, 1.15, 1.3, 1.45, 1.6],
  // Každá z prvních čtyř vln přinese jen jeden druh fast foodu, aby se ho hráč naučil;
  // v páté se všechny smíchají.
  waves: [
    // 1. vlna: jen hamburgery.
    seq(Array(8).fill(H), 2.4),
    // 2. vlna: jen hranolky – házejí zdálky a zmrazí zeleninu.
    seq(Array(11).fill(F), 1.7),
    // 3. vlna: jen lízátka – točí se a oblepí zeleninu kolem sebe.
    seq(Array(18).fill(L), 1.0),
    // 4. vlna: jen velké hamburgery, ve dvou náporech.
    [...seq(Array(7).fill(B), 1.2), ...seq(Array(7).fill(B), 1.0, 4)],
    // 5. vlna (finále): všechno dohromady ve čtyřech náporech.
    [
      ...seq([H, L, F, H, L, F, B, L, F, B, H, L], 0.6),
      ...seq([L, L, F, B, H, L, F, B, L, F, H, B, L, F], 0.55, 3),
      ...seq([B, L, F, B, L, L, F, B, L, B, F, B, H, L], 0.5, 3),
      ...seq([B, B, L, F, B, L, B, F, B, L, B, B], 0.5, 3),
    ],
  ],
};
