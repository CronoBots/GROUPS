#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Le classeur anonymisé recopié EN ENTIER dans un JSON, sans rien interpréter.

Le client, le 25/09/2026 : « toutes les cellules, commentaires, pages, lignes,
colonnes doivent être récupérés avec le fichier ; après le convertisseur tout
doit être dans la base de données, sauf les vrais noms et prénoms des
travailleurs ».

LE CONVERTISSEUR NE GARDE QUE CE QU'IL SAIT LIRE. C'est son rôle : il produit
l'horaire dont l'application se sert, journée par journée. Mais deux fois une
information s'est perdue parce qu'elle n'était pas dans les lignes qu'il
regardait — et une perte silencieuse est une perte qu'on ne corrige jamais.

Cet outil-ci ne lit rien : il RECOPIE. Ce qui n'est pas compris aujourd'hui
reste disponible demain, en JSON, sans avoir à rouvrir un classeur ni à
savoir lire du XML.

IL PART DU CLASSEUR DÉJÀ ANONYMISÉ, ET C'EST TOUT L'ARGUMENT. Anonymiser à
nouveau ici demanderait d'écrire une troisième fois des motifs de noms, donc
d'ouvrir un troisième trou. data/classeur-2026.xlsx est passé par
l'anonymiseur ET par son second contrôle indépendant. On recopie une source
propre plutôt que de nettoyer une source sale.

    python3 tools/exporter-classeur.py data/classeur-2026.xlsx \\
            data/classeur-2026-brut.json

CE QUE LE JSON PORTE — ET DEPUIS LE 26/09/2026, VRAIMENT TOUT. La première
version ne gardait que le texte des cellules, celui des commentaires et les
fusions. L'audit du 26/09 a mesuré ce qui tombait : le TYPE des valeurs (une
date sortait en « 46290.64 »), 13 637 formules, toute la mise en forme — dont
le BARRÉ de deux journées entières et de centaines de commentaires, qui dit
qu'une consigne a été annulée —, 262 lignes et 62 colonnes masquées, deux
feuilles cachées, les validations, les mises en forme conditionnelles, les
noms définis et les 25 boutons. Par feuille :

  etat            "visible" | "hidden"
  cellules        {adresse: texte}             — comme avant
  commentaires    {adresse: texte}             — le texte BRUT, sauts de ligne
                                                 compris (il était nettoyé)
  riches          {adresse: [[texte, "sui"]]}  — les morceaux d'un commentaire,
                                                 quand l'un est barré (s),
                                                 souligné (u) ou italique (i)
  fusions         ["A1:B2", …]                 — comme avant
  types           {adresse: "n"|"b"|"e"|"str"} — ce qui n'est pas du texte
  dates           {adresse: "AAAA-MM-JJ[THH:MM]"} — les nombres au format date
  formules        {adresse: "…" | {"f", "plage", "partage"} | {"partage": n}}
  styles          {ligne: [[colonne, nombre, index], …]} — index dans la table
                                                 `styles` du classeur, pour
                                                 les cellules non vides, ou
                                                 vides mais peintes ou barrées
  lignes_masquees, colonnes_masquees, lignes_groupees, colonnes_groupees
                  "3-5,9"
  volets, protegee, validations, mfc

Et pour le classeur : `styles` (la table ; écarts au style par défaut
seulement), `styles_base`, `noms`, `controles` (boutons et leur macro),
`modifie` — la date du classeur, et non l'heure de l'export : deux exports du
même fichier sont identiques octet pour octet.

UN ALLER-RETOUR LE PROUVE. Avant d'écrire, l'outil recompte dans le XML —
par un autre chemin que celui de l'export — les formules, les cellules
barrées et peintes, les commentaires et ceux qui ont un morceau barré, et
les compare au JSON. Un seul écart, et rien n'est écrit.

