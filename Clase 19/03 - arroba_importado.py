# ============================================================
# EJEMPLO 03: Reutilizar un decorador desde otro archivo
# ------------------------------------------------------------
# En proyectos reales los decoradores se guardan en un módulo
# aparte (decoradores_lib.py) y se importan donde se necesiten.
# ============================================================

# Importamos el decorador desde nuestro módulo de utilidades.
from decoradores_lib import mi_decorador


# Lo aplicamos igual que si estuviera definido en este archivo.
@mi_decorador
def saludar():
    print("¡Hola, mundo!")


# Este bloque solo se ejecuta si corremos ESTE archivo directamente,
# no cuando se importa desde otro módulo.
if __name__ == "__main__":
    saludar()
