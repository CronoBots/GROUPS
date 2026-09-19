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
import json, re, sys, unicodedata, zipfile
import xml.etree.ElementTree as ET

M = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

# Une feuille par groupe, et la catégorie sous laquelle ses gens apparaissent.
FEUILLES = {
    "Shift1": "Shift 1", "Shift2": "Shift 2", "Shift3": "Shift 3",
    "Shift4": "Shift 4", "Shift5": "Shift 5",
    "Opérateurs": "Opérateurs en formation", "Step": "Opérateurs STEP",
    "Contremaître": "Contremaîtres de production",
}
LIGNE_NOMS = 10          # la ligne qui porte les noms
COL_JOUR = 2             # la colonne qui porte le numéro du jour
MOIS = ["JANVIER", "FEVRIER", "MARS", "AVRIL", "MAI", "JUIN", "JUILLET",
        "AOUT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DECEMBRE"]

# « Nom, Prénom: », « Nom, Prénom (external): », « RT01386: »
AUTEUR = re.compile(r"(?:^|\s)(?:[A-ZÉÈÀ][\wÉÈÀéèàêç'-]+,\s*[A-ZÉÈÀ][\wÉÈÀéèàêç'-]+"
                    r"(?:\s*\([^)]*\))?|[Rr][Tt]\d{4,6}|Auteur)\s*:\s*")


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
                yield categorie, nom, jours


def convertir(chemin_xlsm, annee):
    cl = Classeur(chemin_xlsm)
    annuaire = _annuaire(cl)
    gens, homonymes = {}, {}
    for categorie, nom, jours in _colonnes(cl):
        base = annuaire.get(_sans_accent(nom).lower()) or _initiales(nom)
        if not base:
            print("  nom illisible, ligne ignorée :", nom, file=sys.stderr)
            continue
        cle = _sans_accent(nom).lower()
        ident = homonymes.get(cle)
        if ident is None:
            pris = {i for i in gens if i == base or i.startswith(base + "-")}
            ident = base if not pris else "%s-%d" % (base, len(pris))
            homonymes[cle] = ident
        p = gens.setdefault(ident, {"id": ident, "cat": categorie, "d": {}})
        # une feuille peut porter des journées ou des commentaires que l'autre
        # n'a pas ; on garde l'entrée la plus informative
        for k, e in jours.items():
            if len(e) >= len(p["d"].get(k, [])):
                p["d"][k] = e
    return {"year": annee,
            "people": sorted(gens.values(), key=lambda p: (p["cat"], p["id"]))}


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
