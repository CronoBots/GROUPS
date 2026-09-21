# Convertir l'horaire d'équipe

Comment transformer l'horaire Excel de l'équipe en `data/horaire-2026.json`,
et comment chaque cellule doit être lue. Tout ce qui suit a été établi avec le
client, cellule par cellule, sur l'horaire 2026 (19 882 cellules, 77 agents).

Les règles de lecture sont implémentées dans `index.html`
(`parseHoraireEntry` et les fonctions qui l'entourent). **Ce document est la
source ; le code doit le suivre, pas l'inverse.**

## 1. Le format du JSON

```json
{"year":2026,
 "people":[{"id":"VBN","cat":"Contremaîtres de production",
            "d":{"0429":["-","4h +FT","presté le 27.04"]}}]}
```

- `id` — identifiant anonymisé à trois lettres. **Jamais le nom complet.**
- `cat` — la fonction (`Shift 1`…`Shift 5`, `Contremaîtres de production`,
  `Opérateurs en formation`, `Opérateurs STEP`)
- `d` — les journées, clé `MMJJ`, valeur `[cellule, annotation, commentaire]`,
  les éléments vides de fin étant omis

### Les trois champs

Chaque personne occupe **deux colonnes** dans le classeur, et ses cellules
peuvent porter un commentaire Excel :

- la **cellule** dit ce qui était prévu : un poste, une plage horaire, `-`
  pour un repos, ou une mention particulière ;
- l'**annotation** dit ce qui modifie la journée : un autre poste réellement
  presté, une absence, un compteur, un remplacement ;
- le **commentaire** est du texte libre.

C'est la distinction fondamentale :

> **La cellule dit le poste PRÉVU par la rotation.
> L'annotation dit ce qui a été RÉELLEMENT presté.**

Vérifié contre le cycle de rotation, source indépendante : là où le
commentaire nomme un poste différent de celui de la cellule, c'est la cellule
qui suit le cycle de base dans **842 cas sur 877**. Le commentaire est donc
bien la modification, et il prime.

Formes rencontrées, pour contrôler une conversion :

### Ce que le commentaire apporte

562 commentaires renvoient à une autre date ou donnent les heures exactes
d'un remplacement :

| Commentaire | Ce qu'il permet |
|---|---|
| « presté le 27.04 », « du 14/04 » | rattacher un compteur `+FT` à la journée qu'il compense — sans quoi son excédent passerait à tort en heures supplémentaires |
| « remplace GPS » | résoudre un `R-CM` en reprenant le poste de la personne remplacée |
| « Remplace FPS de 12h à 14h » | connaître les heures réelles d'un renfort |

Ces renvois ne suivent aucune règle de proximité : le compteur du 12/04
concerne le 14/04, ceux des 29 et 30/04 concernent les 27 et 28. Seul le
commentaire les apparie.

## 2. Les postes

D'après la note « Grille horaire en Pauses — 5 équipes » :

| Code | Horaire | Prime (note fiche de paie, 2020) |
|---|---|---|
| `AM` | 6h-14h | 0,67 € |
| `PM` | 14h-22h | 1,34 € |
| `N` | 22h-6h | 3,14 € |
| `D` | 7h30-16h, ½ h de midi non payée | — |

Cycle 5 équipes : 38,4 h/semaine, 192 h par cycle de cinq semaines.

## 3. Résoudre le poste d'une journée

Dans cet ordre, le premier qui répond gagne :

1. **Le commentaire nomme un poste** — `?AM`, `?PM`, `?N`, `?D` → ce poste.
   Il l'emporte sur le code franc : la journée a été modifiée.
2. **Le commentaire donne une plage dont l'équivalence est confirmée** —
   `6h-14h` → AM ; `7h-15h`, `8h30-16h30`, `H. flott.` → D.
3. **Le code franc de la cellule** — `AM`, `PM`, `N`, `D`.
4. **Déduire le poste de la plage horaire** (uniquement si rien ci-dessus) :
   - le poste dont **le début coïncide** avec le début de la plage
     (`6h-18h` → AM, `22h-10h` → N, `14h-02h` → PM) ;
   - sinon celui dont **la fin coïncide** (`18h-06h` → N, `10h-22h` → PM) ;
   - sinon le poste **le plus recouvert** par la plage.

   Ces plages ne sont **pas** des postes de 12 h : ce sont des postes normaux
   étendus. « Il fait 18h-06h, logiquement en N » — sa nuit prise 4 h en avance.

Normalisation avant comparaison : minuscules, espaces / apostrophes / points
retirés, zéros initiaux supprimés (`06h-14h` = `6h-14h` = `6h-14h`).

## 4. Résoudre la durée

Base : `hJour` (8 h par défaut).

**Une plage horaire en commentaire donne la durée réellement prestée**, selon
deux lectures :

- **elle décrit toute la journée** si elle recouvre les heures normales du
  poste, ou si elle vaut au moins une journée complète.
  *AFA 12/08, `N|?18h-06h` : 12 h. MHI 11/04, son matin jusque 17h : 11 h.*
- **elle s'ajoute au poste** si elle en est disjointe **et** plus courte
  qu'une journée.
  *JBI 31/01, `N|?19h-22h` : sa nuit plus 3 h de remplacement = 11 h.*

La seconde condition est indispensable : sans elle, un `22h-10h` commenté en
regard d'un après-midi donnerait une journée de 20 h.

## 5. Au-delà de 8 h : heures supplémentaires ou compteur

**C'est un choix de la personne, pas une règle.**

| Dans la cellule | Lecture |
|---|---|
| rien de plus | l'excédent est en **heures supplémentaires** (payées) |
| `nH +FT` | l'excédent est **épargné au compteur** flex time |

Exemples donnés par le client :

- AFA 01/08, `PM|2H +FT` — il fait son après-midi puis reste jusque minuit
  (2 h pour remplacer VBN) ; **il a choisi** de les épargner.
- AFA 01/09, `AM|?06h-18h` — il étend son matin de 4 h, rien n'est marqué :
  **4 h supplémentaires payées**.
- AFA 15/09, `?18h-06h|4H +FT` — il prend sa nuit 4 h en avance pour
  remplacer ATA : **4 h épargnées**.

Mise en œuvre : l'excédent devient un code `nH HS` de l'horaire quand il
tombe juste sur une heure entière et que la cellule ne porte pas déjà un code
d'absence ; sinon la durée réelle est conservée telle quelle et la journée
est signalée.

## 6. Le compteur `-FT` : une récupération

**La personne ne preste pas le poste prévu, ou le preste amputé d'autant.**
Le poste affiché n'est que le poste prévu.

| Cellule | Heures prestées |
|---|---|
| `8H -FT` | **0** — journée de congé |
| `D\|1H -FT` | **7** — AFA le 05/09 a terminé à 14h au lieu de 15h |
| `PM\|3H -FT` | 5 |

Du 21 au 24/09, AFA porte `8H -FT` quatre jours de suite : il est en congé,
remplacé par YPE, et l'Excel écrit « RHS » à droite de la cellule.

## 6 bis bis. « R-CM » : le poste est celui de SON cycle

Quand la cellule dit `R-CM` sans nommer de poste, c'est le **propre poste de
cycle** de la personne qui a été presté, pas celui de la personne remplacée.

> « Le 05/03 je remplace GPS en PM et non en matin, car c'était notre horaire
> de cycle normal. GPS a été repris en AM pour une commission
> d'accompagnement. » — le client

Ne **pas** reprendre le poste de la personne nommée dans le commentaire :
elle peut elle-même avoir été déplacée. Une version antérieure le faisait et
attribuait un matin là où la fiche de paie porte un après-midi.

### Ajuster le cycle, et pourquoi mensuellement

Le cycle s'ajuste sur les cellules de la personne elle-même : elles donnent
le poste prévu, `-` le repos. On cherche le triplet (cycle, binôme, décalage)
qui colle le mieux, et on s'abstient en dessous de 60 % d'accord.

**L'ajustement doit être mensuel.** Les gens changent de position dans le
cycle en cours d'année : VBN passe adjoint à contremaître le 15 septembre
2026, et cesse d'être le binôme de GPS pour devenir le contremaître n° 5. Un
ajustement annuel plafonne alors à 58 %, là où le mensuel tient entre 80 et
100 %.

Les écarts qui subsistent au sein d'un mois sont précisément les journées
intéressantes — remplacements, absences, renforts — c'est-à-dire ce que le
cycle ne peut pas prévoir.

## 6 quater. Un « - » en annotation : le poste n'a pas été presté

Quand la cellule porte un poste et que l'annotation vaut `-`, **le poste n'a
pas été presté**. Quelqu'un d'autre l'a pris, et la personne récupère une
prestation faite ailleurs.

> « Le 20/03 : repos car travaillé une nuit de plus le 18/03 pour
> remplacer. » — le client

Les commentaires le confirment systématiquement : « remplacé par JBI »,
« voir le 6/5/2026 », « voir 15.10 », « CIE : cf 18/03 ». La symétrie est
visible dans le classeur — le 07/03, GPS porte `N` / `-` avec « remplacé par
VBN », pendant que VBN porte le poste correspondant.

**109 journées** de l'horaire 2026 sont dans ce cas. Le poste reste
renseigné, c'est celui qui était prévu ; il ne donne ni heure prestée ni
prime d'équipe.

À établir : ces journées sont-elles payées comme un repos compensatoire ?

## 6 ter. Une absence ampute la journée, elle ne s'y ajoute pas

On ne peut pas prester huit heures et poser huit heures de congé le même
jour. Les heures prestées valent donc **la journée moins les heures
d'absence**, jamais les deux additionnées.

| Cellule | Heures prestées | Et aussi |
|---|---|---|
| `D\|CP` | **0** | 8 h de congé parental |
| `PM\|RTT` | **0** | 8 h de RTT |
| `D\|4H RTT` | **4** | 4 h de RTT |
| `AM\|1/2 RJF` | **4** | 4 h de jour férié |
| `?F\|3H RTT` | **5** | 3 h de RTT |

**Le compteur flex time fait exception et ne retire rien.** Le client :
« les heures de FT+ ne doivent pas être comptées comme prestées, elles ne le
seront que lorsque je les récupère en FT-, et sont payées ce jour-là comme si
j'étais venu travailler ». Une journée `PM|4H -FT` ou `D|8H -FT` garde donc
ses huit heures : elles sont payées depuis le compteur au lieu d'être
prestées. Symétriquement, un `+FT` n'ajoute aucune heure — ces heures-là sont
mises de côté, sans prime d'équipe ni heure prestée.

Vérifié sur la fiche d'avril 2026 : sans cette exception, le dimanche 26/04
(`PM|4H -FT`) ne comptait que quatre heures au lieu des huit de la fiche, et
le total dimanche tombait à 12 h au lieu de 16 h.

Le poste reste renseigné même à zéro heure : c'est le poste prévu, et il ne
donne ni prime d'équipe ni heure prestée tant que la durée est nulle.

Cette règle vaut pour **4 601 cellules** de l'horaire 2026, soit 34 466 heures
qui étaient comptées deux fois. Sans elle, un agent totalisait 1 950 heures
prestées sur l'année, ce qu'aucun horaire ne permet ; avec elle, 1 503 heures,
cohérent avec 38,4 h/semaine moins les congés.

## 6 bis. Horaire de jour, prime de pause conservée

Six mentions désignent une journée **prestée en horaire de jour** par
quelqu'un qui **conserve la prime de la pause qu'il aurait dû faire** :

| Mention | Sens |
|---|---|
| `SD26`, `SD 26` | arrêt technique — « SHUT-DOWN 2026 » figure en clair dans la colonne des mois de mars et avril |
| `F` | formation |
| `D-F`, `DF` | jour de formation — « recyclage en secourisme de 08h30' à 12h30' », « formation Feu d'éthanol » |
| `DS` | journée syndicale (formation) |
| `D-CPPT`, `CPPT` | délégation CPPT, presque toujours un mercredi |
| `DS-CE` | délégation syndicale, conseil d'entreprise, toujours un mercredi |
| `TP` | préparation de l'arrêt technique — « Prépa SD 26 power plan » revient dans les commentaires |

> « Jour de formation pour D-F, et juste pour les autres aussi ; conserve la
> prime de pause normalement effectuée dans le cycle. » — le client

**C'est le cycle qui donne la prime**, et non la cellule — laquelle est le
plus souvent occupée par la mention elle-même (`D-CPPT`, `DS-CE`, `SD26`).
On prend le poste de cycle de la personne pour ce jour-là, ajusté
mensuellement comme décrit en 6 bis bis.

Quand le cycle ne prévoit pas de poste, il n'y a pas de prime à conserver et
la journée vaut un poste de jour :

> « FLI le 16/04 prévu en repos mais fait DS, donc payé comme un D sans prime
> de pause. » — le client

**La cellule donne l'horaire presté, le cycle donne la prime.** Une cellule
`7h-15h` en face d'un `TP` dit que la journée s'est faite en horaire de jour ;
elle ne dit rien de la prime, qui reste celle de la pause prévue au cycle.

Exemples relus dans le classeur 2026 :

| Cellule / annotation | Cycle | Résultat |
|---|---|---|
| `D-CPPT` / `1h rhs` (VBN 28/01) | AM | **AM**, prime du matin conservée |
| `DS-CE` / `1h rhs` (LCI 17/06) | N | **N**, prime de nuit conservée |
| `-` / `D-F` (ATR 23/04) | repos | **D**, sans prime |

**Une absence qui couvre la journée entière l'emporte** : `?DS|VA`,
`?CP|?DS`, `?DS|RJF` restent des absences. On ne transforme pas un congé en
prestation.

Une absence **partielle**, en revanche, laisse des heures prestées :
`?F|3H RTT` vaut cinq heures de jour plus trois heures de RTT. Le client :
« JBI le 29/05 a fait F mais presté 06h-11h, car il a repris 3 h de RTT pour
partir à 11h au lieu de 14h, pour avoir ses 8 h. »

`DS-CE` (conseil d'entreprise) et `D-CPPT` ne sont **pas** couverts par cette
règle — le client ne les a pas encore décrits.

## 6 quinquies. Ce que l'horaire ne dira jamais

> « Les reprises d'heures supplémentaires sont affichées dans l'horaire, mais
> pas les HS qu'on fait et qui se mettent dans un compteur hors fichier
> Excel. » — le client

Deux conséquences, à ne pas chercher à contourner.

**Les HS déductibles le restent.** Une plage de douze heures donne quatre
heures d'excédent, et l'application les calcule : sur la fiche de mars 2026
de VBN, les huit heures supplémentaires issues des nuits `18h-6h` des 21 et
22 mars tombent exactement.

**Les prolongations ponctuelles sont hors de portée.** Quarante-cinq minutes
de plus un samedi soir, deux heures dix-sept un dimanche : ces minutes
n'existent que dans la pointeuse. Aucune cellule, aucune annotation, aucun
commentaire ne les porte. Elles se saisissent à la main, par le champ
« Heures suppl. non compensées » de l'onglet Horaire.

### Une piste écartée : le découpage des nuits

On aurait pu croire que la prime d'équipe suit le jour calendaire, une nuit
de 22h à 6h donnant deux heures au premier jour et six au suivant. **C'est
faux.** La nuit compte entièrement au jour où elle commence : c'est ainsi que
la prime de nuit du samedi tombe exactement sur les fiches de mars (16:00) et
d'avril (8:00) de VBN, là où le découpage donnerait 10:00 en mars.

## 6 bis ter. En repos et en renfort : le poste de la personne remplacée

Quand la personne était **prévue en repos** et vient remplacer quelqu'un, son
cycle ne dit rien. Le commentaire nomme alors la personne remplacée, et c'est
son poste du jour qu'on reprend.

> « Pour le 04/10, il faut regarder l'horaire normal de BLR pour savoir quand
> LHR le remplace, car ce n'est pas précisé à côté dans l'horaire de LHR
> puisqu'il était normalement en repos. Et en vérifiant BLR, c'est en N. Le
> 20/12 en AM, car c'est indiqué dans l'horaire de DKS. » — le client

**À ne pas confondre avec `R-CM`**, où c'est le propre cycle qui commande :
là, la personne avait un poste prévu. L'ordre est donc :

1. le poste écrit dans la cellule ou l'annotation ;
2. à défaut, le poste de cycle de la personne (section 6 bis bis) ;
3. à défaut, le poste de la personne nommée dans le commentaire ;
4. à défaut, pour une journée en horaire de jour, un poste de jour.

## 6 sexies. Mentions reconnues, sans effet sur le calcul

| Mention | Occurrences | Sens |
|---|---|---|
| `R` | 237 | réserve — « remplace FLI **si nécessaire** ». La personne preste son poste normal. |
| `VM` | 40 | visite médicale, chez 37 personnes différentes, jamais le week-end |
| noms d'atelier | 906 | `meunerie`, `distillation`, `terr. Arr.`, `poly. Arr.`, `Poly. Etoh`, `chaudières`, `gluten`, `Ferm. Liq.`, `STEP`, `polyvalence` |

> « Cela ne change rien à l'horaire ni aux primes, si c'est juste une
> indication de la zone de remplacement et qu'il n'y a rien d'autre de
> compromettant dans le commentaire. » — le client

`poly. Arr.`, `Poly. Etoh` et `terr. Arr.` relèvent de la même règle. Le
poste reste dans la cellule — 827 fois sur 906 — et l'atelier dit seulement
**où** la personne est allée.

Elles ne changent ni les heures ni la prime, et ne doivent pas non plus faire
signaler la journée comme douteuse.

Pour `VM`, le client : « une heure supplémentaire est comptée si elle tombe
en dehors de l'horaire, et le trajet est payé, mais par un système interne
qui ne passe pas par la fiche de paie ». Rien à calculer ici, donc.

## 7. Les absences et compteurs déjà connus

Un **commentaire qui nomme exactement un code d'absence connu est cette
absence** (`?CP`, `?RTT`). Trois cellules sur l'horaire 2026.

Codes francs repris tels quels, définis dans `ABS` (`index.html`) :
`VA`, `RTT` (et `1H`…`7H RTT`), `RJF`, `DTT`, `CP`, `CT`, `CPAR`, `FER`,
`SMG`, `FORM`, `ABS`, `SANS SOLDE`, `nH +FT`, `nH -FT`, `nH HS`.

## 8. Ce qui reste à établir

À demander au client avant d'aller plus loin.

### Les codes courts — 207 cellules encore vides

Hypothèses déduites de qui les porte et des jours où ils tombent :

| Code | Occ. | Indice | Hypothèse |
|---|---|---|---|
| `R-CM` | 326 | 6 personnes, tous postes, week-ends inclus | remplacement contremaître |
| `R` | 237 | 34 personnes, jamais seul dans la cellule | remplacement |
| `TP` | 210 | 8 personnes, surtout en poste D | ? |
| `DS-CE` | 27 | **25 fois sur 27 un mercredi** | délég. – conseil d'entreprise |
| `D-CPPT` | 47 | **31 fois sur 40 un mercredi** | délégation CPPT |
| `VM` | 40 | 37 personnes, surtout lundi | visite médicale |
| `D-F` | 49 | 26 personnes, jamais le week-end | ? |

Pour chacun : journée prestée normale, absence payée, ou absence non payée ?
Et si c'est une journée prestée, relève-t-elle de la règle « horaire de jour,
prime de pause conservée » de la section 6 bis ?

`SD26`, `F` et `DS` sont résolus — voir section 6 bis.

### Les autres points ouverts

- **Chèques-repas sur les jours `8H -FT`** — la note explicative dit que les
  récupérations y donnent droit ; le calcul ne les attribue qu'aux jours
  prestés. 396 journées concernées.
- **Opérateurs STEP** — ne s'ajustent à aucun cycle connu (24 %, contre 80 %
  ou mieux pour 62 agents sur 77). Quel cycle suivent-ils ?
- **38,4 h ou 38 h 40 ?** — la grille annonce 38,4 h/semaine, l'app a 38 h 40
  par défaut. 38 h 24 ≠ 38 h 40.

## 9. Les noms d'ateliers

`meunerie`, `terr. Arr.`, `distillation`, `poly. Arr.`, `poly. Etoh`,
`chaudières`, `gluten`, `Ferm. Liq.`, `STEP`, `polyvalence` — environ 800
occurrences, toutes orthographes confondues.

Traités comme le **lieu de travail**, sans effet sur la paie. La journée
reste signalée comme particulière. *(À confirmer par le client.)*

## 9 bis. Le poste tenu : la ligne 9

**Établi avec le client le 20/09/2026.**

Chaque feuille d'équipe porte en **ligne 9**, au-dessus du nom, le poste que
la personne tient. C'est là que se trouvait l'information dont le
convertisseur ne lisait rien : il n'allait chercher que la ligne 10.

Une personne occupe **deux colonnes** — sa cellule et son annotation — d'où
des couples : `O`+`P` désignent une seule personne.

| Colonnes | Ligne 9 | Sur les cinq feuilles |
|---|---|---|
| `C` | Adjoints Contremaître | partout |
| `G` `I` `K` `M` | *(vide)* | les cinq contremaîtres, repris de leur propre feuille |
| **`O`** | **Polyvalent** | le polyvalent **arrière** |
| `Q` | Fermentation | partout |
| `S` | Distillation | partout |
| `U` | Renfort arrière | **sauf Shift2, où c'est un renfort avant** |
| `W` | Renfort avant | Shift2, Shift4 |
| `Y` | Meunerie | partout |
| `AA` | Gluten | partout |
| **`AC` `AE`** | **Polyvalent** | après `V` : les polyvalents **avant** |
| `AG` | Chaudières | partout |
| `AM` | Renfort arrière | Shift2 seulement |

**C'est le libellé qui fait foi, pas la colonne.** La position des renforts
change d'une feuille à l'autre — en Shift2, `U` porte un renfort *avant* et le
renfort *arrière* est relégué en `AM`. Lire la ligne 9 ; ne jamais déduire le
poste du numéro de colonne, à la seule exception du couple `O`+`P`, que le
client donne comme toujours réservé au polyvalent arrière.

`O` est **vide en Shift1 et Shift5** : ces équipes n'ont pas de polyvalent
arrière. Un poste sans personne n'est pas une anomalie.

### Ce que chacun peut tenir

Le poste de la ligne 9 dit où la personne se trouve *par défaut*. Ce qu'elle
peut tenir en plus obéit à des règles distinctes :

- **Polyvalent arrière** (`O`+`P`) — tient le poste « Polyvalent arrière », et
  peut remplacer **en fermentation et en distillation** si nécessaire.
- **Renfort arrière** — tient les postes pour lesquels il a la polyvalence.
- **Polyvalent avant** (`AC`, `AE`) — tient les postes pour lesquels il a la
  polyvalence, mais se trouve **le plus souvent au gluten**. S'il n'y a pas de
  meunier et qu'il a la polyvalence, il y remplace — *si l'horaire le dit*.
- **Renfort avant** — même règle : le plus souvent au gluten, et seulement les
  postes où il a la polyvalence.

**Ce que l'application en fait, depuis le 21/09/2026.** Le client : « Terrain
arrière doit comprendre les opérateurs Polyvalent arrière ; s'ils ne sont pas
là, les Renforts arrière ». L'onglet Équipe lit donc la ligne 9 pour ce poste :
le polyvalent arrière le tient, et le renfort arrière prend le relais en son
absence — marqué « fait fonction », comme l'adjoint qui remplace un
contremaître.

**Et il faut les deux postes.** Le client : « le terrain arrière ne peut être
tenu que par quelqu'un qui possède le poste fermentation ET le poste
distillation ». Il couvre les deux ; sans l'un d'eux, on ne peut pas le
tenir — quand bien même la ligne 9 vous y place. Deux renforts arrière sont
dans ce cas, `BBZ` et `QBY`, qui n'ont pas la fermentation.

Une personne que **sa cellule du jour** envoie au terrain arrière y est de
plein droit : la cellule dit ce qui a été fait, et elle prime sur la ligne 9.

**Les polyvalents et renforts avant vont au gluten**, sous la même forme de
condition. Le client : « cela peut être une règle si l'opérateur possède bien
le poste gluten ». Dix des treize l'ont ; `YRS`, `SMK` et `GBT` ne l'ont pas
et restent sans poste par défaut — ce qui vaut mieux que de les y placer à
tort.

**Un remplacement est presque toujours écrit.** La ligne 9 donne le poste
habituel ; c'est la cellule du jour et son commentaire qui disent où la
personne était réellement — la règle qui gouverne tout ce document.

### Les cellules fusionnées

**Le poste couvre souvent plusieurs colonnes**, et une fusion ne se voit pas
dans le XML : seule la case en haut à gauche porte la valeur, les autres sont
vides. Dix personnes — deux par équipe, en `AI` et `AK` — semblaient ainsi
n'avoir aucun poste. Elles sont aux chaudières.

- `Chaudières` couvre `AG` à `AK` : **trois** opérateurs par équipe.
- `Adjoints Contremaître` couvre `C` à `M` : les **cinq** adjoints le portent.

Le convertisseur déplie donc les fusions — **mais seulement sur la ligne 9**.
Déplié partout, le mécanisme est un désastre discret : la ligne des noms est
fusionnée elle aussi, chaque personne apparaît sur ses deux colonnes, est lue
deux fois, et la conversion passe à 27 683 journées au lieu de 27 462.

### La feuille « Step » : le nom porte le poste

Sa ligne 9 est vide, et ce n'est pas un oubli : tout le monde y tient le même
poste, la **station d'épuration**. Le convertisseur le remplit d'après le nom
de la feuille — c'est la seule endroit où il déduit un poste, et la seule
feuille concernée.

### La feuille « Opérateurs »

Elle ne suit pas la même logique. Les gens qui y figurent sont **validés ou en
cours de formation** sur le poste écrit au-dessus d'eux, avec l'équipe à
laquelle ils sont rattachés — d'où des libellés comme `chaudières éq. 5` ou
`Distillation éq. 1`, qui portent le poste ET le numéro d'équipe.

## 10. Le convertisseur

`tools/convertir-horaire.py` lit le récapitulatif Excel et produit le JSON :

```
python3 tools/convertir-horaire.py Recapitulatif.xlsm data/horaire-2026.json 2026
```

Il reste **fidèle** : il recopie la cellule, la colonne d'annotation et le
commentaire sans les interpréter. Toute la lecture est faite par
l'application, si bien qu'une règle qui change ne demande pas de reconvertir.

### La structure de l'Excel

Une feuille par groupe (`Shift1` à `Shift5`, `Opérateurs`, `Step`,
`Contremaître`), plus une feuille `Personnel` qui donne la correspondance
officielle nom → initiales. **Une même personne figure sur plusieurs
feuilles** ; les lignes sont fusionnées sur l'identifiant.

Dans chaque feuille : la ligne 10 porte les noms, la colonne 2 le numéro du
jour, la colonne 1 le nom du mois écrit verticalement — ce qui délimite les
douze blocs. **Chaque personne occupe deux colonnes** : le poste, puis une
annotation. Les commentaires Excel sont attachés à l'une ou l'autre.

### L'identifiant anonyme

La feuille `Personnel` fait foi. Elle est incomplète, et la convention maison
prend le relais : **première lettre du prénom, première et dernière lettre du
nom de famille**. « Renard V » donne `VBN`, « Gilbert V. » donne `VGG`,
« Renard JJ » donne `JBI`. Les homonymes reçoivent un suffixe `-1`, `-2`.

Sur l'horaire 2026, cette règle retrouve 72 des 77 identifiants de la
conversion précédente ; les cinq autres ne diffèrent que par ce suffixe.

### Le format produit

```json
"0429": ["-", "4h +FT", "presté le 27.04"]
```

`[cellule, annotation, commentaire]`, les éléments vides de fin étant omis.
Le commentaire est anonymisé : Excel préfixe chaque commentaire du nom de son
auteur, retiré ici, y compris au milieu d'un fil de discussion.

### Ce que la conversion précédente avait perdu

L'ancien fichier `data/horaire-2026.json` ne gardait que la cellule et
l'annotation, cette dernière préfixée d'un `?` quand elle n'était pas reconnue
comme un code connu. Étaient perdus :

- **Les 11 339 commentaires**, dont 562 renvoient à une autre date
  (« presté le 27.04 », « du 14/04 », « rappel le 02/02 ») ou donnent les
  heures exactes d'un remplacement (« Remplace FPS de 12h à 14h »).
- **Le marqueur « - »**, qui est le repos. Il est écrit dans 8 384 cellules
  de l'Excel et n'apparaît nulle part dans l'ancien JSON — c'est lui que le
  client signalait pour VGG les 16 et 17/02.
- **La valeur brute de la cellule** : « 7h-15h » y était déjà traduit en `D`,
  ce qui empêchait de distinguer l'horaire écrit du poste déduit.
- **Les dates citées en commentaire** — aucune n'a survécu.
- **Le report de repos après une prestation sur un jour de repos.** FLI, prévu
  en repos le 16/04, preste une journée syndicale ; le 17/04, prévu en AM, il
  est en repos en compensation, et un commentaire de l'Excel l'explique. Le
  JSON ne porte que `"AM"` : le pré-remplissage comptera donc à tort une
  journée prestée. Le mécanisme est décrit dans la note sur les repos
  (« repos des jours 8 et 9 = repos payés, liés aux prestations de week-end
  des jours 6 et 7 »).

Un convertisseur refait doit donc conserver : le contenu de la cellule, le
contenu intégral du commentaire, et tout marqueur visuel porteur de sens
(couleur de fond, barré, gras) — à vérifier avec le client.

## 10 quinquies. Le commentaire prime aussi sur le cycle

`["R-CM","4h +FT","remplace ATA remplace GPS de 18h à 22h"]` — VBN le 27/07.
La cellule ne donne aucun poste ; le cycle ajusté du mois disait PM, et le
commentaire nomme ATA, qui était de **nuit**. Le client : « je ne fais pas PM
mais 18h-06h ». Il couvrait les quatre dernières heures de GPS, puis la nuit
d'ATA.

Le cycle est une rotation **théorique** ajustée au mois ; il se trompe
d'autant plus que la personne passe son temps à remplacer les autres. Le
commentaire, lui, nomme quelqu'un dont le poste est écrit. **Quand la cellule
ne donne rien — ni code franc, ni plage, ni journée de jour — le
remplacement l'emporte sur le cycle.** Dans tous les autres cas le poste ou sa
prime sont déjà établis et c'est le cycle qui tranche (section 6 bis).

Deux corrections sont venues avec :

- `posteDuRemplace()` ne regardait que la racine `remplac` : il prenait le
  poste de **celui qui vous remplace** pour le vôtre. « Remplacé par JBI »
  est l'inverse de « remplace JBI ». Seuls les remplacements **actifs**
  comptent désormais.
- Les heures épargnées ne sortent de la journée que si elles en font partie.
  Quand le commentaire les situe **hors du poste** — « de 18h à 22h » devant
  une nuit qui commence à 22h — elles s'ajoutent : la personne a fait son
  poste entier, plus ces heures-là.

Effet mesuré sur les 27 462 journées : **13 changent de poste, 5 changent
d'heures, +14 h sur l'année**. Les huit mois de prime de remplacement
contrôlés sur fiches restent justes au centime.

## 10 sexies. Poste et lieu dans la même cellule

`N-terr. Arr.`, `PM - poly. Arr.`, `PM-distil`, `PM-terr arr` : le poste ET
l'endroit où il se tient. Quatre journées de l'année, qui se lisaient comme
un simple nom de lieu — et le poste, pourtant écrit noir sur blanc, se
perdait. La cellule donne maintenant les deux.

## 10 quater. Une journée non prestée n'est pas un poste

`["PM","VA"]` : la rotation prévoyait un après-midi, la personne était en
congé annuel. La cellule porte le poste **prévu**, l'annotation dit qu'il
n'a pas été presté — et le calcul le sait déjà (zéro heure, section 6 bis
bis). Les deux calendriers, eux, peignaient la case en après-midi avec
l'étiquette « PM », et un point gris pour toute nuance. Six journées de
février 2026 d'affilée chez VBN, et le mois annonçait des postes que
personne n'avait faits.

