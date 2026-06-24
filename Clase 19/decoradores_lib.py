# ============================================================
# MÓDULO REUTILIZABLE DE DECORADORES
# ------------------------------------------------------------
# Aquí guardamos decoradores genéricos para importarlos desde
# cualquier otro archivo (ej.: 03 y 04 los usan).
# ============================================================

# Necesitamos 'time' para medir cuánto tarda una función.
import time


def mi_decorador(funcion_original):
    """Un decorador simple que muestra mensajes antes y después
    de ejecutar la función original.
    """
    def funcion_envoltorio():
        print("--- Iniciando la ejecución ---")
        funcion_original()
        print("--- Ejecución finalizada ---")
    return funcion_envoltorio


def medir_tiempo(func):
    """Decorador que mide y muestra el tiempo de ejecución de una función."""
    def envoltorio(*args, **kwargs):
        # *args y **kwargs permiten que el decorador funcione
        # con CUALQUIER función, sin importar sus argumentos.

        inicio = time.time()                 # marca de tiempo ANTES
        resultado = func(*args, **kwargs)     # ejecutamos la función original
        fin = time.time()                     # marca de tiempo DESPUÉS

        # Mostramos el nombre de la función y el tiempo transcurrido.
        print(f"La función '{func.__name__}' tardó {fin - inicio:.4f} segundos.")
        return resultado  # devolvemos lo que la función original devolvió
    return envoltorio
