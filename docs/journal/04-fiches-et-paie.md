# Contrôles contre les fiches, relevés, états SAP, et l'interface qui en est née

Historique déplacé tel quel de `CLAUDE.md` le 18/10/2026. Les dates, mesures et erreurs y restent.

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

### Cinq notes de service, et le solde flex time du jour

Le client, le 09/10/2026 : cinq notes de service internes (flex time 2021
et 2024, congé par heure en production 2022, absence imprévue 2025, temps
partiels 2025), « à garder en privé et utiliser pour optimiser l'app ».
Quatre sont des **scans** : Tesseract n'a pas le français dans ce conteneur
et le proxy refuse de le télécharger (403) ; les neuf pages ont été lues
une à une. Rangées dans `CronoBots/groups-fiches/regles/`, métadonnées
vidées — elles portaient les identifiants de connexion de l'auteur et du
copieur —, transcrites dans `regles/notes-internes.md`. Les règles, sans
nom, sont dans `docs/regles-paie.md`, « Les notes de service du
09/10/2026 » : la plupart confirment ce qui est déjà codé.

**Ce qui est codé : le solde flex time AU JOUR J**, dans l'onglet
Compteurs. La note de 2024 borne le compteur à −8 h et 104 h sur le solde
« à la pointeuse, situation au jour J » — les reprises planifiées plus tard
n'en déduisent rien — et demande de redescendre à 80 h au-delà. L'onglet ne
montrait que les heures portées et reprises de l'année, jamais un solde.
`compteursCalcules()` prend un troisième argument facultatif (MMJJ) et
compte à part les ±FT jusqu'à ce jour. Le solde est la case « Total: »
du classeur, telle quelle (`soldeFTClasseur()`). Une phrase dit l'état : dans les bornes, au-dessus de
80 h (jaune), au-delà de 104 h ou sous −8 h (rouge). Le vérificateur appelle
la fonction à deux arguments : ses quatre sorties sont identiques à
l'octet.

**Et le solde était faux jusqu'au 16/10/2026.** J'avais lu « Total: » comme
le report de 2025 et je calculais report + portées − reprises : « onze
personnes sous −8 h » (PDR −49…), une question posée au client puis passée
à la RH. Le client : « les heures de FT sont celles indiquées dans la ligne
430, pour PDR donc −3 ». La case contient déjà le solde de fin 2025 et
toutes les journées écrites de l'année : la recompter avec les colonnes +FT
et −FT doublait l'année. Le convertisseur la nomme désormais `total`.
Il s'affiche tel quel, sans en retirer les ±FT planifiés plus tard : ce
serait supposer ce que la case compte. Mesuré au 16/10 : **personne sous
−8 h** (SMA −8, CKS et LHS −7), personne au-dessus de 80 h (ADK 68 h). **La leçon** : un libellé du classeur se lit tel qu'il
est écrit — « Total » veut dire total ; c'est moi qui l'avais renommé. Rien ne sort de l'écran à 320 (hors
ligne), 390 et 1280 px ; les seuls débordements sont dans les tableaux qui
défilent déjà de côté.

**La suite, le même jour** : sept documents de plus (la note explicative
du relevé mensuel, la filière intérimaires de 2017, la procédure des
primes de rappel, la prime de garde de janvier et de septembre 2026, les
montants des primes ponctuelles 2026 ; la fiche de paie et les repos
étaient déjà rangés, texte identique). Rangés dans `regles/` du dépôt
privé, métadonnées vidées ET commentaires JPEG des scans retirés — ils
portaient le nom du copieur. Résumé dans `docs/regles-paie.md`, « La
suite, remise le même jour ». **Rien n'est codé** : la procédure de rappel
est celle déjà appliquée, la garde et les primes ponctuelles ne touchent
pas les pauses. Deux pistes pour le client : le code `V` du relevé
(heures sup volontaires, payées sans récupération) explique sans doute les
« pas compenser » de VBN ; et les rappels pourraient proposer les
permanents avant les intérimaires, comme le veut la note de 2017.
Le client, le même jour : il pose la question des heures sup au bureau
RH, et a demandé ses relevés de prestations officiels de toute l'année.
**À leur arrivée** : chercher `V` ou `U` les 21 et 22/03 (nuits de 12 h,
« pas compenser » sur la fiche), en janvier (1 h 30 « à compenser ») et en
avril (0 h 45 « pas compenser ») ; les ranger dans le dépôt privé, jamais
ici (nom et matricule).

**Les permanents avant les intérimaires** (le client, le 09/10/2026 :
« il faut toujours proposer les permanents avant les intérimaires », la
règle de la note de 2017). `permanentsDabord()` range chaque liste de
propositions — en D, changement de pause, prolongation 12 h, et les
remplaçants du congé en heures — permanents d'abord, ordre d'origine
gardé ; les rappels d'intérimaires ont leur cadre à eux, « Rappel -
Intérimaire · Repos / Veille X », après tous ceux des permanents.
`estInterim()` lit `statutAffiche()`. Mesuré au navigateur sur les 110
cadres des sous-effectifs : aucun permanent après un intérimaire, SMK seul
dans « Rappel - Intérimaire · Veille N ». Vérificateur identique à
l'octet (il ne découpe pas ces modules) ; rien ne déborde à 320 (hors
ligne), 390 et 1280 px.

### Toutes les fiches, recopiées une fois pour toutes

