#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La sauvegarde quotidienne de la base BIOWANZE (21/10/2026).

La formule gratuite de Supabase n'en fait aucune ; avant que la RH saisisse
dans l'application, il en faut une. Une fois par jour, au premier passage
du robot :

  1. public.biowanze_sauvegarde (base/08-sauvegarde.sql) rend tout le schéma
     biowanze en JSON, avec la clé du robot ;
  2. le JSON est compressé (gzip) puis CHIFFRÉ (openssl, AES-256, PBKDF2)
     avec cette même clé, PUSH_CLE ;
  3. il part en pièce jointe à la boîte Gmail du robot, « Sauvegarde BWZ-base
     AAAA-MM-JJ » — jamais au dépôt, qui est public. Le sujet ne contient pas
     « BIOWANZE » : purger_rapports() de horaire-auto.py les jetterait au
     bout de sept jours.

On garde les GARDE dernières ; les plus anciennes vont à la corbeille.
Le journal de l'action (public) ne dit que des nombres. Jamais d'échec : une
sauvegarde manquée se refait au passage suivant.

Restaurer (sur un poste qui a la clé) :

    openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass env:PUSH_CLE \\
        -in bwz-base-AAAA-MM-JJ.json.gz.enc | gunzip > sauvegarde.json

    PUSH_CLE=… GMAIL_USER=… GMAIL_APP_PASSWORD=… python3 tools/base-sauvegarde.py
"""
import datetime
import email.message
import gzip
import imaplib
import json
import os
import smtplib
import subprocess
import sys
import urllib.request

SUPABASE = "https://pnizdddritizjbsksoir.supabase.co"
CLE_PUBLIQUE = "sb_publishable_FzetjMxWmdjSaTHWl1uZSg_HhMyErQI"
SUJET = "Sauvegarde BWZ-base"
GARDE = 30


def lire_base(cle):
    req = urllib.request.Request(
        SUPABASE + "/rest/v1/rpc/biowanze_sauvegarde",
        data=json.dumps({"p_cle": cle}).encode("utf-8"),
        headers={"apikey": CLE_PUBLIQUE, "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def chiffrer(donnees, cle):
    r = subprocess.run(["openssl", "enc", "-aes-256-cbc", "-salt", "-pbkdf2",
                        "-iter", "200000", "-pass", "env:BWZ_CLE"],
                       input=gzip.compress(donnees), capture_output=True,
                       env=dict(os.environ, BWZ_CLE=cle))
    if r.returncode != 0:
        raise RuntimeError("openssl : " + r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout


def dechiffrer(chiffre, cle):
    r = subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2",
                        "-iter", "200000", "-pass", "env:BWZ_CLE"],
                       input=chiffre, capture_output=True, env=dict(os.environ, BWZ_CLE=cle))
    if r.returncode != 0:
        raise RuntimeError("déchiffrement impossible")
    return gzip.decompress(r.stdout)


def main():
    cle, user, mdp = (os.environ.get(k) for k in ("PUSH_CLE", "GMAIL_USER", "GMAIL_APP_PASSWORD"))
    if not (cle and user and mdp):
        print("Sauvegarde : secrets absents, rien fait.")
        return 0
    jour = datetime.date.today().isoformat()
    sujet = "%s %s" % (SUJET, jour)
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user, mdp)
    imap.select("INBOX")
    typ, data = imap.uid("search", None, '(FROM "%s" SUBJECT "%s")' % (user, sujet))
    if (data[0] or b"").split() and "--forcer" not in sys.argv:
        print("Sauvegarde : déjà faite aujourd'hui.")
        imap.logout()
        return 0

    brut = lire_base(cle)
    tables = json.loads(brut)
    chiffre = chiffrer(brut, cle)
    # on ne part pas sans avoir relu : une sauvegarde qu'on ne sait pas
    # rouvrir ne sauve rien
    if dechiffrer(chiffre, cle) != brut:
        raise RuntimeError("relecture de la sauvegarde différente")
    lignes = sum(len(v) for v in tables.values() if isinstance(v, list))

    msg = email.message.EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = user, user, sujet
    msg.set_content(
        "Sauvegarde chiffrée de la base BIOWANZE du %s : %d lignes, %d tables.\n\n"
        "Elle s'ouvre avec la clé du robot (PUSH_CLE) ; la commande est en tête "
        "de tools/base-sauvegarde.py. Les %d plus récentes sont gardées."
        % (jour, lignes, sum(1 for v in tables.values() if isinstance(v, list)), GARDE))
    msg.add_attachment(chiffre, maintype="application", subtype="octet-stream",
                       filename="bwz-base-%s.json.gz.enc" % jour)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(user, mdp)
        s.send_message(msg)

    # les plus anciennes à la corbeille, les GARDE dernières restent
    typ, data = imap.uid("search", None, '(FROM "%s" SUBJECT "%s")' % (user, SUJET))
    uids = sorted((data[0] or b"").split(), key=int)
    vieux = uids[:-GARDE] if len(uids) > GARDE else []
    for u in vieux:
        imap.uid("store", u, "+X-GM-LABELS", "\\Trash")
    if vieux:
        imap.expunge()
    imap.logout()
    print("Sauvegarde : %d lignes, %d Ko chiffrés, envoyée%s."
          % (lignes, len(chiffre) // 1024,
             ", %d ancienne(s) à la corbeille" % len(vieux) if vieux else ""))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:      # le robot ne tombe jamais pour la sauvegarde
        print("Sauvegarde : non faite (%s : %s)." % (type(e).__name__, str(e)[:160]))
        sys.exit(0)
