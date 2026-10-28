# BIOWANZE

Simulateur de fiche de paie belge (Groupe S, CP 220) pour les équipes en
pauses de Biowanze. Application web installable, **entièrement contenue dans
`index.html`** — pas de build, pas de dépendances, pas de framework.

## Méthode de travail — à appliquer TOUJOURS

Le client, le 26/09/2026 : « enregistre tout ce que tu viens de faire pour ne
jamais oublier et toujours utiliser la meilleure méthodologie ». Ce qui suit
résume les règles que le journal (`docs/journal/`) démontre, cas par cas. En
cas de doute, c'est le journal qui fait foi.

**Git.** Le client, le 26/09/2026 : « il faut toujours pousser sur main »,
puis le 28/09/2026 : « il ne faut qu'une branche, la main ». On travaille
et on committe directement sur `main`, et on pousse `main` ; aucune autre
branche, aucune pull request sauf demande. Les deux anciennes branches
`claude/…` sont identiques à `main` ou déjà contenues dedans ; le serveur
refuse de les supprimer depuis une session (comme les étiquettes), elles
se suppriment à la main sur GitHub.
**Pas de maquette.** Le client, le 10/10/2026 : « il ne faut pas de
maquette ; toujours poussé sur main, et on optimisera au fur et à mesure ».
On code dans l'application et on pousse.
**Langue.** Le client, le 29/09/2026 : « réponds-moi toujours en
français ». Toutes les réponses au client sont en français, comme
l'interface, les commentaires de code et les messages de commit.
**Dans un conteneur neuf, `git config core.hooksPath .githooks` d'abord** :
le 26/09/2026 un commit est passé avec `verifier-depot.py` à 1, parce que
le crochet n'était pas installé — lire le code de retour ne suffit pas si
la commande est enchaînée avec `;` au lieu de `&&`. En session cloud,
`.claude/hooks/session-start.sh` le fait seul (et installe `playwright-cli`).

**Aucune demande d'autorisation.** Le client, le 18/10/2026 : « il faut
que tu acceptes tout tout seul ». `.claude/settings.json` autorise donc
le terminal, les fichiers, le web, les artefacts et les connecteurs
(Notion, GitHub, Supabase, sessions, Docs). Une session cloud ne lit ce
fichier que si elle n'a qu'un seul dépôt ; le reste se règle par le mode
« Auto » du menu à côté de la zone de saisie, que seul le client peut
choisir. Le 20/10/2026 : « j'aimerais que tu arrêtes de me demander les
permissions, que tu le fasses tout seul ». Ni fenêtre d'autorisation (la
liste de `.claude/settings.json` couvre aussi Gmail et le connecteur des
sessions), ni question de choix : quand plusieurs améliorations se
présentent, on fait celles qu'on recommande, puis on dit ce qui a été fait.
On ne demande que ce que le classeur et le client seuls savent (une règle
de lecture ou de paie), et ce qui reviendrait sur une décision du client.
Le 21/10/2026, plus net encore : « j'aimerais que tu valides toujours
tout seul et pousser sur Notion et GitHub ; on perd un temps fou car je
ne fais pas attention que tu ne progresses pas tant que je n'ai pas
validé ». **Ne jamais finir un tour sur une question de goût ou de
choix** (« dites-moi lesquels appliquer ») : trancher selon la
recommandation, l'appliquer, la vérifier, committer, pousser sur `main`,
reporter dans Notion (SUSPENDU depuis le 22/10/2026 : « arrête de
pousser sur Notion si tu n'arrives pas à approuver tout seul ces
modifications » — aucune écriture Notion tant que le client ne dit pas
que les fenêtres ont disparu), puis DIRE ce qui a été choisi et pourquoi — le
client corrige après coup s'il le veut. Les fenêtres d'autorisation de
la session ne s'effacent que par le mode « Auto » choisi par le client.
**Une question n'est pas un ordre.** Le 23/10/2026, « c'est bien pour
l'agenda scolaire, on est d'accord ? » a été lu comme une demande de
retrait, et le client voulait garder. On répond, on dit ce qui dépasse
la demande, et on ne défait rien qu'il n'ait demandé de défaire.

