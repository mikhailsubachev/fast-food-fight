import { catmullRom, clipStartAtX } from '../core/path';
import type { HexGrid, SlotRules } from '../core/placement';
import type { Vec2 } from '../core/types';
import type { AttackerType, DefenderType } from './units';

export interface Spawn {
  type: AttackerType;
  /** Sekundy od předchozího fast foodu ve vlně. */
  delay: number;
}

/**
 * Překážky: v 1. úrovni pařez, kámen, kaluž a krtina, ve 2. úrovni školní věci ležící na louce
 * (svačinový box, láhev, penál, sešit, pastelky, guma), ve 3. zbytky oběda (tác, kelímek, ubrousky,
 * sáčky s omáčkou, účtenka, krabička od hranolek, papír od burgeru). Kaluž, školní věci a zbytky
 * oběda jsou ploché a jsou nakreslené přímo v obrázku země.
 */
export type ObstacleKind =
  | 'parez'
  | 'kamen'
  | 'kaluz'
  | 'krtina'
  | 'box'
  | 'lahev'
  | 'penal'
  | 'sesit'
  | 'pastelky'
  | 'guma'
  | 'tac'
  | 'kelimek'
  | 'ubrousky'
  | 'omacky'
  | 'uctenka'
  | 'krabicka'
  | 'papir';

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
  /** Obrázek země z návrhu (public/assets/prostredi, z tools/export_louka.py). */
  ground: string;
  /** Středová čára cesty od okraje záhonu k puse. */
  path: Vec2[];
  obstacles: Obstacle[];
  /** Záhon: obdélník, na který se dá sázet. */
  board: Rect;
  /** Mřížka šestihranů přes celou mapu. */
  hexGrid: HexGrid;
  /** Která políčka mřížky jsou k sázení. */
  slotRules: SlotRules;
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
  /** Násobek vody za odražený fast food (v těžších úrovních se zahrádka plní pomaleji). */
  rewardScale?: number;
}

/** Fast food jeden za druhým po `gap` sekundách; `first` je pauza před prvním. */
export function seq(types: AttackerType[], gap: number, first = 0): Spawn[] {
  return types.map((type, i) => ({ type, delay: i === 0 ? first : gap }));
}

const H: AttackerType = 'hamburger';
const F: AttackerType = 'hranolky';
const B: AttackerType = 'velkyHamburger';

/**
 * Záhon podle návrhu úrovně: na obrazovce 16 × 9 políček (1920 × 1080 px, 120 px na políčko),
 * nahoře pás pro horní lištu.
 */
export const BOARD: Rect = { minX: 0, maxX: 16, minZ: 0.85, maxZ: 10 };

/**
 * Řídicí body cesty z návrhu úrovně (plátno „Úroveň 1 – Snídaňová cesta“): vstupuje zleva,
 * klikatí se dolů, nahoru kolem kaluže, znovu dolů a nahoru a končí vpravo dole u pusy.
 */
export const PATH_CONTROL: Vec2[] = [
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

/**
 * Mřížka šestihranů z návrhu úrovně, varianta D (design/generator/gen_level.py): poloměr
 * šestihranu 89 px, sloupce po 133,5 px, políčka ve sloupci po 154,15 px; 120 px = 1 políčko v ose x,
 * 108 px v ose z. Stejná je i ve 2. úrovni.
 */
export const HEX_GRID: HexGrid = {
  x0: 40 / 120,
  z0: 150 / 108,
  dx: 133.5 / 120,
  dz: (89 * Math.sqrt(3)) / 108,
  halfWidth: 89 / 120,
  halfHeight: (89 * Math.sqrt(3)) / 2 / 108,
};

export const SLOT_RULES: SlotRules = {
  // Sází se mezi 40 a 1880 px na šířku a 130 až 1030 px na výšku obrazovky návrhu.
  area: { minX: 40 / 120, maxX: 1880 / 120, minZ: 130 / 108 - 1e-6, maxZ: 1030 / 108 + 1e-6 },
  pathClearance: 0.78,
  // Kolem pusy vpravo dole se nesází (od 1600 px vpravo a 560 px dolů).
  blocked: [{ minX: 1600 / 120, maxX: 99, minZ: 560 / 108, maxZ: 99 }],
};

export const VIEW: Rect = { minX: 0, maxX: 16, minZ: 1, maxZ: 10 };
export const MOUTH: Vec2 = { x: 14.3, z: 8.0 };

export const LEVEL1: LevelData = {
  id: 1,
  name: 'Snídaňová cesta',
  ground: 'louka.svg',
  path: clipStartAtX(catmullRom(PATH_CONTROL), BOARD.minX),
  // Sází se do šestihranů; na cestě, na překážkách a u pusy políčka nejsou.
  // Polohy překážek z generátoru návrhu D; políčka pod nimi jsou šedá a nesází se do nich.
  obstacles: [
    { kind: 'parez', x: 0.6167, z: 8.6147, r: 0.6 },
    { kind: 'kamen', x: 15.1917, z: 2.6648, r: 0.7 },
    { kind: 'kaluz', x: 8.5667, z: 3.5148, r: 0.85 },
    { kind: 'krtina', x: 12.5417, z: 2.6648, r: 0.6 },
  ],
  board: BOARD,
  hexGrid: HEX_GRID,
  slotRules: SLOT_RULES,
  view: VIEW,
  mouth: MOUTH,
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
