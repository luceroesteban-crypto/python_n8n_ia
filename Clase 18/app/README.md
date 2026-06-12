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
├── styles.py         # StyleManager — estilos TTK centralizados
├── clientes.json     # Archivo de ejemplo para importación
├── icono.ico         # Icono de la aplicación
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

Layout de la ventana con `grid` (optimizado para más espacio en la tabla):

```
┌───────────────────────────────────────────────────────────┐
│                                                           │
│              Treeview — tabla de clientes                 │  ← row=0, 70%
│                 (más alta, ordenable por clic)            │
│                                                           │
├───────────────────────────────────────────────────────────┤
│  ┌─ Datos del Cliente ────────────────────────────────┐   │  ← row=1
│  │  Nombre: [________]  Email: [________]            │   │
│  │  Teléfono: [________]                              │   │
│  │                                                    │   │
│  │  [➕ Agregar]  [📝 Actualizar]  [🗑️ Eliminar]  [🧹 Limpiar] │   │
│  └────────────────────────────────────────────────────┘   │
├───────────────────────────────────────────────────────────┤
│              [🔄 Recargar Datos]  [📥 Importar JSON]      │  ← row=2
├───────────────────────────────────────────────────────────┤
│    🟢 Conectado a MySQL        │       📋 36 clientes     │  ← row=3
└───────────────────────────────────────────────────────────┘
```

**Flujo de uso típico:**

1. La app carga y muestra todos los clientes ordenados por nombre.
2. El usuario hace **clic en una fila** → los campos se rellenan automáticamente.
3. El usuario hace **clic en los encabezados** (ID, Nombre, Email, Teléfono) para ordenar la tabla (↑ ascendente, ↓ descendente).
4. El usuario edita los campos y presiona **Actualizar** para guardar cambios.
5. Para **agregar**, limpia los campos, escribe los datos y presiona Agregar.
6. Para **eliminar**, selecciona una fila y presiona Eliminar → aparece un diálogo de confirmación.
7. **Recargar** refresca los datos y resetea el ordenamiento al valor por defecto (nombre ascendente).
8. Al cerrar la ventana (botón X), la conexión a MySQL se cierra correctamente.

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
| `crear_barra_estado()` | Crea la barra inferior con estado de conexión. |
| `actualizar_barra_estado()` | Actualiza indicadores de conexión y contador. |
| `importar_json()` | Abre diálogo para importar clientes desde JSON. |
| `recargar_datos()` | Recarga datos y resetea ordenamiento al valor por defecto. |
| `ordenar_por(columna)` | Ordena la tabla por la columna clickeada (ASC/DESC). |

---

## Estilos y UI Moderna

La aplicación utiliza **estilos TTK personalizados** para una apariencia moderna y profesional.

### Tema y Paleta de Colores

- **Tema TTK**: `clam` (más limpio que el tema por defecto)
- **Paleta Material Design**:
  - 🔵 **Primario**: `#2196F3` (azul)
  - 🟢 **Éxito**: `#4CAF50` (verde)
  - 🔴 **Peligro**: `#F44336` (rojo)
  - ⚪ **Neutro**: `#757575` (gris)

### Estilos Personalizados

| Estilo | Aplicado a | Características |
|--------|------------|-----------------|
| `Card.TLabelframe` | Frame de datos | Fondo gris claro, borde sutil, título destacado |
| `Success.TButton` | Botón Agregar | Verde con efectos hover/pressed |
| `Primary.TButton` | Botón Actualizar | Azul con efectos hover/pressed |
| `Danger.TButton` | Botón Eliminar | Rojo con efectos hover/pressed |
| `Neutral.TButton` | Botón Limpiar | Gris con efectos hover/pressed |
| `Modern.Treeview` | Tabla de clientes | Encabezado azul, filas altas (28px), fuente Segoe UI |
| `Modern.TEntry` | Campos de input | Padding interno, fuente moderna |
| `Modern.TLabel` | Etiquetas | Fuente Segoe UI, fondo consistente |

### Características de la UI

