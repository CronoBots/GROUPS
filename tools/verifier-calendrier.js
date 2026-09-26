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
  /* La découpe prenait la PREMIÈRE occurrence sans rien dire. Une seconde
     fonction du même nom, ajoutée plus bas dans index.html, écrase la
     première au chargement — mais le vérificateur continuait de rejouer la
     première et annonçait neuf règles vertes. C'est arrivé : un
     posteDuRemplace() rendant un atelier a doublé celui qui rend une pause,
     et l'outil censé s'en apercevoir était précisément aveugle à ce cas.
     Une découpe ambiguë ne vérifie plus ce qu'exécute l'application : on
     s'arrête. */
  const bis=html.indexOf(debut,i+debut.length);
  if(bis>=0) throw new Error(
    "deux fois dans index.html : "+debut+"\n  "+
    "la seconde déclaration écrase la première à l'exécution, et la découpe "+
    "rejouerait la première — donner un autre nom à l'une des deux.");
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
  ["var POSTES_TRAVAIL=[","\n];"],
  ["function posteDepuisNom(","\n}"],
  ["function reprisRHS(","\n}"],
  ["function posteDepuisPlage(","\n}"],
  ["function dureeReelle(","\n}"],
  ["var ALIAS_HORAIRE=","\n"],
  ["var COQUILLES=","\n"],
  ["var JOUR_EN_ABSENCE=","\n"],
  ["var RX_PRIS_AILLEURS=","\n"],
  ["function parseHoraireEntry(","\n}"],
  ["var CYCLES=[","];"],
  ["function cycleDuMois(","\n}"],
  ["function posteDeCycle(","\n}"],
  ["function posteDuRemplace(","\n}"],
  ["function plageCommentaire(","\n}"],
  ["function debordePoste(","\n}"],
  ["var RX_PRIME_GARDEE=","\n"],
  ["function primeGardee(","\n}"],
  ["function motPrime(","\n}"],
  ["function lireJournee(","\n}"],
  ["function plageHorsPoste(","\n}"],
  ["var RX_RENVOI=","\n"],
  ["function renvoisDuMois(","\n}"],
  ["function epargnesDuMois(","\n}"],
  ["function marqueDoute(","\n}"],
  ["function etiqJour(","\n}"],
  ["function etiqAbsence(","\n}"],
  ["function familleAbsence(","\n}"],
  ["function compteursCalcules(","\n}"],
  /* la polyvalence : on DÉCOUPE le calcul de l'application au lieu de le
     refaire. Une première version le réimplémentait, et elle a aussitôt
     divergé sur BBZ — « poste habituel » n'y suivait pas la même chaîne. */
  ["var POLY_QUOTA=",";"],
  ["var POSTE_PERIODE=","\n"],
  ["function _posteDePeriode(","\n}"],
  ["function _posteDeLigne9(","\n}"],
  /* posteAttitre() et posteDeFormation() tenaient chacune sur UNE ligne et
     se découpaient jusqu'au premier saut de ligne. La tranche de période
     les a mises à trois lignes, et la découpe rendait une fonction coupée
     en deux : SyntaxError au chargement. Elles se ferment sur « \n} »
     comme les autres. */
  ["function posteAttitre(","\n}"],
  ["function posteDeFormation(","\n}"],
  ["function aLaPolyvalence(","\n}"],
  ["var _poly=null",";"],
  ["function calculerPolyvalence(","\n}"],
  ["function polyvalenceDe(","\n}"],
  /* le mémo que equipeDuJour() emploie : sans lui la découpe le laisserait
     hors du champ et equipeDuJour() lèverait une ReferenceError */
  ["var _moisCache=","\n}"],
  /* l'effectif des postes — le tableau des manques rejoue le calcul de
     l'onglet Équipe, il ne le refait pas */
  ["var CONTREMAITRES=","\n"],
  ["function estCadre(","\n}"],
  ["var EMPLOYES_HORS_CADRE=","\n"],
  ["function idLisible(","\n"],
  ["function statutPersonne(","\n}"],
  ["function estContremaitre(","\n}"],
  ["var EST_FORMATION=","\n"],
  ["var PROJETS_SUR_POSTE=","\n"],
  ["function surSonPosteMalgreF(","\n}"],
  ["function roleDeFeuille(","\n}"],
  ["function posteLigne9(","\n}"],
  ["function atelierDuRemplace(","\n}"],
  ["function posteEcrit(","\n}"],
  ["function enFormation(","\n}"],
  ["function compteAuPoste(","\n}"],
  ["function effectif(","\n}"],
  ["var RENFORT_TRANCHE=","\n"],
  ["var RENFORT_CLOS=","\n"],
  ["var RENFORT_MOTIF=","\n"],
  ["var RENFORT_POSTE=","\n"],
  ["var renfortCache=","\n"],
  ["function renfortDuJour(","\n}"],
  ["function attenduAuPoste(","\n}"],
  ["function peutTenir(","\n}"],
  ["var EST_RENFORT=","\n"],
  ["function reequilibrer(","\n}"],
  ["var POSTE_TRANCHE=","\n"],
  ["function posteParDefaut(","\n}"],
  ["function posteTenu(","\n}"],
  ["var EQ_GROUPES=","\n];"],
  /* son mémo, déclaré juste au-dessus d'elle : la découpe prend les deux */
  ["var _finCache=","\n}"],
  ["function equipeDuJour(","\n}"],
  ["function remplacementCM(","\n}"],
  ["function aLAtelier(","\n}"],
  ["function polyFinie(","\n}"],
  ["function tientTerrainArriere(","\n}"],
  ["function posteHabituel(","\n}"],
  ["function plageInterne(","\n}"],
  ["function gainFT(","\n}"],
  ["function celluleSansPoste(","\n}"],
  ["function postesDePause(","\n}"]
];
/* compteursCalcules() interroge st.params : l'application le remplit, l'outil
   n'en a qu'un besoin, la journée contractuelle. */
