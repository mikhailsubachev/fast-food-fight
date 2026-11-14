// Celá obrazovka pro mobily. Android a iPad umí Fullscreen API (a na Androidu i zamknout
// otočení na šířku). iPhone ho pro stránky nemá: tam se hra spustí přes celou obrazovku
// jen po „Přidat na plochu“ (viz manifest.webmanifest a meta značky v index.html).

type FsDocument = Document & {
  webkitFullscreenEnabled?: boolean;
  webkitFullscreenElement?: Element | null;
  webkitExitFullscreen?: () => Promise<void>;
};
type FsElement = HTMLElement & { webkitRequestFullscreen?: () => Promise<void> };

const doc = document as FsDocument;

/** Prohlížeč umí přepnout stránku na celou obrazovku. */
export const fullscreenSupported = !!(doc.fullscreenEnabled || doc.webkitFullscreenEnabled);

/** Hra běží jako aplikace z plochy (už je přes celou obrazovku). */
export const runsAsApp =
  window.matchMedia('(display-mode: fullscreen), (display-mode: standalone)').matches ||
  (navigator as Navigator & { standalone?: boolean }).standalone === true;

/** iPhone / iPod: celá obrazovka jen přes „Přidat na plochu“. */
export const isIPhone = /iPhone|iPod/.test(navigator.userAgent);

export const isTouchDevice = window.matchMedia('(pointer: coarse)').matches;

export function isFullscreen(): boolean {
  return !!(doc.fullscreenElement || doc.webkitFullscreenElement);
}

export async function enterFullscreen(): Promise<void> {
  if (isFullscreen()) return;
  const root = document.documentElement as FsElement;
  try {
    if (root.requestFullscreen) await root.requestFullscreen({ navigationUI: 'hide' });
    else await root.webkitRequestFullscreen?.();
  } catch {
    return;
  }
  // Na šířku zamknout jde jen v režimu celé obrazovky a jen někde (Android Chrome).
  try {
    await (screen.orientation as ScreenOrientation & { lock?: (o: string) => Promise<void> }).lock?.('landscape');
  } catch {
    /* nepodporováno */
  }
}

export async function exitFullscreen(): Promise<void> {
  try {
    if (doc.exitFullscreen && doc.fullscreenElement) await doc.exitFullscreen();
    else if (doc.webkitFullscreenElement) await doc.webkitExitFullscreen?.();
  } catch {
    /* nic */
  }
}

export function onFullscreenChange(cb: () => void): void {
  document.addEventListener('fullscreenchange', cb);
  document.addEventListener('webkitfullscreenchange', cb);
}
