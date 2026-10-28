# Vérificateur du calendrier, manques, polyvalence, compteurs

Historique déplacé tel quel de `CLAUDE.md` le 18/10/2026. Les dates, mesures et erreurs y restent.

## Vérifier le calendrier de tout le monde

```bash
node tools/verifier-calendrier.js
```

Confronte ce que le calendrier **affiche** à ce que le classeur **dit**, pour
les 77 personnes et les 27 574 journées. Il ne réimplémente rien : il découpe
dans `index.html` les fonctions de lecture elles-mêmes et les rejoue — ce
qu'il mesure est donc bien ce que l'application fera.

Il découpe par `indexOf`, donc **il s'arrête si un nom est déclaré deux fois**
dans `index.html` : la seconde déclaration écrase la première à l'exécution,
alors que la découpe rejouerait la première — et l'outil annoncerait neuf
règles vertes sur du code que le navigateur n'exécute plus. C'est arrivé avec
`posteDuRemplace`.

Neuf règles, et aucune n'a le droit d'être enfreinte :

| Règle | Ce qu'elle interdit |
|---|---|
| cellule non reconnue | le classeur écrit quelque chose que la lecture ne sait pas traduire |
| poste prévu effacé | `["N","-"]` affiché comme un repos ordinaire |
| poste sans heure | une case peinte en poste sans heure prestée |
| heure sans poste | des heures prestées sans poste à montrer |
| repos habillé | un repos affiché en poste ou en absence |
| absence sans code | une journée non prestée sans rien qui le dise |
| étiquette vide / trop longue | une case muette, ou un code coupé |
| **vues en désaccord** | le mois et l'année divergents sur la même journée |

La dernière est la plus importante : le mois lit une journée **enregistrée**
par le pré-remplissage, l'année **relit le classeur**. Deux chemins pour une
même journée — et c'est ainsi qu'une divergence est passée. Ils partagent
maintenant `lireJournee()` ; le vérificateur refait le trajet complet
(lecture → écriture du mois → relecture) et exige le même résultat.

Le code de retour est 1 s'il reste une faute **dans les neuf règles
dures** : l'outil se branche tel quel sur un contrôle automatique. Il
additionnait jusqu'au 26/09/2026 les règles faibles — des questions à
trancher, jamais à zéro — et sortait donc en 1 sur des données saines ; un
contrôle qui échoue toujours ne se lit plus. `--strict` rend l'ancien
comportement.

Pour demander à l'outil ce que l'application fait d'une journée précise —
plutôt que d'écrire un script à côté, qui réimplémenterait la lecture et
pourrait donc se tromper d'accord avec lui-même :

```bash
node tools/verifier-calendrier.js --journee FPA 0919 0921
```

**Au 22/09/2026 : les neuf règles sont à ZÉRO sur les 27 462 journées.**
La dernière cellule non reconnue était `CAN 24/07 ["*"]` — une faute de
frappe pour un tiret, tranchée par le client le 22/09/2026 et rangée dans
`ALIAS_HORAIRE`. Le classeur est désormais lu sans une exception.

Une cellule se juge sur ce que l'APPLICATION y lit, pas sur ce que le
classeur y écrit : la règle applique `ALIAS_HORAIRE` avant de conclure, et
suivra donc toute addition future sans qu'on y pense.

Une dixième règle, plus faible, liste les **mentions non comprises** : la
case s'affiche juste, mais un morceau de la cellule reste illisible. **19
journées**, regroupées par mention — `HS`, `eval`, `CPPT-F`, et d'autres,
aucune au-delà de deux journées. Elles n'empêchent rien d'afficher, mais elles
pourraient déplacer des heures : à faire trancher, une par une.

### L'onglet Équipe n'a plus qu'une vue

Le client, le 22/09/2026 : « supprime la vue par pause de l'onglet équipe ».
Elles étaient deux, sous une bascule « Par poste / Par pause » : les postes
en lignes et les trois pauses en colonnes d'un côté, les quatre pauses en
lignes et les huit postes en colonnes de l'autre.

**C'est la vue par POSTE qui reste** — huit postes en lignes tiennent
l'écran là où huit postes en colonnes le débordent, et c'est elle qui a reçu
toutes les corrections du 22/09 : les trigrammes empilés, « à déterminer »
sous la ligne STEP, les légendes réduites à ce qui est dessiné. La vue par
pause ne les avait suivies sur aucun point — ses trigrammes se lisaient
encore en ligne, séparés d'un point médian.

Sont partis avec elle : la bascule `#eqVue`, la variable `eqVue` et son
écouteur, la clé `ui/eqVue`, les 39 règles `.eqg2` et les 88 lignes de rendu.
`postesDePause()` **reste** — c'est elle que la vue restante, le module des
manques, la polyvalence et le poste du jour de la barre du haut rejouent
tous.

Un appareil qui avait choisi « Par pause » ouvre désormais la vue par poste
sans rien dire : la clé oubliée n'est plus lue. Vérifié.

**Les trigrammes s'empilent, un par ligne.** Le client le demandait le
21/09/2026, une passe d'optimisation les avait remis en ligne pour gagner de
la largeur, et il l'a redemandé le 22 : « les trigrammes doivent être l'un
en dessous de l'autre (donc la ligne plus haute) ». Le souci de largeur se
règle autrement — une pause n'a plus besoin que de la largeur d'UN nom, et
les pixels reviennent à l'intitulé de poste, qui retrouve ses 122 px et son
corps lisible.

Un piège au passage, et il tenait à UN pixel : la colonne d'une pause offre
62 px de contenu à 390 px de large, et « Après-midi » en demande 63 — le mot
se coupait en deux. Le remplissage de l'en-tête en prenait seize à lui seul ;
on lui en rend huit, plutôt que de réduire le corps de ce qu'on lit en
premier. À 360 px il faut en plus un demi-point de moins.

**L'opérateur « à déterminer » est dans le tableau, pas à côté.** Le client,
le 22/09/2026 : « l'opérateur à déterminer doit être affiché sous la ligne
STEP dans sa pause ». Il se lisait dans la carte « Hors poste », loin du
tableau — donc loin de la question qu'il pose. Il en occupe désormais la
dernière ligne, sans couleur d'atelier : n'ayant pas de poste, il n'a pas de
zone. Il a quitté la carte du même coup ; l'y laisser l'aurait montré deux
fois.

Le tiret cadratin « — » dit « personne » ; le tiret court « – » dit « ce
poste n'attend personne à cette pause ». Les deux ne veulent pas dire la
même chose, et la ligne « à déterminer » emploie le premier.

**L'opérateur en formation s'écrit en DERNIER de la case.** Le client, le
22/09/2026 : il est présent, mais il n'y est pas encore validé — le lire
après ceux qui tiennent le poste évite de compter sur lui d'un coup d'œil.
La partition se fait dans `postesDePause()`, donc les deux vues et le
vérificateur la partagent.

Elle est **stable**, et c'est tout l'enjeu : l'ordre établi plus haut —
titulaires avant renforts, contremaîtres avant adjoints — ne doit pas se
défaire. Un tri par comparaison le mélangerait ; deux seaux recollés le
gardent intact. L'ordre seul change : `tenu`, `attendu` et les drapeaux
restent ce qu'ils étaient — vérifié, les manques sont toujours à 12 journées
et 14 places.

**Les légendes ne montrent que ce qui est à l'écran.** Le client, le
22/09/2026 : « ne laisser que les légendes utiles ». Une légende qui explique
un signe absent est du bruit — la plupart des jours il n'y a ni opérateur en
formation ni poste sous son effectif, et les deux entrées s'affichaient
quand même. Le rendu note ce qu'il a réellement dessiné (`aForm`, `aManque`,
`aVide`, `zVues`) et n'explique que cela ; les zones se rangent dans l'ordre
où le tableau les montre, celui de la production.

Vérifié en avançant jour par jour : sans formation ni manque, une seule
ligne ; trois opérateurs en formation, l'entrée revient ; un poste sous son
effectif, la sienne aussi.

**Une journée a deux postes depuis le 21/09/2026** : `r.s` porte la prime
PAYÉE, `r.sp` le poste PRESTÉ quand ils diffèrent — 275 journées où le
commentaire nomme une prime à conserver, plus les journées `SD26` et `D-F`.
Pour afficher, `postePeint(rec)` et `gardePrime(rec)` ; jamais `rec.s` seul.
Voir `docs/regles-paie.md`, « La prime conservée ».

`RHS`, `RTT-` et `E. min` en sont sortis : le client les a tranchés le
20/09/2026 — voir `docs/regles-paie.md`.

Une **onzième règle**, plus faible elle aussi, dit ce que le motif des
ateliers **avale sans en faire un poste**. C'est le pire angle mort : non pas
ce que l'outil déclare ne pas savoir lire, mais ce qu'il **croit avoir lu**.
`ATELIERS` commence par `^(…|poly|…)`, si bien que « Poly. Etoh » y
correspondait par son premier mot — reconnu, donc absent des mentions non
comprises, et traduit en aucun poste. **46 journées** ont passé ainsi,
invisibles aux dix autres règles, jusqu'à ce que le client le signale.

Il en reste **5** : `consign.` (3), `Polyvalence` et `polyvalence` (1 chacune).

Une **douzième règle**, la plus utile des trois faibles, confronte les motifs
de l'application à une version délibérément **plus large** d'eux-mêmes, et dit
ce que la seconde trouverait de plus. Deux défauts du 21/09/2026 venaient d'un
motif trop étroit, et rien ne pouvait les voir : un motif qui lit moins qu'il
ne croit ne ment pas — il se tait.

Elle a trouvé, le jour même de sa naissance : `plageCommentaire()` exigeait un
espace après « à », donc `de 14h à18h00'` lui échappait — **38 journées**, et
la plage décide si les heures épargnées sont DANS le poste ou à côté. Et
`atelierDuRemplace()` ignorait « rempl SBZ » abrégé.

Elle découpe les motifs dans `index.html` plutôt que de les recopier : sa
première version les recopiait, et elle a continué d'annoncer 38 manques après
que `index.html` eut été corrigé. **Une règle qui dénonce les copies ne peut
pas en être une.**

Elle a trouvé une seconde fois, le 22/09/2026 : `plageMention()` refusait
l'apostrophe des minutes — `11h-15h30'` — alors que `normPlage()` la
retirait depuis toujours. Deux motifs, deux sévérités sur la même
notation ; AFA le 10/02 s'affichait en absence à zéro heure alors qu'il
était au travail.

Il reste **46 écarts**, et ce sont des questions, pas des fautes : `10h-11h`
écrit avec un tiret, `00h à 6h` sans « de », des passifs mal orthographiés
comme « Remplacé pa VBN ».

## Vérifier une modification du pré-remplissage

`tools/verifier-calendrier.js` fait ce contrôle et le rend chiffré — c'est
lui qu'il faut relancer, et non un script à côté. Au 22/09/2026, sur les
27 462 journées : **14 648 prestées, 5 082 absences, 157 postes prévus non
prestés, 7 575 repos** (classeur du 22/09/2026 à 15 h 46). Un écart important
signale une régression — mais un nouveau classeur en déplace légitimement :
celui-ci fait passer CHD de Shift 4 à Shift 5, ce qui rebat 88 de ses
journées.

Ces nombres ne se comparent pas aux anciens repères de la section 11 de
`docs/conversion-horaire.md`, qui comptaient autre chose : ils mesuraient la
sortie brute de `parseHoraireEntry`, alors que ceux-ci mesurent ce que la
case AFFICHE, une fois le cycle, le remplacement et l'annotation « - »
appliqués.

### L'onglet « Recyclage »

Le client, le 22/09/2026 : « les polyvalences doivent être affichées dans un
onglet à part », puis « l'onglet polyvalence doit s'appeler Recyclage ». Elles vivaient sous chaque personne de l'annuaire, en
jetons ; à l'étroit dans une carte de 148 px, on ne pouvait ni comparer deux
personnes ni chercher qui peut tenir un poste.

Un onglet donne la largeur d'une **grille** : les gens en lignes, les postes
en colonnes. On y lit dans les deux sens. Le point plein marque SON poste —
il ne compte pas, et le dire évite de prendre une case vide pour une lacune.
Le point maigre dit « jamais tenu une journée complète » : un zéro se lirait
comme un résultat, un point comme une absence de résultat.

La colonne des trigrammes et la ligne d'en-tête restent collées au bord
quand la grille défile ; sans elles on ne sait plus de qui ni de quoi on lit
la case.

**Le titre et la période vivent HORS du cadre.** Le client, le 22/09/2026 :
« il faut le titre "Recyclage des polyvalences" au dessus du cadre avec
juste en dessous la ligne avec les dates (donc les sortir du tableau) ». Ils
annoncent la grille, ils n'en font pas partie — et une fois dehors, la
grille commence par sa propre ligne d'en-tête au lieu d'un bandeau qui lui
ressemblait. Le bloc s'appelle `.pvtete` : hors du cadre, il ne peut pas
emprunter la mise en forme de `.card>header`.

**Un filet gris au-dessus de « Qui »**, de la même épaisseur que les filets
d'atelier des autres colonnes — « pour avoir comme les autres colonnes ».
Sans lui la ligne d'en-tête commençait par un creux de trois pixels.

**TROIS entrées de légende, et pas une de plus** : « le point doit être
"Poste actuel", le petit point "Poste non acquis", F "En formation" ; les
autres légendes ne sont pas nécessaires dans ce tableau ». Ne restent que
les trois SIGNES, ceux qu'on ne peut pas deviner. Le vert d'un quota atteint
et le « 0/X » se lisent tout seuls — le chiffre y est écrit — et une légende
qui répète ce que la case dit déjà est du bruit. `.lg-pvok` et `.lg-pvnul`
sont partis avec elles.

**L'identifiant interne reste `polyvalence`** — la vue, la clé `ui/view`,
`calculerPolyvalence()`, `POLY_QUOTA`. Seul l'INTITULÉ change : ce que la
grille montre, c'est bien le recyclage DES polyvalences, et renommer la clé
aurait renvoyé au Résumé tous les appareils qui avaient l'onglet ouvert.

**Huit onglets** : « Polyvalence » était le plus long et la barre débordait
de 44 px à 320 et de 4 px à 360 ; d'où un demi-point de moins et deux pixels
de moins de chaque côté sous 375 px. **« Recyclage » a réglé le problème
qu'elle traitait** — mesuré : plus rien n'est tronqué à 10,5 px, même à
320 px. La règle est gardée pour ce qu'elle rapporte encore, **3 px de
hauteur de barre** (46 contre 49), et non plus pour faire rentrer les
intitulés. Le relire ici avant de rallonger un onglet.

Elle se pose APRÈS celle qui définit la barre mobile : à spécificité égale
c'est la dernière qui gagne, et une première tentative posée trois cents
lignes plus haut n'avait rien changé du tout.

### Le jour et son tableau ne font qu'un cadre

Le client, le 23/09/2026 : « supprimer la zone "comment lire ce tableau" et
lier le cadre avec la sélection de jour au cadre qui reprend les trois
pauses ».

C'étaient **deux cadres pour une seule chose** : on choisit une journée POUR
lire ce tableau-là. La barre de navigation et son contenu ne se séparent pas
— entre les deux il y avait une bordure, une ombre et seize pixels de vide.

**Deux hôtes et non un**, et c'est le point : `#eqCorps` rend le tableau des
pauses DANS le cadre du jour, et `#eqReste` rend « Hors poste » juste en
dessous, dans le sien. Un cadre dans un cadre ne se lit pas, et « Hors
poste » parle d'autre chose — de ceux qui ne tiennent aucun poste.

Le tableau a donc perdu son `.card` : il EST le contenu du cadre, posé sous
la barre qui le pilote. Mesuré : **0 px** entre le bas de la barre et le haut
du tableau, à 390 comme à 1280 px.

**Le repli « Comment lire ce tableau » est parti avec sa phrase.** Elle
décrivait ce qu'on voit — une ligne par poste, trois pauses en colonnes — et
le tableau le montre mieux qu'elle ne le disait. Les trois règles `.eqaide`
sont parties aussi : un style qui ne sert plus égare celui qui le relit.

### Ce qu'on a presté, jamais ce qu'on a touché

Le client, le 22/09/2026 : « FLN est en formation en D et non en PM ; il est
remplacé en PM, si tu regardes dans les commentaires ». Sa cellule du 23/09
dit `["PM","F","Formation Excel IFAPME remplacé par ALZ GKT"]` — PM est la
prime conservée, `F` dit que la journée s'est faite en horaire de jour, et
deux collègues tiennent son poste d'après-midi. Le montrer en PM le comptait
deux fois.

**Deux champs disent la même chose selon la source** : `r.sp` quand le
COMMENTAIRE nomme une prime à conserver, `r.jourCode` quand la MENTION
elle-même est l'une des huit de `JOUR_PRIME_PAUSE` — `SD26`, `F`, `D-F`,
`DS`, `CPPT`, `DS-CE`, `TP`. Le calendrier lisait déjà les deux, par
`postePeint()` ; `equipeDuJour()` n'en lisait qu'un, et rangeait ces
journées-là dans la pause PAYÉE.

`var pv=r.sp||((r.jourCode && !surSonPosteMalgreF(raw))?"D":r.s);` — la garde
est la même que celle de `postesDePause()` deux fonctions plus bas : sur les
22 journées de projet, le `F` ne sort pas du poste.

Les manques passent de **12 journées / 13 places à 14 / 16**, et c'est le
sens de la correction : quelqu'un parti en formation n'est plus à son poste,
et le trou qu'il laisse était invisible. Les neuf règles restent à zéro, les
compteurs à 76/77.

**`--journee` imprime désormais la prime, le poste presté et le code de
jour.** Sans ces trois champs à l'écran, rien ne disait POURQUOI quelqu'un
apparaît dans une pause plutôt qu'une autre — il a fallu les ajouter pour
voir le défaut.

### L'onglet « Mon horaire » n'a plus qu'une vue

Le client, le 23/09/2026 : « dans l'onglet Horaire il ne faut avoir que la
vue année par défaut, et toujours scroller jusqu'à la date du jour », puis
« je ne veux plus les autres boutons ; il faut donc supprimer la sélection
de mois qui était au-dessus du cadre et y ajouter un titre "Mon horaire"
comme pour Équipe ».

**La vue SEMAINE est morte** — 90 lignes de rendu, 35 règles de feuille,
`lundiDe()` et `lundiCourant`. `JOURS_LONGS` reste : la barre du haut écrit
« Mardi 22 septembre » avec, et elle ne lui appartenait pas.

**Le MOIS n'est plus une vue, c'est le détail d'une journée.** On l'ouvre en
cliquant une case de l'année — c'est là qu'on corrige — et un bouton
« ‹ Retour à l'année » ramène. Sans lui, la seule sortie aurait été de
changer d'onglet : **supprimer un aller sans laisser de retour aurait rendu
la correction d'une journée inaccessible.** `vueHoraire()` n'a donc plus
que deux états, et la bascule ne s'enregistre plus : on revient toujours sur
l'année.

**Le clic sur une journée visait un sélecteur mort.** `.day[data-d]` est une
disposition en liste qui n'existe plus ; le mois s'ouvrait sur son premier
jour. Cela comptait peu tant qu'un bouton « Mois » existait — c'est
maintenant le SEUL chemin. Il vise `.mc-j[data-d]` et ouvre la feuille du
jour, ce pour quoi on a cliqué.

Le titre vit **hors du cadre**, comme celui d'Équipe : `.pvtete`, « Mon
horaire » et « VBN · 2026 » dessous. Et « Septembre 2026 » disparaît de
l'en-tête du cadre tant qu'on lit l'année : il décrit le mois qu'on corrige,
pas l'année qu'on regarde.

**`centrerSurAujourdhui()` est appelée de DEUX endroits, et il en faut
deux** : à la fin de `renderAnnee()`, pour le changement de personne, et
dans `setView()` à l'ouverture de l'onglet — car la vue est déjà dessinée
quand on y revient, et `setView()` remet la page en haut APRÈS coup. Le
premier essai n'appelait que le premier des deux, et la page restait sur
janvier.

Sans animation : un glissement se battrait avec le repli de la barre du
haut, qui écoute le défilement. Et rien ne bouge si le panneau est caché.

Mesuré : la case du jour est **au milieu de l'écran** à 390 comme à 1280 px
(2 661 px et 571 px de défilement), et « Mois » choisi à la main revient
bien après un rechargement.

### « N ? » — le poste prévu que rien ne confirme

Le client, le 23/09/2026, sur LHR les 2 et 3 octobre : « c'est N avec ? car
ce n'est pas encore confirmé si nécessaire ou si l'opérateur a accepté ».

Sa cellule dit `["-","N?","Echange avec JKS SPT présent?"]` : la rotation le
met en repos, et on lui demande peut-être deux nuits en échange avec un
collègue. Le « ? » rendait la mention illisible, le poste retombait sur le
repos, et **deux nuits disparaissaient avec leurs primes** — le pire des deux
résultats possibles, puisque le classeur dit au moins qu'il s'agit d'une
nuit.

L'étiquette devient **« N ? »**, qui tient dans les quatre signes, et la
journée part au compteur des journées à vérifier.

**LE DOUTE NE VAUT QUE S'IL PORTE SUR LE POSTE**, et une première version
s'est trompée de cible. Quatre cellules de l'année finissent par un point
d'interrogation, et deux le mettent sur l'ATELIER : `["N","Poly. Arr.?"]` et
`["AM","gluten?"]` — là le poste est écrit noir sur blanc dans la cellule
franche et ne fait aucun doute. Elles s'affichaient « N ? » et « AM ? »,
c'est-à-dire qu'elles faisaient douter de la mauvaise chose. Le `?` n'est
retenu que si le texte qui reste EST un poste ou une plage.

Le point d'interrogation du COMMENTAIRE — « SPT présent? » — ne compte pas :
seule l'annotation porte le poste.

**Le vérificateur garde sa PROPRE copie de l'écriture du mois** (`enregistre()`),
et elle s'est désynchronisée immédiatement : l'année écrivait « N ? », le
mois « N », et la règle « vues en désaccord » est montée à 4. C'est le piège
déjà rencontré — **deux copies, et c'est toujours la seconde qui reste en
arrière**. Les deux portent maintenant le drapeau.

`marqueDoute()` lit les DEUX formes de journée — `doute` pour celle que
`parseHoraireEntry()` rend, `q` pour celle qu'un mois enregistre — parce que
les deux vues doivent montrer la même étiquette.

Journées prestées : **14 648 → 14 650**, exactement les deux nuits de LHR.
Neuf règles à zéro, compteurs 76/77, mentions non comprises **19 → 17**.

### Deux cellules qui valaient seize heures et une demi-journée

Deux autres « repos à zéro heure » qui n'en étaient pas, tranchés par le
client le 23/09/2026 en même temps que le « N ? ».

**`HS` seul — la journée entière en heures supplémentaires.** AFA les 23 et
24 avril. Le client : « il avait d'abord déplacé ses 2 jours de D (23 et 24)
au 16 et 17, car à la base il ne travaillait pas le 16 et 17 ; par contre il
a quand même été rappelé le 22 et 23 pour travailler en HS le 23 et 24 »,
puis « il a bien fait 2x8h en D de rappel ».

Quatre journées prestées sur des repos, donc — et les deux dernières
s'affichaient en repos à zéro heure : **seize heures supplémentaires
perdues**. Le classeur n'écrit `HS` seul que sur ces deux cellules de toute
l'année ; il n'y a rien à généraliser au-delà de ce qu'elles disent. On
réemploie ce qui existe : `8H HS` du barème ne retire rien à la journée
(`h:0`) et crédite huit heures supplémentaires (`hs:8`), et le code de jour
peint la journée en D comme le fait déjà un repos portant `SD26`.

**Le rappel, lui, n'est écrit nulle part sur ses cellules** — leurs
commentaires disent « D déplacé au 16.04 » et rien d'autre. Les « rappel le
16.04 » du classeur sont sur les colonnes d'AUTRES personnes, aux mêmes
dates. La prime de rappel ne peut donc pas se déduire : à faire écrire au
classeur, ou à poser à la main sur ces deux journées.

