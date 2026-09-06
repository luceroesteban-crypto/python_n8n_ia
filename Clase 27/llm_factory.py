"""
llm_factory.py - Fábrica de modelos de lenguaje (LLM)
=====================================================

Este módulo centraliza la creación del LLM. Permite cambiar de proveedor
(OpenAI, Google Gemini, Groq, Ollama, etc.) editando únicamente las
variables de configuración en `config.py`, sin tocar `rag_chain.py` ni
`app.py`.

La importación de cada integración ocurre dentro de la función, de modo
que solo es necesario tener instalado el paquete correspondiente al
proveedor elegido.

Autor: Clase 24 - IA Python para Principiantes
Fecha: 2026
"""

from config import LLM_MODEL, LLM_PROVIDER


def get_llm(temperature=None, max_tokens=None):
    """
    Crea y retorna una instancia del LLM configurado en `config.py`.

    Args:
        temperature (float, optional): Controla la creatividad de las
            respuestas. Si es None, se usa el default del proveedor.
        max_tokens (int, optional): Límite de tokens de salida. Si es None,
            se usa el default del proveedor.

    Returns:
        BaseChatModel: Instancia del LLM lista para usar en la cadena RAG.

    Raises:
        ValueError: Si el proveedor configurado no está soportado.
        ImportError: Si falta instalar el paquete del proveedor elegido.
        Exception: Si falla la inicialización (ej: API key inválida).
    """
    provider = LLM_PROVIDER.lower().strip()

    kwargs = {}
    if temperature is not None:
        kwargs["temperature"] = temperature
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens

    if provider in ("google", "google_genai", "gemini"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        # Timeout de 60s para evitar que una key/modelo inválido deje
        # la aplicación colgada indefinidamente.
        google_kwargs = {"timeout": 60}
        google_kwargs.update(kwargs)
        return ChatGoogleGenerativeAI(model=LLM_MODEL, **google_kwargs)

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=LLM_MODEL, **kwargs)

    if provider == "groq":
        from langchain_groq import ChatGroq
        # Groq usa 'model_name' en lugar de 'model' en algunas versiones
        return ChatGroq(model_name=LLM_MODEL, **kwargs)

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=LLM_MODEL, **kwargs)

    raise ValueError(
        f"Proveedor de LLM no soportado: '{LLM_PROVIDER}'. "
        f"Configura LLM_PROVIDER en config.py con uno de: "
        f"google, openai, groq, ollama."
    )


if __name__ == "__main__":
    # Pequeño sanity check: intenta crear la instancia y muestra info
    llm = get_llm()
    print(f"Proveedor: {LLM_PROVIDER}")
    print(f"Modelo: {LLM_MODEL}")
    print(f"Instancia: {type(llm).__name__}")
