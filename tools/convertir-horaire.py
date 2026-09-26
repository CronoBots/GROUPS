#!/usr/bin/env python3
"""Convertit le récapitulatif horaire Excel en data/horaire-<année>.json.

    python3 tools/convertir-horaire.py Recapitulatif.xlsm \
            data/horaire-2026.json 2026 data/horaire-2025.json

Le dernier argument, facultatif, est une conversion précédente : elle sert à
retrouver les identifiants anonymisés en appariant les lignes sur leurs
journées, pour qu'ils restent stables d'une année sur l'autre.

Le convertisseur reste FIDÈLE : il recopie la cellule, la colonne d'annotation
et le commentaire sans les interpréter. Toute la lecture est faite par
l'application (voir docs/conversion-horaire.md) — ainsi une règle qui change
ne demande pas de reconvertir.

Deux règles de confidentialité, non négociables :
  - aucun nom complet ne sort d'ici ; les personnes sont désignées par leur
    identifiant à trois lettres ;
  - les commentaires Excel portent le nom de leur auteur en préfixe, retiré
    ici, y compris au milieu d'un fil de discussion.
"""
import datetime, difflib, hashlib, json, re, sys, unicodedata, zipfile
import xml.etree.ElementTree as ET

M = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

# Une feuille par groupe, et la catégorie sous laquelle ses gens apparaissent.
#
# L'ORDRE COMPTE. Une même personne figure sur plusieurs feuilles : les
# adjoints contremaître sont recopiés sur les cinq feuilles d'équipe, à
# l'identique — 365 journées, aucune divergence. C'est la feuille de son
# propre groupe qui donne sa catégorie, pas celle où il est recopié pour
# référence ; les feuilles spécialisées passent donc avant les équipes.
FEUILLES = {
    "Contremaître": "Contremaîtres de production",
    "Step": "Opérateurs STEP",
    "Opérateurs": "Opérateurs en formation",
    "Shift1": "Shift 1", "Shift2": "Shift 2", "Shift3": "Shift 3",
    "Shift4": "Shift 4", "Shift5": "Shift 5",
}
LIGNE_NOMS = 10          # la ligne qui porte les noms
LIGNE_POSTE = 9          # juste au-dessus : le poste tenu (section 9 bis)

# Une feuille dont le NOM porte le poste : la ligne 9 y est vide parce
# qu'il n'y a rien à préciser — tout le monde y tient le même poste.
# Établi avec le client le 20/09/2026.
POSTE_DE_LA_FEUILLE = {"Step": "Station d'épuration"}


def _lettre(n):
    """Le nom de colonne d'Excel. « Polyvalent » seul est ambigu : en O
    c'est le polyvalent ARRIÈRE, après V c'est un polyvalent AVANT, et
    les deux ne tiennent pas les mêmes postes. Sans la colonne, on ne
    peut pas les distinguer."""
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s
COL_JOUR = 2             # la colonne qui porte le numéro du jour
MOIS = ["JANVIER", "FEVRIER", "MARS", "AVRIL", "MAI", "JUIN", "JUILLET",
        "AOUT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DECEMBRE"]

# « Nom, Prénom: », « Nom, Prénom (external): », « RT0xxxx: »
AUTEUR = re.compile(r"(?:^|\s)(?:[A-ZÉÈÀ][\wÉÈÀéèàêç'-]+,\s*[A-ZÉÈÀ][\wÉÈÀéèàêç'-]+"
                    r"(?:\s*\([^)]*\))?|[Rr][Tt]\d{4,6}|Auteur)\s*:\s*")

# LES NOMS QUE LE CLASSEUR DÉCLARE LUI-MÊME. AUTEUR exige une virgule, et
# trois formes lui ont échappé sur le classeur du 22/09/2026 :
# « Nom Prénom : » sans virgule, « Nom, Prénom/rt0xxxx: » dont le
# suffixe rompt l'ancrage, et « Prénom: » — un prénom seul, qui n'a aucune
# forme reconnaissable. Elles seraient parties dans data/horaire-2026.json,
# qui vit dans un dépôt PUBLIC.
#
# On ne devine donc plus la forme d'un nom : on prend ceux qu'Excel écrit
# dans <authors>, qui sont les gens ayant posé ces commentaires-là. Rien à
# inférer, rien à rater.
#
# La majuscule initiale est exigée et protégée de l'insensibilité à la casse,
# comme l'anonymiseur le fait de son côté : « Marie » est un nom, « marie »
# est un verbe français.
_AUTEUR_MOTS_IGNORES = {"auteur", "external", "ext", "interne", "externe"}


def _motif_auteurs(racine):
    """Le motif qui retrouve les noms déclarés comme auteurs des commentaires
    de CE fichier — nom complet ou mot isolé, où qu'il apparaisse."""
    mots = set()
    bloc = racine.find("{%s}authors" % M)
    for x in (list(bloc) if bloc is not None else []):
        t = re.sub(r"\([^)]*\)", " ", (x.text or ""))
        for b in re.split(r"[,\s/]+", t):
            b = b.strip(".").strip()
            if (len(b) >= 3 and not b.isdigit()
                    and b.lower() not in _AUTEUR_MOTS_IGNORES):
                mots.add(b)
    if not mots:
        return None
    def _alt(m):
        return (re.escape(m[0].upper())
                + "".join("[%s%s]" % (c.upper(), c.lower()) if c.isalpha()
                          else re.escape(c) for c in m[1:]))
    # Le plus long d'abord : « Jean-Pierre » avant « Jean ».
    alt = "|".join(_alt(m) for m in sorted(mots, key=len, reverse=True))
    return re.compile(r"\b(?:" + alt + r")\b")

# L'onglet « Config » du classeur le dit lui-même : « les lignes de 11 à 376
# sont consacrées à l'horaire, les lignes de 377 à 420 aux compteurs ». En
# pratique le bloc court jusqu'à 434, la position du bloc CP variant d'une
# personne à l'autre.
#
# Le pied de feuille se lit comme les journées : le libellé dans la colonne
# de la personne, la valeur dans la colonne d'annotation. Les titres de
# section sont écrits à gauche, dans les deux premières colonnes, mais AU
# MILIEU de leur bloc et non en tête — d'où des bornes explicites, que l'on
# vérifie en cherchant le titre attendu à l'intérieur.
BLOCS = [
    ("prevision", 377, 394, "prévisions"),
    ("solde", 395, 402, "soldes en heures au"),
    ("restant", 403, 408, "compte tenu des prévisions"),
    ("flex", 409, 430, "compteur flex time"),
    ("conges", 431, 440, None),
]

# Le libellé « Total: » du bloc flex time est le report de l'année
# précédente. Le client : « les compteurs totaux sont repartis d'où ils
# étaient en fin d'année 2025, donc des valeurs manuelles avaient été
# rentrées en début d'année. » Ce n'est donc pas la somme des colonnes +FT
# et -FT de l'année en cours, et le nommer « Total » induirait en erreur.
RENOMME = {"Total": "report"}

# Trigrammes corrigés à la demande du client, quand la règle des initiales
# tombe sur un trigramme déjà pris ou attribué à quelqu'un d'autre.
#
# La clé est l'empreinte du nom normalisé, pas le nom : elle vise une
# personne précise sans que le dépôt porte son identité. Elle ne protège que
# de la lecture — qui a le classeur a les noms — mais elle suffit à tenir la
# règle « aucun nom complet dans le dépôt ».
#
# Une correction prime sur l'onglet Personnel comme sur la règle des
# initiales : c'est une décision, pas une déduction. Si son empreinte ne
# correspond plus à personne, le convertisseur le signale — le nom a changé
# d'orthographe dans le classeur, et la correction ne s'applique plus.
CORRECTIONS = {
    # opérateur gluten arrivé en septembre ; NPE revient à l'opérateur de
    # Shift 2, qui le porte depuis le début de l'année
    "548e47d27c": "NPI",
    # JBY est le trigramme d'un responsable, pas celui de cet opérateur
    "db4592e0af": "JBA",
    # trois trigrammes pour deux personnes : le client tranche, celui de
    # l'équipe 5 garde CDE, celui de l'équipe 3 garde PDR
    "a056b3f782": "CHD",   # l'autre CDE, en équipe 4
    "0ad0bc1dfe": "PDF",   # l'autre PDR, en équipe 1
    # La même personne, écrite au long dans l'onglet Polyvalence et en
    # court dans l'horaire : ni son trigramme ni son nom ne concordent
    # d'une feuille à l'autre. Le client : « il faut prendre leur
    # polyvalence sur leur vrai trigramme SAUF pour celui qui a un nom
    # compliqué et qui devient PDF ». C'est ce « sauf » — sans cette
    # ligne, sa polyvalence (chaudières et STEP) ne lui revient pas.
    "6699f9fcb4": "PDF",
    # GBT n'est plus corrigé. Le client, le 21/09/2026 : « il faut annuler
    # ma demande de renommage de GBO, il doit y avoir 2 GBT (un aux
    # chaudières et l'autre au Gluten/Meunerie) ». Ce sont deux personnes
    # qui portent réellement les mêmes initiales, et le suffixe des
    # trigrammes partagés — GBT et GBT-1 — est fait pour ce cas-là.
    # CDE figure aussi dans l'onglet Personnel sous un troisième nom ; le
    # client confirme qu'il revient à celui de l'équipe 5. L'inscrire ici
    # fait de ce maintien une décision, et non le hasard d'un calcul.
    "e829c2c542": "CDE",
}


# Les corrections qu'a employées l'onglet Polyvalence : sans elles, une
# correction qui n'y sert qu'à cet onglet se signalerait comme « inutilisée ».
_corrections_polyvalence = set()


