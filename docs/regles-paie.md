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

| Mois 2026 | Prime / jour |
|---|---|
| janvier – février | 26,865 € |
| mars – août | 27,365 € |

La prime a donc été indexée entre février et mars, mais **pas dans la même
proportion que le salaire horaire** : c'est bien un forfait, et non un
pourcentage.

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

| Réglage | Où le lire |
|---|---|
| Rémunération fixe | déduite : « Montant heures prestées » ÷ fraction |
| Fraction payée | un temps partiel la réduit — 0,9 pour un congé parental 9/10 |
| Diviseur horaire | rémunération fixe ÷ salaire horaire |

Le recoupement doit être exact **au centime**, et le salaire horaire juste
**à la quatrième décimale** — c'est la ligne « Heure de déplacement à » de la
fiche qui le confirme.

**La fraction est le piège** : c'est la rémunération à temps plein qui se
saisit, et la fraction qui la réduit. Saisir le montant déjà réduit avec une
fraction de 1 donnerait le bon montant mensuel mais un salaire horaire faux,
et toutes les primes horaires avec.

**Aucun montant de salaire ne s'écrit dans ce document.** Le dépôt est
public : `docs/` se lit sans authentification, aussi bien par le site que
par `raw.githubusercontent.com`. Les règles se décrivent ; les montants
restent sur l'appareil de chacun.

Le piège s'est refermé le 21/09/2026, sur quelqu'un qui avait ce paragraphe
sous la main et ne l'a pas lu : des réglages préparés pour VBN portaient
`fraction: 1`, au motif que ses jours de congé parental étaient écrits un par
un dans l'horaire. Les deux ne s'excluent pas — **l'horaire dit QUAND le
dixième est pris, la fraction dit COMBIEN**. La fiche portait les deux
montants à deux lignes d'écart.

Contrôle en une soustraction : « Rém. périodique fixe » et « Montant heures
prestées » sont deux lignes différentes de la fiche. Si elles diffèrent, la
fraction n'est pas 1.

### Les codes, leur sens et ce qu'ils paient

La table de référence. Elle se relit **avant** de toucher à `ABS[]` dans
`index.html` ou à la légende de l'onglet « Mon horaire » — les deux doivent
dire la même chose, et elles se sont déjà contredites.

**Aucune ligne d'heures ne porte de montant.** Relevé sur les onze fiches
mensuelles : « Heure(s) prestée(s) », « Heure(s) SMG maladie », « Heure(s)
congé parent. » sont des QUANTITÉS. Ce qui paie, c'est « Rém. périodique
fixe » et « Montant heures prestées ». La colonne « Payé » ci-dessous dit
donc si la rémunération fixe **couvre** la journée, et non si une ligne
porte des euros.

| Code | Ce que c'est | Ligne de fiche | Payé | D'où on le sait |
|---|---|---|---|---|
| `VA` | vacances annuelles | Heure(s) vacances annuelles | oui | fiches |
| `RTT` | réduction du temps de travail | Heure(s) RTT | oui | fiches |
| `RHS` | récupération d'heures supplémentaires | Heure(s) récup. heures supplémentaires | oui | client, 20/09 |
| `DTT` | congé d'ancienneté | Heure(s) repos compensatoire | oui | fiches |
| `RJF` | jour férié de remplacement, à choix libre | Heure(s) jour férié / RJF | oui | classeur |
| `FER` | jour férié légal | Heure(s) jour férié | oui | fiches |
| `SMG` | **salaire mensuel garanti** — la maladie payée par l'employeur | Heure(s) SMG maladie | oui | fiches |
| `FORM` | formation, congé syndical | Heure(s) formation syndicale | oui | fiches |
| `CP` | congé parental 9/10 ou 4/5 | Heure(s) congé parent. AR 29.10.1997 | **non** — la fraction l'a déjà retiré | client, 25/09 |
| `CT` | crédit-temps 1/5 ou 1/2 | Heure(s) crédit-temps | **non** — idem | client, 25/09 |
| `TP` | temps partiel | Heure(s) temps partiel | **non** — idem | client, 25/09 |
| `SANS SOLDE`, `CSS` | congé sans solde | aucune | **non** | classeur |
| `ABS` | **deux choses** — voir ci-dessous | selon l'origine | selon l'origine | classeur + code |
| `+FT`, `−FT` | flex time épargné / repris | compteur | différé | client, 20/09 |
| `HS` | heures supplémentaires | compteur + sursalaire | voir « Le rappel » | client, 25/09 |
| `1/2 …`, `3H …` | la même chose sur 4 h, 3 h… | la même | la même | classeur |

**`SMG` n'est pas un mot de la maison** — le client ne le connaissait pas et
a demandé ce que c'était. Il vient de **la fiche de paie**, qui écrit
« Heure(s) SMG maladie » : *salaire mensuel garanti*, la rémunération que
l'employeur continue de verser pendant la maladie. L'application a repris
l'intitulé du secrétariat social pour que l'onglet Contrôle se lise ligne à
ligne contre la fiche — et il ne faut pas le présenter comme venant du
client.

**`ABS` est le seul code qui dise deux choses**, et il faut le savoir :

- **écrit par le CLASSEUR**, c'est une maladie, **toujours**. `ALIAS_HORAIRE`
  le traduit en `MAL`, donc en `SMG` — payé. C'est le vocabulaire de la
  maison, confirmé par le client le 25/09/2026 : « chez nous "Absence" veut
  dire maladie » ;
- **posé À LA MAIN** dans le mois, c'est une absence non rémunérée, et la
  fiche écrit « Heure(s) abs. volontaire / injustifiée ».

### « Abs » avec « remplace X » n'est pas une contradiction

Sur les **1 848 journées `Abs`** de l'année, **562 portent un commentaire qui
parle d'un remplacement** — « remplace GPS », « remplace ATA ». De quoi
croire que la personne était au travail et que la lecture se trompe en
affichant une absence à zéro heure. La question a été posée au client le
25/09/2026 ; sa réponse tient en deux mots : **toujours une absence**.

**Et le classeur le prouve tout seul.** Quarante-cinq de ces commentaires
disent LES DEUX à la fois :

