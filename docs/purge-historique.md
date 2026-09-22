# Purge de l'historique — faite le 22/09/2026, à terminer côté GitHub

## Ce qui a été purgé

**Six noms complets.** Deux versions de `data/classeur-2026.xlsx` étaient
passées avant que l'anonymiseur ne sache lire la ligne des noms. Six
personnes, absentes de la feuille « Personnel » comme des colonnes
nom/prénom de « Polyvalence », n'y avaient pas été remplacées.

| Empreinte du blob | État |
|---|---|
| `fee9c67387738271d045d5845dcdfe6ae71eab5a` | ⚠️ retiré de l'historique |
| `78e254a277df47a2f4f00720bb26c38bcb05fd79` | ⚠️ retiré de l'historique |
| `dc31569…`, `19cead6…`, `4f409d0…` | ✅ propres, conservés |

**Les montants de salaire.** `docs/regles-paie.md` a porté, du 20 au 22
septembre 2026, la rémunération fixe de VBN mois par mois, son salaire
horaire à quatre décimales, son treizième mois, son double pécule, l'avance
mensuelle et le montant repris après l'incident de février. Vingt-cinq
chaînes remplacées par « (montant retiré) » dans tous les commits.

## Comment

```bash
pip install git-filter-repo
git bundle create /tmp/avant-purge.bundle --all          # filet de sécurité
git filter-repo --strip-blobs-with-ids /tmp/blobs-sales.txt \
                --replace-text /tmp/montants.txt --force
git remote add origin https://github.com/CronoBots/GROUPS
git push --force origin travail:main
git push --force origin travail:claude/zen-bell-pfx7el
```

## Ce qui a été vérifié

- **L'arbre de HEAD est inchangé**, empreinte pour empreinte
  (`d2d472a739330486171fbd86f2bcf7aa6a96bc1e` avant comme après) : la purge
  n'a touché à aucun fichier courant.
- Les deux blobs sales ne sont plus atteignables — `git cat-file -e` échoue.
- Aucun des vingt-cinq montants ne subsiste dans aucun commit
  (`git log --all -S`).
- `raw.githubusercontent.com` sur `main` ne les sert plus.
- Le site répond, la version servie est la bonne.

## Ce qui reste, et ce n'est pas un détail

**GitHub sert encore les anciens commits par leur empreinte.** Vérifié le
22/09/2026 : trois anciennes empreintes répondent `HTTP 200` et le document
qu'elles servent porte encore les montants.

Et ces empreintes ne sont pas secrètes : l'API d'évènements publics de
GitHub publie les SHA de chaque poussée sur un dépôt public, et ces
évènements sont archivés par des tiers.

Deux remèdes, et un seul est complet :

1. **Demander au support GitHub** de passer le ramasse-miettes sur le dépôt
   et de purger les vues en cache, en citant les anciennes empreintes.
   C'est la voie normale ; elle demande quelques jours.
2. **Supprimer le dépôt et le recréer** à partir de l'historique réécrit.
   Immédiat et sans reste, mais fait disparaître les issues, les étoiles et
   les forks s'il y en a.

Tant que l'un des deux n'est pas fait, **la purge n'est qu'à moitié faite**.

## Une seconde fuite, le 22/09/2026 : des noms, cette fois

Découverte en allant lire le classeur brut pour vérifier une journée — pas
par un contrôle, ce qui est le vrai enseignement.

| Fichier | Ce qu'il portait |
|---|---|
| `data/classeur-2026.xlsx` | **20 912 occurrences**, neuf personnes — les auteurs des commentaires Excel |
| `data/horaire-2026.json` | **36 occurrences** dans 22 champs — signatures non coupées, et quatre prénoms écrits au milieu d'une phrase |

Les deux fichiers avaient des restes **différents** : le JSON est converti
depuis le classeur source, pas depuis la copie anonymisée. Chacun a donc été
nettoyé chez lui.

Nettoyés dans l'arbre courant par le commit `265d521`. Les deux outils ont
été corrigés ensuite — l'anonymiseur lit maintenant la structure des
commentaires, et le contrôle indépendant sait enfin voir une signature.

**Le même reste demeure, et il est maintenant double** : GitHub sert encore
les anciens commits par leur empreinte, et ces empreintes-là portent des
noms de personnes en plus des montants. Les deux remèdes ci-dessous valent
pour les deux fuites, et le second est toujours le seul complet.

## La leçon, qui vaut plus que la purge

Rien de tout cela n'aurait eu lieu si la règle avait été écrite avant — et
pour les noms, la règle ÉTAIT écrite depuis le début. Elle ne suffisait pas :
il y avait un outil pour l'appliquer et un second pour la vérifier, et les
deux ont répondu « c'est propre » sur un fichier qui portait neuf noms.
**Un contrôle qu'on n'a jamais mis à l'épreuve sur un cas connu n'est pas un
contrôle.** Les deux le sont désormais, dans les deux sens : sur le fichier
qui fuyait, et sur le fichier nettoyé.
Elle l'est maintenant, dans `CLAUDE.md` sous « Conventions » : aucun nom
complet, **et aucun montant de salaire**. Le dépôt est public — `docs/` se
lit sans authentification, par le site comme par `raw.githubusercontent.com`.
