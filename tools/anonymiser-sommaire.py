#!/usr/bin/env python3
"""Anonymise un « Sommaire mensuelle » scanné : le relevé de pointage.

    python3 tools/anonymiser-sommaire.py SCAN.pdf TRIGRAMME SORTIE.pdf
    python3 tools/anonymiser-sommaire.py SCAN.pdf TRI1,TRI2,... DOSSIER [--mois=AAAAMM]
    python3 tools/anonymiser-sommaire.py SCAN.pdf TRI:AAAAMM,TRI:AAAAMM,... DOSSIER

Un scan peut porter plusieurs relevés, une personne par page : on donne
alors UN TRIGRAMME PAR PAGE, dans l'ordre, et l'outil écrit un fichier par
personne et par mois dans DOSSIER (sommaire-TRI-AAAAMM.pdf) ; deux pages
d'un même trigramme et d'un même mois vont dans le même fichier. Le mois se
donne pour toute la série (--mois) ou page par page (TRI:AAAAMM). Si le nombre de trigrammes n'est pas
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
Section et « Sommaire de ». Le titre est la ligne « Sommaire mensuelle »
au-dessus. Chaque ligne est ensuite RECONNUE à la largeur de ses intitulés
(« Matricule: » fait dix signes dans la police à chasse fixe du relevé) :
une position comptée ne suffit pas, les poussières d'un scan peuvent
ajouter des lignes. (Le haut du tableau n'est pas un repère : son trait
est trop fin, le scan le rompt.) Si cette structure
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
POUSSIERE = 20                   # pixels d'encre sous lesquels un bloc est une poussière
PAS = DPI * 0.0615               # pas d'un signe de la police du relevé, en pixels


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
    """Blocs d'encre séparés par un blanc d'au moins une espace, POUSSIÈRES
    ÉCARTÉES. Un scan porte des points gris — l'autre face du papier, le
    copieur — : 1 à 15 pixels d'encre, là où une étoile en pèse 35 et un
    mot des centaines. Comptés comme des mots, ils faisaient échouer le
    repère des « * » (pages sautées) ou, pire, décalaient les lignes : sur
    un relevé de juin 2026, une bande de poussière au-dessus du titre
    passait pour le titre, et le vrai titre gardait le nom."""
    px = img.load()
    y0, y1 = bande
    cols = [sum(1 for y in range(y0, y1) if px[x, y] < 128) for x in range(img.width)]
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
    return [bl for bl in blocs if sum(cols[bl[0]:bl[1]]) >= POUSSIERE]


def largeur_de(n):
    """Largeur d'un mot de n signes dans la police à chasse fixe du relevé."""
    return n * PAS - 2


def est_mot(bloc, n):
    """Le bloc a-t-il la largeur d'un mot de n signes, à un signe près ?"""
    return abs((bloc[1] - bloc[0]) - largeur_de(n)) <= PAS


def zones(img):
    bandes = [b for b in lignes_de_texte(img, int(img.height * 0.45), int(img.width * 0.7))
              if mots(img, b)]          # une bande de poussière n'est pas une ligne
    M = [mots(img, b) for b in bandes]
    etoiles = [i for i, m in enumerate(M)
               if len(m) == 1 and m[0][1] < img.width * 0.06 and m[0][1] - m[0][0] <= PAS * 1.5]
    if not etoiles:
        raise ValueError("aucune ligne « * » : ce n'est pas la forme connue")
    i0 = etoiles[0]
    if etoiles != list(range(i0, i0 + len(etoiles))):
        raise ValueError("les lignes « * » ne se suivent pas")
    i_nom = etoiles[-1] + 1
    if i0 < 4:
        raise ValueError("Matricule et Section introuvables")
    # CHAQUE LIGNE SE RECONNAÎT À SES INTITULÉS, par leur largeur en signes :
    # une position comptée depuis les « * » peut tomber sur une autre ligne.
    attendu = [(i0 - 3, [10], "Matricule"), (i0 - 2, [8], "Section"),
               (i0 - 1, [8, 3], "Sommaire de"), (i_nom, [4], "Nom")]
    for i, largeurs, quoi in attendu:
        if i >= len(M) or len(M[i]) <= len(largeurs) or not all(
                est_mot(M[i][k], n) for k, n in enumerate(largeurs)):
            raise ValueError("ligne « %s » non reconnue à sa place" % quoi)
    # Le titre est la ligne « Sommaire mensuelle - <nom> » au-dessus : la
    # première bande de la page peut être de la poussière.
    titres = [i for i in range(i0 - 3)
              if len(M[i]) >= 3 and est_mot(M[i][0], 8) and est_mot(M[i][1], 9)]
    if len(titres) != 1:
        raise ValueError("ligne de titre introuvable (%d candidates)" % len(titres))
    z = []

    def apres(i, n_mots, quoi, texte):
        b = bandes[i]
        x0 = M[i][n_mots][0] - 4
        z.append((quoi, (x0, b[0] - 3, img.width - 20, b[1] + 3), texte))

    # Tout ce qui suit « mensuelle ». Le tiret, léger, passe souvent pour une
    # poussière : s'il est reconnu, il est repeint et se réécrit devant le
    # trigramme ; sinon il reste en place, et le trigramme seul suffit.
    t2 = M[titres[0]][2]
    apres(titres[0], 2, "titre", "- " if t2[1] - t2[0] <= PAS * 1.5 else None)
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
        d.text((x0 + 4, y0 + 1), (texte + tri) if texte == "- " else (texte or tri),
               fill="black", font=police)
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
    # « TRI » ou « TRI:AAAAMM » : une série peut mêler les mois d'une même
    # personne (le client, le 27/09/2026 : cinq personnes, janvier à août).
    tris, moisp = [], []
    for t in liste.split(","):
        t, _, m = t.strip().upper().partition(":")
        if not (len(t) == 3 and t.isalpha()):
            sys.exit("Un trigramme doit faire trois lettres : " + t)
        if m and not (len(m) == 6 and m.isdigit()):
            sys.exit("Un mois s'écrit AAAAMM : " + m)
        tris.append(t)
        moisp.append(m or (mois[0] if mois else ""))
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
        sorties, apercus = {}, {}
        for n, tri in enumerate(tris):
            suf = ("-" + moisp[n]) if moisp[n] else ""
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
