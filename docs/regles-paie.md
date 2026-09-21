# Règles de paie confirmées par le client

Règles de calcul établies avec le client, que ni la note explicative de la
fiche de paie ni la note sur les repos ne suffisent à déduire. Elles sont
implémentées dans `compute()` (`index.html`).

Les règles de **lecture de l'horaire d'équipe** sont dans
`conversion-horaire.md` ; ici, ce qui touche au calcul de la fiche.

## Chèques-repas

```
chèques = journées prestées d'au moins 4 h
        + ⌊ RTT cumulées / 8 ⌋
        + ⌊ flex time cumulé / 8 ⌋
```

**Une journée prestée d'au moins quatre heures donne toujours un chèque.**
En dessous de quatre heures, aucun.

**Les heures récupérées en donnent un de plus par tranche de huit heures.**
Le client : « sur une journée de 8 h je récupère 4 h de RTT, je n'aurai droit
qu'à un chèque-repas, celui des 4 h prestées ; la fois d'après, quand je
reprendrai encore 4 h de RTT, j'ai droit à 2 chèques, car il prendra en
compte les 4 h de RTT où je n'y ai pas eu droit. Nous avons donc droit à un
chèque-repas par 8 h total de RTT récupéré. »

**Les trois compteurs sont séparés.** Quatre heures de RTT et quatre heures
de flex time ne font **pas** un chèque. Sur l'horaire 2026, l'écart entre un
compteur commun et des compteurs séparés atteint 17 chèques à l'année.

| Compteur | Où il vit | Ce que l'horaire en dit |
|---|---|---|
| **RTT** | bas du classeur | les reprises, jour par jour |
| **Flex time** | bas du classeur, lignes `+FT` et `-FT` | les reprises **et** les mises de côté |
| **Récup. HS** | hors classeur | **seulement** les reprises |

> « RHS, c'est un compteur hors fichier ; si le travailleur les reprend c'est
> marqué, mais ce n'est pas marqué quand il en fait. » — le client

Une reprise de récup. HS ne retire rien à la journée, comme un `-FT` : AFA le
28/01, prévu 7h-15h, part à 12h45 — 5 h 45 de présence plus 2 h 15 reprises,
soit ses 8 h. 173 journées de l'horaire 2026 en portent une.

**Le reliquat se reporte de mois en mois et repart à zéro en début d'année.**
L'application calculant un mois à la fois, trois champs de l'onglet Horaire
reçoivent le reliquat de la fiche précédente — RTT, flex time et récup. HS —
et la fiche affiche les trois reliquats à reporter au mois suivant. En
janvier, ils valent zéro. Le pré-remplissage renseigne de lui-même les heures
de récup. HS reprises dans le mois.

Seuls RTT et flex time ouvrent ce droit. Les vacances annuelles, la maladie,
le congé parental, le repos compensatoire, le CT et la récupération de jour
férié n'y donnent pas droit, pas plus que les jours de repos — conformément
à la note sur les repos : « les chèques-repas sont attribués lors des jours
de prestations ».

Le champ « Nombre de chèques-repas » de l'onglet Horaire reste disponible
pour forcer une valeur ; laissé vide, le calcul ci-dessus s'applique.

## Primes de rappel

Source : **OP_BWZ_CoD_00020**, « Octroi et calcul des primes de rappel pour le
personnel en pause », version 1 en vigueur depuis le 18/06/2025. Elle compile
et remplace les notes du 21/12/2012 et du 19/11/2012. Le classeur
« prime rappel au 22.12.2020 » en donne le calcul chiffré.

### Calcul

> prime = 2 h de déplacement × (salaire horaire × coefficient du jour
> + prime de pause × coefficient de pause) × coefficient du moment

| Coefficient du jour | | Coefficient de pause | | Moment |  |
|---|---|---|---|---|---|
| semaine (lundi 6h → samedi 6h) | 150 % | semaine | 150 % | J et J-1 | 2 |
| samedi | 187,5 % | samedi | 200 % | J-2 à J-15 | 1,5 |
| dimanche | 200 % | dimanche et férié | 300 % | | |
| jour férié | 250 % | | | | |

Le jour férié prend le coefficient de jour de 250 % mais le coefficient de
pause du dimanche, 300 % — c'est bien ce que fait le classeur, qui va chercher
la colonne « Dimanche et JF » pour la prime.

Les vingt-quatre montants du classeur sont reproduits à l'identique par
l'application (salaire horaire 23,0181, primes 0,90 / 1,80 / 4,00).

La **modification de pause** est à part : 2 h de salaire horaire à 100 %, sans
prime de pause, quand elle est demandée la veille ou le jour même.

### Où la prime apparaît sur la fiche

Le client : « les primes de rappel sont reprises dans **heures de
déplacement** ». C'est cohérent avec la procédure, qui définit la prime comme
« 2 heures de déplacement multipliées par un coefficient » : le coefficient du
moment porte sur les heures, pas sur le taux. Un rappel J-1 vaut donc 4 h de
déplacement, un rappel J-2 à J-15 en vaut 3, et une modification de pause 2.

L'application les affiche en heures, sur la même ligne que le champ manuel
« Heures de déplacement », et rappelle le total. Ce champ manuel ne doit donc
reprendre que le déplacement **non** couvert par les rappels cochés dans
l'horaire, sous peine de compter deux fois.

Pour VBN, les quatre rappels de 2026, tous en pause de nuit et en semaine :

