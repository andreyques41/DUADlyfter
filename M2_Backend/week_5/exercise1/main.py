from utilities.db import PgManager
from exercise1.users import create_users
from exercise1.cars import create_cars
from exercise1.rentals import create_rentals

db_manager = PgManager(
    db_name="postgres", user="postgres", password="postgres", host="localhost"
)


def main():
    print("\n=== EXERCISE 1: CAR RENTAL TABLES CREATION ===\n")

    create_users(db_manager)
    create_cars(db_manager)
    create_rentals(db_manager)
    db_manager.close_connection()
