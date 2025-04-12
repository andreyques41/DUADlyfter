def main():
    first_name = input("What is your first name? ")
    last_name = input("What is your last name? ")
    age = int(input("What is your age? "))

    if age < 2:
        print("You are a baby")
    elif 2 <= age <= 11:
        print("You are a child")
    elif 12 <= age <= 14:
        print("You are a preadolescent")
    elif 15 <= age <= 17:
        print("You are a teenager")
    elif 18 <= age <= 35:
        print("You are a young adult")
    elif 36 <= age <= 64:
        print("You are an adult")
    else:
        print("You are a senior adult")

if __name__ == "__main__":
    main()