| Jour | Demande | Heures | Taux horaire | Montant |
|---|---|---|---|---|
| 19/02 | 18/02, J-1 | 4 h | 62,1156 | 248,46 € |
| 14/04 | 13/04, J-1 | 4 h | 62,9293 | 251,72 € |
| 11/06 | 10/06, J-1 | 4 h | 62,9293 | 251,72 € |
| 25/06 | 25/06, J | 4 h | 62,9293 | 251,72 € |

Ces primes sont payées : « vu qu'il s'agit dans les deux cas de primes payées,
il n'y a pas de récupération d'heures ». Les heures de présence effective sont
en revanche rémunérées selon les règles des heures supplémentaires, ou versées
au flex time.

### Octroi

Prime de rappel, à la demande de la ligne hiérarchique :

- **rappel la veille ou le jour même** : commencer au moins 30 minutes avant
  le début de la pause, ou être rappelé d'un jour de repos (le repos est
  maintenu) ou d'un jour de congé (le congé est reporté) ;
- **modification d'horaire entre 2 et 15 jours** — par exemple pour remplacer
  une absence de longue durée : prestation demandée sur un jour de repos ou
  sur un jour prévu en congé ;
- **prestation avant ou après la pause** suite à une absence imprévue ou à une
  prolongation pour panne : la prime n'est due qu'à partir de **3 h** de
  prestation ; en deçà, rien.

### Le seuil de trois heures ne vaut que pour l'après-pause

La procédure énonce le seuil au point 6.2, pour une « prestation avant ou
après la pause ». Le client le précise : « il faut minimum 3 h si tu restes
après ta pause, mais cette règle ne s'applique pas si tu es rappelé avant ta
pause, tu y as droit ». C'est cohérent avec le point 6.1.a, qui fixe pour le
rappel en début de poste un minimum de **trente minutes** avant l'heure de
début de la pause.

### Détection automatique depuis l'horaire

L'horaire porte 460 mentions de rappel sur l'année, dont 450 avec la date de
la demande — « Rappel le 13/04 » sur la journée du 14/04 donne le coefficient
du moment sans rien deviner. `rappelDuJour()` propose un rappel quand :

| Signal | Exemple |
|---|---|
| poste prévu au repos | AFA le 31/01, `- ǀ 16h-19h` |
| repos ou congé cité en toutes lettres | FLI le 23/01, « était prévu en repos » ; LHR le 31/08, « avait posé une VA » |
| heures gagnées au compteur flex time | YPE le 19/01, `N ǀ 8h +FT` — prestées hors horaire par définition |
| au moins 30 min avant la pause | AFA le 24/07, `N ǀ 18h-6h`, quatre heures d'avance |
| au moins 3 h après la pause | AFA le 03/02, `AM ǀ 06h-18h`, quatre heures de plus |

La plage se lit dans l'annotation, dans la cellule, ou à défaut dans le
commentaire — AFA le 10/09, « AM ǀ VM ǀ remplace VBN **de 2h à 6h** ».

Sur l'année : **405 rappels proposés** (235 en J/J-1, 170 en J-2 → J-15) et
**55 mentions laissées de côté**, que le pré-remplissage signale au lieu de
les taire :

- deux rappels dans la même cellule, sans dire lequel s'applique — BBZ le
  20/03, « rappel 1 le 09.03 rappel 2 le 19.03 » ;
- un rappel qui se rapporte à une autre journée — GDT le 15/03, « presté le
  20.03 rappel le 19.03 » ;
- le rappel d'un collègue — APN le 18/03, « SMA pp de rappel » ;
- une date postérieure à la prestation — VBN le 19/02, faute de frappe pour
  le 18/02.

Les propositions sont comptées « à vérifier » : la cellule ne dit pas toujours
si la demande venait de la ligne hiérarchique, ce qui conditionne le droit.

### La seule exclusion

> « Aucune prime ne sera accordée en cas de demande de la ligne hiérarchique
> pour une prestation en pause AM dans les jours prévus en "Day" de la 5ᵉ et
> 6ᵉ semaine du cycle. »

L'application l'applique seule : le poste `D` n'existe que dans les semaines 5
et 6 du cycle, il suffit donc de lire le cycle de la personne. Un rappel coché
en pause AM sur une de ces journées ne produit pas de prime, et la fiche
l'indique en ligne d'information.

## Prime de remplacement de contremaître

Les adjoints contremaître **n'ont pas** de prime mensuelle fixe. Le client :
« les adjoints ne possèdent pas la prime mensuelle de la demi-heure, ils ne
l'ont qu'en faisant les remplacements contremaître au cas par cas ». Et sur
son mode de paiement : « ce ne sont pas des heures à récupérer, elles sont
payées directement ce mois-là ». Elle apparaît sur la fiche sous **Primes
diverses**.

### Montant

Forfaitaire par journée de remplacement, et non une fraction du salaire
horaire — les deux ne suivent pas la même indexation :

| Mois 2026 | Prime / jour | Salaire horaire de la fiche |
|---|---|---|
| janvier – février | 26,865 € | (taux retiré) € |
| mars – août | 27,365 € | (taux retiré) € |

La valeur par défaut de l'application est 27,365 €, modifiable dans l'onglet
« Barèmes ».

### Quelles journées comptent

La mention `R-CM` dans la cellule ou dans sa colonne d'annotation, **et** un
remplacement couvrant un poste entier. Le client, à propos du 04/06 :
« je n'ai pas eu la prime de remplacement, car c'est partiel ».

