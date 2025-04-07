import os
import csv
from typing import List, Dict, Union
from Clases.finance_movements import FinanceMonth, HEADERS

# Writes data to a CSV file with specified headers
def export_to_csv(file_path: str, data: List[Dict[str, str]], headers: List[str]):
    try:
        # Open the file and write data using DictWriter
        with open(file_path, 'w', encoding='utf-8') as file:
            writer = csv.DictWriter(file, headers)
            writer.writeheader()
            writer.writerows(data)
    except PermissionError as e:
        raise PermissionError(f"Permission denied when writing to file {file_path}.") from e
    except Exception as e:
        raise RuntimeError(f"Error exporting to CSV: {e}") from e

# Reads data from a CSV file and returns it as a list of dictionaries
def import_from_csv(file_path: str) -> List[Dict[str, str]]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data = [row for row in reader]
            return data
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File {file_path} not found.") from e
    except csv.Error as e:
        raise RuntimeError(f"Error reading CSV file {file_path}: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error while reading CSV file {file_path}: {e}") from e

# Exports a FinanceMonth object to a CSV file
def export_data(finance_month: FinanceMonth):
    if not isinstance(finance_month, FinanceMonth):
        raise TypeError("finance_month must be a FinanceMonth object.")
    try:
        file_path = f'../DataFiles/{finance_month.month}_{finance_month.year}.csv'
        export_to_csv(
            file_path,
            finance_month.convert_to_list_of_dict(),
            HEADERS
        )
    except AttributeError as e:
        raise AttributeError(f"Failed to access FinanceMonth attributes or methods. Details: {e}") from e
    except PermissionError as e:
        raise PermissionError(f"Permission denied when writing to file {file_path}.") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error while exporting data: {e}") from e

# Imports data from a CSV file and returns the updated FinanceMonth object
def import_data(month: str, year: str) -> FinanceMonth:
    if not month or not year:
        raise ValueError("Both month and year must be provided.")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_files_dir = os.path.join(base_dir, '..', 'DataFiles')
    file_name = os.path.join(data_files_dir, f'{month}_{year}.csv')
    
    try:
        list_of_dict = import_from_csv(file_name)
    except FileNotFoundError:
        # Create an empty CSV file with HEADERS
        os.makedirs(data_files_dir, exist_ok=True)
        export_to_csv(file_name, [], HEADERS)
        # Return an empty FinanceMonth object
        return FinanceMonth(month, year)
    except Exception as e:
        raise RuntimeError(f"Failed to import data from file {file_name}. Details: {e}") from e

    return create_finance_month_from_list(month, year, list_of_dict)

# Creates a FinanceMonth object and populates it with data
def create_finance_month_from_list(month: str, year: str, list_of_dict: List[Dict[str, str]]) -> FinanceMonth:
    try:
        # Return an empty FinanceMonth object if the list is empty
        if not list_of_dict:
            return FinanceMonth(month, year)
        finance_month = FinanceMonth(month, year)
        finance_month.add_movements_from_list(list_of_dict)
        return finance_month
    except AttributeError as e:
        raise AttributeError(f"Failed to populate FinanceMonth object. Details: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error while creating FinanceMonth object. Details: {e}") from e