const st={params:{hJour:8}};
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
  ["postes de travail",          ()=>posteDepuisNom("gluten")==="glut" && posteDepuisNom("Poly. Etoh")==="terr"],
  ["journées de jour",           ()=>JOUR_PRIME_PAUSE.indexOf("d-cppt")>=0],
  ["cycle théorique",            ()=>!!cyclePoste(1,"6 semaines",0,Date.UTC(2026,0,1))],
  ["lecture d'une cellule",      ()=>parseHoraireEntry(["AM"],8).s==="AM"],
  ["annotation « - »",           ()=>parseHoraireEntry(["N","-"],8).h===0],
  ["annotation renvoyée ailleurs",()=>!parseHoraireEntry(["-","2h -FT","pris le 19.09"],8).a
                                     && parseHoraireEntry(["-","2h -FT"],8).a==="2H -FT"],
  ["heures reçues d'un renvoi",  ()=>lireJournee({people:[]},["PM"],2026,9,12,null,0,8,["2H RTT"]).h===6],
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
    etiquette: preste ? marqueDoute(r,r.jourCode?etiqJour(r.jourCode):r.s)
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
    /* le doute d'un « N? » suit la journée jusqu'au mois, comme dans
       index.html : sans lui, l'année écrivait « N ? » et le mois « N ». */
    if(r.doute) rec.q=1;
    /* Les codes d'absence SUPPLÉMENTAIRES de la journée. index.html les
       écrit depuis toujours (nrec.ax) et cette copie-ci ne le faisait pas :
       le mois rejoué ici perdait les heures qu'une autre journée lui
       renvoie, et depuis le 25/09/2026 les heures supplémentaires d'un
       rappel logé dans une cellule de congé. Deux copies, et c'est la
       seconde qui reste en arrière. */
    if(r.ax && r.ax.length) rec.ax=r.ax.slice();
    /* le poste des heures supplémentaires, quand il n'est pas celui du jour */
    if(r.hsp) rec.hsp=r.hsp;
  }
  return rec;
}
function affichageRecord(rec,hJour){
  const h=rec.s?((rec.h===undefined||rec.h===null||rec.h==="")?hJour:Number(rec.h)):0;
  const preste=(h>0);
  const absence=!!(rec.a && ABSMAP[rec.a]);
  const prevu=(!preste && rec.s && !absence);
  return {
    etiquette: preste ? marqueDoute(rec,rec.j?etiqJour(rec.j):rec.s)
             : (absence ? etiqAbsence(rec.a) : (prevu ? rec.s : "")),
    genre: preste ? "poste" : (absence ? "absence" : (prevu ? "prévu" : "repos"))
  };
}

