-- ============================================================
-- ESQUEMA DE LA BASE DE DATOS (tabla de clientes)
-- ============================================================

-- Si la tabla ya existe, no la volvemos a crear.
-- Esto permite reutilizar la base sin perder datos.
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- identificador único automático
    nombre TEXT NOT NULL,                  -- nombre (obligatorio)
    email TEXT NOT NULL UNIQUE,            -- email (obligatorio y único)
    telefono TEXT NOT NULL                 -- teléfono (obligatorio)
);