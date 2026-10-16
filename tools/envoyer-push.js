#!/usr/bin/env node
/* La notification du téléphone, application fermée, à chaque classeur
   installé — appelé par tools/horaire-auto.py après un envoi réussi sur main.

     node tools/envoyer-push.js "Titre" "Texte"
     node tools/envoyer-push.js --messages=fichier.json

   Le second, depuis le 16/10/2026 (« les notifications doivent être
   optimisées au max ») : un message PAR PERSONNE, choisi par le trigramme de
   l'abonnement — {tag, url, defaut:{title,body}, par_tri:{ID:{title,body}}, connus:[ID]}.
   Un abonnement « GBT », que deux personnes portent, prend le message commun.

   Le client, le 16/10/2026 : « une notification PWA lors de la mise à jour du
   classeur », puis « B tant que mnt » : la même pour tous les abonnés. Le
   09/10 il avait écarté l'envoi application fermée faute de serveur ; il en
   existe un depuis le 16/10, l'action GitHub qui installe les classeurs.

   Les abonnements vivent dans la base Supabase du projet PINO (le choix du
   client), table biowanze_push, fermée au public : l'application s'y inscrit
   par biowanze_abonner(), la liste ne sort que par biowanze_abonnes() avec la
   clé partagée PUSH_CLE. La clé privée d'envoi est le secret
   VAPID_PRIVATE_KEY ; la clé publique est écrite ici et dans index.html, et
   les deux doivent être la même.

   N'imprime que des comptes : le journal d'une action est public. Un
   abonnement que le service d'envoi déclare mort (404, 410) est retiré.
   Jamais d'échec : une notification manquée ne doit pas faire croire que
   l'horaire n'est pas installé. */
var webpush = require("web-push");

var SUPABASE = "https://pnizdddritizjbsksoir.supabase.co";
var CLE_PUBLIQUE_SUPABASE = "sb_publishable_FzetjMxWmdjSaTHWl1uZSg_HhMyErQI";
var VAPID_PUBLIQUE = "BF28dyZP0cTh-oFWm2lZiYLHxdp3lTem9lTN806GT-jVeiMkWk0tnRKMux_6qpojHLmlon3N1F4llyPCUX8efpg";

function rpc(nom, corps) {
  return fetch(SUPABASE + "/rest/v1/rpc/" + nom, {
    method: "POST",
    headers: { apikey: CLE_PUBLIQUE_SUPABASE, "Content-Type": "application/json" },
    body: JSON.stringify(corps)
  }).then(function (r) {
    if (!r.ok) throw new Error(nom + " : HTTP " + r.status);
    return r.status === 204 ? null : r.json();
  });
}

function lireMessages() {
  var opt = process.argv.slice(2).filter(function (a) { return a.indexOf("--messages=") === 0; })[0];
  if (opt) return JSON.parse(require("fs").readFileSync(opt.slice(11), "utf8"));
  return { tag: "classeur", url: "./", par_tri: {},
           defaut: { title: process.argv[2] || "Horaire mis à jour", body: process.argv[3] || "" } };
}

/* Le message d'un abonné : celui de son identifiant, sinon celui de son
   trigramme s'il ne désigne qu'une personne, sinon le message commun. */
function messageDe(m, tri) {
  var par = m.par_tri || {};
  if (tri && par[tri]) return par[tri];
  var ids = Object.keys(par).filter(function (k) { return tri && k.split("-")[0] === tri; });
  if (ids.length === 1) return par[ids[0]];
  // une personne connue pour qui rien ne change ne reçoit rien (le client,
  // le 16/10/2026) ; un abonné sans trigramme reconnu, le message commun
  var connus = (m.connus || []).filter(function (k) { return tri && (k === tri || k.split("-")[0] === tri); });
  return connus.length ? null : m.defaut;
}

function main() {
  var m = lireMessages();
  var prive = process.env.VAPID_PRIVATE_KEY, cle = process.env.PUSH_CLE;
  if (!prive || !cle) { console.log("Notifications : secrets absents, rien envoyé."); return Promise.resolve(); }
  webpush.setVapidDetails("https://cronobots.github.io/groups/", VAPID_PUBLIQUE, prive);
  return rpc("biowanze_abonnes", { p_cle: cle }).then(function (liste) {
    var ok = 0, morts = 0, ko = 0, tus = 0;
    return Promise.all((liste || []).map(function (a) {
      var sub = { endpoint: a.endpoint, keys: { p256dh: a.p256dh, auth: a.auth } };
      var x = messageDe(m, a.tri);
      if (!x) { tus++; return null; }
      var charge = JSON.stringify({ title: x.title, body: x.body, tag: m.tag || "classeur", url: m.url || "./" });
      return webpush.sendNotification(sub, charge, { TTL: 86400 }).then(function () { ok++; })
        .catch(function (e) {
          if (e && (e.statusCode === 404 || e.statusCode === 410)) {
            morts++; return rpc("biowanze_desabonner", { p_endpoint: a.endpoint }).catch(function () {});
          }
          ko++;
        });
    })).then(function () {
      console.log("Notifications : " + ok + " envoyée(s), " + morts + " abonnement(s) périmé(s) retiré(s), " + ko + " échec(s), " + tus + " sans changement.");
    });
  }).catch(function (e) { console.log("Notifications : non envoyées (" + e.message + ")."); });
}

main();
