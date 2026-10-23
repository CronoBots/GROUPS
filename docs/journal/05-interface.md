# Barre du haut, thème, téléphone, Accueil, héros, Planning, agenda

Historique déplacé tel quel de `CLAUDE.md` le 18/10/2026. Les dates, mesures et erreurs y restent.

## La barre du haut est une barre d'identité

Le client, le 22/09/2026 : « la barre du haut doit être une vraie barre
personnelle, avec le logo, le trigramme et le poste actuel ; il faut que ce
soit 100 % professionnel ».

Trois choses, dans l'ordre où on les cherche : **à qui appartient cet écran**
(le logo, déjà mis en cache par le service worker), **qui le regarde** (le
trigramme, sur une plaque), et **ce qu'il fait aujourd'hui**. La fonction
seule — « Contremaître » — ne disait rien du jour ; `posteDuJourDe()` rejoue
`equipeDuJour()` et `postesDePause()` pour la date du jour et rend
« Contremaître · nuit », « STEP · matin », « Jour », « Congé » ou « Repos ».
Il ne recompte rien : c'est la vue de l'équipe qui répond.

**Deux BLOCS, et non deux lignes.** Le client, le 22/09/2026 : « la date au
dessus à droite et le poste en dessous avec la pause ; le trigramme doit
être près de BIOWANZE ».

À gauche, ce qui ne change **jamais** : le logo, le nom, le trigramme — d'un
seul tenant, parce que c'est une seule chose, à qui appartient cet écran. À
droite, ce qui change **chaque jour** : la date, et sous elle le poste avec
sa pause, les deux lignes alignées sur le même bord. On lit la colonne de
droite pour savoir sa journée, jamais celle de gauche.

```
[logo] BIOWANZE [VBN]                    Mardi 22 septembre
                                        Contremaître · Nuit
```

Deux dispositions l'ont précédée dans la même journée, et chacune corrigeait
la précédente : le nom seul sur une ligne presque vide, puis le nom à gauche
et le trigramme à l'autre bout avec date et poste dessous. La première
gaspillait quatre cinquièmes de sa première ligne ; la seconde séparait le
trigramme du nom, alors qu'ils disent la même chose.

**Le jour et la pause portent une majuscule** — « Mardi 22 septembre »,
« Contremaître · **N**uit ». Le client : « le jour doit avoir une majuscule
et la pause aussi ». Ce sont les deux mots qu'on cherche du regard ; le
mois, lui, accompagne le quantième et reste en bas de casse. Concrètement :
`dateDuJourLisible()` ne rabaisse plus `JOURS_LONGS`, et `posteDuJourDe()`
ne rabaisse plus `g.t`.

Mesuré à 320, 360, 390, 430, 768 et 1280 px : **58 px de barre**, et **rien
de tronqué, 320 px compris** — où les deux blocs se frôlent à 12 px. Au-delà
de 760 px la marque se réduit à sa largeur de contenu et les deux blocs se
retrouvaient à 10 px l'un de l'autre alors que la barre a mille pixels de
vide plus loin : `@media (min-width:761px)` leur rend 20 px. Sur téléphone
il n'y en a pas à donner.

Vérifié sur six états — Matin, Après-midi, Nuit, Congé, Repos, Absent — et
hors ligne : logo, trigramme, date et poste du jour se rendent tous.

**Elle s'efface quand on descend.** Le client, le 22/09/2026, cherchant
comment l'optimiser encore. Elle se replie dès qu'on descend PASSÉ sa propre
hauteur, et revient entière au premier geste vers le haut : **53 px rendus
au contenu** sur l'Équipe, la Polyvalence et l'Horaire — une ligne de tableau
entière — sans rien perdre, puisqu'elle est là dès qu'on la cherche.

Trois précautions, et chacune répare un défaut qu'on aurait eu :

- **un seuil de six pixels** — sans lui, le tremblement d'un doigt posé sur
  l'écran la fait battre ;
- **tant qu'on est dans ses propres pixels** (`y <= sa hauteur`) elle reste —
  se replier là n'aurait rien découvert et l'aurait fait sauter ;
- **un défilement négatif la redéplie toujours**, même sous le seuil : c'est
  le geste par lequel on la cherche.

**SEULEMENT SOUS 760 px**, et c'est essentiel : au-delà, la barre d'ONGLETS
remonte dans cet en-tête. La replier ferait disparaître la navigation, pour
gagner de la hauteur là où il n'en manque pas. Le garde-fou est dans la
FEUILLE (`@media (max-width:760px){ .top.repliee{…} }`) et non dans le
script : une fenêtre redimensionnée à travers le seuil se comporte
correctement sans écouteur de plus.

Sur téléphone, la barre d'onglets ne bouge pas : elle vit dans son propre
cadre ancré par ses quatre côtés, sans rapport avec cet en-tête.

Le repli tombe de lui-même sous `prefers-reduced-motion`, qui coupe toutes
les transitions de la feuille — il devient instantané plutôt que d'être
imposé en mouvement.

Mesuré à 320, 390, 430 et 1280 px, sur cinq positions de défilement et un
changement d'onglet : replié à 600 px de descente, redéplié à 120 px de
remontée, toujours visible en haut de page, et **immobile à 1280 px**.

**Le logo fait 32 px, et non 38.** C'est LUI qui fixait la hauteur de la
barre, pas le texte : 38 px contre 31 pour le bloc de droite. Mesuré à
l'essai — 34 donnent 54 px de barre, 32 en donnent 52, et en dessous il n'y
a plus rien à gagner, le texte reprenant la main à 51. **La barre passe de
58 à 52 px** (53 avec son filet), sur tous les onglets, en permanence.

**Le sélecteur de mois n'y est plus.** Le client, le 22/09/2026 : « la
sélection du mois de l'année ne doit pas être dans la barre du haut mais
seulement là où elle est nécessaire dans les onglets ». Il était masqué
onglet par onglet — quatre règles CSS pour le cacher là où il n'a rien à
dire — et occupait quand même la place la plus chère de l'écran sur les
autres.

Il se **range** désormais dans l'onglet qui l'emploie : Résumé, Horaire,
Fiche et Contrôle ont un `.mnavhote`, les autres n'en ont pas et il
disparaît. **Un seul exemplaire déménage**, comme la barre d'onglets : quatre
copies auraient demandé quatre jeux d'écouteurs, et rien n'aurait garanti
qu'elles affichent le même mois.

Deux mécanismes sont morts avec ce déménagement et ont été retirés plutôt
que laissés en place : le mois abrégé (`sept. 2026`, un compromis pour cinq
pixels manquants dans l'en-tête) et le masquage de « BIOWANZE » sous 340 px.
**Un mécanisme qui ne sert plus égare celui qui le relit.**

**`flex:1 1 0`, et non `auto`** — cela reste vrai pour la marque. Un élément
flexible se replie selon sa taille de BASE, pas selon sa taille minimale :
avec `auto`, elle réclamait ses 190 px avant d'accepter de rétrécir.

Vérifié hors ligne : logo, trigramme, date et poste du jour se rendent tous.

### Le net à recevoir n'y est plus

Le client, le 23/09/2026 : « le cadre avec le net à recevoir apparaît encore
dans la barre de navigation du haut, cela ne doit pas arriver ».

Cette barre dit trois choses — à qui appartient cet écran, qui le regarde, ce
qu'il fait aujourd'hui. **Un montant n'en est pas une**, et surtout pas
celui-là : c'est le chiffre le plus personnel de l'application, qui restait
affiché en permanence, sur tous les onglets, par-dessus l'épaule de
n'importe qui. Il se lit dans « Mon salaire », qui est fait pour lui — deux
fois même, en tête du panneau et au pied de la fiche simulée.

Il avait déjà à moitié perdu sa place : **cinq règles le masquaient onglet
par onglet** et une sixième le repliait sous 760 px, si bien qu'il ne se
voyait plus que sur deux vues. Un élément qu'on passe son temps à cacher n'a
pas sa place où on l'a mis. Sont partis avec lui ses trois règles de mise en
forme, celle qui l'habillait de blanc sur le bleu, et l'écriture de `#netTop`
dans `renderSlip()` — **laisser cette ligne aurait suffi à casser tout le
calcul**, `getElementById` rendant `null`.

## Un horaire qu'on ne peut plus lire vide tout, en silence

Le client, le 23/09/2026 : « Mon salaire n'est plus correctement calculé et
tout est vide dans l'onglet » — 0 journée sur 30, zéro heure, zéro prime,
zéro chèque-repas, et un net réduit à la seule rémunération fixe.

**Le calcul n'avait rien.** C'est `data/horaire-2026.json` que son appareil
n'arrivait plus à lire, et tout en dépend : sans lui le sélecteur de personne
reste vide, donc `prefillAuto()` sort sans rien faire, donc le mois reste
blanc — et la cascade continue de se dérouler sur la rémunération fixe, avec
des zéros parfaitement crédibles.

**Le service worker mettait en cache n'importe quelle réponse.** Une page
d'erreur, un 404, un portail Wi-Fi qui répond une page de connexion : `c.put`
la déposait à la place du fichier, et le cache d'abord la resservait ensuite
à chaque ouverture. **Le défaut se réparait tout seul une fois posé** — ni le
retour du réseau, ni un rechargement, ni une nouvelle version de la page n'y
changeaient quoi que ce soit ; seul un changement de `V`, qui efface les
anciens caches, le levait par accident.

Reproduit avec Playwright en empoisonnant l'entrée à la main : sur un profil
neuf, l'écran du client, au pixel près.

Deux remèdes, et il en faut deux :

- **`cacheSiBon()` dans `sw.js`** : une réponse qui se LIT et qui n'est pas
  bonne ne remplace plus jamais ce qui est en cache, et un rafraîchissement
  d'horaire qui échoue RETIRE l'entrée au lieu d'en garder une dont on ne
  sait plus rien. Les réponses **opaques** passent toujours — les polices sont
  demandées sans CORS, on ne peut ni lire leur code ni les juger, et les
  refuser priverait la page de ses polices hors ligne ;
- **`fetchHoraireDB()` se soigne lui-même** : un appareil déjà empoisonné ne
  guérit pas d'une garde écrite après coup. Un horaire illisible — la
  coupure réseau, le code HTTP, le JSON invalide, ou un fichier sans personne
  dedans — fait vider
  l'entrée de tous les caches et refaire le trajet UNE fois, avec un
  paramètre d'URL et `cache:"no-store"` pour interdire qu'on ressorte la
  même réponse. Le premier essai, lui, se sert normalement : le cache
  d'abord, c'est tout l'intérêt de ne pas attendre 690 Ko.

**Et si les deux échouent, cela se DIT.** Un bandeau qui reste en haut de la
page, pas une bulle de deux secondes : sans horaire, la moitié de
l'application affiche des zéros qu'on peut croire. `flash()` ne convenait
pas — le message passait avant même qu'on ait regardé l'écran.

Vérifié aux quatre états : marche normale, cache empoisonné qui guérit, hors
ligne avec un bon cache, horaire injoignable où le bandeau parle. Contraste
du bandeau 5,4:1 en clair et 6,3:1 en sombre, et l'audit complet des six
onglets reste à **0 texte sous le seuil** dans les deux thèmes.

**Le piège de l'épreuve** : `page.route()` n'intercepte pas les requêtes
émises par le SERVICE WORKER. Un premier essai croyait couper l'horaire et
le laissait passer, bandeau éteint et 11 personnes dans le sélecteur. Il faut
`serviceWorkers:"block"` sur le contexte pour éprouver ce cas-là.

## Le thème entier est de la famille de la marque

Le client, le 23/09/2026 : « modifie tout le thème du site pour qu'il soit en
accord avec les deux nouvelles barres de navigation ; je veux des couleurs
qui fassent professionnel et que ce soit un résultat incroyable ».

**Le défaut tenait en un chiffre.** Les gris de l'application étaient un
gris-pétrole — teinte 238 à 244 en OKLCH — alors que la tuile du logo est un
bleu-nuit à **262**. Les barres flottaient donc sur une page d'une autre
famille, et c'est cela qu'on voyait.

Toute la rampe neutre est **rebâtie à la teinte de la marque**, chroma
décroissant à mesure que la clarté monte : une page claire franchement
teintée de violet se remarquerait. Les pas sont **calculés en OKLCH**, pas
choisis à l'œil — `scratchpad/oklch.js` et `rampe.js` font la conversion
sRGB ↔ OKLab dans les deux sens.

**L'ordre des plans ne change pas** : la page reste le plus sombre, la carte
vient au-dessus, et la barre du haut se place juste au-dessus d'elle. Seule
la FAMILLE change.

**L'accent est le cyan du logo**, pris plus profond pour tenir sur du blanc :
même teinte (222), pas la même clarté. Il ne vient plus d'ailleurs.

**Les teintes de l'usine ne bougent pas** — elles disent les pauses et les
ateliers, pas la marque — mais tous leurs pas sont recalculés sur une même
clarté et un même chroma. Le contraste de chacun sur son fond doux tient
entre 4,6 et 5,6:1, là où l'ancienne série allait de 3,9 à 7,2.

### Un seul thème, le sombre

Le client, le 30/09/2026 : « l'app ne doit avoir que le thème sombre ».
`<html data-theme="dark">` le pose quel que soit le réglage du téléphone,
`color-scheme:dark` partout, et le manifeste prend `#111727` pour fond et
couleur de thème. Le bloc `@media (prefers-color-scheme: dark)` était la
copie exacte de `:root[data-theme="dark"]` (55 jetons sur 55) : il est
retiré. Le `:root` clair reste comme base que le bloc sombre surcharge.
**Ce qui est écrit dans ce fichier sur le thème clair ne vaut plus** que
comme histoire. Vérifié avec un téléphone réglé en clair, à 320 (hors
ligne), 390 et 1280 px : tout est sombre, filigrane compris.

### Zéro texte sous le seuil, et il y en avait 456

Un audit qui parcourt les six onglets, calcule le fond RÉEL de chaque texte
(en remontant les parents jusqu'à une couleur opaque) et le compare au seuil
WCAG de sa taille : **456 textes en dessous en thème sombre, 460 en clair**,
avant. Personne ne l'avait mesuré.

La cause était une seule : `--faint` portait des centaines de libellés —
unités, sous-titres, mentions — à **3,0:1**. Elle passe à 5,5:1 sur la carte
et 4,7 sur la page ; `--muted` descend d'autant pour que la hiérarchie reste
lisible. Le dernier récalcitrant, « virement de fin de mois » sur le fond
d'accent, a été réglé en assombrissant `--in-soft`.

**Résultat : 0 sur 0**, dans les deux thèmes, à 390 et 1280 px, sur les six
onglets.

**`--sur-in` est né de cet audit** : l'encre qui se pose SUR l'accent ne peut
pas être « blanc » dans les deux thèmes, puisqu'en sombre l'accent est le
cyan clair du logo — du blanc dessus se lit à 1,9:1. Le bouton principal
l'écrivait en dur.

**Les deux palettes du calendrier sont inchangées et revalidées** contre les
nouvelles surfaces par `scripts/validate_palette.js` du savoir-faire
« dataviz », en mode « toutes paires » : tout passe, pire paire 23,2 en
vision normale en clair, 16,6 en sombre.

## Les deux barres portent la couleur du logo

Le client, le 22/09/2026 : « barre de navigation de la même couleur que le
background du logo », puis le 23/09 : « j'aimerais aussi que le background
des barres du haut ET DU BAS soit de la même couleur que le background du
logo Biowanze ». C'est **`#111727`** depuis le 23/09/2026 — le fond du NOUVEAU logo, et non
plus la tuile de `logo.png`.

**Le client l'a dit à l'envers de ce que j'avais compris, et il a fallu le
mesurer pour s'en rendre compte.** « J'aimerais que la couleur du background
de ce screen soit le background des barres de navigation » : sa page donne la
couleur, la barre la reçoit — et non l'inverse. J'avais lu la phrase dans
l'autre sens et je lui ai expliqué que ses couleurs étaient fausses. Elles ne
l'étaient pas.

**Les deux fonds sont relevés au PIXEL sur ses captures**, par histogramme :
sa barre de navigation est `#111727` à 38 % des pixels du bandeau, et le fond
de son contenu `#F6F6F6` à 52 % des marges. On ne devine pas une couleur de
marque, on la mesure — c'est déjà comme cela que `#1A2539` avait été relevé
dans `logo.png`.

**Tout le reste suit** : la rampe neutre se réancre sur la teinte du nouveau
bleu (268 au lieu de 262), le thème clair prend `#F6F6F6` pour page, et le
sombre se restéage pour que la barre reste lisible entre la page et les
cartes. Zéro texte sous le seuil WCAG, dans les deux thèmes, après comme
avant.

**Les règles de l'en-tête portent toutes `.top` devant** : elles battent par
la SPÉCIFICITÉ celles qui le peignaient, et non par leur position. C'est ce
qui les rend sûres — le piège de la requête média, qui n'ajoute aucune
spécificité, s'est déjà refermé trois fois sur ce fichier.

Au-delà de 760 px la barre d'onglets remonte DANS cet en-tête : elle y prend
les mêmes encres que dans son cadre du bas, sans quoi elle disparaîtrait sur
le bleu. Sous 760 px elle n'est pas là, et ces règles ne l'atteignent pas.

**`<meta name="theme-color">` suit**, et n'a plus qu'une valeur : la barre
d'état du téléphone prend la couleur de la barre du haut, sans quoi un
liseré d'une autre teinte la surmonte. Les deux déclarations par thème n'ont
plus lieu d'être — une couleur de marque n'appartient ni au clair ni au
sombre.

**Le logo passe à 36 px** — « le logo peut être légèrement plus grand ». Il
redevient ce qui fixe la hauteur de la barre : **57 px au lieu de 52**.

**Et c'est le logo VECTORIEL, en négatif**, que le client a poussé lui-même
le 23/09/2026 pour qu'il s'affiche dans la barre. Texte blanc, marque en
dégradé, fond transparent : il se pose sur le bleu nuit sans tuile ni coin
arrondi, comme il est dessiné pour l'être — là où `icon-192.png` apportait
son propre fond.

**36 px de HAUT et la largeur suit** : le dessin fait 1810 × 1388, il se
déformerait dans un carré. Il rend 47 × 36, et rien n'est tronqué même à
320 px, où la marque et le bloc du jour se frôlent à 10 px.

**`logo.svg` entre dans `CORE` du service worker.** Sans cela la barre
serait nue hors ligne — vérifié avec `setOffline(true)` : il se rend depuis
le cache. « BIOWANZE » reste écrit à côté : le mot du lockup fait cinq
pixels de haut à cette taille, il décore, il ne se lit pas.

Les icônes de la PWA restent en PNG — le manifeste n'accepte pas autre
chose pour l'installation.

Elle se pose dans les **deux thèmes**, et c'est le point : une couleur de
marque n'appartient ni au clair ni au sombre. D'où deux jetons déclarés une
seule fois, hors des deux blocs de thème — `--marque` et `--marque-vif` — et
des couleurs d'écriture à elle, en blanc transparent. Sans cela, en thème
clair, `--ink` est presque noir et `--in` un bleu foncé : les deux
disparaîtraient sur ce fond.

Mesuré dans les deux thèmes : fond `rgb(26, 37, 57)` — exactement celui de
la tuile — **contraste 7,46:1** pour un onglet au repos et **6,46:1** pour
l'onglet actif, contre un seuil de 4,5.

Les trois règles qui peignent les boutons ont la MÊME spécificité que celles
du haut de la feuille, qui peignent la barre du bureau ; **elles gagnent
parce qu'elles sont écrites après**. Ne pas les déplacer plus haut — c'est
le même piège que la zébrure de la polyvalence et que la barre d'onglets
sous 375 px.

## La barre d'onglets n'est pas ancrée par une unité de hauteur

Elle vit dans un cadre à elle, `.navwrap`, hors de l'en-tête collant — c'est
la bonne moitié d'un remède de septembre 2026, et il faut la garder.

L'autre moitié était fausse : le cadre tirait sa hauteur de `100dvh`. Sous
iOS cette unité se trompe quand la barre d'URL est **réduite** — Safari
continue d'annoncer la hauteur de la barre pleine, le cadre devient plus
court que l'écran, et la barre d'onglets remonte d'autant. Le client l'a
photographié le 22/09/2026 : deux lignes du tableau visibles SOUS la barre.

Le cadre est donc ancré par ses **quatre côtés**, sans aucune unité à
interpréter. Le premier remède avait eu tort de bannir `bottom` : ce n'est
pas lui qui se résolvait mal, c'est l'en-tête collant qui l'enfermait.

Mesuré à 320, 360, 430 et 760 px, sur quatre onglets et quatre positions de
défilement : **écart de 0 px au bas de l'écran**, y compris sur un onglet
plus court que l'écran — le cas que l'ancien commentaire décrivait comme
cassé. Au-delà de 760 px la barre remonte dans l'en-tête, inchangée.

**Chromium ne reproduit pas le défaut d'iOS** : la mesure prouve que la
dépendance à `dvh` a disparu, pas que le téléphone est guéri. Seul l'appareil
du client peut le dire.

## Sur téléphone, une vitrine

Le client, le 29/09/2026 : « je veux que même sur mobile cela soit une
expérience unique, une vitrine de mon savoir-faire ». Avant d'ajouter quoi
que ce soit, les six onglets ont été photographiés à 390 px dans les deux
thèmes. **Quatre défauts sont apparus, et ils passaient avant la finition** :

- **les textes d'introduction portaient la classe `top`**, celle de la
  barre du haut. Ils étaient donc COLLANTS (`position:sticky`, z-index 40)
  et peints en bleu nuit : en thème clair, « Choisissez votre fonction… »
  s'écrivait en gris sur du bleu nuit, presque illisible. Personne ne
  l'avait vu parce qu'en sombre la page est déjà bleu nuit. La classe
  s'appelle désormais `haut`. **Un nom de classe générique en rejoint un
  autre sans le dire** ;
- **les onglets passaient à la ligne à 390 px** : `nowrap` ne valait que
  sous 375 px, et l'onglet choisi, en gras, poussait « Mon horaire » sur
  deux lignes. La barre fait maintenant la même hauteur (62 px) quel que
  soit l'onglet ;
- **les tuiles de « Mon horaire »** prenaient la largeur de leur libellé :
  deux rangées qui ne tombaient jamais d'aplomb, la première collée au
  filet de l'en-tête. C'est désormais une grille de colonnes égales ;
- **les intitulés des Réglages** passaient à la ligne (« Primes de /
  rappel ») pour faire place à leur sous-titre. Celui-ci passe dessous.

Ce qui est ajouté, et qui s'éteint sous `prefers-reduced-motion` :

- **l'entrée d'un onglet** : la vue monte de 6 px en s'éclairant, en
  0,22 s ;
- **le geste qui répond** : onglets et boutons s'enfoncent sous le doigt,
  et l'icône de l'onglet choisi se soulève d'un cran ;
- **feuilleter les journées du doigt** : un glissement horizontal sur le
  tableau des équipes du jour change de jour, comme les flèches, et le
  tableau arrive du côté où l'on va. Il faut un geste franc (60 px, 1,8
  fois plus large que haut, moins de 0,7 s) pour ne jamais voler un
  défilement vertical. Si le tableau défile lui-même de côté, le geste lui
  revient. Éprouvé : un glissement court ou en biais ne change rien.

Rien ne bouge dans la lecture : les quatre sorties du vérificateur sont
identiques à l'octet, et `comparer-fiches` passe son épreuve. Vérifié à
320 (hors ligne), 390 et 1280 px, en clair et en sombre.

**Et feuilleter les MOIS du doigt.** Le client, le 09/10/2026 : « le swipe
gauche droite pour la sélection de mois doit être actif sur les autres
onglets aussi ». Partout où le sélecteur de mois est rangé — Calendrier et
Salaire —, le même geste franc change de mois (gauche : le suivant, droite :
le précédent, comme ‹ ›), avec la même animation que le jour. Jamais sur un
champ de saisie ni dans un bloc qui défile de côté — **sauf le champ
invisible posé sur l'étiquette du mois** (`#moisPick`) : la première
version l'excluait comme tout champ, et le geste ne prenait pas sur la barre
du mois, l'endroit le plus naturel pour feuilleter. Un appui l'ouvre
toujours ; seul un glissement de 60 px change de mois. Éprouvé à 320 (hors
ligne), 390 et 1280 px, sur la barre du mois et au milieu du contenu :
glissement franc dans les deux sens, court et en biais sans effet.

**Les cadres restent en place.** Le client, le 09/10/2026 : « pourquoi lors
du swipe les cadres ont l'air de se déplacer au lieu de rester à leur
place ? ». L'animation s'appliquait à tout le panneau, cartes comprises.
Elle ne s'applique plus qu'au contenu des cartes, hors barre du mois, et la
carte rogne ce contenu le temps du glissement (`overflow:clip`, retiré après
260 ms). Mesuré au toucher simulé, à 320 px (hors ligne) et à 390 px :
pendant l'animation, la carte ne bouge pas d'un pixel, la barre du mois
reste fixe et le contenu glisse de 13 à 16 px.

**Et les flèches répondent aux appuis rapides.** Le client, le 09/10/2026 :
« les flèches gauche/droite des mois sur mobile ne réagissent pas si l'on
veut passer les mois rapidement ». La garde anti-zoom au double-tap annulait
toute 2e tape à moins de 320 ms au même endroit — c'est exactement appuyer
vite sur la même flèche — et chaque tape annulée relançait le délai :
mesuré au toucher simulé, **quatre appuis rapides sur › avançaient d'un
mois**, et les flèches du jour de l'onglet Horaire d'un jour. La garde ne
s'applique plus aux boutons, liens, champs et onglets, qui ne zooment pas
(`touch-action:manipulation`) ; elle reste ailleurs. Quatre appuis = quatre
mois et quatre jours, dans les deux sens, à 320 (hors ligne) et 390 px.

### Le menu du bas, à la BETSFIX

Le client, le 09/10/2026 : « un menu identique à celui du GitHub BETSFIX
dans le bas de page et PWA ». Recopié de la feuille de `CronoBots/BETSFIX`
(`app/web.py`, `.botnav` sous 1000 px), sous 760 px : une capsule
flottante en pilule, à 16 px du bas et des côtés (safe area en plus), fond
`rgba(24,27,36,.9)` sans flou, filet clair, ombre portée ; icônes seules
de 25 px au trait 1,9, grises au repos ; l'onglet ouvert en pilule teintée
de l'accent avec un filet, icône grossie d'un dixième. Seul l'accent
diffère : le cyan de la marque au lieu du bleu de BETSFIX. **Pas de
`backdrop-filter`, `transform` ni `will-change` sur la barre fixe** : sous
iOS ils cassent le `position:fixed` (leçon de BETSFIX). L'onglet Horaire
perd sa plaque cyan du 06/10 : tous les onglets se traitent pareil. Les
libellés restent lus par les lecteurs d'écran. Le bas de page, la bulle et
le bouton de retour en haut se décalent au-dessus de la capsule. Le bureau
ne change pas. Mesuré à 320 (hors ligne) et 390 px : 16 px des trois bords,
51 px de haut, sept onglets égaux, rien ne déborde.

**L'onglet Horaire passait sous la capsule**, et c'est le client qui l'a
vu sur son iPhone. Son tableau remplit l'écran au-dessus de la barre, et
`ajusterHauteurJour()` lui réservait la HAUTEUR de la barre (`--jnav`) :
juste tant qu'elle touchait le bas, faux depuis qu'elle flotte à 16 px
plus la zone d'accueil. On mesure désormais du haut de la barre au bas de
l'écran. Mesuré : 16 px entre le cadre et la capsule, à 320 (hors ligne)
et 390 px.

**En PWA, la capsule descend dans la zone d'accueil, comme celle de
Strava.** Le client, le 09/10/2026, deux captures côte à côte : « bonne
sur navigateur », mais plus haute que Strava une fois installée. Elle se
posait à 16 px AU-DESSUS de la zone d'accueil de l'iPhone (34 px), donc à
50 px du bas ; Strava se pose à cheval sur cette zone. `--navbas` vaut
`max(16px, zone d'accueil − 16px)` : 16 px dans le navigateur, où la zone
vaut 0, inchangé ; 18 px sur l'écran d'accueil. Le bas de page, la bulle
et le bouton de retour en haut suivent la même variable. Chromium n'a pas
de zone d'accueil : mesuré 16 px à 320 (hors ligne) et 390 px, et la
formule rend 18 px avec 34 px ; seul l'iPhone du client dit le reste.
Puis, le même jour : « c'est mieux mais un rien plus haute » — zone
d'accueil − 12 px, soit **22 px** du bas sur l'iPhone ; le navigateur ne
bouge pas.

**Plus haute** (le client, le 09/10/2026 : « tu peux augmenter la hauteur
de la barre de menus ») : 61 px au lieu de 51 (boutons de 11 px de marge
verticale, capsule de 6 px), l'onglet ouvert en pilule de 20 px de rayon ;
le bas de page, la bulle et le bouton de retour en haut remontent de
10 px. Mesuré à 320 (hors ligne) et 390 px : 16 px des trois bords, et le
cadre du Planning toujours à 16 px de la capsule.

### « Votre horaire a changé » : dans l'application, et sur le téléphone

Le client, le 09/10/2026 : « des notifications pour l'opérateur connecté,
en cas de changement d'horaire, de poste ; il faut que cela soit
professionnel », puis « go pour 1 et 2 » (dans l'application, et une
notification du téléphone à l'ouverture). Le niveau 3 — une notification
application fermée — demanderait un serveur d'envoi et une liste
d'appareils abonnés hors du téléphone : écarté pour l'instant, c'est sa
décision. Le client a demandé pourquoi BETSFIX notifie écran verrouillé :
son serveur Python garde les abonnements (`pushManager.subscribe`, clé
VAPID) et envoie par `pywebpush` au service d'Apple, qui réveille le
service worker. Ici, il faudrait un service d'abonnements (une
fonction Supabase suffirait), une action GitHub qui compare l'horaire à
chaque classeur et envoie, et deux secrets. Réponse le 09/10/2026 : « ne
rien faire pour ça maintenant ».

**Il n'y a pas de serveur** : l'horaire change quand un classeur est
installé, et l'application le découvre en s'ouvrant (le nouveau `V` vide
les caches, l'horaire neuf arrive).

- **L'instantané** (`notif/vu/<id>/<année>`) : pour chaque journée
  d'aujourd'hui à la fin de l'horaire, ce que la cellule dit —
  `descJourNotif()` : la pause, l'atelier ÉCRIT dans la cellule
  (`posteEcrit`), le code de journée, le congé, « rappel ». Une absence
  d'une journée entière se dit seule (« Maladie », pas « AM · MAL »). Le
  poste vient de la cellule de la personne, jamais du rééquilibrage : on
  annonce SON horaire, pas un placement déduit des absences des autres.
- **La comparaison** (`detecterChangements()`) : une journée dont la
  lecture a changé entre dans l'attente (`notif/attente/…`) avec son AVANT ;
  elle y reste jusqu'au bouton « Vu » ou jusqu'à ce que la date passe. La
  première fois, on photographie sans rien signaler ; le passé ne compte
  pas ; un commentaire qui change sans changer la lecture non plus.
- **La carte** sous le héros : liseré cyan (un changement n'est pas une
  faute), « Votre horaire a changé · n journées modifiées · classeur du… »,
  puis une ligne par série — **les journées qui se suivent et changent
  pareil n'en font qu'une** (`groupesNotif()`) : « Du lundi 12 octobre au
  dimanche 22 novembre · 42 j → Maladie ». L'avant barré ne s'écrit que
  s'il est le même pour toute la série. Cinq lignes, le reste se déplie.
  Une ligne ouvre son mois. Un point cyan sur l'onglet Accueil (`#notifDot`).
- **Le téléphone** : Réglages → Mon compte → « Notifications du
  téléphone », Activer / Désactiver (`ui/notifTel`). La permission n'est
  demandée qu'à ce clic. `showNotification()` par le service worker — la
  seule voie d'iOS, et seulement pour l'app installée sur l'écran
  d'accueil (le réglage le dit sur un iPhone qui ne l'est pas). Une
  notification par ouverture, seulement pour les journées NOUVELLEMENT
  changées, même étiquette pour remplacer la précédente ; la toucher ramène
  l'app (`notificationclick` dans `sw.js`).

**Éprouvé sur un vrai changement** : instantané pris sur le classeur du
01/10, puis celui du 09/10 servi à sa place. YBT : 65 journées, d'abord
65 lignes « AM → AM · MAL » — d'où le regroupement et le libellé seul de
l'absence ; ensuite « Du lundi 12 octobre au dimanche 22 novembre · 42 j →
Maladie » et quatre lignes. VBN : deux journées. Chromium sans écran répond
toujours « refusé » aux notifications : l'épreuve simule l'autorisation et
enregistre ce que `showNotification()` reçoit — une à l'activation, une au
changement, aucune au rechargement suivant. Vérificateur identique à
l'octet ; rien ne déborde à 320 (hors ligne), 390 et 1280 px. **Seul
l'iPhone du client dira si la notification s'affiche** une fois l'app
installée.

### Le bouton de retour en haut

Le client, le 30/09/2026 : « un bouton pour remonter dans le haut de page,
en bas à droite, avec une opacité quand il n'est pas pointé ». `#enHaut`,
rond de 44 px sur `--marque`, flèche blanche : il n'apparaît qu'après
300 px de descente (en haut de page il n'a rien à faire), à 55 % d'opacité,
et passe à 100 % au survol, au clavier ou sous le doigt. Sur téléphone il
se pose au-dessus de la barre d'onglets (76 px du bas, safe area en plus),
au bureau à 20 px du coin. Le clic remonte en douceur, sauf sous
`prefers-reduced-motion`, et redéplie la barre du haut. Mesuré à 320 (hors
ligne), 390 et 1280 px : caché en haut, visible à 0,55 descendu, 1 au
survol, retour à 0 px après le clic.

Le 18/10/2026 (« optimise au max »), il ne se montrait plus qu'en
REMONTANT et s'effaçait 2,2 s après, parce qu'il couvrait la valeur de
droite des rangées. Le client, le 19/10/2026 : « il apparaît quand on
remonte mais n'est pas visible quand on descend ; il devrait toujours être
visible quand on n'est pas en haut de page ». Il l'est désormais dès
200 px, dans les deux sens, sans s'effacer ; l'opacité de 0,55 reste
(`nfdm-v832`). Mesuré à 390 et 1280 px : caché en haut et à 150 px,
visible à 800 et 1 600 px en descendant, encore visible trois secondes
après, et après une remontée ; caché après le clic, la page en haut.

### La déconnexion se confirme dans une fenêtre de l'application

Le client, le 09/10/2026 : « il faut un message de déconnexion plus
professionnel ». `confirm()` ouvrait la boîte du SYSTÈME : l'adresse du site
en titre, les boutons et la police du téléphone, au milieu d'une
application qui a tout le reste à sa marque. `confirmerPro()` pose la même
carte que les autres fenêtres (fond voilé, carte arrondie) : une icône, le
titre « Se déconnecter ? », le compte en pastille (le trigramme, ou BWZ RH),
une phrase qui dit ce qui se passe — le compte n'est plus lié à l'appareil,
les mois et les réglages restent —, puis Annuler et Se déconnecter. Le focus
va sur Annuler, pour qu'un Entrée réflexe ne déconnecte personne ; Échap et
le fond referment. Elle resservira pour les autres confirmations (vider un
mois, une année), qui passent encore par `confirm()`. Éprouvé à 320 (hors
ligne), 390 et 1280 px : aucune boîte du système, Échap et Annuler gardent
le compte, Se déconnecter le retire et rouvre l'écran de connexion.

### « Qui je suis » ne se montre plus à un employé connecté

Le client, le 09/10/2026, capture des Réglages : « c'est pas redondant ces
2 sections ? ». Ça l'était. Pour un employé, « Mon compte » donnait le
trigramme, la fonction et un bouton de déconnexion, et « Qui je suis »
répétait la même phrase avec un second bouton qui faisait la même chose.
Le cadre « Qui je suis » (`#quiFold`) est donc caché pour un compte
employé ; son texte en double et `#btnChangerCompte` sont supprimés. Il
reste affiché pour BWZ RH (le sélecteur sert à choisir l'horaire à
afficher) et quand personne n'est connecté. `#prefillId` reste dans la
page, caché : le pré-remplissage continue de le lire (VBN rempli, salaire
calculé). Le vérificateur donne des sorties identiques à l'octet. Vérifié
à 320 px (hors ligne), 390 px et 1280 px pour l'employé, et à 390 px pour
le RH, sans aucune erreur.

### Les compteurs du Calendrier, sans défilement de côté

Le client, le 09/10/2026 : « optimiser l'onglet calendrier avec les mêmes
styles que les onglets horaire/équipe, surtout ne pas devoir faire de
scroll horizontal dans les cadres, et que les compteurs soient
professionnels et intuitifs ». Mesuré avant le changement à 390 px : les deux
tableaux de l'état des compteurs (congés, flex time) faisaient 430 px de
large dans un cadre de 322 px, d'où un défilement de côté. Les phrases
d'explication faisaient aussi plus de la moitié du cadre.
`renderCompteurs()` dessine maintenant un bloc par sujet, séparés par des
filets `--cadre` :

- **Congés** : sur chaque rangée, le nom, ce qui RESTE en grand et une
  barre « posé / droit de l'année ». Le restant devient rouge s'il est
  négatif. Deux colonnes au bureau.
- **Flex time** : le solde du jour en grand, avec son état. Une jauge de
  −8 h à 104 h, le seuil de 80 h marqué. Quatre chiffres dans la bande de
  `.calstats` (portées, reprises, total du classeur). La comparaison
  au pied du classeur tient en une ligne, et elle ne passe au rouge que
  s'il y a un écart.
- **Récupération d'heures sup., temps réduit, congés et maladie** : des
  rangées libellé / valeur. MAL et FORM sont écrits en toutes lettres
  (`LIB_CPT_LONG`), car la légende du classeur ne les définit pas.
- **Polyvalence** : une puce par atelier.

Les cadres de l'onglet (les codes, les compteurs) prennent la bordure, le
rayon et le relief de `#calCard`. Les styles `.cpt-tab` et `.cpt-tuiles`
sont retirés. `compteursCalcules()` n'a pas changé : les quatre sorties du
vérificateur sont identiques à l'octet. Mesuré à 320 px (hors ligne),
390 px et 1280 px : aucun bloc ne défile de côté et rien ne dépasse de la
page. Le cadre passe de 1 718 à 1 359 px de haut à 390 px.

Puis, le même jour : « j'aime bcp l'évolution ; par contre le nombre de
rappels et le montant ne se mettent pas bien ; les heures du bas aussi en
jours (8 h) ; les badges de poste optimisés ». Trois retouches :

- la case Rappels écrivait le montant collé au nombre (« 1 95,04 € » se
  lisait comme un seul nombre). Le montant passe sous l'étiquette, en petit
  (`.cstat-m`) ;
- « Congés et maladie de l'année » donne les jours de 8 h en gras et les
  heures à côté, plus discrètes (`hj()`) : 26 j · 208 h ;
- les ateliers de polyvalence sont des badges compacts en grille de colonnes
  égales, chacun avec un point à la couleur de sa zone (celle du liseré du
  tableau du jour, lue dans `POSTES_TRAVAIL`). Cinq ateliers tiennent en deux
  rangées alignées à 390 px.

Les sorties du vérificateur sont identiques à l'octet. Rien ne défile de
côté ni ne dépasse de la page à 320 px (hors ligne), 390 px et 1280 px.

Et encore le même jour : « il faut que cela soit logique, donc le nombre
disponible, le nombre placé, le nombre restant, et afficher VA avant
l'intitulé complet ». Chaque congé porte d'abord son code en badge
(`.cpt-code`, largeur fixe pour que les intitulés s'alignent), puis
l'intitulé, puis trois colonnes : **Disponible** (le solde au 1er janvier,
2025 inclus), **Placé** (posé dans l'horaire), **Restant** (en avant, à
droite). La barre suit en dessous. La liste « Congés et maladie de
l'année » prend le même badge devant l'intitulé. DTT, que la légende du
classeur ne définit pas, s'écrit « Congé d'ancienneté », comme dans la
table des codes de `docs/regles-paie.md`. Le vérificateur donne des
sorties identiques à l'octet. Rien ne défile de côté à 320 px (hors
ligne), 390 px et 1280 px.

Puis : « restant peut être exprimé en jour aussi ». Sous les heures du
restant, les jours de 8 h en petit (« 12 h » puis « 1,5 j »), rouges
quand le restant est négatif. Vérifié à 320 px (hors ligne), 390 px et
1280 px, sans débordement.

### Le relevé de prestations, comme celui reçu au travail

Le client, le 09/10/2026 : « que l'app reproduise une feuille de prestation
comme on reçoit au travail, afin de pouvoir directement comparer avec celle
que l'on reçoit ». Un cadre repliable « Relevé de prestations » se trouve
dans l'onglet Calendrier, sous le mois. `renderReleve()` le remplit à
chaque calcul. Il écrit chaque journée du mois avec les codes de la note
explicative du relevé mensuel (novembre 2025, dans le dépôt privé, résumée
dans `regles/notes-internes.md`) :

- **l'horaire** : 1A40, 2A40 et 3A40 pour les pauses, A21 pour le D seul
  (7h-15h), 4A60 et TP pour le crédit-temps et le temps partiel, Y90 pour
  un week-end sans prestation ;
- **les prestations**, « P » + le jour (1, 3, 5, 8 pour un férié) + la
  pause (0 à 3), sur la prime PAYÉE ;
- **les heures sup** en « U » sur le même schéma, plus F0, J84 (rappel),
  J83, A87 et Z93 ;
- **les absences par leur numéro** : 75, 58, 54, 47, 50, 60, 4, 23, 79 ;
- **9063** pour le chèque du jour ;
- **au bas**, les totaux par code, 454 (chèques du mois, `crNb`), A10
  (jours prestés), 290 (déplacements) et A! (vélo).

Les valeurs sont en centièmes d'heure, comme sur le relevé. **Ce qui n'y
est pas, et pourquoi** : les pointages IN/OUT, que l'application ne connaît
pas ; le REP/FREE et le Z03 d'un repos de semaine, que le classeur ne
distingue pas d'un repos ordinaire ; les soldes de contingents du bas de
page. Rien n'est recalculé : la fonction relit les journées du mois comme
`compute()` les paie. Le vérificateur donne des sorties identiques à
l'octet. Vérifié sur septembre de VBN à 320 px (hors ligne), 390 px et
1280 px : 30 lignes, aucun débordement. Les totaux montrent déjà les deux
écarts connus de la fiche de septembre : la nuit du 30/09 (P13 6,00 au
lieu d'un code du matin) et l'heure sup du même jour (U33 1,00).

### Le changement d'heure

Le client, le 14/10/2026 : en octobre, ceux qui font la nuit du passage
reçoivent 1 h sup au compteur ; en mars, ils prestent 7 h et sont payés
8 h. Règle dans `docs/regles-paie.md`, « Le changement d'heure ». Codé
dans `lireJournee()` pour la nuit du samedi qui précède le dernier dimanche
d'octobre, calculée sur l'année lue — **la règle vaut chaque année** (le
client, le 14/10/2026), vérifiée sur 2027 projeté (AFA, « U43 1,00 » le
30/10/2027). En 2026, le 24/10 : **13 personnes**, +1 h chacune (`r.hc`,
prime N). Mars ne demande rien. Les cinq sorties du vérificateur sont
identiques à l'octet (règle de paie seulement), les agendas aussi ;
`--journee` imprime désormais les heures sup d'une journée. Vérifié au
relevé d'ATR (« U43 1,00 » le 24/10) à 320 px (hors ligne), 390 et
1280 px.

### Les états de présence SAP, confrontés jour par jour

Le client, le 14/10/2026 : sa responsable RH lui a ouvert ses « États de
présence » officiels (SAP), de janvier au 13/10/2026, « place-les dans le
git privé et commençons ensemble la vérification ». Ce sont des PDF
**texte**, pas des scans : horaire prévu (PRJ), codes de prestation et
d'absence avec leur durée, pointage IN/OUT, chèque-repas, puis la synthèse
du mois et les droits à l'absence. Rangés dans `CronoBots/groups-fiches`,
`releves/`, propriétés vidées (l'identifiant de connexion de l'émetteur),
avec leur extraction jour par jour sans l'en-tête personnel
(`releves/lire-etat-presence.py`, par la position des mots). Le portail en
propose aussi d'octobre à décembre 2025.

**La confrontation** : le « Relevé de prestations » de l'application
(`renderReleve()`), relevé au navigateur mois par mois pour VBN, contre
l'état SAP, code par code et jour par jour. Le flex time n'a pas de code
journalier chez SAP (il vit dans le compteur « BIOW flextime ») : F0 et 60
sont écartés de la comparaison. **285 journées, 263 identiques**. Les
heures prestées (codes P) du mois concordent à 2 h près ou mieux.
**Remesuré le 14/10/2026 au soir, après les corrections du jour : 276
identiques sur 285**, et les six primes de rappel (J84) tombent les mêmes
jours des deux côtés (leur durée dépend du taux horaire personnel, que le
profil de test ne porte pas). Les neuf restantes sont toutes des écarts
connus que le classeur n'écrit pas : 14/01 (1,5 h sup), 09/02 (0,5 h de
compensation), 08/03 (venu puis malade), 21 et 22/03 (heures sup du
shut-down payées, V au lieu de U), 04/04 (0,75 h sup), 02/07 et 10/09
(maladie sans certificat), 30/07 (arrivée tardive).

Trois défauts du relevé de l'application, corrigés (affichage seulement,
`compute()` n'est pas touché) :

- le RJF s'écrivait **50** : c'est **48** (« Jour férié choix libre ») ; la
  formation et la délégation syndicale (`FORM`) s'écrivent **68**
  (« Congé syndical ») ;
- un rappel sur un repos écrivait ses heures sup DEUX fois — une fois par
  `rec.rs`, une fois par son code « nH HS » : U31 16 au lieu de 8 le 02/10,
  U33 14 au lieu de 7 le 25/06 ;
- le chèque d'une journée entière de récupération (RTT, DTT, RHS, flex time
  repris) n'apparaissait pas dans la colonne 9063, alors que `crRecup` le
  paie au mois et que SAP le porte jour par jour.

