import csv

with open('personas.csv') as archivo:
    lector = csv.reader(archivo)
    for fila in lector:
        print(fila)
print('Se ha leído el archivo personas.csv con éxito.')