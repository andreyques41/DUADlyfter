def print_name ():
	print('Hola me llamo Andrey')
	a = 5

def print_fullname ():
	print_name()
	b = a

if __name__ == '__main__':
	print_fullname()
	
#     Hola me llamo Andrey
# Traceback (most recent call last):
#   File "c:\Users\andre\OneDrive\Documents\VSCode\Lyfter\M1\py1\test.py", line 10, in <module>
#     print_fullname()
#     ~~~~~~~~~~~~~~^^
#   File "c:\Users\andre\OneDrive\Documents\VSCode\Lyfter\M1\py1\test.py", line 7, in print_fullname      
#     b = a
#         ^
# NameError: name 'a' is not defined

number = 5

def change_number ():
	number = 8
	return number
	
if __name__ == '__main__':
	print(change_number())