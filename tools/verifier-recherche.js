#!/usr/bin/env node
/* Vérifie la RECHERCHE (congé, absence) heure par heure, sur chaque jour des
 * horaires installés et chaque personne en pause.
 *
 * Le client, le 03/11/2026, après la correction de la v1333 (la recherche
 * comptait GDT jusqu'à 14 h alors qu'il partait à 13 h) : « il faut vérifier
 * cela pour tous les cas possibles ». Pour chaque personne de chaque pause
 * (matin, après-midi, nuit) de chaque jour, l'outil rejoue dans la page :
 *
 *   - le congé à l'heure, de 1 à 7 h, départ tôt et arrivée tard
 *     (caCongeHeures, demandé à 7 jours ou moins) ;
 *   - le congé d'un jour (caSimuler, « conge ») ;
 *   - l'absence (caSimuler, « absence ») ;
 *
 * et confronte la réponse à SON propre compte du poste, demi-heure par
 * demi-heure : chacun à ses heures (la part d'une autre pause, l'arrivée et
 * le départ que lit l'application), les relais d'une autre pause à leurs
 * heures, les copies venues du D pour toute la pause.
 *
 * Fautes (code 1) :
 *   H  congé à l'heure : « possible sans remplaçant » alors qu'une
 *      demi-heure des heures demandées reste sous l'effectif, ou l'inverse ;
 *   J  congé d'un jour : « l'équipe reste au complet » alors qu'une
 *      demi-heure de la pause reste sous l'effectif, ou l'inverse ;
 *   A  absence : un trou à une heure que l'absence ouvre (il n'y était pas
 *      avec la personne) et que la recherche ne signale pas ;
 *   M  le mode Remplaçant (caRechercher) : le poste montré (« 1/1 ») ne
 *      suit pas le compte heure par heure (le 12/01, « 1/1, LHS » alors que
 *      LHS part à 7 h) ;
 *   P  le Planning du jour réel : un poste « complet » à la pause qui a
 *      pourtant une demi-heure sous l'effectif sans être en manque — le
 *      client, le 03/11/2026, en QCM : « oui, en rouge » (trouAuxHeures) ;
 *   R  ses relais ailleurs : la personne tient aussi, quelques heures, le
 *      poste d'un autre (« remplace FPA de 22h à 01h00' », ou « départ à
 *      13h remplacé par PAM ») ; sans elle ce poste passe sous l'effectif,
 *      et le congé (d'un jour, ou à l'heure quand ses heures tombent dans
 *      ce qu'elle quitte) ou l'absence doit le dire ;
 *   E  une erreur de la page.
 *
 * Pour information (sans faute) :
 *   L  la LECTURE DES HEURES recoupée : l'outil relit l'arrivée, le départ
 *      et la plage écrits avec ses propres motifs, sans rien emprunter à
 *      l'application ; un désaccord est listé avec la cellule, à relire ;
 *   (le Planning du jour réel est passé dans les fautes, P, le 03/11/2026)
 *
 * Usage : node tools/verifier-recherche.js [index.html] [--detail]
 * Environ 3 minutes pour deux années.
 */
"use strict";
const http=require("http"), fs=require("fs"), path=require("path");
let chromium;
try{ ({chromium}=require("playwright")); }catch(e){ ({chromium}=require("/opt/node-tools/node_modules/playwright")); }

const RACINE=path.join(__dirname,"..");
const ARGS=process.argv.slice(2), DETAIL=ARGS.indexOf("--detail")>=0;
const PAGE=ARGS.filter(a=>!a.startsWith("--"))[0]||path.join(RACINE,"index.html");

let html=fs.readFileSync(PAGE,"utf8");
const ANCRE="\nfunction caCongeHeures(db,id,an,m,j,n,moment,pausesDe,delai){";
if(html.split(ANCRE).length!==2) throw new Error("repère introuvable ou double dans la page : function caCongeHeures(");

