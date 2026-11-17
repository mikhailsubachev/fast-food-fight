import type { Vec2 } from './types';

/** Hladká křivka přes řídicí body (Catmull-Rom), stejná jako v návrhu `design/generator/curve.py`. */
export function catmullRom(ctrl: readonly Vec2[], samplesPerSegment = 14): Vec2[] {
  const p = [ctrl[0], ...ctrl, ctrl[ctrl.length - 1]];
  const out: Vec2[] = [];
  for (let i = 1; i < p.length - 2; i++) {
    const [p0, p1, p2, p3] = [p[i - 1], p[i], p[i + 1], p[i + 2]];
    for (let k = 0; k < samplesPerSegment; k++) {
      const t = k / samplesPerSegment;
      const t2 = t * t;
      const t3 = t2 * t;
      const f = (a: number, b: number, c: number, d: number) =>
        0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3);
      out.push({ x: f(p0.x, p1.x, p2.x, p3.x), z: f(p0.z, p1.z, p2.z, p3.z) });
    }
  }
  out.push(ctrl[ctrl.length - 1]);
  return out;
}

/** Odřízne začátek křivky tak, aby začínala přesně na okraji záhonu (x = minX). */
export function clipStartAtX(points: readonly Vec2[], minX: number): Vec2[] {
  const i = points.findIndex((p) => p.x >= minX);
  if (i <= 0) return [...points];
  const a = points[i - 1];
  const b = points[i];
  const t = (minX - a.x) / (b.x - a.x);
  return [{ x: minX, z: a.z + (b.z - a.z) * t }, ...points.slice(i)];
}

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

  /** Nejbližší místo na středové čáře cesty: vzdálenost od startu `d` a od bodu `dist`. */
  project(p: Vec2): { d: number; dist: number } {
    let best = { d: 0, dist: Infinity };
    let start = 0;
    for (let i = 0; i < this.points.length - 1; i++) {
      const a = this.points[i];
      const b = this.points[i + 1];
      const dx = b.x - a.x;
      const dz = b.z - a.z;
      const len2 = dx * dx + dz * dz;
      const t = len2 > 0 ? Math.max(0, Math.min(1, ((p.x - a.x) * dx + (p.z - a.z) * dz) / len2)) : 0;
      const dist = Math.hypot(p.x - (a.x + dx * t), p.z - (a.z + dz * t));
      if (dist < best.dist) best = { d: start + this.lengths[i] * t, dist };
      start += this.lengths[i];
    }
    return best;
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
