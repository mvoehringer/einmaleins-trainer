// Minimaler Offline-Cache: die App ist eine Datei plus Icon.
// Bei jeder neuen Version den Namen hochzählen, dann räumt activate den alten Stand ab.
const CACHE = 'hedi-1';
const FILES = ['./', './index.html', './icon.png', './manifest.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// Netz zuerst, Cache als Rückfall — so ist eine neue Version sofort da,
// und ohne Verbindung läuft die letzte weiter.
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then(r => {
        const copy = r.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {});
        return r;
      })
      .catch(() => caches.match(e.request).then(r => r || caches.match('./index.html')))
  );
});
