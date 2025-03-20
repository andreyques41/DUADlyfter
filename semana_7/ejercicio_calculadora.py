def calculator(current_number):
    # Define local variables
    is_valid = False
    input_number = 0

    # Print current number on console
    print_current_number(current_number)

    # Run the ask_for_operation method until the input is valid
    while not is_valid:
        is_valid, operation = ask_for_operation()
        if operation == 6:
            raise Exception('Exiting the calculator')

    # Runs if operation is different from clear result option
    if operation != 5:
        # Run the ask_for_digit method until the input is valid
        is_valid = False
        while not is_valid:
            is_valid, input_number = ask_for_digit()

    # Calculates the result value based on the operation and input number
    return perform_operation(operation, current_number, input_number)

# Method to ask the user to select an operation
def ask_for_operation():
    try:
        operation = int(input('Select an operation: \n 1 -> Addition \n 2 -> Subtraction \n 3 -> Multiplication \n 4 -> Division \n 5 -> Clear result \n 6 -> Exit \n'))
        if 1 <= operation <= 6:
            return True, operation
        else:
            print('-----Error: You selected an invalid operation-----')
            # Print current number on console
            print_current_number(current_number)
            return False, -1
    except ValueError:
        print('-----Error: You selected an invalid operation-----')
        # Print current number on console
        print_current_number(current_number)
        return False, -1

# Method to ask the user to input a numerical number
def ask_for_digit():
    try:
        number = float(input('Select a numerical digit: \n'))
        return True, number
    except ValueError:
        print('-----Error: That is not a numerical digit-----')
        # Print current number on console
        print_current_number(current_number)
        return False, -1

# Method to perform an operation based on the user selection
def perform_operation(operation, current_number, input_number):
    # Options for operation = 1 -> Addition \n 2 -> Subtraction  \n 3 -> Multiplication \n 4 -> Division \n 5 -> Clear result \n 6 -> Exit 
    if operation == 1:
        result = current_number + input_number
    elif operation == 2:
        result = current_number - input_number
    elif operation == 3:
        result = current_number * input_number
    elif operation == 4:
        if input_number == 0:
            print('-----Error: Is not possible to divide by 0-----')
            result = current_number
        else:
            result = current_number / input_number
    elif operation == 5:
        result = 0
    elif operation == 6:
        exit()
    return result

def print_current_number (number):
    print(f'Current number: \n --------> {number}')

if __name__ == '__main__':
    current_number = 0
    try:
        # Will run calculator method until exit option is selected
        while True:
            current_number = calculator(current_number)
    except Exception as ex:
        print(ex)
        exit()