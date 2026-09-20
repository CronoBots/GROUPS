<#
    Recopie le récapitulatif Excel en remplaçant les noms par les trigrammes.

        .\anonymiser-classeur.ps1 "Recapitulatif.xlsm" classeur-2026.xlsx

    POURQUOI CETTE VERSION. C'est le portage de tools/anonymiser-classeur.py
    pour les postes qui n'ont pas Python — PowerShell, lui, est sur tout
    Windows, et il n'y a rien à installer.

    Le travail est le même, et il n'interprète rien : le classeur est ouvert
    comme l'archive ZIP qu'il est, les noms sont remplacés partout où ils
    apparaissent, puis on referme. Feuilles, formules, mises en forme,
    commentaires, colonnes qu'on n'a pas encore comprises : tout passe intact.

    CE QUI SORT DU FICHIER :
      - les noms sous toutes leurs formes, remplacés par le trigramme ;
      - les auteurs de commentaires, préfixés à leur texte ;
      - les macros (vbaProject.bin) : d'où un .xlsx, pas un .xlsm ;
      - les propriétés du document : auteur, dernier enregistreur.

    GARANTIE. Après écriture, la sortie est relue entièrement et l'outil y
    CHERCHE les noms qu'il vient de remplacer. S'il en trouve un seul, il
    détruit sa sortie et s'arrête avec le détail. Un anonymiseur qui peut
    laisser passer un nom sans le dire ne vaut rien.

    Tout ce qui s'affiche part aussi dans anonymiser-journal.txt : une fenêtre
    qui se referme emporterait l'erreur avec elle.
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

# Ce qui, dans le ZIP, ne doit pas être recopié.
$EXCLUS = [regex]::new('(vbaProject\.bin|/vbaProject|\.bin$)', 'IgnoreCase')
# Les parties où chercher du texte. Tout le reste est recopié tel quel.
$TEXTE  = [regex]::new('\.(xml|rels|vml)$', 'IgnoreCase')
# « Nom, Prénom: », « Nom, Prénom (external): », « RT01386: »
$AUTEUR = "(?:^|\s)(?:[A-ZÉÈÀ][\wÉÈÀéèàêç'-]+,\s*[A-ZÉÈÀ][\wÉÈÀéèàêç'-]+(?:\s*\([^)]*\))?|[Rr][Tt]\d{4,6}|Auteur)\s*:\s*"
# Une cellule qui pourrait porter un nom : des lettres, et la ponctuation
# qu'on met dans un nom. Pas de chiffres.
$NOM_POSSIBLE = [regex]::new("^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s.,'()-]*$")
# Le texte d'une cellule dans le XML, sans avoir à l'analyser.
$RX_CELLULE = [regex]::new('<c\s+([^>]*?)(/>|>(.*?)</c>)', 'Singleline')
$RX_TEXTE = [regex]::new('<(?:t|v)(?:\s[^>]*)?>([^<>&]{3,40})</(?:t|v)>')


function Plat([string] $t) {
    # Une copie sans accents, de MÊME LONGUEUR que l'original : c'est ce qui
    # permet de comparer sur l'une et de remplacer sur l'autre aux mêmes
    # positions. « Prénom » et « Prénom » se valent sans qu'on écrive les deux.
    if (-not $t) { return '' }
    try { return ($t.Normalize([Text.NormalizationForm]::FormD) -replace '\p{Mn}', '') }
    catch { return $t }
}

function ColNum([string] $lettres) {
    $n = 0
    foreach ($c in $lettres.ToCharArray()) { $n = $n * 26 + ([int][char]$c - 64) }
    return $n
}

function Initiales([string] $nom) {
    # L'identifiant anonyme selon la convention maison : première lettre du
    # prénom, puis première et dernière lettre du nom de famille. « Renard V »
    # donne VBN, « Nom A. » donne ATR, « P-Y. Nom » donne PLZ.
    $n = [regex]::Replace((Plat $nom).Replace('.', ' '), '\([^)]*\)', ' ')
    $parts = @($n -split '[\s,]+' | Where-Object { $_ })
    if ($parts.Count -lt 2) { return $null }
    if ($parts[$parts.Count - 1].Length -le 2) {
        $prenom  = $parts[$parts.Count - 1]
        $famille = -join $parts[0..($parts.Count - 2)]
    } else {
        $prenom  = $parts[0]
        $famille = -join $parts[1..($parts.Count - 1)]
    }
    if (-not $prenom -or $famille.Length -lt 2) { return $null }
    return ('' + $prenom[0] + $famille[0] + $famille[$famille.Length - 1]).ToUpper()
}

