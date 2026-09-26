#!/usr/bin/env python3
"""Compare les fiches de paie à ce que l'horaire d'équipe produit.

    python3 tools/comparer-fiches.py VBN /chemin/vers/fiches/*.pdf

Deux chemins indépendants vers le même mois : d'un côté la fiche du
secrétariat social, de l'autre les journées lues dans le récapitulatif Excel.
Quand ils divergent, l'un des deux se trompe — et c'est presque toujours la
lecture de l'horaire, ce que ce script sert à trouver.

**Les fiches ne rentrent JAMAIS dans le dépôt** : elles portent le nom, le
numéro de registre national et l'IBAN. Ce script les lit sur place et n'en
ressort que des heures.
"""
import glob
import json
import os
import re
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)

# Ce que la fiche appelle une absence, et le code correspondant de l'horaire.
# « Repos compensatoire » couvre RTT et DTT sans les distinguer.
# Les clés sont celles sous lesquelles l'application ACCUMULE — « CP »
# s'additionne sous « CPAR », « MAL » sous « SMG ». Le code affiché dans
# l'horaire et la clé d'accumulation ne sont pas le même mot.
FAMILLES = {
    "vacances": ["VA"],
    "congé parent.": ["CPAR"],
    "jour férié": ["RJF", "FER"],
    "repos compensatoire": ["RTT", "DTT"],
    "SMG maladie": ["SMG"],
    "formation syndicale": ["FORM"],
    "abs. volontaire / injustifiée": ["ABS"],
}


def _hm(t):
    h, m = t.split(":")
    return int(h) + int(m) / 60


def lire_fiche(chemin):
    """Une fiche de paie : le mois, les heures prestées, les jours, les absences."""
    brut = subprocess.run([sys.executable, os.path.join(ICI, "lire-pdf.py"), chemin],
                          capture_output=True, text=True).stdout
    t = " ".join(brut.split())
    per = re.search(r"Période du (\d{2})\.(\d{2})\.(\d{4}) au", t)
    if not per:
        return None
    f = {"mois": int(per.group(2)), "annee": int(per.group(3)), "abs": {}}
    m = re.search(r"(\d{1,3}:\d{2})\s*Heure\(s\) prestée\(s\)", t)
    f["h"] = _hm(m.group(1)) if m else None
    m = re.search(r"(\d{1,3})\s*Jour\(s\) presté\(s\)", t)
    f["j"] = int(m.group(1)) if m else None
    for q, lib in re.findall(r"(\d{1,3}:\d{2})\s*Heure\(s\) "
                             r"([A-Za-zéèêàç.\s]{3,28}?)(?= [A-ZÉÈ0-9]| N°|$)", t):
        lib = lib.strip()
        if lib.lower().startswith("prest"):
            continue
        f["abs"][lib] = f["abs"].get(lib, 0) + _hm(q)
    # Les primes d'équipe, avec leurs heures : « 13:00 Suppl.Equipe Matin à
    # 0,90 ». Les variantes à 150 % et à 200 % sont les dimanches et jours
    # fériés — ce sont les MÊMES heures, payées plus cher, et elles comptent
    # donc dans le même total d'heures de prime.
    f["prime"] = {}
    for q, lib in re.findall(r"(\d{1,3}:\d{2})\s*Suppl\.?\s*Equipe\s*"
                             r"(Matin|Apr[èe]s-Midi|Nuit)", t, re.I):
        k = {"matin": "AM", "nuit": "N"}.get(lib.lower(), "PM")
        f["prime"][k] = f["prime"].get(k, 0) + _hm(q)
    # LA FICHE D'OUVRIER, relevée le 26/09/2026 sur celles de LCI : elle
    # n'écrit pas « Heure(s) prestée(s) » mais « Prestation normale », à 100,
    # 150 (samedi) et 200 % (dimanche et férié) — les mêmes heures payées plus
    # cher, qu'on additionne donc. Ses absences ont leurs propres libellés.
    if f["h"] is None and re.search(r"Type personnel Ouvrier", t):
        f["type"] = "Ouvrier"
        deja = set(f["abs"])
        f["h"] = sum(_hm(q) for q in re.findall(
            r"(\d{1,3}:\d{2})\s*Prestation normale à", t))
        for q, lib in re.findall(r"(\d{1,3}:\d{2})\s*(Congé Légal|Heures SHG Maladie|"
                                 r"Réduction Temps Travail) à", t):
            fam = {"Congé Légal": "vacances", "Heures SHG Maladie": "SMG maladie",
                   "Réduction Temps Travail": "repos compensatoire"}[lib]
            # la même absence s'écrit aussi en « Heure(s) vacances » plus
            # haut : ne pas la compter deux fois. La maladie, elle, tient sur
            # trois lignes (100, 150 et 200 %) qui s'additionnent.
            if fam not in deja:
                f["abs"][fam] = f["abs"].get(fam, 0) + _hm(q)
    f["jours"] = lire_jours(brut)
    return f if f["h"] is not None else None


