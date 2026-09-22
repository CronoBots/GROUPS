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
XML** (`I` puis `stasse, Prénom`) : un motif appliqué balise par balise ne
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

**Elle prend toute la largeur, sur sa propre ligne.** Le client, le
22/09/2026 : « pourquoi ne pas utiliser toute la largeur de la barre du
haut ? il faut écrire aussi la date du jour près de la pause prévue
aujourd'hui ». Serrée sous le nom de l'application, la moitié droite de sa
ligne restait vide sous le sélecteur de mois. Sur sa propre bande elle porte
le trigramme, **la date du jour** et le poste — la date étant ce à quoi
« nuit » se rapporte : sans elle, la pause annoncée ne dit pas de quel jour
elle est.

Elle coûte 36 px de barre collante sur téléphone (55 → 91). C'est le prix de
la rangée, et il est assumé.

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
lui qu'il faut relancer, et non un script à côté. Au 21/09/2026, sur les
27 462 journées : **14 657 prestées, 5 074 absences, 156 postes prévus non
prestés, 7 575 repos** (classeur du 21/09/2026 à 17 h 35). Un écart important
signale une régression — mais un nouveau classeur en déplace légitimement :
deux absences longues y sont apparues, APN et QDE.

Ces nombres ne se comparent pas aux anciens repères de la section 11 de
`docs/conversion-horaire.md`, qui comptaient autre chose : ils mesuraient la
sortie brute de `parseHoraireEntry`, alors que ceux-ci mesurent ce que la
case AFFICHE, une fois le cycle, le remplacement et l'annotation « - »
appliqués.

### La polyvalence a son onglet

Le client, le 22/09/2026 : « les polyvalences doivent être affichées dans un
onglet à part ». Elles vivaient sous chaque personne de l'annuaire, en
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

**Huit onglets, et « Polyvalence » est le plus long** : la barre débordait de
44 px à 320 et de 4 px à 360. Un demi-point de moins et deux pixels de moins
de chaque côté sous 375 px, et les huit rentrent — mesuré, pas estimé : la
somme des intitulés fait 326 px à 10,5 et 295 à 9,5. La règle se pose APRÈS
celle qui définit la barre mobile : à spécificité égale c'est la dernière qui
gagne, et une première tentative posée trois cents lignes plus haut n'avait
rien changé du tout.

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

### Les manques d'effectif à venir

```bash
node tools/verifier-calendrier.js --manques [MMJJ]
```

Mesure ce que le module « Postes en manque » de l'onglet Équipe annoncera,
de la date donnée à la fin de l'horaire. Il ne le simule pas : il découpe
`equipeDuJour()` et `postesDePause()` dans `index.html` et les rejoue. Une
alerte qui compterait autrement que la vue du jour serait pire que pas
d'alerte.

**Au 22/09/2026 : 12 journées sur 102, 14 places creuses** — fermentation
(6), terrain arrière (3), chaudières (2). Si ce nombre s'effondre ou explose
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
ne se comble plus.

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

**Les intitulés de poste restent abrégés et horizontaux**, et la légende
reste SOUS la grille. Une version verticale en toutes lettres et une légende
remontée ont vécu une demi-heure : « j'aimais bien les postes écrits comme
avant ». Les deux tenaient à toutes les largeurs — ce n'était pas la
question. **Deux mots de retour valent mieux que trois hypothèses**, et il a
fallu demander pour trouver la bonne.

**La liste est alphabétique, sans intercalaire d'équipe** : on cherche
quelqu'un par son trigramme, pas par son équipe.

**Au 22/09/2026 : 33 couples personne-poste au quota sur 101, dont 23 où la
polyvalence est acquise sans un seul remplacement** — mesuré identique par
l'outil et par le navigateur.

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
