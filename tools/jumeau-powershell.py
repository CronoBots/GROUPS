#!/usr/bin/env python3
"""Confronte les deux anonymiseurs sur un vrai classeur.

    python3 tools/jumeau-powershell.py /chemin/Recapitulatif.xlsm [...]

POURQUOI. tools/anonymiser-classeur.ps1 est le portage, pour les postes sans
Python, de tools/anonymiser-classeur.py. Deux copies d'une même règle
divergent, et c'est la seconde qui reste en arrière : le 28/10/2026, le
jumeau avait un mois de retard — ni la ligne des noms, ni les corrections du
client, ni les signatures, ni les identifiants de connexion — et s'arrêtait
de lui-même sur un nom à particule. Rien ne le disait, parce que rien ne les
comparait.

CE QUI EST COMPARÉ. Les deux outils tournent sur le même classeur, chacun
vers un fichier temporaire HORS du dépôt (effacé à la fin). Puis :
  - les mêmes parties, dans le même ordre ;
  - les mêmes octets pour tout ce qui n'est pas du XML ;
  - le même XML, lu et non recopié : mêmes balises, mêmes attributs, même
    texte. Les deux outils réécrivent les commentaires chacun avec sa
    bibliothèque — préfixes d'espace de noms, guillemets de la déclaration —
    et ces différences-là ne disent rien du contenu ;
  - le même résumé : noms connus, remplacements, identifiants retirés.

Code 0 : identiques. Code 1 : une différence, détaillée. Code 2 : pas de
PowerShell (pwsh) sur ce poste, rien n'a été comparé — ce n'est pas une
réussite, et cela se dit.

Aucun nom n'est imprimé : on dit OÙ les sorties divergent, pas ce qu'elles
contiennent au-delà de quelques caractères d'un texte déjà anonymisé.

CE CONTRÔLE NE BLOQUE RIEN (le client, le 28/10/2026 : « je ne veux pas que
décider de le garder bloque les mises à jour des prochains classeurs »). La
mise à jour n'emploie que la version Python ; on la corrige et on la pousse
sans attendre le jumeau. Quand tout est identique, ce contrôle écrit
l'empreinte de la version Python dans tools/jumeau-verifie.txt ; le jumeau
compare cette empreinte à la version Python présente et REFUSE de tourner
si elle a changé depuis. En retard, il le dit au lieu de servir.
"""
import datetime, hashlib, os, re, shutil, subprocess, sys, tempfile, zipfile
import xml.etree.ElementTree as ET

ICI = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ICI, "anonymiser-classeur.py")
PS = os.path.join(ICI, "anonymiser-classeur.ps1")
VERIFIE = os.path.join(ICI, "jumeau-verifie.txt")


def empreinte_python():
    """L'empreinte de la version Python, fins de ligne ramenées à « \\n » :
    une copie Windows (CRLF) a la même. Le jumeau la calcule pareil."""
    with open(PY, "rb") as f:
        texte = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(texte).hexdigest()
RESUME = re.compile(r"(\d+) nom\(s\) connu\(s\) · (\d+) remplacement\(s\) dans (\d+) partie\(s\)"
                    r"|(\d+) identifiant\(s\) de connexion")


def _resume(sortie):
    out = []
    for m in RESUME.finditer(sortie):
        out.append(m.group(0).split(" · ")[0] if m.group(1) else m.group(0))
        if m.group(1):
            out.append("%s remplacements dans %s parties" % (m.group(2), m.group(3)))
    return out


def _arbre(e):
    """Un élément XML réduit à ce qu'il dit : balise, attributs, texte."""
    return (e.tag, sorted(e.attrib.items()), e.text or "", e.tail or "",
            [_arbre(x) for x in e])


