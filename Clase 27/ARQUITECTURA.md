# 🏗️ Arquitectura del Sistema RAG

## 📊 Diagrama de Flujo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMA RAG COMPLETO                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  FASE 1: INGESTA DE DOCUMENTOS (document_processor.py)         │
└─────────────────────────────────────────────────────────────────┘

    📄 Archivos PDF/TXT
           ↓
    ┌─────────────┐
    │  1. CARGAR  │  ← PyPDFLoader, TextLoader
    └─────────────┘
           ↓
    📚 Documentos LangChain
           ↓
    ┌─────────────┐
    │ 2. DIVIDIR  │  ← RecursiveCharacterTextSplitter
    └─────────────┘     chunk_size=1500, overlap=250
           ↓
    📑 Chunks (fragmentos pequeños)
           ↓
    ┌─────────────┐
    │ 3. EMBEDAR  │  ← HuggingFaceEmbeddings
    └─────────────┘     (paraphrase-multilingual-MiniLM-L12-v2)
           ↓
    🔢 Vectores [0.2, 0.8, -0.3, ...]
           ↓
    ┌─────────────┐
    │ 4. GUARDAR  │  ← ChromaDB
    └─────────────┘
           ↓
    💾 Base de Datos Vectorial


┌─────────────────────────────────────────────────────────────────┐
│  FASE 2: CONSULTA (rag_chain.py)                               │
└─────────────────────────────────────────────────────────────────┘

    💬 Pregunta del Usuario
           ↓
    ┌──────────────────┐
    │  1. EMBEDAR      │  ← Mismo modelo de embeddings
    └──────────────────┘
           ↓
    🔢 Vector de la pregunta
           ↓
    ┌──────────────────────────────────────────┐
    │  2. BUSCAR (HÍBRIDO)                     │
    │  - ChromaDB.similarity_search() (denso) │
    │  - BM25RetrieverLocal (léxico)           │
    │  - EnsembleRetriever (RRF ponderado)     │
    └──────────────────────────────────────────┘
           ↓
    📑 Top chunks más similares
           ↓
    ┌──────────────────┐
    │  3. FORMATEAR    │  ← ChatPromptTemplate
    └──────────────────┘     {context} + {question}
           ↓
    📝 Prompt completo
           ↓
    ┌──────────────────┐
    │  4. GENERAR      │  ← LLM (Google Gemini por defecto)
    └──────────────────┘     Se puede cambiar por OpenAI, Groq, Ollama, etc.
           ↓
    💡 Respuesta basada en documentos


┌─────────────────────────────────────────────────────────────────┐
│  FASE 3: INTERFAZ (app_refactorizado.py)                       │
└─────────────────────────────────────────────────────────────────┘

    👤 Usuario
           ↓
    ┌──────────────────┐
    │  Interfaz Gradio │
    └──────────────────┘
           ↓
    ┌──────────────────┬──────────────────┬──────────────────┐
    │   💬 Chatbot    │  📚 Gestión      │  ℹ️ Info        │
    │                  │   Documentos      │                  │
    │  - Chat          │  - Cargar         │  - Ayuda         │
    │  - Historial     │  - Estadísticas   │  - Documentación │
    └──────────────────┴──────────────────┴──────────────────┘
```

## 🔄 Flujo Detallado de una Pregunta (LCEL)

```
┌──────────────────────────────────────────────────────────────────┐
│  CADENA RAG CON LCEL (LangChain Expression Language)            │
└──────────────────────────────────────────────────────────────────┘

    { "question": "¿Qué es Python?", "chat_history": "..." }  ← Input del usuario
           ↓
    ┌─────────────────────────────────────────┐
    │  PASO 1: Preparar Inputs                │
    │  {                                       │
    │    "context": retriever,  ──────┐      │
    │    "question": itemgetter("question") ─┐│
    │    "chat_history": itemgetter("chat_history") │
    │  }                                  │ │ │
    └─────────────────────────────────────│─│─┘
                                          │ │
                Búsqueda en ChromaDB ◄────┘ │
                         ↓                   │
                "Python es un lenguaje..."   │
                "Python fue creado..."       │
                "Python se usa para..."      │
                         ↓                   │
           context = [doc1, doc2, doc3]     │
                         ├──────────────────►│
                         ↓                   ↓
    ┌─────────────────────────────────────────┐
    │  PASO 2: Formatear Prompt               │
    │  prompt_template.format(                │
    │    context="Python es un lenguaje..."   │
    │    chat_history="Usuario: Hola\nAsistente: ..."
    │    question="¿Qué es Python?"           │
    │  )                                       │
    └─────────────────────────────────────────┘
                         ↓
    "Eres un asistente...
     Historial reciente: ...
     Contexto: Python es un lenguaje...
     Pregunta: ¿Qué es Python?
     Respuesta:"
                         ↓
    ┌─────────────────────────────────────────┐
    │  PASO 3: Enviar al LLM                  │
    │  ChatGoogleGenerativeAI.invoke()        │
    └─────────────────────────────────────────┘
                         ↓
    AIMessage(content="Python es un lenguaje...")
                         ↓
    ┌─────────────────────────────────────────┐
    │  PASO 4: Parsear Salida                 │
    │  StrOutputParser()                      │
    └─────────────────────────────────────────┘
                         ↓
    "Python es un lenguaje de programación..."  ← Respuesta final
