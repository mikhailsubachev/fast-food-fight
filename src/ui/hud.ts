import type { Game } from '../core/game';
import { T } from '../data/texts.cs';
import { MOUTH_LIVES } from '../data/units';
import { button, el, replayAnimation } from './dom';
import { DROP_SVG, TOOTH_SVG, iconEl } from './icons';
import {
  enterFullscreen,
  exitFullscreen,
  fullscreenSupported,
  isFullscreen,
  isIPhone,
  onFullscreenChange,
  runsAsApp,
} from './fullscreen';

/** Čtyři rohy: přepnutí na celou obrazovku (při zapnutí se rohy otočí dovnitř přes CSS). */
const FULLSCREEN_ICON =
  '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>';

/** Horní lišta (voda, zoubky, vlna, pauza), odpočet do vlny, nápisy a létající kapky vody. */
export class Hud {
  private readonly waterPill: HTMLElement;
  private readonly waterValue: HTMLElement;
  private readonly teeth: HTMLElement[] = [];
  private readonly waveLabel: HTMLElement;
  private readonly countdown: HTMLElement;
  private readonly countdownText: HTMLElement;
  private readonly banner: HTMLElement;
  private bannerTimer = 0;
  /** Voda, která už patří hráči, ale kapka ještě letí do počítadla. */
  private pendingWater = 0;
  private shownBites = 0;

  constructor(
    private readonly parent: HTMLElement,
    handlers: { onPause: () => void; onNow: () => void },
  ) {
    const bar = el('div', 'hud');
    this.waterPill = el('div', 'pill water');
    this.waterPill.append(iconEl('icon', DROP_SVG));
    this.waterValue = el('span', 'value', '0');
    this.waterPill.append(this.waterValue);

    const mid = el('div', 'hud-mid');
    const teeth = el('div', 'pill teeth');
    for (let i = 0; i < MOUTH_LIVES; i++) {
      const t = iconEl('tooth', TOOTH_SVG);
      teeth.append(t);
      this.teeth.push(t);
    }
    this.waveLabel = el('div', 'pill wave', '');
    // Odpočet je v horní liště místo čísla vlny, aby nezakrýval mapu.
    this.countdown = el('div', 'countdown');
    this.countdownText = el('span', '', '');
    this.countdown.append(this.countdownText, button('big now', T.now + ' ▶', handlers.onNow));
    mid.append(teeth, this.waveLabel, this.countdown);

    const pause = button('round pause', '⏸', handlers.onPause);
    pause.setAttribute('aria-label', T.pause);
    const right = el('div', 'hud-right');
    // Tlačítko celé obrazovky: kde to prohlížeč umí, nebo na iPhonu s radou „Přidat na plochu“.
    if (!runsAsApp && (fullscreenSupported || isIPhone)) {
      const fs = button('round fullscreen', '', () => {
        if (!fullscreenSupported) this.showBanner(T.fullscreenIPhone, 4000);
        else if (isFullscreen()) void exitFullscreen();
        else void enterFullscreen();
      });
      fs.innerHTML = FULLSCREEN_ICON;
      fs.setAttribute('aria-label', T.fullscreen);
      onFullscreenChange(() => fs.classList.toggle('on', isFullscreen()));
      right.append(fs);
    }
    right.append(pause);
    bar.append(this.waterPill, mid, right);

    this.banner = el('div', 'banner');
    parent.append(bar, this.banner);
  }

  update(game: Game): void {
    this.waterValue.textContent = String(Math.max(0, game.water - this.pendingWater));
    this.waveLabel.textContent = T.wave(game.waveIndex + 1, game.waveCount);
    this.teeth.forEach((t, i) => t.classList.toggle('lost', i >= MOUTH_LIVES - game.bites));
    if (game.bites !== this.shownBites) {
      if (game.bites > this.shownBites) replayAnimation(this.teeth[0].parentElement!, 'shake');
      this.shownBites = game.bites;
    }

    const counting = game.phase === 'countdown';
    this.countdown.classList.toggle('show', counting);
    this.waveLabel.classList.toggle('hidden', counting);
    if (counting) this.countdownText.textContent = T.nextWaveIn(game.waveIndex + 1, Math.ceil(game.countdown));
  }

  showBanner(text: string, ms = 1800): void {
    this.banner.textContent = text;
    replayAnimation(this.banner, 'show');
    window.clearTimeout(this.bannerTimer);
    this.bannerTimer = window.setTimeout(() => this.banner.classList.remove('show'), ms);
  }

  /** Kapka vyskočí z utíkajícího fast foodu a obloukem odletí do počítadla vody. */
  flyDrop(x: number, y: number, amount: number): void {
    this.pendingWater += amount;
    const drop = el('div', 'drop');
    drop.innerHTML = DROP_SVG;
    drop.style.left = `${x}px`;
    drop.style.top = `${y}px`;
    this.parent.append(drop);

    const target = this.waterPill.getBoundingClientRect();
    const dx = target.left + 22 - x;
    const dy = target.top + target.height / 2 - y;
    const anim = drop.animate(
      [
        { transform: 'translate(-50%, -50%) scale(0.4)' },
        { transform: 'translate(-50%, -150%) scale(1.3)', offset: 0.25 },
        { transform: 'translate(-50%, -150%) scale(1.1) rotate(-10deg)', offset: 0.4 },
        { transform: `translate(calc(-50% + ${dx * 0.5}px), calc(-50% + ${dy * 0.5 - 80}px)) scale(1)`, offset: 0.7 },
        { transform: `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px)) scale(0.6)` },
      ],
      { duration: 1100, easing: 'ease-in-out' },
    );
    anim.onfinish = () => {
      drop.remove();
      this.pendingWater = Math.max(0, this.pendingWater - amount);
      replayAnimation(this.waterPill, 'bump');
    };
  }

  reset(): void {
    this.pendingWater = 0;
    this.shownBites = 0;
    this.parent.querySelectorAll('.drop').forEach((d) => d.remove());
    this.banner.classList.remove('show');
  }
}
