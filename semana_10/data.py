import csv

# Writes the data into a file in csv format
# file_path: The path to the file where data will be written
# data: A list of dictionaries containing the data to be written
# headers: A list of column headers for the CSV file
def export_to_csv(file_path, data, headers):
    with open(file_path, 'w', encoding='utf-8') as file:
        # Create a CSV writer object with tab delimiter
        writer = csv.DictWriter(file, headers, delimiter='\t')
        writer.writeheader()  # Write the header row
        writer.writerows(data)  # Write the data rows

# Reads data from a CSV file
# file_path: The path to the file to be read
def import_from_csv(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Create a CSV reader object
            writer = csv.DictReader(file)
    except FileNotFoundError:
        # Handle the case where the file does not exist
        print(f"---The file {file_path} does not exist, please create one by selecting option 5 from the menu---")