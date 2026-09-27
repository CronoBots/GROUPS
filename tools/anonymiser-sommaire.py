#!/usr/bin/env python3
"""Anonymise un « Sommaire mensuelle » scanné : le relevé de pointage.

    python3 tools/anonymiser-sommaire.py SCAN.pdf TRIGRAMME SORTIE.pdf

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
servir — toujours. Les pages au-delà de la première sont recopiées et
signalées.

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


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    src, tri, out = sys.argv[1], sys.argv[2].upper(), sys.argv[3]
    if not (len(tri) == 3 and tri.isalpha()):
        sys.exit("Le trigramme doit faire trois lettres : " + tri)
    doc = pymupdf.open(src)
    pages = []
    for n, page in enumerate(doc):
        pix = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csRGB)
        pages.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    gris = pages[0].convert("L")
    try:
        zs = zones(gris)
    except ValueError as e:
        sys.exit("STRUCTURE NON RECONNUE, rien n'est écrit : %s" % e)

    avant = pages[0].copy()
    d = ImageDraw.Draw(pages[0])
    for quoi, (x0, y0, x1, y1), texte in zs:
        d.rectangle((x0, y0, x1, y1), fill="white")
        police = ImageFont.truetype(POLICE, int((y1 - y0) * 0.85))
        d.text((x0 + 4, y0 + 1), texte or tri, fill="black", font=police)
        print("  %-10s repeint  x %4d-%4d  y %4d-%4d" % (quoi, x0, x1, y0, y1))

    # Fidélité : hors des zones, pas un pixel ne diffère.
    diff = ImageChops.difference(avant, pages[0]).convert("L")
    masque = Image.new("L", diff.size, 255)
    dm = ImageDraw.Draw(masque)
    for _q, box, _t in zs:
        dm.rectangle(box, fill=0)
    reste = ImageChops.multiply(diff, masque).getbbox()
    if reste:
        sys.exit("FIDÉLITÉ : l'image diffère hors des zones, en %s" % (reste,))

    neuf = pymupdf.open()
    for img in pages:
        p = neuf.new_page(width=img.width * 72 / DPI, height=img.height * 72 / DPI)
        tmp = out + ".tmp.png"
        img.save(tmp)
        p.insert_image(p.rect, filename=tmp)
        os.remove(tmp)
    neuf.set_metadata({})
    neuf.save(out, garbage=4, deflate=True, no_new_id=True)
    apercu = os.path.splitext(out)[0] + "-apercu.png"
    pages[0].save(apercu)

    meta = {k: v for k, v in pymupdf.open(out).metadata.items()
            if v and k not in ("format", "encryption")}
    if meta:
        sys.exit("MÉTADONNÉES restantes : %s" % meta)
    print("écrit : %s (%d page(s)), métadonnées vides" % (out, len(pages)))
    print("À REGARDER avant usage : %s" % apercu)
    if len(pages) > 1:
        print("ATTENTION : pages 2 à %d recopiées sans traitement — à regarder"
              % len(pages))


if __name__ == "__main__":
    main()
