import sqlite3
from pelicula import Pelicula


class PeliculaDAO:
    """
    DAO (Data Access Object) para la entidad Pelicula.

    Concentra TODA la lógica de acceso a la base de datos SQLite,
    aislándola completamente de la lógica de negocio.
    De esta forma, si en el futuro se cambia el motor de base de datos
    (por ejemplo a PostgreSQL), solo se modifica esta clase.

    Archivo de base de datos: catalogo.db (se crea automáticamente).
    Tabla gestionada: peliculas (id, nombre, director, anio).
    """
    def __init__(self, db_name='catalogo.db'):
        """
        Args:
            db_name (str): Nombre del archivo de base de datos SQLite.
                           Se crea en el directorio actual si no existe.
        """
        self.db_name = db_name

    def _get_connection(self):
        """
        Crea y retorna una nueva conexión a la base de datos.
        El prefijo '_' indica que es un método de uso interno de la clase.
        Cada operación abre y cierra su propia conexión (patrón simple y seguro).
        """
        return sqlite3.connect(self.db_name)

    def inicializar_tabla(self):
        """
        Crea la tabla 'peliculas' si todavía no existe en la base de datos.
        Se llama una sola vez al iniciar la aplicación (desde ServicioPeliculas).
        Usa 'CREATE TABLE IF NOT EXISTS' para que sea seguro ejecutarlo
        múltiples veces sin errores.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS peliculas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                director TEXT,
                anio INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    def agregar(self, pelicula: Pelicula):
        """
        Inserta una nueva película en la base de datos.

        Los '?' en la consulta SQL son parámetros enlazados (parameterized query),
        lo que previene ataques de inyección SQL.
        El 'id' se omite porque SQLite lo genera automáticamente (AUTOINCREMENT).

        Args:
            pelicula (Pelicula): Objeto con los datos a persistir.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO peliculas (nombre, director, anio)
            VALUES (?, ?, ?)
        ''', (pelicula.nombre, pelicula.director, pelicula.anio))
        conn.commit()   # Confirma la transacción en la base de datos
        conn.close()

    def listar(self):
        """
        Recupera todas las películas almacenadas en la base de datos.

        Convierte cada fila de la tabla en un objeto Pelicula usando
        una list comprehension, manteniendo la separación entre la capa
        de datos (tuplas de SQLite) y el modelo de negocio (objetos Pelicula).

        Returns:
            list[Pelicula]: Lista con todas las películas. Lista vacía si no hay registros.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre, director, anio FROM peliculas')
        filas = cursor.fetchall()   # Trae todos los registros de una vez
        conn.close()
        # Mapea cada tupla (fila) a un objeto Pelicula con argumentos nombrados
        return [Pelicula(id=f[0], nombre=f[1], director=f[2], anio=f[3]) for f in filas]

    def eliminar(self, id_pelicula):
        """
        Elimina una película específica por su ID.

        Nota: Este método está disponible para usos futuros (por ejemplo,
        eliminar una sola película). La opción del menú actual usa
        'eliminar_catalogo' en ServicioPeliculas para borrar todos los registros.

        Args:
            id_pelicula (int): ID de la película a eliminar.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        # La coma en (id_pelicula,) es necesaria para que Python lo trate como tupla
        cursor.execute('DELETE FROM peliculas WHERE id = ?', (id_pelicula,))
        conn.commit()
        conn.close()
