from typing import List, Dict, Union

from Utilities.utilities import validate_positive_number
from Utilities.utilities import debug_print

# Define the headers used for representing movement data
HEADERS = ['Name', 'Category', 'Income/Expense', 'Amount']

class Movement:
    # Represents a financial movement, either an income or an expense.
    # Each movement has a name, category, type (Income/Expense), and amount.
    VALID_TYPES = ['Income', 'Expense']

    def __init__(self, name: str = '', category: str = '', movement_type: str = '', amount: float = 0):
        # Validate the movement type and amount
        if movement_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid movement type: {movement_type}. Must be one of {self.VALID_TYPES}.")
        if amount < 0:
            raise ValueError("Amount must be a positive number.")
        self.name = name
        self.category = category
        self.movement_type = movement_type
        self.amount = amount

    def __str__(self) -> str:
        # Return a string representation of the movement
        return f"Name: {self.name}, Category: {self.category}, Income/Expense: {self.movement_type}, Amount: {self.amount}"

class FinanceMonth:
    # Represents a financial summary for a specific month and year.
    # Allows adding, removing, and analyzing financial movements.
    headers = HEADERS

    def __init__(self, month: str = 'enero', year: int = '2000'):
        # Initialize the month, year, and list of movements
        self.month = month
        self.year = year
        self.movements: List[Movement] = []

    def add_movement(self, movement: Movement) -> None:
        # Add a financial movement to the list
        self.movements.append(movement)

    def remove_movement(self, movement: Movement) -> None:
        # Remove a financial movement from the list
        # Raise an error if the movement does not exist
        try:
            self.movements.remove(movement)
        except ValueError:
            raise ValueError(f"The movement '{movement.name}' in category '{movement.category}' does not exist.")
            
    def convert_to_list_of_list(self) -> List[List[str]]:
        # Convert movements to a list of lists for table display
        return [
            [movement.name, movement.category, movement.movement_type, str(movement.amount)]
            for movement in self.movements
        ]
    
    def convert_to_list_of_dict(self) -> List[Dict[str, Union[str, float]]]:
        # Convert the list of movements into a list of dictionaries
        # for easier data representation and export
        if len(self.headers) != 4:
            raise ValueError("HEADERS must contain exactly 4 elements.")
        return [
            {
                self.headers[0]: movement.name,
                self.headers[1]: movement.category,
                self.headers[2]: movement.movement_type,
                self.headers[3]: movement.amount,
            }
            for movement in self.movements
        ]
    
    def add_movements_from_list(self, list_of_dict: List[Dict[str, str]]) -> None:
        # Validate headers
        if set(list_of_dict[0].keys()) != set(HEADERS):
            raise ValueError(f"The data from the CSV file '{self.month}_{self.year}.csv' must have the headers: {HEADERS}")

        # Add movements from the list of dictionaries
        for dictionary in list_of_dict:
            try:
                movement = Movement(
                    name=dictionary[HEADERS[0]],
                    category=dictionary[HEADERS[1]],
                    movement_type=dictionary[HEADERS[2]],
                    amount=validate_positive_number(dictionary[HEADERS[3]])
                )
                self.add_movement(movement)
            except Exception as ex:
                raise ValueError(f"Error processing movement data: {dictionary}. Details: {ex}")