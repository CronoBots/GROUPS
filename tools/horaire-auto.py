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
     la corbeille et envoie au client le rapport de ce qui a bougé. Ses
     rapports de plus de sept jours partent à la corbeille, le plus récent
     excepté (`purger_rapports()`).

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
import datetime
import email
import email.utils
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
CONFIRMEES = os.path.join(OUTILS, "arrivees-confirmees.txt")


def horaire_de(annee):
    """data/horaire-AAAA.json : un classeur par année depuis le 20/10/2026
    (le client envoie le récapitulatif 2027 en gardant celui de 2026)."""
    return os.path.join(RACINE, "data", "horaire-%d.json" % annee)


def horaires_installes():
    """{année: horaire installé}, pour chaque data/horaire-AAAA.json."""
    out = {}
    for nom in os.listdir(os.path.join(RACINE, "data")):
        m = re.match(r"horaire-(\d{4})\.json$", nom)
        if m:
            out[int(m.group(1))] = _lire(horaire_de(int(m.group(1))))
    return out


def annee_classeur(chemin):
    """La lecture de l'année de tools/mettre-a-jour.py, empruntée telle
    quelle : deux copies d'une même règle divergent."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("maj", os.path.join(OUTILS, "mettre-a-jour.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.annee_classeur(chemin)


def etat(texte):
    """Une ligne d'état, la seule chose qui va au journal public."""
    print(texte, flush=True)


def _option(nom):
    for a in sys.argv[1:]:
        if a.startswith(nom + "="):
            return a.split("=", 1)[1]
    return None


# L'EXPÉDITEUR DU CLASSEUR (audit de sécurité du 05/11/2026, SEC-2). L'adresse
# du robot est publique (index.html, EXPEDITEUR_CODE) et le sujet attendu est
# dans le dépôt : n'importe qui pouvait lui soumettre un classeur, que les huit
# portes jugent sur sa cohérence, jamais sur son origine. Un classeur ne vient
# donc que du domaine de l'entreprise, AUTHENTIFIÉ. Ce domaine publie une
# politique DMARC « p=REJECT » : un e-mail qui l'usurpe est refusé par Gmail
# lui-même. Tous les classeurs et recyclages reçus du 16/10 au 04/11/2026
# viennent de ce domaine (relu le 05/11/2026 ; journal 02).
DOMAINE_ADMIS = (os.environ.get("HORAIRE_DOMAINE") or "biowanze.be").strip().lower()


def expediteur(m):
    return email.utils.parseaddr(str(m.get("From", "")))[1].lower()


def expediteur_admis(m, domaine=None):
    """L'adresse « From » est du domaine, et le PREMIER « Authentication-
    Results » — celui que Gmail pose en tête à l'arrivée, au-dessus de tout ce
    que l'expéditeur aurait écrit lui-même — est de mx.google.com et dit
    « dmarc=pass » pour ce domaine (et non pour « domaine.autre.com »)."""
    domaine = (domaine or DOMAINE_ADMIS).lower()
    if not expediteur(m).endswith("@" + domaine):
        return False
    ar = m.get_all("Authentication-Results") or []
    if not ar:
        return False
    tete = re.sub(r"\s+", " ", str(ar[0])).strip().lower()
    if not tete.startswith("mx.google.com"):
        return False
    return re.search(r"(?:^|[;\s])dmarc=pass\b[^;]*\bheader\.from=" + re.escape(domaine) + r"(?![\w.-])",
                     tete) is not None


def ecarter(imap, user, mdp, sujet, ecartes):
    """Les e-mails d'un expéditeur non admis : à la corbeille sans être lus,
    et un rapport. Le journal des Actions, public, n'en dit que le nombre."""
    if not ecartes:
        return
    corbeille(imap, [u for u, _a in ecartes])
    etat("%d e-mail(s) « %s » écarté(s) : expéditeur non admis." % (len(ecartes), sujet))
    envoyer(user, mdp, "BIOWANZE · %d e-mail(s) « %s » écarté(s)" % (len(ecartes), sujet),
            "Ces e-mails ne venaient pas d'une adresse @%s authentifiée (DMARC) :"
            " mis à la corbeille sans être lus, rien installé.\n\n%s\n\nSi l'un"
            " d'eux est le vôtre, renvoyez le classeur depuis votre adresse"
            " professionnelle." % (DOMAINE_ADMIS, "\n".join("- " + (a or "(sans adresse)") for _u, a in ecartes)))