Deux formes de remplacement partiel, qui ne donnent pas la prime :

| Journée | Cellule | Commentaire | Pourquoi |
|---|---|---|---|
| 21/01 | `R-CM ǀ 2h +FT` | remplace GPS | la cellule ne nomme aucun poste et le compteur ne gagne que 2 h |
| 27/07 | `R-CM ǀ 4h +FT` | remplace GPS de 18h à 22h | 4 h, et la plage tient dans le poste PM |
| 04/06 | `AM ǀ R-CM` | remplace ATA de 11h30 à 14h | plage entièrement comprise dans son poste AM (6h-14h) |

À l'inverse, comptent bien :

| Journée | Cellule | Commentaire | Pourquoi |
|---|---|---|---|
| 19/03 | `R-CM ǀ 8h +FT` | remplacement de YBT | journée entière au compteur |
| 14/04 | `R-CM` | remplace en 18h-06h | plage débordant largement le poste |
| 01/07 | `R-CM ǀ 4h -FT` | remplace AFA | une reprise `-FT` ne rend pas la journée partielle : les heures reprises sont payées comme si la personne était présente |
| 22 et 23/06 | `N ǀ R-CM` | CP a replacé | congé déplacé pour venir travailler, le poste est bien presté en entier |

Un échange de poste (« échange avec ATR ») n'exclut rien par lui-même : la
journée compte si le poste est presté en entier.

### Vérification

`remplacementCM()` applique la règle ; le pré-remplissage compte les journées
et remplit le champ « Jours de remplacement contremaître » de l'onglet
Horaire. Rejoué sur les huit premières fiches de 2026 :

| Mois | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 |
|---|---|---|---|---|---|---|---|---|
| Journées | 7 | 2 | 16 | 14 | 4 | 7 | 5 | 7 |
| Calculé | 188,06 | 53,73 | 437,84 | 383,11 | 109,46 | 191,55 | 136,82 | 191,55 |
| Fiche | 188,06 | 53,73 | 437,84 | 383,11 | 109,46 | 191,55 | 136,82 | 191,55 |

Huit mois sur huit, au centime près.

## Ce que les fiches de paie confirment, et corrigent

`tools/comparer-fiches.py` confronte les fiches à ce que l'horaire produit.
Premier passage sur VBN, huit fiches de 2026. **Vacances, congé parental et
jour férié concordent à tous les mois, à l'heure près** — la lecture des
absences est juste dans son principe. Deux erreurs en sont sorties.

### « Abs » du classeur veut dire maladie

Le code était lu comme une absence volontaire et injustifiée. Les fiches
disent maladie, et le disent exactement :

| | Fiche (SMG maladie) | Journées « Abs » |
|---|---|---|
| mai | 48,00 h | 6 journées = 48,00 h |
| juillet | 8,00 h | 1 journée = 8,00 h |
| juin | 0,00 h | 2 journées, toutes deux sur un repos |

`ALIAS_HORAIRE` traduit donc « Abs » en `MAL` **à la lecture du classeur
seulement** : le code `ABS` reste disponible à la main pour une vraie absence
injustifiée. Rien ne change en euros — la rémunération du mois est fixe —
mais la bonne ligne apparaît sur la fiche.

Le « remplace X » qui accompagne souvent ces cellules était le plan, pas ce
qui s'est passé : la cellule d'en face porte un **second** remplacement. CDE
le 31/05, « Remplacée par VBN, MPE : Remplacée par LDY » ; AFA le 02/07,
« Remplacé par VBN, remplacé par VGG et GPS ». L'absence prime.

### « DS » est une sortie syndicale, pas une journée prestée

Le client tranche : « uniquement les sorties DS, pas les CPPT ». Une sortie
syndicale est une **absence**, et elle ne conserve pas la prime de la pause
prévue. Les délégations CPPT et les conseils d'entreprise gardent leur
traitement : journée prestée en horaire de jour, prime conservée.

La fiche de février le montrait doublement. Le 12/02, `N ǀ DS ǀ à
l'extérieur`, est la seule journée `DS` de l'année, et février la seule fiche
à porter une ligne « Heure(s) formation syndicale », de 8 h. Et sa prime de
nuit ne fait que 8 h sur le mois — celles du 11/02, dont le commentaire dit
« Conserver prime de nuit ». Il n'en restait aucune pour le 12.

### Une absence d'une journée entière sur un repos ne vaut rien

Elle remplace un poste ; sans poste ce jour-là, elle ne remplace rien. Les
deux journées de maladie posées au 1er et 2 juin tombent sur des repos, et la
fiche de juin ne porte aucune heure de maladie.

Un code d'une **fraction** de journée est autre chose : c'est un prélèvement
sur un compteur, qui vaut même un jour de repos. Le 01/03, « - ǀ 1h RTT ǀ
pris le 05.03 », et la fiche de mars porte bien son heure de repos
compensatoire.

### Ce qui reste à comprendre

| Écart | Détail |
|---|---|
| heures prestées | 897 h calculées contre 962,53 h sur huit fiches. L'écart va dans les deux sens selon le mois : février +22,50, avril −29,00 |
| maladie de mars | 48 h calculées contre 45,72 h sur la fiche |
| repos compensatoire | janvier 4 h contre 5, février 0 contre 0,50 |

## Le contrat, sans lequel rien ne vaut

