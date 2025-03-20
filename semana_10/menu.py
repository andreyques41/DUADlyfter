import sys
import data, actions

def select_menu_option(is_data_loaded):
    # Checks if the user has loaded any CSV file with students data
    check_if_data_loaded(is_data_loaded)
    # Loop to display the menu until a valid option is selected
    while True:
        try:
            # Prompt the user to select an option from the menu
            operation = int(input(
                'Select an option: \n'
                ' 1 -> Add new student information \n'
                ' 2 -> View all students\' information \n'
                ' 3 -> View the top 3 students with the highest scores \n'
                ' 4 -> Get the average score of all students \n'
                ' 5 -> Export the information to a CSV file \n'
                ' 6 -> Import the information from an existing CSV file \n'
                ' 7 -> Exit the program \n'
            ))
            # Check if the selected option is valid
            if 1 <= operation <= 7:
                return operation
            else:
                print('-----Error: You selected an invalid option-----')
        except ValueError:
            # Handle invalid input that cannot be converted to an integer
            print('-----Error: You selected an invalid option-----')

def execute_from_menu(menu_option, all_students, is_data_loaded):
    # Execute the corresponding action based on the selected menu option
    if menu_option == 1:
        # Add new student information
        all_students.extend(actions.input_students())
    elif menu_option == 2:
        # Display all students' information
        actions.show_all_info(all_students)
    elif menu_option == 3:
        # Display the top 3 students with the highest scores
        actions.show_top_students(all_students)
    elif menu_option == 4:
        # Display the average score of all students
        actions.show_average_all_students(all_students)
    elif menu_option == 5:
        # Export student information to a CSV file
        if all_students:
            data.export_to_csv(f'./{input("Please input the name of the CSV file to export the information to: \n")}.csv', all_students, all_students[0].keys())
        else:
            print('-----No students available to export-----')
    elif menu_option == 6:
        # Import student information from a CSV file
        is_data_loaded, all_students = data.import_from_csv(f'./{input("Please input the name of the CSV file to import the information from: \n")}.csv')
    else:
        # Exit the program
        sys.exit('Exiting the program')
    return is_data_loaded, all_students

def check_if_data_loaded(flag):
    if flag==False:
        print('-----You have not loaded any CSV file with students data yet-----')