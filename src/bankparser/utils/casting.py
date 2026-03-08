from datetime import date
from decimal import Decimal


def parse_date(value: str) -> date:
    """Convert a raw date string to a ``datetime.date`` value.

    Args:
        value: Source date string to parse.

    Returns:
        Parsed ``date`` instance.

    Raises:
        NotImplementedError: Always raised until date parsing logic is
            implemented.
    """
    raise NotImplementedError


def parse_amount(value: str) -> Decimal:
    """Convert a raw amount string to a ``Decimal`` value.

    Args:
        value: Source numeric string to parse.

    Returns:
        Parsed ``Decimal`` amount.

    Raises:
        NotImplementedError: Always raised until amount parsing logic is
            implemented.
    """
    raise NotImplementedError
