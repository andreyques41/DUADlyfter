def bubble_sort(unsorted_list: list[float] | list[int]):
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
                print(f'Iteration {len(unsorted_list)-1-outer_index,len(unsorted_list)-1-index}: \t{unsorted_list}')  # Print the list after each swap
        if not has_made_changes:  # Exit early if no swaps were made
            return

def execute():
    # Initialize the list to be sorted
    unsorted_list = [-625, 87, 3, -96, 44, 29, 999]
    print(f'Original list:\n\t{unsorted_list}')

    bubble_sort(unsorted_list)  # Call the bubble sort function
    print(f'Ordered list:\n\t{unsorted_list}')  # Print the sorted list

if __name__ == '__main__':
    try:
        execute()  # Execute the main function
    except Exception as ex:
        # Handle any unexpected errors
        print(f'There was an unknown error {ex}')