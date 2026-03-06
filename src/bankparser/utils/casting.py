"""Placeholder casting helpers for parser implementations."""

from datetime import date
from decimal import Decimal


def parse_date(value: str) -> date:
    """Parse a date string into a ``date`` object."""
    raise NotImplementedError


def parse_amount(value: str) -> Decimal:
    """Parse an amount string into a ``Decimal`` value."""
    raise NotImplementedError