Le net se construit sur la **rémunération fixe du mois**, pas sur les heures :
la ligne « Montant heures prestées » de la fiche en est la recopie. Tant que
ce montant reste à la valeur d'exemple de 3 000 €, le salaire horaire vaut
20,2200 € au lieu de 37,95, et tout ce qui en découle est faux — sans que
rien ne le signale.

L'onglet Résumé porte donc un avertissement tant que la rémunération fixe
n'a pas été renseignée.

### Lire ces valeurs sur la fiche

| Réglage | Où le lire | VBN 2026 |
|---|---|---|
| Rémunération fixe | déduite : « Montant heures prestées » ÷ fraction | (montant retiré) jusqu'en février, (montant retiré) depuis mars |
| Fraction payée | un temps partiel la réduit | 0,9 — congé parental à 9/10 |
| Diviseur horaire | rémunération fixe ÷ salaire horaire | 148,368007 |

Le recoupement est exact au centime : (montant retiré) × 0,9 = (montant retiré), ce que porte
la fiche de février ; (montant retiré) × 0,9 = (montant retiré), celle d'août. Et le salaire
horaire tombe à la quatrième décimale — (taux retiré) puis (taux retiré) — ce que la
ligne « Heure de déplacement à » de la fiche confirme.

**La fraction est le piège** : c'est la rémunération à temps plein qui se
saisit, et la fraction qui la réduit. Saisir (montant retiré) avec une fraction de 1
donnerait le bon montant mensuel mais un salaire horaire faux, et toutes les
primes horaires avec.

Le piège s'est refermé le 21/09/2026, sur quelqu'un qui avait ce paragraphe
sous la main et ne l'a pas lu : des réglages préparés pour VBN portaient
`fraction: 1`, au motif que ses jours de congé parental étaient écrits un par
un dans l'horaire. Les deux ne s'excluent pas — **l'horaire dit QUAND le
dixième est pris, la fraction dit COMBIEN**. La fiche portait les deux
montants à deux lignes d'écart.

Contrôle en une soustraction : « Rém. périodique fixe » et « Montant heures
prestées » sont deux lignes différentes de la fiche. Si elles diffèrent, la
fraction n'est pas 1.

## Valeurs relevées sur les fiches de paie 2026

Servent de valeurs par défaut ; tout reste modifiable dans l'application.

| | Valeur | Source |
|---|---|---|
| Prime d'équipe matin | 0,90 € | fiches 2026 (la note de 2020 donnait 0,67) |
| Prime d'équipe après-midi | 1,80 € | fiches 2026 (note : 1,34) |
| Prime d'équipe nuit | 4,00 € | fiches 2026 (note : 3,14) |
| Chèque-repas, valeur faciale | 10,00 € | 8,91 patronale + 1,09 personnelle |
| Heures par semaine | 38:40 | figure sur toutes les fiches — la grille écrivait « 38,4 h », qui se lit 38 h 24 et n'est pas la même chose |

Le chèque-repas est passé de 6,90 à 8,91 de part patronale au 1er janvier
2026 : la fiche de décembre 2025 porte encore l'ancienne valeur.

Le diviseur horaire se retrouve sur la fiche : rémunération fixe divisée par
le salaire horaire, soit (montant retiré) / (taux retiré) = 148,368 pour VBN — la valeur
par défaut de l'application.

## Une cellule « VM » avec un horaire presté

**Confirmé par le client le 21/09/2026.** À propos de QBY le 10/09,
`["VM", "4h rhs", "remplace PAM"]` : « le 10/09 il a fait son horaire normal
mais avec VM, par contre il a repris 4 h rhs (parti à 10 h) ».

`VM` ne fait donc pas de la journée une absence : la personne preste son
poste — ici la distillation, en remplacement de PAM — et la visite médicale
se place dedans. La reprise de 4 h comble le départ anticipé, comme le dit la
règle RHS ci-dessous : 4 h de présence + 4 h reprises = ses 8 h.

L'application comptait déjà ces 8 h et le plaçait déjà à son poste ; la règle
est écrite ici parce qu'elle était une déduction, et qu'elle ne l'est plus.

## Une journée épargnée au flex time ne se paie pas

**Confirmé par le client et par la fiche, le 21/09/2026.** À propos de son
19/02 : « c'est une grosse prime de rappel avec 12 h FT+ à la demande du
travailleur — j'aurais pu choisir HS mais j'ai préféré FT. »

> **Heures payées = durée réellement prestée − tout ce qui part au compteur.**

Ce qui part au compteur, c'est le `+FT` de la journée elle-même **plus** ce
que d'autres journées lui renvoient. VBN écrit 8 h le 19/02 et 4 h le 20/02
(« cf 19/02 ») : douze heures prestées, douze épargnées, **zéro payée**.

Et l'on retranche d'abord ce qui dépasse la journée contractuelle : AFA le
15/09 preste 12 h et n'en épargne que 4, donc ses 8 h lui restent dues.

| | Durée | Épargné | Payé |
|---|---|---|---|
| `AFA 15/09 ["18h-06h","4h +FT"]` | 12 h | 4 | **8 h** |
| `VBN 19/02 ["18h-06h","8h +FT"]` + 4 h renvoyées | 12 h | 12 | **0 h** |
| `YPE 19/01 ["N","8h +FT"]` | 8 h | 8 | **0 h** |
| `VBN 19/03 ["R-CM","8h +FT"]` | 8 h | 8 | **0 h** |

