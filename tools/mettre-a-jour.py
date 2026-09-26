#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Du récapitulatif Excel reçu du client à ce que l'application lit — en UNE
commande, et rien n'est installé tant qu'une porte reste fermée.

    python3 tools/mettre-a-jour.py /chemin/Recapitulatif.xlsm            # à blanc
    python3 tools/mettre-a-jour.py /chemin/Recapitulatif.xlsm --installer

La procédure tenait en douze commandes à enchaîner à la main, dans le bon
ordre, en lisant chaque code de retour — et deux de ces contrôles sortaient
TOUJOURS en 1, si bien qu'on avait appris à ne plus les lire. L'audit du
26/09/2026 a trouvé la copie de référence publique corrompue sur 480 cellules
et porteuse de 60 identifiants de connexion : chaque outil avait fait son
travail, aucune porte n'avait été fermée.

LES PORTES, dans l'ordre — la première qui échoue arrête tout :

  1. l'anonymiseur, et sa garantie (aucun nom appris ne subsiste) ;
  2. le second contrôle, qui n'emprunte rien à l'anonymiseur ;
  3. LA FIDÉLITÉ : hors des zones nominatives — ligne 10 des feuilles de
     personnes, « Personnel », nom et prénom de « Polyvalence » —, la copie
     anonymisée ne diffère de la source sur AUCUNE cellule. C'est la porte
     qui manquait le jour où « Arr » est devenu « PAR » ;
  4. le convertisseur, et sa garantie (aucun nom du classeur dans le JSON) ;
  5. l'export intégral, et son aller-retour contre le XML ;
  6. l'intégralité, cellule par cellule : horaire contre classeur entier ;
  7. les neuf règles dures du calendrier, sur le nouvel horaire.

Tout s'écrit dans un DOSSIER TEMPORAIRE. À blanc, l'outil s'arrête là et
imprime le rapport du comparateur — qu'il faut LIRE, et dont il faut dire au
client ce qui a bougé. Avec --installer, et seulement si les sept portes
sont ouvertes : les trois fichiers de data/ sont remplacés ensemble, `V` est
incrémenté dans sw.js, et le garde-fou du dépôt passe sur le résultat. S'il
échoue, les fichiers d'avant sont remis en place depuis leur copie — et non
par git, qui écraserait aussi ce qu'on n'a pas touché.

Restent à faire à la main, et l'outil le rappelle : relire le rapport,
tester dans un navigateur, committer.
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTILS = os.path.join(RACINE, "tools")


