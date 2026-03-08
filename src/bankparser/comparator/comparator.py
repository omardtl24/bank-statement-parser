from typing import List

from bankparser.models.transaction import Transaction
from bankparser.parser.base_parser import Parser

class TransactionComparator:
    """Compares and merges transaction lists from different extracts."""

    def __init__(self, left: Parser, right: Parser) -> None:
        """Store two parser instances to compare their transactions.

        Args:
            left: Parser instance used as left-side input.
            right: Parser instance used as right-side input.

        Returns:
            None.

        Raises:
            No explicit exception is raised by this initializer.
        """
        self.left = left
        self.right = right

    def merge(self) -> List[Transaction]:
        """Build a merged transaction list from both parser outputs.

        Args:
            None.

        Returns:
            A merged list of ``Transaction`` objects.

        Raises:
            NotImplementedError: Always raised by this placeholder method
                until a concrete merge strategy is implemented.
        """
        raise NotImplementedError

    def compare(self) -> dict:
        """Compare parser outputs and return a structured result.

        Args:
            None.

        Returns:
            A dictionary with comparison details.

        Raises:
            NotImplementedError: Always raised by this placeholder method
                until comparison logic is implemented.
        """
        raise NotImplementedError
