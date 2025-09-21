import random
from faker import Faker
from utilities.db import PgManager


def generate_users(db_manager, fake, count=200):
    """Generate fake users"""
    print(f"[INFO] Generating {count} fake users...")
    for i in range(count):
        try:
            query = """
            SET search_path TO lyfter_car_rental;
            INSERT INTO users (full_name, email, username, password, birthday, account_status_id)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
            db_manager.execute_query(
                query,
                fake.name(),
                fake.email(),
                fake.user_name(),
                fake.password(),
                fake.date_of_birth(minimum_age=18, maximum_age=80),
                random.randint(1, 2),
            )
        except Exception:
            pass  # Skip duplicates (email/username constraints)


def ensure_car_models(db_manager):
    """Add car models if they don't exist and return model IDs"""
    try:
        check_query = (
            "SET search_path TO lyfter_car_rental; SELECT COUNT(*) FROM model;"
        )
        result = db_manager.execute_query(check_query)
        if result[0][0] == 0:
            print("[INFO] No car models found, adding default models...")
            brands = [("Toyota", "Corolla"), ("Honda", "Civic"), ("Ford", "Focus")]
            for brand, model in brands:
                query = "SET search_path TO lyfter_car_rental; INSERT INTO model (brand, name) VALUES (%s, %s);"
                db_manager.execute_query(query, brand, model)
    except Exception:
        pass

    # Get model IDs
    model_query = "SET search_path TO lyfter_car_rental; SELECT id FROM model;"
    model_results = db_manager.execute_query(model_query)
    return [row[0] for row in model_results] if model_results else [1, 2, 3]


def generate_cars(db_manager, model_ids, count=100):
    """Generate fake cars"""
    print(f"[INFO] Generating {count} fake cars...")
    for i in range(count):
        try:
            query = """
            SET search_path TO lyfter_car_rental;
            INSERT INTO cars (model_id, year, state_id) VALUES (%s, %s, %s);
            """
            db_manager.execute_query(
                query,
                random.choice(model_ids),
                random.randint(2015, 2024),
                random.randint(1, 3),
            )
        except Exception:
            pass


def get_user_car_ids(db_manager):
    """Get available user and car IDs for rental creation"""
    user_query = "SET search_path TO lyfter_car_rental; SELECT id FROM users LIMIT 200;"
    car_query = "SET search_path TO lyfter_car_rental; SELECT id FROM cars LIMIT 100;"

    user_results = db_manager.execute_query(user_query)
    car_results = db_manager.execute_query(car_query)

    user_ids = [row[0] for row in user_results] if user_results else []
    car_ids = [row[0] for row in car_results] if car_results else []

    return user_ids, car_ids


def generate_rentals(db_manager, fake, user_ids, car_ids):
    """Generate fake rental records"""
    rental_count = random.randint(50, 150)
    print(f"[INFO] Generating {rental_count} fake rentals...")

    if user_ids and car_ids:
        for i in range(rental_count):
            try:
                query = """
                SET search_path TO lyfter_car_rental;
                INSERT INTO rentals (user_id, car_id, created_date, state_id)
                VALUES (%s, %s, %s, %s);
                """
                past_date = fake.date_between(start_date="-1y", end_date="today")
                db_manager.execute_query(
                    query,
                    random.choice(user_ids),
                    random.choice(car_ids),
                    past_date,
                    random.randint(1, 3),
                )
            except Exception:
                pass
    else:
        print("[ERROR] No users or cars available for rental creation")


def run_seeding():
    """Generate fake data using Faker: 200 users, 100 cars, 50-150 rentals"""
    print("[INFO] Starting data seeding process...")
    
    db_manager = PgManager(
        db_name="postgres", user="postgres", password="postgres", host="localhost"
    )
    
    if not db_manager or not db_manager.connection:
        print("[ERROR] Cannot connect to database")
        return False
        
    fake = Faker()

    # Generate users
    generate_users(db_manager, fake, 200)

    # Ensure models exist and get IDs
    model_ids = ensure_car_models(db_manager)

    # Generate cars
    generate_cars(db_manager, model_ids, 100)

    # Get user and car IDs for rentals
    user_ids, car_ids = get_user_car_ids(db_manager)

    # Generate rentals
    generate_rentals(db_manager, fake, user_ids, car_ids)

    print("[SUCCESS] Data seeding completed successfully!")

    # Close database connection
    db_manager.close_connection()

    return True


if __name__ == "__main__":
    run_seeding()