**`SD26/ Abs` — la journée prestée, puis écourtée.** VGG le 11 mars,
`["-","SD26/ Abs","Départ à 12h"]`, seule cellule de ce genre dans l'année.
Le client : « pendant le SD26 les gens venaient selon les besoins
nécessaires à la production, mais il a certainement fait 6/14 et est parti à
12h ».

**Il n'y a donc AUCUNE règle à tirer de `SD26`** : il n'implique pas de
pause, et la durée ne se déduit pas de la cellule. Les deux heures
manquantes ne se calculent pas depuis le commentaire non plus — **393
commentaires de l'année parlent d'un départ**, et tous les autres portent une
plage ou un poste dans leur cellule, qui donne l'heure de début. Celle-ci
n'en a pas : le 6 h vient du client, et il est écrit dans le code avec sa
raison plutôt que deviné.

La journée prend la prime de **jour**, et non celle du matin, pour rester
d'accord avec les 23 autres journées « repos + SD26 » : une journée prestée
sur un repos se fait en horaire de jour, sans prime de pause puisqu'il n'y
avait pas de pause prévue.

**`var n` est déclaré plus bas dans `lire()`, et les deux branches sont
mortes en silence.** Écrites au-dessus de `var n=normPlage(txt)`, elles
lisaient un `undefined` hissé : aucune erreur, aucun effet, et le
vérificateur annonçait les mêmes chiffres qu'avant. Elles appellent
`normPlage(txt)` directement.

Journées prestées **14 648 → 14 653**, repos **7 575 → 7 570**, mentions non
comprises **19 → 14**. Neuf règles à zéro, compteurs 76/77.

### Une plage qui nomme une pause dit qu'on est à son poste

Le client, le 25/09/2026 : « GPS le 30/09 fait 10-22 mais vient plus tôt
pour participer au CPPT ».

Sa cellule dit `["10h-22h","D-CPPT"]`. Le code de jour le sortait de sa
pause : la case **Contremaître de l'après-midi passait à 0/1**, et lui se
lisait dans « Hors poste » sous l'étiquette CPPT. Il était pourtant bien à
son poste de 10 h à 22 h — la réunion explique seulement pourquoi il est
venu plus tôt.

Le code de jour dit que la journée s'est faite EN HORAIRE DE JOUR. **Une
plage qui nomme une PAUSE dit le contraire, et elle le dit avec des
heures.** `surSonPosteMalgreF()` ne laisse donc plus sortir du poste quand
la cellule porte une plage dont `posteDepuisPlage()` ne rend pas le jour.

**216 journées portent une plage ET un code de jour ; 121 restent où elles
étaient** — « 7h-15h | SD26 » est bien une journée de jour, et la règle ne
la touche pas. **95 changent de place, dont 80 en « 6h-14h »** : quelqu'un
qui travaille de 6 h à 14 h est au MATIN, quoi que dise l'annotation.

GPS reprend sa place de contremaître le 30/09, et **JKS avec lui** :
`["09h-21h","CPPT"]`, même forme, et son commentaire le confirme — « Réunion
DS de 9h à 10h, CPPT à partir de 10h, remplacé par IME de 21 à 22h ».

**SBZ, non, et je l'avais dit trop vite.** Sa cellule du 30/09 est `["PM"]`,
sans plage ni code de jour : la règle ne le touche pas. Il était déjà dans
une pause et a simplement glissé du gluten au terrain arrière, parce que JKS
a repris la place de gluten. C'est le rééquilibrage, pas cette règle.

**Les manques passent de 12 à 11, et pas par le 30/09.** Cette journée perd
bien son `PM Contremaître 0/1`, mais elle garde son `N Gluten 1/2` : elle
compte toujours. Le −1 vient du **16 décembre**, par un chemin qu'il faut
avoir vu une fois :

- **QBY** y porte `["10h-22h","DS-CE"]`, polyvalences gluten et
  distillation. Avant, `DS-CE` le sortait de sa pause et il partait en
  « Jour » ; maintenant sa plage le garde en après-midi et **il tient sa
  distillation lui-même** ;
- **PAM** y porte `["PM"]`, avec la fermentation dans ses polyvalences.
  Son collègue parti en « Jour », le rééquilibrage l'envoyait boucher la
  distillation — et la **fermentation restait à `0/1`**. Celle-ci étant
  désormais tenue par son titulaire, PAM **couvre la fermentation**.

C'est exactement le mécanisme de couverture établi le 22/09 : le tableau dit
qui TIENT un poste, et PAM a la fermentation pour le jour où le trou se
présente. **Une place qui se libère en déplace une autre trois mois plus
loin** — c'est pourquoi on relit `--manques` en entier après chaque
correction de placement, et pas seulement la journée qu'on croyait toucher.

### `TP` comptait 209 journées prestées pour des gens qui sont chez eux

Le client, le 25/09/2026 : « TP c'est temps partiel, CP (congé parental 4/5
ou 9/10) et TP c'est pareil mais sans la compensation de l'ONEM », puis,
interrogé sur le paiement de la journée : « pour le TP je ne pense pas,
c'est une réduction de temps de travail avec la loi belge pour le 9/10 ou
4/5 ».

**Ce n'est pas une absence que l'on pose** : c'est un jour qui ne fait pas
partie du contrat, comme un samedi l'est pour tout le monde. La réduction
est dans le salaire de base ; le jour n'a donc **aucune ligne de fiche** à
porter. C'est tout ce qui le sépare de `CP`, qui ouvre l'allocation de
l'ONEM et porte la sienne.

**J'avais invoqué le réglage « Fraction payée » comme preuve, et le client
l'a relevé** — « une fraction payée pour les TP ? ce n'est pas plutôt les
CP ? ». Son aide disait « 0,90 = congé parental 9/10 » : elle nommait le
`CP` et rien d'autre. Le champ lui-même est pourtant générique — il
multiplie la rémunération fixe, forfaitairement (`remFixe*p.fraction`), et
un 4/5ᵉ temps partiel fait la même arithmétique qu'un 4/5ᵉ parental. Mais
un texte qui ne nomme qu'un cas laisse l'autre croire qu'il n'est pas
concerné : **l'aide et l'écran d'accueil nomment désormais les deux**, sans
quoi les 8 personnes à `TP` garderaient une fraction de 1 et un socle trop
élevé.

**Ce que la correction déplace se mesure, et ce ne sont pas des primes.**
`primeD` vaut **0** — la prime « jour » est nulle, donc les 209 journées
n'en portaient aucune. Le socle, lui, est forfaitaire et ne dépend pas des
heures. Ce qui bougeait vraiment, c'est le **chèque-repas** :
`if(h>=4) acc.joursCr++` en donne un par journée prestée d'au moins quatre
heures, donc **209 chèques étaient accordés pour des jours non travaillés**
— FLN 40, LAX 34, ATA 26, DWS 26, SPT 26, SMA 26, LCI 25, GDT 6.

`TP` était pourtant dans `JOUR_PRIME_PAUSE`, donc lu comme une journée
**prestée** en horaire de jour. Même forme de cellule, lecture opposée :
`["7h-15h","CP"]` donnait une absence à zéro heure, `["6h-14h","TP"]` un
poste à huit heures avec la prime de jour. **La cellule franche de ces
journées porte ce que la rotation avait PRÉVU**, pas ce qui a été presté —
`D` 73 fois, `6h-14h` 57, `7h-15h` 47, `N` 18. Le module des manques les
croyait à leur poste.

**Le « c'est pareil » s'est mesuré avant d'être cru.** Les deux codes se
posent par blocs de un à trois jours — et non un jour fixe par semaine — et
leurs totaux sont ceux d'un temps partiel : 26 journées valent un jour par
quinzaine (9/10), 51 un jour par semaine (4/5). `TP` : 209 journées chez 8
personnes. `CP` : 423 chez 17.

**Le code entre au barème avec SON PROPRE `k`**, et non celui de
`SANS SOLDE` — qui ne porte pas de ligne non plus. Un congé sans solde et un
temps partiel ne sont pas la même chose, et le jour où une fiche montrera
une ligne pour l'un, il ne faudra pas la poser sur l'autre.

Journées prestées **14 645 → 14 436**, absences **+209** — exactement les
209 journées, sans un écart. Neuf règles à zéro, compteurs **76/77**,
manques **inchangés à 11 / 11** : le rééquilibrage couvrait déjà ces
absences. Couples de polyvalence **101 → 99**, les 33 au quota inchangés.
Vérifié au navigateur sur ATA : ses 26 journées se rendent en absence, pas
en poste.

**La `fraction` reste saisie à la main** : on pourrait la déduire du nombre
de journées `TP`, mais c'est un réglage personnel qui ne quitte pas
l'appareil, et la déduction se tromperait sur une année incomplète.

**Et la fiche MONTRE ces heures.** Puisque aucun code d'absence ne paie,
`k:"TP"` ne décidait que de les afficher ou de les taire — la première
version les taisait, et le client a tranché : « fait cela ». La ligne
**« Heure(s) temps partiel »** se pose à côté de celle du congé parental,
dont elle est le jumeau, avec **son infobulle à elle**. Surtout pas celle
des heures assimilées à du travail : ce motif annonce « payées comme des
heures prestées », ce qui serait faux ici. Vérifié sur ATA : 24 heures en
septembre, et aucune colonne en euros.

### Un congé et un rappel dans la même cellule

GPS le 02/07, `["7h-15h","RHS+02h-06h","Rappel le 02/07"]` — la seule
cellule de l'année à mêler un code d'absence et une plage. Le client, le
25/09/2026 : « il a fait 4 HS de 02-06h en étant rappelé le jour même ; **je
sais que c'est du HS car il n'y a aucune cellule dans sa liste qui mette
`+4h FT`**, et de 06 à 14h il était bien en RHS ». Le raisonnement est celui
du classeur : l'épargne au compteur s'écrit, elle.

Le calcul en faisait un poste `D` de **8 h prestées sans aucun RHS** — les
deux moitiés fausses.

**`abs` n'accepte qu'un code, et c'est le congé qui le prend** : c'est lui
qui vide la journée, et c'est le libellé de fiche de ses 1er et 3 juillet.
Les heures supplémentaires passent par **`ax`**, que l'accumulateur
concatène déjà à `a`. Ses deux autres lecteurs ne regardent que les codes
dont `h>0`, donc un `4H HS` n'y touche à rien. Un champ parallèle aurait
demandé cinq points de synchronisation ; **une source de plus pour un
mécanisme existant vaut mieux qu'un mécanisme de plus à tenir en phase.**

**LA PLAGE DU RAPPEL NE SE MET PAS DANS `r.plage`**, et la première version
l'a fait sans rien casser de visible. Ce champ dit la plage prestée COMME
POSTE DU JOUR, et `dureeReelle("D",[2,6],8)` rend **12** : le poste est
étendu pour couvrir 2 h à 6 h, la journée devient douze heures, les huit de
RHS en sont retirées, et l'on affiche « 4 h prestées en D » — ni le congé,
ni les heures supplémentaires. La plage ne sert qu'à COMPTER les heures du
rappel.

**Et la copie du vérificateur ne portait pas `ax`.** `index.html` l'écrit
depuis toujours (`nrec.ax=parsed.ax`), `enregistre()` du vérificateur non :
le mois rejoué perdait les codes supplémentaires. C'est encore le même
piège — deux copies, et c'est la seconde qui reste en arrière. `--journee`
les imprime désormais sous « codes en plus ».

Journées prestées **14 436 → 14 435**, absences **+1**, mentions non
comprises **14 → 13**. Neuf règles à zéro, compteurs 76/77. Vérifié au
navigateur sur la fiche de juillet de GPS : 24 h de récup. HS, 4 h
supplémentaires, 4 h payées à 150 %, et la prime de rappel J.

**LES HEURES VONT AU COMPTEUR, LA PRIME DE PAUSE SE PAIE.** Le client, en
réponse à la question de la prime de nuit : « il reçoit les 4 h HS dans un
compteur et il les reprend quand il veut ou se les fait payer en fin
d'année, quand on doit mettre les compteurs HS à zéro », puis « les 4 h de
rappel (02-06) sont payées en nuit ».

La fiche séparait déjà les deux sans qu'on s'en serve : `hsAutoBkt` paie les
HEURES, `hsAutoPoste` paie la PRIME D'ÉQUIPE. **Une heure récupérée rend
l'heure, pas la prime de la pause où elle a été prestée.** Les heures
versées au compteur ne passent donc plus par le premier.

**Et le poste des heures supplémentaires n'est pas celui de la journée** : un
rappel de 02 h à 06 h est de la nuit, même posé sur un congé dont la cellule
dit « 7h-15h ». Sans cela la prime se cherchait dans le seau « D », dont la
prime est nulle — donc aucune ligne. `rec.hsp` porte le poste, `rec.hsc` le
versement au compteur, tous deux jusqu'au mois et dans les DEUX copies de
`enregistre()`.

