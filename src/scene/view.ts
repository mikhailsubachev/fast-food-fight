import * as THREE from 'three';
import type { Game, GameEvent } from '../core/game';
import type { LevelData } from '../data/level1';
import { DEFENDERS, MOUTH_LIVES, type DefenderType } from '../data/units';
import { buildBoard, type Board } from './board';
import { makeAttacker, makeDefender, makeMouth, makeProjectile, type MouthView, type Puppet } from './meshes';
import type { Stage } from './stage';

interface Anim {
  puppet: Puppet;
  attackT: number;
  hitT: number;
}

interface Effect {
  obj: THREE.Object3D;
  age: number;
  life: number;
  step: (e: Effect, k: number, dt: number) => void;
}

const FROZEN = new THREE.Color(0x9fd8ff);
const LIPS_OK = new THREE.Color(0xd9434e);
const LIPS_SICK = new THREE.Color(0x7fc23a);
const puffGeo = new THREE.SphereGeometry(0.3, 12, 8);
const dotGeo = new THREE.SphereGeometry(0.07, 8, 6);

/** Převádí stav hry na 3D scénu a hraje jednoduché animace šedého prototypu. */
export class View {
  readonly board: Board;
  private readonly dynamic = new THREE.Group();
  private readonly defenders = new Map<number, Anim>();
  private readonly attackers = new Map<number, Anim>();
  private readonly projectiles = new Map<number, THREE.Object3D>();
  private effects: Effect[] = [];
  private readonly mouth: MouthView;
  private mouthPulse = 1;
  private mouthMood: 'play' | 'won' | 'lost' = 'play';
  private readonly ring: THREE.Group;
  private readonly ringFill: THREE.MeshBasicMaterial;
  private readonly ringEdge: THREE.MeshBasicMaterial;
  private readonly spot: THREE.Group;

  constructor(
    stage: Stage,
    private readonly level: LevelData,
  ) {
    this.board = buildBoard(level);
    stage.scene.add(this.board.root, this.dynamic);

    this.mouth = makeMouth();
    this.mouth.root.position.set(level.mouth.x, 0, level.mouth.z);
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

  handleEvents(events: GameEvent[]): void {
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
          this.burst(e.x, 0.5, e.z, 0xd8312b, 5);
          break;
        }
        case 'flee':
          this.burst(e.x, 0.6, e.z, 0x4fb3ff, 6);
          break;
        case 'escaped':
          this.puff(e.x, e.z, 0xffffff, 1.4);
          break;
        case 'miss':
          this.puff(e.x, e.z, 0xc9b38a, 0.7);
          break;
        case 'frozen': {
          const d = this.defenders.get(e.defenderId);
          if (d) this.puff(d.puppet.root.position.x, d.puppet.root.position.z, 0x9fd8ff, 0.9);
          break;
        }
        case 'planted':
        case 'upgraded':
          break;
        case 'bite':
          this.mouthPulse = 1.35;
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
    this.syncProjectiles(game);
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
        anim = { puppet, attackT: 99, hitT: 99 };
        this.defenders.set(d.id, anim);
      }
      const { body, star, mats, base } = anim.puppet;
      anim.attackT += dt;

      const grow = d.growLeft > 0 ? 0.15 + 0.85 * (1 - d.growLeft / DEFENDERS[d.type].growTime) : 1;
      const bob = d.growLeft > 0 ? 0 : Math.sin(time * 3 + d.id) * 0.03;
      body.scale.set(grow, grow, grow);
      body.position.set(0, bob, 0);
      body.rotation.set(0, 0, 0);

