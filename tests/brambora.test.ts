import { describe, expect, it } from 'vitest';
import { Game, type GameEvent } from '../src/core/game';
import { LEVEL1 } from '../src/data/level1';
import { POTATO } from '../src/data/units';

/** Hra s jediným hamburgerem a Panem Bramborou v polovině cesty. */
function setup(): { game: Game; d: number } {
  const game = new Game(LEVEL1);
  const d = game.path.length / 2;
  const at = game.path.at(d);
  expect(game.placePotato({ x: at.x, z: at.z })).toBe(true);
  game.startNow();
  return { game, d };
}

function step(game: Game, seconds: number, events: GameEvent[] = []): GameEvent[] {
  for (let t = 0; t < seconds; t += 1 / 30) {
    game.update(1 / 30);
    events.push(...game.drainEvents());
  }
  return events;
}

describe('Pan Brambora', () => {
  it('stojí jen na cestě, ne u pusy a ne těsně vedle jiné brambory', () => {
    const game = new Game(LEVEL1);
    const mid = game.path.at(game.path.length / 2);
    expect(game.checkPotato({ x: mid.x, z: mid.z })).toBe('ok');
    // políčko na záhoně (daleko od cesty)
    const slot = game.slots.reduce((a, b) => (game.path.distanceTo(b) > game.path.distanceTo(a) ? b : a));
    expect(game.checkPotato(slot)).toBe('notPath');
    const end = game.path.at(game.path.length - 0.5);
    expect(game.checkPotato({ x: end.x, z: end.z })).toBe('mouth');
    game.placePotato({ x: mid.x, z: mid.z });
    const near = game.path.at(game.path.length / 2 + 0.5);
    expect(game.checkPotato({ x: near.x, z: near.z })).toBe('crowded');
  });

  it('fast food se zastaví u štítu a nedojde dál', () => {
    const { game, d } = setup();
    // dokud Pan Brambora stojí, žádný fast food není za ním
    for (let t = 0; t < 60 && game.potatoes.length; t += 1 / 30) {
      game.update(1 / 30);
      if (game.potatoes.length) for (const a of game.attackers) expect(a.d).toBeLessThanOrEqual(d - POTATO.blockGap + 1e-9);
    }
    expect(game.bites).toBe(0);
  });

  it('každý náraz vezme 1 srdíčko a bez srdíček se rozpadne', () => {
    const { game } = setup();
    const events = step(game, 120, []);
    const bumps = events.filter((e) => e.type === 'bump');
    expect(bumps.length).toBe(POTATO.lives);
    expect(events.some((e) => e.type === 'crumble')).toBe(true);
    expect(game.potatoes).toHaveLength(0);
  });

  it('po rozpadu jde fast food zase dál k puse', () => {
    const { game, d } = setup();
    step(game, 120);
    step(game, 30);
    const further = game.bites > 0 || game.attackers.some((a) => a.d > d);
    expect(further).toBe(true);
  });
});
