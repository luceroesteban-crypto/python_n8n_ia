# =============================================================================
# config.py - Configuración Centralizada (Single Source of Truth)
# =============================================================================
#
# OBJETIVO PEDAGÓGICO:
#   Demostrar el patrón de configuración centralizada donde los parámetros
#   se definen UNA sola vez y se importan donde se necesiten.
#
# VENTAJAS DE ESTA APROXIMACIÓN:
#   - Single Source of Truth: cambiar en un lugar afecta a toda la aplicación
#   - No hardcodear credenciales dispersas en múltiples archivos
#   - Facilita cambiar entre entornos (dev, test, producción)
#   - Mejor mantenibilidad y menor riesgo de errores
#
# SEGURIDAD EN PROYECTOS REALES:
#   Este archivo es solo para DEMO EDUCATIVA. En producción NUNCA subir
#   credenciales a repositorios git. Usar variables de entorno o archivos .env
#   Ejemplo: os.environ.get('DB_PASSWORD') en lugar de texto plano
#
# USO:
#   from config import DB_CONFIG
#   db = mysql.connector.connect(**DB_CONFIG)  # Desempaquetado de diccionario
#
# =============================================================================

# Diccionario de configuración para la conexión a MySQL
DB_CONFIG = {
    "host": "localhost",       # Servidor donde corre MySQL (localhost = máquina local)
    "user": "root",            # Usuario de MySQL (root = administrador por defecto)
    "password": "root",        # Contraseña (⚠️ CAMBIAR en entornos reales)
    "database": "empresa_db"   # Nombre de la BD (se crea automáticamente si no existe)
}