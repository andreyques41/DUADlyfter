from typing import Any
import FreeSimpleGUI as sg
from Utilities.utilities import validate_non_empty_string

sg.theme('DarkAmber')
# Declarar los elementos
layout = [
    [sg.Text("Finance tracker",font='Courier 12', text_color='blue', background_color='green')],
    [sg.Text('Month:'), sg.InputText(key='month')],
    [sg.Text('Year:'), sg.InputText(key='year')],
    [sg.Button("Sumar"), sg.Button("Restar")],
]


def create_window():
    # Crear la ventana
    window = sg.Window("Primer programa", layout)

    # Event Loop para procesar "events" y obtener los "values" de los inputs
    while True:
        event, values = window.read()

        validate_user_inputs(event, values)

        print(values)

        if event in (sg.WIN_CLOSED, 'Exit'):
            break

    window.close()


def validate_user_inputs(event: Any, values: Any|str):
    try:
        validate_non_empty_string(values['month'])
        validate_non_empty_string(values['year'])
    except ValueError as vex:
        raise vex
    

if __name__ == '__main__':
    try:
        # Start the student tracker application
        create_window()
    except Exception as ex:
        # Catch and display any unexpected errors
        print(f'There was an unexpected error: {ex}')