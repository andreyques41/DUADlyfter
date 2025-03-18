import sys
import data, actions

def show_menu():
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

def execute_from_menu(menu_option):
    # Execute the corresponding action based on the selected menu option
    if menu_option == 1:
        # Add new student information
        actions.input_new_student()
    elif menu_option == 2:
        # Display all students' information
        actions.show_all_info()
    elif menu_option == 3:
        # Display the top 3 students with the highest scores
        actions.show_top_students()
    elif menu_option == 4:
        # Display the average score of all students
        actions.show_average_all_students()
    elif menu_option == 5:
        # Export student information to a CSV file
        headers = ('name', 'score')
        new_data = [{'name': 'andy', 'score': '85'}]
        data.export_to_csv(f'./{input("Please input the name of the CSV file to export the information to:")}.csv', new_data, headers)
    elif menu_option == 6:
        # Import student information from a CSV file
        data.import_from_csv(f'./{input("Please input the name of the CSV file to import the information from:")}.csv')
    else:
        # Exit the program
        sys.exit('Exiting the program')