from sqlalchemy import create_engine, MetaData
from exercise4.car_repository import CarRepository
from exercise4.user_repository import UserRepository
from exercise4.address_repository import AddressRepository

def run_queries():
    """Comprehensive examples of all repository methods"""
    DB_URI = 'postgresql://postgres:postgres@localhost:5432/lyfter'
    engine = create_engine(DB_URI, echo=False)  # Disabled SQL logs for cleaner output
    metadata_obj = MetaData(schema="backend_week6")

    # Reflect existing tables
    metadata_obj.reflect(bind=engine)
    
    # Create all repositories
    car_repo = CarRepository(metadata_obj)
    user_repo = UserRepository(metadata_obj)
    address_repo = AddressRepository(metadata_obj)
    
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful!")
            
            print("\n" + "="*60)
            print("USER REPOSITORY EXAMPLES")
            print("="*60)
            
            # USER REPOSITORY EXAMPLES
            print("\n1. Getting all users:")
            users = user_repo.get_all(conn)
            for user in users[:3]:  # Show first 3 users
                print(f"   ID: {user.id}, Username: {user.username}, Email: {user.email}")
            
            print("\n2. Getting user by ID (first user):")
            if users:
                user = user_repo.get_by_id(conn, users[0].id)
                if user:
                    print(f"   Found: {user.full_name} ({user.username})")
            
            print("\n3. Getting user by username:")
            user = user_repo.get_by_username(conn, "johndoe")
            if user:
                print(f"   Found: {user.full_name} - {user.email}")
            
            print("\n4. Creating a new user:")
            new_user_created = user_repo.create_user(
                conn, 
                full_name="Test User", 
                email="testuser@example.com", 
                username="testuser123",
                phone="555-0123"
            )
            
            print("\n5. Updating user information:")
            if new_user_created:
                test_user = user_repo.get_by_username(conn, "testuser123")
                if test_user:
                    user_repo.update_user(conn, test_user.id, phone="555-9999")
            
            print("\n" + "="*60)
            print("ADDRESS REPOSITORY EXAMPLES") 
            print("="*60)
            
            # ADDRESS REPOSITORY EXAMPLES
            print("\n1. Getting all addresses:")
            addresses = address_repo.get_all(conn)
            for addr in addresses[:3]:  # Show first 3 addresses
                print(f"   ID: {addr.id}, Street: {addr.street}")
                print(f"      User: {addr.username}, Location: {addr.city}, {addr.country}")
            
            print("\n2. Getting address by ID:")
            if addresses:
                address = address_repo.get_by_id(conn, addresses[0].id)
                if address:
                    print(f"   Found: {address.street}, {address.city}")
            
            print("\n3. Getting addresses by user ID:")
            if users:
                user_addresses = address_repo.get_by_user_id(conn, users[0].id)
                for addr in user_addresses:
                    print(f"   {addr.street}, {addr.city}, {addr.country}")
            
            print("\n4. Creating a new address:")
            if users and new_user_created:
                test_user = user_repo.get_by_username(conn, "testuser123")
                if test_user:
                    # Assuming location ID 1 exists
                    address_created = address_repo.create_address(
                        conn,
                        street="123 Test Street",
                        postal_code="12345",
                        location_id=1,
                        user_id=test_user.id
                    )
            
            print("\n5. Updating address information:")
            if 'address_created' in locals() and address_created:
                test_user = user_repo.get_by_username(conn, "testuser123")
                if test_user:
                    user_addresses = address_repo.get_by_user_id(conn, test_user.id)
                    if user_addresses:
                        address_repo.update_address(
                            conn, 
                            user_addresses[0].id, 
                            postal_code="54321"
                        )
            
            print("\n" + "="*60)
            print("CAR REPOSITORY EXAMPLES")
            print("="*60)
            
            # CAR REPOSITORY EXAMPLES
            print("\n1. Getting all cars:")
            cars = car_repo.get_all(conn)
            for car in cars[:3]:  # Show first 3 cars
                print(f"   ID: {car.id}, Model: {car.model}, Year: {car.year}")
                print(f"      Brand: {car.brand}, Owner ID: {car.user_id}")
            
            print("\n2. Getting car by ID:")
            if cars:
                car = car_repo.get_by_id(conn, cars[0].id)
                if car:
                    print(f"   Found: {car.brand} {car.model} ({car.year})")
            
            print("\n3. Creating a new car:")
            # Assuming brand ID 1 exists
            car_created = car_repo.create_car(
                conn,
                brand_id=1,
                model="Test Model",
                year=2023,
                color="Blue",
                license_plate="TEST123"
            )
            
            print("\n4. Assigning user to car:")
            if car_created and users:
                # Get the newly created car
                new_cars = car_repo.get_all(conn)
                test_car = None
                for car in new_cars:
                    if car.model == "Test Model":
                        test_car = car
                        break
                
                if test_car:
                    car_repo.assign_user_to_car(conn, test_car.id, users[0].id)
            
            print("\n5. Updating car information:")
            if 'test_car' in locals() and test_car:
                car_repo.update_car(conn, test_car.id, color="Red", year=2024)
            
            print("\n" + "="*60)
            print("CLEANUP - DELETING TEST RECORDS")
            print("="*60)
            
            # Clean up test data
            print("\n1. Deleting test car:")
            if 'test_car' in locals() and test_car:
                car_repo.delete_car(conn, test_car.id)
            
            print("\n2. Deleting test address:")
            if 'address_created' in locals() and address_created:
                test_user = user_repo.get_by_username(conn, "testuser123")
                if test_user:
                    user_addresses = address_repo.get_by_user_id(conn, test_user.id)
                    for addr in user_addresses:
                        address_repo.delete_address(conn, addr.id)
            
            print("\n3. Deleting test user:")
            if new_user_created:
                test_user = user_repo.get_by_username(conn, "testuser123")
                if test_user:
                    user_repo.delete_user(conn, test_user.id)
            
            # Commit all changes
            conn.commit()
            print("\n[INFO] All repository method examples completed successfully!")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    run_queries()

