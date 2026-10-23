/* LES CONGÉS SCOLAIRES RELUS SUR LE SITE OFFICIEL (le client, le
 * 23/10/2026 : l'agenda des congés scolaires « va vérifier tous les x sur
 * le site enseignement.be ? » — « Yes »).
 *
 * Le décret du 31 mars 2022 fixe la rentrée, la fin d'année, l'hiver et les
 * jours de congé : index.html les calcule (fwbAn). L'automne, la détente et
 * le printemps, eux, sont fixés chaque année par arrêté du Gouvernement ;
 * enseignement.be/calendrier-scolaire publie les années en cours et à
 * venir. Ce robot relit cette page et, pour chaque année « de
 * l'enseignement obligatoire », n'en prend QUE ces trois périodes.
 *
 * Rien n'entre sans avoir été recoupé :
 *   - chaque période commence un lundi, dure deux semaines et tombe dans
 *     sa saison ;
 *   - la rentrée et le début de l'été que la page annonce sont ceux que le
 *     décret donne pour cette année (fwbAn, découpée dans index.html) ;
 *   - le jour et le mois des vacances d'hiver aussi. L'ANNÉE n'est pas
 *     recoupée : la page du 23/10/2026 écrit « du lundi 25 décembre 2029 au
 *     dimanche 7 janvier 2029 » pour 2028-2029, une coquille.
 * Une année qui ne passe pas est laissée de côté, dite, et le code de
 * retour vaut 1 : le flux GitHub échoue et prévient. Une année que la page
 * ne montre plus (les années passées) reste dans FWB_ARRETES.
 *
 *   node tools/conges-auto.js                 à blanc : dit ce qui changerait
 *   node tools/conges-auto.js --installer     écrit index.html (FWB_ARRETES),
 *                                             sw.js (V+1), cal/conges-scolaires.ics
 *   node tools/conges-auto.js --pousser       et committe, pousse sur main
 *   --page=FICHIER                            une page enregistrée au lieu du site
 *
 * Lancé le 1er de chaque mois par .github/workflows/conges-scolaires.yml
 * (le client : « est-ce réellement utile de vérifier trop souvent ? » ; les
 * calendriers paraissent deux à trois ans à l'avance).
 */
const fs=require("fs"), path=require("path"), {execFileSync}=require("child_process");
const RACINE=path.join(__dirname,".."), PAGE=path.join(RACINE,"index.html"), SW=path.join(RACINE,"sw.js");
const SITE="https://www.enseignement.be/calendrier-scolaire";
const ARGS=process.argv.slice(2), POUSSER=ARGS.indexOf("--pousser")>=0, INSTALLER=POUSSER||ARGS.indexOf("--installer")>=0;
const FICHIER=(ARGS.filter(a=>a.indexOf("--page=")===0)[0]||"").slice(7);

const H=fs.readFileSync(PAGE,"utf8");
function part(a,b){ const i=H.indexOf(a); if(i<0) throw new Error("introuvable dans index.html : "+a); return H.slice(i,H.indexOf(b,i)+b.length); }
const BLOC=part("var FWB_ARRETES=","\n};");
eval(part("function easter(","\n}")+"\n"+BLOC+"\n"+part("function fwbAn(","\n}"));
const AVANT=JSON.parse(JSON.stringify(FWB_ARRETES));

