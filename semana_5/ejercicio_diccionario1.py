hotel = {}
hotel['nombre'] = 'Hilton'
hotel['numero_de_estrellas'] = 5
hotel['habitaciones'] = 100

print(hotel)

hotel = {}
hotel['nombre'] = 'Hilton'
hotel['numero_de_estrellas'] = 5
hotel['habitaciones'] = [
    {
        'numero': 101,
        'piso' : 1,
        'precio_por_noche': 100, 
    },
    {
        'numero': 102,
        'piso' : 1,
        'precio_por_noche': 120, 
    }
]

print(hotel)