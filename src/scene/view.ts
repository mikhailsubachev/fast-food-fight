import * as THREE from 'three';
import type { Game, GameEvent } from '../core/game';
import type { LevelData } from '../data/level1';
import { DEFENDERS, MOUTH_LIVES, type DefenderType } from '../data/units';
import { defenderLevel } from '../entities/obranci/defender';
import { buildBoard, type Board } from './board';
import { makeAttacker, makeDefender, makeMouth, makeProjectile, preloadFrames, type Puppet } from './meshes';
import type { Stage } from './stage';

interface Anim {
  puppet: Puppet;
  /** Sekundy od posledního útoku / zásahu / hodu / radosti. */
  attackT: number;
  hitT: number;
  throwT: number;
  joyT: number;
  /** Kdy příště mrknout. */
  blinkAt: number;
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
  return { puppet, attackT: 99, hitT: 99, throwT: 99, joyT: 99, blinkAt: 1 + Math.random() * 3 };
}

/** Převádí stav hry na 3D scénu: papírové loutky, střely a efekty. */
export class View {
  readonly board: Board;
  private readonly dynamic = new THREE.Group();
  private readonly defenders = new Map<number, Anim>();
  private readonly attackers = new Map<number, Anim>();
  private readonly projectiles = new Map<number, THREE.Sprite>();
  private effects: Effect[] = [];
  private readonly mouth: Puppet;
  private mouthPulse = 1;
  private mouthMood: 'play' | 'won' | 'lost' = 'play';
  private readonly ring: THREE.Group;
  private readonly ringFill: THREE.MeshBasicMaterial;
  private readonly ringEdge: THREE.MeshBasicMaterial;
  private readonly spot: THREE.Group;
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