def _epreuve_expediteur():
    """--epreuve-expediteur : l'authentique passe, chaque usurpation échoue."""
    def msg(frm, *ar):
        t = "".join("Authentication-Results: %s\r\n" % x for x in ar)
        return email.message_from_string(t + "From: %s\r\nSubject: BIOWANZE horaire\r\n\r\nx" % frm)
    bon = ("mx.google.com; dkim=pass header.i=@biowanze.be header.s=selector2; spf=pass"
           " smtp.mailfrom=x@biowanze.be; dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=biowanze.be")
    cas = [
        (True, msg('"X" <x@biowanze.be>', bon, "mx.microsoft.com 1; dkim=none; dmarc=none header.from=biowanze.be")),
        (False, msg("x@exemple.com", bon)),                                  # un autre domaine
        (False, msg("x@biowanze.be.exemple.com", bon)),                      # un domaine qui le prolonge
        (False, msg("x@biowanze.be", bon.replace("dmarc=pass", "dmarc=fail"))),
        (False, msg("x@biowanze.be", "mx.google.com; dmarc=pass header.from=biowanze.be.exemple.com")),
        (False, msg("x@biowanze.be", "mx.google.com; spf=softfail; dmarc=fail header.from=biowanze.be", bon)),  # le vrai en tête dit « fail »
        (False, msg("x@biowanze.be", "serveur.exemple.com; dmarc=pass header.from=biowanze.be")),
        (False, msg("x@biowanze.be")),                                       # aucun résultat d'authentification
    ]
    fautes = [i for i, (attendu, m) in enumerate(cas) if expediteur_admis(m, "biowanze.be") != attendu]
    print("expéditeur : %d cas, %d faute(s)%s" % (len(cas), len(fautes), (" (cas %s)" % fautes) if fautes else ""))
    return 1 if fautes else 0


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
        return [], []
    # le plus récent d'un expéditeur admis ; les plus récents que lui, écartés
    ecartes = []
    for u in reversed(uids):
        typ, msg = imap.uid("fetch", u, "(RFC822)")
        m = email.message_from_bytes(msg[0][1])
        if expediteur_admis(m):
            break
        ecartes.append((u, expediteur(m)))
    else:
        return [], ecartes
    uids = [u for u in uids if u not in [e[0] for e in ecartes]]
    meilleure = None
    for part in m.walk():
        if part.get_content_maintype() == "multipart":
            continue
        contenu = part.get_payload(decode=True) or b""
        if contenu[:2] == b"PK" and (meilleure is None or len(contenu) > len(meilleure)):
            meilleure = contenu
    if meilleure is None:
        return uids, ecartes       # un e-mail sans classeur : à la corbeille quand même
    with open(dest, "wb") as f:
        f.write(meilleure)
    return uids, ecartes


def lire_gmail_par_annee(imap, sujet, dossier, moi=None):
    """Tous les e-mails du sujet, du plus récent au plus ancien : la pièce
    jointe de chacun est lue, et l'on garde la PLUS RÉCENTE DE CHAQUE ANNÉE.
    Avant le 20/10/2026, seul le dernier e-mail était lu : un classeur 2027
    arrivé après un 2026 dans le même quart d'heure l'aurait fait jeter.
    Rend (uids, {année: chemin}, nombre de pièces dont l'année ne se lit pas,
    [(uid, adresse)] des e-mails d'un expéditeur non admis, que uids ne
    compte pas)."""
    crit = '(SUBJECT "%s")' % sujet if not moi else '(SUBJECT "%s" NOT FROM "%s")' % (sujet, moi)
    typ, data = imap.uid("search", None, crit)
    uids = sorted((data[0] or b"").split(), key=int)
    par_an, illisibles, ecartes = {}, 0, []
    for u in reversed(uids):
        typ, msg = imap.uid("fetch", u, "(RFC822)")
        m = email.message_from_bytes(msg[0][1])
        if not expediteur_admis(m):
            ecartes.append((u, expediteur(m)))
            continue
        meilleure = None
        for part in m.walk():
            if part.get_content_maintype() == "multipart":
                continue
            contenu = part.get_payload(decode=True) or b""
            if contenu[:2] == b"PK" and (meilleure is None or len(contenu) > len(meilleure)):
                meilleure = contenu
        if meilleure is None:
            continue
        chemin = os.path.join(dossier, "Recapitulatif-%s.xlsm" % u.decode())
        with open(chemin, "wb") as f:
            f.write(meilleure)
        an = annee_classeur(chemin)
        if an is None:
            illisibles += 1
        elif an not in par_an:
            par_an[an] = chemin
    return [u for u in uids if u not in [e[0] for e in ecartes]], par_an, illisibles, ecartes


def corbeille(imap, uids):
    """X-GM-LABELS \\Trash vaut quel que soit la langue du compte Gmail."""
    for u in uids:
        imap.uid("store", u, "+X-GM-LABELS", "\\Trash")
    imap.expunge()


GARDE_RAPPORTS = 7      # jours

def purger_rapports(imap, moi, garde=GARDE_RAPPORTS):
    """Les rapports du robot devenus obsolètes vont à la corbeille (le
    client, le 18/10/2026 : « prévoir la suppression des mails une fois
    qu'ils sont obsolètes »). Les e-mails du classeur y partent déjà dès
    qu'ils sont lus ; restaient les rapports, envoyés à la même adresse et
    jamais retirés. Un rapport de plus de `garde` jours est obsolète : un
    classeur plus récent l'a remplacé, ou le dépôt et l'application disent
    désormais la même chose. Le plus récent est TOUJOURS gardé, même vieux :
    c'est le dernier état connu. Gmail vide sa corbeille après 30 jours.
    Rend le nombre de rapports retirés."""
    import datetime
    limite = (datetime.date.today() - datetime.timedelta(days=garde))
    avant = limite.strftime("%d-%b-%Y")      # format IMAP ; l'action tourne en locale C
    typ, data = imap.uid("search", None, '(FROM "%s" SUBJECT "BIOWANZE")' % moi)
    tous = sorted((data[0] or b"").split(), key=int)
    typ, data = imap.uid("search", None,
                         '(FROM "%s" SUBJECT "BIOWANZE" BEFORE %s)' % (moi, avant))
    vieux = set((data[0] or b"").split())
    retirer = [u for u in tous[:-1] if u in vieux]
    if retirer:
        corbeille(imap, retirer)
    return len(retirer)


