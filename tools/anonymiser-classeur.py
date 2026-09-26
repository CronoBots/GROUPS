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
  - les propriétés du document : auteur, dernier enregistreur, étiquette de
    sensibilité de l'employeur (docProps/custom.xml), chemin réseau ;
  - les identifiants de connexion écrits dans les commentaires.

GARANTIE. Après écriture, le fichier produit est relu entièrement et l'outil
CHERCHE les noms qu'il vient de remplacer. S'il en trouve un seul, il
détruit sa sortie et s'arrête avec le détail. Un anonymiseur qui peut
laisser passer un nom sans le dire ne vaut rien.
"""
import os, re, shutil, sys, unicodedata, zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
_conv = import_module("convertir-horaire")
Classeur, _annuaire, _sans_accent = _conv.Classeur, _conv._annuaire, _conv._sans_accent
LIGNE_NOMS = _conv.LIGNE_NOMS
FEUILLES = _conv.FEUILLES
AUTEUR = _conv.AUTEUR


def _initiales(t):
    """Les initiales, corrigées EXACTEMENT comme le convertisseur les corrige.

    Sans cela, les deux outils écrivaient des identifiants différents pour la
    même personne, et la copie de référence devenait ambiguë là où le JSON ne
    l'était pas : le classeur anonymisé porte deux lignes « GBT » dans
    l'onglet Polyvalence — Gluten et Chaudières — parce que l'anonymiseur
    ignorait que le client avait tranché, et donné GBO à l'un des deux.

    Une copie de référence qui confond deux personnes ne vaut plus comme
    référence : c'est précisément ce qu'on est allé y chercher qu'elle perd.
    """
    corrige = _conv.CORRECTIONS.get(_conv._empreinte(_sans_accent(t).lower()))
    return corrige or _conv._initiales(t)

# Ce qui, dans le ZIP, ne doit pas être recopié.
EXCLUS = re.compile(r"(vbaProject\.bin|/vbaProject|\.bin$|^docProps/custom\.xml$)", re.I)
# Les parties où chercher du texte. Tout le reste est recopié tel quel.
TEXTE = re.compile(r"\.(xml|rels|vml)$", re.I)
COMMENTAIRES = re.compile(r"comments\d*\.xml$", re.I)

# --- la signature d'un commentaire ------------------------------------------
# Neuf noms sont passés par là. AUTEUR, qui travaille sur les octets du XML,
# exige une virgule et ne voit donc ni « Nom Prénom : » ni
# « Prénom: » ; et il ne voit RIEN du tout quand Excel coupe le nom en deux
# runs — « I » puis « om, Prénom ». Un motif appliqué balise par
# balise ne peut pas recoller ce que la structure a séparé.
#
# D'où cette passe-ci, qui lit la STRUCTURE : elle recolle le texte de chaque
# commentaire, et retire ce qui précède le premier « : » quand cela a une
# forme de nom.
#
# Ces formes sont écrites ICI et non empruntées à verifier-anonymat.py : le
# contrôle ne vérifierait plus, il répéterait.
_M_SS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_NOMS = [
    re.compile(r"^[A-ZÀ-Þ][a-zà-ÿ'-]{2,},?\s+[A-ZÀ-Þ][a-zà-ÿ'-]{2,}$"),   # Nom Prénom
    re.compile(r"^[A-ZÀ-Þ]{4,},\s*[A-ZÀ-Þ]{2,}$"),                        # NOM, PRÉNOM
    re.compile(r"^[A-ZÀ-Þ]{2,},\s*[A-ZÀ-Þ]{4,}$"),
    re.compile(r"^[A-ZÀ-Þ][a-zà-ÿ'-]{3,},\s*[A-ZÀ-Þ]{2,4}$"),             # Nom, APN
    re.compile(r"^[A-ZÀ-Þ]{2,4},\s*[A-ZÀ-Þ][a-zà-ÿ'-]{3,}$"),             # JBY, Prénom
]
_ORNEMENT = re.compile(r"\s*\([^)]*\)\s*|\s*/\s*[Rr][Tt]\d{4,6}\s*|\s*-\s*[A-ZÀ-Þ]{2,4}\s*$")


def _est_nom(t):
    t = _ORNEMENT.sub("", t).strip()
    return bool(t) and any(f.match(t) for f in _NOMS)


_XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def _editer_morceaux(noeuds, coupes):
    """Appliquer des coupes au texte RECOLLÉ d'un commentaire, morceau par
    morceau, sans déplacer un seul caractère d'un morceau à l'autre.

    `coupes` : des (début, fin, remplacement) en positions du texte recollé,
    sans chevauchement. Le remplacement s'écrit dans le morceau où la coupe
    commence.

    CHAQUE MORCEAU GARDE SA MISE EN FORME, ET C'EST TOUT L'OBJET. La
    version précédente recollait tout le commentaire dans le PREMIER morceau
    et vidait les autres — or le premier est la signature, en gras et souvent
    BARRÉE. Mesuré le 26/09/2026 : le texte ajouté ensuite par un autre
    auteur, non barré, héritait du barré — 621 commentaires mêlant barré et
    non barré dans la source, 41 dans la copie. Le barré dit qu'une consigne
    a été annulée ; le déplacer, c'est réécrire le classeur. Les sauts de
    ligne suivaient le même chemin : 11 550 commentaires sur plusieurs
    lignes dans la source, 3 860 dans la copie.
    """
    textes = [x.text or "" for x in noeuds]
    debuts, o = [], 0
    for s in textes:
        debuts.append(o)
        o += len(s)
    garde = [list(s) for s in textes]
    touches = set()
    for a, b, rep in sorted(coupes):
        for k, s in enumerate(textes):
            d, f = debuts[k], debuts[k] + len(s)
            for g in range(max(a, d), min(b, f)):
                garde[k][g - d] = ""
                touches.add(k)
        if rep:
            # la coupe n'est jamais vide : `a` tombe dans un morceau
            k = next(k for k, s in enumerate(textes)
                     if debuts[k] <= a < debuts[k] + len(s))
            garde[k][a - debuts[k]] = rep + garde[k][a - debuts[k]]
            touches.add(k)
    for k in touches:
        noeuds[k].text = "".join(garde[k])
        noeuds[k].set(_XML_SPACE, "preserve")
    return bool(touches)


def _sans_signature(donnee):
    """Retirer la signature en tête de chaque commentaire, et les auteurs.

    Une signature est COURTE et d'un seul tenant : sans ces deux bornes, la
    règle avalerait le corps des commentaires qui portent un « MPE : » en
    plein milieu.
    """
    ET.register_namespace("", _M_SS)
    try:
        r = ET.fromstring(donnee)
    except ET.ParseError:
        return donnee, 0
    n = 0
    a = r.find("{%s}authors" % _M_SS)
    if a is not None:
        for x in a:
            if (x.text or "").strip() and (x.text or "").strip() != "Auteur":
                x.text = "Auteur"
                n += 1
    for cm in r.iter("{%s}comment" % _M_SS):
        noeuds = list(cm.iter("{%s}t" % _M_SS))
        joint = "".join(x.text or "" for x in noeuds)
        i = joint.find(":")
        if not (0 < i <= 40) or "\n" in joint[:i] or not _est_nom(joint[:i]):
            continue
        fin = i + 1
        while fin < len(joint) and joint[fin] in " \t\r\n":
            fin += 1
        if _editer_morceaux(noeuds, [(0, fin, "")]):
            n += 1
    if not n:
        return donnee, 0
    return ET.tostring(r, encoding="UTF-8", xml_declaration=True), n


# UN IDENTIFIANT DE CONNEXION N'EST PAS UN NOM, ET IL DÉSIGNE QUAND MÊME
# QUELQU'UN. Mesuré le 26/09/2026 par l'audit : data/classeur-2026.xlsx —
# fichier d'un dépôt PUBLIC — portait 60 occurrences de trois logins
# d'entreprise (de la forme « RT0xxxx »), alors que l'horaire
# et le brut n'en portaient plus. AUTEUR les connaît, mais il travaille sur
# les OCTETS du XML et exige un blanc devant : un login en tête d'un morceau
# suit un « > », et AUTEUR ne le voit jamais. Le motif ne voit pas les
# balises ; ce qui lit la structure, si.
#
# D'où cette passe, sur le texte RECOLLÉ de chaque commentaire, APRÈS les
# signatures et les noms — l'ordre que le convertisseur a appris à ses
# dépens : un login est le suffixe ordinaire d'une signature, le remplacer
# d'abord la rend méconnaissable.
#
# Suivi d'un deux-points, il EST une signature — la seconde d'un
# commentaire, « RT0xxxx: remplace PBL » — et part en entier : il ne signe
# rien qu'on ait besoin de lire. Au fil du texte, il est REMPLACÉ, pas
# effacé : la phrase se lit encore, et dit qu'on a retiré quelque chose.
#
# LE MOTIF NE S'APPLIQUE JAMAIS AUX OCTETS DU XML : il y attraperait les
# couleurs « FF000000 » des styles et les fragments des identifiants
# « ns2:uid » — une centaine par fichier, mesuré.
LOGIN = re.compile(r"\b[A-Za-z]{2}\d{4,6}\b(\s*:[ \t]*)?")


def _sans_login(donnee):
    """Retirer les identifiants de connexion du texte des commentaires."""
    ET.register_namespace("", _M_SS)
    try:
        r = ET.fromstring(donnee)
    except ET.ParseError:
        return donnee, 0
    n = 0
    for cm in r.iter("{%s}comment" % _M_SS):
        noeuds = list(cm.iter("{%s}t" % _M_SS))
        joint = "".join(x.text or "" for x in noeuds)
        coupes = [(m.start(), m.end(), "" if m.group(1) else "(identifiant retiré)")
                  for m in LOGIN.finditer(joint)]
        if coupes and _editer_morceaux(noeuds, coupes):
            n += len(coupes)
    if not n:
        return donnee, 0
    return ET.tostring(r, encoding="UTF-8", xml_declaration=True), n


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


def _borner(motif, texte):
    """Encadrer d'une frontière de mot — mais seulement là où elle a un sens.

    « \b » exige un caractère de mot d'un côté. « Nom P. » finit par un
    point : y coller « \b » rend le motif impossible à satisfaire, et le nom
    n'était remplacé qu'à moitié — « ATR A. ».
    """
    if texte[:1].isalnum() or texte[:1] == "_":
        motif = r"\b" + motif
    if texte[-1:].isalnum() or texte[-1:] == "_":
        motif = motif + r"\b"
    return motif


def _motif(texte):
    """Un motif qui retrouve `texte` quels que soient les accents, la casse
    et les espaces — le classeur n'est pas régulier là-dessus."""
    plat = _sans_accent(texte).strip()
    bouts = [re.escape(b) for b in re.split(r"\s+", plat) if b]
    if not bouts:
        return None
    return _borner(r"[\s,]*".join(bouts), plat)


