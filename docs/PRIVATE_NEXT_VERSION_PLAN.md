# Private Next Version Plan

## Recommended private repository name

Recommended:

- `rb-risk-engine-v5-private`

Alternatives:

- `rb-ouro-v5-private`
- `rb-vector-risk-lab`
- `mt5-risk-engine-private`

The recommended name is more professional because it avoids overemphasizing one symbol, avoids the legacy short-term label and matches the public repository identity.

## Private scope

The private repository should contain:

- advanced logic;
- proprietary filters;
- real parameters;
- real `.set` files;
- real broker exports;
- real backtests;
- optimization results;
- walk-forward results;
- Monte Carlo analysis;
- execution logs;
- private documentation;
- broker-specific notes.

## Priorities

- Robustness before headline return.
- Risk-adjusted return.
- Drawdown control.
- Session and regime validation.
- Execution-cost modeling.
- Forward demo validation.
- Protection against overfitting.
- Clear separation of raw data, processed reports and source code.

## Suggested structure

```text
.
|-- MQL5/
|-- config/private-presets/
|-- data/private/
|-- reports/private/
|-- runs/
|-- tools/
|-- docs/
`-- README.md
```

## Migration rule

Do not migrate old files blindly. Review each file before copying it into the private repository.

Exclude credentials, unnecessary logs, stale experiments and anything that creates security risk without research value.
