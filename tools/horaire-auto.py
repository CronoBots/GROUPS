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


def lire_gmail(user, mdp, dest):
    """Le dernier e-mail « BIOWANZE horaire » : sa pièce jointe écrite dans
    `dest`. Rend (imap, uids de tous ces e-mails) ou (None, []) s'il n'y en a
    pas. La pièce jointe se reconnaît à son contenu (une archive ZIP), pas à
    son nom : Power Automate peut l'appeler par l'identifiant du fichier."""
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user, mdp)
    imap.select("INBOX")
    typ, data = imap.uid("search", None, '(SUBJECT "%s")' % SUJET)
    uids = sorted((data[0] or b"").split(), key=int)
    if not uids:
        return imap, []
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
        return imap, uids          # un e-mail sans classeur : à la corbeille quand même
    with open(dest, "wb") as f:
        f.write(meilleure)
    return imap, uids


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


def main():
    user, mdp = os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD")
    pousser = "--sans-pousser" not in sys.argv
    tmp = tempfile.mkdtemp(prefix="biowanze-auto-")
    source = os.path.join(tmp, "Recapitulatif.xlsm")
    imap, uids = None, []

    local = _option("--fichier")
    if local:
        source = os.path.abspath(local)
    else:
        if not (user and mdp):
            sys.exit("GMAIL_USER et GMAIL_APP_PASSWORD manquent.")
        imap, uids = lire_gmail(user, mdp, source)
        if not uids:
            etat("Aucun e-mail « %s » : rien à faire." % SUJET)
            return 0
        etat("%d e-mail(s) « %s » ; le plus récent est lu." % (len(uids), SUJET))
        if not os.path.exists(source):
            corbeille(imap, uids)
            envoyer(user, mdp, "BIOWANZE · horaire NON installé",
                    "L'e-mail « %s » ne portait pas de classeur en pièce jointe."
                    " Vérifier le flux Power Automate (pièce jointe : File content)." % SUJET)
            etat("Pas de classeur en pièce jointe : rien installé.")
            return 1

    def fin(code, sujet, corps):
        if imap is not None:
            corbeille(imap, uids)
        envoyer(user, mdp, sujet, corps)
        return code

    # 1. à blanc : les huit portes
    r = subprocess.run([sys.executable, os.path.join(OUTILS, "mettre-a-jour.py"), source],
                       cwd=RACINE, capture_output=True, text=True)
    sortie = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        porte = re.search(r"PORTE FERMÉE à l'étape (\d+)", sortie)
        etat("Porte %s fermée : rien installé." % (porte.group(1) if porte else "?"))
        return fin(1, "BIOWANZE · horaire NON installé (porte %s fermée)"
                   % (porte.group(1) if porte else "?"),
                   "Une porte s'est fermée : rien n'a été installé. À transmettre à"
                   " Claude tel quel.\n\n" + sortie[-12000:])

    memo = json.load(open(os.path.join(tempfile.gettempdir(),
                                       "biowanze-dernier-blanc.json"), encoding="utf-8"))
    neuf = os.path.join(memo["tmp"], "horaire-2026.json")
    rapport = open(os.path.join(memo["tmp"], "comparaison.txt"), encoding="utf-8").read()
    maj = json.load(open(neuf, encoding="utf-8")).get("maj", "?")
    try:
        d = maj.split("T")[0].split("-")
        quand = "%s/%s/%s à %s" % (d[2], d[1], d[0], maj.split("T")[1].replace(":", " h "))
    except IndexError:
        quand = maj

    if open(neuf, "rb").read() == open(HORAIRE, "rb").read():
        etat("Classeur du %s : horaire identique à celui en place, rien installé." % quand)
        return fin(0, "BIOWANZE · classeur du %s, rien de changé" % quand,
                   "Les huit portes sont ouvertes, et l'horaire est identique à celui"
                   " en place : rien n'a été installé.")

    nouveaux = [t for t in arrivees(rapport) if t not in confirmees()]
    if nouveaux:
        etat("Arrivée(s) à confirmer (%s) : rien installé." % ", ".join(nouveaux))
        return fin(1, "BIOWANZE · horaire NON installé : nouvelle personne à confirmer",
                   "Le classeur du %s ajoute : %s.\n\nUne arrivée se fait toujours"
                   " confirmer avant d'être installée : dire à Claude qui c'est, sa"
                   " fonction, intérimaire ou non. Il l'ajoutera à"
                   " tools/arrivees-confirmees.txt et le prochain envoi s'installera."
                   "\n\nCe qui change :\n\n%s" % (quand, ", ".join(nouveaux), rapport))

    # 2. installer (reprend le passage à blanc)
    r = subprocess.run([sys.executable, os.path.join(OUTILS, "mettre-a-jour.py"), source,
                        "--installer"], cwd=RACINE, capture_output=True, text=True)
    sortie = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        etat("Installation refusée par le garde-fou du dépôt : rien installé.")
        return fin(1, "BIOWANZE · horaire NON installé (garde-fou du dépôt)",
                   "Le garde-fou du dépôt a refusé l'installation ; les fichiers d'avant"
                   " sont en place. À transmettre à Claude tel quel.\n\n" + sortie[-12000:])

    if pousser:
        git("add", "data/horaire-2026.json", "sw.js", "cal")
        message = ("Classeur du %s (mise à jour automatique)\n\n"
                   "Les huit portes de mettre-a-jour.py ouvertes, installé par"
                   " .github/workflows/horaire-auto.yml." % quand)
        c = git("commit", "-q", "-m", message)
        p = git("push", "-q", "origin", "HEAD:main") if c.returncode == 0 else c
        if p.returncode != 0:
            etat("Le commit ou l'envoi sur main a échoué.")
            print((p.stderr or "")[-2000:])
            return fin(1, "BIOWANZE · horaire NON publié",
                       "Installé, mais le commit ou l'envoi sur main a échoué. À"
                       " transmettre à Claude.\n\n" + (p.stderr or "")[-4000:])
    etat("Classeur du %s installé%s." % (quand, " et poussé sur main" if pousser else ""))
    return fin(0, "BIOWANZE · horaire du %s installé" % quand,
               "L'application est à jour (classeur du %s).\n\nCe qui change :\n\n%s"
               % (quand, rapport))


if __name__ == "__main__":
    sys.exit(main())
