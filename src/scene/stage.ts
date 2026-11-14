import * as THREE from 'three';
import type { LevelData } from '../data/level1';
import type { Vec2 } from '../core/types';

/**
 * Pevný šikmý pohled shora a z boku, bez otáčení, zoomu a posouvání.
 * Širší úhel záběru (FOV) a kamera blíž k záhonu dávají silnější perspektivu:
 * postavy vzadu (na začátku cesty) jsou menší a cestou k puse rostou.
 */
const CAMERA_TILT = THREE.MathUtils.degToRad(50);
const CAMERA_FOV = 60;
/** Místo nahoře pro horní lištu (v CSS pixelech), než se dá změřit skutečná lišta. */
const HUD_HEIGHT = 72;

/** Výška horní lišty; na úzkém displeji má dva řádky. */
function hudHeight(): number {
  const hud = document.querySelector<HTMLElement>('.hud');
  return hud ? hud.getBoundingClientRect().bottom : HUD_HEIGHT;
}
const MARGIN = 0.03;
/** Výška postav, aby se do obrazovky vešly i hlavy postav u horního okraje. */
const FIGURE_HEIGHT = 1.8;

export class Stage {
  readonly renderer: THREE.WebGLRenderer;
  readonly scene = new THREE.Scene();
  readonly camera = new THREE.PerspectiveCamera(CAMERA_FOV, 1, 0.1, 500);
  width = 1;
  height = 1;

  private readonly target: THREE.Vector3;
  private readonly corners: THREE.Vector3[] = [];
  private readonly raycaster = new THREE.Raycaster();
  private readonly ground = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
  private readonly tmp = new THREE.Vector3();

  constructor(container: HTMLElement, level: LevelData) {
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.domElement.className = 'stage';
    container.appendChild(this.renderer.domElement);

    this.scene.background = new THREE.Color(0x8bb85a);
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0xb59b7a, 1.4));
    const sun = new THREE.DirectionalLight(0xffffff, 1.8);
    sun.position.set(-4, 10, 6);
    this.scene.add(sun);

    const v = level.view;
    this.target = new THREE.Vector3((v.minX + v.maxX) / 2, 0, (v.minZ + v.maxZ) / 2);
    // Vzadu musí být vidět i hlavy postav, vepředu stačí zem.
    for (const x of [v.minX, v.maxX]) {
      this.corners.push(new THREE.Vector3(x, FIGURE_HEIGHT, v.minZ), new THREE.Vector3(x, 0, v.maxZ));
    }

    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  /** Najde vzdálenost kamery, při které se celá mapa vejde pod horní lištu, a mapu vycentruje. */
  resize(): void {
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.width = w;
    this.height = h;
    this.renderer.setSize(w, h);
    this.camera.aspect = w / h;
    this.camera.clearViewOffset();
    this.camera.updateProjectionMatrix();

    const top = Math.min(0.5, (2 * hudHeight()) / h);
    const availW = 2 - 2 * MARGIN;
    const availH = 2 - 2 * MARGIN - top;
    let lo = 2;
    let hi = 400;
    for (let i = 0; i < 40; i++) {
      const mid = (lo + hi) / 2;
      this.placeCamera(mid);
      const box = this.ndcBox();
      if (box.maxX - box.minX <= availW && box.maxY - box.minY <= availH) hi = mid;
      else lo = mid;
    }
    this.placeCamera(hi);
    const box = this.ndcBox();
    const dx = -(box.minX + box.maxX) / 2;
    const dy = -top / 2 - (box.minY + box.maxY) / 2;
    this.camera.setViewOffset(w, h, (-dx * w) / 2, (dy * h) / 2, w, h);
  }

  private placeCamera(dist: number): void {
    this.camera.position.set(
      this.target.x,
      this.target.y + Math.sin(CAMERA_TILT) * dist,
      this.target.z + Math.cos(CAMERA_TILT) * dist,
    );
    this.camera.lookAt(this.target);
    this.camera.updateMatrixWorld();
  }

  private ndcBox() {
    const box = { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity };
    for (const c of this.corners) {
      const p = this.tmp.copy(c).project(this.camera);
      box.minX = Math.min(box.minX, p.x);
      box.maxX = Math.max(box.maxX, p.x);
      box.minY = Math.min(box.minY, p.y);
      box.maxY = Math.max(box.maxY, p.y);
    }
    return box;
  }

  /** Bod ve světě → pixely na obrazovce. */
  toScreen(x: number, y: number, z: number): { x: number; y: number } {
    const p = this.tmp.set(x, y, z).project(this.camera);
    return { x: ((p.x + 1) / 2) * this.width, y: ((1 - p.y) / 2) * this.height };
  }

  /** Pixely na obrazovce → bod na zemi (nebo null mimo zem). */
  groundAt(clientX: number, clientY: number): Vec2 | null {
    const ndc = new THREE.Vector2((clientX / this.width) * 2 - 1, -(clientY / this.height) * 2 + 1);
    this.raycaster.setFromCamera(ndc, this.camera);
    const hit = this.raycaster.ray.intersectPlane(this.ground, this.tmp);
    return hit ? { x: hit.x, z: hit.z } : null;
  }

  render(): void {
    this.renderer.render(this.scene, this.camera);
  }
}
