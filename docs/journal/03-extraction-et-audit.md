# Le convertisseur, l'export entier, l'audit du 26/09/2026

Historique déplacé tel quel de `CLAUDE.md` le 18/10/2026. Les dates, mesures et erreurs y restent.

## Le convertisseur ne gardait qu'un commentaire sur deux

Le client, le 23/09/2026 : « de nouveau tu poses des questions sans vérifier
toutes les cellules ni tous les commentaires ». Il avait raison, et la cause
n'était pas dans ma lecture : elle était dans le fichier.

**Chaque personne occupe DEUX colonnes** — la cellule et son annotation — et
**chacune peut porter son propre commentaire Excel**. Le convertisseur
écrivait `cm.get(cellule) or cm.get(annotation)` : dès que la première en
avait un, la seconde était jetée sans un mot. Une ligne.

Mesuré sur le classeur du 23/09/2026 : **684 journées portent deux
commentaires différents, et 496 n'en gardaient qu'un.** Ce qui disparaissait
n'était pas du décor :

> « remplace GPS **de 14h à 16h** » · « Remplace KDN Rappel le 10/03 **+3
> HS** » · « Remplace QDE **RAPPEL le 30/07** » · « départ à 19h00' » ·
> « arrivée à 23h00' » · « **conserver prime de nuit** »

Des heures, des rappels et une prime. Le client a dû signaler lui-même les
« rappel le 22.04 » d'AFA parce que rien ne les montrait — et j'ai commencé
par lui répondre que le classeur ne les portait pas.

`_les_deux()` joint les deux par un saut de ligne, comme Excel joint déjà
les lignes d'un même commentaire, et ne garde que le plus complet quand l'un
contient l'autre : le classeur recopie souvent la cellule sur l'annotation,
et répéter une phrase la ferait lire deux fois par les motifs de
remplacement.

**373 journées chez 61 personnes** ont retrouvé leur commentaire. Rien
d'autre n'a bougé — ni arrivée, ni départ, ni compteur, ni polyvalence :
le comparateur ne montre que cette section. Les journées de rappel passent
de **462 à 487**, et **9 231 signes** de commentaire reviennent.

### Un prénom mal orthographié par son propre auteur

Et ces commentaires récupérés ont aussitôt amené un nom dans le JSON d'un
dépôt PUBLIC. `tools/verifier-depot.py` l'a arrêté avant le commit — c'est
exactement ce pour quoi il existe, et ce n'est pas le convertisseur qui l'a
vu.

La tête du commentaire est écrite **avec une faute de frappe de son auteur**
— un « e » final manquant au prénom. `_motif_auteurs()` retire les noms que le
classeur DÉCLARE dans `<authors>` : le nom de famille correspondait, le
prénom tronqué non. Le motif a donc emporté la moitié qu'il reconnaissait et
laissé l'autre. **Une moitié de nom nomme encore la personne** — c'est la
règle déjà écrite pour l'anonymiseur, et elle s'est vérifiée ici.

On ne peut pas deviner les fautes de frappe. On peut lire la STRUCTURE :
**ce qui précède le premier deux-points, quand c'est court ET que cela nomme
un auteur déclaré, est une signature quoi qu'il y soit écrit.** La tête part
alors en entier.

La borne de longueur n'est pas décorative : sans elle, un commentaire citant
un auteur au fil du texte verrait tout son début avalé jusqu'au premier
deux-points. Et une tête qui ne nomme personne — « MPE : Maintien prime
PM » — n'est pas touchée : c'est le piège que `CLAUDE.md` décrivait déjà
pour l'anonymiseur.

Deux têtes retirées sur tout le classeur, et rien d'autre : le prénom, et un
identifiant de connexion. **L'anonymiseur, lui, n'avait pas ce trou** — zéro
occurrence dans `data/classeur-2026.xlsx`, parce qu'il retire la signature
AVANT le remplacement.

Contrôles après installation : neuf règles à **zéro**, 14 653 journées
prestées, compteurs **76/77**, découpe de `comparer-fiches` à l'épreuve, six
onglets rendus. Les motifs trop étroits passent de 46 à **49** — il y a
simplement plus de texte à lire, et la douzième règle fait son travail.

## Tout le classeur, et pas seulement ce qu'on sait lire

Le client, le 25/09/2026 : « toutes les cellules, commentaires, pages,
lignes, colonnes doivent être récupérés avec le fichier ; après le
convertisseur tout doit être dans la base de données, sauf les vrais noms et
prénoms des travailleurs ».

```bash
python3 tools/exporter-classeur.py data/classeur-2026.xlsx \
        data/classeur-2026-brut.json
```

**Le convertisseur ne garde que ce qu'il sait lire**, et c'est son rôle : il
produit l'horaire dont l'application se sert. Mais deux fois une information
s'est perdue parce qu'elle n'était pas dans les lignes qu'il regardait, et
une perte silencieuse est une perte qu'on ne corrige jamais. Il annonçait
déjà ce qu'il laissait ; **annoncer n'est pas garder**.

Cet outil ne lit rien : il **RECOPIE**. Douze feuilles, **75 660 cellules**
à leur adresse, **11 564 commentaires**, **521 étendues fusionnées** — contre
27 574 journées et 6 702 commentaires dans l'horaire. C'est à peu près le
DOUBLE de ce que le convertisseur retenait.

**IL PART DU CLASSEUR DÉJÀ ANONYMISÉ, ET C'EST TOUT L'ARGUMENT.** Anonymiser
à nouveau ici demanderait d'écrire une troisième fois des motifs de noms,
donc d'ouvrir un troisième trou — et ce fichier en a déjà décrit deux.
`data/classeur-2026.xlsx` est passé par l'anonymiseur ET par son second
contrôle indépendant : il ne porte plus de nom, et c'est prouvé. **On
recopie une source propre plutôt que de nettoyer une source sale.**

**Sans recopie des fusions** : on veut le fichier tel qu'il est écrit. Seule
la case en haut à gauche d'une fusion porte la valeur ; les étendues sont
exportées à part, de sorte que rien ne se perd et que rien ne s'invente.

**Il réemploie la lecture du convertisseur** plutôt que d'en écrire une
autre : deux lecteurs de xlsx dans le même dépôt finiraient par diverger, et
c'est toujours le second qui reste en arrière.

**Un identifiant de connexion survivait, et il est parti.** `RT0xxxx`, au
fil de six commentaires — la même phrase recopiée d'une feuille à l'autre.
Ce n'est pas un nom, donc l'anonymiseur le laisse passer, et il a raison :
il remplace des noms. Le convertisseur, lui, l'emportait par accident, parce
qu'il ouvrait une tête de commentaire. **Ici rien ne l'emporte par accident,
puisque rien n'est interprété** — d'où une règle nommée. Dans un dépôt
PUBLIC, un login d'entreprise se recoupe avec les annuaires de la maison
aussi sûrement qu'un nom. Le motif est étroit à dessein — deux lettres et
quatre à six chiffres — et mesuré : **un seul jeton de cette forme dans tout
l'export**, six occurrences, zéro après.

**Le garde-fou du dépôt a été éprouvé DANS LES DEUX SENS sur ce fichier**, et
la première épreuve a échoué pour une raison qu'il faut connaître : un nom
factice planté dans le JSON n'a rien déclenché, **parce que le fichier
n'était pas encore suivi par git**. `verifier-depot.py` lit les fichiers
SUIVIS ; un fichier neuf lui est invisible tant qu'il n'est pas ajouté. Une
fois `git add -N` fait, le nom factice le fait échouer, et le vrai fichier
passe à zéro.

**L'application ne le charge pas.** Elle continue de lire
`data/horaire-2026.json`, qui ne porte que ce dont elle se sert — 700 Ko
contre 1,3 Mo. Celui-ci est une réserve : on y va chercher ce qu'on découvre
avoir besoin, sans redemander le classeur.

**À régénérer après chaque nouveau classeur**, juste après l'anonymiseur et
son second contrôle.

### Revérifier tout depuis le fichier complet

Le client, le 25/09/2026 : « il faut qu'à partir du fichier complet, tu
revérifies tout ».

```bash
python3 tools/verifier-integralite.py
```

Il confronte le classeur entier à ce que l'horaire porte. **La grille des
jours doit être à ZÉRO** — c'est la seule exigence dure, et le code de
retour la porte. **Depuis le 26/09/2026 elle se compare cellule par
cellule** : voir « L'audit du 26/09/2026 ». Ce qui suit décrit la première
version, par sous-chaîne, et reste vrai de la normalisation des
commentaires.

**LA COMPARAISON NAÏVE MENT, et elle a menti trois fois.** Les deux fichiers
ne passent pas par le même chemin : l'horaire sort du `.xlsm` par le
convertisseur, le brut sort du `.xlsx` par l'anonymiseur puis l'exporteur.
D'où trois écarts d'écriture, et **1 584 fausses pertes** avant qu'on les
comprenne :

| Ce qui diffère | Faux positifs |
|---|---|
| un ESPACE — l'un colle deux fragments que l'autre sépare | **1 099** |
| la TÊTE DE SIGNATURE — le brut garde `ABC:`, le convertisseur la retire | **473** |
| le jeton `(identifiant retiré)`, posé à deux moments différents | **12** |

On compare donc sur un texte réduit — minuscules, sans ponctuation, sans
tête de trigramme, sans mention de retrait. **Ce qui survit à cela manque
vraiment**, et il n'en restait que 167.

