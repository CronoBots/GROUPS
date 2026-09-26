#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Confronter l'horaire au classeur ENTIER : qu'est-ce qui ne lui arrive pas ?

Le client, le 25/09/2026 : « il faut qu'à partir du fichier complet, tu
revérifies tout ».

data/classeur-2026-brut.json porte tout le classeur ; data/horaire-2026.json
ne porte que ce que le convertisseur a su lire. Tout ce qui est dans le
premier et pas dans le second est soit une perte, soit une zone qu'on n'a pas
encore décidé de lire — et il faut savoir laquelle.

LA GRILLE DES JOURS SE COMPARE CELLULE PAR CELLULE — c'est la seule exigence
dure, et le code de retour la porte. La première version versait tous les
commentaires dans un SAC et cherchait chacun n'importe où dedans : un
commentaire posé sur la mauvaise journée passait, un commentaire court —
« rappel », « remplace » — se retrouvait toujours quelque part (4 365 font
douze signes ou moins), et les valeurs des cellules n'étaient pas regardées
du tout. L'audit du 26/09/2026 l'a mesuré : elle voyait 6 écarts là où 256
cellules et annotations étaient corrompues dans la copie de référence.

Pour chaque colonne-personne du brut, on retrouve la personne de l'horaire
PAR L'ACCORD DE LEURS JOURNÉES — et non par le trigramme, que CORRECTIONS et
les suffixes -1 font diverger —, puis, journée par journée, on compare la
cellule, l'annotation et le commentaire. Échouent :

  - une colonne qu'aucune personne ne reconnaît ;
  - une journée écrite d'un côté et pas de l'autre (sauf une cellule vide
    devenue repos entre la première et la dernière journée écrite — c'est
    la règle du convertisseur) ;
  - une cellule, une annotation ou un commentaire différents ;
  - DEUX COPIES D'UNE MÊME PERSONNE QUI DIVERGENT entre feuilles : les
    adjoints sont recopiés sur cinq feuilles, et « une copie concorde »
    masquerait une faute posée dans l'une des quatre autres ;
  - un identifiant de connexion, dans l'un OU l'autre fichier.

LES DEUX FICHIERS NE PASSENT PAS PAR LE MÊME CHEMIN, et la comparaison naïve
ment. L'horaire sort du .xlsm par le convertisseur, qui NETTOIE les
commentaires ; le brut sort du .xlsx par l'anonymiseur puis par l'exporteur,
qui les RECOPIE. On compare donc les commentaires sur un texte réduit :
minuscules, sans ponctuation ni blancs, sans tête de signature — trigramme
ou « Auteur: », le nom par défaut d'Excel — ni mention de retrait. Et les
deux commentaires d'une journée (cellule et annotation) se joignent comme le
convertisseur les joint, le plus complet l'emportant quand l'un contient
l'autre.

Le pied de feuille et la feuille « Polyvalence » sont comptés et montrés,
sans faire échouer, tant que le client n'a pas dit ce qu'il faut en faire.

    python3 tools/verifier-integralite.py [brut.json] [horaire.json] [--detail]
"""
import collections
import importlib.util
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRUT = os.path.join(RACINE, "data", "classeur-2026-brut.json")
HORAIRE = os.path.join(RACINE, "data", "horaire-2026.json")
PREMIERE_LIGNE_DE_PIED = 377

# La mise en page du classeur est celle que le convertisseur connaît : on la
# lui emprunte plutôt que de la recopier — deux copies divergent.
_spec = importlib.util.spec_from_file_location(
    "cv", os.path.join(RACINE, "tools", "convertir-horaire.py"))
cv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cv)

# Le motif est écrit ICI : ce contrôle ne doit pas emprunter les motifs des
# outils qu'il vérifie. Deux lettres qui ne sont pas toutes deux de A à F —
# une couleur n'est pas un login.
LOGIN = re.compile(r"(?<![A-Za-z0-9#])(?![A-Fa-f]{2}[0-9])[A-Za-z]{2}[0-9]{4,6}(?![0-9A-Za-z])")


def _reduit(t):
    """Le texte réduit à ce que les deux chemins d'écriture ont en commun."""
    t = (t or "").replace("(identifiant retiré)", "").replace("(nom retiré)", "")
    t = re.sub(r"(?:^|(?<=\n))\s*(?:[A-Z]{3}(?:-\d)?|Auteur)\s*:", "", t)
    t = re.sub(r"\b[A-Z]{3}(?:-\d)?\s*:", "", t)
    return re.sub(r"[^0-9a-zà-ÿ]", "", t.lower())


