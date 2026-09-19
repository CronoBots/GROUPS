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

Dans l'onglet Horaire, un sélecteur permet de retrouver sa ligne dans
l'horaire réel de l'équipe (par fonction puis par identifiant anonymisé —
initiales ou matricule, jamais le nom complet) et de pré-remplir
automatiquement **les douze mois de l'année**, d'un seul clic. Les journées
déjà encodées à la main ne sont jamais écrasées : le bouton se rejoue sans
risque après une correction manuelle ou un nouveau classeur.

Le bilan dit ce qui a été fait et ce qui reste à regarder — journées
remplies, heures reprises au compteur HS, jours de remplacement
contremaître, rappels proposés, mentions de rappel non tranchées, jours de
repos et journées conservées. Près de 99 % des jours sont reconnus
automatiquement : les codes francs, mais aussi les mentions qui nomment le
poste sans l'encoder (« AM », « N ») ou le désignent par une plage horaire
connue (6h-14h le matin, 7h-15h et l'horaire flottant en jour).

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
| **Mois** | encoder : c'est la surface de saisie, inchangée |
| **Année** | voir la rotation d'un coup d'œil, et les totaux |

L'en-tête suit l'onglet. Le net à recevoir ne s'affiche plus au-dessus d'un
calendrier ou d'un état de compteurs, et le sélecteur de mois disparaît là
où il n'a pas de sens — les réglages, la vue annuelle, et la vue semaine qui
a sa propre navigation et peut enjamber deux mois.

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