- **Iconos emoji** en botones para mejor UX visual (➕ 📝 🗑️ 🧹)
- **Efectos hover**: los botones oscurecen al pasar el mouse
- **Espaciado mejorado**: padding de 15px en frames principales
- **Tipografía moderna**: fuente Segoe UI (nativa Windows)
- **Scrollbar estilizado**: combinación de colores primario y fondo
- **Filas intercaladas** (zebra striping): fondo blanco/gris claro para mejor lectura
- **Ordenamiento por clic**: los encabezados de la tabla son clickeables para ordenar

### Ordenamiento de la Tabla

Los encabezados de la tabla funcionan como botones de ordenamiento:

| Indicador | Significado |
|-----------|-------------|
| `Nombre ↕` | Columna ordenable (clic para ordenar) |
| `Nombre ↑` | Ordenado ascendente (A→Z, 1→9) |
| `Nombre ↓` | Ordenado descendente (Z→A, 9→1) |

**Comportamiento:**
- **Primer clic** en encabezado: ordena ascendente (↑)
- **Segundo clic** en mismo encabezado: ordena descendente (↓)
- **Clic en otro encabezado**: cambia a esa columna en orden ascendente
- **Botón Recargar**: resetea al orden por defecto (nombre ascendente)

### Archivo `styles.py` — `StyleManager`

Los estilos están centralizados en `styles.py` para mantener la consistencia visual:

```python
from styles import StyleManager

# Configurar todos los estilos al iniciar
StyleManager.configurar_estilos()

# Acceder a colores programáticamente
color_primario = StyleManager.obtener_color('PRIMARY')  # '#2196F3'
```

**Beneficios de separar estilos:**
- **Consistencia**: un solo lugar define todos los colores y fuentes
- **Mantenibilidad**: cambiar un color actualiza toda la aplicación
- **Reutilización**: otros proyectos pueden importar `StyleManager`
- **Legibilidad**: `app.py` se enfoca en la lógica, no en estilos

---

## Documentación Educativa en el Código

Cada archivo del proyecto incluye documentación extensa diseñada para el aprendizaje:

### Cómo leer los archivos (recomendación para estudiantes)

| Archivo | Secciones destacadas | Qué aprender |
|---------|---------------------|--------------|
| `app.py` | Encabezado (líneas 1-58) | Arquitectura en capas, flujo de datos MVC |
| `app.py` | `__init__()` (líneas 67-106) | Orden de inicialización de componentes |
| `app.py` | `crear_widgets()` (líneas 118-180) | Layout con grid(), Treeview, event bindings |
| `app.py` | `ordenar_por()` (líneas 251-302) | Patrón de estado, feedback visual |
| `database.py` | Encabezado (líneas 1-21) | Patrón DAO, prevención de inyección SQL |
| `database.py` | `fetch_all_clientes()` (líneas 122-162) | SQL dinámico seguro, validación de parámetros |
| `styles.py` | Encabezado (líneas 1-26) | Sistema TTK, herencia de estilos |
| `config.py` | Encabezado (líneas 1-24) | Single Source of Truth, variables de entorno |

### Formatos de comentarios utilizados

```python
# =============================================================================
# SECCIONES CON === : Bloques explicativos de alto nivel
# =============================================================================

# NOTA PARA ESTUDIANTES: Explicaciones didácticas sobre conceptos específicos

# Guard clause: Patrones de código con nombre (ej: salir temprano si no hay conexión)

"""
PATRÓN: Descripción de patrones de diseño aplicados
"""
```

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
9. **Estilos TTK personalizados** — `ttk.Style()` con temas, paletas de colores y efectos hover para UI moderna
10. **Separación de responsabilidades** — estilos en `styles.py`, configuración en `config.py`, lógica en `app.py`
11. **Ordenamiento dinámico** — encabezados clickeables con `command=` que ejecutan SQL `ORDER BY` con parámetros variables
12. **Layout responsive** — uso de `grid_rowconfigure(weight=)` para distribución óptima del espacio vertical
13. **Documentación profesional** — cada archivo tiene encabezados educativos con objetivos pedagógicos, diagramas ASCII y comentarios explicativos