**Et le premier vrai reste était une fuite, dans le dépôt PUBLIC.**
`RT0xxxx` — un identifiant de connexion — vivait dans
`data/horaire-2026.json`. Ni l'anonymiseur ni son second contrôle ne
pouvaient le voir : ils cherchent des NOMS, et ce n'en est pas un. Le
convertisseur en avait retiré un le 23/09, mais seulement parce qu'il
ouvrait une SIGNATURE ; au fil du texte, il restait. **C'est la
confrontation des deux fichiers qui l'a montré**, en mettant les deux
versions du même commentaire côte à côte.

`LOGIN` vit donc dans le convertisseur, et l'exporteur l'emprunte : deux
copies d'un même motif divergent, et c'est toujours la seconde qui reste en
arrière. La doctrine qui veut que deux outils ne s'empruntent pas leurs
motifs vaut pour les NOMS, où la contradiction EST le contrôle ; un login
n'est pas un nom, et il n'y a rien à vérifier par recoupement.

**ET L'ORDRE S'EST REFERMÉ SUR MOI, MOT POUR MOT.** Posée avant
`AUTEUR.sub()`, la règle transformait le suffixe ordinaire d'une signature —
« Nom, Prénom/rt0xxxx: » — en « (identifiant retiré): », que le motif de
signature ne reconnaît plus : **324 commentaires ont porté ce reste** pendant
une version. C'est exactement ce que ce fichier décrit pour l'anonymiseur
depuis le 22/09 — *la signature se retire AVANT le remplacement*. Elle se
pose donc en dernier, quand les signatures sont déjà parties.

Après correction : **9 journées changent**, dont 8 sont les quatre prénoms à
re-remplacer comme toujours, et **une seule** est le login. Zéro jeton de
cette forme dans les deux fichiers.

**Ce que l'horaire ne porte pas encore, et qui attend une décision :**

- **81 commentaires du pied de feuille** (lignes 396 à 434) qui écrivent les
  **CP et TP contractuels avec leurs dates** — « CP 10% du 01.11.2022 au
  28.02.2026 », « 12 mois à 90% », « TP contractuel 10% du 16.05.2025 au
  15.06.2027 ». **C'est la « fraction payée » que l'application demande de
  saisir à la main**, et le classeur la porte, datée, pour chacun ;
- **74 commentaires de la feuille « Polyvalence »** : les dates
  d'acquisition et de suppression de chaque polyvalence — « supprimée àpd
  01/02/19 », « fin au 30/09/2026 » ;
- **6 copies d'un même commentaire de la grille**, qui ne sont pas une perte
  mais une CORRUPTION de la copie de référence : l'anonymiseur y a remplacé
  « Poly Arr » par « PAR ». **Corrigé le 26/09/2026, et c'était bien pire** :
  480 CELLULES et 8 commentaires, pas 6. Et la phrase qui était écrite ici —
  « le classeur emploie bien `PAR` comme abrégé » — était FAUSSE : la source
  écrit « P. arr » et « P.arr », jamais « PAR ». Voir « L'audit du
  26/09/2026 ».

### La fraction payée se lit dans le classeur

Le client, le 25/09/2026 : « il faut que toutes les données du fichier soient
récupérées pour alimenter l'app et les règles ».

Le pied de chaque feuille porte, **en commentaire**, le congé parental et le
temps partiel de chacun avec ses dates. **46 périodes chez 28 personnes**,
que personne ne lisait — et c'est la « fraction payée » que l'application
faisait saisir à la main.

> « CP 10% du 01.11.2022 au 28.02.2026 » · « TP contractuel 20% du
> 01.07.2025 au 30.06.2027 » · « CP 20% à partir du 01/11/2026 pour 5 mois »
> · « 12 mois à 90% »

**LE SENS DU POURCENTAGE NE SE DEVINE PAS — LE CLASSEUR LE DIT DEUX FOIS.**
Une personne porte « TP 10% du 15.03.2024 au 14.03.2026 … TP 20% à partir du
01/06 » et, trois lignes plus haut, « **90%** 01/01 au 14/03  **80%** 01/06 au
31/12 ». Une autre porte « CP 10% du 01/12/25 au 30/09/26 » et « **CP 90 %**
du 01/12/2025 au 30/09/2026 » — mêmes dates, deux notations. Dix pour cent de
RÉDUCTION valent quatre-vingt-dix pour cent PRESTÉS, et **ce sont les colonnes
du classeur qui se répondent**, pas une supposition.

D'où la borne : **au plus 30 = une réduction, au moins 70 = la part prestée**.
Le classeur n'écrit rien entre les deux — mesuré : 10 et 20 d'un côté, 80, 90
et 100 de l'autre. Ce qui tomberait entre serait gardé **sans** fraction
plutôt que deviné.

**Un commentaire peut porter DEUX périodes** — « CP 10% du 02.04.24 au
01.10.2026 CP 10% du 02.10.26 au 01.02.2030 » — et n'en lire qu'une ferait
croire que le contrat s'arrête. Le texte est donc découpé à chaque
pourcentage, et chaque morceau porte sa période. Trois commentaires en
portaient deux, un en portait quatre.

**Et le « du » manque une fois sur deux** : « CP 10% 01/03/26 au 30/06/2029 ».
Il est donc facultatif — **à condition qu'un « au » relie les deux dates**,
sans quoi la ligne des jours fériés non pris, « -01/01 -06/04 -01/05 »,
donnerait une période de janvier à avril.

**La fraction vaut pour un MOIS, pas pour l'année**, une même personne passant
de 90 % à 80 % en cours d'année. `fractionDuMois()` regarde **le 15** : un
mois appartient à la période qui couvre son milieu. Deux périodes qui se
recouvrent — le classeur écrit parfois la même sous deux notations — sont
départagées par la plus récemment commencée : c'est la dernière décision
écrite.

**Le réglage reste, en dernier recours**, pour qui n'est pas dans l'horaire.
Le classeur prime — c'est la règle de tête du projet, et **c'est déjà ainsi
que le statut ouvrier ou employé suit la personne** depuis le 22/09.

Vérifié au navigateur, dans les deux sens, sur quelqu'un dont le congé
parental commence le 01/09/2026 : **septembre 2 700 €, août 3 000 €** sur une
rémunération d'exemple de 3 000 — la fraction s'applique dans la période et
pas avant.

`tools/verifier-integralite.py` en tient compte : le pied de feuille passe de
**81 commentaires non repris à 16**, et les seize restants sont douze lignes
de jours fériés non pris, qui ne sont pas des contrats.

**`CT` est un crédit-temps**, confirmé par le client le 25/09/2026. Trois
personnes le portent — `CT 20%`, donc 0,80 — et **sans aucune date**.

### Trois dispositifs, une seule arithmétique — et une allocation hors fiche

Le client, le 25/09/2026, a décrit les trois réductions du temps de travail
du droit belge. Elles mènent au même 4/5 ou au même 9/10 et **font la même
arithmétique sur la fiche** : la rémunération fixe × la fraction, et la
journée non prestée n'ajoute rien. Relevé sur les onze fiches mensuelles :
« Heure(s) congé parent. » y est une QUANTITÉ, sans colonne en euros.

**Ce qui les sépare ne se voit PAS sur la fiche, et c'est le piège.** Le
crédit-temps et le congé parental ouvrent une allocation de l'ONEM — versée
par l'ONEM, absente de la fiche, donc **impossible à simuler ici**. Le temps
partiel n'ouvre rien. Quelqu'un en `CP` ou en `CT` reçoit plus que ce que
l'écran affiche, et rien ne le disait : les trois infobulles et le réglage
« Fraction payée » le nomment désormais.

**`CT` n'est PAS un congé de circonstance** — la légende des codes l'écrivait
ainsi. Le classeur le prouve seul : les **159 journées `CT`** sont chez
**trois personnes**, exactement les trois qui portent « CT 20% » en pied de
feuille, à **55, 53 et 51 journées** — une par semaine. Un congé de
circonstance se compte en jours par événement, jamais en cinquante. La ligne
s'appelle « Heure(s) crédit-temps » et a quitté, avec le congé parental, le
seau des heures « assimilées à du travail » : ces heures ne sont pas payées,
et l'infobulle disait le contraire.

**Le crédit-temps se prend en 1/5 ou en 1/2 ; le 9/10 n'en est pas un
régime.** `_dire_regimes()` le dit sur la sortie d'erreur, **sans rien
refuser** : un pourcentage hors régime est souvent une faute de frappe, mais
il peut être un régime qu'on ne connaît pas encore. Aujourd'hui elle ne dit
rien — les 33 contrats codés tombent tous juste.

**Cinquante pour cent entre dans la bande refusée, et c'est démontrable** :
un mi-temps s'écrira « 50% », et à cinquante l'ambiguïté n'existe pas — la
réduction et la part prestée donnent le même 0,50. **Cent avec un code reste
refusé** : suspension complète ou temps plein retrouvé, l'écart est tout le
socle du mois.

**La semaine de la maison fait 38:40**, pas les 38:00 des exemples du droit :
30 h 56 pour un 4/5, 34 h 48 pour un 9/10. Ne pas recopier les nombres d'un
exemple générique.

### Sans date, la période est écrite dans l'horaire

Le client, le 25/09/2026 : « si pas de date il faut prendre en compte celle
écrite dans l'horaire, mais ne pas deviner ».

