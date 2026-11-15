// Ikony lišty a menu jako vlastní obrázky (z návrhu úrovně, design/generator/gen_level.py).
// Emoji vypadají v každém systému jinak (např. ve Windows), tyhle všude stejně.
import type { DefenderType } from '../data/units';

export const DROP_SVG =
  '<svg class="ico-drop" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2 C12 2 4.5 11 4.5 15.5 A7.5 7.5 0 0 0 19.5 15.5 C19.5 11 12 2 12 2 Z" fill="#3D9BE0" stroke="#2B2118" stroke-width="1.8"/><path d="M8.5 15 Q8.5 11.5 10.5 9" stroke="#CDEBFF" stroke-width="1.6" fill="none" stroke-linecap="round"/></svg>';

export const TOOTH_SVG =
  '<svg class="ico-tooth" viewBox="0 0 30 34" aria-hidden="true"><path d="M4 6 Q4 2 9 2 Q15 4 21 2 Q26 2 26 6 Q27 16 23 30 Q21 34 19 28 L17 20 Q15 17 13 20 L11 28 Q9 34 7 30 Q3 16 4 6 Z" fill="#FFFFFF" stroke="#2B2118" stroke-width="2.4" stroke-linejoin="round"/></svg>';

export const LOCK_SVG =
  '<svg class="ico-lock" viewBox="0 0 24 24" aria-hidden="true"><path d="M7.5 11 V8 A4.5 4.5 0 0 1 16.5 8 V11" fill="none" stroke="#2B2118" stroke-width="2.6"/><rect x="4.5" y="10.5" width="15" height="11" rx="2.5" fill="#FFC93C" stroke="#2B2118" stroke-width="2"/><circle cx="12" cy="15.5" r="1.7" fill="#2B2118"/></svg>';

/** Zmenšená postavička zeleniny tak, jak stojí ve hře. */
export function vegImage(type: DefenderType): HTMLImageElement {
  const img = document.createElement('img');
  img.className = 'ico-veg';
  img.src = `${import.meta.env.BASE_URL}assets/postavy/${type}-klid.svg`;
  img.alt = '';
  img.draggable = false;
  return img;
}

/** Prvek s HTML ikonou (obrázek SVG z tohoto souboru). */
export function iconEl(className: string, svg: string): HTMLSpanElement {
  const s = document.createElement('span');
  s.className = className;
  s.innerHTML = svg;
  return s;
}