```

## 🧩 Interacción entre Módulos

```
┌─────────────────────────────────────────────────────────────────┐
│                      DEPENDENCIAS                                │
└─────────────────────────────────────────────────────────────────┘

    config.py  ← Base (sin dependencias)
       ↓
       ├────────────────┬────────────────────────┬─────────────────┐
       ↓                ↓                        ↓                 ↓
  llm_factory.py  database_manager.py   document_processor.py  app_refactorizado.py
                          │                                      ↑
                          ↓                                      │
                   retrievers.py                                 │
                          │                                      │
                          ↓                                      │
                   rag_chain.py ────────────────────────────────┘
                          │
                          ├─ usa llm_factory.py
                          └─ usa database_manager.py


┌─────────────────────────────────────────────────────────────────┐
│                  FLUJO DE DATOS                                  │
└─────────────────────────────────────────────────────────────────┘

[Usuario] → [Gradio UI] → [app_refactorizado]
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
          [DocumentProcessor] [DatabaseManager] [RAGChain]
                    ↓               ↓               ↓
                [Archivos]      [ChromaDB]       [LLM]
```

## 📦 Estructura de Clases

```
┌──────────────────────────────────────────────────────────────┐
│  CLASS DatabaseManager                                       │
├──────────────────────────────────────────────────────────────┤
│  Atributos:                                                  │
│    - embeddings: HuggingFaceEmbeddings                      │
│    - vectordb: Chroma                                        │
│                                                              │
│  Métodos:                                                    │
│    + __init__()                                             │
│    + add_documents(documents)                               │
│    + get_retriever(k)                                       │
│    + get_hybrid_retriever(k)                                │
│    + get_stats()                                            │
│    + clear_all_documents()                                  │
└──────────────────────────────────────────────────────────────┘

                          △
                          │ usa
                          │
┌──────────────────────────────────────────────────────────────┐
│  MODULE llm_factory.py                                       │
├──────────────────────────────────────────────────────────────┤
│  Funciones:                                                  │
│    + get_llm(temperature, max_tokens)                       │
│       → soporta Google, OpenAI, Groq, Ollama                │
└──────────────────────────────────────────────────────────────┘
                          △
                          │ usa
                          │
┌──────────────────────────────────────────────────────────────┐
│  CLASS BM25RetrieverLocal (retrievers.py)                    │
├──────────────────────────────────────────────────────────────┤
│  Atributos:                                                  │
│    - documentos: List[Document]                              │
│    - k: int                                                  │
│    - vectorizador: BM25Okapi                                 │
│                                                              │
│  Métodos:                                                    │
│    + __init__(documentos, k)                                │
│    + _get_relevant_documents(query)                         │
└──────────────────────────────────────────────────────────────┘
                          △
                          │ usa
                          │
┌──────────────────────────────────────────────────────────────┐
│  CLASS DocumentProcessor                                     │
├──────────────────────────────────────────────────────────────┤
│  Atributos:                                                  │
│    - chunk_size: int                                         │
│    - chunk_overlap: int                                      │
│    - text_splitter: RecursiveCharacterTextSplitter          │
│                                                              │
│  Métodos:                                                    │
│    + __init__(chunk_size, chunk_overlap)                    │
│    + load_file(file_path)                                   │
│    + load_multiple_files(file_paths)                        │
│    + split_documents(documents)                             │
│    + process_files(file_paths)                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  CLASS RAGChain                                              │
├──────────────────────────────────────────────────────────────┤
│  Atributos:                                                  │
│    - database_manager: DatabaseManager                       │
│    - llm: ChatGoogleGenerativeAI                            │
│    - prompt: ChatPromptTemplate                             │
│                                                              │
│  Métodos:                                                    │
│    + __init__(database_manager)                             │
│    + create_chain(k)                                        │
│    + query(question, k)                                     │
│    + query_with_sources(question, k)                        │
└──────────────────────────────────────────────────────────────┘
```

## 🎯 Patrón de Diseño: Separación de Responsabilidades

```
┌──────────────────────────────────────────────────────────────┐
│  PRINCIPIO: Single Responsibility Principle (SRP)           │
└──────────────────────────────────────────────────────────────┘

Cada módulo tiene UNA responsabilidad principal:

📄 config.py
   └─► Almacenar configuración

🏭 llm_factory.py
   └─► Crear instancia del LLM según proveedor configurado

