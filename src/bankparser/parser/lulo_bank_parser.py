from bankparser.parser import Parser
from bankparser.loader.pdf_loader import PDFLoader
import re

PARTS_PATTERN = r"Movimientos\s*(.*?)\s*Bolsillos\s*(.*)"
MOVEMENTS_PATTERN = r"\s*\d*\s*(\d{2} [a-z]*\. \d{4})\s*\d{2} [a-z]*\. \d{4}\s*(.*)\s*([\+\-][\d,\.]+)"
POCKETS_PATTERN = r"\s*\d*\s*(\d{2} [a-z]*\. \d{4})\s*(.*)\s*([\+\-][\d,\.]+)"
MOVEMENTS_COLS_GROUPS_IDS = {"date": 1, "description": 2, "amount": 3}
MOVEMENTS_DEFAULT_VALUES = {"currency": "COP", "account": "Lulo Bank"}
POCKETS_COLS_GROUPS_IDS = {"date": 1, "description": 2, "amount": 3}
POCKETS_DEFAULT_VALUES = {"account": "Lulo Bank Pockets", "currency": "COP"}

class LuloBankParser(Parser):
    def parse(self) -> None:
        """Parse a Lulo Bank statement and populate transaction results.

        Args:
            None.

        Returns:
            None. The method updates ``self.transactions`` in place.

        Raises:
            ValueError: If the statement content does not match the expected
                section split between movements and pockets.
            Exception: Propagates loader, regex, or transaction-construction
                errors raised during parsing.
        """
        # Load document
        raw_input = PDFLoader.load(self.file_path, password=self.password)
        # Split document into parts and extract transactions from movements part
        
        splitter = re.search(PARTS_PATTERN,raw_input,re.DOTALL)
        if splitter:
            movements = splitter.group(1).strip()
            pockets = splitter.group(2).strip()
        else:
            raise ValueError(f"Parsing failed due to file mismatch. File {self.file_path}")
        # Extract movements transactions
        
        movements_transactions = self._extract_data(
            movements,
            MOVEMENTS_PATTERN,
            MOVEMENTS_COLS_GROUPS_IDS,
            MOVEMENTS_DEFAULT_VALUES,
        )
        # Extract pockets transactions
        pockets_transactions = self._extract_data(
            pockets,
            POCKETS_PATTERN,
            POCKETS_COLS_GROUPS_IDS,
            POCKETS_DEFAULT_VALUES,
        )
        # Define result list
        self.transactions = movements_transactions + pockets_transactions
        return self
