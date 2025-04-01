def sum_from_list (list):
	sum = 0
	for number in list:
		sum = sum + number
	return sum

if __name__ == '__main__':
	list = [12, 5, 7, 15]
	print(sum_from_list(list))