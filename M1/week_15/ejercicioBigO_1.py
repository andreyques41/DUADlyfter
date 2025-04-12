def bubble_sort(unsorted_list: list[float] | list[int], verbose: bool = False):  # O(n^2) worst case, O(n) best case
    if not isinstance(unsorted_list, list) or not all(isinstance(item, (float, int)) for item in unsorted_list): # O(n)
        raise ValueError('The input variable is not a list of numbers!')  # O(1)
    elif len(unsorted_list) == 0:  # O(1)
        raise ValueError('The list is empty!')  # O(1)

    # Outer loop to control the number of passes
    for outer_index in range(0, len(unsorted_list) - 1):  # O(n)
        has_made_changes = False  # O(1)
        # Inner loop to compare adjacent elements
        for index in range(0, len(unsorted_list) - 1 - outer_index):  # O(n) in the worst case
            if unsorted_list[index] > unsorted_list[index+1]:  # O(1)
                temporary = unsorted_list[index]  # O(1)
                unsorted_list[index] = unsorted_list[index+1]  # O(1)
                unsorted_list[index+1] = temporary  # O(1)
                has_made_changes = True  # O(1)
                if verbose:  # Print the list after each swap if verbose is True
                    print(f'Iteration {outer_index,index}: \t{unsorted_list}')  # O(1)
        if not has_made_changes:  # O(1)
            return unsorted_list # O(1)

    return unsorted_list  # O(1)

def execute():  # O(1)
    # Initialize the list to be sorted
    unsorted_list = [64, 34, 25, 12, 22, 11, 90]  # O(1)
    print(f'Original list: \t\t{unsorted_list}')  # O(1)

    sorted_list = bubble_sort(unsorted_list, verbose=True)  # O(n^2) worst case, O(n) best case
    print(f'Ordered list: \t\t{sorted_list}')  # O(1)  

if __name__ == '__main__':
    try:  # O(1)
        execute()  # O(1)
    except Exception as ex:  # O(1)
        # Handle any unexpected errors
        print(f'There was an unknown error {ex}')  # O(1)