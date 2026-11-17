import type { LevelData, Spawn } from '../data/level1';
import {
  ATTACKER_BODY_RADIUS,
  ATTACKERS,
  DEFENDERS,
  FLEE_SPEED_FACTOR,
  MOUTH_LIVES,
  POTATO,
  WAVE_PAUSE,
  type DefenderType,
  type SpinStats,
  type SquirtStats,
} from '../data/units';
import { createAttacker, type Attacker } from '../entities/utocnici/attacker';
import { createDefender, defenderLevel, isGrown, type Defender } from '../entities/obranci/defender';
import { Path } from './path';
import { checkPlace, hexSlots, slotAt, type PlaceCheck } from './placement';
import type { Vec2 } from './types';

export type Phase = 'countdown' | 'wave' | 'won' | 'lost';

export interface Projectile {
  id: number;
  kind: 'porek' | 'hranolka' | 'brokolice';
  x0: number;
  z0: number;
  /** Cíl; pórek a brokolicová raketa ho sledují, dokud cíl nezačne utíkat. */
  tx: number;
  tz: number;
  t: number;
  duration: number;
  targetId: number;
  /** Brokolice: poloměr deštníku, do kterého se raketa nad cílem rozprskne. */
  splash?: number;
}

/** Pan Brambora stojí přímo na cestě (`d` od startu) a fast food přes něj nemůže projít. */
export interface Potato {
  id: number;
  d: number;
  x: number;
  z: number;
  lives: number;
}

/** Proč se Pan Brambora na tohle místo postavit nemůže. */
export type PotatoCheck = 'ok' | 'notPath' | 'mouth' | 'crowded' | 'finished';

/** Kečupová louže na cestě mezi `d0` a `d1`: fast food po ní klouže rychleji. */
export interface Puddle {
  id: number;
  d0: number;
  d1: number;
  left: number;
  life: number;
}

/** Oblak smradu cibule: fast food uvnitř jde pomaleji, dokud oblak nevyvětrá. */
export interface Cloud {
  id: number;
  x: number;
  z: number;
  r: number;
  left: number;
  /** Jak dlouho oblak vydrží celkem (pro zobrazení). */
  life: number;
}

export type GameEvent =
  | { type: 'planted'; defenderId: number }
  | { type: 'upgraded'; defenderId: number }
  /** Zelenina útočí; `x`, `z` je místo, kde stojí cíl (aby se k němu otočila). */
  | { type: 'attack'; defenderId: number; x: number; z: number }
  /** Zásah fast foodu; `melee` je sek mrkve (mrkvomeč k cíli teprve doskočí). */
  | { type: 'hit'; attackerId: number; x: number; z: number; melee: boolean }
  | { type: 'flee'; attackerId: number; x: number; z: number; water: number }
  | { type: 'escaped'; x: number; z: number }
  | { type: 'bite'; bites: number }
  | { type: 'miss'; x: number; z: number }
  | { type: 'throw'; attackerId: number }
  | { type: 'frozen'; defenderId: number }
  /** Cibule vypustila oblak smradu. */
  | { type: 'cloud'; defenderId: number; x: number; z: number; r: number }
  /** Brokolicová raketa se nad cílem rozprskla do deštníku (poloměr `r`). */
  | { type: 'burst'; x: number; z: number; r: number }
  /** Kečup se naštval a vyprskl louži na cestu. */
  | { type: 'squirt'; attackerId: number }
  /** Lízátko se roztočilo; `stuck` je zelenina, kterou oblepilo. */
  | { type: 'spin'; attackerId: number; stuck: number[] }
  | { type: 'waveStart'; wave: number }
  | { type: 'unlocked'; defender: DefenderType }
  | { type: 'potato'; potatoId: number }
  | { type: 'bump'; potatoId: number; attackerId: number; x: number; z: number }
  | { type: 'crumble'; potatoId: number; x: number; z: number }
  | { type: 'won'; stars: number }
  | { type: 'lost' };

export type PlantCheck = PlaceCheck | 'locked' | 'water';

/** Herní logika bez grafiky: dá se spustit i v automatickém testu. */
export class Game {
  readonly path: Path;
  /** Šestihranná políčka, kam se dá sázet. */
  readonly slots: Vec2[];
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
  clouds: Cloud[] = [];
  puddles: Puddle[] = [];
  potatoes: Potato[] = [];
  readonly unlocked = new Set<DefenderType>();

  private events: GameEvent[] = [];
  private queue: Spawn[] = [];
  private spawnTimer = 0;
  private nextId = 1;

