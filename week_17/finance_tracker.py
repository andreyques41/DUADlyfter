from Gui.main_gui import create_window
# Entry point of the program
if __name__ == '__main__':
    try:
        # Start the student tracker application
        create_window()
    except Exception as ex:
        # Catch and display any unexpected errors
        print(f'There was an unexpected error: {ex}')