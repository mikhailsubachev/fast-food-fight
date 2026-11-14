import './ui/styles.css';
import { Game, type GameEvent } from './core/game';
import { loadProgress, recordWin, saveProgress } from './core/save';
import { LEVEL1 } from './data/level1';
import { T } from './data/texts.cs';
import { Stage } from './scene/stage';
import { View } from './scene/view';
import { Hud } from './ui/hud';
import { Menus } from './ui/menus';
import { Screens } from './ui/screens';

const app = document.getElementById('app')!;
const level = LEVEL1;
const game = new Game(level);
const stage = new Stage(app, level);
const view = new View(stage, level);
let progress = loadProgress();

let paused = false;
let endTimer = 0;

const hud = new Hud(app, {
  onPause: () => pause(),
  onNow: () => game.startNow(),
});
const menus = new Menus(app, game, stage, view);
const screens = new Screens(app);

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
}

function handle(events: GameEvent[]): void {
  view.handleEvents(events);
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
        saveProgress(progress);
        endTimer = window.setTimeout(() => {
          screens.show('won', T.winTitle, [], [{ text: `↺ ${T.playAgain}`, onClick: restart, primary: true }]);
          const stars = document.createElement('p');
          stars.className = 'stars';
          stars.textContent = '⭐'.repeat(e.stars) + '☆'.repeat(3 - e.stars);
          const unlocked = document.createElement('p');
          unlocked.textContent = `🔓 ${T.nextLevelSoon}`;
          document.querySelector('.card h1')!.after(stars, unlocked);
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
  if (paused || game.finished) return;
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
  if (place === 'ok') menus.openSpot(p);
  else if (place !== 'outside') menus.showCross(p);
});

window.addEventListener('resize', () => menus.close());

// Hra se sama pozastaví, když se telefon přepne do jiné aplikace nebo zamkne.
document.addEventListener('visibilitychange', () => {
  if (document.hidden) pause();
});

// Na telefonu na výšku je vidět jen prosba o otočení; hra mezitím stojí.
const portraitPhone = window.matchMedia('(orientation: portrait) and (pointer: coarse)');

let last = performance.now();
function frame(now: number): void {
  const dt = Math.min(0.1, (now - last) / 1000);
  last = now;
  if (!paused && !portraitPhone.matches) {
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

// Pro automatické testy v prohlížeči.
(window as unknown as { __game: Game }).__game = game;
