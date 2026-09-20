/* Confronte ce que le calendrier AFFICHE à ce que le classeur DIT, pour les
   77 personnes et les 365 journées de l'année.
 *
 * Le calendrier n'a pas le droit de se tromper : il sert à contrôler une
 * fiche de paie. Une journée peinte en poste là où personne n'a travaillé,
 * ou laissée vide là où le classeur écrit quelque chose, est une faute —
 * pas une approximation.
 *
 * L'outil ne réimplémente rien : il découpe dans index.html les fonctions
 * de lecture elles-mêmes et les rejoue. Ce qu'il mesure est donc bien ce
 * que l'application fera, et non une copie qui aurait vieilli à côté.
 *
 *   node tools/verifier-calendrier.js [chemin/horaire.json]
 *
 * Sortie : un état par règle, puis le détail de chaque manquement.
 * Code de retour 1 s'il reste une faute.
 */
/* pas de « use strict » : les fonctions découpées sont évaluées ici même,
   et le mode strict les enfermerait dans la portée de l'eval. */
const fs=require("fs"), path=require("path");
const RACINE=path.join(__dirname,"..");
const html=fs.readFileSync(path.join(RACINE,"index.html"),"utf8");

/* --- découpe des fonctions de l'application ------------------------------ */
function part(debut,fin){
  const i=html.indexOf(debut);
  if(i<0) throw new Error("introuvable dans index.html : "+debut);
  const j=html.indexOf(fin,i+debut.length);
  if(j<0) throw new Error("fin introuvable pour : "+debut);
  return html.slice(i,j+fin.length);
}
const MORCEAUX=[
  ["var SHIFT_CODES=[","];"],
  ["var POSTE_LIB=","};"],
  ["var ABS=[","\n];"],
  ["var ABSMAP={};","\n"],
  ["var ABSNORM={};","});"],
  ["function codeAbsence(","\n}"],
  ["function R(","\n}"],
  ["function pad2(","\n}"],
  ["var CYCLE6=[","];"],
  ["var CYCLE5=","\n"],
  ["var ANCRAGE=[","\n"],
  ["var ANCRAGE_BASE=","\n"],
  ["function cyclePoste(","\n}"],
  ["function daysInMonth(","\n}"],
  ["var HORAIRE_PLAGES=","};"],
  ["function normPlage(","\n}"],
  ["function posteDepuisMention(","\n}"],
  ["var SHIFT_PLAGE=","};"],
  ["function plageMention(","\n}"],
  ["function seChevauchent(","\n}"],
  ["var JOUR_PRIME_PAUSE=","];"],
  ["var MENTIONS_NEUTRES=","];"],
  ["var ATELIERS=","\n"],
  ["function reprisRHS(","\n}"],
  ["function posteDepuisPlage(","\n}"],
  ["function dureeReelle(","\n}"],
  ["var ALIAS_HORAIRE=","\n"],
  ["var JOUR_EN_ABSENCE=","\n"],
  ["function parseHoraireEntry(","\n}"],
  ["var CYCLES=[","];"],
  ["function cycleDuMois(","\n}"],
  ["function posteDeCycle(","\n}"],
  ["function posteDuRemplace(","\n}"],
  ["function plageCommentaire(","\n}"],
  ["function debordePoste(","\n}"],
  ["function lireJournee(","\n}"],
  ["function plageHorsPoste(","\n}"],
  ["var RX_RENVOI=","\n"],
  ["function epargnesDuMois(","\n}"],
  ["function etiqJour(","\n}"],
  ["function etiqAbsence(","\n}"]
];
eval(MORCEAUX.map(m=>part(m[0],m[1])).join("\n"));

/* Découper du code par repères est fragile : une table remplie sur deux
   lignes dont on ne prend que la première reste VIDE, et tout ce qu'elle
   devait reconnaître passe pour inconnu. C'est arrivé — trois cellules
   déclarées illisibles ne l'étaient pas. On ne fait donc pas confiance à la
   découpe : on la met à l'épreuve sur des cas dont on connaît la réponse,
   et on refuse de mesurer quoi que ce soit si l'un d'eux tombe à côté. */
const EPREUVES=[
  ["table des absences remplie", ()=>Object.keys(ABSMAP).length>20],
  ["codes d'absence normalisés", ()=>codeAbsence("8h +FT")==="8H +FT"],
  ["codes d'absence exacts",     ()=>codeAbsence("VA")==="VA"],
  ["postes reconnus",            ()=>SHIFT_CODES.indexOf("AM")>=0],
  ["plages horaires",            ()=>posteDepuisPlage(plageMention("6h-14h"))==="AM"],
  ["ateliers reconnus",          ()=>ATELIERS.test("STEP")],
  ["journées de jour",           ()=>JOUR_PRIME_PAUSE.indexOf("d-cppt")>=0],
  ["cycle théorique",            ()=>!!cyclePoste(1,"6 semaines",0,Date.UTC(2026,0,1))],
  ["lecture d'une cellule",      ()=>parseHoraireEntry(["AM"],8).s==="AM"],
  ["annotation « - »",           ()=>parseHoraireEntry(["N","-"],8).h===0],
  ["plage d'un commentaire",     ()=>{const p=plageCommentaire("de 18h à 22h"); return p&&p[0]===18&&p[1]===22;}],
  ["plage hors du poste",        ()=>plageHorsPoste([18,22],"N") && !plageHorsPoste([18,22],"PM")]
];
const ratees=EPREUVES.filter(e=>{ try{ return !e[1](); }catch(x){ return true; } });
if(ratees.length){
  console.error("La découpe de index.html est faussée — rien n'a été vérifié :");
  ratees.forEach(e=>console.error("   ✗ "+e[0]));
  process.exit(2);
}

