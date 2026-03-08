import pandas as pd
from bankparser.loader.base_loader import Loader


class CSVLoader(Loader):
    """Loader for CSV bank statements."""

    def load(
        file_path: str,
        has_headers: bool = True,
        delimiter: str = ",",
    ) -> pd.DataFrame:
        """Load CSV content into a DataFrame.

        Args:
            file_path: Path to the CSV statement.
            has_headers: Whether the first row contains column headers.
            delimiter: Field separator used by the CSV file.

        Returns:
            A ``pandas.DataFrame`` with CSV rows and columns.

        Raises:
            FileNotFoundError: If ``file_path`` does not exist.
            pandas.errors.ParserError: If CSV parsing fails.
            UnicodeDecodeError: If the file has an unsupported encoding.
        """
        header = 0 if has_headers else None
        # Preserve original textual values (especially monetary formatting).
        return pd.read_csv(
            file_path,
            header=header,
            sep=delimiter,
            dtype=str,
            keep_default_na=False,
        )