> `["PM","Abs","remplace GPS remplacé par JBI? et YPE"]`
> `["N","Abs","Remplace LDT remplace FLI; remplacé par LDY"]`

On ne peut pas remplacer quelqu'un et être remplacé le même jour au même
poste. La seule lecture qui tienne est celle de la **règle de tête du
projet** : le code franc est la journée **PRÉVUE** — il devait remplacer GPS
— et l'annotation dit ce qui s'est réellement passé : il était absent, et
d'autres ont couvert. Le commentaire garde la trace des deux moments.

**Il n'y avait donc rien à corriger**, et c'est écrit ici pour que le doute
ne se rouvre pas : ces 562 journées s'affichent en absence à zéro heure
parce qu'elles en sont.



La légende a déjà menti sur ce code : elle le rangeait dans « Compteurs et
NON PAYÉ » avec la définition « absence injustifiée », alors que le chemin du
classeur le paie. **Le code avait raison, la légende avait tort, et dans le
sens qui coûte cher.**

**Deux autres ont menti, et les trois fautes ont la même forme** : un libellé
qui décrit autre chose que ce que le code fait. `CT` était donné pour un
« congé de circonstance » ; `CT` et `CP` étaient rangés parmi les heures
« assimilées à du travail, payées comme des heures prestées », alors que la
fraction les a déjà retirées de la rémunération fixe. **Une légende n'est pas
de la décoration : c'est la seule chose que l'utilisateur lit pour savoir ce
qu'il regarde.**

## Trois dispositifs, une seule arithmétique — et une allocation hors fiche

Le client, le 25/09/2026, a décrit les trois réductions du temps de travail
que connaît le droit belge. Elles mènent toutes au même 4/5 ou au même 9/10,
et l'application les traitait comme un seul objet : une « fraction payée ».

| | Travail | Allocation de l'ONEM | Motif | Temporaire |
|---|---|---|---|---|
| temps partiel `TP` | 80 % ou 90 % | non | aucun à justifier | pas nécessairement |
| crédit-temps `CT` | 80 % (1/5) ou 50 % (1/2) | possible, sous conditions | selon le motif | oui |
| congé parental `CP` | 80 % (1/5) ou 90 % (1/10) | possible, sous conditions | un enfant | oui |

**Sur la fiche, les trois font la même arithmétique** : la rémunération fixe
est multipliée par la fraction, et la journée non prestée n'ajoute rien. La
fiche du secrétariat social le montre noir sur blanc — « Heure(s) congé
parent. AR 29.10.1997 » y est une QUANTITÉ, sans montant en regard, comme
« Heure(s) prestée(s) » et « Heure(s) SMG maladie ». Relevé sur les onze
fiches mensuelles : aucune de ces lignes ne porte de colonne en euros.

**Ce qui les sépare ne se voit donc PAS sur la fiche, et c'est le piège.**
Le crédit-temps et le congé parental ouvrent une allocation de l'ONEM ; elle
est versée par l'ONEM, pas par l'employeur, et ne figure nulle part sur la
fiche de paie. **L'application ne la simule pas, et ne le peut pas** — elle
recopie une fiche. Quelqu'un en `CP` ou en `CT` reçoit donc plus que ce que
cet écran affiche, et rien ne le disait. Les infobulles des trois lignes le
nomment désormais, et le réglage « Fraction payée » aussi.

**Le temps partiel, lui, n'ouvre rien** : c'est exactement ce que le client
disait le 25/09 — « CP et TP c'est pareil mais sans la compensation de
l'ONEM ».

### `CT` n'est pas un congé de circonstance

La légende des codes écrivait « congé de circonstance ». C'était faux, et le
classeur le prouve tout seul : les **159 journées codées `CT`** sont chez
**trois personnes**, exactement les trois qui portent un contrat « CT 20% »
en pied de feuille, à raison de **55, 53 et 51 journées** — une par semaine
sur l'année. Un congé de circonstance se compte en jours par événement,
jamais en cinquante. C'est un **crédit-temps 1/5**, confirmé par le client le
25/09/2026.

La journée se lit donc comme celle d'un temps partiel : la réduction est déjà
dans la rémunération fixe par la fraction 0,80, et la ligne de fiche est une
quantité sans montant. Elle s'appelle « Heure(s) crédit-temps » et non plus
« Heure(s) CT », et elle a quitté le seau des heures « assimilées à du
travail » — ces heures-là ne sont pas payées, et l'infobulle disait le
contraire. Le congé parental en est sorti pour la même raison.

### Les régimes que chaque dispositif connaît

Le crédit-temps se prend en 1/5 ou en 1/2 ; **le 9/10 n'en est pas un
régime**. Le congé parental, lui, se prend en 1/5 ou en 1/10. Le temps
partiel est ce que le contrat dit, et rien ne lui est opposé.

`_dire_regimes()` le dit sur la sortie d'erreur quand un pourcentage ne va
pas avec son code — **sans rien refuser ni corriger** : un pourcentage hors
régime est le plus souvent une faute de frappe du pied de feuille, mais il
peut aussi être un régime qu'on ne connaît pas, et la seconde hypothèse
interdit de trancher à la place de qui écrit. Au 25/09/2026 elle ne dit
rien : les 33 contrats codés tombent tous sur un régime légal — 21 `CP 10%`,
2 `CP 20%`, 7 `TP` et 3 `CT 20%`.

### Cinquante pour cent est la seule exception à la bande refusée

Le convertisseur garde sans fraction tout pourcentage entre 31 et 69, faute
de savoir s'il dit la réduction ou la part prestée. **Un mi-temps s'écrira
« 50% » un jour** — c'est le second régime du crédit-temps — et il serait
tombé en plein dans cette bande. Or à cinquante l'ambiguïté n'existe pas :
cinquante pour cent de réduction et cinquante pour cent prestés sont le même
nombre, 0,50. On ne devine rien en l'acceptant ; on constate que les deux
lectures coïncident.

