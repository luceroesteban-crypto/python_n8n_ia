import gradio as gr
import os
import shutil
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# --- Importaciones de LangChain (paquetes standalone/modernos) ---
from langchain_core.documents import Document
from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_classic.retrievers import EnsembleRetriever

# --- Nuevas Importaciones para el Chatbot ---
from operator import itemgetter

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from retrievers import construir_bm25_desde_vectordb

# --- 1. Configuración Global y Carga de Modelos ---
# (Cargamos los modelos caros UNA SOLA VEZ al inicio)

print("Cargando modelos globales...")

# Variables (actualizadas: embeddings multilingüe + búsqueda híbrida + memoria)
# Nota: app.py es la versión monolítica; todas las constantes se definen aquí
# para no depender de config.py ni de llm_factory.py.
PERSIST_DIRECTORY = "db_chroma"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# Número de chunks que se recuperan y se pasan al LLM.
# Aumentamos a 5 para cubrir más posibilidades cuando la pregunta es corta.
K_RESULTADOS = 5

# Pesos del retriever híbrido. Para preguntas con palabras clave concretas
# (ej: "mandato diputado"), BM25 suele funcionar mejor que la búsqueda densa.
PESO_BM25 = 0.7
PESO_DENSO = 0.3
MAX_CHAT_HISTORY = 5

# Modelo de Google Gemini a utilizar.
# Para la versión modular ver app_refactorizado.py / config.py / llm_factory.py.
LLM_MODEL = "gemini-2.5-flash"

# Inicializar el modelo de Embeddings (Open-Source)
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={'device': 'cpu'}
)

# Inicializar el LLM (Google Gemini)
# ¡Asegurate de tener la variable de entorno GOOGLE_API_KEY en el archivo .env!
try:
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL)
except ImportError:
    print("Error: 'langchain-google-genai' no está instalado. Ejecuta: pip install langchain-google-genai")
    exit()
except Exception as e:
    print(f"Error al cargar el LLM. ¿Estableciste la GOOGLE_API_KEY? Error: {e}")
    exit()


# Inicializar el cliente de la base de datos vectorial
# Esto se conecta al directorio persistente si existe, 
# o se prepara para crearlo.
vectordb = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embeddings
)

# Plantilla de Prompt para RAG con memoria conversacional
RAG_PROMPT_TEMPLATE = """
Eres un asistente de IA experto. Respondé la pregunta del usuario utilizando preferentemente la información del contexto provisto.
Si el contexto contiene información parcial o relacionada, usala para dar la mejor respuesta posible.
Solo si el contexto es completamente irrelevante o no contiene ninguna pista útil, indicá amablemente que no tenés esa información.
Mantén coherencia con el historial reciente de la conversación.

Historial reciente de la conversación:
{chat_history}

Contexto:
{context}

Pregunta:
{question}

Respuesta:
"""
rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)


def format_chat_history(chat_history):
    """Formatea el historial de Gradio (formato messages) para el prompt."""
    if not chat_history:
        return "No hay mensajes previos en esta conversación."

    # Gradio 6+ usa lista de dicts {'role': ..., 'content': ...}
    recent = chat_history[-MAX_CHAT_HISTORY * 2:]
    lines = []
    for msg in recent:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user":
            lines.append(f"Usuario: {content}")
        elif role == "assistant":
            lines.append(f"Asistente: {content}")
    return "\n".join(lines)

# --- 2. Lógica de la Aplicación (Funciones) ---

