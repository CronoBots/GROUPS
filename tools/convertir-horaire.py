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

# « Nom, Prénom: », « Nom, Prénom (external): », « RT01386: »
AUTEUR = re.compile(r"(?:^|\s)(?:[A-ZÉÈÀ][\wÉÈÀéèàêç'-]+,\s*[A-ZÉÈÀ][\wÉÈÀéèàêç'-]+"
                    r"(?:\s*\([^)]*\))?|[Rr][Tt]\d{4,6}|Auteur)\s*:\s*")

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
    # l'équipe 5 garde CDE et GBT, celui de l'équipe 3 garde PDR
    "a056b3f782": "CHD",   # l'autre CDE, en équipe 4
    "531e312a2e": "GBO",   # l'autre GBT, en équipe 4
    "0ad0bc1dfe": "PDF",   # l'autre PDR, en équipe 1
    # CDE figure aussi dans l'onglet Personnel sous un troisième nom ; le
    # client confirme qu'il revient à celui de l'équipe 5. L'inscrire ici
    # fait de ce maintien une décision, et non le hasard d'un calcul.
    "e829c2c542": "CDE",
}


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

    def _shared(self):
        if "xl/sharedStrings.xml" not in self.z.namelist():
            return []
        return ["".join(t.text or "" for t in si.iter('{%s}t' % M))
                for si in ET.fromstring(self.z.read("xl/sharedStrings.xml"))]

    def grille(self, feuille):
        """{ligne: {colonne: texte}}"""
        out = {}
        for c in ET.fromstring(self.z.read(self.feuilles[feuille])).iter('{%s}c' % M):
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
            for cm in ET.fromstring(self.z.read(chemin)).iter('{%s}comment' % M):
                txt = " ".join("".join(t.text or "" for t in cm.iter('{%s}t' % M)).split())
                txt = AUTEUR.sub(" ", txt).strip(" .;:")
                txt = " ".join(txt.split())
                if not txt:
                    continue
                ref = cm.get('ref')
                lettres = re.match(r'([A-Z]+)', ref).group(1)
                out[(int(re.search(r'(\d+)', ref).group(1)), _colnum(lettres))] = txt
        return out


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
    famille. « Renard V » donne VBN, « Gilbert V. » donne VGG, « Renard JJ »
    donne JBI. Le prénom est la partie d'une ou deux lettres."""
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
    for feuille in FEUILLES:
        if feuille not in cl.feuilles:
            continue
        g = cl.grille(feuille)
        leg = {str(g[r][1]).strip(): str(g[r][2]).strip()
               for r in range(4, 9) if r in g and 1 in g[r] and 2 in g[r]}
        if leg:
            out["legende"] = leg
            break
    if "Polyvalence" in cl.feuilles:
        g = cl.grille("Polyvalence")
        out["ateliers"] = [str(g[3][c]).strip()
                           for c in sorted(g.get(3, {})) if c >= 6]
    return out


def polyvalence(cl, annuaire):
    """L'onglet « Polyvalence » : le degré de chacun et les ateliers qu'il
    peut tenir. Il porte matricule, nom et prénom en clair — rien de tout
    cela ne sort d'ici, seul l'identifiant à trois lettres est conservé."""
    if "Polyvalence" not in cl.feuilles:
        return {}
    g = cl.grille("Polyvalence")
    noms = {c: str(g[3][c]).strip() for c in sorted(g.get(3, {})) if c >= 6}
    out = {}
    for r in sorted(g):
        if r < 5:
            continue
        famille, prenom = str(g[r].get(2, "")).strip(), str(g[r].get(3, "")).strip()
        if not famille or not prenom:
            continue
        cand = "%s %s." % (famille.title(), prenom[0].upper())
        ident = annuaire.get(_sans_accent(cand).lower()) or _initiales(cand)
        if not ident:
            continue
        ateliers = [noms[c] for c in noms if g[r].get(c)]
        fiche = {}
        if g[r].get(4):
            fiche["degre"] = str(g[r][4]).strip()
        if ateliers:
            fiche["ateliers"] = ateliers
        if fiche:
            out[ident] = fiche
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


def _colonnes(cl):
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
        for colonne in sorted(g.get(LIGNE_NOMS, {})):
            nom = str(g[LIGNE_NOMS][colonne]).strip()
            if colonne < 3 or nom in ("", "0"):
                continue
            entete = []
            for r in list(range(1, LIGNE_NOMS)) + list(range(LIGNE_NOMS + 1, premier_jour)):
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
            jours = {}
            for m, r0 in mois.items():
                for d in range(1, 32):
                    r = r0 + d - 1
                    if str(g.get(r, {}).get(COL_JOUR, "")) != str(d):
                        continue
                    cell = g.get(r, {}).get(colonne, "")
                    annot = g.get(r, {}).get(colonne + 1, "")
                    com = cm.get((r, colonne), "") or cm.get((r, colonne + 1), "")
                    if not (cell or annot or com):
                        continue
                    e = [cell, annot, com]
                    while e and not e[-1]:
                        e.pop()
                    jours["%02d%02d" % (m, d)] = e
            if jours:
                yield (categorie, nom, jours,
                       compteurs(g, colonne) if pied else {}, entete,
                       feuille, poste, _lettre(colonne))


def convertir(chemin_xlsm, annee):
    cl = Classeur(chemin_xlsm)
    annuaire = _annuaire(cl)

    # 1. Une fiche par personne, repérée par son nom normalisé. Une même
    #    personne figure sur plusieurs feuilles : la première rencontrée
    #    donne sa catégorie, et FEUILLES met les feuilles spécialisées en
    #    tête pour que ce soit celle de son propre groupe.
    fiches, utilisees, noms = {}, set(), {}
    for categorie, nom, jours, cpt, entete, feuille, poste, col in _colonnes(cl):
        cle = _sans_accent(nom).lower()
        noms[cle] = nom
        corrige = CORRECTIONS.get(_empreinte(cle))
        officiel = corrige or annuaire.get(cle)
        base = officiel or _initiales(nom)
        if not base:
            print("  nom illisible, ligne ignorée :", nom, file=sys.stderr)
            continue
        utilisees.add(_empreinte(cle))
        f = fiches.setdefault(cle, {"base": base, "officiel": bool(officiel),
                                    "cat": categorie, "d": {}, "c": {}, "e": [],
                                    "postes": {}})
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

    for empreinte, trig in CORRECTIONS.items():
        if empreinte not in utilisees:
            print("  correction inutilisée : %s -> %s (le nom a changé dans le"
                  " classeur)" % (empreinte, trig), file=sys.stderr)

    par_base = {}
    for cle, f in fiches.items():
        par_base.setdefault(f["base"], []).append((cle, f))

    gens = {}
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
            gens[ident] = p

    for ident, fiche in polyvalence(cl, annuaire).items():
        if ident in gens:
            gens[ident]["poly"] = fiche
    sortie = {"year": annee}
    sortie.update(metadata(cl))
    sortie["people"] = sorted(gens.values(), key=lambda p: (p["cat"], p["id"]))
    return sortie


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
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else "-"
    annee = int(sys.argv[3]) if len(sys.argv) > 3 else 2026
    data = convertir(src, annee)
    n = sum(len(p["d"]) for p in data["people"])
    k = sum(1 for p in data["people"] for e in p["d"].values() if len(e) > 2)
    print("%d personnes, %d journées, %d commentaires" % (len(data["people"]), n, k),
          file=sys.stderr)
    out = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    if dst == "-":
        print(out)
    else:
        open(dst, "w", encoding="utf-8").write(out)
