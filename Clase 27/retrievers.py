"""
retrievers.py - Retrievers personalizados para el sistema RAG
===========================================================

Este módulo contiene retrievers auxiliares que no dependen de
`langchain_community` (paquete en sunset). En particular, implementa
un retriever léxico basado en BM25 usando directamente la librería
`rank_bm25`, compatible con `EnsembleRetriever` de `langchain-classic`.

Autor: Clase 24 - IA Python para Principiantes
Fecha: 2025
"""

from typing import Any, List

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict
from rank_bm25 import BM25Okapi


# Stopwords básicas del español para BM25. El objetivo es evitar que
# términos muy frecuentes como "qué", "es", "la", "de" dominen el ranking
# léxico sobre términos más discriminativos (nombres propios, términos
# técnicos, etc.).
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

_PUNTUACION = ".,;:!?¿¡()[]{}\"\"`''"


def _tokenizar_basico(texto: str) -> List[str]:
    """
    Tokenización básica para BM25.

    - Pasa a minúsculas.
    - Elimina puntuación adherida (ej. "LangChain?" -> "langchain").
    - Filtra stopwords básicas del español.

    No se usa stemming para preservar términos técnicos exactos.
    """
    tokens = texto.lower().split()
    return [
        token.strip(_PUNTUACION)
        for token in tokens
        if token.strip(_PUNTUACION) and token.strip(_PUNTUACION) not in _STOPWORDS_ES
    ]


class BM25RetrieverLocal(BaseRetriever):
    """
    Retriever léxico (BM25) implementado directamente con `rank_bm25`.

    Hereda de `BaseRetriever` para poder usarse dentro de `EnsembleRetriever`
    de `langchain-classic`, sin depender de `langchain_community`.
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


def construir_bm25_desde_vectordb(vectordb, k: int = 4):
    """
    Construye un `BM25RetrieverLocal` a partir de los documentos ya
    persistidos en Chroma.

    Obtener los documentos desde Chroma garantiza que BM25 indexa exactamente
    los mismos chunks (mismo texto, mismos metadatos) que el índice vectorial.
    """
    coleccion = vectordb.get(include=["documents", "metadatas"])
    documentos = [
        Document(page_content=texto, metadata=metadata)
        for texto, metadata in zip(coleccion["documents"], coleccion["metadatas"])
    ]
    if not documentos:
        return None
    return BM25RetrieverLocal(documentos, k=k)
