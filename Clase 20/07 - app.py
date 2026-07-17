# ============================================================
# EJEMPLO 07: Primera app web con Flask
# ------------------------------------------------------------
# Flask usa decoradores (@app.route) para asociar una URL con
# la función que debe responder cuando el usuario la visita.
# ============================================================

from flask import Flask

# Creamos la aplicación. __name__ ayuda a Flask a ubicar los archivos.
app = Flask(__name__)


@app.route('/')  # Asocia la ruta '/' (página principal) con esta función.
def inicio():
    app.logger.debug('Entramos al path de inicio /')  # mensaje de depuración
    return '<p>Hola Mundo</p>'  # lo que se envía al navegador (HTML)


# Arranca el servidor de desarrollo. debug=True recarga al guardar cambios
# y muestra errores detallados en el navegador.
if __name__ == '__main__':
    app.run(debug=True)