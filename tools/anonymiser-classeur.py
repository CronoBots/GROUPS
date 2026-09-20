#!/usr/bin/env python3
"""Recopie le récapitulatif Excel en remplaçant les noms par les trigrammes.

    python3 tools/anonymiser-classeur.py Recapitulatif.xlsm data/classeur-2026.xlsx

POURQUOI CET OUTIL EXISTE. Le convertisseur ne garde du classeur que ce
qu'il sait lire ; deux fois de suite, une information s'est perdue parce
qu'elle n'était pas dans les lignes qu'il regardait — le poste de travail de
chacun, puis ce qui entoure les noms. Le client : « ne peux-tu pas
simplement récupérer le même fichier en remplaçant les noms par les
trigrammes, pour l'avoir sous la main ».

C'est la bonne réponse, et elle supprime la catégorie entière de problème :
cet outil **n'interprète rien**. Il ouvre le classeur comme l'archive ZIP
qu'il est, remplace les noms partout où ils apparaissent, et referme. Tout
le reste — feuilles, formules, mises en forme, commentaires, colonnes qu'on
n'a pas encore comprises — passe intact. Ce qui n'est pas compris
aujourd'hui reste disponible demain.

CE QUI SORT DU FICHIER :
  - les noms complets, sous toutes leurs formes, remplacés par le trigramme ;
  - les auteurs de commentaires, préfixés à leur texte ;
  - les macros (vbaProject.bin) : elles peuvent contenir des noms, on ne
    sait pas les relire, et une macro n'a rien à faire dans un dépôt. La
    sortie est donc un .xlsx, pas un .xlsm ;
  - les propriétés du document : auteur, dernier enregistreur.

GARANTIE. Après écriture, le fichier produit est relu entièrement et l'outil
CHERCHE les noms qu'il vient de remplacer. S'il en trouve un seul, il
détruit sa sortie et s'arrête avec le détail. Un anonymiseur qui peut
laisser passer un nom sans le dire ne vaut rien.
"""
import os, re, shutil, sys, unicodedata, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
_conv = import_module("convertir-horaire")
Classeur, _annuaire, _sans_accent = _conv.Classeur, _conv._annuaire, _conv._sans_accent
_initiales, AUTEUR = _conv._initiales, _conv.AUTEUR

# Ce qui, dans le ZIP, ne doit pas être recopié.
EXCLUS = re.compile(r"(vbaProject\.bin|/vbaProject|\.bin$)", re.I)
# Les parties où chercher du texte. Tout le reste est recopié tel quel.
TEXTE = re.compile(r"\.(xml|rels|vml)$", re.I)


def _formes(nom):
    """Toutes les façons d'écrire un nom dans le classeur.

    « Nom, Prénom » s'y trouve aussi en « Nom Prénom », « Prénom Nom »,
    « NOM Prénom »… On génère les combinaisons plutôt que de deviner.
    """
    bouts = [b.strip() for b in re.split(r"[,\s]+", nom) if b.strip()]
    if not bouts:
        return []
    out = set()
    for sep in (", ", " ", "  ", ",", ""):
        out.add(sep.join(bouts))
        out.add(sep.join(reversed(bouts)))
    return [f for f in out if len(f) > 3]


def _motif(texte):
    """Un motif qui retrouve `texte` quels que soient les accents, la casse
    et les espaces — le classeur n'est pas régulier là-dessus."""
    bouts = [re.escape(b) for b in re.split(r"\s+", _sans_accent(texte).strip()) if b]
    if not bouts:
        return None
    return r"\b" + r"[\s,]*".join(bouts) + r"\b"


def _remplacer(donnee, regles):
    """Applique les règles sur le texte d'une partie XML.

    La comparaison se fait sur une copie SANS ACCENTS, et le remplacement sur
    l'original aux mêmes positions : « Prénom » et « Prénom » se valent sans
    qu'on ait à écrire les deux.
    """
    txt = donnee.decode("utf-8", "replace")
    plat = _sans_accent(txt)
    coupes = []
    for motif, par in regles:
        for m in re.finditer(motif, plat, re.I):
            coupes.append((m.start(), m.end(), par))
    if not coupes:
        return donnee, 0
    coupes.sort(key=lambda c: (c[0], -(c[1] - c[0])))
    out, pos, n = [], 0, 0
    for a, b, par in coupes:
        if a < pos:
            continue                      # déjà couvert par une règle plus longue
        out.append(txt[pos:a]); out.append(par); pos = b; n += 1
    out.append(txt[pos:])
    return "".join(out).encode("utf-8"), n


