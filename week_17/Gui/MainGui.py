import FreeSimpleGUI as sg

# Declarar los elementos
layout = [
    [sg.Text("Ingreso de finanzas")],
    [sg.Input('Monto', key="monto")],
    [sg.Button("Sumar"), sg.Button("Restar")],
]

# Crear la ventana
window = sg.Window("Primer programa", layout)

# Event Loop para procesar "events" y obtener los "values" de los inputs
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

window.close()