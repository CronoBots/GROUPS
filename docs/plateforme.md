# La plateforme qui remplace le classeur

Le client, le 21/10/2026 : « le but est, à terme, de ne plus travailler avec
Excel. Actuellement je l'utilise pour construire l'app, car il contient tout
le nécessaire et leur manière de travailler. » Ce document est l'inventaire
de cette manière de travailler, mesuré sur le classeur du 19/10/2026
(récapitulatif 2026), et l'équivalent que la plateforme doit offrir pour
chaque usage. [M] = mesuré, [S] = supposé. Aucun nom : trigrammes seulement.

## 1. Le circuit du classeur

- **14 classeurs par fonction** [M], dans le même dossier que le
  récapitulatif : Poly arrière, Fermentation, Distillation, Renforts,
  Meunerie, Gluten, Poly Av., Poly Avant, Centrale thermique, Adjoints,
  Contremaîtres, Opérateurs en formation, Chaudières + renfort, STEP. Chacun
  est tenu à part ; le récapitulatif n'est qu'une COLLECTE.
- **34 procédures VBA** [M], lancées par 17 boutons de « Config » :
  - « Générer l'horaire » ouvre les 14 classeurs, copie les lignes 11 à 376
    (366 jours) en valeurs et commentaires dans Shift1 à Shift5, Opérateurs,
    Step, Contremaître ; le pied (377-450) recollé en valeurs, les formules
    des sources « casseraient le collage » ; horodate, reprotège, referme ;
  - un bouton par fonction fait la même chose pour une seule source ;
  - « Mettre à jour noms opérateurs » recopie la ligne 10 (les noms) ;
  - « Modifier l'année » réécrit les onglets attendus, recopie les dates
    depuis Poly arrière (le calendrier modèle) et EFFACE données et
    commentaires de l'année ;
  - à chaque ouverture, la polyvalence est importée d'un autre classeur
    (« Niveaux de polyvalence pour horaire », sur un partage réseau) ;
  - 8 filtres de la feuille Polyvalence par atelier (« Poly. arrière » =
    Fermentation ET Distillation ; le bouton « Step » est sans doute cassé).
- **Protection** de toutes les feuilles par un mot de passe écrit en clair
  dans les macros (jamais recopié).
- Conséquences mesurées : les couleurs des sources sont perdues (collage
  en valeurs) ; les adjoints sont copiés six fois (5 Shift + Contremaître).

## 2. Les feuilles

| Feuille | Rôle [M] |
|---|---|
| Config | liste des 14 sources, date de mise à jour, consignes, boutons |
| Shift1 à Shift5 | une équipe ; l.1-8 légende, l.9 poste tenu, l.10 nom, l.11-376 les jours, l.377-450 compteurs ; 2 colonnes par personne (prévu, annotation) |
| Opérateurs, Step, Contremaître | opérateurs en formation (10), station d'épuration (4), contremaîtres (6) + copie des adjoints |
| Polyvalence | 73 lignes : matricule ou statut, nom, prénom, degré G/H (classification entreprise), une croix par atelier, 74 commentaires datés (66 acquisitions, 7 fins, 1 revalidation) |
| Personnel (cachée) | 56 lignes nom → trigramme |
| Récapitulatif (1) (cachée) | ébauche abandonnée d'un plan de postes par pause (9 postes × 3 pauses, ~9 500 formules, janvier-février seulement, listes déroulantes) |

## 3. Les codes

- **Cellule (prévu)**, 27 577 journées : AM 5 674, PM 5 103, N 4 934,
  D 1 349, repos 8 425, plages horaires 1 778, « H. flott. » 124, divers
  208 (SD26, R-CM, F, DS-CE, D-CPPT, D-F, DS…).
- **Annotation (réel)**, 11 079 journées (40 %) : Abs 1 987, VA 1 373,
  RTT 778, RJF 665, CP 425, RHS 363, DTT 236, TP 209, CT 160, ±FT 473/418,
  R-CM/R 324/249, F/D-F 299, SD26 197, atelier 983, poste réel 1 497…