    // Místo, kam se chystá sázet: bílý kruh se zeleným okrajem.
    this.spot = new THREE.Group();
    const spotFill = new THREE.Mesh(
      new THREE.CircleGeometry(0.42, 32),
      new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.55, depthWrite: false }),
    );
    const spotEdge = new THREE.Mesh(new THREE.RingGeometry(0.4, 0.46, 32), new THREE.MeshBasicMaterial({ color: 0x3fa34d }));
    this.spot.add(spotFill, spotEdge);
    this.spot.rotation.x = -Math.PI / 2;
    this.spot.visible = false;
    stage.scene.add(this.spot);
  }

  /** Dosah zeleniny: mrkev oranžově, pórek modře (barvy z návrhu). */
  showRange(x: number, z: number, r: number, type: DefenderType): void {
    const color = type === 'mrkev' ? 0xf08a24 : 0x2d8cd6;
    this.ringFill.color.setHex(color);
    this.ringEdge.color.setHex(color);
    this.ring.position.set(x, 0.06, z);
    this.ring.scale.setScalar(r);
    this.ring.visible = true;
  }

  hideRange(): void {
    this.ring.visible = false;
  }

  showSpot(x: number, z: number): void {
    this.spot.position.set(x, 0.05, z);
    this.spot.visible = true;
  }

  hideSpot(): void {
    this.spot.visible = false;
  }

  reset(): void {
    this.dynamic.clear();
    this.defenders.clear();
    this.attackers.clear();
    this.projectiles.clear();
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
          if (a) a.attackT = 0;
          break;
        }
        case 'hit': {
          const a = this.attackers.get(e.attackerId);
          if (a) a.hitT = 0;
          this.burst(e.x, 0.6, e.z, 0xd8312b, 5);
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
    this.updateMouth(game, dt, time);
    this.updateEffects(dt);
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
        this.defenders.set(d.id, anim);
      }
      anim.attackT += dt;
      anim.joyT += dt;
      const { sprite, width, height } = anim.puppet;
      const prefix = d.level >= 2 ? `${d.type}2` : d.type;

      // Vyrůstání: loutka vyleze ze záhonu se zavřenýma očima.
      if (d.growLeft > 0) {
        const k = 1 - d.growLeft / DEFENDERS[d.type].growTime;
        sprite.scale.set(width * (0.6 + 0.4 * k), height * Math.max(0.05, k), 1);
        sprite.position.set(0, 0, 0);
        anim.puppet.setFrame(`${d.type}-mrk`);
        continue;
      }

      let frame = `${prefix}-klid`;
      let squash = Math.sin(time * 3 + d.id) * 0.02;
      let jitter = 0;
      let hop = 0;
      if (d.frozenLeft > 0) {
        frame = d.type === 'mrkev' ? 'mrkev-ztuhla' : 'porek-ztuhl';
        jitter = Math.sin(time * 60) * 0.04;
        squash = 0;
      } else if (anim.attackT < 0.3) {
        frame = d.type === 'mrkev' ? `${prefix}-sek` : `${prefix}-vystrel`;
        squash = -Math.sin((anim.attackT / 0.3) * Math.PI) * 0.08;
      } else if (anim.joyT < 0.7) {
        frame = `${prefix}-radost`;
        hop = Math.abs(Math.sin((anim.joyT / 0.7) * Math.PI * 2)) * 0.25;
      } else if (d.type === 'porek' && this.hasTarget(game, d.x, d.z, defenderLevel(d).range)) {
        frame = `${prefix}-miri`;
      } else {
        // Mrkání: čas od času na chvilku zavře oči.
        if (time > anim.blinkAt + 0.15) anim.blinkAt = time + 2 + Math.random() * 3;
        if (time > anim.blinkAt) frame = `${prefix}-mrk`;
      }
      anim.puppet.setFrame(frame);
      sprite.scale.set(width * (1 - squash * 0.5), height * (1 + squash), 1);
      sprite.position.set(jitter, hop, 0);
    }
    this.removeMissing(this.defenders, alive);
  }

  private hasTarget(game: Game, x: number, z: number, range: number): boolean {
    return game.attackers.some((a) => {
      if (a.fleeing) return false;
      const p = game.path.at(a.d);
      return Math.hypot(p.x - x, p.z - z) <= range;
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
      }
      anim.hitT += dt;
      anim.throwT += dt;
      const p = game.path.at(a.d);
      const { root, sprite, width, height } = anim.puppet;
      root.position.set(p.x, 0, p.z);

      const base = a.type === 'hranolky' ? 'hranolky' : 'hamburger';
      const step = Math.floor(time * (a.fleeing ? 7 : 4) + a.id) % 2 === 0;
      let frame = `${base}-krok${step ? 1 : 2}`;
      let squash = 0;
      if (a.fleeing) frame = `${base}-utek${step ? 1 : 2}`;
      else if (anim.hitT < 0.25) {
        frame = `${base}-zasah`;
        squash = Math.sin((anim.hitT / 0.25) * Math.PI) * 0.15;
      } else if (base === 'hranolky' && anim.throwT < 0.15) frame = 'hranolky-naprah';
      else if (base === 'hranolky' && anim.throwT < 0.45) frame = 'hranolky-hod';
      anim.puppet.setFrame(frame);

      // Otočit loutku podle toho, kam jde na obrazovce (doleva / doprava).
      const dir = a.fleeing ? -1 : 1;
      const sx = this.screenDirX(p.x, p.z, p.dirX * dir, p.dirZ * dir);
      const flip = sx < -0.05 ? -1 : 1;
      const bounce = Math.abs(Math.sin(time * (a.fleeing ? 14 : 8) + a.id)) * (a.fleeing ? 0.14 : 0.07);
      sprite.scale.set(width * flip * (1 + squash * 0.6), height * (1 - squash), 1);
      sprite.position.set(0, bounce, 0);
    }
    this.removeMissing(this.attackers, alive);
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
      const at = (t: number) => ({
        x: p.x0 + (p.tx - p.x0) * t,
        y: 0.9 + Math.sin(t * Math.PI) * (p.kind === 'porek' ? 1.1 : 0.9),
        z: p.z0 + (p.tz - p.z0) * t,
      });
      const now = at(k);
      s.position.set(now.x, now.y, now.z);
      const mat = s.material as THREE.SpriteMaterial;
      if (p.kind === 'porek') {
        // Pórkošíp letí hrotem napřed po oblouku.
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

  private updateEffects(dt: number): void {
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