PARTICULES = {"de", "van", "von", "der", "den", "le", "la", "du", "des",
              "di", "dos", "mac", "mc"}

# Les mots par lesquels un classeur nomme ses colonnes. « NOM » et « PRENOM »
# côte à côte donnent P + N + M : la ligne d'en-tête se faisait prendre pour
# quelqu'un, et le classeur archivé perdait le nom de ses propres colonnes.
ENTETES = {"nom", "noms", "prenom", "prenoms", "initiales", "matricule",
           "service", "groupe", "atelier", "equipe", "personnel", "total",
           "date", "jour", "mois", "fonction", "poste"}


def _accessoire(bout):
    """Ce qui peut entourer un nom sans en être un : une initiale, un point,
    une particule."""
    return (len(bout) <= 2 or bout in PARTICULES
            or re.fullmatch(r"[a-z]\.?(-[a-z])?\.?", bout) is not None)


NOM_POSSIBLE = re.compile(r"^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s.,'()-]*$")


def _motif_seul(mot):
    """Un nom de famille ou un prénom SEUL dans sa cellule.

    On exige la majuscule initiale, et on la protège de l'insensibilité à la
    casse : « Petit » et « PETIT » sont des noms, « petit » est un mot
    français qu'il ne faut pas remplacer au milieu d'un commentaire.
    """
    p = _sans_accent(mot)
    if len(p) < 3:
        return None
    suite = "".join("[%s%s]" % (c.upper(), c.lower()) if c.isalpha() else re.escape(c)
                    for c in p[1:])
    return _borner(r"(?-i:" + re.escape(p[0].upper()) + r")" + suite, p)


