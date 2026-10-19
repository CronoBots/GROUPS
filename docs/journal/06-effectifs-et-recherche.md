# Congé, absence, recherche, sous-effectifs, classeurs reçus

Historique déplacé tel quel de `CLAUDE.md` le 18/10/2026. Les dates, mesures et erreurs y restent.

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

**Le héros, le 16/10/2026** (le client, capture de l'iPhone : « le héros
doit mieux présenter la personne connectée, le bouton setting ne doit pas
avoir la lumière blanche autour ; ce matin je faisais AM mais en me
connectant à 05h il était marqué que je travaillais demain »). Trois
choses :

- **l'identité en trois lignes** : le trigramme et le statut en pastille
  (jaune pour un intérimaire), la fonction en clair (le poste attitré d'un
  opérateur), puis le rangement : « Binôme 5 · avec ATR » pour un cadre
  (`_pfPartenaire()`, l'autre cadre du même numéro de binôme), l'équipe
  pour un opérateur, « En formation · Meunerie » en jaune ;
- **la roue sans halo** : plus de cercle blanc ni de lueur cyan derrière
  elle, l'icône seule ;
- **le poste du moment se calcule sur l'HEURE**. Avant 6 h, le jour de
  l'usine est encore la veille (`jourUsine()`), et le matin du jour, qui
  commence à 5 h 30 pour le contremaître de la pause, se lisait « Demain ».
  `_pfInfos()` compte désormais les heures depuis minuit du jour de chaque
  poste, et les mots suivent le calendrier (`kc`) : à 3 h et à 5 h,
  « Aujourd'hui · Début à 5 h 30 » ; à 5 h 45, « En poste · Fin à 14 h » ;
  « Auj. » de la semaine est le jour du calendrier. Vérifié horloge au
  16/10 sur VBN (3 h, 5 h, 5 h 45, 16 h), SKS, GJR, JBI et SLI, à 320 px
  (hors ligne), 390 et 1280 px ; vérificateur et agendas identiques.

**Puis en profil de réseau social** (le client, le même jour : « c'est
possible de présenter cela comme un style de présentation de réseau
social ? »). `_pfHead()` pose une couverture à la couleur de la marque, avec
le logo à droite à côté de la roue, et un avatar rond au trigramme, cerclé
de cyan et à cheval sur elle. Dessous : le trigramme et son statut, la
fonction (« bio ») et, en jaune, la formation. Puis une rangée de chiffres
comme sous un profil : binôme et partenaire (Adjoint ou Contremaître) pour
un cadre, l'équipe pour un opérateur, les polyvalences validées (pas pour un
contremaître, celles qui se terminent sont retirées par `polyFinie()`), et
le prochain week-end libre (« 17 oct. », toujours affiché). Celui-ci
quitte le pied du héros. Rien de neuf n'est calculé. **Première version
fausse sur deux points** : le logo, en haut à gauche, passait sous
l'avatar, et l'identité chevauchait la couverture à 320 px. Elle commence
désormais sous la couverture. Vérifié sur VBN, SKS, GJR, JBI et SLI à
320 px (hors ligne), 390 et 1280 px, sans débordement ni erreur.
Puis, le même jour (le client : « le trigramme dans le cercle est top ! il
faut le poste puis le statut à la place du VBN en dehors du cercle, pas
besoin de badge pour le statut ») : à côté de l'avatar, le poste en grand
(« Contremaître », « Chaudières »), puis le statut en clair, sans pastille
(jaune pour un intérimaire) ; le trigramme ne s'écrit plus qu'une fois, dans
le cercle. Vérifié sur les mêmes cinq personnes, aux mêmes largeurs.
Puis une vraie bannière (le client, le même jour : « peut-être avec une
bannière dans toute la zone où il y a le logo ? »). La couverture passe de
74 à 112 px (100 sous 380 px, 132 au bureau). La marque du logo, sans le
mot, y est dessinée en grand, à droite, et déborde du cadre (`PF_MARQUE`,
le tracé de `logo.svg`, en SVG dans la page : rien à mettre en cache).
Le logo entier passe en haut à gauche, au-dessus de l'avatar ; la roue
reste en haut à droite. Aucune donnée ne change. Vérifié sur VBN (à 3 h,
5 h, 5 h 45, 16 h), SKS, GJR, JBI et SLI, à 320 px (hors ligne), 390 et
1280 px : rien ne déborde, aucune erreur.
Puis le héros et le calendrier en un seul cadre (le client, le même jour :
« comment combiner le héros avec le cadre calendrier en dessous ? il ne
faut pas de redondance et il faut que cela soit 100 % pro »). **La bande
des sept jours est retirée** : le calendrier du mois, juste dessous, montre
les mêmes journées. Le calendrier se soude sous le héros : les coins se
touchent sans arrondi, un seul filet sépare les deux, et il ne reste qu'une
ombre. Les cartes de mise à jour d'horaire et d'installation passent
au-dessus du héros. La carte « Mise à jour de votre horaire » montre
désormais tous les changements, puisque les cercles de la semaine ont
disparu avec elle ; la ligne des changements de poste proposés par
l'application reste sous le prochain poste. Neuf règles à zéro (aucune
lecture touchée) ; vérifié sur VBN (3 h, 5 h, 5 h 45, 16 h), SKS, GJR, JBI
et SLI à 320 px (hors ligne), 390 et 1280 px, sans débordement ni erreur.

**Puis la bannière du client** (le même jour : « j'ai déposé la bannière
dans le git »). Il a poussé deux versions de la même image, l'usine vue du
ciel à gauche et la marque avec son nom à droite :
`banniere-biowanze-usine.png` (2170 × 540, 2,7 Mo) et une copie `.jfif`
plus petite. L'application emploie `banniere.jpg`, tirée du PNG à 1600 px
de large (134 Ko), dans `CORE` du service worker pour le hors ligne ; les
deux originaux restent tels quels et ne sont pas chargés. Elle remplace le
dégradé, la marque dessinée (`PF_MARQUE`, retirée) et le petit logo de la
couverture : la bannière porte déjà la marque. Sur téléphone la couverture
garde les proportions de l'image (2170/540), rien n'est rogné. Au bureau
elle fait 240 px de haut, calée en bas à droite, pour que la marque et
« biowanze » restent entiers. **Un `max-height` avait d'abord été essayé** :
avec `aspect-ratio`, il rétrécit aussi la LARGEUR, et la bannière laissait
un vide à droite. La roue passe en haut à GAUCHE, sur l'usine, dans un
disque sombre translucide : à droite elle couvrait la marque. Vérifié sur
VBN (3 h, 5 h, 5 h 45, 16 h), SKS, GJR, JBI et SLI à 320 px (hors ligne),
390 et 1280 px, sans débordement ni erreur.

**Le cadre du mois réorganisé** (le client, le même jour, capture à
l'appui : « je ne suis pas satisfait de la partie calendrier ; réorganise
tout 100 % pro »). Dans l'ordre : la barre du mois, **le calendrier tout
de suite dessous** (il venait après sept tuiles de chiffres), la légende,
puis le **bilan du mois** (« Bilan d'août »). Un repos n'est plus une case
pleine : sans bordure ni fond, le numéro pâle (classe `repos`), si bien
que les journées prestées ressortent seules. Le samedi et le dimanche ont
leur en-tête un peu plus marqué ; le jour courant porte son numéro en
pastille d'accent ; la colonne des heures de la semaine est séparée d'un
filet. Le bilan a quatre chiffres fixes sur une rangée (prestées, jours,
week-end, heures sup, avec l'écart au mois d'avant) ; les rappels (et leur
montant, « 1 · (montant retiré) € »), le flex du mois et le vélo passent sur une
ligne dessous et **ne s'écrivent que s'ils ne valent pas zéro** — « 0
vélo » et « 0 rappel » n'apprenaient rien. Aucun calcul touché.
Vérifié sur VBN en octobre et en août à 320 px (hors ligne), 390 et
1280 px, sans débordement ni erreur.

**La feuille du jour montre la reprise partielle** (le client, le même
jour, capture de VBN le 14/10, `["7h-15h","2h RHS","Départ à 13h"]` :
« dans les sélections, les 2h HS doivent être sélectionnées pour
comprendre »). La liste des congés disait « — » : une reprise partielle
vit dans `rec.rh`, et un congé lu dans le commentaire dans `rec.ax`, pas
dans `rec.a`. `jourCongesLus()` les rassemble, et la feuille les met en
tête de la liste, choisis (« 2H RHS », ou « 4H RTT + 2H RHS » avec un
code posé). Choisir autre chose les remplace (`rec.rh` et les congés de
`rec.ax` partent ; les heures sup d'un rappel restent). Aucun calcul
touché. Vérifié à 320 px (hors ligne), 390 et 1280 px.

**Tout l'Accueil réorganisé** (le client, le même jour : « optimise et
réorganise TOUT le contenu de l'accueil … j'aime bcp la première partie avec
la bannière, trigramme et poste »). Le héros ne bouge pas. Dessous : le mois
avec son bilan, puis **un seul cadre « Mon année » à deux onglets, Compteurs
et Rythme** (`#anCard`, `data-o`, onglet retenu dans `ui/accOnglet`). Les deux
cartes empilées faisaient 2 900 px. Toucher les congés restants du héros
ouvre l'onglet Compteurs. Les redites sont retirées :
- « Jours prestés par mois » (la barre empilée des pauses a la même
  hauteur), avec `ryBars()` ;
- la case « Solde » du flex time (la ligne au-dessus le dit) ;
- « Concorde avec le pied du classeur », qui ne parle plus que s'il y a un
  écart.

**Les onglets n'ont vécu qu'une version.** Le client, capture de la
comparaison à la moyenne à l'appui : « toute cette partie-là est inutile, et
le rythme, le nombre de nuits et le graphique peuvent être visibles sans
devoir passer par un bouton ». Ont été retirés la comparaison à la moyenne
(`ryCompareHTML()`, `statsEquipe()` et son cache, qui calculait `statsRythme()`
pour tout le monde au repos) ainsi que les trois chiffres (heures estimées,
jours de travail et de repos d'affilée). Les onglets sont partis aussi :
« Mon rythme » puis « Mes compteurs » s'affichent chacun à découvert, dans
deux cadres. À 390 px, l'Accueil de VBN fait environ 3 200 px.

**« Mon année » monte dans le héros** (le client, le même jour : « prochain
congé inutile aussi, mais mon année avec la ligne de progression et les
stats de pauses sont intéressantes près du héros »). `ryAnneeHTML()` remplit
`#ryAn`, placé au pied du héros sous les congés restants. On y lit la barre
des journées prestées et à venir, puis AM, PM, N et D, faites et à venir. Le
prochain congé est retiré, avec `estCongePose()`. « Mon rythme » ne garde que
la répartition, les pauses par mois et l'année jour par jour.

**Les congés en tuiles** (le client, le même jour : « il n'y a pas une façon
plus professionnelle d'afficher les compteurs sur l'Accueil ? »). « Congés
restants » devient une grille de tuiles, deux de front sur téléphone et
quatre au bureau. Chaque tuile porte le code et son intitulé, le restant en
jours de 8 h en grand avec les heures à côté, une barre fine « placé sur
disponible », puis « 56 / 68 h placées ». La tuile se borde de rouge quand le
restant est négatif. Ce sont les jours du héros, avec leur détail. Sous
380 px, l'intitulé passe sous le code : à côté, « Congé d'ancienneté » se
coupait. Aucun calcul touché, neuf règles à zéro. Vérifié sur VBN et SKS à
320 px (hors ligne), 390 et 1280 px.

**Puis la passe complète** (le même jour, voir « Méthode de travail »).
Le donut de « Mon rythme » et ses pourcentages redisaient les cases AM ·
PM · N · D de « Mon année » : ils sont retirés, avec `ryDonut()`.
« Pauses par mois » gagne une légende de couleurs et 96 px de haut, et le
sous-titre ne promet plus des week-ends qu'il ne montre pas. Le flex time
ne laisse plus de bande vide sous ses chiffres. « Mes compteurs », ce qui
se décide, passe avant « Mon rythme », ce qui se constate. À 390 px,
l'Accueil de VBN fait 2 985 px. Neuf règles à zéro ; vérifié sur VBN et SKS
à 320 px (hors ligne), 390 et 1280 px.

**Et la seconde passe complète** (le client, le même jour : « réorganise
tout l'accueil à fond pro 100 % »). Relevé sur captures à 320, 390 et
1280 px, puis corrigé en une fois :
- le flex time et la récup. HS deviennent deux tuiles « Heures », du même
  dessin que les congés : le solde en grand avec son état en couleur et en
  mots, la jauge −8 / 80 / 104 (le « 0 » s'y chevauchait avec « −8 », il
  est retiré dans la tuile), portées et reprises de l'année. La bande
  `.calstats` du flex time, `.ft-ligne` et `cst()` sont retirés ;
- la légende du mois tient en deux lignes au lieu de trois, avec des mots
  courts (« Congé ou maladie », « Prime conservée », « Rappel ») ;
- l'agenda quitte le cadre du mois pour un cadre à lui, « Agenda du
  téléphone », avant les codes : c'est un réglage qu'on fait une fois, pas
  une lecture du mois. Il se cache avec le héros quand personne n'est
  connecté.

L'ordre est désormais : héros, mois, compteurs, rythme, agenda, codes. À
390 px, l'Accueil de VBN fait 2 930 px. Neuf règles à zéro ; vérifié sur VBN
et SKS à 320 px (hors ligne), 390 et 1280 px, et sans personne connectée.

Chaque congé tient sur une rangée : code, intitulé, barre, « Placé · disponible »,
et le restant en grand à droite. Les trois chiffres demandés le 09/10 sont
gardés. Les deux boutons d'agenda passent sur une ligne (« Partager »). Mesuré
à 390 px : **4 200 → 2 550 px** pour VBN. Aucun calcul touché, neuf règles à
zéro. **Une ligne CSS orpheline**, restée du nettoyage des anciennes règles
`.cg-nb` (une règle sur deux lignes dont seule la première était retirée),
a d'abord annulé la règle qui la suivait : un compteur d'accolades ne la voit
pas, la capture si. Vérifié sur VBN et SKS à 320 px (hors ligne), 390 et
1280 px, sans débordement ni erreur.

**« Mes compteurs », une seule forme de rangée** (le client, le
18/10/2026, capture de l'iPhone : « il y a moyen d'optimiser bien mieux
cela pour être intuitif, propre et professionnel »). Défauts relevés à 320,
390 et 1280 px :
- quatre tuiles de congés de même taille, même vides (« 0 j ») ;
- des chiffres en chasse fixe (« 2,5 j » se lisait « 2 , 5  j ») ;
- des badges encadrés à chaque ligne ;
- un texte d'excuse dans la tuile RHS (« Le solde n'est pas dans le
  classeur ») ;
- une jauge flex time au gros rond blanc ;
- des sous-titres longs ;
- des tuiles en haut et des rangées en bas, deux styles ;
- le lien « Mon recyclage » en grande police (raccourci `font` invalide).

Tout compteur est désormais une rangée (`.cr`) : le code en petites
capitales d'accent et le nom à gauche, le détail dessous, la valeur en
grand à droite, dans la police du texte avec des chiffres alignés. Les
congés commencent par **le total à placer** (« 5,5 j à placer · 44 h »).
Chaque congé montre « placé sur disponible », sa barre et son restant ; un
congé tout placé tient sur une ligne pâle, « Tout placé », en fin de liste.
Les restants négatifs s'écrivent avec un vrai signe moins. Le flex time
a son état en pastille et une jauge fine dont le point prend la couleur de
l'état, avec des repères −8 h, 80 h et 104 h. La RHS dit « reprises en
2026 », et le solde absent passe dans l'infobulle. Le temps réduit et la
maladie prennent la même rangée. Au bureau, deux colonnes. Aucun calcul
touché : le vérificateur est identique à l'octet. Vérifié sur VBN, LCI,
ATA et SMA à 320 px (hors ligne), 390 et 1280 px, sans débordement ni
erreur.

**Tous les congés dans une seule liste** (le client, le 18/10/2026 : « il
faut regrouper les types de congé ensemble et les présenter de la même
manière »). Les blocs « Congés restants », « Heures » et « Temps de
travail réduit » deviennent un seul bloc, « Congés ». Il commence par le
total à placer, puis une rangée par type, dans un ordre fixe : VA, RTT,
DTT, RJF, FT, RHS, puis CP, TP et CT. Chaque rangée a la même forme
(`rangee()`) : le code et le nom, une ligne de détail, la valeur en grand
à droite et, dessous, ce qu'elle mesure (« 12 h restantes », « solde »,
« reprises », « à planifier »). Un congé tout placé tient sur une ligne
pâle, à sa place dans l'ordre. Les périodes d'un même code de temps
réduit s'additionnent sur une seule rangée (« 26 j posés en 2 périodes
(5 + 21) »), et « À planifier » devient sa valeur. Au bureau, la liste
coule sur deux colonnes de journal (`columns:2`), sans les trous d'une
grille. La maladie garde son bloc : ce n'est pas un congé. Vérificateur
identique à l'octet ; vérifié sur VBN, LCI, ATA et SMA à 320 px (hors
ligne), 390 et 1280 px.

