import sys

def calculator(current_number):
    while True:
        print_current_number(current_number)
        operation = ask_for_operation()

        if operation == 6:  # Exit
            sys.exit('Exiting the calculator')

        if operation == 5:  # Clear result
            return 0

        input_number = ask_for_digit()
        current_number = perform_operation(operation, current_number, input_number)

def ask_for_operation():
    while True:
        try:
            operation = int(input(
                'Select an operation: \n'
                ' 1 -> Addition \n'
                ' 2 -> Subtraction \n'
                ' 3 -> Multiplication \n'
                ' 4 -> Division \n'
                ' 5 -> Clear result \n'
                ' 6 -> Exit \n'
            ))
            if 1 <= operation <= 6:
                return operation
            else:
                print('-----Error: You selected an invalid operation-----')
        except ValueError:
            print('-----Error: You selected an invalid operation-----')

def ask_for_digit():
    while True:
        try:
            return float(input('Select a numerical digit: \n'))
        except ValueError:
            print('-----Error: That is not a numerical digit-----')

def perform_operation(operation, current_number, input_number):
    if operation == 1:  # Addition
        return current_number + input_number
    elif operation == 2:  # Subtraction
        return current_number - input_number
    elif operation == 3:  # Multiplication
        return current_number * input_number
    elif operation == 4:  # Division
        if input_number == 0:
            print('-----Error: It is not possible to divide by 0-----')
            return current_number
        return current_number / input_number
    return current_number

def print_current_number(number):
    print(f'Current number: \n --------> {number}')

if __name__ == '__main__':
    current_number = 0
    try:
        while True:
            current_number = calculator(current_number)
    except SystemExit as ex:
        print(ex)