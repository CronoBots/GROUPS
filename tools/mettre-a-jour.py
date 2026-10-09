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
  7. les neuf règles dures du calendrier, sur le nouvel horaire ;
  8. le garde-fou du dépôt, sur l'horaire NEUF — au passage à blanc, et non
     plus seulement après l'installation (le 09/10/2026, une forme innocente
     n'a été vue qu'à l'installation, et tout a été refait).

ET VITE. Le 09/10/2026, le client : « pourquoi la mise en place est-elle si
longue ? » — quatre minutes par passage, et il en faut deux (à blanc, puis
--installer). Mesuré étape par étape, puis corrigé là où le temps passait,
chaque fois avec une sortie IDENTIQUE À L'OCTET : l'anonymiseur 115 → 16 s,
le convertisseur 22 → 4 s, le vérificateur du calendrier 14 → 1,4 s, le
garde-fou 14 → 1,4 s. Les portes qui ne dépendent pas l'une de l'autre
tournent EN MÊME TEMPS (le convertisseur part du classeur source, pas de la
copie anonymisée), et leurs comptes rendus s'impriment dans l'ordre : la
première porte fermée, dans l'ordre des numéros, arrête tout comme avant.
Et --installer REPREND un passage à blanc réussi sur le même classeur, avec
les mêmes outils et le même horaire installé, au lieu de tout refaire.

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
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTILS = os.path.join(RACINE, "tools")


