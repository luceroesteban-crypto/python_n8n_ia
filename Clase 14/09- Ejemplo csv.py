# Crear un archivo CSV con al menos 5 personas (nombre y edad). 
# Luego, mostrar solo las mayores de 30 años.

import csv

# Lectura
with open('personas.csv') as archivo:
    lector = csv.reader(archivo)
    next(lector)  # Saltar encabezado
    for nombre, edad in lector:
        if int(edad) > 30:
            print(f"{nombre} tiene {edad} años")
print('Se ha leído el archivo personas.csv con éxito.')