# Mejoras propuestas: embeddings y métodos de búsqueda

## Situación actual

`ingesta.py` usa:

```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

Este modelo está entrenado **principalmente en inglés**. Los documentos
fuente del proyecto (`datos.txt` y `documento.pdf`, este último con la
Constitución de la Nación Argentina) están **en español**, por lo que no es
el modelo más adecuado para este caso de uso.

Esto se pudo observar en las pruebas de `consulta.py`: al preguntar
`'¿Qué es LangChain?'` con `documento.pdf` (Constitución) cargado en la base,
los resultados devueltos eran artículos de la Constitución poco
relacionados semánticamente con la pregunta.

## Alternativas evaluadas

### Multilingües (recomendadas para este proyecto, dado que el contenido está en español)

| Modelo | Notas |
|---|---|
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Mismo tamaño/familia que el modelo actual (rápido, liviano), pero con soporte real de español. Reemplazo directo más simple. |
| `intfloat/multilingual-e5-large` | Mejor calidad, pero más pesado (más lento en CPU). Requiere prefijos `"query: "` / `"passage: "` en los textos para mejor rendimiento. |
| `BAAI/bge-m3` | Multilingüe, soporta contextos largos (8192 tokens) y búsqueda densa+dispersa. Mencionado en la documentación oficial de LangChain como recomendado para proyectos nuevos. |

### Solo inglés (si los documentos fueran en inglés)

| Modelo | Notas |
|---|---|
| `sentence-transformers/all-mpnet-base-v2` | Mejor calidad que MiniLM, algo más lento. |
| `intfloat/e5-large-v2` | Recomendado en la doc de LangChain para embeddings "instruction-aware". |

## Recomendación

Cambiar `EMBEDDING_MODEL` en `ingesta.py` (y en `consulta.py` /
`consulta_filtrada.py`, que cargan el mismo modelo para hacer las consultas)
a:

```python
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

Es el reemplazo más directo (mismo tamaño/velocidad) pero con soporte real de
español, lo que debería mejorar los resultados de similitud frente a los
observados en las pruebas actuales.

Si se busca más calidad a costa de velocidad, `BAAI/bge-m3` es la opción más
robusta.

> Nota: cualquier cambio de modelo de embeddings requiere volver a correr
> `ingesta.py` para regenerar `db_chroma`, ya que los vectores existentes
> fueron generados con un modelo distinto y no son compatibles entre sí.

## Alternativa: embeddings de OpenAI y otros proveedores (vía API)

Todas las opciones anteriores (`sentence-transformers/*`, `BAAI/bge-m3`,
`intfloat/*`) corren **localmente y son gratuitas**, pero existe la
alternativa de usar embeddings **comerciales vía API**, generalmente con
mejor calidad de recuperación a costa de costo por uso, latencia de red y
dependencia de una API key.

### OpenAI (`langchain-openai`)

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",  # o "text-embedding-3-small"
    # dimensions=1024  # opcional: reduce el tamaño del vector (solo modelos "3")
)
```

| Modelo | Dimensiones (default) | Notas |
|---|---|---|
| `text-embedding-3-small` | 1536 | Más económico, buen punto de partida. |
| `text-embedding-3-large` | 3072 | Mejor calidad; permite reducir dimensiones con el parámetro `dimensions` (ej. `1024`) para ahorrar espacio en la DB vectorial sin perder demasiada calidad. |

Estos modelos son **multilingües** (soportan español sin problema), por lo
que resuelven el problema de idioma mencionado arriba sin necesidad de
buscar un modelo específico multilingüe. Requiere `OPENAI_API_KEY` y tiene
costo por token procesado (ingesta + cada consulta).

### Google (Gemini / Vertex AI)

```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004"  # también disponible: gemini-embedding-001
)
```

Requiere el paquete `langchain-google-genai` (o `langchain-google-vertexai`
si se usa vía Vertex AI en GCP en lugar de la API directa de Google AI
Studio) y una `GOOGLE_API_KEY`. Es multilingüe y, según datos de la
industria, es una de las opciones más económicas del mercado en costo por
token.

### Anthropic (Claude) — aclaración importante

**Anthropic no ofrece un modelo de embeddings propio.** Claude es un modelo
de generación de texto (chat/completions), no genera vectores de embeddings.
Para RAG con Claude como LLM de respuesta, Anthropic recomienda oficialmente
usar un proveedor externo de embeddings —principalmente **Voyage AI**— y
combinarlo con Claude solo para la parte de generación:

```python
# Ejemplo conceptual: embeddings con Voyage AI + generación con Claude
from langchain_voyageai import VoyageAIEmbeddings
from langchain_anthropic import ChatAnthropic

