# ============================================================
# MÓDULO DE BASE DE DATOS (usado por 11 - clientesdb.py)
# ------------------------------------------------------------
# Centraliza la conexión a SQLite y la creación inicial de la
# tabla. También mejora la gestión de la base para proyectos
# más robustos y con mejor concurrencia.
# ============================================================

import sqlite3
import os
from flask import g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'clientes.db')


def get_db():
    """Devuelve la conexión a la base; la reutiliza durante la misma petición."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)  # abrimos la conexión
        # row_factory = Row permite acceder a las columnas por nombre (fila['nombre']).
        g.db.row_factory = sqlite3.Row
        # Mejorar concurrencia de SQLite con múltiples procesos
        g.db.execute('PRAGMA journal_mode=WAL;')
        g.db.execute('PRAGMA synchronous=NORMAL;')
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
    schema_path = os.path.join(BASE_DIR, 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())

    # Asegurar unicidad de email también en bases existentes
    db.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_clientes_email ON clientes(email);')

    # Inserción idempotente y segura ante concurrencia gracias a UNIQUE(email)
    cursor = db.cursor()
    cursor.executescript('''
        INSERT OR IGNORE INTO clientes (nombre, email, telefono) VALUES
        ('Juan Pérez', 'juan@email.com', '555-0001'),
        ('María García', 'maria@email.com', '555-0002'),
        ('Carlos López', 'carlos@email.com', '555-0003');
    ''')
    db.commit()