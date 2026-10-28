<#
    Recopie le récapitulatif Excel en remplaçant les noms par les trigrammes.

        .\anonymiser-classeur.ps1 "Recapitulatif.xlsm" classeur-2026.xlsx

    POURQUOI CETTE VERSION. C'est le portage de tools/anonymiser-classeur.py
    pour les postes qui n'ont pas Python — PowerShell, lui, est sur tout
    Windows, et il n'y a rien à installer.

    LE MÊME TRAVAIL, passe pour passe. Le 28/10/2026, ce jumeau avait pris un
    mois de retard sur la version Python : ni la ligne des noms, ni les
    corrections du client, ni les noms à particule, ni les auteurs des
    commentaires, ni les signatures, ni les identifiants de connexion, ni
    les intérimaires. Sur le classeur du 24/10, sa garantie l'arrêtait d'elle-
    même sur un nom qu'il ne savait pas lire. Il refait désormais chaque
    passe dans le même ordre, et tools/jumeau-powershell.py confronte les
    deux sorties sur un vrai classeur : même texte, partie par partie.

    CE QUE LE CONVERTISSEUR DÉCIDE, IL LE LIT DANS LE CONVERTISSEUR. Les
    corrections du client (CORRECTIONS), les feuilles de personnes
    (FEUILLES), la ligne des noms et le motif des signatures (AUTEUR) sont
    lus dans convertir-horaire.py, à côté de cet outil : une seconde copie
    de ces décisions serait la première à prendre du retard. Python n'a pas
    à être installé ; le fichier, lui, doit être là — il l'est dans toute
    copie du dépôt.

    Le travail n'interprète rien : le classeur est ouvert comme l'archive ZIP
    qu'il est, les noms sont remplacés partout où ils apparaissent, puis on
    referme. Feuilles, formules, mises en forme, commentaires, colonnes qu'on
    n'a pas encore comprises : tout passe intact.

    CE QUI SORT DU FICHIER :
      - les noms sous toutes leurs formes, remplacés par le trigramme ;
      - les signatures en tête des commentaires, et leurs auteurs ;
      - les macros (vbaProject.bin) : d'où un .xlsx, pas un .xlsm ;
      - les propriétés du document : auteur, dernier enregistreur, étiquette
        de sensibilité de l'employeur (docProps/custom.xml), chemin réseau ;
      - les identifiants de connexion écrits dans les commentaires.

    GARANTIE. Après écriture, la sortie est relue entièrement et l'outil y
    CHERCHE les noms qu'il vient de remplacer. S'il en trouve un seul, il
    détruit sa sortie et s'arrête avec le détail. Un anonymiseur qui peut
    laisser passer un nom sans le dire ne vaut rien.

    Tout ce qui s'affiche part aussi dans anonymiser-journal.txt : une fenêtre
    qui se referme emporterait l'erreur avec elle.

    Ce fichier est en UTF-8 AVEC BOM : sans lui, PowerShell 5.1 lirait les
    accents de travers et les motifs de noms seraient faux.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)] [string] $Source,
    [Parameter(Mandatory = $true, Position = 1)] [string] $Sortie,
    [string] $Tolerer = ''
)

$ErrorActionPreference = 'Stop'
try { Add-Type -AssemblyName System.IO.Compression } catch { }
try { Add-Type -AssemblyName System.IO.Compression.FileSystem } catch { }

$journal = Join-Path (Get-Location).ProviderPath 'anonymiser-journal.txt'
try { Start-Transcript -LiteralPath $journal -Force | Out-Null } catch { $journal = $null }

trap {
    Write-Host ''
    Write-Host "ERREUR : $($_.Exception.Message)" -ForegroundColor Red
    if ($_.InvocationInfo) {
        Write-Host ("  ligne {0} : {1}" -f $_.InvocationInfo.ScriptLineNumber,
                                           $_.InvocationInfo.Line.Trim())
    }
    if ($journal) {
        try { Stop-Transcript | Out-Null } catch { }
        Write-Host ''
        Write-Host "Le détail est dans $journal"
    }
    exit 3
}

$UTF8 = New-Object System.Text.UTF8Encoding($false)
$NS_M = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
$NS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
$NS_P = 'http://schemas.openxmlformats.org/package/2006/relationships'
$NS_XML = 'http://www.w3.org/XML/1998/namespace'
$OPT  = [Text.RegularExpressions.RegexOptions]::CultureInvariant
$OPTI = [Text.RegularExpressions.RegexOptions]'IgnoreCase, CultureInvariant'

# --- ce que le convertisseur décide ----------------------------------------
$convChemin = Join-Path $PSScriptRoot 'convertir-horaire.py'
if (-not (Test-Path -LiteralPath $convChemin)) {
    throw "convertir-horaire.py est introuvable à côté de cet outil ($convChemin). " +
          "Il porte les décisions du client (corrections de trigrammes, feuilles de personnes) : " +
          "lancer l'outil depuis une copie complète du dépôt."
}
$convTxt = [IO.File]::ReadAllText($convChemin, $UTF8)

function BlocPython([string] $nom) {
    $m = [regex]::Match($convTxt, '(?ms)^' + $nom + ' = \{(.*?)^\}')
    if (-not $m.Success) { throw "convertir-horaire.py ne porte plus de bloc $nom : cet outil doit être revu." }
    return $m.Groups[1].Value
}

# Les corrections du client : l'empreinte d'un nom → son trigramme.
$CORRECTIONS = New-Object 'System.Collections.Generic.Dictionary[string,string]'
foreach ($m in [regex]::Matches((BlocPython 'CORRECTIONS'), '"([0-9a-f]{10})"\s*:\s*"([^"]+)"')) {
    $CORRECTIONS[$m.Groups[1].Value] = $m.Groups[2].Value
}
if ($CORRECTIONS.Count -eq 0) { throw "Aucune correction lue dans convertir-horaire.py : cet outil doit être revu." }

# Les feuilles de personnes : leur ligne 10 porte les gens, un par colonne.
$FEUILLES_PERS = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($m in [regex]::Matches((BlocPython 'FEUILLES'), '"([^"]+)"\s*:\s*"[^"]*"')) {
    [void] $FEUILLES_PERS.Add($m.Groups[1].Value)
}
if ($FEUILLES_PERS.Count -eq 0) { throw "Aucune feuille de personnes lue dans convertir-horaire.py : cet outil doit être revu." }

$m = [regex]::Match($convTxt, '(?m)^LIGNE_NOMS = (\d+)')
if (-not $m.Success) { throw "LIGNE_NOMS introuvable dans convertir-horaire.py." }
$LIGNE_NOMS = [int] $m.Groups[1].Value
$m = [regex]::Match($convTxt, '(?m)^LIGNE_POSTE = (\d+)')
if (-not $m.Success) { throw "LIGNE_POSTE introuvable dans convertir-horaire.py." }
$LIGNE_POSTE = [int] $m.Groups[1].Value

# « Nom, Prénom: », « Nom, Prénom (external): », « RT0xxxx: »
$m = [regex]::Match($convTxt, '(?m)^AUTEUR = re\.compile\(r"(.*?)"\s*\r?\n\s*r"(.*?)"\)')
if (-not $m.Success) { throw "Le motif AUTEUR de convertir-horaire.py a changé de forme : cet outil doit être revu." }
$AUTEUR = $m.Groups[1].Value + $m.Groups[2].Value

# Ce qui, dans le ZIP, ne doit pas être recopié.
$EXCLUS = [regex]::new('(vbaProject\.bin|/vbaProject|\.bin$|^docProps/custom\.xml$)', $OPTI)
# Les parties où chercher du texte. Tout le reste est recopié tel quel.
$RX_TEXTE  = [regex]::new('\.(xml|rels|vml)$', $OPTI)
$COMMENTAIRES = [regex]::new('comments\d*\.xml$', $OPTI)

