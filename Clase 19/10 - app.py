# ============================================================
# EJEMPLO 10: Leer datos de un archivo JSON y crear una API
# ------------------------------------------------------------
# La página '/' muestra el HTML y la ruta '/api/clientes'
# devuelve los datos en formato JSON (útil para JavaScript).
# ============================================================

from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)


def cargar_clientes():
    """Lee el archivo clientes.json y devuelve su contenido."""
    try:
        with open('clientes.json', 'r', encoding='utf-8') as archivo:
            return json.load(archivo)  # convierte el JSON a diccionario Python
    except FileNotFoundError:
        # Si el archivo no existe, devolvemos una lista vacía para no romper.
        return {"clientes": []}


@app.route('/')
def index():
    # Página principal: muestra la plantilla HTML.
    return render_template('clientes.html')


@app.route('/api/clientes')
def get_clientes():
    # Endpoint tipo API: devuelve los datos en JSON.
    datos = cargar_clientes()
    return jsonify(datos)  # jsonify convierte el diccionario en respuesta JSON


if __name__ == '__main__':
    app.run(debug=True)