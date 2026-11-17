import * as THREE from 'three';
import type { Game, GameEvent } from '../core/game';
import type { LevelData } from '../data/level1';
import { ATTACKER_BODY_RADIUS, ATTACKERS, DEFENDERS, MOUTH_LIVES, type DefenderType } from '../data/units';
import { defenderLevel } from '../entities/obranci/defender';
import { buildBoard, type Board } from './board';
import { Path } from '../core/path';
import { hexSlots } from '../core/placement';
import { Critters } from './decor';
import { SlotsView } from './slots';
import {
  attackerFrames,
  makeAttacker,
  makeCloud,
  makeDefender,
  makeHitStar,
  makeLifeBar,
  makeMouth,
  makeProjectile,
  makePuddlePiece,
  makeUmbrella,
  preloadFrames,
  type LifeBar,
  type Puppet,
} from './meshes';
import type { Stage } from './stage';

interface Anim {
  puppet: Puppet;
  /** Sekundy od posledního útoku / zásahu / hodu / radosti. */
  attackT: number;
  hitT: number;
  throwT: number;
  /** Lízátko: sekundy od začátku roztočení. */
  spinT: number;
  joyT: number;
  /** Kdy příště mrknout. */
  blinkAt: number;
  /**
   * Kam je postava otočená: 1 doprava (jak je nakreslená, mrkvomeč i luk vpravo), −1 doleva.
   * Zelenina se otáčí k cíli, aby sekla nebo střílela tou rukou, která je blíž k cestě.
   */
  face: number;
  /** Kam mrkev naposledy sekla (místo cíle), aby k němu při seku doskočila. */
  target: { x: number; z: number } | null;
}

interface Effect {
  obj: THREE.Object3D;
  age: number;
  life: number;
  step: (e: Effect, k: number, dt: number) => void;
}

const MOUTH_SICK = new THREE.Color(0xa6e07a);
const WHITE = new THREE.Color(0xffffff);
const puffGeo = new THREE.SphereGeometry(0.3, 12, 8);
const dotGeo = new THREE.SphereGeometry(0.07, 8, 6);

function newAnim(puppet: Puppet): Anim {
  return { puppet, attackT: 99, hitT: 99, throwT: 99, spinT: 99, joyT: 99, blinkAt: 1 + Math.random() * 3, face: 1, target: null };
}

/** Převádí stav hry na 3D scénu: papírové loutky, střely a efekty. */
/** Jak dlouho trvá sek nebo výstřel (s). */
const ATTACK_TIME = 0.3;
/** Jak dlouho se cibule naježí a vypouští oblak (s). */
const CLOUD_ANIM = 1.1;

const FROZEN: Record<DefenderType, string> = {
  mrkev: 'mrkev-ztuhla',
  porek: 'porek-ztuhl',
  cibule: 'cibule-ztuhla',
  brokolice: 'brokolice-ztuhla',
};
const STICKY: Record<DefenderType, string> = {
  mrkev: 'mrkev-lepkava',
  porek: 'porek-lepkavy',
  cibule: 'cibule-lepkava',
  brokolice: 'brokolice-lepkava',
};
const STICKY_HALF: Record<DefenderType, string> = {
  mrkev: 'mrkev-lepkava2',
  porek: 'porek-lepkavy2',
  cibule: 'cibule-lepkava2',
  brokolice: 'brokolice-lepkava2',
};
/** Dosah: mrkev oranžově, ostatní modře (barvy z návrhu). */
const RANGE_COLOR: Record<DefenderType, number> = { mrkev: 0xf08a24, porek: 0x2d8cd6, cibule: 0x2d8cd6, brokolice: 0x2d8cd6 };
/** Brokolice: utržení růžičky a hod (s). */
const PLUCK_TIME = 0.3;
const THROW_TIME = 0.6;
/** Kečup: jak dlouho se zlobí, než vyprskne (s). */
const MAD_TIME = 0.4;
/** Kousky louže leží na cestě po tomhle kroku (políčka). */
const PUDDLE_STEP = 0.6;
/** Jak daleko od středu mrkve sahá špička mrkvomeče (políčka). */
const SWORD_REACH = 0.45;
/** Kdy je mrkev při seku nejdál (první třetina seku). */
const LUNGE_PEAK = ATTACK_TIME / 3;

