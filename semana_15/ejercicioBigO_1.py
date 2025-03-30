def bubble_sort(unsorted_list: list[float] | list[int]):  # O(n^2) worst case, O(n) best case
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
                print(f'Iteration {outer_index,index}: \t{unsorted_list}')  # O(1) 
        if not has_made_changes:  # O(1)
            return

def execute():  # O(1)
    # Initialize the list to be sorted
    unsorted_list = [-625, 87, 3, -96, 44, 29, 999]  # O(1)
    print(f'Original list:\n\t{unsorted_list}')  # O(1)

    bubble_sort(unsorted_list)  # O(n^2) worst case, O(n) best case
    print(f'Ordered list:\n\t{unsorted_list}')  # O(1)  

if __name__ == '__main__':
    try:  # O(1)
        execute()  # O(1)
    except Exception as ex:  # O(1)
        # Handle any unexpected errors
        print(f'There was an unknown error {ex}')  # O(1)