import os
import csv
from actions import Student
from actions import HEADERS

# Helper function to construct file paths
def get_file_path(file_name):
    return os.path.join(os.path.dirname(__file__), file_name)

# Exports a list of students to a CSV file
def export_students(all_students):
    if all_students:
        file_name = input("Enter the CSV file name to export (without extension): \n").strip()
        if not file_name or not file_name.isalnum():
            print("---Invalid file name. Export canceled.---")
            return
        export_to_csv(f'{file_name}.csv', all_students, HEADERS)
    else:
        print('-----No students available to export-----')

# Imports student data from a CSV file and returns the updated state
def import_students(is_data_loaded):
    print(f'-----Warning: Ensure the CSV file has headers: {HEADERS}-----')
    file_name = input("Enter the CSV file name to import (without extension): \n").strip()
    if not file_name or not file_name.isalnum():
        print("---Invalid file name. Import canceled.---")
        return is_data_loaded, []
    is_data_loaded, imported_students = import_from_csv(f'{file_name}.csv')
    return is_data_loaded, imported_students

# Writes data to a CSV file with specified headers
def export_to_csv(file_name, data, headers):
    file_path = get_file_path(file_name)
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            # Create a CSV writer object
            writer = csv.DictWriter(file, headers)
            writer.writeheader()  # Write headers

            for student in data:
                writer.writerow(student.to_dict())  # Write rows
    except Exception as e:
        print(f"---Error exporting to CSV: {e}---")

# Reads data from a CSV file and returns it as a list of dictionaries
def import_from_csv(file_name):
    file_path = get_file_path(file_name)
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return False, []    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read rows into a list of dictionaries
            reader = csv.DictReader(file)
            data = [Student().from_dict(row) for row in reader]
            return True, data
    except csv.Error as e:
        # Handle CSV parsing errors
        print(f"---Error reading CSV file: {e}---")
        return False, []
