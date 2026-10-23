# Anonymat : anonymiseur, contrôles, garde-fous du dépôt

Historique déplacé tel quel de `CLAUDE.md` le 18/10/2026. Les dates, mesures et erreurs y restent.

## Garder le classeur sous la main, anonymisé

```bash
python3 tools/anonymiser-classeur.py /chemin/Recapitulatif.xlsm \
        data/classeur-2026.xlsx
```

**À faire EN PREMIER, avant toute conversion.** Le convertisseur ne garde
que ce qu'il sait lire ; deux fois de suite une information s'est perdue
parce qu'elle n'était pas dans les lignes qu'il regardait. L'anonymiseur,
lui, **n'interprète rien** : il ouvre le classeur comme l'archive ZIP qu'il
est, remplace les noms partout où ils apparaissent, et referme. Feuilles,
formules, mises en forme, commentaires, colonnes qu'on n'a pas encore
comprises — tout passe intact. Ce qui n'est pas compris aujourd'hui reste
disponible demain, sans avoir à redemander le fichier.

Sortent du fichier : les noms sous toutes leurs formes, les auteurs de
commentaires, les macros (`vbaProject.bin` — d'où un `.xlsx`, pas un
`.xlsm`) et les propriétés du document.

**Il ne se contente pas de la feuille « Personnel ».** Elle est incomplète,
et le classeur écrit les gens de bien d'autres façons : `Nom P.`,
`J-M. Nom`, `Nom P.(ass.Us.)`, ou le nom et le prénom dans deux
cellules voisines. L'outil récolte donc tous les textes du classeur — mais
n'en retient un que si `_initiales()` y retrouve un **trigramme connu**. Un
alias qui ne se recoupe pas n'est pas un nom : c'est ainsi que « Step »,
écrit sur la ligne de quelqu'un, ne devient pas quelqu'un.

Les mots seuls — `PETIT`, `ADAM` — ne sont remplacés qu'avec leur majuscule
initiale : « petit » reste un mot français au milieu d'un commentaire.

**La garantie.** La sortie est relue entièrement et l'outil y cherche les
noms qu'il vient de remplacer. S'il en trouve un seul, il détruit sa sortie
et s'arrête avec le détail. Un anonymiseur qui peut laisser passer un nom
sans le dire ne vaut rien. Si un reste n'est pas un nom — « Paye » est aussi
un mot français — le relancer avec `--tolerer=paye` **après avoir lu le
contexte imprimé**.

**Elle ne voyait pas les AUTEURS comme une source de noms, et un prénom est
passé.** Découvert le 22/09/2026 sur un nouveau classeur, par le second
contrôle — pas par la garantie. Quelqu'un signait des centaines de
commentaires ; son nom de famille était connu par la feuille
« Polyvalence » et remplacé partout, **son prénom ne l'était par rien**. Les
signatures de tête ont bien été retirées, mais trois commentaires portaient
DEUX signatures, la seconde au milieu du texte : celles-là ne disparaissent
que si le nom y est RECONNU. L'une d'elles laissait le prénom suivi du
trigramme d'un collègue — une moitié remplacée nomme encore la personne.

L'anonymiseur **apprend donc des `<author>`**, comme il apprend de la ligne
des noms : ce qu'Excel écrit là EST le nom d'une personne, il n'y a pas de
corroboration à chercher. Deux morceaux sont exigés — « Nom, Prénom » en
donne toujours deux — pour écarter le « Auteur » que l'outil écrit lui-même
et les trigrammes qu'un classeur y dépose. Chaque MOT est appris à part en
plus de la forme complète, sans quoi un prénom employé seul au fil d'une
phrase échappe encore.

Quand le nom ne s'attribue à personne — deux homonymes, et c'était le cas —
ses initiales tiennent lieu d'identifiant, comme pour les gens de la ligne
des noms que l'annuaire ignore. Et si même cela est impossible, **ses mots
partent sous surveillance** : la garantie détruit la sortie et le dit. Mieux
vaut un outil qui s'arrête qu'un outil qui laisse passer.