Vérifié au navigateur sur juillet : la ligne « HS non compensées » a disparu,
« 4 h versées au compteur » apparaît, et « Suppl. Équipe Nuit à 150 % (heures
suppl. de l'horaire) » paie la prime.

**ET LA RÈGLE VAUT POUR TOUTES LES HEURES SUPPLÉMENTAIRES.** Le client,
interrogé sur les 205 autres journées : « cela dépend de si il remplit une
feuille pour avoir des FT+ ou des HS. **Quoi qu'il arrive les 2 vont dans un
compteur**, mais le compteur HS n'apparaît pas dans le classeur. »

C'est son raisonnement sur GPS, généralisé : **le classeur ÉCRIT l'épargne
au flex time ; son silence désigne l'autre compteur**, celui qu'il ne porte
pas.

**ELLES SONT PAYÉES À LA REPRISE, ET J'AVAIS ÉCRIT LE CONTRAIRE.** Le
client : « les HS sont payées quand les opérateurs reprennent leurs heures
sup (indiqué dans l'horaire ou en commentaire), donc ta phrase n'est pas
correcte ». J'avais annoncé que l'application ne les payait plus. Le circuit
se lit en deux temps : **prestée**, l'heure va au compteur et le classeur
n'écrit rien ; **reprise**, le classeur l'écrit — `RHS`, `2h RHS`, un
commentaire — et la journée est payée. Une reprise d'un jour vaut zéro heure
prestée sans que le socle bouge ; une reprise partielle ne retire rien à la
journée. **L'argent n'est pas perdu, il est décalé.**

Ce qui est parti, c'est le paiement AU MOIS DE LA PRESTATION, au taux
majoré — **775 heures sur 205 journées** — qui faisait payer ces heures
**deux fois**. La prime d'équipe reste due, et c'est la moitié qu'il ne
faut pas emporter avec l'autre.

Le champ manuel « Heures suppl. non compensées » reste payé : c'est
désormais le SEUL endroit où l'on déclare des heures réellement payées, et
c'est une saisie volontaire, pas une déduction de l'horaire.

Le drapeau `rec.hsc` a disparu avec l'exception qu'il portait — ce n'est
plus un cas particulier, c'est la règle. `rec.hsp` reste : le poste des
heures supplémentaires n'est toujours pas celui de la journée.

**ET LA FICHE EN PORTE DEUX, QUE J'AVAIS TOUTES DEUX RETIRÉES.** Le client :
« vérifie avec toutes mes feuilles de paye si ta logique est bonne ». Elle
ne l'était pas. Trois de ses fiches portent des heures supplémentaires,
toujours sous la même paire :

```
 1:30  Heures sup à compenser à <taux> à 150 %     +
-1:30  déduc HS à comp à <taux>                    −
```

Le sursalaire est payé au taux majoré LE MOIS DE LA PRESTATION, et l'heure
de base est déduite puisqu'elle sera reprise plus tard. Net : la moitié du
taux horaire. La fiche affiche le solde d'année du compteur juste à côté. **L'heure part au compteur, le sursalaire ne l'attend pas** —
j'avais lu « les heures vont au compteur » comme « rien n'est payé », et
c'était faux d'une moitié.

Les deux lignes s'écrivent séparément plutôt que nettes : l'onglet Contrôle
se lit ligne à ligne contre la fiche, et une ligne à 50 % n'y existe pas.

**La leçon de méthode** : les fiches sont le contrôle le plus sévère dont on
dispose, et je n'avais pas pensé à les ouvrir pour une règle de paie. Le
client a dû le demander.

### Ce que les fiches disent d'autre, et qui n'est pas expliqué

La même comparaison montre un écart ANCIEN, identique avant et après tout ce
qui a été fait le 25/09 — vérifié en rejouant l'outil sur un commit
antérieur : **l'application compte 843 h là où huit fiches en portent
962,53**, soit **−119,53 h et −8 journées** sur l'année.

Ce qu'on sait déjà : les familles d'absence concordent presque toutes
(vacances, congé parental, jour férié, formation syndicale : identiques),
la période de chaque fiche est bien le mois civil, et VBN n'a **aucune**
journée `HS` dans l'horaire — l'écart n'a donc rien à voir avec les heures
supplémentaires. Ce sont les **heures et jours PRESTÉS** qui manquent.

#### L'horaire avait des trous, mais ce n'est PAS l'explication

En cherchant l'écart, mai a paru le donner : la fiche y compte 14 jours et
112 h, l'application 12 et 96 — deux journées, seize heures, exactement
l'écart. Et ces deux journées, les 23 et 24 mai, n'existaient pas dans
`data/horaire-2026.json`.

**J'ai annoncé « mai s'explique en entier ». C'était faux**, et le client
l'a dit aussitôt : « si vide c'est une journée sans travail (repos), et je
confirme que je ne travaillais pas ces jours-là dans mon calendrier ». Une
journée qu'il n'a pas travaillée ne peut pas être les seize heures qui
manquent. **Deux nombres qui tombent juste ne sont pas une cause** — c'était
une coïncidence, et je l'ai prise pour une preuve.

L'écart de **−119,53 h reste donc entier et inexpliqué**.

#### Le trou était réel, lui, et il est corrigé

Le classeur laisse ces cellules VIDES — pas « - », rien du tout. Le
convertisseur sautait la ligne : **643 journées absentes du fichier chez 13
personnes**, pas « en repos » mais ABSENTES. Le calendrier n'avait pas de
case à peindre et `equipeDuJour()` recevait un `undefined`.

Une cellule vide devient donc un repos — **mais seulement entre la première
et la dernière journée écrite de la personne**. Sans cette borne, la règle
donnait 348 journées de repos à quelqu'un qui n'en a que 17 d'écrites sur
l'année, 193 et 69 à deux autres : **ceux-là ne sont pas en repos, ils ne
sont pas encore arrivés ou ils sont partis**, et les peindre les aurait fait
vivre dans la composition et dans les manques d'effectif de mois où ils
n'étaient pas là.

Le classeur ne dit nulle part quand quelqu'un arrive. Ce qu'il dit, c'est où
sa colonne commence à porter quelque chose : **la borne est ce qu'il écrit,
pas une date devinée.**

**Et le client l'a confirmé** : « ceux qui n'avaient rien avant sont
certainement des nouveaux qui sont arrivés en cours d'année ». Les cinq
personnes dont la colonne commence en retard le disent d'elles-mêmes — leur
première journée écrite tombe **chaque fois un LUNDI, suivi de cinq « D »
d'affilée** : la semaine d'accueil, en horaire de jour, avant d'entrer dans
une rotation. Cinq sur cinq, du 5 janvier au 14 septembre. C'est la preuve
que la borne haute du remplissage est la bonne : avant ce lundi, la personne
n'était pas là, et lui peindre des repos l'aurait fait vivre dans les manques
d'effectif de mois où elle n'existait pas.

**+20 journées**, 27 462 → 27 482, repos 7 571 → 7 591, journées prestées
**inchangées à 14 435**. Neuf règles à zéro, compteurs 76/77, manques
inchangés à 11.

**Et la comparaison aux fiches est identique au centième après la
correction** — −119,53 h comme avant. C'est la preuve que ces journées
n'étaient pas l'explication : un repos vaut zéro heure, qu'il existe dans le
fichier ou non. La correction rend au calendrier des cases qui lui
manquaient ; elle ne rend aucune heure.

#### Ce qui est ÉCARTÉ, avec ses chiffres

Trois pistes ont été mesurées et ne tiennent pas :

- **les heures supplémentaires** : VBN n'a **aucune** journée `HS` dans
  l'horaire ;
- **les journées de plus de huit heures** (`18h-06h` lu 8 h au lieu de 12) :
  **26 h sur l'année**, et dans les mauvais mois ;
- **le flex time épargné** (55 h) et les **postes prévus non prestés**
  (56 h) : février et juillet en portent beaucoup pour un écart quasi nul,
  mai n'en porte aucun pour un écart de 16 h.

#### Ce que la fiche compte, et qui n'est pas ce que l'application compte

Les lignes d'heures de chaque fiche **somment à un multiple exact de huit** :
176, 200, 208, 216, 192, 168, 144 selon le mois. La fiche **partage un total
mensuel fixe** entre prestées, vacances, maladie, congé parental et repos
compensatoire.

L'application, elle, n'a aucune notion de ce total : elle **additionne ce
qu'elle lit**, et une journée absente du fichier ne pèse rien.

**Une question reste pour le client**, et elle se répond d'une phrase : que
compte exactement la ligne « Heure(s) prestée(s) » de sa fiche — les heures
réellement faites, ou le solde du mois contractuel une fois les absences
retirées ? La première question, celle des cellules vides, est répondue et
close ci-dessus.

### Le classeur du 25/09/2026 à 15 h 23

Un nouveau récapitulatif, reçu le soir même. Procédure complète :
anonymiseur, second contrôle, conversion à côté, comparaison, installation,
contrôle croisé du dépôt, puis les trois vérificateurs.

**Ce n'est pas une correction, c'est une AVANCE** : le classeur a été rempli
sur octobre. **201 journées changent chez 34 personnes**, 27 482 → **27 574**,
journées prestées 14 435 → **14 490**.

**NPI ne s'arrêtait pas au 30/09 : sa colonne n'était pas encore remplie.**
La question posée la veille se répond d'elle-même — **92 journées** lui sont
écrites jusqu'au 31 décembre, et son compteur RTT apparaît. Il n'y avait rien
à trancher : il fallait attendre le classeur suivant. C'est la démonstration
de la règle du projet — **ne pas deviner à la place du classeur**.

**Les manques d'effectif tombent de 11 à 8 journées** d'ici la fin de
l'année, ce qu'on attend d'un mois qu'on vient de remplir : les
remplacements d'octobre sont maintenant écrits.

Ce qui bouge par ailleurs, et qui se lit dans la sortie du comparateur :
**13 compteurs** corrigés, une maladie de quatre jours posée en fin
septembre, un « Test de performance » retiré de onze cellules où il n'était
qu'un commentaire d'organisation.

**Les quatre prénoms sont revenus, et c'était prévu.** Ils étaient retirés à
la main à chaque conversion. **Ce n'est plus le cas depuis le 26/09/2026** :
le convertisseur les apprend de la feuille « Polyvalence », et une garantie
arrête la conversion si un nom du classeur subsiste. Voir « L'audit du
26/09/2026 » — l'une des quatre corrections faites à la main était fausse.

`CEPS` est apparu dans les survivants du second contrôle : c'est un centre de
formation — « Formation ARI - CEPS Seraing » — et non quelqu'un.

Neuf règles à zéro, compteurs 76/77, découpe de `comparer-fiches` à
l'épreuve, garde-fou du dépôt et contrôle croisé à zéro.

### Le classeur du 28/09/2026 à 11 h 11

`mettre-a-jour.py` : les sept portes ouvertes, installé. **32 journées
chez 22 personnes, 13 compteurs** ; 27 574 journées, prestées 14 490 →
**14 451**. Rien de structurel : les journées du 25 au 29/09 complétées
après coup (départs anticipés en RTT, reprises RHS, trois « Abs ·
Justificatif à fournir » le 28/09 — AFA, FPS, SMA —, ajustements de flex
time), FLI malade le 02/10, DWS en RTT les 21 et 22/10 remplacé par GDT,
les congés d'octobre de MGY. Un sous-effectif de plus d'ici la fin de
l'année : **le 02/10, contremaître du matin 0/1** (FLI malade), avec JBI
en D comme piste.

**JKS le 21/10** : `["DS","4h +FT","… présent à la DS prestera la pause
N"]`. La pause n'est plus dans la cellule (l'ancien classeur écrivait
`["N","DS"]`), elle est dans le commentaire ; lue par le cycle, l'épargne
s'en retranchait — 4 h de nuit au lieu de 8. `parseHoraireEntry()` lit
« prestera la pause X » quand la cellule franche est « DS » seul : c'est
exactement son 17/06, `DS + PM · 4h +FT` (`COQUILLES`), 8 h et 4 h au
compteur. Une seule journée de l'année ; les quatre sorties du
vérificateur identiques à l'octet avant et après ce correctif.

MGY le 26/09, `1,25 rhs`, se lit bien : 1 h 15 de reprise, 6,75 h
prestées.

### Le classeur du 28/09/2026 à 13 h 39

Deux heures et demie après le précédent. Sept portes ouvertes, installé :
**20 journées chez 9 personnes, 2 compteurs**, prestées 14 451 → 14 448.
AFA malade du 28 au 30/09 ; SPT malade du 30/09 au 06/10 (ses échanges
avec JKS et sa DS du 05/10 deviennent des « Abs ») ; VBN rappelé sur un
repos le 02/10 pour remplacer FLI — le contremaître du matin n'est plus en
sous-effectif ; SVE en formation distillation en 7h-15h du 28/09 au 01/10,
prime de nuit conservée les 28 et 29 (lu : prime N, presté D) ; ATR au
terrain arrière pour SMA le 28/09 ; DBE parti à 13 h le 16/10, relayé par
RDT (1 h +FT). **Nouveau sous-effectif : le 02/10, terrain arrière de nuit
0/1** — SPT malade, ASS en DTT, GKT en RTT, JKS passé en PM par échange ;
piste proposée : SKS, depuis la meunerie. **C'était faux** : sa cellule
disait déjà « Remplace SBZ », voir « Les réponses du 29/09/2026 ». Neuf règles à zéro, compteurs
76/77, intégralité à zéro.

### Le classeur du 28/09/2026 à 16 h 44

Sept portes ouvertes, installé : **17 journées chez 8 personnes**, aucun
compteur. LHR les 02 et 03/10 perd son « N ? » : `["-","N","MPE :
Remplace SPT RAPPEL 28/09 accord LH"]`, la nuit est confirmée et se lit
en rappel sur un repos (8 h sup). ASS et DBE rappelés sur un repos le
05/10 pour une intervention au gluten (N, 8 h sup chacun). FPS malade du
28 au 30/09. SPT : « Remplacé par LHR » les 02 et 03/10, et le 04/10
devient une nuit prévue non prestée (« Abs »). BLR : ses deux congés
posés les 10 et 11/10 sont renvoyés aux 14 et 15/10 (« CF »). ATR en
12h-20h le 29/09 (remise en service du F2), AFA avec un commentaire de
CIP le 06/10. **Sous-effectifs d'ici la fin de l'année : inchangés à
l'octet** (7 journées, `--manques 0929`). Neuf règles à zéro, compteurs
76/77, intégralité à zéro ; vérifié au navigateur à 320 (hors ligne),
390 et 1280 px.

### Le classeur du 29/09/2026 à 7 h 46

Sept portes ouvertes, installé : **17 journées chez 11 personnes, 1
compteur** (les RJF de KDN, 8 posés le 02/10). Prestées 14 447 → 14 445.
SMA malade du 28 au 30/09 (le « Justificatif à fournir » du 28 est parti),
PLZ la remplace au terrain arrière le 29 ; échange de pause CHD et LAA les
30/09 et 01/10 ; AAI rappelé en nuit le 30/09 au terrain arrière, BBZ
rappelé sur un repos à la même nuit ; KDN en RJF le 02/10, DWS aux
chaudières à sa place et GDT au terrain arrière ; JBI le 28/09 complète
sa matinée (« +2h rhs », lu par la règle des deux moitiés ; le départ à
14 h n'est pas pris pour un départ sans code, la journée portant déjà un
RTT) ; SPT, VM de reprise le 13/10.

**« poly.Etha »** (AAI le 30/09) est une nouvelle écriture de « poly.
Etoh », le terrain arrière : la règle « mention avalée » l'a signalée, et
le motif des postes l'accepte désormais. Sous-effectifs d'ici la fin de
l'année **inchangés à 6 journées**, compteurs identiques, neuf règles à
zéro, intégralité à zéro ; Recyclage : PLZ fermentation 13 → 12 (il est
au terrain arrière le 29/09). Vérifié au navigateur à 320 (hors ligne),
390 et 1280 px.

**J'ai posé au client une question dont la réponse était déjà à l'écran.**
La nuit du 30/09, AAI porte « Remplace SKS Remplacé par BBZ » et
l'application le montrait au terrain arrière, BBZ en distillation ; j'ai
demandé si ce n'était pas l'inverse. Le client : « BBZ ne peut pas faire
le terrain, il a été rappelé pour faire une nuit de plus. AAI, prévu en
distillation, passe sur le terrain (polyvalence ok) et BBZ vient en
distillation ». C'est la règle déjà écrite : **« remplacé par » parle du
poste PRÉVU**, pas d'une absence. Avant de douter d'un placement, vérifier
les polyvalences (BBZ n'a pas la fermentation, donc pas le terrain
arrière) : elles tranchent seules.

### Les sous-effectifs restants, relus commentaire par commentaire

Le 29/09/2026, après le terrain arrière du 02/10, les six sous-effectifs
restants ont été relus avec tous les commentaires du jour.

**Un seul avait sa réponse dans le fichier** : le 24/11, GPS porte
`["N","D-CPPT","remplacé au CPPT par TFI"]` — un autre va à la réunion,
il reste contremaître de nuit. `surSonPosteMalgreF()` lit désormais
« remplacé au CPPT (CE, DS) par X », sauf si la personne est AUSSI
remplacée à son poste : GPS le 25/03, « remplacé au CPPT par NDO remlacé
par VBN », reste hors poste. Deux journées de l'année portent la forme,
une seule change. Sous-effectifs d'ici la fin de l'année **6 → 5**, sur
l'année 269 → 268 places ; neuf règles, Recyclage et compteurs identiques
à l'octet.

**Les cinq autres, le classeur ne dit pas qui comble** :

- 05/10 AM fermentation (équipe 4) : la place de fermentation de l'équipe
  4 est sans titulaire (colonne Shift 4 Q), QBY en RTT, PAM à la
  distillation ; GSK écrit « équipe au complet » ;
- 16/10 N meunerie (équipe 5) : CDE « Abs », sans remplaçant écrit.
  **Et un commentaire n'y était pas suivi** : LCI `["N","R","en
  fermentation"]` restait en distillation. Le client, le 29/09/2026 : la
  présence ne lui était pas utile là-bas, « cependant il faut suivre ce qui
  est écrit dans l'horaire » (il fera retirer le commentaire).
  `posteEcrit()` lit désormais un commentaire qui COMMENCE par l'atelier
  (« en fermentation », « en meunerie remplace TCE »), sauf s'il doute
  (ALZ le 23/10, « …pour remplacer FPS? »). Trois journées de l'année, une
  seule change de place ; neuf règles, sous-effectifs, Recyclage et
  les compteurs sont identiques à l'octet ;
- 21 et 22/10 N chaudières (équipe 2) : ADS en RJF, sans remplaçant
  écrit, alors que le gluten a quatre personnes pour deux ;
- 12/11 N terrain arrière (équipe 1) : GDT en VA remplacé par BBZ, qui
  n'a que la distillation.

### Le classeur du 29/09/2026 à 13 h 09

Sept portes ouvertes, installé : **17 journées chez 11 personnes**, aucun
compteur. **Le classeur comble trois des cinq sous-effectifs restants** :
le 05/10 AM, ATR `["AM","fermentation"]` ; le 16/10 N, LHR « Remplace
CDE » en meunerie (le commentaire « en fermentation » de LCI est retiré,
comme le client l'avait annoncé, et SMA passe en fermentation pour CHD,
AAI au terrain arrière) ; le 12/11 N, ATR au terrain arrière pour DWS.
GPS le 24/11 perd son « D-CPPT » (« remplacé au CPPT par TFI » reste) ;
MMS remplace SPT jusqu'à 14 h 30 le 13/10 (VM de reprise). Restent les
chaudières de nuit des 21 et 22/10 : **2 journées** d'ici la fin de
l'année.

**« Poly.Ethol »** (ATR le 12/11) : troisième écriture du terrain arrière,
après « poly. Etoh » et « poly.Etha » ; la règle « mention avalée » l'a
signalée, le motif l'accepte. Neuf règles à zéro, Recyclage et compteurs
identiques à l'octet, intégralité à zéro ; vérifié au navigateur à 320
(hors ligne), 390 et 1280 px.

### Le classeur du 29/09/2026 à 13 h 28

Reçu le 30/09. Sept portes ouvertes, installé : **8 journées chez 4
personnes, 2 compteurs**. JBI le 29/09 (« 3,5 rhs ») et QBY le 29/09
(« 2h rhs », départ à 12 h) : reprises en fin de journée ; NPE le 18/10
part à 10 h (« 4h -FT »), QBY le relaie de 10 h à 14 h (« 10h-22h ·
4h +FT », lu 8 h en PM et 4 h au compteur) ; NPI en 6h-14h les 09 et
10/11, ses D des 12 et 13/11 marqués « - ». Compteurs flex time de NPE
et QBY suivis. Neuf règles à zéro, `--manques 0930` et `--compteurs`
identiques à l'octet, intégralité à zéro ; vérifié au navigateur à 320
(hors ligne), 390 et 1280 px.

### Le classeur du 30/09/2026 à 14 h 17

Sept portes ouvertes, installé : **14 journées chez 9 personnes, 4
compteurs** (RTT de CJD, GDT, PDF et VBN). Prestées 14 445 → 14 441.
VGG malade les 30/09 et 01/10 ; PDR (CT le 30/09) est désormais remplacé
par QBY au lieu de VGG ; CJD part à 4 h la nuit du 29/09 (« 2h RTT,
équipe complète ») et PDF passe cette nuit-là en RTT ; ATR en 10h-18h le
29/09 ; GDT en VA le 08/12 remplacé par DWS au terrain arrière, et son
29/10 passe de VA à RTT ; LHR : ses VA des 22 et 23/10 avancés aux 08
et 09/10. **VBN le 30/09** : `["D-CPPT","1h RTT","+1h RHS Arrivée à
09h Départ à 15h"]` — la nuit avec « D-CPPT » attendue pour trancher la
question de la prime est devenue une journée de 9 h à 15 h ; lue 6 h
(1 h RTT, 1 h de reprise par la règle des deux moitiés), prime de nuit
conservée comme pour toute journée « N · D-CPPT ». Le client l'a
tranché le même jour : les heures prestées gardent la prime que le
commentaire écrit, celle de la pause prévue sinon — la lecture était
déjà la bonne.
Sous-effectifs d'ici la fin de l'année et compteurs **identiques à
l'octet**, neuf règles à zéro, intégralité à zéro ; vérifié au
navigateur à 320 (hors ligne), 390 et 1280 px.

### Le classeur du 01/10/2026 à 9 h 25

Sept portes ouvertes, installé : **14 journées chez 9 personnes, 7
compteurs**. Prestées 14 441 → 14 437. CKS part à 13 h le 30/09 (1 h de
reprise) ; FPS : son 05/09 devient un DTT entier et le 07/09 un repos ;
KDN en RTT le 16/12, ½ VA le 17/12 et ½ DTT le 18/12, remplacé par MHI
(PM → N) ; JBA en VA le 18/12, remplacé par SPS ; LHR le 30/09 passe en
`D-CPPT · 2h RTT` (6 h) ; SVE le 30/09 et le 01/10 en formation
distillation `7h-15h · 8h +FT` — le poste entier part au compteur, 0 h
payée (section 5 de `docs/conversion-horaire.md`), compteur flex time
+16 h. **VBN le 30/09** devient `["D-CPPT","2h RTT","+1h RHS compteur à
0 Arrivée à 09h Départ à 15h"]` : lu d'abord 5 h (8 − 2 − 1), alors que
9 h-15 h en font 6. Le client, le même jour : « 6 h prestées (09-15),
+ 1 h sup faite après 15 h ». Le classeur le disait : « compteur à 0 »
(JBS le 04/03, SMK le 06/08 l'écrivent aussi) veut dire que le compteur
de récup. HS est vide — rien n'est repris. `lireJournee()` lit donc un
« +Nh RHS » accompagné de « compteur à 0 » comme N heures sup (`r.hc`,
prime de la pause payée) et non comme une reprise : 6 h prestées, 2 h de
RTT, 1 h sup. Seule journée de l'année de cette forme ; neuf règles,
sous-effectifs, Recyclage et compteurs identiques à l'octet ; la fiche
de septembre porte l'heure sup, hors ligne compris. Trois compteurs passent en négatif
au classeur : VA restant de JBA (−8), RTT restant de KDN (−6) et de SMA
(−4). Sous-effectifs d'ici la fin de l'année et compteurs **identiques
à l'octet**, neuf règles à zéro, intégralité à zéro ; vérifié au
navigateur à 320 (hors ligne), 390 et 1280 px.

### Le classeur du 09/10/2026 à 9 h 30

**La porte d'intégralité s'est fermée, sur une seule journée, et elle avait
raison.** VBN le 15/10 : le commentaire écrit « cf. 09/10 », saut de ligne,
puis la signature de son auteur et son deux-points. Le convertisseur, qui
retire toute la tête d'un commentaire quand elle nomme un auteur, emportait
le renvoi avec la signature ; l'anonymiseur, lui, ne retire que la ligne
signée, et gardait « cf. 09/10 ». Le convertisseur relève désormais ce qui
précède la DERNIÈRE ligne de la tête avant que les sauts de ligne soient
écrasés, et le garde : la signature tient sur sa ligne. Mesuré : sur ce
classeur, l'ancien et le nouveau convertisseur ne diffèrent que par cette
journée ; sur le classeur du 01/10, ils sont identiques à l'octet.

**Le garde-fou du dépôt s'est fermé ensuite** sur « Débourrage Ligne »
(TCE le 05/10, « Débourrage Ligne L » : déboucher la ligne L) — lu en
contexte, ajouté à `tools/formes-admises.txt`.

Puis sept portes ouvertes, installé : **175 journées chez 38 personnes, 14
compteurs**, et une personne de plus — **SLI**, opérateur en formation,
21 journées. **Je ne l'ai pas signalé au client, et j'aurais dû** : il a dû
préciser lui-même que c'est un intérimaire en formation meunerie. Une
ARRIVÉE du rapport se dit au client avec la question de qui elle est. YBT malade du 12/10 à la fin de l'année (65 journées, ses VA
deviennent des « Abs ») ; PDE malade du 10 au 16/10 ; FLN en congé du 29/10
au 08/11, remplacé par ALZ au terrain arrière ; MHI en congé du 23 au 28/10 ;
échanges IME/RDT (09-11/10), CJD/DBE (21-22/10), NPE/QBY (21/11) ; GBT-1
rappelé les 21 et 22/10 pour QDE. Neuf règles à zéro, compteurs **77/78**
(la nouvelle personne concorde), intégralité à zéro, découpe de
`comparer-fiches` à l'épreuve ; vérifié au navigateur à 320 (hors ligne),
390 et 1280 px.

### Le classeur du 12/10/2026 à 9 h 27

Huit portes ouvertes, installé : **51 journées chez 24 personnes, 14
compteurs**, aucune arrivée ni aucun départ. Les journées du 09 au 11/10
complétées (départs anticipés en −FT : GKT, GPS, JBI, JBS ; MHI « départ à
5h » sans code, lu en RHS par la règle du 29/09 ; GST « Abs » le 10/10 ;
VGG en « 8h -FT » le 11/10 ; échange ATA/YPE les 10 et 11/10). Plus loin :
AFA en RHS du 14 au 17/12, VGG le remplace en R-CM les 14 et 15 ; FPA au
gluten pour GSK les 28 et 29/10 ; RDT en VA et RTT les 04-06/11 et
08-09/12 ; SPS remplace QDE en nuit les 21 et 22/12. Sous-effectifs d'ici
la fin de l'année **24 → 23 journées**, 25 → 23 places (les chaudières de
nuit sont comblées). Compteurs 77/78 (FPA, l'écart connu), intégralité à
zéro.

**« Falling film »** (JBI, 02 au 04/11 et 09 au 13/11, en annotation d'un
7h-15h, sans commentaire) : mention nouvelle, 8 journées non comprises.
Ce sont les semaines de D de JBI, et il suivait déjà le projet le 26/10
(« projet falling film en distillation ») : une tâche de jour, comme
« consign. ». Elle entre dans `MENTIONS_NEUTRES` ; la journée reste un D de
8 h, et la règle des 2 h sup du projet (qui lit le commentaire) ne s'y
applique pas. Seule la règle faible change (11 → 3 mentions) ; les quatre
sorties du vérificateur sont identiques à l'octet sur le nouvel horaire.

**Recyclages** (classeur RH du 12/10/2026 à 9 h 14), onze portes ouvertes :
ATR gluten 0 → 4 et chaudières 1 → 2 (restant 17 → 12), JBI distillation
1 → 2 et contremaître 0 → 5 (restant 24 → 18), SBZ chaudières 0 → 1
(restant 12 → 11).

### Le classeur du 13/10/2026 à 10 h 17

Huit portes ouvertes en 17 s, installé : **73 journées chez 22 personnes, 9
compteurs**, aucune arrivée ni aucun départ. FLN malade du 12 au 16/10,
remplacé par ALZ puis GKT (rappelé les 14 et 15/10) ; les remplacements que
YBT, malade, portait encore dans ses commentaires (22/10, 23/10, 05/11,
19/11, 24 et 25/11) passent à JBI, rappelé ; échanges VBN/GPS (21-22/10),
VBN/FLI (09-10/11, 21-22/12), GSK/IME (02-03/12) ; ALZ en RTT le 13/10, le
23/10 et le 31/12 ; GBT en RTT le 31/10 ; SVE en RTT et VA du 12 au 14/10.
Neuf règles à zéro, compteurs 77/78 (FPA, l'écart connu), intégralité à
zéro. Sous-effectifs d'ici la fin de l'année **21 → 23 places** : le 12/12 AM
contremaître disparaît (JBI) ; apparaissent le **31/10 AM fermentation** (LHS
malade, CHD en RTT) et le **13/10 PM terrain arrière**. Celui-ci est un
**écart connu** : ALZ, qui remplaçait FLN, prend un RTT, et le classeur
couvre l'après-midi par deux 12 h — AAI `["6h-18h","4h +FT","poly. Etoh.
Remplace ALZ (FLN)"]` et GKT `["18h-6h","4h +FT",…"remplace ALZ (FLN) de
18h à 22h"]`. L'application ne sait pas additionner deux moitiés de pause
venues du matin et de la nuit ; sa propre fiche propose d'ailleurs cette
paire-là (« AAI 06-18 · GKT 18-06 »). Vérifié à 320 px (hors ligne), 390 et
1280 px.

**Deux 12 h qui se relaient tiennent le poste** (le client, le même jour :
« oui pour les 12 h pour couvrir un trou, et il faut trouver une manière pro
de l'afficher dans l'horaire »). L'écart connu ci-dessus est levé.
`relaisDouze()`, appelé par `postesDePause()` pour un poste encore vide et
jamais pour la colonne D, cherche ceux d'une AUTRE pause, la veille et le
lendemain compris, dont la plage écrite dépasse 8 h et déborde sur la pause
sans la contenir, au poste qu'ils tiennent : l'atelier écrit, dans la
cellule ou en tête du commentaire (« poly. Etoh. Remplace ALZ »), celui du
remplacé, sinon leur poste habituel. **La première version ne prenait que
la cellule**, et le 13/10 restait vide : AAI et GKT écrivent l'atelier dans
le commentaire. Les morceaux ne valent que s'ils couvrent TOUTE la pause ;
le poste compte alors une personne de plus (`o.relais`). Au Planning, les
relais s'écrivent dans la case, badge à bord pointillé d'accent et la PART
de la pause que chacun tient (« AAI 14-18 », « GKT 18-22 ») — d'abord leur
plage entière (« 06-18 », « 18-06 »), corrigée le même jour par le client :
« ils tiennent d'autres postes dans leurs pauses respectives, mais ce sont
bien eux qui partagent le PM ». L'infobulle donne leur journée. **Et j'avais
oublié leur commentaire** : le client, le même jour, « de nouveau pourquoi
pas de commentaire justificatif dans les trigrammes de ces 2 personnes ? ».
Tout badge du Planning qui a un commentaire le porte (trigramme souligné,
le clic l'affiche, `data-com`) ; les badges de relais le portent désormais
aussi, celui de la cellule qui fonde le relais (la veille si elle vient de
la veille). **À chaque nouveau badge, reprendre ce mécanisme.** Mesuré
(`--placement --tout` imprime les relais) : **40 postes couverts sur
l'année**, tous des paires 06-18 / 18-06, 14-02 / 02-14 ou 22-10 / 10-22 ;
places creuses de l'année 250 → **218** ; d'ici la fin de l'année seul le
13/10 PM disparaît ; neuf règles, compteurs et Recyclage identiques à
l'octet (les relais ne sont pas dans `gens`). `PF_DEB` entre dans la
découpe du vérificateur. Vérifié à 320 px (hors ligne), 390 et 1280 px.

### Le classeur du 13/10/2026 à 15 h 58

Huit portes ouvertes en 15 s, installé : **33 journées chez 13 personnes,
8 compteurs**, aucune arrivée ni aucun départ. AFA absent jusqu'en
décembre a désormais ses remplaçants écrits — VBN les 04/11 et 23/11, ATR
en R-CM du 02 au 06/12 — : **six sous-effectifs de contremaître
disparaissent**, 20 → 14 places d'ici la fin de l'année. AFA et ATR
échangent leur pause le 25/10 ; HKB remplace BLR (VA) en meunerie le 11/12 ; formations EPI et
ATEX de CDT et NPI ; BLR, JBA et YRS : congés corrigés ; SMA part à 12 h le
13/10, relayé par PDR. CAN est toujours en RJF les 13 et 14/10 : PDF reste
proposé à la STEP. Intégralité à zéro.

### Le classeur du 14/10/2026 à 10 h 19

Huit portes ouvertes en 15 s, installé : **14 journées chez 7 personnes,
4 compteurs**, aucune arrivée ni aucun départ. PDR en congé du 14 au
17/11 (VA, RJF), ALZ le remplace en distillation ; PLZ en RJF le 30/10,
remplacé par « CJT » — le classeur l'écrit ainsi, et c'est CJD qui porte
« Remplace PLZ » ce jour-là (passé du PM à l'AM) ; CAN rappelé le 13/10
au lieu de son VA ; PDF à la STEP pour PDE les 15 et 16/10 (le transfert
proposé par l'application est désormais écrit) ; GST part à 20 h le 13/10
(2 h RHS) ; GDT a un temps partiel à 90 % à partir du 01/10. Neuf règles à
zéro, sous-effectifs d'ici la fin de l'année identiques à l'octet,
compteurs 77/78 (FPA, l'écart connu), intégralité à zéro ; agendas
réécrits ; vérifié à 320 px (hors ligne), 390 et 1280 px.

### Le classeur du 15/10/2026 à 14 h 09

Huit portes ouvertes en 20 s, installé : **122 journées chez 47 personnes,
19 compteurs**, aucune arrivée ni aucun départ. Les journées du 13 au 15/10
complétées (la formation d'anglais du 14/10 devient des départs en RTT, RHS
ou DTT ; CAN rappelé, son RJF du 14 annulé ; LHR, BLR et ATA « Abs ·
justificatif à fournir ») ; échanges ATR/AFA (24-25/10), DBE puis PLZ
(21-22/10), ASS/IME (06-08/11 et 11-13/12) ; « Test performance sécheur 1 »
écrit du 04 au 06/11 (sans effectif demandé) ; GPO en distillation pour PAM
du 13 au 15/11, FPA en R-CM les 14 et 15/11 ; congés de JBS, MGY, NPI, LCI.
Neuf règles à zéro, compteurs 77/78 (FPA, l'écart connu), intégralité à
zéro ; agendas réécrits. Sous-effectifs d'ici la fin de l'année **14 → 15
places** : le **15/10 PM meunerie** — CDE et LHR absentes, CDE écrit
« remplacée par ? et PLZ » alors que PLZ est au projet falling film
(« SLT et BGT présents ») : le classeur ne sait pas lui-même qui est venu.
Vérifié à 320 px (hors ligne), 390 et 1280 px.

**Recyclages** (classeur RH du 15/10/2026 à 13 h 49), onze portes
ouvertes : JBI fermentation 0 → 1 (restant 18 → 17) ; VGG meunerie 4 → 5,
gluten 1 → 2, fermentation 2 → 5, distillation 0 → 1 (restant 16 → 10).

### Les chaudières d'ATR : trois raisons, trois réponses (« ABC »)

Le client, le 12/10/2026 : « ATR est bien aux chaudières les deux jours
encodés dans le fichier RH ; trouve pourquoi ». L'application en comptait
0. Les trois propositions ont été acceptées (« ABC ») :

- **A — une journée en D qui écrit l'atelier compte.** ATR le 16/09,
  `["D","chaudières"]`, troisième homme du nettoyage Bang and Clean : le D
  restait hors du compte. `calculerPolyvalence()` lit désormais la colonne
  D quand la cellule ou l'annotation nomme l'atelier (`posteEcrit()`), à
  8 h, hors poste attitré ; un D sans atelier écrit ne compte toujours pas.
  Sept journées depuis le 01/02 (ATR, VGG, CWN). `RECYC_POSTES` entre dans
  la découpe du vérificateur.
- **B — « CH » en capitales, mot entier, se lit chaudières**
  (`posteEcrit()`) : ATR le 29/06, « Présent pour redémarrage CH ». Seule
  journée de l'année à l'écrire.
- **C — pourquoi une date RH n'est pas comptée** : au clic sur un opérateur
  du recyclage, sous chaque poste, « Non comptées par l'app » donne la
  raison de chaque date RH absente des dates de l'application — « journée
  en D », « atelier non écrit (placé X) », « autre atelier dans l'horaire
  (X) », « journée de n h », « son poste attitré », « pas présent dans
  l'horaire ». `calculerPolyvalence()` garde où chacun a été placé chaque
  jour (`lieux`) ; `raisonNonCompte()` le relit, sans rien recalculer.

**B seul ne suffisait pas, et la mesure l'a montré** : le 29/06 se lisait
bien « chaudières », mais le renfort du terrain arrière (option B du
02/10) l'en retirait, ATR y étant en surnombre. Ce renfort ignorait
`x.fixe`, alors que `postesDePause()` écrit « écrit dans la cellule :
inamovible ». Il le respecte désormais. **Les sous-effectifs ne bougent
pas** (`--manques 0926` et `0101` identiques à l'octet) : le renfort ne
comble aucun manque. Le Recyclage, oui — ceux dont l'atelier écrit était
retiré pour le terrain arrière retrouvent leur journée : ATR chaudières
0 → 2 et meunerie 1 → 2, VGG meunerie 4 → 5 et chaudières 2 → 5, CWN STEP
7 → 9, FPA chaudières 6 → 10, FPS meunerie 2 → 6 et gluten 2 → 5, PLZ
meunerie 15 → 17, CDE fermentation et JBI gluten +1 ; 20 → 22 couples au
quota. ATR chaudières et VGG concordent désormais avec le classeur RH ; FPA
et FPS comptent plus que lui (le RH ne note pas toutes les journées).
Neuf règles et compteurs identiques à l'octet. Vérifié à 320 px (hors
ligne), 390 et 1280 px : ATR « 28/09 · autre atelier dans l'horaire
(T. arr.) » au gluten, FPA cinq dates expliquées, rien ne déborde.

**Les commentaires relus, le même jour** (le client : « d'autres
commentaires non compris ou utilisés à bon escient ? »). Les règles
faibles du vérificateur, lues une par une : 3 mentions non comprises et 50
motifs trop étroits. **Une seule journée à venir était fausse** : GPS le
16/10, `["PM","VM-F", … "ATEX poussières … de 08h30' à 16h30' remplacé
par JBI"]`, restait contremaître de l'après-midi à côté de JBI, qui le
remplace. « VM-F », « AM-VM » et « PM-VM » entrent dans `COQUILLES` : GPS
passe en formation comme ATA (même formation, même jour, prime recalée
sur le cycle comme toute journée F) ; DBE et RDT ne bougent pas. Mentions
non comprises 3 → 0 ; sous-effectifs, Recyclage et compteurs identiques à
l'octet ; au Planning du 16/10, CM PM : JBI seul, à 320 px (hors ligne),
390 et 1280 px. Des 50 motifs trop étroits, la plupart sont sans effet
(plages d'une formation d'une heure sur une journée F, « remplacé pa »
mal écrit sur une absence déjà codée, « remplace aussi » d'un cadre) ;
**trois journées passées perdent des heures sup écrites en plage** —
questions au client, dans « Ce qui attend le client ».

**Tranchées le même jour.** Le client : QBY « a bien fait 12h et il n'y a
pas de cellule avec du FT+ ce jour-là, donc c'est bien du HS » ; « oui »
pour JBS ; « oui HS pour JBI, et rappel le 22/06 ». `HS_TRANCHEES` pose les
4 h sup de chaque journée (`r.hc`) à la prime de leur plage — nuit pour
QBY (22 h-2 h), après-midi pour JBS (14 h-18 h), matin pour JBI
(6 h-10 h) — et `RAPPEL_DATE_TRANCHEE` lit « rappel le? » de JBI comme
« rappel le 22/06 » (rappel J). Table nommée, journée par journée, et non
une règle « plage plus longue que la pause », qui prendrait aussi des
remplacements partiels. Les deux outils qui découpent `lireJournee()` la
prennent. Avant : 0 h sup sur les trois journées ; après : 4 h chacune.
Les quatre sorties du vérificateur sont identiques à l'octet (règle de
paie seulement), découpe de `comparer-fiches` à l'épreuve.

**Le 26/10 en PM, tranché le même jour.** JBI porte `["PM","F","projet
falling film en distillation remplace en ferm-liq pour QBY"]` ; l'appli le
laissait adjoint, GPO tenant la fermentation. Le client : « JBI en
fermentation, PAM en distillation, FPS terrain et GPO gluten », puis
« il tient le poste mais suivra la formation quand même ». PAM et FPS y
étaient déjà ; JBI et GPO entrent dans `POSTE_DU_JOUR`. **Et la table ne
suffisait pas** : GPO, mis au gluten, en surnombre, partait au terrain
arrière en renfort (le même renfort que pour ATR le 29/06). Un poste
tranché par le client est désormais inamovible (`x.fixe`), comme un atelier
écrit. Planning du 26/10 PM : ferm. JBI, glut. GPO · GSK · RDT, t. arr.
FPS, dist. PAM, à 320 px (hors ligne), 390 et 1280 px ; VGG le 27/09 ne
bouge pas ; les quatre sorties du vérificateur identiques à l'octet (le
26/10 est à venir).

**Puis les autres journées du projet falling film relues** (le client :
« suite »). Le projet garde chacun à son poste (`PROJETS_SUR_POSTE`) ;
un balayage des journées à venir, atelier écrit contre atelier placé, a
montré trois personnes qui n'y étaient pas : SPS le 26/10, `["7h-15h",
"F", … "maintien prime N RCO et LDY présents"]`, comptée aux chaudières
de nuit ; SKS le 15/10 en « D-F », comptée en meunerie l'après-midi ; PLZ
le 15/10, « SLT et BGT présents ». Une plage de jour, « D-F » ou d'autres
nommés « présents » sortent désormais du poste. **« Remplacé par » avait
été ajouté aussi, et c'était faux** : trois sous-effectifs sont apparus,
qui n'existent pas — ATR ne remplace ATA le 15/10 que de 12 h 30 à 13 h 30,
SBZ le 09/10 et GDT le 05/10 sont remplacés parce qu'ils vont eux-mêmes
remplacer quelqu'un. Retiré. Les quatre sorties du vérificateur sont
identiques à l'octet (aucun manque ne bougeait par ces trois-là) ;
Planning du 15/10 vérifié à 320 px (hors ligne), 390 et 1280 px.

**SLT le 28/09 en PM, « remplace CDE »** (le client, le 13/10/2026 : « SLT
remplace CDE en meunerie »). Sa cellule `["PM","","remplace CDE"]` n'écrit
pas l'atelier ; CDE porte « Abs · remplacée par SLT ». Le Planning le
laissait au gluten (sa ligne 9) et envoyait PLZ en meunerie : « remplace X »
n'était lu qu'en DERNIER recours, après le poste attitré (sauf pour un
opérateur en formation). **J'ai d'abord écarté la règle générale, et
c'était contraire à la doctrine** : elle déplaçait une quarantaine de
journées, j'ai posé SLT seul dans `POSTE_DU_JOUR`. Le client, aussitôt :
« comme toujours, le commentaire doit toujours être l'info prioritaire ».
Les deux trous qu'elle créait (26/07, 06/07) n'en ajoutaient pas : ils
DÉPLAÇAIENT un trou existant vers le poste que le commentaire libère.

**« Remplace X » prime désormais sur le poste attitré, pour tout le
monde** (`postesDePause()`) : le remplaçant prend `posteAttitreLe()` du
remplacé ce jour-là, s'il en a la polyvalence. Pas quand l'atelier est
écrit ou tranché, pas pour un contremaître, pas quand X est présent dans la
même pause, et pas pour un remplacement partiel (`remplPartiel()`) : une
heure dans le commentaire, une plage de moins de 8 h, un « ? », ou un
« R-CM » écrit. **Ces deux dernières gardes viennent de la mesure** : sans
elles, cinq adjoints en R-CM (ATR le 13/02 « remplace SKS remplace PBL »,
VGG le 28/07…) quittaient le contremaître pour l'atelier du trigramme, et
« remplace QBY? » (JBI le 18/11) se lisait comme sûr. SLT n'a plus besoin de
`POSTE_DU_JOUR` : la règle rend son placement à l'identique.

**Et la table fuyait** : `posteAttitreLe()` demande le poste attitré avec
une cellule vide, et `posteTenu()` y appliquait `POSTE_DU_JOUR`, si bien
que le poste tranché devenait le poste attitré du jour et que la journée ne
comptait pas au Recyclage. La table ne vaut plus que pour une journée
écrite.

Mesuré par `--placement --tout` (nouveau mode du vérificateur, toute
l'année pause par pause, comparé ligne à ligne) : **37 pauses changent**,
toutes passées sauf les 27-29/10 (GKT « remplace QBY » passe du terrain
arrière à la distillation, aucun manque ne bouge) ; neuf règles, compteurs
et `--manques 1013` identiques à l'octet ; places creuses de l'année
279 → 277 ; Recyclage 22 → 23 couples au quota (AAI fermentation 3 → 8,
PLZ distillation 9 → 10 ✓, SLT meunerie 1 → 2, GKT, SKS, JKS +1 ou 2 ;
PLZ fermentation 13 → 10, PAM, HKB, ALZ, VGG −1). La découpe de
`POSTE_DU_JOUR` se ferme sur `};`. Vérifié à 320 px (hors ligne), 390 et
1280 px.

**Les sous-effectifs disent qui remplacer, et le poste pour poste vient en
tête** (le client, le 13/10/2026 : « en plus de mettre le poste où il manque
quelqu'un, dire quelle est la personne qu'il faut remplacer ; dans les
propositions, s'il y en a, toujours proposer le poste pour poste en premier
lieu »). Sous la ligne du poste, « À remplacer » nomme ceux qui étaient
PRÉVUS à cette pause (`r.s`) et dont c'est le poste habituel ce jour-là
(`posteAttitreLe()`), avec leur motif : malade, le code du congé, absent
(poste prévu non presté), formation ou le code de jour (`aRemplacer()`).
Dans `caCandidats()`, ceux dont c'est AUSSI le poste habituel quittent les
cadres « En D », « Change de pause » et les rappels pour un cadre « Poste
pour poste », le premier de la fiche : D et changement de pause d'abord,
rappels ensuite, permanents avant intérimaires. Il vaut pour les
sous-effectifs et la Recherche ; le Congé n'y compte pas les rappels.
Mesuré le 13/10 : 21 fiches sur 21 nomment qui remplacer, 20 ont un poste
pour poste.

**Puis plus intuitif, et le contremaître distingué de l'adjoint** (le
client, le même jour : « le poste pour poste doit faire la différence entre
contremaître et adjoint ; la ligne avec la personne à remplacer n'est pas
professionnelle ni dans le même style que les propositions »). « À
remplacer » devient la première section de la fiche, du même style que les
propositions, intitulé et badges en rouge (`.capaire.arem`), le motif en
clair à côté du trigramme : maladie, congé et son code, flex time, formation. Pour un poste
de contremaître, le poste pour poste ne garde que les contremaîtres ; les
adjoints proposés — l'adjoint déjà dans la pause (« Même pause », retiré
des chaînes), en D, d'une autre pause ou en rappel — ont leur section,
« Adjoint faisant fonction », juste après (`t.adj`). Le 23/10 PM : À
remplacer AFA (congé VA) ; poste pour poste YPE, GPS ; adjoint faisant
fonction JBI (même pause), VGG. Vérifié à 320 px (hors ligne), 390 et
1280 px.

**La prolongation 12 h poste pour poste passe avant l'adjoint** (le client,
le 13/10/2026 : « si les prolongations 12h sont poste pour poste cela doit
être avant adjoint faisant fonction »). Quand tous les membres proposés de la
paire ont le poste vide pour poste habituel ce jour-là, le cadre
« Prolongation 12 h » se place juste après « Poste pour poste » ; sinon, il
reste après le changement de pause. La paire 06-18 / 18-06 se prend au poste
du jour, et non au poste habituel : un adjoint qui y figure la laisse donc
après l'adjoint. Mesuré sur les 22 fiches à venir : les 26/10 et 27/10 (FLI
06-18, ATA 18-06) passent avant l'adjoint ; les 24/11 et 25/11 (VGG dans la
paire) restent après. Vérifié à 320 px (hors ligne), 390 et 1280 px.

**Un adjoint qui « remplace » un contremaître tient le poste de
contremaître** (le client, le 13/10/2026, sur le 23/10 encore en
sous-effectif : « JBI est bien là et son commentaire indique bien la
solution »). JBI porte `["AM","PM","MPE : Remplace AFA …"]`. La règle
générale « remplace X » écartait tout remplacé dont le poste habituel est
contremaître. `atelierDuRemplace()` le rend désormais à un adjoint
(`estCadre` sans `estContremaitre`). Mesuré par `--placement --tout` : quatre
pauses changent (16/03 N, JBI ; 29/04 AM, ATR ; 20/06 PM, couvert par le
relais ATA 14-18 + ATR 18-22 ; 23/10 PM, JBI). Les sous-effectifs à venir
passent de 22 à **21** places. Les neuf règles, les compteurs et le Recyclage
sont identiques à l'octet. Même demande : « À remplacer » écrit « Absent »
au lieu de « Malade », et le congé par son seul code (« VA », « RTT »,
« -FT »).

**Et la première mesure a montré un faux trou, plus ancien.** Le 21/12,
« À remplacer » donnait CGI avec « 8H +FT ». Sa cellule, `["N","8h +FT",
"remplace BLR"]`, dit qu'il tient la meunerie de nuit et verse le poste
entier au compteur (section 5 de `docs/conversion-horaire.md`) : 0 h
payée, donc `equipeDuJour()` le rangeait en congé. Un code d'épargne
(`ft>0`) sans heure payée laisse désormais la personne à sa pause. 92
journées de l'année portent « 8h +FT » ; **86 pauses changent**, les places
creuses de l'année passent de 277 à **249**, et d'ici la fin de l'année de
22 à **21** (la meunerie du 21/12 disparaît) ; neuf règles et compteurs
identiques à l'octet ; Recyclage : cinq cases d'une journée, 23 couples au
quota inchangés. Vérifié à 320 px (hors ligne), 390 et 1280 px.

### Un commentaire peut relever l'effectif d'une journée

Le client, le 25/09/2026 : « quand il est écrit "Test de performance
Vyncke", c'est pour que ces dates-là il fallait 3 opérateurs chaudière en AM
et PM ».

**Je l'avais rangé parmi les commentaires d'organisation**, c'est-à-dire
nulle part — je venais d'annoncer qu'il avait « quitté onze cellules », comme
si sa disparition n'ôtait rien. C'est la règle de tête du projet appliquée à
l'effectif : **le commentaire dit ce qui a réellement été demandé, et il
prime**. Un poste tenu à deux ce jour-là n'est pas complet, et le module des
manques l'annonçait vert.

**LA PHRASE EST LUE, PAS LA DATE.** Une table de journées — comme
`POSTE_TRANCHE` ou `EQUIPE_TRANCHEE` — aurait vieilli au premier classeur
suivant. Ici le classeur ÉCRIT l'exigence ; il n'y a rien à décider à sa
place, seulement à lire. Le motif l'a prouvé sur-le-champ : il a trouvé
**le 09/03, que le client n'a pas cité** — « Nettoyage Bang and Clean.
Présence de 3 opérateurs obligatoire en AM et PM ». Même exigence, autre
raison. Une table des journées « Vyncke » l'aurait manqué.

Mesuré sur les 27 574 journées : **15 journées**, toutes de cette forme,
toutes à 3, et **aucune autre cellule attrapée**.

**Les pauses viennent du TEXTE** : « en AM et PM » sur quatorze journées,
« en AM, PM et N » sur celle du 29/09. Les deviner aurait ajouté une nuit
que personne n'avait demandée.

**Le poste, lui, n'est pas écrit — et le classeur le corrobore quand
même.** Sur les 17 personnes qui portent la phrase, **14 sont des
chaudières de la ligne 9**, et les trois autres ont « chaudières » écrit
dans leur annotation ce jour-là : c'est le renfort envoyé au poste. Ce n'est
donc pas la parole du client contre le silence du fichier — les deux disent
la même chose.

La règle ne fait que **monter** l'effectif : un commentaire ne peut pas
vider un poste, et le jour n'attend toujours personne.

**Ce que cela déplace, mesuré** : sur l'année, les places creuses passent de
**377 à 384** et les journées de 188 à 189 — cinq journées de janvier où les
chaudières tenaient à deux ou un pour trois demandés (22, 23, 26, 27 et
28/01). Le 09/03 et les 22 au 25/09 ne bougent pas : ils étaient bien trois.
Fermentation **+1**, par le rééquilibrage — une place qui manque ailleurs en
déplace une autre, c'est le mécanisme déjà documenté.

**Et une seule journée à venir est concernée : le 29/09 au matin**, qui
passe de « complet » à **`2/3`**. Vérifié au navigateur, à 390 et 1280 px :
le module « Postes en manque » l'affiche, entre le terrain arrière du 27 et
le gluten du 30. Les manques d'ici la fin de l'année passent de 8 à 9.

**Et le motif était trop étroit, comme la douzième règle le prédit.** Deux
journées portent la même exigence écrite autrement et lui échappaient :
le **13/07**, « Présence de 3 opérateurs obligatoire », sans dire la pause,
et le **16/09**, « 3 opérateurs en poste par pause » — ATR y est noté
« Renfort chaudières… en D comme 3ᵉ homme ». Un motif qui lit moins qu'il ne
croit ne ment pas : il se tait.

`RENFORT_TRANCHE` porte la décision du client pour le 13/07 — « c'est en AM
surtout qu'il faut être 3 ». Elle **COMPLÈTE** le classeur au lieu de le
corriger, d'où une fusion par le maximum : c'est ce qui la distingue de
`POSTE_PERIODE`, qui vient en premier justement pour effacer ce que le
classeur écrit. L'après-midi n'y figure pas alors que trois cellules du
13/07 sont en PM — le client a dit « surtout en AM », et inventer une
exigence ferait apparaître un manque qui n'a jamais existé.

La journée passe à **`AM Chaudières 2/3`** : sur l'année, 384 → **385**
places creuses et 189 → **190** journées. Rien ne bouge d'ici la fin de
l'année, le 13/07 étant passé.

**Le 16/09 : « par pause » veut dire AM et PM.** Le client, le 25/09/2026 :
« c'était 3 en AM et en PM ». La nuit n'y est donc pas — et le classeur dit
la même chose de lui-même, toutes les journées renforcées de l'année étant
en AM et PM, la seule exception nommant explicitement « en AM, PM et N ».
La journée passe à `AM Chaudières 2/3 · PM Chaudières 2/3`.

**Et une exigence que le classeur porte encore peut ne plus valoir.** Le
client, le même jour : « c'est fini aujourd'hui ». Le classeur reçu le
25/09 avait déjà retiré le commentaire de **13 cellules sur deux
journées** — 5 des 6 du 25/09, 8 des 9 du 29/09 — mais il en a laissé UNE de
chaque, et chaque fois celle du **renfort lui-même**, venu en 7h-15h avec sa
prime de pause. Un reste de nettoyage, pas une exigence.

`RENFORT_CLOS` lève la journée du **29/09**, la seule qui soit APRÈS
aujourd'hui. Le 25/09 garde la sienne — « fini aujourd'hui » se lisant
« aujourd'hui compris » — et cela ne change aucun chiffre, les trois
opérateurs y étant.

**C'est la seule table du projet qui RETIRE quelque chose**, d'où son nom à
elle. La confondre avec `RENFORT_TRANCHE`, qui ne sait qu'ajouter, ferait
disparaître un renfort réel le jour où l'on s'y tromperait.

Mesuré : les journées avec un manque passent de 190 à **189** sur l'année,
les places creuses restent à **385** — le 16/09 en ajoute deux, le 29/09 en
retire autant une fois le rééquilibrage refait. **D'ici la fin de l'année,
retour à 8 journées**, et le 29/09 a bien disparu des pastilles « Postes en
manque » — vérifié au navigateur à 390 et 1280 px.

`renfortDuJour()` est mémoïsée par journée : elle balaie les 77 colonnes, et
`postesDePause()` l'appelle trois fois par jour. Elle entre dans la découpe
du vérificateur avec ses trois constantes — sans quoi l'outil aurait rejoué
un `attenduAuPoste()` qui ne sait plus lire son troisième argument.

### Le vocabulaire de la maison : « absence » veut dire MALADIE

Le client, le 25/09/2026 : « attention que chez nous "Absence" veut dire
maladie ; quand c'est une prise de congé on dit "Congé" ».

C'est la même distinction qu'il avait donnée le 21/09 pour l'onglet Équipe —
« il faut différencier absent et en congé ; les absents ne sont que les
personnes malades » — mais elle ne valait que pour les CARTES du Résumé. Le
reste de l'application appelait encore « absence » tout ce qui n'est pas
presté.

**Et un endroit ne se contentait pas d'un mot de travers : il disait le
contraire du code.** La légende rangeait `ABS` dans la colonne « Compteurs
et NON PAYÉ », avec la définition « absence injustifiée ». Or
`ALIAS_HORAIRE={"ABS":"MAL"}` le traduit en `MAL`, qui est `{c:"MAL",
k:"SMG"}` — **maladie, salaire garanti**. Le code avait raison depuis le
début ; c'est la légende qui mentait, et dans le sens qui coûte cher. `ABS`
est passé dans la liste des journées PAYÉES, à côté de `SMG`.

Sept autres emplois du mot sont repris dans son vocabulaire :

| Où | Avant | Après |
|---|---|---|
| légende de l'année | Absence | **Congé ou maladie** |
| légende du mois | absence — non presté | **congé ou maladie — non presté** |
| compteurs | Absences de l'année | **Congés et maladie de l'année** |
| liste des codes | Absences payées | **Congés et maladie payés** |
| son sous-titre | postes, absences et primes | **postes, congés, maladie et primes** |
| aide de la ligne | le menu pose une absence | **pose un congé ou une maladie** |
| infobulle de l'année | « Absence » + le code | **le code seul** — il se suffit |

**Deux libellés restent « absence », et c'est voulu** : « heures d'absence
assimilées à du travail » et « absence non rémunérée » sont les intitulés de
la FICHE DE PAIE du secrétariat social. Ils recopient un document, pas le
parler de l'usine — les renommer ferait perdre la correspondance ligne à
ligne avec la fiche, qui est tout l'objet de l'onglet Contrôle.

### Le relais de la fermentation se fait tout seul, et le doublon est voulu

Le client, le 25/09/2026 : « CHD arrive dans l'équipe 5 ce lundi et
remplacement LCI à partir de là ».

**Rien n'a été codé pour cela**, et il ne fallait rien coder : deux
mécanismes indépendants s'accordent déjà.

Le CLASSEUR porte l'arrivée de CHD — il ne rejoint pas l'entreprise, il
change d'équipe, de la 4 vers la 5. Sa rotation ne coïncide avec celle de
l'équipe 5 que **1 à 5 journées par mois de janvier à septembre, puis 26 en
octobre** ; il est en repos les 25, 26 et 27, et **le lundi 28 il tombe
exactement sur elle**. Sa ligne 9 dit déjà « Shift5 → Fermentation ».

`POSTE_PERIODE` fait sortir LCI de la fermentation le 30/09. Le relais se
lit donc de lui-même :

| Jour | Fermentation éq. 5 |
|---|---|
| 25 au 27/09 | LCI seul, au matin |
| **lundi 28/09** | **CHD et LCI ensemble**, en après-midi |
| mardi 29/09 | CHD en après-midi, LCI en nuit |
| mercredi 30/09 | CHD seul — LCI passe en distillation |

**Le doublon du 28 et du 29 n'est pas un défaut, c'est le tuilage** : deux
journées où le partant et l'arrivant tiennent le poste ensemble. Ne pas le
« corriger » en croyant qu'une place unique a été violée — la règle d'une
place par personne porte sur la COMPOSITION, pas sur le nombre de personnes
à un poste un jour donné.

### Ces semaines-ci sont exceptionnelles

Le client, le 25/09/2026 : « ces semaines-ci c'est exceptionnel mais il y a
une transition des postes de certains opérateurs ; tout devrait rentrer
dans l'ordre dans les semaines qui viennent mais il se peut qu'il y ait des
trous ces semaines-ci ».

**À lire avant de courir après les manques d'effectif de septembre et
d'octobre.** Les trous qui restent ne sont pas tous des défauts de lecture :
une partie est la réalité du terrain pendant la transition. C'est aussi ce
qui explique `POSTE_PERIODE` — un poste qui change à une date n'est pas une
bizarrerie du classeur, c'est cette transition-là.

### Une absence qui finit aujourd'hui le dit

Le client, le 23/09/2026 : « pourquoi pas de durée pour la maladie de
GJR ? » — parce que le 23/09 était le DERNIER jour de sa série, et que le
rendu se taisait au lieu de le dire. `finAbsence()` rend la dernière journée
de la série ; quand il n'y en a pas au-delà d'aujourd'hui, elle rend `null`,
et la pastille n'écrivait rien.

« MAL » tout seul ne disait pas si l'absence s'arrête là ou si on ne sait
pas jusqu'à quand. Elle écrit maintenant **« MAL · dernier jour »**, ce qui
est une information et non un vide — GJR est « Abs » du 15 au 23/09, en
repos du 24 au 27, et reprend le 28.

**Les malades se lisent du retour le plus proche au plus lointain.** Le
client, le 26/09/2026 : « les absents maladie doivent être triés par dates
de retour (le plus court au plus long) ». Le tri se fait au RENDU de la
carte « Hors poste », qui retriait chaque groupe par catégorie et
trigramme — un tri posé dans `equipeDuJour()` s'y faisait défaire, et la
première version l'a montré au navigateur : huit malades dans le désordre.
Une série qui finit aujourd'hui (« dernier jour ») vient en tête ; à date
égale, l'ordre habituel. Congés et repos gardent le leur. Vérifié à 390 et
1280 px, hors ligne compris : 27/09, 27/09, 30/09, 11/10 … 27/12.

**Et la pastille dit « Absent jusqu'au 27 Septembre »**, et non plus « MAL ·
jusqu'au 27 sept. ». Le client, le 26/09/2026 : « au lieu de MAL, il faut
indiquer Absent jusqu'au 27 Septembre ». Chez nous absent veut dire malade :
le code n'ajoutait rien. Le dernier jour s'écrit « Absent jusqu'à
aujourd'hui ». Les congés gardent leur code (« RJF · dernier jour »), qui
dit lequel. **À 320 px la phrase sortait de la carte** : la règle qui la
laisse passer à la ligne sur téléphone était écrite AVANT celle qui
l'interdit, et perdait à spécificité égale — le piège de la requête média,
une quatrième fois. Elle est posée après ; le jour et le mois sont liés par
une espace insécable pour ne pas se séparer.

**Les congés n'avaient pas de fin, et disaient tous « dernier jour ».** Le
client, le 26/09/2026 : « pourquoi ceux en congé sont indiqués dernier
jour ? ». Ce jour-là c'était vrai pour les trois — un seul jour chacun —,
mais par hasard : `equipeDuJour()` ne calculait la fin que pour la maladie,
et la pastille d'un congé écrivait « dernier jour » sur n'importe quelle
journée, le premier jour de trois semaines compris. `finAbsence()` reçoit
désormais la famille `"CONGE"`, qui **enchaîne tous les congés d'une
journée entière** : JBI en VA le 20/04 puis en RJF le 21/04 reprend le 22, et
s'arrêter au changement de code aurait redit « dernier jour » le 20. La
maladie reste sa propre famille. Vérifié horloge au 20/04 : LCI « VA ·
jusqu'au 22 avr. », JBI « jusqu'au 21 avr. », CKS seul en « dernier jour » ;
les quatre sorties du vérificateur identiques à l'octet.

**Puis jusqu'à la reprise du travail, repos compris.** Le client, le même
jour, devant LDY — RJF le 30/09, RHS le 01/10, trois repos, RJF, RJF, VA,
quatre repos, premier poste le 12/10 : « jusqu'à la reprise du travail ».
La série « CONGE » court donc sur tout congé d'une journée entière ET tout
repos, et s'arrête à la première journée prestée, à une maladie ou à un
poste prévu non presté. Une journée entière de flex time repris (« 8h
-FT ») compte comme un congé : ses heures sont payées mais personne ne
vient — LHR le 26/09 reprend le 28, pas le 27. La pastille dit donc la
REPRISE : « RJF · reprise le 12 oct. », « · reprise demain ». « Jusqu'au
dimanche » se serait moins bien lu que « reprise le lundi ». La maladie ne
bouge pas : « Absent jusqu'au » son dernier jour de maladie. Vérifié au
30/09 (LDY reprise le 12 oct., 15 congés datés) et au 20/04 (FLN, TP puis
VA entrecoupés de repos, reprise le 13 mai — contrôlé jour par jour) ;
sorties du vérificateur identiques à l'octet.

**Congé et repos ne font plus qu'une ligne, triée par reprise.** Le client,
le 26/09/2026 : « repos et congés doivent être mélangés car les repos aussi
ont une reprise ». Dans « Hors poste », on cherche QUAND chacun revient ;
congé ou repos ne change pas la question. Chaque repos reçoit sa date de
reprise par la même série « CONGE », et la ligne « Congé et repos » se trie
du retour le plus proche au plus lointain : « NRD RJF · reprise demain »,
« AFA Repos · reprise le 28 sept. » … « ATA Repos · reprise le 10 oct. ».
Restent sans date, en fin de ligne : le poste prévu non presté (« AM
prévu ») et la personne dont la colonne est vide ce jour-là — pas encore
arrivée. **Le calcul se fait au rendu, pas dans `equipeDuJour()`** : le
module des manques la rejoue sur des mois, et une trentaine de séries par
jour y coûterait pour rien. `par.off` est inchangé, de sorte que la barre
du haut dit toujours « Repos ». Vérifié au 26/09 et au 20/04, à 320, 390
et 1280 px, hors ligne compris ; neuf règles et `--manques` identiques.

**Puis regroupés par date.** Le client, le 26/09/2026, devant sa capture —
dix-neuf lignes « Repos · reprise le 28 sept. » d'affilée : « penses-tu qu'il
faut regrouper les noms par date ? », puis « optimise au mieux ce cadre-là
avec absences et personnes en congé ». Les deux lignes, Absents et Congé et
repos, se lisent désormais par DATE : une colonne étroite porte « Dim.
27 sept. », « Demain », « Lun. 28 sept. », et les trigrammes se rangent à
côté. « jusqu'au » et « reprise le » ne s'écrivent qu'une fois, sous
l'intitulé de la ligne. Le trigramme ne garde que ce que la date ne dit
pas : le code d'un congé (RJF, VA, RHS, « AM prévu ») — rien pour un repos
ni pour une maladie ; l'infobulle garde la phrase entière. **Le cadre passe
de 906 à 594 px de haut à 390 px** (34 lignes de congés et repos en font
onze). Sous 380 px la date passe au-dessus de ses trigrammes : à côté, elle
leur laissait 20 px et ils s'empilaient un par ligne — **une première
tentative, sortir l'intitulé de la ligne au-dessus des dates, a échoué** :
la table garde ses largeurs de colonnes. 930 px à 320 px, rien ne déborde à
320, 390 et 1280 px, hors ligne compris.

**Deux cadres à eux, et plus aucun code.** Le client, le même jour : « peut-être
pas utile de marquer le type de repos vu que tout est mélangé et que le
cadre a déjà le nom de congé et repos ; pareil pour les absents ; je veux
également séparer les deux cadres ». « Absents » (maladie · jusqu'au) et
« Congé et repos » (date de reprise) sont deux cartes, avec leur compte dans
le titre ; « Hors poste » ne garde que ce qui reste — la ligne Jour. Sous
chaque date, les trigrammes seuls : le code (RJF, VA, « AM prévu ») ne vit
plus que dans l'infobulle. Sorties du tableau, les dates gagnent la largeur
de l'intitulé et du compte : **à 320 px elles tiennent à côté de leurs
trigrammes**, et la règle qui les mettait dessus sous 380 px est partie.
390 px : Absents 236 px, Congé et repos 345 px ; rien ne déborde à 320, 390
et 1280 px, hors ligne compris.

**Puis en tuiles.** Le client, le 26/09/2026, capture à l'appui — prise sur
la version d'AVANT les deux cadres, que son téléphone n'avait pas encore
reçue : « il y a moyen de mieux organiser ça pour que cela fasse moins vide
et mieux réparti ». En lignes, une date à une personne laissait les trois
quarts de la largeur vides. Chaque date est désormais une TUILE — la date
en haut, les trigrammes dessous —, en grille de cases d'au moins 96 px :
trois côte à côte à 390 px, deux à 320. La largeur suit le nombre de
personnes : une ou deux, une case ; trois ou quatre, deux cases ; au-delà,
la ligne entière. `grid-auto-flow: dense` comble les trous avec les petites
tuiles — ce qui plaçait une date avant une plus proche (le 29/09 avant le
28/09). **Le client l'a vu aussitôt** : « ce n'est plus vraiment par ordre
chronologique ». La grille est devenue une RANGÉE QUI S'ENROULE : chaque
tuile prend la largeur de ses trigrammes, dans l'ordre strict des dates, et
s'élargit pour finir sa ligne — ni trou, ni date déplacée. Les « une,
deux ou toute la ligne » selon le nombre de personnes sont partis avec la
grille : c'est le contenu qui décide. Vérifié en clair et en sombre, à
320, 390 et 1280 px, hors ligne compris.

**Puis dans le style des sous-effectifs.** Le client, le 28/09/2026 :
« présenter dans le même style les absents et personnes en congé ». Les
tuiles cèdent la place à des rangées séparées d'un filet : la date à
gauche, écrite comme aux sous-effectifs (« MAR. 29 SEPT. »), les
trigrammes en étiquettes à droite ; la personne choisie a le bord et le
trigramme à l'accent. **La date tient sur une ligne, et non en bloc** : le
bloc de trois lignes des sous-effectifs, essayé d'abord, montait les deux
cartes à 1 300 px pour vingt dates d'un trigramme — 789 px ainsi à 390 px.
Rien ne déborde à 320 (hors ligne), 390 et 1280 px, en clair et en sombre.

**Les dates proches en mots, et une coupure par semaine.** Le client, le
28/09/2026, parmi quatre pistes proposées : « A et C ». Dans les deux
cartes, « Aujourd'hui », « Demain », puis le jour seul (« Mercredi »)
jusqu'à six jours ; au-delà, la date comme avant, et l'infobulle de la
rangée garde toujours la date complète. Des intertitres « Cette semaine »,
« Semaine prochaine », « Plus tard » coupent la liste, la semaine allant du
lundi au dimanche autour du jour de l'usine. Les deux pistes écartées :
replier la suite (B) et mettre sa propre équipe en tête (D). 923 px à
390 px ; rien ne déborde à 320 (hors ligne), 390 et 1280 px, en clair et
en sombre ; vérificateur identique à l'octet.

**Et la date quand même.** Le client, le même jour : « quand même indiquer
la date ? ». « Mercredi » seul obligeait à compter les jours : le mot reste
en gras, et « 30 sept. » s'écrit en petit dessous. 965 px à 390 px.
Puis, « moyen d'uniformiser » : la même forme pour TOUTES les rangées,
« Mardi / 6 oct. » au lieu de « MAR. 6 OCT. » au-delà de six jours —
l'intertitre de semaine dit déjà si c'est proche. 1 026 px à 390 px.

**Et les sous-effectifs aussi** (« ça aussi même style ? ») : mêmes
intertitres de semaine, même date en deux lignes. La mise en forme vit
dans UNE fonction, `dateEnMots()`, que les trois cadres appellent — deux
copies d'une même règle divergent. Sous 380 px, « Terrain arrière »
devient « T. arrière » dans les sous-effectifs, qui sinon se coupait.
Vérifié à 320 (hors ligne), 390 et 1280 px, en clair et en sombre ;
vérificateur identique à l'octet. Puis le mois en entier sous le jour
(« 30 septembre ») : « il y a la place » — et c'est mesuré, il tient dans
la colonne de date des trois cadres jusqu'à 320 px.

**Trois retouches aux sous-effectifs** (le client, le 28/09/2026, « go »
sur trois pistes proposées) : l'étiquette « Remplaçants possibles » part,
une flèche « → » précède les noms — le 05/10 tient de nouveau sur une
ligne ; « Aucun remplaçant » devient une étiquette rouge pâle, de la forme
des étiquettes de noms, parce que c'est l'information la plus urgente ;
l'équipe passe sous la date, en gras, quand tous les manques du jour sont
de la même équipe (toutes les journées au 28/09) — sinon chaque fiche
garde la sienne. Libérée de l'équipe, la ligne du poste écrit « Terrain
arrière » en entier même à 320 px. Piste écartée : supprimer la barre de
repli « 7 journées ». Vérifié en clair et en sombre, à 320 (hors ligne),
390 et 1280 px ; vérificateur identique à l'octet.

**Puis la barre de repli part, et les trois cadres s'alignent.** Le
client, le même jour : « retire-la et regarde si rien ne peut être mieux
placé ou aligné ». Le compte (« 7 journées ») passe sous le titre, comme
celui de « Équipes du jour » ; `#mqFold`, son écouteur et la clé
`ui/mqFold` sont retirés. Les cadres rognent leurs coins (`overflow:hidden`)
pour que l'intertitre de semaine, désormais tout en haut, n'en dépasse pas.
La colonne de date fait la même largeur dans les trois (84 px, 72 sous
380 px) : mesuré, les dates commencent au même pixel et le contenu aussi
(33 et 127 px à 390 px, 33 et 111 à 320). Le cadre passe de 640 à 603 px.

**Trois accolades orphelines dans la feuille**, dont deux d'avant ce
changement : un « } » seul au niveau de la feuille avale la règle qui le
suit (ici `.eqfold>summary`, que plus rien n'emploie). Retirées ; la
feuille est équilibrée, ce qu'un petit compteur d'accolades vérifie en
une ligne — à relancer après toute découpe de CSS.

**Puis sous « Équipes du jour ».** Le client, le 28/09/2026 : « on peut
mettre les postes en sous-effectif sous les équipes du jour ». L'onglet se
lit désormais : Mon prochain poste, Équipes du jour (le tableau, les absents, les congés
et les repos), Postes en sous-effectif. Le bloc est placé APRÈS les deux cadres
Absents et Congé et repos, et non entre eux et le tableau : ils font partie
de la même section, qu'il ne faut pas couper. **Le clic sur une journée
remonte désormais**, et la barre du haut se redéplie en remontant : viser
`#eqCorps` avec `scrollIntoView` la laissait passer PAR-DESSUS la barre du
jour (−34 px mesurés). Le clic vise donc la barre du jour, décalée de la
hauteur de l'en-tête. Mesuré : elle arrive à 76 px du haut sous une barre
de 57 px (390 px), à 117 sous 98 (1280 px). Vérifié à 320 (hors ligne),
390 et 1280 px ; neuf règles à zéro.

**Les deux cadres disent AUJOURD'HUI, quel que soit le jour affiché.** Le
client, le 28/09/2026 : « il ne faut pas que les listes absent/congé soient
adaptées par rapport à la date sélectionnée mais par rapport à la date du
jour ». Il avait cliqué sur le sous-effectif du 16/10 et lu YBT « en congé,
reprise le 22 oct. », alors qu'il est malade jusqu'au 11/10 : c'était juste
pour le 16/10, mais on ouvre ces cadres pour savoir qui manque MAINTENANT.
Le tableau suit le jour choisi ; les deux cadres se calculent sur
`jourUsine()` (le jour de l'usine, qui change à 6 h), par un second
`equipeDuJour()` seulement quand le jour affiché est un autre. Leur
sous-titre commence alors par « aujourd'hui · ». **J'ai d'abord cru que
l'application se trompait sur YBT** : la barre du haut, toujours datée du
jour, laissait croire que la capture montrait le 28/09. Vérifié en avançant
au 16/10 à 320 (hors ligne), 390 et 1280 px : les cadres ne bougent pas ;
les quatre sorties du vérificateur sont identiques à l'octet.

**Le premier cadre du Résumé dit le poste SUIVANT, jamais celui du jour.**
Le client, le même jour : « est-ce utile de remettre la pause du jour vu
qu'elle est dans la barre du haut ? ». Non : les jours travaillés, ce
cadre écrivait « Aujourd'hui · nuit » sous une barre qui disait déjà
« Contremaître · Nuit ». `majProchain()` part donc de DEMAIN. Et il
s'arrêtait au dernier jour du mois affiché — le 30/09, « plus de poste d'ici
la fin du mois » quand le prochain est le 5 octobre : il lit désormais la
suite dans `HORAIRE_DB`, par `moisDe()` et `lireJournee()`, la lecture du
calendrier. Vérifié horloge au 26, 28 et 30/09 : « lundi 28 », « demain »,
« lundi 5 octobre », hors ligne compris.

### Le Résumé en trois sections, et la journée dans le tableau

Le client, le 26/09/2026 : « réorganise le premier onglet avec des titres
et logique d'affichage ; et comment intégrer les personnes en D dans
l'horaire ? ». Trois titres hors cadre (`.pvtete`, comme Équipe et Mon
horaire), dans l'ordre des questions qu'on se pose en ouvrant
l'application :

1. **Mon prochain poste** : le cadre commence par le jour
   (« Demain · jour · 8 h »), puisque le titre dit déjà ce que c'est ;
2. **À venir** : les postes en manque ;
3. **À l'usine** : qui travaille, les absents, congé et repos. Sous le
   titre, le compte (« 35 personnes en poste · 77 au total »).

**Puis un étage de titres en moins.** Le client, le même jour, capture à
l'appui : « comment mieux présenter ceci ? ». Trois titres se suivaient
avant la première ligne du tableau : celui de la section, « Qui
travaille », puis la date du jour. Le cadre n'a plus d'en-tête : la barre
du jour sert de titre. Et le titre de la section ne répète plus la date.
Une première version écrivait « Aujourd'hui à l'usine » ou « L'usine le
lundi 28 septembre », juste au-dessus d'une barre qui disait la même
chose. Sont aussi partis : le mot « Poste » au-dessus de la colonne des
postes (elle se lit seule), « horaire variable » sous « En journée », et
la légende des zones. Le liseré de couleur regroupe des lignes qui portent
déjà leur nom : sa légende prenait deux lignes sous le tableau sans rien
apprendre. `ZONE_NOMS` et les styles `.lg-z` sont retirés avec elle. Rien
ne déborde à 320, 390 et 1280 px, hors ligne compris. Les quatre sorties du
vérificateur sont identiques à l'octet.

**« Mon prochain poste n'est plus affiché. »** Le client, le même jour. Le
défaut date de la première version du cadre, pas de la réorganisation :
`majProchain()` se cachait dès que le mois affiché n'était pas celui du
jour. Or le mois se choisit dans Mon horaire et Mon salaire, et on revient
au Résumé en gardant ce choix. Il suffisait d'avoir regardé octobre dans
Mon salaire pour trouver un cadre vide sous son titre. Reproduit
au navigateur : mois suivant, retour au Résumé, cadre caché. Le cadre part
désormais d'AUJOURD'HUI. Il lit le mois enregistré quand le jour en fait
partie (on garde ainsi les corrections faites à la main), sinon le
classeur, avec la même lecture que le calendrier. Tant que l'horaire n'est
pas chargé, il ne dit rien plutôt que « plus de poste ». **Un premier test a
cru montrer une erreur chez LCI** : il changeait de catégorie en boucle, et
les pré-remplissages en cours écrasaient la personne choisie. Refait
avec une seule sélection : « Demain · matin », ce que dit sa cellule du
27/09.

**Le tableau perd 18 % de sa hauteur sans rien perdre.** Même demande :
« penses-tu pouvoir optimiser l'affichage de ce tableau ? ». Les trigrammes
restent l'un sous l'autre, comme le client l'a demandé le 22/09. Mais
chacun prenait une ligne de 18 px pour un corps de 10,5 px : l'interligne
passe à 14 px, et les cases perdent deux pixels de marge. La légende tient
sur une ligne (« en formation », « aucun effectif attendu »). À 390 px, le
tableau passe de 470 à 386 px et le cadre de 585 à 482 px. Les règles
portent `#eqCorps` en tête : elles battent les règles de téléphone par la
spécificité, quel que soit leur ordre dans la feuille.

### Les pauses se disent AM, PM, N et D

Le client, le 26/09/2026 : « il faut parler en AM PM N D au lieu du nom de
la pause complet ». C'est ce qu'écrit le classeur, et ce qu'on dit à
l'usine. Les deux tables de libellés passent aux codes : `EQ_GROUPES` (le
tableau du jour, la barre du haut) et `POSTE_LIB` (le calendrier, sa
légende, les infobulles, le prochain poste). Les `toLowerCase()` qui les
suivaient sont retirés : ils auraient écrit « am ». La barre du haut dit
donc désormais « Fermentation · AM » ou « D », et plus « Contremaître ·
Nuit » comme le montrent les exemples plus haut dans ce fichier. **Restent
en toutes lettres, et c'est voulu : les lignes de fiche de paie**
(`SHIFT_NOMS`, « Suppl. Équipe Nuit »). Elles recopient le secrétariat
social, et l'onglet Contrôle se lit ligne à ligne contre la fiche.

Le prochain poste ne répète plus la pause dans son texte : la pastille la
porte. On lit « [AM] Demain · 8 h ».

**Noms de poste courts sur téléphone** (le client a choisi l'option B) :
« CM », « Adj. », « Meun. », « Glut. », « Ferm. », « T. arr. », « Dist. »,
« Chaud. » et « STEP », avec les noms
complets au-delà de 760 px. Le mécanisme est celui de l'onglet Équipe,
`.orgl1` / `.orgl2`. La colonne passe de 122 à 62 px, et chaque pause de
78 à 98 px. Cette largeur sert à la lisibilité : les trigrammes passent de
10,5 à 12 px, pour un tableau de 396 px (386 avant, 470 ce matin). La
ligne de la journée s'appelle « D ». Rien ne déborde à 320, 390 et
1280 px, hors ligne compris. Les quatre sorties du vérificateur sont
identiques à l'octet : ses sorties parlent en codes depuis toujours.

### La journée est une colonne, et un flex time complet n'est pas une présence

Le client, le 26/09/2026 : « une colonne D entre AM et PM ; par contre
cette nuit, comment ça se fait deux personnes comme CM ? ».

**La colonne D** remplace la ligne « D » posée une heure plus tôt. L'ordre
suit les heures d'arrivée : AM, D, PM puis N ; chacun y est rangé à son poste,
par le même `postesDePause()` que les trois pauses. Aucun effectif n'y est
attendu (`attenduAuPoste()` rend zéro pour D) : une case vide y est un
tiret, jamais un manque. Cinq colonnes tiennent à 320 px sans déborder. À
390 px, chaque pause fait 74 px et le tableau 352 px.

**Deux contremaîtres de nuit le 26/09 : YPE et FPA.** YPE porte
`["N","8h -FT","Remplacé par VGG"]` : une journée entière de flex time
repris. FPA porte `["R-CM","3h -FT","Remplace YPE …"]`. `equipeDuJour()`
rangeait à sa pause quiconque avait des heures. Or les 8 h de YPE sont
PAYÉES depuis le compteur (section 6 de `docs/conversion-horaire.md`),
sans qu'il soit présent. PDR, `["N","8h -FT","rempl par ALZ"]`, était
compté deux fois de la même façon en distillation. C'est la règle déjà
posée pour le chèque-repas et pour la date de reprise : **seules les heures
PRÉSENTES comptent**. Une reprise d'une journée entière passe donc dans
« Congé et repos », avec sa date de reprise. Une reprise partielle
(« 3h -FT ») laisse la personne à son poste.

Mesuré : neuf règles, compteurs et `--manques 0926` **identiques à
l'octet** (rien ne change d'ici la fin de l'année). Sur l'année entière,
les places creuses passent de **245 à 264** et les journées en manque de
159 à 172, dont **+10 chez les contremaîtres** : autant de journées passées
où l'absent comptait comme présent. Dans les journées de contremaître en
flex time complet, le remplaçant est presque toujours nommé. Quand un trou
apparaît, le remplaçant n'est pas dans l'horaire (« remplacé par PBL »,
absent des 77) ou n'est pas nommé du tout. Recyclage : 23 → **22** couples
au quota (CDE chaudières 10 → 9), et une dizaine de cases bougent d'une
journée.

### Le tableau du jour : gras, « (F) », une colonne blanche

Le client, le 26/09/2026, capture à l'appui : « le poste de la personne
sélectionnée ne doit pas être souligné mais peut être en gras ; supprimer
la légende des gens en formation mais indiquer (F) à côté du trigramme ».

- **La personne choisie** se lit en gras (800), dans la couleur d'accent,
  sans soulignement.
- **« (F) » remplace le jaune expliqué par une légende**, et il suit le
  POSTE, pas la catégorie. La capture montrait LCI en jaune à la
  fermentation, qu'il tient validé jusqu'au 29/09. Le tableau testait
  `enFormation()`, qui ne regarde que la catégorie. Il teste désormais
  `compteAuPoste()`, la règle même de l'effectif, avec le jour affiché.
  C'est ce que la composition fait depuis le 25/09 (« le jaune suit le
  poste ») : les deux vues disent maintenant la même chose. Le 26/09, SKS
  (meunerie), SVE (distillation) et MGY (chaudières) portent « (F) », et
  LCI non.
- **La colonne D reste blanche** là où personne n'est en journée : un
  tiret sur chaque ligne en faisait une colonne de traits, pour un poste
  qui n'attend jamais personne.
- **La légende du tiret part aussi** : il ne reste de tirets qu'à l'adjoint
  et à la STEP hors matin, qui se lisent seuls. La légende du manque
  reste, les jours où un manque est dessiné.

Le cadre passe de 448 à 413 px à 390 px. Neuf règles, manques, compteurs
et Recyclage identiques à l'octet ; rien ne déborde à 320, 390 et
1280 px, hors ligne compris.

**Puis les quatre pistes, toutes** (le client : « go tout ») :

1. **la barre du jour s'affine** : boutons de 30 px au lieu de 34, marges de
   7 px au lieu de 12, « Aujourd'hui » en petit. Elle passe de 59 à 45 px ;
2. **plus de « 10 pers. » sous les pauses** : le total est sous « À
   l'usine », et un effectif se compte en trigrammes. L'horaire de la pause
   reste au bureau. L'en-tête passe de 45 à 31 px ;
3. **la colonne D n'apparaît que les jours où quelqu'un est en journée**.
   C'était déjà le cas depuis qu'elle existe (une pause vide n'a pas de
   colonne), et c'est vérifié : les samedis et dimanches 3-4 et 10-11/10,
   le tableau revient à AM, PM, N ;
4. **la couleur range l'ordre de lecture** : les intitulés de poste passent
   de `--faint` à `--muted`, les tirets à 45 % d'opacité. Un tiret dit
   « rien à voir ici » et ne doit pas peser autant qu'un trigramme.

Le cadre passe de 413 à **385 px** à 390 px de large. Neuf règles, manques,
compteurs et Recyclage identiques à l'octet ; rien ne déborde à 320, 390 et
1280 px, en clair et en sombre, hors ligne compris.

**Des traits visibles, et des lignes de même hauteur.** Le client, le même
soir, capture à l'appui : « les lignes ne sont plus assez visibles ; il
faut également des hauteurs fixes de même taille pour chaque ligne ».
Deux jetons de thème, `--trait` (entre deux postes) et `--trait-fort`
(entre deux zones et sous l'en-tête), déclarés dans les trois blocs,
clair, sombre automatique et sombre forcé. Ils remplacent `--line2`, qui
se confondait avec le fond des cartes. Pour la hauteur, un tableau
n'égalise pas ses lignes de lui-même : le rendu compte la case la plus
pleine du jour (`maxLig`, avec le compte d'un manque et les lignes « à
déterminer » et « Formation ») et pose `--eqh = 12 + 16 × maxLig` px sur
chaque ligne. Le 26/09, trois trigrammes aux chaudières donnent 60 px
partout. **Ce choix coûte de la hauteur** : le cadre passe de 385 à 619 px
à 390 px de large. Le client, à qui le coût a été montré avec trois autres
options : « tout », c'est-à-dire telle quelle. Neuf règles, manques,
compteurs et Recyclage identiques à l'octet ; rien ne déborde, hors ligne
compris.

**Puis corrigé dans le même soir**, sur quatre points :

- **hauteur de deux trigrammes pour toutes les lignes**, et seule une case
  plus pleine fait grandir la sienne. Le client : « comme celle où il y
  avait 2 trigrammes pour toutes les lignes, sauf celles de plus de 2 ».
  Une hauteur de ligne de tableau est un minimum : `height:44px` sur
  chaque ligne suffit, et le calcul `maxLig` / `--eqh` est retiré. Le 26/09,
  toutes les lignes font 44 px et les chaudières 60. Le cadre passe de 619
  à 491 px ;
- **le liseré de zone sur le bord des postes était parti, par ma faute** :
  la règle des traits visibles, `#eqCorps .eqp2 th, td{border-left-color}`,
  battait par sa spécificité les couleurs `tr[data-z] th.eqposte`. Elle
  ne vise plus que les cases et l'en-tête ;
- **le zébra vaut pour toutes les cases**, colonne D et tirets compris.
  Les tirets avaient leur propre fond, et l'opacité à 45 % pâlissait aussi
  ce fond : ils s'éclaircissent désormais par leur couleur (`--trait-fort`) ;
- **les postes s'écrivent comme AM, PM, N** (12 px, graisse 650, encre
  principale, sans capitales), au centre de leur colonne.

Neuf règles, manques, compteurs et Recyclage identiques à l'octet ; rien
ne déborde, hors ligne compris.

**Et trois retouches encore** (le client, le même soir) : sur téléphone,
les postes s'écrivent en trois capitales — « CM », « ADJ », « MEU »,
« GLU », « FER », « TER », « DIS », « CHA », « STEP » — ; les trigrammes
passent en graisse normale, seule la personne choisie restant en gras ; et
le zébra s'adoucit. Le jeton `--zebre` vaut, en sombre, le milieu entre la
carte et l'ancien `--surface2` (`#1C2130`). En clair il garde la valeur
d'avant, déjà très légère. Neuf règles, manques, compteurs et Recyclage
identiques ; rien ne déborde, hors ligne compris.

**Et quatre derniers réglages** (le client, le même soir) : plus de
couleur au-dessus des pauses ; le trait sous l'en-tête est le même que
celui sous ADJ ; les tirets reviennent dans les cases vides de la colonne
D, que le client avait d'abord voulues blanches ; « Aujourd'hui » a la
hauteur des flèches (30 px). Le trait sous l'en-tête paraissait plus
épais **parce qu'il était double** : la première ligne ouvre une zone et
portait son propre trait de 2 px, qui s'ajoutait aux 2 px de l'en-tête.
Elle n'en porte plus. Neuf règles, manques, compteurs et Recyclage
identiques ; rien ne déborde, hors ligne compris.

**Plus aucune légende, et la formation s'écrit comme un poste** (le
client, le même soir) : « il ne faut jamais de légende, même pour les
postes en sous-effectif ». Le compte écrit dans la case (« 1/2 ») se lit
seul, et la construction de la légende est retirée avec son drapeau
`aManque`. La ligne formation quitte le style italique et grisé de
« À déterminer » (`eqinc`) pour sa propre classe, `eqform`. Elle
s'écrit « Formation » au bureau et « FORM » sur téléphone, en 12 px et
en graisse 650, comme les postes. Son liseré gauche prend l'encre
principale : blanc en sombre, presque noir en clair, où du blanc ne se
verrait pas sur la carte. Le coin vide au-dessus des postes perd son
trait de 3 px en haut et son liseré gauche. Vérifié le 27/09 (un manque,
aucune légende) et le 28/09 (ligne FORM) ; neuf règles, manques,
compteurs et Recyclage identiques à l'octet ; rien ne déborde à 320, 390
et 1280 px, hors ligne compris.

**La colonne D dit l'horaire quand le classeur l'écrit.** Le client, le
26/09/2026 : « il y a des gens qui font D (6-14), il faut les mettre dans
la colonne 6-14 ; les autres en D, préciser 7-15 ou H. flot. », puis « D
seul laisser rien ». Le D seul de YRS et BLR est un 7h30-16h, les jours où
ils sont consignateurs ; GSK l'a fait le temps de sa reprise après une
longue absence ; les opérateurs en formation commencent tous par des D
avant de passer en pause au poste. Aucun de ces D ne s'écrit.

- **« 7-15 », « H. flot. » ou « 6-14 »** à côté du trigramme, en petit,
  quand la cellule ou l'annotation porte 7h-15h, « H. flott. » ou 6h-14h
  (`horaireEcritD()`, lu dans le classeur du jour). Toute autre plage :
  rien. Le 6-14 ne s'écrit jamais avec un code de jour : dans
  `["6h-14h","F"]`, `D-F`, `DS-CE` ou `D-CPPT`, la plage n'est que le poste
  prévu (GDT le 14/10, « formation anglais sur site 8h-11h »).
- **Un D écrit 6h-14h reste dans la colonne D.** Une première version le
  passait en AM, dans `equipeDuJour()`. Elle déplaçait d'abord aussi vingt
  journées de formation ou de réunion, ce que le journal des déplacements
  a montré avant le commit. Restreinte à SKS les 5, 6 et 7/10
  (`["6h-14h","D"]`), elle a été poussée en v269 : SKS comblait la
  fermentation du 05/10. Le client, aussitôt : « je préfère laisser les
  gens prévus en D (6-14) dans la colonne D mais préciser à côté leurs
  horaires ». La règle est retirée en v271, et SKS porte « 6-14 ».

**Puis entre parenthèses, et toujours** (le client, le même jour : « il
doit toujours être marqué l'horaire de quelqu'un en D ; cet horaire doit
être en () ; si BLR ou YRS est en D, il faut mettre (C) à côté de lui
pour Consignation »). L'ordre : (C) pour `CONSIGNATEURS` ; (H. flot.) ;
la plage écrite dans l'annotation ou la cellule, quelle qu'elle soit
(« (7-15) », « (6-14) », « (8-12) ») ; sinon celle que le commentaire
écrit avec un tiret (DWS le 28/09, « (8h30-16h30) »). « De 10h à 14h »
dans un commentaire dit un remplacement partiel et ne compte pas. Avec un
code de jour, seule une plage de journée compte. **Reste le D seul sans
aucune heure écrite** : 103 journées d'ici la fin de l'année chez 19
personnes (YBT 15, NPI 14, FPS 9, MGY 9, FLI 8…). La question est posée
au client, et rien n'y est écrit en attendant.

**Pas d'horaire sur la ligne FORMATION, un horaire pour tous les autres.**
Le client, le 28/09/2026. La ligne FORMATION n'écrit plus de parenthèses
(`chip(…, sansHoraire)`) ; mesuré du 28/09 au 31/12, 48 présences sur
cette ligne, aucune avec horaire. « Tous les autres présents en D » doivent
avoir le leur : il en reste **140 sans horaire** sur 426 présences en D
d'ici la fin de l'année — les « D » seuls (FPS le 28/09, `["D"]`) et les
journées de réunion sans plage (`["AM","D-CPPT"]`). Quel horaire leur
écrire est la question du « D seul » ci-dessous, reposée au client le
même jour ; rien n'est deviné en attendant.

Rien ne bouge dans la lecture ni dans le placement : les quatre sorties du
vérificateur sont identiques à l'octet à celles d'avant v269. Vérifié au
navigateur le 28/09 (AFA et JBI « 7-15 », YRS rien), le 05/10 (SKS
« 6-14 ») et le 02/12 (FPA « H. flot. »), à 320, 390 et 1280 px, hors
ligne compris.

**« Postes en sous-effectif », sans choix d'horizon, et un prochain poste
qui dit où.** Le client, le 26/09/2026 : « il ne doit pas y avoir de
sélection de temps sur les postes en manque ; il faut l'appeler "Postes en
sous-effectif" et ne pas marquer le nombre de journées regardées ; dans le
cadre Mon prochain poste il faut écrire la date, la pause, le poste
occupé ». Les boutons 7 j / 14 j / 30 j / Tout sont partis avec leur
écouteur et la clé `ui/mqHorizon` : le module regarde d'aujourd'hui à la
fin de l'horaire, et son sous-titre ne dit plus que « 7 journées » ou
« rien à signaler ». Le cadre écrit « Lundi 28 septembre · D ·
Contremaître », avec « (demain) » quand c'en est un et les heures
seulement si la journée n'est pas complète. Le poste vient de
`posteLeJour()`, la chaîne du tableau du jour (`equipeDuJour()` puis
`postesDePause()`, colonne D comprise) : le cadre et le tableau disent
donc la même chose. La pastille colorée est partie, puisque la pause
s'écrit en toutes lettres, et avec elle ses styles et ceux de `.mqbar`.
Les quatre sorties du vérificateur sont identiques à l'octet ; rien ne
déborde à 320, 390 et 1280 px, hors ligne compris.

**La pause du moment surlignée, un trait après les postes, et deux titres
renommés.** Le client, le 27/09/2026 : « met en surbrillance légère la
pause du moment ; fais une bordure semblable à celle sous la ligne de pause
à droite de la colonne du poste ; écris "Équipes du jour" au lieu de "À
l'usine", et "Postes en sous-effectif" à la place de "À venir", sans le
remettre juste en dessous ».

- La colonne de la pause en cours (AM de 6 h à 14 h, PM de 14 h à 22 h, N
  de 22 h à 6 h) reçoit un voile `--maint`, posé en `box-shadow` intérieur
  PAR-DESSUS le fond de la case : le zébra et le rouge d'un manque restent
  visibles dessous. Seulement sur la journée qu'elle concerne : après
  minuit, la nuit en cours est celle de la veille, et le tableau d'aujourd'hui
  ne surligne rien (voir juste dessous : le tableau lui-même montre
  désormais la veille jusqu'à 6 h). La colonne se désigne par son rang (`data-mc` sur le
  tableau), et quatre règles `nth-child` suffisent.
- `th.eqposte` porte à droite le même trait de 2 px `--trait-fort` que
  celui sous l'en-tête.
- Le titre du module est au-dessus du cadre ; le repli ne garde que le
  compte (« 7 journées »), et ses deux règles `summary h2` sont parties.

Un point de sauvegarde était demandé : le tag `checkpoint-v273` est refusé
à l'envoi par le serveur (403), le commit 8b1edcd, déjà sur `main`, en
tient lieu. Les quatre sorties du vérificateur sont identiques à l'octet ;
vérifié à 7 h, 15 h, 23 h et 2 h, à 320, 390 et 1280 px, hors ligne compris.

**Le jour de l'usine commence à 6 h.** Le client, le 27/09/2026 : « il faut
afficher l'équipe du jour jusqu'à 6 heures du matin et passer au jour
suivant seulement à 06h ». `jourUsine()` rend la veille entre minuit et
6 h, et `eqJourValide()` s'en sert. Tant qu'on n'a pas choisi un jour à la
main (flèches ou clic sur un manque), `eqAuto` le fait recalculer à chaque
rendu : une application restée ouverte passe au jour suivant à 6 h, au
prochain affichage. « Aujourd'hui » rend la main au jour de l'usine. La
surbrillance de la nuit, qui prenait déjà la veille après minuit, tombe
désormais sur le tableau affiché. Vérifié à 23 h 30, 2 h et 5 h 59
(dimanche 27, N surlignée) puis à 6 h 01 (lundi 28, AM), à 320, 390 et
1280 px, hors ligne compris ; les quatre sorties du vérificateur sont
identiques à l'octet.

**La ligne des pauses a la hauteur des postes, et un trait au-dessus.** Le
client, le 27/09/2026 : « hauteur de la ligne des pauses comme les lignes
de poste, et ajouter la même bordure qu'en dessous de la ligne des pauses
au-dessus des pauses ». `thead tr{height:44px}` et un trait de 2 px
`--trait-fort` en haut des cases de pause ; le coin au-dessus des postes
reste sans trait, comme demandé la veille. 44 px à 320 et 390 px, 45 au
bureau où l'horaire de la pause s'écrit sous son code. Les quatre sorties
du vérificateur sont identiques à l'octet, hors ligne compris.

**Les postes s'écrivent comme dans le tableau des équipes, et le coin dit
« Poste ».** Le client, le 27/09/2026. Mêmes abrégés que l'onglet Équipe
(`PV_COURT` : MEUN., GLUT., FERM., T. ARR., DIST., CHAUD., STEP), plus CM,
ADJ., FORM. et « À DÉT. », en capitales, 10,5 px sur téléphone ; les noms
entiers en 12,5 px au bureau. La colonne passe à 76 px et 136 px, avec les
marges intérieures du tableau des équipes (7 px au bureau) : avec
l'ancienne marge gauche de 14 px, « TERRAIN ARRIÈRE » était coupé à
1280 px, et la mesure l'a montré avant le commit. Les trois pauses
rendent chacune 3 à 4 px à 320 px, et l'horaire de la colonne D passe
sous le trigramme, coupé au tiret s'il le faut (« (8h30-16h30) »
débordait de 16 px). Les trois abrégés d'avant (MEU, GLU…) sont partis.
Les quatre sorties du vérificateur sont identiques à l'octet ; rien ne
déborde à 320, 390 et 1280 px, hors ligne compris.

**Sous chaque pause, l'équipe qui y tourne.** Le client, le 28/09/2026 :
« indiquer dans la cellule de la pause (à la place de l'horaire) l'équipe
avec laquelle la pause est prévue de tourner ce jour-là ; pareil pour les
D, juste l'équipe, pas le binôme ». `equipesDuCycle()` lit, mois par mois,
le décalage de chaque équipe dans le cycle de cinq semaines, sur les
cellules franches de TOUS ses membres (catégorie « Shift n ») — une voix
par cellule, si bien qu'un échange ou une personne déplacée ne fait pas
basculer l'équipe. `equipeALaPause()` en tire « AM Éq. 2 · D Éq. 4 · PM
Éq. 5 · N Éq. 1 » (« Équipe n » au bureau). **Mesuré sur 2026** : le même
décalage les douze mois pour les cinq équipes (équipe 3 à 0, 1 à 7, 5 à
14, 4 à 21, 2 à 28 jours), de 71 à 99 % des cellules d'accord, et **jamais
deux équipes à la même pause un même jour**. Sous 60 % d'accord, rien
n'est écrit plutôt que deviné. L'horaire de la pause (6h-14h…), qui ne se
voyait qu'au bureau, a cédé sa place. Vérifié le 28/09, le 03/10 (samedi,
pas de D) et le 07/10, à 320 (hors ligne), 390 et 1280 px, chaque fois
égal au calcul fait à part en Python ; les quatre sorties du vérificateur
sont identiques à l'octet.

**Chaque sous-effectif dit son équipe, et qui pourrait le combler.** Le
client, le 28/09/2026 : « indiquer l'équipe dans laquelle il manque
quelqu'un et s'il y a des possibilités de remplacement avec les gens
présents ce jour-là selon leur polyvalence (attention de bien garder
l'effectif minimum à chaque poste et pause) ». Une ligne par manque :
« N Terrain arrière 0/1 · Éq. 1 → ATR (Chaud.) ». L'équipe vient de
`equipeALaPause()`. Les pistes viennent de `pistesDeRemplacement()`, qui
ne DÉPLACE personne — le rééquilibrage a déjà fait ce que le classeur lui
permet — et propose, dans l'ordre : quelqu'un de la même pause dont le
poste garde son minimum sans lui (un poste qui n'attend personne, comme
l'adjoint, compris) ; un « à déterminer » ; une personne en D sans code de
journée, au matin et à l'après-midi seulement. Il faut la polyvalence du
poste et y compter (un opérateur en formation n'y compte pas) ; pour le
contremaître, seul un cadre. Sinon « personne de libre ». Au 28/09 : six
journées, trois avec une piste — le 12/11, ATR aux chaudières (trois pour
deux attendus) est proposé au terrain arrière, ce que la question posée le
même jour suggérait. Les quatre sorties du vérificateur sont identiques à
l'octet (il ne découpe pas ce module) ; rien ne déborde à 320 (hors
ligne), 390 et 1280 px.

**Puis refait en fiches.** Le client, le 28/09/2026, capture à l'appui :
« il y a certainement moyen d'optimiser bien mieux ce tableau-là et de
faire ça 100 % professionnel ». Pastilles, équipe et flèche se suivaient à
la file et passaient à la ligne n'importe où (le 16/10 sur une ligne, le
12/11 sur deux). Chaque journée est désormais une rangée : à gauche un bloc
de date (« VEN. / 2 / OCT. »), à droite une fiche par manque, liseré à la
couleur de l'atelier ; ligne 1, la pause en pastille à sa couleur, le
poste, l'effectif en rouge, l'équipe calée à droite ; ligne 2,
« Remplaçants possibles » suivi d'étiquettes trigramme + provenance, ou
« Aucun remplaçant disponible ». Les journées sont séparées d'un filet
(`--trait`). Sous 380 px, « Équipe 2 » devient « Éq. 2 » et l'étiquette
« Possibles » : à 320 px « Terrain arrière » se coupait. Au bureau, la
fiche s'arrête à 560 px pour que l'équipe reste près du poste. Vérifié en
clair et en sombre à 320 (hors ligne), 390 et 1280 px : rien ne déborde,
rien n'est tronqué ; vérificateur identique à l'octet.

**Et le cadre « Mon prochain poste » vide** de la même capture : non
reproduit — même un horaire servi avec quatre secondes de retard finit par
le remplir. Par sûreté, il se redessine désormais dès que l'horaire arrive
(`fetchHoraireDB()`), puisqu'il se cache tant qu'il n'a personne à lire.
Si le cadre reste vide chez le client après la v291, c'est une autre
cause, à chercher sur son appareil.

**Les trigrammes du tableau du jour en étiquettes.** Le client, le
28/09/2026 : « il faut les mêmes badges de trigrammes sur ce tableau que
sur le tableau du dessus et du dessous ». Chaque trigramme prend
l'étiquette des sous-effectifs et des absents (fond `--surface3`, filet
`--trait`, mono gras 11,5 px), toujours l'un sous l'autre. La personne
choisie a le bord et l'encre de l'accent : elle n'est plus « la seule en
gras » (règle du 26/09), toutes les étiquettes l'étant. « (F) », « (C) »
et l'horaire de la colonne D restent dans l'étiquette, **en ligne** — une
règle générale `.eqn{flex-direction:column}` les faisait passer dessous,
et le tableau montait à 676 px ; 620 px ainsi à 390 px. Sous 380 px,
l'étiquette se resserre (3 px de marge, 11 px) pour que « SKS (F) » tienne
dans une colonne de 50 px. Vérifié en clair et en sombre, à 320 (hors
ligne), 390 et 1280 px : aucune étiquette ne sort de sa case ;
vérificateur identique à l'octet.

**Plus de « (F) » ni de « (C) », un horaire pour la consignation.** Le
client, le 28/09/2026 : « supprimer le F vu que le badge jaune dit déjà que
c'est en formation, pareil pour le (C) ; mais il faut indiquer l'horaire
de tous ceux qui apparaissent dans la colonne D ». Le « (F) » part ; le
« (C) » de YRS et BLR devient « (7h30-16) », l'horaire que le client a
donné pour leur D de consignation le 26/09 — une plage écrite dans le
classeur passe avant. **Restent 138 présences en D sans aucune heure
écrite** d'ici la fin de l'année (NPI 15, YBT 15, SKS 13…) : le classeur ne
définit nulle part l'horaire d'un « D » seul (cherché dans la légende et
dans tout le brut), c'est donc la question du « D seul », toujours posée.
Les règles mortes `.eqf` et `.eqfold` sont retirées. Vérificateur
identique à l'octet ; rien ne sort d'une case à 320 (hors ligne), 390 et
1280 px.

**« Horaire selon celui qu'ils font en D ».** La réponse du client, le
même jour. `horaireHabituelD()` lit, sur les journées de la personne elle-
même, la plage de JOURNÉE qu'elle écrit en D (annotation d'un « D », ou
cellule franche seule) : retenue si elle revient au moins deux fois et
fait au moins 60 % de ce qu'elle écrit. Elle vaut aussi les jours à code
(CPPT, DS-CE) : « tous ceux qui apparaissent dans la colonne D ». D'ici la
fin de l'année, les présences en D sans horaire passent de 138 à **112**,
chez **21 personnes qui n'écrivent jamais leurs heures en D** (NPI, YBT,
SKS, FPS, MGY, GPO, JBS, FLN, CDE, GKT, PAM, LHR, LCI, SPT, TCE, ALZ, RCO,
JKS, JBA, SVE, AAI) — ni en cellule, ni en commentaire, vérifié. Leur
horaire est demandé au client ; rien n'est deviné.