**Et elle y est.** Les trois `CT 20%` portent **55, 53 et 51 journées codées
`CT`** dans leurs colonnes, étalées sur l'année. La période n'était pas
absente : elle était écrite ailleurs. `_borner()` prend donc la première et
la dernière de ces journées.

C'est le contraire d'une supposition : **on ne comble pas un trou, on va lire
la réponse là où le classeur l'a mise.** Et sans journée de ce code, rien
n'est posé — la fiche reste sans date et le réglage reprend la main.

**Le code doit être NOMMÉ dans la fiche.** « 12 mois à 90% » ne dit ni CP ni
TP : on ne saurait pas quelles journées regarder. Ces deux fiches-là restent
telles quelles — et elles doublent de toute façon un contrat daté chez les
deux personnes qui les portent.

**Cinq contrats sont ainsi bornés** : les trois crédits-temps, un `TP 10%
jusqu'au` dont la phrase s'arrête net, et un `CP 90% 10mois` sans dates.

### Et une date sans année est de l'année du fichier

« 90% 01/01 au 14/03 », « 80% 01/06 au 31/12 » : le jour et le mois, pas
l'année. Un classeur de 2026 qui écrit cela parle de 2026 — ce n'est pas une
supposition, c'est l'année du fichier.

**Le classeur se corrobore d'ailleurs lui-même** : cette fin du 14/03 est
exactement celle du contrat daté « TP 10% du 15.03.2024 au **14.03.2026** »
de la même personne, et le « 01/06 » celui de son « TP 20% à partir du
01/06 ». Les deux notations disent la même chose, comme pour le pourcentage.

Vérifié au navigateur sur un `CT 20%` : **2 400 €** sur une rémunération
d'exemple de 3 000, en août comme en septembre — sa période couvre l'année
entière.

### La feuille « Polyvalence » date chaque acquisition

Soixante-quatorze commentaires, posés **sur la croix** de chaque case, disent
depuis quand la polyvalence est acquise — et l'onglet Recyclage ne le disait
nulle part.

> « 31-01-2023 » · « 01/03/2026 » · « 19-10-17 » · « MDE: supprimée àpd
> 01/02/19 » · « fin polyvalence gluten le 31/08/18 » · « fin au 30/09/2026 »
> · « 16-07-2019 revalidé en 2023 »

**DEUX SENS, ET UN MOT LES SÉPARE.** Une date seule est une ACQUISITION ; la
même précédée de « fin » ou de « supprimée » est une PERTE. Se tromper
afficherait « acquise en 2019 » sur une polyvalence retirée depuis — pire que
de ne rien dire.

**La croix ne suffit pas à trancher.** Les trois polyvalences supprimées n'en
portent plus, mais « fin au 30/09/2026 » en garde une : elle n'est pas encore
terminée. **C'est le mot qui décide, pas la croix.**

**Une polyvalence PERDUE garde sa date alors que sa case est vide.** Les
dates vivent donc à part des ateliers : les ranger dans `ateliers` rendrait
la polyvalence à la personne, les taire perdrait la seule trace qu'elle a
existé. La case affiche toujours `·`, et son infobulle dit désormais
**« Polyvalence retirée le 01/02/2019 »** au lieu de « pas la polyvalence de
ce poste » — ce qui explique un point qu'on prenait pour une lacune.

**70 dates lues**, dont **6 fins**. Les quatre commentaires restants sont sur
des lignes que l'horaire ne rattache à personne, celles que le convertisseur
signale depuis toujours.

