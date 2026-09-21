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

| Cellule | Heures **présentes** |
|---|---|
| `8H -FT` | **0** — journée de congé |
| `D\|1H -FT` | **7** — AFA le 05/09 a terminé à 14h au lieu de 15h |
| `PM\|3H -FT` | 5 |

**Ce sont les heures PRÉSENTES, pas les heures PAYÉES.** Les heures reprises
au compteur sont payées comme si la personne était venue — voir
« Le compteur complète une journée écourtée » dans `docs/regles-paie.md`.
Une journée portant un `-FT` vaut donc ses huit heures sur la fiche.

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

## 6 septies. « pris le JJ.MM » : l'annotation appartient à un autre jour

**Confirmé par le client le 21/09/2026.** À propos de FPA le 21/09 : « FPA
est indiqué "2h -FT" alors qu'il s'agit d'un commentaire qui dit bien que
c'est pour un autre jour. Il faut faire attention à tous les commentaires ! »

```
FPA 21/09  ["-", "2h -FT", "pris le 19.09 arrivée à 0h00'"]
FPA 19/09  ["N", "R-CM",   "remplace FLI de 0h à06h00'"]
```

Le classeur écrit ces heures **deux fois** : sur le jour où le quota était
prévu — une case de repos portant « pris le JJ.MM » — et sur le jour où il a
réellement été consommé. Les appliquer des deux côtés les compte double :

```
QDE 13/06  ["-", "4h -FT", "pris le 12.06"]      ← le renvoi
QDE 12/06  ["7h-15h", "4h RTT"]                  ← le compteur réel
```

**26 journées** portent « pris le JJ.MM ». Dans **12** d'entre elles, la
journée visée porte déjà son propre compteur ; trois l'écrivent même en
toutes lettres dans leur commentaire — `["PM","4h -FT","+4h RTT"]`.

### La règle

**Le client, le 21/09/2026, les a toutes tranchées une par une** — « CKS oui
ça complète le 25/07, VGG aussi, GJR aussi le 08/04, CWN aura fait 10-20 car
aura repris 2 h RTT en plus fin de journée, PAM aussi c'est pour le 12/09 **en
plus de ses -FT**, HKB pareil. Les commentaires sont justes s'il reporte sur
une autre journée. »

> L'annotation appartient au jour que le commentaire nomme, **en plus** du
> compteur que ce jour porte déjà. Le jour où elle est écrite n'en garde rien.

`renvoisDuMois()` est la jumelle de `epargnesDuMois()`, dans l'autre sens :
celle-ci part du jour qui écrit « pris le 12.06 » et rend ce que reçoit le
12 juin. Elle balaie l'année entière — VBN renvoie du 23/07 au 01/08, d'un
mois à l'autre.

La journée visée peut donc porter deux compteurs : le sien et celui qu'on lui
renvoie. C'est le champ `ax` du mois, à côté de `a`.

| | Écrit | Avant | Après | Journée visée | Avant | Après |
|---|---|---|---|---|---|---|
| CKS 26/07 | `["PM","5h RTT","pris le 25.07"]` | 3 h | **8 h** | `25/07 ["PM","3h -FT"]` | 8 h | **3 h** |
| VGG 02/11 | `["AM","4h RTT","pris le 03.11"]` | 4 h | **8 h** | `03/11 ["AM","1/2VA"]` | 4 h | **0 h** |
| GJR 07/04 | `["AM","3h RTT","pris le 08.04"]` | 5 h | **8 h** | `08/04 ["PM","1/2VA"]` | 4 h | **1 h** |
| CWN 25/06 | `["AM","2h RTT","pris le 26.06"]` | 6 h | **8 h** | `26/06 ["10h-22h","4h +FT"]` | 8 h | **6 h** |
| PAM 13/09 | `["PM","2h RTT","pris le 12.09"]` | 6 h | **8 h** | `12/09 ["Ferm. Liq.","3h -FT"]` | 8 h | **6 h** |
| HKB 08/05 | `["PM","1h -FT","pris le 09.05"]` | 8 h | 8 h | `09/05 ["PM","1h RTT"]` | 7 h | **6 h** |

CWN le 26/06 tombe exactement sur ce que dit le client : 10 h-22 h moins
2 h RTT reprises en fin de journée, soit 10 h-20 h — **six heures** après les
quatre épargnées au flex time.

### Ce qui prouve que le report ne perd rien

Trois journées visées portent le renvoi **écrit dans leur propre commentaire** :
`["PM","4h -FT","+4h RTT"]` chez ATR le 28/06, `["N","1/2VA","+4h RTT"]` chez
JBI le 24/06, `["AM","7h RTT","+1h -FT"]` chez QBY le 24/10. La somme y tombe
juste — zéro, zéro et une heure. Le classeur écrit donc lui-même l'addition que
la règle fait.

Et le contrôle des compteurs, `node tools/verifier-calendrier.js --compteurs`,
donne **76 personnes sur 77** avant comme après, avec la même unique divergence
connue : FPA, 44 h contre 41, l'inversion de colonnes du 07/11. Le pied de
classeur additionne les compteurs là où ils sont ÉCRITS — un report déplace
donc l'heure de jour, jamais de total.

## 6 octies. Une journée de plus de 8 h ne donne qu'UNE prime de pause

**Tranché par la fiche de paie, le 21/09/2026.** La question était posée : une
plage de 12 h traverse deux pauses — `18h-06h` couvre la fin d'après-midi
(18 h-22 h) **et** toute la nuit. Faut-il une prime par pause traversée ?

