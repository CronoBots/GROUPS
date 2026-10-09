#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Du classeur RH « Suivi des recyclages sur poste de production » reçu du
client à ce que l'application lit — en UNE commande, et rien n'est installé
tant qu'une porte reste fermée.

    python3 tools/mettre-a-jour-recyclage.py /chemin/Suivi_recyclages.xlsx            # à blanc
    python3 tools/mettre-a-jour-recyclage.py /chemin/Suivi_recyclages.xlsx --installer

POURQUOI CET OUTIL EXISTE. Le 06/10/2026 ce petit classeur a été lu À LA MAIN,
et deux fois de travers : d'abord un seul poste sur trois (une seule ligne
d'en-tête relue), puis — corrigé — la colonne « Contremaître » des adjoints
FUSIONNÉE avec « Centrale thermique », donnant des chaudières à 10 là où le
classeur n'en compte que 5 + 5 recyclages contremaître. Le client, le
07/10/2026 : « mets en place exactement la même chose que pour le classeur
horaire, et enregistre la marche à suivre pour ne JAMAIS passer à côté ». Le
voici : la lecture n'est plus jamais faite à la main, elle passe par des
PORTES qui auraient arrêté chacune de ces deux erreurs.

CE QUE LE CLASSEUR CONTIENT. Une feuille « Suivi Polyvalence » faite de
SECTIONS empilées. Chaque section a sa ligne d'en-tête (« Nom | Prénom |
Degré… | recyclage restant | <POSTE> … »), puis une ligne « J-1 … J-n » qui
donne la LARGEUR de chaque poste (n = l'objectif : 10 pour un opérateur, 5
pour un adjoint), puis les personnes. Chaque cellule sous un poste porte la
DATE d'un recyclage fait ; le nombre de recyclages d'un poste = le nombre de
cellules remplies. La section des adjoints porte une colonne de plus,
« Contremaître » (les recyclages faits en tant que contremaître).