**« 100 % ? »** (le client, le 18/10/2026, capture du cadre regroupé). Non :
deux défauts dans le cadre. La rangée RHS de VBN écrivait « en 2026 », ce
qui ne disait rien : elle dit désormais « en reprises partielles », « en
journées entières » ou « aucune reprise cette année ». Un congé parental ou
un temps partiel sans rien à planifier affichait « 0 j à planifier » en
grand : il s'écrit « Tout planifié », en petit, comme « Tout placé ». Le
troisième défaut est hors du cadre : le bouton de retour en haut passe sur
la dernière valeur à droite quand on descend (il apparaît après 300 px).
Vérificateur identique à l'octet ; vérifié sur VBN, LCI, ATA et SMA à
320 px (hors ligne), 390 et 1280 px.

**« Super intuitif et propre »** (le client, le 18/10/2026, juste après).
Chaque rangée se lit maintenant comme une phrase : le NOM d'abord, le code
en petite étiquette après lui (la colonne de codes laissait un grand vide
entre « VA » et « Vacances annuelles ») ; à droite, ce qu'il reste à faire.
Un congé tout placé tient sur une ligne, « ✓ Tout placé » en vert, sans
détail ni barre. Le restant s'écrit « 12 h à placer » (« de trop » sous
zéro). Le flex time perd sa pastille : son état passe sous la valeur, en
couleur (« Dans les bornes », « À redescendre », « Au-delà de 104 h »,
« Sous −8 h »), la date du solde dans l'infobulle. La RHS dit « repris en
2026 », le temps réduit « 26 j posés en 2 périodes », sans la liste. Le
total s'écrit « 1,5 jours à placer, soit 12 h », sous un filet ; « soldes
2025 inclus » passe en infobulle, « jours de 8 h » devient « 1 jour = 8 h ».
Vérificateur identique à l'octet ; vérifié sur VBN, LCI, ATA et SMA à
320 px (hors ligne), 390 et 1280 px, rien ne déborde.

**Le code d'abord, et « restant »** (le client, le 18/10/2026 : « le nom
raccourci du congé doit être affiché en premier (VA RHS RTT…) ; au lieu de
« à placer » il faut mettre restant »). L'étiquette du code passe devant le
nom, à largeur fixe (44 px) pour que les noms s'alignent ; à 320 px, un nom
long passe sur deux lignes à côté d'elle, sans descendre sous le code. Le
total dit « 1,5 jours restants, soit 12 h », chaque congé « 12 h
restantes ». Vérificateur identique à l'octet ; vérifié sur VBN, LCI, ATA
et SMA à 320 px (hors ligne), 390 et 1280 px.

**Passe complète de l'Accueil** (le client, le 18/10/2026 : « Optimisation
acceuil ? »). Photographié à 320 px (hors ligne), 390 et 1280 px sur VBN, LCI
et SKS. Défauts relevés et corrigés :
- au bureau, dans « Mes compteurs », la seconde colonne commençait par un
  filet et pas la première (Formation sous un trait, Maladie sans) : chaque
  colonne commence désormais par le sien ;
- le détail d'une rangée (« 56 h placées sur 68 h ») commençait sous
  l'étiquette du code, et non sous le nom : il s'aligne sous le nom, sauf
  sous 380 px où il reprend la largeur ; un chiffre et son unité ne se
  séparent plus (« −55 / h » à 320 px) ;
- dans la frise du cycle, la case du jour débordait de la frise (anneau
  extérieur) : l'anneau est intérieur ;
- le pourcentage de « Mon année » était en chasse fixe (« 75 % » espacé) :
  police du texte.
Reste, et pourquoi : le bouton de retour en haut passe sur la valeur de
droite d'une rangée quand on descend (il s'efface en haut de page, à 55 %
d'opacité) ; les déplacer tous deux serait un autre chantier. Aucun calcul
touché : vérificateur identique à l'octet.

**La feuille d'une journée lue, en clair** (le client, le 18/10/2026,
capture de la feuille du 01/10 : « pro ? »). Non : depuis que le classeur
l'emporte, la journée s'affichait comme un formulaire grisé (boutons de
pause éteints, menu « — », champ « 8 », « Rappel aucun » en chasse fixe, et
une aide « Comment lire cette ligne » qui décrivait des commandes
inutilisables). `jourLuHTML()` remplace ce formulaire pour toute journée du
classeur : la pause en pastille à la couleur du calendrier (contour pour un
congé, rouge pour la maladie), son nom, l'horaire de l'agenda
(`_pfJour()`, `pfHeures()`, remise de 30 min comprise) et les heures
payées ; puis, seulement s'il y a lieu, « Prévu au cycle » quand la cellule
franche dit une autre pause, la prime conservée, le congé posé, la prime de
rappel en mots et le rappel sur un repos. Le vélo, seul réglage restant,
devient un interrupteur, et ne s'affiche que les jours prestés. La ligne du
classeur s'intitule « Classeur », le commentaire en citation ; l'aide se
cache pour une journée lue. Les journées hors classeur gardent le
formulaire. Vérificateur identique à l'octet ; vérifié sur VBN (01, 02, 03,
09, 15/10) et YBT (maladie) à 320 px (hors ligne), 390 et 1280 px, rien ne
déborde, l'interrupteur vélo s'enregistre.

**Glisser d'un jour à l'autre sur la feuille** (le client, le 18/10/2026 :
« il faut pouvoir swiper gauche/droite sur ces fiches »). Le même geste
franc que le Planning et les mois (60 px, 1,8 fois plus large que haut,
moins de 0,7 s) : vers la gauche le jour suivant, vers la droite le
précédent, et le contenu arrive du côté où l'on va (`jourBouge()`). Les
flèches ‹ › et celles du clavier font de même, et toutes passent désormais
d'un mois à l'autre : la feuille du 1er octobre mène au 30 septembre (avant,
elles s'arrêtaient au bord du mois). Éprouvé au toucher simulé à 320 px
(hors ligne), 390 et 1280 px : 01/10 → 02/10 → 30/09, un glissement court ou
en biais ne change rien, rien ne déborde. Vérificateur identique à l'octet.

**Plus de flou derrière les fenêtres** (le client, le 18/10/2026 : « diminuer
le flou dans le haut de l'écran »). La feuille d'une journée et la fenêtre de
confirmation posaient un voile sombre ET un flou (`backdrop-filter:blur(2px)`)
sur la page restée visible au-dessus d'elles. Le flou est retiré, le voile
reste : la page dessous est nette et assombrie. Vérifié à 320 px (hors ligne),
390 et 1280 px, feuille du 01/10 ouverte ; vérificateur identique à l'octet.

**Les congés se voient, et la barre d'état reste opaque** (le client, le
18/10/2026, capture du mois : « les congés ne se voient pas fort, et
autres ? »). Un congé (CP, RJF, VA…) avait le contour en tirets et le code
gris d'un poste prévu non presté : la case la plus fréquente était la plus
pâle. Il prend une case teintée, un filet plein et son code dans une
pastille claire et neutre, qu'on ne confond ni avec une pause ni avec la
maladie ; le poste prévu non presté garde ses tirets, et sa légende devient
« AM non presté » (deux lignes de légende au lieu de trois à 390 px). Le
montant des rappels du bilan quitte la chasse fixe. **Et le flou du haut
n'était pas celui que j'avais retiré** : sur sa capture, c'est le contenu
qui défile sous l'heure et la batterie de l'iPhone, montré flou par iOS ; le
voile des fenêtres n'y était pour rien. Une bande à la couleur de la marque
(`html::after`, hauteur `env(safe-area-inset-top)`) couvre désormais cette
zone. Chromium n'a pas d'encoche (hauteur 0) : seul l'iPhone dira si le flou
a disparu. Vérificateur identique à l'octet ; vérifié à 320 px (hors ligne),
390 et 1280 px, rien ne déborde.

**Les badges du mois, un seul gabarit** (le client, le 18/10/2026, capture du
mois : « les badges de pauses doivent être mieux faits et de même taille,
plus discrets ? »). Chaque pastille prenait la largeur de son texte : N, D
et F en ronds, AM et PM en pilules, RJF plus large encore, et le congé en
pilule claire qui dominait le mois. Tous les codes (pauses et congés) ont
désormais la même boîte : un rectangle aux coins doux de 30 × 18 px (26 × 17
sous 360 px, 40 × 22 au bureau), texte de 10 px, un code long (CPPT) resserré
dans la même boîte. Le congé passe d'un fond clair plein à une teinte neutre
translucide avec un filet, la légende suit. Mesuré à 320 px (hors ligne), 390
et 1280 px : une seule taille de badge par largeur, aucun texte coupé, rien
ne déborde ; vérificateur identique à l'octet.

**Le poste prévu non presté ne s'affiche plus barré** (le client, le
18/10/2026 : « utile de mettre les pauses barrées ? », puis « 3 »). Au
calendrier du mois, une journée dont le classeur prévoyait une pause sans
qu'elle soit faite, ni congé écrit (VBN le 15/10, « 7h-15h · - · cf.
09/10 », un D déplacé), montrait le code barré dans une case en tirets.
Elle se lit désormais comme un repos ordinaire, et l'entrée « AM non
presté » quitte la légende. L'infobulle et la feuille du jour disent
toujours « prévu, non presté ». CSS seulement : la règle dure « poste prévu
effacé » du vérificateur porte sur la lecture, qui ne change pas, et ses
sorties sont identiques à l'octet. Vérifié à 320 px (hors ligne), 390 et
1280 px, rien ne déborde.

**Un coin pour le commentaire** (le client, le 18/10/2026, capture du mois :
« rien n'indique un commentaire pourtant il est encore dans la cellule »).
Depuis que le poste prévu non presté se lit comme un repos, rien ne disait
que la cellule du 15/10 de VBN (« 7h-15h · - · cf. 09/10 remplace ATA… »)
porte un commentaire. Toute journée dont la cellule du classeur a un
commentaire porte un petit triangle cyan dans son coin bas droit, comme le
coin rouge d'Excel (`comJour()`), et la légende dit « Commentaire » les mois
où il y en a. Un appui ouvre la feuille du jour, qui cite le commentaire.
La marque « AM non presté » est partie de `legendeMois()` avec sa variable.
Affichage seulement : vérificateur identique à l'octet ; vérifié à 320 px
(hors ligne), 390 et 1280 px, rien ne déborde.

Puis, le même jour (le client : « des fines bordures sur les pauses comme
sur les congés, et le commentaire avec le triangle rouge en haut à droite
comme Excel ») : chaque journée de pause a un filet de 1 px à la couleur de
sa pause, et son badge un liseré clair comme celui du congé ; le triangle
du commentaire passe en rouge dans le coin haut droit, et les points
(vélo, rappel, heures modifiées) en haut à gauche. Affichage seulement ;
vérificateur identique à l'octet ; vérifié à 320 px (hors ligne), 390 et
1280 px.

**Le vélo coché se perdait** (le client, le 18/10/2026 : « je suis venu en
vélo les 12, 13 et 14 et mes ajouts manuels sont toujours annulés »).
`save()` attend 700 ms avant d'écrire ; quitter l'application avant (sur
iPhone, balayer vers le haut juste après avoir coché) perdait la dernière
saisie. Reproduit au navigateur : trois vélos cochés, rechargement
immédiat, deux restaient. `viderEcritures()` écrit tout ce qui attend dès
que la page se cache ou se ferme (`visibilitychange`, `pagehide`,
`beforeunload`) : trois sur trois, rechargement immédiat ou non.
Vérificateur identique à l'octet.

**Quatrième passe complète de l'Accueil** (le client, le 18/10/2026 :
« optimise au max pro 100 % »). Photographié à 320 px (hors ligne), 390 et
1280 px sur VBN. Relevé et corrigé :
- le héros donnait « Week-end libre · 17 oct. » le dimanche 18 : un
  dimanche comptait comme le week-end en cours, déjà à moitié passé. Seul
  un samedi ouvre désormais un week-end (24 oct.), et « Ce week-end »
  s'écrit le samedi même ;
- « Maladie et autres absences » devient « Maladie et formation » : chez
  nous, absence veut dire maladie ;
- « Récup. Jour férié » (intitulé du classeur) s'écrit « Récup. jour
  férié » à l'écran (`libCompteur()`), comme « Récup. temps de travail » ;
- les pastilles de pause du héros et de « Mes pauses » quittent la chasse
  fixe pour la police des badges du calendrier ;
- le point vélo d'un jour D, vert sur vert, passe en blanc ;
- le bouton de retour en haut ne se montre plus qu'en REMONTANT, et
  s'efface 2,2 s après le geste : en permanence, il couvrait la valeur de
  droite des rangées des compteurs (l'écart connu depuis le 18/10).
Reste, et pourquoi : rien de vu à ces trois largeurs. Vérificateur
identique à l'octet ; rien ne déborde, aucune erreur.

**Plus de colonne des heures, et le week-end en bande** (le client, le
18/10/2026 : « pas besoin de la colonne avec nombre d'heures et il faut
différencier les 2 colonnes de wk »). La colonne « H » du calendrier du
mois (heures de chaque semaine) est retirée, avec ses styles : le bilan
du mois donne les heures. Samedi et dimanche se lisent sur une bande
claire arrondie (`.mc-we`), de l'en-tête à la dernière semaine, posée
derrière les cases dans `.mc-grille` (`--g`, l'écart entre colonnes, sert
à la caler). Affichage seulement ; vérificateur identique à l'octet ;
vérifié à 320 px (hors ligne), 390 et 1280 px.

Puis, le même jour, capture à l'appui : « je n'aime pas du tout les
colonnes de wk ». La bande est retirée. Le week-end se distingue case par
case : un samedi ou un dimanche sans prestation garde une tuile très
légère (`.mc-j.we`), là où un repos de semaine n'a rien, et SAM et DIM
s'écrivent en cyan ; les jours prestés gardent leur couleur. Le jour
courant garde sa pastille. Vérifié à 320 px (hors ligne), 390 et 1280 px.

Puis : « il faut mettre des bordures aux cellules sans rien aussi ».
Tout repos (et poste prévu non presté) a désormais un filet fin ; le
samedi et le dimanche gardent en plus leur tuile légère. Les cases avant
le 1er et après le dernier jour restent vides. Vérifié à 320 px (hors
ligne), 390 et 1280 px.

**Le texte des pauses en blanc partout** (le client, le 18/10/2026 :
« AM et PM sont en noir, il y a une raison ? »). Oui : sur l'orange
(#C68128) et le turquoise (#229B97) du thème sombre, le blanc ne tenait
qu'à 3,2 et 3,4:1, d'où une encre sombre. Les deux fonds s'assombrissent
d'un cran (#B5721F, #1E8C88) et toutes les pauses s'écrivent en blanc
(3,9 et 4,1:1, en gras). Les couleurs servent partout (calendrier,
Planning, graphiques) : la teinte ne change pas, seule la clarté baisse.
Vérificateur identique à l'octet ; vérifié à 320 px (hors ligne), 390 et
1280 px.

**Passe complète du Planning** (le client, le 18/10/2026 : « optimise aussi
le Planning 100 % pro »). Photographié à 320 px (hors ligne), 390 et
1280 px, le 18/10 (dimanche) et le 13/10 (relais de 12 h, horaires
modifiés). Relevé et corrigé :
- sur téléphone, un badge avec horaire (« ATA 8-14 », « QBY 10-22 »)
  passait à la ligne dans une case et pas dans l'autre, et prenait une
  forme à lui, plus large : l'horaire s'écrit toujours sous le trigramme,
  en petit, si bien que tous les badges ont la largeur d'un trigramme ;
- « Auj. », grisé sur le jour courant, se lisait comme un bouton en panne :
  il disparaît ce jour-là et revient dès qu'on change de jour ;
- la pastille « Hors ligne » couvrait la date du Planning (et le haut du
  héros) : sur téléphone elle se pose au-dessus de la capsule du menu, et
  s'efface d'elle-même 4 s après la perte du réseau.
Reste, et pourquoi : rien vu d'autre à ces largeurs ; au bureau, le tableau
remplit l'écran comme voulu le 12/10. Affichage seulement ; vérificateur
identique à l'octet ; rien ne déborde, aucune erreur.

**La colonne D tout à droite** (le client, le 18/10/2026 : « mettre la
colonne D tout à droite ? »). Le Planning se lit AM · PM · N · D : les
trois pauses d'affilée, la journée à part. Elle était entre AM et PM depuis
le 26/09 (l'ordre des heures d'arrivée). Seul l'ordre de `PAUSES` change ;
la surbrillance de la pause du moment suit, son rang se calculant sur cet
ordre (AM surlignée le 13/10 à 10 h). Affichage seulement ; vérificateur
identique à l'octet ; vérifié à 320 px (hors ligne), 390 et 1280 px.

**Les relais de 12 h dans une case fusionnée** (le client, le 18/10/2026 :
« si 2 personnes font 12 h sur 3 pauses pour combler un poste, est-ce
possible de fusionner les cellules ? », puis « essaye pour voir »). Sur
une ligne du Planning, une pause tenue seulement par deux relais
(`relaisDouze()`) fusionne avec la pause voisine quand le relais qui en
vient y tient, seul, le même poste toute la pause (`fusionsLigne()`). La
case (`colspan`, `caseFusion()`) porte une barre par personne, longue de
ses heures, avec la part qu'elle tient : le 27/01, contremaître, « ATA
06-18 | YPE 18-06 » sur AM · PM · N ; le 13/10, terrain arrière, « AAI
14-18 | GKT 18-06 » sur PM · N (AAI est à la distillation le matin, la
case AM reste à SMA). Le commentaire s'ouvre au clic, comme sur tout badge.
La surbrillance de la pause du moment passe d'un rang de colonne à la clé
de pause de chaque case (`data-k`, `data-mck`), un rang ne tenant plus
quand une case en couvre deux. Affichage seulement ; vérificateur identique
à l'octet ; vérifié à 320 px (hors ligne), 390 et 1280 px. **Gardée** (le
client, le 18/10/2026 : « on garde la fusion »).
Puis (le client : « go » sur deux retouches) : un trait fin en pointillé
marque, dans la case fusionnée, la limite de chaque pause (14 h, 22 h), et
la pause du moment y garde son voile, posé derrière les barres sur sa seule
part de la case (`.eqfus-sep`, `.eqfus-maint`) ; la case entière n'est
plus voilée. Vérifié le 27/01 à 15 h (PM voilé) et le 13/10, à 320 px (hors
ligne), 390 et 1280 px ; vérificateur identique à l'octet.

**« Remplace » son propre trigramme : une faute d'encodage corrigée**
(le client, le 18/10/2026, devant SMK le 23/10, « remplace SMK » : « il
faut corriger le commentaire dans celui qui remplace si on est certain
que c'est bien une erreur d'encodage et que l'on est sûr de ne pas faire
d'erreur »). C'est la seule correction du classeur que l'application
s'autorise, et elle est bornée : un commentaire qui écrit « remplace X »
dans la colonne de X lui-même, et UNE SEULE autre personne qui, le même
jour et sur la même cellule franche, écrit « remplacé par X ». Le X fautif
devient alors ce trigramme (`corrigerAutoRemplacements()`, au chargement
de l'horaire ; le vérificateur la découpe et l'applique aussi, et
`--auto-remplacements` liste ce qu'elle corrige). Mesuré sur le classeur
du 16/10 : **6 journées, toutes SMK pour CGI** (10/07, 14/08, 23/10,
27/11, 16 et 17/12), CGI écrivant chaque fois « remplacé par SMK ». Deux
journées qui se nomment elles-mêmes restent telles quelles, faute de
répondant : YPE le 23/06 (« échange avec ATA remplace YPE ») et SLT le
01/10 (« remplace SLT de 12h30 à 14h »). Seul le texte change : neuf
règles, `--manques 0926`, `--polyvalence` et `--compteurs` identiques à
l'octet, `--placement --tout` ne diffère que par ce texte, `cal/SMK.ics`
par la note de ces journées. Vérifié au Planning du 23/10 (« SMK :
remplace CGI ») à 320 px (hors ligne), 390 et 1280 px.

**Le binôme de l'équipe, en initiales** (le client, le 17/10/2026 : « dans le
héros les opérateurs doivent voir leur équipe et le binôme avec qui ils
tournent ; on se fout du numéro de binôme, le plus important ce sont les
initiales », puis « pour adjoint et contremaître, le numéro de binôme dans le
héros est inutile »). Les chiffres d'un opérateur portent « Équipe » puis
« Binôme » : les trigrammes du contremaître et de l'adjoint (« AFA · YBT »,
« GPS » seul pour le binôme 2). `_pfBinomeEquipe()` prend la pause de
l'équipe par son cycle (`equipeALaPause()`) et les cadres dont la cellule
franche, la rotation prévue, écrit cette pause, sur les quatre premiers jours
de SEMAINE à partir d'aujourd'hui. **La première version prenait le premier
jour venu, un samedi, et donnait un faux binôme à l'équipe 2** (l'adjoint du
binôme 3, au matin du 18/10 ; elle tourne la semaine avec GPS) : le week-end,
les cadres tournent autrement. Mesuré au 17/10 contre le classeur : équipe 2
GPS, équipe 4 ATA · JBI, équipe 5 AFA · YBT. Un cadre ne voit plus que son
partenaire, sans numéro. Sous 380 px, les intitulés des chiffres passent sur
deux lignes (« Polyvalence » touchait « Week-end libre »), et la ligne de
formation aussi (« Distillation » était coupé). Vérifié sur LCI, GJR, PAM,
AAI, SKS, VBN, ATR et GPS à 320 px (hors ligne), 390 et 1280 px.

