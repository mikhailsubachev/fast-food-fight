import type { Vec2 } from '../core/types';
import type { AttackerType, DefenderType } from './units';

export interface Spawn {
  type: AttackerType;
  /** Sekundy od předchozího fast foodu ve vlně. */
  delay: number;
}

export interface LevelData {
  id: number;
  name: string;
  /** Cesta od okraje mapy k puse. */
  path: Vec2[];
  slots: Vec2[];
  /** Obdélník, který musí být vždy celý vidět. */
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

export const LEVEL1: LevelData = {
  id: 1,
  name: 'Snídaňová cesta',
  // Cesta tvaru „S“: tři vodorovné úseky spojené dvěma krátkými.
  path: [
    { x: -1, z: 2.5 },
    { x: 8, z: 2.5 },
    { x: 8, z: 5 },
    { x: 2.5, z: 5 },
    { x: 2.5, z: 7.5 },
    { x: 9.5, z: 7.5 },
  ],
  slots: [
    // Blízko cesty (dobrá pro mrkev): 1,25 políčka od cesty, často mezi dvěma úseky.
    { x: 1, z: 1.25 },
    { x: 6, z: 1.25 },
    { x: 3.5, z: 3.75 },
    { x: 5.5, z: 3.75 },
    { x: 9.25, z: 3.75 },
    { x: 1.25, z: 6.25 },
    { x: 5, z: 6.25 },
    { x: 7, z: 6.25 },
    // Dál od cesty (dobrá pro pórek): mimo hod hranolek, pórek odtud dostřelí.
    // Leží po stranách, protože obrazovka na šířku má víc místa do šířky než do hloubky.
    { x: 10.5, z: 0.5 },
    { x: 10.8, z: 4 },
    { x: -0.3, z: 5.5 },
    { x: 12.2, z: 6 },
  ],
  board: { minX: -1, maxX: 12.7, minZ: -0.1, maxZ: 8.6 },
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
