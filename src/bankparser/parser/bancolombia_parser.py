from bankparser.parser import Parser
from bankparser.loader.pdf_loader import PDFLoader
import re

PATTERN_GET_PERIODS = r'\s*(?:DESDE:)?\s*(\d{4}/\d{2}/\d{2})\s*(?:HASTA:)?\s*(\d{4}/\d{2}/\d{2})'
PATTERN_PAGE = r'(?:HOJA NO|PÁGINA:)\s*(\d+)'
DATA_PATTERN  = r'^(\d{1,2}/\d{2})\s+(.+?)\s+([\-–]?(?:\d*,?\d+)?\.\d{2})\s+[\d,]+\.\d{2}$'
ACCOUNT_COLS_GROUPS_ID = { 'date': 1 , 'description' : 2 , 'amount' : 3 }
ACCOUNT_DEFAULT_VALUES = {'account':'Bancolombia' , 'currency': 'COP'}

class BancolombiaParser(Parser):
    def parse(self) -> None:
        """Parse a Bancolombia statement and populate transaction results.

        Args:
            None.

        Returns:
            None. The method updates ``self.transactions`` in place.

        Raises:
            ValueError: If a page does not include the expected statement
                period or page number metadata.
            Exception: Propagates loader, regex, or transaction-construction
                errors raised during parsing.
        """
        # Load document
        raw_pages = PDFLoader.load(self.file_path, password=self.password, split_pages=True)
        # Split document into parts and extract transactions from movements part
        structure_readed = {}
        for page in raw_pages:
            # Retreive periods from page and page number
            periods_match = re.search(PATTERN_GET_PERIODS, page)
            page_number_match = re.search(PATTERN_PAGE, page)
            if periods_match and page_number_match:
                period_1 = periods_match.group(1)
                period_2 = periods_match.group(2)
                page_number = page_number_match.group(1)
            else:
                raise ValueError(f"Parsing failed due to file mismatch. File {self.file_path}")
            # Mark page as readed in structure
            key = f'{period_1} - {period_2}'
            if key not in structure_readed:
                structure_readed[key] = [page_number]
            elif page_number in structure_readed[key]:
                continue
            else:
                structure_readed[key].append(page_number)
            # Get transactions year
            year = period_2[:4]
            transactions = self._extract_data(
                page,
                DATA_PATTERN,
                ACCOUNT_COLS_GROUPS_ID,
                default_values=ACCOUNT_DEFAULT_VALUES,
                function_mapper =  {'date': lambda x: f"{x}/{year}"}
            )
            self.transactions.extend(transactions)
        return self
