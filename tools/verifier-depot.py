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
import io
import json
import os
import re
import subprocess
import sys
import zipfile

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADMISES = os.path.join(RACINE, "tools", "formes-admises.txt")

# Les fichiers où chercher : ceux que git suit, et qui portent du texte.
TEXTE = re.compile(r"\.(md|py|ps1|js|html|json|txt|css|webmanifest|yml|yaml)$", re.I)
# ET LE CLASSEUR, qui est le fichier du dépôt le plus susceptible de porter
# un nom — c'est de lui qu'ils viennent tous. Un .xlsx est une archive ZIP :
# son texte est COMPRESSÉ, donc invisible à qui lit les octets du fichier.
# La première version de cet outil ne le regardait pas du tout.
CLASSEUR = re.compile(r"\.xlsx$", re.I)

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
_INI = r"[A-ZÀ-ÖØ-Þ]"                              # P
# Un nom s'écrit d'un seul tenant : l'espace ne traverse pas une fin de
# ligne. Sans cette borne, le dernier mot d'une ligne et le premier de la
# suivante formaient un nom, et le bruit noyait le signal.
_ESP = r"[ \t]"
# Les espaces ne traversent pas une fin de ligne : un nom s'écrit d'un seul
# tenant. Sans cette borne, le dernier mot d'une ligne et le premier de la
# suivante formaient un nom — « Gluten \n Fermentation » — et le bruit
# noyait le signal.
FORMES = [
    re.compile(r"\b(%s),%s*(%s)\b" % (_MIN, _ESP, _MIN)),      # Nom, Prénom
    re.compile(r"\b(%s),%s*(%s)\b" % (_MAJ, _ESP, _MAJ)),      # NOM, PRÉNOM
    re.compile(r"\b(%s),%s*(%s)\b" % (_MIN, _ESP, _TRI)),      # Nom, APN
    re.compile(r"\b(%s),%s*(%s)\b" % (_TRI, _ESP, _MIN)),      # JBY, Prénom
    re.compile(r"\b(%s)%s+(%s)\b" % (_MIN, _ESP, _MAJ)),       # Nom PRÉNOM
    re.compile(r"\b(%s)%s+(%s)\b" % (_MAJ, _ESP, _MIN)),       # NOM Prénom
    re.compile(r"\b(%s)%s+(%s\.)" % (_MIN, _ESP, _INI)),       # Nom P.
    re.compile(r"\b(%s\.)%s*(%s)\b" % (_INI, _ESP, _MIN)),    # P. Nom
    # DEUX MOTS CAPITALISÉS À LA SUITE, sans virgule ni deux-points — « Nom
    # Prénom » tout court. C'est la forme la plus banale d'un nom, et la
    # première version de ce fichier ne la cherchait pas : un nom planté dans
    # le README y est passé sans un mot. Elle ramasse aussi du français
    # ordinaire — un début de phrase suivi d'un nom propre — et c'est le prix
    # à payer : ce bruit se range UNE fois dans formes-admises.txt, après
    # quoi seules les nouveautés parlent.
    re.compile(r"\b(%s)%s+(%s)\b" % (_MIN, _ESP, _MIN)),       # Nom Prénom
    # UN PRÉNOM SEUL SUIVI D'UN TRIGRAMME, puis un deux-points : c'est la
    # signature d'un commentaire Excel, et deux prénoms sont passés par là —
    # « Prénom JBY », « Prénom -CIE : ». Un prénom seul ne se distingue pas
    # d'un mot français ; accolé à un trigramme et à un deux-points, il se
    # distingue très bien. Le convertisseur, lui, ne retire que les auteurs
    # QUE LE CLASSEUR DÉCLARE : celui qui signe au fil du texte lui échappe.
    re.compile(r"\b(%s)%s*-?%s*(%s)%s*:" % (_MIN, _ESP, _ESP, _TRI, _ESP)),
]

# UN MOT CAPITALISÉ SUIVI D'UN TRIGRAMME — « Prénom JBY ». C'est l'autre
# forme par laquelle un prénom est passé, et elle est partout dans les
# commentaires du classeur : « Remplace JKS » y figure six cents fois. Ce qui
# distingue les deux n'est pas la forme mais le MOT DE TÊTE — « Remplace »
# est du français, « Prénom » est quelqu'un. La forme se range donc sous ce
# mot seul, « Remplace + trigramme », et la liste des admises en compte une
# quarantaine plutôt que six cents.
AVANT_TRIGRAMME = re.compile(r"\b(%s)%s+(%s)\b" % (_MIN, _ESP, _TRI))


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
        if (TEXTE.search(nom) or CLASSEUR.search(nom)) and nom not in IGNORES:
            yield nom


def _lire(octets, chemin):
    """Le texte d'un fichier suivi — en dépliant l'archive d'un classeur."""
    if CLASSEUR.search(chemin):
        morceaux = []
        try:
            z = zipfile.ZipFile(io.BytesIO(octets))
            for info in z.infolist():
                if re.search(r"\.(xml|rels|vml)$", info.filename, re.I):
                    morceaux.append(z.read(info).decode("utf-8", "ignore"))
        except (zipfile.BadZipFile, OSError):
            return ""
        return "\n".join(morceaux)
    return octets.decode("utf-8", "ignore")


