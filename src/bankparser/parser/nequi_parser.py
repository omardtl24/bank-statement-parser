from .base_parser import Parser
from bankparser.loader.pdf_loader import PDFLoader

DATA_PATTERN = r'\s*(\d{2}/\d{2}/\d{4})\s*([A-Za-záéíóúÁÉÍÓÚ\s]+)\s*\$(-?[\d,\.]+)\s*\$(-?[\d,\.]+)\s*'
WALLET_COLS_GROUPS_IDS = {"date": 1, "description": 2, "amount": 3, "balance": 4}
WALLET_DEFAULT_VALUES = {"account": "Nequi", "currency": "COP"}

class NequiParser(Parser):
    def parse(self) -> None:
        """Parse a Nequi statement and populate transaction results.

        Args:
            None.

        Returns:
            None. The method updates ``self.transactions`` in place.

        Raises:
            Exception: Propagates loader, regex, or transaction-construction
                errors raised during parsing.
        """
        # Load document
        raw_input = PDFLoader.load(self.file_path, password=self.password)
        # Extract transactions
        self.transactions = self._extract_data(
            raw_input,
            DATA_PATTERN,
            WALLET_COLS_GROUPS_IDS,
            WALLET_DEFAULT_VALUES,
        )
        return self