**Cent avec un code reste refusé**, et pour la raison inverse : « CP 100% »
peut dire un temps plein retrouvé (1,00) comme une suspension complète
(0,00), et l'écart est tout le socle du mois. Un « 100% » sans code reste ce
qu'il est — personne n'a nommé de dispositif, donc rien n'est suspendu.

### La semaine de la maison fait 38:40, et non 38:00

Les exemples du droit se comptent sur 38 h — 4/5 = 30 h 24, 9/10 = 34 h 12.
**Ce ne sont pas les heures d'ici.** La fiche porte « Nombre heures / semaine
temps plein / 38:40 », ce qui donne **30 h 56** pour un 4/5 et **34 h 48**
pour un 9/10. Ne pas recopier les nombres d'un exemple générique : c'est la
fiche qui donne la semaine.

## La commission paritaire, relevée et non supposée

**`220.00`**, écrit en toutes lettres sur la fiche : « Commission paritaire
220.00 ». C'est la commission des EMPLOYÉS de l'industrie alimentaire.

Elle figurait depuis toujours en tête de `CLAUDE.md` et du `README`, sans
que rien ne dise d'où elle venait — une valeur héritée vaut ce que vaut sa
source. Relevée le 25/09/2026 sur les fiches : **les onze fiches mensuelles
la portent, toutes la même**. Les trois autres documents du lot — le pécule
et deux décomptes — ne portent pas cette ligne, ce qui est normal : ce ne
sont pas des fiches de paie mensuelles.

**Ce qu'elle commande** : le barème, les primes d'équipe, le chèque-repas,
le treizième mois, la CCT 90 — tout ce que ce document décrit est celui de
cette commission-là. Une règle relevée sur une fiche ne vaut que pour elle.

**Et c'est la ligne à regarder LE JOUR OÙ UNE FICHE D'OUVRIER ARRIVERA.**
Le client l'a annoncée : « il ne faudra pas calculer les intérimaires de la
même manière (pareil pour les primes et jours de paye) ». Dans l'industrie
alimentaire, les ouvriers relèvent d'une autre commission que les employés ;
**laquelle, c'est la fiche qui le dira**, et non une supposition. Rien n'est
codé d'ici là — voir « Les intérimaires ».

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
le salaire horaire. La valeur par défaut de l'application, 148,368007,
correspond à 38:40 par semaine.

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
Avantage non récurrent                B
Cotisation de solidarité     B × 13,07 %
Précompte professionnel              0,00     le bonus en est exempt
Net                          B × 86,93 %
```

**Elle est versée en deux fois : une avance en septembre, le solde en mars.**
Confirmé par le client le 21/09/2026. Pour VBN :

| | Fiche |
|---|---|
| avance 2026 | période 08/2026, payée le 02/09 |
| solde 2026 | mars 2027, à venir |
| solde 2025 | période 02/2026, payée le 16/03 |

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

| Période | Ligne de la fiche |
|---|---|
| 05/2026 | Simple Pécule |
| 05/2026 | Double pécule de vacances |
| 06/2026 | Treizième mois |

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
Treizième mois                            T   ( = rémunération fixe × fraction )
ONSS 13,07 %                     T × 0,1307
base au taux distinct            T × 0,8693
Précompte 53,50 %       T × 0,8693 × 0,5350   ← au centime près sur la fiche de juin
```

### Le double pécule : la formule NE tombe PAS

La fiche de mai porte, sur le double pécule, un précompte que l'application
ne retrouve pas — quelle que soit la façon dont on y range le simple pécule :

| Ce qu'on met dans « complément DPV » | Écart au précompte de la fiche |
|---|---|
| 0 | environ 224 € de trop peu |
| le simple pécule | environ 245 € de trop |

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

La fiche la porte en retenue, sous « **Déduction avance reçue** ». C'est un
montant FIXE, le même tous les mois sans exception — sauf février 2026, où
il est double.

Ce doublement est un **incident, pas une règle**. Le client : « en février
c'était une erreur, elle avait été payée deux fois ; j'ai dû rendre une
partie avec mon salaire du mois d'après. » La reprise se lit sur la fiche
complémentaire du 09/03/2026, qui porte un **brut négatif** sous « Recup à
payer » — une reprise, non une retenue ordinaire, d'où le brut négatif.

Un simulateur n'a pas à reproduire cela : c'est une correction de paie, pas
un mécanisme. Mais il fallait l'écrire, sinon ce mois restera longtemps un
mystère pour qui compare les fiches à l'horaire.

### Les deux dates, et pourquoi ce ne sont pas des jours « ouvrables »

**Confirmé par le client le 22/09/2026** : « la règle pour les employés,
c'est l'avance 4 jours ouvrables avant la fin du mois, et le solde 4 jours
ouvrables après la fin du mois ».

Le mot employé était « ouvrable », et c'est bien celui de la loi du
12 avril 1965 sur la protection de la rémunération, d'où sort ce délai de
quatre jours. Mais au sens légal **le samedi est un jour ouvrable**, et
cette lecture plaçait quatre dates de 2026 sur un samedi : le 4 avril, le
25 avril, le 4 juillet et le 26 décembre. Le client, aussitôt :
**« jamais payé le wk »**.

C'est le fait qui tranche, pas le vocabulaire. On compte donc du **lundi au
vendredi, jours fériés exclus**, à partir du dernier jour du mois sans le
compter lui-même. Contrôlé sur les douze mois de 2026 : aucune date ne tombe
un week-end ni un jour férié.

L'application en tire les deux montants du mois — l'avance, et le solde qui
est le net total moins l'avance — dans un bloc sous le Résumé, à partir du
réglage **« Avance mensuelle (€) »**.

### Où la saisir

Elle se saisit dans le champ **« Avance déjà reçue (€) »** de l'onglet
Horaire, mois par mois. Sans elle, le « net à recevoir » de la fiche simulée
est trop élevé d'autant : le brut et les retenues sont justes, c'est le
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

## Les intérimaires

**Liste donnée par le client le 22/09/2026**, onze personnes :

> LAA · JBA · JBS · TCE · CHD · MGY · LHS · CJD · DKS · SMK · MMS

