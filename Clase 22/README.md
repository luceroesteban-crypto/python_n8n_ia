# Clase 22: Aplicaciones de IA Generativa con Python
### Curso: Python y N8N con IA — Centro de Graduados Facultad de Ingeniería

¡Bienvenido al material de estudio de la **Clase 22**! En esta clase aprenderemos cómo conectar scripts de Python con los principales proveedores de modelos de lenguaje a gran escala (LLMs) del mercado mediante sus interfaces de programación de aplicaciones (APIs).

Este documento funciona como una guía teórica y práctica basada en los conceptos explicados en clase y en los ejemplos de código provistos en esta carpeta.

---

## 📖 1. Conceptos Teóricos Clave

### Interfaces Web vs. Aplicaciones
*   **Interfaces Web (Consumo Directo):** Son herramientas listas para el usuario final (como ChatGPT o Google AI Studio) que permiten interactuar con el modelo mediante un chat manual.
*   **Aplicaciones Integradas:** Es software que utiliza internamente un modelo para realizar tareas específicas de manera automatizada (por ejemplo, clasificar correos entrantes, extraer datos a una base de datos o generar resúmenes automáticos al recibir un documento).

### La Arquitectura Cliente-Servidor de las APIs de IA
El desarrollo de software con IA generativa se basa en una arquitectura de comunicación clásica:
*   **El Cliente (Tu script de Python):** Prepara los datos, define las instrucciones (prompts), realiza la petición (*request*) y espera la respuesta.
*   **La Red (Internet):** El medio físico que transporta la consulta.
*   **El Servidor de IA (El Backend del Proveedor):** La infraestructura externa que procesa tus tokens de entrada a través del modelo de IA y te devuelve los tokens de salida (*response*).
*   **La analogía del restaurante:** Piensa en la **API** como el *camarero* de un restaurante. Tu código (el cliente) hace un pedido (el prompt), el camarero lo lleva a la cocina (el servidor de IA) y, finalmente, regresa con el plato listo (la respuesta estructurada). 
*   **La API Key:** Es la "llave VIP" que te identifica ante el proveedor de la API para autorizar el consumo de sus servicios y facturar según tu uso. ¡Recuerda mantenerla siempre en secreto!

### Protocolos de Comunicación
La comunicación entre tu cliente de Python y los servidores de IA se realiza bajo el protocolo **HTTP**:
*   **Peticiones POST:** Son las que usamos para enviar el prompt, el historial y las configuraciones de temperatura o límites de tokens hacia el servidor.
*   **Respuestas estructuradas (JSON):** El servidor responde en un formato de texto estructurado conocido como JSON, el cual contiene la respuesta de la IA junto a datos de diagnóstico como la cantidad de tokens consumidos.

### Estrategias de Chatbots en Atención al Cliente
Las empresas implementan los LLMs de distintas maneras según el nivel de automatización que deseen:
1.  **Solo Humanos:** La atención es directa entre personas.
2.  **Bots como Soporte Interno (*Human-in-the-Loop*):** La IA sugiere respuestas o redacta borradores para que un operador humano los revise, edite o descarte antes de enviarlos.
3.  **Bots como Triajes (Clasificadores):** La IA analiza y clasifica la consulta del cliente. Si es sencilla, la resuelve directamente; si es compleja, la deriva al departamento humano adecuado.
4.  **Solo Bots:** El bot asume por completo la conversación interactiva con el cliente.

---

## 🛠️ 2. Guía de los Scripts de Ejemplo (01 al 06)

A continuación, se detalla la estructura y el objetivo de cada uno de los archivos prácticos de esta clase:

### 🔹 01 - conexion.py
*   **Objetivo:** Verificar la correcta configuración de las variables de entorno y probar una llamada inicial simple al modelo.
*   **Concepto clave:** Uso de `python-dotenv` para cargar de manera segura las credenciales de la API desde el archivo oculto `.env` evitando exponerlas directamente en el código de Python.

### 🔹 02 - chatbot.py
*   **Objetivo:** Crear un chatbot básico e interactivo por consola mediante OpenAI.
*   **Concepto clave:** Utilizar un bucle `while True` para capturar el texto que el usuario ingresa en la terminal y enviarlo al modelo, manteniendo el flujo de preguntas y respuestas.

