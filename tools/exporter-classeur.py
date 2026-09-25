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

Cet outil-ci ne lit rien : il RECOPIE. Chaque feuille, chaque cellule non
vide à son adresse, chaque commentaire, chaque fusion. Ce qui n'est pas
compris aujourd'hui reste disponible demain, en JSON, sans avoir à rouvrir
un classeur ni à savoir lire du XML.

IL PART DU CLASSEUR DÉJÀ ANONYMISÉ, ET C'EST TOUT L'ARGUMENT. Anonymiser à
nouveau ici demanderait d'écrire une troisième fois des motifs de noms, donc
d'ouvrir un troisième trou. data/classeur-2026.xlsx est passé par
l'anonymiseur ET par son second contrôle indépendant : il ne porte plus de
nom, et c'est prouvé. On recopie une source propre plutôt que de nettoyer
une source sale.

    python3 tools/exporter-classeur.py data/classeur-2026.xlsx \
            data/classeur-2026-brut.json

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

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
# QUELQU'UN. Le classeur en porte un, « RT0xxxx », écrit au fil de six
# commentaires — la même phrase recopiée d'une feuille à l'autre. L'anonymiseur
# le laisse passer, et il a raison : il remplace des NOMS, et ce n'en est pas
# un. Le convertisseur, lui, l'emportait par accident, parce qu'il ouvrait une
# tête de commentaire.
#
# Ici rien ne l'emporte : cet outil recopie. Dans un dépôt PUBLIC, un login
# d'entreprise se recoupe avec les annuaires de la maison aussi sûrement qu'un
# nom. Il part donc, remplacé et non effacé — « (identifiant retiré) » laisse
# lire la phrase, et dit qu'on a retiré quelque chose.
#
# Le motif est étroit À DESSEIN : deux lettres et quatre à six chiffres, d'un
# seul tenant. Mesuré sur l'export entier : UN seul jeton de cette forme, six
# occurrences. Un motif plus large avalerait des codes d'horaire.
# La règle vit dans le convertisseur, et cet outil l'emprunte : DEUX COPIES
# D'UN MÊME MOTIF DIVERGENT, et c'est toujours la seconde qui reste en
# arrière — le projet en a la démonstration. La doctrine qui veut que deux
# outils ne s'empruntent pas leurs motifs vaut pour les NOMS, où la
# contradiction est le contrôle ; un login n'est pas un nom, et il n'y a rien
# à vérifier par recoupement : soit la forme est là, soit elle n'y est pas.
def _sans_login(t, cv):
    return cv.LOGIN.sub("(identifiant retiré)", t)


def _adresse(ligne, colonne):
    """(12, 3) -> « C12 »."""
    lettres, n = "", colonne
    while n > 0:
        n, r = divmod(n - 1, 26)
        lettres = chr(65 + r) + lettres
    return "%s%d" % (lettres, ligne)


def exporter(chemin, cv):
    cl = cv.Classeur(chemin)
    feuilles = {}
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
        try:
            cm = cl.commentaires(nom)
        except Exception as e:                      # pragma: no cover
            sys.stderr.write("  %s : commentaires illisibles (%s)\n" % (nom, e))
            cm = {}
        commentaires = dict((_adresse(l, c), _sans_login(t, cv))
                            for (l, c), t in cm.items())
        feuilles[nom] = {
            "cellules": cellules,
            "commentaires": commentaires,
            "fusions": _fusions_de(cl, nom, cv),
        }
    return {
        "source": os.path.basename(chemin),
        "genere": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "feuilles": feuilles,
    }


def _fusions_de(cl, nom, cv):
    """Les étendues fusionnées, telles que le classeur les déclare."""
    import xml.etree.ElementTree as ET
    racine = ET.fromstring(cl.z.read(cl.feuilles[nom]))
    out = []
    for m in racine.iter('{%s}mergeCell' % cv.M):
        ref = m.get('ref') or ""
        if ":" in ref:
            out.append(ref)
    return out


def main():
    if len(sys.argv) < 2:
        sys.stderr.write(__doc__)
        return 2
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        RACINE, "data", "classeur-2026-brut.json")
    cv = _convertisseur()
    out = exporter(src, cv)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"),
                  sort_keys=True)
    nc = sum(len(v["cellules"]) for v in out["feuilles"].values())
    nm = sum(len(v["commentaires"]) for v in out["feuilles"].values())
    nf = sum(len(v["fusions"]) for v in out["feuilles"].values())
    print("%d feuille(s) · %d cellule(s) · %d commentaire(s) · %d fusion(s)"
          % (len(out["feuilles"]), nc, nm, nf))
    print("%s — %.1f Mo" % (dst, os.path.getsize(dst) / 1048576.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
