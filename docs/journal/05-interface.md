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

- la case Rappels écrivait le montant collé au nombre (« 1 (montant retiré) € » se
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
  d'année, alors que la nuit donnait les (montant retiré) € de l'application au
  lieu de (montant retiré) €. `parseHoraireEntry()` pose `rpp`, la pause de
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
- **Le mois d'avant** : sous le net, « −(montant retiré) € par rapport à
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
