import { T } from '../data/texts.cs';
import { button, el } from './dom';

export interface ScreenButton {
  text: string;
  onClick: () => void;
  primary?: boolean;
}

/** Celoobrazovkové okno: pauza, výhra, prohra. */
export class Screens {
  private readonly overlay: HTMLElement;
  private readonly card: HTMLElement;

  constructor(parent: HTMLElement) {
    this.overlay = el('div', 'overlay');
    this.card = el('div', 'card');
    this.overlay.append(this.card);
    parent.append(this.overlay);

    const rotate = el('div', 'rotate', `📱↻ ${T.rotate}`);
    parent.append(rotate);
  }

  get isOpen(): boolean {
    return this.overlay.classList.contains('show');
  }

  show(kind: 'pause' | 'won' | 'lost', title: string, lines: string[], buttons: ScreenButton[]): void {
    this.card.className = `card ${kind}`;
    this.card.replaceChildren(el('h1', '', title));
    for (const line of lines) this.card.append(el('p', '', line));
    const row = el('div', 'buttons');
    for (const b of buttons) row.append(button(b.primary ? 'big primary' : 'big', b.text, b.onClick));
    this.card.append(row);
    this.overlay.classList.add('show');
  }

  hide(): void {
    this.overlay.classList.remove('show');
  }
}
