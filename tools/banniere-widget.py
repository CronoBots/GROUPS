"""L'image du widget « Mon profil » en moyen (banniere-widget.jpg).

La bannière (banniere-biowanze-usine.png) entière et intacte, réduite à
1600 px de large ; sous elle, le dégradé part de sa dernière ligne (le
blanc à droite, la photo à gauche), s'adoucit en descendant et finit sur
le fond du widget, --surface (#212737) exactement. Le client, le
05/11/2026 : « la transition ne doit pas couper le logo ; la bannière doit
être totalement visible et le blanc être le dégradé vers la partie
basse ». Dépend de numpy, opencv-python-headless et Pillow.

    python3 tools/banniere-widget.py      # depuis la racine du dépôt
"""
import os, numpy as np, cv2
from PIL import Image
RACINE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src=np.asarray(Image.open(os.path.join(RACINE,'banniere-biowanze-usine.png')).convert('RGB')).astype(np.float32)
W=1600; H=round(540*W/2170)            # 398
b=cv2.resize(src,(W,H),interpolation=cv2.INTER_AREA)
EXT=300                                 # le dégradé, sous la bannière (0,75 de sa hauteur)
fond=np.array([33,39,55],np.float32)
der=b[H-1]                              # la dernière ligne de la bannière
moy=b[H-8:].mean(0)                     # les 8 dernières, sans le détail d'une seule
ext=np.empty((EXT,W,3),np.float32)
for k in range(EXT):
    t=(k+1)/EXT
    sig=6+90*t**0.5                     # vite doux (sinon des stries), puis de plus en plus
    ligne=cv2.GaussianBlur(moy[None,:,:],(0,0),sigmaX=sig,sigmaY=0.1)[0]
    r=min(1,k/20); ligne=der*(1-r)+ligne*r  # la couture : de la vraie ligne au flou
    # de 0 (la ligne) à 1 (le fond). Le plus doux possible au départ (le
    # client, le 06/11/2026 : « optimise cette transition, plus douce ? »)
    # tant que le texte blanc posé dessus garde 4,5 : 1 de contraste au
    # milieu du titre (15 px sous la bannière à 390 px d'écran, 19 à 320)
    # et 3 : 1 en haut de ses lettres (9 px) : de toutes les longueurs et
    # puissances essayées, 300 px et 4,5 ont la pente de départ la plus
    # faible (0,015 contre 0,023 avant, 219 px et 5)
    a=1-(1-t)**4.5
    ext[k]=ligne*(1-a)+fond*a
o=np.clip(np.concatenate([b,ext],0).round(),0,255).astype(np.uint8)
assert (o[:H]==np.clip(b.round(),0,255).astype(np.uint8)).all()   # la bannière, intacte
Image.fromarray(o).save(os.path.join(RACINE,'banniere-widget.jpg'),quality=84,optimize=True,progressive=True)
print(o.shape, 'bas =', o[-1].mean(0).round(1))
