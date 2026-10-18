#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La mise à jour de l'horaire sans personne au clavier — lancée chaque heure
par GitHub (.github/workflows/horaire-auto.yml).

    python3 tools/horaire-auto.py                  # lit Gmail, installe, pousse
    python3 tools/horaire-auto.py --fichier=X.xlsm --sans-pousser   # essai local

Le chemin, établi avec le client le 16/10/2026 :

  1. son PC virtuel copie chaque jour le récapitulatif du serveur vers un
     dossier OneDrive (Planificateur de tâches, robocopy) ;
  2. Power Automate, à chaque modification du fichier, le lui envoie en pièce
     jointe sur Gmail, sujet « BIOWANZE horaire » ;
  3. ce script lit le DERNIER de ces e-mails par IMAP, met le classeur dans
     un dossier temporaire HORS du dépôt, et lance `mettre-a-jour.py` : les
     huit portes, puis l'installation. Il pousse sur main, met les e-mails à
     la corbeille et envoie au client le rapport de ce qui a bougé.

CE QUI NE S'IMPRIME JAMAIS : le compte rendu des portes. Une porte fermée
imprime son contexte, et le contexte d'une garantie d'anonymat qui s'est
fermée EST le nom qu'elle a trouvé. Le journal d'une action GitHub est
PUBLIC sur un dépôt public : il ne reçoit que des lignes d'état. Le compte
rendu entier part par e-mail au client, dans sa boîte à lui.

DEUX REFUS DE PLUS que l'installation à la main : une personne NOUVELLE
(CLAUDE.md : une arrivée se fait toujours confirmer — qui, quelle fonction,
intérimaire ou non) n'est installée que si son trigramme est dans
`tools/arrivees-confirmees.txt` ; et un horaire identique à celui en place
n'installe rien, pas même `V`.

LE CLASSEUR DES RECYCLAGES suit le même chemin depuis le 16/10/2026 (le
client : « peut-on mettre cela en place pour le fichier des recyclages
aussi ? ») : un e-mail « BIOWANZE recyclage » porte le classeur RH, que
`mettre-a-jour-recyclage.py --installer` fait passer par ses onze portes.
Son brut vit hors du dépôt, donc absent ici : l'outil réinstallerait à chaque
passage. On regarde donc si `data/recyclages-2026.json` a VRAIMENT changé, et
sinon `sw.js` est remis comme avant — pas de `V` qui bouge pour rien.

