from exercise1.create_tables import create_tables
from exercise2.run_querys import run_querys
from exercise3.run_api import run_api
from exercise_extra1.backup_script import run_backup
from exercise_extra2.health_check import run_health_check
from exercise_extra3.data_seeder import run_seeding


def run_exercise(exercise_num):
    if exercise_num == 1:
        create_tables()

    elif exercise_num == 2:
        run_querys()

    elif exercise_num == 3:
        run_api()

    elif exercise_num == 4:
        run_backup()

    elif exercise_num == 5:
        run_health_check()

    elif exercise_num == 6:
        run_seeding()
    # Add more exercises as needed


if __name__ == "__main__":
    while True:
        print("\nAvailable exercises:")
        print("0 - Exit")
        print("1 - Create Tables (exercise1)")
        print("2 - Run Queries (exercise2)")
        print("3 - Run API Server (exercise3)")
        print("4 - Database Backup (exercise_extra1)")
        print("5 - Database Health Check (exercise_extra2)")
        print("6 - Data Seeding with Faker (exercise_extra3)")

        try:
            exercise = int(input("\nWhich exercise? (0-6): "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if exercise == 0:
            print("Exiting...")
            break
        elif 1 <= exercise <= 6:
            run_exercise(exercise)
        else:
            print("Invalid option. Please choose a valid exercise.")
