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
  /** Lízátko: za kolik sekund se zase roztočí. */
  spinCooldown: number;
  /** Lízátko: jak dlouho se ještě točí (stojí na místě). */
  spinLeft: number;
  /** Je právě v oblaku smradu (jde pomaleji). */
  slowed: boolean;
  /** Kečup: za kolik sekund zase vyprskne. */
  squirtCooldown: number;
  /** Kečup: jak dlouho se ještě zlobí a prská (stojí na místě). */
  squirtLeft: number;
  /** Klouže po kečupu (jede rychleji). */
  sliding: boolean;
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
    spinCooldown: stats.spin?.firstDelay ?? 0,
    spinLeft: 0,
    slowed: false,
    squirtCooldown: stats.squirt?.firstDelay ?? 0,
    squirtLeft: 0,
    sliding: false,
  };
}
