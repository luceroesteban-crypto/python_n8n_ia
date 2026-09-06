---
name: context7-dependencias
description: Consultar documentación actualizada de cualquier librería usada en el proyecto usando context7
---

Este workflow define cómo obtener contexto actualizado sobre **cualquier librería o
dependencia usada en este proyecto** (no solo LangChain), apoyándose en el servidor
MCP `devin/context7`. Aplica a todo lo listado en `requirements.txt` y a cualquier
otra librería que se agregue en el futuro (por ejemplo: `chromadb`,
`sentence-transformers`, `pypdf`, `fastapi`, `numpy`, etc.).

1. Antes de escribir o modificar código que use una librería externa (esté o no en
   `requirements.txt` todavía), identificar el nombre exacto del paquete que se va a
   consultar.

2. Resolver el identificador de esa librería con la tool `resolve-library-id` de
   `devin/context7`, usando el nombre del paquete tal como se importa o se instala
   (ej: `langchain`, `langchain-community`, `pypdf`, `sentence-transformers`,
   `chromadb`, `fastapi`, `requests`, etc.). No asumir que solo aplica a LangChain.

3. Con el ID resuelto, llamar a `get-library-docs` (modo `code` para APIs/ejemplos,
   modo `info` para guías conceptuales, arquitectura o migración) indicando un
   `topic` específico relacionado con el cambio que se va a hacer (ej: `deprecation
   migration`, `persistence`, `authentication`, `async support`, según corresponda).

4. Usar la documentación devuelta para verificar, para la librería que corresponda:
   - Si una clase, función o import está deprecado.
   - Cuál es la alternativa o paquete recomendado, si existe.
   - Firmas y parámetros actualizados antes de editar el código del proyecto
     (`ingesta.py`, `consulta.py`, `consulta_filtrada.py`, `siguiente.py`, o
     cualquier archivo nuevo).

5. Si `context7` no ofrece un reemplazo o paquete standalone para una integración
   dada, documentar esa conclusión brevemente y mantener la implementación actual
   en lugar de inventar una alternativa inexistente.

6. Repetir este proceso cada vez que se actualice `requirements.txt`, se agregue una
   nueva librería al proyecto, o se detecten nuevos `DeprecationWarning` en la
   consola — sin importar de qué librería provengan.