**Dès qu'aucune heure n'est prestée, c'est l'absence qui fait la journée**,
et c'est elle que la case porte : son code — `VA`, `CP`, `FORM` — sur un
**trait discontinu**, qui ne ressemble à aucun poste. Le poste prévu reste
dans l'infobulle, où il répond à la seule question qu'il éclaire encore :
« qu'est-ce que j'aurais dû faire ce jour-là ? »

La vue annuelle appliquait déjà cette règle (`travaille = s && h > 0`) ; le
mois et le mini-calendrier du résumé s'y sont alignés.

Corollaire : un mouvement de flex time sur une journée de repos —
`["-","4h -FT"]` — s'affiche `4-FT` et non `-FT`. Les heures sont le seul
chiffre utile du code ; les couper ne gardait que l'étiquette.

## 10 ter. Montrer une journée dont la prime dit autre chose

Une journée de délégation, de formation ou d'arrêt technique se preste en
**horaire de jour** mais conserve la **prime de la pause qui était prévue**
(section 6 bis). Deux informations, donc, et elles ne coïncident pas :

| | |
|---|---|
| ce qui est **payé** | la pause prévue au cycle — nuit, après-midi, matin |
| ce qui est **presté** | une journée de jour, sous son code : `D-CPPT`, `SD26`, `D-F`… |

