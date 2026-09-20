#!/usr/bin/env python3
"""Compare deux versions de l'horaire converti et dit ce qui a bougé.

    python3 tools/comparer-horaire.py data/horaire-2026.json nouveau.json

Le client renvoie régulièrement son récapitulatif Excel. Écraser l'ancien
JSON sans regarder ferait passer une correction d'horaire pour un simple
rafraîchissement, alors qu'une journée qui change déplace des heures, des
primes et parfois un chèque-repas. Ce script dit exactement ce qui change
avant d'installer la nouvelle version.

Il ne compare que des identifiants à trois lettres : aucun nom n'entre ni ne
sort.
"""
import json
import sys

EXEMPLES = 6


def _charger(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def _gens(base):
    return {p["id"]: p for p in base.get("people", [])}


def _jour(cle):
    return "%s/%s" % (cle[2:], cle[:2])


def comparer(avant, apres):
    lignes, change = [], False

    # Tous les champs d'en-tête, pas seulement ceux qu'on connaît : un champ
    # ajouté demain doit se voir dès demain.
    for cle in sorted(set(avant) | set(apres)):
        if cle == "people" or avant.get(cle) == apres.get(cle):
            continue
        a_, b_ = avant.get(cle), apres.get(cle)
        if isinstance(a_, (dict, list)) or isinstance(b_, (dict, list)):
            a_, b_ = "%d entrée(s)" % len(a_ or ()), "%d entrée(s)" % len(b_ or ())
        lignes.append("  %-10s %s -> %s" % (cle, a_, b_))
        change = True
    if lignes:
        lignes.insert(0, "En-tête :")
        lignes.append("")

    A, B = _gens(avant), _gens(apres)
    partis, arrives = sorted(set(A) - set(B)), sorted(set(B) - set(A))
    if partis or arrives:
        change = True
        lignes.append("Personnes :")
        for i in arrives:
            lignes.append("  + %-6s %-28s %d journées" % (i, B[i]["cat"], len(B[i]["d"])))
        for i in partis:
            lignes.append("  - %-6s %-28s %d journées" % (i, A[i]["cat"], len(A[i]["d"])))
        lignes.append("")

    cats = [(i, A[i]["cat"], B[i]["cat"]) for i in sorted(set(A) & set(B))
            if A[i]["cat"] != B[i]["cat"]]
    if cats:
        change = True
        lignes.append("Changements de groupe :")
        for i, a, b in cats:
            lignes.append("  %-6s %s -> %s" % (i, a, b))
        lignes.append("")

    detail = []
    for i in sorted(set(A) & set(B)):
        ja, jb = A[i]["d"], B[i]["d"]
        touches = sorted(k for k in set(ja) | set(jb) if ja.get(k) != jb.get(k))
        if touches:
            detail.append((i, touches, ja, jb))
    if detail:
        change = True
        total = sum(len(t) for _, t, _, _ in detail)
        lignes.append("Journées modifiées : %d, chez %d personne(s)"
                      % (total, len(detail)))
        for i, touches, ja, jb in detail:
            lignes.append("  %s — %d journée(s)" % (i, len(touches)))
            for k in touches[:EXEMPLES]:
                lignes.append("      %s  %s" % (_jour(k), json.dumps(ja.get(k), ensure_ascii=False)))
                lignes.append("      %s  %s" % (" " * 5, json.dumps(jb.get(k), ensure_ascii=False)))
            if len(touches) > EXEMPLES:
                lignes.append("      … et %d autre(s)" % (len(touches) - EXEMPLES))
        lignes.append("")

    bouges = []
    for i in sorted(set(A) & set(B)):
        ca, cb = A[i].get("c") or {}, B[i].get("c") or {}
        if ca == cb:
            continue
        ecarts = []
        for sec in sorted(set(ca) | set(cb)):
            va, vb = ca.get(sec) or {}, cb.get(sec) or {}
            for k in sorted(set(va) | set(vb)):
                if va.get(k) != vb.get(k):
                    ecarts.append("%s.%s %s -> %s" % (sec, k, va.get(k, "—"), vb.get(k, "—")))
        bouges.append((i, ecarts))
    if bouges:
        change = True
        lignes.append("Compteurs : %d personne(s)" % len(bouges))
        for i, ecarts in bouges:
            lignes.append("  %-6s %s" % (i, " · ".join(ecarts)))
        lignes.append("")

    bouges = [(i, A[i].get("poly"), B[i].get("poly")) for i in sorted(set(A) & set(B))
              if A[i].get("poly") != B[i].get("poly")]
    if bouges:
        change = True
        lignes.append("Polyvalence : %d personne(s)" % len(bouges))
        for i, a, b in bouges:
            lignes.append("  %-6s %s -> %s" % (i, json.dumps(a, ensure_ascii=False),
                                               json.dumps(b, ensure_ascii=False)))
        lignes.append("")

    # Le filet : tout champ de personne que les sections ci-dessus ne
    # présentent pas. Sans lui, le champ « e » — ajouté au convertisseur pour
    # garder ce qui entoure les noms — a pu apparaître chez 67 personnes sans
    # que le comparateur dise un mot. Un comparateur muet sur ce qu'il ne
    # connaît pas ne compare rien.
    PRESENTES = {"id", "cat", "d", "c", "poly"}
    autres = {}
    for i in sorted(set(A) & set(B)):
        for cle in sorted((set(A[i]) | set(B[i])) - PRESENTES):
            if A[i].get(cle) != B[i].get(cle):
                autres.setdefault(cle, []).append(i)
    if autres:
        change = True
        lignes.append("Autres champs :")
        for cle, gens in sorted(autres.items()):
            apercu = ", ".join(gens[:EXEMPLES])
            if len(gens) > EXEMPLES:
                apercu += ", … et %d autre(s)" % (len(gens) - EXEMPLES)
            lignes.append("  %-8s %d personne(s) : %s" % (cle, len(gens), apercu))
            i = gens[0]
            lignes.append("      %-5s %s" % (i, json.dumps(A[i].get(cle), ensure_ascii=False)[:90]))
            lignes.append("      %-5s %s" % (" " * 5, json.dumps(B[i].get(cle), ensure_ascii=False)[:90]))
        lignes.append("")

    if not change:
        lignes.append("Rien n'a changé : les deux versions sont identiques.")
    return lignes


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    for ligne in comparer(_charger(sys.argv[1]), _charger(sys.argv[2])):
        print(ligne)