def _cv():
    spec = importlib.util.spec_from_file_location(
        "cv", os.path.join(OUTILS, "convertir-horaire.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _lancer(commande, sortie=None):
    """Lancer une étape ; rendre (code, sortie). Rien n'est imprimé ici : les
    étapes tournent en parallèle, leurs comptes rendus s'impriment dans
    l'ordre des portes."""
    r = subprocess.run(commande, cwd=RACINE, capture_output=True, text=True)
    texte = (r.stdout or "") + (r.stderr or "")
    if sortie:
        with open(sortie, "w", encoding="utf-8") as f:
            f.write(texte)
    return r.returncode, texte


def _rendre(numero, titre, resultat):
    """Le compte rendu d'une porte — ou l'arrêt de tout."""
    code, texte = resultat
    print("── %d. %s" % (numero, titre), flush=True)
    if code != 0:
        print(texte[-4000:])
        print("\nPORTE FERMÉE à l'étape %d (%s), code %d. Rien n'est installé."
              % (numero, titre, code), flush=True)
        os._exit(1)        # sans attendre les étapes encore en cours
    dernieres = [l for l in texte.strip().splitlines() if l.strip()][-2:]
    for l in dernieres:
        print("     " + l.strip())
    return texte


def _empreinte(*chemins):
    h = hashlib.sha256()
    for c in chemins:
        if os.path.exists(c):
            h.update(c.encode() + b"\0")
            with open(c, "rb") as f:
                h.update(f.read())
    return h.hexdigest()


def _outils():
    """Tout ce dont dépendent les huit portes : les outils et la page (le
    vérificateur du calendrier la découpe)."""
    noms = sorted(n for n in os.listdir(OUTILS) if n.endswith((".py", ".js", ".txt")))
    return _empreinte(*([os.path.join(OUTILS, n) for n in noms]
                        + [os.path.join(RACINE, "index.html")]))


MEMO = os.path.join(tempfile.gettempdir(), "biowanze-dernier-blanc.json")


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


def _portes(source, annee, tmp, neuf):
    """Les huit portes. Dépendances : 2, 3 et 5 lisent la copie anonymisée
    (1) ; 4 lit le classeur SOURCE et ne dépend de rien ; 7 lit l'horaire (4) ;
    6 lit l'export (5) et l'horaire (4) ; 8 lit l'horaire (4) et la copie (1).
    Tout ce qui peut tourner en même temps tourne en même temps ; les comptes
    rendus, eux, s'impriment dans l'ordre des numéros."""
    print("Dossier de travail : %s\n" % tmp, flush=True)
    py = sys.executable
    log = lambda n: os.path.join(tmp, n)
    with ThreadPoolExecutor(max_workers=4) as ex:
        f1 = ex.submit(_lancer, [py, os.path.join(OUTILS, "anonymiser-classeur.py"),
                                 source, neuf["classeur"]], log("1-anonymiser.log"))
        f4 = ex.submit(_lancer, [py, os.path.join(OUTILS, "convertir-horaire.py"),
                                 source, neuf["horaire"], str(annee)], log("4-convertir.log"))

        def calendrier():
            if f4.result()[0] != 0:
                return (0, "")
            return _lancer(["node", os.path.join(OUTILS, "verifier-calendrier.js"),
                            neuf["horaire"]], log("7-calendrier.log"))
        f7 = ex.submit(calendrier)

        _rendre(1, "anonymiser", f1.result())
        f2 = ex.submit(_lancer, [py, os.path.join(OUTILS, "verifier-anonymat.py"),
                                 source, neuf["classeur"]], log("2-anonymat.log"))
        f3 = ex.submit(fidelite, source, neuf["classeur"])
        f5 = ex.submit(_lancer, [py, os.path.join(OUTILS, "exporter-classeur.py"),
                                 neuf["classeur"], neuf["brut"]], log("5-exporter.log"))

        def garde_fou():
            if f4.result()[0] != 0:
                return (0, "")
            return _lancer([py, os.path.join(OUTILS, "verifier-depot.py"),
                            "--horaire=" + neuf["horaire"], "--classeur=" + neuf["classeur"]],
                           log("8-depot.log"))
        f8 = ex.submit(garde_fou)

        _rendre(2, "second contrôle d'anonymat", f2.result())
        ecarts = f3.result()
        print("── 3. fidélité de la copie à la source", flush=True)
        if ecarts:
            for k in ecarts[:20]:
                print("     %s ligne %d colonne %d" % k)
            print("\nPORTE FERMÉE à l'étape 3 : %d cellule(s) hors des zones nominatives"
                  " diffèrent de la source. L'anonymiseur a remplacé ce qui n'était pas"
                  " un nom. Rien n'est installé." % len(ecarts), flush=True)
            os._exit(1)
        print("     0 cellule différente hors des zones nominatives")
        _rendre(4, "convertir", f4.result())
        _rendre(5, "exporter le classeur entier", f5.result())
        _rendre(6, "intégralité cellule par cellule",
                _lancer([py, os.path.join(OUTILS, "verifier-integralite.py"),
                         neuf["brut"], neuf["horaire"]], log("6-integralite.log")))
        _rendre(7, "les neuf règles dures du calendrier", f7.result())
        _rendre(8, "garde-fou du dépôt sur l'horaire neuf", f8.result())


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
    cle = {"source": _empreinte(source), "outils": _outils(),
           "installe": _empreinte(cibles["horaire"]), "annee": annee}
    tmp = None
    if installer:
        try:
            memo = json.load(open(MEMO, encoding="utf-8"))
        except (OSError, ValueError):
            memo = {}
        if memo.get("cle") == cle and os.path.exists(os.path.join(memo.get("tmp", ""), "PORTES-OUVERTES")):
            tmp = memo["tmp"]
            print("Les huit portes ont été ouvertes à blanc sur ce même classeur, avec les"
                  " mêmes outils et le même horaire installé : elles ne sont pas refaites."
                  "\nDossier de travail repris : %s" % tmp)
    neuf_dir = tmp or tempfile.mkdtemp(prefix="biowanze-")
    # les mêmes noms que les cibles : l'export inscrit le nom du classeur lu,
    # et un nom de travail rendrait le fichier différent de celui qu'on
    # obtiendrait sur place
    neuf = dict((c, os.path.join(neuf_dir, os.path.basename(v))) for c, v in cibles.items())
    if tmp is None:
        tmp = neuf_dir
        _portes(source, annee, tmp, neuf)
        with open(os.path.join(tmp, "PORTES-OUVERTES"), "w") as f:
            f.write("ok\n")
        with open(MEMO, "w", encoding="utf-8") as f:
            json.dump({"cle": cle, "tmp": tmp}, f)

    rapport = os.path.join(tmp, "comparaison.txt")
    r = subprocess.run([sys.executable, os.path.join(OUTILS, "comparer-horaire.py"),
                        cibles["horaire"], neuf["horaire"]],
                       cwd=RACINE, capture_output=True, text=True)
    with open(rapport, "w", encoding="utf-8") as f:
        f.write(r.stdout)
    print("\n══ CE QUI CHANGE par rapport à l'horaire installé — à LIRE, et à dire"
          " au client ══\n")
    print(r.stdout.strip() or "(rien)")

    if not installer:
        print("\nLes huit portes sont ouvertes. À blanc : rien n'est installé.")
        print("Relancer avec --installer pour remplacer les trois fichiers de data/ —"
              " le passage à blanc sera repris, pas refait.")
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
    r = subprocess.run([sys.executable, os.path.join(OUTILS, "verifier-depot.py")],
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
