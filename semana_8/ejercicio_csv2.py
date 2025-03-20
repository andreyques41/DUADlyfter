import csv

# Method that creates the csv file with the input data
def create_csv():
    # Ask the user to input a positive integer
    amount_of_games = ask_amount_of_games()

    # Creates a list of inputs from the user
    list_of_games = [ask_csv_input(index + 1) for index in range(amount_of_games)]

    # Creates the csv file with the list of inputs from the user
    write_csv_file('./videogames.csv', list_of_games, list_of_games[0].keys())

# Method that asks the user to input a positive integer
def ask_amount_of_games():
    while True:
        try:
            amount_of_games = int(input('How many videogames are you going to record? \n'))
            if amount_of_games > 0:
                return amount_of_games
            else:
                print('-----Error: Only positive integers values are allowed-----')
        except ValueError:
            print('-----Error: Only positive integers values are allowed-----')

# Method to ask the user to input the values for the designated keys 
def ask_csv_input(index):
    return {
        'name': input(f'Input the name of the game #{index}: \n'),
        'genre': input(f'Input the genre of the game #{index}: \n'),
        'developer': input(f'Input the developer of the game #{index}: \n'),
        'classification': input(f'Input the ESRB classification of the game #{index}: \n')
    }

# Writes the data into a file in csv format
def write_csv_file(file_path, data, headers):
    with open(file_path, 'w', encoding='utf-8') as file:
        writer = csv.DictWriter(file, headers, delimiter='\t')
        writer.writeheader()
        writer.writerows(data)

if __name__ == '__main__':
    try:
        create_csv()
    except Exception as ex:
        print(ex)
        exit()