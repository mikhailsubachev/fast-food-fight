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

export interface LevelData {
  id: number;
  name: string;
  /** Středová čára cesty od okraje záhonu k puse. */
  path: Vec2[];
  obstacles: Obstacle[];
  /** Záhon: obdélník, na který se sází a který musí být vždy celý vidět. */
  board: { minX: number; maxX: number; minZ: number; maxZ: number };
  mouth: Vec2;
  startWater: number;
  startDefenders: DefenderType[];
  /** Zelenina se odemkne před vlnou s tímto indexem (0 = první vlna). */
  unlocks: { wave: number; type: DefenderType }[];
  waves: Spawn[][];
}

function seq(types: AttackerType[], gap: number): Spawn[] {
  return types.map((type, i) => ({ type, delay: i === 0 ? 0 : gap }));
}

const H: AttackerType = 'hamburger';
const F: AttackerType = 'hranolky';

const BOARD = { minX: -1, maxX: 12.7, minZ: -0.1, maxZ: 8.6 };

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
    { kind: 'kamen', x: 12.0, z: 5.0, r: 0.7 },
    { kind: 'kaluz', x: 3.6, z: 6.3, r: 0.85 },
    { kind: 'krtina', x: 10.4, z: 2.2, r: 0.6 },
  ],
  board: BOARD,
  mouth: { x: 10.4, z: 7.5 },
  startWater: 120,
  startDefenders: ['mrkev'],
  unlocks: [{ wave: 1, type: 'porek' }],
  waves: [
    seq([H, H, H], 4),
    seq([H, H, H, H, H, H], 3),
    seq([H, H, F, H, H, F], 3),
    [...seq([H, H, F, H, H, F, H, H, F, H, H, F], 2.5), { type: 'velkyHamburger', delay: 4 }],
  ],
};
