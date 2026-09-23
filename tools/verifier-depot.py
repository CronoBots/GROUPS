#!/usr/bin/env python3
"""Cherche des noms de personnes dans le dépôt lui-même.

    python3 tools/verifier-depot.py                # l'arbre de travail
    python3 tools/verifier-depot.py --historique   # + tous les commits

POURQUOI CET OUTIL EXISTE. Le 22/09/2026, treize noms de personnes réelles
vivaient dans ce dépôt PUBLIC — dans `CLAUDE.md` et dans les quatre outils
d'anonymisation, cités en exemple pour illustrer leurs motifs, pendant que
ces mêmes outils étaient écrits pour les retirer du classeur. Rien n'était
fonctionnel : que des commentaires et des docstrings. C'était tout aussi
public.

Le classeur et l'horaire passent, eux, par l'anonymiseur et son second
contrôle. **Le reste du dépôt n'avait aucun garde-fou** : une règle écrite
dans `CLAUDE.md`, et rien pour la faire respecter. Une règle ne garde rien.

CE QU'IL FAIT. Il lit tous les fichiers SUIVIS par git, y cherche les
chaînes ayant une forme de nom, et écarte celles qu'un humain a déjà
regardées — la liste `tools/formes-admises.txt`. Tout ce qui reste est
imprimé et le code de retour vaut 1.

CE QU'IL NE FAIT PAS, et il faut le savoir : il ne SAIT pas qu'une chaîne
est un nom. Personne ne le peut. Il sait dire « voici une chaîne qui a la
forme d'un nom et que personne n'a encore regardée », et il s'arrête là.
C'est la même doctrine que la garantie de l'anonymiseur : mieux vaut un
outil qui s'arrête qu'un outil qui laisse passer.

Ses motifs sont les SIENS et ne sont pas empruntés à verifier-anonymat.py :
les deux doivent pouvoir se contredire, sans quoi le second ne vérifie plus,
il répète.

QUAND UNE FORME EST LÉGITIME — « Fermentation, Distillation », « Chrome,
Edge », « Nom, Prénom » — on l'ajoute à `tools/formes-admises.txt`, avec la
raison. Ajouter une ligne à ce fichier est un acte : c'est là qu'un vrai nom
se glisserait s'il se glissait quelque part.
"""
import os
import re
import subprocess
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADMISES = os.path.join(RACINE, "tools", "formes-admises.txt")

# Les fichiers où chercher : ceux que git suit, et qui portent du texte.
TEXTE = re.compile(r"\.(md|py|ps1|js|html|json|txt|css|webmanifest|yml|yaml)$", re.I)

# --- les formes d'un nom de personne ----------------------------------------
# Un nom, ici, c'est DEUX morceaux dont au moins un porte des minuscules :
# « Nom, Prénom », « NOM, Prénom », « Nom PRÉNOM », « P. Nom ». Un morceau
# tout en majuscules de deux à quatre lettres est un trigramme et non un nom
# — c'est la convention anonyme du projet — mais accolé à un morceau en
# minuscules il redevient suspect : « Nom, APN » est une moitié de nom, et
# une moitié de nom nomme encore la personne.
_MIN = r"[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ'’-]{2,15}"     # Nom
_MAJ = r"[A-ZÀ-ÖØ-Þ]{4,15}"                        # NOM
_TRI = r"[A-ZÀ-ÖØ-Þ]{2,4}"                         # ABC
# Les espaces ne traversent pas une fin de ligne : un nom s'écrit d'un seul
# tenant. Sans cette borne, le dernier mot d'une ligne et le premier de la
# suivante formaient un nom — « Gluten \n Fermentation » — et le bruit
# noyait le signal.
FORMES = [
    re.compile(r"\b(%s),[ \\t]*(%s)\b" % (_MIN, _MIN)),          # Nom, Prénom
    re.compile(r"\b(%s),[ \\t]*(%s)\b" % (_MAJ, _MAJ)),          # NOM, PRÉNOM
    re.compile(r"\b(%s),[ \\t]*(%s)\b" % (_MIN, _TRI)),          # Nom, APN
    re.compile(r"\b(%s),[ \\t]*(%s)\b" % (_TRI, _MIN)),          # JBY, Prénom
    re.compile(r"\b(%s)[ \\t]+(%s)\b" % (_MIN, _MAJ)),           # Nom PRÉNOM
    re.compile(r"\b(%s)[ \\t]+(%s)\b" % (_MAJ, _MIN)),           # NOM Prénom
    re.compile(r"\b(%s)[ \\t]+([A-ZÀ-ÖØ-Þ]\.)" % _MIN),          # Nom P.
    re.compile(r"\b([A-ZÀ-ÖØ-Þ]\.)[ \\t]*(%s)\b" % _MIN),        # P. Nom
    re.compile(r"\b(%s)[ \\t]+(%s)[ \\t]*:" % (_MIN, _MIN)),         # Nom Prénom :
    # DEUX MOTS CAPITALISÉS À LA SUITE, sans virgule ni deux-points — « Nom
    # Prénom » tout court. C'est la forme la plus banale d'un nom, et la
    # première version de ce fichier ne la cherchait pas : un nom planté
    # dans le README y a passé sans un mot. Elle ramasse aussi du français
    # ordinaire — un début de phrase suivi d'un nom propre — et c'est le
    # prix à payer : ce bruit se range UNE fois dans formes-admises.txt,
    # après quoi seules les nouveautés parlent.
    re.compile(r"\b(%s)[ \\t]+(%s)\b" % (_MIN, _MIN)),           # Nom Prénom
]


