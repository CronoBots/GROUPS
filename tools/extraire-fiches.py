#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""On recopie tout ce que porte une fiche de paie Group S, sauf ce qui nomme la
personne, dans un JSON réutilisable pour les vérifications.

    python3 tools/extraire-fiches.py CONTRAT=TRI[,CONTRAT=TRI…] SORTIE.json FICHE.pdf [FICHE.pdf …]

POURQUOI. Le client, le 09/10/2026 : « garde quelque part toutes les infos
des fiches de paie que je vais t'envoyer, afin de pouvoir réutiliser les
chiffres pour toute une série de vérifications ». `comparer-fiches.py` ne
retient que des heures, pour une comparaison ; celui-ci recopie la fiche
entière, ligne par ligne, une fois pour toutes.

COMMENT. Une fiche n'a pas de structure de texte utile — son flux mélange
les deux colonnes. On la lit par la POSITION des mots (pymupdf) : la
colonne de gauche (x < 360) porte les lignes de rémunération et de retenue
— quantité, libellé, code A/B/D/F/G, montant —, la colonne de droite les
informations générales, les soldes d'année et le détail des jours ; le bas
de page le récapitulatif (brut, ONSS, imposable, précompte, net…), et les
pages d'un ouvrier le détail des prestations jour par jour.

