import * as THREE from 'three';
import type { LevelData } from '../data/level1';
import type { Vec2 } from '../core/types';

/**
 * Pevný šikmý pohled shora a z boku, bez otáčení, zoomu a posouvání. Podle návrhu úrovně
 * (plátno „Úroveň 1 – Snídaňová cesta“) je pohled pravoúhlý, bez perspektivy: postavy mají
 * všude na záhonu stejnou velikost a kruh dosahu je elipsa s poměrem stran 0,9, tedy
 * sklon kamery asi 64° od vodorovné roviny.
 */
const CAMERA_TILT = Math.asin(0.9);
const CAMERA_DISTANCE = 60;
/** Místo nahoře pro horní lištu (v CSS pixelech), než se dá změřit skutečná lišta. */
const HUD_HEIGHT = 72;

/** Displej nižší než tohle (v CSS pixelech) šetří místem nahoře a dole. */
const LOW_SCREEN = 500;
/** O kolik políček se na nízkém displeji ořízne výřez nahoře a dole. */
const LOW_TRIM = 0.3;

/** Spodní okraj horní lišty v pixelech. */
function hudHeight(): number {
  const hud = document.querySelector<HTMLElement>('.hud');
  return hud ? hud.getBoundingClientRect().bottom : HUD_HEIGHT;
}

export class Stage {
  readonly renderer: THREE.WebGLRenderer;
  readonly scene = new THREE.Scene();
  readonly camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 500);
  width = 1;
  height = 1;

  /** Rohy výřezu, který musí být vždy celý vidět, v souřadnicích kamery. */
  private readonly viewBox: { minX: number; maxX: number; minY: number; maxY: number };
  /** Výřez oříznutý nahoře a dole pro nízké displeje. */
  private readonly tightBox: { minX: number; maxX: number; minY: number; maxY: number };
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
    const target = new THREE.Vector3((v.minX + v.maxX) / 2, 0, (v.minZ + v.maxZ) / 2);
    this.camera.position.set(
      target.x,
      Math.sin(CAMERA_TILT) * CAMERA_DISTANCE,
      target.z + Math.cos(CAMERA_TILT) * CAMERA_DISTANCE,
    );
    this.camera.lookAt(target);
    this.camera.updateMatrixWorld();

    // Pravoúhlý pohled: poloha bodu na obrazovce nezávisí na vzdálenosti kamery,
    // takže rohy výřezu stačí jednou převést do souřadnic kamery.
    const box = { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity };
    for (const x of [v.minX, v.maxX]) {
      for (const z of [v.minZ, v.maxZ]) {
        const p = new THREE.Vector3(x, 0, z).applyMatrix4(this.camera.matrixWorldInverse);
        box.minX = Math.min(box.minX, p.x);
        box.maxX = Math.max(box.maxX, p.x);
        box.minY = Math.min(box.minY, p.y);
        box.maxY = Math.max(box.maxY, p.y);
      }
    }
    this.viewBox = box;
    const trim = LOW_TRIM * Math.sin(CAMERA_TILT);
    this.tightBox = { ...box, minY: box.minY + trim, maxY: box.maxY - trim };

    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  /**
   * Celý výřez se vejde pod horní lištu, co největší a vycentrovaný. Na nízkých displejích
   * (telefon naležato s lištou prohlížeče) by tak zbylo hodně místa po stranách, proto se tam
   * výřez nahoře a dole trochu ořízne (krajní pruhy louky bez cesty) a lišta smí zasahovat do
   * horního pruhu, kde nejsou políčka.
   */
  resize(): void {
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.width = w;
    this.height = h;
    this.renderer.setSize(w, h);

    const low = h < LOW_SCREEN;
    const hud = Math.min(hudHeight(), h * 0.3) * (low ? 0.55 : 1);
    const b = low ? this.tightBox : this.viewBox;
    const scale = Math.min(w / (b.maxX - b.minX), (h - hud) / (b.maxY - b.minY));
    const cx = (b.minX + b.maxX) / 2;
    // Střed výřezu patří doprostřed místa pod lištou, tedy o polovinu lišty níž než střed obrazovky.
    const cy = (b.minY + b.maxY) / 2 + hud / 2 / scale;
    const halfW = w / 2 / scale;
    const halfH = h / 2 / scale;
    this.camera.left = cx - halfW;
    this.camera.right = cx + halfW;
    this.camera.top = cy + halfH;
    this.camera.bottom = cy - halfH;
    this.camera.updateProjectionMatrix();
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
