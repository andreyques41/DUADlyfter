def sort_string1(string):
    new_string = ''
    list = []

    #Divide la cadena de strings utilizando - como separador
    for char in string:
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

def sort_string2(string):
    #Divide la cadena de strings utilizando - como separador
    list = string.split('-')
    
    # Ordenar la lista
    list.sort()
    
    # Unir los elementos de la lista en una cadena, separados por -
    sorted_string = '-'.join(list)

    return sorted_string

if __name__ == '__main__':
    string = 'python-variable-funcion-computadora-monitor'
    print(sort_string1(string))
    print(sort_string2(string))