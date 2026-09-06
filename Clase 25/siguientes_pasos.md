# Paso siguiente: conectar un LLM para responder preguntas con RAG

Este documento es un ejemplo conceptual de cómo conectar la base vectorial
(`db_chroma`) generada por `ingesta.py` con un LLM para armar un sistema de
Preguntas y Respuestas (RAG = Retrieval Augmented Generation).

Incluye el código de ejemplo comentado, más las recomendaciones de
actualización a **LangChain v1** (con `langchain-classic`) detectadas en la
revisión, junto con su justificación.

---

## 1. Imports actualizados (estructura moderna de LangChain)

```python
# Para LLMs, ahora cada proveedor tiene su propio paquete:
from langchain_openai import ChatOpenAI        # Para OpenAI/ChatGPT
from langchain_anthropic import ChatAnthropic  # Para Claude
from langchain_google_genai import ChatGoogleGenerativeAI  # Para Gemini
from langchain_ollama import ChatOllama        # Para modelos locales con Ollama
from langchain_groq import ChatGroq            # Para Groq (rápido y gratuito)

# Para la base vectorial:
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
```

**Estado: correcto, sin cambios.** El modelo "un proveedor = un paquete"
(`langchain-openai`, `langchain-anthropic`, `langchain-google-genai`,
`langchain-ollama`, `langchain-groq`, `langchain-huggingface`,
`langchain-chroma`) no fue afectado por la reestructuración de LangChain v1.

### ⚠️ Actualización necesaria: imports de chains

```python
# Para las chains de Q&A:
# (Esta estructura de imports correspondía a LangChain 0.1.x–0.3.x, es decir,
# a las versiones previas a v1.0. RetrievalQA quedó deprecado desde la 0.1.17
# —y se reafirmó en la 0.2.13— en favor de create_retrieval_chain, ambos
# todavía dentro de `langchain.chains` en esas versiones.)
from langchain.chains import RetrievalQA  # ⚠️ DEPRECADO
from langchain.chains import create_retrieval_chain  # ⚠️ DEPRECADO -> ver justificación
from langchain.chains.combine_documents import create_stuff_documents_chain
```

**Justificación:** con LangChain v1, el paquete `langchain` se simplificó
("Simplified namespace") para enfocarse en bloques de construcción de agentes
(`create_agent`, mensajes, tools, modelos). **Todo `langchain.chains`
—incluyendo `create_retrieval_chain` y `create_stuff_documents_chain`, no solo
`RetrievalQA`— fue movido al paquete `langchain-classic`**, que agrupa
"legacy chains and chain implementations", retrievers antiguos, indexing API,
hub module y re-exports de `langchain-community`.

Esto significa que `create_retrieval_chain`, que en su momento reemplazó a
`RetrievalQA` como forma recomendada, **hoy está igual de deprecado**: ambos
viven ahora en el paquete `langchain-classic` en vez de en `langchain`.

Import correcto si igual se quiere usar (requiere `pip install langchain-classic`):

```python
from langchain_classic.chains import RetrievalQA
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
```

---

## 2. Ejemplos de inicialización de LLM

```python
# EJEMPLO 1: USANDO OPENAI (requiere API key y créditos)
import os
os.environ["OPENAI_API_KEY"] = "tu-api-key-aqui"

llm = ChatOpenAI(
    model="gpt-3.5-turbo",  # o "gpt-4"
    temperature=0  # 0 = más determinista, 1 = más creativo
)

# EJEMPLO 2: USANDO GROQ (gratuito, rápido, requiere API key)
import os
os.environ["GROQ_API_KEY"] = "tu-api-key-aqui"

from langchain_groq import ChatGroq
llm = ChatGroq(
    model="llama-3.1-70b-versatile",  # Modelo gratuito y potente
    temperature=0
)

# EJEMPLO 3: USANDO OLLAMA (100% local, sin API key, sin internet)
# Primero instala Ollama desde: https://ollama.ai
# Luego descarga un modelo: ollama pull llama3.2

from langchain_ollama import ChatOllama
llm = ChatOllama(
    model="llama3.2",  # o "mistral", "phi3", etc.
    temperature=0
)
```

**Estado: correcto, sin cambios.** Ninguno de estos tres ejemplos usa
funcionalidad movida a `langchain-classic`.

---

## 3. Cargar la base vectorial