Les 22 écarts restants, rangés :

- **la pause d'un remplacement partiel** : le 21/01, `["R-CM","2h +FT",
  "remplace GPS de 20h à 22h00'"]`, l'application lit PM 6 h ; SAP dit nuit
  8 h (pointé 19:20-06:05), les 2 h de 20 h à 22 h au flex time. **Tranché
  le 14/10/2026** (le client : « oui », pour tout le monde) : un
  remplacement « de A à 22h » épargné en +FT, quand la pause ne vient que
  du remplacé (d'après-midi), ouvre une NUIT — la personne est venue plus
  tôt. `lireJournee()` lit N, 8 h, les heures du remplacement au flex time.
  Une seule journée de l'année ; `--placement --tout` ne change que le
  21/01 (CM PM 2/1 → 1/1, CM N 0/1 → 1/1), les autres sorties sont
  identiques à l'octet ; relevé de janvier « 3A40 · P13 8,00 · F0 2,00 »,
  comme SAP. Le 05/03,
  « remplace GPS arrivée à 15h00' », l'application lisait AM ; SAP dit PM
  7 h + 1 h de RTT (pointé 15:16-22:00). **Tranché le 14/10/2026** (le
  client : « je faisais PM », arrivé pour la remise de 15 h 30, 1 h RTT et
  1 h -FT posées toutes deux) : quand la pause ne vient que du remplacé et
  que le commentaire écrit « arrivée à H » hors de cette pause, la pause
  est celle qui contient H — sauf si le commentaire écrit aussi une plage
  (VGG le 10/06, « de 22h à 23h … Arrivée à 08h », plusieurs morceaux, non
  touché). Une seule journée ; `--placement --tout` ne change que le 05/03
  (CM AM 2/1 → 1/1, CM PM 0/1 → 1/1). Relevé de mars : « 2A40 · P12 7,00 ·
  58 1,00 · 60 1,00 », comme SAP pour la pause, les heures et le RTT. Le
  −FT reste compté (le client l'a posé) ; SAP n'écrit aucun mouvement de
  flex time ce jour-là ;
- **les heures sup du week-end sont des « V »** (Overtime 187,5 % / 200 %),
  pas des « U » : 21 et 22/03 (V42, V52 : la PAUSE des 4 h est l'après-midi,
  18 h-22 h, et non la nuit), 04/04 (V43 0,75). Ce sont exactement les
  « pas compenser » des fiches de mars et d'avril, et l'unique « à
  compenser » de janvier est l'U30 du 14/01, un mercredi. **Répondu le
  14/10/2026** : pendant le shut-down 2026, l'inspection sociale a autorisé
  les heures sup « HS SD 2026 », et un formulaire RH laissait chacun choisir
  de les faire payer à la fin du mois ou de les récupérer ; le client a
  choisi le paiement (confirmé le 14/10/2026). En temps normal, elles vont toujours au
  compteur. Ce choix est écrit sur le formulaire, **pas dans le classeur** :
  c'est un écart connu, et l'application garde la règle ordinaire (« à
  compenser »). **La PAUSE de ces 4 h est tranchée le même jour** (le
  client : « oui », pour tout le monde) : quand une plage plus longue que la
  journée couvre une pause entière et déborde, les heures en plus prennent
  la prime de la pause où elles tombent — « 18h-6h » : 8 h de nuit et 4 h
  sup à la prime de l'après-midi ; « 6h-18h » : 8 h de matin et 4 h à
  l'après-midi. `parseHoraireEntry()` pose `hsp`. **180 journées** sur
  l'année (141 en après-midi, 26 au matin, 13 de nuit) ; les cinq sorties
  du vérificateur sont identiques à l'octet (règle de paie seulement), et
  `--journee` imprime désormais « prime des HS ». Relevé de mars : U42 et
  U52 les 21 et 22/03, la pause de SAP ;
- **un même congé écrit deux fois** : le 30/01 porte « 4h RTT », et le 04/02
  « 4h -FT pris le 30.01 » ; le 05/03 porte « 1h -FT », et le 01/03 « 1h RTT
  pris le 05.03 ». **Répondu le 14/10/2026, et il n'y avait pas
  d'écart** : le client a posé les DEUX congés chaque fois (« le 30/01
  j'étais en congé en combinant 4h -FT et 4h RTT, je n'ai pas travaillé »).
  Le renvoi du 04/02 pose bien le −FT sur le 30/01, et le relevé de
  l'application écrit « P12 4,00 · 58 4,00 · 60 4,00 · chèque 1 », SAP
  « P12 4 · 58 4 · chèque 1 » : les 4 h de flex time repris, payées depuis
  le compteur, sont la « prestation » P12 de SAP, qui n'a pas de code
  journalier pour le flex time (le 60 est écarté de la comparaison). Le
  05/03 de même. Je l'avais rangé parmi les écarts sur la seule colonne 60.
  Rien n'a changé dans le code ;
- **le chèque d'un jour de délégation** (12/02, « DS à l'extérieur ») : SAP
  le donne, l'application non. **Tranché le 14/10/2026** (le client :
  « oui », pour tout le monde) : une journée entière de congé syndical (DS,
  code FORM d'une journée) donne le chèque-repas, à la fiche comme au relevé
  (`jourSyndicalEntier()`). **37 journées chez 12 personnes** (JKS 13,
  LHR 11, FLI 3…) ; les cinq sorties du vérificateur identiques à l'octet
  (règle de paie seulement) ; relevé de février « 68 8,00 · chèque 1 »,
  comme SAP, à 320 px (hors ligne), 390 et 1280 px ;
- **le rappel sur un repos payé** (REP, 25/06) : SAP ne porte aucune heure
  sup, seulement le déplacement, comme la fiche. **Ce n'était pas une
  question à poser** (14/10/2026) : la réponse est dans le classeur. VBN
  porte `["23-06h","R-CM","Remplace ATA Rappel le 25/06"]`, et le
  lendemain `["-","7h +FT"]`, seul, sans date ni commentaire. Une nuit
  finit le matin du jour suivant, et c'est sur cette case que l'épargne
  est écrite. L'application payait les 7 h en heures sup ET les comptait
  au flex time le 26/06, soit deux fois. `lireJournee()` ne pose plus
  d'heure sup sur une nuit de rappel sur un repos quand le lendemain est
  un repos qui ne porte que « n h +FT », pour le même nombre d'heures. Sur
  les 62 repos de l'année qui portent « n h +FT », c'est la seule journée
  de cette forme ; les autres écrivent une date (« presté le », « cf »),
  déjà rattachée à son jour. SKS le 13/04, `["10h-22h","8h +FT","rappel le
  09.04"]` puis le 14/04 `["-","4h +FT","rappel le 13.04"]`, n'est pas
  touché : plage de jour, commentaire, ni fiche ni relevé pour trancher.
  **Et la prime de rappel manquait** sur cette nuit, ainsi que sur 13
  autres rappels sur un repos du cycle dont la cellule écrit la pause
  faite. `rappelDuJour()` recevait cette pause comme « poste prévu », et
  la prestation ne débordait pas d'elle-même. Ces journées sont : JBI les
  15/01, 22 et 23/08 ; VGG le 10/05 ; PDF le 18/06 ; JKS les 23/01 et
  02/05 ; LAA le 21/08 ; JBA le 13/08 ; PAM les 14/01, 20 et 21/06 ; SPS
  le 21/01. Un rappel lu sur un repos (`r.rs`) a désormais le repos pour
  poste prévu, comme le veut la procédure (« rappel d'un repos, repos
  maintenu »), et la fiche de juin le confirme : ses 13 h 16 de
  déplacement sont les deux rappels des 11 et 25/06. VGG le 26/05
  (« Rappel le 25/06 », date postérieure) reste sans prime. Relevé de
  juin : « 3A40 · J84 », sans U ni chèque, comme SAP. Les cinq sorties du
  vérificateur et les agendas sont identiques à l'octet (la paie seule
  change) ; vérifié à 320 px (hors ligne), 390 et 1280 px ;
- **le 30/09** confirme la fiche : prime du matin pour les 6 h (P11) et
  0,5 h sup de jour (U30). **Tranché le 14/10/2026.** Le client : « oui,
  je pensais déjà avoir répondu à cette question pour un CPPT » (le 30/09 :
  « la prime qui est bien indiquée dans le commentaire »). Je n'avais pas
  relié sa réponse à cette journée, où le commentaire n'écrit pas de
  prime mais écrit les heures. Une journée à code de jour (CPPT, DS-CE…)
  dont le commentaire écrit l'arrivée et le départ prend la prime de la
  pause où tombent ces heures : 9 h-15 h donne le matin, quand le cycle
  prévoyait une nuit (la semaine était passée en matin par échanges ; SAP
  planifie 1A40). C'est la seule journée de l'année de cette forme. L'heure
  sup passe à 0,5 h sans prime (`HS_DUREE_TRANCHEE`, décision du client
  pour cette journée), alors que le classeur écrit « +1h ». Relevé de
  septembre : « 1A40 · P11 6,00 · 58 2,00 · U30 0,50 · chèque 1 »,
  identique à SAP. Les cinq sorties du vérificateur et les agendas sont
  identiques à l'octet ; vérifié à 320 px (hors ligne), 390 et 1280 px ;
- **la durée des heures de déplacement** (J84 : 6,29, 4,98, 6,28, 6,63,
  4,6 h) contre le réglage fixe de l'application. **Résolu le 14/10/2026,
  sans question.** SAP et la fiche expriment la prime de rappel en heures
  au taux horaire : 2 h × (coefficient du jour + prime de pause ×
  coefficient de pause ÷ taux) × coefficient du moment. Le relevé de
  l'application écrivait seulement 2 h × le coefficient du moment (3 ou
  4 h). Le calcul tombe juste sur les six dates, à une condition : **la
  prime de pause est celle des heures ajoutées**. Les nuits de 12 h des
  19/02 et 14/04 (« 18h-06h », rappel pour 18 h-22 h) prennent la prime
  de l'après-midi : 6 h 17 sur les fiches, 6,29 et 6,28 h chez SAP. La
  prime de nuit aurait donné 6,64 h. LCI le 20/03, même forme, le
  confirme : 6 h 25 sur sa fiche avec l'après-midi au taux de début
  d'année, alors que la nuit donnait les 183,37 € de l'application au
  lieu de 170,44 €. `parseHoraireEntry()` pose `rpp`, la pause de
  l'excédent, dès que la plage déborde de la journée, que les heures en
  plus soient payées, épargnées ou reportées ; `hsp` en reprend la valeur
  quand elles sont payées. `compute()` paie la prime de rappel à
  `rpp || hsp || s`, la fiche simulée écrit les heures de déplacement en
  montant ÷ taux (VBN en juin : 13 h 16, comme la fiche), et le relevé
  écrit la même durée en J84. 230 journées de rappel de l'année ont une
  plage qui déborde ; leur prime suit désormais cette règle. Les cinq
  sorties du vérificateur et les agendas sont identiques à l'octet ;
  `--journee` imprime « pause des heures en plus » ;
- **ce que le classeur n'écrit pas** : 1,5 h sup le 14/01 (formation
  jusqu'à 16 h 15), 0,5 h de compensation le 09/02, venu puis malade le
  08/03 (salaire garanti 5,72 h et 2,28 h prestées), 0,75 h sup le 04/04,
  arrivée tardive de 0,25 h le 30/07, maladie sans certificat (code 15)
  les 02/07 et 10/09 — écarts connus ;
- **le DTT** se décompte en « Congé d'ancienneté » (56) en semaine et en
  « VCP » (47) le week-end (17 au 21/07) ; le relevé de l'application
  écrivait 47 partout. **Corrigé le 14/10/2026** (affichage seulement) :
  56 du lundi au vendredi, 47 le samedi et le dimanche. Les cinq journées
  concordent, le férié du 21/07 compris (SAP y écrit 56) ;
- **le chèque du 02/10** (rappel un vendredi de repos, 8 h sup au matin) :
  SAP n'en donne pas, l'application oui. **Tranché le 14/10/2026 par les
  documents, sans réponse du client** (« je ne sais pas, tu n'as pas cette
  information dans les documents ? ») : je lui avais posé la question
  sans avoir relu ses propres envois. La note sur les repos de la grille
  le dit (« les chèques-repas sont attribués lors des jours de
  prestations »), et les quatre cas connus concordent. Sur la fiche
  d'avril de LCI, il y a 10 jours d'heures normales et 9 chèques ; les 11
  et 13/04, journées entières en heures sup, n'ont pas de chèque. Les
  états SAP de VBN n'en donnent ni le 25/06 ni le 02/10. Un rappel sur
  un repos (`r.rs`) ne donne donc plus de chèque, ni à la fiche
  (`compute()`), ni au relevé. L'indemnité de déplacement reste due : la
  fiche d'avril de LCI en compte 12 jours, ces deux-là compris. Les cinq
  sorties du vérificateur sont identiques à l'octet (la règle est de paie
  seulement). Le relevé d'octobre de VBN laisse la colonne 9063 vide le
  02/10, à 320 px (hors ligne), 390 et 1280 px.

### L'Accueil fondu dans le Calendrier

Le client, le 09/10/2026 : « que penses-tu de combiner l'onglet calendrier
avec l'accueil étant donné que les deux sont personnels au profil ? », puis
« go, et fais cela de la manière la plus professionnelle possible ». Les deux
onglets parlaient de la même personne : l'Accueil montrait son profil et son
année, le Calendrier son mois. **Sept onglets deviennent six** ; l'onglet
garde le nom « Calendrier », « Mon horaire » ayant été écarté parce qu'il
se serait lu à côté de l'onglet « Horaire » de l'équipe.

L'onglet se lit de haut en bas : la tête du profil (trigramme, fonction,
statut et binôme sur la ligne du dessous), le mois, l'état des compteurs,
« Mon rythme » (répartition des pauses, nuits et week-ends comparés à
l'équipe, l'année jour par jour, congés restants), le relevé de
prestations, puis les codes. Ce qui était dit deux fois est parti : la
ligne « Rôle » des faits (le binôme est dans la tête), et les puces de
polyvalence des compteurs, qui ne s'affichent plus que si « Mon rythme »
ne les porte pas.

**L'année jour par jour défilait de côté** : 740 px de grille, semaines en
colonnes. Elle est redessinée en douze rangées d'un mois sur trente et une
colonnes, cases carrées de 14 px au plus, la case du jour cerclée : elle
tient à 320 px. `VUES_MIGREES` envoie `resume` vers `horaire`, si bien
qu'un appareil qui avait l'Accueil ouvert retrouve le Calendrier, et c'est
la vue par défaut. Le glissement du mois n'anime que la carte du mois :
les compteurs et « Mon rythme » parlent de l'année et ne bougent pas.
Vérificateur identique à l'octet ; vérifié à 320 px (hors ligne), 390 px et
1280 px, sans débordement ni erreur. **Le tableau « Six onglets » plus bas
date du 22/09** : son Résumé a disparu depuis.

### Le héros de l'Accueil, et un menu nommé par son contenu

Le client, le 09/10/2026 : « il faut mieux présenter la personne connectée
dans le héros de la page d'accueil ; revois également tous les onglets du
menu pour mieux correspondre au contenu ».

**Le héros** (`_pfHead(db,p)`, dans `#rythmeTete`) est une carte à la
couleur de la marque : l'avatar au trigramme cerclé de cyan, « Bonjour /
Bonsoir » et le trigramme, la fonction en grand, puis des puces — binôme
ou équipe, poste attitré à la couleur de sa zone (« En formation ·
Meunerie » en jaune pour qui l'apprend), statut. Dessous, trois chiffres
de soi, lus là où le reste de l'onglet les lit : **congés à placer** (la
somme des « restant » VA, RTT, DTT, RJF de l'état des compteurs, en jours
de 8 h — « vacances restantes » seules valaient 0 pour presque tout le
monde, tout étant déjà posé), **flex time au jour de l'usine** (même
calcul et mêmes couleurs que la jauge), **polyvalences validées** (pas pour
un contremaître). Les « faits » qui suivaient la tête (`_pfFacts`) sont
partis : ils redisaient le poste et les polyvalences. Le poste du jour
n'y est pas : la barre du haut le dit déjà.

**Le menu**, dans l'ordre : **Accueil** (moi : profil, mois, compteurs,
rythme, relevé — « Calendrier » ne disait que le mois), **Salaire**,
**Planning** (les équipes d'un jour — « Horaire » se confondait avec
l'horaire personnel), **Effectifs** (sous-effectifs, congé, absence,
recherche, rappels non nécessaires — « RH » nommait un service, pas un
contenu), **Équipes** (composition, recyclage, statuts, annuaire),
**Réglages**. D'abord ce qui est à moi, puis l'usine du jour, puis sa
structure ; `VIEWS` suit. Les identifiants (`data-v`, `ui/view`) ne
changent pas. Icônes redessinées pour Accueil (maison et personne) et
Effectifs (personne et loupe). Deux phrases visibles renvoyaient encore à
« l'onglet Horaire » : corrigées. Vérificateur identique à l'octet ;
vérifié à 320 px (hors ligne), 390 px et 1280 px sur VBN, SKS, AFA et LCI,
sans débordement ni erreur.

### « Optimise tout » : six pistes, mesurées avant et après

Le client, le 09/10/2026, après une liste de six pistes : « optimise
tout ». Mesuré d'abord à 390 px sur VBN : Accueil 3 903 px, **Salaire
5 025**, Planning 745, **Effectifs 11 795** (quatorze écrans), Équipes
3 242.

- **Effectifs, un mois ouvert** : les sous-effectifs et les rappels non
  nécessaires se rangent par mois (`mqMoisTete()`), le mois qui vient
  ouvert, les suivants repliés sur leur intertitre, qui garde son compte et
  s'ouvre d'un appui (`mqBascule()`, retenu dans `MQ_OUVERT` le temps de la
  page). Au-dessus, une rangée de sauts (`.rhsauts`) — Demande (partie
  depuis avec la fenêtre de recherche), Sous-effectif avec son compte,
  rappels, absents — mène droit à chaque
  cadre, sous la barre du haut. **11 795 → 3 848 px.**
- **Salaire, replis qui se souviennent** : « Vérifier sa fiche en quatre
  temps », la fiche simulée et le contrôle sont des `details.fold
  data-memo`, fermés par défaut, leur état retenu par appareil
  (`ui/fold/<id>`). Le net à recevoir reste sous la fiche repliée, le
  statut du contrôle dans son intitulé ; l'impression déplie tout et
  remet comme avant. **5 025 → 1 996 px.** Le contrôle ne déborde plus à
  320 px (marges, champ et pastille resserrés sous 380 px).
- **Le mois d'avant** : sous le net, « −279,88 € par rapport à
  septembre », et la ligne de fiche qui a le plus bougé
  (`netMoisPrecedent()`, qui relit le mois enregistré par `compute()`
  lui-même, comme `hsDuMoisStocke()`). **Premier essai muet** : le mois
  d'avant n'était pas encore dans le stockage, `save()` attendant 700 ms ;
  `DERNIER_ECRIT` garde ce qui vient d'être écrit. Rien quand le mois
  d'avant est vide (janvier) ou que les deux nets sont égaux.
- **Le retour dans le héros** : « Absent jusqu'au 22 novembre », « En
  repos · reprise le 12 octobre », « En congé · reprise demain »
  (`_pfEtat()`, même lecture que les cadres Absents et Congé et repos :
  `equipeDuJour()`, `finAbsence()`). Rien un jour travaillé. Calculé
  30 ms APRÈS le premier affichage : `equipeDuJour()` rejoue toute l'usine
  (170 ms au processeur divisé par quatre), le héros n'a pas à l'attendre.
- **Les deux dernières boîtes du système** : « Vider ce mois » et
  « Effacer toute l'année » passent par `confirmerPro()`, Annuler au
  focus ; `viderAnnee()` sort de l'écouteur. Éprouvé : Échap referme sans
  rien toucher, la confirmation efface bien les douze mois.
