#!/usr/bin/env node
/* LES NOTIFICATIONS DES DEMANDES DE CONGÉ (le client, le 22/10/2026 : « si
   sur la demande de congé le travailleur sélectionne un remplaçant, ce même
   remplaçant doit recevoir la demande sur son téléphone pour signer le
   remplacement ; et la RH ne doit recevoir la demande qu'une fois le
   remplacement signé »).

   La base remplit la file biowanze.notifs (base/14-remplacant-puis-rh.sql)
   et lance aussitôt l'action « notifier.yml », qui appelle ce script :

     node tools/notifier-demandes.js

   Il lit la file par biowanze_notifs_a_envoyer(PUSH_CLE) — elle se marque
   envoyée en même temps — puis la confie à envoyer-push.js, un message par
   trigramme, rien aux autres abonnés. Plusieurs messages pour la même
   personne se regroupent en un. La clé privée d'envoi reste le secret
   VAPID_PRIVATE_KEY. N'imprime que des comptes : le journal d'une action est
   public. Jamais d'échec.

   LES ANNONCES DE LA RH (30/10/2026, base/35-annonces-infos.sql) passent
   par la même file, avec « * » pour trigramme : elles vont à TOUS les
   abonnés, dans un envoi à part (tag « annonce », elles ouvrent « Infos et
   aide »), sans attendre l'abonnement « sûr » des demandes. */
var fs = require("fs"), path = require("path"), os = require("os"), cp = require("child_process");
var SUPABASE = "https://pnizdddritizjbsksoir.supabase.co";
var CLE_PUBLIQUE_SUPABASE = "sb_publishable_FzetjMxWmdjSaTHWl1uZSg_HhMyErQI";

function main() {
  var cle = process.env.PUSH_CLE;
  if (!cle || !process.env.VAPID_PRIVATE_KEY) { console.log("Demandes : secrets absents, rien envoyé."); return Promise.resolve(); }
  return fetch(SUPABASE + "/rest/v1/rpc/biowanze_notifs_a_envoyer", {
    method: "POST",
    headers: { apikey: CLE_PUBLIQUE_SUPABASE, "Content-Type": "application/json" },
    body: JSON.stringify({ p_cle: cle })
  }).then(function (r) {
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.json();
  }).then(function (l) {
    l = l || [];
    var tous = l.filter(function (n) { return n.tri === "*"; });
    l = l.filter(function (n) { return n.tri !== "*"; });
    if (tous.length) annoncer(tous);
    if (!l.length) { console.log("Demandes : aucune notification en attente."); return; }
    var par = {};
    l.forEach(function (n) { (par[n.tri] = par[n.tri] || []).push(n); });
    var m = { tag: "demande", url: "./?vue=demandes", defaut: null, par_tri: {}, connus: [] };
    Object.keys(par).forEach(function (t) {
      var x = par[t];
      m.par_tri[t] = x.length === 1 ? { title: x[0].titre, body: x[0].texte }
        : { title: x.length + " demandes de congé", body: x.map(function (n) { return n.texte; }).join(" ") };
    });
    var f = path.join(os.tmpdir(), "notifs-demandes.json");
    fs.writeFileSync(f, JSON.stringify(m));
    console.log("Demandes : " + l.length + " notification(s) pour " + Object.keys(par).length + " personne(s).");
    cp.execFileSync(process.execPath, [path.join(__dirname, "envoyer-push.js"), "--messages=" + f], { stdio: "inherit" });
  }).catch(function (e) { console.log("Demandes : non envoyées (" + e.message + ")."); });
}
function annoncer(tous) {
  var m = { tag: "annonce", url: "./?vue=aide", par_tri: {}, connus: [],
            defaut: tous.length === 1 ? { title: tous[0].titre, body: tous[0].texte }
              : { title: tous.length + " annonces", body: tous.map(function (n) { return n.titre; }).join(" · ") } };
  var f = path.join(os.tmpdir(), "notifs-annonces.json");
  fs.writeFileSync(f, JSON.stringify(m));
  console.log("Annonces : " + tous.length + " à tous les abonnés.");
  try { cp.execFileSync(process.execPath, [path.join(__dirname, "envoyer-push.js"), "--messages=" + f], { stdio: "inherit" }); }
  catch (e) { console.log("Annonces : non envoyées (" + e.message + ")."); }
}
main();
