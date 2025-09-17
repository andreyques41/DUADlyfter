import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))


def run_exercise(exercise_num):
    if exercise_num == 1:
        from exercise1.main import main

        main()
    elif exercise_num == 2:
        from exercise2.main import main

        main()
    # Add more exercises as needed


if __name__ == "__main__":
    exercise = int(input("Which exercise? (1, 2, 3...): "))
    run_exercise(exercise)
