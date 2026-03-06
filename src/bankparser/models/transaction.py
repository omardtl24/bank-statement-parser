"""Transaction domain model."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass(slots=True)
class Transaction:
    """Structured transaction extracted from a bank statement."""

    date: date
    description: str
    amount: Decimal
    balance: Optional[Decimal] = None