/* --- ce que la case affichera, règle pour règle -------------------------- */
const H_JOUR=8;
function affichage(r){
  const h=r.s?((r.h===undefined||r.h===null||r.h==="")?H_JOUR:Number(r.h)):0;
  const preste=(h>0);
  const absence=!!(r.a && ABSMAP[r.a]);
  /* un poste prévu que personne n'a presté : ni travail, ni repos */
  const prevu=(!preste && r.s && !absence);
  return {
    preste:preste, heures:h,
    etiquette: preste ? (r.jourCode?etiqJour(r.jourCode):r.s)
             : (absence ? etiqAbsence(r.a) : (prevu ? r.s : "")),
    genre: preste ? "poste" : (absence ? "absence" : (prevu ? "prévu" : "repos"))
  };
}

/* Le mois lit une journée ENREGISTRÉE — ce que le pré-remplissage a écrit —
   là où l'année relit le classeur. Deux chemins pour une même journée, et
   c'est ainsi qu'une divergence était passée : le mois affichait un repos,
   l'année un poste. On refait donc ici le trajet complet — lecture, écriture
   du mois, relecture — et on exige le même résultat des deux côtés. */
function enregistre(r,hJour){
  var rec={};
  if(r.s || (r.a && ABSMAP[r.a])){
    if(r.s){ rec.s=r.s; rec.h=(r.h===undefined)?hJour:r.h; }
    if(r.a && ABSMAP[r.a]) rec.a=r.a;
    if(r.jourCode) rec.j=r.jourCode;
  }
  return rec;
}
function affichageRecord(rec,hJour){
  const h=rec.s?((rec.h===undefined||rec.h===null||rec.h==="")?hJour:Number(rec.h)):0;
  const preste=(h>0);
  const absence=!!(rec.a && ABSMAP[rec.a]);
  const prevu=(!preste && rec.s && !absence);
  return {
    etiquette: preste ? (rec.j?etiqJour(rec.j):rec.s)
             : (absence ? etiqAbsence(rec.a) : (prevu ? rec.s : "")),
    genre: preste ? "poste" : (absence ? "absence" : (prevu ? "prévu" : "repos"))
  };
}

/* --- lecture du classeur ------------------------------------------------- */
const fichier=process.argv[2]||path.join(RACINE,"data","horaire-2026.json");
const db=JSON.parse(fs.readFileSync(fichier,"utf8"));
const ANNEE=Number(db.year);

const REGLES=[
  ["cellule non reconnue","le classeur écrit un poste ou une plage que la lecture ne sait pas traduire"],
  ["poste prévu effacé",  "la cellule porte un poste et l'annotation « - » : non presté, mais la case ne le dit pas"],
  ["poste sans heure",    "la case est peinte en poste alors qu'aucune heure n'est prestée"],
  ["heure sans poste",    "des heures sont prestées sans poste à afficher"],
  ["repos habillé",       "le classeur dit repos, la case affiche un poste ou une absence"],
  ["absence sans code",   "la journée n'est pas prestée et aucun code ne le dit"],
  ["étiquette vide",      "la case a un genre mais rien à écrire dedans"],
  ["étiquette trop longue","l'étiquette dépasse quatre signes et sera coupée"],
  ["vues en désaccord",    "le mois et l'année ne montrent pas la même chose le même jour"],
  ["mention non comprise", "la case dit quelque chose, mais un morceau de la cellule reste illisible"]
];
const fautes={}; REGLES.forEach(r=>fautes[r[0]]=[]);
let cellules=0, postes=0, absences=0, repos=0, prevus=0;
const incomprises={};