/* --- lecture du classeur ------------------------------------------------- */
/* --journee et --manques prennent des arguments qui ne sont pas un fichier */
const ARGS=process.argv.slice(2);
const coupe=["--journee","--manques","--polyvalence"].map(o=>ARGS.indexOf(o))
  .filter(i=>i>=0).sort((a,b)=>a-b)[0];
const fichier=(coupe===undefined?ARGS:ARGS.slice(0,coupe))
  .filter(a=>a.charAt(0)!=="-")[0]||path.join(RACINE,"data","horaire-2026.json");
const db=JSON.parse(fs.readFileSync(fichier,"utf8"));
const ANNEE=Number(db.year);

/* ── les manques à venir ────────────────────────────────────────────────
   Le module de l'application ne regarde que devant lui. Ici on mesure tout
   ce qu'il montrerait, du jour dit à la fin de l'horaire, pour savoir s'il
   alerte juste ou s'il crie tous les jours.

   node tools/verifier-calendrier.js --manques [MMJJ]                      */
if(process.argv.indexOf("--manques")>=0){
  const i0=process.argv.indexOf("--manques");
  const depart=/^\d{4}$/.test(process.argv[i0+1]||"")?process.argv[i0+1]:"0101";
  let jours=0, avecManque=0, avecInconnu=0, creuxTotal=0;
  const parPoste={}, parPause={}, lignes=[], deductions=[];
  for(let m=1;m<=12;m++) for(let d=1;d<=daysInMonth(ANNEE,m-1);d++){
    const mmdd=pad2(m)+pad2(d); if(mmdd<depart) continue;
    const par=equipeDuJour(db,ANNEE,m,d);
    let duJour=[], inconnusJour=0; const x_mmdd=mmdd.slice(2)+"/"+mmdd.slice(0,2);
    EQ_GROUPES.forEach(g=>{
      if(g.k==="off"||g.k==="abs"||g.k==="cong"||g.k==="D") return;
      const l=par[g.k]; if(!l||!l.length) return;
      const vue=postesDePause(db,l,g.k,mmdd);
      inconnusJour+=vue.inconnus.length;
      vue.postes.forEach(o=>{
        o.gens.forEach(y=>{ if(y.deduit) deductions.push(
          x_mmdd+"  "+g.k+"  "+y.p.id+" → "+o.P.t); });
        if(!o.manque) return;
        duJour.push({pause:g.k,poste:o.P.t,tenu:o.tenu,attendu:o.attendu,
                     creux:o.creux,inconnus:vue.inconnus.length});
        parPoste[o.P.t]=(parPoste[o.P.t]||0)+1;
        parPause[g.k]=(parPause[g.k]||0)+1;
        creuxTotal+=o.creux;
      });
    });
    jours++;
    if(duJour.length){ avecManque++; if(inconnusJour) avecInconnu++;
      lignes.push({mmdd:mmdd,l:duJour,inc:inconnusJour}); }
  }
  console.log("\nManques d'effectif — du "+depart.slice(2)+"/"+depart.slice(0,2)
              +" au 31/12, "+jours+" journées\n");
  console.log("  "+String(avecManque).padStart(5)+"  journées avec au moins un poste sous son effectif"
              +"  ("+Math.round(avecManque*100/jours)+" %)");
  console.log("  "+String(avecInconnu).padStart(5)+"  dont un poste reste « à déterminer » le même jour");
  console.log("  "+String(creuxTotal).padStart(5)+"  places creuses au total\n");
  console.log("par poste :");
  Object.keys(parPoste).sort((a,b)=>parPoste[b]-parPoste[a])
    .forEach(k=>console.log("  "+String(parPoste[k]).padStart(5)+"  "+k));
  console.log("\npar pause :");
  Object.keys(parPause).sort((a,b)=>parPause[b]-parPause[a])
    .forEach(k=>console.log("  "+String(parPause[k]).padStart(5)+"  "+k));
  console.log("\ndéductions de polyvalence (un indéterminé, un seul poste possible) : "
              +deductions.length);
  deductions.slice(0,12).forEach(x=>console.log("   "+x));
  console.log("\nles vingt premières journées :");
  lignes.slice(0,20).forEach(x=>{
    console.log("  "+x.mmdd.slice(2)+"/"+x.mmdd.slice(0,2)
      +(x.inc?"  ("+x.inc+" à déterminer)":"")+"  "
      +x.l.map(o=>o.pause+" "+o.poste+" "+o.tenu+"/"+o.attendu).join(" · "));
  });
  /* --detail : pour chaque manque, ce que le classeur écrit sur les gens de
     la pause dont l'application ne sait pas le poste. C'est là que se
     cachent les manques qui n'en sont pas — ATR le 25/09 en était un, et
     sa cellule disait « Gluten » en toutes lettres. */
  if(process.argv.indexOf("--detail")>=0){
    console.log("\n── ce que le classeur écrit sur les postes indéterminés\n");
    lignes.forEach(x=>{
      const [m,d]=[Number(x.mmdd.slice(0,2)),Number(x.mmdd.slice(2))];
      const par=equipeDuJour(db,ANNEE,m,d);
      EQ_GROUPES.forEach(g=>{
        if(["off","abs","cong","D"].indexOf(g.k)>=0) return;
        const l=par[g.k]; if(!l||!l.length) return;
        const vue=postesDePause(db,l,g.k,x.mmdd);
        const mq=vue.postes.filter(o=>o.manque);
        if(!mq.length) return;
        console.log("  "+x.mmdd.slice(2)+"/"+x.mmdd.slice(0,2)+"  "+g.k+"  manque : "
          +mq.map(o=>o.P.t+" "+o.tenu+"/"+o.attendu).join(", "));
        if(!vue.inconnus.length){ console.log("      (personne d'indéterminé)"); return; }
        vue.inconnus.forEach(y=>{
          console.log("      "+y.p.id.padEnd(6)+JSON.stringify(y.p.d[x.mmdd])
            +"   poly:"+JSON.stringify((y.p.poly&&y.p.poly.ateliers)||[])
            +(y.p.e&&y.p.e.length?"  e:"+JSON.stringify(y.p.e):""));
        });
      });
    });
  }
  process.exit(0);
}

