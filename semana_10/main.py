# Importing the menu module to handle menu-related operations
import menu

# Function to start the student tracker application
def start_student_tracker():
    all_students = []
    is_data_loaded = False
    while True:
        # Display the menu and execute the selected option
        is_data_loaded, all_students  = menu.execute_from_menu(menu.select_menu_option(is_data_loaded),all_students,is_data_loaded)

# Entry point of the program2
if __name__ == '__main__':
    try:
        # Start the student tracker application
        start_student_tracker()
    except Exception as ex:
        # Catch and display any unknown errors
        print(f'There was an unexpected error: {ex}')
    except SystemExit as exit:
        # Handle system exit gracefully
        print(exit)