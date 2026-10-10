# BIOWANZE

Simulateur de fiche de paie belge (Groupe S, CP 220) pour les équipes en
pauses de Biowanze. Application web installable, **entièrement contenue dans
`index.html`** — pas de build, pas de dépendances, pas de framework.

## Méthode de travail — à appliquer TOUJOURS

Le client, le 26/09/2026 : « enregistre tout ce que tu viens de faire pour ne
jamais oublier et toujours utiliser la meilleure méthodologie ». Ce qui suit
résume les règles que ce fichier démontre, cas par cas, plus bas. En cas de
doute, c'est la section détaillée qui fait foi.

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
la commande est enchaînée avec `;` au lieu de `&&`.

**Un nouveau classeur arrive.** Une seule commande, jamais les étapes à la
main :

```bash
python3 tools/mettre-a-jour.py /chemin/Recapitulatif.xlsm              # à blanc
python3 tools/mettre-a-jour.py /chemin/Recapitulatif.xlsm --installer
```

**Le classeur RH des recyclages** (« Suivi des recyclages sur poste de
production », `.xlsx`) a la sienne, même démarche, onze portes :

```bash
python3 tools/mettre-a-jour-recyclage.py /chemin/Suivi_recyclages.xlsx              # à blanc
python3 tools/mettre-a-jour-recyclage.py /chemin/Suivi_recyclages.xlsx --installer
```

Durées mesurées le 09/10/2026 : horaire **22 s à blanc, 0 s pour
`--installer`** (il reprend le passage à blanc réussi), recyclages **moins
d'une seconde**. Si c'est nettement plus long, quelque chose a régressé :
voir « Huit portes, et vite ».

Les deux sources restent HORS du dépôt. On LIT le rapport de comparaison, on dit au
client ce qui a bougé, on teste au navigateur, on committe. Si une porte se
ferme, on comprend pourquoi avant de toucher à quoi que ce soit : la
contourner, c'est rouvrir le trou qu'elle ferme.

**Avant chaque commit**, selon ce qui a été touché :

| Touché | À relancer, et le résultat exigé |
|---|---|
| tout | `python3 tools/verifier-depot.py` → 0 ; fichier neuf : `git add -N` d'abord, sinon il est invisible |
| `index.html` | `node --check` sur les scripts extraits ; `V` +1 dans `sw.js` ; test Playwright, hors ligne compris |
| lecture de l'horaire, placement, `index.html` | `node tools/verifier-calendrier.js` (neuf règles à 0), `--manques 0926`, `--polyvalence`, `--compteurs` : **sorties comparées à l'octet avec celles d'avant** ; `python3 tools/comparer-fiches.py VBN` |
| outils de `tools/` touchant `data/` | `mettre-a-jour.py` à blanc doit reproduire `data/` à l'octet, ou ne changer QUE ce qui est voulu |
| `data/` | `python3 tools/verifier-integralite.py` → 0 ; `verifier-anonymat.py` → 0 |

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

**Écrire ici ce qui a été appris**, dans la section qui en parle, avec la
date, la mesure et l'erreur commise s'il y en a eu une. Une affirmation de
ce fichier démentie par la mesure se CORRIGE sur place, en disant qu'elle
était fausse.

**Les questions ouvertes au client** sont dans « L'audit du 26/09/2026 »,
sous-section « Ce qui attend le client ». Quand il répond, on applique, on
mesure, et on retire la question de la liste.

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
départs (une arrivée se fait TOUJOURS confirmer par le client : qui,
quelle fonction, intérimaire ou non — SLI le 09/10/2026 ne l'a pas été), changements de groupe, journées modifiées avec l'avant et l'après,
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

## Le convertisseur ne gardait qu'un commentaire sur deux

Le client, le 23/09/2026 : « de nouveau tu poses des questions sans vérifier
toutes les cellules ni tous les commentaires ». Il avait raison, et la cause
n'était pas dans ma lecture : elle était dans le fichier.

**Chaque personne occupe DEUX colonnes** — la cellule et son annotation — et
**chacune peut porter son propre commentaire Excel**. Le convertisseur
écrivait `cm.get(cellule) or cm.get(annotation)` : dès que la première en
avait un, la seconde était jetée sans un mot. Une ligne.

Mesuré sur le classeur du 23/09/2026 : **684 journées portent deux
commentaires différents, et 496 n'en gardaient qu'un.** Ce qui disparaissait
n'était pas du décor :

> « remplace GPS **de 14h à 16h** » · « Remplace KDN Rappel le 10/03 **+3
> HS** » · « Remplace QDE **RAPPEL le 30/07** » · « départ à 19h00' » ·
> « arrivée à 23h00' » · « **conserver prime de nuit** »

Des heures, des rappels et une prime. Le client a dû signaler lui-même les
« rappel le 22.04 » d'AFA parce que rien ne les montrait — et j'ai commencé
par lui répondre que le classeur ne les portait pas.

`_les_deux()` joint les deux par un saut de ligne, comme Excel joint déjà
les lignes d'un même commentaire, et ne garde que le plus complet quand l'un
contient l'autre : le classeur recopie souvent la cellule sur l'annotation,
et répéter une phrase la ferait lire deux fois par les motifs de
remplacement.

**373 journées chez 61 personnes** ont retrouvé leur commentaire. Rien
d'autre n'a bougé — ni arrivée, ni départ, ni compteur, ni polyvalence :
le comparateur ne montre que cette section. Les journées de rappel passent
de **462 à 487**, et **9 231 signes** de commentaire reviennent.

### Un prénom mal orthographié par son propre auteur

Et ces commentaires récupérés ont aussitôt amené un nom dans le JSON d'un
dépôt PUBLIC. `tools/verifier-depot.py` l'a arrêté avant le commit — c'est
exactement ce pour quoi il existe, et ce n'est pas le convertisseur qui l'a
vu.

La tête du commentaire est écrite **avec une faute de frappe de son auteur**
— un « e » final manquant au prénom. `_motif_auteurs()` retire les noms que le
classeur DÉCLARE dans `<authors>` : le nom de famille correspondait, le
prénom tronqué non. Le motif a donc emporté la moitié qu'il reconnaissait et
laissé l'autre. **Une moitié de nom nomme encore la personne** — c'est la
règle déjà écrite pour l'anonymiseur, et elle s'est vérifiée ici.

On ne peut pas deviner les fautes de frappe. On peut lire la STRUCTURE :
**ce qui précède le premier deux-points, quand c'est court ET que cela nomme
un auteur déclaré, est une signature quoi qu'il y soit écrit.** La tête part
alors en entier.

La borne de longueur n'est pas décorative : sans elle, un commentaire citant
un auteur au fil du texte verrait tout son début avalé jusqu'au premier
deux-points. Et une tête qui ne nomme personne — « MPE : Maintien prime
PM » — n'est pas touchée : c'est le piège que `CLAUDE.md` décrivait déjà
pour l'anonymiseur.

Deux têtes retirées sur tout le classeur, et rien d'autre : le prénom, et un
identifiant de connexion. **L'anonymiseur, lui, n'avait pas ce trou** — zéro
occurrence dans `data/classeur-2026.xlsx`, parce qu'il retire la signature
AVANT le remplacement.

Contrôles après installation : neuf règles à **zéro**, 14 653 journées
prestées, compteurs **76/77**, découpe de `comparer-fiches` à l'épreuve, six
onglets rendus. Les motifs trop étroits passent de 46 à **49** — il y a
simplement plus de texte à lire, et la douzième règle fait son travail.

## Tout le classeur, et pas seulement ce qu'on sait lire

Le client, le 25/09/2026 : « toutes les cellules, commentaires, pages,
lignes, colonnes doivent être récupérés avec le fichier ; après le
convertisseur tout doit être dans la base de données, sauf les vrais noms et
prénoms des travailleurs ».

```bash
python3 tools/exporter-classeur.py data/classeur-2026.xlsx \
        data/classeur-2026-brut.json
```

**Le convertisseur ne garde que ce qu'il sait lire**, et c'est son rôle : il
produit l'horaire dont l'application se sert. Mais deux fois une information
s'est perdue parce qu'elle n'était pas dans les lignes qu'il regardait, et
une perte silencieuse est une perte qu'on ne corrige jamais. Il annonçait
déjà ce qu'il laissait ; **annoncer n'est pas garder**.

Cet outil ne lit rien : il **RECOPIE**. Douze feuilles, **75 660 cellules**
à leur adresse, **11 564 commentaires**, **521 étendues fusionnées** — contre
27 574 journées et 6 702 commentaires dans l'horaire. C'est à peu près le
DOUBLE de ce que le convertisseur retenait.

**IL PART DU CLASSEUR DÉJÀ ANONYMISÉ, ET C'EST TOUT L'ARGUMENT.** Anonymiser
à nouveau ici demanderait d'écrire une troisième fois des motifs de noms,
donc d'ouvrir un troisième trou — et ce fichier en a déjà décrit deux.
`data/classeur-2026.xlsx` est passé par l'anonymiseur ET par son second
contrôle indépendant : il ne porte plus de nom, et c'est prouvé. **On
recopie une source propre plutôt que de nettoyer une source sale.**

**Sans recopie des fusions** : on veut le fichier tel qu'il est écrit. Seule
la case en haut à gauche d'une fusion porte la valeur ; les étendues sont
exportées à part, de sorte que rien ne se perd et que rien ne s'invente.

**Il réemploie la lecture du convertisseur** plutôt que d'en écrire une
autre : deux lecteurs de xlsx dans le même dépôt finiraient par diverger, et
c'est toujours le second qui reste en arrière.

**Un identifiant de connexion survivait, et il est parti.** `RT0xxxx`, au
fil de six commentaires — la même phrase recopiée d'une feuille à l'autre.
Ce n'est pas un nom, donc l'anonymiseur le laisse passer, et il a raison :
il remplace des noms. Le convertisseur, lui, l'emportait par accident, parce
qu'il ouvrait une tête de commentaire. **Ici rien ne l'emporte par accident,
puisque rien n'est interprété** — d'où une règle nommée. Dans un dépôt
PUBLIC, un login d'entreprise se recoupe avec les annuaires de la maison
aussi sûrement qu'un nom. Le motif est étroit à dessein — deux lettres et
quatre à six chiffres — et mesuré : **un seul jeton de cette forme dans tout
l'export**, six occurrences, zéro après.

**Le garde-fou du dépôt a été éprouvé DANS LES DEUX SENS sur ce fichier**, et
la première épreuve a échoué pour une raison qu'il faut connaître : un nom
factice planté dans le JSON n'a rien déclenché, **parce que le fichier
n'était pas encore suivi par git**. `verifier-depot.py` lit les fichiers
SUIVIS ; un fichier neuf lui est invisible tant qu'il n'est pas ajouté. Une
fois `git add -N` fait, le nom factice le fait échouer, et le vrai fichier
passe à zéro.

**L'application ne le charge pas.** Elle continue de lire
`data/horaire-2026.json`, qui ne porte que ce dont elle se sert — 700 Ko
contre 1,3 Mo. Celui-ci est une réserve : on y va chercher ce qu'on découvre
avoir besoin, sans redemander le classeur.

**À régénérer après chaque nouveau classeur**, juste après l'anonymiseur et
son second contrôle.

### Revérifier tout depuis le fichier complet

Le client, le 25/09/2026 : « il faut qu'à partir du fichier complet, tu
revérifies tout ».

```bash
python3 tools/verifier-integralite.py
```

Il confronte le classeur entier à ce que l'horaire porte. **La grille des
jours doit être à ZÉRO** — c'est la seule exigence dure, et le code de
retour la porte. **Depuis le 26/09/2026 elle se compare cellule par
cellule** : voir « L'audit du 26/09/2026 ». Ce qui suit décrit la première
version, par sous-chaîne, et reste vrai de la normalisation des
commentaires.

**LA COMPARAISON NAÏVE MENT, et elle a menti trois fois.** Les deux fichiers
ne passent pas par le même chemin : l'horaire sort du `.xlsm` par le
convertisseur, le brut sort du `.xlsx` par l'anonymiseur puis l'exporteur.
D'où trois écarts d'écriture, et **1 584 fausses pertes** avant qu'on les
comprenne :

| Ce qui diffère | Faux positifs |
|---|---|
| un ESPACE — l'un colle deux fragments que l'autre sépare | **1 099** |
| la TÊTE DE SIGNATURE — le brut garde `ABC:`, le convertisseur la retire | **473** |
| le jeton `(identifiant retiré)`, posé à deux moments différents | **12** |

On compare donc sur un texte réduit — minuscules, sans ponctuation, sans
tête de trigramme, sans mention de retrait. **Ce qui survit à cela manque
vraiment**, et il n'en restait que 167.

**Et le premier vrai reste était une fuite, dans le dépôt PUBLIC.**
`RT0xxxx` — un identifiant de connexion — vivait dans
`data/horaire-2026.json`. Ni l'anonymiseur ni son second contrôle ne
pouvaient le voir : ils cherchent des NOMS, et ce n'en est pas un. Le
convertisseur en avait retiré un le 23/09, mais seulement parce qu'il
ouvrait une SIGNATURE ; au fil du texte, il restait. **C'est la
confrontation des deux fichiers qui l'a montré**, en mettant les deux
versions du même commentaire côte à côte.

`LOGIN` vit donc dans le convertisseur, et l'exporteur l'emprunte : deux
copies d'un même motif divergent, et c'est toujours la seconde qui reste en
arrière. La doctrine qui veut que deux outils ne s'empruntent pas leurs
motifs vaut pour les NOMS, où la contradiction EST le contrôle ; un login
n'est pas un nom, et il n'y a rien à vérifier par recoupement.

**ET L'ORDRE S'EST REFERMÉ SUR MOI, MOT POUR MOT.** Posée avant
`AUTEUR.sub()`, la règle transformait le suffixe ordinaire d'une signature —
« Nom, Prénom/rt0xxxx: » — en « (identifiant retiré): », que le motif de
signature ne reconnaît plus : **324 commentaires ont porté ce reste** pendant
une version. C'est exactement ce que ce fichier décrit pour l'anonymiseur
depuis le 22/09 — *la signature se retire AVANT le remplacement*. Elle se
pose donc en dernier, quand les signatures sont déjà parties.

Après correction : **9 journées changent**, dont 8 sont les quatre prénoms à
re-remplacer comme toujours, et **une seule** est le login. Zéro jeton de
cette forme dans les deux fichiers.

**Ce que l'horaire ne porte pas encore, et qui attend une décision :**

- **81 commentaires du pied de feuille** (lignes 396 à 434) qui écrivent les
  **CP et TP contractuels avec leurs dates** — « CP 10% du 01.11.2022 au
  28.02.2026 », « 12 mois à 90% », « TP contractuel 10% du 16.05.2025 au
  15.06.2027 ». **C'est la « fraction payée » que l'application demande de
  saisir à la main**, et le classeur la porte, datée, pour chacun ;
- **74 commentaires de la feuille « Polyvalence »** : les dates
  d'acquisition et de suppression de chaque polyvalence — « supprimée àpd
  01/02/19 », « fin au 30/09/2026 » ;
- **6 copies d'un même commentaire de la grille**, qui ne sont pas une perte
  mais une CORRUPTION de la copie de référence : l'anonymiseur y a remplacé
  « Poly Arr » par « PAR ». **Corrigé le 26/09/2026, et c'était bien pire** :
  480 CELLULES et 8 commentaires, pas 6. Et la phrase qui était écrite ici —
  « le classeur emploie bien `PAR` comme abrégé » — était FAUSSE : la source
  écrit « P. arr » et « P.arr », jamais « PAR ». Voir « L'audit du
  26/09/2026 ».

### La fraction payée se lit dans le classeur

Le client, le 25/09/2026 : « il faut que toutes les données du fichier soient
récupérées pour alimenter l'app et les règles ».

Le pied de chaque feuille porte, **en commentaire**, le congé parental et le
temps partiel de chacun avec ses dates. **46 périodes chez 28 personnes**,
que personne ne lisait — et c'est la « fraction payée » que l'application
faisait saisir à la main.

> « CP 10% du 01.11.2022 au 28.02.2026 » · « TP contractuel 20% du
> 01.07.2025 au 30.06.2027 » · « CP 20% à partir du 01/11/2026 pour 5 mois »
> · « 12 mois à 90% »

**LE SENS DU POURCENTAGE NE SE DEVINE PAS — LE CLASSEUR LE DIT DEUX FOIS.**
Une personne porte « TP 10% du 15.03.2024 au 14.03.2026 … TP 20% à partir du
01/06 » et, trois lignes plus haut, « **90%** 01/01 au 14/03  **80%** 01/06 au
31/12 ». Une autre porte « CP 10% du 01/12/25 au 30/09/26 » et « **CP 90 %**
du 01/12/2025 au 30/09/2026 » — mêmes dates, deux notations. Dix pour cent de
RÉDUCTION valent quatre-vingt-dix pour cent PRESTÉS, et **ce sont les colonnes
du classeur qui se répondent**, pas une supposition.

D'où la borne : **au plus 30 = une réduction, au moins 70 = la part prestée**.
Le classeur n'écrit rien entre les deux — mesuré : 10 et 20 d'un côté, 80, 90
et 100 de l'autre. Ce qui tomberait entre serait gardé **sans** fraction
plutôt que deviné.

**Un commentaire peut porter DEUX périodes** — « CP 10% du 02.04.24 au
01.10.2026 CP 10% du 02.10.26 au 01.02.2030 » — et n'en lire qu'une ferait
croire que le contrat s'arrête. Le texte est donc découpé à chaque
pourcentage, et chaque morceau porte sa période. Trois commentaires en
portaient deux, un en portait quatre.

**Et le « du » manque une fois sur deux** : « CP 10% 01/03/26 au 30/06/2029 ».
Il est donc facultatif — **à condition qu'un « au » relie les deux dates**,
sans quoi la ligne des jours fériés non pris, « -01/01 -06/04 -01/05 »,
donnerait une période de janvier à avril.

**La fraction vaut pour un MOIS, pas pour l'année**, une même personne passant
de 90 % à 80 % en cours d'année. `fractionDuMois()` regarde **le 15** : un
mois appartient à la période qui couvre son milieu. Deux périodes qui se
recouvrent — le classeur écrit parfois la même sous deux notations — sont
départagées par la plus récemment commencée : c'est la dernière décision
écrite.

**Le réglage reste, en dernier recours**, pour qui n'est pas dans l'horaire.
Le classeur prime — c'est la règle de tête du projet, et **c'est déjà ainsi
que le statut ouvrier ou employé suit la personne** depuis le 22/09.

Vérifié au navigateur, dans les deux sens, sur quelqu'un dont le congé
parental commence le 01/09/2026 : **septembre 2 700 €, août 3 000 €** sur une
rémunération d'exemple de 3 000 — la fraction s'applique dans la période et
pas avant.

`tools/verifier-integralite.py` en tient compte : le pied de feuille passe de
**81 commentaires non repris à 16**, et les seize restants sont douze lignes
de jours fériés non pris, qui ne sont pas des contrats.

**`CT` est un crédit-temps**, confirmé par le client le 25/09/2026. Trois
personnes le portent — `CT 20%`, donc 0,80 — et **sans aucune date**.

### Trois dispositifs, une seule arithmétique — et une allocation hors fiche

Le client, le 25/09/2026, a décrit les trois réductions du temps de travail
du droit belge. Elles mènent au même 4/5 ou au même 9/10 et **font la même
arithmétique sur la fiche** : la rémunération fixe × la fraction, et la
journée non prestée n'ajoute rien. Relevé sur les onze fiches mensuelles :
« Heure(s) congé parent. » y est une QUANTITÉ, sans colonne en euros.

**Ce qui les sépare ne se voit PAS sur la fiche, et c'est le piège.** Le
crédit-temps et le congé parental ouvrent une allocation de l'ONEM — versée
par l'ONEM, absente de la fiche, donc **impossible à simuler ici**. Le temps
partiel n'ouvre rien. Quelqu'un en `CP` ou en `CT` reçoit plus que ce que
l'écran affiche, et rien ne le disait : les trois infobulles et le réglage
« Fraction payée » le nomment désormais.

**`CT` n'est PAS un congé de circonstance** — la légende des codes l'écrivait
ainsi. Le classeur le prouve seul : les **159 journées `CT`** sont chez
**trois personnes**, exactement les trois qui portent « CT 20% » en pied de
feuille, à **55, 53 et 51 journées** — une par semaine. Un congé de
circonstance se compte en jours par événement, jamais en cinquante. La ligne
s'appelle « Heure(s) crédit-temps » et a quitté, avec le congé parental, le
seau des heures « assimilées à du travail » : ces heures ne sont pas payées,
et l'infobulle disait le contraire.

**Le crédit-temps se prend en 1/5 ou en 1/2 ; le 9/10 n'en est pas un
régime.** `_dire_regimes()` le dit sur la sortie d'erreur, **sans rien
refuser** : un pourcentage hors régime est souvent une faute de frappe, mais
il peut être un régime qu'on ne connaît pas encore. Aujourd'hui elle ne dit
rien — les 33 contrats codés tombent tous juste.

**Cinquante pour cent entre dans la bande refusée, et c'est démontrable** :
un mi-temps s'écrira « 50% », et à cinquante l'ambiguïté n'existe pas — la
réduction et la part prestée donnent le même 0,50. **Cent avec un code reste
refusé** : suspension complète ou temps plein retrouvé, l'écart est tout le
socle du mois.

**La semaine de la maison fait 38:40**, pas les 38:00 des exemples du droit :
30 h 56 pour un 4/5, 34 h 48 pour un 9/10. Ne pas recopier les nombres d'un
exemple générique.

### Sans date, la période est écrite dans l'horaire

Le client, le 25/09/2026 : « si pas de date il faut prendre en compte celle
écrite dans l'horaire, mais ne pas deviner ».

**Et elle y est.** Les trois `CT 20%` portent **55, 53 et 51 journées codées
`CT`** dans leurs colonnes, étalées sur l'année. La période n'était pas
absente : elle était écrite ailleurs. `_borner()` prend donc la première et
la dernière de ces journées.

C'est le contraire d'une supposition : **on ne comble pas un trou, on va lire
la réponse là où le classeur l'a mise.** Et sans journée de ce code, rien
n'est posé — la fiche reste sans date et le réglage reprend la main.

**Le code doit être NOMMÉ dans la fiche.** « 12 mois à 90% » ne dit ni CP ni
TP : on ne saurait pas quelles journées regarder. Ces deux fiches-là restent
telles quelles — et elles doublent de toute façon un contrat daté chez les
deux personnes qui les portent.

**Cinq contrats sont ainsi bornés** : les trois crédits-temps, un `TP 10%
jusqu'au` dont la phrase s'arrête net, et un `CP 90% 10mois` sans dates.

### Et une date sans année est de l'année du fichier

« 90% 01/01 au 14/03 », « 80% 01/06 au 31/12 » : le jour et le mois, pas
l'année. Un classeur de 2026 qui écrit cela parle de 2026 — ce n'est pas une
supposition, c'est l'année du fichier.

**Le classeur se corrobore d'ailleurs lui-même** : cette fin du 14/03 est
exactement celle du contrat daté « TP 10% du 15.03.2024 au **14.03.2026** »
de la même personne, et le « 01/06 » celui de son « TP 20% à partir du
01/06 ». Les deux notations disent la même chose, comme pour le pourcentage.

Vérifié au navigateur sur un `CT 20%` : **2 400 €** sur une rémunération
d'exemple de 3 000, en août comme en septembre — sa période couvre l'année
entière.

### La feuille « Polyvalence » date chaque acquisition

Soixante-quatorze commentaires, posés **sur la croix** de chaque case, disent
depuis quand la polyvalence est acquise — et l'onglet Recyclage ne le disait
nulle part.

> « 31-01-2023 » · « 01/03/2026 » · « 19-10-17 » · « MDE: supprimée àpd
> 01/02/19 » · « fin polyvalence gluten le 31/08/18 » · « fin au 30/09/2026 »
> · « 16-07-2019 revalidé en 2023 »

**DEUX SENS, ET UN MOT LES SÉPARE.** Une date seule est une ACQUISITION ; la
même précédée de « fin » ou de « supprimée » est une PERTE. Se tromper
afficherait « acquise en 2019 » sur une polyvalence retirée depuis — pire que
de ne rien dire.

**La croix ne suffit pas à trancher.** Les trois polyvalences supprimées n'en
portent plus, mais « fin au 30/09/2026 » en garde une : elle n'est pas encore
terminée. **C'est le mot qui décide, pas la croix.**

**Une polyvalence PERDUE garde sa date alors que sa case est vide.** Les
dates vivent donc à part des ateliers : les ranger dans `ateliers` rendrait
la polyvalence à la personne, les taire perdrait la seule trace qu'elle a
existé. La case affiche toujours `·`, et son infobulle dit désormais
**« Polyvalence retirée le 01/02/2019 »** au lieu de « pas la polyvalence de
ce poste » — ce qui explique un point qu'on prenait pour une lacune.

**70 dates lues**, dont **6 fins**. Les quatre commentaires restants sont sur
des lignes que l'horaire ne rattache à personne, celles que le convertisseur
signale depuis toujours.

**Ce qui se voit** : l'infobulle de chaque case porte sa date, **48 dans la
grille**. Une polyvalence qui se termine reçoit un **soulignement rouge** —
pas un fond : les deux fonds de cette grille disent un ÉTAT (vert, le quota
est atteint ; jaune, la personne s'y forme), alors qu'une fin est un
ÉVÉNEMENT À VENIR et que la case **garde son chiffre**, puisqu'elle compte
encore. Le rouge est celui des ateliers, déjà validé dans les deux thèmes —
inventer une couleur l'aurait laissée hors de ce contrôle.

### La table des codes est dans les règles de paie

`docs/regles-paie.md`, section « **Les codes, leur sens et ce qu'ils
paient** » : chaque code, sa signification, sa ligne de fiche, s'il est payé,
et d'où on le sait. **À relire avant de toucher à `ABS[]` ou à la légende de
l'onglet « Mon horaire »** — les deux doivent dire la même chose, et elles se
sont contredites TROIS fois, toujours de la même façon : un libellé qui
décrit autre chose que ce que le code fait.

- `ABS` rangé dans « non payé » avec « absence injustifiée », alors que le
  chemin du classeur le traduit en `SMG` et le paie ;
- `CT` donné pour un « congé de circonstance » quand c'est un crédit-temps ;
- `CT` et `CP` rangés parmi les heures « payées comme des heures prestées »,
  alors que la fraction les a déjà retirées de la rémunération fixe.

D'où un bloc de légende à eux, « **Temps de travail réduit** », où `CP`, `CT`
et `TP` se lisent ensemble avec la phrase qui vaut pour les trois : le jour
ne se paie pas, la réduction est déjà dans la rémunération fixe, et
l'allocation de l'ONEM — pour le congé parental et le crédit-temps
seulement — se verse hors fiche.

**`ABS` dit deux choses selon qui l'écrit** : le classeur, c'est une maladie
payée ; posé à la main dans le mois, c'est une absence non rémunérée. La
légende le dit maintenant.

**`SMG` N'EST PAS UN MOT DE LA MAISON.** Le client ne le connaissait pas et a
demandé ce que c'était — parce que je l'avais posé à côté de ses phrases
comme s'il en venait. Il vient de **la fiche de paie** : « Heure(s) SMG
maladie », *salaire mensuel garanti*. L'application a repris l'intitulé du
secrétariat social pour que l'onglet Contrôle se lise ligne à ligne contre la
fiche. La légende l'écrit désormais en toutes lettres, avec sa provenance.

**Et « Abs » avec « remplace X » n'est PAS une contradiction.** 562 des 1 848
journées `Abs` portent un commentaire qui parle d'un remplacement — de quoi
croire la lecture fausse, et j'ai ouvert ce doute. Le client, le 25/09/2026 :
**« toujours 1 »**, c'est-à-dire toujours une absence. Le classeur le prouve
seul : **45 de ces commentaires disent LES DEUX** — « remplace GPS remplacé
par JBI? et YPE ». On ne remplace pas quelqu'un et on n'est pas remplacé le
même jour au même poste. C'est la règle de tête du projet : le code franc est
la journée PRÉVUE, l'annotation dit ce qui s'est passé. **Il n'y avait rien à
corriger** — et c'est écrit pour que le doute ne se rouvre pas.

### Une polyvalence qui se termine cesse de compter le lendemain

Le client, le 25/09/2026, interrogé sur les deux polyvalences que le classeur
donne comme finissant le 30/09 : « **oui il perd sa polyvalence** ».

La date était LUE mais pas APPLIQUÉE : elle s'affichait, et la case
continuait de compter. Le 1er octobre, l'application aurait donc cru que
cette personne savait encore tenir la meunerie et le gluten — **et le
rééquilibrage l'y aurait envoyée boucher un trou qu'elle ne sait plus
tenir**. Le poste se serait affiché COMPLET alors qu'il manque quelqu'un. Un
manque annoncé à tort est pire qu'un manque qu'on n'annonce pas.

`polyFinie()` s'intercale donc dans `aLAtelier()`, qui est le seul point de
passage de « sait-elle tenir ce poste » — la grille du Recyclage, la
composition, le tableau du jour et le rééquilibrage y passent tous.

**La date est INCLUSE** : le 30/09 la polyvalence compte encore, le 1er
octobre elle ne compte plus. Vérifié au navigateur, horloge déplacée aux
trois dates.

**LE JOUR CALCULÉ, ET NON L'HORLOGE** — même règle et même piège que
`POSTE_PERIODE`. Sans lui, une polyvalence terminée hier vaudrait encore pour
tout novembre dans la liste des manques. `postesDePause()` calcule le jour
une fois et le passe à la chaîne des postes ET au rééquilibrage ; la
composition et la grille n'ont pas de date et se lisent sur aujourd'hui, ce
qui est exactement ce qu'elles montrent.

**Ce que cela déplace : rien, et c'est mesuré.** Manques inchangés — 189
journées et 385 places sur l'année, 8 et 8 d'ici la fin de l'année —,
couples de polyvalence 33 au quota sur 99, neuf règles à zéro, compteurs
76/77. Ces deux polyvalences-là ne servaient à combler aucun trou d'octobre
à décembre.

**D'où une épreuve, parce qu'un chiffre inchangé ne prouve rien.** En
terminant le gluten au 01/01 pour les 31 personnes qui l'ont, les manques de
gluten passent de 50 à **279** et les places creuses de 385 à 611. Le
mécanisme mord ; il n'avait simplement rien à mordre ici.

**La case vide sait déjà le dire** : son infobulle passe de « se termine le
30/09/2026 » à « **Polyvalence retirée le 30/09/2026** », le soulignement
rouge disparaît et la ligne « Se termine » sous la grille se vide. Rien n'a
été écrit pour cela — c'est la règle du 25/09 sur les polyvalences perdues
qui reprend la main d'elle-même.

**Et elle s'écrit en toutes lettres sous la grille** : « Se termine : PAM ·
Meun. le 30/09/2026 · PAM · Glut. le 30/09/2026 ». Un trait dit qu'il se
passe quelque chose ; il ne dit pas QUAND, et c'est la date qui compte quand
il reste cinq jours. La ligne et l'entrée de légende n'apparaissent **que
les jours où la grille en porte une**, comme le veut la règle du 22/09.

Vérifié au navigateur à 390 et 1280 px : 48 infobulles datées, 2 cases
soulignées, la ligne nommant les deux polyvalences qui se terminent, aucune
erreur.

## L'audit du 26/09/2026

Le client, le 26/09/2026, en envoyant un nouveau récapitulatif : « fais un
check complet multiagent sur la manière de récupérer toutes les infos de ce
fichier et de le rendre anonyme ». Cinq auditeurs indépendants —
anonymat, extraction, usage par l'application, méthode, contrôles — chacun
suivi d'un sceptique chargé de réfuter ses constats en les remesurant.

**Le nouveau classeur est le même que celui du 25/09 à 15 h 23**, texte pour
texte : la conversion ne change que les huit journées aux quatre prénoms.

### L'anonymiseur corrompait la copie de référence, de trois façons

Aucun nom n'y survivait — la chasse indépendante l'a confirmé sur 168 mots
tirés de la source. Mais la copie **n'était pas fidèle**, et elle **n'était
pas propre** :

| Défaut | Mesuré | Cause |
|---|---|---|
| « Arr » devenu « PAR » | **480 cellules**, 8 commentaires | la ligne 10 de la feuille cachée « Récapitulatif (1) » porte « P. arr » trois fois : trois cellules suffisaient à en faire une ligne de noms |
| le barré déplacé | 621 commentaires mêlant barré et non barré dans la source, **41** dans la copie | le retrait de la signature recollait tout le texte dans le PREMIER morceau — la signature, souvent barrée — et vidait les autres |
| des mots collés | **environ 350** commentaires, « ATAremplace » | AUTEUR emportait le saut de ligne qui précède une seconde signature |
| identifiants de connexion | **60** dans le fichier public | AUTEUR travaille sur les octets du XML et exige un blanc devant ; un login en tête d'un morceau suit un « > » |
| étiquette « Confidential » de l'employeur, identifiant de son annuaire, chemin réseau | docProps/custom.xml, x15ac:absPath | recopiés tels quels |
| un paquet qui annonce des macros | 13 relations vers des parties absentes | le retrait du `vbaProject.bin` ne nettoyait rien autour |

Tout est corrigé dans `tools/anonymiser-classeur.py`, et **chaque correction
est mesurée contre la source** :

- **hors des zones nominatives, plus UNE cellule ne diffère de la source** —
  les 301 écarts sont tous en ligne 10 des feuilles de personnes, dans
  « Personnel » et dans les colonnes nom et prénom de « Polyvalence » ;
  l'ancienne copie en corrompait 480 de plus ;
- **10 457 commentaires dont le texte est intact ont leur barré identique,
  caractère par caractère** ; les 1 107 autres ont perdu un nom ou un login,
  et trois seulement ont perdu un saut de ligne — celui d'une signature
  posée seule sur sa ligne, qui part avec elle ;
- **0 identifiant de connexion** (191 retirés, dont les 60 qui passaient),
  **6 collages** — ceux que la source porte elle-même ;
- le paquet s'ouvre : **0 relation pendante**, le type « classeur » et non
  « classeur à macros ».

**La ligne des noms ne se lit plus que dans les feuilles de personnes**
(`FEUILLES` du convertisseur), et **sans seuil** : la feuille Step n'a que
deux personnes, et le seuil de trois la laissait de côté.

**Le retrait se fait morceau par morceau** : `_editer_morceaux()` applique
les coupes au texte recollé sans déplacer un caractère d'un morceau à
l'autre. C'est ce qui garde le barré à sa place — et **le barré porte une
information** : voir plus bas.

**Les deux contrôles ne voyaient pas les identifiants de connexion**, et
c'est pour cela qu'ils ont vécu dans un dépôt public :

- `verifier-anonymat.py` les rangeait explicitement parmi les signatures
  ANONYMES. Il les cherche désormais dans le texte, avec son propre motif ;
- `verifier-depot.py` répondait « aucune forme de nom ». Il a une règle à
  eux, qui écarte les couleurs et les identifiants de commit — deux lettres
  de A à F — et ne lit, dans un classeur, que le texte des cellules et des
  commentaires.

**Et ce fichier-ci en écrivait un en toutes lettres**, pour illustrer un
motif — comme les neuf noms cités en exemple avant lui. Il s'écrit désormais
`RT0xxxx`, dans `CLAUDE.md` et dans quatre outils.

**`verifier-anonymat.py` sortait TOUJOURS en 1** — « CPPT », « STEP » ou « PRODUCTION »
ont la forme d'un nom — et un contrôle qui échoue toujours ne se lit plus.
`tools/survivants-admis.txt` porte les chaînes déjà lues, avec leur raison ;
l'outil sort en 0 quand il ne reste qu'elles. **Y ajouter une ligne est un
acte**, comme pour `tools/formes-admises.txt`.

### Le convertisseur apprend les prénoms, et se relit

Les quatre prénoms qu'on retirait à la main à chaque conversion **sont dans
la colonne Prénom de « Polyvalence »**, chacun sur une ligne dont le
trigramme est celui qu'on posait. `_motif_registre()` apprend donc aussi le
nom et le prénom de cette feuille, avec le trigramme de leur ligne — celui
que `polyvalence()` calcule, `CORRECTIONS` et « Personnel » compris.

- **un prénom n'est appris que s'il est UNIQUE dans la colonne** : partagé,
  on ne saurait quel trigramme écrire ;
- **accents et casse ne comptent pas, sauf la majuscule initiale** : l'un des
  quatre n'est pas écrit pareil dans la feuille et dans le commentaire, et
  une comparaison exacte le laissait passer ;
- **une garantie relit TOUT le JSON produit** — journées, champ `e`,
  contrats, dates de polyvalence — et y cherche chaque mot de nom des
  feuilles de personnes et de « Polyvalence », qu'on ait su l'attribuer ou
  non. Un seul reste, et rien n'est écrit (code 2, `--tolerer=` après avoir
  lu le contexte). C'est la doctrine de l'anonymiseur ; le convertisseur ne
  l'avait pas.

**L'étape manuelle disparaît, et elle se trompait une fois sur quatre.** La
conversion du nouveau classeur donne l'horaire installé à DEUX journées
près : GST les 25 et 26/02, « Remplacé par CDE (<prénom>) ». La main avait
écrit CDE ; le calcul écrit **CHD**. Le classeur tranche seul : ces deux
jours-là, **la colonne de CHD porte « Remplace GST », et CDE est en
repos**. CHD est « l'autre CDE, en équipe 4 » de `CORRECTIONS` — le
classeur l'appelle encore par ses initiales, le client l'a renommé. Le
prénom est le sien.

**L'anonymiseur faisait la même erreur**, pour la même raison : il
calculait les initiales du couple nom-prénom sans consulter `CORRECTIONS`.
`_ini_de_ligne()` le fait désormais — **pour le prénom seul**. Le nom de
famille garde ses initiales : il est souvent partagé, et le faire suivre a
changé, à l'essai, **460 signatures d'un auteur** en celles d'un homonyme de
la même feuille. Trois prénoms suivent ainsi une décision du client (CHD,
JBA, PDF), deux commentaires concordent désormais avec l'horaire, et
`verifier-integralite.py` repasse à zéro.

Rien d'autre ne bouge : les quatre sorties de `verifier-calendrier.js` sont
identiques à l'octet, et `comparer-fiches` passe son épreuve.

### L'export recopie maintenant TOUT le classeur

`tools/exporter-classeur.py` ne gardait que le texte des cellules, celui des
commentaires et les fusions. L'audit a mesuré ce qui tombait, et c'était
beaucoup : **le type** des valeurs (la date de mise à jour sortait en
« 46290.64 »), **13 637 formules**, **toute la mise en forme** — dont le
**barré** —, 262 lignes et 62 colonnes masquées, deux feuilles cachées, les
validations, 302 règles de mise en forme conditionnelle, 13 noms définis et
25 boutons avec leur macro.

Tout y est désormais — le format est décrit en tête de l'outil. Deux choix
à connaître :

- **les commentaires se lisent dans le XML, tels qu'ils sont écrits.** L'outil
  passait par la lecture du convertisseur, qui les NETTOIE : têtes retirées,
  sauts de ligne écrasés. « Cet outil ne lit rien, il recopie », disait ce
  fichier — c'était faux pour les commentaires. Leurs morceaux barrés,
  soulignés ou en italique sont dans `riches` ;
- **seule la mise en forme qui peut porter un sens** est gardée : fond,
  couleur et style de l'écriture, format des nombres. Pas les bordures ni
  l'alignement, qui doubleraient le fichier.

**Un aller-retour le prouve à chaque export** : l'outil recompte dans le XML,
par des motifs et non par l'arbre qu'il vient de parcourir, les formules,
les cellules peintes et barrées, les commentaires et ceux qui ont un morceau
barré. Un écart, et rien n'est écrit. Éprouvé : cinq sabotages — une
formule, un commentaire, un morceau barré, une suite de cellules barrées,
une cellule peinte en moins — sont tous détectés.

**L'export est reproductible** : la date inscrite est celle du classeur, et
non l'heure de l'export. Deux exports du même fichier sont identiques à
l'octet.

**4,0 Mo au lieu de 1,3** — 571 Ko compressés, ce que git stocke. Les formules
de « Récapitulatif (1) » en font 1,5. L'application ne le charge pas.

### L'intégralité se vérifie cellule par cellule

`tools/verifier-integralite.py` versait les commentaires dans un SAC et
cherchait chacun n'importe où dedans. Il ne regardait pas les valeurs des
cellules, un commentaire posé sur le mauvais jour passait, et un commentaire
court — « rappel », « remplace » — se retrouvait toujours quelque part. **Il
voyait 6 écarts là où 256 cellules et annotations étaient corrompues.**

Il compare désormais **chaque journée de chaque colonne-personne** du brut à
l'horaire — cellule, annotation, commentaire —, après avoir retrouvé la
personne par **l'accord de leurs journées** et non par le trigramme, que
`CORRECTIONS` et les suffixes font diverger. Une colonne que personne ne
reconnaît échoue ; **deux copies d'une même personne qui divergent entre
feuilles échouent** (les adjoints sont recopiés sur cinq feuilles) ; un
identifiant de connexion dans l'un des deux fichiers échoue.

Mesuré sur le classeur du 25/09 : **102 colonnes reconnues sur 102, 27 554
journées identiques**, 20 cellules vides devenues repos — la règle du
convertisseur —, **0 écart**. Éprouvé par six sabotages, tous détectés : un
commentaire décalé d'un jour, un commentaire court supprimé, une cellule
changée, une journée supprimée, une des cinq copies d'un adjoint corrompue,
un login planté.

**Les deux jointures d'une journée sont acceptées, et rien d'autre** : le
convertisseur joint le commentaire de la cellule et celui de l'annotation,
et ne garde que le plus complet quand l'un contient l'autre — casse
comprise. « Rappel 19/1 » n'est pas contenu dans « RAPPEL 19/1 », et il
garde les deux. Le contrôle, qui compare sur un texte en minuscules, doit
accepter l'un et l'autre.

**Le pied de feuille et « Polyvalence » ne font pas échouer**, et le second
était faux : il comptait 74 commentaires « non repris » en oubliant les 70
dates de polyvalence que l'horaire porte. Il en reste **2** — deux lignes que
l'horaire ne rattache à personne.

### Ce que l'application reçoit de plus

- **La légende entière** : onze codes au lieu de quatre. Elle ne lisait que
  les colonnes A et B de la première feuille ; les sept autres — `xxx`, `R`,
  `Abs` · `DS` · `CP` · `CSS` · `R-CM` — sont écrits au-dessus des
  colonnes-personnes et **partaient dans le champ `e` de 29 personnes**,
  affiché sous leur nom dans l'annuaire comme s'il les concernait. Les
  lignes 1 à 8 ne portent que la légende et la date de mise à jour —
  mesuré sur les 102 colonnes —, et `e` ne les lit plus. Les libellés des
  compteurs suivent la légende, comme ils le faisaient déjà pour les quatre
  premiers codes : « CP » s'y lit « Congé Parental ».
- **Le statut de « Polyvalence »** (`poly.statut`) : « interim », « Adj CM »,
  « Assistant usine ». Jamais le matricule. Rien n'en est tiré.
- **Le bloc « Temps de travail réduit » de l'onglet Compteurs** : il ne
  montrait que le congé parental — les huit personnes en temps partiel et les
  trois en crédit-temps avaient leurs compteurs dans le classeur et rien à
  l'écran — et ne lisait « à planifier » que sous une des deux écritures du
  classeur, si bien que onze personnes sur seize ne le voyaient pas.
  Vérifié au navigateur sur LCI, SBZ, VBN et ATA.
- **Les colonnes sans nom sont annoncées** : Shift1 AG et Shift4 Q portent
  une année de journées sans rien en ligne 10. **J'ai écrit que c'étaient des
  copies de travail de DWS et de CHD, et c'était faux** — leurs cellules
  franches coïncident, rien de plus. Le client, le 26/09/2026 : « Shift 1 AG,
  c'est le troisième chaudiériste de l'équipe 1, mais avec les transferts
  d'équipe actuels il n'y a plus personne pour le moment ; Shift 4 Q, c'est
  l'opérateur fermentation de l'équipe 4, modifié aussi récemment ». Ce sont
  des **places sans titulaire** : la colonne porte la rotation du poste, pas
  une personne. Le convertisseur les DIT sur sa sortie d'erreur sans les
  rattacher à personne, et c'est juste — une place qui se remplit s'y verra
  en premier, un nom apparaissant en ligne 10.

Rien d'autre ne bouge : champ `e` chez 29 personnes, `poly` chez 21, la
légende — et aucune journée. Les quatre sorties de `verifier-calendrier.js`
sont identiques, l'intégralité reste à zéro.

### Un commentaire barré ne compte plus

Le client, le 26/09/2026 : « un commentaire barré est un commentaire qui
n'est plus à prendre en compte ». Règle et raisons dans
`docs/conversion-horaire.md`, « Ce qui est barré ne compte plus ».

**La première version s'est trompée d'ordre**, encore : retirer le barré
AVANT le nettoyage a fait échouer l'intégralité sur deux journées — un
trigramme collé à la signature qui suivait le morceau rayé, et une
initiale orpheline, Excel ayant coupé une signature en un morceau barré et
un morceau qui ne l'est pas. `_TexteBarre` porte le barré caractère par
caractère à travers le nettoyage, et le retire à la fin. **Rejouée avec
tous les drapeaux à faux, la nouvelle chaîne reproduit l'ancien horaire à
l'octet** : c'est la preuve que la refonte ne change que le barré.

`verifier-integralite.py` retire le barré du brut de son côté, par les
`riches` de l'export — sa propre lecture, pas celle du convertisseur.

Mesuré sur le classeur du 26/09/2026 :

- **496 journées chez 59 personnes** perdent tout ou partie d'un
  commentaire ; aucune cellule, aucune annotation ne bouge ;
- **sept touchent à l'argent** : un rappel retiré (DBE 06/02), quatre
  « maintien prime » retirés (YBT 14/01, BLR 04/10, CGI 01 et 02/04) ;
- **FLN** : son temps partiel finit au **30/09/2026** — la fin de 2027
  était rayée — et la fraction retombe sur le réglage à partir d'octobre ;
- polyvalence **33 → 32** couples au quota (JBI meunerie 5/5 → 4/5 : son
  « remplace SKS en AM » du 14/01 est rayé), manques de l'année **385 →
  386** places ; `--manques 0926` et `--compteurs` identiques ; neuf règles
  à zéro ; motifs trop étroits 50 → 48 ;
- deux formes innocentes admises dans `tools/formes-admises.txt`, nées du
  retrait d'un morceau rayé entre deux mots.

**Une ligne ENTIÈREMENT barrée, elle, vaut comme si elle ne l'était pas.**
Le client, le 26/09/2026 : « c'est une erreur de manipulation du RH, ne pas
prendre en compte les lignes entièrement barrées ». Deux lignes le sont : le
02/03 (ligne 71) et le 14/05 (ligne 144), sur les cinq Shift et
« Contremaître », de 25 à 39 cellules chacune, avec de vraies prestations
dessous. Le barré d'une CELLULE n'a jamais été lu — seul celui des
commentaires l'est —, et **aucun des 52 commentaires de ces deux lignes ne
porte de morceau barré** : la règle précédente ne leur a rien retiré. Rien à
changer dans le code ni dans `data/`, et la distinction est à garder : le
barré d'un commentaire est une décision, celui d'une ligne un accident.

### Le jaune d'une journée est un pense-bête

Le client, le 26/09/2026, sur les trois « Abs » de GSK surlignées les 16, 19
et 20/01 : « ce sont des jours où il remplaçait, mais le commentaire a été
barré ; à mon avis c'était mis en jaune pour ne pas oublier de trouver un
remplaçant à celui qu'il était censé remplacer ».

**Le classeur le confirme de lui-même** : les trois commentaires sont
« ~~remplace CGI~~ », entièrement barrés, et ces trois jours-là la colonne de
CGI porte « remplacé par LDY » puis « remplacé par ATR » — le remplaçant a
été trouvé. Les quatre autres « Abs » de la série (14, 15, 17, 18/01) ne
sont pas jaunes : ce jour-là GSK ne remplaçait personne.

**Rien à lire ni à coder** : le jaune ne porte ni heure ni montant, et la
journée reste une maladie. La règle du barré du 26/09 avait déjà retiré
« remplace CGI » des trois journées ; avant elle, l'horaire faisait croire
que GSK remplaçait quelqu'un un jour où il était malade.

**Le gris des colonnes de SKS ne veut rien dire non plus.** Grisées sur
« Opérateurs » du 02/01 au 12/06, elles tombaient pile sur ses 112 journées
en meunerie — une coïncidence qui ressemblait à une preuve. Le client, le
26/09/2026 : « cela ne correspond à rien, sûrement une ancienne zone d'un
autre opérateur, car SKS a pris sa place dans l'horaire de la page
Opérateurs ». **Une mise en forme survit à celui pour qui elle a été posée** :
une colonne réattribuée garde les couleurs de son ancien occupant. SKS est
en formation en meunerie — depuis le 21/09 seulement, voir plus bas.

### Une formation commence à une date

Le client, le 26/09/2026, dans la foulée : « il a commencé en meunerie le
21/09 ». La feuille range SKS parmi les opérateurs en formation, « Meunerie »
en ligne 9, pour toute l'année ; ses commentaires ne nomment la meunerie
qu'à partir du 21/09, et sa polyvalence le déclare validé en fermentation,
distillation et chaudières. `FORMATION_DEBUT` porte la date : avant elle,
`enFormation()` rend faux et `posteTenu()` ne lit ni la ligne 9 ni `e`.

Mesuré : neuf règles, compteurs et `--manques 0926` **identiques à
l'octet** ; manques de l'année **386 → 362** places, 189 → 177 journées ;
SKS **« à déterminer » 31 journées** et déduit de sa polyvalence 67 fois ;
son recyclage passe de « Chaudières 10/10 » à Terrain arrière 32, Distillation
20, Chaudières 13, Fermentation 11 — **34** couples au quota au lieu de 32.
Vérifié au navigateur, hors ligne compris.

**Son poste d'avant : polyvalent arrière de l'équipe 5.** Le client, le
26/09/2026 : « il était polyvalent arrière dans l'équipe 5 avant cela ; il a
été sorti de l'horaire d'équipe pour sa formation meunerie ». Il entre donc
dans `POSTE_PERIODE` — terrain arrière jusqu'au 20/09 —, la seconde tranche
de la table après LCI.

**Et le Recyclage lisait « son poste » sur aujourd'hui**, ce qui ne tient plus
dès qu'on change de poste à une date : en formation aujourd'hui, SKS n'a pas
de poste à lui, et ses journées au terrain arrière d'avant le 21/09
comptaient comme du recyclage — **103/10**, un quota atteint dix fois sur le
poste qu'il tenait tous les jours. `posteAttitreLe(p, jour)` rend le poste
attitré CE jour-là, et `calculerPolyvalence()` n'y compte pas une journée à ce
poste. **Rejoué sans cette règle, seul SKS change** : elle ne touche
personne d'autre, puisque personne d'autre ne change de poste avant
aujourd'hui.

Mesuré, depuis l'état d'avant le 21/09 : neuf règles, compteurs et
`--manques 0926` **identiques à l'octet** ; manques de l'année **386 → 358**
places, 189 → 177 journées, **plus aucun « à déterminer »** ; SKS
« Chaudières 10/10 ✓, Distillation 4, Fermentation 2, Terrain arrière 0,
Meunerie F » ; **31** couples au quota au lieu de 32 — ceux qui tenaient le
terrain arrière à sa place y comptent moins (PLZ 16 → 9, CDE 8 → 3, SMA
30 → 28). Vérifié au navigateur, hors ligne compris.

Le découpage du vérificateur prend désormais `POSTE_PERIODE` jusqu'à
`] };` : la table tient sur plusieurs lignes, et la découpe au premier saut
de ligne rendait une `SyntaxError`.

### Le terrain arrière ne se recycle pas

Le client, le 26/09/2026, en voyant « Terrain arrière 0/10 » sur la ligne de
SKS : « terrain arrière ne doit pas compter de recyclage », puis, la question
posée entre SKS seul et tout le monde : « ce poste ne compte pas pour un
recyclage, c'est fermentation/distillation ».

Ce n'est pas un atelier, c'est la réunion de deux — aucune liste de
polyvalence ne le porte, `tientTerrainArriere()` le déduit. `PV_SANS_RECYCLAGE`
le sort de `polyvalenceDe()` et de la grille, et une journée passée au terrain
arrière **ne compte nulle part** : la reverser à la fermentation ET à la
distillation était l'autre lecture possible, et le client ne l'a pas
demandée. Si c'était son intention, c'est `calculerPolyvalence()` qu'il
faudrait toucher.

Mesuré : **seule la colonne part** — aucune autre case ne bouge, neuf
règles, compteurs et manques identiques à l'octet. Couples au quota
**31 → 23** sur **99 → 86** : les huit quotas de terrain arrière (ATR, FPA,
GDT, GPO, JBI, PAM, SMA, VGG). La grille a six colonnes au navigateur :
Meun., Glut., Ferm., Dist., Chaud., STEP. Le polyvalent arrière dont c'est le
poste perd son point plein — il n'y a plus de colonne pour le porter.

### Entre les deux arrêts, aucun effectif n'est exigé

Le client, le 26/09/2026, sur les fenêtres « SHUT-DOWN » que le classeur
surligne en jaune dans la colonne des jours — du 16 au 23/03 et du 10 au
18/04 : « l'effectif ne devait pas être respecté car il n'y avait souvent
que 2-3 personnes en pause de nuit ».

**Je l'ai d'abord appliqué à l'envers**, en exemptant les deux fenêtres
elles-mêmes — et c'est poussé ainsi pendant un commit. Le client, en
réponse à la question qui suivait : « les périodes avec les cellules à
droite de celle en jaune dans la colonne A devaient respecter les
effectifs, les autres entre non ». Les fenêtres jaunes sont tenues ; ce sont
les jours **entre** elles qui ne le sont pas.

`SANS_EFFECTIF` porte donc **du 24/03 au 09/04** : exactement les jours dont
les nuits sont vides, l'équipe de nuit passée en jour avec « maintien
prime N ». Avant la première fenêtre (09-15/03) et après la seconde (19/04),
les manques sont ceux d'une semaine ordinaire — mesuré sans aucune
exemption. `renfortDuJour()`, déjà le point où une journée ajuste ce qu'on
attend d'elle, rend `{_libre:true}`, et `attenduAuPoste()` rend zéro.

Mesuré : neuf règles, compteurs et `--manques 0926` identiques à l'octet ;
manques de l'année **358 → 247** places, 177 → 160 journées. Le Recyclage
bouge un peu, pour la raison attendue — sans effectif exigé, le rééquilibrage
ne PLACE plus personne pendant ces jours-là, et seules comptent les journées
que la cellule écrit : CDE chaudières 12 → 10, HKB meunerie 26 → 23, GST
fermentation 13 → 11 ; **23 couples au quota, inchangé**.

La nuit du 23/03, dernier jour de la première fenêtre, reste en manque sur
six postes : c'est la règle du client, la fenêtre se tient.

### Les fiches d'un ouvrier, et les grèves écrites « Abs »

Le client, le 26/09/2026, a transmis les fiches de LCI, ouvrier. Tout ce
qu'elles ont appris est dans `docs/regles-paie.md`, « La fiche d'ouvrier ».
`comparer-fiches.py` lit leur format et leur **détail jour par jour** :
214 journées confrontées, 202 identiques d'emblée.

**Trois « Abs » étaient des grèves** — « Grève reconnue » sur la fiche, et
l'usine le montrait seule : 15, 14 et 11 « Abs » ces jours-là contre 4 les
lendemains. Le client : « c'est bien grève, l'employeur ne paye rien ».
`GREVE_JOURS` fait de tout « Abs » du 10/02, du 12/05 et du 16/06 un code
`GREVE` (étiquette « GREV »), avec sa ligne de fiche et son entrée de
légende. Neuf règles, manques, Recyclage et compteurs **identiques à
l'octet** — maladie et grève sont toutes deux des absences —, 205 journées
sur 214 identiques aux fiches, et la maladie concorde désormais les quatre
mois où elle apparaît. Vérifié au navigateur sur LCI.

**Ce que cela ne fait pas** : retirer la journée du salaire. La rémunération
de l'application est FIXE ; une journée non payée — grève, sans solde,
absence injustifiée — y apparaît en heures sans rien ôter. Limite
antérieure, écrite dans `docs/regles-paie.md`.

### Une reprise partielle sort de la prime d'équipe

Le client, le 26/09/2026, devant la fiche de LCI du 17/06 —
`["DS-CE","1h rhs"]`, 7 h de nuit et 1 h de « Compensation payée » : les
heures reprises se paient sans prime. Règle et mesures dans
`docs/regles-paie.md`, « RHS ».

**Posée d'abord dans `parseHoraireEntry()`, elle n'a rien changé** : la
cellule de LCI ne nomme pas de poste, c'est le cycle qui le donne, dans
`lireJournee()`. Elle vit donc à la fin de celle-ci. **Et la première
version retranchait deux fois** : DWS le 25/03, `["8h-12h","4h rhs"]`,
tombait à zéro heure alors que sa plage dit déjà sa présence. Les heures
prestées valent au plus 8 − n.

178 journées chez 53 personnes, 377,5 h ; neuf règles, manques et compteurs
identiques à l'octet ; FPS gluten 9 → 8 au Recyclage ; `comparer-fiches` LCI
207 journées sur 214. Vérifié au navigateur sur juin, hors ligne compris.

### « PM · DS-CE » : quatre heures sans prime, « AM · DS-CE » : huit avec

Le client, le 26/09/2026. **La règle proposée d'abord — la même pour toute
cellule « poste + DS-CE » — aurait été fausse** : la fiche de LCI paie le
18/02 `AM · DS-CE` en journée pleine, le 25/08 `PM · DS-CE` en 4 h + 4 h. La
question posée avec les deux fiches côte à côte a donné la réponse. Détail
dans `docs/regles-paie.md`, « Le conseil d'entreprise d'un après-midi ».
Cinq journées, tout identique à l'octet sauf elles ; LCI 208 journées sur
214. La nuit est tranchée le 30/09/2026 : les heures prestées gardent la
prime que le commentaire écrit (celle de la pause prévue sinon), ce que
l'application faisait déjà.

### Un déplacement demandé garde la prime la plus élevée

Le client, le 26/09/2026, devant son relevé de pointage d'août : les 19 et
20/08 il a remplacé en AM sur une journée prévue PM, et garde la prime PM ;
le 30/08, même cellule, c'était un « échange » écrit dans la colonne du
COLLÈGUE, et il est payé AM. Règle : la prime la plus élevée entre la pause
faite et la pause prévue (cycle recalé), sauf échange. Détail et mesures
dans `docs/regles-paie.md`. **16 journées**, tout le reste identique à
l'octet ; 13 des 33 journées de cette forme disaient déjà « maintien
prime » — le classeur confirme la règle de lui-même.

**Un relevé de pointage** (« Sommaire mensuel ») vaut une fiche jour par
jour : horaire prévu (1A40 matin, 2A40 après-midi, 3A40 nuit), prime payée
(P11/P12/P13, P3x le samedi, P5x le dimanche), pointage IN/OUT. Il porte le
nom et le matricule : **il ne rentre pas dans le dépôt**, comme les fiches.

### Un rappel sur un repos se paie en heures sup

Le client, le 26/09/2026 : « la règle est la même pour tout le monde ». La
fiche de LCI le 11/04, `["-","N","rappel le 07.04"]` : aucune heure
normale, 8 h d'heures sup à compenser à 187,5 % et leur déduction, prime de
nuit majorée, repos payé. C'est sa règle du 25/09 — pas de « +FT » écrit,
donc le compteur d'heures sup.

`lireJournee()` pose `r.rs` et un code `nH HS` (9 à 12 h ajoutés au
barème) ; la journée garde poste et heures, si bien que placement, manques,
Recyclage et compteurs sont **identiques à l'octet** — seule la paie
change, dans `compute()`. **122 journées chez 46 personnes** ; écartées à
raison : six « +FT », et SPS le 17/04 dont la plage fait 9 h 30.

**Je l'ai d'abord mal demandé** : « j'attends ton ok pour appliquer la
lecture de la fiche » — le client n'a pas compris quoi ni pourquoi. La
question qui a marché montrait UNE journée, ce que l'application fait, ce
que la fiche porte, et « oui / non ». Toujours cette forme.

LCI le 13/04, `["N","22h-10h","Rappel…"]`, reste un écart : sa cellule
franche dit N, pas repos, alors que la fiche le paie en 12 h d'heures sup.

### Les mentions non comprises, lues par leur commentaire

Le 26/09/2026, en appliquant la règle « commentaires d'abord » : sur onze
mentions non comprises, **neuf** se sont résolues sans question. Sept se
lisaient déjà juste (`MENTIONS_NEUTRES` : `CPPT-F`, `SD26+R`, `R-CM/VM`,
`chaud. + F`, `R + F`, `+CPPT`) ou étaient un atelier (`liq - ferm`,
fermentation liquide) ; une était FAUSSE — JKS le 17/06, `DS + PM ·
4h +FT`, « réunion mensuelle Direction - délégation syndicale », comptait
4 h au lieu de 8 : le « PM » n'était pas lu, et la règle du +FT sur un
poste prévu ne s'appliquait pas (`COQUILLES`). Les manques, le Recyclage, les
compteurs et les fiches sont identiques à l'octet.

Les deux dernières se sont lues sans question non plus, parce que leurs
deux lectures possibles PAIENT PAREIL : TCE 20/02 `N · F-PM` (formation
l'après-midi, « remplacé par ATR remplacé par DKS ») est le F de la règle
de FLN ; VGG 25/02 `PM · SD26 -F` réunit deux codes de journée de jour.
**Zéro mention non comprise** dans le classeur ; seul le Recyclage bouge
d'une case (HKB meunerie 23 → 24, le rééquilibrage comblant la nuit du
20/02 que TCE a quittée).

« consign. » (BLR 22 au 24/07) quitte `ATELIERS` pour `MENTIONS_NEUTRES` :
les consignations de YRS, renfort avant en congé, faites en 7h-15h — une
tâche, pas un atelier. Rien d'autre ne bouge. Reste « Polyvalence » sur un
repos (LCI 23/09, SVE 21/09), sans aucun commentaire : question posée au
client le 26/09/2026 — venus travailler (A, heures sup ; B, payé
normalement) ou simple note (C).

### Changer de personne laissait des heures sup d'une autre

Trouvé le 26/09/2026 en rapprochant au centime la fiche de janvier de LCI :
l'application lui comptait 3 h d'heures sup que ni son horaire ni sa fiche
ne portent. Le pré-remplissage remplit d'abord la première personne de la
liste — AFA, rappelé sur un repos le 31/01 —, puis celle qu'on choisit ;
sur un repos, `remplirMois()` n'effaçait que `s`, `h`, `a` et `r`, et
laissait `ax`, `hsp`, `rs`, `rh`, `j`, `sp`, `q`. LCI héritait des heures
sup d'AFA, sursalaire et prime compris. Tous les champs écrits par le
pré-remplissage sont désormais effacés. Janvier de LCI passe de +71,57 € à
**−7,89 €** de brut — exactement la demi-heure sup « +0,5 hs » que son
commentaire du 14/01 porte et que l'application ne lit pas.

**Le rapprochement au centime trouve ce qu'aucun vérificateur ne voit** :
`verifier-calendrier.js` rejoue la lecture d'UNE personne à la fois, jamais
un changement de personne dans le même navigateur.

### Un férié presté se paie à 200 %, prime d'équipe comprise

Le rapprochement au centime des fiches de LCI (26/09/2026) : mai, le 21/07
et le 15/08 manquaient exactement « heures fériées × taux horaire », et la
prime d'équipe doublée. Le client : « c'est la même règle pour les employés
aussi ». Le supplément d'un férié en semaine passe de 100 à **200 %**, non
déduit ; un férié un **samedi** se paie comme un dimanche ; la prime d'une
heure fériée va au seau du dimanche. Mai, juillet et août de LCI concordent
alors **au centime** sur le brut ; le net des huit mois passe de −910 € (au
premier tableau) à −41 €.

**Comment on est arrivé au centime** : chaque paramètre de la fiche repris
dans l'application — le TAUX HORAIRE (26,1568 puis 26,5622, via une
rémunération de référence taux × 148,368 et l'écart de base en « autre
rémunération brute »), la réduction de précompte sur heures sup, le
volontariat fiscal sorti du précompte, la fraction 0,90 —, puis l'écart
rangé par rubrique, puis la rubrique ramenée à la journée. **Chaque écart
restant a une journée et une ligne de fiche**.

### Deux lectures de commentaire que la fiche a confirmées

Toujours le 26/09/2026, sur le rapprochement au centime de LCI :

- **les heures sup écrites en commentaire** — « +0,5 hs », « +3h hs » :
  trente journées de l'année, que l'application ne lisait pas. La fiche du
  14/01 les paie en heures sup à compenser, prime de la pause de la plage
  citée (`r.hc`, `r.hcp`) ;
- **deux rappels à deux dates** dans le même commentaire — « Rappel le
  07/04 + rappel le 13/04 » : deux primes, 12 h 05 d'heures de déplacement
  sur la fiche (`secondRappel()`, `rec.r2`). Une date recopiée ne compte
  qu'une fois.

Résultat sur LCI : **brut au centime** en janvier, mai, juin, juillet et
août ; février +0,90 € (le 20/02), mars −0,36 €, avril −5,40 € ; **net à
moins de 8 € chaque mois**, le reste étant un précompte de 6 à 11 € plus
bas que la fiche. Neuf règles, manques, Recyclage et compteurs identiques.

### Les quelques euros de net : le calage, l'indemnité, une journée de flex time

Le client, le 26/09/2026 : « d'où viennent les quelques euros de
différence ? ». Trois causes, et **quatre mois sur huit tombent alors au
centime sur le NET** (janvier, mai, juillet, août).

- **Le précompte suit le barème de l'application À UNE CONSTANTE PRÈS**, la
  même sur les huit fiches : une seule valeur de « Calage barème » les
  reproduit toutes au centime, sans arrondi par tranche de 15 €. L'écart de
  6 à 11 € n'était que le calage par défaut, qui vient d'une autre fiche.
  **Rien à coder** : c'est le réglage personnel prévu pour cela, et l'onglet
  Contrôle le recalcule depuis le précompte d'une fiche. Ce qui variait
  d'un mois à l'autre venait de la base : l'indemnité imposable.
- **L'indemnité de déplacement change de taux** d'un mois à l'autre sur les
  fiches, avec une régularisation une fois. C'est le champ du mois
  « Indemnité déplacement / jour ». **La fiche simulée écrivait le taux des
  Réglages** à côté du montant calculé au taux du mois : elle écrit
  désormais celui du mois.
- **Une reprise de flex time d'une journée entière comptait comme une
  journée de présence** : le 01/03, « 8h -FT, remplacé par GDT », donnait
  un chèque-repas et une indemnité de déplacement. La fiche n'en porte
  aucun — 18 jours pour 19. Les heures restent payées depuis le compteur
  (section 6 de `docs/conversion-horaire.md`), mais **le chèque et
  l'indemnité se comptent sur les heures PRÉSENTES**. 212 journées chez
  52 personnes ; neuf règles, manques, Recyclage et compteurs identiques à
  l'octet.

Restent : février +0,40 € (le 20/02), mars −1,25 € (un chèque de
récupération de flex time, question ci-dessous), avril −5,68 € (trois
chèques et les journées connues), juin +2,26 € — la régularisation
d'indemnité, que la simulation a saisie en « autre indemnité nette », non
imposable, alors que la fiche l'impose.

### Les compteurs CP, TP, CT comptent les journées posées

Mesuré le 26/09/2026 : le compteur du pied de feuille est le nombre de
journées DÉJÀ POSÉES, et « à planifier » (ou « solde à planifier ») ce qui
reste du droit de l'année — LCI 25 posées dans l'horaire pour un compteur
de 25 et 1 à planifier, GSK 51 et 51 et 1.

**RCO en a une de plus dans l'horaire** : 27 journées `CP` pour un compteur
de 26 et rien à planifier. Le client, le 26/09/2026, entre le 01/01 et le
11/11 — les deux fériés de la série : **le CP du 01/01 ne compte pas** (jour
férié, ou compté sur 2025). Le 11/11, lui, compte.

**Rien n'est codé** : l'application affiche les compteurs du classeur tels
quels et ne les recalcule pas. Si un jour elle les recompte depuis les
journées, cette journée-là est l'exemple à reproduire — et un férié ne
suffit PAS à l'écarter, puisque le 11/11 reste dans le compte.

### Ce qui attend le client

L'audit a trouvé des informations que le classeur porte et que l'application
ne sait pas encore interpréter. **Elles sont toutes dans le brut**, et rien
n'est deviné à leur sujet :

- **les lettres G et H** du degré de polyvalence — la fiche d'ouvrier
  porte une « Classification entreprise » qui commence par la même lettre ;
- **les fiches d'ouvrier de LCI** (26/09/2026) — les grèves sont tranchées
  (`GREVE_JOURS`), le `+FT` sur un poste prévu aussi (voir
  `docs/conversion-horaire.md`, section 5 : +240 h chez 52 personnes), la
  reprise partielle et le « PM · DS-CE » aussi. Restent, en attente d'une
  réponse :
  - ~~la nuit avec « DS-CE » ou « D-CPPT »~~ : tranchée le 30/09/2026,
    « pas obligatoirement la prime de nuit, mais la prime qui est bien
    indiquée dans le commentaire » — ce que l'application faisait déjà
    par la prime conservée (AFA 25/02, JKS 25/03, QBY 15/04), rien n'a
    changé dans le code ;
  - la paie à l'heure elle-même — voir `docs/regles-paie.md`, « La fiche
    d'ouvrier » ;
  - **LCI le 17/03** : 1 h sup sur la fiche, `["AM"]` dans l'horaire, la
    veille `AM · VM` — l'heure de visite médicale hors horaire ? (−13,29 €) ;
  - ~~le départ anticipé sans code~~ et ~~« Polyvalence » sur un repos~~ :
    tranchés le 29/09/2026, voir « Les réponses du 29/09/2026 » ;
  - **le tableau des salaires de VBN** fiche contre application, comme celui
    de LCI. **« absentes de ce conteneur » était faux** (relevé le
    07/10/2026) : les fiches de VBN (contrat 200237, employé) de
    décembre 2025 à août 2026 sont dans les envois de la session, avec
    celles de LCI (200218, ouvrier) de janvier à août — mensuelles,
    deux régularisations de février, prime de fin d'année, pécule et
    deux documents 2025 scannés. Elles restent hors du dépôt.
    **Fait le 07/10/2026**, janvier à août, SANS rien caler : la session
    du 27/09 versait le reste de chaque mois en « autre rémunération
    brute », ce qui égalisait le brut et ne mesurait rien. Juillet et
    août tombent au centime ; chaque autre écart de brut a sa rubrique
    et sa journée (reste non attribué : zéro). Le férié (fixe + 100 %
    chez l'employé, 200 % dans l'application : 01/01, 06/04, 01/05,
    25/05) fait l'essentiel de janvier, avril et mai — question
    ci-dessous, inchangée. Le reste : le rappel du 25/06 (déjà listé) ;
    une heure et demie (janvier) et trois quarts d'heure (avril) d'heures
    sup que le classeur n'écrit pas ; le dimanche 22/03 payé 10 h 17 de
    nuit au lieu de 8 h ; la durée des heures de déplacement du 20/03 et
    du 14/04 ; un chèque-repas de plus ou de moins sur quatre mois ;
    deux questions au client, juste dessous ;
  - **VBN le 19/02**, `["18h-06h","8h +FT","remplace FPA rappel le
    19.06 …"]` : la fiche paie un rappel (6 h 17 de déplacement), et
    `momentRappel()` refuse une date de rappel POSTÉRIEURE au jour.
    « 19.06 » pour « 19.02 » ? **Tranché le 07/10/2026** : « j'ai fait
    12h avec rappel le 19.02 et non 19.06 ». `RAPPEL_DATE_TRANCHEE`
    corrige la date pour cette journée seulement (une date postérieure
    au jour reste refusée ailleurs). Les quatre sorties du vérificateur
    sont identiques à l'octet — la règle est de paie seulement ; février
    passe d'un écart de près d'une centaine d'euros de net à moins de
    dix (un chèque-repas, un jour d'indemnité, quelques minutes de
    déplacement). Neuf autres journées de l'année portent une date de
    rappel postérieure au jour (JBI 08/03, VGG 26/05, SKS 26/06, PAM
    15/03, 28/06 et 01/07, RCO 25/07, GDT 15/03, PLZ 28/04) — certaines
    sont des nuits qui finissent le lendemain ; non tranchées ;
  - **les 21 et 22/03 de VBN**, `["R-CM","18h-6h","remplace GPS;
    remplace aussi YBT"]` : la fiche de mars paie 4 h à 187,5 % et 4 h
    à 200 % en « HS pas compenser » (sursalaire ET heure, sans
    déduction), là où l'application paie le sursalaire et déduit
    l'heure, versée au compteur HS. **J'ai d'abord attribué ces 8 h au
    19/03, et c'était faux** : le client, le 07/10/2026, « il est
    indiqué +8 FT pour le 19/03 et rappel le 06/03 » — ces 8 h-là vont
    au flex time (0 h payée, ce que l'application fait), et seul le
    rappel se paie. Ce sont les 4 h au-delà de 8 des deux nuits de
    12 h du week-end, mêmes taux des deux côtés. Payées ou au
    compteur : le classeur ne l'écrit pas. Le client, le 07/10/2026 :
    « si rien n'est indiqué ce sont logiquement des HS, sinon il serait
    indiqué FT+ » — c'est la règle du 25/09, et l'application la suit
    déjà (HS, pas flex time). Reste ce qu'elle ne tranche pas : les
    fiches de VBN portent DEUX traitements d'heures sup, « à compenser »
    avec déduction de l'heure (janvier, 1 h 30) et « pas compenser »
    sans déduction (mars, 8 h ; avril, 0 h 45). Ce qui fait passer de
    l'un à l'autre est redemandé au client. Il répond le 07/10/2026 :
    « on a une date limite pour reprendre ses HS, sinon elles sont
    payées ». **Mesuré sur les 24 fiches** : LCI (ouvrier) n'a QUE des
    « à compenser » (janvier, mars, avril), son solde d'heures sup
    monte à 21 h en mai-juin et redescend par ses « Compensation
    payée » (21/02, 06/04, 18/06, 05/07, 26/08) — jamais rien de payé
    d'office. VBN (employé) a des « à compenser » en décembre 2025 et
    janvier, son solde tombe à 0 sur la fiche de février, qui porte
    une ligne « Recup à payer » presque entièrement annulée par la
    régularisation du 09/03 ; à partir de mars, ses heures sup sont
    « pas compenser » le mois même et son solde reste à 0. La date
    limite n'explique donc pas mars à elle seule : demandé au client
    quelle est cette date et si le changement de VBN en février est
    un choix ou une règle d'employé. **La date limite**, le client le
    07/10/2026 : « fin février pour celles faites dans l'année et fin
    mars pour celles faites durant le mois de février » — détail dans
    `docs/regles-paie.md`, « La date limite des heures sup » ; l'année
    des heures sup court de mars à février, confirmé le même jour. Elle
    explique le solde remis à zéro en février (LCI par une reprise, VBN
    par une ligne « Recup à payer ») ; elle n'explique pas les nuits des
    21-22/03 de VBN payées « pas compenser » le mois même. **Codé le
    07/10/2026** : `echeanceHS()` paie le reste du compteur sur les
    fiches de février et de mars (« Recup à payer »), voir
    `docs/regles-paie.md` ; vérificateur identique à l'octet ;
  - restes connus du rapprochement de LCI, sans question posée : le 13/04
    (cellule `N`, payé 12 h sup), la prime de rappel du 20/03 (fiche
    6 h 25 = 170,44 €, application 183,37 €) ;
  - **trois chèques d'avril** : la fiche en porte 9 pour 12 journées
    indemnisées. Les deux journées payées entièrement en heures sup (11 et
    13/04) en expliquent sans doute deux ; la troisième est l'une des
    demi-journées du 05, du 08 ou du 15/04 ;
- **la fiche de septembre de VBN** (reçue le 09/10/2026, rangée dans
  `CronoBots/groups-fiches`) : VBN passe contremaître, avec une nouvelle
  rémunération fixe. Comparée sans calage, chaque écart de brut a sa
  ligne, et la somme ne laisse aucun reste :
  - le fixe payé dépasse « fixe × 0,90 » d'exactement la moitié de
    « hausse × 0,90 » : c'est sans doute un rappel de la hausse pour
    une demi-quinzaine d'août. Hypothèse à faire confirmer ;
  - le 30/09, `["D-CPPT","2h RTT","+1h RHS compteur à 0 Arrivée à 09h
    Départ à 15h"]` : la fiche paie la prime du **matin** pour les 6 h
    (38 h de matin contre 32 h, 64 h de nuit contre 70 h). L'application
    garde la prime de nuit de la pause prévue, puisque le commentaire
    n'en nomme aucune. Ma règle du 30/09 « celle de la pause prévue
    sinon » est donc démentie par la fiche. Question posée au client ;
  - le même jour, la fiche paie **0 h 30** d'heures sup à compenser.
    L'application en paie 1 h, à la prime de nuit, comme le client l'a
    dit le 01/10 (« + 1 h sup faite après 15 h »). Question posée ;
  - les primes diverses : la fiche porte bien plus que les 4 primes de
    remplacement de contremaître (R-CM des 01, 07, 08 et 09/09), et le
    reste ne correspond pas à un nombre entier de primes. Question
    posée ;
  - indemnités : 17 jours sur la fiche contre 18 dans l'application,
    plus une ligne « Indemn. déplacement/vélo » de 50 km, qui se saisit
    dans le mois (`kmVelo`).
- **la paie de l'ouvrier** (09/10/2026, voir « La paie à l'heure de LCI,
  revérifiée ») : ~~réduction du temps de travail non payée~~ — tranché
  par la note explicative de la fiche de paie (« non payé pour les
  ouvriers »), appliqué le 09/10/2026, voir `docs/regles-paie.md`, « Les
  deux notes internes ». Restent : vacances payées par la caisse et non
  par l'employeur ? maladie du week-end majorée comme le poste prévu ? ;
- **le D de la grille** (09/10/2026) : la note sur les repos écrit D =
  7h30-16h (une demi-heure de midi non payée) ; le client avait dit le
  28/09 « seulement D : 7-15 ». Lequel vaut aujourd'hui ? La note date de
  2009 ;
- **la RJF de l'ouvrier** : la note ne la nomme pas — payée comme un férié
  (salaire moyen) ou au garanti ?
- ~~le repos payé lié au week-end~~ : codé le 09/10/2026 à la demande du
  client (« optimise tout ce qui peut l'être avec ces documents »), avec le
  férié presté de l'ouvrier payé une seule fois ; voir
  `docs/regles-paie.md`, « Les deux notes internes ». Prestation et repos
  concordent sur cinq mois de LCI ; les restes ont chacun leur journée ;
- **le férié d'un employé** (27/09/2026) : les fiches de VBN paient
  « fixe + 100 % » (supplément non déduit) le 01/01 travaillé ET les trois
  fériés en « 8h -FT » (06/04, 01/05, 25/05) ; celles de LCI, ouvrier,
  200 % sur ses cinq fériés travaillés. L'application applique 200 % à
  tous. Le client : **attendre la fiche d'un autre employé** avant de
  distinguer les statuts. Un seul vrai férié travaillé chez l'employé —
  je l'avais d'abord annoncé comme quatre ;
- ~~une cellule vide et un commentaire qui doute~~ : tranché par le
  classeur le 29/09/2026, sans question. VGG le 09/08,
  `["","","Remplace YBT qui remplaçait BLR ?"]` : BLR porte « Remplacé par
  VGG ? remplacé par TCE », TCE « remplace BLR ; rappel le 6/8 ». C'est TCE
  qui est venu, et le relevé de VGG dit repos. `lireJournee()` ne lit plus
  de poste sur une cellule ET une annotation vides dont le commentaire
  finit par « ? » — seule journée de l'année de cette forme. Prestées
  14 448 → 14 447, repos +1 ; sous-effectifs, Recyclage et compteurs
  identiques à l'octet ;
- **le rappel sur un repos d'un EMPLOYÉ** : VBN le 25/06, la fiche ne
  porte aucune heure sup mais 13 h 16 d'« Heure de déplacement » au taux
  plein ; l'application paie 7 h sup. Les relevés (JBI, codes U) disent
  heures sup. À trancher avec une autre fiche d'employé ;
- ~~« remplace Y » sans rien chez Y~~ : tranché le 29/09/2026 (B), voir
  « Les réponses du 29/09/2026 » ;
- ~~le D seul sans heure écrite~~ : tranché le 28/09/2026, 7-15 (voir
  « Seulement D : 7-15 »). Restent sans horaire les journées à code
  (D-CPPT, DS-CE, F) : 10 présences d'ici la fin de l'année. A : (7h30-16), l'horaire de jour de la grille.
  B : un horaire propre à chaque fonction (contremaître, opérateur,
  formation). C : (D), sans heures ;
- ~~les deux heures du projet falling film~~ : tranché le 29/09/2026, voir
  « Les réponses du 29/09/2026 » ;
- ~~le doublage de 12 h pour couvrir une absence~~ : tranché le
  29/09/2026 (A), voir « Recherche par pause et par poste » ;
- **les soldes flex time sous −8 h** (09/10/2026) : la note du 18/09/2024
  fixe le minimum à −8 h, et onze personnes sont en dessous au jour J
  (jusqu'à −49 h). Le minimum est-il appliqué, ou ces soldes comptent-ils
  des −FT remplacés (remarque 3 de la note) ? Les compteurs les marquent
  en rouge en attendant ;
- **les 51 matricules** de « Polyvalence » vivent dans le dépôt public, à côté
  du trigramme. Ce fichier les tolère (« initiales ou matricule ») ; s'ils
  figurent sur les fiches de paie, ils relient le trigramme à la personne.

### Les réponses du 29/09/2026

**Un départ anticipé sans code est une reprise (RHS).** Le client : « A :
toujours en RHS ». `lireJournee()` lit « départ à Xh » — fautes de frappe
comprises, « D2PART 0 18H » — et verse les heures du départ à la fin du
poste au compteur de récup. HS (`rhsJ` → `rec.rh`), sans prime ; les
heures prestées baissent d'autant. La fin d'un D est 15 h (« seulement D :
7-15 »), **16 h pour les consignateurs** : YRS l'écrit lui-même le 08/01,
« départ à 15h30 - RHS ». Seulement sur une journée pleine dont la cellule
franche est un poste, sans aucun autre code (RTT, DTT, VA, CSS, ±FT, RHS
chiffré) ni code de jour, et pas quand le commentaire remplace quelqu'un
AVANT le départ — c'est alors l'autre qui part. **Cinq journées** : LCI
05/04 (4 h, comme sa fiche), VGG 23/07 (2 h, comme son relevé), BLR 28/08
(2 h), YRS 09/01 (1 h 15) et 08/01 (0 h 30). Neuf règles, `--manques 0929`
et `--compteurs` identiques à l'octet ; Recyclage : VGG chaudières 3 → 2
(le 23/07 n'est plus une journée pleine). VGG le 15/05 reste un écart
connu : sa cellule `["AM","R-CM","Remplace AFA"]` ne dit pas le départ.

**« Polyvalence » sur un repos est une note.** Le client : « le mot
polyvalence veut juste dire qu'à partir de ce jour-là ils ont changé de
poste pour commencer leur formation à un autre poste ». Les deux journées
(LCI 23/09, SVE 21/09) se lisaient déjà en repos ; la mention entre dans
`MENTIONS_NEUTRES`, et la règle « mention avalée » du vérificateur ne
compte plus une mention neutre (2 → 0, règles faibles 50 → 48). **La date
n'est pas posée dans `FORMATION_DEBUT`** : le poste d'avant de SVE n'est
écrit nulle part, et LCI tient la fermentation jusqu'au 29/09 par décision
du client (`POSTE_PERIODE`).

**Un opérateur en formation rappelé pour remplacer prend la place du
remplacé.** Le client, devant le terrain arrière vide de la nuit du 02/10 :
« la réponse est pourtant dans le fichier ». Elle l'était : SKS porte
`["-","N","Remplace SBZ …"]`, et SBZ tient le terrain arrière. SKS, en
formation meunerie depuis le 21/09, y est validé (fermentation et
distillation) ; mais la ligne 9 le rangeait en meunerie, en plus, avant
que quoi que ce soit lise son commentaire. **J'avais proposé SKS comme
« piste » le 28/09 au lieu de lire sa cellule** : la règle « les
commentaires d'abord » vaut aussi pour le placement. `postesDePause()`
lit donc `atelierDuRemplace()` AVANT `posteTenu()` pour un opérateur en
formation — la règle du client du 21/09, « on le rappelle pour remplacer
dans un poste qu'il peut, et ce sera marqué en commentaire » —, à
condition qu'il ait la polyvalence et que la cellule n'écrive pas
l'atelier. Le même soir LHR, « Remplace SPT », passe des chaudières (en
plus) au gluten. Neuf règles et compteurs identiques à l'octet ;
sous-effectifs d'ici la fin de l'année **7 → 6** (le 02/10 disparaît) ;
sur l'année, 277 → **269** places creuses, 174 → 171 journées ;
Recyclage : les journées où un stagiaire remplaçait comptent à son poste
validé (GST fermentation 11 → 16, LHR gluten 3 → 7, SVE gluten 1 → 2,
HKB et LHR meunerie +1) et JKS fermentation 10 → 9, qui ne comble plus la
place ; **22** couples au quota au lieu de 23.

**Les deux heures du projet falling film sont des HS, à la prime de
l'autre pause.** Le client : les opérateurs choisiront HS ou FT+ sur une
feuille de demande, et « si FT+ il sera marqué dans l'horaire en
commentaire » ; puis « ceux qui font le matin auront la formation après
14h et ceux qui font PM avant 14h ». `lireJournee()` pose donc 2 h sup
(`r.hc`, le mécanisme des « +0,5 hs » écrits) sur une journée « projet
falling film » : prime d'après-midi après un matin (14 h-16 h), prime du
matin avant un après-midi (12 h-14 h). Seulement pour qui TIENT sa pause :
pas un « remplacé par » (5 journées), pas une plage de jour ni « D-F » ni
un repos (6), et rien si un flex time est écrit. **21 journées sur 33**,
les 05, 09, 15 et 26/10. La première version laissait passer les
« remplacé par » : `\w` ne reconnaît pas le « é » en JavaScript sans
`/u`, le piège déjà écrit pour « éq ». Neuf règles, sous-effectifs,
Recyclage et compteurs identiques à l'octet (la règle est de paie
seulement) ; la fiche d'octobre de VBN porte ses 2 h du 15/10 à la prime
d'après-midi, hors ligne compris.

**« remplace Y » sans rien chez Y : Y était ailleurs à l'usine.** Le
client : « B : FLI ailleurs ». Rien à coder : l'application montre déjà
les deux présents (16 journées), ce qui est juste.

**L'historique public porte encore les 60 identifiants** — trois versions de
`data/classeur-2026.xlsx` et six de `data/horaire-2026.json`. Le purger est
une décision du client, comme pour les noms (`docs/purge-historique.md`).

## Structure

| Fichier | Rôle |
|---|---|
| `index.html` | toute l'application (HTML, CSS, JS dans une IIFE) |
| `data/horaire-2026.json` | horaire d'équipe anonymisé, pour le pré-remplissage |
| `data/classeur-2026-brut.json` | le classeur ENTIER en JSON — réserve, non chargée par l'application |
| `tools/anonymiser-classeur.py` | recopie le classeur en remplaçant les noms par les trigrammes |
| `tools/anonymiser-classeur.ps1` | le même, en PowerShell, pour les postes sans Python |
| `tools/verifier-anonymat.py` | cherche les noms de la source dans la sortie, sans rien emprunter à l'anonymiseur |
| `tools/verifier-depot.py` | cherche des formes de nom dans le dépôt lui-même, arbre et historique |
| `tools/formes-admises.txt` | les formes de nom qu'un humain a regardées et jugées innocentes |
| `tools/survivants-admis.txt` | les survivants de `verifier-anonymat.py` qu'un humain a lus et jugés innocents |
| `tools/mettre-a-jour.py` | toute la procédure en une commande, derrière huit portes |
| `tools/mettre-a-jour-recyclage.py` | le classeur RH des recyclages, même démarche, onze portes |
| `tools/convertir-horaire.py` | convertit le récapitulatif Excel en JSON |
| `tools/exporter-classeur.py` | recopie TOUT le classeur anonymisé en JSON, sans rien interpréter |
| `tools/verifier-integralite.py` | confronte l'horaire au classeur entier : ce qui ne lui arrive pas |
| `tools/comparer-horaire.py` | dit ce qui change entre deux versions converties |
| `tools/comparer-fiches.py` | confronte les fiches de paie à ce que l'horaire produit |
| `tools/extraire-fiches.py` | recopie toute une fiche de paie en JSON, sans rien d'identifiant — sortie hors du dépôt |
| `tools/verifier-calendrier.js` | vérifie le calendrier, les compteurs et les manques d'effectif |
| `tools/anonymiser-sommaire.py` | repeint le nom, le matricule et la section d'un relevé de pointage scanné, trigramme à la place |
| `tools/lire-pdf.py` | extrait le texte d'un PDF, sans dépendance |
| `docs/conversion-horaire.md` | les règles de lecture de l'horaire |
| `docs/regles-paie.md` | les règles de calcul confirmées par le client |
| `sw.js` | cache et fonctionnement hors ligne |
| `logo.png` | le logo Biowanze, source des icônes — ne sert pas à l'application |

## Contrôler contre les fiches de paie

Deux chemins indépendants mènent au même mois : la fiche du secrétariat
social, et les journées lues dans le récapitulatif. Les confronter est le
contrôle le plus sévère dont on dispose.

```bash
python3 tools/comparer-fiches.py VBN /chemin/vers/fiches/*.pdf
```

**Les fiches ne rentrent JAMAIS dans le dépôt** : elles portent le nom, le
numéro de registre national et l'IBAN. L'outil les lit sur place et n'en
ressort que des heures. Il écarte de lui-même les fiches d'une autre année —
décembre se paie en janvier.

**Il garde sa PROPRE copie de la découpe de `index.html`**, et elle s'est
déjà désynchronisée en silence : une constante ajoutée dans `index.html`, et
l'outil s'arrêtait sur une `ReferenceError` au milieu d'une comparaison. Il
met donc désormais sa découpe à l'épreuve avant de s'en servir, comme
`verifier-calendrier.js`. **Toute modification de `parseHoraireEntry()` ou de
ce qui l'entoure demande de relancer cet outil**, ne serait-ce qu'à vide :

```bash
python3 tools/comparer-fiches.py VBN
```

**ET L'ÉPREUVE À VIDE N'ÉPROUVAIT RIEN.** Découvert le 25/09/2026, en
vérifiant la logique à la demande du client. `main()` sortait en **2** sur
`len(sys.argv) < 3` — c'est-à-dire AVANT d'appeler `horaire()`, qui est la
seule chose qui met la découpe à l'épreuve. La commande que cette page
prescrit depuis toujours, `python3 tools/comparer-fiches.py VBN`, imprimait
son mode d'emploi et s'en allait. **Une consigne écrite ici était fausse**,
et j'ai annoncé « découpe à l'épreuve » dans un message de commit sur la foi
de cette sortie-là.

La forme à un seul argument appelle désormais `horaire()` et rend compte :
`0` et le nombre de mois lus si la découpe tient, `1` si elle ne rend rien,
et l'erreur de node si elle casse. Éprouvé dans les deux sens le
25/09/2026 — un `JOUR_PRIME_PAUSE` saboté fait sortir l'outil en 1, le
fichier sain en 0 avec ses douze mois.

**Et il faut que son cri s'entende.** Le script node s'arrête bien quand sa
découpe est faussée — c'est tout l'intérêt de ses épreuves — mais son
enveloppe Python faisait `json.loads(r.stdout or "{}")` : elle rendait un
dictionnaire vide, et l'outil annonçait sereinement zéro mois lu. La panne
était silencieuse pendant deux commits, qui ont annoncé « fiches d'accord »
sans que rien ne l'ait été. `horaire()` lève désormais une exception avec le
message de node. **Une panne silencieuse est pire que pas de contrôle.**

### Cinq notes de service, et le solde flex time du jour

Le client, le 09/10/2026 : cinq notes de service internes (flex time 2021
et 2024, congé par heure en production 2022, absence imprévue 2025, temps
partiels 2025), « à garder en privé et utiliser pour optimiser l'app ».
Quatre sont des **scans** : Tesseract n'a pas le français dans ce conteneur
et le proxy refuse de le télécharger (403) ; les neuf pages ont été lues
une à une. Rangées dans `CronoBots/groups-fiches/regles/`, métadonnées
vidées — elles portaient les identifiants de connexion de l'auteur et du
copieur —, transcrites dans `regles/notes-internes.md`. Les règles, sans
nom, sont dans `docs/regles-paie.md`, « Les notes de service du
09/10/2026 » : la plupart confirment ce qui est déjà codé.

**Ce qui est codé : le solde flex time AU JOUR J**, dans l'onglet
Compteurs. La note de 2024 borne le compteur à −8 h et 104 h sur le solde
« à la pointeuse, situation au jour J » — les reprises planifiées plus tard
n'en déduisent rien — et demande de redescendre à 80 h au-delà. L'onglet ne
montrait que les heures portées et reprises de l'année, jamais un solde.
`compteursCalcules()` prend un troisième argument facultatif (MMJJ) et
compte à part les ±FT jusqu'à ce jour ; le solde = report + portées −
reprises au jour de l'usine, et une tuile donne le 31/12, reprises
planifiées comprises. Une phrase dit l'état : dans les bornes, au-dessus de
80 h (jaune), au-delà de 104 h ou sous −8 h (rouge). Le vérificateur appelle
la fonction à deux arguments : ses quatre sorties sont identiques à
l'octet. Mesuré au navigateur le 09/10 sur les 78 personnes : **aucune
au-dessus de 80 h, onze sous −8 h** (PDR −49, TCE −37, CGI −32, PAM −20,
ASS −19, DBE −16, AAI −12, PLZ −11, LHR et CDE −10, RDT −9) — question au
client, ci-dessous. ATA 60 h, VBN 7 h. Rien ne sort de l'écran à 320 (hors
ligne), 390 et 1280 px ; les seuls débordements sont dans les tableaux qui
défilent déjà de côté.

**La suite, le même jour** : sept documents de plus (la note explicative
du relevé mensuel, la filière intérimaires de 2017, la procédure des
primes de rappel, la prime de garde de janvier et de septembre 2026, les
montants des primes ponctuelles 2026 ; la fiche de paie et les repos
étaient déjà rangés, texte identique). Rangés dans `regles/` du dépôt
privé, métadonnées vidées ET commentaires JPEG des scans retirés — ils
portaient le nom du copieur. Résumé dans `docs/regles-paie.md`, « La
suite, remise le même jour ». **Rien n'est codé** : la procédure de rappel
est celle déjà appliquée, la garde et les primes ponctuelles ne touchent
pas les pauses. Deux pistes pour le client : le code `V` du relevé
(heures sup volontaires, payées sans récupération) explique sans doute les
« pas compenser » de VBN ; et les rappels pourraient proposer les
permanents avant les intérimaires, comme le veut la note de 2017.
Le client, le même jour : il pose la question des heures sup au bureau
RH, et a demandé ses relevés de prestations officiels de toute l'année.
**À leur arrivée** : chercher `V` ou `U` les 21 et 22/03 (nuits de 12 h,
« pas compenser » sur la fiche), en janvier (1 h 30 « à compenser ») et en
avril (0 h 45 « pas compenser ») ; les ranger dans le dépôt privé, jamais
ici (nom et matricule).

**Les permanents avant les intérimaires** (le client, le 09/10/2026 :
« il faut toujours proposer les permanents avant les intérimaires », la
règle de la note de 2017). `permanentsDabord()` range chaque liste de
propositions — en D, changement de pause, prolongation 12 h, et les
remplaçants du congé en heures — permanents d'abord, ordre d'origine
gardé ; les rappels d'intérimaires ont leur cadre à eux, « Rappel -
Intérimaire · Repos / Veille X », après tous ceux des permanents.
`estInterim()` lit `statutAffiche()`. Mesuré au navigateur sur les 110
cadres des sous-effectifs : aucun permanent après un intérimaire, SMK seul
dans « Rappel - Intérimaire · Veille N ». Vérificateur identique à
l'octet (il ne découpe pas ces modules) ; rien ne déborde à 320 (hors
ligne), 390 et 1280 px.

### Toutes les fiches, recopiées une fois pour toutes

Le client, le 09/10/2026 : « garde quelque part toutes les infos des fiches
de paie, afin de pouvoir réutiliser les chiffres pour toute une série de
vérifications ». `comparer-fiches.py` ne garde que des heures, le temps
d'une comparaison ; `tools/extraire-fiches.py` recopie la fiche ENTIÈRE :

```bash
python3 tools/extraire-fiches.py CONTRAT=TRI,CONTRAT=TRI /hors/du/depot/fiches-2026.json FICHE.pdf …
```

**Il lit par la POSITION des mots** (pymupdf), pas par le flux de texte, qui
mélange les deux colonnes : à gauche les lignes de rémunération et de
retenue (quantité, libellé, code A/B/D/F/G, montant) et les bases ; à droite
les informations générales, les soldes d'année et le détail des jours ; la
ligne « EUR » du récapitulatif ; les prestations jour par jour d'un ouvrier.
Le compte individuel annuel se lit par trimestre, et ce qui n'a pas de
structure connue (une page scannée) est recopié mot par mot avec sa
position.

**Le contrôle de fidélité est la fiche elle-même** : sur les 21 fiches
mensuelles de VBN et de LCI, la somme des lignes extraites redonne le TOTAL
imprimé des rémunérations ET des retenues, et le récapitulatif se boucle
(brut − ONSS = imposable, − précompte = net, + divers = net à recevoir).

**Ce qui ne sort jamais** : le bloc nom et adresse, le numéro de registre
national et la date de naissance qu'il contient, le numéro de contrat
(remplacé par le trigramme donné), l'IBAN et le BIC, la référence de
diffusion. **La garantie** relève tout cela sur les fiches elles-mêmes et
le cherche en mots entiers dans la sortie ; un seul, et rien n'est écrit.
**Elle a fermé trois fois à la mise au point, et à raison** : la ligne du
virement (IBAN) entrait dans les informations générales, l'en-tête du
compte individuel (contrat) dans ses trimestres, et des montants pris pour
le bloc adresse.

**La sortie porte des montants de salaire** : l'outil refuse de l'écrire
sous la racine du dépôt, et refuse une fiche qui serait dans le dépôt.
**Elle vit dans le dépôt PRIVÉ `CronoBots/groups-fiches`** (le client, le
09/10/2026, « garde toutes les infos utiles pour vérifier les prestations et
payes »), `fiches/fiches-2026.json`, avec sa propre note `CLAUDE.md`. Une
session qui doit vérifier une paie l'attache (`add_repo`) et le lit ; rien
n'en revient ici que des règles écrites avec des lettres. L'application
Claude ne peut pas créer de dépôt : c'est le client qui l'a créé. **Les
fiches ne se poussent jamais sur un git**, même privé, même pour les retirer
ensuite : elles portent le nom, le registre national et l'IBAN.

Les deux documents de VBN datés du 24/02 que le texte ne lisait pas sont les
**fiches fiscales 281.10 et 281.18 de 2025**, scannées : l'OCR en lit mal
les montants, et les mêmes totaux 2025 (imposable, précompte, heures sup)
sont en texte dans le compte individuel 2025, extrait sans erreur.

### La paie à l'heure de LCI, revérifiée le 09/10/2026

Le client : « vérifie les prestations et salaires ». Depuis la fin
septembre, l'application paie un OUVRIER à l'heure (`salHorGaranti`,
`salHorMoyen`, la branche `ouvrier` de `compute()`) ; la comparaison du
26/09 calait encore une rémunération fixe, et ne mesurait donc plus rien.
Elle est refaite sans calage, avec le taux garanti et le taux moyen imprimés sur
chaque fiche (lus dans `CronoBots/groups-fiches`) : brut identique en
janvier et en juin, trop haut les autres mois. **Jour par jour, la lecture
de l'horaire concorde** — un jour presté est un jour d'« heures normales »,
une absence une absence, un repos un repos, et les heures des jours prestés
sont les mêmes à cinq journées près, toutes déjà connues (14/01, 20/02,
17/03, 20/03, 13/04). Les écarts sont des RÈGLES DE PAIE d'ouvrier que
l'application n'a pas :

- **les vacances ne sont pas payées par l'employeur** : « Congé Légal »
  porte des heures sans montant sur les huit fiches (16 h en février, 44 h
  en avril…) — chez l'ouvrier, c'est la caisse de vacances qui paie.
  L'application les paie au taux garanti ;
- **la réduction du temps de travail n'est pas payée** : « RED TEMPS TRAV
  NON PAYE » au détail des jours, « Réduction Temps Travail » sans montant
  (6 h en avril, 8 h en mai). L'application la paie ;
- **une maladie un samedi se paie à 150 %, un dimanche à 200 %** : « Heures
  SHG Maladie à … à 150% / à 200% » les 02-03/05 et 11-12/07.
  L'application paie toute la maladie au taux moyen simple ;
- **chaque jour de week-end presté donne un jour de repos payé en
  semaine** : « Jours de Compensation » = jours de « JOUR DE REPOS PAYE »
  du détail, et ils suivent les jours de week-end prestés (6/6 en janvier,
  5/5 en février, 4/4 en avril, 6/6 en août). Ce sont des repos « - » de
  l'horaire, jamais choisis au hasard : 33 repos de semaine payés, 13 non.
  L'application paie la même somme autrement (base du week-end dans la
  prestation, aucun repos payé) ; l'écart n'apparaît que quand le jour de
  compensation tombe le mois suivant (mai trop haut, juin trop bas).

Les trois premières sont posées au client (« Ce qui attend le client »),
rien n'est codé avant sa réponse : elles touchent à des montants. **La
deuxième est tranchée le même jour** par la note explicative de la fiche de
paie, que le client a remise avec la note sur les repos de la grille :
« Réduction Temps Travail … non payé pour les ouvriers ». Appliquée, avec
deux autres lignes que la note corrige (libellé de la RHS/DTT, férié au
salaire moyen) — voir `docs/regles-paie.md`, « Les deux notes internes ».
L'écart de RTT d'avril et de mai disparaît exactement ; la quatrième ligne,
le repos lié au week-end, est désormais décrite jour par jour par la note. VBN
(employé) est **identique à l'octet** à la comparaison du 07/10 : rien n'a
régressé. Les scripts de comparaison vivent dans le scratchpad ; les
copies texte des fiches qui y traînaient (nom, registre national, IBAN)
ont été supprimées.

### Les relevés de pointage d'autres personnes, anonymisés

Le client, le 27/09/2026, en envoyant son relevé d'août scanné : « je vais
t'envoyer les fiches comme celle-ci d'autres opérateurs ; regarde comment
ma fiche est construite afin de l'anonymiser en gardant le trigramme, pour
faire à chaque fois la même chose ».

```bash
python3 tools/anonymiser-sommaire.py SCAN.pdf TRIGRAMME sommaire-TRI-AAAAMM.pdf
```

**Un scan n'a pas de texte** : le copieur écrit une image de fond et des
masques noir et blanc. On ne remplace donc pas un mot, on repeint des
zones. Quatre choses nomment la personne : le titre « Sommaire mensuelle -
<nom> », « Matricule: » (le numéro de contrat des fiches de paie),
« Section: », « Nom: ». Le titre et le nom reçoivent le trigramme, le
matricule et la section « (retiré) ». **Les métadonnées et le nom du
fichier portent l'identifiant de connexion de celui qui a scanné** :
elles sont vidées, et la sortie prend le nom qu'on lui donne.

**Les zones se trouvent par la structure** : la suite des lignes « * »,
un seul signe tout à gauche, sert de repère ; la ligne sous elle est
« Nom: », les trois au-dessus sont Matricule puis Section et « Sommaire de ».
Le haut du tableau avait été choisi d'abord, et il a échoué : son trait est
trop fin, le scan le rompt. Si la structure n'est pas retrouvée, l'outil
s'arrête sans rien écrire. Éprouvé : un scan dont on efface les « * »
échoue, un trigramme de deux lettres et un chiffre aussi.

**Fidélité** : hors des zones, l'image produite ne diffère de la source sur
aucun pixel, et l'outil le vérifie. La sortie est une image pure dans un
PDF neuf : rien du scan d'origine ne survit sous ce qui a été repeint.

**Sa garantie n'est pas complète** : sans lecture de caractères, il ne peut
pas chercher le nom ailleurs sur la page. On regarde l'aperçu PNG qu'il
écrit, **toujours**, avant de s'en servir. Le trigramme se donne à la main :
le matricule n'est pas dans les données de l'horaire.

**Un scan peut porter une série** — le client, le 27/09/2026 : treize
pages, douze personnes, août 2026. On donne un trigramme par page, dans
l'ordre, et l'outil écrit un fichier par personne :

```bash
python3 tools/anonymiser-sommaire.py SCAN.pdf YRS,PLZ,SKS,SKS,… DOSSIER --mois=202608
```

Tout ou rien : chaque page est repeinte et vérifiée avant qu'un seul
fichier s'écrive, et un nombre de trigrammes différent du nombre de pages
arrête tout. La première version ne traitait que la page 1 et recopiait
les autres **telles quelles**, noms compris : sur une série, douze pages
sur treize seraient sorties nominatives, avec pour seul garde-fou un
avertissement imprimé.

**Le trigramme se calcule, puis se vérifie.** L'initiale du prénom, la
première et la dernière lettre du nom : c'est la règle de l'anonymiseur,
et onze des douze tombent sur un trigramme connu. Mais `CORRECTIONS`
renomme quatre personnes (NPI, JBA, CHD, PDF), et le douzième relevé donnait
CDE, que CHD portait aussi à l'origine. **Le relevé a tranché seul** : ses
pauses du 3 au 16/08 concordent jour pour jour avec l'horaire de CDE, le
13/08 compris (6h-18h dans l'horaire, pointé de 5 h 39 à 18 h 16), et pas
avec celui de CHD. Une page de relevé peut déborder sur la suivante : deux
pages du même trigramme vont dans le même fichier (SKS, 2 pages).

**Ni le scan ni sa version anonymisée n'entrent dans le dépôt** : même sans
nom, un relevé de pointage porte les heures d'arrivée d'une personne
identifiée par son trigramme. Dépendances : `pip install pymupdf pillow`.

**Un scan poussiéreux trompait l'outil EN SILENCE**, et c'est la deuxième
série qui l'a montré (le 27/09/2026 : 23 pages, cinq employés, janvier à
août). Trois pages échouaient — les poussières grises des lignes « * »
comptaient pour des mots —, et c'était le moindre mal : sur la page 8, une
bande de poussière AU-DESSUS du titre passait pour le titre, qui gardait le
nom ; sur la page 12, des bandes de poussière décalaient le décompte, et la
zone « Matricule » visait une ligne de compteurs. **Le contrôle de fidélité
passait dans les deux cas** : il vérifie que rien n'a bougé hors des zones,
pas que les zones sont les bonnes.

D'où deux gardes. Un bloc de moins de 20 pixels d'encre est une poussière
(une étoile en pèse 35, un mot des centaines), et une bande qui n'a que des
poussières n'est pas une ligne. Et **chaque ligne se reconnaît à la largeur
de ses intitulés** — la police est à chasse fixe, « Matricule: » fait dix
signes, « Nom: » quatre, le titre commence par « Sommaire » et
« mensuelle » ; une position comptée ne suffit plus. Éprouvé : effacer
« Matricule: », sa valeur, « Section: », « Nom: » ou « mensuelle » fait
échouer la page ; les 14 pages de la série d'août passent toujours, et le
scan saboté d'août échoue toujours.

Le mois se donne désormais page par page, `TRI:AAAAMM`, un fichier par
personne et par mois.

**Une chasse aux noms par OCR** complète la garantie qui manquait : chaque
page produite est lue par Tesseract, et on y cherche, à cinq lettres près,
les mots des noms lus sur la source — gardés en mémoire, jamais écrits.
Elle mord : 23 pages sur 23 dans la source, **0 sur 23** dans la sortie. Le
script vit dans le scratchpad ; l'aperçu se regarde quand même.

### Les relevés d'août confrontés à l'horaire, jour par jour

Le client, le 27/09/2026 : « oui c'est le but ». Treize relevés, 403
journées d'août. **Pas de couche de texte** : Tesseract (`apt-get install
tesseract-ocr`) lit le tableau, **après avoir coupé l'en-tête** au bas de
la ligne « Nom: » que `zones()` de l'anonymiseur repère — aucun nom ne
passe dans le texte extrait. L'OCR confond lettres et chiffres (« P1i2 »,
« zo3 », « g84 ») et lit mal les chiffres des dates : les jours se
numérotent par leur RANG (chaque jour a sa ligne), jamais par la date lue.
**Et la ligne « faits à: 24.09.2026 » a une date** : comptée comme un
jour, elle décalait tout d'une ligne et fabriquait des écarts.

Les codes du relevé, lus sur les pages : `P10`/`P11`/`P12`/`P13` prime D,
AM, PM, N ; `P3x` le samedi, `P5x` le dimanche, `P8x` un férié ; `Y90`
week-end libre, `Z03` repos ; `F0` flex time épargné ; `U32`/`U33` heures
sup en PM, en N ; `J84` heures de déplacement d'un rappel ; `A57` le TP ;
9063 en « Sold.j. », le chèque-repas (MCH, *maaltijdcheque*). Absences :
4 et 13 maladie (13 à partir du 2ᵉ mois), 15 maladie sans certificat,
2 salaire journalier garanti, 23 congé parental, 47 VCP (le DTT du
classeur), 48 jour férié au choix (le RJF), 54 compensation payée (RHS),
58 RTT, 75 vacances.

**Les pauses et les primes concordent** sur toutes les journées lues,
une fois retirés les artefacts d'OCR — la prime la plus élevée des 19 et
20/08 (VBN) comprise. Les rappels, le flex time épargné et les heures sup
aussi : LDY le 12, GBT, PLZ et SKS le 27, SKS le 24. **Ce que le classeur
n'écrit pas**, et que le relevé paie :

- SMA le 17/08 : rappel et 4 h sup avant sa nuit (pointé dès 17 h 36) —
  la cellule dit `["N"]` ;
- CDE le 13/08 : rappel écrit « rappek ke 12/08 », faute de frappe ;
- CDE le 14/08 : 0,5 h sup en nuit (sortie à 23 h 06) ;
- SMA le 24/08 : venu 1 h (21 h 14 – 23 h), puis 7 h de salaire garanti ;
  le classeur écrit « Abs » et l'application une maladie entière ;
- SMA le 28/08 : « Abs » sur un repos, le relevé dit repos.

**Le chèque-repas : j'ai d'abord écrit qu'il ne concordait pas, et
c'était faux.** Le comparateur ne regardait que les journées de présence,
et ignorait la ligne « Chèque(s) repas issu(s) des heures récupérées »
(`crRecup`, un chèque par 8 h de RTT, de flex time ou de RHS). Mesuré au
navigateur, mois d'août, personne par personne : **dix sur douze au
chèque près**. Le relevé confirme la règle chez tout le monde — journées
entières de récupération 15 sur 15 avec chèque (9 « 8h -FT », 5 RTT,
1 DTT), congés et maladie 0 sur 62 (VA, RJF, CP, TP, maladie). Le client,
le 27/09/2026 : « A — oui, récup = chèque ». **Seul le DTT manquait**
(YRS le 06/08) : il entre dans `crRecup`, compté à part, sans report —
YRS 18 → 19, comme son relevé. Le 01/03 de LCI, 8 h de flex time sans
chèque sur sa fiche, reste une exception. Neuf règles, manques, compteurs
et Recyclage identiques à l'octet (la règle est de paie seulement).

**Piège de mesure** : le sélecteur de personne affiche « GBT » pour deux
colonnes (GBT-1 en Shift 4, GBT en Shift 5). Choisir par le libellé a
d'abord mesuré la mauvaise personne (15 au lieu de 21) : on choisit par
l'identifiant, la valeur de l'option.

**Les cinq journées, une par une** (le client, le 27/09/2026, « point par
point ») :

- **CDE le 13/08, « rappek ke 12/08 »** : c'est le classeur qui l'écrit,
  avec une faute de frappe — la seule du mot sur l'année. La lecture la
  tolère (`RX_RAPPEL` et les trois tests du mot : « rappe[lk] ») ; le
  rappel est lu, 4 h de déplacement comme les autres rappels du mois.
  Vérificateur identique à l'octet ;
- **SPS le 21/08, maladie sans certificat** (code 15 du relevé, non payée
  selon le client) : le classeur écrit « Abs » comme pour une maladie
  payée. **Écart connu.** Un code lu sur « Abs s/c » a été ajouté puis
  retiré le même jour : personne ne l'écrira ;
- **SMA le 24/08**, venu 1 h puis malade ; **SMA le 17/08**, rappel et 4 h
  sup ; **CDE le 14/08**, 0,5 h sup : le classeur et les commentaires des
  collègues n'en disent rien. **Écarts connus** ;
- **SMA le 28/08**, « Abs » sur un repos : l'application n'en paie aucune
  heure — 32 h de maladie en août (24 au 27), le relevé dit repos le 28.
  Rien à corriger. Les scripts (OCR, analyse,
extraction de l'application) vivent dans le scratchpad de la session.

### Une date de rappel n'est pas un renvoi de flex time

Trouvé le 27/09/2026 en reprenant, un par un, les écarts des fiches de
VBN : le 11/06, un repos, `["02h-06h","4h +FT","… rappel le 10.06"]`, comptait
4 h prestées, avec prime de nuit, chèque et indemnité. La fiche n'en porte
aucun. Ce n'était pas une question au client : la section 6 ter de
`docs/conversion-horaire.md` le disait déjà — un `+FT` part au compteur,
sans prime ni heure prestée.

**Deux défauts, et le second était large.**

- **L'épargne se retirait de la journée contractuelle, pas de la plage.**
  Une plage de 4 h épargnée en entier laissait 8 − 4 = 4 h prestées. La
  présence est désormais la durée de la plage, relue sur le poste du jour
  (y compris quand le cycle corrige le poste, `r.plageEp`), et l'épargne
  s'en retire : VBN le 11/06, BBZ le 14/02, `0 h`.
- **Toute date d'un commentaire `+FT` passait pour un renvoi.** Et **121
  des 183 étaient des dates de rappel**, le jour de l'appel. FLI le 23/01,
  « 8h +FT, rappel le 18/01 », retirait 8 h au 18/01 ; 36 journées se
  renvoyaient leurs propres heures (« rappel le 27.01 » écrit le 27/01) et
  les épargnaient deux fois : ATA le 27/01, `06h-18h · 4h +FT`, comptait
  4 h au lieu de 8. Sept autres n'étaient pas des renvois non plus
  (« CP déplacés aux 26 & 27/03 », « encodé le 13/08 », « TP déplacé au
  21/04 »). `RX_RENVOI` exige désormais « presté le », « du », « cf » ou la
  date en tête : **55 renvois**, exactement les 62 d'avant hors rappels,
  moins les sept faux.

Une demi-heure sup écrite (« +0,5 hs ») qui est le reste d'une plage
épargnée — AFA le 10/02, `11h-15h30' · 4h +FT` — ne reste pas en heure
prestée : elle se paie déjà comme heure sup.

Mesuré : **49 journées** changent, chacune pour l'une de ces raisons ;
journées prestées 14 473 → 14 465 ; neuf règles à zéro ; **compteurs
(76/77) et `--manques 0926` identiques à l'octet** — les compteurs du pied
de feuille ne dépendent pas des renvois ; sur l'année passée, 269 → 272
places creuses ; Recyclage : cinq cases d'une journée, 23 couples au quota
inchangés. VBN en juin : nuit 79 h au lieu de 83 (fiche 72 ; les 7 h
restantes sont le rappel du 25/06, déjà sur la liste).

### Les relevés de cinq employés, de janvier à août

Le client, le 27/09/2026 : 23 pages, 16 relevés (ATA, JBI, YPE, VGG, AFA),
**481 journées lues sur 488**. Deux passes d'OCR (300 ppp, et 400 ppp
nettoyé : seuil puis filtre médian) se complètent ; les jours se datent
par la date lue, et une ligne illisible prend la date manquante entre ses
voisines **seulement si l'écart tombe juste** — sinon le jour est déclaré
illisible, jamais décalé. Les absences se lisent par leur LIBELLÉ
(« MALADIE », « Vacances », « Congé Anc. »…), pas par leur numéro, que
l'OCR lit « S » ou « 5S ». Codes appris : `U` et `S` + jour (3 semaine,
4 samedi, 5 dimanche ou férié) + pause = heures sup ; `P8x` férié ;
« 56 Congé Anc., RTT » est le DTT du classeur, comme le 47 VCP.

**425 journées concordent sur 481.** Trois règles en sont sorties, toutes
tirées du classeur et de son cycle — les relevés n'ont fait que vérifier :

- **un rappel sur un repos DU CYCLE se paie en heures sup**, même quand la
  cellule franche écrit la pause — les adjoints l'y écrivent (VGG le
  10/05, JBI le 22/08, VBN le 25/06). 17 journées ; le cycle concorde
  avec le relevé ou la fiche les cinq fois où c'est vérifiable. **VBN en
  juin : nuit 72 h, comme la fiche** (79 avant) ;
- **« SD26 · n h +FT »** : repos au cycle, les n heures sont toute la
  présence et partent au compteur (AFA le 07/01, 0 h prestée) ; poste au
  cycle, elles s'ajoutent à la journée (VGG le 09/04, 8 h + 3). 15
  journées, 5 vérifiées ;
- **une plage en annotation qui couvre ENTIÈREMENT une pause plus haute
  que celle de la cellule** en fait la pause prestée : AFA le 10/08,
  `["PM","18h-6h"]`, relevé 8 h de nuit et 4 h sup de nuit. 25 journées ;
  la prime ne baisse jamais (ATA le 21/03, « Conserve sa prime », reste
  PM). Le manque du 30/09 en N au gluten disparaît : IME,
  `["AM","21-06h"]`, y est.

Neuf règles à zéro, compteurs 76/77 identiques ; 5 journées « SD26 » sur
repos passent en non prestées ; Recyclage : trois cases d'une ou deux
journées, 23 couples au quota inchangés.

**Le cycle n'est pas une source sûre SEUL**, et c'est mesuré : « une
pause écrite sur un repos du cycle, sans rappel » donne 170 journées,
dont VGG le 08/05 — repos au cycle, matin au relevé. Rien n'est tiré de
cette forme ; le mot « rappel » est ce qui la rend fiable.

**Le client l'a tranché le 27/09/2026 : B, rien sans le mot « rappel ».**
Et il a donné la raison de l'erreur du cycle : « les jours de D peuvent
être déplacés et ne sont pas toujours prestés les jours où ils l'étaient ;
VGG ne vient pas faire ses horaires flottants les 04 et 05 mai, donc il
décale un de ses D le vendredi et vient remplacer en matin car cela
l'arrange mieux ». Un D déplacé fait d'un repos au cycle un jour
travaillé normal. JBI les 08/08 et 14 au 16/08 restent un écart connu.

Écarts connus, que le classeur n'écrit pas : RHS d'un départ anticipé
(VGG 15/05 et 03/04 ; le 23/07, « départ à 20h », est lu depuis le
29/09/2026), flex time épargné non écrit
(AFA 30/07, JBI 18/08, VGG 01/07), maladie sans certificat écrite en
poste (VGG 07/08), une pause prévue différente (AFA 12 au 15/01 en SD26,
ATA 05, 06 et 17/08 écrits D ou 7h-15h et pointés 6 h-14 h, VGG 30/04),
RJF renvoyé par « cf 21/08 » (JBI 13/08), « Abs » sur un repos (YPE 17
et 18/08), un jour férié écrit « 8h -FT » (YPE 14/05, Ascension).

## La barre du haut est une barre d'identité

Le client, le 22/09/2026 : « la barre du haut doit être une vraie barre
personnelle, avec le logo, le trigramme et le poste actuel ; il faut que ce
soit 100 % professionnel ».

Trois choses, dans l'ordre où on les cherche : **à qui appartient cet écran**
(le logo, déjà mis en cache par le service worker), **qui le regarde** (le
trigramme, sur une plaque), et **ce qu'il fait aujourd'hui**. La fonction
seule — « Contremaître » — ne disait rien du jour ; `posteDuJourDe()` rejoue
`equipeDuJour()` et `postesDePause()` pour la date du jour et rend
« Contremaître · nuit », « STEP · matin », « Jour », « Congé » ou « Repos ».
Il ne recompte rien : c'est la vue de l'équipe qui répond.

**Deux BLOCS, et non deux lignes.** Le client, le 22/09/2026 : « la date au
dessus à droite et le poste en dessous avec la pause ; le trigramme doit
être près de BIOWANZE ».

À gauche, ce qui ne change **jamais** : le logo, le nom, le trigramme — d'un
seul tenant, parce que c'est une seule chose, à qui appartient cet écran. À
droite, ce qui change **chaque jour** : la date, et sous elle le poste avec
sa pause, les deux lignes alignées sur le même bord. On lit la colonne de
droite pour savoir sa journée, jamais celle de gauche.

```
[logo] BIOWANZE [VBN]                    Mardi 22 septembre
                                        Contremaître · Nuit
```

Deux dispositions l'ont précédée dans la même journée, et chacune corrigeait
la précédente : le nom seul sur une ligne presque vide, puis le nom à gauche
et le trigramme à l'autre bout avec date et poste dessous. La première
gaspillait quatre cinquièmes de sa première ligne ; la seconde séparait le
trigramme du nom, alors qu'ils disent la même chose.

**Le jour et la pause portent une majuscule** — « Mardi 22 septembre »,
« Contremaître · **N**uit ». Le client : « le jour doit avoir une majuscule
et la pause aussi ». Ce sont les deux mots qu'on cherche du regard ; le
mois, lui, accompagne le quantième et reste en bas de casse. Concrètement :
`dateDuJourLisible()` ne rabaisse plus `JOURS_LONGS`, et `posteDuJourDe()`
ne rabaisse plus `g.t`.

Mesuré à 320, 360, 390, 430, 768 et 1280 px : **58 px de barre**, et **rien
de tronqué, 320 px compris** — où les deux blocs se frôlent à 12 px. Au-delà
de 760 px la marque se réduit à sa largeur de contenu et les deux blocs se
retrouvaient à 10 px l'un de l'autre alors que la barre a mille pixels de
vide plus loin : `@media (min-width:761px)` leur rend 20 px. Sur téléphone
il n'y en a pas à donner.

Vérifié sur six états — Matin, Après-midi, Nuit, Congé, Repos, Absent — et
hors ligne : logo, trigramme, date et poste du jour se rendent tous.

**Elle s'efface quand on descend.** Le client, le 22/09/2026, cherchant
comment l'optimiser encore. Elle se replie dès qu'on descend PASSÉ sa propre
hauteur, et revient entière au premier geste vers le haut : **53 px rendus
au contenu** sur l'Équipe, la Polyvalence et l'Horaire — une ligne de tableau
entière — sans rien perdre, puisqu'elle est là dès qu'on la cherche.

Trois précautions, et chacune répare un défaut qu'on aurait eu :

- **un seuil de six pixels** — sans lui, le tremblement d'un doigt posé sur
  l'écran la fait battre ;
- **tant qu'on est dans ses propres pixels** (`y <= sa hauteur`) elle reste —
  se replier là n'aurait rien découvert et l'aurait fait sauter ;
- **un défilement négatif la redéplie toujours**, même sous le seuil : c'est
  le geste par lequel on la cherche.

**SEULEMENT SOUS 760 px**, et c'est essentiel : au-delà, la barre d'ONGLETS
remonte dans cet en-tête. La replier ferait disparaître la navigation, pour
gagner de la hauteur là où il n'en manque pas. Le garde-fou est dans la
FEUILLE (`@media (max-width:760px){ .top.repliee{…} }`) et non dans le
script : une fenêtre redimensionnée à travers le seuil se comporte
correctement sans écouteur de plus.

Sur téléphone, la barre d'onglets ne bouge pas : elle vit dans son propre
cadre ancré par ses quatre côtés, sans rapport avec cet en-tête.

Le repli tombe de lui-même sous `prefers-reduced-motion`, qui coupe toutes
les transitions de la feuille — il devient instantané plutôt que d'être
imposé en mouvement.

Mesuré à 320, 390, 430 et 1280 px, sur cinq positions de défilement et un
changement d'onglet : replié à 600 px de descente, redéplié à 120 px de
remontée, toujours visible en haut de page, et **immobile à 1280 px**.

**Le logo fait 32 px, et non 38.** C'est LUI qui fixait la hauteur de la
barre, pas le texte : 38 px contre 31 pour le bloc de droite. Mesuré à
l'essai — 34 donnent 54 px de barre, 32 en donnent 52, et en dessous il n'y
a plus rien à gagner, le texte reprenant la main à 51. **La barre passe de
58 à 52 px** (53 avec son filet), sur tous les onglets, en permanence.

**Le sélecteur de mois n'y est plus.** Le client, le 22/09/2026 : « la
sélection du mois de l'année ne doit pas être dans la barre du haut mais
seulement là où elle est nécessaire dans les onglets ». Il était masqué
onglet par onglet — quatre règles CSS pour le cacher là où il n'a rien à
dire — et occupait quand même la place la plus chère de l'écran sur les
autres.

Il se **range** désormais dans l'onglet qui l'emploie : Résumé, Horaire,
Fiche et Contrôle ont un `.mnavhote`, les autres n'en ont pas et il
disparaît. **Un seul exemplaire déménage**, comme la barre d'onglets : quatre
copies auraient demandé quatre jeux d'écouteurs, et rien n'aurait garanti
qu'elles affichent le même mois.

Deux mécanismes sont morts avec ce déménagement et ont été retirés plutôt
que laissés en place : le mois abrégé (`sept. 2026`, un compromis pour cinq
pixels manquants dans l'en-tête) et le masquage de « BIOWANZE » sous 340 px.
**Un mécanisme qui ne sert plus égare celui qui le relit.**

**`flex:1 1 0`, et non `auto`** — cela reste vrai pour la marque. Un élément
flexible se replie selon sa taille de BASE, pas selon sa taille minimale :
avec `auto`, elle réclamait ses 190 px avant d'accepter de rétrécir.

Vérifié hors ligne : logo, trigramme, date et poste du jour se rendent tous.

### Le net à recevoir n'y est plus

Le client, le 23/09/2026 : « le cadre avec le net à recevoir apparaît encore
dans la barre de navigation du haut, cela ne doit pas arriver ».

Cette barre dit trois choses — à qui appartient cet écran, qui le regarde, ce
qu'il fait aujourd'hui. **Un montant n'en est pas une**, et surtout pas
celui-là : c'est le chiffre le plus personnel de l'application, qui restait
affiché en permanence, sur tous les onglets, par-dessus l'épaule de
n'importe qui. Il se lit dans « Mon salaire », qui est fait pour lui — deux
fois même, en tête du panneau et au pied de la fiche simulée.

Il avait déjà à moitié perdu sa place : **cinq règles le masquaient onglet
par onglet** et une sixième le repliait sous 760 px, si bien qu'il ne se
voyait plus que sur deux vues. Un élément qu'on passe son temps à cacher n'a
pas sa place où on l'a mis. Sont partis avec lui ses trois règles de mise en
forme, celle qui l'habillait de blanc sur le bleu, et l'écriture de `#netTop`
dans `renderSlip()` — **laisser cette ligne aurait suffi à casser tout le
calcul**, `getElementById` rendant `null`.

## Un horaire qu'on ne peut plus lire vide tout, en silence

Le client, le 23/09/2026 : « Mon salaire n'est plus correctement calculé et
tout est vide dans l'onglet » — 0 journée sur 30, zéro heure, zéro prime,
zéro chèque-repas, et un net réduit à la seule rémunération fixe.

**Le calcul n'avait rien.** C'est `data/horaire-2026.json` que son appareil
n'arrivait plus à lire, et tout en dépend : sans lui le sélecteur de personne
reste vide, donc `prefillAuto()` sort sans rien faire, donc le mois reste
blanc — et la cascade continue de se dérouler sur la rémunération fixe, avec
des zéros parfaitement crédibles.

**Le service worker mettait en cache n'importe quelle réponse.** Une page
d'erreur, un 404, un portail Wi-Fi qui répond une page de connexion : `c.put`
la déposait à la place du fichier, et le cache d'abord la resservait ensuite
à chaque ouverture. **Le défaut se réparait tout seul une fois posé** — ni le
retour du réseau, ni un rechargement, ni une nouvelle version de la page n'y
changeaient quoi que ce soit ; seul un changement de `V`, qui efface les
anciens caches, le levait par accident.

Reproduit avec Playwright en empoisonnant l'entrée à la main : sur un profil
neuf, l'écran du client, au pixel près.

Deux remèdes, et il en faut deux :

- **`cacheSiBon()` dans `sw.js`** : une réponse qui se LIT et qui n'est pas
  bonne ne remplace plus jamais ce qui est en cache, et un rafraîchissement
  d'horaire qui échoue RETIRE l'entrée au lieu d'en garder une dont on ne
  sait plus rien. Les réponses **opaques** passent toujours — les polices sont
  demandées sans CORS, on ne peut ni lire leur code ni les juger, et les
  refuser priverait la page de ses polices hors ligne ;
- **`fetchHoraireDB()` se soigne lui-même** : un appareil déjà empoisonné ne
  guérit pas d'une garde écrite après coup. Un horaire illisible — la
  coupure réseau, le code HTTP, le JSON invalide, ou un fichier sans personne
  dedans — fait vider
  l'entrée de tous les caches et refaire le trajet UNE fois, avec un
  paramètre d'URL et `cache:"no-store"` pour interdire qu'on ressorte la
  même réponse. Le premier essai, lui, se sert normalement : le cache
  d'abord, c'est tout l'intérêt de ne pas attendre 690 Ko.

**Et si les deux échouent, cela se DIT.** Un bandeau qui reste en haut de la
page, pas une bulle de deux secondes : sans horaire, la moitié de
l'application affiche des zéros qu'on peut croire. `flash()` ne convenait
pas — le message passait avant même qu'on ait regardé l'écran.

Vérifié aux quatre états : marche normale, cache empoisonné qui guérit, hors
ligne avec un bon cache, horaire injoignable où le bandeau parle. Contraste
du bandeau 5,4:1 en clair et 6,3:1 en sombre, et l'audit complet des six
onglets reste à **0 texte sous le seuil** dans les deux thèmes.

**Le piège de l'épreuve** : `page.route()` n'intercepte pas les requêtes
émises par le SERVICE WORKER. Un premier essai croyait couper l'horaire et
le laissait passer, bandeau éteint et 11 personnes dans le sélecteur. Il faut
`serviceWorkers:"block"` sur le contexte pour éprouver ce cas-là.

## Le thème entier est de la famille de la marque

Le client, le 23/09/2026 : « modifie tout le thème du site pour qu'il soit en
accord avec les deux nouvelles barres de navigation ; je veux des couleurs
qui fassent professionnel et que ce soit un résultat incroyable ».

**Le défaut tenait en un chiffre.** Les gris de l'application étaient un
gris-pétrole — teinte 238 à 244 en OKLCH — alors que la tuile du logo est un
bleu-nuit à **262**. Les barres flottaient donc sur une page d'une autre
famille, et c'est cela qu'on voyait.

Toute la rampe neutre est **rebâtie à la teinte de la marque**, chroma
décroissant à mesure que la clarté monte : une page claire franchement
teintée de violet se remarquerait. Les pas sont **calculés en OKLCH**, pas
choisis à l'œil — `scratchpad/oklch.js` et `rampe.js` font la conversion
sRGB ↔ OKLab dans les deux sens.

**L'ordre des plans ne change pas** : la page reste le plus sombre, la carte
vient au-dessus, et la barre du haut se place juste au-dessus d'elle. Seule
la FAMILLE change.

**L'accent est le cyan du logo**, pris plus profond pour tenir sur du blanc :
même teinte (222), pas la même clarté. Il ne vient plus d'ailleurs.

**Les teintes de l'usine ne bougent pas** — elles disent les pauses et les
ateliers, pas la marque — mais tous leurs pas sont recalculés sur une même
clarté et un même chroma. Le contraste de chacun sur son fond doux tient
entre 4,6 et 5,6:1, là où l'ancienne série allait de 3,9 à 7,2.

### Un seul thème, le sombre

Le client, le 30/09/2026 : « l'app ne doit avoir que le thème sombre ».
`<html data-theme="dark">` le pose quel que soit le réglage du téléphone,
`color-scheme:dark` partout, et le manifeste prend `#111727` pour fond et
couleur de thème. Le bloc `@media (prefers-color-scheme: dark)` était la
copie exacte de `:root[data-theme="dark"]` (55 jetons sur 55) : il est
retiré. Le `:root` clair reste comme base que le bloc sombre surcharge.
**Ce qui est écrit dans ce fichier sur le thème clair ne vaut plus** que
comme histoire. Vérifié avec un téléphone réglé en clair, à 320 (hors
ligne), 390 et 1280 px : tout est sombre, filigrane compris.

### Zéro texte sous le seuil, et il y en avait 456

Un audit qui parcourt les six onglets, calcule le fond RÉEL de chaque texte
(en remontant les parents jusqu'à une couleur opaque) et le compare au seuil
WCAG de sa taille : **456 textes en dessous en thème sombre, 460 en clair**,
avant. Personne ne l'avait mesuré.

La cause était une seule : `--faint` portait des centaines de libellés —
unités, sous-titres, mentions — à **3,0:1**. Elle passe à 5,5:1 sur la carte
et 4,7 sur la page ; `--muted` descend d'autant pour que la hiérarchie reste
lisible. Le dernier récalcitrant, « virement de fin de mois » sur le fond
d'accent, a été réglé en assombrissant `--in-soft`.

**Résultat : 0 sur 0**, dans les deux thèmes, à 390 et 1280 px, sur les six
onglets.

**`--sur-in` est né de cet audit** : l'encre qui se pose SUR l'accent ne peut
pas être « blanc » dans les deux thèmes, puisqu'en sombre l'accent est le
cyan clair du logo — du blanc dessus se lit à 1,9:1. Le bouton principal
l'écrivait en dur.

**Les deux palettes du calendrier sont inchangées et revalidées** contre les
nouvelles surfaces par `scripts/validate_palette.js` du savoir-faire
« dataviz », en mode « toutes paires » : tout passe, pire paire 23,2 en
vision normale en clair, 16,6 en sombre.

## Les deux barres portent la couleur du logo

Le client, le 22/09/2026 : « barre de navigation de la même couleur que le
background du logo », puis le 23/09 : « j'aimerais aussi que le background
des barres du haut ET DU BAS soit de la même couleur que le background du
logo Biowanze ». C'est **`#111727`** depuis le 23/09/2026 — le fond du NOUVEAU logo, et non
plus la tuile de `logo.png`.

**Le client l'a dit à l'envers de ce que j'avais compris, et il a fallu le
mesurer pour s'en rendre compte.** « J'aimerais que la couleur du background
de ce screen soit le background des barres de navigation » : sa page donne la
couleur, la barre la reçoit — et non l'inverse. J'avais lu la phrase dans
l'autre sens et je lui ai expliqué que ses couleurs étaient fausses. Elles ne
l'étaient pas.

**Les deux fonds sont relevés au PIXEL sur ses captures**, par histogramme :
sa barre de navigation est `#111727` à 38 % des pixels du bandeau, et le fond
de son contenu `#F6F6F6` à 52 % des marges. On ne devine pas une couleur de
marque, on la mesure — c'est déjà comme cela que `#1A2539` avait été relevé
dans `logo.png`.

**Tout le reste suit** : la rampe neutre se réancre sur la teinte du nouveau
bleu (268 au lieu de 262), le thème clair prend `#F6F6F6` pour page, et le
sombre se restéage pour que la barre reste lisible entre la page et les
cartes. Zéro texte sous le seuil WCAG, dans les deux thèmes, après comme
avant.

**Les règles de l'en-tête portent toutes `.top` devant** : elles battent par
la SPÉCIFICITÉ celles qui le peignaient, et non par leur position. C'est ce
qui les rend sûres — le piège de la requête média, qui n'ajoute aucune
spécificité, s'est déjà refermé trois fois sur ce fichier.

Au-delà de 760 px la barre d'onglets remonte DANS cet en-tête : elle y prend
les mêmes encres que dans son cadre du bas, sans quoi elle disparaîtrait sur
le bleu. Sous 760 px elle n'est pas là, et ces règles ne l'atteignent pas.

**`<meta name="theme-color">` suit**, et n'a plus qu'une valeur : la barre
d'état du téléphone prend la couleur de la barre du haut, sans quoi un
liseré d'une autre teinte la surmonte. Les deux déclarations par thème n'ont
plus lieu d'être — une couleur de marque n'appartient ni au clair ni au
sombre.

**Le logo passe à 36 px** — « le logo peut être légèrement plus grand ». Il
redevient ce qui fixe la hauteur de la barre : **57 px au lieu de 52**.

**Et c'est le logo VECTORIEL, en négatif**, que le client a poussé lui-même
le 23/09/2026 pour qu'il s'affiche dans la barre. Texte blanc, marque en
dégradé, fond transparent : il se pose sur le bleu nuit sans tuile ni coin
arrondi, comme il est dessiné pour l'être — là où `icon-192.png` apportait
son propre fond.

**36 px de HAUT et la largeur suit** : le dessin fait 1810 × 1388, il se
déformerait dans un carré. Il rend 47 × 36, et rien n'est tronqué même à
320 px, où la marque et le bloc du jour se frôlent à 10 px.

**`logo.svg` entre dans `CORE` du service worker.** Sans cela la barre
serait nue hors ligne — vérifié avec `setOffline(true)` : il se rend depuis
le cache. « BIOWANZE » reste écrit à côté : le mot du lockup fait cinq
pixels de haut à cette taille, il décore, il ne se lit pas.

Les icônes de la PWA restent en PNG — le manifeste n'accepte pas autre
chose pour l'installation.

Elle se pose dans les **deux thèmes**, et c'est le point : une couleur de
marque n'appartient ni au clair ni au sombre. D'où deux jetons déclarés une
seule fois, hors des deux blocs de thème — `--marque` et `--marque-vif` — et
des couleurs d'écriture à elle, en blanc transparent. Sans cela, en thème
clair, `--ink` est presque noir et `--in` un bleu foncé : les deux
disparaîtraient sur ce fond.

Mesuré dans les deux thèmes : fond `rgb(26, 37, 57)` — exactement celui de
la tuile — **contraste 7,46:1** pour un onglet au repos et **6,46:1** pour
l'onglet actif, contre un seuil de 4,5.

Les trois règles qui peignent les boutons ont la MÊME spécificité que celles
du haut de la feuille, qui peignent la barre du bureau ; **elles gagnent
parce qu'elles sont écrites après**. Ne pas les déplacer plus haut — c'est
le même piège que la zébrure de la polyvalence et que la barre d'onglets
sous 375 px.

## La barre d'onglets n'est pas ancrée par une unité de hauteur

Elle vit dans un cadre à elle, `.navwrap`, hors de l'en-tête collant — c'est
la bonne moitié d'un remède de septembre 2026, et il faut la garder.

L'autre moitié était fausse : le cadre tirait sa hauteur de `100dvh`. Sous
iOS cette unité se trompe quand la barre d'URL est **réduite** — Safari
continue d'annoncer la hauteur de la barre pleine, le cadre devient plus
court que l'écran, et la barre d'onglets remonte d'autant. Le client l'a
photographié le 22/09/2026 : deux lignes du tableau visibles SOUS la barre.

Le cadre est donc ancré par ses **quatre côtés**, sans aucune unité à
interpréter. Le premier remède avait eu tort de bannir `bottom` : ce n'est
pas lui qui se résolvait mal, c'est l'en-tête collant qui l'enfermait.

Mesuré à 320, 360, 430 et 760 px, sur quatre onglets et quatre positions de
défilement : **écart de 0 px au bas de l'écran**, y compris sur un onglet
plus court que l'écran — le cas que l'ancien commentaire décrivait comme
cassé. Au-delà de 760 px la barre remonte dans l'en-tête, inchangée.

**Chromium ne reproduit pas le défaut d'iOS** : la mesure prouve que la
dépendance à `dvh` a disparu, pas que le téléphone est guéri. Seul l'appareil
du client peut le dire.

## Sur téléphone, une vitrine

Le client, le 29/09/2026 : « je veux que même sur mobile cela soit une
expérience unique, une vitrine de mon savoir-faire ». Avant d'ajouter quoi
que ce soit, les six onglets ont été photographiés à 390 px dans les deux
thèmes. **Quatre défauts sont apparus, et ils passaient avant la finition** :

- **les textes d'introduction portaient la classe `top`**, celle de la
  barre du haut. Ils étaient donc COLLANTS (`position:sticky`, z-index 40)
  et peints en bleu nuit : en thème clair, « Choisissez votre fonction… »
  s'écrivait en gris sur du bleu nuit, presque illisible. Personne ne
  l'avait vu parce qu'en sombre la page est déjà bleu nuit. La classe
  s'appelle désormais `haut`. **Un nom de classe générique en rejoint un
  autre sans le dire** ;
- **les onglets passaient à la ligne à 390 px** : `nowrap` ne valait que
  sous 375 px, et l'onglet choisi, en gras, poussait « Mon horaire » sur
  deux lignes. La barre fait maintenant la même hauteur (62 px) quel que
  soit l'onglet ;
- **les tuiles de « Mon horaire »** prenaient la largeur de leur libellé :
  deux rangées qui ne tombaient jamais d'aplomb, la première collée au
  filet de l'en-tête. C'est désormais une grille de colonnes égales ;
- **les intitulés des Réglages** passaient à la ligne (« Primes de /
  rappel ») pour faire place à leur sous-titre. Celui-ci passe dessous.

Ce qui est ajouté, et qui s'éteint sous `prefers-reduced-motion` :

- **l'entrée d'un onglet** : la vue monte de 6 px en s'éclairant, en
  0,22 s ;
- **le geste qui répond** : onglets et boutons s'enfoncent sous le doigt,
  et l'icône de l'onglet choisi se soulève d'un cran ;
- **feuilleter les journées du doigt** : un glissement horizontal sur le
  tableau des équipes du jour change de jour, comme les flèches, et le
  tableau arrive du côté où l'on va. Il faut un geste franc (60 px, 1,8
  fois plus large que haut, moins de 0,7 s) pour ne jamais voler un
  défilement vertical. Si le tableau défile lui-même de côté, le geste lui
  revient. Éprouvé : un glissement court ou en biais ne change rien.

Rien ne bouge dans la lecture : les quatre sorties du vérificateur sont
identiques à l'octet, et `comparer-fiches` passe son épreuve. Vérifié à
320 (hors ligne), 390 et 1280 px, en clair et en sombre.

**Et feuilleter les MOIS du doigt.** Le client, le 09/10/2026 : « le swipe
gauche droite pour la sélection de mois doit être actif sur les autres
onglets aussi ». Partout où le sélecteur de mois est rangé — Calendrier et
Salaire —, le même geste franc change de mois (gauche : le suivant, droite :
le précédent, comme ‹ ›), avec la même animation que le jour. Jamais sur un
champ de saisie ni dans un bloc qui défile de côté — **sauf le champ
invisible posé sur l'étiquette du mois** (`#moisPick`) : la première
version l'excluait comme tout champ, et le geste ne prenait pas sur la barre
du mois, l'endroit le plus naturel pour feuilleter. Un appui l'ouvre
toujours ; seul un glissement de 60 px change de mois. Éprouvé à 320 (hors
ligne), 390 et 1280 px, sur la barre du mois et au milieu du contenu :
glissement franc dans les deux sens, court et en biais sans effet.

**Les cadres restent en place.** Le client, le 09/10/2026 : « pourquoi lors
du swipe les cadres ont l'air de se déplacer au lieu de rester à leur
place ? ». L'animation s'appliquait à tout le panneau, cartes comprises.
Elle ne s'applique plus qu'au contenu des cartes, hors barre du mois, et la
carte rogne ce contenu le temps du glissement (`overflow:clip`, retiré après
260 ms). Mesuré au toucher simulé, à 320 px (hors ligne) et à 390 px :
pendant l'animation, la carte ne bouge pas d'un pixel, la barre du mois
reste fixe et le contenu glisse de 13 à 16 px.

**Et les flèches répondent aux appuis rapides.** Le client, le 09/10/2026 :
« les flèches gauche/droite des mois sur mobile ne réagissent pas si l'on
veut passer les mois rapidement ». La garde anti-zoom au double-tap annulait
toute 2e tape à moins de 320 ms au même endroit — c'est exactement appuyer
vite sur la même flèche — et chaque tape annulée relançait le délai :
mesuré au toucher simulé, **quatre appuis rapides sur › avançaient d'un
mois**, et les flèches du jour de l'onglet Horaire d'un jour. La garde ne
s'applique plus aux boutons, liens, champs et onglets, qui ne zooment pas
(`touch-action:manipulation`) ; elle reste ailleurs. Quatre appuis = quatre
mois et quatre jours, dans les deux sens, à 320 (hors ligne) et 390 px.

### Le menu du bas, à la BETSFIX

Le client, le 09/10/2026 : « un menu identique à celui du GitHub BETSFIX
dans le bas de page et PWA ». Recopié de la feuille de `CronoBots/BETSFIX`
(`app/web.py`, `.botnav` sous 1000 px), sous 760 px : une capsule
flottante en pilule, à 16 px du bas et des côtés (safe area en plus), fond
`rgba(24,27,36,.9)` sans flou, filet clair, ombre portée ; icônes seules
de 25 px au trait 1,9, grises au repos ; l'onglet ouvert en pilule teintée
de l'accent avec un filet, icône grossie d'un dixième. Seul l'accent
diffère : le cyan de la marque au lieu du bleu de BETSFIX. **Pas de
`backdrop-filter`, `transform` ni `will-change` sur la barre fixe** : sous
iOS ils cassent le `position:fixed` (leçon de BETSFIX). L'onglet Horaire
perd sa plaque cyan du 06/10 : tous les onglets se traitent pareil. Les
libellés restent lus par les lecteurs d'écran. Le bas de page, la bulle et
le bouton de retour en haut se décalent au-dessus de la capsule. Le bureau
ne change pas. Mesuré à 320 (hors ligne) et 390 px : 16 px des trois bords,
51 px de haut, sept onglets égaux, rien ne déborde.

**L'onglet Horaire passait sous la capsule**, et c'est le client qui l'a
vu sur son iPhone. Son tableau remplit l'écran au-dessus de la barre, et
`ajusterHauteurJour()` lui réservait la HAUTEUR de la barre (`--jnav`) :
juste tant qu'elle touchait le bas, faux depuis qu'elle flotte à 16 px
plus la zone d'accueil. On mesure désormais du haut de la barre au bas de
l'écran. Mesuré : 16 px entre le cadre et la capsule, à 320 (hors ligne)
et 390 px.

**En PWA, la capsule descend dans la zone d'accueil, comme celle de
Strava.** Le client, le 09/10/2026, deux captures côte à côte : « bonne
sur navigateur », mais plus haute que Strava une fois installée. Elle se
posait à 16 px AU-DESSUS de la zone d'accueil de l'iPhone (34 px), donc à
50 px du bas ; Strava se pose à cheval sur cette zone. `--navbas` vaut
`max(16px, zone d'accueil − 16px)` : 16 px dans le navigateur, où la zone
vaut 0, inchangé ; 18 px sur l'écran d'accueil. Le bas de page, la bulle
et le bouton de retour en haut suivent la même variable. Chromium n'a pas
de zone d'accueil : mesuré 16 px à 320 (hors ligne) et 390 px, et la
formule rend 18 px avec 34 px ; seul l'iPhone du client dit le reste.
Puis, le même jour : « c'est mieux mais un rien plus haute » — zone
d'accueil − 12 px, soit **22 px** du bas sur l'iPhone ; le navigateur ne
bouge pas.

**Plus haute** (le client, le 09/10/2026 : « tu peux augmenter la hauteur
de la barre de menus ») : 61 px au lieu de 51 (boutons de 11 px de marge
verticale, capsule de 6 px), l'onglet ouvert en pilule de 20 px de rayon ;
le bas de page, la bulle et le bouton de retour en haut remontent de
10 px. Mesuré à 320 (hors ligne) et 390 px : 16 px des trois bords, et le
cadre du Planning toujours à 16 px de la capsule.

### « Votre horaire a changé » : dans l'application, et sur le téléphone

Le client, le 09/10/2026 : « des notifications pour l'opérateur connecté,
en cas de changement d'horaire, de poste ; il faut que cela soit
professionnel », puis « go pour 1 et 2 » (dans l'application, et une
notification du téléphone à l'ouverture). Le niveau 3 — une notification
application fermée — demanderait un serveur d'envoi et une liste
d'appareils abonnés hors du téléphone : écarté pour l'instant, c'est sa
décision. Le client a demandé pourquoi BETSFIX notifie écran verrouillé :
son serveur Python garde les abonnements (`pushManager.subscribe`, clé
VAPID) et envoie par `pywebpush` au service d'Apple, qui réveille le
service worker. Ici, il faudrait un service d'abonnements (une
fonction Supabase suffirait), une action GitHub qui compare l'horaire à
chaque classeur et envoie, et deux secrets. Réponse le 09/10/2026 : « ne
rien faire pour ça maintenant ».

**Il n'y a pas de serveur** : l'horaire change quand un classeur est
installé, et l'application le découvre en s'ouvrant (le nouveau `V` vide
les caches, l'horaire neuf arrive).

- **L'instantané** (`notif/vu/<id>/<année>`) : pour chaque journée
  d'aujourd'hui à la fin de l'horaire, ce que la cellule dit —
  `descJourNotif()` : la pause, l'atelier ÉCRIT dans la cellule
  (`posteEcrit`), le code de journée, le congé, « rappel ». Une absence
  d'une journée entière se dit seule (« Maladie », pas « AM · MAL »). Le
  poste vient de la cellule de la personne, jamais du rééquilibrage : on
  annonce SON horaire, pas un placement déduit des absences des autres.
- **La comparaison** (`detecterChangements()`) : une journée dont la
  lecture a changé entre dans l'attente (`notif/attente/…`) avec son AVANT ;
  elle y reste jusqu'au bouton « Vu » ou jusqu'à ce que la date passe. La
  première fois, on photographie sans rien signaler ; le passé ne compte
  pas ; un commentaire qui change sans changer la lecture non plus.
- **La carte** sous le héros : liseré cyan (un changement n'est pas une
  faute), « Votre horaire a changé · n journées modifiées · classeur du… »,
  puis une ligne par série — **les journées qui se suivent et changent
  pareil n'en font qu'une** (`groupesNotif()`) : « Du lundi 12 octobre au
  dimanche 22 novembre · 42 j → Maladie ». L'avant barré ne s'écrit que
  s'il est le même pour toute la série. Cinq lignes, le reste se déplie.
  Une ligne ouvre son mois. Un point cyan sur l'onglet Accueil (`#notifDot`).
- **Le téléphone** : Réglages → Mon compte → « Notifications du
  téléphone », Activer / Désactiver (`ui/notifTel`). La permission n'est
  demandée qu'à ce clic. `showNotification()` par le service worker — la
  seule voie d'iOS, et seulement pour l'app installée sur l'écran
  d'accueil (le réglage le dit sur un iPhone qui ne l'est pas). Une
  notification par ouverture, seulement pour les journées NOUVELLEMENT
  changées, même étiquette pour remplacer la précédente ; la toucher ramène
  l'app (`notificationclick` dans `sw.js`).

**Éprouvé sur un vrai changement** : instantané pris sur le classeur du
01/10, puis celui du 09/10 servi à sa place. YBT : 65 journées, d'abord
65 lignes « AM → AM · MAL » — d'où le regroupement et le libellé seul de
l'absence ; ensuite « Du lundi 12 octobre au dimanche 22 novembre · 42 j →
Maladie » et quatre lignes. VBN : deux journées. Chromium sans écran répond
toujours « refusé » aux notifications : l'épreuve simule l'autorisation et
enregistre ce que `showNotification()` reçoit — une à l'activation, une au
changement, aucune au rechargement suivant. Vérificateur identique à
l'octet ; rien ne déborde à 320 (hors ligne), 390 et 1280 px. **Seul
l'iPhone du client dira si la notification s'affiche** une fois l'app
installée.

### Le bouton de retour en haut

Le client, le 30/09/2026 : « un bouton pour remonter dans le haut de page,
en bas à droite, avec une opacité quand il n'est pas pointé ». `#enHaut`,
rond de 44 px sur `--marque`, flèche blanche : il n'apparaît qu'après
300 px de descente (en haut de page il n'a rien à faire), à 55 % d'opacité,
et passe à 100 % au survol, au clavier ou sous le doigt. Sur téléphone il
se pose au-dessus de la barre d'onglets (76 px du bas, safe area en plus),
au bureau à 20 px du coin. Le clic remonte en douceur, sauf sous
`prefers-reduced-motion`, et redéplie la barre du haut. Mesuré à 320 (hors
ligne), 390 et 1280 px : caché en haut, visible à 0,55 descendu, 1 au
survol, retour à 0 px après le clic.

### La déconnexion se confirme dans une fenêtre de l'application

Le client, le 09/10/2026 : « il faut un message de déconnexion plus
professionnel ». `confirm()` ouvrait la boîte du SYSTÈME : l'adresse du site
en titre, les boutons et la police du téléphone, au milieu d'une
application qui a tout le reste à sa marque. `confirmerPro()` pose la même
carte que les autres fenêtres (fond voilé, carte arrondie) : une icône, le
titre « Se déconnecter ? », le compte en pastille (le trigramme, ou BWZ RH),
une phrase qui dit ce qui se passe — le compte n'est plus lié à l'appareil,
les mois et les réglages restent —, puis Annuler et Se déconnecter. Le focus
va sur Annuler, pour qu'un Entrée réflexe ne déconnecte personne ; Échap et
le fond referment. Elle resservira pour les autres confirmations (vider un
mois, une année), qui passent encore par `confirm()`. Éprouvé à 320 (hors
ligne), 390 et 1280 px : aucune boîte du système, Échap et Annuler gardent
le compte, Se déconnecter le retire et rouvre l'écran de connexion.

### « Qui je suis » ne se montre plus à un employé connecté

Le client, le 09/10/2026, capture des Réglages : « c'est pas redondant ces
2 sections ? ». Ça l'était. Pour un employé, « Mon compte » donnait le
trigramme, la fonction et un bouton de déconnexion, et « Qui je suis »
répétait la même phrase avec un second bouton qui faisait la même chose.
Le cadre « Qui je suis » (`#quiFold`) est donc caché pour un compte
employé ; son texte en double et `#btnChangerCompte` sont supprimés. Il
reste affiché pour BWZ RH (le sélecteur sert à choisir l'horaire à
afficher) et quand personne n'est connecté. `#prefillId` reste dans la
page, caché : le pré-remplissage continue de le lire (VBN rempli, salaire
calculé). Le vérificateur donne des sorties identiques à l'octet. Vérifié
à 320 px (hors ligne), 390 px et 1280 px pour l'employé, et à 390 px pour
le RH, sans aucune erreur.

### Les compteurs du Calendrier, sans défilement de côté

Le client, le 09/10/2026 : « optimiser l'onglet calendrier avec les mêmes
styles que les onglets horaire/équipe, surtout ne pas devoir faire de
scroll horizontal dans les cadres, et que les compteurs soient
professionnels et intuitifs ». Mesuré avant le changement à 390 px : les deux
tableaux de l'état des compteurs (congés, flex time) faisaient 430 px de
large dans un cadre de 322 px, d'où un défilement de côté. Les phrases
d'explication faisaient aussi plus de la moitié du cadre.
`renderCompteurs()` dessine maintenant un bloc par sujet, séparés par des
filets `--cadre` :

- **Congés** : sur chaque rangée, le nom, ce qui RESTE en grand et une
  barre « posé / droit de l'année ». Le restant devient rouge s'il est
  négatif. Deux colonnes au bureau.
- **Flex time** : le solde du jour en grand, avec son état. Une jauge de
  −8 h à 104 h, le seuil de 80 h marqué. Quatre chiffres dans la bande de
  `.calstats` (report, portées, reprises, solde au 31/12). La comparaison
  au pied du classeur tient en une ligne, et elle ne passe au rouge que
  s'il y a un écart.
- **Récupération d'heures sup., temps réduit, congés et maladie** : des
  rangées libellé / valeur. MAL et FORM sont écrits en toutes lettres
  (`LIB_CPT_LONG`), car la légende du classeur ne les définit pas.
- **Polyvalence** : une puce par atelier.

Les cadres de l'onglet (les codes, les compteurs) prennent la bordure, le
rayon et le relief de `#calCard`. Les styles `.cpt-tab` et `.cpt-tuiles`
sont retirés. `compteursCalcules()` n'a pas changé : les quatre sorties du
vérificateur sont identiques à l'octet. Mesuré à 320 px (hors ligne),
390 px et 1280 px : aucun bloc ne défile de côté et rien ne dépasse de la
page. Le cadre passe de 1 718 à 1 359 px de haut à 390 px.

Puis, le même jour : « j'aime bcp l'évolution ; par contre le nombre de
rappels et le montant ne se mettent pas bien ; les heures du bas aussi en
jours (8 h) ; les badges de poste optimisés ». Trois retouches :

- la case Rappels écrivait le montant collé au nombre (« 1 95,04 € » se
  lisait comme un seul nombre). Le montant passe sous l'étiquette, en petit
  (`.cstat-m`) ;
- « Congés et maladie de l'année » donne les jours de 8 h en gras et les
  heures à côté, plus discrètes (`hj()`) : 26 j · 208 h ;
- les ateliers de polyvalence sont des badges compacts en grille de colonnes
  égales, chacun avec un point à la couleur de sa zone (celle du liseré du
  tableau du jour, lue dans `POSTES_TRAVAIL`). Cinq ateliers tiennent en deux
  rangées alignées à 390 px.

Les sorties du vérificateur sont identiques à l'octet. Rien ne défile de
côté ni ne dépasse de la page à 320 px (hors ligne), 390 px et 1280 px.

Et encore le même jour : « il faut que cela soit logique, donc le nombre
disponible, le nombre placé, le nombre restant, et afficher VA avant
l'intitulé complet ». Chaque congé porte d'abord son code en badge
(`.cpt-code`, largeur fixe pour que les intitulés s'alignent), puis
l'intitulé, puis trois colonnes : **Disponible** (le solde au 1er janvier,
2025 inclus), **Placé** (posé dans l'horaire), **Restant** (en avant, à
droite). La barre suit en dessous. La liste « Congés et maladie de
l'année » prend le même badge devant l'intitulé. DTT, que la légende du
classeur ne définit pas, s'écrit « Congé d'ancienneté », comme dans la
table des codes de `docs/regles-paie.md`. Le vérificateur donne des
sorties identiques à l'octet. Rien ne défile de côté à 320 px (hors
ligne), 390 px et 1280 px.

Puis : « restant peut être exprimé en jour aussi ». Sous les heures du
restant, les jours de 8 h en petit (« 12 h » puis « 1,5 j »), rouges
quand le restant est négatif. Vérifié à 320 px (hors ligne), 390 px et
1280 px, sans débordement.

### Le relevé de prestations, comme celui reçu au travail

Le client, le 09/10/2026 : « que l'app reproduise une feuille de prestation
comme on reçoit au travail, afin de pouvoir directement comparer avec celle
que l'on reçoit ». Un cadre repliable « Relevé de prestations » se trouve
dans l'onglet Calendrier, sous le mois. `renderReleve()` le remplit à
chaque calcul. Il écrit chaque journée du mois avec les codes de la note
explicative du relevé mensuel (novembre 2025, dans le dépôt privé, résumée
dans `regles/notes-internes.md`) :

- **l'horaire** : 1A40, 2A40 et 3A40 pour les pauses, A21 pour le D seul
  (7h-15h), 4A60 et TP pour le crédit-temps et le temps partiel, Y90 pour
  un week-end sans prestation ;
- **les prestations**, « P » + le jour (1, 3, 5, 8 pour un férié) + la
  pause (0 à 3), sur la prime PAYÉE ;
- **les heures sup** en « U » sur le même schéma, plus F0, J84 (rappel),
  J83, A87 et Z93 ;
- **les absences par leur numéro** : 75, 58, 54, 47, 50, 60, 4, 23, 79 ;
- **9063** pour le chèque du jour ;
- **au bas**, les totaux par code, 454 (chèques du mois, `crNb`), A10
  (jours prestés), 290 (déplacements) et A! (vélo).

Les valeurs sont en centièmes d'heure, comme sur le relevé. **Ce qui n'y
est pas, et pourquoi** : les pointages IN/OUT, que l'application ne connaît
pas ; le REP/FREE et le Z03 d'un repos de semaine, que le classeur ne
distingue pas d'un repos ordinaire ; les soldes de contingents du bas de
page. Rien n'est recalculé : la fonction relit les journées du mois comme
`compute()` les paie. Le vérificateur donne des sorties identiques à
l'octet. Vérifié sur septembre de VBN à 320 px (hors ligne), 390 px et
1280 px : 30 lignes, aucun débordement. Les totaux montrent déjà les deux
écarts connus de la fiche de septembre : la nuit du 30/09 (P13 6,00 au
lieu d'un code du matin) et l'heure sup du même jour (U33 1,00).

### L'Accueil fondu dans le Calendrier

Le client, le 09/10/2026 : « que penses-tu de combiner l'onglet calendrier
avec l'accueil étant donné que les deux sont personnels au profil ? », puis
« go, et fais cela de la manière la plus professionnelle possible ». Les deux
onglets parlaient de la même personne : l'Accueil montrait son profil et son
année, le Calendrier son mois. **Sept onglets deviennent six** ; l'onglet
garde le nom « Calendrier », « Mon horaire » ayant été écarté parce qu'il
se serait lu à côté de l'onglet « Horaire » de l'équipe.

L'onglet se lit de haut en bas : la tête du profil (trigramme, fonction,
statut et binôme sur la ligne du dessous), le mois, l'état des compteurs,
« Mon rythme » (répartition des pauses, nuits et week-ends comparés à
l'équipe, l'année jour par jour, congés restants), le relevé de
prestations, puis les codes. Ce qui était dit deux fois est parti : la
ligne « Rôle » des faits (le binôme est dans la tête), et les puces de
polyvalence des compteurs, qui ne s'affichent plus que si « Mon rythme »
ne les porte pas.

**L'année jour par jour défilait de côté** : 740 px de grille, semaines en
colonnes. Elle est redessinée en douze rangées d'un mois sur trente et une
colonnes, cases carrées de 14 px au plus, la case du jour cerclée : elle
tient à 320 px. `VUES_MIGREES` envoie `resume` vers `horaire`, si bien
qu'un appareil qui avait l'Accueil ouvert retrouve le Calendrier, et c'est
la vue par défaut. Le glissement du mois n'anime que la carte du mois :
les compteurs et « Mon rythme » parlent de l'année et ne bougent pas.
Vérificateur identique à l'octet ; vérifié à 320 px (hors ligne), 390 px et
1280 px, sans débordement ni erreur. **Le tableau « Six onglets » plus bas
date du 22/09** : son Résumé a disparu depuis.

### Le héros de l'Accueil, et un menu nommé par son contenu

Le client, le 09/10/2026 : « il faut mieux présenter la personne connectée
dans le héros de la page d'accueil ; revois également tous les onglets du
menu pour mieux correspondre au contenu ».

**Le héros** (`_pfHead(db,p)`, dans `#rythmeTete`) est une carte à la
couleur de la marque : l'avatar au trigramme cerclé de cyan, « Bonjour /
Bonsoir » et le trigramme, la fonction en grand, puis des puces — binôme
ou équipe, poste attitré à la couleur de sa zone (« En formation ·
Meunerie » en jaune pour qui l'apprend), statut. Dessous, trois chiffres
de soi, lus là où le reste de l'onglet les lit : **congés à placer** (la
somme des « restant » VA, RTT, DTT, RJF de l'état des compteurs, en jours
de 8 h — « vacances restantes » seules valaient 0 pour presque tout le
monde, tout étant déjà posé), **flex time au jour de l'usine** (même
calcul et mêmes couleurs que la jauge), **polyvalences validées** (pas pour
un contremaître). Les « faits » qui suivaient la tête (`_pfFacts`) sont
partis : ils redisaient le poste et les polyvalences. Le poste du jour
n'y est pas : la barre du haut le dit déjà.

**Le menu**, dans l'ordre : **Accueil** (moi : profil, mois, compteurs,
rythme, relevé — « Calendrier » ne disait que le mois), **Salaire**,
**Planning** (les équipes d'un jour — « Horaire » se confondait avec
l'horaire personnel), **Effectifs** (sous-effectifs, congé, absence,
recherche, rappels non nécessaires — « RH » nommait un service, pas un
contenu), **Équipes** (composition, recyclage, statuts, annuaire),
**Réglages**. D'abord ce qui est à moi, puis l'usine du jour, puis sa
structure ; `VIEWS` suit. Les identifiants (`data-v`, `ui/view`) ne
changent pas. Icônes redessinées pour Accueil (maison et personne) et
Effectifs (personne et loupe). Deux phrases visibles renvoyaient encore à
« l'onglet Horaire » : corrigées. Vérificateur identique à l'octet ;
vérifié à 320 px (hors ligne), 390 px et 1280 px sur VBN, SKS, AFA et LCI,
sans débordement ni erreur.

### « Optimise tout » : six pistes, mesurées avant et après

Le client, le 09/10/2026, après une liste de six pistes : « optimise
tout ». Mesuré d'abord à 390 px sur VBN : Accueil 3 903 px, **Salaire
5 025**, Planning 745, **Effectifs 11 795** (quatorze écrans), Équipes
3 242.

- **Effectifs, un mois ouvert** : les sous-effectifs et les rappels non
  nécessaires se rangent par mois (`mqMoisTete()`), le mois qui vient
  ouvert, les suivants repliés sur leur intertitre, qui garde son compte et
  s'ouvre d'un appui (`mqBascule()`, retenu dans `MQ_OUVERT` le temps de la
  page). Au-dessus, une rangée de sauts (`.rhsauts`) — Demande (partie
  depuis avec la fenêtre de recherche), Sous-effectif avec son compte,
  rappels, absents — mène droit à chaque
  cadre, sous la barre du haut. **11 795 → 3 848 px.**
- **Salaire, replis qui se souviennent** : « Vérifier sa fiche en quatre
  temps », la fiche simulée et le contrôle sont des `details.fold
  data-memo`, fermés par défaut, leur état retenu par appareil
  (`ui/fold/<id>`). Le net à recevoir reste sous la fiche repliée, le
  statut du contrôle dans son intitulé ; l'impression déplie tout et
  remet comme avant. **5 025 → 1 996 px.** Le contrôle ne déborde plus à
  320 px (marges, champ et pastille resserrés sous 380 px).
- **Le mois d'avant** : sous le net, « −279,88 € par rapport à
  septembre », et la ligne de fiche qui a le plus bougé
  (`netMoisPrecedent()`, qui relit le mois enregistré par `compute()`
  lui-même, comme `hsDuMoisStocke()`). **Premier essai muet** : le mois
  d'avant n'était pas encore dans le stockage, `save()` attendant 700 ms ;
  `DERNIER_ECRIT` garde ce qui vient d'être écrit. Rien quand le mois
  d'avant est vide (janvier) ou que les deux nets sont égaux.
- **Le retour dans le héros** : « Absent jusqu'au 22 novembre », « En
  repos · reprise le 12 octobre », « En congé · reprise demain »
  (`_pfEtat()`, même lecture que les cadres Absents et Congé et repos :
  `equipeDuJour()`, `finAbsence()`). Rien un jour travaillé. Calculé
  30 ms APRÈS le premier affichage : `equipeDuJour()` rejoue toute l'usine
  (170 ms au processeur divisé par quatre), le héros n'a pas à l'attendre.
- **Les deux dernières boîtes du système** : « Vider ce mois » et
  « Effacer toute l'année » passent par `confirmerPro()`, Annuler au
  focus ; `viderAnnee()` sort de l'écouteur. Éprouvé : Échap referme sans
  rien toucher, la confirmation efface bien les douze mois.
- **Le chargement** : l'horaire est déjà compact (708 Ko, 108 compressés à
  l'envoi). Profilé au processeur divisé par quatre : 2,2 s jusqu'au
  héros, dont plus d'une seconde à lire le script lui-même ; la
  comparaison à l'équipe était déjà différée et mémoïsée. Seul le calcul du
  retour est différé ; découper `index.html` serait le vrai gain, et ce
  n'est pas un chantier d'une passe.

Vérificateur identique à l'octet (aucune lecture touchée), garde-fou du
dépôt à zéro ; vérifié à 320 px (hors ligne), 390 et 1280 px sur VBN, YBT,
LDY et SKS, sans débordement ni erreur.

### Mon salaire dans les cadres du Calendrier

Le client, le 09/10/2026 : « les cadres de l'onglet salaire doivent être
présentés comme pour le cadre horaire (sélection etc.) ». Le sélecteur de
mois flottait au-dessus des cartes ; il est désormais la première ligne du
premier cadre, `#salCard`, avec la barre `.calnav` / `.calmois` du
Calendrier (même `.mnavhote`, donc `placerMnav("salaire")`, le glissement
du mois et le masquage sans personne restent inchangés). Sous lui, le net,
puis les six chiffres du mois en cases bordées comme `.calstats` (valeur
mono 17 px, étiquette en petites capitales). Toutes les cartes de l'onglet
prennent la bordure `--cadre`, le rayon `--rj` et le relief de `#calCard`.
Aucune ligne de calcul touchée ; vérifié à 320 (hors ligne), 390 et
1280 px, flèches du mois comprises. **Reste, préexistant** : à 320 px le
tableau « Contrôle de la vraie fiche » est plus large que sa carte.

### L'écran d'intro

Le client, le 29/09/2026 : « un écran d'intro avec le logo au chargement de
la page ». `#intro` est dans le HTML, juste après `<body>` et avant tout
script : il se peint dès la première image, sur `--marque`, avec
`logo.svg` (déjà dans `CORE`, donc aussi hors ligne) et un trait de
lumière. `finIntro()` l'efface quand l'horaire est lu, jamais avant 0,9 s
ni après 3 s, puis le retire du document. **Le nom n'est pas écrit sous
le logo** : le dessin porte déjà « biowanze », et la première version le
disait deux fois. Sous `prefers-reduced-motion`, il reste un écran fixe.

**Et son fond sous toute l'application, en sombre.** Le client, le
29/09/2026 : « j'aime beaucoup le background de l'écran de chargement, je
voudrais le même à mon application ». Le même dégradé radial (#1b2640 au
centre, #111727 aux bords) vit dans un jeton `--fond`, posé sur un calque
fixe `body::before` — Safari sur iOS ignore `background-attachment:fixed`.
Thème sombre seulement : le clair garde sa page #F6F6F6, relevée sur les
captures du client, et `--fond` y vaut `none`. Les cartes (#212737) restent
au-dessus du fond le plus clair, et le texte posé sur la page tient : le
gris le plus pâle, `--faint`, lit à 4,8:1 sur #1b2640. Vérifié à 390 et
1280 px, en haut de page et défilé.

**Et le logo en filigrane.** Le client, le 30/09/2026 : « le logo doit
rester en fond fixe dans mon app en filigrane une fois l'écran de
chargement disparu ». `body::after`, calque fixe au-dessus du dégradé :
`logo.svg` centré, `min(56vw,300px)` de large, opacité `--filigrane`
(0,06). Thème sombre seulement : en clair le texte blanc du dessin
disparaît et il ne restait qu'un morceau de la marque, `--filigrane` y vaut
0. Les cartes passent par-dessus. Même commit : sans personne choisie, la
barre du haut écrit « Choisissez qui vous êtes / dans Réglages » sur deux
lignes — sur une seule, elle chevauchait BIOWANZE à 320 px. Vérifié à 320
(hors ligne), 390 et 1280 px.

## Congé et absence : la journée rejouée sans quelqu'un

Le client, le 29/09/2026 : un module de **demande de congé** qui dit si
l'opérateur peut prendre congé ce jour-là et propose les changements,
« faits par les opérateurs d'une même pause et selon leurs polyvalences » ;
un module d'**absence** qui trouve les remplacements ou changements pour un
jour ou une période. Ils vivent dans le Résumé, sous les sous-effectifs,
dans un même cadre à deux onglets (Qui, Du, Au, Vérifier).

**Une seule simulation pour les deux, et elle ne recalcule rien** :
`caSimuler()` rejoue la journée par `equipeDuJour()` puis
`postesDePause()`, une fois telle quelle et une fois SANS la personne. Ce
que le rééquilibrage déplace alors d'un poste à l'autre de la même pause,
ce sont les **changements** ; un poste qui passe sous son effectif est un
**trou**, et `pistesDeRemplacement()` — celle des sous-effectifs — dit qui
peut le boucher, minimum des autres postes gardé. Une personne en D ne
pèse que sur la meunerie du matin (la consignation) : c'est la seule
pause rejouée pour elle.

- **Congé** : seule la même pause compte. « Possible », « Possible avec
  changement » (les déplacements ou les pistes nommés), « Pas possible »
  (« Personne dans la même pause »), « Déjà en repos / en congé /
  malade ».
- **Absence** : la même pause, puis les gens **en D** (au matin et à
  l'après-midi, sans code de journée), puis les **rappels** : qui est en
  repos ce jour-là (ni congé, ni maladie, ni poste prévu non presté) et
  sait tenir le poste. Huit rappels au plus, le reste compté. **J'avais
  écrit « repos court sous onze heures », en simple avertissement, et
  c'était faux** : voir « Les règles de la maison » juste dessous.

Rien n'est écrit dans l'horaire : ce sont des propositions. Un clic sur une
journée ouvre son tableau, comme les sous-effectifs. 62 journées au plus
par demande.

**Les règles de la maison, et le changement en chaîne.** Le client, le
29/09/2026 : « oui on peut mettre en place le changement en chaîne (dans
une même pause). Une journée à Biowanze va de 06 h à 06 h le lendemain
(donc AM, PM, N sont sur le même jour). On ne peut jamais faire plus de
12 h sur la même journée, et il faut un minimum de 8 h de repos entre deux
pauses de journées différentes ».

- **Repos : 8 h, et c'est une règle, pas un avertissement.** `CA_REPOS_MIN`
  compte de la fin de la pause de la veille au début de celle du jour : N
  puis AM, 0 h, écarté ; PM puis AM ou N puis PM, 8 h, permis. Un rappel ou
  une personne en D qui ne les aurait pas est écarté, et la fiche le dit
  (« 2 écartés : moins de 8 h de repos »). La première version avertissait
  sous onze heures — le droit commun, pas la maison.
- **12 h par journée** : un rappel ne se cherche que parmi ceux qui ne
  travaillent pas ce jour-là, puisque deux pauses font 16 h.
- **La chaîne**, `caChaines()` : si celui qui sait tenir le poste vide
  laisserait le sien sous l'effectif, un autre de la même pause vient le
  relever, trois maillons au plus, chacun selon sa polyvalence et en
  comptant au poste. **Seules les chaînes les plus courtes se montrent**
  (deux maillons seulement si aucun changement seul ne suffit), et celles
  qui ne diffèrent que par leur dernier maillon se regroupent :
  « VGG Chaud. → CM puis SKS ou PLZ ou SPS → Chaud. ». Mesuré sur octobre,
  toutes personnes : 158 chaînes avant ce tri, 26 après — AAI le 16/10,
  « SMA Ferm. → T. arr. puis LCI Dist. → Ferm. ».

**Un jour ou une période, au choix.** Le client, le 29/09/2026, capture de
son iPhone : « il faut pouvoir sélectionner une date ou une période ». Les
deux champs « Du » et « Au » côte à côte ne disaient pas qu'un seul jour se
demandait en les laissant égaux, et **sous iOS le champ de date ignore
`width:100%`** tant qu'il garde son apparence native : « Au » sortait du
cadre. Un choix « Un jour / Une période » (retenu dans `ui/caDuree`) : un
seul champ « Le » pour un jour, « Du » et « Au » pour une période. Quatre
durées rapides (3 jours, 1, 2, 4 semaines) ont vécu une version ; le
client, le 29/09/2026 : « il ne faut pas les boutons 3 jours 1 semaine
etc » — retirées avec leur écouteur et leurs styles. Le champ de date perd son
apparence native (`appearance:none`) et reprend une hauteur de 42 px.
Chromium ne reproduit pas le défaut d'iOS : seul l'appareil du client dit
qu'il est guéri.

**Plus de texte d'aide sous les onglets.** Le client, le 29/09/2026 :
« pas besoin des explications sous les boutons congés et absence ».
`CA_AIDE`, `#caAide` et ses styles sont retirés ; la recherche n'en avait
déjà plus.

**Le choix du jour ou de la période à droite de la personne.** Le
client, le 29/09/2026, captures de son iPhone : « un jour une période
doit être à droite du choix de trigramme », et la date « centrée comme
les autres filtres ». Le choix prend la seconde moitié de la ligne de
« Qui », à la hauteur du menu (44 px) ; au bureau, une colonne de plus.
Sur téléphone il s'écrit « Jour » et « Période » : « Une période » ne
tenait pas dans 58 px à 320 px. La valeur de la date se posait en haut
du champ sous iOS, sans apparence native : une ligne de 42 px la
recentre, à la hauteur du texte des menus. Rien ne déborde à 320, 390 et
1280 px ; seul l'iPhone du client dit si iOS suit.

**Les champs à la même hauteur.** Le client, le 29/09/2026, capture de
son iPhone : « les 3 filtres doivent avoir la même hauteur » — le menu
déroulant gardait sa hauteur native d'iOS, plus basse que le champ de
date. Menus et champs perdent tous leur apparence native et prennent
44 px ; le chevron du menu est redessiné. Mesuré à 320, 390 et 1280 px :
44 px partout, les trois de la recherche sur la même ligne.

Éprouvé le 29/09/2026 : VBN en congé le 02/10 est « Pas possible » (seul
contremaître du matin, aucun cadre dans la pause), le 01/10 « avec
changement » (VGG, adjoint, prend le poste) ; TCE les 02-04/10, SVE vient
de la distillation à la meunerie ; GPS absent le 07/10, AFA et ATR en D,
YPE en rappel, VGG en « repos court · veille N ». Les quatre sorties du
vérificateur sont identiques à l'octet (le module ne touche aucune
lecture) ; rien ne déborde à 320 (hors ligne), 390 et 1280 px, en clair et
en sombre.

### Le doublage de 12 h, et la recherche par pause et par poste

Le client, le 29/09/2026, à la question du doublage : « **A** » — le
proposer. Puis : « il faut aussi un troisième module de recherche par pause
sur un tel poste — exemple : le 21 octobre je recherche un opérateur
chaudière en pause de N ; ce module peut également être adapté pour le
module sous-effectif en proposant des remplacements ».

**Un tronc commun, `caCandidats()`**, sert aux trois modules et aux
sous-effectifs. Il rend, pour un poste d'une pause : les chaînes de la
même pause (`caChaines()`), les gens en D, le doublage et les rappels,
avec le même repos de 8 h. `caGroupes()` les écrit, toujours dans cet
ordre. Le congé ne garde que la même pause, comme avant.

- **Le doublage, l'après-midi** : le matin reste jusqu'à 18 h (« Reste
  → 18 h », 6 h-18 h), la nuit arrive à 18 h (« Arrive 18 h »,
  18 h-6 h). Le repos tient toujours (12 h dans les deux cas).
- **Le doublage, la nuit** : le client, le 29/09/2026, « cela arrive de
  rester après sa nuit 14-02, ou même rarement de commencer son matin à
  02 h (faire 02-14) ». L'après-midi reste jusqu'à 2 h (14 h-2 h), le
  matin du LENDEMAIN arrive à 2 h (2 h-14 h). Celui qui reste ne peut pas
  être du matin ni en D le lendemain (4 h de repos) ; celui qui arrive
  fait 4 h sur la journée du jour, donc n'y est pas prévu, ou seulement au
  matin (8 + 4 = 12 h, 12 h de repos après 14 h). Les deux écartés
  comptent parmi « moins de 8 h de repos ». Le lendemain d'un 31/12
  n'est pas dans l'horaire : pas d'arrivée proposée.
- **Le doublage, le matin** : le client, le 29/09/2026, « ceux de
  l'après-midi peuvent arriver à 10 h, mais c'est rare de demander à
  quelqu'un de rester 4 h après sa nuit ». « PM arrive 10 h » (10 h-22 h)
  se montre donc EN PREMIER, « N veille reste → 10 h » (22 h-10 h)
  ensuite. Celui qui arrive ne doit pas sortir d'une nuit (4 h de repos) ;
  celui qui reste n'est, ce jour-là, qu'en repos ou de nuit. Éprouvé le
  06/10 AM gluten : cinq PM à 10 h, les six nuits du 05/10 pour rester.
- **Toujours par paire, et l'horaire écrit.** Le client, le 29/09/2026 :
  « pour ceux qui restent après leur PM il faut indiquer 14-02, et pareil
  pour les autres cas ; si on fait rester un 06-18, il faut un 18-06 pour
  que cela fonctionne ». Les deux rangées vivent dans un même cadre,
  « Doublage 12 h · un de chaque », et s'intitulent par l'horaire demandé :
  06-18 et 18-06, 14-02 et 02-14, 10-22 et 22-10. **Une moitié seule ne se
  montre plus** — la première version l'affichait avec « personne pour
  arriver à 18 h » : ce n'était pas une solution. Seuls ceux qui font leur
  journée entière, sans code de journée, peuvent doubler.
- **La recherche** (troisième onglet du cadre, rebaptisé « Congé, absence
  et recherche ») demande une pause, un poste et un jour ou une période ;
  pause et poste sont retenus dans `ui/caRech`. **Une date unique** : le
  client, le 29/09/2026, « la recherche doit être pour une date unique
  (pas de période) » — le choix « Un jour / Une période » disparaît sur
  cet onglet, et celui des deux autres reste retenu. Rien n'est retiré de la
  journée : elle dit l'effectif (« Au complet » ou « Sous-effectif »),
  qui tient déjà le poste, puis les candidats. Éprouvé sur l'exemple du
  client : le 21/10, N chaudières, 1/2, GJR au poste, six rappels (GPO et
  JBS en repos, quatre après une nuit la veille).
- **Les sous-effectifs** gardent leur première ligne (les présents : même
  pause, à déterminer, en D) ; s'y ajoutent la chaîne quand aucun présent
  ne suffit seul, le doublage et les rappels. Les 21 et 22/10 (N
  chaudières) affichent désormais six et cinq rappels, et quatre écartés
  pour le repos. Depuis le doublage de nuit, ils proposent aussi trois et
  quatre après-midi qui restent jusqu'à 2 h, et cinq et quatre matins du
  lendemain qui arrivent à 2 h.

**Changer de pause, là où un poste a du monde en trop.** Le client, le
29/09/2026 : « il arrive aussi de regarder les pauses avant/après s'il y a
des effectifs en trop ; par exemple s'ils sont deux à un poste qui n'en
demande qu'un en PM et qu'il manque quelqu'un en nuit, on peut lui
demander s'il veut bien changer de pause et faire la nuit ».
`caCandidats()` rejoue les autres pauses du même jour (`caAutres()`, une
fois chacune, sans la personne absente) et propose, sous « Change de
pause », ceux dont le poste garde son minimum sans eux (`caLibre()`, la
règle des chaînes, désormais partagée), qui ont la polyvalence du poste
vide, font leur journée entière et gardent 8 h de repos avec la veille
et le lendemain, comptées sur la pause NOUVELLE. Ce n'est pas un
doublage : la personne quitte sa pause. Modules absence, recherche et
sous-effectifs ; pas le Congé, qui reste dans la même pause. Éprouvé : le
22/10 en N aux chaudières, PLZ (gluten du matin, en surplus) et ATR
(adjoint en plus du contremaître l'après-midi) ; le 21/10, personne,
aucun poste n'ayant de surplus compatible. Vérificateur identique à
l'octet.

**Le cadre de recherche optimisé** (le client, le 29/09/2026, « optimise
tout » sur cinq pistes) : plus de texte d'aide sur cet onglet ; pause,
poste et date sur une seule ligne ; plus de bouton « Vérifier », le
résultat se refait à chaque changement de champ ; un seul titre
(« N Chaudières 1/2 · Éq. 2 », l'effectif rouge s'il manque quelqu'un,
vert sinon), sans intertitre de semaine ni bloc de date, la date étant
dans le champ. Dans les trois modules et les sous-effectifs, les rappels
se regroupent en « Rappel · reposés » et « Rappel · veille N »
(« veille PM »…), et le doublage en « PM reste → 2 h » / « AM demain
arrive 2 h » (« AM reste → 18 h » / « N arrive 18 h ») : l'étiquette ne
porte plus que le trigramme. Rien ne déborde à 320 et 390 px.

**Poste d'abord, et rien tant qu'on n'a pas choisi.** Le client, le
29/09/2026 : « poste doit être devant le filtre trigramme, et à
l'ouverture aucune date ; rien ne doit s'afficher tant que l'on ne change
pas un filtre ». La recherche n'a pas de menu « Qui » : le filtre
visé est la pause, et Poste passe devant (`order:-1`, colonnes
réordonnées), suivi de Pause puis de la date. `caDates()` laisse la date
vide en recherche, l'ouverture de l'onglet ne calcule plus rien, et une
date vide n'affiche rien (pas même « Choisissez une date »). Congé et
Absence gardent leur date par défaut. Vérifié à 320 (hors ligne), 390 et
1280 px.
Puis, le même jour, en partie défait : « réafficher une date dans le
filtre et remettre Vérifier comme avant ; pas de ligne de séparation sous
le bouton tant qu'il n'y a pas de résultat ». La date du jour revient,
le bouton aussi, et rien ne se calcule avant son clic — ni à l'ouverture
de l'onglet, ni à un changement de champ. Poste reste en premier. Le
filet quitte le bas du formulaire pour le haut de `#caCorps`, qui se
cache vide (`:empty`) : il n'apparaît qu'avec un résultat, dans les trois
onglets.

**Un cadre pointillé par type de solution.** Le client, le 29/09/2026,
capture à l'appui : « il faut regrouper tous les types de solutions dans
le même genre de cadre pointillé et toujours mettre les premiers résultats
sous le type, mais ça peut être à droite des créneaux horaires pour les
12 h ; il faut dire Rappel - Repos ». `caCadre()` pose l'intitulé en haut
et les trigrammes dessous : « Au poste », « Changements », « Même
pause », « En D », « Change de pause », « Rappel - Repos », « Rappel -
Veille N ». Le doublage
garde ses horaires à gauche des noms. Les sous-effectifs perdent leur
ligne « → » d'avant : leurs présents sont désormais la « Même pause » et
le « En D » de `caCandidats()`, repos de 8 h compris — mesuré, aucune
des deux journées restantes (21 et 22/10) n'avait de piste dans cette
ligne.

**« En poste », cadre plein, et une étiquette « ? » par place vide ;
« Prolongation 12 h ».** Le client, le 29/09/2026 : « Au poste » devient
« En poste », sans pointillé — ce n'est pas une solution, c'est l'état du
poste —, et chaque place manquante s'y lit en « ? » bordé de rouge (le
21/10 en N aux chaudières : GJR puis « ? »). Le cadre s'affiche dès qu'il
manque quelqu'un, même si personne n'est au poste. Le doublage s'intitule
« Prolongation 12 h », sans « un de chaque » : les deux lignes d'horaires
disent déjà la paire. Rien ne déborde à 320 et 390 px.
Puis, le même jour : le « ? » a la taille d'une étiquette de trigramme
(trois signes de large, 36,8 px mesurés comme GJR), et « Qui » se
resserre — « ce n'est que 3 lettres » : trois huitièmes de la ligne sur
téléphone (89 px à 320, 115 à 390), 110 px au bureau ; Du et Au restent
égaux en période.
Et dans le tableau du jour, le compte « 1 / 2 » d'une case en manque
cède la place aux mêmes étiquettes « ? » bordées de rouge, une par place
vide (le client, le 29/09/2026) ; le compte reste dans l'infobulle. Le
fond rouge pâle de la case demeure. Mesuré à 390 px : « ? » et GJR font
33,5 px tous deux ; rien ne déborde à 320 et 390 px.
Le fond de la case passe de l'orangé de `--out-soft` à un rouge de la
teinte du badge (le client, le 29/09/2026) : un jeton `--manque-fond`,
`#F8D4CF` en clair et `#512E30` en sombre, déclaré dans les trois blocs de
thème. Un `color-mix` avec la carte a été essayé d'abord : sur le bleu
nuit, il virait au mauve.
« H. flot. » devient « H.fl. » dans le tableau du jour (le client, le
29/09/2026 : « le badge h flot. doit être de la même taille que les autres
avec l'horaire ») : même sans coupure, « VGG H. flot. » demandait 65 px
dans une case de 56 à 390 px et passait sur deux lignes. « VGG H.fl. »
fait 54 px, une ligne, comme « ATR 7-15 », de 320 à 1280 px.

**Une ligne « DS » sous la formation.** Le client, le 29/09/2026, après
avoir fait retirer le « DS-CE » écrit à côté du trigramme : « une ligne
sous formation DS, qui reprend ceux qui sont en DS ou CPPT ce jour-là ».
Ceux que leur code de jour (DS, DS-CE, CPPT, D-CPPT) range dans la
colonne D quittent la case de leur poste pour cette ligne, avec leur
horaire s'il est connu (QBY 10-18). Qui tient son poste malgré le code —
une plage de pause écrite, GPS `["10h-22h","D-CPPT"]` — reste à son
poste, et la colonne D n'attendant personne, aucun effectif ne bouge.
Au navigateur : le 21/10, ATR, LCI et QBY ; le 30/09, ADK, LHR et VBN ;
le 24/11, cinq personnes. La ligne ADJ disparaît le 21/10, ATR y étant
seul. Rien ne déborde à 320, 390 et 1280 px.
Puis, le même jour : **pas d'horaire sur la ligne DS**, comme sur FORM.,
et **pas de jaune sur ces deux lignes** — le client : « quand ceux en
formation sont sur un poste qu'ils ont déjà la polyvalence (ou dans la
ligne DS ou FORM.) ils doivent avoir un badge normal ». Le premier cas
était déjà juste : le jaune suit `compteAuPoste()`, donc la polyvalence
(SKS, validé en fermentation, distillation et chaudières, n'est jaune
qu'en meunerie). Au 21/10, les jaunes restants — SKS meunerie, NPI gluten,
SVE et CDT distillation, MGY chaudières — sont tous sur le poste qu'ils
apprennent, sans la polyvalence.

**Le matin : 06-18 et 18-06 avec ceux du poste.** Le client, le
30/09/2026 : « pour un AM, s'il faut une prolongation 12 h, c'est toujours
mieux 06-18 18-06 en proposant les effectifs de PM et N de ce poste ».
L'après-midi du poste vide arrive à 6 h et reste jusqu'à 18 h, la nuit du
même poste arrive à 18 h : personne d'autre ne bouge. Celui de
l'après-midi qui sort d'une nuit est écarté (0 h de repos). Quand cette
paire existe, le 10-22 / 22-10 ne se montre plus ; il reste en repli.
Éprouvé sur VBN absent : le 01/10, GPS 06-18 et ATR 18-06 ; le 02/10, YPE
et GPS. Vérificateur identique ; rien ne déborde à 320 (hors ligne), 390
et 1280 px.

**Le relais d'une chaîne peut venir du D.** Le client, le 30/09/2026, sur
PDE malade le 02/10 (STEP du matin à 0/1) : « PDF est repris pour aller à
la STEP (polyvalence) et JBI, qui est en D, pour aller aux chaudières ;
c'est ce qui a été fait ». `caChaines()` accepte, comme dernier maillon,
une personne en D (matin et après-midi, sans code de journée, 8 h de
repos) qui sait tenir le poste que le maillon précédent a quitté. Seul,
il ne tiendrait pas le poste vide : le cadre « En D » le dit déjà quand il
le peut. Au navigateur : « PDF Chaud. → STEP puis JBI D ou MHI D →
Chaud. ». Absence, recherche et sous-effectifs ; **pas le Congé**. Le
relais a été étendu au Congé le 30/09/2026 puis retiré dans l'heure, le
client : « annule, c'est ok » — pour PDE le 02/10, le Congé qui dit « Pas
possible · Personne dans la même pause » est juste.
Vérificateur identique ; rien ne déborde à 320 (hors ligne), 390 et
1280 px.

**La chaîne se lit en étapes numérotées.** Le client, le 30/09/2026 :
« moyen de mieux présenter la chaîne ? ». Tout tenait sur une ligne qui
passait à la ligne n'importe où. Chaque étape est désormais une ligne :
un numéro rond, les trigrammes (« JBI ou MHI » pour les alternatives du
dernier maillon), puis le déplacement en gris (« Chaud. → STEP »), qui
passe sous les trigrammes quand la place manque — la colonne des
solutions ne fait que 150 px à 320 px, et une grille à trois colonnes y a
d'abord fait déborder les étiquettes. Rien ne déborde à 320 (hors ligne),
390 et 1280 px.

**Et l'horaire proposé à qui vient du D.** Le client, le 30/09/2026 :
« si tu as compris, tu peux proposer de modifier l'horaire des personnes
en D ». Qui quitte sa journée pour tenir un poste prend l'horaire de la
pause : l'étiquette porte « 6-14 » au matin, « 14-22 » l'après-midi
(`CA_HOR_D`), dans le cadre « En D » comme au dernier maillon d'une
chaîne (« JBI 6-14 · D → Chaud. »). Le repos de 8 h était déjà compté sur
la pause. Vérifié sur PDE et VBN absents le 02/10, à 320 (hors ligne),
390 et 1280 px ; vérificateur identique.

**Un contremaître ne remplace jamais ailleurs qu'au poste de
contremaître ; un adjoint, si.** Le client, le 29/09/2026. La règle vit
dans `peutTenir()`, le point de passage du rééquilibrage et des
propositions. Mesuré : `--manques` sur l'année entière, `--polyvalence`
et `--polyvalence --tout` **identiques à l'octet** — le rééquilibrage ne
déplaçait déjà aucun contremaître. Elle mord sur les propositions : le
21/10 en N aux chaudières, VBN ne figure plus parmi ceux qui restent
jusqu'à 2 h ; les adjoints (JBI, VGG, ATR) restent proposés partout.

**« Changement de poste », au pluriel pour une chaîne.** Le client, le
30/09/2026 : le cadre « Changements » des modules Congé et Absence
s'intitule « Changement de poste » quand un seul déplacement suffit,
« Changements de poste » quand il en faut plusieurs. Mesuré sur octobre,
40 personnes : 6 cadres au singulier (ALZ en congé), 4 au pluriel (BLR).

Les onglets du cadre deviennent « Congé », « Absence », « Recherche ».
Les quatre sorties du vérificateur sont identiques à l'octet (il ne
découpe pas ces modules) ; rien ne déborde à 320 et 390 px, en clair et
en sombre.

### La recherche dans une fenêtre à elle

Le client, le 09/10/2026 : « un bouton recherche pour les 3 types de
recherche, et donc ne pas les mélanger avec les sous-effectifs et rappels
etc », puis « go » sur la fenêtre et le bouton par sous-effectif. L'onglet
Effectifs mêlait deux usages : CHERCHER une solution (un outil qu'on ouvre)
et SURVEILLER ce qui ne va pas (une liste qu'on parcourt).

- **`#caCard` quitte l'onglet** pour une fenêtre, `#caSheet`, hors des
  onglets : elle monte du bas sur téléphone (poignée, coins hauts
  arrondis, en-tête collé quand les résultats défilent) et se centre au
  bureau (760 px au plus). Les trois onglets Congé · Absence · Recherche,
  les champs et le calcul n'ont pas changé : seul leur cadre a bougé.
- **En tête d'Effectifs, un bouton « Rechercher · Congé · absence ·
  remplaçant »** (`#caOuvrir`). Le saut « Demande » de la rangée de sauts
  part avec le cadre.
- **« Chercher un remplaçant » au pied de chaque sous-effectif** (`.mqcher`) :
  `ouvrirRecherche({pause, poste, an, mois, jour})` passe sur Recherche,
  remplit les trois champs et calcule — avant, il fallait les recopier à la
  main. Le reste de la fiche ouvre toujours le Planning de ce jour-là.
- **Se referme** par la croix, le fond voilé, Échap et le geste retour du
  téléphone : l'ouverture pose une entrée d'historique (`pushState`), et
  `popstate` la referme au lieu de quitter l'onglet. Un clic sur une journée
  du résultat ouvre le Planning et referme la fenêtre (`setView()` la ferme
  toujours). La page dessous ne défile plus tant qu'elle est ouverte.

Vérificateur identique à l'octet (aucune lecture touchée) ; éprouvé à 320
(hors ligne), 390 et 1280 px : ouverture, focus sur la croix, calcul,
retour, préremplissage depuis le sous-effectif du 10/10 (AM · STEP · Éq. 3,
« Rappel - Repos » PDF), Échap, clic vers le Planning, rien ne déborde.

### Un onglet pour la recherche, et les réglages dans le héros

Le client, le 10/10/2026 : « je pensais à un onglet recherche à part ; que
penses-tu de placer les réglages dans le héros de l'accueil ? », puis, sur
le héros, « il doit contenir le logo et le trigramme doit être à côté ; il
faut des infos intéressantes, pas nécessairement les jours de congés
restants ». **Et sur la méthode : « il ne faut pas de maquette ; toujours
poussé sur main, et on optimisera au fur et à mesure ».** Une proposition
passée par une maquette publiée a coûté un aller-retour pour rien : on code
dans l'application, on pousse, et le client corrige sur la vraie page.

- **La fenêtre de la veille devient un onglet**, `#v-recherche`, entre
  Planning et Effectifs (vue `recherche`). Congé · Absence · Recherche, les
  champs et le calcul n'ont pas bougé ; `#caSheet`, sa croix, son fond,
  Échap, l'entrée d'historique et le bouton `#caOuvrir` d'Effectifs sont
  partis. « Chercher un remplaçant » d'un sous-effectif ouvre l'onglet,
  jour, pause et poste remplis (`ouvrirRecherche(pre)`).
- **Réglages n'est plus un onglet** : la roue en haut à droite du héros
  (`.pf-roue`) y mène — sur téléphone c'est le seul chemin, la barre du
  haut étant masquée depuis le 03/10/2026 (je l'avais oublié et en ai
  parlé au client comme si elle existait) ; au bureau, où la barre porte
  les onglets, son trigramme (`data-go`) y mène aussi, et la page s'ouvre sur « ‹ Accueil » (`.regretour`). La vue
  `reglages` reste dans `VIEWS`, de sorte que `ui/view` la retrouve.
- **Le héros** : le logo (`logo.svg`, déjà dans `CORE`) et le trigramme en
  grand, côte à côte, la fonction et le binôme ou l'équipe dessous ;
  « Bonjour » et le retour (« En repos · reprise le 12 octobre ») ; les
  puces poste et statut ; puis, au lieu des congés à placer et des
  polyvalences, le **prochain poste** (la pause en pastille, « Demain » ou
  le jour, ses heures, l'atelier si la cellule l'écrit) et trois chiffres :
  le **prochain week-end libre** (samedi et dimanche sans prestation, « Ce
  week-end » quand c'est le cas), les **nuits du mois** faites sur prévues,
  et le **flex time** au jour de l'usine (vert, jaune au-dessus de 80 h,
  rouge hors des bornes). `_pfInfos()` lit les journées par
  `lireJournee()`, et `horaireDe()` pour passer en 2027. **Première
  version fausse** : elle testait `r.h>0`, alors qu'une journée sans heure
  écrite laisse `r.h` vide (journée entière) ; personne n'avait de prochain
  poste et les nuits valaient 0/0. Corrigé par la règle de `compute()`.

**Puis, le même jour** : « l'onglet horaire doit être un calendrier,
l'onglet rechercher tout à droite ; pas mal le héros mais il y a moyen
d'encore mieux faire ». L'icône de Planning, une grille qui se lisait
comme un tableau, devient un calendrier à anneaux (le menu du téléphone
n'a que des icônes : c'est par elles qu'on nomme un onglet). Recherche
passe en dernier, après Équipes. Le héros gagne **les sept jours qui
viennent**, aujourd'hui compris : le jour, la date, et la pause aux
couleurs du calendrier (AM, PM, N, D), le congé ou « MAL » en neutre, un
tiret pour un repos. Le prochain poste dit « dans n j » et ouvre le
Planning de ce jour-là. Le week-end libre se tait pour qui est malade
aujourd'hui (YBT, absent jusqu'au 22/11, l'affichait).

**Et encore le même jour**, capture de l'iPhone à l'appui : « l'onglet
salaire n'est pas bien par rapport aux autres (vérifie toi) ; le héros
peut mieux faire ; ça doit faire 100 % pro et pas d'info redondante ».

- **Héros** : plus de « Bonjour », de ligne d'état ni de puces. Sous le
  trigramme, deux lignes : fonction · binôme ou équipe, puis poste
  attitré (en jaune s'il est en formation) · statut. Le bloc du prochain
  poste dit « Reprise » quand on n'est pas au travail aujourd'hui, ce qui
  remplace « En repos · reprise le 12 octobre » (le même jour écrit deux
  fois) ; `_pfEtat()` est retiré. Les nuits du mois partent (la semaine
  et le cadre du mois les montrent), le week-end libre ne s'écrit que
  s'il tombe au-delà des sept jours, et « Flex time » devient « Solde
  flex time » : le cadre du mois, juste dessous, donnait déjà un « Flex
  time » qui est celui du MOIS. Seul dans le pied, il tient sur une ligne.
- **Salaire**, mesuré à côté des autres onglets : le net perd son fond
  cyan et se centre, en chiffres mono, comme les chiffres de l'Accueil ;
  « Net estimé » sans le mois, déjà dans la barre ; les tuiles ne gardent
  que l'argent (primes d'équipe, suppléments week-end, primes de rappel,
  chèques-repas) — heures, jours et brut étaient déjà à l'Accueil ou en
  tête de la cascade ; « Le mois en un coup d'œil » part (c'était le
  calendrier de l'Accueil) ; la ligne « Net à recevoir » sous la fiche
  simulée ne sert plus qu'à l'impression ; les cadres prennent le filet
  sous l'en-tête des cadres de l'Accueil. **Piège évité** : masquer
  `#v-salaire .final` aurait aussi masqué la dernière ligne de la
  cascade (`.fall .row.final`) ; la règle vise `.card>.final`.

L'icône de Salaire, un billet frappé d'un €, devient un **portefeuille**
(le client, le 10/10/2026 : « il faut changer le logo du salaire dans le
menu ») : même trait que les autres, lisible à 25 px dans la capsule.
La roue des réglages, dessinée en rayons, ressemblait à un bouton de
luminosité (le client, le même jour) : c'est désormais un engrenage à
dents.

**« Go pour tout »** (le client, le même jour), sur cinq pistes proposées
pour le héros :

1. **le poste du moment** : tant que la pause du jour n'est pas finie, le
   bloc dit « En poste · Fin à 15 h » avec une barre qui avance, ou
   « Aujourd'hui · Début à 6 h » avant elle ; ensuite seulement le
   prochain poste. Les heures se comptent depuis minuit du jour de
   l'usine (`PF_DEB`, `PF_FIN`), la nuit finit donc à 30 h : LCI à 2 h le
   17/10 est « En poste · Fin à 6 h » sur la nuit du 16 ;
2. **les sept jours se touchent** : chacun ouvre le Planning de ce jour ;
3. **l'atelier sous la pause** quand la cellule l'écrit (`PV_COURT`), et
   un point jaune quand la journée porte un rappel ;
4. **les changements dans la semaine** : la journée modifiée est cerclée
   de cyan, l'ancienne lecture dans son libellé d'accessibilité. Quand
   tous les changements tombent dans ces sept jours, la carte « Votre
   horaire a changé » s'efface au profit d'une ligne « n journées
   modifiées · Vu » sous la semaine ; s'il en reste au-delà, la carte
   revient, et son « Vu » efface aussi les cercles. Éprouvé : 13 et 14/10
   modifiés, cercles et ligne, carte cachée ; 13/10 et 20/11, carte
   visible ; « Vu », cercles partis, et rien au rechargement ;
5. **moins haut** : semaine et bloc du poste resserrés.

Mesuré le 10/10 sur VBN, SKS et LCI : prochain poste le lundi 12 (D 7-15,
D 7-15, AM 6-14), nuits 0/2, 1/1, 1/6. Rien ne déborde à 320 (hors ligne),
390 et 1280 px ; le sous-effectif du 10/10 mène à l'onglet avec STEP · AM
calculé. Vérificateur identique à l'octet (`--polyvalence` ne bouge que
par la date du jour, identique à `HEAD`).

### L'audit multi-agent du 10/10/2026

Le client : « faut une analyse multi agent avec skill etc pour optimiser au
max chaque onglet et toute l'app ». Sept auditeurs (un par onglet, plus un
transversal : performance, hors ligne, accessibilité, cohérence), chacun au
navigateur à 320, 390 et 1280 px sur VBN, LCI, YBT et SKS, puis un
sceptique qui a tout remesuré : **72 constats bruts, 19 retenus, 19
rejetés** (faux, déjà faits, ou contraires à une décision du client — par
exemple les trigrammes empilés ou l'absence de légende au tableau du jour).

**Premier lot, appliqué le même jour :**

- **Planning à 320 px** : la date longue débordait sur la flèche « jour
  suivant » et en volait le toucher, trois jours sur quatre. Libellé court
  sous 380 px (« Sam. 10 oct. »), flèches à 10 px du bord, zone de toucher
  de 44 px. Le glissement de jour écoute tout le cadre, barre de date
  comprise (il visait `#eqCorps`, qui n'existe plus).
- **Une fiche de journée n'est plus un bouton** (Effectifs, rappels,
  Recherche) : toucher un trigramme ou commencer un défilement ouvrait le
  Planning et faisait perdre la recherche. Seul l'en-tête de date y mène
  (`mqCible()`), « Chercher un remplaçant » est un vrai bouton, et la
  recherche d'un jour a son « Voir le planning de ce jour ».
- **Salaire** : « Net imposable » portait le net APRÈS impôt (C.E) — il
  s'appelle « Net après impôt » ; le mode d'emploi renvoyait aux onglets
  disparus « Fiche » et « Contrôle ». Un contrat resté à l'exemple
  (`valeurExemple()`) pâlit le net, l'appelle « Net d'exemple », tait la
  comparaison au mois d'avant et monte l'alerte sous la barre du mois, avec
  « Renseigner mon contrat ». Les tuiles passent en grille 2 × 2 (4 au
  bureau) : la cinquième restait seule sur sa ligne.
- **Équipes** : la période du recyclage s'écrivait dans un `#pvSub` qui
  n'existait plus ; une ligne sous la grille dit ce que « 7/10 » compte
  (jours relevés par l'app / recyclages des RH). L'annuaire prend
  `statutAffiche()` comme le reste de l'onglet.
- **Accueil** : la grille de polyvalences de « Mon rythme » (`_pfPoly`)
  doublait l'onglet Équipes et coûtait 2,7 s au démarrage d'un téléphone
  lent : retirée, les compteurs gardent les ateliers et « Voir mon
  recyclage ». La courbe des congés restants (`ryCongesChart`) partait des
  journées POSÉES et tombait à zéro par construction : retirée. Les congés
  déjà comptés ne se redisent plus dans « Maladie et autres absences ». La
  tuile du mois s'appelle « Flex du mois ». L'intro part dès que le héros
  est dessiné, et la comparaison à l'équipe attend que le fil soit libre.

Mesuré : l'intro part en 1,7 s (le filet de 7 s n'est plus atteint) ;
Accueil de 3 903 à 3 509 px à 390 px ; rien ne déborde à 320 (hors ligne),
390 et 1280 px ; vérificateur identique à l'octet. Binôme, cycle et
décalage des Réglages : faits ensuite, voir « Le cycle des primes de
rappel lu dans l'horaire ».

**Second lot, le même jour :**

- **Effectifs** : un mois replié ne se calcule plus — ses fiches et leurs
  candidats (`caCandidats`, le plus lourd) se construisent à son dépli
  (`mqDiff`, `hote._diff` appelé par `mqBascule()`). Au processeur divisé
  par quatre, 1 393 → 1 228 ms ; 6 fiches calculées sur 25 à l'ouverture.
  L'essentiel du temps reste le balayage des journées (`mqJoursAVenir`).
- **Réglages** : « Mon contrat » ne montre que ce qui est à soi ; les
  valeurs communes sous cadenas vont dans un repli fermé « Valeurs communes
  de l'équipe », écrites en clair (`valFige()` : taux en %, 38:40, diviseur
  à deux décimales). Le calage du précompte, personnel, passe sous « Mon
  précompte ». La sauvegarde suit `data-scope`, pas l'endroit du champ.
- **Recherche sur une période** : les journées « possible, rien à
  changer » et « déjà en repos ou en congé » tiennent chacune en une ligne
  de dates ; seules les journées qui demandent quelque chose gardent leur
  fiche. Le bilan reprend les mots des verdicts (`caVerdict`), la pause
  s'écrit AM, PM ou N, et le dernier mode revient (`ui/caMode`). Mesuré :
  VBN du 12/10 au 08/11, 12 fiches au lieu de 28.
- **Planning** : un jour trop chargé pour le cadre se signale par un fondu
  en bas, qui disparaît en bas du défilement.
- **Mon rythme** compare à la « moyenne des opérateurs » (ou des cadres),
  ce qu'il calcule, et non à une « équipe » ; plus de tutoiement.
- Zones de toucher de 44 px autour des flèches du mois et de la roue ;
  « STEP. » perd son point ; Recherche et Réglages prennent la bordure des
  cadres de l'Accueil.

Rien ne déborde à 320 (hors ligne), 390 et 1280 px, aucune erreur ;
vérificateur identique à l'octet, découpe de `comparer-fiches` à l'épreuve.
**Laissés de côté, et pourquoi** : unifier les têtes de cadre de tous les
onglets (le client a lui-même choisi les titres centrés d'Effectifs et
d'Équipes) ; un plancher de 11 px pour tous les libellés (à mesurer onglet
par onglet) ; « 1 personne manquante » et le cadre « En poste » des
sous-effectifs, demandés par le client.

**Le cycle des primes de rappel lu dans l'horaire** (le client, le
10/10/2026, « Optimise tout », en réponse à la question posée). Binôme,
cycle et décalage ne servent qu'à une règle : pas de prime de rappel pour
une prestation au matin sur une journée prévue en D du cycle (procédure,
point D). Ils se saisissaient à la main, et presque personne ne le
faisait : tout le monde calculait avec « Binôme 1, 6 semaines, 0 ».
`cycleDitD()` lit désormais le cycle de la personne liée dans ses propres
cellules (`moisDe().fit`, la lecture du calendrier) ; sans personne liée,
ou un mois que le cycle ne cale pas, les trois réglages reprennent la
main. Dans « Mon contrat », ils cèdent la place à une ligne en lecture
seule, « Cycle de roulement · 6 semaines », lu dans l'horaire.

Mesuré mois par mois sur VBN, LCI, AFA, VGG, GPS et JBI, ancienne et
nouvelle version côte à côte : **seul JBI change**, trois primes de rappel
retirées, le 06/07 et les 19 et 20/08, trois remplacements de
contremaître en 6h-18h pendant ses semaines de D, soit le cas que la
procédure exclut ; ses relevés de pointage diront si la prime a bien été
refusée. Vérificateur identique à l'octet, découpe de `comparer-fiches` à
l'épreuve ; rien ne déborde à 320 px (hors ligne), 390 et 1280 px.

**Le reste des finitions, le même jour** (le client : « Go ») :

- **Les deux GBT se distinguent** dans l'onglet Équipes : un exposant
  d'équipe (« GBT⁴ », « GBT⁵ ») et l'infobulle « GBT · Équipe 4 »,
  calculés une fois pour les trigrammes que deux personnes partagent
  (`_orgJeton`, `__partage`).
- **Code mort retiré** : les règles CSS de l'ancienne plaque cyan de
  l'onglet Planning (`#tab-jour`, retirée le 09/10, dont un
  `.dotwarn{display:none}` qui aurait caché en silence un point d'alerte),
  et quatre fonctions que plus rien n'appelait (`_orgZone`,
  `anneeDeLaPersonne`, `atelierDuJour`, `tipOn`). Le menu du bas est
  identique au pixel, capture contre capture, à 320, 390 et 1280 px.
- **L'annuaire garde son contenu** : l'audit proposait d'en retirer le
  statut et les polyvalences, déjà dans « Statut » et « Recyclage », mais
  c'est le contenu que le client a lui-même réglé le 06/10.
- **Effectifs n'est pas accéléré davantage** : profilé, il reste environ
  350 ms de calcul sur PC, presque tout dans la lecture de chaque journée
  de chacun (`equipeDuJour` → `lireJournee`). Mettre ces lectures en cache
  partagé exposerait les sous-effectifs aux drapeaux que `postesDePause()`
  pose sur les personnes (`fixe`, `fait`) : le gain ne vaut pas ce risque.

**La ligne du jour et celle des pauses prennent les traits latéraux** (le
client, le 10/10/2026, capture de l'iPhone : « mettre les mêmes bordures
pour la ligne des pauses et des jours »). Les lignes de poste du Planning
portent un trait de 3 px à gauche et à droite, à la couleur de leur zone ;
la barre de date et la ligne AM · PM · N n'en avaient pas. Elles prennent
le gris des lignes CM et ADJ (`--bordg`), si bien que le trait court sans
interruption du haut du cadre jusqu'au bas du tableau. **J'avais d'abord
compris de travers** : j'ai foncé le gris des lignes CM et ADJ (v635), ce
que le client ne demandait pas ; c'est annulé. Vérifié à 320 px (hors
ligne), 390 et 1280 px, sans erreur.
Puis, le même jour : « retire juste pour la ligne de date et mets en gris
la ligne des pauses ». La barre de date n'a plus de trait ; celui de la
ligne des pauses passe à un gris moyen (#7C8699), `--bordg` s'y lisant
blanc. Vérifié à 320 px (hors ligne), 390 et 1280 px.

**La ligne des équipes de l'onglet Équipes, comme celle des pauses** (le
client, le 10/10/2026 : « ajouter une bordure aussi pour la ligne des
équipes et la police de la ligne équipe doit être comme la ligne des
pauses »). Dans le tableau « Les équipes » seulement (`.orgeqs`), la ligne
d'en-tête prend le trait gris de 3 px à gauche et à droite, et « Éq. 1 »
à « Éq. 5 » (« Équipe 1 » au bureau) s'écrivent comme AM · PM · N :
13,5 px, graisse 650, sans capitales ; le coin « Poste » garde son
écriture. Au passage, l'exposant d'équipe des deux GBT faisait déborder
leur badge de sa case à 320 px : il est posé dans le coin du badge, qui
garde la largeur des autres. Mesuré à 320 px, 390 et 1280 px : aucun badge
hors de sa case, rien ne défile de côté.

**Dans les listes de choix, « GBT Chaud. » et « GBT Glut. »** (le client,
le 10/10/2026 : « au lieu de mettre GBT et le nom de l'équipe dans les
listes de choix, il faut mettre GBT Chaud. et GBT Glu. »). Les trois listes
de personnes (onglet des réglages, onglet de recherche, écran de connexion) départageaient les
deux GBT par l'identifiant interne (« GBT-1 ») ou la catégorie (« Shift4 »).
`libelleChoix()` les nomme désormais par leur poste attitré, l'abrégé de
`PV_COURT` : « Glut. » et non « Glu. », pour rester l'abrégé qu'on lit
partout ailleurs. Vérifié à 320 px (hors ligne), 390 et 1280 px.
Puis, le même jour : « pareil pour le trigramme, pas besoin du numéro
d'équipe ». L'exposant d'équipe des badges GBT de l'onglet Équipes
(« GBT⁴ », « GBT⁵ ») et son infobulle sont retirés : la ligne du tableau
dit déjà le poste. Le badge redevient « GBT » tout court.

**Le menu dans l'ordre du client** (le 10/10/2026 : « menu dans ce sens :
accueil, horaire, équipes, salaire, rh, recherche ») : Accueil · Planning ·
Équipes · Salaire · Effectifs · Recherche. Le client nomme les onglets à sa
façon (« horaire » pour Planning, « rh » pour Effectifs) ; les intitulés,
choisis avec lui le 09/10, ne changent pas, et les identifiants (`data-v`,
`ui/view`) non plus. `VIEWS` suit l'ordre. Vérifié à 320 px (hors ligne),
390 et 1280 px : chaque onglet s'ouvre, rien ne déborde, aucune erreur.

**Le héros ne se colle plus en haut au retour sur l'Accueil** (le client, le
10/10/2026 : « en changeant d'onglet, quand on revient sur l'accueil, le
héros est collé au-dessus de l'écran et n'a plus l'écart »). `setView()`
appelait encore `centrerSurAujourdhui()`, né pour la vue année (douze mois
sous l'écran) : il amenait la case du jour du calendrier à l'écran. Sur un
téléphone, cette case est sous le bas de l'écran, et la page descendait
d'autant. Reproduit à 390 × 600 : 80 px de défilement après chaque
changement d'onglet ; Chromium à 800 px de haut ne le montrait pas, la case
y tenait à l'écran. La fonction et son appel sont retirés : 0 px, le héros
à 16 px du haut après les cinq onglets. Vérificateur identique ; vérifié à
320 px (hors ligne), 390 et 1280 px.

**Une bulle sur l'onglet Effectifs, plus de rangée de sauts** (le client, le
10/10/2026 : « sur l'onglet rh, il doit y avoir une petite bulle avec le
nombre de jours en sous-effectif ; les badges au-dessus de la page rh ne
sont pas utiles »). Une pastille rouge à chiffre (`#rhNb`) se pose au coin
de l'icône sur téléphone, à côté du libellé au bureau ; elle dit le nombre
de journées en sous-effectif d'aujourd'hui à la fin de l'horaire, le même
que le sous-titre du cadre, et se tait à zéro. `renderManques()` l'écrit ;
il est appelé au repos dès le démarrage (`requestIdleCallback`), si bien
que la bulle est là sans ouvrir l'onglet. Le libellé d'accessibilité de
l'onglet le dit en mots. La rangée « Sous-effectif · Rappels · Absents »
(`.rhsauts`), ses styles et son écouteur sont retirés. Le rouge plein
#D63A30 et non `--at-rouge`, trop pâle en sombre pour un chiffre blanc.
Mesuré à 320 px (hors ligne), 390 et 1280 px : 25, comme le cadre ;
l'onglet commence par le cadre des sous-effectifs ; rien ne déborde.

**En pauses, et non en jours** (le client, le même jour : « indiquer en
description 25 pauses en sous-effectif ; bien parler en pause et non en
jour »). `mqPauses()` compte les pauses distinctes d'une journée de
manque — deux postes vides la même nuit font une pause, un matin et une
nuit en font deux. Le sous-titre dit « 25 pauses en sous-effectif »,
chaque intertitre de mois « 6 pauses », la bulle et son libellé
d'accessibilité comptent pareil. Au 10/10 les deux comptes tombent égaux
(aucune journée n'a deux pauses en manque) : seul le mot change. Même
demande : le nom du mois se centre verticalement dans son intertitre (le
`align-items:baseline` de `#mqCorps .eqsem` le collait en haut) ; la
description sous « Rappels non nécessaires » disparaît ; les cadres
Absents et Congé et repos prennent la première ligne des autres cadres de
l'onglet (`.toolbar.rhtitle` : titre centré, puis « 6 personnes ·
jusqu'au » ou « 40 personnes · reprise »). Vérifié à 320 px (hors ligne),
390 et 1280 px : écart de centrage 0 px, rien ne déborde, aucune erreur.
Puis : « la ligne avec la date doit être foncée comme la ligne des mois
repliable ». L'en-tête de chaque journée (`.mqjt`) prend le fond
`--surface2` de l'intertitre (`.eqsem`), coins hauts arrondis comme la
carte ; mesuré, les deux fonds sont identiques à 320 px (hors ligne), 390
et 1280 px.
Puis : « pour les mois il faut indiquer les pauses en sous-effectif en
rouge, et retirer le 1 personne manquante pour mettre le 0/1 à la place ;
centrer le badge de recherche ». L'intertitre dit « 6 pauses en
sous-effectif » en rouge (`.mqmn`) ; l'en-tête du jour porte l'effectif
« 0/1 » (un par manque, précédé de la pause et du poste, s'il y en a
plusieurs), et le cadre « En poste » des sous-effectifs ne le répète plus
(`cadreEnPoste()` sans compte ; la recherche garde le sien). « Chercher un
remplaçant » est centré, y compris sous 380 px où la fiche a 7 px de marge
à gauche (écart mesuré 0 px à 320 px hors ligne, 390 et 1280 px).

### Le congé en heures

Le client, le 09/10/2026, à la proposition tirée de la note de service du
24/02/2022 (prise de congé par heure en production) : « oui on peut
regarder à cela, ça sera utile pour les opérateurs ». Le module Congé a un
troisième choix de durée, « Heures » (absent des onglets Absence et
Recherche, où il vaut « Un jour ») : une date, une durée de 1 à 7 h, et
« Départ tôt » ou « Arrivée tard ». `caCongeHeures()` applique la note :
- **en période de D**, possible sans remplaçant à indiquer ;
- **plus de 7 jours avant**, un remplaçant est exigé même si l'équipe est
  complète ; **7 jours ou moins**, possible si le poste garde son effectif
  sans la personne, sinon avec un remplaçant ;
- les remplaçants, de la **même fonction** (savoir tenir le poste ; pour
  un poste d'opérateur, pas un cadre — la première version proposait des
  adjoints aux chaudières), **hors de la pause** : la pause voisine qui
  arrive plus tôt ou reste plus tard (en fin de nuit, le matin du
  lendemain ; en début de matin, la nuit de la veille), ceux qui sont en
  repos ce jour-là, ceux qui sont en D (matin et après-midi). Ils viennent
  en FT, n h à leur compteur ; 12 h au plus par journée, et 8 h de repos
  comptées sur leurs heures NOUVELLES (« n écartés » sinon).

Éprouvé : VBN en D le 12/10 (possible sans remplaçant), MMS le 13/10 en N
(possible, l'équipe reste au complet), AFA contremaître le 13/10 (VGG
arrive à 12 h, ATA et JBI en repos, ATR, FLI et VBN en D), GJR le 22/10 en
N (le matin du lendemain arrive à 4 h), LAA le 20/10 en arrivée tardive
(l'après-midi reste jusqu'à minuit, six écartés pour le repos). Sur
téléphone, « Arrivée tard » ne tenait pas dans sa colonne à 320 px : sous
380 px, le moment passe sur sa propre ligne. Vérificateur identique à
l'octet (il ne découpe pas ce module) ; rien ne déborde à 320 (hors
ligne), 390 et 1280 px.

### Les rappels que l'effectif ne demandait pas

Le client, le 30/09/2026 : « un cadre dans le premier onglet reprenant les
erreurs du fichier Excel : un rappel d'un travailleur pour une journée, un
poste où il n'y avait pas besoin, car l'effectif permettait d'avoir une
équipe complète ». Cadre « Rappels non nécessaires », sous les
sous-effectifs, même forme qu'eux (date en mots, coupure par semaine, clic
qui ouvre le tableau du jour).

`rappelsInutiles()` prend chaque rappel du jour de l'usine à la fin de
l'horaire — journée lue en rappel sur un repos (`r.rs`), ou cellule
franche « - » avec une pause tenue, sauf un échange — et rejoue la journée
sans la personne par `caSimuler()`, la simulation du module d'absence :
aucun poste sous son effectif, même après les changements que le
rééquilibrage ferait dans la pause, et le rappel est signalé (« Complet
sans lui », ou « … si HKB Glut. → Meun. »). Le commentaire est dans
l'infobulle. Écartés : un commentaire qui nomme un renfort ou une
intervention (la tâche justifie le rappel, pas l'effectif) et les journées
`SANS_EFFECTIF`.

Mesuré le 30/09/2026 : 178 rappels sur l'année, dont 102 sans trou sans
eux — beaucoup de renforts du SD26 et des journées sans effectif, d'où les
deux exclusions ; **6 à venir** (LHR les 02 et 03/10, YRS les 04 et 11/10,
ADS le 14/10, GKT le 27/10), les deux « intervention gluten » du 05/10
écartées. Ce sont des signalements, pas des corrections : le classeur
n'est pas modifié, et un rappel peut avoir une raison qu'il n'écrit pas.
Vérificateur à zéro ; rien ne déborde à 320 (hors ligne), 390 et 1280 px.
Puis, le même jour : « que rappel ». Seul un commentaire qui écrit le mot
compte ; une présence sur un repos sans lui (« Remplace BLR ») n'est plus
un rappel. Restent **3 à venir** : LHR les 02 et 03/10, YRS le 04/10.

### Le Résumé réordonné, sans « Mon prochain poste »

Le client, le 30/09/2026 : « le cadre congé/absence/recherche doit être
tout en haut ; on peut supprimer le cadre prochain poste ; poste en
sous-effectif et rappel non nécessaire doivent être juste en dessous du
cadre équipe du jour ». L'onglet se lit désormais : Congé, absence et
recherche ; Équipes du jour (le tableau) ; Postes en sous-effectif ;
Rappels non nécessaires ; puis les cadres Absents et Congé et repos, qui
restent sous le tableau dont ils dépendent. « Mon prochain poste » part
en entier : son HTML, `majProchain()` et ses deux appels, `posteLeJour()`
qui ne servait qu'à lui, et les styles `.prochain`, `.pp-txt`,
`.cardjour`. La barre du haut dit déjà le poste du jour. Vérificateur à
zéro ; rien ne déborde à 320 (hors ligne), 390 et 1280 px.

**Une carte par journée, et plus de fond gris.** Le client, le 09/10/2026 :
« pas assez clair entre les différents jours de sous-effectif (il y a
également ce fond gris qui n'est présent que là-bas, que je n'aime pas) ».
Le gris était un défaut : `#mqCorps .mqj,#rnCorps .mqj:hover{…}`, le
`:hover` manquant au premier sélecteur peignait en permanence chaque
journée en `--surface3`. Il ne reste qu'un survol, sur les appareils qui
survolent. Et chaque journée empilait des blocs (en poste, rappels,
prolongation) séparés de filets, de sorte que le filet entre deux jours
ne s'en distinguait pas. Chaque journée est désormais une carte bordée
(`--cadre`, coins de 12 px, 10 px d'écart, 660 px au plus au bureau),
sans fond à elle, avec un en-tête : la date à gauche, « 1 place vide » /
« n places vides » en rouge à droite. Deux manques d'un même jour sont
séparés d'un filet fort. Vérificateur identique à l'octet ; rien ne
déborde à 320 (hors ligne), 390 et 1280 px.

Puis, le même jour, sur sa capture d'iPhone : « 1 personne manquante » /
« n personnes manquantes » au lieu de « place vide » ; la pause en code
(AM, PM, N) et l'équipe en entier (« Équipe 3 ») sur la ligne du poste ;
le nombre de journées du mois à droite de l'intertitre (« Octobre ·
6 journées »), comme le total sous le titre. L'espace sous la date était
plus grand qu'au-dessus : la date gardait la marge basse de 11 px de son
ancienne disposition (`.mqd.eqproche`), annulée dans l'en-tête. Et le
cadre « Congé, absence et recherche » perd sa description (`#caSub`,
« simuler une journée sans quelqu'un », « trouver quelqu'un pour un
poste », et le « VBN · 3 journées » qu'il écrivait après un calcul).

**Les sous-effectifs disent qui est en poste.** Le client, le 30/09/2026 :
« il faut également marquer qui est en poste (même manière que le module
de recherche) ». Chaque manque ouvre sur le cadre plein « En poste » de la
recherche, les présents puis un « ? » par place vide (le 21/10 en N aux
chaudières : GJR puis « ? »), avant les solutions.

**Sur PC, les trigrammes du tableau du jour côte à côte.** Le client, le
30/09/2026 : « sur PC les badges de trigramme doivent être l'un à côté de
l'autre ». Au-delà de 760 px les étiquettes passent en ligne dans leur
case ; sur téléphone elles restent l'une sous l'autre (sa demande du
22/09). Mesuré le 30/09 : 14 paires côte à côte à 1280 px, 14 empilées à
390 px, aucune case qui déborde ; le tableau passe à 485 px au bureau.
Vérificateur à zéro ; vérifié à 320 (hors ligne), 390 et 1280 px.


## Personne n'est choisi par défaut

Le client, le 30/09/2026 : « par défaut, aucun trigramme d'opérateur ni
réglage ne doit être sélectionné, pour ne pas voir le salaire de la
personne en défaut ». Un `<select>` prend sa première option : sur un
appareil neuf, la première fonction et le premier trigramme de la liste
(AFA) étaient choisis d'office, et Mon salaire montrait ses heures, ses
primes et ses rappels. C'est aussi ce qui avait fait hériter LCI des
heures sup d'AFA le 26/09. Les deux listes des Réglages commencent donc
par « — Choisir — » ; seul un choix fait par l'utilisateur
(`ui/prefillCat`, `ui/prefillId`) revient au lancement. Sans personne,
la barre du haut dit « Choisissez qui vous êtes dans Réglages » et le
mois reste vide.

**Les appareils déjà servis gardaient les journées de l'autre** dans
leurs douze mois. `viderAuto()` les retire une fois, quand aucune
personne n'est choisie : seulement les journées posées par le
pré-remplissage (`rec.auto`), jamais une saisie à la main. Éprouvé :
profil neuf, 0 journée sur 30 ; AFA choisi, 25 sur 30, gardé au
rechargement ; choix effacé, 0 sur 30, hors ligne compris ; aucune
erreur. La rémunération fixe d'exemple (`remFixe` de `DEF_P`) n'est pas
touchée : elle n'appartient à personne.

**Et Mon salaire ne montre aucun montant.** Le client, le 30/09/2026,
capture à l'appui : sans personne, l'onglet affichait un « Net estimé »
calculé sur la rémunération d'exemple et zéro journée. `majBrandsub()`,
appelée à chaque rendu, pose `data-sanspers` sur `body` ; la feuille cache
alors tout l'onglet, sélecteur de mois compris, et ne laisse que la carte
`#salVide`, qui renvoie aux Réglages. Vérifié à 320 (hors ligne), 390 et
1280 px, avec et sans VBN.

## La barre d'onglets et un onglet court, en PWA sous iOS

Le client, le 30/09/2026, captures de son iPhone : sur « Mon horaire »
presque vide, la barre d'onglets flottait au-dessus d'une bande noire. Avec
la barre d'état translucide (`black-translucent`, `viewport-fit=cover`),
iOS calcule le bloc des éléments fixes sans la hauteur de la barre d'état
tant que la page ne dépasse pas l'écran. `html` et `body` ont donc une
hauteur minimale égale à l'écran plus `env(safe-area-inset-top)` : une page
courte défile de cette zone, et le cadre fixe `.navwrap` retrouve tout
l'écran. Toujours pas de `dvh`. **Chromium ne reproduit pas le défaut** :
seul l'iPhone du client dit s'il est guéri.

## Le pré-remplissage ne parle que s'il faut agir

Il se rejoue à chaque ouverture, et il fait bouger quelque chose presque à
chaque fois : sa bulle s'affichait donc au démarrage, par-dessus le tableau
de l'équipe, deux secondes et demie durant. Le client, le 22/09/2026 :
« il faut également supprimer la bulle d'info qui apparaît en cas de
chargement ».

Elle ne parle plus **que si l'utilisateur a quelque chose à faire de ses
mains** — une journée que la lecture n'a pas su traduire. Le reste (journées
reprises, heures au compteur HS, rappels proposés, journées à vérifier) est
un compte rendu et non une demande : il part au journal de la console, où il
reste consultable sans rien recouvrir.

Au 22/09/2026 ce cas ne se présente jamais, les neuf règles du vérificateur
étant à zéro. C'est un filet, pas un bavardage.

Les autres bulles répondent toutes à une action de l'utilisateur —
enregistrer, vider, exporter, importer — et restent.

## Régénérer les icônes

Les cinq icônes dérivent toutes de `logo.png`. Elles sont mises en cache à
l'installation de la PWA, d'où la palette indexée : un tiers de poids en
moins pour un écart moyen de 0,2 sur 255, invisible à l'œil.

```python
from PIL import Image
src = Image.open("logo.png").convert("RGB")
fond = src.getpixel((6, 6))

def icone(nom, taille, marge=0.0):
    toile = Image.new("RGB", (taille, taille), fond)
    dedans = int(round(taille * (1 - 2 * marge)))
    toile.paste(src.resize((dedans, dedans), Image.LANCZOS),
                ((taille - dedans) // 2, (taille - dedans) // 2))
    toile.quantize(colors=256, dither=Image.FLOYDSTEINBERG).save(nom, "PNG", optimize=True)

icone("favicon.png", 64);          icone("apple-touch-icon.png", 180)
icone("icon-192.png", 192);        icone("icon-512.png", 512)
icone("icon-maskable-512.png", 512, 0.10)
```

La marge de 10 % de la dernière n'est pas cosmétique : Android rogne l'icône
*maskable* dans un masque, et seuls les 80 % centraux sont garantis visibles.
Sans elle, le mot « biowanze » se ferait couper.

## Les deux versements du mois

Le client, le 22/09/2026 : « pour les employés, il faut ajouter un paramètre
où il peut indiquer le montant de son avance mensuelle, afin de pouvoir voir
les 2 montants qu'il recevra au cours du mois ; la règle pour les employés
c'est l'avance 4 jours ouvrables avant la fin du mois, et le solde 4 jours
ouvrables après la fin du mois ».

**`avanceMens` est un RÉGLAGE, `M.avance` est un fait du mois**, et il ne
faut pas les confondre. Le premier est le montant de l'avance, le même tous
les mois, marqué `personal:true` — il ne quitte jamais l'appareil. Le second,
« Avance déjà reçue », dit ce qui a effectivement été versé ce mois-ci et se
DÉDUIT du net. Le bloc repart donc du TOTAL — `net + avance déjà déduite` —
et le compte tombe juste que la case du mois soit remplie ou non. Vérifié
dans les deux cas : 2 615,64 sans, 1 215,64 avec, et les deux versements
affichés restent les mêmes.

**JOUR OUVRÉ, et non « ouvrable ».** Le mot du client était le second, et
il fallait pourtant le premier. La loi du 12 avril 1965 sur la protection de
la rémunération — celle dont sort le délai de quatre jours — compte en jours
OUVRABLES, **samedi compris** ; cette lecture plaçait quatre dates de 2026
sur un samedi : le 4 avril, le 25 avril, le 4 juillet et le 26 décembre. Le
client, aussitôt : **« jamais payé le wk »**. C'est le fait qui tranche, pas
le vocabulaire — on compte du **lundi au vendredi, jours fériés exclus**.

La fonction s'appelle donc `_ouvre()` et non `_ouvrable()` : les deux mots
ne désignent pas le même ensemble, et un nom qui ment sur un jour de paie se
paie un jour.

On compte À PARTIR du dernier jour du mois **sans le compter lui-même** : on
avance d'un jour avant de regarder s'il est ouvré. Les fériés viennent de
`feries()`, ceux-là mêmes que le calendrier du mois peint, et ils sont relus
quand le comptage change d'année — ce qui arrive tous les décembres.

Contrôlé sur les douze mois de 2026 : **zéro date en week-end, zéro date sur
un jour férié**. C'est l'épreuve à relancer si la règle bouge.

Le bloc ne s'affiche **que si le réglage est renseigné** : celui qui est
payé en une fois ne voit rien de plus qu'avant.

## Six onglets, et ce que chacun porte

Le client, le 22/09/2026 : « l'onglet Équipe doit reconstruire les équipes
(équipes 1 à 5 complètes par poste) et les binômes (adjoint, contremaître),
plus les opérateurs en formation et la station d'épuration ; ce qui est
affiché actuellement dans Équipe doit être affiché dans Résumé afin d'avoir
une vue directe sur la journée ; tout ce qui est lié à la paye doit être
dans un onglet "Mon salaire" ; Horaire doit s'appeler "Mon horaire" et
reprendre le contenu de l'onglet Compteurs ».

| Onglet | Ce qu'il porte |
|---|---|
| **Résumé** | AUJOURD'HUI : prochain poste, postes en manque, qui travaille |
| **Mon horaire** | mon calendrier, et les compteurs à sa suite |
| **Équipe** | la COMPOSITION : équipes 1-5 par poste, binômes, formation, STEP, annuaire |
| **Recyclage** | inchangé |
| **Mon salaire** | le net, les deux versements, la cascade, la fiche, le contrôle |
| **Réglages** | inchangé |

**La ligne de partage est le TEMPS, pas le sujet.** Le Résumé dit
aujourd'hui, l'Équipe ne dépend d'aucune date, Mon horaire et Mon salaire
parlent d'un MOIS — et ce sont les deux seuls à porter le sélecteur de mois.
`placerMnav()` n'a donc plus que deux hôtes.

**`VUES_MIGREES` existe pour que personne ne se réveille au Résumé.**
`ui/view` retient la dernière vue ouverte ; les clés `compteurs`, `fiche` et
`controle` ayant disparu, un appareil qui les avait enregistrées serait
retombé au Résumé sans raison. La table les redirige vers leur nouvel hôte.
Vérifié : `fiche` et `controle` mènent à `salaire`, `compteurs` à `horaire`,
et une clé inconnue au Résumé.

**Les clés internes ne bougent que si elles le doivent** : l'onglet s'appelle
Recyclage mais la vue reste `polyvalence`, pour la même raison. `salaire` est
neuf, donc il n'avait rien à casser.

### La vue d'organisation lit, elle ne calcule pas

`renderOrganisation()` ne rejoue ni le cycle ni les remplacements — elle lit
ce que le classeur écrit à côté de chaque nom. Le classeur range ces quatre
choses de quatre façons différentes, et il faut les prendre comme elles
viennent :

- une personne d'équipe porte `Shift3 → Chaudières` ;
- un cadre porte `Contremaître → 4`, où **4 est son BINÔME et non un poste** ;
  l'adjoint du binôme porte en plus `Shift1 → Adjoints Contremaître` — et ce
  `Shift1` est **l'en-tête de la colonne où il a été lu, pas son équipe**.
  Ne pas le prendre pour telle ;
- un opérateur en formation porte son poste d'apprentissage, parfois avec son
  équipe collée dedans (`chaudières éq. 3`) ;
- la station d'épuration a sa propre catégorie.

**Six binômes, et le 2 n'a pas d'adjoint** — la case le dit par un tiret
cadratin plutôt que de rester blanche.

**L'annuaire reste dans Équipe**, où le client l'a laissé quand la question
lui a été posée. Les quatre cartes au-dessus disent la composition ; lui
garde, sous chaque nom, **ce que le classeur écrit mot pour mot à côté** —
on ne sait pas toujours ce que cela désigne, et le supprimer serait perdre
ce qu'on n'a pas encore compris.

**UNE PLACE, UNE SEULE, ET C'EST CELLE DU RÉSUMÉ.** Le client, le
22/09/2026 : « les opérateurs ne peuvent avoir qu'une seule place dans le
tableau ; il faut regarder comment ils sont placés dans l'onglet Résumé ».

Deux versions ont tenté de répartir les gens d'après leur POLYVALENCE —
d'abord sur toutes leurs lignes, puis sur celles de leur côté d'usine — et
les deux écrivaient le même trigramme jusqu'à six fois. Une composition
d'équipe ne se lit pas comme ça : on demande à ce tableau qui tient quoi, pas
qui pourrait tenir quoi. C'est le Recyclage qui répond à la seconde question,
et il a un onglet pour lui.

> Chaque personne occupe **exactement une** case, celle que `posteAttitre()`
> lui donne — c'est-à-dire `posteTenu(p,[],hJour,null) || posteParDefaut(p)`,
> la chaîne du Résumé sans la date, et la même que « son poste » du Recyclage.

Le Résumé n'a jamais eu ce défaut : `postesDePause()` donne à chacun un poste
et un seul. **La bonne règle était déjà écrite ; elle n'était pas appelée
ici.** Elle range d'elle-même ce que les deux versions tentaient de deviner :
le polyvalent ARRIÈRE va au terrain arrière — « terrain arrière doit
comprendre les opérateurs polyvalent arrière ; s'ils ne sont pas là, les
renforts arrière » —, le polyvalent AVANT au gluten s'il le possède.

Reste l'ORDRE dans la case : celui que le classeur NOMME au poste vient en
tête, le polyvalent que la chaîne y envoie vient après. C'est tout ce que la
ligne des fonctions apporte encore ici.

**Ce que la vue montre alors, et qui est vrai** : la meunerie n'a qu'un ou
deux noms par équipe, le gluten en a trois, la fermentation de l'équipe 4 est
VIDE — le classeur n'y nomme personne, et c'est le polyvalent arrière qui la
couvre depuis le terrain arrière. (Sa colonne Q n'est pas vide pour autant :
c'est sa LIGNE DES NOMS qui l'est. Elle porte une rotation et des congés
jusqu'en décembre — la rotation de la PLACE, restée sans titulaire depuis le
passage de CHD en équipe 5, que le convertisseur annonce sans la lire. Je
l'avais d'abord prise pour une copie de travail de CHD : c'était faux.)

**Une personne que la chaîne ne place pas est NOMMÉE sous le tableau**, elle
ne disparaît pas. Au 22/09/2026 il y en a une : QBY, « Renfort arrière » de
l'équipe 4, dont les polyvalences sont gluten et distillation — pas de
fermentation, donc pas de terrain arrière, et « renfort arrière » ne l'envoie
pas au gluten. Le classeur ne dit pas où il va ; **à faire trancher par le
client** plutôt qu'à deviner.

**QBY est en distillation**, et c'est le client qui le dit — le 22/09/2026,
en réponse au nom qui restait sous le tableau. Le classeur l'écrit « Renfort
arrière » et ne lui donne que gluten et distillation : pas de fermentation,
donc pas de terrain arrière, et rien ne le plaçait. `POSTE_TRANCHE` porte
cette décision, en DERNIER recours de `posteParDefaut()` — après la cellule
et après tout ce que le classeur dit, de sorte qu'elle ne peut rien écraser.
Une table nommée, et non une règle inventée autour de son cas.

Elle déborde volontairement de cette vue, et il faut le savoir : les manques
d'effectif passent de **15 journées / 17 places à 12 / 13** (fermentation de
9 à 5), et « son poste » du Recyclage devient la distillation, si bien que
ses journées là-bas ne comptent plus en recyclage. C'est ce qu'on attend
d'un poste enfin connu.

**La fermentation de l'équipe 4 reste vide, et c'est juste.** Le client, le
22/09/2026 : « PAM possède la polyvalence fermentation, donc logiquement il
peut tenir ce poste s'il y a un manquement ». C'est une COUVERTURE, pas une
affectation : le tableau dit qui tient un poste, le Recyclage dit qui peut
le tenir — PAM y a bien la fermentation — et le module des manques s'en sert
le jour où le trou se présente. L'écrire deux fois dans la composition
casserait la règle d'une place unique.

**Les opérateurs en formation sont DANS le tableau, en dernier et en jaune.**
Le client, le 22/09/2026 : « les opérateurs en formation doivent être sous
les opérateurs qui tiennent le poste et il faut qu'ils soient en jaune ».
Même jaune (`--at-jaune`) et même place que dans le tableau du jour du
Résumé : on ne réapprend pas à lire d'un onglet à l'autre.

**Leur équipe n'est pas dans leur catégorie** — ils n'ont pas de « Shift n » —
mais collée à leur poste : `chaudières éq. 3`. Cinq des huit la portent
ainsi ; pour CDT, NPI et SKS le classeur ne la dit nulle part, et ceux-là
restent seuls dans leur carte, qui s'appelle désormais ce qu'elle contient.
Les cinq autres ont quitté la carte : les montrer deux fois aurait fait
croire à deux personnes.

**Pas de `\b` devant « éq »**, et le motif n'a rien trouvé pendant une
version : en JavaScript sans `/u`, « é » n'est pas un caractère de mot, et
l'espace qui le précède non plus — la limite n'existe donc jamais.

**Le contenu est centré dans les deux sens.** Le client, le 22/09/2026 :
« pour les équipes, il faut centrer le contenu verticalement et
horizontalement ». Les lignes portent de un à quatre noms ; les cases courtes
restaient collées en haut d'une ligne haute. Mesuré : **2 px d'écart au pire**
entre le blanc du haut et celui du bas, à 390 comme à 1280 px.

**SKS et NPI n'ont pas encore d'équipe**, et ce n'est pas une lacune du
classeur : c'est leur situation, dite par le client le 22/09/2026. La carte
porte donc ce titre-là. **CDT est de l'équipe 2**, en formation distillation,
et c'est lui qui le dit également — sa ligne écrit « Distillation » tout
court là où LCI porte « Distillation éq. 5 ». `EQUIPE_TRANCHEE` porte cette
décision, comme `POSTE_TRANCHE` porte celle de QBY.

**Sa rotation colle à 90 % à celle de l'équipe 2 — et on ne s'en sert
pas.** Il faut savoir pourquoi : GST suit celle de l'équipe 4 à 74 % alors
que le classeur le donne à l'équipe 3, et SKS celle de l'équipe 5 à 97 %
alors qu'il n'a pas d'équipe du tout. **Suivre une rotation n'est pas
appartenir à une équipe** ; la déduire aurait donné deux réponses fausses
sur trois.

**L'ENCRE S'INVERSE : les intitulés en clair, les trigrammes en gris.** Le
client, le 22/09/2026 : « je préfère les colonnes principales en blanc et les
trigrammes en gris (inversion avec titre) ». Ce sont les intitulés qu'on
cherche d'abord — de quelle équipe, de quel poste lit-on cette case — et le
contenu se lit ensuite, une fois la case trouvée. Mesuré dans les deux
thèmes : intitulés à **13,7:1** (sombre) et **17,7:1** (clair), trigrammes à
**10,1** et **9,9**, jaune de formation à **7,9** et **5,4**.

**Sur bureau, le nom d'équipe s'écrit en entier.** « Sur PC, les noms
d'équipe peuvent être écrits plus grand et en texte complet » : « Équipe 3 »
au-delà de 760 px, « Éq. 3 » sur un téléphone où la colonne fait 57 px. Les
deux sont écrits et la feuille choisit, par les mêmes `.orgl1` / `.orgl2` que
la colonne des postes — pas d'écouteur de redimensionnement.

**136 px et non 128** pour cette colonne : à 12,5 px « TERRAIN ARRIÈRE »
débordait d'UN pixel. C'est le même piège qu'à 104 px, et il se rouvre à
chaque fois qu'on grossit cet intitulé — mesurer, ne pas estimer.

Contrôlé : **62 trigrammes**, chacun écrit une fois et une seule — les 56
personnes d'équipe et les 6 opérateurs en formation rattachés à une équipe. Personne sous le tableau, aucun débordement à 390, 1280 clair
et 1280 sombre.

### Un poste qui change à une date

Le client, le 25/09/2026 : « pour LCI, il est bien en fermentation dans
l'équipe 5 jusqu'au 29/09 inclus ». La table le montrait en distillation.

**Les deux ne se contredisent pas.** La ligne 9 du classeur écrit
« Distillation éq. 5 » sur sa ligne, mais sa POLYVALENCE déclarée est la
fermentation — c'est-à-dire le poste qu'il TIENT, la distillation étant
celui où il se FORME. Le classeur nomme le second ; le client dit que le
premier vaut jusqu'au 29/09. Vérifié : **aucune de ses 365 cellules ne nomme
un atelier avant le 15/10**, et le classeur ne dit nulle part ce qui change
ce jour-là. La date ne peut venir que de lui.

`POSTE_PERIODE` porte cette décision. **La ligne 9 en est ÉCRASÉE, et c'est
l'inverse de `POSTE_TRANCHE`** : celle-ci vient en DERNIER recours, après
tout ce que le classeur dit, pour ne rien pouvoir effacer ; celle-là vient
en PREMIER, parce qu'elle corrige justement ce que le classeur écrit. Deux
tables, deux places, et le nom doit les distinguer.

**La borne porte l'ANNÉE et pas seulement le jour.** Un appareil ouvert en
2027 comparerait « 0929 » à son propre septembre et rejouerait une
correction qui ne vaut que pour 2026. Passé la date, la ligne 9 reprend la
main d'elle-même — il n'y a rien à retirer d'ici le jour venu.

**Le poste de la période est TENU, pas appris**, et la première version
s'est trompée de moitié. Posée dans `_posteDeLigne9()`, la correction
passait aussi par `posteDeFormation()` : LCI devenait un opérateur en
formation à la fermentation — jaune dans la composition, pastille « F » dans
le Recyclage. Exactement l'inverse de ce que dit le classeur. Elle se pose
donc dans `posteAttitre()`, et là seulement.

**Et les deux coexistent, ce qui n'était jamais arrivé.** `posteAttitre()`
et `posteDeFormation()` étaient exclusives à dessein — « le MÊME calcul,
seule la personne décide lequel des deux il devient ». LCI est le premier à
tenir un poste ET à se former à un autre. Les couper toutes deux l'a fait
**disparaître de la grille de Recyclage** : sa seule polyvalence étant
devenue son poste, il ne lui restait rien à montrer, et le « F » de la
distillation partait avec. Le rendu les lisait déjà séparément — `sien`
s'exclut, `posteForm` porte le F — et sa ligne dit maintenant les deux
vérités : **● à la fermentation, F à la distillation**.

**LE JAUNE SUIT LE POSTE, PAS LA CATÉGORIE.** Il veut dire « présent, mais
pas encore validé ICI », et c'est le poste montré qui le décide. LCI est
bien un opérateur en formation, mais à la fermentation il est validé.
`renderOrganisation()` lit donc `posteAttitre()` plutôt que `enFormation()`
pour choisir le seau.

Mesuré aux quatre dates, horloge déplacée : le 25/09 et le 29/09 il est à la
fermentation et en gris ; le 30/09 il repasse en distillation et en jaune ;
le 25/09/**2027** aussi — la correction ne fuit pas sur l'année suivante.

**62 trigrammes**, chacun une fois, 5 en jaune, personne sous le tableau. Le
Résumé le place déjà en fermentation ce jour-là : les deux vues sont
d'accord, comme le veut « une place, une seule, et c'est celle du Résumé ».
Manques inchangés à 14 journées, neuf règles à zéro, compteurs 76/77.

**ET LA CHAÎNE DU JOUR NE LA VOYAIT PAS.** Le client, le 25/09/2026 :
« chez moi il manque toujours LCI demain par exemple ». Sa capture montrait
la fermentation à **0/1** le 26/09 et LCI rangé en distillation — parce que
la correction n'était posée que dans `posteAttitre()`, que seule la
COMPOSITION emploie. Le tableau du JOUR passe par `posteTenu()`, où
`posteLigne9()` rendait « dist » bien avant qu'on arrive à sa polyvalence.
**Une correction qui ne vaut que pour une vue est pire qu'aucune** : les
deux se contredisent, et c'est celle du jour qu'on regarde le matin.

Elle se pose donc dans `posteTenu()`, **après la cellule et avant tout le
reste** : la cellule écrit ce qui a été presté CE jour-là, la tranche ne dit
que le poste habituel de la période. C'est la règle de tête du projet.

**Et elle lit LE JOUR CALCULÉ, pas l'horloge.** La première version
appelait toujours `new Date()` : tant qu'on était avant le 29/09, elle
plaçait LCI à la fermentation sur TOUTE l'année — novembre compris — et le
module des manques annonçait un effectif qui n'existerait pas.
`postesDePause()` a le jour et l'année sous la main et les passe ; la
composition, qui n'a pas de date, se lit sur aujourd'hui, ce qui est
exactement ce qu'elle montre.

Vérifié jour par jour : fermentation du 25 au 29/09, distillation les 30/09
et 1er/10, repos le 2/10.

**Le poste de FORMATION se lit alors directement sur la ligne 9.** Pendant
une tranche, la chaîne complète rend le poste TENU — c'est tout son objet —
et `posteDeFormation()` y aurait pris la fermentation, posant le « F » du
Recyclage sur le poste qu'il tient.

**Les manques passent de 14 à 12 journées** : LCI comble les trous de
fermentation des 26 et 27/09. Et il faut savoir ce que cela déplace ailleurs
— **le recyclage fermentation de SKS tombe de 10/10 à 2/10**. Ce n'est pas
une régression : ces compteurs comptent les journées où la chaîne PLACE
quelqu'un à un poste, et le rééquilibrage n'envoie plus SKS combler une
fermentation déjà tenue.

**La découpe du vérificateur a cassé au passage** : `posteAttitre()` et
`posteDeFormation()` tenaient chacune sur UNE ligne et se découpaient
jusqu'au premier saut de ligne. Passées à trois lignes, la découpe rendait
une fonction coupée en deux — `SyntaxError` au chargement. Elles se ferment
sur `\n}` comme les autres, et `POSTE_PERIODE` est entrée dans la liste de
découpe, comme `POSTE_TRANCHE` avant elle.

### Les cadres de l'onglet Équipe

« Il faut mieux optimiser les cadres de l'onglet Équipe. » Deux gâchis, tous
deux mesurés :

- **la colonne des postes prenait 104 px sur 356 à 390 px** — 29 % de la
  largeur pour un intitulé. Elle porte les DEUX libellés, et la feuille
  choisit : le court (`PV_COURT`, celui du Recyclage) sur téléphone,
  l'entier au-delà de 760 px où la place ne manque pas. Les faire dépendre
  du script aurait demandé un écouteur de redimensionnement ; écrire les
  deux coûte quelques octets. **76 px sur téléphone, 128 sur bureau** — 128
  et non 104, « TERRAIN ARRIÈRE » se faisant couper d'un cheveu ;
- **les cartes se touchaient** : « les différents cadres sont trop collés ».
  Elles vivent toutes dans `#orgCorps`, et `.stack` ne pose son écart
  qu'entre ses enfants DIRECTS — le conteneur en était un, les cartes non.
  Il reprend le même écart, et le même que partout ailleurs : une valeur de
  plus ici aurait fait un onglet qui ne respire pas comme les autres ;
- **les binômes coûtaient 222 px pour six lignes** de deux trigrammes, et
  leur tableau s'étirait à 1146 px sur un écran de bureau pour un contenu
  qui en demande quarante. Six **tuiles** remplacent le tableau : **115 px
  sur téléphone, 61 sur bureau**.

Le panneau passe de **1 296 à 1 189 px** à 390 px, et de 1 278 à **1 082** à
1 280 px.

**`white-space:nowrap` sur les onglets sous 375 px**, et c'est le mot qui
compte : « Mon horaire » et « Mon salaire » sont les deux intitulés en DEUX
mots, et à 320 px ils passaient à la ligne — la barre montait de 59 à 74 px,
quinze pixels pris au tableau sans que personne les ait demandés. Sur une
seule ligne, à 9,5 px et sans marge latérale, les six tiennent : mesuré,
rien n'est tronqué à 320 px.

Vérifié aux trois largeurs et hors ligne : chaque onglet porte du contenu,
pas un cadre vide — prochain poste, manques, tableau du jour, calendrier,
compteurs, 14 lignes d'organisation, 77 d'annuaire, 38 de recyclage, le net,
la cascade et les tuiles.

## Les intérimaires : une liste qu'aucun fichier ne porte

Dix personnes au 26/09/2026. **J'ai écrit ici que le classeur ne les
distingue nulle part, et c'était faux** : la colonne A de « Polyvalence »
porte « interim » pour eux — l'audit du 26/09/2026 l'a trouvé, et le
convertisseur le garde dans `poly.statut`. La liste du client (22/09)
ajoutait MGY, le classeur ajoute NPE ; le client, le 26/09/2026 : **les deux
sont employés depuis août**. `poly.statut` retarde donc sur une embauche.
Le détail est dans `docs/regles-paie.md`, section « Les intérimaires ».

**Les nouveaux commencent toujours intérimaires** (le client, le
09/10/2026, devant SLI affiché « Ouvrier ») : un opérateur sans ligne dans
« Polyvalence » s'affiche « Intérimaire » — ce sont exactement les quatre
arrivés en cours d'année. Voir `docs/regles-paie.md`, « Les intérimaires ».

**Rien n'est codé, et c'est voulu.** Le client : « rien pour l'instant, mais
garder l'info ». Une liste codée sans emploi égarerait celui qui la relit.

Elle servira quand une fiche de paie d'OUVRIER arrivera : « il ne faudra pas
calculer les intérimaires de la même manière (pareil pour les primes et
jours de paye) ». Trois règles, aucune encore connue — elles touchent à des
montants, donc **ne rien deviner**.

## Mettre à jour une valeur commune à l'équipe

Primes de pause, chèque-repas, coefficients de la procédure de rappel,
barèmes ONSS et impôt : ces valeurs sont les mêmes pour tout le monde. Elles
ne sont **pas modifiables dans l'application** — elles s'y affichent sous un
cadenas — et elles vivent dans `DEF_P` et `DEF_B`, en tête du script de
`index.html`.

Pour en changer une : corriger la valeur dans `DEF_P` / `DEF_B`, incrémenter
`V` dans `sw.js`, pousser. **Rien d'autre à faire côté utilisateur** : au
démarrage, `reprendreFigees()` reprend du code toutes les clés marquées
`fige:true` et écrase celle qui dormait sur l'appareil. Sans ce mécanisme, un
téléphone ayant déjà enregistré l'ancienne prime aurait continué de calculer
avec, sans que rien ne le dise.

Un champ est figé par `fige:true` dans `PARAM_FIELDS`, `RAPPEL_FIELDS` ou
`BAREME_FIELDS`. Y ajouter une clé la verrouille et la fait reprendre ; l'en
retirer la rend à l'utilisateur. Trois exceptions restent à lui :
`calage` (que l'onglet Contrôle recalcule sur sa propre fiche), tout ce qui
est marqué `personal:true`, et les montants du mois.

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
  ici, et rien pour la faire respecter. Voir ci-dessous : il en a un.

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

## Après avoir modifié `index.html`

1. Vérifier la syntaxe : extraire le contenu des balises `<script>` et lancer
   `node --check`.
2. **Incrémenter `V` dans `sw.js`** (`nfdm-vNN`). Sans ça, les installations
   existantes gardent l'ancienne page indéfiniment.

   Depuis `nfdm-v119`, la PAGE se prend **au réseau d'abord** : une version
   poussée arrive au premier rechargement, et non au deuxième comme avant.
   L'horaire JSON reste au cache d'abord, rafraîchi en arrière-plan ; icônes
   et polices, au cache. Hors ligne, tout retombe sur le cache — vérifié à
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
3. Tester dans un navigateur, pas seulement en unitaire. Playwright et
   Chromium sont disponibles ; servir le dossier (`npx http-server`) puis
   piloter la page. Le script étant dans une IIFE, rien n'est accessible
   depuis `page.evaluate` : il faut passer par l'interface.

## Vérifier le calendrier de tout le monde

```bash
node tools/verifier-calendrier.js
```

Confronte ce que le calendrier **affiche** à ce que le classeur **dit**, pour
les 77 personnes et les 27 574 journées. Il ne réimplémente rien : il découpe
dans `index.html` les fonctions de lecture elles-mêmes et les rejoue — ce
qu'il mesure est donc bien ce que l'application fera.

Il découpe par `indexOf`, donc **il s'arrête si un nom est déclaré deux fois**
dans `index.html` : la seconde déclaration écrase la première à l'exécution,
alors que la découpe rejouerait la première — et l'outil annoncerait neuf
règles vertes sur du code que le navigateur n'exécute plus. C'est arrivé avec
`posteDuRemplace`.

Neuf règles, et aucune n'a le droit d'être enfreinte :

| Règle | Ce qu'elle interdit |
|---|---|
| cellule non reconnue | le classeur écrit quelque chose que la lecture ne sait pas traduire |
| poste prévu effacé | `["N","-"]` affiché comme un repos ordinaire |
| poste sans heure | une case peinte en poste sans heure prestée |
| heure sans poste | des heures prestées sans poste à montrer |
| repos habillé | un repos affiché en poste ou en absence |
| absence sans code | une journée non prestée sans rien qui le dise |
| étiquette vide / trop longue | une case muette, ou un code coupé |
| **vues en désaccord** | le mois et l'année divergents sur la même journée |

La dernière est la plus importante : le mois lit une journée **enregistrée**
par le pré-remplissage, l'année **relit le classeur**. Deux chemins pour une
même journée — et c'est ainsi qu'une divergence est passée. Ils partagent
maintenant `lireJournee()` ; le vérificateur refait le trajet complet
(lecture → écriture du mois → relecture) et exige le même résultat.

Le code de retour est 1 s'il reste une faute **dans les neuf règles
dures** : l'outil se branche tel quel sur un contrôle automatique. Il
additionnait jusqu'au 26/09/2026 les règles faibles — des questions à
trancher, jamais à zéro — et sortait donc en 1 sur des données saines ; un
contrôle qui échoue toujours ne se lit plus. `--strict` rend l'ancien
comportement.

Pour demander à l'outil ce que l'application fait d'une journée précise —
plutôt que d'écrire un script à côté, qui réimplémenterait la lecture et
pourrait donc se tromper d'accord avec lui-même :

```bash
node tools/verifier-calendrier.js --journee FPA 0919 0921
```

**Au 22/09/2026 : les neuf règles sont à ZÉRO sur les 27 462 journées.**
La dernière cellule non reconnue était `CAN 24/07 ["*"]` — une faute de
frappe pour un tiret, tranchée par le client le 22/09/2026 et rangée dans
`ALIAS_HORAIRE`. Le classeur est désormais lu sans une exception.

Une cellule se juge sur ce que l'APPLICATION y lit, pas sur ce que le
classeur y écrit : la règle applique `ALIAS_HORAIRE` avant de conclure, et
suivra donc toute addition future sans qu'on y pense.

Une dixième règle, plus faible, liste les **mentions non comprises** : la
case s'affiche juste, mais un morceau de la cellule reste illisible. **19
journées**, regroupées par mention — `HS`, `eval`, `CPPT-F`, et d'autres,
aucune au-delà de deux journées. Elles n'empêchent rien d'afficher, mais elles
pourraient déplacer des heures : à faire trancher, une par une.

### L'onglet Équipe n'a plus qu'une vue

Le client, le 22/09/2026 : « supprime la vue par pause de l'onglet équipe ».
Elles étaient deux, sous une bascule « Par poste / Par pause » : les postes
en lignes et les trois pauses en colonnes d'un côté, les quatre pauses en
lignes et les huit postes en colonnes de l'autre.

**C'est la vue par POSTE qui reste** — huit postes en lignes tiennent
l'écran là où huit postes en colonnes le débordent, et c'est elle qui a reçu
toutes les corrections du 22/09 : les trigrammes empilés, « à déterminer »
sous la ligne STEP, les légendes réduites à ce qui est dessiné. La vue par
pause ne les avait suivies sur aucun point — ses trigrammes se lisaient
encore en ligne, séparés d'un point médian.

Sont partis avec elle : la bascule `#eqVue`, la variable `eqVue` et son
écouteur, la clé `ui/eqVue`, les 39 règles `.eqg2` et les 88 lignes de rendu.
`postesDePause()` **reste** — c'est elle que la vue restante, le module des
manques, la polyvalence et le poste du jour de la barre du haut rejouent
tous.

Un appareil qui avait choisi « Par pause » ouvre désormais la vue par poste
sans rien dire : la clé oubliée n'est plus lue. Vérifié.

**Les trigrammes s'empilent, un par ligne.** Le client le demandait le
21/09/2026, une passe d'optimisation les avait remis en ligne pour gagner de
la largeur, et il l'a redemandé le 22 : « les trigrammes doivent être l'un
en dessous de l'autre (donc la ligne plus haute) ». Le souci de largeur se
règle autrement — une pause n'a plus besoin que de la largeur d'UN nom, et
les pixels reviennent à l'intitulé de poste, qui retrouve ses 122 px et son
corps lisible.

Un piège au passage, et il tenait à UN pixel : la colonne d'une pause offre
62 px de contenu à 390 px de large, et « Après-midi » en demande 63 — le mot
se coupait en deux. Le remplissage de l'en-tête en prenait seize à lui seul ;
on lui en rend huit, plutôt que de réduire le corps de ce qu'on lit en
premier. À 360 px il faut en plus un demi-point de moins.

**L'opérateur « à déterminer » est dans le tableau, pas à côté.** Le client,
le 22/09/2026 : « l'opérateur à déterminer doit être affiché sous la ligne
STEP dans sa pause ». Il se lisait dans la carte « Hors poste », loin du
tableau — donc loin de la question qu'il pose. Il en occupe désormais la
dernière ligne, sans couleur d'atelier : n'ayant pas de poste, il n'a pas de
zone. Il a quitté la carte du même coup ; l'y laisser l'aurait montré deux
fois.

Le tiret cadratin « — » dit « personne » ; le tiret court « – » dit « ce
poste n'attend personne à cette pause ». Les deux ne veulent pas dire la
même chose, et la ligne « à déterminer » emploie le premier.

**L'opérateur en formation s'écrit en DERNIER de la case.** Le client, le
22/09/2026 : il est présent, mais il n'y est pas encore validé — le lire
après ceux qui tiennent le poste évite de compter sur lui d'un coup d'œil.
La partition se fait dans `postesDePause()`, donc les deux vues et le
vérificateur la partagent.

Elle est **stable**, et c'est tout l'enjeu : l'ordre établi plus haut —
titulaires avant renforts, contremaîtres avant adjoints — ne doit pas se
défaire. Un tri par comparaison le mélangerait ; deux seaux recollés le
gardent intact. L'ordre seul change : `tenu`, `attendu` et les drapeaux
restent ce qu'ils étaient — vérifié, les manques sont toujours à 12 journées
et 14 places.

**Les légendes ne montrent que ce qui est à l'écran.** Le client, le
22/09/2026 : « ne laisser que les légendes utiles ». Une légende qui explique
un signe absent est du bruit — la plupart des jours il n'y a ni opérateur en
formation ni poste sous son effectif, et les deux entrées s'affichaient
quand même. Le rendu note ce qu'il a réellement dessiné (`aForm`, `aManque`,
`aVide`, `zVues`) et n'explique que cela ; les zones se rangent dans l'ordre
où le tableau les montre, celui de la production.

Vérifié en avançant jour par jour : sans formation ni manque, une seule
ligne ; trois opérateurs en formation, l'entrée revient ; un poste sous son
effectif, la sienne aussi.

**Une journée a deux postes depuis le 21/09/2026** : `r.s` porte la prime
PAYÉE, `r.sp` le poste PRESTÉ quand ils diffèrent — 275 journées où le
commentaire nomme une prime à conserver, plus les journées `SD26` et `D-F`.
Pour afficher, `postePeint(rec)` et `gardePrime(rec)` ; jamais `rec.s` seul.
Voir `docs/regles-paie.md`, « La prime conservée ».

`RHS`, `RTT-` et `E. min` en sont sortis : le client les a tranchés le
20/09/2026 — voir `docs/regles-paie.md`.

Une **onzième règle**, plus faible elle aussi, dit ce que le motif des
ateliers **avale sans en faire un poste**. C'est le pire angle mort : non pas
ce que l'outil déclare ne pas savoir lire, mais ce qu'il **croit avoir lu**.
`ATELIERS` commence par `^(…|poly|…)`, si bien que « Poly. Etoh » y
correspondait par son premier mot — reconnu, donc absent des mentions non
comprises, et traduit en aucun poste. **46 journées** ont passé ainsi,
invisibles aux dix autres règles, jusqu'à ce que le client le signale.

Il en reste **5** : `consign.` (3), `Polyvalence` et `polyvalence` (1 chacune).

Une **douzième règle**, la plus utile des trois faibles, confronte les motifs
de l'application à une version délibérément **plus large** d'eux-mêmes, et dit
ce que la seconde trouverait de plus. Deux défauts du 21/09/2026 venaient d'un
motif trop étroit, et rien ne pouvait les voir : un motif qui lit moins qu'il
ne croit ne ment pas — il se tait.

Elle a trouvé, le jour même de sa naissance : `plageCommentaire()` exigeait un
espace après « à », donc `de 14h à18h00'` lui échappait — **38 journées**, et
la plage décide si les heures épargnées sont DANS le poste ou à côté. Et
`atelierDuRemplace()` ignorait « rempl SBZ » abrégé.

Elle découpe les motifs dans `index.html` plutôt que de les recopier : sa
première version les recopiait, et elle a continué d'annoncer 38 manques après
que `index.html` eut été corrigé. **Une règle qui dénonce les copies ne peut
pas en être une.**

Elle a trouvé une seconde fois, le 22/09/2026 : `plageMention()` refusait
l'apostrophe des minutes — `11h-15h30'` — alors que `normPlage()` la
retirait depuis toujours. Deux motifs, deux sévérités sur la même
notation ; AFA le 10/02 s'affichait en absence à zéro heure alors qu'il
était au travail.

Il reste **46 écarts**, et ce sont des questions, pas des fautes : `10h-11h`
écrit avec un tiret, `00h à 6h` sans « de », des passifs mal orthographiés
comme « Remplacé pa VBN ».

## Vérifier une modification du pré-remplissage

`tools/verifier-calendrier.js` fait ce contrôle et le rend chiffré — c'est
lui qu'il faut relancer, et non un script à côté. Au 22/09/2026, sur les
27 462 journées : **14 648 prestées, 5 082 absences, 157 postes prévus non
prestés, 7 575 repos** (classeur du 22/09/2026 à 15 h 46). Un écart important
signale une régression — mais un nouveau classeur en déplace légitimement :
celui-ci fait passer CHD de Shift 4 à Shift 5, ce qui rebat 88 de ses
journées.

Ces nombres ne se comparent pas aux anciens repères de la section 11 de
`docs/conversion-horaire.md`, qui comptaient autre chose : ils mesuraient la
sortie brute de `parseHoraireEntry`, alors que ceux-ci mesurent ce que la
case AFFICHE, une fois le cycle, le remplacement et l'annotation « - »
appliqués.

### L'onglet « Recyclage »

Le client, le 22/09/2026 : « les polyvalences doivent être affichées dans un
onglet à part », puis « l'onglet polyvalence doit s'appeler Recyclage ». Elles vivaient sous chaque personne de l'annuaire, en
jetons ; à l'étroit dans une carte de 148 px, on ne pouvait ni comparer deux
personnes ni chercher qui peut tenir un poste.

Un onglet donne la largeur d'une **grille** : les gens en lignes, les postes
en colonnes. On y lit dans les deux sens. Le point plein marque SON poste —
il ne compte pas, et le dire évite de prendre une case vide pour une lacune.
Le point maigre dit « jamais tenu une journée complète » : un zéro se lirait
comme un résultat, un point comme une absence de résultat.

La colonne des trigrammes et la ligne d'en-tête restent collées au bord
quand la grille défile ; sans elles on ne sait plus de qui ni de quoi on lit
la case.

**Le titre et la période vivent HORS du cadre.** Le client, le 22/09/2026 :
« il faut le titre "Recyclage des polyvalences" au dessus du cadre avec
juste en dessous la ligne avec les dates (donc les sortir du tableau) ». Ils
annoncent la grille, ils n'en font pas partie — et une fois dehors, la
grille commence par sa propre ligne d'en-tête au lieu d'un bandeau qui lui
ressemblait. Le bloc s'appelle `.pvtete` : hors du cadre, il ne peut pas
emprunter la mise en forme de `.card>header`.

**Un filet gris au-dessus de « Qui »**, de la même épaisseur que les filets
d'atelier des autres colonnes — « pour avoir comme les autres colonnes ».
Sans lui la ligne d'en-tête commençait par un creux de trois pixels.

**TROIS entrées de légende, et pas une de plus** : « le point doit être
"Poste actuel", le petit point "Poste non acquis", F "En formation" ; les
autres légendes ne sont pas nécessaires dans ce tableau ». Ne restent que
les trois SIGNES, ceux qu'on ne peut pas deviner. Le vert d'un quota atteint
et le « 0/X » se lisent tout seuls — le chiffre y est écrit — et une légende
qui répète ce que la case dit déjà est du bruit. `.lg-pvok` et `.lg-pvnul`
sont partis avec elles.

**L'identifiant interne reste `polyvalence`** — la vue, la clé `ui/view`,
`calculerPolyvalence()`, `POLY_QUOTA`. Seul l'INTITULÉ change : ce que la
grille montre, c'est bien le recyclage DES polyvalences, et renommer la clé
aurait renvoyé au Résumé tous les appareils qui avaient l'onglet ouvert.

**Huit onglets** : « Polyvalence » était le plus long et la barre débordait
de 44 px à 320 et de 4 px à 360 ; d'où un demi-point de moins et deux pixels
de moins de chaque côté sous 375 px. **« Recyclage » a réglé le problème
qu'elle traitait** — mesuré : plus rien n'est tronqué à 10,5 px, même à
320 px. La règle est gardée pour ce qu'elle rapporte encore, **3 px de
hauteur de barre** (46 contre 49), et non plus pour faire rentrer les
intitulés. Le relire ici avant de rallonger un onglet.

Elle se pose APRÈS celle qui définit la barre mobile : à spécificité égale
c'est la dernière qui gagne, et une première tentative posée trois cents
lignes plus haut n'avait rien changé du tout.

### Le jour et son tableau ne font qu'un cadre

Le client, le 23/09/2026 : « supprimer la zone "comment lire ce tableau" et
lier le cadre avec la sélection de jour au cadre qui reprend les trois
pauses ».

C'étaient **deux cadres pour une seule chose** : on choisit une journée POUR
lire ce tableau-là. La barre de navigation et son contenu ne se séparent pas
— entre les deux il y avait une bordure, une ombre et seize pixels de vide.

**Deux hôtes et non un**, et c'est le point : `#eqCorps` rend le tableau des
pauses DANS le cadre du jour, et `#eqReste` rend « Hors poste » juste en
dessous, dans le sien. Un cadre dans un cadre ne se lit pas, et « Hors
poste » parle d'autre chose — de ceux qui ne tiennent aucun poste.

Le tableau a donc perdu son `.card` : il EST le contenu du cadre, posé sous
la barre qui le pilote. Mesuré : **0 px** entre le bas de la barre et le haut
du tableau, à 390 comme à 1280 px.

**Le repli « Comment lire ce tableau » est parti avec sa phrase.** Elle
décrivait ce qu'on voit — une ligne par poste, trois pauses en colonnes — et
le tableau le montre mieux qu'elle ne le disait. Les trois règles `.eqaide`
sont parties aussi : un style qui ne sert plus égare celui qui le relit.

### Ce qu'on a presté, jamais ce qu'on a touché

Le client, le 22/09/2026 : « FLN est en formation en D et non en PM ; il est
remplacé en PM, si tu regardes dans les commentaires ». Sa cellule du 23/09
dit `["PM","F","Formation Excel IFAPME remplacé par ALZ GKT"]` — PM est la
prime conservée, `F` dit que la journée s'est faite en horaire de jour, et
deux collègues tiennent son poste d'après-midi. Le montrer en PM le comptait
deux fois.

**Deux champs disent la même chose selon la source** : `r.sp` quand le
COMMENTAIRE nomme une prime à conserver, `r.jourCode` quand la MENTION
elle-même est l'une des huit de `JOUR_PRIME_PAUSE` — `SD26`, `F`, `D-F`,
`DS`, `CPPT`, `DS-CE`, `TP`. Le calendrier lisait déjà les deux, par
`postePeint()` ; `equipeDuJour()` n'en lisait qu'un, et rangeait ces
journées-là dans la pause PAYÉE.

`var pv=r.sp||((r.jourCode && !surSonPosteMalgreF(raw))?"D":r.s);` — la garde
est la même que celle de `postesDePause()` deux fonctions plus bas : sur les
22 journées de projet, le `F` ne sort pas du poste.

Les manques passent de **12 journées / 13 places à 14 / 16**, et c'est le
sens de la correction : quelqu'un parti en formation n'est plus à son poste,
et le trou qu'il laisse était invisible. Les neuf règles restent à zéro, les
compteurs à 76/77.

**`--journee` imprime désormais la prime, le poste presté et le code de
jour.** Sans ces trois champs à l'écran, rien ne disait POURQUOI quelqu'un
apparaît dans une pause plutôt qu'une autre — il a fallu les ajouter pour
voir le défaut.

### L'onglet « Mon horaire » n'a plus qu'une vue

Le client, le 23/09/2026 : « dans l'onglet Horaire il ne faut avoir que la
vue année par défaut, et toujours scroller jusqu'à la date du jour », puis
« je ne veux plus les autres boutons ; il faut donc supprimer la sélection
de mois qui était au-dessus du cadre et y ajouter un titre "Mon horaire"
comme pour Équipe ».

**La vue SEMAINE est morte** — 90 lignes de rendu, 35 règles de feuille,
`lundiDe()` et `lundiCourant`. `JOURS_LONGS` reste : la barre du haut écrit
« Mardi 22 septembre » avec, et elle ne lui appartenait pas.

**Le MOIS n'est plus une vue, c'est le détail d'une journée.** On l'ouvre en
cliquant une case de l'année — c'est là qu'on corrige — et un bouton
« ‹ Retour à l'année » ramène. Sans lui, la seule sortie aurait été de
changer d'onglet : **supprimer un aller sans laisser de retour aurait rendu
la correction d'une journée inaccessible.** `vueHoraire()` n'a donc plus
que deux états, et la bascule ne s'enregistre plus : on revient toujours sur
l'année.

**Le clic sur une journée visait un sélecteur mort.** `.day[data-d]` est une
disposition en liste qui n'existe plus ; le mois s'ouvrait sur son premier
jour. Cela comptait peu tant qu'un bouton « Mois » existait — c'est
maintenant le SEUL chemin. Il vise `.mc-j[data-d]` et ouvre la feuille du
jour, ce pour quoi on a cliqué.

Le titre vit **hors du cadre**, comme celui d'Équipe : `.pvtete`, « Mon
horaire » et « VBN · 2026 » dessous. Et « Septembre 2026 » disparaît de
l'en-tête du cadre tant qu'on lit l'année : il décrit le mois qu'on corrige,
pas l'année qu'on regarde.

**`centrerSurAujourdhui()` est appelée de DEUX endroits, et il en faut
deux** : à la fin de `renderAnnee()`, pour le changement de personne, et
dans `setView()` à l'ouverture de l'onglet — car la vue est déjà dessinée
quand on y revient, et `setView()` remet la page en haut APRÈS coup. Le
premier essai n'appelait que le premier des deux, et la page restait sur
janvier.

Sans animation : un glissement se battrait avec le repli de la barre du
haut, qui écoute le défilement. Et rien ne bouge si le panneau est caché.

Mesuré : la case du jour est **au milieu de l'écran** à 390 comme à 1280 px
(2 661 px et 571 px de défilement), et « Mois » choisi à la main revient
bien après un rechargement.

### « N ? » — le poste prévu que rien ne confirme

Le client, le 23/09/2026, sur LHR les 2 et 3 octobre : « c'est N avec ? car
ce n'est pas encore confirmé si nécessaire ou si l'opérateur a accepté ».

Sa cellule dit `["-","N?","Echange avec JKS SPT présent?"]` : la rotation le
met en repos, et on lui demande peut-être deux nuits en échange avec un
collègue. Le « ? » rendait la mention illisible, le poste retombait sur le
repos, et **deux nuits disparaissaient avec leurs primes** — le pire des deux
résultats possibles, puisque le classeur dit au moins qu'il s'agit d'une
nuit.

L'étiquette devient **« N ? »**, qui tient dans les quatre signes, et la
journée part au compteur des journées à vérifier.

**LE DOUTE NE VAUT QUE S'IL PORTE SUR LE POSTE**, et une première version
s'est trompée de cible. Quatre cellules de l'année finissent par un point
d'interrogation, et deux le mettent sur l'ATELIER : `["N","Poly. Arr.?"]` et
`["AM","gluten?"]` — là le poste est écrit noir sur blanc dans la cellule
franche et ne fait aucun doute. Elles s'affichaient « N ? » et « AM ? »,
c'est-à-dire qu'elles faisaient douter de la mauvaise chose. Le `?` n'est
retenu que si le texte qui reste EST un poste ou une plage.

Le point d'interrogation du COMMENTAIRE — « SPT présent? » — ne compte pas :
seule l'annotation porte le poste.

**Le vérificateur garde sa PROPRE copie de l'écriture du mois** (`enregistre()`),
et elle s'est désynchronisée immédiatement : l'année écrivait « N ? », le
mois « N », et la règle « vues en désaccord » est montée à 4. C'est le piège
déjà rencontré — **deux copies, et c'est toujours la seconde qui reste en
arrière**. Les deux portent maintenant le drapeau.

`marqueDoute()` lit les DEUX formes de journée — `doute` pour celle que
`parseHoraireEntry()` rend, `q` pour celle qu'un mois enregistre — parce que
les deux vues doivent montrer la même étiquette.

Journées prestées : **14 648 → 14 650**, exactement les deux nuits de LHR.
Neuf règles à zéro, compteurs 76/77, mentions non comprises **19 → 17**.

### Deux cellules qui valaient seize heures et une demi-journée

Deux autres « repos à zéro heure » qui n'en étaient pas, tranchés par le
client le 23/09/2026 en même temps que le « N ? ».

**`HS` seul — la journée entière en heures supplémentaires.** AFA les 23 et
24 avril. Le client : « il avait d'abord déplacé ses 2 jours de D (23 et 24)
au 16 et 17, car à la base il ne travaillait pas le 16 et 17 ; par contre il
a quand même été rappelé le 22 et 23 pour travailler en HS le 23 et 24 »,
puis « il a bien fait 2x8h en D de rappel ».

Quatre journées prestées sur des repos, donc — et les deux dernières
s'affichaient en repos à zéro heure : **seize heures supplémentaires
perdues**. Le classeur n'écrit `HS` seul que sur ces deux cellules de toute
l'année ; il n'y a rien à généraliser au-delà de ce qu'elles disent. On
réemploie ce qui existe : `8H HS` du barème ne retire rien à la journée
(`h:0`) et crédite huit heures supplémentaires (`hs:8`), et le code de jour
peint la journée en D comme le fait déjà un repos portant `SD26`.

**Le rappel, lui, n'est écrit nulle part sur ses cellules** — leurs
commentaires disent « D déplacé au 16.04 » et rien d'autre. Les « rappel le
16.04 » du classeur sont sur les colonnes d'AUTRES personnes, aux mêmes
dates. La prime de rappel ne peut donc pas se déduire : à faire écrire au
classeur, ou à poser à la main sur ces deux journées.

**`SD26/ Abs` — la journée prestée, puis écourtée.** VGG le 11 mars,
`["-","SD26/ Abs","Départ à 12h"]`, seule cellule de ce genre dans l'année.
Le client : « pendant le SD26 les gens venaient selon les besoins
nécessaires à la production, mais il a certainement fait 6/14 et est parti à
12h ».

**Il n'y a donc AUCUNE règle à tirer de `SD26`** : il n'implique pas de
pause, et la durée ne se déduit pas de la cellule. Les deux heures
manquantes ne se calculent pas depuis le commentaire non plus — **393
commentaires de l'année parlent d'un départ**, et tous les autres portent une
plage ou un poste dans leur cellule, qui donne l'heure de début. Celle-ci
n'en a pas : le 6 h vient du client, et il est écrit dans le code avec sa
raison plutôt que deviné.

La journée prend la prime de **jour**, et non celle du matin, pour rester
d'accord avec les 23 autres journées « repos + SD26 » : une journée prestée
sur un repos se fait en horaire de jour, sans prime de pause puisqu'il n'y
avait pas de pause prévue.

**`var n` est déclaré plus bas dans `lire()`, et les deux branches sont
mortes en silence.** Écrites au-dessus de `var n=normPlage(txt)`, elles
lisaient un `undefined` hissé : aucune erreur, aucun effet, et le
vérificateur annonçait les mêmes chiffres qu'avant. Elles appellent
`normPlage(txt)` directement.

Journées prestées **14 648 → 14 653**, repos **7 575 → 7 570**, mentions non
comprises **19 → 14**. Neuf règles à zéro, compteurs 76/77.

### Une plage qui nomme une pause dit qu'on est à son poste

Le client, le 25/09/2026 : « GPS le 30/09 fait 10-22 mais vient plus tôt
pour participer au CPPT ».

Sa cellule dit `["10h-22h","D-CPPT"]`. Le code de jour le sortait de sa
pause : la case **Contremaître de l'après-midi passait à 0/1**, et lui se
lisait dans « Hors poste » sous l'étiquette CPPT. Il était pourtant bien à
son poste de 10 h à 22 h — la réunion explique seulement pourquoi il est
venu plus tôt.

Le code de jour dit que la journée s'est faite EN HORAIRE DE JOUR. **Une
plage qui nomme une PAUSE dit le contraire, et elle le dit avec des
heures.** `surSonPosteMalgreF()` ne laisse donc plus sortir du poste quand
la cellule porte une plage dont `posteDepuisPlage()` ne rend pas le jour.

**216 journées portent une plage ET un code de jour ; 121 restent où elles
étaient** — « 7h-15h | SD26 » est bien une journée de jour, et la règle ne
la touche pas. **95 changent de place, dont 80 en « 6h-14h »** : quelqu'un
qui travaille de 6 h à 14 h est au MATIN, quoi que dise l'annotation.

GPS reprend sa place de contremaître le 30/09, et **JKS avec lui** :
`["09h-21h","CPPT"]`, même forme, et son commentaire le confirme — « Réunion
DS de 9h à 10h, CPPT à partir de 10h, remplacé par IME de 21 à 22h ».

**SBZ, non, et je l'avais dit trop vite.** Sa cellule du 30/09 est `["PM"]`,
sans plage ni code de jour : la règle ne le touche pas. Il était déjà dans
une pause et a simplement glissé du gluten au terrain arrière, parce que JKS
a repris la place de gluten. C'est le rééquilibrage, pas cette règle.

**Les manques passent de 12 à 11, et pas par le 30/09.** Cette journée perd
bien son `PM Contremaître 0/1`, mais elle garde son `N Gluten 1/2` : elle
compte toujours. Le −1 vient du **16 décembre**, par un chemin qu'il faut
avoir vu une fois :

- **QBY** y porte `["10h-22h","DS-CE"]`, polyvalences gluten et
  distillation. Avant, `DS-CE` le sortait de sa pause et il partait en
  « Jour » ; maintenant sa plage le garde en après-midi et **il tient sa
  distillation lui-même** ;
- **PAM** y porte `["PM"]`, avec la fermentation dans ses polyvalences.
  Son collègue parti en « Jour », le rééquilibrage l'envoyait boucher la
  distillation — et la **fermentation restait à `0/1`**. Celle-ci étant
  désormais tenue par son titulaire, PAM **couvre la fermentation**.

C'est exactement le mécanisme de couverture établi le 22/09 : le tableau dit
qui TIENT un poste, et PAM a la fermentation pour le jour où le trou se
présente. **Une place qui se libère en déplace une autre trois mois plus
loin** — c'est pourquoi on relit `--manques` en entier après chaque
correction de placement, et pas seulement la journée qu'on croyait toucher.

### `TP` comptait 209 journées prestées pour des gens qui sont chez eux

Le client, le 25/09/2026 : « TP c'est temps partiel, CP (congé parental 4/5
ou 9/10) et TP c'est pareil mais sans la compensation de l'ONEM », puis,
interrogé sur le paiement de la journée : « pour le TP je ne pense pas,
c'est une réduction de temps de travail avec la loi belge pour le 9/10 ou
4/5 ».

**Ce n'est pas une absence que l'on pose** : c'est un jour qui ne fait pas
partie du contrat, comme un samedi l'est pour tout le monde. La réduction
est dans le salaire de base ; le jour n'a donc **aucune ligne de fiche** à
porter. C'est tout ce qui le sépare de `CP`, qui ouvre l'allocation de
l'ONEM et porte la sienne.

**J'avais invoqué le réglage « Fraction payée » comme preuve, et le client
l'a relevé** — « une fraction payée pour les TP ? ce n'est pas plutôt les
CP ? ». Son aide disait « 0,90 = congé parental 9/10 » : elle nommait le
`CP` et rien d'autre. Le champ lui-même est pourtant générique — il
multiplie la rémunération fixe, forfaitairement (`remFixe*p.fraction`), et
un 4/5ᵉ temps partiel fait la même arithmétique qu'un 4/5ᵉ parental. Mais
un texte qui ne nomme qu'un cas laisse l'autre croire qu'il n'est pas
concerné : **l'aide et l'écran d'accueil nomment désormais les deux**, sans
quoi les 8 personnes à `TP` garderaient une fraction de 1 et un socle trop
élevé.

**Ce que la correction déplace se mesure, et ce ne sont pas des primes.**
`primeD` vaut **0** — la prime « jour » est nulle, donc les 209 journées
n'en portaient aucune. Le socle, lui, est forfaitaire et ne dépend pas des
heures. Ce qui bougeait vraiment, c'est le **chèque-repas** :
`if(h>=4) acc.joursCr++` en donne un par journée prestée d'au moins quatre
heures, donc **209 chèques étaient accordés pour des jours non travaillés**
— FLN 40, LAX 34, ATA 26, DWS 26, SPT 26, SMA 26, LCI 25, GDT 6.

`TP` était pourtant dans `JOUR_PRIME_PAUSE`, donc lu comme une journée
**prestée** en horaire de jour. Même forme de cellule, lecture opposée :
`["7h-15h","CP"]` donnait une absence à zéro heure, `["6h-14h","TP"]` un
poste à huit heures avec la prime de jour. **La cellule franche de ces
journées porte ce que la rotation avait PRÉVU**, pas ce qui a été presté —
`D` 73 fois, `6h-14h` 57, `7h-15h` 47, `N` 18. Le module des manques les
croyait à leur poste.

**Le « c'est pareil » s'est mesuré avant d'être cru.** Les deux codes se
posent par blocs de un à trois jours — et non un jour fixe par semaine — et
leurs totaux sont ceux d'un temps partiel : 26 journées valent un jour par
quinzaine (9/10), 51 un jour par semaine (4/5). `TP` : 209 journées chez 8
personnes. `CP` : 423 chez 17.

**Le code entre au barème avec SON PROPRE `k`**, et non celui de
`SANS SOLDE` — qui ne porte pas de ligne non plus. Un congé sans solde et un
temps partiel ne sont pas la même chose, et le jour où une fiche montrera
une ligne pour l'un, il ne faudra pas la poser sur l'autre.

Journées prestées **14 645 → 14 436**, absences **+209** — exactement les
209 journées, sans un écart. Neuf règles à zéro, compteurs **76/77**,
manques **inchangés à 11 / 11** : le rééquilibrage couvrait déjà ces
absences. Couples de polyvalence **101 → 99**, les 33 au quota inchangés.
Vérifié au navigateur sur ATA : ses 26 journées se rendent en absence, pas
en poste.

**La `fraction` reste saisie à la main** : on pourrait la déduire du nombre
de journées `TP`, mais c'est un réglage personnel qui ne quitte pas
l'appareil, et la déduction se tromperait sur une année incomplète.

**Et la fiche MONTRE ces heures.** Puisque aucun code d'absence ne paie,
`k:"TP"` ne décidait que de les afficher ou de les taire — la première
version les taisait, et le client a tranché : « fait cela ». La ligne
**« Heure(s) temps partiel »** se pose à côté de celle du congé parental,
dont elle est le jumeau, avec **son infobulle à elle**. Surtout pas celle
des heures assimilées à du travail : ce motif annonce « payées comme des
heures prestées », ce qui serait faux ici. Vérifié sur ATA : 24 heures en
septembre, et aucune colonne en euros.

### Un congé et un rappel dans la même cellule

GPS le 02/07, `["7h-15h","RHS+02h-06h","Rappel le 02/07"]` — la seule
cellule de l'année à mêler un code d'absence et une plage. Le client, le
25/09/2026 : « il a fait 4 HS de 02-06h en étant rappelé le jour même ; **je
sais que c'est du HS car il n'y a aucune cellule dans sa liste qui mette
`+4h FT`**, et de 06 à 14h il était bien en RHS ». Le raisonnement est celui
du classeur : l'épargne au compteur s'écrit, elle.

Le calcul en faisait un poste `D` de **8 h prestées sans aucun RHS** — les
deux moitiés fausses.

**`abs` n'accepte qu'un code, et c'est le congé qui le prend** : c'est lui
qui vide la journée, et c'est le libellé de fiche de ses 1er et 3 juillet.
Les heures supplémentaires passent par **`ax`**, que l'accumulateur
concatène déjà à `a`. Ses deux autres lecteurs ne regardent que les codes
dont `h>0`, donc un `4H HS` n'y touche à rien. Un champ parallèle aurait
demandé cinq points de synchronisation ; **une source de plus pour un
mécanisme existant vaut mieux qu'un mécanisme de plus à tenir en phase.**

**LA PLAGE DU RAPPEL NE SE MET PAS DANS `r.plage`**, et la première version
l'a fait sans rien casser de visible. Ce champ dit la plage prestée COMME
POSTE DU JOUR, et `dureeReelle("D",[2,6],8)` rend **12** : le poste est
étendu pour couvrir 2 h à 6 h, la journée devient douze heures, les huit de
RHS en sont retirées, et l'on affiche « 4 h prestées en D » — ni le congé,
ni les heures supplémentaires. La plage ne sert qu'à COMPTER les heures du
rappel.

**Et la copie du vérificateur ne portait pas `ax`.** `index.html` l'écrit
depuis toujours (`nrec.ax=parsed.ax`), `enregistre()` du vérificateur non :
le mois rejoué perdait les codes supplémentaires. C'est encore le même
piège — deux copies, et c'est la seconde qui reste en arrière. `--journee`
les imprime désormais sous « codes en plus ».

Journées prestées **14 436 → 14 435**, absences **+1**, mentions non
comprises **14 → 13**. Neuf règles à zéro, compteurs 76/77. Vérifié au
navigateur sur la fiche de juillet de GPS : 24 h de récup. HS, 4 h
supplémentaires, 4 h payées à 150 %, et la prime de rappel J.

**LES HEURES VONT AU COMPTEUR, LA PRIME DE PAUSE SE PAIE.** Le client, en
réponse à la question de la prime de nuit : « il reçoit les 4 h HS dans un
compteur et il les reprend quand il veut ou se les fait payer en fin
d'année, quand on doit mettre les compteurs HS à zéro », puis « les 4 h de
rappel (02-06) sont payées en nuit ».

La fiche séparait déjà les deux sans qu'on s'en serve : `hsAutoBkt` paie les
HEURES, `hsAutoPoste` paie la PRIME D'ÉQUIPE. **Une heure récupérée rend
l'heure, pas la prime de la pause où elle a été prestée.** Les heures
versées au compteur ne passent donc plus par le premier.

**Et le poste des heures supplémentaires n'est pas celui de la journée** : un
rappel de 02 h à 06 h est de la nuit, même posé sur un congé dont la cellule
dit « 7h-15h ». Sans cela la prime se cherchait dans le seau « D », dont la
prime est nulle — donc aucune ligne. `rec.hsp` porte le poste, `rec.hsc` le
versement au compteur, tous deux jusqu'au mois et dans les DEUX copies de
`enregistre()`.

Vérifié au navigateur sur juillet : la ligne « HS non compensées » a disparu,
« 4 h versées au compteur » apparaît, et « Suppl. Équipe Nuit à 150 % (heures
suppl. de l'horaire) » paie la prime.

**ET LA RÈGLE VAUT POUR TOUTES LES HEURES SUPPLÉMENTAIRES.** Le client,
interrogé sur les 205 autres journées : « cela dépend de si il remplit une
feuille pour avoir des FT+ ou des HS. **Quoi qu'il arrive les 2 vont dans un
compteur**, mais le compteur HS n'apparaît pas dans le classeur. »

C'est son raisonnement sur GPS, généralisé : **le classeur ÉCRIT l'épargne
au flex time ; son silence désigne l'autre compteur**, celui qu'il ne porte
pas.

**ELLES SONT PAYÉES À LA REPRISE, ET J'AVAIS ÉCRIT LE CONTRAIRE.** Le
client : « les HS sont payées quand les opérateurs reprennent leurs heures
sup (indiqué dans l'horaire ou en commentaire), donc ta phrase n'est pas
correcte ». J'avais annoncé que l'application ne les payait plus. Le circuit
se lit en deux temps : **prestée**, l'heure va au compteur et le classeur
n'écrit rien ; **reprise**, le classeur l'écrit — `RHS`, `2h RHS`, un
commentaire — et la journée est payée. Une reprise d'un jour vaut zéro heure
prestée sans que le socle bouge ; une reprise partielle ne retire rien à la
journée. **L'argent n'est pas perdu, il est décalé.**

Ce qui est parti, c'est le paiement AU MOIS DE LA PRESTATION, au taux
majoré — **775 heures sur 205 journées** — qui faisait payer ces heures
**deux fois**. La prime d'équipe reste due, et c'est la moitié qu'il ne
faut pas emporter avec l'autre.

Le champ manuel « Heures suppl. non compensées » reste payé : c'est
désormais le SEUL endroit où l'on déclare des heures réellement payées, et
c'est une saisie volontaire, pas une déduction de l'horaire.

Le drapeau `rec.hsc` a disparu avec l'exception qu'il portait — ce n'est
plus un cas particulier, c'est la règle. `rec.hsp` reste : le poste des
heures supplémentaires n'est toujours pas celui de la journée.

**ET LA FICHE EN PORTE DEUX, QUE J'AVAIS TOUTES DEUX RETIRÉES.** Le client :
« vérifie avec toutes mes feuilles de paye si ta logique est bonne ». Elle
ne l'était pas. Trois de ses fiches portent des heures supplémentaires,
toujours sous la même paire :

```
 1:30  Heures sup à compenser à <taux> à 150 %     +
-1:30  déduc HS à comp à <taux>                    −
```

Le sursalaire est payé au taux majoré LE MOIS DE LA PRESTATION, et l'heure
de base est déduite puisqu'elle sera reprise plus tard. Net : la moitié du
taux horaire. La fiche affiche le solde d'année du compteur juste à côté. **L'heure part au compteur, le sursalaire ne l'attend pas** —
j'avais lu « les heures vont au compteur » comme « rien n'est payé », et
c'était faux d'une moitié.

Les deux lignes s'écrivent séparément plutôt que nettes : l'onglet Contrôle
se lit ligne à ligne contre la fiche, et une ligne à 50 % n'y existe pas.

**La leçon de méthode** : les fiches sont le contrôle le plus sévère dont on
dispose, et je n'avais pas pensé à les ouvrir pour une règle de paie. Le
client a dû le demander.

### Ce que les fiches disent d'autre, et qui n'est pas expliqué

La même comparaison montre un écart ANCIEN, identique avant et après tout ce
qui a été fait le 25/09 — vérifié en rejouant l'outil sur un commit
antérieur : **l'application compte 843 h là où huit fiches en portent
962,53**, soit **−119,53 h et −8 journées** sur l'année.

Ce qu'on sait déjà : les familles d'absence concordent presque toutes
(vacances, congé parental, jour férié, formation syndicale : identiques),
la période de chaque fiche est bien le mois civil, et VBN n'a **aucune**
journée `HS` dans l'horaire — l'écart n'a donc rien à voir avec les heures
supplémentaires. Ce sont les **heures et jours PRESTÉS** qui manquent.

#### L'horaire avait des trous, mais ce n'est PAS l'explication

En cherchant l'écart, mai a paru le donner : la fiche y compte 14 jours et
112 h, l'application 12 et 96 — deux journées, seize heures, exactement
l'écart. Et ces deux journées, les 23 et 24 mai, n'existaient pas dans
`data/horaire-2026.json`.

**J'ai annoncé « mai s'explique en entier ». C'était faux**, et le client
l'a dit aussitôt : « si vide c'est une journée sans travail (repos), et je
confirme que je ne travaillais pas ces jours-là dans mon calendrier ». Une
journée qu'il n'a pas travaillée ne peut pas être les seize heures qui
manquent. **Deux nombres qui tombent juste ne sont pas une cause** — c'était
une coïncidence, et je l'ai prise pour une preuve.

L'écart de **−119,53 h reste donc entier et inexpliqué**.

#### Le trou était réel, lui, et il est corrigé

Le classeur laisse ces cellules VIDES — pas « - », rien du tout. Le
convertisseur sautait la ligne : **643 journées absentes du fichier chez 13
personnes**, pas « en repos » mais ABSENTES. Le calendrier n'avait pas de
case à peindre et `equipeDuJour()` recevait un `undefined`.

Une cellule vide devient donc un repos — **mais seulement entre la première
et la dernière journée écrite de la personne**. Sans cette borne, la règle
donnait 348 journées de repos à quelqu'un qui n'en a que 17 d'écrites sur
l'année, 193 et 69 à deux autres : **ceux-là ne sont pas en repos, ils ne
sont pas encore arrivés ou ils sont partis**, et les peindre les aurait fait
vivre dans la composition et dans les manques d'effectif de mois où ils
n'étaient pas là.

Le classeur ne dit nulle part quand quelqu'un arrive. Ce qu'il dit, c'est où
sa colonne commence à porter quelque chose : **la borne est ce qu'il écrit,
pas une date devinée.**

**Et le client l'a confirmé** : « ceux qui n'avaient rien avant sont
certainement des nouveaux qui sont arrivés en cours d'année ». Les cinq
personnes dont la colonne commence en retard le disent d'elles-mêmes — leur
première journée écrite tombe **chaque fois un LUNDI, suivi de cinq « D »
d'affilée** : la semaine d'accueil, en horaire de jour, avant d'entrer dans
une rotation. Cinq sur cinq, du 5 janvier au 14 septembre. C'est la preuve
que la borne haute du remplissage est la bonne : avant ce lundi, la personne
n'était pas là, et lui peindre des repos l'aurait fait vivre dans les manques
d'effectif de mois où elle n'existait pas.

**+20 journées**, 27 462 → 27 482, repos 7 571 → 7 591, journées prestées
**inchangées à 14 435**. Neuf règles à zéro, compteurs 76/77, manques
inchangés à 11.

**Et la comparaison aux fiches est identique au centième après la
correction** — −119,53 h comme avant. C'est la preuve que ces journées
n'étaient pas l'explication : un repos vaut zéro heure, qu'il existe dans le
fichier ou non. La correction rend au calendrier des cases qui lui
manquaient ; elle ne rend aucune heure.

#### Ce qui est ÉCARTÉ, avec ses chiffres

Trois pistes ont été mesurées et ne tiennent pas :

- **les heures supplémentaires** : VBN n'a **aucune** journée `HS` dans
  l'horaire ;
- **les journées de plus de huit heures** (`18h-06h` lu 8 h au lieu de 12) :
  **26 h sur l'année**, et dans les mauvais mois ;
- **le flex time épargné** (55 h) et les **postes prévus non prestés**
  (56 h) : février et juillet en portent beaucoup pour un écart quasi nul,
  mai n'en porte aucun pour un écart de 16 h.

#### Ce que la fiche compte, et qui n'est pas ce que l'application compte

Les lignes d'heures de chaque fiche **somment à un multiple exact de huit** :
176, 200, 208, 216, 192, 168, 144 selon le mois. La fiche **partage un total
mensuel fixe** entre prestées, vacances, maladie, congé parental et repos
compensatoire.

L'application, elle, n'a aucune notion de ce total : elle **additionne ce
qu'elle lit**, et une journée absente du fichier ne pèse rien.

**Une question reste pour le client**, et elle se répond d'une phrase : que
compte exactement la ligne « Heure(s) prestée(s) » de sa fiche — les heures
réellement faites, ou le solde du mois contractuel une fois les absences
retirées ? La première question, celle des cellules vides, est répondue et
close ci-dessus.

### Le classeur du 25/09/2026 à 15 h 23

Un nouveau récapitulatif, reçu le soir même. Procédure complète :
anonymiseur, second contrôle, conversion à côté, comparaison, installation,
contrôle croisé du dépôt, puis les trois vérificateurs.

**Ce n'est pas une correction, c'est une AVANCE** : le classeur a été rempli
sur octobre. **201 journées changent chez 34 personnes**, 27 482 → **27 574**,
journées prestées 14 435 → **14 490**.

**NPI ne s'arrêtait pas au 30/09 : sa colonne n'était pas encore remplie.**
La question posée la veille se répond d'elle-même — **92 journées** lui sont
écrites jusqu'au 31 décembre, et son compteur RTT apparaît. Il n'y avait rien
à trancher : il fallait attendre le classeur suivant. C'est la démonstration
de la règle du projet — **ne pas deviner à la place du classeur**.

**Les manques d'effectif tombent de 11 à 8 journées** d'ici la fin de
l'année, ce qu'on attend d'un mois qu'on vient de remplir : les
remplacements d'octobre sont maintenant écrits.

Ce qui bouge par ailleurs, et qui se lit dans la sortie du comparateur :
**13 compteurs** corrigés, une maladie de quatre jours posée en fin
septembre, un « Test de performance » retiré de onze cellules où il n'était
qu'un commentaire d'organisation.

**Les quatre prénoms sont revenus, et c'était prévu.** Ils étaient retirés à
la main à chaque conversion. **Ce n'est plus le cas depuis le 26/09/2026** :
le convertisseur les apprend de la feuille « Polyvalence », et une garantie
arrête la conversion si un nom du classeur subsiste. Voir « L'audit du
26/09/2026 » — l'une des quatre corrections faites à la main était fausse.

`CEPS` est apparu dans les survivants du second contrôle : c'est un centre de
formation — « Formation ARI - CEPS Seraing » — et non quelqu'un.

Neuf règles à zéro, compteurs 76/77, découpe de `comparer-fiches` à
l'épreuve, garde-fou du dépôt et contrôle croisé à zéro.

### Le classeur du 28/09/2026 à 11 h 11

`mettre-a-jour.py` : les sept portes ouvertes, installé. **32 journées
chez 22 personnes, 13 compteurs** ; 27 574 journées, prestées 14 490 →
**14 451**. Rien de structurel : les journées du 25 au 29/09 complétées
après coup (départs anticipés en RTT, reprises RHS, trois « Abs ·
Justificatif à fournir » le 28/09 — AFA, FPS, SMA —, ajustements de flex
time), FLI malade le 02/10, DWS en RTT les 21 et 22/10 remplacé par GDT,
les congés d'octobre de MGY. Un sous-effectif de plus d'ici la fin de
l'année : **le 02/10, contremaître du matin 0/1** (FLI malade), avec JBI
en D comme piste.

**JKS le 21/10** : `["DS","4h +FT","… présent à la DS prestera la pause
N"]`. La pause n'est plus dans la cellule (l'ancien classeur écrivait
`["N","DS"]`), elle est dans le commentaire ; lue par le cycle, l'épargne
s'en retranchait — 4 h de nuit au lieu de 8. `parseHoraireEntry()` lit
« prestera la pause X » quand la cellule franche est « DS » seul : c'est
exactement son 17/06, `DS + PM · 4h +FT` (`COQUILLES`), 8 h et 4 h au
compteur. Une seule journée de l'année ; les quatre sorties du
vérificateur identiques à l'octet avant et après ce correctif.

MGY le 26/09, `1,25 rhs`, se lit bien : 1 h 15 de reprise, 6,75 h
prestées.

### Le classeur du 28/09/2026 à 13 h 39

Deux heures et demie après le précédent. Sept portes ouvertes, installé :
**20 journées chez 9 personnes, 2 compteurs**, prestées 14 451 → 14 448.
AFA malade du 28 au 30/09 ; SPT malade du 30/09 au 06/10 (ses échanges
avec JKS et sa DS du 05/10 deviennent des « Abs ») ; VBN rappelé sur un
repos le 02/10 pour remplacer FLI — le contremaître du matin n'est plus en
sous-effectif ; SVE en formation distillation en 7h-15h du 28/09 au 01/10,
prime de nuit conservée les 28 et 29 (lu : prime N, presté D) ; ATR au
terrain arrière pour SMA le 28/09 ; DBE parti à 13 h le 16/10, relayé par
RDT (1 h +FT). **Nouveau sous-effectif : le 02/10, terrain arrière de nuit
0/1** — SPT malade, ASS en DTT, GKT en RTT, JKS passé en PM par échange ;
piste proposée : SKS, depuis la meunerie. **C'était faux** : sa cellule
disait déjà « Remplace SBZ », voir « Les réponses du 29/09/2026 ». Neuf règles à zéro, compteurs
76/77, intégralité à zéro.

### Le classeur du 28/09/2026 à 16 h 44

Sept portes ouvertes, installé : **17 journées chez 8 personnes**, aucun
compteur. LHR les 02 et 03/10 perd son « N ? » : `["-","N","MPE :
Remplace SPT RAPPEL 28/09 accord LH"]`, la nuit est confirmée et se lit
en rappel sur un repos (8 h sup). ASS et DBE rappelés sur un repos le
05/10 pour une intervention au gluten (N, 8 h sup chacun). FPS malade du
28 au 30/09. SPT : « Remplacé par LHR » les 02 et 03/10, et le 04/10
devient une nuit prévue non prestée (« Abs »). BLR : ses deux congés
posés les 10 et 11/10 sont renvoyés aux 14 et 15/10 (« CF »). ATR en
12h-20h le 29/09 (remise en service du F2), AFA avec un commentaire de
CIP le 06/10. **Sous-effectifs d'ici la fin de l'année : inchangés à
l'octet** (7 journées, `--manques 0929`). Neuf règles à zéro, compteurs
76/77, intégralité à zéro ; vérifié au navigateur à 320 (hors ligne),
390 et 1280 px.

### Le classeur du 29/09/2026 à 7 h 46

Sept portes ouvertes, installé : **17 journées chez 11 personnes, 1
compteur** (les RJF de KDN, 8 posés le 02/10). Prestées 14 447 → 14 445.
SMA malade du 28 au 30/09 (le « Justificatif à fournir » du 28 est parti),
PLZ la remplace au terrain arrière le 29 ; échange de pause CHD et LAA les
30/09 et 01/10 ; AAI rappelé en nuit le 30/09 au terrain arrière, BBZ
rappelé sur un repos à la même nuit ; KDN en RJF le 02/10, DWS aux
chaudières à sa place et GDT au terrain arrière ; JBI le 28/09 complète
sa matinée (« +2h rhs », lu par la règle des deux moitiés ; le départ à
14 h n'est pas pris pour un départ sans code, la journée portant déjà un
RTT) ; SPT, VM de reprise le 13/10.

**« poly.Etha »** (AAI le 30/09) est une nouvelle écriture de « poly.
Etoh », le terrain arrière : la règle « mention avalée » l'a signalée, et
le motif des postes l'accepte désormais. Sous-effectifs d'ici la fin de
l'année **inchangés à 6 journées**, compteurs identiques, neuf règles à
zéro, intégralité à zéro ; Recyclage : PLZ fermentation 13 → 12 (il est
au terrain arrière le 29/09). Vérifié au navigateur à 320 (hors ligne),
390 et 1280 px.

**J'ai posé au client une question dont la réponse était déjà à l'écran.**
La nuit du 30/09, AAI porte « Remplace SKS Remplacé par BBZ » et
l'application le montrait au terrain arrière, BBZ en distillation ; j'ai
demandé si ce n'était pas l'inverse. Le client : « BBZ ne peut pas faire
le terrain, il a été rappelé pour faire une nuit de plus. AAI, prévu en
distillation, passe sur le terrain (polyvalence ok) et BBZ vient en
distillation ». C'est la règle déjà écrite : **« remplacé par » parle du
poste PRÉVU**, pas d'une absence. Avant de douter d'un placement, vérifier
les polyvalences (BBZ n'a pas la fermentation, donc pas le terrain
arrière) : elles tranchent seules.

### Les sous-effectifs restants, relus commentaire par commentaire

Le 29/09/2026, après le terrain arrière du 02/10, les six sous-effectifs
restants ont été relus avec tous les commentaires du jour.

**Un seul avait sa réponse dans le fichier** : le 24/11, GPS porte
`["N","D-CPPT","remplacé au CPPT par TFI"]` — un autre va à la réunion,
il reste contremaître de nuit. `surSonPosteMalgreF()` lit désormais
« remplacé au CPPT (CE, DS) par X », sauf si la personne est AUSSI
remplacée à son poste : GPS le 25/03, « remplacé au CPPT par NDO remlacé
par VBN », reste hors poste. Deux journées de l'année portent la forme,
une seule change. Sous-effectifs d'ici la fin de l'année **6 → 5**, sur
l'année 269 → 268 places ; neuf règles, Recyclage et compteurs identiques
à l'octet.

**Les cinq autres, le classeur ne dit pas qui comble** :

- 05/10 AM fermentation (équipe 4) : la place de fermentation de l'équipe
  4 est sans titulaire (colonne Shift 4 Q), QBY en RTT, PAM à la
  distillation ; GSK écrit « équipe au complet » ;
- 16/10 N meunerie (équipe 5) : CDE « Abs », sans remplaçant écrit.
  **Et un commentaire n'y était pas suivi** : LCI `["N","R","en
  fermentation"]` restait en distillation. Le client, le 29/09/2026 : la
  présence ne lui était pas utile là-bas, « cependant il faut suivre ce qui
  est écrit dans l'horaire » (il fera retirer le commentaire).
  `posteEcrit()` lit désormais un commentaire qui COMMENCE par l'atelier
  (« en fermentation », « en meunerie remplace TCE »), sauf s'il doute
  (ALZ le 23/10, « …pour remplacer FPS? »). Trois journées de l'année, une
  seule change de place ; neuf règles, sous-effectifs, Recyclage et
  compteurs identiques à l'octet ;
- 21 et 22/10 N chaudières (équipe 2) : ADS en RJF, sans remplaçant
  écrit, alors que le gluten a quatre personnes pour deux ;
- 12/11 N terrain arrière (équipe 1) : GDT en VA remplacé par BBZ, qui
  n'a que la distillation.

### Le classeur du 29/09/2026 à 13 h 09

Sept portes ouvertes, installé : **17 journées chez 11 personnes**, aucun
compteur. **Le classeur comble trois des cinq sous-effectifs restants** :
le 05/10 AM, ATR `["AM","fermentation"]` ; le 16/10 N, LHR « Remplace
CDE » en meunerie (le commentaire « en fermentation » de LCI est retiré,
comme le client l'avait annoncé, et SMA passe en fermentation pour CHD,
AAI au terrain arrière) ; le 12/11 N, ATR au terrain arrière pour DWS.
GPS le 24/11 perd son « D-CPPT » (« remplacé au CPPT par TFI » reste) ;
MMS remplace SPT jusqu'à 14 h 30 le 13/10 (VM de reprise). Restent les
chaudières de nuit des 21 et 22/10 : **2 journées** d'ici la fin de
l'année.

**« Poly.Ethol »** (ATR le 12/11) : troisième écriture du terrain arrière,
après « poly. Etoh » et « poly.Etha » ; la règle « mention avalée » l'a
signalée, le motif l'accepte. Neuf règles à zéro, Recyclage et compteurs
identiques à l'octet, intégralité à zéro ; vérifié au navigateur à 320
(hors ligne), 390 et 1280 px.

### Le classeur du 29/09/2026 à 13 h 28

Reçu le 30/09. Sept portes ouvertes, installé : **8 journées chez 4
personnes, 2 compteurs**. JBI le 29/09 (« 3,5 rhs ») et QBY le 29/09
(« 2h rhs », départ à 12 h) : reprises en fin de journée ; NPE le 18/10
part à 10 h (« 4h -FT »), QBY le relaie de 10 h à 14 h (« 10h-22h ·
4h +FT », lu 8 h en PM et 4 h au compteur) ; NPI en 6h-14h les 09 et
10/11, ses D des 12 et 13/11 marqués « - ». Compteurs flex time de NPE
et QBY suivis. Neuf règles à zéro, `--manques 0930` et `--compteurs`
identiques à l'octet, intégralité à zéro ; vérifié au navigateur à 320
(hors ligne), 390 et 1280 px.

### Le classeur du 30/09/2026 à 14 h 17

Sept portes ouvertes, installé : **14 journées chez 9 personnes, 4
compteurs** (RTT de CJD, GDT, PDF et VBN). Prestées 14 445 → 14 441.
VGG malade les 30/09 et 01/10 ; PDR (CT le 30/09) est désormais remplacé
par QBY au lieu de VGG ; CJD part à 4 h la nuit du 29/09 (« 2h RTT,
équipe complète ») et PDF passe cette nuit-là en RTT ; ATR en 10h-18h le
29/09 ; GDT en VA le 08/12 remplacé par DWS au terrain arrière, et son
29/10 passe de VA à RTT ; LHR : ses VA des 22 et 23/10 avancés aux 08
et 09/10. **VBN le 30/09** : `["D-CPPT","1h RTT","+1h RHS Arrivée à
09h Départ à 15h"]` — la nuit avec « D-CPPT » attendue pour trancher la
question de la prime est devenue une journée de 9 h à 15 h ; lue 6 h
(1 h RTT, 1 h de reprise par la règle des deux moitiés), prime de nuit
conservée comme pour toute journée « N · D-CPPT ». Le client l'a
tranché le même jour : les heures prestées gardent la prime que le
commentaire écrit, celle de la pause prévue sinon — la lecture était
déjà la bonne.
Sous-effectifs d'ici la fin de l'année et compteurs **identiques à
l'octet**, neuf règles à zéro, intégralité à zéro ; vérifié au
navigateur à 320 (hors ligne), 390 et 1280 px.

### Le classeur du 01/10/2026 à 9 h 25

Sept portes ouvertes, installé : **14 journées chez 9 personnes, 7
compteurs**. Prestées 14 441 → 14 437. CKS part à 13 h le 30/09 (1 h de
reprise) ; FPS : son 05/09 devient un DTT entier et le 07/09 un repos ;
KDN en RTT le 16/12, ½ VA le 17/12 et ½ DTT le 18/12, remplacé par MHI
(PM → N) ; JBA en VA le 18/12, remplacé par SPS ; LHR le 30/09 passe en
`D-CPPT · 2h RTT` (6 h) ; SVE le 30/09 et le 01/10 en formation
distillation `7h-15h · 8h +FT` — le poste entier part au compteur, 0 h
payée (section 5 de `docs/conversion-horaire.md`), compteur flex time
+16 h. **VBN le 30/09** devient `["D-CPPT","2h RTT","+1h RHS compteur à
0 Arrivée à 09h Départ à 15h"]` : lu d'abord 5 h (8 − 2 − 1), alors que
9 h-15 h en font 6. Le client, le même jour : « 6 h prestées (09-15),
+ 1 h sup faite après 15 h ». Le classeur le disait : « compteur à 0 »
(JBS le 04/03, SMK le 06/08 l'écrivent aussi) veut dire que le compteur
de récup. HS est vide — rien n'est repris. `lireJournee()` lit donc un
« +Nh RHS » accompagné de « compteur à 0 » comme N heures sup (`r.hc`,
prime de la pause payée) et non comme une reprise : 6 h prestées, 2 h de
RTT, 1 h sup. Seule journée de l'année de cette forme ; neuf règles,
sous-effectifs, Recyclage et compteurs identiques à l'octet ; la fiche
de septembre porte l'heure sup, hors ligne compris. Trois compteurs passent en négatif
au classeur : VA restant de JBA (−8), RTT restant de KDN (−6) et de SMA
(−4). Sous-effectifs d'ici la fin de l'année et compteurs **identiques
à l'octet**, neuf règles à zéro, intégralité à zéro ; vérifié au
navigateur à 320 (hors ligne), 390 et 1280 px.

### Le classeur du 09/10/2026 à 9 h 30

**La porte d'intégralité s'est fermée, sur une seule journée, et elle avait
raison.** VBN le 15/10 : le commentaire écrit « cf. 09/10 », saut de ligne,
puis la signature de son auteur et son deux-points. Le convertisseur, qui
retire toute la tête d'un commentaire quand elle nomme un auteur, emportait
le renvoi avec la signature ; l'anonymiseur, lui, ne retire que la ligne
signée, et gardait « cf. 09/10 ». Le convertisseur relève désormais ce qui
précède la DERNIÈRE ligne de la tête avant que les sauts de ligne soient
écrasés, et le garde : la signature tient sur sa ligne. Mesuré : sur ce
classeur, l'ancien et le nouveau convertisseur ne diffèrent que par cette
journée ; sur le classeur du 01/10, ils sont identiques à l'octet.

**Le garde-fou du dépôt s'est fermé ensuite** sur « Débourrage Ligne »
(TCE le 05/10, « Débourrage Ligne L » : déboucher la ligne L) — lu en
contexte, ajouté à `tools/formes-admises.txt`.

Puis sept portes ouvertes, installé : **175 journées chez 38 personnes, 14
compteurs**, et une personne de plus — **SLI**, opérateur en formation,
21 journées. **Je ne l'ai pas signalé au client, et j'aurais dû** : il a dû
préciser lui-même que c'est un intérimaire en formation meunerie. Une
ARRIVÉE du rapport se dit au client avec la question de qui elle est. YBT malade du 12/10 à la fin de l'année (65 journées, ses VA
deviennent des « Abs ») ; PDE malade du 10 au 16/10 ; FLN en congé du 29/10
au 08/11, remplacé par ALZ au terrain arrière ; MHI en congé du 23 au 28/10 ;
échanges IME/RDT (09-11/10), CJD/DBE (21-22/10), NPE/QBY (21/11) ; GBT-1
rappelé les 21 et 22/10 pour QDE. Neuf règles à zéro, compteurs **77/78**
(la nouvelle personne concorde), intégralité à zéro, découpe de
`comparer-fiches` à l'épreuve ; vérifié au navigateur à 320 (hors ligne),
390 et 1280 px.

### Un commentaire peut relever l'effectif d'une journée

Le client, le 25/09/2026 : « quand il est écrit "Test de performance
Vyncke", c'est pour que ces dates-là il fallait 3 opérateurs chaudière en AM
et PM ».

**Je l'avais rangé parmi les commentaires d'organisation**, c'est-à-dire
nulle part — je venais d'annoncer qu'il avait « quitté onze cellules », comme
si sa disparition n'ôtait rien. C'est la règle de tête du projet appliquée à
l'effectif : **le commentaire dit ce qui a réellement été demandé, et il
prime**. Un poste tenu à deux ce jour-là n'est pas complet, et le module des
manques l'annonçait vert.

**LA PHRASE EST LUE, PAS LA DATE.** Une table de journées — comme
`POSTE_TRANCHE` ou `EQUIPE_TRANCHEE` — aurait vieilli au premier classeur
suivant. Ici le classeur ÉCRIT l'exigence ; il n'y a rien à décider à sa
place, seulement à lire. Le motif l'a prouvé sur-le-champ : il a trouvé
**le 09/03, que le client n'a pas cité** — « Nettoyage Bang and Clean.
Présence de 3 opérateurs obligatoire en AM et PM ». Même exigence, autre
raison. Une table des journées « Vyncke » l'aurait manqué.

Mesuré sur les 27 574 journées : **15 journées**, toutes de cette forme,
toutes à 3, et **aucune autre cellule attrapée**.

**Les pauses viennent du TEXTE** : « en AM et PM » sur quatorze journées,
« en AM, PM et N » sur celle du 29/09. Les deviner aurait ajouté une nuit
que personne n'avait demandée.

**Le poste, lui, n'est pas écrit — et le classeur le corrobore quand
même.** Sur les 17 personnes qui portent la phrase, **14 sont des
chaudières de la ligne 9**, et les trois autres ont « chaudières » écrit
dans leur annotation ce jour-là : c'est le renfort envoyé au poste. Ce n'est
donc pas la parole du client contre le silence du fichier — les deux disent
la même chose.

La règle ne fait que **monter** l'effectif : un commentaire ne peut pas
vider un poste, et le jour n'attend toujours personne.

**Ce que cela déplace, mesuré** : sur l'année, les places creuses passent de
**377 à 384** et les journées de 188 à 189 — cinq journées de janvier où les
chaudières tenaient à deux ou un pour trois demandés (22, 23, 26, 27 et
28/01). Le 09/03 et les 22 au 25/09 ne bougent pas : ils étaient bien trois.
Fermentation **+1**, par le rééquilibrage — une place qui manque ailleurs en
déplace une autre, c'est le mécanisme déjà documenté.

**Et une seule journée à venir est concernée : le 29/09 au matin**, qui
passe de « complet » à **`2/3`**. Vérifié au navigateur, à 390 et 1280 px :
le module « Postes en manque » l'affiche, entre le terrain arrière du 27 et
le gluten du 30. Les manques d'ici la fin de l'année passent de 8 à 9.

**Et le motif était trop étroit, comme la douzième règle le prédit.** Deux
journées portent la même exigence écrite autrement et lui échappaient :
le **13/07**, « Présence de 3 opérateurs obligatoire », sans dire la pause,
et le **16/09**, « 3 opérateurs en poste par pause » — ATR y est noté
« Renfort chaudières… en D comme 3ᵉ homme ». Un motif qui lit moins qu'il ne
croit ne ment pas : il se tait.

`RENFORT_TRANCHE` porte la décision du client pour le 13/07 — « c'est en AM
surtout qu'il faut être 3 ». Elle **COMPLÈTE** le classeur au lieu de le
corriger, d'où une fusion par le maximum : c'est ce qui la distingue de
`POSTE_PERIODE`, qui vient en premier justement pour effacer ce que le
classeur écrit. L'après-midi n'y figure pas alors que trois cellules du
13/07 sont en PM — le client a dit « surtout en AM », et inventer une
exigence ferait apparaître un manque qui n'a jamais existé.

La journée passe à **`AM Chaudières 2/3`** : sur l'année, 384 → **385**
places creuses et 189 → **190** journées. Rien ne bouge d'ici la fin de
l'année, le 13/07 étant passé.

**Le 16/09 : « par pause » veut dire AM et PM.** Le client, le 25/09/2026 :
« c'était 3 en AM et en PM ». La nuit n'y est donc pas — et le classeur dit
la même chose de lui-même, toutes les journées renforcées de l'année étant
en AM et PM, la seule exception nommant explicitement « en AM, PM et N ».
La journée passe à `AM Chaudières 2/3 · PM Chaudières 2/3`.

**Et une exigence que le classeur porte encore peut ne plus valoir.** Le
client, le même jour : « c'est fini aujourd'hui ». Le classeur reçu le
25/09 avait déjà retiré le commentaire de **13 cellules sur deux
journées** — 5 des 6 du 25/09, 8 des 9 du 29/09 — mais il en a laissé UNE de
chaque, et chaque fois celle du **renfort lui-même**, venu en 7h-15h avec sa
prime de pause. Un reste de nettoyage, pas une exigence.

`RENFORT_CLOS` lève la journée du **29/09**, la seule qui soit APRÈS
aujourd'hui. Le 25/09 garde la sienne — « fini aujourd'hui » se lisant
« aujourd'hui compris » — et cela ne change aucun chiffre, les trois
opérateurs y étant.

**C'est la seule table du projet qui RETIRE quelque chose**, d'où son nom à
elle. La confondre avec `RENFORT_TRANCHE`, qui ne sait qu'ajouter, ferait
disparaître un renfort réel le jour où l'on s'y tromperait.

Mesuré : les journées avec un manque passent de 190 à **189** sur l'année,
les places creuses restent à **385** — le 16/09 en ajoute deux, le 29/09 en
retire autant une fois le rééquilibrage refait. **D'ici la fin de l'année,
retour à 8 journées**, et le 29/09 a bien disparu des pastilles « Postes en
manque » — vérifié au navigateur à 390 et 1280 px.

`renfortDuJour()` est mémoïsée par journée : elle balaie les 77 colonnes, et
`postesDePause()` l'appelle trois fois par jour. Elle entre dans la découpe
du vérificateur avec ses trois constantes — sans quoi l'outil aurait rejoué
un `attenduAuPoste()` qui ne sait plus lire son troisième argument.

### Le vocabulaire de la maison : « absence » veut dire MALADIE

Le client, le 25/09/2026 : « attention que chez nous "Absence" veut dire
maladie ; quand c'est une prise de congé on dit "Congé" ».

C'est la même distinction qu'il avait donnée le 21/09 pour l'onglet Équipe —
« il faut différencier absent et en congé ; les absents ne sont que les
personnes malades » — mais elle ne valait que pour les CARTES du Résumé. Le
reste de l'application appelait encore « absence » tout ce qui n'est pas
presté.

**Et un endroit ne se contentait pas d'un mot de travers : il disait le
contraire du code.** La légende rangeait `ABS` dans la colonne « Compteurs
et NON PAYÉ », avec la définition « absence injustifiée ». Or
`ALIAS_HORAIRE={"ABS":"MAL"}` le traduit en `MAL`, qui est `{c:"MAL",
k:"SMG"}` — **maladie, salaire garanti**. Le code avait raison depuis le
début ; c'est la légende qui mentait, et dans le sens qui coûte cher. `ABS`
est passé dans la liste des journées PAYÉES, à côté de `SMG`.

Sept autres emplois du mot sont repris dans son vocabulaire :

| Où | Avant | Après |
|---|---|---|
| légende de l'année | Absence | **Congé ou maladie** |
| légende du mois | absence — non presté | **congé ou maladie — non presté** |
| compteurs | Absences de l'année | **Congés et maladie de l'année** |
| liste des codes | Absences payées | **Congés et maladie payés** |
| son sous-titre | postes, absences et primes | **postes, congés, maladie et primes** |
| aide de la ligne | le menu pose une absence | **pose un congé ou une maladie** |
| infobulle de l'année | « Absence » + le code | **le code seul** — il se suffit |

**Deux libellés restent « absence », et c'est voulu** : « heures d'absence
assimilées à du travail » et « absence non rémunérée » sont les intitulés de
la FICHE DE PAIE du secrétariat social. Ils recopient un document, pas le
parler de l'usine — les renommer ferait perdre la correspondance ligne à
ligne avec la fiche, qui est tout l'objet de l'onglet Contrôle.

### Le relais de la fermentation se fait tout seul, et le doublon est voulu

Le client, le 25/09/2026 : « CHD arrive dans l'équipe 5 ce lundi et
remplacement LCI à partir de là ».

**Rien n'a été codé pour cela**, et il ne fallait rien coder : deux
mécanismes indépendants s'accordent déjà.

Le CLASSEUR porte l'arrivée de CHD — il ne rejoint pas l'entreprise, il
change d'équipe, de la 4 vers la 5. Sa rotation ne coïncide avec celle de
l'équipe 5 que **1 à 5 journées par mois de janvier à septembre, puis 26 en
octobre** ; il est en repos les 25, 26 et 27, et **le lundi 28 il tombe
exactement sur elle**. Sa ligne 9 dit déjà « Shift5 → Fermentation ».

`POSTE_PERIODE` fait sortir LCI de la fermentation le 30/09. Le relais se
lit donc de lui-même :

| Jour | Fermentation éq. 5 |
|---|---|
| 25 au 27/09 | LCI seul, au matin |
| **lundi 28/09** | **CHD et LCI ensemble**, en après-midi |
| mardi 29/09 | CHD en après-midi, LCI en nuit |
| mercredi 30/09 | CHD seul — LCI passe en distillation |

**Le doublon du 28 et du 29 n'est pas un défaut, c'est le tuilage** : deux
journées où le partant et l'arrivant tiennent le poste ensemble. Ne pas le
« corriger » en croyant qu'une place unique a été violée — la règle d'une
place par personne porte sur la COMPOSITION, pas sur le nombre de personnes
à un poste un jour donné.

### Ces semaines-ci sont exceptionnelles

Le client, le 25/09/2026 : « ces semaines-ci c'est exceptionnel mais il y a
une transition des postes de certains opérateurs ; tout devrait rentrer
dans l'ordre dans les semaines qui viennent mais il se peut qu'il y ait des
trous ces semaines-ci ».

**À lire avant de courir après les manques d'effectif de septembre et
d'octobre.** Les trous qui restent ne sont pas tous des défauts de lecture :
une partie est la réalité du terrain pendant la transition. C'est aussi ce
qui explique `POSTE_PERIODE` — un poste qui change à une date n'est pas une
bizarrerie du classeur, c'est cette transition-là.

### Une absence qui finit aujourd'hui le dit

Le client, le 23/09/2026 : « pourquoi pas de durée pour la maladie de
GJR ? » — parce que le 23/09 était le DERNIER jour de sa série, et que le
rendu se taisait au lieu de le dire. `finAbsence()` rend la dernière journée
de la série ; quand il n'y en a pas au-delà d'aujourd'hui, elle rend `null`,
et la pastille n'écrivait rien.

« MAL » tout seul ne disait pas si l'absence s'arrête là ou si on ne sait
pas jusqu'à quand. Elle écrit maintenant **« MAL · dernier jour »**, ce qui
est une information et non un vide — GJR est « Abs » du 15 au 23/09, en
repos du 24 au 27, et reprend le 28.

**Les malades se lisent du retour le plus proche au plus lointain.** Le
client, le 26/09/2026 : « les absents maladie doivent être triés par dates
de retour (le plus court au plus long) ». Le tri se fait au RENDU de la
carte « Hors poste », qui retriait chaque groupe par catégorie et
trigramme — un tri posé dans `equipeDuJour()` s'y faisait défaire, et la
première version l'a montré au navigateur : huit malades dans le désordre.
Une série qui finit aujourd'hui (« dernier jour ») vient en tête ; à date
égale, l'ordre habituel. Congés et repos gardent le leur. Vérifié à 390 et
1280 px, hors ligne compris : 27/09, 27/09, 30/09, 11/10 … 27/12.

**Et la pastille dit « Absent jusqu'au 27 Septembre »**, et non plus « MAL ·
jusqu'au 27 sept. ». Le client, le 26/09/2026 : « au lieu de MAL, il faut
indiquer Absent jusqu'au 27 Septembre ». Chez nous absent veut dire malade :
le code n'ajoutait rien. Le dernier jour s'écrit « Absent jusqu'à
aujourd'hui ». Les congés gardent leur code (« RJF · dernier jour »), qui
dit lequel. **À 320 px la phrase sortait de la carte** : la règle qui la
laisse passer à la ligne sur téléphone était écrite AVANT celle qui
l'interdit, et perdait à spécificité égale — le piège de la requête média,
une quatrième fois. Elle est posée après ; le jour et le mois sont liés par
une espace insécable pour ne pas se séparer.

**Les congés n'avaient pas de fin, et disaient tous « dernier jour ».** Le
client, le 26/09/2026 : « pourquoi ceux en congé sont indiqués dernier
jour ? ». Ce jour-là c'était vrai pour les trois — un seul jour chacun —,
mais par hasard : `equipeDuJour()` ne calculait la fin que pour la maladie,
et la pastille d'un congé écrivait « dernier jour » sur n'importe quelle
journée, le premier jour de trois semaines compris. `finAbsence()` reçoit
désormais la famille `"CONGE"`, qui **enchaîne tous les congés d'une
journée entière** : JBI en VA le 20/04 puis en RJF le 21/04 reprend le 22, et
s'arrêter au changement de code aurait redit « dernier jour » le 20. La
maladie reste sa propre famille. Vérifié horloge au 20/04 : LCI « VA ·
jusqu'au 22 avr. », JBI « jusqu'au 21 avr. », CKS seul en « dernier jour » ;
les quatre sorties du vérificateur identiques à l'octet.

**Puis jusqu'à la reprise du travail, repos compris.** Le client, le même
jour, devant LDY — RJF le 30/09, RHS le 01/10, trois repos, RJF, RJF, VA,
quatre repos, premier poste le 12/10 : « jusqu'à la reprise du travail ».
La série « CONGE » court donc sur tout congé d'une journée entière ET tout
repos, et s'arrête à la première journée prestée, à une maladie ou à un
poste prévu non presté. Une journée entière de flex time repris (« 8h
-FT ») compte comme un congé : ses heures sont payées mais personne ne
vient — LHR le 26/09 reprend le 28, pas le 27. La pastille dit donc la
REPRISE : « RJF · reprise le 12 oct. », « · reprise demain ». « Jusqu'au
dimanche » se serait moins bien lu que « reprise le lundi ». La maladie ne
bouge pas : « Absent jusqu'au » son dernier jour de maladie. Vérifié au
30/09 (LDY reprise le 12 oct., 15 congés datés) et au 20/04 (FLN, TP puis
VA entrecoupés de repos, reprise le 13 mai — contrôlé jour par jour) ;
sorties du vérificateur identiques à l'octet.

**Congé et repos ne font plus qu'une ligne, triée par reprise.** Le client,
le 26/09/2026 : « repos et congés doivent être mélangés car les repos aussi
ont une reprise ». Dans « Hors poste », on cherche QUAND chacun revient ;
congé ou repos ne change pas la question. Chaque repos reçoit sa date de
reprise par la même série « CONGE », et la ligne « Congé et repos » se trie
du retour le plus proche au plus lointain : « NRD RJF · reprise demain »,
« AFA Repos · reprise le 28 sept. » … « ATA Repos · reprise le 10 oct. ».
Restent sans date, en fin de ligne : le poste prévu non presté (« AM
prévu ») et la personne dont la colonne est vide ce jour-là — pas encore
arrivée. **Le calcul se fait au rendu, pas dans `equipeDuJour()`** : le
module des manques la rejoue sur des mois, et une trentaine de séries par
jour y coûterait pour rien. `par.off` est inchangé, de sorte que la barre
du haut dit toujours « Repos ». Vérifié au 26/09 et au 20/04, à 320, 390
et 1280 px, hors ligne compris ; neuf règles et `--manques` identiques.

**Puis regroupés par date.** Le client, le 26/09/2026, devant sa capture —
dix-neuf lignes « Repos · reprise le 28 sept. » d'affilée : « penses-tu qu'il
faut regrouper les noms par date ? », puis « optimise au mieux ce cadre-là
avec absences et personnes en congé ». Les deux lignes, Absents et Congé et
repos, se lisent désormais par DATE : une colonne étroite porte « Dim.
27 sept. », « Demain », « Lun. 28 sept. », et les trigrammes se rangent à
côté. « jusqu'au » et « reprise le » ne s'écrivent qu'une fois, sous
l'intitulé de la ligne. Le trigramme ne garde que ce que la date ne dit
pas : le code d'un congé (RJF, VA, RHS, « AM prévu ») — rien pour un repos
ni pour une maladie ; l'infobulle garde la phrase entière. **Le cadre passe
de 906 à 594 px de haut à 390 px** (34 lignes de congés et repos en font
onze). Sous 380 px la date passe au-dessus de ses trigrammes : à côté, elle
leur laissait 20 px et ils s'empilaient un par ligne — **une première
tentative, sortir l'intitulé de la ligne au-dessus des dates, a échoué** :
la table garde ses largeurs de colonnes. 930 px à 320 px, rien ne déborde à
320, 390 et 1280 px, hors ligne compris.

**Deux cadres à eux, et plus aucun code.** Le client, le même jour : « peut-être
pas utile de marquer le type de repos vu que tout est mélangé et que le
cadre a déjà le nom de congé et repos ; pareil pour les absents ; je veux
également séparer les deux cadres ». « Absents » (maladie · jusqu'au) et
« Congé et repos » (date de reprise) sont deux cartes, avec leur compte dans
le titre ; « Hors poste » ne garde que ce qui reste — la ligne Jour. Sous
chaque date, les trigrammes seuls : le code (RJF, VA, « AM prévu ») ne vit
plus que dans l'infobulle. Sorties du tableau, les dates gagnent la largeur
de l'intitulé et du compte : **à 320 px elles tiennent à côté de leurs
trigrammes**, et la règle qui les mettait dessus sous 380 px est partie.
390 px : Absents 236 px, Congé et repos 345 px ; rien ne déborde à 320, 390
et 1280 px, hors ligne compris.

**Puis en tuiles.** Le client, le 26/09/2026, capture à l'appui — prise sur
la version d'AVANT les deux cadres, que son téléphone n'avait pas encore
reçue : « il y a moyen de mieux organiser ça pour que cela fasse moins vide
et mieux réparti ». En lignes, une date à une personne laissait les trois
quarts de la largeur vides. Chaque date est désormais une TUILE — la date
en haut, les trigrammes dessous —, en grille de cases d'au moins 96 px :
trois côte à côte à 390 px, deux à 320. La largeur suit le nombre de
personnes : une ou deux, une case ; trois ou quatre, deux cases ; au-delà,
la ligne entière. `grid-auto-flow: dense` comble les trous avec les petites
tuiles — ce qui plaçait une date avant une plus proche (le 29/09 avant le
28/09). **Le client l'a vu aussitôt** : « ce n'est plus vraiment par ordre
chronologique ». La grille est devenue une RANGÉE QUI S'ENROULE : chaque
tuile prend la largeur de ses trigrammes, dans l'ordre strict des dates, et
s'élargit pour finir sa ligne — ni trou, ni date déplacée. Les « une,
deux ou toute la ligne » selon le nombre de personnes sont partis avec la
grille : c'est le contenu qui décide. Vérifié en clair et en sombre, à
320, 390 et 1280 px, hors ligne compris.

**Puis dans le style des sous-effectifs.** Le client, le 28/09/2026 :
« présenter dans le même style les absents et personnes en congé ». Les
tuiles cèdent la place à des rangées séparées d'un filet : la date à
gauche, écrite comme aux sous-effectifs (« MAR. 29 SEPT. »), les
trigrammes en étiquettes à droite ; la personne choisie a le bord et le
trigramme à l'accent. **La date tient sur une ligne, et non en bloc** : le
bloc de trois lignes des sous-effectifs, essayé d'abord, montait les deux
cartes à 1 300 px pour vingt dates d'un trigramme — 789 px ainsi à 390 px.
Rien ne déborde à 320 (hors ligne), 390 et 1280 px, en clair et en sombre.

**Les dates proches en mots, et une coupure par semaine.** Le client, le
28/09/2026, parmi quatre pistes proposées : « A et C ». Dans les deux
cartes, « Aujourd'hui », « Demain », puis le jour seul (« Mercredi »)
jusqu'à six jours ; au-delà, la date comme avant, et l'infobulle de la
rangée garde toujours la date complète. Des intertitres « Cette semaine »,
« Semaine prochaine », « Plus tard » coupent la liste, la semaine allant du
lundi au dimanche autour du jour de l'usine. Les deux pistes écartées :
replier la suite (B) et mettre sa propre équipe en tête (D). 923 px à
390 px ; rien ne déborde à 320 (hors ligne), 390 et 1280 px, en clair et
en sombre ; vérificateur identique à l'octet.

**Et la date quand même.** Le client, le même jour : « quand même indiquer
la date ? ». « Mercredi » seul obligeait à compter les jours : le mot reste
en gras, et « 30 sept. » s'écrit en petit dessous. 965 px à 390 px.
Puis, « moyen d'uniformiser » : la même forme pour TOUTES les rangées,
« Mardi / 6 oct. » au lieu de « MAR. 6 OCT. » au-delà de six jours —
l'intertitre de semaine dit déjà si c'est proche. 1 026 px à 390 px.

**Et les sous-effectifs aussi** (« ça aussi même style ? ») : mêmes
intertitres de semaine, même date en deux lignes. La mise en forme vit
dans UNE fonction, `dateEnMots()`, que les trois cadres appellent — deux
copies d'une même règle divergent. Sous 380 px, « Terrain arrière »
devient « T. arrière » dans les sous-effectifs, qui sinon se coupait.
Vérifié à 320 (hors ligne), 390 et 1280 px, en clair et en sombre ;
vérificateur identique à l'octet. Puis le mois en entier sous le jour
(« 30 septembre ») : « il y a la place » — et c'est mesuré, il tient dans
la colonne de date des trois cadres jusqu'à 320 px.

**Trois retouches aux sous-effectifs** (le client, le 28/09/2026, « go »
sur trois pistes proposées) : l'étiquette « Remplaçants possibles » part,
une flèche « → » précède les noms — le 05/10 tient de nouveau sur une
ligne ; « Aucun remplaçant » devient une étiquette rouge pâle, de la forme
des étiquettes de noms, parce que c'est l'information la plus urgente ;
l'équipe passe sous la date, en gras, quand tous les manques du jour sont
de la même équipe (toutes les journées au 28/09) — sinon chaque fiche
garde la sienne. Libérée de l'équipe, la ligne du poste écrit « Terrain
arrière » en entier même à 320 px. Piste écartée : supprimer la barre de
repli « 7 journées ». Vérifié en clair et en sombre, à 320 (hors ligne),
390 et 1280 px ; vérificateur identique à l'octet.

**Puis la barre de repli part, et les trois cadres s'alignent.** Le
client, le même jour : « retire-la et regarde si rien ne peut être mieux
placé ou aligné ». Le compte (« 7 journées ») passe sous le titre, comme
celui de « Équipes du jour » ; `#mqFold`, son écouteur et la clé
`ui/mqFold` sont retirés. Les cadres rognent leurs coins (`overflow:hidden`)
pour que l'intertitre de semaine, désormais tout en haut, n'en dépasse pas.
La colonne de date fait la même largeur dans les trois (84 px, 72 sous
380 px) : mesuré, les dates commencent au même pixel et le contenu aussi
(33 et 127 px à 390 px, 33 et 111 à 320). Le cadre passe de 640 à 603 px.

**Trois accolades orphelines dans la feuille**, dont deux d'avant ce
changement : un « } » seul au niveau de la feuille avale la règle qui le
suit (ici `.eqfold>summary`, que plus rien n'emploie). Retirées ; la
feuille est équilibrée, ce qu'un petit compteur d'accolades vérifie en
une ligne — à relancer après toute découpe de CSS.

**Puis sous « Équipes du jour ».** Le client, le 28/09/2026 : « on peut
mettre les postes en sous-effectif sous les équipes du jour ». L'onglet se
lit désormais : Mon prochain poste, Équipes du jour (le tableau, les absents, les congés
et les repos), Postes en sous-effectif. Le bloc est placé APRÈS les deux cadres
Absents et Congé et repos, et non entre eux et le tableau : ils font partie
de la même section, qu'il ne faut pas couper. **Le clic sur une journée
remonte désormais**, et la barre du haut se redéplie en remontant : viser
`#eqCorps` avec `scrollIntoView` la laissait passer PAR-DESSUS la barre du
jour (−34 px mesurés). Le clic vise donc la barre du jour, décalée de la
hauteur de l'en-tête. Mesuré : elle arrive à 76 px du haut sous une barre
de 57 px (390 px), à 117 sous 98 (1280 px). Vérifié à 320 (hors ligne),
390 et 1280 px ; neuf règles à zéro.

**Les deux cadres disent AUJOURD'HUI, quel que soit le jour affiché.** Le
client, le 28/09/2026 : « il ne faut pas que les listes absent/congé soient
adaptées par rapport à la date sélectionnée mais par rapport à la date du
jour ». Il avait cliqué sur le sous-effectif du 16/10 et lu YBT « en congé,
reprise le 22 oct. », alors qu'il est malade jusqu'au 11/10 : c'était juste
pour le 16/10, mais on ouvre ces cadres pour savoir qui manque MAINTENANT.
Le tableau suit le jour choisi ; les deux cadres se calculent sur
`jourUsine()` (le jour de l'usine, qui change à 6 h), par un second
`equipeDuJour()` seulement quand le jour affiché est un autre. Leur
sous-titre commence alors par « aujourd'hui · ». **J'ai d'abord cru que
l'application se trompait sur YBT** : la barre du haut, toujours datée du
jour, laissait croire que la capture montrait le 28/09. Vérifié en avançant
au 16/10 à 320 (hors ligne), 390 et 1280 px : les cadres ne bougent pas ;
les quatre sorties du vérificateur sont identiques à l'octet.

**Le premier cadre du Résumé dit le poste SUIVANT, jamais celui du jour.**
Le client, le même jour : « est-ce utile de remettre la pause du jour vu
qu'elle est dans la barre du haut ? ». Non : les jours travaillés, ce
cadre écrivait « Aujourd'hui · nuit » sous une barre qui disait déjà
« Contremaître · Nuit ». `majProchain()` part donc de DEMAIN. Et il
s'arrêtait au dernier jour du mois affiché — le 30/09, « plus de poste d'ici
la fin du mois » quand le prochain est le 5 octobre : il lit désormais la
suite dans `HORAIRE_DB`, par `moisDe()` et `lireJournee()`, la lecture du
calendrier. Vérifié horloge au 26, 28 et 30/09 : « lundi 28 », « demain »,
« lundi 5 octobre », hors ligne compris.

### Le Résumé en trois sections, et la journée dans le tableau

Le client, le 26/09/2026 : « réorganise le premier onglet avec des titres
et logique d'affichage ; et comment intégrer les personnes en D dans
l'horaire ? ». Trois titres hors cadre (`.pvtete`, comme Équipe et Mon
horaire), dans l'ordre des questions qu'on se pose en ouvrant
l'application :

1. **Mon prochain poste** : le cadre commence par le jour
   (« Demain · jour · 8 h »), puisque le titre dit déjà ce que c'est ;
2. **À venir** : les postes en manque ;
3. **À l'usine** : qui travaille, les absents, congé et repos. Sous le
   titre, le compte (« 35 personnes en poste · 77 au total »).

**Puis un étage de titres en moins.** Le client, le même jour, capture à
l'appui : « comment mieux présenter ceci ? ». Trois titres se suivaient
avant la première ligne du tableau : celui de la section, « Qui
travaille », puis la date du jour. Le cadre n'a plus d'en-tête : la barre
du jour sert de titre. Et le titre de la section ne répète plus la date.
Une première version écrivait « Aujourd'hui à l'usine » ou « L'usine le
lundi 28 septembre », juste au-dessus d'une barre qui disait la même
chose. Sont aussi partis : le mot « Poste » au-dessus de la colonne des
postes (elle se lit seule), « horaire variable » sous « En journée », et
la légende des zones. Le liseré de couleur regroupe des lignes qui portent
déjà leur nom : sa légende prenait deux lignes sous le tableau sans rien
apprendre. `ZONE_NOMS` et les styles `.lg-z` sont retirés avec elle. Rien
ne déborde à 320, 390 et 1280 px, hors ligne compris. Les quatre sorties du
vérificateur sont identiques à l'octet.

**« Mon prochain poste n'est plus affiché. »** Le client, le même jour. Le
défaut date de la première version du cadre, pas de la réorganisation :
`majProchain()` se cachait dès que le mois affiché n'était pas celui du
jour. Or le mois se choisit dans Mon horaire et Mon salaire, et on revient
au Résumé en gardant ce choix. Il suffisait d'avoir regardé octobre dans
Mon salaire pour trouver un cadre vide sous son titre. Reproduit
au navigateur : mois suivant, retour au Résumé, cadre caché. Le cadre part
désormais d'AUJOURD'HUI. Il lit le mois enregistré quand le jour en fait
partie (on garde ainsi les corrections faites à la main), sinon le
classeur, avec la même lecture que le calendrier. Tant que l'horaire n'est
pas chargé, il ne dit rien plutôt que « plus de poste ». **Un premier test a
cru montrer une erreur chez LCI** : il changeait de catégorie en boucle, et
les pré-remplissages en cours écrasaient la personne choisie. Refait
avec une seule sélection : « Demain · matin », ce que dit sa cellule du
27/09.

**Le tableau perd 18 % de sa hauteur sans rien perdre.** Même demande :
« penses-tu pouvoir optimiser l'affichage de ce tableau ? ». Les trigrammes
restent l'un sous l'autre, comme le client l'a demandé le 22/09. Mais
chacun prenait une ligne de 18 px pour un corps de 10,5 px : l'interligne
passe à 14 px, et les cases perdent deux pixels de marge. La légende tient
sur une ligne (« en formation », « aucun effectif attendu »). À 390 px, le
tableau passe de 470 à 386 px et le cadre de 585 à 482 px. Les règles
portent `#eqCorps` en tête : elles battent les règles de téléphone par la
spécificité, quel que soit leur ordre dans la feuille.

### Les pauses se disent AM, PM, N et D

Le client, le 26/09/2026 : « il faut parler en AM PM N D au lieu du nom de
la pause complet ». C'est ce qu'écrit le classeur, et ce qu'on dit à
l'usine. Les deux tables de libellés passent aux codes : `EQ_GROUPES` (le
tableau du jour, la barre du haut) et `POSTE_LIB` (le calendrier, sa
légende, les infobulles, le prochain poste). Les `toLowerCase()` qui les
suivaient sont retirés : ils auraient écrit « am ». La barre du haut dit
donc désormais « Fermentation · AM » ou « D », et plus « Contremaître ·
Nuit » comme le montrent les exemples plus haut dans ce fichier. **Restent
en toutes lettres, et c'est voulu : les lignes de fiche de paie**
(`SHIFT_NOMS`, « Suppl. Équipe Nuit »). Elles recopient le secrétariat
social, et l'onglet Contrôle se lit ligne à ligne contre la fiche.

Le prochain poste ne répète plus la pause dans son texte : la pastille la
porte. On lit « [AM] Demain · 8 h ».

**Noms de poste courts sur téléphone** (le client a choisi l'option B) :
« CM », « Adj. », « Meun. », « Glut. », « Ferm. », « T. arr. », « Dist. »,
« Chaud. » et « STEP », avec les noms
complets au-delà de 760 px. Le mécanisme est celui de l'onglet Équipe,
`.orgl1` / `.orgl2`. La colonne passe de 122 à 62 px, et chaque pause de
78 à 98 px. Cette largeur sert à la lisibilité : les trigrammes passent de
10,5 à 12 px, pour un tableau de 396 px (386 avant, 470 ce matin). La
ligne de la journée s'appelle « D ». Rien ne déborde à 320, 390 et
1280 px, hors ligne compris. Les quatre sorties du vérificateur sont
identiques à l'octet : ses sorties parlent en codes depuis toujours.

### La journée est une colonne, et un flex time complet n'est pas une présence

Le client, le 26/09/2026 : « une colonne D entre AM et PM ; par contre
cette nuit, comment ça se fait deux personnes comme CM ? ».

**La colonne D** remplace la ligne « D » posée une heure plus tôt. L'ordre
suit les heures d'arrivée : AM, D, PM puis N ; chacun y est rangé à son poste,
par le même `postesDePause()` que les trois pauses. Aucun effectif n'y est
attendu (`attenduAuPoste()` rend zéro pour D) : une case vide y est un
tiret, jamais un manque. Cinq colonnes tiennent à 320 px sans déborder. À
390 px, chaque pause fait 74 px et le tableau 352 px.

**Deux contremaîtres de nuit le 26/09 : YPE et FPA.** YPE porte
`["N","8h -FT","Remplacé par VGG"]` : une journée entière de flex time
repris. FPA porte `["R-CM","3h -FT","Remplace YPE …"]`. `equipeDuJour()`
rangeait à sa pause quiconque avait des heures. Or les 8 h de YPE sont
PAYÉES depuis le compteur (section 6 de `docs/conversion-horaire.md`),
sans qu'il soit présent. PDR, `["N","8h -FT","rempl par ALZ"]`, était
compté deux fois de la même façon en distillation. C'est la règle déjà
posée pour le chèque-repas et pour la date de reprise : **seules les heures
PRÉSENTES comptent**. Une reprise d'une journée entière passe donc dans
« Congé et repos », avec sa date de reprise. Une reprise partielle
(« 3h -FT ») laisse la personne à son poste.

Mesuré : neuf règles, compteurs et `--manques 0926` **identiques à
l'octet** (rien ne change d'ici la fin de l'année). Sur l'année entière,
les places creuses passent de **245 à 264** et les journées en manque de
159 à 172, dont **+10 chez les contremaîtres** : autant de journées passées
où l'absent comptait comme présent. Dans les journées de contremaître en
flex time complet, le remplaçant est presque toujours nommé. Quand un trou
apparaît, le remplaçant n'est pas dans l'horaire (« remplacé par PBL »,
absent des 77) ou n'est pas nommé du tout. Recyclage : 23 → **22** couples
au quota (CDE chaudières 10 → 9), et une dizaine de cases bougent d'une
journée.

### Le tableau du jour : gras, « (F) », une colonne blanche

Le client, le 26/09/2026, capture à l'appui : « le poste de la personne
sélectionnée ne doit pas être souligné mais peut être en gras ; supprimer
la légende des gens en formation mais indiquer (F) à côté du trigramme ».

- **La personne choisie** se lit en gras (800), dans la couleur d'accent,
  sans soulignement.
- **« (F) » remplace le jaune expliqué par une légende**, et il suit le
  POSTE, pas la catégorie. La capture montrait LCI en jaune à la
  fermentation, qu'il tient validé jusqu'au 29/09. Le tableau testait
  `enFormation()`, qui ne regarde que la catégorie. Il teste désormais
  `compteAuPoste()`, la règle même de l'effectif, avec le jour affiché.
  C'est ce que la composition fait depuis le 25/09 (« le jaune suit le
  poste ») : les deux vues disent maintenant la même chose. Le 26/09, SKS
  (meunerie), SVE (distillation) et MGY (chaudières) portent « (F) », et
  LCI non.
- **La colonne D reste blanche** là où personne n'est en journée : un
  tiret sur chaque ligne en faisait une colonne de traits, pour un poste
  qui n'attend jamais personne.
- **La légende du tiret part aussi** : il ne reste de tirets qu'à l'adjoint
  et à la STEP hors matin, qui se lisent seuls. La légende du manque
  reste, les jours où un manque est dessiné.

Le cadre passe de 448 à 413 px à 390 px. Neuf règles, manques, compteurs
et Recyclage identiques à l'octet ; rien ne déborde à 320, 390 et
1280 px, hors ligne compris.

**Puis les quatre pistes, toutes** (le client : « go tout ») :

1. **la barre du jour s'affine** : boutons de 30 px au lieu de 34, marges de
   7 px au lieu de 12, « Aujourd'hui » en petit. Elle passe de 59 à 45 px ;
2. **plus de « 10 pers. » sous les pauses** : le total est sous « À
   l'usine », et un effectif se compte en trigrammes. L'horaire de la pause
   reste au bureau. L'en-tête passe de 45 à 31 px ;
3. **la colonne D n'apparaît que les jours où quelqu'un est en journée**.
   C'était déjà le cas depuis qu'elle existe (une pause vide n'a pas de
   colonne), et c'est vérifié : les samedis et dimanches 3-4 et 10-11/10,
   le tableau revient à AM, PM, N ;
4. **la couleur range l'ordre de lecture** : les intitulés de poste passent
   de `--faint` à `--muted`, les tirets à 45 % d'opacité. Un tiret dit
   « rien à voir ici » et ne doit pas peser autant qu'un trigramme.

Le cadre passe de 413 à **385 px** à 390 px de large. Neuf règles, manques,
compteurs et Recyclage identiques à l'octet ; rien ne déborde à 320, 390 et
1280 px, en clair et en sombre, hors ligne compris.

**Des traits visibles, et des lignes de même hauteur.** Le client, le même
soir, capture à l'appui : « les lignes ne sont plus assez visibles ; il
faut également des hauteurs fixes de même taille pour chaque ligne ».
Deux jetons de thème, `--trait` (entre deux postes) et `--trait-fort`
(entre deux zones et sous l'en-tête), déclarés dans les trois blocs,
clair, sombre automatique et sombre forcé. Ils remplacent `--line2`, qui
se confondait avec le fond des cartes. Pour la hauteur, un tableau
n'égalise pas ses lignes de lui-même : le rendu compte la case la plus
pleine du jour (`maxLig`, avec le compte d'un manque et les lignes « à
déterminer » et « Formation ») et pose `--eqh = 12 + 16 × maxLig` px sur
chaque ligne. Le 26/09, trois trigrammes aux chaudières donnent 60 px
partout. **Ce choix coûte de la hauteur** : le cadre passe de 385 à 619 px
à 390 px de large. Le client, à qui le coût a été montré avec trois autres
options : « tout », c'est-à-dire telle quelle. Neuf règles, manques,
compteurs et Recyclage identiques à l'octet ; rien ne déborde, hors ligne
compris.

**Puis corrigé dans le même soir**, sur quatre points :

- **hauteur de deux trigrammes pour toutes les lignes**, et seule une case
  plus pleine fait grandir la sienne. Le client : « comme celle où il y
  avait 2 trigrammes pour toutes les lignes, sauf celles de plus de 2 ».
  Une hauteur de ligne de tableau est un minimum : `height:44px` sur
  chaque ligne suffit, et le calcul `maxLig` / `--eqh` est retiré. Le 26/09,
  toutes les lignes font 44 px et les chaudières 60. Le cadre passe de 619
  à 491 px ;
- **le liseré de zone sur le bord des postes était parti, par ma faute** :
  la règle des traits visibles, `#eqCorps .eqp2 th, td{border-left-color}`,
  battait par sa spécificité les couleurs `tr[data-z] th.eqposte`. Elle
  ne vise plus que les cases et l'en-tête ;
- **le zébra vaut pour toutes les cases**, colonne D et tirets compris.
  Les tirets avaient leur propre fond, et l'opacité à 45 % pâlissait aussi
  ce fond : ils s'éclaircissent désormais par leur couleur (`--trait-fort`) ;
- **les postes s'écrivent comme AM, PM, N** (12 px, graisse 650, encre
  principale, sans capitales), au centre de leur colonne.

Neuf règles, manques, compteurs et Recyclage identiques à l'octet ; rien
ne déborde, hors ligne compris.

**Et trois retouches encore** (le client, le même soir) : sur téléphone,
les postes s'écrivent en trois capitales — « CM », « ADJ », « MEU »,
« GLU », « FER », « TER », « DIS », « CHA », « STEP » — ; les trigrammes
passent en graisse normale, seule la personne choisie restant en gras ; et
le zébra s'adoucit. Le jeton `--zebre` vaut, en sombre, le milieu entre la
carte et l'ancien `--surface2` (`#1C2130`). En clair il garde la valeur
d'avant, déjà très légère. Neuf règles, manques, compteurs et Recyclage
identiques ; rien ne déborde, hors ligne compris.

**Et quatre derniers réglages** (le client, le même soir) : plus de
couleur au-dessus des pauses ; le trait sous l'en-tête est le même que
celui sous ADJ ; les tirets reviennent dans les cases vides de la colonne
D, que le client avait d'abord voulues blanches ; « Aujourd'hui » a la
hauteur des flèches (30 px). Le trait sous l'en-tête paraissait plus
épais **parce qu'il était double** : la première ligne ouvre une zone et
portait son propre trait de 2 px, qui s'ajoutait aux 2 px de l'en-tête.
Elle n'en porte plus. Neuf règles, manques, compteurs et Recyclage
identiques ; rien ne déborde, hors ligne compris.

**Plus aucune légende, et la formation s'écrit comme un poste** (le
client, le même soir) : « il ne faut jamais de légende, même pour les
postes en sous-effectif ». Le compte écrit dans la case (« 1/2 ») se lit
seul, et la construction de la légende est retirée avec son drapeau
`aManque`. La ligne formation quitte le style italique et grisé de
« À déterminer » (`eqinc`) pour sa propre classe, `eqform`. Elle
s'écrit « Formation » au bureau et « FORM » sur téléphone, en 12 px et
en graisse 650, comme les postes. Son liseré gauche prend l'encre
principale : blanc en sombre, presque noir en clair, où du blanc ne se
verrait pas sur la carte. Le coin vide au-dessus des postes perd son
trait de 3 px en haut et son liseré gauche. Vérifié le 27/09 (un manque,
aucune légende) et le 28/09 (ligne FORM) ; neuf règles, manques,
compteurs et Recyclage identiques à l'octet ; rien ne déborde à 320, 390
et 1280 px, hors ligne compris.

**La colonne D dit l'horaire quand le classeur l'écrit.** Le client, le
26/09/2026 : « il y a des gens qui font D (6-14), il faut les mettre dans
la colonne 6-14 ; les autres en D, préciser 7-15 ou H. flot. », puis « D
seul laisser rien ». Le D seul de YRS et BLR est un 7h30-16h, les jours où
ils sont consignateurs ; GSK l'a fait le temps de sa reprise après une
longue absence ; les opérateurs en formation commencent tous par des D
avant de passer en pause au poste. Aucun de ces D ne s'écrit.

- **« 7-15 », « H. flot. » ou « 6-14 »** à côté du trigramme, en petit,
  quand la cellule ou l'annotation porte 7h-15h, « H. flott. » ou 6h-14h
  (`horaireEcritD()`, lu dans le classeur du jour). Toute autre plage :
  rien. Le 6-14 ne s'écrit jamais avec un code de jour : dans
  `["6h-14h","F"]`, `D-F`, `DS-CE` ou `D-CPPT`, la plage n'est que le poste
  prévu (GDT le 14/10, « formation anglais sur site 8h-11h »).
- **Un D écrit 6h-14h reste dans la colonne D.** Une première version le
  passait en AM, dans `equipeDuJour()`. Elle déplaçait d'abord aussi vingt
  journées de formation ou de réunion, ce que le journal des déplacements
  a montré avant le commit. Restreinte à SKS les 5, 6 et 7/10
  (`["6h-14h","D"]`), elle a été poussée en v269 : SKS comblait la
  fermentation du 05/10. Le client, aussitôt : « je préfère laisser les
  gens prévus en D (6-14) dans la colonne D mais préciser à côté leurs
  horaires ». La règle est retirée en v271, et SKS porte « 6-14 ».

**Puis entre parenthèses, et toujours** (le client, le même jour : « il
doit toujours être marqué l'horaire de quelqu'un en D ; cet horaire doit
être en () ; si BLR ou YRS est en D, il faut mettre (C) à côté de lui
pour Consignation »). L'ordre : (C) pour `CONSIGNATEURS` ; (H. flot.) ;
la plage écrite dans l'annotation ou la cellule, quelle qu'elle soit
(« (7-15) », « (6-14) », « (8-12) ») ; sinon celle que le commentaire
écrit avec un tiret (DWS le 28/09, « (8h30-16h30) »). « De 10h à 14h »
dans un commentaire dit un remplacement partiel et ne compte pas. Avec un
code de jour, seule une plage de journée compte. **Reste le D seul sans
aucune heure écrite** : 103 journées d'ici la fin de l'année chez 19
personnes (YBT 15, NPI 14, FPS 9, MGY 9, FLI 8…). La question est posée
au client, et rien n'y est écrit en attendant.

**Pas d'horaire sur la ligne FORMATION, un horaire pour tous les autres.**
Le client, le 28/09/2026. La ligne FORMATION n'écrit plus de parenthèses
(`chip(…, sansHoraire)`) ; mesuré du 28/09 au 31/12, 48 présences sur
cette ligne, aucune avec horaire. « Tous les autres présents en D » doivent
avoir le leur : il en reste **140 sans horaire** sur 426 présences en D
d'ici la fin de l'année — les « D » seuls (FPS le 28/09, `["D"]`) et les
journées de réunion sans plage (`["AM","D-CPPT"]`). Quel horaire leur
écrire est la question du « D seul » ci-dessous, reposée au client le
même jour ; rien n'est deviné en attendant.

Rien ne bouge dans la lecture ni dans le placement : les quatre sorties du
vérificateur sont identiques à l'octet à celles d'avant v269. Vérifié au
navigateur le 28/09 (AFA et JBI « 7-15 », YRS rien), le 05/10 (SKS
« 6-14 ») et le 02/12 (FPA « H. flot. »), à 320, 390 et 1280 px, hors
ligne compris.

**« Postes en sous-effectif », sans choix d'horizon, et un prochain poste
qui dit où.** Le client, le 26/09/2026 : « il ne doit pas y avoir de
sélection de temps sur les postes en manque ; il faut l'appeler "Postes en
sous-effectif" et ne pas marquer le nombre de journées regardées ; dans le
cadre Mon prochain poste il faut écrire la date, la pause, le poste
occupé ». Les boutons 7 j / 14 j / 30 j / Tout sont partis avec leur
écouteur et la clé `ui/mqHorizon` : le module regarde d'aujourd'hui à la
fin de l'horaire, et son sous-titre ne dit plus que « 7 journées » ou
« rien à signaler ». Le cadre écrit « Lundi 28 septembre · D ·
Contremaître », avec « (demain) » quand c'en est un et les heures
seulement si la journée n'est pas complète. Le poste vient de
`posteLeJour()`, la chaîne du tableau du jour (`equipeDuJour()` puis
`postesDePause()`, colonne D comprise) : le cadre et le tableau disent
donc la même chose. La pastille colorée est partie, puisque la pause
s'écrit en toutes lettres, et avec elle ses styles et ceux de `.mqbar`.
Les quatre sorties du vérificateur sont identiques à l'octet ; rien ne
déborde à 320, 390 et 1280 px, hors ligne compris.

**La pause du moment surlignée, un trait après les postes, et deux titres
renommés.** Le client, le 27/09/2026 : « met en surbrillance légère la
pause du moment ; fais une bordure semblable à celle sous la ligne de pause
à droite de la colonne du poste ; écris "Équipes du jour" au lieu de "À
l'usine", et "Postes en sous-effectif" à la place de "À venir", sans le
remettre juste en dessous ».

- La colonne de la pause en cours (AM de 6 h à 14 h, PM de 14 h à 22 h, N
  de 22 h à 6 h) reçoit un voile `--maint`, posé en `box-shadow` intérieur
  PAR-DESSUS le fond de la case : le zébra et le rouge d'un manque restent
  visibles dessous. Seulement sur la journée qu'elle concerne : après
  minuit, la nuit en cours est celle de la veille, et le tableau d'aujourd'hui
  ne surligne rien (voir juste dessous : le tableau lui-même montre
  désormais la veille jusqu'à 6 h). La colonne se désigne par son rang (`data-mc` sur le
  tableau), et quatre règles `nth-child` suffisent.
- `th.eqposte` porte à droite le même trait de 2 px `--trait-fort` que
  celui sous l'en-tête.
- Le titre du module est au-dessus du cadre ; le repli ne garde que le
  compte (« 7 journées »), et ses deux règles `summary h2` sont parties.

Un point de sauvegarde était demandé : le tag `checkpoint-v273` est refusé
à l'envoi par le serveur (403), le commit 8b1edcd, déjà sur `main`, en
tient lieu. Les quatre sorties du vérificateur sont identiques à l'octet ;
vérifié à 7 h, 15 h, 23 h et 2 h, à 320, 390 et 1280 px, hors ligne compris.

**Le jour de l'usine commence à 6 h.** Le client, le 27/09/2026 : « il faut
afficher l'équipe du jour jusqu'à 6 heures du matin et passer au jour
suivant seulement à 06h ». `jourUsine()` rend la veille entre minuit et
6 h, et `eqJourValide()` s'en sert. Tant qu'on n'a pas choisi un jour à la
main (flèches ou clic sur un manque), `eqAuto` le fait recalculer à chaque
rendu : une application restée ouverte passe au jour suivant à 6 h, au
prochain affichage. « Aujourd'hui » rend la main au jour de l'usine. La
surbrillance de la nuit, qui prenait déjà la veille après minuit, tombe
désormais sur le tableau affiché. Vérifié à 23 h 30, 2 h et 5 h 59
(dimanche 27, N surlignée) puis à 6 h 01 (lundi 28, AM), à 320, 390 et
1280 px, hors ligne compris ; les quatre sorties du vérificateur sont
identiques à l'octet.

**La ligne des pauses a la hauteur des postes, et un trait au-dessus.** Le
client, le 27/09/2026 : « hauteur de la ligne des pauses comme les lignes
de poste, et ajouter la même bordure qu'en dessous de la ligne des pauses
au-dessus des pauses ». `thead tr{height:44px}` et un trait de 2 px
`--trait-fort` en haut des cases de pause ; le coin au-dessus des postes
reste sans trait, comme demandé la veille. 44 px à 320 et 390 px, 45 au
bureau où l'horaire de la pause s'écrit sous son code. Les quatre sorties
du vérificateur sont identiques à l'octet, hors ligne compris.

**Les postes s'écrivent comme dans le tableau des équipes, et le coin dit
« Poste ».** Le client, le 27/09/2026. Mêmes abrégés que l'onglet Équipe
(`PV_COURT` : MEUN., GLUT., FERM., T. ARR., DIST., CHAUD., STEP), plus CM,
ADJ., FORM. et « À DÉT. », en capitales, 10,5 px sur téléphone ; les noms
entiers en 12,5 px au bureau. La colonne passe à 76 px et 136 px, avec les
marges intérieures du tableau des équipes (7 px au bureau) : avec
l'ancienne marge gauche de 14 px, « TERRAIN ARRIÈRE » était coupé à
1280 px, et la mesure l'a montré avant le commit. Les trois pauses
rendent chacune 3 à 4 px à 320 px, et l'horaire de la colonne D passe
sous le trigramme, coupé au tiret s'il le faut (« (8h30-16h30) »
débordait de 16 px). Les trois abrégés d'avant (MEU, GLU…) sont partis.
Les quatre sorties du vérificateur sont identiques à l'octet ; rien ne
déborde à 320, 390 et 1280 px, hors ligne compris.

**Sous chaque pause, l'équipe qui y tourne.** Le client, le 28/09/2026 :
« indiquer dans la cellule de la pause (à la place de l'horaire) l'équipe
avec laquelle la pause est prévue de tourner ce jour-là ; pareil pour les
D, juste l'équipe, pas le binôme ». `equipesDuCycle()` lit, mois par mois,
le décalage de chaque équipe dans le cycle de cinq semaines, sur les
cellules franches de TOUS ses membres (catégorie « Shift n ») — une voix
par cellule, si bien qu'un échange ou une personne déplacée ne fait pas
basculer l'équipe. `equipeALaPause()` en tire « AM Éq. 2 · D Éq. 4 · PM
Éq. 5 · N Éq. 1 » (« Équipe n » au bureau). **Mesuré sur 2026** : le même
décalage les douze mois pour les cinq équipes (équipe 3 à 0, 1 à 7, 5 à
14, 4 à 21, 2 à 28 jours), de 71 à 99 % des cellules d'accord, et **jamais
deux équipes à la même pause un même jour**. Sous 60 % d'accord, rien
n'est écrit plutôt que deviné. L'horaire de la pause (6h-14h…), qui ne se
voyait qu'au bureau, a cédé sa place. Vérifié le 28/09, le 03/10 (samedi,
pas de D) et le 07/10, à 320 (hors ligne), 390 et 1280 px, chaque fois
égal au calcul fait à part en Python ; les quatre sorties du vérificateur
sont identiques à l'octet.

**Chaque sous-effectif dit son équipe, et qui pourrait le combler.** Le
client, le 28/09/2026 : « indiquer l'équipe dans laquelle il manque
quelqu'un et s'il y a des possibilités de remplacement avec les gens
présents ce jour-là selon leur polyvalence (attention de bien garder
l'effectif minimum à chaque poste et pause) ». Une ligne par manque :
« N Terrain arrière 0/1 · Éq. 1 → ATR (Chaud.) ». L'équipe vient de
`equipeALaPause()`. Les pistes viennent de `pistesDeRemplacement()`, qui
ne DÉPLACE personne — le rééquilibrage a déjà fait ce que le classeur lui
permet — et propose, dans l'ordre : quelqu'un de la même pause dont le
poste garde son minimum sans lui (un poste qui n'attend personne, comme
l'adjoint, compris) ; un « à déterminer » ; une personne en D sans code de
journée, au matin et à l'après-midi seulement. Il faut la polyvalence du
poste et y compter (un opérateur en formation n'y compte pas) ; pour le
contremaître, seul un cadre. Sinon « personne de libre ». Au 28/09 : six
journées, trois avec une piste — le 12/11, ATR aux chaudières (trois pour
deux attendus) est proposé au terrain arrière, ce que la question posée le
même jour suggérait. Les quatre sorties du vérificateur sont identiques à
l'octet (il ne découpe pas ce module) ; rien ne déborde à 320 (hors
ligne), 390 et 1280 px.

**Puis refait en fiches.** Le client, le 28/09/2026, capture à l'appui :
« il y a certainement moyen d'optimiser bien mieux ce tableau-là et de
faire ça 100 % professionnel ». Pastilles, équipe et flèche se suivaient à
la file et passaient à la ligne n'importe où (le 16/10 sur une ligne, le
12/11 sur deux). Chaque journée est désormais une rangée : à gauche un bloc
de date (« VEN. / 2 / OCT. »), à droite une fiche par manque, liseré à la
couleur de l'atelier ; ligne 1, la pause en pastille à sa couleur, le
poste, l'effectif en rouge, l'équipe calée à droite ; ligne 2,
« Remplaçants possibles » suivi d'étiquettes trigramme + provenance, ou
« Aucun remplaçant disponible ». Les journées sont séparées d'un filet
(`--trait`). Sous 380 px, « Équipe 2 » devient « Éq. 2 » et l'étiquette
« Possibles » : à 320 px « Terrain arrière » se coupait. Au bureau, la
fiche s'arrête à 560 px pour que l'équipe reste près du poste. Vérifié en
clair et en sombre à 320 (hors ligne), 390 et 1280 px : rien ne déborde,
rien n'est tronqué ; vérificateur identique à l'octet.

**Et le cadre « Mon prochain poste » vide** de la même capture : non
reproduit — même un horaire servi avec quatre secondes de retard finit par
le remplir. Par sûreté, il se redessine désormais dès que l'horaire arrive
(`fetchHoraireDB()`), puisqu'il se cache tant qu'il n'a personne à lire.
Si le cadre reste vide chez le client après la v291, c'est une autre
cause, à chercher sur son appareil.

**Les trigrammes du tableau du jour en étiquettes.** Le client, le
28/09/2026 : « il faut les mêmes badges de trigrammes sur ce tableau que
sur le tableau du dessus et du dessous ». Chaque trigramme prend
l'étiquette des sous-effectifs et des absents (fond `--surface3`, filet
`--trait`, mono gras 11,5 px), toujours l'un sous l'autre. La personne
choisie a le bord et l'encre de l'accent : elle n'est plus « la seule en
gras » (règle du 26/09), toutes les étiquettes l'étant. « (F) », « (C) »
et l'horaire de la colonne D restent dans l'étiquette, **en ligne** — une
règle générale `.eqn{flex-direction:column}` les faisait passer dessous,
et le tableau montait à 676 px ; 620 px ainsi à 390 px. Sous 380 px,
l'étiquette se resserre (3 px de marge, 11 px) pour que « SKS (F) » tienne
dans une colonne de 50 px. Vérifié en clair et en sombre, à 320 (hors
ligne), 390 et 1280 px : aucune étiquette ne sort de sa case ;
vérificateur identique à l'octet.

**Plus de « (F) » ni de « (C) », un horaire pour la consignation.** Le
client, le 28/09/2026 : « supprimer le F vu que le badge jaune dit déjà que
c'est en formation, pareil pour le (C) ; mais il faut indiquer l'horaire
de tous ceux qui apparaissent dans la colonne D ». Le « (F) » part ; le
« (C) » de YRS et BLR devient « (7h30-16) », l'horaire que le client a
donné pour leur D de consignation le 26/09 — une plage écrite dans le
classeur passe avant. **Restent 138 présences en D sans aucune heure
écrite** d'ici la fin de l'année (NPI 15, YBT 15, SKS 13…) : le classeur ne
définit nulle part l'horaire d'un « D » seul (cherché dans la légende et
dans tout le brut), c'est donc la question du « D seul », toujours posée.
Les règles mortes `.eqf` et `.eqfold` sont retirées. Vérificateur
identique à l'octet ; rien ne sort d'une case à 320 (hors ligne), 390 et
1280 px.

**« Horaire selon celui qu'ils font en D ».** La réponse du client, le
même jour. `horaireHabituelD()` lit, sur les journées de la personne elle-
même, la plage de JOURNÉE qu'elle écrit en D (annotation d'un « D », ou
cellule franche seule) : retenue si elle revient au moins deux fois et
fait au moins 60 % de ce qu'elle écrit. Elle vaut aussi les jours à code
(CPPT, DS-CE) : « tous ceux qui apparaissent dans la colonne D ». D'ici la
fin de l'année, les présences en D sans horaire passent de 138 à **112**,
chez **21 personnes qui n'écrivent jamais leurs heures en D** (NPI, YBT,
SKS, FPS, MGY, GPO, JBS, FLN, CDE, GKT, PAM, LHR, LCI, SPT, TCE, ALZ, RCO,
JKS, JBA, SVE, AAI) — ni en cellule, ni en commentaire, vérifié. Leur
horaire est demandé au client ; rien n'est deviné.

**BLR et YRS en D vont dans la colonne AM, à la meunerie.** Le client, le
28/09/2026 : « règle unique : si BLR ou YRS est en D il faut les mettre
dans la colonne AM mais avec leurs horaires 7h30-16 en dessous ; ils sont
en consignation meunerie ». Le tableau du jour déplace leur étiquette de
la colonne D vers la case AM · Meunerie, APRÈS ceux qui tiennent le
poste, avec « (7h30-16) » (ou la plage écrite ce jour-là). **Affichage
seulement** : la consignation est une tâche, pas la tenue du poste (le
client, le 26/09, pour « consign. ») — l'effectif de la case et les
sous-effectifs ne bougent pas, et l'étiquette n'est jamais jaune. La
colonne D disparaît si elle ne portait qu'eux. Vérifié les 28/09 (YRS),
05/10 (BLR), 16/10 et 08/10 — ce jour-là YRS est déjà en AM, il remplace
BLR ; vérificateur identique à l'octet.

**« Seulement D » : 7-15.** Le client, le même jour : « les gens où il
est seulement marqué D doivent avoir 7-15 sous eux ». Après les plages
écrites, la consignation et l'horaire habituel, un « D » seul — en cellule
franche (`["D"]`, `["D","meunerie"]`) ou en annotation (`["PM","D"]`,
`["-","D"]`) — affiche (7-15). Une prime conservée n'y change rien (ALZ le
05/10, « maintien prime N ») ; une journée à code, si : D-CPPT, DS-CE et
les formations F ne sont pas « seulement D ». D'ici la fin de l'année,
**317 présences en D, 10 sans horaire**, toutes de cette sorte (LHR,
LCI, JKS en CPPT ou CE, SVE et AAI en formation). La liste des 21
personnes demandée plus haut n'a plus d'objet.

**Et avant l'horaire habituel.** Le client, le même jour : « ceux qui sont
en D sans rien d'autre sont en 7-15 ». L'horaire habituel passait avant,
et une journée « seulement D » pouvait afficher autre chose que 7-15.
L'ordre est désormais : plage écrite ce jour-là, H. flot., commentaire à
tiret, consignation (7h30-16), **« seulement D » → 7-15**, et l'horaire
habituel pour ce qui reste (QBY en DS-CE le 21/10 : son 10-18 de CE).
D'ici la fin de l'année : 277 × (7-15), 21 × (H. flot.), 9 plages écrites,
10 journées à code sans horaire.

**Le tableau du jour resserré.** Le client, le 28/09/2026, capture à
l'appui : « comment optimiserais-tu ceci ? », puis « go » sur quatre
pistes :

- des étiquettes moins hautes : 1 px de marge au lieu de 2, 2 px entre
  deux trigrammes empilés, 3 px de marge de case ;
- l'horaire de la colonne D sans parenthèses, à côté du trigramme
  (« GPS 7-15 »). Il passait à la ligne dans toutes les étiquettes ;
  seul « 7h30-16 » de la consignation y passe encore ;
- la colonne des postes à 64 px au lieu de 76 sur téléphone, et 2 px de
  marge de case sous 380 px : « GPS 7-15 » tient ainsi dans une pause de
  56 px à 320 px ;
- un seul tiret, le court « – », dans toutes les cases vides : les lignes
  FORM. et « À dét. » écrivaient un tiret cadratin « — ». La distinction
  entre les deux tirets (« personne » ou « personne n'est attendu »)
  n'avait plus de légende pour la dire.

Le liseré gauche du coin « POSTE » reste : le client l'a redemandé le
27/09. La hauteur minimale d'une ligne (deux trigrammes) et les
trigrammes l'un sous l'autre restent aussi. Mesuré le 25/09 : 566 → 518 px
à 390 px, 576 → 517 px à 320 px. Rien ne sort d'une case à 320 (hors
ligne), 390 et 1280 px, en clair et en sombre. Neuf règles et
`--manques 0928` identiques à l'octet.

**« Cons. » au lieu de « 7h30-16 ».** Le client, le 28/09/2026, pour les
étiquettes qui passaient encore à la ligne : « écrire Cons. ». BLR et YRS
rangés à la meunerie du matin portent « Cons. », quoi qu'écrive leur
cellule ; en D le week-end, « Cons. » remplace aussi « 7h30-16 » quand
aucune plage n'est écrite. « 7h30-16 » ne tenait sur une ligne dans aucune
case de téléphone (64 px pour 62, mesuré). À 390 px la ligne MEUN. passe
de 57 à 46 px et le tableau à 507 px ; à 320 px, « BLR Cons. » passe
encore à la ligne. Neuf règles identiques à l'octet.

**Puis « 8-16 ».** Le client, le même jour : « écrire 8-16, ça ira
mieux ». « Cons. » est remplacé partout par « 8-16 », qui tient sur une
ligne jusqu'à 320 px, comme « 7-15 ».

**Le badge de formation bordé de jaune.** Le client, le même jour :
« le badge doit être jaune comme le badge perso ». **Je l'ai d'abord
compris de travers** : j'ai mis BLR et YRS en jaune (v310). Le client :
« non, eux deux ne devaient pas changer ; je voulais que les badges des
personnes en formation soient jaunes comme le badge perso ». Le badge de
la personne choisie a le bord ET le trigramme à l'accent ; celui d'un
opérateur en formation n'avait que le trigramme en jaune. Il prend
désormais aussi le bord jaune. BLR et YRS retrouvent leur badge
ordinaire.

### La meunerie du matin : deux en semaine, consignation comprise

Le client, le 28/09/2026 : « le poste consignation en meunerie est un
poste qui doit compter dans l'effectif meunerie du matin ; ils doivent être
toujours au moins 2 dans cette case du lundi au vendredi ». Question posée
avant de coder (A : les consignateurs en D comptent dans les deux ; B :
deux en pause plus la consignation). Réponse : « A, mais il faut vérifier :
si d'autres personnes sont en D meunerie (et validées, donc pas ceux en
formation), c'est bon ».

- `renfortDuJour()` pose `meun:{AM:2}` du lundi au vendredi, **jours fériés
  exclus**. Ce choix était le mien, et le client l'a confirmé le
  28/09/2026 : « A », un férié se traite comme un week-end. Les autres renforts fusionnent par le maximum.
  `RENFORT_CLOS` ne lève que ceux du classeur ;
- `meunDepuisD()` fait compter pour la meunerie du matin, parmi les gens en
  D, BLR et YRS (`CONSIGNATEURS`) et quiconque la chaîne met en meunerie
  avec `compteAuPoste()`. Sont exclus les gens en formation et ceux qui
  portent un code de jour (CPPT, DS…). Ces copies portent
  `depuisD` : la polyvalence, le prochain poste et le poste de la barre du
  haut les ignorent ;
- au tableau du jour, un consignateur s'écrit dans la case AM de la
  meunerie avec son (7h30-16), et plus en colonne D. Un validé en D
  meunerie reste en D, mais il compte.

Mesuré : neuf règles, compteurs et `--manques 0928` identiques à l'octet.
Sur l'année, 272 → 277 places creuses : quatre matins de meunerie à 1/2
(03/07, 17/07, 11/08, 14/08, les deux consignateurs en congé, malades ou en
repos) ; le 06/01 passe de 0/1 à 1/2 ; le 13/08, le rééquilibrage envoie un
chaudiériste en meunerie (chaudières 1/2). Recyclage : meunerie +1 chez
JKS, LDY et PLZ, qui tiennent la seconde place ; CDE distillation −1, SKS
distillation +1 et chaudières −1 ; couples au quota inchangés. Au navigateur, le 28/09 :
« MEUN. JKS · YRS (7h30-16) », SKS (formation meunerie) reste en D
(7-15) et ne compte pas. Vérifié à 320 (hors ligne), 390 et 1280 px.

### Un atelier écrit peut être le mauvais : `POSTE_DU_JOUR`

Le client, le 26/09/2026 : « pourquoi VGG est en distillation demain alors
que BBZ est là ? ». Le 27/09 en PM, GDT, titulaire de la distillation, est
en DTT ; VGG porte `["PM","distillation","remplace GDT"]` ; BBZ, renfort
arrière dont la seule polyvalence est la distillation, porte `["PM"]`.
Deux en distillation, le terrain arrière à 0/1. Le commentaire de GDT,
« remplacé par FPA », est faux de son côté : FPA est de nuit ce jour-là.
Trois lectures proposées, le client a répondu « A » : BBZ en distillation,
VGG au terrain arrière, qu'il sait tenir (fermentation et distillation).

`POSTE_DU_JOUR` porte cette décision, **pour la journée nommée seulement**.
C'est la seule table qui passe AVANT la cellule dans `posteTenu()` : elle
corrige justement ce que la cellule écrit. Elle entre dans la découpe du
vérificateur.

**Pas de règle générale, et c'est mesuré.** Une sonde a cherché sur l'année
la même forme : quelqu'un d'écrit sur un poste en surnombre qui a la
polyvalence d'un poste vide à la même pause. **11 journées**, et plusieurs
sont justes telles quelles : GPO les 19 et 20/08 en « Ferm. Liq. », PAM le
21/05 en « terr. Arr. + fermentation », VGG le 07/08 dont le commentaire
dit « atelier gluten 08h-14h ». La règle se tromperait : chaque cas se
tranche avec le client.

Mesuré : neuf règles, compteurs et Recyclage identiques à l'octet ; le
27/09 PM quitte la liste des manques (8 → 7 d'ici la fin de l'année, 269
→ 268 places sur l'année). Vérifié au navigateur, hors ligne compris.

### AAI à la distillation, SMA au terrain arrière : `POSTE_HABITUEL`

Le client, le 27/09/2026 : « dans l'équipe 5, par défaut c'est toujours AAI
qui tient le poste distillation et SMA le terrain ». Sur l'année, les jours
où ils sont dans la même pause, la chaîne disait **l'inverse 80 fois**.
AAI est renfort arrière, avec fermentation et distillation : la règle du
terrain arrière le prenait. SMA porte « Distillation » en ligne 9.

`POSTE_HABITUEL` passe après la cellule et la tranche de période (ce qui
est écrit pour un jour prime) et avant le rôle et la ligne 9, qu'elle
corrige. Il reste quatre journées « inversées », et elles sont justes :
AAI y porte « poly. Etoh » (22 et 23/07, 23/10, 04/11). La table entre
dans la découpe du vérificateur.

Mesuré : neuf règles, compteurs et `--manques 0926` identiques à l'octet.
Sur l'année, 268 → 269 places creuses (le 14/01 AM, le trou passe de la
fermentation au terrain arrière). Recyclage : la distillation devient le
poste d'AAI et sort de sa ligne ; SKS distillation 4 → 12 ✓, SMA
distillation 2, SPS 30 → 31, CDE et LDY bougent d'une ou deux journées.
**23 couples au quota, inchangé.** La composition de l'onglet Équipe suit :
AAI en distillation, SMA au terrain arrière.

Même commit : le coin « Poste » du tableau du jour retrouve sa bordure
haute (2 px, le trait des pauses) et gauche (3 px, la largeur des liserés
de zone). Le client, le 27/09/2026 : « remettre les bordures gauche et
haute ».

### Tout l'horaire relu : d'où viennent ces erreurs

Le client, le 26/09/2026 : « vérifie tout l'horaire, comment cela se fait
ces erreurs ? ». `node tools/verifier-calendrier.js --doublons` relit
l'année et liste deux formes. (1) Une personne PRÉSENTE à une pause dont
le commentaire dit « remplacé par » sans heures. (2) Une personne présente
à côté d'un collègue qui écrit « remplace » son trigramme, sans heures.
Le mode est informatif (code 0) : **606 journées** remontent, et la plupart
sont justes. « Remplacé par » parle du poste PRÉVU : quelqu'un envoyé au
terrain arrière, en formation ou en SD26 est remplacé à son poste
habituel, et il est bien à l'usine, ailleurs.

**Première version, trop étroite** : elle n'exigeait que le remplaçant nommé
soit à la même pause, et elle ne voyait pas YPE, dont le commentaire nomme
VGG (qui ouvre la nuit en PM) alors que c'est FPA qui tient sa place.
Rejouée sur la version d'avant la correction, elle ne trouvait rien : un
contrôle qui ne peut pas échouer ne contrôle rien.

Trois familles d'erreurs, triées à la main :

- **la journée entière de flex time repris** (YPE, PDR) : corrigée, voir
  la section précédente ;
- **une absence écrite en deux moitiés, la seconde dans le commentaire** :
  `["AM","1/2VA","+4h rhs remplacé par SPS"]`. La lecture ne prend que la
  cellule : la personne paraît présente 4 h, avec prime et chèque-repas.
  **59 journées sur l'année**, dont 50 en « +Nh rhs ». Aucune fiche de LCI
  ni de VBN n'en porte : c'est une question au client ;
- **« remplace Y » chez un collègue, alors que la cellule de Y ne porte que
  son code** : `FPA ["PM","R-CM","remplace FLI"]` et `FLI ["PM"]` le 16/01,
  soit deux contremaîtres en PM. **16 journées.** Deux relèvent d'une
  évaluation (partielle). Pour les autres, le classeur ne dit pas si Y
  était absent ou déplacé : c'est une question au client.

**Les deux moitiés sont lues depuis le 26/09/2026.** Le client : « 2 A »,
c'est-à-dire que le complément du commentaire complète la journée. Le
point des 16 journées « remplace Y » sera vérifié avec lui le lendemain.
`lireJournee()` lit, à sa fin, chaque « +N h rhs / RTT / DTT / VA / -FT »
du commentaire. Les heures de rhs vont au compteur de récup. HS de la
fiche (`rhsJ` → `rec.rh`), comme une reprise écrite dans la cellule. Les
autres codes rejoignent `r.ax`, sans doublon : KDN le 28/02 avait déjà
son « 4h VA » lu par un autre chemin, et la première version l'écrivait
deux fois. Les heures prestées valent **au plus la journée moins toutes
les absences du jour**. Une plage déjà écourtée n'est donc pas retranchée
deux fois : ADK `["7h-15h","8h-12h","+4RHS"]` reste à 4 h, et CKS
`["7h-15h","1/2VA","+2h RTT Départ à 9h"]` tombe à 2 h, ce que dit son
départ. Le flex time repris ne retire rien aux heures payées : c'est la
présence qui baisse. « +4h CSS » est une demi-journée de congé sans
solde, non payée (le client, le 26/09/2026). Elle a désormais ses codes
cachés, `4H CSS` et `1/2 CSS`, de la famille de `SANS SOLDE` : SMA le
10/09 est une absence complète, ½ DTT + ½ CSS. Une journée de plus en
absence ; neuf règles, compteurs, manques et Recyclage identiques à
l'octet.

Mesuré : **20 journées passent de prestées à absences** (14 494 → 14 474),
les autres ont moins d'heures ; neuf règles à zéro ; compteurs et
`--manques 0926` identiques à l'octet ; année 264 → **269** places creuses ;
22 couples au quota, inchangé. Au navigateur, le 27/02 de SMA s'affiche
« ½VA » dans son calendrier, et plus « AM ».

**Les personnes en journée entrent dans le tableau « Qui travaille »**, sur
une dernière ligne « En journée » qui occupe toute la largeur : la journée
n'a pas de pause, et trois colonnes vides l'auraient fait lire comme un
manque. Sous chaque trigramme, ce qui l'amène en journée (F, CPPT, DS). Le
tableau porte désormais aussi la formation hors poste, une ligne par pause.
Ces personnes vivaient seules dans une carte « Hors poste », sous les
malades, alors qu'elles sont à l'usine ce jour-là : **la carte a disparu**,
avec `ligne()` et les styles `.eqt`, qui ne servaient plus qu'à elle.

Le 28/09 : 11 personnes en journée, sur deux lignes à 390 px. Rien ne
déborde à 320, 390 et 1280 px, en clair et en sombre, hors ligne compris.
Les quatre sorties du vérificateur sont identiques à l'octet.

### Le mémo des trois fonctions du mois

`equipeDuJour()` recalculait `cycleDuMois()`, `epargnesDuMois()` et
`renvoisDuMois()` **pour chaque personne et chaque jour**, et la dernière
balaie l'année entière à chaque appel. Une saison coûtait donc 265 jours ×
77 personnes × 365 journées de balayage.

Elles ne dépendent que de la personne, du mois et de l'heure de journée :
`moisDe()` les retient. **`--manques` est passé de 90 s à 8,7 s**, au
résultat identique — et c'est ce qui rend la polyvalence calculable dans le
navigateur, 1,6 s à l'ouverture du repli.

La clé porte `hJour` : un changement de réglage refait le calcul.

**`finAbsence()` gardait son propre cache, et il ne survivait pas à
l'appel.** Mesuré le 26/09/2026, profileur à l'appui : l'onglet Recyclage
figeait l'écran **13,6 s sur un processeur de téléphone** (2,9 s sur PC), et
84 % de ce temps était là. Chaque malade de chaque journée depuis février
refaisait `cycleDuMois()` pour tous les mois de sa série — et une série de
trois cents jours se relisait depuis chacun de ses jours.

Elle prend donc ses tables dans `moisDe()`, et retient dans `_finCache` la
fin trouvée pour **chaque** journée parcourue : partie du 2 ou du 3 d'une
même absence, la recherche aboutit au même dernier jour, et s'arrête dès
qu'elle en rencontre un déjà connu.

**Recyclage 13,6 s → 1,4 s** au téléphone simulé (0,31 s sur PC), Résumé
785 → 167 ms. Rien d'autre ne bouge, et c'est prouvé : les 1 847 journées de
maladie de l'année rendent la même fin qu'avant, **dans l'ordre, à rebours et
dans le désordre** — le cache ne doit pas dépendre de l'ordre des appels —,
et les quatre sorties du vérificateur (règles, `--manques`, `--polyvalence`,
`--compteurs`) sont identiques à l'octet.

`_finCache` entre dans la découpe du vérificateur, déclaré juste au-dessus
de la fonction : sans lui, `finAbsence()` y lèverait une `ReferenceError`.

### Les manques d'effectif à venir

```bash
node tools/verifier-calendrier.js --manques [MMJJ]
```

Mesure ce que le module « Postes en manque » de l'onglet Équipe annoncera,
de la date donnée à la fin de l'horaire. Il ne le simule pas : il découpe
`equipeDuJour()` et `postesDePause()` dans `index.html` et les rejoue. Une
alerte qui compterait autrement que la vue du jour serait pire que pas
d'alerte.

**Au 22/09/2026, classeur de 15 h 46 : 15 journées sur 101, 17 places
creuses** — fermentation (9), terrain arrière (3), chaudières (2), gluten
(1). Si ce nombre s'effondre ou explose
après une modification du rééquilibrage ou des polyvalences, c'est une
régression.

L'outil met une minute et demie : tout son code passe par `eval()`, que V8
n'optimise pas. **Ce n'est pas la vitesse de l'application** — le navigateur
fait les mêmes 102 journées en 2 secondes.

**Ne jamais tester la fonction d'une personne avant d'avoir lu sa cellule.**
`posteTenu()` le faisait : `estCadre()` renvoyait « adjoint » avant que
`posteEcrit()` ne lise `["AM","Gluten","Remplace SLT"]`. 184 journées de
cadres nommaient ainsi un poste sans être lues, et le module criait au manque
sur la moitié de ses alertes. Voir `docs/conversion-horaire.md`, « La cellule
prime, y compris sur la fonction de la personne ».

Le module de l'application ne regarde **jamais en arrière** — un manque passé
ne se comble plus. C'est sa règle de naissance, et elle n'a plus besoin d'être
écrite au-dessus de lui : « À partir d'aujourd'hui » occupait une ligne pour
décrire ce qu'il est.

**Son en-tête coûtait 189 px avant la première journée**, presque autant que
quatre jours de contenu : un titre de 28 px, un sous-titre, une légende et une
rangée de boutons. Le client, le 22/09/2026 : « moyen de faire beaucoup
mieux ». Titre et compte tiennent maintenant sur une ligne — « journées » deux
fois dans la même phrase ne disait rien de plus la seconde — et le tout fait
**83 px**. La carte passe de 586 à 414.

**« 1 poste à déterminer ce jour-là »** occupait sa propre ligne en italique
sur quatre journées de neuf. C'est une pastille `+1 ?` de la rangée, à côté
des postes qu'elle nuance : l'un de ces postes indéterminés est peut-être
celui qui manque, et c'est là qu'on le lit.

### La polyvalence : combien de journées complètes à chaque poste

```bash
node tools/verifier-calendrier.js --polyvalence [MMJJ] [--tout]
```

Le client, le 22/09/2026 : « pour les opérateurs, cela peut être bien aussi
d'indiquer combien de jours (complet 8h) ils ont fait sur chaque poste de
production ; les autres ont un quota de polyvalence de 10 jours par poste,
les adjoints 5 jours par poste ».

Il ne recompte rien à côté : il **découpe** `calculerPolyvalence()` et
`polyvalenceDe()` dans `index.html`. Sa première version les réimplémentait,
et elle a divergé le jour même sur BBZ — « son poste » n'y suivait pas la
même chaîne.

Cinq choix, tranchés avec le client le 22/09/2026 et écrits dans le code
plutôt que cachés :

- **la période court du 1er février au 1er février**, et non sur l'année
  civile : « la polyvalence se déroule sur la période du 1er février au
  1er février de l'année d'après ». Compter depuis le 1er janvier ajoutait
  un mois appartenant à la période précédente — quatre couples au quota de
  moins une fois janvier écarté. L'horaire ne couvrant qu'une année, une
  période à cheval n'est mesurable que pour sa part présente dans le
  fichier ;
- on s'arrête **AUJOURD'HUI**. Le classeur court jusqu'au 31/12 ; compter
  la fin de l'année créditerait des journées qui n'ont pas eu lieu, et ATR
  atteignait ainsi le quota aux chaudières sans y avoir mis les pieds ;
- **le poste habituel ne compte pas** : un quota de dix journées ne veut rien
  dire sur le poste qu'on tient tous les jours, et NPE y affichait 211/10 ;
- seules les pauses **AM, PM et N** — le « Jour » ne tient pas un poste de
  production, et `postesDePause()` n'y attend d'ailleurs personne ;
- **huit heures pleines ou rien** : une demi-journée n'apprend pas un poste à
  moitié.

**« Son poste » se prend avec `posteTenu(p,[],hJour,null)`, pas avec
`posteHabituel()`.** Les deux fonctions répondent à la même question et la
seconde répond moins bien : elle rend « terrain arrière » dès que le rôle de
feuille le dit, sans la garde `tientTerrainArriere()`. BBZ y gagnait terrain
arrière alors qu'il n'y a pas fait une journée et qu'il en a fait 133 en
distillation. `posteParDefaut()` vient en dernier, faute de quoi PDE n'a pas
de poste habituel et ses 134 journées à la station passent pour de la
polyvalence.

**Une journée ne compte QUE si la personne possède la polyvalence du
poste.** Le client, le 22/09/2026 : « les polyvalences ne doivent compter que
s'ils ont cette polyvalence dans leurs connaissances ; AAI et ALZ ont été à
la STEP pour voir à quoi cela ressemblait sans faire de polyvalence ». Une
journée à un poste qu'on ne possède pas n'apprend pas ce poste : on y est
passé, on ne l'a pas tenu. Le poste non possédé disparaît donc de la ligne,
journées comprises — quatre journées à la STEP chez trois personnes.

L'outil les liste tout de même, sous « journées tenues SANS la polyvalence
du poste » : elles ne comptent pas, mais les taire serait perdre une
information que personne d'autre ne porte.

**Un opérateur EN FORMATION n'a pas de poste à lui.** Le client, le
22/09/2026 : « les opérateurs en formation ne peuvent pas posséder comme
poste par défaut le poste où ils sont en formation ; ils ne doivent pas y
faire de recyclage vu qu'ils n'y sont pas validés (exemple SKS en
meunerie) ». La ligne 9 leur en donne bien un — SKS la meunerie, LHR et GST
les chaudières — mais c'est celui où ils APPRENNENT. Aucun des huit ne l'a
dans sa polyvalence, ce qui le confirme : on n'est pas validé là où l'on se
forme.

Ce poste ne devient donc ni « son poste » ni une ligne de recyclage : les
112 journées de SKS en meunerie ne comptent pas. Sa case porte un **F** —
muette à côté de tant de journées, elle poserait plus de questions qu'elle
n'en résout.

`posteAttitre()` et `posteDeFormation()` partagent la même chaîne à dessein :
c'est le MÊME calcul, seule la personne décide lequel des deux il devient.
Une première version calculait le poste une fois dans `polyvalenceDe()` et
une fois dans le rendu — la seconde copie ignorait la règle, et la pastille
pleine restait sur la meunerie de SKS. **Deux copies, et c'est toujours la
seconde qui reste en arrière.**

**Attention au piège documenté plus haut** : polyvalence INCONNUE n'est pas
polyvalence VIDE. Les trois personnes sans liste déclarée sont des opérateurs
en formation, qui n'en ont effectivement aucune ; les quatre que `CORRECTIONS`
avait dépouillées ont retrouvé la leur. Si cela changeait, la règle stricte
effacerait des polyvalences réelles sans rien dire.

**« 0/X » ne porte AUCUN fond.** Le client, le 22/09/2026 : « quand c'est
0/X il ne faut pas changer le background ». Elle en avait un, gris, pour se
distinguer du néant — mais un fond est une alerte, et il n'y a rien
d'anormal à pouvoir tenir un poste sans l'avoir encore fait. Le chiffre le
dit. Les deux fonds qui restent signalent chacun un écart : le vert un quota
atteint, le jaune une formation.

**« 0/X » se lit dans la colonne d'un poste dont la polyvalence est acquise
sans qu'un seul remplacement ait été fait.** Le client : « il doit être écrit
0/X dans la colonne où ils ont la polyvalence mais qu'ils n'ont pas encore
fait de remplacement ». Une case vide ne disait pas si la personne ne pouvait
pas tenir le poste ou si elle le pouvait sans l'avoir encore fait — et c'est
justement cela qu'un contremaître cherche. « Terrain arrière » ne figure dans
aucune liste de polyvalence du classeur : il se déduit de Fermentation ET
Distillation, comme `tientTerrainArriere()` le fait partout ailleurs.

**Au-dessus de la grille, la période et rien d'autre.** Le client, le
22/09/2026 : « pas très compréhensible » — et, interrogé sur quoi : « le
texte au-dessus des postes », puis « c'est la légende au-dessus que je
n'aimais pas ». Cette ligne annonçait quatre chiffres — personnes, postes au
quota, total, sans remplacement — avant qu'on ait vu la grille : un bilan
par-dessus ce qui n'était pas encore lu. La période, elle, se lit AVANT,
sans quoi aucun nombre du tableau ne veut dire quelque chose. Elle tient
désormais sur la ligne du titre.

**La vue de bureau a de la place : qu'elle s'en serve.** Le client, le
22/09/2026 : « optimise la vue PC, les chiffres sont peu visibles (les 10
et 5), titre plus grand, et la date et le poste à droite comme sur mobile ».

Les réglages de la grille sont ceux d'une colonne de 38 px sur un
téléphone ; à 1280 px ils laissaient la grille minuscule au milieu du vide,
et le quota — en petit, derrière la barre, à demi effacé — ne disait plus
sur combien on compte. Au-delà de 760 px : titre à **20 px**, chiffres à
**13**, quota à **11 px et 80 % d'opacité** au lieu de 9 px et 55 %.

**La date et le poste se calent à droite**, comme sur téléphone. La marque
se réduisait à sa largeur de contenu — `margin-right:auto` la pousse à
gauche et elle ne réclame rien de plus — si bien que le bloc du jour restait
collé au trigramme avec mille pixels de vide à sa droite. `flex:1 1 auto`
lui rend la place libre, et le `margin-left:auto` de la colonne du jour fait
le reste : 16 px du bord, ou 14 px du chèque du net sur les onglets qui le
portent.

**La requête se pose APRÈS les règles qu'elle doit battre**, et non dans le
haut de la feuille où elle avait d'abord été écrite : une requête média
n'ajoute AUCUNE spécificité, donc à égalité c'est la dernière écrite qui
gagne. Elle n'avait rien changé du tout. C'est la TROISIÈME fois que ce
piège se referme sur ce fichier — la zébrure de cette grille, la barre
d'onglets sous 375 px, et celle-ci.

**Les intitulés de poste restent abrégés et horizontaux**, et la légende
reste SOUS la grille. Une version verticale en toutes lettres et une légende
remontée ont vécu une demi-heure : « j'aimais bien les postes écrits comme
avant ». Les deux tenaient à toutes les largeurs — ce n'était pas la
question. **Deux mots de retour valent mieux que trois hypothèses**, et il a
fallu demander pour trouver la bonne.

**La liste est alphabétique, sans intercalaire d'équipe** : on cherche
quelqu'un par son trigramme, pas par son équipe.

**Au 22/09/2026, classeur de 15 h 46 : 33 couples personne-poste au quota
sur 101, dont 22 où la polyvalence est acquise sans un seul remplacement** —
mesuré identique par l'outil et par le navigateur.

Second contrôle, indépendant, et il se lance lui aussi :

```bash
node tools/verifier-calendrier.js --compteurs
```

Il recalcule les compteurs flex time de chacun depuis ses journées et les
compare à ceux du pied de classeur, saisis à la main. Les neuf règles
regardent ce que la case AFFICHE ; celui-ci additionne ce qu'elle COMPTE.
**76 personnes sur 77 doivent concorder exactement** — la seule divergence
connue est une erreur du classeur (FPA, 39 h contre 36 au 22/09/2026 ;
44 contre 41 la veille — l'écart de 3 h, lui, ne bouge pas), documentée en
section 10 bis.