Le fichier produit n'est PAS chargé par l'application : elle continue de lire
data/horaire-2026.json, qui ne porte que ce dont elle se sert. Celui-ci est
une réserve — on y va chercher ce qu'on découvre avoir besoin.
"""
import datetime
import importlib.util
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def _convertisseur():
    """Réemployer la lecture du convertisseur plutôt que d'en écrire une autre.

    Deux lecteurs de xlsx dans le même dépôt finiraient par diverger, et c'est
    le second qui resterait en arrière — le projet en a la démonstration.
    """
    spec = importlib.util.spec_from_file_location(
        "cv", os.path.join(RACINE, "tools", "convertir-horaire.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# UN IDENTIFIANT DE CONNEXION N'EST PAS UN NOM, ET IL DÉSIGNE QUAND MÊME
# QUELQU'UN. L'anonymiseur les retire depuis le 26/09/2026 ; cette passe-ci
# reste en second rideau, sur le TEXTE seulement — jamais sur des octets de
# XML, où la forme se confond avec des couleurs. La règle vit dans le
# convertisseur et cet outil l'emprunte : un login n'est pas un nom, et il
# n'y a rien à vérifier par recoupement.
def _sans_login(t, cv):
    return cv.LOGIN.sub("(identifiant retiré)", t)


def _adresse(ligne, colonne):
    """(12, 3) -> « C12 »."""
    lettres, n = "", colonne
    while n > 0:
        n, r = divmod(n - 1, 26)
        lettres = chr(65 + r) + lettres
    return "%s%d" % (lettres, ligne)


def _plages(nombres):
    """[3, 4, 5, 9] -> « 3-5,9 »."""
    out, nombres = [], sorted(set(nombres))
    i = 0
    while i < len(nombres):
        j = i
        while j + 1 < len(nombres) and nombres[j + 1] == nombres[j] + 1:
            j += 1
        out.append(str(nombres[i]) if i == j else "%d-%d" % (nombres[i], nombres[j]))
        i = j + 1
    return ",".join(out)


# --- la mise en forme ----------------------------------------------------------
# On ne garde que ce qui PEUT porter un sens : le fond, la couleur et le style
# de l'écriture (gras, italique, souligné, BARRÉ), le format des nombres. Les
# bordures, l'alignement et les largeurs disent la présentation, pas le
# contenu — et doubleraient le fichier.

def _couleur(e):
    if e is None:
        return None
    if e.get("rgb"):
        return e.get("rgb")[-6:]
    if e.get("theme") is not None:
        t = e.get("tint")
        return "th%s%s" % (e.get("theme"), ("%+.2f" % float(t)) if t else "")
    if e.get("indexed") is not None:
        return "ix" + e.get("indexed")
    return None


def _drapeau(rp, tag):
    e = rp.find(M + tag) if rp is not None else None
    return e is not None and e.get("val", "1") not in ("0", "false", "none")


def _police(f):
    d = {}
    for t in ("b", "i", "strike"):
        if _drapeau(f, t):
            d[t] = 1
    u = f.find(M + "u")
    if u is not None and u.get("val", "single") != "none":
        d["u"] = u.get("val", "single")
    c = _couleur(f.find(M + "color"))
    if c:
        d["c"] = c
    return d


def _remplissage(f):
    p = f.find(M + "patternFill")
    if p is None or p.get("patternType") in (None, "none"):
        return None
    fg = _couleur(p.find(M + "fgColor"))
    return fg if p.get("patternType") == "solid" else "%s:%s" % (p.get("patternType"), fg)


# Les formats de nombre prédéfinis qui sont des dates (ECMA-376, 18.8.30).
_DATES_PREDEFINIES = set(range(14, 23)) | set(range(45, 48))


class Styles:
    def __init__(self, z):
        st = ET.fromstring(z.read("xl/styles.xml"))
        self.fmts = {int(n.get("numFmtId")): n.get("formatCode") for n in st.iter(M + "numFmt")}
        self.polices = [_police(f) for f in st.find(M + "fonts")]
        self.fonds = [_remplissage(f) for f in st.find(M + "fills")]
        self.xfs = list(st.find(M + "cellXfs"))
        self.dxfs = []
        dx = st.find(M + "dxfs")
        for d in (dx if dx is not None else []):
            o = {}
            f = d.find(M + "font")
            if f is not None:
                o.update(_police(f))
            fl = d.find(M + "fill/" + M + "patternFill")
            if fl is not None:
                c = _couleur(fl.find(M + "bgColor")) or _couleur(fl.find(M + "fgColor"))
                if c:
                    o["fond"] = c
            self.dxfs.append(o)
        self.table, self._idx, self._cache = [], {}, {}
        self.base = self._brut(0)

    def _brut(self, s):
        x = self.xfs[s]
        d = dict(self.polices[int(x.get("fontId", 0))])
        f = self.fonds[int(x.get("fillId", 0))]
        if f:
            d["fond"] = f
        nf = int(x.get("numFmtId", 0))
        if nf:
            d["fmt"] = self.fmts.get(nf, nf)
        return d

    def est_date(self, s):
        nf = int(self.xfs[int(s or 0)].get("numFmtId", 0))
        if nf in _DATES_PREDEFINIES:
            return True
        # un format personnalisé est une date s'il porte des jours, mois,
        # années ou heures hors des guillemets et des crochets — et pas de 0,
        # qui dirait un nombre
        code = re.sub(r'"[^"]*"|\[[^\]]*\]|\\.', "", str(self.fmts.get(nf, "")))
        return bool(re.search(r"[dmyhs]", code, re.I)) and "0" not in code

    def index(self, s):
        """L'index du style de la cellule dans la table, ou None s'il ne
        s'écarte pas du style par défaut."""
        s = int(s or 0)
        if s in self._cache:
            return self._cache[s]
        d = self._brut(s)
        ecart = {k: v for k, v in d.items() if self.base.get(k) != v}
        ecart.update({k: None for k in self.base if k not in d})
        if not ecart:
            self._cache[s] = None
            return None
        cle = json.dumps(ecart, sort_keys=True)
        if cle not in self._idx:
            self._idx[cle] = len(self.table)
            self.table.append(ecart)
        self._cache[s] = self._idx[cle]
        return self._cache[s]


