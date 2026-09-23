/* BIOWANZE — service worker */
var V = "nfdm-v192";
var CORE = ["./", "./index.html", "./manifest.webmanifest", "./logo.svg",
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

/* TROIS STRATÉGIES, et pas une seule.

   Tout était en cache d'abord, y compris la page. Conséquence : une version
   poussée n'arrivait sur l'appareil qu'au DEUXIÈME lancement — le premier
   installait le nouveau service worker, le second servait enfin la nouvelle
   page. Le client, le 21/09/2026 : « tout est sur main car je ne vois pas
   encore en ligne ? » Il avait raison de douter : la page était en ligne, et
   son téléphone lui montrait l'ancienne.

   - La PAGE : le réseau d'abord, le cache s'il ne répond pas. Une seconde de
     plus au démarrage quand la connexion traîne, et la version du jour à
     coup sûr. Hors ligne, le cache reprend la main sans que rien ne change.
   - L'HORAIRE : le cache d'abord pour ne pas attendre 290 Ko, mais une
     relecture réseau en arrière-plan qui met le cache à jour pour la fois
     suivante.
   - LE RESTE — icônes, polices : le cache d'abord. Elles ne changent pas. */
function reseauPuisCache(req) {
  return fetch(req).then(function (res) {
    var copy = res.clone();
    caches.open(V).then(function (c) { try { c.put(req, copy); } catch (err) {} });
    return res;
  }).catch(function () {
    return caches.match(req).then(function (hit) {
      return hit || caches.match("./index.html").then(function (h2) {
        return h2 || Response.error();
      });
    });
  });
}
self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  var sameOrigin = url.origin === self.location.origin;
  var isFont = url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com";
  if (!sameOrigin && !isFont) return;

  if (req.mode === "navigate" || /\/(index\.html)?$/.test(url.pathname)
      || /\.(html|webmanifest)$/.test(url.pathname)) {
    e.respondWith(reseauPuisCache(req));
    return;
  }

  e.respondWith(
    caches.match(req).then(function (hit) {
      if (hit) {
        /* l'horaire se rafraîchit derrière, sans faire attendre personne */
        if (/\.json$/.test(url.pathname)) {
          fetch(req).then(function (res) {
            caches.open(V).then(function (c) { try { c.put(req, res); } catch (err) {} });
          }).catch(function () {});
        }
        return hit;
      }
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