**LA SIGNATURE SE RETIRE AVANT LE REMPLACEMENT**, et l'ordre inverse a vécu
une demi-heure. Les auteurs étant désormais appris, leur nom est remplacé
par son trigramme et « Nom, Prénom (external): » devenait
« PNO (external): », que `_est_nom()` ne reconnaît plus : **2311 têtes de
commentaire restaient en place**. Y ajouter un motif « trigramme seul »
aurait été pire — il aurait avalé le corps des commentaires qui COMMENCENT
par un code, « MPE : Maintien prime PM » en tête. Les motifs de signature
sont écrits pour des noms ; on les laisse voir des noms.

**Elle ne voyait pas les signatures de commentaires, et neuf personnes sont
passées.** Découvert le 22/09/2026 : `data/classeur-2026.xlsx`, dans le dépôt
PUBLIC, portait **20 912 occurrences** de neuf noms complets — les auteurs des
commentaires Excel — et `data/horaire-2026.json` en portait 36 de plus. Le
contrôle indépendant, mis à l'épreuve sur ce fichier, répondait « aucune
chaîne de forme nominale ne survit ».

Trois trous, tous dans les formes : `Nom, Prénom:` — le deux-points faisait
échouer l'ancrage `$` ; `NOM, PRÉNOM` — aucune forme ne couvrait deux
majuscules à virgule ; `Nom, APN` — une seule moitié remplacée nomme
encore la personne. Et surtout, **Excel coupe volontiers un nom en deux runs
XML** (`I` puis `om, Prénom`) : un motif appliqué balise par balise ne
peut pas recoller ce que la structure a séparé.

Les deux outils lisent donc maintenant la **structure** des commentaires, sur
le texte RECOLLÉ — chacun avec ses propres motifs, sans rien s'emprunter.
Une tête de commentaire est COURTE et d'un seul tenant : sans ces deux
bornes, la règle avale le corps des commentaires portant un `MPE :` au
milieu.

**Le jumeau PowerShell n'est PAS corrigé** : il porte le même trou. Ne pas
s'en servir pour une copie destinée au dépôt tant qu'il ne fait pas cette
passe.

**La garantie a une seconde faille, de naissance, et il faut la connaître** : elle ne
cherche que les noms que l'outil a SU APPRENDRE. Six personnes absentes de
« Personnel » et des colonnes nom/prénom de « Polyvalence » ont traversé
l'anonymiseur sans être remplacées ni signalées — il a répondu « aucun nom ne
subsiste » en toute bonne foi. Il lit depuis la ligne des noms, ce qui ferme
ce trou-là ; mais le principe demeure.

D'où un **second contrôle, qui n'emprunte rien à l'outil** :

```bash
python3 tools/verifier-anonymat.py /chemin/Recapitulatif.xlsm \
        data/classeur-2026.xlsx
```

Il prend toutes les chaînes du classeur d'origine, retient celles qui ont une
forme de nom, et dit lesquelles survivent. Il n'utilise ni la liste de noms de
l'anonymiseur, ni ses règles, ni sa notion de personne — sans quoi il ne le
vérifierait pas, il le répéterait. Ses survivants se lisent un par un :
`PRODUCTION`, `CPPT` ou `Adjoints Contremaître` ont la forme d'un nom sans en
être un.

Le `.xlsx` produit ne porte plus de nom : il peut donc, lui, vivre dans le
dépôt. C'est la copie de référence — **après** ce second contrôle, jamais
avant.

**Sur un poste sans Python** — un PC d'entreprise, typiquement — le même
outil existe en PowerShell, qui est présent sur tout Windows :

```powershell
.\tools\anonymiser-classeur.ps1 "Recapitulatif.xlsm" data\classeur-2026.xlsx
```

