def reverse_string (string):
	string_reversed = []
	for index in range(len(string) -1, -1, -1):
		string_reversed.append(string[index])
	return ''.join(string_reversed)

def reverse_string2 (string):
	return ''.join(reversed(string))

def reverse_string3 (string):
	return string[::-1]

if __name__ == '__main__':
	string = 'Hola comunidad de Lyfter'
	print(reverse_string(string))
	print(reverse_string2(string))
	print(reverse_string3(string))