**Plus de rangée de chiffres dans le héros** (le client, le 18/10/2026,
capture de « ATR / ADJOINT · 24 oct. / WEEK-END LIBRE » : « ceci est
inutile présenté comme cela »). Deux informations de nature différente
s'y lisaient comme des statistiques, en grands caractères à chasse fixe.
Le binôme rejoint l'identité, sous le poste : « Binôme · ATR » pour un
cadre, « Équipe 5 · AFA · YBT » pour un opérateur. Le week-end libre
devient une ligne sous le prochain poste, « Prochain week-end libre ·
Samedi 24 octobre », absente quand il n'y en a plus (YBT). Le nombre de
polyvalences part : l'onglet Équipes les montre poste par poste. Neuf
règles à zéro (aucune lecture touchée) ; vérifié sur VBN, LCI, YBT et PDE
à 320 px (hors ligne), 390 et 1280 px, rien ne déborde, aucune erreur.

**Puis le héros repris en entier** (le client, le 18/10/2026 : « il y a
moyen de faire bien mieux pour le héros, je veux du 100 % »). Photographié
à 320 px (hors ligne), 390 et 1280 px sur VBN, LCI, SKS et YBT. Défauts
relevés et corrigés :
- le week-end libre flottait seul, mal aligné, entre le prochain poste et
  « Mon année » : il devient la seconde ligne du même cadre (`.pf-bloc`),
  sous un filet, avec une icône de calendrier ; « Week-end libre » tout
  court, « Prochain week-end… » se coupait à 320 px ;
- le statut et la formation prenaient deux lignes : une seule, « Ouvrier ·
  En formation · Distillation », la formation en jaune ;
- les trois progressions se suivaient sans séparation : un filet entre
  l'année et chaque cycle, et la semaine du cycle (« semaine 6 / 6 »)
  passe de 9,5 à 11 px ;
- au bureau, tout s'étirait sur 1 100 px (barres de 1 100 px, week-end aux
  deux bouts de l'écran) : deux colonnes, l'identité et le bloc du poste à
  gauche, les progressions à droite ; le héros passe de 714 à 595 px.
Aucune lecture touchée, neuf règles à zéro ; rien ne déborde, aucune
erreur.

**Le prochain poste en billet** (le client, le 18/10/2026 : « j'aime
prochain wk libre mais pas la présentation du prochain poste »). Le bloc
se lit désormais de haut en bas : l'intitulé (« Prochain poste »,
« Reprise », « En poste ») et, à droite dans une pastille, quand
(« Aujourd'hui », « Demain », « Dans 3 j », « Encore 2 h 40 » en
poste) ; puis la pause en grand carré à sa couleur, la date entière, et
l'heure de début et de fin reliées par un trait, qui se remplit comme
une barre de progression pendant la pause ; l'atelier dessous (en orange
quand c'est un changement proposé par l'application). « Aujourd'hui »
n'est plus écrit deux fois, ni « Début à 22 h » à côté de l'horaire qui
le dit déjà. La ligne du week-end libre ne change pas. Aucune lecture
touchée, neuf règles à zéro ; vérifié sur VBN, LCI, SKS et YBT à 320 px
(hors ligne), 390 et 1280 px, à 5 h 10, 17 h 18 et en poste.

**Troisième passe complète** (le client, le 17/10/2026 : « optimise un max
encore l'accueil »). Captures à 320, 390 et 1280 px sur LCI et VBN, puis :
- **la tuile RHS contredisait la liste du bas** : « 1 h reprises » d'un
  côté, « RHS 2 j · 16 h » de l'autre. Les reprises partielles (« 1h rhs »,
  `r.rhs`) et les journées entières (code RHS, `calc.abs.RHS`) sont lues
  par deux chemins qui s'excluent ; la tuile les additionne (LCI : 17 h,
  « 2 j entières · 1 h en partie »), et la liste ne redit plus RHS ;
- « 1/2 VA » se coupait sur deux lignes dans son badge et redisait un
  congé déjà en tuile : un code ne se coupe plus, et une demi-journée d'un
  congé déjà compté plus haut ne revient pas en bas ;
- héros : « Équipe 5 » n'est plus écrit sous le poste (c'est le premier
  chiffre) ; sous 760 px, les intitulés des chiffres passent sur deux lignes
  (« Polyvalence » touchait « Week-end libre » à 390 px aussi) ;
- intitulés de bloc : sous 380 px, le sous-titre passe sous le titre
  (« Congés restants » se coupait) ; « Maladie et autres absences » perd le
  sien, qui la coupait en deux lignes ;
- polyvalence : « Mon recyclage › » en lien simple, plus en gros bouton ;
- jour par jour : la légende prend les codes et l'ordre des autres
  (AM, PM, N, D) ; le congé ou la maladie est un contour neutre, comme au
  mois (en orange, il se confondait avec le matin), et l'infobulle dit
  « Congé ou maladie » (« absence » veut dire maladie dans la maison) ;
  « Repos » quitte la légende (une case vide se lit seule) ;
- bureau : la grille jour par jour ne tenait que la moitié du cadre (cases
  de 22 px au plus, 900 px de large), et les barres des pauses par mois
  passent à 34 px.
Aucun calcul touché, neuf règles à zéro. Vérifié sur LCI et VBN à 320 px
(hors ligne), 390 et 1280 px, sans débordement ni erreur. Les congés
restants écrits deux fois (héros et tuiles) : tranché le 17/10/2026, un
seul endroit, voir « Les congés en un seul endroit ».

**Le guide d'installation** (le client, le 17/10/2026 : « l'app amène à
l'explication d'installation complète, professionnelle et intuitive de l'app
sur mobile ? »). Non : la carte du 10/10 ne disait qu'une ligne à l'iPhone,
rien à un Android sans invite du système, rien sur l'écran de connexion, et
plus rien une fois masquée. `guideInstall()` ouvre une fenêtre (du bas sur
téléphone, au centre au bureau) : un onglet iPhone / Android choisi selon
l'appareil, les étapes numérotées avec le pictogramme du bouton à toucher
(Partager, Sur l'écran d'accueil, menu ⋮, menu de Samsung Internet), la
variante de Chrome ou Firefox sur iPhone (iOS 16.4 et plus), le bouton
« Installer maintenant » quand Android l'offre, et ce que l'installation
apporte. **Une messagerie (WhatsApp, Messenger, Instagram…) ne sait pas
installer** : le guide le dit d'abord, avec « Ouvrir dans Safari » et
« Copier le lien ». **Sur iPhone, l'application installée ne partage pas la
mémoire de Safari** : la dernière étape prévient que la connexion se refait
une fois. Le guide s'ouvre depuis l'écran de connexion (« Installer
l'application sur mon téléphone »), la carte de l'Accueil (« Comment
faire ») et les Réglages (« Application sur l'écran d'accueil », qui dit
aussi si elle est installée). Vérifié en iPhone Safari à 320 px (hors
ligne) et 390, Android Chrome et WhatsApp à 390, bureau à 1280 : rien ne
déborde, Échap et la croix ferment. Seul un vrai téléphone dira si les
libellés de son système sont exactement ceux-là.

**Puis comme Pino** (le client, le même jour : « pour l'installation de
l'app, la même chose que pour le GitHub pizzeria Pino »). Le dépôt
`CronoBots/PIZZAPINO` a été lu : son guide n'est pas une notice, c'est une
démonstration. Le guide de BIOWANZE en est la reprise, aux couleurs de la
marque (`#instGuide`, `guideInstall()` inchangé pour les appelants), et la
fenêtre à onglets iPhone / Android de la version du matin est retirée :
- plein écran : un téléphone dessiné à 212 × 400, mis à l'échelle de
  l'écran, rejoue en boucle les gestes. La page dessinée est l'Accueil
  (la bannière, un avatar « BWZ » et des cadres vides), sans personne
  dedans. Un doigt se pose sur le bouton à toucher, et la boucle finit sur
  l'icône BIOWANZE posée sur l'écran d'accueil ;
- les gestes sont ceux du navigateur réellement ouvert : Safari (sous
  iOS 26, Partager est rangé sous « ⋯ » ; sur iPad, il est en haut),
  Chrome, Edge et Firefox sur iPhone ; Chrome, Samsung, Edge et Firefox
  sur Android. « Pas le bon navigateur ? » corrige d'un geste ;
- dessous, une barre par étape (toucher un segment rejoue son étape),
  « Étape n sur m » et la consigne ; une flèche « Ici » montre le vrai
  bouton du navigateur, en bas ou en haut à droite ;
- une messagerie est d'abord invitée à ouvrir le lien dans le
  navigateur : « Ouvrir dans Chrome » (lien `intent://`) sur Android, la
  démonstration de « Ouvrir dans Safari » sur iPhone, et « Copier le
  lien » ;
- quand Android offre l'invite du système, il n'y a qu'un bouton :
  « Installer l'application ». La carte de l'Accueil n'a plus qu'un
  bouton « Installer », qui lance cette invite ou ouvre le guide ;
- au bureau, un QR code (`qr-installer.svg`, écrit par
  `tools/qr-installer.py`), qui mène à `…/groups/#installer` : cette
  adresse ouvre le guide à l'arrivée, puis la marque est retirée de
  l'adresse (sinon l'icône ajoutée sur iPhone rouvrirait le guide à chaque
  lancement) ;
- après l'installation : « C'est installé ! ». Le retour arrière d'Android
  ferme le guide sans quitter l'application (entrée d'historique), comme
  Échap et la croix.

**Le premier QR code ne se lisait pas** : jsQR le rendait vide, alors que
celui de Pino, de même dessin, se lisait. Le cœur des yeux était au cyan
clair de la marque, que le lecteur prenait pour du blanc. Il est passé au
cyan foncé (`#1F6F8B`) : le code rend l'adresse. Vérifié en iPhone Safari
(iOS 18 et 26) à 320 px (hors ligne, ouvert par l'écran de connexion,
fermé par le retour arrière) et 390, en Android Chrome, en WhatsApp et au
bureau à 1280 : rien ne déborde, aucune erreur. **Ce qui n'est pas repris
de Pino** : son manifeste n'est chargé que sur téléphone (au bureau, pas
de proposition d'installation), et son bandeau d'installation flottant.
BIOWANZE garde sa carte dans l'Accueil, et reste installable au bureau.
Puis, le même jour (le client) : le téléphone dessiné affiche l'adresse
« BioWanze.app » et non celle de l'hébergeur (`HOTE`, affichage seulement ;
le lien `intent://` et « Copier le lien » gardent la vraie adresse). « Ici »
n'était pas centré sur sa flèche : les deux étaient calés séparément au
bord droit. Ils sont désormais dans un même bloc (`.inst-f`), et l'écart
mesuré entre leurs centres est de 0 px. En tête, le logo vectoriel à fond
transparent (`logo.svg`) remplace l'icône à tuile, avec le titre et le
sous-titre centrés dessous. Vérifié à 320 px (hors ligne), 390 et 1280 px.
**Et ce n'était pas fini** : le client, « juste Ici devait être centré sur
la flèche à droite, et non centrer la flèche ». La flèche n'avait pas
bougé, mais « ICI » restait visiblement à gauche de la pointe :
l'espacement des lettres (.12em) laisse un blanc après le dernier « I »,
que la boîte mesurée comptait. `margin-right:-.12em` le retire. **Mesurer
la boîte ne suffisait pas** : il fallait regarder la capture. Écart au
centre de la pointe : moins d'un pixel en Safari iOS 26 (en bas à
droite), en Safari iOS 18 (en bas au centre, où est le bouton Partager)
et en Chrome Android (en haut à droite), à 320 et 390 px.
Le titre devient « Installer l'application » (le client : le logo dit déjà
BIOWANZE). Le sous-titre « Sur l'écran d'accueil, comme une application »
redisait « application » et ce que les étapes montrent ; il dit désormais
ce que l'application apporte, sur une seule ligne : d'abord « Votre
horaire et votre salaire en un geste, même hors ligne », qui passait à la
ligne à 320 et 390 px ; puis « Horaire et salaire, même hors ligne », en
`white-space:nowrap` (le client : « une phrase plus courte sans mise à la
ligne »).

**Les changements d'horaire, un badge dans le héros** (le client, le
17/10/2026 : « ne devraient-elles pas être un badge quelque part dans le
héros qui affiche les changements, au lieu d'un cadre au-dessus ?
Optimise au maximum »). Le cadre « Mise à jour de votre horaire »
poussait tout l'Accueil vers le bas tant qu'on n'avait pas touché « Vu ».
Une pilule sombre, cloche et nombre de journées sur une pastille cyan, se
pose désormais sur la bannière, à côté de la roue (`badgeNotifHTML()`,
`NOTIF_NB`) ; elle pulse trois fois à l'arrivée, puis se tait. Un appui
ouvre les changements dans une feuille (`#notifOv`), du bas sur téléphone
et au centre au bureau : « Horaire modifié », un sous-titre d'une ligne
(« 3 journées · classeur du 16/10 »), les journées avec leur commentaire,
puis « Vu, effacer », qui efface le badge et l'attente. La croix, le fond,
Échap ou un appui sur une journée referment la feuille ; le dépli « Voir
les n autres » est parti, la liste défile dans la feuille. Le point de
l'onglet Accueil et la notification du téléphone ne changent pas. Vérifié
sur VBN, trois journées en attente, à 320 px (hors ligne), 390 et
1280 px : badge à 8 px de la roue, sous-titre sur une ligne, Échap
referme, « Vu » efface et rien ne revient au rechargement, aucune erreur.

