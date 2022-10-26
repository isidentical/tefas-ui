from __future__ import annotations

from argparse import ArgumentParser
from collections import Counter, defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from enum import Enum, auto
from functools import lru_cache, partial
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from rich.console import Console
from rich.progress import track
from rich.table import Table
from tefas import Crawler

BASE_CURRENCY = "TRY"

try:
    from forex_python.converter import get_rate
except Exception:

    def get_rate(c1: str, c2: str, date: Optional[date] = None) -> float:
        assert c1 == c2 == BASE_CURRENCY, "install forex-python for other currencies"
        return 1.0


fx_rate = partial(lru_cache(get_rate), BASE_CURRENCY)


@dataclass
class Profits:
    key: str
    title: str
    initial_date: date
    total_shares: int
    total_worth: float
    pl_today: float
    pl_week: float
    pl_all_time: float

    @property
    def simple(self) -> Dict[str, float]:
        return {
            "total_worth": self.total_worth,
            "pl_today": self.pl_today,
            "pl_week": self.pl_week,
            "pl_all_time": self.pl_all_time,
        }


class ActionKind(Enum):
    BUY = auto()
    SELL = auto()


@dataclass
class Action:
    kind: ActionKind
    date: date
    num_shares: int
    share_price: float


@dataclass
class Fund:
    key: str
    actions: List[Action] = field(default_factory=list, repr=False)

    def share_info(self, currency: str = BASE_CURRENCY) -> Tuple[float, float]:
        """Return the total spent amount (with the FX conversion by the date it was spent),
        and the total number of shares."""

        total_shares = 0
        total_spent = 0
        for action in self.actions:
            assert action.kind is ActionKind.BUY
            total_shares += action.num_shares
            total_spent += (
                action.num_shares * action.share_price * fx_rate(currency, action.date)
            )
        return total_shares, total_spent

    def calculate_profits(
        self,
        tefas: Crawler,
        currency: str = BASE_CURRENCY,
        start: datetime = datetime.now(),
    ) -> Profits:
        """Calculate daily, weekly and all time P/L in the specified currency."""

        assert len(self.actions) >= 1
        assert all(action.kind is ActionKind.BUY for action in self.actions)

        initial_date = self.actions[0].date
        total_shares, total_spent = self.share_info(currency)

        current_data = tefas.fetch(
            start=start - timedelta(days=8),
            end=start,
            name=self.key,
            columns=["price", "title", "date"],
        )

        pricing_info = {}
        for key, index in [
            ("current", 0),
            ("daily", 1),
            ("weekly", len(current_data) - 1),
        ]:
            pricing_info[key] = (
                total_shares
                * current_data.price[index].item()
                * fx_rate(currency, current_data.date[index])
            )

        total_worth = pricing_info["current"]
        return Profits(
            self.key,
            current_data.title[0],
            initial_date,
            total_shares,
            total_worth,
            total_worth - pricing_info["daily"],
            total_worth - pricing_info["weekly"],
            total_worth - total_spent,
        )

    def deduct_sales(self) -> Fund:
        """Deduct sales in a FIFO fashion."""
        actions = sorted(self.actions, key=lambda action: action.date)

        data = defaultdict(list)
        for action in actions:
            data[action.kind].append(action)

        buys = data[ActionKind.BUY]
        sells = data[ActionKind.SELL]

        def deduct_shares(num_shares: int) -> None:
            for buy in buys.copy():
                if buy.num_shares > num_shares:
                    buy.num_shares -= num_shares
                    break
                else:
                    buys.remove(buy)
                    num_shares -= buy.num_shares
                    if num_shares == 0:
                        break
            else:
                raise ValueError("Can't deduct any more shares.")

        for sell in sells.copy():
            deduct_shares(sell.num_shares)

        return replace(self, actions=buys)


def drop_sold_funds(funds: List[Fund]) -> Iterator[Fund]:
    for fund in funds.copy():
        new_fund = fund.deduct_sales()
        if new_fund.actions:
            yield new_fund


def get_profits(funds: List[Fund], currency: str = BASE_CURRENCY) -> Iterator[Profits]:
    tefas = Crawler()
    for fund in track(
        funds,
        transient=True,
        description="Fetching the latest data from TEFAS...",
    ):
        yield fund.calculate_profits(tefas, currency)


