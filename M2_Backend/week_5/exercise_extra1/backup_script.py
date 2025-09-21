import csv
import os
from datetime import datetime
from utilities.db import PgManager


def create_backup_folder(folder_name="db_backups"):
    """Create backup folder if it doesn't exist"""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name


def get_table_data_with_headers(db_manager, table_name):
    """Get all data and column names from a specific table"""
    query = f"SELECT * FROM {table_name} ORDER BY id;"
    # Use a raw connection to get column names
    conn = db_manager.get_connection()
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]
    return headers, rows


def save_table_to_csv_with_headers(headers, data, table_name, backup_folder, timestamp):
    """Save table data with headers to CSV file"""
    filename = f"{table_name}_{timestamp}.csv"
    filepath = os.path.join(backup_folder, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(data)

    print(f"[SUCCESS] Backed up {table_name} to {filename}")


def backup_single_table(db_manager, table_name, backup_folder, timestamp):
    """Backup a single table to CSV with headers"""
    try:
        headers, results = get_table_data_with_headers(db_manager, table_name)
        if results:
            save_table_to_csv_with_headers(
                headers, results, table_name, backup_folder, timestamp
            )
        else:
            print(f"[INFO] Table {table_name} is empty, skipping backup")
    except Exception as error:
        print(f"[ERROR] Failed to backup {table_name}: {error}")


def run_backup():
    """Backup database tables to CSV files with timestamps"""
    print("[INFO] Starting database backup process...")
    
    db_manager = PgManager(
        db_name="postgres", user="postgres", password="postgres", host="localhost"
    )

    if not db_manager or not db_manager.connection:
        print("[ERROR] Cannot connect to database")
        return False

    tables = [
        "users",
        "cars", 
        "rentals",
        "account_status",
        "model",
        "car_state",
        "rent_state",
    ]

    backup_folder = create_backup_folder()
    timestamp = datetime.now().strftime("%Y-%m-%d")
    print(f"[INFO] Backup folder created: {backup_folder}")

    for table in tables:
        backup_single_table(db_manager, table, backup_folder, timestamp)

    print("[SUCCESS] Backup completed successfully")

    # Close database connection
    db_manager.close_connection()
    return True


if __name__ == "__main__":
    run_backup()
