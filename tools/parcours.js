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

   LES DEUX THÈMES (le client, le 29/10/2026, la version claire) : tout le
   parcours en sombre, le thème par défaut, puis le clair sur le téléphone
   portrait, l'iPhone simulé, le téléphone couché et le PC.

   Faute (code 1) : une requête du téléphone couché qui diverge des
   autres (contrôle sans navigateur, fait d'abord), une erreur JavaScript, un débordement horizontal de la
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
const VUES=[["Accueil","tab-horaire"],["Planning","tab-jour"],["Équipes","tab-equipe"],["Horaire","ws:planning"]];

async function ouvrir(nav,url,ecran,role,theme){
  theme=theme||"dark";
  const ctx=await nav.newContext({viewport:{width:ecran.w,height:ecran.h},isMobile:ecran.mobile,hasTouch:ecran.mobile,colorScheme:theme});
  await ctx.addInitScript(([role,theme])=>{ try{ if(localStorage.getItem("__p")) return; localStorage.setItem("__p","1");
    localStorage.setItem("ui/theme",JSON.stringify(theme));
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
  const div=requetesDivergentes(iS>=0&&process.argv[iS+1]?process.argv[iS+1]:path.join(RACINE,"index.html"));
  div.forEach(l=>console.log("✗ requête du téléphone couché qui diverge, "+l));
  if(iS>=0){ console.log(div.length?div.length+" requête(s) divergente(s)":"requêtes du téléphone couché : toutes identiques"); process.exit(div.length?1:0); }
  const vite=process.argv.indexOf("--vite")>=0;
  const srv=await servir(), url="http://127.0.0.1:"+srv.address().port+"/";
  const nav=await chromium.launch();
  const ecrans=vite?ECRANS.filter(e=>e.nom==="téléphone 390"):ECRANS;
  /* le sombre partout ; le clair sur quatre écrans (--vite : le portrait) */
  const CLAIR=["téléphone 390","iPhone 390 (zones protégées)","couché 844","PC 1280"];
  const passes=[];
  ecrans.forEach(e=>passes.push([e,"dark"]));
  ecrans.filter(e=>CLAIR.indexOf(e.nom)>=0).forEach(e=>passes.push([e,"light"]));
  let fautes=div.length, essais=1;
  for(const [ecran,theme] of passes) for(const role of (vite?["hierarchie"]:ROLES)){
    const page=await ouvrir(nav,url,ecran,role,theme); const lignes=[];
    for(const [nom,cible] of VUES){
      if(cible.indexOf("ws:")===0&&!role) continue;
      await aller(page,cible); essais++;
      const f=await page.evaluate(constater);
      if(f.length) lignes.push(nom+" : "+f.join(" ; "));
      if(cible.indexOf("ws:")===0) await aller(page,"tab-horaire");
    }
    lignes.push(...page.fautes);
    const tag=ecran.nom+(theme==="light"?" · clair":"")+" · "+(role||"sans compte");
    if(lignes.length){ fautes+=lignes.length; console.log("✗ "+tag); lignes.forEach(l=>console.log("    "+l)); }
    else console.log("✓ "+tag);
    await page.ctx.close();
  }
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
