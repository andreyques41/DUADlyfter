from sqlalchemy import MetaData, create_engine, insert


def insert_data(users_table, brands_table, cars_table, locations_table, addresses_table):
    """Inserts sample data into all normalized tables."""
    print("\n=== INSERTING SAMPLE DATA ===\n")

    DB_URI = 'postgresql://postgres:postgres@localhost:5432/lyfter'
    engine = create_engine(DB_URI, echo=False)  # Disabled SQL logs for cleaner output

    try:
        with engine.connect() as conn:
            # Insert reference data first
            print("Inserting brands...")
            brands_stmt = insert(brands_table).values([
                {"name": "Toyota", "country_origin": "Japan"},
                {"name": "Ford", "country_origin": "USA"},
                {"name": "BMW", "country_origin": "Germany"},
                {"name": "Honda", "country_origin": "Japan"},
                {"name": "Chevrolet", "country_origin": "USA"}
            ])
            conn.execute(brands_stmt)
            
            print("Inserting locations...")
            locations_stmt = insert(locations_table).values([
                {"city": "New York", "state": "NY", "country": "USA", "postal_code_pattern": "10001"},
                {"city": "Los Angeles", "state": "CA", "country": "USA", "postal_code_pattern": "90210"},
                {"city": "Miami", "state": "FL", "country": "USA", "postal_code_pattern": "33101"},
                {"city": "Chicago", "state": "IL", "country": "USA", "postal_code_pattern": "60601"},
                {"city": "Houston", "state": "TX", "country": "USA", "postal_code_pattern": "77001"}
            ])
            conn.execute(locations_stmt)
            
            # Insert main entities
            print("Inserting users...")
            users_stmt = insert(users_table).values([
                {"full_name": "John Doe", "email": "john.doe@email.com", "username": "johndoe", "phone": "+1-555-0101"},
                {"full_name": "Jane Smith", "email": "jane.smith@email.com", "username": "janesmith", "phone": "+1-555-0102"},
                {"full_name": "Bob Johnson", "email": "bob.johnson@email.com", "username": "bobjohnson", "phone": "+1-555-0103"},
                {"full_name": "Alice Brown", "email": "alice.brown@email.com", "username": "alicebrown", "phone": "+1-555-0104"},
                {"full_name": "Charlie Wilson", "email": "charlie.wilson@email.com", "username": "charliewilson", "phone": "+1-555-0105"}
            ])
            conn.execute(users_stmt)
            
            # Insert related data
            print("Inserting cars...")
            cars_stmt = insert(cars_table).values([
                {"brand_id": 1, "model": "Camry", "year": 2022, "color": "Blue", "license_plate": "ABC-123", "user_id": 1},
                {"brand_id": 2, "model": "Mustang", "year": 2021, "color": "Red", "license_plate": "DEF-456", "user_id": 2},
                {"brand_id": 3, "model": "X5", "year": 2023, "color": "Black", "license_plate": "GHI-789", "user_id": 3},
                {"brand_id": 4, "model": "Civic", "year": 2020, "color": "White", "license_plate": "JKL-012", "user_id": 4},
                {"brand_id": 5, "model": "Malibu", "year": 2022, "color": "Silver", "license_plate": "MNO-345", "user_id": 5},
                {"brand_id": 1, "model": "Corolla", "year": 2021, "color": "Gray", "license_plate": "PQR-678", "user_id": 1},
                {"brand_id": 2, "model": "F-150", "year": 2023, "color": "Blue", "license_plate": "STU-901", "user_id": None}
            ])
            conn.execute(cars_stmt)
            
            print("Inserting addresses...")
            addresses_stmt = insert(addresses_table).values([
                {"street": "123 Main St", "postal_code": "10001", "location_id": 1, "user_id": 1},
                {"street": "456 Oak Ave", "postal_code": "90210", "location_id": 2, "user_id": 2},
                {"street": "789 Pine Rd", "postal_code": "33101", "location_id": 3, "user_id": 3},
                {"street": "321 Elm St", "postal_code": "60601", "location_id": 4, "user_id": 4},
                {"street": "654 Maple Dr", "postal_code": "77001", "location_id": 5, "user_id": 5},
                {"street": "987 Broadway", "postal_code": "10002", "location_id": 1, "user_id": 1}
            ])
            conn.execute(addresses_stmt)
            
            # Commit all transactions
            conn.commit()
            print("\n✅ All data inserted successfully!")
            print("Summary: 5 brands, 5 locations, 5 users, 7 cars, 6 addresses")
        
    except Exception as e:
        print(f"❌ Error inserting data: {e}")