Le calendrier ne montrait que la première. VBN le 30/09, `N ǀ D-CPPT`,
s'affichait « N » : juste pour la paie, faux pour la réalité. Le client l'a
vu par hasard.

La cause était en amont : `parseHoraireEntry()` ne retenait du code que le
fait — un booléen `jour` — et non le code lui-même. Il le conserve désormais
dans `jourCode`, et la case porte les deux informations par **deux encodages
distincts** :

- le **fond** et l'**étiquette** donnent la journée **prestée** : couleur du
  poste de jour, et le code lui-même — `CPPT` plutôt que `N` ;
- un **liseré au bas de la case**, dans la teinte de la pause prévue au
  cycle, dit la **prime conservée**.

Le premier essai avait mis ces deux informations dans l'autre sens — fond du
poste payé, liseré de jour. Le client l'a refusé, et il avait raison : le
fond est ce qu'on lit d'abord, et ce qu'on lit d'abord doit être ce qu'on a
fait. Un fond violet sur une journée passée en délégation se lit « j'ai fait
une nuit », quelle que soit l'étiquette. La prime, elle, se vérifie ; la
journée, on s'en souvient.

L'infobulle l'écrit en toutes lettres — « Journée de jour (D-CPPT), prime de
nuit conservée » — la légende a son entrée, et la vue semaine porte la même
mention.

