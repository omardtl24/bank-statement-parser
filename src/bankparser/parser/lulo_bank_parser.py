from bankparser.parser import BankParser
from bankparser.loader.pdf_loader import PDFLoader
import re

class LuloBankParser(BankParser):
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
        parts_pattern = r"Movimientos\s*(.*?)\s*Bolsillos\s*(.*)"
        splitter = re.search(parts_pattern,raw_input,re.DOTALL)
        if splitter:
            movements = splitter.group(1).strip()
            pockets = splitter.group(2).strip()
        else:
            raise ValueError(f"Parsing failed due to file mismatch. File {self.file_path}")
        # Extract movements transactions
        movements_pattern = r"\s*\d*\s*(\d{2} [a-z]*\. \d{4})\s*\d{2} [a-z]*\. \d{4}\s*(.*)\s*([\+\-][\d,\.]+)"
        mov_cols_groups_ids = {'date': 1, 'description' : 2, 'amount' : 3  }
        mov_default_values = {'currency': 'COP',
                              'account': "Lulo Bank"}
        movements_transactions = self._extract_data(
            movements,
            movements_pattern,
            mov_cols_groups_ids,
            mov_default_values
        )
        # Extract pockets transactions
        pockets_pattern =  r"\s*\d*\s*(\d{2} .* \d{4})\s*(.*)\s*([\+\-][\d,\.]+)"
        pkt_cols_groups_ids = {'date': 1, 'description' : 2, 'amount' : 3  }
        pkt_default_values = {'account' : 'Lulo Bank Pockets',
                              'currency': 'COP'}
        pockets_transactions = self._extract_data(
            pockets,
            pockets,
            pkt_cols_groups_ids,
            pkt_default_values
        )
        # Define result list
        self.transactions = movements_transactions + pockets_transactions
        return self