**L'invitation à installer, au bas de l'Accueil** (le client, le 17/10/2026,
capture de l'iPhone : « le cadre Installer l'application dans le bas de
l'Accueil, et optimise car on ne sait pas tout lire »). Le sous-titre était
coupé par des points de suspension (« En trois gestes : le guide v… ») : la
carte empruntait le style des notifications, qui coupe le sous-titre à une
ligne. Elle devient un cadre ordinaire, placé après l'agenda : l'icône, le
titre et un texte qui passe à la ligne, la croix en haut à droite, puis
« Installer » sur toute la largeur. Les textes sont plus courts : « Trois
gestes, le guide vous les montre. », ou « Sur l'écran d'accueil, plein écran
et hors ligne. » quand Android propose l'installation. Mesuré à 320 px (hors
ligne) et 390 px en iPhone : aucun texte coupé, rien ne déborde, et le
bouton ouvre le guide. Au bureau, la carte reste cachée sans invite du
système, comme avant.

**Les congés en un seul endroit, et le cycle en cours** (le client, le
17/10/2026, à la question des congés restants écrits deux fois : « non, il
faut regrouper tout au même endroit ; remettre les badges de pause AM PM N
D dans la partie Mon rythme ; sous Mon année 2026 et sa progression, la
même chose pour Mon cycle actuel »). La rangée des congés restants et du
solde flex time quitte le héros : ils ne vivent plus que dans « Mes
compteurs », en tuiles (`.pf-cg` et son écouteur sont retirés). Les cases
AM · PM · N · D, faites et à venir, reviennent en tête de « Mon rythme »
(`ryPausesHTML()`, « Pauses de l'année »). Le pied du héros garde « Mon
année » et gagne « Mon cycle actuel » : la semaine du cycle et ses bornes
(« Semaine 6 sur 6 · 7 sept. – 18 oct. »), la même barre de journées
prestées faites et à venir, comptées sur le cycle (`ryCompte()`,
`ryBarre()`). `cycleActuel()` cale le cycle par `calageLong()`, qui prend
désormais une fin facultative, sur les 92 jours qui entourent aujourd'hui
(sur un seul mois, 5 et 6 semaines se confondent), puis sur ceux qui en
partent si le premier calage échoue : VBN, nommé contremaître le 15/09, ne
calait pas sur la fenêtre qui chevauche le changement. Mesuré au 17/10 :
VBN semaine 6 sur 6 (sa semaine de D), LCI et SKS semaine 1 sur 5 depuis le
12/10, BLR semaine 3 sur 10 (le relais de consignation), CAN semaine 2 sur
2 (la quinzaine de la STEP, partie du lundi). Aucune lecture touchée :
neuf règles à zéro, le calage par défaut de la prolongation inchangé.
Vérifié sur VBN, LCI, CAN, BLR et SKS à 320 px (hors ligne), 390 et
1280 px, sans débordement ni erreur.

Puis, le même jour (le client, capture de « Mon rythme » : « la partie
avec mois le plus chargé et férié n'est pas utile ; centrer et optimiser
les légendes des deux autres graphiques ; la barre de progression du cycle,
peut-on encore l'optimiser ? ») : la phrase du mois le plus chargé et des
fériés travaillés part, avec `ryInsight()` ; les légendes « Pauses par
mois » et « Jour par jour » sont centrées sous leur graphique. Le cycle
n'est plus une barre mais une **frise** (`ryCycleHTML()`) : une case par
jour du cycle, groupée par semaine, à la couleur de la pause tenue (celle
des badges), le congé en contour, la maladie en rouge, le repos vide ; les
jours passés pleins, ceux à venir pâlis, aujourd'hui cerclé, la semaine en
cours encadrée. En tête, « Semaine 6 / 6 » à droite du titre (et le
pourcentage à droite de « Mon année ») ; dessous, prestées et à venir, puis
les bornes. Le relais de consignation (10 semaines) prend des cases plus
fines. Vérifié sur VBN, LCI, CAN, BLR et SKS à 320 px (hors ligne), 390 et
1280 px, sans débordement ni erreur ; neuf règles à zéro.

Puis (le client, le même jour : « dans jour par jour ajouter la ligne avec
les numéros de jours au-dessus et supprimer l'explication ; séparer le
cadre calendrier du héros juste après la progression de cycle ») : la
grille « Jour par jour » a une ligne de numéros au-dessus (`.ry-hm-n`),
le jour courant en clair (d'abord 1, 5, 10… 30 seulement sur téléphone,
puis les 31, voir plus bas). « chaque case = un jour » est retiré. Le héros et le cadre du mois
ne sont plus soudés (la règle du 16/10 est retirée) : deux cadres, 16 px
d'écart, chacun ses coins et son ombre. Vérifié à 320 px (hors ligne),
390 et 1280 px ; neuf règles à zéro.

Puis (le client, le même jour : « faire pareil avec le prochain cycle, et
à chaque fois indiquer à droite l'équipe avec laquelle on travaille si
c'est la fiche d'un contremaître ou adjoint, ou les trigrammes du CM et de
l'adjoint si c'est un opérateur ») : une seconde frise, « Mon prochain
cycle », commence le lendemain du dernier jour du cycle en cours, même
longueur et même calage ; ses jours ne sont pas pâlis, tous étant à venir,
et sa légende dit les journées à prester. La semaine du cycle passe à côté
du titre, en petit. À droite de chaque titre, une pastille cyan
(`cycleAvec()`) : pour un cadre, l'équipe que son cycle met à sa pause
(`equipeALaPause()`) ; pour un opérateur, le contremaître et l'adjoint dont
la cellule franche porte sa pause (la lecture de `_pfBinomeEquipe()`).
Seuls les jours de semaine où la cellule franche prévoit AM, PM ou N
comptent (le week-end, les cadres tournent autrement). Les cycles de 5 et
6 semaines glissent l'un sur l'autre : quand le partenaire change en cours
de cycle et pèse au moins un quart des jours, la pastille écrit « A → B »
dans l'ordre (la STEP : « ATA · JBI → AFA · YBT »). Mesuré au 17/10 contre
le classeur : VBN Éq. 5 puis Éq. 1, GPS Éq. 2 puis Éq. 4, LCI AFA · YBT
puis ATA · JBI, BLR GPS (le binôme 2 n'a pas d'adjoint) puis FLI · FPA ;
SLI, sans cycle calé, n'a ni l'un ni l'autre. À 320 px, une pastille longue
passe sous le titre. Vérifié à 320 px (hors ligne), 390 et 1280 px, sans
débordement ni erreur ; neuf règles à zéro.

Puis (le client, le même jour : « la hauteur de la ligne des cases des
cycles doit être la même que celle de l'année ; les jours ne sont pas tous
affichés dans la ligne des jours ») : les cases des deux frises font 8 px
de haut, comme la barre de « Mon année », et la semaine en cours n'est plus
qu'un contour, sans marge qui grandirait la frise. La ligne des numéros de
« Jour par jour » écrit désormais les 31 jours, aussi sur téléphone :
chiffres resserrés (7 px sous 380 px, 8,5 px au-delà, 10 px au bureau).
Vérifié à 320 px (hors ligne), 390 et 1280 px ; neuf règles à zéro.

Puis (le client, le même jour) : les trois blocs de « Mon rythme »
s'intitulent « 2026 : Mes pauses », « 2026 : Mois par mois » et « 2026 :
Jour par jour », sans explication à côté (« faites · à venir », « touchez
un mois ») ; un mois du graphique ne se touche plus (la barre n'est plus un
bouton, son écouteur et son survol sont retirés) ; le filet au-dessus de
« Jour par jour » part, avec `.ry-sep`. Vérifié à 320 px (hors ligne), 390
et 1280 px ; neuf règles à zéro.

Puis (le client, le même jour, deux captures : « supprimer la partie
explication des horaires des années futures et supprimer la ligne bilan,
les stats parlent d'elles-mêmes ; centrer et espacer la légende pour
utiliser la largeur ») : la note « Horaire 2029 prolongé par les cycles… »
quitte le cadre du mois ET celui du salaire (`#calProj`, `#salProj`,
`majProjNote()` et `.projnote` retirés ; le tableau du jour garde son
« prolongé par les cycles »). Le titre « Bilan d'octobre » part
(`#calBilanT`), les quatre chiffres suivent le calendrier sous un seul
filet. La légende du mois se répartit sur toute la largeur
(`space-evenly`). Vérifié en octobre 2026 et en janvier 2028 projeté, à
320 px (hors ligne), 390 et 1280 px ; neuf règles à zéro.

Le sous-titre de « Mon rythme » a perdu son « · 2026 », puis c'est l'inverse
qu'il fallait (le client, le 18/10/2026 : « non, 2026 apparaît toujours ») :
**j'avais compris le sous-titre, il parlait des trois titres**. Ils
redeviennent « Mes pauses », « Mois par mois » et « Jour par jour », et
l'année ne s'écrit plus qu'une fois, en sous-titre du cadre : « année 2026 »
(« mois par mois et jour par jour » redisait les titres).

**La roue des réglages en haut à droite de la bannière** (le client, le
18/10/2026). Elle était à gauche depuis le 16/10 pour ne pas couvrir la
marque ; elle mord désormais un peu sur le haut du logo, à la demande du
client. Le badge des changements d'horaire prend sa place en haut à gauche,
sur l'usine. La roue ouvre bien les Réglages à 320 px (hors ligne), 390 et
1280 px.

Puis (le client, le 18/10/2026) : **un cadre dans sa seconde semaine de D
(la 6e de son cycle de 6 semaines) n'affiche plus d'équipe pour le cycle
actuel** — elle a repris son cycle de 5 semaines sans lui. VBN et ATR, en
semaine 6 le 18/10, n'ont plus que « Équipe 1 » au prochain cycle ; GPS,
en semaine 3, garde « Équipe 2 ». L'équipe ou le binôme s'écrit en texte
cyan, sans pastille, et « Éq. 5 » devient « Équipe 5 ». La ligne des
numéros de « Jour par jour » revient à 1, 5, 10… 30 et un point entre sur
téléphone (« tous les chiffres, c'est trop serré ») ; le bureau garde les
31. Vérifié à 320 px (hors ligne), 390 et 1280 px ; neuf règles à zéro.

**Le classeur l'emporte toujours, même sur une journée touchée à la main**
(le client, le 18/10/2026, capture de la feuille du 30/09 : « pourquoi le
30 je suis en nuit alors que non ? », puis « ça doit être marqué comme dans
la feuille de prestation ; il ne faut plus les journées touchées à la
main »). Le classeur, lu depuis le 14/10, dit AM (9 h-15 h, le `1A40 · P11`
du relevé) ; son téléphone gardait N, une journée corrigée sur l'appareil
n'étant jamais rafraîchie par l'horaire. **J'ai d'abord ajouté une ligne
« Corrigée à la main » et un bouton « Reprendre »** : le client n'y a rien
compris et ne se souvenait d'aucune saisie. C'est retiré. `remplirMois()`
relit désormais TOUTE journée que le classeur couvre, à chaque ouverture ;
la feuille du jour l'affiche sans la laisser corriger (pause, congé,
heures et rappel grisés), et seul le vélo, que le classeur n'écrit pas,
reste à la main et survit au rechargement. Éprouvé à 320 px (hors ligne),
390 et 1280 px : un N forcé sur le 30/09 redevient AM au rechargement, le
vélo coché reste ; rien ne déborde. Neuf règles à zéro (aucune lecture
touchée).

**Le cadre du mois, repris case par case** (le client, le 18/10/2026,
capture de septembre : « comment optimiser cela ? 100 % pro »). Relevé à
320, 390 et 1280 px, puis corrigé en une fois :
- le numéro du jour tombe au même endroit dans toutes les cases : le repos,
  centré, décalait sa ligne ;
- un code de plus de trois signes (« CPPT ») se resserre au lieu d'être
  coupé par le bord de sa case à 320 et 390 px ;
- les points (vélo, rappel, heures modifiées) passent dans le coin haut
  droit : en bas, ils mordaient sur la pastille et sur le liseré de la
  prime conservée ;
- un « +FT » sur un repos sans heure prestée (VBN le 02/09, « 2h +FT · cf
  01/09 ») s'affichait comme un congé « 2+FT » : c'est un renvoi, les heures
  sont celles d'un autre jour. La case reste un repos (affichage seulement,
  comme l'agenda depuis le 13/10). **Le point des heures modifiées y est
  d'abord resté, et c'était le mauvais jour** (le client, le même jour :
  « les heures modifiées avec commentaire pour d'autres cellules ne
  devraient-elles pas être dans la cellule du jour en question ? »). Le
  calcul les comptait déjà sur le 01/09 (`epargnesDuMois()`,
  `renvoisDuMois()`) ; `renvoisAffiches()` le dit désormais à l'écran, avec
  les mêmes motifs : le point va sur le jour qui reçoit les heures, la
  feuille de ce jour écrit « Heures de cette journée : 2h +FT · écrites au
  02/09 », et celle du 02/09 « Ces heures comptent le 01/09 » (`rvD`,
  `rvS`, effacés avec les autres champs du pré-remplissage). **Mesuré pour
  tout le monde** (le client : « cela est bon pour tout le monde ? ») : 86
  renvois chez 28 personnes, relus au navigateur un par un. 85 jours qui
  reçoivent des heures portent le point. La cellule source ne devient un
  repos que si sa cellule franche est « - » : JBS le 21/12
  (« PM · 8h +FT · cf 20/12 ») et ATA le 16/03 (« 06h-18h ») ont travaillé
  ce jour-là, et une première version les montrait en repos. Les heures
  affichées sont celles que le commentaire nomme (« +4h +FT cf 08/03 »),
  sinon celles de l'annotation. Un seul jour n'avait pas le point, le
  15/05 de VGG : le 16/05 écrit « 2h rhs pris le 15.05 départ à 12h », que
  le calcul ne lisait pas (`renvoisDuMois()` n'acceptait que les codes du
  barème). Le client, le 18/10/2026 : « oui ». `renvoisDuMois()` rend
  désormais « RHS@n » pour une reprise d'heures sup renvoyée, et
  `lireJournee()` la lit comme le « +Nh rhs » d'un commentaire : le 15/05
  passe de 8 h à 6 h prestées et 2 h de récup. HS, la feuille le dit. Seule
  journée de l'année de cette forme ; les cinq sorties du vérificateur sont
  identiques à l'octet. **L'agenda gardait 6-14**, le départ étant écrit sur
  l'autre case ; le client : « les agendas doivent être corrects aussi ».
  `renvoisHeures()` passe les « arrivée à » et « départ à » d'une cellule
  qui renvoie à un autre jour (mêmes motifs que `renvoisDuMois()`) à
  `lectureAgenda()` de ce jour-là. Sept événements de 2026 changent, chacun
  lu contre sa cellule : VGG 15/05 6-12, ATR 21/01 fin à 12 h, CKS 27/06
  début à 7 h, CWN 26/06 fin à 20 h, FPA 19/09 début à 0 h, SVE nuit du
  12/07 fin à 2 h, VBN 19/09 début à 16 h. **Et VGG n'était pas seul** (le
  client : « bizarre que cela ne concernait que VGG, tu es sûr ? ») :
  relu tout l'horaire, les 29 « pris le » (10 RTT, 15 −FT, 3 VA, 1 RHS)
  étaient bien comptés sauf la reprise de VGG, mais deux renvois s'écrivent
  « pour le », que rien ne lisait. RDT le 13/10, ["-","4h rhs","pour le
  16.10"] : le 16/10 il part à 18 h, 8 h payées comme travaillées ; CKS le
  12/11, ["-","4h RTT","pour 13/11"] : le 13/11, ½ VA « remplacé par LHS »,
  4 h travaillées alors qu'il n'est pas venu, et le RTT affiché le 12/11 sur
  un repos. `RX_POUR_LE` et `prisAilleurs()` les lisent comme « pris le »,
  mais seulement en tête du commentaire d'une cellule franche vide ou « - ».
  RDT 16/10 : 4 h prestées et 4 h de récup. HS ; CKS 13/11 : 0 h, ½ VA et
  4 h RTT, son agenda perd le matin du 13/11, et la fermentation de ce
  matin-là passe de 2/1 à 1/1 (LHS la tient). Les manques, le Recyclage et
  les compteurs sont identiques à l'octet ;
- **puis tous les commentaires** (le client, le 18/10/2026 : « tous les
  commentaires doivent être vérifiés, pour le classeur existant et les
  futurs »). Les 853 dates citées par les commentaires de l'horaire ont été
  classées une à une. Une famille entière échappait encore : un congé posé
  sur un repos (« - ») qui nomme UNE date sous d'autres mots — « cf
  02/01 », « Cfr 17/12 », « du 19/10 », « au 18/02 », « arrivée à 08h00' le
  25.03 ». Le congé était compté sur le repos, et souvent une seconde fois
  sur la journée nommée, qui l'écrit elle-même (CKS le 14/01, « +2h RTT
  Départ à 9h »). `prisAilleurs()` les lit désormais comme « pris le »
  (une seule date, ni « rappel », ni « voir », ni « +FT »), et un congé
  renvoyé que la journée porte déjà n'est pas ajouté. 15 cellules sources
  redeviennent des repos ; sept journées changent d'heures : IME 25/03
  7 → 5 h (2 h RTT, arrivé à 8 h), SPS 02/02 8 → 6 h, DBE 15/03 8 → 6 h
  (départ à 20 h), KDN 17/12 et ADK 14/10 4 → 0 h (remplacés, ½ VA ou ½ DTT
  en plus), JBI 21/08 4 → 0 h (le RJF « cf 21/08 » posé le 13/08 : relevé
  d'août, écart connu levé) ; VBN 14/06 garde ses 4 h payées mais reçoit les
  4 h de −FT écrites le 19/06, et n'est plus compté présent (le précédent du
  30/01 : RTT et −FT posés ensemble, il n'a pas travaillé). **Les compteurs
  flex time passent de 77/78 à 78/78** : l'« erreur du classeur » de FPA
  était un −FT compté deux fois. Placement : trois pauses passées perdent
  une personne comptée deux fois (14/06, 14/10, 17/12), manques et
  Recyclage identiques à l'octet. Agendas : ADK 14/10, KDN 17/12 et VBN
  14/06 retirés, IME 25/03 commence à 8 h.
  **Et pour les classeurs futurs, une règle faible du vérificateur, « date
  d'un autre jour »** : toute cellule portant un code d'heures dont le
  commentaire cite une date que rien ne lit (ni le jour même, ni un motif de
  l'application, ni un mot de simple référence — « mail du », « déplacé
  au », « voir », « encodé le »…). `mettre-a-jour.py` l'ajoute au rapport,
  qui part par e-mail avec chaque classeur. Éprouvée : « à reprendre le
  13/11 » planté chez CKS est signalé. Elle en signale une aujourd'hui,
  VGG le 15/03, « 1h RTT · presté 7h le 20.03 » (et le 20/03 « SD 26 · voir
  15.03 ») : question au client ;
- « Heures en ± » devient « Heures modifiées » ; la légende est centrée et
  resserrée sous 380 px (deux lignes à 320 px au lieu de trois) ;
- les chiffres du bilan et le flex du mois quittent la police à chasse
  fixe (« 0,5 » s'y lisait « 0 , 5 ») ; « +1  h » perd son espace double ;
- au bureau, cases de 78 px et textes agrandis, qui flottaient dans des
  cases de 260 px.
Le 30/09 garde « CPPT » avec le liseré de la prime du matin : c'est la règle
de toutes les journées à code de jour. Neuf règles à zéro (aucune lecture
touchée) ; vérifié à 320 px (hors ligne), 390 et 1280 px, sans débordement
ni erreur.

**L'année, avec les cases du mois** (le client, le 18/10/2026 : « la même
chose que le calendrier mais pour l'année »). Le 07/10, le client avait fait
retirer la bascule Mois/Année (« il ne faut que le choix par mois ») : la
vue année d'alors ne montrait que douze petites grilles colorées. Je lui ai
d'abord proposé une frise compacte dans « Mon rythme » ; elle y était déjà
(« Jour par jour »), et je ne l'avais pas vue avant de la proposer : un
`grep -n ryHeatmap` aurait suffi. Ce qu'il voulait, c'est le calendrier
lui-même. `nfdm-v821` :
- une bascule « Mois | Année » sous la barre du mois, retenue dans
  `ui/calVue` ;
- en Année, `renderAnnee()` dessine les douze mois avec `caseJour()`, la
  fonction même du mois (codes, congés, maladie, commentaires, rappels,
  prime conservée, jour courant). Chaque mois est relu dans son
  enregistrement, comme le fait `loadMonth()` ; le mois affiché garde
  `st.month`. La légende réunit ce que l'année contient
  (`legendeDrapeaux()` / `legendeHTML()`, l'ancienne `legendeMois()`
  coupée en deux) ;
- un mois par ligne sur téléphone, deux de front à partir de 761 px, trois
  à partir de 1100 px, avec des cases de 52 px au bureau ; le bilan du mois
  se retire ;
- les flèches et le glissement changent d'année, et l'étiquette dit
  « 2026 » ; l'onglet Salaire, qui partage la barre, reste au mois
  (`vueAnnee()` exige l'Accueil) ;
- toucher un jour d'un autre mois charge ce mois, puis ouvre sa feuille
  (`jourAttendu`) ; dans la feuille, ‹ › passent au mois voisin
  (`allerMois()`), et non à l'année voisine : `go()` aurait sauté d'un an
  au 31.
Mesuré pour VBN : 12 mois, 365 cases, 271 codes, 162 commentaires. Le 3 mars
touché ouvre « Mardi 3 mars » ; 29 jours suivants mènent au « Mercredi 1
avril », toujours en 2026. Le choix est gardé au rechargement, et la vue tient
hors ligne. Le vérificateur (calendrier, manques, polyvalence, compteurs) et
`comparer-fiches.py VBN` sortent identiques à l'octet avant et après.
Vérifié à 320, 390 et 1280 px, sans débordement ni erreur.

Le même soir (le client, capture du téléphone à l'appui : « les boutons mois
année doivent prendre la largeur du cadre et en année le background et les
flèches de sélection sont décalés ; il faut aussi empêcher d'aller avant
2026 »), `nfdm-v822` :
- **le décalage** : la classe `annee` posée sur `#calCard` rencontrait
  `.annee{padding:0 16px 16px}`, reste CSS de la vue année retirée le
  07/10, qu'aucun élément ne portait plus. La barre et la grille
  rentraient de 12 px de chaque côté (372 px au lieu de 396 à 430 px). La
  classe devient `vue-an`, et les 75 lignes mortes (`.annee`,
  `.mois .jours`) partent. Mesuré : 396 px dans les deux modes. **Erreur
  commise** : la v821 avait été vérifiée par débordements et troncatures,
  qui ne voient pas un retrait intérieur. Il fallait comparer les boîtes
  des deux modes ;
- **la bascule** prend la largeur du cadre, alignée sur les flèches
  (344 px à 430). Au bureau, elle garde 420 px, au centre : étirée sur
  1 100 px, elle ne se lisait plus comme un choix ;
- **pas avant 2026** (`AN_MIN`) : la flèche ‹ s'éteint en janvier 2026
  (en Mois) ou en 2026 (en Année), aussi dans l'onglet Salaire, qui
  partage la barre. Le glissement bute au même endroit, le sélecteur
  refuse un mois de 2025 (`min`), et la feuille du 1er janvier ne recule
  plus. Éprouvé : le glissement mord (janvier → février → janvier), puis
  ne descend pas plus bas ; en Année, 2026 → 2027 → 2026, et pas en deçà ;
- **un vrai défaut trouvé en vérifiant** : ouverte directement en Année sur
  un appareil neuf, la vue n'avait de codes que pour le mois en cours (22
  sur 271). Le pré-remplissage écrit les douze mois par `save()`, qui
  attend 700 ms, et `renderAnnee()` les relisait avant. Le premier test de
  la v821 partait du mode Mois et basculait après quatre secondes : il ne
  pouvait pas le voir. La vue prend désormais la version en attente
  (`pending` / `DERNIER_ECRIT`) : 271 codes dès 1,5 s ;
- **passe complète de l'Accueil** (320, 390, 1280 px, bloc par bloc) : la
  frise « Jour par jour » de « Mon rythme » restait collée à gauche au
  bureau, sous une légende centrée ; elle est centrée (124 px de chaque
  côté). Rien d'autre ne déborde ni n'est tronqué, et aucune erreur.
  Reste, volontairement : la frise « Jour par jour » recoupe la vue Année,
  mais elle donne l'année sur un seul écran, là où la vue Année en demande
  dix sur un téléphone ; et les deux colonnes de « Mes compteurs » au
  bureau finissent à 40 px l'une de l'autre, ce qui tient au nombre de
  lignes de chacune.

**Les périodes de maladie, les polyvalences dans le héros** (le client, le
18/10/2026 : « indiquer le nombre de périodes de maladie ; pour les
opérateurs/adjoints, dans le héros, indiquer les polyvalences »),
`nfdm-v823` :
- **une période de maladie** enjambe les jours de repos et s'arrête au
  premier jour prévu qui n'est pas en maladie. Mesuré sur tout le classeur
  avant de choisir : 238 suites de jours consécutifs chez 65 personnes ;
  dans 6 cas seulement, deux maladies ne sont séparées que par 2 à 4 jours
  de repos laissés vides. Le classeur tranche lui-même : ATR numérote la
  même absence « cp 6/20 », « cp 7/20 », puis « cp 8/20 » après trois jours
  vides, et ainsi jusqu'à « cp 12/20 ». Les quatre autres cas (YPE, CJD,
  FPS, LHS) n'ont pas de commentaire qui dise le contraire : même règle.
  Un jour travaillé ou une autre absence entre deux maladies coupe la
  période (23 cas). `compteursCalcules()` rend `malPer` : **232 périodes**
  sur le classeur. Le décompte indépendant, sans la règle des repos, en
  trouve 238 : l'écart est exactement celui des 6 trous, la règle mord.
  VBN 4 (8 mars, 26 mai, 2 juillet, 10 septembre), ATR 3, PDE 3. La
  rangée « Maladie » de « Mes compteurs » écrit « en 4 périodes » sous son
  nom, comme le congé parental ;
- **les polyvalences** montent dans le héros, au-dessus du bloc du
  prochain poste, pour tout le monde sauf un contremaître (`estContremaitre`,
  la même garde qu'avant) : les ateliers acquis, un point à la couleur de
  leur zone, et le « degré » quand le classeur le donne (colonne « Degré de
  polyvalence », la lettre G ou H de la fiche de paie). Un toucher mène au
  recyclage. Le bloc « Polyvalence » de « Mes compteurs » les répétait : il
  part, avec ses styles (`.cpt-puces`, `.cpt-lien`). La classe `pf-poly`
  était déjà prise par l'ancien profil : la nouvelle s'appelle `pf-pv`,
  vérifiée libre avant l'emploi (leçon de la v822).
Vérifié à 320, 390 et 1280 px pour un contremaître (VBN, rien), un adjoint
(ATR, cinq ateliers) et un opérateur (PDE, trois, degré G), sans débordement
ni erreur ; vérificateur (calendrier, manques, polyvalence, compteurs 78/78)
et `comparer-fiches.py VBN` identiques à l'octet ; hors ligne.

**Les recyclages dans le héros** (le client, le 18/10/2026 : « pour ceux qui
ont des recyclages à faire, indiquer la progression et les compteurs dans
leur héros, tout près des polyvalences »), `nfdm-v824`. Dans le cadre
« Polyvalences », pour qui a un « restant » au classeur RH (sauf un
contremaître) :
- sur chaque puce, fait / objectif, par `polyvalenceDe()`, la lecture de
  l'onglet Recyclage, sans seconde copie de la règle ; au vert au quota, et
  aucune autre couleur (règle du 07/10). Un atelier exempté (le client,
  06-07/10) dit « exempté » au lieu de rester muet. Pour un adjoint, une
  puce « Contremaître », sur 5 ;
- dessous, la progression du classeur RH : la somme de ses recyclages
  faits, sur fait + SON « restant » (ATR 18 / 30, 12 à faire) ;
- posé après le premier affichage (`recyclageHeros()`, dans le même
  `plusTard` que « Mon année ») : `calculerPolyvalence()` rejoue l'année,
  et avait coûté 2,7 s au démarrage d'un téléphone lent. Le héros reste
  sous la seconde.
**Mesuré avant de choisir** : le « restant » du classeur égale la somme de
ce qui manque à chaque atelier pour 20 personnes sur 29, et pas pour 9
(DWS 17 contre 27, FLN 7 contre 22, PAM 18 contre 10…). « Fait +
restant » vaut 15 ou 20 pour cinq d'entre eux, là où l'application attend
30 ou 40 ; 30 pour PAM et VBN, 10 pour ASS et PDR. (Une première écriture,
corrigée avant de rendre la main, disait « 15 ou 20 » pour les neuf.) La
copie du classeur RH n'est pas dans le dépôt : impossible d'y lire la
largeur de leurs sections. Rien n'est deviné : chaque chiffre est montré tel
que le classeur le donne, et la question est posée
(`docs/questions-client.md`). Vérifié pour ATR (adjoint), FLN (deux
ateliers exemptés), PDE, ASS, VBN (contremaître, rien) et CWN (restant 0,
pas de progression), à 320, 390 et 1280 px ; vérificateur et fiches
identiques à l'octet ; hors ligne.

**Le jour d'une personne, et « Aujourd'hui » au calendrier** (le client, le
19/10/2026 à 0 h 16, capture à l'appui : « pourquoi je suis toujours sur
l'ancien cycle au lieu du nouveau qui commence aujourd'hui en nuit, alors
que je ne fais pas la nuit ? », puis « dans le calendrier il faut un bouton
pour revenir à aujourd'hui, le mois actuel ou l'année »), `nfdm-v825` :
- **le jour de l'usine** (`jourUsine()`, la veille jusqu'à 6 h, règle du
  27/09/2026 pour l'équipe de la nuit en cours) servait aussi au héros, à
  « Mon année », aux deux cycles, à la frise et aux dates des
  notifications. En repos le dimanche, VBN restait donc jusqu'à 6 h le
  lundi sur le cycle « 7 sept. – 18 oct. », pendant que le bloc du dessus
  annonçait déjà la nuit « d'aujourd'hui ». `jourPerso(p)` : avant 6 h, la
  veille ne dure que si la personne y tient encore son poste
  (`pfFin()`, une nuit finit à 30 h) ; sinon, c'est le jour du calendrier.
  Le Planning, les effectifs et les compteurs gardent le jour de l'usine.
  Éprouvé à heure simulée (Bruxelles, `page.clock`), sur la version d'avant
  et sur la nouvelle : VBN à 0 h 16, avant « 7 sept. – 18 oct. »,
  après « 19 oct. – 29 nov. », comme à 7 h ; LCI, de nuit le 18,
  « En poste, encore 5 h 45 » sur son cycle en cours, avant comme après ;
- **le bouton « Aujourd'hui »**, à côté de la bascule Mois | Année, du même
  gabarit. En Mois, il ramène au mois en cours et s'éteint quand on y est
  déjà ; en Année, il ramène à l'année en cours et fait défiler jusqu'au
  mois en cours, une fois l'année dessinée (`_anMontrer`, et non un délai
  fixe). Mesuré : depuis août, retour en octobre, bouton éteint ; depuis
  2027 en Année, retour en 2026, octobre à 16 px du haut sur téléphone et
  à 84 px au bureau, sous l'en-tête.
Vérifié à 320, 390 et 1280 px, sans débordement ni erreur ; vérificateur et
fiches identiques à l'octet ; hors ligne. **Erreur commise en testant** :
un `pkill -f "http.server 8766"` a tué le shell qui le lançait, sa propre
ligne de commande contenant le motif. Arrêter un serveur de test par son
PID, pas par un motif.

**Les badges de polyvalence, deux par deux** (le client, le 19/10/2026 :
« les badges doivent s'arranger pour occuper la largeur du cadre, 2 par 2
sur mobile »), `nfdm-v826`. Le cadre « Polyvalences » du héros passe d'une
rangée qui s'enroulait à une grille : deux colonnes égales sur téléphone,
trois au bureau, le nom à gauche et le compteur calé à droite. Mesuré à
320 px : un badge fait 115 px, et « Fermentation 1/5 », « Chaudières
5/10 », « Fermentation exempté », « Contremaître 5/5 » y étaient coupés.
Sous 361 px, les abréviations de l'onglet Recyclage (`PV_COURT` : Meun.,
Ferm., Chaud. ; « Contrem. ») prennent le relais, le nom entier restant
dans l'infobulle : plus aucune coupure. ATR : 2+2+2 badges de 150 px à
390, 3+3 de 137 px au bureau ; FLN : 2+2+1. Vérificateur et fiches
identiques à l'octet ; hors ligne.

**Le cycle actuel en pleine couleur** (le client, le 19/10/2026 à 0 h 28,
capture à l'appui : « le cycle actuel n'est pas bien visible comme le
prochain cycle »), `nfdm-v827`. Les jours à venir du cycle actuel étaient
estompés (`.cy-c.av`, opacité 0,42) ; au premier jour d'un cycle, tout
l'était donc, à côté d'un prochain cycle en pleine couleur. Estomper les
jours PASSÉS à la place aurait ramené le défaut en fin de cycle (à la
semaine 6/6, la capture du matin se lisait bien parce que tout y était
passé) : l'estompage part. Le jour cerclé de blanc et la semaine encadrée
disent où l'on en est, et le texte dessous compte les jours prestés et à
venir. Mesuré le 19/10 à 0 h 28 (heure simulée) : 0 case pâle sur 42
(VBN, ATR) et sur 35 (LCI), un jour cerclé et une semaine encadrée par
cycle actuel. Vérificateur et fiches identiques à l'octet ; hors ligne.

**La vue Semaine** (le client, le 19/10/2026 : « ajout d'une vue semaine en
plus de la vue mois et année »), `nfdm-v828`. La bascule devient Semaine |
Mois | Année. Une semaine n'a d'intérêt que si elle dit ce que le mois n'a
pas la place d'écrire : une ligne par jour, la case du mois à gauche
(`caseJour()`, la même, codes et marques compris), et à droite le jour en
toutes lettres, la pause et ses heures (« Nuit · 21 h 30-6 h »), l'atelier,
ou l'absence et son libellé (`libCompteur()`), puis le commentaire du
classeur sur deux lignes. Les heures et l'atelier sont ceux du héros et de
l'agenda (`lectureAgenda()` par `_pfJour()`). En tête, « Semaine 43 » et
le total : « 4 journées · 32 h ». La ligne du jour est mise en avant.
- La semaine va du lundi au dimanche. Le mois de son jeudi (la règle des
  semaines ISO) devient le mois de l'application : repasser en Mois
  retombe dessus. Une semaine à cheval relit ses deux mois comme l'Année
  (y compris l'écriture en attente) ; `avecJour()` bascule aussi l'année et
  `st.personD` pour une semaine qui déborde sur l'année suivante.
- Les flèches et le glissement vont d'une semaine à l'autre ; plancher : la
  semaine du 1er janvier 2026, dont les jours de 2025 sont grisés.
  « Aujourd'hui » ramène à la semaine en cours. Le sélecteur de mois mène à
  la semaine du 1er du mois choisi.
- Toucher une ligne ouvre la feuille du jour, mois et année chargés au
  besoin.
- Mesuré, le 19/10 à 10 h (heure simulée) : 19 – 25 oct., semaine 43 ;
  › › mène au 2 – 8 nov. ; « Aujourd'hui » ramène au 19 – 25 oct., éteint ;
  janvier donne « 29 déc. – 4 janv. », flèche ‹ éteinte, et un ‹ forcé ne
  bouge pas ; octobre donne « 28 sept. – 4 oct. » ; une ligne de
  septembre ouvre « Lundi 28 septembre », la semaine gardée.
- Trois boutons dans la bascule : à 320 px, « Semaine » dépassait d'un
  pixel (47 px de texte pour 46). Mesuré par la largeur réelle du texte
  (un `Range`), pas par `scrollWidth`, qui signalait les trois boutons
  « coupés » même à 1280 px : la marge passe à 2 px sous 361 px (47 pour
  50).
Vérifié à 320, 360, 390 et 1280 px, sans débordement ni erreur ; les vues
Mois et Année repassent leur scénario ; vérificateur et fiches identiques
à l'octet ; hors ligne.

Le même jour (le client : « nom du mois complet et les boutons plus proches
des bords gauche et droit »), `nfdm-v829` : l'étiquette de la semaine écrit
le mois en entier (« 19 – 25 octobre », « 28 septembre – 4 octobre ») ; les
flèches ‹ › passent de 26 à 12 px du bord intérieur du cadre (13 px du
bord mesurés), et la rangée Semaine | Mois | Année | Aujourd'hui s'aligne
sur elles. Mesuré à 320 px : la semaine à cheval tenait en 205 px pour 204
de place entre les flèches ; l'étiquette passe à 16 px sous 361 px
(188 px). Au bureau, la rangée garde 520 px au centre. Dans l'onglet de
la paie, qui partage la barre, le mois reste affiché.

Puis (le client : « les sélecteurs de date propres à chaque mode ne sont
pas adaptés ; en Année il propose aussi le mois »), `nfdm-v830`. Toucher
l'étiquette ouvrait toujours le champ « mois » natif. Chaque vue a
désormais le sien, posé au même endroit et seul visible : un mois en Mois
(`#moisPick`, inchangé) ; un JOUR en Semaine (`#semPick`, type « date »),
dont on affiche la semaine, faute de champ « semaine » sur iPhone ; une
liste d'années en Année (`#anPick`), d'AN_MIN à l'année suivante.
L'onglet de la paie garde le champ « mois ». Le glissement n'est pas
bloqué par un appui sur l'un des trois. Mesuré à 320 et 1280 px : le
3 décembre mène à « 30 novembre – 6 décembre », un jour de 2025 à la
première semaine de 2026, 2027 choisi à ses douze mois. Vérificateur et
fiches identiques à l'octet ; hors ligne. Vérificateur et fiches identiques à
l'octet ; hors ligne.

**Congé et maladie séparés, les couleurs des badges partout** (le client,
le 17/10/2026, capture de « Mon rythme » : « ne pas faire les congés et
maladies de la même manière ; dans le calendrier il faut que les couleurs
de pauses soient les mêmes que les badges »). Le calendrier du mois et
« Mon rythme » (barres, jour par jour, légendes) peignaient les pauses avec
`--am`, `--pm`, `--n`, `--d` (D gris), alors que les badges du héros, des
notifications et de la vue direction emploient `--cal-*` (D vert). Tout
passe à `--cal-*` : au calendrier du mois, la pause s'écrit dans une
pastille pleine sur un fond teinté de sa couleur. La maladie (un code de
la famille `SMG`, donc `MAL` et l'« Abs » du classeur) a désormais son
signe : hachures et contour rouges dans le jour par jour (`s-mal`), tirets
rouges et code rouge au calendrier du mois (`.mal`) ; le congé garde le
contour neutre. Légendes « Congé » et « Maladie » séparées. **Et le héros
plantait** pour qui n'a plus de week-end libre dans l'horaire (YBT, malade
jusqu'à la fin de l'année) : la case « Week-end libre » de la passe du
17/10 lisait `inf.weekend` sans garde, et tout l'Accueil restait vide. La
case se tait désormais. Aucune lecture touchée, neuf règles à zéro ;
vérifié sur LCI, YBT et VBN à 320 px (hors ligne), 390 et 1280 px, aucun
code ne déborde de sa case.

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
**C'était faux pour ces trois-là, et le client l'a tranché le 14/10/2026** :
« il y a bien rappel car il ne fait pas son horaire de D normal et il fait
plus de 8 h, et en plus il est indiqué rappel ». Le point D ne vaut que pour
une prestation tenue dans la pause AM : une journée de plus de 8 h, ou dont
des heures débordent (`rpp`, `hsp`), garde sa prime. JBI retrouve ses trois
primes, ATR le 09/03 (« 6h-17h · 3 HS rappel ») la sienne ; VGG, FPA et VBN
inchangés. Les cinq sorties du vérificateur et les agendas sont identiques
à l'octet (règle de paie seulement).

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

**Absents et congés : un seul cadre à deux onglets** (le client, le
10/10/2026, « optimise au max » sur cinq pistes proposées). Les deux
cadres empilés, Absents puis Congé et repos, répondaient à une seule
question — qui n'est pas là, et jusqu'à quand — et prenaient près de trois
écrans. Ils deviennent `#eqAbsCard` : titre « Absents et congés », les
onglets de la Recherche (`.caseg`) avec leur compte (« Absents 6 »,
« Congé et repos 40 »), l'onglet retenu par appareil (`ui/eqResteOnglet`),
et un sous-titre qui dit ce que la date veut dire (« malade · date de
retour », « date de reprise du travail »). Les mois se replient comme les
sous-effectifs (`mqMoisTete()`, compte de personnes à droite), le premier
ouvert ; « Sans date » passe en tête, hors des mois, au lieu d'être caché
sous la barre du menu ; les rangées se resserrent (date sur deux lignes
courtes, 5 px de marge). Mesuré à 390 px : Absents 411 px (environ
1 180 avant), Congé et repos 703 px (plus de 2 000 avant). Rien ne déborde
à 320 px (hors ligne), 390 et 1280 px ; onglets et dépli éprouvés, aucune
erreur.
Puis : « centrage des textes ? ne pas afficher ceux sans date ». Les
journées sans date de reprise (pas encore dans l'horaire, poste prévu non
presté) ne s'affichent plus et ne comptent plus dans l'onglet (40 → 38).
La date était plus haute que ses badges : elle gardait la marge basse de
11 px de `.mqd.eqproche`, retirée ici (écart mesuré 0 px). Le chevron d'un
mois replié se recentre sur celui d'un mois ouvert (`translateX(-2px)`,
tous les cadres repliables), le dernier intertitre perd son filet doublé,
et « Rien à signaler » se centre dans son cadre. Vérifié à 320 px (hors
ligne), 390 et 1280 px.

**Chaque cadre à sa place** (le client, le 10/10/2026 : « trouves-tu que
chaque cadre est bien dans son onglet ? », puis « tout »). Quatre
déplacements :

- le **relevé de prestations** quitte l'Accueil pour **Salaire**, sous
  « Contrôle de la vraie fiche » : on l'ouvre la feuille reçue au travail
  sous les yeux, comme la fiche. Replié par défaut, état retenu
  (`data-memo`) ;
- **Absents et congés** passe en tête d'Effectifs : il dit aujourd'hui, les
  sous-effectifs et les rappels les jours à venir ;
- **les codes** de l'Accueil restent en bas, repliés par défaut, état retenu
  (`#codesFold`) ;
- le bloc flex time des compteurs ne répète plus le solde en grand (le
  héros l'affiche juste au-dessus) : une ligne d'état, « Dans les bornes ·
  solde au 10/10 : 7 h », puis la jauge et les quatre chiffres.

Vérifié à 320 px (hors ligne), 390 et 1280 px : le relevé se remplit dans
Salaire (32 lignes en octobre), aucun débordement ni erreur.

**Les intitulés relus** (le client, le 10/10/2026 : « trouves-tu les
titres, intitulés, descriptions logiques avec le contenu ? », puis « oui,
fais-le »). Quatre défauts : un sous-titre qui redit le titre, du jargon,
une forme incohérente, des cadres voisins sans sous-titre. Changés :
« Mes compteurs » · classeur du… (sans le trigramme, déjà dans le héros) ;
« Mon rythme » · pauses, nuits et week-ends en 2026 ; « Récupération
d'heures supplémentaires » · compteur de récup. HS ; « journées lues dans
l'horaire » ; légende « Non payés » ; « Composition des équipes » ·
5 équipes · 62 personnes ; « Binômes contremaître · adjoint » · 6 binômes ;
« Opérateurs en formation » · 9 opérateurs ; « Du brut au net » · dans
l'ordre de la fiche ; « Saisies du mois » ; fiche simulée · telle que le
secrétariat social la calculerait ; « Comparer avec ma fiche » ; relevé ·
à comparer avec le relevé reçu ; « Absents, congés et repos » ;
sous-effectifs · 25 pauses d'ici le 31/12 ; Recherche · congé, absence ou
remplaçant pour un poste, son troisième onglet « Remplaçant » ; primes de
rappel · coefficients de la procédure de rappel. Les renvois du mode
d'emploi suivent. Vérifié à 320 px (hors ligne), 390 et 1280 px.

**« Chercher un remplaçant » retiré** (le client, le 10/10/2026 : « est-il
utile vu que les propositions sont déjà faites sous le sous-effectif ? »,
puis « oui »). Vérifié avant de le retirer : la fiche et l'onglet
Recherche appellent `caCandidats()` avec les mêmes arguments et
`caGroupes(t,true)` : mêmes cadres, mêmes noms. Le bouton, son écouteur,
ses styles et `ouvrirRecherche()`, qui ne servait qu'à lui, sont partis.
La ligne de date ouvre toujours le Planning de ce jour (`mqCible()`) ; le
soulignement du jour, seul indice, cède la place à un chevron au bout de
la ligne. Même demande, les majuscules et les retours à la ligne relus
sur les six onglets par un balayage au navigateur (textes courts sur
plusieurs lignes, intitulés en minuscule, unité mise en capitales par
`text-transform`) : aucun retour à la ligne parasite à 320 et 390 px ;
deux unités passaient en capitales, « PROLONGATION 12 H » et « DANS 2 J »
dans le héros — l'unité porte désormais `.unite`, hors capitales.
Vérifié à 320 px (hors ligne), 390 et 1280 px : la ligne de date mène au
Planning, le corps de la fiche n'y mène pas, aucune erreur.

**Une application, pas une page** (le client, le 10/10/2026 : « que
l'utilisateur ne pense pas à une page web ; un vrai « wow » de la
direction »). Premier lot, sans rien changer à la lecture :

- **le manifeste** nomme l'application « BIOWANZE · Mon équipe » et non plus
  un simulateur de paie, déclare un `id`, et porte **quatre raccourcis**
  (appui long sur l'icône) : Planning · Salaire · Effectifs · Recherche. Ils
  ouvrent `./?vue=…` ; le démarrage prend cet onglet avant `ui/view`, puis
  nettoie l'adresse (`history.replaceState`). Le titre iOS de l'écran
  d'accueil passe de « Ma paie » à « BIOWANZE » ;
- **installée** (`display-mode: standalone`), l'interface ne se sélectionne
  plus au doigt, l'appui long n'ouvre plus le menu « copier / ouvrir le
  lien » (les champs restent sélectionnables) et le rebond du défilement ne
  tire plus la page ;
- **une impulsion haptique** de 8 ms au changement d'onglet (`vibrer()`,
  Android seulement, coupée sous « réduire les animations ») ;
- **une carte « Installer l'application »** dans l'Accueil, dans le navigateur
  seulement : le bouton de l'invite du système sur Android
  (`beforeinstallprompt`), le geste « Partager → Sur l'écran d'accueil » sur
  iPhone ; la croix la masque pour de bon (`ui/installVu`) ;
- **« Hors ligne · données de l'appareil »**, une pastille en haut de
  l'écran tant que le réseau manque (`#horsLigne`).

Éprouvé à 320 px (hors ligne : la pastille paraît), 390 px en iPhone (la
carte, la croix) et 1280 px : `?vue=salaire` ouvre Salaire et l'adresse
redevient propre, rien ne déborde, aucune erreur. Chromium sans écran ne
déclenche pas `beforeinstallprompt` : seul un Android dira le bouton.

**Le « wow » : cinq pistes, toutes** (le client, le 10/10/2026 : « go tout
optimal ») :

- **l'écart avec le mois d'avant** sous les chiffres du mois de l'Accueil
  (prestées, jours, week-end, heures sup : « ▼ 54 vs sept. »). Il est relu
  par `netMoisPrecedent()`, le même `compute()`, et calculé une seule fois
  par calcul (`precDe()`), puisque le net du Salaire le lit aussi. Un mois
  d'avant jamais ouvert n'était pas stocké : il se lit désormais dans
  l'horaire par `remplirMois()`, sur une copie, sans rien enregistrer ;
- **« Mon année à ce jour »** en tête de Mon rythme (`ryAnneeHTML()`) : les
  journées prestées faites et à venir (barre), les nuits faites et à venir,
  le prochain congé posé (date, code, durée, dans combien de jours). Il est lu
  par `_pfJour()`, la lecture du héros, et calculé au repos. **Première
  version fausse** : le temps partiel de LCI passait pour son « prochain
  congé ». `estCongePose()` écarte la maladie, TP, CP, CT, la grève et le
  sans-solde ;
- **un onglet arrive du côté où il est dans le menu** (`de-d` / `de-g`,
  16 px), comme une application native. Le corps rogne le débord
  (`overflow-x:clip`, qui ne casse pas les en-têtes collants) ;
- **« Ajouter mes postes à mon agenda »** au pied du mois : un `.ics` des
  120 jours qui viennent (postes avec leurs heures, l'atelier écrit,
  « rappel » ; congés posés en journée entière). Chaque journée garde son
  identifiant (`TRI-AAAAMMJJ@biowanze`), si bien que réimporter met à jour
  au lieu de doubler. VBN : 84 événements ;
- **la vue direction** (Réglages → Vue direction, plein écran, Échap ou la
  croix pour fermer) : présents du jour sur l'effectif, maladie et son
  pourcentage, congés, pauses en sous-effectif d'ici le 31/12, les quatre
  pauses avec leur équipe, les sept jours qui viennent en barres (rouge les
  jours en sous-effectif), l'heure. Tout est relu par `equipeDuJour()` et
  `mqJoursAVenir()` : le 10/10, 32 présents sur 78, 10 · 10 · 12 par pause,
  6 malades (15,8 %), 25 pauses en sous-effectif, comme l'onglet Effectifs.

**Les squelettes de chargement ne sont pas faits** : l'écran d'intro couvre
déjà le chargement de l'horaire (1,7 s), et rien d'autre n'attend le réseau.
Les quatre sorties du vérificateur sont identiques à l'octet, la découpe de
`comparer-fiches` est à l'épreuve. Rien ne déborde et aucune erreur à 320 px
(hors ligne), 390 et 1280 px. Seul un téléphone dira comment l'agenda
importe le fichier.

**Toutes les pauses dans les statistiques, et plus de pause finie dans
les sous-effectifs** (le client, le 10/10/2026, capture de l'iPhone à
16 h 06 : « pourquoi les stats ne parlent que de nuit ? il faut voir aussi
les autres pauses ; une pause qui est terminée mais aujourd'hui ne doit
plus être visible dans les sous-effectifs »).

- **« Mon année à ce jour »** montre AM, PM, N et D, chacune avec ce qui
  est fait et ce qui reste à venir (VBN : 34 · 12 · 66 · 16, plus 7 · 7 ·
  19 · 13), puis le prochain congé. **Mon rythme** compare matins,
  après-midi, nuits, journées (D) et week-ends à la moyenne
  (`statsEquipe()` calcule les quatre). « Nuits par mois » devient
  **« Pauses par mois »**, une barre empilée aux couleurs du calendrier
  (`ryBarsPauses()`). La phrase du bas donne la part de chaque pause et le
  mois le plus chargé. « Nuits d'affilée » devient « jours de travail
  d'affilée ».
- **`statsRythme()` comptait les congés comme prestés** : un congé ou une
  maladie garde la pause PRÉVUE dans `rec.s`, à zéro heure, et passait le
  test. VBN : 264 journées « prestées » pour 174 réelles. Une journée
  compte désormais si elle a des heures, et elle compte à la pause TENUE
  (`postePeint()`, comme le héros et le calendrier). Le donut et
  « Mon année » donnent maintenant le même total : 41 + 19 + 85 + 29 = 174,
  soit 128 faites et 46 à venir.
- **Les sous-effectifs partent du jour de l'usine** (`jourUsine()`) et,
  ce jour-là, sautent les pauses déjà finies (`pausesFinies()`, `PF_FIN` :
  l'AM à 14 h, le PM à 22 h, la nuit à 6 h le lendemain). La clé du cache
  de `renderManques()` porte les pauses finies : le cadre se refait quand
  une pause se termine. La bulle et la vue direction suivent, puisqu'elles
  lisent `mqJoursAVenir()`. Mesuré horloge au 10/10 : à 10 h, 25 pauses,
  l'AM STEP du jour en tête ; à 16 h 06 et à 23 h, 24, le lundi 12 en tête.

Vérificateur identique à l'octet, découpe de `comparer-fiches` à l'épreuve
(il ne découpe ni `statsRythme()` ni `mqJoursAVenir()`). Rien ne déborde et
aucune erreur à 320 px (hors ligne), 390 et 1280 px.

**Les trigrammes sous leur type, et « En poste » seulement à deux** (le
client, le 10/10/2026, capture de l'iPhone). Une première version mettait
chaque type de solution sur une ligne, l'intitulé à gauche et les
trigrammes à droite (197 px au lieu de 330 pour la fiche du 12/10). Le
client : « j'aimais mieux les trigrammes sous le type de rappel » —
annulé, la colonne d'intitulés est partie. Ce qui reste :

- **« En poste » ne se montre que si le poste attend deux personnes ou
  plus** (« est-ce que le en poste est utile à part pour les postes avec
  minimum de 2 ? ») : à un seul attendu, il ne portait qu'un « ? », que le
  « 0/1 » de l'en-tête dit déjà. Au 10/10, 2 fiches sur 24 le gardent
  (N Chaud. 1/2) ; la Recherche garde le sien, qui dit qui tient le poste ;
- **l'horaire aligné sur le trigramme** dans les étiquettes (« ATA
  06-14 ») : centrés l'un sur l'autre, un mono de 11,5 px et un texte de
  10 px ne partageaient pas leur ligne d'écriture, et l'heure paraissait
  plus basse. Les deux se posent sur la même ligne de base, l'heure en
  mono ; « pour faire 06-18 » suit cette ligne, avec une espace devant
  l'horaire, que la règle `.cahr{margin:0}` collait au mot.

CSS et une condition : vérificateur identique à l'octet ; rien ne déborde
à 320 px (hors ligne), 390 et 1280 px.

**L'horaire et la pause hors du badge** (le client, le 10/10/2026 :
« l'horaire et la pause doivent être hors du trigramme »). Dans les
propositions de remplacement (sous-effectifs, Recherche, congé en heures),
le badge ne porte plus que le trigramme. L'horaire (« 06-14 ») ou la pause
et le poste (« PM Glut. ») le suivent à droite, sur sa ligne de base, en
mono gris (`caChip()` → `.mqcw` + `.mqch`). Les pistes des sous-effectifs,
qui écrivaient leur badge à la main, passent elles aussi par `caChip()`.
Mesuré : aucun `small` dans un badge, écart de ligne de base de 0 px ;
vérificateur identique à l'octet ; rien ne déborde à 320 px (hors ligne),
390 et 1280 px.

Puis, le même jour : « pour le sous-effectif on peut remettre juste
l'horaire dans le badge avec le trigramme ». Dans les sous-effectifs
seulement, un horaire seul (« ATA 06-14 ») revient dans le badge : `caChip()`
marque `.mqcw.hor` quand la mention est un horaire, et la feuille borde
l'ensemble sous `#mqCorps`. Une pause et un poste (« CWN PM Glut. ») restent
à côté, et la Recherche garde tout hors du badge. Même demande : le
sous-titre dit « 24 pauses jusqu'à la fin de l'année », l'intertitre du mois
« 5 pauses ». Vérificateur identique à l'octet ; rien ne déborde à 320 px
(hors ligne), 390 et 1280 px.

**« Rappels évitables »** (le client, le 10/10/2026, à la question de
l'intitulé : « Évitable »). « Rappels non nécessaires » jugeait le rappel ;
le cadre dit seulement que l'équipe aurait été complète sans lui, et un
rappel peut avoir une raison que le classeur n'écrit pas. Le titre et le
message vide changent ; `rappelsInutiles()` et les identifiants
(`#rnCorps`, `#rnSub`) gardent leur nom. Vérifié à 320 px (hors ligne),
390 et 1280 px.

**Le bureau** (le client, le 12/10/2026 : « le site est pas optimisé pc »,
capture d'une fenêtre de 1920 px à l'appui). La barre du haut tenait sur
deux lignes. Le tableau du jour faisait 330 px de haut au milieu d'un
écran vide, avec des badges de 11 px. Tout ce qui suit ne vaut qu'au-delà
de 1100 px, dans un bloc posé en fin de feuille :

- **Une barre d'application** : la marque à gauche, le jour derrière un
  filet, les onglets à droite, sur une seule ligne de 59 px. Ses bords
  intérieurs suivent la largeur du contenu (`--lw`) : le logo et le dernier
  onglet tombent sur les bords des cartes.
- **Le Planning remplit l'écran** : la carte va de sous la barre au bas de
  la fenêtre (`--jtop`, mesuré par `ajusterHauteurJour()`). Comme sur
  téléphone, `ajusterLignesJour()` partage la hauteur entre les lignes.
  Pauses en 16 px, postes en 13 px, badges en 13,5 px.
- **Plus large au-delà de 1600 px** : le contenu passe de 1 340 à 1 480 px.
- **Effectifs** : les fiches de sous-effectif s'affichent sur deux colonnes
  (une seule fiche de 660 px laissait la moitié du cadre vide). Les mois
  restent en travers. Absents, congés et repos passent aussi sur deux
  colonnes.

Rien ne change sous 1100 px : à 900 px la carte du Planning garde ses
340 px. Les quatre sorties du vérificateur sont identiques à l'octet
(`--polyvalence` comparé à `HEAD`, puisqu'elle dépend de la date du jour).
Rien ne déborde à 320 px (hors ligne), 390, 900, 1280 et 1920 px, aucune
erreur.

### Le verdict en bandeau, une capsule par remplaçant

Le client, le 13/10/2026, capture du Congé de PLZ le 30/10 : « comment
mieux présenter les remplaçants et leurs horaires prévus, et le badge
"possible" ». Le petit badge du verdict se perdait entre la date et le
poste, et la mention à côté d'un trigramme avait trois sens selon le cadre :
« PM » (d'où il vient), « 06-14 » (ce qu'on lui demanderait), « N
Adjoint ». Rien ne disait lequel.

- **Le verdict est un bandeau** de toute la largeur, avec un liseré et une
  icône cerclée à sa couleur : ✓ possible, ⇄ avec changement ou remplaçable,
  ✕ pas possible, – hors (`.catete .caverd`). Le bilan d'une période garde
  ses petits badges.
- **L'horaire à tenir s'écrit une fois**, en tête de la fiche, à côté de la
  pause (« Gluten · AM 06-14 · Éq. 5 », `caCreneau()`). Cela vaut pour
  les trois onglets de la Recherche et pour les sous-effectifs.
- **Chaque remplaçant est une capsule** « trigramme | ce qu'il a de prévu » :
  la pause en couleur du calendrier, son horaire, son poste s'il en change
  (« SVE | PM 14-22 Dist. », « VGG | D 7-15 », « ADK | Repos »,
  `caPrevu()`). Le D prend l'horaire que la personne écrit en D, sinon
  7-15. L'horaire de base des prolongations 12 h passe dans la même
  capsule (`caBase()`). « 06-14 » ne s'écrit donc plus à côté de qui vient
  du D (la règle du 30/09) : c'est l'horaire en tête de la fiche qui le dit.

Vérificateur à zéro (il ne découpe pas ces modules) ; rien ne déborde à 320
(hors ligne), 390 et 1280 px dans la Recherche et les sous-effectifs.

### « Horaire modifié », et les congés restants sous la semaine

Le client, le 13/10/2026, capture de l'Accueil : « optimise les
notifications personnelles, ça doit faire pro ; les soldes de congés
restants doivent être affichés sous le calendrier des 7 jours ».

- **La carte de notification** s'intitule « Horaire modifié · 6 journées ·
  classeur du 13/10 ». Chaque ligne est une grille fixe : la date courte
  sur deux étages (« 21 – 22 oct. », puis « mer. → jeu. · 2 j »,
  `dateCourteNotif()`), le changement calé à droite, un chevron. Avant, la
  date longue (« Du mercredi 21 octobre au jeudi 22 octobre ») passait à la
  ligne n'importe où et poussait le changement tantôt à droite, tantôt
  dessous. Le changement est en pastilles (`pastilleNotif()`) : la pause aux
  couleurs du calendrier, le reste à côté. L'avant est en contour gris
  pointillé, le texte barré. **La première version barrait une pastille
  pleine**, et le trait sur le fond coloré la rendait illisible.
- **Les congés restants** (`soldesConges()`, que l'état des compteurs
  emploie aussi) : une rangée « Congés restants » sous la semaine du héros,
  VA, RTT, DTT et RJF en jours de 8 h, en rouge sous zéro et pâle à zéro.
  Un appui mène aux compteurs. C'était l'inverse du 10/10 (« pas
  nécessairement les jours de congés restants ») : la demande du jour
  prime.

Compteurs du vérificateur identiques à l'octet ; neuf règles à zéro ; rien
ne déborde à 320 px (hors ligne), 390 et 1280 px, aucune erreur.

**Une ligne par journée, et le poste** (le client, le 13/10/2026 : « chaque
jour doit être sur une ligne, le titre du cadre « Mise à jour de votre
horaire » et cela doit également afficher le poste »). Le regroupement en
séries (`groupesNotif()`) est retiré : chaque journée modifiée a sa ligne
(`parJourNotif()`), sur l'Accueil comme dans la notification du téléphone
(trois journées puis « et n autres »). Le jour se lit en entier, abrégé
sous 380 px (« Ven. »). `descJourNotif()` écrit désormais le poste d'une
pause AM, PM ou N même quand la cellule ne le nomme pas : le poste attitré
de la personne ce jour-là (`posteAttitreLe()`), ou celui qu'elle apprend
si elle est en formation ; jamais le placement que le rééquilibrage tire
des absences des autres. **Changer cette description aurait annoncé toute
l'année comme modifiée** : l'instantané porte `NOTIF_VERSION` (2), et une
autre version se rephotographie sans rien signaler. Éprouvé : VBN avec un
instantané v1, aucune carte ; avec un instantané v2 truqué, « Repos → N ·
Contremaître », GJR « → PM · Chaudières », LCI « → N · Distillation ».
Rien ne déborde à 320 px (hors ligne), 390 et 1280 px.

**Les badges aux couleurs de la pause, les jours comme aux sous-effectifs**
(le client, le même jour). Tout le badge prend la couleur de sa pause,
celle du calendrier : fond doux, filet et pastille pleine. L'ancien état
garde sa couleur, pâli, en pointillé, avec le texte barré. La date se lit
par `dateEnMots()`, comme aux sous-effectifs : « Aujourd'hui », « Demain »,
puis le jour en entier, et « 16 octobre » dessous (`dateCourteNotif()`
est retiré). La ligne ne passe plus jamais à la ligne. Sous 380 px, le
poste s'abrège (« CM », « Chaud. ») : en entier, il se coupait en
« Contrem… ». Vérifié à 320 px (hors ligne), 390 et 1280 px.

**Et le commentaire de la journée** (le client, le même jour : « s'il y a un
commentaire dans le changement il faut l'afficher ») : sous la ligne, dans
un encadré à filet cyan, celui de l'horaire installé (« remplace ATA »,
« échange avec ATA ») ; il dit pourquoi la journée a changé. La
notification du téléphone le cite entre guillemets. Vérifié sur VBN à
320 px (hors ligne), 390 et 1280 px.

**Majuscule en tête du commentaire, et trois finitions** (le client, le
même jour : « mettre des majuscules dans les commentaires ; est-ce pro à
100 % ? »). `comNotif()` met la majuscule à la première lettre
(« Échange avec GPS »), sur l'Accueil comme dans la notification du
téléphone. Relu sur sa capture : « Voir les 1 autre » devient « Voir
l'autre journée » (« Voir les 2 autres journées » au pluriel). Une ancienne
pause écrite seule (« PM → N ») avait l'air d'un état présent : elle est
pâlie, en pointillé et barrée, comme l'ancien libellé. Vérifié à 320 px
(hors ligne), 390 et 1280 px.

**Le poste n'est plus écrit pour un contremaître ou un adjoint** (le
client, le même jour : « ok pour les CM ») : leur fonction ne change
jamais, la répéter sur chaque ligne n'apprenait rien. Seul l'atelier d'un
opérateur s'écrit. `NOTIF_VERSION` passe à 3.

### L'abonnement à l'agenda

Le client, le 13/10/2026, capture de son abonnement « Jours fériés
belges » : « est-ce possible de créer un fichier qui s'ajoute comme cela ? »,
puis « adresse trigramme pour l'agenda ». **Un fichier par personne,
`cal/<id>.ics`** (`cal/GBT-1.ics` pour le second GBT), servi par GitHub
Pages. Le téléphone s'y abonne une fois et le relit seul : une journée
modifiée est corrigée, une journée devenue repos disparaît. Le délai est
celui du téléphone (iPhone : Réglages → Calendrier → Comptes → Récupérer ;
Google, jusqu'à un jour). Le fichier demande une heure
(`REFRESH-INTERVAL`), sans garantie que l'agenda la respecte.

- **Écrit par `node tools/verifier-calendrier.js --agendas cal`**, avec
  `icsAgenda()` découpée dans `index.html` : il n'existe pas de seconde
  copie. `lectureAgenda()` est la
  lecture du héros, sortie de `_pfJour()` pour pouvoir être découpée.
  `horaireDe()` et `calageLong()` entrent dans la découpe : les fichiers
  vont du 1er janvier de l'année du classeur au **31 décembre de la
  suivante** (le client, le 14/10/2026 : « jusque fin décembre 2027 » ; le
  30 juin d'abord), par les cycles prolongés (SLI ne l'est pas). 78
  fichiers, 36 344 événements, 16 Mo ; l'extension n'a fait qu'ajouter des
  lignes, aucune de 2026 ne bouge.
- **`mettre-a-jour.py --installer` les réécrit** sur l'horaire installé.
  L'horodatage est celui du classeur, si bien qu'un horaire inchangé donne
  des fichiers identiques à l'octet, et les fichiers d'une personne partie
  sont retirés. **Après une modification de la lecture dans `index.html`,
  relancer la commande** et committer ce qui bouge.
- **Contenu** : poste et heures (fuseau de Bruxelles déclaré), atelier
  écrit, « rappel » ; « Formation ». Les congés en sont retirés depuis le
  14/10/2026 (voir plus bas).
  Aucun nom. **« Ni commentaire » était vrai jusqu'au 14/10/2026** : voir
  plus bas, le commentaire est désormais dans la note. **Deux défauts de l'ancien export trouvés en
  relisant les 26 674 événements** : une journée entière « 8h +FT » (poste
  tenu, heures au compteur) s'écrivait « Congé +FT » — c'est désormais le
  poste ; un ±FT sur un repos (« presté le 28.02 », un renvoi) donnait un
  « Congé -FT » — il ne donne plus rien ; le code de formation s'écrit
  « Formation », et non plus comme un congé.
- **Le bouton** « S'abonner à mon horaire » ouvre `webcal://…/cal/<id>.ics`
  sur un iPhone, un iPad ou un Mac ; ailleurs, la page d'ajout de l'agenda
  de Google (l'application Android ne sait pas s'abonner, il faut le site).
  Le service worker ne met jamais `cal/` en cache. **Le seul bouton**
  (le client, le même jour : « il ne faut que le bouton abonnement ») :
  « Copier l'adresse » et « Télécharger une fois » sont retirés, avec
  `exporterAgenda()` — un fichier téléchargé ne se met jamais à jour.
- **Public, et c'est la décision du client** : chacun peut lire l'horaire
  d'un collègue à son trigramme, comme il le peut déjà dans
  `data/horaire-2026.json`. Une adresse avec un jeton par personne était
  l'autre option, écartée.

**« Roue libre »** (le client, le 14/10/2026 : « pour un adjoint, il faut
préciser dans l'agenda "Roue libre" quand il ne remplace à aucun poste ce
jour-là »). `lectureAgenda()` pose `roue` pour un adjoint (`estCadre` sans
`estContremaitre`) présent à une pause AM, PM ou N, sans « R-CM », sans
atelier écrit et sans remplacement en commentaire ; l'événement s'intitule
« N · Roue libre ». En 2026 : ATR 27, FPA 18, JBI 36, VGG 31 journées ;
les journées projetées par les cycles (2027) n'ont pas de commentaire et
le sont toutes.

**Les jours de travail seulement, et chacun avec son poste** (le client,
le 14/10/2026 : « il ne faut pas afficher les congés dans l'agenda » ;
« des jours sont sans rien », sur l'agenda d'ATR). Les congés (VA, RTT,
RJF, DTT, RHS, -FT…) ne donnent plus d'événement ; la formation reste,
c'est une journée de travail. 36 344 → **33 427 événements**. Le poste de
l'agenda (`x.ka`, `lectureAgenda()`) : l'atelier écrit ; sinon, pour un
adjoint, « Contremaître » si « R-CM » est écrit, et le poste du remplacé
pour un « remplace X » d'une journée entière (`atelierDuRemplace()`, la
lecture du Planning ; pas un remplacement de quelques heures,
`remplPartiel()`) ; pour un opérateur, son poste habituel ce jour-là
(`posteAttitreLe()`, ou celui qu'il apprend), comme les notifications.
Les contremaîtres gardent la pause seule. ATR passe de 98 journées sans
poste à **4** (des remplacements de quelques heures, des évaluations) ;
LCI lit la fermentation jusqu'au 29/09 et la distillation ensuite, SKS le
terrain arrière jusqu'au 20/09. **Premier essai faux** : le jour passé en
`Date` au lieu du nombre AAAAMMJJ que `_posteDePeriode()` attend, et LCI
était en distillation toute l'année. Les quatre sorties du vérificateur
sont identiques à l'octet (agenda seulement).

**L'horaire que le commentaire écrit** (le client, le 14/10/2026 : « si
le commentaire précise l'horaire, il faut adapter cet horaire au
commentaire », ATR le 16/10, « ATEX … de 08h30' à 16h30' », que l'agenda
mettait en 7-15). `lectureAgenda()` pose `hd` et `hf`, lus par
`pfDebut()` et `pfFin()` dans l'agenda et dans le bloc du prochain poste
de l'Accueil : une journée de jour (D, formation) qui écrit une plage de
4 à 12 h la prend ; « arrivée à 9h » et « départ à 15h » valent pour toute
journée prestée, s'ils tombent près de la pause (une heure avant 6 h est du
lendemain : « arrivée à 01h00' » d'une nuit). Sur une pause, « de 20h à
22h » dit un remplacement de quelques heures et ne compte pas ; « remplace
X … départ à » sans rien de posé ce jour-là, c'est X qui part (la garde du
départ anticipé du 29/09). **La plage de la cellule, écartée d'abord, est
lue depuis** (le client, le même jour : « NPE fait 6-10 et QBY 10-22 » ;
QBY écrit `["10h-22h","4h +FT","… remplace NPE de 10h à 14h"]` et
l'agenda le mettait en 14-22). Elle donne `hd`/`hf`, 12 h comprises, et
le commentaire l'affine ensuite ; l'annotation passe avant la cellule
quand elle écrit une plage (YPE le 30/03, « 7h-15h · 6h-14h ») ; elle ne
compte pas avec un code de jour (F, CPPT, DS… : elle n'y est que la pause
prévue) ni quand l'annotation écrit une pause (« 7h-15h · AM »). **198
événements** de plus changent : les 12 h « 06h-18h » affichées 05h30-14,
les « 18h-06h » affichées 21h30-06 ou 22-06, les 10-22, 14-02, 22-10 et
02-14 des relais. **613 événements** changent
d'heure sur 2026-2027, relus par échantillon : départs avec RTT, −FT, ½ VA
ou RHS (06-10, 06-12, 14-18…), arrivées tardives, les 21 formations
datées (08h30-16h30, 09h-17h). Les quatre sorties du vérificateur sont
identiques à l'octet (agenda seulement).

**Une plage collée à la pause la prolonge, et le Planning l'écrit** (le
client, le 14/10/2026 : ATR le 31/10, `["chaudières","3h +FT","remplace
PDF remplace FPA de 22h à 01h00'"]`, fait 14-22 puis 22-01, et l'agenda le
laissait en 14-22 ; « quand un horaire est diminué ou prolongé, comme QBY et
NPE, il faut écrire l'horaire dans la bulle du trigramme »). Sur une pause,
une plage « de X à Y » DANS la pause reste un remplacement de quelques
heures ; une plage qui COMMENCE à la fin de la pause, ou FINIT à son début
(4 h au plus), la prolonge (`lectureAgenda()`, `hd`/`hf`). Pas au passif :
« Remplacé de 14h à 18h par AAI » (BBZ le 09/07, GBT les 21-22/03) dit que
l'autre vient — les trois faux de la première mesure. **71 événements** de
l'agenda changent, relus un par un (22-24, 22-01, 20-22, 12-14…). Au
Planning, un badge de pause dont l'horaire diffère de la pause porte cet
horaire, le même que l'agenda et l'Accueil (`horaireModifie()`) : le 18/10
« NPE 6-10 », « QBY 10-22 » ; le 31/10 « ATR 14-1 », « FPA 1-6 ». Vérifié à
320 px (hors ligne), 390 et 1280 px, aucun badge hors de sa case ; les
quatre sorties du vérificateur identiques à l'octet.

**Un congé porte son seul code** (le client, le même jour : « RJF au
lieu de Congé RJF ») : « VA », « RJF », « RTT », comme dans l'horaire.

**Le flex time repris est un congé** (le client, le même jour : « le
flextime est bien un congé quand on le reprend »). Une journée entière
« 8h -FT » sur un poste prévu s'affichait encore comme le poste (« N »)
dans l'agenda et dans la semaine du héros : ses heures sont payées depuis
le compteur, mais personne ne vient. `lectureAgenda()` ne compte plus que
les heures PRÉSENTES, comme `equipeDuJour()` : la journée devient le congé
« -FT », en journée entière. **236 journées** de l'agenda changent ; un
±FT sur un repos (un renvoi) reste sans événement. L'intitulé « Congés
restants », avec la tuile FT, reste tel quel.

Vérifié à 320 px (hors ligne), 390 et 1280 px : téléchargement (79
événements pour VBN), adresse d'abonnement, rien ne déborde. **Seul un
téléphone dira comment l'abonnement s'affiche.**

**Partager l'abonnement à un collègue** (le client, le 14/10/2026 : un
lien `webcal://…/cal/ATR.ics` envoyé à un collègue ouvrait, chez lui, une
RECHERCHE de ce texte dans son agenda). Beaucoup de messageries ne
prennent pas `webcal://` pour un lien. On partage donc un lien `https`
ordinaire, **`agenda.html?id=TRI`**, que toutes rendent cliquable : la
page dit de qui est l'horaire et lance la bonne méthode selon le
téléphone qui l'ouvre (`webcal://` sur Apple, la page d'ajout de Google
ailleurs), avec « Copier l'adresse » et la marche à suivre à la main ; un
navigateur intégré (WhatsApp, Messenger) est invité à passer par Safari ;
un trigramme sans fichier se dit (« Aucun horaire n'est publié »). Dans
l'application, « Partager le lien » sous « S'abonner » ouvre le menu de
partage du téléphone (`navigator.share`), sinon copie le lien. Vérifié à
la largeur d'un iPhone, d'un Pixel, à 1280 px et dans l'application à
320 px hors ligne. Seul un vrai téléphone dira si la messagerie de chacun
laisse passer.

**Le vrai téléphone l'a dit** (le client, le 19/10/2026 : « j'ai partagé le
lien à mon épouse ; chez moi cela ouvre bien l'ajout dans le calendrier,
mais chez elle rien ne se passe avec le lien partagé dans Messenger »). Le
lien s'ouvrait, mais dans le navigateur INTÉGRÉ de Messenger, qui bloque
`webcal://` sur iPhone et ne connaît pas le compte Google sur Android : le
bouton « S'abonner » n'y faisait rien. L'invitation à « passer par
Safari » n'était qu'une ligne d'aide sous ce bouton, et seulement sur
iPhone ; sur Android, rien. `agenda.html` :
- reconnaît aussi Messenger sur Android (« Orca », « FB_IAB »), Snapchat,
  TikTok, X ;
- dans une messagerie, une **étape 1** encadrée : « Messenger ouvre les
  liens dans sa propre fenêtre, qui ne sait pas ajouter un agenda », un
  bouton « Ouvrir dans Safari » (`x-safari-https://`, iOS 17 et
  suivants) ou « Ouvrir dans le navigateur » (un lien `intent://` sur
  Android), et le menu ⋯ / ⋮ en secours ; puis l'étape 2, « S'abonner » ;
- **plus de silence** : si « S'abonner » n'a rien ouvert au bout de 2,5 s
  (ni perte de focus, ni page cachée), un encadré le dit et la marche à
  suivre à la main s'ouvre.
Vérifié en imitant quatre navigateurs (Messenger sur iPhone et sur
Android ; Safari ; Chrome) :
l'étape 1 n'apparaît que dans Messenger, avec le bon bouton ; l'aide suit
un toucher resté sans effet. **Ce que seul un téléphone dira** : si
Messenger laisse passer `x-safari-https://` et `intent://`. S'ils sont
bloqués, le menu ⋯ / ⋮ reste écrit sous le bouton.

**Le commentaire, l'adresse et la remise de pause** (le client, le
14/10/2026). Trois ajouts aux événements de `icsAgenda()` :

- **la note** (`DESCRIPTION`) porte le commentaire de la journée, tel que
  `data/horaire-2026.json` le publie déjà, majuscule en tête ;
- **le lieu** de chaque poste presté est l'usine, « BioWanze s.a. »,
  Rue Léon Charlier 11, 4520 Wanze. « Rue Léon » et « Wanze, Belgique » sont
  admis dans `tools/formes-admises.txt` : c'est une adresse. **Le texte
  seul ne suffisait pas**, et la capture du client le montrait : l'iPhone
  géocodait l'adresse lui-même, posait l'épingle sur une maison voisine et
  écrivait le lieu en blanc, là où une entrée choisie dans Plans s'écrit
  en rouge. Le client, le même jour : « pourquoi le lieu n'est pas indiqué
  en rouge comme une entrée manuelle ? ». `icsLieu()` donne donc un lieu
  STRUCTURÉ : `LOCATION` (nom puis adresse), `X-APPLE-STRUCTURED-LOCATION`
  (nom, adresse, coordonnées) et `GEO` pour les autres agendas. Les
  coordonnées sont celles du site dans OpenStreetMap (zone industrielle
  « BioWanze S.A. », 50,531149 · 5,207899). Le lieu s'écrit désormais en
  rouge et Plans pose l'épingle au bon endroit (le client, le 14/10/2026).
  **Mais l'aperçu de carte dans l'événement était trop serré** : avec un
  rayon (`X-APPLE-RADIUS`) de 150 m, il ne montrait que quelques bâtiments,
  sans rue ni repère, là où l'entrée choisie à la main cadre le site et sa
  route. Le rayon passe à 500 m, avec `X-APPLE-REFERENCEFRAME=1` comme
  l'écrit l'agenda d'Apple lui-même. Seul l'iPhone dira si le cadrage
  convient. **Le cadrage ne suffisait pas** : le client, le
  14/10/2026, deux cartes côte à côte, « la meilleure est la plus
  complète ». Une entrée choisie dans Plans porte l'identifiant de la
  fiche du lieu chez Apple (`X-APPLE-MAPKIT-HANDLE`), qui donne nom, photo
  et itinéraire ; aucun texte ne le reconstitue. Le client s'est envoyé
  une invitation iCloud avec ce lieu, et le `.eml` a donné la ligne :
  l'identifiant (`ICS_MAPKIT`, il ne contient que pays, province,
  commune, rue et nom du lieu), le rayon (172,93 m) et les coordonnées
  qu’Apple y écrit (50,531912 · 5,206511) sont repris tels
  quels. La fiche Apple dit « 18 » ; le texte du lieu garde le n° 11.
  Rien d'autre de l'invitation n'est recopié (adresse mail, nom). Seul
  l'iPhone dira si l'aperçu est désormais celui de l'entrée manuelle. **L'adresse est bien le n° 11** (le client, le 14/10/2026,
  alors que Plans d'Apple écrit 18) ;
- **le contremaître DE LA PAUSE**, et l'adjoint qui le remplace (« R-CM »
  écrit, le client : « oui »), commence 30 min avant pour la remise :
  05h30-14, 13h30-22, 21h30-06. Jamais en D, et **pas un contremaître en
  surplus** (le client : « cela dépend si le contremaître est celui de la
  pause, pas un contremaître en D qui fait 6-14 en surplus »).
  `lectureAgenda()` pose `remise` : il est celui de la pause si la cellule
  franche écrit cette pause (ou une autre, l'annotation celle-ci : il a
  changé de pause), si son cycle la lui donne, ou si le commentaire dit un
  remplacement, un échange, une inversion ou un rappel. **Ma première règle
  oubliait « Remplacement ATA », « pour remplacer YBT », « inversion avec
  AFA » et les journées entières versées au flex time** : 54 journées
  revenaient à l'heure de la pause, 17 après correction, toutes un D ou un
  repos sans remplacement (FLI le 13/10, « D · 6h-14h », l'exemple même
  du client ; YPE du 30/03 au 01/04 ; les deux SD26 de GPS). Cette
  demi-heure ne compte pas dans les 12 h de la journée. L'Accueil la montre
  aussi (`pfDebut()`, `pfHeures()`) : VBN le 15/10 au soir, « Reprise ·
  Demain · 5 h 30-14 h », le 16/10 à 7 h « En poste · Fin à 14 h ».