/* --- les compteurs, recalculés puis confrontés au pied de classeur -------
   node tools/verifier-calendrier.js --compteurs
   Deuxième contrôle, indépendant du premier : les neuf règles regardent ce
   que la case AFFICHE, celui-ci additionne ce qu'elle COMPTE. Le pied de
   feuille est saisi à la main par le client, et il additionne les compteurs
   LÀ OÙ ILS SONT ÉCRITS — un renvoi « pris le 12.06 » déplace donc l'heure
   de jour, jamais de total. Une divergence qui apparaît après une
   modification de la lecture est une régression, pas une trouvaille. */
if(process.argv.indexOf("--compteurs")>=0){
  let bons=0; const ecarts=[];
  for(const p of db.people){
    const f=(p.c&&p.c.flex)||null; if(!f) continue;
    const calc=compteursCalcules(p,ANNEE);
    const attPlus=Number(f["+FT"]||0), attMoins=Number(f["-FT"]||0);
    const ecart=Math.abs(calc.ftPlus-attPlus)+Math.abs(-calc.ftMoins-attMoins);
    if(ecart<0.01) bons++;
    else ecarts.push("   "+p.id+"  +FT "+calc.ftPlus+" vs "+attPlus+
                     "   -FT "+(-calc.ftMoins)+" vs "+attMoins);
  }
  console.log("compteurs flex time — "+bons+" personnes concordent, "+
              ecarts.length+" divergent");
  ecarts.forEach(l=>console.log(l));
  process.exit(ecarts.length>1?1:0);
}

/* --- la polyvalence : combien de journées COMPLÈTES à chaque poste -------
   node tools/verifier-calendrier.js --polyvalence [--tout]

   Le client, le 22/09/2026 : « pour les opérateurs, cela peut être bien
   aussi d'indiquer combien de jours (complet 8h) ils ont fait sur chaque
   poste de production ; les autres ont un quota de polyvalence de 10 jours
   par poste, les adjoints 5 jours par poste ».

   Ne recompte RIEN à côté : rejoue equipeDuJour() et postesDePause(), les
   deux fonctions que l'onglet Équipe emploie pour dire qui tient quoi. Un
   décompte qui compterait autrement que la vue du jour ne vaudrait rien.

   Trois choix, qui se discutent et sont donc écrits ici plutôt que cachés :
     — seules les pauses AM, PM et N comptent. Le « Jour » ne tient pas un
       poste de production : postesDePause() n'y attend d'ailleurs personne.
     — une journée ne compte que si elle vaut HUIT heures pleines. Une
       demi-journée n'apprend pas un poste à moitié.
     — « Contremaître » et « Adjoint » ne sont pas des postes de production
       et sortent du décompte.                                              */
