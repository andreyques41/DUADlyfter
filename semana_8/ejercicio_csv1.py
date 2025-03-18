import csv

# Method that creates the csv file with the input data
def create_csv():
    is_valid = False
    index = 0
    list_of_games = []

    # Ask the user to input a positive integer
    while not is_valid:
        is_valid, amount_of_games =  ask_amount_of_games()

    # Creates a list of inputs from the user
    while index < amount_of_games:
        input_dict = ask_csv_input(index + 1)
        list_of_games.append(input_dict)
        index += 1

    # Creates the csv file with the list of inputs from the user
    write_csv_file('videogames.csv', list_of_games, list_of_games[0].keys())

# Method that asks the user to input a positve integer
def ask_amount_of_games():
    try:
        amount_of_games = int(input('How many videogames are you going to record? \n'))
        if amount_of_games <= 0:
            print('-----Error: Only positive integers values are allowed-----')
            return False, 0  
        return True, amount_of_games
    except ValueError:
        print('-----Error: Only positive integers values are allowed-----')
        return False, 0

# Method to ask the user to input the values for the designated keys 
def ask_csv_input(index):
    dictionary = {
        'name':  input(f'Input the name of the game #{index}: \n'),
        'gender' : input(f'Input the gender of the game #{index}: \n'),
        'developer' : input(f'Input the developer of the game #{index}: \n'),
        'clasification' : input(f'Input the ESRB clasification of the game #{index}: \n')
    }
    return dictionary

# Writes the into a file a set of data in csv format
def write_csv_file(file_path, data, headers):
    with open(file_path, 'w', encoding='utf-8') as file:
        writer = csv.DictWriter(file, headers)
        writer.writeheader()
        writer.writerows(data)

if __name__ == '__main__':
    try:
        create_csv()
    except Exception as ex:
        print(ex)
        exit()