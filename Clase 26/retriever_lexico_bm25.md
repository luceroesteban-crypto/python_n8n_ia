# Retriever léxico: BM25

## ¿Qué es un retriever léxico?

Un **retriever léxico** busca documentos relevantes comparando las
**palabras** (o tokens) que aparecen en la consulta del usuario con las
palabras que aparecen en los documentos almacenados. A diferencia de un
**retriever denso** (vectorial), que convierte textos en vectores numéricos y
busca por similitud semántica, un retriever léxico no "entiende" el
significado: simplemente cuenta y pondera coincidencias de términos.

En el proyecto `Clase 26`, el retriever denso está dado por `Chroma` + el
modelo de embeddings `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`,
mientras que el retriever léxico está implementado en `retrievers.py` con el
algoritmo **BM25** usando la librería `rank_bm25`.

## ¿Qué es BM25?

**BM25** (Best Match 25) es un algoritmo de ranking desarrollado a partir de
los años 70-90, ampliamente usado en motores de búsqueda (por ejemplo,
Elasticsearch usa variantes de BM25). Dada una consulta y una colección de
documentos, BM25 asigna un score a cada documento según:

1. **Frecuencia del término (TF):** cuántas veces aparece cada palabra de la
   consulta en el documento.
2. **Frecuencia inversa de documento (IDF):** qué tan rara es cada palabra en
   toda la colección. Palabras que aparecen en pocos documentos (como
   "LangChain" o "LangGraph") reciben más peso que palabras que aparecen en
   casi todos los documentos (como "el", "la", "es").
3. **Longitud del documento:** documentos más cortos se benefician más por
   coincidencia de términos que documentos muy largos, porque una coincidencia
   en un texto corto es más significativa.

### Intuición del score

Para cada término `t` de la consulta y cada documento `d`:

```
score(d, t) ≈ IDF(t) * (frecuencia_de_t_en_d * (k + 1))
              -----------------------------------------------
              frecuencia_de_t_en_d + k * (1 - b + b * (longitud_d / longitud_promedio))
```

- `k` y `b` son hiperparámetros del algoritmo. En `BM25Okapi` de `rank_bm25`
  los valores por defecto suelen ser `k1=1.5` y `b=0.75`.
- El **IDF** penaliza términos comunes y premia términos raros.
- El denominador evita que documentos muy largos monopolicen el ranking solo
  por repetir muchas veces una palabra.

El score final del documento es la suma de los scores de cada término de la
consulta.

## Diferencias clave: retriever denso vs. retriever léxico

| Característica | Retriever denso (embeddings) | Retriever léxico (BM25) |
|---|---|---|
| **Qué representa** | Significado/semántica del texto. | Coincidencia exacta de palabras/tokens. |
| **Ventaja principal** | Funciona bien con paráfrasis, sinónimos y conceptos generales. | Excelente con nombres propios, siglas, términos técnicos exactos. |
| **Debilidad principal** | Puede fallar con términos poco frecuentes o muy específicos. | No entiende sinónimos ni reformulaciones. |
| **Relevancia de términos** | Depende de cómo el modelo de embeddings haya aprendido a representarlos. | Depende directamente de la frecuencia de los términos en la colección. |
| **Idioma** | Depende de la calidad del modelo multilingüe usado. | Funciona con cualquier idioma, siempre que la tokenización sea adecuada. |
| **Costo computacional** | Requiere calcular/embeddings y comparar vectores. | Generalmente más rápido y liviano en colecciones pequeñas/medias. |

## ¿Por qué usar BM25 en un pipeline RAG?

En un sistema de Retrieval Augmented Generation (RAG), el objetivo es
recuperar los documentos más relevantes para construir un contexto que se
le pase a un LLM. Ni el retriever denso ni el léxico son perfectos en
solitario:

- El retriever **denso** puede fallar cuando el usuario pregunta usando un
  término exacto que no quedó bien representado en el espacio vectorial, o
  cuando los embeddings no capturan bien palabras técnicas/raras.
- El retriever **léxico** puede fallar cuando el usuario usa sinónimos,
  reformulaciones o preguntas conceptuales que no contienen exactamente las
  mismas palabras que los documentos.

Por eso se combinan ambos en una **búsqueda híbrida**: cada uno compensa las
limitaciones del otro.

### Ejemplo concreto de este proyecto

En la Clase 25, con el modelo `all-MiniLM-L6-v2` (entrenado principalmente en
inglés) y búsqueda densa pura, la pregunta:

```text
¿Qué es LangChain?
```

devolvía artículos de la Constitución Argentina. Con el modelo
multilingüe y BM25 en paralelo, el retriever léxico prioriza los chunks de
`datos.txt` que contienen literalmente la palabra "LangChain", mientras que
el retriever denso prioriza los chunks con significado similar. El resultado
híbrido mejora la probabilidad de recuperar el contenido correcto.

