from __future__ import annotations

import argparse
import math
import statistics
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


@dataclass(frozen=True)
class Trade:
    open_time: datetime
    close_time: datetime
    symbol: str
    side: str
    volume: float
    open_price: float | None
    stop_loss: float | None
    take_profit: float | None
    close_price: float | None
    gross_profit: float
    commission: float
    swap: float

    @property
    def pnl(self) -> float:
        return self.gross_profit + self.commission + self.swap

    @property
    def duration_seconds(self) -> float:
        return max(0.0, (self.close_time - self.open_time).total_seconds())


@dataclass(frozen=True)
class Session:
    first_open: datetime
    last_close: datetime
    trades: tuple[Trade, ...]

    @property
    def pnl(self) -> float:
        return sum(t.pnl for t in self.trades)

    @property
    def win_rate(self) -> float:
        return pct(sum(t.pnl > 0 for t in self.trades), len(self.trades))

    @property
    def profit_factor(self) -> float:
        wins = sum(t.pnl for t in self.trades if t.pnl > 0)
        losses = abs(sum(t.pnl for t in self.trades if t.pnl < 0))
        return wins / losses if losses else math.inf


def col_to_idx(ref: str) -> int:
    letters = "".join(ch for ch in ref if ch.isalpha())
    value = 0
    for char in letters:
        value = value * 26 + ord(char.upper()) - 64
    return value - 1


