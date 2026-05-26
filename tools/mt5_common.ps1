param()

function Get-RepoRoot {
    return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
}

function Import-Mt5LocalConfig {
    $repoRoot = Get-RepoRoot
    $localConfig = Join-Path $repoRoot "config\mt5.local.ps1"

    if (Test-Path -LiteralPath $localConfig) {
        . $localConfig
        return @{
            InstallDir = $Mt5InstallDir
            DataDir    = $Mt5DataDir
        }
    }

    return $null
}

function Find-Mt5ByOrigin {
    param(
        [string] $PreferredOrigin = ""
    )

    $terminalRoot = Join-Path $env:APPDATA "MetaQuotes\Terminal"
    if (!(Test-Path -LiteralPath $terminalRoot)) {
        return $null
    }

    $matches = Get-ChildItem -LiteralPath $terminalRoot -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        $originFile = Join-Path $_.FullName "origin.txt"
        if (Test-Path -LiteralPath $originFile) {
            $origin = (Get-Content -LiteralPath $originFile -Raw).Trim()
            [PSCustomObject]@{
                InstallDir = $origin
                DataDir    = $_.FullName
            }
        }
    }

    $preferred = $null
    if ($PreferredOrigin -ne "") {
        $preferred = $matches | Where-Object { $_.InstallDir -eq $PreferredOrigin } | Select-Object -First 1
    }

    if ($preferred) {
        return @{
            InstallDir = $preferred.InstallDir
            DataDir    = $preferred.DataDir
        }
    }

    $firstUsable = $matches | Where-Object {
        (Test-Path -LiteralPath (Join-Path $_.InstallDir "terminal64.exe")) -and
        (Test-Path -LiteralPath (Join-Path $_.InstallDir "MetaEditor64.exe"))
    } | Select-Object -First 1
    if ($firstUsable) {
        return @{
            InstallDir = $firstUsable.InstallDir
            DataDir    = $firstUsable.DataDir
        }
    }

    return $null
}

function Resolve-Mt5Paths {
    $config = Import-Mt5LocalConfig
    if ($null -eq $config) {
        $config = Find-Mt5ByOrigin
    }

    if ($null -eq $config) {
        throw "Nao encontrei MT5. Crie config\mt5.local.ps1 baseado em config\mt5.local.example.ps1."
    }

    $installDir = $config.InstallDir
    $dataDir = $config.DataDir
    $terminal = Join-Path $installDir "terminal64.exe"
    $metaEditor = Join-Path $installDir "MetaEditor64.exe"

    if (!(Test-Path -LiteralPath $terminal)) {
        throw "terminal64.exe nao encontrado em: $terminal"
    }

    if (!(Test-Path -LiteralPath $metaEditor)) {
        throw "MetaEditor64.exe nao encontrado em: $metaEditor"
    }

    if (!(Test-Path -LiteralPath $dataDir)) {
        throw "Pasta de dados do MT5 nao encontrada: $dataDir"
    }

    return @{
        InstallDir  = $installDir
        DataDir     = $dataDir
        Terminal    = $terminal
        MetaEditor  = $metaEditor
    }
}

function Get-EaSourcePath {
    $repoRoot = Get-RepoRoot
    return Join-Path $repoRoot "MQL5\Experts\RBRiskEngine\RBRiskEngine_Public.mq5"
}

function Get-EaTargetPath {
    param([string] $DataDir)

    return Join-Path $DataDir "MQL5\Experts\RBRiskEngine\RBRiskEngine_Public.mq5"
}
