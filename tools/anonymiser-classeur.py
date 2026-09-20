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
        """Le trigramme que ce texte donne, s'il en donne un de connu. On
        essaie les deux ordres : le classeur écrit « Nom A. » ici et
        « Nom, Prénom » là."""
        ini = _initiales(t)
        if ini in connus:
            return ini
        bouts = [b for b in re.split(r"[,\s]+", t) if b]
        if len(bouts) > 1:
            ini = _initiales(" ".join(reversed(bouts)))
            if ini in connus:
                return ini
        return None

    for feuille in cl.feuilles:
        g = cl.grille(feuille)

        # Le classeur écrit les gens de bien plus de façons que la feuille
        # « Personnel » n'en connaît : « Nom A. », « P-Y. Nom »,
        # « Nom F.(ass.Us.) ». On les récolte — mais on ne les croit que si
        # _initiales() y retrouve un trigramme connu. Un alias qui ne se
        # recoupe pas n'est pas un nom, et « Step » ne devient pas quelqu'un.
        for ligne in g.values():
            for v in ligne.values():
                t = _candidat(v)
                if not t:
                    continue
                # « Nom F.(ass.Us.) » : on n'enregistre que le nom, pour
                # que la parenthèse — qui dit le rôle, pas la personne —
                # reste dans le classeur.
                t = " ".join(re.sub(r"\([^)]*\)", " ", t).split()) or t
                cle = _sans_accent(t).lower()
                if cle not in noms:
                    ini = _ini_connues(t)
                    if ini:
                        noms[cle] = ini

        # Le nom et le prénom dans DEUX COLONNES — la feuille « Polyvalence »
        # les range ainsi, « NOM » d'un côté, « PRÉNOM » de l'autre.
        # Aucun des deux n'est un nom complet, donc aucun n'était remplacé.
        #
        # On ne devine pas quelles colonnes : on cherche le couple qui, sur
        # TOUTE la feuille, redonne des trigrammes connus. Trois lettres se
        # rencontrent par hasard — « Polyvalence Nom » donne PDE et faisait
        # du nom de la feuille l'alias de quelqu'un. Un couple qui ne tombe
        # juste qu'une fois est un hasard ; celui qui tombe juste cinquante
        # fois est la structure de la feuille.
        mots = {l: {c: t for c, t in ((c, _candidat(v)) for c, v in ligne.items()) if t}
                for l, ligne in g.items()}
        scores = {}
        for m in mots.values():
            for i in m:
                for j in m:
                    if i != j and _initiales(m[i] + " " + m[j]) in connus:
                        scores[(i, j)] = scores.get((i, j), 0) + 1
        for (i, j), n in scores.items():
            if n < 10:
                continue
            # Le couple est établi : chaque ligne porte alors une personne,
            # même absente de l'annuaire — ses initiales tiennent lieu
            # d'identifiant, comme partout ailleurs.
            for m in mots.values():
                if i in m and j in m:
                    ini = _initiales(m[i] + " " + m[j])
                    if ini:
                        noms.setdefault(_sans_accent(m[i]).lower(), ini)
                        noms.setdefault(_sans_accent(m[j]).lower(), ini)

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
