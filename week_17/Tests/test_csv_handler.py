import os
import csv
import pytest
from unittest.mock import MagicMock, patch
from Actions.finance_movements import FinanceMonth

# filepath: DUADlyfter/week_17/DataHandler/test_csv_handler.py
from DataHandler.csv_handler import (
    export_to_csv,
    import_from_csv,
    export_data,
    import_data,
    create_finance_month,
)

@pytest.fixture
def sample_data():
    return [
        {"name": "Salary", "category": "Job", "movement_type": "Income", "amount": "5000"},
        {"name": "Rent", "category": "Housing", "movement_type": "Expense", "amount": "1500"},
    ]

@pytest.fixture
def temp_csv_file(tmp_path, sample_data):
    file_path = tmp_path / "test.csv"
    with open(file_path, "w", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=sample_data[0].keys())
        writer.writeheader()
        writer.writerows(sample_data)
    return file_path

def test_export_to_csv(tmp_path, sample_data):
    file_path = tmp_path / "output.csv"
    headers = sample_data[0].keys()
    export_to_csv(str(file_path), sample_data, headers)
    assert os.path.exists(file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert rows == sample_data

def test_import_from_csv(temp_csv_file, sample_data):
    data = import_from_csv(str(temp_csv_file))
    assert data == sample_data

## Hasta aqui entiendo, WIP estudiar lo siguiente --->>>

# @patch("DataHandler.csv_handler.export_to_csv")
# def test_export_data(mock_export_to_csv):
#     finance_month = MagicMock(spec=FinanceMonth)
#     finance_month.month = "January"
#     finance_month.year = "2025"
#     finance_month.convert_to_list_of_dict.return_value = [
#         {"name": "Salary", "category": "Job", "movement_type": "Income", "amount": "5000"}
#     ]
#     export_data(finance_month)
#     mock_export_to_csv.assert_called_once()

# @patch("DataHandler.csv_handler.import_from_csv")
# @patch("DataHandler.csv_handler.create_finance_month")
# def test_import_data(mock_create_finance_month, mock_import_from_csv, sample_data):
#     mock_import_from_csv.return_value = sample_data
#     mock_create_finance_month.return_value = MagicMock(spec=FinanceMonth)
#     finance_month = import_data("January", "2025")
#     mock_import_from_csv.assert_called_once()
#     mock_create_finance_month.assert_called_once_with("January", "2025", sample_data)
#     assert isinstance(finance_month, FinanceMonth)

# def test_create_finance_month(sample_data):
#     finance_month = create_finance_month("January", "2025", sample_data)
#     assert isinstance(finance_month, FinanceMonth)
#     assert finance_month.month == "January"
#     assert finance_month.year == "2025"
#     finance_month.add_movements_from_list.assert_called_once_with(sample_data)