Le client, le 09/10/2026 : « garde quelque part toutes les infos des fiches
de paie, afin de pouvoir réutiliser les chiffres pour toute une série de
vérifications ». `comparer-fiches.py` ne garde que des heures, le temps
d'une comparaison ; `tools/extraire-fiches.py` recopie la fiche ENTIÈRE :

```bash
python3 tools/extraire-fiches.py CONTRAT=TRI,CONTRAT=TRI /hors/du/depot/fiches-2026.json FICHE.pdf …
```

**Il lit par la POSITION des mots** (pymupdf), pas par le flux de texte, qui
mélange les deux colonnes : à gauche les lignes de rémunération et de
retenue (quantité, libellé, code A/B/D/F/G, montant) et les bases ; à droite
les informations générales, les soldes d'année et le détail des jours ; la
ligne « EUR » du récapitulatif ; les prestations jour par jour d'un ouvrier.
Le compte individuel annuel se lit par trimestre, et ce qui n'a pas de
structure connue (une page scannée) est recopié mot par mot avec sa
position.

**Le contrôle de fidélité est la fiche elle-même** : sur les 21 fiches
mensuelles de VBN et de LCI, la somme des lignes extraites redonne le TOTAL
imprimé des rémunérations ET des retenues, et le récapitulatif se boucle
(brut − ONSS = imposable, − précompte = net, + divers = net à recevoir).

**Ce qui ne sort jamais** : le bloc nom et adresse, le numéro de registre
national et la date de naissance qu'il contient, le numéro de contrat
(remplacé par le trigramme donné), l'IBAN et le BIC, la référence de
diffusion. **La garantie** relève tout cela sur les fiches elles-mêmes et
le cherche en mots entiers dans la sortie ; un seul, et rien n'est écrit.
**Elle a fermé trois fois à la mise au point, et à raison** : la ligne du
virement (IBAN) entrait dans les informations générales, l'en-tête du
compte individuel (contrat) dans ses trimestres, et des montants pris pour
le bloc adresse.

**La sortie porte des montants de salaire** : l'outil refuse de l'écrire
sous la racine du dépôt, et refuse une fiche qui serait dans le dépôt.
**Elle vit dans le dépôt PRIVÉ `CronoBots/groups-fiches`** (le client, le
09/10/2026, « garde toutes les infos utiles pour vérifier les prestations et
payes »), `fiches/fiches-2026.json`, avec sa propre note `CLAUDE.md`. Une
session qui doit vérifier une paie l'attache (`add_repo`) et le lit ; rien
n'en revient ici que des règles écrites avec des lettres. L'application
Claude ne peut pas créer de dépôt : c'est le client qui l'a créé. **Les
fiches ne se poussent jamais sur un git**, même privé, même pour les retirer
ensuite : elles portent le nom, le registre national et l'IBAN.

Les deux documents de VBN datés du 24/02 que le texte ne lisait pas sont les
**fiches fiscales 281.10 et 281.18 de 2025**, scannées : l'OCR en lit mal
les montants, et les mêmes totaux 2025 (imposable, précompte, heures sup)
sont en texte dans le compte individuel 2025, extrait sans erreur.

### La paie à l'heure de LCI, revérifiée le 09/10/2026

Le client : « vérifie les prestations et salaires ». Depuis la fin
septembre, l'application paie un OUVRIER à l'heure (`salHorGaranti`,
`salHorMoyen`, la branche `ouvrier` de `compute()`) ; la comparaison du
26/09 calait encore une rémunération fixe, et ne mesurait donc plus rien.
Elle est refaite sans calage, avec le taux garanti et le taux moyen imprimés sur
chaque fiche (lus dans `CronoBots/groups-fiches`) : brut identique en
janvier et en juin, trop haut les autres mois. **Jour par jour, la lecture
de l'horaire concorde** — un jour presté est un jour d'« heures normales »,
une absence une absence, un repos un repos, et les heures des jours prestés
sont les mêmes à cinq journées près, toutes déjà connues (14/01, 20/02,
17/03, 20/03, 13/04). Les écarts sont des RÈGLES DE PAIE d'ouvrier que
l'application n'a pas :

- **les vacances ne sont pas payées par l'employeur** : « Congé Légal »
  porte des heures sans montant sur les huit fiches (16 h en février, 44 h
  en avril…) — chez l'ouvrier, c'est la caisse de vacances qui paie.
  L'application les payait au taux garanti ; **tranché le 14/10/2026**,
  elle les montre en heures sans montant ;
- **la réduction du temps de travail n'est pas payée** : « RED TEMPS TRAV
  NON PAYE » au détail des jours, « Réduction Temps Travail » sans montant
  (6 h en avril, 8 h en mai). L'application la paie ;
- **une maladie un samedi se paie à 150 %, un dimanche à 200 %** : « Heures
  SHG Maladie à … à 150% / à 200% » les 02-03/05 et 11-12/07.
  L'application payait toute la maladie au taux moyen simple ; **tranché
  le 14/10/2026**, elle la majore, et au-delà du premier mois elle n'en
  paie plus rien (mutuelle) ;
- **chaque jour de week-end presté donne un jour de repos payé en
  semaine** : « Jours de Compensation » = jours de « JOUR DE REPOS PAYE »
  du détail, et ils suivent les jours de week-end prestés (6/6 en janvier,
  5/5 en février, 4/4 en avril, 6/6 en août). Ce sont des repos « - » de
  l'horaire, jamais choisis au hasard : 33 repos de semaine payés, 13 non.
  L'application paie la même somme autrement (base du week-end dans la
  prestation, aucun repos payé) ; l'écart n'apparaît que quand le jour de
  compensation tombe le mois suivant (mai trop haut, juin trop bas).