**BLR et YRS en D vont dans la colonne AM, à la meunerie.** Le client, le
28/09/2026 : « règle unique : si BLR ou YRS est en D il faut les mettre
dans la colonne AM mais avec leurs horaires 7h30-16 en dessous ; ils sont
en consignation meunerie ». Le tableau du jour déplace leur étiquette de
la colonne D vers la case AM · Meunerie, APRÈS ceux qui tiennent le
poste, avec « (7h30-16) » (ou la plage écrite ce jour-là). **Affichage
seulement** : la consignation est une tâche, pas la tenue du poste (le
client, le 26/09, pour « consign. ») — l'effectif de la case et les
sous-effectifs ne bougent pas, et l'étiquette n'est jamais jaune. La
colonne D disparaît si elle ne portait qu'eux. Vérifié les 28/09 (YRS),
05/10 (BLR), 16/10 et 08/10 — ce jour-là YRS est déjà en AM, il remplace
BLR ; vérificateur identique à l'octet.

**« Seulement D » : 7-15.** Le client, le même jour : « les gens où il
est seulement marqué D doivent avoir 7-15 sous eux ». Après les plages
écrites, la consignation et l'horaire habituel, un « D » seul — en cellule
franche (`["D"]`, `["D","meunerie"]`) ou en annotation (`["PM","D"]`,
`["-","D"]`) — affiche (7-15). Une prime conservée n'y change rien (ALZ le
05/10, « maintien prime N ») ; une journée à code, si : D-CPPT, DS-CE et
les formations F ne sont pas « seulement D ». D'ici la fin de l'année,
**317 présences en D, 10 sans horaire**, toutes de cette sorte (LHR,
LCI, JKS en CPPT ou CE, SVE et AAI en formation). La liste des 21
personnes demandée plus haut n'a plus d'objet.