- **Le chargement** : l'horaire est déjà compact (708 Ko, 108 compressés à
  l'envoi). Profilé au processeur divisé par quatre : 2,2 s jusqu'au
  héros, dont plus d'une seconde à lire le script lui-même ; la
  comparaison à l'équipe était déjà différée et mémoïsée. Seul le calcul du
  retour est différé ; découper `index.html` serait le vrai gain, et ce
  n'est pas un chantier d'une passe.

Vérificateur identique à l'octet (aucune lecture touchée), garde-fou du
dépôt à zéro ; vérifié à 320 px (hors ligne), 390 et 1280 px sur VBN, YBT,
LDY et SKS, sans débordement ni erreur.

### Mon salaire dans les cadres du Calendrier

Le client, le 09/10/2026 : « les cadres de l'onglet salaire doivent être
présentés comme pour le cadre horaire (sélection etc.) ». Le sélecteur de
mois flottait au-dessus des cartes ; il est désormais la première ligne du
premier cadre, `#salCard`, avec la barre `.calnav` / `.calmois` du
Calendrier (même `.mnavhote`, donc `placerMnav("salaire")`, le glissement
du mois et le masquage sans personne restent inchangés). Sous lui, le net,
puis les six chiffres du mois en cases bordées comme `.calstats` (valeur
mono 17 px, étiquette en petites capitales). Toutes les cartes de l'onglet
prennent la bordure `--cadre`, le rayon `--rj` et le relief de `#calCard`.
Aucune ligne de calcul touchée ; vérifié à 320 (hors ligne), 390 et
1280 px, flèches du mois comprises. **Reste, préexistant** : à 320 px le
tableau « Contrôle de la vraie fiche » est plus large que sa carte.

### L'écran d'intro

Le client, le 29/09/2026 : « un écran d'intro avec le logo au chargement de
la page ». `#intro` est dans le HTML, juste après `<body>` et avant tout
script : il se peint dès la première image, sur `--marque`, avec
`logo.svg` (déjà dans `CORE`, donc aussi hors ligne) et un trait de
lumière. `finIntro()` l'efface quand l'horaire est lu, jamais avant 0,9 s
ni après 3 s, puis le retire du document. **Le nom n'est pas écrit sous
le logo** : le dessin porte déjà « biowanze », et la première version le
disait deux fois. Sous `prefers-reduced-motion`, il reste un écran fixe.

**Et son fond sous toute l'application, en sombre.** Le client, le
29/09/2026 : « j'aime beaucoup le background de l'écran de chargement, je
voudrais le même à mon application ». Le même dégradé radial (#1b2640 au
centre, #111727 aux bords) vit dans un jeton `--fond`, posé sur un calque
fixe `body::before` — Safari sur iOS ignore `background-attachment:fixed`.
Thème sombre seulement : le clair garde sa page #F6F6F6, relevée sur les
captures du client, et `--fond` y vaut `none`. Les cartes (#212737) restent
au-dessus du fond le plus clair, et le texte posé sur la page tient : le
gris le plus pâle, `--faint`, lit à 4,8:1 sur #1b2640. Vérifié à 390 et
1280 px, en haut de page et défilé.

**Et le logo en filigrane.** Le client, le 30/09/2026 : « le logo doit
rester en fond fixe dans mon app en filigrane une fois l'écran de
chargement disparu ». `body::after`, calque fixe au-dessus du dégradé :
`logo.svg` centré, `min(56vw,300px)` de large, opacité `--filigrane`
(0,06). Thème sombre seulement : en clair le texte blanc du dessin
disparaît et il ne restait qu'un morceau de la marque, `--filigrane` y vaut
0. Les cartes passent par-dessus. Même commit : sans personne choisie, la
barre du haut écrit « Choisissez qui vous êtes / dans Réglages » sur deux
lignes — sur une seule, elle chevauchait BIOWANZE à 320 px. Vérifié à 320
(hors ligne), 390 et 1280 px.


### Une note écrite dans l'annotation se montre comme un commentaire (19/10/2026)

Le client : « les commentaires de JBI du 02/11 au 11/11 n'apparaissent pas,
car ils ont indiqué "Falling film" dans la case au lieu du commentaire ».
La journée se lisait juste (un D de 8 h, `MENTIONS_NEUTRES`) ; seul
l'affichage ne regardait que la colonne commentaire. `comAffiche(raw)`
rend le commentaire, ou, s'il n'y en a pas, une tâche écrite dans
l'annotation (`NOTES_ANNOTATION` : falling film, consignations,
« Polyvalence ») — jamais un code, une plage ni un atelier. Elle sert le
coin du calendrier, la vue semaine, la bulle des badges d'équipe et la
note de l'agenda. Mesuré : seules les 8 journées « Falling film » de JBI
changent dans `cal/` (une DESCRIPTION de plus chacune) ; vérificateur,
manques, polyvalences, compteurs et fiches VBN identiques. Navigateur :
novembre marque les 02-04 et 09-12, la semaine les affiche, hors ligne
sans erreur.

## Accueil, passe du 20/10/2026

Le client : « optimise l'accueil au max et propose des changements ».
Photographié à 320, 390 et 1280 px (hauteurs 3 067, 2 921, 2 910 px),
aucun débordement ni erreur mesurés. Défauts relevés et corrigés :
« 1 prestées » dans le cycle (accord), « 1,5 jours restants » (au-dessous
de deux, le singulier), « journées prestées » sans accord dans la barre de
l'année, « 75 % » sans dire de quoi (« 75 % fait »), la légende AM · PM ·
N · D dite trois fois dans la page (celle de « Mois par mois » retirée : le
« jour par jour » juste dessous et le calendrier la donnent). Vérifié et
NON fautif : « ▼ 56 vs sept. » compare bien deux mois entiers. Les
changements de structure (bureau sur deux colonnes, « jour par jour » qui
redit la vue Année du calendrier, explication du flex time, congés « tout
placés » regroupés) sont proposés au client, non faits.

**Suite, même jour** (`nfdm-v848`). Le client : « il faut tout
optimiser ». Faits : (1) au bureau (≥ 1100 px), calendrier et compteurs
côte à côte, les compteurs en une colonne de rangées — 2 910 → 2 412 px à
1280 ; (3) les congés « Tout placé » regroupés en une rangée « VA · DTT ·
RJF — Congés » ; une première version écrivait leurs noms en toutes
lettres, quatre lignes à 320 px, ramenée au seul mot « Congés » ; (4) le
report de l'an passé du flex time dit quand il n'est pas nul — total du
classeur − (+FT) − (−FT), de −8 h à +90 h selon les personnes en 2026 :
« +62 h portées · −55 h reprises · report 2025 −7 h » pour un solde de
0 h ; (5) au pied du héros, « Horaire 2027 · 7 jours de congé déjà posés ·
Voir janvier › », seulement quand le classeur de l'année suivante est reçu
(pas prolongé). (2) NON fait : replier « Jour par jour » — le client :
« mais j'aime bien jour par jour ». Éprouvé à 320, 390 et 1280 px : aucun
débordement, aucune erreur ; le lien ouvre janvier 2027, hors ligne compris.

## Planning : badges côte à côte, colonne D étroite, année, légende (20/10/2026)

Le client, capture du 21/10 : « comment optimiser les badges et la vue ? »,
puis « go » sur sept propositions. Faits (`nfdm-v853`) : au téléphone, les
badges (de même taille) se rangent DEUX par ligne au lieu de s'empiler ; la
colonne D prend 15 % de la largeur (53 px à 390, chaque pause 80 px) ;
l'année s'écrit dans le titre hors de l'année en cours (« Mardi 5 janvier
2027 ») ; une légende repliée sous le tableau, des seuls signes présents ce
jour-là, ouverte ou fermée d'un jour à l'autre. Mesuré à 320, 390 et
1280 px : le tableau du 20/10 tient dans l'écran (650 px), aucune case ne
déborde, aucune erreur.

NON faits, et redemandés : trois des sept propositions revenaient sur ses
propres décisions, que je n'avais pas relues avant de proposer — erreur de
méthode : le tiret des cases vides (voulu le 26/09), l'effectif sous la
pause (retiré le 26/09, « le total est déjà sous À l'usine »), l'horaire
dans le badge (contraire à l'uniformisation demandée le même jour).

**Suite, même jour** (`nfdm-v854`). Le client : « ne pas mettre de légende
à ce planning, mettre les horaires dans les badges, donc ceux avec l'horaire
peuvent être plus grands, même tous de la même taille ». La légende est
retirée (fonction et styles). Le cadre entoure de nouveau toute l'étiquette,
trigramme ET horaire en petit dessous, DANS le badge ; largeur commune
`3ch + 10px` (31 px au téléphone, 52 px au bureau), un badge à horaire plus
haut d'une ligne (31 × 28 contre 31 × 18). Une première largeur de 35 px
défaisait les deux badges par ligne (35 + 35 + marges > 80 px de pause) :
ramenée à 31. Le tiret des cases vides et l'effectif sous la pause restent
comme le client les avait voulus le 26/09.

**Grille de badges, puis plus de colonne D** (même jour, `nfdm-v855`).
Le client : « il y a moyen de mieux disposer les badges trigramme non ? » —
le badge seul d'une seconde ligne se centrait en pyramide (TCE VGG / SLI)
et un badge à horaire dépassait son voisin. Les badges d'une case vivent
désormais dans une grille (`.eqc`) : deux colonnes au téléphone, alignées
d'une ligne à l'autre, deux voisins à la même hauteur, un badge seul
centré. Une première version (`min-width:100%`) ramenait les badges à
27 px, sous la largeur commune ; corrigée (`justify-self:stretch`), 31 px.
Puis : « retirer la colonne D, mais au lieu de ça les mettre dans la
colonne AM avec l'horaire choisi ». Les gens en D rejoignent la case AM de
leur poste, la formation, le DS et « à déterminer » leurs lignes, leur
horaire dans le badge (`x.deD`), même sur les lignes Formation et DS où il
ne s'écrivait pas. Aucun compte ne bouge (vérificateur et manques
identiques) : la colonne D n'attendait personne. Le 21/10 : CKS « 7-15 » en
fermentation du matin, MMS « 7h30-16 » en formation, ATR, LCI, QBY « 7-15 »
en DS.

**Tous les badges à la même hauteur** (même jour, `nfdm-v858`). Le client :
« tous les badges de la même hauteur (la même que pour ceux avec horaire) ».
La hauteur est fixe, celle d'un badge à horaire : 28 px au téléphone, 43 au
bureau, le trigramme seul centré. Une hauteur seulement minimale laissait,
au bureau, des badges de 47 px : les cases à plusieurs lignes étiraient
chaque badge à la hauteur de sa rangée (`align-items:stretch`), remplacé
par un alignement en haut. Mesuré : une seule hauteur à 320, 390 et
1280 px, aucune case qui déborde.

**Badges agrandis, et qui peut combler une place vide** (même jour,
`nfdm-v859`). Le client choisit « 1 et 3 » parmi cinq propositions. (1) Au
téléphone, trigrammes à 13 px au lieu de 11,5, badges de 32 px de haut
(12 px et 30 px sous 361 px de large, où deux badges doivent tenir dans une
pause de 74 px) : mesuré 33 × 32 à 390, 32 × 30 à 320, toujours deux par
ligne, aucune case qui déborde. (3) Le « ? » d'une place vide s'ouvre au
toucher dans la bulle des commentaires (`candidatsPlace()`) : la place et
son compte, la proposition de l'application s'il y en a une, puis les
présents de la pause qui savent tenir le poste (peutTenir et
compteAuPoste, la même polyvalence que le rééquilibrage), ceux d'un poste
en surnombre d'abord. Le 21/10 : « Place vide · Terrain arrière AM (0/1) ·
Proposé : SMA · Peuvent le tenir : SMA (fermentation, en surnombre) · AAI
(distillation) ».

**La bulle d'une place vide, mise en forme** (même jour, `nfdm-v860`). Le
client : « supprime les mots place vide et optimise le rendu des
propositions ». La bulle n'est plus une phrase où le proposé revenait deux
fois : un titre (« Terrain arrière · AM · 0/1 »), puis un candidat par
ligne — son badge, pointillé orange pour la proposition, le poste qu'il
tient, « proposé » ou « en surnombre » — le proposé d'abord, puis le
surnombre (`bulleCandidatsHTML()`, données en `data-cand`). Une première
version nommait ses classes `cpt-…`, déjà prises par les compteurs : le
titre sortait en capitales. Renommées `cdp-…`.

**Un cran plus petits** (même jour, `nfdm-v861`). Le client : « sur mobile
les badges sont un rien trop grands ». 12,5 px et 30 px de haut au
téléphone (33 × 30 à 390), 12 px et 28 px sous 361 px (32 × 28 à 320) ;
bureau inchangé (52 × 43). Toujours une seule hauteur, deux par ligne,
aucune case qui déborde.

**De légers écarts entre les badges** (même jour, `nfdm-v862`). Le client :
« il faut de légers écarts entre les badges ». Grille à 4 px d'écart au
téléphone (2 avant), 6 px au bureau (4 avant). Deux badges et l'écart font
68 px à 320, dans une pause de 74 : toujours deux par ligne, aucune case
qui déborde.

**Qui tient le poste à gauche, qui s'y forme à droite** (même jour,
`nfdm-v863`). Le client : « les personnes qui ont le poste doivent être
prioritaires sur le côté gauche de la case par rapport aux personnes qui
sont en formation, qui doivent être placées à droite ». Quand une case
porte un opérateur en formation (la règle de l'étiquette jaune :
`enFormation` et pas `compteAuPoste`), elle se coupe en deux colonnes
(`.eqc.deux`) : à gauche ceux qui tiennent, les relais et les places vides,
à droite les apprentis ; sans apprenti, la grille ordinaire. Le 21/10 :
meunerie AM « LDY VGG | SKS SLI », gluten AM « DBE GBT SLT | NPI », chaudières
PM « KDN PDF | MGY ». Mesuré à 320, 390 et 1280 px : tailles inchangées,
aucune case qui déborde, aucune erreur.

**L'apprenti en bas à droite** (même jour, `nfdm-v864`). Le client, sur les
deux colonnes de la version précédente : « celui en formation doit être mis
en bas à droite ; s'ils sont 4, il faut qu'il y en ait un en poste au-dessus
de lui ». Retour à la grille remplie ligne par ligne, titulaires d'abord,
apprentis à la fin ; quand le compte est impair, une case vide (`.eqtrou`,
au téléphone seulement) précède les apprentis. Le 21/10 : gluten AM « DBE
GBT / SLT NPI », chaudières PM « KDN PDF / · MGY », meunerie « LDY VGG / SKS
SLI ».

**L'équipe de la pause à son horaire normal, d'abord** (même jour,
`nfdm-v865`). Le client : « prioritairement, ceux de gauche sont ceux de la
pause et de l'horaire normal, au lieu de ceux qui tiennent le poste mais
sont en décalé ». Parmi ceux qui tiennent, trois rangs, tri stable : 0
l'équipe que le cycle met à cette pause (« Shift N » contre
`equipeALaPause`), horaire normal ; 1 une autre équipe (échange,
remplaçant, renfort, adjoint) ; 2 un autre horaire (badge à horaire). Les
apprentis restent en bas à droite. Le 21/10 : gluten AM « GBT SLT / DBE
NPI » (DBE, équipe 2, en échange), fermentation AM « CHD SMA / CKS 7-15 »,
meunerie « LDY VGG / SKS SLI ».

**Le trou en haut à droite** (même jour, `nfdm-v866`). Le client, capture
du 20/10 (« TCE VGG / · SLI ») : « VGG et ATR devraient être à gauche
aussi ; il ne faut jamais laisser de trou en bas à gauche s'il y a d'autres
opérateurs hors formation ». La case vide se pose désormais juste après le
premier titulaire : meunerie AM « TCE · / VGG SLI », chaudières AM « PDF · /
ATR MGY ». L'apprenti reste en bas à droite, un titulaire au-dessus quand
ils sont quatre.

**Un seul apprenti, en haut à droite** (même jour, `nfdm-v867`). Le client :
« du coup, si un seul en formation, il doit être au-dessus à droite au lieu
d'en dessous ». Un seul apprenti et un compte impair : il prend la place du
trou, en haut à droite, les titulaires la colonne de gauche — meunerie AM
« TCE SLI / VGG », chaudières AM « PDF MGY / ATR ». Quatre badges : toujours
un titulaire au-dessus de l'apprenti, en bas à droite (gluten AM du 21/10
« DBE GBT / SLT NPI »). Plusieurs apprentis et un compte impair : le trou
reste en haut à droite.

**Le dernier badge d'un compte impair se centre, et une cellule « D »
annotée d'une plage garde son horaire (20/10/2026, `nfdm-v868`).** Le
client, sur la capture du 14/10 : « pourquoi ne voit-on pas l'horaire
presté par FLI, étant donné qu'il est en D ? », et « en cas de nombre
impair, les cadres du dernier opérateur doivent être toujours centrés
comme FPS ». FLI avait « D · 06h-14h » : la plage le range au matin, et le
badge n'y prenait l'horaire que pour une colonne D, une consignation ou un
`deD` — un 6-14 au matin est l'horaire du matin, `horaireModifie` se tait.
`celluleD(x)` ajoute ce cas, seulement quand l'annotation est une plage :
« D · AM » (16 jours sur les deux années) passe au matin à l'heure du
matin, et l'horaire habituel de journée y serait faux. Mesuré au 14/10 :
« FLI 6-14 ». Au téléphone (320 et 390 px), le dernier enfant impair
d'une case prend les deux colonnes et se centre : écart de centre 0 px
pour les six cases impaires du jour (CM, chaudières AM « GBT 6-10 »…). Avec
des apprentis la case est toujours paire, la règle ne la touche pas ; sur
bureau, le `flex-wrap` centrait déjà. Vérificateur identique à l'octet
(base, manques), aucune erreur de page.

**Consignation : « 8-16 » quoi qu'écrive la cellule, confirmé (20/10/2026).**
Relevé des 23 cellules « D » annotées d'une plage (22 en 2026, aucune en
2027) : 21 montrent la plage écrite, et BLR, les 22/01 et 27/10, montre
« 8-16 » malgré « 7h-15h ». Le client : « il faut bien laisser 8-16 ».
Puis, dans la foulée : « si c'est bien précisé dans la cellule, il faut
prendre la valeur de la cellule ». La première réponse est donc remplacée
(`nfdm-v869`) : pour un consignateur ou son remplaçant, une plage écrite
dans la cellule ou l'annotation passe avant « 8-16 ». Relevé des seize
journées de consignation qui écrivent une plage : huit changent — BLR les
21-22/01, 09-10/06, 22-23/07 et 27/10 passent de « 8-16 » à « 7-15 », YRS
le 12/03 à « 8-16h30 » —, les huit autres montraient déjà la plage.
Vérificateur identique (le badge seul change), hors ligne sans erreur.

## Calendrier : la vue Cycle, « Aujourd'hui » discret (20/10/2026, `nfdm-v870`)

Le client : « ajouter une vue cycle qui serait présentée comme une vue
mois… cycle, semaine, mois, année. Et un bouton plus discret pour revenir à
aujourd'hui », et « supprimer la phrase qui parle de l'horaire 2027 sous le
héros ».

**Cycle.** Un cinquième bouton, en tête de la bascule. Les cases du mois
(`caseJour`), semaine par semaine, du lundi où le cycle commence à son
dernier jour : le cycle du héros (`cycleActuel`, 5 ou 6 semaines calées sur
la personne), les autres posés bout à bout de la même longueur
(`cycleDe`). Sans calage, cinq semaines depuis le lundi. Les mois se
relisent comme dans la Semaine ; le 1er de chaque mois porte son nom
abrégé ; une case d'un autre mois ouvre sa feuille. Le titre dit les bornes
(« 19 octobre – 29 novembre », « 30 novembre – 10 janvier 2027 », abrégé au
téléphone étroit quand il ne tient pas), l'en-tête « Cycle de 6 semaines ·
21 journées · 168 h ». ‹ › passent d'un cycle à l'autre, ‹ s'éteint au
cycle qui contient le 1er janvier 2026 ; le sélecteur de date mène au cycle
du jour choisi. Le bilan du mois se retire, comme en Semaine et en Année.
Mesuré le 20/10 pour VBN, à 320, 390 et 1280 px : 42 cases, aucune page
plus large que l'écran, aucune erreur, hors ligne compris.

**Aujourd'hui** n'est plus un bouton encadré mais une icône de calendrier
sans cadre, pâlie quand on y est déjà : la place va aux quatre vues.

**La ligne « Horaire 2027 · n jours de congé déjà posés · Voir janvier »**
(`ryAnSuivanteHTML`, proposition 5 du même jour) est retirée du héros, avec
son style et son clic.

## Accueil, contrôle complet après la vue Cycle (20/10/2026, `nfdm-v871`)

Le client : « faire un check complet de l'accueil, qu'est-ce qui devient
inutile, qu'est-ce qui serait bien d'ajouter, dans quel ordre, et est-ce que
chaque partie est logique ». Photographié à 320, 390 et 1280 px, pour un
contremaître (VBN) et un opérateur (GBT) : hauteurs 2 946, 2 835 et 2 376 px,
aucun débordement ni erreur. Ordre relevé : héros (identité, prochain
poste, week-end libre, année, cycle actuel, prochain cycle) → calendrier et
bilan du mois → compteurs → Mon rythme (pauses, mois par mois, jour par
jour) → agenda du téléphone → codes. Il reste logique, du plus immédiat au
plus rare : rien n'est déplacé.

**Faute trouvée** : l'infobulle des cases des frises de cycle était cassée
depuis `9ad3540` (`title=""'+…`, l'attribut vide puis le texte hors de
tout attribut), et elle aurait de toute façon nommé le mauvais jour :
`JOURS_LONGS[d.getDay()]` part du lundi, `getDay()` du dimanche. Mesuré
après : « Mardi 20 octobre · N ».

**Ajouts** : (1) les frises « Cycle actuel » et « Prochain cycle » ouvrent
ce cycle dans la vue Cycle du calendrier (un « › » après les dates le
dit) — éprouvé : « 30 novembre – 10 janvier 2027 », puis « 19 octobre –
29 novembre » ; (2) une ligne « Congé … » sous le week-end libre : le
premier congé posé dans les 120 jours, ses codes et le nombre de jours de
congé avant la reprise, les repos du milieu non comptés, ni maladie, ni
formation, ni crédit-temps. Mesuré : VBN « Congé RJF · VA · 6 j, vendredi
23 octobre » (23-25, 28-29 RJF, 30 VA, reprise le 31 en PM, conforme au
calendrier), GBT « Congé VA · RTT · 2 j, vendredi 30 octobre ».

**Laissé, et pourquoi** : « Jour par jour » redit la vue Année et la vue
Cycle, mais le client l'a gardé (« j'aime bien jour par jour ») ; le total
« Congés · n jours restants » redit la seule ligne RTT quand les autres
congés sont tout placés, mais il reste le total dès que deux compteurs
ont un reste.

**La vue du cycle : l'équipe ou le binôme du cycle, et un cycle calé comme le
héros (20/10/2026, `nfdm-v872`).** Le client : « dans la vue cycle, les
contremaîtres et adjoints doivent voir avec quelle équipe ils sont le
cycle, et pour les 5 équipes avec quel binôme ils sont (pas le numéro mais
les trigrammes du binôme) ». L'en-tête porte à droite la lecture du héros
(`cycleAvec`) sur le cycle affiché : VBN et ATR « Équipe 1 », puis
« Équipe 3 », « Équipe 2 » ; GBT « AFA · YBT », puis « ATA · JBI »,
« GPS » ; les journées passent dessous.

**Erreur trouvée en le mesurant** : ouverte d'emblée en Cycle (vue gardée
d'une visite à l'autre), la vue partait avant que la personne soit connue,
donc du lundi de la semaine, et gardait ce départ : GBT avait « 19 octobre
– 22 novembre » quand le héros disait « 12 oct. – 15 nov. », et l'équipe
lue y était « AFA · YBT → ATA · JBI ». Pour VBN (six semaines commençant ce
lundi-là) la faute ne se voyait pas : le contrôle du `nfdm-v870` n'avait
regardé que lui. Le départ se recale désormais quand la personne ou le
jour change ; mesuré, les deux concordent pour VBN, ATR et GBT.

**Héros : « Prochain cycle » retiré, « Prochaines pauses » ajoutées
(20/10/2026, `nfdm-v873`).** Le client : « cycle actuel, on peut le
laisser, mais prochain cycle est devenu inutile », et « ajouter une stat
prochain matin, prochain PM et prochaine nuit pour savoir quand cela
arrivera ». La frise du cycle suivant (ajoutée le 17/10) part : la vue
Cycle du calendrier la montre en un appui. À sa place, trois tuiles AM ·
PM · N : la première journée prestée à cette pause dans les 180 jours,
aujourd'hui compris tant que la pause n'est pas finie, la date et le délai
(« aujourd'hui », « demain », « dans 11 j »). Mesuré le 20/10 : VBN N
mar. 20 oct., PM sam. 31 oct., AM ven. 6 nov., conformes à son calendrier ;
GBT AM demain, PM dans 3 j, N dans 6 j. À 320 px les trois dates tiennent ;
aucun débordement, aucune erreur, hors ligne compris.

**Héros : la barre de progression du cycle actuel (20/10/2026,
`nfdm-v874`).** Le client, sur sa capture : « 100 % pro ? Et si on ajoute
une barre de progression du cycle actuel ? ». La barre de l'année, reprise
entre le titre du cycle et sa frise : journées prestées sur journées du
cycle, le pourcentage au bout (« 5 % fait »), l'équipe ou le binôme
gardant sa place à droite du titre. Mesuré : VBN 1 prestée sur 21, 5 % ;
GBT 6 sur 18, 33 %. Aucun débordement à 320, 390 et 1280 px, aucune
erreur, hors ligne compris ; la frise ouvre toujours la vue Cycle.

**Héros : plus de redites (20/10/2026, `nfdm-v875`).** Le client, à deux
redites relevées : « oui exactement, et les types de congé des prochains
congés ne sont pas utiles non plus ». (1) « Prochaines pauses » ne redit
plus le prochain poste : VBN, de nuit ce soir, lit la nuit suivante,
« mer. 21 oct. · demain ». (2) Un week-end libre pris dans le prochain congé
cède la place au premier week-end libre après la reprise
(`weekendLibreApres`) : VBN, en congé du 23 au 30, passait du samedi 24
octobre au samedi 14 novembre (31 en PM, 7-8 en AM, conforme au
calendrier). (3) La ligne du congé perd ses codes : « Congé · 6 j ». Une
première écriture, « Prochain congé · 6 j », se tronquait à 320 px ;
mesurée sans troncature pour cinq personnes (VBN, GBT, ATR, KDN, JBS),
aucune erreur, hors ligne compris.

**Héros : « Prochain congé », et « Mes pauses » réunies aux prochaines
(20/10/2026, `nfdm-v877`).** Le client : « il faut indiquer Prochain congé
(pas de durée) », et « ne faut-il pas combiner mes pauses avec prochaines
pauses ? ». La ligne du congé dit « Prochain congé » et la date. Les tuiles
« Mes pauses » de « Mon rythme » (revenues là le 17/10, « le héros ne garde
que les progressions ») rejoignent celles du héros, sous le nom « Mes
pauses » : par pause, la prochaine date et son délai, puis l'année
(« 31 faites · +7 à venir »). Le D s'y ajoute s'il existe dans l'année ou
à venir ; à quatre, deux tuiles par ligne au téléphone, quatre au bureau.
« Mon rythme » garde « Mois par mois » et « Jour par jour ».

**Mesuré** pour cinq personnes à 320 px : rien de tronqué après une
correction — « Prochain congé » et « Vendredi 13 novembre » ne tenaient
pas sur une ligne (JBS) ; sous 360 px les deux dates du bloc s'abrègent
(« ven. 13 nov. »). Hauteur de l'Accueil 2 952 px à 390 (2 931 avant),
2 346 à 1280 (2 445) ; aucune erreur, hors ligne compris.

**Héros : « Mes pauses » en liste (20/10/2026, `nfdm-v878`).** Le client,
sur sa capture : « moyen d'optimiser 100 % pro ? ». Les quatre tuiles de
deux lignes prenaient environ 270 px au téléphone pour quatre dates. Une
ligne par pause, comme le week-end libre et le prochain congé : la pause,
sa prochaine date et le délai, puis l'année à droite (« 31 +7 »), sous une
seule légende de colonne, « faites · à venir ». Une ligne touchée ouvre ce
jour dans le calendrier (éprouvé : 6 novembre, 21 octobre). Hauteur de
l'Accueil 2 879 px à 390 (2 952 avant), 2 990 à 320 (3 063) ; rien de
tronqué pour cinq personnes, aucune erreur, hors ligne compris.

## Héros : la bande du haut retirée, passe complète (20/10/2026, `nfdm-v880`)

Le client, capture à l'appui : « il y a une zone foncée et une zone de
flou, ce n'était pas le cas avant » ; puis « retire la bande et optimise
tout le contenu du héros ». Aucun changement du haut de page depuis le
18/10 (relu commit par commit) : la zone foncée est la bande opaque posée
ce jour-là sous la barre d'état, le flou juste dessous vient de l'iPhone,
qui floute lui-même ce qui passe sous le haut de l'écran. La bande est
retirée : le contenu repasse sous l'heure et la batterie, comme avant le
18/10.

Photographié à 320, 390 et 1280 px pour VBN et GBT. Défauts relevés et
corrigés : (1) le pourcentage de l'année était dans le titre, celui du
cycle au bout de sa barre — tous deux au bout de la barre désormais ;
(2) « 128 journées prestées » d'un côté, « 1 prestée » de l'autre — la
légende de l'année devient « 128 prestées · 42 à venir » ; (3) la ligne D
de « Mes pauses » d'un opérateur disait « mer. 24 févr. · dans 126 j ·
1 +0 » : elle ne s'affiche que s'il reste des D dans l'année ou si le
prochain revient dans les 60 jours ; (4) au bureau, la colonne de gauche
restait vide sous le prochain poste pendant que la droite descendait seule :
« Mes pauses » passe à gauche, sous lui (son propre conteneur, `#ryPr`,
après les progressions au téléphone). Mesuré : héros 755 px au bureau pour
VBN, rien de tronqué pour cinq personnes, aucune erreur, hors ligne
compris ; la frise ouvre toujours le cycle, une pause ouvre son jour.

**Reste, et pourquoi** : le flou de l'iPhone sous la barre d'état ne
dépend pas de l'application.

**Seconde passe (20/10/2026, `nfdm-v881`).** Le client : « optimise
encore ». Héros photographié à 320, 390 et 1280 px pour cinq profils :
contremaître en poste (VBN), opérateur polyvalent (JKS), opérateur en
formation (GST), opérateur STEP en congé (PDE), contremaître en congé
(YPE). Défauts relevés et corrigés : (1) depuis le pourcentage au bout de la
barre, « Année 2026 » restait seul sur sa ligne : « 168 prestées · 39 à
venir » passe à sa droite, une ligne de moins (−22 px) ; (2) le titre et
ce qui l'accompagne à droite (« Équipe 1 », les journées) n'étaient pas
sur la même ligne de base : alignés ; (3) au bureau, « Fermentation 9/10 »
se tronquait dans les polyvalences sur trois colonnes : autant de colonnes
que la place en tient ; (4) au bureau, avec les polyvalences, la colonne
de gauche devenait la plus longue une fois « Mes pauses » dessous : elle
reste alors à droite (JKS, héros 956 → 749 px). Vérifié et NON fautif :
« Aujourd'hui » sur une nuit du 21 lu le 20 à 22 h 59 venait de l'horloge
du test, interprétée en temps universel (00 h 59 à Bruxelles). Aucun
débordement, aucune erreur, hors ligne compris.

**Le statut à côté du poste (20/10/2026, `nfdm-v882`).** Le client : « le
statut de travail à côté de son poste ? ». « Employé », « Ouvrier » ou
« Intérimaire » (en jaune) devient une étiquette à droite du poste ; la
troisième ligne ne reste que pour la formation (« En formation ·
Chaudières »). Une ligne de moins pour qui n'est pas en formation : héros
de VBN 745 → 726 px à 390. Mesuré pour sept profils à 320, 390 et
1280 px : ni poste ni étiquette tronqués, aucune erreur, hors ligne compris.

### L'Accueil vide à la première connexion (21/10/2026, `nfdm-v888`)

Le client : « au premier chargement rien n'était affiché, j'ai dû
recliquer sur Accueil ». Reproduit au navigateur, avec la nouvelle
connexion ET avec l'ancienne (version d'avant le 21/10, même résultat :
« Janvier 0 », tuiles à zéro) : le défaut n'est pas né de l'écran
d'accès. Sur un appareil neuf, le sélecteur de la personne se garnit et
appelle `suivre()` avant que `loadMonth` ait lu le mois ;
`renderFields()` lisait alors `st.month`, encore nul (« Cannot read
properties of null (reading 'primes') »), et l'erreur interrompait le
premier rendu. `renderFields()` ne fait plus rien tant que le mois n'est
pas lu ; `loadMonth` le rappelle ensuite. Après : Accueil complet dès
l'entrée, aucune erreur. Piège du test : `pageerror` de Playwright ne
remontait pas l'erreur ; il a fallu écouter `error` dans la page.
Vérificateur : quatre sorties identiques à l'octet.

