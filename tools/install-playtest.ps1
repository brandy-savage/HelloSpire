<#
.SYNOPSIS
    Installs (or updates) the latest HelloSpire playtest build into Slay the Spire 2.

.DESCRIPTION
    For playtesters. One line in PowerShell:

        irm https://raw.githubusercontent.com/r0zar/HelloSpire/main/tools/install-playtest.ps1 | iex

    It finds the game through Steam, downloads the newest HelloSpire release from GitHub,
    replaces mods\HelloSpire with it, and installs the exact BaseLib version that build
    was made against -- unless BaseLib already comes from a Steam Workshop subscription.

    Re-running it is how you update. Nothing outside the game's mods\ folder is touched.

.PARAMETER Version
    A specific release tag (e.g. v0.1.0) instead of the latest. Every player in a co-op
    lobby must be on the same one.

.PARAMETER GameDir
    The Slay the Spire 2 install folder, if auto-detection fails.
#>
[CmdletBinding()]
param(
    [string]$Version,
    [string]$GameDir
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'   # Invoke-WebRequest's progress bar is very slow on PS 5
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Repo = 'r0zar/HelloSpire'
$BaseLibRepo = 'Alchyr/BaseLib-StS2'
$AppId = '2868840'
$BaseLibWorkshopId = '3737335127'

function Say($msg)  { Write-Host "==> $msg" -ForegroundColor Cyan }
function Good($msg) { Write-Host "    $msg" -ForegroundColor Green }
function Fail($msg) { Write-Host "    $msg" -ForegroundColor Red; exit 1 }

# ---------------------------------------------------------------------------
# Find the game: the uninstall registry key, then every Steam library folder.
# ---------------------------------------------------------------------------
function Get-SteamLibraries {
    $steam = (Get-ItemProperty 'HKCU:\Software\Valve\Steam' -ErrorAction SilentlyContinue).SteamPath
    if (-not $steam) { $steam = 'C:\Program Files (x86)\Steam' }
    $libs = @((Join-Path $steam 'steamapps'))
    $vdf = Join-Path $steam 'steamapps\libraryfolders.vdf'
    if (Test-Path $vdf) {
        foreach ($m in [regex]::Matches((Get-Content $vdf -Raw), '"path"\s+"([^"]+)"')) {
            $libs += (Join-Path ($m.Groups[1].Value -replace '\\\\', '\') 'steamapps')
        }
    }
    $libs | Select-Object -Unique
}

if (-not $GameDir) {
    $key = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App $AppId"
    $GameDir = (Get-ItemProperty $key -ErrorAction SilentlyContinue).InstallLocation
}
$Libraries = Get-SteamLibraries
if (-not $GameDir -or -not (Test-Path $GameDir)) {
    $GameDir = $Libraries | ForEach-Object { Join-Path $_ 'common\Slay the Spire 2' } |
        Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $GameDir) {
    Fail "Couldn't find Slay the Spire 2. Re-run with -GameDir 'D:\path\to\Slay the Spire 2'."
}
Say "Slay the Spire 2: $GameDir"
$ModsDir = Join-Path $GameDir 'mods'

if (Get-Process -Name 'SlayTheSpire2' -ErrorAction SilentlyContinue) {
    Fail "Close Slay the Spire 2 first -- it locks the mod files while running."
}

# ---------------------------------------------------------------------------
# Download the HelloSpire release.
# ---------------------------------------------------------------------------
$api = if ($Version) { "https://api.github.com/repos/$Repo/releases/tags/$Version" }
       else          { "https://api.github.com/repos/$Repo/releases/latest" }
try { $release = Invoke-RestMethod $api -Headers @{ 'User-Agent' = 'HelloSpire-installer' } }
catch { Fail "No release found at $api. Has a build been published yet?" }

$asset = $release.assets | Where-Object { $_.name -like 'HelloSpire-*.zip' } | Select-Object -First 1
if (-not $asset) { Fail "Release $($release.tag_name) has no HelloSpire-*.zip attached." }
Say "Downloading HelloSpire $($release.tag_name)"

$tmp = Join-Path ([IO.Path]::GetTempPath()) ("hellospire-" + [guid]::NewGuid())
New-Item -ItemType Directory $tmp | Out-Null
try {
    $zip = Join-Path $tmp $asset.name
    Invoke-WebRequest $asset.browser_download_url -OutFile $zip -UseBasicParsing
    Expand-Archive $zip -DestinationPath (Join-Path $tmp 'x')
    $staged = Join-Path $tmp 'x\HelloSpire'
    if (-not (Test-Path (Join-Path $staged 'HelloSpire.json'))) { Fail "The zip isn't laid out as HelloSpire\... -- report this." }

    New-Item -ItemType Directory $ModsDir -Force | Out-Null
    $target = Join-Path $ModsDir 'HelloSpire'
    if (Test-Path $target) { Remove-Item $target -Recurse -Force }   # stale files from an older build must not linger
    Move-Item $staged $target
    Good "Installed to $target"

    # -----------------------------------------------------------------------
    # BaseLib: the version this build declares, unless Workshop already provides it.
    # -----------------------------------------------------------------------
    $manifest = Get-Content (Join-Path $target 'HelloSpire.json') -Raw | ConvertFrom-Json
    $need = ($manifest.dependencies | Where-Object { $_.id -eq 'BaseLib' }).min_version
    $fromWorkshop = $Libraries | ForEach-Object { Join-Path $_ "workshop\content\$AppId\$BaseLibWorkshopId" } |
        Where-Object { Test-Path $_ } | Select-Object -First 1
    $baseDir = Join-Path $ModsDir 'BaseLib'
    $have = $null
    if (Test-Path (Join-Path $baseDir 'BaseLib.json')) {
        $have = ((Get-Content (Join-Path $baseDir 'BaseLib.json') -Raw) | ConvertFrom-Json).version -replace '^v', ''
    }

    if ($fromWorkshop) {
        Good "BaseLib comes from your Steam Workshop subscription; leaving it alone."
        if (Test-Path $baseDir) {
            Write-Host "    Note: mods\BaseLib also exists. Two copies can conflict -- delete one." -ForegroundColor Yellow
        }
    }
    elseif ($have -eq $need) {
        Good "BaseLib $have already installed."
    }
    else {
        Say "Installing BaseLib $need"
        $bl = Invoke-RestMethod "https://api.github.com/repos/$BaseLibRepo/releases/tags/v$need" -Headers @{ 'User-Agent' = 'HelloSpire-installer' }
        $blAsset = $bl.assets | Where-Object { $_.name -like 'BaseLib*.zip' } | Select-Object -First 1
        $blZip = Join-Path $tmp $blAsset.name
        Invoke-WebRequest $blAsset.browser_download_url -OutFile $blZip -UseBasicParsing
        if (Test-Path $baseDir) { Remove-Item $baseDir -Recurse -Force }
        Expand-Archive $blZip -DestinationPath $baseDir    # BaseLib's zip is flat: dll, json, pck
        Good "Installed to $baseDir"
    }
}
finally {
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Say "Done: HelloSpire $($release.tag_name)."
Write-Host "    Launch the game, choose 'Play with Mods', and enable HelloSpire and BaseLib in the Mods menu."
Write-Host "    Co-op: everyone must run this same version ($($release.tag_name))."
