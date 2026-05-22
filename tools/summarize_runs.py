import argparse
import csv
import re
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class RunSummary:
    run: str
    final_balance: str = ""
    profit_factor: str = ""
    total_net_profit: str = ""
    balance_drawdown_maximal: str = ""
    equity_drawdown_maximal: str = ""
    total_trades: str = ""
    short_trades: str = ""
    long_trades: str = ""
    consecutive_losses: str = ""
    report_files: str = ""
    summary_status: str = ""


PATTERNS = {
    "final_balance": [r"final balance\s+([0-9.,]+)", r"Balance\s+([0-9.,]+)"],
    "profit_factor": [r"Profit Factor\s+([0-9.,]+)", r"profit factor\s+([0-9.,]+)"],
    "total_net_profit": [r"Total Net Profit\s+([-0-9.,]+)"],
    "balance_drawdown_maximal": [r"Balance Drawdown Maximal\s+([^\n\r]+)"],
    "equity_drawdown_maximal": [r"Equity Drawdown Maximal\s+([^\n\r]+)"],
    "total_trades": [r"Total Trades\s+([0-9]+)"],
    "short_trades": [r"Short Trades \(won %\)\s+([^\n\r]+)"],
    "long_trades": [r"Long Trades \(won %\)\s+([^\n\r]+)"],
    "consecutive_losses": [r"Maximal consecutive losses\s+([^\n\r]+)", r"consecutive losses\s+([^\n\r]+)"],
}


def read_text_safe(path: Path) -> str:
    for encoding in ("utf-16", "utf-8", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding, errors="ignore")
        except Exception:
            pass
    return ""


def extract_value(text: str, key: str) -> str:
    for pat in PATTERNS[key]:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return " ".join(match.group(1).strip().split())
    return ""


def summarize_run(run_dir: Path) -> RunSummary:
    report_candidates = sorted(
        list(run_dir.glob("*.htm")) + list(run_dir.glob("*.html")) + list(run_dir.glob("*.xml")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    log_candidates = [run_dir / "summary.txt", run_dir / "tester.log", run_dir / "agent-1.log"]

    combined = []
    for path in report_candidates[:3] + [p for p in log_candidates if p.exists()]:
        combined.append(read_text_safe(path))
    text = "\n".join(combined)

    summary = RunSummary(run=run_dir.name)
    summary.report_files = ", ".join(p.name for p in report_candidates[:5])

    if not text.strip():
        summary.summary_status = "sem_relatorio_ou_log_lido"
        return summary

    for key in PATTERNS:
        setattr(summary, key, extract_value(text, key))

    if re.search(r"error|failed|excedeu|timeout|nao gerou|não gerou", text, re.IGNORECASE):
        summary.summary_status = "verificar_log"
    elif summary.final_balance or summary.total_net_profit or summary.profit_factor:
        summary.summary_status = "ok"
    else:
        summary.summary_status = "sem_metricas_extraidas"

    return summary


def write_csv(rows, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(rows[0]).keys()) if rows else list(asdict(RunSummary(run="")).keys())
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_markdown(rows, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Leaderboard RB Ouro / MT5",
        "",
        "Tabela gerada automaticamente a partir da pasta `runs/`.",
        "",
        "| Run | Status | Final balance | Profit factor | Net profit | Balance DD | Equity DD | Trades | Reports |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.run} | {row.summary_status} | {row.final_balance} | {row.profit_factor} | "
            f"{row.total_net_profit} | {row.balance_drawdown_maximal} | {row.equity_drawdown_maximal} | "
            f"{row.total_trades} | {row.report_files} |"
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Resume relatorios/logs de backtests MT5 em runs/.")
    parser.add_argument("--runs", default="runs", help="Pasta com subpastas de rodadas.")
    parser.add_argument("--csv", default="docs/leaderboard_rb_ouro.csv", help="CSV de saida.")
    parser.add_argument("--output", default="docs/leaderboard_rb_ouro.md", help="Markdown de saida.")
    args = parser.parse_args()

    runs_root = Path(args.runs)
    if not runs_root.exists():
        raise SystemExit(f"Pasta de runs nao encontrada: {runs_root}")

    rows = [summarize_run(path) for path in sorted(runs_root.iterdir()) if path.is_dir()]
    rows.sort(key=lambda r: r.run, reverse=True)

    write_csv(rows, Path(args.csv))
    write_markdown(rows, Path(args.output))

    print(f"Rodadas resumidas: {len(rows)}")
    print(f"CSV: {args.csv}")
    print(f"Markdown: {args.output}")


if __name__ == "__main__":
    main()
