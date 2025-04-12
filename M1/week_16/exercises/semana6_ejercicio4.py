def reverse_string (input_string):
	check_if_valid_string(input_string)
	
	string_reversed = []
	for index in range(len(input_string) -1, -1, -1):
		string_reversed.append(input_string[index])
	return ''.join(string_reversed)

def reverse_string2 (input_string):
	check_if_valid_string(input_string)
	
	return ''.join(reversed(input_string))

def reverse_string3 (input_string):
	check_if_valid_string(input_string)
	
	return input_string[::-1]

def check_if_valid_string(input_string: str):
	if not isinstance(input_string, str):
		raise ValueError("The input must be a string")
	elif input_string == '':
		raise ValueError("The input string is empty")
	
if __name__ == '__main__':
	string = 'Hola comunidad de Lyfter'
	print(reverse_string(string))
	print(reverse_string2(string))
	print(reverse_string3(string))