Les trois premières sont posées au client (« Ce qui attend le client »),
rien n'est codé avant sa réponse : elles touchent à des montants. **La
deuxième est tranchée le même jour** par la note explicative de la fiche de
paie, que le client a remise avec la note sur les repos de la grille :
« Réduction Temps Travail … non payé pour les ouvriers ». Appliquée, avec
deux autres lignes que la note corrige (libellé de la RHS/DTT, férié au
salaire moyen) — voir `docs/regles-paie.md`, « Les deux notes internes ».
L'écart de RTT d'avril et de mai disparaît exactement ; la quatrième ligne,
le repos lié au week-end, est désormais décrite jour par jour par la note. VBN
(employé) est **identique à l'octet** à la comparaison du 07/10 : rien n'a
régressé. Les scripts de comparaison vivent dans le scratchpad ; les
copies texte des fiches qui y traînaient (nom, registre national, IBAN)
ont été supprimées.

### Les relevés de pointage d'autres personnes, anonymisés

Le client, le 27/09/2026, en envoyant son relevé d'août scanné : « je vais
t'envoyer les fiches comme celle-ci d'autres opérateurs ; regarde comment
ma fiche est construite afin de l'anonymiser en gardant le trigramme, pour
faire à chaque fois la même chose ».

```bash
python3 tools/anonymiser-sommaire.py SCAN.pdf TRIGRAMME sommaire-TRI-AAAAMM.pdf
```

**Un scan n'a pas de texte** : le copieur écrit une image de fond et des
masques noir et blanc. On ne remplace donc pas un mot, on repeint des
zones. Quatre choses nomment la personne : le titre « Sommaire mensuelle -
<nom> », « Matricule: » (le numéro de contrat des fiches de paie),
« Section: », « Nom: ». Le titre et le nom reçoivent le trigramme, le
matricule et la section « (retiré) ». **Les métadonnées et le nom du
fichier portent l'identifiant de connexion de celui qui a scanné** :
elles sont vidées, et la sortie prend le nom qu'on lui donne.

**Les zones se trouvent par la structure** : la suite des lignes « * »,
un seul signe tout à gauche, sert de repère ; la ligne sous elle est
« Nom: », les trois au-dessus sont Matricule puis Section et « Sommaire de ».
Le haut du tableau avait été choisi d'abord, et il a échoué : son trait est
trop fin, le scan le rompt. Si la structure n'est pas retrouvée, l'outil
s'arrête sans rien écrire. Éprouvé : un scan dont on efface les « * »
échoue, un trigramme de deux lettres et un chiffre aussi.

**Fidélité** : hors des zones, l'image produite ne diffère de la source sur
aucun pixel, et l'outil le vérifie. La sortie est une image pure dans un
PDF neuf : rien du scan d'origine ne survit sous ce qui a été repeint.

**Sa garantie n'est pas complète** : sans lecture de caractères, il ne peut
pas chercher le nom ailleurs sur la page. On regarde l'aperçu PNG qu'il
écrit, **toujours**, avant de s'en servir. Le trigramme se donne à la main :
le matricule n'est pas dans les données de l'horaire.

**Un scan peut porter une série** — le client, le 27/09/2026 : treize
pages, douze personnes, août 2026. On donne un trigramme par page, dans
l'ordre, et l'outil écrit un fichier par personne :

```bash
python3 tools/anonymiser-sommaire.py SCAN.pdf YRS,PLZ,SKS,SKS,… DOSSIER --mois=202608
```

Tout ou rien : chaque page est repeinte et vérifiée avant qu'un seul
fichier s'écrive, et un nombre de trigrammes différent du nombre de pages
arrête tout. La première version ne traitait que la page 1 et recopiait
les autres **telles quelles**, noms compris : sur une série, douze pages
sur treize seraient sorties nominatives, avec pour seul garde-fou un
avertissement imprimé.

**Le trigramme se calcule, puis se vérifie.** L'initiale du prénom, la
première et la dernière lettre du nom : c'est la règle de l'anonymiseur,
et onze des douze tombent sur un trigramme connu. Mais `CORRECTIONS`
renomme quatre personnes (NPI, JBA, CHD, PDF), et le douzième relevé donnait
CDE, que CHD portait aussi à l'origine. **Le relevé a tranché seul** : ses
pauses du 3 au 16/08 concordent jour pour jour avec l'horaire de CDE, le
13/08 compris (6h-18h dans l'horaire, pointé de 5 h 39 à 18 h 16), et pas
avec celui de CHD. Une page de relevé peut déborder sur la suivante : deux
pages du même trigramme vont dans le même fichier (SKS, 2 pages).

**Ni le scan ni sa version anonymisée n'entrent dans le dépôt** : même sans
nom, un relevé de pointage porte les heures d'arrivée d'une personne
identifiée par son trigramme. Dépendances : `pip install pymupdf pillow`.

**Un scan poussiéreux trompait l'outil EN SILENCE**, et c'est la deuxième
série qui l'a montré (le 27/09/2026 : 23 pages, cinq employés, janvier à
août). Trois pages échouaient — les poussières grises des lignes « * »
comptaient pour des mots —, et c'était le moindre mal : sur la page 8, une
bande de poussière AU-DESSUS du titre passait pour le titre, qui gardait le
nom ; sur la page 12, des bandes de poussière décalaient le décompte, et la
zone « Matricule » visait une ligne de compteurs. **Le contrôle de fidélité
passait dans les deux cas** : il vérifie que rien n'a bougé hors des zones,
pas que les zones sont les bonnes.

