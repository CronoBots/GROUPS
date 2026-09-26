# BIOWANZE

Simulateur de fiche de paie belge (Groupe S, CP 220) pour les équipes en
pauses de Biowanze. Application web installable, **entièrement contenue dans
`index.html`** — pas de build, pas de dépendances, pas de framework.

## Méthode de travail — à appliquer TOUJOURS

Le client, le 26/09/2026 : « enregistre tout ce que tu viens de faire pour ne
jamais oublier et toujours utiliser la meilleure méthodologie ». Ce qui suit
résume les règles que ce fichier démontre, cas par cas, plus bas. En cas de
doute, c'est la section détaillée qui fait foi.

**Git.** Le client, le 26/09/2026 : « il faut toujours pousser sur main ».
Chaque commit part sur la branche de travail ET sur `main`
(`git push origin <branche>:main`). Aucune pull request, sauf demande.
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

Le `.xlsm` reste HORS du dépôt. On LIT le rapport de comparaison, on dit au
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

Elle enchaîne tout ce qui suit dans un dossier temporaire, derrière **sept
portes** — anonymiseur, second contrôle, **fidélité de la copie à la
source**, convertisseur, export et son aller-retour, intégralité cellule par
cellule, neuf règles dures du calendrier. La première qui se ferme arrête
tout, et rien n'est installé. Elle imprime ensuite le rapport du
comparateur. Avec `--installer`, les trois fichiers de `data/` sont
remplacés ENSEMBLE, `V` est incrémenté, et le garde-fou du dépôt passe sur
le résultat — s'il échoue, les fichiers d'avant reviennent depuis leur
copie. Si rien n'a changé, rien n'est touché, pas même `V`.

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
départs, changements de groupe, journées modifiées avec l'avant et l'après,
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
214. La nuit (une journée) attend une réponse.

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
  - **la nuit avec « DS-CE » ou « D-CPPT »** — 8 h de prime de nuit, ou
    4 h + 4 h sans prime comme l'après-midi ? Le client se renseigne ; sa
    fiche de septembre le dira, VBN le 30/09 `["N","D-CPPT"]` étant sa
    seule journée de ce genre du mois. Aujourd'hui : 8 h, prime conservée ;
  - la paie à l'heure elle-même — voir `docs/regles-paie.md`, « La fiche
    d'ouvrier » ;
  - **LCI le 17/03** : 1 h sup sur la fiche, `["AM"]` dans l'horaire, la
    veille `AM · VM` — l'heure de visite médicale hors horaire ? (−13,29 €) ;
  - **le départ anticipé sans code** — LCI le 05/04, « D2PART 0 18H
    REMPLAC2 PAR alz » (tapé en verrouillage majuscule : « départ à 18h,
    remplacé par ALZ », confirmé par « arrivée à 18h00' » chez ALZ) : la
    fiche paie 4 h PM + 4 h de compensation sans prime. Six journées de
    cette forme dans l'année. A (toujours ainsi), B (au cas par cas), C ;
  - **« Polyvalence » sur un repos** (LCI 23/09, SVE 21/09), sans aucun
    commentaire : A (venus, heures sup), B (venus, payé normalement), C
    (simple note) ;
  - **le tableau des salaires de VBN** fiche contre application, comme celui
    de LCI : le client renverra ses fiches (absentes de ce conteneur) ;
  - restes connus du rapprochement de LCI, sans question posée : le 13/04
    (cellule `N`, payé 12 h sup), la prime de rappel du 20/03 (fiche
    6 h 25 = 170,44 €, application 183,37 €) ;
  - **le chèque de récupération du flex time** : les RTT (mai) et les RHS
    (juillet) en donnent un par 8 h sur la fiche de LCI, les 8 h de flex
    time du 01/03 aucun. A (le flex time n'en donne jamais), B (cas
    isolé) ;
  - **trois chèques d'avril** : la fiche en porte 9 pour 12 journées
    indemnisées. Les deux journées payées entièrement en heures sup (11 et
    13/04) en expliquent sans doute deux ; la troisième est l'une des
    demi-journées du 05, du 08 ou du 15/04 ;
- **« remplace Y » sans rien chez Y** (26/09/2026) : le 16/01, FPA porte
  « remplace FLI » en R-CM, et FLI ne porte que « PM ». L'application les
  montre tous les deux contremaîtres en PM. A : FLI était absent ce
  jour-là. B : FLI était ailleurs à l'usine. C : au cas par cas. 16 journées ;
- **les 51 matricules** de « Polyvalence » vivent dans le dépôt public, à côté
  du trigramme. Ce fichier les tolère (« initiales ou matricule ») ; s'ils
  figurent sur les fiches de paie, ils relient le trigramme à la personne.

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
| `tools/mettre-a-jour.py` | toute la procédure en une commande, derrière sept portes |
| `tools/convertir-horaire.py` | convertit le récapitulatif Excel en JSON |
| `tools/exporter-classeur.py` | recopie TOUT le classeur anonymisé en JSON, sans rien interpréter |
| `tools/verifier-integralite.py` | confronte l'horaire au classeur entier : ce qui ne lui arrive pas |
| `tools/comparer-horaire.py` | dit ce qui change entre deux versions converties |
| `tools/comparer-fiches.py` | confronte les fiches de paie à ce que l'horaire produit |
| `tools/verifier-calendrier.js` | vérifie le calendrier, les compteurs et les manques d'effectif |
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