Le texte s'échappe (virgule, point-virgule, saut de ligne : `icsTexte()`)
et toute ligne de plus de 75 octets se plie (`icsPlier()`, RFC 5545) :
mesuré, aucune ligne des 78 fichiers ne dépasse 75 octets. Le
vérificateur découpe les deux fonctions et `ICS_LIEU`. ATR le 25/10 :
13h30-22, « Remplace AFA » ; un opérateur garde 6 h, 14 h, 22 h. Les
quatre sorties du vérificateur (dont `--placement --tout`) sont
identiques à l'octet ; rien ne déborde à 320 px (hors ligne), 390 et
1280 px.

**Le solde flex time rangé avec les congés restants** (le client, le
13/10/2026 : « le solde flex time doit être affiché comme les autres congés
sous le calendrier 7 jours »). Une tuile « FT » au bout de la rangée, en
heures (« +7 h »), vert dans les bornes, jaune au-dessus de 80 h, rouge
au-delà de 104 h ou sous −8 h ; le pied du héros ne garde que
le week-end libre lointain. Vérifié à 320 px (hors ligne), 390 et 1280 px.

**L'ancienne pause n'est plus barrée ni pâlie** (le client, le même jour :
« il ne faut pas barrer ni diminuer la visibilité du badge de la pause qui
était prévue avant le changement »). L'avant s'écrit comme l'après, en
pleine couleur ; la flèche seule dit le sens (« PM → N »). Les règles
`.nt-e.av` sont retirées. Vérifié à 320 px (hors ligne), 390 et 1280 px.