/* --- ce qui tourne DANS la page ------------------------------------------ */
const DANS_LA_PAGE=String.raw`
window.__verifRech=function(an,m,j){
  var db=horaireDe(an); if(!db) return null;
  var mmdd=pad2(m)+pad2(j), jour=an*10000+m*100+j, memo={};
  function pl(dt){ var k=caIso(dt); if(memo[k]) return memo[k]; var out={}, y=dt.getFullYear(), d2=horaireDe(y);
    if(d2){ var par=equipeDuJour(d2,y,dt.getMonth()+1,dt.getDate());
      ["AM","PM","N","D"].forEach(function(g){ (par[g]||[]).forEach(function(x){ out[x.p.id]=g; }); });
      Object.defineProperty(out,"_par",{value:par}); }
    return (memo[k]=out); }
  function pd(dec){ return pl(new Date(an,m-1,j+dec)); }
  var par=pd(0)._par, PZ={AM:[6,14],PM:[14,22],N:[22,30]};
  var R={f:[], l:[], p:[], n:{h:0,j:0,a:0,r:0,m:0}};
  function faute(c,t){ R.f.push(c+" "+t); }
  /* --- SA lecture des heures, sans rien emprunter à l'application ---------- */
  function hDe(hh,mm,t0){ var v=Number(hh)+Number(mm||0)/60; while(v<t0-12) v+=24; while(v>=t0+12) v-=24; return v; }
  function heuresSceptique(raw,g){
    /* la règle écrite (docs/conversion-horaire.md) : la cellule dit le
       prévu, l'annotation et le commentaire le presté — une annotation qui
       écrit une pause rend la plage de la cellule au prévu ; une plage
       dans l'annotation passe avant celle de la cellule */
    var t0=PZ[g][0], t1=PZ[g][1], s=t0, e=t1, c0=String(raw[0]||"").trim(), c1=String(raw[1]||"").trim(), com=String(raw[2]||"");
    var rxP=/^(\d{1,2})\s*(?:h\s*(\d{2})?)?\s*[-\u2013]\s*(\d{1,2})\s*h?\s*(\d{2})?['\u2019]?$/i;
    var mp=rxP.exec(c1)||(/^(AM|PM|N|D)$/i.test(c1)?null:rxP.exec(c0));
    if(mp){ var a=hDe(mp[1],mp[2],t0), b=hDe(mp[3],mp[4],t0); if(b<=a) b+=24; if(b-a>=0.5 && b-a<=12.5){ s=a; e=b; } }
    var ar=/arriv\S*\s*(?:\u00e0|a)?\s*(\d{1,2})\s*[h:]\s*(\d{2})?/i.exec(com), dp=/d[\u00e9e]part\S*\s*(?:\u00e0|a)?\s*(\d{1,2})\s*[h:]\s*(\d{2})?/i.exec(com);
    if(ar){ var va=hDe(ar[1],ar[2],t0); if(va>t0-4 && va<t1) s=va; }
    if(dp){ var vd=hDe(dp[1],dp[2],t0); if(vd>t0 && vd<t1+4) e=vd; }
    return [Math.max(s,t0),Math.min(e,t1)];
  }
  /* --- les heures que l'APPLICATION lit (heuresAuPoste), pour compter ; le
     compte lui-même est celui de l'outil --------------------------------- */
  function heuresApp(x,g){ return heuresAuPoste(db,x,g,an,m,j); }
  /* le compte du poste, demi-heure par demi-heure */
  /* le compte du poste, demi-heure par demi-heure : les présents à leurs
     heures, puis les relais (d'une pause entière, et à heures :
     relaisAuxHeures), sans celui qu'on retire */
  function compte(o,gens,g,sans){
    var t0=PZ[g][0], t1=PZ[g][1], H=gens.map(function(x){ return heuresApp(x,g); }), out=[];
    var rel=(o.relais||[]).filter(function(r){ return r.a!=null && r.b!=null; }).concat(relaisAuxHeures(db,o,g,an,m,j))
      .filter(function(r){ return r.p.id!==sans; });
    for(var u=t0; u<t1-0.01; u+=0.5){
      var la=gens.filter(function(x,i){ return H[i][0]<=u+0.01 && H[i][1]>=u+0.49; });
      var n=effectif(la,o.P,jour);
      if(o.attendu && n<o.attendu) n+=Math.min(o.attendu-n, rel.filter(function(r){ return r.a<=u+0.01 && r.b>=u+0.49; }).length);
      out.push(n);
    }
    return out;
  }
  function plein(cpt,o,g,a,b){ var t0=PZ[g][0];
    for(var i=0;i<cpt.length;i++){ var u=t0+i*0.5; if(u>=a-0.01 && u+0.5<=b+0.01 && cpt[i]<o.attendu) return false; } return true; }
  function hh(v){ v=((v%24)+24)%24; var e=Math.floor(v+1e-6), mn=Math.round((v-e)*60); return e+(mn?"h"+pad2(mn):"h"); }
  function trousDe(cpt,o,g){ var t0=PZ[g][0], z=[];
    cpt.forEach(function(n,i){ if(o.attendu && n<o.attendu){ var u=t0+i*0.5, w=z[z.length-1]; if(w && Math.abs(w[1]-u)<0.01) w[1]=u+0.5; else z.push([u,u+0.5]); } });
    return z.map(function(w){ return hh(w[0])+"-"+hh(w[1]); }).join(" "); }

  var VUES={};
  ["AM","PM","N"].forEach(function(g){ if((par[g]||[]).length) VUES[g]=postesDePause(db,caCopie(par[g],null),g,mmdd,g==="AM"?caCopie(par.D,null):null); });
  /* R : les relais de la personne AILLEURS (une autre pause, ou un autre
     poste de la sienne) : les demi-heures où, sans elle, le poste passe sous
     son effectif alors qu'elle le tenait. Le compte est celui de l'outil. */
  function ailleurs(id,g,o){
    var out=[];
    Object.keys(VUES).forEach(function(g2){ VUES[g2].postes.forEach(function(o2){
      if(!o2.attendu || (g2===g && o2===o)) return;
      var siens=relaisAuxHeures(db,o2,g2,an,m,j).concat((o2.relais||[]).filter(function(r){ return r && r.p && r.a!=null && r.b!=null; }))
        .filter(function(r){ return r.p.id===id; });
      if(!siens.length) return;
      var gens=o2.gens.filter(function(y){ return y.p.id!==id; }), cW=compte(o2,gens,g2,null), cS=compte(o2,gens,g2,id), us=[];
      cS.forEach(function(v,i){ if(v<o2.attendu && cW[i]>v) us.push(PZ[g2][0]+i*0.5); });
      out.push({g:g2, k:o2.P.k, us:us, siens:siens});
    }); });
    return out;
  }
  ["AM","PM","N"].forEach(function(g){
    if(!VUES[g]) return;
    var t0=PZ[g][0], t1=PZ[g][1];
    var vue=VUES[g];
    /* L : la lecture des heures recoupée, une fois par personne */
    vue.postes.forEach(function(o){ o.gens.forEach(function(x){
      if(x.depuisD || x.horPart || x.partage) return;
      var raw=(x.p.d||{})[mmdd]; if(!raw) return;
      var A=heuresApp(x,g), B=heuresSceptique(raw,g);
      if(Math.abs(A[0]-B[0])>0.01 || Math.abs(A[1]-B[1])>0.01)
        R.l.push(g+" "+idLisible(x.p.id)+" : l'application "+hh(A[0])+"-"+hh(A[1])+", l'outil "+hh(B[0])+"-"+hh(B[1])+"  "+JSON.stringify(raw));
    }); });
    /* M : le mode Remplaçant (caRechercher) montre le poste à son plus bas,
       chacun à ses heures, comme le Planning */
    vue.postes.forEach(function(o){
      if(!o.attendu) return;
      var rr=caRechercher(db,an,m,j,g,o.P.k,pd); R.n.m++;
      var c=compte(o,o.gens,g,null), bas=Math.min.apply(null,c);
      /* un trou : le compte au plus bas ; sinon, le poste au complet (le
         surnombre de la pause peut rester affiché : 3/2 quand l'un part tôt) */
      var dit=rr?(bas<o.attendu?rr.tenu!==Math.min(bas,o.tenu):rr.tenu<o.attendu):false;
      if(dit) faute("M",g+" "+o.P.k+" : la recherche dit "+rr.tenu+"/"+rr.attendu+", le compte "+Math.min(bas,o.tenu)+"/"+o.attendu+(bas<o.attendu?" (sous l'effectif "+trousDe(c,o,g)+")":""));
    });
    /* P : le Planning du jour réel */
    vue.postes.forEach(function(o){
      if(!o.attendu || o.manque) return;
      var c=compte(o,o.gens,g);
      if(!plein(c,o,g,t0,t1)) R.f.push("P "+g+" "+o.P.k+" "+o.tenu+"/"+o.attendu+" : sous l'effectif "+trousDe(c,o,g)+"  ("+o.gens.map(function(x){ var h=heuresApp(x,g); return idLisible(x.p.id)+" "+hh(h[0])+"-"+hh(h[1]); }).join(", ")+")");
    });
    (par[g]||[]).forEach(function(x){
      var id=x.p.id, o=null;
      vue.postes.forEach(function(q){ q.gens.forEach(function(y){ if(y.p.id===id && !y.depuisD) o=q; }); });
      if(!o || !o.attendu) return;
      var restants=o.gens.filter(function(y){ return !y.depuisD && y.p.id!==id; });
      var cpt=compte(o,restants,g,id), tri=idLisible(id), qui=g+" "+o.P.k+" sans "+tri, AIL0=ailleurs(id,g,o);
      var AIL=AIL0.filter(function(x){ return x.us.length; });
      R.n.r+=AIL.length;
      /* ses heures du jour : sa présence au poste, prolongée de ses relais qui la touchent */
      var hP=heuresApp(x,g), S=hP[0], E=hP[1], rels=[];
      AIL0.forEach(function(z){ z.siens.forEach(function(r){ rels.push([r.a,r.b]); }); });
      var bouge=true; while(bouge){ bouge=false; rels.forEach(function(r){
        if(r[0]<S-0.01 && r[1]>=S-0.01){ S=r[0]; bouge=true; } if(r[1]>E+0.01 && r[0]<=E+0.01){ E=r[1]; bouge=true; } }); }
      /* H : le congé à l'heure */
      for(var n=1;n<=7;n++) ["fin","debut"].forEach(function(mo){
        var nn=Math.min(n,Math.max(0.5,E-S)), a=mo==="fin"?E-nn:S, b=mo==="fin"?E:S+nn;
        var oa=Math.max(a,hP[0]), ob=Math.min(b,hP[1]), att=ob-oa<0.5 || plein(cpt,o,g,oa,ob);
        var r=caCongeHeures(db,id,an,m,j,n,mo,pd,0); R.n.h++;
        if(!r || r.v==="hors" || /introuvable/.test(r.t||"")) return;
        var dit=r.v==="ok";
        /* ses relais perdus avec ses heures : après le départ, avant l'arrivée */
        var perd=AIL.filter(function(x){ return x.us.some(function(u){ return u>=a-0.01 && u+0.5<=b+0.01; }); });
        if(perd.length) att=false;
        if(dit!==att) faute(perd.length?"R":"H",qui+", "+n+" h "+(mo==="fin"?"départ tôt":"arrivée tard")+" : la recherche dit « "+r.t+" », le compte "+(att?"complet":(perd.length?"un relais perdu ("+perd.map(function(x){ return x.g+" "+x.k; }).join(", ")+")":"sous l'effectif "+trousDe(cpt,o,g))));
      });
      /* J : le congé d'un jour */
      var rj=caSimuler(db,id,an,m,j,"conge",pd); R.n.j++;
      if(rj && !rj.hors && rj.poste && rj.poste.k===o.P.k){
        var dj=!!rj.couverture, aj=plein(cpt,o,g,t0,t1);
        if(dj!==aj) faute("J",qui+" : la recherche dit « "+(dj?"au complet":"trou")+" », le compte "+(aj?"complet":"sous l'effectif "+trousDe(cpt,o,g)));
        AIL.forEach(function(x){
          if(!(rj.trous||[]).some(function(t){ return t.P && t.P.k===x.k && t.pause===x.g; }))
            faute("R",qui+" : son relais en "+x.g+" "+x.k+" ("+x.us.map(hh).join(" ")+") reste vide, le congé d'un jour ne le dit pas");
        });
      }
      /* A : l'absence — un trou à une heure qu'elle ouvre doit être signalé */
      var ra=caSimuler(db,id,an,m,j,"absence",pd); R.n.a++;
      if(ra && !ra.hors){
        var vB=postesDePause(db,caCopie(par[g],id),g,mmdd,g==="AM"?caCopie(par.D,id):null), tA={};
        vue.postes.forEach(function(q){ tA[q.P.k]=q; });
        vB.postes.forEach(function(q){
          if(!q.attendu) return;
          var cB=compte(q,q.gens,g,id), qa=tA[q.P.k], cA=qa?compte(qa,qa.gens,g):null, neuf=false;
          cB.forEach(function(v,i){ if(v<q.attendu && !(cA && cA[i]<=v)) neuf=true; });
          var signale=(ra.trous||[]).some(function(t){ return t.P && t.P.k===q.P.k && t.pause===g; });
          if(neuf && !signale) faute("A",g+" "+q.P.k+" absence de "+tri+" : sous l'effectif "+trousDe(cB,q,g)+", la recherche ne le dit pas");
        });
        AIL.forEach(function(x){
          if(x.g===g) return; /* sa pause : déjà comptée ci-dessus */
          if(!(ra.trous||[]).some(function(t){ return t.P && t.P.k===x.k && t.pause===x.g; }))
            faute("R",qui+" : son relais en "+x.g+" "+x.k+" ("+x.us.map(hh).join(" ")+") reste vide, l'absence ne le dit pas");
        });
      }
    });
  });
  return R;
};`;
html=html.replace(ANCRE,"\n"+DANS_LA_PAGE+ANCRE);

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
const ANNEES=fs.readdirSync(path.join(RACINE,"data")).map(f=>(/^horaire-(\d{4})\.json$/.exec(f)||[])[1]).filter(Boolean).map(Number).sort();

