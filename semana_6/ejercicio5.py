def count_letters(string):
    uppercase = 0
    lowercase = 0
    for char in string:
        if char.isupper():
            uppercase += 1
        elif char.islower():
            lowercase += 1
    return uppercase, lowercase

if __name__ == '__main__':
    string = 'Hola comunIdad dE Lyfter'
    upper, lower = count_letters(string)
    print(f'There are {upper} uppercase and {lower} lowercase letters in "{string}"')