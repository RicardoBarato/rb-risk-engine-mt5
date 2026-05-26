from __future__ import annotations

import argparse
import math
import random
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEAL_RE = re.compile(
    r"Trades\s+(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\s+deal #(\d+)\s+"
    r"(buy|sell)\s+([0-9]+(?:\.[0-9]+)?)\s+(\S+)\s+at\s+([0-9]+(?:\.[0-9]+)?)"
)
START_RE = re.compile(
    r"from\s+(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2})\s+to\s+(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2})"
)
FINAL_BALANCE_RE = re.compile(r"final balance\s+([0-9]+(?:\.[0-9]+)?)\s+USD")


@dataclass
class Deal:
    time: datetime
    side: str
    volume: float
    symbol: str
    price: float


@dataclass
class Trade:
    entry_time: datetime
    exit_time: datetime
    side: str
    volume: float
    symbol: str
    entry: float
    exit: float
    gross_pnl: float
    net_pnl: float = 0.0


@dataclass
class RunData:
    run_dir: Path
    period_start: datetime | None
    period_end: datetime | None
    final_balance: float | None
    net_adjustment: float
    trades: list[Trade]


def parse_time(value: str, fmt: str = "%Y.%m.%d %H:%M:%S") -> datetime:
    return datetime.strptime(value, fmt)


def parse_run(run_dir: Path, contract_size: float, deposit: float) -> RunData:
    log_path = run_dir / "agent-1.log"
    if not log_path.exists():
        raise FileNotFoundError(f"agent-1.log nao encontrado: {log_path}")

    deals: list[Deal] = []
    period_start: datetime | None = None
    period_end: datetime | None = None
    final_balance: float | None = None

    with log_path.open("r", encoding="utf-16", errors="ignore") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if "started with inputs" in line:
                deals = []
                final_balance = None
                match = START_RE.search(line)
                if match:
                    period_start = parse_time(match.group(1), "%Y.%m.%d %H:%M")
                    period_end = parse_time(match.group(2), "%Y.%m.%d %H:%M")
                continue

            match = DEAL_RE.search(line)
            if match:
                deals.append(
                    Deal(
                        time=parse_time(match.group(1)),
                        side=match.group(3),
                        volume=float(match.group(4)),
                        symbol=match.group(5),
                        price=float(match.group(6)),
                    )
                )
                continue

            match = FINAL_BALANCE_RE.search(line)
            if match:
                final_balance = float(match.group(1))

    trades = reconstruct_trades(deals, contract_size)
    net_adjustment = compute_net_adjustment(trades, final_balance, deposit)

    return RunData(
        run_dir=run_dir,
        period_start=period_start,
        period_end=period_end,
        final_balance=final_balance,
        net_adjustment=net_adjustment,
        trades=trades,
    )


def reconstruct_trades(deals: list[Deal], contract_size: float) -> list[Trade]:
    trades: list[Trade] = []
    open_deal: Deal | None = None

    for deal in deals:
        if open_deal is None:
            open_deal = Deal(deal.time, deal.side, deal.volume, deal.symbol, deal.price)
            continue

        if deal.side == open_deal.side:
            new_volume = open_deal.volume + deal.volume
            open_deal.price = ((open_deal.price * open_deal.volume) + (deal.price * deal.volume)) / new_volume
            open_deal.volume = new_volume
            continue

        closing_volume = min(open_deal.volume, deal.volume)
        direction = 1.0 if open_deal.side == "buy" else -1.0
        pnl = (deal.price - open_deal.price) * direction * closing_volume * contract_size
        trades.append(
            Trade(
                entry_time=open_deal.time,
                exit_time=deal.time,
                side=open_deal.side,
                volume=closing_volume,
                symbol=open_deal.symbol,
                entry=open_deal.price,
                exit=deal.price,
                gross_pnl=pnl,
            )
        )

        if deal.volume > closing_volume:
            open_deal = Deal(deal.time, deal.side, deal.volume - closing_volume, deal.symbol, deal.price)
        elif open_deal.volume > closing_volume:
            open_deal.volume -= closing_volume
        else:
            open_deal = None

    return trades


