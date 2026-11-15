import { describe, expect, it } from 'vitest';
import { LEVEL2 } from '../src/data/level2';
import { Game } from '../src/core/game';
import { Path } from '../src/core/path';
import type { Vec2 } from '../src/core/types';
import { LEVEL3 } from '../src/data/level3';
import { ATTACKER_BODY_RADIUS, ATTACKERS, DEFENDERS, type AttackerType, type DefenderType } from '../src/data/units';

const path = new Path(LEVEL3.path);
const free = new Game(LEVEL3).slots;

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
const brocRange = DEFENDERS.brokolice.levels[0].range;
const brocSpots = byCoverage(free.filter((p) => path.distanceTo(p) > throwRange + 0.1 && path.distanceTo(p) <= brocRange - 0.5), brocRange);
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



const seqK = (types: AttackerType[], gap: number) => types.map((type, i) => ({ type, delay: i === 0 ? 0 : gap }));
/** Hráč: nejdřív daný počet od každé zeleniny (šetří na ni), potom vylepšuje. */
function player(carrots: number, leeks: number, onions: number, brocs: number, upgrade: boolean) {
  return (g: Game) => {
    const count = (t: DefenderType) => g.defenders.filter((d) => d.type === t).length;
    const want = (t: DefenderType, n: number, spots: Vec2[]) => {
      if (count(t) >= n || !g.unlocked.has(t)) return false;
      if (!spots.some((p) => g.checkPlace(p) === 'ok')) return false;
      if (g.water >= DEFENDERS[t].cost) plantFirst(g, spots, t);
      return true; // šetří na tuhle zeleninu
    };
    if (want('mrkev', carrots, carrotSpots)) return;
    if (want('porek', leeks, leekSpots)) return;
    if (want('brokolice', brocs, brocSpots)) return;
    if (want('cibule', onions, onionSpots)) return;
    if (upgrade && g.waveIndex >= 2) for (const d of g.defenders) { const c = g.upgradeCost(d); if (c !== null && g.water >= c) g.upgrade(d.id); }
  };
}

describe('3. úroveň „Oběd v Mekáči“', () => {
  it('má 6 vln, 180 vody, brokolici před 2. vlnou a kečup od 2. vlny', () => {
    expect(LEVEL3.waves).toHaveLength(6);
    expect(LEVEL3.startWater).toBe(180);
    expect(LEVEL3.unlocks).toEqual([{ wave: 1, type: 'brokolice' }]);
    expect(LEVEL3.waves[0].some((s) => s.type === 'kecup')).toBe(false);
    expect(LEVEL3.waves[1].every((s) => s.type === 'kecup')).toBe(true);
    expect(LEVEL3.waves.slice(1).every((w) => w.some((s) => s.type === 'kecup'))).toBe(true);
  });

  it('zbytky oběda leží mimo cestu a místa je ještě míň než ve 2. úrovni', () => {
    for (const o of LEVEL3.obstacles) expect(path.distanceTo(o)).toBeGreaterThan(o.r * 0.9);
    expect(free.length).toBeLessThan(new Game(LEVEL2).slots.length);
    expect(free.length).toBeGreaterThanOrEqual(30);
  });

  it('brokolicová raketa nad cílem zasáhne všechny pod deštníkem najednou', () => {
    const g = new Game({ ...LEVEL3, startDefenders: ['brokolice'], waves: [seqK(['hamburger', 'hamburger', 'hamburger'], 0.3)], startWater: 1000 });
    const spot = brocSpots[0];
    g.plant(spot, 'brokolice');
    g.startNow();
    let bursts = 0;
    let hitsInBurst = 0;
    for (let i = 0; i < 30 * 60 && bursts === 0; i++) {
      g.update(1 / 30);
      const ev = g.drainEvents();
      const b = ev.findIndex((e) => e.type === 'burst');
      if (b >= 0) {
        bursts++;
        hitsInBurst = ev.slice(b).filter((e) => e.type === 'hit').length;
      }
    }
    expect(bursts).toBe(1);
    expect(hitsInBurst).toBeGreaterThanOrEqual(2);
  });

  it('kečup vyprskne louži před sebe, fast food na ní jede 2× rychleji a za 5 s zaschne', () => {
    const g = new Game({ ...LEVEL3, waves: [seqK(['kecup', 'hamburger'], 2.5)], startWater: 0 });
    g.startNow();
    let squirted = false;
    for (let i = 0; i < 30 * 10 && !squirted; i++) {
      g.update(1 / 30);
      squirted = g.drainEvents().some((e) => e.type === 'squirt');
    }
    expect(squirted).toBe(true);
    const ketchup = g.attackers.find((a) => a.type === 'kecup')!;
    const puddle = g.puddles[0];
    expect(puddle.d0).toBeCloseTo(ketchup.d, 5);
    expect(puddle.d1 - puddle.d0).toBeCloseTo(ATTACKERS.kecup.squirt!.length, 5);
    // Kečup chvíli stojí a prská.
    const before = ketchup.d;
    g.update(0.3);
    expect(ketchup.d).toBe(before);
    // Hamburger, který na louži dojde, klouže rychleji.
    const burger = g.attackers.find((a) => a.type === 'hamburger')!;
    while (burger.d < puddle.d0 + 0.2 && g.puddles.length) g.update(1 / 30);
    const d0 = burger.d;
    g.update(0.1);
    expect(burger.sliding).toBe(true);
    expect((burger.d - d0) / 0.1).toBeCloseTo(ATTACKERS.hamburger.speed * ATTACKERS.kecup.squirt!.boost * LEVEL3.waveSpeed![0], 1);
    run(g, 6);
    expect(g.puddles.some((p) => p.id === puddle.id)).toBe(false);
  });

  it('za odražení je v 3. úrovni poloviční voda', () => {
    const g = new Game({ ...LEVEL3, startDefenders: ['mrkev'], waves: [seqK(['hamburger'], 0)], startWater: 1000 });
    g.plant(carrotSpots[0], 'mrkev');
    g.startNow();
    let water = 0;
    run(g, 120, undefined, (gg) => gg.drainEvents().some((e) => e.type === 'flee' && (water = e.water) > 0));
    expect(water).toBe(10);
  });
});

describe('hratelnost 3. úrovně', () => {
  it('vyvážená zahrádka s brokolicí a vylepšením vyhraje na aspoň 2 hvězdy', () => {
    const g = new Game(LEVEL3);
    run(g, 1500, player(8, 6, 3, 4, true));
    expect(g.phase).toBe('won');
    expect(g.stars).toBeGreaterThanOrEqual(2);
  });

  it('bez brokolice to jde jen těsně', () => {
    const g = new Game(LEVEL3);
    run(g, 1500, player(8, 6, 3, 0, true));
    expect(g.stars).toBeLessThanOrEqual(1);
  });

  it('bez vylepšení nebo s malou zahrádkou se úroveň prohraje', () => {
    for (const bot of [player(8, 6, 3, 4, false), player(6, 4, 2, 2, true)]) {
      const g = new Game(LEVEL3);
      run(g, 1500, bot);
      expect(g.phase).toBe('lost');
    }
  });
});
