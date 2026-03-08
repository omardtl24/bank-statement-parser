from __future__ import annotations

from typing import Callable, Optional

from bankparser.loader.csv_loader import CSVLoader
from bankparser.parser.base_parser import Parser


class CSVParser(Parser):
    """Generic parser for transaction tables stored in CSV files."""

    def __init__(
        self,
        file_path: str,
        cols_groups_ids: dict[str, str | int],
        default_values: dict[str, str] | None = None,
        function_mapper: dict[str, Callable[[str], str]] | None = None,
        has_headers: bool = True,
        delimiter: str = ",",
        password: Optional[str] = None,
    ) -> None:
        """Store CSV parsing configuration.

        Args:
            file_path: Path to the CSV file.
            cols_groups_ids: Transaction-field to CSV-column mapping.
            default_values: Extra fixed values for each transaction.
            function_mapper: Optional field transformation functions.
            has_headers: Whether the CSV file includes a header row.
            delimiter: Field separator used in the CSV file.
            password: Unused, kept for base parser interface consistency.
        """
        super().__init__(file_path=file_path, password=password)
        self.cols_groups_ids = cols_groups_ids
        self.default_values = default_values or {}
        self.function_mapper = function_mapper or {}
        self.has_headers = has_headers
        self.delimiter = delimiter

    def parse(self) -> None:
        """Parse CSV rows into transactions and store them in memory."""
        table = CSVLoader.load(
            self.file_path,
            has_headers=self.has_headers,
            delimiter=self.delimiter,
        )
        self.transactions = self._extract_table_data(
            table=table,
            cols_groups_ids=self.cols_groups_ids,
            default_values=self.default_values,
            function_mapper=self.function_mapper,
        )
        return self
