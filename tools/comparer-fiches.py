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
    return f if f["h"] is not None else None


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
 g("var ALIAS_HORAIRE=","\n"),g("var JOUR_EN_ABSENCE=","\n"),g("function parseHoraireEntry(","\n}"),g("var CYCLES=[","];"),g("function cycleDuMois(","\n}"),
 g("function posteDeCycle(","\n}"),g("function posteDuRemplace(","\n}"),g("var RX_RENVOI=","\n"),
 g("function epargnesDuMois(","\n}")].join("\n"));
const db=JSON.parse(fs.readFileSync(process.argv[3],"utf8"));
const p=db.people.filter(function(x){return x.id===process.argv[4];})[0];
if(!p){ console.log("{}"); process.exit(0); }
const out={};
for(var m=1;m<=12;m++){
  var ep=epargnesDuMois(p,m), fit=cycleDuMois(p,db.year,m), nd=new Date(db.year,m,0).getDate();
  var h=0,j=0,ab={};
  for(var d=1;d<=nd;d++){
    var k=pad2(m)+pad2(d), e=p.d[k]; if(!e) continue;
    var r=parseHoraireEntry(e,8,ep[d]);
    if((!r.s&&(e[0]||"").trim()!=="-")||r.jour){
      var c=posteDeCycle(fit,db.year,m,d)||posteDuRemplace(db,e,k,8)||(r.jour?(r.s||"D"):null);
      if(c&&c!==r.s) r.s=c; }
    var hj=(r.h===undefined?8:r.h), A=r.a&&ABSMAP[r.a];
    if(r.s&&hj>0){ h+=hj; j++; }
    if(A){
      /* même règle que la fiche : une absence d'une journée entière posée
         sur un repos ne vaut aucune heure */
      var pleine=(A.h>=8-0.01);
      ab[A.k]=(ab[A.k]||0)+((r.s||!pleine)?(A.h||0):0);
    }
  }
  out[m]={h:h,j:j,abs:ab};
}
console.log(JSON.stringify(out));
"""
    chemin = os.path.join(ICI, ".horaire-mois.js")
    with open(chemin, "w", encoding="utf-8") as fh:
        fh.write(script)
    try:
        r = subprocess.run(["node", chemin, os.path.join(RACINE, "index.html"),
                            os.path.join(RACINE, "data", "horaire-%d.json" % annee), ident],
                           capture_output=True, text=True)
        return json.loads(r.stdout or "{}")
    finally:
        os.remove(chemin)


MOIS = ["", "janv", "févr", "mars", "avr", "mai", "juin",
        "juil", "août", "sept", "oct", "nov", "déc"]


def main():
    if len(sys.argv) < 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    ident = sys.argv[1]
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
