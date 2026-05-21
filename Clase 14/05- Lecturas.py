# Modos de apertura de archivos
# 'r' - lectura (por defecto)     

# abrir un archivo para leerlo completo (read)
with open('mi_archivo.txt', 'r') as f:
    contenido = f.read()        # Lee todo
    
# abrir un archivo para leerlo línea por línea (readlines)
with open('mi_archivo.txt', 'r') as f:    
    lineas = f.readlines()  # Devuelve una lista de líneas

    for linea in lineas:
        print(linea.strip()) # strip() elimina espacios en blanco y saltos de línea

# abrir un archivo para leer una línea a la vez (readline)
with open('mi_archivo.txt', 'r') as f:
    while True:
        linea = f.readline()
        if not linea:
            break
        print(linea.strip())
