import csv

# Writes data to a CSV file with specified headers
def export_to_csv(file_path, data, headers):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            # Create a CSV writer object
            writer = csv.DictWriter(file, headers)
            writer.writeheader()  # Write headers
            writer.writerows(data)  # Write rows
    except Exception as e:
        print(f"---Error exporting to CSV: {e}---")

# Reads data from a CSV file and returns it as a list of dictionaries
def import_from_csv(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read rows into a list of dictionaries
            reader = csv.DictReader(file)
            data = [row for row in reader]
            return True, data
    except FileNotFoundError:
        # Handle missing file
        print(f"---File {file_path} not found---")
        return False, []
    except csv.Error as e:
        # Handle CSV parsing errors
        print(f"---Error reading CSV file: {e}---")
        return False, []

# Exports a list of students to a CSV file
def export_students(all_students):
    if all_students:
        file_name = input("Enter the CSV file name to export (without extension): \n").strip()
        if not file_name:
            print("---Invalid file name. Export canceled.---")
            return
        export_to_csv(f'./{file_name}.csv', all_students, all_students[0].keys())
    else:
        print('-----No students available to export-----')

# Imports student data from a CSV file and returns the updated state
def import_students(is_data_loaded):
    print('-----Warning: Ensure the CSV file has headers: [Name, Section, Spanish score, English score, Socials score, Science score, Average score]-----')
    file_name = input("Enter the CSV file name to import (without extension): \n").strip()
    if not file_name:
        print("---Invalid file name. Import canceled.---")
        return is_data_loaded, []
    is_data_loaded, imported_students = import_from_csv(f'./{file_name}.csv')
    return is_data_loaded, imported_students