# Le DÉTAIL DES PRESTATIONS, jour par jour — la fiche d'ouvrier le porte en
# seconde page. C'est le contrôle le plus fin qui soit : chaque date y dit
# la pause payée, les heures, l'absence. Les codes relevés sur huit fiches de
# 2026, tels que le secrétariat social les écrit (« VANCANCES » compris).
CODES_JOUR = {
    "PRIME EQUIPE MATIN": "AM", "PRIME EQUIPE APRES MIDI": "PM",
    "PRIME EQUIPE NUIT": "N",
    "VANCANCES LEGALES": "VA", "SHG MALADIE": "MAL",
    "ABSENCE TEMPS PARTIEL": "TP", "RED TEMPS TRAV NON PAYE": "RTT-np",
    "GREVE RECONNUE": "GREVE", "JOUR DE REPOS PAYE": "repos",
    "REPOS DIMANCHE": "repos",
}


def lire_jours(brut):
    """{MMJJ: [(heures, code)]} depuis le détail des prestations, ou {}."""
    if "Détail des prestations" not in brut:
        return {}
    d = " ".join(brut[brut.index("Détail des prestations"):].split())
    # Le détail court sur plusieurs pages, et l'outil n'en lisait que la
    # PREMIÈRE : la fin du mois tombait sans un mot, et une journée coupée
    # par le saut de page perdait sa suite (LCI le 22/03 : la prime en bas
    # de page, « 8:00 HEURES NORMALES » en haut de la suivante). Chaque page
    # « (suite) » est recollée à partir de sa première prestation, ce qui
    # laisse l'en-tête — nom, adresse — derrière.
    pages = d.split("##########")
    d = pages[0]
    for pg in pages[1:]:
        if "Détail des prestations (suite)" not in pg:
            continue
        m = re.search(r"\d{1,2}:\d{2} [A-Z]|\b(?:Lu|Ma|Me|Je|Ve|Sa|Di) \d{2}\.\d{2}\.\d{4}",
                      pg[pg.index("(suite)"):])
        if m:
            d += " " + pg[pg.index("(suite)") + m.start():]
    morceaux = re.split(r"\b(?:Lu|Ma|Me|Je|Ve|Sa|Di) (\d{2})\.(\d{2})\.\d{4}", d)
    out = {}
    for i in range(1, len(morceaux) - 2, 3):
        jour = morceaux[i + 1] + morceaux[i]
        out[jour] = [(_hm(q), c.strip()) for q, c in re.findall(
            r"(\d{1,2}:\d{2}) ([A-Z][A-Z .'/+-]+?)(?= \d{1,2}:\d{2}|$)", morceaux[i + 2])]
    return out


def resume_jour(items):
    """Ce que la fiche dit d'une journée : (pause payée ou code, heures)."""
    h = sum(q for q, c in items if c == "HEURES NORMALES")
    codes = [CODES_JOUR.get(c) for q, c in items]
    pause = next((c for c in codes if c in ("AM", "PM", "N")), None)
    if h:
        return (pause or "D", h)
    autre = next((c for c in codes if c and c not in ("AM", "PM", "N")), None)
    return (autre or ",".join(c for q, c in items) or "?", 0)