La règle ne regardait auparavant que les journées dont la cellule **ne
nommait pas** le poste. La même annotation donnait donc deux résultats
opposés selon un détail d'écriture — 0 h pour `["R-CM","8h +FT"]`, 8 h pour
`["N","8h +FT"]` — sur **56 journées et 26 personnes**.

**La preuve.** La fiche de février de VBN porte 9 jours, 71,50 h et 8 h de
prime de nuit. L'application en comptait 10, 78 h et 16 h de nuit ; elle
compte maintenant 9 jours et 8 h de nuit, au centième. La journée du 19/02
n'y est plus du tout — ni en heures, ni en jours, ni en prime.

La prime de RAPPEL, elle, reste due : elle ne dépend pas des heures de la
journée et l'application la calcule à part.

## Le compteur complète une journée écourtée

**Confirmé par la fiche, le 21/09/2026.** `VBN 24/02 ["6h-12h","2h -FT"]` :
six heures de présence, deux reprises au flex time. La fiche de février porte
**16 h de prime du matin pour deux matins** — donc huit heures ce jour-là, pas
six. Les heures reprises « sont payées ce jour-là comme si j'étais venu
travailler ».

Quatre journées de l'année seulement, et les quatre tombent exactement sur
huit heures une fois le compteur ajouté :

```
VBN 24/02  ["6h-12h","2h -FT"]   6 + 2 = 8
NRD 15/08  ["2h-6h","4h -FT"]    4 + 4 = 8
DKS 06/09  ["6h-12h","2h -FT"]   6 + 2 = 8
GBT 12/09  ["22h-2h","4h -FT"]   4 + 4 = 8
```

La règle ne vaut que pour une **plage plus courte** que la journée
contractuelle. Là où la plage fait déjà huit heures — `7h-15h | 8h -FT`,
13 journées — le `-FT` dit que la journée n'a pas été prestée, et elle vaut
déjà ses huit heures payées : il n'y a rien à ajouter. Les 350 journées dont
la cellule ne porte aucune plage sont dans le même cas.

**Ceci rend caduque la table de la section 6 de `docs/conversion-horaire.md`**,
qui annonce encore `PM|3H -FT` → 5 heures prestées. C'est vrai des heures
PRÉSENTES, faux des heures PAYÉES, et c'est la paie qui nous occupe.

## La prime CCT 90 — avance et solde

**La prime CCT 90 s'appelle « Avantage non récurrent »** et arrive sur une
fiche à part, « Rémunérations - Heures - Avantages divers ». Elle ne porte ni
heure prestée ni prime d'équipe — `comparer-fiches.py` l'écarte donc à raison,
mais il ne faut pas la confondre avec une fiche manquante.

Le calcul est confirmé au centime par la fiche de VBN portant la période de
février 2026, et c'est celui que l'application applique déjà :

```
Avantage non récurrent        (montant retiré)
Cotisation de solidarité        (montant retiré)     = (montant retiré) × 13,07 %
Précompte professionnel           0,00     le bonus en est exempt
Net                           (montant retiré)
```

**Elle est versée en deux fois : une avance en septembre, le solde en mars.**
Confirmé par le client le 21/09/2026. Pour VBN :

| | Fiche | Montant |
|---|---|---|
| avance 2026 | période 08/2026, payée le 02/09 | **(montant retiré)** |
| solde 2026 | mars 2027 | à venir |
| solde 2025 | période 02/2026, payée le 16/03 | **(montant retiré)** |

La fiche n'indique **jamais** l'année que le montant couvre : seul le mois de
versement permet de la retrouver — et c'est ce qui rend l'erreur facile.

Une seconde fiche complémentaire de février porte une « Recup à payer »
négative ; elle n'a rien à voir avec le CCT 90 et s'explique plus bas.

### Une fiche porte le mois PRÉCÉDENT

Le client, le 21/09/2026 : « c'est celle qui est payée en septembre, donc
celle du mois d'août ». Le nom du fichier porte la date de **virement**, la
fiche porte la **période**. `comparer-fiches.py` lit la période, et a donc
raison contre le nom du fichier — mais il faut y penser en cherchant un mois.

## Le pécule de vacances et le treizième mois

**Le client, le 21/09/2026** : « avec la paie du mois de mai tu verras
également les congés payés, et avec la paie du mois de juin la paie du
treizième mois. » Vérifié sur ses fiches — et ce sont bien les **périodes**
de mai et de juin, payées début juin et début juillet.

| Période | Ligne de la fiche | Montant |
|---|---|---|
| 05/2026 | Simple Pécule | (montant retiré) |
| 05/2026 | Double pécule de vacances | (montant retiré) |
| 06/2026 | Treizième mois | (montant retiré) |

**Ces mois-là valent pour les EMPLOYÉS.** Le client, le 21/09/2026 : « en tout
cas chez les employés ; les ouvriers, ce sont d'autres dates. » Lesquelles
reste à établir — aucune fiche d'ouvrier n'a encore été vue.

Le champ « Statut » de l'application ne sait rien de ces dates : il ne change
que la base ONSS, majorée de 8 % pour un ouvrier. Un ouvrier qui se servirait
de l'application y saisirait donc son pécule au mauvais mois sans que rien ne
l'avertisse. Le dire ici, à défaut de pouvoir encore le corriger.

