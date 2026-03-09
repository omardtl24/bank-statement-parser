import importlib
import sys
import types
from datetime import date

import pytest


def _ensure_parser_imports() -> None:
    """Provide missing model symbols required by parser imports in this repo."""
    if "bankparser.models.category" not in sys.modules:
        category_module = types.ModuleType("bankparser.models.category")
        category_module.Category = object
        category_module.Subcategory = object
        sys.modules["bankparser.models.category"] = category_module


def _import_lulo_parser_class():
    _ensure_parser_imports()
    module = importlib.import_module("bankparser.parser.lulo_bank_parser")
    return module.LuloBankParser


def test_parse_extracts_movements_and_pockets(monkeypatch: pytest.MonkeyPatch) -> None:
    LuloBankParser = _import_lulo_parser_class()

    statement_text = (
        "Header text\n"
        "Movimientos\n"
        "1 05 ene. 2024 06 ene. 2024 Supermercado -12,34\n"
        "2 07 ene. 2024 08 ene. 2024 Nomina +1.234,56\n"
        "Bolsillos\n"
        "1 09 ene. 2024 Ahorro +10,00\n"
    )

    monkeypatch.setattr(
        "bankparser.parser.lulo_bank_parser.PDFLoader.load",
        lambda *_args, **_kwargs: statement_text,
    )

    parser = LuloBankParser("dummy.pdf", password="secret").parse()

    assert len(parser.transactions) == 3

    movement_debit = parser.transactions[0]
    assert movement_debit.date == date(2024, 1, 5)
    assert movement_debit.description == "Supermercado"
    assert str(movement_debit.amount) == "-12.34"
    assert movement_debit.account == "Lulo Bank"
    assert movement_debit.currency == "COP"

    movement_credit = parser.transactions[1]
    assert movement_credit.date == date(2024, 1, 7)
    assert movement_credit.description == "Nomina"
    assert str(movement_credit.amount) == "1234.56"

    pocket = parser.transactions[2]
    assert pocket.date == date(2024, 1, 9)
    assert pocket.description == "Ahorro"
    assert str(pocket.amount) == "10.00"
    assert pocket.account == "Lulo Bank Pockets"
    assert pocket.currency == "COP"


def test_parse_raises_for_non_lulo_layout(monkeypatch: pytest.MonkeyPatch) -> None:
    LuloBankParser = _import_lulo_parser_class()

    monkeypatch.setattr(
        "bankparser.parser.lulo_bank_parser.PDFLoader.load",
        lambda *_args, **_kwargs: "This document has no expected section markers",
    )

    with pytest.raises(ValueError, match="Parsing failed due to file mismatch"):
        LuloBankParser("wrong-layout.pdf").parse()


def test_parse_can_retrieve_only_movements(monkeypatch: pytest.MonkeyPatch) -> None:
    LuloBankParser = _import_lulo_parser_class()

    statement_text = (
        "Header text\n"
        "Movimientos\n"
        "1 05 ene. 2024 06 ene. 2024 Supermercado -12,34\n"
        "2 07 ene. 2024 08 ene. 2024 Nomina +1.234,56\n"
        "Bolsillos\n"
        "1 09 ene. 2024 Ahorro +10,00\n"
    )

    monkeypatch.setattr(
        "bankparser.parser.lulo_bank_parser.PDFLoader.load",
        lambda *_args, **_kwargs: statement_text,
    )

    parser = LuloBankParser("dummy.pdf", section="movements").parse()

    assert len(parser.transactions) == 2
    assert parser.transactions[0].account == "Lulo Bank"
    assert parser.transactions[1].account == "Lulo Bank"


def test_parse_can_retrieve_only_pockets(monkeypatch: pytest.MonkeyPatch) -> None:
    LuloBankParser = _import_lulo_parser_class()

    statement_text = (
        "Header text\n"
        "Movimientos\n"
        "1 05 ene. 2024 06 ene. 2024 Supermercado -12,34\n"
        "2 07 ene. 2024 08 ene. 2024 Nomina +1.234,56\n"
        "Bolsillos\n"
        "1 09 ene. 2024 Ahorro +10,00\n"
    )

    monkeypatch.setattr(
        "bankparser.parser.lulo_bank_parser.PDFLoader.load",
        lambda *_args, **_kwargs: statement_text,
    )

    parser = LuloBankParser("dummy.pdf", section="pockets").parse()

    assert len(parser.transactions) == 1
    assert parser.transactions[0].account == "Lulo Bank Pockets"


def test_parse_rejects_invalid_section(monkeypatch: pytest.MonkeyPatch) -> None:
    LuloBankParser = _import_lulo_parser_class()

    monkeypatch.setattr(
        "bankparser.parser.lulo_bank_parser.PDFLoader.load",
        lambda *_args, **_kwargs: "any content",
    )

    with pytest.raises(ValueError, match="Invalid section option"):
        LuloBankParser("dummy.pdf", section="invalid").parse()