**Non.** La fiche d'avril 2026 de VBN le dit sans ambiguïté. Ce mois-là,
VBN fait trois nuits `18h-06h` (les 14, 27 et 28) et trois après-midi
ordinaires (les 24, 25 et 26) :

| | Fiche | Application |
|---|---|---|
| Suppl. Équipe Matin | 13:00 | 13,00 |
| Suppl. Équipe Après-Midi | 24:00 | 24,00 |
| Suppl. Équipe Nuit | 88:45 | 88,00 |

Les 24 h d'après-midi sont **exactement** les trois après-midi ordinaires.
Si les 18 h-22 h des trois nuits longues donnaient droit à une prime
d'après-midi, la fiche en porterait **36**. Elle en porte 24.

Et la nuit ne compte pas 12 h non plus : 88 h, soit onze nuits à 8 h. Une
prime, celle du poste retenu.

Les 45 minutes d'écart sur la nuit sont une ligne `8:45 Suppl.Equipe Nuit à
4,00 à 200%` — un dimanche de nuit prolongé de trois quarts d'heure, pas une
règle.

Ce qu'il advient des heures au-delà de huit reste inchangé : elles partent
aux heures supplémentaires ou au compteur flex time selon l'annotation. Le
classeur l'écrit lui-même — `12/04 ["-","4h +FT","du 14/04"]`,
`29/04 ["-","4h +FT","presté le 27.04"]`, `30/04 ["-","4h +FT","presté le
28.04"]`.

À ne pas confondre avec le découpage des nuits (section 6 quinquies), qui
était déjà tranché : une nuit compte entièrement au jour où elle commence.

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

### Audit des 6 643 commentaires — 21/09/2026

Le client : « vérifie tous les commentaires et qu'ils sont respectés. »
Recensement de ce que les commentaires **disent**, confronté à ce que le code
en **fait**.

| Ce que le commentaire dit | Journées | Lu ? |
|---|---|---|
| `remplace XXX` | 3 632 | **oui** |
| `remplacé par XXX` | 1 738 | non — volontairement |
| `échange avec XXX` | 990 | non — la cellule porte déjà la pause échangée |
| plage `de Xh à Yh` | 466 | **oui** |
| `rappel` | 462 | **oui** |
| départ / arrivée | 476 | non — mais 459 ont un compteur qui l'explique |
| **`conserve la prime de X`** | **336** | **NON — voir ci-dessous** |
| renvoi de date | 217 | **oui** |
| effectif / renfort / « ne compte pas » | 47 | non |
| heures sup. écrites dans le commentaire | 20 | non |
| rien de reconnaissable | 1 201 | — |

#### Ce qui est sans conséquence

`remplacé par XXX` est exclu **à dessein** : le lire comme un remplacement
actif inverserait le sens. La personne qui remplace porte l'information de son
côté, et c'est elle qu'on lit.

`échange avec XXX` n'apprend rien de plus : la cellule porte déjà la pause
échangée — `GPS 28/01 ["+CPPT","18h-06h","Echange avec ATA"]` dit 18h-06h.

Départ et arrivée sont presque toujours doublés d'un compteur qui les chiffre.
**17 journées** font exception, et elles se lisent une par une.

#### Ce qui touche à la paie : « conserve la prime de X »

**336 journées** portent « conserve sa prime de N », « maintien prime de
nuit », « conserve sa prime de pause ». L'application n'a aucune règle qui les
lise : elle applique la prime du poste qu'elle a retenu.

Dans **270 de ces journées, le poste retenu ne correspond pas à la prime
nommée** :

```
AFA 04/09  ["N","7h-15h","… conserver prime de nuit …"]    → l'app retient D
AFA 26/02  ["PM","","… conserver prime de nuit"]            → l'app retient PM
ATA 06/05  ["-","AM","remplace AFA; conserver prime de nuit"] → l'app retient AM
ATR 16/09  ["D","chaudières","Conserve sa prime de AM …"]   → l'app retient D
```

L'écart se chiffre : une journée de huit heures vaut 0 € en prime de jour,
14,40 € en après-midi, **32,00 € en nuit**. La répartition des 336 : 219 fois
la nuit, 39 l'après-midi, 38 « nuit » écrit en toutes lettres, 37 « pause »,
2 le matin, 1 le dimanche.

**Rien n'a été changé** : cela touche des montants, sur 270 journées et
beaucoup de personnes. Il faut que le client tranche — et notamment ce que
« conserve sa prime de pause », sans nommer laquelle, doit valoir.

#### Ce qui reste plus petit

Vingt journées portent des heures supplémentaires **dans le commentaire seul**
— `["11h-15h30'","4h +FT","+0,5 hs"]`, `["14h-02h","1h +FT","+3h hs"]`. Le
compteur de l'annotation est lu, ces heures-là non.

Et le classeur écrit parfois la règle d'effectif en toutes lettres :
`VGG 04/08 ["7h-15h","chaudières","Ne compte pas comme un effectif chaudières
…"]`.

### Les autres points ouverts

- **Le précompte du double pécule de vacances** — la fiche de mai 2026 porte
  (montant retiré) ; l'application donne (montant retiré) ou (montant retiré) selon la façon dont on
  y range le simple pécule. Aucune combinaison simple ne tombe juste. Voir
  « Le pécule de vacances et le treizième mois » dans `docs/regles-paie.md`.
  *(Le treizième mois, lui, tombe au centime.)*

- **Chèques-repas sur les jours `8H -FT`** — la note explicative dit que les
  récupérations y donnent droit ; le calcul ne les attribue qu'aux jours
  prestés. 396 journées concernées.
- **Opérateurs STEP** — ne s'ajustent à aucun cycle connu (24 %, contre 80 %
  ou mieux pour 62 agents sur 77). Quel cycle suivent-ils ?