**Ce qui se voit** : l'infobulle de chaque case porte sa date, **48 dans la
grille**. Une polyvalence qui se termine reçoit un **soulignement rouge** —
pas un fond : les deux fonds de cette grille disent un ÉTAT (vert, le quota
est atteint ; jaune, la personne s'y forme), alors qu'une fin est un
ÉVÉNEMENT À VENIR et que la case **garde son chiffre**, puisqu'elle compte
encore. Le rouge est celui des ateliers, déjà validé dans les deux thèmes —
inventer une couleur l'aurait laissée hors de ce contrôle.

### La table des codes est dans les règles de paie

`docs/regles-paie.md`, section « **Les codes, leur sens et ce qu'ils
paient** » : chaque code, sa signification, sa ligne de fiche, s'il est payé,
et d'où on le sait. **À relire avant de toucher à `ABS[]` ou à la légende de
l'onglet « Mon horaire »** — les deux doivent dire la même chose, et elles se
sont contredites TROIS fois, toujours de la même façon : un libellé qui
décrit autre chose que ce que le code fait.

- `ABS` rangé dans « non payé » avec « absence injustifiée », alors que le
  chemin du classeur le traduit en `SMG` et le paie ;
- `CT` donné pour un « congé de circonstance » quand c'est un crédit-temps ;
- `CT` et `CP` rangés parmi les heures « payées comme des heures prestées »,
  alors que la fraction les a déjà retirées de la rémunération fixe.

D'où un bloc de légende à eux, « **Temps de travail réduit** », où `CP`, `CT`
et `TP` se lisent ensemble avec la phrase qui vaut pour les trois : le jour
ne se paie pas, la réduction est déjà dans la rémunération fixe, et
l'allocation de l'ONEM — pour le congé parental et le crédit-temps
seulement — se verse hors fiche.

**`ABS` dit deux choses selon qui l'écrit** : le classeur, c'est une maladie
payée ; posé à la main dans le mois, c'est une absence non rémunérée. La
légende le dit maintenant.

**`SMG` N'EST PAS UN MOT DE LA MAISON.** Le client ne le connaissait pas et a
demandé ce que c'était — parce que je l'avais posé à côté de ses phrases
comme s'il en venait. Il vient de **la fiche de paie** : « Heure(s) SMG
maladie », *salaire mensuel garanti*. L'application a repris l'intitulé du
secrétariat social pour que l'onglet Contrôle se lise ligne à ligne contre la
fiche. La légende l'écrit désormais en toutes lettres, avec sa provenance.

**Et « Abs » avec « remplace X » n'est PAS une contradiction.** 562 des 1 848
journées `Abs` portent un commentaire qui parle d'un remplacement — de quoi
croire la lecture fausse, et j'ai ouvert ce doute. Le client, le 25/09/2026 :
**« toujours 1 »**, c'est-à-dire toujours une absence. Le classeur le prouve
seul : **45 de ces commentaires disent LES DEUX** — « remplace GPS remplacé
par JBI? et YPE ». On ne remplace pas quelqu'un et on n'est pas remplacé le
même jour au même poste. C'est la règle de tête du projet : le code franc est
la journée PRÉVUE, l'annotation dit ce qui s'est passé. **Il n'y avait rien à
corriger** — et c'est écrit pour que le doute ne se rouvre pas.

### Une polyvalence qui se termine cesse de compter le lendemain

Le client, le 25/09/2026, interrogé sur les deux polyvalences que le classeur
donne comme finissant le 30/09 : « **oui il perd sa polyvalence** ».

La date était LUE mais pas APPLIQUÉE : elle s'affichait, et la case
continuait de compter. Le 1er octobre, l'application aurait donc cru que
cette personne savait encore tenir la meunerie et le gluten — **et le
rééquilibrage l'y aurait envoyée boucher un trou qu'elle ne sait plus
tenir**. Le poste se serait affiché COMPLET alors qu'il manque quelqu'un. Un
manque annoncé à tort est pire qu'un manque qu'on n'annonce pas.

`polyFinie()` s'intercale donc dans `aLAtelier()`, qui est le seul point de
passage de « sait-elle tenir ce poste » — la grille du Recyclage, la
composition, le tableau du jour et le rééquilibrage y passent tous.

**La date est INCLUSE** : le 30/09 la polyvalence compte encore, le 1er
octobre elle ne compte plus. Vérifié au navigateur, horloge déplacée aux
trois dates.

**LE JOUR CALCULÉ, ET NON L'HORLOGE** — même règle et même piège que
`POSTE_PERIODE`. Sans lui, une polyvalence terminée hier vaudrait encore pour
tout novembre dans la liste des manques. `postesDePause()` calcule le jour
une fois et le passe à la chaîne des postes ET au rééquilibrage ; la
composition et la grille n'ont pas de date et se lisent sur aujourd'hui, ce
qui est exactement ce qu'elles montrent.

**Ce que cela déplace : rien, et c'est mesuré.** Manques inchangés — 189
journées et 385 places sur l'année, 8 et 8 d'ici la fin de l'année —,
couples de polyvalence 33 au quota sur 99, neuf règles à zéro, compteurs
76/77. Ces deux polyvalences-là ne servaient à combler aucun trou d'octobre
à décembre.

**D'où une épreuve, parce qu'un chiffre inchangé ne prouve rien.** En
terminant le gluten au 01/01 pour les 31 personnes qui l'ont, les manques de
gluten passent de 50 à **279** et les places creuses de 385 à 611. Le
mécanisme mord ; il n'avait simplement rien à mordre ici.

**La case vide sait déjà le dire** : son infobulle passe de « se termine le
30/09/2026 » à « **Polyvalence retirée le 30/09/2026** », le soulignement
rouge disparaît et la ligne « Se termine » sous la grille se vide. Rien n'a
été écrit pour cela — c'est la règle du 25/09 sur les polyvalences perdues
qui reprend la main d'elle-même.

**Et elle s'écrit en toutes lettres sous la grille** : « Se termine : PAM ·
Meun. le 30/09/2026 · PAM · Glut. le 30/09/2026 ». Un trait dit qu'il se
passe quelque chose ; il ne dit pas QUAND, et c'est la date qui compte quand
il reste cinq jours. La ligne et l'entrée de légende n'apparaissent **que
les jours où la grille en porte une**, comme le veut la règle du 22/09.

Vérifié au navigateur à 390 et 1280 px : 48 infobulles datées, 2 cases
soulignées, la ligne nommant les deux polyvalences qui se terminent, aucune
erreur.

## L'audit du 26/09/2026

Le client, le 26/09/2026, en envoyant un nouveau récapitulatif : « fais un
check complet multiagent sur la manière de récupérer toutes les infos de ce
fichier et de le rendre anonyme ». Cinq auditeurs indépendants —
anonymat, extraction, usage par l'application, méthode, contrôles — chacun
suivi d'un sceptique chargé de réfuter ses constats en les remesurant.

**Le nouveau classeur est le même que celui du 25/09 à 15 h 23**, texte pour
texte : la conversion ne change que les huit journées aux quatre prénoms.

### L'anonymiseur corrompait la copie de référence, de trois façons

Aucun nom n'y survivait — la chasse indépendante l'a confirmé sur 168 mots
tirés de la source. Mais la copie **n'était pas fidèle**, et elle **n'était
pas propre** :

| Défaut | Mesuré | Cause |
|---|---|---|
| « Arr » devenu « PAR » | **480 cellules**, 8 commentaires | la ligne 10 de la feuille cachée « Récapitulatif (1) » porte « P. arr » trois fois : trois cellules suffisaient à en faire une ligne de noms |
| le barré déplacé | 621 commentaires mêlant barré et non barré dans la source, **41** dans la copie | le retrait de la signature recollait tout le texte dans le PREMIER morceau — la signature, souvent barrée — et vidait les autres |
| des mots collés | **environ 350** commentaires, « ATAremplace » | AUTEUR emportait le saut de ligne qui précède une seconde signature |
| identifiants de connexion | **60** dans le fichier public | AUTEUR travaille sur les octets du XML et exige un blanc devant ; un login en tête d'un morceau suit un « > » |
| étiquette « Confidential » de l'employeur, identifiant de son annuaire, chemin réseau | docProps/custom.xml, x15ac:absPath | recopiés tels quels |
| un paquet qui annonce des macros | 13 relations vers des parties absentes | le retrait du `vbaProject.bin` ne nettoyait rien autour |

Tout est corrigé dans `tools/anonymiser-classeur.py`, et **chaque correction
est mesurée contre la source** :

- **hors des zones nominatives, plus UNE cellule ne diffère de la source** —
  les 301 écarts sont tous en ligne 10 des feuilles de personnes, dans
  « Personnel » et dans les colonnes nom et prénom de « Polyvalence » ;
  l'ancienne copie en corrompait 480 de plus ;
- **10 457 commentaires dont le texte est intact ont leur barré identique,
  caractère par caractère** ; les 1 107 autres ont perdu un nom ou un login,
  et trois seulement ont perdu un saut de ligne — celui d'une signature
  posée seule sur sa ligne, qui part avec elle ;
- **0 identifiant de connexion** (191 retirés, dont les 60 qui passaient),
  **6 collages** — ceux que la source porte elle-même ;
- le paquet s'ouvre : **0 relation pendante**, le type « classeur » et non
  « classeur à macros ».

**La ligne des noms ne se lit plus que dans les feuilles de personnes**
(`FEUILLES` du convertisseur), et **sans seuil** : la feuille Step n'a que
deux personnes, et le seuil de trois la laissait de côté.

**Le retrait se fait morceau par morceau** : `_editer_morceaux()` applique
les coupes au texte recollé sans déplacer un caractère d'un morceau à
l'autre. C'est ce qui garde le barré à sa place — et **le barré porte une
information** : voir plus bas.

**Les deux contrôles ne voyaient pas les identifiants de connexion**, et
c'est pour cela qu'ils ont vécu dans un dépôt public :

- `verifier-anonymat.py` les rangeait explicitement parmi les signatures
  ANONYMES. Il les cherche désormais dans le texte, avec son propre motif ;
- `verifier-depot.py` répondait « aucune forme de nom ». Il a une règle à
  eux, qui écarte les couleurs et les identifiants de commit — deux lettres
  de A à F — et ne lit, dans un classeur, que le texte des cellules et des
  commentaires.

**Et ce fichier-ci en écrivait un en toutes lettres**, pour illustrer un
motif — comme les neuf noms cités en exemple avant lui. Il s'écrit désormais
`RT0xxxx`, dans `CLAUDE.md` et dans quatre outils.

**`verifier-anonymat.py` sortait TOUJOURS en 1** — « CPPT », « STEP » ou « PRODUCTION »
ont la forme d'un nom — et un contrôle qui échoue toujours ne se lit plus.
`tools/survivants-admis.txt` porte les chaînes déjà lues, avec leur raison ;
l'outil sort en 0 quand il ne reste qu'elles. **Y ajouter une ligne est un
acte**, comme pour `tools/formes-admises.txt`.

### Le convertisseur apprend les prénoms, et se relit

Les quatre prénoms qu'on retirait à la main à chaque conversion **sont dans
la colonne Prénom de « Polyvalence »**, chacun sur une ligne dont le
trigramme est celui qu'on posait. `_motif_registre()` apprend donc aussi le
nom et le prénom de cette feuille, avec le trigramme de leur ligne — celui
que `polyvalence()` calcule, `CORRECTIONS` et « Personnel » compris.

- **un prénom n'est appris que s'il est UNIQUE dans la colonne** : partagé,
  on ne saurait quel trigramme écrire ;
- **accents et casse ne comptent pas, sauf la majuscule initiale** : l'un des
  quatre n'est pas écrit pareil dans la feuille et dans le commentaire, et
  une comparaison exacte le laissait passer ;
- **une garantie relit TOUT le JSON produit** — journées, champ `e`,
  contrats, dates de polyvalence — et y cherche chaque mot de nom des
  feuilles de personnes et de « Polyvalence », qu'on ait su l'attribuer ou
  non. Un seul reste, et rien n'est écrit (code 2, `--tolerer=` après avoir
  lu le contexte). C'est la doctrine de l'anonymiseur ; le convertisseur ne
  l'avait pas.

**L'étape manuelle disparaît, et elle se trompait une fois sur quatre.** La
conversion du nouveau classeur donne l'horaire installé à DEUX journées
près : GST les 25 et 26/02, « Remplacé par CDE (<prénom>) ». La main avait
écrit CDE ; le calcul écrit **CHD**. Le classeur tranche seul : ces deux
jours-là, **la colonne de CHD porte « Remplace GST », et CDE est en
repos**. CHD est « l'autre CDE, en équipe 4 » de `CORRECTIONS` — le
classeur l'appelle encore par ses initiales, le client l'a renommé. Le
prénom est le sien.

**L'anonymiseur faisait la même erreur**, pour la même raison : il
calculait les initiales du couple nom-prénom sans consulter `CORRECTIONS`.
`_ini_de_ligne()` le fait désormais — **pour le prénom seul**. Le nom de
famille garde ses initiales : il est souvent partagé, et le faire suivre a
changé, à l'essai, **460 signatures d'un auteur** en celles d'un homonyme de
la même feuille. Trois prénoms suivent ainsi une décision du client (CHD,
JBA, PDF), deux commentaires concordent désormais avec l'horaire, et
`verifier-integralite.py` repasse à zéro.

Rien d'autre ne bouge : les quatre sorties de `verifier-calendrier.js` sont
identiques à l'octet, et `comparer-fiches` passe son épreuve.

### L'export recopie maintenant TOUT le classeur

`tools/exporter-classeur.py` ne gardait que le texte des cellules, celui des
commentaires et les fusions. L'audit a mesuré ce qui tombait, et c'était
beaucoup : **le type** des valeurs (la date de mise à jour sortait en
« 46290.64 »), **13 637 formules**, **toute la mise en forme** — dont le
**barré** —, 262 lignes et 62 colonnes masquées, deux feuilles cachées, les
validations, 302 règles de mise en forme conditionnelle, 13 noms définis et
25 boutons avec leur macro.

Tout y est désormais — le format est décrit en tête de l'outil. Deux choix
à connaître :

- **les commentaires se lisent dans le XML, tels qu'ils sont écrits.** L'outil
  passait par la lecture du convertisseur, qui les NETTOIE : têtes retirées,
  sauts de ligne écrasés. « Cet outil ne lit rien, il recopie », disait ce
  fichier — c'était faux pour les commentaires. Leurs morceaux barrés,
  soulignés ou en italique sont dans `riches` ;
- **seule la mise en forme qui peut porter un sens** est gardée : fond,
  couleur et style de l'écriture, format des nombres. Pas les bordures ni
  l'alignement, qui doubleraient le fichier.

**Un aller-retour le prouve à chaque export** : l'outil recompte dans le XML,
par des motifs et non par l'arbre qu'il vient de parcourir, les formules,
les cellules peintes et barrées, les commentaires et ceux qui ont un morceau
barré. Un écart, et rien n'est écrit. Éprouvé : cinq sabotages — une
formule, un commentaire, un morceau barré, une suite de cellules barrées,
une cellule peinte en moins — sont tous détectés.

