# Catalogoapp/servicio_peliculas.py
from pelicula import Pelicula
from pelicula_dao import PeliculaDAO


class ServicioPeliculas:
    """
    Capa de lógica de negocio para la gestión del catálogo de películas.

    Evolución respecto a Clase 16:
    - Ya no maneja archivos .txt directamente.
    - Delega TODO el acceso a datos al objeto PeliculaDAO.
    - Aplica el principio de separación de responsabilidades:
        * ServicioPeliculas -> decide QUÉ hacer (lógica de negocio)
        * PeliculaDAO       -> decide CÓMO persistir (acceso a datos)
    """
    def __init__(self):
        """
        Instancia el DAO y garantiza que la tabla exista antes de operar.
        Se llama automáticamente al crear AppCatalogo.
        """
        self.dao = PeliculaDAO()         # Crea el objeto de acceso a datos
        self.dao.inicializar_tabla()     # Asegura que la tabla 'peliculas' exista

    def agregar_pelicula(self, pelicula):
        """
        Persiste una nueva película y confirma al usuario con un mensaje.

        Args:
            pelicula (Pelicula): Objeto con nombre, director y año a guardar.
        """
        self.dao.agregar(pelicula)
        print(f"Película '{pelicula.nombre}' agregada correctamente.")

    def listar_peliculas(self):
        """
        Recupera todas las películas desde la base de datos y las imprime.
        Cada película se muestra usando su método __str__ (definido en la clase Pelicula).
        """
        peliculas = self.dao.listar()    # Obtiene lista de objetos Pelicula desde el DAO
        print("--- Listado de películas: ---")
        for pelicula in peliculas:
            print(pelicula)             # Llama a Pelicula.__str__ implícitamente
        print("--- Fin del listado ---\n")

    def eliminar_catalogo(self):
        """
        Borra TODOS los registros de la tabla 'peliculas' sin eliminar la tabla.

        Diferencia clave con Clase 16:
        - Clase 16 eliminaba el archivo .txt completo (os.remove).
        - Clase 17 usa DELETE FROM, por lo que la tabla sigue existiendo
          y puede volver a usarse inmediatamente después.
        """
        # Elimina todas las películas de la tabla (la estructura de la tabla se conserva)
        from sqlite3 import connect
        conn = connect(self.dao.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM peliculas")
        conn.commit()
        conn.close()
        print("Catálogo de películas eliminado.")
