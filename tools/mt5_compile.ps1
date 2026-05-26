param(
    [switch] $OpenEditor
)

. (Join-Path $PSScriptRoot "mt5_common.ps1")

$paths = Resolve-Mt5Paths
$source = Get-EaSourcePath
$target = Get-EaTargetPath -DataDir $paths.DataDir
$targetDir = Split-Path -Parent $target
$repoRoot = Get-RepoRoot
$logDir = Join-Path $repoRoot "runs\compile"
$logPath = Join-Path $logDir "RBRiskEngine_Public.compile.log"

if (!(Test-Path -LiteralPath $source)) {
    throw "EA fonte nao encontrado: $source"
}

New-Item -ItemType Directory -Force -Path $targetDir, $logDir | Out-Null
Copy-Item -LiteralPath $source -Destination $target -Force

$args = "/compile:`"$target`" /log:`"$logPath`""

if (!$OpenEditor) {
    $args = "$args /quiet"
}

Write-Host "MetaEditor: $($paths.MetaEditor)"
Write-Host "EA copiado para: $target"
Write-Host "Log: $logPath"

$process = Start-Process -FilePath $paths.MetaEditor -ArgumentList $args -Wait -PassThru -WindowStyle Hidden

if (Test-Path -LiteralPath $logPath) {
    Get-Content -LiteralPath $logPath | Select-Object -Last 80
}

$compiled = [System.IO.Path]::ChangeExtension($target, ".ex5")
if (!(Test-Path -LiteralPath $compiled)) {
    throw "Compilacao nao gerou EX5 esperado: $compiled"
}

$logText = ""
if (Test-Path -LiteralPath $logPath) {
    $logText = Get-Content -LiteralPath $logPath -Raw
}

if ($process.ExitCode -ne 0 -and $logText -notmatch "Result:\s+0 errors") {
    throw "MetaEditor retornou codigo $($process.ExitCode). Veja o log em $logPath"
}

Write-Host "Compilado: $compiled"
