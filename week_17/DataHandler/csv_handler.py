import os
import csv
from typing import List, Dict
from Clases.finance_movements import FinanceMonth, Movement, HEADERS

DEFAULT_FILE_NAME = "finance_data.csv"

# Writes data to a CSV file with specified headers
def export_to_csv(data: List[Dict[str, str]], headers: List[str]):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DEFAULT_FILE_NAME)
    try:
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, headers)
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        raise RuntimeError(f"Error exporting to CSV: {e}") from e

# Reads data from a CSV file and returns it as a list of dictionaries
def import_from_csv() -> List[Dict[str, str]]:
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DEFAULT_FILE_NAME)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return [row for row in reader]
    except FileNotFoundError:
        return []  # Return an empty list if the file does not exist
    except Exception as e:
        raise RuntimeError(f"Error reading CSV file: {e}") from e

# Exports a FinanceMonth object to the default CSV file
def export_data(finance_month: FinanceMonth):
    if not isinstance(finance_month, FinanceMonth):
        raise TypeError("finance_month must be a FinanceMonth object.")
    export_to_csv(finance_month.convert_to_list_of_dict(), HEADERS)

# Imports data from the default CSV file and returns a FinanceMonth object
def import_data() -> FinanceMonth:
    list_of_dict = import_from_csv()
    finance_month = FinanceMonth()
    if list_of_dict:
        finance_month.add_movements_from_list(list_of_dict)
    return finance_month