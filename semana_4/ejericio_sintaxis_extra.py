def main():
    user_number = int(input("Enter a number: "))
    count = 0
    sum = 0
    while (count <= user_number):
        sum += count
        count += 1
    print("The sum is: ", sum)

if __name__ == "__main__":
    main()