def purger_envoyes(imap, moi, garde=GARDE_RAPPORTS):
    """Les e-mails que le robot ENVOIE à d'autres (codes de connexion, avis)
    restaient à jamais dans « Envoyés » : le robot ne nettoyait que sa boîte
    de réception (le client, le 06/11/2026, « optimise tout cela » : une
    trentaine du 21 au 29/10, des codes périmés). Ceux de plus de `garde`
    jours, adressés à un autre que lui, vont à la corbeille ; ses rapports et
    ses sauvegardes, adressés à lui-même, gardent leurs règles. Le dossier
    se trouve par son attribut \\Sent, quelle que soit la langue du compte.
    Rend le nombre d'e-mails retirés ; la boîte de réception est resélectionnée."""
    import datetime
    nom = None
    typ, boites = imap.list()
    for b in boites or []:
        ligne = b.decode("utf-8", "replace") if isinstance(b, bytes) else str(b)
        if "\\Sent" in ligne:
            m = re.search(r'"([^"]+)"\s*$', ligne) or re.search(r'(\S+)\s*$', ligne)
            nom = m.group(1) if m else None
            break
    if not nom:
        return 0
    n = 0
    try:
        imap.select('"%s"' % nom)
        avant = (datetime.date.today() - datetime.timedelta(days=garde)).strftime("%d-%b-%Y")
        typ, data = imap.uid("search", None, '(FROM "%s" NOT TO "%s" BEFORE %s)' % (moi, moi, avant))
        uids = (data[0] or b"").split()
        if uids:
            corbeille(imap, uids)
        n = len(uids)
    finally:
        imap.select("INBOX")
    return n


def _epreuve_purge_envoyes():
    """Une boîte simulée : deux vieux envoyés à un autre, un récent, un
    rapport à soi-même vieux ; seuls les deux premiers partent."""
    class Faux:
        def __init__(s): s.choisie, s.retires = None, []
        def list(s): return ("OK", [b'(\\HasNoChildren) "/" "INBOX"',
                                    b'(\\HasNoChildren \\Sent) "/" "[Gmail]/Messages envoy&AOk-s"'])
        def select(s, b): s.choisie = b
        def uid(s, cmd, *a):
            if cmd == "search":
                assert 'NOT TO "moi@x"' in a[1] and "BEFORE" in a[1]
                return ("OK", [b"11 12"])
            s.retires.append(a[0]); return ("OK", [])
        def expunge(s): pass
    f = Faux()
    assert purger_envoyes(f, "moi@x") == 2 and f.retires == [b"11", b"12"] and f.choisie == "INBOX"


def genre_sans_changement(sujet):
    """Le classeur dont parle un rapport « rien de changé » : « horaire
    2027 », « recyclages » ; None pour tout autre rapport. Les rapports
    d'avant le 20/10/2026 ne disaient pas l'année : c'était 2026."""
    if not re.search(r"rien de chang\u00e9\s*$", sujet or ""):
        return None
    m = re.search(r"horaire (\d{4})", sujet)
    if m:
        return "horaire " + m.group(1)
    if "recyclages" in sujet:
        return "recyclages"
    if "classeur du" in sujet:
        return "horaire 2026"
    return None


def purger_sans_changement(imap, moi):
    """« Rien de changé » ne vaut que jusqu'au rapport suivant du même
    classeur. Le client, le 20/10/2026, devant sa boîte : « et pas de
    nettoyage ici des anciens mails ? » — douze « rien de changé » en deux
    heures, gardés sept jours par purger_rapports(). On ne garde donc que le
    plus récent de chaque classeur (horaire de chaque année, recyclages) ;
    les installations et les portes fermées gardent leurs sept jours. Rend
    le nombre de rapports retirés."""
    import email.header
    typ, data = imap.uid("search", None, '(FROM "%s" SUBJECT "BIOWANZE")' % moi)
    uids = sorted((data[0] or b"").split(), key=int)
    vus, retirer = set(), []
    for u in reversed(uids):                 # du plus récent au plus ancien
        typ, msg = imap.uid("fetch", u, "(BODY.PEEK[HEADER.FIELDS (SUBJECT)])")
        try:
            brut = email.message_from_bytes(msg[0][1]).get("Subject", "")
            sujet = str(email.header.make_header(email.header.decode_header(brut)))
        except Exception:
            continue
        g = genre_sans_changement(" ".join(sujet.split()))
        if g is None:
            continue
        if g in vus:
            retirer.append(u)
        vus.add(g)
    if retirer:
        corbeille(imap, retirer)
    return len(retirer)


# LES RAPPORTS LISIBLES (le client, le 06/11/2026 : « optimise la
# présentation des mails […] les espaces et les mises à la ligne sont
# bizarres ; dis combien de changements ont été faits »). Le rapport était
# la sortie brute de comparer-horaire.py : cellules en JSON (["7h-15h",
# "RTT"]), flèches « -> », alignement en espaces que le téléphone casse.
# comparer-horaire.py reste tel quel (d'autres outils le lisent) ; le
# rapport se met en forme à l'envoi : une version texte propre et une
# version HTML (tableaux), et le nombre de changements en tête et dans le
# sujet.
import html as _html

_SEC = {"prevision": "prévus", "restant": "restants", "pris": "pris", "flex": "flex",
        "droit": "droit", "planifie": "planifiés", "consomme": "consommés", "conges": "congés"}


def _cellule(brut):
    """'["AM", "R-CM", "remplace YPE"]' → ('AM · R-CM', 'remplace YPE')."""
    try:
        v = json.loads(brut)
    except Exception:
        return (brut.strip(), "")
    if v is None:
        return ("vide", "")
    if not isinstance(v, list):
        return (str(v), "")
    v = [str(x) for x in v]
    return (" · ".join(x for x in v[:2] if x.strip()) or "vide", " ".join(v[2:]).strip())


def _quand_court(t):
    m = re.match(r"(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d)", t or "")
    return "%s/%s à %s h %s" % (m.group(3), m.group(2), m.group(4), m.group(5)) if m else t


def _compteur(ecart):
    """'prevision.RTT 40 -> 56' → 'RTT prévus : 40 → 56'."""
    m = re.match(r"(\w+)\.(\S+) (.*) -> (.*)$", ecart.strip())
    if not m:
        return ecart.replace(" -> ", " → ")
    return "%s %s : %s → %s" % (m.group(2), _SEC.get(m.group(1), m.group(1)), m.group(3), m.group(4))


