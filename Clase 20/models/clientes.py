# ============================================================
# MODELO DE CLIENTES
# ------------------------------------------------------------
# Este archivo contiene la lógica de acceso a datos para la tabla
# clientes. Sirve como capa intermedia entre Flask y SQLite.
# ============================================================

import sqlite3
from typing import Optional, List

from database import get_db


class Clientes:
    """Capa de acceso a datos para la tabla clientes."""

    # @staticmethod indica que este método se puede llamar desde la clase
    # sin necesidad de crear una instancia. Es útil para operaciones que no
    # dependen de atributos de un objeto concreto, como consultar o modificar
    # la base de datos desde el modelo.
    @staticmethod
    def listar_todos() -> List[sqlite3.Row]:
        """Devuelve todos los clientes ordenados por id de forma descendente."""
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT * FROM clientes ORDER BY id DESC')
        return cur.fetchall()

    @staticmethod
    def obtener_por_id(cliente_id: int) -> Optional[sqlite3.Row]:
        """Busca un cliente por su identificador y devuelve una fila si existe."""
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,))
        return cur.fetchone()

    @staticmethod
    def crear(nombre: str, email: str, telefono: str) -> int:
        """Inserta un nuevo cliente en la base de datos y devuelve su id."""
        db = get_db()
        cur = db.cursor()
        cur.execute(
            'INSERT INTO clientes (nombre, email, telefono) VALUES (?, ?, ?)',
            (nombre, email, telefono)
        )
        db.commit()
        return cur.lastrowid

    @staticmethod
    def actualizar(cliente_id: int, nombre: str, email: str, telefono: str) -> int:
        """Actualiza los datos de un cliente existente y devuelve cuántas filas cambió."""
        db = get_db()
        cur = db.cursor()
        cur.execute(
            'UPDATE clientes SET nombre = ?, email = ?, telefono = ? WHERE id = ?',
            (nombre, email, telefono, cliente_id)
        )
        db.commit()
        return cur.rowcount

    @staticmethod
    def eliminar(cliente_id: int) -> int:
        """Elimina un cliente por su id y devuelve cuántas filas se borraron."""
        db = get_db()
        cur = db.cursor()
        cur.execute('DELETE FROM clientes WHERE id = ?', (cliente_id,))
        db.commit()
        return cur.rowcount