La vue annuelle a été la première servie ; le mois n'en gardait aucune trace
et continuait d'afficher « N » seul. Le code presté est donc désormais
**enregistré sur la journée** (champ `j`), et les deux autres endroits où
l'on lit un mois le montrent avec le même langage : le mini-calendrier du
Résumé (barre basse, étiquette `CPPT`) et la ligne de saisie de l'onglet
Horaire (pastille à côté du jour). Corriger la journée à la main efface le
champ — il ne décrirait plus rien.

**881 journées de 2026 sont dans ce cas**, réparties ainsi : `F` 289,
`SD26` 216, `TP` 210, `D-F` 47, `DS` 43, `D-CPPT` 40, `DS-CE` 27, `CPPT` 7,
`DF` 2.

## 10 quater. Un poste prévu n'est pas un poste presté

Une cellule porte souvent **deux choses à la fois** : le poste prévu par la
rotation, et ce qui l'a remplacé. VBN à la fin d'octobre :

| Jour | Cellule | Ce que ça veut dire |
|---|---|---|
| 23 au 25/10 | `N ǀ RJF ǀ remplacé par ATR` | trois nuits prévues, prises en récup. de jour férié |
| 28 et 29/10 | `AM ǀ RJF ǀ remplacé par ATR` | idem en matin |
| 30/10 | `PM ǀ VA ǀ remplacé par ATR` | après-midi prévu, pris en vacances annuelles |