def lire_rapport(corps):
    """Découpe le corps d'un rapport en blocs : ('p', texte), ('titre', t),
    ('jours', [(qui, n, [(date, avant, apres), …], reste)]), ('liste', [lignes])."""
    blocs, L, i = [], corps.split("\n"), 0
    sec = None
    while i < len(L):
        l = L[i].rstrip()
        if not l.strip():
            i += 1; sec = None if sec != "jours" else sec; continue
        m = re.match(r"^Journées modifiées : (\d+), chez (\d+) personne", l)
        if m:
            sec = "jours"; blocs.append(("titre", "Journées modifiées"))
            blocs.append(("jours", [])); i += 1; continue
        if sec == "jours":
            mp = re.match(r"^  (\S+) — (\d+) journée", l)
            md = re.match(r"^\s{4,}(\d\d/\d\d)\s+(.*)$", l)
            me = re.match(r"^\s+… et (\d+) autre", l)
            if mp:
                blocs[-1][1].append([mp.group(1), int(mp.group(2)), [], 0]); i += 1; continue
            if md and blocs[-1][1]:
                apres = L[i + 1].strip() if i + 1 < len(L) else "null"
                blocs[-1][1][-1][2].append((md.group(1), _cellule(md.group(2)), _cellule(apres)))
                i += 2; continue
            if me and blocs[-1][1]:
                blocs[-1][1][-1][3] = int(me.group(1)); i += 1; continue
            sec = None
        mt = re.match(r"^(En-tête|Personnes|Changements de groupe|Compteurs|Polyvalence|Autres champs|Commentaires à relire)\b[^:]*:\s*(.*)$", l)
        if mt and not l.startswith(" "):
            sec = mt.group(1); blocs.append(("titre", {"En-tête": "Classeur", "Commentaires à relire": "Commentaires à relire (date d'un autre jour)"}.get(sec, sec)))
            blocs.append(("liste", [])); i += 1; continue
        if sec and l.startswith(" ") and blocs and blocs[-1][0] == "liste":
            t = re.sub(r"\s{2,}", " ", l.strip())
            if t.startswith("[") or '{"' in t:
                i += 1; continue   # le détail brut d'un champ : le nom du champ suffit
            mm = re.match(r"^maj (\S+) -> (\S+)$", t)
            if mm:
                t = "reçu le %s (avant : %s)" % (_quand_court(mm.group(2)), _quand_court(mm.group(1)))
            elif sec == "Commentaires à relire":
                mm = re.match(r"^(\S+) (\d\d/\d\d) (\[.*\])\s*→\s*(.*)$", t)
                if mm:
                    c, com = _cellule(mm.group(3))
                    t = "%s, %s : %s%s (date citée : %s)" % (mm.group(1), mm.group(2), c,
                                                             (" « %s »" % com) if com else "", mm.group(4))
            elif sec == "Compteurs":
                q, _, r = t.partition(" ")
                t = q + " : " + ", ".join(_compteur(e) for e in r.split(" · "))
            elif sec == "Personnes":
                mm = re.match(r"^([+-])\s+(\S+)\s+(.*?)\s+(\d+) journées$", t)
                if mm:
                    t = "%s %s (%s)" % ("arrivée :" if mm.group(1) == "+" else "départ :", mm.group(2), mm.group(3))
            t = re.sub(r"\s{2,}", " ", t).replace(" -> ", " → ")
            blocs[-1][1].append(t); i += 1; continue
        sec = None
        # une ligne suivie de lignes en retrait (« manques commentés — … ») :
        # un titre et sa liste, les cellules JSON rendues lisibles
        if i + 1 < len(L) and L[i + 1].startswith("  ") and L[i + 1].strip():
            titre, _, reste_t = l.strip().partition(" — ")
            blocs.append(("titre", titre[:1].upper() + titre[1:]))
            if reste_t:
                blocs.append(("p", reste_t[:1].upper() + reste_t[1:]))
            lignes = []
            i += 1
            while i < len(L) and L[i].startswith("  ") and L[i].strip():
                t = re.sub(r"\[[^\[\]]*\]", lambda m: "%s%s" % (
                    _cellule(m.group(0))[0], (" « %s »" % _cellule(m.group(0))[1]) if _cellule(m.group(0))[1] else ""),
                    L[i].strip())
                t = re.sub(r"\s{2,}", " ", t).replace(" : ", " : ", 1)
                lignes.append(("   " if L[i].startswith("    ") else "") + t)
                i += 1
            blocs.append(("liste", lignes))
            continue
        # un paragraphe : les lignes jusqu'à la prochaine ligne vide
        par = [l.strip()]
        i += 1
        while i < len(L) and L[i].strip() and not re.match(r"^(Journées modifiées|En-tête|Personnes|Compteurs|Polyvalence|Autres champs|Changements de groupe)\b", L[i]):
            par.append(L[i].strip()); i += 1
        blocs.append(("p", " ".join(par).replace(" -> ", " → ")))
    return blocs


def compter(corps):
    """(journées modifiées, personnes, arrivées, départs, compteurs) d'un rapport."""
    m = re.search(r"Journées modifiées : (\d+), chez (\d+)", corps)
    mc = re.search(r"(?m)^Compteurs : (\d+) personne", corps)
    arr = len(re.findall(r"(?m)^  \+ \S", corps)); dep = len(re.findall(r"(?m)^  - \S", corps))
    return (int(m.group(1)) if m else 0, int(m.group(2)) if m else 0, arr, dep, int(mc.group(1)) if mc else 0)


