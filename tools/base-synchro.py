#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recopier l'horaire installé dans la base BIOWANZE (étape 2).

Le client, le 20/10/2026 : remplacer le classeur Excel par la saisie dans
l'application, en trois étapes ; la deuxième fait saisir la RH dans
l'application pendant que le classeur continue d'arriver. La base doit donc
porter, à tout moment, ce que le classeur écrit : ce script lui envoie
data/horaire-AAAA.json, personne par personne, quand la version de la base
(« maj ») n'est pas celle du fichier. Rien ne se renvoie pour rien.

Une journée SAISIE dans l'application n'est jamais écrasée : c'est la base
qui le garantit (public.biowanze_synchro, base/03-synchro.sql).

La clé est le secret PUSH_CLE, celle des notifications : la base n'en garde
que l'empreinte. Sans elle, le script ne fait rien et le dit.

    PUSH_CLE=… python3 tools/base-synchro.py            # ce qui a changé
    PUSH_CLE=… python3 tools/base-synchro.py --tout     # tout, même à jour
"""
import json
import os
import sys
import urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUPABASE = "https://pnizdddritizjbsksoir.supabase.co"
CLE_PUBLIQUE = "sb_publishable_FzetjMxWmdjSaTHWl1uZSg_HhMyErQI"
LOT = 12          # personnes par appel : un appel reste sous la seconde


def rpc(nom, corps):
    req = urllib.request.Request(
        SUPABASE + "/rest/v1/rpc/" + nom,
        data=json.dumps(corps).encode("utf-8"),
        headers={"apikey": CLE_PUBLIQUE, "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8") or "null")


def horaires():
    out = []
    dossier = os.path.join(RACINE, "data")
    for f in sorted(os.listdir(dossier)):
        if f.startswith("horaire-") and f.endswith(".json"):
            d = json.load(open(os.path.join(dossier, f), encoding="utf-8"))
            if not d.get("projete"):
                out.append(d)
    return out


def main():
    cle = os.environ.get("PUSH_CLE")
    if not cle:
        print("Base : secret PUSH_CLE absent, rien recopié.")
        return 0
    tout = "--tout" in sys.argv
    etat = {int(x["annee"]): x["maj"] for x in (rpc("biowanze_synchro_etat", {"p_cle": cle}) or [])}
    faits = []
    for d in horaires():
        an, maj = int(d["year"]), d.get("maj") or ""
        if not tout and etat.get(an) == maj:
            continue
        gens = [{"t": p["id"], "cat": p.get("cat") or "", "d": p.get("d") or {}}
                for p in d["people"]]
        n_p = n_j = 0
        for i in range(0, len(gens), LOT):
            fin = i + LOT >= len(gens)
            r = rpc("biowanze_synchro", {"p_cle": cle, "p_annee": an, "p_maj": maj,
                                          "p_lot": gens[i:i + LOT], "p_fin": fin})
            n_p += r.get("personnes", 0)
            n_j += r.get("journees", 0)
        faits.append("%d (%d personnes, %d journées)" % (an, n_p, n_j))
    print("Base : " + ("recopié " + ", ".join(faits) if faits else "déjà à jour."))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:      # le robot ne tombe jamais pour la base
        print("Base : non recopiée (%s : %s)." % (type(e).__name__, str(e)[:160]))
        sys.exit(0)