**L'export est reproductible** : la date inscrite est celle du classeur, et
non l'heure de l'export. Deux exports du même fichier sont identiques à
l'octet.

**4,0 Mo au lieu de 1,3** — 571 Ko compressés, ce que git stocke. Les formules
de « Récapitulatif (1) » en font 1,5. L'application ne le charge pas.

### L'intégralité se vérifie cellule par cellule

`tools/verifier-integralite.py` versait les commentaires dans un SAC et
cherchait chacun n'importe où dedans. Il ne regardait pas les valeurs des
cellules, un commentaire posé sur le mauvais jour passait, et un commentaire
court — « rappel », « remplace » — se retrouvait toujours quelque part. **Il
voyait 6 écarts là où 256 cellules et annotations étaient corrompues.**

Il compare désormais **chaque journée de chaque colonne-personne** du brut à
l'horaire — cellule, annotation, commentaire —, après avoir retrouvé la
personne par **l'accord de leurs journées** et non par le trigramme, que
`CORRECTIONS` et les suffixes font diverger. Une colonne que personne ne
reconnaît échoue ; **deux copies d'une même personne qui divergent entre
feuilles échouent** (les adjoints sont recopiés sur cinq feuilles) ; un
identifiant de connexion dans l'un des deux fichiers échoue.

Mesuré sur le classeur du 25/09 : **102 colonnes reconnues sur 102, 27 554
journées identiques**, 20 cellules vides devenues repos — la règle du
convertisseur —, **0 écart**. Éprouvé par six sabotages, tous détectés : un
commentaire décalé d'un jour, un commentaire court supprimé, une cellule
changée, une journée supprimée, une des cinq copies d'un adjoint corrompue,
un login planté.

**Les deux jointures d'une journée sont acceptées, et rien d'autre** : le
convertisseur joint le commentaire de la cellule et celui de l'annotation,
et ne garde que le plus complet quand l'un contient l'autre — casse
comprise. « Rappel 19/1 » n'est pas contenu dans « RAPPEL 19/1 », et il
garde les deux. Le contrôle, qui compare sur un texte en minuscules, doit
accepter l'un et l'autre.

**Le pied de feuille et « Polyvalence » ne font pas échouer**, et le second
était faux : il comptait 74 commentaires « non repris » en oubliant les 70
dates de polyvalence que l'horaire porte. Il en reste **2** — deux lignes que
l'horaire ne rattache à personne.

### Ce que l'application reçoit de plus

- **La légende entière** : onze codes au lieu de quatre. Elle ne lisait que
  les colonnes A et B de la première feuille ; les sept autres — `xxx`, `R`,
  `Abs` · `DS` · `CP` · `CSS` · `R-CM` — sont écrits au-dessus des
  colonnes-personnes et **partaient dans le champ `e` de 29 personnes**,
  affiché sous leur nom dans l'annuaire comme s'il les concernait. Les
  lignes 1 à 8 ne portent que la légende et la date de mise à jour —
  mesuré sur les 102 colonnes —, et `e` ne les lit plus. Les libellés des
  compteurs suivent la légende, comme ils le faisaient déjà pour les quatre
  premiers codes : « CP » s'y lit « Congé Parental ».
- **Le statut de « Polyvalence »** (`poly.statut`) : « interim », « Adj CM »,
  « Assistant usine ». Jamais le matricule. Rien n'en est tiré.
- **Le bloc « Temps de travail réduit » de l'onglet Compteurs** : il ne
  montrait que le congé parental — les huit personnes en temps partiel et les
  trois en crédit-temps avaient leurs compteurs dans le classeur et rien à
  l'écran — et ne lisait « à planifier » que sous une des deux écritures du
  classeur, si bien que onze personnes sur seize ne le voyaient pas.
  Vérifié au navigateur sur LCI, SBZ, VBN et ATA.
- **Les colonnes sans nom sont annoncées** : Shift1 AG et Shift4 Q portent
  une année de journées sans rien en ligne 10. **J'ai écrit que c'étaient des
  copies de travail de DWS et de CHD, et c'était faux** — leurs cellules
  franches coïncident, rien de plus. Le client, le 26/09/2026 : « Shift 1 AG,
  c'est le troisième chaudiériste de l'équipe 1, mais avec les transferts
  d'équipe actuels il n'y a plus personne pour le moment ; Shift 4 Q, c'est
  l'opérateur fermentation de l'équipe 4, modifié aussi récemment ». Ce sont
  des **places sans titulaire** : la colonne porte la rotation du poste, pas
  une personne. Le convertisseur les DIT sur sa sortie d'erreur sans les
  rattacher à personne, et c'est juste — une place qui se remplit s'y verra
  en premier, un nom apparaissant en ligne 10.

Rien d'autre ne bouge : champ `e` chez 29 personnes, `poly` chez 21, la
légende — et aucune journée. Les quatre sorties de `verifier-calendrier.js`
sont identiques, l'intégralité reste à zéro.

### Un commentaire barré ne compte plus

Le client, le 26/09/2026 : « un commentaire barré est un commentaire qui
n'est plus à prendre en compte ». Règle et raisons dans
`docs/conversion-horaire.md`, « Ce qui est barré ne compte plus ».

**La première version s'est trompée d'ordre**, encore : retirer le barré
AVANT le nettoyage a fait échouer l'intégralité sur deux journées — un
trigramme collé à la signature qui suivait le morceau rayé, et une
initiale orpheline, Excel ayant coupé une signature en un morceau barré et
un morceau qui ne l'est pas. `_TexteBarre` porte le barré caractère par
caractère à travers le nettoyage, et le retire à la fin. **Rejouée avec
tous les drapeaux à faux, la nouvelle chaîne reproduit l'ancien horaire à
l'octet** : c'est la preuve que la refonte ne change que le barré.

`verifier-integralite.py` retire le barré du brut de son côté, par les
`riches` de l'export — sa propre lecture, pas celle du convertisseur.

Mesuré sur le classeur du 26/09/2026 :

- **496 journées chez 59 personnes** perdent tout ou partie d'un
  commentaire ; aucune cellule, aucune annotation ne bouge ;
- **sept touchent à l'argent** : un rappel retiré (DBE 06/02), quatre
  « maintien prime » retirés (YBT 14/01, BLR 04/10, CGI 01 et 02/04) ;
- **FLN** : son temps partiel finit au **30/09/2026** — la fin de 2027
  était rayée — et la fraction retombe sur le réglage à partir d'octobre ;
- polyvalence **33 → 32** couples au quota (JBI meunerie 5/5 → 4/5 : son
  « remplace SKS en AM » du 14/01 est rayé), manques de l'année **385 →
  386** places ; `--manques 0926` et `--compteurs` identiques ; neuf règles
  à zéro ; motifs trop étroits 50 → 48 ;
- deux formes innocentes admises dans `tools/formes-admises.txt`, nées du
  retrait d'un morceau rayé entre deux mots.

**Une ligne ENTIÈREMENT barrée, elle, vaut comme si elle ne l'était pas.**
Le client, le 26/09/2026 : « c'est une erreur de manipulation du RH, ne pas
prendre en compte les lignes entièrement barrées ». Deux lignes le sont : le
02/03 (ligne 71) et le 14/05 (ligne 144), sur les cinq Shift et
« Contremaître », de 25 à 39 cellules chacune, avec de vraies prestations
dessous. Le barré d'une CELLULE n'a jamais été lu — seul celui des
commentaires l'est —, et **aucun des 52 commentaires de ces deux lignes ne
porte de morceau barré** : la règle précédente ne leur a rien retiré. Rien à
changer dans le code ni dans `data/`, et la distinction est à garder : le
barré d'un commentaire est une décision, celui d'une ligne un accident.

### Le jaune d'une journée est un pense-bête

Le client, le 26/09/2026, sur les trois « Abs » de GSK surlignées les 16, 19
et 20/01 : « ce sont des jours où il remplaçait, mais le commentaire a été
barré ; à mon avis c'était mis en jaune pour ne pas oublier de trouver un
remplaçant à celui qu'il était censé remplacer ».

**Le classeur le confirme de lui-même** : les trois commentaires sont
« ~~remplace CGI~~ », entièrement barrés, et ces trois jours-là la colonne de
CGI porte « remplacé par LDY » puis « remplacé par ATR » — le remplaçant a
été trouvé. Les quatre autres « Abs » de la série (14, 15, 17, 18/01) ne
sont pas jaunes : ce jour-là GSK ne remplaçait personne.

**Rien à lire ni à coder** : le jaune ne porte ni heure ni montant, et la
journée reste une maladie. La règle du barré du 26/09 avait déjà retiré
« remplace CGI » des trois journées ; avant elle, l'horaire faisait croire
que GSK remplaçait quelqu'un un jour où il était malade.

**Le gris des colonnes de SKS ne veut rien dire non plus.** Grisées sur
« Opérateurs » du 02/01 au 12/06, elles tombaient pile sur ses 112 journées
en meunerie — une coïncidence qui ressemblait à une preuve. Le client, le
26/09/2026 : « cela ne correspond à rien, sûrement une ancienne zone d'un
autre opérateur, car SKS a pris sa place dans l'horaire de la page
Opérateurs ». **Une mise en forme survit à celui pour qui elle a été posée** :
une colonne réattribuée garde les couleurs de son ancien occupant. SKS est
en formation en meunerie — depuis le 21/09 seulement, voir plus bas.

### Une formation commence à une date

