import sys
from argparse import ArgumentParser, FileType
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum, auto
from typing import Dict, Iterator, List, Optional, Tuple

from rich.console import Console
from rich.progress import track
from rich.table import Table
from tefas import Crawler


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

    def share_info(self) -> Tuple[float, float]:
        total_shares = 0
        total_spent = 0
        for action in self.actions:
            assert action.kind is ActionKind.BUY
            total_shares += action.num_shares
            total_spent += action.num_shares * action.share_price
        return total_shares, total_spent

    def deduct_sales(self) -> None:
        """Deduct sales in a FIFO fashion."""
        actions = sorted(self.actions, key=lambda action: action.date)

        data = defaultdict(list)
        for action in actions:
            data[action.kind].append(action)

        buys = data[ActionKind.BUY]
        sells = data[ActionKind.SELL]

        def deduct_shares(num_shares: int):
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

        self.actions = buys


def drop_sold_funds(funds: List[Fund]) -> Iterator[Fund]:
    for fund in funds.copy():
        fund.deduct_sales()
        if fund.actions:
            yield fund


@contextmanager
def ui(console: Console):
    table = Table(title="TEFAS Index")
    table.add_column("Name")
    table.add_column("Title")
    table.add_column("Purchase Date")
    table.add_column("Total Shares")
    table.add_column("Total Worth")
    table.add_column("P/L (today)")
    table.add_column("P/L (this week)")
    table.add_column("P/L (all time)")
    yield table
    console.print(table)


def display_pl(funds: List[Fund]) -> None:
    tefas = Crawler()
    rows = []

    def annotate(price: float) -> str:
        if price > 0:
            color = "green"
        elif price < 0:
            color = "red"
        else:
            color = "yellow"

        return f"[{color}]{price}[/{color}]"

    today = datetime.now()
    for fund in track(
        funds,
        transient=True,
        description="Fetching the latest data from TEFAS...",
    ):
        assert len(fund.actions) >= 1
        initial_date = fund.actions[0].date
        total_shares, total_spent = fund.share_info()

        current_data = tefas.fetch(
            start=today - timedelta(days=8),
            end=today,
            name=fund.key,
            columns=["price", "title"],
        )

        assert len(current_data) >= 7
        total_worth = total_shares * current_data.price[0].item()
        total_worth_yesterday = total_shares * current_data.price[1].item()
        total_worth_7_days_ago = total_shares * current_data.price[6].item()

        rows.append(
            (
                fund.key,
                current_data.title[0],
                str(initial_date),
                total_shares,
                total_worth,
                annotate(total_worth - total_worth_yesterday),
                annotate(total_worth - total_worth_7_days_ago),
                annotate(total_worth - total_spent),
            )
        )

    console = Console()
    with ui(console) as table:
        for row in rows:
            table.add_row(*map(str, row))


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
                _,
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
        funds = {}
        for key, action in self.iter_actions(raw_data.splitlines()):
            fund = funds.setdefault(key, Fund(key))
            fund.actions.append(action)
        return list(funds.values())


def main(argv: Optional[List[str]] = None) -> None:
    parser = ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("file_format", choices=EXPORT_FORMATS.keys())

    options = parser.parse_args(argv)
    with open(options.input_file) as stream:
        file_format = EXPORT_FORMATS[options.file_format]()
        funds = file_format.process(stream.read())

    funds = list(drop_sold_funds(funds))
    display_pl(funds)


if __name__ == "__main__":
    main()
