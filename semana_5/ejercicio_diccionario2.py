list_a = ['first_name', 'last_name', 'role']
list_b = ['Alek', 'Castillo', 'Software Engineer']

dict = {}
for index in range(len(list_a)):
    dict[list_a[index]] = list_b[index]

print(dict)