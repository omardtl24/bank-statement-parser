"""Placeholder comparison logic for transaction collections."""

from typing import List

from bankparser.models.transaction import Transaction


class TransactionComparator:
    """Compares and merges transaction lists from different extracts."""

    def __init__(self, left: List[Transaction], right: List[Transaction]) -> None:
        self.left = left
        self.right = right

    def merge(self) -> List[Transaction]:
        """Return a merged view of both transaction lists."""
        raise NotImplementedError

    def compare(self) -> dict:
        """Return a placeholder comparison result between both lists."""
        raise NotImplementedError