function LireXml([byte[]] $octets) {
    $s = $UTF8.GetString($octets).TrimStart([char]0xFEFF)
    $doc = New-Object System.Xml.XmlDocument
    $doc.LoadXml($s)
    return $doc
}

function Grille([string] $partie) {
    # { ligne = { colonne = texte } }
    $doc = LireXml $entrees[$partie]
    $ns = New-Object System.Xml.XmlNamespaceManager($doc.NameTable)
    $ns.AddNamespace('m', $NS_M)
    $out = @{}
    foreach ($c in $doc.SelectNodes('//m:c', $ns)) {
        $ref = $c.GetAttribute('r')
        $t   = $c.GetAttribute('t')
        $inl = $c.SelectSingleNode('m:is', $ns)
        $v   = $c.SelectSingleNode('m:v', $ns)
        if ($inl) {
            $val = ''
            foreach ($x in $inl.SelectNodes('.//m:t', $ns)) { $val += $x.InnerText }
        } elseif (-not $v) {
            continue
        } elseif ($t -eq 's') {
            $i = [int] $v.InnerText
            if ($i -lt 0 -or $i -ge $shared.Count) { continue }
            $val = $shared[$i]
        } else {
            $val = $v.InnerText
        }
        $val = ("$val").Trim()
        if (-not $val) { continue }
        $lig = [int] ([regex]::Match($ref, '(\d+)').Groups[1].Value)
        $col = ColNum ([regex]::Match($ref, '([A-Z]+)').Groups[1].Value)
        if (-not $out.ContainsKey($lig)) { $out[$lig] = @{} }
        $out[$lig][$col] = $val
    }
    return $out
}

function CellulesBrutes([byte[]] $octets) {
    # { ligne = { colonne = texte } }, lu au motif plutôt qu'au XML : charger
    # douze feuilles de plusieurs méga-octets dans un XmlDocument coûte des
    # minutes, et on ne cherche ici que du texte.
    $txt = $UTF8.GetString($octets)
    $out = @{}
    foreach ($m in $RX_CELLULE.Matches($txt)) {
        $attrs  = $m.Groups[1].Value
        $dedans = $m.Groups[3].Value
        if (-not $dedans) { continue }
        $ref = [regex]::Match($attrs, 'r="([A-Z]+)(\d+)"')
        if (-not $ref.Success) { continue }
        $t = [regex]::Match($attrs, 't="([^"]*)"')
        $v = [regex]::Match($dedans, '<v>([^<]*)</v>')
        if ($t.Success -and $t.Groups[1].Value -eq 's') {
            if (-not $v.Success) { continue }
            $i = [int] $v.Groups[1].Value
            if ($i -lt 0 -or $i -ge $shared.Count) { continue }
            $val = $shared[$i]
        } elseif ($t.Success -and $t.Groups[1].Value -eq 'inlineStr') {
            $val = ''
            foreach ($x in [regex]::Matches($dedans, '<t[^>]*>([^<]*)</t>')) { $val += $x.Groups[1].Value }
        } elseif ($v.Success) {
            $val = $v.Groups[1].Value
        } else {
            continue
        }
        $val = ("$val").Trim()
        if (-not $val) { continue }
        $lig = [int] $ref.Groups[2].Value
        $col = ColNum $ref.Groups[1].Value
        if (-not $out.ContainsKey($lig)) { $out[$lig] = @{} }
        $out[$lig][$col] = $val
    }
    return $out
}

