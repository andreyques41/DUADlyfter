number_list = []
index = 0
largest_number = 0

while index < 10:
    index += 1
    number = int(input("Ingrese un número: "))
    number_list.append(number)
    if number > largest_number:
        largest_number = number

print(f"Number list: {number_list}. El mas alto fue: {largest_number}")