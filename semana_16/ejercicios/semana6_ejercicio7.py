import math
from ejercicios.semana6_ejercicio3 import check_if_valid_number_list

# Lee una lista de números y devuelve otra lista con solo los números primos
def get_prime_numbers(input_list):
    check_if_valid_number_list(input_list)
    
    prime_numbers = []

    for number in input_list:
        if is_prime(number):
            prime_numbers.append(number)

    return prime_numbers

# Evalúa si un número es primo o no
def is_prime(number):
    if not isinstance(number, (int, float)):
        raise ValueError("The input must be a numeric value")
    
    if number < 2:
        return False
    if number == 2:
        return True
    if number % 2 == 0:
        return False

    sqrt = int(math.sqrt(number))
    for index in range(3, sqrt + 1, 2):
        if number % index == 0:
            return False
    return True

if __name__ == '__main__':
    list = [1, 4, 6, 7, 13, 9, 67]
    print(get_prime_numbers(list))
