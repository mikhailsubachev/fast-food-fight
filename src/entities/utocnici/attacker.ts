import { ATTACKERS, type AttackerType } from '../../data/units';

export interface Attacker {
  id: number;
  type: AttackerType;
  /** Vzdálenost od startu cesty. */
  d: number;
  hitsLeft: number;
  /** Utíkající fast food už neškodí a nedá se zasáhnout. */
  fleeing: boolean;
  throwCooldown: number;
}

export function createAttacker(id: number, type: AttackerType): Attacker {
  const stats = ATTACKERS[type];
  return {
    id,
    type,
    d: 0,
    hitsLeft: stats.hits,
    fleeing: false,
    throwCooldown: stats.throws?.firstDelay ?? 0,
  };
}
