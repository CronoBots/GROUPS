#!/usr/bin/env node
/* LE PARCOURS DE L'APPLICATION, d'un bout à l'autre, au navigateur.
   node tools/parcours.js            → tout ; code 1 à la moindre faute
   node tools/parcours.js --vite     → téléphone portrait seulement
   node tools/parcours.js --statique [fichier]
                                     → les requêtes du téléphone couché
                                       seules, sans navigateur

   Le client, le 28/10/2026 (« go complet ») : les essais au navigateur
   vivaient dans des scripts jetables, perdus à chaque session. Celui-ci
   reste dans le dépôt et se relance avant chaque envoi qui touche
   index.html.

   Il sert le dossier lui-même (aucune dépendance que Playwright, déjà
   présent), simule la base BIOWANZE (aucun appel réel : les réponses sont
   des listes vides, un compte et son rôle), et ouvre chaque onglet pour
   chaque rôle et chaque écran : téléphone portrait 320 et 390, iPhone aux
   zones protégées simulées, téléphone couché, PC. Puis il coupe le réseau
   et recharge : la page doit tenir hors ligne.

   UN SEUL THÈME, le sombre : le clair, ajouté le 29/10/2026, est retiré
   le 03/11/2026 (le client : « nous allons adapter celui-ci plus tard »).

   Faute (code 1) : une requête du téléphone couché qui diverge des
   autres, une accolade CSS orpheline, une boîte du système (confirm,
   alert, prompt : trois contrôles sans navigateur, faits d'abord), une règle CSS écrite que le navigateur jette, une
   erreur JavaScript, un débordement horizontal de la
   page, un cadre posé sous la barre d'onglets (portrait) ou sous le rail
   (couché), une page blanche hors ligne, un TEXTE SOUS LE SEUIL de
   contraste WCAG de sa taille (4,5:1, 3:1 à 24 px ou 18,66 px gras), sur le
   fond réellement peint derrière lui. Le reste se lit dans la sortie.
   Aucun nom : les comptes simulés n'ont qu'un trigramme. */
"use strict";
const http=require("http"), fs=require("fs"), path=require("path");
let chromium;
try{ ({chromium}=require("playwright")); }catch(e){ ({chromium}=require("/opt/node-tools/node_modules/playwright")); }

const RACINE=path.join(__dirname,"..");
const TYPES={".html":"text/html; charset=utf-8",".js":"text/javascript",".json":"application/json",".css":"text/css",
  ".png":"image/png",".jpg":"image/jpeg",".svg":"image/svg+xml",".webmanifest":"application/manifest+json",".ics":"text/calendar",".woff2":"font/woff2"};
function servir(){
  return new Promise(ok=>{
    const srv=http.createServer((rq,rs)=>{
      let u=decodeURIComponent(rq.url.split("?")[0]); if(u.endsWith("/")) u+="index.html";
      const f=path.join(RACINE,path.normalize(u));
      if(!f.startsWith(RACINE)||!fs.existsSync(f)||fs.statSync(f).isDirectory()){ rs.writeHead(404); rs.end(); return; }
      rs.writeHead(200,{"Content-Type":TYPES[path.extname(f)]||"application/octet-stream","Cache-Control":"no-cache"});
      fs.createReadStream(f).pipe(rs);
    }).listen(0,"127.0.0.1",()=>ok(srv));
  });
}

const ECRANS=[
  {nom:"téléphone 320",w:320,h:568,mobile:true},
  {nom:"téléphone 390",w:390,h:844,mobile:true},
  {nom:"iPhone 390 (zones protégées)",w:390,h:844,mobile:true,zones:{top:59,bottom:34,left:0,right:0}},
  {nom:"couché 844",w:844,h:390,mobile:true},
  {nom:"iPhone couché (encoche)",w:844,h:390,mobile:true,zones:{top:0,bottom:21,left:47,right:47}},
  {nom:"PC 1280",w:1280,h:800,mobile:false}
];
const ROLES=[null,"operateur","hierarchie","rh"];