# LES IDENTIFIANTS DE CONNEXION. Soixante vivaient dans data/classeur-2026.xlsx
# et cet outil répondait « aucune forme de nom » — ce n'en est pas une. Ils
# désignent pourtant quelqu'un, et CLAUDE.md lui-même en écrivait un en
# toutes lettres pour illustrer un motif. Découvert le 26/09/2026 par l'audit.
#
# Deux lettres et quatre à six chiffres, MAIS PAS DEUX LETTRES DE A À F : un
# dépôt est plein de couleurs (« #DD9877 », « FF000000 ») et d'identifiants
# de commit (« dc31569 ») qui ont exactement cette forme. Les logins de la
# maison commencent par « rt », qui n'est pas hexadécimal. Dans un classeur,
# on ne cherche que dans le TEXTE des cellules et des commentaires, jamais
# dans les octets du XML.
LOGIN = re.compile(r"(?<![A-Za-z0-9#])(?![A-Fa-f]{2}[0-9])[A-Za-z]{2}[0-9]{4,6}(?![0-9A-Za-z])")


def _texte_de_classeur(texte):
    """Le texte des cellules et des commentaires d'un classeur déplié, élément
    par élément — un login coupé en deux balises se recolle, deux
    commentaires voisins ne se collent pas."""
    return "\n".join("".join(re.findall(r"<t[^>]*>([^<]*)</t>", bloc))
                     for bloc in re.split(r"</comment>|</si>|</is>", texte))


def _cherche(texte, classeur=False):
    """Les chaînes de forme nominale, normalisées sur leurs espaces."""
    trouve = set()
    for m in LOGIN.finditer(_texte_de_classeur(texte) if classeur else texte):
        trouve.add("identifiant de connexion " + m.group(0))
    for motif in FORMES:
        for m in motif.finditer(texte):
            trouve.add(" ".join(m.group(0).split()))
    for m in AVANT_TRIGRAMME.finditer(texte):
        trouve.add(m.group(1) + " + trigramme")
    return trouve


def _blobs():
    """Tous les blobs de l'historique, avec le chemin qui les portait."""
    r = subprocess.run(["git", "-C", RACINE, "rev-list", "--objects", "--all"],
                       capture_output=True, text=True)
    for ligne in r.stdout.splitlines():
        if " " not in ligne:
            continue
        sha, chemin = ligne.split(" ", 1)
        if (TEXTE.search(chemin) or CLASSEUR.search(chemin)) and chemin not in IGNORES:
            yield sha, chemin


HORAIRE = os.path.join(RACINE, "data", "horaire-2026.json")
CLASSEUR_ANON = os.path.join(RACINE, "data", "classeur-2026.xlsx")


def _croise():
    """LES DEUX SORTIES VIENNENT DU MÊME CLASSEUR : ce que l'une a retiré et
    que l'autre a gardé est suspect.

    Le 25/09/2026, `data/horaire-2026.json` — dépôt PUBLIC — portait QUATRE
    prénoms et noms de famille de collègues, écrits au fil de commentaires :
    « changement d'équipe de <nom> », « remplace <prénom> qui remplaçait
    <prénom> », « Remplacé par CDE (<prénom>) ». Les motifs de cet outil ne
    les ont pas vus, et ils ne le pouvaient pas : UN PRÉNOM SEUL N'A AUCUNE
    FORME RECONNAISSABLE — c'est la faille que `CLAUDE.md` décrit depuis le
    22/09, et elle s'est refermée sur nous.

    Le convertisseur ne pouvait pas mieux faire : ces prénoms n'existent
    nulle part ailleurs dans le classeur, ni dans la ligne des noms, ni dans
    la feuille « Personnel », qui réduit le prénom à une initiale. Il n'avait aucun
    moyen de savoir que c'étaient des gens.

    L'ANONYMISEUR, LUI, LES AVAIT TOUS LES QUATRE. On ne lui emprunte pas ses
    motifs — les deux outils doivent pouvoir se contredire — on compare ses
    RÉSULTATS : tout mot capitalisé qui vit dans les commentaires du JSON
    mais ne se retrouve nulle part dans le classeur anonymisé est un mot que
    l'un des deux outils a retiré et que l'autre a laissé passer.

    Mesuré le 25/09/2026 : 121 mots capitalisés distincts dans les
    commentaires du JSON, 3 signalés — et les trois étaient des prénoms.
    Aucun bruit.
    """
    if not (os.path.exists(HORAIRE) and os.path.exists(CLASSEUR_ANON)):
        return {}
    try:
        db = json.load(io.open(HORAIRE, encoding="utf-8"))
        z = zipfile.ZipFile(CLASSEUR_ANON)
        blob = "".join(z.read(f).decode("utf-8", "ignore") for f in z.namelist()
                       if f.endswith((".xml", ".rels")))
    except Exception as e:
        print("  contrôle croisé impossible : %s" % e, file=sys.stderr)
        return {}
    mots = {}
    for p in db.get("people", []):
        for jour, v in (p.get("d") or {}).items():
            if not v or len(v) < 3:
                continue
            for m in re.findall(r"\b[A-ZÀ-Ý][a-zà-ÿ]{2,}\b", v[2] or ""):
                if m not in blob:
                    mots.setdefault(m, set()).add(
                        "data/horaire-2026.json (%s %s)" % (p.get("id"), jour))
    return mots


def main():
    hist = "--historique" in sys.argv
    admises = _admises()
    restes = {}

    for nom in _fichiers():
        chemin = os.path.join(RACINE, nom)
        try:
            with open(chemin, "rb") as f:
                texte = _lire(f.read(), nom)
        except OSError:
            continue
        for forme in _cherche(texte, bool(CLASSEUR.search(nom))) - admises:
            restes.setdefault(forme, set()).add(nom)

    # Le contrôle croisé, qui ne repose sur aucun motif.
    for forme, ou in _croise().items():
        if forme not in admises:
            restes.setdefault(forme, set()).update(ou)

    if hist:
        for sha, chemin in _blobs():
            data = subprocess.run(["git", "-C", RACINE, "cat-file", "blob", sha],
                                  capture_output=True).stdout
            texte = _lire(data, chemin)
            for forme in _cherche(texte, bool(CLASSEUR.search(chemin))) - admises:
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