# --- la signature d'un commentaire -----------------------------------------
# Neuf noms sont passés par là : AUTEUR exige une virgule et ne voit ni
# « Nom Prénom : » ni « Prénom: », et rien du tout quand Excel coupe le nom
# en deux morceaux. Cette passe lit la STRUCTURE : elle recolle le texte de
# chaque commentaire, et retire ce qui précède le premier « : » quand cela a
# une forme de nom. Ces formes sont celles de la version Python, recopiées :
# c'est elle que ce jumeau doit rendre, au caractère près.
$NOMS_SIG = @(
    [regex]::new("^[A-ZÀ-Þ][a-zà-ÿ'-]{2,},?\s+[A-ZÀ-Þ][a-zà-ÿ'-]{2,}$", $OPT),   # Nom Prénom
    [regex]::new("^[A-ZÀ-Þ]{4,},\s*[A-ZÀ-Þ]{2,}$", $OPT),                        # NOM, PRÉNOM
    [regex]::new("^[A-ZÀ-Þ]{2,},\s*[A-ZÀ-Þ]{4,}$", $OPT),
    [regex]::new("^[A-ZÀ-Þ][a-zà-ÿ'-]{3,},\s*[A-ZÀ-Þ]{2,4}$", $OPT),            # Nom, APN
    [regex]::new("^[A-ZÀ-Þ]{2,4},\s*[A-ZÀ-Þ][a-zà-ÿ'-]{3,}$", $OPT)             # JBY, Prénom
)
$ORNEMENT = [regex]::new('\s*\([^)]*\)\s*|\s*/\s*[Rr][Tt]\d{4,6}\s*|\s*-\s*[A-ZÀ-Þ]{2,4}\s*$', $OPT)

# UN IDENTIFIANT DE CONNEXION N'EST PAS UN NOM, ET IL DÉSIGNE QUAND MÊME
# QUELQU'UN. Suivi d'un deux-points, c'est une signature : il part en entier.
# Au fil du texte, il est remplacé. Jamais appliqué aux octets du XML.
$LOGIN = [regex]::new('\b[A-Za-z]{2}\d{4,6}\b(\s*:[ \t]*)?', $OPT)

# UNE PERSONNE QUE LE CLASSEUR NE RECENSE PAS : « Prénom Nom (intérimaire … ».
$INTERIMAIRE = [regex]::new(
    "\b([A-ZÀ-Þ][a-zà-ÿ'’-]+)[ \t]+([A-ZÀ-Þ][a-zà-ÿ'’-]{1,}(?:[ \t]+[A-ZÀ-Þ][a-zà-ÿ'’-]{1,})?)" +
    "(?=[ \t]*\([ \t]*int[ée]rim)", $OPT)

# Une cellule qui pourrait porter un nom : des lettres, et la ponctuation
# qu'on met dans un nom. Pas de chiffres.
$NOM_POSSIBLE = [regex]::new("^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s.,'()-]*$", $OPT)
$PARTICULES = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($e in @('de', 'van', 'von', 'der', 'den', 'le', 'la', 'du', 'des',
                 'di', 'dos', 'mac', 'mc')) { [void] $PARTICULES.Add($e) }
# Les mots par lesquels un classeur nomme ses colonnes. « NOM » et
# « PRENOM » côte à côte donnent P + N + M : la ligne d'en-tête se faisait
# prendre pour quelqu'un.
$ENTETES = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($e in @('nom', 'noms', 'prenom', 'prenoms', 'initiales', 'matricule',
                 'service', 'groupe', 'atelier', 'equipe', 'personnel', 'total',
                 'date', 'jour', 'mois', 'fonction', 'poste')) { [void] $ENTETES.Add($e) }
$ACCESSOIRE = [regex]::new('^[a-z]\.?(-[a-z])?\.?$', $OPT)
# Le texte d'une cellule dans le XML, sans avoir à l'analyser : charger
# douze feuilles de plusieurs méga-octets dans un XmlDocument coûte des
# minutes, et on ne cherche ici que du texte.
$RX_CELLULE = [regex]::new('<c\s+([^>]*?)(/>|>(.*?)</c>)', 'Singleline')
$RX_FUSION  = [regex]::new('<mergeCell\b[^>]*\bref="([^"]*)"')


function Plat([string] $t) {
    # Une copie sans accents, de MÊME LONGUEUR que l'original : c'est ce qui
    # permet de comparer sur l'une et de remplacer sur l'autre aux mêmes
    # positions. « Prénom » et « Prenom » se valent sans qu'on écrive les deux.
    if (-not $t) { return '' }
    try { return ($t.Normalize([Text.NormalizationForm]::FormD) -replace '\p{Mn}', '') }
    catch { return $t }
}

function Bouts([string] $t) {
    # re.split(r"[,\s]+", t), sans les morceaux vides
    $out = New-Object 'System.Collections.Generic.List[string]'
    foreach ($b in [regex]::Split($t, '[,\s]+')) { if ($b) { $out.Add($b) } }
    return ,$out
}

function ColNum([string] $lettres) {
    $n = 0
    foreach ($c in $lettres.ToCharArray()) { $n = $n * 26 + ([int][char]$c - 64) }
    return $n
}

function Desechapper([string] $s) {
    # ce que l'analyseur XML rendrait du texte d'une balise
    if ($s.IndexOf('&') -lt 0) { return $s }
    $s = [regex]::Replace($s, '&#x([0-9A-Fa-f]+);', { param($x) [char]::ConvertFromUtf32([Convert]::ToInt32($x.Groups[1].Value, 16)) })
    $s = [regex]::Replace($s, '&#([0-9]+);', { param($x) [char]::ConvertFromUtf32([int] $x.Groups[1].Value) })
    return $s.Replace('&lt;', '<').Replace('&gt;', '>').Replace('&quot;', '"').Replace('&apos;', "'").Replace('&amp;', '&')
}

$SHA1 = [System.Security.Cryptography.SHA1]::Create()
function Empreinte([string] $cle) {
    $h = $SHA1.ComputeHash($UTF8.GetBytes($cle))
    $sb = New-Object System.Text.StringBuilder
    for ($k = 0; $k -lt 5; $k++) { [void] $sb.Append($h[$k].ToString('x2')) }
    return $sb.ToString()
}

function InitialesConv([string] $nom) {
    # L'identifiant anonyme selon la convention maison : première lettre du
    # prénom, puis première et dernière lettre du nom de famille. « Renard P »
    # donne PRD, « Renard P. » donne PRD, « J-M. Renard » donne JRD.
    $n = [regex]::Replace((Plat $nom).Replace('.', ' '), '\([^)]*\)', ' ')
    $parts = Bouts $n
    if ($parts.Count -lt 2) { return $null }
    if ($parts[$parts.Count - 1].Length -le 2) {
        $prenom  = $parts[$parts.Count - 1]
        $famille = -join $parts.GetRange(0, $parts.Count - 1)
    } else {
        $prenom  = $parts[0]
        $famille = -join $parts.GetRange(1, $parts.Count - 1)
    }
    if (-not $prenom -or $famille.Length -lt 2) { return $null }
    return ('' + $prenom[0] + $famille[0] + $famille[$famille.Length - 1]).ToUpperInvariant()
}

$cacheIni = New-Object 'System.Collections.Generic.Dictionary[string,object]'
function Initiales([string] $t) {
    # Les initiales, corrigées EXACTEMENT comme le convertisseur les corrige :
    # sans cela, les deux outils écriraient des identifiants différents pour
    # la même personne.
    if ($cacheIni.ContainsKey($t)) { return $cacheIni[$t] }
    $k = Empreinte ((Plat $t).ToLowerInvariant())
    if ($CORRECTIONS.ContainsKey($k)) { $r = $CORRECTIONS[$k] } else { $r = InitialesConv $t }
    $cacheIni[$t] = $r
    return $r
}

