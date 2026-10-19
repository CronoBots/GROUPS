# Ce qui attend le client

Questions ouvertes au client et à la RH. Quand il répond : on applique, on mesure, on barre la question ici et on note la réponse dans le journal.

### Ce qui attend le client

L'audit a trouvé des informations que le classeur porte et que l'application
ne sait pas encore interpréter. **Elles sont toutes dans le brut**, et rien
n'est deviné à leur sujet :

- ~~les lettres G et H~~ du degré de polyvalence — la fiche d'ouvrier
  porte une « Classification entreprise » qui commence par la même lettre.
  Tranché le 14/10/2026, le client : « c'est le degré de polyvalence mais
  ça ne change rien du tout ». Rien à coder ;
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
    veille `AM · VM` — l'heure de visite médicale hors horaire ? Le
    client, le 14/10/2026 : « je vérifierai » ;
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
    ci-dessous, inchangée. Le reste : le rappel du 25/06 (tranché le 14/10/2026 : flex time écrit le lendemain) ;
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
  - **les évolutions de la rémunération fixe** (le client, le 14/10/2026 :
    « prends en compte les indexations et augmentations salariales suite à
    mon changement de fonction ») : réglage personnel `remHist`, une ligne
    par changement (date d'effet, montant), lu par `remFixeDuMois()` dans
    `compute()`. Éprouvé sur les neuf mois de VBN avec un seul jeu de
    réglages : brut, net et montant des heures prestées identiques au
    centime à ceux obtenus en saisissant le fixe de chaque fiche à la main.
    Saisie vérifiée à 320 px (hors ligne), 390 et 1280 px ; vérificateur
    identique à l'octet. L'exemple de l'aide est neutre : la première
    version recopiait un vrai montant, retiré avant le commit. Reste le
    rappel d'une hausse en cours de mois (question de la date d'effet) ;
  - **le salaire de VBN remesuré le 14/10/2026**, janvier à septembre,
    sans calage (rémunération fixe et taux d'indemnité de chaque fiche, le
    reste de ses réglages ; montants dans le scratchpad, jamais ici).
    Juin et août tombent au centime une fois retirées les rubriques que
    l'application ne simule pas, et février à quelques euros près :
    « Recup à payer » (février), simple et double pécule de vacances (mai),
    treizième mois (juin), avantage non récurrent (août). Les autres mois,
    chaque reste a sa cause, toutes déjà connues : le férié de l'employé
    (100 % sur la fiche, 200 % dans l'application : janvier, avril, mai),
    les heures sup du shut-down payées « pas compenser » (mars), l'arrivée
    tardive du 30/07 (juillet) ; en septembre toutes les lignes concordent
    sauf deux, le rappel de la hausse sur le fixe et les primes diverses,
    deux questions déjà posées ;
  - restes connus du rapprochement de LCI, sans question posée : le 13/04
    (cellule `N`, payé 12 h sup) ; ~~la prime de rappel du 20/03~~, résolue
    le 14/10/2026 (prime de l'après-midi, la pause des heures ajoutées) ;
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
    une demi-quinzaine d'août. Hypothèse à faire confirmer. Le client,
    le 14/10/2026 : nommé le **15/09** (le classeur écrit « CM » ce
    jour-là). La fiche le contredit : nouveau taux horaire dès les 05 et
    06/09, septembre entier au nouveau fixe et la demi-hausse en plus,
    soit un effet au 15/08. **Tranché le 14/10/2026** : effet au 15/09,
    « le RH a fait une erreur ». La fiche paie trop, à signaler à la RH
    (détail dans `docs/regles-paie.md`). Le partage d'un mois où le fixe
    change (les deux fixes, selon quelle clé ?) passe à la RH ;
  - le 30/09, `["D-CPPT","2h RTT","+1h RHS compteur à 0 Arrivée à 09h
    Départ à 15h"]` : la fiche paie la prime du **matin** pour les 6 h
    (38 h de matin contre 32 h, 64 h de nuit contre 70 h). L'application
    garde la prime de nuit de la pause prévue, puisque le commentaire
    n'en nomme aucune. Ma règle du 30/09 « celle de la pause prévue
    sinon » est donc démentie par la fiche. **Tranché le 14/10/2026**,
    voir « Les états de présence SAP » ;
  - le même jour, la fiche paie **0 h 30** d'heures sup à compenser.
    L'application en payait 1 h, à la prime de nuit, comme le client l'a
    dit le 01/10 (« + 1 h sup faite après 15 h »). **Tranché le
    14/10/2026** : 0,5 h sans prime ;
  - les primes diverses : la fiche porte bien plus que les 4 primes de
    remplacement de contremaître (R-CM des 01, 07, 08 et 09/09), et le
    reste ne correspond pas à un nombre entier de primes. **Répondu le
    14/10/2026** : ce reste est la moitié de la prime mensuelle de remise
    de pause (nommé le 15/09). Elle est payée dans « Primes Diverses »,
    partagée par quinzaine. Voir `docs/regles-paie.md`, « La prime de
    remise de pause » ;
  - indemnités : 17 jours sur la fiche contre 18 dans l'application,
    plus une ligne « Indemn. déplacement/vélo ». **Répondu le
    14/10/2026** : un jour venu à vélo, qui ne donne pas l'indemnité
    voiture (18 − 1 = 17). L'application le fait déjà : la journée
    marquée « Vélo » sort des jours d'indemnité et compte
    2 × la distance en km vélo. Rien à coder, il suffit de marquer le jour.
- **la paie de l'ouvrier** (09/10/2026, voir « La paie à l'heure de LCI,
  revérifiée ») : ~~réduction du temps de travail non payée~~ — tranché
  par la note explicative de la fiche de paie (« non payé pour les
  ouvriers »), appliqué le 09/10/2026, voir `docs/regles-paie.md`, « Les
  deux notes internes ». ~~Vacances payées par la caisse~~ : tranché le
  14/10/2026 (« A pour les VA »), les `VA` d'un ouvrier s'affichent en
  heures sans montant, voir `docs/regles-paie.md`, « Les deux notes
  internes » ; LCI juin au centime sur le brut. ~~Maladie du week-end~~ :
  tranchée le même jour (samedi 150 %, dimanche 200 %, et payée par
  l'employeur le premier mois seulement, ensuite par la mutuelle) ; LCI au
  centime en mai, juin et juillet. Le premier mois vaut aussi pour
  l'employé (le client : « c'est pareil pour les maladies employé ») : le
  fixe perd les heures au-delà, au taux horaire. Restent pour la RH : le
  « premier mois » vaut-il 30 jours calendrier ? Comment le fixe d'un
  employé est-il réduit ? ;
- ~~le repos lié au dimanche de la semaine 3 de l'ouvrier~~ : tranché le
  14/10/2026 par le client lui-même (« oui »), appliqué : le repos du jeudi
  A1 recule au lundi de la même semaine quand le jeudi est un `TP` et le
  lundi un repos (`jourTP()`, `jourRepos()`). LCI : août au centime ; le
  13/04, ce lundi où il est rappelé, se lit en rappel sur un repos
  (`reposA1()` : 12 h sup de nuit, comme la fiche — **je l'avais laissé en
  « question » alors que le cycle et le commentaire le disaient**, le
  client l'a relevé) ; avril −3,80 € au lieu de +247,80 € ; vérificateur
  et VBN identiques. Historique
  (14/10/2026) :
  quand le jour désigné (A1, un jeudi) est un `TP`, la fiche paie le repos
  le lundi de la même semaine, 4 fois sur 4 chez LCI (02/02, 13/04,
  22/06, 31/08), et le jour A1 quand il est un « - » (3 sur 3). Le
  déplacer aussi ? Seul août change de mois. **Le client, le 14/10/2026 :
  « question RH »** : rien n'est codé, la question passe à la RH. Remesuré
  le même jour, fiche par fiche, sur l'application actuelle : la
  demi-journée de conseil d'entreprise du 25/08 n'était pas payée à
  l'ouvrier, elle l'est (`docs/regles-paie.md`) ; tout le reste de l'écart
  de LCI est ce repos, le 01/01 (un week-end de 2025), le 13/04 et le
  17/03 ;
- **deux questions pour la RH** (le client, le 14/10/2026 : « garde la
  question pour RH »), tirées des fiches de LCI, ouvrier :
  - **la nuit de 12 h « 18h-06h »** (LCI le 20/03) : la fiche paie les 4 h
    de 18 h à 22 h à la prime de NUIT à 150 % ; l'application les paie à
    la prime de l'après-midi, la pause où elles tombent, comme les états
    SAP de VBN, employé, les 21 et 22/03 (V42). Prime de nuit pour
    l'ouvrier ? Mars de LCI −13,20 € de prime ;
  - **« DS-CE + ½ VA »** (LCI le 15/04, `["DS-CE","1/2VA"]`) : la fiche paie
    les 4 h prestées avec la prime du matin ; l'application les lit sans
    prime (code de jour). Le 18/03, même forme, a déjà la prime de
    l'après-midi des deux côtés. Trois journées de l'année (18/03, 15/04,
    21/10). Avril de LCI −3,60 € ;
- ~~le D de la grille~~ (09/10/2026) : tranché le 14/10/2026, le client :
  « le D est un jour où le travailleur peut choisir son horaire (6-14 /
  7-15 / 7:30-16) ; le choix par défaut est celui indiqué dans l'horaire
  dans son cycle perso ». `horaireHabituelD()` lit désormais la cellule
  franche des jours que le cycle de la personne met en D (« 6h-14h » chez
  DBE, « 7h-15h » chez VBN, « H. flott. » chez VGG) et un D sans heure
  prend cet horaire, au Planning, dans l'agenda, à l'Accueil et dans les
  propositions ; à défaut, 7-15. L'ancienne lecture ne savait pas que
  « 6h-14h » est un horaire de D, et rendait 10-18 à QBY (ses jours de
  CE). Agendas : 893 événements passent de 7 h à 6 h (62 en 2026, 831 en
  2027 projeté), aucun n'apparaît ni ne disparaît ; personne n'écrit
  7h30-16h. Les cinq sorties du vérificateur sont identiques à l'octet
  (aucune heure payée ne bouge) ;
- **la RJF de l'ouvrier** : la note ne la nomme pas — payée comme un férié
  (salaire moyen) ou au garanti ? Le client, le 14/10/2026 : RJF veut dire
  « récupération jour férié » (la légende disait « férié à choix libre »,
  corrigé). Le taux n'est pas tranché : question pour la RH, l'application
  garde le garanti ;
- ~~le repos payé lié au week-end~~ : codé le 09/10/2026 à la demande du
  client (« optimise tout ce qui peut l'être avec ces documents »), avec le
  férié presté de l'ouvrier payé une seule fois ; voir
  `docs/regles-paie.md`, « Les deux notes internes ». Prestation et repos
  concordent sur cinq mois de LCI ; les restes ont chacun leur journée ;
- ~~le férié d'un employé~~ : tranché le 14/10/2026, le client : « ok »
  pour fixe + 100 % sans attendre d'autre fiche. Appliqué (« Supplément
  weekend à <taux> », non déduit, prime d'équipe à 200 %) ; VBN mai au
  centime, janvier et avril ne gardent que les heures sup non écrites des
  14/01 et 04/04 ; l'ouvrier garde 200 %. Historique : les fiches de VBN paient
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
- ~~le rappel sur un repos d'un EMPLOYÉ~~ (VBN le 25/06) : tranché le
  14/10/2026 par le classeur lui-même, sans question. Le lendemain porte
  `["-","7h +FT"]` : les heures sont au flex time, et ce n'était pas une
  règle d'employé. Voir « Les états de présence SAP » ;
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
- ~~trois heures sup écrites en plage~~ : tranchées le 12/10/2026, voir
  « Les chaudières d'ATR », fin ;
- ~~les soldes flex time sous −8 h~~ : la question était FAUSSE, et je
  l'ai fait passer à la RH. Le client, le 16/10/2026 : « les heures de FT
  sont celles indiquées dans la ligne 430 » — la case « Total: » du pied
  de feuille EST le solde. Je la lisais comme le seul report de 2025 et y
  ajoutais les ±FT de l'année. Relu juste : personne sous −8 h (SMA
  exactement −8), voir « Cinq notes de service » ;
- **le « recyclage restant » du classeur RH ne se recoupe pas pour neuf
  personnes** (posée le 18/10/2026, en mettant les recyclages dans le
  héros). Pour vingt personnes, le restant écrit par le classeur égale ce
  qui manque pour atteindre l'objectif de chaque atelier possédé (10 pour un
  opérateur, 5 pour un adjoint, 5 de plus pour le contremaître d'un
  adjoint). Pour neuf, non : DWS 17 au classeur pour 27, SBZ 11 pour 26,
  FLN 7 pour 22, FPS 15 pour 30, PLZ 8 pour 28, PAM 18 pour 10, ASS 10 et
  PDR 2 pour 0, VBN 30 pour 5. Le total « fait + restant » vaut 15 ou 20
  pour cinq d'entre eux (DWS, SBZ, FLN, FPS, PLZ) là où l'application
  attend 30 ou 40 — un objectif de 5 par atelier, ou sur certains ateliers
  seulement ? —, 30 pour PAM et VBN, 10 pour ASS et PDR, pour qui
  l'application ne trouve rien à recycler. **Quel est l'objectif de recyclage de ces neuf personnes, et
  sur quels ateliers ?** En attendant, le héros montre les deux chiffres
  tels que le classeur les donne : fait / objectif par atelier, et la
  progression avec SON restant ;
- **les 51 matricules** de « Polyvalence » vivent dans le dépôt public, à côté
  du trigramme. Ce fichier les tolère (« initiales ou matricule ») ; s'ils
  figurent sur les fiches de paie, ils relient le trigramme à la personne.