💾 database_manager.py
   └─► Gestionar base de datos vectorial

📑 document_processor.py
   └─► Procesar documentos

🔍 retrievers.py
   └─► Implementar retriever léxico BM25

🔗 rag_chain.py
   └─► Implementar lógica RAG

🖥️ app_refactorizado.py
   └─► Gestionar interfaz de usuario
```

## 🔍 Búsqueda por Similaridad Vectorial

```
┌──────────────────────────────────────────────────────────────┐
│  CÓMO FUNCIONA LA BÚSQUEDA VECTORIAL                         │
└──────────────────────────────────────────────────────────────┘

1. PREGUNTA DEL USUARIO:
   "¿Qué es Python?"
        ↓ (embedding)
   [0.2, 0.8, -0.3, 0.5, ...]  ← Vector de 384 dimensiones

2. DOCUMENTOS EN LA BASE DE DATOS:
   Doc1: "Python es un lenguaje..."
         [0.21, 0.79, -0.31, 0.48, ...]  ← Similaridad: 0.95 ✅

   Doc2: "JavaScript es un lenguaje..."
         [0.18, 0.82, -0.28, 0.52, ...]  ← Similaridad: 0.88 ✅

   Doc3: "La receta de la pizza..."
         [-0.5, 0.1, 0.9, -0.3, ...]     ← Similaridad: 0.12 ❌

3. RESULTADO:
   Se retornan los documentos con mayor similaridad (top_k)
   En este caso: Doc1 y Doc2


MEDIDA DE SIMILARIDAD (Distancia Coseno):
   
    Vector A    Vector B
       ↓           ↓
      [...]       [...]
         \         /
          \       /
           \     /
            \   /    ← Ángulo θ
             \ /
              ×
              
   Similaridad = cos(θ)
   - 1.0  = Idénticos
   - 0.0  = Perpendiculares (no relacionados)
   - -1.0 = Opuestos
```

## 💡 Ventajas de la Arquitectura Modular

```
┌────────────────────────────────────────────────────────────────┐
│  VENTAJAS                                                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ MANTENIBILIDAD                                             │
│     Cambios aislados en un módulo no afectan otros            │
│                                                                 │
│  ✅ TESTING                                                    │
│     Cada módulo se puede probar independientemente             │
│                                                                 │
│  ✅ REUSABILIDAD                                               │
│     Los módulos se pueden usar en otros proyectos             │
│                                                                 │
│  ✅ COLABORACIÓN                                               │
│     Diferentes personas pueden trabajar en módulos diferentes  │
│                                                                 │
│  ✅ COMPRENSIÓN                                                │
│     Código más fácil de entender y aprender                   │
│                                                                 │
│  ✅ ESCALABILIDAD                                              │
│     Agregar funcionalidades sin romper lo existente           │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## 🚀 Puntos de Extensión

```
┌────────────────────────────────────────────────────────────────┐
│  CÓMO EXTENDER EL SISTEMA                                      │
└────────────────────────────────────────────────────────────────┘

1. AGREGAR NUEVOS TIPOS DE DOCUMENTOS:
   document_processor.py → Agregar nuevo loader

2. CAMBIAR BASE DE DATOS VECTORIAL:
   database_manager.py → Reemplazar Chroma por Pinecone/Weaviate

3. USAR OTRO LLM:
   rag_chain.py → Cambiar ChatGoogleGenerativeAI por ChatOpenAI

4. MEJORAR RETRIEVAL:
   rag_chain.py → Agregar re-ranking, filtros, metadata

5. AGREGAR FUNCIONALIDADES UI:
   app_refactorizado.py → Nuevas pestañas, componentes

6. IMPLEMENTAR CACHÉ:
   rag_chain.py → Cachear respuestas frecuentes

7. MULTI-IDIOMA:
   config.py → Múltiples RAG_PROMPT_TEMPLATE
```

## 📚 Para Profundizar

```
┌────────────────────────────────────────────────────────────────┐
│  TEMAS AVANZADOS                                               │
└────────────────────────────────────────────────────────────────┘

1. 🧮 EMBEDDINGS:
   - Modelos multilíngües
   - Fine-tuning de embeddings
   - Dimensionality reduction

2. 🔍 RETRIEVAL:
   - Hybrid search (vectorial + keyword)
   - Re-ranking
   - Metadata filtering

3. 🤖 LLM:
   - Temperature tuning
   - Max tokens optimization
   - Streaming responses

4. 💾 BASES DE DATOS:
   - Índices HNSW
   - Quantization
   - Distributed systems

5. 🎨 PROMPTS:
   - Few-shot learning
   - Chain of thought
   - Prompt engineering

6. 🏗️ ARQUITECTURA:
   - Microservicios
   - Async processing
   - Caching strategies
```

---

💡 **Este documento complementa el README.md con detalles técnicos de arquitectura**
