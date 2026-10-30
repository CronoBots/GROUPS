# Questions ouvertes

Seulement ce qui attend encore une réponse. Quand une réponse arrive : on
applique, on mesure, on écrit la règle dans `docs/regles-paie.md` ou
`docs/conversion-horaire.md`, et on **retire la question d'ici le jour
même**. Avant de poser une question, la recouper avec ces deux fichiers et
le journal : le 19/10/2026, une question tranchée le 14/10 a été reposée
parce qu'elle n'avait pas été retirée. L'historique des questions
tranchées est dans `docs/journal/03-extraction-et-audit.md`, « Archive
des questions au client ».

## Au client

1. **Supprimer à la main sur GitHub** la branche
   `feature/calendar-weekly-desktop` et les deux étiquettes
   `checkpoint-…` : la purge de `main` est poussée (30/10/2026, journal
   01, « La seconde purge »), mais ces trois références gardent
   l'ancienne histoire et la session ne peut pas les remplacer.
2. **Relire les infos pratiques** (30/10/2026) : vingt-deux, tirées du
   règlement de travail (version 5, 2025) et publiées dans « Infos et
   aide » ; la RH les corrige ou les complète dans l'application. Les deux
   points du scan qu'on croyait illisibles se lisent sur l'image (relecture
   du 30/10/2026) : l'article 44 (fin d'année, demande au plus tard le
   31 août, réponse au plus tard le 1er octobre) et l'affiche de sécurité
   de l'annexe VI. Depuis cette relecture, il y en a trente-neuf, dont
   deux tirés des notes de service : à relire de même.
3. **« Vos données »** (30/10/2026) : qui est le responsable du
   traitement, sur quelle base légale, et combien de temps garder les
   comptes, l'horaire, les demandes et l'historique ? Et faut-il que les
   noms et prénoms restent lisibles de tout compte validé (l'Horaire
   production s'en sert), ou seulement de la RH et de la hiérarchie ?
4. **Que compte la ligne « Heure(s) prestée(s) » de la fiche** (posée le
   25/09/2026, `docs/journal/08-verifications.md`) : les heures réellement
   faites, ou le solde du mois contractuel une fois les absences
   retirées ? Aucun montant n'en dépend (la ligne est une quantité, le
   salaire de VBN tombe au centime sans elle) ; elle sert à confronter les
   heures de l'application à celles de la fiche.