def _cle_nom(t):
    """Pour reconnaître un même nom d'un onglet à l'autre.

    L'horaire écrit « Nom P », l'onglet Polyvalence reconstruit
    « Nom P. » depuis ses colonnes nom et prénom : un point d'écart, et
    les deux personnes qui partagent le trigramme GBT ne se départageaient
    plus. On compare donc les lettres, et rien d'autre.

    Cette clé ne sert QU'À COMPARER. La clé des fiches, elle, ne bouge pas :
    les empreintes de CORRECTIONS sont calculées dessus, et les changer les
    invaliderait toutes.
    """
    return re.sub(r"[^a-z0-9]+", "", _sans_accent(t).lower())


def _empreinte(cle):
    return hashlib.sha1(cle.encode("utf-8")).hexdigest()[:10]


# Le compteur s'écrit dans la colonne d'annotation, le poste dans celle de
# la personne. Les deux inversés, le classeur ne voit plus le compteur : ses
# totaux comptent la colonne d'annotation, et rien d'autre.
COMPTEUR = re.compile(r"^\d+(?:[.,]\d+)?\s*h?\s*[-+]\s*FT$"
                      r"|^\d+(?:[.,]\d+)?\s*h\s*(?:RTT|RHS|DTT|RJF)$", re.I)
POSTE = re.compile(r"^(?:AM|PM|N|D|-|poly|meun|gluten|ferm|disti|chaudi|terr|step|etoh)",
                   re.I)


def colonnes_inversees(jours):
    """Une seule dans le classeur 2026 : FPA le 07/11, « 3h -FT » écrit dans
    la colonne du poste et « poly-arr » dans celle de l'annotation. Son
    compteur flex time en perd trois heures — 44 h reprises, 41 comptées."""
    return [k for k, e in sorted(jours.items())
            if COMPTEUR.match((e[0] or "").strip())
            and len(e) > 1 and POSTE.match((e[1] or "").strip())]


def _colnum(lettres):
    n = 0
    for c in lettres:
        n = n * 26 + ord(c) - 64
    return n


class Classeur:
    def __init__(self, chemin):
        self.z = zipfile.ZipFile(chemin)
        self.shared = self._shared()
        wb = ET.fromstring(self.z.read("xl/workbook.xml"))
        rels = {r.get('Id'): r.get('Target')
                for r in ET.fromstring(self.z.read("xl/_rels/workbook.xml.rels"))}
        self.feuilles = {}
        for s in wb.find('{%s}sheets' % M):
            cible = rels[s.get('{%s}id' % R)].lstrip('/')
            self.feuilles[s.get('name')] = cible if cible.startswith('xl/') else 'xl/' + cible
        # Le registre des noms relit toutes les feuilles avant la conversion :
        # sans ce cache, chaque feuille serait analysée deux fois.
        self._grilles = {}
        # Les noms des personnes, appris de la ligne des noms. Posé par
        # convertir() AVANT la première lecture de commentaire.
        self.registre = None

    def _shared(self):
        if "xl/sharedStrings.xml" not in self.z.namelist():
            return []
        return ["".join(t.text or "" for t in si.iter('{%s}t' % M))
                for si in ET.fromstring(self.z.read("xl/sharedStrings.xml"))]

    def _fusions(self, racine, out, lignes):
        """Recopier la valeur d'une cellule fusionnée sur toute son étendue.

        Dans un classeur, seule la case en HAUT À GAUCHE d'une fusion porte la
        valeur ; les autres sont vides. Le poste « Chaudières » couvre ainsi
        trois colonnes d'un seul tenant, et deux opérateurs par équipe
        paraissaient n'avoir rien au-dessus d'eux.

        On ne remplit que les cases vides : une fusion ne peut rien écraser.
        Et seulement les LIGNES DEMANDÉES. Déplier partout serait un désastre
        discret : la ligne des noms est fusionnée elle aussi, si bien que
        chaque personne apparaîtrait sur ses deux colonnes et serait lue deux
        fois — 27 683 journées au lieu de 27 462, sans que rien ne le dise.
        """
        for m in racine.iter('{%s}mergeCell' % M):
            ref = m.get('ref') or ""
            if ":" not in ref:
                continue
            bouts = []
            for coin in ref.split(":"):
                mm = re.match(r'([A-Z]+)(\d+)$', coin.strip())
                if not mm:
                    break
                bouts.append((int(mm.group(2)), _colnum(mm.group(1))))
            if len(bouts) != 2:
                continue
            (l1, c1), (l2, c2) = bouts
            if not any(l in lignes for l in range(min(l1, l2), max(l1, l2) + 1)):
                continue
            val = out.get(l1, {}).get(c1)
            if val in (None, ""):
                continue
            for l in range(min(l1, l2), max(l1, l2) + 1):
                if l not in lignes:
                    continue
                for c in range(min(c1, c2), max(c1, c2) + 1):
                    if out.setdefault(l, {}).get(c) in (None, ""):
                        out[l][c] = val

    def grille(self, feuille, fusions=(LIGNE_POSTE,)):
        """{ligne: {colonne: texte}}"""
        out = {}
        if feuille in self._grilles:
            return self._grilles[feuille]
        racine = ET.fromstring(self.z.read(self.feuilles[feuille]))
        for c in racine.iter('{%s}c' % M):
            ref, t = c.get('r'), c.get('t')
            inline, v = c.find('{%s}is' % M), c.find('{%s}v' % M)
            if inline is not None:
                val = "".join(x.text or "" for x in inline.iter('{%s}t' % M))
            elif v is None:
                continue
            elif t == 's':
                val = self.shared[int(v.text)]
            else:
                val = v.text
            val = (val or "").strip()
            if not val:
                continue
            lettres = re.match(r'([A-Z]+)', ref).group(1)
            out.setdefault(int(re.search(r'(\d+)', ref).group(1)), {})[_colnum(lettres)] = val
        self._fusions(racine, out, set(fusions))
        self._grilles[feuille] = out
        return out

    def commentaires(self, feuille):
        """{(ligne, colonne): texte anonymisé}"""
        p = self.feuilles[feuille]
        rp = p.replace("xl/worksheets/", "xl/worksheets/_rels/") + ".rels"
        if rp not in self.z.namelist():
            return {}
        out = {}
        for r in ET.fromstring(self.z.read(rp)):
            cible = r.get('Target')
            if 'comments' not in cible:
                continue
            chemin = ("xl/" + cible.replace("../", "")).replace("xl/xl/", "xl/")
            if chemin not in self.z.namelist():
                continue
            racine = ET.fromstring(self.z.read(chemin))
            auteurs = _motif_auteurs(racine)
            for cm in racine.iter('{%s}comment' % M):
                txt = " ".join("".join(t.text or "" for t in cm.iter('{%s}t' % M)).split())
                # Les noms déclarés d'abord : ce qui reste — « , » esseulée,
                # « /rt0xxxx: », « : » en tête — est balayé par AUTEUR et par
                # le strip qui suit.
                if auteurs:
                    # UNE TÊTE QUI NOMME UN AUTEUR CONNU EST UNE SIGNATURE,
                    # ET ELLE PART EN ENTIER.
                    #
                    # Retirer les MOTS déclarés ne suffit pas : le 23/09/2026,
                    # un auteur avait signé son propre nom avec une faute de
                    # frappe — un « e » final manquant au prénom. Le nom de
                    # famille, lui, correspondait. Le motif a donc emporté la
                    # moitié qu'il reconnaissait et laissé l'autre, et une
                    # MOITIÉ DE NOM NOMME ENCORE LA PERSONNE. Le prénom
                    # tronqué est arrivé jusqu'au JSON d'un dépôt PUBLIC ;
                    # c'est tools/verifier-depot.py qui l'a arrêté, pas ce
                    # fichier.
                    #
                    # On ne peut pas deviner les fautes de frappe. On peut
                    # lire la STRUCTURE : ce qui précède le premier
                    # deux-points, quand c'est court ET que cela nomme un
                    # auteur déclaré, est une signature quoi qu'il y soit
                    # écrit. Le reste du commentaire n'est pas touché.
                    #
                    # La borne de longueur n'est pas décorative : sans elle,
                    # un commentaire citant un auteur au fil du texte verrait
                    # tout son début avalé jusqu'au premier deux-points.
                    tete = re.match(r"^([^:]{0,48}):", txt)
                    if tete and auteurs.search(tete.group(1)):
                        txt = txt[tete.end():]
                    txt = auteurs.sub(" ", txt)
                    # Le nom parti, son ornement reste : « (external): ».
                    # Il ne nomme personne, mais il ouvre le commentaire par
                    # un reste de signature que rien ne lit.
                    txt = re.sub(r"\(\s*[^)]*\)\s*:\s*", " ", txt)
                # LE REGISTRE DES TRIGRAMMES PASSE APRÈS LES AUTEURS. Un collègue
                # nommé au fil d'un commentaire — « changement d'équipe de
                # <nom> » — n'est déclaré auteur de rien : seule la ligne des
                # noms le connaît. Son nom part remplacé par son trigramme,
                # et non effacé : « changement d'équipe de MMS » se lit
                # encore, « changement d'équipe de » ne dit plus rien.
                txt = _sans_registre(txt, self.registre)
                txt = AUTEUR.sub(" ", txt).strip(" .;:")
                txt = re.sub(r"^[\s,;:/]+", "", " ".join(txt.split()))
                # APRÈS LES SIGNATURES, ET NON AVANT. Un login est le suffixe
                # ordinaire d'une signature — « Nom, Prénom/rt0xxxx: » — et le
                # remplacer d'abord le rend méconnaissable à AUTEUR, qui
                # laisse alors la tête en place : 324 commentaires ont porté
                # « (identifiant retiré): » pendant une version. C'est le
                # piège que CLAUDE.md décrit pour l'anonymiseur, mot pour mot.
                # Ce qui survit ICI est un login au FIL du texte, et lui seul.
                txt = LOGIN.sub("(identifiant retiré)", txt)
                txt = " ".join(txt.split())
                if not txt:
                    continue
                ref = cm.get('ref')
                lettres = re.match(r'([A-Z]+)', ref).group(1)
                out[(int(re.search(r'(\d+)', ref).group(1)), _colnum(lettres))] = txt
        return out