D'où deux gardes. Un bloc de moins de 20 pixels d'encre est une poussière
(une étoile en pèse 35, un mot des centaines), et une bande qui n'a que des
poussières n'est pas une ligne. Et **chaque ligne se reconnaît à la largeur
de ses intitulés** — la police est à chasse fixe, « Matricule: » fait dix
signes, « Nom: » quatre, le titre commence par « Sommaire » et
« mensuelle » ; une position comptée ne suffit plus. Éprouvé : effacer
« Matricule: », sa valeur, « Section: », « Nom: » ou « mensuelle » fait
échouer la page ; les 14 pages de la série d'août passent toujours, et le
scan saboté d'août échoue toujours.

Le mois se donne désormais page par page, `TRI:AAAAMM`, un fichier par
personne et par mois.

**Une chasse aux noms par OCR** complète la garantie qui manquait : chaque
page produite est lue par Tesseract, et on y cherche, à cinq lettres près,
les mots des noms lus sur la source — gardés en mémoire, jamais écrits.
Elle mord : 23 pages sur 23 dans la source, **0 sur 23** dans la sortie. Le
script vit dans le scratchpad ; l'aperçu se regarde quand même.

### Les relevés d'août confrontés à l'horaire, jour par jour

Le client, le 27/09/2026 : « oui c'est le but ». Treize relevés, 403
journées d'août. **Pas de couche de texte** : Tesseract (`apt-get install
tesseract-ocr`) lit le tableau, **après avoir coupé l'en-tête** au bas de
la ligne « Nom: » que `zones()` de l'anonymiseur repère — aucun nom ne
passe dans le texte extrait. L'OCR confond lettres et chiffres (« P1i2 »,
« zo3 », « g84 ») et lit mal les chiffres des dates : les jours se
numérotent par leur RANG (chaque jour a sa ligne), jamais par la date lue.
**Et la ligne « faits à: 24.09.2026 » a une date** : comptée comme un
jour, elle décalait tout d'une ligne et fabriquait des écarts.

Les codes du relevé, lus sur les pages : `P10`/`P11`/`P12`/`P13` prime D,
AM, PM, N ; `P3x` le samedi, `P5x` le dimanche, `P8x` un férié ; `Y90`
week-end libre, `Z03` repos ; `F0` flex time épargné ; `U32`/`U33` heures
sup en PM, en N ; `J84` heures de déplacement d'un rappel ; `A57` le TP ;
9063 en « Sold.j. », le chèque-repas (MCH, *maaltijdcheque*). Absences :
4 et 13 maladie (13 à partir du 2ᵉ mois), 15 maladie sans certificat,
2 salaire journalier garanti, 23 congé parental, 47 VCP (le DTT du
classeur), 48 jour férié au choix (le RJF), 54 compensation payée (RHS),
58 RTT, 75 vacances.

**Les pauses et les primes concordent** sur toutes les journées lues,
une fois retirés les artefacts d'OCR — la prime la plus élevée des 19 et
20/08 (VBN) comprise. Les rappels, le flex time épargné et les heures sup
aussi : LDY le 12, GBT, PLZ et SKS le 27, SKS le 24. **Ce que le classeur
n'écrit pas**, et que le relevé paie :

- SMA le 17/08 : rappel et 4 h sup avant sa nuit (pointé dès 17 h 36) —
  la cellule dit `["N"]` ;
- CDE le 13/08 : rappel écrit « rappek ke 12/08 », faute de frappe ;
- CDE le 14/08 : 0,5 h sup en nuit (sortie à 23 h 06) ;
- SMA le 24/08 : venu 1 h (21 h 14 – 23 h), puis 7 h de salaire garanti ;
  le classeur écrit « Abs » et l'application une maladie entière ;
- SMA le 28/08 : « Abs » sur un repos, le relevé dit repos.

**Le chèque-repas : j'ai d'abord écrit qu'il ne concordait pas, et
c'était faux.** Le comparateur ne regardait que les journées de présence,
et ignorait la ligne « Chèque(s) repas issu(s) des heures récupérées »
(`crRecup`, un chèque par 8 h de RTT, de flex time ou de RHS). Mesuré au
navigateur, mois d'août, personne par personne : **dix sur douze au
chèque près**. Le relevé confirme la règle chez tout le monde — journées
entières de récupération 15 sur 15 avec chèque (9 « 8h -FT », 5 RTT,
1 DTT), congés et maladie 0 sur 62 (VA, RJF, CP, TP, maladie). Le client,
le 27/09/2026 : « A — oui, récup = chèque ». **Seul le DTT manquait**
(YRS le 06/08) : il entre dans `crRecup`, compté à part, sans report —
YRS 18 → 19, comme son relevé. Le 01/03 de LCI, 8 h de flex time sans
chèque sur sa fiche, reste une exception. Neuf règles, manques, compteurs
et Recyclage identiques à l'octet (la règle est de paie seulement).

**Piège de mesure** : le sélecteur de personne affiche « GBT » pour deux
colonnes (GBT-1 en Shift 4, GBT en Shift 5). Choisir par le libellé a
d'abord mesuré la mauvaise personne (15 au lieu de 21) : on choisit par
l'identifiant, la valeur de l'option.

**Les cinq journées, une par une** (le client, le 27/09/2026, « point par
point ») :

- **CDE le 13/08, « rappek ke 12/08 »** : c'est le classeur qui l'écrit,
  avec une faute de frappe — la seule du mot sur l'année. La lecture la
  tolère (`RX_RAPPEL` et les trois tests du mot : « rappe[lk] ») ; le
  rappel est lu, 4 h de déplacement comme les autres rappels du mois.
  Vérificateur identique à l'octet ;
- **SPS le 21/08, maladie sans certificat** (code 15 du relevé, non payée
  selon le client) : le classeur écrit « Abs » comme pour une maladie
  payée. **Écart connu.** Un code lu sur « Abs s/c » a été ajouté puis
  retiré le même jour : personne ne l'écrira ;
- **SMA le 24/08**, venu 1 h puis malade ; **SMA le 17/08**, rappel et 4 h
  sup ; **CDE le 14/08**, 0,5 h sup : le classeur et les commentaires des
  collègues n'en disent rien. **Écarts connus** ;
- **SMA le 28/08**, « Abs » sur un repos : l'application n'en paie aucune
  heure — 32 h de maladie en août (24 au 27), le relevé dit repos le 28.
  Rien à corriger. Les scripts (OCR, analyse,
extraction de l'application) vivent dans le scratchpad de la session.

### Une date de rappel n'est pas un renvoi de flex time

Trouvé le 27/09/2026 en reprenant, un par un, les écarts des fiches de
VBN : le 11/06, un repos, `["02h-06h","4h +FT","… rappel le 10.06"]`, comptait
4 h prestées, avec prime de nuit, chèque et indemnité. La fiche n'en porte
aucun. Ce n'était pas une question au client : la section 6 ter de
`docs/conversion-horaire.md` le disait déjà — un `+FT` part au compteur,
sans prime ni heure prestée.

**Deux défauts, et le second était large.**

- **L'épargne se retirait de la journée contractuelle, pas de la plage.**
  Une plage de 4 h épargnée en entier laissait 8 − 4 = 4 h prestées. La
  présence est désormais la durée de la plage, relue sur le poste du jour
  (y compris quand le cycle corrige le poste, `r.plageEp`), et l'épargne
  s'en retire : VBN le 11/06, BBZ le 14/02, `0 h`.
- **Toute date d'un commentaire `+FT` passait pour un renvoi.** Et **121
  des 183 étaient des dates de rappel**, le jour de l'appel. FLI le 23/01,
  « 8h +FT, rappel le 18/01 », retirait 8 h au 18/01 ; 36 journées se
  renvoyaient leurs propres heures (« rappel le 27.01 » écrit le 27/01) et
  les épargnaient deux fois : ATA le 27/01, `06h-18h · 4h +FT`, comptait
  4 h au lieu de 8. Sept autres n'étaient pas des renvois non plus
  (« CP déplacés aux 26 & 27/03 », « encodé le 13/08 », « TP déplacé au
  21/04 »). `RX_RENVOI` exige désormais « presté le », « du », « cf » ou la
  date en tête : **55 renvois**, exactement les 62 d'avant hors rappels,
  moins les sept faux.

Une demi-heure sup écrite (« +0,5 hs ») qui est le reste d'une plage
épargnée — AFA le 10/02, `11h-15h30' · 4h +FT` — ne reste pas en heure
prestée : elle se paie déjà comme heure sup.

