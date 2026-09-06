# Guía de `uv`: gestor de proyectos Python ultrarrápido

> Si ya conocen `pip` + `venv` y quieren aprender una herramienta moderna,
> unificada y ultrarrápida para manejar versiones de Python, entornos,
> dependencias y proyectos, miren esto.

---

## 1. ¿Qué es `uv`?

`uv` es un gestor integral de proyectos, entornos virtuales y dependencias
para Python desarrollado en Rust por Astral. Reemplaza de forma unificada a
prácticamente todo el ecosistema de herramientas tradicionales:

| Herramienta tradicional | Reemplazo en `uv`           |
| ----------------------- | --------------------------- |
| `pip`                   | `uv pip` / `uv add`         |
| `venv` / `virtualenv`   | `uv venv`                   |
| `poetry` / `pdm` / `pipenv` | `uv init` / `uv add` / `uv sync` |
| `pip-tools`             | `uv pip compile` / `uv lock` |
| `pyenv`                 | `uv python` / `uv python pin` |
| `pipx`                  | `uvx` / `uv tool run`        |
| `python -m pip`         | `uv run` / `uv pip install` |

---

## 2. Ventajas principales

- **Velocidad extrema**: resuelve e instala dependencias mucho más rápido que
  `pip` gracias a su motor en Rust y su caché global.
- **Unificación total**: gestiona versiones de Python, entornos, dependencias,
  scripts y herramientas CLI desde un solo binario.
- **Manejo de versiones de Python integrado**: descarga e instala versiones
  oficiales de CPython y PyPy sin depender de instaladores del sistema ni
  `pyenv`.
- **Proyectos estándar y reproducibles**: ofrece soporte nativo de
  `pyproject.toml` y genera un `uv.lock` determinista y multiplataforma.
- **No requiere activar entornos manualmente**: `uv run` detecta y ejecuta
  automáticamente en el entorno correspondiente.
- **Ejecución de herramientas y dependencias al vuelo**: permite ejecutar CLIs
  aisladas (`uvx`) o scripts con dependencias temporales.
- **Compatibilidad hacia atrás**: funciona directamente con `requirements.txt`.

---

## 3. Instalación

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS / Linux (bash/zsh)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Verificar instalación

```bash
uv --version
```

> Nota: reiniciá la terminal después de instalar para que el comando esté
> disponible en el `PATH`.

---

## 4. Gestión de versiones de Python (`uv python`)

`uv` puede descargar, listar y fijar versiones de Python automáticamente en
cualquier sistema operativo.

### 4.1. Instalar versiones de Python

```bash
uv python install 3.11 3.12 3.13
```

### 4.2. Listar versiones disponibles e instaladas

```bash
uv python list
```

### 4.3. Fijar la versión de Python para un proyecto

Crea un archivo `.python-version` en el directorio actual para que `uv` use
siempre esa versión:

```bash
uv python pin 3.12
```

---

## 5. Modo 1: Flujo de proyectos moderno (`pyproject.toml` + `uv.lock`)

Este es el flujo recomendado para proyectos nuevos o aplicaciones completas.

### 5.1. Inicializar un nuevo proyecto

```bash
uv init mi-proyecto
cd mi-proyecto
```

### 5.2. Agregar dependencias

```bash
uv add fastapi uvicorn requests
uv add --dev pytest ruff black
```

Los paquetes se registran en `pyproject.toml` y `uv.lock` se actualiza
automáticamente.

### 5.3. Sincronizar el entorno y actualizar el lockfile

```bash
uv sync
uv lock
```

Al clonar un repositorio o cambiar de rama, `uv sync` deja el `.venv` igual que
lo definido en `uv.lock`.

---

## 6. Modo 2: Flujo clásico / compatibilidad (`uv pip` + `requirements.txt`)

Ideal para proyectos heredados o scripts simples donde se prefiere trabajar
con `requirements.txt`.

## 7. Crear un entorno virtual

### 7.1. Entorno con la versión de Python por defecto

```bash
uv venv
```

Crea una carpeta `.venv` en el directorio actual.

Salida típica:

```text
Using CPython 3.13.11
Creating virtual environment at: .venv
Activate with: .venv\Scripts\activate
```

### 7.2. Entorno con una versión específica de Python

```bash
uv venv --python 3.11
```

Si `uv` no tiene esa versión, la descarga e instala automáticamente:

```bash
uv python install 3.11
uv venv --python 3.11
```

### 7.3. Entorno con un nombre personalizado

```bash
uv venv --name mi_entorno
```

Esto crea `mi_entorno/` en lugar de `.venv`.

### 7.4. Listar versiones de Python disponibles

```bash
uv python list
```

### 7.5. Activar el entorno (opcional)

- **Windows:**

  ```powershell
  .venv\Scripts\activate
  ```

- **macOS / Linux:**

  ```bash
  source .venv/bin/activate
  ```

Con `uv` no es obligatorio activarlo: se puede ejecutar todo con `uv run`.

---

## 8. Instalar dependencias

### 8.1. Desde un `requirements.txt`

```bash
uv pip install -r requirements.txt
```

### 8.2. Instalar un paquete suelto

```bash
uv pip install gradio
```

### 8.3. Ver dependencias instaladas

```bash
uv pip list
```

### 8.4. Actualizar dependencias

```bash
uv pip install -r requirements.txt --upgrade
```