def _date_iso(serie):
    """Un numéro de série Excel (système 1900) en date ISO."""
    v = float(serie)
    jour = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=v)
    return jour.strftime("%Y-%m-%dT%H:%M" if v % 1 else "%Y-%m-%d")


def _runs(cm):
    """Les morceaux d'un commentaire : [texte] ou [texte, drapeaux]."""
    morceaux = cm.findall(M + "text/" + M + "r")
    if not morceaux:
        return [["".join(x.text or "" for x in cm.iter(M + "t"))]]
    out = []
    for r in morceaux:
        t = "".join(x.text or "" for x in r.iter(M + "t"))
        if not t:
            continue
        rp = r.find(M + "rPr")
        fl = "".join(k for k, tag in (("s", "strike"), ("u", "u"), ("i", "i"))
                     if _drapeau(rp, tag))
        out.append([t, fl] if fl else [t])
    return out


def _parties_de(z, chemin_feuille):
    """Les commentaires et les dessins VML rattachés à une feuille."""
    rp = chemin_feuille.replace("worksheets/", "worksheets/_rels/") + ".rels"
    out = {"commentaires": None, "vml": []}
    if rp not in z.namelist():
        return out
    for r in ET.fromstring(z.read(rp)):
        cible = r.get("Target") or ""
        chemin = ("xl/" + cible.replace("../", "")).replace("xl/xl/", "xl/")
        if chemin not in z.namelist():
            continue
        if "comments" in cible:
            out["commentaires"] = chemin
        elif "vmlDrawing" in cible:
            out["vml"].append(chemin)
    return out


