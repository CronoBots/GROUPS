/* BIOWANZE — service worker */
var V = "nfdm-v54";
var CORE = ["./", "./index.html", "./manifest.webmanifest",
            "./icon-192.png", "./icon-512.png", "./icon-maskable-512.png",
            "./apple-touch-icon.png", "./favicon.png"];
/* data/horaire-2026.json (~290 Ko) est volontairement absent d'ici : il est mis en
   cache à la demande par le handler fetch ci-dessous, seulement pour qui utilise
   le pré-remplissage, plutôt que de ralentir l'installation pour tout le monde. */

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(V).then(function (c) { return c.addAll(CORE); })
      .then(function () { return self.skipWaiting(); })
      .catch(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (ks) {
      return Promise.all(ks.map(function (k) { return k === V ? null : caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  var sameOrigin = url.origin === self.location.origin;
  var isFont = url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com";
  if (!sameOrigin && !isFont) return;

  e.respondWith(
    caches.match(req).then(function (hit) {
      if (hit) return hit;
      return fetch(req).then(function (res) {
        var copy = res.clone();
        caches.open(V).then(function (c) { try { c.put(req, copy); } catch (err) {} });
        return res;
      }).catch(function () {
        return req.mode === "navigate" ? caches.match("./index.html") : Response.error();
      });
    })
  );
});