def horaire(ident, annee):
    """Le même mois, calculé depuis l'horaire, par le code de l'application."""
    script = r"""
/* argv : [node, script, index.html, horaire.json, identifiant] */
const fs=require("fs"); const html=fs.readFileSync(process.argv[2],"utf8");
function g(a,b){const i=html.indexOf(a);return html.slice(i,html.indexOf(b,i)+b.length);}
function pad2(n){return (n<10?"0":"")+n;}
eval([g("function R(x,d){","\n"),g("var SHIFT_CODES=[","];"),g("var ABS=[","\n];"),
 g("var ABSMAP={};","\n}"),g("var CYCLE6=[","];"),g("var CYCLE5=","\n"),g("var ANCRAGE=[","];"),
 g("var ANCRAGE_BASE=","\n"),g("function cyclePoste(","\n}"),g("var HORAIRE_PLAGES=","};"),
 g("function normPlage(","\n}"),g("function posteDepuisMention(","\n}"),g("var SHIFT_PLAGE=","};"),
 g("function plageMention(","\n}"),g("function seChevauchent(","\n}"),g("var JOUR_PRIME_PAUSE=","];"),
 g("var MENTIONS_NEUTRES=","];"),g("var ATELIERS=","\n"),g("function reprisRHS(","\n}"),
 g("function posteDepuisPlage(","\n}"),g("function dureeReelle(","\n}"),
 g("var ALIAS_HORAIRE=","\n"),g("var COQUILLES=","\n"),g("var JOUR_EN_ABSENCE=","\n"),
 g("var RX_PRIS_AILLEURS=","\n"),
 g("function parseHoraireEntry(","\n}"),g("var CYCLES=[","];"),g("function cycleDuMois(","\n}"),
 g("function posteDeCycle(","\n}"),g("function posteDuRemplace(","\n}"),
 g("function plageCommentaire(","\n}"),g("function debordePoste(","\n}"),
 g("var RX_PRIME_GARDEE=","\n"),g("function primeGardee(","\n}"),g("function motPrime(","\n}"),
 g("var GREVE_JOURS=","\n"),g("function lireJournee(","\n}"),g("function plageHorsPoste(","\n}"),
 g("var RX_RENVOI=","\n"),
 g("function renvoisDuMois(","\n}"),
 g("function epargnesDuMois(","\n}")].join("\n"));
/* La découpe est recopiée ici, et elle s'est déjà désynchronisée de
   index.html en silence : une constante ajoutée là-bas, et ce script
   s'arrêtait sur une ReferenceError au milieu d'une comparaison. On met
   donc la découpe à l'épreuve AVANT de s'en servir, comme le fait
   verifier-calendrier.js. */
[["lecture d'une cellule",function(){return parseHoraireEntry(["AM"],8).s==="AM";}],
 ["annotation « - »",function(){return parseHoraireEntry(["N","-"],8).h===0;}],
 ["renvoi « pris le »",function(){return !parseHoraireEntry(["-","2h -FT","pris le 19.09"],8).a;}],
 ["table des absences",function(){return Object.keys(ABSMAP).length>20;}],
 ["prime conservée",function(){
    return lireJournee({people:[]},["PM","AM","conserver prime de nuit"],2026,3,2,null,0,8,null).s==="N";}]
].forEach(function(e){
  var ok; try{ ok=e[1](); }catch(x){ ok=false; }
  if(!ok){ console.error("découpe de index.html faussée : "+e[0]); process.exit(2); }
});
const db=JSON.parse(fs.readFileSync(process.argv[3],"utf8"));
const p=db.people.filter(function(x){return x.id===process.argv[4];})[0];
if(!p){ console.log("{}"); process.exit(0); }
const out={}, jours={};
for(var m=1;m<=12;m++){
  var ep=epargnesDuMois(p,m), rv=renvoisDuMois(p,m,8),
      fit=cycleDuMois(p,db.year,m), nd=new Date(db.year,m,0).getDate();
  var h=0,j=0,ab={},par={};
  for(var d=1;d<=nd;d++){
    var k=pad2(m)+pad2(d), e=p.d[k]; if(!e) continue;
    /* lireJournee() ELLE-MÊME, et non une copie : la correction de cycle,
       les plages du commentaire et les heures renvoyées s'y enchaînent dans
       un ordre qui compte. Cet outil en gardait une version simplifiée, et
       il annonçait 24 h de prime du matin en avril là où l'application en
       montre 13 — c'est l'outil qui se trompait, pas elle. */
    var r=lireJournee(db,e,db.year,m,d,fit,ep[d],8,rv[d]);
    var hj=(r.h===undefined?8:r.h);
    /* rappel sur un repos : aucune heure normale, comme la fiche — mais la
       prime de pause reste payée, sur les heures sup */
    if(r.rs){ par[r.hsp||r.s]=(par[r.hsp||r.s]||0)+hj; j++; hj=0; }
    var A=r.a&&ABSMAP[r.a];
    if(r.s&&hj>0){ h+=hj; j++; par[r.s]=(par[r.s]||0)+hj; }
    jours[k]={s:(r.s&&hj>0)?r.s:null,h:(r.s?hj:0),a:r.a||null,
              k:(A?A.k:null),raw:e};
    if(r.ax) for(var q2=0;q2<r.ax.length;q2++){
      var AY=ABSMAP[r.ax[q2]];
      if(AY) ab[AY.k]=(ab[AY.k]||0)+((r.s||AY.h<8-0.01)?(AY.h||0):0);
    }
    /* la reprise partielle d'une journée prestée, comme compute() */
    if(r.s && r.rhsJ) ab.RHS=(ab.RHS||0)+r.rhsJ;
    if(A){
      /* même règle que la fiche : une absence d'une journée entière posée
         sur un repos ne vaut aucune heure */
      var pleine=(A.h>=8-0.01);
      ab[A.k]=(ab[A.k]||0)+((r.s||!pleine)?(A.h||0):0);
    }
  }
  out[m]={h:h,j:j,abs:ab,par:par};
}
out.jours=jours;
console.log(JSON.stringify(out));
"""
    chemin = os.path.join(ICI, ".horaire-mois.js")
    with open(chemin, "w", encoding="utf-8") as fh:
        fh.write(script)
    try:
        r = subprocess.run(["node", chemin, os.path.join(RACINE, "index.html"),
                            os.path.join(RACINE, "data", "horaire-%d.json" % annee), ident],
                           capture_output=True, text=True)
        # Le script node S'ARRÊTE quand sa découpe de index.html est faussée,
        # et c'est tout l'intérêt de ses épreuves. Encore faut-il ne pas
        # avaler son cri : « or "{}" » rendait un dictionnaire vide, et
        # l'outil annonçait sereinement zéro mois lu. Une panne silencieuse
        # est pire que pas de contrôle du tout.
        if r.returncode != 0 or not (r.stdout or "").strip():
            raise RuntimeError(
                "la lecture de l'horaire a échoué (code %d).\n%s"
                % (r.returncode, (r.stderr or "").strip() or "aucun message"))
        return json.loads(r.stdout)
    finally:
        os.remove(chemin)