# UN IDENTIFIANT DE CONNEXION N'EST PAS UN NOM, ET IL DÉSIGNE QUAND MÊME
# QUELQU'UN. « RT0xxxx » vivait dans data/horaire-2026.json — dépôt PUBLIC —
# depuis que les commentaires d'annotation sont lus : il n'y ouvrait pas de
# signature, donc rien ne l'emportait. Le convertisseur en retirait un, le
# 23/09, mais seulement parce qu'il était en TÊTE ; au fil du texte, il
# restait.
#
# C'est l'export intégral qui l'a montré : le même login survivait dans six
# commentaires du classeur, et la confrontation des deux fichiers l'a mis
# côte à côte avec sa version d'horaire. Ni l'anonymiseur ni son second
# contrôle ne pouvaient le voir — ils cherchent des NOMS, et ce n'en est pas
# un.
#
# Dans un dépôt public, un login d'entreprise se recoupe avec les annuaires
# de la maison aussi sûrement qu'un nom. Il part donc, remplacé et non
# effacé. Le motif est étroit à dessein — deux lettres, quatre à six
# chiffres, d'un seul tenant — et mesuré : UN seul jeton de cette forme dans
# tout le classeur, six occurrences.
LOGIN = re.compile(r"\b[A-Za-z]{2}\d{4,6}\b")


def _les_deux(cellule, annotation):
    """Les DEUX commentaires d'une journée, et non l'un OU l'autre.

    Chaque personne occupe deux colonnes — la cellule et son annotation — et
    CHACUNE peut porter son propre commentaire Excel. Le convertisseur
    écrivait `cm.get(cellule) or cm.get(annotation)` : dès que la première
    en avait un, la seconde était jetée sans un mot.

    Mesuré sur le classeur du 23/09/2026 : **684 journées portent deux
    commentaires différents**, et 496 d'entre elles n'en gardaient qu'un.
    Ce qui se perdait n'était pas du décor — « remplace GPS de 14h à 16h »,
    « départ à 19h00' », « conserver prime de nuit », et les « rappel le
    22.04 » d'AFA que le client a dû signaler lui-même parce que rien ne
    les montrait.

    On les joint par un saut de ligne, comme Excel joint déjà les lignes
    d'un même commentaire. Quand l'un contient déjà l'autre — le classeur
    recopie souvent la cellule sur l'annotation — on ne garde que le plus
    complet : répéter une phrase la ferait lire deux fois par les motifs de
    remplacement.
    """
    a = (cellule or "").strip()
    b = (annotation or "").strip()
    if not a:
        return b
    if not b:
        return a
    if a in b:
        return b
    if b in a:
        return a
    return a + "\n" + b


def blocs_de_mois(grille):
    """{numéro de mois: ligne du 1er}. Le nom du mois est écrit verticalement
    en colonne 1, une lettre par ligne."""
    debuts = [r for r in sorted(grille) if str(grille[r].get(COL_JOUR, "")) == "1"]
    out = {}
    for i, r0 in enumerate(debuts):
        r1 = debuts[i + 1] if i + 1 < len(debuts) else r0 + 40
        mot = "".join(str(grille.get(r, {}).get(1, "")) for r in range(r0, r1)).upper()
        for n, nom in enumerate(MOIS, 1):
            if mot.startswith(nom) and n not in out:
                out[n] = r0
                break
    return out


POSTES = {"AM", "PM", "N", "D"}


def _sans_accent(t):
    return "".join(c for c in unicodedata.normalize("NFD", t)
                   if unicodedata.category(c) != "Mn")


def _initiales(nom):
    """Identifiant anonyme d'après le nom, selon la convention maison :
    première lettre du prénom, puis première et dernière lettre du nom de
    famille. « Renard P » donne PRD, « Gilbert P. » donne PGT, « Renard PJ »
    donne PRD. Le prénom est la partie d'une ou deux lettres."""
    n = _sans_accent(str(nom)).replace(".", " ")
    n = re.sub(r"\([^)]*\)", " ", n)
    parts = [p for p in re.split(r"[\s,]+", n) if p]
    if len(parts) < 2:
        return None
    if len(parts[-1]) <= 2:
        prenom, famille = parts[-1], "".join(parts[:-1])
    elif len(parts[0]) <= 2:
        prenom, famille = parts[0], "".join(parts[1:])
    else:
        prenom, famille = parts[0], "".join(parts[1:])
    if not prenom or len(famille) < 2:
        return None
    return (prenom[0] + famille[0] + famille[-1]).upper()


def _motif_registre(cl, annuaire):
    """Les noms des PERSONNES, appris de la ligne des noms, avec le trigramme
    de chacune. Rend (motif, {mot: trigramme}).

    Le 25/09/2026, `data/horaire-2026.json` — dépôt PUBLIC — portait le nom
    de famille d'un collègue, écrit au fil de QUATRE commentaires : « changement
    d'équipe de <nom> ». `_motif_auteurs()` ne l'a pas vu, et pour une bonne
    raison : ce collègue n'est déclaré AUTEUR nulle part. L'anonymiseur, lui,
    l'avait retiré — il apprend depuis la ligne des noms.

    Or le convertisseur LIT cette même ligne : c'est d'elle qu'il tire les
    trigrammes. Il avait donc le nom en main et ne s'en servait que pour
    nommer la personne, jamais pour la retirer du texte des autres. C'est
    cette information-là, déjà présente, que l'on emploie ici — et non les
    motifs de l'anonymiseur, que les deux outils doivent pouvoir se
    contredire.

    LA MAJUSCULE INITIALE EST EXIGÉE, comme pour l'anonymiseur : un nom de
    famille peut être un mot français, et « petit » au milieu d'une phrase
    n'est pas quelqu'un. Les mots de moins de trois lettres sont écartés :
    la ligne des noms écrit « Nom P », et un « P » isolé ne nomme personne.
    """
    mots = {}

    def _retenir(nom, tri):
        for mot in re.split(r"[\s,./()]+", nom):
            mot = mot.strip(".").strip()
            if len(mot) >= 3 and mot[:1].isupper() and mot.replace("-", "").isalpha():
                mots.setdefault(_plier(mot), tri.upper())

    for feuille in cl.feuilles:
        try:
            g = cl.grille(feuille)
        except Exception:
            continue
        for colonne, val in (g.get(LIGNE_NOMS) or {}).items():
            nom = str(val).strip()
            if colonne < 3 or nom in ("", "0"):
                continue
            cle = _sans_accent(nom).lower()
            tri = (CORRECTIONS.get(_empreinte(cle)) or annuaire.get(cle)
                   or _initiales(nom))
            if tri:
                _retenir(nom, tri)

    # LA FEUILLE « POLYVALENCE » PORTE LE PRÉNOM EN TOUTES LETTRES, et c'est
    # par elle que quatre prénoms auraient dû partir. CLAUDE.md affirmait le
    # 25/09/2026 qu'ils « n'existent nulle part ailleurs dans le classeur » ;
    # l'audit du 26/09 l'a démenti : chacun est dans la colonne Prénom, sur
    # UNE ligne, et le trigramme de cette ligne est exactement celui qu'on
    # posait à la main sur les huit journées. L'information était là ; on
    # retirait à la main, à chaque conversion, ce que le fichier disait.
    #
    # Le nom de famille (colonne B) et le prénom (colonne C) sont appris avec
    # le trigramme de la ligne — celui que polyvalence() lui donne. Un prénom
    # n'est retenu que s'il est UNIQUE dans sa colonne : partagé par deux
    # personnes, on ne saurait lequel des deux trigrammes écrire, et en
    # choisir un serait troquer une fuite contre une fausse attribution.
    # Ceux-là restent sous la garantie finale, qui arrête la conversion.
    if "Polyvalence" in cl.feuilles:
        g = cl.grille("Polyvalence")
        lignes = []
        for r in sorted(g):
            if r < 5:
                continue
            famille, prenom = str(g[r].get(2, "")).strip(), str(g[r].get(3, "")).strip()
            if not famille or not prenom:
                continue
            cand = "%s %s." % (famille.title(), prenom[0].upper())
            cle = _sans_accent(cand).lower()
            tri = CORRECTIONS.get(_empreinte(cle)) or annuaire.get(cle) or _initiales(cand)
            if tri:
                lignes.append((famille, prenom, tri))
        compte = {}
        for _, prenom, _ in lignes:
            compte[_plier(prenom)] = compte.get(_plier(prenom), 0) + 1
        for famille, prenom, tri in lignes:
            _retenir(famille.title(), tri)
            if compte[_plier(prenom)] == 1:
                _retenir(prenom[:1].upper() + prenom[1:], tri)
    if not mots:
        return None, {}
    return _motif_mots(mots), mots


# Les mots de nom que la garantie cherche dans la sortie : posé par convertir().
_SURVEILLES = set()