5. **« CEP » chez ADK en 2027** (posée le 20/10/2026) : seize journées,
   une par semaine de janvier à juin (le jeudi le plus souvent), écrites
   avec un poste et l'annotation « CEP » (`["PM","CEP"]`), sans
   commentaire, inconnues de 2026 et de la légende. Est-ce le congé-
   éducation payé (des cours, la personne n'est pas au poste) ? Si oui,
   la journée est une absence payée, sans prime de pause. En attendant,
   l'application la lit comme un poste presté, 8 h et la prime. Deux notes
   de service y penchent (30/10/2026) : la note du congé par heure (2022)
   compte les « congés (tous types confondus y compris les CEP) » et parle
   des « congés CEP relatifs à l'année scolaire », et la note du relevé
   mensuel donne « 53 = congé éducation payé ».

6. **Un « R-CM » de quelques heures, dans quelle ligne du Planning ?**
   (posée le 20/10/2026) Le Planning range un remplacement de
   contremaître PARTIEL dans la ligne Adjoint — la règle de la prime
   (`remplacementCM`, journée entière seulement) sert aussi au rangement.
   C'est le cas de VGG le 05/06 (« R-CM, remplace ATA de 10h à 14h ») et le 30/06,
   FPA le 19/09 (« remplace FLI de 0h à 6h »), JBI le 21/08 (« R-CM,
   4h +FT, remplace YPE », GPS faisant 18h-22h). Faut-il les montrer dans
   la ligne Contremaître, à côté du titulaire, avec leurs heures ? La prime
   ne change pas.

7. **Qui est le « responsable de zone » de la fiche de recyclage ?**
   (posée le 22/10/2026) La fiche papier exige sa signature pour un
   recyclage en doublure. En attendant, n'importe quel compte hiérarchie
   ou RH peut contresigner (la base n'a aujourd'hui que des comptes RH).
   Dites qui, et la base le réservera à ces personnes.

- **Le report FT de fin 2025 (27/10/2026).** Le solde FT montré est le
  « Total » de la ligne 430, report de 2025 compris ; ce report est une
  constante dans la formule, et la copie reçue n'a que des valeurs. Pour
  vérifier chaque solde, et retrouver la personne dont le Total ne compte
  pas son +FT (inventaire, `docs/plateforme.md` section 5), il faut le
  classeur avec ses formules (le `.xlsm` d'origine), ou la liste des
  reports de fin 2025.

- **Les places vides que les commentaires expliquent (28/10/2026).** Le
  contrôle `--manques-commentes 0101` trouve, avant aujourd'hui, 97 places
  vides du Planning dont le titulaire absent est nommé par un commentaire
  du jour. Trois cas se corrigeaient sans rien supposer (29/01, 16/02,
  14/09) ; les autres demandent une règle que le classeur ne donne pas :
  1. **« échange avec X » (27 places)** : le 06/02 PM, le fermentier passe
     en nuit « échange avec » un chaudiériste, qui vient en PM. La
     fermentation reste vide : le chaudiériste la tient-il, ou reste-t-il
     aux chaudières (et la place est vraiment vide) ?
  2. **« N h +FT » d'une autre pause (dans les 43 « remplace »)** : le
     02/02, le contremaître du matin écrit « 4h +FT · remplace » celui de
     l'après-midi. Ses 4 h de flex time sont-elles de 14 h à 18 h, au poste
     du remplacé ?
  3. **« R-CM · 1h +FT · remplace X »** (le 07/03) : l'adjoint tient-il
     tout le poste de contremaître de la pause, ou une heure seulement
     (c'est ce que la prime lit aujourd'hui) ?
  4. **« remplacé par X » écrit par le seul titulaire (26 places)** : X
     est à un autre poste ce jour-là ; le Planning doit-il le déplacer ?

- **Le repos payé A1 en semaine 5bis (30/10/2026).** La note de 2009 met
  le repos payé A1 le jeudi de la semaine 5 (D du lundi au mercredi). En
  semaine 5bis (règlement, art. 8-2.3 : D du mercredi au vendredi), ce
  jeudi est un D ; l'application ne le recule au lundi que si le jeudi est
  un TP — la règle confirmée le 14/10 sur les fiches de LCI. Vaut-elle pour
  tous en 5bis ? Si oui, JBA le 13/08 et LAA le 29/10, `["D","N",…,
  "Rappel…"]`, ne sont plus des rappels sur un repos (8 h sup) mais un D
  changé en nuit, comme ADK le 10/07 et LAA le 21/08 le vendredi.

## À la RH

Le client, le 14/10/2026 : « garde la question pour RH ».

5. **Le mois où le fixe change** (VBN, contremaître au 15/09) : comment
   partager le mois entre les deux fixes, par demi-mois ou par jours de
   calendrier ? Et à signaler : la fiche de septembre paie la hausse dès le
   15/08 (« le RH a fait une erreur »). Voir `docs/regles-paie.md`.
6. **La maladie** : le « premier mois » payé par l'employeur vaut-il
   30 jours calendrier (`MALADIE_EMPLOYEUR_J`) ? Comment le fixe d'un
   employé est-il réduit au-delà — au taux horaire, en jours, au prorata ?
   Et une rechute : le règlement (art. 48, annexe XII) présume la même
   maladie dans les 14 jours calendrier qui suivent la fin de la
   précédente ; le mois de salaire garanti continue-t-il alors, au lieu de
   recommencer comme le fait l'application ?
7. **La nuit de 12 h « 18h-06h » d'un ouvrier** (LCI le 20/03) : la fiche
   paie 18 h-22 h à la prime de nuit, l'application à celle de
   l'après-midi (la règle de l'employé, états SAP de VBN). Laquelle pour
   l'ouvrier ?
7 bis. **Quelle grille pour qui ?** (30/10/2026) Le règlement de travail
   connaît deux régimes en feu continu : 38,40 h en moyenne et 8 jours de
   RTT (art. 8-2.3, cinq semaines), 38,67 h — soit 38 h 40 — et 10 jours
   (art. 8-2.4, six semaines). Le classeur donne 64 h de RTT aux opérateurs
   et 80 h aux contremaîtres et adjoints ; la fiche d'un adjoint porte
   38:40. Les opérateurs sont-ils à 38,40 h (192 h sur cinq semaines, soit
   38 h 24) ? L'application prend 38 h 40 pour tous (réglage « Heures /
   semaine », affiché seulement ; le diviseur horaire ne sert qu'au fixe
   d'un employé).
   Le règlement précise aussi que le temps plein est de 37 h par contrat :
   38,40 et 38,67 h sont des durées moyennes effectives. Au 4/5 (art. 8-4.3) :
   30,7 h et 6,5 jours de RTT sur cinq semaines, 30,9 h et 8 jours sur six.
   Un indice : la fiche d'un ouvrier opérateur porte « temps partiel /
   34:24 », soit 38:24 moins 4 h. La CCT d'entreprise du 26/09/2013 « ayant
   pour objet le temps de travail » (annexe IX) trancherait : peut-on en
   avoir le texte ?
7 ter. **La demi-journée de conseil d'entreprise** : l'annexe XI paie les
   jours de dispense « primes de pause » comprises ; la fiche d'un ouvrier
   (25/08) paie la demi-journée « PM · DS-CE » sans prime d'équipe, et
   l'application fait comme la fiche. La demi-journée est-elle un « jour de
   dispense » au sens de l'annexe ?
8. **La RJF d'un ouvrier** (« récupération jour férié ») : payée comme un
   férié (salaire moyen) ou au salaire garanti ? L'application garde le
   garanti. Deux pièces (30/10/2026) : la note de la fiche paie « Hrs. Jours
   fériés » au salaire horaire moyen sous le code 50, et la note du relevé
   mensuel dit « 50 = récupération de jour férié » ; mais l'état SAP d'un
   employé code ses RJF 48. Et le salaire horaire moyen lui-même est
   « calculé chaque mois sur base du mois précédent » (note de la fiche) :
   l'application n'en garde qu'un, saisi dans Réglages. Faut-il le
   recalculer chaque mois ?
9. **Le recyclage de neuf personnes** : le « restant » du classeur RH ne
   correspond pas aux objectifs par atelier pour DWS (17 au classeur pour
   27), SBZ (11/26), FLN (7/22), FPS (15/30), PLZ (8/28), PAM (18/10),
   ASS (10/0), PDR (2/0), VBN (30/5). Quel est leur objectif, et sur
   quels ateliers ? Le héros montre en attendant les chiffres du classeur.
10. **Le pécule et le treizième mois des ouvriers** : à quelles dates ?
   (Chez l'employé : mai et juin ; chez l'ouvrier, le pécule vient de la
   caisse de vacances.) Le règlement de travail (art. 18) ne donne que
   l'avance et le solde — l'application les calcule pour l'ouvrier depuis
   le 30/10/2026 (`docs/regles-paie.md`, « Chez l'ouvrier ») — ; ni pécule
   ni treizième mois. Voir `docs/regles-paie.md`, « Reste ouvert ».

## La plateforme (inventaire du 21/10/2026, `docs/plateforme.md`)

1. **Les bornes du flex time** : [−8 ; 80] pour 70 personnes, [−8 ; 24]
   pour 11 (dans 02, 08, 09 et 12 ; six d'entre elles arrivées en cours
   d'année, quatre présentes toute l'année ; ni le temps partiel, ni le
   statut, ni la fonction ne l'expliquent). Quelle règle ? Nouvel engagé,
   période d'essai ?
2. **Trois personnes n'arrivent jamais au récapitulatif** (les macros
   copient des plages fixes) : une 6e personne en Fermentation, une en
   Chaudières + renfort, un « CM Travaux ». Faut-il qu'elles soient dans
   l'application ?

3. **Le jour du remplaçant, quand une demande est acceptée** (formulaire de
   courte durée, 21/10/2026) : faut-il l'écrire tout seul, et avec quoi —
   la pause du demandeur en cellule et « Remplace X » en commentaire, comme
   le classeur ? Un remplacement peut valoir une prime de rappel : tant que
   ce n'est pas dit, l'application ne l'écrit pas, il se pose au planning.
4. **Le quatrième document du dossier** (« RECMA – Demande de congé,
   déclaration », PDF) : à quoi sert-il, faut-il le reprendre ?

## À la RH (d'après les 14 classeurs de fonction)

1. Le solde RTT `64-(n*4)` et le `-4` : que retranche-t-on ? (Le 64 et le
   80 des contremaîtres et adjoints sont expliqués depuis le 30/10/2026 :
   les 8 et 10 jours de RTT des art. 8-2.3 et 8-2.4 du règlement de
   travail, × 8 h. Reste le `-(n*4)` ; une piste : un 4/5 a 6,5 jours de
   RTT sur cinq semaines (art. 8-4.3), soit 52 h = 64 − 3 × 4.)
2. Le DTT `report + 24 + 16` : d'où viennent ces crédits ?
3. « RTT- » (41 fois, du 02 au 10/01) : des RTT de 2025 pris en janvier ?
4. ~~Pourquoi les RHS n'ont-elles aucun compteur ?~~ Réponse dans la note
   du relevé mensuel (30/10/2026) : le compteur vit dans SAP et à la
   pointeuse (« 54 = solde des heures supplémentaires à récupérer »), comme
   le client l'avait dit (« un compteur hors fichier »). À retirer.
5. Les couleurs peintes à la main : jaune, orange (SD26 ?), lavande ?
6. Des erreurs de formule ont été mesurées (un flex time jamais compté,
   un DTT fictif de 224 h…) : la liste est dans `docs/plateforme.md`.

## Écarts connus — aucune question

Ce que les fiches montrent et que le classeur n'écrit pas. Règle du
projet : on ne le corrige pas, on le note.

- VBN : heures sup non écrites le 14/01 (1 h 30) et le 04/04 (0 h 45) ;
  le dimanche 22/03 payé 10 h 17 de nuit au lieu de 8 h ; la durée des
  heures de déplacement des 20/03 et 14/04 ; un chèque-repas de plus ou
  de moins sur quatre mois ; l'arrivée tardive du 30/07 ; les heures sup
  du shut-down payées « pas compenser » en mars et avril (choix fait sur
  le formulaire RH, tranché le 14/10/2026).
- LCI : 1 h sup réellement faite le 17/03 (19/10/2026) ; trois
  chèques-repas d'avril (9 pour 12 journées, sans doute les 11 et 13/04
  payés en heures sup et une demi-journée) ; le 01/01, un week-end de
  2025 hors de l'horaire.

## Deux types de congé le même jour (22/10/2026)

Une demande peut désormais porter deux types de congé le même jour
(« 4h RTT + 4h -FT »). Une fois acceptée, la journée garde le premier code
en annotation ; le second va dans le commentaire. **Comment le classeur
écrit-il un jour à deux codes ?** Une seule annotation, deux, une
écriture combinée ? On aligne la base dès que c'est connu.
