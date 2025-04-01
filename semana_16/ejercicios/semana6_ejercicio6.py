from ejercicios.semana6_ejercicio4 import check_if_valid_string

def sort_string1(input_string):
    check_if_valid_string(input_string)

    new_string = ''
    list = []

    #Divide la cadena de strings utilizando - como separador
    for char in input_string:
        if char != '-':
            new_string += char
        else:
            list.append(new_string)
            new_string = ''
            
    # Añadir la última palabra a la lista
    list.append(new_string)
    
    # Ordenar la lista
    list.sort()
    
    # Unir los elementos de la lista en una cadena, separados por -
    sorted_string = '-'.join(list)

    return sorted_string

def sort_string2(input_string):
    check_if_valid_string(input_string)

    #Divide la cadena de strings utilizando - como separador
    list = input_string.split('-')
    
    # Ordenar la lista
    list.sort()
    
    # Unir los elementos de la lista en una cadena, separados por -
    sorted_string = '-'.join(list)

    return sorted_string

if __name__ == '__main__':
    string = 'python-variable-funcion-computadora-monitor'
    print(sort_string1(string))
    print(sort_string2(string))