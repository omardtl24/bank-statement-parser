from .base_parser import Parser
from bankparser.loader.pdf_loader import PDFLoader
import re
from typing import Optional

PARTS_PATTERN = r"Movimientos\s*(.*?)\s*Bolsillos\s*(.*)"
MOVEMENTS_PATTERN = r"\s*\d*\s*(\d{2} [a-z]*\. \d{4})\s*\d{2} [a-z]*\. \d{4}\s*(.*)\s*([\+\-][\d,\.]+)"
POCKETS_PATTERN = r"\s*\d*\s*(\d{2} [a-z]*\. \d{4})\s*(.*)\s*([\+\-][\d,\.]+)"
MOVEMENTS_COLS_GROUPS_IDS = {"date": 1, "description": 2, "amount": 3}
MOVEMENTS_DEFAULT_VALUES = {"currency": "COP", "account": "Lulo Bank"}
POCKETS_COLS_GROUPS_IDS = {"date": 1, "description": 2, "amount": 3}
POCKETS_DEFAULT_VALUES = {"account": "Lulo Bank Pockets", "currency": "COP"}

class LuloBankParser(Parser):
    def __init__(
        self,
        file_path: str,
        password: Optional[str] = None,
        section: str = "both",
        **kwargs,
    ) -> None:
        """Initialize parser with section selection.

        Args:
            file_path: Path to the PDF statement file.
            password: Optional password used to open protected files.
            section: Section to parse. Supported values are ``"movements"``,
                ``"pockets"``, and ``"both"``.
            **kwargs: Additional parser-specific options.
        """
        super().__init__(file_path=file_path, password=password, section=section, **kwargs)

    def parse(self) -> None:
        """Parse a Lulo Bank statement and populate transaction results.

        Args:
            None.

        Returns:
            None. The method updates ``self.transactions`` in place.

        Raises:
            ValueError: If the statement content does not match the expected
                section split between movements and pockets.
            ValueError: If ``section`` is not one of ``movements``,
                ``pockets``, or ``both``.
            Exception: Propagates loader, regex, or transaction-construction
                errors raised during parsing.
        """
        section = str(self.kwargs.get("section", "both")).lower().strip()
        if section not in {"movements", "pockets", "both"}:
            raise ValueError(
                "Invalid section option. Use 'movements', 'pockets', or 'both'."
            )

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
        
        movements_transactions = []
        if section in {"movements", "both"}:
            movements_transactions = self._extract_data(
                movements,
                MOVEMENTS_PATTERN,
                MOVEMENTS_COLS_GROUPS_IDS,
                MOVEMENTS_DEFAULT_VALUES,
            )
        # Extract pockets transactions
        pockets_transactions = []
        if section in {"pockets", "both"}:
            pockets_transactions = self._extract_data(
                pockets,
                POCKETS_PATTERN,
                POCKETS_COLS_GROUPS_IDS,
                POCKETS_DEFAULT_VALUES,
            )
        # Define result list
        self.transactions = movements_transactions + pockets_transactions
        return self
