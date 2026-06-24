# ============================================================
# EJEMPLO 11: CRUD completo con Flask + SQLite
# ------------------------------------------------------------
# CRUD = Crear, Leer (Read), Actualizar (Update) y Eliminar (Delete).
# Aquí conectamos Flask a una base de datos SQLite para gestionar
# clientes desde el navegador con formularios.
# ============================================================

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from database import get_db, init_db  # funciones auxiliares de database.py

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Necesario para los mensajes flash (avisos)

# Inicializamos la base de datos al arrancar (crea la tabla y datos de ejemplo).
with app.app_context():
    init_db()


# ---------- LEER: mostrar la lista de clientes ----------
@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM clientes')   # traemos todos los clientes
    clientes = cursor.fetchall()               # lista de filas resultantes
    return render_template('clientes/listar_clientes.html', clientes=clientes)

# ---------- CREAR: alta de un nuevo cliente ----------
@app.route('/crear', methods=['GET', 'POST'])
def crear():
    # POST = el usuario envió el formulario; GET = solo muestra el formulario.
    if request.method == 'POST':
        # Leemos los datos escritos en el formulario.
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']

        if not nombre or not email or not telefono:
            flash('Todos los campos son requeridos', 'error')  # validación simple
        else:
            db = get_db()
            cursor = db.cursor()
            # Usamos ? para evitar inyección SQL (forma segura de insertar datos).
            cursor.execute(
                'INSERT INTO clientes (nombre, email, telefono) VALUES (?, ?, ?)',
                (nombre, email, telefono)
            )
            db.commit()  # confirmamos (guardamos) el cambio en la base
            flash('Cliente creado exitosamente', 'success')
            return redirect(url_for('index'))  # volvemos a la lista

    return render_template('clientes/crear_cliente.html')

# ---------- ACTUALIZAR: editar un cliente existente ----------
# <int:id> captura el número de la URL (ej.: /editar/3) y lo pasa como 'id'.
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        # El usuario guardó cambios: actualizamos el registro.
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']

        if not nombre or not email or not telefono:
            flash('Todos los campos son requeridos', 'error')
        else:
            cursor.execute(
                'UPDATE clientes SET nombre = ?, email = ?, telefono = ? WHERE id = ?',
                (nombre, email, telefono, id)
            )
            db.commit()
            flash('Cliente actualizado exitosamente', 'success')
            return redirect(url_for('index'))

    # Si es GET: buscamos el cliente actual para rellenar el formulario.
    cursor.execute('SELECT * FROM clientes WHERE id = ?', (id,))
    cliente = cursor.fetchone()  # una sola fila
    return render_template('clientes/editar_cliente.html', cliente=cliente)

# ---------- ELIMINAR: borrar un cliente ----------
@app.route('/eliminar/<int:id>')
def eliminar(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM clientes WHERE id = ?', (id,))  # borra por id
    db.commit()
    flash('Cliente eliminado exitosamente', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)