- ~~**38,4 h ou 38 h 40 ?**~~ — **tranché par la fiche, le 21/09/2026** : elle
  écrit `Nombre heures / semaine temps plein / 38:40`. Ce n'est donc pas
  38,4 h (qui vaudrait 38 h 24) mais bien **38 h 40**, la valeur de
  l'application. La grille écrivait une durée en heures et minutes avec une
  virgule.
*(La question des primes des journées de plus de 8 h est tranchée — voir la
section 6 octies.)*

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

### La cellule fusionnée des chaudières, et qui n'y appartient pas

**Confirmé par le client le 21/09/2026.** Dans les cinq feuilles d'équipe,
« Chaudières » est écrit une fois pour **trois colonnes** — AG, AI et AK —
alors que le poste attend deux personnes. Tout le monde en dessous hérite du
libellé, y compris le polyvalent avant rangé dans l'une de ces colonnes.

Le client : « GBT qui n'a que chaudière, c'est normal qu'il soit aux
chaudières ; par contre l'autre opérateur ne possédant pas les chaudières est
celui qui est polyvalent avant, donc gluten ou meunerie selon sa polyvalence,
mais **par défaut au gluten** ».

C'est donc la **polyvalence** qui tranche, pas la ligne 9 :

| Équipe | Sous « Chaudières » | Sans la polyvalence chaudières |
|---|---|---|
| Shift 1 | DWS, KDN, PDF | **PDF** → gluten |
| Shift 2 | ADS, GJR, QDE | aucun |
| Shift 3 | ADK, JBA, LAX | **JBA** → gluten |
| Shift 4 | GBO, JBS, MHI | **GBO** → gluten |
| Shift 5 | LDY, RCO, SPS | aucun |

GBT fait le chemin inverse : sa ligne 9 dit « Polyvalent », mais sa
polyvalence ne porte que les chaudières — il y va, et le client le confirme.

**La règle ne s'applique que si la polyvalence est CONNUE.** Polyvalence
inconnue n'est pas polyvalence vide, et la confondre déplaçait des gens sur
un trou — voir juste dessous.

**Reste ouvert** : dans les Shifts 2, 4 et 5, les trois personnes possèdent les
chaudières. La polyvalence ne peut alors rien départager, et l'effectif y
paraît encore à trois pour deux. À faire trancher.

### La polyvalence se cherche sur le VRAI trigramme

**Le client, le 21/09/2026** : « dans le fichier Excel il faut prendre leur
polyvalence sur leur vrai trigramme, sauf pour celui qui a un nom compliqué
et qui devient PDF car PDR existe déjà. »