Le treizième mois vaut exactement le « Montant heures prestées » du mois,
c'est-à-dire la rémunération fixe multipliée par la fraction payée. Les deux
sont taxés au **taux distinct**, pas au barème ordinaire : la fiche les met
sous « Précompte prof. allocations except. » et « Précompte prof. double péc.
vacances », à côté du « Précompte prof. rémun. normale ».

### Le treizième mois : la formule est confirmée au centime

L'application calcule déjà ONSS 13,07 % puis précompte 53,50 % sur le reste,
et la fiche de juin le confirme sans un centime d'écart :

```
Treizième mois                      (montant retiré)
ONSS 13,07 %                          (montant retiré)
base au taux distinct               (montant retiré)
Précompte 53,50 %                   (montant retiré)   ← la fiche porte (montant retiré)
```

### Le double pécule : la formule NE tombe PAS

La fiche de mai porte un précompte de **(montant retiré)** sur le double pécule.
L'application en donne un autre, quelle que soit la façon dont on y range le
simple pécule :

| Ce qu'on met dans « complément DPV » | Précompte calculé | Écart |
|---|---|---|
| 0 | (montant retiré) | −223,96 |
| (montant retiré) (le simple pécule) | (montant retiré) | +244,74 |

La fiche est donc **entre les deux**, et aucune combinaison simple des deux
montants ne la reproduit. Quelque chose manque à la règle — une assiette
réduite pour la cotisation, ou un taux qui n'est pas 53,50 % sur toute la
base. **À établir avec le client**, sur la fiche de mai qui porte tous les
chiffres.

En attendant, le simple pécule et le double pécule se saisissent tels quels
dans l'onglet Horaire, et le précompte affiché sera approximatif sur ce
seul mois.

## L'avance mensuelle sur le salaire

**Confirmé par le client le 21/09/2026** : « c'est l'avance de mon salaire
normal, que tu touches toujours fin du mois, tandis que le solde du mois est
toujours payé début du mois suivant. »

La fiche la porte en retenue, sous « **Déduction avance reçue** ». Pour VBN,
**(montant retiré) € tous les mois** sans exception — sauf février 2026, **3 900,00**.

Ce doublement est un **incident, pas une règle**. Le client : « en février
c'était une erreur, elle avait été payée deux fois ; j'ai dû rendre une
partie avec mon salaire du mois d'après. » La reprise se lit sur la fiche
complémentaire du 09/03/2026, qui porte un **brut négatif de (montant retiré) €**
sous « Recup à payer » — une reprise, non une retenue ordinaire, d'où le
brut négatif.

Un simulateur n'a pas à reproduire cela : c'est une correction de paie, pas
un mécanisme. Mais il fallait l'écrire, sinon ce mois restera longtemps un
mystère pour qui compare les fiches à l'horaire.

Elle se saisit dans le champ **« Avance déjà reçue (€) »** de l'onglet
Horaire, mois par mois. Sans elle, le « net à recevoir » de la fiche simulée
est trop élevé de 1 950 € : le brut et les retenues sont justes, c'est le
solde à virer qui ne l'est pas.

**À ne pas confondre avec l'avance CCT 90**, qui porte le libellé « Avantage
non récurrent » et se trouve du côté des rémunérations, pas des retenues. Les
deux figurent sur la fiche d'août 2026, et c'est précisément là qu'on peut
les prendre l'une pour l'autre.

## « CSS » est un congé sans solde

**Le classeur le définit lui-même** : la légende posée à côté des noms écrit
`CSS` puis « Congé sans solde ». L'application connaissait le congé — son
code `SANS SOLDE`, journée entière — mais pas l'abréviation, si bien que
`["N","CSS",…]` comptait **huit heures prestées** pour une journée non payée.

`CSS` est donc un alias caché de `SANS SOLDE`, comme `CPAR` l'est de `CP`.
Deux journées de 2026 en dépendent, SMA les 01 et 09/10.

## Jusqu'à quand court une absence

**Demandé par le client le 21/09/2026** : « pour les absents, il faut indiquer
en bas de la page équipe la date jusqu'à laquelle ils sont indiqués ABS dans
les jours qui suivent l'absence actuelle. »

La tuile d'un absent porte donc « MAL · jusqu'au 11 octobre ». Le classeur
écrit l'absence sur **chaque** case, jours de repos compris — YBT porte
« Abs » du 1er janvier au 11 octobre sans une interruption — si bien qu'un
parcours jour après jour suffit, sans tolérance de trou : un trou est une
reprise, pas une absence qui continue.

La règle ne vaut que pour les **absents** au sens du client, c'est-à-dire les
malades. Les congés ont leur propre groupe et leurs dates sont connues.

## RHS — récupération d'heures supplémentaires

**Confirmé par le client le 20/09/2026.**

Deux écritures, deux sens :

| Écriture | Sens | Effet |
|---|---|---|
| `2h RHS`, `1h rhs`, `2,25h RHS` | une **reprise** | comble la journée — AFA le 28/01, prévu 7 h-15 h, part à 12 h 45 : 5 h 45 de présence + 2 h 15 reprises = ses 8 h |
| `RHS` **seul** | la **journée entière** | absence, exactement comme `RTT` seul |

Le compteur est le même dans les deux cas : une journée entière en consomme
huit heures, « 2h RHS » en consomme deux. C'est un compteur **hors fichier**,
distinct du flex time — s'il reprend des heures c'est marqué, mais rien n'est
marqué quand il en fait.

157 journées de l'horaire 2026 portent `RHS` seul.

## RTT- — le tiret ne change rien

**Confirmé par le client le 20/09/2026.**

