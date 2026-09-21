# BIOWANZE

Simulateur de fiche de paie belge (Groupe S, CP 220) pour les équipes en
pauses de Biowanze. Application web installable, **entièrement contenue dans
`index.html`** — pas de build, pas de dépendances, pas de framework.

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
et le classeur écrit les gens de bien d'autres façons : `Nom A.`,
`P-Y. Nom`, `Nom F.(ass.Us.)`, ou le nom et le prénom dans deux
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

**La garantie a une faille de naissance, et il faut la connaître** : elle ne
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

Le client envoie régulièrement le récapitulatif Excel. La procédure :

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

Si le nombre de personnes ou de journées s'écarte nettement des repères, la
structure du classeur a bougé — vérifier la ligne des noms (10), la colonne
des jours (2) et les blocs de mois avant d'aller plus loin.

## Structure

| Fichier | Rôle |
|---|---|
| `index.html` | toute l'application (HTML, CSS, JS dans une IIFE) |
| `data/horaire-2026.json` | horaire d'équipe anonymisé, pour le pré-remplissage |
| `tools/anonymiser-classeur.py` | recopie le classeur en remplaçant les noms par les trigrammes |
| `tools/anonymiser-classeur.ps1` | le même, en PowerShell, pour les postes sans Python |
| `tools/verifier-anonymat.py` | cherche les noms de la source dans la sortie, sans rien emprunter à l'anonymiseur |
| `tools/convertir-horaire.py` | convertit le récapitulatif Excel en JSON |
| `tools/comparer-horaire.py` | dit ce qui change entre deux versions converties |
| `tools/comparer-fiches.py` | confronte les fiches de paie à ce que l'horaire produit |
| `tools/verifier-calendrier.js` | vérifie que le calendrier ne ment jamais sur le classeur |
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
  initiales ou matricule.

## Après avoir modifié `index.html`

1. Vérifier la syntaxe : extraire le contenu des balises `<script>` et lancer
   `node --check`.
2. **Incrémenter `V` dans `sw.js`** (`nfdm-vNN`). Sans ça, les installations
   existantes gardent l'ancienne page indéfiniment.
3. Tester dans un navigateur, pas seulement en unitaire. Playwright et
   Chromium sont disponibles ; servir le dossier (`npx http-server`) puis
   piloter la page. Le script étant dans une IIFE, rien n'est accessible
   depuis `page.evaluate` : il faut passer par l'interface.

## Vérifier le calendrier de tout le monde

```bash
node tools/verifier-calendrier.js
```

Confronte ce que le calendrier **affiche** à ce que le classeur **dit**, pour
les 77 personnes et les 27 462 journées. Il ne réimplémente rien : il découpe
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

Le code de retour est 1 s'il reste une faute : l'outil se branche tel quel
sur un contrôle automatique.

Pour demander à l'outil ce que l'application fait d'une journée précise —
plutôt que d'écrire un script à côté, qui réimplémenterait la lecture et
pourrait donc se tromper d'accord avec lui-même :

```bash
node tools/verifier-calendrier.js --journee FPA 0919 0921
```

**Au 20/09/2026 : 1 cellule non reconnue sur 27 462, zéro faute ailleurs.**
C'est `CAN 24/07 ["*"]`, une étoile seule, qui demande une décision du
client. Les deux autres cellules annoncées plus tôt étaient un artefact de
la découpe, corrigé depuis : d'où les épreuves d'auto-contrôle.

Une dixième règle, plus faible, liste les **mentions non comprises** : la
case s'affiche juste, mais un morceau de la cellule reste illisible. **25
journées**, regroupées par mention — `HS`, `eval`, `CPPT-F`, et d'autres,
aucune au-delà de deux journées. Elles n'empêchent rien d'afficher, mais elles
pourraient déplacer des heures : à faire trancher, une par une.

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

## Vérifier une modification du pré-remplissage

`tools/verifier-calendrier.js` fait ce contrôle et le rend chiffré — c'est
lui qu'il faut relancer, et non un script à côté. Au 21/09/2026, sur les
27 462 journées : **14 741 prestées, 4 953 absences, 156 postes prévus non
prestés, 7 612 repos**. Un écart important signale une régression.

Ces nombres ne se comparent pas aux anciens repères de la section 11 de
`docs/conversion-horaire.md`, qui comptaient autre chose : ils mesuraient la
sortie brute de `parseHoraireEntry`, alors que ceux-ci mesurent ce que la
case AFFICHE, une fois le cycle, le remplacement et l'annotation « - »
appliqués.

Second contrôle, indépendant, et il se lance lui aussi :

```bash
node tools/verifier-calendrier.js --compteurs
```

Il recalcule les compteurs flex time de chacun depuis ses journées et les
compare à ceux du pied de classeur, saisis à la main. Les neuf règles
regardent ce que la case AFFICHE ; celui-ci additionne ce qu'elle COMPTE.
**76 personnes sur 77 doivent concorder exactement** — la seule divergence
connue est une erreur du classeur (FPA, 44 h contre 41), documentée en
section 10 bis.
