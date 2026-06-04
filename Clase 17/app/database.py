# database.py
# Gestiona la conexión y las operaciones CRUD con la base de datos MySQL.

import mysql.connector
from mysql.connector import Error
from tkinter import messagebox


class DatabaseManager:
    """
    Gestiona la conexión y todas las operaciones CRUD sobre la tabla 'clientes' en MySQL.

    Diferencias clave respecto a PeliculaDAO (SQLite - Clase 17 Catalogoapp):
    - Usa MySQL como motor (servidor externo, requiere estar corriendo).
    - Mantiene una conexión PERSISTENTE (self.connection) en lugar de
      abrir y cerrar la conexión en cada operación.
    - Usa %s como placeholder en las queries (sintaxis MySQL), no '?'.
    - Crea la base de datos automáticamente si no existe (CREATE DATABASE).
    - Los errores se muestran en ventanas emergentes (messagebox) en lugar
      de lanzar excepciones, ya que la app tiene interfaz gráfica.
    """
    def __init__(self, config):
        """
        Inicializa el gestor con la configuración de conexión y prepara la BD.

        Args:
            config (dict): Diccionario con host, user, password y database.
                           Generalmente se pasa DB_CONFIG desde config.py.
        """
        self.config = config
        self.connection = None  # Se establece en _initialize_database()
        self._initialize_database()

    def _initialize_database(self):
        """
        Crea la base de datos y la tabla 'clientes' si no existen. Se ejecuta al inicio.

        Proceso en dos pasos:
        1. Conecta a MySQL SIN especificar base de datos, para poder crearla.
        2. Conecta ya a la base de datos creada y crea la tabla si no existe.

        El prefijo '_' indica que es un método de uso interno de la clase.
        Si falla (MySQL no está corriendo, credenciales incorrectas, etc.),
        muestra un messagebox y self.connection queda en None.
        """
        try:
            # Paso 1: conectar sin base de datos para poder crearla
            db = mysql.connector.connect(
                host=self.config["host"],
                user=self.config["user"],
                password=self.config["password"]
            )
            cursor = db.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            cursor.close()
            db.close()  # Cierra esta conexión temporal
            
            # Paso 2: conectar ahora con la base de datos ya creada
            self.connect()
            cursor = self.connection.cursor()
            
            # Crea la tabla si no existe, con id autoincrementable como clave primaria
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    telefono VARCHAR(50)
                )
            """)
            self.connection.commit()
            cursor.close()
            print("Base de datos y tabla verificadas/creadas correctamente.")

        except Error as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudo inicializar la base de datos: {e}")

    def connect(self):
        """
        Establece la conexión persistente con la base de datos MySQL.
        Usa el operador ** para desempaquetar el diccionario DB_CONFIG como argumentos.
        Si falla, self.connection queda en None y los métodos CRUD verifican esto
        antes de operar (patrón 'if not self.connection: return ...').
        """
        try:
            self.connection = mysql.connector.connect(**self.config)  # Desempaqueta el dict de config
        except Error as e:
            messagebox.showerror("Error de Conexión", f"Error al conectar a MySQL: {e}")
            self.connection = None

    def close(self):
        """
        Cierra la conexión a MySQL de forma segura.
        Se llama desde App.on_closing() al cerrar la ventana,
        garantizando que no queden conexiones abiertas al servidor.
        Verifica is_connected() para evitar errores si ya estaba cerrada.
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexión a la base de datos cerrada.")

    def fetch_all_clientes(self):
        """
        Obtiene todos los clientes de la tabla ordenados alfabéticamente por nombre.

        Returns:
            list[tuple]: Lista de tuplas (id, nombre, email, telefono).
                         Lista vacía si no hay registros o hay error de conexión.
        """
        if not self.connection: return []  # Conexión no disponible, retorna lista vacía
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id, nombre, email, telefono FROM clientes ORDER BY nombre")
            records = cursor.fetchall()  # Trae todos los registros en memoria
            cursor.close()
            return records
        except Error as e:
            messagebox.showerror("Error de Lectura", f"No se pudieron cargar los clientes: {e}")
            return []

    def insert_cliente(self, nombre, email, telefono):
        """
        Inserta un nuevo cliente en la tabla.

        Usa %s como placeholder (sintaxis de MySQL, distinto al '?' de SQLite).
        El id se omite porque MySQL lo asigna automáticamente (AUTO_INCREMENT).

        Args:
            nombre (str): Nombre del cliente. Campo obligatorio.
            email (str): Correo electrónico. Puede estar vacío.
            telefono (str): Número de teléfono. Puede estar vacío.

        Returns:
            bool: True si la inserción fue exitosa, False si hubo un error.
        """
        if not self.connection: return False
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO clientes (nombre, email, telefono) VALUES (%s, %s, %s)"
            cursor.execute(query, (nombre, email, telefono))  # Parámetros enlazados, previenen inyección SQL
            self.connection.commit()  # Confirma la transacción
            cursor.close()
            return True
        except Error as e:
            messagebox.showerror("Error de Inserción", f"No se pudo agregar el cliente: {e}")
            return False

    def update_cliente(self, client_id, nombre, email, telefono):
        """
        Actualiza los datos de un cliente existente identificado por su id.

        El id va al FINAL de la tupla de parámetros porque en la query SQL
        aparece en la cláusula WHERE, que está al final de la sentencia.

        Args:
            client_id (int): ID del cliente a modificar.
            nombre (str): Nuevo nombre.
            email (str): Nuevo email.
            telefono (str): Nuevo teléfono.

        Returns:
            bool: True si la actualización fue exitosa, False si hubo un error.
        """
        if not self.connection: return False
        try:
            cursor = self.connection.cursor()
            query = "UPDATE clientes SET nombre = %s, email = %s, telefono = %s WHERE id = %s"
            cursor.execute(query, (nombre, email, telefono, client_id))  # client_id al final (cláusula WHERE)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            messagebox.showerror("Error de Actualización", f"No se pudo actualizar el cliente: {e}")
            return False

    def delete_cliente(self, client_id):
        """
        Elimina un cliente de la tabla por su id.

        Nota: (client_id,) lleva una coma para que Python lo interprete
        como una tupla de un elemento, que es lo que espera cursor.execute().

        Args:
            client_id (int): ID del cliente a eliminar.

        Returns:
            bool: True si la eliminación fue exitosa, False si hubo un error.
        """
        if not self.connection: return False
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM clientes WHERE id = %s"
            cursor.execute(query, (client_id,))  # La coma hace que sea una tupla, no un entero
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            messagebox.showerror("Error de Eliminación", f"No se pudo eliminar el cliente: {e}")
            return False