def _sonde(texte):
    """Le premier mot du texte, en minuscules : s'il n'est pas dans la partie,
    la règle ne peut pas s'y appliquer."""
    m = re.match(r"[^\W\d_]+", _sans_accent(texte), re.U)
    return m.group(0).lower() if m else ""


def _remplacer(donnee, regles, sondes):
    """Applique les règles sur le texte d'une partie XML.

    La comparaison se fait sur une copie SANS ACCENTS, et le remplacement sur
    l'original aux mêmes positions : « Prénom » et « Prenom » se valent sans
    qu'on ait à écrire les deux.

    Chaque règle porte une sonde — le premier mot du nom qu'elle cherche. On
    cherche les sondes UNE fois pour toutes, puis on saute les règles dont la
    sonde est absente. Sans cela, deux mille motifs balaient chacun les dix-
    huit méga-octets du classeur, y compris ceux qui cherchent un nom qui n'y
    est pas.
    """
    txt = donnee.decode("utf-8", "replace")
    plat = _sans_accent(txt)
    bas = plat.lower()
    presentes = set(sd for sd in sondes if sd in bas)
    coupes = []
    for motif, par, sonde in regles:
        if sonde and sonde not in presentes:
            continue
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


# --- le paquet : une copie qui s'ouvre, et qui ne dit rien de la maison -----
# Retirer les macros laissait un paquet qui les annonçait encore : le
# classeur se déclarait « à macros » et treize relations pointaient vers des
# parties absentes (les macros, les réglages d'imprimante). Excel refuse
# volontiers un tel fichier, et la copie de référence ne servait qu'à être
# relue par nos outils.
#
# Et le classeur portait, recopiés tels quels, l'étiquette de sensibilité de
# l'employeur avec l'identifiant de son annuaire (docProps/custom.xml) et le
# chemin réseau d'où il a été enregistré (x15ac:absPath). Rien de cela n'est
# un nom ; rien de cela n'a à vivre dans un dépôt public.
_MACROS = b"application/vnd.ms-excel.sheet.macroEnabled.main+xml"
_CLASSEUR = b"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"