```python
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

vectordb = Chroma(
    persist_directory="db_chroma",
    embedding_function=embeddings
)

# Crear el retriever (recuperador de documentos)
retriever = vectordb.as_retriever(
    search_type="mmr",  # Usar MMR para diversidad
    search_kwargs={"k": 3, "fetch_k": 20}  # Parámetros de búsqueda
)
```

**Estado: correcto, sin cambios.**

---

## 4. Método antiguo (deprecado) ⚠️

```python
from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # "stuff" mete todos los docs en el prompt
    retriever=retriever
)
respuesta = qa_chain.run("¿Qué es LangChain?")  # .run() está deprecado
print(respuesta)
```

**Estado: sigue siendo el método más desactualizado**, y además el import
ahora requiere `langchain-classic` (ver punto 1). Mantiene su etiqueta de
"deprecado".

---

## 5. Método "moderno" con chains — hoy también deprecado ⚠️

```python
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. Crear un prompt personalizado
system_prompt = (
    "Eres un asistente útil. Usa el siguiente contexto para responder la pregunta. "
    "Si no sabes la respuesta, di que no lo sabes. No inventes información.\n\n"
    "Contexto: {context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

# 2. Crear la chain de documentos
question_answer_chain = create_stuff_documents_chain(llm, prompt)

# 3. Crear la chain de recuperación completa
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# 4. Hacer una pregunta (usa .invoke() en vez de .run())
resultado = rag_chain.invoke({"input": "¿Qué es LangChain?"})

print("Respuesta:", resultado["answer"])
print("\nDocumentos usados:")
for i, doc in enumerate(resultado["context"]):
    print(f"{i+1}. Fuente: {doc.metadata.get('source')}")
```

**Justificación:** este método solía considerarse la forma recomendada de
implementar RAG (reemplazo directo de `RetrievalQA`). Con LangChain v1 pasó a
estar **deprecado**: tanto
`create_retrieval_chain` como `create_stuff_documents_chain` fueron movidos a
`langchain-classic` junto con el resto de las "legacy chain implementations".
Sigue siendo funcional (instalando `langchain-classic`), pero LangChain ya no
lo posiciona como el camino a seguir para RAG.

---

## 6. Alternativa simple: retriever + LLM directo ✅ (sigue vigente)

```python
pregunta = "¿Qué es LangChain?"

# 1. Recuperar documentos relevantes
docs = retriever.invoke(pregunta)

# 2. Crear el contexto
contexto = "\n\n".join([doc.page_content for doc in docs])

# 3. Crear el prompt manualmente
prompt_text = f"""Responde la siguiente pregunta basándote en el contexto proporcionado.
Si no puedes responder con el contexto dado, di que no lo sabes.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""

# 4. Enviar al LLM
respuesta = llm.invoke(prompt_text)
print(respuesta.content)
```

**Estado: correcto y es la opción que mejor envejeció.** No depende de
`langchain.chains` ni de `langchain-classic`; solo usa `retriever.invoke()`
y `llm.invoke()`, ambos parte del núcleo estable de LangChain.

---

## 7. Recomendación para la clase: el enfoque realmente "nuevo" en v1

Ninguna de las dos chains (`RetrievalQA` ni `create_retrieval_chain`) es hoy
el camino recomendado por LangChain. Con v1, el framework se reorientó hacia
**agentes** como abstracción principal. Para investigar de cara a la próxima
clase:

- **`create_agent`** (`langchain.agents`, incluido en el núcleo de v1, sin
  necesitar `langchain-classic`): permite exponer el `retriever` como una
  *tool* y dejar que el agente decida cuándo consultarlo, en vez de armar una
  chain fija de recuperación + respuesta.
- Investigar cómo envolver `retriever.invoke()` como una tool (`@tool`) y
  pasarla a `create_agent(model, tools=[...])`.

### Resumen de estados

| Método | Estado en LangChain v1 | Paquete requerido |
|---|---|---|
| `RetrievalQA` | ⚠️ Deprecado | `langchain-classic` |
| `create_retrieval_chain` + `create_stuff_documents_chain` | ⚠️ Deprecado | `langchain-classic` |
| Retriever + LLM directo (manual) | ✅ Vigente | Núcleo (`langchain-core`) |
| `create_agent` con retriever como tool | ✅ Nuevo enfoque recomendado en v1 | Núcleo (`langchain`) |

---

## 8. Recurso recomendado para investigar

- **[Introduction to LangChain (LangChain Academy)](https://academy.langchain.com/courses/foundation-introduction-to-langchain-python)**
