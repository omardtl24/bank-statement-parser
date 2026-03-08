from datetime import date, datetime
from decimal import Decimal

import pytest

from bankparser.utils.casting import parse_amount, parse_date


def test_parse_date_accepts_existing_date_and_datetime() -> None:
    d = date(2024, 1, 31)
    dt = datetime(2024, 1, 31, 10, 11, 12)

    assert parse_date(d) == d
    assert parse_date(dt) == dt


def test_parse_date_supports_lulo_format() -> None:
    assert parse_date("05 ene. 2024") == date(2024, 1, 5)
    assert parse_date("15 DIC. 2023") == date(2023, 12, 15)


def test_parse_date_supports_standard_and_iso_formats() -> None:
    assert parse_date("05/02/2024") == date(2024, 2, 5)
    assert parse_date("5/02/2024") == date(2024, 2, 5)
    assert parse_date("2024-02-05T13:14:15") == datetime(2024, 2, 5, 13, 14, 15)
    assert parse_date("05/02/2024 13:14:15") == datetime(2024, 2, 5, 13, 14, 15)


def test_parse_date_rejects_invalid_types_and_formats() -> None:
    with pytest.raises(TypeError):
        parse_date(123)  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        parse_date("2024/02/05")

    with pytest.raises(KeyError):
        parse_date("05 xyz. 2024")


def test_parse_amount_parses_us_eu_and_simple_formats() -> None:
    assert parse_amount("1,234.56") == Decimal("1234.56")
    assert parse_amount("-1,234.56") == Decimal("-1234.56")
    assert parse_amount("1.234,56") == Decimal("1234.56")
    assert parse_amount("-1.234,56") == Decimal("-1234.56")
    assert parse_amount("100") == Decimal("100")
    assert parse_amount("100.25") == Decimal("100.25")


def test_parse_amount_accepts_non_string_values() -> None:
    assert parse_amount(10) == Decimal("10")
    assert parse_amount(Decimal("3.5")) == Decimal("3.5")


def test_parse_amount_rejects_ambiguous_or_invalid_values() -> None:
    assert parse_amount("1,23") == Decimal("1.23")

    with pytest.raises(ValueError):
        parse_amount("abc")
