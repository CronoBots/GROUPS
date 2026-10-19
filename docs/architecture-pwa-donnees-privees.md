# Architecture cible : PWA publique, horaires protégés

## Objectif

Conserver l'installation PWA, l'URL publique, le manifeste, le shell HTML/CSS/JS et les ressources statiques sur GitHub Pages. Ne pas rendre le dépôt privé : cela casserait ou compliquerait la distribution actuelle.

Le point à corriger est la publication des données d'équipe, pas le caractère public du shell de l'application.

## Constat

Les fichiers d'horaires et calendriers publiés dans ce dépôt sont récupérables directement, même si l'interface masque certaines vues. Un code RH embarqué dans le JavaScript ne peut pas protéger des données livrées au navigateur.

## Architecture recommandée

1. **Shell PWA public** : conserver GitHub Pages pour `index.html`, le manifeste, les icônes, les polices et le service worker.
2. **API de données protégée** : servir les horaires individuels et les vues RH depuis un backend avec authentification et contrôle d'accès appliqués côté serveur.
3. **Séparation des données** : ne laisser dans le dépôt public que les données explicitement approuvées pour une publication publique. Ne pas simplement déplacer les fichiers tout en laissant une copie accessible dans Git.
4. **Autorisations minimales** : les utilisateurs authentifiés ne reçoivent que les horaires et opérations nécessaires à leur rôle. Les vues RH doivent être contrôlées par le backend, pas par un booléen local.
5. **Mode hors ligne explicite** : après authentification, la PWA peut conserver une copie locale si le métier l'exige. Documenter que les données en cache restent accessibles sur l'appareil et définir une durée de conservation, une déconnexion qui purge les données sensibles et une politique adaptée aux appareils partagés. Ne pas mettre les réponses privées dans un cache partagé ou public.
6. **Notifications** : vérifier séparément les politiques du fournisseur distant et limiter les données envoyées aux seules informations nécessaires.

## Migration sans casser la PWA

- Étape A — inventorier toutes les lectures des fichiers `data/` et `cal/`, les vues RH, les notifications et les usages hors ligne.
- Étape B — choisir/configurer le backend et les fournisseurs d'identité; créer des environnements de test et de production distincts.
- Étape C — définir les rôles et les règles d'accès côté serveur, puis tester les refus d'accès et les journaux.
- Étape D — adapter le chargement de données avec un mode de compatibilité temporaire et des tests d'intégration.
- Étape E — vérifier l'installation PWA, les mises à jour, la déconnexion, le cache, les appareils partagés et le mode hors ligne.
- Étape F — retirer les fichiers privés du dépôt public et de la publication Pages uniquement après validation de la nouvelle source et préparation de la gestion de l'historique/cache.
- Étape G — contrôler le contenu du dépôt, les artefacts, les caches et les copies historiques. Une suppression Git ne garantit pas l'effacement des copies déjà téléchargées.

## Critères d'acceptation

- Le shell PWA s'installe toujours depuis l'URL publique actuelle.
- Sans session valide, l'API ne révèle aucun horaire individuel ni donnée RH.
- Changer le stockage local, le rôle côté client ou l'URL d'une requête ne permet pas d'obtenir des données non autorisées.
- Les calendriers et les réponses API privées ne sont pas publiés dans le dépôt ou servis depuis une URL publique.
- Le mode hors ligne, la déconnexion et la purge locale ont des tests automatisés et des tests sur appareils réels.
- Les règles métier et les calculs existants restent inchangés.

## Décision requise avant l'implémentation

Choisir le backend et le fournisseur d'authentification disponibles pour l'organisation, puis valider la politique d'accès : horaires individuels, vues RH, calendriers exportables et durée d'accès hors ligne. La présence de clés publiques dans le code client n'est pas en soi un secret; les règles d'accès et les opérations privilégiées doivent être appliquées par le serveur.
