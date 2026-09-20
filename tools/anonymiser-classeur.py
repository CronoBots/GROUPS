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


def _borner(motif, texte):
    """Encadrer d'une frontière de mot — mais seulement là où elle a un sens.

    « \b » exige un caractère de mot d'un côté. « Nom A. » finit par un
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

        L'ordre inversé — « Nom, Prénom » pour GBT — n'est essayé que
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
                ini = _initiales(m[i] + " " + m[j])
                if ini:
                    _apprendre(_sans_accent(m[i]).lower(), ini)
                    _apprendre(_sans_accent(m[j]).lower(), ini)

    # Les variantes : « Nom A. », « P-Y. Nom », « Nom
    # F.(ass.Us.) ». On ne les croit que si _initiales() y retrouve un
    # trigramme connu ET si elles partagent un mot avec une façon déjà connue
    # d'écrire cette personne-là. Trois lettres se rencontrent par hasard ; un
    # nom de famille en commun, non.
    for feuille, mots in recolte.items():
        for m in mots.values():
            for t in m.values():
                # « Nom F.(ass.Us.) » : on n'enregistre que le nom, pour
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

    pesees, surveille = [], []
    for cle, ini in noms.items():
        bouts = [b for b in re.split(r"[,\s]+", cle) if b]
        if len(bouts) > 1:
            for forme in _formes(cle):
                m = _motif(forme)
                if m:
                    pesees.append((len(forme), m, ini))
        else:
            m = _motif_seul(cle)
            if m:
                pesees.append((len(cle), m, ini))
        for bout in bouts:
            if len(bout) >= 3:
                surveille.append((bout, ini))
    # Les règles qui attrapent le plus long d'abord : « Nom A. » avant
    # « Nom », sans quoi il resterait « ATR A. ». On pèse ce que la règle
    # ATTRAPE et non la longueur du motif : « [Tt][Rr][Ee]… » est un long
    # motif pour un petit mot, et il passerait devant.
    pesees.sort(key=lambda r: -r[0])
    regles = [(m, ini) for _, m, ini in pesees]
    regles.append((AUTEUR.pattern, ""))

    # On écrit À CÔTÉ. Tant que la garantie n'est pas franchie, le fichier
    # peut porter des noms : il n'a rien à faire à sa destination, où un
    # commit distrait l'emporterait. Il n'y prend sa place qu'à la fin.
    encours = dst + ".en-cours"
    total, parties = 0, 0
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(encours, "w", zipfile.ZIP_DEFLATED) as zout:
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
    zv = zipfile.ZipFile(encours)
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