## Implementación en `retrievers.py`

El retriever léxico del proyecto se construye en tres pasos:

### 1. Obtener los documentos de Chroma

En lugar de releer `datos.txt` y `documento.pdf`, se obtienen los chunks
exactos que ya fueron persistidos en la base vectorial:

```python
coleccion = vectordb.get(include=["documents", "metadatas"])
documentos = [
    Document(page_content=texto, metadata=metadata)
    for texto, metadata in zip(coleccion["documents"], coleccion["metadatas"])
]
```

Esto garantiza que el índice léxico y el índice denso indexen exactamente
los mismos fragmentos, con los mismos metadatos.

### 2. Tokenizar los documentos

BM25 no trabaja con texto "crudo", sino con listas de tokens. La función
`_tokenizar_basico` del proyecto realiza:

- **Minúsculas:** para que "LangChain" y "langchain" sean el mismo token.
- **Eliminación de puntuación adherida:** para que `"LangChain?"` se
  convierta en `"langchain"`. Esto es importante porque `str.split()` deja
  los signos de puntuación pegados a las palabras.
- **Eliminación de stopwords:** palabras muy frecuentes en español como
  `"qué"`, `"es"`, `"la"`, `"de"` tienen muy poco poder discriminativo y
  pueden distorsionar el ranking si no se filtran.

### 3. Construir y consultar el índice BM25

Con `rank_bm25.BM25Okapi` se construye el índice a partir del corpus
tokenizado:

```python
from rank_bm25 import BM25Okapi

vectorizador = BM25Okapi(corpus_tokenizado)
resultados = vectorizador.get_top_n(query_tokenizada, documentos, n=k)
```

`get_top_n` devuelve los `k` documentos con mayor score BM25 para la consulta.

## Híbrido: cómo se combina con el retriever denso

En `consulta.py` y `consulta_filtrada.py` se usan ambos retrievers dentro de
un `EnsembleRetriever`:

```python
retriever_hibrido = EnsembleRetriever(
    retrievers=[retriever_bm25, retriever_denso],
    weights=[0.5, 0.5]
)
```

`EnsembleRetriever` aplica **Reciprocal Rank Fusion (RRF)** ponderada:

- Cada retriever devuelve su propio ranking de documentos.
- Para cada documento, se calcula un score combinado basado en su posición
  en cada ranking (más alto en el ranking = mejor).
- Los pesos permiten darle más importancia a uno u otro retriever según el
  tipo de consulta esperada.

Por ejemplo:

- Si se esperan muchas consultas con términos técnicos exactos, conviene dar
  más peso al BM25 (ej. `weights=[0.7, 0.3]`).
- Si se esperan consultas conceptuales o en lenguaje natural variado,
  conviene dar más peso al denso (ej. `weights=[0.3, 0.7]`).

## Cuándo BM25 ayuda y cuándo no

### Casos donde BM25 suele ayudar

- Búsquedas por **nombres propios**, **siglas**, **códigos** o **términos
  técnicos específicos** que aparecen literalmente en los documentos.
- Colecciones pequeñas/medias donde un término raro puede discriminar muy
  bien.
- Combinación con embeddings para mejorar el **recall** (recuperar más
  documentos potencialmente relevantes).

### Casos donde BM25 puede fallar

- Consultas que usan **sinónimos** o **paráfrasis** sin repetir las mismas
  palabras del documento.
- Consultas conceptuales como "¿cuáles son los derechos fundamentales?" si
  los documentos no contienen exactamente esas palabras.
- Si la tokenización es pobre (por ejemplo, sin manejar puntuación o
  stopwords), el ranking se degrada.

## Consideraciones prácticas de tokenización

BM25 es sensible a cómo se separa el texto en tokens. Decisiones tomadas en
este proyecto:

| Decisión | Justificación |
|---|---|
| Minúsculas | Evita que "LangChain" y "langchain" sean tokens distintos. |
| Quitar puntuación adherida | Evita que `"langchain?"` (consulta) no coincida con `"langchain"` (documento). |
| Stopwords básicas del español | Evita que `"qué"`, `"es"`, `"la"` dominen el ranking sobre términos técnicos. |
| Sin stemming | Preserva términos técnicos exactos como "LangChain" / "LangGraph"; el stemming podría deformarlos. |

## Resumen

BM25 es un retriever léxico clásico, rápido y efectivo para recuperar
documentos por coincidencia de términos. En este proyecto se usa junto con
un retriever denso (embeddings + Chroma) para formar una **búsqueda
híbrida**: la componente léxica asegura que términos técnicos o nombres
propios específicos se encuentren, mientras que la componente densa captura
similitud semántica y paráfrasis. Ambos se combinan con `EnsembleRetriever`
mediante RRF ponderada, y su implementación vive en el módulo
`retrievers.py` para mantener `consulta.py` y `consulta_filtrada.py` limpios.