### 🔹 03 - chatbot_gemini.py
*   **Objetivo:** Implementar un chatbot interactivo utilizando el SDK moderno y oficial de Google (`google-genai`) y conectarse a sus modelos de la generación Gemini 3.
*   **Conceptos clave:**
    *   Uso de la clase `Client` para manejar las conexiones.
    *   Manejo de chats con mantenimiento automático de historial interno a través del método `client.chats.create()`.
    *   Uso del modelo **`gemini-3.5-flash`**, un modelo de frontera que destaca por su velocidad e inteligencia a un costo sumamente bajo.
    *   Uso de instrucciones de sistema (*system prompts*) para modular el comportamiento e identidad del asistente.

### 🔹 04 - resumidor.py
*   **Objetivo:** Realizar tareas de lectura y procesamiento de textos largos de forma automatizada mediante la API de **Groq**.
*   **Concepto clave:** Groq nos permite realizar inferencias ultra velozmente. Aquí le pedimos al modelo de código abierto `llama-3.1-8b-instant` que tome un texto largo y lo condense en exactamente 3 puntos clave estructurados.

### 🔹 05 - extractor.py
*   **Objetivo:** Extraer datos específicos y desordenados de un bloque de texto libre y estructurarlos en formato JSON.
*   **Concepto clave:** Mediante prompts de sistema, forzamos a la IA a que devuelva **únicamente** un objeto JSON válido que contenga campos como `nombre`, `email` y `empresa`. Esto es fundamental para conectar las salidas de los modelos de IA con otros programas o bases de datos de backend tradicionales.

### 🔹 06 - custom.py
*   **Objetivo:** Desarrollar un chatbot avanzado con gestión de memoria y filosofía multi-proveedor utilizando el SDK oficial de OpenAI.
*   **Conceptos clave:**
    *   **Filosofía Multi-Proveedor (Portabilidad):** Al inicio del script definimos constantes configurables como `API_BASE_URL`, `MODELO` y `API_KEY`. Esto nos permite redirigir el cliente de OpenAI a proveedores externos como **Groq** o **DeepSeek**, o incluso a un modelo local corriendo en nuestra computadora mediante **Ollama**, con solo modificar dos variables y sin cambiar una sola línea de código del chatbot.
    *   **Lógica de Ventana Deslizante (*Sliding Window*):** Los modelos de lenguaje tienen límites de memoria y tokens. Este script implementa un control del historial que, al exceder el límite establecido, descarta los mensajes más viejos del chat, pero **conserva siempre la instrucción de sistema original** al inicio de la lista y los últimos diálogos más recientes.

---

## 💻 3. Instrucciones de Configuración y Uso

Sigue estos pasos en tu computadora para configurar y ejecutar los ejemplos prácticos:

### 1. Preparar el Entorno Virtual (venv)
Es una buena práctica crear un entorno virtual para aislar las dependencias del proyecto:
```bash
# Crear el entorno virtual en la carpeta del proyecto
python -m venv venv

# Activar el entorno virtual en Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activar el entorno virtual en macOS o Linux
source venv/bin/activate
```

### 2. Instalar las dependencias requeridas
Utiliza el archivo `requirements.txt` para instalar todas las librerías necesarias ejecutando el siguiente comando desde tu terminal:
```bash
python -m pip install -r requirements.txt
```

### 3. Configurar tus credenciales
1.  Haz una copia del archivo `.env_ejemplo` y renombralo a `.env`.
2.  Ábrelo y coloca tus claves de API reales de los proveedores correspondientes:
    ```env
    OPENAI_API_KEY="tu_clave_de_openai_aqui"
    GEMINI_API_KEY="tu_clave_de_gemini_aqui"
    GROQ_API_KEY="tu_clave_de_groq_aqui"
    ```

### 4. Ejecutar cualquiera de los scripts
Una vez configurado todo, ejecuta cualquiera de los scripts en la terminal. Por ejemplo, para iniciar el chatbot de Gemini:
```bash
python "03 - chatbot_gemini.py"
```

---
> **Graduados FIUBA**: Este material ha sido desarrollado para fines educativos. ¡No dudes en experimentar alterando los prompts de sistema o cambiando los modelos utilizados para observar cómo cambia el comportamiento de las respuestas!
