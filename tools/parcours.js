#!/usr/bin/env node
/* LE PARCOURS DE L'APPLICATION, d'un bout à l'autre, au navigateur.
   node tools/parcours.js            → tout ; code 1 à la moindre faute
   node tools/parcours.js --vite     → téléphone portrait seulement

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

   Faute (code 1) : une erreur JavaScript, un débordement horizontal de la
   page, un cadre posé sous la barre d'onglets (portrait) ou sous le rail
   (couché), une page blanche hors ligne. Le reste se lit dans la sortie.
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
const VUES=[["Accueil","tab-horaire"],["Planning","tab-jour"],["Équipes","tab-equipe"],["Horaire","ws:planning"]];

async function ouvrir(nav,url,ecran,role){
  const ctx=await nav.newContext({viewport:{width:ecran.w,height:ecran.h},isMobile:ecran.mobile,hasTouch:ecran.mobile,colorScheme:"dark"});
  await ctx.addInitScript(([role])=>{ if(localStorage.getItem("__p")) return; localStorage.setItem("__p","1");
    localStorage.setItem("ui/prefillId",JSON.stringify("VBN"));
    if(role){ localStorage.setItem("account/current",JSON.stringify({role:"employe",tri:"VBN",cat:"",email:"x@exemple.be",base:role,at:"x"}));
      localStorage.setItem("base/session",JSON.stringify({access:"a",refresh:"r",exp:Date.now()+9e12,email:"x@exemple.be"})); } },[role]);
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
  return f;
}

(async()=>{
  const vite=process.argv.indexOf("--vite")>=0;
  const srv=await servir(), url="http://127.0.0.1:"+srv.address().port+"/";
  const nav=await chromium.launch();
  const ecrans=vite?ECRANS.filter(e=>e.nom==="téléphone 390"):ECRANS;
  let fautes=0, essais=0;
  for(const ecran of ecrans) for(const role of (vite?["hierarchie"]:ROLES)){
    const page=await ouvrir(nav,url,ecran,role); const lignes=[];
    for(const [nom,cible] of VUES){
      if(cible.indexOf("ws:")===0&&!role) continue;
      await aller(page,cible); essais++;
      const f=await page.evaluate(constater);
      if(f.length) lignes.push(nom+" : "+f.join(" ; "));
      if(cible.indexOf("ws:")===0) await aller(page,"tab-horaire");
    }
    lignes.push(...page.fautes);
    if(lignes.length){ fautes+=lignes.length; console.log("✗ "+ecran.nom+" · "+(role||"sans compte")); lignes.forEach(l=>console.log("    "+l)); }
    else console.log("✓ "+ecran.nom+" · "+(role||"sans compte"));
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