def _mots_de_noms(cl):
    """TOUS les mots qui nomment quelqu'un dans le classeur, qu'on ait su ou
    non les attribuer : la ligne des noms, et le nom et le prénom de la
    feuille « Polyvalence » — y compris les prénoms partagés, que le
    registre n'ose pas remplacer."""
    out = set()
    lignes = []
    # Les feuilles de PERSONNES seulement : la ligne 10 de « Récapitulatif
    # (1) » porte des en-têtes — « P. arr », « Ferm. », « Gluten » — et
    # l'anonymiseur a appris le 26/09/2026 ce qu'il en coûte de les prendre
    # pour des gens.
    for feuille in cl.feuilles:
        if feuille not in FEUILLES:
            continue
        g = cl.grille(feuille)
        lignes += [v for c, v in (g.get(LIGNE_NOMS) or {}).items() if c >= 3]
    if "Polyvalence" in cl.feuilles:
        g = cl.grille("Polyvalence")
        for r in g:
            if r >= 5:
                lignes += [g[r].get(2, ""), g[r].get(3, "")]
    for nom in lignes:
        # « Nom P.(ass.Us.) » : la parenthèse dit le rôle, pas la personne.
        for mot in re.split(r"[\s,./()]+", re.sub(r"\([^)]*\)", " ", str(nom))):
            mot = mot.strip(".").strip()
            if len(mot) >= 3 and mot.replace("-", "").isalpha() and not mot.isupper():
                out.add(_plier(mot))
            elif len(mot) >= 4 and mot.replace("-", "").isalpha():
                out.add(_plier(mot))
    return out


def garantie(texte, surveilles, tolere=()):
    """LA SORTIE EST RELUE, ET UN SEUL NOM L'ARRÊTE.

    C'est la doctrine de l'anonymiseur, et le convertisseur ne l'avait pas :
    il remplaçait ce qu'il savait reconnaître et écrivait le reste. Quatre
    prénoms sont ainsi arrivés dans le JSON d'un dépôt PUBLIC, et il a
    fallu les retirer à la main à chaque conversion. On cherche ici, dans
    TOUT le JSON produit — journées, champ « e », contrats, dates de
    polyvalence —, chaque mot de nom du classeur, écrit avec sa majuscule.

    Rend la liste des restes : (mot, contexte).
    """
    plie = _plier(texte)
    restes = []
    for mot in sorted(surveilles):
        if mot in tolere or mot not in plie:
            continue
        for m in re.finditer(r"\b" + re.escape(mot) + r"\b", plie):
            if texte[m.start()].isupper():
                restes.append((mot, texte[max(0, m.start() - 30):m.end() + 30]))
    return restes


def _plier(t):
    """Le mot sans accents et en minuscules, caractère pour caractère."""
    return "".join((_sans_accent(c) or c)[:1].lower()[:1] for c in t)


def _motif_mots(mots):
    """Un motif qui retrouve chacun des mots SANS TENIR COMPTE DES ACCENTS NI
    DE LA CASSE, sauf la majuscule initiale, qu'il exige.

    L'un des quatre prénoms du 25/09 n'était pas écrit pareil dans la feuille
    « Polyvalence » et dans le commentaire — un accent ou une capitale de
    différence. Une comparaison exacte le laissait passer, et la
    reconversion l'aurait réécrit sans que personne ne le voie.

    Il s'applique au texte PLIÉ caractère pour caractère (`_plier` garde la
    longueur), ce qui laisse remplacer aux mêmes positions dans l'original.
    La majuscule se lit sur l'original : « marie » est un verbe, « Marie »
    une personne.
    """
    # Le plus long d'abord, pour qu'un nom composé ne soit pas coupé.
    alt = "|".join(re.escape(m) for m in sorted(mots, key=len, reverse=True))
    return re.compile(r"\b(?:" + alt + r")\b")


def _sans_registre(txt, registre):
    """Remplacer par leur trigramme les noms appris du classeur."""
    if not registre or not registre[0]:
        return txt
    motif, tri = registre
    plie = _plier(txt)
    out, pos = [], 0
    for m in motif.finditer(plie):
        if not txt[m.start()].isupper():
            continue
        out.append(txt[pos:m.start()])
        out.append(tri[m.group(0)])
        pos = m.end()
    out.append(txt[pos:])
    return "".join(out)


def _annuaire(cl):
    """La feuille « Personnel » donne la correspondance officielle nom →
    initiales. Elle est incomplète ; _initiales() prend le relais."""
    out = {}
    if "Personnel" not in cl.feuilles:
        return out
    for ligne in cl.grille("Personnel").values():
        nom, ini = str(ligne.get(1, "")).strip(), str(ligne.get(2, "")).strip()
        if nom and ini and nom not in ("0", "Nom"):
            out[_sans_accent(nom).lower()] = ini.upper()
    return out


# LE CLASSEUR ÉCRIT LES CONTRATS RÉDUITS EN PIED DE FEUILLE, et personne ne
# les lisait. Le client, le 25/09/2026 : « il faut que toutes les données du
# fichier soient récupérées pour alimenter l'app et les règles ».
#
# Quatre-vingt-deux commentaires, lignes 396 à 434, écrivent le congé
# parental et le temps partiel de chacun avec leurs dates :
#
#     « CP 10% du 01.11.2022 au 28.02.2026 »
#     « TP contractuel 20% du 01.07.2025 au 30.06.2027 »
#     « CP 20% à partir du 01/11/2026 pour 5 mois »
#     « 12 mois à 90% »
#
# C'est la « fraction payée » que l'application fait saisir À LA MAIN.
#
# LE SENS DU POURCENTAGE NE SE DEVINE PAS — LE CLASSEUR LE DIT DEUX FOIS.
# Une même personne porte « TP 10% du 15.03.2024 au 14.03.2026 … TP 20% à
# partir du 01/06 » et, trois lignes plus haut, « 90% 01/01 au 14/03  80% du
# 01/06 au 31/12 ». Une autre porte « CP 10% du 01/12/25 au 30/09/26 » et
# « CP 90 % du 01/12/2025 au 30/09/2026 » — mêmes dates, deux notations. Dix
# pour cent de RÉDUCTION valent donc quatre-vingt-dix pour cent PRESTÉS, et
# ce sont les colonnes du classeur qui se répondent, pas une supposition.
#
# D'où la borne : un pourcentage d'au plus 30 est une réduction, un
# pourcentage d'au moins 70 est la part prestée. Le classeur n'écrit rien
# entre les deux — mesuré : 10 et 20 d'un côté, 80, 90 et 100 de l'autre. Ce
# qui tomberait entre serait gardé SANS fraction plutôt que deviné.
#
# CINQUANTE EST LA SEULE EXCEPTION, ET ELLE SE DÉMONTRE. Le client a décrit
# les trois dispositifs belges le 25/09/2026 : le crédit-temps se prend « 1/5
# → travail à 4/5 » ou « 1/2 → travail à mi-temps ». Un mi-temps s'écrira
# donc « 50% » un jour, en plein milieu de la bande refusée — mais à
# cinquante l'ambiguïté N'EXISTE PAS : cinquante pour cent de réduction et
# cinquante pour cent prestés sont le même nombre, 0,50. On ne devine rien en
# l'acceptant ; on constate que les deux lectures coïncident.
#
# CENT AVEC UN CODE EST AMBIGU, ET LUI RESTE REFUSÉ. « CP 100% » peut dire un
# temps plein retrouvé (1,00) comme une suspension complète (0,00) — les deux
# existent en droit belge, et l'écart est tout le socle du mois. Un « 100% »
# SANS code reste ce qu'il est : personne n'a nommé de dispositif, donc rien
# n'est suspendu.
CONTRAT = re.compile(r"(?:(CP|TP|CT)\b[^%\d]{0,24})?(\d{1,3})\s*%", re.I)
# Les régimes que chaque dispositif connaît, en pourcentage de RÉDUCTION.
# Le congé parental se prend en 1/5 ou en 1/10 ; le crédit-temps en 1/5 ou en
# 1/2, « le 9/10 n'est pas le régime général du crédit-temps 1/5 ». Le temps
# partiel, lui, est ce que le contrat dit — aucune borne à lui opposer, donc
# aucune ligne ici. Ce n'est pas un filtre : rien n'est refusé sur cette
# foi-là, c'est seulement dit sur la sortie d'erreur.
REGIMES = {"CP": (10, 20), "CT": (20, 50)}
_JOUR = r"(\d{1,2})[./](\d{1,2})(?:[./\s](\d{2,4}))?"
# « du 01.11.2022 au 28.02.2026 », mais aussi « 01/03/26 au 30/06/2029 » : le
# « du » manque une fois sur deux. On l'accepte donc absent — à CONDITION
# qu'un « au » relie les deux dates, sans quoi la ligne des jours fériés non
# pris, « -01/01 -06/04 -01/05 », donnerait une période de janvier à avril.
PERIODE = re.compile(
    r"(?:(?:du|dès|à partir du|apd|àpd)\s*)?" + _JOUR
    + r"\s*(?:au|jusqu'au|jusque)\s*" + _JOUR, re.I)
DEBUT_SEUL = re.compile(r"(?:du|dès|à partir du|apd|àpd)\s*" + _JOUR, re.I)
DUREE = re.compile(r"pour\s+(\d{1,2})\s*mois", re.I)


def _date(j, m, a, defaut=None):
    """« 28.02.26 » et « 28/02/2026 » donnent la même chose.

    SANS ANNÉE, C'EST CELLE DE L'HORAIRE. Le client, le 25/09/2026 : « si pas
    de date il faut prendre en compte celle écrite dans l'horaire, mais ne pas
    deviner ». Un classeur de 2026 qui écrit « 90% 01/01 au 14/03 » parle de
    2026 — ce n'est pas une supposition, c'est l'année du fichier. Et le
    classeur se corrobore : cette fin du 14/03 est exactement celle du contrat
    daté « TP 10% du 15.03.2024 au 14.03.2026 » de la même personne.

    Sans année ET sans défaut, None : une période qui ne se rattache à rien ne
    se compare à rien."""
    if not a:
        a = defaut
    if not (j and m and a):
        return None
    j, m, a = int(j), int(m), int(a)
    if a < 100:
        a += 2000
    if not (1 <= m <= 12 and 1 <= j <= 31 and 2000 <= a <= 2100):
        return None
    return "%04d-%02d-%02d" % (a, m, j)