def anonymiser(src, dst, tolere=()):
    cl = Classeur(src)
    annuaire = _annuaire(cl)

    # Les noms connus, et le trigramme qui les remplace. L'annuaire officiel
    # d'abord ; à défaut, les initiales, comme partout ailleurs.
    noms = {}
    for cle, ini in annuaire.items():
        noms[cle] = ini
    for feuille in cl.feuilles:
        g = cl.grille(feuille)
        for ligne in g.values():
            for v in ligne.values():
                t = str(v).strip()
                if 4 <= len(t) <= 40 and re.search(r"[A-Za-zÀ-ÿ]{2,}[\s,]+[A-Za-zÀ-ÿ]{2,}", t) \
                   and not re.search(r"\d", t):
                    cle = _sans_accent(t).lower()
                    if cle in annuaire and cle not in noms:
                        noms[cle] = annuaire[cle]
    if not noms:
        sys.exit("Aucun nom trouvé : la feuille « Personnel » a-t-elle bougé ?")

    regles, surveille = [], []
    for cle, ini in noms.items():
        for forme in _formes(cle):
            m = _motif(forme)
            if m:
                regles.append((m, ini))
        for bout in re.split(r"[,\s]+", cle):
            if len(bout) >= 3:
                surveille.append((bout, ini))
    # les règles les plus longues d'abord : « Nom Prénom » avant « Nom »
    regles.sort(key=lambda r: -len(r[0]))
    regles.append((AUTEUR.pattern, ""))

    total, parties = 0, 0
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            if EXCLUS.search(info.filename):
                print("  écarté :", info.filename, file=sys.stderr)
                continue
            donnee = zin.read(info.filename)
            if TEXTE.search(info.filename):
                donnee, n = _remplacer(donnee, regles)
                if info.filename.startswith("docProps/"):
                    donnee = re.sub(rb"<(dc:creator|cp:lastModifiedBy)>[^<]*</\1>",
                                    rb"<\1></\1>", donnee)
                total += n
                parties += 1 if n else 0
            zout.writestr(info.filename, donnee)
    zin.close()

    # --- la garantie : relire, et chercher ce qu'on vient de remplacer -----
    restes = []
    zv = zipfile.ZipFile(dst)
    for info in zv.infolist():
        if not TEXTE.search(info.filename):
            continue
        plat = _sans_accent(zv.read(info.filename).decode("utf-8", "replace"))
        for bout, ini in surveille:
            if bout in tolere:
                continue
            for m in re.finditer(r"\b" + re.escape(bout) + r"\b", plat, re.I):
                # un mot courant écrit en minuscules n'est pas un nom
                brut = plat[m.start():m.end()]
                if brut[:1].islower():
                    continue
                ctx = plat[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")
                restes.append((info.filename, ini, ctx))
    zv.close()
    if restes:
        os.remove(dst)
        print("\n%d reste(s) de nom dans la sortie — fichier détruit :" % len(restes),
              file=sys.stderr)
        for f, ini, ctx in restes[:20]:
            print("   %-28s (%s)  …%s…" % (f, ini, ctx), file=sys.stderr)
        print("\nSi l'un d'eux n'est pas un nom — « Paye » peut être un mot —"
              " relancer avec --tolerer mot1,mot2 APRÈS l'avoir lu.", file=sys.stderr)
        sys.exit(2)

    taille = os.path.getsize(dst)
    print("%d nom(s) connu(s) · %d remplacement(s) dans %d partie(s) · %.1f Mo"
          % (len(noms), total, parties, taille / 1048576.0), file=sys.stderr)
    print("Aucun nom ne subsiste : vérifié sur la sortie.", file=sys.stderr)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tol = ()
    for a in sys.argv[1:]:
        if a.startswith("--tolerer="):
            tol = tuple(_sans_accent(x).strip().lower() for x in a.split("=", 1)[1].split(","))
    if len(args) < 2:
        sys.exit(__doc__)
    anonymiser(args[0], args[1], tol)
