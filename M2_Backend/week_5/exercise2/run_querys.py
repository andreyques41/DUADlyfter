from utilities.db import PgManager
from exercise2.car_repository import CarRepository
from exercise2.user_repository import UserRepository
from exercise2.rental_repository import RentalRepository

db_manager = PgManager(
    db_name="postgres", user="postgres", password="postgres", host="localhost"
)


def run_querys():
    if not db_manager or not db_manager.connection:
        print("[ERROR] Cannot connect to database")
        return False
        
    print("[INFO] Starting car rental system operations...")
    
    # Initialize repositories
    user_repo = UserRepository(db_manager)
    car_repo = CarRepository(db_manager)
    rental_repo = RentalRepository(db_manager)

    print("\n=== EXERCISE 2: CAR RENTAL SYSTEM OPERATIONS ===\n")

    # 1. Add a new user
    print("[INFO] 1. Adding a new user...")
    user_repo.insert_new_user(
        full_name="John Doe",
        email="john.doe@example.com",
        username="johndoe",
        password="secure123",
        birthday="1990-05-15",
        account_status_id=1,  # active
    )

    # 2. Add a new car
    print("[INFO] 2. Adding a new car...")
    car_repo.insert_new_car(
        model_id=1, year=2023, state_id=1  # Toyota Corolla  # available
    )

    # 3. Change user status
    print("[INFO] 3. Changing user status...")
    user_repo.update_user_status(user_id=1, account_status_id=2)  # suspended

    # 4. Change car status
    print("[INFO] 4. Changing car status...")
    car_repo.update_state(car_id=1, state_id=3)  # rented

    # 5. Create a new rental
    print("[INFO] 5. Creating a new rental...")
    rental_repo.insert_new_rental(user_id=1, car_id=1)

    # 6. Complete a rental (return car)
    print("[INFO] 6. Completing a rental...")
    rental_repo.complete_rental(rental_id=1, car_repository=car_repo)

    # 7. Disable a car from rental
    print("[INFO] 7. Disabling a car from rental...")
    car_repo.disable_car(car_id=2)

    # 8. Get all rented cars and available cars
    print("[INFO] 8. Getting rented and available cars...")

    print("[INFO] 8a. All rented cars:")
    rented_cars = car_repo.get_rented_cars()
    if rented_cars:
        print(rented_cars)
    else:
        print("   [INFO] No cars currently rented")

    print("[INFO] 8b. All available cars:")
    available_cars = car_repo.get_available_cars()
    if available_cars:
        print(available_cars)
    else:
        print("   [INFO] No cars currently available")

    # Close database connection
    db_manager.close_connection()
    print("[SUCCESS] Car rental operations completed successfully")
    return True
