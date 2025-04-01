from ejercicios.semana6_ejercicio4 import check_if_valid_string

def count_letters(input_string):
    check_if_valid_string(input_string)

    uppercase = 0
    lowercase = 0
    for char in input_string:
        if char.isupper():
            uppercase += 1
        elif char.islower():
            lowercase += 1
    return uppercase, lowercase

if __name__ == '__main__':
    string = 'Hola comunIdad dE Lyfter'
    upper, lower = count_letters(string)
    print(f'There are {upper} uppercase and {lower} lowercase letters in "{string}"')