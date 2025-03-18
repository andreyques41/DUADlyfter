import sys
import data, actions

def show_menu():
    while True:
        try:
            operation = int(input(
                'Select an option: \n'
                ' 1 -> Add new student information \n'
                ' 2 -> Check all stundent\'s information \n'
                ' 3 -> Check top 3 students with highest scores \n'
                ' 4 -> Get the average score of all students \n'
                ' 5 -> Export the information to a CSV file \n'
                ' 6 -> Import the information from an existing CSV file \n'
                ' 7 -> Exit the program \n'
            ))
            if 1 <= operation <= 7:
                return operation
            else:
                print('-----Error: You selected an invalid operation-----')
        except ValueError:
            print('-----Error: You selected an invalid operation-----')

def execute_from_menu(menu_option):
    if menu_option == 1:
        actions.input_new_student()
    elif menu_option == 2:
        actions.show_all_info()
    elif menu_option == 3:
        actions.show_top_students()
    elif menu_option == 4:
        actions.show_average_all_students()
    elif menu_option == 5:
        data.export_info_to_csv()
    elif menu_option == 6:
        data.import_info_from_csv()
    else:
        sys.exit('Exiting the program')