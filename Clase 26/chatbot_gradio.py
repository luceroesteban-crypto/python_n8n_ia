import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

# Cargar las variables del archivo .env
load_dotenv()

# =====================================================================
# CONFIGURACIÓN DE PROVEEDOR (FILOSOFÍA MULTI-PROVEEDOR COMPATIBLE)
# =====================================================================

# --- Opción 1: OpenAI (Por defecto) ---
API_BASE_URL = None
MODELO = "gpt-4o-mini"
API_KEY = os.getenv("OPENAI_API_KEY")

# --- Opción 2: Groq (Inferencia Ultrarrápida) ---
# API_BASE_URL = "https://api.groq.com/openai/v1"
# MODELO = "llama-3.1-8b-instant"
# API_KEY = os.getenv("GROQ_API_KEY")

# --- Opción 3: DeepSeek ---
# API_BASE_URL = "https://api.deepseek.com/v1"
# MODELO = "deepseek-chat"
# API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- Opción 4: Ollama (Modelos locales ejecutándose en tu PC) ---
# API_BASE_URL = "http://localhost:11434/v1"
# MODELO = "llama3"
# API_KEY = "ollama"

# =====================================================================

# Inicializamos el cliente
client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL
)

# =====================================================================
# CONFIGURACIÓN DEL CHATBOT (modificar según necesidad)
# =====================================================================

# Prompt de sistema: define la personalidad y restricciones del bot
SYSTEM_PROMPT = "Eres un historiador que solo puede hablar de eventos del siglo XX."

# Máximo de intercambios (pregunta + respuesta) a recordar antes de recortar
MAX_HISTORY = 10

# Máximo de tokens en la respuesta del modelo
MAX_TOKENS = 1000

# =====================================================================
# CONFIGURACIÓN DE LA INTERFAZ GRADIO (modificar según necesidad)
# =====================================================================

# Título que aparece en la parte superior del chat
TITULO = "Chatbot Historiador del Siglo XX"

# Descripción debajo del título
DESCRIPCION = f"Modelo: {MODELO} | Historial máximo: {MAX_HISTORY} intercambios"

# Ejemplos que aparecen como botones clickeables debajo del chat
# Cuando se usan additional_inputs, cada ejemplo debe ser una lista: [mensaje]
EJEMPLOS = [["Hola"], ["Contame sobre la Segunda Guerra Mundial"], ["Qué pasó en la Guerra Fría?"]]

# Puerto del servidor local
PUERTO = 7860

# Tema visual: "soft", "default", "glass", "mono", "ocean", "origin", "citrus"
TEMA = "soft"

# =====================================================================


def responder(mensaje: str, historial: list, system_prompt: str, max_tokens: int, max_history: int) -> str:
    """
    Función que recibe el mensaje del usuario, el historial de Gradio,
    y los parámetros configurables desde la interfaz gráfica.
    """
    # Construimos los mensajes para la API: system + historial + mensaje actual
    messages = [{"role": "system", "content": system_prompt}]

    # Aplicamos ventana deslizante al historial
    max_messages = int(max_history) * 2
    historial_recortado = historial[-max_messages:] if len(historial) > max_messages else historial

    # Agregamos el historial existente
    for msg in historial_recortado:
        role = msg["role"]
        # En Gradio 6.x content puede ser una lista de bloques [{"type": "text", "text": "..."}]
        content = msg["content"]
        if isinstance(content, list):
            # Extraemos solo el texto
            texto = " ".join(
                bloque.get("text", "") for bloque in content if bloque.get("type") == "text"
            )
        else:
            texto = content
        messages.append({"role": role, "content": texto})

    # Agregamos el mensaje actual del usuario
    messages.append({"role": "user", "content": mensaje})

    try:
        response = client.chat.completions.create(
            model=MODELO,
            max_tokens=int(max_tokens),
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al contactar la API: {e}"


# Creamos la interfaz de chat con Gradio usando additional_inputs
# para exponer configuraciones modificables desde la UI
demo = gr.ChatInterface(
    fn=responder,
    title=TITULO,
    description=DESCRIPCION,
    examples=EJEMPLOS,
    additional_inputs=[
        gr.Textbox(
            value=SYSTEM_PROMPT,
            label="System Prompt",
            info="Define la personalidad y restricciones del bot. Cambiar esto reinicia el contexto.",
            lines=3,
        ),
        gr.Slider(
            minimum=100,
            maximum=4000,
            value=MAX_TOKENS,
            step=100,
            label="Max Tokens",
            info="Largo máximo de la respuesta del modelo.",
        ),
        gr.Slider(
            minimum=1,
            maximum=30,
            value=MAX_HISTORY,
            step=1,
            label="Max Historial",
            info="Cantidad de intercambios (pregunta+respuesta) que recuerda el bot.",
        ),
    ],
)

if __name__ == "__main__":
    demo.launch(server_port=PUERTO, theme=TEMA)