### La capsule qui remonte de la hauteur du clavier (21/10/2026, `nfdm-v903`)

Le client, capture de l'iPhone à l'appui : « de temps en temps la barre de
menu déconne ». La capsule ET le bouton de retour en haut flottaient au
milieu de l'écran, décalés d'environ 300 points — la hauteur du clavier.
Défaut d'iOS en application installée : après la fermeture du clavier, la
zone de mise en page reste parfois raccourcie, et tout ce qui est fixé par
le bas s'y pose jusqu'au geste suivant. L'ancrage par quatre côtés du
22/09 n'y peut rien : c'est ce bas-là qui est faux.

On mesure l'écran réellement visible (`visualViewport`) : quand son bas
descend sous celui de la zone de mise en page, `--vvbas` (négatif) y
ramène la capsule, la bulle, le bandeau hors ligne et le bouton de retour
en haut ; clavier ouvert, on ne bouge rien. Au retour au premier plan, à
`pageshow` et à la sortie d'un champ, un `scrollTo` sur place redemande à
iOS de recaler sa zone. Chromium ne reproduit pas le défaut : on a
simulé un écran visible plus haut de 300 px que la zone de mise en page,
à 320 et 390 px : la capsule descend de 300 px (le mécanisme mord), ne
bouge pas quand le visible est plus court (clavier ouvert), revient à
16 px du bas ensuite, et hors ligne. Seul l'iPhone du client dira si c'est
guéri.

### « Une vraie plateforme de gestion et de lecture, mobile et PC » (21/10/2026, `nfdm-v905` à `nfdm-v906`)

Le client : « l'app doit être une vraie plateforme de gestion et de
lecture sur mobile/PC ; il faut optimiser tout le contenu pour cela ».
Méthode de CLAUDE.md (« optimise tout ») : un script a photographié
chaque écran (sept onglets, Réglages, six sections de l'espace RH) à 320,
390 et 1280 px, 83 captures, et mesuré lui-même le défilement horizontal,
les débordements, les textes coupés, les cibles de moins de 30 px et les
textes de moins de 10,5 px ; trois relecteurs ont lu les captures en
parallèle (une centaine de constats), et chaque correction a été
rephotographiée.

Fait :
- **Cibles du doigt** : petits boutons, vues du calendrier, flèches du
  planning à 34-36 px au téléphone (`nfdm-v905`).
- **Espace RH** : au téléphone, le menu des sections en icônes (titre
  dans la page, pastille sur l'icône), fondu aux bords entre 560 et 900 px,
  l'onglet actif centré ; le Personnel en cartes (la personne, puis VA ·
  RTT · DTT · RJF · Flex étiquetés ; flex négatif en rouge) ; tableau de
  bord : « Aujourd'hui », chiffres serrés, « Absents aujourd'hui · n
  malades, n en congé », cartes alignées en haut, « Ouvrir le planning »
  réservé au PC ; Demandes : « À viser » / « À signer » au lieu de « En
  attente » pour qui doit agir, l'étape attendue cerclée, onglets sur une
  ligne, cartes plus larges au PC ; Absences : vue **par personne et par
  période** (« CDE · Abs · Me 21 → Ve 23 oct. ») par défaut, « Jour par
  jour » gardé ; planning : textes des cases et des présents à 10,5-11 px,
  légende complète au téléphone, commentaire et saisie légendés.
- **Lisibilité** : un bloc final de styles relève les libellés porteurs
  d'information (statistiques du mois, jours de la semaine, tuiles du
  salaire, rubriques des Effectifs, polyvalences, relevé) à 10,5-11 px, du
  gris pâle au gris lisible ; les pastilles du calendrier gagnent 2 px.
  **Erreur rattrapée** : relevés à 10 px, les sous-libellés d'horaire de
  l'Équipe du jour faisaient déborder les pastilles à 320 px ; ce tableau
  tient sur un écran au pixel près, il garde ses tailles au téléphone.
- **PC (≥ 1100 px)** : Salaire en deux colonnes (le net et « Du brut au
  net » côte à côte, volets fermés par deux, un volet ouvert reprend la
  largeur) ; Réglages en colonne de 880 px ; Effectifs, les journées en
  grille ; Équipes, binômes et opérateurs en formation côte à côte ;
  bannière de l'Accueil de 240 à 190 px.
- **Anomalies** : « Lié le Invalid Date » dans Mon compte ; « +1 autres
  rappels possibles » ; « pied de feuille » retiré ; les deux pastilles de
  l'icône Effectifs ne se chevauchent plus.

Mesuré après : aucun défilement horizontal, aucune erreur, aux trois
largeurs ; textes de moins de 10,5 px de ~400 à 162 (les grilles denses
calées au pixel : planning, Équipe du jour, polyvalences) ; vérificateur
identique à l'octet ; connexion, demandes et hors ligne rejoués.

Laissé, et pourquoi : le bouton de retour en haut reste visible dès 200 px
(décision du client du 19/10) ; la date « mm/jj » du champ de la
Recherche vient de la langue du navigateur de test, pas d'un téléphone
français ; les redites de « Mes compteurs » et du « Prochain poste », la
légende de l'Équipe du jour et le regroupement des cartes d'Effectifs par
mois touchent à des choix faits avec le client et attendent son avis.

### Le menu de contrôle à gauche, au PC (21/10/2026, `nfdm-v907`)

Le client : « sur PC cela peut être une plateforme avec menu de contrôle
complet sur la gauche. Tout doit être optimisé. » Au-delà de 1100 px,
l'en-tête devient une colonne fixe de 248 px, comme les applications RH du
marché : la marque, le jour et le poste ; les sept sections de l'application (Effectifs garde
ses deux pastilles) ;
un groupe **Gestion** (« Mon équipe » pour un opérateur) qui ouvre les
sections de l'espace RH (Demandes y porte le nombre à traiter) et,
en bas, les Réglages. L'espace RH s'ouvre À DROITE du menu, qui reste
utilisable (le fond n'est plus rendu inerte au PC) ; son propre menu se
cache ; un onglet de l'application ou les Réglages le referment. La
sélection suit : l'onglet sous l'espace ouvert s'efface au profit de la
section de Gestion. Le tableau de bord passe en colonnes qui se remplissent
(la carte des absents ne creuse plus de trou). La catégorie écrite en
minuscule par le classeur (« chaudières éq. 5 ») prend sa majuscule à
l'affichage. Téléphone et tablette ne changent pas (mesuré à 390 et
1000 px : pas de menu latéral, contenu à 0 px du bord).

Éprouvé au navigateur à 1280 px, Supabase simulé : contenu à 248 px du
bord, pas de défilement horizontal ; Gestion → Tableau de bord (espace à
248 px, section cochée, pastille « 1 »), → Personnel, puis l'onglet
Salaire referme l'espace, puis Réglages ; aucune erreur.

### « Valide toujours tout seul » (21/10/2026, `nfdm-v908`)

Le client : « j'aimerais que tu valides toujours tout seul et pousser sur
Notion et GitHub ; on perd un temps fou car je ne fais pas attention que
tu ne progresses pas tant que je n'ai pas validé ». La règle est dans
CLAUDE.md. Les trois choix laissés en suspens au tour précédent sont
tranchés : **légende de l'Équipe du jour** ajoutée au PC (vous, en
formation, commentaire, changement de poste proposé, relais 12 h, place
vide — le sens lu dans le code qui pose chaque repère ; au téléphone le
tableau tient sur un écran au pixel près, pas de place) ; **« Mes
compteurs »** : le total des congés reste en tête, c'est le résumé de
tous les compteurs et il ne double une ligne que lorsqu'un seul compteur
a un solde ; **« Prochain poste »** : la date reste, le billet du 18/10
est le dessin du client et l'en-tête du téléphone ne montre pas la date.

### Notion suspendu tant qu'il demande une validation (22/10/2026)

Le client : « arrête de pousser sur Notion si tu n'arrives pas à approuver
tout seul ces modifications ». Les écritures par le connecteur Notion
ouvraient une fenêtre d'autorisation chez lui, alors que tout Notion est
autorisé dans `.claude/settings.json` : une session cloud ne s'y fie pas
toujours, seul le mode « Auto », que lui seul peut choisir, les fait
taire. **Décision : plus aucune écriture dans Notion** (ni ligne du
journal des versions, ni page principale, ni décision, ni suivi) jusqu'à
ce que le client dise que les fenêtres ont disparu. Le dépôt reste la
source de vérité ; le dossier Notion s'arrête à `nfdm-v914`, et se
rattrapera depuis le journal si le client le réactive. Cette décision
l'emporte sur la consigne du 21/10 (« pousser sur Notion et GitHub »)
et sur l'étape « reporter dans Notion » de CLAUDE.md.

### Le contrôle « UI UX Pro Max » (21/10/2026, `nfdm-v911`)

Le client : « check avec le nouveau skill ». La liste de contrôle avant
livraison du skill (`references/pro-rules.md`) a été traduite en mesures
au navigateur, sur chaque écran à 375 px (son « petit téléphone ») et
1280 px : contraste de chaque texte contre son fond réel (4,5:1, 3:1 en
grand), cibles du doigt de 44 px, boutons à icône sans nom, champs sans
libellé, images sans texte, émojis en guise d'icônes, défilement
horizontal, zoom, mouvement réduit, focus visible.

Avant : 90 textes sous le contraste minimal, 169 cibles de moins de
44 px ; aucun bouton sans nom, aucun champ sans libellé, aucune image
sans texte, aucun émoji, pas de défilement horizontal, mouvement réduit
et focus visible présents. **Erreur de mesure rattrapée** : le premier
calcul prenait un fond à 2,5 % d'opacité pour du blanc pur (les
week-ends du relevé à « 1,7:1 ») ; les fonds se composent désormais
couche par couche.

Corrigé : dans le thème sombre, les pastilles de pause (fond clair) et
les compteurs de présents passent à l'encre foncée (de 2,1-2,7:1 à plus
de 6:1), les pastilles de nombre orange de même ; l'orange et le
sarcelle du calendrier, un ton plus soutenus (3,9 et 4,1 → 4,5:1 et
plus) ; tirets et points des cases vides au gris lisible. Au téléphone,
44 px pour les petits boutons, les bascules, les flèches, les champs du
Salaire, des Réglages et de la Recherche, les en-têtes de mois, le menu
et la croix de l'espace RH, les lignes « Mes pauses » et celles de
l'explication du salaire. Après : **0** texte sous le contraste,
**0** cible sous 44 px hors les cases du calendrier (43 px de large :
sept colonnes à 375 px) ; aucun défilement horizontal, aucune erreur.

Laissé, et pourquoi : **le zoom reste bloqué** — la règle du skill dit
l'inverse, mais c'est une décision du client (06/10/2026 : « désactiver
absolument le zoom in/out même au double clic »).

### « Optimise tout », la passe entière (21/10/2026, `nfdm-v912`)

Le client : « Optimise tout ». Méthode de CLAUDE.md : 82 captures (320,
390 et 1280 px, clair et sombre), trois audits parallèles avec le skill
(l’espace RH ; le salaire, les réglages et la recherche ; l’accueil, le planning et les équipes),
puis tout corrigé dans la même version.

- **Espace RH** : la table des absences par personne passe en cartes au
  téléphone ; trois chiffres par ligne ; les onglets ne passent plus à la
  ligne ; le badge des absents ne montre que le nombre ; le sous-titre
  suit la vue et l'horizon ; « (h) » dans les en-têtes des compteurs ;
  un état vide avec un bouton dans l'historique ; « Équipe » prend sa
  majuscule ; sous 360 px, le compteur du jour se cache et le menu se
  resserre.
- **Le salaire, les réglages et la recherche** : « Mon contrat » sous « Mon compte » ;
  durée étiquetée, les doublons « Jour / Période / Heures » retirés ; le
  nom de la pause n'est plus réécrit dans les rappels évitables ; « ·
  Équipe N » dans les changements de poste ; « Renseigner mon contrat »
  devient le bouton principal ; la Recherche vide dit quoi faire.
- **L’accueil et les équipes** : l'écart avec le mois d'avant porte son unité
  (« ▼ 56 h vs sept. », et non « ▼ 56 ») ; sous 381 px, les quatre tuiles
  passent en 2×2 (l'écart se rognait) ; les notes du classeur ne
  ressemblent plus à des champs à remplir (un trait à gauche) ; la
  légende dit « (touchez) » au téléphone, « (cliquez) » à la souris — le
  commentaire se lit au clic, pas au survol.

Laissé, et pourquoi : le zoom bloqué (décision du 06/10) et le bouton
« remonter » dès 200 px (décision du 19/10) ; la légende des
polyvalences, retirée le 03/10, n'est pas remise sans le client ; la
carte « Planning des équipes » reste au PC tant que le menu de gauche ne
mène pas à toutes ses vues.

### Direction, un onglet et non plus une feuille (21/10/2026, `nfdm-v913`)

Le client : « Direction doit s'afficher comme un onglet au lieu d'une
feuille à part ». La vue s'ouvrait par-dessus tout (`position:fixed`,
défilement de la page bloqué, croix pour fermer) : elle est désormais le
panneau `#v-direction`, une vue comme les autres de `VIEWS`, choisie par
`setView()` depuis la barre du bas, le menu de gauche au PC ou le bouton
des Réglages ; la croix et la touche Échap n'ont plus lieu d'être. La
carte sombre reste, posée dans la page. L'horloge s'arrête quand on
quitte l'onglet. Une personne qui n'est pas RH n'y atterrit jamais, même
si l'onglet était le dernier ouvert sur l'appareil.

Éprouvé au navigateur : RH à 320, 390 et 1280 px, onglet sélectionné,
aucun défilement horizontal, aucune erreur ; une section puis « ‹
Direction » ramène à l'accueil de la vue ; Salaire puis Direction la
rouvre ; un opérateur dont la dernière vue était Direction retombe sur
l'Accueil, sans onglet Direction.

### « BioWanze APP », et l'Accueil du PC rééquilibré (21/10/2026, `nfdm-v914`)

Le client : la fenêtre de l'application installée sur PC s'intitulait
« BIOWANZE - Mon équipe - BIOWANZE » (le nom du manifeste, puis le titre
de la page) ; elle doit dire « BioWanze APP ». Le nom et le nom court du
manifeste, le `<title>` et le titre de l'écran d'accueil iOS le disent
désormais tous. Une application déjà installée relit son manifeste au fil
des jours (Chrome le revérifie de lui-même) ; le titre de la page, lui,
change dès le rechargement.

Le haut de l'Accueil, au PC : sous le poste en cours, « Mes pauses »
laissait un grand vide à droite, sous les progressions. Dès 1240 px, elle
y passe, en deux colonnes, et les deux côtés finissent à la même hauteur.
Entre 1100 et 1240 px on garde l'ancienne place : en deux colonnes,
« dans 16 j » se coupait, et en une seule, c'était la gauche qui restait
vide (essayé, photographié, défait).

Le même jour, sur une capture du client au PC, deux choses de plus. **Le
logo prend toute la largeur du menu de gauche** (215 px), et le mot
« BIOWANZE » n'est plus réécrit à côté : le logo le porte déjà (le titre
reste pour les lecteurs d'écran). **Le menu était dans le désordre** :
la Gestion, puis les Réglages, puis l’Accueil et le Planning `placerOnglets()` remettait
la barre d'onglets à la FIN de l'en-tête (`appendChild`) quand la fenêtre
passait d'étroite à large — ouverte petite puis agrandie, cas du client.
Elle se replace désormais juste après la marque, et la feuille fixe en
plus l'ordre des blocs (`order`). Éprouvé au navigateur, page ouverte à
700 px puis agrandie à 1280 : la marque, les onglets, la Gestion et les Réglages (la
cause a été lue dans le code, le désordre n'a pas été photographié avant
le correctif).

### Le Planning au PC sans légende, un filet sous la barre de titre, « BioWanze.app » (22/10/2026, `nfdm-v915`)

Trois demandes du client, captures à l'appui.

- « Il ne faut pas de légende au planning sur PC et il faut optimiser son
  affichage. » La légende ajoutée le 21/10 (`nfdm-v908`) se cache dès
  1100 px ; elle reste sur tablette, dont le client n'a rien dit. Le
  tableau prend toute la largeur à droite du menu (il flottait entre deux
  marges, 1480 px au plus). Sur un écran d'au moins 1500 × 850, les
  pastilles grossissent (trigramme à 15,5 px, horaire à côté) pour se lire
  de loin. Mesuré : à 1920 × 1040, les dix lignes tiennent sans défiler ;
  à 1280 × 720, les pastilles agrandies passaient à la ligne et la
  dernière ligne sortait du cadre (essayé, photographié) : en dessous de
  1500 × 850 elles gardent leur taille, et le tableau entier tient grâce à
  la place que la légende a rendue.
