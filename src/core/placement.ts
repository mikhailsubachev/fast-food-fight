// Kam se dá zasadit zelenina: do šestihranných políček podle návrhu úrovně
// (plátno „Místo na zeleninu podle úrovní“): jedna zelenina na políčko. Volná jsou skoro
// všechna políčka záhonu, kromě těch na cestě, u překážek a u pusy.
import type { LevelData } from '../data/level1';
import type { Path } from './path';
import type { Vec2 } from './types';

/**
 * Mřížka šestihranů s plochým vrškem: sloupce po `dx`, v sloupci políčka po `dz`,
 * liché sloupce posunuté o půl políčka dolů. `x0`, `z0` je střed levého horního políčka.
 */
export interface HexGrid {
  x0: number;
  z0: number;
  dx: number;
  dz: number;
}

/** Polovina šířky šestihranu (od středu ke špičce vlevo a vpravo), podle návrhu. */
export const HEX_HALF_WIDTH = 0.565;
/** Polovina výšky šestihranu (od středu k hornímu okraji), podle návrhu. */
export const HEX_HALF_HEIGHT = 0.545;
/** Ťuknutí do této vzdálenosti od středu políčka ho vybere. */
export const SLOT_PICK_RADIUS = 0.62;
/** Políčko nesmí zasahovat do cesty (cesta je široká asi 1 políčko). */
export const SLOT_PATH_CLEARANCE = 0.95;
/** Políčko nesmí zasahovat do překážky (k poloměru překážky se přičte tato rezerva). */
export const SLOT_OBSTACLE_CLEARANCE = 0.15;
/** Kolem pusy se nesází. */
export const MOUTH_CLEARANCE = 1.4;

export type PlaceCheck = 'ok' | 'outside' | 'path' | 'obstacle' | 'mouth' | 'crowded' | 'noSlot';

/** Všechna políčka záhonu, kam se dá sázet. */
export function hexSlots(level: LevelData, path: Path): Vec2[] {
  const { hexGrid: g, board: b } = level;
  const slots: Vec2[] = [];
  for (let i = 0; ; i++) {
    const x = g.x0 + i * g.dx;
    if (x + HEX_HALF_WIDTH > b.maxX) break;
    if (x - HEX_HALF_WIDTH < b.minX) continue;
    for (let j = -1; ; j++) {
      const z = g.z0 + j * g.dz + (i % 2 === 1 ? g.dz / 2 : 0);
      if (z + HEX_HALF_HEIGHT > b.maxZ) break;
      if (z - HEX_HALF_HEIGHT < b.minZ) continue;
      const p = { x, z };
      if (path.distanceTo(p) < SLOT_PATH_CLEARANCE) continue;
      if (level.obstacles.some((o) => Math.hypot(o.x - x, o.z - z) < o.r + SLOT_OBSTACLE_CLEARANCE)) continue;
      if (Math.hypot(level.mouth.x - x, level.mouth.z - z) < MOUTH_CLEARANCE) continue;
      slots.push(p);
    }
  }
  return slots;
}

/** Políčko pod prstem, nebo null. */
export function slotAt(slots: readonly Vec2[], p: Vec2): Vec2 | null {
  let best: Vec2 | null = null;
  let bestDist = SLOT_PICK_RADIUS;
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
  const slot = slotAt(slots, p);
  if (!slot) {
    // Mimo políčka: řekni proč, aby křížek dával smysl.
    if (path.distanceTo(p) < 0.7) return 'path';
    if (level.obstacles.some((o) => Math.hypot(o.x - p.x, o.z - p.z) < o.r)) return 'obstacle';
    if (Math.hypot(level.mouth.x - p.x, level.mouth.z - p.z) < MOUTH_CLEARANCE) return 'mouth';
    return 'noSlot';
  }
  if (plants.some((d) => Math.hypot(d.x - slot.x, d.z - slot.z) < 0.1)) return 'crowded';
  return 'ok';
}