MOIS = ["", "janv", "févr", "mars", "avr", "mai", "juin",
        "juil", "août", "sept", "oct", "nov", "déc"]


# l'année sur laquelle l'épreuve à vide se fait : celle de l'horaire du dépôt
ANNEE_EPREUVE = 2026


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    ident = sys.argv[1]
    if len(sys.argv) == 2:
        # SANS FICHE, ON MET QUAND MÊME LA DÉCOUPE À L'ÉPREUVE. CLAUDE.md
        # prescrit de relancer cet outil « ne serait-ce qu'à vide » après
        # toute modification de parseHoraireEntry() — et cette forme-là
        # sortait en 2 AVANT d'appeler horaire(), donc sans rien éprouver.
        # Un contrôle qui ne contrôle rien est pire que pas de contrôle :
        # c'est la règle déjà écrite pour l'enveloppe silencieuse de node.
        d = horaire(ident, ANNEE_EPREUVE)
        if not d:
            print("La découpe de index.html ne rend rien.", file=sys.stderr)
            return 1
        print("Découpe de index.html à l'épreuve : %d mois lus pour %s en %d."
              % (len([k for k in d if k.isdigit()]), ident, ANNEE_EPREUVE))
        print("Aucune fiche donnée — rien à confronter.")
        return 0
    chemins = []
    for a in sys.argv[2:]:
        chemins.extend(glob.glob(a))
    lues = [f for f in (lire_fiche(c) for c in sorted(chemins)) if f]
    if not lues:
        print("Aucune fiche lisible.", file=sys.stderr)
        return 1
    # un lot mélange souvent deux années : décembre se paie en janvier. On
    # garde celle qui porte le plus de fiches, et on dit ce qu'on écarte.
    annees = {}
    for f in lues:
        annees[f["annee"]] = annees.get(f["annee"], 0) + 1
    annee = max(annees, key=lambda a: annees[a])
    ecartees = sum(n for a, n in annees.items() if a != annee)
    fiches = {f["mois"]: f for f in lues if f["annee"] == annee}
    if ecartees:
        print("  (%d fiche(s) d'une autre année écartée(s))" % ecartees, file=sys.stderr)
    calc = horaire(ident, annee)

    print("%s — %d, %d fiche(s)\n" % (ident, annee, len(fiches)))
    print("  mois     FICHE           APPLICATION      ÉCART")
    print("           jours  heures   jours  heures    jours   heures")
    tj = th = fj = fh = 0
    for m in sorted(fiches):
        f = fiches[m]
        c = calc.get(str(m)) or calc.get(m) or {"h": 0, "j": 0, "abs": {}}
        tj += c["j"]; th += c["h"]; fj += f["j"]; fh += f["h"]
        print("  %-7s %5d %7.2f   %5d %7.2f    %+5d %+8.2f"
              % (MOIS[m], f["j"], f["h"], c["j"], c["h"], c["j"] - f["j"], c["h"] - f["h"]))
    print("  %-7s %5d %7.2f   %5d %7.2f    %+5d %+8.2f"
          % ("TOTAL", fj, fh, tj, th, tj - fj, th - fh))

    # Les primes d'équipe : une heure prestée dans une pause donne une heure
    # de prime de cette pause. C'est le contrôle le plus direct de la lecture
    # du POSTE — les heures peuvent tomber juste avec le mauvais poste, les
    # primes d'équipe non.
    #
    # Les variantes « à 150 % » et « à 200 % » de la fiche sont les dimanches
    # et jours fériés : les mêmes heures payées plus cher, donc comptées dans
    # le même total d'heures.
    if any(f.get("prime") for f in fiches.values()):
        print("\n  primes d'équipe, en heures")
        print("           matin           après-midi       nuit")
        print("           fiche  appli    fiche  appli    fiche  appli")
        for m in sorted(fiches):
            pf = fiches[m].get("prime") or {}
            c = calc.get(str(m)) or calc.get(m) or {}
            pa = c.get("par") or {}
            ligne = "  %-7s" % MOIS[m]
            for k in ("AM", "PM", "N"):
                a_, b_ = pf.get(k, 0), pa.get(k, 0)
                ligne += "  %6.2f %6.2f%s" % (a_, b_, " " if abs(a_ - b_) < 0.01 else "*")
            print(ligne)
        print("           * = écart")

    print("\n  absences, par famille")
    for lib, codes in FAMILLES.items():
        lignes = []
        for m in sorted(fiches):
            c = calc.get(str(m)) or calc.get(m) or {"abs": {}}
            vf = fiches[m]["abs"].get(lib, 0)
            vc = sum(c["abs"].get(k, 0) for k in codes)
            if vf or vc:
                lignes.append((m, vf, vc))
        if not lignes:
            continue
        faux = [x for x in lignes if abs(x[1] - x[2]) > 0.02]
        print("    %-22s %2d mois — %s" % (lib, len(lignes),
              "tous identiques" if not faux else
              "écart en " + ", ".join("%s (%.2f contre %.2f)" % (MOIS[m], vf, vc) for m, vf, vc in faux)))
    comparer_jours(fiches, calc.get("jours") or {})
    return 0


