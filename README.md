# Net de fin de mois

Simulateur de fiche de paie belge (secrétariat social Groupe S, CP 220).
On y saisit l'horaire presté du mois — matin, après-midi, nuit, jour, congés —
et la page reconstitue la fiche ligne par ligne jusqu'au net à recevoir.

Application web installable (PWA) : elle s'installe comme une application,
garde son icône et **fonctionne hors ligne**.

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
automatiquement le mois affiché. Les horaires à heures non standard
(horaire flottant, plages spéciales) ne sont pas reconnus automatiquement
et restent à compléter à la main ; un message indique combien de jours
sont concernés. Les jours déjà encodés à la main ne sont jamais écrasés.

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
