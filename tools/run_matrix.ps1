param(
    [string] $MatrixPath = "config\\matrix\\rb_ouro_v4_7_qa_matrix.csv",
    [string] $Symbol = "XAUUSD",
    [string] $Period = "M1",
    [double] $Deposit = 1000,
    [string] $Leverage = "1:500",
    [int] $TimeoutSeconds = 900,
    [switch] $PrepareV47,
    [switch] $CompileFirst,
    [string] $Login = "",
    [string] $Password = "",
    [string] $Server = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$matrixFullPath = Join-Path $repoRoot $MatrixPath

if (!(Test-Path -LiteralPath $matrixFullPath)) {
    throw "Matriz nao encontrada: $matrixFullPath"
}

if ($PrepareV47) {
    Write-Host "Gerando RB_Ouro_v4_7_QA.mq5 a partir da v4.6 atual..."
    python (Join-Path $repoRoot "tools\\prepare_rb_ouro_v4_7_qa.py")
}

$rows = Import-Csv -LiteralPath $matrixFullPath
if (!$rows -or $rows.Count -eq 0) {
    throw "Matriz vazia: $matrixFullPath"
}

$backtestScript = Join-Path $repoRoot "tools\\mt5_backtest.ps1"

foreach ($row in $rows) {
    $enabled = "$($row.enabled)".Trim().ToLowerInvariant()
    if ($enabled -in @("0", "false", "no", "nao", "não")) {
        continue
    }

    $label = "$($row.label)".Trim()
    if ($label -eq "") {
        $label = "matrix-run"
    }

    $sourcePath = "$($row.source_path)".Trim()
    $expertPath = "$($row.expert_path)".Trim()
    $setPath = "$($row.set_path)".Trim()
    $fromDate = "$($row.from_date)".Trim()
    $toDate = "$($row.to_date)".Trim()
    $expertParameters = "$($row.expert_parameters)".Trim()

    if ($expertPath -eq "") { throw "Linha $label sem expert_path" }
    if ($fromDate -eq "") { throw "Linha $label sem from_date" }
    if ($toDate -eq "") { throw "Linha $label sem to_date" }

    $args = @(
        "-ExecutionPolicy", "Bypass",
        "-File", $backtestScript,
        "-Symbol", $Symbol,
        "-Period", $Period,
        "-FromDate", $fromDate,
        "-ToDate", $toDate,
        "-Deposit", $Deposit,
        "-Leverage", $Leverage,
        "-TimeoutSeconds", $TimeoutSeconds,
        "-ExpertPath", $expertPath,
        "-RunLabel", $label
    )

    if ($CompileFirst) { $args += "-CompileFirst" }
    if ($sourcePath -ne "") { $args += @("-SourcePath", (Join-Path $repoRoot $sourcePath)) }
    if ($setPath -ne "") { $args += @("-SetPath", (Join-Path $repoRoot $setPath)) }
    if ($expertParameters -ne "") { $args += @("-ExpertParameters", $expertParameters) }
    if ($Login -ne "") { $args += @("-Login", $Login) }
    if ($Password -ne "") { $args += @("-Password", $Password) }
    if ($Server -ne "") { $args += @("-Server", $Server) }

    Write-Host "============================================================"
    Write-Host "Rodando matriz: $label | $fromDate -> $toDate | $expertPath"
    Write-Host "============================================================"

    powershell @args
}

Write-Host "Matriz finalizada. Use: python tools\\summarize_runs.py --runs runs --output docs\\leaderboard_rb_ouro.md"
