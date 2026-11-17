import { el } from './dom';

/** Karta z generátoru návrhů má 1380 × 740 px; s přesahem stuhy a stínem kolem 1400 × 800. */
const CARD_W = 1400;
const CARD_H = 800;

/**
 * Představení nové postavy: karta s animací (Nová zelenina! / Pozor, nový fast food!), která se
 * ukáže v pauze před vlnou, ve které postava přijde poprvé. Karty vytváří generátor návrhů
 * (design/generator/gen_predstaveni.py) do public/assets/predstaveni/<typ>.html; tady se vloží
 * do stínového DOM, aby se jejich styly nepletly se zbytkem hry. Hra mezitím stojí.
 */
export class IntroCards {
  private readonly overlay: HTMLElement;
  private readonly scaler: HTMLElement;
  private readonly root: ShadowRoot;
  private readonly cache = new Map<string, Promise<string>>();
  private queue: string[] = [];
  private open = false;

  constructor(
    parent: HTMLElement,
    /** Zavolá se po zavření poslední karty z fronty. */
    private readonly onDone: () => void,
    /** Zavolá se pro každou kartu, kterou hráč viděl. */
    private readonly onSeen: (type: string) => void,
  ) {
    this.overlay = el('div', 'intro');
    this.overlay.setAttribute('role', 'dialog');
    this.overlay.setAttribute('aria-modal', 'true');
    this.scaler = el('div', 'intro-card');
    this.root = this.scaler.attachShadow({ mode: 'open' });
    this.overlay.append(this.scaler);
    parent.append(this.overlay);
    window.addEventListener('resize', () => this.fit());
  }

  get isOpen(): boolean {
    return this.open;
  }

  /** Načte karty dopředu, aby se pak ukázaly hned. */
  preload(types: string[]): void {
    for (const t of types) void this.load(t);
  }

  show(types: string[]): void {
    if (!types.length) return;
    this.queue.push(...types);
    if (!this.open) void this.next();
  }

  private load(type: string): Promise<string> {
    let p = this.cache.get(type);
    if (!p) {
      p = fetch(`${import.meta.env.BASE_URL}assets/predstaveni/${type}.html`).then((r) => (r.ok ? r.text() : ''));
      this.cache.set(type, p);
    }
    return p;
  }

  private async next(): Promise<void> {
    const type = this.queue.shift();
    if (!type) {
      this.open = false;
      this.overlay.classList.remove('show');
      this.onDone();
      return;
    }
    this.open = true;
    const html = await this.load(type).catch(() => '');
    if (!html) {
      // Karta se nenačetla (třeba bez připojení): hra pokračuje bez ní.
      void this.next();
      return;
    }
    this.root.innerHTML = html;
    const btn = this.root.querySelector<HTMLButtonElement>('.btn');
    btn?.addEventListener('click', () => {
      this.onSeen(type);
      void this.next();
    });
    this.fit();
    this.overlay.classList.add('show');
    btn?.focus({ preventScroll: true });
  }

  /** Karta se zmenší, aby se vešla na obrazovku (i na telefon naležato). */
  private fit(): void {
    const s = Math.min((window.innerWidth * 0.96) / CARD_W, (window.innerHeight * 0.94) / CARD_H, 1);
    this.scaler.style.transform = `scale(${s})`;
  }
}
