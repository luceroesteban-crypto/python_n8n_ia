"""
rag_chain.py - Cadena RAG (Retrieval Augmented Generation)
===========================================================

Este módulo implementa la cadena RAG completa, que combina:
1. Búsqueda de documentos relevantes (Retrieval)
2. Generación de respuestas con LLM (Generation)

¿QUÉ ES RAG?
RAG = Retrieval Augmented Generation
- Recupera información relevante de una base de datos
- Aumenta el prompt del LLM con esa información
- Genera respuestas basadas en datos reales (no inventados)

Autor: Clase 24 - IA Python para Principiantes
Fecha: 2025
"""

from operator import itemgetter

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from config import (
    LLM_PROVIDER,
    LLM_MODEL,
    TOP_K_DOCUMENTS,
    K_RESULTADOS,
    MAX_CHAT_HISTORY,
    RAG_PROMPT_TEMPLATE,
    ERROR_NO_API_KEY,
    ERROR_MODEL_LOAD
)
from llm_factory import get_llm

# ==============================================================================
# CLASE: RAGChain
# ==============================================================================

class RAGChain:
    """
    Clase que implementa la cadena RAG completa.
    
    La cadena RAG es el "cerebro" de nuestro chatbot. Conecta:
    - El retriever (busca documentos)
    - El prompt template (formatea la pregunta)
    - El LLM (genera la respuesta)
    
    Esta arquitectura permite que el LLM responda basándose en
    documentos específicos en lugar de solo su conocimiento interno.
    """
    
    def __init__(self, database_manager):
        """
        Constructor de la cadena RAG.
        
        Args:
            database_manager (DatabaseManager): Instancia del gestor de base de datos
                que contiene los documentos y el retriever
                
        Raises:
            Exception: Si no se puede inicializar el LLM
        """
        self.database_manager = database_manager
        
        # Inicializar el modelo de lenguaje (LLM)
        self.llm = self._initialize_llm()
        
        # Crear el prompt template
        self.prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
        
        print("✅ Cadena RAG inicializada correctamente")
    
    def _initialize_llm(self):
        """
        Inicializa el modelo de lenguaje (LLM).

        Utiliza `llm_factory.get_llm()` para crear el modelo configurado en
        `config.py` a través de las variables `LLM_PROVIDER` y `LLM_MODEL`.
        De este modo, cambiar de proveedor (Google, OpenAI, Groq, Ollama, etc.)
        no requiere modificar este archivo.

        Returns:
            BaseChatModel: Instancia del LLM inicializada

        Raises:
            ImportError: Si no está instalado el paquete del proveedor elegido
            Exception: Si falla la inicialización (ej: API key inválida)

        Nota para estudiantes:
            La API key debe estar en el archivo .env con el nombre que espera
            cada proveedor (GOOGLE_API_KEY, OPENAI_API_KEY, GROQ_API_KEY, etc.).
            Ver README.md → "Cambiar el Proveedor de LLM".
        """
        try:
            print(f"🤖 Inicializando LLM: {LLM_PROVIDER} / {LLM_MODEL}")

            # Delegar la creación del LLM a la fábrica.
            # La fábrica se encarga de importar e instanciar la clase correcta.
            llm = get_llm()

            print(f"✅ LLM inicializado: {LLM_MODEL}")
            return llm

        except ImportError as e:
            error_msg = (
                f"❌ Error: falta instalar el paquete para el proveedor '{LLM_PROVIDER}'.\n"
                f"Detalle: {e}"
            )
            print(error_msg)
            raise

        except Exception as e:
            print(f"{ERROR_MODEL_LOAD}: {e}")
            print("\n💡 Posibles soluciones:")
            print(f"   1. Verifica la API key para el proveedor '{LLM_PROVIDER}'")
            print("   2. Verifica que la API key sea válida")
            print("   3. Verifica tu conexión a internet")
            raise
    
    def _format_context(self, docs):
        """
        Une los documentos recuperados en un único string para el prompt.

        EnsembleRetriever puede devolver más de k resultados cuando los rankings
        de BM25 y denso no se superponen. Limitamos a K_RESULTADOS para
        mantener el contexto manejable.
        """
        docs = docs[:K_RESULTADOS]
        context = "\n\n".join(doc.page_content for doc in docs)

        # Debug: mostrar qué contexto se recuperó para esta pregunta
        print("\n--- CONTEXTO RECUPERADO (rag_chain) ---")
        print(context if context else "(NINGUNO)")
        print("--- FIN CONTEXTO ---\n")

        return context

    def _format_chat_history(self, chat_history):
        """
        Formatea el historial de chat de Gradio para incluirlo en el prompt.

        Soporta dos formatos:
        - Lista de tuplas (mensaje_usuario, respuesta_bot)  [Gradio < 6]
        - Lista de dicts {'role': 'user'|'assistant', 'content': str}  [Gradio 6+]

        Se conservan los últimos MAX_CHAT_HISTORY intercambios para mantener
        el prompt acotado.

        Args:
            chat_history (list): Historial de Gradio

        Returns:
            str: Historial formateado o mensaje indicando que no hay historial
        """
        if not chat_history:
            return "No hay mensajes previos en esta conversación."

        lines = []

        # Detectar formato por el primer elemento
        if chat_history and isinstance(chat_history[0], dict):
            # Formato messages de Gradio 6+: cada elemento es un mensaje individual.
            # Un intercambio = 2 mensajes (user + assistant).
            recent = chat_history[-MAX_CHAT_HISTORY * 2:]
            for msg in recent:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    lines.append(f"Usuario: {content}")
                elif role == "assistant":
                    lines.append(f"Asistente: {content}")
        else:
            # Formato tuplas de Gradio < 6: cada elemento es un intercambio.
            recent = chat_history[-MAX_CHAT_HISTORY:]
            for user_msg, bot_msg in recent:
                lines.append(f"Usuario: {user_msg}")
                lines.append(f"Asistente: {bot_msg}")

        if not lines:
            return "No hay mensajes previos en esta conversación."

        return "\n".join(lines)

    def create_chain(self, k=TOP_K_DOCUMENTS):
        """
        Crea la cadena RAG completa usando LCEL (LangChain Expression Language),
        retriever HÍBRIDO (BM25 + búsqueda densa) y MEMORIA conversacional.

        LCEL es una forma declarativa de construir cadenas en LangChain.
        El operador | (pipe) conecta componentes secuencialmente.

        Flujo de la cadena:
        1. {question, chat_history} → retriever híbrido → context (documentos)
        2. {context, question, chat_history} → prompt (prompt formateado)
        3. prompt → llm (respuesta generada)
        4. llm → output_parser (texto limpio)

        Args:
            k (int): Número de documentos a recuperar por cada retriever

        Returns:
            Runnable: Cadena RAG ejecutable. Espera un dict con las claves
                      "question" y "chat_history".

        Ejemplo:
            >>> rag = RAGChain(db_manager)
            >>> chain = rag.create_chain(k=5)
            >>> response = chain.invoke({
            ...     "question": "¿Qué es Python?",
            ...     "chat_history": [("Hola", "¡Hola! ¿En qué puedo ayudarte?")]
            ... })

        Nota para estudiantes:
            Esta es la parte más importante del sistema RAG.
            Estudia cuidadosamente cómo se conectan los componentes.
        """
        # Obtener el retriever HÍBRIDO de la base de datos
        hybrid_retriever = self.database_manager.get_hybrid_retriever(k=k)

        # Construir la cadena usando LCEL (LangChain Expression Language)
        rag_chain = (
            # Paso 1: Preparar inputs
            # - "context": retriever busca docs similares a la pregunta
            # - "question": pasa la pregunta original sin modificar
            # - "chat_history": historial formateado para contexto conversacional
            {
                "context": itemgetter("question") | hybrid_retriever | self._format_context,
                "question": itemgetter("question"),
                "chat_history": itemgetter("chat_history"),
            }
            # Paso 2: Formatear el prompt
            | self.prompt
            # Paso 3: Generar respuesta
            | self.llm
            # Paso 4: Parsear la salida
            | StrOutputParser()
        )

        return rag_chain
    
    def query(self, question, chat_history=None, k=TOP_K_DOCUMENTS):
        """
        Realiza una consulta completa al sistema RAG con memoria conversacional.

        Este es el método principal que usarás para hacer preguntas.
        Internamente:
        1. Crea la cadena RAG
        2. Busca documentos relevantes
        3. Genera una respuesta basada en esos documentos y el historial

        Args:
            question (str): Pregunta del usuario
            chat_history (list): Lista de tuplas (user_msg, bot_msg) con la
                                  conversación previa. None o vacía si no hay.
            k (int): Número de documentos a recuperar (default: TOP_K_DOCUMENTS)

        Returns:
            str: Respuesta generada por el LLM

        Raises:
            Exception: Si hay error durante la generación

        Ejemplo:
            >>> rag = RAGChain(db_manager)
            >>> respuesta = rag.query("¿Qué es machine learning?")
            >>> print(respuesta)
            "Machine learning es una rama de la inteligencia artificial..."
        """
        try:
            print(f"\n🔍 Procesando pregunta: {question[:100]}...")

            # Crear la cadena RAG
            rag_chain = self.create_chain(k=k)

            # Formatear el historial de chat para el prompt
            formatted_history = self._format_chat_history(chat_history)

            # Invocar la cadena con la pregunta y el historial
            # Esto ejecuta todo el flujo: retrieval → prompt → LLM → parse
            response = rag_chain.invoke({
                "question": question,
                "chat_history": formatted_history
            })

            print(f"✅ Respuesta generada ({len(response)} caracteres)")

            return response

        except Exception as e:
            error_msg = f"❌ Error al generar respuesta: {e}"
            print(error_msg)
            # En lugar de fallar, retornar un mensaje de error al usuario
            return f"Lo siento, ocurrió un error al procesar tu pregunta: {str(e)}"
    
    def query_with_sources(self, question, chat_history=None, k=TOP_K_DOCUMENTS):
        """
        Realiza una consulta y retorna también los documentos fuente.

        Esto es útil para:
        - Transparencia: mostrar de dónde viene la información
        - Debugging: verificar qué documentos se recuperaron
        - Citación: dar crédito a las fuentes

        Args:
            question (str): Pregunta del usuario
            chat_history (list): Lista de tuplas (user_msg, bot_msg) con la
                                  conversación previa. None o vacía si no hay.
            k (int): Número de documentos a recuperar por cada retriever

        Returns:
            dict: Diccionario con la respuesta y las fuentes
                {
                    'answer': str,           # Respuesta generada
                    'sources': list,         # Lista de documentos fuente
                    'source_count': int      # Número de fuentes usadas
                }

        Ejemplo:
            >>> rag = RAGChain(db_manager)
            >>> result = rag.query_with_sources("¿Qué es RAG?")
            >>> print(result['answer'])
            >>> for i, doc in enumerate(result['sources']):
            ...     print(f"Fuente {i+1}: {doc.page_content[:100]}...")
        """
        try:
            # Obtener el retriever híbrido
            hybrid_retriever = self.database_manager.get_hybrid_retriever(k=k)

            # Buscar documentos relevantes y limitar a K_RESULTADOS
            source_docs = hybrid_retriever.invoke(question)[:K_RESULTADOS]

            # Generar la respuesta considerando el historial
            response = self.query(question, chat_history=chat_history, k=k)

            return {
                'answer': response,
                'sources': source_docs,
                'source_count': len(source_docs)
            }

        except Exception as e:
            print(f"❌ Error en query_with_sources: {e}")
            return {
                'answer': f"Error al procesar la pregunta: {str(e)}",
                'sources': [],
                'source_count': 0
            }

