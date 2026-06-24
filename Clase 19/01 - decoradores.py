# ============================================================
# EJEMPLO 01: ¿Qué es un decorador? (forma manual, sin @)
# ------------------------------------------------------------
# Un decorador es una función que recibe OTRA función y le
# agrega comportamiento extra SIN modificar su código interno.
# Aquí lo hacemos "a mano" para entender la idea antes de usar @.
# ============================================================

# Función común y corriente que queremos "decorar".
def saludar():
    print("¡Hola, mundo!")


# Esta es nuestra función decoradora.
# Recibe como parámetro la función original que vamos a envolver.
def mi_decorador(funcion_original):
    # 1. Definimos una nueva función interna (el "papel de regalo")
    #    que contiene el comportamiento extra + la función original.
    def funcion_envoltorio():
        print("--- Iniciando la ejecución ---")  # se ejecuta ANTES

        # 2. Llamamos a la función original que nos pasaron.
        funcion_original()

        print("--- Ejecución finalizada ---")    # se ejecuta DESPUÉS

    # 3. La función decoradora NO ejecuta; DEVUELVE la función envuelta.
    return funcion_envoltorio


# Usamos el decorador de forma manual:
# reemplazamos 'saludar' por su versión decorada.
# (Descomenta la siguiente línea para ver la diferencia.)
#saludar = mi_decorador(saludar)

# Si la línea anterior está comentada -> imprime solo "¡Hola, mundo!".
# Si la descomentas -> imprime los mensajes de inicio y fin alrededor.
saludar()