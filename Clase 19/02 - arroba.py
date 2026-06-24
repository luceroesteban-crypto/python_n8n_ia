# ============================================================
# EJEMPLO 02: La sintaxis @ (la manera corta)
# ------------------------------------------------------------
# Es exactamente lo mismo que el ejemplo 01, pero usando la
# notación @mi_decorador. Es la manera corta de escribir:
#     saludar = mi_decorador(saludar)
# Python hace esa línea por nosotros automáticamente.
# ============================================================

# Esta es nuestra función decoradora (idéntica a la del ejemplo 01).
def mi_decorador(funcion_original):
    # 1. Definimos una nueva función interna (el "papel de regalo").
    def funcion_envoltorio():
        print("--- Iniciando la ejecución ---")

        # 2. Llamamos a la función original que nos pasaron.
        funcion_original()

        print("--- Ejecución finalizada ---")

    # 3. La función decoradora devuelve la función envuelta.
    return funcion_envoltorio


# Usamos @ seguido del nombre del decorador, justo encima de la función.
# Esto aplica el decorador automáticamente al definir 'saludar'.
@mi_decorador
def saludar():
    print("¡Hola, mundo!")

# Ahora, al llamar a saludar, ya está decorada automáticamente.
saludar()