from sqlalchemy import create_engine, MetaData
from exercise4.car_repository import CarRepository
from exercise4.user_repository import UserRepository
from exercise4.address_repository import AddressRepository

def run_extra_queries():
    """Demo: Specialized query methods."""
    DB_URI = 'postgresql://postgres:postgres@localhost:5432/lyfter'
    engine = create_engine(DB_URI, echo=False)
    metadata_obj = MetaData(schema="backend_week6")
    metadata_obj.reflect(bind=engine)
    car_repo = CarRepository(metadata_obj)
    user_repo = UserRepository(metadata_obj)
    address_repo = AddressRepository(metadata_obj)
    
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful!")
            
            print("\n" + "="*60)
            print("SPECIALIZED QUERY METHODS - NEW FEATURES")
            print("="*60)
            
            # NEW SPECIALIZED QUERIES
            print("\n1. Cars without associated users:")
            cars_without_users = car_repo.get_cars_without_users(conn)
            if cars_without_users:
                print(f"   Found {len(cars_without_users)} cars without users:")
                for car in cars_without_users:
                    print(f"   • ID: {car.id}, {car.brand} {car.model} ({car.year})")
                    print(f"     License: {car.license_plate}, Color: {car.color}")
            else:
                print("   ❌ No cars without users found")
            
            print("\n2. Users with more than 1 car:")
            users_multiple_cars = user_repo.get_users_with_multiple_cars(conn)
            if users_multiple_cars:
                print(f"   Found {len(users_multiple_cars)} users with multiple cars:")
                for user in users_multiple_cars:
                    print(f"   • ID: {user.id}, {user.full_name} ({user.username})")
                    print(f"     Email: {user.email}, Total Cars: {user.car_count}")
            else:
                print("   ❌ No users with multiple cars found")
            
            print("\n3. Addresses containing 'Calle' in street name:")
            addresses_with_calle = address_repo.get_addresses_containing_substring(conn, "Calle")
            if addresses_with_calle:
                print(f"   Found {len(addresses_with_calle)} addresses containing 'Calle':")
                for addr in addresses_with_calle:
                    print(f"   • ID: {addr.id}, Street: {addr.street}")
                    print(f"     User: {addr.user_name}, Location: {addr.city}, {addr.country}")
            else:
                print("   ❌ No addresses containing 'Calle' found")
            
            print("\n4. Addresses containing 'Main' in street name:")
            addresses_with_main = address_repo.get_addresses_containing_substring(conn, "Main")
            if addresses_with_main:
                print(f"   Found {len(addresses_with_main)} addresses containing 'Main':")
                for addr in addresses_with_main:
                    print(f"   • ID: {addr.id}, Street: {addr.street}")
                    print(f"     User: {addr.user_name}, Location: {addr.city}, {addr.country}")
            else:
                print("   ❌ No addresses containing 'Main' found")
            
            print("\n[INFO] All specialized query examples completed successfully!")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    run_extra_queries()

