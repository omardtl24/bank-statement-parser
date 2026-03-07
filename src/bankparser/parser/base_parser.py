from abc import ABC, abstractmethod
from typing import List

from bankparser.models.transaction import Transaction


class Parser(ABC):
    """Parsers transform raw extract text into transaction objects."""

    def __init__(self, raw_text: str) -> None:
        self.raw_text = raw_text

    @abstractmethod
    def parse(self) -> List[Transaction]:
        """Parse raw text and return a list of transactions."""
        raise NotImplementedError
