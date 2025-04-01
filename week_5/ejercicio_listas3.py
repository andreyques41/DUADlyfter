my_list = [3, 4, 3, 5, 6, 1, 7, 6]
print("List:", my_list)

last_index = len(my_list) - 1
last_item = my_list[last_index]
my_list[last_index] = my_list[0]
my_list[0] = last_item

print("List after switch:", my_list)