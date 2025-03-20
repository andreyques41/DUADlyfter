# Importing the menu module to handle menu-related operations
import menu

# Function to start the student tracker application
def start_student_tracker():
    all_students = []
    data_loaded = False  # Indicates whether student data has been loaded
    while True:
        # Verify if student data has been loaded from a CSV file
        menu.check_if_data_loaded(data_loaded)
        # Display the menu and execute the selected option
        data_loaded, all_students = menu.execute_from_menu(
            menu.select_menu_option(), all_students, data_loaded
        )

# Entry point of the program
if __name__ == '__main__':
    try:
        # Start the student tracker application
        start_student_tracker()
    except Exception as ex:
        # Catch and display any unexpected errors
        print(f'There was an unexpected error: {ex}')