def _premiere_difference(a, b, chemin="/"):
    if a[0] != b[0]:
        return chemin + " : balise %s / %s" % (a[0], b[0])
    if a[1] != b[1]:
        return chemin + a[0] + " : attributs différents"
    for k, nom in ((2, "texte"), (3, "suite")):
        if a[k] != b[k]:
            i = next(i for i in range(min(len(a[k]), len(b[k])) + 1)
                     if i >= len(a[k]) or i >= len(b[k]) or a[k][i] != b[k][i])
            return chemin + a[0] + " : %s différent dès le caractère %d" % (nom, i)
    if len(a[4]) != len(b[4]):
        return chemin + a[0] + " : %d enfants / %d" % (len(a[4]), len(b[4]))
    for k, (x, y) in enumerate(zip(a[4], b[4])):
        d = _premiere_difference(x, y, chemin + a[0].split("}")[-1] + "[%d]/" % k)
        if d:
            return d
    return None


def comparer(source):
    pwsh = shutil.which("pwsh") or shutil.which("powershell")
    if not pwsh:
        print("pas de PowerShell (pwsh) sur ce poste : rien n'a été comparé")
        return 2
    tmp = tempfile.mkdtemp(prefix="jumeau-")
    try:
        fp, fs = os.path.join(tmp, "py.xlsx"), os.path.join(tmp, "ps.xlsx")
        rp = subprocess.run([sys.executable, "-W", "ignore", PY, source, fp],
                            capture_output=True, text=True)
        rs = subprocess.run([pwsh, "-NoProfile", "-File", PS, source, fs, "-Confronter"],
                            capture_output=True, text=True, cwd=tmp)
        fautes = []
        if rp.returncode or not os.path.exists(fp):
            fautes.append("la version Python s'est arrêtée (code %d)" % rp.returncode)
        if rs.returncode or not os.path.exists(fs):
            fautes.append("la version PowerShell s'est arrêtée (code %d)" % rs.returncode)
        if fautes:
            for f in fautes:
                print("✗ " + f)
            return 1
        rsp, rss = _resume(rp.stderr), _resume(rs.stdout)
        if rsp != rss:
            fautes.append("résumés différents : Python %s · PowerShell %s" % (rsp, rss))
        zp, zs = zipfile.ZipFile(fp), zipfile.ZipFile(fs)
        np_, ns_ = zp.namelist(), zs.namelist()
        if np_ != ns_:
            fautes.append("parties différentes : en plus côté Python %s, côté PowerShell %s"
                          % (sorted(set(np_) - set(ns_)), sorted(set(ns_) - set(np_))))
        identiques = relues = 0
        for nom in [n for n in np_ if n in ns_]:
            a, b = zp.read(nom), zs.read(nom)
            if a == b:
                identiques += 1
                continue
            if not re.search(r"\.(xml|rels|vml)$", nom, re.I):
                fautes.append("%s : octets différents" % nom)
                continue
            try:
                d = _premiere_difference(_arbre(ET.fromstring(a)), _arbre(ET.fromstring(b)))
            except ET.ParseError as e:
                fautes.append("%s : XML illisible (%s)" % (nom, e))
                continue
            if d:
                fautes.append("%s%s" % (nom, d))
            else:
                relues += 1
        print("%s · %d partie(s) identique(s) à l'octet, %d au même XML"
              % (" · ".join(rsp), identiques, relues))
        for f in fautes:
            print("✗ " + f)
        return 1 if fautes else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    code = 0
    for s in sys.argv[1:]:
        print("— " + os.path.basename(s))
        code = max(code, comparer(s))
    if code == 0:
        with open(VERIFIE, "w", encoding="utf-8") as f:
            f.write("# Écrit par tools/jumeau-powershell.py quand les deux anonymiseurs rendent\n"
                    "# la même sortie. anonymiser-classeur.ps1 refuse de tourner si\n"
                    "# anonymiser-classeur.py a changé depuis : il serait peut-être en retard.\n"
                    "confronté le %s sur %d classeur(s)\n"
                    "anonymiser-classeur.py %s\n"
                    % (datetime.date.today().strftime("%d/%m/%Y"), len(sys.argv) - 1,
                       empreinte_python()))
        print("empreinte de la version Python enregistrée : le jumeau est à jour")
    sys.exit(code)
