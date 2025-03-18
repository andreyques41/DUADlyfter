# Importing the menu module to handle menu-related operations
import menu

# Function to start the student tracker application
def start_student_tracker():
    while True:
        # Display the menu and execute the selected option
        menu.execute_from_menu(menu.show_menu())

# Entry point of the program
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