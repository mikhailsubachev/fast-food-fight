import { describe, expect, it } from 'vitest';
import { Game } from '../src/core/game';
import { Path } from '../src/core/path';
import { MIN_PATH_DISTANCE } from '../src/core/placement';
import type { Vec2 } from '../src/core/types';
import { LEVEL1 } from '../src/data/level1';
import { ATTACKERS, DEFENDERS, type DefenderType } from '../src/data/units';

const path = new Path(LEVEL1.path);
const carrotRange = DEFENDERS.mrkev.levels[0].range;
const leekRange = DEFENDERS.porek.levels[0].range;
const throwRange = ATTACKERS.hranolky.throws!.range;

/** Body záhonu po čtvrt políčku, kam se dá na prázdném záhonu zasadit. */
const free: Vec2[] = [];
{
  const empty = new Game(LEVEL1);
  const b = LEVEL1.board;
  for (let x = b.minX; x <= b.maxX; x += 0.25)
    for (let z = b.minZ; z <= b.maxZ; z += 0.25) if (empty.checkPlace({ x, z }) === 'ok') free.push({ x, z });
}
/** Místa dobrá pro mrkev: cesta v dosahu. */
const carrotSpots = free.filter((p) => path.distanceTo(p) <= 1.25);
/** Mrkve z návrhu úrovně (design/generator/gen_level.py). */
const designCarrots: Vec2[] = [
  { x: 3.3, z: 3.6 },
  { x: 5.4, z: 3.65 },
  { x: 9.65, z: 3.9 },
  { x: 1.1, z: 6.7 },
  { x: 5.0, z: 6.15 },
  { x: 7.2, z: 6.2 },
];
/** Místa dobrá pro pórek: mimo hod hranolek, ale cesta v dosahu. */
const leekSpots = free.filter((p) => path.distanceTo(p) > throwRange + 0.1 && path.distanceTo(p) <= leekRange - 0.3);

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

/** Zasadí na první volné místo ze seznamu. */
function plantFirst(g: Game, spots: Vec2[], type: DefenderType): boolean {
  const p = spots.find((s) => g.checkPlant(s, type) === 'ok');
  return p ? g.plant(p, type) : false;
}

describe('záhon 1. úrovně', () => {
  it('cesta vede od levého okraje záhonu k puse', () => {
    expect(LEVEL1.path[0].x).toBeCloseTo(LEVEL1.board.minX, 5);
    const end = LEVEL1.path[LEVEL1.path.length - 1];
    expect(Math.hypot(end.x - LEVEL1.mouth.x, end.z - LEVEL1.mouth.z)).toBeLessThan(1);
  });

  it('sází se skoro kamkoliv: volná je velká část záhonu', () => {
    const b = LEVEL1.board;
    const all = Math.floor((b.maxX - b.minX) / 0.25 + 1) * Math.floor((b.maxZ - b.minZ) / 0.25 + 1);
    expect(free.length / all).toBeGreaterThan(0.3);
  });

  it('mrkve z návrhu úrovně jdou zasadit', () => {
    const g = new Game({ ...LEVEL1, startWater: 1000 });
    for (const p of designCarrots) expect(g.plant(p, 'mrkev')).toBe(true);
  });

  it('je dost místa pro mrkev u cesty i pro pórek mimo dosah hranolek', () => {
    expect(carrotSpots.length).toBeGreaterThan(100);
    expect(leekSpots.length).toBeGreaterThan(20);
  });

  it('na cestu, překážky a těsně k jiné zelenině sázet nejde', () => {
    const g = new Game(LEVEL1);
    expect(g.checkPlace(LEVEL1.path[40])).toBe('path');
    for (const o of LEVEL1.obstacles) expect(g.checkPlace(o)).toBe('obstacle');
    expect(g.checkPlace(LEVEL1.mouth)).not.toBe('ok');
    const spot = carrotSpots[0];
    expect(g.plant(spot, 'mrkev')).toBe(true);
    expect(g.checkPlace({ x: spot.x + 0.5, z: spot.z })).toBe('crowded');
    expect(g.checkPlace({ x: LEVEL1.board.maxX + 1, z: 4 })).toBe('outside');
  });

  it('překážky ani pusa neleží na cestě', () => {
    for (const o of LEVEL1.obstacles) expect(path.distanceTo(o)).toBeGreaterThan(o.r);
    for (const p of free) expect(path.distanceTo(p)).toBeGreaterThanOrEqual(MIN_PATH_DISTANCE);
  });

  it('hamburger dojde ze startu do pusy za 20 až 30 s', () => {
    const walk = path.length / ATTACKERS.hamburger.speed;
    expect(walk).toBeGreaterThanOrEqual(20);
    expect(walk).toBeLessThanOrEqual(30);
  });

  it('mrkev z místa u cesty na cestu dosáhne', () => {
    for (const p of carrotSpots) expect(path.distanceTo(p)).toBeLessThanOrEqual(carrotRange);
  });
});

