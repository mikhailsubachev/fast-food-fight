import { describe, expect, it } from 'vitest';
import { Game } from '../src/core/game';
import { Path } from '../src/core/path';
import type { Vec2 } from '../src/core/types';
import { LEVEL2 } from '../src/data/level2';
import { ATTACKER_BODY_RADIUS, ATTACKERS, DEFENDERS, type DefenderType } from '../src/data/units';

const path = new Path(LEVEL2.path);
const free = new Game(LEVEL2).slots;

function pathInRange(p: Vec2, range: number): number {
  let n = 0;
  for (let d = 0; d < path.length; d += 0.25) {
    const q = path.at(d);
    if (Math.hypot(q.x - p.x, q.z - p.z) <= range) n++;
  }
  return n;
}
const byCoverage = (spots: Vec2[], range: number) => [...spots].sort((a, b) => pathInRange(b, range) - pathInRange(a, range));
const carrotRange = DEFENDERS.mrkev.levels[0].range + ATTACKER_BODY_RADIUS;
const leekRange = DEFENDERS.porek.levels[0].range;
const throwRange = ATTACKERS.hranolky.throws!.range;
const carrotSpots = byCoverage(free.filter((p) => path.distanceTo(p) <= carrotRange), carrotRange);
const leekSpots = byCoverage(
  free.filter((p) => path.distanceTo(p) > throwRange + 0.1 && path.distanceTo(p) <= leekRange - 0.3),
  leekRange,
);
const onionSpots = byCoverage(free.filter((p) => path.distanceTo(p) <= 1.6), DEFENDERS.cibule.levels[0].range);

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

function plantFirst(g: Game, spots: Vec2[], type: DefenderType): boolean {
  const p = spots.find((s) => g.checkPlant(s, type) === 'ok');
  return p ? g.plant(p, type) : false;
}

describe('2. úroveň „Školní svačina“', () => {
  it('má 5 vln: hamburgery, hranolky, lízátka, velké hamburgery a nakonec všechno', () => {
    expect(LEVEL2.waves).toHaveLength(5);
    expect(LEVEL2.startWater).toBe(150);
    const kinds = LEVEL2.waves.map((w) => [...new Set(w.map((s) => s.type))]);
    expect(kinds.slice(0, 4)).toEqual([['hamburger'], ['hranolky'], ['lizatko'], ['velkyHamburger']]);
    expect(new Set(kinds[4]).size).toBe(4);
  });

  it('školní věci leží mimo cestu a zaberou políčka', () => {
    for (const o of LEVEL2.obstacles) expect(path.distanceTo(o)).toBeGreaterThan(o.r * 0.9);
    expect(free.length).toBeLessThan(new Game({ ...LEVEL2, obstacles: [] }).slots.length);
    expect(free.length).toBeGreaterThanOrEqual(30);
  });

  it('cibule se odemkne před 2. vlnou', () => {
    const g = new Game({ ...LEVEL2, waves: [[{ type: 'hamburger', delay: 0 }], ...LEVEL2.waves.slice(1)] });
    expect(g.unlocked.has('cibule')).toBe(false);
    g.startNow();
    run(g, 200, undefined, (game) => game.waveIndex === 1);
    expect(g.unlocked.has('cibule')).toBe(true);
  });
});

describe('cibule a lízátko', () => {
  it('cibule vypustí oblak, jen když je fast food blízko, a ten v něm jde pomaleji', () => {
    const g = new Game({ ...LEVEL2, startDefenders: ['cibule'], waves: [[{ type: 'hamburger', delay: 0 }]], startWater: 1000 });
    const spot = onionSpots[0];
    g.plant(spot, 'cibule');
    g.defenders[0].growLeft = 0;
    run(g, 2);
    expect(g.clouds).toHaveLength(0); // vlna ještě nezačala, nikdo není blízko
    g.startNow();
    let slowStep = 0;
    let normalStep = 0;
    let prev = 0;
    run(g, 60, (game) => {
      const a = game.attackers[0];
      if (!a) return;
      const step = a.d - prev;
      prev = a.d;
      if (a.slowed) slowStep = step;
      else if (step > 0) normalStep = step;
    });
    expect(slowStep).toBeGreaterThan(0);
    expect(slowStep).toBeCloseTo(normalStep * DEFENDERS.cibule.cloudSlow!, 3);
  });

  it('lízátko oblepí vyrostlou zeleninu kolem sebe a ta pak 3 s nebojuje', () => {
    const g = new Game({ ...LEVEL2, waves: [[{ type: 'lizatko', delay: 0 }]], startWater: 1000 });
    const spot = carrotSpots[0];
    g.plant(spot, 'mrkev');
    const d = g.defenders[0];
    d.growLeft = 0;
    g.startNow();
    let stuck = false;
    let attackedWhileStuck = false;
    run(g, 60, (game) => {
      if (d.stickyLeft > 0) stuck = true;
      const events = game.drainEvents();
      if (d.stickyLeft > 0.05 && events.some((e) => e.type === 'attack' && e.defenderId === d.id)) attackedWhileStuck = true;
    });
    expect(stuck).toBe(true);
    expect(attackedWhileStuck).toBe(false);
  });

  it('rostoucí zeleninu lízátko neoblepí', () => {
    const g = new Game({ ...LEVEL2, waves: [[{ type: 'lizatko', delay: 0 }]], startWater: 1000 });
    g.plant(carrotSpots[0], 'mrkev');
    const d = g.defenders[0];
    d.growLeft = 1e9;
    g.startNow();
    let stuck = false;
    run(g, 40, () => {
      if (d.stickyLeft > 0) stuck = true;
    });
    expect(stuck).toBe(false);
  });
});

describe('hratelnost 2. úrovně', () => {
  function player(carrots: number, leeks: number, onions: number, upgrade: boolean) {
    return (g: Game) => {
      const count = (t: DefenderType) => g.defenders.filter((d) => d.type === t).length;
      if (count('mrkev') < carrots) {
        if (g.water >= DEFENDERS.mrkev.cost) plantFirst(g, carrotSpots, 'mrkev');
        return;
      }
      if (count('porek') < leeks) {
        if (g.water >= DEFENDERS.porek.cost) plantFirst(g, leekSpots, 'porek');
        return;
      }
      if (g.unlocked.has('cibule') && count('cibule') < onions) {
        if (g.water >= DEFENDERS.cibule.cost) plantFirst(g, onionSpots, 'cibule');
        return;
      }
      if (upgrade && g.waveIndex >= 2) {
        for (const d of g.defenders) {
          const cost = g.upgradeCost(d);
          if (cost !== null && g.water >= cost) g.upgrade(d.id);
        }
      }
    };
  }

  it('rozumný hráč (mrkve, pórky, cibule, vylepšení) vyhraje na aspoň 2 hvězdy', () => {
    const g = new Game(LEVEL2);
    const seconds = run(g, 900, player(6, 4, 2, true));
    expect(g.phase).toBe('won');
    expect(g.stars).toBeGreaterThanOrEqual(2);
    expect(seconds).toBeLessThan(420);
  });

  it('bez vylepšení se úroveň vyhrát nedá', () => {
    const g = new Game(LEVEL2);
    run(g, 900, player(6, 4, 0, false));
    expect(g.phase).toBe('lost');
  });
});