def _plus_mois(iso, n):
    if not iso:
        return None
    a, m, j = (int(x) for x in iso.split("-"))
    m += int(n)
    a += (m - 1) // 12
    m = (m - 1) % 12 + 1
    return "%04d-%02d-%02d" % (a, m, min(j, 28))


def _periode(bout, annee=None):
    """La première période écrite dans ce bout de texte, et sa durée."""
    d = fin = None
    p = PERIODE.search(bout)
    if p:
        d = _date(p.group(1), p.group(2), p.group(3), annee)
        fin = _date(p.group(4), p.group(5), p.group(6), annee)
    else:
        p = DEBUT_SEUL.search(bout)
        if p:
            d = _date(p.group(1), p.group(2), p.group(3), annee)
    n = DUREE.search(bout)
    if n and d and not fin:
        fin = _plus_mois(d, n.group(1))
    return d, fin


def contrats(cl, feuille, colonne, annee=None):
    """Les périodes de contrat réduit d'une personne, lues en pied de feuille.

    UN COMMENTAIRE PEUT EN PORTER DEUX — « CP 10% du 02.04.24 au 01.10.2026
    CP 10% du 02.10.26 au 01.02.2030 » — et n'en lire qu'une ferait croire
    que le contrat s'arrête. On découpe donc le texte à chaque pourcentage,
    et chaque morceau porte sa propre période.

    On garde TOUJOURS le texte d'origine à côté de ce qui a été compris : ce
    qui n'est pas compris aujourd'hui reste lisible demain, et une fraction
    absente vaut mieux qu'une fraction inventée.
    """
    out = []
    for (ligne, col), txt in cl.commentaires(feuille).items():
        if ligne < 396 or col not in (colonne, colonne + 1):
            continue
        bouts = [m for m in CONTRAT.finditer(txt)]
        if not bouts:
            # Sans pourcentage, seul un code explicite fait un contrat ; le
            # reste du pied de feuille — jours fériés non pris, notes de
            # planification — vit dans l'export intégral, pas ici.
            if re.search(r"\b(CP|TP|CT)\b", txt, re.I):
                d, fin = _periode(txt, annee)
                out.append({"txt": txt, "l": ligne, "d": d, "fin": fin})
            continue
        for i, m in enumerate(bouts):
            arret = bouts[i + 1].start() if i + 1 < len(bouts) else len(txt)
            bout = txt[m.start():arret]
            fiche = {"txt": txt if len(bouts) == 1 else bout.strip(),
                     "l": ligne}
            pct = int(m.group(2))
            code = (m.group(1) or "").upper()
            if code:
                fiche["t"] = code
            if code and pct == 100:
                # Suspension complète ou temps plein retrouvé : tout ou rien
                # sur le socle, et le classeur ne dit pas lequel.
                fiche["amb"] = True
            elif pct <= 30 or pct == 50:
                fiche["pct"], fiche["f"] = pct, round(1 - pct / 100.0, 4)
            elif pct >= 70:
                fiche["pct"], fiche["f"] = 100 - pct, round(pct / 100.0, 4)
            fiche["d"], fiche["fin"] = _periode(bout, annee)
            out.append(fiche)
    return out


def _borner(fiches, jours, annee):
    """Un contrat sans date se borne aux JOURNÉES que l'horaire écrit.

    Le client, le 25/09/2026 : « si pas de date il faut prendre en compte
    celle écrite dans l'horaire, mais ne pas deviner ». Trois personnes
    portent « CT 20% » et rien d'autre — et leurs colonnes portent 55, 53 et
    51 journées codées `CT`, étalées sur l'année. La période est donc écrite,
    simplement ailleurs : de la première de ces journées à la dernière.

    C'est le contraire d'une supposition : on ne comble pas un trou, on va
    lire la réponse là où le classeur l'a mise. Et sans journée de ce code,
    rien n'est posé — une fiche sans date reste sans date, et la fraction du
    réglage reprend la main.

    Le code doit être NOMMÉ dans la fiche : « 12 mois à 90% » ne dit ni CP ni
    TP, donc on ne saurait pas quelles journées regarder. Ces fiches-là
    restent telles quelles ; elles doublent d'ailleurs un contrat daté chez
    les deux personnes qui les portent.
    """
    if not jours:
        return fiches
    trouve = {}
    for fiche in fiches:
        code = fiche.get("t")
        if not code or fiche.get("d") or not fiche.get("f"):
            continue
        if code not in trouve:
            motif = re.compile(r"\b" + code + r"\b", re.I)
            dates = sorted(k for k, v in jours.items()
                           if motif.search(" ".join(str(x) for x in v)))
            trouve[code] = dates
        dates = trouve[code]
        if not dates:
            continue
        fiche["d"] = "%04d-%s-%s" % (annee, dates[0][:2], dates[0][2:])
        fiche["fin"] = "%04d-%s-%s" % (annee, dates[-1][:2], dates[-1][2:])
        fiche["src"] = "horaire"
    return fiches


def _norme_cle(libelle):
    """« 1/2VA » -> « demiVA », « 4h +FT » -> « 4h+FT », « Total: » -> « Total »."""
    t = libelle.strip().rstrip(":").strip()
    return t.replace("1/2", "demi").replace(" ", "") or None


def verifier_blocs(g, feuille):
    """Le titre attendu doit se trouver dans son bloc, sinon la structure du
    classeur a bougé et les compteurs seraient lus de travers."""
    for nom, r0, r1, titre in BLOCS:
        if not titre:
            continue
        gauche = " ".join(str(g[r][c]) for r in range(r0, r1 + 1) if r in g
                          for c in sorted(g[r]) if c <= 2).lower()
        if _sans_accent(titre) not in _sans_accent(gauche):
            print("  %s : bloc « %s » introuvable en lignes %d-%d — compteurs"
                  " ignorés" % (feuille, titre, r0, r1), file=sys.stderr)
            return False
    return True


def compteurs(g, colonne):
    """Le pied de feuille d'une personne : prévisions de congé, soldes au
    1er janvier, soldes restants, compteurs flex time, CP.

    Ces valeurs sont SAISIES, pas calculées — 1 099 cellules contre 12
    formules sur la feuille des contremaîtres. Aucun calcul ne les retrouve
    depuis l'horaire : il faut les lire.

    Dans le bloc des prévisions, un libellé qui revient est un total : les
    journées entières d'abord, le cumul ensuite. VBN : 40 h de RTT en
    journées entières, plus 14 h prises à l'heure, soit 54 h au total.

    Ailleurs, un libellé qui revient est un compteur distinct, et non une
    somme. Le client a deux lignes CP parce qu'il a terminé le congé
    parental pris pour sa fille et en a ouvert un second pour son fils en
    cours d'année : 5 journées puis 21, soit bien les 26 journées marquées
    CP dans son horaire, coupées par un mois de mars sans aucune."""
    out = {}
    for nom, r0, r1, _ in BLOCS:
        vals = {}
        for r in range(r0, r1 + 1):
            ligne = g.get(r)
            if not ligne:
                continue
            lib = str(ligne.get(colonne, "")).strip()
            brut = ligne.get(colonne + 1)
            if not lib or brut is None:
                continue
            cle = _norme_cle(lib)
            if not cle:
                continue
            try:
                val = float(brut)
            except (TypeError, ValueError):
                continue
            if val == int(val):
                val = int(val)
            cle = RENOMME.get(cle, cle)
            n = 2
            while cle in vals:
                cle = ("%sTotal" % cle) if nom == "prevision" else ("%s%d" % (_norme_cle(lib), n))
                n += 1
            vals[cle] = val
        if vals:
            out[nom] = vals
    return out


def metadata(cl):
    """Ce que le classeur dit de lui-même : la date de sa dernière mise à
    jour (onglet « Config »), la légende des codes d'absence et la liste des
    ateliers de l'onglet « Polyvalence »."""
    out = {}
    if "Config" in cl.feuilles:
        brut = cl.grille("Config").get(19, {}).get(2)
        try:
            jour = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=float(brut))
            out["maj"] = jour.strftime("%Y-%m-%dT%H:%M")
        except (TypeError, ValueError):
            pass
    # LA LÉGENDE ENTIÈRE, et non ses quatre premières paires. Elle ne lisait
    # que les colonnes A et B de la première feuille : VA, RTT, RHS, RJF. Le
    # reste — « xxx » congé accordé sous restriction, R · Abs · DS · CP · CSS ·
    # R-CM — est écrit au-dessus des colonnes-personnes, lignes 1 à 8, et
    # partait dans le champ « e » de vingt-neuf personnes, affiché sous leur
    # nom dans l'annuaire comme s'il les concernait. Mesuré par l'audit du
    # 26/09/2026.
    #
    # Une paire est un code court suivi de son libellé dans la cellule
    # voisine ; la date de mise à jour, suivie d'un nombre, n'en est pas une.
    # La première écriture d'un code l'emporte : les feuilles se recopient.
    leg = {}
    for feuille in FEUILLES:
        if feuille not in cl.feuilles:
            continue
        g = cl.grille(feuille, fusions=())
        for r in range(1, LIGNE_POSTE):
            for c in sorted(g.get(r, {})):
                code = str(g[r][c]).strip().rstrip(",.")
                lib = str(g[r].get(c + 1, "")).strip()
                if (code and lib and len(code) <= 6 and " " not in code
                        and not re.match(r"^[\d.,]+$", lib) and len(lib) > len(code)):
                    leg.setdefault(code, lib)
    if leg:
        out["legende"] = leg
    if "Polyvalence" in cl.feuilles:
        g = cl.grille("Polyvalence")
        out["ateliers"] = [str(g[3][c]).strip()
                           for c in sorted(g.get(3, {})) if c >= 6]
    return out