@contextmanager
def ui(console: Console) -> Iterator[Table]:
    table = Table(title="TEFAS Index")
    table.add_column("Name")
    table.add_column("Title")
    table.add_column("Purchase Date")
    table.add_column("Total Shares", justify="right")
    table.add_column("Total Worth", justify="right")
    table.add_column("P/L (today)", justify="right")
    table.add_column("P/L (this week)", justify="right")
    table.add_column("P/L (all time)", justify="right")
    yield table
    console.print(table)


def display_pl(funds: List[Fund], currency: str = BASE_CURRENCY) -> None:
    def annotate(price: float, use_color: bool = True) -> str:
        if use_color:
            if price > 0:
                color = "green"
            elif price < 0:
                color = "red"
            else:
                color = "yellow"
        else:
            color = "white"

        return f"[{color}]{price:6.4f}[/{color}] {currency}"

    console = Console()
    with ui(console) as table:
        total: Counter[Any] = Counter()
        for profits in get_profits(funds, currency):
            total.update(profits.simple)
            table.add_row(
                profits.key,
                profits.title,
                str(profits.initial_date),
                str(profits.total_shares),
                annotate(profits.total_worth, use_color=False),
                annotate(profits.pl_today),
                annotate(profits.pl_week),
                annotate(profits.pl_all_time),
            )

        table.add_row(
            *[
                f"[bold]{text}[/bold]"
                for text in (
                    "N/A",
                    "Total Portfolio",
                    "N/A",
                    "N/A",
                    annotate(total["total_worth"], use_color=False),
                    annotate(total["pl_today"]),
                    annotate(total["pl_week"]),
                    annotate(total["pl_all_time"]),
                )
            ]
        )


EXPORT_FORMATS = {}


class ExportFormat:
    def __init_subclass__(cls):
        EXPORT_FORMATS[cls.__name__.lower()] = cls

    def process(self, raw_data: str) -> List[Fund]:
        raise NotImplementedError


class Teb(ExportFormat):
    ACTION_KINDS = {
        "Alış": ActionKind.BUY,
        "Satış": ActionKind.SELL,
    }

    def normalize_float(self, data: str) -> float:
        # 5.000,50 => 5000.50
        return float(data.replace(".", "").replace(",", ".", 1))

    def iter_actions(self, lines: List[str]) -> Iterator[Tuple[str, Action]]:
        # Format:
        # <dd>/<mm>/<yyyy> <KEY>-<FQN> <Alış/Satış> <BRANCH>
        # <ACCOUNT> <AMOUNT_OF_SHARES> <PRICE> <CURRENCY>
        # <SHARES*PRICE>
        for line in lines:
            (
                date,
                mixed_name,
                action_kind,
                _,
                _,
                num_shares,
                share_price,
                currency,
                _,
            ) = line.split("\t")
            key, _ = mixed_name.split("-")

            yield key, Action(
                kind=self.ACTION_KINDS[action_kind],
                date=datetime.strptime(date, "%d/%m/%Y").date(),
                num_shares=int(self.normalize_float(num_shares)),
                share_price=self.normalize_float(share_price),
            )

    def process(self, raw_data: str) -> List[Fund]:
        funds: Dict[str, Fund] = {}
        for key, action in self.iter_actions(raw_data.splitlines()):
            fund = funds.setdefault(key, Fund(key))
            fund.actions.append(action)
        return list(funds.values())


def run_from_file(
    input_file: Path, file_format: str, *, currency: str = BASE_CURRENCY
) -> None:
    export_format = EXPORT_FORMATS[file_format]()
    with open(input_file) as stream:
        funds = export_format.process(stream.read())

    funds = list(drop_sold_funds(funds))
    display_pl(funds, currency)


def main(argv: Optional[List[str]] = None) -> None:
    parser = ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("file_format", choices=EXPORT_FORMATS.keys())
    parser.add_argument("--currency", type=str.upper, default="TRY")
    options = parser.parse_args(argv)
    run_from_file(options.input_file, options.file_format, currency=options.currency)


if __name__ == "__main__":
    main()
