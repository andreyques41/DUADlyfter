def bubble_sort(unsorted_list: list[float] | list[int], verbose: bool = False):
    if not isinstance(unsorted_list, list) or not all(isinstance(item, (float, int)) for item in unsorted_list):
        raise ValueError('The input variable is not a list of numbers!')
    elif len(unsorted_list) == 0:
        raise ValueError('The list is empty!')
    
    # Outer loop to control the number of passes, starting from the end of the list
    for outer_index in range(len(unsorted_list)-1, 0, -1):
        has_made_changes = False  # Flag to check if any swaps were made
        # Inner loop to compare and swap elements from right to left
        for index in range(len(unsorted_list)-1, 0 + (len(unsorted_list)-1 - outer_index), -1):
            if unsorted_list[index] < unsorted_list[index-1]:  # Swap if elements are out of order
                temporary = unsorted_list[index]
                unsorted_list[index] = unsorted_list[index-1]
                unsorted_list[index-1] = temporary
                has_made_changes = True
                if verbose:  # Print the list after each swap if verbose is True
                    print(f'Iteration {len(unsorted_list)-1-outer_index,len(unsorted_list)-1-index}: \t{unsorted_list}')  # Print the list after each swap
        if not has_made_changes:  # Exit early if no swaps were made
            return unsorted_list

    return unsorted_list  # Return the sorted list

def execute():
    # Initialize the list to be sorted
    unsorted_list = [64, 34, 25, 12, 22, 11, 90]  # Example list for testing
    print(f'Original list: \t\t{unsorted_list}')

    sorted_list = bubble_sort(unsorted_list, verbose=True)  # Call the bubble sort function
    print(f'Ordered list: \t\t{sorted_list}')  # Print the sorted list

if __name__ == '__main__':
    try:
        execute()  # Execute the main function
    except Exception as ex:
        # Handle any unexpected errors
        print(f'There was an unknown error {ex}')