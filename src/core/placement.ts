// Kam se dá zasadit zelenina (Plán první úrovně v6): téměř kamkoliv na záhon,
// kromě cesty, překážek, pusy a míst těsně u jiné zeleniny.
import type { LevelData } from '../data/level1';
import type { Path } from './path';
import type { Vec2 } from './types';

/** Poloměr sazenice (hlína pod zeleninou). */
export const PLANT_RADIUS = 0.4;
/** Cesta je široká asi 1 políčko; zelenina nesmí zasahovat do cesty. */
export const MIN_PATH_DISTANCE = 0.9;
/** Mezi rostlinami aspoň ~1 políčko (návrh z plánu). */
export const MIN_PLANT_SPACING = 1.0;
/** Kolem pusy se nesází. */
export const MOUTH_CLEARANCE = 1.4;

export type PlaceCheck = 'ok' | 'outside' | 'path' | 'obstacle' | 'mouth' | 'crowded';

export function checkPlace(level: LevelData, path: Path, plants: readonly Vec2[], p: Vec2): PlaceCheck {
  const b = level.board;
  if (
    p.x < b.minX + PLANT_RADIUS ||
    p.x > b.maxX - PLANT_RADIUS ||
    p.z < b.minZ + PLANT_RADIUS ||
    p.z > b.maxZ - PLANT_RADIUS
  )
    return 'outside';
  if (path.distanceTo(p) < MIN_PATH_DISTANCE) return 'path';
  if (level.obstacles.some((o) => Math.hypot(o.x - p.x, o.z - p.z) < o.r + PLANT_RADIUS)) return 'obstacle';
  if (Math.hypot(level.mouth.x - p.x, level.mouth.z - p.z) < MOUTH_CLEARANCE) return 'mouth';
  if (plants.some((d) => Math.hypot(d.x - p.x, d.z - p.z) < MIN_PLANT_SPACING)) return 'crowded';
  return 'ok';
}
