import type { LevelData, Spawn } from '../data/level1';
import {
  ATTACKERS,
  DEFENDERS,
  FLEE_SPEED_FACTOR,
  MOUTH_LIVES,
  WAVE_PAUSE,
  type DefenderType,
} from '../data/units';
import { createAttacker, type Attacker } from '../entities/utocnici/attacker';
import { createDefender, defenderLevel, isGrown, type Defender } from '../entities/obranci/defender';
import { Path } from './path';
import { checkPlace, type PlaceCheck } from './placement';
import type { Vec2 } from './types';

export type Phase = 'countdown' | 'wave' | 'won' | 'lost';

export interface Projectile {
  id: number;
  kind: 'porek' | 'hranolka';
  x0: number;
  z0: number;
  /** Cíl; pórek ho sleduje, dokud cíl nezačne utíkat. */
  tx: number;
  tz: number;
  t: number;
  duration: number;
  targetId: number;
}

export type GameEvent =
  | { type: 'planted'; defenderId: number }
  | { type: 'upgraded'; defenderId: number }
  | { type: 'attack'; defenderId: number }
  | { type: 'hit'; attackerId: number; x: number; z: number }
  | { type: 'flee'; attackerId: number; x: number; z: number; water: number }
  | { type: 'escaped'; x: number; z: number }
  | { type: 'bite'; bites: number }
  | { type: 'miss'; x: number; z: number }
  | { type: 'throw'; attackerId: number }
  | { type: 'frozen'; defenderId: number }
  | { type: 'waveStart'; wave: number }
  | { type: 'unlocked'; defender: DefenderType }
  | { type: 'won'; stars: number }
  | { type: 'lost' };

export type PlantCheck = PlaceCheck | 'locked' | 'water';

/** Herní logika bez grafiky: dá se spustit i v automatickém testu. */
export class Game {
  readonly path: Path;
  water = 0;
  bites = 0;
  /** Index vlny, která právě běží nebo přijde po odpočtu. */
  waveIndex = 0;
  phase: Phase = 'countdown';
  countdown = 0;
  stars = 0;
  defenders: Defender[] = [];
  attackers: Attacker[] = [];
  projectiles: Projectile[] = [];
  readonly unlocked = new Set<DefenderType>();

  private events: GameEvent[] = [];
  private queue: Spawn[] = [];
  private spawnTimer = 0;
  private nextId = 1;

  constructor(readonly level: LevelData) {
    this.path = new Path(level.path);
    this.reset();
  }

  get waveCount(): number {
    return this.level.waves.length;
  }

  get finished(): boolean {
    return this.phase === 'won' || this.phase === 'lost';
  }

  reset(): void {
    this.water = this.level.startWater;
    this.bites = 0;
    this.waveIndex = 0;
    this.stars = 0;
    this.defenders = [];
    this.attackers = [];
    this.projectiles = [];
    this.queue = [];
    this.events = [];
    this.unlocked.clear();
    for (const t of this.level.startDefenders) this.unlocked.add(t);
    this.beginCountdown();
  }

  drainEvents(): GameEvent[] {
    const e = this.events;
    this.events = [];
    return e;
  }

  /** Zelenina, na kterou hráč ťukl (v okruhu `radius` od bodu). */
  defenderNear(p: Vec2, radius = 0.7): Defender | undefined {
    let best: Defender | undefined;
    let bestDist = radius;
    for (const d of this.defenders) {
      const dist = Math.hypot(d.x - p.x, d.z - p.z);
      if (dist < bestDist) {
        best = d;
        bestDist = dist;
      }
    }
    return best;
  }

  /** Dá se na tohle místo vůbec sázet (bez ohledu na vodu)? */
  checkPlace(p: Vec2): PlaceCheck {
    return checkPlace(this.level, this.path, this.defenders, p);
  }

  checkPlant(p: Vec2, type: DefenderType): PlantCheck {
    const place = this.checkPlace(p);
    if (place !== 'ok') return place;
    if (!this.unlocked.has(type)) return 'locked';
    if (this.water < DEFENDERS[type].cost) return 'water';
    return 'ok';
  }

