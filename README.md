# Net de fin de mois

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
automatiquement le mois affiché. Près de 99 % des jours sont reconnus
automatiquement : les codes francs, mais aussi les mentions qui nomment le
poste sans l'encoder (« AM », « N ») ou le désignent par une plage horaire
connue (6h-14h le matin, 7h-15h et l'horaire flottant en jour).

Le message de fin distingue deux cas : les jours **à vérifier**, pré-remplis
mais porteurs d'une mention particulière (remplacement, poste déduit d'une
plage horaire), et les jours **non reconnus**, laissés vides et à compléter à
la main. Les jours déjà encodés à la main ne sont jamais écrasés.

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

## Licence

Usage personnel.