      if (d.frozenLeft > 0) {
        body.position.x = Math.sin(time * 60) * 0.03;
      } else if (anim.attackT < 0.3) {
        const k = Math.sin((anim.attackT / 0.3) * Math.PI);
        if (d.type === 'mrkev') body.rotation.z = -k * 0.7;
        else body.scale.y = grow * (1 - k * 0.15);
      }
      mats.forEach((m, i) => (d.frozenLeft > 0 ? m.color.copy(base[i]).lerp(FROZEN, 0.65) : m.color.copy(base[i])));
      if (star) {
        star.visible = d.level >= 2;
        star.rotation.y = time * 2;
      }
    }
    this.removeMissing(this.defenders, alive);
  }

  private syncAttackers(game: Game, dt: number, time: number): void {
    const alive = new Set<number>();
    for (const a of game.attackers) {
      alive.add(a.id);
      let anim = this.attackers.get(a.id);
      if (!anim) {
        const puppet = makeAttacker(a.type);
        this.dynamic.add(puppet.root);
        anim = { puppet, attackT: 99, hitT: 99 };
        this.attackers.set(a.id, anim);
      }
      anim.hitT += dt;
      const p = game.path.at(a.d);
      const { root, body, mats, base } = anim.puppet;
      root.position.set(p.x, 0, p.z);
      root.rotation.y = Math.atan2(p.dirX, p.dirZ) + (a.fleeing ? Math.PI : 0);

      const pace = a.fleeing ? 18 : 10;
      body.position.y = Math.abs(Math.sin(time * pace + a.id)) * (a.fleeing ? 0.15 : 0.08);
      body.rotation.z = Math.sin(time * pace + a.id) * 0.1;
      const squash = anim.hitT < 0.25 ? Math.sin((anim.hitT / 0.25) * Math.PI) * 0.3 : 0;
      body.scale.set(1 + squash * 0.5, 1 - squash, 1 + squash * 0.5);
      // Utíkající fast food zbledne strachy.
      mats.forEach((m, i) => (a.fleeing ? m.color.copy(base[i]).lerp(new THREE.Color(0xffffff), 0.35) : m.color.copy(base[i])));
    }
    this.removeMissing(this.attackers, alive);
  }

  private syncProjectiles(game: Game): void {
    const alive = new Set<number>();
    for (const p of game.projectiles) {
      alive.add(p.id);
      let obj = this.projectiles.get(p.id);
      if (!obj) {
        obj = makeProjectile(p.kind);
        this.dynamic.add(obj);
        this.projectiles.set(p.id, obj);
      }
      const k = Math.min(1, p.t / p.duration);
      const arc = Math.sin(k * Math.PI) * (p.kind === 'porek' ? 0.9 : 0.7);
      obj.position.set(p.x0 + (p.tx - p.x0) * k, 0.6 + arc, p.z0 + (p.tz - p.z0) * k);
      obj.rotation.y = -Math.atan2(p.tz - p.z0, p.tx - p.x0);
      if (p.kind === 'hranolka') obj.rotation.x += 0.4;
    }
    for (const [id, obj] of this.projectiles) {
      if (!alive.has(id)) {
        this.dynamic.remove(obj);
        this.projectiles.delete(id);
      }
    }
  }

  private updateMouth(game: Game, dt: number, time: number): void {
    const m = this.mouth;
    const sick = Math.min(1, game.bites / MOUTH_LIVES);
    m.lips.color.copy(LIPS_OK).lerp(LIPS_SICK, sick);
    m.teeth.forEach((t, i) => (t.visible = i < MOUTH_LIVES - game.bites));

    this.mouthPulse += (1 - this.mouthPulse) * Math.min(1, dt * 6);
    let s = this.mouthPulse;
    if (this.mouthMood === 'won') s *= 1 + Math.abs(Math.sin(time * 6)) * 0.12;
    if (this.mouthMood === 'lost') {
      s *= 1 + Math.sin(time * 20) * 0.04;
      if (Math.random() < dt * 40) this.vomitDrop();
    } else {
      // nervózní pohled, když je fast food blízko
      const near = game.attackers.some((a) => !a.fleeing && game.path.length - a.d < 3);
      m.root.position.x = this.level.mouth.x + (near ? Math.sin(time * 30) * 0.03 : 0);
    }
    m.root.scale.setScalar(s);
  }

  // --- efekty ---

  private puff(x: number, z: number, color: number, size: number): void {
    const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.8, depthWrite: false });
    const mesh = new THREE.Mesh(puffGeo, mat);
    mesh.position.set(x, 0.4, z);
    this.addEffect(mesh, 0.45, (e, k) => {
      e.obj.scale.setScalar(size * (0.4 + k));
      mat.opacity = 0.8 * (1 - k);
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
    mesh.position.set(this.level.mouth.x - 0.4, 0.9, this.level.mouth.z + 0.2);
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