def resume(corps):
    """« 4 journées modifiées chez 3 personnes · 1 arrivée » ; '' si rien."""
    j, p, a, d, c = compter(corps)
    morceaux = []
    if j:
        morceaux.append("%d journée%s modifiée%s chez %d personne%s" % (j, "s" * (j > 1), "s" * (j > 1), p, "s" * (p > 1)))
    if a:
        morceaux.append("%d arrivée%s" % (a, "s" * (a > 1)))
    if d:
        morceaux.append("%d départ%s" % (d, "s" * (d > 1)))
    if c and morceaux:
        morceaux.append("compteurs de %d personne%s" % (c, "s" * (c > 1)))
    return " · ".join(morceaux)


def mettre_en_forme(corps):
    """(texte, html) d'un rapport."""
    blocs = lire_rapport(corps)
    t, h = [], []
    def e(x):   # « 12 h 51 » ne se coupe pas au téléphone
        return re.sub(r"(\d) h (\d)", "\\1&nbsp;h&nbsp;\\2", _html.escape(x))
    h.append('<div style="font-family:system-ui,-apple-system,sans-serif;'
             'font-size:15px;line-height:1.45;color:#1d2433;max-width:640px">')
    r = resume(corps)
    if r:
        t += [r, ""]
        h.append('<p style="margin:0 0 14px;padding:10px 14px;background:#eef3fb;border-radius:10px;'
                 'font-weight:600">%s</p>' % e(r))
    for k, v in blocs:
        if k == "p":
            t += [v, ""]
            fort = v.startswith("À RELIRE") or "NON " in v[:40]
            h.append('<p style="margin:0 0 12px%s">%s</p>' % (";color:#a3361f;font-weight:600" if fort else "", e(v)))
        elif k == "titre":
            t += [v.upper()]
            h.append('<h3 style="margin:18px 0 6px;font-size:13px;letter-spacing:.06em;'
                     'text-transform:uppercase;color:#5b6475">%s</h3>' % e(v))
        elif k == "liste":
            t += [("     " + x.strip()) if x.startswith("   ") else "• " + x for x in v] + [""]
            h.append('<ul style="margin:0 0 8px;padding-left:20px">%s</ul>'
                     % "".join(('<li style="margin:0 0 2px;list-style:none;color:#5b6475">%s</li>' if x.startswith("   ")
                                else '<li style="margin:6px 0 2px">%s</li>') % e(x.strip()) for x in v))
        elif k == "jours":
            for qui, n, jours, reste in v:
                t.append("%s — %d journée%s" % (qui, n, "s" * (n > 1)))
                h.append('<p style="margin:10px 0 4px;font-weight:700">%s <span style="font-weight:400;'
                         'color:#5b6475">· %d journée%s</span></p>' % (e(qui), n, "s" * (n > 1)))
                h.append('<table cellpadding="0" cellspacing="0" style="border-collapse:collapse;width:100%">')
                for date, (av, avc), (ap, apc) in jours:
                    if av == ap:
                        ligne = "%s, commentaire %s" % (ap, ("« %s »" % apc) if apc else "retiré")
                    else:
                        ligne = "%s → %s%s" % (av, ap, (" (« %s »)" % apc) if apc else "")
                    t.append("   %s : %s" % (date, ligne))
                    if av == ap:
                        cellule = '<b>%s</b> <span style="color:#5b6475">· commentaire %s</span>' % (
                            e(ap), "modifié" if apc else "retiré")
                    else:
                        cellule = ('<span style="color:#8a92a3;text-decoration:line-through">%s</span>'
                                   ' &rarr; <b>%s</b>' % (e(av), e(ap)))
                    if apc:
                        cellule += '<br><i style="color:#5b6475">« %s »</i>' % e(apc)
                    h.append('<tr><td style="padding:5px 10px 5px 0;white-space:nowrap;vertical-align:top;'
                             'color:#5b6475;width:48px">%s</td><td style="padding:5px 0;vertical-align:top;'
                             'border-bottom:1px solid #eef0f4">%s</td></tr>' % (e(date), cellule))
                if reste:
                    t.append("   … et %d autre%s" % (reste, "s" * (reste > 1)))
                    h.append('<tr><td></td><td style="padding:4px 0;color:#5b6475">… et %d autre%s</td></tr>'
                             % (reste, "s" * (reste > 1)))
                h.append("</table>")
            t.append("")
    h.append("</div>")
    return ("\n".join(t).strip() + "\n", "".join(h))


def _epreuve_mise_en_forme():
    corps = ("L'application est à jour (classeur du 06/11/2026 à 07 h 42, horaire 2026).\n\nCe qui change :\n\n"
             "En-tête :\n  maj 2026-11-05T15:48 -> 2026-11-06T07:42\n\n"
             "Journées modifiées : 4, chez 3 personne(s)\n  AAA — 2 journée(s)\n"
             "      09/11  [\"7h-15h\"]\n             [\"7h-15h\", \"RTT\"]\n"
             "      10/11  [\"7h-15h\"]\n             [\"7h-15h\", \"RTT\"]\n"
             "  BBB — 1 journée(s)\n      11/11  [\"AM\"]\n             [\"AM\", \"R-CM\", \"remplace CCC\"]\n\n"
             "Compteurs : 1 personne(s)\n  AAA    prevision.RTT 40 -> 56 · restant.RTT 18 -> 2\n")
    t, h = mettre_en_forme(corps)
    assert resume(corps).startswith("4 journées modifiées chez 3 personnes · "), resume(corps)
    assert "09/11 : 7h-15h → 7h-15h · RTT" in t, t
    assert "11/11 : AM → AM · R-CM (« remplace CCC »)" in t, t
    assert resume(corps).endswith("compteurs de 1 personne"), resume(corps)
    assert "RTT prévus : 40 → 56" in t and "reçu le 06/11 à 07 h 42" in t, t
    assert "->" not in t and '["' not in t and "<table" in h, t
    return t