(async()=>{
  const srv=await servir(), b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:1280,height:900},serviceWorkers:"block"});
  await ctx.addInitScript(()=>{ try{ localStorage.setItem("ui/prefillId",JSON.stringify("VBN"));
    localStorage.setItem("account/current",JSON.stringify({role:"employe",tri:"VBN",cat:"",email:"x@exemple.be",base:"hierarchie",at:"x"}));
    localStorage.setItem("base/session",JSON.stringify({access:"a",refresh:"r",exp:Date.now()+9e12,email:"x@exemple.be"})); }catch(e){} });
  const p=await ctx.newPage();
  await p.route(/supabase\.co\//,r=>{ const u=r.request().url(); r.fulfill({status:200,contentType:"application/json",
    body:u.includes("mon_compte")?JSON.stringify([{role:"hierarchie",valide:true,trigramme:"VBN"}]):"[]"}); });
  await p.route(/open-meteo/,r=>r.abort());
  const ERR=[]; p.on("pageerror",e=>ERR.push("erreur de la page : "+e.message));
  await p.clock.setFixedTime(new Date(ANNEES[0]+"-01-01T09:00:00"));
  await p.goto("http://127.0.0.1:"+srv.address().port+"/"); await p.waitForTimeout(4000);
  const F={}, L=[], P=[], N={h:0,j:0,a:0,r:0,m:0};
  let jours=0;
  for(const an of ANNEES){
    for(let t=Date.UTC(an,0,1); t<=Date.UTC(an,11,31); t+=864e5){
      const D=new Date(t), m=D.getUTCMonth()+1, j=D.getUTCDate(), dt=String(j).padStart(2,"0")+"/"+String(m).padStart(2,"0")+"/"+an;
      let r=null;
      try{ r=await p.evaluate(a=>window.__verifRech(a[0],a[1],a[2]),[an,m,j]); }catch(e){ ERR.push(dt+" "+String(e.message||e).slice(0,160)); continue; }
      if(!r) continue; jours++;
      ["h","j","a","r","m"].forEach(k=>N[k]+=r.n[k]);
      r.f.forEach(x=>{ const c=x[0]; (F[c]=F[c]||[]).push(dt+"  "+x.slice(2)); });
      r.l.forEach(x=>L.push(dt+"  "+x)); r.p.forEach(x=>P.push(dt+"  "+x));
    }
  }
  await b.close(); srv.close();
  if(ERR.length) F.E=ERR;
  const NOMS={H:"congé à l'heure : la réponse contredit le compte heure par heure",J:"congé d'un jour : la réponse contredit le compte heure par heure",
    A:"absence : un trou à une heure que la recherche ne signale pas",P:"Planning : un poste « complet » vide à une heure, pas en rouge",M:"remplaçant : le poste montré ne suit pas le compte heure par heure",R:"ses relais ailleurs : le poste qu'elle tenait quelques heures reste vide sans qu'on le dise",E:"erreur"};
  console.log(jours+" journées · "+N.h+" congés à l'heure, "+N.j+" congés d'un jour, "+N.a+" absences, "+N.m+" recherches de remplaçant rejoués · "+N.r+" relais ailleurs");
  let fautes=0;
  ["E","H","J","A","R","M","P"].forEach(c=>{ const l=F[c]||[]; fautes+=l.length;
    console.log((l.length?"✗ ":"✓ ")+c+" "+NOMS[c]+" : "+l.length);
    l.slice(0,DETAIL?l.length:12).forEach(x=>console.log("    "+x)); if(!DETAIL && l.length>12) console.log("    … (--detail pour tout)"); });
  console.log("· L lecture des heures en désaccord avec l'outil : "+L.length+" (à relire)");
  L.slice(0,DETAIL?L.length:8).forEach(x=>console.log("    "+x)); if(!DETAIL && L.length>8) console.log("    … (--detail pour tout)");
  console.log(fautes?"\n"+fautes+" faute"+(fautes>1?"s":""):"\n0 faute");
  process.exit(fautes?1:0);
})().catch(e=>{ console.error(e); process.exit(2); });
