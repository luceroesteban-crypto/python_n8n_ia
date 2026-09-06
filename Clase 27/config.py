"""
config.py - Archivo de Configuración del Chatbot RAG
=====================================================

Este archivo contiene todas las constantes y configuraciones globales
de la aplicación. Es una buena práctica mantener toda la configuración
en un solo lugar para facilitar los cambios y el mantenimiento.

Autor: Clase 24 - IA Python para Principiantes
Fecha: 2025
"""

import os
from dotenv import load_dotenv

# ==============================================================================
# 1. CARGA DE VARIABLES DE ENTORNO
# ==============================================================================

# Cargar las variables de entorno desde el archivo .env
# Esto nos permite mantener las API keys seguras y fuera del código
load_dotenv()

# ==============================================================================
# 2. CONFIGURACIÓN DE LA BASE DE DATOS VECTORIAL
# ==============================================================================

# Directorio donde se guardarán los datos de ChromaDB
# ChromaDB es nuestra base de datos vectorial que almacena los embeddings
PERSIST_DIRECTORY = "db_chroma"

# ==============================================================================
# 3. CONFIGURACIÓN DEL MODELO DE EMBEDDINGS
# ==============================================================================

# Modelo de embeddings a utilizar (Open Source de Hugging Face)
# Este modelo convierte texto en vectores numéricos para buscar similaridad.
# Se usa un modelo multilingüe (incluye español) para mejorar la recuperación
# con documentos en español y evitar los problemas observados con modelos
# entrenados principalmente en inglés.
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Configuración del dispositivo (CPU o GPU)
# Para este ejemplo usamos CPU. Si tienes GPU, cambia a 'cuda'
DEVICE = 'cpu'

# ==============================================================================
# 4. CONFIGURACIÓN DEL MODELO DE LENGUAJE (LLM)
# ==============================================================================

# Proveedor del LLM. Opciones soportadas por llm_factory.py:
#   - "google" / "google_genai" / "gemini"  → ChatGoogleGenerativeAI
#   - "openai"                             → ChatOpenAI
#   - "groq"                               → ChatGroq
#   - "ollama"                             → ChatOllama (modelos locales)
LLM_PROVIDER = "google"

# Modelo de lenguaje a utilizar.
# Por defecto se usa Gemini 2.5 Flash: modelo rápido y económico.
# Otros ejemplos:
#   - Gemini 2.5 Flash:  "gemini-2.5-flash"
#   - Gemini 2.5 Pro:    "gemini-2.5-pro"
#   - OpenAI GPT-4o:     "gpt-4o"
#   - Groq Llama 3.1:    "llama-3.1-70b-versatile"
#   - Ollama local:      "llama3.1"
LLM_MODEL = "gemini-2.5-flash"

# NOTA: Para cambiar de proveedor basta con editar LLM_PROVIDER y LLM_MODEL
# en este archivo. La importación e inicialización del LLM se maneja
# automáticamente desde llm_factory.py.

# ==============================================================================
# 5. CONFIGURACIÓN DEL PROCESAMIENTO DE DOCUMENTOS
# ==============================================================================

# Tamaño de cada fragmento (chunk) de texto en caracteres
# Un chunk más grande = más contexto pero menos precisión
# Un chunk más pequeño = más precisión pero menos contexto
CHUNK_SIZE = 1500

# Superposición entre chunks consecutivos
# Esto ayuda a mantener el contexto entre fragmentos
CHUNK_OVERLAP = 250

# ==============================================================================
# 6. CONFIGURACIÓN DEL RETRIEVER
# ==============================================================================

# Número de documentos relevantes a recuperar para cada pregunta
# Más documentos = más contexto pero puede incluir información irrelevante
TOP_K_DOCUMENTS = 5

# Número de intercambios recientes (usuario + asistente) que se incluirán
# en el prompt como memoria conversacional.
MAX_CHAT_HISTORY = 5

# Número de resultados finales que se pasan al LLM después de fusionar los
# rankings de BM25 y búsqueda densa. Un valor más alto da más contexto al
# modelo, pero también puede incluir ruido.
K_RESULTADOS = 5

