// Všechny texty hry na jednom místě, aby se daly později přeložit nebo namluvit.
import type { AttackerType, DefenderType } from './units';

export const T = {
  names: {
    mrkev: 'Mrkev',
    porek: 'Pórek',
    hamburger: 'Hamburger',
    hranolky: 'Hranolky',
    velkyHamburger: 'Velký hamburger',
  } satisfies Record<DefenderType | AttackerType, string>,
  wave: (n: number, total: number) => `Vlna ${n}/${total}`,
  nextWaveIn: (n: number, seconds: number) => `Vlna ${n} za ${seconds}`,
  now: 'Hned!',
  waveStart: (n: number) => `Vlna ${n}!`,
  newVeg: (name: string) => `Nová zelenina: ${name}!`,
  locked: 'Zatím zamčeno',
  upgrade: 'Vylepšit',
  maxLevel: 'Nejlepší',
  pause: 'Pauza',
  resume: 'Pokračovat',
  restart: 'Začít znovu',
  soundOn: 'Zvuk: zapnutý',
  soundOff: 'Zvuk: vypnutý',
  winTitle: 'Hurá! Zelenina vyhrála!',
  nextLevelSoon: 'Úroveň 2 – brzy!',
  playAgain: 'Hrát znovu',
  loseTitle: 'Bléééé! Puse je špatně.',
  loseHint: 'Zasaď víc zeleniny u cesty.',
  tryAgain: 'Zkusit znovu',
  rotate: 'Otoč telefon na šířku',
};
