import { DEFENDERS, type DefenderLevel, type DefenderType } from '../../data/units';
import type { Vec2 } from '../../core/types';

export interface Defender {
  id: number;
  type: DefenderType;
  slot: number;
  x: number;
  z: number;
  level: 1 | 2;
  /** Zbývající sekundy růstu; dokud roste, nebrání a hranolky ho netrefí. */
  growLeft: number;
  cooldown: number;
  /** Zbývající sekundy ztuhnutí po zásahu hranolkou. */
  frozenLeft: number;
}

export function createDefender(id: number, type: DefenderType, slot: number, pos: Vec2): Defender {
  return {
    id,
    type,
    slot,
    x: pos.x,
    z: pos.z,
    level: 1,
    growLeft: DEFENDERS[type].growTime,
    cooldown: 0,
    frozenLeft: 0,
  };
}

export function defenderLevel(d: Defender): DefenderLevel {
  return DEFENDERS[d.type].levels[d.level - 1];
}

export function isGrown(d: Defender): boolean {
  return d.growLeft <= 0;
}
