# Documentación adicional del ejemplo de la clase 20

Este archivo recoge la documentación nueva del ejemplo de la clase 20

## ¿Qué vamos a construir?

Vamos a crear una aplicación que permita:

- mostrar la lista de clientes,
- agregar un nuevo cliente,
- editar los datos de un cliente existente,
- eliminar un cliente.

Este ejemplo sigue el flujo típico de un CRUD: Crear, Leer, Actualizar y Eliminar.

## Archivos del ejemplo

- [11 - clientesdb.py](11%20-%20clientesdb.py): archivo principal donde se definen las rutas y la lógica de Flask.
- [database.py](database.py): módulo que gestiona la conexión a SQLite y la inicialización de la base.
- [schema.sql](schema.sql): archivo con la estructura de la tabla clientes.
- [models/clientes.py](models/clientes.py): capa de acceso a datos para separar la lógica SQL del controlador.
- [templates/clientes](templates/clientes): carpetas con las plantillas HTML para listar, crear y editar clientes.

## 1. Crear la aplicación Flask

En el archivo [11 - clientesdb.py](11%20-%20clientesdb.py) se crea la aplicación con Flask y se define la clave secreta necesaria para usar mensajes flash.

```python
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'
```

## 2. Inicializar la base de datos

Antes de trabajar con los clientes, la app prepara la base de datos.

```python
with app.app_context():
    init_db()
```

## 3. Leer clientes

La ruta principal muestra todos los clientes almacenados.

```python
@app.route('/')
def index():
    clientes = Clientes.listar_todos()
    return render_template('clientes/listar_clientes.html', clientes=clientes)
```

## 4. Crear clientes

La ruta /crear permite agregar un cliente nuevo.

```python
@app.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
```

## 5. Editar clientes

La ruta /editar/<id> permite modificar los datos de un cliente existente.

```python
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
```

## 6. Eliminar clientes

La ruta /eliminar/<id> borra un cliente de la base de datos.

```python
@app.route('/eliminar/<int:id>')
def eliminar(id):
```

## 7. Estructura de la base de datos

La tabla clientes tiene estas columnas:

- id: identificador único automático,
- nombre: texto obligatorio,
- email: texto obligatorio y único,
- telefono: texto obligatorio.

> Nota: esta restricción de unicidad en el email es correcta para una base nueva o para una base ya existente sin correos duplicados. Si una base antigua ya contiene emails repetidos, habría que limpiar o ajustar esos datos antes de aplicar esta regla.

## 8. Qué mejora esta versión respecto a la clase 19

Esta versión está más organizada porque:

- separa la lógica de acceso a datos en [models/clientes.py](models/clientes.py),
- usa mejor la gestión de la base de datos en [database.py](database.py),
- y añade una restricción de unicidad para el email.

## 9. Cómo ejecutar el ejemplo

Desde la carpeta del proyecto, puedes ejecutar la aplicación con:

```powershell
python "11 - clientesdb.py"
```

Luego abre en el navegador:

```text
http://127.0.0.1:5000/
```

## Resumen

Este ejemplo enseña cómo conectar Flask con SQLite, gestionar formularios y trabajar con operaciones CRUD de forma organizada.
