from datetime import date, datetime
from decimal import Decimal
from typing import Union
import re

MONTHS = {
    # Spanish
    "ene": 1, "feb": 2, "mar": 3, "abr": 4,
    "may": 5, "jun": 6, "jul": 7, "ago": 8,
    "sep": 9, "oct": 10, "nov": 11, "dic": 12,

    # English
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12
}


def parse_date(value: Union[str, date, datetime]) -> Union[date, datetime]:
    """Convert a supported raw date value into date or datetime.

    Args:
        value: Date text in one of the supported statement formats, or an
            existing ``date``/``datetime`` object.

    Returns:
        A parsed ``date`` or ``datetime`` value.

    Raises:
        TypeError: If ``value`` is not a string, date, or datetime.
        KeyError: If a month abbreviation is unknown in the Lulo format.
        ValueError: If the string input does not match a supported date
            format.
    """
    
    if isinstance(value, date) or isinstance(value, datetime):
        return value

    if not isinstance(value, str):
        raise TypeError("Date must be a string, date, or datetime")

    s = value.strip()
    s_lower = s.lower()

    # ISO datetime: YYYY-MM-DDTHH:MM:SS(.ffffff)(+HH:MM)
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        pass

    # Lulo bank and Payoneer: "DD MMM. YYYY" or "DD MMM, YYYY"
    m = re.fullmatch(r"(\d{2})\s*([A-Za-z]+)[\.,]\s*(\d{4})", s_lower)
    if m:
        day, month, year = m.groups()
        return date(int(year), MONTHS[month.lower()], int(day))

    # Standard: DD/MM/YYYY
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)
    if m:
        day, month, year = map(int, m.groups())
        return date(year, month, day)

    # Google Sheets: D/MM/YYYY
    m = re.fullmatch(r"(\d{1})/(\d{2})/(\d{4})", s)
    if m:
        day, month, year = map(int, m.groups())
        return date(year, month, day)

    # Datetime: DD/MM/YYYY HH:MM:SS
    m = re.fullmatch(r"(\d{1,2})/(\d{2})/(\d{4})\s+(\d{2}):(\d{2}):(\d{2})", s)
    if m:
        day, month, year, hh, mm, ss = map(int, m.groups())
        return datetime(year, month, day, hh, mm, ss)

    raise ValueError(f"Unrecognized date format: {value}")


def parse_amount(value: str) -> Decimal:
    """Convert a raw amount value into ``Decimal``.

    Args:
        value: Numeric text (US/EU formats) or a value accepted by
            ``decimal.Decimal``.

    Returns:
        A parsed ``Decimal`` amount.

    Raises:
        ValueError: If a string input is invalid or ambiguous.
        decimal.InvalidOperation: Propagated when non-string input cannot be
            converted by ``Decimal``.
    """

    if not isinstance(value, str):
        return Decimal(value)

    s = value.strip()

    # 🇺🇸 US format: 1,234.56 or .56
    if re.fullmatch(r"[-+]?[\.]?\d{1,3}(,\d{3})*(\.\d+)?", s):
        return Decimal(s.replace(",", ""))

    # 🇪🇺 EU / LATAM: 1.234,56
    if re.fullmatch(r"[-+]?\d{1,3}(\.\d{3})*(,\d+)?", s):
        return Decimal(s.replace(".", "").replace(",", "."))

    # Simple decimal or integer
    if re.fullmatch(r"[-+]?\d+(\.\d+)?", s):
        return Decimal(s)

    raise ValueError(f"Invalid or ambiguous amount: {value}")