| Écriture | Sens |
|---|---|
| `RTT-` seul (ou `RTT -`) | un **RTT complet** — la journée entière, comme `RTT` |
| `2h RTT-`, `3 RTT-`, `7h RTT-` | des **heures de RTT reprises pendant la pause**, comme `2h RTT` |

Le tiret ne modifie donc aucun décompte : `RTT-` se lit exactement comme
`RTT`. Le « h » manque parfois (`3 RTT-`), et la lecture le supplée.

Le tiret n'est enlevé **qu'accolé à RTT** : `8h -FT` en porte un aussi, et
lui veut dire tout autre chose.

39 journées de l'horaire 2026, **toutes en janvier**.

## E. min — effectif minimum

**Confirmé par le client le 20/09/2026.**

`E. min SD26`, `E. Min SD26` : « effectif minimum — il fallait plus de
personnes à ce poste cette période-là ».

C'est l'**explication d'une présence**, pas un décompte. La mention est
retirée et ce qui reste — ici `SD26` — est lu comme la journée elle-même.
Aucune heure, aucune prime ne s'y attache.

12 journées de l'horaire 2026.

## « N SD26 » — le poste et la journée dans la même cellule

**Confirmé par le client le 20/09/2026.**

`N SD26` se lit « **nuit SD26** ». Le client : « ça dit juste que l'opérateur
change d'horaire pour le SD26, donc ici il passe en nuit ».

L'annotation porte donc deux choses à la fois : le poste réellement tenu, et
la journée particulière. `PLZ` les 27, 28 et 29 mars était prévu en
après-midi et a fait la nuit — il restait en après-midi, avec la mauvaise
prime.

**Et le poste indiqué est bien tenu.** `SBZ 25/03 ["N","E. min SD26"]`,
`FPA 03/04 ["N","E. Min SD26"]` : ces personnes tiennent la pause écrite,
elles ne passent pas en horaire de jour.

Attention au découpage : `D-F` et `D-CPPT` commencent aussi par ce qui
ressemble à un poste. Le texte entier est donc éprouvé d'abord ; on ne
découpe qu'à défaut.

## R-F et R-VM — remplacer ceux qui sont partis

**Confirmé par le client le 20/09/2026.**

« Ce sont des remplacements d'autres opérateurs pendant sa pause normale de
travail. » La personne preste donc sa pause, et remplace ceux qui sont partis
en formation.

`R-VM` est le même geste pour la **visite médicale**, pendant ses heures de
travail : elle remplace ceux qui y sont partis, elle n'y va pas.

Aucun effet sur le calcul : `R-F` et `R-VM` rejoignent `R`, `R-CM` et `VM`
parmi les mentions reconnues mais neutres.

## À établir

Ces points touchent à des montants et attendent une réponse du client — ne
pas les deviner :

- `R` (237), `TP` (210), `D-F` (49), `VM` (40),
  `DS-CE` (27), `D-CPPT` (47) : journée prestée normale, absence payée, ou
  absence non payée ? Certains relèvent peut-être de la règle « horaire de
  jour, prime de pause conservée » (`conversion-horaire.md`, section 6 bis).
- L'horaire pendant l'arrêt technique. Le client : « pendant le SD, l'horaire
  est un peu spécial pour ceux qui s'occupent de la préparation ; ils doivent
  toujours prester 8 h mais arrivent et partent quand leur présence est
  nécessaire ». L'horaire écrit y est donc nominal, et les heures d'arrivée
  citées en commentaire ne permettent pas d'en déduire la durée.
- `?SD26|8H +FT` : journée d'arrêt technique tombant sur un repos — les huit
  heures sont-elles payées **et** épargnées, ou seulement épargnées ?
- Une journée de 12 h portant aussi une absence partielle vaut-elle 10 h
  prestées (ce que fait le calcul) ou 12 h ?

## Adjoint n'est pas contremaître, sauf quand il le remplace

**Confirmé par le client le 21/09/2026.**

« Les adjoints doivent être classés dans "Adjoint" et non contremaître dans
l'onglet Équipe s'ils ne remplacent pas comme contremaître. »

L'onglet Équipe les rangeait tous sous « Contremaître », si bien qu'un poste
paraissait tenu — voire doublé — par des gens qui n'y étaient pas. Un adjoint
présent n'est pas un contremaître de plus.

Le poste « Adjoint » n'annonce **aucun effectif attendu** : ce n'est pas un
poste à tenir, c'est une fonction. Un adjoint ne rejoint « Contremaître » que
le jour où `remplacementCM()` le reconnaît — « R-CM » dans la cellule ou son
annotation, et pas un remplacement partiel.

Conséquence voulue : une pause sans contremaître et avec deux adjoints
affiche maintenant « Contremaître 0 / 1 » et « Adjoint 2 ». C'est la vérité,
et elle se voit.

## Contremaîtres et adjoints

Confirmé par le client le 20/09/2026.

**Six contremaîtres** : AFA, ATA, FLI, GPS, YPE et VBN — ce dernier passé
contremaître le 15/09/2026. **Cinq adjoints** : ATR, FPA, JBI, VGG, YBT.

Le classeur les met dans la même liste sans les distinguer. L'indice
disponible — les adjoints figurent sur la feuille « Polyvalence », les
contremaîtres non — aurait classé VBN du mauvais côté : la liste est donc
nommée en clair dans `CONTREMAITRES`, en tête du script.

