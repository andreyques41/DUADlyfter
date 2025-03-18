import sys, menu, actions

def start_student_tracker():
    menu_option = menu.show_menu()
    menu.execute_from_menu()
    return True

if __name__ == '__main__':
    try:
        start_student_tracker()
    except Exception as ex:
        print(f'There was an unknown error: {ex}')
    except SystemExit as exit:
        print(exit)