def bubble_sort(unsorted_list: list[float] | list[int]):
    if not isinstance(unsorted_list, list) or not all(isinstance(item, (float, int)) for item in unsorted_list):
        print('The input variable is not a list of numbers!')
    else:
        # Outer loop to control the number of passes
        for outer_index in range(0, len(unsorted_list) - 1):
            has_made_changes = False  # Flag to check if any swaps were made
            # Inner loop to compare adjacent elements
            for index in range(0, len(unsorted_list) - 1 - outer_index):
                if unsorted_list[index] > unsorted_list[index+1]:  # Swap if elements are out of order
                    temporary = unsorted_list[index]
                    unsorted_list[index] = unsorted_list[index+1]
                    unsorted_list[index+1] = temporary
                    has_made_changes = True
                    print(f'Iteration {outer_index,index}: \t{unsorted_list}')  # Print the list after each swap
            if not has_made_changes:  # Exit early if no swaps were made
                return

def execute():
    # Initialize the list to be sorted
    unsorted_list = []
    print(f'Original list:\n\t{unsorted_list}')

    bubble_sort(unsorted_list)  # Call the bubble sort function
    print(f'Ordered list:\n\t{unsorted_list}')  # Print the sorted list

if __name__ == '__main__':
    try:
        execute()  # Execute the main function
    except Exception as ex:
        # Handle any unexpected errors
        print(f'There was an unknown error {ex}')