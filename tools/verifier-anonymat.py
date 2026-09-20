#!/usr/bin/env python3
"""Cherche, dans un classeur anonymisé, les noms du classeur d'origine.

    python3 tools/verifier-anonymat.py Recapitulatif.xlsm data/classeur-2026.xlsx

POURQUOI CET OUTIL EXISTE. L'anonymiseur relit sa propre sortie et y cherche
les noms qu'il vient de remplacer. Cette garantie a une faille de naissance :
elle ne cherche que les noms qu'il a SU APPRENDRE. Six personnes absentes de
la feuille « Personnel » et des colonnes nom/prénom de « Polyvalence » ont
ainsi traversé l'outil sans être remplacées, et sans être signalées — la
garantie a dit « aucun nom ne subsiste » en toute bonne foi.

Un second contrôle avait pourtant été fait. Il était bâti sur ces deux mêmes
sources, donc aveugle exactement au même endroit. Deux vérifications qui
puisent où l'outil puise n'en font qu'une : elles le répètent au lieu de le
contredire.

D'où celui-ci, qui n'emprunte RIEN à l'anonymiseur : ni sa liste de noms, ni
ses règles, ni sa notion de personne. Il prend TOUTES les chaînes du classeur
d'origine, retient celles qui ont une forme de nom — « Nom C. »,
« A. Nom », « Nom Prénom », « NOM » — et regarde lesquelles
survivent intactes dans la sortie.

Les survivants ne sont pas tous des fautes : « PRODUCTION », « CPPT » ou
« Adjoints Contremaître » ont la forme d'un nom sans en être un. C'est
pourquoi l'outil les IMPRIME au lieu de trancher : ils se lisent un par un.

Code de retour 1 s'il reste quelque chose à examiner, 0 sinon.
"""
import re
import sys
import unicodedata
import zipfile

# Les formes sous lesquelles un nom de personne s'écrit dans un classeur.
FORMES = [
    re.compile(r"^[A-ZÀ-Þ][a-zà-ÿ'-]{2,}\s+[A-ZÀ-Þ]\.?$"),                  # Nom C.
    re.compile(r"^[A-ZÀ-Þ]\.?\s*[A-ZÀ-Þ]?\.?\s+[A-ZÀ-Þ][a-zà-ÿ'-]{2,}$"),   # A. Nom
    re.compile(r"^[A-ZÀ-Þ][a-zà-ÿ'-]{2,},?\s+[A-ZÀ-Þ][a-zà-ÿ'-]{2,}$"),     # Nom Prénom
    re.compile(r"^[A-ZÀ-Þ]{4,}$"),                                          # NOM
]


def _plat(t):
    return "".join(c for c in unicodedata.normalize("NFD", t)
                   if unicodedata.category(c) != "Mn")


def _chaines(chemin):
    """Tout le texte du classeur, sans rien interpréter de sa structure."""
    z = zipfile.ZipFile(chemin)
    out = set()
    for n in z.namelist():
        if n.endswith((".xml", ".rels", ".vml")):
            t = z.read(n).decode("utf-8", "replace")
            out |= set(re.findall(r"<t[^>]*>([^<]{2,60})</t>", t))
            out |= set(re.findall(r"<v>([^<]{2,60})</v>", t))
    return out


def verifier(source, sortie):
    src = _chaines(source)
    texte = _plat("\n".join(_chaines(sortie)))

    survivants = []
    for t in sorted(src):
        t = t.strip()
        if not any(f.match(t) for f in FORMES):
            continue
        for mot in re.findall(r"[A-Za-zÀ-ÿ]{4,}", _plat(t)):
            # sensible à la casse : « paye » le verbe n'est pas « Paye » le nom
            if re.search(r"\b" + re.escape(mot) + r"\b", texte):
                survivants.append((t, mot))
                break

    print("%d chaînes distinctes dans la source · %d de forme nominale survivent"
          % (len(src), len(survivants)), file=sys.stderr)
    if not survivants:
        print("Aucune chaîne de forme nominale ne survit.", file=sys.stderr)
        return 0
    print("\nÀ examiner une par une — toutes ne sont pas des noms :", file=sys.stderr)
    for t, mot in survivants:
        print("   %-28s (mot retrouvé : %s)" % (t, mot), file=sys.stderr)
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__.strip())
    sys.exit(verifier(sys.argv[1], sys.argv[2]))
