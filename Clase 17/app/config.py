# config.py
# Contiene las credenciales y la configuración de la base de datos.

# Diccionario de configuración para la conexión a MySQL.
# Buena práctica: centralizar los parámetros de conexión en un único lugar
# para no hardcodear credenciales dispersas en el código.
# En proyectos reales, estos valores se cargan desde variables de entorno
# o archivos .env para no exponerlos en el repositorio.
DB_CONFIG = {
    "host": "localhost",       # Servidor donde corre MySQL
    "user": "root",            # Usuario de MySQL
    "password": "root",        # Cambia esto por tu contraseña
    "database": "empresa_db"   # Nombre de la base de datos a usar/crear
}