Même travail, même garantie. Le fichier est encodé en UTF-8 **avec BOM** :
sans lui, PowerShell 5.1 lirait les accents de travers et les motifs de noms
seraient faux. Ne pas le retirer.

## Quatre prénoms sont passés, et aucun motif ne pouvait les voir

Découvert le 25/09/2026, par hasard, en lisant la sortie d'une mesure sans
rapport : `data/horaire-2026.json` — dépôt **PUBLIC** — portait le nom de
famille d'un collègue et trois prénoms, écrits au fil de huit commentaires.

> « changement d'équipe de <nom> » · « remplace <prénom> qui remplaçait
> <prénom> » · « Remplacé par CDE (<prénom>) »

**`verifier-depot.py` répondait « aucune forme de nom ».** Et il ne pouvait
pas mieux faire : **un prénom seul n'a aucune forme reconnaissable**. C'est
la faille que ce fichier décrit depuis le 22/09 — elle s'est refermée sur
nous.

**J'ai écrit ici que le convertisseur ne pouvait pas mieux faire, et c'était
faux.** Ces quatre-là ne sont ni dans la ligne des noms, ni dans « Personnel »
— mais ils sont dans la colonne Prénom de la feuille « Polyvalence », chacun
sur une ligne. L'audit du 26/09/2026 l'a montré, et le convertisseur les
apprend désormais de là : voir « L'audit du 26/09/2026 ».

**L'anonymiseur, lui, les avait tous les quatre** — zéro occurrence dans
`data/classeur-2026.xlsx`.

### Le contrôle croisé : comparer les RÉSULTATS, pas les motifs

Les deux fichiers de `data/` sortent du MÊME classeur. Ce que l'un a retiré
et que l'autre a gardé est donc suspect, et cela se vérifie sans connaître
la forme d'un nom :

> Tout mot capitalisé vivant dans les commentaires de `horaire-2026.json`
> mais introuvable dans `classeur-2026.xlsx` est un mot que l'un des deux
> outils a retiré et que l'autre a laissé passer.

On n'emprunte pas les motifs de l'anonymiseur — les deux outils doivent
pouvoir se contredire, c'est la doctrine de `verifier-anonymat.py`. On
compare ses **résultats**.

Mesuré : **121 mots capitalisés distincts** dans les commentaires du JSON,
**3 signalés** — et les trois étaient des prénoms. **Aucun bruit.** Le
quatrième nom avait déjà été corrigé à la main.

Éprouvé dans les deux sens : dépôt propre à **0**, et un prénom replanté
dans le JSON fait sortir l'outil en 1 en le nommant avec sa journée.

### Ce qui a été corrigé, et avec quoi

Les quatre remplacements viennent de l'anonymiseur lui-même, relevés dans sa
sortie commentaire par commentaire — **on ne devine pas un trigramme**. Huit
journées chez quatre personnes, vérifiées par `comparer-horaire.py` : rien
d'autre n'a bougé, et les neuf règles, les 14 435 journées prestées et les
compteurs 76/77 sont identiques après.

**LE CLASSEUR ÉCRIT LA MÊME PERSONNE DE DEUX FAÇONS**, et c'est ce qui a
permis au nom de passer. La ligne des noms porte une orthographe, les
commentaires en portent une autre — `_initiales()` rend le même trigramme
pour les deux, mais le mot lui-même ne se recoupe pas, si bien que
`_motif_registre()` ne pouvait pas le reconnaître.

**J'ai d'abord conclu à une collision** — deux personnes donnant les mêmes
initiales — et je l'avais écrit ici. C'était faux, et le client l'a relevé :
« MMS c'est <nom>, au cas où ». **Le classeur le prouve tout seul** : les
deux journées où ce trigramme est « remplacé par DBE et RDT » sont
exactement les deux journées où DBE et RDT portent le commentaire qui
nomme la personne. Les deux colonnes se répondent.