  constructor(readonly level: LevelData) {
    this.path = new Path(level.path);
    this.slots = hexSlots(level, this.path);
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
    this.clouds = [];
    this.puddles = [];
    this.potatoes = [];
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

  /** Může se sem (na cestu) postavit Pan Brambora? Zásobu brambor hlídá hra kolem (main). */
  checkPotato(p: Vec2): PotatoCheck {
    if (this.finished) return 'finished';
    const { d, dist } = this.path.project(p);
    if (dist > 0.75) return 'notPath';
    if (d > this.path.length - 1.6) return 'mouth';
    if (this.potatoes.some((o) => Math.abs(o.d - d) < POTATO.spacing)) return 'crowded';
    return 'ok';
  }

  /** Postaví Pana Bramboru na cestu (doprostřed cesty v nejbližším místě). */
  placePotato(p: Vec2): boolean {
    if (this.checkPotato(p) !== 'ok') return false;
    const d = Math.max(0.3, this.path.project(p).d);
    const at = this.path.at(d);
    const potato: Potato = { id: this.nextId++, d, x: at.x, z: at.z, lives: POTATO.lives };
    this.potatoes.push(potato);
    this.events.push({ type: 'potato', potatoId: potato.id });
    return true;
  }

  /** Dá se na tohle místo vůbec sázet (bez ohledu na vodu)? */
  checkPlace(p: Vec2): PlaceCheck {
    return checkPlace(this.level, this.path, this.slots, this.defenders, p);
  }

  /** Políčko pod prstem (střed šestihranu), nebo null. */
  slotAt(p: Vec2): Vec2 | null {
    return slotAt(this.level, this.slots, p);
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
    // Zelenina se zasadí doprostřed políčka.
    const d = createDefender(this.nextId++, type, this.slotAt(p)!);
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
    this.updateClouds(dt);
    this.updatePuddles(dt);
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
    if (d.stickyLeft > 0) {
      d.stickyLeft = Math.max(0, d.stickyLeft - dt);
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
    const at = this.path.at(target.d);
    this.events.push({ type: 'attack', defenderId: d.id, x: at.x, z: at.z });

    if (stats.cloudTime) {
      // Cibule nezasahuje: kolem sebe vypustí oblak smradu.
      this.clouds.push({ id: this.nextId++, x: d.x, z: d.z, r: stats.range, left: stats.cloudTime, life: stats.cloudTime });
      this.events.push({ type: 'cloud', defenderId: d.id, x: d.x, z: d.z, r: stats.range });
      return;
    }
    const rocketTime = DEFENDERS[d.type].rocketTime;
    if (rocketTime) {
      // Brokolice: růžička letí vysokým obloukem za cílem a nad ním se rozprskne.
      const p = this.path.at(target.d);
      this.projectiles.push({
        id: this.nextId++,
        kind: 'brokolice',
        x0: d.x,
        z0: d.z,
        tx: p.x,
        tz: p.z,
        t: 0,
        duration: rocketTime,
        targetId: target.id,
        splash: stats.splash,
      });
      return;
    }
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
      this.hitAttacker(target, true);
    }
  }

  private updateClouds(dt: number): void {
    if (!this.clouds.length) return;
    for (const c of this.clouds) c.left -= dt;
    this.clouds = this.clouds.filter((c) => c.left > 0);
  }

  private updatePuddles(dt: number): void {
    if (!this.puddles.length) return;
    for (const p of this.puddles) p.left -= dt;
    this.puddles = this.puddles.filter((p) => p.left > 0);
  }

  /** Zrychlení fast foodu na kečupu (1 = bez kečupu). */
  private puddleBoost(a: Attacker): number {
    a.sliding = this.puddles.some((p) => a.d >= p.d0 && a.d <= p.d1);
    return a.sliding ? ATTACKERS.kecup.squirt!.boost : 1;
  }

  /** Zpomalení fast foodu v oblaku smradu (1 = bez oblaku). */
  private cloudSlow(a: Attacker): number {
    const p = this.path.at(a.d);
    a.slowed = this.clouds.some((c) => Math.hypot(c.x - p.x, c.z - p.z) <= c.r + ATTACKER_BODY_RADIUS);
    return a.slowed ? DEFENDERS.cibule.cloudSlow! : 1;
  }

  /** Nejdál došlý fast food v dosahu, který ještě neutíká. */
  private pickTarget(x: number, z: number, range: number): Attacker | undefined {
    let best: Attacker | undefined;
    for (const a of this.attackers) {
      if (a.fleeing) continue;
      const p = this.path.at(a.d);
      if (Math.hypot(p.x - x, p.z - z) > range + ATTACKER_BODY_RADIUS) continue;
      if (!best || a.d > best.d) best = a;
    }
    return best;
  }

  private hitAttacker(a: Attacker, melee = false): void {
    if (a.fleeing) return;
    const p = this.path.at(a.d);
    a.hitsLeft--;
    this.events.push({ type: 'hit', attackerId: a.id, x: p.x, z: p.z, melee });
    if (a.hitsLeft > 0) return;
    a.fleeing = true;
    const reward = Math.round((ATTACKERS[a.type].reward * (this.level.rewardScale ?? 1)) / 5) * 5;
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

    const spin = stats.spin;
    if (spin && this.updateSpin(a, spin, dt)) return false;
    const squirt = stats.squirt;
    if (squirt && this.updateSquirt(a, squirt, dt)) return false;
    const before = a.d;
    a.d += stats.speed * (this.level.waveSpeed?.[this.waveIndex] ?? 1) * this.cloudSlow(a) * this.puddleBoost(a) * dt;
    // Pan Brambora na cestě: fast food se zastaví u jeho štítu a naráží do něj.
    const wall = this.potatoAhead(before);
    if (wall && a.d > wall.d - POTATO.blockGap) {
      a.d = Math.max(before, wall.d - POTATO.blockGap);
      a.bumpCooldown -= dt;
      if (a.bumpCooldown <= 0) {
        a.bumpCooldown = POTATO.bumpInterval;
        this.bumpPotato(wall, a);
      }
    }
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

  /** Nejbližší Pan Brambora před fast foodem (na cestě dál než `d`). */
  private potatoAhead(d: number): Potato | undefined {
    let best: Potato | undefined;
    for (const p of this.potatoes) if (p.d > d && (!best || p.d < best.d)) best = p;
    return best;
  }

  /** Fast food narazí do štítu: Pan Brambora přijde o srdíčko, bez srdíček se rozpadne. */
  private bumpPotato(p: Potato, a: Attacker): void {
    p.lives--;
    this.events.push({ type: 'bump', potatoId: p.id, attackerId: a.id, x: p.x, z: p.z });
    if (p.lives > 0) return;
    this.potatoes = this.potatoes.filter((o) => o !== p);
    this.events.push({ type: 'crumble', potatoId: p.id, x: p.x, z: p.z });
  }

  /** Lízátko: roztočení. Vrací true, dokud se točí (stojí na místě). */
  private updateSpin(a: Attacker, spin: SpinStats, dt: number): boolean {
    if (a.spinLeft > 0) {
      a.spinLeft = Math.max(0, a.spinLeft - dt);
      return true;
    }
    a.spinCooldown -= dt;
    if (a.spinCooldown > 0) return false;
    const p = this.path.at(a.d);
    // Oblepit jde jen vyrostlá zelenina (rostoucí je schovaná v zemi).
    const stuck = this.defenders.filter((d) => isGrown(d) && Math.hypot(d.x - p.x, d.z - p.z) <= spin.range);
    if (!stuck.length) {
      a.spinCooldown = 0.25;
      return false;
    }
    a.spinCooldown = spin.interval;
    a.spinLeft = spin.duration;
    for (const d of stuck) d.stickyLeft = spin.sticky;
    this.events.push({ type: 'spin', attackerId: a.id, stuck: stuck.map((d) => d.id) });
    return true;
  }

  /** Kečup: naštvání a vyprsknutí louže. Vrací true, dokud prská (stojí na místě). */
  private updateSquirt(a: Attacker, squirt: SquirtStats, dt: number): boolean {
    if (a.squirtLeft > 0) {
      a.squirtLeft = Math.max(0, a.squirtLeft - dt);
      return true;
    }
    a.squirtCooldown -= dt;
    // Prská jen na cestu, kde ještě zbývá kus k puse.
    if (a.squirtCooldown > 0 || a.d < 0.5 || a.d > this.path.length - 1) return false;
    a.squirtCooldown = squirt.interval;
    a.squirtLeft = squirt.duration;
    this.puddles.push({
      id: this.nextId++,
      d0: a.d,
      d1: Math.min(this.path.length, a.d + squirt.length),
      left: squirt.dry,
      life: squirt.dry,
    });
    this.events.push({ type: 'squirt', attackerId: a.id });
    return true;
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
      if (p.kind === 'brokolice') {
        const target = this.attackers.find((a) => a.id === p.targetId);
        if (target && !target.fleeing) {
          const pos = this.path.at(target.d);
          p.tx = pos.x;
          p.tz = pos.z;
        }
        if (p.t < p.duration) {
          left.push(p);
          continue;
        }
        // Bum! Každý fast food pod deštníkem dostane jeden zásah.
        const r = p.splash ?? 1;
        this.events.push({ type: 'burst', x: p.tx, z: p.tz, r });
        for (const a of this.attackers) {
          if (a.fleeing) continue;
          const q = this.path.at(a.d);
          if (Math.hypot(q.x - p.tx, q.z - p.tz) <= r + ATTACKER_BODY_RADIUS) this.hitAttacker(a);
        }
      } else if (p.kind === 'porek') {
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