def envoyer(user, mdp, sujet, corps, forme=False):
    if not (user and mdp):
        print("\n" + sujet + "\n" + corps)       # essai local : à l'écran
        return
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = user, user, sujet
    if forme:
        texte, page = mettre_en_forme(corps)
        msg.set_content(texte)
        msg.add_alternative(page, subtype="html")
    else:
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


def relire_commentaires(horaire):
    """LES COMMENTAIRES DU CLASSEUR NEUF RELUS À CHAQUE INSTALLATION (le
    client, le 03/11/2026 : « ce n'est pas la première fois que tu ne prends
    pas en compte les commentaires […] je dois avoir quelque chose de sérieux
    pour présenter au RH »). Le classeur du 03/11 a apporté des chaînes de
    remplacement (le 13/11, ADK → FLN absent → ALZ) que personne n'a relues :
    l'installation ne lançait que les neuf règles du calendrier. Ici,
    `verifier-calendrier.js --manques-commentes` : chaque place vide, d'aujourd'hui
    au 31/12, dont un commentaire du jour nomme le titulaire absent, et que
    personne n'a encore lue (tools/manques-admis.txt). Rend (nombre, texte) ;
    le texte ne porte que des trigrammes, comme l'horaire publié."""
    try:
        r = subprocess.run(["node", os.path.join(OUTILS, "verifier-calendrier.js"), horaire,
                            "--manques-commentes"], cwd=RACINE, capture_output=True, text=True,
                           timeout=900)
    except Exception as e:
        return (-1, "Le contrôle des commentaires n'a pas pu tourner : %s" % e)
    sortie = (r.stdout or "").strip()
    if r.returncode == 0:
        return (0, sortie.splitlines()[0] if sortie else "")
    m = re.search(r", (\d+) dont un commentaire", sortie)
    if r.returncode != 1 or not m:
        return (-1, "Le contrôle des commentaires a échoué :\n" + (sortie + "\n" + (r.stderr or ""))[-4000:])
    return (int(m.group(1)), sortie[-8000:])


def traiter_horaire(source):
    """Rend (code, sujet, corps, installé?, quand, année)."""
    r = subprocess.run([sys.executable, os.path.join(OUTILS, "mettre-a-jour.py"), source],
                       cwd=RACINE, capture_output=True, text=True)
    sortie = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        porte = re.search(r"PORTE FERMÉE à l'étape (\d+)", sortie)
        n = porte.group(1) if porte else "?"
        etat("Horaire : porte %s fermée, rien installé." % n)
        return (1, "BIOWANZE · horaire NON installé (porte %s fermée)" % n,
                "Une porte s'est fermée : rien n'a été installé. À transmettre à"
                " Claude tel quel.\n\n" + sortie[-12000:], False, "", None)
    memo = json.load(open(os.path.join(tempfile.gettempdir(),
                                       "biowanze-dernier-blanc.json"), encoding="utf-8"))
    annee = int(memo["cle"]["annee"])
    neuf = os.path.join(memo["tmp"], "horaire-%d.json" % annee)
    rapport = open(os.path.join(memo["tmp"], "comparaison.txt"), encoding="utf-8").read()
    # l'année dite partout : deux classeurs vivent côte à côte (20/10/2026)
    quand = "%s, horaire %d" % (_quand(json.load(open(neuf, encoding="utf-8")).get("maj", "?")), annee)
    installe = horaire_de(annee)
    if os.path.exists(installe) and open(neuf, "rb").read() == open(installe, "rb").read():
        etat("Horaire du %s : identique à celui en place, rien installé." % quand)
        return (0, "BIOWANZE · classeur du %s, rien de changé" % quand,
                "Les huit portes sont ouvertes, et l'horaire est identique à celui"
                " en place : rien n'a été installé.", False, quand, annee)
    nouveaux = [t for t in arrivees(rapport) if t not in confirmees()]
    # UN NOUVEL OPÉRATEUR EST TOUJOURS UN INTÉRIMAIRE (le client, le
    # 19/10/2026 : « quand un nouvel opérateur apparaît c'est toujours un
    # intérimaire, il faut que la mise à jour le prenne en compte »). Une
    # arrivée hors des contremaîtres est donc confirmée d'office, comme
    # intérimaire, et l'horaire s'installe ; l'application l'affiche déjà
    # « Intérimaire » (absent de « Polyvalence », pas cadre : statutAffiche).
    # Une arrivée chez les contremaîtres sort de cette règle : elle attend
    # toujours le client.
    par_id = dict((p.get("id"), p) for p in json.load(open(neuf, encoding="utf-8")).get("people", []))
    cadres = [t for t in nouveaux if re.search(r"contrema", str((par_id.get(t) or {}).get("cat", "")), re.I)]
    interims = [t for t in nouveaux if t not in cadres]
    if cadres:
        etat("Horaire : arrivée(s) de contremaître à confirmer (%s), rien installé." % ", ".join(cadres))
        return (1, "BIOWANZE · horaire NON installé : nouveau contremaître à confirmer",
                "Le classeur du %s ajoute chez les contremaîtres : %s.\n\nUn nouvel"
                " opérateur est confirmé d'office comme intérimaire, pas un"
                " contremaître : dire à Claude qui c'est et sa fonction. Il"
                " l'ajoutera à tools/arrivees-confirmees.txt et le prochain envoi"
                " s'installera.\n\nCe qui change :\n\n%s" % (quand, ", ".join(cadres), rapport),
                False, quand, annee)
    annonce = ""
    if interims:
        jour = datetime.date.today().strftime("%d/%m/%Y")
        with open(CONFIRMEES, "a", encoding="utf-8") as f:
            for t in interims:
                f.write("%s  # %s : nouvel opérateur, intérimaire d'office (%s) — règle du client du 19/10/2026\n"
                        % (t, jour, (par_id.get(t) or {}).get("cat", "catégorie inconnue")))
        annonce = ("Nouvel intérimaire : " if len(interims) == 1 else "Nouveaux intérimaires : ") \
            + ", ".join("%s (%s)" % (t, (par_id.get(t) or {}).get("cat", "?")) for t in interims) + ".\n\n"
        etat("Horaire : %s confirmé(s) d'office comme intérimaire(s)." % ", ".join(interims))
    r = subprocess.run([sys.executable, os.path.join(OUTILS, "mettre-a-jour.py"), source,
                        "--installer"], cwd=RACINE, capture_output=True, text=True)
    sortie = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        etat("Horaire : installation refusée par le garde-fou du dépôt.")
        return (1, "BIOWANZE · horaire NON installé (garde-fou du dépôt)",
                "Le garde-fou du dépôt a refusé l'installation ; les fichiers d'avant"
                " sont en place. À transmettre à Claude tel quel.\n\n" + sortie[-12000:],
                False, quand, annee)
    etat("Horaire du %s installé." % quand)
    n, texte = relire_commentaires(installe)
    alerte, suffixe = "", ""
    if n:
        etat("Horaire : %s." % ("%d place(s) commentée(s) à relire" % n if n > 0
                                 else "contrôle des commentaires en échec"))
        suffixe = (" — %d commentaire(s) à relire" % n) if n > 0 else " — contrôle des commentaires en échec"
        alerte = ("À RELIRE AVANT DE SE FIER AU PLANNING : des places vides que les"
                  " commentaires du jour expliquent peut-être. À transmettre à Claude"
                  " tel quel ; une fois lues, elles vont dans tools/manques-admis.txt,"
                  " ou la lecture se corrige.\n\n%s\n\n" % texte)
    return (0, "BIOWANZE · horaire du %s installé%s" % (quand, suffixe),
            "L'application est à jour (classeur du %s).\n\n%s%sCe qui change :\n\n%s"
            % (quand, alerte, annonce, rapport), True, quand, annee)


