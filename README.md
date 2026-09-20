# BIOWANZE

Simulateur de fiche de paie belge (secrétariat social Groupe S, CP 220).
On y saisit l'horaire presté du mois — matin, après-midi, nuit, jour, congés —
et la page reconstitue la fiche ligne par ligne jusqu'au net à recevoir.

Application web installable (PWA) : elle s'installe comme une application,
garde son icône et **fonctionne hors ligne**.

À la première ouverture, un court formulaire demande vos informations
personnelles (rémunération, situation familiale, équipe…) avec une
explication pour chaque champ. Les réglages communs à toute l'équipe
(primes, barèmes) sont déjà configurés. Tout reste modifiable ensuite dans
l'onglet « Réglages ».

## Installer

Une fois le dépôt publié sur GitHub Pages, ouvrez son adresse :

- **PC (Chrome, Edge)** — une icône « Installer » apparaît dans la barre d'adresse.
- **Android** — menu ⋮ → *Installer l'application*.
- **iPhone (Safari)** — Partager → *Sur l'écran d'accueil*.

## Ce que fait le calcul

- Suppléments de week-end (samedi 150 %, dimanche 200 %) et déduction correspondante
- Supplément de jour férié presté
- Primes d'équipe matin / après-midi / nuit, au taux du jour
- Heures supplémentaires non compensées et heures de déplacement
- ONSS 13,07 %, cotisation de solidarité sur bonus CCT 90
- Précompte professionnel : frais forfaitaires, tranches annuelles, réductions
  quotité exemptée et enfants à charge, réduction sur heures supplémentaires
- Cotisation spéciale de sécurité sociale (barème et plafonds)
- Chèques-repas, indemnités de déplacement voiture et vélo, avantages en nature

Tous les barèmes sont modifiables dans la page (onglet « Barèmes ») : rien
n'est figé dans le code.

## Pré-remplir depuis l'horaire d'équipe

Choisir sa ligne dans l'horaire d'équipe (par fonction puis par identifiant
anonymisé — initiales ou matricule, jamais le nom complet) remplit **les
douze mois de l'année**. Il n'y a pas de bouton : l'horaire est la source,
l'appareil n'en est que la copie, et la copie se refait à chaque ouverture
et à chaque changement de personne. Les journées corrigées à la main ne sont
jamais écrasées ; celles qui viennent de l'horaire, si — une correction des
règles de lecture ou un nouveau classeur les rattrape donc toutes seules.

