from abc import ABC, abstractmethod
from typing import Callable, List, Optional
import pandas as pd
from bankparser.models.transaction import Transaction
import re

PARAMS = [
    "date",
    "description",
    "amount",
    "balance",
    "currency",
    "account"
]

class Parser(ABC):
    """Parsers transform raw extract text into transaction objects."""

    def __init__(
            self,
            file_path: str,
            password: Optional[str] = None,
            **kwargs,
        ) -> None:
        """Initialize parser state for a statement source.

        Args:
            file_path: Path to the source statement file.
            password: Optional password used to open protected files.
            **kwargs: Parser-specific options consumed by concrete parsers.

        Returns:
            None.

        Raises:
            No explicit exception is raised by this initializer.
        """
        self.file_path = file_path
        self.password = password
        self.kwargs = kwargs
        self.transactions: List[Transaction] = []

    @abstractmethod
    def parse(self) -> None:
        """Parse raw input and populate ``self.transactions``.

        Args:
            None.

        Returns:
            None.

        Raises:
            NotImplementedError: Always raised by the abstract base
                implementation. Concrete parsers must override this method.
        """
        raise NotImplementedError
    
    def _extract_data(self,
                      text: str,
                      pattern: str,
                      cols_groups_ids: dict[str, int | None],
                      default_values: dict[str, str] | None = None,
                      function_mapper: dict[str, Callable[[str], str]] | None = None,
                      amount_groups_ids: dict[str, int | None] | None = None,
        ) -> List[Transaction]:
        """Extract transactions from text lines using a regular expression.

        Args:
            text: Raw text to scan line by line.
            pattern: Regular expression with capture groups for transaction
                fields.
            cols_groups_ids: Mapping between transaction field names and regex
                group indices.
            default_values: Fallback or fixed values injected into every
                extracted transaction.
            function_mapper: Mapping between transaction field names and functions that take 
                the extracted string value and return a transformed value.Applied after regex 
                extraction and default value injection.
            amount_groups_ids: Optional mapping that supports split amount
                extraction from separate columns, with accepted keys
                ``income`` and/or ``expense``. If provided, ``amount`` is
                generated using the first non-empty value where expense values
                are normalized to negative amounts.

        Returns:
            A list of ``Transaction`` objects created from all matching lines.

        Raises:
            AssertionError: If ``cols_groups_ids`` or ``default_values``
                contains unsupported field names.
            IndexError: If a configured group index does not exist for a
                regex match.
            ValueError: Propagated when ``Transaction`` validation fails
                (for example, invalid date/amount parsing).
        """

        default_values = default_values or {}
        function_mapper = function_mapper or {}
        amount_groups_ids = amount_groups_ids or {}

        assert set(cols_groups_ids.keys()).issubset(PARAMS), "cols_groups_ids keys must be a subset of PARAMS"
        assert set(default_values.keys()).issubset(PARAMS), "default_values keys must be a subset of PARAMS"
        assert set(amount_groups_ids.keys()).issubset({"income", "expense"}), "amount_groups_ids keys must be income and/or expense"

        valid_mapper_keys = set(cols_groups_ids.keys())
        if amount_groups_ids:
            valid_mapper_keys.add("amount")
        assert set(function_mapper.keys()).issubset(valid_mapper_keys), "function_mapper keys must be a subset of extracted keys"
        
        flows = text.split('\n')
        data = []
        for flow in flows:
            match_ = re.search(pattern, flow)
            if match_:
                r = {
                    col_name: match_.group(id).strip() if id is not None else ""
                    for col_name, id in cols_groups_ids.items()
                }

                if amount_groups_ids:
                    income_value = ""
                    if "income" in amount_groups_ids:
                        income_group = amount_groups_ids["income"]
                        income_value = match_.group(income_group).strip() if income_group is not None else ""

                    expense_value = ""
                    if "expense" in amount_groups_ids:
                        expense_group = amount_groups_ids["expense"]
                        expense_value = match_.group(expense_group).strip() if expense_group is not None else ""

                    if income_value:
                        r["amount"] = income_value
                    elif expense_value:
                        if expense_value.startswith("-"):
                            r["amount"] = expense_value
                        elif expense_value.startswith("+"):
                            r["amount"] = f"-{expense_value[1:]}"
                        else:
                            r["amount"] = f"-{expense_value}"

                for col_name, value in default_values.items():
                    r[col_name] = value
                for col_name, func in function_mapper.items():
                    r[col_name] = func(r[col_name])
                data.append(Transaction(**r))
        return data

    def to_df(self) -> pd.DataFrame:
        """Build a DataFrame from the current parsed transactions.

        Args:
            None.

        Returns:
            A ``pandas.DataFrame`` with one row per transaction.

        Raises:
            ValueError: If no parsed transactions are available.
        """
        if not self.transactions:
            raise ValueError("Parser results are empty. Run parse() first.")

        df = pd.DataFrame([transaction.to_dict() for transaction in self.transactions])
        if df.empty:
            raise ValueError("Parser results are empty. Run parse() first.")

        return df

    def _extract_table_data(
        self,
        table: pd.DataFrame,
        cols_groups_ids: dict[str, str | int],
        default_values: dict[str, str] | None = None,
        function_mapper: dict[str, Callable[[str], str]] | None = None,
    ) -> List[Transaction]:
        """Extract transactions from tabular data such as CSV DataFrames.

        Args:
            table: DataFrame with one row per transaction.
            cols_groups_ids: Mapping between transaction field names and
                DataFrame column labels or integer indices.
            default_values: Fallback or fixed values injected into every
                extracted transaction.
            function_mapper: Mapping between transaction field names and
                transformation functions applied after extraction/defaults.

        Returns:
            A list of ``Transaction`` objects created from table rows.

        Raises:
            AssertionError: If mapping keys include unsupported transaction
                fields.
            KeyError: If a configured table column is missing.
            ValueError: Propagated when ``Transaction`` validation fails.
        """
        default_values = default_values or {}
        function_mapper = function_mapper or {}

        assert set(cols_groups_ids.keys()).issubset(PARAMS), "cols_groups_ids keys must be a subset of PARAMS"
        assert set(default_values.keys()).issubset(PARAMS), "default_values keys must be a subset of PARAMS"
        assert set(function_mapper.keys()).issubset(cols_groups_ids.keys()), "function_mapper keys must be a subset of cols_groups_ids keys"

        data = []
        for _, row in table.iterrows():
            extracted = {}
            for col_name, column_key in cols_groups_ids.items():
                value = row[column_key]
                if pd.isna(value):
                    extracted[col_name] = ""
                else:
                    extracted[col_name] = str(value).strip()

            for col_name, value in default_values.items():
                extracted[col_name] = value

            for col_name, func in function_mapper.items():
                extracted[col_name] = func(extracted[col_name])

            data.append(Transaction(**extracted))

        return data

