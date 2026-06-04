# Catalogoapp/pelicula.py


class Pelicula:
    """
    Modelo de datos que representa una película del catálogo.

    Evolución respecto a Clase 16:
    - Se agregaron los atributos 'director', 'anio' e 'id'.
    - El 'id' es asignado automáticamente por la base de datos (AUTOINCREMENT).
    - Los parámetros nuevos son opcionales (tienen valor por defecto None)
      para mantener compatibilidad y flexibilidad.
    """
    def __init__(self, nombre, director=None, anio=None, id=None):
        """
        Inicializa una instancia de Pelicula.

        Args:
            nombre (str): Título de la película. Campo obligatorio.
            director (str, opcional): Nombre del director. Por defecto None.
            anio (int, opcional): Año de estreno. Por defecto None.
            id (int, opcional): Identificador único en la base de datos.
                                 Lo asigna SQLite automáticamente al insertar.
        """
        self.id = id          # Clave primaria en la tabla 'peliculas'
        self.nombre = nombre
        self.director = director
        self.anio = anio

    def __str__(self):
        """Devuelve una representación legible de la película con todos sus datos."""
        return f"Pelicula({self.id}): {self.nombre} - {self.director} ({self.anio})"