- « La même ligne qui sépare la colonne de gauche et droite pour séparer
  la barre de titre de fenêtre et le contenu. » Un filet d'un pixel en
  haut de la fenêtre, dès 1100 px, de la couleur pleine que prend le trait
  vertical (#232937, mesurée sur la capture) : en semi-transparent comme
  lui, il sortait plus foncé au-dessus du contenu, dont le fond est plus
  sombre que celui du menu. Mesuré au pixel : même couleur au-dessus du
  menu et du contenu que le trait vertical. **Erreur** : le filet était
  posé sur `body::before`, qui porte déjà le fond dégradé de
  l'application ; la v915 a donc remplacé tout le fond par le filet
  (le client : « le background a changé, il ne fallait pas »). J'avais
  mesuré la couleur du filet, pas le reste de la page. Corrigé en
  `nfdm-v916` : le filet passe sur `html::before`, et le fond est comparé
  au pixel avec la `nfdm-v914` (quatre points, identiques).
- « BioWanze.app » remplace « BioWanze APP » (nom, nom court, titre,
  écran d'accueil iOS).

### Le menu rangé, et le Planning du PC à la forme du téléphone (22/10/2026, `nfdm-v917`)

Le client : « comment organiserais-tu mieux les onglets et catégories du
menu ? », puis, à la proposition : « optimise au maximum, et aussi j'aime
beaucoup le planning sur mobile, mais j'ai du mal avec la version PC
(tableau trop grand ?) ».

- **Au PC, trois catégories** dans le menu de gauche : « Mon espace »
  (Accueil · Salaire), « L'usine » (Planning · Équipes · Effectifs ·
  Recherche), « Gestion » (Direction, puis l'espace RH). L'ordre se fait
  par la feuille (`order`) : le document garde l'ordre du 10/10, que
  suivent la tablette et les flèches du clavier. Direction quitte la
  liste des onglets pour la Gestion, réservée à la RH comme elle.
- **« Planning des équipes » devient « Planning par personne »** dans le
  menu : à côté de « Planning », les deux noms se confondaient ; le
  second est une ligne par personne. L'onglet « Planning », nommé avec
  le client le 09/10, garde son nom.
- **Au téléphone, cinq icônes** au lieu de sept pour la RH (six pour les
  autres) : Accueil · Planning · Équipes · Salaire · Plus. « Plus » ouvre une
  feuille au-dessus de la barre : Effectifs (et ses deux pastilles) ·
  Recherche · Direction pour la RH, puis la Gestion ou « Mon équipe ». Le
  bouton porte la pastille des absents du jour, et se teinte quand l'une
  de ses sections est ouverte. Échap ou le fond la referment.
- **Le Planning du PC** reprend la forme du téléphone : une carte de
  1000 px au plus, centrée, à la hauteur de la fenêtre, au lieu d'un
  tableau étiré sur toute la largeur où l'œil traversait des vides pour
  lier un poste à ses trigrammes ; les pastilles agrandies de la v915 sont
  retirées. À 1280 × 720, le tableau entier tient.
- La flèche « › » des cartes de Direction passe de 2,9:1 à plus de
  4,5:1 de contraste : la vue n'était pas contrôlée tant qu'elle était
  une feuille à part.

Éprouvé au navigateur : RH et opérateur à 320 et 390 px (cinq icônes,
feuille, Effectifs ouvre l'onglet et teinte « Plus », la Gestion s'ouvre
depuis la feuille) ; RH à 1280 (catégories, Direction depuis la Gestion
et marquée, l'espace RH s'ouvre et se referme sur un onglet) ; 900 px
inchangé. Aucun défilement horizontal, aucune erreur ; contraste et
cibles à zéro partout, hors les cases du calendrier (connues).

Le même jour, le client : « sur PC le logo peut être plus petit et centré
horizontalement dans la colonne du menu ». 96 px de haut, centré
(`object-fit:contain`), au lieu des 165 px de toute la largeur.

### « Horaire production », au style de l'outil « Horaires » du client (22/10/2026, `nfdm-v919`)

Le client : « j'aimerais que le "Planning par personne" devienne "Horaire
production" et que celui-ci ressemble plus à ce que nous utilisons », puis,
avec sa page `Horaires.html` (son outil, hors du dépôt) : « inspire-toi de
ce style pour l'horaire ». La page et ses données (`operateurs-data.txt`,
des noms réels) ne sont PAS entrées dans le dépôt : la page a été ouverte
dans un navigateur isolé, réseau coupé, nourrie d'une liste faite de nos
seuls trigrammes, pour en relever le style.

- **Le nom** : « Horaire production » au menu, dans la feuille « Plus »,
  dans l'espace RH et en titre.
- **Le style relevé** et repris : la feuille claire ; la colonne du mois
  en lettres verticales ; les mois alternés bleu (#C7DEF5) et jaune
  (#FEF9C3) ; le gris des week-ends (#C7CCD4), l'orange des fériés
  (#FFE2B3), le jaune d'aujourd'hui (#FDE68A) ; la ligne des postes
  teintée (meunerie et gluten jaune, arrière vert, chaudières saumon,
  STEP bleu) au-dessus de la ligne des personnes ; un trait épais entre
  les personnes et entre les semaines ; les équipes en pilules sombres,
  l'active en blanc (« Équipe 1 » à « Équipe 5 », « Contremaître »,
  « Formation », « STEP ») ; la légende des codes, tirée du classeur, en
  bas.
- **Du classeur**, gardé : deux cases par personne, le prévu puis
  l'annotation en rouge, et le triangle rouge des commentaires. La saisie
  (RH, hiérarchie) se fait sur l'une ou l'autre case.
- Au téléphone, la colonne des présents, absente du classeur, cède sa
  place aux personnes.

Une première version reprenait les couleurs du classeur Excel (bleu
#B8CCE4, onglets des feuilles en bas) ; remplacée le même jour par le
style de l'outil, que le client a désigné.

### L'Horaire production, exactement comme l'outil du client, en vue année (22/10/2026, `nfdm-v920`)

Le client : « l'horaire doit être exactement présenté comme le fichier que
je t'ai fourni et toujours en vue année, mais avec toutes les
améliorations et fonctionnalités que nous avons ajoutées ». Sa page
(`Horaires.html`, hors du dépôt) a été lue — feuille de style et rendu
de la vue équipe, `buildPlanning` et `buildFooterTables` — et reproduite :

- **Toujours l'année** : 365 lignes, du 1er janvier au 31 décembre,
  ouvertes sur aujourd'hui au milieu de l'écran ; les flèches changent
  d'année (2026, 2027), les boutons Semaine et Mois disparaissent.
- **La barre de l'outil** : « Vue journée » (mène au Planning du jour),
  Équipe 1 à 5 et Contremaître en pilules sombres, puis les postes dans
  leur couleur — Meunerie · Gluten · Fermentation · Polyvalent Arrière ·
  Distillation · Chaudière · Station d'Épuration · Formation. Un poste
  montre ses gens des cinq équipes (« Éq. N » sous le nom).
- **Le tableau** : colonne du mois en lettres verticales et colonne du
  jour (44 px chacune), puis par personne pause (44), congé en rouge
  (44) et commentaire (20, une bulle) ; le bouton des adjoints, ON/OFF, dans le coin
  en vue équipe ; jours ouvrables jaunes, mois pairs bleus, week-ends
  gris, fériés orange, aujourd'hui plus soutenu ; traits de 2 px entre
  personnes, postes, semaines et mois ; ligne et colonne survolées.
- **Le pied** de l'outil — et du classeur : « Soldes en heures au
  01/01 », « Prévisions en heures » (VA, RTT, DTT, RJF, FT+, FT−), « Soldes
  compte tenu des prévisions » (en bleu, négatifs en rouge). Réservé à
  la RH et à la hiérarchie, et seulement pour une année aux compteurs
  fiables, comme la fiche d'une personne : un opérateur ne lit pas les
  compteurs d'un collègue. Les prévisions sont recomptées sur l'horaire
  (saisies comprises), les soldes viennent du classeur.
- **La légende des codes** en bas, tirée du classeur ; les trois boutons
  ronds haut, aujourd'hui, bas.
- **Gardé de l'application** : la saisie d'une case (RH, hiérarchie), le
  nom qui ouvre les compteurs, la recherche, le liseré vert des saisies.

Écarts voulus avec l'outil : la colonne du congé montre l'annotation du
classeur (le réel), la pause celle du classeur (le prévu) — l'outil
recalculait la pause par le cycle ; ici le classeur reste la source.
La bulle de commentaire est dessinée, pas un émoji.

Éprouvé : RH à 1280 et 390 px, opérateur à 1280 (365 lignes ; pied de 14
lignes pour la RH, aucun pour l'opérateur ; le bouton des adjoints retire le
groupe ; Gluten des cinq équipes ; survol ligne et colonne ; une case
ouvre la saisie ; 2027 puis retour ; Vue journée) ; aucune erreur,
aucun défilement horizontal de la page.

### L'Accueil réorganisé (22/10/2026, `nfdm-v921`)

Le client : « GO », à la proposition de réorganiser l'Accueil au PC.

- **Retirés de l'Accueil, passés dans Réglages** : « Agenda du
  téléphone » et « Les codes » — un réglage et une référence, dont on ne
  se sert qu'une fois.
- **« Mois par mois » retiré de Mon rythme** : le « jour par jour », juste
  dessous, dit la même saison en plus précis (et le client l'aimait, le
  20/10).
- **Ajoutés, sous le héros** : « Ma semaine » (aujourd'hui et les six
  jours suivants, la pause ou ce qui la remplace, un point quand la
  journée porte un commentaire ; un toucher ouvre le jour) et « Mes
  demandes » (celles en cours, avec leurs étapes ; « Nouvelle demande » et
  « Mes demandes » ouvrent l'espace des demandes). Au PC, côte à côte,
  dans les deux colonnes du calendrier et des compteurs.
- **Ce qui n'a pas été fait de la proposition, et pourquoi** : la photo
  du haut devait passer à ~90 px ; à 100 puis 140 px, le logo du bandeau
  se coupait (photographié) — elle garde ses 190 px. Les trois colonnes
  au PC rendaient le calendrier trop étroit à 1280 px (≈ 400 px) : Ma
  semaine et Mes demandes se rangent dans les deux colonnes existantes.

Mesuré à 1280 px, photo à 190 px : la page passe de 2 208 à 2 058 px ;
le calendrier, lui, DESCEND de 631 à 808 px du haut, sous Ma semaine et
Mes demandes. Une première version de cette entrée disait « 2 008 px, le
calendrier monte à 758 » : mesuré avec la photo à 140 px, elle était
fausse et est corrigée ici.

Le même jour, le style clair de l'ancienne page Équipes du client a été
posé sur l'onglet Équipes, puis RETIRÉ à sa demande : « il faut garder le
thème initial pour tous les onglets, sauf celui de l'horaire, que l'on
optimisera ensemble ». Seul l'Horaire production a le style de l'outil.

### « Vraiment adapté au PC », première passe (22/10/2026, `nfdm-v922`)

Le client : « optimise tout pour que cela soit vraiment adapté sur PC ».
51 captures à 1280 et 1920 px (`audit-pc`), relues par trois audits
parallèles ; en attendant leurs rapports :

- **Le héros à 1920 px** laissait vide le bas de sa colonne de gauche,
  sous « En poste » : dès 1600 px il passe en trois colonnes (le poste ;
  l'année et le cycle ; mes pauses en liste). Mesuré : 615 → 520 px de
  haut, le calendrier apparaît sans défiler.
- **Ma semaine et Mes demandes**, côte à côte, prennent la même hauteur.
- **« Touchez » devient « Cliquez » à la souris** (`(hover:hover) and
  (pointer:fine)`) : mode d'emploi du Salaire, consigne de l'Horaire
  production, aide des compteurs du Personnel. Le guide d'installation
  garde « Touchez » : il décrit un téléphone.

### « Vraiment adapté au PC », les trois audits (22/10/2026, `nfdm-v923`)

Trois audits parallèles des 51 captures (l’accueil, le planning et les équipes ;
le salaire, les effectifs, la recherche, les réglages et la direction ;
l’espace RH), chaque
constat revu sur la capture avant d'être appliqué.

Appliqué (au-delà de 1100 px, sauf mention) :
- Accueil : le passage de « Mes pauses » à droite dès 1240 px (v914) est
  RETIRÉ — à 1280 la colonne de gauche finissait 140 px plus haut ;
  jusqu'à 1599 px la fiche reprend sa disposition du 20/10, dès 1600 elle
  est en trois colonnes. Calendrier et compteurs à la même hauteur ;
  « Mon rythme » sur 1 200 px, mois et jours en 11 px (9 et 10 avant).
- Équipes : en-têtes du recyclage en 12 px (9,5 avant), « Opérateurs hors
  équipe » en 11 px.
- Horaire production : la rangée de boutons passe à la ligne (on ne voyait
  rien après « Gluten » à 1280) ; l'en-tête des noms colle à celui des
  postes (une bande de 3 à 4 px laissait voir le corps défiler).
- Dans l’espace RH : les outils d'en-tête collés à droite ; recherche du
  Personnel à 420 px ; l'historique vide en 900 px ; au tableau de bord, le
  second « Ouvrir le planning » retiré et la pastille « AM » à 11 px ; dès
  1500 px, la table des absences à 1 100 px et les onglets des demandes à
  760 px.
- Direction : la largeur de la carte, les tuiles en rangées pleines (cinq
  par rangée à 1920), sans redire le logo du menu.
- Recherche : la carte à 1 100 px au plus, centrée.
- Effectifs : les sous-effectifs et les absents au même rythme de colonnes
  (360 et 300 px) ; une grille essayée sur les rappels évitables rétrécissait
  l'en-tête du mois — retirée (photographié).
- Salaire : le bouton « Renseigner mon contrat » sous la phrase ; les
  libellés du relevé en 11,5 px ; l'échelle du flex time en 11 px.

Non appliqué, et pourquoi : élargir le Planning du jour à 1 240 px (le
client le trouvait trop grand ; 1 000 px voulus) ; masquer les boutons
ronds de l'Horaire production (l'outil du client les a) ; deux colonnes
aux Réglages et une refonte de « Du brut au net » (pas de défaut de
lecture, seulement de la place).

Mesuré après : aucune police utile sous 10,5 px à 1280 et 1920 px (21
avant), aucun défilement horizontal de page à 320, 390, 1280 et 1920 px,
aucune erreur ; seul l'Horaire production défile dans sa zone, comme voulu.

### Revenir en arrière depuis une demande, au téléphone (22/10/2026, `nfdm-v924`)

Le client : « quand je regarde une demande sur mobile, pas possible de
revenir en arrière ». Reproduit au navigateur (390 px, tactile) : la
feuille s'ouvre en plein écran ; le geste « retour » du téléphone QUITTAIT
la page entière (l'application ne posait aucune étape dans l'historique) ;
et la croix, à 17 px du haut d'une feuille qui commence au bord de
l'écran, tombait sous la barre d'état dans l'application installée.

- Ouvrir une feuille (panneau) ou l'espace RH pose une étape dans
  l'historique ; « retour » referme la feuille, puis l'espace, dans
  l'ordre — même procédé que le guide d'installation. Refermer par un
  bouton retire l'étape (un seul `history.go(-n)` pour plusieurs), pour
  que le retour suivant ne sorte pas de l'application.
- L'en-tête de la feuille laisse la place de la barre d'état
  (`env(safe-area-inset-top)`), un bouton « ‹ Retour » bien visible à
  gauche, la croix à 44 px.

Éprouvé : 1er retour → feuille fermée, espace ouvert ; 2e → espace
fermé, toujours dans l'application ; « ‹ Retour » et la croix ferment la
feuille ; un retour ensuite ferme l'espace sans quitter la page ; aucune
erreur, et les parcours des demandes (`dm3.js`, `dmod.js`), du menu et de
l'Horaire production passent.

Le même jour, sur une capture du client (iPhone) : « moyen d'optimiser ».
En lecture, au téléphone, les lignes vides de la feuille se replient en
« + N lignes libres » : une demande d'un jour montrait neuf lignes vides,
la moitié de l'écran ; la demande entière tient désormais sur un écran,
visa compris (photographié à 390 px). La feuille complète reste au PC et
dans le formulaire, où les lignes servent. Le titre de l'en-tête
paraissait flou et pâle sur l'iPhone : aucune règle ne l'explique et
Chromium ne le reproduit pas ; il est désormais blanc franc, en 650, sur
un fond opaque — à revoir sur le téléphone du client (`nfdm-v925`).

### La vue Semaine cassée par « Ma semaine » (22/10/2026, `nfdm-v927`)

Le client : « la vue semaine de l'Accueil ne va pas ». **Erreur commise
le 22/10 (`nfdm-v921`)** : la carte « Ma semaine » a reçu une fonction
nommée `renderSemaine` — le nom de celle, plus ancienne, qui dessine la
vue Semaine du calendrier. Dans un même script, la seconde déclaration
remplace la première : le calendrier appelait la fonction de la carte
avec un mauvais argument (« Cannot read properties of undefined (reading
'id') »), et la vue Semaine restait vide. Aucun test ne cliquait
« Semaine » ; `audit.js` ne relevait que les erreurs du chargement.
Renommée `renderMaSemaine` ; vérifié qu'aucune autre fonction de premier
niveau n'est déclarée deux fois (`grep … | uniq -d` → aucune). Éprouvé à
390 et 1280 px : la semaine s'affiche, aucune erreur, Ma semaine aussi.

### Au téléphone, plus de menu en haut de l'espace (22/10/2026, `nfdm-v928`)

Le client : « il ne faut pas le menu en haut de page quand on veut faire
une demande de congé (ni nulle part ailleurs sur mobile) ». Au téléphone,
la rangée d'icônes de l'espace (`.ws-nav`) disparaît ; la barre du bas de
l'application reste active au-dessus de l'espace (elle était rendue
inerte à l'ouverture) : ses onglets le referment, « Plus » mène à ses
sections et se teinte tant que l'espace est ouvert. Une feuille ouverte
en plein écran (demande, signature) efface la barre du bas : restent
« ‹ Retour » et « Signer et envoyer ».

Trouvé en l'éprouvant : toucher un onglet ne refermait pas l'espace —
l'écouteur cherchait la barre dans l'en-tête (`header.top .tabs`), alors
qu'au téléphone elle est déjà rangée en bas. Il la cherche partout.

Éprouvé à 390 px (tactile) : menu du haut caché, barre du bas active et
« Plus » teinté ; formulaire en plein écran sans la barre, « Signer » dans
l'écran ; « ‹ Retour » puis l'onglet Accueil referment l'espace ; aucune
erreur, et les parcours des demandes, du menu et de l'Horaire production
passent.

**Erreur de méthode trouvée le même jour** : `dm3.js` (le parcours d'une
demande : envoi, signature du remplaçant, visa RH) lit la largeur dans son
DEUXIÈME argument (`node dm3.js <dossier> <largeur>`) ; il était lancé
`node dm3.js 1280`, si bien que toutes les passes « 1280 » des journaux
du 21 et du 22/10 ont en réalité testé 390 px. Lancé correctement, il
passe à 390 et à 1280 (après l'avoir fait passer par la barre du bas au
téléphone, le menu du haut n'y étant plus).

### Supprimer une demande, et le cadre « Mes demandes » resserré (22/10/2026, `nfdm-v929`)

Le client : « une demande peut être supprimée tant qu'elle n'a été signée
par aucune autre personne que soit ; il faut optimiser le cadre des
demandes de congé ».

- **Supprimer** : le bouton n'apparaît que si personne d'autre que le
  demandeur n'a signé (ni remplaçant, ni contremaître, ni RH :
  `dmSignesAutres`). Il remplace « Annuler ma demande », sur la carte et
  dans le pied de la feuille, passe par une confirmation (« Supprimer la
  demande ? » / « Garder ») et appelle `biowanze_annuler_demande`. Une
  demande supprimée disparaît de l'historique. Mesuré (`suppr.js`,
  390 px) : demande non signée → [Voir la feuille · Modifier · Supprimer] ;
  signée par le remplaçant → sans Supprimer ; l'appel part bien sur le
  bon numéro ; 0 erreur.
- **La garde n'est qu'à l'écran** : la base accepte encore l'annulation
  d'une demande signée par un remplaçant (elle ne refuse qu'après un visa
  du contremaître ou de la RH). La fermer demande un changement de base,
  soumis au client.
- **Le cadre** : « + Nouvelle » dans l'en-tête, une ligne par demande en
  cours (date, statut, étapes), une bannière « N remplacement(s) à
  signer », et l'historique replié derrière un lien. 280 px de haut à
  390 px de large.
- **Le titre flou sous la barre d'état d'iOS 26** : c'est l'effet de verre
  que le système pose sous la barre d'état quand le contenu y défile ; un
  voile opaque (`html::after`, hauteur `env(safe-area-inset-top)`) le
  masque au téléphone.

### Le cadre de l'adresse retiré de la demande de congé (22/10/2026, `nfdm-v930`)

Le client : « supprimer le cadre en haut à droite avec l'adresse sur la
demande de congé ». Le cadre (`dm-pp-adr`) et ses deux règles CSS sont
retirés ; le logo reste seul en tête de la feuille, pour les trois
formulaires. Vérifié à 390 px (`dmvoir.js`) : plus de cadre, 0 erreur ;
`dmod.js` et `gate2.js` inchangés.

### « Mes demandes » devient « Demande de congé » (22/10/2026, `nfdm-v931`)

Le client : « Mes demandes doit s'appeler “demande de congé” ». Le titre
du cadre de l'Accueil change ; rien d'autre (l'onglet « Demandes » de
l'espace RH garde son nom). `suppr.js` et `gate2.js` : 0 erreur.

### Les fiches de recyclage « polyvalence » (22/10/2026, `nfdm-v932`)

Le client : « il faut aussi ajouter, comme pour les demandes de congé, les
demandes de polyvalence ; c'est la personne qui fait office de
contremaître lors de la pause de la demande qui doit valider si la
polyvalence a été faite complètement et confirmer », avec la fiche papier
du dossier RH (juin 2021), puis « go recyclage ».

- **La base** (`base/15-recyclages.sql`, appliqué avec `execute_sql`, sans
  aucune suppression) : une table à part de `demandes` (la décision d'une
  demande réécrit l'horaire ; une fiche ne doit rien y toucher), cinq
  fonctions et le déclencheur des notifications. Le circuit du papier :
  le travailleur signe → le contremaître de la pause confirme ou refuse
  (motif obligatoire) → en doublure, le responsable de zone contresigne →
  la RH valide et enregistre. Une fiche par pause, et on ne signe jamais
  sa propre fiche, à aucune étape.
- **Éprouvé dans une transaction annulée** (trois comptes, dont deux
  prêtés pour l'essai puis remis en place par l'annulation) : doublon
  refusé ; confirmer sa propre fiche refusé ; opérateur qui contresigne
  refusé ; validation RH avant la contresignature refusée ; RH qui valide
  sa propre fiche refusé ; anonyme refusé ; le circuit complet aboutit à
  « validée », avec les bons signataires et les sept notifications à la
  bonne personne. Défaut trouvé à l'essai et corrigé : un demandeur RH
  recevait « à contresigner » et « à valider » pour sa propre fiche.
- **Le contremaître attendu** se lit dans l'horaire, par les mêmes
  fonctions qu'« Équipe du jour » (`equipeDuJour`, `postesDePause`, le
  poste `P.cm`) ; la pause est préremplie là où l'horaire place la
  personne. Introuvable (pause D, horaire absent), la fiche va à la RH.
  L'application l'envoie avec la fiche : la base ne connaît pas l'horaire
  des postes. La RH voit qui a confirmé.
- **L'écran** : la section « Recyclages » (menu du PC, feuille « Plus » du
  téléphone), avec ses onglets « À traiter », « Mes fiches », « Historique »
  ou « Toutes » ; la fiche reproduit le papier, sans le cadre de l'adresse,
  les mots choisis entourés comme au stylo ; une bannière sur l'Accueil
  quand une fiche attend sa confirmation ; la notification ouvre la
  section (`?vue=recyclages`). Les compteurs de recyclage restent ceux du
  classeur RH : une fiche validée ne les change pas.
- **Navigateur** (`rc.js`, base simulée) : à 390 px pour l'opérateur, puis
  pour le contremaître, et à 1280 px pour la RH ; plus à 320 px pour
  l'opérateur. Fonction absente, titulaire absent en doublure et refus
  sans motif sont arrêtés à l'écran. Les appels partent avec les bons
  paramètres. Aucun débordement, aucune erreur. Corrigé à l'essai : le
  contremaître ne retrouvait plus la fiche qu'il venait de confirmer.
  Elle est maintenant dans son « Historique ».
- **Question ouverte** : qui est le responsable de zone
  (`docs/questions-client.md`). D'ici là, tout compte hiérarchie ou RH
  contresigne.

### Les demandes supprimées ne se voient plus nulle part (22/10/2026)

Le client : « les demandes supprimées, donc annulées, peuvent être effacées
et n'ont pas besoin d'être visibles » (`base/16-effacer.sql`).

- **Appliqué** : les listes de la base (`biowanze_liste_demandes`,
  `biowanze_liste_recyclages`) ne rendent plus rien d'annulé, ni chez
  l'opérateur, ni chez la RH. Cela vaut aussi pour l'ancienne version
  d'une demande modifiée. Et la base fait maintenant respecter la règle
  du client : une demande déjà signée par une autre personne (remplaçant,
  contremaître ou RH) ne se supprime plus. Jusqu'ici, c'était l'écran
  seul qui retenait la signature du remplaçant. Les notifications pas
  encore parties d'une demande supprimée ne partent pas.
- **Éprouvé** dans une transaction annulée : suppression d'une demande
  signée par le remplaçant refusée ; demande libre supprimée, sa
  notification retenue, invisible dans la liste ; la demande signée,
  elle, reste visible.
- **En attente** : l'effacement réel, c'est-à-dire des fonctions qui
  effacent la ligne au lieu de la marquer « annulée », et la purge des
  demandes déjà annulées. Le connecteur Supabase demande une
  confirmation pour toute instruction qui efface. L'envoi est resté
  suspendu une minute, puis a expiré : vérifié ensuite, rien n'était
  appliqué. On ne contourne pas cette confirmation ; la partie est
  écrite, en commentaire, au bas du fichier.

### « Durée » de la Recherche : les boutons débordaient (22/10/2026, `nfdm-v933`)

Le client, capture d'iPhone à l'appui : « sur mobile les boutons buguent ».
Le cadre « Jour / Période / Heures » est fixé à 44 px, marge intérieure de
3 px comprise ; la règle du toucher (44 px minimum par bouton, au
téléphone) faisait des boutons de 44 px, posés 4 px sous le haut du
cadre : ils en sortaient de 4 px par le bas. Désormais, ils remplissent
le cadre (36 px), et un `::after` invisible leur rend 44 px au doigt.
Mesuré : tous les boutons des grilles et des barres, sur l'Accueil, la
Recherche, les Effectifs, la Direction, le Planning, l'Équipe et le
Salaire, à 390 px : aucun ne sort de son parent (`deb.js`). Le contrôle
mord : sur la version d'avant, il nomme les trois boutons de « Durée »,
4 px de chaque côté. Un toucher 2 px sous « Période » le sélectionne.

### L'Accueil devient un centre de contrôle (22/10/2026, `nfdm-v934`)

Le client : « l'accueil doit être un vrai centre de contrôle pour
l'utilisateur ; il doit avoir tout à portée de main, intuitif,
professionnel et complet ». Photographié d'abord à 390 et 1280 px :
l'Accueil avait le héros, Ma semaine, la demande de congé, le calendrier,
les compteurs et le rythme. Ce qui manquait, c'étaient les gestes
eux-mêmes, et un endroit qui dise ce qui attend une action ; les
remplacements à signer et les fiches à confirmer n'étaient que des
bannières dans le cadre des congés.

Un cadre « À portée de main », juste sous le héros (pleine largeur au
PC, en trois colonnes), réunit trois choses :

- **Six raccourcis** : demander un congé, une fiche de recyclage (la
  feuille s'ouvre directement), ma fiche de paie, l'équipe du jour,
  l'horaire production et mon agenda (l'abonnement). Sans compte relié à
  la base, il en reste quatre.
- **« À faire »** : seulement ce qui attend une action (horaire modifié,
  remplacements à signer, demandes à viser pour la RH, fiches de
  recyclage à confirmer), avec leur nombre en pastille ; puis, « En
  route », ses fiches de recyclage en cours. Les demandes de congé en
  cours restent dans leur cadre, juste en dessous ; ses bannières sont
  retirées, pour qu'elles ne s'affichent pas deux fois. Si rien
  n'attend : « Rien ne vous attend ».
- **« Ma prochaine pause »** : la pause, le poste, l'effectif, le
  contremaître et les collègues du même poste, lus par `equipeDuJour` et
  `postesDePause` ; toucher la ligne ouvre le Planning de ce jour.

Mesuré (`ctl.js`, base simulée) : à 390 et 1280 px, chacune des neuf
cibles mène au bon écran ou au bon onglet ; aucun débordement à 320 px ;
0 erreur. `deb.js` : aucun bouton ne sort de son cadre dans les sept
écrans parcourus.

### Planning : sa place habituelle revient d'office au remplacé (22/10/2026, `nfdm-v935`)

Le client, capture du 21/10 AM : SMA proposé de la fermentation vers le
terrain arrière, et le terrain arrière laissé en « ? ». « Ce genre de
changement devrait être comblé d'office. » La règle et ses trois
conditions sont dans `docs/conversion-horaire.md`, « Remplacé à son tour ».

- **Deux erreurs de la première version**, trouvées par une trace dans le
  navigateur : `posteAttitreLe()` rend le poste DU JOUR (AAI écrit
  « distillation » ce jour-là), pas la place habituelle ; et la lecture de
  « remplace X » courait jusqu'au bout du commentaire (« remplace LCI
  remplacé par AAI » donnait LCI, PAR, AAI). On lit `posteAttitre()`, et
  la lecture s'arrête au « remplac » suivant. La première hypothèse (un
  chassé-croisé : AAI laisserait vide SA place) était fausse : le terrain
  arrière est la place de SMA, pas celle d'AAI (POSTE_HABITUEL, 27/09).
- **Mesuré sur l'année** (`plan-an.js`, le Planning des 365 jours avant et
  après) : trois journées changent, le 21/10 AM, le 31/01 PM (ALZ) et le
  06/07 N (FPS), toutes trois dans la forme que le client décrit. Le
  vérificateur (quatre sorties), les agendas et `comparer-fiches.py VBN`
  sont identiques à l'octet.

### JBI le 22/10 : « remplaçait » n'était pas lu ; la vraie pause dans la demande de congé (22/10/2026, `nfdm-v936`)

**1. « Remplace YBT qui remplaçait YRS ».** Le client : « pourquoi JBI
n'est placé nulle part alors que son commentaire indique bien “remplace
YRS” pour aller en meunerie ? ». `atelierDuRemplace()` lisait
« remp\w* » : en JavaScript, `\w` ne connaît pas le « ç », et
« remplaçait » s'arrêtait à « rempla ». On ne lisait que YBT (adjoint absent) :
JBI restait en ligne Adjoint, la meunerie en « ? ». Le motif prend
désormais les lettres accentuées.

Mesuré, avant et après :
- **Planning** (365 jours) : cinq journées changent, toutes celles de
  JBI. Le 22/10 AM, il passe en meunerie et le « ? » disparaît. Les
  05/11 N, 24/11 AM, 25 et 26/11 PM, il tient le poste de contremaître :
  « Remplace YBT qui remplaçait AFA », AFA absent et « Remplacé par
  JBI ». C'est la règle du 13/10, un adjoint qui remplace un contremaître.
- **Manques** : 22 places creuses deviennent 18 ; les quatre manques de
  contremaître de novembre disparaissent.
- **Polyvalence** : JBI passe à 5/5 en meunerie, SLT redescend à 4/10.
- **Agendas** : seul `cal/JBI.ics` change, sur ces cinq journées.
- **Vérificateur** : « motif trop étroit » passe de 47 à 46. Il le
  signalait.
- **Compteurs** et `comparer-fiches.py VBN` sont identiques à l'octet.

**2. La pause de la demande de congé.** Le client : « la pause qui
s'indique dans ma colonne est la pause normale du cycle et non celle que
je fais vraiment ». `dmPrevue()`, à l'écran, et la base
(`base/17-pause-du-jour.sql`, `biowanze.pause_du_jour`) lisaient la
cellule. Désormais, une annotation qui écrit une pause ou une plage
l'emporte : pour un échange, ["N","PM"] donne PM ; pour un rappel,
["-","AM"] donne AM. Ce rappel était refusé jusqu'ici comme « un repos :
rien à modifier ». Avant d'appliquer, la version en base a été comparée à
`12-formulaires.sql` : identique à l'octet. Éprouvé : dans la base (une
transaction annulée), BLR le 22/10 avec JBI remplaçant donne
`prevue: PM` et `rp_prevue: AM` (avant : N et « - ») ; à l'écran, les
cartes de BLR, de JBI et de SMA donnent PM, AM et AM (avant : N, « – »,
AM).

### Des badges décalés de 2 px, et PLZ annoncé pour rien (22/10/2026, `nfdm-v937`)

**« Badge non aligné ? »** (capture du Planning du 22/10, au PC) : LDY
2 px sous JBI, CHD sous CKS, ATR sous GDT. Le premier badge d'une case
ne recevait que `.eqc>.eqn{margin:0}`, du même poids que la règle des
états `.eqn:is(.coment, .form…){margin:2px 3px}`, posée plus loin : elle
gagnait. Les badges suivants, eux, avaient `.eqn+.eqn`, plus lourde. Le
remède : `.eqn.eqn`. Mesuré sur 30 jours de Planning (`alig.js`), en
comptant les rangées de badges d'une même case dont les hauts diffèrent :
109 sur 1 392 au PC avant, 0 sur 1 380 après ; 0 au téléphone, avant
comme après (la grille du téléphone n'avait pas le défaut).

**« Et pourquoi PLZ ? »** L'onglet des effectifs annonçait « PLZ · Gluten →
Terrain arrière » pour l'après-midi du 22/10, alors que GDT (« poly.
Etoh », remplace DWS) puis ATR (de 20 h à 22 h) tiennent le poste. Le
Planning ne le proposait plus depuis le 20/10 : un changement n'y a de
sens que vers un poste qui resterait sous son effectif. Mais la liste
« Changements de poste à prévenir » (`transfertsDuJour`, lue aussi par
le héros de l'Accueil), calculée à part, reprenait le rééquilibrage
brut : c'était la seconde copie d'une règle, celle qui était restée en
arrière. Elle applique désormais la même condition. Mesuré sur les
sept jours à venir : 5 changements avant, 2 après. Les trois retirés
(PLZ le 22, GDT les nuits des 24 et 25) ne sont pas proposés au
Planning ; les deux restants (SMA le 23, PAM le 26) le sont. Les quatre
sorties du vérificateur sont inchangées.

### AAI à la distillation, PAM à la fermentation : d'office (22/10/2026, `nfdm-v938`)

Deux demandes du client, à la suite : « AAI et SMA, on avait déjà dit
que c'était AAI qui prenait la place de SMA en distillation », puis « et
pareil pour PAM le 26, qui est en fermentation vu que GPO remplace QBY ».
Les règles, leurs conditions et les 27 journées qu'elles changent sont
dans `docs/conversion-horaire.md`, « Deux autres changements que
l'application fait d'office ».

**Erreurs de la première version, mesurées avant le commit**
(`plan-an.js`, le Planning des 365 jours) : 35 journées changeaient ;
la règle du remplaçant écrit passait avant l'échange AAI / SMA et le
défaisait (le 23/10 remontrait SMA en distillation) ; et elle déplaçait
vers des postes déjà complets (CDE le 20/01). Corrigées en réordonnant
les règles et en ajoutant deux conditions : sa place habituelle, et un
poste d'arrivée qui manquerait sans lui. Les quatre sorties du
vérificateur et les agendas sont inchangés ; l'alignement des badges
reste à 0 décalage.

### Le centre de contrôle, une seconde passe (22/10/2026, `nfdm-v939`)

Le client : « top le centre de contrôle, mais il y a moyen d'optimiser
cela encore plus ». Photographié à 390 et 1280 px, puis relu bloc par
bloc :

- **Une redite** : « Ma prochaine pause » était un second « Prochain
  poste », juste sous celui du héros. Elle est retirée. Ce qu'elle
  apportait, le contremaître de la pause et les collègues du même poste,
  passe dans le billet du héros, sous l'atelier (« Fermentation · CM
  GPS »). Le trigramme en gras y héritait la taille de la date (15,5 px) :
  ramené à celle de la ligne.
- **Des raccourcis qui disent leur état** : « 1 en cours » sous
  « Demander un congé », « 1 en route » sous la fiche de recyclage, le
  mois sous la fiche de paie ; sinon une ligne fixe, pour que les tuiles
  aient toutes la même hauteur. « Équipe du jour » disait « 21 oct. »
  pendant que le héros annonçait jeudi 22 (avant 6 h, le jour de l'usine
  est encore la veille) : elle dit « aujourd'hui ».
- **Plus compact** : au PC, deux colonnes (raccourcis, à faire) au lieu
  de trois. Au téléphone, des tuiles de 68 px au lieu de 76. Le cadre
  passe de 666 à 516 px de haut à 390 px, avec deux tâches.

Mesuré : à 320, 390 et 1280 px, aucun débordement ; les huit raccourcis
et lignes testés mènent au bon écran ; 0 erreur.

### Les placements d'office ne sont plus « à prévenir » (22/10/2026, `nfdm-v940`)

Le client, capture des Effectifs à l'appui : « toujours le cas ? AAI et
PAM ? ». Le Planning les plaçait bien, mais la liste « Changements de
poste à prévenir » les annonçait encore, avec leur raison. Le choix,
fait la veille sans le dire, était de prévenir quiconque change de poste
par rapport à sa case. Or le client parle d'office : c'est leur place,
rien à annoncer. `transfertsDuJour()` écarte désormais les trois
placements d'office, par les mêmes fonctions que le Planning :
`placeDOffice`, `echangeHabituel` et `tenuParRemplacant` (avec la même
condition d'un poste d'arrivée en manque). Mesuré : la semaine du 22/10
passe de 2 changements à « Rien à signaler » ; celle du 20/10 garde sa
vraie proposition (JBI en distillation la nuit du 20) et ne liste plus
SMA le 21. Les quatre sorties du vérificateur sont inchangées.

### L'Accueil relu en entier : quatre défauts (22/10/2026, `nfdm-v941`)

Le client : « tout est professionnel et optimisé pour l'accueil ? ».
Photographié à 320 et 1280 px, bloc par bloc ; quatre défauts, tous
corrigés :

1. **« Demande de congé » vide** : sans demande en cours ni traitée, le
   cadre ne disait que « Aucune demande en cours », et son
   « + Nouvelle » répétait le raccourci « Demander un congé ». Il se
   cache ; au PC, « Ma semaine » prend alors toute la largeur.
2. **« Ma semaine » contredisait le héros** : avant 6 h, elle partait du
   jour de l'usine (« Auj. 21 ») sous un héros et un calendrier qui
   disaient le 22. Elle part du jour du calendrier.
3. **Au PC, le centre de contrôle** : six raccourcis sur une rangée et
   « À faire » dessous, au lieu de deux rangées et d'une moitié droite
   vide. 237 px de haut au lieu de 310.
4. **À 320 px**, « sur le téléphone » passait sur trois lignes et
   déformait la grille : « abonnement ».

Ce qui reste, et pourquoi : le mois d'octobre de l'opérateur d'essai est
tout en maladie, et ses compteurs font 815 px au téléphone. Ce sont ses
données : on ne les touche pas. Mesuré : aucun débordement à 320 et
1280 px ; les raccourcis mènent au bon écran ; 0 erreur.

### Le contremaître du jour, après le remplaçant ; les cartes de sous-effectif alignées (22/10/2026, `nfdm-v942`)

**Les réponses du client.**
- « C'est le contremaître qui a la fonction ce jour-là qui doit être
  notifié de la demande faite durant sa pause ; sinon cela doit bien
  apparaître pour tous les autres contremaîtres et adjoints. »
- « Non, toujours le remplaçant avant le contremaître. »
- Le responsable de zone reste, en attendant, tout compte hiérarchie ou
  RH.

**Ce qui est fait** (`base/18-contremaitre-du-jour.sql`). Les quatre
fonctions remplacées avaient été comparées à l'octet à celles du dépôt
avant d'être appliquées.
- À l'envoi, chaque ligne porte `cm` : le contremaître de la pause du
  demandeur ce jour-là, lu dans l'horaire (`rcContremaitre`, comme la
  fiche de recyclage).
- Il est notifié en même temps que la RH, une fois la demande complète
  (sans remplaçant, ou à la dernière signature).
- `attend_cm` attend les remplaçants, et la garde de la base refuse le
  visa de la hiérarchie avant leur signature.
- Les autres comptes hiérarchie voient toujours toutes les demandes.

**Éprouvé dans une transaction annulée** :
- la ligne garde `cm: GPS` ;
- avant la signature, GPS ne voit rien à viser et son visa est refusé ;
- après, il voit la demande, la vise (« validée en partie »), et les
  notifications vont à JBI (remplaçant), GPS (« pendant votre pause »)
  et au demandeur.
- Au navigateur (`dmod.js`), l'envoi porte `cm: ATR` les trois jours,
  c'est-à-dire le contremaître que le Planning montre à ces pauses.

**Limite.** Quand deux personnes sont sur la ligne Contremaître (ATR et
YPE le 28/10 AM), c'est la première qui est notifiée.

**« Décalage des cadres sous-effectifs ? »** Au PC, la première carte
d'une rangée descendait de 10 px : `:first-child` et `.eqsem+.mqj`,
plus lourds, gardaient la marge du téléphone que `html #mqCorps .mqj`
devait annuler. C'est le même défaut que les badges du Planning.
Mesuré (`mq.js`, mois dépliés) : 2 rangées décalées de 10 px à 1280 et
1920 px avant, 0 après. Puis tous les onglets à 1920 px (`grilles.js`) :
il ne reste que les 4 px voulus du titre « Mes pauses » dans le héros en
trois colonnes.

### La gestion au style du Planning et des Équipes ; « Demande de congé » (22/10/2026, `nfdm-v943`)

Le client : « Demande, dans le menu, doit être “Demande de congé”, et sur
PC l'écran » ; puis « les onglets de gestion ne respectent pas vraiment le
style des onglets Planning et Équipe ; il faudrait uniformiser les
cadres ». Photographiés à 1440 px :
- **Le Planning, les Équipes et les Effectifs** : chaque bloc est un cadre (bord
  `--cadre`, coins `--rj`, ombre) avec une barre de titre interne : fond
  `--surface2`, titre centré de 16 px, description de 11 px, filet bas.
- **La gestion** : un grand titre de 22 px aligné à gauche, hors cadre ;
  des cartes au bord léger ; des listes et des tableaux posés sur le fond.

Corrigé en CSS seul, sans toucher aux rendus. Chaque section de gestion
devient le cadre, et sa tête devient la barre centrée (les boutons à
droite, dessous au téléphone). Les cartes intérieures reçoivent la barre
des journées des Effectifs : titre à gauche, nombre ou bouton à droite.
Une première version les centrait : « Sous-effectif (14 j) » se coupait
sous sa pastille, et « Tout l'historique » passait sur deux lignes. L'Horaire
production garde son style, comme le client l'a demandé. Le menu, la
feuille « Plus » et le titre de l'écran disent « Demande de congé ».
Vérifié à 1440 et 390 px, sur les six sections ; tests des demandes et
des fiches : 0 erreur.

### Les fonds de la gestion (22/10/2026, `nfdm-v944`)

Le client : « surtout les backgrounds aussi ». Mesuré au pixel, à 1440 px,
sur un coin vide de la page : l'onglet Équipes est à (14, 19, 32) et
(17, 25, 42), le dégradé navy `--fond` de `body::before` ; la gestion
était à (6, 10, 19), l'aplat `--paper` de `.grille`, posé par-dessus.
Désormais `.grille.ws` prend `--fond` sur `--paper` : (15, 21, 35) et
(18, 26, 44), le même dégradé à un point près. Les en-têtes de tableau
(`--surface2`, gris, fin) prennent ceux des Équipes : le fond du cadre,
le texte en clair et en gras, un filet `--cadre`. Vérifié à 1440 et
390 px : 0 erreur.

### La bulle du « ? » : qui remplacer, et seulement ceux qu'on peut prendre (22/10/2026, `nfdm-v945`)

Le client, capture du Planning du 28/10 à l'appui : « quand on clique sur
un absent, il doit marquer les personnes qu'il faut remplacer en plus de
ceux qui peuvent prendre le poste, et ne pas proposer ceux qui sont à un
poste qui serait en sous-effectif sans eux (exemple FPA), mais préciser
en jaune ceux qui sont en formation, comme pour GST ».

`candidatsPlace()` et `bulleCandidatsHTML()` :
- **« À remplacer »** en tête : le titulaire absent et son motif, par
  `aRemplacer()`, la même lecture que les raisons d'un changement.
- **« Peut prendre le poste »** dessous. Un candidat dont le poste
  tomberait sous son effectif sans lui n'est plus cité (FPA, seul au
  gluten l'après-midi). On garde la proposition de l'application
  elle-même, pour que la bulle ne contredise pas le pointillé du
  Planning.
- **« en formation »** écrit en jaune à côté du badge jaune.

Mesuré le 28/10 : la fermentation PM affiche « À remplacer : CKS RJF »,
puis ALZ (proposé), FLN (en surnombre) et GST (Chaudières, en
formation) ; FPA n'y est plus. Le vérificateur (quatre sorties) et
l'alignement des badges sont inchangés.

### « Remplacé par X » dans la case de l'absent (22/10/2026, `nfdm-v946`)

Le client : « il faut vérifier aussi, lorsqu'il y a des trous comme cela,
si le remplaçant n'était pas nommé dans le commentaire de CKS cette
pause là ». CKS le 28/10 n'a pas de commentaire (`["PM","RJF"]`), et
personne ne le nomme : rien à trouver ce jour-là. Mais sur l'année, un
balayage des 502 places vides du Planning (`trous.js`) en a trouvé 128
dont l'absent nomme un remplaçant. La règle et ses conditions sont dans
`docs/conversion-horaire.md`, « “Remplacé par X” dans la case de
l'absent ».

**Erreurs de la première version**
- `verifier-calendrier.js` s'arrêtait (« nommesParAbsents is not
  defined ») : il reprend une liste NOMMÉE de fonctions d'`index.html`,
  il fallait lui ajouter les deux nouvelles.
- « Remplacé par JKS ou HKB » (YRS, le 30/04) déplaçait JKS et creusait
  le gluten. Un nom suivi de « ou » ou de « ? » est désormais écarté.

**Mesuré**
- Planning (365 jours) : 13 journées changent, toutes fidèles au
  classeur.
- `--manques` (depuis le 26/09) et `--compteurs` sont identiques ;
  `--polyvalence` change, une journée de recyclage pour six personnes ;
  les agendas sont identiques.
- La bulle du « ? » montre ce que dit la case de l'absent quand
  l'application n'a pas pu placer le remplaçant (LAX le 22/01 :
  « remplacé par KDN et FLN »).

### La bulle du « ? » : les mentions de couleur à droite, de même taille (22/10/2026, `nfdm-v947`)

Le client : « uniformiser la taille des explications de couleur
(formation, proposé, surnombre) ainsi que l'alignement à droite (comme
pour proposé et surnombre) ». « en formation » était écrit dans le
texte du poste, à 12 px ; il devient une mention `em` comme les deux
autres : 11 px, gras 600, alignée à droite, en jaune. Si un candidat
est à la fois en formation et proposé, les deux mentions se suivent.
Vérifié au navigateur le 28/10 PM.

### Le 28/10 : PAM, pas GPO (22/10/2026, `nfdm-v953`)

Les deux règles du client (les trois postes arrière se comblent entre
eux ; on déplace d'abord celui que rien n'attache) sont dans
`docs/conversion-horaire.md`, « Fermentation, terrain arrière,
distillation se comblent entre eux ».

Mesuré :
- **Planning** (`plan-an.js`, 365 jours) : 50 journées changent.
- **La bulle du 28/10 N** : « PAM · Distillation · proposé » en tête,
  puis GKT et GPO en surnombre.
- **Le vérificateur** : `--manques` et `--compteurs` identiques ;
  `--polyvalence` change pour quatre personnes, d'une à quatre journées.

### La bulle du « ? » dit toujours qui manque (22/10/2026, `nfdm-v954`)

Le client, sur la fermentation de la nuit du 28/10 : « il n'est pas
marqué qui il manque ? ». Personne n'y manque : l'équipe 4 n'a pas de
titulaire de fermentation (APN, LAA, CKS et CHD sont des équipes 1, 2,
3 et 5). La section « À remplacer » restait muette. Elle dit désormais,
quand personne n'est absent : le titulaire présent mais placé ailleurs
(« présent, en … »), sinon « Personne de l'équipe n'est prévu à cette
place ». La première formule, « pas de titulaire à ce poste », était
fausse au gluten du 22/01 PM : il y attend deux personnes et un titulaire
est là. Vérifié le 28/10 N et le 22/01.

### Le 11/11 : le terrain arrière « complet mais cherché », et PAM (22/10/2026, `nfdm-v955`)

