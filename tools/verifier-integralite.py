#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Confronter l'horaire au classeur ENTIER : qu'est-ce qui ne lui arrive pas ?

Le client, le 25/09/2026 : « il faut qu'à partir du fichier complet, tu
revérifies tout ».

data/classeur-2026-brut.json porte tout le classeur ; data/horaire-2026.json
ne porte que ce que le convertisseur a su lire. Tout commentaire du premier
qui ne se retrouve pas dans le second est soit une perte, soit une zone qu'on
n'a pas encore décidé de lire — et il faut savoir laquelle.

LES DEUX FICHIERS NE PASSENT PAS PAR LE MÊME CHEMIN, et la comparaison naïve
ment. L'horaire sort du .xlsm par le convertisseur ; le brut sort du .xlsx par
l'anonymiseur puis par l'exporteur. Trois différences d'écriture s'ensuivent,
et chacune a fait croire à une perte :

  * les ESPACES — l'un colle deux fragments de commentaire que l'autre sépare
    (1 099 faux positifs) ;
  * les TÊTES DE SIGNATURE — le brut garde « ABC: », le convertisseur la
    retire (473 de plus) ;
  * les JETONS RETIRÉS — « (identifiant retiré) » n'est pas écrit pareil des
    deux côtés selon le moment où il est posé (12 de plus).

On compare donc sur un texte réduit : minuscules, sans ponctuation, sans tête
de trigramme, sans mention de retrait. Ce qui survit à cela manque vraiment.

LA GRILLE DES JOURS DOIT ÊTRE COMPLÈTE — c'est la seule exigence dure, et le
code de retour la porte. Le pied de feuille et la feuille « Polyvalence »
portent des commentaires que l'horaire ne reprend pas encore ; ils sont
comptés et montrés, sans faire échouer, tant que le client n'a pas dit ce
qu'il faut en faire.

    python3 tools/verifier-integralite.py
"""
import collections
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRUT = os.path.join(RACINE, "data", "classeur-2026-brut.json")
HORAIRE = os.path.join(RACINE, "data", "horaire-2026.json")
PREMIERE_LIGNE_DE_PIED = 377


def _reduit(t):
    """Le texte réduit à ce que les deux chemins d'écriture ont en commun."""
    t = t.replace("(identifiant retiré)", "")
    t = re.sub(r"\b[A-Z]{3}\s*:", "", t)
    return re.sub(r"[^0-9a-zà-ÿ]", "", t.lower())


def _ligne(adresse):
    return int(re.search(r"(\d+)$", adresse).group(1))


def main():
    if not (os.path.exists(BRUT) and os.path.exists(HORAIRE)):
        sys.stderr.write("il manque un des deux fichiers de data/\n")
        return 2
    with open(BRUT, encoding="utf-8") as f:
        brut = json.load(f)
    with open(HORAIRE, encoding="utf-8") as f:
        hor = json.load(f)

    # Le sac de ce que l'horaire porte : les commentaires des journées, ET
    # les contrats réduits lus en pied de feuille depuis le 25/09. Oublier
    # les seconds ferait compter comme perdu ce qu'on vient de récupérer.
    sac = _reduit(" ".join(
        [" ".join(v[1:]) for p in hor["people"] for v in p["d"].values()]
        + [c.get("txt", "") for p in hor["people"] for c in p.get("ct", [])]))
    jours, pied, poly = [], [], []
    total = 0
    for nom in brut["feuilles"]:
        for adr, txt in brut["feuilles"][nom]["commentaires"].items():
            total += 1
            reduit = _reduit(txt)
            if not reduit or reduit in sac:
                continue
            if nom == "Polyvalence":
                poly.append((nom, adr, txt))
            elif _ligne(adr) >= PREMIERE_LIGNE_DE_PIED:
                pied.append((nom, adr, txt))
            else:
                jours.append((nom, adr, txt))

    print("Classeur entier : %d commentaires · horaire : %d journées"
          % (total, sum(len(p["d"]) for p in hor["people"])))
    print()
    print("  %s %4d  grille des jours — doit être à ZÉRO"
          % ("✓" if not jours else "✗", len(jours)))
    print("  ·  %4d  pied de feuille — compteurs, CP et TP contractuels"
          % len(pied))
    print("  ·  %4d  feuille « Polyvalence » — dates d'acquisition"
          % len(poly))

    for titre, lot in (("grille des jours", jours),
                       ("pied de feuille", pied),
                       ("feuille Polyvalence", poly)):
        if not lot:
            continue
        print("\n── %s (%d)" % (titre, len(lot)))
        par = collections.Counter(_ligne(a) for _, a, _ in lot)
        for l, n in par.most_common(8):
            ex = [x for x in lot if _ligne(x[1]) == l][0]
            print("   ligne %4d : %3d — %s %s : %s"
                  % (l, n, ex[0], ex[1], ex[2][:88]))
    return 1 if jours else 0


if __name__ == "__main__":
    sys.exit(main())