def parse_float(value: object) -> float | None:
    text = str(value).strip().replace(" ", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_time(value: object) -> datetime | None:
    text = str(value).strip()
    for fmt in ("%Y.%m.%d %H:%M:%S", "%Y.%m.%d %H:%M"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    return None


def read_shared_strings(book: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in book.namelist():
        return []
    root = ET.fromstring(book.read("xl/sharedStrings.xml"))
    values: list[str] = []
    for item in root.findall(NS + "si"):
        values.append("".join(node.text or "" for node in item.iter(NS + "t")))
    return values


def read_cell_value(cell: ET.Element, shared: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.iter(NS + "t"))

    value_node = cell.find(NS + "v")
    if value_node is None:
        return ""

    value = value_node.text or ""
    if cell_type == "s":
        try:
            return shared[int(value)]
        except (ValueError, IndexError):
            return value
    return value


def read_xlsx_rows(path: Path) -> list[list[str]]:
    with zipfile.ZipFile(path) as book:
        shared = read_shared_strings(book)
        root = ET.fromstring(book.read("xl/worksheets/sheet1.xml"))
        rows: list[list[str]] = []
        for row_node in root.findall(NS + "sheetData/" + NS + "row"):
            row: list[str] = []
            for cell in row_node.findall(NS + "c"):
                idx = col_to_idx(cell.attrib.get("r", "A1"))
                while len(row) <= idx:
                    row.append("")
                row[idx] = read_cell_value(cell, shared)
            rows.append(row)
        return rows


def find_positions_range(rows: list[list[str]]) -> tuple[int, int]:
    start = None
    for idx, row in enumerate(rows):
        padded = row + [""] * 3
        if padded[1].strip() == "Position" and padded[2].strip() == "Ativo":
            start = idx + 1
            break
    if start is None:
        raise ValueError("Nao encontrei a tabela de posicoes.")

    end = len(rows)
    for idx in range(start, len(rows)):
        if rows[idx] and rows[idx][0].strip().startswith("Ordens"):
            end = idx
            break
    return start, end


def parse_trades(path: Path) -> list[Trade]:
    rows = read_xlsx_rows(path)
    start, end = find_positions_range(rows)
    trades: list[Trade] = []

    for row in rows[start:end]:
        padded = row + [""] * 13
        open_time = parse_time(padded[0])
        close_time = parse_time(padded[8])
        gross = parse_float(padded[12])
        if open_time is None or close_time is None or gross is None:
            continue

        trades.append(
            Trade(
                open_time=open_time,
                close_time=close_time,
                symbol=padded[2].strip(),
                side=padded[3].strip(),
                volume=parse_float(padded[4]) or 0.0,
                open_price=parse_float(padded[5]),
                stop_loss=parse_float(padded[6]),
                take_profit=parse_float(padded[7]),
                close_price=parse_float(padded[9]),
                gross_profit=gross,
                commission=parse_float(padded[10]) or 0.0,
                swap=parse_float(padded[11]) or 0.0,
            )
        )

    return sorted(trades, key=lambda trade: trade.close_time)


def parse_initial_balance(path: Path) -> float | None:
    rows = read_xlsx_rows(path)
    start = None
    for idx, row in enumerate(rows):
        padded = row + [""] * 3
        if padded[0].strip().startswith("Hor") and padded[1].strip() == "Oferta":
            start = idx + 1
            break
    if start is None:
        return None

    for row in rows[start:]:
        padded = row + [""] * 14
        balance = parse_float(padded[12])
        if parse_time(padded[0]) is not None and balance is not None:
            return balance
    return None


def pct(part: int | float, total: int | float) -> float:
    return (100.0 * part / total) if total else 0.0


def quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(q * (len(ordered) - 1))
    return ordered[idx]


def metrics(values: list[float]) -> dict[str, float]:
    wins = [value for value in values if value > 0]
    losses = [value for value in values if value < 0]
    gross = sum(wins)
    loss = sum(losses)
    return {
        "net": sum(values),
        "gross": gross,
        "loss": loss,
        "pf": gross / abs(loss) if loss else math.inf,
        "wr": pct(len(wins), len(values)),
        "avg_win": statistics.mean(wins) if wins else 0.0,
        "avg_loss": statistics.mean(losses) if losses else 0.0,
        "expectancy": statistics.mean(values) if values else 0.0,
    }


def group_by_session(trades: list[Trade], max_gap_minutes: int = 20) -> list[Session]:
    sessions: list[Session] = []
    current: list[Trade] = []

    for trade in sorted(trades, key=lambda item: item.open_time):
        same_day = current and trade.open_time.date() == current[-1].open_time.date()
        gap_ok = current and (trade.open_time - current[-1].open_time).total_seconds() <= max_gap_minutes * 60
        if not current or (same_day and gap_ok):
            current.append(trade)
        else:
            sessions.append(make_session(current))
            current = [trade]

    if current:
        sessions.append(make_session(current))
    return sessions


def make_session(trades: list[Trade]) -> Session:
    return Session(
        first_open=min(t.open_time for t in trades),
        last_close=max(t.close_time for t in trades),
        trades=tuple(trades),
    )


def drawdown_summary(trades: list[Trade], start_balance: float) -> dict[str, float]:
    balance = start_balance
    peak = start_balance
    max_dd = 0.0
    max_dd_pct = 0.0

    for trade in trades:
        balance += trade.pnl
        peak = max(peak, balance)
        drawdown = peak - balance
        if drawdown > max_dd:
            max_dd = drawdown
            max_dd_pct = pct(drawdown, peak)

    return {
        "start": start_balance,
        "end": balance,
        "peak": peak,
        "return_pct": pct(balance - start_balance, start_balance),
        "max_dd": max_dd,
        "max_dd_pct": max_dd_pct,
    }


def format_money(value: float) -> str:
    return f"{value:,.2f}".replace(",", " ")


def format_pf(value: float) -> str:
    return "inf" if value == math.inf else f"{value:.2f}"


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        output.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(output)


def grouped_rows(trades: list[Trade], key_name: str) -> list[list[object]]:
    groups: dict[object, list[Trade]] = defaultdict(list)
    for trade in trades:
        if key_name == "symbol":
            key = trade.symbol
        elif key_name == "side":
            key = trade.side
        elif key_name == "hour":
            key = trade.open_time.hour
        elif key_name == "weekday":
            key = trade.open_time.strftime("%a")
        else:
            raise ValueError(key_name)
        groups[key].append(trade)

    rows = []
    for key, items in groups.items():
        stats = metrics([trade.pnl for trade in items])
        rows.append(
            [
                key,
                len(items),
                format_money(stats["net"]),
                f'{stats["wr"]:.1f}%',
                format_pf(stats["pf"]),
                format_money(stats["expectancy"]),
            ]
        )
    return sorted(rows, key=lambda row: float(str(row[2]).replace(" ", "")), reverse=True)


def session_rows(sessions: list[Session], reverse: bool) -> list[list[object]]:
    ordered = sorted(sessions, key=lambda session: session.pnl, reverse=reverse)
    rows = []
    for session in ordered[:10]:
        sides = Counter(trade.side for trade in session.trades)
        symbols = ",".join(sorted(set(trade.symbol for trade in session.trades)))
        rows.append(
            [
                session.first_open.strftime("%Y-%m-%d %H:%M"),
                session.last_close.strftime("%Y-%m-%d %H:%M"),
                len(session.trades),
                format_money(session.pnl),
                f"{session.win_rate:.1f}%",
                format_pf(session.profit_factor),
                f"{sides.get('buy', 0)}/{sides.get('sell', 0)}",
                symbols,
            ]
        )
    return rows


def analyze_report(path: Path) -> str:
    trades = parse_trades(path)
    start_balance = parse_initial_balance(path) or 1000.0
    stats = metrics([trade.pnl for trade in trades])
    drawdown = drawdown_summary(trades, start_balance)
    sessions = group_by_session(trades)
    durations = [trade.duration_seconds for trade in trades]

    lines = [f"## {path.name}", ""]
    lines.append(
        markdown_table(
            ["Metrica", "Valor"],
            [
                ["Trades", len(trades)],
                ["Saldo inicial", format_money(drawdown["start"])],
                ["Saldo final estimado", format_money(drawdown["end"])],
                ["Retorno", f'{drawdown["return_pct"]:.1f}%'],
                ["Lucro liquido", format_money(stats["net"])],
                ["Profit factor", format_pf(stats["pf"])],
                ["Win rate", f'{stats["wr"]:.1f}%'],
                ["Expectancy por trade", format_money(stats["expectancy"])],
                ["Drawdown maximo", format_money(drawdown["max_dd"])],
                ["Drawdown maximo %", f'{drawdown["max_dd_pct"]:.1f}%'],
                ["Duracao mediana", f"{statistics.median(durations):.0f}s"],
                ["Trades ate 5 min", f"{pct(sum(d <= 300 for d in durations), len(durations)):.1f}%"],
                ["SL informado", f"{pct(sum(t.stop_loss is not None for t in trades), len(trades)):.1f}%"],
                ["TP informado", f"{pct(sum(t.take_profit is not None for t in trades), len(trades)):.1f}%"],
            ],
        )
    )

    lines.extend(["", "### Por ativo", "", markdown_table(["Chave", "Trades", "Net", "WR", "PF", "Exp"], grouped_rows(trades, "symbol")[:12])])
    lines.extend(["", "### Por lado", "", markdown_table(["Chave", "Trades", "Net", "WR", "PF", "Exp"], grouped_rows(trades, "side"))])
    lines.extend(["", "### Por hora", "", markdown_table(["Hora", "Trades", "Net", "WR", "PF", "Exp"], grouped_rows(trades, "hour"))])
    lines.extend(["", "### Melhores sessoes", "", markdown_table(["Inicio", "Fim", "Trades", "Net", "WR", "PF", "Buy/Sell", "Ativos"], session_rows(sessions, True))])
    lines.extend(["", "### Piores sessoes", "", markdown_table(["Inicio", "Fim", "Trades", "Net", "WR", "PF", "Buy/Sell", "Ativos"], session_rows(sessions, False))])

    chaos = [session for session in sessions if session.pnl <= -100 or session.profit_factor < 0.75 and len(session.trades) >= 10]
    technique = [session for session in sessions if session.pnl >= 100 and session.profit_factor >= 1.4]
    lines.extend(
        [
            "",
            "### Classificacao preliminar",
            "",
            f"- Sessoes candidatas a tecnica: {len(technique)}",
            f"- Sessoes candidatas a caos: {len(chaos)}",
            f"- Maior ganho em sessao: {format_money(max((s.pnl for s in sessions), default=0.0))}",
            f"- Maior perda em sessao: {format_money(min((s.pnl for s in sessions), default=0.0))}",
        ]
    )

    return "\n".join(lines)


def build_report(paths: list[Path]) -> str:
    lines = [
        "# Analise dos Relatorios MT5",
        "",
        "Relatorio gerado automaticamente por `tools/analyze_mt5_reports.py`.",
        "",
        "A leitura usa lucro liquido por posicao: lucro + comissao + swap.",
        "",
    ]
    for path in paths:
        lines.append(analyze_report(path))
        lines.append("")

    lines.extend(
        [
            "## Research checklist",
            "",
            "1. Keep raw broker exports outside Git.",
            "2. Treat session and spread as first-class risk variables.",
            "3. Use a session loss limit before increasing risk.",
            "4. Pause after adverse sequences.",
            "5. Separate signal research from execution-risk controls.",
            "6. Validate ideas on demo data before any live use.",
            "7. Do not infer future performance from a single historical sample.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analisa relatorios historicos do MT5 em XLSX.")
    parser.add_argument("reports", nargs="*", type=Path, help="Arquivos .xlsx. Se vazio, usa *.xlsx da pasta atual.")
    parser.add_argument("--output", type=Path, default=Path("docs/analise_relatorios.md"))
    args = parser.parse_args()

    reports = args.reports or sorted(Path(".").glob("*.xlsx"))
    if not reports:
        raise SystemExit("Nenhum .xlsx encontrado.")

    report = build_report([path for path in reports if path.suffix.lower() == ".xlsx"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"Analise escrita em {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