**Et avant l'horaire habituel.** Le client, le même jour : « ceux qui sont
en D sans rien d'autre sont en 7-15 ». L'horaire habituel passait avant,
et une journée « seulement D » pouvait afficher autre chose que 7-15.
L'ordre est désormais : plage écrite ce jour-là, H. flot., commentaire à
tiret, consignation (7h30-16), **« seulement D » → 7-15**, et l'horaire
habituel pour ce qui reste (QBY en DS-CE le 21/10 : son 10-18 de CE).
D'ici la fin de l'année : 277 × (7-15), 21 × (H. flot.), 9 plages écrites,
10 journées à code sans horaire.

**Le tableau du jour resserré.** Le client, le 28/09/2026, capture à
l'appui : « comment optimiserais-tu ceci ? », puis « go » sur quatre
pistes :

- des étiquettes moins hautes : 1 px de marge au lieu de 2, 2 px entre
  deux trigrammes empilés, 3 px de marge de case ;
- l'horaire de la colonne D sans parenthèses, à côté du trigramme
  (« GPS 7-15 »). Il passait à la ligne dans toutes les étiquettes ;
  seul « 7h30-16 » de la consignation y passe encore ;
- la colonne des postes à 64 px au lieu de 76 sur téléphone, et 2 px de
  marge de case sous 380 px : « GPS 7-15 » tient ainsi dans une pause de
  56 px à 320 px ;
