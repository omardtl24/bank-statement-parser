import importlib
from datetime import date

import pandas as pd
import pytest


def _import_payoneer_parser_class():
    module = importlib.import_module("bankparser.parser.payoneer_parser")
    return module.PayoneerParser


def test_parse_extracts_transactions_grouped_by_currency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    PayoneerParser = _import_payoneer_parser_class()

    table = pd.DataFrame(
        [
            {
                "Date": "01/02/2024",
                "Description": "USD Payment",
                "Amount": "100.00",
                "Currency": "USD",
            },
            {
                "Date": "02/02/2024",
                "Description": "EUR Fee",
                "Amount": "-10.50",
                "Currency": "EUR",
            },
        ]
    )

    monkeypatch.setattr(
        "bankparser.parser.payoneer_parser.CSVLoader.load",
        lambda *_args, **_kwargs: table,
    )

    parser = PayoneerParser("payoneer.csv").parse()

    assert len(parser.transactions) == 2

    first = parser.transactions[0]
    assert first.date == date(2024, 2, 1)
    assert first.description == "USD Payment"
    assert str(first.amount) == "100.00"
    assert first.currency == "USD"
    assert first.account == "Payoneer USD"

    second = parser.transactions[1]
    assert second.date == date(2024, 2, 2)
    assert second.description == "EUR Fee"
    assert str(second.amount) == "-10.50"
    assert second.currency == "EUR"
    assert second.account == "Payoneer EUR"


def test_parse_raises_when_required_columns_are_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    PayoneerParser = _import_payoneer_parser_class()

    table = pd.DataFrame(
        [
            {
                "Date": "01/02/2024",
                "Description": "Missing amount and currency",
            }
        ]
    )

    monkeypatch.setattr(
        "bankparser.parser.payoneer_parser.CSVLoader.load",
        lambda *_args, **_kwargs: table,
    )

    with pytest.raises(KeyError):
        PayoneerParser("payoneer.csv").parse()
