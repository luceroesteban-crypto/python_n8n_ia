
# Abrir un archivo en modo escritura
print('*** Abrir un archivo en modo escritura ***')

with open("mi_archivo.txt", "w") as archivo:
    archivo.write("Hola, este es un archivo de texto creado desde Python.") 

print('Se ha creado el archivo mi_archivo.txt con éxito.')