def add_to_knowledge_base(file_list):
    """
    Función para la pestaña "Cargar Archivos".
    Procesa los archivos y los añade a ChromaDB.
    """
    if not file_list:
        stats = get_knowledge_base_stats()
        return "Por favor, selecciona al menos un archivo.", stats

    print(f"Procesando {len(file_list)} archivo(s)...")
    
    # 1. Cargar documentos (adaptado de ingesta.py)
    # Usamos loaders standalone/modernos para evitar langchain_community.
    documents = []
    for file_obj in file_list:
        file_path = file_obj.name
        print(f"Cargando {file_path}")
        if file_path.endswith(".pdf"):
            loader = PyMuPDF4LLMLoader(file_path, mode="page")
            documents.extend(loader.load())
        elif file_path.endswith(".txt"):
            with open(file_path, encoding='utf-8') as f:
                contenido = f.read()
            documents.append(Document(page_content=contenido, metadata={"source": file_path}))
        else:
            print(f"Archivo no soportado: {file_path}")
            continue

    if not documents:
        stats = get_knowledge_base_stats()
        return "No se pudieron cargar documentos válidos (solo .txt y .pdf).", stats

    # 2. Dividir documentos (adaptado de ingesta.py)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=250)
    splits = text_splitter.split_documents(documents)
    
    if not splits:
        stats = get_knowledge_base_stats()
        return "Los documentos están vacíos o no se pudieron dividir.", stats

    # 3. Añadir a la base de datos (Usamos .add_documents para añadir)
    print(f"Añadiendo {len(splits)} chunks a la base de datos...")
    vectordb.add_documents(splits)
    print("¡Archivos procesados y añadidos a la base de datos!")
    
    # Obtener estadísticas actualizadas
    stats = get_knowledge_base_stats()
    
    return f"¡Éxito! Se añadieron {len(splits)} fragmentos de {len(file_list)} archivo(s).", stats