  plant(p: Vec2, type: DefenderType): boolean {
    if (this.finished || this.checkPlant(p, type) !== 'ok') return false;
    this.water -= DEFENDERS[type].cost;
    const d = createDefender(this.nextId++, type, p);
    this.defenders.push(d);
    this.events.push({ type: 'planted', defenderId: d.id });
    return true;
  }

  /** Cena vylepšení, nebo null, když už víc nejde (v 1. úrovni hry jen na úroveň 2). */
  upgradeCost(d: Defender): number | null {
    return d.level >= 2 ? null : DEFENDERS[d.type].upgradeCost;
  }

  upgrade(defenderId: number): boolean {
    const d = this.defenders.find((x) => x.id === defenderId);
    if (!d || this.finished) return false;
    const cost = this.upgradeCost(d);
    if (cost === null || this.water < cost) return false;
    this.water -= cost;
    d.level = 2;
    this.events.push({ type: 'upgraded', defenderId: d.id });
    return true;
  }

  /** Tlačítko „Hned!“: přeskočí odpočet do další vlny. */
  startNow(): void {
    if (this.phase === 'countdown') this.startWave();
  }

  update(dt: number): void {
    if (this.finished) return;
    if (this.phase === 'countdown') {
      this.countdown -= dt;
      if (this.countdown <= 0) this.startWave();
    } else {
      this.spawnDue(dt);
    }

    for (const d of this.defenders) this.updateDefender(d, dt);
    const gone = new Set<number>();
    for (const a of this.attackers) {
      if (this.updateAttacker(a, dt)) gone.add(a.id);
      if (this.finished) return;
    }
    if (gone.size) this.attackers = this.attackers.filter((a) => !gone.has(a.id));
    this.updateProjectiles(dt);

    if (this.phase === 'wave' && this.queue.length === 0 && this.attackers.length === 0) this.endWave();
  }

  // --- vlny ---

  private beginCountdown(): void {
    this.phase = 'countdown';
    this.countdown = WAVE_PAUSE;
    for (const u of this.level.unlocks) {
      if (u.wave === this.waveIndex && !this.unlocked.has(u.type)) {
        this.unlocked.add(u.type);
        this.events.push({ type: 'unlocked', defender: u.type });
      }
    }
  }

  private startWave(): void {
    this.phase = 'wave';
    this.countdown = 0;
    this.queue = [...this.level.waves[this.waveIndex]];
    this.spawnTimer = this.queue[0]?.delay ?? 0;
    this.events.push({ type: 'waveStart', wave: this.waveIndex });
  }

  private spawnDue(dt: number): void {
    this.spawnTimer -= dt;
    while (this.queue.length && this.spawnTimer <= 0) {
      const s = this.queue.shift()!;
      this.attackers.push(createAttacker(this.nextId++, s.type));
      if (this.queue.length) this.spawnTimer += this.queue[0].delay;
    }
  }

  private endWave(): void {
    if (this.waveIndex >= this.waveCount - 1) {
      this.phase = 'won';
      this.stars = this.bites === 0 ? 3 : this.bites === 1 ? 2 : 1;
      this.events.push({ type: 'won', stars: this.stars });
      return;
    }
    this.waveIndex++;
    this.beginCountdown();
  }

  // --- zelenina ---

  private updateDefender(d: Defender, dt: number): void {
    if (d.growLeft > 0) {
      d.growLeft = Math.max(0, d.growLeft - dt);
      return;
    }
    if (d.frozenLeft > 0) {
      d.frozenLeft = Math.max(0, d.frozenLeft - dt);
      return;
    }
    d.cooldown -= dt;
    if (d.cooldown > 0) return;

    const stats = defenderLevel(d);
    const target = this.pickTarget(d.x, d.z, stats.range);
    if (!target) {
      d.cooldown = 0;
      return;
    }
    d.cooldown = stats.attackInterval;
    this.events.push({ type: 'attack', defenderId: d.id });

    const speed = DEFENDERS[d.type].projectileSpeed;
    if (speed) {
      const p = this.path.at(target.d);
      this.projectiles.push({
        id: this.nextId++,
        kind: 'porek',
        x0: d.x,
        z0: d.z,
        tx: p.x,
        tz: p.z,
        t: 0,
        duration: Math.max(0.2, Math.hypot(p.x - d.x, p.z - d.z) / speed),
        targetId: target.id,
      });
    } else {
      this.hitAttacker(target);
    }
  }

