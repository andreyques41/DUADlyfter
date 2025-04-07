import sys
import os
from typing import Any
import FreeSimpleGUI as sg

# TEMPORARY Add the parent directory of 'Utilities' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Clases.finance_movements import FinanceMonth, HEADERS
from Utilities.utilities import validate_non_empty_string
from DataHandler.csv_handler import export_data,import_data

# Declarar los elementos

col1 = sg.Column([
    # Categories sg.Frame
    [sg.Frame('Tracking information:',
                [[sg.Text('Month:'), sg.InputText(key='month')],
                [sg.Text('Year:'), sg.InputText(key='year')],
                [sg.Button("Enter"), sg.Button("Exit")],],)], ], pad=(0,0))

col2 = sg.Column(
    [[sg.Frame('Table:', [[sg.Table([['','','','']], HEADERS, num_rows=1)]])]],
    pad=(0, 10)
)

# The final layout is a simple one
layout = [[col1],
        [col2]]

def create_window():
    # Crear la ventana
    window = sg.Window("Primer programa", layout)

    # Event Loop para procesar "events" y obtener los "values" de los inputs
    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        if validate_user_inputs(event, values):
            # Take actions if inputs are valid
            print(values)
            import_data(values['month'],values['year'])
        else:
            # Optionally, you can update a specific GUI element to show the error
            window['month'].update('')
            window['year'].update('')

    window.close()


def validate_user_inputs(event: Any, values: Any|str):
    try:
        validate_non_empty_string(values['month'])
        validate_non_empty_string(values['year'])
        return True
    except ValueError as vex:
        sg.popup(f"Input Error: {vex}", title="Validation Error", keep_on_top=True)
        return False    

if __name__ == '__main__':
    try:
        # Start the student tracker application
        create_window()
    except Exception as ex:
        # Catch and display any unexpected errors
        print(f'There was an unexpected error: {ex}')