if(process.argv.indexOf("--polyvalence")>=0){
  const gens=db.people.filter(p=>!estContremaitre(p));
  const tout=process.argv.indexOf("--tout")>=0;
  const t=calculerPolyvalence(db);
  console.log("\nPolyvalence — journées COMPLÈTES (8 h) tenues à chaque poste"
    +"\nAUTRE que le sien, du "+t.debut.slice(2)+"/"+t.debut.slice(0,2)
    +" au "+t.fin.slice(2)+"/"+t.fin.slice(0,2)+"/"+ANNEE
    +"\n(la période de polyvalence court du 1er février au 1er février)\n");
  let atteints=0, total=0, vierges=0;
  gens.sort((a,b)=>a.id<b.id?-1:(a.id>b.id?1:0)).forEach(p=>{
    const l=polyvalenceDe(db,p)||[];
    if(!l.length && !tout) return;
    const bouts=l.map(o=>{
      /* Le poste de FORMATION n'est ni le sien ni une polyvalence : il ne
         compte dans aucun des deux totaux, sans quoi l'outil annonçait
         31 « sans remplacement » là où le navigateur en montrait 23. */
      if(o.forme) return o.t+" (en formation)";
      total++; if(o.ok) atteints++; if(!o.n) vierges++;
      return o.t+" "+o.n+"/"+o.q+(o.ok?" \u2713":""); });
    console.log("  "+p.id+"  "+(estCadre(p)?"adjoint  ":"opérateur")+"  "
      +(bouts.join("  ")||"\u2014"));
  });
  console.log("\n  "+atteints+" couple(s) personne-poste au quota sur "+total
    +",\n  dont "+vierges+" où la polyvalence est acquise sans qu'un seul "
    +"remplacement ait été fait");
  /* Ce que la règle stricte ÉCARTE : des journées bel et bien tenues, à un
     poste que la personne ne possède pas. Elles ne comptent pas — « AAI et
     ALZ ont été à la STEP pour voir à quoi cela ressemblait » — mais les
     taire serait perdre une information que personne d'autre ne porte. */
  const hors=[];
  gens.forEach(p=>{
    const par=t.parId[p.id]||{};
    const sien=posteAttitre(p)||posteDeFormation(p);
    POSTES_TRAVAIL.forEach(P=>{
      if(P.cm||P.k==="adj"||P.k===sien) return;
      if(!par[P.k]||aLaPolyvalence(p,P)) return;
      hors.push("   "+p.id+"  "+P.t+" "+par[P.k]+" journée(s)");
    });
  });
  console.log("\n  Journées tenues SANS la polyvalence du poste, donc non "
    +"comptées ("+hors.length+") :");
  hors.forEach(l=>console.log(l));
  process.exit(0);
}

/* --- interroger la lecture sur une journée précise -----------------------
   node tools/verifier-calendrier.js --journee FPA 0919 0921
   Répond ce que l'APPLICATION fait de la cellule — pas ce qu'on croit
   qu'elle en fait. Sans ce mode on écrivait un script à côté, qui
   réimplémentait la lecture et pouvait donc se tromper d'accord avec
   lui-même. */
