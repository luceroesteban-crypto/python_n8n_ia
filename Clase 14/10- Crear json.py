import json

usuario = {"nombre": "Omar", "edad": 35}
with open('usuario.json', 'w') as archivo:
    json.dump(usuario, archivo)
print('Se ha creado el archivo usuario.json con éxito.')