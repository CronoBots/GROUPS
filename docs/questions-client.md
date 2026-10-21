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

1. **Purger l'historique git public** (posée le 26/09/2026) : d'anciennes
   versions de `data/` portent encore des identifiants de connexion et
   quatre prénoms, celles de ce fichier deux numéros de contrat, et `verifier-depot.py --historique` signale des formes
   anciennes. Réécrire l'histoire d'un dépôt public est la décision du
   client ; la procédure est prête dans `docs/purge-historique.md`.
2. **Que compte la ligne « Heure(s) prestée(s) » de la fiche** (posée le
   25/09/2026, `docs/journal/08-verifications.md`) : les heures réellement
   faites, ou le solde du mois contractuel une fois les absences
   retirées ? Aucun montant n'en dépend (la ligne est une quantité, le
   salaire de VBN tombe au centime sans elle) ; elle sert à confronter les
   heures de l'application à celles de la fiche.

3. **« CEP » chez ADK en 2027** (posée le 20/10/2026) : seize journées,
   une par semaine de janvier à juin (le jeudi le plus souvent), écrites
   avec un poste et l'annotation « CEP » (`["PM","CEP"]`), sans
   commentaire, inconnues de 2026 et de la légende. Est-ce le congé-
   éducation payé (des cours, la personne n'est pas au poste) ? Si oui,
   la journée est une absence payée, sans prime de pause. En attendant,
   l'application la lit comme un poste presté, 8 h et la prime.

4. **Un « R-CM » de quelques heures, dans quelle ligne du Planning ?**
   (posée le 20/10/2026) Le Planning range un remplacement de
   contremaître PARTIEL dans la ligne Adjoint — la règle de la prime
   (`remplacementCM`, journée entière seulement) sert aussi au rangement.
   C'est le cas de VGG le 05/06 (« R-CM, remplace ATA de 10h à 14h ») et le 30/06,
   FPA le 19/09 (« remplace FLI de 0h à 6h »), JBI le 21/08 (« R-CM,
   4h +FT, remplace YPE », GPS faisant 18h-22h). Faut-il les montrer dans
   la ligne Contremaître, à côté du titulaire, avec leurs heures ? La prime
   ne change pas.

## À la RH

Le client, le 14/10/2026 : « garde la question pour RH ».

5. **Le mois où le fixe change** (VBN, contremaître au 15/09) : comment
   partager le mois entre les deux fixes, par demi-mois ou par jours de
   calendrier ? Et à signaler : la fiche de septembre paie la hausse dès le
   15/08 (« le RH a fait une erreur »). Voir `docs/regles-paie.md`.
6. **La maladie** : le « premier mois » payé par l'employeur vaut-il
   30 jours calendrier (`MALADIE_EMPLOYEUR_J`) ? Comment le fixe d'un
   employé est-il réduit au-delà — au taux horaire, en jours, au prorata ?
7. **La nuit de 12 h « 18h-06h » d'un ouvrier** (LCI le 20/03) : la fiche
   paie 18 h-22 h à la prime de nuit, l'application à celle de
   l'après-midi (la règle de l'employé, états SAP de VBN). Laquelle pour
   l'ouvrier ?
8. **La RJF d'un ouvrier** (« récupération jour férié ») : payée comme un
   férié (salaire moyen) ou au salaire garanti ? L'application garde le
   garanti.
9. **Le recyclage de neuf personnes** : le « restant » du classeur RH ne
   correspond pas aux objectifs par atelier pour DWS (17 au classeur pour
   27), SBZ (11/26), FLN (7/22), FPS (15/30), PLZ (8/28), PAM (18/10),
   ASS (10/0), PDR (2/0), VBN (30/5). Quel est leur objectif, et sur
   quels ateliers ? Le héros montre en attendant les chiffres du classeur.
10. **Le pécule et le treizième mois des ouvriers** : à quelles dates ?
   (Chez l'employé : mai et juin ; chez l'ouvrier, le pécule vient de la
   caisse de vacances.) Voir `docs/regles-paie.md`, « Reste ouvert ».

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

1. Le solde RTT `64-(n*4)` et le `-4` : que retranche-t-on ?
2. Le DTT `report + 24 + 16` : d'où viennent ces crédits ?
3. « RTT- » (41 fois, du 02 au 10/01) : des RTT de 2025 pris en janvier ?
4. Pourquoi les RHS n'ont-elles aucun compteur ?
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
