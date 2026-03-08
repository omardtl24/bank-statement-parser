import importlib
from datetime import date

import pytest


def _import_nequi_parser_class():
    module = importlib.import_module("bankparser.parser.nequi_parser")
    return module.NequiParser


def test_parse_extracts_nequi_transactions(monkeypatch: pytest.MonkeyPatch) -> None:
    NequiParser = _import_nequi_parser_class()

    statement_text = (
        "Encabezado\n"
        "01/02/2024 Pago servicio $-12,345.67 $100,000.00\n"
        "03/02/2024 Transferencia recibida $1,200.00 $101,200.00\n"
    )

    monkeypatch.setattr(
        "bankparser.parser.nequi_parser.PDFLoader.load",
        lambda *_args, **_kwargs: statement_text,
    )

    parser = NequiParser("nequi.pdf", password="secret").parse()

    assert len(parser.transactions) == 2

    debit = parser.transactions[0]
    assert debit.date == date(2024, 2, 1)
    assert debit.description == "Pago servicio"
    assert str(debit.amount) == "-12345.67"
    assert debit.account == "Nequi"
    assert debit.currency == "COP"

    credit = parser.transactions[1]
    assert credit.date == date(2024, 2, 3)
    assert credit.description == "Transferencia recibida"
    assert str(credit.amount) == "1200.00"
    assert credit.account == "Nequi"
    assert credit.currency == "COP"


def test_parse_returns_empty_transactions_for_non_matching_layout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    NequiParser = _import_nequi_parser_class()

    monkeypatch.setattr(
        "bankparser.parser.nequi_parser.PDFLoader.load",
        lambda *_args, **_kwargs: "This statement has no matching transaction rows",
    )

    parser = NequiParser("nequi.pdf").parse()

    assert parser.transactions == []
