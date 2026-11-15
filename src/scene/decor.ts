// Poletující ozdoby louky z návrhu úrovně: modrý a růžový motýl a včelka.
// Jen pro radost, do hry nezasahují.
import * as THREE from 'three';

interface Critter {
  sprite: THREE.Sprite;
  /** Místo v návrhu, kolem kterého poletuje (políčka). */
  home: THREE.Vector3;
  /** Jak daleko a jak rychle krouží. */
  reach: number;
  speed: number;
  phase: number;
  /** Mávání křídly za sekundu. */
  flap: number;
  size: number;
  /** Včelka létá osmičku, motýl líné kolečko. */
  eight: boolean;
}

const loader = new THREE.TextureLoader();

function critter(name: string, x: number, z: number, opts: Partial<Critter>): Critter {
  const map = loader.load(`${import.meta.env.BASE_URL}assets/prostredi/${name}.svg`);
  map.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map, transparent: true, depthWrite: false }));
  const size = opts.size ?? 0.42;
  sprite.scale.set(size, size, 1);
  sprite.renderOrder = 3;
  return {
    sprite,
    home: new THREE.Vector3(x, 1.1, z),
    reach: 0.6,
    speed: 0.5,
    phase: Math.random() * 10,
    flap: 3,
    size,
    eight: false,
    ...opts,
  };
}

export class Critters {
  readonly root = new THREE.Group();
  private readonly list: Critter[];

  constructor() {
    // Polohy z návrhu (px / 120 a px / 108), posunuté kousek dozadu, protože létají nad zemí.
    this.list = [
      critter('motyl-modry', 1.9, 8.3, { reach: 0.8, speed: 0.45 }),
      critter('motyl-ruzovy', 15.2, 5.7, { reach: 0.7, speed: 0.55 }),
      critter('vcela', 4.8, 2.1, { reach: 0.9, speed: 0.9, flap: 12, size: 0.36, eight: true }),
    ];
    for (const c of this.list) this.root.add(c.sprite);
  }

  update(time: number): void {
    for (const c of this.list) {
      const t = time * c.speed + c.phase;
      const x = c.home.x + Math.cos(t) * c.reach;
      const z = c.home.z + (c.eight ? Math.sin(2 * t) / 2 : Math.sin(t)) * c.reach * 0.6;
      const y = c.home.y + Math.sin(t * 2.3) * 0.15;
      c.sprite.position.set(x, y, z);
      // Mávání křídly: obrázek se rytmicky zužuje; letí tam, kam se dívá.
      const wings = 0.55 + 0.45 * Math.abs(Math.sin(time * c.flap * Math.PI));
      const dir = -Math.sin(t) >= 0 ? 1 : -1;
      c.sprite.scale.set(c.size * wings, c.size, 1);
      // Sprite záporné měřítko neumí: otočení se dělá zrcadlením obrázku.
      const map = c.sprite.material.map!;
      map.repeat.x = dir;
      map.offset.x = dir < 0 ? 1 : 0;
    }
  }
}
