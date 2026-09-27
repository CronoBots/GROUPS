#!/usr/bin/env python3
"""Anonymise un « Sommaire mensuelle » scanné : le relevé de pointage.

    python3 tools/anonymiser-sommaire.py SCAN.pdf TRIGRAMME SORTIE.pdf
    python3 tools/anonymiser-sommaire.py SCAN.pdf TRI1,TRI2,... DOSSIER [--mois=AAAAMM]

Un scan peut porter plusieurs relevés, une personne par page : on donne
alors UN TRIGRAMME PAR PAGE, dans l'ordre, et l'outil écrit un fichier par
personne dans DOSSIER (sommaire-TRI-AAAAMM.pdf) ; deux pages d'un même
trigramme vont dans le même fichier. Si le nombre de trigrammes n'est pas
celui des pages, il s'arrête. Chaque page est traitée avant qu'un seul
fichier s'écrive : une page de forme inconnue, et rien n'est écrit.

Le relevé arrive SCANNÉ : aucune couche de texte, une image de fond et des
masques noir et blanc (le copieur fait du « MRC »). On ne peut donc pas y
remplacer un mot : on repeint des zones.

Ce qui identifie la personne, et ce que l'outil en fait :

  ligne de titre   « Sommaire mensuelle - <Prénom Nom> »  → le trigramme
  Matricule:       le numéro de contrat, celui des fiches  → « (retiré) »
  Section:         le centre de frais                      → « (retiré) »
  Nom:             « <Prénom Nom> »                        → le trigramme
  métadonnées      l'identifiant de connexion de celui qui a scanné, le
                   copieur, le titre                       → vidées
  nom du fichier   porte ce même identifiant               → choisi par vous

Tout le reste — compteurs, période, journées, codes, pointages — passe tel
quel, et c'est vérifié : l'image produite est comparée pixel par pixel à la
source HORS des zones repeintes, et elle ne doit différer nulle part.

LES ZONES SE TROUVENT PAR LA STRUCTURE, pas par des coordonnées : chaque
ligne de texte de l'en-tête est repérée par sa bande d'encre. Le repère est
la suite des lignes « * », qui n'ont qu'un signe, tout à gauche : la ligne
juste en dessous est « Nom: », les trois juste au-dessus sont Matricule,
Section et « Sommaire de ». Le titre est la première ligne de la page. (Le
haut du tableau n'est pas un repère : son trait est trop fin, le scan le
rompt.) Si cette structure
n'est pas retrouvée, l'outil S'ARRÊTE sans rien écrire : un relevé d'une
autre forme se regarde avant qu'on invente où est le nom.

LA GARANTIE N'EST PAS COMPLÈTE, et il faut le savoir : sans lecture de
caractères, l'outil ne peut pas CHERCHER le nom ailleurs sur la page. Il
écrit un aperçu PNG à côté de la sortie, et on le regarde avant de s'en
servir — toujours, une page après l'autre.

LE TRIGRAMME SE DONNE À LA MAIN, et il se VÉRIFIE : l'initiale du prénom
puis la première et la dernière lettre du nom, comme l'anonymiseur — mais
`CORRECTIONS` renomme certaines personnes (deux pouvaient porter CDE). On
confronte alors les pauses du relevé à l'horaire des candidats : elles
doivent concorder jour pour jour.

La sortie est une image pure, remise dans un PDF neuf : aucune couche du
scan d'origine ne survit en dessous de ce qui a été repeint.

Dépendances : pymupdf et pillow (`pip install pymupdf pillow`).
"""
import os
import sys

try:
    import pymupdf
    from PIL import Image, ImageChops, ImageDraw, ImageFont
except ImportError:
    sys.exit("Il faut pymupdf et pillow : pip install pymupdf pillow")

DPI = 200
POLICE = "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf"


def lignes_de_texte(img, y_max, x_max):
    """Bandes horizontales d'encre au-dessus de y_max, dans x < x_max."""
    px = img.load()
    w = min(img.width, x_max)
    encre = []
    for y in range(y_max):
        encre.append(any(px[x, y] < 128 for x in range(0, w, 2)))
    bandes, debut = [], None
    for y, e in enumerate(encre + [False]):
        if e and debut is None:
            debut = y
        elif not e and debut is not None:
            if y - debut >= 6:          # une poussière de scan n'est pas une ligne
                bandes.append((debut, y))
            debut = None
    return bandes


def mots(img, bande):
    """Blocs d'encre séparés par un blanc d'au moins une espace."""
    px = img.load()
    y0, y1 = bande
    cols = [any(px[x, y] < 128 for y in range(y0, y1)) for x in range(img.width)]
    esp = int(DPI * 0.045)              # une espace de la police du relevé
    blocs = []
    debut = dernier = None
    for x, c in enumerate(cols):
        if c:
            if debut is None:
                debut = x
            elif x - dernier > esp:
                blocs.append((debut, dernier + 1))
                debut = x
            dernier = x
    if debut is not None:
        blocs.append((debut, dernier + 1))
    return blocs


