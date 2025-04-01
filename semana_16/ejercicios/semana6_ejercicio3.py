def sum_from_list(list_to_sum):
    check_if_valid_number_list(list_to_sum)
    
    sum = 0
    for number in list_to_sum:
        sum = sum + number
    return sum

def check_if_valid_number_list(input_list: list[float] | list[int]):
    if not isinstance(input_list, list) or not all(isinstance(item, (float, int)) for item in input_list):
        raise ValueError("The input must be a list of numbers")
    elif len(input_list) == 0:
        raise ValueError("Input list cannot be empty")

if __name__ == '__main__':
    input_list = [12, 5, 7, 15]
    print(sum_from_list(input_list))