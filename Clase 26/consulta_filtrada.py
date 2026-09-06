"""
Script de consulta con BÚSQUEDA HÍBRIDA (densa + léxica) y filtro opcional
por fuente, sobre la base vectorial Chroma generada por `ingesta.py`.

--------------------------------------------------------------------------
CAMBIOS respecto a la versión de "Clase 25" (documentados en `mejoras.md`)
--------------------------------------------------------------------------

1) Modelo de embeddings multilingüe
   -----------------------------------
   Igual que en `consulta.py`: `EMBEDDING_MODEL` pasa de
   `sentence-transformers/all-MiniLM-L6-v2` (inglés) a
   `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
   (multilingüe), para que el idioma de los documentos (español) esté bien
   representado en el espacio de embeddings. Debe coincidir siempre con el
   modelo usado en `ingesta.py`.

2) Búsqueda híbrida (BM25 + densa) en vez de `similarity_search` simple
   -------------------------------------------------------------------------
   La versión anterior usaba `similarity_search` (solo densa, sin
   diversidad ni componente léxico). Se reemplaza por un `EnsembleRetriever`
   que combina:
   - Un `BM25RetrieverLocal` (búsqueda léxica por coincidencia de palabras).
   - Un retriever vectorial con `similarity_search` denso (se usa
     similitud simple aquí, no MMR, ya que junto con el filtro por fuente
     el conjunto de candidatos suele ser chico y no hace falta forzar
     diversidad adicional).

   Ver la justificación completa de por qué usar búsqueda híbrida en el
   docstring de `consulta.py` (aplica igual acá).

3) El filtro por fuente aplica a AMBOS retrievers, no solo al denso
   -----------------------------------------------------------------
   En la versión anterior, el filtro por `source` sólo tenía sentido con
   `similarity_search` (que soporta `filter=...` nativamente en Chroma).
   Acá, cuando se pasa `source_filter`:
   - Al retriever denso se le pasa `filter={"source": source_filter}` en
     `search_kwargs` (Chroma filtra a nivel de metadata antes de calcular
     similitud).
   - Al retriever BM25 se le pasa sólo el subconjunto de documentos de esa
     fuente (BM25 no tiene un mecanismo de filtro por metadata propio, así
     que el filtrado se hace antes de construir el índice léxico).

   Así, con filtro, ambos retrievers buscan exclusivamente dentro de los
   chunks de la fuente indicada, y sin filtro buscan en toda la colección.

La implementación del retriever BM25 fue extraída al módulo `retrievers.py`
para no sobrecargar este script. Requiere los paquetes `rank-bm25` y
`langchain-classic` (ver `requirements.txt`).
"""

import sys
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_classic.retrievers import EnsembleRetriever

from retrievers import construir_bm25_desde_vectordb


# 1. Definir el modelo y el directorio de la DB (deben ser los mismos que en ingesta.py)
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
PERSIST_DIRECTORY = "db_chroma"

K_RESULTADOS = 3
PESO_BM25 = 0.5
PESO_DENSO = 0.5


def construir_retriever_denso(vectordb, source_filter=None, k=K_RESULTADOS):
    search_kwargs = {"k": k}
    if source_filter:
        search_kwargs["filter"] = {"source": source_filter}
    return vectordb.as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs
    )


def main(query_text, source_filter=None):
    if not query_text:
        print("Por favor, proporciona un texto para la consulta.")
        return

    print("Cargando modelo de embeddings y base de datos...")

    # 2. Cargar el modelo de Embeddings (debe ser el mismo que en ingesta.py)
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'}
    )

    # 3. Cargar la base de datos vectorial persistente
    vectordb = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings
    )

    print(f"Realizando búsqueda HÍBRIDA (BM25 + similitud) para: '{query_text}'")
    if source_filter:
        print(f"Filtrando por fuente: {source_filter}\n")
    else:
        print()

    # 4. Construir retrievers (con filtro por fuente, si corresponde) y
    #    combinarlos en un retriever híbrido.
    retriever_denso = construir_retriever_denso(vectordb, source_filter)
    retriever_bm25 = construir_bm25_desde_vectordb(vectordb, source_filter, k=K_RESULTADOS)

    if retriever_bm25 is None:
        # No hay documentos para esa fuente: no tiene sentido armar el
        # ensemble, directamente no habrá resultados.
        results = []
    else:
        retriever_hibrido = EnsembleRetriever(
            retrievers=[retriever_bm25, retriever_denso],
            weights=[PESO_BM25, PESO_DENSO]
        )
        results = retriever_hibrido.invoke(query_text)[:K_RESULTADOS]

    if not results:
        print("No se encontraron resultados relevantes.")
        return

    # 5. Mostrar los resultados
    print("Resultados encontrados:\n" + "="*30)
    for i, doc in enumerate(results):
        print(f"Resultado {i+1}:")
        print(f"Fuente: {doc.metadata.get('source', 'N/A')}")
        print(f"Página: {doc.metadata.get('page', 'N/A')}") # Útil para PDFs
        print("Contenido:")
        print(doc.page_content)
        print("-" * 30)

if __name__ == "__main__":
    # La consulta se pasa como argumento en la terminal
    # Uso: python consulta_filtrada.py "¿Qué es LangChain?" datos.txt
    if len(sys.argv) > 1:
        query = sys.argv[1]
        source = sys.argv[2] if len(sys.argv) > 2 else None
        main(query, source)
    else:
        print("Error: Debes pasar tu consulta como argumento.")
        print("Ejemplo: python consulta_filtrada.py '¿Qué es LangChain?'")
        print("O con filtro: python consulta_filtrada.py '¿Qué es LangChain?' datos.txt")