function LireXml([byte[]] $octets) {
    $s = $UTF8.GetString($octets).TrimStart([char]0xFEFF)
    $doc = New-Object System.Xml.XmlDocument
    $doc.LoadXml($s)
    return $doc
}

function Grille([string] $partie, [int[]] $fusions) {
    # { ligne = { colonne = texte } }, dans l'ordre du document — l'ordre
    # compte : à deux lectures possibles d'un même mot, la première apprise
    # l'emporte, comme dans la version Python.
    $txt = $UTF8.GetString($entrees[$partie])
    $out = New-Object 'System.Collections.Generic.Dictionary[int,object]'
    foreach ($m in $RX_CELLULE.Matches($txt)) {
        $attrs  = $m.Groups[1].Value
        $dedans = $m.Groups[3].Value
        if (-not $dedans) { continue }
        $ref = [regex]::Match($attrs, '\br="([A-Z]+)(\d+)"')
        if (-not $ref.Success) { continue }
        $t  = [regex]::Match($attrs, '\bt="([^"]*)"')
        $is = [regex]::Match($dedans, '<is>(.*?)</is>', 'Singleline')
        $v  = [regex]::Match($dedans, '<v>([^<]*)</v>')
        if ($is.Success) {
            $sb = New-Object System.Text.StringBuilder
            foreach ($x in [regex]::Matches($is.Groups[1].Value, '<t(?:\s[^>]*)?>([^<]*)</t>')) {
                [void] $sb.Append((Desechapper $x.Groups[1].Value))
            }
            $val = $sb.ToString()
        } elseif (-not $v.Success) {
            continue
        } elseif ($t.Success -and $t.Groups[1].Value -eq 's') {
            $i = [int] $v.Groups[1].Value
            if ($i -lt 0 -or $i -ge $shared.Count) { continue }
            $val = $shared[$i]
        } else {
            $val = Desechapper $v.Groups[1].Value
        }
        $val = ("$val").Trim()
        if (-not $val) { continue }
        $lig = [int] $ref.Groups[2].Value
        $col = ColNum $ref.Groups[1].Value
        if (-not $out.ContainsKey($lig)) { $out[$lig] = New-Object 'System.Collections.Generic.Dictionary[int,string]' }
        $out[$lig][$col] = $val
    }
    # Une cellule fusionnée ne porte sa valeur qu'en haut à gauche : on la
    # recopie sur son étendue, sur les SEULES lignes demandées (la ligne du
    # poste), et seulement dans les cases vides.
    foreach ($f in $RX_FUSION.Matches($txt)) {
        $r = $f.Groups[1].Value
        if ($r.IndexOf(':') -lt 0) { continue }
        $coins = @()
        foreach ($coin in $r.Split(':')) {
            $mm = [regex]::Match($coin.Trim(), '^([A-Z]+)(\d+)$')
            if (-not $mm.Success) { break }
            $coins += , @([int] $mm.Groups[2].Value, (ColNum $mm.Groups[1].Value))
        }
        if ($coins.Count -ne 2) { continue }
        $l1 = $coins[0][0]; $c1 = $coins[0][1]; $l2 = $coins[1][0]; $c2 = $coins[1][1]
        $la = [Math]::Min($l1, $l2); $lb = [Math]::Max($l1, $l2)
        $ca = [Math]::Min($c1, $c2); $cb = [Math]::Max($c1, $c2)
        $touche = $false
        foreach ($l in $fusions) { if ($l -ge $la -and $l -le $lb) { $touche = $true } }
        if (-not $touche) { continue }
        if (-not $out.ContainsKey($l1) -or -not $out[$l1].ContainsKey($c1)) { continue }
        $val = $out[$l1][$c1]
        if (-not $val) { continue }
        for ($l = $la; $l -le $lb; $l++) {
            if ($fusions -notcontains $l) { continue }
            if (-not $out.ContainsKey($l)) { $out[$l] = New-Object 'System.Collections.Generic.Dictionary[int,string]' }
            for ($c = $ca; $c -le $cb; $c++) {
                if (-not $out[$l].ContainsKey($c) -or -not $out[$l][$c]) { $out[$l][$c] = $val }
            }
        }
    }
    return $out
}

function Formes([string] $nom) {
    # Toutes les façons d'écrire un nom complet. « Nom, Prénom » s'y trouve
    # aussi en « Nom Prénom », « Prénom Nom »… On génère les combinaisons
    # plutôt que de deviner.
    $bouts = New-Object 'System.Collections.Generic.List[string]'
    foreach ($b in [regex]::Split($nom, '[,\s]+')) { if ($b.Trim()) { $bouts.Add($b.Trim()) } }
    $out = New-Object 'System.Collections.Generic.List[string]'
    if ($bouts.Count -eq 0) { return ,$out }
    $inv = New-Object 'System.Collections.Generic.List[string]' (, $bouts)
    $inv.Reverse()
    $vus = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($sep in @(', ', ' ', '  ', ',', '')) {
        foreach ($f in @(($bouts -join $sep), ($inv -join $sep))) {
            if ($f.Length -gt 3 -and $vus.Add($f)) { $out.Add($f) }
        }
    }
    return ,$out
}

function Borner([string] $motif, [string] $texte) {
    # « \b » exige un caractère de mot d'un côté. « Nom P. » finit par un
    # point : y coller « \b » rend le motif impossible à satisfaire, et le nom
    # n'est remplacé qu'à moitié — « ATR A. ».
    if ($texte.Length -eq 0) { return $motif }
    $g = $texte[0]
    $d = $texte[$texte.Length - 1]
    if ([char]::IsLetterOrDigit($g) -or $g -eq '_') { $motif = '\b' + $motif }
    if ([char]::IsLetterOrDigit($d) -or $d -eq '_') { $motif = $motif + '\b' }
    return $motif
}

function Motif([string] $texte) {
    # Un motif qui retrouve le texte quels que soient les accents, la casse et
    # les espaces — le classeur n'est pas régulier là-dessus.
    $plat = (Plat $texte).Trim()
    $bouts = @([regex]::Split($plat, '\s+') | Where-Object { $_ } | ForEach-Object { [regex]::Escape($_) })
    if ($bouts.Count -eq 0) { return $null }
    return (Borner ($bouts -join '[\s,]*') $plat)
}

function MotifSeul([string] $mot) {
    # Un nom de famille ou un prénom SEUL dans sa cellule. On exige la
    # majuscule initiale, et on la protège de l'insensibilité à la casse :
    # « Blanc » et « BLANC » sont des noms, « blanc » est un mot français
    # qu'il ne faut pas remplacer au milieu d'un commentaire.
    $p = Plat $mot
    if ($p.Length -lt 3) { return $null }
    $sb = New-Object System.Text.StringBuilder
    foreach ($c in $p.Substring(1).ToCharArray()) {
        if ([char]::IsLetter($c)) {
            [void] $sb.Append('[' + ([string]$c).ToUpperInvariant() + ([string]$c).ToLowerInvariant() + ']')
        } else {
            [void] $sb.Append([regex]::Escape([string]$c))
        }
    }
    return (Borner ('(?-i:' + [regex]::Escape(([string]$p[0]).ToUpperInvariant()) + ')' + $sb.ToString()) $p)
}

function Sonde([string] $texte) {
    # Le premier mot du texte, en minuscules : s'il n'est pas dans la partie,
    # la règle ne peut pas s'y appliquer.
    $m = [regex]::Match((Plat $texte), '^[^\W\d_]+')
    if ($m.Success) { return $m.Value.ToLowerInvariant() }
    return ''
}

