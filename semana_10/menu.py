import sys
import data, actions

# Define menu options as a dictionary
MENU_OPTIONS = {
    1: "Add new student information",
    2: "View all students' information",
    3: "View the top 3 students with the highest scores",
    4: "Get the average score of all students",
    5: "Export the information to a CSV file",
    6: "Import the information from an existing CSV file",
    7: "Exit the program"
}

# Display the menu options and prompt the user to select a valid option.
def select_menu_option():
    while True:
        print("Select an option:")
        for key, description in MENU_OPTIONS.items():
            print(f" {key} -> {description}")
        try:
            operation = int(input("Enter your choice: "))
            if operation in MENU_OPTIONS:
                return operation
            else:
                print("-----Error: You selected an invalid option-----")
        except ValueError:
            print("-----Error: You selected an invalid option-----")

# Execute the action corresponding to the selected menu option.
def execute_from_menu(menu_option, all_students, is_data_loaded):
    actions_map = {
        1: lambda: all_students.extend(actions.input_students()),
        2: lambda: actions.show_all_info(all_students),
        3: lambda: actions.show_top_students(all_students),
        4: lambda: actions.show_average_all_students(all_students),
        5: lambda: data.export_students(all_students),
        6: lambda: data.import_students(is_data_loaded)
    }

    if menu_option in actions_map:
        result = actions_map[menu_option]()
        if menu_option == 6:  # Special handling for importing data
            is_data_loaded, all_students = result
    else:
        sys.exit("Exiting the program")
    return is_data_loaded, all_students

# Check if student data has been loaded from a CSV file.
def check_if_data_loaded(flag):
    if not flag:
        print("-----You have not loaded any CSV file with students data yet-----")