### Les changements de poste faits par l'application, à prévenir

Le client, le 13/10/2026, sur PDF mis à la STEP le 14/10 (CAN en RJF, PDE
malade, cellule `["6h-14h"]` sans atelier écrit) : « si c'est l'application
qui fait le transfert de poste il faut pouvoir le savoir et le différencier,
car nous devons avertir PDF qu'il devra s'y rendre », puis « ok go » sur
trois propositions. `transfertApp()` reconnaît un transfert : quelqu'un que
le rééquilibrage a placé (`comble` ou `deduit`) à un autre poste que son
poste habituel du jour (`posteAttitreLe()`, ou celui qu'il apprend s'il est
en formation), jamais ce que la cellule ou un commentaire écrit, ni la
consignation venue du D. La raison se lit au poste d'arrivée
(`aRemplacer()`).

- **Planning** : badge à bord orange en pointillé, « ↪ » devant le
  trigramme ; au clic, « Proposé par l'application : Chaudières → STEP
  (PDE absent · CAN en RJF). À confirmer avec PDF. », puis le commentaire du
  classeur s'il y en a un.
- **Effectifs** : cadre « Changements de poste à prévenir », sept jours
  (`transfertsAVenir()`, mémoïsée par jour de l'usine et par classeur, sans
  les pauses finies), une ligne par transfert ; une bulle orange sur
  l'onglet, à côté de la rouge des sous-effectifs.
