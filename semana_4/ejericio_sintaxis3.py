import random

def main():
    secret_number = random.randint(1, 10)
    user_number = 0
    while user_number != secret_number:
        user_number = int(input("Enter a number between 1 and 10: "))
    print("You win!")

if __name__ == "__main__":
    main()