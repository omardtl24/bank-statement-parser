from abc import ABC, abstractmethod
from typing import List
import pandas as pd
from bankparser.models.transaction import Transaction


class Parser(ABC):
    """Parsers transform raw extract text into transaction objects."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.transactions: List[Transaction] = []

    @abstractmethod
    def parse(self) -> self:
        """Parse raw text and return a list of transactions."""
        raise NotImplementedError

    def to_df(self) -> pd.DataFrame:
        """Build a DataFrame from parser transaction results.

        Raises:
            ValueError: If no parsed transactions are available.
        """
        if not self.transactions:
            raise ValueError("Parser results are empty. Run parse() first.")

        df = pd.DataFrame([transaction.to_dict() for transaction in self.transactions])
        if df.empty:
            raise ValueError("Parser results are empty. Run parse() first.")

        return df