embeddings = VoyageAIEmbeddings(model="voyage-3-large")  # o "voyage-3.5"
llm = ChatAnthropic(model="claude-sonnet-4-5")
```

Es decir: si en el futuro se quisiera usar Claude como LLM de respuesta en
este proyecto (ver `siguientes_pasos.md`), la base vectorial (embeddings)
seguiría necesitando otro proveedor (HuggingFace local, OpenAI, Google,
Cohere o Voyage AI) — Anthropic no es una opción para esa parte del
pipeline.

### Otros proveedores soportados por LangChain

| Proveedor | Paquete | Clase | Notas |
|---|---|---|---|
| Cohere | `langchain-cohere` | `CohereEmbeddings` | Buen soporte multilingüe (`embed-multilingual-v3.0`), pensado para retrieval. |
| Mistral AI | `langchain-mistralai` | `MistralAIEmbeddings` | Modelo `mistral-embed`, requiere API key de Mistral. |
| Voyage AI | `langchain-voyageai` | `VoyageAIEmbeddings` | Proveedor recomendado por Anthropic para embeddings (ver arriba). Modelos `voyage-3-large`, `voyage-3.5`, `voyage-code-3` (optimizado para código). |
| Azure OpenAI | `langchain-openai` | `AzureOpenAIEmbeddings` | Mismos modelos que OpenAI, pero alojados en infraestructura de Azure (útil si ya se usa Azure por temas de compliance/región). |
| Ollama (local, distinto a HuggingFace) | `langchain-ollama` | `OllamaEmbeddings` | Corre modelos de embeddings localmente vía Ollama (ej. `qwen3-embedding`), sin costo de API pero sin depender de `sentence-transformers`/sin descargar pesos de HuggingFace directamente. |

### Comparación rápida: local (HuggingFace) vs. API (OpenAI, Google, Voyage, etc.)

| Criterio | Local (`langchain-huggingface`, actual) | API (OpenAI, Google, Cohere, Voyage, etc.) |
|---|---|---|
| Costo | Gratis (solo cómputo local) | Pago por token |
| Privacidad | Los datos no salen de la máquina | Los documentos se envían a un servicio externo |
| Calidad multilingüe | Depende del modelo elegido (ver alternativas de arriba) | En general muy buena de forma nativa (OpenAI, Cohere, Google) |
| Latencia | Depende de la CPU/GPU local | Depende de la red + rate limits del proveedor |
| Setup | Sin API key, pero requiere descargar pesos (~cientos de MB) | Requiere API key y conexión a internet |

### Recomendación

Para este proyecto (uso educativo, con documentos en español, sin
requerimientos de privacidad estrictos), la opción local multilingüe
(`paraphrase-multilingual-MiniLM-L12-v2` o `BAAI/bge-m3`) sigue siendo
razonable por ser gratuita y no depender de conectividad ni API keys. Si en
el futuro se prioriza calidad de recuperación por sobre costo/privacidad,
`OpenAIEmbeddings(model="text-embedding-3-small")` es la alternativa más
simple de integrar (mismo patrón `HuggingFaceEmbeddings` → `OpenAIEmbeddings`,
sin cambiar el resto del pipeline de `langchain_chroma`).

---

# Observación: métodos de búsqueda en `consulta.py` y `consulta_filtrada.py`

## Situación actual

- **`consulta.py`** usa `max_marginal_relevance_search` (MMR) con
  `k=3, fetch_k=20, lambda_mult=0.5`, y deja comentada la alternativa con
  `similarity_search`.
- **`consulta_filtrada.py`** usa `similarity_search` simple con `k=3`, con
  filtro opcional por `metadata["source"]`.

En las pruebas realizadas (`'¿Qué es LangChain?'` sobre la base con
`documento.pdf` de la Constitución + `datos.txt`), ambos scripts devolvieron
resultados poco relevantes semánticamente (artículos de la Constitución sin
relación con la pregunta). Esto se debe en gran parte al modelo de
embeddings (ver sección anterior), pero también hay margen de mejora en la
estrategia de recuperación en sí.

## Recomendaciones para mejorar la recuperación

### 1. Usar `similarity_search_with_score` para depurar relevancia
Ninguno de los dos scripts muestra el score de similitud de cada resultado,
por lo que no hay forma de saber si un resultado devuelto es realmente
relevante o simplemente "el menos malo" de la base. Se recomienda usar:

```python
results = vectordb.similarity_search_with_score(query_text, k=3)
for doc, score in results:
    print(f"Score: {score:.4f} | Fuente: {doc.metadata.get('source')}")
