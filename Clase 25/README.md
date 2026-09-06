# Proyecto de ingesta y consulta RAG (Clase 25)

Pipeline de ejemplo de RAG (Retrieval Augmented Generation): ingesta de `.txt`/`.pdf`
en una base vectorial Chroma (`ingesta.py`), y consulta por similitud/MMR
(`consulta.py`, `consulta_filtrada.py`). Ver `siguientes_pasos.md` para conectar un
LLM y armar el flujo completo de preguntas y respuestas.

## Instalación

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

## Uso

```bash
python ingesta.py
python consulta.py "¿Qué es LangChain?"
python consulta_filtrada.py "¿Qué es LangChain?" datos.txt
```

## Skill: `context7-dependencias`

Este repo incluye un skill en `.agents/skills/context7-dependencias/SKILL.md` que
usa el MCP server **Context7** para consultar documentación actualizada de
cualquier librería del proyecto (LangChain, ChromaDB, etc.) y detectar imports
deprecados antes de escribir código.

Para que el skill funcione necesitás tener el **MCP server de Context7** configurado
en tu propio editor (no viaja con el `git clone`, es una configuración de usuario).

### Instalación rápida (recomendada)

Requiere Node.js 18+:

```bash
npx ctx7 setup
```

Este comando detecta tu editor (Cursor, Claude Code, OpenCode, etc.), te autentica
por OAuth, genera una API key y configura el servidor automáticamente.

### Instalación manual

1. Conseguí una API key gratuita en [context7.com/dashboard](https://context7.com/dashboard)
   (opcional, pero da límites de uso más altos).
2. Agregá esta configuración en el archivo de MCP de tu editor:

   | Editor | Archivo de configuración |
   |---|---|
   | Windsurf / Devin Desktop | `~/.codeium/mcp_config.json` (o el equivalente que muestre tu IDE en la sección MCP) |
   | Cursor | `~/.cursor/mcp.json` (o `.cursor/mcp.json` en el proyecto) |
   | Claude Code | `claude mcp add ...` (ver comando abajo) |
   | Claude Desktop | `claude_desktop_config.json` |
   | VS Code | Extensión "Context7" desde el Marketplace |

   **Servidor remoto (recomendado, sin instalar nada localmente):**
   ```json
   {
     "mcpServers": {
       "context7": {
         "url": "https://mcp.context7.com/mcp",
         "headers": {
           "CONTEXT7_API_KEY": "TU_API_KEY"
         }
       }
     }
   }
   ```

   **Servidor local (requiere Node.js):**
   ```json
   {
     "mcpServers": {
       "context7": {
         "command": "npx",
         "args": ["-y", "@upstash/context7-mcp", "--api-key", "TU_API_KEY"]
       }
     }
   }
   ```

   **Claude Code (por línea de comandos):**
   ```bash
   claude mcp add --scope user --header "CONTEXT7_API_KEY: TU_API_KEY" --transport http context7 https://mcp.context7.com/mcp
   ```

3. Reiniciá el editor y verificá que las tools `resolve-library-id` y
   `get-library-docs` aparezcan disponibles (o que Context7 figure activo en la
   lista de servidores MCP).

Una vez configurado, el skill se activa automáticamente cuando la tarea coincide
con su `description`, o se puede invocar manualmente según el mecanismo de
`@mention` de cada editor.
