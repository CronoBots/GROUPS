/* LES WIDGETS UN PAR UN (le client, le 05/11/2026 : « travailler widget par
   widget, pour trouver le meilleur réglage et affichage 100 % pro selon
   chaque taille »). Photographie un widget de l'Accueil à chacun des
   formats (bandeau, petit, moyen, grand, très grand), au téléphone (390 et
   320 px, zones de l'iPhone simulées) et au PC (1280 et 1920 px), et relève
   ce qui déborde, ce qui est coupé et tout texte sous 11 px. Un format
   que le widget n'offre pas retombe sur celui d'origine (accTaille).

     npx http-server -p 8790 -s -c-1 .       (le dossier servi, à part)
     node tools/widget-photos.js profil /hors/du/depot/photos [TRIGRAMME]
*/
const {chromium}=require('playwright');
const k=process.argv[2], out=process.argv[3], qui=process.argv[4]||"VBN";
const F={tel:{R:[1,0.5],B:[2,0.5],S:[1,1],M:[2,1],L:[2,2]}, large:{R:[3,0.5],B:[6,0.5],S:[3,1],M:[6,1],L:[6,2],XL:[12,2]}};
const E=[{n:'tel390',w:390,h:844,m:'tel',z:{top:59,bottom:34,left:0,right:0}},{n:'tel320',w:320,h:568,m:'tel',z:{top:20,bottom:0,left:0,right:0}},{n:'couche852',w:852,h:393,m:'tel',z:{top:0,bottom:21,left:59,right:59}},{n:'ordi-1280',w:1280,h:800,m:'large',pc:true},{n:'ordi-1920',w:1920,h:1080,m:'large',pc:true}];
(async()=>{
 const b=await chromium.launch(); const res=[];
 for(const e of E) for(const f of Object.keys(F[e.m])){
  const ctx=await b.newContext({viewport:{width:e.w,height:e.h},isMobile:!e.pc,hasTouch:!e.pc,deviceScaleFactor:2});
  await ctx.addInitScript(([k,m,t,h,qui])=>{ if(localStorage.getItem("__p")) return; localStorage.setItem("__p","1"); localStorage.setItem("ui/prefillId",JSON.stringify(qui));
   localStorage.setItem("account/current",JSON.stringify({role:"employe",tri:qui,cat:"",email:"x@exemple.be",base:"hierarchie",at:"x"}));
   localStorage.setItem("base/session",JSON.stringify({access:"a",refresh:"r",exp:Date.now()+9e12,email:"x@exemple.be"}));
   const tt={}, hh={}; tt[k]=t; hh[k]=h; localStorage.setItem("ui/accueil/"+m,JSON.stringify({v:1,o:[k],t:tt,m:{},h:hh})); },[k,e.m,F[e.m][f][0],F[e.m][f][1],qui]);
  const p=await ctx.newPage(); const errs=[]; p.on('pageerror',x=>errs.push(x.message));
  /* une météo de Wanze fabriquée : sans réseau, le widget se cache */
  await p.route(/open-meteo\.com/,r=>{ const n=Date.now(), h=[...Array(48)].map((_,i)=>new Date(n+(i-1)*36e5).toISOString().slice(0,13)+":00"), d=[...Array(7)].map((_,i)=>new Date(n+i*864e5).toISOString().slice(0,10));
    r.fulfill({status:200,contentType:"application/json",body:JSON.stringify({latitude:50.54,longitude:5.21,timezone:"Europe/Brussels",current:{temperature_2m:3.2,weather_code:1,is_day:1},
      hourly:{time:h,temperature_2m:h.map((_,i)=>2+i%9),weather_code:h.map(()=>1),is_day:h.map(()=>1)},daily:{time:d,temperature_2m_max:d.map(()=>11),temperature_2m_min:d.map(()=>1),weather_code:d.map(()=>2)}})}); });
  await p.route(/supabase\.co\//,r=>{ const u=r.request().url(); r.fulfill({status:200,contentType:"application/json",body:u.includes("mon_compte")?JSON.stringify([{role:"hierarchie",valide:true,trigramme:qui}]):"[]"}); });
  await p.goto('http://localhost:8790/'); await p.waitForTimeout(3000);
  if(e.z) await p.evaluate(z=>{ document.querySelectorAll("style").forEach(s=>{ s.textContent=s.textContent.replace(/env\(safe-area-inset-top(,[^)]*)?\)/g,z.top+"px").replace(/env\(safe-area-inset-bottom(,[^)]*)?\)/g,z.bottom+"px").replace(/env\(safe-area-inset-left(,[^)]*)?\)/g,z.left+"px").replace(/env\(safe-area-inset-right(,[^)]*)?\)/g,z.right+"px"); }); window.dispatchEvent(new Event("resize")); },e.z);
  await p.waitForTimeout(700);
  const el=p.locator('#v-horaire [data-w="'+k+'"]').first();
  const ok=await el.count()&&await el.isVisible();
  if(!ok){ res.push(e.n+' '+f+' : invisible'); await ctx.close(); continue; }
  await el.scrollIntoViewIfNeeded(); await p.waitForTimeout(300);
  const m=await el.evaluate(w=>{ const r=w.getBoundingClientRect(), f=[];
    w.querySelectorAll('*').forEach(x=>{ if(!x.getClientRects().length||getComputedStyle(x).visibility==='hidden') return; const q=x.getBoundingClientRect();
      if(q.width&&(q.right>r.right+1||q.left<r.left-1||q.bottom>r.bottom+1||q.top<r.top-1)&&getComputedStyle(x).position!=='absolute') f.push('déborde:'+(x.className.baseVal!==undefined?x.tagName:x.className||x.tagName).toString().slice(0,30));
      if(x.children.length===0&&x.textContent.trim()&&x.scrollWidth>x.clientWidth+1&&getComputedStyle(x).overflow!=='visible') f.push('coupé:'+x.textContent.trim().slice(0,20));
      const fs=parseFloat(getComputedStyle(x).fontSize); if(x.children.length===0&&x.textContent.trim()&&fs<11) f.push('petit '+fs+'px:'+x.textContent.trim().slice(0,15)); });
    return {taille:Math.round(r.width)+'×'+Math.round(r.height), fautes:[...new Set(f)].slice(0,8)}; });
  res.push(e.n+' '+f+' '+m.taille+' '+(m.fautes.join(' ; ')||'ok')+(errs.length?' ERREURS '+errs.join('|'):''));
  await el.screenshot({path:out+'/'+k+'-'+qui+'-'+e.n+'-'+f+'.png'});
  await ctx.close(); }
 console.log(res.join('\n')); await b.close(); })();
