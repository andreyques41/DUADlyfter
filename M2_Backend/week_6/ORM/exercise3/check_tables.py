from exercise2.create_tables import create_tables_with_data
from sqlalchemy import create_engine, inspect

# Required tables for the database schema
REQUIRED_TABLES = ['users', 'brands', 'cars', 'locations', 'addresses']

def check_and_create_tables():
    """Checks if tables exist and creates them if missing."""
    DB_URI = 'postgresql://postgres:postgres@localhost:5432/lyfter'
    engine = create_engine(DB_URI, echo=False)  # Disabled SQL logs for cleaner output

    try:
        connection = engine.connect()
        print("✅ Database connection successful!")
        
        # Check existing tables in schema
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names(schema="backend_week6")
        
        print(f"Tables found in schema 'backend_week6': {existing_tables}")
        
        # Check which tables are missing
        missing_tables = [table for table in REQUIRED_TABLES 
                         if table not in existing_tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            print("Creating missing tables...")
            create_tables_with_data()
            print("✅ Table creation completed!")
        else:
            print("✅ All required tables already exist!")
        
        connection.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

