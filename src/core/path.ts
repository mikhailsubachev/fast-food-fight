import type { Vec2 } from './types';

export interface PathPoint extends Vec2 {
  dirX: number;
  dirZ: number;
}

/** Lomená čára cesty; pozice na ní se měří vzdáleností od startu. */
export class Path {
  readonly length: number;
  private readonly lengths: number[] = [];

  constructor(readonly points: readonly Vec2[]) {
    if (points.length < 2) throw new Error('Cesta potřebuje aspoň 2 body.');
    let total = 0;
    for (let i = 0; i < points.length - 1; i++) {
      const l = Math.hypot(points[i + 1].x - points[i].x, points[i + 1].z - points[i].z);
      this.lengths.push(l);
      total += l;
    }
    this.length = total;
  }

  at(distance: number): PathPoint {
    let rest = Math.max(0, Math.min(distance, this.length));
    const last = this.lengths.length - 1;
    for (let i = 0; i <= last; i++) {
      const a = this.points[i];
      const b = this.points[i + 1];
      const l = this.lengths[i];
      if (rest <= l || i === last) {
        const t = l > 0 ? rest / l : 0;
        return {
          x: a.x + (b.x - a.x) * t,
          z: a.z + (b.z - a.z) * t,
          dirX: (b.x - a.x) / l,
          dirZ: (b.z - a.z) / l,
        };
      }
      rest -= l;
    }
    throw new Error('unreachable');
  }

  /** Nejkratší vzdálenost bodu od středové čáry cesty. */
  distanceTo(p: Vec2): number {
    let best = Infinity;
    for (let i = 0; i < this.points.length - 1; i++) {
      const a = this.points[i];
      const b = this.points[i + 1];
      const dx = b.x - a.x;
      const dz = b.z - a.z;
      const len2 = dx * dx + dz * dz;
      const t = len2 > 0 ? Math.max(0, Math.min(1, ((p.x - a.x) * dx + (p.z - a.z) * dz) / len2)) : 0;
      best = Math.min(best, Math.hypot(p.x - (a.x + dx * t), p.z - (a.z + dz * t)));
    }
    return best;
  }
}