CE QUI NE SORT JAMAIS : le bloc nom et adresse (en haut à droite de chaque
page), le numéro de registre national, le numéro de contrat (remplacé par
le trigramme qu'on donne), l'IBAN et le BIC, la référence de diffusion
électronique (elle contient le numéro de registre national), les numéros
de dossier. On ne les recopie pas : on ne lit que les zones où ils ne sont
pas.

LA GARANTIE, comme partout dans ce dépôt : chaque mot du bloc nom et
adresse, le numéro de registre national, l'IBAN, le BIC, la référence et le
numéro de contrat sont relevés sur la fiche ELLE-MÊME, puis cherchés dans
la sortie. Un seul, et rien n'est écrit.

LA SORTIE PORTE DES MONTANTS DE SALAIRE : elle n'entre JAMAIS dans ce dépôt
public (CLAUDE.md, « Aucun montant de salaire non plus »). Elle s'écrit hors
du dépôt, et l'outil refuse une sortie sous la racine du dépôt. Les fiches
elles-mêmes non plus : l'outil les refuse si elles sont dans le dépôt.
"""
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

QTE = re.compile(r"^-?\d+(?::\d{2})?$")
NOMBRE = re.compile(r"^-?[\d.]+,\d+$|^-?\d+$")
DATE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
JOURS = {"Lu", "Ma", "Me", "Je", "Ve", "Sa", "Di"}
RECAP = ["brut", "retenue_securite_sociale", "imposable", "precompte",
         "net", "divers_positifs", "divers_negatifs", "net_a_recevoir"]
# informations générales qui identifient : jamais recopiées
INFOS_INTERDITES = ("N° contrat", "N° registre national")


def nombre(t):
    """« 1.171,48 » → 1171.48 ; « -306,44 » → -306.44 ; « 22 » → 22."""
    t = t.rstrip(":")
    if not NOMBRE.match(t):
        return None
    return float(t.replace(".", "").replace(",", "."))


def heures(t):
    """« 168:00 » → 168.0 ; « -4:30 » → -4.5 ; « 22 » → None (un nombre)."""
    m = re.match(r"^(-?)(\d+):(\d{2})$", t)
    if not m:
        return None
    v = int(m.group(2)) + int(m.group(3)) / 60
    return round(-v if m.group(1) else v, 4)


def iso(d):
    j, m, a = d.split(".")
    return "%s-%s-%s" % (a, m, j)


def lignes_de(page, fin=False):
    """[(y arrondi, [(x, mot), …])] trié ; avec fin=True, (x, x1, mot)."""
    rows = {}
    for w in page.get_text("words"):
        m = (round(w[0]), round(w[2]), w[4]) if fin else (round(w[0]), w[4])
        rows.setdefault(round(w[1]), []).append(m)
    return [(y, sorted(rows[y])) for y in sorted(rows)]


def sensibles(doc):
    """Ce qui nomme la personne, relevé sur la fiche elle-même."""
    s = set()
    fiche = "Fiche de paie" in doc[0].get_text()
    for page in doc:
        for y, mots in lignes_de(page):
            # le bloc nom et adresse d'une fiche mensuelle : des lignes qui
            # COMMENCENT à x≈335, entre y 140 et 215. Ailleurs (le compte
            # individuel) cette zone porte des montants, et les prendre pour
            # des noms a fermé la garantie sur 48 chiffres le 09/10/2026.
            if fiche and 140 <= y <= 215 and mots and 330 <= mots[0][0] <= 345:
                for x, t in mots:
                    s.add(t)
            for x, t in mots:
                m = re.match(r"^(\d{2})(\d{2})(\d{2})-?\d{3}-\d{2}$", t)
                if m:
                    # la date de naissance est dans le numéro de registre national
                    for siecle in ("19", "20"):
                        s.add("%s.%s.%s%s" % (m.group(3), m.group(2), siecle, m.group(1)))
                if re.match(r"^\d{6}-?\d{3}-\d{2}$", t) or re.match(r"^\d{20,}$", t) \
                        or re.match(r"^\d{5}/\d-\d{6}$", t):
                    s.add(t)
            texte = " ".join(t for _, t in mots)
            m = re.search(r"BIC\s+(\S+)\s+-\s+IBAN\s+((?:\S+\s?){4})", texte)
            if m:
                s.add(m.group(1))
                s.add(m.group(2).replace(" ", ""))
                for morceau in m.group(2).split():
                    s.add(morceau)
            m = re.search(r"N° contrat\s+(\d+)", texte)
            if m:
                s.add(m.group(1))
    # les mots courts ou communs du bloc adresse (« RUE », un numéro) ne
    # nomment personne et feraient crier la garantie pour rien
    return set(t for t in s if len(t) >= 4 and not re.match(r"^(RUE|AVENUE|CHAUSSEE|PLACE)$", t, re.I))


# lignes d'un document annexe qui identifient : jamais recopiées
LIBELLES_INTERDITS = ("Date de naissance", "Sexe", "Nationalit", "N° registre",
                      "Travailleur", "Référence pour diffusion")
COLONNES_TRIM = [("T1", 290), ("T2", 350), ("T3", 410), ("T4", 470), ("total", 530)]


def lire_annexe(chemin, doc, contrats, interdits):
    """Un document qui n'est pas une fiche mensuelle — le compte individuel
    annuel, une fiche fiscale scannée. Les tableaux par trimestre du compte
    individuel sont lus ligne par ligne ; TOUT le reste est recopié mot par
    mot avec sa position (page, y, x), pour qu'on puisse le relire plus tard
    sans redemander le document. Les mots identifiants (relevés sur toutes
    les fiches reçues) et les lignes identifiantes sont retirés."""
    texte1 = " ".join(t for _, mots in lignes_de(doc[0]) for _, t in mots)
    contrat = next((c for c in contrats if c in texte1.replace(" ", "")), None)
    if contrat is None:
        for page in doc:
            for _, mots in lignes_de(page):
                for _, t in mots:
                    if t in contrats:
                        contrat = t
    if contrat is None:
        raise ValueError("%s : aucun contrat connu dans le document" % chemin)
    a = {"fichier": re.sub(r"^[0-9a-f]{8}-", "", os.path.basename(chemin)),
         "trigramme": contrats[contrat],
         "type": "compte individuel" if "Compte individuel" in texte1 else "autre",
         "pages": len(doc), "trimestres": [], "mots": []}
    m = re.search(r"Période\s*:\s*(\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})", texte1)
    if m:
        a["periode"] = [iso(m.group(1)), iso(m.group(2))]
    courant = None
    for n, page in enumerate(doc, 1):
        for y, mots in lignes_de(page, fin=True):
            texte = " ".join(t for _, _, t in mots)
            if any(texte.startswith(l) or (" " + l) in texte for l in LIBELLES_INTERDITS):
                continue
            garde = [(x, t) for x, _, t in mots if t not in interdits]
            # (au-dessus de y 100, l'en-tête de page : nom, employeur/contrat)
            if a["type"] == "compte individuel" and n in (2, 3) and y >= 100:
                lab = [t for x, x1, t in mots if x < 250]
                vals = [(x1, t) for x, x1, t in mots if x >= 250]
                if vals and (nombre(vals[0][1]) is not None or heures(vals[0][1]) is not None):
                    col = {}
                    for x1, t in vals:
                        nom = min(COLONNES_TRIM, key=lambda c: abs(c[1] - x1))[0]
                        col[nom] = t
                    if lab:
                        courant = {"libelle": " ".join(lab), "valeurs": col}
                        a["trimestres"].append(courant)
                    elif courant is not None:
                        courant["montants"] = col
                    continue
            if garde:
                a["mots"].append([n, y, garde])
    return a


def lire(chemin, contrats, interdits=()):
    import pymupdf
    doc = pymupdf.open(chemin)
    if "Fiche de paie" not in doc[0].get_text():
        return lire_annexe(chemin, doc, contrats, interdits)
    fiche = {"fichier": re.sub(r"^[0-9a-f]{8}-", "", os.path.basename(chemin)),
             "informations": {}, "soldes": {}, "jours": [],
             "remunerations": [], "bases": [], "retenues": [],
             "totaux": {}, "recapitulatif": {}, "prestations": []}
    # le contrat se lit sur la fiche, puis se remplace par le trigramme
    contrat = None
    for y, mots in lignes_de(doc[0]):
        texte = " ".join(t for _, t in mots)
        m = re.search(r"N° contrat\s+(\d+)", texte)
        if m:
            contrat = m.group(1)
    if contrat not in contrats:
        raise ValueError("%s : contrat %s sans trigramme donné" % (chemin, contrat))
    fiche["trigramme"] = contrats[contrat]
    m = re.search(r"-(\d{8})(?:_(\d+))?\.pdf$", chemin)
    if m:
        fiche["emise_fichier"] = "%s-%s-%s" % (m.group(1)[:4], m.group(1)[4:6], m.group(1)[6:])
        fiche["variante"] = int(m.group(2)) if m.group(2) else 0
    section = "remunerations"
    jour = None
    for page in doc:
        for y, mots in lignes_de(page):
            texte = " ".join(t for _, t in mots)
            # en-tête : la période et la date d'émission seulement
            if "Période" in texte and "du" in texte:
                ds = [t for _, t in mots if DATE.match(t)]
                if len(ds) == 2:
                    fiche["periode"] = [iso(ds[0]), iso(ds[1])]
                continue
            if 225 <= y <= 245 and len(mots) == 1 and DATE.match(mots[0][1]) and mots[0][0] > 450:
                fiche["emise"] = iso(mots[0][1])
                continue
            if mots and mots[0][1] == "EUR" and len(mots) == 9:
                fiche["recapitulatif"] = dict(zip(RECAP, (nombre(t) for _, t in mots[1:])))
                continue
            if texte.startswith("Rémunérations"):
                section = "remunerations"
                continue
            if texte.startswith("Retenues sociales"):
                section = "retenues"
                continue
            if texte.startswith("Détail des prestations"):
                section = "prestations"
                continue
            # prestations jour par jour (ouvrier) : date à x≈65, heures à x≈115
            if section == "prestations":
                if mots and mots[0][1] in JOURS and len(mots) > 1 and DATE.match(mots[1][1]):
                    jour = {"date": iso(mots[1][1]), "lignes": []}
                    fiche["prestations"].append(jour)
                    mots = mots[2:]
                if jour is not None and mots and 105 <= mots[0][0] <= 125 and QTE.match(mots[0][1]):
                    jour["lignes"].append({"quantite": mots[0][1], "heures": heures(mots[0][1]),
                                           "libelle": " ".join(t for _, t in mots[1:])})
                continue
            # sous le tableau : les intitulés du récapitulatif (déjà lu par sa
            # ligne « EUR ») et le virement, IBAN et BIC compris — la garantie
            # l'a arrêté le 09/10/2026, la ligne du virement entrait dans les
            # informations générales
            if y < 290 or y >= 680:
                continue
            gauche = [(x, t) for x, t in mots if x < 360]
            droite = [(x, t) for x, t in mots if x >= 360]
            if gauche:
                lire_gauche(fiche, section, gauche)
            if droite:
                lire_droite(fiche, droite)
    return fiche


def lire_gauche(fiche, section, mots):
    if mots[0][1] == "TOTAL":
        v = [nombre(t) for _, t in mots if nombre(t) is not None]
        fiche["totaux"][section] = v[-1] if v else None
        return
    code = [i for i, (x, t) in enumerate(mots) if 276 <= x <= 292 and re.match(r"^[A-Z]$", t)]
    ligne = {}
    if code:
        i = code[0]
        avant, apres = mots[:i], mots[i + 1:]
        ligne["code"] = mots[i][1]
        if apres:
            ligne["montant"] = nombre(apres[-1][1])
    else:
        avant = mots
        # « libellé : valeur » (bases, chèques-repas, indemnités…) ou
        # « libellé valeur » (salaire horaire)
        if len(avant) > 1 and nombre(avant[-1][1]) is not None and avant[-1][0] > 100:
            ligne["valeur"] = nombre(avant[-1][1])
            avant = avant[:-1]
    if avant and avant[0][0] < 45 and QTE.match(avant[0][1]):
        ligne["quantite"] = avant[0][1]
        h = heures(avant[0][1])
        if h is not None:
            ligne["heures"] = h
        avant = avant[1:]
    ligne["libelle"] = " ".join(t for _, t in avant)
    if section == "retenues":
        fiche["retenues"].append(ligne)
    elif "code" in ligne or "quantite" in ligne and "valeur" not in ligne:
        fiche["remunerations"].append(ligne)
    else:
        fiche["bases"].append(ligne)


def lire_droite(fiche, mots):
    texte = " ".join(t for _, t in mots)
    if texte.startswith(("Informations générales", "Détail des jours")):
        return
    # détail des jours : « 22 Jour(s) presté(s) »
    if mots[0][0] < 370 and re.match(r"^\d+$", mots[0][1]):
        fiche["jours"].append({"nombre": int(mots[0][1]),
                               "libelle": " ".join(t for _, t in mots[1:])})
        return
    lab = [t for x, t in mots if x < 490]
    val = [t for x, t in mots if x >= 490]
    cle = " ".join(lab)
    if cle.startswith(INFOS_INTERDITES):
        return
    if "solde d'année" in cle:
        fiche["soldes"][cle] = nombre(" ".join(val)) if val else None
    else:
        fiche["informations"][cle] = " ".join(val)


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    contrats = dict(c.split("=") for c in sys.argv[1].split(","))
    sortie = os.path.abspath(sys.argv[2])
    if os.path.commonpath([sortie, RACINE]) == RACINE:
        sys.exit("La sortie porte des montants de salaire : jamais dans le dépôt public.")
    import pymupdf
    fiches, interdits = [], set(contrats)
    for chemin in sys.argv[3:]:
        if os.path.commonpath([os.path.abspath(chemin), RACINE]) == RACINE:
            sys.exit("%s : une fiche de paie n'a rien à faire dans le dépôt." % chemin)
        interdits |= sensibles(pymupdf.open(chemin))
    for chemin in sys.argv[3:]:
        fiches.append(lire(chemin, contrats, interdits))
    # une fiche reçue deux fois (même fichier d'origine) ne compte qu'une fois
    vus, uniques = set(), []
    for f in fiches:
        cle = json.dumps(f, sort_keys=True, ensure_ascii=False)
        if cle not in vus:
            vus.add(cle)
            uniques.append(f)
    uniques.sort(key=lambda f: (f["trigramme"], f.get("emise_fichier", f["fichier"]), f.get("variante", 0)))
    texte = json.dumps({"fiches": uniques}, ensure_ascii=False, indent=1)
    # mot ENTIER : un code postal se retrouve sinon au milieu d'un montant
    restes = sorted(t for t in interdits
                    if re.search(r"(?<![\w.,:/-])" + re.escape(t) + r"(?![\w.,:/-])", texte))
    if restes:
        sys.exit("GARANTIE : %d donnée(s) identifiante(s) dans la sortie — rien n'est écrit."
                 % len(restes))
    with open(sortie, "w", encoding="utf-8") as f:
        f.write(texte)
    print("%d fiche(s) lue(s), %d distincte(s) — %s" % (len(fiches), len(uniques), sortie))
    print("%d donnée(s) identifiante(s) relevée(s) sur les fiches et cherchée(s) : aucune dans la sortie."
          % len(interdits))


if __name__ == "__main__":
    main()
