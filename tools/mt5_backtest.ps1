param(
    [string] $Symbol = "XAUUSD",
    [string] $Period = "M1",
    [string] $FromDate = "2026.02.18",
    [string] $ToDate = "2026.02.20",
    [double] $Deposit = 1000,
    [string] $Leverage = "1:500",
    [int] $TimeoutSeconds = 180,
    [string] $Login = "",
    [string] $Password = "",
    [string] $Server = "",
    [switch] $CompileFirst
)

. (Join-Path $PSScriptRoot "mt5_common.ps1")

$repoRoot = Get-RepoRoot
$paths = Resolve-Mt5Paths

if ($CompileFirst) {
    & (Join-Path $PSScriptRoot "mt5_compile.ps1")
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$runDir = Join-Path $repoRoot "runs\$stamp"
$mt5RunRoot = Join-Path $paths.DataDir "MQL5\Files\RoboScalperRuns"
$mt5RunDir = Join-Path $mt5RunRoot $stamp
$configPath = Join-Path $mt5RunDir "tester.ini"
$reportBase = Join-Path $mt5RunDir "RoboScalper"
$sourceSetPath = Join-Path $repoRoot "config\RoboScalper.set"
$profileSetDir = Join-Path $paths.DataDir "MQL5\Profiles\Tester"
$profileSetPath = Join-Path $profileSetDir "RoboScalper.set"

New-Item -ItemType Directory -Force -Path $runDir, $mt5RunDir, $profileSetDir | Out-Null

if (Test-Path -LiteralPath $sourceSetPath) {
    Copy-Item -LiteralPath $sourceSetPath -Destination $profileSetPath -Force
    Copy-Item -LiteralPath $sourceSetPath -Destination (Join-Path $runDir "RoboScalper.set") -Force
}

$commonConfig = ""
if ($Login -ne "" -or $Password -ne "" -or $Server -ne "") {
    $commonConfig = @"
[Common]
Login=$Login
Password=$Password
Server=$Server

"@
}

$testerConfig = $commonConfig + @"
[Tester]
Expert=RoboScalper\RoboScalper
ExpertParameters=RoboScalper.set
Symbol=$Symbol
Period=$Period
Optimization=0
Model=0
FromDate=$FromDate
ToDate=$ToDate
ForwardMode=0
Deposit=$Deposit
Currency=USD
Leverage=$Leverage
ExecutionMode=0
Visual=0
Report=$reportBase
ReplaceReport=1
ShutdownTerminal=1
"@

Set-Content -LiteralPath $configPath -Value $testerConfig -Encoding ASCII

Write-Host "Terminal: $($paths.Terminal)"
Write-Host "Config: $configPath"
Write-Host "Relatorio base: $reportBase"

$launchTime = Get-Date
$argList = "/config:`"$configPath`" /skipupdate"
$process = Start-Process -FilePath $paths.Terminal -ArgumentList $argList -PassThru -WindowStyle Hidden

if (!$process.WaitForExit($TimeoutSeconds * 1000)) {
    Stop-Process -Id $process.Id -Force
    Copy-Item -LiteralPath $configPath -Destination (Join-Path $runDir "tester.ini") -Force
    throw "Backtest excedeu $TimeoutSeconds segundos. Verifique login/sincronizacao do MT5 e historico do simbolo."
}

Write-Host "Terminal finalizou com codigo: $($process.ExitCode)"

$watch = [System.Diagnostics.Stopwatch]::StartNew()
while ($watch.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
    $spawned = Get-Process terminal64 -ErrorAction SilentlyContinue | Where-Object {
        $_.StartTime -ge $launchTime.AddSeconds(-2)
    }

    if (!$spawned) {
        break
    }

    Start-Sleep -Seconds 1
}

$stillRunning = Get-Process terminal64 -ErrorAction SilentlyContinue | Where-Object {
    $_.StartTime -ge $launchTime.AddSeconds(-2)
}

if ($stillRunning) {
    $stillRunning | Stop-Process -Force
    Copy-Item -LiteralPath $configPath -Destination (Join-Path $runDir "tester.ini") -Force
    throw "MT5 continuou aberto apos o comando de teste. Processo encerrado para evitar ficar pendurado."
}

Copy-Item -LiteralPath $configPath -Destination (Join-Path $runDir "tester.ini") -Force
Get-ChildItem -LiteralPath $mt5RunDir -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne "tester.ini" } | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $runDir $_.Name) -Force
}

$dateStamp = Get-Date -Format "yyyyMMdd"
$terminalLog = Join-Path $paths.DataDir "Logs\$dateStamp.log"
$testerLog = Join-Path $paths.DataDir "Tester\logs\$dateStamp.log"

if (Test-Path -LiteralPath $terminalLog) {
    Copy-Item -LiteralPath $terminalLog -Destination (Join-Path $runDir "terminal.log") -Force
}

if (Test-Path -LiteralPath $testerLog) {
    Copy-Item -LiteralPath $testerLog -Destination (Join-Path $runDir "tester.log") -Force
}

$agentRoot = Join-Path $env:APPDATA "MetaQuotes\Tester"
$agentLogs = Get-ChildItem -LiteralPath $agentRoot -Filter "$dateStamp.log" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -ge $launchTime.AddMinutes(-1) } |
    Sort-Object LastWriteTime -Descending

$agentIndex = 1
foreach ($agentLog in $agentLogs) {
    Copy-Item -LiteralPath $agentLog.FullName -Destination (Join-Path $runDir "agent-$agentIndex.log") -Force
    $agentIndex++
}

$summaryPath = Join-Path $runDir "summary.txt"
$summaryLines = @()
foreach ($logName in @("tester.log", "agent-1.log")) {
    $candidate = Join-Path $runDir $logName
    if (Test-Path -LiteralPath $candidate) {
        $candidateLines = @(Get-Content -LiteralPath $candidate)
        $lastRunStart = 0
        for ($i = 0; $i -lt $candidateLines.Count; $i++) {
            if ($candidateLines[$i] -match "started with inputs") {
                $lastRunStart = $i
            }
        }
        $currentRunLines = $candidateLines[$lastRunStart..($candidateLines.Count - 1)]

        $summaryLines += "[$logName]"
        $summaryLines += $currentRunLines | Where-Object {
            $_ -match "testing of" -or
            $_ -match "final balance" -or
            $_ -match "Test passed" -or
            $_ -match "automatical testing finished" -or
            $_ -match "error" -or
            $_ -match "failed"
        }
        $summaryLines += ""
    }
}

if ($summaryLines.Count -gt 0) {
    Set-Content -LiteralPath $summaryPath -Value $summaryLines -Encoding UTF8
}

Write-Host "Arquivos da rodada:"
Get-ChildItem -LiteralPath $runDir -Force | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize
