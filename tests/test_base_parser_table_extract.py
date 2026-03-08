import pandas as pd

from bankparser.parser.base_parser import Parser


class DummyParser(Parser):
    def parse(self) -> None:
        return self


def test_extract_table_data_with_named_columns() -> None:
    parser = DummyParser("dummy.csv")
    table = pd.DataFrame(
        [
            {
                "date": "01/02/2024",
                "description": "Payroll",
                "amount": "1200.00",
                "balance": "2200.00",
            }
        ]
    )

    transactions = parser._extract_table_data(
        table=table,
        cols_groups_ids={
            "date": "date",
            "description": "description",
            "amount": "amount",
            "balance": "balance",
        },
        default_values={"account": "CSV Account", "currency": "COP"},
    )

    assert len(transactions) == 1
    transaction = transactions[0]
    assert str(transaction.amount) == "1200.00"
    assert str(transaction.balance) == "2200.00"
    assert transaction.account == "CSV Account"
    assert transaction.currency == "COP"


def test_extract_table_data_with_indexed_columns_and_mapper() -> None:
    parser = DummyParser("dummy.csv")
    table = pd.DataFrame(
        [
            ["01/02/2024", "Coffee", "-5.50"],
            ["02/02/2024", "Refund", "5.50"],
        ]
    )

    transactions = parser._extract_table_data(
        table=table,
        cols_groups_ids={"date": 0, "description": 1, "amount": 2},
        default_values={"account": "CSV Account", "currency": "COP"},
        function_mapper={"description": lambda value: value.upper()},
    )

    assert len(transactions) == 2
    assert transactions[0].description == "COFFEE"
    assert str(transactions[0].amount) == "-5.50"
    assert transactions[1].description == "REFUND"
