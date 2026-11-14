// Postavy jako papírové loutky: obrázky z dětských kreseb (překreslené v návrhu,
// vyexportované skriptem tools/export_postavy.py) stojí ve 3D scéně natočené ke kameře.
import * as THREE from 'three';
import type { AttackerType, DefenderType } from '../data/units';

export function toon(color: number): THREE.MeshToonMaterial {
  return new THREE.MeshToonMaterial({ color });
}

// Rámeček obrázků z exportu: 330 × 450, chodidla na 165 / 388 od levého horního rohu.
const FRAME_W = 330;
const FRAME_H = 450;
const FEET_U = 165 / FRAME_W;
const FEET_V = (FRAME_H - 438) / FRAME_H;

const loader = new THREE.TextureLoader();
const textures = new Map<string, THREE.Texture>();

function texture(name: string): THREE.Texture {
  let t = textures.get(name);
  if (!t) {
    t = loader.load(`${import.meta.env.BASE_URL}assets/postavy/${name}.svg`);
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 4;
    textures.set(name, t);
  }
  return t;
}

export const FRAMES = [
  'mrkev-klid', 'mrkev-mrk', 'mrkev-sek', 'mrkev-ztuhla', 'mrkev-radost',
  'mrkev2-klid', 'mrkev2-mrk', 'mrkev2-sek', 'mrkev2-radost',
  'porek-klid', 'porek-mrk', 'porek-miri', 'porek-vystrel', 'porek-ztuhl', 'porek-radost',
  'porek2-klid', 'porek2-mrk', 'porek2-miri', 'porek2-vystrel', 'porek2-radost',
  'hamburger-krok1', 'hamburger-krok2', 'hamburger-zasah', 'hamburger-utek1', 'hamburger-utek2',
  'hranolky-krok1', 'hranolky-krok2', 'hranolky-naprah', 'hranolky-hod', 'hranolky-zasah',
  'hranolky-utek1', 'hranolky-utek2',
  'pusa', 'porkosip', 'hranolka',
] as const;

/** Načte všechny obrázky předem, aby postavy při prvním objevení neblikly. */
export function preloadFrames(): void {
  for (const f of FRAMES) texture(f);
}

export interface Puppet {
  root: THREE.Group;
  sprite: THREE.Sprite;
  /** Šířka a výška obrázku ve světě (políčkách). */
  width: number;
  height: number;
  frame: string;
  setFrame(name: string): void;
}

/** Loutka: obrázek natočený ke kameře, chodidla na zemi v bodě `root`. */
function puppet(firstFrame: string, worldHeight: number): Puppet {
  const root = new THREE.Group();
  const mat = new THREE.SpriteMaterial({ map: texture(firstFrame), alphaTest: 0.3, depthWrite: true });
  const sprite = new THREE.Sprite(mat);
  sprite.center.set(FEET_U, FEET_V);
  const height = worldHeight;
  const width = (worldHeight * FRAME_W) / FRAME_H;
  sprite.scale.set(width, height, 1);
  root.add(sprite);
  const p: Puppet = {
    root,
    sprite,
    width,
    height,
    frame: firstFrame,
    setFrame(name: string) {
      if (p.frame === name) return;
      p.frame = name;
      mat.map = texture(name);
    },
  };
  return p;
}

const shadowGeo = new THREE.CircleGeometry(1, 24);
const shadowMat = new THREE.MeshBasicMaterial({ color: 0x3a2210, transparent: true, opacity: 0.22, depthWrite: false });

function blobShadow(p: Puppet, r: number): void {
  const m = new THREE.Mesh(shadowGeo, shadowMat);
  m.rotation.x = -Math.PI / 2;
  m.position.y = 0.03;
  m.scale.set(r, r * 0.45, 1);
  p.root.add(m);
}

const moundEdge = new THREE.MeshBasicMaterial({ color: 0x2b2118 });
const moundSoil = new THREE.MeshBasicMaterial({ color: 0x6b4a2e });

/** Hromádka hlíny pod zasazenou zeleninou (jako v návrhu úrovně). */
function mound(p: Puppet, r: number): void {
  for (const [mat, s, y] of [
    [moundEdge, 1.1, 0.03],
    [moundSoil, 1, 0.035],
  ] as const) {
    const m = new THREE.Mesh(shadowGeo, mat);
    m.rotation.x = -Math.PI / 2;
    m.position.y = y;
    m.scale.set(r * s, r * 0.75 * s, 1);
    p.root.add(m);
  }
}

/**
 * Výška obrázku (celého rámečku 450 px) ve světě, podle návrhu úrovně:
 * měřítko postavy v návrhu × 450 px / 120 px na políčko. Postava sama je asi o pětinu menší.
 */
const DEFENDER_HEIGHT: Record<DefenderType, number> = { mrkev: 1.8, porek: 1.94 };
const ATTACKER_HEIGHT: Record<'hamburger' | 'hranolky', number> = { hamburger: 1.73, hranolky: 1.58 };

export function makeDefender(type: DefenderType): Puppet {
  const p = puppet(`${type}-mrk`, DEFENDER_HEIGHT[type]);
  mound(p, 0.36);
  return p;
}

export function makeAttacker(type: AttackerType): Puppet {
  const base = type === 'hranolky' ? 'hranolky' : 'hamburger';
  const p = puppet(`${base}-krok1`, ATTACKER_HEIGHT[base]);
  blobShadow(p, 0.36);
  if (type === 'velkyHamburger') p.root.scale.setScalar(1.5);
  return p;
}

export function makeMouth(): Puppet {
  return puppet('pusa', 2.9);
}

/** Střela: pórkošíp (letí hrotem napřed) nebo hranolka (točí se). */
export function makeProjectile(kind: 'porek' | 'hranolka'): THREE.Sprite {
  const mat = new THREE.SpriteMaterial({
    map: texture(kind === 'porek' ? 'porkosip' : 'hranolka'),
    alphaTest: 0.3,
    depthWrite: true,
  });
  const s = new THREE.Sprite(mat);
  if (kind === 'porek') s.scale.set(0.5, 0.21, 1);
  else s.scale.set(0.11, 0.46, 1);
  return s;
}
