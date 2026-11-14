// Šedý prototyp: postavy z jednoduchých tvarů. Později je nahradí papírové loutky z dětských kreseb.
import * as THREE from 'three';
import type { AttackerType, DefenderType } from '../data/units';

export interface Puppet {
  root: THREE.Group;
  /** Část, která se hýbe (pohupování, zmáčknutí, máchnutí). */
  body: THREE.Group;
  mats: THREE.MeshToonMaterial[];
  base: THREE.Color[];
  star?: THREE.Object3D;
}

export function toon(color: number): THREE.MeshToonMaterial {
  return new THREE.MeshToonMaterial({ color });
}

function newPuppet(): Puppet {
  const root = new THREE.Group();
  const body = new THREE.Group();
  root.add(body);
  return { root, body, mats: [], base: [] };
}

function part(
  p: Puppet,
  geo: THREE.BufferGeometry,
  color: number,
  pos: [number, number, number],
  rot: [number, number, number] = [0, 0, 0],
): THREE.Mesh {
  const mat = toon(color);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(...pos);
  mesh.rotation.set(...rot);
  p.body.add(mesh);
  p.mats.push(mat);
  p.base.push(mat.color.clone());
  return mesh;
}

const shadowGeo = new THREE.CircleGeometry(1, 24);
const shadowMat = new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.2, depthWrite: false });

function blobShadow(p: Puppet, r: number): void {
  const m = new THREE.Mesh(shadowGeo, shadowMat);
  m.rotation.x = -Math.PI / 2;
  m.position.y = 0.02;
  m.scale.setScalar(r);
  p.root.add(m);
}

const eyeGeo = new THREE.SphereGeometry(0.08, 10, 8);
const pupilGeo = new THREE.SphereGeometry(0.045, 8, 6);

/** Oči na přední straně (+z), aby bylo vidět, kam postava kouká. */
function eyes(p: Puppet, y: number, z: number, spread = 0.12): void {
  for (const sx of [-1, 1]) {
    part(p, eyeGeo, 0xffffff, [sx * spread, y, z]);
    part(p, pupilGeo, 0x222222, [sx * spread, y, z + 0.06]);
  }
}

const moundGeo = new THREE.CircleGeometry(1, 24);
const moundEdge = new THREE.MeshBasicMaterial({ color: 0x2b2118 });
const moundSoil = new THREE.MeshBasicMaterial({ color: 0x6b4a2e });

/** Hromádka hlíny pod zasazenou zeleninou (jako v návrhu úrovně). */
function mound(p: Puppet, r: number): void {
  for (const [mat, s, y] of [
    [moundEdge, 1.1, 0.03],
    [moundSoil, 1, 0.035],
  ] as const) {
    const m = new THREE.Mesh(moundGeo, mat);
    m.rotation.x = -Math.PI / 2;
    m.position.y = y;
    m.scale.set(r * s, r * 0.8 * s, 1);
    p.root.add(m);
  }
}

export function makeDefender(type: DefenderType): Puppet {
  const p = newPuppet();
  mound(p, 0.4);
  if (type === 'mrkev') {
    part(p, new THREE.ConeGeometry(0.3, 0.95, 12), 0xf28c28, [0, 0.48, 0], [Math.PI, 0, 0]);
    part(p, new THREE.ConeGeometry(0.1, 0.4, 6), 0x3fa34d, [-0.08, 1.12, 0], [0, 0, 0.3]);
    part(p, new THREE.ConeGeometry(0.1, 0.4, 6), 0x3fa34d, [0.08, 1.12, 0], [0, 0, -0.3]);
    // mrkvomeč
    part(p, new THREE.BoxGeometry(0.08, 0.6, 0.06), 0xffb35c, [0.38, 0.62, 0.05], [0, 0, -0.25]);
    eyes(p, 0.7, 0.22, 0.1);
  } else {
    part(p, new THREE.CylinderGeometry(0.17, 0.21, 1.0, 12), 0xeef5d6, [0, 0.5, 0]);
    part(p, new THREE.CylinderGeometry(0.04, 0.16, 0.65, 8), 0x4caf50, [-0.1, 1.25, 0], [0, 0, 0.35]);
    part(p, new THREE.CylinderGeometry(0.04, 0.16, 0.65, 8), 0x2e8b3e, [0.1, 1.25, 0], [0, 0, -0.35]);
    // luk
    part(p, new THREE.TorusGeometry(0.28, 0.035, 6, 14, Math.PI), 0x8d6e3f, [0.32, 0.6, 0.05], [0, 0, -Math.PI / 2]);
    eyes(p, 0.72, 0.19, 0.09);
  }
  const star = new THREE.Mesh(new THREE.OctahedronGeometry(0.16), toon(0xffd23f));
  star.position.y = 1.65;
  star.visible = false;
  p.root.add(star);
  p.star = star;
  return p;
}

