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
      - les noms complets, sous toutes leurs formes, remplacés par le trigramme ;
      - les auteurs de commentaires, préfixés à leur texte ;
      - les macros (vbaProject.bin) : d'où un .xlsx, pas un .xlsm ;
      - les propriétés du document : auteur, dernier enregistreur.

    GARANTIE. Après écriture, la sortie est relue entièrement et l'outil y
    CHERCHE les noms qu'il vient de remplacer. S'il en trouve un seul, il
    détruit sa sortie et s'arrête avec le détail. Un anonymiseur qui peut
    laisser passer un nom sans le dire ne vaut rien.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)] [string] $Source,
    [Parameter(Mandatory = $true, Position = 1)] [string] $Sortie,
    [string] $Tolerer = ''
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$UTF8   = New-Object System.Text.UTF8Encoding($false)
$NS_M   = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
$NS_R   = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
$NS_P   = 'http://schemas.openxmlformats.org/package/2006/relationships'

# Ce qui, dans le ZIP, ne doit pas être recopié.
$EXCLUS = [regex]::new('(vbaProject\.bin|/vbaProject|\.bin$)', 'IgnoreCase')
# Les parties où chercher du texte. Tout le reste est recopié tel quel.
$TEXTE  = [regex]::new('\.(xml|rels|vml)$', 'IgnoreCase')
# « Nom, Prénom: », « Nom, Prénom (external): », « RT01386: »
$AUTEUR = "(?:^|\s)(?:[A-ZÉÈÀ][\wÉÈÀéèàêç'-]+,\s*[A-ZÉÈÀ][\wÉÈÀéèàêç'-]+(?:\s*\([^)]*\))?|[Rr][Tt]\d{4,6}|Auteur)\s*:\s*"


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

function Formes([string] $nom) {
    # Toutes les façons d'écrire un nom dans le classeur. « Nom, Prénom »
    # s'y trouve aussi en « Nom Prénom », « Prénom Nom »… On génère les
    # combinaisons plutôt que de deviner.
    $bouts = @($nom -split '[,\s]+' | Where-Object { $_ })
    if ($bouts.Count -eq 0) { return @() }
    $inv = @($bouts[($bouts.Count - 1)..0])
    $out = New-Object System.Collections.Generic.HashSet[string]
    foreach ($sep in @(', ', ' ', '  ', ',', '')) {
        [void] $out.Add(($bouts -join $sep))
        [void] $out.Add(($inv   -join $sep))
    }
    return @($out | Where-Object { $_.Length -gt 3 })
}

function Motif([string] $texte) {
    # Un motif qui retrouve le texte quels que soient les accents, la casse et
    # les espaces — le classeur n'est pas régulier là-dessus.
    $bouts = @((Plat $texte).Trim() -split '\s+' |
               Where-Object { $_ } | ForEach-Object { [regex]::Escape($_) })
    if ($bouts.Count -eq 0) { return $null }
    return '\b' + ($bouts -join '[\s,]*') + '\b'
}

function Remplacer([byte[]] $octets) {
    $txt  = $UTF8.GetString($octets)
    $plat = Plat $txt
    # Si la copie sans accents n'a pas la même longueur, les positions ne
    # correspondent plus : on cherche alors dans l'original, quitte à manquer
    # une graphie. Jamais de remplacement posé au mauvais endroit.
    if ($plat.Length -ne $txt.Length) { $plat = $txt }
    $coupes = New-Object System.Collections.Generic.List[object]
    foreach ($r in $regles) {
        if ($r.Sonde -and $plat.IndexOf($r.Sonde, [StringComparison]::OrdinalIgnoreCase) -lt 0) { continue }
        foreach ($m in $r.Rx.Matches($plat)) {
            $coupes.Add([pscustomobject] @{ A = $m.Index; B = $m.Index + $m.Length; Par = $r.Par })
        }
    }
    if ($coupes.Count -eq 0) { return [pscustomobject] @{ Octets = $octets; N = 0 } }
    # les plus longues d'abord à position égale : « Nom Prénom » avant « Nom »
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

$shared = New-Object System.Collections.Generic.List[string]
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
$annuaire = @{}
if ($feuilles.ContainsKey('Personnel')) {
    foreach ($ligne in (Grille $feuilles['Personnel']).Values) {
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

# --- les règles, et ce qu'on surveillera dans la sortie -------------------
$regles    = New-Object System.Collections.Generic.List[object]
$surveille = New-Object System.Collections.Generic.List[object]
foreach ($cle in $annuaire.Keys) {
    $ini = $annuaire[$cle]
    foreach ($forme in (Formes $cle)) {
        $m = Motif $forme
        if ($m) {
            $sonde = (($forme -split '\s+')[0]) -replace '[^\p{L}]', ''
            $regles.Add([pscustomobject] @{
                Rx = [regex]::new($m, 'IgnoreCase'); Par = $ini; Sonde = $sonde; Long = $m.Length })
        }
    }
    foreach ($bout in ($cle -split '[,\s]+')) {
        if ($bout.Length -ge 3) {
            $surveille.Add([pscustomobject] @{ Bout = $bout; Ini = $ini })
        }
    }
}
$regles = @($regles | Sort-Object -Property Long -Descending)
$regles += [pscustomobject] @{ Rx = [regex]::new($AUTEUR); Par = ''; Sonde = ''; Long = 0 }

$tol = @()
if ($Tolerer) {
    $tol = @($Tolerer -split ',' | ForEach-Object { (Plat $_).Trim().ToLower() } | Where-Object { $_ })
}

# --- la recopie ----------------------------------------------------------
Write-Host ("{0} nom(s) connu(s) · {1} règle(s) · lecture en cours…" -f $annuaire.Count, $regles.Count)
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
$restes = New-Object System.Collections.Generic.List[object]
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
                    Fichier = $e.FullName; Ini = $w.Ini
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
        Write-Host ("   {0,-28} ({1})  …{2}…" -f $r.Fichier, $r.Ini, $r.Ctx)
    }
    Write-Host ''
    Write-Host "Si l'un d'eux n'est pas un nom — « Paye » peut être un mot — relancer avec"
    Write-Host "  -Tolerer mot1,mot2   APRÈS l'avoir lu."
    exit 2
}

$taille = (Get-Item -LiteralPath $dst).Length
$resume = "{0} nom(s) connu(s) · {1} remplacement(s) dans {2} partie(s) · {3:N1} Mo"
Write-Host ($resume -f $annuaire.Count, $total, $parties, ($taille / 1MB))
Write-Host 'Aucun nom ne subsiste : vérifié sur la sortie.' -ForegroundColor Green
