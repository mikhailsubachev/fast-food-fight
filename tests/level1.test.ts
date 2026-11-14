import { describe, expect, it } from 'vitest';
import { Game } from '../src/core/game';
import { Path } from '../src/core/path';
import { LEVEL1 } from '../src/data/level1';
import { ATTACKERS, DEFENDERS, type DefenderType } from '../src/data/units';

const path = new Path(LEVEL1.path);
const carrotRange = DEFENDERS.mrkev.levels[0].range;
const leekRange = DEFENDERS.porek.levels[0].range;
const throwRange = ATTACKERS.hranolky.throws!.range;

const nearSlots = LEVEL1.slots.map((s, i) => ({ s, i })).filter(({ s }) => path.distanceTo(s) <= carrotRange);
const farSlots = LEVEL1.slots
  .map((s, i) => ({ s, i }))
  .filter(({ s }) => path.distanceTo(s) > throwRange && path.distanceTo(s) <= leekRange);

function run(game: Game, seconds: number, bot?: (g: Game) => void, until?: (g: Game) => boolean): number {
  const dt = 1 / 30;
  let t = 0;
  while (t < seconds && !game.finished && !until?.(game)) {
    bot?.(game);
    game.update(dt);
    t += dt;
  }
  return t;
}

describe('mapa 1. úrovně', () => {
  it('má 12 políček na sázení', () => {
    expect(LEVEL1.slots).toHaveLength(12);
  });

  it('aspoň 6 políček má cestu v dosahu mrkve', () => {
    expect(nearSlots.length).toBeGreaterThanOrEqual(6);
  });

  it('aspoň 3 políčka jsou mimo hod hranolek, ale pórek z nich dostřelí', () => {
    expect(farSlots.length).toBeGreaterThanOrEqual(3);
  });

  it('políčka nestojí na cestě a nepřekrývají se', () => {
    for (const s of LEVEL1.slots) expect(path.distanceTo(s)).toBeGreaterThanOrEqual(0.9);
    for (let i = 0; i < LEVEL1.slots.length; i++) {
      for (let j = i + 1; j < LEVEL1.slots.length; j++) {
        const a = LEVEL1.slots[i];
        const b = LEVEL1.slots[j];
        expect(Math.hypot(a.x - b.x, a.z - b.z)).toBeGreaterThanOrEqual(1);
      }
    }
  });

  it('políčka i pusa leží uvnitř viditelné plochy', () => {
    const b = LEVEL1.board;
    for (const p of [...LEVEL1.slots, LEVEL1.mouth]) {
      expect(p.x).toBeGreaterThan(b.minX);
      expect(p.x).toBeLessThan(b.maxX);
      expect(p.z).toBeGreaterThan(b.minZ);
      expect(p.z).toBeLessThan(b.maxZ);
    }
  });
});