**Le classeur ne le dit nulle part.** Vérifié : ce qui est écrit au-dessus
de leur nom — « Fermentation », « Renfort arrière », « Polyvalent » — est
exactement ce que portent des gens qui ne sont pas intérimaires. Il n'y a
donc rien à lire dans le fichier : cette liste est tenue À LA MAIN, et
**elle vieillira** à chaque embauche ou départ. La redemander au client
quand elle compte.

**L'application n'en fait rien aujourd'hui, et c'est voulu.** Le client :
« rien pour l'instant, mais garder l'info ». Une liste codée sans emploi
égarerait celui qui la relit ; elle vit donc ici, et non dans `index.html`.

**Ce à quoi elle servira** — le client, le 22/09/2026 : « quand je te
donnerai une fiche de paye d'un ouvrier, il ne faudra pas calculer les
intérimaires de la même manière (pareil pour les primes et jours de paye) ».
Trois choses, donc, et aucune n'est encore connue : le calcul de la fiche,
les primes, et les jours de paie. **Ne rien deviner sur ces points** : ils
touchent à des montants.

Au passage, leur situation dans le classeur, telle qu'elle est au
22/09/2026 :

| | équipe | poste au classeur | polyvalence validée |
|---|---|---|---|
| LAA | Shift 2 | Fermentation | Fermentation |
| JBA | Shift 3 | Chaudières | Chaudières |
| JBS | Shift 4 | Chaudières | Chaudières |
| TCE | Shift 1 | Meunerie | Meunerie |
| CHD | Shift 5 | Fermentation | Fermentation |
| MGY | en formation | chaudières éq. 1 | aucune — en formation |
| LHS | Shift 5 | Renfort arrière | Fermentation |
| CJD | Shift 1 | Polyvalent | Gluten |
| DKS | Shift 3 | Meunerie | Meunerie |
| SMK | Shift 4 | Renfort avant | Meunerie |
| MMS | Shift 3 | Polyvalent | Gluten |

**Deux lignes semblent fausses et ne le sont pas.** LHS est inscrit
« Renfort arrière » avec la seule Fermentation, SMK « Renfort avant » avec
la seule Meunerie — un renfort suppose pourtant plus d'un poste. Le client,
le 22/09/2026 : « oui, ce n'est pas logique, mais c'est comme ça que le RH
les a attribués dans le classeur ». **Ne pas « corriger » ces lignes** : le
classeur dit vrai sur ce qu'il décrit, c'est l'attribution qui est ainsi.

**MGY est le quatrième opérateur en formation**, avec SKS, LHR et GST. Le
classeur le place bien aux chaudières de l'équipe 1 — l'application l'y
montre, avec un **F** — mais il n'y a aucune polyvalence validée, et c'est
la règle : on n'est pas validé là où l'on se forme.

## `TP` : le jour non travaillé d'un temps partiel

**Confirmé par le client le 25/09/2026.** D'abord : « TP c'est temps
partiel, CP (congé parental 4/5 ou 9/10) et TP c'est pareil mais sans la
compensation de l'ONEM je pense ». Puis, interrogé sur le paiement de la
journée : « pour le TP je ne pense pas, c'est une réduction de temps de
travail avec la loi belge pour le 9/10 ou 4/5 ».

**Ce n'est donc pas une absence que l'on pose.** C'est un jour qui ne fait
pas partie du contrat — comme un samedi l'est pour tout le monde. La
rémunération est déjà réduite à la source, et le jour non travaillé n'a donc
**aucune ligne de fiche** à porter : la réduction est dans le salaire de
base, pas dans une retenue.

Le réglage qui la porte est **« Fraction payée »**, qui multiplie la
rémunération fixe forfaitairement. Son aide ne nommait que le congé
parental — « 0,90 = congé parental 9/10 » — et le client l'a relevé :
« une fraction payée pour les TP ? ce n'est pas plutôt les CP ? ». Le champ
est générique, un 4/5ᵉ temps partiel faisant la même arithmétique qu'un
4/5ᵉ parental, mais **un texte qui ne nomme qu'un cas laisse l'autre croire
qu'il n'est pas concerné** : l'aide et l'écran d'accueil nomment désormais
les deux.

C'est ce qui sépare `TP` de `CP`. Les deux marquent le même jour d'absence,
mais `CP` ouvre l'allocation de l'ONEM et porte sa ligne — « congé parental
AR 29.10.1997 » — tandis que `TP` ne porte rien.

### La mesure qui a confirmé le « c'est pareil »

Les deux codes se posent de la même façon : par blocs de un à trois jours,
et non un jour fixe par semaine. Leurs totaux annuels sont ceux d'un temps
partiel — 26 journées valent un jour par quinzaine (9/10), 51 un jour par
semaine (4/5).

| | Journées | Séries | Tailles |
|---|---|---|---|
| VBN `CP` | 26 | 12 | 3×6, 2×2, 1×4 |
| GSK `CP` | 51 | 26 | 3×9, 2×7, 1×10 |
| LCI `TP` | 25 | 10 | 3×5, 2×5 |
| FLN `TP` | 40 | 14 | 3×8, 2×1, 1×3 |

`TP` : **209 journées chez 8 personnes** — FLN 40, LAX 34, ATA 26, DWS 26,
SPT 26, SMA 26, LCI 25, GDT 6. `CP` : 423 journées chez 17 personnes.

### Le calcul faisait exactement l'inverse

`TP` était rangé dans `JOUR_PRIME_PAUSE`, donc lu comme une journée
**prestée** en horaire de jour. Même forme de cellule, lecture opposée :

| Cellule | Avant | Après |
|---|---|---|
| `["7h-15h","CP"]` | absence — 0 h | inchangé |
| `["6h-14h","TP"]` | poste — **8 h + prime de jour** | absence — **0 h** |

La cellule franche de ces journées porte ce que la rotation avait **prévu**
— `D` (73), `6h-14h` (57), `7h-15h` (47), `N` (18), `PM` (9), `AM` (5) — et
non ce qui a été presté. Les 209 journées comptaient donc huit heures et une
prime pour des gens qui sont chez eux, et le module des manques les croyait
à leur poste.

