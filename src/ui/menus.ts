import type { Game } from '../core/game';
import type { Vec2 } from '../core/types';
import { T } from '../data/texts.cs';
import { DEFENDERS, type DefenderType } from '../data/units';
import { defenderLevel } from '../entities/obranci/defender';
import type { Stage } from '../scene/stage';
import type { View } from '../scene/view';
import { button, el } from './dom';

const ICONS: Record<DefenderType, string> = { mrkev: '🥕', porek: '🌿' };
const ORDER: DefenderType[] = ['mrkev', 'porek'];

/**
 * Kruhové menu nad místem na záhoně.
 * Volné místo: 1. ťuknutí na zeleninu ukáže její dosah, 2. ťuknutí ji zasadí.
 * Zasazená zelenina: ukáže dosah a tlačítko Vylepšit.
 */
export class Menus {
  private readonly root: HTMLElement;
  private readonly parent: HTMLElement;
  private spot: Vec2 | null = null;
  private defenderId: number | null = null;
  private selected: DefenderType | null = null;
  private vegButtons = new Map<DefenderType, HTMLButtonElement>();
  private upgradeButton: HTMLButtonElement | null = null;

  constructor(
    parent: HTMLElement,
    private readonly game: Game,
    private readonly stage: Stage,
    private readonly view: View,
  ) {
    this.parent = parent;
    this.root = el('div', 'slot-menu');
    parent.append(this.root);
  }

  get isOpen(): boolean {
    return this.spot !== null || this.defenderId !== null;
  }

  /** Menu pro sázení na volné místo. */
  openSpot(p: Vec2): void {
    this.close();
    this.spot = p;
    this.view.showSpot(p.x, p.z);
    this.buildPlant();
    this.show(p);
  }

  /** Menu pro zasazenou zeleninu. */
  openDefender(id: number): void {
    this.close();
    const d = this.game.defenders.find((x) => x.id === id);
    if (!d) return;
    this.defenderId = id;
    this.view.showRange(d.x, d.z, defenderLevel(d).range, d.type);
    this.buildUpgrade(id);
    this.show(d);
  }

  close(): void {
    this.spot = null;
    this.defenderId = null;
    this.selected = null;
    this.vegButtons.clear();
    this.upgradeButton = null;
    this.root.replaceChildren();
    this.root.classList.remove('show');
    this.view.hideRange();
    this.view.hideSpot();
  }

  /** Krátký červený křížek tam, kde sázet nejde. */
  showCross(p: Vec2): void {
    const s = this.stage.toScreen(p.x, 0, p.z);
    const cross = el('div', 'no-plant');
    cross.style.left = `${s.x}px`;
    cross.style.top = `${s.y}px`;
    this.parent.append(cross);
    cross.addEventListener('animationend', () => cross.remove());
  }

  /** Volá se každý snímek: přizpůsobí tlačítka aktuální vodě. */
  refresh(): void {
    if (this.spot) {
      for (const [type, b] of this.vegButtons) {
        const check = this.game.checkPlant(this.spot, type);
        b.classList.toggle('disabled', check !== 'ok');
        b.classList.toggle('locked', check === 'locked');
        b.classList.toggle('selected', this.selected === type);
      }
      // Místo mohla mezitím zabrat jiná zelenina (nebo skončila hra).
      if (this.game.checkPlace(this.spot) !== 'ok' || this.game.finished) this.close();
    }
    if (this.upgradeButton && this.defenderId !== null) {
      const d = this.game.defenders.find((x) => x.id === this.defenderId);
      const cost = d ? this.game.upgradeCost(d) : null;
      this.upgradeButton.classList.toggle('disabled', cost === null || this.game.water < cost);
    }
  }

  private buildPlant(): void {
    const row = el('div', 'menu-row');
    for (const type of ORDER) {
      const b = button('veg', '', () => this.onVeg(type));
      const locked = !this.game.unlocked.has(type);
      b.append(el('span', 'icon', locked ? '🔒' : ICONS[type]));
      if (!locked) b.append(el('span', 'price', `${DEFENDERS[type].cost}`));
      b.append(el('span', 'check', '✓'));
      b.setAttribute('aria-label', locked ? T.locked : T.names[type]);
      this.vegButtons.set(type, b);
      row.append(b);
    }
    this.root.append(row);
  }

  private onVeg(type: DefenderType): void {
    if (!this.spot) return;
    const check = this.game.checkPlant(this.spot, type);
    if (check === 'locked') return;
    if (this.selected === type && check === 'ok') {
      this.game.plant(this.spot, type);
      this.close();
      return;
    }
    this.selected = type;
    this.view.showRange(this.spot.x, this.spot.z, DEFENDERS[type].levels[0].range, type);
    this.refresh();
  }

  private buildUpgrade(defenderId: number): void {
    const d = this.game.defenders.find((x) => x.id === defenderId)!;
    const cost = this.game.upgradeCost(d);
    const row = el('div', 'menu-row');
    if (cost === null) {
      row.append(el('div', 'pill maxed', `⭐ ${T.maxLevel}`));
    } else {
      const b = button('big upgrade', `⭐ ${T.upgrade}  ${cost} 💧`, () => {
        if (this.game.upgrade(defenderId)) this.close();
      });
      this.upgradeButton = b;
      row.append(b);
    }
    this.root.append(row);
  }

  /** Menu nad místem, ale vždy celé na obrazovce. */
  private show(p: Vec2): void {
    this.root.classList.add('show');
    const s = this.stage.toScreen(p.x, 0, p.z);
    const w = this.root.offsetWidth || 180;
    const h = this.root.offsetHeight || 96;
    const x = Math.min(window.innerWidth - w / 2 - 8, Math.max(w / 2 + 8, s.x));
    let y = s.y - 34 - h;
    if (y < 72) y = s.y + 34;
    this.root.style.left = `${x}px`;
    this.root.style.top = `${y}px`;
    this.refresh();
  }
}