def traiter_recyclage(source):
    """Rend (code, sujet, corps, installé?, quand, None)."""
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
                " Claude tel quel.\n\n" + sortie[-12000:], False, "", None)
    m = re.search(r"══ CE QUI CHANGE.*?══\n\n(.*?)(?:\n\n(?:Réserve locale|Le recyclage installé|Installé|Les onze)|\Z)",
                  sortie, re.S)
    rapport = m.group(1).strip() if m else "(rapport introuvable)"
    quand = _quand(json.load(open(RECYC, encoding="utf-8")).get("maj", "?"))
    if open(RECYC, "rb").read() == json_avant:
        open(sw, "wb").write(sw_avant)
        etat("Recyclages du %s : identiques à ceux en place, rien installé." % quand)
        return (0, "BIOWANZE · recyclages enregistrés le %s, rien de changé" % quand,
                "Les onze portes sont ouvertes, et les recyclages sont identiques à"
                " ceux en place : rien n'a été installé.", False, quand, None)
    etat("Recyclages du %s installés." % quand)
    return (0, "BIOWANZE · recyclages enregistrés le %s installés" % quand,
            "L'application est à jour (classeur RH enregistré le %s).\n\nCe qui change :"
            "\n\n%s" % (quand, rapport), True, quand, None)


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
            apres = _lire(horaire_de(x[7]))
            ch = changements_horaire(avant_h.get(x[7]) or {}, apres, x[7], _aujourdhui())
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
            connus = sorted(set(p.get("id") for h in horaires_installes().values()
                                for p in (h.get("people") or [])))
            out.append({"tag": "recyclage", "url": "./?vue=equipe", "par_tri": par, "connus": connus,
                        "defaut": {"title": "Recyclages mis à jour",
                                   "body": "Classeur RH du %s · le recyclage est dans l'onglet Équipes." % quand}})
    return out


def synchro_base():
    """LA BASE BIOWANZE (étape 2, 20/10/2026) : l'horaire installé y est
    recopié quand sa version diffère — à CHAQUE passage, e-mail ou non : la
    première version ne la recopiait qu'après une installation, et le
    passage sans e-mail s'arrêtait avant. Jamais d'échec pour elle."""
    try:
        r = subprocess.run([sys.executable, os.path.join(OUTILS, "base-synchro.py")],
                           cwd=RACINE, capture_output=True, text=True, timeout=300)
        etat((r.stdout or "").strip() or "Base : non recopiée.")
    except subprocess.TimeoutExpired:
        etat("Base : recopie abandonnée après 5 minutes.")
    # la sauvegarde du jour, au premier passage qui la trouve absente
    # cinq minutes au plus : le 22/10/2026 au soir, une sauvegarde pendue a
    # tenu la relève 20 minutes, et la suivante (le classeur du client)
    # attendait derrière elle
    try:
        r = subprocess.run([sys.executable, os.path.join(OUTILS, "base-sauvegarde.py")],
                           cwd=RACINE, capture_output=True, text=True, timeout=300)
        etat((r.stdout or "").strip() or "Sauvegarde : non faite.")
    except subprocess.TimeoutExpired:
        etat("Sauvegarde : abandonnée après 5 minutes.")


