import './ui/styles.css';
import { Game, type GameEvent } from './core/game';
import { loadProgress, recordWin, saveProgress } from './core/save';
import { LEVELS } from './data/levels';
import { POTATO } from './data/units';
import { T } from './data/texts.cs';
import { Stage } from './scene/stage';
import { View } from './scene/view';
import { Hud } from './ui/hud';
import { IntroCards } from './ui/intro';
import { Menus } from './ui/menus';
import { enterFullscreen, fullscreenSupported, isTouchDevice, runsAsApp } from './ui/fullscreen';
import { Screens } from './ui/screens';

const app = document.getElementById('app')!;
let progress = loadProgress();
/**
 * Hraje se úroveň z adresy (?uroven=2), pokud už je odemčená; jinak poslední odemčená.
 * Přechod na jinou úroveň znovu načte stránku s jinou adresou.
 */
const unlocked = Math.min(progress.unlockedLevel, LEVELS.length);
const asked = Number(new URLSearchParams(location.search).get('uroven'));
const level = LEVELS[(asked >= 1 && asked <= unlocked ? asked : unlocked) - 1];
const nextLevel = LEVELS.find((l) => l.id === level.id + 1);

function goToLevel(id: number): void {
  const url = new URL(location.href);
  url.searchParams.set('uroven', String(id));
  location.href = url.toString();
}

const game = new Game(level);
const stage = new Stage(app, level, game.slots);
const view = new View(stage, level);

let paused = false;
let endTimer = 0;

const hud = new Hud(app, {
  onPause: () => pause(),
  onNow: () => game.startNow(),
});
const menus = new Menus(app, game, stage, view);
menus.potatoStock = () => progress.potatoes;
menus.onPotato = (p) => {
  if (progress.potatoes <= 0 || !game.placePotato(p)) return;
  progress = { ...progress, potatoes: progress.potatoes - 1 };
  saveProgress(progress);
};
// Horní lišta už existuje: kamera změří její výšku a mapu umístí pod ni.
stage.resize();
const screens = new Screens(app);

// Představení nových postav (jen v úrovních, které to mají zapnuté, a každá postava jen poprvé).
const intros = new IntroCards(
  app,
  () => undefined,
  (type) => {
    if (progress.seenIntros.includes(type)) return;
    progress = { ...progress, seenIntros: [...progress.seenIntros, type] };
    saveProgress(progress);
  },
);
/** Pro kterou vlnu už se karty řešily. */
let introWave = -1;
const levelStart = performance.now();

/** Postavy, které přijdou poprvé ve vlně `wave`: nová zelenina a nový fast food. */
function newcomers(wave: number): string[] {
  if (!level.intros) return [];
  const veg = wave === 0 ? [...level.startDefenders] : level.unlocks.filter((u) => u.wave === wave).map((u) => u.type);
  const before = new Set(level.waves.slice(0, wave).flat().map((s) => s.type));
  const food = [...new Set(level.waves[wave]?.map((s) => s.type) ?? [])].filter((t) => !before.has(t));
  // Pan Brambora se představí na začátku první úrovně, kterou hráč s bramborami hraje.
  const potato = wave === 0 && progress.potatoes > 0 ? ['brambora'] : [];
  return [...veg, ...potato, ...food].filter((t) => !progress.seenIntros.includes(t));
}

/** V pauze před vlnou ukáže karty postav, které v ní přijdou poprvé. */
function checkIntros(): void {
  if (game.phase !== 'countdown' || game.waveIndex === introWave || paused) return;
  // Na začátku úrovně nechat nejdřív chvilku vidět nápis s názvem úrovně.
  if (game.waveIndex === 0 && performance.now() - levelStart < 1200) return;
  introWave = game.waveIndex;
  const list = newcomers(game.waveIndex);
  if (!list.length) return;
  menus.close();
  intros.show(list);
}
intros.preload(level.waves.map((_, i) => newcomers(i)).flat());

function pause(): void {
  if (paused || game.finished) return;
  paused = true;
  menus.close();
  showPauseScreen();
}

function showPauseScreen(): void {
  screens.show('pause', T.pause, [], [
    { text: `▶ ${T.resume}`, onClick: resume, primary: true },
    { text: `↺ ${T.restart}`, onClick: restart },
    {
      text: progress.sound ? `🔊 ${T.soundOn}` : `🔇 ${T.soundOff}`,
      onClick: () => {
        progress = { ...progress, sound: !progress.sound };
        saveProgress(progress);
        showPauseScreen();
      },
    },
    // Přepnutí na jinou odemčenou úroveň.
    ...LEVELS.filter((l) => l.id !== level.id && l.id <= progress.unlockedLevel).map((l) => ({
      text: `🗺️ ${T.nextLevel(l.id)}`,
      onClick: () => goToLevel(l.id),
    })),
  ]);
}

function resume(): void {
  paused = false;
  screens.hide();
}

function restart(): void {
  window.clearTimeout(endTimer);
  game.reset();
  view.reset();
  hud.reset();
  menus.close();
  screens.hide();
  paused = false;
  introWave = -1;
}