def _admises():
    """Les formes qu'un humain a déjà regardées et jugées innocentes."""
    vues = set()
    if not os.path.exists(ADMISES):
        return vues
    with open(ADMISES, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.split("#")[0].strip()
            if ligne:
                vues.add(" ".join(ligne.split()))
    return vues


# Sa propre liste n'est pas un texte à fouiller : elle EST la liste des
# formes. La lire reviendrait à signaler chacune d'elles.
IGNORES = ("tools/formes-admises.txt",)


def _fichiers():
    r = subprocess.run(["git", "-C", RACINE, "ls-files"],
                       capture_output=True, text=True)
    for nom in r.stdout.splitlines():
        if TEXTE.search(nom) and nom not in IGNORES:
            yield nom


def _cherche(texte):
    """Les chaînes de forme nominale, normalisées sur leurs espaces."""
    trouve = set()
    for motif in FORMES:
        for m in motif.finditer(texte):
            trouve.add(" ".join(m.group(0).split()))
    return trouve


def _blobs():
    """Tous les blobs de l'historique, avec le chemin qui les portait."""
    r = subprocess.run(["git", "-C", RACINE, "rev-list", "--objects", "--all"],
                       capture_output=True, text=True)
    for ligne in r.stdout.splitlines():
        if " " not in ligne:
            continue
        sha, chemin = ligne.split(" ", 1)
        if TEXTE.search(chemin) and chemin not in IGNORES:
            yield sha, chemin


def main():
    hist = "--historique" in sys.argv
    admises = _admises()
    restes = {}

    for nom in _fichiers():
        chemin = os.path.join(RACINE, nom)
        try:
            with open(chemin, encoding="utf-8", errors="ignore") as f:
                texte = f.read()
        except OSError:
            continue
        for forme in _cherche(texte) - admises:
            restes.setdefault(forme, set()).add(nom)

    if hist:
        for sha, chemin in _blobs():
            data = subprocess.run(["git", "-C", RACINE, "cat-file", "blob", sha],
                                  capture_output=True).stdout
            texte = data.decode("utf-8", "ignore")
            for forme in _cherche(texte) - admises:
                restes.setdefault(forme, set()).add(chemin + " @" + sha[:8])

    if not restes:
        print("Aucune forme de nom que personne n'ait regardée."
              + ("  (arbre de travail ET historique)" if hist
                 else "  (arbre de travail)"))
        print("%d forme(s) admises dans %s." % (len(admises), "tools/formes-admises.txt"))
        return 0

    print("%d forme(s) de nom que personne n'a encore regardée :\n" % len(restes))
    for forme in sorted(restes):
        ou = sorted(restes[forme])
        print("  « %s »" % forme)
        for x in ou[:4]:
            print("        %s" % x)
        if len(ou) > 4:
            print("        … et %d autre(s)" % (len(ou) - 4))
    print("\nChacune se lit UNE par une. Si ce n'est pas un nom de personne,")
    print("l'ajouter à tools/formes-admises.txt avec sa raison. Si c'en est un,")
    print("le retirer du dépôt — et, s'il a déjà été poussé, réécrire l'histoire.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
