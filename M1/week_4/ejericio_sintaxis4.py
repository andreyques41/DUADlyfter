def main():
    user_number1 = int(input("Enter a number: "))
    user_number2 = int(input("Enter a second number: "))
    user_number3 = int(input("Enter a third number: "))
    if user_number1 > user_number2 and user_number1 > user_number3:
        print(f"{user_number1} is the largest number.")
    elif user_number2 > user_number1 and user_number2 > user_number3:
        print(f"{user_number2} is the largest number.")
    else:
        print(f"{user_number3} is the largest number.")

if __name__ == "__main__":
    main()