# LA FEUILLE « POLYVALENCE » DATE CHAQUE ACQUISITION, en commentaire sur la
# croix. Soixante-quatorze dates que personne ne lisait, alors que l'onglet
# Recyclage montre les polyvalences sans jamais dire DEPUIS QUAND on les a.
#
#     « 31-01-2023 » · « 01/03/2026 » · « 19-10-17 »
#     « MDE: supprimée àpd 01/02/19 » · « fin polyvalence gluten le 31/08/18 »
#     « fin au 30/09/2026 » · « 16-07-2019 revalidé en 2023 »
#
# DEUX SENS, ET UN MOT LES SÉPARE. Une date seule est une acquisition ; la
# même date précédée de « fin » ou de « supprimée » est une PERTE. Se
# tromper afficherait « acquise en 2019 » sur une polyvalence retirée depuis.
#
# Une perte se lit aussi à la croix : les trois polyvalences supprimées n'en
# portent plus. Mais « fin au 30/09/2026 » en garde une — elle n'est pas
# encore terminée. Le mot décide, pas la croix.
#
# On garde TOUJOURS le texte : « revalidé en 2023 », « CLE prod passée le
# 25/04 » disent quelque chose que deux champs de date ne portent pas.
DATE_POLY = re.compile(r"\b(\d{1,2})[-/.](\d{1,2})[-/.](\d{2,4})\b")
FIN_POLY = re.compile(r"\b(fin|supprim)", re.I)


def _date_polyvalence(txt):
    """{« d » : acquise le, « fin » : perdue le, « txt » : ce qui est écrit}."""
    fiche = {"txt": txt}
    m = DATE_POLY.search(txt)
    if m:
        quand = _date(m.group(1), m.group(2), m.group(3))
        if quand:
            fiche["fin" if FIN_POLY.search(txt) else "d"] = quand
    return fiche


def polyvalence(cl, annuaire):
    """L'onglet « Polyvalence » : le degré de chacun et les ateliers qu'il
    peut tenir. Il porte matricule, nom et prénom en clair — rien de tout
    cela ne sort d'ici, seul l'identifiant à trois lettres est conservé.
    Elle rend, par trigramme RÉEL, la liste des lignes qui le portent — sans
    en écraser aucune. Deux lignes pour un même trigramme sont deux personnes,
    pas une erreur.
    """
    if "Polyvalence" not in cl.feuilles:
        return {}
    g = cl.grille("Polyvalence")
    cm = cl.commentaires("Polyvalence")
    noms = {c: str(g[3][c]).strip() for c in sorted(g.get(3, {})) if c >= 6}
    out = {}
    for r in sorted(g):
        if r < 5:
            continue
        famille, prenom = str(g[r].get(2, "")).strip(), str(g[r].get(3, "")).strip()
        if not famille or not prenom:
            continue
        cand = "%s %s." % (famille.title(), prenom[0].upper())
        # Le trigramme RÉEL — celui que le classeur écrit — et non celui que
        # CORRECTIONS attribuera ensuite. Le client : « dans le fichier Excel
        # il faut prendre leur polyvalence sur leur vrai trigramme ». Une
        # personne renommée reste inscrite ici sous son ancien trigramme :
        # c'est là, et nulle part ailleurs, qu'il faut aller la chercher.
        cle = _sans_accent(cand).lower()
        # Une correction du client tranche tout : elle désigne la personne
        # elle-même, et court-circuite le trigramme comme le nom. C'est le
        # « sauf pour » de la règle — il faut bien un endroit où le dire.
        forcee = CORRECTIONS.get(_empreinte(cle))
        if forcee:
            _corrections_polyvalence.add(_empreinte(cle))
        reel = forcee or annuaire.get(cle) or _initiales(cand)
        if not reel:
            continue
        ateliers = [noms[c] for c in noms if g[r].get(c)]
        fiche = {}
        # LA COLONNE A PORTE UN MATRICULE OU UN STATUT — « interim », « Adj
        # CM », « Assistant usine ». Le statut est gardé : docs/regles-paie.md
        # tenait à la main la liste des intérimaires en écrivant que « le
        # classeur ne le dit nulle part », et il le disait, pour dix des
        # onze. Le MATRICULE, lui, ne sort jamais d'ici : il n'est qu'une
        # suite de chiffres, et c'est à cela qu'on le reconnaît.
        statut = str(g[r].get(1, "")).strip()
        if statut and not re.match(r"^[\d.\s]+$", statut):
            fiche["statut"] = statut
        if g[r].get(4):
            fiche["degre"] = str(g[r][4]).strip()
        if ateliers:
            fiche["ateliers"] = ateliers
        # Les dates vivent à PART des ateliers, et il le faut : une
        # polyvalence retirée n'a plus de croix mais garde son commentaire.
        # La ranger dans « ateliers » la rendrait à la personne ; la taire
        # perdrait la seule trace qu'elle a existé.
        dates = {}
        for c in noms:
            t = cm.get((r, c))
            if t:
                dates[noms[c]] = _date_polyvalence(t)
        if dates:
            fiche["dates"] = dates
        if not fiche:
            continue
        # On rend les lignes TELLES QUELLES, sans en écraser aucune : le
        # classeur en porte deux pour GBT — Gluten et Chaudières — et ce
        # sont deux personnes. C'est au rattachement de les départager.
        out.setdefault(reel, []).append((_cle_nom(cand), fiche))
    return out


def restes(g, feuille, mois, premier_jour):
    """Dit ce que le convertisseur N'A PAS repris.

    Il ne lisait que la ligne des noms, les journées et le pied de feuille ;
    tout le reste tombait, sans un mot. Le poste de travail de chacun était
    probablement là. Une perte silencieuse est une perte qu'on ne corrige
    jamais : à partir d'ici, il compte ce qu'il laisse et le dit.

    Les échantillons imprimés évitent tout ce qui ressemble à un nom.
    """
    lues = set(range(1, premier_jour + 1))
    for r0 in mois.values():
        for d in range(1, 32):
            r = r0 + d - 1
            if str(g.get(r, {}).get(COL_JOUR, "")) == str(d):
                lues.add(r)
    for _, debut, fin, _ in BLOCS:
        lues.update(range(debut, fin + 1))
    perdues = {}
    for r in sorted(g):
        if r in lues:
            continue
        vals = [str(v).strip() for c, v in g[r].items()
                if c >= 3 and str(v).strip() not in ("", "0")]
        if vals:
            perdues[r] = vals
    if not perdues:
        return
    n = sum(len(v) for v in perdues.values())
    print("  %s : %d cellule(s) non reprise(s) sur %d ligne(s)"
          % (feuille, n, len(perdues)), file=sys.stderr)
    for r in sorted(perdues)[:6]:
        sur = [v for v in perdues[r] if "," not in v and len(v) <= 20][:3]
        print("      ligne %-4d %3d valeur(s)%s"
              % (r, len(perdues[r]), ("  — " + " | ".join(sur)) if sur else ""),
              file=sys.stderr)


def _sans_nom(g, feuille, mois):
    """ANNONCER les colonnes qui portent des journées sans nom en ligne 10.

    Le convertisseur ne lit que les colonnes dont la ligne des noms est
    remplie, et restes() ne regarde que les LIGNES : deux colonnes entières
    tombaient sans un mot — Shift4 Q, la fermentation de l'équipe 4, avec des
    congés jusqu'en décembre, et Shift1 AG, une rotation de chaudières.
    L'audit du 26/09/2026 les a trouvées : ce sont des copies de travail de
    DWS et de CHD, et les lire compterait deux fois ces personnes. On ne les
    rattache donc à personne — c'est au client de dire ce qu'elles sont —,
    mais on les DIT : une perte silencieuse est une perte qu'on ne corrige
    jamais.
    """
    nommees = set(c for c, v in (g.get(LIGNE_NOMS) or {}).items()
                  if str(v).strip() not in ("", "0"))
    lignes = [r0 + d - 1 for r0 in mois.values() for d in range(1, 32)
              if str(g.get(r0 + d - 1, {}).get(COL_JOUR, "")) == str(d)]
    vues = set()
    for c in sorted(set(k for r in lignes for k in g.get(r, {}))):
        if c < 3 or c in nommees or c - 1 in nommees or c - 1 in vues:
            continue
        ecrites = sum(1 for r in lignes if str(g.get(r, {}).get(c, "")).strip())
        if not ecrites:
            continue
        vues.add(c)
        poste = str(g.get(LIGNE_POSTE, {}).get(c, "")).strip() or "?"
        annot = sum(1 for r in lignes if str(g.get(r, {}).get(c + 1, "")).strip())
        print("  %s colonne %s (%s) : %d journée(s) et %d annotation(s) SANS NOM en"
              " ligne %d — non reprises, à faire trancher"
              % (feuille, _lettre(c), poste, ecrites, annot, LIGNE_NOMS), file=sys.stderr)


