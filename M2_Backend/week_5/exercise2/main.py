from utilities.db import PgManager
from car_repository import CarRepository
from user_repository import UserRepository
from rental_repository import RentalRepository

db_manager = PgManager(
    db_name="postgres", user="postgres", password="postgres", host="localhost"
)


def main():
    # Initialize repositories
    user_repo = UserRepository(db_manager)
    car_repo = CarRepository(db_manager)
    rental_repo = RentalRepository(db_manager)

    print("\n=== EXERCISE 2: CAR RENTAL SYSTEM OPERATIONS ===\n")

    # 1. Add a new user
    print("1. Adding a new user...")
    user_repo.insert_new_user(
        full_name="John Doe",
        email="john.doe@example.com",
        username="johndoe",
        password="secure123",
        birthday="1990-05-15",
        account_status_id=1,  # active
    )

    # 2. Add a new car
    print("\n2. Adding a new car...")
    car_repo.insert_new_car(
        model_id=1, year=2023, state_id=1  # Toyota Corolla  # available
    )

    # 3. Change user status
    print("\n3. Changing user status...")
    user_repo.update_user_status(user_id=1, account_status_id=2)  # suspended

    # 4. Change car status
    print("\n4. Changing car status...")
    car_repo.update_state(car_id=1, state_id=3)  # rented

    # 5. Create a new rental
    print("\n5. Creating a new rental...")
    rental_repo.insert_new_rental(user_id=1, car_id=1)

    # 6. Complete a rental (return car)
    print("\n6. Completing a rental...")
    rental_repo.complete_rental(rental_id=1, car_repository=car_repo)

    # 7. Disable a car from rental
    print("\n7. Disabling a car from rental...")
    car_repo.disable_car(car_id=2)

    # 8. Get all rented cars and available cars
    print("\n8. Getting rented and available cars...")

    print("\n8a. All rented cars:")
    rented_cars = car_repo.get_rented_cars()
    if rented_cars:
        for car in rented_cars:
            print(
                f"   Car ID: {car['id']}, Model ID: {car['model_id']}, Year: {car['year']}"
            )
    else:
        print("   No cars currently rented")

    print("\n8b. All available cars:")
    available_cars = car_repo.get_available_cars()
    if available_cars:
        for car in available_cars:
            print(
                f"   Car ID: {car['id']}, Model ID: {car['model_id']}, Year: {car['year']}"
            )
    else:
        print("   No cars currently available")

    # Close database connection
    db_manager.close_connection()


if __name__ == "__main__":
    main()