function Formes([string] $nom) {
    # Toutes les façons d'écrire un nom complet. « Nom, Prénom » s'y trouve
    # aussi en « Nom Prénom », « Prénom Nom »… On génère les combinaisons
    # plutôt que de deviner.
    $bouts = @($nom -split '[,\s]+' | Where-Object { $_ })
    if ($bouts.Count -eq 0) { return @() }
    $inv = @($bouts[($bouts.Count - 1)..0])
    $out = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($sep in @(', ', ' ', '  ', ',', '')) {
        [void] $out.Add(($bouts -join $sep))
        [void] $out.Add(($inv   -join $sep))
    }
    return @($out | Where-Object { $_.Length -gt 3 })
}

function Borner([string] $motif, [string] $texte) {
    # « \b » exige un caractère de mot d'un côté. « Nom A. » finit par un
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
    $bouts = @($plat -split '\s+' | Where-Object { $_ } | ForEach-Object { [regex]::Escape($_) })
    if ($bouts.Count -eq 0) { return $null }
    return (Borner ($bouts -join '[\s,]*') $plat)
}

function MotifSeul([string] $mot) {
    # Un nom de famille ou un prénom SEUL dans sa cellule. On exige la
    # majuscule initiale, et on la protège de l'insensibilité à la casse :
    # « Petit » et « PETIT » sont des noms, « petit » est un mot français
    # qu'il ne faut pas remplacer au milieu d'un commentaire.
    $p = Plat $mot
    if ($p.Length -lt 3) { return $null }
    $suite = ''
    foreach ($c in $p.Substring(1).ToCharArray()) {
        if ([char]::IsLetter($c)) {
            $suite += '[' + ([string]$c).ToUpper() + ([string]$c).ToLower() + ']'
        } else {
            $suite += [regex]::Escape([string]$c)
        }
    }
    return (Borner ('(?-i:' + [regex]::Escape(([string]$p[0]).ToUpper()) + ')' + $suite) $p)
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
    foreach ($r in $regles) {
        if ($r.Sonde -and -not $presentes.Contains($r.Sonde)) { continue }
        foreach ($m in $r.Rx.Matches($plat)) {
            $coupes.Add([pscustomobject] @{ A = $m.Index; B = $m.Index + $m.Length; Par = $r.Par })
        }
    }
    if ($coupes.Count -eq 0) { return [pscustomobject] @{ Octets = $octets; N = 0 } }
    # à position égale, la plus longue d'abord
    $coupes = @($coupes | Sort-Object -Property A, @{ Expression = { $_.A - $_.B } })
    $sb = New-Object System.Text.StringBuilder
    $pos = 0
    $n = 0
    foreach ($c in $coupes) {
        if ($c.A -lt $pos) { continue }          # déjà couvert par une règle plus longue
        [void] $sb.Append($txt.Substring($pos, $c.A - $pos))
        [void] $sb.Append($c.Par)
        $pos = $c.B
        $n++
    }
    [void] $sb.Append($txt.Substring($pos))
    return [pscustomobject] @{ Octets = $UTF8.GetBytes($sb.ToString()); N = $n }
}


# --- le classeur, lu une fois pour toutes --------------------------------
$src = (Resolve-Path -LiteralPath $Source).ProviderPath
if ([IO.Path]::IsPathRooted($Sortie)) { $dst = $Sortie }
else { $dst = Join-Path (Get-Location).ProviderPath $Sortie }
$dst = [IO.Path]::GetFullPath($dst)

$entrees = New-Object System.Collections.Specialized.OrderedDictionary
$zin = [IO.Compression.ZipFile]::OpenRead($src)
try {
    foreach ($e in $zin.Entries) {
        $ms = New-Object IO.MemoryStream
        $st = $e.Open(); $st.CopyTo($ms); $st.Dispose()
        $entrees[$e.FullName] = $ms.ToArray()
        $ms.Dispose()
    }
} finally { $zin.Dispose() }

foreach ($requis in @('xl/workbook.xml', 'xl/_rels/workbook.xml.rels')) {
    if (-not $entrees.Contains($requis)) {
        throw "Ce fichier n'a pas la forme d'un classeur Excel : $requis est absent. " +
              "Est-ce bien le .xlsm, et non un raccourci ou un fichier OneDrive non téléchargé ?"
    }
}

# --- les feuilles, puis l'annuaire ---------------------------------------
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