def _paquet(nom, donnee, retires):
    if nom == "[Content_Types].xml":
        donnee = donnee.replace(_MACROS, _CLASSEUR)
        for r in retires:
            donnee = re.sub(rb'<Override PartName="/' + re.escape(r.encode()) + rb'"[^>]*/>',
                            b"", donnee)
    elif nom.endswith(".rels"):
        bases = set(os.path.basename(r).encode() for r in retires)

        def _garder(m):
            cible = re.search(rb'Target="([^"]*)"', m.group(0))
            return b"" if cible and os.path.basename(cible.group(1)) in bases else m.group(0)
        donnee = re.sub(rb"<Relationship\b[^>]*/>", _garder, donnee)
    elif nom == "xl/workbook.xml":
        donnee = re.sub(rb"<mc:AlternateContent\b(?:(?!</mc:AlternateContent>).)*?absPath"
                        rb"(?:(?!</mc:AlternateContent>).)*</mc:AlternateContent>",
                        b"", donnee, flags=re.S)
    return donnee


def anonymiser(src, dst, tolere=()):
    cl = Classeur(src)
    annuaire = _annuaire(cl)

    # Les noms connus, et le trigramme qui les remplace. L'annuaire officiel
    # d'abord.
    noms = dict(annuaire)
    connus = set(annuaire.values())
    if not noms:
        sys.exit("Aucun nom trouvé : la feuille « Personnel » a-t-elle bougé ?")

    # Les mots par lesquels on connaît déjà chaque personne. Une nouvelle
    # façon de l'écrire devra en partager un : sans cela, « PM DS-CE » donne
    # P + D + E, retombe sur le trigramme de quelqu'un, et un code de
    # délégation syndicale devient un nom.
    def _mots_de(cle):
        return set(b for b in re.split(r"[,\s]+", cle) if len(b) >= 3)

    connues = {}
    par_mot = {}

    def _retenir(cle, ini):
        connues.setdefault(ini, set()).update(_mots_de(cle))
        for b in _mots_de(cle):
            par_mot.setdefault(b, set()).add(ini)

    def _apprendre(cle, ini):
        if cle in noms:
            return
        noms[cle] = ini
        _retenir(cle, ini)

    for cle, ini in annuaire.items():
        _retenir(cle, ini)

    def _candidat(v):
        """Une cellule qui pourrait porter un nom. Un trigramme n'en est pas
        un : sans cette garde, « ATR » devient l'alias de lui-même, entre dans
        la liste surveillée, et la relecture signale comme reste chaque
        trigramme qu'on vient d'écrire."""
        t = str(v).strip()
        if not (3 <= len(t) <= 40) or not NOM_POSSIBLE.match(t):
            return None
        if sum(c.isalpha() for c in t) < 3 or _sans_accent(t).upper() in connus:
            return None
        return t

    def _ini_connues(t):
        """Le trigramme que ce texte donne, s'il en donne un de connu.

        L'ordre inversé — « Renard, Paul » pour PRD — n'est essayé que
        si le texte porte une VIRGULE. Sans cette condition, trois lettres se
        rencontrent trop facilement : « terr arr » lu à l'envers donne ATR,
        « pm ds-ce » donne PDE, et des noms d'ateliers devenaient des gens.
        La virgule est ce qui distingue « Nom, Prénom » de deux mots côte à
        côte.
        """
        ini = _initiales(t)
        if ini in connus:
            return ini
        if "," in t:
            bouts = [b for b in re.split(r"[,\s]+", t) if b]
            if len(bouts) > 1:
                ini = _initiales(" ".join(reversed(bouts)))
                if ini in connus:
                    return ini
        return None

    # On récolte d'abord les cellules qui pourraient porter un nom. Elles
    # sont peu nombreuses au regard du classeur, et les garder évite de relire
    # douze feuilles deux fois.
    recolte = {}
    for feuille in cl.feuilles:
        g = cl.grille(feuille)
        recolte[feuille] = {
            l: {c: t for c, t in ((c, _candidat(v)) for c, v in ligne.items()) if t}
            for l, ligne in g.items()}

    # LA LIGNE DES NOMS. C'est la structure même du classeur : la ligne 10 de
    # chaque feuille d'équipe porte les gens, un par colonne. Le convertisseur
    # la lit depuis toujours ; l'anonymiseur ne la lisait pas, et six personnes
    # absentes de « Personnel » comme de « Polyvalence » ont traversé l'outil
    # sans être ni remplacées ni signalées.
    #
    # Ici, pas de corroboration à chercher : ce qui est écrit là EST un nom.
    #
    # MAIS SEULEMENT DANS LES FEUILLES DE PERSONNES — celles que le
    # convertisseur lit comme telles, `FEUILLES`. La règle précédente
    # parcourait TOUTES les feuilles et se contentait de trois cellules
    # donnant des initiales. La feuille cachée « Récapitulatif (1) » porte
    # en ligne 10 l'en-tête « P. arr » trois fois : trois cellules, donc une
    # ligne de noms, et « P. arr » devint une personne, PAR. Mesuré le
    # 26/09/2026 : 480 cellules du classeur de référence — « poly. Arr. »,
    # « terr. Arr. » — et 8 commentaires y portaient « PAR ». L'horaire n'en
    # souffrait pas, le convertisseur lisant le .xlsm ; la copie de
    # référence, oui.
    #
    # Et le seuil de trois fermait la porte à la feuille Step, qui ne compte
    # que deux personnes : elles n'étaient remplacées que parce qu'on les
    # connaissait par ailleurs. Dans une feuille de personnes, la ligne 10
    # porte des gens par construction ; il n'y a rien à compter.
    for feuille, mots in recolte.items():
        if feuille not in FEUILLES:
            continue
        ligne = mots.get(LIGNE_NOMS) or {}
        trouves = [(t, _initiales(t)) for t in ligne.values()]
        trouves = [(t, i) for t, i in trouves if i and i.isalpha()]
        for t, ini in trouves:
            _apprendre(_sans_accent(t).lower(), annuaire.get(_sans_accent(t).lower(), ini))

    # Le nom et le prénom dans DEUX COLONNES — la feuille « Polyvalence » les
    # range ainsi, « NOM » d'un côté, « PRÉNOM » de l'autre. Aucun des
    # deux n'est un nom complet, donc aucun n'était remplacé.
    #
    # On ne devine pas quelles colonnes : on cherche le couple qui, sur TOUTE
    # la feuille, redonne des trigrammes connus — et dont les deux colonnes
    # portent des valeurs majoritairement DISTINCTES. « Abs » répété cent
    # fois, suivi d'un nom de famille, redonne des trigrammes connus des
    # dizaines de fois ; une colonne de prénoms, elle, ne se répète pas.
    #
    # Cette passe vient en premier : elle établit les gens, y compris ceux
    # que l'annuaire ignore, et les variantes de la passe suivante s'appuient
    # sur eux.
    for feuille, mots in recolte.items():
        scores = {}
        for m in mots.values():
            for i in m:
                for j in m:
                    if i != j and _initiales(m[i] + " " + m[j]) in connus:
                        scores[(i, j)] = scores.get((i, j), 0) + 1
        for (i, j), n in scores.items():
            paires = [m for m in mots.values() if i in m and j in m]
            if n < 10 or len(paires) < 10:
                continue
            if min(len(set(m[i] for m in paires)),
                   len(set(m[j] for m in paires))) * 2 < len(paires):
                continue
            # Le couple est établi : chaque ligne porte alors une personne,
            # même absente de l'annuaire — ses initiales tiennent lieu
            # d'identifiant, comme partout ailleurs.
            for m in paires:
                if (_sans_accent(m[i]).lower() in ENTETES
                        or _sans_accent(m[j]).lower() in ENTETES):
                    continue
                ini = _initiales(m[i] + " " + m[j])
                if ini:
                    _apprendre(_sans_accent(m[i]).lower(), ini)
                    _apprendre(_sans_accent(m[j]).lower(), ini)

    # Les variantes : « Nom P. », « J-M. Nom », « Nom
    # P.(ass.Us.) ». On ne les croit que si _initiales() y retrouve un
    # trigramme connu ET si elles partagent un mot avec une façon déjà connue
    # d'écrire cette personne-là. Trois lettres se rencontrent par hasard ; un
    # nom de famille en commun, non.
    for feuille, mots in recolte.items():
        for m in mots.values():
            for t in m.values():
                # « Nom P.(ass.Us.) » : on n'enregistre que le nom, pour
                # que la parenthèse — qui dit le rôle, pas la personne —
                # reste dans le classeur.
                t = " ".join(re.sub(r"\([^)]*\)", " ", t).split()) or t
                cle = _sans_accent(t).lower()
                if cle in noms:
                    continue
                # Un mot qui ne désigne qu'une personne tranche à lui seul :
                # « de Nomlong P. » porte « nomlong », et c'est assez.
                # Ses initiales, elles, donnent autre chose — la particule
                # « de » les déplace — et la corroboration échouait.
                #
                # Encore faut-il que la cellule ait la forme d'un nom : tous
                # ses morceaux doivent être un mot de nom connu, une
                # particule, ou une initiale. Sans quoi « Conti de la ligne »
                # deviendrait le trigramme tout entier, au lieu de garder ce
                # qui n'est pas le nom.
                bouts = [b for b in re.split(r"[,\s]+", cle) if b]
                vises = set()
                for b in bouts:
                    vises |= par_mot.get(b, set())
                if (vises and len(bouts) <= 4
                        and all(b in par_mot or _accessoire(b) for b in bouts)):
                    if len(vises) == 1:
                        _apprendre(cle, next(iter(vises)))
                        continue
                ini = _ini_connues(t)
                if ini and (_mots_de(cle) & connues.get(ini, set())):
                    _apprendre(cle, ini)

    # LES AUTEURS DE COMMENTAIRES SONT DES NOMS, au même titre que la ligne
    # des noms — et pas seulement quelque chose à effacer. Découvert le
    # 22/09/2026 sur un nouveau classeur : quelqu'un signait des centaines de
    # commentaires. Son NOM DE FAMILLE était connu par la feuille
    # « Polyvalence » et remplacé partout ; son PRÉNOM ne l'était par rien.
    #
    # Les signatures de tête ont bien été retirées, la liste des auteurs
    # vidée — mais trois commentaires portaient DEUX signatures, la seconde au
    # milieu du texte, et « _sans_signature » ne retire que la tête. Ces
    # secondes signatures ne disparaissaient que si le nom y était RECONNU.
    # Celle-là ne l'était pas : ni remplacée, ni même SURVEILLÉE, elle a
    # traversé la garantie, qui a répondu « aucun nom ne subsiste » en toute
    # bonne foi. C'est la faille de naissance que CLAUDE.md décrit — l'outil
    # ne cherche que ce qu'il a su apprendre.
    #
    # Ici, comme pour la ligne des noms, PAS DE CORROBORATION À CHERCHER : ce
    # qu'Excel écrit dans <author> EST le nom d'une personne. On exige
    # seulement deux morceaux — « Nom, Prénom » en donne toujours deux — pour
    # écarter le « Auteur » que cet outil écrit lui-même et les trigrammes
    # qu'un classeur y dépose parfois.
    zc = zipfile.ZipFile(src)
    auteurs = set()
    for info in zc.infolist():
        if COMMENTAIRES.search(info.filename):
            texte = zc.read(info.filename).decode("utf-8", "replace")
            for m in re.finditer(r"<author>([^<]*)</author>", texte):
                brut = (m.group(1).replace("&amp;", "&").replace("&lt;", "<")
                        .replace("&gt;", ">").replace("&quot;", '"')
                        .replace("&apos;", "'"))
                t = _candidat(brut)
                if t:
                    auteurs.add(t)
    zc.close()

    # Un nom qu'on n'a pas su attribuer ne doit pas pour autant sortir en
    # silence : ses mots vont sous surveillance, la garantie détruit la
    # sortie et le dit. Mieux vaut un outil qui s'arrête qu'un outil qui
    # laisse passer.
    orphelins = []
    mintes = set()
    for t in sorted(auteurs):
        # « Nom, Prénom (external) » : la parenthèse dit le rôle, pas
        # la personne — on ne retient que le nom.
        t = " ".join(re.sub(r"\([^)]*\)", " ", t).split()) or t
        cle = _sans_accent(t).lower()
        bouts = [b for b in re.split(r"[,\s]+", cle) if b]
        if not (2 <= len(bouts) <= 4) or any(b in ENTETES for b in bouts):
            continue
        vises = set()
        for b in bouts:
            vises |= par_mot.get(b, set())
        ini = next(iter(vises)) if len(vises) == 1 else None
        if ini is None:
            ini = _ini_connues(t)
        if ini is None:
            # Personne de connu — deux homonymes, ou quelqu'un qui n'est dans
            # aucune feuille. Ses initiales tiennent lieu d'identifiant,
            # comme pour les gens de la ligne des noms que l'annuaire ignore.
            # On refuse seulement de lui donner un code DÉJÀ pris : ce serait
            # troquer une fuite contre une fausse attribution.
            cand = _initiales(t)
            if cand and cand.isalpha() and cand not in connus and cand not in mintes:
                ini = cand
                mintes.add(cand)
            else:
                orphelins.extend((b, "?") for b in bouts if len(b) >= 3)
                continue
        _apprendre(cle, ini)
        for b in bouts:
            if len(b) >= 3 and b not in PARTICULES and b not in ENTETES:
                _apprendre(b, ini)

    pesees, surveille = [], []
    for cle, ini in noms.items():
        bouts = [b for b in re.split(r"[,\s]+", cle) if b]
        if len(bouts) > 1:
            for forme in _formes(cle):
                m = _motif(forme)
                if m:
                    pesees.append((len(forme), m, ini, _sonde(forme)))
        else:
            m = _motif_seul(cle)
            if m:
                pesees.append((len(cle), m, ini, _sonde(cle)))
        for bout in bouts:
            if len(bout) >= 3:
                surveille.append((bout, ini))
    surveille.extend(orphelins)
    # Les règles qui attrapent le plus long d'abord : « Renard P. » avant
    # « Renard », sans quoi il resterait « PRD P. ». On pèse ce que la règle
    # ATTRAPE et non la longueur du motif : « [Tt][Rr][Ee]… » est un long
    # motif pour un petit mot, et il passerait devant.
    pesees.sort(key=lambda r: -r[0])
    regles = [(m, ini, sd) for _, m, ini, sd in pesees]
    # LE BLANC QUI PRÉCÈDE UNE SIGNATURE RESTE. AUTEUR commence par
    # « (?:^|\s) » et, remplacé par une chaîne vide, emportait le saut de
    # ligne qui séparait deux notes : « remplace ATA\nNom, Prénom:
    # remplace GPS » devenait « remplace ATAremplace GPS ». Mesuré le
    # 26/09/2026 : environ 350 commentaires collés ainsi, et le trigramme
    # n'était plus un mot — « \bATA\b » ne le retrouvait plus. Le blanc
    # devient un regard en arrière : il borne la signature sans en faire
    # partie.
    regles.append((AUTEUR.pattern.replace(r"(?:^|\s)", r"(?:^|(?<=\s))", 1), "", ""))
    sondes = sorted(set(sd for _, _, sd in regles if sd))

    # On écrit À CÔTÉ. Tant que la garantie n'est pas franchie, le fichier
    # peut porter des noms : il n'a rien à faire à sa destination, où un
    # commit distrait l'emporterait. Il n'y prend sa place qu'à la fin.
    encours = dst + ".en-cours"
    total, parties, logins = 0, 0, 0
    zin = zipfile.ZipFile(src)
    retires = [i.filename for i in zin.infolist() if EXCLUS.search(i.filename)]
    with zipfile.ZipFile(encours, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            if EXCLUS.search(info.filename):
                print("  écarté :", info.filename, file=sys.stderr)
                continue
            donnee = zin.read(info.filename)
            if TEXTE.search(info.filename):
                # LA SIGNATURE D'ABORD, LE REMPLACEMENT ENSUITE. L'ordre
                # inverse a vécu une demi-heure le 22/09/2026 : depuis que
                # les auteurs sont APPRIS, leur nom est remplacé par son
                # trigramme, et « Nom, Prénom (external): » devenait
                # « PNO (external): » — que « _est_nom » ne reconnaît plus.
                # 2311 têtes de commentaire restaient en place.
                #
                # Y ajouter un motif « trigramme seul » aurait été pire : il
                # aurait avalé le corps des commentaires qui COMMENCENT par
                # un code, « MPE : Maintien prime PM » en tête. Les motifs de
                # signature sont écrits pour des noms ; on les laisse donc
                # voir des noms.
                n = 0
                if COMMENTAIRES.search(info.filename):
                    donnee, n = _sans_signature(donnee)
                donnee, m = _remplacer(donnee, regles, sondes)
                n += m
                if COMMENTAIRES.search(info.filename):
                    donnee, m = _sans_login(donnee)
                    n += m
                    logins += m
                if info.filename.startswith("docProps/"):
                    donnee = re.sub(rb"<(dc:creator|cp:lastModifiedBy)>[^<]*</\1>",
                                    rb"<\1></\1>", donnee)
                donnee = _paquet(info.filename, donnee, retires)
                total += n
                parties += 1 if n else 0
            # On reprend la date du classeur source. Sans elle, le ZIP
            # s'horodate à l'instant présent : deux conversions du même
            # fichier donneraient deux sorties différentes, et git verrait
            # 1,5 Mo de changement là où rien n'a bougé.
            sortie = zipfile.ZipInfo(info.filename, info.date_time)
            sortie.compress_type = zipfile.ZIP_DEFLATED
            sortie.external_attr = info.external_attr
            sortie.create_system = info.create_system
            zout.writestr(sortie, donnee)
    zin.close()

    # --- la garantie : relire, et chercher ce qu'on vient de remplacer -----
    restes = []
    zv = zipfile.ZipFile(encours)
    for info in zv.infolist():
        if not TEXTE.search(info.filename):
            continue
        plat = _sans_accent(zv.read(info.filename).decode("utf-8", "replace"))
        bas = plat.lower()
        for bout, ini in surveille:
            if bout in tolere or bout not in bas:
                continue
            for m in re.finditer(r"\b" + re.escape(bout) + r"\b", plat, re.I):
                # un mot courant écrit en minuscules n'est pas un nom
                brut = plat[m.start():m.end()]
                if brut[:1].islower():
                    continue
                ctx = plat[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")
                restes.append((info.filename, ini, brut, ctx))
    zv.close()
    if restes:
        os.remove(encours)
        print("\n%d reste(s) de nom dans la sortie — fichier détruit :" % len(restes),
              file=sys.stderr)
        for f, ini, brut, ctx in restes[:20]:
            print("   %-22s %-14s (%s)  …%s…" % (f, brut, ini, ctx), file=sys.stderr)
        print("\nSi l'un d'eux n'est pas un nom — « Paye » peut être un mot —"
              " relancer avec --tolerer mot1,mot2 APRÈS l'avoir lu.", file=sys.stderr)
        sys.exit(2)

    os.replace(encours, dst)
    taille = os.path.getsize(dst)
    print("%d nom(s) connu(s) · %d remplacement(s) dans %d partie(s) · %.1f Mo"
          % (len(noms), total, parties, taille / 1048576.0), file=sys.stderr)
    print("%d identifiant(s) de connexion retiré(s) des commentaires" % logins,
          file=sys.stderr)
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
