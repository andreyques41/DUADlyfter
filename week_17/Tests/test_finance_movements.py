HEADERS = ['Name', 'Category', 'Income/Expense', 'Amount']

class Movement():
    def __init__(self, name: str, category: str, type_in_out: str, amount: float):
        self.name = name
        self.category = category
        self.type_in_out = type_in_out
        self.amount = amount

class FinanceMonth:
    headers = HEADERS
    def __init__(self, month, year):
        self.month = month
        self.year = year
        self.movements = []

    def add_movement(self, movement: Movement):
        self.movements.append(movement)

    def remove_movement(self, movement: Movement):
        try:
            self.movements.remove(movement)
        except ValueError:
            print(f'The movement with name: {movement.name} does not exist')