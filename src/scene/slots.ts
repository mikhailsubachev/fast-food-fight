// Šestihranná políčka na sázení, jak je kreslí návrh úrovně:
// volné světle zelené, zasazené hnědé (hlína) a vybrané bílé se zeleným okrajem.
import * as THREE from 'three';
import { HEX_HALF_HEIGHT, HEX_HALF_WIDTH } from '../core/placement';
import type { Vec2 } from '../core/types';

/** Šestihran s plochým vrškem; `scale` ho zvětší nebo zmenší (pro okraj a vnitřek). */
function hexShape(scale = 1): THREE.Shape {
  const w = HEX_HALF_WIDTH * scale;
  const h = HEX_HALF_HEIGHT * scale;
  const s = new THREE.Shape();
  s.moveTo(w, 0);
  s.lineTo(w / 2, h);
  s.lineTo(-w / 2, h);
  s.lineTo(-w, 0);
  s.lineTo(-w / 2, -h);
  s.lineTo(w / 2, -h);
  s.closePath();
  return s;
}

/** Plný šestihran ležící na zemi. */
function hexFill(scale = 1): THREE.BufferGeometry {
  const g = new THREE.ShapeGeometry(hexShape(scale));
  g.rotateX(-Math.PI / 2);
  return g;
}

/** Okraj šestihranu široký `width` políček (tah štětce z návrhu převedený z px). */
function hexEdge(width: number): THREE.BufferGeometry {
  const outer = hexShape(1 + width / 2 / HEX_HALF_WIDTH);
  outer.holes.push(hexShape(1 - width / 2 / HEX_HALF_WIDTH));
  const g = new THREE.ShapeGeometry(outer);
  g.rotateX(-Math.PI / 2);
  return g;
}

const PX = 1 / 120;
const mat = (color: number, opacity = 1) =>
  new THREE.MeshBasicMaterial({ color, transparent: opacity < 1, opacity, depthWrite: false });

const FREE_FILL = mat(0xd9f2a6, 0.38);
const FREE_EDGE = mat(0x4e7f2e);
const PLANTED_FILL = mat(0x7a5433);
const PLANTED_INNER = mat(0x8b633d);
const PLANTED_EDGE = mat(0x2b2118);
const SELECTED_FILL = mat(0xffffff, 0.6);
const SELECTED_EDGE = mat(0x2f9e44);

const GEO = {
  fill: hexFill(),
  inner: hexFill(0.743),
  edgeThin: hexEdge(3 * PX),
  edgePlanted: hexEdge(3.5 * PX),
  edgeSelected: hexEdge(6 * PX),
};

type SlotState = 'free' | 'planted' | 'selected';

interface SlotMesh {
  p: Vec2;
  state: SlotState | null;
  fill: THREE.Mesh;
  inner: THREE.Mesh;
  edge: THREE.Mesh;
}

export class SlotsView {
  readonly root = new THREE.Group();
  private readonly meshes: SlotMesh[];
  private selected: Vec2 | null = null;

  constructor(slots: readonly Vec2[]) {
    this.meshes = slots.map((p) => {
      const fill = new THREE.Mesh(GEO.fill, FREE_FILL);
      const inner = new THREE.Mesh(GEO.inner, PLANTED_INNER);
      const edge = new THREE.Mesh(GEO.edgeThin, FREE_EDGE);
      fill.position.set(p.x, 0.02, p.z);
      inner.position.set(p.x, 0.025, p.z);
      edge.position.set(p.x, 0.03, p.z);
      // Políčka se kreslí po zemi a před postavami (ty mají vyšší pořadí).
      for (const m of [fill, inner, edge]) m.renderOrder = 1;
      this.root.add(fill, inner, edge);
      return { p, state: null, fill, inner, edge };
    });
    this.update([]);
  }

  select(p: Vec2 | null): void {
    this.selected = p;
  }

  /** Obarví políčka podle toho, kde roste zelenina a které je vybrané. */
  update(planted: readonly Vec2[]): void {
    for (const m of this.meshes) {
      const isPlanted = planted.some((d) => Math.hypot(d.x - m.p.x, d.z - m.p.z) < 0.1);
      const isSelected = !isPlanted && this.selected !== null && Math.hypot(this.selected.x - m.p.x, this.selected.z - m.p.z) < 0.1;
      const state: SlotState = isPlanted ? 'planted' : isSelected ? 'selected' : 'free';
      if (state === m.state) continue;
      m.state = state;
      m.inner.visible = state === 'planted';
      if (state === 'planted') {
        m.fill.material = PLANTED_FILL;
        m.edge.material = PLANTED_EDGE;
        m.edge.geometry = GEO.edgePlanted;
      } else if (state === 'selected') {
        m.fill.material = SELECTED_FILL;
        m.edge.material = SELECTED_EDGE;
        m.edge.geometry = GEO.edgeSelected;
      } else {
        m.fill.material = FREE_FILL;
        m.edge.material = FREE_EDGE;
        m.edge.geometry = GEO.edgeThin;
      }
    }
  }
}
