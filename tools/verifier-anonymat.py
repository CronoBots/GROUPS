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
« P. Nom », « Nom Prénom », « NOM » — et regarde lesquelles
survivent intactes dans la sortie.

Les survivants ne sont pas tous des fautes : « PRODUCTION », « CPPT » ou
« Adjoints Contremaître » ont la forme d'un nom sans en être un. C'est
pourquoi l'outil les IMPRIME au lieu de trancher : ils se lisent un par un.

Code de retour 1 s'il reste quelque chose à examiner, 0 sinon.
"""
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

_M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

# Les formes sous lesquelles un nom de personne s'écrit dans un classeur.
FORMES = [
    re.compile(r"^[A-ZÀ-Þ][a-zà-ÿ'-]{2,}\s+[A-ZÀ-Þ]\.?$"),                  # Nom C.
    re.compile(r"^[A-ZÀ-Þ]\.?\s*[A-ZÀ-Þ]?\.?\s+[A-ZÀ-Þ][a-zà-ÿ'-]{2,}$"),   # P. Nom
    re.compile(r"^[A-ZÀ-Þ][a-zà-ÿ'-]{2,},?\s+[A-ZÀ-Þ][a-zà-ÿ'-]{2,}$"),     # Nom Prénom
    re.compile(r"^[A-ZÀ-Þ]{4,}$"),                                          # un NOM entier en majuscules
    # Deux MAJUSCULES séparées par une virgule — « NOM, PRÉNOM ». Un
    # morceau d'au moins quatre lettres est exigé, sans quoi « DKS, JBI »
    # y passerait : deux trigrammes ne sont pas un nom.
    re.compile(r"^[A-ZÀ-Þ]{4,},\s*[A-ZÀ-Þ]{2,}$|^[A-ZÀ-Þ]{2,},\s*[A-ZÀ-Þ]{4,}$"),
    # Un nom et un trigramme, dans un sens ou dans l'autre : l'anonymiseur
    # n'a remplacé QU'UNE des deux moitiés — « Nom, APN », « JBY,
    # Prénom ». Une demi-anonymisation nomme encore la personne.
    re.compile(r"^[A-ZÀ-Þ][a-zà-ÿ'-]{3,},\s*[A-ZÀ-Þ]{2,4}$"),
    re.compile(r"^[A-ZÀ-Þ]{2,4},\s*[A-ZÀ-Þ][a-zà-ÿ'-]{3,}$"),
]
# Les formes se testent sur un texte DÉBARRASSÉ de ce qui les entoure : dans
# un commentaire Excel la signature s'écrit « Nom, Prénom: » — avec deux
# points — et « Nom, Prénom (external): » — avec une parenthèse. Les
# deux faisaient échouer l'ancrage « $ », et neuf noms sont passés.
_ORNEMENTS = re.compile(r"\s*\([^)]*\)\s*|\s*:\s*$")


def _nu(t):
    return _ORNEMENTS.sub("", t.strip()).strip()


# --- les signatures de commentaires -----------------------------------------
# Elles échappaient à TOUTES les formes ci-dessus, et c'est par elles que la
# fuite est passée. On ne les devine plus : on les lit dans la structure du
# fichier et on les rend une par une. Ce qui est déjà anonyme est connu et
# court ; tout le reste est un nom jusqu'à preuve du contraire.
_ANONYMES = re.compile(r"^(?:Auteur|[A-ZÀ-Þ]{2,4}|[Rr][Tt]\d{4,6})$")


def _signatures(chemin):
    """Ce qui précède le premier « : » de chaque commentaire du classeur.

    Lit le TEXTE RECOLLÉ du commentaire : Excel coupe volontiers un nom en
    deux runs XML — « I » puis « om, Prénom (external): » — et un
    motif appliqué balise par balise ne voit alors ni l'un ni l'autre.
    """
    z = zipfile.ZipFile(chemin)
    out = {}
    for n in z.namelist():
        if "comments" not in n or not n.endswith(".xml"):
            continue
        try:
            r = ET.fromstring(z.read(n))
        except ET.ParseError:
            continue
        a = r.find("{%s}authors" % _M)
        if a is not None:
            for x in a:
                t = (x.text or "").strip()
                if t:
                    out[t] = out.get(t, 0) + 1
        for cm in r.iter("{%s}comment" % _M):
            txt = "".join((x.text or "") for x in cm.iter("{%s}t" % _M))
            i = txt.find(":")
            # Une signature est COURTE et d'un seul tenant. Sans ces deux
            # bornes, la règle avale le corps entier des commentaires qui
            # portent un « MPE : » ou un « CIE : » en plein milieu — et cent
            # cinq faux positifs noient les quinze vrais.
            if 0 < i <= 40 and "\n" not in txt[:i]:
                t = txt[:i].strip()
                if t:
                    out[t] = out.get(t, 0) + 1
    return out


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
        t = _nu(t)
        if not t or not any(f.match(t) for f in FORMES):
            continue
        for mot in re.findall(r"[A-Za-zÀ-ÿ]{4,}", _plat(t)):
            # sensible à la casse : « paye » le verbe n'est pas « Paye » le nom
            if re.search(r"\b" + re.escape(mot) + r"\b", texte):
                survivants.append((t, mot))
                break

    # --- les signatures de commentaires, contrôle à part ------------------
    # C'est par elles que neuf noms sont passés, et AUCUNE forme ci-dessus ne
    # les voyait : « Nom, Prénom: » a un deux-points, « Prénom: » est un
    # mot seul, et « I » + « om, Prénom » est coupé en deux balises.
    signatures = _signatures(sortie)
    sales = {t: c for t, c in signatures.items() if not _ANONYMES.match(t)}
    # Celles qui ont une FORME DE NOM sont des fautes ; les autres sont du
    # texte de corps attrapé au passage — « Validation CLE prod 09 » — et se
    # lisent sans qu'on crie. Les deux sortent, car une signature qu'aucune
    # forme ne reconnaît peut encore être un prénom seul.
    noms = {t: c for t, c in sales.items() if any(f.match(_nu(t)) for f in FORMES)}
    autres = {t: c for t, c in sales.items() if t not in noms}

    print("%d chaînes distinctes dans la source · %d de forme nominale survivent"
          % (len(src), len(survivants)), file=sys.stderr)
    print("%d signature(s) de commentaire distincte(s) dans la sortie · %d non anonyme(s)"
          % (len(signatures), len(sales)), file=sys.stderr)

    if not survivants and not sales:
        print("Aucune chaîne de forme nominale ne survit, aucune signature non anonyme.",
              file=sys.stderr)
        return 0
    if survivants:
        print("\nÀ examiner une par une — toutes ne sont pas des noms :", file=sys.stderr)
        for t, mot in survivants:
            print("   %-28s (mot retrouvé : %s)" % (t, mot), file=sys.stderr)
    if noms:
        print("\nSIGNATURES DE COMMENTAIRE QUI SONT DES NOMS — une signature n'est"
              "\njamais une information de travail ; elle doit disparaître :", file=sys.stderr)
        for t, c in sorted(noms.items(), key=lambda kv: -kv[1]):
            print("   %6d ×  %s" % (c, t), file=sys.stderr)
    if autres:
        print("\nAutres têtes de commentaire, à lire — un prénom seul n'a pas de"
              "\nforme reconnaissable et se cacherait ici :", file=sys.stderr)
        for t, c in sorted(autres.items(), key=lambda kv: -kv[1]):
            print("   %6d ×  %s" % (c, t), file=sys.stderr)
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__.strip())
    sys.exit(verifier(sys.argv[1], sys.argv[2]))
