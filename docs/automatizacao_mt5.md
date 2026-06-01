# MT5 Automation Workflow

This document describes the public automation flow for compiling and testing the educational EA.

## Local setup

Copy the example local configuration:

```powershell
Copy-Item config\mt5.local.example.ps1 config\mt5.local.ps1
```

Edit `config\mt5.local.ps1` with your local MT5 install directory and data directory.

The local file is ignored by Git.

## Compile

```powershell
powershell -ExecutionPolicy Bypass -File tools\mt5_compile.ps1
```

The script copies:

```text
MQL5\Experts\RBRiskEngine\RBRiskEngine_Public.mq5
```

into the configured MT5 data directory and compiles it through `MetaEditor64.exe`.

## Backtest

```powershell
powershell -ExecutionPolicy Bypass -File tools\mt5_backtest.ps1 -CompileFirst
```

Useful parameters:

```powershell
powershell -ExecutionPolicy Bypass -File tools\mt5_backtest.ps1 `
  -Symbol XAUUSD `
  -Period M1 `
  -FromDate 2025.01.01 `
  -ToDate 2025.12.31 `
  -Deposit 1000 `
  -Leverage 1:100 `
  -SetPath examples\RBRiskEngine_Public.example.set `
  -ExpertParameters RBRiskEngine_Public.example.set `
  -CompileFirst
```

Generated files go to `runs/`, which is ignored by Git.

## Credentials

Do not store login, password or server values in committed files.

If you need to pass credentials during a local run, pass them directly in your local shell or keep them in ignored local configuration. Never commit them.

## Public reporting

Only publish synthetic examples or fully sanitized reports. Real broker data, real statements, real `.set` files, real tester logs and optimization results belong in protected non-public storage.