if(process.argv.indexOf("--journee")>=0){
  const args=process.argv.slice(process.argv.indexOf("--journee")+1);
  const qui=args[0], jours=args.slice(1);
  const p=db.people.filter(x=>x.id===qui)[0];
  if(!p){ console.error("inconnu : "+qui); process.exit(2); }
  const liste=jours.length?jours:Object.keys(p.d).sort();
  for(const mmdd of liste){
    const m=Number(mmdd.slice(0,2)), d=Number(mmdd.slice(2));
    const raw=p.d[mmdd];
    if(raw===undefined){ console.log(mmdd+"  (rien)"); continue; }
    const fit=cycleDuMois(p,ANNEE,m), ep=epargnesDuMois(p,m),
          rv=renvoisDuMois(p,m,H_JOUR);
    const r=lireJournee(db,raw,ANNEE,m,d,fit,ep[d],H_JOUR,rv[d]);
    const a=affichage(r);
    console.log(qui+" "+d+"/"+pad2(m)+"  "+JSON.stringify(raw));
    console.log("     lu       : poste="+(r.s||"—")+"  heures="+
      (r.h===undefined?"(défaut "+H_JOUR+")":r.h)+"  absence="+(r.a||"—")+
      "  épargne="+(r.epargne||0)+
      ((r.ax&&r.ax.length)?"  codes en plus="+r.ax.join(", "):"")+
      (r.modifie?"  [poste corrigé]":""));
    /* r.s est la prime PAYÉE, r.sp le poste PRESTÉ quand ils diffèrent, et
       c'est r.sp qui décide dans quelle pause la vue du jour range la
       personne. Sans ces deux champs à l'écran on ne peut pas voir pourquoi
       quelqu'un apparaît dans une pause plutôt qu'une autre. */
    console.log("     journée  : prime="+(r.s||"—")+"  presté="+(r.sp||"(idem)")
      +"  code de jour="+(r.jourCode||"—"));
    console.log("     affiché  : "+a.genre+"  « "+a.etiquette+" »  "+a.heures+" h");
  }
  process.exit(0);
}

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
  ["mention non comprise", "la case dit quelque chose, mais un morceau de la cellule reste illisible"],
  ["mention avalée",       "le motif des ateliers la reconnaît, mais elle ne devient AUCUN poste — l'outil croit l'avoir comprise"],
  ["motif trop étroit",    "un motif plus large trouverait davantage dans le même commentaire — l'outil lit moins qu'il ne croit"]
];
const fautes={}; REGLES.forEach(r=>fautes[r[0]]=[]);
let cellules=0, postes=0, absences=0, repos=0, prevus=0;
const incomprises={}, avalees={}, etroits={};

/* --- douzième règle : ce qu'un motif plus large trouverait ---------------
   Deux défauts du 21/09/2026 venaient d'un motif trop étroit, et aucune
   règle ne pouvait les voir : « Poly. Etoh » avalé par ATELIERS, et 568
   « Remplace XXX » perdus faute d'ignorer la casse. Un motif qui lit moins
   qu'il ne croit ne ment pas — il se tait.

   On prend donc les motifs de l'application EUX-MÊMES, découpés dans
   index.html, et on les confronte à une version délibérément plus large.
   L'écart n'est pas une faute : c'est une question. */