LES PORTES, dans l'ordre — la première qui échoue arrête tout :

  1. LECTURE : la feuille s'ouvre, ses sections se repèrent, chaque poste a un
     nom connu et une largeur ;
  2. TRIGRAMMES : chaque personne reçoit son trigramme (convention maison,
     la MÊME que l'horaire via convertir-horaire._initiales), unique, et qui
     correspond à quelqu'un de data/horaire-%d.json — sinon le classeur et
     l'application ne parlent pas des mêmes gens ;
  3. BORNES : aucun compte de poste ne dépasse la largeur de sa colonne.
     C'est la porte qui ferme le jour où « Contremaître » est recollé à
     « Centrale thermique » : chaudières à 10 dans une colonne large de 5 ;
  4. INTÉGRALITÉ : toute cellule-date d'une ligne de personne est comptée une
     fois et une seule — la somme des comptes égale le total des cellules
     remplies, rien n'est perdu ni compté deux fois ;
  5. COHÉRENCE : pour chacun, « restant » ≥ 0 et (fait + restant) est un
     multiple de 5 au moins égal à « fait » — l'invariant du classeur ;
  6. ANONYMAT : la sortie (et le brut) ne portent AUCUN nom ni prénom du
     classeur.

Puis, le client le 09/10/2026 : « exactement la même démarche d'anonymat et
de récupération de toutes les infos » que pour l'horaire :

  7. COPIE ANONYMISÉE : l'archive recopiée, colonne A des personnes = le
     trigramme, colonne B vidée, leurs chaînes partagées vidées, auteur et
     dernier modificateur retirés. GARANTIE : la copie est relue en entier,
     un seul mot de nom et elle est détruite ;
  8. SECOND CONTRÔLE : tools/verifier-anonymat.py source → copie, qui
     n'emprunte rien à l'anonymiseur ;
  9. FIDÉLITÉ : hors des colonnes de noms des personnes, la copie ne
     diffère de la source sur AUCUNE cellule, d'aucune feuille ;
 10. EXPORT : tools/exporter-classeur.py recopie la copie ENTIÈRE en JSON
     (cellules, types, formules, styles, fusions, lignes masquées…) avec
     son aller-retour ;
 11. INTÉGRALITÉ : ce classeur entier, lu par un autre chemin (le trigramme
     ÉCRIT en colonne A de la copie, et non recalculé), redonne pour chaque
     personne et chaque poste les mêmes comptes et les mêmes dates que la
     sortie.

À blanc, l'outil s'arrête après les portes et imprime CE QUI CHANGERAIT par
rapport au recyclage installé — à LIRE, et à dire au client. Avec
--installer, et seulement si les onze portes sont ouvertes : data/recyclages-%d.json
est remplacé, le brut (trigrammes seuls, jamais de nom) est écrit à côté, la
copie anonymisée et son export entier vont dans data/ (hors dépôt, la
réserve), `V` est incrémenté dans sw.js, et le garde-fou du dépôt passe sur
le résultat. S'il échoue, les fichiers d'avant sont remis en place depuis
leur copie.

Restent à faire à la main, et l'outil le rappelle : relire le rapport,
tester dans un navigateur, committer.
"""
import datetime
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTILS = os.path.join(RACINE, "tools")
M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

# Poste du classeur -> clé de l'application. « Terrain arrière » n'est pas un
# poste (règle écrite dans l'onglet REGLES du classeur) : il n'apparaît pas.
NOM_POSTE = {
    "MEUNERIE": "meun", "GLUTEN": "glut", "FERMENTATION": "ferm",
    "DISTILLATION": "dist", "CENTRALE THERMIQUE": "chau", "STEP": "step",
    "CONTREMAITRE": "cm", "CONTREMAÎTRE": "cm",
}
LIBELLES = {
    "meun": "Meunerie", "glut": "Gluten", "ferm": "Fermentation",
    "dist": "Distillation", "chau": "Chaudieres (Centrale thermique)",
    "step": "STEP",
}
CLES = ["meun", "glut", "ferm", "dist", "chau", "step", "cm"]


def _convert():
    spec = importlib.util.spec_from_file_location(
        "cv", os.path.join(OUTILS, "convertir-horaire.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _colnum(ref):
    c = re.match(r"[A-Z]+", ref).group()
    n = 0
    for ch in c:
        n = n * 26 + (ord(ch) - 64)
    return n


def lire_feuille(path):
    """Rend (cellules, feuille_data) : cellules[(row,col)] = texte (non vide),
    pour la feuille « Suivi Polyvalence » du classeur."""
    z = zipfile.ZipFile(path)
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(M + "si"):
            ss.append("".join(t.text or "" for t in si.iter(M + "t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid2target = {}
    for rel in rels:
        rid2target[rel.get("Id")] = rel.get("Target")
    RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    cible = None
    for sh in wb.findall(M + "sheets/" + M + "sheet"):
        if "polyvalence" in (sh.get("name") or "").lower():
            tgt = rid2target.get(sh.get(RNS + "id"))
            cible = "xl/" + tgt if not tgt.startswith("xl/") else tgt
    if not cible:
        raise ValueError("feuille « Suivi Polyvalence » introuvable")
    cells = {}
    for row in ET.fromstring(z.read(cible)).iter(M + "row"):
        rn = int(row.get("r"))
        for c in row.findall(M + "c"):
            ref = c.get("r")
            t = c.get("t")
            v = c.find(M + "v")
            isv = c.find(M + "is")
            val = ""
            if t == "s" and v is not None:
                val = ss[int(v.text)]
            elif isv is not None:
                val = "".join(x.text or "" for x in isv.iter(M + "t"))
            elif v is not None:
                val = v.text
            if val not in (None, ""):
                cells[(rn, _colnum(ref))] = str(val).strip()
    return cells


def analyser(cells):
    """Repère les sections, leurs postes (largeurs comprises), et rend la liste
    des sections : [{postes:[(start,end,key,largeur,nom)], data_rows:[...]}].
    Lève ValueError si un poste porte un nom inconnu."""
    get = lambda r, c: cells.get((r, c), "")
    maxrow = max(r for r, _ in cells)
    entetes = [r for r in range(1, maxrow + 1) if get(r, 1) == "Nom"]
    if not entetes:
        raise ValueError("aucune section (aucune ligne « Nom »)")
    sections = []
    for i, hr in enumerate(entetes):
        nexth = entetes[i + 1] if i + 1 < len(entetes) else maxrow + 1
        jr = hr + 1
        debuts = sorted(c for (r, c) in cells if r == jr and cells[(r, c)].upper() == "J-1")
        postes = []
        for idx, s in enumerate(debuts):
            nom = get(hr, s).strip()
            key = NOM_POSTE.get(nom.upper())
            if not key:
                raise ValueError("poste inconnu « %s » (ligne %d, colonne %d)" % (nom, hr, s))
            fin = (debuts[idx + 1] - 1) if idx + 1 < len(debuts) else s + 10
            largeur = sum(1 for c in range(s, fin + 1) if get(jr, c).upper().startswith("J-"))
            postes.append((s, fin, key, largeur, nom))
        data_rows = [r for r in range(hr + 2, nexth) if get(r, 1) and get(r, 1) != "Nom"]
        sections.append({"hr": hr, "postes": postes, "data_rows": data_rows})
    return sections


def extraire(cells, sections, cv, ids_horaire):
    """Construit ops / brut / inventaire, SANS écrire de nom. Rend aussi, pour
    les portes, les anomalies détectées (bornes, intégralité, cohérence,
    trigrammes)."""
    get = lambda r, c: cells.get((r, c), "")
    ops, brut, noms = {}, {}, {}
    anomalies = {"tri": [], "bornes": [], "coherence": []}
    total_comptees = 0
    total_remplies = 0  # cellules-date (colonnes >= 6) dans les lignes de personnes
    for sec in sections:
        couvert = set()
        for r in sec["data_rows"]:
            nom, pre = get(r, 1), get(r, 2)
            tri = cv._initiales((pre + " " + nom).strip())
            if not tri:
                anomalies["tri"].append("ligne %d : « %s %s » → pas de trigramme" % (r, pre, nom))
                continue
            if tri in ops:
                anomalies["tri"].append("ligne %d : « %s %s » → %s déjà vu" % (r, pre, nom, tri))
            if ids_horaire is not None and tri not in ids_horaire:
                anomalies["tri"].append("ligne %d : %s (« %s %s ») absent de l'horaire" % (r, tri, pre, nom))
            rec = ops.setdefault(tri, dict((k, 0) for k in CLES))
            bru = brut.setdefault(tri, {})
            noms[tri] = (nom, pre)
            for (s, fin, key, largeur, _nm) in sec["postes"]:
                serials = [get(r, c) for c in range(s, fin + 1) if get(r, c)]
                for c in range(s, fin + 1):
                    if get(r, c):
                        couvert.add((r, c))
                cnt = len(serials)
                rec[key] += cnt
                total_comptees += cnt
                if serials:
                    bru[key] = bru.get(key, []) + serials
                if cnt > largeur:
                    anomalies["bornes"].append(
                        "%s · %s : %d recyclages pour une colonne large de %d (ligne %d)"
                        % (tri, key, cnt, largeur, r))
            e = get(r, 5)
            rec["restant"] = int(float(e)) if e not in ("",) and _num(e) else rec.get("restant", 0)
        # intégralité : toute cellule-date (col >= 6) d'une ligne de personne
        # doit tomber dans un poste (donc être « couverte »)
        for r in sec["data_rows"]:
            for (rr, c) in list(cells):
                if rr == r and c >= 6:
                    total_remplies += 1
                    if (r, c) not in couvert:
                        anomalies["coherence"].append(
                            "cellule hors poste : ligne %d colonne %d = %s" % (r, c, get(r, c)))
    for tri, rec in ops.items():
        fait = sum(rec[k] for k in CLES)
        rest = rec.get("restant", 0)
        if rest is None or rest < 0 or (fait + rest) % 5 != 0 or (fait + rest) < fait:
            anomalies["coherence"].append(
                "%s : fait=%d restant=%s (total %s n'est pas un multiple de 5 >= fait)"
                % (tri, fait, rest, (fait + rest) if rest is not None else "?"))
    return ops, brut, noms, anomalies, total_comptees, total_remplies


def _num(s):
    try:
        float(s)
        return True
    except (TypeError, ValueError):
        return False


def _date_serie(s):
    """Une série Excel (46165) → « JJ/MM ». Époque 1899-12-30 (convention Excel)."""
    try:
        d = datetime.date(1899, 12, 30) + datetime.timedelta(days=int(float(s)))
        return "%02d/%02d" % (d.day, d.month)
    except (TypeError, ValueError):
        return None


def composer_json(source_nom, ops, brut):
    """La sortie servie par l'app : postes libellés + ops {clés, restant, dates}.
    Les dates des recyclages RH (converties des séries Excel du brut, triées) sont
    jointes pour le tableau « dates app / dates RH » au clic d'un opérateur."""
    out = {
        "source": source_nom,
        "postes": dict((k, LIBELLES[k]) for k in LIBELLES),
        "contremaitre": "Recyclages contremaitre (colonne des adjoints)",
        "note": "Terrain arriere non suivi (regle du classeur). cm = recyclages contremaitre (adjoints).",
        "ops": {},
    }
    for tri in sorted(ops):
        rec = ops[tri]
        o = dict((k, rec[k]) for k in CLES)
        o["restant"] = rec.get("restant", 0)
        bru = brut.get(tri, {})
        dates = {}
        for k in CLES:
            series = bru.get(k) or []
            ds = [_date_serie(s) for s in sorted(series, key=lambda x: int(float(x)))]
            ds = [d for d in ds if d]
            if ds:
                dates[k] = ds
        if dates:
            o["dates"] = dates
        out["ops"][tri] = o
    return out


def tokens_noms(noms):
    """Les morceaux de noms/prénoms à bannir de la sortie (>= 3 lettres, sans accent)."""
    toks = set()
    for (nom, pre) in noms.values():
        for mot in re.split(r"[\s,.\-]+", (nom + " " + pre)):
            mot = _sans_accent(mot).upper()
            if len(mot) >= 3:
                toks.add(mot)
    return toks


def _sans_accent(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                    if unicodedata.category(c) != "Mn")


def porte(n, titre, ok, details):
    print("── %d. %s" % (n, titre), flush=True)
    if ok:
        print("     ouverte")
        return
    for d in details[:25]:
        print("     " + d)
    print("\nPORTE FERMÉE à l'étape %d (%s) : %d problème(s). Rien n'est installé."
          % (n, titre, len(details)))
    sys.exit(1)


def diff_installe(cible, neuf):
    """Ce qui change par rapport au recyclage installé."""
    anc = {}
    if os.path.exists(cible):
        try:
            anc = json.load(open(cible, encoding="utf-8")).get("ops", {})
        except Exception:
            anc = {}
    nx = neuf["ops"]
    lignes = []
    for tri in sorted(set(anc) | set(nx)):
        a, b = anc.get(tri), nx.get(tri)
        if a == b:
            continue
        if a is None:
            lignes.append("  + %s (nouveau) : %s" % (tri, _resume(b)))
        elif b is None:
            lignes.append("  - %s (retiré)" % tri)
        else:
            ch = [k for k in (CLES + ["restant"]) if a.get(k) != b.get(k)]
            lignes.append("  ~ %s : %s" % (tri, ", ".join(
                "%s %s→%s" % (k, a.get(k), b.get(k)) for k in ch)))
    return lignes


def _resume(o):
    return " ".join("%s=%s" % (k, o[k]) for k in CLES if o.get(k)) or "tout à 0"


# ── L'anonymiseur du classeur RH ───────────────────────────────────────────
# La même démarche que pour l'horaire (CLAUDE.md, « Garder le classeur sous la
# main, anonymisé ») : on n'INTERPRÈTE rien, on recopie l'archive en ne
# touchant QUE les noms. Ici les noms ont une place fixe — colonnes A (nom)
# et B (prénom) des lignes de personnes de « Suivi Polyvalence » — et c'est
# tout : la colonne A reçoit le trigramme, la B est vidée. Leurs chaînes
# partagées sont vidées aussi (sans quoi le nom resterait dans
# sharedStrings.xml), à condition qu'aucune autre cellule ne les emploie.
# Sortent avec eux : l'auteur et le dernier modificateur du document.
#
# LA GARANTIE, comme l'anonymiseur de l'horaire : la copie est relue en entier
# et l'on y cherche chaque mot de nom et de prénom (3 lettres et plus, sans
# accent, en mot entier). Un seul, et la copie est détruite.

def _cible_feuille(z):
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid = dict((r.get("Id"), r.get("Target")) for r in rels)
    RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    for sh in wb.findall(M + "sheets/" + M + "sheet"):
        if "polyvalence" in (sh.get("name") or "").lower():
            t = rid.get(sh.get(RNS + "id"))
            return t if t.startswith("xl/") else "xl/" + t
    raise ValueError("feuille « Suivi Polyvalence » introuvable")


def _lettres(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def anonymiser_recyclage(source, dst, sections, cells, cv):
    """Copie anonymisée du classeur RH. Rend (nb de cellules remplacées,
    mots surveillés). Lève ValueError si une chaîne de nom est partagée avec
    une cellule qui n'en est pas une, ou si la garantie trouve un reste."""
    get = lambda r, c: cells.get((r, c), "")
    lignes = {}
    for sec in sections:
        for r in sec["data_rows"]:
            nom, pre = get(r, 1), get(r, 2)
            lignes[r] = cv._initiales((pre + " " + nom).strip()) or ""
    z = zipfile.ZipFile(source)
    feuille = _cible_feuille(z)
    xml = z.read(feuille).decode("utf-8")
    vides, n = set(), 0

    def cellule(r, col, rep):
        nonlocal xml, n
        ref = "%s%d" % (col, r)
        m = re.search(r'<c r="%s"(?=[\s>/])([^>]*?)(/>|>(.*?)</c>)' % ref, xml, re.S)
        if not m:
            return
        attrs = m.group(1)
        if re.search(r'\bt="s"', attrs):
            v = re.search(r"<v>(\d+)</v>", m.group(3) or "")
            if v:
                vides.add(int(v.group(1)))
        style = re.search(r'\bs="\d+"', attrs)
        style = " " + style.group(0) if style else ""
        nouveau = ('<c r="%s"%s t="inlineStr"><is><t>%s</t></is></c>' % (ref, style, rep)
                   if rep else '<c r="%s"%s/>' % (ref, style))
        xml = xml[:m.start()] + nouveau + xml[m.end():]
        n += 1
    for r, tri in sorted(lignes.items()):
        cellule(r, "A", tri)
        cellule(r, "B", "")
    # une chaîne de nom employée ailleurs que dans une cellule de nom ?
    employees = set()
    for nomf in z.namelist():
        if re.match(r"xl/worksheets/sheet\d+\.xml$", nomf):
            texte = xml if nomf == feuille else z.read(nomf).decode("utf-8")
            for m in re.finditer(r'<c [^>]*\bt="s"[^>]*>\s*(?:<f[^<]*</f>\s*)?<v>(\d+)</v>', texte):
                employees.add(int(m.group(1)))
    partagees = vides & employees
    if partagees:
        raise ValueError("%d chaîne(s) de nom employée(s) aussi par une autre cellule"
                         % len(partagees))
    surveilles = set()
    for r in lignes:
        for mot in re.split(r"[\s,.\-']+", get(r, 1) + " " + get(r, 2)):
            mot = _sans_accent(mot).upper()
            if len(mot) >= 3:
                surveilles.add(mot)
    encours = dst + ".en-cours"
    with zipfile.ZipFile(encours, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in z.infolist():
            donnee = z.read(info.filename)
            if info.filename == feuille:
                donnee = xml.encode("utf-8")
            elif info.filename == "xl/sharedStrings.xml" and vides:
                txt = donnee.decode("utf-8")
                morceaux, i = [], [0]

                def si(m):
                    k = i[0]
                    i[0] += 1
                    return "<si><t></t></si>" if k in vides else m.group(0)
                donnee = re.sub(r"<si>.*?</si>", si, txt, flags=re.S).encode("utf-8")
            elif info.filename.startswith("docProps/"):
                donnee = re.sub(rb"<(dc:creator|cp:lastModifiedBy)>[^<]*</\1>",
                                rb"<\1></\1>", donnee)
            zout.writestr(info, donnee)
    # la garantie
    restes = []
    zr = zipfile.ZipFile(encours)
    for nomf in zr.namelist():
        if not re.search(r"\.(xml|rels|vml)$", nomf):
            continue
        plat = _sans_accent(zr.read(nomf).decode("utf-8", "replace")).upper()
        for mot in surveilles:
            if re.search(r"(?<![A-Z0-9])" + re.escape(mot) + r"(?![A-Z0-9])", plat):
                restes.append((mot, nomf))
    zr.close()
    if restes:
        os.remove(encours)
        raise ValueError("garantie : %d nom(s) subsistent dans la copie (détruite) : %s"
                         % (len(restes), ", ".join(sorted(set(f for _, f in restes)))))
    os.replace(encours, dst)
    return n, len(surveilles)


def fidelite_recyclage(source, copie, sections, cv):
    """Les cellules où la copie diffère de la source HORS des colonnes de
    noms des lignes de personnes. Doit être vide."""
    noms = set()
    for sec in sections:
        for r in sec["data_rows"]:
            noms.add((r, 1))
            noms.add((r, 2))

    def lire(chemin):
        cl = cv.Classeur(chemin)
        out = {}
        for f in cl.feuilles:
            for l, ligne in cl.grille(f, fusions=()).items():
                for c, v in ligne.items():
                    out[(f, l, c)] = v
        return out
    a, b = lire(source), lire(copie)
    ecarts = []
    for k in sorted(set(a) | set(b), key=str):
        if a.get(k) == b.get(k):
            continue
        f, l, c = k
        if "polyvalence" in f.lower() and (l, c) in noms:
            continue
        ecarts.append("%s ligne %d colonne %d" % k)
    return ecarts


def integralite_export(export, sections, neuf):
    """Le classeur ENTIER, exporté depuis la copie anonymisée, contre ce que
    l'application lit. Deux chemins indépendants — la lecture des portes part
    de la SOURCE et calcule le trigramme ; celui-ci part de la COPIE, où le
    trigramme est écrit en colonne A par l'anonymiseur — doivent donner, pour
    chaque personne et chaque poste, le même nombre de recyclages et les
    mêmes dates."""
    f = next(v for k, v in export["feuilles"].items() if "polyvalence" in k.lower())
    cel = f["cellules"]
    tot, vus = {}, set()
    for sec in sections:
        for r in sec["data_rows"]:
            tri = str(cel.get("A%d" % r, ""))
            vus.add(tri)
            for (d, fin, key, _l, _n) in sec["postes"]:
                vals = [cel["%s%d" % (_lettres(c), r)] for c in range(d, fin + 1)
                        if str(cel.get("%s%d" % (_lettres(c), r), "")).strip()]
                tot.setdefault((tri, key), []).extend(vals)
    ecarts = []
    for tri in sorted(vus - set(neuf["ops"])):
        ecarts.append("« %s » : ligne de personne de la copie, absente de la sortie" % tri)
    for tri in sorted(set(neuf["ops"]) - vus):
        ecarts.append("%s : dans la sortie, absent de la copie anonymisée" % tri)
    for (tri, key), vals in sorted(tot.items()):
        o = neuf["ops"].get(tri)
        if o is None:
            continue
        if o.get(key, 0) != len(vals):
            ecarts.append("%s · %s : %d dans le classeur entier, %d dans la sortie"
                          % (tri, key, len(vals), o.get(key, 0)))
            continue
        attendu = sorted(d for d in (_date_serie(v) for v in
                         sorted(vals, key=lambda x: float(x) if _num(x) else 0)) if d)
        if sorted((o.get("dates") or {}).get(key, [])) != attendu:
            ecarts.append("%s · %s : dates différentes entre le classeur entier et la sortie"
                          % (tri, key))
    return ecarts

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__ % (2026, 2026))
    source = os.path.abspath(args[0])
    annee = int(args[1]) if len(args) > 1 else 2026
    installer = "--installer" in sys.argv
    if not os.path.exists(source):
        sys.exit("introuvable : %s" % source)
    if os.path.commonpath([source, RACINE]) == RACINE:
        sys.exit("Le classeur source porte des noms : il ne doit pas être dans le dépôt.")

    data = os.path.join(RACINE, "data")
    cible = os.path.join(data, "recyclages-%d.json" % annee)
    cible_brut = os.path.join(data, "recyclages-%d-brut.json" % annee)
    horaire = os.path.join(data, "horaire-%d.json" % annee)
    ids = None
    if os.path.exists(horaire):
        ids = set(str(p.get("id", "")).split("-")[0]
                  for p in json.load(open(horaire, encoding="utf-8")).get("people", []))

    cv = _convert()
    copie_cible = os.path.join(data, "recyclages-%d.xlsx" % annee)
    export_cible = os.path.join(data, "recyclages-%d-classeur.json" % annee)
    travail = tempfile.mkdtemp(prefix="recyc-portes-")
    copie = os.path.join(travail, os.path.basename(copie_cible))
    export = os.path.join(travail, os.path.basename(export_cible))
    # ── 1. lecture & structure ────────────────────────────────────────────
    print("── 1. lecture & structure", flush=True)
    cells = lire_feuille(source)
    try:
        sections = analyser(cells)
    except ValueError as e:
        print("     " + str(e))
        print("\nPORTE FERMÉE à l'étape 1. Rien n'est installé.")
        sys.exit(1)
    print("     %d section(s), %d poste(s) au total"
          % (len(sections), sum(len(s["postes"]) for s in sections)))

    ops, brut, noms, anom, comptees, remplies = extraire(cells, sections, cv, ids)

    porte(2, "trigrammes connus et uniques", not anom["tri"], anom["tri"])
    porte(3, "bornes (aucun compte > largeur de colonne)", not anom["bornes"], anom["bornes"])
    integ = []
    if comptees != remplies:
        integ.append("%d cellules comptées, %d remplies : %d non attribuée(s)"
                     % (comptees, remplies, abs(remplies - comptees)))
    integ += [d for d in anom["coherence"] if d.startswith("cellule hors poste")]
    porte(4, "intégralité (chaque cellule comptée une fois)", not integ, integ)
    coher = [d for d in anom["coherence"] if not d.startswith("cellule hors poste")]
    porte(5, "cohérence (fait + restant = multiple de 5)", not coher, coher)

    neuf = composer_json(os.path.basename(source), ops, brut)
    texte_sortie = json.dumps(neuf, ensure_ascii=False) + json.dumps(brut, ensure_ascii=False)
    fuite = [t for t in tokens_noms(noms) if t in _sans_accent(texte_sortie).upper()]
    porte(6, "anonymat (aucun nom dans la sortie)", not fuite,
          ["nom/prénom présent : %s" % t for t in fuite])

    # ── 7. la copie anonymisée, et sa garantie ────────────────────────────
    try:
        nrep, nsurv = anonymiser_recyclage(source, copie, sections, cells, cv)
        porte(7, "copie anonymisée (garantie : aucun mot de nom dans l'archive)", True, [])
        print("     %d cellule(s) de nom remplacée(s), %d mot(s) de nom cherché(s) : aucun"
              % (nrep, nsurv))
    except ValueError as e:
        porte(7, "copie anonymisée", False, [str(e)])
    # ── 8. le second contrôle, qui n'emprunte rien à l'anonymiseur ────────
    r = subprocess.run([sys.executable, os.path.join(OUTILS, "verifier-anonymat.py"),
                        source, copie], capture_output=True, text=True)
    porte(8, "second contrôle d'anonymat (verifier-anonymat.py)", r.returncode == 0,
          (r.stdout + r.stderr).strip().splitlines())
    # ── 9. fidélité : hors des noms, la copie ne diffère de la source sur rien
    ecarts = fidelite_recyclage(source, copie, sections, cv)
    porte(9, "fidélité de la copie à la source (hors colonnes de noms)", not ecarts, ecarts)
    # ── 10. le classeur ENTIER en JSON, depuis la copie, avec son aller-retour
    r = subprocess.run([sys.executable, os.path.join(OUTILS, "exporter-classeur.py"),
                        copie, export], capture_output=True, text=True)
    porte(10, "export du classeur entier (aller-retour)", r.returncode == 0,
          (r.stdout + r.stderr).strip().splitlines())
    for l in r.stdout.strip().splitlines()[:2]:
        print("     " + l)
    # ── 11. intégralité : le classeur entier contre la sortie ─────────────
    ecarts = integralite_export(json.load(open(export, encoding="utf-8")), sections, neuf)
    porte(11, "intégralité classeur entier ↔ sortie (comptes et dates)", not ecarts, ecarts)

    print("\n══ CE QUI CHANGE par rapport au recyclage installé — à LIRE, et à dire"
          " au client ══\n")
    lignes = diff_installe(cible, neuf)
    print("\n".join(lignes) if lignes else "(rien)")

    if not installer:
        print("\nLes onze portes sont ouvertes. À blanc : rien n'est installé.")
        print("Relancer avec --installer pour remplacer data/recyclages-%d.json." % annee)
        return 0

    # ── installer ──────────────────────────────────────────────────────────
    neuf_txt = json.dumps(neuf, ensure_ascii=False, indent=1)
    brut_txt = json.dumps(brut, ensure_ascii=False, indent=1)
    def _pareil(a, b):
        return os.path.exists(b) and open(a, "rb").read() == open(b, "rb").read()
    for src_, dst_ in ((copie, copie_cible), (export, export_cible)):
        if not _pareil(src_, dst_):
            shutil.copy2(src_, dst_)
            print("Réserve locale (hors dépôt) : %s" % os.path.relpath(dst_, RACINE))
    if os.path.exists(cible) and open(cible, encoding="utf-8").read() == neuf_txt \
            and os.path.exists(cible_brut) and open(cible_brut, encoding="utf-8").read() == brut_txt:
        print("\nLe recyclage installé est déjà identique : rien à installer, V ne bouge pas.")
        return 0
    tmp = tempfile.mkdtemp(prefix="recyc-")
    sw = os.path.join(RACINE, "sw.js")
    for chemin in (cible, cible_brut, sw):
        if os.path.exists(chemin):
            shutil.copy2(chemin, os.path.join(tmp, os.path.basename(chemin)))
    open(cible, "w", encoding="utf-8").write(neuf_txt)
    open(cible_brut, "w", encoding="utf-8").write(brut_txt)
    swtxt = open(sw, encoding="utf-8").read()
    m = re.search(r'var V = "nfdm-v(\d+)";', swtxt)
    if m:
        open(sw, "w", encoding="utf-8").write(
            swtxt.replace(m.group(0), 'var V = "nfdm-v%d";' % (int(m.group(1)) + 1), 1))
    r = subprocess.run([sys.executable, os.path.join(OUTILS, "verifier-depot.py")],
                       cwd=RACINE, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        for nom in os.listdir(tmp):
            dest = sw if nom == "sw.js" else os.path.join(data, nom)
            shutil.copy2(os.path.join(tmp, nom), dest)
        print("\nLE GARDE-FOU DU DÉPÔT ÉCHOUE : les fichiers d'avant sont remis en place.")
        return 1
    print("\nInstallé : %s" % os.path.relpath(cible, RACINE))
    print("Brut (trigrammes seuls, hors dépôt) : %s" % os.path.relpath(cible_brut, RACINE))
    if m:
        print("V : nfdm-v%s → nfdm-v%d" % (m.group(1), int(m.group(1)) + 1))
    print("Garde-fou du dépôt : à zéro.")
    print("\nReste à faire : relire le rapport ci-dessus, tester dans un navigateur, committer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
