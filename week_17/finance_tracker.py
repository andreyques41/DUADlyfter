from Gui.main_gui import execute_main_window

# Entry point of the program
if __name__ == '__main__':
    try:
        # Start the finance tracker application
        execute_main_window()
    except Exception as ex:
        # Catch and display any unexpected errors
        print(f'There was an unexpected error: {ex}')