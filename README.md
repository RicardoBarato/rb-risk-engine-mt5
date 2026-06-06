# MT5 EA Auto Backtest Engine

![MQL5](https://img.shields.io/badge/MQL5-Expert%20Advisor-blue)
![MetaTrader 5](https://img.shields.io/badge/MetaTrader%205-supported-informational)
![Educational](https://img.shields.io/badge/status-educational-lightgrey)
![Risk Management](https://img.shields.io/badge/focus-risk%20management-success)

Public educational MetaTrader 5 / MQL5 framework combining an Expert Advisor scaffold with automated Strategy Tester loops, report collection and publication hygiene.

This public repository is a sanitized educational release. It is not a profit promise, trading recommendation, signal service, investment product, or production trading system.

## Status

Public educational release: `v1.0-public`.

This project is the public backtesting and MT5 automation foundation that preceded later XAUUSD-specific research. The public version keeps the EA scaffold, automation structure, risk controls, documentation and safe publication boundary while excluding proprietary strategy logic, real presets, raw reports and production parameters.

## Why this project matters

This project is not about promising returns. It demonstrates how a trading automation idea can be translated into a controlled engineering workflow:

- define objective rules;
- compile and execute MT5 Expert Advisor tests repeatedly;
- collect test artifacts in a structured run folder;
- protect capital with explicit risk controls;
- document assumptions and limitations;
- separate public educational code from non-public research artifacts;
- avoid publishing sensitive broker, account or strategy artifacts.

## Portfolio Value

This repository demonstrates practical experience with MQL5 development, Expert Advisor structure, automated Strategy Tester workflows, risk management, Python report parsing, PowerShell automation, repository organization, documentation and security hygiene.

It also shows an important engineering decision: the public repository exposes a safe backtesting framework, not proprietary edge logic, real parameters, broker exports or optimization history.

## Skills demonstrated

- MQL5 / MetaTrader 5 development;
- Expert Advisor architecture;
- automated Strategy Tester workflows;
- repeatable backtest execution;
- risk management;
- report parsing and analysis;
- PowerShell automation;
- Python tooling;
- code organization;
- documentation;
- security hygiene;
- public/private research boundary management.

## Technologies

- MetaTrader 5;
- MQL5;
- PowerShell automation;
- Python report parsing;
- Strategy Tester workflow;
- Git and GitHub.

## Repository structure

```text
.
|-- MQL5/
|   `-- Experts/
|       `-- RBRiskEngine/
|           `-- RBRiskEngine_Public.mq5
|-- config/
|   `-- mt5.local.example.ps1
|-- docs/
|   |-- ARCHITECTURE.md
|   |-- PROJECT_HISTORY.md
|   |-- PUBLICATION_BOUNDARY.md
|   |-- PUBLIC_RELEASE_NOTES.md
|   |-- ROADMAP.md
|   `-- SAFETY_AND_RISK_NOTICE.md
|-- examples/
|   |-- README.md
|   |-- RBRiskEngine_Public.example.set
|   `-- example-parameters.md
|-- tools/
|   |-- mt5_backtest.ps1
|   |-- mt5_compile.ps1
|   |-- mt5_common.ps1
|   |-- mt5_parse_run.ps1
|   |-- mt5_robustness.py
|   `-- analyze_mt5_reports.py
|-- CHANGELOG.md
|-- SECURITY.md
|-- SECURITY_AUDIT_REPORT.md
`-- README.md
```

## Install

1. Install MetaTrader 5.
2. Clone this repository.
3. Copy the local MT5 configuration example:

```powershell
Copy-Item config\mt5.local.example.ps1 config\mt5.local.ps1
```

4. Edit `config\mt5.local.ps1` with your local MT5 install path and data directory.

The local file is ignored by Git.

## Compile

```powershell
powershell -ExecutionPolicy Bypass -File tools\mt5_compile.ps1
```

The script copies `MQL5\Experts\RBRiskEngine\RBRiskEngine_Public.mq5` into the MT5 data directory and calls `MetaEditor64.exe`.

## Run an automated MT5 backtest

Use demo mode first. The public EA has live orders disabled by default:

```text
InpEnableLiveOrders=false
InpEnableTesterOrders=true
```

Run a basic Strategy Tester job:

```powershell
powershell -ExecutionPolicy Bypass -File tools\mt5_backtest.ps1 -CompileFirst
```

Use the fictitious example preset:

```powershell
powershell -ExecutionPolicy Bypass -File tools\mt5_backtest.ps1 `
  -SetPath examples\RBRiskEngine_Public.example.set `
  -ExpertParameters RBRiskEngine_Public.example.set `
  -CompileFirst
```

Backtest artifacts are written to `runs/`, which is intentionally ignored by Git. The runner saves a redacted configuration copy as `tester.redacted.ini` for safer artifact handling.

## Analyze reports privately

Generated performance reports are private research artifacts by default. The report analyzer writes to an ignored folder unless another output path is explicitly provided:

```powershell
python tools\analyze_mt5_reports.py --output reports\private\analise_relatorios.md
```

Do not commit generated performance reports unless they are synthetic, intentionally public and manually reviewed.

## Example configuration

Public examples are in `examples/`.

They are fictitious and should not be treated as optimized settings. Real presets, broker data, account reports and production settings should stay outside public Git.

## Logs and reports

The tools can collect tester logs and summarize backtest output. Generated reports belong in ignored folders such as `runs/`, `reports/` or `backtests/` unless they are fully synthetic and intentionally safe for public release.

## What is not included

The public version does not include:

- proprietary strategy logic;
- real presets;
- real broker exports;
- real account reports;
- optimization grids;
- production parameters;
- sensitive backtest results;
- account numbers, server names, credentials or local machine paths.

## Known limitations

- The public EA is an educational scaffold, not a finished strategy.
- Backtests can overestimate future performance.
- Spread, slippage, latency and broker execution can materially change results.
- CFDs and leveraged products can cause rapid losses.
- A security audit and public-history cleanup were completed before the official public release; see `SECURITY_AUDIT_REPORT.md`.

## Roadmap

Public roadmap:

- keep documentation clean and educational;
- improve examples with synthetic data only;
- keep the public EA safe and readable;
- maintain strong `.gitignore` coverage;
- improve safe automation around compile, test and report collection;
- avoid publishing performance claims.

Non-public research, real reports, broker data, production presets and internal planning stay outside this repository. See `docs/PUBLICATION_BOUNDARY.md`.

## Security

See `SECURITY.md` and `SECURITY_AUDIT_REPORT.md`.

Do not commit credentials, `.set` production files, broker exports, real reports, account identifiers or logs.

## Responsibility

This repository is for software engineering and educational research. It is not financial advice. Trading involves risk, and past performance does not guarantee future results.
