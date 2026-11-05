"""L'image du widget « Mon profil » en moyen (banniere-widget.jpg).

La bannière (banniere-biowanze-usine.png) intacte, réduite à 1600 px de
large, puis prolongée vers le bas : sa dernière bande (sous le mot
« biowanze », sans texte), étirée et floutée, et fondue jusqu'au fond du
widget, --surface (#212737) exactement. Le client, le 05/11/2026, maquette
à l'appui. Dépend de numpy, opencv-python-headless et Pillow.

    python3 tools/banniere-widget.py      # depuis la racine du dépôt
"""
import os, numpy as np, cv2
from PIL import Image
RACINE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src=np.asarray(Image.open(os.path.join(RACINE,'banniere-biowanze-usine.png')).convert('RGB')).astype(np.float32)
W=1600; H=round(540*W/2170)            # 398
b=cv2.resize(src,(W,H),interpolation=cv2.INTER_AREA)
EXT=0.42; T=H+round(H*EXT)
fond=np.array([33,39,55],np.float32)
# prolongement : la dernière bande (sous le mot), étirée et floutée
bande=b[H-12:H]
ext=cv2.resize(bande,(W,T-H),interpolation=cv2.INTER_LINEAR)
ext=cv2.GaussianBlur(ext,(0,0),sigmaX=18,sigmaY=10)
img=np.concatenate([b,ext],0)
# raccord : les 10 dernières lignes de la bannière glissent vers le prolongement flouté
for i in range(10):
    t=(i+1)/11; y=H-10+i; img[y]=b[y]*(1-t*0.6)+ext[0]*(t*0.6)
y=np.arange(T)/H                         # 0 = haut, 1 = bas de la bannière
xp=[0,0.50,0.88,1.0,1.18,1.36,EXT+1]
fp=[0,0.06,0.18,0.45,0.82,1.0,1.0]
a=np.interp(y,xp,fp)
a=a*a*(3-2*a)                            # lissé
a3=a.reshape(-1,1,1)
out=img*(1-a3)+fond*a3
o=np.clip(out.round(),0,255).astype(np.uint8)
Image.fromarray(o).save(os.path.join(RACINE,'banniere-widget.jpg'),quality=84,optimize=True,progressive=True)
print(o.shape, 'bas =', o[-1].mean(0).round(1))
