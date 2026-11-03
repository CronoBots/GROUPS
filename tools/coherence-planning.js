/* LA COHÉRENCE DU PLANNING JOUR APRÈS JOUR (le client, le 03/11/2026 :
   « check logique complète »).
 *
 * Le vérificateur du calendrier rejoue le MOTEUR (postesDePause) ; le
 * Planning, lui, ajoute ses passes d'affichage (propositions, relais d'une
 * heure, colonne D) et l'onglet Effectifs tire « À prévenir » d'une autre
 * fonction (transfertsDuJour). Trois calculs pour une même journée : ce
 * contrôle les confronte, chaque jour de chaque horaire installé.
 *
 * L'outil ne réimplémente rien : il sert la page elle-même, avec deux
 * relevés insérés dans renderEquipe() (l'état du moteur, puis celui du
 * tableau), et feuillette le Planning jour par jour au navigateur.
 *
 *   node tools/coherence-planning.js [chemin/index.html] [--detail]
 *
 * Code de retour 1 à la moindre FAUTE :
 *   R1  une personne placée deux fois le même jour ;
 *   R2  un absent ou un congé placé à un poste ;
 *   R2b un présent de la pause absent du tableau (ni case, ni relais,
 *       ni formation, ni « à déterminer ») ;
 *   R3  une case en manque alors que son compte est plein, ou l'inverse
 *       (le trou d'une heure excepté) ;
 *   R4  une case orange sans personne proposée vers elle, ou une
 *       proposition vers une case qui n'est pas orange ;
 *   R5  une proposition qui dépasse les heures du proposé : pour toute
 *       la pause alors qu'il part tôt ou arrive tard, ou à des heures où
 *       il n'est pas là (le client, le 03/11/2026, capture du 13/11 :
 *       SKS, « départ à 10h00' », proposé aux chaudières de 6 h à 14 h ;
 *       14 propositions de l'année dans ce cas avant nfdm-v1348) ;
 *   R9  « À prévenir » et le Planning qui ne disent pas les mêmes
 *       changements (pause, personne, poste de départ, poste visé) : 34
 *       écarts le 03/11/2026, avant que les deux ne partagent
 *       propositionsPause().
 * Le reste est INFORMATIF (une question au client, une cascade, un trou
 * réel) et ne change pas le code de retour. */
const http=require("http"), fs=require("fs"), path=require("path");
let chromium;
try{ ({chromium}=require("playwright")); }catch(e){ ({chromium}=require("/opt/node-tools/node_modules/playwright")); }

const RACINE=path.join(__dirname,"..");
const ARGS=process.argv.slice(2), DETAIL=ARGS.indexOf("--detail")>=0;
const PAGE=ARGS.filter(a=>!a.startsWith("--"))[0]||path.join(RACINE,"index.html");

/* --- la page, avec ses deux relevés --------------------------------------- */
/* les repères, à toute indentation : le bloc du moteur a quitté
   renderEquipe() pour planningDuJour() le 03/11/2026 */
const repere=s=>{ const m=html.match(new RegExp("^ *"+s.replace(/[.*+?^${}()|[\]\\\/]/g,"\\$&"),"gm"));
  if(!m||m.length!==1) throw new Error("repère introuvable ou double dans la page ("+(m?m.length:0)+") : "+s); return m[0]; };