Mesuré : **49 journées** changent, chacune pour l'une de ces raisons ;
journées prestées 14 473 → 14 465 ; neuf règles à zéro ; **compteurs
(76/77) et `--manques 0926` identiques à l'octet** — les compteurs du pied
de feuille ne dépendent pas des renvois ; sur l'année passée, 269 → 272
places creuses ; Recyclage : cinq cases d'une journée, 23 couples au quota
inchangés. VBN en juin : nuit 79 h au lieu de 83 (fiche 72 ; les 7 h
restantes sont le rappel du 25/06, déjà sur la liste).

### Les relevés de cinq employés, de janvier à août

Le client, le 27/09/2026 : 23 pages, 16 relevés (ATA, JBI, YPE, VGG, AFA),
**481 journées lues sur 488**. Deux passes d'OCR (300 ppp, et 400 ppp
nettoyé : seuil puis filtre médian) se complètent ; les jours se datent
par la date lue, et une ligne illisible prend la date manquante entre ses
voisines **seulement si l'écart tombe juste** — sinon le jour est déclaré
illisible, jamais décalé. Les absences se lisent par leur LIBELLÉ
(« MALADIE », « Vacances », « Congé Anc. »…), pas par leur numéro, que
l'OCR lit « S » ou « 5S ». Codes appris : `U` et `S` + jour (3 semaine,
4 samedi, 5 dimanche ou férié) + pause = heures sup ; `P8x` férié ;
« 56 Congé Anc., RTT » est le DTT du classeur, comme le 47 VCP.

**425 journées concordent sur 481.** Trois règles en sont sorties, toutes
tirées du classeur et de son cycle — les relevés n'ont fait que vérifier :

- **un rappel sur un repos DU CYCLE se paie en heures sup**, même quand la
  cellule franche écrit la pause — les adjoints l'y écrivent (VGG le
  10/05, JBI le 22/08, VBN le 25/06). 17 journées ; le cycle concorde
  avec le relevé ou la fiche les cinq fois où c'est vérifiable. **VBN en
  juin : nuit 72 h, comme la fiche** (79 avant) ;
- **« SD26 · n h +FT »** : repos au cycle, les n heures sont toute la
  présence et partent au compteur (AFA le 07/01, 0 h prestée) ; poste au
  cycle, elles s'ajoutent à la journée (VGG le 09/04, 8 h + 3). 15
  journées, 5 vérifiées ;
