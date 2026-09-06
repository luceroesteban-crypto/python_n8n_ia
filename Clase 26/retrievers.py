"""
Módulo auxiliar con retrievers personalizados para el pipeline RAG.

La idea de separar esto en un archivo propio es evitar cargar `consulta.py` y
`consulta_filtrada.py` con la implementación detallada de BM25, y facilitar
su reutilización/mantenimiento.

Contenido actual:
- `BM25RetrieverLocal`: retriever léxico basado en `rank_bm25.BM25Okapi`,
  compatible con `EnsembleRetriever` de LangChain heredando de
  `BaseRetriever`.
- `_tokenizar_basico`: tokenizador para BM25 con eliminación de puntuación
  adherida y stopwords básicas del español.
"""

from typing import Any, List

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict
from rank_bm25 import BM25Okapi


# Stopwords básicas del español para BM25. El objetivo es evitar que
# términos muy frecuentes como "qué", "es", "la", "de" dominen el ranking
# léxico sobre términos más discriminativos ("LangChain", "Constitución",
# "artículo", etc.).
_STOPWORDS_ES = {
    "a", "al", "algo", "algunas", "algunos", "ante", "antes", "como",
    "con", "contra", "cual", "cuando", "de", "del", "desde", "donde",
    "durante", "e", "el", "ella", "ellas", "ellos", "en", "entre",
    "era", "erais", "eran", "eras", "eres", "es", "esa", "esas",
    "ese", "eso", "esos", "esta", "estas", "este", "esto", "estos",
    "estoy", "fue", "fueron", "ha", "han", "has", "hasta", "hay",
    "he", "hemos", "hubo", "la", "las", "le", "les", "lo", "los",
    "me", "mi", "mis", "muy", "más", "nada", "ni", "nos", "nosotras",
    "nosotros", "nuestra", "nuestras", "nuestro", "nuestros", "o",
    "os", "otra", "otras", "otro", "otros", "para", "pero", "poco",
    "por", "porque", "que", "qué", "quien", "quienes", "se", "sea",
    "son", "soy", "su", "sus", "suya", "suyas", "suyo", "suyos",
    "también", "tanto", "te", "ti", "tu", "tus", "tú", "un", "una",
    "uno", "unos", "vosotras", "vosotros", "vuestra", "vuestras",
    "vuestro", "vuestros", "y", "ya", "yo", "él", "ésa", "ésas",
    "ése", "ésos", "ésta", "éstas", "éste", "éstos", "última",
    "últimas", "último", "últimos",
}

_PUNTUACION = ".,;:!?¿¡()[]{}\"\"`'"


def _tokenizar_basico(texto: str) -> List[str]:
    """Tokenización para BM25.

    - Pasa a minúsculas.
    - Elimina puntuación adherida (ej. "LangChain?" -> "langchain"), porque
      `str.split()` no separa los signos de puntuación y `BM25Okapi` no
      hace ese paso por defecto.
    - Filtra stopwords básicas del español para que términos muy frecuentes
      como "qué", "es", "la" no dominen el ranking sobre términos más
      discriminativos ("LangChain", "Constitución", etc.).

    No se usa stemming a propósito: con vocabulario técnico como "LangChain",
    "LangGraph", "LangSmith", es mejor mantener las palabras originales.
    """
    tokens = texto.lower().split()
    return [
        token.strip(_PUNTUACION)
        for token in tokens
        if token.strip(_PUNTUACION) and token.strip(_PUNTUACION) not in _STOPWORDS_ES
    ]


class BM25RetrieverLocal(BaseRetriever):
    """Retriever léxico (BM25) implementado directamente con `rank_bm25`.

    Evita importar desde `langchain_community`, que está en proceso de
    "sunset" y genera advertencias de deprecación. Hereda de
    `BaseRetriever` para poder usarse dentro de `EnsembleRetriever`.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    documentos: List[Document]
    k: int = 4
    vectorizador: Any = None

    def __init__(self, documentos: List[Document], k: int = 4):
        super().__init__(documentos=documentos, k=k, vectorizador=None)
        corpus_tokenizado = [_tokenizar_basico(doc.page_content) for doc in documentos]
        self.vectorizador = BM25Okapi(corpus_tokenizado)

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun | None = None
    ) -> List[Document]:
        query_tokenizada = _tokenizar_basico(query)
        if not query_tokenizada:
            return []
        return self.vectorizador.get_top_n(
            query_tokenizada, self.documentos, n=self.k
        )


def construir_bm25_desde_vectordb(vectordb, source_filter: str | None = None, k: int = 4):
    """Construye un `BM25RetrieverLocal` a partir de los documentos ya
    persistidos en Chroma.

    Obtener los documentos desde Chroma (en vez de releer `datos.txt` o el
    PDF) garantiza que BM25 indexa exactamente los mismos chunks (mismo
    texto, mismos metadatos) que el índice vectorial, evitando duplicar
    lógica de carga y manteniendo sincronizados ambos retrievers.
    """
    coleccion = vectordb.get(include=["documents", "metadatas"])
    documentos = [
        Document(page_content=texto, metadata=metadata)
        for texto, metadata in zip(coleccion["documents"], coleccion["metadatas"])
    ]
    if source_filter:
        documentos = [
            doc for doc in documentos if doc.metadata.get("source") == source_filter
        ]
    if not documentos:
        return None
    return BM25RetrieverLocal(documentos, k=k)