**La leçon est de méthode** : `_initiales()` rejoué à la main sur la ligne
des noms ne dit PAS qui est qui quand le classeur orthographie un nom de
deux façons. Ce qui tranche, c'est ce que les journées se disent entre
elles — ici, un remplacement nommé aux mêmes dates des deux côtés.

### Le convertisseur apprend aussi de la ligne des noms

`_motif_registre()` construit, depuis la ligne des noms que le convertisseur
lit DÉJÀ pour en tirer les trigrammes, un motif qui remplace chaque nom par
le sien dans les commentaires. Il avait l'information en main et ne s'en
servait que pour nommer la personne, jamais pour la retirer du texte des
autres.

**Il ne trouve rien aujourd'hui** — les quatre noms de ce jour-là lui
échappaient par construction — et c'est un garde-fou, pas un correctif : le
jour où un commentaire nommera quelqu'un de la ligne des noms, il partira
tout seul. La majuscule initiale est exigée et les mots de moins de trois
lettres écartés, comme pour l'anonymiseur.

`grille()` est mémoïsée du même coup : le registre relit toutes les feuilles
avant la conversion, et sans ce cache chacune serait analysée deux fois.

### Ce qui reste : l'HISTORIQUE

Les quatre noms ont été poussés. Ils vivent donc dans les commits déjà
publiés, et le contrôle croisé ne regarde que l'arbre de travail.
`python3 tools/verifier-depot.py --historique` signale par ailleurs dix
formes anciennes. **Réécrire l'histoire d'un dépôt public est une décision
du client** — la procédure est dans `docs/purge-historique.md`.

## Le dépôt se contrôle lui-même

```bash
python3 tools/verifier-depot.py                # l'arbre de travail
python3 tools/verifier-depot.py --historique   # + tous les commits
```

**Une règle ne garde rien, et celle du dessus n'a rien gardé.** Cet outil lit
tous les fichiers suivis par git, y cherche les chaînes ayant une forme de
nom, et écarte celles qu'un humain a déjà regardées — `tools/formes-admises.txt`.
Tout ce qui reste est imprimé, et le code de retour vaut 1.

**Il ne SAIT pas qu'une chaîne est un nom**, et personne ne le peut. Il sait
dire « voici une forme de nom que personne n'a encore regardée », et il
s'arrête là. C'est la doctrine de la garantie de l'anonymiseur : mieux vaut
un outil qui s'arrête qu'un outil qui laisse passer.

**Ses motifs sont les SIENS** et ne sont pas empruntés à
`verifier-anonymat.py` : les deux doivent pouvoir se contredire.

**Il a trouvé deux noms dès sa première exécution** — deux que la correction
à la main venait de manquer, dans `verifier-anonymat.py` et dans
l'anonymiseur. C'est exactement ce pour quoi il existe.

**Et il en a manqué un, lui aussi, à sa première version** : elle ne
cherchait `Nom Prénom` qu'avec une virgule ou un deux-points, si bien qu'un
nom planté dans le README y est passé sans un mot. Le motif « deux mots
capitalisés à la suite » a été ajouté ; il ramasse du français ordinaire, et
ce bruit se range une fois pour toutes dans la liste.

**Ajouter une ligne à `tools/formes-admises.txt` est un acte** : c'est le
seul endroit par lequel un vrai nom pourrait entrer sans que rien ne crie.
On n'y met une forme qu'après l'avoir lue DANS SON CONTEXTE, avec sa raison.

**Le crochet git le lance à chaque commit**, et refuse au lieu de rappeler :

```bash
git config core.hooksPath .githooks     # une fois par machine
```