- **Accueil de la personne** : la journée de la semaine porte « ↪ STEP »
  cerclé d'orange, le bloc du prochain poste aussi, et une ligne sous la
  semaine : « Demain : STEP au lieu de Chaudières · proposé par
  l'application, à confirmer ». Calculé 60 ms après le premier affichage.

**L'application ne sait pas si la personne a été prévenue** : la marque
reste jusqu'à ce que le classeur écrive le transfert (cellule ou
commentaire : la cellule fixe alors le poste) ou que la journée passe. CAN
annulera ses congés des 13 et 14/10 : au classeur suivant, PDF retourne aux
chaudières de lui-même. Mesuré le 13/10 : 7 transferts, 5 personnes (PDF
14-16/10 à la STEP, GPO 15/10 Gluten → Fermentation ; AAI 15/10 Distillation
→ Terrain arrière, LHR et PLZ le 18/10). Aucune lecture touchée : neuf
règles à zéro, découpe de `comparer-fiches` à l'épreuve. Vérifié à 320 px
(hors ligne), 390 et 1280 px, sans débordement ni erreur.

**Sans flèche, et chaque changement dit qui il remplace** (le client, le
même jour : « retirer la flèche ; mieux présenter ce nouveau cadre et dire
pourquoi ils doivent être changés de poste, donc qui il faut remplacer »).
Le « ↪ » est retiré partout : le bord orange en pointillé suffit. Le cadre
d'Effectifs prend les cartes des sous-effectifs : la date en en-tête avec
« n changements », puis par changement le poste d'arrivée et sa pause
(« STEP · AM 06-14 · Éq. 4 »), un cadre « À prévenir » (« PDF | Chaud. →
STEP ») et un cadre « Remplace » rouge (« PDE Absent · CAN RJF »).
`raisonsTransfert()` cherche, dans l'ordre : ceux prévus au poste et
absents (`aRemplacer()`) ; en cascade, celui qu'il relaie
(`x.relaie`, posé par `reequilibrer()`) ; le titulaire du poste placé
ailleurs (« PLZ passé en Ferm. ») ; le renfort du terrain arrière
(`x.renfortTerr` : « Renfort : Distillation en surnombre ») ; sinon
« Place sans titulaire dans l'équipe » (GPO le 15/10, la place de
fermentation vacante de l'équipe 4). La même raison est dans
l'explication du badge au Planning et sous la semaine du héros. Les deux
drapeaux ne changent aucun placement : les cinq sorties du vérificateur
(dont `--placement --tout`) sont identiques à l'octet. Vérifié à 320 px
(hors ligne), 390 et 1280 px.

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


