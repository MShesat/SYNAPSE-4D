# Synapse 4D - Especificación de la API MCP (Model Context Protocol v2.5)

El servidor MCP nativo de **Synapse 4D** permite a interfaces de IA agénticas como **Cursor**, **Claude Desktop**, **VS Code** y **Antigravity** interactuar directamente con la memoria multi-dimensional del usuario mediante llamadas a herramientas estandarizadas.

---

## 1. Configuración de Clientes MCP

### Configuración para Claude Desktop

Edita el archivo de configuración de Claude Desktop:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "synapse4d": {
      "command": "python",
      "args": [
        "-m",
        "synapse4d.cli",
        "mcp",
        "--vault",
        "C:\\Users\\ANGEL RUIZ\\Desktop\\os ai"
      ]
    }
  }
}
```

> **Nota:** Reemplaza la ruta de `--vault` por la ruta absoluta a tu bóveda de Obsidian. En Windows, asegúrate de escapar las barras invertidas (`\\`).

---

### Configuración para Cursor

En la raíz de tu proyecto o bóveda, crea o edita `.cursor/mcp.json` (o configúralo desde *Cursor Settings > Features > MCP*):

```json
{
  "mcpServers": {
    "synapse4d": {
      "command": "python",
      "args": [
        "-m",
        "synapse4d.cli",
        "mcp",
        "--vault",
        "${workspaceFolder}"
      ]
    }
  }
}
```

---

## 2. Catálogo de Herramientas MCP

El servidor expone **6 herramientas fundamentales** para el ciclo cognitivo:

---

### 1. `synapse_get_working_memory`

Recupera el contexto activo de atención inmediata ($D_1$ Focus), el perfil del sistema/usuario y el proyecto en curso.

- **Parámetros:** Ninguno (`{}`).
- **Ejemplo de Request (JSON-RPC 2.0):**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "synapse_get_working_memory",
    "arguments": {}
  }
}
```

- **Ejemplo de Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "# Active Context\nProyecto activo: Migración Synapse 4D v2.0.\nFoco actual: Calibración empírica y soporte MCP.\n\n# System Profile\nUsuario: Ángel Ruiz\nHardware: Windows x64, SQLite WAL, ONNX local embeddings."
      }
    ]
  }
}
```

---

### 2. `synapse_search_memory`

Ejecuta una búsqueda semántica y relacional híbrida en SQLite WAL combinando concordancia léxica con similitud de embeddings ONNX.

- **Parámetros:**
  - `query` (*string*, requerido): Concepto, término o pregunta a buscar.

- **Ejemplo de Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "synapse_search_memory",
    "arguments": {
      "query": "PostgreSQL persistencia"
    }
  }
}
```

- **Ejemplo de Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[\n  {\n    \"id\": \"f_8a7d3c12\",\n    \"entity\": \"PostgreSQL\",\n    \"attribute\": \"persistencia\",\n    \"value\": \"usar PostgreSQL para persistencia de datos relacionales\",\n    \"status\": \"active\",\n    \"confidence\": 1.0,\n    \"session_id\": \"sess_20261028_1530\",\n    \"valid_from\": \"2026-10-28T15:30:00Z\",\n    \"needs_review\": 0\n  }\n]"
      }
    ]
  }
}
```

---

### 3. `synapse_consolidate`

Dispara de forma autónoma el ciclo de consolidación 4D. Absorbe las bitácoras episódicas (`10_Episodic_Memory`), extrae hechos atómicos, arbitra contradicciones lógicas mediante supersesión bi-temporal, actualiza el grafo Hebbiano relacional y genera stubs recíprocos.

- **Parámetros:** Ninguno (`{}`).
- **Ejemplo de Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "synapse_consolidate",
    "arguments": {}
  }
}
```

- **Ejemplo de Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"status\": \"success\",\n  \"session_id\": \"sess_20261028_153022\",\n  \"facts_extracted\": 14,\n  \"facts_superseded\": 2,\n  \"edges_updated\": 28,\n  \"stubs_created\": 1,\n  \"health_score\": 0.98,\n  \"duration_ms\": 842.5\n}"
      }
    ]
  }
}
```

---

### 4. `synapse_audit` (alias: `synapse_audit_vault`)

Inspecciona la integridad estructural de la bóveda: puntuación de salud epistémica (*health score*), wikilinks rotos, hechos provisionales pendientes de revisión (`needs_review`) y estado de los ficheros SQLite WAL.

- **Parámetros:** Ninguno (`{}`).
- **Ejemplo de Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "synapse_audit_vault",
    "arguments": {}
  }
}
```

- **Ejemplo de Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"health_score\": 0.96,\n  \"total_active_facts\": 1420,\n  \"needs_review_count\": 3,\n  \"broken_wikilinks_count\": 0,\n  \"wal_frames\": 24,\n  \"journal_reconciliation_status\": \"clean\"\n}"
      }
    ]
  }
}
```

---

### 5. `synapse_undo` (alias: `synapse_undo_session`)

Revierte de forma determinista y atómica todos los efectos de una sesión previa de consolidación (hechos insertados, supersesiones aplicadas y referencias asociativas), restaurando el estado exacto anterior.

- **Parámetros:**
  - `session_id` (*string*, requerido): Identificador de la sesión a revertir (obtenido del histórico de consolidación o auditoría).

- **Ejemplo de Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "synapse_undo_session",
    "arguments": {
      "session_id": "sess_20261028_153022"
    }
  }
}
```

- **Ejemplo de Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"status\": \"rolled_back\",\n  \"session_id\": \"sess_20261028_153022\",\n  \"facts_restored\": 2,\n  \"facts_invalidated\": 14,\n  \"restoration_timestamp\": \"2026-10-28T15:35:10Z\"\n}"
      }
    ]
  }
}
```

---

### 6. `synapse_review` (alias: `synapse_review_facts`)

Lista todas las afirmaciones y hechos provisionales que fueron extraídos heurísticamente o que presentan ambigüedad semántica y se encuentran marcados con `needs_review = 1`.

- **Parámetros:** Ninguno (`{}`).
- **Ejemplo de Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "synapse_review_facts",
    "arguments": {}
  }
}
```

- **Ejemplo de Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[\n  {\n    \"id\": \"f_c0192e8a\",\n    \"entity\": \"Cache\",\n    \"attribute\": \"politica_desalojo\",\n    \"value\": \"posible uso de algoritmo LFU en lugar de LRU\",\n    \"confidence\": 0.65,\n    \"needs_review\": 1,\n    \"session_id\": \"sess_20261028_121500\"\n  }\n]"
      }
    ]
  }
}
```
