export function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className = '',
  text = '',
): HTMLElementTagNameMap[K] {
  const e = document.createElement(tag);
  if (className) e.className = className;
  if (text) e.textContent = text;
  return e;
}

export function button(className: string, text: string, onClick: () => void): HTMLButtonElement {
  const b = el('button', className, text);
  b.type = 'button';
  b.addEventListener('click', (ev) => {
    ev.stopPropagation();
    onClick();
  });
  return b;
}

/** Restartuje CSS animaci (např. poskočení počítadla). */
export function replayAnimation(e: HTMLElement, className: string): void {
  e.classList.remove(className);
  void e.offsetWidth;
  e.classList.add(className);
}