`parseHoraireEntry()` lisait tout cela correctement — absence reconnue, zéro
heure prestée — et le calcul de la fiche en tenait compte. C'est le
**calendrier** qui fautait : il affichait le poste dès qu'il y en avait un,
et une semaine de vacances passait pour une semaine de travail.

La règle est désormais explicite, et **c'est le nombre d'heures qui
tranche** : une journée n'est prestée que si elle porte un poste **et** des
heures. Sinon l'absence fait la journée, le poste prévu passant en mention
dans l'infobulle.

L'erreur ne coûtait rien en euros mais faussait les totaux de bout en bout.
Pour VBN 2026 : **184 journées prestées, 90 d'absence, 87 de repos** — là où
le calendrier annonçait 269 prestées et 12 d'absence, soit 85 congés comptés
comme du travail, et une moyenne de 5,4 h par journée prestée au lieu de 7,9.

## 10 bis. Ce que le convertisseur lit hors de la grille des jours

Le classeur ne se réduit pas à ses douze blocs de mois. L'onglet `Config` le
dit lui-même : « les lignes de 11 à 376 sont consacrées à l'horaire, les
lignes de 377 à 420 aux compteurs ».

### Le pied de feuille (lignes 377 à 440)

Il se lit comme les journées : le **libellé dans la colonne de la personne**,
la **valeur dans la colonne d'annotation**. Ces valeurs sont saisies, pas
calculées — 1 099 cellules contre 12 formules sur la feuille des
contremaîtres. Aucun calcul ne les retrouve depuis l'horaire.

