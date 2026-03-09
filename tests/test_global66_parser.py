import importlib
from datetime import datetime

import pytest


def _import_global66_parser_class():
    module = importlib.import_module("bankparser.parser.global66_parser")
    return module.Global66Parser


def test_parse_extracts_transactions_and_infers_sign_from_balance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    Global66Parser = _import_global66_parser_class()

    statement_text = (
        "Movimientos de cuenta en USD\n"
        "Inicio de período: $100.00\n"
        "2024-01-01 10:00:00 Coffee shop 123 $10.00 $90.00\n"
        "2024-01-01 12:00:00 Salary 456 $20.00 $110.00\n"
    )

    monkeypatch.setattr(
        "bankparser.parser.global66_parser.PDFLoader.load",
        lambda *_args, **_kwargs: statement_text,
    )

    parser = Global66Parser("global66.pdf", password="secret").parse()

    assert len(parser.transactions) == 2

    debit = parser.transactions[0]
    assert debit.date == datetime(2024, 1, 1, 0, 0, 0)
    assert debit.description == "Coffee shop"
    assert str(debit.amount) == "-10.00"
    assert str(debit.balance) == "90.00"
    assert debit.account == "Global66 USD"
    assert debit.currency == "USD"

    credit = parser.transactions[1]
    assert credit.date == datetime(2024, 1, 1, 0, 0, 0)
    assert credit.description == "Salary"
    assert str(credit.amount) == "20.00"
    assert str(credit.balance) == "110.00"


def test_parse_raises_for_missing_currency_or_initial_balance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    Global66Parser = _import_global66_parser_class()

    missing_currency_text = (
        "Inicio de período: $100.00\n"
        "2024-01-01 10:00:00 Coffee 123 $10.00 $90.00\n"
    )
    monkeypatch.setattr(
        "bankparser.parser.global66_parser.PDFLoader.load",
        lambda *_args, **_kwargs: missing_currency_text,
    )
    with pytest.raises(ValueError, match="Parsing failed due to file mismatch"):
        Global66Parser("global66.pdf").parse()

    missing_initial_balance_text = (
        "Movimientos de cuenta en USD\n"
        "2024-01-01 10:00:00 Coffee 123 $10.00 $90.00\n"
    )
    monkeypatch.setattr(
        "bankparser.parser.global66_parser.PDFLoader.load",
        lambda *_args, **_kwargs: missing_initial_balance_text,
    )
    with pytest.raises(ValueError, match="Parsing failed due to file mismatch"):
        Global66Parser("global66.pdf").parse()


def test_global66_parser_is_exported_from_public_packages() -> None:
    parser_module = importlib.import_module("bankparser.parser")
    package_module = importlib.import_module("bankparser")

    assert hasattr(parser_module, "Global66Parser")
    assert hasattr(package_module, "Global66Parser")
