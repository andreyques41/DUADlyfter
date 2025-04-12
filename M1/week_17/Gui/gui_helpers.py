from Clases.finance_movements import FinanceMonth, Movement
from Utilities.utilities import validate_non_empty_string, validate_positive_number, debug_print
from DataHandler.csv_handler import export_data
import FreeSimpleGUI as sg

def determine_movement_type(values: dict) -> str:
    # Determine the movement type based on the radio button selection
    if values['income']:
        return 'Income'
    elif values['expense']:
        return 'Expense'
    return None

def add_movement_to_finance_month(window: sg.Window, finance_month: FinanceMonth, name: str, category: str, movement_type: str, amount: str):
    if validate_new_movement_inputs(name, category, movement_type, amount):
        try:
            movement = Movement(name, category, movement_type, validate_positive_number(amount))
            finance_month.add_movement(movement)
            update_data_table(window, finance_month)
            export_data(finance_month)  # Automatically save to the default file
            sg.popup(f"{movement_type} added successfully!", title="Success", keep_on_top=True)
        except Exception as ex:
            popup_error_msg(f"Failed to add {movement_type.lower()}: {ex}")

def validate_new_movement_inputs(name: str, category: str, movement_type: str, amount: str):
    try:
        validate_non_empty_string(name)
        validate_non_empty_string(category)
        validate_positive_number(amount)
        return True
    except ValueError as vex:
        popup_error_msg(vex)
        return False    

def update_data_table(window: sg.Window, finance_month: FinanceMonth):
    try:
        # Convert movements to a list of lists for the table
        table_data = finance_month.convert_to_list_of_list()
        debug_print(f"Updating table with data: {table_data}")  # Debugging output
        window['data_table'].update(values=table_data)
    except Exception as ex:
        popup_error_msg(f"Failed to update table: {ex}")

def popup_error_msg(error):
    sg.popup(f"Input Error: {error}", title="Validation Error", keep_on_top=True)