describe('pravidla', () => {
  it('na začátku jde zasadit jen mrkev, pórek se odemkne před 2. vlnou', () => {
    const g = new Game(LEVEL1);
    const spot = carrotSpots[0];
    expect(g.checkPlant(spot, 'porek')).toBe('locked');
    expect(g.checkPlant(spot, 'mrkev')).toBe('ok');
    g.startNow();
    run(g, 120, undefined, (game) => game.waveIndex === 1);
    // bez obránců hamburgery dojdou do pusy, ale 3 kousnutí ještě nejsou prohra
    expect(g.bites).toBe(3);
    expect(g.phase).toBe('countdown');
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
    expect(plantFirst(g, carrotSpots, 'mrkev')).toBe(true);
    expect(plantFirst(g, carrotSpots, 'mrkev')).toBe(true);
    expect(plantFirst(g, carrotSpots, 'mrkev')).toBe(true);
    expect(g.water).toBe(0);
    expect(plantFirst(g, carrotSpots, 'mrkev')).toBe(false);
    expect(g.defenders).toHaveLength(3);
  });

  it('odražený hamburger nechá vodu, uteče a zmizí z mapy', () => {
    const g = new Game(LEVEL1);
    for (const p of designCarrots.slice(0, 3)) g.plant(p, 'mrkev');
    g.startNow();
    const seen = new Set<string>();
    run(g, 60, (game) => game.drainEvents().forEach((e) => seen.add(e.type)), (game) => game.waveIndex === 1);
    expect(g.water).toBe(3 * ATTACKERS.hamburger.reward);
    expect(g.bites).toBe(0);
    expect(g.attackers).toHaveLength(0);
    expect([...seen]).toEqual(expect.arrayContaining(['hit', 'flee', 'escaped']));
  });

  it('hranolky zmrazí jen vyrostlou zeleninu', () => {
    const g = new Game({ ...LEVEL1, waves: [[{ type: 'hranolky', delay: 0 }]] });
    g.plant(designCarrots[1], 'mrkev');
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
    plantFirst(g, carrotSpots, 'mrkev');
    const d = g.defenders[0];
    expect(g.upgrade(d.id)).toBe(true);
    expect(d.level).toBe(2);
    expect(g.upgradeCost(d)).toBeNull();
    expect(g.upgrade(d.id)).toBe(false);
  });

  it('ťuknutí vedle zeleniny ji najde', () => {
    const g = new Game(LEVEL1);
    plantFirst(g, carrotSpots, 'mrkev');
    const d = g.defenders[0];
    expect(g.defenderNear({ x: d.x + 0.5, z: d.z })?.id).toBe(d.id);
    expect(g.defenderNear({ x: d.x + 2, z: d.z })).toBeUndefined();
  });
});

describe('hratelnost', () => {
  /** Jednoduchý hráč: mrkve u cesty, po odemčení pórky dál od cesty, zbytek vody na vylepšení. */
  function sensiblePlayer(maxCarrots: number) {
    return (g: Game) => {
      if (g.unlocked.has('porek') && g.defenders.filter((d) => d.type === 'porek').length < 4) {
        if (g.water >= DEFENDERS.porek.cost) plantFirst(g, leekSpots, 'porek');
        return;
      }
      const carrots = g.defenders.filter((d) => d.type === 'mrkev').length;
      if (carrots < maxCarrots && plantFirst(g, designCarrots, 'mrkev')) return;
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

  it('s jedinou mrkví se úroveň vyhrát nedá', () => {
    const g = new Game(LEVEL1);
    g.plant(designCarrots[1], 'mrkev');
    run(g, 600);
    expect(g.phase).toBe('lost');
  });
});
