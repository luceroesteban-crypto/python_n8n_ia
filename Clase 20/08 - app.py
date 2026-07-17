# ============================================================
# EJEMPLO 08: Enviar variables de Python al HTML
# ------------------------------------------------------------
# render_template puede recibir variables (ej.: titulo=...).
# Dentro del HTML se usan con la sintaxis Jinja2: {{ titulo }}.
# ============================================================

from flask import Flask, render_template

app = Flask(__name__)

app_titulo = 'Mi primera app con Flask'

@app.route('/')  # url: http://localhost:5000/
def inicio():
    app.logger.debug('Entramos al path de inicio /')
     # Pasamos 'app_titulo' a la plantilla con el nombre 'titulo'.
    return render_template('index2.html', titulo=app_titulo)

if __name__ == '__main__':
    app.run(debug=True)