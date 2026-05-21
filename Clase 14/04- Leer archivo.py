print('*** Abrir un archivo en modo lectura ***')

nombre_archivo = 'mi_archivo.txt'

with open(nombre_archivo, 'r') as archivo:
    contenido = archivo.read()
    print('Contenido del archivo:')
    print(contenido)
    
print(f'Se ha leído el archivo {nombre_archivo} con éxito.')











# Abrir un archivo en modo lectura con readline
# print('*** Abrir un archivo en modo lectura línea por línea ***')

# with open(nombre_archivo, 'r') as archivo:
#     for linea in archivo:
#         print(linea, end='')

# print(f'Se ha leído el archivo {nombre_archivo} con éxito.')

# Abrir un archivo en modo lectura con readlines
# print('*** Abrir un archivo en modo lectura con readlines ***')

# with open(nombre_archivo, 'r') as archivo:
#     lineas = archivo.readlines() # devuelve una lista de líneas
#     print('Contenido del archivo línea por línea:')
#     for linea in lineas:
#         print(linea, end='')

# print(f'Se ha leído el archivo {nombre_archivo} con éxito.')