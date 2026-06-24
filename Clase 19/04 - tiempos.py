# ============================================================
# EJEMPLO 04: Un decorador útil de verdad -> medir_tiempo
# ------------------------------------------------------------
# Aplicamos el decorador 'medir_tiempo' a varias funciones para
# saber cuánto tardan, sin tocar el código de cada función.
# ============================================================

import time                                   # para simular tareas con sleep
from decoradores_lib import medir_tiempo      # importamos nuestro decorador


@medir_tiempo
def proceso_largo(nombre):
    print(f"Iniciando proceso para {nombre}...")
    time.sleep(2)  # Simulamos una tarea que tarda 2 segundos
    print("Proceso completado.")
    return "Finalizado"  # esta función SÍ devuelve un valor


@medir_tiempo
def proceso_corto():
    time.sleep(0.5)  # tarea más corta (medio segundo)


# Llamamos a las funciones normalmente; el decorador mide el tiempo solo.
resultado_final = proceso_largo("archivos")
proceso_corto()

# El decorador devuelve el resultado original, por eso lo podemos imprimir.
print(f"El resultado fue: {resultado_final}")