Le client : « terrain arrière complet, mais tu cherches un remplaçant ?
Et pourquoi PAM n'est pas en fermentation ? »

**Le faux « ? » du terrain arrière** (11/11 AM, SBZ et GKT présents,
« 0/1 »). Au terrain arrière, `tenu` n'est pas une somme : c'est le
nombre de polyvalents arrière, ou, à défaut, celui des renforts
(`postesDePause`). Le Planning, en remettant les propositions à leur
place (`renderEquipe`), faisait `tenu--` à chaque départ. AAI, porté au
terrain arrière par le rééquilibrage puis rendu à la distillation, ôtait
donc 1 à un compte auquel il n'avait rien ajouté. Trouvé par une trace
dans le navigateur (`DBG terr 1111 0 1 1 SBZ GKT`). Désormais
`tenuDuPoste()` recompte à chaque déplacement, avec la règle de
`postesDePause`.

**Erreurs de la première version**
- `tenuDuPoste` écartait les copies venues du D. La meunerie du matin
  compte pourtant son consignateur (« 8-16 ») : 4 journées gagnaient un
  « ? ».
- `verifier-calendrier.js` ne connaissait pas `ARRIERE_POSTES`.

**PAM** : voir `docs/conversion-horaire.md`, « … et, entre ces trois
postes, d'office ».

**Mesuré** (`plan-an.js`, 365 jours)
- Planning : 121 journées changent, 119 « ? » disparaissent, aucun
  n'apparaît.
- Effectifs : cette semaine, « Rien à signaler ».
- Les quatre sorties du vérificateur sont identiques à l'octet :
  l'affichage seul a changé.

### « Mes pauses » dans l'ordre où elles reviennent (22/10/2026, v956)

Le client, avec une capture : « moyen d'optimiser la partie mes pauses ».
Ce qui n'allait pas :

- l'ordre était fixe (AM, PM, N, D) alors que les dates ne l'étaient pas :
  l'œil cherchait la plus proche entre « dans 15 j », « dans 9 j » et
  « dans 10 j » ;
- « 31 +7 » ne se lisait qu'avec la légende de colonne, loin à droite.

Ce qui a été fait :

- les lignes sont triées par date de retour ; une pause sans date ferme la
  liste ; la première a son délai en couleur ;
- sous les nombres, un filet de la couleur de la pause donne la part faite
  de l'année (faites ÷ faites + à venir) ;
- le délai passe sous la date : sur une ligne, « dans 8 j » se coupait à
  320 px une fois le filet ajouté (vu à la capture, corrigé avant le
  commit). Padding réduit de 9 à 7 px : une ligne fait 51 px au lieu de 48.

Mesuré à 320, 390 et 1280 px : aucun débordement, aucune erreur. Les
quatre sorties du vérificateur sont identiques à l'octet.

### « Ma semaine » à la place du « Cycle actuel », dans le héros (22/10/2026, v957)

Le client, sur la capture de la v956 : « supprimer cycle actuel et
remplacer par ma semaine ».

- Dans le héros, sous l'année, les sept jours qui viennent remplacent le
  cycle actuel. Pour la plage du titre, une seule fois le mois s'il ne
  change pas (« 22 – 28 oct. »).
- Le cadre « Ma semaine » placé sous le centre de contrôle disparaît : il
  aurait redit le héros. Au PC, « Demande de congé » prend toute la
  largeur.
- Les cases prennent le fond sombre du héros, comme « Mes pauses ». Une
  pause AM, PM, N ou D y porte la même pastille que le reste du héros ;
  les autres codes gardent la leur. Le point d'un commentaire passe en
  5 px dans le coin : à 320 px, il touchait les lettres « VE ».
- Le cycle reste à un appui : vue Cycle du calendrier. `ryCycleHTML`,
  `ouvrirCycle` et leurs deux écouteurs ne servaient plus qu'au héros :
  retirés (le premier état de cette note disait à tort que `ryCycleHTML`
  servait encore au calendrier ; un `grep` l'a démenti).

Mesuré à 320, 390 et 1280 px (cases de 34, 44 et 73 px) : aucun
débordement, aucune erreur. Les quatre sorties du vérificateur sont
identiques à l'octet.

### « Ma semaine » nomme le remplaçant au lieu d'un point (22/10/2026, v959)

Le client, sur la capture de la v958 : « comment optimiser ». Sa semaine
portait le point jaune du commentaire sur six cases sur sept : un signal
partout ne signale plus rien. Ses commentaires disaient pourtant tout :
« échange avec GPS », « remplacé par ATR » (trois jours), « remplacé par
AFA ».

`msNomme()` prend le premier trigramme connu, écrit en majuscules, après
« remplacé par », « remplace », « remplaçait » ou « échange avec ». Il est
écrit en jaune sous la pastille : sur un congé, c'est le remplaçant ; sur
un poste, celui qu'on remplace ou avec qui l'on échange. Le point reste
pour un commentaire qui ne nomme personne (« équipe au complet »). Un
commentaire qui doute (« ou », « ? ») ne nomme personne, comme au
Planning. Le commentaire entier est dans le titre et dans le libellé
d'accessibilité.

Mesuré sur la semaine du client : GPS, ATR, ATR, AFA, repos, repos, ATR.
Les cases passent de 81 à 101 px. Aucun débordement à 320, 390 et
1280 px. Les quatre sorties du vérificateur sont identiques à l'octet.

### Les cases de « Ma semaine » resserrées, sans trigramme ni point (22/10/2026, v960)

Le client, à la v959 : « inutile les trigrammes et c'est tous les jours
que je te demandais d'optimiser ». **Erreur commise** : sa question
« comment optimiser » visait les cases elles-mêmes, et j'avais répondu
par un détail du commentaire. Les trigrammes sont retirés (`msNomme`
supprimé), le point de commentaire aussi : il marquait six cases sur
sept, et le commentaire se lit en touchant le jour.

Les cases :

- le jour et la date serrés, la pastille dessous : 76 px au lieu de 81 (au
  PC, 81 au lieu de 89) ;
- un repos s'efface : sans cadre, la date et « repos » en gris, pour que
  les jours travaillés et les congés ressortent ;
- le samedi et le dimanche ont leur libellé en bleu clair.

Aucun débordement à 320, 390 et 1280 px. Les quatre sorties du
vérificateur sont identiques à l'octet.

### Dates en entier, et des compteurs de pauses à l'échelle (22/10/2026, v961)

Le client : « jour avec majuscule dans la semaine, jour écrit en entier,
et le mois aussi. Concernant les compteurs de pauses, il faut que cela
soit mieux représentatif par rapport à la quantité et le restant ».

- **Ma semaine** : « Ve », « Sa », « Auj. », l'initiale seule en
  majuscule, au lieu de « VE » ; la plage du titre a le mois en entier
  (« 22 – 28 octobre »). Le nom du jour en entier ne tient pas dans une
  case de 34 px (320 px) : il reste en deux lettres.
- **Mes pauses**, date en entier comme le prochain poste (« Samedi 31
  octobre »), le délai au bout de la même ligne.
- **Les compteurs** :
  - avant, un filet de 62 px par pause donnait la seule part faite : 11 PM
    sur 15 et 70 nuits sur 94 se ressemblaient ;
  - chaque barre court maintenant sous toute la ligne, longue du total
    de l'année de sa pause rapporté à la pause la plus fréquente, la part
    faite en plein et le restant en pâle ;
  - dessous, « 70 faites » à gauche et « reste 24 » à droite, en toutes
    lettres ;
  - la légende « faites · à venir » devient « année 2026 ».
- **Erreur évitée** : avec les nombres à droite de la date, « Dimanche 1
  novembre » passait sur deux lignes à 320 px. Les nombres sont passés
  sous la barre. Sous 360 px, la pastille se resserre (30 px) et la date
  passe à 13,5 px.

Mesuré à 390 et 1280 px : une ligne fait 77 px. À 320 px, aucune date
réelle de la semaine du client ne passe sur deux lignes. Le pire cas
construit (« Mercredi 30 septembre », « dans 100 j ») passe proprement
sur deux lignes, 90 px. Aucun débordement. Les quatre sorties du
vérificateur sont identiques à l'octet.

### « Mes pauses » en tableau, sous une barre de répartition (22/10/2026, v962)

Le client, sur la capture de la v961 : « que penses-tu de mes pauses,
c'est clair ou non ? Sinon trouve une autre présentation plus intuitive
et professionnelle ». Ma réponse : non, pas assez clair.

- Chaque pause prenait trois étages (la date, une barre, « 70 faites ·
  reste 24 ») : 90 px par ligne, 360 px pour quatre pauses.
- Le restant, en pâle à 32 % sur une piste sombre, ne se distinguait
  presque pas de la piste.
- Les nombres, en phrases sous la barre, ne se comparaient pas d'une
  pause à l'autre.

Ce qui l'a remplacé :

- **une barre pour l'année**, au-dessus : un segment par pause, long de son
  total. La part faite est en plein ; le restant est hachuré de la même
  couleur et se voit même sombre. Une légende « faites / restantes » ;
- **un tableau** : la pause, la prochaine date en entier et son délai,
  puis deux colonnes de nombres titrées, « Faites » (blanc) et « Reste »
  (gris), alignées à droite pour se comparer d'un coup d'œil. Une ligne
  touchée ouvre toujours le jour.

Mesuré :

- une ligne fait 50 px à 390 px (90 avant) ;
- à 320 px, colonnes et pastille resserrées : « Dimanche 1 novembre »
  passe sur deux lignes, les autres dates tiennent ;
- aucun débordement à 320, 390 et 1280 px ;
- les quatre sorties du vérificateur sont identiques à l'octet.

### Une seule barre pour l'année, par pause (22/10/2026, v963)

Le client, sur la capture de la v962 : « qu'en penses-tu ? ».

**Le constat.** Le tableau était clair. Mais deux barres disaient la même
chose, à trois blocs d'écart :

- « Année 2026 », 130 prestées sur 170, en bleu ;
- la répartition de « Mes pauses », les mêmes 130 et 40 découpés par
  pause, avec sa propre légende.

**Ce qui a été fait.**

- La barre de l'année est la répartition elle-même (`ryBarre`, quand
  `ryCompte` donne le détail par pause) : un segment par pause, la part
  prestée en plein, le reste hachuré, et toujours « 76 % fait » au bout.
- La légende entre dans le compte : une pastille pleine devant
  « 130 prestées », une hachurée devant « 40 à venir ».
- « Mes pauses » ne garde que le tableau : une barre et une ligne de
  légende en moins.

Aucun débordement à 320, 390 et 1280 px. Les quatre sorties du
vérificateur sont identiques à l'octet.

### Week-end libre et prochain congé en deux cases (22/10/2026, v964)

Le client, sur la capture de la v963 : « qu'en penses-tu ? Et les lignes
prochain week-end et congé, présenterais-tu cela autrement ? ».

**Avis.** Le haut est cohérent. Mais les deux lignes « libellé … date »
ne disaient pas quand, alors que « Mes pauses », dessous, écrit « dans
9 j ». Et le week-end ne donnait que le samedi.

**Ce qui a été fait.**

- Deux cases côte à côte sous le prochain poste, séparées par un filet.
  Chacune donne le libellé (petites capitales), la date en entier, puis le
  délai (« dans 23 j », « demain »).
- Le week-end donne les deux jours : « 14 – 15 novembre », ou les deux
  mois s'il est à cheval.
- « Ce week-end » reste tel quel, sans délai.
- S'il n'y a qu'une des deux, elle prend toute la largeur.
- Sous 380 px, les libellés perdent les capitales : « WEEK-END LI… » se
  coupait à 320 px.

Mesuré : aucun débordement à 320, 390 et 1280 px. À 320 px, les dates
passent sur deux lignes dans leur case. Les quatre sorties du
vérificateur sont identiques à l'octet.

### La bande du haut, retirée une seconde fois ; trois chiffres de l'année (22/10/2026, v965)

Le client : « de nouveau la barre bleue dans le dessus de l'écran est
revenue ; quelles autres stats peuvent être présentes dans le héros ? ».

**Erreur commise.** Le matin même (v929, avec la suppression des
demandes), j'avais posé un fond opaque `#0d1220` derrière la barre d'état
(`html::after`), pour que les titres ne passent plus flous dessous. Le
client avait refusé exactement cette bande le 20/10 (v880, « retire la
bande »). Je ne l'avais pas cherché dans le journal avant de la remettre.
Elle est retirée ; à sa place, un commentaire le dit. **À retenir :** le
flou de l'iPhone sous la barre d'état est accepté par le client ; on ne
pose rien derrière elle.

**Trois chiffres sous la barre de l'année**, ce qu'elle ne dit pas :

- les heures ;
- les journées travaillées un samedi ou un dimanche (« en week-end ») ;
- les jours fériés travaillés.

Ils couvrent toute l'année, journées à venir comprises, comme la barre
(`statsRythme` : pause tenue et heures > 0). Pour le client : 1 380, 32,
6.

Aucun débordement à 320, 390 et 1280 px. Les quatre sorties du
vérificateur sont identiques à l'octet.

### L'année et ses pauses d'un seul tenant (22/10/2026, v966)

Le client, sur la capture de la v965 : « combiner année et mes pauses ».

**L'ordre du héros devient :**

1. le prochain poste, avec le week-end libre et le prochain congé ;
2. « Ma semaine » ;
3. un seul bloc pour l'année : son titre et « 130 prestées · 40 à
   venir », la barre par pause, le tableau des pauses, puis les trois
   chiffres (heures, en week-end, fériés travaillés).

**Pour le tableau** : il perd son titre « Mes pauses » et sa légende
« année 2026 », qui redisaient le titre du bloc. « Mes pauses » devient
l'en-tête de sa colonne : « Mes pauses · prochaine ». Sous 360 px, il ne
reste que « prochaine » : il passait sur deux lignes à 320 px.

**Pour le code** : « Ma semaine » a son propre conteneur (`#ryAn`), et
l'année, le tableau et les chiffres le second (`#ryPr` : `ryAnneeHTML`,
`ryProchainesHTML`, puis `ryChiffresHTML`, tirée de `ryAnneeHTML`).

**Au PC**, de 761 à 1599 px, le prochain poste et « Ma semaine » sont à
gauche, le bloc de l'année à droite, avec ou sans polyvalences. Mesuré :
colonne de gauche 467 px, droite 333 px pour un opérateur polyvalent. Dès
1600 px, les trois colonnes restent celles d'avant.

Aucun débordement à 320, 390 et 1280 px. Les quatre sorties du
vérificateur sont identiques à l'octet.

### « Mes congés » dans le héros (22/10/2026, v967)

Le client : « ajouter les compteurs de congés disponibles de façon pro et
intuitive dans le héros ».

**Où.** Sous « Ma semaine », donc à gauche au PC, sous le prochain poste.
Le prochain congé est juste au-dessus.

**Ce que le bloc montre.**

- Un titre « Mes congés », et à droite le total à placer (« 1,5 j à
  placer »).
- Une case par compteur du classeur, les mêmes que « Mes compteurs »
  (`soldesConges` : VA, RTT, DTT, RJF), avec :
  - le code ;
  - ce qui reste à placer, en jours et en grand ;
  - une barre de ce qui reste, pleine en début d'année, vide une fois
    tout placé ;
  - « sur N j » en dessous.
- Un compteur épuisé reste, en gris, avec « tout placé » : on voit qu'il
  n'y a plus rien.
- Rien ne s'affiche si l'année n'a pas de soldes fiables (`soldesSaisis`,
  donc pas en 2027 tant que le client ne l'a pas dit).
- Une case touchée mène au détail, la carte « Mes compteurs ».

**Mesuré.**

- Pour le client : VA, DTT et RJF tout placés, RTT 1,5 j sur 8,5.
- Pour un opérateur : 11,5 sur 20, 5,25 sur 6,5, 72,13 sur 72,13, 10 sur
  10. Ce sont les 577 h de DTT écrites dans son classeur. Ce n'est pas une
  erreur de lecture : « Mes compteurs » dit la même chose.

**Mise en page.**

- Quatre cases sur une ligne, même à 320 px. Les chiffres sont réduits
  sous 420 px : « 72,13 j » passait sur deux lignes.
- Aucun débordement à 320, 390 et 1280 px.
- Les quatre sorties du vérificateur sont identiques à l'octet.

### « Mes congés » en heures, l'équivalent en jours, et le flex time (22/10/2026, v968)

Le client, sur la v967 : « sur 8,5 ? Et il faut afficher le solde des FT
(sans les bornes) et indiquer l'équivalent en jour de congé des congés
restants ».

**« Sur 8,5 ».** C'était son droit RTT de l'année, 68 h, converti en
jours. La case disait « 1,5 j / sur 8,5 j » : on ne savait pas de quoi
était fait ce « sur ».

**Ce qui change.**

- Chaque case donne le reste en heures, comme le classeur (« 12 h »), et
  dessous l'équivalent en jours, « ≈ 1,5 j ». La journée est celle de
  l'onglet Barèmes (`hJour`, 8 h par défaut).
- Le droit n'est plus écrit : la barre du reste suffit, et le détail est
  dans « Mes compteurs ».
- Le titre dit « 12 h à placer · ≈ 1,5 j ».
- **Flex time** : une cinquième case donne le solde de la case « Total »
  du classeur (`soldeFTClasseur`, comme « Mes compteurs »), signé, avec son
  équivalent en jours. Elle n'a ni jauge ni bornes, comme demandé, et n'entre
  pas dans le total à placer. Un solde négatif s'écrit en rouge.

**Mesuré.**

- Le client : VA 0 h, RTT 12 h ≈ 1,5 j, DTT 0, RJF 0, FT 0 h.
- Un opérateur : 92, 42, 577, 80 h, et FT +14 h ≈ +1,75 j.
- Cinq cases sur une ligne à 320 px, les chiffres réduits sous 420 px.
  Aucun débordement à 320, 390 et 1280 px.
- Les quatre sorties du vérificateur sont identiques à l'octet.

### La barre du flex time (22/10/2026, v969)

Le client : « efficace, barre dans FT aussi ». La case FT avait sa place
de barre, cachée. Elle se remplit désormais du solde rapporté au plafond de
104 h de la note de service. Les bornes ne sont pas écrites, comme demandé
la veille. La barre est en bleu, pour la distinguer des congés (vert).
Elle est vide à 0 h ou en négatif : le chiffre, rouge, le dit.

Mesuré : +14 h donne 13 % de barre. Aucun débordement à 320, 390 et
1280 px. Les quatre sorties du vérificateur sont identiques à l'octet.

### Le billet du prochain poste repensé (22/10/2026, v970)

Le client : « pas satisfait du premier cadre, prochain poste, et de son
contenu ».

**Défauts relevés sur sa capture.**

- « Aujourd'hui » en pastille et « Jeudi 22 octobre » en titre disaient
  deux fois le jour.
- Un trait gris vide reliait 21 h 30 et 6 h : hors du poste, il ne
  mesurait rien.
- « Contremaître » redisait la fonction écrite sous le trigramme.
- On ne savait pas dans combien de temps le poste commence.

**Le billet désormais.**

- Le titre est en mots quand c'est aujourd'hui ou demain (« Ce matin »,
  « Cet après-midi », « Ce soir », « Demain matin »…), la date en entier
  sinon.
- La pastille donne le compte à rebours jusqu'au début (« dans 7 h 10 »,
  « dans 40 min », puis « Demain » ou « dans N j »), et « Encore … »
  pendant le poste.
- Sous le titre : les heures (« 21 h 30 – 6 h ») et la durée en pastille
  (« 8 h 30 »). La date vient en dessous si le titre est en mots.
- La barre de progression n'apparaît que pendant le poste.
- L'atelier ne s'écrit que s'il diffère de la fonction sous le trigramme
  (`role`). Un opérateur à son poste habituel ne lit plus que « CM GPS »
  et ses collègues. Le marquage d'un changement de poste proposé
  (`marquerTransfertsHeros`) remplit toujours cette ligne.

**Erreur corrigée en cours de route.** `pf-sep` existait déjà, un filet
vertical : mes séparateurs prenaient sa forme. Ils s'appellent `pf-ps`. Et
la date, les heures et la durée sur une seule ligne coupaient « 21 h 30 –
6 h » en deux à 320 px. Les heures tiennent maintenant leur propre ligne.

Mesuré pour un contremaître avant sa nuit, et pour un opérateur en poste,
à 320, 390 et 1280 px : aucun débordement. Les quatre sorties du
vérificateur sont identiques à l'octet.

### Toucher « Accueil » quand on y est (22/10/2026, v971)

Le client : « si tu es sur l'accueil et que tu appuies sur le bouton
accueil, l'affichage bugge une fraction de seconde, alors que sur les
autres onglets non ».

**Cause.** `setView` relançait `renderCompteurs` et `renderRythme`, qui
reconstruisent tout le héros. « Ma semaine », l'année et les pauses se
remplissent en différé (`plusTard`) : leurs blocs retombaient vides un
instant, la page rétrécissait puis se regonflait.

**Correctif.** Dans l'écouteur de la barre d'onglets, toucher Accueil
quand on y est remonte en haut en douceur et ne reconstruit rien. Les
autres appels à `setView` (connexion, données reçues) ne changent pas.

**Mesuré.** Avec un observateur des changements de la page :

- avant le correctif, 15 modifications de la page au toucher ;
- après, 0, et la page est revenue en haut (`scrollY` 0) ;
- le retour depuis un autre onglet reconstruit toujours l'Accueil (4
  lignes de pauses), sans erreur.

Les quatre sorties du vérificateur sont identiques à l'octet.

### Moins de cadres sur l'Accueil (22/10/2026, v972)

Le client : « les chiffres dans le bas du héros sont inutiles. Le cadre
des compteurs inutile aussi vu que c'est repris dans le héros. Prochain
week-end libre et congé doivent être séparés du poste actuel ».

**Les trois chiffres** (heures, en week-end, fériés travaillés, v965)
sont retirés, avec leur style (`ryChiffresHTML`, `.pf-kp`).

**Le cadre « Mes compteurs »** est retiré de la page. `renderCompteurs`
et ses deux appels sont supprimés aussi. « Mes congés » du héros le
reprend : ses cases ne mènent plus nulle part et ne sont donc plus des
boutons. Au PC, le calendrier prend toute la largeur. `compteursCalcules`
reste : le vérificateur (`--compteurs`) et la paie s'en servent.

**Le week-end libre et le prochain congé** ont leur propre cadre, neutre
(gris, et non bleu comme le poste), sous celui du prochain poste.

Mesuré : aucune erreur, aucun débordement à 320, 390 et 1280 px. Toucher
« Accueil » sur l'Accueil ne modifie toujours rien (0 changement de la
page). Les quatre sorties du vérificateur sont identiques à l'octet.

### « À portée de main » resserré (22/10/2026, v973)

Le client, capture du cadre : « optimiser ? ». Les défauts relevés :

- « tout est à jour » en titre, puis « ✓ Rien ne vous attend » dans une
  case en pointillés, sous un titre « À faire » : trois fois la même
  chose ;
