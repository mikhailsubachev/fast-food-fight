import type { Game } from '../core/game';
import { T } from '../data/texts.cs';
import { DEFENDERS, type DefenderType } from '../data/units';
import { defenderLevel } from '../entities/obranci/defender';
import type { View } from '../scene/view';
import { button, el } from './dom';

const ICONS: Record<DefenderType, string> = { mrkev: '🥕', porek: '🌿' };
const ORDER: DefenderType[] = ['mrkev', 'porek'];

/**
 * Kruhové menu nad políčkem.
 * Prázdné políčko: 1. ťuknutí na zeleninu ukáže její dosah, 2. ťuknutí ji zasadí.
 * Zasazená zelenina: ukáže dosah a tlačítko Vylepšit.
 */
export class Menus {
  private readonly root: HTMLElement;
  private slot: number | null = null;
  private selected: DefenderType | null = null;
  private vegButtons = new Map<DefenderType, HTMLButtonElement>();
  private upgradeButton: HTMLButtonElement | null = null;

  constructor(
    parent: HTMLElement,
    private readonly game: Game,
    private readonly view: View,
  ) {
    this.root = el('div', 'slot-menu');
    parent.append(this.root);
  }

  get isOpen(): boolean {
    return this.slot !== null;
  }

  open(slot: number): void {
    this.close();
    this.slot = slot;
    this.view.highlightSlot(slot);
    const defender = this.game.defenderAt(slot);
    if (defender) this.buildUpgrade(defender.id);
    else this.buildPlant();
    this.root.classList.add('show');
    this.position();
    this.refresh();
  }

  close(): void {
    this.slot = null;
    this.selected = null;
    this.vegButtons.clear();
    this.upgradeButton = null;
    this.root.replaceChildren();
    this.root.classList.remove('show');
    this.view.hideRange();
    this.view.highlightSlot(null);
  }

  /** Volá se každý snímek: přizpůsobí tlačítka aktuální vodě. */
  refresh(): void {
    if (this.slot === null) return;
    for (const [type, b] of this.vegButtons) {
      const check = this.game.checkPlant(this.slot, type);
      b.classList.toggle('disabled', check !== 'ok');
      b.classList.toggle('locked', check === 'locked');
      b.classList.toggle('selected', this.selected === type);
    }
    if (this.upgradeButton) {
      const d = this.game.defenderAt(this.slot);
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
      b.append(el('span', 'price', locked ? '' : `${DEFENDERS[type].cost} 💧`));
      b.append(el('span', 'check', '✓'));
      b.setAttribute('aria-label', locked ? T.locked : T.names[type]);
      this.vegButtons.set(type, b);
      row.append(b);
    }
    this.root.append(row);
  }

  private onVeg(type: DefenderType): void {
    if (this.slot === null) return;
    const check = this.game.checkPlant(this.slot, type);
    if (check === 'locked') return;
    if (this.selected === type && check === 'ok') {
      this.game.plant(this.slot, type);
      this.close();
      return;
    }
    this.selected = type;
    const s = this.game.level.slots[this.slot];
    this.view.showRange(s.x, s.z, DEFENDERS[type].levels[0].range);
    this.refresh();
  }

  private buildUpgrade(defenderId: number): void {
    const d = this.game.defenders.find((x) => x.id === defenderId)!;
    this.view.showRange(d.x, d.z, defenderLevel(d).range);
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

  /** Menu nad políčkem, ale vždy celé na obrazovce. */
  private position(): void {
    if (this.slot === null) return;
    const p = this.view.slotOnScreen(this.slot);
    const w = this.root.offsetWidth || 180;
    const h = this.root.offsetHeight || 96;
    const x = Math.min(window.innerWidth - w / 2 - 8, Math.max(w / 2 + 8, p.x));
    let y = p.y - 40 - h;
    if (y < 72) y = p.y + 40;
    this.root.style.left = `${x}px`;
    this.root.style.top = `${y}px`;
  }
}