def identites_base(source, annee):
    """LES NOMS ET MATRICULES (étape 2, 21/10/2026) : lus dans le classeur
    par le convertisseur, écrits dans un fichier du dossier temporaire —
    jamais dans le dépôt, qui est public — puis envoyés à la base, qui seule
    les garde ; base-synchro.py efface le fichier. Le journal de l'action
    n'en dit que le nombre. Jamais d'échec pour eux."""
    if not os.environ.get("PUSH_CLE"):
        return
    fd, chemin = tempfile.mkstemp(prefix="biowanze-identites-", suffix=".json")
    os.close(fd)
    sortie = os.path.join(tempfile.gettempdir(), "biowanze-identites-horaire.json")
    try:
        r = subprocess.run([sys.executable, os.path.join(OUTILS, "convertir-horaire.py"),
                            source, sortie, str(annee or 2026), "--identites=" + chemin],
                           cwd=RACINE, capture_output=True, text=True)
        if r.returncode != 0:
            etat("Base : identités non lues (convertisseur, code %d)." % r.returncode)
            return
        r = subprocess.run([sys.executable, os.path.join(OUTILS, "base-synchro.py"),
                            "--identites=" + chemin], cwd=RACINE, capture_output=True, text=True)
        etat((r.stdout or "").strip() or "Base : identités non envoyées.")
    finally:
        for f in (chemin, sortie):
            try:
                os.remove(f)
            except OSError:
                pass


def main():
    if "--epreuve-expediteur" in sys.argv:
        return _epreuve_expediteur()
    if "--epreuve-courrier" in sys.argv:
        # la purge des envoyés et la mise en forme des rapports (06/11/2026)
        _epreuve_purge_envoyes()
        print(_epreuve_mise_en_forme())
        print("épreuves du courrier : ok")
        return 0
    user, mdp = os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD")
    avant_h, avant_r = horaires_installes(), _lire(RECYC)
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
        n = purger_rapports(imap, user)
        if n:
            etat("%d rapport(s) de plus de %d jours mis à la corbeille." % (n, GARDE_RAPPORTS))
        try:
            n = purger_envoyes(imap, user)
            if n:
                etat("%d e-mail(s) envoyé(s) de plus de %d jours mis à la corbeille." % (n, GARDE_RAPPORTS))
        except Exception as e:               # le ménage ne fait jamais échouer un passage
            etat("Envoyés : ménage non fait (%s)." % type(e).__name__)
        n = purger_sans_changement(imap, user)
        if n:
            etat("%d rapport(s) « rien de changé » remplacé(s) mis à la corbeille." % n)
        # L'horaire : la plus récente pièce jointe de CHAQUE année (2026 et
        # 2027 se copient du serveur côte à côte depuis le 20/10/2026).
        uids, par_an, illisibles, ecartes = lire_gmail_par_annee(imap, SUJET, tmp, user)
        ecarter(imap, user, mdp, SUJET, ecartes)
        if uids:
            etat("%d e-mail(s) « %s » ; le plus récent de chaque année est lu (%s)."
                 % (len(uids), SUJET, ", ".join(str(a) for a in sorted(par_an)) or "aucune"))
            if illisibles:
                envoyer(user, mdp, "BIOWANZE · horaire : %d classeur(s) sans année lisible" % illisibles,
                        "L'année de %d pièce(s) jointe(s) « %s » ne se lit pas dans l'onglet"
                        " Config (« Contremaîtres-AAAA ») : ignorée(s). À transmettre à"
                        " Claude." % (illisibles, SUJET))
            if not par_an:
                corbeille(imap, uids)
                if not illisibles:
                    envoyer(user, mdp, "BIOWANZE · horaire NON installé",
                            "L'e-mail « %s » ne portait pas de classeur en pièce jointe."
                            " Vérifier le flux Power Automate (pièce jointe : File content)." % SUJET)
                etat("Horaire : aucun classeur lisible en pièce jointe, rien installé.")
            for i, an in enumerate(sorted(par_an)):
                lots.append(("horaire", par_an[an], uids if i == 0 else []))
        for genre, sujet, nom in (("recyclage", SUJET_RECYC, "Suivi_recyclages.xlsx"),):
            source = os.path.join(tmp, nom)
            uids, ecartes = lire_gmail(imap, sujet, source, user)
            ecarter(imap, user, mdp, sujet, ecartes)
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
            etat("Aucun e-mail « %s » ni « %s » : rien à installer." % (SUJET, SUJET_RECYC))
            synchro_base()
            return 0

    resultats = []     # (genre, uids, code, sujet, corps, installé, quand, année)
    for genre, source, uids in lots:
        f = traiter_horaire if genre == "horaire" else traiter_recyclage
        resultats.append((genre, uids) + f(source))
        if genre == "horaire" and resultats[-1][2] == 0:
            identites_base(source, resultats[-1][7])

    installes = [x for x in resultats if x[5]]
    publie = True
    if installes and pousser:
        fichiers = ["sw.js"]
        titres = []
        for x in installes:
            if x[0] == "horaire":
                fichiers += ["data/horaire-%d.json" % x[7], "cal", "tools/arrivees-confirmees.txt",
                             "index.html"]      # HORAIRE_ANNEES, si l'année est nouvelle
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

    synchro_base()

    code = 0
    for genre, uids, c, sujet, corps, inst, quand, _an in resultats:
        if inst and pousser and not publie:
            c, sujet = 1, "BIOWANZE · %s NON publié" % genre
            corps = ("Installé, mais le commit ou l'envoi sur main a échoué. À"
                     " transmettre à Claude.\n\n" + corps)
        if imap is not None and uids:
            corbeille(imap, uids)
        # le nombre de changements dans le sujet (06/11/2026)
        r = resume(corps)
        if r and inst:
            sujet = sujet.replace(" installé", " installé · " + r, 1)
        # la mise en forme ne vaut que pour le rapport de l'horaire (ses
        # sections sont celles de comparer-horaire.py) ; les autres partent tels quels
        envoyer(user, mdp, sujet, corps, forme="\nCe qui change :\n" in corps and "Journées modifiées" in corps)
        code = max(code, c)
    return code


if __name__ == "__main__":
    sys.exit(main())
