import csv

with open('personas.csv', 'w', newline='') as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow(['Nombre', 'Edad'])
    escritor.writerow(['Omar', 35])
    escritor.writerow(['Ana', 28])
print('Se ha creado el archivo personas.csv con éxito.')