Éprouvé dans les deux sens le 23/09/2026 : un nom glissé dans le README fait
échouer le commit, et le dépôt propre passe à zéro.
- **Aucun montant de salaire non plus.** Le dépôt est PUBLIC : `docs/` se lit
  sans authentification, par le site comme par `raw.githubusercontent.com`.
  La rémunération fixe, le pécule, le treizième mois, l'avance, une prime
  nominative — rien de tout cela ne s'écrit ici. Les règles se décrivent
  avec des lettres (`T × 13,07 %`) ou des ordres de grandeur ; les montants
  restent sur l'appareil de leur propriétaire. Les valeurs communes à
  l'équipe — primes d'équipe, chèque-repas, barèmes — ne sont pas
  concernées : elles n'appartiennent à personne en particulier.


## Un intérimaire que le classeur ne recense pas

Le 19/10/2026 au soir, la mise à jour automatique a refusé le classeur du
jour : **porte 8 fermée**, « Prénom Nom » dans `data/horaire-2026.json`
neuf. Le client : « pourquoi pas de mise à jour horaire ? ». Un seul
commentaire, celui de GPS le 26/10 : « Visite du site avec Prénom Nom
(intérimaire chaudières) ». Le client, le même soir : « LCO est un nouvel
intérimaire chaudière, il ne figure pas encore dans le tableau ».

**Pourquoi il est passé.** L'anonymiseur et le convertisseur apprennent
les noms du classeur lui-même : la ligne des noms, « Personnel », la
colonne Prénom de « Polyvalence ». Ce nom n'est dans aucune — une seule
occurrence dans tout le fichier (`comments8.xml`). Il a traversé les trois
sorties (horaire, copie anonymisée, export brut). **Le second contrôle
d'anonymat (porte 2) a répondu « aucune chaîne de forme nominale ne
survit »** : il cherche les noms de la source et les signatures, pas une
forme au fil du texte. C'est la porte 8, faite de motifs indépendants,
qui l'a arrêté. Rien n'a été installé, rien n'a fuité.