$feuilles = @{}
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
        $v = ''
        foreach ($t in $si.SelectNodes('.//m:t', $nss)) { $v += $t.InnerText }
        $shared.Add($v)
    }
}

# La feuille « Personnel » donne la correspondance officielle nom → initiales.
$gPersonnel = $null
$annuaire = @{}
if ($feuilles.ContainsKey('Personnel')) {
    $gPersonnel = Grille $feuilles['Personnel']
    foreach ($ligne in $gPersonnel.Values) {
        $nom = ''; $ini = ''
        if ($ligne.ContainsKey(1)) { $nom = ([string] $ligne[1]).Trim() }
        if ($ligne.ContainsKey(2)) { $ini = ([string] $ligne[2]).Trim() }
        if ($nom -and $ini -and $nom -ne '0' -and $nom -ne 'Nom') {
            $annuaire[(Plat $nom).ToLower()] = $ini.ToUpper()
        }
    }
}
if ($annuaire.Count -eq 0) {
    throw "Aucun nom trouvé : la feuille « Personnel » a-t-elle bougé ?"
}

$noms = @{}
foreach ($k in $annuaire.Keys) { $noms[$k] = $annuaire[$k] }
$connus = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($v in $annuaire.Values) { [void] $connus.Add($v) }

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
    if ($connus.Contains((Plat $t).ToUpper())) { return $null }
    return $t
}

function IniConnues([string] $t) {
    # Le trigramme que ce texte donne, s'il en donne un de connu.
    #
    # L'ordre inversé — « Nom, Prénom » pour GBT — n'est essayé que si
    # le texte porte une VIRGULE. Sans cette condition, trois lettres se
    # rencontrent trop facilement : « terr arr » lu à l'envers donne ATR,
    # « pm ds-ce » donne PDE, et des noms d'ateliers devenaient des gens.
    $i = Initiales $t
    if ($i -and $connus.Contains($i)) { return $i }
    if ($t.Contains(',')) {
        $bouts = @($t -split '[,\s]+' | Where-Object { $_ })
        if ($bouts.Count -gt 1) {
            $inv = @($bouts[($bouts.Count - 1)..0])
            $i = Initiales ($inv -join ' ')
            if ($i -and $connus.Contains($i)) { return $i }
        }
    }
    return $null
}

# --- les alias : toutes les façons dont le classeur écrit les gens --------
# Le classeur en connaît bien plus que la feuille « Personnel » :
# « Nom A. », « P-Y. Nom », « Nom F.(ass.Us.) ». On les récolte
# partout — mais on ne les croit que si Initiales() y retrouve un trigramme
# connu. Un alias qui ne se recoupe pas n'est pas un nom, et « Step » ne
# devient pas quelqu'un.
$vus = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($nom in @($entrees.Keys)) {
    if (-not $TEXTE.IsMatch($nom)) { continue }
    foreach ($m in $RX_TEXTE.Matches($UTF8.GetString($entrees[$nom]))) {
        $brut = $m.Groups[1].Value
        if (-not $vus.Add($brut)) { continue }
        $t = Candidat $brut
        if (-not $t) { continue }
        # « Nom F.(ass.Us.) » : on n'enregistre que le nom, pour que la
        # parenthèse — qui dit le rôle, pas la personne — reste au classeur.
        $t = (([regex]::Replace($t, '\([^)]*\)', ' ')) -replace '\s+', ' ').Trim()
        if (-not $t) { continue }
        $cle = (Plat $t).ToLower()
        if ($noms.ContainsKey($cle)) { continue }
        $ini = IniConnues $t
        if ($ini) { $noms[$cle] = $ini }
    }
}