Le client, le 26/09/2026, dans la foulée : « il a commencé en meunerie le
21/09 ». La feuille range SKS parmi les opérateurs en formation, « Meunerie »
en ligne 9, pour toute l'année ; ses commentaires ne nomment la meunerie
qu'à partir du 21/09, et sa polyvalence le déclare validé en fermentation,
distillation et chaudières. `FORMATION_DEBUT` porte la date : avant elle,
`enFormation()` rend faux et `posteTenu()` ne lit ni la ligne 9 ni `e`.

Mesuré : neuf règles, compteurs et `--manques 0926` **identiques à
l'octet** ; manques de l'année **386 → 362** places, 189 → 177 journées ;
SKS **« à déterminer » 31 journées** et déduit de sa polyvalence 67 fois ;
son recyclage passe de « Chaudières 10/10 » à Terrain arrière 32, Distillation
20, Chaudières 13, Fermentation 11 — **34** couples au quota au lieu de 32.
Vérifié au navigateur, hors ligne compris.

**Son poste d'avant : polyvalent arrière de l'équipe 5.** Le client, le
26/09/2026 : « il était polyvalent arrière dans l'équipe 5 avant cela ; il a
été sorti de l'horaire d'équipe pour sa formation meunerie ». Il entre donc
dans `POSTE_PERIODE` — terrain arrière jusqu'au 20/09 —, la seconde tranche
de la table après LCI.

**Et le Recyclage lisait « son poste » sur aujourd'hui**, ce qui ne tient plus
dès qu'on change de poste à une date : en formation aujourd'hui, SKS n'a pas
de poste à lui, et ses journées au terrain arrière d'avant le 21/09
comptaient comme du recyclage — **103/10**, un quota atteint dix fois sur le
poste qu'il tenait tous les jours. `posteAttitreLe(p, jour)` rend le poste
attitré CE jour-là, et `calculerPolyvalence()` n'y compte pas une journée à ce
poste. **Rejoué sans cette règle, seul SKS change** : elle ne touche
personne d'autre, puisque personne d'autre ne change de poste avant
aujourd'hui.

Mesuré, depuis l'état d'avant le 21/09 : neuf règles, compteurs et
`--manques 0926` **identiques à l'octet** ; manques de l'année **386 → 358**
places, 189 → 177 journées, **plus aucun « à déterminer »** ; SKS
« Chaudières 10/10 ✓, Distillation 4, Fermentation 2, Terrain arrière 0,
Meunerie F » ; **31** couples au quota au lieu de 32 — ceux qui tenaient le
terrain arrière à sa place y comptent moins (PLZ 16 → 9, CDE 8 → 3, SMA
30 → 28). Vérifié au navigateur, hors ligne compris.

Le découpage du vérificateur prend désormais `POSTE_PERIODE` jusqu'à
`] };` : la table tient sur plusieurs lignes, et la découpe au premier saut
de ligne rendait une `SyntaxError`.

### Le terrain arrière ne se recycle pas

Le client, le 26/09/2026, en voyant « Terrain arrière 0/10 » sur la ligne de
SKS : « terrain arrière ne doit pas compter de recyclage », puis, la question
posée entre SKS seul et tout le monde : « ce poste ne compte pas pour un
recyclage, c'est fermentation/distillation ».

Ce n'est pas un atelier, c'est la réunion de deux — aucune liste de
polyvalence ne le porte, `tientTerrainArriere()` le déduit. `PV_SANS_RECYCLAGE`
le sort de `polyvalenceDe()` et de la grille, et une journée passée au terrain
arrière **ne compte nulle part** : la reverser à la fermentation ET à la
distillation était l'autre lecture possible, et le client ne l'a pas
demandée. Si c'était son intention, c'est `calculerPolyvalence()` qu'il
faudrait toucher.

Mesuré : **seule la colonne part** — aucune autre case ne bouge, neuf
règles, compteurs et manques identiques à l'octet. Couples au quota
**31 → 23** sur **99 → 86** : les huit quotas de terrain arrière (ATR, FPA,
GDT, GPO, JBI, PAM, SMA, VGG). La grille a six colonnes au navigateur :
Meun., Glut., Ferm., Dist., Chaud., STEP. Le polyvalent arrière dont c'est le
poste perd son point plein — il n'y a plus de colonne pour le porter.

### Entre les deux arrêts, aucun effectif n'est exigé

Le client, le 26/09/2026, sur les fenêtres « SHUT-DOWN » que le classeur
surligne en jaune dans la colonne des jours — du 16 au 23/03 et du 10 au
18/04 : « l'effectif ne devait pas être respecté car il n'y avait souvent
que 2-3 personnes en pause de nuit ».

**Je l'ai d'abord appliqué à l'envers**, en exemptant les deux fenêtres
elles-mêmes — et c'est poussé ainsi pendant un commit. Le client, en
réponse à la question qui suivait : « les périodes avec les cellules à
droite de celle en jaune dans la colonne A devaient respecter les
effectifs, les autres entre non ». Les fenêtres jaunes sont tenues ; ce sont
les jours **entre** elles qui ne le sont pas.

`SANS_EFFECTIF` porte donc **du 24/03 au 09/04** : exactement les jours dont
les nuits sont vides, l'équipe de nuit passée en jour avec « maintien
prime N ». Avant la première fenêtre (09-15/03) et après la seconde (19/04),
les manques sont ceux d'une semaine ordinaire — mesuré sans aucune
exemption. `renfortDuJour()`, déjà le point où une journée ajuste ce qu'on
attend d'elle, rend `{_libre:true}`, et `attenduAuPoste()` rend zéro.

Mesuré : neuf règles, compteurs et `--manques 0926` identiques à l'octet ;
manques de l'année **358 → 247** places, 177 → 160 journées. Le Recyclage
bouge un peu, pour la raison attendue — sans effectif exigé, le rééquilibrage
ne PLACE plus personne pendant ces jours-là, et seules comptent les journées
que la cellule écrit : CDE chaudières 12 → 10, HKB meunerie 26 → 23, GST
fermentation 13 → 11 ; **23 couples au quota, inchangé**.

La nuit du 23/03, dernier jour de la première fenêtre, reste en manque sur
six postes : c'est la règle du client, la fenêtre se tient.

### Les fiches d'un ouvrier, et les grèves écrites « Abs »

Le client, le 26/09/2026, a transmis les fiches de LCI, ouvrier. Tout ce
qu'elles ont appris est dans `docs/regles-paie.md`, « La fiche d'ouvrier ».
`comparer-fiches.py` lit leur format et leur **détail jour par jour** :
214 journées confrontées, 202 identiques d'emblée.

**Trois « Abs » étaient des grèves** — « Grève reconnue » sur la fiche, et
l'usine le montrait seule : 15, 14 et 11 « Abs » ces jours-là contre 4 les
lendemains. Le client : « c'est bien grève, l'employeur ne paye rien ».
`GREVE_JOURS` fait de tout « Abs » du 10/02, du 12/05 et du 16/06 un code
`GREVE` (étiquette « GREV »), avec sa ligne de fiche et son entrée de
légende. Neuf règles, manques, Recyclage et compteurs **identiques à
l'octet** — maladie et grève sont toutes deux des absences —, 205 journées
sur 214 identiques aux fiches, et la maladie concorde désormais les quatre
mois où elle apparaît. Vérifié au navigateur sur LCI.

**Ce que cela ne fait pas** : retirer la journée du salaire. La rémunération
de l'application est FIXE ; une journée non payée — grève, sans solde,
absence injustifiée — y apparaît en heures sans rien ôter. Limite
antérieure, écrite dans `docs/regles-paie.md`.

### Une reprise partielle sort de la prime d'équipe

Le client, le 26/09/2026, devant la fiche de LCI du 17/06 —
`["DS-CE","1h rhs"]`, 7 h de nuit et 1 h de « Compensation payée » : les
heures reprises se paient sans prime. Règle et mesures dans
`docs/regles-paie.md`, « RHS ».

**Posée d'abord dans `parseHoraireEntry()`, elle n'a rien changé** : la
cellule de LCI ne nomme pas de poste, c'est le cycle qui le donne, dans
`lireJournee()`. Elle vit donc à la fin de celle-ci. **Et la première
version retranchait deux fois** : DWS le 25/03, `["8h-12h","4h rhs"]`,
tombait à zéro heure alors que sa plage dit déjà sa présence. Les heures
prestées valent au plus 8 − n.

178 journées chez 53 personnes, 377,5 h ; neuf règles, manques et compteurs
identiques à l'octet ; FPS gluten 9 → 8 au Recyclage ; `comparer-fiches` LCI
207 journées sur 214. Vérifié au navigateur sur juin, hors ligne compris.

### « PM · DS-CE » : quatre heures sans prime, « AM · DS-CE » : huit avec

Le client, le 26/09/2026. **La règle proposée d'abord — la même pour toute
cellule « poste + DS-CE » — aurait été fausse** : la fiche de LCI paie le
18/02 `AM · DS-CE` en journée pleine, le 25/08 `PM · DS-CE` en 4 h + 4 h. La
question posée avec les deux fiches côte à côte a donné la réponse. Détail
dans `docs/regles-paie.md`, « Le conseil d'entreprise d'un après-midi ».
Cinq journées, tout identique à l'octet sauf elles ; LCI 208 journées sur
214. La nuit est tranchée le 30/09/2026 : les heures prestées gardent la
prime que le commentaire écrit (celle de la pause prévue sinon), ce que
l'application faisait déjà.

