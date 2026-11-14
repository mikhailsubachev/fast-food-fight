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

const BOARD: Rect = { minX: 0, maxX: 6, minZ: 0, maxZ: 20 };

/**
 * Řídicí body cesty pro telefon na výšku: z levého horního rohu záhonu mírným obloukem
 * přes celou výšku obrazovky k puse v pravém dolním rohu. Cesta se skoro nevlní,
 * takže se úseky cesty na obrazovce nepřekrývají.
 */
const PATH_CONTROL: Vec2[] = [
  { x: -2, z: 0.5 },
  { x: 0, z: 0.5 },
  { x: 1.5, z: 1.1 },
  { x: 2.3, z: 3.8 },
  { x: 2.5, z: 8.2 },
  { x: 3.2, z: 12.7 },
  { x: 4.0, z: 16.7 },
  { x: 4.5, z: 18.9 },
];

export const LEVEL1: LevelData = {
  id: 1,
  name: 'Snídaňová cesta',
  path: clipStartAtX(catmullRom(PATH_CONTROL), BOARD.minX),
  // Sází se téměř kamkoliv na záhon; nejde na cestu, na tyto překážky a těsně k jiné zelenině.
  obstacles: [
    { kind: 'parez', x: 4.8, z: 2.0, r: 0.6 },
    { kind: 'kamen', x: 0.8, z: 7.1, r: 0.6 },
    { kind: 'kaluz', x: 5.0, z: 10.7, r: 0.85 },
    { kind: 'krtina', x: 1.2, z: 15.1, r: 0.5 },
  ],
  board: BOARD,
  view: { minX: 0, maxX: 6, minZ: 0.1, maxZ: 19.8 },
  mouth: { x: 4.6, z: 19.4 },
  startWater: 120,
  startDefenders: ['mrkev'],
  unlocks: [{ wave: 1, type: 'porek' }],
  waveSpeed: [1, 1, 1.3, 1.6],
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
      ...seq([B, B, F, B, F, B, F, B, B, F, B, B], 0.55).map((s, i) => (i === 0 ? { ...s, delay: 2.5 } : s)),
    ],
  ],
};
