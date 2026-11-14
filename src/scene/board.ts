import * as THREE from 'three';
import type { LevelData, Obstacle } from '../data/level1';
import type { Vec2 } from '../core/types';
import { toon } from './meshes';

// Barvy podle návrhu úrovně (design/artboardy/5-uroven-1.html).
export const INK = 0x2b2118;
const GRASS = 0x8bb85a;
const GRASS_DARK = 0x7fae4e;
const GRASS_LIGHT = 0x9cc768;
const DIRT = 0xc9965a;
const DIRT_LIGHT = 0xddb27a;
const DIRT_RUT = 0xb9844b;

export interface Board {
  root: THREE.Group;
}

/** Proměnlivá šířka cesty jako v návrhu: cesta je „ručně kreslená“, ne rovný pruh. */
function halfWidth(i: number): number {
  return 0.52 + 0.07 * Math.sin(i * 0.37) + 0.04 * Math.sin(i * 1.13 + 1);
}

/** Pás podél čáry: šířka podle funkce, posun do strany `offset`. */
function ribbon(points: readonly Vec2[], width: (i: number) => number, y: number, offset = 0): THREE.BufferGeometry {
  const pos: number[] = [];
  const idx: number[] = [];
  points.forEach((p, i) => {
    const a = points[Math.max(0, i - 1)];
    const b = points[Math.min(points.length - 1, i + 1)];
    const len = Math.hypot(b.x - a.x, b.z - a.z) || 1;
    const nx = -(b.z - a.z) / len;
    const nz = (b.x - a.x) / len;
    const w = width(i);
    const cx = p.x + nx * offset;
    const cz = p.z + nz * offset;
    pos.push(cx + nx * w, y, cz + nz * w, cx - nx * w, y, cz - nz * w);
    if (i > 0) {
      const k = i * 2;
      idx.push(k - 2, k - 1, k, k - 1, k + 1, k);
    }
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  g.computeVertexNormals();
  return g;
}

function flat(color: number): THREE.MeshBasicMaterial {
  return new THREE.MeshBasicMaterial({ color });
}

function grassPatch(x: number, z: number, rx: number, rz: number, color: number): THREE.Mesh {
  const m = new THREE.Mesh(new THREE.CircleGeometry(1, 14), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.45 }));
  m.rotation.x = -Math.PI / 2;
  m.scale.set(rx, rz, 1);
  m.position.set(x, 0.003, z);
  return m;
}

function obstacleMesh(o: Obstacle): THREE.Object3D {
  const g = new THREE.Group();
  g.position.set(o.x, 0, o.z);
  const outline = (mesh: THREE.Mesh, scale = 1.08) => {
    const back = new THREE.Mesh(mesh.geometry, new THREE.MeshBasicMaterial({ color: INK, side: THREE.BackSide }));
    back.position.copy(mesh.position);
    back.rotation.copy(mesh.rotation);
    back.scale.copy(mesh.scale).multiplyScalar(scale);
    g.add(back);
  };
  switch (o.kind) {
    case 'parez': {
      const side = new THREE.Mesh(new THREE.CylinderGeometry(o.r * 0.85, o.r, 0.45, 18), toon(0x8a5a30));
      side.position.y = 0.22;
      const top = new THREE.Mesh(new THREE.CircleGeometry(o.r * 0.85, 18), toon(0xe9c48c));
      top.rotation.x = -Math.PI / 2;
      top.position.y = 0.451;
      const ring = new THREE.Mesh(new THREE.RingGeometry(o.r * 0.4, o.r * 0.46, 18), flat(0xc49a60));
      ring.rotation.x = -Math.PI / 2;
      ring.position.y = 0.455;
      outline(side);
      g.add(side, top, ring);
      break;
    }
    case 'kamen': {
      const rock = new THREE.Mesh(new THREE.DodecahedronGeometry(o.r, 0), toon(0xa7a196));
      rock.scale.set(1, 0.6, 0.85);
      rock.position.y = 0.2;
      rock.rotation.y = 0.4;
      outline(rock);
      g.add(rock);
      break;
    }
    case 'kaluz': {
      // Kaluž je vidět o něco menší, než je místo, kam se nedá sázet, aby nezasahovala do cesty.
      const edge = new THREE.Mesh(new THREE.CircleGeometry(o.r * 0.72, 24), flat(INK));
      edge.rotation.x = -Math.PI / 2;
      edge.scale.set(1.04, 0.74, 1);
      edge.position.y = 0.01;
      const water = new THREE.Mesh(new THREE.CircleGeometry(o.r * 0.72, 24), flat(0x8fcff2));
      water.rotation.x = -Math.PI / 2;
      water.scale.set(1, 0.7, 1);
      water.position.y = 0.02;
      const shine = new THREE.Mesh(new THREE.CircleGeometry(o.r * 0.25, 12), flat(0xffffff));
      shine.rotation.x = -Math.PI / 2;
      shine.scale.set(1.6, 0.4, 1);
      shine.position.set(-o.r * 0.3, 0.03, -o.r * 0.25);
      g.add(edge, water, shine);
      break;
    }
    case 'krtina': {
      const hill = new THREE.Mesh(new THREE.SphereGeometry(o.r, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2), toon(0x6b4a2e));
      hill.scale.y = 0.6;
      outline(hill);
      g.add(hill);
      break;
    }
  }
  return g;
}

