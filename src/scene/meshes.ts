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

function texture(name: string, mirrored = false): THREE.Texture {
  const key = mirrored ? `${name}|zrcadlo` : name;
  let t = textures.get(key);
  if (!t) {
    if (mirrored) {
      // Zrcadlový obrázek: stejná kresba, jen čtená zprava doleva. (Sprite záporné měřítko
      // neumí, proto se postava otáčí takhle.)
      t = texture(name).clone();
      t.repeat.x = -1;
      t.offset.x = 1;
    } else {
      t = loader.load(`${import.meta.env.BASE_URL}assets/postavy/${name}.svg`);
      t.colorSpace = THREE.SRGBColorSpace;
      t.anisotropy = 4;
    }
    textures.set(key, t);
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
  'cibule-klid', 'cibule-mrk', 'cibule-nalez', 'cibule-smrad', 'cibule-ztuhla', 'cibule-radost',
  'cibule2-klid', 'cibule2-mrk', 'cibule2-nalez', 'cibule2-smrad', 'cibule2-radost',
  'mrkev-lepkava', 'mrkev-lepkava2', 'porek-lepkavy', 'porek-lepkavy2', 'cibule-lepkava', 'cibule-lepkava2',
  'lizatko-krok1', 'lizatko-krok2', 'lizatko-naprah', 'lizatko-toci', 'lizatko-zasah', 'lizatko-utek1', 'lizatko-utek2',
  'brokolice-klid', 'brokolice-mrk', 'brokolice-mir', 'brokolice-hod', 'brokolice-ztuhla', 'brokolice-radost',
  'brokolice2-klid', 'brokolice2-mrk', 'brokolice2-mir', 'brokolice2-hod', 'brokolice2-radost',
  'brokolice-lepkava', 'brokolice-lepkava2',
  'kecup-krok1', 'kecup-krok2', 'kecup-nastvani', 'kecup-prsk', 'kecup-zasah', 'kecup-utek1', 'kecup-utek2',
  'pusa', 'porkosip', 'hranolka', 'oblak', 'raketa', 'destnik', 'louze',
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
  /** Postava otočená doleva (zrcadlově); nakreslené jsou čelem doprava. */
  mirrored: boolean;
  setFrame(name: string): void;
  setMirrored(mirrored: boolean): void;
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
    mirrored: false,
    setFrame(name: string) {
      if (p.frame === name) return;
      p.frame = name;
      mat.map = texture(name, p.mirrored);
    },
    setMirrored(mirrored: boolean) {
      if (p.mirrored === mirrored) return;
      p.mirrored = mirrored;
      mat.map = texture(p.frame, mirrored);
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

/**
 * Výška obrázku (celého rámečku 450 px) ve světě, podle návrhu úrovně:
 * měřítko postavy v návrhu × 450 px / 120 px na políčko. Postava sama je asi o pětinu menší.
 */
// Zelenina podle návrhu D (menší, aby se vešla do políčka mřížky): 0,415 a 0,419 × 450 / 120.
// Cibule má v návrhu 2. úrovně stejné měřítko jako mrkev, lízátko jako hamburger.
// Brokolice má v návrhu 3. úrovně měřítko mrkve, kečup hamburgeru.
const DEFENDER_HEIGHT: Record<DefenderType, number> = { mrkev: 1.56, porek: 1.57, cibule: 1.56, brokolice: 1.56 };
const ATTACKER_HEIGHT: Record<AttackerFrames, number> = { hamburger: 1.73, hranolky: 1.58, lizatko: 1.73, kecup: 1.73 };

type AttackerFrames = 'hamburger' | 'hranolky' | 'lizatko' | 'kecup';

/** Jméno obrázků útočníka (velký hamburger je zvětšený hamburger). */
export function attackerFrames(type: AttackerType): AttackerFrames {
  return type === 'velkyHamburger' ? 'hamburger' : type;
}

export function makeDefender(type: DefenderType): Puppet {
  // Pod zeleninou je hnědé políčko (šestihran), takže hromádka hlíny není potřeba.
  const p = puppet(`${type}-mrk`, DEFENDER_HEIGHT[type]);
  return p;
}

export function makeAttacker(type: AttackerType): Puppet {
  const base = attackerFrames(type);
  const p = puppet(`${base}-krok1`, ATTACKER_HEIGHT[base]);
  blobShadow(p, 0.36);
  if (type === 'velkyHamburger') p.root.scale.setScalar(1.5);
  return p;
}

export function makeMouth(): Puppet {
  return puppet('pusa', 2.9);
}

/** Oblak smradu cibule: leží na zemi kolem cibule (průměr 2r) a pomalu se rozplyne. */
export function makeCloud(r: number): THREE.Mesh {
  const mat = new THREE.MeshBasicMaterial({ map: texture('oblak'), transparent: true, opacity: 0.6, depthWrite: false });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(2 * r * 1.08, 2 * r * 1.08 * (132 / 224)), mat);
  m.rotation.x = -Math.PI / 2;
  m.renderOrder = 2;
  return m;
}

/** Střela: pórkošíp a brokolicová raketa (letí hrotem napřed) nebo hranolka (točí se). */
export function makeProjectile(kind: 'porek' | 'hranolka' | 'brokolice'): THREE.Sprite {
  const mat = new THREE.SpriteMaterial({
    map: texture(kind === 'porek' ? 'porkosip' : kind === 'brokolice' ? 'raketa' : 'hranolka'),
    alphaTest: 0.3,
    depthWrite: true,
  });
  const s = new THREE.Sprite(mat);
  if (kind === 'porek') s.scale.set(0.5, 0.21, 1);
  else if (kind === 'brokolice') s.scale.set(0.85, 0.5, 1);
  else s.scale.set(0.11, 0.46, 1);
  return s;
}

/** Deštník z rozprsknuté růžičky brokolice nad cílem (stojí ke kameře, `r` je poloměr zásahu). */
export function makeUmbrella(r: number): THREE.Sprite {
  const mat = new THREE.SpriteMaterial({ map: texture('destnik'), transparent: true, depthWrite: false });
  const s = new THREE.Sprite(mat);
  // Obrázek 220 × 220, žebra deštníku sahají ±92 px do stran.
  const size = (2 * r * 220) / 184;
  s.scale.set(size, size, 1);
  s.renderOrder = 3;
  return s;
}

/** Kus kečupové louže ležící na cestě. */
export function makePuddlePiece(): THREE.Mesh {
  const mat = new THREE.MeshBasicMaterial({ map: texture('louze'), transparent: true, depthWrite: false });
  // Obrázek 184 × 68 je kreslený už šikmo; na zemi se natáhne, aby na obrazovce vypadal stejně.
  const w = 1.15;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, ((w * 68) / 184) / 0.9), mat);
  m.rotation.x = -Math.PI / 2;
  m.renderOrder = 2;
  return m;
}
