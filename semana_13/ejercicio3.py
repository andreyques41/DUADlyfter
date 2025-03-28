from datetime import date

class User():
    # Define the attributes of the User class
    name: str
    date_of_birth: date

    def __init__(self, name: str, date_of_birth: date):
        # Initialize the User object with name and date of birth
        self.name = name
        self.date_of_birth = date_of_birth

    @property
    def age(self):
        # Calculate the user's age based on the current date and date of birth
        today = date.today()
        return (
            today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )

# A decorator function to validate the user's age before executing the decorated function
def decorator(func):
    def wrapper(user: User):
        # Check if the user is underage and raise an error if true
        if user.age < 18:
            raise ValueError(f'Error: The user {user.name} is underage')
        # Call the original function if the user is of valid age
        func(user)
    return wrapper

# A function to print the user's age, decorated with the age validation decorator
@decorator
def print_user_age(user: User):
    # Print the user's name and age
    print(f"User {user.name} Age: {user.age}")

if __name__ == '__main__':
    try:
        # Create a user who is of valid age and print their age
        my_user = User('Andy', date(1990, 1, 1))
        print_user_age(my_user)

        # Create a user who is underage and attempt to print their age
        my_other_user = User('Juan', date(2010, 7, 1))
        print_user_age(my_other_user)
    except Exception as ex:
        # Handle and print any exceptions that occur during execution
        print(ex)