### Un déplacement demandé garde la prime la plus élevée

Le client, le 26/09/2026, devant son relevé de pointage d'août : les 19 et
20/08 il a remplacé en AM sur une journée prévue PM, et garde la prime PM ;
le 30/08, même cellule, c'était un « échange » écrit dans la colonne du
COLLÈGUE, et il est payé AM. Règle : la prime la plus élevée entre la pause
faite et la pause prévue (cycle recalé), sauf échange. Détail et mesures
dans `docs/regles-paie.md`. **16 journées**, tout le reste identique à
l'octet ; 13 des 33 journées de cette forme disaient déjà « maintien
prime » — le classeur confirme la règle de lui-même.

**Un relevé de pointage** (« Sommaire mensuel ») vaut une fiche jour par
jour : horaire prévu (1A40 matin, 2A40 après-midi, 3A40 nuit), prime payée
(P11/P12/P13, P3x le samedi, P5x le dimanche), pointage IN/OUT. Il porte le
nom et le matricule : **il ne rentre pas dans le dépôt**, comme les fiches.

### Un rappel sur un repos se paie en heures sup

Le client, le 26/09/2026 : « la règle est la même pour tout le monde ». La
fiche de LCI le 11/04, `["-","N","rappel le 07.04"]` : aucune heure
normale, 8 h d'heures sup à compenser à 187,5 % et leur déduction, prime de
nuit majorée, repos payé. C'est sa règle du 25/09 — pas de « +FT » écrit,
donc le compteur d'heures sup.

`lireJournee()` pose `r.rs` et un code `nH HS` (9 à 12 h ajoutés au
barème) ; la journée garde poste et heures, si bien que placement, manques,
Recyclage et compteurs sont **identiques à l'octet** — seule la paie
change, dans `compute()`. **122 journées chez 46 personnes** ; écartées à
raison : six « +FT », et SPS le 17/04 dont la plage fait 9 h 30.

**Je l'ai d'abord mal demandé** : « j'attends ton ok pour appliquer la
lecture de la fiche » — le client n'a pas compris quoi ni pourquoi. La
question qui a marché montrait UNE journée, ce que l'application fait, ce
que la fiche porte, et « oui / non ». Toujours cette forme.

LCI le 13/04, `["N","22h-10h","Rappel…"]`, reste un écart : sa cellule
franche dit N, pas repos, alors que la fiche le paie en 12 h d'heures sup.

### Les mentions non comprises, lues par leur commentaire

Le 26/09/2026, en appliquant la règle « commentaires d'abord » : sur onze
mentions non comprises, **neuf** se sont résolues sans question. Sept se
lisaient déjà juste (`MENTIONS_NEUTRES` : `CPPT-F`, `SD26+R`, `R-CM/VM`,
`chaud. + F`, `R + F`, `+CPPT`) ou étaient un atelier (`liq - ferm`,
fermentation liquide) ; une était FAUSSE — JKS le 17/06, `DS + PM ·
4h +FT`, « réunion mensuelle Direction - délégation syndicale », comptait
4 h au lieu de 8 : le « PM » n'était pas lu, et la règle du +FT sur un
poste prévu ne s'appliquait pas (`COQUILLES`). Les manques, le Recyclage, les
compteurs et les fiches sont identiques à l'octet.

Les deux dernières se sont lues sans question non plus, parce que leurs
deux lectures possibles PAIENT PAREIL : TCE 20/02 `N · F-PM` (formation
l'après-midi, « remplacé par ATR remplacé par DKS ») est le F de la règle
de FLN ; VGG 25/02 `PM · SD26 -F` réunit deux codes de journée de jour.
**Zéro mention non comprise** dans le classeur ; seul le Recyclage bouge
d'une case (HKB meunerie 23 → 24, le rééquilibrage comblant la nuit du
20/02 que TCE a quittée).

« consign. » (BLR 22 au 24/07) quitte `ATELIERS` pour `MENTIONS_NEUTRES` :
les consignations de YRS, renfort avant en congé, faites en 7h-15h — une
tâche, pas un atelier. Rien d'autre ne bouge. Reste « Polyvalence » sur un
repos (LCI 23/09, SVE 21/09), sans aucun commentaire : question posée au
client le 26/09/2026 — venus travailler (A, heures sup ; B, payé
normalement) ou simple note (C).

### Changer de personne laissait des heures sup d'une autre

Trouvé le 26/09/2026 en rapprochant au centime la fiche de janvier de LCI :
l'application lui comptait 3 h d'heures sup que ni son horaire ni sa fiche
ne portent. Le pré-remplissage remplit d'abord la première personne de la
liste — AFA, rappelé sur un repos le 31/01 —, puis celle qu'on choisit ;
sur un repos, `remplirMois()` n'effaçait que `s`, `h`, `a` et `r`, et
laissait `ax`, `hsp`, `rs`, `rh`, `j`, `sp`, `q`. LCI héritait des heures
sup d'AFA, sursalaire et prime compris. Tous les champs écrits par le
pré-remplissage sont désormais effacés. Janvier de LCI passe de +(montant retiré) € à
**−(montant retiré) €** de brut — exactement la demi-heure sup « +0,5 hs » que son
commentaire du 14/01 porte et que l'application ne lit pas.

**Le rapprochement au centime trouve ce qu'aucun vérificateur ne voit** :
`verifier-calendrier.js` rejoue la lecture d'UNE personne à la fois, jamais
un changement de personne dans le même navigateur.

### Un férié presté se paie à 200 %, prime d'équipe comprise

**Chez l'ouvrier seulement depuis le 14/10/2026** : l'employé est payé
fixe + 100 %, voir « Ce qui attend le client ».

Le rapprochement au centime des fiches de LCI (26/09/2026) : mai, le 21/07
et le 15/08 manquaient exactement « heures fériées × taux horaire », et la
prime d'équipe doublée. Le client : « c'est la même règle pour les employés
aussi ». Le supplément d'un férié en semaine passe de 100 à **200 %**, non
déduit ; un férié un **samedi** se paie comme un dimanche ; la prime d'une
heure fériée va au seau du dimanche. Mai, juillet et août de LCI concordent
alors **au centime** sur le brut ; le net des huit mois passe de −910 € (au
premier tableau) à −41 €.

**Comment on est arrivé au centime** : chaque paramètre de la fiche repris
dans l'application — le TAUX HORAIRE ((montant retiré) puis (montant retiré), via une
rémunération de référence taux × 148,368 et l'écart de base en « autre
rémunération brute »), la réduction de précompte sur heures sup, le
volontariat fiscal sorti du précompte, la fraction 0,90 —, puis l'écart
rangé par rubrique, puis la rubrique ramenée à la journée. **Chaque écart
restant a une journée et une ligne de fiche**.

### Deux lectures de commentaire que la fiche a confirmées

Toujours le 26/09/2026, sur le rapprochement au centime de LCI :

- **les heures sup écrites en commentaire** — « +0,5 hs », « +3h hs » :
  trente journées de l'année, que l'application ne lisait pas. La fiche du
  14/01 les paie en heures sup à compenser, prime de la pause de la plage
  citée (`r.hc`, `r.hcp`) ;
- **deux rappels à deux dates** dans le même commentaire — « Rappel le
  07/04 + rappel le 13/04 » : deux primes, 12 h 05 d'heures de déplacement
  sur la fiche (`secondRappel()`, `rec.r2`). Une date recopiée ne compte
  qu'une fois.

Résultat sur LCI : **brut au centime** en janvier, mai, juin, juillet et
août ; février +0,90 € (le 20/02), mars −0,36 €, avril −5,40 € ; **net à
moins de 8 € chaque mois**, le reste étant un précompte de 6 à 11 € plus
bas que la fiche. Neuf règles, manques, Recyclage et compteurs identiques.

### Les quelques euros de net : le calage, l'indemnité, une journée de flex time

Le client, le 26/09/2026 : « d'où viennent les quelques euros de
différence ? ». Trois causes, et **quatre mois sur huit tombent alors au
centime sur le NET** (janvier, mai, juillet, août).

- **Le précompte suit le barème de l'application À UNE CONSTANTE PRÈS**, la
  même sur les huit fiches : une seule valeur de « Calage barème » les
  reproduit toutes au centime, sans arrondi par tranche de 15 €. L'écart de
  6 à 11 € n'était que le calage par défaut, qui vient d'une autre fiche.
  **Rien à coder** : c'est le réglage personnel prévu pour cela, et l'onglet
  Contrôle le recalcule depuis le précompte d'une fiche. Ce qui variait
  d'un mois à l'autre venait de la base : l'indemnité imposable.
- **L'indemnité de déplacement change de taux** d'un mois à l'autre sur les
  fiches, avec une régularisation une fois. C'est le champ du mois
  « Indemnité déplacement / jour ». **La fiche simulée écrivait le taux des
  Réglages** à côté du montant calculé au taux du mois : elle écrit
  désormais celui du mois.
- **Une reprise de flex time d'une journée entière comptait comme une
  journée de présence** : le 01/03, « 8h -FT, remplacé par GDT », donnait
  un chèque-repas et une indemnité de déplacement. La fiche n'en porte
  aucun — 18 jours pour 19. Les heures restent payées depuis le compteur
  (section 6 de `docs/conversion-horaire.md`), mais **le chèque et
  l'indemnité se comptent sur les heures PRÉSENTES**. 212 journées chez
  52 personnes ; neuf règles, manques, Recyclage et compteurs identiques à
  l'octet.

