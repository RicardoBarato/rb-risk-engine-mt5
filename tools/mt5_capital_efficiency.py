from __future__ import annotations

import argparse
import math
from pathlib import Path

from mt5_robustness import RunData, drawdown, parse_run, pf, table


def fmt(value: float) -> str:
    return f"{value:.2f}"


def pct(value: float) -> str:
    return f"{value:.2f}%"


def infer_name(run_dir: Path) -> str:
    name = run_dir.name
    for prefix in ("RBRiskEngine_", "MT5_"):
        if prefix in name:
            return name.split(prefix, 1)[1]
    parts = name.split("-", 2)
    return parts[-1] if parts else name


def max_notional_leverage(data: RunData, deposit: float, contract_size: float) -> tuple[float, float]:
    balance = deposit
    max_lev = 0.0
    max_notional = 0.0

    for trade in data.trades:
        equity_ref = max(balance, 1.0)
        notional = trade.volume * contract_size * trade.entry
        leverage_used = notional / equity_ref
        if leverage_used > max_lev:
            max_lev = leverage_used
            max_notional = notional
        balance += trade.gross_pnl

    return max_lev, max_notional


def run_metrics(
    data: RunData,
    deposit: float,
    contract_size: float,
    dd_target_pct: float,
    broker_leverage: float,
    max_margin_use_pct: float,
) -> dict[str, float | str]:
    values = [trade.gross_pnl for trade in data.trades]
    exact_net = (data.final_balance - deposit) if data.final_balance is not None else sum(values)
    _, dd_pct = drawdown(values, deposit)
    return_pct = 100.0 * exact_net / deposit if deposit else 0.0
    max_lev, max_notional = max_notional_leverage(data, deposit, contract_size)

    dd_scale = dd_target_pct / dd_pct if dd_pct > 0 else math.inf
    margin_fraction = max_margin_use_pct / 100.0
    margin_scale = (broker_leverage * margin_fraction / max_lev) if max_lev > 0 else math.inf
    recommended_scale = max(0.0, min(dd_scale, margin_scale))

    return {
        "name": infer_name(data.run_dir),
        "period": (
            f"{data.period_start:%Y-%m-%d}..{data.period_end:%Y-%m-%d}"
            if data.period_start and data.period_end
            else "desconhecido"
        ),
        "trades": float(len(data.trades)),
        "return_pct": return_pct,
        "dd_pct": dd_pct,
        "pf": pf(values),
        "return_dd": return_pct / dd_pct if dd_pct else math.inf,
        "max_lev": max_lev,
        "max_notional": max_notional,
        "margin_use_pct": 100.0 * max_lev / broker_leverage if broker_leverage else math.inf,
        "dd_scale": dd_scale,
        "margin_scale": margin_scale,
        "recommended_scale": recommended_scale,
        "scaled_return_pct": return_pct * recommended_scale,
        "scaled_dd_pct": dd_pct * recommended_scale,
        "scaled_margin_pct": 100.0 * max_lev * recommended_scale / broker_leverage if broker_leverage else math.inf,
    }


def row(metric: dict[str, float | str]) -> list[object]:
    return [
        metric["name"],
        metric["period"],
        int(metric["trades"]),
        pct(float(metric["return_pct"])),
        pct(float(metric["dd_pct"])),
        fmt(float(metric["pf"])),
        fmt(float(metric["return_dd"])),
        fmt(float(metric["max_lev"])) + "x",
        pct(float(metric["margin_use_pct"])),
        fmt(float(metric["recommended_scale"])) + "x",
        pct(float(metric["scaled_return_pct"])),
        pct(float(metric["scaled_dd_pct"])),
        pct(float(metric["scaled_margin_pct"])),
    ]


def build_report(args: argparse.Namespace) -> str:
    metrics = [
        run_metrics(
            parse_run(run_dir, args.contract_size, args.deposit),
            args.deposit,
            args.contract_size,
            args.dd_target_pct,
            args.broker_leverage,
            args.max_margin_use_pct,
        )
        for run_dir in args.run_dirs
    ]

    metrics.sort(key=lambda item: float(item["scaled_return_pct"]), reverse=True)
    best = metrics[0] if metrics else None

    lines = [
        "# Eficiencia de capital e alavancagem",
        "",
        "Relatorio gerado por `tools/mt5_capital_efficiency.py`.",
        "",
        "A leitura e uma aproximacao linear para comparar perfis. Ela escala retorno, DD e uso de margem como se o lote fosse multiplicado pelo mesmo fator. Serve para ranking e decisao de pesquisa, nao substitui backtest real com novo risco.",
        "",
        f"Premissas: deposito {fmt(args.deposit)}, alavancagem da corretora 1:{fmt(args.broker_leverage)}, DD alvo {pct(args.dd_target_pct)}, uso maximo de margem {pct(args.max_margin_use_pct)}.",
        "",
    ]

    if best:
        lines.extend(
            [
                "## Melhor por retorno ajustado ao limite",
                "",
                f"- Perfil: `{best['name']}`",
                f"- Escala recomendada aproximada: {fmt(float(best['recommended_scale']))}x",
                f"- Retorno ajustado aproximado: {pct(float(best['scaled_return_pct']))}",
                f"- DD ajustado aproximado: {pct(float(best['scaled_dd_pct']))}",
                f"- Uso maximo de margem ajustado: {pct(float(best['scaled_margin_pct']))}",
                "",
            ]
        )

    lines.extend(
        [
            "## Comparativo",
            "",
            table(
                [
                    "Perfil",
                    "Periodo",
                    "Trades",
                    "Retorno",
                    "DD",
                    "PF",
                    "Ret/DD",
                    "Max lev",
                    "Margem",
                    "Escala",
                    "Ret ajust.",
                    "DD ajust.",
                    "Margem ajust.",
                ],
                [row(item) for item in metrics],
            ),
            "",
            "## Como interpretar",
            "",
            "- `Max lev` estima o maior notional/equity usado por uma posicao no backtest.",
        "- `Margem` mostra quanto isso consumiria em uma conta com a alavancagem informada.",
            "- `Escala` e o menor limite entre DD alvo e margem maxima permitida.",
            "- `Ret ajust.` e `DD ajust.` mostram uma normalizacao para comparar perfis no mesmo teto de risco.",
            "- Se a escala for menor que 1.00x, o perfil esta agressivo demais para o DD alvo informado.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara eficiencia de capital de runs MT5.")
    parser.add_argument("run_dirs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, default=Path("docs/eficiencia_capital_alavancagem.md"))
    parser.add_argument("--deposit", type=float, default=1000.0)
    parser.add_argument("--contract-size", type=float, default=100.0)
    parser.add_argument("--broker-leverage", type=float, default=100.0)
    parser.add_argument("--dd-target-pct", type=float, default=30.0)
    parser.add_argument("--max-margin-use-pct", type=float, default=60.0)
    args = parser.parse_args()

    report = build_report(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"Relatorio escrito em {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