- un seul tiret, le court « – », dans toutes les cases vides : les lignes
  FORM. et « À dét. » écrivaient un tiret cadratin « — ». La distinction
  entre les deux tirets (« personne » ou « personne n'est attendu »)
  n'avait plus de légende pour la dire.

Le liseré gauche du coin « POSTE » reste : le client l'a redemandé le
27/09. La hauteur minimale d'une ligne (deux trigrammes) et les
trigrammes l'un sous l'autre restent aussi. Mesuré le 25/09 : 566 → 518 px
à 390 px, 576 → 517 px à 320 px. Rien ne sort d'une case à 320 (hors
ligne), 390 et 1280 px, en clair et en sombre. Neuf règles et
`--manques 0928` identiques à l'octet.

**« Cons. » au lieu de « 7h30-16 ».** Le client, le 28/09/2026, pour les
étiquettes qui passaient encore à la ligne : « écrire Cons. ». BLR et YRS
rangés à la meunerie du matin portent « Cons. », quoi qu'écrive leur
cellule ; en D le week-end, « Cons. » remplace aussi « 7h30-16 » quand
aucune plage n'est écrite. « 7h30-16 » ne tenait sur une ligne dans aucune
case de téléphone (64 px pour 62, mesuré). À 390 px la ligne MEUN. passe
de 57 à 46 px et le tableau à 507 px ; à 320 px, « BLR Cons. » passe
encore à la ligne. Neuf règles identiques à l'octet.

