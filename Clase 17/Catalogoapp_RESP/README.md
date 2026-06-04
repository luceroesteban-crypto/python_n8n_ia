# Catálogo de Películas — Solución Clase 17

Solución al ejercicio **"Catálogo de Películas con SQLite y el Patrón DAO"**.  
Esta aplicación es la evolución directa del proyecto desarrollado en Clase 16.

---

## Qué hace la aplicación

Gestiona un catálogo de películas desde la consola, permitiendo:

1. **Agregar** una película (nombre, director y año)
2. **Listar** todas las películas almacenadas
3. **Eliminar** todos los registros del catálogo
4. **Salir** de la aplicación

Los datos se persisten en una base de datos SQLite (`catalogo.db`) que se crea automáticamente al ejecutar el programa.

---

## Cómo ejecutar

```bash
python app_catalogo.py
```

> No requiere instalación de librerías externas. `sqlite3` viene incluido en Python.

---

## Estructura del proyecto

```
Catalogoapp_RESP/
│
├── app_catalogo.py       # Capa de presentación: menú e interacción con el usuario
├── servicio_peliculas.py # Capa de lógica de negocio
├── pelicula_dao.py       # Capa de acceso a datos (patrón DAO) — NUEVO en Clase 17
├── pelicula.py           # Modelo de datos (clase Pelicula)
└── catalogo.db           # Base de datos SQLite (se genera al ejecutar)
```

---

## Arquitectura en capas

```
AppCatalogo          ← presentación (menú, input del usuario)
     ↓
ServicioPeliculas    ← lógica de negocio (qué operaciones se pueden hacer)
     ↓
PeliculaDAO          ← acceso a datos (cómo se persiste en SQLite)
     ↓
SQLite (catalogo.db) ← base de datos
```

Cada capa **solo conoce a la capa inmediatamente inferior**, nunca salta niveles.

---

## Patrón DAO (Data Access Object)

El patrón DAO consiste en crear una clase cuya **única responsabilidad** es el acceso a la base de datos. Esto permite:

- **Cambiar el motor de BD** (por ejemplo, de SQLite a PostgreSQL) modificando solo `pelicula_dao.py`, sin tocar el resto del código.
- **Testear** la lógica de negocio de forma independiente al almacenamiento.
- **Código más limpio**: cada clase tiene una sola razón para cambiar.

---

## Evolución respecto a Clase 16

| Aspecto | Clase 16 | Clase 17 (esta solución) |
|---|---|---|
| **Persistencia** | Archivo de texto `.txt` | Base de datos SQLite `.db` |
| **Estructura** | 3 archivos | 4 archivos (se agrega `pelicula_dao.py`) |
| **Clase Pelicula** | Solo atributo `nombre` | `id`, `nombre`, `director`, `anio` |
| **Acceso a datos** | Directamente en `ServicioPeliculas` | Delegado al `PeliculaDAO` |
| **Eliminar catálogo** | `os.remove()` — borra el archivo | `DELETE FROM peliculas` — borra los datos, la tabla persiste |
| **Agregar película** | Solo pide nombre | Pide nombre, director y año |
| **ID automático** | No existía | SQLite lo genera con `AUTOINCREMENT` |

---

## Descripción de cada archivo

### `pelicula.py` — Modelo de datos

Clase que representa una película. Contiene los atributos `id`, `nombre`, `director` y `anio`.  
El `id` es asignado automáticamente por la base de datos al insertar.

```python
pelicula = Pelicula(nombre="Inception", director="Nolan", anio=2010)
```

---

### `pelicula_dao.py` — Acceso a datos *(nuevo en Clase 17)*

Encapsula todas las operaciones SQL sobre la tabla `peliculas`:

| Método | Operación SQL |
|---|---|
| `inicializar_tabla()` | `CREATE TABLE IF NOT EXISTS` |
| `agregar(pelicula)` | `INSERT INTO` |
| `listar()` | `SELECT` → retorna lista de objetos `Pelicula` |
| `eliminar(id_pelicula)` | `DELETE WHERE id = ?` |

Usa **parámetros enlazados** (`?`) para prevenir inyección SQL.

---

### `servicio_peliculas.py` — Lógica de negocio

Orquesta las operaciones del catálogo delegando al DAO. No contiene SQL directo  
(excepto `eliminar_catalogo`, que podría refactorizarse al DAO como mejora futura).

---

### `app_catalogo.py` — Presentación y menú

Bucle principal `while True` con manejo de errores en dos niveles:
- **Error en opción del menú**: `ValueError` si el usuario escribe texto.
- **Error en el año**: si no es un número, se guarda como `None` en lugar de lanzar excepción.
- **Error general**: `except Exception` captura fallos inesperados de la base de datos.

---

## Puntos extra resueltos

- ✅ Clase `Pelicula` con todos los atributos necesarios (`id`, `nombre`, `director`, `anio`)
- ✅ Manejo de errores de entrada (año inválido → `None`) y de acceso a la BD (`except Exception`)
