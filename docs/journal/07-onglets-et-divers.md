# Personne par défaut, versements, onglets, intérimaires, valeurs communes

Historique déplacé tel quel de `CLAUDE.md` le 18/10/2026. Les dates, mesures et erreurs y restent.

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
icone("icon-maskable-512.png", 512, 0.14)
```

La marge de 10 % de la dernière n'est pas cosmétique : Android rogne l'icône
*maskable* dans un masque, et seuls les 80 % centraux sont garantis visibles.
Sans elle, le mot « biowanze » se ferait couper.

**Nouveau logo (22/10/2026, `nfdm-v988`).** Le client a déposé sur GitHub
le logo « biowanze.app » : le « ce » en dégradé vert-bleu, le mot dessous,
sur fond marine `#182032`, en 1254 × 1254 px. Il devient `logo.png`, et les
cinq icônes sont régénérées par le code ci-dessus. La marge de l'icône
*maskable* passe de 10 à **14 %** : le mot « biowanze.app » est plus large
que l'ancien. Mesuré : aucun pixel du dessin hors du cercle central de
80 %.

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


## Les nouveaux opérateurs d'office dans les tableaux (20/10/2026)

Le client : « supprimer l'explication dans le bas des recyclages, ajouter
les nouveaux opérateurs automatiquement dans les tableaux de statut et de
formation (DCI, LCO etc.) ». La ligne « Chaque case : jours relevés par
l'app / recyclages enregistrés par les RH… » est retirée ; reste « Se
termine : … » quand une polyvalence finit. Mesuré : les arrivées de 2026
(CDT, MGY, NPI, SLI) étaient déjà dans les deux tableaux — le classeur les
écrit « Opérateurs en formation ». Manquaient qui n'est que dans le
classeur d'une année suivante (DCI, 2027 seulement : ni statut ni
formation, les tableaux ne lisant que l'année en cours) et une arrivée
rangée d'emblée dans une équipe. `gensAVenir()` ajoute les premiers,
marqués de leur année ; `nouvelOperateur()` (pas cadre ; sans ligne dans
« Polyvalence » ou venu d'une année suivante) les met au tableau de
formation. Éprouvé : DCI « Chaud. · Équipe 4 · dès 2027 » en formation,
« Ouvr. » au statut ; 10 opérateurs en formation au lieu de 9. **C'était
faux pour DCI**, le client aussitôt : « DCI n'est pas en formation
chaudière, il est validé et seul poste connu. C'est LCO le nouveau aux
chaudières ». Venir d'une année suivante ne fait pas un apprenti : seul
un opérateur SANS ligne dans « Polyvalence » (aucun poste validé) entre
d'office au tableau de formation ; DCI reste au statut seulement
(`nfdm-v857`, 9 opérateurs en formation). LCO n'est
dans aucun classeur — un seul commentaire le nomme, le 26/10 (« Visite du
site avec LCO (intérimaire chaudières) ») : il viendra avec sa colonne.
L'effectif n'en dépend pas (vérificateur et polyvalence identiques).
