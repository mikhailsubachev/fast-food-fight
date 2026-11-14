import { catmullRom, clipStartAtX } from '../core/path';
import type { Vec2 } from '../core/types';
import type { AttackerType, DefenderType } from './units';

export interface Spawn {
  type: AttackerType;
  /** Sekundy od předchozího fast foodu ve vlně. */
  delay: number;
}

export type ObstacleKind = 'parez' | 'kamen' | 'kaluz' | 'krtina';

export interface Obstacle extends Vec2 {
  kind: ObstacleKind;
  /** Poloměr překážky; zelenina se k ní nedá zasadit. */
  r: number;
}

export interface Rect {
  minX: number;
  maxX: number;
  minZ: number;
  maxZ: number;
}

export interface LevelData {
  id: number;
  name: string;
  /** Středová čára cesty od okraje záhonu k puse. */
  path: Vec2[];
  obstacles: Obstacle[];
  /** Záhon: obdélník, na který se dá sázet. */
  board: Rect;
  /** Výřez, který kamera vždy celý ukáže (o kousek menší než záhon kvůli většímu přiblížení). */
  view: Rect;
  mouth: Vec2;
  startWater: number;
  startDefenders: DefenderType[];
  /** Zelenina se odemkne před vlnou s tímto indexem (0 = první vlna). */
  unlocks: { wave: number; type: DefenderType }[];
  waves: Spawn[][];
  /** Násobek rychlosti chůze fast foodu v jednotlivých vlnách (pozdější vlny jsou rychlejší). */
  waveSpeed?: number[];
}

function seq(types: AttackerType[], gap: number): Spawn[] {
  return types.map((type, i) => ({ type, delay: i === 0 ? 0 : gap }));
}

const H: AttackerType = 'hamburger';
const F: AttackerType = 'hranolky';
const B: AttackerType = 'velkyHamburger';

const BOARD: Rect = { minX: -1, maxX: 12.2, minZ: 0.3, maxZ: 8.6 };

/** Řídicí body zvlněné cesty „S“ z návrhu (design/generator/curve.py). */
const PATH_CONTROL: Vec2[] = [
  { x: -4.5, z: 2.6 },
  { x: -1.8, z: 2.45 },
  { x: 0.6, z: 2.25 },
  { x: 3.0, z: 2.6 },
  { x: 5.6, z: 2.35 },
  { x: 7.6, z: 2.7 },
  { x: 8.5, z: 3.7 },
  { x: 7.9, z: 4.8 },
  { x: 6.2, z: 5.15 },
  { x: 4.2, z: 4.85 },
  { x: 2.6, z: 5.25 },
  { x: 2.1, z: 6.3 },
  { x: 3.0, z: 7.3 },
  { x: 5.0, z: 7.65 },
  { x: 7.4, z: 7.35 },
  { x: 9.9, z: 7.5 },
];

export const LEVEL1: LevelData = {
  id: 1,
  name: 'Snídaňová cesta',
  path: clipStartAtX(catmullRom(PATH_CONTROL), BOARD.minX),
  // Sází se téměř kamkoliv na záhon; nejde na cestu, na tyto překážky a těsně k jiné zelenině.
  // Polohy podle návrhu úrovně (design/artboardy/5-uroven-1.html).
  obstacles: [
    { kind: 'parez', x: 7.6, z: 0.9, r: 0.6 },
    { kind: 'kamen', x: 0.6, z: 7.7, r: 0.6 },
    { kind: 'kaluz', x: 3.6, z: 6.3, r: 0.85 },
    { kind: 'krtina', x: 10.4, z: 2.2, r: 0.6 },
  ],
  board: BOARD,
  view: { minX: -0.6, maxX: 12.0, minZ: 0.5, maxZ: 8.4 },
  mouth: { x: 10.4, z: 7.5 },
  startWater: 120,
  startDefenders: ['mrkev'],
  unlocks: [{ wave: 1, type: 'porek' }],
  waveSpeed: [1, 1, 1.1, 1.4],
  waves: [
    seq([H, H, H], 4),
    seq([H, H, H, H, H, H], 3),
    // 3. vlna: hranolky poprvé a hned v hloučcích s hamburgery.
    seq([H, F, H, H, F, H, F, H, H, F, H, F, F, H], 1.3),
    // 4. vlna (finále): tři husté nápory, v každém velké hamburgery s doprovodem hranolek.
    [
      ...seq([H, F, H, F, H, F, H, F, B, F, B], 0.6),
      ...seq([F, F, H, B, F, H, F, B, F, H, B, F], 0.55).map((s, i) => (i === 0 ? { ...s, delay: 3 } : s)),
      ...seq([B, F, B, F, H, F, B, F, H, F, B, B], 0.5).map((s, i) => (i === 0 ? { ...s, delay: 3 } : s)),
    ],
  ],
};