def exporter(chemin, cv):
    cl = cv.Classeur(chemin)
    z = cl.z
    sty = Styles(z)
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    ordre = [s.get("name") for s in wb.find(M + "sheets")]
    etats = {s.get("name"): s.get("state") or "visible" for s in wb.find(M + "sheets")}
    feuilles, controles = {}, []

    for nom in cl.feuilles:
        # SANS RECOPIE DES FUSIONS : on veut le fichier tel qu'il est écrit.
        # Seule la case en haut à gauche d'une fusion porte la valeur ; les
        # étendues sont exportées à part, de sorte que rien ne se perd et que
        # rien ne s'invente.
        cl._grilles.pop(nom, None)
        g = cl.grille(nom, fusions=())
        cellules = {}
        for ligne in g:
            for col, val in g[ligne].items():
                cellules[_adresse(ligne, col)] = _sans_login(val, cv)

        racine = ET.fromstring(z.read(cl.feuilles[nom]))
        types, dates, formules, styles = {}, {}, {}, {}
        for c in racine.iter(M + "c"):
            a = c.get("r")
            t = c.get("t") or "n"
            v = c.find(M + "v")
            if a in cellules and t not in ("s", "inlineStr"):
                types[a] = t
                if t == "n" and v is not None and v.text and sty.est_date(c.get("s")):
                    try:
                        dates[a] = _date_iso(v.text)
                    except (ValueError, OverflowError):
                        pass
            fo = c.find(M + "f")
            if fo is not None:
                if fo.get("t") == "shared" and not (fo.text or "").strip():
                    formules[a] = {"partage": int(fo.get("si"))}
                elif fo.get("t") or fo.get("ref"):
                    o = {"f": fo.text or "", "plage": fo.get("ref")}
                    if fo.get("si") is not None:
                        o["partage"] = int(fo.get("si"))
                    formules[a] = o
                else:
                    formules[a] = fo.text or ""
            i = sty.index(c.get("s"))
            if i is None:
                continue
            e = sty.table[i]
            if a in cellules or e.get("fond") or e.get("strike"):
                m = re.match(r"([A-Z]+)(\d+)$", a)
                styles.setdefault(int(m.group(2)), []).append((cv._colnum(m.group(1)), i))
        # des lignes : [[colonne, nombre, index], …] par suites contiguës
        rle = {}
        for ligne in sorted(styles):
            out = []
            for col, i in sorted(styles[ligne]):
                if out and out[-1][2] == i and out[-1][0] + out[-1][1] == col:
                    out[-1][1] += 1
                else:
                    out.append([col, 1, i])
            rle[str(ligne)] = out

        lm, lg, cm_, cg = [], [], [], []
        for row in racine.iter(M + "row"):
            if row.get("hidden") in ("1", "true"):
                lm.append(int(row.get("r")))
            if row.get("outlineLevel"):
                lg.append(int(row.get("r")))
        for col in racine.iter(M + "col"):
            for n in range(int(col.get("min")), int(col.get("max")) + 1):
                if col.get("hidden") in ("1", "true"):
                    cm_.append(n)
                if col.get("outlineLevel"):
                    cg.append(n)

        fiche = {
            "etat": etats.get(nom, "visible"),
            "cellules": cellules,
            "fusions": [m.get("ref") for m in racine.iter(M + "mergeCell")
                        if ":" in (m.get("ref") or "")],
            "types": types, "dates": dates, "formules": formules, "styles": rle,
            "lignes_masquees": _plages(lm), "colonnes_masquees": _plages(cm_),
            "lignes_groupees": _plages(lg), "colonnes_groupees": _plages(cg),
            "protegee": racine.find(M + "sheetProtection") is not None,
            "validations": [{"plages": d.get("sqref"), "type": d.get("type"),
                             "operateur": d.get("operator"),
                             "formule1": d.findtext(M + "formula1"),
                             "formule2": d.findtext(M + "formula2")}
                            for d in racine.iter(M + "dataValidation")],
            "mfc": [{"plages": cf.get("sqref"), "type": r.get("type"),
                     "operateur": r.get("operator"), "priorite": int(r.get("priority", 0)),
                     "formules": [x.text for x in r.findall(M + "formula")],
                     "style": sty.dxfs[int(r.get("dxfId"))] if r.get("dxfId") else None}
                    for cf in racine.iter(M + "conditionalFormatting")
                    for r in cf.findall(M + "cfRule")],
        }
        pane = racine.find(".//" + M + "pane")
        if pane is not None:
            fiche["volets"] = {k: pane.get(k) for k in ("xSplit", "ySplit", "topLeftCell", "state")
                               if pane.get(k)}

        # LES COMMENTAIRES SE LISENT DANS LE XML, TELS QU'ILS SONT ÉCRITS. La
        # première version passait par la lecture du convertisseur, qui les
        # NETTOIE — têtes de signature retirées, sauts de ligne écrasés en
        # espaces : des milliers de commentaires sur plusieurs lignes dans le
        # classeur, aucun dans le JSON. Recopier, c'est ne rien retoucher.
        commentaires, riches = {}, {}
        parties = _parties_de(z, cl.feuilles[nom])
        if parties["commentaires"]:
            for cm in ET.fromstring(z.read(parties["commentaires"])).iter(M + "comment"):
                runs = [[_sans_login(r[0], cv)] + r[1:] for r in _runs(cm)]
                txt = "".join(r[0] for r in runs)
                if not txt.strip():
                    continue
                commentaires[cm.get("ref")] = txt
                if any(len(r) > 1 for r in runs):
                    riches[cm.get("ref")] = runs
        fiche["commentaires"] = commentaires
        fiche["riches"] = riches
        for vml in parties["vml"]:
            x = z.read(vml).decode("utf-8", "replace")
            for sh in re.findall(r"<v:shape .*?</v:shape>", x, re.S):
                mac = re.search(r"<x:FmlaMacro>([^<]*)", sh)
                if mac:
                    boite = re.search(r"<v:textbox[^>]*>(.*?)</v:textbox>", sh, re.S)
                    txt = re.sub(r"<[^>]+>", "", boite.group(1) if boite else "")
                    controles.append({"feuille": nom, "texte": " ".join(txt.split()),
                                      "macro": mac.group(1)})
        feuilles[nom] = fiche

    noms = []
    dn = wb.find(M + "definedNames")
    for d in (dn if dn is not None else []):
        o = {"nom": d.get("name"), "valeur": d.text}
        if d.get("localSheetId") is not None:
            o["feuille"] = ordre[int(d.get("localSheetId"))]
        noms.append(o)
    modifie = ""
    if "docProps/core.xml" in z.namelist():
        m = re.search(rb"<dcterms:modified[^>]*>([^<]*)<", z.read("docProps/core.xml"))
        modifie = m.group(1).decode() if m else ""
    return {
        "source": os.path.basename(chemin),
        "modifie": modifie,
        "styles": sty.table,
        "styles_base": sty.base,
        "noms": noms,
        "controles": controles,
        "feuilles": feuilles,
    }


