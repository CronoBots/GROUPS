# Nouveaux classeurs, mise à jour automatique, recyclages, cycles prolongés

Historique déplacé tel quel de `CLAUDE.md` le 18/10/2026. Les dates, mesures et erreurs y restent.

## Mettre à jour l'horaire depuis un nouveau classeur

Le client envoie régulièrement le récapitulatif Excel. **Depuis le 26/09/2026,
une seule commande** :

```bash
python3 tools/mettre-a-jour.py /chemin/Recapitulatif.xlsm              # à blanc
python3 tools/mettre-a-jour.py /chemin/Recapitulatif.xlsm --installer
```

Elle enchaîne tout ce qui suit dans un dossier temporaire, derrière **huit
portes** — anonymiseur, second contrôle, **fidélité de la copie à la
source**, convertisseur, export et son aller-retour, intégralité cellule par
cellule, neuf règles dures du calendrier. La première qui se ferme arrête
tout, et rien n'est installé. Elle imprime ensuite le rapport du
comparateur. Avec `--installer`, les trois fichiers de `data/` sont
remplacés ENSEMBLE, `V` est incrémenté, et le garde-fou du dépôt passe sur
le résultat — s'il échoue, les fichiers d'avant reviennent depuis leur
copie. Si rien n'a changé, rien n'est touché, pas même `V`.

**Huit portes, et vite, depuis le 09/10/2026.** Le client : « pourquoi la
mise en place est si longue ? », puis « vérifie et optimise au maximum
cette tâche ». Un passage prenait **environ 4 minutes, et il en fallait
deux** (à blanc, puis `--installer`) ; ce jour-là, deux portes fermées en
ont fait quatre. Mesuré étape par étape, corrigé là où le temps passait,
et **chaque correction prouvée identique à l'octet** sur deux classeurs :

| Étape | Avant | Après | Cause |
|---|---|---|---|
| anonymiseur | 115 s | 16 s | chaque règle de nom balayait tout le XML (18 Mo) ; elle n'est plus essayée qu'au début des mots qui portent son premier mot (un index par partie), et `_sans_accent()` passe par une table |
| convertisseur | 22 s | 4 s | `commentaires()` relue pour chaque colonne-personne (112 fois pour 12 feuilles) : mémoïsée |
| vérificateur du calendrier | 14 s | 1,4 s | `cycleDuMois()` de l'application essayait 504 calages, qui ne font que 77 positions : comptées une fois, parcourues dans le même ordre (l'application s'ouvre plus vite aussi) |
| garde-fou du dépôt | 14 s | 1,4 s | le contrôle croisé cherchait chaque OCCURRENCE de mot dans 18 Mo, et non chaque mot |

Puis l'orchestration : les portes indépendantes tournent **en même temps**
(le convertisseur part du classeur source), leurs comptes rendus
s'impriment dans l'ordre, et la première porte fermée arrête tout comme
avant. Une **huitième porte**, le garde-fou du dépôt sur l'horaire NEUF
(`verifier-depot.py --horaire= --classeur=`), se ferme dès le passage à
blanc — éprouvé en retirant « Débourrage Ligne » des formes admises :
porte 8 fermée, rien d'installé. Et **`--installer` reprend un passage à
blanc réussi** sur le même classeur, avec les mêmes outils et le même
horaire installé (empreintes dans un mémo hors du dépôt), au lieu de le
refaire. **22 s à blanc, 0 s pour l'installation.**

**Et le vérificateur était cassé depuis le 07/10, en silence pour
l'installation** : `--manques` et `--polyvalence` s'arrêtaient sur
`nbPostesTenables`, `RECYC_OFF` et `RECYC_EXEMPT`, ajoutés à `index.html`
sans entrer dans sa découpe. La porte 7 n'emploie que les neuf règles, qui
ne les appellent pas — d'où le silence. Les trois sont dans la découpe.

**La porte de fidélité est celle qui manquait** : hors des zones
nominatives, la copie anonymisée ne doit différer de la source sur aucune
cellule. Elle se ferme sur l'ancienne copie de référence — 480 cellules —
et s'ouvre sur la nouvelle.

**Éprouvée sur le classeur du 26/09/2026** : les sept portes s'ouvrent, et
les trois fichiers produits sont **identiques à l'octet** à ceux de `data/`.
La procédure est donc reproductible de bout en bout, ce qui est la meilleure
preuve qu'elle ne régresse pas.

**Restent à la main** : lire le rapport et dire au client ce qui a bougé,
tester dans un navigateur, committer. Le détail des étapes, pour
comprendre ce que l'outil fait ou le refaire pas à pas :

**Ne jamais écraser l'ancien JSON sans avoir regardé ce qui change.** Le
client renvoie souvent le même classeur corrigé sur quelques journées ; une
journée qui bouge déplace des heures, des primes et parfois un chèque-repas.
Convertir d'abord à côté, comparer, puis installer.

```bash
# 1. convertir À CÔTÉ — le classeur reste HORS du dépôt, il contient des noms
python3 tools/convertir-horaire.py /chemin/Recapitulatif.xlsm \
        /tmp/nouveau.json 2026

# 2. comparer à la version en place, et RENDRE COMPTE de ce qui change
python3 tools/comparer-horaire.py data/horaire-2026.json /tmp/nouveau.json

# 3. installer
cp /tmp/nouveau.json data/horaire-2026.json

# 4. contrôler les repères (section 11 de docs/conversion-horaire.md)
# 5. incrémenter V dans sw.js
# 6. tester dans un navigateur
```

Le comparateur dit tout : date de mise à jour du classeur, arrivées et
départs (une arrivée se faisait TOUJOURS confirmer par le client : qui,
quelle fonction, intérimaire ou non — SLI le 09/10/2026 ne l'a pas été ;
**depuis le 19/10/2026, un nouvel OPÉRATEUR est intérimaire d'office**,
voir « Un nouvel opérateur est toujours un intérimaire »), changements de groupe, journées modifiées avec l'avant et l'après,
compteurs et polyvalence. Il ne manipule que des identifiants à trois
lettres. Sa sortie n'est pas un journal à archiver : **il faut la lire, et
dire au client ce qui a bougé** — c'est lui qui sait si une journée modifiée
est une correction attendue ou une erreur de saisie.

**Le poste tenu est en ligne 9** — établi avec le client, voir la section
9 bis de `docs/conversion-horaire.md`. Le convertisseur ne la lit pas encore ;
c'est le premier chantier ouvert.

Pour regarder ce qui entoure les noms sans rien convertir :

```bash
python3 tools/convertir-horaire.py /chemin/Recapitulatif.xlsm --entetes
```

Il imprime les lignes 5 à 12 de chaque feuille, colonne par colonne, les
noms réduits à leurs initiales.

**Le convertisseur dit maintenant ce qu'il ne reprend pas.** Il ne lisait que
la ligne des noms, les journées et le pied de feuille ; tout le reste tombait
sans un mot — et le poste de travail de chacun était probablement là. Il
compte désormais les cellules qu'il laisse et les annonce, ligne par ligne.
Ces messages se lisent : une perte silencieuse est une perte qu'on ne corrige
jamais.

Il garde aussi, dans le champ `e` de chaque personne, **tout ce qui est écrit
au-dessus de son nom** et entre le nom et la première journée — sans
l'interpréter, comme le reste.

Le convertisseur signale de son côté les anomalies du classeur : trigrammes
partagés, corrections devenues orphelines, compteur écrit dans la mauvaise
colonne. Ces messages vont sur la sortie d'erreur ; ils ne sont pas du bruit.

**Ne jamais committer le `.xlsm`**, ni aucun nom complet. Le convertisseur
n'en laisse pas sortir : identifiants à trois lettres, et commentaires
débarrassés du nom de leur auteur.