# Le nom et le prénom dans DEUX COLONNES — la feuille « Polyvalence » les
# range ainsi, « NOM » d'un côté, « PRÉNOM » de l'autre. Aucun des deux
# n'est un nom complet, donc aucun n'était remplacé.
#
# On ne devine pas quelles colonnes : on cherche le couple qui, sur TOUTE la
# feuille, redonne des trigrammes connus. Trois lettres se rencontrent par
# hasard — « Polyvalence Nom » donne PDE et faisait du nom de la feuille
# l'alias de quelqu'un. Un couple qui ne tombe juste qu'une fois est un
# hasard ; celui qui tombe juste cinquante fois est la structure.
foreach ($partie in @($feuilles.Values)) {
    if (-not $entrees.Contains($partie)) { continue }
    $grille = CellulesBrutes $entrees[$partie]
    $mots = @{}
    foreach ($l in $grille.Keys) {
        $m = @{}
        foreach ($c in $grille[$l].Keys) {
            $t = Candidat $grille[$l][$c]
            if ($t) { $m[$c] = $t }
        }
        if ($m.Count -gt 1) { $mots[$l] = $m }
    }
    $scores = @{}
    foreach ($m in $mots.Values) {
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
    foreach ($k in $scores.Keys) {
        if ($scores[$k] -lt 10) { continue }
        $ij = $k -split '/'
        $i = [int] $ij[0]
        $j = [int] $ij[1]
        $paires = @()
        foreach ($m in $mots.Values) {
            if ($m.ContainsKey($i) -and $m.ContainsKey($j)) { $paires += , $m }
        }
        # Dix coïncidences ne suffisent pas. « Abs » répété dans une colonne,
        # suivi d'un nom de famille, redonne des trigrammes connus des
        # dizaines de fois — et « Polyvalence » ou « Ferm. » devenaient
        # l'alias de quelqu'un. Une colonne de noms, elle, ne se répète pas :
        # c'est à ça qu'on la reconnaît.
        if ($paires.Count -lt 10) { continue }
        $di = New-Object 'System.Collections.Generic.HashSet[string]'
        $dj = New-Object 'System.Collections.Generic.HashSet[string]'
        foreach ($m in $paires) { [void] $di.Add($m[$i]); [void] $dj.Add($m[$j]) }
        if ([Math]::Min($di.Count, $dj.Count) * 2 -lt $paires.Count) { continue }
        # Le couple est établi : chaque ligne porte alors une personne, même
        # absente de l'annuaire — ses initiales tiennent lieu d'identifiant,
        # comme partout ailleurs.
        foreach ($m in $paires) {
            $ini = Initiales ($m[$i] + ' ' + $m[$j])
            if (-not $ini) { continue }
            foreach ($x in @($m[$i], $m[$j])) {
                $cle = (Plat $x).ToLower()
                if (-not $noms.ContainsKey($cle)) { $noms[$cle] = $ini }
            }
        }
    }
}

# --- les règles, et ce qu'on surveillera dans la sortie -------------------
$pesees    = New-Object 'System.Collections.Generic.List[object]'
$surveille = New-Object 'System.Collections.Generic.List[object]'
foreach ($cle in $noms.Keys) {
    $ini = $noms[$cle]
    $bouts = @($cle -split '[,\s]+' | Where-Object { $_ })
    if ($bouts.Count -gt 1) {
        foreach ($forme in (Formes $cle)) {
            $m = Motif $forme
            if ($m) {
                $sonde = (($forme -split '\s+')[0]) -replace '[^\p{L}]', ''
                $pesees.Add([pscustomobject] @{
                    Poids = $forme.Length; Motif = $m; Par = $ini; Sonde = $sonde })
            }
        }
    } else {
        $m = MotifSeul $cle
        if ($m) {
            $pesees.Add([pscustomobject] @{
                Poids = $cle.Length; Motif = $m; Par = $ini; Sonde = ($cle -replace '[^\p{L}]', '') })
        }
    }
    foreach ($b in $bouts) {
        if ($b.Length -ge 3) {
            $surveille.Add([pscustomobject] @{ Bout = $b; Ini = $ini })
        }
    }
}

# Les règles qui attrapent le plus long d'abord : « Nom A. » avant
# « Nom », sans quoi il resterait « ATR A. ». On pèse ce que la règle
# ATTRAPE et non la longueur du motif : « [Tt][Rr][Ee]… » est un long motif
# pour un petit mot, et il passerait devant.
$regles = @($pesees | Sort-Object -Property Poids -Descending | ForEach-Object {
    [pscustomobject] @{ Rx = [regex]::new($_.Motif, 'IgnoreCase'); Par = $_.Par; Sonde = $_.Sonde }
})
$regles += [pscustomobject] @{ Rx = [regex]::new($AUTEUR); Par = ''; Sonde = '' }
$sondes = @($regles | ForEach-Object { $_.Sonde } | Where-Object { $_ } | Sort-Object -Unique)

$tol = @()
if ($Tolerer) {
    $tol = @($Tolerer -split ',' | ForEach-Object { (Plat $_).Trim().ToLower() } | Where-Object { $_ })
}

# --- la recopie ----------------------------------------------------------
$depart = "{0} nom(s) connu(s) · {1} règle(s) · {2} sonde(s) · lecture en cours…"
Write-Host ($depart -f $noms.Count, $regles.Count, $sondes.Count)
if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Force }
$total = 0
$parties = 0
$zout = [IO.Compression.ZipFile]::Open($dst, [IO.Compression.ZipArchiveMode]::Create)
try {
    foreach ($nom in @($entrees.Keys)) {
        if ($EXCLUS.IsMatch($nom)) {
            Write-Host "  écarté : $nom"
            continue
        }
        $donnee = $entrees[$nom]
        if ($TEXTE.IsMatch($nom)) {
            $res = Remplacer $donnee
            $donnee = $res.Octets
            if ($nom.StartsWith('docProps/')) {
                $s = $UTF8.GetString($donnee)
                $s = [regex]::Replace($s, '<(dc:creator|cp:lastModifiedBy)>[^<]*</\1>', '<$1></$1>')
                $donnee = $UTF8.GetBytes($s)
            }
            $total += $res.N
            if ($res.N) { $parties++ }
        }
        $e  = $zout.CreateEntry($nom, [IO.Compression.CompressionLevel]::Optimal)
        $st = $e.Open(); $st.Write($donnee, 0, $donnee.Length); $st.Dispose()
    }
} finally { $zout.Dispose() }

