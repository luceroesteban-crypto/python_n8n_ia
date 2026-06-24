-- ============================================================
-- ESQUEMA DE LA BASE DE DATOS (tabla de clientes)
-- ============================================================

-- Si la tabla ya existe, la borramos para empezar limpio.
DROP TABLE IF EXISTS clientes;

-- Creamos la tabla 'clientes' con sus columnas.
CREATE TABLE clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- identificador único automático
    nombre TEXT NOT NULL,                  -- nombre (obligatorio)
    email TEXT NOT NULL,                   -- email (obligatorio)
    telefono TEXT NOT NULL                 -- teléfono (obligatorio)
);