**Ce qui est corrigé** : c'est le classeur qui dit que c'est quelqu'un —
« (intérimaire » suit son nom. L'anonymiseur (`INTERIMAIRE`,
`_sans_interimaire()`) et le convertisseur (`_INTERIM`,
`_coupes_interimaire()`) ont chacun SA règle, écrite séparément : un
« Prénom Nom » suivi de « (intérimaire » ou « (intérim » prend le
trigramme de la convention maison (`_initiales()`, prénom d'abord comme au
fil d'une phrase), celui qu'il recevra en entrant dans la ligne des noms.
Pour lui, c'est LCO, inconnu jusque-là (ni dans l'horaire, ni aux recyclages, ni cité).
Le nom n'est écrit nulle part dans le dépôt : la règle porte sur la
FORME, pas sur la personne. Éprouvé sur des exemples fictifs : « Remplace
GPS (intérimaire) » et « Formation (intérim) » ne bougent pas.

**Mesuré sur le classeur du 19/10/2026 (13 h 22)**, anciens outils puis
nouveaux : une seule journée diffère, GPS le 26/10, « Visite du site avec
LCO (intérimaire chaudières) » ; le nom n'est plus dans aucune des trois
sorties ; les huit portes s'ouvrent. Installé : 55 journées modifiées chez
27 personnes, 15 compteurs, 78 agendas ; intégralité à 0, garde-fou à 0,
flex time 78/78, neuf règles à 0.

**Erreur commise en cherchant.** J'ai cru que la porte 8, qui ne lit que
l'horaire neuf, laisserait l'export brut emporter un nom dans le dépôt, et
je l'avais étendue. C'était faux : `data/classeur-2026-brut.json` et
`data/classeur-2026.xlsx` sont exclus par `.gitignore` et ne sont jamais
publiés. L'extension a été retirée avant le commit.

**Ce qui n'a pas pu être fait d'ici** : le robot avait mis l'e-mail à la
corbeille après l'avoir lu, et l'outil Gmail de la session ne télécharge
pas les pièces jointes ; le client a déposé le classeur dans la
conversation.


## Une chaudière prise pour un nom (21/10/2026)

Le 21/10/2026 à 12 h 45 UTC, le robot a installé le classeur 2027 mais
refusé le 2026 : **porte 8 fermée** sur un mot à majuscule suivi de « Demandé ». Le
client a reçu l'e-mail d'échec de GitHub (« All jobs have failed ») :
c'est le code 1 d'une porte fermée, voulu — une forme de nom non regardée
EST une faute. Le client a déposé le classeur dans la conversation (l'outil
Gmail ne télécharge pas les pièces jointes, comme le 19/10).

Lu dans son contexte : un commentaire du 20/10, « Renfort pour démarrage
Stein/arrêt … Demandé le 20/10 15h ». Le mot revient dans des dizaines
de commentaires depuis janvier (« Test de performance … », « fuite
blowdown … ») : c'est une chaudière et son fabricant, comme Stein, pas
une personne. Il passait jusque-là parce qu'un point ou une minuscule le
suivait ; ici, deux espaces puis « Demandé » avec sa majuscule. Admis dans
`tools/formes-admises.txt` avec sa raison, pour cette forme seule.
Installé ensuite : les huit portes ouvertes, 63 journées modifiées chez
25 personnes, 12 compteurs ; intégralité et garde-fou à 0.

## Un skill tiers dans le dépôt, et le garde-fou (21/10/2026)

Le client veut des skills pour optimiser l'application ; il cite « UI UX
Pro Max » et « Impeccable », absents du catalogue d'Anthropic, publics
sur GitHub. Relus par un sous-agent avant d'entrer :
- **UI UX Pro Max** : une base de connaissances hors ligne (styles,
  palettes, polices, règles d'ergonomie, en CSV) et un script de recherche
  Python, bibliothèque standard seule, sans réseau ni commande, qui
  n'écrit que sur demande (`--persist`). Installé dans
  `.claude/skills/ui-ux-pro-max/`, sans ses tests, son outil de
  maintenance ni quatre catalogues JSON que seul ce dernier lit (2 Mo) ;
  les chemins de SKILL.md pointent sur le dépôt. `.gitignore` excluait
  tout `.claude/skills/` (10/10, « outillage d'agent ») : ce seul skill
  est admis, pour survivre au clone neuf de chaque session.
- **Impeccable : refusé.** Son lanceur télécharge et exécute un binaire
  non relu (contrôle sha256 pris à la même source), l'écrit dans `~/`,
  installe des hooks dans la configuration de Claude et d'autres outils,
  et une de ses références dit d'agir « sans demander la permission ».

Le garde-fou du dépôt y voyait 180 « formes » — en-têtes de colonnes
anglais, noms de polices. Plutôt que de les admettre une à une, le
dossier du skill est écarté de `verifier-depot.py` (`TIERS`), lui seul,
dans l'arbre comme dans l'historique. Contre-épreuve : un nom inventé
posé dans `docs/` est toujours signalé.

### Un second skill tiers : find-skills (22/10/2026)

Le client : « installe find-skills ». Le skill de `vercel-labs/skills`
(celui de l'outil `npx skills`) est un seul `SKILL.md` d'instructions, sans
script ni binaire : il apprend à chercher des skills (`npx skills find`) et
à les installer. Il a été téléchargé hors du dépôt, lu en entier, puis
copié dans `.claude/skills/find-skills/`. Une phrase du fichier propose
d'installer « avec -y, sans confirmation » : elle ne lie pas — chaque
skill trouvé se lit avant d'entrer, comme celui-ci et UI UX Pro Max.
`verifier-depot.py` y voyait 19 « formes » (ses titres anglais, « Find
Skills » et d’autres titres anglais) ; le dossier rejoint `TIERS`, LUI SEUL,
pour la même raison que UI UX Pro Max, et `.gitignore` le laisse entrer.

### Un troisième : supabase-postgres-best-practices (22/10/2026)

Le client : « quel skill serait le plus utile pour mon projet ? ».
Cherché avec find-skills (`npx skills find`, huit requêtes : supabase,
postgres, playwright, pwa, accessibilité, guides d'interface, javascript,
sécurité). Retenu : les règles Postgres de Supabase (éditeur officiel,
454 K installations), qui couvrent exactement `base/*.sql` — RLS,
fonctions `security definer`, privilèges, index, verrous. Écartés :
web-design-guidelines (Vercel), qui télécharge ses règles à chaque usage
— un texte qui changerait sans relecture — et que UI UX Pro Max couvre
déjà ; webapp-testing (Anthropic), en Python, quand nos essais Playwright
existent déjà.

Relu avant d'entrer, deux fois : un sous-agent a lu les 36 fichiers en
entier (aucune consigne d'agir, de télécharger ni d'installer ; aucun
script ; 87 liens de documentation), et une recherche des motifs à
risque n'a rien trouvé. Ses exemples SQL destructifs (`drop table`,
`alter system`, `pg_stat_statements_reset()`) sont des exemples ; la règle
« pas de delete ni de drop par le connecteur » reste. Le dossier rejoint
`TIERS` et `.gitignore` le laisse entrer.


### playwright-cli et son skill, avec un crochet de démarrage (23/10/2026)

Le client : « installe playwright cli et impeccable pour le projet ».

- **L'outil** : `@playwright/cli` (Microsoft), épinglé à la version 0.1.22. Il pilote un navigateur en ligne de commande, et chaque commande rend l'état de la page en quelques lignes, ce qui coûte moins de contexte que nos scripts Playwright.
  - Il embarque un Playwright qui attend le Chromium de révision 1247 ; le conteneur a la révision 1194, dans `/opt/pw-browsers`, et la règle de l'environnement est de ne jamais lancer « playwright install ». La configuration `.playwright/cli.config.json` le fait donc démarrer sur `/opt/pw-browsers/chromium` (`executablePath`).
  - Éprouvé sur l'application servie en local : ouverture, taille 390 × 844, recherche dans la page, passage hors ligne puis rechargement, aucune erreur de console.
- **Le skill** (`.claude/skills/playwright-cli/`), écrit par `playwright-cli install --skills` hors du dépôt puis relu : 11 fichiers Markdown (2 233 lignes), sans script.
  - Les exemples de `gh pr …` (pièces jointes de pull request) et de `npm init playwright` sont des exemples ; ils ne lient pas. Les règles du projet restent : aucune pull request sans demande, aucune dépendance.
  - Le garde-fou y voyait 113 « formes » (titres anglais, noms inventés d'exemples) : le dossier rejoint `TIERS`, lui seul. Contre-épreuve : une forme « Nom, Prénom » posée dans `docs/` est toujours signalée (code 1).
  - **Erreur rattrapée** : le commentaire ajouté à `verifier-depot.py` citait deux de ces noms d'exemple, et le garde-fou l'a refusé. Le commentaire est reformulé sans eux.
- **Le crochet de démarrage** (`.claude/hooks/session-start.sh`, déclaré dans `.claude/settings.json`) ne s'exécute qu'en session cloud, où le conteneur est neuf à chaque fois. Un échec n'empêche pas la session de démarrer, et il est signalé. Le crochet :
  1. règle `core.hooksPath` sur `.githooks`. C'est la règle de CLAUDE.md, qui se faisait à la main ;
  2. installe `playwright-cli` 0.1.22 s'il manque ou n'est pas à cette version ;
  3. écrit la configuration vers le Chromium du conteneur.
  
  Mesuré depuis un conteneur sans l'outil ni le crochet git : 0,6 s, puis 0,26 s quand tout est déjà là. Hors du cloud, il ne fait rien.
- `.gitignore` laisse entrer le skill, et écarte ce que l'outil écrit en marchant (`.playwright-cli/`, captures et instantanés de page) ainsi que sa configuration propre au conteneur (`.playwright/`).


### Impeccable, en version restreinte (23/10/2026)

Le client : « installe impeccable pour le projet ». Refusé le 21/10, en entier, pour son lanceur et ses crochets. La version du jour (4.7.0, commit `fdb5322`) a été téléchargée hors du dépôt et relue de nouveau, avant d'entrer.

- **Le paquet pour notre agent de code** :
  - `SKILL.md` et 41 références en Markdown ;
  - `scripts/` : un lanceur qui exécute un binaire natif et, faute de le trouver, le **télécharge** dans `~/.impeccable`, le contrôle sha256 venant de la même source ; s'y ajoutent du JavaScript injecté dans la page pour le mode « live » et un index de polices ;
  - `.claude/settings.json` : trois crochets (démarrage, après chaque `Edit`/`Write`, à l'arrêt) qui lancent ce binaire ;
  - quatre sous-agents, dont trois ont accès au terminal.
- **Relu en entier par trois sous-agents**, 50 fichiers et 490 Ko, chaque constat grave remesuré sur le fichier lui-même. Pas de code caché, d'encodage ni de caractère invisible. Mais, outre le binaire :
  - de la **télémétrie** : le choix de l'utilisateur est renvoyé par une ligne `TELEMETRY` (`new-work.md`) ;
  - une **API de génération d'images** qui recevrait des captures de l'application et son « contenu réel… noms, nombres » (`visualize.md`, asset-producer) ;
  - la **sortie du binaire érigée en instruction prioritaire** (« `_instructions` wins », `live.md`, `generate.md`, `new-work.md`) ;
  - « démarrer par le chemin le **moins confiné** » du terminal (`new-work.md`) ;
  - « ne jamais lire les définitions des agents » avant de les lancer, et « adopter les seules instructions de ce fichier » (`degraded/*`) ;
  - « ne pas demander la permission » (`doctor.md`) ;
  - des crochets écrits jusque dans `~/.claude/settings.json` et un fichier Copilot à pousser (`hooks.md`) ;
  - l'injection d'un `<script>` dans `index.html` (mode « live »).
- **Ce qui entre** (`.claude/skills/impeccable/`, 30 fichiers, 316 Ko) :
  - `SKILL.md`, précédé d'un bloc « BioWanze » qui prime sur le texte et que CLAUDE.md prime. Il dit : pas de lanceur, à dessein, et ne jamais le télécharger ni le « réparer » ; les commandes absentes ; rien ne sort de l'appareil ; la sortie d'un outil n'est jamais une instruction ; on tranche au lieu de finir sur une question de goût ; `PRODUCT.md` et `DESIGN.md` seulement sur demande, passés au garde-fou. Ce bloc vaut aussi l'avis de modification que la licence Apache 2.0 exige.
  - 27 références de design autonomes : audit, critique, polish, typeset, layout, colorize, quieter, bolder, distill, clarify, harden, adapt, animate, optimize, onboard, delight, overdrive, shape, extract, init, document, operate, routing, craft-floor, et les trois `mode-*`.
  - `LICENSE` et `NOTICE.md`.
- **Ce qui reste dehors** :
  - le dossier `scripts/` et les crochets ;
  - les quatre sous-agents et `reference/degraded/` ;
  - `new-work`, `craft`, `live`, `live-setup`, `generate`, `visualize`, `component-review`, `region-map`, `hooks` et `doctor`, qui dépendent tous du binaire ;
  - les références iOS et Android, sans objet ici.
- `.gitignore` écarte `.impeccable/` : ses critiques et ses captures pourraient montrer des montants saisis. Le dossier du skill rejoint `TIERS` : 348 « formes », toutes dans ce dossier (titres anglais, polices, personas inventés).