def compute_net_adjustment(trades: list[Trade], final_balance: float | None, deposit: float) -> float:
    gross_net = sum(trade.gross_pnl for trade in trades)
    for trade in trades:
        trade.net_pnl = trade.gross_pnl

    if final_balance is None or not trades:
        return 0.0

    exact_net = final_balance - deposit
    return exact_net - gross_net


def money(value: float) -> str:
    return f"{value:.2f}"


def pct(value: float) -> str:
    return f"{value:.2f}%"


def pf(values: list[float]) -> float:
    gross_win = sum(value for value in values if value > 0)
    gross_loss = abs(sum(value for value in values if value < 0))
    if gross_loss == 0:
        return math.inf if gross_win > 0 else 0.0
    return gross_win / gross_loss


def max_loss_streak(values: list[float]) -> int:
    streak = 0
    max_streak = 0
    for value in values:
        if value < 0:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak


def drawdown(values: list[float], deposit: float) -> tuple[float, float]:
    balance = deposit
    peak = deposit
    max_dd = 0.0
    max_dd_pct = 0.0
    for value in values:
        balance += value
        peak = max(peak, balance)
        dd = peak - balance
        if dd > max_dd:
            max_dd = dd
        dd_pct = 100.0 * dd / peak if peak else 0.0
        if dd_pct > max_dd_pct:
            max_dd_pct = dd_pct
    return max_dd, max_dd_pct


def stats(values: list[float], deposit: float, net_override: float | None = None) -> dict[str, float]:
    wins = [value for value in values if value > 0]
    gross_sequence_net = sum(values)
    net = gross_sequence_net if net_override is None else net_override
    max_dd, max_dd_pct = drawdown(values, deposit)
    return {
        "trades": float(len(values)),
        "net": net,
        "return_pct": 100.0 * net / deposit if deposit else 0.0,
        "final_balance": deposit + net,
        "winrate": 100.0 * len(wins) / len(values) if values else 0.0,
        "pf": pf(values),
        "expectancy": net / len(values) if values else 0.0,
        "max_dd": max_dd,
        "max_dd_pct": max_dd_pct,
        "max_loss_streak": float(max_loss_streak(values)),
    }


def quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = round((len(ordered) - 1) * q)
    return ordered[idx]


def monte_carlo(values: list[float], deposit: float, net_adjustment: float, iterations: int, seed: int) -> dict[str, float]:
    rng = random.Random(seed)
    shuffle_dd: list[float] = []
    bootstrap_net: list[float] = []
    bootstrap_dd: list[float] = []
    losing = 0

    for _ in range(iterations):
        shuffled = values[:]
        rng.shuffle(shuffled)
        _, dd_pct = drawdown(shuffled, deposit)
        shuffle_dd.append(dd_pct)

        sample = [values[rng.randrange(len(values))] for _ in values]
        net = sum(sample) + net_adjustment
        _, boot_dd_pct = drawdown(sample, deposit)
        bootstrap_net.append(net)
        bootstrap_dd.append(boot_dd_pct)
        if net < 0:
            losing += 1

    return {
        "shuffle_dd_p50": quantile(shuffle_dd, 0.50),
        "shuffle_dd_p90": quantile(shuffle_dd, 0.90),
        "shuffle_dd_p95": quantile(shuffle_dd, 0.95),
        "shuffle_dd_p99": quantile(shuffle_dd, 0.99),
        "bootstrap_return_p05": 100.0 * quantile(bootstrap_net, 0.05) / deposit,
        "bootstrap_return_p25": 100.0 * quantile(bootstrap_net, 0.25) / deposit,
        "bootstrap_return_p50": 100.0 * quantile(bootstrap_net, 0.50) / deposit,
        "bootstrap_return_p75": 100.0 * quantile(bootstrap_net, 0.75) / deposit,
        "bootstrap_return_p95": 100.0 * quantile(bootstrap_net, 0.95) / deposit,
        "bootstrap_losing_prob": 100.0 * losing / iterations,
        "bootstrap_dd_p95": quantile(bootstrap_dd, 0.95),
    }