Le bilan ne s'affiche que si quelque chose a bougé, et dit alors quoi —
journées mises à jour, heures reprises au compteur HS, jours de
remplacement contremaître, rappels proposés, mentions de rappel non
tranchées, journées non reconnues et corrections manuelles conservées. Près de 99 % des jours sont reconnus
automatiquement : les codes francs, mais aussi les mentions qui nomment le
poste sans l'encoder (« AM », « N ») ou le désignent par une plage horaire
connue (6h-14h le matin, 7h-15h et l'horaire flottant en jour).

### Qui l'on regarde

L'équipe et la personne se choisissent **une fois**, dans Réglages → « Qui je
suis ». C'est l'application d'un travailleur : une question réglée n'a pas à
occuper la place la plus chère de l'écran. L'en-tête n'en garde que la
réponse — l'identifiant et la fonction — et mène au réglage d'un toucher.

La personne choisie reste un contexte global : elle pilote les trois vues de
l'horaire et l'onglet Compteurs. La laisser au fond d'un
onglet obligeait à y revenir pour en changer.

Les sélecteurs sont garnis dès le démarrage, quel que soit l'onglet ouvert.

### Un seul chemin pour remplir l'horaire

« Appliquer le cycle » et « Copier le mois précédent » ont été retirés. Le
pré-remplissage lit l'horaire réel de la personne, ce que ni l'un ni l'autre
ne savait faire : le cycle théorique ignore les échanges, les remplacements
et les journées de délégation ; le mois précédent encore davantage. Trois
chemins vers le même but, dont deux moins bons, ne rendaient pas service.

La remise à zéro reste — le pré-remplissage n'écrasant jamais ce qui est
déjà encodé, il faut pouvoir repartir de zéro quand on s'est trompé de
personne. Elle a rejoint « Mes données », dans les réglages, où sont les
actions qui détruisent.

Le binôme, le cycle et le décalage ne servent plus au remplissage. Ils ne
gardent qu'un usage, désormais écrit dans leur aide : la procédure de rappel
n'accorde pas de prime pour une prestation en pause du matin sur une journée
prévue en « Day » de la 5ᵉ ou 6ᵉ semaine du cycle.

### Semaine, mois, année

Un sélecteur segmenté donne trois échelles de lecture, chacune pour une
question différente :

| Vue | À quoi elle sert |
|---|---|
| **Semaine** | relire sept journées en détail — poste, durée, ce qui est parti aux compteurs, et le commentaire du classeur en toutes lettres |
| **Mois** | le calendrier du mois : poste, code presté, marques de la journée, heures de chaque semaine |
| **Année** | voir la rotation d'un coup d'œil, et les totaux |

L'en-tête suit l'onglet. Le net à recevoir ne s'affiche plus au-dessus d'un
calendrier ou d'un état de compteurs, et le sélecteur de mois disparaît là
où il n'a pas de sens — les réglages, la vue annuelle, et la vue semaine qui
a sa propre navigation et peut enjamber deux mois.

#### Le mois se regarde, la journée se corrige

L'onglet Horaire montrait trente lignes de saisie empilées — trois écrans et
demi sur un téléphone. C'était faire de la correction le sujet et de
l'horaire un sous-produit, alors que le pré-remplissage se fait seul et que
corriger est l'exception.

Le mois est donc un **calendrier** : sept colonnes de jours, une huitième
pour les heures de la semaine, et dans chaque case le poste, le code presté
quand il diffère, et les marques de la journée — vélo, prime de rappel,
absence partielle. Toucher une journée ouvre une **feuille** qui porte sa
ligne de correction et, au-dessus, ce que le classeur d'équipe dit de cette
journée : la cellule, son annotation, le commentaire. C'est la seule source,
et c'est elle qu'on veut sous les yeux au moment de la contredire.

### L'équipe

Un travailleur en pauses ne se demande pas seulement ce qu'**il** fait : il
se demande **avec qui**. L'horaire d'équipe portait la réponse pour les 77
personnes et les 365 jours, et elle ne servait à rien — seule sa propre
ligne était lue.

L'onglet **Équipe** la donne : un jour, les quatre pauses, et pour chacune
la liste de ceux qui y sont, avec leur fonction. Puis les absents, avec le
code qui le dit, et les repos, repliés — c'est la moitié de l'équipe et la
question qu'on se pose le moins. Sa propre ligne est surlignée : se
retrouver dans soixante-dix-sept identifiants demande un repère.

Un **annuaire** complète l'onglet : chacun sous sa fonction, avec les
ateliers où il est formé.

### État des compteurs

Un onglet à part met **deux sources face à face** : le pied du classeur,
saisi à la main, et le même compteur recalculé depuis les 365 journées de
l'horaire. Quand les deux divergent, l'un des deux se trompe — c'est ainsi
qu'a été trouvée la colonne inversée du 07/11 chez FPA.

On y lit les soldes de congé au 1er janvier avec le prévu et le restant, les
compteurs de flex time et leur report de l'année précédente, les congés
parentaux, et les absences de l'année regroupées par famille. La
récupération d'heures supplémentaires n'y montre que les reprises : son
compteur vit hors du classeur.

### Vue année

Le calendrier annuel affiche :
les douze mois de la personne choisie, chaque journée colorée par son poste,
avec le total d'heures, la répartition par pause et le nombre de
remplacements. Survoler une case en donne le détail — poste, heures,
absence, rappel, et le commentaire d'origine du classeur. La cliquer ramène
au mois, sur cette journée.

Le codage des couleurs suit une méthode, pas un goût. Quatre postes, quatre
teintes en ordre fixe, validées au calcul : toutes les paires sont séparées
d'au moins 15 en vision normale et 8 en protanopie, sur la surface claire
comme sur la sombre. L'ancienne palette y échouait — après-midi et jour
n'étaient distants que de 9,5. Les absences ne prennent pas une cinquième
teinte : ce n'est pas une identité mais un état, elles restent neutres. Et la
couleur ne porte jamais seule l'information : chaque case affiche son numéro
et l'initiale de son poste, une légende chiffrée accompagne la grille.

Le commentaire d'une cellule prime sur le code de rotation : le code dit le
poste *prévu*, le commentaire ce qui a été *presté*. Une plage horaire en
commentaire fixe aussi la durée réelle de la journée.

Les compteurs sont interprétés selon les règles maison :

| Dans l'horaire | Interprétation |
|---|---|
| journée de plus de 8 h, sans mention | 8 h prestées + l'excédent en heures supplémentaires |
| journée de plus de 8 h avec `4H +FT` | 8 h prestées, l'excédent épargné au compteur |
| `8H -FT` | journée de congé : aucune heure prestée |
| `1H` à `7H -FT` | le poste amputé d'autant (`D` + `1H -FT` = 7 h) |

Le message de fin distingue deux cas : les jours **à vérifier**, pré-remplis
mais porteurs d'une mention particulière, et les jours **non reconnus**,
laissés vides et à compléter à la main. Les jours déjà encodés à la main ne
sont jamais écrasés.

### La barre de navigation ne bouge pas

Elle vivait en `position:fixed` **à l'intérieur** de l'en-tête collant. Sous
iOS, son `bottom:0` ne se résolvait pas sur le même viewport selon que la
page défilait ou non : sur un onglet court elle remontait de la hauteur de
la barre d'état — 59 px — et laissait le fond de page sous elle. Une barre
de navigation qui change de place selon l'onglet n'est plus un repère.

Elle est sortie de l'en-tête, dans un cadre ancré **par le haut** sur la
hauteur dynamique de l'écran (`100dvh`), où elle se range en bas. Plus de
`bottom` à interpréter : le haut de l'écran, lui, ne bouge jamais. Sur grand
écran la barre reprend sa place sous le nom de l'application — c'est le seul
déménagement du document, piloté par un `matchMedia`, et il ne coûte rien :
les clics passent par la barre elle-même, qui voyage avec ses écouteurs.

### Ce qui se règle, et ce qui ne se règle pas

Les valeurs communes à toute l'équipe — primes de pause, chèque-repas,
coefficients de la procédure de rappel, barèmes ONSS et impôt — s'affichent
sous un **cadenas** et ne se modifient pas depuis l'application. Les laisser
modifiables, c'était offrir un moyen de fausser sa fiche sans s'en
apercevoir.

Elles arrivent avec l'application et se mettent à jour avec elle : au
démarrage, chaque valeur verrouillée est **reprise du code**. Une valeur
qu'un appareil aurait gardée d'une version précédente est donc corrigée
toute seule — sans quoi la mise à jour ne serait jamais arrivée jusqu'au
calcul.

Restent à l'utilisateur : sa situation familiale, sa rémunération et sa
fraction, son cycle, ses déplacements, ses avantages, les montants de chaque
mois, et le « calage barème » que l'onglet Contrôle recalcule sur sa propre
fiche.

## Vos données

Elles ne quittent jamais l'appareil : tout est enregistré par le navigateur.
Rien n'est envoyé à GitHub ni à aucun serveur — l'hébergement ne sert qu'à
livrer la page.

Le bouton **Exporter mes données** en bas de page produit un fichier `.json`
qui sert de sauvegarde et permet de transférer vos mois vers un autre appareil
(bouton **Importer**).

## Fichiers

| Fichier | Rôle |
|---|---|
| `index.html` | l'application entière |
| `manifest.webmanifest` | nom, icône, couleurs |
| `sw.js` | cache et fonctionnement hors ligne |
| `icon-*.png` | icônes |
| `.nojekyll` | désactive le traitement Jekyll de GitHub Pages |
| `data/horaire-2026.json` | horaire d'équipe 2026 pour le pré-remplissage, anonymisé (identifiants uniquement, aucun nom) |
| `docs/conversion-horaire.md` | comment lire l'horaire d'équipe : règles de conversion et de résolution |
| `docs/regles-paie.md` | règles de calcul confirmées par le client (chèques-repas…) |

## Licence

Usage personnel.
