from exercise1.create_tables import create_tables
from exercise2.run_querys import run_querys
from exercise3.run_api import run_api


def run_exercise(exercise_num):
    if exercise_num == 1:
        create_tables()

    elif exercise_num == 2:
        run_querys()

    elif exercise_num == 3:
        run_api()
    # Add more exercises as needed


if __name__ == "__main__":
    exercise = int(input("Which exercise? (1, 2, 3...): "))
    run_exercise(exercise)