/** Louka, záhon, hliněná cesta a překážky. */
export function buildBoard(level: LevelData): Board {
  const root = new THREE.Group();

  // Louka je velká, aby na širších obrazovkách po stranách nic nechybělo.
  const meadow = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), toon(GRASS));
  meadow.rotation.x = -Math.PI / 2;
  root.add(meadow);

  // Pár tmavších a světlejších skvrn trávy, aby louka nebyla jednolitá.
  const rnd = mulberry32(7);
  const b = level.board;
  for (let i = 0; i < 26; i++) {
    const x = b.minX - 2 + rnd() * (b.maxX - b.minX + 4);
    const z = b.minZ - 1 + rnd() * (b.maxZ - b.minZ + 2);
    root.add(grassPatch(x, z, 0.3 + rnd() * 0.5, 0.2 + rnd() * 0.3, rnd() < 0.5 ? GRASS_DARK : GRASS_LIGHT));
  }

  // Cesta: obrys, hlína, světlý střed a vyjeté koleje.
  const pts = level.path;
  // Cesta je poskládaná z překrývajících se kruhů: okraj je hladký i ve vnitřku ostrých ohybů.
  const discs = (width: (i: number) => number, y: number, color: number) => {
    const geo = new THREE.CircleGeometry(1, 20);
    geo.rotateX(-Math.PI / 2);
    const mesh = new THREE.InstancedMesh(geo, new THREE.MeshBasicMaterial({ color }), pts.length);
    const m = new THREE.Matrix4();
    pts.forEach((p, i) => {
      const w = width(i);
      mesh.setMatrixAt(i, m.makeScale(w, 1, w).setPosition(p.x, y, p.z));
    });
    root.add(mesh);
  };
  discs((i) => halfWidth(i) + 0.07, 0.01, INK);
  discs(halfWidth, 0.015, DIRT);
  discs((i) => halfWidth(i) * 0.72, 0.02, DIRT_LIGHT);
  for (const off of [0.24, -0.24])
    root.add(new THREE.Mesh(ribbon(pts, () => 0.035, 0.025, off), new THREE.MeshBasicMaterial({ color: DIRT_RUT, side: THREE.DoubleSide })));

  // Šipka na startu cesty.
  const start = pts[0];
  const arrow = new THREE.Mesh(new THREE.ConeGeometry(0.32, 0.7, 3), flat(0xe0574f));
  arrow.rotation.set(-Math.PI / 2, 0, -Math.PI / 2);
  arrow.position.set(start.x + 0.5, 0.04, start.z);
  arrow.scale.z = 0.1;
  root.add(arrow);

  for (const o of level.obstacles) root.add(obstacleMesh(o));

  return { root };
}

/** Malý deterministický generátor náhody, aby louka vypadala pokaždé stejně. */
function mulberry32(seed: number): () => number {
  let a = seed;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
