# ============================================================
# MÓDULO DE BASE DE DATOS (usado por 11 - clientesdb.py)
# ------------------------------------------------------------
# Centraliza la conexión a SQLite y la creación inicial de la
# tabla. Así el archivo principal queda más limpio.
# ============================================================

import sqlite3
import os
from flask import g  # 'g' es un objeto temporal por cada petición

DATABASE = 'clientes.db'  # nombre del archivo de la base de datos


def get_db():
    """Devuelve la conexión a la base; la reutiliza durante la misma petición."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)   # abrimos la conexión
        # row_factory = Row permite acceder a las columnas por nombre (fila['nombre']).
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Cierra la conexión a la base de datos si estaba abierta."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Crea la tabla a partir de schema.sql y carga datos de ejemplo."""
    db = get_db()

    # Ejecutamos el script SQL que crea la tabla 'clientes'.
    with open('schema.sql', 'r') as f:
        db.executescript(f.read())

    # Verificamos si la tabla está vacía (cuántos registros hay).
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM clientes')
    count = cursor.fetchone()[0]

    if count == 0:
        # Si no hay clientes, insertamos algunos de ejemplo.
        cursor.executescript('''
            INSERT INTO clientes (nombre, email, telefono) VALUES
            ('Juan Pérez', 'juan@email.com', '555-0001'),
            ('María García', 'maria@email.com', '555-0002'),
            ('Carlos López', 'carlos@email.com', '555-0003');
        ''')
        db.commit()