def _les_deux(a, b):
    """Les façons dont le convertisseur a pu joindre les deux commentaires
    d'une journée (cv._les_deux) : bout à bout, ou le plus complet seul quand
    l'un contient l'autre. Il compare sur son texte à LUI, casse comprise —
    « Rappel 19/1 » n'est pas contenu dans « RAPPEL 19/1 » et il garde les
    deux —, alors qu'on compare ici sur un texte réduit : on accepte donc les
    deux jointures, et rien d'autre."""
    if not a or not b:
        return frozenset([a or b])
    out = {a + b}
    if a in b:
        out.add(b)
    if b in a:
        out.add(a)
    return frozenset(out)


def _non_barre(fiche, adresse):
    """Le commentaire d'une adresse du brut, SANS SES MORCEAUX BARRÉS.

    Le client, le 26/09/2026 : « un commentaire barré est un commentaire qui
    n'est plus à prendre en compte ». Le convertisseur les retire ; le brut
    les garde, avec leur drapeau, dans `riches`. On compare donc ce que
    l'horaire doit porter — le texte non barré —, et non tout ce qui est
    écrit.
    """
    runs = fiche.get("riches", {}).get(adresse)
    if not runs:
        return fiche["commentaires"].get(adresse, "")
    return "".join(" " if len(r) > 1 and "s" in r[1] else r[0] for r in runs)


def _ligne(adresse):
    return int(re.search(r"(\d+)$", adresse).group(1))


def _grille(dico):
    g = {}
    for adr, v in dico.items():
        m = re.match(r"([A-Z]+)(\d+)$", adr)
        g.setdefault(int(m.group(2)), {})[cv._colnum(m.group(1))] = v
    return g


def colonnes_du_brut(brut):
    """{(feuille, colonne): {"tri": …, "jours": {MMJJ: (cellule, annotation,
    commentaire réduit)}}} pour la grille des jours de chaque feuille de
    personnes."""
    out = {}
    for feuille in cv.FEUILLES:
        if feuille not in brut["feuilles"]:
            continue
        f = brut["feuilles"][feuille]
        g = _grille(f["cellules"])
        cm = _grille(dict((a, _non_barre(f, a)) for a in f["commentaires"]))
        mois = cv.blocs_de_mois(g)
        for col in sorted(g.get(cv.LIGNE_NOMS, {})):
            nom = str(g[cv.LIGNE_NOMS][col]).strip()
            if col < 3 or nom in ("", "0"):
                continue
            jours = {}
            for m, r0 in mois.items():
                for d in range(1, 32):
                    r = r0 + d - 1
                    if str(g.get(r, {}).get(cv.COL_JOUR, "")) != str(d):
                        continue
                    jours["%02d%02d" % (m, d)] = (
                        str(g.get(r, {}).get(col, "")), str(g.get(r, {}).get(col + 1, "")),
                        _les_deux(_reduit(cm.get(r, {}).get(col, "")),
                                  _reduit(cm.get(r, {}).get(col + 1, ""))))
            out[(feuille, col)] = {"tri": nom, "jours": jours}
    return out


def associer(colonnes, hor):
    """Colonne du brut -> identifiant de l'horaire, par l'accord des valeurs."""
    gens = {p["id"]: p for p in hor["people"]}
    assoc, ratees = {}, []
    for k, c in colonnes.items():
        ecrites = [(j, v) for j, v in c["jours"].items() if v[0] or v[1]]

        def score(pid):
            d = gens[pid]["d"]
            return sum(1 for j, v in ecrites if j in d and d[j][0] == v[0]
                       and (d[j] + ["", ""])[1] == v[1])
        meilleur = max(gens, key=score)
        s = score(meilleur)
        if not ecrites:
            continue
        if s < 0.5 * len(ecrites):
            ratees.append("%s colonne %s (%s) : aucune personne ne concorde (%d/%d)"
                          % (k[0], cv._lettre(k[1]), c["tri"], s, len(ecrites)))
            continue
        assoc[k] = meilleur
    return assoc, ratees


