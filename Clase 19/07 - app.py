# ============================================================
# EJEMPLO 07: Devolver una plantilla HTML (render_template)
# ------------------------------------------------------------
# En lugar de escribir el HTML dentro de Python, lo guardamos
# en archivos dentro de la carpeta 'templates/' y los mostramos
# con render_template.
# ============================================================

from flask import Flask, render_template

app = Flask(__name__)

app_titulo = 'Mi primera app con Flask'  # variable de ejemplo


@app.route('/')  # url: http://localhost:5000/
def inicio():
    app.logger.debug('Entramos al path de inicio /')
    # Busca y devuelve el archivo templates/index.html
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)