- **une plage en annotation qui couvre ENTIÈREMENT une pause plus haute
  que celle de la cellule** en fait la pause prestée : AFA le 10/08,
  `["PM","18h-6h"]`, relevé 8 h de nuit et 4 h sup de nuit. 25 journées ;
  la prime ne baisse jamais (ATA le 21/03, « Conserve sa prime », reste
  PM). Le manque du 30/09 en N au gluten disparaît : IME,
  `["AM","21-06h"]`, y est.

Neuf règles à zéro, compteurs 76/77 identiques ; 5 journées « SD26 » sur
repos passent en non prestées ; Recyclage : trois cases d'une ou deux
journées, 23 couples au quota inchangés.

**Le cycle n'est pas une source sûre SEUL**, et c'est mesuré : « une
pause écrite sur un repos du cycle, sans rappel » donne 170 journées,
dont VGG le 08/05 — repos au cycle, matin au relevé. Rien n'est tiré de
cette forme ; le mot « rappel » est ce qui la rend fiable.

**Le client l'a tranché le 27/09/2026 : B, rien sans le mot « rappel ».**
Et il a donné la raison de l'erreur du cycle : « les jours de D peuvent
être déplacés et ne sont pas toujours prestés les jours où ils l'étaient ;
VGG ne vient pas faire ses horaires flottants les 04 et 05 mai, donc il
décale un de ses D le vendredi et vient remplacer en matin car cela
l'arrange mieux ». Un D déplacé fait d'un repos au cycle un jour
travaillé normal. JBI les 08/08 et 14 au 16/08 restent un écart connu.

Écarts connus, que le classeur n'écrit pas : RHS d'un départ anticipé
(VGG 03/04 ; le 15/05 est lu depuis le 18/10/2026 ; le 23/07, « départ à 20h », est lu depuis le
29/09/2026), flex time épargné non écrit
(AFA 30/07, JBI 18/08, VGG 01/07), maladie sans certificat écrite en
poste (VGG 07/08), une pause prévue différente (AFA 12 au 15/01 en SD26,
ATA 05, 06 et 17/08 écrits D ou 7h-15h et pointés 6 h-14 h, VGG 30/04),
RJF renvoyé par « cf 21/08 » (JBI 13/08), « Abs » sur un repos (YPE 17
et 18/08), un jour férié écrit « 8h -FT » (YPE 14/05, Ascension).


### L'avance de l'ouvrier, tirée du règlement de travail (30/10/2026)

Le client : « les versements employé et ouvrier sont renseignés dans le
règlement ? » Oui, à l'article 18 : l'avance dix jours ouvrables avant la
fin du mois pour l'ouvrier, quatre pour l'employé ; le solde au plus tard le
7e jour ouvrable qui suit ; la clôture des états de salaires le 4e jour
ouvrable, pour tous. Rien sur les dates du pécule ni du treizième mois de
l'ouvrier (question 10 au client, toujours ouverte).

Jusque-là, l'application donnait à tous les dates de l'employé ; v1205 suit
le Statut des Réglages (`versementsDuMois(y,m,ouvrier)`). Mesuré :

- **les fiches** (dépôt privé) : les huit fiches mensuelles de l'ouvrier,
  janvier à août 2026, portent la date d'émission de celles de l'employé,
  mois pour mois — d'où le même solde ; l'« Avantage non récurrent » (CCT
  90) est sur ses fiches 02 et 08, comme chez l'employé ;
- **les dates** : 24 mois (2026-2027), aucune avance d'ouvrier un week-end
  ni un férié ; au navigateur, « Avance de novembre » passe du mardi 24 au
  lundi 16 novembre quand le Statut devient « Ouvrier », sans erreur ;
- **rien d'autre n'a bougé** : les quatre sorties du vérificateur du
  calendrier (base, `--manques 0926`, `--polyvalence`, `--compteurs`)
  identiques à l'octet.

Le mot « ouvrables » se lit, pour l'ouvrier, comme le client l'a tranché
pour l'employé (« jamais payé le wk ») : c'est une déduction, écrite comme
telle dans `docs/regles-paie.md`, à revoir si une fiche la dément.

