# Method that reads a file, creates a list with each text line, and return the list sorted
def read_file(filepath):
    with open(filepath) as file:
        list = file.readlines()
        list.sort()
    return list

# Method that takes a list of strings and write them in a new file
def write_file(list, filepath):
    with open(filepath, 'w', encoding='utf-8') as file:
        file.writelines(list)

if __name__ == '__main__':
    try:
        list = read_file('song_names.txt')
        write_file(list, 'song_names_sorted.txt')
    except Exception as ex:
        print(ex)
        exit()