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

/**
 * Záhon podle návrhu úrovně: na obrazovce 16 × 9 políček (1920 × 1080 px, 120 px na políčko),
 * nahoře pás pro horní lištu.
 */
const BOARD: Rect = { minX: 0, maxX: 16, minZ: 1, maxZ: 10 };

/**
 * Řídicí body cesty z návrhu úrovně (plátno „Úroveň 1 – Snídaňová cesta“): vstupuje zleva,
 * klikatí se dolů, nahoru kolem kaluže, znovu dolů a nahoru a končí vpravo dole u pusy.
 */
const PATH_CONTROL: Vec2[] = [
  { x: -3.0, z: 3.1 },
  { x: -1.25, z: 3.05 },
  { x: 1.0, z: 2.95 },
  { x: 2.5, z: 3.35 },
  { x: 2.9, z: 4.8 },
  { x: 2.75, z: 6.5 },
  { x: 3.15, z: 7.85 },
  { x: 4.5, z: 8.4 },
  { x: 5.85, z: 7.85 },
  { x: 6.25, z: 6.3 },
  { x: 6.1, z: 4.45 },
  { x: 6.6, z: 3.05 },
  { x: 7.9, z: 2.5 },
  { x: 9.3, z: 2.7 },
  { x: 10.3, z: 3.7 },
  { x: 10.5, z: 5.4 },
  { x: 10.4, z: 6.75 },
  { x: 11.0, z: 7.8 },
  { x: 12.3, z: 8.05 },
  { x: 13.35, z: 7.95 },
];

export const LEVEL1: LevelData = {
  id: 1,
  name: 'Snídaňová cesta',
  path: clipStartAtX(catmullRom(PATH_CONTROL), BOARD.minX),
  // Sází se téměř kamkoliv na záhon; nejde na cestu, na tyto překážky a těsně k jiné zelenině.
  obstacles: [
    { kind: 'parez', x: 0.9, z: 8.3, r: 0.55 },
    { kind: 'kamen', x: 14.7, z: 2.6, r: 0.6 },
    { kind: 'kaluz', x: 8.3, z: 4.2, r: 0.85 },
    { kind: 'krtina', x: 12.7, z: 2.4, r: 0.5 },
  ],
  board: BOARD,
  view: { minX: 0, maxX: 16, minZ: 1, maxZ: 10 },
  mouth: { x: 14.3, z: 8.0 },
  startWater: 120,
  startDefenders: ['mrkev'],
  unlocks: [{ wave: 1, type: 'porek' }],
  waveSpeed: [1, 1, 1.3, 1.5],
  waves: [
    seq([H, H, H], 4),
    seq([H, H, H, H, H, H], 3),
    // 3. vlna: hranolky poprvé a hned v hloučcích s hamburgery.
    seq([H, F, H, H, F, H, F, H, H, F, H, F, F, H], 1.3),
    // 4. vlna (finále): čtyři husté nápory, v každém velké hamburgery s doprovodem hranolek.
    [
      ...seq([H, F, H, F, H, F, H, F, B, F, B], 0.6),
      ...seq([F, F, H, B, F, H, F, B, F, H, B, F], 0.6).map((s, i) => (i === 0 ? { ...s, delay: 3.5 } : s)),
      ...seq([B, F, B, F, H, F, B, F, H, F, B, B], 0.55).map((s, i) => (i === 0 ? { ...s, delay: 3.5 } : s)),
      ...seq([B, B, F, B, F, B, F, B, B], 0.6).map((s, i) => (i === 0 ? { ...s, delay: 3 } : s)),
    ],
  ],
};