  /** Nejdál došlý fast food v dosahu, který ještě neutíká. */
  private pickTarget(x: number, z: number, range: number): Attacker | undefined {
    let best: Attacker | undefined;
    for (const a of this.attackers) {
      if (a.fleeing) continue;
      const p = this.path.at(a.d);
      if (Math.hypot(p.x - x, p.z - z) > range) continue;
      if (!best || a.d > best.d) best = a;
    }
    return best;
  }

  private hitAttacker(a: Attacker): void {
    if (a.fleeing) return;
    const p = this.path.at(a.d);
    a.hitsLeft--;
    this.events.push({ type: 'hit', attackerId: a.id, x: p.x, z: p.z });
    if (a.hitsLeft > 0) return;
    a.fleeing = true;
    const reward = ATTACKERS[a.type].reward;
    this.water += reward;
    this.events.push({ type: 'flee', attackerId: a.id, x: p.x, z: p.z, water: reward });
  }

  // --- fast food ---

  /** Vrací true, když fast food zmizel z mapy. */
  private updateAttacker(a: Attacker, dt: number): boolean {
    const stats = ATTACKERS[a.type];
    if (a.fleeing) {
      a.d -= stats.speed * FLEE_SPEED_FACTOR * dt;
      if (a.d > 0) return false;
      const p = this.path.at(0);
      this.events.push({ type: 'escaped', x: p.x, z: p.z });
      return true;
    }

    a.d += stats.speed * (this.level.waveSpeed?.[this.waveIndex] ?? 1) * dt;
    if (a.d >= this.path.length) {
      this.bites++;
      this.events.push({ type: 'bite', bites: this.bites });
      if (this.bites > MOUTH_LIVES) {
        this.phase = 'lost';
        this.events.push({ type: 'lost' });
      }
      return true;
    }

    const throws = stats.throws;
    if (throws) {
      a.throwCooldown -= dt;
      if (a.throwCooldown <= 0) {
        const p = this.path.at(a.d);
        const target = this.nearestGrownDefender(p.x, p.z, throws.range);
        if (target) {
          a.throwCooldown = throws.interval;
          this.projectiles.push({
            id: this.nextId++,
            kind: 'hranolka',
            x0: p.x,
            z0: p.z,
            tx: target.x,
            tz: target.z,
            t: 0,
            duration: Math.max(0.2, Math.hypot(target.x - p.x, target.z - p.z) / throws.projectileSpeed),
            targetId: target.id,
          });
          this.events.push({ type: 'throw', attackerId: a.id });
        } else {
          a.throwCooldown = 0.25;
        }
      }
    }
    return false;
  }

  private nearestGrownDefender(x: number, z: number, range: number): Defender | undefined {
    let best: Defender | undefined;
    let bestDist = Infinity;
    for (const d of this.defenders) {
      if (!isGrown(d)) continue;
      const dist = Math.hypot(d.x - x, d.z - z);
      if (dist <= range && dist < bestDist) {
        best = d;
        bestDist = dist;
      }
    }
    return best;
  }

  // --- střely ---

  private updateProjectiles(dt: number): void {
    if (!this.projectiles.length) return;
    const left: Projectile[] = [];
    for (const p of this.projectiles) {
      p.t += dt;
      if (p.kind === 'porek') {
        const target = this.attackers.find((a) => a.id === p.targetId);
        if (target && !target.fleeing) {
          const pos = this.path.at(target.d);
          p.tx = pos.x;
          p.tz = pos.z;
        }
        if (p.t < p.duration) {
          left.push(p);
        } else if (target && !target.fleeing) {
          this.hitAttacker(target);
        } else {
          // Cíl mezitím utekl: pórek dopadne na zem, „puf“ a zmizí.
          this.events.push({ type: 'miss', x: p.tx, z: p.tz });
        }
      } else {
        if (p.t < p.duration) {
          left.push(p);
          continue;
        }
        const target = this.defenders.find((d) => d.id === p.targetId);
        if (target) {
          target.frozenLeft = ATTACKERS.hranolky.throws!.freeze;
          this.events.push({ type: 'frozen', defenderId: target.id });
        }
      }
    }
    this.projectiles = left;
  }
}
