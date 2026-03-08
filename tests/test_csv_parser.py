from datetime import date

from bankparser.parser.csv_parser import CSVParser


def test_csv_parser_parses_headered_file(tmp_path) -> None:
    csv_file = tmp_path / "transactions.csv"
    csv_file.write_text(
        "date,description,amount,balance\n"
        "01/02/2024,Salary,1200.00,2200.00\n"
        "02/02/2024,Coffee,-5.50,2194.50\n"
    )

    parser = CSVParser(
        file_path=str(csv_file),
        cols_groups_ids={
            "date": "date",
            "description": "description",
            "amount": "amount",
            "balance": "balance",
        },
        default_values={"account": "CSV Account", "currency": "COP"},
    ).parse()

    assert len(parser.transactions) == 2
    assert parser.transactions[0].date == date(2024, 2, 1)
    assert parser.transactions[0].description == "Salary"
    assert str(parser.transactions[0].amount) == "1200.00"
    assert str(parser.transactions[0].balance) == "2200.00"


def test_csv_parser_parses_file_without_headers(tmp_path) -> None:
    csv_file = tmp_path / "transactions_no_headers.csv"
    csv_file.write_text("01/02/2024,Bonus,100.00\n")

    parser = CSVParser(
        file_path=str(csv_file),
        has_headers=False,
        cols_groups_ids={"date": 0, "description": 1, "amount": 2},
        default_values={"account": "CSV Account", "currency": "COP"},
    ).parse()

    assert len(parser.transactions) == 1
    assert parser.transactions[0].description == "Bonus"
    assert str(parser.transactions[0].amount) == "100.00"