Secrets : GMAIL_USER, GMAIL_APP_PASSWORD (mot de passe d'application Google).
"""
import email
import imaplib
import json
import os
import re
import smtplib
import subprocess
import sys
import tempfile
from email.message import EmailMessage

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTILS = os.path.join(RACINE, "tools")
SUJET = "BIOWANZE horaire"
SUJET_RECYC = "BIOWANZE recyclage"
RECYC = os.path.join(RACINE, "data", "recyclages-2026.json")
HORAIRE = os.path.join(RACINE, "data", "horaire-2026.json")
CONFIRMEES = os.path.join(OUTILS, "arrivees-confirmees.txt")


def etat(texte):
    """Une ligne d'état, la seule chose qui va au journal public."""
    print(texte, flush=True)


def _option(nom):
    for a in sys.argv[1:]:
        if a.startswith(nom + "="):
            return a.split("=", 1)[1]
    return None


def lire_gmail(imap, sujet, dest, moi=None):
    """Le dernier e-mail du sujet donné : sa pièce jointe écrite dans
    `dest`. Rend les uids de tous ces e-mails ([] s'il n'y en a pas). La pièce jointe se reconnaît à son contenu (une archive ZIP), pas à
    son nom : Power Automate peut l'appeler par l'identifiant du fichier.

    JAMAIS ses propres rapports. Le 16/10/2026, de 11 h 45 à 16 h 45, le
    rapport « BIOWANZE · horaire NON installé », envoyé à la même adresse,
    répondait à la recherche (Gmail cherche par mots : « BIOWANZE » et
    « horaire » y sont) : sans pièce jointe, il partait à la corbeille et
    un nouveau rapport le remplaçait, 22 fois, toutes les 15 minutes,
    jusqu'à l'arrivée d'un vrai classeur (relu dans la boîte par le
    connecteur Gmail, le 18/10/2026). Les e-mails de l'adresse du robot
    sont donc écartés."""
    crit = '(SUBJECT "%s")' % sujet if not moi else '(SUBJECT "%s" NOT FROM "%s")' % (sujet, moi)
    typ, data = imap.uid("search", None, crit)
    uids = sorted((data[0] or b"").split(), key=int)
    if not uids:
        return []
    typ, msg = imap.uid("fetch", uids[-1], "(RFC822)")
    m = email.message_from_bytes(msg[0][1])
    meilleure = None
    for part in m.walk():
        if part.get_content_maintype() == "multipart":
            continue
        contenu = part.get_payload(decode=True) or b""
        if contenu[:2] == b"PK" and (meilleure is None or len(contenu) > len(meilleure)):
            meilleure = contenu
    if meilleure is None:
        return uids                # un e-mail sans classeur : à la corbeille quand même
    with open(dest, "wb") as f:
        f.write(meilleure)
    return uids


def corbeille(imap, uids):
    """X-GM-LABELS \\Trash vaut quel que soit la langue du compte Gmail."""
    for u in uids:
        imap.uid("store", u, "+X-GM-LABELS", "\\Trash")
    imap.expunge()


def envoyer(user, mdp, sujet, corps):
    if not (user and mdp):
        print("\n" + sujet + "\n" + corps)       # essai local : à l'écran
        return
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = user, user, sujet
    msg.set_content(corps)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(user, mdp)
        s.send_message(msg)


def arrivees(rapport):
    """Les trigrammes que le comparateur annonce comme arrivés (« + XXX »)."""
    bloc = rapport.split("Personnes :", 1)
    if len(bloc) < 2:
        return []
    out = []
    for l in bloc[1].splitlines()[1:]:      # [0] : la fin de la ligne du titre
        if not l.strip():
            break
        m = re.match(r"\s*\+\s+(\S+)", l)
        if m:
            out.append(m.group(1))
    return out


def confirmees():
    try:
        lignes = open(CONFIRMEES, encoding="utf-8").read().splitlines()
    except OSError:
        return set()
    return set(l.split("#")[0].strip() for l in lignes if l.split("#")[0].strip())


def git(*args):
    return subprocess.run(["git", "-C", RACINE] + list(args),
                          capture_output=True, text=True)


def _quand(maj):
    try:
        d = maj.split("T")[0].split("-")
        return "%s/%s/%s à %s" % (d[2], d[1], d[0], maj.split("T")[1][:5].replace(":", " h "))
    except (IndexError, AttributeError):
        return str(maj)


def traiter_horaire(source):
    """Rend (code, sujet, corps, installé?, quand)."""
    r = subprocess.run([sys.executable, os.path.join(OUTILS, "mettre-a-jour.py"), source],
                       cwd=RACINE, capture_output=True, text=True)
    sortie = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        porte = re.search(r"PORTE FERMÉE à l'étape (\d+)", sortie)
        n = porte.group(1) if porte else "?"
        etat("Horaire : porte %s fermée, rien installé." % n)
        return (1, "BIOWANZE · horaire NON installé (porte %s fermée)" % n,
                "Une porte s'est fermée : rien n'a été installé. À transmettre à"
                " Claude tel quel.\n\n" + sortie[-12000:], False, "")
    memo = json.load(open(os.path.join(tempfile.gettempdir(),
                                       "biowanze-dernier-blanc.json"), encoding="utf-8"))
    neuf = os.path.join(memo["tmp"], "horaire-2026.json")
    rapport = open(os.path.join(memo["tmp"], "comparaison.txt"), encoding="utf-8").read()
    quand = _quand(json.load(open(neuf, encoding="utf-8")).get("maj", "?"))
    if open(neuf, "rb").read() == open(HORAIRE, "rb").read():
        etat("Horaire du %s : identique à celui en place, rien installé." % quand)
        return (0, "BIOWANZE · classeur du %s, rien de changé" % quand,
                "Les huit portes sont ouvertes, et l'horaire est identique à celui"
                " en place : rien n'a été installé.", False, quand)
    nouveaux = [t for t in arrivees(rapport) if t not in confirmees()]
    if nouveaux:
        etat("Horaire : arrivée(s) à confirmer (%s), rien installé." % ", ".join(nouveaux))
        return (1, "BIOWANZE · horaire NON installé : nouvelle personne à confirmer",
                "Le classeur du %s ajoute : %s.\n\nUne arrivée se fait toujours"
                " confirmer avant d'être installée : dire à Claude qui c'est, sa"
                " fonction, intérimaire ou non. Il l'ajoutera à"
                " tools/arrivees-confirmees.txt et le prochain envoi s'installera."
                "\n\nCe qui change :\n\n%s" % (quand, ", ".join(nouveaux), rapport),
                False, quand)
    r = subprocess.run([sys.executable, os.path.join(OUTILS, "mettre-a-jour.py"), source,
                        "--installer"], cwd=RACINE, capture_output=True, text=True)
    sortie = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        etat("Horaire : installation refusée par le garde-fou du dépôt.")
        return (1, "BIOWANZE · horaire NON installé (garde-fou du dépôt)",
                "Le garde-fou du dépôt a refusé l'installation ; les fichiers d'avant"
                " sont en place. À transmettre à Claude tel quel.\n\n" + sortie[-12000:],
                False, quand)
    etat("Horaire du %s installé." % quand)
    return (0, "BIOWANZE · horaire du %s installé" % quand,
            "L'application est à jour (classeur du %s).\n\nCe qui change :\n\n%s"
            % (quand, rapport), True, quand)


def traiter_recyclage(source):
    """Rend (code, sujet, corps, installé?, quand)."""
    sw = os.path.join(RACINE, "sw.js")
    sw_avant = open(sw, "rb").read()
    json_avant = open(RECYC, "rb").read() if os.path.exists(RECYC) else b""
    r = subprocess.run([sys.executable, os.path.join(OUTILS, "mettre-a-jour-recyclage.py"),
                        source, "--installer"], cwd=RACINE, capture_output=True, text=True)
    sortie = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        porte = re.search(r"PORTE FERMÉE à l'étape (\d+)", sortie)
        n = porte.group(1) if porte else "?"
        # rien ne doit rester à moitié posé
        open(sw, "wb").write(sw_avant)
        if json_avant:
            open(RECYC, "wb").write(json_avant)
        etat("Recyclages : porte %s fermée, rien installé." % n)
        return (1, "BIOWANZE · recyclages NON installés (porte %s fermée)" % n,
                "Une porte s'est fermée : rien n'a été installé. À transmettre à"
                " Claude tel quel.\n\n" + sortie[-12000:], False, "")
    m = re.search(r"══ CE QUI CHANGE.*?══\n\n(.*?)(?:\n\n(?:Réserve locale|Le recyclage installé|Installé|Les onze)|\Z)",
                  sortie, re.S)
    rapport = m.group(1).strip() if m else "(rapport introuvable)"
    quand = _quand(json.load(open(RECYC, encoding="utf-8")).get("maj", "?"))
    if open(RECYC, "rb").read() == json_avant:
        open(sw, "wb").write(sw_avant)
        etat("Recyclages du %s : identiques à ceux en place, rien installé." % quand)
        return (0, "BIOWANZE · recyclages enregistrés le %s, rien de changé" % quand,
                "Les onze portes sont ouvertes, et les recyclages sont identiques à"
                " ceux en place : rien n'a été installé.", False, quand)
    etat("Recyclages du %s installés." % quand)
    return (0, "BIOWANZE · recyclages enregistrés le %s installés" % quand,
            "L'application est à jour (classeur RH enregistré le %s).\n\nCe qui change :"
            "\n\n%s" % (quand, rapport), True, quand)


JOURS_C = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."]
JOURS_L = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
POSTES_RECYC = {"meun": "Meunerie", "glut": "Gluten", "ferm": "Fermentation",
                "dist": "Distillation", "chau": "Chaudières", "step": "STEP",
                "cm": "Contremaître"}


def _lire(chemin):
    try:
        return json.load(open(chemin, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _aujourdhui():
    import datetime
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo("Europe/Brussels")).date()
    except Exception:
        return datetime.date.today()


def _court(quand):
    """« 16/10/2026 à 13 h 45 » → « 16/10 à 13 h 45 » : l'année se devine."""
    return re.sub(r"^(\d\d/\d\d)/\d{4}", r"\1", quand or "")


def _desc_jour(j):
    """Ce que la cellule dit, sans le commentaire : « Repos », « AM »,
    « AM · MAL », « 18h-06h ». Un commentaire seul qui change ne compte pas,
    comme dans l'application (detecterChangements)."""
    j = j or []
    cel = (j[0] if len(j) > 0 else "").strip()
    ann = (j[1] if len(j) > 1 else "").strip()
    repos = cel in ("", "-")
    a = ann.rstrip(" ?").strip()
    # une absence d'une journée entière se dit seule, comme l'application :
    # « Maladie », « VA », et non « N · Abs »
    if re.fullmatch(r"(?i)abs\.?|mal", a):
        return "Maladie"
    m = re.fullmatch(r"(?i)(?:8\s*h\s*)?(VA|RTT|RJF|DTT|RHS|CP|TP|CT|CSS|GREVE)", a)
    if m:
        return m.group(1).upper()
    if re.fullmatch(r"(?i)8\s*h\s*-\s*FT", a):
        return "Flex time repris"
    if a == "-":
        return "Repos" if repos else "%s non presté" % cel
    # l'annotation qui est une pause ou une plage dit ce qui a été PRESTÉ :
    # elle remplace la pause prévue (« PM · N » se lit « N »)
    if re.fullmatch(r"(?i)AM|PM|N|D|\d{1,2}\s*h?\s*(\d\d)?'?\s*-\s*\d{1,2}\s*h?\s*(\d\d)?'?", a):
        return a
    base = "Repos" if repos else cel
    if a and a != cel:
        base = a if repos else base + " · " + a
    return base


def changements_horaire(avant, apres, annee, jour):
    """{id: [(date, avant, après)]} pour les journées d'aujourd'hui à la fin
    de l'année dont la cellule a changé."""
    import datetime
    av = {p.get("id"): p.get("d") or {} for p in avant.get("people") or []}
    out = {}
    for p in apres.get("people") or []:
        pid = p.get("id")
        if pid not in av:
            continue                         # une arrivée : rien à comparer
        d1, d2 = av[pid], p.get("d") or {}
        for k in sorted(set(d1) | set(d2)):
            try:
                dt = datetime.date(annee, int(k[:2]), int(k[2:]))
            except ValueError:
                continue
            if dt < jour:
                continue
            a, b = _desc_jour(d1.get(k)), _desc_jour(d2.get(k))
            if a != b:
                out.setdefault(pid, []).append((dt, a, b))
    return out


def postes_agenda(pid):
    """{date: poste} lu dans l'agenda de la personne (cal/<id>.ics), que
    mettre-a-jour.py vient de réécrire sur l'horaire installé : c'est la
    lecture de l'application elle-même (lectureAgenda : atelier écrit, sinon
    le poste habituel ce jour-là), et non une seconde copie de ses règles."""
    import datetime
    out, quand = {}, None
    try:
        lignes = open(os.path.join(RACINE, "cal", pid + ".ics"), encoding="utf-8").read().splitlines()
    except OSError:
        return out
    for l in lignes:
        m = re.match(r"UID:.*-(\d{8})@", l)
        if m:
            quand = datetime.date(int(m.group(1)[:4]), int(m.group(1)[4:6]), int(m.group(1)[6:]))
        elif l.startswith("SUMMARY:") and quand:
            morceaux = l[8:].split(" · ")
            if morceaux[0] in ("AM", "PM", "N") and len(morceaux) > 1 and morceaux[1] not in ("rappel", "Roue libre"):
                out[quand] = morceaux[1]
            quand = None
    return out


def message_horaire(liste, postes=None):
    """Titre et texte d'une notification « votre horaire a été modifié » :
    une ligne par journée, jamais regroupées, trois au plus, la plus proche
    en tête, toujours « Mercredi 21/10 : PM → N » (le client, le
    16/10/2026 : « il ne faut pas regrouper les jours »). Le titre seul :
    iOS le coupe à environ 28 signes, et « · 8 journées » devenait
    « · 8 j… » ; « + n autres journées » dit déjà combien."""
    postes = postes or {}
    # le poste d'un OPÉRATEUR sur une pause (le client, le 16/10/2026 : « go »),
    # comme la carte de l'application ; jamais pour un cadre, dont la
    # fonction ne change pas (postes vide)
    lignes = ["%s %s : %s → %s%s" % (JOURS_L[dt.weekday()], dt.strftime("%d/%m"), a, b,
                                     " · " + postes[dt] if b in ("AM", "PM", "N") and dt in postes else "")
              for dt, a, b in liste[:3]]
    reste = len(liste) - 3
    if reste > 0:
        lignes.append("+ %d autre%s journée%s" % (reste, "s" if reste > 1 else "", "s" if reste > 1 else ""))
    return ("Votre horaire a été modifié", "\n".join(lignes))


def changements_recyclage(avant, apres):
    """{trigramme: ([(poste, date)] ajoutés, nb retirés, restant)}."""
    out = {}
    av = avant.get("ops") or {}
    for t, o in (apres.get("ops") or {}).items():
        a = (av.get(t) or {}).get("dates") or {}
        b = o.get("dates") or {}
        ajout, retire = [], 0
        for poste in set(a) | set(b):
            la, lb = list(a.get(poste) or []), list(b.get(poste) or [])
            for x in lb:
                if x in la:
                    la.remove(x)
                else:
                    ajout.append((poste, x))
            retire += len(la)
        if ajout or retire:
            out[t] = (sorted(ajout, key=lambda x: x[1][3:] + x[1][:2]), retire, o.get("restant"))
    return out


def message_recyclage(ajout, retire, restant, annee=2026):
    """Même forme que l'horaire (le client, le 16/10/2026) : une ligne par
    recyclage, « Jeudi 15/10 : Chaudières », trois au plus, puis ce qui
    reste à faire. Les dates du classeur RH n'ont pas d'année : celle du
    classeur."""
    import datetime
    lignes = []
    for p, d in ajout[:3]:
        try:
            dt = datetime.date(annee, int(d[3:5]), int(d[:2]))
            quand = "%s %s" % (JOURS_L[dt.weekday()], d)
        except ValueError:
            quand = d
        lignes.append("%s : %s" % (quand, POSTES_RECYC.get(p, p)))
    if len(ajout) > 3:
        r = len(ajout) - 3
        lignes.append("+ %d autre%s recyclage%s" % (r, "s" if r > 1 else "", "s" if r > 1 else ""))
    if restant is not None:
        lignes.append("Encore %s recyclage%s à faire" % (restant, "s" if str(restant) not in ("0", "1") else ""))
    # le même style que « Votre horaire a été modifié » (le client, le
    # 16/10/2026) ; le nombre est dans les lignes, le titre reste court
    titre = ("Votre recyclage a été ajouté" if len(ajout) == 1 else
             "Vos recyclages ont été ajoutés" if ajout else "Vos recyclages ont été modifiés")
    return titre, "\n".join(lignes)


# Prévenus de CHAQUE classeur installé, même quand rien ne change pour eux
# (le client, le 16/10/2026 : « tant que maintenant, VBN reçoit aussi les
# mises à jour des classeurs horaires et recyclages même s'il n'y figure pas »).
TOUJOURS_PREVENIR = ("VBN",)


def notifications(avant_h, avant_r, installes):
    """Une notification par classeur installé, PERSONNELLE : chacun lit ce
    qui change pour lui (le client, le 16/10/2026 : « les notifications
    doivent être optimisées au max »). Celui pour qui rien ne change ne reçoit
    RIEN (le client, le même jour : « go ») : avec un classeur par jour, « rien
    ne change pour vous » devenait du bruit. Le trigramme de l'abonnement
    choisit le message ; sans trigramme, ou s'il ne désigne personne de
    connu, le message commun."""
    out = []
    for x in installes:
        quand = _court(x[6])
        if x[0] == "horaire":
            apres = _lire(HORAIRE)
            ch = changements_horaire(avant_h, apres, int(apres.get("year") or 2026), _aujourdhui())
            par, connus = {}, []
            for p in apres.get("people") or []:
                pid = p.get("id")
                connus.append(pid)
                if pid in ch:
                    cadre = p.get("cat") == "Contremaîtres de production"
                    t, b = message_horaire(ch[pid], {} if cadre else postes_agenda(pid))
                    par[pid] = {"title": t, "body": b}
            for pid in TOUJOURS_PREVENIR:
                par.setdefault(pid, {"title": "Horaire mis à jour",
                                     "body": "Classeur du %s · rien ne change pour vous." % quand})
            out.append({"tag": "horaire", "url": "./?vue=horaire", "par_tri": par, "connus": connus,
                        "defaut": {"title": "Horaire mis à jour",
                                   "body": "Classeur du %s · ouvrez l'application pour voir vos journées." % quand}})
        else:
            apres = _lire(RECYC)
            ch = changements_recyclage(avant_r, apres)
            par = {}
            for t in ch:
                ti, b = message_recyclage(*ch[t])
                par[t] = {"title": ti, "body": b}
            for t in TOUJOURS_PREVENIR:
                par.setdefault(t, {"title": "Recyclages mis à jour",
                                   "body": "Classeur RH du %s · rien ne change pour vous." % quand})
            # les recyclages ne visent que des opérateurs, mais tout le monde
            # est connu de l'horaire : un contremaître n'en reçoit aucun
            connus = [p.get("id") for p in (_lire(HORAIRE).get("people") or [])]
            out.append({"tag": "recyclage", "url": "./?vue=equipe", "par_tri": par, "connus": connus,
                        "defaut": {"title": "Recyclages mis à jour",
                                   "body": "Classeur RH du %s · le recyclage est dans l'onglet Équipes." % quand}})
    return out


def main():
    user, mdp = os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD")
    avant_h, avant_r = _lire(HORAIRE), _lire(RECYC)
    pousser = "--sans-pousser" not in sys.argv
    tmp = tempfile.mkdtemp(prefix="biowanze-auto-")
    imap = None
    lots = []          # (genre, source, uids)

    local = _option("--fichier")
    local_r = _option("--recyclage")
    if local or local_r:
        if local:
            lots.append(("horaire", os.path.abspath(local), []))
        if local_r:
            lots.append(("recyclage", os.path.abspath(local_r), []))
    else:
        if not (user and mdp):
            sys.exit("GMAIL_USER et GMAIL_APP_PASSWORD manquent.")
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(user, mdp)
        imap.select("INBOX")
        for genre, sujet, nom in (("horaire", SUJET, "Recapitulatif.xlsm"),
                                  ("recyclage", SUJET_RECYC, "Suivi_recyclages.xlsx")):
            source = os.path.join(tmp, nom)
            uids = lire_gmail(imap, sujet, source, user)
            if not uids:
                continue
            etat("%d e-mail(s) « %s » ; le plus récent est lu." % (len(uids), sujet))
            if not os.path.exists(source):
                corbeille(imap, uids)
                envoyer(user, mdp, "BIOWANZE · %s NON installé" % genre,
                        "L'e-mail « %s » ne portait pas de classeur en pièce jointe."
                        " Vérifier le flux Power Automate (pièce jointe : File content)." % sujet)
                etat("%s : pas de classeur en pièce jointe, rien installé." % genre.capitalize())
                continue
            lots.append((genre, source, uids))
        if not lots:
            etat("Aucun e-mail « %s » ni « %s » : rien à faire." % (SUJET, SUJET_RECYC))
            return 0

    resultats = []     # (genre, uids, code, sujet, corps, installé, quand)
    for genre, source, uids in lots:
        f = traiter_horaire if genre == "horaire" else traiter_recyclage
        resultats.append((genre, uids) + f(source))

    installes = [x for x in resultats if x[5]]
    publie = True
    if installes and pousser:
        fichiers = ["sw.js"]
        titres = []
        for x in installes:
            if x[0] == "horaire":
                fichiers += ["data/horaire-2026.json", "cal"]
                titres.append("Classeur du %s" % x[6])
            else:
                fichiers.append("data/recyclages-2026.json")
                titres.append("Recyclages enregistrés le %s" % x[6])
        git("add", *fichiers)
        message = ("%s (mise à jour automatique)\n\nPortes de mettre-a-jour.py et de"
                   " mettre-a-jour-recyclage.py ouvertes, installé par"
                   " .github/workflows/horaire-auto.yml." % " ; ".join(titres))
        c = git("commit", "-q", "-m", message)
        p = git("push", "-q", "origin", "HEAD:main") if c.returncode == 0 else c
        if p.returncode != 0:
            publie = False
            etat("Le commit ou l'envoi sur main a échoué.")
            print((p.stderr or "")[-2000:])
        else:
            etat("Poussé sur main.")
            # La notification du téléphone, application fermée (le client,
            # le 16/10/2026 : la même pour tous ; puis « je n'ai rien reçu
            # pour le recyclage » : les recyclages aussi). Une seule par
            # passage, même étiquette. Elle ne fait jamais échouer le
            # passage : tout est déjà publié.
            # Puis personnelles (« optimisées au max ») : voir notifications().
            try:
                msgs = notifications(avant_h, avant_r, installes)
            except Exception as e:           # jamais d'échec pour une notification
                msgs = []
                etat("Notifications : messages non calculés (%s)." % type(e).__name__)
            for m in msgs:
                chemin = os.path.join(tmp, "notif-%s.json" % m["tag"])
                json.dump(m, open(chemin, "w", encoding="utf-8"), ensure_ascii=False)
                n = subprocess.run(["node", os.path.join(OUTILS, "envoyer-push.js"),
                                    "--messages=" + chemin],
                                   cwd=RACINE, capture_output=True, text=True)
                etat((n.stdout or "").strip() or "Notifications : non envoyées.")

    code = 0
    for genre, uids, c, sujet, corps, inst, quand in resultats:
        if inst and pousser and not publie:
            c, sujet = 1, "BIOWANZE · %s NON publié" % genre
            corps = ("Installé, mais le commit ou l'envoi sur main a échoué. À"
                     " transmettre à Claude.\n\n" + corps)
        if imap is not None and uids:
            corbeille(imap, uids)
        envoyer(user, mdp, sujet, corps)
        code = max(code, c)
    return code


if __name__ == "__main__":
    sys.exit(main())
