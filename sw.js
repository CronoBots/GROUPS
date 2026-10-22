/* BIOWANZE — service worker */
var V = "nfdm-v939";
var CORE = ["./", "./index.html", "./manifest.webmanifest", "./logo.svg", "./banniere.jpg",
            "./data/recyclages-2026.json",
            "./icon-192.png", "./icon-512.png", "./icon-maskable-512.png",
            "./apple-touch-icon.png", "./favicon.png",
            /* polices auto-hébergées : le sous-ensemble latin, celui qui sert
               au texte français, est mis en cache dès l'installation pour que
               l'app soit complète hors ligne au premier lancement. Le latin-ext
               (accents rares) est pris à la demande par le handler ci-dessous. */
            "./fonts/archivo-latin.woff2", "./fonts/ibmplexmono-400-latin.woff2",
            "./fonts/ibmplexmono-500-latin.woff2", "./fonts/ibmplexmono-600-latin.woff2"];
/* data/horaire-AAAA.json (un par année : 2026 et 2027 depuis le 20/10/2026,
   environ 700 Ko chacun) est volontairement
   absent d'ici : il est mis en cache à la demande par le handler fetch ci-dessous,
   seulement pour qui utilise le pré-remplissage, plutôt que de ralentir l'installation
   pour tout le monde. La taille varie avec les mises à jour de l'horaire. */

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
/* LA PAGE REVALIDÉE, jamais prise dans le cache HTTP. Le client, le
   30/09/2026 : « l'app PWA ne se met pas à jour ? ». GitHub Pages sert
   tout avec « max-age=600 » : le « réseau d'abord » pouvait rendre, dix
   minutes durant, la page que le navigateur gardait déjà. « no-cache »
   oblige à redemander au serveur (réponse 304 si rien n'a changé). */
function reseauPuisCache(req) {
  return fetch(req, { cache: "no-cache" }).then(function (res) {
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
/* L'HORAIRE AU RÉSEAU D'ABORD (le client, le 19/10/2026, capture de
   l'application ouverte sur l'ordinateur : « classeur du 16/10 » et le
   1er novembre en PM, alors que celui du 19/10 était en ligne). Servi du
   cache d'abord et rafraîchi derrière, l'horaire neuf n'apparaissait qu'à
   l'ouverture SUIVANTE : la première après une mise à jour montrait
   toujours l'ancien. Il est désormais revalidé (« no-cache » : 304 sans
   corps s'il n'a pas changé) ; au-delà de quatre secondes, ou hors ligne,
   le cache répond. */
function jsonFrais(req) {
  var reseau = fetch(req, { cache: "no-cache" }).then(function (res) {
    if (res && res.ok) { cacheSiBon(req, res); return res; }
    throw new Error("HTTP " + (res && res.status));
  });
  return new Promise(function (resolve) {
    var fini = false;
    function rendre(r) { if (!fini) { fini = true; resolve(r); } }
    var t = setTimeout(function () {
      caches.match(req).then(function (hit) { if (hit) rendre(hit); });
    }, 4000);
    reseau.then(function (res) { clearTimeout(t); rendre(res); }, function () {
      clearTimeout(t);
      caches.match(req).then(function (hit) { rendre(hit || Response.error()); });
    });
  });
}
self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  var sameOrigin = url.origin === self.location.origin;
  /* Les polices sont désormais servies depuis notre propre origine : plus de
     branche « fonts.googleapis/gstatic » à gérer, et plus de réponse opaque
     à laisser passer sans pouvoir la vérifier. Tout passe par la garde 200. */
  if (!sameOrigin) return;
  /* les abonnements agenda (cal/<id>.ics) : jamais en cache, c'est le
     téléphone qui les relit, et il doit lire le dernier horaire */
  if (/\/cal\/[^/]+\.ics$/.test(url.pathname)) return;

  if (/\/data\/[^/]+\.json$/.test(url.pathname)) {
    e.respondWith(jsonFrais(req));
    return;
  }

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
          fetch(req, { cache: "no-cache" }).then(function (res) {
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
/* La notification « Horaire modifié » (index.html, notifierTelephone) : la
   toucher ramène l'application au premier plan si elle est ouverte, et
   l'ouvre sinon — sur l'Accueil, où la carte des changements l'attend. */
/* LA NOTIFICATION REÇUE APPLICATION FERMÉE (le client, le 16/10/2026) :
   l'action GitHub l'envoie à chaque classeur installé (tools/envoyer-push.js).
   iOS exige qu'un message reçu s'affiche toujours. */
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