for(const p of db.people){
  for(let m=1;m<=12;m++){
    const fit=cycleDuMois(p,ANNEE,m), ep=epargnesDuMois(p,m), nd=daysInMonth(ANNEE,m-1);
    for(let d=1;d<=nd;d++){
      const mmdd=pad2(m)+pad2(d), raw=p.d[mmdd];
      if(raw===undefined) continue;
      cellules++;
      const r=lireJournee(db,raw,ANNEE,m,d,fit,ep[d],H_JOUR);
      const a=affichage(r);
      const cel=(raw[0]||"").trim(), annot=(raw[1]||"").trim();
      const vide=(!cel||cel==="-");
      const ou=p.id+" "+d+"/"+pad2(m);
      const src=JSON.stringify(raw);

      if(a.genre==="poste") postes++;
      else if(a.genre==="absence") absences++;
      else if(a.genre==="prévu") prevus++;
      else repos++;

      /* 1. une cellule pleine ne peut pas laisser la case muette. Deux cas
            très différents : l'annotation « - » dit « prévu, non presté » —
            la journée est juste, il manque seulement de le montrer ; tout
            le reste est une cellule que la lecture n'a pas su traduire, et
            celle-là peut coûter des heures. */
      if(!vide && a.genre==="repos"){
        if(annot==="-") fautes["poste prévu effacé"].push(ou+"  "+src);
        else fautes["cellule non reconnue"].push(ou+"  "+src);
      }
      /* 2. peint en poste sans heure prestée — impossible par construction,
            on le vérifie quand même : c'était la faute de février */
      if(a.genre==="poste" && a.heures<=0)
        fautes["poste sans heure"].push(ou+"  "+src);
      /* 3. des heures sans poste à montrer */
      if(a.heures>0 && !r.s)
        fautes["heure sans poste"].push(ou+"  "+src);
      /* 4. le classeur dit repos et rien d'autre : la case doit rester vide */
      if(vide && !annot && !(raw[2]||"").trim() && a.genre!=="repos")
        fautes["repos habillé"].push(ou+"  "+src+"  → "+a.genre+" "+a.etiquette);
      /* 5. journée non prestée alors que la cellule porte un poste franc :
            un code doit dire pourquoi */
      if(!vide && annot!=="-" && SHIFT_CODES.indexOf(cel)>=0 && a.genre==="repos")
        fautes["absence sans code"].push(ou+"  "+src);
      /* 6. et 7. l'étiquette doit exister et tenir dans la case */
      if(a.genre!=="repos" && !a.etiquette)
        fautes["étiquette vide"].push(ou+"  "+src+"  → "+a.genre);
      if(a.etiquette.length>4)
        fautes["étiquette trop longue"].push(ou+"  "+src+"  → «"+a.etiquette+"»");
      /* La case peut être juste alors qu'un morceau de la cellule n'a pas
         été compris : une plage horaire inconnue ne donne pas de poste, mais
         l'annotation sauve l'affichage. Signal faible — à regarder, pas à
         confondre avec une case muette. */
      if(r.unknown){
        (r.unknownTxt||["?"]).forEach(t=>{
          const cle=String(t).trim();
          if(!incomprises[cle]) incomprises[cle]={n:0, ex:[]};
          incomprises[cle].n++;
          if(incomprises[cle].ex.length<3) incomprises[cle].ex.push(ou+"  "+src);
        });
        fautes["mention non comprise"].push(ou+"  "+src);
      }
      /* 8. le trajet par le mois doit rendre exactement la même case */
      const viaMois=affichageRecord(enregistre(r,H_JOUR),H_JOUR);
      if(viaMois.genre!==a.genre || viaMois.etiquette!==a.etiquette)
        fautes["vues en désaccord"].push(ou+"  "+src+"  → mois "+viaMois.genre+" «"+viaMois.etiquette
          +"» / année "+a.genre+" «"+a.etiquette+"»");
    }
  }
}

/* --- rapport ------------------------------------------------------------- */
const n=x=>String(x).padStart(6);
console.log("Horaire "+ANNEE+" — "+db.people.length+" personnes, "+cellules+" journées\n");
console.log("  "+n(postes)+"  journées prestées");
console.log("  "+n(absences)+"  absences affichées");
console.log("  "+n(prevus)+"  postes prévus, non prestés");
console.log("  "+n(repos)+"  repos\n");

let total=0;
for(const [nom,quoi] of REGLES){
  const l=fautes[nom]; total+=l.length;
  console.log((l.length?"  ✗ ":"  ✓ ")+n(l.length)+"  "+nom+" — "+quoi);
}
if(total){
  console.log("");
  for(const [nom] of REGLES){
    const l=fautes[nom]; if(!l.length) continue;
    console.log("── "+nom+" ("+l.length+")");
    if(nom==="mention non comprise"){
      /* Cinq cents lignes ne se lisent pas. Ce qu'il faut savoir tient dans
         la liste des mentions elles-mêmes : une question par mention, et
         trois exemples pour la poser. */
      Object.keys(incomprises).sort((a,b)=>incomprises[b].n-incomprises[a].n).forEach(k=>{
        console.log("   "+String(incomprises[k].n).padStart(4)+" × «"+k+"»");
        incomprises[k].ex.forEach(x=>console.log("          "+x));
      });
    } else {
      l.slice(0,40).forEach(x=>console.log("   "+x));
      if(l.length>40) console.log("   … et "+(l.length-40)+" autres");
    }
    console.log("");
  }
}
console.log(total?("\n"+total+" faute(s) à corriger."):"\nAucune faute.");
process.exit(total?1:0);
