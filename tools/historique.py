#!/usr/bin/env python3
"""L'HISTORIQUE DES CHANGEMENTS DE L'HORAIRE, classeur par classeur.

Le client, le 06/11/2026 : « pour chaque trigramme, est-ce possible d'avoir
un historique complet personnel avec les changements effectués, et pour la
RH un historique complet de tous les trigrammes, reprenant les changements
(+ date de modification) ».

La cloche « Horaire modifié » ne compare qu'à ce que le téléphone a vu la
dernière fois ; l'historique de l'espace RH ne garde que les journées
corrigées dans l'application. Ici, chaque classeur installé : sa date (le
« maj » de l'horaire), et pour chacun, chaque journée qui a changé — la
cellule d'avant et celle d'après, telles que l'horaire anonymisé les dit
(cellule, annotation, commentaire), plus les arrivées et les départs.

    data/historique-AAAA.json
    {"annee": 2026, "depuis": "2026-09-23T…",
     "classeurs": [{"maj": "2026-11-06T15:59", "ch": [["TRI", "MMJJ", avant, après], …],
                    "pe": [["+", "TRI"], ["-", "TRI"]]}, …]}

Une version de l'horaire dont le « maj » ne change pas n'est pas un
classeur neuf mais une relecture (une règle de lecture changée dans
l'outil) : elle sert de point de comparaison, sans entrée.

    python3 tools/historique.py --git [ANNÉE…]          tout refaire depuis l'historique git
    python3 tools/historique.py --ajouter ANCIEN NEUF   ajouter un classeur (le robot, à l'installation)
    python3 tools/historique.py --epreuve               l'épreuve, sur des horaires fabriqués

Rien d'autre que l'horaire anonymisé n'y entre : les mêmes trigrammes, les
mêmes commentaires, déjà passés par les portes de mettre-a-jour.py.
"""
import json
import os
import subprocess
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def chemin(annee):
    return os.path.join(RACINE, "data", "historique-%s.json" % annee)


def personnes(h):
    return {p["id"]: p.get("d", {}) for p in h.get("people", [])}


def ecarts(ancien, neuf):
    """L'entrée d'un classeur : ce qui change de l'horaire `ancien` au `neuf`."""
    A, N = personnes(ancien), personnes(neuf)
    ch = []
    for t in sorted(N):
        if t not in A:
            continue
        a, n = A[t], N[t]
        for k in sorted(set(a) | set(n)):
            if a.get(k) != n.get(k):
                ch.append([t, k, a.get(k), n.get(k)])
    pe = [["+", t] for t in sorted(set(N) - set(A))] + [["-", t] for t in sorted(set(A) - set(N))]
    e = {"maj": neuf.get("maj") or "", "ch": ch}
    if pe:
        e["pe"] = pe
    return e


def ajouter(hist, ancien, neuf):
    """Ajoute le classeur `neuf` à `hist` ; rien si ce n'est pas un classeur
    neuf (même « maj ») ou s'il y est déjà. Vrai s'il a été ajouté."""
    m = neuf.get("maj") or ""
    if not m or m == (ancien.get("maj") or "") or any(c.get("maj") == m for c in hist["classeurs"]):
        return False
    e = ecarts(ancien, neuf)
    if not e["ch"] and not e.get("pe"):
        return False
    hist["classeurs"].append(e)
    hist["classeurs"].sort(key=lambda c: c["maj"])
    return True


def ecrire(annee, hist):
    with open(chemin(annee), "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")


def lire(annee):
    try:
        with open(chemin(annee), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"annee": int(annee), "depuis": "", "classeurs": []}


def depuis_git(annee):
    f = "data/horaire-%s.json" % annee
    r = subprocess.run(["git", "log", "--reverse", "--format=%H", "--", f], cwd=RACINE,
                       capture_output=True, text=True, check=True)
    hist = {"annee": int(annee), "depuis": "", "classeurs": []}
    prec = None
    for h in r.stdout.split():
        s = subprocess.run(["git", "show", "%s:%s" % (h, f)], cwd=RACINE, capture_output=True, text=True)
        try:
            v = json.loads(s.stdout)
        except ValueError:
            continue
        if prec is None:
            hist["depuis"] = v.get("maj") or ""
        else:
            ajouter(hist, prec, v)
        prec = v
    return hist


def epreuve():
    a = {"maj": "2026-01-01T08:00", "people": [{"id": "AAA", "d": {"0105": ["AM"], "0106": ["PM"]}},
                                                 {"id": "BBB", "d": {"0105": ["N"]}}]}
    b = {"maj": "2026-01-02T08:00", "people": [{"id": "AAA", "d": {"0105": ["AM", "VA"], "0106": ["PM"]}},
                                                 {"id": "CCC", "d": {"0105": ["D"]}}]}
    relu = {"maj": "2026-01-02T08:00", "people": b["people"]}
    h = {"annee": 2026, "depuis": a["maj"], "classeurs": []}
    assert ajouter(h, a, b)
    c = h["classeurs"][0]
    assert c["ch"] == [["AAA", "0105", ["AM"], ["AM", "VA"]]], c
    assert c["pe"] == [["+", "CCC"], ["-", "BBB"]], c
    assert not ajouter(h, b, relu), "une relecture (même maj) n'est pas un classeur"
    assert not ajouter(h, a, b), "un classeur déjà là ne s'ajoute pas deux fois"
    print("épreuve de l'historique : ok")
    return 0


def main(argv):
    if "--epreuve" in argv:
        return epreuve()
    if "--ajouter" in argv:
        i = argv.index("--ajouter")
        with open(argv[i + 1], encoding="utf-8") as f:
            ancien = json.load(f)
        with open(argv[i + 2], encoding="utf-8") as f:
            neuf = json.load(f)
        annee = str(neuf.get("year") or "")
        if not annee:
            print("historique : l'horaire neuf ne dit pas son année.")
            return 1
        h = lire(annee)
        if ajouter(h, ancien, neuf):
            ecrire(annee, h)
            print("historique %s : classeur du %s ajouté (%d journée(s))." % (annee, neuf.get("maj"), len(h["classeurs"][-1]["ch"])))
        else:
            print("historique %s : rien à ajouter." % annee)
        return 0
    if "--git" in argv:
        ans = [a for a in argv if a.isdigit()] or ["2026", "2027"]
        for an in ans:
            h = depuis_git(an)
            ecrire(an, h)
            print("historique %s : %d classeur(s), %d journée(s) changée(s), depuis %s."
                  % (an, len(h["classeurs"]), sum(len(c["ch"]) for c in h["classeurs"]), h["depuis"]))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