function Remplacer([byte[]] $octets) {
    $txt  = $UTF8.GetString($octets)
    $plat = Plat $txt
    # Si la copie sans accents n'a pas la même longueur, les positions ne
    # correspondent plus : on cherche alors dans l'original, quitte à manquer
    # une graphie. Jamais de remplacement posé au mauvais endroit.
    if ($plat.Length -ne $txt.Length) { $plat = $txt }
    # Une sonde par mot de nom, cherchée UNE fois pour toutes les règles qui
    # la portent : sans ça, deux mille motifs balaient chaque partie.
    $presentes = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($sd in $sondes) {
        if ($plat.IndexOf($sd, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
            [void] $presentes.Add($sd)
        }
    }
    $coupes = New-Object 'System.Collections.Generic.List[object]'
    $ordre = 0
    foreach ($r in $regles) {
        if ($r.Sonde -and -not $presentes.Contains($r.Sonde)) { continue }
        foreach ($m in $r.Rx.Matches($plat)) {
            $coupes.Add([pscustomobject] @{ A = $m.Index; L = $m.Length; Par = $r.Par; O = $ordre })
            $ordre++
        }
    }
    if ($coupes.Count -eq 0) { return [pscustomobject] @{ Octets = $octets; N = 0 } }
    # à position égale, la plus longue d'abord ; à égalité, l'ordre des règles
    $tri = @($coupes | Sort-Object -Property A, @{ Expression = { -$_.L } }, O)
    $sb = New-Object System.Text.StringBuilder
    $pos = 0
    $n = 0
    foreach ($c in $tri) {
        if ($c.A -lt $pos) { continue }          # déjà couvert par une règle plus longue
        [void] $sb.Append($txt, $pos, $c.A - $pos)
        [void] $sb.Append($c.Par)
        $pos = $c.A + $c.L
        $n++
    }
    [void] $sb.Append($txt, $pos, $txt.Length - $pos)
    return [pscustomobject] @{ Octets = $UTF8.GetBytes($sb.ToString()); N = $n }
}


# --- les commentaires, lus par leur STRUCTURE --------------------------------
function ChargerXml([byte[]] $octets) {
    $doc = New-Object System.Xml.XmlDocument
    $doc.PreserveWhitespace = $true
    try { $doc.LoadXml($UTF8.GetString($octets).TrimStart([char]0xFEFF)) } catch { return $null }
    return $doc
}

function EcrireXml($doc) {
    $reglages = New-Object System.Xml.XmlWriterSettings
    $reglages.Encoding = $UTF8
    $reglages.NewLineHandling = [System.Xml.NewLineHandling]::None
    $reglages.Indent = $false
    $ms = New-Object IO.MemoryStream
    $w = [System.Xml.XmlWriter]::Create($ms, $reglages)
    $doc.Save($w)
    $w.Dispose()
    $o = $ms.ToArray()
    $ms.Dispose()
    return ,$o
}

function Morceaux($doc) {
    # chaque commentaire et ses morceaux de texte, dans l'ordre du document
    $ns = New-Object System.Xml.XmlNamespaceManager($doc.NameTable)
    $ns.AddNamespace('m', $NS_M)
    $out = New-Object 'System.Collections.Generic.List[object]'
    foreach ($cm in $doc.SelectNodes('//m:comment', $ns)) {
        $noeuds = @($cm.SelectNodes('.//m:t', $ns))
        $sb = New-Object System.Text.StringBuilder
        foreach ($x in $noeuds) { [void] $sb.Append($x.InnerText) }
        $out.Add([pscustomobject] @{ Noeuds = $noeuds; Joint = $sb.ToString() })
    }
    return ,$out
}

function EditerMorceaux($noeuds, $coupes) {
    # Appliquer des coupes au texte RECOLLÉ d'un commentaire, morceau par
    # morceau, sans déplacer un seul caractère d'un morceau à l'autre :
    # CHAQUE MORCEAU GARDE SA MISE EN FORME. Le barré dit qu'une consigne a
    # été annulée ; le déplacer, c'est réécrire le classeur.
    # $coupes : des objets { A = début ; B = fin ; Rep = remplacement }, en
    # positions du texte recollé, sans chevauchement.
    $textes = @($noeuds | ForEach-Object { $_.InnerText })
    $debuts = @()
    $o = 0
    foreach ($s in $textes) { $debuts += $o; $o += $s.Length }
    $garde = @()
    foreach ($s in $textes) {
        $g = New-Object 'string[]' $s.Length
        for ($k = 0; $k -lt $s.Length; $k++) { $g[$k] = [string] $s[$k] }
        $garde += , $g
    }
    $touches = New-Object 'System.Collections.Generic.HashSet[int]'
    $tri = @($coupes | Sort-Object -Property A, B)
    foreach ($c in $tri) {
        $a = $c.A; $b = $c.B; $rep = $c.Rep
        for ($k = 0; $k -lt $textes.Count; $k++) {
            $d = $debuts[$k]; $f = $d + $textes[$k].Length
            for ($p = [Math]::Max($a, $d); $p -lt [Math]::Min($b, $f); $p++) {
                $garde[$k][$p - $d] = ''
                [void] $touches.Add($k)
            }
        }
        if ($rep) {
            for ($k = 0; $k -lt $textes.Count; $k++) {
                if ($debuts[$k] -le $a -and $a -lt $debuts[$k] + $textes[$k].Length) {
                    $garde[$k][$a - $debuts[$k]] = $rep + $garde[$k][$a - $debuts[$k]]
                    [void] $touches.Add($k)
                    break
                }
            }
        }
    }
    foreach ($k in $touches) {
        $noeuds[$k].InnerText = -join $garde[$k]
        [void] $noeuds[$k].SetAttribute('space', $NS_XML, 'preserve')
    }
    return ($touches.Count -gt 0)
}

function EstNom([string] $t) {
    $t = $ORNEMENT.Replace($t, '').Trim()
    if (-not $t) { return $false }
    foreach ($f in $NOMS_SIG) { if ($f.IsMatch($t)) { return $true } }
    return $false
}

function SansSignature([byte[]] $octets) {
    # Retirer la signature en tête de chaque commentaire, et les auteurs. Une
    # signature est COURTE et d'un seul tenant : sans ces deux bornes, la
    # règle avalerait le corps des commentaires qui portent un « MPE : » en
    # plein milieu.
    $doc = ChargerXml $octets
    if (-not $doc) { return [pscustomobject] @{ Octets = $octets; N = 0 } }
    $ns = New-Object System.Xml.XmlNamespaceManager($doc.NameTable)
    $ns.AddNamespace('m', $NS_M)
    $n = 0
    $liste = $doc.DocumentElement.SelectSingleNode('m:authors', $ns)
    if ($liste) {
        foreach ($x in @($liste.ChildNodes | Where-Object { $_.NodeType -eq 'Element' })) {
            $v = $x.InnerText.Trim()
            if ($v -and $v -ne 'Auteur') { $x.InnerText = 'Auteur'; $n++ }
        }
    }
    foreach ($cm in (Morceaux $doc)) {
        $joint = $cm.Joint
        $i = $joint.IndexOf(':')
        if (-not (0 -lt $i -and $i -le 40)) { continue }
        $tete = $joint.Substring(0, $i)
        if ($tete.Contains("`n") -or -not (EstNom $tete)) { continue }
        $fin = $i + 1
        while ($fin -lt $joint.Length -and " `t`r`n".IndexOf($joint[$fin]) -ge 0) { $fin++ }
        if (EditerMorceaux $cm.Noeuds @([pscustomobject] @{ A = 0; B = $fin; Rep = '' })) { $n++ }
    }
    if ($n -eq 0) { return [pscustomobject] @{ Octets = $octets; N = 0 } }
    return [pscustomobject] @{ Octets = (EcrireXml $doc); N = $n }
}

function SansLogin([byte[]] $octets) {
    # Retirer les identifiants de connexion du texte des commentaires.
    $doc = ChargerXml $octets
    if (-not $doc) { return [pscustomobject] @{ Octets = $octets; N = 0 } }
    $n = 0
    foreach ($cm in (Morceaux $doc)) {
        $coupes = @()
        foreach ($m in $LOGIN.Matches($cm.Joint)) {
            if ($m.Groups[1].Success) { $rep = '' } else { $rep = '(identifiant retiré)' }
            $coupes += [pscustomobject] @{ A = $m.Index; B = $m.Index + $m.Length; Rep = $rep }
        }
        if ($coupes.Count -and (EditerMorceaux $cm.Noeuds $coupes)) { $n += $coupes.Count }
    }
    if ($n -eq 0) { return [pscustomobject] @{ Octets = $octets; N = 0 } }
    return [pscustomobject] @{ Octets = (EcrireXml $doc); N = $n }
}

function SansInterimaire([byte[]] $octets) {
    # Remplacer par son trigramme le nom suivi de « (intérimaire ».
    $doc = ChargerXml $octets
    if (-not $doc) { return [pscustomobject] @{ Octets = $octets; N = 0 } }
    $n = 0
    foreach ($cm in (Morceaux $doc)) {
        $coupes = @()
        foreach ($m in $INTERIMAIRE.Matches($cm.Joint)) {
            $tri = Initiales ($m.Groups[1].Value + ' ' + $m.Groups[2].Value)
            if ($tri) { $coupes += [pscustomobject] @{ A = $m.Index; B = $m.Index + $m.Length; Rep = $tri } }
        }
        if ($coupes.Count -and (EditerMorceaux $cm.Noeuds $coupes)) { $n += $coupes.Count }
    }
    if ($n -eq 0) { return [pscustomobject] @{ Octets = $octets; N = 0 } }
    return [pscustomobject] @{ Octets = (EcrireXml $doc); N = $n }
}

# --- le paquet : une copie qui s'ouvre, et qui ne dit rien de la maison ------
# Retirer les macros laissait un paquet qui les annonçait encore ; et le
# classeur portait l'étiquette de sensibilité de l'employeur et le chemin
# réseau d'où il a été enregistré. Rien de cela n'est un nom ; rien de cela
# n'a à vivre dans un dépôt public.
function Paquet([string] $nom, [byte[]] $octets, $retires) {
    if ($nom -eq '[Content_Types].xml') {
        $s = $UTF8.GetString($octets)
        $s = $s.Replace('application/vnd.ms-excel.sheet.macroEnabled.main+xml',
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml')
        foreach ($r in $retires) {
            $s = [regex]::Replace($s, '<Override PartName="/' + [regex]::Escape($r) + '"[^>]*/>', '')
        }
        return ,$UTF8.GetBytes($s)
    }
    if ($nom.EndsWith('.rels')) {
        $bases = New-Object 'System.Collections.Generic.HashSet[string]'
        foreach ($r in $retires) { [void] $bases.Add(($r -split '/')[-1]) }
        $s = $UTF8.GetString($octets)
        $s = [regex]::Replace($s, '<Relationship\b[^>]*/>', {
            param($x)
            $cible = [regex]::Match($x.Value, 'Target="([^"]*)"')
            if ($cible.Success -and $bases.Contains(($cible.Groups[1].Value -split '/')[-1])) { return '' }
            return $x.Value
        }.GetNewClosure())
        return ,$UTF8.GetBytes($s)
    }
    if ($nom -eq 'xl/workbook.xml') {
        $s = $UTF8.GetString($octets)
        $s = [regex]::Replace($s, '<mc:AlternateContent\b(?:(?!</mc:AlternateContent>).)*?absPath(?:(?!</mc:AlternateContent>).)*</mc:AlternateContent>', '', 'Singleline')
        return ,$UTF8.GetBytes($s)
    }
    return ,$octets
}


# --- le classeur, lu une fois pour toutes --------------------------------
$src = (Resolve-Path -LiteralPath $Source).ProviderPath
if ([IO.Path]::IsPathRooted($Sortie)) { $dst = $Sortie }
else { $dst = Join-Path (Get-Location).ProviderPath $Sortie }
$dst = [IO.Path]::GetFullPath($dst)

$entrees = New-Object System.Collections.Specialized.OrderedDictionary
$dates   = @{}
$zin = [IO.Compression.ZipFile]::OpenRead($src)
try {
    foreach ($e in $zin.Entries) {
        $ms = New-Object IO.MemoryStream
        $st = $e.Open(); $st.CopyTo($ms); $st.Dispose()
        $entrees[$e.FullName] = $ms.ToArray()
        $dates[$e.FullName] = $e.LastWriteTime
        $ms.Dispose()
    }
} finally { $zin.Dispose() }

foreach ($requis in @('xl/workbook.xml', 'xl/_rels/workbook.xml.rels')) {
    if (-not $entrees.Contains($requis)) {
        throw "Ce fichier n'a pas la forme d'un classeur Excel : $requis est absent. " +
              "Est-ce bien le .xlsm, et non un raccourci ou un fichier OneDrive non téléchargé ?"
    }
}

# --- les feuilles, dans l'ordre du classeur, puis l'annuaire ----------------
$wb   = LireXml $entrees['xl/workbook.xml']
$nswb = New-Object System.Xml.XmlNamespaceManager($wb.NameTable)
$nswb.AddNamespace('m', $NS_M)

$wbr  = LireXml $entrees['xl/_rels/workbook.xml.rels']
$nsr  = New-Object System.Xml.XmlNamespaceManager($wbr.NameTable)
$nsr.AddNamespace('p', $NS_P)
$rels = @{}
foreach ($r in $wbr.SelectNodes('//p:Relationship', $nsr)) {
    $rels[$r.GetAttribute('Id')] = $r.GetAttribute('Target')
}

$feuilles = New-Object 'System.Collections.Generic.Dictionary[string,string]'
foreach ($sh in $wb.SelectNodes('//m:sheets/m:sheet', $nswb)) {
    $cible = ([string] $rels[$sh.GetAttribute('id', $NS_R)]).TrimStart('/')
    if (-not $cible.StartsWith('xl/')) { $cible = 'xl/' + $cible }
    $feuilles[$sh.GetAttribute('name')] = $cible
}

$shared = New-Object 'System.Collections.Generic.List[string]'
if ($entrees.Contains('xl/sharedStrings.xml')) {
    $ss  = LireXml $entrees['xl/sharedStrings.xml']
    $nss = New-Object System.Xml.XmlNamespaceManager($ss.NameTable)
    $nss.AddNamespace('m', $NS_M)
    foreach ($si in $ss.SelectNodes('//m:si', $nss)) {
        $sb = New-Object System.Text.StringBuilder
        foreach ($t in $si.SelectNodes('.//m:t', $nss)) { [void] $sb.Append($t.InnerText) }
        $shared.Add($sb.ToString())
    }
}

# Chaque feuille, lue une fois, la ligne du poste dépliée sur ses fusions.
$grilles = New-Object 'System.Collections.Generic.Dictionary[string,object]'
foreach ($f in $feuilles.Keys) {
    if ($entrees.Contains($feuilles[$f])) { $grilles[$f] = Grille $feuilles[$f] @($LIGNE_POSTE) }
}

# La feuille « Personnel » donne la correspondance officielle nom → initiales.
$annuaire = New-Object 'System.Collections.Generic.Dictionary[string,string]'
if ($grilles.ContainsKey('Personnel')) {
    foreach ($ligne in $grilles['Personnel'].Values) {
        $nom = ''; $ini = ''
        if ($ligne.ContainsKey(1)) { $nom = ([string] $ligne[1]).Trim() }
        if ($ligne.ContainsKey(2)) { $ini = ([string] $ligne[2]).Trim() }
        if ($nom -and $ini -and $nom -ne '0' -and $nom -ne 'Nom') {
            $annuaire[(Plat $nom).ToLowerInvariant()] = $ini.ToUpperInvariant()
        }
    }
}
if ($annuaire.Count -eq 0) {
    throw "Aucun nom trouvé : la feuille « Personnel » a-t-elle bougé ?"
}

# Les noms connus, et le trigramme qui les remplace. L'annuaire officiel d'abord.
$noms = New-Object 'System.Collections.Generic.Dictionary[string,string]'
foreach ($k in $annuaire.Keys) { $noms[$k] = $annuaire[$k] }
$connus = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($v in $annuaire.Values) { [void] $connus.Add($v) }

# Les mots par lesquels on connaît déjà chaque personne. Une nouvelle façon
# de l'écrire devra en partager un : sans cela, « PM DS-CE » donne P + D + E,
# retombe sur le trigramme de quelqu'un, et un code de délégation syndicale
# devient un nom.
$connues = New-Object 'System.Collections.Generic.Dictionary[string,object]'
$parMot  = New-Object 'System.Collections.Generic.Dictionary[string,object]'

function MotsDe([string] $cle) {
    $out = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($b in [regex]::Split($cle, '[,\s]+')) { if ($b.Length -ge 3) { [void] $out.Add($b) } }
    return ,$out
}

function Retenir([string] $cle, [string] $ini) {
    if (-not $connues.ContainsKey($ini)) {
        $connues[$ini] = New-Object 'System.Collections.Generic.HashSet[string]'
    }
    foreach ($b in (MotsDe $cle)) {
        [void] $connues[$ini].Add($b)
        if (-not $parMot.ContainsKey($b)) { $parMot[$b] = New-Object 'System.Collections.Generic.HashSet[string]' }
        [void] $parMot[$b].Add($ini)
    }
}

function Apprendre([string] $cle, [string] $ini) {
    if (-not $cle -or -not $ini -or $noms.ContainsKey($cle)) { return }
    $noms[$cle] = $ini
    Retenir $cle $ini
}

foreach ($cle in @($annuaire.Keys)) { Retenir $cle $annuaire[$cle] }

function Candidat($v) {
    # Un trigramme n'est pas un nom : sans cette garde, « ATR » devient
    # l'alias de lui-même, entre dans la liste surveillée, et la relecture
    # signale comme reste chaque trigramme qu'on vient d'écrire.
    $t = ("$v").Trim()
    if ($t.Length -lt 3 -or $t.Length -gt 40) { return $null }
    if (-not $NOM_POSSIBLE.IsMatch($t)) { return $null }
    $lettres = 0
    foreach ($c in $t.ToCharArray()) { if ([char]::IsLetter($c)) { $lettres++ } }
    if ($lettres -lt 3) { return $null }
    if ($connus.Contains((Plat $t).ToUpperInvariant())) { return $null }
    return $t
}

function IniConnues([string] $t) {
    # Le trigramme que ce texte donne, s'il en donne un de connu.
    #
    # L'ordre inversé — « Renard, Paul » pour PRD — n'est essayé que si
    # le texte porte une VIRGULE. Sans cette condition, trois lettres se
    # rencontrent trop facilement : « terr arr » lu à l'envers donne ATR,
    # « pm ds-ce » donne PDE, et des noms d'ateliers devenaient des gens.
    $i = Initiales $t
    if ($i -and $connus.Contains($i)) { return $i }
    if ($t.Contains(',')) {
        $bouts = Bouts $t
        if ($bouts.Count -gt 1) {
            $bouts.Reverse()
            $i = Initiales ($bouts -join ' ')
            if ($i -and $connus.Contains($i)) { return $i }
        }
    }
    return $null
}

function IniDeLigne([string] $famille, [string] $prenom) {
    # LE TRIGRAMME QUE LE CONVERTISSEUR DONNE À CETTE LIGNE, s'il en décide
    # un autre que les initiales : une CORRECTION du client, ou l'onglet
    # « Personnel ». La même clé que polyvalence() du convertisseur — « Nom P. ».
    $p1 = ''
    if ($prenom) { $p1 = $prenom.Substring(0, 1) }
    $cle = (Plat ($famille + ' ' + $p1 + '.')).ToLowerInvariant()
    $k = Empreinte $cle
    if ($CORRECTIONS.ContainsKey($k)) { return $CORRECTIONS[$k] }
    if ($annuaire.ContainsKey($cle)) { return $annuaire[$cle] }
    return $null
}

function Accessoire([string] $bout) {
    # Ce qui peut entourer un nom sans en être un : une initiale, un point,
    # une particule.
    return ($bout.Length -le 2 -or $PARTICULES.Contains($bout) -or $ACCESSOIRE.IsMatch($bout))
}

function SansParentheses([string] $t) {
    # « Nom P.(ass.Us.) » : la parenthèse dit le rôle, pas la personne
    $n = (([regex]::Split(([regex]::Replace($t, '\([^)]*\)', ' ')), '\s+') | Where-Object { $_ }) -join ' ')
    if ($n) { return $n }
    return $t
}

# --- les gens, et toutes les façons dont le classeur les écrit -----------
# On récolte d'abord les cellules qui pourraient porter un nom.
$recolte = New-Object 'System.Collections.Generic.Dictionary[string,object]'
foreach ($f in $grilles.Keys) {
    $mots = New-Object 'System.Collections.Generic.Dictionary[int,object]'
    foreach ($l in $grilles[$f].Keys) {
        $m = New-Object 'System.Collections.Generic.Dictionary[int,string]'
        foreach ($c in $grilles[$f][$l].Keys) {
            $t = Candidat $grilles[$f][$l][$c]
            if ($t) { $m[$c] = $t }
        }
        $mots[$l] = $m
    }
    $recolte[$f] = $mots
}

# LA LIGNE DES NOMS. La ligne 10 de chaque feuille de personnes porte les
# gens, un par colonne : ce qui est écrit là EST un nom. Seulement dans les
# feuilles de personnes — une feuille cachée porte « P. arr » en ligne 10.
foreach ($f in $recolte.Keys) {
    if (-not $FEUILLES_PERS.Contains($f)) { continue }
    if (-not $recolte[$f].ContainsKey($LIGNE_NOMS)) { continue }
    foreach ($t in @($recolte[$f][$LIGNE_NOMS].Values)) {
        $ini = Initiales $t
        if (-not $ini -or $ini -notmatch '^\p{L}+$') { continue }
        $cle = (Plat $t).ToLowerInvariant()
        if ($annuaire.ContainsKey($cle)) { $ini = $annuaire[$cle] }
        Apprendre $cle $ini
    }
}

# Le nom et le prénom dans DEUX COLONNES — la feuille « Polyvalence » les
# range ainsi. On ne devine pas quelles colonnes : on cherche le couple qui,
# sur TOUTE la feuille, redonne des trigrammes connus — et dont les deux
# colonnes portent des valeurs majoritairement DISTINCTES.
foreach ($f in $recolte.Keys) {
    $mots = $recolte[$f]
    $scores = New-Object 'System.Collections.Generic.Dictionary[string,int]'
    foreach ($m in $mots.Values) {
        if ($m.Count -lt 2) { continue }
        foreach ($i in $m.Keys) {
            foreach ($j in $m.Keys) {
                if ($i -eq $j) { continue }
                $ini = Initiales ($m[$i] + ' ' + $m[$j])
                if ($ini -and $connus.Contains($ini)) {
                    $k = "$i/$j"
                    if ($scores.ContainsKey($k)) { $scores[$k]++ } else { $scores[$k] = 1 }
                }
            }
        }
    }
    foreach ($k in @($scores.Keys)) {
        if ($scores[$k] -lt 10) { continue }
        $ij = $k -split '/'
        $i = [int] $ij[0]
        $j = [int] $ij[1]
        $paires = New-Object 'System.Collections.Generic.List[object]'
        foreach ($m in $mots.Values) {
            if ($m.ContainsKey($i) -and $m.ContainsKey($j)) { $paires.Add($m) }
        }
        if ($paires.Count -lt 10) { continue }
        $di = New-Object 'System.Collections.Generic.HashSet[string]'
        $dj = New-Object 'System.Collections.Generic.HashSet[string]'
        foreach ($m in $paires) { [void] $di.Add($m[$i]); [void] $dj.Add($m[$j]) }
        if ([Math]::Min($di.Count, $dj.Count) * 2 -lt $paires.Count) { continue }
        # Le couple est établi : chaque ligne porte alors une personne, même
        # absente de l'annuaire. LE PRÉNOM SEUL suit la décision du client, et
        # lui seul ; le NOM DE FAMILLE garde les initiales — souvent partagé,
        # le faire suivre a changé 460 signatures d'un auteur en celles d'un
        # homonyme, le 26/09/2026.
        foreach ($m in $paires) {
            if ($ENTETES.Contains((Plat $m[$i]).ToLowerInvariant()) -or
                $ENTETES.Contains((Plat $m[$j]).ToLowerInvariant())) { continue }
            $ini = Initiales ($m[$i] + ' ' + $m[$j])
            if (-not $ini) { continue }
            $iniI = $ini; $iniJ = $ini
            $dl = IniDeLigne $m[$i] $m[$j]
            if ($dl) { $iniJ = $dl }
            else {
                $dl = IniDeLigne $m[$j] $m[$i]
                if ($dl) { $iniI = $dl }
            }
            Apprendre ((Plat $m[$i]).ToLowerInvariant()) $iniI
            Apprendre ((Plat $m[$j]).ToLowerInvariant()) $iniJ
        }
    }
}

# Les variantes : « Nom P. », « J-M. Nom », « Nom P.(ass.Us.) ». On ne les
# croit que si elles partagent un mot avec une façon déjà connue d'écrire
# cette personne-là — ou si un de leurs mots ne désigne qu'une personne :
# « de Nomlong P. » porte « nomlong », et c'est assez.
foreach ($f in $recolte.Keys) {
    foreach ($m in $recolte[$f].Values) {
        foreach ($t0 in @($m.Values)) {
            $t = SansParentheses $t0
            $cle = (Plat $t).ToLowerInvariant()
            if ($noms.ContainsKey($cle)) { continue }
            # Encore faut-il que la cellule ait la forme d'un nom : tous ses
            # morceaux doivent être un mot de nom connu, une particule, ou une
            # initiale. Sans quoi « Renard de la ligne » deviendrait le
            # trigramme tout entier.
            $bouts = Bouts $cle
            $vises = New-Object 'System.Collections.Generic.HashSet[string]'
            foreach ($b in $bouts) { if ($parMot.ContainsKey($b)) { $vises.UnionWith($parMot[$b]) } }
            if ($vises.Count -gt 0 -and $bouts.Count -le 4) {
                $forme = $true
                foreach ($b in $bouts) { if (-not $parMot.ContainsKey($b) -and -not (Accessoire $b)) { $forme = $false } }
                if ($forme -and $vises.Count -eq 1) {
                    Apprendre $cle (@($vises)[0])
                    continue
                }
            }
            $ini = IniConnues $t
            if ($ini -and $connues.ContainsKey($ini)) {
                $partage = $false
                foreach ($b in (MotsDe $cle)) { if ($connues[$ini].Contains($b)) { $partage = $true } }
                if ($partage) { Apprendre $cle $ini }
            }
        }
    }
}

# LES AUTEURS DE COMMENTAIRES SONT DES NOMS, au même titre que la ligne des
# noms — et pas seulement quelque chose à effacer : une seconde signature au
# milieu d'un commentaire ne disparaît que si le nom y est RECONNU. Pas de
# corroboration à chercher : ce qu'Excel écrit dans <author> EST le nom
# d'une personne. On exige seulement deux à quatre morceaux.
$auteurs = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($nom in @($entrees.Keys)) {
    if (-not $COMMENTAIRES.IsMatch($nom)) { continue }
    $contenu = $UTF8.GetString($entrees[$nom])
    foreach ($m in [regex]::Matches($contenu, '<author>([^<]*)</author>')) {
        $brut = $m.Groups[1].Value.Replace('&amp;', '&').Replace('&lt;', '<').Replace('&gt;', '>').Replace('&quot;', '"').Replace('&apos;', "'")
        $t = Candidat $brut
        if ($t) { [void] $auteurs.Add($t) }
    }
}
$auteursTries = New-Object 'System.Collections.Generic.List[string]' (, [string[]] @($auteurs))
$auteursTries.Sort([StringComparer]::Ordinal)

# Un nom qu'on n'a pas su attribuer ne doit pas pour autant sortir en
# silence : ses mots vont sous surveillance, la garantie détruit la sortie
# et le dit.
$orphelins = New-Object 'System.Collections.Generic.List[object]'
$mintes = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($t0 in $auteursTries) {
    $t = SansParentheses $t0
    $cle = (Plat $t).ToLowerInvariant()
    $bouts = Bouts $cle
    if ($bouts.Count -lt 2 -or $bouts.Count -gt 4) { continue }
    $entete = $false
    foreach ($b in $bouts) { if ($ENTETES.Contains($b)) { $entete = $true } }
    if ($entete) { continue }
    $vises = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($b in $bouts) { if ($parMot.ContainsKey($b)) { $vises.UnionWith($parMot[$b]) } }
    $ini = $null
    if ($vises.Count -eq 1) { $ini = @($vises)[0] }
    if (-not $ini) { $ini = IniConnues $t }
    if (-not $ini) {
        # Personne de connu : ses initiales tiennent lieu d'identifiant — sauf
        # un code DÉJÀ pris, qui troquerait une fuite contre une fausse
        # attribution.
        $cand = Initiales $t
        if ($cand -and $cand -match '^\p{L}+$' -and -not $connus.Contains($cand) -and -not $mintes.Contains($cand)) {
            $ini = $cand
            [void] $mintes.Add($cand)
        } else {
            foreach ($b in $bouts) { if ($b.Length -ge 3) { $orphelins.Add([pscustomobject] @{ Bout = $b; Ini = '?' }) } }
            continue
        }
    }
    Apprendre $cle $ini
    foreach ($b in $bouts) {
        if ($b.Length -ge 3 -and -not $PARTICULES.Contains($b) -and -not $ENTETES.Contains($b)) { Apprendre $b $ini }
    }
}

# --- les règles, et ce qu'on surveillera dans la sortie -------------------
$pesees    = New-Object 'System.Collections.Generic.List[object]'
$surveille = New-Object 'System.Collections.Generic.List[object]'
$rang = 0
foreach ($cle in $noms.Keys) {
    $ini = $noms[$cle]
    $bouts = Bouts $cle
    if ($bouts.Count -gt 1) {
        foreach ($forme in (Formes $cle)) {
            $m = Motif $forme
            if ($m) {
                $pesees.Add([pscustomobject] @{ Poids = $forme.Length; Motif = $m; Par = $ini; Sonde = (Sonde $forme); Rang = $rang })
                $rang++
            }
        }
    } else {
        $m = MotifSeul $cle
        if ($m) {
            $pesees.Add([pscustomobject] @{ Poids = $cle.Length; Motif = $m; Par = $ini; Sonde = (Sonde $cle); Rang = $rang })
            $rang++
        }
    }
    foreach ($b in $bouts) {
        if ($b.Length -ge 3) { $surveille.Add([pscustomobject] @{ Bout = $b; Ini = $ini }) }
    }
}
foreach ($o in $orphelins) { $surveille.Add($o) }

# Les règles qui attrapent le plus long d'abord : « Renard P. » avant
# « Renard », sans quoi il resterait « PRD P. ». On pèse ce que la règle
# ATTRAPE et non la longueur du motif.
$regles = New-Object 'System.Collections.Generic.List[object]'
foreach ($p in @($pesees | Sort-Object -Property @{ Expression = { -$_.Poids } }, Rang)) {
    $regles.Add([pscustomobject] @{ Rx = [regex]::new($p.Motif, $OPTI); Par = $p.Par; Sonde = $p.Sonde })
}
# LE BLANC QUI PRÉCÈDE UNE SIGNATURE RESTE : il devient un regard en
# arrière, qui borne la signature sans en faire partie. Sans quoi « remplace
# ATA\nNom, Prénom: remplace GPS » devenait « remplace ATAremplace GPS ».
$i = $AUTEUR.IndexOf('(?:^|\s)')
$auteurRx = $AUTEUR
if ($i -ge 0) { $auteurRx = $AUTEUR.Substring(0, $i) + '(?:^|(?<=\s))' + $AUTEUR.Substring($i + 8) }
$regles.Add([pscustomobject] @{ Rx = [regex]::new($auteurRx, $OPTI); Par = ''; Sonde = '' })
$sondes = @($regles | ForEach-Object { $_.Sonde } | Where-Object { $_ } | Sort-Object -Unique)

$tol = @()
if ($Tolerer) {
    $tol = @($Tolerer -split ',' | ForEach-Object { (Plat $_).Trim().ToLowerInvariant() } | Where-Object { $_ })
}

# --- la recopie ----------------------------------------------------------
$depart = "{0} nom(s) connu(s) · {1} règle(s) · {2} sonde(s) · lecture en cours…"
Write-Host ($depart -f $noms.Count, $regles.Count, $sondes.Count)
# On écrit À CÔTÉ. Tant que la garantie n'est pas franchie, le fichier peut
# porter des noms : il n'a rien à faire à sa destination. Il n'y prend sa
# place qu'à la fin.
$encours = $dst + '.en-cours'
if (Test-Path -LiteralPath $encours) { Remove-Item -LiteralPath $encours -Force }
$retires = @($entrees.Keys | Where-Object { $EXCLUS.IsMatch($_) })
$total = 0
$parties = 0
$logins = 0
$zout = [IO.Compression.ZipFile]::Open($encours, [IO.Compression.ZipArchiveMode]::Create)
try {
    foreach ($nom in @($entrees.Keys)) {
        if ($EXCLUS.IsMatch($nom)) {
            Write-Host "  écarté : $nom"
            continue
        }
        $donnee = $entrees[$nom]
        if ($RX_TEXTE.IsMatch($nom)) {
            # LA SIGNATURE D'ABORD, LE REMPLACEMENT ENSUITE : depuis que les
            # auteurs sont appris, leur nom remplacé d'abord rendrait la
            # signature méconnaissable. Les identifiants de connexion, eux,
            # après les noms : un login est le suffixe ordinaire d'une
            # signature.
            $n = 0
            $commentaire = $COMMENTAIRES.IsMatch($nom)
            if ($commentaire) { $res = SansSignature $donnee; $donnee = $res.Octets; $n += $res.N }
            $res = Remplacer $donnee; $donnee = $res.Octets; $n += $res.N
            if ($commentaire) {
                $res = SansInterimaire $donnee; $donnee = $res.Octets; $n += $res.N
                $res = SansLogin $donnee; $donnee = $res.Octets; $n += $res.N; $logins += $res.N
            }
            if ($nom.StartsWith('docProps/')) {
                $s = $UTF8.GetString($donnee)
                $s = [regex]::Replace($s, '<(dc:creator|cp:lastModifiedBy)>[^<]*</\1>', '<$1></$1>')
                $donnee = $UTF8.GetBytes($s)
            }
            $donnee = Paquet $nom $donnee $retires
            $total += $n
            if ($n) { $parties++ }
        }
        $e  = $zout.CreateEntry($nom, [IO.Compression.CompressionLevel]::Optimal)
        # La date du classeur source, pour que deux conversions du même
        # fichier donnent la même sortie.
        if ($dates.ContainsKey($nom)) { $e.LastWriteTime = $dates[$nom] }
        $st = $e.Open(); $st.Write($donnee, 0, $donnee.Length); $st.Dispose()
    }
} finally { $zout.Dispose() }

# --- la garantie : relire, et chercher ce qu'on vient de remplacer --------
$restes = New-Object 'System.Collections.Generic.List[object]'
$zv = [IO.Compression.ZipFile]::OpenRead($encours)
try {
    foreach ($e in $zv.Entries) {
        if (-not $RX_TEXTE.IsMatch($e.FullName)) { continue }
        $ms = New-Object IO.MemoryStream
        $st = $e.Open(); $st.CopyTo($ms); $st.Dispose()
        $plat = Plat ($UTF8.GetString($ms.ToArray()))
        $ms.Dispose()
        foreach ($w in $surveille) {
            if ($tol -contains $w.Bout) { continue }
            if ($plat.IndexOf($w.Bout, [StringComparison]::OrdinalIgnoreCase) -lt 0) { continue }
            foreach ($m in [regex]::Matches($plat, '\b' + [regex]::Escape($w.Bout) + '\b', $OPTI)) {
                # un mot courant écrit en minuscules n'est pas un nom
                $brut = $plat.Substring($m.Index, $m.Length)
                if ([char]::IsLower($brut[0])) { continue }
                $a = [Math]::Max(0, $m.Index - 30)
                $b = [Math]::Min($plat.Length, $m.Index + $m.Length + 30)
                $restes.Add([pscustomobject] @{
                    Fichier = $e.FullName; Ini = $w.Ini; Mot = $brut
                    Ctx = ($plat.Substring($a, $b - $a) -replace '\s+', ' ') })
            }
        }
    }
} finally { $zv.Dispose() }

if ($restes.Count -gt 0) {
    Remove-Item -LiteralPath $encours -Force
    Write-Host ''
    Write-Host ("{0} reste(s) de nom dans la sortie — fichier détruit :" -f $restes.Count) -ForegroundColor Red
    foreach ($r in ($restes | Select-Object -First 20)) {
        Write-Host ("   {0,-22} {1,-14} ({2})  …{3}…" -f $r.Fichier, $r.Mot, $r.Ini, $r.Ctx)
    }
    Write-Host ''
    Write-Host "Si l'un d'eux n'est pas un nom — « Marchand » peut être un mot — relancer avec"
    Write-Host "  -Tolerer mot1,mot2   APRÈS l'avoir lu."
    if ($journal) { try { Stop-Transcript | Out-Null } catch { } }
    exit 2
}

if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Force }
Move-Item -LiteralPath $encours -Destination $dst -Force
$taille = (Get-Item -LiteralPath $dst).Length
$resume = "{0} nom(s) connu(s) · {1} remplacement(s) dans {2} partie(s) · {3} Mo"
Write-Host ($resume -f $noms.Count, $total, $parties, ($taille / 1MB).ToString('0.0', [Globalization.CultureInfo]::InvariantCulture))
Write-Host ("{0} identifiant(s) de connexion retiré(s) des commentaires" -f $logins)
Write-Host 'Aucun nom ne subsiste : vérifié sur la sortie.' -ForegroundColor Green
if ($journal) { try { Stop-Transcript | Out-Null } catch { } }