```

Esto permite fijar un umbral de corte y descartar resultados poco relevantes
en vez de mostrar siempre `k` documentos aunque ninguno sea bueno.

### 2. Retriever con `score_threshold` en vez de `k` fijo
En lugar de forzar siempre 3 resultados, conviene usar
`search_type="similarity_score_threshold"` para descartar documentos que no
superen un mínimo de similitud:

```python
retriever = vectordb.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.5, "k": 5}
)
resultados = retriever.invoke(query_text)
```

Así, si la pregunta no tiene relación con ningún documento de la base (como
pasó con `'¿Qué es LangChain?'` sobre la Constitución), el sistema puede
devolver "sin resultados relevantes" en vez de forzar 3 fragmentos poco
útiles.

### 3. Ajustar los parámetros de MMR en `consulta.py`
El `lambda_mult=0.5` balancea relevancia y diversidad por igual. Si el
objetivo es priorizar precisión (evitar resultados poco relacionados), subir
`lambda_mult` hacia `0.7`-`0.8` favorece la relevancia sobre la diversidad.
También conviene bajar `fetch_k` si la base es chica (como en este caso, 75
chunks): `fetch_k=20` sobre una base tan pequeña ya cubre gran parte de la
colección, con poco beneficio real de MMR.

### 4. Aprovechar el filtro por metadata también en `consulta.py`
`consulta_filtrada.py` ya soporta filtrar por `source`, pero `consulta.py`
no. Sería útil unificar ambos scripts (o agregar el parámetro opcional de
filtro a `consulta.py`) para poder combinar MMR + filtro por fuente, y así
evitar que una pregunta sobre "LangChain" recupere fragmentos de la
Constitución simplemente porque comparten vocabulario general en español.

### 5. Combinar búsqueda densa con búsqueda por palabras clave (híbrida)
Para consultas donde el vocabulario específico importa (nombres propios,
términos técnicos como "LangChain", "LangGraph"), una búsqueda puramente
vectorial puede fallar si el embedding no captura bien esos términos
(agravado por el problema de idioma del modelo actual). Se recomienda
evaluar un enfoque híbrido combinando:

- Búsqueda vectorial (la actual, con Chroma).
- Búsqueda por keywords/BM25 (por ejemplo con `rank_bm25` o el
  `BM25Retriever` de LangChain) sobre el mismo conjunto de documentos.

Y combinar ambos resultados con un `EnsembleRetriever` (le da peso relativo
a cada retriever) para mejorar recall en consultas donde el término exacto
importa más que el significado general.

### 6. Reindexar tras cambiar el modelo de embeddings
Cualquiera de estas mejoras de búsqueda rendirá mucho mejor una vez resuelto
el problema de idioma del modelo de embeddings (sección anterior). Se
recomienda aplicar primero el cambio de modelo, volver a correr `ingesta.py`,
y luego volver a probar estas estrategias de búsqueda para comparar
resultados de forma justa.

---

# Implementación aplicada en `Clase 26`

Los archivos de `Clase 26` (`ingesta.py`, `consulta.py`,
`consulta_filtrada.py`, `requirements.txt` y el nuevo `retrievers.py`)
aplican las siguientes decisiones:

## 1. Nuevo módulo `retrievers.py` (separación de responsabilidades)

Para no sobrecargar `consulta.py` y `consulta_filtrada.py` con la
implementación de BM25, se extrajo todo lo relacionado al retriever
léxico a un módulo propio:

- `BM25RetrieverLocal`: hereda de `BaseRetriever` para ser compatible con
  `EnsembleRetriever`.
- `_tokenizar_basico`: tokenizador para BM25.
- `construir_bm25_desde_vectordb`: construye el BM25 a partir de los
  documentos ya persistidos en Chroma, en vez de releer los archivos
  fuente.

## 2. Tokenizador de BM25 mejorado

El tokenizador original (`texto.lower().split()`) fue problemático porque:

- No eliminaba puntuación adherida: `"LangChain?"` quedaba como
  `"langchain?"`, que no coincidía con `"langchain"` en los documentos.
- No filtraba stopwords del español, por lo que términos muy frecuentes
  como `"qué"`, `"es"`, `"la"` podían dominar el ranking léxico.

El tokenizador ahora:

- Pasa a minúsculas.
- Elimina puntuación adherida.
- Filtra stopwords básicas del español.
- No usa stemming (se preservan términos técnicos como `"LangChain"`,
  `"LangGraph"`, `"LangSmith"`).

## 3. Búsqueda híbrida con `EnsembleRetriever`

Ambos scripts de consulta construyen un retriever híbrido combinando:

- Retriever léxico (BM25) → recupera por coincidencia exacta de palabras.
- Retriever denso (similitud de embeddings) → recupera por significado.

Se usa `EnsembleRetriever` (de `langchain-classic`) con fusión ponderada
RRF. Los pesos por defecto son 0.5/0.5, documentados como ajustables para
favorecer BM25 (términos exactos) o denso (paráfrasis/conceptos).

## 4. Filtro por `source` afecta ambos retrievers

En `consulta_filtrada.py`, cuando se pasa una fuente (ej. `datos.txt`):

- El retriever denso recibe `filter={"source": ...}` de Chroma.
- El retriever BM25 se construye únicamente con los documentos de esa
  fuente.

Esto evita que una pregunta sobre "LangChain" recupere fragmentos de la
Constitución.

## 5. Ajuste del retriever denso en `consulta.py`

Se mantiene MMR pero con parámetros más adecuados para una base chica
(~75 chunks):

```python
search_type="mmr",
search_kwargs={"k": 3, "fetch_k": 10, "lambda_mult": 0.7}
```

- `fetch_k` bajado de 20 a 10 (la colección es pequeña).
- `lambda_mult` subido de 0.5 a 0.7 (prioriza relevancia sobre
  diversidad).

## 6. Se limita la salida del ensemble a `K_RESULTADOS`

`EnsembleRetriever` puede devolver más documentos que `k` si los
rankings de BM25 y denso no se superponen. Por eso se recorta la salida
final a exactamente `K_RESULTADOS` (por defecto 3).

## 7. Dependencias actualizadas

Se agregaron a `requirements.txt`:

```text
langchain-classic
rank-bm25
```

Se evita importar directamente desde `langchain_community`
(paquete en sunset/deprecación). La implementación de BM25 usa
`rank_bm25.BM25Okapi` directamente a través de `retrievers.py`.

## 8. Resultado de las pruebas

Ejecutando en `Clase 26`:

```bash
python ingesta.py
python consulta.py '¿Qué es LangChain?'
python consulta_filtrada.py '¿Qué es LangChain?' datos.txt
```

Ambas consultas devolvieron resultados relevantes de `datos.txt`
(referentes a LangChain, LangGraph y LangSmith), en lugar de los
artículos de la Constitución que se obtenían con el modelo en inglés en
la Clase 25.