`CORRECTIONS` renomme des personnes dont le trigramme calculé tombait sur
celui d'un autre : **PDF** (l'autre PDR), **JBA** (JBY est au responsable),
**CHD** (l'autre CDE). Mais l'onglet Polyvalence, lui, les inscrit toujours
sous leur **ancien** trigramme — et c'est là, nulle part ailleurs, qu'il faut
aller les chercher.

Or `polyvalence()` rattachait par le trigramme d'arrivée, et `out[ident] =
fiche` écrasait sans rien dire. Ce que porte l'onglet :

| Ligne | Trigramme | Ateliers | Ce qui se passait |
|---|---|---|---|
| 7 | GBT | Gluten | **écrasée** par la ligne 53 |
| 53 | GBT | Chaudières | gardée, sur un seul des deux GBT |
| 62 | JBY | Chaudières | **perdue** — plus personne ne portait JBY |
| 8 | PDR | Distillation | va au PDR qui l'a ; PDF n'a aucune ligne |
| 31 | CDE | Fermentation | va au CDE qui l'a ; CHD n'a aucune ligne |

D'où des opérateurs à `poly: null` alors que leur polyvalence est écrite noir
sur blanc — **JBA tient les chaudières**.

Le convertisseur rattache désormais par le trigramme réel, garde **toutes**
les lignes d'un même trigramme, les départage par le nom, et **dit** ce qu'il
n'a pas pu départager plutôt que d'en écraser une.

**Le nom ne se compare pas tel quel.** L'horaire écrit `Nom G`, l'onglet
Polyvalence reconstruit `Nom G.` depuis ses colonnes nom et prénom : un
point d'écart, et les deux GBT ne se départageaient plus. `_cle_nom()` ne
garde que les lettres. Elle ne sert **qu'à comparer** — la clé des fiches ne
bouge pas, puisque les empreintes de `CORRECTIONS` sont calculées dessus.

**Le « sauf pour » de la règle.** Une personne est écrite au long dans
l'onglet Polyvalence — surnom de famille complet — et en court dans
l'horaire : ni son trigramme (`PDE` d'un côté, `PDR` de l'autre) ni son nom
ne concordent. Le client : « il faut prendre leur polyvalence sur leur vrai
trigramme **sauf** pour celui qui a un nom compliqué et qui devient PDF ».
Une entrée de `CORRECTIONS` sur le nom long l'envoie directement à `PDF` —
c'est ce « sauf », et il faut bien un endroit où le dire. Sans elle, sa
polyvalence (chaudières et STEP) partait à quelqu'un d'autre.

### Ce que la correction a rendu, le 21/09/2026

Le classeur reconverti ne change **aucune journée** : l'écart tient tout
entier dans la polyvalence de cinq personnes, et dans un identifiant.

| | Avant | Après |
|---|---|---|
| `GBO` | — | devient **`GBT-1`** |
| `GBT` (équipe 5) | Chaudières | **Gluten** |
| `GBT-1` (équipe 4) | *(rien)* | **Chaudières** |
| `JBA` | *(rien)* | **Chaudières** |
| `CHD` | *(rien)* | **Fermentation** |
| `PDF` | *(rien)* | **Chaudières, STEP** |
| `PDE` | Chaudières, STEP | **Fermentation, Distillation, STEP** |

`PDE` portait la polyvalence de `PDF` : une septième erreur, silencieuse
elle aussi.

### Deux GBT, et non un renommage

**Le client, le 21/09/2026** : « il faut annuler ma demande de renommage de
GBO, il doit y avoir 2 GBT — un aux chaudières et l'autre au Gluten/Meunerie. »

Ce ne sont pas deux écritures d'une même personne : ce sont deux personnes qui
portent réellement les mêmes initiales. La correction `GBO` est retirée, et le
suffixe des trigrammes partagés — **`GBT` et `GBT-1`** — reprend son office.
Les deux lignes de l'onglet Polyvalence, Gluten et Chaudières, leur reviennent
une chacune.

**L'anonymiseur avait la même lacune** que le convertisseur, et plus grave :
il écrivait le trigramme calculé sans consulter `CORRECTIONS`, si bien que
`data/classeur-2026.xlsx` — la copie de référence — pouvait confondre deux
personnes là où le JSON les distingue. Une copie de référence qui confond deux
personnes perd précisément ce qu'on vient y chercher. Il applique
`CORRECTIONS` à son tour.

**Le suffixe ne se montre jamais.** Le client : « tu peux garder en mémoire
pour toi `GBT-1` pour t'y retrouver, mais il ne faut jamais afficher `GBT-1`
mais `GBT` sur l'app ». Deux personnes portent réellement les mêmes
initiales ; le suffixe est une commodité de l'application, pas leur nom.
`idLisible()` le retire partout où un identifiant s'affiche. Seule exception,
et elle est de sécurité : si deux personnes du **même groupe** le
partageaient, la liste de choix donnerait deux entrées identiques — celles-là
garderaient leur suffixe. Les deux GBT sont dans deux équipes différentes.

La feuille des opérateurs en formation est hors de cette règle : le libellé
au-dessus d'eux nomme le poste sur lequel ils se forment, et n'est pas une
cellule fusionnée d'équipe.

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

### « remplace XXX » : le poste de la personne remplacée

La ligne 9 donne le poste **habituel**. Elle ne dit rien du jour où quelqu'un
part tenir celui d'un autre — et c'est alors le commentaire qui le dit, comme
toujours dans ce classeur.

Le client, le 21/09/2026 : « pourquoi est-ce que QBY est à déterminer alors
qu'il a le poste distillation et qu'il n'y a personne en distillation ce
jour-là ? » La réponse était écrite dans la cellule : `["PM", "R",
"remplace PAM"]`, et PAM est l'opérateur distillation de l'équipe 4. QBY est
renfort arrière (ligne 9, colonne U) et polyvalent gluten + distillation ; il
n'entrait donc ni au terrain arrière — il lui manque la fermentation — ni au
repli « un seul atelier », puisqu'il en a deux.

`atelierDuRemplace()` lit ce commentaire, **en dernier recours seulement** :
quand ni la cellule, ni l'annotation, ni la ligne 9 n'ont donné de poste. Et
sous les mêmes conditions de polyvalence que les règles du client : on ne
tient que ce qu'on possède — le terrain arrière demande fermentation ET
distillation, le gluten demande le gluten.

Le classeur écrit **2 884** mentions « remplace XXX », dont **1 461** désignent
un trigramme connu. Deux d'entre elles servent de vérité de terrain : QBY les
08 et 09/06 porte « remplace PAM **en distillation** » — le classeur nomme
lui-même le poste que la règle déduit, et les deux concordent.

Ce repli ne s'applique qu'aux groupes de pause travaillée : une personne
absente ou en congé ne peut pas en recevoir un poste.

**Deux fonctions, deux questions.** `posteDuRemplace()` rend la **pause** de
la personne remplacée (section 10 quinquies) ; `atelierDuRemplace()` rend son
**atelier**. La première version les appelait toutes les deux
`posteDuRemplace`, et la seconde déclaration écrasait la première en silence :
la règle « le commentaire prime sur le cycle » était morte, et
`verifier-calendrier.js` annonçait pourtant ses neuf règles vertes — il
découpe `index.html` avec `indexOf`, donc il rejouait la PREMIÈRE des deux.
Il refuse désormais de travailler sur un nom déclaré deux fois.

### « Poly. Etoh » est un terrain arrière

**Confirmé par le client le 21/09/2026.** L'éthanol, c'est la fermentation et
la distillation — exactement ce que le terrain arrière couvre.

**46 journées** de l'année le portent : 23 en `Poly. Etoh`, 14 en
`poly. Etoh`, 9 avec un point final. Et elles passaient toutes inaperçues,
pour une raison qu'il faut retenir : le motif `ATELIERS` commence par
`^(…|poly|…)`, si bien que « poly. Etoh » était avalé comme un **atelier
connu** sans jamais devenir un poste. Il ne figurait donc pas non plus parmi
les mentions non comprises — l'application croyait l'avoir comprise.

C'est le pire genre d'angle mort : non pas une chose que l'outil déclare ne
pas savoir lire, mais une chose qu'il croit avoir lue.

Le 22/09, PAM porte `["PM", "poly. Etoh", "remplace FPS remplacé par QBY"]`.
Sa cellule l'envoie donc au terrain arrière — et le rééquilibrage n'a plus
rien à faire : QBY garde la distillation, GPO reste au gluten.

> **Le client, le 21/09/2026** : « il faut toujours lire les commentaires, ce
> n'est pas la première fois que je te le dis. »

C'est la règle première du projet, rappelée en tête de `CLAUDE.md`, et elle se
perd à chaque fois qu'on cherche la réponse ailleurs que dans la cellule.

### Un opérateur en formation figure au poste, mais n'y compte pas

**Le client, le 21/09/2026** : « un opérateur en formation ne peut pas compter
comme effectif minimum au poste qui lui est attribué, car il n'est pas valide
à ce poste ; il peut y figurer mais doit être **en plus** des opérateurs
présents. Par contre, s'il manque des gens, il se peut qu'on le rappelle pour
retourner remplacer dans un poste qu'il peut — mais tout cela sera marqué en
commentaire. »

C'est la **qualification** qui décide, pas le commentaire : là où sa
polyvalence le porte il est valide et il compte ; là où elle ne le porte pas —
le poste sur lequel il se forme — il est en plus. Le rappel se lit dans le
commentaire, mais c'est la trace de la décision, pas sa condition.

La ligne 9 leur donne le poste sur lequel ils **se forment**, avec leur
équipe : `chaudières éq. 5` pour quelqu'un dont la polyvalence ne porte que
meunerie et gluten. Les y compter, c'est déclarer le poste tenu par quelqu'un
qui n'y est pas encore validé.

**Huit personnes**, qui prestent de 120 à 255 journées par an :

| | Se forme sur | Polyvalence validée |
|---|---|---|
| CDT | Distillation | *(aucune)* |
| MGY | chaudières éq. 1 | *(aucune)* |
| NPI | Gluten | *(aucune)* |
| GST | chaudières éq. 3 | Fermentation |
| LCI | Distillation éq. 5 | Fermentation |
| LHR | chaudières éq. 5 | Meunerie, Gluten |
| SKS | Meunerie | Fermentation, Distillation, Chaudières |
| SVE | Distillation éq. 1 | Meunerie, Gluten |

Exemple, le 21/09 au matin :

```
DISTILLATION  1 / 1   CDT · PDR
```

Deux personnes affichées, une seule comptée. La tuile de CDT porte
« en formation, en plus ».

**Ce que cela change** : sur soixante jours, les postes en manque passent de
71 à **131**, les surnombres de 255 à 127. C'est beaucoup, et c'est le prix de
l'honnêteté — l'application déclarait tenus des postes que seul un opérateur
non validé occupait. Le rééquilibrage compte de la même façon : il ne prend
ni ne pose un opérateur en formation là où il ne compterait pas.

### « R » seul : combler un poste qui serait vide

**Le client, le 21/09/2026** : « des fois il y a juste un R dans la cellule de
droite — QBY les 23 et 24/09. Cela veut dire qu'il remplace à un poste qui est
censé être vide, et dans cet exemple c'est en distillation pour remplacer PAM,
mais ce n'est pas marqué dans les commentaires du 23/24 alors que ça l'est
dans ceux du 21/22. »

Le classeur porte pourtant l'information, mais de l'**autre côté** : PAM les
23 et 24 porte `["N","PM","Remplace IME en PM Equipe complète en N"]` — il
quitte la nuit pour l'après-midi, donc sa distillation de nuit est vide.

On ne va pas la chercher là-bas. On constate qu'un poste manque et que cette
personne-là, marquée `R`, peut le tenir : c'est ce que le `R` annonce.

**236 journées** portent un `R` seul. Dans **213**, le commentaire nomme le
remplacé et la lecture s'en sert depuis toujours ; les **23** autres sont
muettes, et c'est à elles que sert cette règle.

Le 24/09 en nuit, la pause devient complète :

```
MEUNERIE 1/1 SMK · GLUTEN 2/2 GSK·RDT · FERMENTATION 1/1 CHD
TERRAIN ARRIÈRE 1/1 FPS · DISTILLATION 1/1 QBY · CHAUDIÈRES 2/2 GBT·MHI
```

### 568 remplacements perdus pour une majuscule

En mesurant ce qui précède, un défaut est apparu dans `atelierDuRemplace()` :
son motif cherchait `\bremplac` **sans ignorer la casse**. Tout
« **R**emplace GPS » — et le classeur en écrit beaucoup — lui échappait.

| | Mentions exploitables |
|---|---|
| motif sensible à la casse | 1 463 |
| casse ignorée | **2 031** |

**568 de plus, près de trois sur dix.** La fonction avait été écrite le matin
même, et aucune des onze règles ne pouvait le voir : elle ne ment pas, elle
lit seulement moins que ce qu'elle croit.

### Rééquilibrer une pause : combler un manque avec un surnombre

**Le client, le 21/09/2026** : « dans une même pause, quand il manque
quelqu'un sur un poste et que sur un autre poste ils sont plus que le nombre
demandé, celui qui a la polyvalence est d'office placé là où il manque
quelqu'un — exemple, pour le terrain arrière c'est PAM qui y sera et QBY qui
tiendra la distillation. Dans le cas où l'adjoint ne remplace pas le
contremaître et qu'il est disponible, c'est l'adjoint qui peut prendre le
poste où il manque quelqu'un, car il a toutes les polyvalences. »

`reequilibrer()` le fait, sous quatre réserves :

1. **La cellule prime, toujours.** On ne déplace que ce que l'application a
   DÉDUIT — ligne 9, polyvalence, commentaire. Une personne que sa propre
   cellule envoie à un poste y reste, quel qu'en soit l'effet sur les
   effectifs : le classeur dit ce qui a été fait.
2. **La polyvalence commande.** Le terrain arrière demande fermentation ET
   distillation, les autres postes demandent leur atelier.
3. **L'adjoint vient en dernier.** Tant qu'un poste en surnombre peut fournir
   quelqu'un, c'est de là que vient le renfort ; l'adjoint n'est sollicité
   qu'à défaut — et seulement s'il ne remplace pas déjà le contremaître, ce
   que `remplacementCM()` a déjà tranché en amont.
4. **Pas en journée.** Le client, plus tôt : « en jours il n'est pas
   obligatoire d'avoir quelqu'un à chaque poste ». Combler un manque qui n'en
   est pas un déplacerait des gens sans raison.

La tuile d'une personne ainsi placée porte « **comble le poste** » : c'est une
déduction de l'application, pas une ligne du classeur, et cela doit se voir.

**Mesuré sur quatorze jours** : les postes en manque passent de **33 à 13**,
pour 20 déplacements.

### En cascade, quand personne du surnombre ne sait tenir le poste

**Le client, le 21/09/2026** : « tu indiques personne en terrain arrière alors
que SPS peut remplacer AAI en distillation et que AAI peut faire la
polyvalence arrière. »

Un seul saut ne suffit pas toujours. Ici le terrain arrière demande
fermentation ET distillation ; personne en surnombre ne les a toutes deux,
mais AAI les a — sauf qu'il tient déjà la distillation. La solution est à
**deux temps** : SPS quitte les chaudières, en surnombre, pour prendre la
distillation ; AAI passe au terrain arrière.

Les trois postes deviennent justes d'un coup : le poste de départ garde son
effectif, le surnombre se dégonfle, le manque se comble.

Exemple trouvé dans l'horaire — **lundi 31 août, nuit** :

```
MEUNERIE         1/1  DKS
GLUTEN           2/2  IME · LHR ← vient du surnombre
FERMENTATION     1/1  ALZ ← était au gluten, passe combler
TERRAIN ARRIÈRE  1/1  GKT
DISTILLATION     1/1  PDR
CHAUDIÈRES       2/2  FLN · JBA
```

Sans la cascade, la fermentation affichait `0 / 1`.

**Mesuré sur soixante jours** : les manques passent de **75 à 71**, les
surnombres de 259 à 255, pour 7 déplacements de plus. Le gain est modeste
parce que la plupart des manques se comblent déjà en un saut — mais chacun
des quatre était un poste affiché vide alors que l'équipe pouvait le tenir.

On s'arrête à deux sauts : au-delà, l'application inventerait une
réorganisation que personne n'a décidée.

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

## 6 nonies — « conserver prime de nuit » : le commentaire nomme la prime

336 journées de 2026 portent dans le commentaire une phrase qui dit quelle
prime payer. `primeGardee()` la lit et elle l'emporte sur le poste retenu par
la lecture — c'est la seule mention du commentaire qui parle de la PAIE et
non du travail. Les règles de calcul sont dans `docs/regles-paie.md`, section
« La prime conservée, écrite en toutes lettres dans le commentaire ».

Ce qu'il faut retenir ici, parce que cela change la façon de lire une
journée : **une journée a désormais deux postes**.

| champ | ce qu'il dit | qui le lit |
|---|---|---|
| `r.s` | le poste dont la prime est **payée** | la fiche de paie |
| `r.sp` | le poste **presté**, quand il diffère | l'onglet Équipe, la case du calendrier |

`r.sp` n'existe que si les deux diffèrent. Partout ailleurs `postePeint(rec)`
donne celui qu'il faut montrer et `gardePrime(rec)` dit s'il y a une prime
conservée à signaler. **Ne jamais peindre une case avec `rec.s`** : AFA le
04/09 a fait 7h-15h en gardant sa prime de nuit ; la case doit dire « D », le
liseré dire « nuit », et l'effectif de la nuit ne doit pas le compter.

C'est la généralisation de ce que l'application faisait déjà des journées
`SD26` et `D-F` — travaillées en horaire de jour, payées à la prime de leur
pause. Le mécanisme existait ; il ne manquait que de lire le commentaire.

## 9 ter — les manques d'effectif, et pourquoi ils se calculent en un seul endroit

Le client, le 21/09/2026 : « un module qui indique quand il manque quelqu'un
à un poste. Ce module ne doit pas revenir en arrière, uniquement à partir de
la date du jour. »

Deux fonctions portent désormais tout le calcul d'effectif, et **les deux
vues les partagent** :

| Fonction | Ce qu'elle rend |
|---|---|
| `equipeDuJour(db,annee,mois,jour)` | qui travaille, rangé par pause |
| `postesDePause(db,liste,gk,mmdd)` | la pause poste par poste : `{P, gens, tenu, attendu, detail, manque, creux}` |

Elles étaient écrites au milieu du rendu de l'onglet Équipe. Le module des
manques ne pouvait donc ni les appeler, ni les vérifier — il aurait fallu les
recopier, et **une alerte qui compte autrement que la vue du jour est pire
que pas d'alerte du tout** : elle envoie chercher quelqu'un là où il ne manque
personne, ou se tait là où il manque quelqu'un.

Le contrôle croisé se fait dans le navigateur : cliquer une journée du module
emmène l'onglet Équipe sur cette journée, et les deux doivent dire la même
chose. Le 25/09 : le module annonce `AM Gluten 1/2`, la vue affiche
« AM GLUTEN 1 / 2 — 1 manquant ». Le 28/09, deux fermentations manquantes, en
PM et en N, que le module distingue par le code de pause écrit sur la
pastille — la couleur seule ne se lit pas.

Le module est **en tête de l'onglet Équipe**, avant la vue du jour. Il y
était d'abord en dessous, et le client ne l'a pas trouvé : soixante-dix-sept
personnes le séparaient du haut de la page. Ce qui appelle une décision
passe avant ce qui informe.

## 9 quinquies — une carte par pause, la pause en tableau

Le client, le 21/09/2026 : « il faut un cadre pour le matin, un pour le pm,
un pour la nuit, un pour le jour, et un pour le reste. Est-ce possible de
modifier la présentation des équipes et de la faire sous forme de tableau
dans le sens de la production ? »

Cinq cartes : **Matin, Après-midi, Nuit, Jour**, et **Le reste** — malades,
congés, repos, qui ne tiennent aucun poste ce jour-là et n'ont donc pas de
ligne par poste.

Chaque pause est un tableau de trois colonnes : **le poste, son effectif, qui
le tient.** Les lignes suivent `POSTES_TRAVAIL`, qui est déjà l'ordre où l'on
parcourt l'usine — meunerie, gluten, fermentation, terrain arrière,
distillation, chaudières, STEP, précédés du contremaître et de l'adjoint.
Suivent, s'il y en a, la formation et les postes à déterminer.

Deux couleurs, deux informations : la **pastille du titre** dit la pause, le
**liseré de gauche** dit l'atelier, dans la palette de la section précédente.

La colonne des postes fait 110 px et non 96 : « CONTREMAÎTRE » est un seul
mot de douze signes, il ne se coupe pas, et il passait par-dessus son
effectif.

Rien du calcul ne change : `postesDePause()` rend les mêmes lignes, seul leur
habillage est neuf.

### La cellule prime, y compris sur la fonction de la personne

Le client, le 21/09/2026 : « tu mets un absent au gluten le 25/09 en AM alors
que l'opérateur gluten de la pause est bel et bien remplacé par ATR dans
l'horaire de SLT et ATR et les commentaires. »

Il avait raison, et la faute était de tête :

```js
function posteTenu(person,raw,hJour,poste){
  if(estCadre(person)){ ... return "adj"; }   /* ← court-circuit */
  k=posteEcrit(raw); if(k) return k;          /* ← jamais atteint */
```

ATR est adjoint. Sa cellule du 25/09 dit `["AM","Gluten","Remplace SLT"]` —
elle nomme le poste, en toutes lettres — mais `estCadre()` renvoyait « adjoint »
avant qu'on la lise. Le gluten paraissait donc à 1/2, et le module annonçait
un manque là où le classeur disait le contraire sur **deux lignes** : celle de
SLT (« Remplacé par ATR ») et celle d'ATR (« Remplace SLT »).

**184 journées de cadres nomment ainsi un poste, et aucune n'était lue** :
57 terrain arrière, 31 meunerie, 31 chaudières, 19 distillation, 16 gluten,
15 fermentation, 1 STEP — 170 d'adjoints, 14 de contremaîtres.

`posteEcrit(raw)` passe donc **avant** le test de fonction. Les 14 journées de
contremaître sont toutes explicites (`["AM","meunerie","remplace DKS"]`) : ce
jour-là il tient la meunerie, et le poste de contremaître est vraiment vide —
c'est une information, pas une fausse alerte. Aucune de ces 184 journées
n'est en même temps un remplacement de contremaître, donc ce nouvel ordre
n'arbitre rien qui existe : il rend à la cellule ce qui lui revient.

**Effet mesuré : les manques à venir tombent de 28 journées à 15.** Près de la
moitié des alertes étaient cette bévue.

La leçon tient en une ligne, et c'est celle qui ouvre `CLAUDE.md` : *la
cellule dit ce qui a été presté, et elle prime*. Une fonction — cadre,
adjoint, opérateur — ne dit que l'habitude. Toute lecture qui teste la
personne avant de lire sa cellule refera cette faute.

### Les couleurs disent l'atelier, le texte dit la pause

Le client, le 21/09/2026 : « Gluten meunerie en jaune, fermentation /
distillation / polyvalent arrière en verts, chaudière en rouge, step en
bleu. » C'est l'usine telle qu'il la voit ; la pastille la reprend.

| Atelier | Jeton | Clair | Sombre |
|---|---|---|---|
| Gluten, Meunerie | `--at-jaune` | `#8A6417` sur `#F7EDD1` | `#D8AE4E` sur `#33280C` |
| Fermentation | `--at-ferm` | `#1F6B3C` sur `#D9EDE0` | `#5FB682` sur `#122A1C` |
| Distillation | `--at-dist` | `#156B5C` sur `#C7E7EA` | `#4EB4A2` sur `#0A2930` |
| Terrain arrière | `--at-terr` | `#4F6B1F` sur `#E4EDD2` | `#9DBC5B` sur `#232C10` |
| Chaudières | `--at-chau` | `#A3352B` sur `#F6DEDB` | `#E08278` sur `#331816` |
| STEP | `--at-step` | `#1F5A94` sur `#D8E6F4` | `#75A9E2` sur `#12233A` |

**Trois verts et non un seul.** Les trois postes se retrouvent côte à côte
sur la même ligne — le 27/09 en porte deux — et une couleur qui ne distingue
pas ne sert à rien. Vert franc pour la fermentation, vert-bleu pour la
distillation, vert-olive pour le terrain arrière.

Contrôlé : tout texte est à **4,6 au moins** sur son fond en mode clair, 5,9
en mode sombre. Les trois verts s'écartent de ΔE 18,8 au minimum sur le
texte. Le fond de la distillation a dû être bleui (`#D4EBE6` → `#C7E7EA`) :
à 4,3 de ΔE il se confondait avec celui de la fermentation.

La paire la plus serrée reste **jaune / terrain arrière** — ΔE 7,2 sur le
fond. C'est la tension de la consigne elle-même : le jaune et le vert-olive
sont voisins. Écarter l'olive du jaune le pousse dans la fermentation, où il
serait bien pire. Les textes, eux, s'écartent de ΔE 32,4.

Le contremaître n'est pas un atelier : sa pastille reste neutre. La STEP
n'attend aucun effectif (`n:0`), sa couleur ne sert donc pas encore.

### Ce que le module ne dit pas

- **Rien avant aujourd'hui.** Un manque passé ne se comble plus.
- **Rien en journée** : le client, « en jours il n'est pas obligatoire d'avoir
  quelqu'un à chaque poste ».
- Quand un poste reste **« à déterminer »** le même jour, le module l'écrit
  sous la ligne : la personne dont le classeur ne donne pas le poste est
  peut-être exactement celle qui manque.

## 9 quater — un indéterminé qu'un seul poste en manque attend

`reequilibrer()` ne prenait, parmi les gens dont le classeur ne dit pas le
poste, que ceux marqués `R` — explicitement là pour combler. PDE les 26 et
27/09 ne l'est pas : sa cellule est `["AM"]`, sa polyvalence
`Fermentation / Distillation / STEP`, et la fermentation était à 0/1 à côté
de lui.

Il est donc placé, sous **une condition stricte** : il ne doit y avoir qu'UN
SEUL poste en manque qu'il sache tenir. Deux, et le choix appartiendrait au
classeur, pas à nous — « à déterminer » vaut mieux qu'une supposition, c'est
la règle que le client a validée. La vignette le dit : « déduit de sa
polyvalence », pour qu'une déduction ne passe jamais pour un fait.

Le prendre ne dégarnit aucun poste, il passe donc **avant** le prélèvement
sur un poste en surnombre et avant la cascade.

Effet : les manques à venir passent de 15 journées à 14.

### La station d'épuration

Le client, le 21/09/2026 : « PDE et CAN sont à la Station d'épuration s'ils
ne remplacent pas ailleurs. CAN n'a que la STEP, mais PDE revient de temps en
temps en fermentation ou distillation. »

C'est la **catégorie** qui le dit — « Opérateurs STEP » — et non la
polyvalence : CAN n'a que la STEP, donc la règle du poste unique le plaçait
déjà ; PDE en a trois, si bien qu'aucune ne le désignait et qu'il restait
« à déterminer » **359 journées sur 365**.

`posteParDefaut()` vient en **dernier**, après la cellule et après le
remplacement : « s'ils ne remplacent pas ailleurs » est la condition même de
la règle. PDE le 18/02 écrit « terr. Arr. » dans sa cellule, et c'est là
qu'il est.

Cela défait la déduction de la section précédente, qui l'envoyait en
fermentation les 26 et 27/09 : il n'était pas indéterminé, il était à la
station. **Une déduction comblait un trou de ma connaissance, pas un trou de
l'horaire** — c'est le risque de ce genre de règle, et il faut le garder en
tête. Elle sert encore 14 fois dans l'année, toutes pour QBY, renfort arrière
que le classeur ne place nulle part.

### Un opérateur station le matin

Le client, le 21/09/2026 : « autre règle, uniquement pour la pause du matin
il faut au minimum 1 opérateur station d'épuration ».

L'effectif attendu dépend donc de la PAUSE, et non plus du seul poste :
`attenduAuPoste(P,gk)` lit `P.parPause[gk]` avant `P.n`. La STEP porte
`n:0, parPause:{AM:1}` — attendue le matin, nulle part ailleurs. Le jour
reste à zéro partout, comme avant.

`peutTenir()` ne regarde plus l'effectif attendu : savoir tenir un poste ne
dépend pas du nombre qu'on y attend, et CAN sait tenir la station à toute
heure.

**Six matins de l'année n'ont aucun opérateur station.** Quatre personnes
peuvent la tenir : CAN et PDE, plus PDF et CWN qui l'ont en polyvalence.

### Ce qui n'en est pas un : QBY le 23/10

Son en-tête porte « Renfort arrière » et le terrain arrière manque — mais sa
polyvalence est `Gluten / Distillation`. La règle du client : « le terrain
arrière ne peut être tenu que par quelqu'un qui possède le poste fermentation
ET le poste distillation ». QBY ne l'a pas. Le manque est réel.

### À trancher : l'annotation « F » sur un projet

**313 journées** portent `F` en annotation, et `EST_FORMATION` les sort de
leur poste — à raison : « Formation STEP », « Formation Bioéthanol », « ATEX
sur site », « recyclage CESI ».

Mais **28 d'entre elles** portent le commentaire « projet falling film en
distillation ». Ce n'est pas une formation, c'est un projet, et le
commentaire dit où : en distillation. Le 05/10 en après-midi, six personnes
sont dans ce cas, et la pause paraît vide de quatre postes.

Question au client : sur ces journées-là, la personne tient-elle le poste que
le commentaire nomme, ou est-elle hors effectif comme pour une formation ?
Cela touche l'effectif affiché, pas la paie.
