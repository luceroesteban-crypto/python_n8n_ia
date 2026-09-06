"""
Script de consulta con BÚSQUEDA HÍBRIDA (densa + léxica) sobre la base
vectorial Chroma generada por `ingesta.py`.

--------------------------------------------------------------------------
CAMBIOS respecto a la versión de "Clase 25" (documentados en `mejoras.md`)
--------------------------------------------------------------------------

1) Modelo de embeddings multilingüe
   -----------------------------------
   `EMBEDDING_MODEL` cambia de `sentence-transformers/all-MiniLM-L6-v2`
   (inglés) a `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
   (multilingüe). DEBE coincidir siempre con el modelo usado en `ingesta.py`,
   porque los vectores de la consulta y los de la base tienen que vivir en
   el mismo espacio semántico para que la similitud tenga sentido.

2) Búsqueda híbrida (densa + BM25) en vez de solo MMR
   -----------------------------------------------------
   La versión anterior usaba únicamente `max_marginal_relevance_search`
   (búsqueda "densa": basada en similitud de embeddings). Esto tiene una
   debilidad conocida: los embeddings capturan bien el significado general,
   pero pueden fallar con términos específicos (nombres propios, siglas,
   términos técnicos como "LangGraph" o "LangSmith") si esos términos no
   quedaron bien representados en el espacio vectorial.

   Para compensar eso, se agrega un segundo retriever **léxico** (BM25, el
   mismo algoritmo de ranking que usan buscadores como Elasticsearch), que
   no depende de embeddings sino de coincidencia de palabras/subcadenas.
   Ambos retrievers se combinan con `EnsembleRetriever`, que fusiona los
   rankings de cada uno usando "Reciprocal Rank Fusion" (RRF) ponderado.

   Por qué esto mejora la recuperación:
   - Si la pregunta usa un término exacto que aparece en un chunk (ej.
     "LangGraph"), BM25 lo va a encontrar aunque el embedding denso no lo
     priorice.
   - Si la pregunta es más conceptual/paráfrasis, la búsqueda densa sigue
     aportando esos resultados.
   - En la práctica, la búsqueda híbrida suele tener mejor recall que
     cualquiera de los dos métodos por separado, que es justamente el
     problema observado en las pruebas de la Clase 25 (resultados poco
     relacionados con la pregunta).

3) Ajuste de parámetros del retriever denso (dentro del híbrido)
   ----------------------------------------------------------------
   Se mantiene MMR para el componente denso, pero se sube `lambda_mult` de
   0.5 a 0.7 (prioriza más la relevancia que la diversidad) y se baja
   `fetch_k` de 20 a 10, ya que la base de este proyecto es chica (~75
   chunks): pedir 20 candidatos sobre una colección tan pequeña no aporta
   mucha diversidad real y sólo hace más lento el reordenamiento MMR.

4) Nuevo: se limita la salida a exactamente K_RESULTADOS
   --------------------------------------------------------
   `EnsembleRetriever` puede devolver hasta la suma de los `k` de cada
   retriever cuando hay poca superposición. Para mantener el comportamiento
   esperado (por defecto 3 resultados), se recorta la lista final a
   `K_RESULTADOS`.

Requiere los paquetes `rank-bm25` (usado internamente por `BM25RetrieverLocal`)
y `langchain-classic` (donde vive `EnsembleRetriever` desde LangChain v1). Ver
`requirements.txt`. La implementación de `BM25RetrieverLocal` fue extraída
al módulo `retrievers.py` para no sobrecargar este script.
"""

import sys
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_classic.retrievers import EnsembleRetriever

from retrievers import construir_bm25_desde_vectordb


# 1. Definir el modelo y el directorio de la DB (deben ser los mismos que en ingesta.py)
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
PERSIST_DIRECTORY = "db_chroma"

# Cantidad de resultados finales a mostrar
K_RESULTADOS = 3

# Pesos del ensemble: cuánto pesa cada retriever en el ranking final.
# 0.5/0.5 = mismo peso para BM25 (léxico) y para la búsqueda densa (MMR).
# Subir el peso de BM25 favorece coincidencias exactas de términos;
# subir el peso denso favorece similitud semántica/paráfrasis.
PESO_BM25 = 0.5
PESO_DENSO = 0.5


def construir_retriever_denso(vectordb, k=K_RESULTADOS):
    """Construye el retriever vectorial (denso) con MMR, con parámetros
    ajustados para una base chica (ver punto 3 del docstring del módulo).
    """
    return vectordb.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": 10, "lambda_mult": 0.7}
    )


def main(query_text):
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

    # 4. Construir los dos retrievers y combinarlos en un retriever híbrido.
    retriever_bm25 = construir_bm25_desde_vectordb(vectordb, k=K_RESULTADOS)
    retriever_denso = construir_retriever_denso(vectordb)

    retriever_hibrido = EnsembleRetriever(
        retrievers=[retriever_bm25, retriever_denso],
        weights=[PESO_BM25, PESO_DENSO]
    )

    print(f"Realizando búsqueda HÍBRIDA (BM25 + MMR) para: '{query_text}'\n")
    results = retriever_hibrido.invoke(query_text)

    # El ensemble puede devolver más de K_RESULTADOS si los rankings de
    # BM25 y denso no se superponen; se limita la salida final.
    results = results[:K_RESULTADOS]

    # --- Para comparar métodos durante la clase, se puede correr cada
    #     retriever por separado en vez del híbrido:
    # results = retriever_bm25.invoke(query_text)[:K_RESULTADOS]   # Solo léxico (BM25)
    # results = retriever_denso.invoke(query_text)[:K_RESULTADOS]    # Solo denso (MMR)

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
    if len(sys.argv) > 1:
        main(" ".join(sys.argv[1:]))
    else:
        print("Error: Debes pasar tu consulta como argumento.")
        print("Ejemplo: python consulta.py '¿Qué es LangChain?'")
