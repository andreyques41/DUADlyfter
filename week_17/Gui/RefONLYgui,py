import FreeSimpleGUI as sg

counter = 0

# Declarar los elementos
layout = [
    [sg.Text("Haz click en lo que quieras hacer")],
    [sg.Text(counter, key="-COUNTER-")],
    [sg.Button("Sumar"), sg.Button("Restar")],
]

# Crear la ventana
window = sg.Window("Primer programa", layout)

# Event Loop para procesar "events" y obtener los "values" de los inputs
while True:
    event, values = window.read()
    # Procesar el evento del cerrar la ventaja
    # (si el usuario lo hace)
    if event == sg.WIN_CLOSED:
        break
    elif event == "Sumar":
        counter += 1
    elif event == "Restar":
        counter -= 1

    window["-COUNTER-"].update(counter)

window.close()