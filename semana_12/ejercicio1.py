class BankAccount():
    balance: float

    def __init__(self, balance: float = 0):
        """Initialize the bank account with an optional initial balance."""
        self.balance = balance

    def _add_money(self, money):
        """Protected method to add money to the account."""
        self.balance += money

    def _subtract_money(self, money):
        """Protected method to subtract money from the account."""
        self.balance -= money

    def check_balance(self):
        """Print the current balance."""
        print(f'Current balance is: {self.balance}')

class SavingsAccount(BankAccount):
    min_balance: float

    def __init__(self, min_balance: float):
        """Initialize the savings account with a minimum balance."""
        self.balance = min_balance
        self.min_balance = min_balance

    def add_money(self, money):
        """Add money to the savings account."""
        self._add_money(money)

    def subtract_money(self, money):
        """Subtract money, ensuring the balance does not go below the minimum."""
        if self.balance - money < self.min_balance:
            raise Exception(f'Error: Transaction failed because balance can not go below {self.min_balance}')
        else:
            self._subtract_money(money)

def execute():
    """Run a series of operations on a savings account."""
    savings_account = SavingsAccount(500)
    savings_account.check_balance()
    savings_account.add_money(1000)
    savings_account.check_balance()
    while True:
        # Continuously subtract money based on user input
        savings_account.subtract_money(float(input('Input a numeric value to subtract from the account: \n')))
        savings_account.check_balance()

if __name__ == '__main__':
    try:
        # Execute the main program and handle exceptions
        execute()
    except Exception as ex:
        print(ex)