import json

with open('usuario.json', 'r') as archivo:
    datos = json.load(archivo)
    print(datos)
    print(f"Nombre: {datos['nombre']}, Edad: {datos['edad']}")

print('Se ha leído el archivo usuario.json con éxito.')    