const MOIS=["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"];
const RX_DATE=/(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+(\d{1,2})\s*(?:er)?\s+([a-zéèêûô]+)\s+(\d{4})/i;
function date(m){ const k=MOIS.indexOf(m[2].toLowerCase().replace("aout","août").replace("fevrier","février").replace("decembre","décembre"));
  return k<0?null:new Date(+m[3],k,+m[1]); }
function iso(d){ return d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0"); }
function plus(x,n){ return new Date(x.getFullYear(),x.getMonth(),x.getDate()+n); }
function texte(html){
  const ent={nbsp:" ",amp:"&",quot:"\"",apos:"'",rsquo:"'",lsquo:"'",eacute:"é",egrave:"è",ecirc:"ê",agrave:"à",acirc:"â",ccedil:"ç",ucirc:"û",icirc:"î",ocirc:"ô",laquo:"«",raquo:"»"};
  /* « 1<sup>er</sup>&nbsp;novembre » : l'exposant reste collé au chiffre */
  return html.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/gi,"").replace(/<\/?sup[^>]*>/gi,"").replace(/<[^>]+>/g,"\n")
    .replace(/&#x([0-9a-f]+);/gi,(_,h)=>String.fromCharCode(parseInt(h,16))).replace(/&#(\d+);/g,(_,d)=>String.fromCharCode(+d))
    .replace(/&([a-z]+);/gi,(t,n)=>ent[n.toLowerCase()]!==undefined?ent[n.toLowerCase()]:t).replace(/[’‘]/g,"'")
    .split("\n").map(l=>l.replace(/\s+/g," ").trim()).filter(Boolean);
}

/* les sections « Calendrier de l'enseignement obligatoire AAAA-AAAA »
   suivies de « Rentrée scolaire » (les mêmes titres, en tête de page, ne
   sont que des liens) */
function sections(lignes){
  const out=[];
  lignes.forEach((l,i)=>{
    const m=/^Calendrier de l'enseignement obligatoire (\d{4})-(\d{4})$/.exec(l);
    if(!m || !/^Rentrée scolaire/.test(lignes[i+1]||"")) return;
    let k=i+1; while(k<lignes.length && !/^Calendrier /.test(lignes[k])) k++;
    out.push({a:+m[1], b:+m[2], t:lignes.slice(i+1,k).join(" ")});
  });
  return out;
}
const PERIODES=[["automne",/Vacances d'automne \(Toussaint\)/i,[9,10],0],["detente",/Vacances de détente \(Carnaval\)/i,[0,2],1],["printemps",/Vacances de printemps \(Pâques\)/i,[2,4],1]];
function lire(s){
  const r={a:s.a, fautes:[]};
  if(s.b!==s.a+1) r.fautes.push("années "+s.a+"-"+s.b);
  function apres(rx){ const i=s.t.search(rx); return i<0?null:s.t.slice(i); }
  const re=apres(/Rentrée scolaire/), mr=re&&RX_DATE.exec(re); r.rentree=mr?date(mr):null;
  const ete=apres(/vacances d'été débutent le/i), me=ete&&RX_DATE.exec(ete); r.ete=me?date(me):null;
  const hi=apres(/Vacances d'hiver \(Noël\)/i), mh=hi&&RX_DATE.exec(hi); r.hiver=mh?date(mh):null;
  PERIODES.forEach(([k,rx,saison,decale])=>{
    const t=apres(rx); if(!t){ r.fautes.push(k+" introuvable"); return; }
    const m=/^[^D]*Du\s+(.*?)\s+au\s+(.*?\d{4})/.exec(t), d1=m&&RX_DATE.exec(m[1]), d2=m&&RX_DATE.exec(m[2]);
    if(!d1||!d2){ r.fautes.push(k+" : dates illisibles"); return; }
    const a=date(d1), b=date(d2);
    if(!a||!b){ r.fautes.push(k+" : mois inconnu"); return; }
    if(a.getDay()!==1) r.fautes.push(k+" : ne commence pas un lundi ("+iso(a)+")");
    if(+b!==+plus(a,13) && +b!==+plus(a,11)) r.fautes.push(k+" : pas deux semaines ("+iso(a)+" → "+iso(b)+")");
    if(a.getFullYear()!==s.a+decale || a.getMonth()<saison[0] || a.getMonth()>saison[1]) r.fautes.push(k+" : hors de sa saison ("+iso(a)+")");
    r[k]=a;
  });
  return r;
}

/* ce que le décret donne, avec les trois périodes lues : la rentrée (qui
   dépend des jours de classe), le lendemain de la fin, l'hiver */
function recouper(r){
  const garde=FWB_ARRETES[r.a];
  FWB_ARRETES[r.a]={automne:iso(r.automne), detente:iso(r.detente), printemps:iso(r.printemps), src:"essai"};
  const x=fwbAn(r.a);
  if(garde) FWB_ARRETES[r.a]=garde; else delete FWB_ARRETES[r.a];
  const h=x.periodes.filter(q=>q.k==="hiver")[0].d;
  if(!r.rentree) r.fautes.push("rentrée illisible");
  else if(+r.rentree!==+x.rentree) r.fautes.push("rentrée "+iso(r.rentree)+", le décret donne "+iso(x.rentree));
  if(!r.ete) r.fautes.push("début de l'été illisible");
  else if(+r.ete!==+plus(x.fin,1)) r.fautes.push("été dès le "+iso(r.ete)+", le décret donne "+iso(plus(x.fin,1)));
  if(!r.hiver) r.fautes.push("hiver illisible");
  else if(r.hiver.getDate()!==h.getDate()||r.hiver.getMonth()!==h.getMonth()) r.fautes.push("hiver le "+iso(r.hiver)+", le décret donne "+iso(h));
}

async function page(){
  if(FICHIER) return fs.readFileSync(FICHIER,"utf8");
  const r=await fetch(SITE,{headers:{"User-Agent":"BioWanze (agenda des congés scolaires ; github.com/cronobots/GROUPS)"},signal:AbortSignal.timeout(30000)});
  if(!r.ok) throw new Error("HTTP "+r.status);
  return r.text();
}

(async()=>{
  let html;
  try{ html=await page(); }
  catch(e){ console.log("enseignement.be injoignable ("+e.message+") : rien de changé, on réessaiera le mois prochain."); process.exit(0); }
  const S=sections(texte(html));
  if(!S.length){ console.log("ÉCART  aucune section « Calendrier de l'enseignement obligatoire » lue : la page a changé de forme."); process.exit(1); }
  const auj=new Date(), releve=String(auj.getDate()).padStart(2,"0")+"/"+String(auj.getMonth()+1).padStart(2,"0")+"/"+auj.getFullYear();
  let fautes=0, change=[];
  S.forEach(s=>{
    const r=lire(s);
    if(!r.fautes.length) recouper(r);
    const nom=s.a+"-"+s.b;
    if(r.fautes.length){ fautes++; r.fautes.forEach(f=>console.log("ÉCART  "+nom+" : "+f+" — année laissée de côté")); return; }
    const neuf={automne:iso(r.automne), detente:iso(r.detente), printemps:iso(r.printemps)}, vieux=FWB_ARRETES[s.a];
    if(vieux && vieux.automne===neuf.automne && vieux.detente===neuf.detente && vieux.printemps===neuf.printemps){ console.log(nom+" : déjà à jour."); return; }
    neuf.src="enseignement.be, relevé le "+releve;
    console.log(nom+(vieux?" : CHANGÉ sur le site (":" : NOUVELLE (")+"automne "+neuf.automne+", détente "+neuf.detente+", printemps "+neuf.printemps+")");
    FWB_ARRETES[s.a]=neuf; change.push(nom);
  });
  if(change.length && INSTALLER){
    const lignes=Object.keys(FWB_ARRETES).map(Number).sort((a,b)=>a-b).map(a=>{ const x=FWB_ARRETES[a];
      return "  "+a+":{automne:\""+x.automne+"\", detente:\""+x.detente+"\", printemps:\""+x.printemps+"\", src:\""+x.src.replace(/"/g,"'")+"\"}"; });
    fs.writeFileSync(PAGE,H.replace(BLOC,"var FWB_ARRETES={\n"+lignes.join(",\n")+"\n};"));
    const sw=fs.readFileSync(SW,"utf8"), v=/var V = "nfdm-v(\d+)";/.exec(sw);
    fs.writeFileSync(SW,sw.replace(v[0],'var V = "nfdm-v'+(+v[1]+1)+'";'));
    execFileSync("node",[path.join(__dirname,"verifier-conges-scolaires.js")],{stdio:"inherit"});
  }
  /* l'agenda, chaque fois : il avance aussi d'une année au 1er janvier */
  if(INSTALLER) execFileSync("node",[path.join(__dirname,"verifier-calendrier.js"),"--agendas",path.join(RACINE,"cal"),"--conges-seulement"],{stdio:"inherit"});
  if(POUSSER){
    const git=(...a)=>execFileSync("git",["-C",RACINE].concat(a),{encoding:"utf8"});
    git("add","index.html","sw.js","cal/conges-scolaires.ics");
    if(git("status","--porcelain","--","index.html","sw.js","cal/conges-scolaires.ics").trim()){
      git("commit","-q","-m",(change.length?"Congés scolaires : "+change.join(", ")+" relu(s) sur enseignement.be":"Congés scolaires : l'agenda avance d'une année")
        +" (mise à jour automatique)\n\nRecoupé avec le décret du 31 mars 2022, installé par .github/workflows/conges-scolaires.yml.");
      git("push","-q","origin","HEAD:main");
      console.log("Poussé sur main.");
    } else console.log("Rien à pousser.");
  } else if(change.length && !INSTALLER) console.log("À blanc : rien d'écrit (--installer pour écrire).");
  if(!change.length && !fautes) console.log("Rien de neuf sur enseignement.be ("+S.length+" années lues).");
  process.exit(fautes?1:0);
})();