/* LE TÉLÉPHONE COUCHÉ, UNE SEULE DÉFINITION (28/10/2026). CSS n'a pas de
   requête média nommée que les navigateurs comprennent : la condition est
   recopiée dans une soixantaine de blocs et dans trois matchMedia. Une
   copie qui diverge (501px, 1100px…) casserait une seule mise en page,
   sans erreur. Toute requête qui parle de 760/761 px ou de 500 px de haut
   doit donc être, au caractère près, l'une de celles-ci : « téléphone »
   (portrait étroit ou couché bas) et son complément exact. */
const TEL="(orientation:landscape) and (max-height:500px) and (max-width:1099px)";
const REQUETES_ADMISES=[
  "(max-width:760px), "+TEL,
  TEL,
  "(max-width:760px) and (max-height:640px), "+TEL,
  "(min-width:761px) and (min-height:500.01px), (min-width:761px) and (orientation:portrait), (min-width:1100px)",
  "(min-width:761px) and (max-width:1099px) and (min-height:500.01px), (min-width:761px) and (max-width:1099px) and (orientation:portrait)",
  "(min-width:761px) and (max-width:1279px) and (min-height:500.01px), (min-width:761px) and (max-width:1279px) and (orientation:portrait), (min-width:1100px) and (max-width:1279px)"
];
function requetesDivergentes(fichier){
  const src=fs.readFileSync(fichier,"utf8"), f=[];
  const re=/@media\s*([^{]*)\{|matchMedia\(\s*"([^"]*)"/g; let m;
  while((m=re.exec(src))){
    const q=(m[1]||m[2]||"").trim();
    if(!/76[01]px|max-height:500px|500\.01px/.test(q)) continue;
    if(REQUETES_ADMISES.indexOf(q)<0) f.push("ligne "+src.slice(0,m.index).split("\n").length+" : "+q.slice(0,140));
  }
  return f;
}
/* JAMAIS LA BOÎTE DU SYSTÈME (le client, le 09/10/2026 pour la
   déconnexion, puis le 04/11/2026 pour l'effacement d'un message : « le
   message de suppression est horrible »). confirm(), alert() et prompt()
   ouvrent la boîte du navigateur, l'adresse du site en titre ; la page a
   confirmerPro(). Cherché dans les <script>, commentaires ôtés. */
function boitesSysteme(fichier){
  const src=fs.readFileSync(fichier,"utf8"), f=[], re=/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g; let m;
  while((m=re.exec(src))){
    const debut=src.slice(0,m.index+m[0].indexOf(">")+1).split("\n").length;
    /* les commentaires ôtés en gardant les sauts de ligne, pour compter juste */
    const code=m[1].replace(/\/\*[\s\S]*?\*\//g,c=>c.replace(/[^\n]/g," ")).replace(/(^|[\s;{}])\/\/[^\n]*/g,"$1");
    /* et sous la forme window.prompt( (05/11/2026 : trois appels y
       échappaient, le point excluant la forme) ; « p.prompt() », l'invite
       d'installation, reste admise */
    const r=/(^|[^\w.$]|\b(?:window|self|top)\.)(confirm|alert|prompt)\s*\(/g; let k;
    while((k=r.exec(code))) f.push("ligne "+(debut+code.slice(0,k.index).split("\n").length-1)+" : "+k[2]+"()");
  }
  return f;
}
/* UNE ACCOLADE ORPHELINE NE FAIT AUCUN BRUIT (29/10/2026). Une « } » de
   trop au premier niveau d'un <style> devient le début du sélecteur
   suivant, et le navigateur jette cette règle-là sans rien dire : celle
   de la case fusionnée du Planning est restée trois jours sans effet.
   Chaque bloc <style> doit refermer exactement ce qu'il ouvre (hors
   commentaires et chaînes). */
function accoladesOrphelines(fichier){
  const src=fs.readFileSync(fichier,"utf8"), f=[], re=/<style[^>]*>([\s\S]*?)<\/style>/g; let m;
  while((m=re.exec(src))){
    const s=m[1], base=m.index+m[0].indexOf(">")+1; let d=0;
    for(let i=0;i<s.length;i++){
      if(s.startsWith("/*",i)){ const j=s.indexOf("*/",i+2); i=j<0?s.length:j+1; continue; }
      const c=s[i];
      if(c==='"'||c==="'"){ i++; while(i<s.length&&s[i]!==c){ if(s[i]==="\\") i++; i++; } continue; }
      if(c==="{") d++;
      else if(c==="}"){ d--; if(d<0){ f.push("ligne "+src.slice(0,base+i).split("\n").length+" : « } » sans ouvrante"); d=0; } }
    }
    if(d>0) f.push("ligne "+src.slice(0,base).split("\n").length+" : bloc <style> laissé ouvert ("+d+")");
  }
  return f;
}
/* …et le navigateur le confirme : chaque sélecteur écrit dans un <style>
   doit se retrouver parmi les règles qu'il a retenues. Deux fautes qui
   s'annulent (une « { » de trop, une « } » plus loin) échappent au compte
   des accolades ; une règle jetée, non. */
function selecteursEcrits(fichier){
  const src=fs.readFileSync(fichier,"utf8"), re=/<style[^>]*>([\s\S]*?)<\/style>/g; let m, n=0;
  while((m=re.exec(src))){
    const s=m[1].replace(/\/\*[\s\S]*?\*\//g,""); let tete=0, prof=0;
    for(let k=0;k<s.length;k++){ const c=s[k];
      if(c==='"'||c==="'"){ k++; while(k<s.length&&s[k]!==c){ if(s[k]==="\\") k++; k++; } continue; }
      if(c==="{"){ const t=s.slice(tete,k).trim(); if(t.charAt(0)!=="@"&&!/^(from|to|\d+%)/.test(t)) n++; prof++; tete=k+1; }
      else if(c==="}"){ prof--; tete=k+1; }
      else if(c===";"&&prof===0) tete=k+1; }
  }
  return n;
}
/* « go: » ouvre une sous-page par son lien (data-go), toutes ses parties
   dépliées : « Infos et aide » (30/10/2026) se mesure en entier */
const VUES=[["Accueil","tab-horaire"],["Planning","tab-jour"],["Équipes","tab-equipe"],["Horaire","ws:planning"],["Infos et aide","go:aide"]];

async function ouvrir(nav,url,ecran,role,theme){
  theme=theme||"dark";
  const ctx=await nav.newContext({viewport:{width:ecran.w,height:ecran.h},isMobile:ecran.mobile,hasTouch:ecran.mobile,colorScheme:theme});
  await ctx.addInitScript(([role,theme])=>{ try{ if(localStorage.getItem("__p")) return; localStorage.setItem("__p","1");
    localStorage.setItem("ui/prefillId",JSON.stringify("VBN"));
    if(role){ localStorage.setItem("account/current",JSON.stringify({role:"employe",tri:"VBN",cat:"",email:"x@exemple.be",base:role,at:"x"}));
      localStorage.setItem("base/session",JSON.stringify({access:"a",refresh:"r",exp:Date.now()+9e12,email:"x@exemple.be"})); } }catch(e){} },[role,theme]);
  const page=await ctx.newPage(); page.fautes=[];
  page.on("pageerror",e=>page.fautes.push("erreur JS : "+e.message.slice(0,140)));
  await page.route(/supabase\.co\//,r=>{ const u=r.request().url();
    r.fulfill({status:200,contentType:"application/json",body:u.includes("mon_compte")?JSON.stringify([{role:role||"operateur",valide:true,trigramme:"VBN"}]):"[]"}); });
  await page.goto(url); await page.waitForTimeout(3000);
  if(ecran.zones) await page.evaluate(z=>{ document.querySelectorAll("style").forEach(s=>{ s.textContent=s.textContent
      .replace(/env\(safe-area-inset-top(,[^)]*)?\)/g,z.top+"px").replace(/env\(safe-area-inset-bottom(,[^)]*)?\)/g,z.bottom+"px")
      .replace(/env\(safe-area-inset-left(,[^)]*)?\)/g,z.left+"px").replace(/env\(safe-area-inset-right(,[^)]*)?\)/g,z.right+"px"); });
    window.dispatchEvent(new Event("resize")); },ecran.zones);
  page.ctx=ctx;
  return page;
}
async function aller(page,cible){
  await page.evaluate(c=>{
    if(c.indexOf("ws:")===0){ const s=c.slice(3); const b=[...document.querySelectorAll('[data-side-ws="'+s+'"]')].find(x=>x.offsetParent); if(b) b.click(); return; }
    if(c.indexOf("go:")===0){ const b=document.createElement("button"); b.setAttribute("data-go",c.slice(3)); document.body.appendChild(b); b.click(); b.remove();
      const v=document.getElementById("v-"+c.slice(3)); if(v) v.querySelectorAll("details").forEach(d=>{ d.open=true; }); return; }
    const t=document.getElementById(c); if(t) t.click(); },cible);
  await page.waitForTimeout(1400);
}
/* ce que la page montre de travers : débordement, cadre sous la barre */
function constater(){
  const W=innerWidth, H=innerHeight, f=[];
  if(document.documentElement.scrollWidth>W+1) f.push("débordement horizontal ("+document.documentElement.scrollWidth+" px pour "+W+")");
  const nav=document.querySelector(".navwrap:not([hidden])>.tabs");
  const nr=nav&&nav.getClientRects().length?nav.getBoundingClientRect():null;
  const g=document.getElementById("grille");
  const cadre=(g&&!g.hidden)?document.querySelector(".ws-s:not([hidden])"):[...document.querySelectorAll("section.panel")].find(x=>!x.hidden&&x.offsetParent);
  const cr=cadre&&cadre.getBoundingClientRect();
  if(nr&&cr&&nr.width<nr.height){ if(cr.left<nr.right-1) f.push("cadre sous le rail ("+Math.round(cr.left)+" < "+Math.round(nr.right)+")"); }
  else if(nr&&cr&&g&&!g.hidden&&cr.bottom>nr.top+1&&nr.top<H) f.push("cadre sous la barre ("+Math.round(cr.bottom)+" > "+Math.round(nr.top)+")");
  /* LE CONTRASTE DE CHAQUE TEXTE VISIBLE, sur le fond réellement peint
     derrière lui : on remonte les parents jusqu'à une couleur opaque, en
     composant les transparences. Un dégradé ou une image derrière le texte
     le laisse de côté (le fond n'est pas une couleur). Trois au plus par
     vue, un par sélecteur. */
  function rgb(c){ const m=c.match(/rgba?\(([^)]+)\)/); if(!m) return null; const p=m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}; }
  function lum(c){ const k=v=>{ v/=255; return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4); }; return 0.2126*k(c.r)+0.7152*k(c.g)+0.0722*k(c.b); }
  function sur(h,b){ return {r:h.r*h.a+b.r*(1-h.a), g:h.g*h.a+b.g*(1-h.a), b:h.b*h.a+b.b*(1-h.a), a:1}; }
  const vus={}; let n=0;
  document.querySelectorAll("body *").forEach(e=>{
    if(n>=3||(!e.offsetParent&&getComputedStyle(e).position!=="fixed")) return;
    let txt=""; e.childNodes.forEach(c=>{ if(c.nodeType===3) txt+=c.textContent; }); txt=txt.trim(); if(!txt) return;
    const r=e.getBoundingClientRect(); if(r.width<1||r.height<1) return;
    const cs=getComputedStyle(e), px=parseFloat(cs.fontSize); if(px<1||cs.visibility==="hidden"||+cs.opacity===0) return;
    const pile=[]; let x=e, image=false;
    while(x&&x.nodeType===1){ const s=getComputedStyle(x); if(s.backgroundImage!=="none"&&!/url\(/.test(s.backgroundImage)) image=true; const c=rgb(s.backgroundColor); if(c&&c.a>0){ pile.push(c); if(c.a>=0.99) break; } x=x.parentElement; }
    if(image) return;
    let fond=rgb(getComputedStyle(document.body).backgroundColor)||{r:255,g:255,b:255,a:1}; if(fond.a<1) fond={r:255,g:255,b:255,a:1};
    for(let i=pile.length-1;i>=0;i--) fond=sur(pile[i],fond);
    const c=rgb(cs.color); if(!c) return; const enc=sur(c,fond);
    const L1=lum(enc), L2=lum(fond), ct=(Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
    const seuil=(px>=24||(px>=18.66&&+cs.fontWeight>=700))?3:4.5;
    if(ct>=seuil-0.01) return;
    const k=e.tagName.toLowerCase()+"."+[...e.classList].slice(0,2).join(".");
    if(vus[k]) return; vus[k]=1; n++;
    f.push("contraste "+(Math.round(ct*100)/100)+":1 « "+txt.slice(0,24)+" » ("+k+", "+px+" px)");
  });
  return f;
}

(async()=>{
  /* d'abord le contrôle sans navigateur, en une fraction de seconde ;
     « --statique [fichier] » ne fait que lui (l'épreuve sur une copie) */
  const iS=process.argv.indexOf("--statique");
  const cible=iS>=0&&process.argv[iS+1]?process.argv[iS+1]:path.join(RACINE,"index.html");
  const div=requetesDivergentes(cible), acc=accoladesOrphelines(cible), boi=boitesSysteme(cible);
  div.forEach(l=>console.log("✗ requête du téléphone couché qui diverge, "+l));
  acc.forEach(l=>console.log("✗ accolade CSS, "+l));
  boi.forEach(l=>console.log("✗ boîte du système (confirmerPro à la place), "+l));
  if(iS>=0){ console.log(div.length?div.length+" requête(s) divergente(s)":"requêtes du téléphone couché : toutes identiques");
    console.log(acc.length?acc.length+" accolade(s) orpheline(s)":"accolades CSS : toutes appariées");
    console.log(boi.length?boi.length+" boîte(s) du système":"boîtes du système : aucune"); process.exit(div.length||acc.length||boi.length?1:0); }
  const vite=process.argv.indexOf("--vite")>=0;
  const srv=await servir(), url="http://127.0.0.1:"+srv.address().port+"/";
  const nav=await chromium.launch();
  const ecrans=vite?ECRANS.filter(e=>e.nom==="téléphone 390"):ECRANS;
  /* un seul thème, le sombre : le clair est retiré le 03/11/2026 (le
     client : « supprimer le thème clair, nous allons adapter celui-ci plus
     tard ») */
  const passes=[];
  ecrans.forEach(e=>passes.push([e,"dark"]));
  let fautes=div.length+acc.length+boi.length, essais=1;
  /* EN PARALLÈLE (le client, le 03/11/2026 : « pourquoi ce parcours
     complet ? », après six minutes d'attente à chaque envoi) : les mêmes
     passes — chaque écran, thème et rôle dans son propre contexte —, trois
     à la fois sur le même navigateur ; les résultats s'écrivent dans
     l'ordre d'avant. Rien n'est retiré : seul le temps change. */
  const travaux=[]; for(const [ecran,theme] of passes) for(const role of (vite?["hierarchie"]:ROLES)) travaux.push({ecran,theme,role});
  const res=new Array(travaux.length);
  const iRech=travaux.findIndex(x=>x.role==="hierarchie");
  async function faire(i){ const {ecran,theme,role}=travaux[i];
    const page=await ouvrir(nav,url,ecran,role,theme); const lignes=[], avant=[]; let n=0;
    if(i===0){ n++;
      const ecrits=selecteursEcrits(path.join(RACINE,"index.html"));
      const retenus=await page.evaluate(()=>{ let n=0; const p=l=>{ for(const x of l){ if(x.selectorText!==undefined) n++; if(x.cssRules) p(x.cssRules); } };
        /* la feuille que la page écrit elle-même (la disposition de l'Accueil
           personnalisable, data-genere) n'est pas dans le fichier : hors du compte */
        [...document.styleSheets].forEach(s=>{ if(s.ownerNode&&s.ownerNode.tagName==="STYLE"&&!s.ownerNode.hasAttribute("data-genere")) p(s.cssRules); }); return n; });
      if(ecrits!==retenus) avant.push({faute:true, txt:"✗ règles CSS : "+ecrits+" écrites, "+retenus+" retenues par le navigateur"});
      else avant.push({faute:false, txt:"✓ règles CSS : les "+ecrits+" écrites, toutes retenues"}); }
    for(const [nom,cible] of VUES){
      if((cible.indexOf("ws:")===0||cible.indexOf("go:")===0)&&!role) continue;
      await aller(page,cible); n++;
      const f=await page.evaluate(constater);
      if(f.length) lignes.push(nom+" : "+f.join(" ; "));
      if(cible.indexOf("ws:")===0||cible.indexOf("go:")===0) await aller(page,"tab-horaire");
    }
    /* LES ONGLETS RÉPONDENT AU CLIC (le 03/11/2026 : ceux de la Recherche,
       Absence et Remplaçant, ne répondaient plus depuis la v1304 — un
       sélecteur des Effectifs à la même classe leur prenait leurs
       écouteurs ; les captures, elles, restaient justes) */
    if(i===iRech){ n++;
      await aller(page,"go:recherche");
      for(const k of ["absence","recherche","conge"]){
        await page.click("#caOng-"+k).catch(()=>{});
        await page.waitForTimeout(250);
        const ok=await page.evaluate(k=>{ const b=document.getElementById("caOng-"+k); return !!b&&b.getAttribute("aria-selected")==="true"; },k);
        if(!ok) lignes.push("Recherche : l'onglet « "+k+" » ne répond pas au clic");
      } }
    /* UNE SEULE FICHE DE L'USINE (05/11/2026) : sur l'iPhone couché, 844 px
       de fenêtre mais 670 px d'Accueil, la largeur de la fenêtre envoyait
       l'usine au PC alors que l'Accueil était « téléphone » ; un poste
       touché ouvrait la bulle ET le panneau. On touche le premier poste de
       la légende (téléphone) ou de la bande d'état (PC) */
    if(role==="hierarchie"){
      await aller(page,"tab-horaire");
      const cible=await page.evaluate(()=>{ const vis=e=>!!e&&getComputedStyle(e).display!=="none"&&e.getClientRects().length>0;
        const u=document.getElementById("usineCard"); if(!vis(u)) return null;
        const l=[...document.querySelectorAll("#uspListe .usp-li,#uspEtat .usp-st")].find(vis);
        return l?(l.closest("#uspListe")?"#uspListe .usp-li":"#uspEtat .usp-st"):null; });
      if(cible){ n++;
        const b=page.locator(cible).first(); await b.scrollIntoViewIfNeeded().catch(()=>{});
        if(ecran.mobile) await b.tap({force:true}).catch(()=>{}); else await b.click({force:true}).catch(()=>{});
        await page.waitForTimeout(400);
        const f=await page.evaluate(()=>{ const vis=e=>!!e&&getComputedStyle(e).display!=="none"&&e.getClientRects().length>0;
          return {bulle:vis(document.getElementById("uspPop")), panneau:vis(document.querySelector("#usineCard .us-panneau"))}; });
        if(f.bulle&&f.panneau) lignes.push("L'usine en direct : la fiche du poste s'ouvre deux fois (bulle et panneau)");
        if(!f.bulle&&!f.panneau) lignes.push("L'usine en direct : le poste touché n'ouvre aucune fiche");
        await page.keyboard.press("Escape").catch(()=>{}); await page.waitForTimeout(200); } }
    /* LA BARRE DIT OÙ L'ON EST (05/11/2026) : la vue ouverte allume son
       onglet, ou « Plus » quand son onglet est caché — jamais les deux,
       jamais aucun. Au téléphone, les Effectifs ouverts par « Plus »
       n'allumaient rien ; à la tablette, la Recherche allumait les deux */
    if(role==="hierarchie"){ n++;
      for(const v of ["horaire","jour","equipe","salaire","rh","recherche"]){
        await page.evaluate(v=>{ const b=document.createElement("button"); b.setAttribute("data-go",v); document.body.appendChild(b); b.click(); b.remove(); },v);
        await page.waitForTimeout(350);
        const r=await page.evaluate(()=>{ const vu=b=>!!b&&b.offsetParent!==null;
          const sel=[...document.querySelectorAll(".tabs button[aria-selected='true']")].filter(vu).length;
          const t=document.getElementById("tab-plus"); return {sel:sel, plus:vu(t)&&t.classList.contains("actif")?1:0}; });
        if(r.sel+r.plus!==1) lignes.push("Barre : la vue « "+v+" » allume "+(r.sel+r.plus)+" entrée(s) ("+r.sel+" onglet(s), « Plus » "+(r.plus?"allumé":"éteint")+")");
      }
      await aller(page,"tab-horaire"); }
    /* LES PAGES DE L'ACCUEIL (05/11/2026) : en mode Modifier, un widget
       passe sur la page de droite (Maj et →) ; il y est seul, les points
       en montrent trois ; au téléphone, un balayage vers la droite ramène
       à la page principale ; revenu, l'Accueil est inchangé et Échap
       ferme sans rien demander */
    if(role==="hierarchie"){ n++;
      await aller(page,"tab-horaire");
      await page.evaluate(()=>{ const b=document.querySelector("[data-acc-editer]"); if(b) b.click(); }); await page.waitForTimeout(500);
      const k=await page.evaluate(()=>{ const b=[...document.querySelectorAll(".acc-b:not(.app)")].find(x=>x.getClientRects().length); return b?b.getAttribute("data-acc-pour"):null; });
      const etat=()=>page.evaluate(k=>{ const pts=document.getElementById("accPoints"), vis=[...document.querySelectorAll("#v-horaire [data-w]")].filter(e=>e.getClientRects().length).map(e=>e.getAttribute("data-w"));
        return {pts:pts&&!pts.hidden?pts.children.length:0, cur:pts?[...pts.children].findIndex(x=>x.getAttribute("aria-current")==="page"):-1, seul:vis.length===1&&vis[0]===k, vis:vis.length}; },k);
      if(!k) lignes.push("Pages : aucun widget à déplacer en mode Modifier");
      else {
        await page.focus('.acc-b[data-acc-pour="'+k+'"] .acc-bouger'); await page.keyboard.press("Shift+ArrowRight"); await page.waitForTimeout(400);
        const e1=await etat();
        /* l'Accueil large n'a pas de pages (le client, le 05/11/2026) :
           ni points, ni widget parti */
        if(await page.evaluate(()=>document.getElementById("v-horaire").classList.contains("acc-large"))){
          if(e1.pts||e1.seul) lignes.push("Pages : l'Accueil large en a ("+e1.pts+" point(s), « "+k+" » seul : "+e1.seul+")");
        }
        else if(e1.pts!==3||e1.cur!==2||!e1.seul) lignes.push("Pages : « "+k+" » passé à droite, mais "+e1.pts+" point(s), page "+e1.cur+", "+e1.vis+" élément(s) montré(s)");
        if(ecran.mobile&&await page.evaluate(()=>document.getElementById("v-horaire").classList.contains("acc-tel"))){
          /* le doigt part du bord gauche de l'Accueil (couché, un menu est à sa gauche) */
          const c=await page.context().newCDPSession(page), o=await page.evaluate(()=>{ const r=document.getElementById("v-horaire").getBoundingClientRect(); return {x:Math.round(Math.max(0,r.left)+20), w:r.width, y:Math.round(innerHeight*0.6)}; }), y=o.y, pas=Math.round(o.w*0.6/8);
          await c.send("Input.dispatchTouchEvent",{type:"touchStart",touchPoints:[{x:o.x,y}]});
          for(let j=1;j<=8;j++){ await c.send("Input.dispatchTouchEvent",{type:"touchMove",touchPoints:[{x:o.x+pas*j,y}]}); await page.waitForTimeout(16); }
          await c.send("Input.dispatchTouchEvent",{type:"touchEnd",touchPoints:[]}); await page.waitForTimeout(700);
          const e2=await etat(); if(e2.cur!==1||e2.seul) lignes.push("Pages : le balayage vers la droite ne ramène pas à la page principale (page "+e2.cur+")");
          /* le point de droite y retourne */
          await page.evaluate(()=>{ const b=document.querySelector('#accPoints [data-acc-page="1"]'); if(b) b.click(); }); await page.waitForTimeout(700);
          if(!(await etat()).seul) lignes.push("Pages : le point de droite n'ouvre pas la page de droite");
        }
        const e3=await page.evaluate(()=>!!document.querySelector(".acc-b .acc-bouger"));
        /* Maj et ← : la page principale au téléphone ; dans l'Accueil large,
           la place d'avant (Maj et une flèche y déplacent comme la flèche) */
        await page.evaluate(k=>{ const b=document.querySelector('.acc-b[data-acc-pour="'+k+'"] .acc-bouger'); if(b) b.focus(); },k);
        await page.keyboard.press("Shift+ArrowLeft"); await page.waitForTimeout(400);
        const e4=await etat(); if(e4.cur!==(e1.pts?1:0)||e4.seul) lignes.push("Pages : Maj et ← ne ramène pas « "+k+" » sur la page principale");
        await page.keyboard.press("Escape"); await page.waitForTimeout(400);
        const r=await page.evaluate(()=>({edit:document.getElementById("v-horaire").classList.contains("acc-edit"), cfm:!!document.querySelector(".cfm-ov")}));
        if(r.cfm||r.edit) lignes.push("Pages : revenu à l'identique, Échap "+(r.cfm?"demande une confirmation":"ne ferme pas le mode Modifier"));
        if(!e3) lignes.push("Pages : le mode Modifier a perdu ses outils");
      }
      if(await page.evaluate(()=>!!document.querySelector(".cfm-ov"))){ await page.keyboard.press("Escape"); }
      if(await page.evaluate(()=>document.getElementById("v-horaire").classList.contains("acc-edit"))) await page.click("#accOk").catch(()=>{});
    }
    lignes.push(...page.fautes);
    await page.ctx.close();
    res[i]={avant:avant, tag:ecran.nom+" · "+(role||"sans compte"), lignes:lignes, n:n}; }
  const PAR=vite?1:Math.max(1,Math.min(3,require("os").cpus().length-1)); let suivant=0;
  await Promise.all(Array.from({length:PAR},async()=>{ while(suivant<travaux.length){ const i=suivant++; await faire(i); } }));
  res.forEach(r=>{ essais+=r.n; r.avant.forEach(a=>{ if(a.faute) fautes++; console.log(a.txt); });
    if(r.lignes.length){ fautes+=r.lignes.length; console.log("✗ "+r.tag); r.lignes.forEach(l=>console.log("    "+l)); }
    else console.log("✓ "+r.tag); });
  /* hors ligne : le service worker installé, le réseau coupé, on recharge */
  { const page=await ouvrir(nav,url,ECRANS[1],"hierarchie"); await page.waitForTimeout(1500);
    await page.ctx.setOffline(true); await page.reload().catch(()=>{}); await page.waitForTimeout(2500);
    const ok=await page.evaluate(()=>!!document.querySelector(".tabs")&&document.body.innerText.length>200).catch(()=>false);
    essais++; if(!ok){ fautes++; console.log("✗ hors ligne : page vide après rechargement"); } else console.log("✓ hors ligne");
    await page.ctx.close(); }
  await nav.close(); srv.close();
  console.log("\n"+essais+" essais, "+fautes+" faute"+(fautes>1?"s":""));
  process.exit(fautes?1:0);
})().catch(e=>{ console.error(e); process.exit(2); });
