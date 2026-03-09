from .base_parser import Parser
from bankparser.loader import PDFLoader
from decimal import Decimal
from bankparser.utils import parse_amount
import re

GLOBAL66_PATTERN = r"(\d{4}\-\d{2}\-\d{2}) \d{2}:\d{2}:\d{2}\s+(.+?)\s+\d+\s+\$([\d,.]+)\s+\$([\d,.]+)\s*"
GLOBAL66_COLS_GROUPS_IDS = {"date": 1, "description": 2, "amount": 3, "balance": 4}

class Global66Parser(Parser):

    def _fix_sign(self, previous_balance: Decimal, amount: Decimal, current_balance: Decimal) -> Decimal:
        """Infer signed amount based on balance delta between consecutive rows."""
        if current_balance < previous_balance:
            return -abs(amount)
        return abs(amount)

    def parse(self):
        # Load data from pdf
        text = PDFLoader.load(self.file_path, password=self.password)

        # Currency
        currency_match = re.search(r"Movimientos de cuenta en ([A-Z]{3})", text)
        if not currency_match:
            raise ValueError(f"Parsing failed due to file mismatch. File {self.file_path}")
        currency = currency_match.group(1)

        # Extract transactions
        self.transactions = self._extract_data(
            text=text,
            pattern=GLOBAL66_PATTERN,
            cols_groups_ids=GLOBAL66_COLS_GROUPS_IDS,
            default_values={"account": f"Global66 {currency}",
                            "currency": currency}
        )

        # Fix signs using running balance comparison.
        first_balance_match = re.search(r"Inicio de período:\s+\$([\d,.]+)", text)
        if not first_balance_match:
            raise ValueError(f"Parsing failed due to file mismatch. File {self.file_path}")
        previous_balance = parse_amount(first_balance_match.group(1))

        self.transactions.sort(key=lambda t: t.date)
        for transaction in self.transactions:
            if transaction.balance is None:
                continue
            transaction.amount = self._fix_sign(previous_balance, transaction.amount, transaction.balance)
            previous_balance = transaction.balance

        return self

