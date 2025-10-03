from exercise2.create_tables import create_tables_with_data
from exercise3.check_tables import check_and_create_tables
from exercise4.queries import run_queries
from exercise_extra1.extra_queries import run_extra_queries
from exercise_extra2.orm_queries import orm_queries
from exercise_extra3.data_seeder import run_seeding

def run_exercise(exercise_num):
    """Executes the specified exercise based on user selection."""
    if exercise_num == 1:
        print("Running Exercise 1: Refer to screenshot in Notion")

    elif exercise_num == 2:
        print("Running Exercise 2: Create Tables")
        create_tables_with_data()

    elif exercise_num == 3:
        print("Running Exercise 3: Check & Create Tables")
        check_and_create_tables()
        
    elif exercise_num == 4:
        print("Running Exercise 4: Run queries")
        run_queries()
        
    elif exercise_num == 5:
        print("Running Exercise Extra 1: Run complex queries")
        run_extra_queries()
        
    elif exercise_num == 6:
        print("Running Exercise Extra 2: Run bidirectional orm queries")
        orm_queries()
        
    elif exercise_num == 7:
        print("Running Exercise Extra 3: Insert data with Faker")
        run_seeding()


if __name__ == "__main__":
    """Main menu for exercise selection."""
    print("🎓 DUAD Backend Week 6 - Database Exercises")
    print("=" * 50)
    
    while True:
        print("\nAvailable exercises:")
        print("0 - Exit")
        print("1 - Exercise 1: Refer to screenshot in Notion")
        print("2 - Exercise 2: Create Tables - Tables + Sample data")
        print("3 - Exercise 3: Check & Create Tables - Smart verification")
        print("4 - Exercise 4: Run queries")
        print("5 - Exercise Extra 1: Run complex queries")
        print("6 - Exercise Extra 2: Run bidirectional orm queries")
        print("7 - Exercise Extra 3: Insert data with Faker")

        try:
            exercise = int(input("\nWhich exercise? (0-7): "))
        except ValueError:
            print("❌ Invalid input. Please enter a number between 0-6.")
            continue

        if exercise == 0:
            print("Exiting... Thanks for using DUAD exercises!")
            break
        elif 1 <= exercise <= 7:
            print(f"\n🚀 Starting Exercise {exercise}...")
            run_exercise(exercise)
            print(f"✅ Exercise {exercise} completed!")
        else:
            print("❌ Invalid option. Please choose a valid exercise (0-6).")