function handle(events: GameEvent[]): void {
  view.handleEvents(events, game);
  for (const e of events) {
    switch (e.type) {
      case 'flee': {
        const p = stage.toScreen(e.x, 0.8, e.z);
        hud.flyDrop(p.x, p.y, e.water);
        break;
      }
      case 'unlocked':
        hud.showBanner(T.newVeg(T.names[e.defender]), 2600);
        break;
      case 'waveStart':
        hud.showBanner(T.waveStart(e.wave + 1), 1200);
        break;
      case 'won':
        menus.close();
        progress = recordWin(progress, level.id, e.stars);
        // Přes 1000 kapek na konci úrovně: nový Pan Brambora (nejvýš 1 za úroveň).
        const newPotato = game.water > POTATO.rewardWater;
        if (newPotato) progress = { ...progress, potatoes: progress.potatoes + 1 };
        saveProgress(progress);
        endTimer = window.setTimeout(() => {
          const buttons = nextLevel
            ? [
                { text: `▶ ${T.nextLevel(nextLevel.id)}`, onClick: () => goToLevel(nextLevel.id), primary: true },
                { text: `↺ ${T.playAgain}`, onClick: restart },
              ]
            : [{ text: `↺ ${T.playAgain}`, onClick: restart, primary: true }];
          screens.show('won', T.winTitle, [], buttons);
          const stars = document.createElement('p');
          stars.className = 'stars';
          stars.textContent = '⭐'.repeat(e.stars) + '☆'.repeat(3 - e.stars);
          const unlocked = document.createElement('p');
          unlocked.textContent = nextLevel ? `🔓 ${T.levelTitle(nextLevel.id, nextLevel.name)}` : `🔓 ${T.nextLevelSoon}`;
          document.querySelector('.card h1')!.after(stars, unlocked);
          if (newPotato) {
            const reward = document.createElement('p');
            reward.className = 'potato-reward';
            const img = document.createElement('img');
            img.src = `${import.meta.env.BASE_URL}assets/postavy/brambora-radost.svg`;
            img.alt = '';
            reward.append(img, T.potatoReward);
            unlocked.after(reward);
          }
        }, 1500);
        break;
      case 'lost':
        menus.close();
        endTimer = window.setTimeout(() => {
          screens.show('lost', T.loseTitle, [T.loseHint], [{ text: `↺ ${T.tryAgain}`, onClick: restart, primary: true }]);
        }, 2200);
        break;
      default:
        break;
    }
  }
}

// Jedno ťuknutí / kliknutí na všechno; nic se netáhne a nic nezávisí na najetí myší.
stage.renderer.domElement.addEventListener('pointerdown', (ev) => {
  if (paused || intros.isOpen || game.finished) return;
  const p = stage.groundAt(ev.clientX, ev.clientY);
  if (!p) return;
  // Ťuknutí na zeleninu (velkorysý okruh kvůli dětským prstům) → vylepšení.
  const d = game.defenderNear(p, 0.7);
  if (d) {
    menus.openDefender(d.id);
    return;
  }
  // Druhé ťuknutí mimo otevřené menu ho jen zavře.
  if (menus.isOpen) {
    menus.close();
    return;
  }
  const place = game.checkPlace(p);
  // Ťuknutí na cestu: Pan Brambora, pokud nějakého hráč má.
  if (place === 'path' && progress.potatoes > 0 && game.checkPotato(p) === 'ok') {
    menus.openPotato(p);
    return;
  }
  if (place === 'ok') menus.openSpot(game.slotAt(p)!);
  else if (place !== 'outside') menus.showCross(p);
});

window.addEventListener('resize', () => menus.close());

// Na telefonu a tabletu se hra při prvním ťuknutí sama přepne na celou obrazovku
// (prohlížeč to dovolí jen po ťuknutí). Potom už jen tlačítkem v horní liště.
if (isTouchDevice && fullscreenSupported && !runsAsApp) {
  window.addEventListener('pointerdown', () => void enterFullscreen(), { once: true, capture: true });
}

// Hra se sama pozastaví, když se telefon přepne do jiné aplikace nebo zamkne.
document.addEventListener('visibilitychange', () => {
  if (document.hidden) pause();
});

// Hra je na šířku. Na telefonu na výšku je vidět jen prosba o otočení; hra mezitím stojí.
const portraitPhone = window.matchMedia('(orientation: portrait) and (pointer: coarse)');

let last = performance.now();
function frame(now: number): void {
  const dt = Math.min(0.1, (now - last) / 1000);
  last = now;
  checkIntros();
  if (!paused && !intros.isOpen && !portraitPhone.matches) {
    game.update(dt);
    handle(game.drainEvents());
    view.update(game, dt, now / 1000);
  }
  hud.update(game);
  menus.refresh();
  stage.render();
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);

// Na začátku krátce ukázat, která úroveň se hraje.
hud.showBanner(T.levelTitle(level.id, level.name), 2400);

// Pro automatické testy v prohlížeči.
(window as unknown as { __game: Game }).__game = game;