const _ids=new Set(db.people.map(p=>p.id));
function _rx(depuis,jusqu){
  const t=part(depuis,jusqu);
  return eval(t.slice(t.indexOf("/"), t.lastIndexOf("/")+3).replace(/,$/,""));
}
const MOTIFS=[
  {nom:"remplacement nommé",
   /* le motif de atelierDuRemplace(), tel qu'il est écrit */
   strict:_rx("rx=/\\bremp","/gi,"),
   /* délibérément plus large que l'application : trois mots de liaison au
      lieu de deux, et l'espace après « remp… » rendu optionnel. */
   large:/\bremp\w*\.?\s*(?:(?:en|au|aux|le|la|les|de|du|des|a|\u00e0)?\s*[\wàâéèêîôû'-]+\s+){0,3}?([A-Za-z]{3})\b/gi,
   garde:t=>_ids.has(String(t).toUpperCase()) && String(t).toUpperCase()!=="PAR"},
  {nom:"plage horaire du commentaire",
   /* plageCommentaire() ELLE-MÊME, et non une copie de son motif : la
      première version de cette règle recopiait le motif ici, et elle a
      continué d'annoncer 38 manques après que index.html eut été corrigé.
      Une règle qui dénonce les copies ne peut pas en être une. */
   strictFn:com=>{ const p=plageCommentaire(com); return p?new Set([String(Math.floor(p[0]))]):new Set(); },
   /* un commentaire porte souvent PLUSIEURS plages et la fonction n'en rend
      qu'une — c'est une autre question que celle d'un motif trop étroit. On
      ne compare donc que la première trouvée de chaque côté. */
   premierSeul:true,
   large:/(\d{1,2})\s*h\s*(?:\d{2})?\s*(?:\u00e0|a|-|\u2013|jusqu\W{0,3}(?:e|au)?)\s*(\d{1,2})\s*h/gi,
   garde:()=>true}
];
function _trouve(rx,com,garde){
  const out=new Set(); let m; rx.lastIndex=0;
  /* « 9 » et « 09 » sont la même heure : on normalise, sans quoi la règle
     se dénoncerait elle-même à chaque plage écrite avec un zéro devant. */
  while((m=rx.exec(com))){
    const v=m[1]; if(!garde(v)) continue;
    out.add(/^\d+$/.test(v)?String(Number(v)):String(v).toUpperCase());
  }
  return out;
}

for(const p of db.people){
  for(let m=1;m<=12;m++){
    const fit=cycleDuMois(p,ANNEE,m), ep=epargnesDuMois(p,m),
          rv=renvoisDuMois(p,m,H_JOUR), nd=daysInMonth(ANNEE,m-1);
    for(let d=1;d<=nd;d++){
      const mmdd=pad2(m)+pad2(d), raw=p.d[mmdd];
      if(raw===undefined) continue;
      cellules++;
      const r=lireJournee(db,raw,ANNEE,m,d,fit,ep[d],H_JOUR,rv[d]);
      const a=affichage(r);
      const cel=(raw[0]||"").trim(), annot=(raw[1]||"").trim();
      /* Une cellule se juge sur ce que l'APPLICATION y lit, pas sur ce que le
         classeur y écrit : « * » est un alias de « - » depuis le 22/09/2026,
         et la règle l'accusait encore d'être illisible. ALIAS_HORAIRE est
         découpé dans index.html, donc la règle suit toute addition future
         sans qu'on y pense. */
      const celA=(COQUILLES&&COQUILLES[cel]!==undefined)?COQUILLES[cel]:cel;
      const vide=(!celA||celA==="-");
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
      /* 7 bis. Le pire angle mort : non pas ce que l'outil déclare ne pas
            savoir lire, mais ce qu'il CROIT avoir lu. ATELIERS reconnaît une
            mention, parseHoraireEntry la tient donc pour comprise — et
            aucun poste n'en sort. « Poly. Etoh » est passé ainsi pendant
            46 journées, invisible aux dix autres règles. */
      [0,1].forEach(c=>{
        const txt=String(raw[c]||"").trim();
        if(!txt || !ATELIERS.test(txt) || posteDepuisNom(txt)) return;
        if(!avalees[txt]) avalees[txt]={n:0, ex:[]};
        avalees[txt].n++;
        if(avalees[txt].ex.length<3) avalees[txt].ex.push(ou+"  "+src);
        fautes["mention avalée"].push(ou+"  "+src);
      });
      /* 7 ter. un motif plus large trouverait-il davantage ? */
      const com=String(raw[2]||"");
      if(com) MOTIFS.forEach(M=>{
        const s1=M.strictFn?M.strictFn(com):_trouve(M.strict,com,M.garde);
        let s2=_trouve(M.large,com,M.garde);
        if(M.premierSeul) s2=new Set([...s2].slice(0,1));
        const plus=[...s2].filter(x=>!s1.has(x));
        if(!plus.length) return;
        const cle=M.nom;
        if(!etroits[cle]) etroits[cle]={n:0, ex:[]};
        etroits[cle].n++;
        if(etroits[cle].ex.length<3) etroits[cle].ex.push(ou+"  "+src+"   → "+plus.join(", "));
        fautes["motif trop étroit"].push(ou+"  "+src);
      });
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
    if(nom==="motif trop étroit"){
      Object.keys(etroits).sort((a,b)=>etroits[b].n-etroits[a].n).forEach(k=>{
        console.log("   "+String(etroits[k].n).padStart(4)+" × «"+k+"»");
        etroits[k].ex.forEach(x=>console.log("          "+x));
      });
    } else if(nom==="mention avalée"){
      Object.keys(avalees).sort((a,b)=>avalees[b].n-avalees[a].n).forEach(k=>{
        console.log("   "+String(avalees[k].n).padStart(4)+" × «"+k+"»");
        avalees[k].ex.slice(0,2).forEach(x=>console.log("          "+x));
      });
    } else if(nom==="mention non comprise"){
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
