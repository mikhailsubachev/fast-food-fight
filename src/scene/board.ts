import * as THREE from 'three';
import type { LevelData } from '../data/level1';
import { toon } from './meshes';

export interface Board {
  root: THREE.Group;
  slots: THREE.Mesh[];
}

const SLOT_COLOR = 0x6b4a2e;
export const SLOT_HIGHLIGHT = 0xa8794a;

/** Kuchyňský stůl, záhon, cesta z prostírání a políčka na sázení. */
export function buildBoard(level: LevelData): Board {
  const root = new THREE.Group();

  // Stůl je velký, aby na širších obrazovkách po stranách nic nechybělo.
  const table = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), toon(0xd9b98c));
  table.rotation.x = -Math.PI / 2;
  table.position.y = -0.06;
  root.add(table);

  const b = level.board;
  const bed = new THREE.Mesh(new THREE.BoxGeometry(b.maxX - b.minX, 0.1, b.maxZ - b.minZ), toon(0x8bb85a));
  bed.position.set((b.minX + b.maxX) / 2, -0.05, (b.minZ + b.maxZ) / 2);
  root.add(bed);

  const pathMat = toon(0xf2e3c0);
  for (let i = 0; i < level.path.length - 1; i++) {
    const a = level.path[i];
    const c = level.path[i + 1];
    const len = Math.hypot(c.x - a.x, c.z - a.z);
    const strip = new THREE.Mesh(new THREE.BoxGeometry(len + 1, 0.04, 1), pathMat);
    strip.position.set((a.x + c.x) / 2, 0.02, (a.z + c.z) / 2);
    strip.rotation.y = -Math.atan2(c.z - a.z, c.x - a.x);
    root.add(strip);
  }

  // Šipka na startu cesty.
  const start = level.path[0];
  const arrow = new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.6, 3), toon(0xe0574f));
  arrow.rotation.set(-Math.PI / 2, 0, -Math.PI / 2);
  arrow.position.set(start.x + 0.4, 0.08, start.z);
  arrow.scale.z = 0.2;
  root.add(arrow);

  const slotGeo = new THREE.BoxGeometry(0.86, 0.06, 0.86);
  const slots = level.slots.map((s) => {
    const m = new THREE.Mesh(slotGeo, toon(SLOT_COLOR));
    m.position.set(s.x, 0.03, s.z);
    root.add(m);
    return m;
  });

  return { root, slots };
}

export function setSlotHighlight(board: Board, index: number | null): void {
  board.slots.forEach((m, i) => {
    (m.material as THREE.MeshToonMaterial).color.setHex(i === index ? SLOT_HIGHLIGHT : SLOT_COLOR);
  });
}
