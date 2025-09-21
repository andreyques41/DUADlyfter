from utilities.db import PgManager


def connect_to_database():
    """Connect to the database and return db_manager"""
    try:
        return PgManager(
            db_name="postgres", user="postgres", password="postgres", host="localhost"
        )
    except Exception:
        return None


def check_table_exists(db_manager, table_name):
    """Check if a specific table exists in the database"""
    query = """
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'lyfter_car_rental' AND table_name = %s
    );
    """
    result = db_manager.execute_query(query, table_name)
    return result and result[0][0]


def check_required_tables(db_manager):
    """Check if all required tables exist"""
    required_tables = ["users", "cars", "rentals"]
    for table in required_tables:
        if not check_table_exists(db_manager, table):
            return False
    return True


def count_available_cars(db_manager):
    """Count available cars (state_id = 1)"""
    query = """
    SET search_path TO lyfter_car_rental;
    SELECT COUNT(*) FROM cars WHERE state_id = 1;
    """
    result = db_manager.execute_query(query)
    return result[0][0] if result else 0


def run_health_check():
    """Check database connection, tables, and available cars"""
    print("[INFO] Starting database health check...")
    
    # Connect to database
    db_manager = connect_to_database()
    if not db_manager:
        print("[ERROR] Cannot connect to database")
        return False

    # Check required tables exist
    if not check_required_tables(db_manager):
        print("[ERROR] Required tables are missing")
        db_manager.close_connection()
        return False

    # Check available cars
    available_cars = count_available_cars(db_manager)

    # Close database connection
    db_manager.close_connection()

    if available_cars > 0:
        print(f"[SUCCESS] Database operational normally. Available cars: {available_cars}")
        return True
    else:
        print("[ERROR] No cars available for rental")
        return False


if __name__ == "__main__":
    run_health_check()
