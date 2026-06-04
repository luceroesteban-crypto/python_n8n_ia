from pelicula import Pelicula
from servicio_peliculas import ServicioPeliculas


class AppCatalogo:
    """
    Punto de entrada y capa de presentación de la aplicación.

    Responsabilidad única: interactuar con el usuario (mostrar menú,
    leer entradas, delegar operaciones al ServicioPeliculas).
    No contiene lógica de negocio ni acceso directo a datos.

    Arquitectura en capas de esta solución:
        AppCatalogo (presentación)
            ↓
        ServicioPeliculas (lógica de negocio)
            ↓
        PeliculaDAO (acceso a datos / SQLite)
    """
    def __init__(self):
        """Inicializa la aplicación creando el servicio (que a su vez inicializa la BD)."""
        self.servicio_peliculas = ServicioPeliculas()

    def mostrar_menu(self):
        """
        Muestra el menú interactivo en un bucle hasta que el usuario elige Salir.

        Manejo de errores implementado:
        - ValueError en la opción del menú: el usuario ingresó texto en vez de número.
        - ValueError en el año: se acepta el ingreso pero se guarda como None.
        - Exception general: captura cualquier error inesperado (por ej. fallo de BD).
        """
        print("*** Bienvenido al Catálogo de Películas ***\n")
        while True:
            try:
                print(f"=== MENU ===\n"
                      f"1. Agregar película\n"
                      f"2. Listar películas\n"
                      f"3. Eliminar datos del catálogo\n"
                      f"4. Salir\n")
                
                opcion = int(input("Seleccione una opción (1-4): "))
                if opcion == 1:
                    nombre_pelicula = input("Ingrese el nombre de la película: ")
                    director = input("Ingrese el director: ")
                    anio = input("Ingrese el año: ")
                    try:
                        anio = int(anio)    # Intenta convertir el año a entero
                    except ValueError:
                        anio = None         # Si no es un número válido, se guarda como None
                    pelicula = Pelicula(nombre=nombre_pelicula, director=director, anio=anio)
                    self.servicio_peliculas.agregar_pelicula(pelicula)
                elif opcion == 2:
                    self.servicio_peliculas.listar_peliculas()
                elif opcion == 3:
                    self.servicio_peliculas.eliminar_catalogo()
                    print("Catálogo de películas eliminado.\n")
                elif opcion == 4:
                    print("Saliendo del catálogo...")
                    break
                else:
                    print("Opción no válida. Intente de nuevo.\n")
            except ValueError:
                print("Por favor, ingrese un número válido.\n")        
            except Exception as e:
                print(f"Error al mostrar el menú: {e}\n")

if __name__ == "__main__":
    app = AppCatalogo()
    app.mostrar_menu()
   