- quatre sous-titres de raccourci ne disaient rien de plus que le nom
  (« formulaire RH », « aujourd'hui », « 2026 », « abonnement ») et
  allongeaient la case d'une ligne.

**Ce qui a été fait.**

- La section « À faire » n'apparaît que s'il y a quelque chose à faire.
- Ce qui est en route garde son titre (« En route »).
- Sans compte, le cadre dit toujours de se connecter dans Réglages.
- Un raccourci n'a plus de sous-titre que s'il apporte un état : « 1 en
  cours », « 1 en route », le mois de la fiche de paie.

Mesuré : aucun débordement à 320, 390 et 1280 px. Les quatre sorties du
vérificateur sont identiques à l'octet.

### Congés et recyclages dans un seul onglet « Demandes » (22/10/2026, v974)

Le client : « demandes de congés et recyclage doivent être dans le même
onglet et on peut choisir l'un ou l'autre ».

**Les menus** (barre de gauche au PC, « Plus » au téléphone, menu de
l'espace) n'ont plus qu'une entrée, « Demandes ». Son nombre à traiter
additionne les congés et les fiches de recyclage (`wsNbDemandes`).

**La section** garde ses deux contenus (`demandes`, `recyclages`, marquée
`sous:1` et absente des menus). En tête, dans l'ordre :

1. le titre « Demandes » ;
2. un sélecteur Congé · Recyclage, chacun avec ce qu'il a à traiter
   (`dmBasculeHTML`) ;
3. la phrase qui dit ce que fait le type choisi, et son bouton
   (« + Nouvelle demande », « + Nouvelle fiche », `dmIntro`).

« Demandes » reste en surbrillance dans le menu quand on est sur
Recyclage (`wsActif`). Les raccourcis de l'Accueil (« Demander un congé »,
« Fiche de recyclage ») et les notifications ouvrent toujours le bon type.

Éprouvé au navigateur à 390 et 1280 px : bascule dans un sens puis dans
l'autre, sélection et menu justes, aucun débordement ni erreur. Les quatre
sorties du vérificateur sont identiques à l'octet.

### Le sélecteur dans la barre de titre (22/10/2026, v975)

Le client : « le sélecteur doit être au-dessus des demandes ». Le
sélecteur Congé · Recyclage prend la barre de titre de la section
(`dmTete`), à la place du titre « Demandes », que le menu dit déjà. Tout
le reste vient dessous.

**Erreur corrigée en route.** Au téléphone, la règle de la barre
(`.ws-tete>div` : colonne flex centrée) empilait les deux boutons l'un
sur l'autre. Le sélecteur y retrouve sa grille à deux colonnes, avec une
règle plus précise.

Éprouvé à 390 et 1280 px : bascule dans les deux sens, aucun débordement,
aucune erreur. Les quatre sorties du vérificateur sont identiques à
l'octet.

### Le jour d'une demande se choisit dans notre calendrier (22/10/2026, v976)

Le client, capture de la feuille : « lors du choix du premier jour de
congé, cela met toujours aujourd'hui sans rien faire, il ne faut pas ».

**Cause.** La cellule de date était un `<input type="date">` invisible
posé sur la case. L'iPhone y inscrit la date du jour dès que son
sélecteur s'ouvre ; l'évènement `change` remplissait alors la ligne
(aujourd'hui, VA) avant tout choix.

**Correctif.** La cellule est un bouton (« choisir », en italique, tant
qu'elle est vide). Il ouvre `dmChoisirJour`, un mois de calendrier :

- la pause prévue est écrite sous chaque date ;
- un repos ne se choisit pas, ni un jour déjà sur la feuille (« pris »),
  ni un jour de plus de 31 jours (la base le refuse) ;
- ‹ › changent de mois ;
- « Retirer la date » vide la ligne ; « Annuler », Échap ou un toucher à
  côté ne changent rien.

Rien n'est écrit tant qu'un jour n'est pas touché. Ensuite, la ligne se
remplit comme avant (pause prévue, VA par défaut). La période « Du … Au »
garde ses champs date : on la remplit exprès, avec le bouton « Remplir
les lignes ».

Éprouvé à 390 et 1280 px. À l'ouverture de la feuille, les lignes
disent « choisir ». Le calendrier d'octobre a 21 jours choisissables sur
31. Un jour touché donne « Lu 05/10 · PM · VA ». Aucune erreur. Les quatre
sorties du vérificateur sont identiques à l'octet.

### Le calendrier du choix montre l'état des journées (22/10/2026, v977)

Le client, sur la v976 : « le calendrier ne montre pas l'état actuel des
journées (si on est déjà en congé ou pas) et les journées de repos peuvent
être sélectionnables ».

**L'état réel des journées** (`dmEtatJour`) :

- un congé ou une récupération écrits dans le classeur (CP, RJF, VA…)
  s'affichent en vert, avec leur code ;
- une absence ou un arrêt, en rouge ;
- un jour déjà dans une demande en attente, en jaune pointillé
  (« demandé ») ;
- ces jours-là ne se choisissent plus ;
- une partie de journée (« 2h RHS », « 1/2 VA ») se montre aussi, mais le
  reste de la journée se demande encore ;
- une légende sous le mois les nomme.

**Les repos** se choisissent désormais : « repos » sous la date, cadre en
pointillés.

Mesuré sur la feuille du client, en octobre : CP les 5-7, 2h RHS le 14
(choisissable), RJF les 23-25 et 28-29, VA le 30, tous en vert ; les
repos choisissables. Aucune erreur. Les quatre sorties du vérificateur sont
identiques à l'octet.

### Le haut de page descendu de 12 px au téléphone (22/10/2026, v978)

Le client, capture de l'Accueil : « sur mobile les cadres du haut sont un
peu dans le flou, il faut les descendre très légèrement ». Le haut du
héros tombait dans le flou que l'iPhone pose sous la barre d'état. La
marge du haut de page (`.wrap`, ≤ 760 px) passe de « encoche + 16 px » à
« encoche + 28 px ». La bande opaque reste écartée, comme le client l'a
demandé le 20/10. « Du jour » garde sa marge : la vue doit tenir sans
défilement.

Aucun débordement à 320, 390 et 1280 px. Les quatre sorties du
vérificateur sont identiques à l'octet.

### « Demandes » repris en entier (22/10/2026, v979)

Le client, captures des deux côtés : « optimise cela 100 % pro ».

**Défauts relevés :**

- deux paragraphes de trois lignes avant toute action ;
- « + Nouvelle fiche » en bouton fantôme pleine largeur pour un
  contremaître (`btnlike` quand `peutSaisir`) ;
- une carte qui redisait l'onglet (« Ma fiche ») et le sélecteur
  (« RECYCLAGE · FERMENTATION » en capitales) ;
- la date coupée en deux lignes (« Me 21 oct. 2026 · / PM ») ;
- des boutons longs (« Ouvrir la fiche pour confirmer ») ;
- « Aucune demande. » collé au bord haut de sa carte.

**Ce qui a été fait :**

- une phrase par côté (« Le remplaçant signe, puis le contremaître et la
  RH visent… », « Le contremaître de la pause confirme… ») ;
- le bouton principal est plein, à la couleur du sélecteur, pour tous ;
- la tête des cartes : à soi, le poste ou la période en gras, puis la date
  en entier ou le formulaire dessous, l'état à droite ; d'un autre, la
  personne puis cette ligne ;
- les boutons d'action sont courts (« Signer » · « Viser » · « Confirmer »
  · « Contresigner » · « Valider » · « Voir la fiche ») et alignés à
  droite ;
- une liste vide est centrée dans sa carte.

Éprouvé à 320, 390 et 1280 px avec une fiche et une demande simulées :
aucun débordement, aucune erreur. Les quatre sorties du vérificateur sont
identiques à l'octet.

### Le premier cadre de chaque onglet à la même hauteur (22/10/2026, v980)

Le client : « sur mobile, tous les premiers cadres des onglets doivent
être à la même distance du bord haut que pour l'onglet planning du
jour ».

**Mesuré à 390 px, du haut de l'écran sous l'encoche au premier cadre :**

- Du jour : 16 px ;
- l'Accueil, les Équipes, le Salaire et la Recherche : 28 px (la marge de
  la v978) ;
- Effectifs : 32 px (`.eqcorps` ajoutait 4 px) ;
- la gestion (Demandes…) : 12 px.

**Correctif.** Partout « encoche + 16 px », comme « Du jour » :

- la marge du haut de page revient à 16 px ;
- le premier bloc d'Effectifs perd ses 4 px ;
- une section de la gestion prend 16 px au lieu de 12.

La v978 (+28 px, pour sortir du flou de la barre d'état) est donc
défaite : la référence choisie par le client est « Du jour ».

Remesuré : 16 px pour les huit vues. Aucun débordement à 320, 390 et
1280 px. Les quatre sorties du vérificateur sont identiques à l'octet.

### Tous les premiers cadres à « encoche + 28 px » (22/10/2026, v981)

Le client, deux captures (la v979 encore installée) : « l'écart est bon
sur les Équipes, un peu trop haut dans le planning. Adapter pour tous les
premiers cadres sur mobile ».

**Erreur commise.** À la v980, j'avais pris « Du jour » (16 px) pour
référence, parce que le client l'avait nommé. Ce qu'il voulait, c'était
la même distance partout, et la bonne était celle des Équipes (28 px). Sur
ses captures, le premier cadre de « Du jour » est 12,5 points plus haut
que celui des Équipes. Ce sont les 12 px qui séparent 16 de 28.

**Correctif.** « Encoche + 28 px » partout : la page (`.wrap`), la vue
fixe « Du jour », les sections de la gestion. Effectifs garde le retrait
de ses 4 px de trop.

Remesuré : 28 px pour les huit vues. « Du jour » tient toujours sans
défilement à 390 × 844, 375 × 667 et 320 × 568. Les quatre sorties du
vérificateur sont identiques à l'octet.

### Les règles du recyclage hors de la fiche (22/10/2026, v982)

Le client : « l'explication des recyclages doit être en dehors de la
demande de recyclage et ça doit faire professionnel ».

**Avant.** Le haut de la fiche papier recopiait, en bleu, le paragraphe
des règles et les quatre conditions de la doublure. Cela faisait une
dizaine de lignes avant le premier champ.

**Désormais.**

- La fiche commence par « Membre du personnel de Production ».
- Les règles sont dans un encadré de l'application, au-dessus de la
  fiche (`rcReglesHTML`). Il est replié sur l'essentiel : « Règles du
  recyclage · 10 jours de présence sur poste · du 1er février au 31
  janvier ».
- Déplié, il range les mots du dossier RH en quatre points (« Pourquoi » ·
  « Combien » · « Comment » · « Fiche »), puis la liste des conditions cumulatives de
  la doublure.
- Le texte est celui du papier ; seul « doit être informé » devient « est
  informé ».

**Erreur corrigée en route.** Le panneau est une colonne flexible :
l'encadré y rétrécissait jusqu'à un simple trait. `flex:none` le garde
entier.

Éprouvé à 390 et 1280 px : replié et déplié, aucun débordement, aucune
erreur. Les quatre sorties du vérificateur sont identiques à l'octet.

### La feuille de demande : type centré, pause sans flèche, initiales, flex time (22/10/2026, v983)

Le client : « dans les demandes, le type de congé pris doit être centré,
et pour les changements de pause il ne faut pas la flèche devant la
pause. Pour les remplaçants il faut juste les initiales. Il faut aussi
ajouter le FT au type de congé ».

- **Centré.** La colonne « Type de congé ou Modification pause » est
  centrée : la liste à remplir, la feuille en lecture, et la colonne
  « Demandé » des cartes.
- **Sans flèche.** « → AM » devient « AM » dans la liste, et « Modif.
  pause → N » devient « N » sur la feuille en lecture : l'en-tête de la
  colonne dit déjà ce que c'est.
- **Initiales.** La liste des remplaçants ne montre que le trigramme ; le
  nom ne s'ajoute plus.
- **Flex time.** Les reprises (« 1h -FT » à « 8h -FT ») s'ajoutent aux
  types demandables. Côté base, `base/19-flex-demandable.sql` (appliqué)
  élargit `code_demandable`. Contrôlé : « 8h -FT » est accepté, « 8h +FT »
  (heures prestées en plus) et « MAL » sont refusés. `dmCompteur` range
  ces codes sous « FT ».

Éprouvé au navigateur : la liste des types vaut « VA · RTT · 8h -FT · AM ·
PM · D », les remplaçants « BBZ · CJD · DWS… », alignement centré. Aucune
erreur. Les quatre sorties du vérificateur sont identiques à l'octet.

### Deux types de congé, l'heure de départ ou d'arrivée, remplaçant centré (22/10/2026, v984)

Le client : « le trigramme du remplacement centré aussi, et il faut pouvoir
mettre deux sortes de congé, et si on quitte ou arrive plus tôt, le
préciser ».

- **Remplaçant centré**, comme le type : dans la feuille à remplir, sur la
  feuille en lecture et dans les cartes.
- **Une rangée de précision** sous chaque jour de congé de la courte durée
  (`ligne()`, redessinée avec sa ligne par `remettre()`) :
  - « + autre type » : un second type demandable, différent du premier ;
  - « horaire complet / quitte à / arrive à », puis l'heure, au quart
    d'heure. Une liste et non le champ heure du téléphone, qui aurait
    inscrit l'heure courante d'office, comme la date le faisait.
- **Partout où la demande se lit** : « 4h RTT + 4h -FT » et « quitte à
  18 h 00 » sur la feuille et dans les cartes. Les heures et les compteurs
  de la carte comptent les deux types.
- **Base** : `base/20-deux-types-heure.sql`, appliqué.
  - `biowanze_demander_formulaire` accepte `code2` (demandable, différent du
    premier, courte durée seulement), et `part` ('quitte' ou 'arrive')
    avec `heure` (HH:MM).
  - `biowanze_decider_demande`, à l'acceptation, garde le premier code en
    annotation, celui que lisent le classeur et les compteurs. Le second
    type et l'heure vont dans le commentaire : « Demande n° 12 · + 4h -FT ·
    quitte à 18:00 ».
  - **Écart à confirmer** : on ne connaît pas l'écriture d'une annotation à
    deux codes dans le classeur, donc on ne l'invente pas.

Éprouvé au navigateur : jour choisi, 4h RTT + 4h -FT, quitte à 18:00,
remplaçant. L'envoi part avec `code`, `code2`, `part`, `heure`, `rp` et
`cm`. Aucune erreur. Les quatre sorties du vérificateur sont identiques à
l'octet.

### La précision d'un jour dans une fenêtre (22/10/2026, v985)

Le client, capture de la rangée grise de la v984 : « il y a moyen de faire
bien plus professionnel ».

**Le défaut.** Une rangée grise s'insérait dans le tableau du formulaire,
avec trois listes serrées (« + autre type », « arrive à », « 02 h 00 »).
Le tableau perdait sa forme de papier.

**Désormais.**

- Le tableau garde ses dix lignes. Sous le type de congé, un lien discret
  « préciser » apparaît.
- Il ouvre `dmPreciser`, une fenêtre de l'application :
  - le jour en titre et le premier type à droite ;
  - « Second type de congé », une liste avec les libellés (« 4h -FT — Flex
    time, 4 h de moins ») ;
  - « Horaire », un sélecteur Complet · Je quitte à · J'arrive à, puis
    l'heure au quart d'heure ;
  - Annuler, et Valider en plein.
- Une fois rempli, le lien devient le résumé, en gras dans la case :
  « + 4h -FT · quitte à 18 h 00 ».
- Rien ne change pour la base (`base/20`) ni pour l'envoi.

Éprouvé au navigateur : fenêtre, choix, résumé dans la case. L'envoi part
avec `code2`, `part` et `heure`. Aucune erreur. Les quatre sorties du
vérificateur sont identiques à l'octet.

### L'heure de départ ou d'arrivée seulement pour une journée incomplète (22/10/2026, v986)

Le client : « attention que la justification arrivée ou départ plus tôt
ou plus tard n'est logique que si la personne ne prend pas une journée
complète, c'est-à-dire 8 heures ».

**La durée d'un code** : ses heures quand il se compte en heures, en
valeur absolue (« 4h -FT » s'écrit -4 dans la base), sinon une journée,
8 h. Dans l'application, c'est `dmDuree` ; dans la base, `duree_code`.
Mesuré : VA 8, 4h RTT 4, 4h -FT 4, CP 8, RHS 8, un code inconnu 8.

**Ce que la feuille fait :**

- « préciser » n'apparaît que si le premier type fait moins de 8 h. Pour
  VA, RTT, RJF ou DTT, plus rien à préciser.
- Dans la fenêtre, le second type ne propose que les codes qui tiennent
  dans la journée (total ≤ 8 h).
- Si le total atteint 8 h (4h RTT + 4h -FT), l'horaire disparaît. Une note
  le dit : « Journée complète (8 h) : pas d'heure de départ ni d'arrivée à
  préciser ».
- Un type changé pour une journée complète efface le second type et
  l'heure.

**La base** (`base/21-journee-complete.sql`, appliqué) : le déclencheur
`demande_ligne_garde` refuse un second type si le premier fait déjà 8 h,
et une heure si le total fait 8 h. Éprouvé dans un bloc annulé à la fin :

- 4h RTT + 2h rhs avec une heure : accepté ;
- 4h RTT + 4h -FT avec une heure : refusé (« journée complète ») ;
- VA avec un second type : refusé.

Au navigateur : 4+4, horaire caché et note visible ; 4+2, horaire
visible, envoyé avec « quitte à 18:00 » ; VA, plus de lien, envoyé sans
précision. Aucune erreur. Les quatre sorties du vérificateur sont
identiques à l'octet.

### Le week-end libre et le prochain congé retirés (22/10/2026, v987)

Le client : « on peut supprimer prochain week-end libre et prochain
congé ». Le cadre gris sous le prochain poste est retiré, avec tout ce qui
ne servait qu'à lui :

- `prochainConge` et `RX_CONGE_PROCHAIN` ;
- `weekendLibreApres` et `dateLigneHeros` ;
- le calcul du week-end dans `_pfInfos` ;
- les styles `.pf-wes`, `.pf-we` et `.pf-bloc-we`.

« Ma semaine » et « Mes congés », juste dessous, montrent déjà les jours de
congé à venir.

Au passage, le compte à rebours écrit ses minutes sur deux chiffres :
« dans 2 h 05 », et non « dans 2 h 5 », vu sur la capture de contrôle.

Aucune erreur, aucun débordement à 320, 390 et 1280 px. Toucher « Accueil »
sur l'Accueil ne change toujours rien. Les quatre sorties du vérificateur
sont identiques à l'octet.

### Deux modules : « Mes demandes » et « À valider » ; liste et fiche côte à côte sur PC (22/10/2026, v993)

Le client : « il faut bien faire une différence entre le module de demande
et de suivi des opérateurs, et le module de réception et confirmation du
contremaître et RH », puis « sur PC, la partie de droite se divise en 2
parties pour les onglets demande de congé et recyclages ».

- Deux entrées de menu. **Mes demandes** (sections `demandes`,
  `recyclages`) : ses propres congés et fiches, onglets En cours ·
  Historique (· Je remplace), badge = remplacements à signer.
  **À valider** (`valider`, `valider-rc`), seulement pour qui peut
  saisir ou a quelque chose à viser : onglets À traiter · En cours ·
  Traitées, badge = ce qui attend sa signature. Une étiquette en tête
  (« Mes demandes » bleue, « Réception et validation » ambre) dit dans
  quel module on est. Les raccourcis « viser » et « recyclage à faire »
  du centre de contrôle ouvrent À valider.
- Statuts : une demande en attente dit CHEZ QUI elle est (« Chez le
  remplaçant », « Chez le contremaître et la RH », « Chez la RH », « Chez
  le resp. de zone ») au lieu de « En attente ».
- À 1100 px et plus, dans ces quatre sections, le panneau de la fiche
  n'est plus posé par-dessus : il prend la moitié droite
  (`clamp(460px,48%,780px)`), la liste reste visible à gauche, la carte
  ouverte s'entoure de bleu ; sans fiche ouverte, la moitié droite le dit.
  Mesuré à 1280 : liste 248–784, fiche 784–1280, position `relative`.
  Au téléphone, rien ne change (le panneau reste par-dessus).
- Vérifié : 320, 390, 1280 px, contremaître simulé, aucune erreur ni
  débordement ; vérificateur, quatre sorties identiques à l'octet.

### Des cartes qu'on distingue, et le circuit des signatures (22/10/2026, v994)

Le client : « les listes des différentes fiches ne sont pas facilement
différenciables et intuitives », puis « on ne voit pas bien qui fait la
demande, à qui est le tour de signer, et puis la RH ».

- Chaque carte porte à gauche une **tuile de date** (jour, numéro, mois ;
  « 3 j » pour une période) et une **bande de couleur selon l'état** :
  bleu à faire, ambre en route, vert acceptée ou enregistrée, rouge
  refusée ; une demande retirée est estompée. Le type demandé (CA, FT,
  « Changement de pause » ; pour un recyclage, la pause et « doublure »)
  est une étiquette. Les cartes sont groupées par mois. Pour ses propres
  demandes, le titre est le formulaire et la période passe dessous (la
  tuile disait déjà la date).
- La rangée d'étiquettes « Contremaître → RH » devient un **circuit** :
  une pastille par personne, reliées par un trait, en commençant par le
  **demandeur** (« Vous » ou son trigramme, et la date d'envoi), puis
  remplaçant, contremaître, responsable de zone, RH. Chaque pastille dit
  son état : signé ✓, « à son tour » (ambre), « à vous de signer » (bleu)
  quand c'est le lecteur, « ensuite », ou refusé ✕.
- Toute la carte ouvre sa fiche, pas seulement le bouton. Sur PC, en
  liste et fiche côte à côte, le tableau des jours quitte la carte (il
  est dans la fiche).
- Au téléphone (≤ 520 px), l'étiquette d'état de la tête est masquée : le
  circuit dit la même chose, et elle coupait le titre à 320 px. Elle
  reste pour une demande retirée, qui n'a pas de circuit.
- Vérifié : 320, 390, 1280 px, contremaître simulé, aucune erreur ni
  débordement ; vérificateur, quatre sorties identiques à l'octet ; hors
  ligne.

### Sous-effectifs repliables au PC, filet de la barre de titre partout (22/10/2026, v995)

- Le client : « les onglets sous-effectif ne se replient plus ». Au PC
  seulement : la grille en colonnes de « Postes en sous-effectif »
  (`#mqCorps :has(> .mqj){display:grid}`, id + :has) l'emportait sur
  `.mqmois:not(.ouvert)>.mqmc{display:none}`. Le repli prime désormais
  (`!important`). Mesuré : les six intertitres repliables de l'onglet
  Effectifs basculent, à 390 comme à 1280 px (avant : le premier mois de
  #mqCorps restait en grille, replié ou non).
- Le client : « la barre de séparation avec la barre de titre ne
  s'affiche pas sur tous les onglets ». Le filet (`html::before`, z-index
  70) passait sous l'espace RH (95), les feuilles et les panneaux. Mis
  au-dessus de tout (il est inerte, `pointer-events:none`). Mesuré par la
  couleur de la première ligne de pixels : 1280/1280 sur les six onglets,
  les sept sections de l'espace RH, le formulaire et un panneau ouvert.

### Remplaçant → contremaître de pause → RH, et l'heure des signatures (22/10/2026, v995)

Le client : « il manque l'étape de signature du contremaître de pause,
c'est lui qui valide la demande, puis la RH confirme et accepte pour que
cela soit encodé dans l'horaire », puis « redondance de la date du
demandeur ? Il faut l'heure de signature aussi ; au lieu de “à son tour”,
“en attente de signature”, et pour le contremaître “en attente
d'acceptation” ».

- **Erreur de lecture corrigée** : le 21/10, « les contremaîtres et RH »
  avait été lu « dans n'importe quel ordre », et « la demande d'un cadre
  n'attend que la RH ». Rien de cela n'avait été dit. Base :
  `base/23-contremaitre-puis-rh.sql` — toute demande passe par l'étape
  du contremaître, puis la RH ; la RH n'accepte qu'après ; l'étape du
  contremaître se signe par un compte hiérarchie ou un compte RH (les
  seuls comptes validés aujourd'hui sont des comptes RH, dont celui du
  client), la confirmation RH par un AUTRE compte ; un refus se porte à
  l'étape où il est donné. Notifications dans l'ordre : contremaître du
  jour (à défaut, hiérarchie et RH sauf le demandeur), puis la RH quand le
  contremaître a validé, et le demandeur en est averti.
- **Trou de sécurité fermé** (`base/24-role-vide.sql`), trouvé en
  éprouvant : `role_courant()` est NULL pour un compte connecté non
  validé, et `if NULL not in ('rh','hierarchie') then raise` ne levait
  rien. Saisir, annuler une saisie, viser et décider étaient ouverts à
  un tel compte. Les quatre gardes deviennent « rôle vide ou hors liste ».
- Éprouvé dans un bloc annulé, avec quatre comptes fictifs : non validé
  → « réservé aux contremaîtres et à la RH » ; RH n° 1 → étape du
  contremaître (`validee_en_partie`, la liste passe de attend_cm à rien
  pour lui) ; RH n° 1 encore → refusé (« un autre compte ») ;
  contremaître après coup → refusé ; RH n° 2 voit attend_rh et accepte,
  1 jour posé ; notifications dans l'ordre.
- Application : le circuit montre toujours le contremaître. Chaque
  signature porte son heure (« aujourd'hui · 21 h 54 », « hier · … »,
  sinon « 22/10 · … ») ; l'attente est nommée : « en attente de
  signature » (remplaçant), « en attente d'acceptation » (contremaître),
  « en attente de confirmation » (RH) ; pour le lecteur « à vous de
  signer / d'accepter / de confirmer ». Statuts : « Chez le
  contremaître » puis « Chez la RH » ; à faire : « À accepter »,
  « À confirmer » ; bouton et feuille « Accepter et signer » ou
  « Confirmer et encoder ». Recyclage, même circuit : « en attente de
  confirmation / de contresignature / d'enregistrement ».

### Le cadre « Demande de congé » de l'Accueil, et la règle de modification (23/10/2026, v996)

Le client : « il faut optimiser le cadre de la demande de congé, on ne
voit même pas pour quelle pause c'est. Et quelle est la règle pour la
modification ? »

- Chaque demande en cours : la tuile de la date, le formulaire et le type
  demandé (VA, CA…), puis **la pause prévue** (la pastille du planning,
  réduite), les heures, l'heure de départ ou d'arrivée, le remplaçant (ou
  « sans remplaçant ») ; une modification de pause dit « de N à PM ». Le
  circuit dessous. Toute la ligne ouvre la feuille (clavier compris).
- **Erreur trouvée** : `.md-l li` habillait aussi les étapes du circuit
  (des `li`) : chaque étape devenait une case grise (la capture du
  client). Désormais `.md-l>li`.
- La feuille ouverte depuis l'Accueil se refermait aussitôt : à
  l'ouverture de l'espace, le second rendu (les noms arrivés, `relire`)
  repassait par `wsAller`, qui ferme le panneau. `wsAller(s,garder)` ne
  ferme plus rien quand la section ne change pas.
- Au téléphone (≤ 440 px), le circuit se lit de haut en bas, une étape
  par ligne : à 320 px, quatre étapes côte à côte coupaient les rôles.
- **La règle de la modification** (base/13, puis base/16) : le demandeur
  modifie sa demande tant que le contremaître de pause ne l'a pas
  acceptée ; la modification fait une NOUVELLE feuille, que le remplaçant
  signe à nouveau. La suppression, elle, n'est possible que tant
  qu'aucune autre personne n'a signé. **Défaut trouvé** : depuis base/16,
  modifier une feuille déjà signée par le remplaçant l'EFFAÇAIT, et la
  signature disparaissait avec elle, alors que base/13 la gardait
  « annulée, remplacée par la demande n° N ».
  `base/25-modifier-garde-la-trace.sql` la garde ; elle n'est **pas
  appliquée** : le connecteur Supabase demande une confirmation pour un
  corps qui contient « delete » (deux essais, 60 s chacun, rien
  d'appliqué), et la règle est de ne pas la contourner.
- Vérifié : 320 et 1280 px, aucune erreur ni débordement, la feuille
  s'ouvre depuis l'Accueil ; vérificateur, quatre sorties identiques ;
  hors ligne.

### Une seule date par demande, et l'heure de chaque signature sur la feuille (23/10/2026, v997)

Le client : « toujours 2 dates pour la demande et pas d'heure de
signature ». La carte disait « Je 22 oct. 2026 » sous une tuile qui dit
déjà 22 oct. : le résumé de l'Accueil (`mdQuoi`, partagé) remplace la
période sur les cartes de « Mes demandes » et de « À valider » — pause
prévue, heures, remplaçant ; « jusqu'au … » seulement si la période
dépasse un jour. La ligne « 1 jour · 8 h » ne reste que pour qui valide
(elle y porte les compteurs restants). Sur la feuille, chaque signature
dit son heure (`dmSigLe` : « le 23/10/2026 à 0 h 49 ») : demandeur,
remplaçant, contremaître, RH, et la fiche de recyclage ; le champ
« Date: » du formulaire papier garde la date seule.

### Les heures supplémentaires, troisième sorte de demande (23/10/2026, v998)

Le client : « et voici une nouvelle sorte de demande à implémenter
aussi », avec le formulaire « Demande de validation d'heures
supplémentaires » (07.12.2012 - V3 ; texte du PDF encodé par sa police,
chaque caractère décalé de 29 : décodé avant lecture).

- Base : `base/26-heures-sup.sql`, une table à part (`biowanze.heures_sup`)
  et quatre fonctions (demander, liste, viser, retirer), sur le modèle des
  recyclages (base/15). Le circuit est celui du papier : la personne
  demande, le responsable hiérarchique vise. On ne valide que des heures
  déjà prestées (pas de date future). « Travail nécessaire » exige ses
  quelques mots ; « suite à un rappel » le nom du responsable, puis la
  date du rappel au visa. Une restriction et un refus se motivent. Nul ne
  vise sa propre demande. Retirer passe la demande « annulée » (aucune
  suppression). Notifications : le responsable nommé (à défaut la
  hiérarchie et la RH), puis le demandeur au visa ; le lien
  `?vue=heures` ouvre la section.
- Éprouvé dans un bloc annulé (comptes fictifs) : date future, texte
  manquant, visa de soi, rappel sans date, refus sans motif → refusés ;
  approbation avec restriction et refus → passent ; six notifications.
- Application : le sélecteur devient Congé · Recyclage · Heures sup., dans
  « Mes demandes » et « À valider » ; sections `heures` et `valider-hs`.
  La feuille reprend le papier champ pour champ ; l'horaire prévu et le
  responsable d'équipe (le contremaître de la pause ce jour-là) sont
  préremplis depuis l'horaire ; la mention « prime de rappel » apparaît
  dès 3 h en prolongation de pause. Cartes : tuile, durée en étiquette,
  horaire et justification, circuit Demandeur → Responsable. Le centre
  de l'Accueil dit les heures à viser et celles en route.
- Ce que la RH fait ensuite n'est pas sur la feuille : question au client
  (`docs/questions-client.md`). Rien n'est écrit dans l'horaire.
- Vérifié : 320 et 1280 px, remplir, envoyer (195 min, prolongation,
  prime affichée), viser avec restriction ; messages d'erreur ; aucune
  erreur ni débordement.

### Heures supplémentaires : la RH enregistre, HS ou flex time ; les signataires impliqués (23/10/2026, v999)

Les réponses du client aux questions du matin (retirées de
`docs/questions-client.md`) :

- « Après le visa du responsable, la RH doit-elle confirmer ou enregistrer
  la demande, comme pour les congés ? — Oui. » Circuit : demandeur →
  responsable d'équipe (« c'est bien le contremaître de la pause ce
  jour-là ? — Oui ») → RH, qui enregistre ou refuse (motivé), jamais avec
  le compte qui a visé. Sans toucher à la contrainte du statut (il
  faudrait la supprimer) : « approuvee » sans `rh_le` = chez la RH, avec
  `rh_le` = enregistrée.
- « Il faut ajouter l'option HS ou Flex time ; le flex time c'est par
  heure, les HS par quart d'heure. » Colonne `type` ; la base refuse une
  durée HS hors du quart d'heure et une durée FT hors de l'heure entière
  (contrainte `heures_sup_pas`) ; la feuille propose « à prendre en : HS /
  Flex time », les minutes 00, 15, 30, 45 pour les HS, rien pour le FT.
  « Cela permettra d'avoir toutes les heures supplémentaires dont on
  n'avait pas de suivi avant » : chaque liste dit les heures de l'année,
  enregistrées et en cours, HS et flex time à part (les siennes ; à la RH
  et à la hiérarchie, celles de tous).
- « Les 2 contremaîtres impliqués dans une demande de changement de pause
  ne peuvent pas signer leurs feuilles » : celui qui figure comme
  remplaçant sur une demande de congé ne signe ni l'étape du contremaître
  ni celle de la RH (`biowanze_decider_demande`, et l'application ne la
  lui propose plus) ; le demandeur ne signait déjà pas la sienne. « Pour
  les heures supplémentaires de contremaître, le contremaître ne peut pas
  non plus signer sa feuille » : déjà la règle, vérifiée.
- Base : `base/27-hs-rh-et-type.sql` (colonnes, deux contraintes,
  `biowanze_demander_hs` à neuf arguments, `biowanze_liste_hs2`,
  `biowanze_enregistrer_hs`, notifications dans l'ordre ; aucune
  suppression). Éprouvé dans un bloc annulé : HS 70 min et FT 90 min
  refusés ; FT 120 min créé ; RH avant visa refusée ; visa puis
  enregistrement ; le remplaçant contremaître refusé, un autre signataire
  accepté.
- Application : vérifiée à 320 et 1280 px — FT sans minutes, envoi
  `p_type` FT, visa avec restriction, enregistrement RH ; totaux.

### Le responsable d'équipe : un contremaître ou un adjoint ; la feuille au téléphone (23/10/2026, v1000)

Le client, capture de la feuille au téléphone : « moyen d'optimiser
cela ? Et les responsables d'équipe ne peuvent être que les contremaîtres
et/ou adjoints ». (La capture montrait encore la v998.)

- La liste ne propose plus que la catégorie « Contremaîtres de
  production » du classeur (`estCadre` ; onze personnes, six contremaîtres
  et cinq adjoints, soi-même exclu), rangée en deux groupes. Le
  contremaître de la pause ce jour-là reste proposé, avec la mention
  « le contremaître de votre pause ce jour-là ». Le choix devient
  obligatoire : « — la hiérarchie et la RH — » disparaît.
- Base : `base/28-hs-responsable-cadre.sql`, `biowanze_demander_hs` refuse
  un responsable hors de cette catégorie.
- Au téléphone : le sélecteur sombre du thème, la date en pastille grise
  et les cases de durée vides juraient sur la feuille blanche ; tous les
  champs prennent le style du papier (fond crème, trait dessous, 16 px —
  iOS ne zoome plus à la saisie), la durée tient sur une ligne.
- Vérifié à 320 et 1280 px : sans responsable, la feuille le dit ; les
  groupes (5 contremaîtres, 5 adjoints pour un contremaître) ; l'envoi
  porte le trigramme choisi.

### « Optimise au max » : les cartes des trois sortes de demandes (23/10/2026, v1001)

Le client, capture d'une demande de congé au téléphone : « optimise au
max ». Passe entière, à 320, 390 et 1280 px, sur les six vues (Mes
demandes et À valider × congé, recyclage, heures sup.), le script
mesurant débordements et textes coupés (zéro partout).

Défauts relevés et corrigés :
- l'intro prenait trois lignes avant la première demande : au téléphone,
  le nom du module et le bouton tiennent sur une ligne, l'explication ne
  se lit qu'au PC ;
- le tableau Jour/Prévu/Demandé/Remplaçant redisait, pour un seul jour,
  le résumé sous le titre : il ne reste que pour plusieurs jours (la
  feuille le garde toujours) ; « FLI – » disparaît avec lui ;
- l'étape « Contremaître » disait « ensuite » sans nom : elle nomme le
  contremaître de la pause que la demande a gardé ;
- « Voir la feuille / la fiche » faisait doublon avec la carte, qui
  s'ouvre d'un toucher (même sans bouton désormais) ; « Modifier »,
  « Supprimer » et « Retirer » deviennent des liens discrets ; seul le
  geste à faire (« Accepter », « Confirmer », « Viser », « Enregistrer »)
  reste un bouton plein ;
- la carte de recyclage disait le jour trois fois (tuile, « Mercredi 21
  octobre · Nuit », « Nuit · doublure ») et « En doublure de … » une
  quatrième : une ligne, « pause N · en doublure de LCI » ;
- à 320 px, « Heures sup. 1 » débordait du sélecteur : le compteur passe
  en pastille dans le coin du bouton.

Ce qui reste : à 320 px, le circuit vertical renvoie l'heure du
demandeur à la ligne (« aujourd'hui · » / « 10 h 00 ») ; lisible, laissé.

### Audit complet multi-agents, vague 1 : 77 correctifs (23/10/2026, v1002)

Le client : « fais un audit complet multi-agents et multi-skills pour optimiser
tout au maximum, mobile, PC, contenu, design ; je veux la passe la plus
complète ». Douze auditeurs (Accueil · planning du jour et Équipes · Effectifs ·
Salaire · Recherche et Direction · espace RH · demandes · coquille · design avec le
skill ui-ux-pro-max · contenu · accessibilité · performance), chacun à 320, 390 et
1280 px sur un banc commun (base simulée), puis un sceptique par zone qui a
reproduit chaque constat : 108 retenus, 34 rejetés. Vague 1 : neuf agents,
chacun dans une copie isolée du dépôt (worktree) avec son serveur, mesure
avant/après de chaque correctif ; neuf patchs appliqués sans conflit sur main.
Vérifié après fusion : syntaxe, vérificateur (quatre sorties identiques à
l'octet aux références prises le même jour sur la version d'avant — la
polyvalence dépend du jour), tous les essais de la session.

**performance** :
- Réseau qui accepte sans répondre : la page installée ne s'affiche jamais
- Premier passage hors ligne après l'installation : aucun horaire en cache
- Le héros d'un contremaître calculait toute la polyvalence sans l'afficher
- L'onglet Équipe : gel de 1,4 s à la première ouverture
- Retour du réseau : le bandeau « Horaire indisponible » restait affiché
- Rien d'autre de cassé autour

**coquille** :
- Le geste « retour » referme la feuille du jour, la fiche personne, la feuille « Plus » et les notifications
- Tablette (761 à 1099 px) : une entrée Gestion et Direction dedans, plus aucun débordement
- Menu latéral du PC : Réglages toujours en vue
- Bandeau du menu la nuit : le poste de la nuit en cours avant 6 h
- Pastille « Hors ligne » centrée sur le contenu au PC
- Clavier : les flèches passent par « Plus » et sautent les onglets cachés ; la feuille Plus garde le focus
- Pastille « À valider » et « Demandes » en orange dans la feuille Plus
- « Aller au contenu » inerte sous l'écran de connexion et les feuilles
- Titre de l'onglet du navigateur selon la vue, et titre h2 caché dans le Planning
- Notifications refusées : le message ne parle plus du téléphone au PC
- NON FAIT — Vérification sur un vrai téléphone (pointeur tactile) du message des notifications : Playwright émule un pointeur fin à toutes les largeurs. Seule la branche « navigateur » a été vue au navigateur ; la branche « téléphone » est le texte d'origine, inchangé.

**accueil** :
- « Revenir en haut » et « Aujourd'hui » (vue Année) ne s'arrêtent plus net
- Bilan du mois : l'écart « Week-end » est maintenant en heures
- « En route » : une demande de flex time n'est plus affichée comme « Heures sup. »
- La vue Année s'ouvre sur le mois affiché
- « Jour par jour » : les jours à venir sont pâlis
- Mes congés : équivalent en jours au dixième, et « à zéro » pour un solde FT nul
- Petit téléphone : l'en-tête et la pastille des prochaines pauses ne descendent plus sous 10,5 px
- Au PC, plus de vide sous « Mes pauses » dans le héros
- Demande de congé : les deux cibles tactiles font maintenant 40 px
- NON FAIT — Petit téléphone : abréger le jour de la date des prochaines pauses (« Dim. 1 novembre ») : Ce serait revenir sur une décision du client. Il a demandé le jour écrit en entier (« jour écrit en entier, et le mois aussi », journal 05-interface.md l. 2690-2699 ; commentaire « la date en entier, comme le prochain poste (le client, le 22/10/2026) » dans ryProchainesHTML). À 320 px, « Dimanche 1 

**jour-equipes** :
- Planning du jour : la ligne AM / PM / N et « Auj. » restent collées en haut quand le jour défile
- Équipes : l'en-tête des polyvalences colle, et celui des adjoints (CM) prend sa place
- PC : les flèches ← → changent de jour au Planning
- Les badges commentés et les « ? » se prennent au clavier
- Bouton « Auj. » : zone de toucher agrandie sans changer le dessin
- Date du Planning : le sélecteur couvre toute la barre
- Équipes au PC : les cartes des binômes et de la formation ont la même hauteur
- NON FAIT — Polyvalences à 320 px : l'en-tête « CHAUD. » est coupé : Le correctif retenu ne change rien. À 320 px, la règle existante `@media (max-width:360px){ html .pvt thead th{letter-spacing:0} }` met déjà l'espacement à normal, et .pvt th a déjà 2 px de marge intérieure. Les styles calculés le montrent : letter-spacing normal, padding 2px, 44/40. J'ai essayé plu

**effectifs** :
- Au PC, « Rien à signaler » des changements de poste est maintenant centré
- L'en-tête d'une journée s'atteint au clavier et ouvre le Planning du jour
- Absents et congés au PC : plus de filet de 1 px au-dessus de la 3e (et 4e) case
- Jamais « +1 autre rappel possible » : le 9e rappel s'affiche
- États vides : « d'ici la fin de l'année » au lieu de « d'ici la fin de l'horaire »
- NON FAIT — Étendre l'horizon des sous-effectifs et des rappels évitables à 2027 : Cela touche aux compteurs et aux places annoncées, et COMPTEURS_FIABLES ne contient que 2026. Le correctif retenu demande d'abord d'écrire la question dans docs/questions-client.md, et la consigne interdit de toucher à docs/. Je n'ai donc changé que le texte des états vides. La question est à poser 

**salaire** :
- Comparer avec ma fiche : l'écart signé se lit au téléphone
- Saisies du mois rangées en groupes, réglages des heures sup. masqués sans heures
- Au PC, la molette ne change plus la valeur d'un champ numérique actif
- Virgule décimale lue quelle que soit la langue du navigateur
- Relevé de prestations : l'en-tête « HORAIRE » tient dans sa colonne
- Fiche simulée : le « ? » ne part plus seul à la ligne
- Le « ? » de la fiche simulée se voit aussi à la souris
- Champs vides des Saisies du mois : la valeur que le calcul prendra est montrée en grisé

**recherche-direction** :
- La Recherche lit l'horaire 2027 (et le dit pour une année sans classeur)
- Période de plus de 62 jours : un avis
- Comparatif par statut et Intérimaires à 320 px
- Polices de Direction : de 9,5 et 10 px à 11 px
- « Équipe 5 » au lieu de « Shift 5 » dans « Nuits par équipe »
- Pas de filet ni de vide de 30 px sous « ‹ Direction »
- En-tête de la Recherche en colonne
- Cibles de 44 px pour « ‹ Direction » et la bascule Toutes / Hors longues maladies
- Accueil de Direction : des rangées pleines
- Pli « Vue direction » caché aux comptes non RH, gardé sans compte
- Graphiques par mois de Direction : les mois à venir sont grisés (mesure d'attente)
- NON FAIT — Définition du taux d'absentéisme (à date ou sur l'année planifiée) : L'audit lui-même demande de ne pas trancher : c'est un chiffre montré à la RH. La question doit être écrite dans docs/questions-client.md (« taux d'absentéisme du 1/01 à aujourd'hui, ou sur l'année planifiée ? »), et la consigne m'interdit de toucher à docs/. Seule la mesure d'attente est faite : gr
- NON FAIT — Repli des journées « Remplaçable » dans un <details> sur une période (page de 4 135 px) : L'audit le donne comme facultatif. Le style des journées et du bilan de la Recherche fait l'objet de décisions du client (06-effectifs-et-recherche.md) : replier par défaut ce qu'il a voulu voir en clair reviendrait sur sa manière de lire. Seul l'avis de coupure à 62 jours, la priorité, est fait. La

**espace-rh** :
- Horaire production au téléphone : une seule rangée de pilules qui défile
- La feuille de saisie passe au-dessus de « Adjoints » et des boutons ronds
- La recherche de l'Horaire production parcourt toutes les feuilles
- Tableau de bord : la carte « Demandes à traiter » compte la même chose que « À valider »
- Personnel et Absences au PC : l'en-tête des colonnes reste à l'écran
- Au téléphone, la case touchée reste au-dessus de la feuille
- Absences : l'horizon passe le 31 décembre
- Tableau de bord avant 6 h : le libellé dit la nuit
- Historique au PC : la carte est centrée
- Menu latéral au PC : l'entrée active reste visible

**demandes** :
- Zoom de l'iPhone à la saisie (feuille de congé, recyclage, visa, « Remplir une période »)
- Cibles du tableau de congé au téléphone
- Les deux GBT se distinguent dans les listes de choix
- « aujourd'hui » et « hier » faux entre 0 h et 6 h
- La case Remplaçant invite au choix
- Liste des remplaçants en deux groupes
- Cartes ouvrables au clavier
- Décision du visa aussi dans la barre du bas (congé et heures sup.)
- « Complet » devient « Habituel » dans la fenêtre « préciser »
- Deux textes remontés au plancher de 10,5 px
- Même tête de carte pour les trois sortes de demandes
- NON FAIT — Remplacer les listes Type et Remplaçant par un bouton qui ouvre une liste en fenêtre : C'était l'option forte de l'audit, notée « moyen ». Le correctif minimal (hauteur de 36 px, largeur de 38 px) suffit à 320 px sans débordement, et un changement plus profond du tableau papier toucherait à la forme voulue par le client (v904).


### Audit, vague 2 (design · accessibilité · contenu) et deux réponses du client (23/10/2026, v1003)

Trois agents l'un après l'autre sur main (styles communs), chacun vérifiant
d'abord si la vague 1 avait déjà réglé son constat.

**design** :
- Texte blanc sur le cyan d'accent dans Demandes
- #apCard sans la recette des cadres des Effectifs
- Jetons --cal-am et --cal-pm définis deux fois
- Ombre des cadres recopiée en dur
- Pastille de pause des listes du tableau de bord sous 10,5 px
- Pastilles de nombre du menu latéral : deux typographies
- déjà fait par la vague 1 — « Rien à signaler » décentré dans #apCard au bureau : déjà corrigé par la vague 1. #apCorps ne passe en grille que s'il contient des .mqj (#apCorps:has(> .mqj)). Mesuré à 1280 px : écart des centres d
- NON FAIT — Sélecteurs segmentés : unifier trois recettes : Le défaut est seulement esthétique, et aucun sélecteur n'est illisible depuis que .dm-bascule a l'encre --sur-in. Aligner .seg, .pl-seg et .dm-prec-seg sur .caseg changerait le rendu de quatre composants sur plusieurs écrans, alors que .caseg passe en grille à 320 px. Il faudrait photographier chaqu
- NON FAIT — Couleur des boutons principaux portée par une seule règle .btn.primary : Le défaut visible (#fff sur l'accent) est corrigé : toutes les copies portent maintenant var(--sur-in). Retirer les trois propriétés de 7 règles de spécificités différentes (html #grille .dm-intro>button, .pn-pied .ss-ok…) risque de laisser une règle intermédiaire gagner la cascade, sans gain visibl
- NON FAIT — Horaire des badges du Jour (.eqhd) à 10,5 px au téléphone : Le correctif proposé (l. « .eqhote … .eqhd{font-size:9px} », ≤ 760 px) ne touche pas le Jour : la règle #jourCorps, plus forte, y fixe 9 px (8,5 px sous 361 px). Je l'ai mesuré : 8,5 px à 320, 9 px à 390, 10,5 px à 1280. Dans le Jour, le badge a une hauteur fixe de 30 px (28 px sous 361 px), une déc

**accessibilite** :
- Thème sombre : texte blanc sur les accents clairs (coches .dm-pt, pastille « À faire » .ctl-nb)
- Panneau d'une demande ou d'une fiche : rôle dialog, focus et inert au téléphone
- Cibles de 44 px : « + Nouvelle » et « Historique » (carte Mes demandes), « Modifier », « Supprimer » et « Retirer » (cartes de l'espace)
- Barre du bas au téléphone : anneau de focus
- Espace RH non modal au téléphone
- Annotations rouges de l'Horaire production
- Invites « choisir » de la feuille papier
- Demandes de l'Accueil : une étiquette propre à chaque ligne
- Un seul <main> quand l'espace est ouvert
- Paysage : bords protégés de l'encoche
- Deux défilements doux ignoraient « mouvement réduit »
- déjà fait par la vague 1 — Thème sombre, bascule Congé/Recyclage/Heures sup. et « + Nouvelle demande » : déjà en var(--sur-in) avant mon passage (première vague) ; le balayage au navigateur ne les relève plus.
- déjà fait par la vague 1 — Barre du bas, flèches : le gestionnaire ne garde déjà que les onglets visibles et passe par #tab-plus (première vague). Mesuré : Accueil → Jour → Équipe → Salaire → Plus → Accueil à 320 et 390 px. Seu

**contenu** :
- Barre de gauche entre minuit et 6 h : jour du calendrier au lieu de la nuit en cours
- Carte « Absents aujourd'hui » : répartition « n malades, n en congé »
- « À faire » : sous-titre tiré de la demande au lieu de « remplacement signé » écrit en dur
- Verbes du congé alignés sur les boutons (Accepter / Confirmer)
- Durée des messages flash
- Erreurs de la plateforme traduites dans baseMsg, et la validation des comptes passe par baseMsg
- Sous-effectif : « quinze prochains jours » remplacé par « 14 prochains jours »
- La case FT à zéro pâlit comme un congé tout placé
- « 1er » pour le premier du mois dans les dates longues
- Alerte « Montant d'exemple » du Salaire : ni taux à 4 décimales, ni chemin Réglages
- « Cliquez » au PC, « Touchez » au doigt
- déjà fait par la vague 1 — Mes congés, case FT « ≈ 0 j » : le texte était déjà corrigé dans 53f3c9d (« à zéro ») ; seule la pâleur de la case manquait, je l'ai ajoutée (voir faits).
- déjà fait par la vague 1 — Barre de gauche avant 6 h : correction partielle déjà présente (le poste de la nuit, « N · jusqu'à 6 h ») ; la date restait celle du lendemain, je l'ai complétée (voir faits).

**Les réponses du client** aux deux questions de la vague 1 :
- « Le taux d'absentéisme : c'est sur toute l'année, mais le taux est celui
  de janvier à maintenant. » `dirRH()` compte à part les jours programmés et
  la maladie jusqu'au jour de l'usine (`schedA`, `malA`) : le taux (par
  personne, par équipe, global) en est tiré ; les jours de maladie et la
  maladie par mois restent ceux de l'année planifiée. Mesuré : 7,5 % → 8,5 %
  au 23/10 (l'auditeur l'avait estimé à 8,6 %), 1 463 jours inchangés.
- « Oui » pour étendre les sous-effectifs et les rappels évitables à 2027,
  « mais pas se fier aux compteurs tant que maintenant ». `horaireSuivant()`
  ne prend que le classeur installé ; `mqJoursAVenir`, `rappelsInutiles` et
  `transfertsAVenir` y passent au 1er janvier, chaque jour portant son année
  et son classeur ; les mois se repèrent avec leur année (octobre 2026 et
  octobre 2027 ne se mêlent pas), le nom du mois la dit hors de l'année en
  cours, et un clic ouvre le bon jour. Les compteurs de 2027 restent tenus à
  l'écart par `soldesSaisis()` (COMPTEURS_FIABLES = 2026). Mesuré au 20/12/2026
  (horloge fixée) : 377 jours examinés jusqu'au 31/12/2027 ; le classeur 2027
  n'a aujourd'hui aucun sous-effectif ni rappel évitable (même résultat en
  partant du 10/01/2027). Le vérificateur n'utilise pas ces fonctions : ses
  quatre sorties sont inchangées.


### Direction : aussi ceux qui n'ont pas été absents (23/10/2026, v1004)

Le client, capture du classeur et de la Direction : « GKT n'est pas dans
l'application ? pas d'absence ? », puis « il faut quand même indiquer les
travailleurs qui n'ont pas été absents ». GKT y était (Shift 2, renfort
arrière, 2026 et 2027) mais sans aucun jour « Abs » ni maladie dans le
classeur 2026 ; `dirOpsSub()` ne montrait que les personnes ayant au
moins un jour de maladie. Désormais les absents d'abord (taux
décroissant), puis les autres par trigramme, « 0 % · aucun jour », en vert
discret, dans les listes par équipe et par poste. Mesuré : équipe 2, 13
personnes dont 2 sans absence (avant : 11) ; résumé inchangé (7,1 %,
255 j) ; 390 et 1280 px sans débordement.

### La Direction au style du site (23/10/2026, v1005)

Le client : « la page Direction n'est pas du tout dans le style du site,
j'aimerais qu'elle soit 100 % optimisée ». Workflow en trois temps, dans une
copie isolée : refonte, critique indépendante (12 défauts relevés sur la
refonte), finition.

- Écarts relevés avant : carte sombre à dégradé en dur au lieu de la page et
  de ses cadres ; couleurs en dur (#FF8A7A, #C9D1E0, #6FD6F2…) et barres en
  dégradé ; la mono partout ; titres en capitales grises sans cadre ; tuiles
  hors du style du tableau de bord ; pastilles de pause hors de celles du
  Planning ; bascule en pilules corail ; tableaux en cellules-pilules ;
  « ‹ Direction » en lien de 32 px ; textes à 10 et 10,5 px ; au PC une
  seule colonne étirée.
- Après : chaque section est un cadre des Effectifs (bord, rayon,
  --ombre-cadre, barre de titre centrée) ; tuiles .ws-kpi ; pastilles de
  pause du Planning ; bascule au segmenté .caseg (44 px) ; barres pleines
  aux jetons ; tableaux à filets, nombres à droite en chiffres tabulaires ;
  mono sur les seuls trigrammes ; au PC, deux colonnes, les grands cadres
  sur toute la rangée ; « Vue du jour » a son titre comme les autres
  sous-pages ; jours de la semaine sur deux lignes au téléphone. Seul le
  balisage (dirCadre, dirNav) et le CSS changent : aucun calcul touché.
- Chiffres prouvés identiques : texte des 11 sous-vues à 390 px (hub, jour,
  absences, rappels, rythme, compétences, intérim, statut, et les trois
  « Hors longues maladies ») ; la suite des nombres a la même empreinte
  avant et après (8,5 %, 1 463 j, 515 rappels, équipe 2 à 7,1 %…).
- Mesuré : 320, 390 et 1280 px sans débordement, aucun texte coupé ni sous
  11 px, aucune cible sous 40 px (avant : 8 cibles de 31-32 px, 8 textes à
  10-10,5 px) ; aucune erreur de page ; hors ligne inchangé.
- Laissé : « Hors longues maladies » ne s'affiche que sur Absences (comme
  avant) ; entre 761 et 1099 px la page reste sur une colonne ; les plis
  ouverts des rappels allongent la page (rangées de 44 px).

### Contrôle de non-régression : ce que le grand audit avait abîmé (23/10/2026, v1006)

Le client, la nuit de l'audit : « attention aux régressions, ça ne doit
jamais arriver », puis « contrôler la non-régression, surtout depuis le
grand audit ». Un outil de contrôle (hors dépôt, banc commun) relève
60 vues (20 vues ou sections × 320, 390, 1280 px, horloge fixée, base
simulée) : pour chaque texte, ses lignes, sa taille, s'il est coupé ou
hors de l'écran ; chaque cible ; débordement ; erreurs. Comparé entre la
version d'avant l'audit (6f7bf57) et celle d'après (c64ca8c) : 356 alertes,
cinq causes.

- **Menu latéral du PC** : entrées ramenées de 41 à 35 px sous 900 px de
  haut (un correctif voulait garder Réglages en vue) — rendu à 41 px ; le
  pied collant suffit à garder Réglages visible.
- **Mes pauses à 320 px** : « FAITES » et « RESTE » coupés depuis le
  passage de l'en-tête à 10,5 px — ils débordent maintenant dans l'écart
  entre colonnes (un premier essai, colonnes élargies, faisait passer
  « Vendredi 6 novembre » sur deux lignes : le contrôle l'a vu, annulé).
- **Fiche simulée** : 24 px réservés au « ? » à droite de chaque libellé
  lui faisaient prendre une ligne de plus — le « ? » se pose dans la
  colonne des quantités quand elle est vide, sinon à gauche du montant
  (marge mesurée : 4 px au moins à 320, aucun chevauchement).
- **Acceptés, voulus** : la rangée de filtres de l'Horaire production qui
  défile (la grille a retrouvé sa hauteur) ; les notes du Salaire plus
  longues (elles disent la valeur prise) ; les saisies regroupées ; des
  lignes de la fiche qui tiennent désormais sur une ligne au PC.
- Reste : « Dimanche 1er novembre » sur deux lignes à 390 px, corrigé par
  la seconde ronde (constat de l'Accueil n° 3).

### Le nom « BioWanze » et le nouveau logo (23/10/2026, v1007)

Le client : « j'ai poussé le nouveau logo de l'app. Et le nom doit être
“BioWanze” ». Le nom affiché passe de « BIOWANZE » à « BioWanze » partout
où l'utilisateur le lit : titre de l'onglet et de chaque vue
(« … · BioWanze »), nom de l'application installée (`manifest`, `name` et
`short_name`, et le titre de l'écran d'accueil d'iOS), marque de la barre
du haut et de l'écran de connexion, guide d'installation, nom des agendas
abonnés (`X-WR-CALNAME`, les 79 fichiers de `cal/` régénérés : une ligne
change dans chacun, rien d'autre).

Gardés tels quels, volontairement : l'objet de l'e-mail du code de
connexion (« Votre code BIOWANZE », c'est le texte que l'utilisateur
reçoit réellement, il se change dans Supabase et non ici), le sujet des
e-mails du robot de l'horaire (filtres de la boîte), l'identifiant
`PRODID` des agendas (le changer ferait voir aux agendas un autre
producteur), la fausse barre d'adresse du guide (`BioWanze.app`, déjà
écrite ainsi) et le nom de la société.

Contrôle de non-régression (60 vues, référence v1006) : **0 alerte** ;
un seul texte change par vue au PC, le nom de la marque ; hors ligne
correct, aucune erreur. Le vérificateur du calendrier rend ses quatre
sorties à l'octet.

### La Direction devient un centre de contrôle RH (23/10/2026, v1008)

Le client : « la vue Direction doit être un vrai centre de contrôle
ressources humaines […] un statut complet et des statistiques sur tous
les opérateurs et travailleurs, pour leurs fonctions, leur poste, leur
statut, leur absence, leur congé, les gens présents, les gens malades,
les gens absents […] professionnel et premium ». Démarche : une carte de
ce que l'application sait déjà lire, deux conceptions indépendantes (le
geste de la RH, la lecture des données) notées par un juge (50 contre
48 : la première retenue, six idées de la seconde greffées), la
réalisation, une critique qui a mesuré les tâches réelles de la RH, puis
la finition de ses huit défauts graves et moyens.

- **Trois écrans** sous une barre segmentée : *Aujourd'hui* (choix du
  jour, présents, malades, congé, repos, absentéisme, les quatre pauses
  avec qui manque, « À surveiller » sur sept jours, la répartition sur
  quatre axes, les sept prochains jours), *Effectif* (une ligne par
  personne, recherche sans accents, puces d'état, filtres, sept tris,
  pied de synthèse ; tableau à six colonnes au PC, cartes au téléphone),
  *Analyses* (les six sous-pages d'avant, texte identique à l'octet,
  plus un Comparatif « Par équipe »). Une **fiche par personne** s'ouvre
  par-dessus tout, avec ‹ › pour passer à la suivante dans la liste
  filtrée.
- **Chaque chiffre est un bouton qui ouvre la liste qu'il compte**, et le
  nombre affiché égale toujours le nombre de lignes ouvertes : 830
  boutons parcourus à 390 et 1280 px, aucun écart. Le Retour du
  téléphone ferme la fiche, puis retire le filtre, puis revient à
  Aujourd'hui.
- **Le contrôle des effectifs** : présents + malades + congés + repos =
  tout l'horaire, sinon une erreur et un bandeau. Il mord : une personne
  retirée des repos sur une copie, il crie « 77 personnes rangées sur
  78 ». La lecture du code règle « 14 personnes inexpliquées » d'une
  ancienne carte : chacun tombe dans une seule liste, et le « 7 » de repos
  était faux. **Mesuré** au 22/10 : 40 + 6 + 11 + 21 = 78, et les 21
  repos sont 20 repos lus, 1 poste prévu non presté, 0 journée sans
  entrée.
- **Erreur trouvée par la critique, corrigée** : la fiche titrée « du
  1er janvier au 22/10 » comptait les jours de maladie et les congés de
  TOUTE l'année, jours à venir compris (153 jours pour une personne en
  longue maladie, dont les barres de novembre et décembre). `dirRH`
  calcule désormais, dans la même boucle, les mêmes grandeurs bornées au
  jour de l'usine, sans toucher aux totaux existants : 109 jours à ce
  jour et 44 prévus d'ici le 31/12 font bien les 153 d'avant ; au pied de
  l'Effectif, 1 337 + 126 = les 1 463 jours des Analyses.
- **Tableau du PC sans défilement imbriqué** : il débordait de son cadre
  (1 089 px pour 998) et défilait dans la page. Six colonnes fixes, en-tête
  collé sous la barre : table et cadre égaux de 761 à 1 600 px. Épreuve :
  sur une copie sabotée, le contrôle crie.
- **Les soldes restants** ne se lisent que dans le classeur et seulement
  si `soldesSaisis()` : sur 304 comparaisons, 16 écarts entre la colonne
  du classeur et le calcul de l'espace RH. Avec l'horloge en 2027, la
  colonne disparaît et la page dit « Soldes 2027 non confirmés ».
- Par personne, les congés sont en heures, comme le classeur (« VA 44 h »
  et non « 5,5 j »). Le Comparatif par équipe, lui, garde ses jours,
  comme le tableau des Analyses qu'il prolonge.
- Reste, dit tel quel : le statut « longue maladie » se calcule sur la
  plus longue série de l'année entière, comme dans les Analyses ; les
  périodes de maladie et les RHS de la fiche couvrent l'année, écrites à
  part. Le mot « Absents » diffère entre les Effectifs (malades) et la
  Direction (malades et congés) : question au client n° 9.
- Vérifié : vérificateur, quatre sorties identiques à l'octet ; hors
  ligne, 78 lignes en trigrammes et la note « Noms indisponibles hors
  ligne » ; 320, 390, 761, 900 et 1280 px, 0 débordement, 0 texte sous
  11 px, 0 cible sous 44 px.

### Seconde ronde d'audit, vague A : cinq zones sur sept (23/10/2026, v1009)

La seconde ronde (« optimise tout ») avait retenu 68 constats, dont
25 régressions laissées par la première. Sept agents, un par zone, chacun
dans sa copie ; un patch par zone, appliqué ici par fusion à trois voies.
Cinq zones sont rendues :

- **Performance** : une lettre tapée dans la recherche du planning de l'espace RH
  gelait l'écran ; les rappels évitables passaient l'équipe du jour sur
  435 journées (le mot « rappel » est maintenant cherché avant) ; la bulle
  des sous-effectifs du démarrage faisait une tâche de 1,4 s (téléphone
  simulé, CPU ×4), elle avance au repos, une journée à la fois, et passe
  son résultat aux Effectifs ; la grille de l'année n'est plus refaite à
  chaque retour. Non atteint : la seconde ouverture du planning de l'espace RH reste
  vers 900 ms ×4, c'est la mise en page de 18 000 cellules et non plus
  du JavaScript.
- **Équipes et effectifs** : une date de 2027 dans la Recherche ouvre le
  bon jour ; une seule section « Janvier 2027 » dans Congés et repos ;
  l'anneau de focus des en-têtes de fiche entier ; le focus suit le
  Planning au lieu de tomber sur la page ; la bulle de commentaire est
  annoncée au lecteur d'écran ; les rappels évitables se calculent en
  tranches.
- **Salaire et recherche** : un montant écrit à la belge, « 1.234,50 »,
  était refusé sans un mot et le calcul gardait l'ancienne valeur ; la
  Recherche propose aussi les personnes qui ne sont que dans l'horaire
  2027. Les trois constats de la Direction sont passés au complément du
  centre de contrôle, refondu entre-temps.
- **Accueil** : « Cette nuit » au lieu de « Ce soir » après minuit en
  poste de nuit ; les boutons de la feuille du jour à 44 px ; « Dimanche
  1er novembre » sur une ligne à 390 px (le reste du contrôle de la
  v1006) ; un seul « aujourd'hui » dans la vue Semaine entre 0 h et 6 h ;
  la tuile de la carte de demande dit le même nombre de jours que son
  texte ; « + Nouvelle » reste sur la première rangée à 320 px.
  **Régression rattrapée à la fusion** : pour faire tenir la date, ce
  patch, écrit avant le correctif de la v1006, ramenait sous 400 px les
  colonnes à 34 et 32 px et les dates à 13 px ; le contrôle de
  non-régression a vu « FAITES » et « RESTE » de nouveau coupés à 390 px
  et quatre dates rapetissées. Seize variantes mesurées de 361 à 400 px :
  une seule tient partout, colonnes de 38 et 36 px, écart de 6 px, marges
  de 10 px — la date reste à 14 px et sur une ligne, rien n'est coupé.
- **Coquille** : « Plus » au téléphone ne quitte plus l'espace ouvert ; le
  geste retour des Réglages ne quitte plus l'application ; Échap ferme la
  feuille, puis l'espace, et non les deux d'un coup ; le retour du réseau
  attend que rien ne soit en cours de saisie avant de recharger ; la
  feuille « Plus » ne se fige plus après une rotation.

**La fusion, et l'erreur qu'elle a failli laisser passer.** Deux zones
avaient réécrit `mqJoursAVenir`, chacune à sa façon, pour la même lenteur :
l'une en parcours pas à pas (`mqParcours`), l'autre en mémoire et en
tranches (`mqJoursAVenirTranches`), avec deux fonctions `mqCle` de
signatures différentes. On ne pouvait garder que l'une : la première,
déjà fusionnée et qui alimente la bulle. La fusion avait pourtant glissé
dans la version retenue une ligne de l'autre (`st.premier`, une variable
qui n'y existe pas, une erreur à la première journée) et une accolade de
trop dans `renderManques` : `node --check` a vu la seconde, la relecture
la première. Preuve que rien d'autre n'a glissé : la zone, de
`mqJoursAVenir` aux rappels, est identique à l'octet à celle du patch de
la performance appliqué seul sur la version d'avant. Les deux patchs qui
corrigeaient encore l'ancienne Direction n'ont pas été repris : le
centre de contrôle a son propre cache, calculé une fois par jour.

### Vague A, les deux dernières zones : espace RH et demandes (23/10/2026, v1010)

- **Espace RH** :
  - au téléphone, la feuille de lecture d'une case ne rend plus toute la grille inerte : elle ne couvre que le bas, la grille reste touchable ;
  - le panneau s'annonce par le trigramme ET la date de la case ;
  - l'entrée « Historique » active n'est plus cachée sous le pied « Réglages » ;
  - adjoints et contremaîtres ne sont plus rangés en « Équipe 1 » ou dans l'équipe de leur binôme ;
  - lignes et cases s'atteignent au clavier : une seule case dans l'ordre de Tab, celle du jour, puis les flèches. Les lignes de tableau prennent le focus sans `role="button"`, qui aurait effacé leurs en-têtes au lecteur d'écran ;
  - le tableau du Personnel n'est plus coupé entre 761 et 1099 px ;
  - « Cette nuit » ne coiffe plus, avant 6 h, des quarts finis ;
  - plus de tuile seule sur la seconde rangée du tableau de bord.
- **Demandes** :
  - « Signer et envoyer » sur une feuille incomplète montre l'erreur en vue ;
  - les flèches ← → ne changent d'année qu'au Planning : ailleurs, elles fermaient la feuille ouverte ;
  - le geste retour ferme d'abord le sélecteur de jour ou « préciser » ;
  - Échap, retour ou × sur une feuille en cours de saisie demandent confirmation ;
  - le focus revient où il était après un sélecteur ou un visa ;
  - les champs du visa et du message ont un nom accessible ;
  - `#ppChoix` n'est plus un faux groupe d'onglets.
  Reste, dit par l'agent : changer de section ou toucher une autre carte ferme encore une feuille remplie sans rien demander.
- **Fusion** : six conflits avec la coquille, qui avait corrigé les mêmes endroits.
  - Le titre de l'onglet : un seul `titreVue(v)`, avec la vue restée derrière quand on ne la donne pas.
  - L'inertie : la coquille la règle par `wsAppliquerMode()` (passage du téléphone au PC), l'espace RH par une feuille non modale. Les deux sont gardées : `GR.panNonModal` est lu par `wsAppliquerMode()`.
  - Le clavier : la feuille « Plus » se ferme d'abord, une touche déjà prise ne ferme rien de plus, la confirmation précède la fermeture d'une feuille remplie.
  - Éprouvé au navigateur :
    - case en lecture à 390 px, grille non inerte ;
    - feuille de demande, liste inerte à 390 px, plus à 1280 px, de nouveau à 390 px ;
    - flèche hors du Planning, feuille toujours ouverte ;
    - aucune erreur.

### Vague B, design et contenu (23/10/2026, v1011)

Trois agents, avec la compétence ui-ux-pro-max (le client : « et ui ux pour le design ! »), chacun sur sa zone et dans sa copie.

Zone design et contenu :
- **« 1er »** partout où le mois s'écrit en entier : `dateLongue()`, `dateFr()` (donc « classeur du 1er … »), le Planning du jour, la feuille du jour, la vue Semaine (« 26 octobre – 1er novembre »), Ma semaine, Mon rythme, la légende du tableau du jour, les sous-effectifs à venir, les aria-label des cases. Les formes abrégées gardent « 1 nov. ». Mesuré avec l'horloge au 01/11/2026, avant puis après.
- **Élision** : « la fiche d'octobre », et non « de octobre » (`deMois()`, éprouvée sur avril, août, octobre, janvier, mai).
- **Tablette** : « Gestion » ouvre la feuille sous son titre, sans le faux titre « Sections » au-dessus de la seule Direction.
- **Boutons d'accent** à 650 de graisse ; « Renseigner mon contrat » passe de 12,5 px maigre à 13,5 px.
- **Tableau de bord** : l'année n'est écrite que si elle diffère de l'année en cours (« Ma 27 oct. », mais « Lu 4 janv. → Ma 5 janv. 2027 »).
- Déjà réglé par la vague A : « Dimanche 1er novembre » sur une ligne de 361 à 400 px. À 320 px, la date reste sur deux lignes, selon la décision du 22/10/2026 ; le commentaire du CSS qui disait le contraire est corrigé.
- Laissé à la Direction, en cours de complément : le « 1er » de sa date et les « & » de ses titres (« Absences et santé », « Rythme et charge »…).
- Non-régression : une alerte, fausse, dans le Salaire. L'outil divise la hauteur de tout l'encadré par l'interligne, et le bouton y a gagné 1 px. Le texte lui-même garde ses 2 lignes à 1280 px.

### Vague B, sélecteurs (23/10/2026, v1012)

- **Effectifs** : l'onglet « Congés et repos » s'atteint au clavier. Une fonction commune, `ongletVise()`, gère ←, →, Origine et Fin en boucle ; le focus et la sélection suivent.
- **« En cours / Historique »** : l'anneau de focus n'est plus rogné sur trois côtés (il se trace à l'intérieur du bouton).
- **La bascule Congé · Recyclage · Heures sup.** :
  - tabindex itinérant et flèches ;
  - le focus suit l'onglet malgré les deux rendus de la section (« Chargement… », puis la liste) ;
  - la flèche ne fait plus avancer d'un an la grille du Planning cachée derrière.
- **Cibles** : la bascule (42 px) et le choix de « préciser » (38 px) passent à 44 px au téléphone.
- **État retenu en sombre** : la pastille ne se détachait du rail qu'à 1,03:1 à 1,20:1. Un liseré au jeton `--in` la porte à plus de 5:1 (`.pl-seg`, `.calvue`, `.caseg`).
- **Code mort** : la recette `.seg` ne servait plus et touchait les barres de la cascade du Salaire. Retirée : la plus petite barre retrouve sa vraie largeur (1,31 % du brut).
- **Fusion** : la zone des demandes avait aussi mis les flèches sur la bascule. Deux écouteurs auraient avancé de deux onglets, on garde celui des sélecteurs. Éprouvé à 390 et 1280 px : une flèche, un onglet, Fin et Origine justes, aucune erreur.
- **Laissé à la Direction**, en cours de complément :
  - la barre Aujourd'hui · Effectif · Analyses et les choix « Répartir par » et « Comparer » ne s'atteignent pas aux flèches ;
  - la pastille retenue y est à 1,15:1.

### Vague B, accessibilité (23/10/2026, v1013)

- **Panneau ouvert au téléphone.** Remesuré : la fiche d'une personne rendait encore la liste inerte à 390 et 730 px. La liste ne passe plus en inert que sous la feuille plein écran des demandes. La fiche d'une personne et la feuille d'une case, en lecture comme en saisie, laissent la liste touchable.
- **Au PC, dès 1100 px, l'espace n'est plus un dialogue modal** à côté d'un menu actif. C'est une région ; seuls le contenu caché dessous et « Aller au contenu » deviennent inertes. Mesure sur 60 Tab : avant, 48 dans l'Accueil caché et aucun dans l'espace ; après, 30 dans l'espace, 27 dans l'en-tête, 0 dans l'Accueil. Le fond se relit au passage du seuil.
- **Le focus ne se perd plus** à l'ouverture ni à la fermeture de l'espace au clavier : il va à l'entrée de l'espace, puis revient à la tuile qui l'a ouvert. Au menu de la tablette, il reste sur l'entrée choisie.
- **Mon mois** : le chiffre d'aujourd'hui sur un congé ou un prévu passe de 1,38:1 à 8,27:1.
- **Choix du mois** : un anneau aux trois arrêts du clavier, aucun au clic ni au toucher (classe posée au focus venu du clavier).
- **« Plus » courant** : un anneau de 2 px au focus.
- **Case touchée** : le panneau prend le focus sur lui-même, sans anneau sur « × » ; au clavier, « × » comme avant.
- **Mes congés** : sigle et « 0 h » de 3,5:1 à 6,3:1. Les compteurs prennent `role="group"`, faute de quoi leur aria-label n'était pas lu.
- **Fusion** : cinq conflits, chacun résolu en gardant les deux apports.
  - Titre et retour du focus à la fermeture.
  - Focus du panneau : au doigt, de l'accessibilité ; après un visa, des demandes ; empreinte de la feuille, des demandes.
  - Pluriel « à partir de deux » du contenu et `role="group"` sur les compteurs.
  - L'inertie : la feuille de case est non modale pour l'espace RH comme pour l'accessibilité ; une condition de plus que j'avais ajoutée pour la saisie d'une case ne pouvait jamais jouer, elle est retirée.
- **Éprouvé au navigateur** :
  - case à 390 px, liste non inerte ;
  - demande à 390 px inerte, en région ;
  - à 900 px, dialogue modal ;
  - à 1280 px, région, contenu caché inerte ;
  - aucune erreur.
- **Reste** :
  - une saisie de case en cours se perd si l'on touche une autre case : non demandé, à confirmer avant de bloquer la grille ;
  - laissé à la Direction : le champ de date qui s'allume au clic de souris ;
  - laissé à l'Accueil : les tuiles `role="listitem"` qui ne s'annoncent pas comme boutons.