### 8.5. Generar un archivo de bloqueo determinista (opcional, avanzado)

Si querés asegurar versiones exactas para reproducibilidad:

```bash
uv pip compile requirements.in -o requirements.txt
```

O, en proyectos con `pyproject.toml`:

```bash
uv lock
```

Esto crea `uv.lock`, que es equivalente a `package-lock.json` en Node.js.

---

## 9. Ejecutar aplicaciones y herramientas

### 9.1. Ejecutar sin activar el entorno

```bash
uv run python app_refactorizado.py
```

`uv run` detecta automáticamente `.venv` y ejecuta el script dentro de él.

### 9.2. Ejecutar un módulo

```bash
uv run python -m http.server 8000
```

### 9.3. Ejecutar con variables de entorno

```powershell
# Windows
$env:GOOGLE_API_KEY = "tu-key"
uv run python app_refactorizado.py
```

```bash
# macOS / Linux
export GOOGLE_API_KEY="tu-key"
uv run python app_refactorizado.py
```

### 9.4. Ejecutar un script de una sola vez sin crear entorno

```bash
uv run --with requests python script.py
```

Esto descarga temporalmente `requests` y ejecuta el script.

### 9.5. Ejecutar herramientas CLI aisladas (`uvx` / `uv tool run`)

Es un reemplazo directo de `pipx`: ejecuta herramientas en un entorno aislado
sin instalarlas en el proyecto.

```bash
# Ejecutar el linter y formateador Ruff
uvx ruff check .
uvx ruff format .

# Probar una utilidad CLI
uvx httpie https://api.github.com
```

---

## 10. Flujo de trabajo práctico para la Clase 27

```powershell
# 1. Ir al proyecto
cd "c:\Users\ofazz\Desktop\Clase 27"

# 2. Listar e instalar la versión requerida de Python
uv python list
uv python install 3.11

# 3. Opción A: flujo clásico (el proyecto usa requirements.txt)
uv venv --python 3.11

#    Instalar dependencias
uv pip install -r requirements.txt

# 4. Opción B: flujo moderno (el proyecto usa pyproject.toml / uv.lock)
uv sync

# 5. Crear el archivo de entorno a partir del ejemplo
copy .env.example .env

# 6. Editar .env con tus API keys
notepad .env

# 7. Ejecutar la aplicación
uv run python app_refactorizado.py
```

---

## 11. Tabla de comandos rápidos

| Tarea                                | Comando `uv`                                  |
| ------------------------------------ | --------------------------------------------- |
| Crear entorno                        | `uv venv`                                     |
| Crear entorno con Python 3.11        | `uv venv --python 3.11`                       |
| Instalar versiones de Python         | `uv python install 3.11 3.12 3.13`            |
| Listar versiones de Python            | `uv python list`                              |
| Fijar versión del proyecto            | `uv python pin 3.12`                          |
| Inicializar un proyecto               | `uv init <nombre>`                            |
| Agregar una dependencia               | `uv add <paquete>`                            |
| Agregar dependencia de desarrollo     | `uv add --dev <paquete>`                      |
| Sincronizar desde `uv.lock`           | `uv sync`                                     |
| Activar entorno (Windows)            | `.venv\Scripts\activate`                     |
| Activar entorno (Linux/macOS)        | `source .venv/bin/activate`                   |
| Instalar dependencias                | `uv pip install -r requirements.txt`          |
| Listar paquetes                      | `uv pip list`                                 |
| Ejecutar script dentro del entorno   | `uv run python app.py`                        |
| Actualizar dependencias              | `uv pip install -r requirements.txt --upgrade` |
| Generar bloqueo determinista         | `uv lock`                                     |
| Ejecutar herramienta aislada         | `uvx <herramienta>`                           |
| Actualizar `uv`                      | `uv self update`                              |
| Ver ayuda                            | `uv --help`                                   |

---

## 12. Comparativa general: `uv` vs herramientas tradicionales

| Característica                  | `pip` + `venv`                          | `uv`                                      |
| ------------------------------- | --------------------------------------- | ----------------------------------------- |
| Crear entorno                   | `python -m venv .venv`                  | `uv venv`                                 |
| Activar + instalar              | `activate` + `pip install -r ...`       | `uv pip install -r ...` o `uv run`      |
| Ejecutar sin activar            | No                                      | Sí, con `uv run`                          |
| Velocidad de resolución         | Media                                   | Muy alta                                  |
| Gestión de versiones de Python  | Requiere `pyenv` o instalar manualmente | Integrada (`uv python install`)           |
| Archivo de bloqueo              | No tiene                                | `uv.lock`                                 |
| Requiere activar el entorno     | Sí, si no se quiere usar path absoluto  | No                                        |

---

## 13. Consejos prácticos

- **No commitear `.venv`**: asegurate de que `.gitignore` lo ignore.
- **Commitear `uv.lock` y `pyproject.toml`**: garantiza que todo el equipo y
  los servidores trabajen con las versiones exactas.
- **No commitear `.env`**: usá `.env.example` como plantilla pública.
- **Actualizar `uv` de vez en cuando**:

  ```bash
  uv self update
  ```

- Si un paquete falla al instalar, probá con:

  ```bash
  uv pip install --no-cache <paquete>
  ```

---

## Referencias

- Documentación oficial: <https://docs.astral.sh/uv/>
- Repositorio: <https://github.com/astral-sh/uv>