def _colonnes(cl, annee=None):
    """Toutes les colonnes-personnes de toutes les feuilles, avec leur nom.
    Une même personne figure sur plusieurs feuilles ; on les fusionne ensuite
    sur son identifiant."""
    for feuille, categorie in FEUILLES.items():
        if feuille not in cl.feuilles:
            print("  feuille absente :", feuille, file=sys.stderr)
            continue
        g = cl.grille(feuille)
        cm = cl.commentaires(feuille)
        pied = verifier_blocs(g, feuille)
        mois = blocs_de_mois(g)
        # Tout ce qui est écrit AU-DESSUS du nom, et entre le nom et la
        # première journée, appartient à la personne : le client a demandé
        # que rien du classeur ne se perde, et c'est probablement là que se
        # trouve le poste de travail. On recopie sans interpréter, comme
        # partout ailleurs — l'application décidera quoi en faire.
        premier_jour = min(mois.values()) if mois else LIGNE_NOMS + 1
        restes(g, feuille, mois, premier_jour)
        _sans_nom(g, feuille, mois)
        for colonne in sorted(g.get(LIGNE_NOMS, {})):
            nom = str(g[LIGNE_NOMS][colonne]).strip()
            if colonne < 3 or nom in ("", "0"):
                continue
            # Les lignes 1 à 8 portent la LÉGENDE et la date de mise à jour,
            # et rien d'autre (mesuré le 26/09/2026 sur les 102 colonnes) :
            # elles vont dans « legende » et « maj », pas dans « e ». La
            # ligne 9 — le poste, ou le binôme d'un cadre — et ce qui suit le
            # nom restent à la personne.
            entete = []
            for r in list(range(LIGNE_POSTE, LIGNE_NOMS)) + list(range(LIGNE_NOMS + 1, premier_jour)):
                for c in (colonne, colonne + 1):
                    v = str(g.get(r, {}).get(c, "")).strip()
                    if v and v != "0" and v not in entete:
                        entete.append(v)
            # Le poste tenu, juste au-dessus du nom. C'est la source
            # PRINCIPALE du poste — le client l'a établi le 20/09/2026. Il
            # peut être écrit sur l'une ou l'autre des deux colonnes de la
            # personne, la fusion de cellules ne se voyant pas d'ici.
            poste = ""
            for c in (colonne, colonne + 1):
                v = str(g.get(LIGNE_POSTE, {}).get(c, "")).strip()
                if v and v != "0":
                    poste = v
                    break
            if not poste:
                poste = POSTE_DE_LA_FEUILLE.get(feuille, "")
            jours, vides = {}, []
            for m, r0 in mois.items():
                for d in range(1, 32):
                    r = r0 + d - 1
                    if str(g.get(r, {}).get(COL_JOUR, "")) != str(d):
                        continue
                    cell = g.get(r, {}).get(colonne, "")
                    annot = g.get(r, {}).get(colonne + 1, "")
                    com = _les_deux(cm.get((r, colonne), ""),
                                    cm.get((r, colonne + 1), ""))
                    if not (cell or annot or com):
                        # UNE CELLULE VIDE EST UN REPOS, ET NON UNE JOURNÉE
                        # QUI N'EXISTE PAS. Le client, le 25/09/2026 : « si
                        # vide c'est une journée sans travail (repos), et je
                        # confirme que je ne travaillais pas ces jours-là
                        # dans mon calendrier ».
                        #
                        # Sauter la ligne laissait 643 journées absentes du
                        # fichier chez 13 personnes — pas « en repos » :
                        # ABSENTES. Le calendrier n'avait pas de case à
                        # peindre, equipeDuJour() recevait un `undefined`,
                        # et rien ne disait que le jour existait.
                        #
                        # La ligne du JOUR existe bien — c'est la colonne
                        # des jours qui l'a fait entrer ici — donc ce qui
                        # manque est la cellule, pas la journée.
                        vides.append("%02d%02d" % (m, d))
                        continue
                    e = [cell, annot, com]
                    while e and not e[-1]:
                        e.pop()
                    jours["%02d%02d" % (m, d)] = e
            # UNE CELLULE VIDE DEVIENT UN REPOS — SEULEMENT ENTRE LA
            # PREMIÈRE ET LA DERNIÈRE JOURNÉE ÉCRITE.
            #
            # Avant de borner, la règle donnait 643 journées à 13 personnes
            # — dont 348 à quelqu'un qui n'a que 17 journées écrites de
            # toute l'année, 193 et 69 à deux autres. Ceux-là ne sont pas en
            # repos : ils ne sont pas encore arrivés, ou ils sont partis.
            # Les peindre en repos les aurait fait vivre dans la composition
            # et dans les manques d'effectif des mois où ils n'étaient pas
            # là.
            #
            # Le classeur ne dit nulle part quand quelqu'un arrive. Ce qu'il
            # dit, c'est où sa colonne commence à porter quelque chose : la
            # borne est donc CE QU'IL ÉCRIT, et non une date devinée.
            if jours:
                bas, haut = min(jours), max(jours)
                for k in vides:
                    if bas < k < haut:
                        jours[k] = ["-"]
            if jours:
                yield (categorie, nom, jours,
                       compteurs(g, colonne) if pied else {}, entete,
                       feuille, poste, _lettre(colonne),
                       contrats(cl, feuille, colonne, annee) if pied else [])


def convertir(chemin_xlsm, annee):
    cl = Classeur(chemin_xlsm)
    annuaire = _annuaire(cl)
    # AVANT toute lecture de commentaire : le nettoyage s'en sert.
    cl.registre = _motif_registre(cl, annuaire)
    if cl.registre[0]:
        print("  registre des noms : %d mot(s) appris de la ligne des noms"
              " et de la feuille Polyvalence" % len(cl.registre[1]), file=sys.stderr)
    global _SURVEILLES
    _SURVEILLES = _mots_de_noms(cl)

    # 1. Une fiche par personne, repérée par son nom normalisé. Une même
    #    personne figure sur plusieurs feuilles : la première rencontrée
    #    donne sa catégorie, et FEUILLES met les feuilles spécialisées en
    #    tête pour que ce soit celle de son propre groupe.
    fiches, utilisees, noms = {}, set(), {}
    for (categorie, nom, jours, cpt, entete, feuille, poste, col,
         ctr) in _colonnes(cl, annee):
        cle = _sans_accent(nom).lower()
        noms[cle] = nom
        corrige = CORRECTIONS.get(_empreinte(cle))
        officiel = corrige or annuaire.get(cle)
        base = officiel or _initiales(nom)
        if not base:
            print("  nom illisible, ligne ignorée :", nom, file=sys.stderr)
            continue
        utilisees.add(_empreinte(cle))
        # Le trigramme que le CLASSEUR écrit, avant toute correction : c'est
        # sous celui-là que l'onglet Polyvalence inscrit la personne.
        f = fiches.setdefault(cle, {"base": base, "officiel": bool(officiel),
                                    "reel": annuaire.get(cle) or _initiales(nom),
                                    "nomcle": _cle_nom(nom),
                                    "cat": categorie, "d": {}, "c": {}, "e": [],
                                    "postes": {}, "ct": []})
        # Le poste est propre à la FEUILLE : la même personne est « Adjoints
        # Contremaître » sur les cinq équipes et porte un numéro d'équipe sur
        # sa propre feuille. On garde les deux plutôt que d'en élire un.
        if poste:
            f["postes"][feuille] = {"p": poste, "c": col}
        for v in entete:
            if v not in f["e"]:
                f["e"].append(v)
        for sec, vals in cpt.items():
            if vals:
                f["c"].setdefault(sec, {}).update(vals)
        # La même personne figure sur plusieurs feuilles, qui recopient le
        # même commentaire de contrat ; on ne le garde qu'une fois.
        for c in ctr:
            if not any(x["txt"] == c["txt"] for x in f["ct"]):
                f["ct"].append(c)
        # une feuille peut porter des journées ou des commentaires que
        # l'autre n'a pas ; on garde l'entrée la plus informative
        for k, e in jours.items():
            if len(e) >= len(f["d"].get(k, [])):
                f["d"][k] = e

    # 2. Deux personnes différentes peuvent donner les mêmes initiales. Le
    #    suffixe qui les départage ne doit PAS dépendre de l'ordre de
    #    lecture des feuilles : un simple changement d'ordre échangerait
    #    leurs identifiants d'une conversion à l'autre, et le pré-remplissage
    #    d'un mois basculerait en silence sur quelqu'un d'autre.
    #
    #    L'ordre est donc : l'identifiant officiel de la feuille Personnel
    #    d'abord, puis la fiche la plus fournie, puis le nom. Tout est
    #    départagé par les données, rien par l'ordre des feuilles.
    # Un trigramme calculé peut tomber sur celui qu'un autre porte
    # officiellement — c'est le cas de JBY, trigramme d'un responsable, que
    # la règle des initiales attribuait à un opérateur.
    #
    # Quand les deux noms se ressemblent, c'est la même personne écrite
    # autrement dans l'onglet Personnel, et la règle est tombée juste.
    #
    # Quand ils diffèrent, ce n'est pas forcément une erreur : l'onglet
    # Personnel est en retard sur le classeur — 55 noms quand l'horaire en
    # porte 77, dont 27 qui n'y figurent plus. Le titulaire officiel est le
    # plus souvent quelqu'un qui est parti. D'où un simple signalement, à
    # vérifier, et non une alerte.
    par_officiel = {}
    for cle_off, trig in annuaire.items():
        par_officiel.setdefault(trig, []).append(cle_off)
    for cle, f in fiches.items():
        if f["officiel"] or f["base"] not in par_officiel:
            continue
        for cle_off in par_officiel[f["base"]]:
            if difflib.SequenceMatcher(None, cle, cle_off).ratio() < 0.72:
                print("  %s : l'onglet Personnel le donne à un autre nom, que"
                      " l'horaire ne porte pas. Il revient sans doute à cette"
                      " personne de %s, l'onglet étant en retard — à vérifier"
                      " si le trigramme est très cité en commentaire"
                      % (f["base"], f["cat"]), file=sys.stderr)
                break

    for trig, cles in par_officiel.items():
        # une contradiction de l'onglet Personnel que CORRECTIONS a déjà
        # tranchée n'a plus à être signalée
        restants = [c for c in cles if _empreinte(c) not in CORRECTIONS]
        if len(restants) > 1:
            print("  l'onglet Personnel attribue %s à %d noms différents"
                  % (trig, len(restants)), file=sys.stderr)

    for cle, f in sorted(fiches.items(), key=lambda kv: kv[1]["base"]):
        for k in colonnes_inversees(f["d"]):
            print("  %s le %s/%s : le compteur « %s » est écrit dans la colonne"
                  " du poste — le classeur ne le compte pas"
                  % (f["base"], k[2:], k[:2], f["d"][k][0]), file=sys.stderr)

    par_base = {}
    for cle, f in fiches.items():
        par_base.setdefault(f["base"], []).append((cle, f))
    gens, reels, cles_ident = {}, {}, {}
    for base in sorted(par_base):
        lot = sorted(par_base[base],
                     key=lambda kv: (not kv[1]["officiel"], -len(kv[1]["d"]), kv[0]))
        if len(lot) > 1:
            print("  initiales partagées par %d personnes : %s -> %s"
                  % (len(lot), base,
                     ", ".join((base if i == 0 else "%s-%d" % (base, i))
                               + " (%d journées)" % len(f["d"])
                               for i, (_, f) in enumerate(lot))), file=sys.stderr)
        for i, (_, f) in enumerate(lot):
            ident = base if i == 0 else "%s-%d" % (base, i)
            p = {"id": ident, "cat": f["cat"], "d": f["d"]}
            if f["c"]:
                p["c"] = f["c"]
            if f.get("e"):
                p["e"] = f["e"]
            if f.get("postes"):
                p["postes"] = f["postes"]
            if f.get("ct"):
                p["ct"] = sorted(_borner(f["ct"], f["d"], annee),
                                 key=lambda x: (x.get("d") or "", x["l"]))
            gens[ident] = p
            cles_ident[ident] = f.get("nomcle")
            reels.setdefault(f.get("reel"), []).append(ident)

    # La polyvalence se rattache par le trigramme RÉEL — le client : « dans
    # le fichier Excel il faut prendre leur polyvalence sur leur vrai
    # trigramme ». Une personne que CORRECTIONS a renommée y figure sous
    # l'ancien, et c'est là qu'il faut aller la chercher : la ligne « JBY »
    # est celle de l'opérateur devenu JBA.
    #
    # Deux lignes peuvent porter le même trigramme réel — le classeur en a
    # deux pour GBT, Gluten et Chaudières, et ce sont deux personnes. On les
    # départage par le NOM, qui est écrit des deux côtés ; à défaut, on ne
    # devine pas, on le dit.
    for reel, lignes in polyvalence(cl, annuaire).items():
        # Une correction désigne directement l'identifiant d'arrivée ; le
        # trigramme réel, lui, passe par la table des correspondances.
        cibles = reels.get(reel) or ([reel] if reel in gens else [])
        if not cibles:
            print("  polyvalence : la ligne %s ne correspond à personne dans"
                  " l'horaire" % reel, file=sys.stderr)
            continue
        restantes, libres = [], list(cibles)
        for cle_lig, fiche in lignes:
            vise = [i for i in libres if cles_ident.get(i) == cle_lig]
            if len(vise) == 1:
                gens[vise[0]]["poly"] = fiche
                libres.remove(vise[0])
            else:
                restantes.append(fiche)
        if len(restantes) == 1 and len(libres) == 1:
            gens[libres[0]]["poly"] = restantes[0]
        elif restantes:
            print("  polyvalence : %d ligne(s) « %s » pour %d personne(s)"
                  " (%s) que le nom ne départage pas — %s. Les trancher dans"
                  " CORRECTIONS."
                  % (len(restantes), reel, len(libres), ", ".join(libres),
                     " ; ".join(str(f.get("ateliers")) for f in restantes)),
                  file=sys.stderr)
    # APRÈS la polyvalence : une correction peut ne servir qu'à cet onglet —
    # c'est le cas du nom écrit au long là-bas et en court dans l'horaire.
    # La signaler avant, c'était la déclarer inutilisée à tort.
    for empreinte, trig in CORRECTIONS.items():
        if empreinte not in utilisees and empreinte not in _corrections_polyvalence:
            print("  correction inutilisée : %s -> %s (le nom a changé dans le"
                  " classeur)" % (empreinte, trig), file=sys.stderr)

    _dire_regimes(gens)

    sortie = {"year": annee}
    sortie.update(metadata(cl))
    sortie["people"] = sorted(gens.values(), key=lambda p: (p["cat"], p["id"]))
    return sortie


