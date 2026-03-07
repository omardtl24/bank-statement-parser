from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from bankparser.models.category import Category, Subcategory


@dataclass(slots=True)
class Transaction:
    """Structured transaction extracted from a bank statement."""

    date: date
    description: str
    amount: Decimal
    category: Category
    subcategory: Subcategory
    balance: Optional[Decimal] = None

    def __post_init__(self) -> None:
        """Ensure the selected subcategory belongs to the selected category."""
        self.validate_subcategory()

    def is_subcategory_in_category(self) -> bool:
        """Return whether the transaction subcategory belongs to its category."""
        return self.subcategory in self.category.subcategories

    def validate_subcategory(self) -> None:
        """Raise ``ValueError`` if subcategory does not belong to category."""
        if not self.is_subcategory_in_category():
            raise ValueError(
                f"Subcategory '{self.subcategory.name}' does not belong to "
                f"category '{self.category.name}'."
            )
    
    def to_dict(self) -> dict:
        """Return a dictionary representation of the transaction."""
        return {
            "date": self.date.isoformat(),
            "description": self.description,
            "amount": str(self.amount),
            "category": self.category.name,
            "subcategory": self.subcategory.name,
            "balance": str(self.balance) if self.balance is not None else None,
        }