def comparer(brut, hor):
    cols = colonnes_du_brut(brut)
    assoc, ratees = associer(cols, hor)
    gens = {p["id"]: p for p in hor["people"]}
    par = collections.defaultdict(lambda: collections.defaultdict(list))
    for k, c in cols.items():
        if k in assoc:
            for j, v in c["jours"].items():
                par[assoc[k]][j].append(v + (k[0],))
    ok = collections.Counter()
    fautes = collections.defaultdict(list)
    for pid, jours in par.items():
        d = gens[pid]["d"]
        for j, copies in jours.items():
            ecrites = [x for x in copies if x[0] or x[1] or x[2] != frozenset([""])]
            h = d.get(j)
            if not ecrites:
                if h is None:
                    ok["vide des deux côtés"] += 1
                elif h == ["-"]:
                    ok["cellule vide devenue repos (règle du convertisseur)"] += 1
                else:
                    fautes["écrit dans l'horaire, vide dans le classeur"].append((pid, j, h))
                continue
            if len(set(x[:3] for x in ecrites)) > 1:
                fautes["deux copies de la même personne divergent"].append(
                    (pid, j, [(x[3], x[0], x[1]) for x in ecrites]))
            if h is None:
                fautes["écrit dans le classeur, absent de l'horaire"].append(
                    (pid, j, [x[:2] for x in ecrites]))
                continue
            hh = (h + ["", "", ""])[:3]
            x = ecrites[0]
            if x[0] != hh[0]:
                fautes["cellule différente"].append((pid, j, hh[0], x[0]))
            if x[1] != hh[1]:
                fautes["annotation différente"].append((pid, j, hh[1], x[1]))
            if _reduit(hh[2]) not in x[2]:
                fautes["commentaire différent"].append((pid, j, hh[2][:90]))
            else:
                ok["journée identique"] += 1
    return ok, fautes, ratees, len(assoc), len(cols)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    brut_p = args[0] if args else BRUT
    hor_p = args[1] if len(args) > 1 else HORAIRE
    detail = "--detail" in sys.argv
    if not (os.path.exists(brut_p) and os.path.exists(hor_p)):
        sys.stderr.write("il manque un des deux fichiers\n")
        return 2
    with open(brut_p, encoding="utf-8") as f:
        brut = json.load(f)
    with open(hor_p, encoding="utf-8") as f:
        hor = json.load(f)

    ok, fautes, ratees, na, nc = comparer(brut, hor)
    logins = collections.Counter()
    for nom, contenu in ((brut_p, brut), (hor_p, hor)):
        for m in LOGIN.finditer(json.dumps(contenu, ensure_ascii=False)):
            logins[(os.path.basename(nom), m.group(0))] += 1

    # Le pied de feuille et « Polyvalence » : ce que l'horaire porte déjà —
    # commentaires des journées, contrats réduits, DATES DE POLYVALENCE
    # (oubliées jusqu'au 26/09/2026 : 74 « non repris » annoncés pour 70
    # dates bel et bien lues).
    sac = _reduit(" ".join(
        [" ".join(v[1:]) for p in hor["people"] for v in p["d"].values()]
        + [c.get("txt", "") for p in hor["people"] for c in p.get("ct", [])]
        + [x.get("txt", "") for p in hor["people"]
           for x in ((p.get("poly") or {}).get("dates") or {}).values()]))
    pied, poly = [], []
    for nom in brut["feuilles"]:
        for adr in brut["feuilles"][nom]["commentaires"]:
            txt = _non_barre(brut["feuilles"][nom], adr)
            reduit = _reduit(txt)
            if not reduit or reduit in sac:
                continue
            if nom == "Polyvalence":
                poly.append((nom, adr, txt))
            elif nom in cv.FEUILLES and _ligne(adr) >= PREMIERE_LIGNE_DE_PIED:
                pied.append((nom, adr, txt))

    n_fautes = sum(len(v) for v in fautes.values()) + len(ratees) + sum(logins.values())
    print("Grille des jours : %d colonne(s)-personne(s) du classeur, %d reconnue(s)"
          % (nc, na))
    for k, v in sorted(ok.items()):
        print("  ✓ %6d  %s" % (v, k))
    print()
    print("  %s %6d  grille des jours — doit être à ZÉRO"
          % ("✓" if not n_fautes else "✗", n_fautes))
    print("  ·  %6d  pied de feuille — commentaires non repris" % len(pied))
    print("  ·  %6d  feuille « Polyvalence » — commentaires non repris" % len(poly))

    for r in ratees:
        print("\n── colonne non reconnue : %s" % r)
    for (f, t), c in sorted(logins.items()):
        print("\n── IDENTIFIANT DE CONNEXION : %d × %s dans %s" % (c, t, f))
    for classe, lot in sorted(fautes.items()):
        print("\n── %s (%d)" % (classe, len(lot)))
        for e in lot[:(40 if detail else 6)]:
            print("   ", e)
    for titre, lot in (("pied de feuille", pied), ("feuille Polyvalence", poly)):
        if not lot:
            continue
        print("\n── %s (%d)" % (titre, len(lot)))
        par = collections.Counter(_ligne(a) for _, a, _ in lot)
        for l, n in par.most_common(8):
            ex = [x for x in lot if _ligne(x[1]) == l][0]
            print("   ligne %4d : %3d — %s %s : %s"
                  % (l, n, ex[0], ex[1], " ".join(ex[2].split())[:88]))
    return 1 if n_fautes else 0


if __name__ == "__main__":
    sys.exit(main())