let html=fs.readFileSync(PAGE,"utf8");
const A1=repere("/* CHACUN SES HEURES DANS CHAQUE PAUSE (le client, le 24/10/2026 :");
const A2=repere("/* L'adjoint a SA ligne. Le client, le 22/09/2026");
const MOTEUR=`    try{ window.__ckE={}; Object.keys(vp).forEach(function(k){ if(!vp[k]) return; window.__ckE[k]=vp[k].vue.postes.map(function(o){ return {k:o.P.k, cm:!!o.P.cm, att:o.attendu, tenu:o.tenu, mq:!!o.manque}; }); }); }catch(e){ console.log("CKERR moteur "+e); }
`;
const TABLEAU=`    try{ var __ck={d:annee*10000+Number(mmdd), e:window.__ckE, p:{}};
      Object.keys(vp).forEach(function(k){ if(!vp[k]) return; var v=vp[k].vue;
        __ck.p[k]={pd:[PF_DEB[k],PF_FIN[k]], postes:v.postes.map(function(o){
          var c=null;
          if(o.manque && !o.P.cm && o.P.k!=="adj"){ try{ c=candidatsPlace(v,o.P,k,jourCalc,o,o.attendu,par).l; }catch(e){ c="ERR "+e; } }
          return {k:o.P.k, cm:!!o.P.cm, att:o.attendu, tenu:o.tenu, mq:!!o.manque, th:!!o.trouHeures, pr:!!o.propose, pp:!!o.proposePartiel, tc:!!o.trouCourt, cand:c,
            g:o.gens.map(function(x){ var hp=null; if(x.propose){ try{ hp=heuresAuPoste(db,x,k,annee,mois,jour); }catch(e){ hp="ERR "+e; } }
              return {id:x.p.id, pa:!!x.partage, dD:!!x.deD, pro:x.propose||null, ph:!!x.proposeH, phv:x.proposeH||null, hp:hp, cpt:!!compteAuPoste(x,o.P,jourCalc)}; }),
            rel:(o.relais||[]).map(function(r){ return r.p.id; }) }; }),
          inc:(v.inconnus||[]).map(function(x){ return x.p.id; }), form:(v.formation||[]).map(function(x){ return x.p.id; }) }; });
      ["abs","cong","D","AM","PM","N"].forEach(function(k){ __ck["l"+k]=(par[k]||[]).map(function(x){ return x.p.id; }); });
      __ck.ds=dsAff.map(function(x){ return x.p.id; }); __ck.incD=incD.map(function(x){ return x.p.id; });
      __ck.tr=transfertsDuJour(db,annee,mois,jour).map(function(t){ return {id:t.p.id, pause:t.pause, de:t.de, vers:t.vers}; });
      console.log("CK "+JSON.stringify(__ck)); }catch(e){ console.log("CKERR tableau "+e); }
`;
html=html.replace(A1,MOTEUR+A1).replace(A2,TABLEAU+A2);

const TYPES={".html":"text/html; charset=utf-8",".js":"text/javascript",".json":"application/json",".css":"text/css",
  ".png":"image/png",".jpg":"image/jpeg",".svg":"image/svg+xml",".webmanifest":"application/manifest+json",".woff2":"font/woff2"};
function servir(){
  return new Promise(ok=>{
    const srv=http.createServer((rq,rs)=>{
      let u=decodeURIComponent(rq.url.split("?")[0]); if(u.endsWith("/")) u+="index.html";
      if(u==="/index.html"){ rs.writeHead(200,{"Content-Type":TYPES[".html"]}); rs.end(html); return; }
      const f=path.join(RACINE,path.normalize(u));
      if(!f.startsWith(RACINE)||!fs.existsSync(f)||fs.statSync(f).isDirectory()){ rs.writeHead(404); rs.end(); return; }
      rs.writeHead(200,{"Content-Type":TYPES[path.extname(f)]||"application/octet-stream"});
      fs.createReadStream(f).pipe(rs);
    }).listen(0,"127.0.0.1",()=>ok(srv));
  });
}

/* les années : celles des horaires installés */
const ANNEES=fs.readdirSync(path.join(RACINE,"data")).map(f=>(/^horaire-(\d{4})\.json$/.exec(f)||[])[1]).filter(Boolean).map(Number).sort();
const DEBUT=new Date(Date.UTC(ANNEES[0],0,1)), FIN=new Date(Date.UTC(ANNEES[ANNEES.length-1],11,31));
const NJ=Math.round((FIN-DEBUT)/864e5)+1;

