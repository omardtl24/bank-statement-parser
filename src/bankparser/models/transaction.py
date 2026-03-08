from dataclasses import dataclass
from datetime import date as Date, datetime as DateTime
from decimal import Decimal
from typing import Optional, Union
from bankparser.utils.casting import parse_amount, parse_date


@dataclass(slots=True)
class Transaction:
    """Structured transaction extracted from a bank statement."""

    date: Union[Date, DateTime, str]
    description: str
    amount: Union[Decimal, str]
    currency: str
    account: str
    balance: Optional[Decimal] = None

    def __post_init__(self) -> None:
        """Normalize input values to strongly typed transaction fields.

        Args:
            None.

        Returns:
            None.

        Raises:
            ValueError: Propagated if date or amount parsing fails.
            TypeError: Propagated if provided values are incompatible with
                parsing helpers.
        """
        if isinstance(self.date, str):
            self.date = parse_date(self.date)
        if isinstance(self.amount, str):
            self.amount = parse_amount(self.amount)
        if isinstance(self.balance, str):
            self.balance = parse_amount(self.balance)

    def to_dict(self) -> dict:
        """Serialize the transaction to a plain dictionary.

        Args:
            None.

        Returns:
            A dictionary with JSON-friendly values, including ISO date and
            stringified decimals.

        Raises:
            AttributeError: If ``self.date`` does not expose ``isoformat``.
        """
        return {
            "date": self.date,
            "description": self.description,
            "amount": self.amount,
            "account": self.account,
            "currency": self.currency,
            "balance": self.balance if self.balance is not None else None
        }
