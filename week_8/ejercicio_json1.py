import json

# Main function to add a new Pokémon to the JSON file
def add_new_pokemon():
    # Step 1: Get the new Pokémon details from the user
    new_pokemon = input_new_pokemon()

    # Step 2: Read the existing Pokémon data from the JSON file
    pokemon_list = read_json('./pokemon.json')

    # Step 3: Add the new Pokémon to the list
    pokemon_list.append(new_pokemon)

    # Step 4: Write the updated list back to the JSON file
    write_json(pokemon_list, './pokemon.json')


# Function to collect details of a new Pokémon from the user
def input_new_pokemon():
    name = input('Name of the new pokemon? \n')
    type = input('Type of the new pokemon? \n')

    return {
        "name": {"english": name},
        "type": [type],
        "base": {
            "HP": get_positive_int('Stat of HP? \n'),
            "Attack": get_positive_int('Stat of attack? \n'),
            "Defense": get_positive_int('Stat of defense? \n'),
            "Sp. Attack": get_positive_int('Stat of sp_attack? \n'),
            "Sp. Defense": get_positive_int('Stat of sp_defense? \n'),
            "Speed": get_positive_int('Stat of speed? \n')
        }
    }

# Prompt the user to input a positive integer.
def get_positive_int(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            print('-----Error: Only positive integers values are allowed-----')
        except ValueError:
            print('-----Error: Only positive integers values are allowed-----')

# Function to read data from a JSON file and return it as a Python dictionary
def read_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            py_dict = json.load(file)
            return py_dict
    except FileNotFoundError:
        print(f"-----Error: The file at '{path}' was not found.-----")
        return []
    except json.JSONDecodeError:
        print(f"-----Error: The file at '{path}' contains invalid JSON.-----")
        return []

# Function to write a Python list back to a JSON file
def write_json(data_list, path):
    try:
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data_list, file, indent=4)
    except (PermissionError, IOError) as e:
        print(f"Failed to write to file {path}: {e}")

if __name__ == '__main__':
    try:
        add_new_pokemon()
    except Exception as ex:
        # Handle any unexpected errors
        print(f"An error occurred: {ex}")
        exit()