**Un nouveau classeur arrive.** Une seule commande, jamais les étapes à la
main :

```bash
python3 tools/mettre-a-jour.py /chemin/Recapitulatif.xlsm              # à blanc
python3 tools/mettre-a-jour.py /chemin/Recapitulatif.xlsm --installer
```

**Un classeur par année** (depuis le 20/10/2026, 2026 et 2027 côte à côte).
L'année se lit dans le classeur (onglet « Config », « …-2027 ») : chacun
s'installe dans son `data/horaire-AAAA.json`, une année nouvelle s'ajoute
d'office à `HORAIRE_ANNEES` de `index.html`, et un classeur ne remplace
jamais celui d'une autre année. Les compteurs d'une année ne se lisent que
si le client a dit qu'ils sont fiables (`COMPTEURS_FIABLES`) : ceux de 2027
ne l'étaient pas à la réception.

**Le classeur RH des recyclages** (« Suivi des recyclages sur poste de
production », `.xlsx`) a la sienne, même démarche, onze portes :

```bash
python3 tools/mettre-a-jour-recyclage.py /chemin/Suivi_recyclages.xlsx              # à blanc
python3 tools/mettre-a-jour-recyclage.py /chemin/Suivi_recyclages.xlsx --installer
```

Durées mesurées le 09/10/2026 : horaire **22 s à blanc, 0 s pour
`--installer`** (il reprend le passage à blanc réussi), recyclages **moins
d'une seconde**. Si c'est nettement plus long, quelque chose a régressé :
voir « Huit portes, et vite » dans
`docs/journal/02-mises-a-jour.md`.

Les deux sources restent HORS du dépôt. On LIT le rapport de comparaison, on dit au
client ce qui a bougé, on teste au navigateur, on committe. Si une porte se
ferme, on comprend pourquoi avant de toucher à quoi que ce soit : la
contourner, c'est rouvrir le trou qu'elle ferme.

**Avant chaque commit**, selon ce qui a été touché :

