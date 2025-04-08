import sys
from typing import Any
import FreeSimpleGUI as sg
from Clases.finance_movements import FinanceMonth, HEADERS
from DataHandler.csv_handler import export_data, import_data
from Gui.gui_helpers import (
    add_movement_to_finance_month,
    update_data_table
)

# Define a custom theme for a more modern look
sg.theme('LightGrey1')

# Initialize a list to store valid categories
valid_categories = []

# Create the main window layout
def create_main_window():
    # Header section
    header = [
        [sg.Text('Finance Tracker', font=('Helvetica', 24, 'bold'), justification='center', text_color='#333333', pad=(10, 20))]
    ]

    # Top section: Buttons for adding movements, categories, and removing movements
    top_buttons = [
        [sg.Button("Add Expense", size=(15, 1), button_color=('white', '#F44336'), font=('Helvetica', 12)),
        sg.Button("Add Income", size=(15, 1), button_color=('white', '#4CAF50'), font=('Helvetica', 12)),
        sg.Button("Add Category", size=(15, 1), button_color=('white', '#2196F3'), font=('Helvetica', 12)),
        sg.Button("Remove Movement", size=(15, 1), button_color=('white', '#FF9800'), font=('Helvetica', 12))]
    ]

    # Middle section: Financial Data Table
    middle_section = [
        [sg.Frame('Financial Data Table',
            [[sg.Table(values=[['', '', '', '']], headings=HEADERS, 
                auto_size_columns=False, justification='center', 
                num_rows=10, row_height=30, alternating_row_color='#e8f4f8', 
                text_color='#333333', font=('Helvetica', 12), key='data_table')]],
            title_color='#333333', relief=sg.RELIEF_GROOVE, pad=(10, 10))]
    ]

    # Bottom section: Exit button
    bottom_section = [
        [sg.Button("Exit", size=(10, 1), button_color=('white', '#F44336'), font=('Helvetica', 12))]
    ]

    # Combine all sections into the final layout
    layout = [
        header,
        top_buttons,
        middle_section,
        bottom_section
    ]

    return sg.Window("Finance Tracker", layout, size=(800, 600), element_justification='center', resizable=True, background_color='#f0f0f0', finalize=True)

# Open a window to add a new movement
def open_add_movement_window(movement_type: str, categories: list):
    if not categories:
        sg.popup("No categories defined. Please add a category first.", title="Error", keep_on_top=True)
        return None
    layout = [
        [sg.Text(f'Add {movement_type}', font=('Helvetica', 16, 'bold'), justification='center')],
        [sg.Text('Name:', size=(10, 1)), sg.InputText(key='name')],
        [sg.Text('Category:', size=(10, 1)), sg.Combo(categories, key='category', readonly=True)],
        [sg.Text('Amount:', size=(10, 1)), sg.InputText(key='amount')],
        [sg.Button("Submit", size=(10, 1)), sg.Button("Cancel", size=(10, 1))]
    ]
    window = sg.Window(f"Add {movement_type}", layout, modal=True)
    return window

# Open a window to add a new category
def open_add_category_window():
    layout = [
        [sg.Text('Add Category', font=('Helvetica', 16, 'bold'), justification='center')],
        [sg.Text('Category Name:', size=(15, 1)), sg.InputText(key='category_name')],
        [sg.Button("Submit", size=(10, 1)), sg.Button("Cancel", size=(10, 1))]
    ]
    window = sg.Window("Add Category", layout, modal=True)
    return window

# Open a window to remove a movement by name
def open_remove_movement_window():
    layout = [
        [sg.Text('Remove Movement', font=('Helvetica', 16, 'bold'), justification='center')],
        [sg.Text('Movement Name:', size=(15, 1)), sg.InputText(key='movement_name')],
        [sg.Button("Submit", size=(10, 1)), sg.Button("Cancel", size=(10, 1))]
    ]
    window = sg.Window("Remove Movement", layout, modal=True)
    return window

# Handle adding a new category
def handle_add_category(valid_categories):
    category_window = open_add_category_window()
    while True:
        cat_event, cat_values = category_window.read()
        if cat_event in (sg.WIN_CLOSED, 'Cancel'):
            category_window.close()
            break
        elif cat_event == 'Submit':
            category_name = cat_values['category_name'].strip()
            if category_name:
                valid_categories.append(category_name)
                sg.popup(f"Category '{category_name}' added successfully!", title="Success", keep_on_top=True)
                category_window.close()
                break
            else:
                sg.popup("Category name cannot be empty.", title="Error", keep_on_top=True)

# Handle adding a new movement
def handle_add_movement(event, window, finance_month, valid_categories):
    movement_type = 'Expense' if event == 'Add Expense' else 'Income'
    add_window = open_add_movement_window(movement_type, valid_categories)
    if add_window:
        while True:
            add_event, add_values = add_window.read()
            if add_event in (sg.WIN_CLOSED, 'Cancel'):
                add_window.close()
                break
            elif add_event == 'Submit':
                if add_values['category']:
                    try:
                        add_movement_to_finance_month(window, finance_month, add_values['name'], add_values['category'], movement_type, add_values['amount'])
                        export_data(finance_month)
                    except Exception as ex:
                        sg.popup(f"Failed to add movement or export data: {ex}", title="Error", keep_on_top=True)
                    add_window.close()
                    break
                else:
                    sg.popup("Please select a category.", title="Error", keep_on_top=True)

# Handle removing a movement
def handle_remove_movement(window, finance_month):
    remove_window = open_remove_movement_window()
    while True:
        remove_event, remove_values = remove_window.read()
        if remove_event in (sg.WIN_CLOSED, 'Cancel'):
            remove_window.close()
            break
        elif remove_event == 'Submit':
            movement_name = remove_values['movement_name'].strip()
            if movement_name:
                try:
                    movement_found = False
                    for movement in finance_month.movements:
                        if movement.name == movement_name:
                            finance_month.remove_movement(movement)
                            movement_found = True
                            break
                    if movement_found:
                        update_data_table(window, finance_month)
                        export_data(finance_month)
                        sg.popup(f"Movement '{movement_name}' removed successfully!", title="Success", keep_on_top=True)
                    else:
                        sg.popup(f"Movement '{movement_name}' not found.", title="Error", keep_on_top=True)
                except Exception as ex:
                    sg.popup(f"Failed to remove movement: {ex}", title="Error", keep_on_top=True)
                remove_window.close()
                break
            else:
                sg.popup("Movement name cannot be empty.", title="Error", keep_on_top=True)

# Execute the main window and handle events
def execute_main_window():
    # Create the main window
    window = create_main_window()
    finance_month = None  # Initialize FinanceMonth object outside the loop

    # Automatically load data from the default file
    try:
        finance_month = import_data()
        if finance_month:
            valid_categories.extend({movement.category for movement in finance_month.movements if movement.category})
            window['data_table'].update(values=finance_month.convert_to_list_of_list())
    except Exception as ex:
        sg.popup(f"Failed to load data: {ex}", title="Error", keep_on_top=True)

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event == 'Add Category':
            handle_add_category(valid_categories)
        elif event in ('Add Expense', 'Add Income'):
            handle_add_movement(event, window, finance_month, valid_categories)
        elif event == 'Remove Movement':
            handle_remove_movement(window, finance_month)
        else:
            sg.popup("Unexpected action.", title="Error", keep_on_top=True)

    window.close()