Le code entre au barème des absences avec **son propre `k`** plutôt qu'en
empruntant celui de `SANS SOLDE` : un congé sans solde et un temps partiel
ne sont pas la même chose, et le jour où une fiche montrera une ligne pour
l'un, il ne faudra pas la poser sur l'autre.

### La fiche montre les heures, elle ne les paie pas

**Aucun code d'absence ne paie quoi que ce soit**, et c'est ce que l'audit
du 25/09/2026 a établi : les lignes d'absence portent une **quantité** (`q`,
`qh:true`) et pas de valeur — seules les `bl(...)` entrent dans le brut. La
rémunération vient du socle forfaitaire `remFixe × fraction` et des
suppléments.

`k:"TP"` ne décidait donc que d'une chose : **montrer ou taire** les heures.
La première version les taisait. Le client, interrogé : « fait cela » — la
ligne **« Heure(s) temps partiel »** s'affiche désormais à côté de celle du
congé parental, dont elle est le jumeau.

**Elle a son infobulle à elle, et surtout pas celle des heures assimilées à
du travail** : ce motif-là — `^Heure\(s\) (vacances|jour férié|repos|RTT|…)`
— annonce « payées comme des heures prestées », ce qui serait faux ici. Le
texte du temps partiel dit l'inverse : ni prestées ni payées, la réduction
étant déjà dans la rémunération fixe.

Vérifié au navigateur sur ATA : sa fiche de septembre porte **24 heures de
temps partiel** — ses trois journées du mois — et **aucune colonne en
euros**, contrairement à la ligne de rappel qui la suit.

### Ce que la correction déplace

**Aucune prime**, et c'est contre-intuitif : `primeD` vaut **0**, donc les
209 journées lues en horaire de jour n'en portaient aucune. Le socle, lui,
est forfaitaire (`remFixe × fraction`) et ne dépend pas des heures.

Ce qui bougeait vraiment, c'est le **chèque-repas** : `if(h>=4)
acc.joursCr++` en donne un par journée prestée d'au moins quatre heures.
**209 chèques étaient donc accordés pour des jours non travaillés** — FLN
40, LAX 34, ATA 26, DWS 26, SPT 26, SMA 26, LCI 25, GDT 6.

Journées prestées **14 645 → 14 436**, absences affichées **+209** — soit
exactement les 209 journées, sans un écart. Neuf règles à zéro, compteurs
**76/77**, manques d'effectif **inchangés à 11 journées / 11 places** : le
rééquilibrage couvre déjà ces absences. Les couples de polyvalence passent
de 101 à **99** — deux couples dont toutes les journées étaient des `TP` —
et les 33 au quota ne bougent pas.

**La `fraction` reste à saisir à la main.** On pourrait la déduire du nombre
de journées `TP` de la personne, mais c'est un réglage personnel qui ne
quitte pas l'appareil, et une déduction se tromperait sur une année
incomplète.

## Un congé et un rappel dans la même cellule

**Confirmé par le client le 25/09/2026.** GPS le 02/07,
`["7h-15h","RHS+02h-06h","Rappel le 02/07"]` — **la seule cellule de
l'année** à mêler un code d'absence et une plage.

D'abord : « il était bien en RHS mais il a été rappelé le jour même pour
venir faire 02-06 ». Puis, sur la nature de ces heures : « il a fait 4 HS de
02-06h en étant rappelé le jour même ; **je sais que c'est du HS car il n'y
a aucune cellule dans sa liste qui mette `+4h FT`**, et de 06 à 14h il était
bien en RHS (reprise d'heure sup donc congé) ».

Le raisonnement est celui du classeur lui-même : l'épargne au compteur
s'écrit, elle ; son absence dit que les heures ont été payées.

**Ce que le calcul faisait avant** : poste `D`, **8 h prestées**, et aucun
RHS. Les deux moitiés étaient fausses.

### Deux faits, un seul champ

Le champ `abs` d'une journée n'accepte qu'un code. **Le congé le prend** —
c'est lui qui vide la journée, et c'est le même libellé de fiche que ses
1er et 3 juillet, qui portent `RHS` tout court. Les heures supplémentaires
passent par **`ax`**, que l'accumulateur concatène déjà à `a` :
`codesJour=(rec.a?[rec.a]:[]).concat(rec.ax||[])`. Ses deux autres lecteurs
ne regardent que les codes dont `h>0`, donc un `4H HS` n'y retire ni n'y
ajoute rien.

Un champ parallèle aurait demandé cinq points de synchronisation — le
parseur, l'accumulateur, les deux `enregistre()` et les deux autres
lecteurs. **Une source de plus pour un mécanisme existant vaut mieux qu'un
mécanisme de plus à tenir en phase.**

### La plage du rappel ne se met PAS dans `r.plage`

Une première version l'a fait, et le résultat était faux sans rien casser.
`r.plage` dit la plage réellement prestée **comme poste du jour**, et
`dureeReelle("D",[2,6],8)` rend **12** : la machinerie étend le poste pour
couvrir 2 h à 6 h et lit une journée de douze heures, dont elle retire
ensuite les huit de RHS. Résultat affiché : « 4 h prestées en D » —
c'est-à-dire ni le congé, ni les heures supplémentaires.

La plage ne sert donc qu'à **compter** les heures du rappel. La journée
garde la plage de sa cellule franche et se vide entièrement contre le RHS.

### Ce que la fiche porte, vérifié au navigateur

Fiche de juillet 2026 de GPS :

| Ligne | |
|---|---|
| 24 h récup. heures supplémentaires | ses trois journées RHS des 1, 2 et 3 |
| 4 h supplémentaires prestées (codes HS de l'horaire) | les 02h-06h |
| 4 h HS non compensées à 150 % | elles sont payées |
| 4 h de déplacement — rappel J / J-1 | le rappel du jour même |

### Les heures vont au compteur, la prime de pause se paie

**Confirmé par le client le 25/09/2026**, en réponse à la question de la
prime de nuit : « il reçoit les 4 h HS dans un compteur et il les reprend
quand il veut ou se les fait payer en fin d'année, quand on doit mettre les
compteurs HS à zéro », puis « **les 4 h de rappel (02-06) sont payées en
nuit** ».

Deux choses distinctes, et la fiche les séparait déjà sans qu'on s'en serve :

| Accumulateur | Ce qu'il paie |
|---|---|
| `hsAutoBkt` | les **heures** — ligne « HS non compensées » |
| `hsAutoPoste` | la **prime d'équipe** de la pause où elles ont été prestées |

**Une heure récupérée rend l'heure, pas la prime de la pause.** Les heures
versées au compteur ne passent donc plus par `hsAutoBkt` ; la prime, elle,
reste due.

**Et le poste des heures supplémentaires n'est pas celui de la journée.** Un
rappel de 02 h à 06 h est de la nuit, même posé sur une journée de congé
dont la cellule franche dit « 7h-15h ». Sans `rec.hsp`, la prime se cherchait
dans le seau « D », dont la prime d'équipe est nulle — donc aucune ligne du
tout. Deux champs portent cela jusqu'au mois : `hsp` le poste, `hsc` le
versement au compteur.

Fiche de juillet 2026 de GPS, vérifiée au navigateur :

| Ligne | |
|---|---|
| 24 h récup. heures supplémentaires | ses trois journées RHS des 1, 2 et 3 |
| 4 h supplémentaires prestées (codes HS de l'horaire) | les 02h-06h |
| **4 h supplémentaires versées au compteur (non payées ce mois-ci)** | la règle du client |
| **4 h Suppl. Équipe Nuit à 150 % (heures suppl. de l'horaire)** | la prime, elle, est payée |
| 4 h de déplacement — rappel J / J-1 | le rappel du jour même |

La ligne « HS non compensées » a disparu de ce mois : les heures ne sont plus
payées deux fois, une fois maintenant et une fois à la reprise.

### La règle vaut pour TOUTES les heures supplémentaires

**Confirmé par le client le 25/09/2026**, interrogé sur les 205 autres
journées : « cela dépend de si il remplit une feuille pour avoir des FT+ ou
des HS. **Quoi qu'il arrive les 2 vont dans un compteur**, mais le compteur
HS n'apparaît pas dans le classeur. »

C'est exactement le raisonnement qu'il avait tenu sur GPS — « je sais que
c'est du HS car il n'y a aucune cellule qui mette `+4h FT` ». **Le classeur
ÉCRIT l'épargne au flex time ; son silence désigne l'autre compteur**, celui
qu'il ne porte pas.

### La fiche porte DEUX lignes, et j'en avais retiré deux de trop

**Le client, le 25/09/2026 : « vérifie avec toutes mes feuilles de paye si
ta logique est bonne ».** Elle ne l'était pas, et ce sont ses fiches qui le
disent — trois d'entre elles portent des heures supplémentaires, toujours
sous la même PAIRE de lignes :

```
 1:30  Heures sup à compenser à <taux> à 150 %     +