**Il a eu le même trou que l'anonymiseur, et le 22/09/2026 il a failli
écrire trois noms complets dans `data/horaire-2026.json`** — fichier d'un
dépôt PUBLIC. Son motif `AUTEUR` exige une virgule : « Nom Prénom : »
lui échappait, « Nom, Prénom/rt0xxxx: » aussi (le suffixe rompt
l'ancrage), et « Prénom: » — un prénom seul — n'a aucune forme
reconnaissable. C'est la COMPARAISON avec la version en place qui l'a
montré, l'ancien JSON portant « (nom retiré) » là où le nouveau écrivait le
prénom.

Il ne devine donc plus la forme d'un nom : `_motif_auteurs()` prend **ceux
qu'Excel déclare dans `<authors>`** pour le fichier de commentaires qu'il
est en train de lire, et les retire où qu'ils soient — nom complet ou mot
isolé. Rien à inférer, rien à rater. La majuscule initiale est exigée :
« Marie » est un nom, « marie » un verbe français.

Ses motifs restent les SIENS, et ne sont pas empruntés à l'anonymiseur :
les deux outils doivent pouvoir se contredire, sans quoi le second ne
vérifie plus, il répète.

Si le nombre de personnes ou de journées s'écarte nettement des repères, la
structure du classeur a bougé — vérifier la ligne des noms (10), la colonne
des jours (2) et les blocs de mois avant d'aller plus loin.

## La mise à jour automatique de l'horaire

Le client, le 16/10/2026 : « que l'horaire soit mis à jour automatiquement
tous les jours ». Son PC de travail est un PC virtuel (application Windows) :
le serveur n'y est visible que par l'Explorateur, et son iPhone n'y a pas
accès. Ni PowerShell, ni droit « Ouvrir une session en tant que tâche ». La
chaîne, montée avec lui ce jour-là :

1. **PC virtuel** : tâche « Copie horaire BIOWANZE » du Planificateur
   (dossier RemoteDesktop), `robocopy` du récapitulatif vers
   `OneDrive\Horaire auto`. Déclencheurs : chaque jour, à l'ouverture de
   session et à la connexion à distance (« N'exécuter que si l'utilisateur
   est connecté » : l'autre option est refusée). robocopy ne recopie que si le
   fichier a changé.
2. **Power Automate** (« Horaire BIOWANZE vers Gmail ») : à chaque
   modification du fichier, Get file content, puis un e-mail « BIOWANZE
   horaire » à son Gmail, classeur en pièce jointe.
3. **GitHub**, chaque heure (`.github/workflows/horaire-auto.yml`,
   `tools/horaire-auto.py`) : le dernier e-mail est lu par IMAP, le classeur
   écrit dans un dossier temporaire, `mettre-a-jour.py` passe les huit
   portes puis installe, pousse sur main ; les e-mails vont à la corbeille et
   le rapport de ce qui change part par e-mail au client.

**Les recyclages suivent le même chemin** (le client, le 16/10/2026 :
« peut-on mettre cela en place pour le fichier des recyclages aussi ? ») :
un dossier OneDrive à eux, un second flux Power Automate, un e-mail
« BIOWANZE recyclage », et `horaire-auto.py` le fait passer par les onze
portes de `mettre-a-jour-recyclage.py --installer`. **Piège évité** : le brut
des recyclages vit hors du dépôt, donc absent sur GitHub, et l'outil
réinstallait (et montait `V`) à chaque passage. Le script regarde si
`data/recyclages-2026.json` a vraiment changé, et remet `sw.js` sinon.
Éprouvé en local sur un clone sans brut : classeur identique, rien ne
bouge, `sw.js` compris ; classeur du 12/10, installé avec son rapport
(JBI, VGG) ; un horaire donné à la place du classeur RH, porte 1 fermée,
rien installé. **Éprouvé en vrai le même jour** : classeur RH du 16/10 à
13 h 45 installé par le commit automatique 6bdf61c (VGG, chaudières le
15/10). Le premier envoi portait le sujet « BIOWANZE horaire », le flux
ayant été copié de celui de l'horaire : porte 1 fermée, rien installé.
D'abord sans notification du téléphone ; le client, le 16/10/2026 :
« je n'ai rien reçu pour le recyclage ». Une notification par passage,
« Recyclages mis à jour », ou « Horaire et recyclages mis à jour » quand
les deux arrivent ensemble. **Puis personnelles**, le même jour (le
client, capture à l'appui : « les notifications doivent être optimisées
au max ») : `notifications()` compare l'avant et l'après et chacun lit ce
qui change POUR LUI — « Votre horaire a été modifié /
Samedi 17/10 : N → Maladie », « Votre recyclage a été ajouté / Jeudi 15/10 :
Chaudières / Encore 9 recyclages à faire » —, et ceux pour qui rien ne change ne reçoivent
RIEN (le client, le même jour : « go » ; avec un classeur par jour, « rien ne
change pour vous » devenait du bruit) — un abonné sans trigramme reconnu
garde le message commun. Le poste d'un OPÉRATEUR suit la pause
(« Mercredi 21/10 : PM → AM · Gluten »), lu dans son agenda `cal/<id>.ics`
que l'installation vient de réécrire : la lecture de l'application, pas une
copie de ses règles ; rien pour un contremaître ou un adjoint.
Exception, le client le même jour : VBN reçoit chaque classeur, horaire et
recyclages, même sans changement pour lui (`TOUJOURS_PREVENIR`). Une journée se décrit par sa cellule et son
annotation, jamais par le commentaire (comme `detecterChangements()`),
une absence entière par son seul mot (Maladie, VA, Flex time repris), une
ligne par journée, jamais regroupée (le client, capture à l'appui : « il ne
faut pas regrouper les jours »), trois au plus puis « + n autres journées ».
Le titre seul : iOS le coupe vers 28 signes (« · 8 j… » sur sa capture).
`envoyer-push.js --messages=` choisit le message par l'identifiant de
l'abonnement, que l'application envoie désormais ENTIER (« GBT-1 ») ;
toucher la notification ouvre l'Accueil ou l'onglet Équipes, y compris
quand l'application est déjà ouverte (message du service worker).
« from BIOWANZE » sous le titre est écrit par iOS pour toute
notification d'une application web : on ne peut pas le retirer.

**Le planificateur de GitHub ne lançait rien** : le 16/10/2026, aucun
passage automatique en plus de deux heures (zéro événement `schedule`, alors
que fichier, branche et action étaient en ordre). Le client : « faisons le
nécessaire ». C'est donc la base Supabase de PINO qui lance l'action :
`pg_cron` (tâche `biowanze-horaire`, toutes les 15 minutes) appelle
`biowanze_lancer_horaire()`, qui envoie un `workflow_dispatch` à GitHub par
`pg_net`. Le jeton GitHub (accès à ce seul dépôt, permission Actions en
écriture) est dans le coffre de la base, secret `biowanze_github`, déposé par
le client lui-même dans l'éditeur SQL : il ne passe ni par le dépôt ni par la
conversation. Sans secret, la fonction ne fait rien. Elle est fermée au
public (appel anonyme : 401). Le cron du fichier `horaire-auto.yml` reste en
secours.

**Le journal d'une action est public** : il ne reçoit que des lignes d'état.
Le compte rendu d'une porte fermée peut contenir le nom qu'une garantie a
trouvé ; il part au client par e-mail, jamais au journal.

**Le robot se répondait à lui-même, et le connecteur Gmail l'a montré**
(18/10/2026 ; le client a connecté Gmail, la boîte de l'application). Le
16/10, après un e-mail portant le classeur RH sous le sujet de l'horaire
(11 h 41), le rapport « BIOWANZE · horaire NON installé » est reparti
**22 fois, toutes les 15 minutes, de 11 h 45 à 16 h 45** : envoyé à la
même adresse, il répondait à la recherche IMAP (Gmail cherche par mots,
« BIOWANZE » et « horaire » y sont), partait à la corbeille faute de
pièce jointe, et un nouveau rapport le remplaçait. Seule l'arrivée d'un
vrai classeur à 16 h 46 a cassé la boucle. `lire_gmail()` écarte
désormais les e-mails de l'adresse du robot (`NOT FROM`) ; la même
recherche dans la boîte (`-from:` l'adresse du robot) ne rend plus que les
cinq envois du classeur. Le journal d'une action restant illisible depuis
la session, **c'est la boîte, par le connecteur Gmail, qui dit
désormais ce que la mise à jour automatique a fait** : rapports reçus,
portes fermées, classeurs arrivés. Aucun classeur n'est arrivé entre le
16/10 à 16 h 46 et le 18/10 au soir (week-end : la tâche du PC virtuel ne
copie qu'à l'ouverture de session).

**Les e-mails obsolètes partent à la corbeille** (le client, le
18/10/2026 : « prévoir la suppression des mails une fois qu'ils sont
obsolètes »). Ceux qui portent un classeur y partaient déjà dès leur
lecture ; les rapports du robot, envoyés à la même adresse, restaient.
`purger_rapports()` met à la corbeille, à chaque passage, ceux de plus de
sept jours, **le plus récent excepté** (dernier état connu) ; Gmail vide
sa corbeille après 30 jours. Éprouvé sur une boîte simulée : quatre
rapports dont trois vieux, les deux plus anciens retirés, le dernier gardé.
Au 18/10, la boîte en porte cinq, tous du 16/10 : rien à retirer avant le
23/10.

**Deux refus de plus qu'à la main** : un horaire identique n'installe rien
(pas même `V`), et une ARRIVÉE n'est installée que si son trigramme est dans
`tools/arrivees-confirmees.txt` — on l'y ajoute quand le client a dit qui
c'est. Secrets du dépôt : `GMAIL_USER`, `GMAIL_APP_PASSWORD`. Éprouvé en
local le 16/10/2026 : horaire identique, horaire changé (122 journées),
arrivée refusée puis acceptée une fois confirmée, porte 1 fermée sans un mot
au journal.

**Éprouvé en vrai le 16/10/2026**, sur l'adresse dédiée `biowanzeapp@gmail.com`
(le client n'a pas voulu mêler son Gmail personnel ; l'Outlook du travail ne
s'ouvre pas sans autorisation du service informatique) : tâche lancée sur le
PC virtuel, e-mail reçu, passage lancé à la main (« Run workflow » — la
session ne peut pas déclencher d'action, 403), réussi en moins d'une minute.
Classeur du 16/10 à 7 h 48 installé par le commit automatique 3db7ba2 :
29 journées chez 7 personnes, 3 compteurs ; garde-fou du dépôt et neuf règles
à zéro relus après coup. Le journal d'une action ne se lit pas depuis la
session (GitHub le sert d'un autre hôte) : l'état se lit au commit et à
l'e-mail de rapport.

**Et le téléphone sonne, application fermée** (le client, le 16/10/2026 :
« une notification PWA lors de la mise à jour du classeur », puis « B tant
que mnt » : la même pour tous). Le 09/10 il l'avait écartée faute de
serveur ; l'action GitHub en tient lieu. Après chaque classeur poussé,
`tools/envoyer-push.js` (Node, `web-push`) envoie « Horaire mis à jour ·
Classeur du … » à chaque abonné ; `sw.js` l'affiche (`push`), un appui
ouvre l'application. **Les abonnements sont dans la base Supabase du projet
PINO**, le choix du client — et non un projet à part, que je recommandais :
table `biowanze_push` (endpoint, clés, trigramme), RLS sans politique, donc
fermée au public ; on n'y entre que par trois fonctions `security definer` :
`biowanze_abonner` et `biowanze_desabonner` (ouvertes, l'adresse doit être
en https), `biowanze_abonnes` qui ne rend la liste qu'à la clé partagée
`PUSH_CLE` (seule son empreinte SHA-256 est dans la base). L'application
s'abonne quand on touche « Activer » dans Réglages (`abonnerPush()`), se
désabonne à « Désactiver », et se réabonne en silence une fois par jour si
c'était déjà actif. Clé publique VAPID écrite dans `index.html` ET
`tools/envoyer-push.js`, la même ; la privée est le secret
`VAPID_PRIVATE_KEY`. Le trigramme est gardé pour, plus tard, ne prévenir que
ceux dont l'horaire change (l'option A). Une notification manquée ne fait
jamais échouer le passage. **Éprouvé** : lecture directe de la table
refusée, adresse non https refusée, liste refusée sans la clé ; un faux
abonné envoyé au vrai service de Google, qui répond « inexistant », est
retiré de la base ; au navigateur, Activer inscrit (clé de 65 octets) et
Désactiver désinscrit, à 320 px (hors ligne avant), 390 et 1280 px ; un
message reçu par le service worker s'affiche. Vérificateur identique à
l'octet. Sur iPhone, seulement pour l'application installée (iOS 16.4 et
plus) : seul le téléphone du client dira si elle sonne.

## Mettre à jour les recyclages depuis le classeur RH

Le client envoie aussi, à part, le classeur RH **« Suivi des recyclages sur
poste de production »** (fichier `.xlsx`, feuille `Suivi Polyvalence`). Il
alimente la colonne des chiffres du tableau « Recyclage des polyvalences »
(`RECYC_OFF` dans `index.html`, servi par `data/recyclages-2026.json`).

**Comme l'horaire, une seule commande, et jamais à la main** :

```bash
python3 tools/mettre-a-jour-recyclage.py /chemin/Suivi_recyclages.xlsx            # à blanc
python3 tools/mettre-a-jour-recyclage.py /chemin/Suivi_recyclages.xlsx --installer
```

**POURQUOI cet outil.** Le 06/10/2026 ce classeur a été lu à la main, et deux
fois de travers : un seul poste sur trois d'abord, puis — corrigé — la colonne
« Contremaître » des adjoints FUSIONNÉE avec « Centrale thermique » (chaudières
à 10 au lieu de 5 + 5 contremaître). Le client, le 07/10/2026 : « mets en place
exactement la même chose que pour l'horaire, et enregistre la marche à suivre
pour ne JAMAIS passer à côté ». La lecture ne se fait donc plus jamais à la
main : elle passe par **six portes** qui auraient arrêté chacune de ces erreurs
— onze depuis le 09/10/2026, voir plus bas.

**Ce que le classeur contient.** La feuille est faite de SECTIONS empilées.
Chaque section a sa ligne d'en-tête (`Nom | Prénom | Degré… | recyclage restant
| <POSTE> …`), puis une ligne `J-1 … J-n` qui donne la **largeur** de chaque
poste (n = l'objectif : 10 pour un opérateur, 5 pour un adjoint), puis les
personnes. Chaque cellule sous un poste porte la **date** d'un recyclage fait ;
le compte d'un poste = le nombre de cellules remplies. **La section des adjoints
porte une colonne de plus, « Contremaître »** — d'où le `cm` du JSON, affiché à
la place de la STEP dans le bloc adjoints du tableau.

**Les six portes**, la première qui se ferme arrête tout : (1) lecture &
structure ; (2) trigrammes connus, uniques, et présents dans l'horaire (même
convention que `convertir-horaire._initiales`) ; (3) **bornes — aucun compte ne
dépasse la largeur de sa colonne** (la porte qui ferme sur chaudières=10 dans
une colonne large de 5) ; (4) intégralité — chaque cellule-date comptée une
fois et une seule ; (5) cohérence — `fait + restant` multiple de 5 ≥ `fait` ;
(6) anonymat — aucun nom dans la sortie. À blanc, l'outil imprime ensuite ce qui
changerait. Avec `--installer`, et seulement si les six portes sont ouvertes :
`data/recyclages-2026.json` est remplacé, le **brut** (`-brut.json`, trigrammes
seuls, hors dépôt via `.gitignore`) est écrit à côté, `V` est incrémenté, le
garde-fou du dépôt passe — sinon tout revient depuis la copie.

**La même démarche d'anonymat et de récupération que l'horaire, depuis le
09/10/2026.** Le client, en envoyant la version du jour : « il faut exactement
la même démarche d'anonymat et de récupération de toutes les infos ». Les six
portes ne lisaient que les comptes de la feuille « Suivi Polyvalence » ; le
reste du classeur — la feuille REGLES, le degré G/H, les formules, la mise en
forme — tombait, et il n'y avait ni copie anonymisée ni contrôle indépendant.
Cinq portes s'ajoutent, sur le modèle de `mettre-a-jour.py` :

- (7) **copie anonymisée** `data/recyclages-2026.xlsx` : l'archive recopiée
  telle quelle, sauf la colonne A des personnes (le trigramme) et la B
  (vidée), leurs chaînes partagées (vidées — sans quoi le nom resterait dans
  `sharedStrings.xml` ; refus si une autre cellule les emploie) et l'auteur
  et le dernier modificateur du document. **Garantie** : l'archive entière
  est relue, un seul mot de nom et la copie est détruite ;
- (8) **second contrôle** : `verifier-anonymat.py` source → copie. Il a
  d'abord fermé sur les quatre noms de poste écrits en capitales (meunerie,
  gluten, fermentation et distillation) : lus et admis dans
  `tools/survivants-admis.txt` ;
- (9) **fidélité** : hors des colonnes de noms, aucune cellule d'aucune
  feuille ne diffère de la source ;
- (10) **export entier** `data/recyclages-2026-classeur.json` par
  `exporter-classeur.py`, avec son aller-retour : 2 feuilles, 544 cellules,
  29 formules, 202 dates, 56 fusions ;
- (11) **intégralité** : l'export, lu par un autre chemin — le trigramme
  ÉCRIT en colonne A de la copie, et non recalculé —, redonne pour chaque
  personne et chaque poste les mêmes comptes ET les mêmes dates que la sortie.

La copie et l'export sont la réserve locale, hors dépôt (`.gitignore`),
comme `classeur-2026.xlsx` et son brut. **Éprouvées** : un mot de nom planté
dans `workbook.xml` fait détruire la copie (7) ; une date décalée d'un jour
dans la copie ferme la fidélité (9) ; une date retirée de l'export, puis une
date changée, ferment l'intégralité (11). Toute la commande prend moins d'une
seconde.

Classeur du 09/10/2026 : onze portes ouvertes, **une seule ligne change** —
GPO, un recyclage de fermentation le 08/10 (2 → 3, restant 19 → 18).

**La date du classeur s'affiche dans Réglages**, cadre « Classeurs », à côté
de celle de l'horaire (le client, le 09/10/2026). Le classeur RH n'écrit
AUCUNE date dans ses cellules : la sienne est celle de son dernier
enregistrement (`dcterms:modified` des propriétés, en UTC), que l'outil
rend à l'heure de Bruxelles dans le `maj` de `data/recyclages-2026.json`.
D'où « enregistré le » à l'écran, et non « du ». Le rapport à blanc dit
aussi quand cette date change.

**Restent à la main** : lire le rapport et dire au client ce qui a bougé, tester
dans un navigateur, committer.

## Après le classeur : les cycles prolongés

Le client, le 09/10/2026 : « pour les horaires après décembre 2026, il faut
continuer le cycle des 5 équipes (5 semaines) et des 6 binômes
(6 semaines) ; je pousserai le classeur 2027 quand il sera disponible, mais
d'ici là les cycles représentent ce que les travailleurs doivent prester ».

`horaireDe(annee)` rend l'horaire du classeur pour son année et, pour toute
année qui le suit, un horaire **projeté** : chaque journée est une cellule
franche seule (`["N"]`, `["-"]`), tirée du cycle de la personne, sans congé,
remplacement ni compteur. Le pré-remplissage (onglets Calendrier et Mon salaire), le
tableau du jour et la barre du haut s'en servent ; les sous-effectifs, les
rappels non nécessaires et les modules congé/absence/recherche restent sur
le classeur. Une ligne « Horaire 2027 prolongé par les cycles » le dit dans
le cadre du mois et dans celui du salaire, et le tableau du jour ajoute
« prolongé par les cycles ».

**Calé sur les 92 derniers jours, et non sur un mois** (`calageLong()`). Sur
un mois, le cycle de 5 semaines EST le début de celui de 6
(`CYCLE5 = CYCLE6.slice(0,35)`), et `cycleDuMois()` hésite : en décembre, la
moitié de l'équipe 2 sortait en « 6 semaines ». Sur trois mois, mesuré le
09/10/2026 : les 11 contremaîtres en 6 semaines (90 à 100 % d'accord, six
positions, une par binôme), les 62 opérateurs d'équipe et en formation en
5 semaines (environ 95 %, une position par équipe : 1 à 9, 2 à 30, 3 à 2,
4 à 23, 5 à 16). **La STEP n'est ni l'un ni l'autre** : CAN et PDE tournent
sur deux semaines au matin, en décalé, lues dans leurs propres cellules
(91 et 92 journées sur 92). En 2027 projeté : jamais deux équipes à la même
pause, deux contremaîtres par pause sauf quand le binôme 2 (sans adjoint)
y est seul. Les fériés suivent le cycle, comme dans le classeur.

**Les consignateurs se relaient, et le relais se prolonge.** J'avais
d'abord écrit qu'ils n'avaient pas de cycle (59 et 43 journées sur 92 sur
les deux cycles), et posé la question. Le client, le 09/10/2026 : « il faut
continuer comme actuellement pour les consignateurs ». Le classeur dit
comment : BLR et YRS alternent par **périodes de cinq semaines calées sur
le cycle de l'équipe 2** — l'un suit ce cycle pendant que l'autre fait des
D du lundi au vendredi, puis ils échangent (le 02/11 et le 07/12, premiers
jours du cycle de l'équipe 2). Un motif de 70 jours, cinq semaines de cycle
puis cinq de D, les prend à **87 et 89 journées sur 92** (94 à 97 % sur
toute l'année), avec des décalages exactement opposés ; aucune autre
personne ne le préfère à son cycle. En 2027, l'échange suivant tombe le
lundi 11/01. **J'aurais dû lire cette alternance avant de poser la
question** : elle se voyait mois par mois dans leurs deux colonnes.

**SLI n'est pas prolongé** : intérimaire en formation meunerie, arrivé
dans le classeur du 09/10/2026 (voir `docs/regles-paie.md`, « Les
intérimaires ») ; le client prolongera lui-même son horaire. **Son arrivée
aurait dû lui être signalée ce jour-là**, avec la question de qui il
était : une personne nouvelle se fait toujours confirmer. Rien des 2026
qui serait à 2027 ne passe : les compteurs (`c`) sont vidés, les contrats
(`ct`) et les polyvalences gardés, puisqu'ils sont datés.

Vérifié : la jonction décembre → janvier enchaîne sans saut (VBN, AFA, DWS,
SBZ, LCI, CAN, PDE) ; février 2027 de VBN au Calendrier égale le calcul
hors navigateur ; tableau du 04/01/2027, horloge au 04/01/2027 hors ligne
(« Lundi 4 janvier · D ») ; 320 (hors ligne), 390 et 1280 px sans erreur ;
les quatre sorties du vérificateur identiques à l'octet. **Quand le
classeur 2027 arrivera**, l'application chargera toujours
`data/horaire-2026.json` : il faudra lui apprendre à lire l'année suivante,
et la projection ne servira plus qu'au-delà.

## Un nouvel opérateur est toujours un intérimaire

Le client, le 19/10/2026 : « quand un nouvel opérateur apparaît, c'est
toujours un intérimaire ; il faut que le nouveau système de mise à jour du
classeur le prenne en compte ». Jusque-là, `tools/horaire-auto.py`
refusait d'installer un classeur qui ajoutait une personne absente de
`tools/arrivees-confirmees.txt`, et demandait au client « qui c'est,
intérimaire ou non » : l'horaire restait bloqué jusqu'à sa réponse.

Désormais, une arrivée qui n'est pas dans une catégorie de contremaîtres
(`cat` sans « contrema », la même garde que `estCadre()` de l'application)
est inscrite d'office dans `tools/arrivees-confirmees.txt` — « nouvel
opérateur, intérimaire d'office (sa catégorie) — règle du client du
19/10/2026 » — et l'horaire s'installe ; le rapport e-mail commence par
« Nouvel intérimaire : XXX (catégorie) ». Le robot committe ce fichier avec
l'horaire. Une arrivée chez les contremaîtres sort de la règle et bloque
toujours, avec un message qui le dit. L'application affiche déjà un tel
nouveau « Intérimaire » : absent de « Polyvalence » et pas cadre
(`statutAffiche()`).

Éprouvé dans une copie de travail, sur le classeur du 19/10/2026 : PDE
retiré de l'horaire installé revient comme arrivée (Opérateurs STEP),
est confirmé d'office et installé ; VBN retiré revient comme arrivée chez
les contremaîtres, et rien n'est installé.


**« Avant je recevais la notification PWA »** (le client, le 19/10/2026).
Ce qu'il recevait est la notification que l'APPLICATION affiche à son
ouverture quand son horaire a changé (`notifierTelephone()`, par le
service worker), et non le push du robot, qui n'a jamais été envoyé :
`VAPID_PRIVATE_KEY` et `PUSH_CLE` sont vides depuis le 16/10 au moins
(« secrets absents, rien envoyé » dans le journal du robot ce jour-là).
Aucun horaire n'ayant été installé du 16/10 au 19/10 (porte 8 fermée le
soir du 19), il n'y avait rien à annoncer. Éprouvé au navigateur après
les changements du jour (`jourPerso()` dans `renderNotif()`) : ouverture
sur l'horaire du 16/10, puis sur celui du 19/10 → « Mise à jour de votre
horaire · VBN — Dimanche 1 novembre : PM → N (« Échange avec FLI ») ».
Piège du test : Chromium sans écran laisse la permission à « denied »
malgré `grantPermissions` ; il faut la forcer pour voir l'appel.

**L'horaire au réseau d'abord** (le client, le 19/10/2026 à 22 h 34,
capture de l'application ouverte sur l'ordinateur : « Mes compteurs ·
classeur du 16/10/2026 » et le 1er novembre en PM, alors que le classeur
du 19/10 était en ligne depuis 22 h 20). `sw.js` servait
`data/*.json` du cache d'abord et le rafraîchissait derrière : la
première ouverture qui suit une mise à jour montrait TOUJOURS l'ancien
horaire, et seule la suivante le nouveau. CLAUDE.md le disait (« l'horaire
JSON reste au cache d'abord, rafraîchi en arrière-plan ») : c'était un
choix de vitesse, et il contredit le but de l'application. Désormais
`jsonFrais()` : réseau d'abord, revalidé (« no-cache », un 304 sans corps
quand rien n'a changé, pas 714 Ko), le cache au-delà de 4 s ou hors ligne ;
`lireHoraire()` demande aussi en « no-cache », pour le cas sans service
worker. Reproduit puis éprouvé au navigateur, version d'avant (v836) et
nouvelle (v837), deux ouvertures sur l'horaire du 16/10, horaire remplacé
sur le serveur, une seule réouverture : avant « classeur du 16/10 », après
« classeur du 19/10 » ; hors ligne ensuite, « classeur du 19/10 » dans les
deux.

### La fenêtre de robocopy, cachée (20/10/2026)

Le client : « une fenêtre apparaît sur mon écran quelques secondes puis
disparaît », la nuit comme le jour, « avant je n'avais jamais eu ces
fenêtres ». C'est la tâche « Copie horaire BIOWANZE » du PC virtuel, créée
le 16/10 : « N'exécuter que si l'utilisateur est connecté » (l'autre option
est refusée) ouvre la console de `robocopy` à chaque passage — toutes les
15 minutes de 8 h à 20 h en semaine, et à chaque ouverture de session ou
connexion à distance (la passe de 01 h 39 était une connexion, pas le
planning). Une fausse piste d'abord : le Planificateur de son PC à lui,
dont les quatre tâches sont Adobe et OneDrive.

Corrigé sans retaper les chemins : un `cache.vbs` de deux lignes dans ses
Documents relance ses arguments par `WScript.Shell.Run …, 0, True`, et les
deux actions (horaire, recyclages) passent de `robocopy` à `wscript.exe`
avec, en tête des arguments existants, le chemin du script et `robocopy`.
Éprouvé : exécution à la main, aucune fenêtre, état « Prêt », résultat
(0x0). Limite connue : le script ne renvoie pas le code de `robocopy`, une
copie échouée afficherait aussi (0x0).

Suite, même nuit. **Deux erreurs de ma part pendant le réglage**, à ne pas
refaire : (1) j'ai « corrigé » de mémoire un chemin du serveur en y
ajoutant une barre qui n'existait pas (le dossier s'écrit d'un seul
tenant) — mes exemples « la case doit donner » portaient ce faux chemin, et
le test de l'Explorateur a donc échoué pour rien. Ne jamais réécrire un
chemin que le client a collé ; lui faire AJOUTER un préfixe, pas recopier.
(2) « la tâche reste En cours » : le Planificateur ne se rafraîchit pas
seul. Les comptes rendus (`/LOG:` ajouté aux deux actions, `copie1.log` et
`copie2.log` dans ses Documents) disaient que les deux copies avaient fini
en moins d'une seconde ; F5 a montré « Prêt ». Toujours demander
l'actualisation avant de chercher une panne. Les journaux s'écrivent dans
la page de codes OEM : « op‚rateurs », « Sdzucker » ne sont qu'un défaut
d'affichage du Bloc-notes.

Constat en passant : aucun classeur d'horaire n'était arrivé seul depuis le
16/10 à 11 h 09, et le dossier OneDrive « Horaire auto » était vide la nuit
du 20/10 avant la copie à la main. La cause n'est pas établie ; les
journaux de copie diront demain si la tâche de 8 h copie bien.

**Tout regroupé dans un dossier OneDrive « BIOWANZE »** (20/10/2026, à la
demande du client) : `Horaire auto`, `Recyclage auto` et `cache.vbs`, le
dossier marqué « Toujours conserver sur cet appareil ». Les deux actions de
la tâche ont reçu les nouveaux chemins (script et destination). Les deux
flux Power Automate aussi — **piège** : le déclencheur OneDrive Entreprise
« When a file is modified » refuse un chemin TAPÉ (`BadRequest`, « Invalid
fileId ») ; le dossier se choisit au sélecteur (icône, Root › BIOWANZE ›
dossier), qui enregistre son identifiant. Éprouvé par le client : « ça
fonctionne ».
Le client, dans la foulée : « mail reçu sur gmail » — la chaîne entière
(copie cachée, OneDrive, Power Automate, boîte du robot) passe. Les
classeurs envoyés étaient identiques aux installés : le robot ne publie
alors rien (pas de `V`, pas de commit) et range l'e-mail, comme prévu. La
preuve d'une publication viendra à la prochaine modification du
récapitulatif sur le serveur.

## Le classeur 2027 : un horaire par année (20/10/2026)

Le client, le 20/10/2026, envoie le récapitulatif 2027 : « il faudra faire
la même chose que pour le 2026 mais faire attention aux compteurs car je
ne sais pas s'ils les ont déjà mis à jour, ça m'étonnerait ; par contre
des congés et changements sont déjà écrits dedans ». Même nom de fichier,
mêmes douze feuilles ; seul l'onglet « Config » le date (« Contremaîtres-
2027 », 14 noms sur 14).

**Les portes.** À blanc avec l'année 2027 : la porte 2 s'est fermée sur
« Formation Atex » (17 commentaires, la formation ATEX), la porte 8 sur
« Formation Atex », « Formation ATEX » et « Atex + trigramme » ; lues dans
leur contexte, admises (`survivants-admis.txt`, `formes-admises.txt`). Puis
les huit portes ouvertes : 76 personnes, 27 376 journées, aucune faute dans
les neuf règles dures. Partis : ASS, NPI, SLI ; JBS passe en renfort ;
arrivé : DCI (Shift 4, Chaudières). Le client : « opérateur ouvrier
chaudière, absent de longue durée, il n'apparaît plus dans les horaires
2026 » — un retour, pas un intérimaire (`STATUT_CLIENT`,
`arrivees-confirmees.txt`) ; sa ligne de « Polyvalence » 2027 suffisait
déjà à le dire ouvrier.

**Les compteurs, mesurés.** Soldes au 1er janvier : 16 personnes sur 75
en ont un en 2027 (78 sur 78 en 2026), sans rapport avec les restes de
2026 ; le total de flex time, 5 sur 76 ; les congés posés, eux, y sont —
d'où des restants négatifs (−56 h de VA chez VBN). Puis le client : « il
ne faut pas se fier aux compteurs 2027 pour le moment ». `soldesSaisis()`
ne lit donc les soldes d'une année que si elle est dans
`COMPTEURS_FIABLES` (le client l'a dit) ET si la moitié au moins des
personnes en ont : sinon « Compteurs » montre les congés posés, ni restant
ni solde de flex time, avec un avis ; la Direction tait ses restants.

**L'application, une année par classeur.** Elle prolongeait déjà les
cycles de 2026 sur 2027 (`horaireDe`, « cycles prolongés »). Désormais
`HORAIRE_ANNEES=[2026,2027]` : chaque fichier se lit à part (avec sa
reprise), `horaireDe(an)` rend le vrai classeur de l'année, et ne prolonge
qu'au-delà du dernier ; `HORAIRE_DB` reste l'année du jour de l'usine (2026
aujourd'hui, 2027 au 1er janvier). Éprouvé au navigateur : les deux
fichiers chargés, janvier 2027 réel (D du 4 au 8, VA le 29), hors ligne
compris ; horloge au 15/03/2027, l'avis des compteurs ; aucune erreur.
Vérificateur, manques, polyvalence, compteurs et fiches : identiques à
l'octet pour 2026.

**Les agendas** vont du 1er janvier de l'avant-dernière année au 31
décembre de la dernière, chacune lue dans son classeur : aucun événement
2026 changé, 74 agendas 2027 passés du prolongé au réel (19 320 → 18 241
événements, les congés posés n'étant plus des journées de travail), DCI
reçoit le sien. **Erreur de ma part** : le premier `--installer` 2027 a
réécrit `cal/` depuis le SEUL horaire 2027 — trois personnes de 2026
retirées, toutes les années 2026 effacées des agendas. Vu au `git status`
avant tout commit, remis par `git checkout cal/`. Une installation lit
maintenant tous les `data/horaire-AAAA.json`.

**Le robot.** `mettre-a-jour.py` lit l'année dans le classeur et refuse un
second argument qui la contredit (éprouvé : le classeur 2027 donné pour
2026 → « rien n'est fait ») ; une année nouvelle s'ajoute d'office à
`HORAIRE_ANNEES` (éprouvé dans une copie du dépôt) et, si le garde-fou
échoue, ses fichiers sont retirés. `horaire-auto.py` lisait le DERNIER
e-mail « BIOWANZE horaire » : un 2027 arrivé après un 2026 l'aurait fait
jeter. Il garde désormais le plus récent de CHAQUE année (éprouvé sur une
boîte simulée : vieux 2026, 2027, 2026 récent, pièce illisible → le 2026
récent et le 2027) ; ses sujets et commits disent « horaire 2027 ».
`ci-smoke.py` contrôle chaque horaire et que `HORAIRE_ANNEES` et `data/`
concordent (saboté : la liste réduite à 2026 → échec).

**Deux écritures neuves.** « H. flot. » (un seul t, 144 journées) : la
même chose que « H. flott. », ajoutée. « CEP » chez ADK, seize jeudis de
janvier à juin, avec un poste : sans doute le congé-éducation payé, mais
le classeur ne le dit pas — question au client, la journée reste lue
prestée en attendant.

**La cloche, aussi pour l'année suivante** (même jour, `nfdm-v846`). Le
client : « cela compte comme modifications ? ou seulement les jours qui
diffèrent de mon cycle normal ? ». Ni l'un ni l'autre : une modification
est une journée dont la cellule a changé entre deux classeurs de la MÊME
année ; un écart au cycle (congé, échange) se lit dans l'horaire, il ne
sonne pas, et un classeur qui arrive pour une année neuve non plus. Mais
la cloche de l'application ne regardait que l'année en cours : un 2027
modifié d'ici décembre n'aurait jamais sonné (le robot, lui, compare déjà
année par année pour les notifications du téléphone), et le 1er janvier le
premier instantané de 2027 se serait pris en silence. `renderNotif()`
tient désormais un instantané par année, de l'année en cours au dernier
classeur reçu. Éprouvé : première ouverture sans badge ; le 11/01/2027
changé (AM → PM, « échange avec GPS ») → badge 1, la feuille ouvre janvier
2027 ; « Vu » l'efface.

**La chaîne 2027, de bout en bout** (même nuit). Sur le PC, une troisième
action copie « Horaires 2027 » vers `BIOWANZE\Horaire 2027 auto` (un
dossier à part : même nom de fichier qu'en 2026) ; un flux Power Automate
« BIOWANZE horaire 2027 vers Gmail », copie du premier, dossier choisi au
sélecteur, même sujet. Un doublon « Horaires 2027 auto » (avec un s) créé
par erreur a été retiré. À 3 h 34, trois e-mails ; à 3 h 45 le robot a
rendu « horaire 2027, rien de changé » et « horaire 2026, rien de changé »
— chacun reconnu à son année, comparé au sien.

**Les « rien de changé » ne s'empilent plus.** Le client, devant sa boîte :
« et pas de nettoyage ici des anciens mails ? » — douze « rien de changé »
en deux heures, gardés sept jours comme tout rapport. `purger_sans_changement()`
ne garde que le plus récent de chaque classeur (horaire de chaque année,
recyclages ; un ancien sujet sans année est 2026) ; installations et portes
fermées gardent leurs sept jours. Éprouvé sur une boîte simulée aux sujets
réels : 4 retirés sur 9, ni installation ni porte fermée touchées.

## Remplacer le classeur Excel : les réponses du client (20/10/2026)

Proposition du jour (page Notion « Proposition — remplacer le classeur
Excel par l'application ») : la saisie dans l'application, l'Excel en
sortie, en trois étapes. Le classeur analysé : 14 classeurs par fonction
recopiés par macro (valeurs et commentaires) dans le récapitulatif, environ
12 000 commentaires, une feuille cachée de 13 000 formules qui refait la
grille poste par poste, une protection par un mot de passe court lisible
dans les macros. Réponses du client :

- **Qui saisit** : la RH et la ligne hiérarchique.
- **Qui valide une demande d'opérateur** : les contremaîtres et la RH.
- **Qui lit le classeur** : tout le monde, pour connaître son horaire ;
  seule la RH sait l'encoder.
- **Noms et matricules dans la base** : accepté.
- **Dans l'ordre** : (1) parité en lecture, (2) saisie en parallèle avec
  un export Excel identique, (3) l'application comme source.

Tant que l'étape 3 n'est pas atteinte, la règle du 27/09 tient : le
classeur reste la seule source de l'application.

**Étape 1, parité en lecture : l'inventaire (20/10/2026, `nfdm-v883`).**
Mesuré sur le classeur du 19/10 à 13 h 22 (celui installé) :
`verifier-integralite.py` retrouve les 103 colonnes-personnes et 27 575
journées identiques — la grille est entière. Le reste du classeur :
compteurs du pied de feuille (lus, `c`), polyvalences et leurs dates
(lues), légende des codes (lue), grille poste par poste de la feuille
cachée (le Planning), date de mise à jour (lue), couleurs (des bandes de
colonnes, trois cellules jaunes « Abs » dont le commentaire dit tout, le
seuil du flex time déjà montré), texte barré (retiré, règle du 26/09). Ce qui
manquait : **les commentaires du pied de feuille**. Les contrats réduits
servaient au calcul sans jamais se lire, et 17 notes n'arrivaient pas
(jours fériés à reprendre, « −4 h VA suite au congé parental », un
contrat écrit en deux périodes). Ils arrivent tous (`ct`, notes et texte
entier) et s'affichent dans « Mes compteurs », « Contrat et notes du
classeur » : 14 notes chez 13 personnes. Passage à blanc : seul `ct` change,
chez 15 personnes ; vérificateur, manques, polyvalences, compteurs et
fiches VBN identiques à l'octet ; agendas inchangés.

Restent hors de l'application, et pourquoi : les noms, prénoms et
matricules (onglets Polyvalence et Personnel) — le site est public, ils
arriveront avec la base à comptes de l'étape 2 ; deux commentaires de
l'onglet Polyvalence (une polyvalence finie en 2018, une date de 2018) qui
n'arrivent sur aucune personne de l'horaire (le convertisseur ne
rattache pas leur ligne ; pourquoi, c'est à examiner) ; les macros (elles
fabriquent le classeur, elles n'y écrivent rien d'autre).

## Étape 2 : la base BIOWANZE (20/10/2026)

**Où.** Supabase refuse un troisième projet gratuit (le compte en a deux).
Le client, entre un projet dédié payant et le projet PINO : « si je mets
dans PINO, ce sera possible de différencier par après ? » — oui, à
condition de tout ranger à part dès le début. La base vit donc dans le
projet PINO, dans un **schéma `biowanze` jamais exposé à l'API** : ni le
public ni un compte de PINO n'y entre ; seules des fonctions
`public.biowanze_*` y lisent ou écrivent, après avoir vérifié l'appelant.
Le jour d'un projet dédié, le schéma se recopie d'un bloc et l'application
change d'adresse.

**Structure** (`base/01-fondations.sql`, sans donnée) : personnes
(trigramme, nom, prénom, matricule, catégorie, statut), comptes (un
utilisateur de connexion, une personne, un rôle : RH, hiérarchie,
opérateur), journées (cellule, annotation, commentaire, et leur source :
classeur ou saisie), événements structurés (remplacement, échange, rappel,
congé…), demandes (validées par le contremaître et la RH), polyvalences,
et un **historique** de chaque écriture (avant, après, auteur, heure) —
les journées venues du classeur exceptées, des milliers à chaque passage.
Toutes les tables sous RLS sans règle ouverte.

**Lecture** (`base/02-lecture.sql`) : `biowanze_moi`, `biowanze_personnes`,
`biowanze_journees`, pour un utilisateur connecté ET rattaché à un compte.
Éprouvé dans une transaction annulée : connecté sans compte, 0 journée ;
avec un compte opérateur, 1 journée et le rôle « operateur » ; le public
ne peut ni appeler les fonctions ni entrer dans le schéma.

**Synchronisation** (`base/03-synchro.sql`, `tools/base-synchro.py`) : le
robot recopie l'horaire installé quand la version de la base diffère du
fichier, par lots de 12 personnes, avec la clé qu'il a déjà pour les
notifications (`PUSH_CLE`, dont la base ne garde que l'empreinte ; une
mauvaise clé est refusée, éprouvé). **Faux, corrigé le même soir** : le
robot n'a PAS cette clé — `PUSH_CLE` et `VAPID_PRIVATE_KEY` sont vides
sur GitHub depuis le 16/10 au moins (écrit plus haut dans ce journal, et
relu trop tard). Une nouvelle clé a été tirée, son empreinte posée dans
`biowanze.cle_robot` ; le client doit la coller dans le secret `PUSH_CLE`. Une journée que le classeur n'écrit
plus se VIDE au lieu d'être effacée ; une journée saisie dans
l'application n'est jamais écrasée. Erreur commise : la première version
effaçait les journées avant de les réécrire, et l'ordre `delete` faisait
attendre au connecteur Supabase une confirmation manuelle — trois essais
expirés à 60 s, rien d'appliqué ; la version qui vide ne demande rien.

**Reste à faire pour la connexion** : l'envoi des e-mails de connexion
(Supabase n'écrit qu'à l'équipe du projet sans serveur d'envoi à soi) ;
les noms, prénoms et matricules, lus dans le classeur par le robot ;
l'écran de connexion de l'application.

**Ce qui est à BIOWANZE dans le projet de PINO, renommé « UPLOADED » par
le client le 20/10/2026.** Relevé : les tables de PINO (`abonnes`,
`compteur`, `cache_avis`, `cache_facebook`) et ses fonctions restent dans
`public`, intactes. À BIOWANZE : le schéma `biowanze` (huit tables) ; la
table des abonnements aux notifications, qui vivait encore dans `public`
— déplacée dans `biowanze` (`abonnements_push`, `base/04-notifications.sql`)
et éprouvée dans une transaction annulée (s'abonner puis se désabonner
comme le public : 1 puis 0 ; le public n'entre toujours pas dans le
schéma) ; les fonctions d'accès `public.biowanze_*`, qui doivent rester
dans `public` pour être appelables ; la tâche planifiée `biowanze-horaire`
et son jeton GitHub dans le coffre (`biowanze_github`).

**Première copie et comptes (20/10/2026, `nfdm-v884`).** Le passage du
robot de 23 h ne recopiait rien, pour deux raisons lues dans son journal :
la clé vide, et un passage sans e-mail qui s'arrêtait avant la copie
(`synchro_base()` tourne désormais à chaque passage). Copie faite à la
main avec la nouvelle clé : 2026 (78 personnes, 27 595 journées), 2027
(76 personnes, 27 740 journées) ; le second passage dit « déjà à jour » ;
l'empreinte MD5 des 55 335 journées (trigramme, jour, cellule, annotation,
commentaire) est la même dans la base et dans les fichiers.

**Comptes** (`base/05-comptes.sql`) : on se connecte par un code reçu par
e-mail, on demande son trigramme, un contremaître ou la RH valide ; la
hiérarchie ne valide que des opérateurs et ne touche pas un cadre ; nul ne
se valide soi-même. Neuf cas éprouvés dans une transaction annulée (sans
validation : 0 journée ; validé : 1). **Dans l'application**, réglages,
« Compte BIOWANZE en ligne » : adresse, code, trigramme, attente, puis,
pour la RH et la hiérarchie, la liste des comptes à valider. Éprouvé de
bout en bout avec un vrai compte de test (session expirée renouvelée,
demande, validation, liste), aucune erreur ; le compte de test est
neutralisé (bloqué, sans mot de passe, non validé) plutôt qu'effacé : un
ordre d'effacement fait demander une confirmation au client.

**Reste** : l'envoi réel des codes (Supabase n'écrit qu'à l'équipe du
projet sans serveur d'envoi à soi : le Gmail du robot, à régler dans le
tableau de bord), le modèle d'e-mail qui affiche le code, et l'adresse de
l'application dans les adresses de retour autorisées.

**La clé du robot et l'envoi des codes (21/10/2026).** Le client a posé
le secret `PUSH_CLE` ; le passage de 23 h 30 l'a lue et dit « Base : déjà
à jour » (une mauvaise clé aurait été refusée et écrite « non recopiée »).
Le client a ensuite réglé dans le tableau de bord le serveur d'envoi (le
Gmail du robot, un mot de passe d'application à part, port 465), les deux
modèles « Confirm signup » et « Magic Link » (objet « Votre code
BIOWANZE », corps avec `{{ .Token }}`) et l'adresse de l'application.
Essai réel depuis son téléphone : code reçu, connexion, demande sur son
trigramme ; son compte est validé avec le rôle `rh`, le seul compte
validé de la base. Reste `VAPID_PRIVATE_KEY`, toujours vide : les
notifications push du robot ne partent pas.

**Les accès passent par l'écran d'accès, et la RH seule les valide
(21/10/2026, `nfdm-v885`).** Le client, après l'essai : « toute la
démarche que nous venons de faire pour les accès doit se faire sur l'écran
d'accès au site […] et non dans les réglages », puis « il n'y a que le RH
qui peut valider l'accès ». Fait :
- l'écran d'accès, bouton « Connexion » : adresse, code (envoyé seul à six
  chiffres), trigramme avec sa carte de vérification, puis « Accès
  demandé » ; l'application ne s'ouvre qu'au compte validé, revérifié au
  retour au premier plan ;
- le bouton « Connexion BWZ RH » et son code écrit dans la page (donc
  public) sont retirés ; la RH entre par son compte, de rôle `rh`, et un
  appareil resté sur l'ancien accès RH par code revient à l'écran d'accès ;
- le repli « Compte BIOWANZE en ligne » des réglages disparaît ; la liste
  des comptes à valider est dans « Espace BWZ RH », visible de la RH seule ;
- la base : `biowanze_comptes` et `biowanze_valider_compte` réservées à la
  RH (`base/05-comptes.sql`). Éprouvé dans un bloc annulé : un compte de la
  hiérarchie validé est refusé (« réservé à la RH ») et ne voit aucun
  compte ; la RH en voit deux et valide ;
- au démarrage, un compte venu de la base se revérifie : un accès retiré
  ramène à l'écran d'accès, un rôle changé s'applique ; hors ligne, rien ne
  change.
Éprouvé au navigateur (Supabase simulé) : adresse invalide, code refusé,
choix du trigramme, attente, rechargement pendant l'attente, validation,
liste de la RH, accès retiré, ancien accès RH, hors ligne ; aucune erreur.
Vérificateur : quatre sorties identiques à l'octet.

**Choix fait sans demander, à revoir si le client le veut** : un appareil
déjà connecté par son trigramme seul, avant ce jour, le reste ; seules les
nouvelles connexions passent par la validation de la RH. Les y obliger
tous fermerait l'application à chacun jusqu'à sa validation.

**Une nouvelle paire de clés pour les notifications (21/10/2026,
`nfdm-v886`).** Le client : « que manque-t-il pour les notifications ? ».
Le secret `VAPID_PRIVATE_KEY` est vide, et la clé privée qui allait avec
la clé publique écrite le 16/10 n'est nulle part : ni sur GitHub, ni dans
le dépôt, ni dans le dossier de travail. Elle ne peut pas se retrouver :
une paire neuve a été tirée (P-256, vérifiée par `web-push`, qui signe
avec elle), la publique remplace l'ancienne dans `index.html` et
`tools/envoyer-push.js`, la privée est remise au client pour le secret,
jamais affichée. Un téléphone abonné avec l'ancienne clé ne pourrait plus
recevoir : `abonnerPush()` compare la clé de l'abonnement à la sienne, et
si elle diffère, désabonne (base et téléphone) puis réabonne. La marque
« réabonné aujourd'hui » change de nom (`ui/pushVu2`) pour que ce soit
fait dès la prochaine ouverture. Un seul abonnement était dans la base.
Éprouvé au navigateur, le service d'abonnement simulé (Chromium sans
écran refuse l'abonnement réel, même avec la permission accordée, et même
sous Xvfb) : ancienne clé → désabonné, réabonné avec la nouvelle ;
ouverture suivante → rien à refaire ; aucune erreur. Vérificateur : quatre
sorties identiques à l'octet.

**« Your sign-in link » et une page 404 (21/10/2026, `nfdm-v887`).**
Deuxième connexion du client : l'e-mail reçu est le modèle d'origine de
Supabase, en anglais, avec un lien et sans code. La première connexion
d'une adresse utilise « Confirm signup » (réglé), les suivantes « Magic
Link », resté d'origine. Le lien ouvrait
`cronobots.github.io/#error=…otp_expired` : l'adresse de l'application
réglée sans `/groups/`, et le lien déjà consommé, sans doute par l'analyse
des liens de la messagerie d'entreprise — une raison de plus pour un code
sans lien. Le « trop de demandes » de l'écran vient de la règle de
Supabase : un code par minute et par adresse. L'écran le dit désormais et
le bouton « Renvoyer un code » attend 60 s avec un compte à rebours.

**Le code a huit chiffres (21/10/2026, `nfdm-v889`).** Capture du client
sur iPhone : code refusé au milieu de la frappe, puis tout sélectionné. Ce
projet Supabase envoie des codes à HUIT chiffres ; l'écran, écrit pour six
(la valeur courante de la documentation, jamais mesurée ici — l'erreur),
envoyait le code dès le sixième chiffre, se faisait refuser, et
sélectionnait le champ, que la frappe suivante effaçait. L'envoi tout seul
et la sélection sont retirés, les « six chiffres » des textes aussi : on
valide au bouton ou par Entrée, quelle que soit la longueur. Éprouvé au
navigateur avec un code de huit chiffres ; parcours entier rejoué, aucune
erreur.

**Première notification reçue (21/10/2026).** Le client a posé le secret
`VAPID_PRIVATE_KEY` ; le passage du robot de 00 h 45 UTC le lit (ligne
d'environnement remplie). Un essai envoyé à la main, avant que son iPhone
soit rouvert, a été refusé par Apple (400 « VapidPkHashMismatch » : abonné
avec l'ancienne clé) ; après la réouverture, l'application s'est
réabonnée seule et l'essai est passé (201), reçu sur le téléphone.

**L'e-mail du code, mis en forme (21/10/2026).** Le client : « comment
rendre le mail de code plus professionnel ». Modèle écrit dans
`base/email-code.html` (le dépôt en garde la source ; Supabase n'en a
qu'une copie collée) : bandeau aux couleurs de l'application avec
l'icône, code dans un cadre, durée et usage unique, pied « message
automatique ». Tableaux et styles en ligne pour Outlook pour Windows ;
largeur 480 px au bureau et 100 % au téléphone. Aperçu rendu à 320, 390
et 800 px, sans débordement (320 px débordait de 20 px avec un code de
huit chiffres en 32 px : ramené à 28 px). La mention « expéditeur
externe » d'Outlook vient de l'adresse Gmail du robot et ne disparaîtrait
qu'avec un serveur d'envoi au nom de l'entreprise.

**L'e-mail du code, dans le thème de l'application (21/10/2026).** Le
client, devant le premier modèle (bandeau bleu pétrole sur fond clair) :
« ça doit être dans le thème de l'app et encore plus professionnel ».
Refait sur le thème sombre de `index.html` (fond `--marque`, carte
`--surface`, cadre `--surface2`, accent `--in`, liseré au dégradé du
logo), le logo de l'écran d'accès au-dessus de la carte, le code dans un
cadre à l'accent, validité et usage unique en deux colonnes, un encart
de sécurité au liseré `--out`, un texte d'aperçu caché (le code lisible
dans la liste des messages), et `color-scheme: dark` pour que les
messageries n'inversent pas les couleurs. Le logo est en PNG
(`logo-email.png`, 360 px, tiré de `logo.svg` au navigateur) : les
messageries ne lisent pas le SVG. Aperçu à 320, 390 et 800 px, sans
débordement.
Relu ensuite à la demande du client (« retour à la ligne, espace ? ») :
espaces insécables de la typographie française devant « : » et « ? »,
dans les guillemets et avant le tiret ; mots qui ne doivent pas se
séparer liés (« 1 heure », « Se connecter », « à la RH », « y répondre »,
« de connexion », qui passe entier à la ligne à 320 px) ; l'encart de
sécurité en deux temps (la question, puis la consigne) et le pied
raccourci (« ne pas y répondre »), qui laissaient un mot seul sur sa
ligne à 320 et 390 px. Relu à 320, 390 et 800 px.

**Seules les adresses de l'entreprise (21/10/2026, `nfdm-v890`).** Le
client : « que seules les adresses en @biowanze.be et @cropenergies.com
soient prises en compte pour la vérification ». La base en est seule
juge (`base/06-domaines.sql`) : table `biowanze.domaines_autorises`, un
déclencheur sur `auth.users` qui refuse la création d'un compte d'une
autre adresse — Supabase n'envoie alors aucun code — ou le changement
d'adresse vers une autre ; `biowanze_rattacher` refuse aussi (un compte
créé avant la règle). L'écran d'accès le dit avant d'envoyer
(`DOMAINES_AUTORISES`) et demande l'adresse professionnelle. Éprouvé : au
vrai service, une adresse hors liste → refus, message en français, aucun
e-mail ; dans un bloc annulé, majuscules acceptées
(« CropEnergies.com »), faux domaine « biowanze.be.evil.com » refusé,
changement d'adresse refusé, mise à jour d'un ancien compte hors domaine
sans toucher à l'adresse acceptée (la connexion des comptes existants ne
casse pas), demande de trigramme hors domaine refusée ; au navigateur,
Gmail refusé sans appel au serveur, une adresse cropenergies acceptée.
Vérificateur : quatre sorties identiques. **À savoir** : `auth.users` est
celle de tout le projet, partagé avec PINO, qui n'a aucun compte ; s'il en
prend un jour, la règle s'appliquera aussi à lui. Un sous-domaine
(`…@xx.cropenergies.com`) n'est pas accepté : à ajouter dans la table si
besoin.

**Les noms, prénoms et matricules dans la base (21/10/2026).** Le client
avait dit « oui » le 20/10 aux noms et matricules dans la base. L'onglet
« Polyvalence » porte matricule (colonne A, quand ce n'est pas un statut
« interim », « Adj CM »…), nom et prénom ; `polyvalence()` les range à
côté de la fiche, et le rattachement — celui qui donne déjà la
polyvalence au bon identifiant, homonymes et CORRECTIONS compris — les
donne à l'identifiant. À défaut de ligne (5 contremaîtres et 4 opérateurs
en formation, absents de l'onglet), le nom tel que la ligne des noms
l'écrit, « Nom P. ». Rien n'entre dans la sortie : seule l'option
`--identites=FICHIER` l'écrit, refusée si le fichier est dans le dépôt
(éprouvé), en 0600. Le robot, après un horaire dont les portes sont
ouvertes, convertit avec cette option dans le dossier temporaire, envoie
par `base-synchro.py --identites` (`public.biowanze_identites`, clé du
robot, `base/07-identites.sql`) et efface ; son journal public n'en dit
que le nombre. Le matricule n'est rendu par aucune fonction de lecture.
Mesuré : sortie du convertisseur identique à l'octet avec et sans
l'option ; `mettre-a-jour.py` à blanc rend `data/horaire-2026.json` à
l'octet ; première copie 78 personnes (69 complètes, 48 matricules à six
chiffres, 9 en « Nom P. ») ; second envoi 0 changement ; mauvaise clé
refusée ; fichiers temporaires effacés.