Une première rédaction de la note ouvrait une phrase sur le mot « prime »,
majuscule comprise, suivi du sigle de la convention : `verifier-depot.py` y
a lu une forme de nom (un mot à majuscule suivi d'un trigramme). Reformulée
plutôt qu'admise — et ce paragraphe-ci, qui la citait telle quelle, a fait
refuser le premier commit par le crochet.

### Ce que le règlement dit de chaque statut (30/10/2026)

Le client : « y a-t-il des nouvelles infos utiles concernant chaque
statut ? » Le règlement est commun aux ouvriers et aux employés ; ce qui
les sépare tient en peu de lignes, relevées sur tout le texte (`ouvrier`,
`employé`, `statut`, `cadre`, chaque article) :

- **en-tête** : commission paritaire 118 pour les ouvriers, 220 pour les
  employés ; caisse de vacances « seulement pour ouvriers » ;
- **art. 15** : l'ouvrier payé à l'heure, l'employé au mois ;
- **art. 18** : l'avance, 10 jours ou 4 (v1205, plus haut) ;
- **art. 49** : la suspension pour raisons économiques, intempéries ou
  force majeure est écrite pour les ouvriers ;
- **art. 55** : les indemnités de maladie (« salaires hebdomadaires,
  2e semaine de maladie, salaire mensuel garanti ») payées au premier jour
  de paie qui suit leur exigibilité — sans durée ni pourcentage : les
  questions 6 à 8 à la RH restent ouvertes ;
- **annexe X** : la formation syndicale des délégués ouvriers ; **annexe
  XI** : les réunions CPPT, CE et DS des deux statuts.

Ce qui n'était pas attendu vient d'ailleurs : **l'art. 8-2 explique les
soldes RTT du classeur.** 8 jours de RTT par an pour la grille de cinq
semaines (38,40 h), 10 pour celle de six semaines (38,67 h) : × 8 h, ce sont
les 64 h des opérateurs et les 80 h des contremaîtres et adjoints que le
classeur écrit à la main (`docs/plateforme.md`). Et cela rouvre une
conclusion du 21/09 : la fiche à 38:40 était celle d'un adjoint, et
38,67 h vaut 38 h 40 ; la grille de cinq semaines, elle, fait bien 38,4 h
décimales (24 pauses × 8 h ÷ 5). Corrigé sur place dans
`docs/conversion-horaire.md` et posé à la RH (7 bis). Rien n'a bougé dans
le calcul : « Heures / semaine » n'est qu'affiché, et le diviseur horaire
ne sert qu'au fixe d'un employé.

Un écart possible, posé aussi (7 ter) : l'annexe XI paie les jours de
dispense « primes de pause » comprises, la fiche d'un ouvrier paie la
demi-journée de conseil d'entreprise sans prime d'équipe.

Publié : trois infos pratiques de plus dans la base (25 en tout) —
« Ouvriers et employés : ce qui diffère » (Paie), « Durée du travail et
jours de RTT » (Congés et absences), « Mandat syndical : formation et
réunions » (Autre) — chacune avec ses articles. Et l'aide du réglage
« Avance mensuelle » nomme l'ouvrier (v1206).

### Tous les documents relus, ligne par ligne (30/10/2026)

Le client : « vérifie l'entièreté des documents pour ne passer à côté
d'infos importantes ». Quinze documents du dépôt privé : le règlement de
travail (58 pages) et les quatorze notes de service. Six relecteurs en
parallèle (le règlement en cinq tranches de pages, les notes ensemble),
chacun confrontant chaque page aux infos publiées, aux règles et aux
questions ; les chiffres relus sur l'image, l'OCR faisant foi de rien. Puis
un sceptique sur le lot de textes, et des remesures ici.

**Ce qui a été trouvé, et ce qui n'a pas tenu :**

- *tenu, important* : la semaine 5 alterne (lundi-mercredi, puis
  mercredi-vendredi au cycle suivant, art. 8-2.3) — remesuré : 435 paires
  de semaines de D sur 446 alternent en 2026, 539 sur 550 en 2027 (« 484 sur
  495 » s'est d'abord écrit ici, et c'était faux : un `tail -6` avait coupé
  la ligne des opérateurs en formation) ; le cycle
  de l'application ne le sait pas (chantier à part, mesuré avant d'entrer) ;
- *tenu* : la ligne de l'art. 44 et l'affiche de l'annexe VI, crues
  illisibles, se lisent sur l'image (31 août / 1er octobre ; sirènes, EPI,
  hygiène, numéros) ; l'annexe VIII (le tableau des sanctions, les six
  comportements inadmissibles, la pause et la relève) ;
  l'annexe V (contrôle alcool et drogues : renvoyé à la maison même si le
  test est négatif) ; le 4/5 en feu continu (6,5 jours de RTT sur cinq
  semaines) ; quatre notes jamais reprises dans les infos (flex time,
  congé de moins de 8 h, temps partiel, absence imprévue) ;
- *tenu, et une phrase de nos règles était fausse* : « seuls RTT et flex
  time ouvrent le chèque-repas » (la note de la fiche dit aussi les
  récupérations d'heures sup et d'ancienneté, et le code les comptait
  déjà) ; « la RJF, que la note ne nomme pas » (la note du relevé la nomme,
  code 50) ; « rien n'est codé » pour les permanents d'abord (c'est codé) ;
  « 30 h 56 pour un 4/5 » (vrai sur six semaines seulement). Corrigées sur
  place, en disant qu'elles étaient fausses ;
- *n'a pas tenu* : « le service externe a changé » (Cohezio au lieu
  d'Attentia) — le classeur nomme Attentia onze fois jusqu'au 28/10/2026,
  Cohezio quatre ; « la prime de rappel devrait prendre le taux le plus
  favorable » — la même procédure dit que la prime de pause est celle de
  la pause prestée, ce que fait l'application ; « compléter le formulaire
  papier de congé » — c'est la copie d'un formulaire réel, on ne la
  retouche pas ;
- *mesuré en passant* : la fiche d'un ouvrier opérateur porte « temps
  partiel / 34:24 », soit 38:24 moins 4 h — un indice de plus que la
  grille de cinq semaines fait 38 h 24, pas 38 h 40 (question 7 bis).

**L'erreur commise, et rattrapée.** Le sceptique, relisant mes trente-deux
textes sur l'image, y a trouvé treize fautes sérieuses et une vingtaine
d'imprécisions, dont plusieurs recopiées des notes des relecteurs : toute
l'annexe VIII présentée comme propre au feu continu (une seule ligne
l'est) ; « le personnel de jour pointe au repas » (seulement s'il sort
manger) ; la combinaison Tyvek rangée au T.W.P. (c'est l'intérieur des
silos) ; « introduire de l'alcool » parmi les six comportements (seule la
consommation y est) ; la pause « flexible, rémunérée » étendue à la nuit ;
« accordé » là où la note dit « peut être introduite » ; « sans e-mail,
injustifiée » étendu à toute absence imprévue ; la protection d'une
plainte sans ses conditions ; « 38,40 h » rapproché de « 38 h 40 », qui
sont deux régimes. Toutes corrigées avant publication : un résumé de
relecteur n'est pas la source, et ce qui part chez les travailleurs se
relit sur l'image.