def respond_chat(message, chat_history):
    """
    Función para el Chatbot con memoria conversacional.
    Construye y ejecuta la cadena RAG completa, incluyendo el historial
    reciente en el prompt para mantener contexto entre preguntas.
    """
    print(f"Recibida pregunta: {message}")

    # 1. Crear los retrievers (denso + léxico BM25) y combinarlos en un híbrido
    retriever_denso = vectordb.as_retriever(search_kwargs={"k": K_RESULTADOS})
    retriever_bm25 = construir_bm25_desde_vectordb(vectordb, k=K_RESULTADOS)

    if retriever_bm25 is not None:
        retriever = EnsembleRetriever(
            retrievers=[retriever_bm25, retriever_denso],
            weights=[PESO_BM25, PESO_DENSO]
        )
    else:
        retriever = retriever_denso

    def format_context(docs):
        # EnsembleRetriever puede devolver más de k resultados; limitamos
        context = "\n\n".join(doc.page_content for doc in docs[:K_RESULTADOS])
        # Debug: mostrar en consola qué contexto se recuperó
        print("\n--- CONTEXTO RECUPERADO ---")
        print(context if context else "(NINGUNO)")
        print("--- FIN CONTEXTO ---\n")
        return context

    # 2. Construir la cadena RAG con LCEL y memoria
    # El input ahora es un dict con la pregunta y el historial formateado
    rag_chain = (
        {
            "context": itemgetter("question") | retriever | format_context,
            "question": itemgetter("question"),
            "chat_history": itemgetter("chat_history"),
        }
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    # 3. Invocar la cadena con la pregunta y el historial formateado
    print("Invocando cadena RAG...")
    response = rag_chain.invoke({
        "question": message,
        "chat_history": format_chat_history(chat_history)
    })

    # Gradio 6+ espera mensajes como dicts con 'role' y 'content'
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": response})
    print(f"Respuesta generada: {response}")

    return "", chat_history

def clear_knowledge_base():
    """
    Función para limpiar la base de datos eliminando todos los documentos.
    """
    global vectordb
    try:
        print("Limpiando base de datos...")
        
        # Obtener todos los IDs de la colección
        collection = vectordb._collection
        
        # Verificar si hay documentos
        count = collection.count()
        if count == 0:
            print("La base de datos ya estaba vacía.")
            stats = get_knowledge_base_stats()
            return "La base de datos ya estaba vacía.", stats
        
        # Obtener todos los IDs y eliminarlos
        all_ids = collection.get()['ids']
        if all_ids:
            collection.delete(ids=all_ids)
            print(f"Se eliminaron {count} fragmentos de la base de datos.")
        
        stats = get_knowledge_base_stats()
        return f"✅ Base de datos limpiada exitosamente. Se eliminaron {count} fragmentos.", stats
        
    except Exception as e:
        print(f"Error al limpiar la base de datos: {e}")
        stats = get_knowledge_base_stats()
        return f"❌ Error al limpiar la base de datos: {e}\n\nSi el problema persiste, reinicia la aplicación.", stats

def get_knowledge_base_stats():
    """
    Obtiene estadísticas de la base de conocimiento.
    Retorna un string formateado con las estadísticas.
    """
    try:
        # Obtener la colección de ChromaDB
        collection = vectordb._collection
        count = collection.count()
        
        if count == 0:
            return " **Estado:** Base de conocimiento vacía (0 fragmentos)"
        else:
            return f" **Estado:** Base de conocimiento activa\n\n **Total de fragmentos:** {count:,}\n\n Puedes hacer preguntas sobre el contenido cargado."
    except Exception as e:
        return f" Error al obtener estadísticas: {e}"

# --- 3. Interfaz de Gradio ---

print("Iniciando interfaz de Gradio...")

with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Chatbot RAG con LangChain y Gradio\nChatea con tus documentos. Sube archivos en la pestaña 'Base de Conocimiento'.")

    with gr.Tab("💬 Chatbot"):
        chatbot = gr.Chatbot(label="Chat", height=400)
        msg_input = gr.Textbox(label="Escribe tu pregunta aquí...", lines=1, max_lines=3)
        
        with gr.Row():
            submit_btn = gr.Button("📤 Enviar", variant="primary")
            clear_button = gr.ClearButton([msg_input, chatbot], value="🗑️ Limpiar Chat")
        
        # Conectar la función de chat
        msg_input.submit(respond_chat, [msg_input, chatbot], [msg_input, chatbot])
        submit_btn.click(respond_chat, [msg_input, chatbot], [msg_input, chatbot])

    with gr.Tab("📚 Base de Conocimiento"):
        
        # Estadísticas compactas
        with gr.Row():
            stats_display = gr.Markdown(value=get_knowledge_base_stats())
            refresh_button = gr.Button("🔄 Actualizar", size="sm", scale=0)
        
        # Cargar archivos
        with gr.Group():
            gr.Markdown("### 📤 Cargar Documentos")
            file_upload = gr.File(
                label="Archivos (.txt, .pdf)",
                file_count="multiple",
                file_types=[".txt", ".pdf"]
            )
            upload_button = gr.Button("📥 Analizar y Cargar", variant="primary")
            status_output = gr.Textbox(label="Resultado", interactive=False, lines=3)
        
        # Limpiar base de datos
        with gr.Group():
            gr.Markdown("### ⚠️ Limpiar Base de Datos")
            clear_db_button = gr.Button("🗑️ Eliminar Todos los Documentos", variant="stop")
            clear_status_output = gr.Textbox(label="Resultado", interactive=False, lines=2)
        
        # Conectar eventos
        upload_button.click(
            add_to_knowledge_base, 
            inputs=[file_upload], 
            outputs=[status_output, stats_display]
        )
        
        refresh_button.click(
            get_knowledge_base_stats,
            inputs=[],
            outputs=[stats_display]
        )
        
        # Conectar la función de limpiado
        clear_db_button.click(
            clear_knowledge_base, 
            inputs=[], 
            outputs=[clear_status_output, stats_display]
        )

# --- 4. Lanzar la Aplicación ---
if __name__ == "__main__":
    print("Lanzando la aplicación...")
    demo.launch(
        share=False,  # share=True para crear un enlace público temporal
        theme=gr.themes.Soft()
    )