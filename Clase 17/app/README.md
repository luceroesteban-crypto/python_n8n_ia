# Gestor de Clientes con MySQL y Tkinter

Aplicación de escritorio con interfaz gráfica (GUI) que permite gestionar un
catálogo de clientes conectado a una base de datos **MySQL**.

---

## Qué hace la aplicación

- **Agregar** un nuevo cliente (nombre, email, teléfono)
- **Listar** todos los clientes en una tabla visual
- **Actualizar** los datos de un cliente seleccionado
- **Eliminar** un cliente con confirmación previa
- La base de datos y la tabla se **crean automáticamente** si no existen

---

## Requisitos previos

1. **Python 3.x** instalado
2. **MySQL Server** corriendo en `localhost`
3. Instalar la dependencia del proyecto:

```bash
pip install -r requirements.txt
```

> `requirements.txt` contiene: `mysql-connector-python==8.4`

---

## Configuración

Antes de ejecutar, editar `config.py` con las credenciales de tu servidor MySQL:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "TU_CONTRASEÑA",
    "database": "empresa_db"
}
```

La base de datos `empresa_db` y la tabla `clientes` se crean automáticamente
al iniciar la aplicación si no existen.

---

## Cómo ejecutar

```bash
python app.py
```

---

## Estructura del proyecto

```
app/
│
├── app.py            # Interfaz gráfica Tkinter + lógica de eventos
├── database.py       # DatabaseManager — CRUD completo con MySQL
├── config.py         # Credenciales y configuración de la base de datos
└── requirements.txt  # Dependencia: mysql-connector-python
```

---

## Arquitectura

```
App                  ← presentación (ventana Tkinter, botones, tabla visual)
    ↓
DatabaseManager      ← acceso a datos (conexión MySQL, queries SQL)
    ↓
MySQL (empresa_db)   ← base de datos con tabla 'clientes'
```

Cada capa tiene una única responsabilidad:
- **`App`** — solo gestiona la interfaz y los eventos del usuario.
- **`DatabaseManager`** — solo gestiona la comunicación con MySQL.
- **`config.py`** — centraliza las credenciales en un único lugar.

---

## Descripción de cada archivo

### `config.py` — Configuración centralizada

Contiene el diccionario `DB_CONFIG` con los parámetros de conexión a MySQL.
Separar la configuración del código es una buena práctica: si cambian las
credenciales, solo se modifica este archivo.

> En proyectos reales, estos valores se cargan desde variables de entorno
> o archivos `.env` para no exponerlos en el repositorio.

---

### `database.py` — `DatabaseManager`

Gestiona la conexión persistente y todas las operaciones CRUD:

| Método | Operación SQL | Descripción |
|---|---|---|
| `_initialize_database()` | `CREATE DATABASE` + `CREATE TABLE IF NOT EXISTS` | Se ejecuta al iniciar. Crea la BD y la tabla si no existen. |
| `connect()` | — | Establece `self.connection` usando `**config`. |
| `close()` | — | Cierra la conexión de forma segura al cerrar la ventana. |
| `fetch_all_clientes()` | `SELECT ... ORDER BY nombre` | Retorna lista de tuplas `(id, nombre, email, telefono)`. |
| `insert_cliente()` | `INSERT INTO` | Inserta un nuevo cliente. |
| `update_cliente()` | `UPDATE ... WHERE id` | Modifica un cliente existente por su id. |
| `delete_cliente()` | `DELETE WHERE id` | Elimina un cliente por su id. |

**Diferencias importantes respecto a SQLite (Clase 17 - Catalogoapp):**

| Aspecto | SQLite (`PeliculaDAO`) | MySQL (`DatabaseManager`) |
|---|---|---|
| Motor | Archivo local `.db` | Servidor externo |
| Placeholder en SQL | `?` | `%s` |
| Conexión | Abre/cierra por operación | Persistente (`self.connection`) |
| Crear BD | No aplica | `CREATE DATABASE IF NOT EXISTS` |
| Auto ID | `AUTOINCREMENT` | `AUTO_INCREMENT` |

---

### `app.py` — Interfaz Tkinter

Layout de la ventana con `grid`:

```
┌────────────────────────────────────────┐
│   Treeview — tabla de clientes         │  ← row=0, columnspan=2
├────────────────────────┬───────────────┤
│  Formulario            │   Botones     │  ← row=1
│  Nombre / Email /      │   Agregar     │
│  Teléfono              │   Actualizar  │
│                        │   Eliminar    │
│                        │   Limpiar     │
└────────────────────────┴───────────────┘
```

**Flujo de uso típico:**

1. La app carga y muestra todos los clientes en la tabla.
2. El usuario hace **clic en una fila** → los campos se rellenan automáticamente.
3. El usuario edita los campos y presiona **Actualizar** para guardar cambios.
4. Para **agregar**, limpia los campos, escribe los datos y presiona Agregar.
5. Para **eliminar**, selecciona una fila y presiona Eliminar → aparece un diálogo de confirmación.
6. Al cerrar la ventana (botón X), la conexión a MySQL se cierra correctamente.

**Métodos y su función:**

| Método | Descripción |
|---|---|
| `__init__()` | Configura ventana, inicia BD, construye widgets, carga datos. |
| `crear_widgets()` | Construye todo el layout: Treeview, inputs y botones. |
| `cargar_datos()` | Limpia el Treeview y lo repopula desde la BD. |
| `agregar_cliente()` | Valida nombre, inserta en BD, refresca tabla. |
| `actualizar_cliente()` | Requiere selección, actualiza en BD, refresca tabla. |
| `eliminar_cliente()` | Requiere selección, confirma con `askyesno`, elimina de BD. |
| `seleccionar_cliente()` | Evento de clic en tabla: rellena los campos del formulario. |
| `limpiar_campos()` | Vacía los tres Entry. Parámetro `deseleccionar` evita bucles. |
| `on_closing()` | Cierra conexión MySQL y destruye la ventana. |

---

## Conceptos clave

Esta aplicación introduce varios conceptos nuevos respecto a las clases anteriores:

1. **MySQL** como motor de base de datos (servidor externo vs. archivo local SQLite)
2. **Interfaz gráfica con Tkinter** — primera GUI del curso
3. **`ttk.Treeview`** — widget de tabla con filas y columnas seleccionables
4. **Conexión persistente** — `self.connection` se mantiene abierta durante toda la sesión
5. **Desempaquetado de diccionarios** — `connect(**self.config)` pasa el dict como argumentos
6. **Protocolo de cierre** — `WM_DELETE_WINDOW` para no dejar conexiones abiertas
7. **Confirmación antes de eliminar** — `messagebox.askyesno()` para operaciones destructivas
8. **Configuración centralizada** — `config.py` separado del código de la aplicación