def _dire_regimes(gens):
    """Dit les contrats dont le pourcentage ne va pas avec leur dispositif.

    Le client a décrit les trois dispositifs belges le 25/09/2026, et ils
    n'ont pas les mêmes régimes : le congé parental se prend en 1/5 ou en
    1/10, le crédit-temps en 1/5 ou en 1/2 — « le 9/10 n'est pas le régime
    général du crédit-temps 1/5 ». Le temps partiel, lui, est ce que le
    contrat dit, et rien ne lui est opposé ici.

    CE N'EST PAS UN FILTRE. Rien n'est refusé ni corrigé sur cette foi-là :
    la fraction reste celle que le classeur écrit, et c'est la sortie
    d'erreur qui parle. Un pourcentage hors régime est le plus souvent une
    faute de frappe du pied de feuille, mais il peut aussi être un régime
    qu'on ne connaît pas encore — et la deuxième hypothèse interdit de
    trancher à la place de qui écrit.

    Au 25/09/2026 elle ne dit rien : les 33 contrats codés du classeur
    tombent tous sur un régime légal — 21 « CP 10% », 2 « CP 20% », 7 « TP »
    et 3 « CT 20% ». C'est un garde-fou, pas un correctif.
    """
    for ident in sorted(gens):
        for c in gens[ident].get("ct") or []:
            if c.get("amb"):
                print("  contrat %s : « %s » — 100%% avec un code : suspension"
                      " complète (0,00) ou temps plein retrouvé (1,00) ? aucune"
                      " fraction posée" % (ident, c["txt"][:52]),
                      file=sys.stderr)
                continue
            connus = REGIMES.get(c.get("t"))
            if connus and c.get("pct") is not None and c["pct"] not in connus:
                print("  contrat %s : « %s » — %d%% n'est pas un régime de %s"
                      " (%s) ; la fraction est gardée telle quelle"
                      % (ident, c["txt"][:52], c["pct"], c["t"],
                         " ou ".join("%d%%" % x for x in connus)),
                      file=sys.stderr)

def entetes(cl):
    """Montre ce qui entoure les noms, colonne par colonne.

    Le convertisseur ne lit que la ligne des noms ; tout ce qui est écrit
    au-dessus ou en dessous est jeté sans être regardé. Or le poste tenu par
    chacun — meunerie, gluten, fermentation — est « tout près du trigramme »
    d'après le client, et le classeur ne sort jamais du poste de travail où
    il est. Plutôt que de deviner la bonne ligne, on les montre toutes, et
    on lit.

    Aucun nom complet n'est imprimé : les cellules de la ligne des noms sont
    remplacées par leurs initiales, comme partout ailleurs.
    """
    for feuille in FEUILLES:
        if feuille not in cl.feuilles:
            continue
        g = cl.grille(feuille)
        cols = [c for c in sorted(g.get(LIGNE_NOMS, {}))
                if c >= 3 and str(g[LIGNE_NOMS][c]).strip() not in ("", "0")]
        if not cols:
            continue
        print("── feuille « %s » — %d colonnes-personnes" % (feuille, len(cols)))
        for r in range(max(1, LIGNE_NOMS - 5), LIGNE_NOMS + 3):
            vals = []
            for c in cols[:8]:
                v = str(g.get(r, {}).get(c, "")).strip()
                if r == LIGNE_NOMS:
                    v = _initiales(v) or "?"
                vals.append((v[:14] or "·").ljust(14))
            marque = " ← noms" if r == LIGNE_NOMS else ""
            print("   l.%-3d %s%s" % (r, " ".join(vals), marque))
        print()


if __name__ == "__main__":
    if "--entetes" in sys.argv:
        entetes(Classeur(sys.argv[1]))
        sys.exit(0)
    pos = [a for a in sys.argv[1:] if not a.startswith("--")]
    src = pos[0]
    dst = pos[1] if len(pos) > 1 else "-"
    annee = int(pos[2]) if len(pos) > 2 else 2026
    data = convertir(src, annee)
    n = sum(len(p["d"]) for p in data["people"])
    k = sum(1 for p in data["people"] for e in p["d"].values() if len(e) > 2)
    print("%d personnes, %d journées, %d commentaires" % (len(data["people"]), n, k),
          file=sys.stderr)
    out = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    tol = ()
    for a in sys.argv[1:]:
        if a.startswith("--tolerer="):
            tol = tuple(_plier(x.strip()) for x in a.split("=", 1)[1].split(","))
    restes = garantie(out, _SURVEILLES, tol)
    if restes:
        print("\n%d reste(s) de nom dans la sortie — rien n'est écrit :" % len(restes),
              file=sys.stderr)
        for mot, ctx in restes[:30]:
            print("   …%s…" % ctx.replace("\n", " "), file=sys.stderr)
        print("\nSi l'un d'eux n'est pas un nom, relancer avec --tolerer=mot1,mot2"
              " APRÈS avoir lu le contexte.", file=sys.stderr)
        sys.exit(2)
    print("Aucun nom du classeur ne subsiste : vérifié sur la sortie.", file=sys.stderr)
    if dst == "-":
        print(out)
    else:
        open(dst, "w", encoding="utf-8").write(out)