# --- la garantie : relire, et chercher ce qu'on vient de remplacer --------
$restes = New-Object 'System.Collections.Generic.List[object]'
$zv = [IO.Compression.ZipFile]::OpenRead($dst)
try {
    foreach ($e in $zv.Entries) {
        if (-not $TEXTE.IsMatch($e.FullName)) { continue }
        $ms = New-Object IO.MemoryStream
        $st = $e.Open(); $st.CopyTo($ms); $st.Dispose()
        $plat = Plat ($UTF8.GetString($ms.ToArray()))
        $ms.Dispose()
        foreach ($w in $surveille) {
            if ($tol -contains $w.Bout) { continue }
            if ($plat.IndexOf($w.Bout, [StringComparison]::OrdinalIgnoreCase) -lt 0) { continue }
            foreach ($m in [regex]::Matches($plat, '\b' + [regex]::Escape($w.Bout) + '\b', 'IgnoreCase')) {
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
    Remove-Item -LiteralPath $dst -Force
    Write-Host ''
    Write-Host ("{0} reste(s) de nom dans la sortie — fichier détruit :" -f $restes.Count) -ForegroundColor Red
    foreach ($r in ($restes | Select-Object -First 20)) {
        Write-Host ("   {0,-22} {1,-14} ({2})  …{3}…" -f $r.Fichier, $r.Mot, $r.Ini, $r.Ctx)
    }
    Write-Host ''
    Write-Host "Si l'un d'eux n'est pas un nom — « Paye » peut être un mot — relancer avec"
    Write-Host "  -Tolerer mot1,mot2   APRÈS l'avoir lu."
    if ($journal) { try { Stop-Transcript | Out-Null } catch { } }
    exit 2
}

$taille = (Get-Item -LiteralPath $dst).Length
$resume = "{0} nom(s) connu(s) · {1} remplacement(s) dans {2} partie(s) · {3:N1} Mo"
Write-Host ($resume -f $noms.Count, $total, $parties, ($taille / 1MB))
Write-Host 'Aucun nom ne subsiste : vérifié sur la sortie.' -ForegroundColor Green
if ($journal) { try { Stop-Transcript | Out-Null } catch { } }