Les titres de section sont écrits à gauche, dans les deux premières colonnes,
mais **au milieu de leur bloc** et non en tête. D'où des bornes explicites,
vérifiées en cherchant le titre attendu à l'intérieur du bloc ; s'il manque,
la structure a bougé et les compteurs sont ignorés plutôt que lus de travers.

| Bloc | Lignes | Contenu |
|---|---|---|
| `prevision` | 377-394 | congés prévus : VA, RTT (détail 1h à 7h), DTT, RJF |
| `solde` | 395-402 | soldes en heures au 1er janvier, soldes 2025 inclus |
| `restant` | 403-408 | soldes restants compte tenu des prévisions |
| `flex` | 409-430 | compteurs flex time, détail de 1 h à 8 h puis totaux |
| `conges` | 431-440 | CP et « à planifier », dont la position varie |

Dans le bloc des prévisions, un libellé qui revient est un total et prend le
suffixe `Total` : VBN a 40 h de RTT en journées entières plus 14 h prises à
l'heure, soit `RTT: 40` et `RTTTotal: 54`.

Ailleurs, un libellé qui revient est un **compteur distinct**, numéroté. Le
client a deux lignes `CP` parce qu'il a terminé le congé parental pris pour
sa fille et en a ouvert un second pour son fils en cours d'année : `CP: 5` et
`CP2: 21`, soit les 26 journées marquées `CP` dans son horaire — cinq en
janvier et février, vingt et une d'avril à décembre, avec un mois de mars
sans aucune entre les deux.

