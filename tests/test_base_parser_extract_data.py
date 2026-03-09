from bankparser.parser.base_parser import Parser


class DummyParser(Parser):
    def parse(self) -> None:
        return self


def test_extract_data_with_income_and_expense_columns() -> None:
    parser = DummyParser("dummy.txt")
    raw_text = "\n".join(
        [
            "01/01/2024|Salary|1000.00|",
            "02/01/2024|Rent||250.00",
        ]
    )

    transactions = parser._extract_data(
        text=raw_text,
        pattern=r"(\d{2}/\d{2}/\d{4})\|(.+?)\|([^|]*)\|([^|]*)",
        cols_groups_ids={"date": 1, "description": 2},
        default_values={"account": "CSV Account", "currency": "COP"},
        amount_groups_ids={"income": 3, "expense": 4},
    )

    assert len(transactions) == 2
    assert str(transactions[0].amount) == "1000.00"
    assert str(transactions[1].amount) == "-250.00"


def test_extract_data_allows_amount_mapper_for_split_columns() -> None:
    parser = DummyParser("dummy.txt")
    raw_text = "01/01/2024|Transfer||10.00"

    transactions = parser._extract_data(
        text=raw_text,
        pattern=r"(\d{2}/\d{2}/\d{4})\|(.+?)\|([^|]*)\|([^|]*)",
        cols_groups_ids={"date": 1, "description": 2},
        default_values={"account": "CSV Account", "currency": "COP"},
        amount_groups_ids={"income": 3, "expense": 4},
        function_mapper={"amount": lambda value: value.replace("-", "")},
    )

    assert len(transactions) == 1
    assert str(transactions[0].amount) == "10.00"