# ==============================================================================
# NOTAS PARA ESTUDIANTES
# ==============================================================================
"""
📚 CONCEPTOS IMPORTANTES:

1. RAG (Retrieval Augmented Generation):
   - Combina búsqueda (retrieval) con generación (LLM)
   - Soluciona el problema de "alucinaciones" del LLM
   - El LLM solo responde basado en documentos reales
   
2. LCEL (LangChain Expression Language):
   - Forma moderna de construir cadenas en LangChain
   - Operador | (pipe) conecta componentes
   - Más legible y componible que código imperativo
   
3. COMPONENTES DE LA CADENA:
   a) Retriever: Busca documentos relevantes
   b) Prompt Template: Formatea el contexto y la pregunta
   c) LLM: Genera la respuesta
   d) Output Parser: Limpia y formatea la salida
   
4. FLUJO DE DATOS:
   pregunta → [retriever] → documentos → [prompt] → mensaje → [LLM] → respuesta
   
5. TEMPERATURA DEL LLM:
   - 0.0: Determinista, siempre la misma respuesta
   - 0.7: Balanceado (recomendado)
   - 1.0+: Muy creativo, puede divagar

💡 EXPERIMENTOS SUGERIDOS:
   1. Cambia k de 5 a 3 y observa cómo afecta las respuestas
   2. Modifica el prompt template para cambiar el tono de las respuestas
   3. Implementa query_with_sources() en la interfaz para mostrar fuentes
   
⚠️ PREGUNTAS PARA REFLEXIONAR:
   - ¿Qué pasa si el retriever no encuentra documentos relevantes?
   - ¿Cómo afecta el número k a la calidad de las respuestas?
   - ¿Por qué es importante el prompt template en RAG?
   
🎯 EJERCICIO AVANZADO:
   Modifica create_chain() para agregar un paso de "re-ranking"
   que ordene los documentos recuperados por relevancia antes
   de enviarlos al LLM.
"""