**Ce qui a été fait.** Les infos pratiques passent de 25 à 39 (quatorze
neuves, quatorze complétées, chacune avec ses articles), après relecture
sceptique sur le scan. Les règles corrigées ou complétées : chèques-repas,
DS d'un ouvrier (annexe X, question 7 quater), art. 6 pour le déplacement
demandé, horaires J3/J5 du D, glissant, repos du week-end, RJF, 4/5,
rechute de maladie, procédure de rappel. Les questions : 2 (les points
illisibles levés), 5 (CEP : deux notes y penchent), 6 (rechute), 7 bis
(37 h de contrat, 4/5, 34:24, CCT du 26/09/2013), 7 quater, 8 (deux pièces,
et le salaire horaire moyen mensuel), RH 1 (piste du 4/5), RH 4 (réponse :
le compteur des RHS vit dans SAP). Dans l'application (v1207) : l'avance
de l'ouvrier et le DTT des chèques-repas dans le guide, le repos lié au
week-end de l'ouvrier, et le réglage « Heures / semaine » qui disait
« contrat » et « sert au décompte des chèques-repas » — deux fois faux.
Dans le dépôt privé : la transcription des notes, sans montants jusqu'ici,
et une ligne mal lue (« 7, 7, 7, 3 » sont des pauses, pas des heures).

**La semaine 5bis entre dans l'application (v1208).** Un agent l'a codée
dans une copie isolée du dépôt : `CYCLE70` (cinq semaines, puis les mêmes
avec la semaine 5bis), troisième candidat du calage, qui ne l'emporte qu'à
accord strictement meilleur ; `pauseDeRotationD` lit à ±70 jours les
lundis, mardis, jeudis et vendredis d'une semaine de trois D quand ±35 ne
donne aucune journée de jour. Mesuré par lui, puis remesuré ici :
- calage mensuel 89,0 → 92,0 % (2026) et 93,1 → 96,3 % (2027), prolongation
  sur 92 jours 94,8 → 98,3 % et 96,2 → 99,8 % ; 64 personnes gagnent en
  2026, 60 en 2027, personne ne perd ;
- les quatre sorties du vérificateur identiques à l'octet, manques
  commentés à 0, les 81 agendas régénérés identiques au dépôt sauf trois
  journées voulues (une semaine 5bis lue enfin comme un D) ;
- onze journées lues autrement sur 55 462, et trois primes de rappel de
  2026, chacune comme la même cellule un autre jour (détail dans
  `docs/conversion-horaire.md`) ; deux décidées sur une seule cellule à
  ±70 jours, comme ±35 le fait déjà en bord d'année ;
- une première version, trop large, lisait faux un repos de semaine 2 :
  l'agent l'a vue et restreinte avant de mesurer.
Reste une question au client : le repos payé A1 en semaine 5bis.

**Laissé en chantier, et pourquoi** : la feuille de demande n'avertit ni
d'un flex time insuffisant ni d'un congé de moins de 8 h sans remplaçant
(un contrôle à concevoir avec la RH) ; le relevé simulé n'écrit ni V
(heures sup payées) ni Z03 (repos payé) ; les écochèques (fiches de
juillet, hors net) ; le salaire horaire moyen recalculé chaque mois (en
attente de la question 8) ; un e-mail tout prêt pour l'absence sans
certificat (il faut l'adresse de la RH).

### La sortie syndicale de l'ouvrier, et l'e-mail d'absence (30/10/2026, v1209)

Deux réponses du client à la relecture des documents :

- « Pour l'ouvrier en formation syndicale, la vraie version est celle du
  règlement, sinon c'est une erreur de paiement si l'app ne confirme pas. »
  L'annexe X paie ces jours « salaire normal (primes de pause et de
  week-end) ». Or l'application ne payait RIEN pour un `DS` d'ouvrier : une
  quantité d'heures, sans montant ni prime. Désormais, sur un poste prévu,
  les heures se paient au taux garanti et gardent la prime d'équipe de ce
  poste (et la majoration du week-end, qu'aucun `DS` de 2026-2027 ne porte :
  mesuré, aucun ne tombe un samedi ou un dimanche). Mesuré au navigateur sur
  la fiche d'octobre d'un ouvrier (DS le 05/10 sur un 6h-14h) : la ligne
  « Heure(s) formation syndicale » sans montant devient « … à [taux] »,
  et la prime du matin passe de 36 à 44 h ; rien d'autre ne bouge.
  L'employé garde la règle de sa fiche du 12/02 (son fixe paie la journée).
- « pointagebwz@biowanze.be, je pense, comme pour les autres » : l'e-mail
  tout prêt du jour d'absence sans certificat. Il vit dans Infos et aide,
  bloc « Prévenir la RH », à côté de celui du certificat — et non dans les
  tuiles de l'Accueil, que le client a voulues d'une ligne le 25/10.
  L'objet porte le trigramme et la date de l'usine ; la nature de
  l'absence reste à écrire.
