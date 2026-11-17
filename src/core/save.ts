import { POTATO } from '../data/units';

// Postup hráče uložený v zařízení. Úložiště může chybět (soukromé okno), proto vše v try/catch.

export interface Progress {
  unlockedLevel: number;
  stars: Record<string, number>;
  sound: boolean;
  /** Postavy, jejichž kartu představení už hráč viděl (ukáže se jen poprvé). */
  seenIntros: string[];
  /** Kolik Panů Bramborů má hráč v zásobě (na začátku 2, další za přes 1000 kapek na konci úrovně). */
  potatoes: number;
}

const KEY = 'fast-food-fight:postup';

const DEFAULT: Progress = { unlockedLevel: 1, stars: {}, sound: true, seenIntros: [], potatoes: POTATO.startStock };

export function loadProgress(): Progress {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) return { ...DEFAULT, ...(JSON.parse(raw) as Partial<Progress>) };
  } catch {
    // bez uloženého postupu se hraje od začátku
  }
  return { ...DEFAULT, stars: {}, seenIntros: [] };
}

export function saveProgress(p: Progress): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(p));
  } catch {
    // uložení se nepovedlo; hra jede dál
  }
}

export function recordWin(p: Progress, level: number, stars: number): Progress {
  const key = String(level);
  return {
    ...p,
    unlockedLevel: Math.max(p.unlockedLevel, level + 1),
    stars: { ...p.stars, [key]: Math.max(p.stars[key] ?? 0, stars) },
  };
}
