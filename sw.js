/* BIOWANZE — service worker */
var V = "nfdm-v211";
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
/* ON NE MET EN CACHE QUE CE QUI EST BON, et cette garde manquait.

   Le 23/09/2026, l'onglet « Mon salaire » du client s'est vidé : 0 journée
   sur 30, zéro heure, zéro prime, et un net qui ne venait plus que de la
   rémunération fixe. Le calcul n'avait rien : c'est l'HORAIRE D'ÉQUIPE que
   son appareil n'arrivait plus à lire. Une réponse d'erreur — un 404, une
   coupure, un portail Wi-Fi qui répond une page de connexion — avait été
   mise en cache À LA PLACE du fichier, et le cache d'abord la resservait
   ensuite à chaque ouverture. Le défaut se RÉPARE TOUT SEUL une fois posé :
   ni le retour du réseau ni un rechargement n'y changeaient quoi que ce
   soit.

   Une réponse qui n'est pas « 200 de notre origine » ne remplace donc plus
   jamais ce qui est en cache. Reproduit et corrigé avec Playwright, en
   empoisonnant l'entrée à la main. */
function cacheSiBon(req, res) {
  if (!res || res.type === "error") return;
  /* Une réponse OPAQUE — les polices, demandées sans CORS — ne se lit pas :
     ni son code ni son corps. On ne peut donc pas la juger, et la refuser
     priverait la page de ses polices hors ligne. Elle passe, comme avant.
     Tout ce qui se LIT, lui, doit être bon : c'est là qu'était le trou. */
  if (res.type !== "opaque" && !res.ok) return;
  var copy = res.clone();
  caches.open(V).then(function (c) { try { c.put(req, copy); } catch (err) {} });
}
function reseauPuisCache(req) {
  return fetch(req).then(function (res) {
    cacheSiBon(req, res);
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
            /* et si la réponse est mauvaise, on RETIRE ce qui dort en cache
               plutôt que de garder une entrée dont on ne sait plus rien :
               la fois suivante repartira du réseau. */
            if (res && res.ok) cacheSiBon(req, res);
            else caches.open(V).then(function (c) { c.delete(req); });
          }).catch(function () {});
        }
        return hit;
      }
      return fetch(req).then(function (res) {
        cacheSiBon(req, res);
        return res;
      }).catch(function () {
        return req.mode === "navigate" ? caches.match("./index.html") : Response.error();
      });
    })
  );
});