export function makeAttacker(type: AttackerType): Puppet {
  const p = newPuppet();
  if (type === 'hranolky') {
    blobShadow(p, 0.4);
    part(p, new THREE.BoxGeometry(0.56, 0.5, 0.42), 0xd8312b, [0, 0.3, 0]);
    for (let i = 0; i < 5; i++) {
      const x = -0.2 + i * 0.1;
      part(p, new THREE.BoxGeometry(0.07, 0.45, 0.07), 0xffd23f, [x, 0.7 + (i % 2) * 0.06, (i % 2) * 0.08 - 0.04], [0, 0, (i - 2) * 0.08]);
    }
    eyes(p, 0.38, 0.22, 0.12);
  } else {
    blobShadow(p, 0.45);
    part(p, new THREE.CylinderGeometry(0.42, 0.38, 0.16, 18), 0xd99a4e, [0, 0.12, 0]);
    part(p, new THREE.CylinderGeometry(0.46, 0.46, 0.12, 18), 0x6b3f22, [0, 0.26, 0]);
    part(p, new THREE.CylinderGeometry(0.49, 0.49, 0.04, 18), 0x7cc242, [0, 0.34, 0]);
    part(p, new THREE.SphereGeometry(0.43, 18, 10, 0, Math.PI * 2, 0, Math.PI / 2), 0xe0a458, [0, 0.35, 0]);
    eyes(p, 0.55, 0.32, 0.13);
    if (type === 'velkyHamburger') p.root.scale.setScalar(1.5);
  }
  return p;
}

export function makeProjectile(kind: 'porek' | 'hranolka'): THREE.Object3D {
  const g = new THREE.Group();
  const mesh =
    kind === 'porek'
      ? new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.42, 6), toon(0x7bc96f))
      : new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.36, 0.08), toon(0xffd23f));
  mesh.rotation.z = Math.PI / 2;
  g.add(mesh);
  return g;
}

export interface MouthView {
  root: THREE.Group;
  lips: THREE.MeshToonMaterial;
  teeth: THREE.Mesh[];
}

/** Velká komiksová pusa na konci cesty; zoubky ukazují zbývající životy. */
export function makeMouth(): MouthView {
  const root = new THREE.Group();
  const face = new THREE.Group();
  face.position.y = 0.95;
  face.rotation.y = -0.5;
  root.add(face);

  const inner = new THREE.Mesh(new THREE.CircleGeometry(0.78, 28), toon(0x5a0f1a));
  inner.position.z = -0.05;
  inner.scale.y = 0.75;
  face.add(inner);
  const tongue = new THREE.Mesh(new THREE.SphereGeometry(0.32, 14, 10), toon(0xf06b8b));
  tongue.position.set(0, -0.3, 0);
  tongue.scale.set(1.2, 0.5, 0.4);
  face.add(tongue);

  const lips = toon(0xd9434e);
  const lipMesh = new THREE.Mesh(new THREE.TorusGeometry(0.82, 0.24, 12, 32), lips);
  lipMesh.scale.y = 0.75;
  face.add(lipMesh);

  const teeth: THREE.Mesh[] = [];
  const toothGeo = new THREE.BoxGeometry(0.24, 0.26, 0.1);
  const toothMat = toon(0xffffff);
  for (const [x, y] of [
    [-0.3, 0.38],
    [0, 0.42],
    [0.3, 0.38],
  ]) {
    const t = new THREE.Mesh(toothGeo, toothMat);
    t.position.set(x, y, 0.02);
    face.add(t);
    teeth.push(t);
  }

  const shadow = new THREE.Mesh(shadowGeo, shadowMat);
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = 0.02;
  shadow.scale.set(1.1, 0.6, 1);
  root.add(shadow);

  return { root, lips, teeth };
}