Le « Total » du bloc flex time est renommé **`report`**, parce qu'il n'est
pas un total. Le client : « les compteurs totaux sont repartis d'où ils
étaient en fin d'année 2025, donc des valeurs manuelles avaient été rentrées
en début d'année ». C'est le solde reporté de l'année précédente, saisi à la
main — VBN commence 2026 à −5 h, et ses +55 / −53 de l'année ne s'y ajoutent
pas. Le nommer « Total » aurait invité à les additionner.

### Les compteurs comme contrôle

Recalculer les compteurs flex time depuis les journées et les comparer à ceux
du pied de classeur met le convertisseur à l'épreuve : les premiers sont
déduits de 27 462 cellules, les seconds saisis à la main. **Soixante-seize
personnes sur soixante-dix-sept concordent exactement**, dans les deux sens.

La seule divergence est une erreur du classeur, pas de la conversion. FPA a
repris 44 h en flex time, son compteur en compte 41 : le 07/11, « 3h -FT »
est écrit dans la colonne du poste et « poly-arr » dans celle de
l'annotation. Les deux inversées, les totaux du classeur — qui comptent la
colonne d'annotation et rien d'autre — passent à côté. La journée du 12/12
porte les deux mêmes mentions, dans le bon ordre, et compte normalement.

`colonnes_inversees()` cherche ce cas à chaque conversion. Une seule
occurrence sur l'année 2026.

### Ce que ces compteurs ne sont pas

Ils ne remplissent **aucun** champ de la fiche. Les trois champs « en attente
au 1er du mois » de l'onglet Horaire sont des restes d'arrondi qui passent
d'un mois au suivant, entre zéro et sept heures ; le classeur, lui, donne des
soldes de congé annuels. Les confondre fausserait le nombre de chèques-repas.

L'application les affiche donc pour ce qu'ils sont, sous les sélecteurs du
pré-remplissage : un repère, et de quoi contrôler ce que l'horaire a produit.
Les totaux flex time sont à ce titre précieux — ils recoupent exactement ce
que l'application calcule depuis les journées.

### Une personne, plusieurs feuilles

Les adjoints contremaître sont recopiés sur les cinq feuilles d'équipe, à
l'identique : 365 journées, aucune divergence avec la feuille des
contremaîtres. La feuille où quelqu'un est recopié pour référence ne doit pas
décider de sa catégorie — c'est celle de son propre groupe qui compte.

L'ordre de `FEUILLES` porte donc cette règle : les feuilles spécialisées
d'abord (contremaîtres, STEP, opérateurs en formation), les équipes ensuite.
ATR, FPA, JBI, VGG et YBT figurent maintenant chez les contremaîtres, et non
plus en Shift 1 — qui gagnait simplement parce qu'il était lu en premier.

### Deux personnes, les mêmes initiales