def table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)


def grouped_stats(trades: list[Trade], key_fn, deposit: float) -> list[list[object]]:
    groups: dict[str, list[float]] = defaultdict(list)
    for trade in trades:
        groups[str(key_fn(trade))].append(trade.net_pnl)

    rows = []
    for key, values in groups.items():
        item = stats(values, deposit)
        rows.append(
            [
                key,
                int(item["trades"]),
                money(item["net"]),
                pct(item["return_pct"]),
                pct(item["winrate"]),
                "inf" if math.isinf(item["pf"]) else f'{item["pf"]:.2f}',
            ]
        )
    return sorted(rows, key=lambda row: row[0])


def top_concentration(values: list[float], deposit: float, exact_net: float) -> list[list[object]]:
    wins = sorted([value for value in values if value > 0], reverse=True)
    rows = []
    for count in [1, 2, 3, 5]:
        removed = sum(wins[:count])
        remainder = exact_net - removed
        share = 100.0 * removed / exact_net if exact_net else 0.0
        rows.append([f"Top {count} ganhos", money(removed), pct(share), money(remainder), pct(100.0 * remainder / deposit)])
    return rows


def stress_rows(
    trades: list[Trade],
    deposit: float,
    point: float,
    contract_size: float,
    net_adjustment: float,
    extra_points: list[int],
) -> list[list[object]]:
    rows = []
    gross_net = sum(trade.gross_pnl for trade in trades)
    for points in extra_points:
        values = [
            trade.gross_pnl - (points * point * contract_size * trade.volume)
            for trade in trades
        ]
        stressed_net = gross_net + net_adjustment - sum(points * point * contract_size * trade.volume for trade in trades)
        item = stats(values, deposit, stressed_net)
        rows.append(
            [
                points,
                money(item["net"]),
                pct(item["return_pct"]),
                pct(item["winrate"]),
                "inf" if math.isinf(item["pf"]) else f'{item["pf"]:.2f}',
                money(item["max_dd"]),
                pct(item["max_dd_pct"]),
            ]
        )
    return rows


