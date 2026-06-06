# Architecture

## Overview

`MT5 EA Auto Backtest Engine` is organized as a public educational MetaTrader 5 framework that combines a public Expert Advisor scaffold with automated Strategy Tester execution, artifact collection and report-analysis tooling.

The public EA demonstrates risk controls and automation structure, not proprietary strategy logic.

## Main folders

| Path | Purpose |
| --- | --- |
| `MQL5/Experts/RBRiskEngine/` | Public MQL5 Expert Advisor source. |
| `tools/` | Compile, backtest-loop and report-analysis automation. |
| `config/` | Local configuration example only. |
| `examples/` | Fictitious public examples. |
| `docs/` | Public documentation. |

## Expert Advisor flow

The public EA follows this high-level flow:

1. Initialize indicator handles.
2. Validate symbol, environment and session.
3. Check spread.
4. Avoid duplicate open positions for the same symbol and magic number.
5. Generate a generic educational signal.
6. Calculate position size from risk and stop distance.
7. Place orders only with stop-loss and take-profit.
8. Release indicator handles on shutdown.

## Initialization

`OnInit()` creates indicator handles. If any handle fails, initialization fails.

## Parameters

The public parameters cover:

- allowed symbol;
- live/tester order switches;
- magic number;
- risk percent;
- max spread;
- session window;
- generic EMA and ATR periods;
- ATR-based stop and take-profit ratio.

Values in the public example are fictitious and not optimized.

## Entry logic

The public EA uses a simple generic EMA cross as an educational placeholder.

Private entry logic is intentionally excluded from this repository.

## Exit logic

The public EA submits initial SL and TP with the order. It does not include proprietary exit logic, trailing logic or production management rules.

## Risk management

The public EA demonstrates:

- disabled live orders by default;
- symbol guard;
- spread guard;
- session guard;
- one-position-per-symbol/magic guard;
- position sizing by risk percent;
- mandatory SL/TP.

## Automated backtest loop

Backtests are launched through `tools/mt5_backtest.ps1`. The script prepares the local MT5 tester configuration, runs the Strategy Tester, collects generated files and keeps the resulting run artifacts under ignored folders.

The repository-side run configuration is saved as `tester.redacted.ini` to avoid retaining sensitive local runtime values in copied artifacts.

## Logs and reports

The automation can collect terminal, tester and agent logs into `runs/`. Those files are not for public Git commits.

Generated report analysis defaults to `reports/private/`, which is ignored by Git.

## Extension points

The public scaffold exposes generic extension points for educational discussion:

- signal generation;
- regime filters;
- position management;
- backtest orchestration;
- report parsing.

Production logic, optimized parameters, broker-specific configuration and validation outputs are intentionally outside the public repository.

## Limitations

The public EA is not a finished trading product. It is a safe framework for demonstrating engineering structure and automated MT5 backtest workflow.
