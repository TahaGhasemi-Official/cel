/* VOLTEX service worker – makes the app installable and fully offline.
   Precaches the whole app (UI, Python engine, Pyodide runtime, fonts, icons) on first visit. */
const BUILD_ID = "a44021566ea9";
const CACHE = "voltex-" + BUILD_ID;
const PRECACHE = ["./", "app.js", "engine.worker.js", "engine/voltex-engine.zip", "fonts/Vazirmatn-Bold.ttf", "fonts/Vazirmatn-Regular.ttf", "icons/apple-touch-icon.png", "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png", "index.html", "login.json", "manifest.webmanifest", "pyodide/pyodide-lock.json", "pyodide/pyodide.asm.mjs", "pyodide/pyodide.asm.wasm", "pyodide/pyodide.mjs", "pyodide/python_stdlib.zip", "styles.css"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(PRECACHE.map((p) => new Request(p, { cache: "reload" }))))
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith("voltex-") && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") self.skipWaiting();
});

function isSameOrigin(url) {
  return url.origin === self.location.origin;
}

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (!isSameOrigin(url)) return;

  // Accounts file: prefer the latest copy, fall back to the cached one when offline.
  if (url.pathname.endsWith("/login.json")) {
    event.respondWith(
      fetch(req).then((res) => {
        if (res.ok) caches.open(CACHE).then((c) => c.put(req, res.clone()));
        return res;
      }).catch(() => caches.match(req, { ignoreSearch: true }))
    );
    return;
  }

  // App pages (navigations) always resolve to the app shell.
  if (req.mode === "navigate") {
    event.respondWith(
      caches.match("index.html").then((hit) => hit || fetch(req))
    );
    return;
  }

  // Everything else: cache first, then network (and remember the result).
  event.respondWith(
    caches.match(req, { ignoreSearch: true }).then((hit) => {
      if (hit) return hit;
      return fetch(req).then((res) => {
        if (res.ok && res.type === "basic") {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      });
    })
  );
});