(async()=>{
  const srv=await servir(), b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:1280,height:900},serviceWorkers:"block"});
  /* un compte de la hiérarchie, la base simulée : le Planning entier */
  await ctx.addInitScript(()=>{ try{ localStorage.setItem("ui/prefillId",JSON.stringify("VBN"));
    localStorage.setItem("account/current",JSON.stringify({role:"employe",tri:"VBN",cat:"",email:"x@exemple.be",base:"hierarchie",at:"x"}));
    localStorage.setItem("base/session",JSON.stringify({access:"a",refresh:"r",exp:Date.now()+9e12,email:"x@exemple.be"})); }catch(e){} });
  const p=await ctx.newPage();
  await p.route(/supabase\.co\//,r=>{ const u=r.request().url(); r.fulfill({status:200,contentType:"application/json",
    body:u.includes("mon_compte")?JSON.stringify([{role:"hierarchie",valide:true,trigramme:"VBN"}]):"[]"}); });
  const J={}, ERR=[];
  p.on("console",m=>{ const t=m.text(); if(t.startsWith("CK ")){ const o=JSON.parse(t.slice(3)); J[o.d]=o; } else if(t.startsWith("CKERR")) ERR.push(t); });
  p.on("pageerror",e=>ERR.push("erreur de la page : "+e.message));
  await p.clock.setFixedTime(new Date(ANNEES[0]+"-01-01T09:00:00"));
  await p.goto("http://127.0.0.1:"+srv.address().port+"/"); await p.waitForTimeout(4000);
  await p.evaluate(()=>document.getElementById("tab-jour").click()); await p.waitForTimeout(2500);
  for(let i=1;i<NJ;i++){ await p.evaluate(()=>document.getElementById("jourNext").click()); await p.waitForTimeout(90); }
  await p.waitForTimeout(2000);
  await b.close(); srv.close();

  /* --- les règles --------------------------------------------------------- */
  const F={}, I={};
  const date=d=>String(d).slice(6,8)+"/"+String(d).slice(4,6)+"/"+String(d).slice(0,4);
  const faute=(r,d,t)=>(F[r]=F[r]||[]).push(date(d)+"  "+t);
  const info=(r,d,t)=>(I[r]=I[r]||[]).push(date(d)+"  "+t);
  ERR.forEach(e=>faute("R0 erreur",0,e));
  const jours=Object.keys(J);
  if(jours.length!==NJ) faute("R0 journées relevées",0,jours.length+" sur "+NJ);
  jours.forEach(dk=>{ const j=J[dk], d=j.d, P3=["AM","PM","N"];
    const vu={}, ajoute=(id,ou)=>(vu[id]=vu[id]||[]).push(ou), rel={};
    Object.keys(j.p).forEach(k=>{ const v=j.p[k];
      v.postes.forEach(o=>{ o.g.forEach(x=>{ if(!x.pa) ajoute(x.id,k+" "+o.k); }); o.rel.forEach(id=>{ rel[id]=1; }); });
      v.inc.forEach(id=>ajoute(id,k+" ?")); v.form.forEach(id=>ajoute(id,k+" formation")); });
    j.incD.forEach(id=>ajoute(id,"D ?")); j.ds.forEach(id=>ajoute(id,"DS"));
    Object.keys(vu).forEach(id=>{ if(vu[id].length>1) faute("R1 placé deux fois",d,id+" : "+vu[id].join(", ")); });
    const abs={}; j.labs.concat(j.lcong).forEach(id=>{ abs[id]=1; });
    Object.keys(vu).forEach(id=>{ if(abs[id]) faute("R2 absent ou en congé, placé",d,id+" : "+vu[id].join(", ")); });
    ["D","AM","PM","N"].forEach(k=>j["l"+k].forEach(id=>{ if(!vu[id] && !rel[id]) faute("R2b présent, absent du tableau",d,k+" "+id); }));
    const plan={}, ann={};
    P3.forEach(k=>{ const v=j.p[k]; if(!v) return;
      v.postes.forEach(o=>{
        /* R5 : ses heures (heuresAuPoste) bornent la proposition */
        o.g.forEach(x=>{ if(!x.pro) return;
          if(typeof x.hp==="string" || !x.hp){ faute("R0 erreur",d,"heures de "+x.id+" : "+x.hp); return; }
          const pd=v.pd, hh=t=>Math.round(t*100)/100, ses=hh(x.hp[0])+"-"+hh(x.hp[1]);
          const tout=x.hp[0]<=pd[0]+0.01 && x.hp[1]>=pd[1]-0.01;
          if(!x.phv && !tout) faute("R5 proposé pour toute la pause, là une partie seulement",d,k+" "+x.id+" "+o.k+"→"+x.pro+" (ses heures "+ses+")");
          if(x.phv && (x.phv[0]<x.hp[0]-0.01 || x.phv[1]>x.hp[1]+0.01))
            faute("R5 proposé hors de ses heures",d,k+" "+x.id+" "+o.k+"→"+x.pro+" "+hh(x.phv[0])+"-"+hh(x.phv[1])+" (ses heures "+ses+")"); });
        if(o.cm||o.k==="adj") return;
        const mq=!!(o.att && o.tenu<o.att);
        /* le trou à une heure (trouAuxHeures, le 03/11/2026) : rouge, le compte de la pause plein */
        if(mq!==o.mq && !((o.tc||o.th) && o.mq)) faute("R3 manque et compte en désaccord",d,k+" "+o.k+" "+o.tenu+"/"+o.att);
        /* une copie d'une autre pause compte quand elle est proposée à ses heures */
        const vers=[]; v.postes.forEach(q=>q.g.forEach(x=>{ if(x.pro===o.k && (!x.pa || x.ph)) vers.push(x.id+" ("+q.k+")"); }));
        if(o.pr && !vers.length) faute("R4 orange sans personne proposée",d,k+" "+o.k);
        /* un trou d'une pause entière couvert EN PARTIE reste rouge, ses morceaux proposés (le 03/11/2026) */
        if(vers.length && !o.pr && !o.pp) faute("R4 proposé vers une case qui n'est pas orange",d,k+" "+o.k+" ← "+vers.join(", "));
        if(o.pp) info("trou d'une pause couvert en partie, à heures",d,k+" "+o.k+" ← "+vers.join(", "));
        /* des morceaux à heures se partagent une même place */
        const nPl=v.postes.reduce((s,q)=>s+q.g.filter(x=>x.pro===o.k && !x.pa && !x.ph).length,0)
          +(v.postes.some(q=>q.g.some(x=>x.pro===o.k && x.ph))?1:0);
        if(nPl>Math.max(1,o.att-o.tenu)) info("plusieurs proposés pour la place",d,k+" "+o.k+" "+o.tenu+"/"+o.att+" ← "+vers.join(", "));
        if(vers.length && !o.mq) info("proposé vers une case pleine (une cascade)",d,k+" "+o.k+" "+o.tenu+"/"+o.att+" ← "+vers.join(", "));
        if(o.mq && !o.pr && Array.isArray(o.cand)){ const s=o.cand.filter(c=>c.s && !c.f);
          if(s.length) info("trou rouge, quelqu'un en surnombre",d,k+" "+o.k+" "+o.tenu+"/"+o.att+" : "+s.map(c=>c.id+" ("+c.de+")").join(", ")); }
        if(typeof o.cand==="string") faute("R0 erreur",d,"candidats "+k+" "+o.k+" : "+o.cand);
      });
      v.postes.forEach(q=>q.g.forEach(x=>{ if(x.pro && (!x.pa || x.ph)) plan[k+" "+x.id+" "+q.k+" → "+x.pro]=1; }));
      if(!v.postes.some(o=>o.cm && (o.g.length||o.rel.length))) info("pause sans contremaître",d,k);
    });
    j.tr.forEach(t=>{ ann[t.pause+" "+t.id+" "+t.de+" → "+t.vers]=1; });
    Object.keys(ann).forEach(t=>{ if(!plan[t]) faute("R9 annoncé dans « À prévenir », pas au Planning",d,t); });
    Object.keys(plan).forEach(t=>{ if(!ann[t]) faute("R9 proposé au Planning, pas dans « À prévenir »",d,t); });
  });

  const n=o=>Object.keys(o).reduce((s,k)=>s+o[k].length,0);
  console.log("\nCohérence du Planning — "+jours.length+" journées ("+ANNEES.join(", ")+")\n");
  const montre=(o,k)=>(DETAIL?o[k]:o[k].slice(0,8)).forEach(l=>console.log("      "+l));
  if(!n(F)) console.log("  ✓  aucune faute (R1 à R9, R5 compris)");
  Object.keys(F).sort().forEach(k=>{ console.log("  ✗  "+String(F[k].length).padStart(4)+"  "+k); montre(F,k); });
  console.log("\ninformatif :");
  Object.keys(I).sort().forEach(k=>{ console.log("  ·  "+String(I[k].length).padStart(4)+"  "+k); if(DETAIL) montre(I,k); });
  process.exit(n(F)?1:0);
})().catch(e=>{ console.error(e); process.exit(2); });
