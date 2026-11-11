/* BIOWANZE — service worker de la page publique.
   Le client, le 11/11/2026 : « rien ne doit être accessible sans
   connexion ». Il ne garde que ce qui est public (la page de connexion, les
   icônes, les images, les polices) ; l'application et l'horaire vivent dans
   le cache « biowanze-prive », que la page de connexion remplit après la
   connexion et efface à la déconnexion. Les anciens caches, qui
   contenaient l'application et l'horaire en clair, sont effacés. */
var V = "bw-public-2";
var CORE = ["./", "./index.html", "./manifest.webmanifest", "./logo-app.png", "./icon-192.png", "./icon-512.png",
            "./icon-maskable-512.png", "./apple-touch-icon.png", "./favicon.png"];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(V).then(function (c) { return c.addAll(CORE); })
    .then(function () { return self.skipWaiting(); }, function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (ks) {
    return Promise.all(ks.map(function (k) { return k === V || k === "biowanze-prive" ? null : caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener("fetch", function (e) {
  var r = e.request, u = new URL(r.url);
  if (r.method !== "GET" || u.origin !== location.origin) return;
  /* la page : le réseau d'abord, la copie hors ligne ensuite */
  if (r.mode === "navigate") {
    e.respondWith(fetch(r).then(function (res) {
      var c2 = res.clone(); caches.open(V).then(function (c) { c.put("./index.html", c2); }); return res;
    }, function () { return caches.match("./index.html"); }));
    return;
  }
  /* le reste (images, polices) : la copie d'abord, gardée à la volée */
  e.respondWith(caches.match(r).then(function (hit) {
    return hit || fetch(r).then(function (res) {
      if (res.ok) { var c2 = res.clone(); caches.open(V).then(function (c) { c.put(r, c2); }); }
      return res;
    });
  }));
});

/* les notifications, reprises telles quelles de sw.js de l'application */
self.addEventListener("push", function (e) {
  var d = {};
  try { d = e.data ? e.data.json() : {}; } catch (err) { d = { body: e.data ? e.data.text() : "" }; }
  e.waitUntil(self.registration.showNotification(d.title || "Horaire mis à jour", {
    body: d.body || "", icon: "icon-192.png", badge: "favicon.png",
    tag: d.tag || "classeur", renotify: true, data: { url: d.url || "./" }
  }));
});

self.addEventListener("notificationclick", function (e) {
  e.notification.close();
  var cible = new URL((e.notification.data && e.notification.data.url) || "./", self.registration.scope).href;
  e.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(function (l) {
    var vue = (cible.match(/[?&]vue=([a-z]+)/) || [])[1];
    for (var i = 0; i < l.length; i++) if ("focus" in l[i]) {
      if (vue) l[i].postMessage({ type: "vue", vue: vue });
      return l[i].focus();
    }
    return self.clients.openWindow ? self.clients.openWindow(cible) : null;
  }));
});
