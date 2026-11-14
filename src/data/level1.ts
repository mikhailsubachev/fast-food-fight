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

/** Řídicí body zvlněné cesty „S“: tři průchody přes celou šířku záhonu. */
const PATH_CONTROL: Vec2[] = [
  { x: -4.5, z: 1.9 },
  { x: -1.8, z: 1.8 },
  { x: 0.6, z: 1.7 },
  { x: 3.0, z: 1.95 },
  { x: 5.6, z: 1.75 },
  { x: 8.2, z: 1.9 },
  { x: 10.2, z: 2.2 },
  { x: 11.1, z: 3.3 },
  { x: 10.3, z: 4.4 },
  { x: 8.2, z: 4.7 },
  { x: 6.0, z: 4.5 },
  { x: 4.0, z: 4.75 },
  { x: 2.0, z: 4.6 },
  { x: 0.8, z: 5.2 },
  { x: 0.5, z: 6.3 },
  { x: 1.4, z: 7.3 },
  { x: 3.4, z: 7.6 },
  { x: 5.5, z: 7.35 },
  { x: 7.6, z: 7.55 },
  { x: 9.9, z: 7.5 },
];

export const LEVEL1: LevelData = {
  id: 1,
  name: 'Snídaňová cesta',
  path: clipStartAtX(catmullRom(PATH_CONTROL), BOARD.minX),
  // Sází se téměř kamkoliv na záhon; nejde na cestu, na tyto překážky a těsně k jiné zelenině.
  // Cesta je delší a okraje užší než v návrhu úrovně (design/artboardy/5-uroven-1.html).
  obstacles: [
    { kind: 'parez', x: 7.0, z: 3.2, r: 0.6 },
    { kind: 'kamen', x: 4.2, z: 6.1, r: 0.6 },
    { kind: 'kaluz', x: 9.0, z: 6.0, r: 0.85 },
    { kind: 'krtina', x: 2.6, z: 0.75, r: 0.6 },
  ],
  board: BOARD,
  view: { minX: -0.6, maxX: 12.0, minZ: 0.5, maxZ: 8.4 },
  mouth: { x: 10.4, z: 7.5 },
  startWater: 120,
  startDefenders: ['mrkev'],
  unlocks: [{ wave: 1, type: 'porek' }],
  waveSpeed: [1, 1, 1.2, 1.6],
  waves: [
    seq([H, H, H], 4),
    seq([H, H, H, H, H, H], 3),
    // 3. vlna: hranolky poprvé a hned v hloučcích s hamburgery.
    seq([H, F, H, H, F, H, F, H, H, F, H, F, F, H], 1.3),
    // 4. vlna (finále): čtyři husté nápory, v každém velké hamburgery s doprovodem hranolek.
    [
      ...seq([H, F, H, F, H, F, H, F, B, F, B], 0.45),
      ...seq([F, F, H, B, F, H, F, B, F, H, B, F], 0.4).map((s, i) => (i === 0 ? { ...s, delay: 3 } : s)),
      ...seq([B, F, B, F, H, F, B, F, H, F, B, B], 0.35).map((s, i) => (i === 0 ? { ...s, delay: 3 } : s)),
      ...seq([B, B, F, B, F, B, F, B, B, F, B, B], 0.35).map((s, i) => (i === 0 ? { ...s, delay: 2.5 } : s)),
    ],
  ],
};
