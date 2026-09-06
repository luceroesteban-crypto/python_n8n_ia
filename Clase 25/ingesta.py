"""
Script de ingesta para un pipeline RAG (Retrieval Augmented Generation).

Flujo:
1. Cargar documentos fuente (.txt y .pdf).
2. Dividirlos en chunks (fragmentos) manejables.
3. Generar embeddings de cada chunk con un modelo de HuggingFace.
4. Persistir los vectores en una base de datos Chroma en disco.

Nota sobre dependencias:
No se usa `langchain_community` (paquete en proceso de "sunset"/sin mantenimiento
activo). En su lugar:
- El .txt se carga con una función propia (`cargar_txt`), ya que `TextLoader`
  no tiene reemplazo standalone y es trivial de implementar.
- El .pdf se carga con `PyMuPDF4LLMLoader` del paquete `langchain-pymupdf4llm`,
  alternativa standalone y mantenida a `PyPDFLoader`.
"""

import os
from langchain_core.documents import Document
from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# 1. Definir los nombres de los archivos y el modelo de embeddings
TXT_SOURCE = "datos.txt"
PDF_SOURCE = "documento.pdf"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
PERSIST_DIRECTORY = "db_chroma" # Directorio donde se guardará la DB

def cargar_txt(ruta, encoding='utf-8'):
    """Carga un archivo de texto plano como un único Document de LangChain.

    Reemplaza a `langchain_community.document_loaders.TextLoader` (sin
    reemplazo standalone disponible) con una implementación mínima:
    lee el archivo completo y lo envuelve en un `Document`, guardando la
    ruta de origen en `metadata["source"]` para poder filtrar/citar después.

    Args:
        ruta: Ruta al archivo .txt a cargar.
        encoding: Codificación del archivo (por defecto 'utf-8', necesario
            para archivos con tildes/ñ).

    Returns:
        Lista con un único `Document` que contiene todo el contenido del
        archivo.
    """
    with open(ruta, encoding=encoding) as f:
        contenido = f.read()
    return [Document(page_content=contenido, metadata={"source": ruta})]


def main():
    """Ejecuta el pipeline completo de ingesta: carga, chunking, embeddings y persistencia."""
    print("Iniciando proceso de ingesta...")
    
    # 2. Cargar documentos
    # Cargamos el .txt (con cargar_txt) y el .pdf (con PyMuPDF4LLMLoader).
    # mode="page" genera un Document por página del PDF (igual que el
    # comportamiento por defecto de PyPDFLoader), útil para citar la página
    # exacta en los metadatos al hacer búsquedas después.
    # IMPORTANTE: Especificar encoding='utf-8' para archivos con tildes/ñ
    loader_pdf = PyMuPDF4LLMLoader(PDF_SOURCE, mode="page")

    documents = cargar_txt(TXT_SOURCE, encoding='utf-8')
    documents.extend(loader_pdf.load())

    if not documents:
        print("No se encontraron documentos para procesar.")
        return

    print(f"Total de documentos cargados: {len(documents)}")

    # 3. Dividir los documentos (Chunking)
    # ¿Por qué dividimos? Para que quepan en el contexto del modelo y 
    # para encontrar fragmentos más relevantes y específicos.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=250)
    splits = text_splitter.split_documents(documents)
    
    print(f"Total de chunks (fragmentos) creados: {len(splits)}")

    # 4. Inicializar el modelo de Embeddings
    # Usamos un modelo open-source de HuggingFace.
    # La primera vez, tardará un poco en descargarlo.
    print("Cargando modelo de embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'} # Usar CPU. Si tienen GPU, pueden cambiarlo.
    )

    # 5. Crear y persistir la Base de Datos Vectorial
    # Aquí ocurre la magia: LangChain toma los chunks, 
    # usa el modelo de embeddings para convertirlos en vectores
    # y los guarda en ChromaDB en el directorio especificado.
    print("Creando y guardando la base de datos vectorial...")
    vectordb = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )

    print(f"¡Base de datos creada y guardada en '{PERSIST_DIRECTORY}'!")
    print(f"Total de segmentos (chunks) procesados: {len(splits)}")

if __name__ == "__main__":
    main()