Restent : février +0,40 € (le 20/02), mars −1,25 € (un chèque de
récupération de flex time, question ci-dessous), avril −5,68 € (trois
chèques et les journées connues), juin +2,26 € — la régularisation
d'indemnité, que la simulation a saisie en « autre indemnité nette », non
imposable, alors que la fiche l'impose.

### Les compteurs CP, TP, CT comptent les journées posées

Mesuré le 26/09/2026 : le compteur du pied de feuille est le nombre de
journées DÉJÀ POSÉES, et « à planifier » (ou « solde à planifier ») ce qui
reste du droit de l'année — LCI 25 posées dans l'horaire pour un compteur
de 25 et 1 à planifier, GSK 51 et 51 et 1.

**RCO en a une de plus dans l'horaire** : 27 journées `CP` pour un compteur
de 26 et rien à planifier. Le client, le 26/09/2026, entre le 01/01 et le
11/11 — les deux fériés de la série : **le CP du 01/01 ne compte pas** (jour
férié, ou compté sur 2025). Le 11/11, lui, compte.

**Rien n'est codé** : l'application affiche les compteurs du classeur tels
quels et ne les recalcule pas. Si un jour elle les recompte depuis les
journées, cette journée-là est l'exemple à reproduire — et un férié ne
suffit PAS à l'écarter, puisque le 11/11 reste dans le compte.

### Pour plus tard, à la demande du client

- ~~Un calendrier du téléphone qui se met à jour seul~~ : fait le
  13/10/2026, voir « L'abonnement à l'agenda ».

### Les réponses du 29/09/2026

**Un départ anticipé sans code est une reprise (RHS).** Le client : « A :
toujours en RHS ». `lireJournee()` lit « départ à Xh » — fautes de frappe
comprises, « D2PART 0 18H » — et verse les heures du départ à la fin du
poste au compteur de récup. HS (`rhsJ` → `rec.rh`), sans prime ; les
heures prestées baissent d'autant. La fin d'un D est 15 h (« seulement D :
7-15 »), **16 h pour les consignateurs** : YRS l'écrit lui-même le 08/01,
« départ à 15h30 - RHS ». Seulement sur une journée pleine dont la cellule
franche est un poste, sans aucun autre code (RTT, DTT, VA, CSS, ±FT, RHS
chiffré) ni code de jour, et pas quand le commentaire remplace quelqu'un
AVANT le départ — c'est alors l'autre qui part. **Cinq journées** : LCI
05/04 (4 h, comme sa fiche), VGG 23/07 (2 h, comme son relevé), BLR 28/08
(2 h), YRS 09/01 (1 h 15) et 08/01 (0 h 30). Neuf règles, `--manques 0929`
et `--compteurs` identiques à l'octet ; Recyclage : VGG chaudières 3 → 2
(le 23/07 n'est plus une journée pleine). VGG le 15/05 n'est plus un
écart connu : sa cellule `["AM","R-CM","Remplace AFA"]` ne dit pas le
départ, mais celle du 16/05 l'écrit (« 2h rhs pris le 15.05 départ à
12h »), voir « Le cadre du mois, repris case par case » (18/10/2026).

**« Polyvalence » sur un repos est une note.** Le client : « le mot
polyvalence veut juste dire qu'à partir de ce jour-là ils ont changé de
poste pour commencer leur formation à un autre poste ». Les deux journées
(LCI 23/09, SVE 21/09) se lisaient déjà en repos ; la mention entre dans
`MENTIONS_NEUTRES`, et la règle « mention avalée » du vérificateur ne
compte plus une mention neutre (2 → 0, règles faibles 50 → 48). **La date
n'est pas posée dans `FORMATION_DEBUT`** : le poste d'avant de SVE n'est
écrit nulle part, et LCI tient la fermentation jusqu'au 29/09 par décision
du client (`POSTE_PERIODE`).

**Un opérateur en formation rappelé pour remplacer prend la place du
remplacé.** Le client, devant le terrain arrière vide de la nuit du 02/10 :
« la réponse est pourtant dans le fichier ». Elle l'était : SKS porte
`["-","N","Remplace SBZ …"]`, et SBZ tient le terrain arrière. SKS, en
formation meunerie depuis le 21/09, y est validé (fermentation et
distillation) ; mais la ligne 9 le rangeait en meunerie, en plus, avant
que quoi que ce soit lise son commentaire. **J'avais proposé SKS comme
« piste » le 28/09 au lieu de lire sa cellule** : la règle « les
commentaires d'abord » vaut aussi pour le placement. `postesDePause()`
lit donc `atelierDuRemplace()` AVANT `posteTenu()` pour un opérateur en
formation — la règle du client du 21/09, « on le rappelle pour remplacer
dans un poste qu'il peut, et ce sera marqué en commentaire » —, à
condition qu'il ait la polyvalence et que la cellule n'écrive pas
l'atelier. Le même soir LHR, « Remplace SPT », passe des chaudières (en
plus) au gluten. Neuf règles et compteurs identiques à l'octet ;
sous-effectifs d'ici la fin de l'année **7 → 6** (le 02/10 disparaît) ;
sur l'année, 277 → **269** places creuses, 174 → 171 journées ;
Recyclage : les journées où un stagiaire remplaçait comptent à son poste
validé (GST fermentation 11 → 16, LHR gluten 3 → 7, SVE gluten 1 → 2,
HKB et LHR meunerie +1) et JKS fermentation 10 → 9, qui ne comble plus la
place ; **22** couples au quota au lieu de 23.

**Les deux heures du projet falling film sont des HS, à la prime de
l'autre pause.** Le client : les opérateurs choisiront HS ou FT+ sur une
feuille de demande, et « si FT+ il sera marqué dans l'horaire en
commentaire » ; puis « ceux qui font le matin auront la formation après
14h et ceux qui font PM avant 14h ». `lireJournee()` pose donc 2 h sup
(`r.hc`, le mécanisme des « +0,5 hs » écrits) sur une journée « projet
falling film » : prime d'après-midi après un matin (14 h-16 h), prime du
matin avant un après-midi (12 h-14 h). Seulement pour qui TIENT sa pause :
pas un « remplacé par » (5 journées), pas une plage de jour ni « D-F » ni
un repos (6), et rien si un flex time est écrit. **21 journées sur 33**,
les 05, 09, 15 et 26/10. La première version laissait passer les
« remplacé par » : `\w` ne reconnaît pas le « é » en JavaScript sans
`/u`, le piège déjà écrit pour « éq ». Neuf règles, sous-effectifs,
Recyclage et compteurs identiques à l'octet (la règle est de paie
seulement) ; la fiche d'octobre de VBN porte ses 2 h du 15/10 à la prime
d'après-midi, hors ligne compris.

**« remplace Y » sans rien chez Y : Y était ailleurs à l'usine.** Le
client : « B : FLI ailleurs ». Rien à coder : l'application montre déjà
les deux présents (16 journées), ce qui est juste.

**L'historique public porte encore les 60 identifiants** — trois versions de
`data/classeur-2026.xlsx` et six de `data/horaire-2026.json`. Le purger est
une décision du client, comme pour les noms (`docs/purge-historique.md`).


### « Presté 7h le 20.03 » : des heures faites un autre jour (19/10/2026)

Question posée le 18/10 : VGG le 15/03, `["AM","1h RTT","presté 7h le
20.03"]`, et le 20/03, `["-","SD 26","voir 15.03"]`. L'application comptait
7 h le 15/03 et 8 h le 20/03, soit 15 h pour une seule journée prévue. Le
client, le 19/10 : « les commentaires disent bien qu'il a fait 7h le 20/03
pour SD26 ». Désormais 0 h le 15/03 (la 1 h RTT reste) et 7 h le 20/03
(`RX_PRESTE_H`, le marqueur « DEP@n » de `renvoisDuMois()`). C'est la seule
journée de l'année qui l'écrit ainsi. Mesuré : vérificateur, une journée
prestée de moins et une absence affichée de plus ; neuf règles à 0 ;
manques, polyvalences, compteurs et fiches VBN identiques à l'octet ;
l'agenda de VGG perd le 15/03, rien d'autre ne change dans `cal/`.

### JBI le 21/08 : PM presté, RJF sur la pause du matin (19/10/2026)

Question posée le 18/10 : depuis que le RJF « cf 21/08 » du 13/08 est posé
le 21/08, l'application y comptait 0 h (le RJF retirait 8 h, le +FT 4 h).
Le client, le 19/10 : « il a fait PM à la place de YPE, mais était en RJF
pour sa pause du matin (RJF décalé à un autre jour pour être compté), il y
a aussi une remarque de 4h FT+ qui ont été faites le 18/08 ». Désormais :
21/08 PM 8 h et RJF compté ; les 4 h +FT épargnées sur le 18/08
(`RX_FT_SUR`, « FT sur » ajouté à `RX_RENVOI`, et « sur la pause X »
dans `lireJournee()`). Mesuré : une journée prestée de plus, une absence
de moins ; neuf règles à 0 ; manques, compteurs et fiches VBN identiques à
l'octet ; polyvalence : JBI Gluten 3/5 → 4/5 (le remplacement du 21/08
compte) ; agenda : le 21/08 de JBI dit « Contremaître ».