> « En pause, l'adjoint est contremaître uniquement s'il n'y a pas de
> contremaître en pause ce créneau-là. »

Le poste de contremaître est donc tenu par le contremaître quand il est
présent ; l'adjoint qui l'accompagne est un renfort. Seul, il **fait
fonction**. Sur 2026, 242 créneaux sont dans ce cas.

## La prime conservée, écrite en toutes lettres dans le commentaire

Confirmé par le client le 21/09/2026 : « il faut vraiment prendre en compte
100 % des commentaires et en faire une règle stricte ».

**336 journées de 2026** portent, dans le commentaire Excel, une phrase qui
nomme la prime à payer : « conserver prime de nuit », « maintien prime N »,
« Conserve sa prime de pause », « maintien prime PM ». Elles se répartissent
en `N` (219), `PM` (39), « nuit » écrit en toutes lettres (38), « pause »
(37), `AM` (2) et « dimanche nuit » (1).

L'application les ignorait toutes. Sur **275 d'entre elles**, le poste qu'elle
retenait — donc la prime qu'elle payait — n'était pas celui que le
commentaire nomme. Une nuit de 8 h se paie 32 € de prime, une après-midi
14,40 €, une journée rien : l'écart va jusqu'à 32 € sur une seule journée.

### Ce que la règle fait

> Quand le commentaire nomme une prime, cette prime l'emporte sur le poste
> que la lecture a retenu. Le commentaire parle de la PAIE ; la cellule et
> son annotation disent le TRAVAIL.

`primeGardee()` traduit le mot qui suit « prime » : `N` et `nuit` → `N`,
`PM` et `après-midi` → `PM`, `AM` et `matin` → `AM`. « Prime de pause », sans
nommer laquelle, désigne la pause **prévue** : celle que la cellule porte
avant que l'annotation ne la remplace — ATA le 18/03, `["AM","SD 26",
"Conserve sa prime de pause"]`, c'est AM. Le premier mot ne suffit pas
toujours : « conserver prime de dimanche nuit » se lit sur le second.

La règle s'applique **à la fin de `lireJournee()`**, après la correction de
cycle : celle-ci recalcule tout depuis zéro et effacerait la prime posée plus
tôt. C'est la même place, et pour la même raison, que les heures renvoyées
par « pris le ».

### Deux postes, parce qu'ils répondent à deux questions

La prime ne déplace personne de pause. `r.s` porte le poste dont la prime est
**payée** ; `r.sp`, quand ils diffèrent, porte celui qui a été **presté**.

- La fiche de paie lit `r.s` — c'est elle qui compte les primes.
- L'onglet Équipe groupe par `r.sp || r.s` : AFA le 04/09 a fait 7h-15h en
  gardant sa prime de nuit ; il figure en journée, pas dans la pause de nuit,
  sans quoi l'effectif de la nuit serait faux et le rééquilibrage avec lui.
- La case du calendrier peint le poste presté et souligne, d'un liseré à la
  couleur de la prime, celle qui est conservée. La bulle l'écrit : « Nuit ·
  8 h — Prime d'après-midi conservée ».

C'est exactement ce que l'application faisait déjà des journées `SD26` et
`D-F`, travaillées en horaire de jour et payées à la prime de leur pause. Le
commentaire fait ici le même travail, en toutes lettres ; il n'y avait qu'à
l'écouter.

### Mesure

336 journées lues, **100 %** traduites en une prime. 275 changent de prime :
103 `PM→N`, 102 `AM→N`, 26 `D→N`, 25 `AM→PM`, 13 `D→PM`, 3 `N→PM`, 2 `D→AM`,
1 `PM→AM`. Les 61 autres confirment ce que l'application appliquait déjà.

Les neuf règles dures de `verifier-calendrier.js` restent à zéro et les quatre
compteurs de journées sont inchangés — la règle déplace la prime, jamais les
heures. Les compteurs flex time restent à 76/77.

## « Absence » ne veut rien dire tant qu'on n'a pas dit laquelle

Le client, le 21/09/2026 : « pour mon horaire, tu indiques 94 jours
d'absence, ça me paraît beaucoup, que considères-tu absence ? »

Il avait raison. La tuile de l'année additionnait **toute journée non prestée
portant un code**. Sur ses 94 :

| | |
|---|---|
| congés payés (CP) | 26 |
| vacances annuelles (VA) | 18 |
| **maladie (MAL)** | **18** |
| récupération jour férié (RJF) | 10 |
| RTT | 5 |
| DTT | 5 |
| formation | 1 |
| mouvements de compteur seuls (`4h +FT`…) | 11 |

C'est la distinction qu'il avait déjà donnée pour l'onglet Équipe — « il faut
différencier absent et en congé ; les absents ne sont que les personnes
malades » — et elle vaut pour sa propre fiche. Trois tuiles désormais :
**jours de congé**, **jours de maladie** (cachée quand il n'y en a pas), et
**jours de repos**.

Et une journée de repos qui ne porte qu'un mouvement de compteur —
`["-","4h +FT","presté le 27.04"]` — est un **repos**. Le classeur y écrit
« - » ; les heures ont été faites un autre jour, et elles sont comptées là.
Onze journées de VBN passaient pour des absences à ce titre.

VBN 2026 : **174 jours prestés, 65 de congé, 18 de maladie, 104 de repos.**

Rien de tout cela ne touche le calcul de la fiche : ces tuiles comptent des
journées, elles n'en paient aucune.