export class View {
  readonly board: Board;
  private readonly dynamic = new THREE.Group();
  private readonly defenders = new Map<number, Anim>();
  private readonly attackers = new Map<number, Anim>();
  /** Srdíčka zbývajících životů nad každým fast foodem. */
  private readonly lifeBars = new Map<number, LifeBar>();
  private readonly projectiles = new Map<number, THREE.Sprite>();
  private readonly clouds = new Map<number, THREE.Mesh>();
  private readonly puddles = new Map<number, THREE.Group>();
  private effects: Effect[] = [];
  private pending: { t: number; fn: () => void }[] = [];
  private readonly mouth: Puppet;
  private mouthPulse = 1;
  private mouthMood: 'play' | 'won' | 'lost' = 'play';
  private readonly ring: THREE.Group;
  private readonly ringFill: THREE.MeshBasicMaterial;
  private readonly ringEdge: THREE.MeshBasicMaterial;
  private readonly slots: SlotsView;
  private readonly critters = new Critters();
  private readonly tmpA = new THREE.Vector3();
  private readonly tmpB = new THREE.Vector3();

  constructor(
    private readonly stage: Stage,
    private readonly level: LevelData,
  ) {
    preloadFrames();
    this.board = buildBoard(level);
    stage.scene.add(this.board.root, this.dynamic);

    this.mouth = makeMouth();
    this.mouth.root.position.set(level.mouth.x + 0.3, 0, level.mouth.z);
    stage.scene.add(this.mouth.root);

    this.ring = new THREE.Group();
    this.ringFill = new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.12, depthWrite: false });
    this.ringEdge = new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.95, depthWrite: false });
    this.ring.add(new THREE.Mesh(new THREE.CircleGeometry(1, 48), this.ringFill));
    // Přerušovaný okraj jako v návrhu.
    const dashes = 28;
    for (let i = 0; i < dashes; i++) {
      const arc = (Math.PI * 2) / dashes;
      this.ring.add(new THREE.Mesh(new THREE.RingGeometry(0.965, 1, 4, 1, i * arc, arc * 0.58), this.ringEdge));
    }
    this.ring.rotation.x = -Math.PI / 2;
    this.ring.visible = false;
    stage.scene.add(this.ring);

    // Šestihranná políčka na sázení a poletující motýli a včelka z návrhu.
    this.slots = new SlotsView(hexSlots(level, new Path(level.path)), level.hexGrid);
    stage.scene.add(this.slots.root, this.critters.root);
  }

  /** Dosah zeleniny (barvy z návrhu). */
  showRange(x: number, z: number, r: number, type: DefenderType): void {
    const color = RANGE_COLOR[type];
    this.ringFill.color.setHex(color);
    this.ringEdge.color.setHex(color);
    this.ring.position.set(x, 0.06, z);
    this.ring.scale.setScalar(r);
    this.ring.visible = true;
  }

  hideRange(): void {
    this.ring.visible = false;
  }

  /** Vybrané políčko, kam se chystá sázet: bílé se zeleným okrajem. */
  showSpot(x: number, z: number): void {
    this.slots.select({ x, z });
  }

  hideSpot(): void {
    this.slots.select(null);
  }

  reset(): void {
    this.pending = [];
    this.dynamic.clear();
    this.defenders.clear();
    this.attackers.clear();
    for (const life of this.lifeBars.values()) life.dispose();
    this.lifeBars.clear();
    this.projectiles.clear();
    this.clouds.clear();
    this.puddles.clear();
    this.effects = [];
    this.mouthMood = 'play';
    this.mouthPulse = 1;
    this.hideRange();
    this.hideSpot();
  }

  handleEvents(events: GameEvent[], game: Game): void {
    for (const e of events) {
      switch (e.type) {
        case 'attack': {
          const a = this.defenders.get(e.defenderId);
          if (a) {
            a.attackT = 0;
            a.target = { x: e.x, z: e.z };
            // Otočit se k cíli; když stojí skoro přesně nad nebo pod zeleninou, zůstat otočená.
            const dx = e.x - a.puppet.root.position.x;
            if (Math.abs(dx) > 0.15) a.face = Math.sign(dx);
          }
          break;
        }
        case 'hit': {
          // Sek mrkve: fast food cukne, až k němu mrkev doskočí (v nejzazším bodě výpadu).
          const delay = e.melee ? LUNGE_PEAK : 0;
          const a = this.attackers.get(e.attackerId);
          if (a) a.hitT = -delay;
          // Zásah je vidět jako žlutá hvězdička na fast foodu (jako v návrhu karet postav).
          const y = a ? a.puppet.height * a.puppet.root.scale.y * 0.5 : 0.8;
          this.later(delay, () => this.hitStar(e.x, y, e.z));
          break;
        }
        case 'flee': {
          this.burst(e.x, 0.7, e.z, 0x4fb3ff, 6);
          // Zelenina, která pomohla, se raduje.
          for (const d of game.defenders) {
            if (Math.hypot(d.x - e.x, d.z - e.z) <= defenderLevel(d).range + 0.5) {
              const a = this.defenders.get(d.id);
              if (a) a.joyT = 0;
            }
          }
          break;
        }
        case 'throw': {
          const a = this.attackers.get(e.attackerId);
          if (a) a.throwT = 0;
          break;
        }
        case 'spin': {
          // Lízátko se roztočí a oblepí zeleninu kolem sebe: „Plác!“ (červené kapky šťávy).
          const a = this.attackers.get(e.attackerId);
          if (a) a.spinT = 0;
          for (const id of e.stuck) {
            const d = this.defenders.get(id);
            if (d) this.later(0.25, () => this.burst(d.puppet.root.position.x, 1.0, d.puppet.root.position.z, 0xe8424a, 7));
          }
          break;
        }
        case 'burst':
          // Bum! Růžička se nad cílem rozprskne do deštníku z malých růžiček.
          this.umbrella(e.x, e.z, e.r);
          this.burst(e.x, 0.8, e.z, 0x4caf50, 8);
          break;
        case 'squirt': {
          const a = this.attackers.get(e.attackerId);
          if (a) a.throwT = 0;
          break;
        }
        case 'escaped':
          this.puff(e.x, e.z, 0xffffff, 1.6);
          break;
        case 'miss':
          this.puff(e.x, e.z, 0xc9b38a, 0.7);
          break;
        case 'frozen': {
          const d = this.defenders.get(e.defenderId);
          if (d) this.puff(d.puppet.root.position.x, d.puppet.root.position.z, 0x9fd8ff, 1);
          break;
        }
        case 'bite':
          this.mouthPulse = 1.3;
          break;
        case 'won':
          this.mouthMood = 'won';
          break;
        case 'lost':
          this.mouthMood = 'lost';
          break;
        default:
          break;
      }
    }
  }

  update(game: Game, dt: number, time: number): void {
    this.syncDefenders(game, dt, time);
    this.syncAttackers(game, dt, time);
    this.syncProjectiles(game, time);
    this.syncClouds(game);
    this.syncPuddles(game);
    this.updateMouth(game, dt, time);
    this.updateEffects(dt);
    this.slots.update(game.defenders);
    this.critters.update(time);
  }

  private syncDefenders(game: Game, dt: number, time: number): void {
    const alive = new Set<number>();
    for (const d of game.defenders) {
      alive.add(d.id);
      let anim = this.defenders.get(d.id);
      if (!anim) {
        const puppet = makeDefender(d.type);
        puppet.root.position.set(d.x, 0, d.z);
        this.dynamic.add(puppet.root);
        anim = newAnim(puppet);
        anim.face = this.faceTowardsPath(game, d.x, d.z);
        this.defenders.set(d.id, anim);
      }
      anim.attackT += dt;
      anim.joyT += dt;
      const { sprite, width, height } = anim.puppet;
      const prefix = d.level >= 2 ? `${d.type}2` : d.type;

      // Vyrůstání: loutka vyleze ze záhonu se zavřenýma očima.
      if (d.growLeft > 0) {
        const k = 1 - d.growLeft / DEFENDERS[d.type].growTime;
        anim.puppet.setMirrored(anim.face < 0);
        sprite.scale.set(width * (0.6 + 0.4 * k), height * Math.max(0.05, k), 1);
        sprite.position.set(0, 0, 0);
        anim.puppet.setFrame(`${d.type}-mrk`);
        continue;
      }

      let frame = `${prefix}-klid`;
      let squash = Math.sin(time * 3 + d.id) * 0.02;
      let jitter = 0;
      let hop = 0;
      let lungeX = 0;
      let lungeZ = 0;
      if (d.frozenLeft > 0) {
        frame = FROZEN[d.type];
        jitter = Math.sin(time * 60) * 0.04;
        squash = 0;
      } else if (d.stickyLeft > 0) {
        // Oblepená šťávou z lízátka: nejdřív celá, v druhé polovině už šťáva stéká dolů.
        const half = d.stickyLeft < ATTACKERS.lizatko.spin!.sticky / 2;
        frame = half ? STICKY_HALF[d.type] : STICKY[d.type];
        squash = 0;
      } else if (d.type === 'cibule' && anim.attackT < CLOUD_ANIM) {
        // Cibule se naježí (třese se), pak vypustí oblak: „Pššš!“
        if (anim.attackT < 0.35) {
          frame = `${prefix}-nalez`;
          jitter = Math.sin(time * 70) * 0.05;
        } else {
          frame = `${prefix}-smrad`;
          squash = -Math.sin(((anim.attackT - 0.35) / (CLOUD_ANIM - 0.35)) * Math.PI) * 0.06;
        }
      } else if (d.type === 'brokolice' && anim.attackT < THROW_TIME) {
        // Brokolice si utrhne z korunky růžičku a vystřelí ji jako raketu.
        frame = anim.attackT < PLUCK_TIME ? `${prefix}-mir` : `${prefix}-hod`;
        squash = anim.attackT < PLUCK_TIME ? 0 : -Math.sin(((anim.attackT - PLUCK_TIME) / (THROW_TIME - PLUCK_TIME)) * Math.PI) * 0.08;
      } else if (d.type !== 'cibule' && anim.attackT < ATTACK_TIME) {
        frame = d.type === 'mrkev' ? `${prefix}-sek` : `${prefix}-vystrel`;
        squash = -Math.sin((anim.attackT / ATTACK_TIME) * Math.PI) * 0.08;
        if (d.type === 'mrkev' && anim.target) [lungeX, lungeZ] = this.lunge(anim, d.x, d.z);
      } else if (anim.joyT < 0.7) {
        frame = `${prefix}-radost`;
        hop = Math.abs(Math.sin((anim.joyT / 0.7) * Math.PI * 2)) * 0.25;
      } else if (d.type === 'porek' && this.hasTarget(game, d.x, d.z, defenderLevel(d).range)) {
        frame = `${prefix}-miri`;
      } else if (d.type === 'brokolice') {
        // Pohupuje korunkou a občas mrkne.
        squash = Math.sin(time * 2 + d.id) * 0.03;
        if (time > anim.blinkAt + 0.15) anim.blinkAt = time + 2 + Math.random() * 3;
        if (time > anim.blinkAt) frame = `${prefix}-mrk`;
      } else {
        // Mrkání: čas od času na chvilku zavře oči.
        if (time > anim.blinkAt + 0.15) anim.blinkAt = time + 2 + Math.random() * 3;
        if (time > anim.blinkAt) frame = `${prefix}-mrk`;
      }
      anim.puppet.setFrame(frame);
      anim.puppet.setMirrored(anim.face < 0);
      sprite.scale.set(width * (1 - squash * 0.5), height * (1 + squash), 1);
      sprite.position.set(jitter + lungeX, hop, lungeZ);
    }
    this.removeMissing(this.defenders, alive);
  }

  /**
   * Výpad mrkve při seku: mrkev rychle doskočí k fast foodu, aby se ho mrkvomeč opravdu
   * dotkl, a vrátí se zpátky na své políčko. Vrací posun loutky v ose x a z.
   */
  private lunge(anim: Anim, x: number, z: number): [number, number] {
    const t = anim.target!;
    const dx = t.x - x;
    const dz = t.z - z;
    const dist = Math.hypot(dx, dz);
    // Špička mrkvomeče je asi 0,45 políčka od středu mrkve, fast food má tělo 0,35 políčka.
    const reach = Math.max(0, dist - SWORD_REACH - ATTACKER_BODY_RADIUS);
    if (dist < 1e-6 || reach === 0) return [0, 0];
    // Rychle tam (první třetina seku), pomaleji zpátky.
    const k = anim.attackT / ATTACK_TIME;
    const out = k < 1 / 3 ? Math.sin((k * 3 * Math.PI) / 2) : Math.cos(((k - 1 / 3) * 1.5 * Math.PI) / 2);
    return [(dx / dist) * reach * out, (dz / dist) * reach * out];
  }

  /** Oblaky smradu cibule: rychle se nafouknou a na konci vyblednou. */
  private syncClouds(game: Game): void {
    const alive = new Set<number>();
    for (const c of game.clouds) {
      alive.add(c.id);
      let m = this.clouds.get(c.id);
      if (!m) {
        m = makeCloud(c.r);
        m.position.set(c.x, 0.08, c.z);
        this.dynamic.add(m);
        this.clouds.set(c.id, m);
      }
      const age = c.life - c.left;
      const grow = Math.min(1, age / 0.35);
      m.scale.setScalar(0.5 + 0.5 * grow);
      (m.material as THREE.MeshBasicMaterial).opacity = 0.6 * Math.min(1, c.left / 0.6);
    }
    for (const [id, m] of this.clouds) {
      if (!alive.has(id)) {
        this.dynamic.remove(m);
        this.clouds.delete(id);
      }
    }
  }

  /** Na kterou stranu má zelenina k nejbližšímu kousku cesty (1 doprava, −1 doleva). */
  private faceTowardsPath(game: Game, x: number, z: number): number {
    let best = { x: x + 1, dist: Infinity };
    for (let d = 0; d <= game.path.length; d += 0.2) {
      const p = game.path.at(d);
      const dist = Math.hypot(p.x - x, p.z - z);
      if (dist < best.dist) best = { x: p.x, dist };
    }
    return best.x < x - 0.15 ? -1 : 1;
  }

  private hasTarget(game: Game, x: number, z: number, range: number): boolean {
    return game.attackers.some((a) => {
      if (a.fleeing) return false;
      const p = game.path.at(a.d);
      return Math.hypot(p.x - x, p.z - z) <= range + ATTACKER_BODY_RADIUS;
    });
  }

  private syncAttackers(game: Game, dt: number, time: number): void {
    const alive = new Set<number>();
    for (const a of game.attackers) {
      alive.add(a.id);
      let anim = this.attackers.get(a.id);
      if (!anim) {
        const puppet = makeAttacker(a.type);
        this.dynamic.add(puppet.root);
        anim = newAnim(puppet);
        this.attackers.set(a.id, anim);
        const life = makeLifeBar(ATTACKERS[a.type].hits);
        // Štítek nad hlavou; u velkého hamburgeru je loutka zvětšená, štítek ale stejně velký.
        const k = 1 / puppet.root.scale.x;
        life.sprite.scale.multiplyScalar(k);
        life.sprite.position.set(0, puppet.height * 0.94, 0);
        puppet.root.add(life.sprite);
        this.lifeBars.set(a.id, life);
      }
      const life = this.lifeBars.get(a.id)!;
      life.set(a.hitsLeft);
      // Utíkající fast food už životy nepotřebuje.
      life.sprite.visible = !a.fleeing;
      anim.hitT += dt;
      anim.throwT += dt;
      anim.spinT += dt;
      const p = game.path.at(a.d);
      const { root, sprite, width, height } = anim.puppet;
      root.position.set(p.x, 0, p.z);

      const base = attackerFrames(a.type);
      const step = Math.floor(time * (a.fleeing ? 7 : 4) + a.id) % 2 === 0;
      let frame = `${base}-krok${step ? 1 : 2}`;
      let squash = 0;
      if (a.fleeing) frame = `${base}-utek${step ? 1 : 2}`;
      else if (anim.hitT >= 0 && anim.hitT < 0.25) {
        frame = `${base}-zasah`;
        squash = Math.sin((anim.hitT / 0.25) * Math.PI) * 0.15;
      } else if (base === 'hranolky' && anim.throwT < 0.15) frame = 'hranolky-naprah';
      else if (base === 'hranolky' && anim.throwT < 0.45) frame = 'hranolky-hod';
      else if (base === 'lizatko' && a.spinLeft > 0) frame = anim.spinT < 0.2 ? 'lizatko-naprah' : 'lizatko-toci';
      else if (base === 'kecup' && a.squirtLeft > 0) frame = anim.throwT < MAD_TIME ? 'kecup-nastvani' : 'kecup-prsk';
      anim.puppet.setFrame(frame);

      // Otočit loutku podle toho, kam jde na obrazovce (doleva / doprava).
      const dir = a.fleeing ? -1 : 1;
      const sx = this.screenDirX(p.x, p.z, p.dirX * dir, p.dirZ * dir);
      // Při chůzi skoro svisle nahoru nebo dolů zůstane otočená, jak byla, aby necukala.
      if (base === 'lizatko' && a.spinLeft > 0) {
        // Roztočení: lízátko se otáčí sem a tam.
        anim.puppet.setMirrored(Math.floor(anim.spinT * 10) % 2 === 1);
      } else if (Math.abs(sx) > 0.2) anim.puppet.setMirrored(sx < 0);
      let bounce = Math.abs(Math.sin(time * (a.fleeing ? 14 : 8) + a.id)) * (a.fleeing ? 0.14 : 0.07);
      let tilt = 0;
      if (base === 'kecup' && a.squirtLeft > 0 && anim.throwT < MAD_TIME) {
        // Naštvaný kečup poskočí do vzduchu.
        bounce = Math.sin((anim.throwT / MAD_TIME) * Math.PI) * 0.45;
      } else if (a.sliding && !a.fleeing) {
        // Klouže po kečupu: nehýbe nohama, jen se nakloní dopředu („Víííí!“).
        bounce = 0;
        tilt = anim.puppet.mirrored ? 0.25 : -0.25;
      }
      sprite.scale.set(width * (1 + squash * 0.6), height * (1 - squash), 1);
      sprite.position.set(0, bounce, 0);
      (sprite.material as THREE.SpriteMaterial).rotation = tilt;
    }
    this.removeMissing(this.attackers, alive);
    for (const [id, life] of this.lifeBars) {
      if (!alive.has(id)) {
        life.dispose();
        this.lifeBars.delete(id);
      }
    }
  }

  /** Vodorovný směr pohybu na obrazovce (kladný = doprava). */
  private screenDirX(x: number, z: number, dx: number, dz: number): number {
    const cam = this.stage.camera;
    const a = this.tmpA.set(x, 0.5, z).project(cam);
    const b = this.tmpB.set(x + dx * 0.3, 0.5, z + dz * 0.3).project(cam);
    return b.x - a.x;
  }

  private syncProjectiles(game: Game, time: number): void {
    const alive = new Set<number>();
    for (const p of game.projectiles) {
      alive.add(p.id);
      let s = this.projectiles.get(p.id);
      if (!s) {
        s = makeProjectile(p.kind);
        this.dynamic.add(s);
        this.projectiles.set(p.id, s);
      }
      const k = Math.min(1, p.t / p.duration);
      // Brokolicová raketa letí vysokým obloukem a rozprskne se nad cílem.
      const arc = p.kind === 'brokolice' ? 3 : p.kind === 'porek' ? 1.1 : 0.9;
      const endY = p.kind === 'brokolice' ? 1.4 : 0.9;
      const at = (t: number) => ({
        x: p.x0 + (p.tx - p.x0) * t,
        y: 0.9 + (endY - 0.9) * t + Math.sin(t * Math.PI) * arc,
        z: p.z0 + (p.tz - p.z0) * t,
      });
      const now = at(k);
      s.position.set(now.x, now.y, now.z);
      const mat = s.material as THREE.SpriteMaterial;
      if (p.kind === 'porek' || p.kind === 'brokolice') {
        // Pórkošíp a raketa letí hrotem napřed po oblouku.
        const next = at(Math.min(1, k + 0.05));
        const cam = this.stage.camera;
        const a = this.tmpA.set(now.x, now.y, now.z).project(cam);
        const b = this.tmpB.set(next.x, next.y, next.z).project(cam);
        mat.rotation = Math.atan2((b.y - a.y) * this.stage.height, (b.x - a.x) * this.stage.width);
      } else {
        mat.rotation = time * 12;
      }
    }
    for (const [id, s] of this.projectiles) {
      if (!alive.has(id)) {
        this.dynamic.remove(s);
        this.projectiles.delete(id);
      }
    }
  }

  /** Kečupové louže: kousky louže podél cesty, na konci zaschnou (vyblednou). */
  private syncPuddles(game: Game): void {
    const alive = new Set<number>();
    for (const p of game.puddles) {
      alive.add(p.id);
      let g = this.puddles.get(p.id);
      if (!g) {
        g = new THREE.Group();
        const n = Math.max(1, Math.round((p.d1 - p.d0) / PUDDLE_STEP));
        for (let i = 0; i <= n; i++) {
          const at = game.path.at(p.d0 + ((p.d1 - p.d0) * i) / n);
          const m = makePuddlePiece();
          m.position.set(at.x + (Math.random() - 0.5) * 0.12, 0.05 + i * 0.001, at.z + (Math.random() - 0.5) * 0.12);
          // Louže leží jako v návrhu (naplocho, skoro vodorovně), kousky se překrývají.
          m.rotation.z = (Math.random() - 0.5) * 0.5;
          m.scale.setScalar(0.7 + Math.random() * 0.25);
          g.add(m);
        }
        this.dynamic.add(g);
        this.puddles.set(p.id, g);
      }
      // Louže se rozlije postupně od kečupu dopředu a na konci zaschne.
      const age = p.life - p.left;
      const shown = Math.min(1, age / 0.4);
      const fade = Math.min(1, p.left / 0.8);
      g.children.forEach((c, i) => {
        const m = c as THREE.Mesh;
        m.visible = i / g!.children.length <= shown;
        (m.material as THREE.MeshBasicMaterial).opacity = fade;
      });
    }
    for (const [id, g] of this.puddles) {
      if (!alive.has(id)) {
        this.dynamic.remove(g);
        this.puddles.delete(id);
      }
    }
  }

  private updateMouth(game: Game, dt: number, time: number): void {
    const m = this.mouth;
    const mat = m.sprite.material as THREE.SpriteMaterial;
    // Po každém kousnutí je pusa zelenější.
    mat.color.copy(WHITE).lerp(MOUTH_SICK, Math.min(1, game.bites / MOUTH_LIVES) * 0.85);

    this.mouthPulse += (1 - this.mouthPulse) * Math.min(1, dt * 6);
    let s = this.mouthPulse;
    let shake = 0;
    if (this.mouthMood === 'won') s *= 1 + Math.abs(Math.sin(time * 6)) * 0.1;
    else if (this.mouthMood === 'lost') {
      shake = Math.sin(time * 20) * 0.05;
      if (Math.random() < dt * 40) this.vomitDrop();
    } else {
      // nervózní pohled, když je fast food blízko
      const near = game.attackers.some((a) => !a.fleeing && game.path.length - a.d < 3);
      if (near) shake = Math.sin(time * 30) * 0.03;
    }
    m.sprite.scale.set(m.width * s, m.height * s, 1);
    m.sprite.position.x = shake;
  }

  // --- efekty ---

  private puff(x: number, z: number, color: number, size: number): void {
    const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.85, depthWrite: false });
    const mesh = new THREE.Mesh(puffGeo, mat);
    mesh.position.set(x, 0.5, z);
    this.addEffect(mesh, 0.45, (e, k) => {
      e.obj.scale.setScalar(size * (0.4 + k));
      mat.opacity = 0.85 * (1 - k);
    });
  }

  /** Deštník z malých růžiček nad místem dopadu brokolicové rakety. */
  private umbrella(x: number, z: number, r: number): void {
    const s = makeUmbrella(r);
    const mat = s.material as THREE.SpriteMaterial;
    const base = s.scale.x;
    s.position.set(x, 0.9, z);
    this.addEffect(s, 0.6, (e, k) => {
      e.obj.scale.set(base * (0.6 + 0.4 * Math.min(1, k * 3)), base * (0.6 + 0.4 * Math.min(1, k * 3)), 1);
      e.obj.position.y = 0.9 - k * 0.3;
      mat.opacity = k < 0.6 ? 1 : 1 - (k - 0.6) / 0.4;
      if (k >= 1) mat.dispose();
    });
  }

  /** Hvězdička zásahu: rychle se zvětší, pootočí a zmizí. */
  private hitStar(x: number, y: number, z: number): void {
    const star = makeHitStar();
    star.position.set(x, y, z);
    const mat = star.material as THREE.SpriteMaterial;
    this.addEffect(star, 0.28, (_e, k) => {
      const size = 0.38 + 0.42 * Math.sin(Math.min(1, k * 1.6) * (Math.PI / 2));
      star.scale.set(size, size, 1);
      mat.rotation = k * 0.5;
      mat.opacity = k < 0.6 ? 1 : 1 - (k - 0.6) / 0.4;
    });
  }

  private burst(x: number, y: number, z: number, color: number, count: number): void {
    for (let i = 0; i < count; i++) {
      const mesh = new THREE.Mesh(dotGeo, new THREE.MeshBasicMaterial({ color }));
      mesh.position.set(x, y, z);
      const vx = (Math.random() - 0.5) * 3;
      const vz = (Math.random() - 0.5) * 3;
      let vy = 2 + Math.random() * 2;
      this.addEffect(mesh, 0.5, (e, _k, dt) => {
        vy -= 9 * dt;
        e.obj.position.x += vx * dt;
        e.obj.position.y = Math.max(0.05, e.obj.position.y + vy * dt);
        e.obj.position.z += vz * dt;
      });
    }
  }

  /** Prohra: komiksový zelený proud z pusy, nic nechutného. */
  private vomitDrop(): void {
    const colors = [0x7fc23a, 0xa6e05a, 0xffe14d];
    const mesh = new THREE.Mesh(dotGeo, new THREE.MeshBasicMaterial({ color: colors[Math.floor(Math.random() * 3)] }));
    mesh.scale.setScalar(1.5 + Math.random());
    mesh.position.set(this.level.mouth.x - 0.3, 1.1, this.level.mouth.z + 0.2);
    const vx = -2.5 - Math.random() * 1.5;
    const vz = (Math.random() - 0.3) * 1.5;
    let vy = 1.5 + Math.random();
    this.addEffect(mesh, 1, (e, _k, dt) => {
      vy -= 6 * dt;
      e.obj.position.x += vx * dt;
      e.obj.position.y = Math.max(0.05, e.obj.position.y + vy * dt);
      e.obj.position.z += vz * dt;
    });
  }

  private addEffect(obj: THREE.Object3D, life: number, step: Effect['step']): void {
    this.dynamic.add(obj);
    this.effects.push({ obj, age: 0, life, step });
  }

  /** Udělá něco o chvilku později (efekt zásahu ve chvíli, kdy mrkvomeč dosekne). */
  private later(seconds: number, fn: () => void): void {
    if (seconds <= 0) fn();
    else this.pending.push({ t: seconds, fn });
  }

  private updateEffects(dt: number): void {
    this.pending = this.pending.filter((p) => {
      p.t -= dt;
      if (p.t > 0) return true;
      p.fn();
      return false;
    });
    this.effects = this.effects.filter((e) => {
      e.age += dt;
      const k = Math.min(1, e.age / e.life);
      e.step(e, k, dt);
      if (k >= 1) {
        this.dynamic.remove(e.obj);
        return false;
      }
      return true;
    });
  }

  private removeMissing(map: Map<number, Anim>, alive: Set<number>): void {
    for (const [id, anim] of map) {
      if (!alive.has(id)) {
        this.dynamic.remove(anim.puppet.root);
        map.delete(id);
      }
    }
  }
}
