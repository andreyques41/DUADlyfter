my_list = [3, 4, 3, 5, 6, 1, 7, 9, 6]
print("List:", my_list)

for index in range(len(my_list)-1, -1, -1):
    if my_list[index] % 2 == 1:
        my_list.pop(index)
        
print("List after removing odd numbers:", my_list)