# Pesos del ensemble: cuánto pesa cada retriever en el ranking final.
# Para preguntas con palabras clave concretas (ej: "mandato diputado"),
# BM25 suele recuperar mejores resultados que la búsqueda densa.
# 0.7/0.3 = favorece BM25 sin descartar completamente el retriever denso.
PESO_BM25 = 0.7
PESO_DENSO = 0.3

# ==============================================================================
# 7. PLANTILLA DE PROMPT PARA RAG
# ==============================================================================

# Plantilla del prompt que se enviará al LLM
# {context} se reemplazará con los documentos recuperados
# {question} se reemplazará con la pregunta del usuario
RAG_PROMPT_TEMPLATE = """
Eres un asistente de IA experto y amigable. Respondé la pregunta del usuario
utilizando preferentemente la información del contexto proporcionado,
manteniendo coherencia con la conversación previa.

INSTRUCCIONES IMPORTANTES:
- Si el contexto contiene la información solicitada, respondé de forma clara y completa.
- Si el contexto contiene información parcial o relacionada, usala para dar la mejor respuesta posible.
- Solo si el contexto es completamente irrelevante o no contiene ninguna pista útil, indicá amablemente que no tenés esa información.
- NO inventes información que no esté en el contexto.
- Podés formatear tu respuesta usando puntos o listas si es apropiado.

HISTORIAL RECIENTE DE LA CONVERSACIÓN:
{chat_history}

CONTEXTO RECUPERADO DE LOS DOCUMENTOS:
{context}

PREGUNTA DEL USUARIO:
{question}

RESPUESTA:
"""

# ==============================================================================
# 8. CONFIGURACIÓN DE LA INTERFAZ DE GRADIO
# ==============================================================================

# Título de la aplicación
APP_TITLE = "🤖 Chatbot RAG con LangChain y Gradio"

# Descripción de la aplicación
APP_DESCRIPTION = "Chatea con tus documentos. Sube archivos en la pestaña 'Cargar Archivos'."

# Altura del área de chat en píxeles
CHAT_HEIGHT = 400

# Tipos de archivo permitidos
ALLOWED_FILE_TYPES = [".txt", ".pdf"]

# Tema de la interfaz (puede ser: Soft, Base, Default, Glass, Monochrome)
UI_THEME = "soft"

# ==============================================================================
# 9. MENSAJES DE LA APLICACIÓN
# ==============================================================================

# Mensajes informativos que se muestran en la consola
MSG_LOADING_MODELS = "🔄 Cargando modelos de IA..."
MSG_MODELS_LOADED = "✅ Modelos cargados exitosamente"
MSG_STARTING_UI = "🚀 Iniciando interfaz de Gradio..."
MSG_PROCESSING_FILES = "📄 Procesando archivos..."
MSG_FILES_ADDED = "✅ Archivos añadidos a la base de conocimiento"
MSG_CLEANING_DB = "🗑️ Limpiando base de datos..."
MSG_DB_CLEANED = "✅ Base de datos limpiada"

# Mensajes de error
ERROR_NO_API_KEY = "❌ Error: No se encontró la GOOGLE_API_KEY en las variables de entorno"
ERROR_MODEL_LOAD = "❌ Error al cargar el modelo"
ERROR_FILE_PROCESSING = "❌ Error al procesar archivos"

# ==============================================================================
# NOTAS PARA ESTUDIANTES
# ==============================================================================
"""
📚 CONCEPTOS IMPORTANTES:

1. VARIABLES DE ENTORNO:
   - Son valores que se cargan desde archivos externos (.env)
   - Útiles para mantener información sensible fuera del código
   - Nunca subas archivos .env a repositorios públicos

2. CONSTANTES:
   - Se escriben en MAYÚSCULAS por convención
   - Son valores que no cambian durante la ejecución
   - Facilitan el mantenimiento del código

3. CONFIGURACIÓN CENTRALIZADA:
   - Mantener toda la configuración en un archivo facilita:
     * Hacer cambios rápidos
     * Entender qué parámetros tiene la aplicación
     * Compartir código sin compartir credenciales
     
4. DOCUMENTACIÓN:
   - Los docstrings (""" """) explican qué hace cada sección
   - Los comentarios (#) aclaran detalles específicos
   - Es fundamental para que otros (y tú en el futuro) entiendan el código
"""