def _cv():
    spec = importlib.util.spec_from_file_location(
        "cv", os.path.join(OUTILS, "convertir-horaire.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _porte(numero, titre, commande, sortie=None):
    """Lancer une étape ; rendre sa sortie, ou arrêter tout."""
    print("── %d. %s" % (numero, titre), flush=True)
    r = subprocess.run(commande, cwd=RACINE, capture_output=True, text=True)
    texte = (r.stdout or "") + (r.stderr or "")
    if sortie:
        with open(sortie, "w", encoding="utf-8") as f:
            f.write(texte)
    if r.returncode != 0:
        print(texte[-4000:])
        print("\nPORTE FERMÉE à l'étape %d (%s), code %d. Rien n'est installé."
              % (numero, titre, r.returncode))
        sys.exit(1)
    dernieres = [l for l in texte.strip().splitlines() if l.strip()][-2:]
    for l in dernieres:
        print("     " + l.strip())
    return texte


def fidelite(source, copie):
    """Les cellules où la copie anonymisée diffère de la source HORS des zones
    nominatives. Écrit ici, et non emprunté à l'anonymiseur : on vérifie son
    résultat, pas sa logique."""
    cv = _cv()

    def cellules(chemin):
        cl = cv.Classeur(chemin)
        out = {}
        for f in cl.feuilles:
            for l, ligne in cl.grille(f, fusions=()).items():
                for c, v in ligne.items():
                    out[(f, l, c)] = v
        return out
    a, b = cellules(source), cellules(copie)
    ecarts = []
    for k in sorted(set(a) | set(b), key=str):
        if a.get(k) == b.get(k):
            continue
        f, l, c = k
        if (f in cv.FEUILLES and l == cv.LIGNE_NOMS) or f == "Personnel" \
                or (f == "Polyvalence" and c in (2, 3)):
            continue
        ecarts.append(k)
    return ecarts


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    source = os.path.abspath(args[0])
    annee = int(args[1]) if len(args) > 1 else 2026
    installer = "--installer" in sys.argv
    if not os.path.exists(source):
        sys.exit("introuvable : %s" % source)
    if os.path.commonpath([source, RACINE]) == RACINE:
        sys.exit("Le classeur source porte des noms : il ne doit pas être dans le dépôt.")

    data = os.path.join(RACINE, "data")
    cibles = {
        "classeur": os.path.join(data, "classeur-%d.xlsx" % annee),
        "brut": os.path.join(data, "classeur-%d-brut.json" % annee),
        "horaire": os.path.join(data, "horaire-%d.json" % annee),
    }
    tmp = tempfile.mkdtemp(prefix="biowanze-")
    # les mêmes noms que les cibles : l'export inscrit le nom du classeur lu,
    # et un nom de travail rendrait le fichier différent de celui qu'on
    # obtiendrait sur place
    neuf = dict((cle, os.path.join(tmp, os.path.basename(c))) for cle, c in cibles.items())
    print("Dossier de travail : %s\n" % tmp)
    py = sys.executable

    _porte(1, "anonymiser", [py, os.path.join(OUTILS, "anonymiser-classeur.py"),
                             source, neuf["classeur"]], os.path.join(tmp, "1-anonymiser.log"))
    _porte(2, "second contrôle d'anonymat",
           [py, os.path.join(OUTILS, "verifier-anonymat.py"), source, neuf["classeur"]],
           os.path.join(tmp, "2-anonymat.log"))
    print("── 3. fidélité de la copie à la source", flush=True)
    ecarts = fidelite(source, neuf["classeur"])
    if ecarts:
        for k in ecarts[:20]:
            print("     %s ligne %d colonne %d" % k)
        print("\nPORTE FERMÉE à l'étape 3 : %d cellule(s) hors des zones nominatives"
              " diffèrent de la source. L'anonymiseur a remplacé ce qui n'était pas"
              " un nom. Rien n'est installé." % len(ecarts))
        sys.exit(1)
    print("     0 cellule différente hors des zones nominatives")
    _porte(4, "convertir", [py, os.path.join(OUTILS, "convertir-horaire.py"),
                            source, neuf["horaire"], str(annee)],
           os.path.join(tmp, "4-convertir.log"))
    _porte(5, "exporter le classeur entier",
           [py, os.path.join(OUTILS, "exporter-classeur.py"), neuf["classeur"], neuf["brut"]],
           os.path.join(tmp, "5-exporter.log"))
    _porte(6, "intégralité cellule par cellule",
           [py, os.path.join(OUTILS, "verifier-integralite.py"), neuf["brut"], neuf["horaire"]],
           os.path.join(tmp, "6-integralite.log"))
    _porte(7, "les neuf règles dures du calendrier",
           ["node", os.path.join(OUTILS, "verifier-calendrier.js"), neuf["horaire"]],
           os.path.join(tmp, "7-calendrier.log"))

    rapport = os.path.join(tmp, "comparaison.txt")
    r = subprocess.run([py, os.path.join(OUTILS, "comparer-horaire.py"),
                        cibles["horaire"], neuf["horaire"]],
                       cwd=RACINE, capture_output=True, text=True)
    with open(rapport, "w", encoding="utf-8") as f:
        f.write(r.stdout)
    print("\n══ CE QUI CHANGE par rapport à l'horaire installé — à LIRE, et à dire"
          " au client ══\n")
    print(r.stdout.strip() or "(rien)")

    if not installer:
        print("\nLes sept portes sont ouvertes. À blanc : rien n'est installé.")
        print("Relancer avec --installer pour remplacer les trois fichiers de data/.")
        return 0

    # --- installer ---------------------------------------------------------
    identiques = all(os.path.exists(cibles[c]) and
                     open(cibles[c], "rb").read() == open(neuf[c], "rb").read()
                     for c in cibles)
    if identiques:
        print("\nLes trois fichiers sont identiques à ceux de data/ : rien à installer,"
              " et V ne bouge pas.")
        return 0
    avant = os.path.join(tmp, "avant")
    os.makedirs(avant)
    sw = os.path.join(RACINE, "sw.js")
    for cle, chemin in list(cibles.items()) + [("sw", sw)]:
        if os.path.exists(chemin):
            shutil.copy2(chemin, os.path.join(avant, os.path.basename(chemin)))
    for cle in cibles:
        shutil.copy2(neuf[cle], cibles[cle])
    texte = open(sw, encoding="utf-8").read()
    m = re.search(r'var V = "nfdm-v(\d+)";', texte)
    if m:
        texte = texte.replace(m.group(0), 'var V = "nfdm-v%d";' % (int(m.group(1)) + 1), 1)
        open(sw, "w", encoding="utf-8").write(texte)
    r = subprocess.run([py, os.path.join(OUTILS, "verifier-depot.py")],
                       cwd=RACINE, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        for nom in os.listdir(avant):
            dest = sw if nom == "sw.js" else os.path.join(data, nom)
            shutil.copy2(os.path.join(avant, nom), dest)
        print("\nLE GARDE-FOU DU DÉPÔT ÉCHOUE : les fichiers d'avant sont remis en place.")
        return 1
    print("\nInstallé : %s" % ", ".join(os.path.relpath(c, RACINE) for c in cibles.values()))
    if m:
        print("V : nfdm-v%s → nfdm-v%d" % (m.group(1), int(m.group(1)) + 1))
    print("Garde-fou du dépôt : à zéro.")
    print("\nReste à faire : relire %s, dire au client ce qui a bougé, tester"
          " dans un navigateur, committer." % rapport)
    return 0


if __name__ == "__main__":
    sys.exit(main())
