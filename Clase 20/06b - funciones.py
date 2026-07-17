# Desempaquetado de tuplas
# En Python, una tupla puede contener varios valores a la vez.
# Cuando asignamos esa tupla a varias variables, Python separa
# automáticamente cada valor en su variable correspondiente.
# Ejemplo:
# datos = ("Ana", 30, "Buenos Aires")
# nombre, edad, ciudad = datos
# print(nombre, edad, ciudad)

# En este ejemplo, cada elemento devuelto por kwargs.items() es una tupla
# con dos valores: (clave, valor). Gracias al desempaquetado, podemos
# asignarlos directamente a las variables clave y valor en el bucle.

def mostrar_info_usuario(**kwargs):
    """Muestra la información de un usuario pasada como argumentos de palabra clave."""
    print("Detalles del usuario:")
    # kwargs es un diccionario, por lo que podemos usar .items() para iterarlo
    for clave, valor in kwargs.items():
        print(f"- {clave.capitalize()}: {valor}")

# Probemos la función
mostrar_info_usuario(nombre="Ana", edad=30, ciudad="Buenos Aires")
print("-" * 20)
mostrar_info_usuario(usuario="juan_perez", email="juan@example.com", activo=True)