- **Légende du classeur** : 11 codes (VA, RTT, RHS, RJF, xxx, R, Abs, DS,
  CP, CSS, R-CM). « xxx » (congé rappelable) n'apparaît dans aucune journée
  de 2026 ; DTT, CT, TP, F, D-F, SD26, E. min, VM, DS-CE, D-CPPT, ±FT, HS,
  H. flott., eval, CEP sont utilisés sans être légendés.
- **Aucune liste déroulante** sur les feuilles visibles : tout est tapé à
  la main (d'où 142 variantes d'écriture d'un même atelier).
- **228 mises en forme conditionnelles** : solde flex time rouge hors de
  [−8 ; 80], [−8 ; 24] ou sous −9 selon les personnes ; soldes restants
  rouges si négatifs ; ligne 9 colorée selon le renfort.
- **Barré** = annulé : 2 195 segments.

## 4. Les commentaires : des événements écrits en texte libre

12 234 commentaires, 6 910 journées commentées une fois les copies
retirées ; un commentaire porte souvent plusieurs faits.

| Événement | Journées | Forme typique |
|---|---|---|
| remplace X | 2 167 | « remplace SBZ », chaînes « remplace FPA qui remplaçait LDT » |
| remplacé par X | 2 003 | « remplacé par KDN et FLN » |
| échange avec X | 1 027 | la cellule porte déjà la pause échangée |
| renvoi à une autre date | 727 | « presté le 27.04 », « déplacé au 03/03 » |
| effectif | 682 | « équipe au complet », « SPT et IME présents » |
| départ / arrivée en cours de pause | 643 | « départ à 19h00' » |
| plage horaire | 580 | « remplace FLI de 22h à 24h00' » |
| rappel | 512 | « rappel le 11/03 » |
| maintien de prime | 348 | « maintien prime N » |
| formation | 301 | « Formation distillation » |
| intervention, projet, test | 212 | « Test performance sécheur 1 » |
| compteur écrit en clair | 200 | « +4h rhs » |
| réunion, évaluation, visite médicale | 94 | |
| renfort, arrêt SD26 | 87 | |
| validation, mail, accord | 73 | |
| changement de pause | 62 | « changement PM-> AM » |
| syndical | 51 | « DS CE » |
| décompte n/m | 41 | « cp 8/20 » |
| maladie, justificatif | 22 | la maladie est surtout l'annotation « Abs » |
| annulation | 18 | « VA annulé rappel le 23.01 » |

## 5. Le pied de feuille

| Bloc | Lignes | Saisi ou calculé |
|---|---|---|
| prévisions VA, ½VA, RTT, DTT, RJF (en heures) | 377-394 | calculé dans les sources (`COUNTIF` × heures), arrive en valeurs |
| soldes au 01/01 | 395-402 | saisi à la main au changement d'année |
| soldes restants | 403-408 | solde − prévisions, rouge si négatif |
| flex time | 409-430 | ±FT par durée, total = solde, report saisi à la main |
| congés réduits CP, TP, CT, à planifier | 431-440 | valeurs |

Contrats (63 commentaires, 36 personnes) et notes (≈ 20 : fériés à
reprendre…) en commentaires du pied : déjà lus par l'application (`ct`).

## 6. L'équivalent dans la plateforme

| Usage du classeur | Dans la plateforme | Ce qui disparaît |
|---|---|---|
| 14 classeurs + collecte | une table `journees`, saisie par la hiérarchie de chaque fonction, droits par périmètre | les fichiers, la copie, les 6 copies des adjoints |
| cellule = poste prévu | le cycle des 5 équipes GÉNÉRÉ (affectation personne → équipe) | « Modifier l'année », le calendrier modèle |
| annotation | un code choisi dans une LISTE FERMÉE (sens, paie, légende) | les variantes d'écriture, les colonnes inversées |
| remplace / remplacé par / échange | UN événement à deux personnes, visible des deux côtés ; contrôles : remplaçant libre, remplacé absent, polyvalence de l'atelier | les deux commentaires qui se répondent |
| plage, départ, arrivée | début, fin, heures de l'événement ; durées calculées | |
| rappel le JJ/MM | événement `rappel` daté ; prime calculée (`regles-paie.md`) | |
| maintien de prime | attribut de l'événement, validé par le contremaître | |
| ±FT, RHS, HS, « presté le » | événements liés à la journée compensée, « payé ou épargné » explicite | |
| congés | module `demandes` : opérateur → contremaître → RH, soldes visibles ; « rappelable » = un statut | « xxx » |
| Abs | événement `maladie`, drapeau « justificatif reçu » | |
| formation, VM, évaluation, syndical | événements typés, avec plage | |
| « équipe au complet », manques | écran d'effectif par pause et par poste, alerte, proposition de remplaçant polyvalent | l'ébauche cachée |
| pied de feuille | compteurs CALCULÉS ; seuls les soldes d'ouverture se saisissent, une fois par an ; bornes flex par personne | lignes masquées, vérification à la main |
| contrats, notes | tables `contrats` (type, %, du, au) et notes datées | |
| polyvalence importée | table `polyvalences` datée, tenue dans la plateforme ; filtres d'écran | l'import réseau |
| barré | `annule_le`, `annule_par`, historique | |
| mot de passe des feuilles | rôles, règles de la base, historique | toute la protection |

## 6 bis. Les 14 classeurs de fonction (reçus le 21/10/2026)

Le client a envoyé les 14 sources (02 à 13, A, B), hors du dépôt. Elles
portent ce que le récapitulatif ne reçoit pas : les FORMULES. Mesuré :

**Structure.** Une feuille par classeur, même disposition que le
récapitulatif (l.11-375 les jours, l.377-435 le pied) ; 81 personnes ;
3 834 formules, toutes dans le pied ; aucune protection, aucune liste
déroulante (9 validations vestiges en ligne 207, toujours fausses), saisie
entièrement libre (186 annotations différentes hors compteurs).

**Le pied, en spécification** (`A` = colonne d'annotation de la personne) :

| Ligne | Calcul |
|---|---|
| 377-394 prévisions | `NB.SI(A11:A375 ; code) × k` : VA 8, 1/2VA 4, « N h RTT » N (1 à 7), RTT 8, DTT 8, 1/2DTT 4, RJF 8, 1/2RJF 4 ; égalité de cellule entière. Un VA vaut 8 h même sur une pause de 12 h ; pas de ½RTT ni de « N h VA » |
| 399-402 soldes au 01/01 | saisis à la main, l'arithmétique dans la cellule : VA 160 à temps plein (144 à 90 %, 128 à 80 %) + report ; RTT 64 opérateurs, 80 contremaîtres et adjoints, `64-(n*4)` ; DTT report + crédits (`24+16`…) ; RJF `80-(n*8)`, 10 fériés × 8 h moins les fériés perdus, listés en commentaire |
| 405-408 restants | solde − prévisions (− report vers l'année suivante, écrit `-24+N("report 24h sur 2027")`) ; rouge si négatif |
| 412-430 flex time | Σ « N h +FT » × N + Σ « N h −FT » × (−N), N de 1 à 8 ; Total = report 2025 écrit en constante dans la formule + les deux sommes ; rouge hors de [−8 ; 80] (70 personnes) ou [−8 ; 24] (11) |
| 432-435 CP, TP, CT | jours posés (`NB.SI`) ; reste = droit écrit à la main d'après le commentaire de contrat (26, 52, 20, 40, 6, 9, 21, 31) − posés |

**Ce que les formules ne comptent pas** : RHS (≈ 300 annotations, aucun
compteur), HS, Abs, R-CM, SD26, F, DS, VM ; 44 annotations « de compteur »
échappent au comptage (41 « RTT- » du 02 au 10/01, 3 fautes d'espace).

**Erreurs de formule mesurées** (à signaler à la RH, à ne pas reproduire) :
un Total flex qui lit une ligne vide (le +FT d'une personne n'est jamais
compté), un DTT = VA + RTT (224 h fictives), un restant VA moins RTT, un
flex décalé de 4 lignes (29-31/12 perdus), des CP comptés à partir du 02
ou du 03/01, cinq formules absentes, un libellé « au 01/01/2025 ».

**Ce qui n'arrive jamais au récapitulatif** : TROIS PERSONNES, au-delà des
plages fixes que copient les macros (une 6e personne en Fermentation, une
en Chaudières + renfort, un « CM Travaux » chez les contremaîtres) — 2 005
cellules et 226 commentaires, donc absents de l'application aujourd'hui ;
les 548 couleurs peintes à la main (jaune : jour déplacé ou à surveiller ;
orange : arrêt SD26 ; lavande : une période, écolage ?) ; les formules
(reports, retenues, CP découpés quand le contrat change). Le reste est
identique (38 623 cellules, 7 714 commentaires, 7 077 valeurs du pied) ; les
seuls écarts sont des saisies faites après la collecte du 19/10.

**« xxx »** (congé rappelable) : dans la légende de 13 sources, employé
dans AUCUNE journée ni aucun commentaire des 14. Il sort de la liste des
codes ; « rappelable » sera un statut de la demande de congé.

**Conséquences pour la plateforme** : liste fermée des codes de compteur
(et un compteur RHS, qui manque) ; compteurs calculés sur toute l'année,
sans plage ; solde au 01/01 = droit × taux de contrat au prorata + report −
retenues DATÉES et motivées (le RJF se calcule : fériés tombés pendant une
absence, un TP, avant l'engagement) ; report vers l'année suivante et
report d'ouverture du flex en CHAMPS, jamais en constante ; bornes du flex
portées par la personne ; couleurs devenues attributs (jour déplacé,
période SD26, date d'entrée) ; aucune plage fixe : une personne de plus ne
se perd plus.

## 6 ter. L'espace RH (21/10/2026)

**La disposition du classeur se garde** (le client, le 21/10/2026) : les
dates à la verticale, les personnes à l'horizontale, parce que ceux qui
l'utiliseront travaillent ainsi depuis toujours. Tout écran de saisie ou
de lecture de l'horaire suit ce sens.

La plateforme prend la forme des logiciels de gestion du personnel : menu,
tableau de bord du jour (effectifs par pause, sous-effectif, absents,
compteurs négatifs, sortie d'Excel, activité), planning (une ligne par
personne, une pastille par jour, panneau de saisie, « jusqu'au »),
personnel (annuaire et fiche), absences et congés, historique. Les modules
qui suivent s'y ajoutent comme des sections.

## 7. L'ordre de construction

1. Saisie des journées par la hiérarchie et la RH, liste fermée des codes. **Fait le 21/10/2026** (`base/09-saisie.sql`, feuille du jour) ; restent les droits par périmètre (équipe, fonction) et une saisie de plusieurs jours d'un coup.
2. Remplacements, échanges et rappels en événements à deux personnes
   (≈ 75 % des commentaires ; alimentent la paie). **En partie le 30/10/2026** : le
   formulaire de courte durée porte déjà l'échange (modification de
   pause, remplaçant qui signe, contremaître puis RH), expliqué dans
   « Infos et aide » ; reste à écrire seul le jour du remplaçant, ce qui
   attend la question 3 de « La plateforme » (la prime de rappel).
3. Demandes de congé, opérateur → contremaître → RH, avec soldes. **Fait le 21/10/2026** (`base/10-demandes.sql`, section « Demandes » de l'espace).
4. Compteurs calculés ; soldes d'ouverture saisis une fois par an.
5. Cycle généré et changement d'année automatique.
6. Effectif par pause et par poste, alertes, suggestion de remplaçant.
7. Polyvalences datées tenues dans la plateforme.
8. Contrats réduits et notes RH.
9. Maladie et justificatifs, formations, syndical, visites médicales.
10. Historique, annulation, rôles (en partie en base).
11. Exports de transition (vue imprimable par équipe, secrétariat social).

Questions ouvertes : `docs/questions-client.md`, « La plateforme ».
