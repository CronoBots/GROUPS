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


def lire_gmail(imap, sujet, dest):
    """Le dernier e-mail du sujet donné : sa pièce jointe écrite dans
    `dest`. Rend les uids de tous ces e-mails ([] s'il n'y en a pas). La pièce jointe se reconnaît à son contenu (une archive ZIP), pas à
    son nom : Power Automate peut l'appeler par l'identifiant du fichier."""
    typ, data = imap.uid("search", None, '(SUBJECT "%s")' % sujet)
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


def main():
    user, mdp = os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD")
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
            uids = lire_gmail(imap, sujet, source)
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
            h = [x[6] for x in installes if x[0] == "horaire"]
            r = [x[6] for x in installes if x[0] != "horaire"]
            if h and r:
                titre = "Horaire et recyclages mis à jour"
                texte = "Classeur du %s · recyclages enregistrés le %s." % (h[0], r[0])
            elif h:
                titre = "Horaire mis à jour"
                texte = "Classeur du %s · ouvrez l'application pour voir vos journées." % h[0]
            else:
                titre = "Recyclages mis à jour"
                texte = "Enregistrés le %s · voir le recyclage dans l'onglet Équipes." % r[0]
            n = subprocess.run(["node", os.path.join(OUTILS, "envoyer-push.js"), titre, texte],
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