def _style_de(fiche, table, adresse):
    """Le style d'une adresse, relu depuis le JSON."""
    m = re.match(r"([A-Z]+)(\d+)$", adresse)
    col = 0
    for ch in m.group(1):
        col = col * 26 + ord(ch) - 64
    for c, n, i in fiche["styles"].get(m.group(2), []):
        if c <= col < c + n:
            return table[i]
    return {}


def aller_retour(cl, out):
    """RECOMPTER DANS LE XML, PAR UN AUTRE CHEMIN, ET COMPARER AU JSON.

    L'export parcourt l'arbre XML ; ce contrôle relit les octets par des
    motifs, résout lui-même les styles barrés et peints, et relit le JSON
    produit — les styles par leur codage en suites, les commentaires par
    leurs morceaux. Un écart dit qu'un morceau n'a pas fait le voyage.
    """
    z = cl.z
    st = z.read("xl/styles.xml").decode("utf-8", "replace")
    bloc = lambda nom: re.search(r"<%s\b[^>]*>(.*?)</%s>" % (nom, nom), st, re.S).group(1)
    polices = re.findall(r"<font\b[^>]*/>|<font\b[^>]*>.*?</font>", bloc("fonts"), re.S)
    fonds = re.findall(r"<fill\b[^>]*/>|<fill\b[^>]*>.*?</fill>", bloc("fills"), re.S)
    xfs = re.findall(r"<xf\b[^>]*/>|<xf\b[^>]*>.*?</xf>", bloc("cellXfs"), re.S)

    def _attr(x, a):
        m = re.search(r'\b%s="(\d+)"' % a, x)
        return int(m.group(1)) if m else 0
    barre = set(i for i, x in enumerate(xfs)
                if re.search(r'<strike(?:\s+val="(?:1|true)")?\s*/>', polices[_attr(x, "fontId")]))
    peint = set(i for i, x in enumerate(xfs)
                if re.search(r'patternType="(?!none")', fonds[_attr(x, "fillId")]))
    base_barre, base_peint = 0 in barre, 0 in peint

    ecarts = []
    for nom, fiche in out["feuilles"].items():
        xml = z.read(cl.feuilles[nom]).decode("utf-8", "replace")
        # les formules
        n = len(re.findall(r"<f[\s>/]", xml))
        if n != len(fiche["formules"]):
            ecarts.append("%s : %d formules dans le XML, %d dans le JSON"
                          % (nom, n, len(fiche["formules"])))
        # les cellules peintes (toutes) et barrées (non vides, ou peintes)
        x_peintes = x_barrees = 0
        for a, s in re.findall(r'<c r="([A-Z]+\d+)"[^>]*?\bs="(\d+)"', xml):
            s = int(s)
            if s in peint and not base_peint:
                x_peintes += 1
            if s in barre and not base_barre and (a in fiche["cellules"] or s in peint):
                x_barrees += 1
        j_peintes = sum(n for cases in fiche["styles"].values() for c, n, i in cases
                        if out["styles"][i].get("fond"))
        j_barrees = sum(n for cases in fiche["styles"].values() for c, n, i in cases
                        if out["styles"][i].get("strike"))
        if (x_peintes, x_barrees) != (j_peintes, j_barrees):
            ecarts.append("%s : peintes/barrées %d/%d dans le XML, %d/%d dans le JSON"
                          % (nom, x_peintes, x_barrees, j_peintes, j_barrees))
    # les commentaires, et ceux qui portent un morceau barré
    x_cm = x_barres = 0
    for n in z.namelist():
        if re.search(r"comments\d*\.xml$", n):
            t = z.read(n).decode("utf-8", "replace")
            for c in re.findall(r"<comment\b.*?</comment>", t, re.S):
                if "".join(re.findall(r"<t[^>]*>([^<]*)</t>", c)).strip():
                    x_cm += 1
                    for r in re.findall(r"<r>(.*?)</r>", c, re.S):
                        if (re.search(r'<strike(?:\s+val="(?:1|true)")?\s*/>', r)
                                and "".join(re.findall(r"<t[^>]*>([^<]*)</t>", r))):
                            x_barres += 1
                            break
    j_cm = sum(len(f["commentaires"]) for f in out["feuilles"].values())
    j_barres = sum(1 for f in out["feuilles"].values() for runs in f["riches"].values()
                   if any(len(r) > 1 and "s" in r[1] for r in runs))
    if (x_cm, x_barres) != (j_cm, j_barres):
        ecarts.append("commentaires / avec morceau barré : %d/%d dans le XML, %d/%d dans le JSON"
                      % (x_cm, x_barres, j_cm, j_barres))
    return ecarts


