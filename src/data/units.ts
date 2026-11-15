// Čísla jednotek pro první playtest (Plán první úrovně, kapitola 4).
// Vzdálenosti jsou v políčkách, časy v sekundách.

export type DefenderType = 'mrkev' | 'porek' | 'cibule' | 'brokolice';
export type AttackerType = 'hamburger' | 'hranolky' | 'velkyHamburger' | 'lizatko' | 'kecup';

export interface DefenderLevel {
  range: number;
  attackInterval: number;
  /** Cibule: jak dlouho vydrží oblak smradu (s). */
  cloudTime?: number;
  /** Brokolice: poloměr deštníku, do kterého se růžička nad cílem rozprskne. */
  splash?: number;
}

export interface DefenderStats {
  cost: number;
  growTime: number;
  upgradeCost: number;
  /** Pórek střílí (střela letí), mrkev seká hned. */
  projectileSpeed?: number;
  /** Cibule nikoho nezasáhne: vypustí oblak smradu, ve kterém fast food chodí pomaleji (násobek rychlosti). */
  cloudSlow?: number;
  /** Brokolice: jak dlouho letí raketa z růžičky vysokým obloukem (s). */
  rocketTime?: number;
  levels: [DefenderLevel, DefenderLevel];
}

export const DEFENDERS: Record<DefenderType, DefenderStats> = {
  mrkev: {
    cost: 40,
    growTime: 3,
    upgradeCost: 30,
    levels: [
      { range: 1.5, attackInterval: 1 },
      // o 40 % rychlejší sek, trochu větší mrkvomeč
      { range: 1.7, attackInterval: 1 / 1.4 },
    ],
  },
  porek: {
    cost: 60,
    growTime: 4,
    upgradeCost: 45,
    projectileSpeed: 8,
    levels: [
      { range: 3.5, attackInterval: 1.5 },
      // dosah +1 políčko, o 20 % rychlejší střelba
      { range: 4.5, attackInterval: 1.5 / 1.2 },
    ],
  },
  // Pan Cibule (list postavy na plátně): 1× za 6 s, jen když je fast food v dosahu, vypustí
  // oblak smradu asi 2 políčka kolem sebe; fast food v něm 3 s chodí poloviční rychlostí.
  cibule: {
    cost: 50,
    growTime: 4,
    upgradeCost: 40,
    cloudSlow: 0.5,
    levels: [
      { range: 2, attackInterval: 6, cloudTime: 3 },
      // úroveň 2: větší oblak, zpomalení déle
      { range: 2.5, attackInterval: 6, cloudTime: 4.5 },
    ],
  },
  // Pan Brokolice (list postavy na plátně): nejdražší a nejpomalejší, ale nejdál dostřelí.
  // Růžička letí vysokým obloukem a nad cílem se rozprskne do deštníku: každý fast food
  // do ~1 políčka dostane jeden zásah.
  brokolice: {
    cost: 80,
    growTime: 5,
    upgradeCost: 60,
    rocketTime: 1,
    levels: [
      { range: 5, attackInterval: 2.5, splash: 1 },
      // úroveň 2: větší roztříštění
      { range: 5.5, attackInterval: 2.5, splash: 1.4 },
    ],
  },
};

export interface ThrowStats {
  interval: number;
  range: number;
  freeze: number;
  projectileSpeed: number;
  firstDelay: number;
}

/** Lízátko se jednou za čas zastaví, roztočí a oblepí šťávou všechnu zeleninu kolem sebe. */
export interface SpinStats {
  interval: number;
  range: number;
  /** Jak dlouho z oblepené zeleniny stéká šťáva (nebojuje). */
  sticky: number;
  /** Jak dlouho se točí (stojí na místě). */
  duration: number;
  firstDelay: number;
}

/** Kečup se jednou za čas naštve, poskočí a vyprskne louži kečupu na cestu před sebe. */
export interface SquirtStats {
  interval: number;
  /** Kolik políček cesty před sebou pokryje. */
  length: number;
  /** Kolikrát rychleji jede fast food po kečupu. */
  boost: number;
  /** Za jak dlouho louže zaschne (s). */
  dry: number;
  /** Jak dlouho se zlobí a prská (stojí na místě). */
  duration: number;
  firstDelay: number;
}

export interface AttackerStats {
  hits: number;
  speed: number;
  reward: number;
  scale: number;
  throws?: ThrowStats;
  spin?: SpinStats;
  squirt?: SquirtStats;
}

export const ATTACKERS: Record<AttackerType, AttackerStats> = {
  hamburger: { hits: 5, speed: 1, reward: 15, scale: 1 },
  hranolky: {
    hits: 6,
    speed: 1.3,
    reward: 20,
    scale: 1,
    throws: { interval: 5, range: 1.6, freeze: 2, projectileSpeed: 6, firstDelay: 2 },
  },
  velkyHamburger: { hits: 8, speed: 0.8, reward: 40, scale: 1.5 },
  // Lízátko (list postavy na plátně): 6 zásahů, ~1 políčko/s, 1× za 6 s roztočení do ~1,5 políčka,
  // šťáva stéká 3 s, za odražení 25 vody.
  lizatko: {
    hits: 6,
    speed: 1,
    reward: 25,
    scale: 1,
    spin: { interval: 6, range: 1.5, sticky: 3, duration: 0.8, firstDelay: 3 },
  },
  // Pan Kečup (list postavy na plátně): 5 zásahů, ~1 políčko/s, 1× za 7 s vyprskne kečup
  // na ~3 políčka cesty, fast food na něm jede 2× rychleji, po 5 s zaschne; 20 vody.
  kecup: {
    hits: 5,
    speed: 1,
    reward: 20,
    scale: 1,
    squirt: { interval: 7, length: 3, boost: 2, dry: 5, duration: 0.9, firstDelay: 3 },
  },
};

/**
 * Fast food má tělo: zelenina ho zasáhne, jakmile se kruh jejího dosahu dotkne okraje
 * jeho těla, ne až jeho středu (tak to vidí i dítě na obrazovce).
 */
export const ATTACKER_BODY_RADIUS = 0.35;

/** Utíkající fast food běží rychleji, než chodil. */
export const FLEE_SPEED_FACTOR = 1.6;

/** Pusa snese 3 kousnutí, čtvrté znamená prohru. */
export const MOUTH_LIVES = 3;

/** Pauza mezi vlnami, potom se další vlna spustí sama. */
export const WAVE_PAUSE = 8;
