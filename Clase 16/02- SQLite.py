import sqlite3

# 1. Conexión a la base de datos (se crea si no existe)
conn = sqlite3.connect("escuela.db")
cursor = conn.cursor()

# 2. Crear tabla
cursor.execute("""
CREATE TABLE IF NOT EXISTS estudiantes (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    edad INTEGER,
    curso TEXT
)
""")

# 3. Insertar datos 
cursor.executemany("""
INSERT INTO estudiantes (id, nombre, edad, curso)
VALUES (?, ?, ?, ?)
""", [
    (1, 'Ana', 20, 'Matemáticas'),
    (2, 'Juan', 22, 'Historia'),
    (3, 'Maria', 21, 'Física')
])

# # 4. Consultas
# print("Todos los estudiantes:")
# for fila in cursor.execute("SELECT * FROM estudiantes"):
#     print(fila)

# print("\nMayores de 20:")
# for fila in cursor.execute("SELECT * FROM estudiantes WHERE edad > 20"):
#     print(fila)

# # 5. Actualizar
# cursor.execute("UPDATE estudiantes SET curso = 'Literatura' WHERE nombre = 'Juan'")

# # 6. Eliminar
# cursor.execute("DELETE FROM estudiantes WHERE id = 3")

# # 7. Funciones agregadas
# cursor.execute("SELECT COUNT(*) FROM estudiantes")
# print("\nCantidad:", cursor.fetchone()[0])

# cursor.execute("SELECT AVG(edad) FROM estudiantes")
# print("Edad promedio:", cursor.fetchone()[0])

# 8. Confirmar cambios y cerrar
conn.commit()
conn.close()
