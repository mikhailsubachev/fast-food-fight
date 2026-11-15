// Kam se dá zasadit zelenina: do šestihranných políček podle návrhu úrovně, varianta D
// (plátno „Úroveň 1 – varianta D, celá mřížka“). Mřížka pokrývá celou mapu; sázet se dá
// do políček na trávě, ne na cestu, na políčka překážek a k puse.
import type { LevelData, Obstacle, Rect } from '../data/level1';
import type { Path } from './path';
import type { Vec2 } from './types';

/**
 * Mřížka šestihranů s plochým vrškem: sloupce po `dx`, v sloupci políčka po `dz`,
 * liché sloupce posunuté o půl políčka dolů. `x0`, `z0` je střed políčka v nultém sloupci
 * a nulté řadě. `halfWidth` a `halfHeight` jsou rozměry celého políčka (ke špičce
 * a k hornímu okraji), jak je kreslí obrysy mřížky.
 */
export interface HexGrid {
  x0: number;
  z0: number;
  dx: number;
  dz: number;
  halfWidth: number;
  halfHeight: number;
}

/** Pravidla, která políčka mřížky jsou k sázení. */
export interface SlotRules {
  /** Střed políčka musí ležet v tomto obdélníku (okraje obrazovky a pás pod horní lištou ne). */
  area: Rect;
  /** Políčko, jehož střed je blíž k ose cesty, leží na cestě. */
  pathClearance: number;
  /** Obdélníky bez políček (místo u pusy). */
  blocked: Rect[];
}

/** Volné, osázené a vybrané políčko je menší než obrys v mřížce (podle návrhu 0,66). */
export const SLOT_SCALE = 0.66;

export type PlaceCheck = 'ok' | 'outside' | 'path' | 'obstacle' | 'mouth' | 'crowded' | 'noSlot';

const inside = (r: Rect, p: Vec2) => p.x > r.minX && p.x < r.maxX && p.z > r.minZ && p.z < r.maxZ;

/** Středy všech políček mřížky, která zasahují na obrazovku záhonu. */
export function hexCenters(g: HexGrid, around: Rect): Vec2[] {
  const out: Vec2[] = [];
  const cols = Math.ceil((around.maxX - g.x0) / g.dx) + 1;
  const rows = Math.ceil((around.maxZ - g.z0) / g.dz) + 1;
  for (let i = -1; i <= cols; i++) {
    for (let j = -1; j <= rows; j++) {
      out.push({ x: g.x0 + i * g.dx, z: g.z0 + j * g.dz + (Math.abs(i) % 2 === 1 ? g.dz / 2 : 0) });
    }
  }
  return out;
}

/**
 * Překážka zabere políčko, jehož střed je blíž než 0,95 poloměru šestihranu nebo 0,9 poloměru
 * překážky (měřeno na obrazovce návrhu, kde je osa z stlačená na 0,9).
 */
function blocksSlot(g: HexGrid, o: Obstacle, p: Vec2): boolean {
  const d = Math.hypot(o.x - p.x, (o.z - p.z) * 0.9);
  return d < Math.max(g.halfWidth * 0.95, o.r * 0.9);
}

/** Všechna políčka záhonu, kam se dá sázet. */
export function hexSlots(level: LevelData, path: Path): Vec2[] {
  const r = level.slotRules;
  return hexCenters(level.hexGrid, level.board).filter(
    (p) =>
      inside(r.area, p) &&
      !r.blocked.some((b) => inside(b, p)) &&
      !level.obstacles.some((o) => blocksSlot(level.hexGrid, o, p)) &&
      path.distanceTo(p) >= r.pathClearance,
  );
}

/** Políčko pod prstem (ťuknutí kamkoliv do obrysu šestihranu), nebo null. */
export function slotAt(level: LevelData, slots: readonly Vec2[], p: Vec2): Vec2 | null {
  // Vnitřní kružnice obrysu: šestihran s plochým vrškem má k bokům √3/2 poloměru.
  const pick = Math.min(level.hexGrid.halfWidth * 0.9, level.hexGrid.halfHeight);
  let best: Vec2 | null = null;
  let bestDist = pick;
  for (const s of slots) {
    const d = Math.hypot(s.x - p.x, s.z - p.z);
    if (d < bestDist) {
      best = s;
      bestDist = d;
    }
  }
  return best;
}

export function checkPlace(
  level: LevelData,
  path: Path,
  slots: readonly Vec2[],
  plants: readonly Vec2[],
  p: Vec2,
): PlaceCheck {
  const b = level.board;
  if (p.x < b.minX || p.x > b.maxX || p.z < b.minZ || p.z > b.maxZ) return 'outside';
  const slot = slotAt(level, slots, p);
  if (!slot) {
    // Mimo políčka: řekni proč, aby křížek dával smysl.
    if (path.distanceTo(p) < 0.7) return 'path';
    if (level.obstacles.some((o) => Math.hypot(o.x - p.x, o.z - p.z) < o.r)) return 'obstacle';
    if (level.slotRules.blocked.some((r) => inside(r, p))) return 'mouth';
    return 'noSlot';
  }
  if (plants.some((d) => Math.hypot(d.x - slot.x, d.z - slot.z) < 0.1)) return 'crowded';
  return 'ok';
}
