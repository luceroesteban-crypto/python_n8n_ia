import os
from dotenv import load_dotenv

# --- LIBRERÍA VIEJA (Obsoleta/Deprecada a finales de 2025) ---
# import google.generativeai as genai

# --- LIBRERÍA NUEVA (Oficial y unificada de Google) ---
# Se utiliza el nuevo paquete 'google-genai'
from google import genai
from google.genai import types

# Cargar las variables del archivo .env
load_dotenv()

# Evitar mensajes informativos molestos de gRPC en la consola
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise EnvironmentError("La variable de entorno GEMINI_API_KEY no está definida.")

# --- CONFIGURACIÓN VIEJA ---
# genai.configure(api_key=gemini_api_key)

# --- CONFIGURACIÓN NUEVA ---
# Ahora se inicializa un cliente único que maneja todas las llamadas a la API
client = genai.Client(api_key=gemini_api_key)

print("¡Gemini configurado con google-genai!")

class Chatbot:
    def __init__(self, system_prompt: str):
        """Inicializa el chatbot con un prompt de sistema."""
        # --- CÓDIGO VIEJO ---
        # self.model = genai.GenerativeModel(
        #     model_name="gemini-2.5-flash",
        #     system_instruction=system_prompt,
        # )
        # self.chat = self.model.start_chat(history=[])

        # --- CÓDIGO NUEVO ---
        # En la nueva librería, los chats con historial se inicializan desde client.chats
        # Por defecto, si no se especifica 'history', se inicia vacío.
        #
        # Opciones de modelos recomendados en Gemini 3 (2026):
        # - "gemini-3.5-flash" (El más balanceado, rápido, inteligente y económico)
        # - "gemini-3.1-flash-lite" (El modelo más económico y rápido para tareas de mucho volumen)
        self.chat = client.chats.create(
            model="gemini-3.5-flash",
            history=[],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            )
        )

    def talk(self, user_message: str) -> str:
        """Envía un mensaje de usuario y obtiene una respuesta."""
        # El método send_message sigue funcionando de forma similar sobre el objeto chat
        response = self.chat.send_message(user_message)
        if not response.text:
            raise RuntimeError("La API de Gemini no devolvió texto en la respuesta.")
        return response.text.strip()

# --- Punto de entrada de la aplicación ---
if __name__ == "__main__":
    mi_chatbot = Chatbot("Eres un asistente servicial y amigable.")
    print("Chatbot Gemini iniciado. Escribe 'salir' para terminar.")

    while True:
        entrada = input("Tú: ")
        if entrada.lower() == "salir":
            break

        respuesta = mi_chatbot.talk(entrada)
        print(f"Asistente: {respuesta}")