def run_section(data: RunData, deposit: float, point: float, contract_size: float, iterations: int, seed: int) -> str:
    trades = data.trades
    values = [trade.gross_pnl for trade in trades]
    exact_net = (data.final_balance - deposit) if data.final_balance is not None else sum(values)
    item = stats(values, deposit, exact_net)
    mc = monte_carlo(values, deposit, data.net_adjustment, iterations, seed) if values else {}
    period = "periodo desconhecido"
    if data.period_start and data.period_end:
        period = f"{data.period_start:%Y-%m-%d} a {data.period_end:%Y-%m-%d}"

    active_months = len({trade.exit_time.strftime("%Y-%m") for trade in trades})
    active_days = len({trade.exit_time.strftime("%Y-%m-%d") for trade in trades})

    lines = [
        f"## {data.run_dir.name}",
        "",
        f"Periodo: {period}.",
        "",
        table(
            ["Metrica", "Valor"],
            [
                ["Trades", int(item["trades"])],
                ["Dias com trade", active_days],
                ["Meses ativos", active_months],
                ["Saldo final ajustado", money(item["final_balance"])],
                ["Retorno", pct(item["return_pct"])],
                ["Profit factor", "inf" if math.isinf(item["pf"]) else f'{item["pf"]:.2f}'],
                ["Winrate", pct(item["winrate"])],
                ["Expectancy/trade", money(item["expectancy"])],
                ["DD max sequencial", money(item["max_dd"])],
                ["DD max sequencial %", pct(item["max_dd_pct"])],
                ["Max loss streak", int(item["max_loss_streak"])],
            ],
        ),
        "",
        "### Stress de custo",
        "",
        "Custo extra por trade fechado, em pontos totais de round trip. Para XAUUSD com `point=0.01` e contrato 100, 20 pontos equivalem a 0.20 USD por onca vezes o lote.",
        "",
        table(
            ["Pontos extra", "Net", "Retorno", "Winrate", "PF", "DD", "DD %"],
            stress_rows(trades, deposit, point, contract_size, data.net_adjustment, [0, 5, 10, 20, 30, 50, 75, 100]),
        ),
        "",
        "### Monte Carlo",
        "",
        table(
            ["Teste", "P50", "P90/P25", "P95/P05", "P99"],
            [
                [
                    "DD por reordenacao",
                    pct(mc.get("shuffle_dd_p50", 0.0)),
                    pct(mc.get("shuffle_dd_p90", 0.0)),
                    pct(mc.get("shuffle_dd_p95", 0.0)),
                    pct(mc.get("shuffle_dd_p99", 0.0)),
                ],
                [
                    "Retorno bootstrap",
                    pct(mc.get("bootstrap_return_p50", 0.0)),
                    pct(mc.get("bootstrap_return_p25", 0.0)),
                    pct(mc.get("bootstrap_return_p05", 0.0)),
                    pct(mc.get("bootstrap_return_p95", 0.0)),
                ],
            ],
        ),
        "",
        f"Probabilidade bootstrap de resultado negativo: {pct(mc.get('bootstrap_losing_prob', 0.0))}. DD bootstrap P95: {pct(mc.get('bootstrap_dd_p95', 0.0))}.",
        "",
        "### Concentracao",
        "",
        table(["Corte", "PnL removido", "% do net", "Net restante", "Retorno restante"], top_concentration(values, deposit, exact_net)),
        "",
        "### Por ano",
        "",
        table(["Ano", "Trades", "Net", "Retorno", "Winrate", "PF"], grouped_stats(trades, lambda t: t.exit_time.year, deposit)),
        "",
        "### Por mes ativo",
        "",
        table(["Mes", "Trades", "Net", "Retorno", "Winrate", "PF"], grouped_stats(trades, lambda t: t.exit_time.strftime("%Y-%m"), deposit)),
        "",
        "### Por hora de entrada",
        "",
        table(["Hora", "Trades", "Net", "Retorno", "Winrate", "PF"], grouped_stats(trades, lambda t: f"{t.entry_time.hour:02d}", deposit)),
        "",
        "### Por dia da semana",
        "",
        table(["Dia", "Trades", "Net", "Retorno", "Winrate", "PF"], grouped_stats(trades, lambda t: t.entry_time.strftime("%A"), deposit)),
        "",
    ]
    return "\n".join(lines)


def build_report(args: argparse.Namespace) -> str:
    sections = [
        "# MT5 robustness report",
        "",
        "Relatorio gerado por `tools/mt5_robustness.py` a partir dos logs do Strategy Tester.",
        "",
        "Observacao: o MT5 fornece o saldo final real, mas o log de deals nao inclui todos os custos linha a linha. O script usa o saldo final para retorno liquido e usa os deals para PF, winrate, drawdown aproximado, concentracao e stress.",
        "",
    ]
    for run_dir in args.run_dirs:
        data = parse_run(run_dir, args.contract_size, args.deposit)
        sections.append(run_section(data, args.deposit, args.point, args.contract_size, args.iterations, args.seed))
    return "\n".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analise de robustez para runs MT5.")
    parser.add_argument("run_dirs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, default=Path("reports/robustness_report.md"))
    parser.add_argument("--deposit", type=float, default=1000.0)
    parser.add_argument("--contract-size", type=float, default=100.0)
    parser.add_argument("--point", type=float, default=0.01)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=12345)
    args = parser.parse_args()

    report = build_report(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"Relatorio escrito em {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