La règle des initiales — première lettre du prénom, première et dernière du
nom — n'est pas injective. Quatre collisions dans le classeur 2026 : `CDE`,
`GBT`, `NPE` et `PDR` désignent chacune deux personnes bien distinctes, sur
des feuilles différentes. Elles ont toujours été séparées, la seconde prenant
un suffixe `-1`.

Ce qui manquait, c'est la **stabilité** du suffixe. Il était attribué dans
l'ordre de lecture des feuilles : changer cet ordre échangeait les deux
identifiants d'une conversion à l'autre, et le pré-remplissage d'un mois
basculait en silence sur quelqu'un d'autre. C'est arrivé en mettant les
feuilles spécialisées en tête — un opérateur de Shift 2 avec 365 journées
s'est fait prendre son identifiant par un arrivant qui en comptait 17.

L'ordre est désormais tiré des données, jamais des feuilles :

1. l'identifiant officiel de l'onglet `Personnel` passe avant celui que la
   règle des initiales a calculé ;
2. à défaut, la fiche la plus fournie ;
3. à défaut, le nom normalisé.

Le convertisseur annonce chaque collision sur sa sortie d'erreur, et
l'application signale un identifiant suffixé sous les sélecteurs du
pré-remplissage — rien d'autre ne permettrait de s'en apercevoir, puisque le
dépôt ne porte aucun nom.

### Trigrammes corrigés à la main

La règle des initiales peut tomber sur un trigramme que quelqu'un d'autre
porte déjà officiellement. Rien ne le laisse voir : ni l'un ni l'autre n'a
l'air faux. Le client en a signalé deux, et `CORRECTIONS` les porte :

| Correction | Pourquoi |
|---|---|
| `NPI` | opérateur gluten arrivé en septembre ; `NPE` revient à l'opérateur de Shift 2, qui le porte depuis janvier |
| `JBA` | `JBY` est le trigramme d'un responsable, pas celui de cet opérateur |
| `CHD` | le second `CDE`, en équipe 4 ; `CDE` reste à celui de l'équipe 5 |
| `GBO` | le second `GBT`, en équipe 4 ; `GBT` reste à celui de l'équipe 5 |
| `PDF` | le second `PDR`, en équipe 1 ; `PDR` reste à celui de l'équipe 3 |
| `CDE` | maintien confirmé pour celui de l'équipe 5, l'onglet `Personnel` portant un troisième nom sous ce trigramme |

Ces trigrammes se recoupent avec l'usage du classeur : les commentaires de
l'horaire citent `CHD` 27 fois, `PDF` 36 fois et `JBA` 20 fois. Avant
correction, ces renvois ne désignaient personne — `posteDuRemplace()` ne
pouvait pas les résoudre. `JBY`, cité 9 fois, reste sans correspondance :
c'est un responsable, qui ne figure pas dans l'horaire.

La clé de la table est l'**empreinte du nom normalisé**, pas le nom : elle
vise une personne précise sans que le dépôt porte son identité. Elle ne
protège que de la lecture — qui a le classeur a les noms — mais elle suffit à
tenir la règle « aucun nom complet dans le dépôt ». Une correction prime sur
l'onglet `Personnel` comme sur la règle des initiales : c'est une décision,
pas une déduction. Si son empreinte ne correspond plus à personne, le
convertisseur le signale : le nom a changé d'orthographe dans le classeur.

Le convertisseur cherche désormais ces cas tout seul. Il compare chaque
trigramme calculé aux trigrammes officiels de l'onglet `Personnel` : quand
l'un d'eux est déjà attribué à un nom qui ne ressemble pas au sien, il le
dit. Au-dessus de 72 % de similitude, c'est la même personne écrite
autrement et la règle est simplement tombée juste — huit cas dans le
classeur 2026, tous sans conséquence.

Trois trigrammes restent signalés — `SBZ` en équipe 2, `FLN` en équipe 3 et
`FPS` en équipe 4 — mais le signalement est faible, et l'onglet `Personnel`
en est la cause plus que la preuve : il porte 55 noms quand l'horaire en
compte 77, il en ignore 49, et 27 des siens ne figurent plus dans l'horaire.
Son titulaire officiel est le plus souvent quelqu'un qui est parti.

Rien ne contredit ces trois trigrammes dans les données : personne ne s'y
cite soi-même en commentaire, exactement comme les trigrammes dont on est
sûr. Ils sont donc tenus pour justes, et le convertisseur se contente de les
signaler.

`JBY` était d'une autre nature : son titulaire officiel travaille toujours
là, comme responsable, et seul le client pouvait le dire.

Enfin, des trigrammes cités dans les commentaires ne correspondent à personne
dans l'horaire — `PBL` 160 fois, `MPE` 60, `LDT` 40. Ce sont des gens
extérieurs aux huit feuilles converties. `posteDuRemplace()` ne peut pas
résoudre un remplacement qui les nomme.

### Les autres onglets

| Onglet | Ce qui en est tiré |
|---|---|
| `Config` | la date de dernière mise à jour du classeur, portée en tête du JSON |
| `Polyvalence` | le degré et les ateliers de chacun, rattachés à l'identifiant à trois lettres ; matricules, noms et prénoms restent dehors |
| en-tête des feuilles | la légende des codes : VA, RTT, RHS, RJF |
| `Personnel` | la correspondance nom → initiales, déjà utilisée |
| `Récapitulatif (1)` | **rien** : 13 453 de ses cellules sont des formules qui pointent vers les feuilles d'équipe, contre 567 valeurs saisies. Tout y est déjà dans l'horaire ; l'embarquer doublerait le fichier sans rien apporter |

## 11. Contrôler une conversion

Repères sur l'horaire 2026, à comparer après toute reconversion :

| Mesure | Valeur |
|---|---|
| personnes | 77 |
| journées du classeur | 27 462 |
| dont journées de repos « - » | 7 580 |
| journées pré-remplies | 19 836 |
| journées non reconnues | **46** (0,2 % des journées travaillées) |
| commentaires conservés | 6 588 |
| renvois de date exploités | 150 |
| remplacements résolus par commentaire | 19 |
| heures prestées | 119 226 h |
| heures supplémentaires déduites | 759 h |
| durée maximale retenue | 9,75 h |

Un chiffre très différent sur un horaire comparable signale une régression.
