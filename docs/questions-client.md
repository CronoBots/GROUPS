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

1. **Les 51 matricules** de « Polyvalence » vivent dans le dépôt public,
   à côté du trigramme. `CLAUDE.md` les tolère (« initiales ou
   matricule ») ; s'ils figurent sur les fiches de paie, ils relient le
   trigramme à la personne. Les retirer ?
2. **Purger l'historique git public** (posée le 26/09/2026) : d'anciennes
   versions de `data/` portent encore des identifiants de connexion et
   quatre prénoms, et `verifier-depot.py --historique` signale des formes
   anciennes. Réécrire l'histoire d'un dépôt public est la décision du
   client ; la procédure est prête dans `docs/purge-historique.md`.
3. **Que compte la ligne « Heure(s) prestée(s) » de la fiche** (posée le
   25/09/2026, `docs/journal/08-verifications.md`) : les heures réellement
   faites, ou le solde du mois contractuel une fois les absences
   retirées ? Aucun montant n'en dépend (la ligne est une quantité, le
   salaire de VBN tombe au centime sans elle) ; elle sert à confronter les
   heures de l'application à celles de la fiche.

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
