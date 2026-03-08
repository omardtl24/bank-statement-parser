import importlib
from datetime import date

import pytest


def _import_bancolombia_parser_class():
    module = importlib.import_module("bankparser.parser.bancolombia_parser")
    return module.BancolombiaParser


def test_parse_extracts_transactions_and_skips_duplicate_pages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    BancolombiaParser = _import_bancolombia_parser_class()

    pages = [
        (
            "DESDE: 2024/01/01 HASTA: 2024/01/31\n"
            "HOJA NO 1\n"
            "01/01 Compra supermercado -12.34 1,000.00\n"
        ),
        (
            "DESDE: 2024/01/01 HASTA: 2024/01/31\n"
            "HOJA NO 1\n"
            "02/01 Duplicate page should be ignored -1.00 999.00\n"
        ),
        (
            "DESDE: 2024/01/01 HASTA: 2024/01/31\n"
            "HOJA NO 2\n"
            "03/01 Salary 1200.00 2,199.00\n"
        ),
    ]

    monkeypatch.setattr(
        "bankparser.parser.bancolombia_parser.PDFLoader.load",
        lambda *_args, **_kwargs: pages,
    )

    parser = BancolombiaParser("bancolombia.pdf", password="secret").parse()

    assert len(parser.transactions) == 2

    debit = parser.transactions[0]
    assert debit.date == date(2024, 1, 1)
    assert debit.description == "Compra supermercado"
    assert str(debit.amount) == "-12.34"
    assert debit.account == "Bancolombia"
    assert debit.currency == "COP"

    credit = parser.transactions[1]
    assert credit.date == date(2024, 1, 3)
    assert credit.description == "Salary"
    assert str(credit.amount) == "1200.00"


def test_parse_raises_for_invalid_page_layout(monkeypatch: pytest.MonkeyPatch) -> None:
    BancolombiaParser = _import_bancolombia_parser_class()

    pages = ["This page has no period and no page number metadata"]

    monkeypatch.setattr(
        "bankparser.parser.bancolombia_parser.PDFLoader.load",
        lambda *_args, **_kwargs: pages,
    )

    with pytest.raises(ValueError, match="Parsing failed due to file mismatch"):
        BancolombiaParser("bancolombia.pdf").parse()
