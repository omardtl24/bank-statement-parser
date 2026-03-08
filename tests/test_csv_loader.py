import pandas as pd

from bankparser.loader.csv_loader import CSVLoader


def test_load_csv_with_headers(tmp_path) -> None:
    csv_file = tmp_path / "with_headers.csv"
    csv_file.write_text("date,description,amount\n01/02/2024,Payroll,1200.00\n")

    df = CSVLoader.load(str(csv_file), has_headers=True)

    assert list(df.columns) == ["date", "description", "amount"]
    assert df.shape == (1, 3)
    assert df.iloc[0]["description"] == "Payroll"


def test_load_csv_without_headers(tmp_path) -> None:
    csv_file = tmp_path / "without_headers.csv"
    csv_file.write_text("01/02/2024,Store,-12.50\n")

    df = CSVLoader.load(str(csv_file), has_headers=False)

    assert list(df.columns) == [0, 1, 2]
    assert df.shape == (1, 3)
    assert df.iloc[0][1] == "Store"