# Ce que l'application range sous une clé d'absence, et le code de la fiche
# qui lui répond. « repos » couvre le jour de repos payé ET le dimanche : la
# fiche d'ouvrier paie ses repos, l'horaire les écrit « - ».
EQUIV = {"VA": "VA", "SMG": "MAL", "TP": "TP", "CPAR": "CP", "RTT": "RTT-np",
         "RHS": "COMPENSATION PAYEE", "CE": "COMPENSATION PAYEE", "GREVE": "GREVE"}


def comparer_jours(fiches, jours):
    lignes = []
    n = ok = 0
    for m in sorted(fiches):
        for jour, items in sorted((fiches[m].get("jours") or {}).items()):
            n += 1
            fc, fh = resume_jour(items)
            a = jours.get(jour) or {}
            if a.get("s"):
                ac, ah = a["s"], a["h"]
            elif a.get("k"):
                ac, ah = EQUIV.get(a["k"], a["k"]), 0
            else:
                ac, ah = "repos", 0
            # une absence posée sur un jour de repos ne vaut rien, ni sur la
            # fiche ni dans l'application : la fiche l'écrit « repos »
            if fc == "repos" and not ah and not a.get("s") and a.get("k"):
                ac = "repos"
            if fc == ac and abs(fh - ah) < 0.01:
                ok += 1
                continue
            lignes.append("  %s/%s  fiche %-6s %5.2f   appli %-6s %5.2f   %s"
                          % (jour[2:], jour[:2], fc, fh, ac, ah,
                             json.dumps(a.get("raw"), ensure_ascii=False)))
    if not n:
        return
    print("\n  jour par jour : %d journées, %d identiques, %d écarts" % (n, ok, n - ok))
    for l in lignes:
        print(l)


if __name__ == "__main__":
    sys.exit(main())