def zones(img):
    bandes = lignes_de_texte(img, int(img.height * 0.45), int(img.width * 0.7))
    etoiles = [i for i, b in enumerate(bandes)
               if len(mots(img, b)) == 1 and mots(img, b)[0][1] < img.width * 0.06]
    if not etoiles:
        raise ValueError("aucune ligne « * » : ce n'est pas la forme connue")
    i0 = etoiles[0]
    if etoiles != list(range(i0, i0 + len(etoiles))):
        raise ValueError("les lignes « * » ne se suivent pas")
    i_nom = etoiles[-1] + 1
    if i_nom >= len(bandes) or len(mots(img, bandes[i_nom])) < 2:
        raise ValueError("pas de ligne « Nom: » sous les « * »")
    if i0 < 4:
        raise ValueError("Matricule et Section introuvables")
    z = []

    def apres(i, n_mots, quoi, texte):
        b = bandes[i]
        m = mots(img, b)
        if len(m) <= n_mots:
            raise ValueError("ligne %s : pas de valeur après l'intitulé" % quoi)
        x0 = m[n_mots][0] - 4
        z.append((quoi, (x0, b[0] - 3, img.width - 20, b[1] + 3), texte))

    apres(0, 3, "titre", None)          # « Sommaire mensuelle - »
    apres(i0 - 3, 1, "Matricule", "(retiré)")
    apres(i0 - 2, 1, "Section", "(retiré)")
    apres(i_nom, 1, "Nom", None)
    return z


def repeindre(img, tri, n):
    """Repeint une page ; rend les zones. Lève ValueError si la forme manque."""
    zs = zones(img.convert("L"))
    avant = img.copy()
    d = ImageDraw.Draw(img)
    for quoi, (x0, y0, x1, y1), texte in zs:
        d.rectangle((x0, y0, x1, y1), fill="white")
        police = ImageFont.truetype(POLICE, int((y1 - y0) * 0.85))
        d.text((x0 + 4, y0 + 1), texte or tri, fill="black", font=police)
    # Fidélité : hors des zones, pas un pixel ne diffère.
    diff = ImageChops.difference(avant, img).convert("L")
    masque = Image.new("L", diff.size, 255)
    dm = ImageDraw.Draw(masque)
    for _q, box, _t in zs:
        dm.rectangle(box, fill=0)
    reste = ImageChops.multiply(diff, masque).getbbox()
    if reste:
        raise ValueError("FIDÉLITÉ : la page diffère hors des zones, en %s" % (reste,))
    return zs


def ecrire(images, out):
    neuf = pymupdf.open()
    for img in images:
        p = neuf.new_page(width=img.width * 72 / DPI, height=img.height * 72 / DPI)
        tmp = out + ".tmp.png"
        img.save(tmp)
        p.insert_image(p.rect, filename=tmp)
        os.remove(tmp)
    neuf.set_metadata({})
    neuf.save(out, garbage=4, deflate=True, no_new_id=True)
    meta = {k: v for k, v in pymupdf.open(out).metadata.items()
            if v and k not in ("format", "encryption")}
    if meta:
        os.remove(out)
        sys.exit("MÉTADONNÉES restantes, %s détruit : %s" % (out, meta))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--mois=")]
    mois = [a[7:] for a in sys.argv[1:] if a.startswith("--mois=")]
    if len(args) != 3:
        sys.exit(__doc__)
    src, liste, out = args
    tris = [t.strip().upper() for t in liste.split(",")]
    for t in tris:
        if not (len(t) == 3 and t.isalpha()):
            sys.exit("Un trigramme doit faire trois lettres : " + t)
    doc = pymupdf.open(src)
    if len(tris) != len(doc):
        sys.exit("%d page(s) dans le scan, %d trigramme(s) donné(s) : il en faut "
                 "un par page, dans l'ordre" % (len(doc), len(tris)))
    pages = []
    for page in doc:
        pix = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csRGB)
        pages.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))

    # Tout ou rien : chaque page est traitée avant qu'un seul fichier s'écrive.
    for n, (img, tri) in enumerate(zip(pages, tris), 1):
        try:
            zs = repeindre(img, tri, n)
        except ValueError as e:
            sys.exit("PAGE %d (%s) : STRUCTURE NON RECONNUE, rien n'est écrit : %s"
                     % (n, tri, e))
        print("  page %2d  %s  %s" % (n, tri, "  ".join(q for q, _b, _t in zs)))

    if len(pages) == 1 and out.lower().endswith(".pdf"):
        sorties = {out: [0]}
        apercus = {0: os.path.splitext(out)[0] + "-apercu.png"}
    else:
        os.makedirs(out, exist_ok=True)
        suf = ("-" + mois[0]) if mois else ""
        sorties, apercus = {}, {}
        for n, tri in enumerate(tris):
            f = os.path.join(out, "sommaire-%s%s.pdf" % (tri, suf))
            sorties.setdefault(f, []).append(n)
            apercus[n] = os.path.join(out, "apercu-p%02d-%s.png" % (n + 1, tri))
    for f, ns in sorties.items():
        ecrire([pages[n] for n in ns], f)
        print("écrit : %s (%d page(s)), métadonnées vides" % (f, len(ns)))
    for n, a in apercus.items():
        pages[n].save(a)
    print("À REGARDER avant usage : les %d aperçus PNG" % len(apercus))


if __name__ == "__main__":
    main()
