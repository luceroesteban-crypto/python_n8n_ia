import os
from dotenv import load_dotenv
# 1. Importamos la clase cliente oficial de OpenAI (mejor práctica en v1.0.0+)
from openai import OpenAI

# Cargar las variables del archivo .env
load_dotenv()

# =====================================================================
# CONFIGURACIÓN DE PROVEEDOR (FILOSOFÍA MULTI-PROVEEDOR COMPATIBLE)
# =====================================================================
# Modificando estas tres constantes, puedes desviar todo el chatbot a otro proveedor
# compatible con el estándar de OpenAI sin tocar el resto del código del script.

# --- Opción 1: OpenAI (Por defecto) ---
API_BASE_URL = None  # None utiliza la URL oficial de OpenAI por defecto
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
# MODELO = "llama3"  # O el modelo local que tengas descargado en Ollama
# API_KEY = "ollama"  # Ollama no requiere credenciales pero la API exige un string no vacío

# =====================================================================

# 2. Inicializamos el cliente apuntando al proveedor elegido mediante las constantes
client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL
)

class Chatbot:
    def __init__(self, system_prompt: str, max_history: int = 10):
        """
        Inicializa el chatbot.
        :param system_prompt: La instrucción inicial para definir el comportamiento del bot.
        :param max_history: El número máximo de intercambios (pregunta + respuesta) a recordar.
        """
        self.system_message = {"role": "system", "content": system_prompt}
        self.messages = [self.system_message]
        # El historial real será el doble (user + assistant)
        self.max_history_tokens = max_history * 2 

    def talk(self, user_message: str) -> str:
        """
        Envía un mensaje de usuario, gestiona el historial y obtiene una respuesta.
        """
        self.messages.append({"role": "user", "content": user_message})

        # --- INICIO DE LA LÓGICA DE VENTANA DESLIZANTE ---
        # Si el historial excede el tamaño máximo...
        if len(self.messages) > self.max_history_tokens + 1: # +1 por el mensaje de sistema
            # ...recorta la lista, manteniendo siempre el mensaje de sistema
            # y los mensajes más recientes.
            self.messages = [self.system_message] + self.messages[-self.max_history_tokens:]
        # --- FIN DE LA LÓGICA DE VENTANA DESLIZANTE ---

        try:
            # 3. Realizamos la llamada a través del cliente instanciado (client) y la constante (MODELO)
            response = client.chat.completions.create(
                model=MODELO,
                max_tokens=1000,
                messages=self.messages
            )

            assistant_response = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": assistant_response})
            return assistant_response
        except Exception as e:
            print(f"⚠️ Ocurrió un error al contactar la API: {e}")
            # Opcional: si hay un error, eliminamos el último mensaje del usuario para que pueda reintentar.
            self.messages.pop() 
            return "Lo siento, tuve un problema para procesar tu solicitud."

# --- Ejemplo de uso ---
if __name__ == "__main__":
    # Creamos un bot que solo recordará los últimos 3 intercambios.
    mi_chatbot = Chatbot(
        system_prompt="Eres un historiador que solo puede hablar de eventos del siglo XX.",
        max_history=3
    )
    
    print("Chatbot iniciado. Prueba a tener una conversación larga para ver cómo olvida el contexto inicial.")
    print("Escribe 'salir' para terminar.")

    while True:
        entrada = input("Tú: ")
        if entrada.lower() == "salir":
            break
        
        respuesta = mi_chatbot.talk(entrada)
        print(f"Historiador: {respuesta}")
        # Opcional: Imprimir el tamaño del historial para ver cómo se gestiona.
        print(f"(Debug: Mensajes en historial = {len(mi_chatbot.messages)})")