describe('pravidla', () => {
  it('na začátku jde zasadit jen mrkev, pórek se odemkne před 2. vlnou', () => {
    const g = new Game(LEVEL1);
    expect(g.checkPlant(0, 'porek')).toBe('locked');
    expect(g.checkPlant(0, 'mrkev')).toBe('ok');
    g.startNow();
    run(g, 120, undefined, (game) => game.waveIndex === 1);
    // bez obránců hamburgery dojdou do pusy, ale 3 kousnutí ještě nejsou prohra
    expect(g.bites).toBe(3);
    expect(g.phase).toBe('countdown');
    expect(g.waveIndex).toBe(1);
    expect(g.unlocked.has('porek')).toBe(true);
    expect(g.drainEvents().some((e) => e.type === 'unlocked')).toBe(true);
  });

  it('čtvrté kousnutí znamená prohru', () => {
    const g = new Game(LEVEL1);
    run(g, 300);
    expect(g.phase).toBe('lost');
    expect(g.bites).toBe(4);
  });

  it('za vodu se sází a bez vody zasadit nejde', () => {
    const g = new Game(LEVEL1);
    expect(g.plant(0, 'mrkev')).toBe(true);
    expect(g.plant(1, 'mrkev')).toBe(true);
    expect(g.plant(2, 'mrkev')).toBe(true);
    expect(g.water).toBe(0);
    expect(g.checkPlant(3, 'mrkev')).toBe('water');
    expect(g.plant(0, 'mrkev')).toBe(false);
  });

  it('odražený hamburger nechá vodu, uteče a zmizí z mapy', () => {
    const g = new Game(LEVEL1);
    g.plant(nearSlots[0].i, 'mrkev');
    g.plant(nearSlots[2].i, 'mrkev');
    g.plant(nearSlots[3].i, 'mrkev');
    g.startNow();
    const seen = new Set<string>();
    run(g, 60, (game) => game.drainEvents().forEach((e) => seen.add(e.type)), (game) => game.waveIndex === 1);
    expect(g.water).toBe(3 * ATTACKERS.hamburger.reward);
    expect(g.bites).toBe(0);
    expect(g.attackers).toHaveLength(0);
    expect([...seen]).toEqual(expect.arrayContaining(['hit', 'flee', 'escaped']));
  });

  it('hranolky zmrazí jen vyrostlou zeleninu', () => {
    const g = new Game({
      ...LEVEL1,
      waves: [[{ type: 'hranolky', delay: 0 }]],
    });
    g.plant(nearSlots[0].i, 'mrkev');
    g.startNow();
    let frozenWhileGrowing = false;
    let frozen = false;
    run(g, 40, (game) => {
      const d = game.defenders[0];
      if (d.frozenLeft > 0) {
        frozen = true;
        if (d.growLeft > 0) frozenWhileGrowing = true;
      }
    });
    expect(frozen).toBe(true);
    expect(frozenWhileGrowing).toBe(false);
  });

  it('vylepšení jde jen na úroveň 2', () => {
    const g = new Game(LEVEL1);
    g.plant(0, 'mrkev');
    const d = g.defenders[0];
    expect(g.upgrade(d.id)).toBe(true);
    expect(d.level).toBe(2);
    expect(g.upgradeCost(d)).toBeNull();
    expect(g.upgrade(d.id)).toBe(false);
  });
});

describe('hratelnost', () => {
  /** Jednoduchý hráč: mrkve u cesty, po odemčení pórky dál od cesty, zbytek vody na vylepšení. */
  function sensiblePlayer(maxCarrots: number) {
    return (g: Game) => {
      const leekSlot = farSlots.find(({ i }) => !g.defenderAt(i));
      if (leekSlot && g.checkPlant(leekSlot.i, 'porek') === 'ok') {
        g.plant(leekSlot.i, 'porek');
        return;
      }
      const carrots = g.defenders.filter((d) => d.type === 'mrkev').length;
      const carrotSlot = nearSlots.find(({ i }) => !g.defenderAt(i));
      const wantLeek = g.unlocked.has('porek') && leekSlot;
      if (!wantLeek && carrots < maxCarrots && carrotSlot && g.checkPlant(carrotSlot.i, 'mrkev') === 'ok') {
        g.plant(carrotSlot.i, 'mrkev');
        return;
      }
      if (g.waveIndex >= 3) {
        for (const d of g.defenders) {
          const cost = g.upgradeCost(d);
          if (cost !== null && g.water >= cost) g.upgrade(d.id);
        }
      }
    };
  }

  it('rozumný hráč vyhraje a úroveň trvá do 5 minut', () => {
    const g = new Game(LEVEL1);
    const seconds = run(g, 600, sensiblePlayer(6));
    expect(g.phase).toBe('won');
    expect(g.stars).toBeGreaterThanOrEqual(2);
    expect(seconds).toBeLessThan(300);
  });

  it('hamburger dojde ze startu do pusy za 20 až 30 s', () => {
    const walk = path.length / ATTACKERS.hamburger.speed;
    expect(walk).toBeGreaterThanOrEqual(20);
    expect(walk).toBeLessThanOrEqual(30);
  });

  it('každá vlna je proti hráči s jednou mrkví těžší', () => {
    // pojistka proti vyvážení, kde stačí jedna mrkev na celou úroveň
    const g = new Game(LEVEL1);
    g.plant(nearSlots[2].i, 'mrkev');
    run(g, 600);
    expect(g.phase).toBe('lost');
  });
});

describe('typy zeleniny', () => {
  it('všechny typy mají 2 úrovně', () => {
    for (const t of Object.keys(DEFENDERS) as DefenderType[]) expect(DEFENDERS[t].levels).toHaveLength(2);
  });
});