-1:30  déduc HS à comp à <taux>                    −
```

Le sursalaire est payé au taux majoré **le mois de la prestation**, et
l'heure de base est **déduite** puisqu'elle sera reprise plus tard. Net : la
moitié du taux horaire. Décembre porte la même paire pour 4:30, et la fiche
affiche le solde d'année du compteur juste à côté.

**J'avais retiré les deux lignes** en croyant que « les heures vont au
compteur » voulait dire « rien n'est payé ce mois-ci ». C'était faux d'une
moitié : **l'HEURE part au compteur, le SURSALAIRE ne l'attend pas.**

Les deux lignes s'écrivent séparément plutôt que nettes : l'onglet Contrôle
se lit ligne à ligne contre la fiche du secrétariat social, et une ligne à
50 % n'y existe pas. Vérifié au navigateur sur juillet — `4 Heures sup à
compenser à 150 %` et `−4 déduc HS à comp`, net exactement la moitié du taux
horaire sur quatre heures.

**Et le champ manuel reste distinct** : « HS non compensées » désigne des
heures payées EN ENTIER au lieu d'être récupérées. Ce n'est pas le même cas,
et la fiche ne les nomme pas pareil.

**ELLES SONT PAYÉES À LA REPRISE, PAS AU MOIS OÙ ELLES SONT PRESTÉES**, et
c'est la formulation qu'il a fallu corriger. Le client : « les HS sont payées
quand les opérateurs reprennent leurs heures sup (indiqué dans l'horaire ou
en commentaire), donc ta phrase n'est pas correcte ». J'avais écrit que
l'application ne les payait plus — c'était faux, et le circuit se lit en
deux temps :

| Quand | Ce que le classeur écrit | Ce que la fiche fait |
|---|---|---|
| l'heure est **prestée** | rien — le compteur HS n'est pas dans le fichier | elle va au compteur |
| l'heure est **reprise** | `RHS`, `2h RHS`, ou un commentaire | **la journée est payée** |

Une journée entière de reprise vaut zéro heure prestée et le socle
forfaitaire ne bouge pas : la personne est payée sans venir. Une reprise
partielle — « 1,5 rhs, arrivée à 08h30' » — ne retire rien à la journée, qui
vaut ses huit heures. **L'argent n'est pas perdu, il est décalé.**

Ce qui a été retiré, c'est donc le paiement **au mois de la prestation**, au
taux majoré — 150 % en semaine, 187,5 % le samedi, 200 % le dimanche. Il
portait **775 heures sur 205 journées**, déduites pour la plupart d'une plage
plus longue que la journée contractuelle (une nuit de 12 h donne 4 h), et il
faisait payer ces heures **deux fois** : une fois à la prestation, une fois à
la reprise.

**La prime d'équipe, elle, reste due**, et c'est la moitié qu'il ne faut pas
emporter avec l'autre : une heure récupérée rend l'heure, pas la prime de la
pause où elle a été prestée. `hsAutoPoste` continue donc d'être alimenté.

**Le champ manuel « Heures suppl. non compensées » reste payé**, et c'est
désormais le SEUL endroit où l'on déclare des heures réellement payées au
lieu d'être récupérées. C'est une saisie volontaire, pas une déduction de
l'horaire.

Vérifié au navigateur sur deux mois de GPS : juillet perd sa ligne payée et
garde sa prime de nuit, septembre perd ses deux lignes payées et garde ses
deux primes d'équipe. Les heures se lisent sous « versées au compteur HS,
non payées ce mois-ci ».

## À établir

Ces points touchent à des montants et attendent une réponse du client — ne
pas les deviner :

- **Les intérimaires** : fiche d'un ouvrier, primes et jours de paie ne se
  calculent pas comme pour les autres. Rien n'est connu de ces trois règles
  — voir la section « Les intérimaires » ci-dessus.

- `R` (237), `D-F` (49), `VM` (40), `DS-CE` (27), `D-CPPT` (47) : journée
  prestée normale, absence payée, ou absence non payée ? Certains relèvent
  peut-être de la règle « horaire de jour, prime de pause conservée »
  (`conversion-horaire.md`, section 6 bis).

- L'horaire pendant l'arrêt technique. Le client : « pendant le SD, l'horaire
  est un peu spécial pour ceux qui s'occupent de la préparation ; ils doivent
  toujours prester 8 h mais arrivent et partent quand leur présence est
  nécessaire ». L'horaire écrit y est donc nominal, et les heures d'arrivée
  citées en commentaire ne permettent pas d'en déduire la durée.
- `?SD26|8H +FT` : journée d'arrêt technique tombant sur un repos — les huit
  heures sont-elles payées **et** épargnées, ou seulement épargnées ?
- Une journée de 12 h portant aussi une absence partielle vaut-elle 10 h
  prestées (ce que fait le calcul) ou 12 h ?

- **La maladie au-delà du premier mois.** Le client, le 25/09/2026 :
  « apparemment la règle des maladies c'est la société qui paye pendant
  1 mois avant que la personne tombe sur la mutuelle ». Le mot
  « apparemment » est le sien : la règle n'est pas confirmée.

  **Ce que le calcul fait aujourd'hui** : les heures `SMG` sont payées
  comme des heures prestées, **sans limite de durée** — « heures d'absence
  assimilées à du travail », ligne « Heure(s) SMG maladie ».

  **Ce que cela vaut en pratique** : sept séries de l'horaire 2026 dépassent
  trente jours, chez six personnes, dont une de **284 jours** et une de
  **258**. Au-delà du premier mois, la fiche simulée de ces personnes
  paierait des journées que la mutuelle prend en charge.

  **Mais rien ne le prouve sur une fiche en main.** Les quatre séries de
  maladie de VBN en 2026 font 8, 8, 1 et 1 journées : aucune n'atteint le
  mois, et les fiches CONFIRMENT la lecture actuelle à l'heure près pour ces
  durées-là (mai : 48,00 h sur la fiche = 6 journées, à l'heure près). Le
  contrôle contre les fiches ne peut donc rien dire de la règle du mois.

  Quatre choses manquent pour la coder, et chacune change le résultat :

  1. **un mois = 30 jours CALENDRIER** depuis le premier jour d'incapacité,
     ou le mois civil ? (le droit belge du salaire garanti compte en jours
     calendrier, mais c'est le fait de la maison qui tranche, pas le texte) ;
  2. **passé ce délai, la fiche porte-t-elle zéro heure de maladie** — la
     mutuelle payant à côté, hors fiche — ou une ligne d'un autre genre ?
  3. **une reprise remet-elle le compteur à zéro ?** Une rechute rapprochée
     compte souvent dans la même période, et sept séries de l'horaire sont
     entrecoupées ;
  4. **cela vaut-il pour les employés seulement** (CP 220) ou aussi pour les
     ouvriers et les intérimaires, dont les règles sont déjà inconnues ?

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

## Employé ou ouvrier : 8 % d'ONSS

Le client, le 22/09/2026 : « tous les contremaîtres et adjoints sont employés,
il y a juste SBZ / GKT / FLN / FPS / PLZ qui le sont aussi en dehors des
contremaîtres-adjoints. Le reste des opérateurs sont ouvriers et quelques-uns
intérimaires. »

**Ce n'est pas une étiquette.** L'ONSS d'un ouvrier se calcule sur **108 %**
du brut, celle d'un employé sur 100 % — c'est le `majOuvrier` de `DEF_B`, et
l'application savait déjà le faire. Mais le champ `statut` restait sur
« Employé » par défaut : **tout opérateur qui s'en servait payait 8 % d'ONSS
en moins que la réalité**, sans que rien ne le dise. Sur un brut de 3 000 €,
cela fait 31 € par mois d'écart sur le net affiché.

Le statut suit donc la personne. `statutPersonne()` le déduit :

- catégorie « Contremaîtres de production » — contremaîtres ET adjoints → **employé** ;
- `EMPLOYES_HORS_CADRE = ["SBZ","GKT","FLN","FPS","PLZ"]` → **employé** ;
- tous les autres → **ouvrier**.

**16 employés, 61 ouvriers** sur les 77 du classeur.

Choisir son identité dans le pré-remplissage pose le statut — choisir, c'est
le dire. Le champ reste modifiable à la main : il est marqué `personal:true`,
et l'application ne le reprend pas au démarrage.

Les **intérimaires** ne sont pas distingués : leur ONSS se calcule comme
celle d'un ouvrier, et le classeur ne dit pas qui ils sont.

**`SBZ` est confirmé** par le client le 22/09/2026 — il avait écrit `SBS`,
qui n'existe pas dans le classeur. Le rapprochement tenait à deux fils : une
lettre d'écart, et le rôle « polyvalent arrière » de la ligne 9 qu'il partage
avec FLN et FPS, les trois seuls de l'usine.

### Ce qu'une fiche d'ouvrier permettra de vérifier

Le client, le 22/09/2026 : « je vais essayer d'avoir des fiches de paie
ouvrier. » Toutes les règles de ce document ont été établies sur des fiches
d'**employé** — les siennes. Une fiche d'ouvrier mettra à l'épreuve, pour la
première fois :

- **l'ONSS sur 108 %** — jamais confrontée à une vraie fiche, seulement au
  barème ;
- **le pécule de vacances**, qui chez l'ouvrier vient de la caisse de
  vacances et non de l'employeur : il ne figure donc pas sur la fiche comme
  chez l'employé ;
- **le treizième mois** et ses dates, encore inconnues pour les ouvriers ;
- les libellés eux-mêmes : `comparer-fiches.py` lit « Heure(s) prestée(s) »,
  « Jour(s) presté(s) » et « Suppl.Equipe ». Ils viennent du même secrétariat
  social, ils devraient tenir — mais cela se vérifiera plutôt que se
  supposera.

L'outil fonctionne déjà tel quel sur n'importe quel trigramme :

```bash
python3 tools/comparer-fiches.py DKS /chemin/vers/fiches/*.pdf
```

**Les fiches ne rentrent JAMAIS dans le dépôt**, celles des autres moins
encore que les siennes.

### Reste ouvert

1. **Les dates du pécule et du treizième mois chez les ouvriers.** Le client,
   plus tôt : « en tout cas chez les employés, les ouvriers ce sont d'autres
   dates ». Chez les employés, pécule en mai et treizième mois en juin. Chez
   les ouvriers, le pécule vient de la caisse de vacances et non de
   l'employeur — il ne figure donc pas sur la fiche de la même façon. Reste
   à établir.

## Une formation se fait dans les heures de travail

Le client, le 22/09/2026 : « cette formation sera dans leurs heures de
travail, ou si pas le cas ils remettront une feuille pour ft+ ou hs ».

Une journée annotée `F` est donc une **journée de travail ordinaire** :
heures normales de la pause, prime de pause, aucun code d'absence. Un
dépassement ne se devine pas — il fait l'objet d'une feuille séparée, et il
reparaît dans la cellule sous forme de `+FT` ou de `HS`.

**C'est déjà ce que l'application fait**, vérifié sur les journées du projet
falling film : `FPS 05/10 ["AM","F",…]` → poste AM, 8 h, aucune absence. Rien
à corriger côté paie ; la règle est notée pour qu'on ne la remette pas en
question.

Ne pas confondre avec les codes d'absence `FORM` de la table `ABS`, qui
eux ne sont pas prestés : `F` en annotation est du travail, `FORM` en
absence n'en est pas.

## Une hausse ne réécrit pas le passé

La rémunération fixe et la prime de remise de pause vivent dans les
paramètres, donc dans UNE valeur — et la changer recalculait toute l'année.
Le client, le 22/09/2026 : « attention que ce sera à partir du mois prochain,
pas avant », puis, précisant, « à partir de la fiche reçue début octobre pour
la paye de septembre ».

C'est donc **septembre** le premier mois concerné : la fiche reçue début
octobre porte la période de septembre. Il aurait fallu recopier l'ancienne
valeur sur huit mois à la main.

`figerPasse()` s'en charge. Quand `remFixe` ou `primeRemise` change dans les
réglages, **l'ancienne valeur est écrite sur chaque mois déjà ÉCOULÉ** qui
n'en portait pas encore — dans `remFixeMois` et `primeRemiseMois`, les champs
du mois qui existaient déjà pour cela.

Trois précautions :

- **Un mois déjà écoulé** veut dire strictement avant le mois en cours. Le
  mois en cours prend la nouvelle valeur, ce qui est juste : une paie se
  règle en fin de mois.
- **Un mois qui porte déjà une valeur propre n'est pas touché** : c'est
  l'utilisateur qui l'y a mise, elle prime.
- **Un mois jamais ouvert n'est pas créé.** Lui écrire une valeur
  fabriquerait un enregistrement pour un mois que personne n'a touché.

La règle d'usage tient en une phrase : **changer le réglage le mois où il
prend effet**, et ne rien faire d'autre.

### La prime de remise de pause

Les trente minutes faites avant sa propre pause, pour relever celui qu'on
remplace. Le client, le 22/09/2026 : « ce n'est plus au cas par cas comme
quand j'étais adjoint, maintenant cette prime sera payée que je fasse 10
relevés ou 20 ». Elle est donc **fixe et mensuelle**, et vit dans les
paramètres — champ `primeRemise`, marqué `personal:true`.

C'est une rémunération ordinaire : elle entre dans le brut, ONSS et précompte
pleins. Elle n'est **pas** proratisée par la fraction, contrairement à la
rémunération fixe : c'est le montant tel qu'il figure sur la fiche qui se
saisit. À confirmer sur la première fiche qui la porte.

## Le rappel se compte depuis le jour PRESTÉ

Le classeur porte parfois le compteur sur une journée, et le travail sur une
autre : la ligne est un repos avec `4h +FT`, et le commentaire dit
« presté le 13.03 ». Le client, le 22/09/2026 : **« oui c'est bien ça le
jour presté »**.

La date du rappel se compare donc à **ce jour-là**, et non à la ligne qui
porte le compteur. Sept journées de l'année le disent ; six changeaient de
coefficient :

| | Depuis la ligne | Depuis le jour presté |
|---|---|---|
| quatre journées | **aucun rappel** | coefficient 2 ou 1,5 |
| deux journées | coefficient 1,5 | **coefficient 2** |
| une journée | coefficient 2 | coefficient 2 (inchangé) |

Mesurées depuis le jour presté, les sept tombent **dans** le barème ; depuis
la ligne, six en sortaient — une demande postérieure à la journée est
refusée, et elle l'était à tort.

`RX_PRESTE_AILLEURS` reste **séparée** de `RX_PRIS_AILLEURS`, qui dit
pourtant presque la même chose. « Pris le » désigne des heures **consommées**
ailleurs, dont l'annotation est écartée pour ne pas les compter deux fois ;
« presté le » désigne des heures **gagnées** ailleurs, que le compteur de la
ligne enregistre bel et bien. Les confondre déplacerait 52 journées de flex
time — le nombre de journées qui écrivent « presté le » sans que l'ancien
motif les voie.

Le classeur écrit aussi la date en tête du commentaire, suivie de deux
points. Ce motif-là est délibérément étroit — ancré au début et exigeant le
« : » — sans quoi n'importe quelle date y passerait.