def main():
    if len(sys.argv) < 2:
        sys.stderr.write(__doc__)
        return 2
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        RACINE, "data", "classeur-2026-brut.json")
    cv = _convertisseur()
    out = exporter(src, cv)
    ecarts = aller_retour(cv.Classeur(src), out)
    if ecarts:
        sys.stderr.write("L'ALLER-RETOUR ÉCHOUE — rien n'est écrit :\n")
        for e in ecarts:
            sys.stderr.write("   %s\n" % e)
        return 1
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    fs = list(out["feuilles"].values())
    print("%d feuille(s) · %d cellule(s) · %d commentaire(s) · %d fusion(s)"
          % (len(fs), sum(len(v["cellules"]) for v in fs),
             sum(len(v["commentaires"]) for v in fs), sum(len(v["fusions"]) for v in fs)))
    print("%d formule(s) · %d date(s) · %d commentaire(s) riche(s) · %d style(s) · "
          "%d bouton(s) · %d nom(s) définis"
          % (sum(len(v["formules"]) for v in fs), sum(len(v["dates"]) for v in fs),
             sum(len(v["riches"]) for v in fs), len(out["styles"]),
             len(out["controles"]), len(out["noms"])))
    print("aller-retour : formules, cellules peintes et barrées, commentaires"
          " et morceaux barrés concordent avec le XML")
    print("%s — %.1f Mo" % (dst, os.path.getsize(dst) / 1048576.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
