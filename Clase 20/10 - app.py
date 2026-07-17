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
    # Renderiza las filas usando Jinja2 y las devuelve como HTML.
    datos = cargar_clientes()
    return render_template('clientes_tabla.html', clientes=datos.get('clientes', []))


@app.route('/api/cliente-detalle/<int:cliente_id>')
def get_cliente_detalle(cliente_id):
    # Renderiza el contenido del modal usando Jinja2 y lo devuelve como HTML.
    datos = cargar_clientes()
    cliente = next((c for c in datos.get('clientes', []) if c['id'] == cliente_id), None)
    if cliente is None:
        return "Cliente no encontrado", 404
    return render_template('cliente_modal.html', cliente=cliente)


if __name__ == '__main__':
    app.run(debug=True)