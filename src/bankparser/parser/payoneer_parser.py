from .base_parser import Parser
from bankparser.loader.csv_loader import CSVLoader

PAYONEER_COLS_GROUPS_IDS = {
    "date": "Date",
    "description": "Description",
    "amount": "Amount",
    "currency": "Currency",
}


class PayoneerParser(Parser):
    """Parser for Payoneer CSV transaction statements."""

    def parse(self) -> None:
        """Parse a Payoneer CSV statement and populate transaction results.

        Args:
            None.

        Returns:
            None. The method updates ``self.transactions`` in place.

        Raises:
            KeyError: If expected CSV columns are missing.
            ValueError: Propagated when ``Transaction`` validation fails.
            Exception: Propagates CSV loader and pandas errors.
        """
        # Load CSV rows with headers enabled (Payoneer exports include them).
        df = CSVLoader.load(self.file_path, has_headers=True)

        # Parse per currency because a single file may include multiple wallets.
        transactions_currencies = df["Currency"].unique()
        for currency in transactions_currencies:
            df_currency = df[df["Currency"] == currency]
            currency_transactions = self._extract_table_data(
                table=df_currency,
                cols_groups_ids=PAYONEER_COLS_GROUPS_IDS,
                default_values={"account": f"Payoneer {currency}"},
            )
            self.transactions.extend(currency_transactions)
        return self