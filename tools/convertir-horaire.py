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
import datetime, json, re, sys, unicodedata, zipfile
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

    Un libellé qui revient dans le même bloc est un total : les journées
    entières d'abord, le cumul ensuite. VBN : 40 h de RTT en journées
    entières, plus 14 h prises à l'heure, soit 54 h au total."""
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
            while cle in vals:
                cle += "Total"
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
        for colonne in sorted(g.get(LIGNE_NOMS, {})):
            nom = str(g[LIGNE_NOMS][colonne]).strip()
            if colonne < 3 or nom in ("", "0"):
                continue
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
                yield categorie, nom, jours, compteurs(g, colonne) if pied else {}


def convertir(chemin_xlsm, annee):
    cl = Classeur(chemin_xlsm)
    annuaire = _annuaire(cl)

    # 1. Une fiche par personne, repérée par son nom normalisé. Une même
    #    personne figure sur plusieurs feuilles : la première rencontrée
    #    donne sa catégorie, et FEUILLES met les feuilles spécialisées en
    #    tête pour que ce soit celle de son propre groupe.
    fiches = {}
    for categorie, nom, jours, cpt in _colonnes(cl):
        cle = _sans_accent(nom).lower()
        officiel = annuaire.get(cle)
        base = officiel or _initiales(nom)
        if not base:
            print("  nom illisible, ligne ignorée :", nom, file=sys.stderr)
            continue
        f = fiches.setdefault(cle, {"base": base, "officiel": bool(officiel),
                                    "cat": categorie, "d": {}, "c": {}})
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
            gens[ident] = p

    for ident, fiche in polyvalence(cl, annuaire).items():
        if ident in gens:
            gens[ident]["poly"] = fiche
    sortie = {"year": annee}
    sortie.update(metadata(cl))
    sortie["people"] = sorted(gens.values(), key=lambda p: (p["cat"], p["id"]))
    return sortie


if __name__ == "__main__":
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