**Puis « 8-16 ».** Le client, le même jour : « écrire 8-16, ça ira
mieux ». « Cons. » est remplacé partout par « 8-16 », qui tient sur une
ligne jusqu'à 320 px, comme « 7-15 ».

**Le badge de formation bordé de jaune.** Le client, le même jour :
« le badge doit être jaune comme le badge perso ». **Je l'ai d'abord
compris de travers** : j'ai mis BLR et YRS en jaune (v310). Le client :
« non, eux deux ne devaient pas changer ; je voulais que les badges des
personnes en formation soient jaunes comme le badge perso ». Le badge de
la personne choisie a le bord ET le trigramme à l'accent ; celui d'un
opérateur en formation n'avait que le trigramme en jaune. Il prend
désormais aussi le bord jaune. BLR et YRS retrouvent leur badge
ordinaire.

### La meunerie du matin : deux en semaine, consignation comprise

Le client, le 28/09/2026 : « le poste consignation en meunerie est un
poste qui doit compter dans l'effectif meunerie du matin ; ils doivent être
toujours au moins 2 dans cette case du lundi au vendredi ». Question posée
avant de coder (A : les consignateurs en D comptent dans les deux ; B :
deux en pause plus la consignation). Réponse : « A, mais il faut vérifier :
si d'autres personnes sont en D meunerie (et validées, donc pas ceux en
formation), c'est bon ».

- `renfortDuJour()` pose `meun:{AM:2}` du lundi au vendredi, **jours fériés
  exclus**. Ce choix était le mien, et le client l'a confirmé le
  28/09/2026 : « A », un férié se traite comme un week-end. Les autres renforts fusionnent par le maximum.
  `RENFORT_CLOS` ne lève que ceux du classeur ;
- `meunDepuisD()` fait compter pour la meunerie du matin, parmi les gens en
  D, BLR et YRS (`CONSIGNATEURS`) et quiconque la chaîne met en meunerie
  avec `compteAuPoste()`. Sont exclus les gens en formation et ceux qui
  portent un code de jour (CPPT, DS…). Ces copies portent
  `depuisD` : la polyvalence, le prochain poste et le poste de la barre du
  haut les ignorent ;
- au tableau du jour, un consignateur s'écrit dans la case AM de la
  meunerie avec son (7h30-16), et plus en colonne D. Un validé en D
  meunerie reste en D, mais il compte.

Mesuré : neuf règles, compteurs et `--manques 0928` identiques à l'octet.
Sur l'année, 272 → 277 places creuses : quatre matins de meunerie à 1/2
(03/07, 17/07, 11/08, 14/08, les deux consignateurs en congé, malades ou en
repos) ; le 06/01 passe de 0/1 à 1/2 ; le 13/08, le rééquilibrage envoie un
chaudiériste en meunerie (chaudières 1/2). Recyclage : meunerie +1 chez
JKS, LDY et PLZ, qui tiennent la seconde place ; CDE distillation −1, SKS
distillation +1 et chaudières −1 ; couples au quota inchangés. Au navigateur, le 28/09 :
« MEUN. JKS · YRS (7h30-16) », SKS (formation meunerie) reste en D
(7-15) et ne compte pas. Vérifié à 320 (hors ligne), 390 et 1280 px.

### Un atelier écrit peut être le mauvais : `POSTE_DU_JOUR`

Le client, le 26/09/2026 : « pourquoi VGG est en distillation demain alors
que BBZ est là ? ». Le 27/09 en PM, GDT, titulaire de la distillation, est
en DTT ; VGG porte `["PM","distillation","remplace GDT"]` ; BBZ, renfort
arrière dont la seule polyvalence est la distillation, porte `["PM"]`.
Deux en distillation, le terrain arrière à 0/1. Le commentaire de GDT,
« remplacé par FPA », est faux de son côté : FPA est de nuit ce jour-là.
Trois lectures proposées, le client a répondu « A » : BBZ en distillation,
VGG au terrain arrière, qu'il sait tenir (fermentation et distillation).

`POSTE_DU_JOUR` porte cette décision, **pour la journée nommée seulement**.
C'est la seule table qui passe AVANT la cellule dans `posteTenu()` : elle
corrige justement ce que la cellule écrit. Elle entre dans la découpe du
vérificateur.

**Pas de règle générale, et c'est mesuré.** Une sonde a cherché sur l'année
la même forme : quelqu'un d'écrit sur un poste en surnombre qui a la
polyvalence d'un poste vide à la même pause. **11 journées**, et plusieurs
sont justes telles quelles : GPO les 19 et 20/08 en « Ferm. Liq. », PAM le
21/05 en « terr. Arr. + fermentation », VGG le 07/08 dont le commentaire
dit « atelier gluten 08h-14h ». La règle se tromperait : chaque cas se
tranche avec le client.

Mesuré : neuf règles, compteurs et Recyclage identiques à l'octet ; le
27/09 PM quitte la liste des manques (8 → 7 d'ici la fin de l'année, 269
→ 268 places sur l'année). Vérifié au navigateur, hors ligne compris.

### AAI à la distillation, SMA au terrain arrière : `POSTE_HABITUEL`

Le client, le 27/09/2026 : « dans l'équipe 5, par défaut c'est toujours AAI
qui tient le poste distillation et SMA le terrain ». Sur l'année, les jours
où ils sont dans la même pause, la chaîne disait **l'inverse 80 fois**.
AAI est renfort arrière, avec fermentation et distillation : la règle du
terrain arrière le prenait. SMA porte « Distillation » en ligne 9.

`POSTE_HABITUEL` passe après la cellule et la tranche de période (ce qui
est écrit pour un jour prime) et avant le rôle et la ligne 9, qu'elle
corrige. Il reste quatre journées « inversées », et elles sont justes :
AAI y porte « poly. Etoh » (22 et 23/07, 23/10, 04/11). La table entre
dans la découpe du vérificateur.

Mesuré : neuf règles, compteurs et `--manques 0926` identiques à l'octet.
Sur l'année, 268 → 269 places creuses (le 14/01 AM, le trou passe de la
fermentation au terrain arrière). Recyclage : la distillation devient le
poste d'AAI et sort de sa ligne ; SKS distillation 4 → 12 ✓, SMA
distillation 2, SPS 30 → 31, CDE et LDY bougent d'une ou deux journées.
**23 couples au quota, inchangé.** La composition de l'onglet Équipe suit :
AAI en distillation, SMA au terrain arrière.

Même commit : le coin « Poste » du tableau du jour retrouve sa bordure
haute (2 px, le trait des pauses) et gauche (3 px, la largeur des liserés
de zone). Le client, le 27/09/2026 : « remettre les bordures gauche et
haute ».

### Tout l'horaire relu : d'où viennent ces erreurs

Le client, le 26/09/2026 : « vérifie tout l'horaire, comment cela se fait
ces erreurs ? ». `node tools/verifier-calendrier.js --doublons` relit
l'année et liste deux formes. (1) Une personne PRÉSENTE à une pause dont
le commentaire dit « remplacé par » sans heures. (2) Une personne présente
à côté d'un collègue qui écrit « remplace » son trigramme, sans heures.
Le mode est informatif (code 0) : **606 journées** remontent, et la plupart
sont justes. « Remplacé par » parle du poste PRÉVU : quelqu'un envoyé au
terrain arrière, en formation ou en SD26 est remplacé à son poste
habituel, et il est bien à l'usine, ailleurs.

**Première version, trop étroite** : elle n'exigeait que le remplaçant nommé
soit à la même pause, et elle ne voyait pas YPE, dont le commentaire nomme
VGG (qui ouvre la nuit en PM) alors que c'est FPA qui tient sa place.
Rejouée sur la version d'avant la correction, elle ne trouvait rien : un
contrôle qui ne peut pas échouer ne contrôle rien.

Trois familles d'erreurs, triées à la main :

- **la journée entière de flex time repris** (YPE, PDR) : corrigée, voir
  la section précédente ;
- **une absence écrite en deux moitiés, la seconde dans le commentaire** :
  `["AM","1/2VA","+4h rhs remplacé par SPS"]`. La lecture ne prend que la
  cellule : la personne paraît présente 4 h, avec prime et chèque-repas.
  **59 journées sur l'année**, dont 50 en « +Nh rhs ». Aucune fiche de LCI
  ni de VBN n'en porte : c'est une question au client ;
- **« remplace Y » chez un collègue, alors que la cellule de Y ne porte que
  son code** : `FPA ["PM","R-CM","remplace FLI"]` et `FLI ["PM"]` le 16/01,
  soit deux contremaîtres en PM. **16 journées.** Deux relèvent d'une
  évaluation (partielle). Pour les autres, le classeur ne dit pas si Y
  était absent ou déplacé : c'est une question au client.

**Les deux moitiés sont lues depuis le 26/09/2026.** Le client : « 2 A »,
c'est-à-dire que le complément du commentaire complète la journée. Le
point des 16 journées « remplace Y » sera vérifié avec lui le lendemain.
`lireJournee()` lit, à sa fin, chaque « +N h rhs / RTT / DTT / VA / -FT »
du commentaire. Les heures de rhs vont au compteur de récup. HS de la
fiche (`rhsJ` → `rec.rh`), comme une reprise écrite dans la cellule. Les
autres codes rejoignent `r.ax`, sans doublon : KDN le 28/02 avait déjà
son « 4h VA » lu par un autre chemin, et la première version l'écrivait
deux fois. Les heures prestées valent **au plus la journée moins toutes
les absences du jour**. Une plage déjà écourtée n'est donc pas retranchée
deux fois : ADK `["7h-15h","8h-12h","+4RHS"]` reste à 4 h, et CKS
`["7h-15h","1/2VA","+2h RTT Départ à 9h"]` tombe à 2 h, ce que dit son
départ. Le flex time repris ne retire rien aux heures payées : c'est la
présence qui baisse. « +4h CSS » est une demi-journée de congé sans
solde, non payée (le client, le 26/09/2026). Elle a désormais ses codes
cachés, `4H CSS` et `1/2 CSS`, de la famille de `SANS SOLDE` : SMA le
10/09 est une absence complète, ½ DTT + ½ CSS. Une journée de plus en
absence ; neuf règles, compteurs, manques et Recyclage identiques à
l'octet.

Mesuré : **20 journées passent de prestées à absences** (14 494 → 14 474),
les autres ont moins d'heures ; neuf règles à zéro ; compteurs et
`--manques 0926` identiques à l'octet ; année 264 → **269** places creuses ;
22 couples au quota, inchangé. Au navigateur, le 27/02 de SMA s'affiche
« ½VA » dans son calendrier, et plus « AM ».

**Les personnes en journée entrent dans le tableau « Qui travaille »**, sur
une dernière ligne « En journée » qui occupe toute la largeur : la journée
n'a pas de pause, et trois colonnes vides l'auraient fait lire comme un
manque. Sous chaque trigramme, ce qui l'amène en journée (F, CPPT, DS). Le
tableau porte désormais aussi la formation hors poste, une ligne par pause.
Ces personnes vivaient seules dans une carte « Hors poste », sous les
malades, alors qu'elles sont à l'usine ce jour-là : **la carte a disparu**,
avec `ligne()` et les styles `.eqt`, qui ne servaient plus qu'à elle.

Le 28/09 : 11 personnes en journée, sur deux lignes à 390 px. Rien ne
déborde à 320, 390 et 1280 px, en clair et en sombre, hors ligne compris.
Les quatre sorties du vérificateur sont identiques à l'octet.

### Le mémo des trois fonctions du mois

`equipeDuJour()` recalculait `cycleDuMois()`, `epargnesDuMois()` et
`renvoisDuMois()` **pour chaque personne et chaque jour**, et la dernière
balaie l'année entière à chaque appel. Une saison coûtait donc 265 jours ×
77 personnes × 365 journées de balayage.

Elles ne dépendent que de la personne, du mois et de l'heure de journée :
`moisDe()` les retient. **`--manques` est passé de 90 s à 8,7 s**, au
résultat identique — et c'est ce qui rend la polyvalence calculable dans le
navigateur, 1,6 s à l'ouverture du repli.

La clé porte `hJour` : un changement de réglage refait le calcul.

**`finAbsence()` gardait son propre cache, et il ne survivait pas à
l'appel.** Mesuré le 26/09/2026, profileur à l'appui : l'onglet Recyclage
figeait l'écran **13,6 s sur un processeur de téléphone** (2,9 s sur PC), et
84 % de ce temps était là. Chaque malade de chaque journée depuis février
refaisait `cycleDuMois()` pour tous les mois de sa série — et une série de
trois cents jours se relisait depuis chacun de ses jours.

Elle prend donc ses tables dans `moisDe()`, et retient dans `_finCache` la
fin trouvée pour **chaque** journée parcourue : partie du 2 ou du 3 d'une
même absence, la recherche aboutit au même dernier jour, et s'arrête dès
qu'elle en rencontre un déjà connu.

**Recyclage 13,6 s → 1,4 s** au téléphone simulé (0,31 s sur PC), Résumé
785 → 167 ms. Rien d'autre ne bouge, et c'est prouvé : les 1 847 journées de
maladie de l'année rendent la même fin qu'avant, **dans l'ordre, à rebours et
dans le désordre** — le cache ne doit pas dépendre de l'ordre des appels —,
et les quatre sorties du vérificateur (règles, `--manques`, `--polyvalence`,
`--compteurs`) sont identiques à l'octet.

`_finCache` entre dans la découpe du vérificateur, déclaré juste au-dessus
de la fonction : sans lui, `finAbsence()` y lèverait une `ReferenceError`.

### Les manques d'effectif à venir

```bash
node tools/verifier-calendrier.js --manques [MMJJ]
```

Mesure ce que le module « Postes en manque » de l'onglet Équipe annoncera,
de la date donnée à la fin de l'horaire. Il ne le simule pas : il découpe
`equipeDuJour()` et `postesDePause()` dans `index.html` et les rejoue. Une
alerte qui compterait autrement que la vue du jour serait pire que pas
d'alerte.

**Au 22/09/2026, classeur de 15 h 46 : 15 journées sur 101, 17 places
creuses** — fermentation (9), terrain arrière (3), chaudières (2), gluten
(1). Si ce nombre s'effondre ou explose
après une modification du rééquilibrage ou des polyvalences, c'est une
régression.

L'outil met une minute et demie : tout son code passe par `eval()`, que V8
n'optimise pas. **Ce n'est pas la vitesse de l'application** — le navigateur
fait les mêmes 102 journées en 2 secondes.

**Ne jamais tester la fonction d'une personne avant d'avoir lu sa cellule.**
`posteTenu()` le faisait : `estCadre()` renvoyait « adjoint » avant que
`posteEcrit()` ne lise `["AM","Gluten","Remplace SLT"]`. 184 journées de
cadres nommaient ainsi un poste sans être lues, et le module criait au manque
sur la moitié de ses alertes. Voir `docs/conversion-horaire.md`, « La cellule
prime, y compris sur la fonction de la personne ».

Le module de l'application ne regarde **jamais en arrière** — un manque passé
ne se comble plus. C'est sa règle de naissance, et elle n'a plus besoin d'être
écrite au-dessus de lui : « À partir d'aujourd'hui » occupait une ligne pour
décrire ce qu'il est.

**Son en-tête coûtait 189 px avant la première journée**, presque autant que
quatre jours de contenu : un titre de 28 px, un sous-titre, une légende et une
rangée de boutons. Le client, le 22/09/2026 : « moyen de faire beaucoup
mieux ». Titre et compte tiennent maintenant sur une ligne — « journées » deux
fois dans la même phrase ne disait rien de plus la seconde — et le tout fait
**83 px**. La carte passe de 586 à 414.

**« 1 poste à déterminer ce jour-là »** occupait sa propre ligne en italique
sur quatre journées de neuf. C'est une pastille `+1 ?` de la rangée, à côté
des postes qu'elle nuance : l'un de ces postes indéterminés est peut-être
celui qui manque, et c'est là qu'on le lit.

### La polyvalence : combien de journées complètes à chaque poste

