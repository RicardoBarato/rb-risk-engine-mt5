# Agent Instructions

This repository is the public educational version of `MT5 EA Auto Backtest Engine`.

## Current Goal

Maintain a clean, safe and professional public MetaTrader 5 / MQL5 project that demonstrates:

- Expert Advisor structure;
- risk controls;
- automated backtesting workflow;
- documentation discipline;
- separation between public educational code and non-public research artifacts.

## Public Repository Rules

- Do not commit real broker exports.
- Do not commit real `.set` presets.
- Do not commit logs, reports, account statements or optimization grids.
- Do not commit account numbers, server names, passwords, tokens or local machine paths.
- Do not publish proprietary strategy logic or production parameters.
- Keep examples synthetic and clearly marked as fictitious.

## Technical Direction

The public EA is intentionally educational. It may show a generic risk-managed structure, but it should not expose proprietary signal logic or optimized parameters.

Useful public topics:

- MQL5 EA lifecycle;
- symbol/session/spread checks;
- risk-based position sizing;
- stop-loss and take-profit placement;
- Strategy Tester automation;
- automated backtest-loop workflow;
- report parsing and validation workflow.

## Validation Workflow

1. Read the changed files.
2. Keep edits scoped.
3. Compile MQL5 when MT5 is available.
4. Run static searches for sensitive terms before publishing.
5. Update documentation when behavior or structure changes.

## Private Research

Real strategy research, backtests, presets, broker data and performance analysis should live in protected non-public storage, not in this public repository.
