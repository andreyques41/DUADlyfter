from exercise2.users import create_users
from exercise2.cars import create_cars
from exercise2.addresses import create_addresses
from exercise2.insert_data import insert_data
from sqlalchemy import MetaData, create_engine


def create_tables_with_data(insert_sample_data=True):
    """
    Creates normalized database tables and optionally inserts sample data.
    
    Args:
        insert_sample_data (bool): Whether to insert sample data after creating tables
    """
    print("\n=== EXERCISE 1: CREATING NORMALIZED TABLES ===\n")

    # Create metadata and engine
    metadata_obj = MetaData(schema="backend_week6")
    DB_URI = 'postgresql://postgres:postgres@localhost:5432/lyfter'
    engine = create_engine(DB_URI, echo=False)  # Disabled SQL logs for cleaner output

    try:
        connection = engine.connect()
        print("✅ Database connection successful!")
        
        # Create table objects
        print("Creating tables...")
        users_table = create_users(metadata_obj)
        brands_table, cars_table = create_cars(metadata_obj)
        locations_table, addresses_table = create_addresses(metadata_obj)
        
        # Execute table creation in database
        metadata_obj.create_all(engine)
        
        print("\n🎉 Tables created successfully!")
        print(f"- Users, Brands, Cars, Locations, Addresses")
        
        # Insert sample data if requested
        if insert_sample_data:
            print("\n=== INSERTING SAMPLE DATA ===")
            insert_data(users_table, brands_table, cars_table, locations_table, addresses_table)
        
        connection.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