```bash
node tools/verifier-calendrier.js --polyvalence [MMJJ] [--tout]
```

Le client, le 22/09/2026 : « pour les opérateurs, cela peut être bien aussi
d'indiquer combien de jours (complet 8h) ils ont fait sur chaque poste de
production ; les autres ont un quota de polyvalence de 10 jours par poste,
les adjoints 5 jours par poste ».

Il ne recompte rien à côté : il **découpe** `calculerPolyvalence()` et
`polyvalenceDe()` dans `index.html`. Sa première version les réimplémentait,
et elle a divergé le jour même sur BBZ — « son poste » n'y suivait pas la
même chaîne.

Cinq choix, tranchés avec le client le 22/09/2026 et écrits dans le code
plutôt que cachés :

- **la période court du 1er février au 1er février**, et non sur l'année
  civile : « la polyvalence se déroule sur la période du 1er février au
  1er février de l'année d'après ». Compter depuis le 1er janvier ajoutait
  un mois appartenant à la période précédente — quatre couples au quota de
  moins une fois janvier écarté. L'horaire ne couvrant qu'une année, une
  période à cheval n'est mesurable que pour sa part présente dans le
  fichier ;
- on s'arrête **AUJOURD'HUI**. Le classeur court jusqu'au 31/12 ; compter
  la fin de l'année créditerait des journées qui n'ont pas eu lieu, et ATR
  atteignait ainsi le quota aux chaudières sans y avoir mis les pieds ;
- **le poste habituel ne compte pas** : un quota de dix journées ne veut rien
  dire sur le poste qu'on tient tous les jours, et NPE y affichait 211/10 ;
- seules les pauses **AM, PM et N** — le « Jour » ne tient pas un poste de
  production, et `postesDePause()` n'y attend d'ailleurs personne ;
- **huit heures pleines ou rien** : une demi-journée n'apprend pas un poste à
  moitié.

**« Son poste » se prend avec `posteTenu(p,[],hJour,null)`, pas avec
`posteHabituel()`.** Les deux fonctions répondent à la même question et la
seconde répond moins bien : elle rend « terrain arrière » dès que le rôle de
feuille le dit, sans la garde `tientTerrainArriere()`. BBZ y gagnait terrain
arrière alors qu'il n'y a pas fait une journée et qu'il en a fait 133 en
distillation. `posteParDefaut()` vient en dernier, faute de quoi PDE n'a pas
de poste habituel et ses 134 journées à la station passent pour de la
polyvalence.

**Une journée ne compte QUE si la personne possède la polyvalence du
poste.** Le client, le 22/09/2026 : « les polyvalences ne doivent compter que
s'ils ont cette polyvalence dans leurs connaissances ; AAI et ALZ ont été à
la STEP pour voir à quoi cela ressemblait sans faire de polyvalence ». Une
journée à un poste qu'on ne possède pas n'apprend pas ce poste : on y est
passé, on ne l'a pas tenu. Le poste non possédé disparaît donc de la ligne,
journées comprises — quatre journées à la STEP chez trois personnes.

L'outil les liste tout de même, sous « journées tenues SANS la polyvalence
du poste » : elles ne comptent pas, mais les taire serait perdre une
information que personne d'autre ne porte.

**Un opérateur EN FORMATION n'a pas de poste à lui.** Le client, le
22/09/2026 : « les opérateurs en formation ne peuvent pas posséder comme
poste par défaut le poste où ils sont en formation ; ils ne doivent pas y
faire de recyclage vu qu'ils n'y sont pas validés (exemple SKS en
meunerie) ». La ligne 9 leur en donne bien un — SKS la meunerie, LHR et GST
les chaudières — mais c'est celui où ils APPRENNENT. Aucun des huit ne l'a
dans sa polyvalence, ce qui le confirme : on n'est pas validé là où l'on se
forme.

Ce poste ne devient donc ni « son poste » ni une ligne de recyclage : les
112 journées de SKS en meunerie ne comptent pas. Sa case porte un **F** —
muette à côté de tant de journées, elle poserait plus de questions qu'elle
n'en résout.

`posteAttitre()` et `posteDeFormation()` partagent la même chaîne à dessein :
c'est le MÊME calcul, seule la personne décide lequel des deux il devient.
Une première version calculait le poste une fois dans `polyvalenceDe()` et
une fois dans le rendu — la seconde copie ignorait la règle, et la pastille
pleine restait sur la meunerie de SKS. **Deux copies, et c'est toujours la
seconde qui reste en arrière.**

**Attention au piège documenté plus haut** : polyvalence INCONNUE n'est pas
polyvalence VIDE. Les trois personnes sans liste déclarée sont des opérateurs
en formation, qui n'en ont effectivement aucune ; les quatre que `CORRECTIONS`
avait dépouillées ont retrouvé la leur. Si cela changeait, la règle stricte
effacerait des polyvalences réelles sans rien dire.

**« 0/X » ne porte AUCUN fond.** Le client, le 22/09/2026 : « quand c'est
0/X il ne faut pas changer le background ». Elle en avait un, gris, pour se
distinguer du néant — mais un fond est une alerte, et il n'y a rien
d'anormal à pouvoir tenir un poste sans l'avoir encore fait. Le chiffre le
dit. Les deux fonds qui restent signalent chacun un écart : le vert un quota
atteint, le jaune une formation.

**« 0/X » se lit dans la colonne d'un poste dont la polyvalence est acquise
sans qu'un seul remplacement ait été fait.** Le client : « il doit être écrit
0/X dans la colonne où ils ont la polyvalence mais qu'ils n'ont pas encore
fait de remplacement ». Une case vide ne disait pas si la personne ne pouvait
pas tenir le poste ou si elle le pouvait sans l'avoir encore fait — et c'est
justement cela qu'un contremaître cherche. « Terrain arrière » ne figure dans
aucune liste de polyvalence du classeur : il se déduit de Fermentation ET
Distillation, comme `tientTerrainArriere()` le fait partout ailleurs.

**Au-dessus de la grille, la période et rien d'autre.** Le client, le
22/09/2026 : « pas très compréhensible » — et, interrogé sur quoi : « le
texte au-dessus des postes », puis « c'est la légende au-dessus que je
n'aimais pas ». Cette ligne annonçait quatre chiffres — personnes, postes au
quota, total, sans remplacement — avant qu'on ait vu la grille : un bilan
par-dessus ce qui n'était pas encore lu. La période, elle, se lit AVANT,
sans quoi aucun nombre du tableau ne veut dire quelque chose. Elle tient
désormais sur la ligne du titre.

**La vue de bureau a de la place : qu'elle s'en serve.** Le client, le
22/09/2026 : « optimise la vue PC, les chiffres sont peu visibles (les 10
et 5), titre plus grand, et la date et le poste à droite comme sur mobile ».

Les réglages de la grille sont ceux d'une colonne de 38 px sur un
téléphone ; à 1280 px ils laissaient la grille minuscule au milieu du vide,
et le quota — en petit, derrière la barre, à demi effacé — ne disait plus
sur combien on compte. Au-delà de 760 px : titre à **20 px**, chiffres à
**13**, quota à **11 px et 80 % d'opacité** au lieu de 9 px et 55 %.

**La date et le poste se calent à droite**, comme sur téléphone. La marque
se réduisait à sa largeur de contenu — `margin-right:auto` la pousse à
gauche et elle ne réclame rien de plus — si bien que le bloc du jour restait
collé au trigramme avec mille pixels de vide à sa droite. `flex:1 1 auto`
lui rend la place libre, et le `margin-left:auto` de la colonne du jour fait
le reste : 16 px du bord, ou 14 px du chèque du net sur les onglets qui le
portent.

**La requête se pose APRÈS les règles qu'elle doit battre**, et non dans le
haut de la feuille où elle avait d'abord été écrite : une requête média
n'ajoute AUCUNE spécificité, donc à égalité c'est la dernière écrite qui
gagne. Elle n'avait rien changé du tout. C'est la TROISIÈME fois que ce
piège se referme sur ce fichier — la zébrure de cette grille, la barre
d'onglets sous 375 px, et celle-ci.

**Les intitulés de poste restent abrégés et horizontaux**, et la légende
reste SOUS la grille. Une version verticale en toutes lettres et une légende
remontée ont vécu une demi-heure : « j'aimais bien les postes écrits comme
avant ». Les deux tenaient à toutes les largeurs — ce n'était pas la
question. **Deux mots de retour valent mieux que trois hypothèses**, et il a
fallu demander pour trouver la bonne.

**La liste est alphabétique, sans intercalaire d'équipe** : on cherche
quelqu'un par son trigramme, pas par son équipe.

**Au 22/09/2026, classeur de 15 h 46 : 33 couples personne-poste au quota
sur 101, dont 22 où la polyvalence est acquise sans un seul remplacement** —
mesuré identique par l'outil et par le navigateur.

Second contrôle, indépendant, et il se lance lui aussi :

```bash
node tools/verifier-calendrier.js --compteurs
```

Il recalcule les compteurs flex time de chacun depuis ses journées et les
compare à ceux du pied de classeur, saisis à la main. Les neuf règles
regardent ce que la case AFFICHE ; celui-ci additionne ce qu'elle COMPTE.
**Tout le monde doit concorder exactement : 78 sur 78 depuis le 18/10/2026.**
La divergence de FPA (3 h de −FT de trop), écrite ici comme « une erreur du
classeur » depuis le 22/09, **n'en était pas une** : sa cellule du 07/11
porte « 3h -FT » et celle du 03/11 « 3h -FT pris le 07.11 », et
l'application comptait les deux. Un congé renvoyé que la journée écrit déjà
ne se compte plus deux fois (voir « Le cadre du mois, repris case par
case »). Une divergence revenue est donc une faute de lecture à chercher,
pas un écart connu.


### Un recyclage se confirme dans le classeur (22/10/2026, `nfdm-v948`)

Le client, devant « six personnes gagnent ou perdent une journée de
recyclage » : « il faut bien vérifier pour les recyclages, car attribuer
des recyclages sans confirmation qu'il tenait bien le poste est donc
faux ». `calculerPolyvalence()` comptait toute journée complète passée à
un autre poste que le sien. Cela incluait celles où c'est l'APPLICATION
qui y avait porté la personne : le rééquilibrage (`comble`) ou une
déduction (`deduit`). Elles ne comptent plus. Restent, parce que le
classeur les écrit : le poste écrit dans la case, « remplace X », « remplacé
par » qui le nomme, un jour tranché par le client.

**Mesuré contre le classeur RH des recyclages**
(`data/recyclages-2026.json`, ses dates par personne et par poste), un
script jetable du bloc-notes :

| | avant | après |
|---|---|---|
| journées comptées par l'application et confirmées par la RH | 143 | 137 |
| journées comptées par l'application, absentes du classeur RH | 402 | 302 |
| journées du classeur RH que l'application ne compte pas | 66 | 72 |

Sur les 106 journées retirées, 100 n'étaient pas dans le classeur RH. Au
quota (`--polyvalence`), 26 couples personne-poste deviennent 20. Les
plus fortes baisses : DWS aux chaudières (16 → 3), GPO en fermentation
(12 → 4), SKS en distillation (13 → 1). Les manques, les compteurs et les
agendas sont identiques. Le profil d'un opérateur suivi par la RH garde
la valeur du classeur RH (RECYC_OFF) : ce sont les « jours planifiés »
de l'application qui changent.

Il reste 302 journées que l'application compte et que le classeur RH
n'a pas. Ce peut être un remplacement réel que la RH n'a pas enregistré,
ou une lecture trop large. Elles ne se tranchent qu'avec la RH.

### Les compteurs FT de chacun, revérifiés (27/10/2026)

Le client : « les compteurs FT de chacun sont-ils corrects ? ». Trois
mesures, chacune indépendante de l'autre :

- `verifier-calendrier.js --compteurs` (la lecture de l'application) :
  79 personnes concordent avec les colonnes +FT et −FT du classeur 2026,
  0 divergent.
- Le motif du pied de l'Horaire (`^(\d)h\s*([+-])FT$`), recompté en Python
  sans rien emprunter à l'application : 79 sur 79 en 2026, 76 sur 76 en
  2027 ; AUCUNE annotation contenant « FT » n'échappe au motif.
- Le solde affiché (le « Total » de la ligne 430) ne se vérifie pas : il
  porte le report de fin 2025, écrit en constante dans la formule, et la
  copie du classeur ne garde que des valeurs. Le report déduit
  (Total − (+FT) − (−FT)) va de −8 à 90 h ; deux personnes ont un Total
  de 0 pile pour une année à +7 et +1. Les deux erreurs de formule
  relevées par l'inventaire (`docs/plateforme.md`, section 5 : un Total
  qui lit une ligne vide, un bloc décalé de quatre lignes qui perd les
  29-31/12) ne se retrouvent qu'avec les FORMULES : question au client
  (`docs/questions-client.md`). En 2027, 10 personnes n'ont pas de Total
  (compteurs non fiables, `COMPTEURS_FIABLES`).

### Les manques que les commentaires expliquent (27/10/2026)

Le client, après la nuit du 31/10 restée sans contremaître alors que trois
commentaires disaient qui la faisait : « je pensais que c'était déjà le
cas, car les commentaires sont toujours la source principale des réponses
en cas de manque ». Ce ne l'était pas : `--manques` comptait les places
vides sans rien confronter aux commentaires, et la ligne « 31/10 N
Contremaître 0/1 » a été lue comme un vrai trou.

`node tools/verifier-calendrier.js --manques-commentes [MMDD]` : pour chaque
place vide, le titulaire du poste prévu à cette pause et absent, puis tout
commentaire du même jour qui le nomme (chez n'importe qui), et le sien s'il
dit un remplacement. Code de retour 1 s'il en reste ; ceux qu'un humain a
lus et jugés vrais s'écrivent dans `tools/manques-admis.txt`
(« MMDD PAUSE Poste # raison »). Par défaut d'aujourd'hui au 31/12.

- Épreuve : sur la version d'avant la correction du 31/10, depuis le
  27/10 → 1 manque commenté (le 31/10, avec les trois commentaires), code
  1 ; sur la version corrigée → 0 sur 8 places vides, code 0.
- **Toute l'année (`0101`) : 100 places vides sur 204** ont un commentaire
  du jour qui nomme le titulaire absent, toutes avant le 27/10. Classées :
  46 où quelqu'un écrit « remplace [titulaire] » (le cas du 31/10 :
  presque sûrement des fautes de lecture — le 29/01 et le 02/02, deux
  contremaîtres de l'après-midi nommés en toutes lettres) ; 27 « échange
  avec » ; 26 où seul le titulaire écrit « remplacé par » ; 1 autre. Par
  poste : contremaître 35, gluten 17, chaudières 15, fermentation 13,
  terrain arrière 9, distillation 4, meunerie 4, STEP 3. À reprendre une
  par une, les commentaires d'abord.

Le 28/10/2026 (`nfdm-v1168`), première reprise des 100. Une règle sûre :
« remplace X », SANS heures, écrit par quelqu'un qui preste une AUTRE pause,
donne au poste vide de X le recouvrement de sa présence (`lectureAgenda`)
avec la pause, en relais. Premier essai, sans la condition « autre pause
PRESTÉE » (la cellule peut écrire PM et l'annotation AM) : 43 lignes du
placement changeaient, dont des gens comptés deux fois (une gluten à 2/2
avec le même en titulaire et en relais) et trois déplacés à tort. Avec
elle : 3 journées, les 29/01 PM (contremaître : 6 h – 18 h puis
18 h – 6 h), 16/02 AM (chaudières : un 6 h – 18 h) et 14/09 PM
(chaudières : deux pièces) ; places creuses de l'année 210 → 207 ; neuf
règles, polyvalence, compteurs, fiches, `--manques 0926` et agendas
identiques. Le 02/02 ne se résout PAS : « 4h +FT » n'allonge pas la
présence lue (`lectureAgenda` ne lit pas les heures de flex time comme
une plage). Les 97 restantes demandent des règles que le classeur ne
donne pas : quatre questions au client (`docs/questions-client.md`).

### Le parcours de l'application, dans le dépôt (28/10/2026)

Le client : « go complet » (les skills en renfort). Les essais au
navigateur vivaient dans des scripts jetables, perdus à chaque session.
`tools/parcours.js` reste : il sert le dossier lui-même (module `http`,
aucune dépendance que Playwright), simule la base (comptes et rôles,
listes vides), et ouvre Accueil, Planning, Équipes et Horaire pour quatre
rôles (sans compte, opérateur, hiérarchie, RH) sur six écrans (320, 390,
iPhone aux zones protégées simulées, couché 844, iPhone couché à
encoche, PC 1280), puis recharge hors ligne. Faute : erreur JavaScript,
débordement horizontal, cadre sous la barre ou sous le rail, page vide
hors ligne. 91 essais, 4 min ; `--vite` (portrait seul) 30 s.

- Premier passage : 91 essais, 0 faute.
- Épreuve : une copie sabotée (un bloc de 2 000 px et une erreur
  JavaScript) → 5 essais, 5 fautes, code 1. Le contrôle mord.
- Règle ajoutée au tableau d'avant commit de `CLAUDE.md`.

### L'audit mesuré, après l'Accueil (28/10/2026, `nfdm-v1170`)

Script (contraste WCAG calculé sur le fond réel, textes sous 11 px, cibles
sous 24 px, éléments interactifs sans nom) sur 390 × 844, 844 × 390 et
1280 × 800, rôle RH, chaque onglet :

- **Contraste** : 0 texte sous 4,5:1 (3:1 pour le grand texte).
- **Sans nom** : l'onglet Horaire de la barre du téléphone (libellé caché,
  aucun `aria-label`) — nommé (`nfdm-v1169`).
- **Sous 11 px** : la pastille des onglets (10,5), au Planning les heures
  sous les trigrammes (9 au téléphone), les équipes et les noms de ligne
  (10,5), aux Équipes les rôles, les polyvalences, l'en-tête de
  l'organigramme et le tableau des polyvalences (9 à 10,5). Tous à 11 px.
  À 320 px : rien de coupé, aucun débordement ; le bord droit de
  l'organigramme identique au pixel près à la version d'avant (un premier
  regard sur une capture recadrée avait cru le contraire).
- **Cibles** : les trigrammes de l'organigramme (36 × 21) et les boutons
  du tableau des polyvalences (20 × 24) passent à 24 × 24 au moins.

### Les couleurs des pauses au validateur (skill dataviz, 28/10/2026)

`validate_palette.js` sur AM, PM, N, D en thème sombre (surface
`#212737`) : séparation pour les daltonismes et pour la vision normale
**réussies** (ΔE 11,7 et 16,0 au plus juste) ; le bleu-vert de
l'après-midi est sous le plancher de chroma (0,085 : il tire vers le
gris) et N et D sont sous 3:1 contre la surface. Gardé tel quel : ces
couleurs portent du texte blanc dans les badges (un bleu-vert plus vif
fait passer le blanc de 5,0 à 4,5:1), elles sont celles de l'horaire, et
la légende et le calendrier (texte) donnent le relief que le validateur
exige.
- Relu à l'œil (Effectifs, tableau de bord RH, demandes, personnel) :
  l'en-tête « Sur site » de l'espace RH gardait le point vert en tête ;
  il prend l'icône de l'Accueil (`SITE_ICO`), le point vivant derrière
  le titre. Les titres centrés des pages de l'espace RH et des Effectifs
  restent : ce sont des titres de page, pas des en-têtes de carte.
- Parcours complet après correction : 91 essais, 0 faute.

### La revue de code des deux derniers jours (28/10/2026, `nfdm-v1172`)

`code-review` (niveau « high ») sur 41 commits. Dix constats, chacun
revérifié ; corrigés :

- `remplaceAbsent` : le drapeau `i` faisait de « remplacé par une
  collègue » un remplacé (`[A-Z]{3}` prenait « une »). Trigramme en
  capitales. Épreuve : l'ancienne expression accepte la phrase, la
  nouvelle non ; placement de l'année identique à l'octet.
- Horaire : Entrée sur une journée commentée ouvre de nouveau sa bulle
  (la case d'annotation n'était pas atteignable au clavier) ; l'annotation
  tronquée retrouve son infobulle (`title`) au PC.
- Sur site : les contremaîtres d'une pause n'y comptent que pendant elle,
  remise comprise (sans borne, celui de la nuit, en 18 h – 6 h, passait
  pour celui de l'après-midi dès 19 h) ; demain matin est lu pour la
  relève de 6 h ; part de relais et présence au poste distinguées
  (`part`) — un premier essai mêlait la nuit à la relève de 14 h. Mesuré
  à huit heures du 27 au 1/11.
- Sur site : un calcul de placement par minute (`siteMemo`), au lieu
  d'une vingtaine par rendu.
- Le trou entre téléphone couché (≤ 500 px de haut) et tablette
  (≥ 501 px) : 500,4 px de haut ne prenait aucune des deux mises en
  page ; le seuil haut passe à 500,01 px (37 requêtes).
- « Mon rythme » au PC retombait à 10 px : 11.
- `--manques-commentes` sur une année finie lisait encore le 31/12 :
  plus rien (`1232`).
- Nettoyage : ternaire aux deux branches identiques, paramètre mort,
  règle `.site-rel` en double. `grEditer` reste (la saisie RH au PC).
- Laissé : la condition du téléphone couché recopiée dans chaque requête
  (une classe sur `<html>` la remplacerait ; à faire avec une passe
  `simplify` dédiée).

### Le téléphone couché : une seule définition, contrôlée (28/10/2026)

La revue de code du 28/10 avait laissé une proposition : remplacer la
condition du téléphone couché, recopiée partout, par une classe posée sur
`<html>`. Relue avant de la faire, elle coûtait plus qu'elle ne rendait.
CSS n'a pas de requête média nommée que les navigateurs comprennent
(`@custom-media` n'est pas pris en charge). Une classe obligerait donc à
préfixer chaque règle des 58 blocs concernés (20 « téléphone », 31 « au
moins tablette », 7 variantes), et à écrire en JavaScript ce que le
navigateur fait seul au changement d'orientation. Le risque réel était
ailleurs : qu'une copie diverge des autres, et casse une seule mise en
page sans aucune erreur.

`tools/parcours.js` commence donc par un contrôle sans navigateur. Toute
requête `@media` ou `matchMedia` qui parle de 760/761 px ou de 500 px de
haut doit être, au caractère près, l'une des six formes admises : le
« téléphone » (portrait étroit, ou couché de 500 px de haut au plus) et
son complément exact. Une fraction de seconde ; `--statique [fichier]`
le lance seul. Éprouvé sur trois copies sabotées, toutes refusées (code 1) :
une hauteur passée de 500,01 px à 501 px dans un bloc, le `matchMedia` de
la navigation passé de 1 099 px à 1 100 px, et un bloc
`@media (max-width:760px)` ajouté sans la condition du couché. Sur le
fichier réel : toutes identiques, puis le parcours rapide : 6 essais,
0 faute.

### Le démarrage, mesuré (28/10/2026)

Le chantier « découper `index.html` pour accélérer le démarrage » (ouvert
le 09/10, « environ une seconde de lecture du script sur un téléphone
lent ») a été mesuré avant d'être entrepris. Mesure : Playwright, téléphone
390 px, processeur ralenti 4 fois (un téléphone moyen), compte connecté,
service worker installé, quatre rechargements. Le fichier fait 2,1 Mo et
31 165 lignes. Le chargement se termine en 0,55 à 0,98 s, et l'Accueil
est rempli entre 0,89 et 1,47 s ; le premier affichage a lieu entre 0,14
et 0,26 s.

Le profil montre que le gros du calcul ne retarde pas l'ouverture. Ce
calcul, c'est la pastille des Effectifs, qui parcourt toutes les journées
à venir : environ 1,5 s de processeur. Il passe déjà en tranches de 40 ms,
au repos, depuis l'audit du 23/10. Couper le fichier irait contre le
principe d'un seul `index.html` sans construction, et ne gagnerait que
la compilation du script, quelques dixièmes de seconde. Chantier fermé
sur ces mesures ; il se rouvrira si un téléphone réel s'en plaint.
