import * as THREE from 'three';
import type { LevelData, Obstacle } from '../data/level1';
import { toon } from './meshes';

// Barvy podle návrhu úrovně (design/artboardy/5-uroven-1.html).
export const INK = 0x2b2118;
const GRASS = 0x8bb85a;

export interface Board {
  root: THREE.Group;
}

/**
 * Zem z návrhu úrovně: trávník s ozdobami, cesta a kaluž v jednom obrázku
 * (public/assets/prostredi/louka.svg z tools/export_louka.py). V návrhu je 120 px na políčko
 * v ose x a 108 px v ose z; obrázek pokrývá px −480 až 2400 a −270 až 1350.
 */
const MEADOW = { minX: -480 / 120, maxX: 2400 / 120, minZ: -270 / 108, maxZ: 1350 / 108 };

function meadowFromDesign(): THREE.Mesh {
  const map = new THREE.TextureLoader().load(`${import.meta.env.BASE_URL}assets/prostredi/louka.svg`);
  map.colorSpace = THREE.SRGBColorSpace;
  map.anisotropy = 8;
  const w = MEADOW.maxX - MEADOW.minX;
  const d = MEADOW.maxZ - MEADOW.minZ;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), new THREE.MeshBasicMaterial({ map }));
  m.rotation.x = -Math.PI / 2;
  m.position.set((MEADOW.minX + MEADOW.maxX) / 2, 0.001, (MEADOW.minZ + MEADOW.maxZ) / 2);
  return m;
}

function flat(color: number): THREE.MeshBasicMaterial {
  return new THREE.MeshBasicMaterial({ color });
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
    case 'kaluz':
      // Kaluž je nakreslená přímo v obrázku země z návrhu.
      break;
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

/** Louka s cestou z návrhu a překážky nad zemí. */
export function buildBoard(level: LevelData): Board {
  const root = new THREE.Group();

  // Jednobarevná louka všude kolem, aby na širších obrazovkách nic nechybělo.
  const meadow = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.MeshBasicMaterial({ color: GRASS }));
  meadow.rotation.x = -Math.PI / 2;
  root.add(meadow, meadowFromDesign());

  for (const o of level.obstacles) root.add(obstacleMesh(o));

  return { root };
}