| Touché | À relancer, et le résultat exigé |
|---|---|
| tout | `python3 tools/verifier-depot.py` → 0 ; fichier neuf : `git add -N` d'abord, sinon il est invisible |
| `index.html` | `node --check` sur les scripts extraits ; `V` +1 dans `sw.js` ; `node tools/parcours.js` → 0 (chaque onglet, rôle et écran — portrait, iPhone simulé, couché, PC — puis hors ligne ; 4 min, `--vite` pour le seul portrait) |
| lecture de l'horaire, placement, `index.html` | `node tools/verifier-calendrier.js` (neuf règles à 0), `--manques 0926`, `--polyvalence`, `--compteurs` : **sorties comparées à l'octet avec celles d'avant** ; `python3 tools/comparer-fiches.py VBN` |
| placement, `data/` | `node tools/verifier-calendrier.js --manques-commentes` → 0 : aucune place vide, d'aujourd'hui au 31/12, dont un commentaire du jour nomme le titulaire absent (les commentaires d'abord) |
| outils de `tools/` touchant `data/` | `mettre-a-jour.py` à blanc doit reproduire `data/` à l'octet, ou ne changer QUE ce qui est voulu |
| `data/` | `python3 tools/verifier-integralite.py` → 0 ; `verifier-anonymat.py` → 0 |
| congés scolaires (`FWB_ARRETES`, `fwbAn`) | `node tools/verifier-conges-scolaires.js` → 0 ; une année parue, le robot l'ajoute seul (`conges-auto.js`) |
| lecture de l'horaire dans `index.html`, `data/` | `node tools/verifier-calendrier.js --agendas cal` : ne doit changer que ce qui est voulu |

**Mesurer avant, mesurer après, et prouver que rien d'autre n'a bougé.** Un
chiffre inchangé ne prouve rien tant qu'on n'a pas montré que le mécanisme
mord : on sabote une copie et on vérifie que le contrôle crie (voir les
épreuves de `verifier-integralite.py`, de l'exporteur, des polyvalences qui
se terminent). Un contrôle qui ne peut pas échouer ne contrôle rien, et un
contrôle qui échoue toujours ne se lit plus : **le code de retour ne porte
que ce qui est une faute**.

**Le classeur est la SEULE source de l'application.** Le client, le
27/09/2026 : « les indications dans le classeur ne seront jamais faites
autrement, ce n'est pas moi qui les gère », puis « il faut se débrouiller
avec le classeur ; les fiches de paye et relevés sont juste là pour
vérifier que le programme est bien fait ». Une règle se tire donc du
classeur tel qu'il est écrit, fautes de frappe comprises — jamais d'une
écriture qu'on voudrait lui voir adopter, ni d'une table recopiée des
relevés. Ce que le classeur ne dit pas, et que seule une fiche montre,
est un **écart connu**, écrit ici, et non corrigé. Une première réponse du
27/09 l'a oublié : un code lu sur « Abs s/c », que personne n'écrira, a
vécu un commit avant d'être retiré.

**Ne jamais deviner à la place du classeur ni du client.** Quand deux
lectures sont possibles, c'est le classeur qui tranche — les colonnes se
répondent (CHD « Remplace GST » le jour où le commentaire d'un autre le
nomme) — et, s'il se tait, c'est une question au client, écrite dans ce
fichier. **Une correction faite à la main peut être fausse** : l'une des
quatre du 25/09 l'était.

**Les commentaires d'abord, avant toute question.** Le client, le
26/09/2026 : « surtout les commentaires, ce sont les plus importants et ça
résout presque toutes tes questions ». Il venait de le prouver : les 19-20
et le 30/08 de VBN, même cellule, deux primes — la réponse était « échange
avec VBN », écrit dans la colonne d'un COLLÈGUE. Avant de poser une
question : (1) le commentaire de la journée, (2) ceux de TOUS les autres
le même jour qui nomment la personne (« remplace X », « échange avec X »,
« remplacé par X »), (3) le brut `data/classeur-2026-brut.json`, barré
compris. Ne demander que si les trois se taisent — et le dire.

**Deux copies d'une même règle divergent, et c'est la seconde qui reste en
arrière** — sauf pour les motifs de NOMS, où deux outils qui ne s'empruntent
rien sont justement le contrôle.

**Rien d'identifiant dans le dépôt public** : ni nom, ni prénom, ni
identifiant de connexion, ni montant de salaire — y compris dans un
commentaire ou comme exemple (`Nom, Prénom`, `RT0xxxx`). Dans le terminal on
peut voir des noms ; on ne les recopie jamais dans un fichier, un commit ou
un message au client.

**Un audit large se fait en parallèle, et chaque constat est remesuré par un
sceptique** avant d'être cru : l'audit du 26/09/2026 a ainsi trouvé qu'un
constat « barré = annulé » avait été mesuré sur une copie corrompue, et
qu'un correctif proposé aurait attribué 460 signatures au mauvais homonyme.

**« Optimise tout » veut dire TOUT, en une passe.** Le client, le
16/10/2026 : « comment cela se fait que je dois te demander de refaire point
par point alors que je t'avais déjà demandé de faire cela avant ». Sa
demande de refondre tout l'Accueil avait reçu des déplacements et des
fusions de cadres ; les blocs eux-mêmes n'étaient pas repris, et il a fallu
quatre demandes de plus. Quand le client demande de tout optimiser :
(1) photographier la page entière à 320, 390 et 1280 px ; (2) dresser
SOI-MÊME la liste de chaque défaut, bloc par bloc : redites, ordre,
légendes, vides, troncatures, style hétérogène ; (3) tout corriger avant de
rendre la main ; (4) dire ce qui reste, et pourquoi.

**Écrire ce qui a été appris dans le journal**, `docs/journal/`, dans le
fichier et la section qui en parlent, avec la date, la mesure et l'erreur
commise s'il y en a eu une. Une affirmation démentie par la mesure se
CORRIGE sur place, en disant qu'elle était fausse. **Ce fichier-ci ne
reçoit que des RÈGLES** qui valent pour toute session — jamais le récit
d'un changement.

**Les questions ouvertes au client** sont dans `docs/questions-client.md`.
Quand il répond, on applique, on mesure, et on retire la question de la
liste.

**Le dossier Notion** (le client, le 18/10/2026 : « optimise au maximum ce
git avec le connecteur Notion, du travail de professionnel »). Une page
privée de son espace Notion, « BIOWANZE · Dossier projet », en donne la
vue d'ensemble : état du projet, règles, guide de l'application,
procédures, architecture, synthèse des règles de lecture et de paie, et
trois bases — « Suivi — questions et écarts » (questions client et RH,
écarts connus, chantiers, avec statut), « Journal des versions » (du
22/09 à aujourd'hui) et « Décisions du client » (la décision, sa date,
son domaine et son effet dans l'application) — et une liste « Démarrer
une session de travail ». Le dépôt reste la source de vérité : une
décision s'écrit d'abord dans le dépôt (le journal, et ce fichier si c'est une règle), puis se reporte dans Notion (base
Décisions, statut du suivi, ligne du journal) par le connecteur. Notion suit la même règle que le dépôt : ni nom, ni montant
de salaire, ni identifiant de connexion.

## Le journal, et pourquoi ce fichier est court

Le client, le 18/10/2026 : « il faut absolument trouver une solution pour
le contexte et les tokens, cela va beaucoup trop vite et compresse toutes
les 15 min ». Ce fichier pesait **598 Ko, environ 150 000 jetons**, rechargé
en entier à chaque session et après chaque compression : il remplissait à
lui seul la moitié du contexte. Tout l'historique a été déplacé MOT POUR MOT
(vérifié ligne par ligne, aucune perdue) dans `docs/journal/` ; ne restent
ici que les règles, les commandes et la structure. **Ne jamais le laisser
regrossir** : au-delà de 25 Ko, déplacer dans le journal.

| Fichier | Ce qu'il raconte |
|---|---|
| `docs/journal/01-anonymat.md` | anonymiseur, second contrôle, prénoms passés, garde-fou du dépôt |
| `docs/journal/02-mises-a-jour.md` | nouveau classeur en une commande, huit portes, mise à jour automatique (e-mail, base Supabase, notifications), recyclages, cycles prolongés |
| `docs/journal/03-extraction-et-audit.md` | convertisseur, export entier, intégralité, audit du 26/09, barré, grèves, RHS, réponses du 29/09 |
| `docs/journal/04-fiches-et-paie.md` | fiches de paie, relevés, notes de service, états SAP, relevé de prestations |
| `docs/journal/05-interface.md` | barre du haut, thème, téléphone, menu, Accueil, héros, mois, compteurs, Planning, agenda |
| `docs/journal/06-effectifs-et-recherche.md` | congé, absence, recherche, sous-effectifs, rappels évitables, classeurs reçus un par un, renforts |
| `docs/journal/07-onglets-et-divers.md` | personne par défaut, versements, onglets Équipe et Recyclage, intérimaires, valeurs communes |
| `docs/journal/08-verifications.md` | vérificateur du calendrier, mémos, manques, polyvalence, compteurs |
| `docs/questions-client.md` | questions ouvertes au client et à la RH |
| `docs/conversion-horaire.md`, `docs/regles-paie.md` | les règles de lecture et de paie (sources de vérité) |

**Économiser le contexte, à chaque session** :

- chercher dans le journal avec `grep -n` puis lire la seule section utile
  (`sed -n a,bp`), jamais un fichier entier — certains font 160 Ko ;
- `index.html` fait plusieurs Mo : `grep -n` puis lire 30 à 80 lignes ;
- les sorties longues (vérificateur, `mettre-a-jour.py`, Playwright) se
  filtrent (`| tail`, `| grep`) ou se comparent par `diff` / `cmp`, sans
  être imprimées ;
- une capture d'écran coûte cher : en regarder deux ou trois (320 px et le
  cas modifié), et faire mesurer le reste par le script (débordements,
  erreurs) plutôt que de tout afficher ;
- une recherche large passe par un sous-agent, qui ne rend que sa
  conclusion.

## Avant de toucher à l'horaire d'équipe

**Lis `docs/conversion-horaire.md`** — et `docs/regles-paie.md` avant de
toucher au calcul de la fiche. Il contient toutes les règles de lecture
d'une cellule d'horaire, établies avec le client cellule par cellule. Le code
de `parseHoraireEntry()` les applique ; le document est la source de vérité.

La règle qu'il ne faut jamais perdre de vue :

> Dans une cellule, le code franc est le poste **prévu** par la rotation ;
> l'annotation à sa droite et le commentaire Excel disent ce qui a été
> **réellement presté**. Le commentaire prime.

Une journée du JSON est un tableau de trois champs, les vides étant coupés :
`["18h-06h", "R-CM", "Remplace FLI de 18h à 22h Rappel le 13/04"]` — la
cellule, son annotation, le commentaire.

Le document liste aussi ce qui reste à faire confirmer par le client — ne pas
deviner à sa place sur ces points : ils touchent à des montants.

## Structure

| Fichier | Rôle |
|---|---|
| `index.html` | toute l'application (HTML, CSS, JS dans une IIFE) |
| `data/horaire-AAAA.json` | horaire d'équipe anonymisé d'une année (2026, 2027), pour le pré-remplissage |
| `data/classeur-AAAA-brut.json` | le classeur ENTIER en JSON — réserve, non chargée par l'application, hors dépôt |
| `tools/anonymiser-classeur.py` | recopie le classeur en remplaçant les noms par les trigrammes |
| `tools/anonymiser-classeur.ps1` | le même, en PowerShell, pour les postes sans Python |
| `tools/verifier-anonymat.py` | cherche les noms de la source dans la sortie, sans rien emprunter à l'anonymiseur |
| `tools/verifier-depot.py` | cherche des formes de nom dans le dépôt lui-même, arbre et historique |
| `tools/formes-admises.txt` | les formes de nom qu'un humain a regardées et jugées innocentes |
| `tools/survivants-admis.txt` | les survivants de `verifier-anonymat.py` qu'un humain a lus et jugés innocents |
| `tools/mettre-a-jour.py` | toute la procédure en une commande, derrière huit portes |
| `tools/envoyer-push.js` | la notification du téléphone à chaque classeur installé |
| `tools/horaire-auto.py` | la mise à jour sans personne au clavier, lancée chaque heure par GitHub |
| `tools/base-synchro.py` | recopie l'horaire installé dans la base BIOWANZE (étape 2), quand sa version diffère |
| `tools/base-sauvegarde.py` | la sauvegarde quotidienne de la base, chiffrée par la clé du robot, envoyée à sa boîte Gmail (30 gardées) ; la commande de restauration est en tête du fichier |
| `base/*.sql` | la structure de la base BIOWANZE (schéma `biowanze` du projet de base de données de PINO) — jamais de données ; `06-domaines.sql` touche `auth.users`, commune à tout le projet |
| `convertir-horaire.py --identites=F` | noms, prénoms et matricules pour la base seule : `F` doit être HORS du dépôt (l'outil refuse sinon) ; le robot l'envoie (`base-synchro.py --identites=F`) puis l'efface |
| `base/email-code.html` | le modèle de l'e-mail du code de connexion, à coller dans Supabase (« Magic Link » et « Confirm signup ») |
| `tools/mettre-a-jour-recyclage.py` | le classeur RH des recyclages, même démarche, onze portes |
| `tools/convertir-horaire.py` | convertit le récapitulatif Excel en JSON |
| `tools/exporter-classeur.py` | recopie TOUT le classeur anonymisé en JSON, sans rien interpréter |
| `tools/verifier-integralite.py` | confronte l'horaire au classeur entier : ce qui ne lui arrive pas |
| `tools/comparer-horaire.py` | dit ce qui change entre deux versions converties |
| `tools/comparer-fiches.py` | confronte les fiches de paie à ce que l'horaire produit |
| `tools/extraire-fiches.py` | recopie toute une fiche de paie en JSON, sans rien d'identifiant — sortie hors du dépôt |
| `cal/<id>.ics` | l'abonnement agenda de chacun, écrit par `verifier-calendrier.js --agendas` ; avec lui `cal/conges-scolaires.ics`, les congés scolaires de la Fédération Wallonie-Bruxelles |
| `tools/verifier-conges-scolaires.js` | confronte le calcul des congés scolaires (décret du 31/03/2022) aux arrêtés publiés |
| `tools/conges-auto.js` | relit enseignement.be le 1er de chaque mois (`conges-scolaires.yml`) ; une année nouvelle n'entre que recoupée avec le décret |
| `tools/verifier-calendrier.js` | vérifie le calendrier, les compteurs et les manques d'effectif |
| `tools/parcours.js` | le parcours de l'application au navigateur, rôles et écrans, hors ligne compris ; code 1 à la moindre faute |
| `tools/anonymiser-sommaire.py` | repeint le nom, le matricule et la section d'un relevé de pointage scanné, trigramme à la place |
| `.claude/hooks/session-start.sh` | démarrage d'une session cloud : crochet git, `playwright-cli` 0.1.22 et sa configuration |
| `.claude/skills/` | skills tiers relus avant d'entrer (journal 01), hors du garde-fou (`TIERS`) |
| `tools/qr-installer.py` | écrit `qr-installer.svg`, le QR code du guide d'installation (`#installer`) |
| `tools/lire-pdf.py` | extrait le texte d'un PDF, sans dépendance |
| `docs/conversion-horaire.md` | les règles de lecture de l'horaire |
| `docs/journal/` | l'historique du projet, daté et mesuré (voir « Le journal ») |
| `docs/questions-client.md` | les questions ouvertes au client et à la RH |
| `docs/regles-paie.md` | les règles de calcul confirmées par le client |
| `docs/plateforme.md` | l'inventaire du classeur (macros, codes, commentaires, pied) et la plateforme qui le remplace, module par module |
| `sw.js` | cache et fonctionnement hors ligne |
| `logo.png` | le logo Biowanze, source des icônes — ne sert pas à l'application |
| `banniere.jpg` | la couverture du héros de l'Accueil, tirée de `banniere-biowanze-usine.png` |

## Conventions

- **Français** partout : interface, commentaires de code, messages de commit.
- **ES5**, `var`, pas de fonctions fléchées — le fichier vise aussi des
  navigateurs anciens et n'est pas transpilé.
- Aucun barème n'est figé : tout est modifiable dans l'onglet « Barèmes ».
- Les données de l'utilisateur ne quittent jamais l'appareil.
- **Aucun nom complet** dans le dépôt : l'horaire n'identifie les gens que par
  initiales ou matricule. **Y compris dans un commentaire, y compris comme
  EXEMPLE.** Neuf noms réels ont vécu des jours dans ce dépôt public, cités
  pour illustrer les motifs de l'anonymiseur — dans `CLAUDE.md` et dans
  quatre outils — pendant que ces mêmes outils étaient écrits pour les
  retirer du classeur. Rien n'était fonctionnel, aucune liste codée : que
  des commentaires, et c'était tout aussi public. Les exemples s'écrivent
  désormais avec des marqueurs — « Nom, Prénom », « NOM, PRÉNOM »,
  « Renard P » donne PRD — qui illustrent la FORME sans nommer personne.
  Le classeur et le JSON passent par l'anonymiseur et son second contrôle ;
  **le reste du dépôt n'avait, lui, aucun garde-fou** — une règle écrite
  ici, et rien pour la faire respecter. Il en a un : `tools/verifier-depot.py`, voir
  `docs/journal/01-anonymat.md`, « Le dépôt se contrôle lui-même ».

## Après avoir modifié `index.html`

1. Vérifier la syntaxe : extraire le contenu des balises `<script>` et lancer
   `node --check`.
2. **Incrémenter `V` dans `sw.js`** (`nfdm-vNN`). Sans ça, les installations
   existantes gardent l'ancienne page indéfiniment.

   Depuis `nfdm-v119`, la PAGE se prend **au réseau d'abord** : une version
   poussée arrive au premier rechargement, et non au deuxième comme avant.
   L'horaire JSON aussi, depuis `nfdm-v837` (`jsonFrais()`, revalidé, le
   cache au-delà de 4 s ou hors ligne) : au cache d'abord, la première
   ouverture après une mise à jour montrait l'ancien. Icônes et polices,
   au cache. Hors ligne, tout retombe sur le cache — vérifié à
   chaque fois avec Playwright en mode `setOffline(true)`.

   **Et l'application installée se met à jour sans être fermée**, depuis
   `nfdm-v356`. Le client, le 30/09/2026 : « l'app PWA ne se met pas à
   jour ? ». Le site en ligne était bien à jour ; deux choses bloquaient
   le téléphone. GitHub Pages sert tout en `max-age=600`, et le « réseau
   d'abord » rendait donc jusqu'à dix minutes la page du cache HTTP : la
   page et le rafraîchissement de l'horaire se demandent désormais en
   `cache:"no-cache"` (revalidation, 304 si rien n'a changé). Surtout, une
   PWA sur l'écran d'accueil n'est presque jamais RECHARGÉE : le téléphone
   la ressort de sa mémoire, le navigateur ne cherche pas de nouveau
   `sw.js`, et la page affichée reste l'ancienne. La page redemande donc
   `sw.js` (`reg.update()`, `updateViaCache:"none"`) à chaque retour au
   premier plan et toutes les trente minutes, et se recharge UNE fois
   quand le nouveau service worker prend la main (`controllerchange`) —
   jamais au tout premier lancement. Éprouvé : application ouverte, `V`
   changé sur le serveur, retour au premier plan simulé → la page se
   recharge seule sur le nouveau cache, puis tient hors ligne.
   **Mais pas à l'ouverture**, depuis `nfdm-v604`. Le client, le
   09/10/2026 : « il y a toujours un double chargement lors de
   l'ouverture de l'app ». La page étant prise au réseau d'abord, elle
   arrive DÉJÀ neuve à l'ouverture qui suit une mise à jour ; puis
   l'enregistrement trouvait le nouveau `sw.js`, et `controllerchange`
   la rechargeait pour rien — à chaque `V` poussé, donc presque à chaque
   ouverture. Reproduit au navigateur : deux navigations. On ne recharge
   plus que si la page peut être ancienne : chargée hors ligne (servie
   par le cache), ou ouverte depuis plus de 15 s quand `verifier()` (retour
   au premier plan, demi-heure) trouve la mise à jour. Éprouvé : ouverture
   après une mise à jour, 1 navigation (2 avant) ; application ouverte
   puis mise à jour au retour au premier plan, 1 rechargement ; page
   chargée hors ligne puis réseau revenu, 1 rechargement.
3. Tester dans un navigateur, pas seulement en unitaire. **Une mise en
   page de téléphone se mesure AUSSI avec les zones protégées de l'iPhone
   simulées** (dans les `<style>` de la page, `env(safe-area-inset-top)` →
   59 px, `-bottom` → 34 px) : Chromium n'en a pas, et le 26/10/2026 un
   cadre juste au navigateur était faux de 59 px sur l'iPhone
   (`docs/journal/05-interface.md`). Playwright et
   Chromium sont disponibles ; servir le dossier (`npx http-server`) puis
   piloter la page. Le script étant dans une IIFE, rien n'est accessible
   depuis `page.evaluate` : il faut passer par l'interface.

