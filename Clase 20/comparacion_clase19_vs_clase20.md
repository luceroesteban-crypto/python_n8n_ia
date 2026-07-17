# Comparación completa: ejemplo de la clase 19 vs ejemplo de la clase 20

Este documento compara el ejemplo de CRUD con Flask + SQLite de la clase 19 y el ejemplo mejorado de la clase 20.

## 1. Objetivo general

- Clase 19: mostrar de forma sencilla cómo crear una aplicación Flask que gestione clientes con SQLite.
- Clase 20: mantener el mismo objetivo, pero con una estructura más ordenada, más robusta y más preparada para proyectos reales.

## 2. Estructura del proyecto

### Clase 19

- archivo principal: 11 - clientesdb.py
- lógica SQL directamente dentro de las rutas
- base de datos gestionada en database.py
- esquema en schema.sql
- plantillas HTML para listar, crear y editar clientes

### Clase 20

- archivo principal: 11 - clientesdb.py
- lógica de acceso a datos separada en models/clientes.py
- base de datos gestionada en database.py
- esquema en schema.sql
- plantillas HTML similares a la clase 19

## 3. Organización del código

### Clase 19

El código principal contiene directamente las consultas SQL en cada ruta.

Ejemplo:

```python
cursor.execute('SELECT * FROM clientes')
```

Esto es muy útil para aprender, pero mezcla varias responsabilidades en el mismo archivo.

### Clase 20

El código principal usa métodos del modelo Clientes para interactuar con la base de datos.

Ejemplo:

```python
clientes = Clientes.listar_todos()
```

Esto hace que el archivo principal sea más limpio y fácil de leer.

## 4. Manejo de la base de datos

### Clase 19

- usa get_db() para obtener la conexión,
- crea la tabla al iniciar la app,
- inserta datos de ejemplo si la tabla está vacía,
- usa rutas relativas simples.

### Clase 20

- usa get_db() también,
- mejora la conexión con configuraciones de SQLite,
- crea un índice único sobre email,
- usa INSERT OR IGNORE para evitar duplicados,
- gestiona mejor la inicialización de la base.

## 5. Esquema de la base de datos

### Clase 19

```sql
DROP TABLE IF EXISTS clientes;

CREATE TABLE clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL,
    telefono TEXT NOT NULL
);
```

### Clase 20

```sql
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    telefono TEXT NOT NULL
);
```

### Diferencia clave

- La clase 19 borra la tabla si ya existe.
- La clase 20 no la borra y además obliga a que el email sea único.

## 6. Validaciones y comportamiento

### Clase 19

- valida que los campos no estén vacíos,
- inserta directamente en la base,
- muestra mensajes flash,
- no gestiona de forma especial la unicidad del email.

### Clase 20

- valida también los campos obligatorios,
- maneja errores como email duplicado,
- muestra mensajes flash más claros,
- evita insertar clientes con el mismo email.

## 7. Arquitectura

### Clase 19

Es una versión más directa y didáctica.

Ventajas:
- simple de entender,
- ideal para aprender SQL y Flask.

Desventajas:
- menos organizada,
- más difícil de escalar.

### Clase 20

Es una versión más profesional.

Ventajas:
- mejor separación de responsabilidades,
- menos repetición de código,
- más segura y mantenible.

Desventajas:
- un poco más compleja para quien está empezando.

## 8. Resumen final

| Aspecto | Clase 19 | Clase 20 |
|---|---|---|
| Objetivo | Enseñar CRUD básico | Enseñar CRUD con mejor estructura |
| Organización | Menos modular | Más modular |
| Lógica SQL | Dentro de las rutas | Separada en modelo |
| Seguridad | Básica | Mejorada |
| Unicidad de email | No aplicada | Aplicada |
| Escalabilidad | Limitada | Mayor |

## Conclusión

La clase 19 es excelente para aprender los fundamentos del CRUD con Flask y SQLite. La clase 20 mejora ese ejemplo al introducir una estructura más limpia, mejor separación de responsabilidades y mejores prácticas de base de datos.
