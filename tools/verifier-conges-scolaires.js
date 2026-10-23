/* Confronte le calcul des congés scolaires de la Fédération
 * Wallonie-Bruxelles (fwbAn, découpée dans index.html) aux calendriers
 * officiels : ce que les arrêtés publiés fixent (rentrée, fin d'année,
 * vacances d'hiver, jours de congé, mardi gras) et, pour les années sans
 * arrêté, les rentrées et fins déjà annoncées.
 *
 * Le décret du 31 mars 2022 (Code de l'enseignement, art. 1.9.1-1) fixe ces
 * dates par des règles ; l'application les calcule pour toute année. Les
 * attendus ci-dessous ne sont pas une seconde copie de ces règles : ce
 * sont les dates PUBLIÉES, que le calcul doit retrouver.
 *
 *   node tools/verifier-conges-scolaires.js [index.html]
 *
 * Code de retour 1 au premier écart. Éprouvé le 23/10/2026 : sans
 * l'exception de la rentrée (30-31 août), la rentrée 2026 et le mardi gras
 * 2027 crient ; une règle de Noël faussée fait crier l'hiver 2027.
 */
const fs=require("fs"), path=require("path");
const H=fs.readFileSync(process.argv[2]||path.join(__dirname,"..","index.html"),"utf8");
function part(a,b){ const i=H.indexOf(a); if(i<0) throw new Error("introuvable : "+a); return H.slice(i,H.indexOf(b,i)+b.length); }
eval(part("function easter(","\n}")+"\n"+part("var FWB_ARRETES=","\n};")+"\n"+part("function fwbAn(","\n}"));
const iso=d=>d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0");
/* les arrêtés : jours de congé qui tombent en semaine hors des vacances */
const ARRETES={
  2025:{rentree:"2025-08-25", fin:"2026-07-03", hiver:"2025-12-22", conges:["2025-11-11","2026-04-06","2026-05-14","2026-05-25"], mardiGras:null},
  2026:{rentree:"2026-08-24", fin:"2027-07-02", hiver:"2026-12-21", conges:["2026-11-02","2026-11-11","2027-03-29","2027-05-17"], mardiGras:"2027-02-09"},
  2027:{rentree:"2027-08-30", fin:"2028-07-07", hiver:"2027-12-27", conges:["2027-09-27","2027-11-11","2028-04-17","2028-05-25","2028-06-05"], mardiGras:null},
  2028:{rentree:"2028-08-28", fin:"2029-07-06", hiver:"2028-12-25", conges:["2028-09-27","2029-04-02","2029-05-21"], mardiGras:"2029-02-13"}
};
/* annoncées sans arrêté (calendrier indicatif de mai 2021) */
const ANNONCES={2029:["2029-08-27","2030-07-05"], 2030:["2030-08-26","2031-07-04"], 2031:["2031-08-25","2032-07-02"]};
let fautes=0;
function ecart(m){ fautes++; console.log("ÉCART  "+m); }
Object.keys(ARRETES).forEach(A=>{
  const e=ARRETES[A], x=fwbAn(+A), h=x.periodes.filter(q=>q.k==="hiver")[0];
  if(iso(x.rentree)!==e.rentree) ecart(A+" rentrée "+iso(x.rentree)+", l'arrêté dit "+e.rentree);
  if(iso(x.fin)!==e.fin) ecart(A+" fin "+iso(x.fin)+", l'arrêté dit "+e.fin);
  if(iso(h.d)!==e.hiver) ecart(A+" hiver "+iso(h.d)+", l'arrêté dit "+e.hiver);
  const c=x.conges.map(z=>iso(z[0])).sort().join(" ");
  if(c!==e.conges.slice().sort().join(" ")) ecart(A+" congés "+c+", l'arrêté dit "+e.conges.join(" "));
  if((x.mardiGras?iso(x.mardiGras):null)!==e.mardiGras) ecart(A+" mardi gras "+(x.mardiGras?iso(x.mardiGras):"aucun")+", l'arrêté dit "+(e.mardiGras||"aucun"));
  if(!x.arrete||x.periodes.length!==4) ecart(A+" : l'automne, la détente ou le printemps manquent (FWB_ARRETES)");
});
Object.keys(ANNONCES).forEach(A=>{
  const x=fwbAn(+A);
  if(iso(x.rentree)!==ANNONCES[A][0]) ecart(A+" rentrée "+iso(x.rentree)+", annoncée "+ANNONCES[A][0]);
  if(iso(x.fin)!==ANNONCES[A][1]) ecart(A+" fin "+iso(x.fin)+", annoncée "+ANNONCES[A][1]);
});
console.log(fautes?fautes+" écart(s)":"Congés scolaires : "+Object.keys(ARRETES).length+" arrêtés et "+Object.keys(ANNONCES).length+" années annoncées retrouvés, 0 écart.");
process.exit(fautes?1:0);
