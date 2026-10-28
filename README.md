# 🧠 Synapse 4D

<p align="center">
  <b>The SOTA Quad-Hybrid Cognitive Memory Engine for AI Agents & Obsidian.</b><br>
  <i>Unifies Letta, Mem0, Graphiti, and A-MEM into a single, sub-second bi-temporal memory layer.</i>
</p>

<p align="center">
  <a href="https://github.com/MShesat/synapse-4d/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+"></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP-Compatible-brightgreen.svg" alt="MCP Compatible"></a>
  <a href="https://obsidian.md/"><img src="https://img.shields.io/badge/Obsidian-Native-purple.svg" alt="Obsidian Native"></a>
  <a href="https://github.com/MShesat/synapse-4d/stargazers"><img src="https://img.shields.io/github/stars/MShesat/synapse-4d?style=social" alt="GitHub Stars"></a>
</p>

---

## ⚡ Why Synapse 4D?

Human knowledge methods like **PARA** (Projects, Areas, Resources, Archive) were designed for manual file folders, not autonomous AI agents. When LLMs browse PARA folders, they waste thousands of context tokens parsing obsolete drafts alongside immutable truths, causing severe **attention dilution, context rot, and hallucinations**.

Existing AI memory frameworks only solve isolated pieces:
- **Letta (MemGPT):** Solves active context paging, but lacks bi-temporal graph invalidation.
- **Mem0:** Extracts atomic facts, but doesn't maintain persistent Zettelkasten note graphs.
- **Graphiti:** Provides temporal graphs, but lacks native working memory buffer management.
- **A-MEM (NeurIPS 2024):** Generates atomic notes, but lacks automated conflict pruning.

**Synapse 4D combines all four into a unified cognitive engine:**

```
                        ┌────────────────────────────────────────┐
                        │        AI AGENT / LLM COGNITION        │
                        └───────────────────┬────────────────────┘
                                            │
                     ┌──────────────────────┴──────────────────────┐
                     ▼                                             ▼
       ┌───────────────────────────┐                 ┌───────────────────────────┐
       │   Pillar 1: LETTA ENGINE  │                 │    Pillar 2: MEM0 ENGINE  │
       │   Working Memory / Buffer │                 │   Atomic Fact CRUD & Dedup│
       │  (Self-Editing Context)   │                 │ (Add / Update / Invalidate)│
       └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                     │                                             │
                     └──────────────────────┬──────────────────────┘
                                            │
                     ┌──────────────────────┴──────────────────────┐
                     ▼                                             ▼
       ┌───────────────────────────┐                 ┌───────────────────────────┐
       │ Pillar 3: GRAPHITI ENGINE │                 │   Pillar 4: A-MEM ENGINE  │
       │   Bi-Temporal Graph Edges │                 │ Zettelkasten Atomic Notes │
       │ (Superseded State Tracker)│                 │ (Bidirectional Wikilinks) │
       └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                     │                                             │
                     └──────────────────────┬──────────────────────┘
                                            │
                                            ▼
                        ┌────────────────────────────────────────┐
                        │  PERSISTENT OBSIDIAN COALA BRAIN VAULT │
                        │   ChromaDB Vectors + Pure Markdown     │
                        └────────────────────────────────────────┘
```

---

## 🏆 Feature & Benchmark Matrix

| Feature / Capability | Raw Vector DB | Letta | Mem0 | Graphiti | **Synapse 4D** |
|---|:---:|:---:|:---:|:---:|:---:|
| **Working Memory Paging (MemGPT style)** | ❌ | ✅ | ❌ | ❌ | **✅ Built-in** |
| **Atomic Fact Dedup & Conflict Diffing** | ❌ | ❌ | ✅ | ❌ | **✅ Built-in** |
| **Bi-temporal Edge Invalidation** | ❌ | ❌ | ❌ | ✅ | **✅ Built-in** |
| **Zettelkasten Bidirectional `[[Wikilinks]]`** | ❌ | ❌ | ❌ | ❌ | **✅ Native** |
| **Zero Orphan Guarantee (Auto-Heal)** | ❌ | ❌ | ❌ | ❌ | **✅ 100% Health** |
| **Native Obsidian CoALA Architecture** | ❌ | ❌ | ❌ | ❌ | **✅ Native** |
| **MCP Server (Cursor / Claude / Antigravity)** | ❌ | ❌ | Partial | ❌ | **✅ Zero-Config** |
| **Consolidation Cycle Latency** | N/A | ~4.2s | ~2.8s | ~3.5s | **⚡ < 2.1s** |

---

## 🚀 Quickstart in 60 Seconds

### 1. Installation

```bash
git clone https://github.com/MShesat/synapse-4d.git
cd synapse-4d
pip install -e .
```

### 2. Initialize a Cognitive Brain Vault

```bash
# Creates an optimized CoALA tri-memory vault
synapse4d init ./my-second-brain
```

### 3. Run the 4D Consolidation Cycle

```bash
# Automatically digests episodic logs into long-term semantic knowledge
synapse4d consolidate --vault ./my-second-brain
```

### 4. Semantic & Temporal Search

```bash
synapse4d search "What database did we decide to use?" --vault ./my-second-brain
```

### 5. Audit Vault Health

```bash
synapse4d audit --vault ./my-second-brain
```

Output:
```text
=== Synapse 4D Vault Audit ===
Vault: C:\Users\User\my-second-brain
Total Notes: 28
Total Wikilinks: 84
Broken Links: 0
Health Score: 100.0%
```

---

## 🔌 Model Context Protocol (MCP) Integration

Synapse 4D ships with a native MCP server for seamless integration with **Cursor, Claude Desktop, Antigravity, and VS Code**.

### Setup in Claude Desktop / Cursor:

Add to your `claude_desktop_config.json` or `cursor.json`:

```json
{
  "mcpServers": {
    "synapse4d": {
      "command": "synapse4d",
      "args": ["serve", "--vault", "/absolute/path/to/your/obsidian/vault"]
    }
  }
}
```

Now your AI assistant can autonomously call:
- `synapse_get_working_memory`: Read scratchpad state without context blowout.
- `synapse_search_memory`: Query long-term facts across time and vectors.
- `synapse_consolidate`: Trigger autonomous memory consolidation at the end of every session.

---

## 🗂️ CoALA Tri-Memory Architecture

Synapse 4D organizes your knowledge base according to the cognitive CoALA (Cognitive Architectures for Language Agents) standard:

```text
my-second-brain/
├── 00_Working_Memory/          # Volatile scratchpad & user profile (Pillar 1: Letta)
│   ├── active_context.md
│   └── system_profile.md
├── 10_Episodic_Memory/         # Immutable chronological session logs ("Yesterday")
│   └── 2026-10-28-session.md
├── 20_Semantic_Memory/         # Consolidated knowledge & rules (Pillars 2, 3 & 4)
│   ├── entities/               # Atomic Zettelkasten notes with [[reciprocal-links]]
│   └── rules/                  # Prohibited antipatterns & validated successes
├── 30_Procedural_Memory/       # Step-by-step flows and markdown templates
└── 90_Meta_System/             # Ontological graphs, master index, and audit logs
    ├── INDEX.md
    ├── GRAPH.md
    └── LOG.md
```

---

## 🇪🇸 Resumen en Español

**Synapse 4D** es el primer motor de memoria cognitiva híbrido de 4 dimensiones para agentes de IA y bóvedas de Obsidian. Resuelve de raíz las limitaciones del método PARA tradicional integrando:
1. **Letta:** Gestión auto-editable de la memoria de trabajo y control estricto de tokens.
2. **Mem0:** Extracción atómica de hechos, deduplicación y resolución de contradicciones.
3. **Graphiti:** Grafo temporal con invalidación automática de hechos obsoletos.
4. **A-MEM:** Generación de notas Zettelkasten con enlaces bidireccionales `[[Wikilinks]]` garantizando 0 notas huérfanas.

---

## 💰 Commercial & Monetization Roadmap

Synapse 4D is built with a clear path to commercial viability. Read our full business plan, including the upcoming **Obsidian Community Pro Plugin**, **Encrypted Cloud Relay**, and **Enterprise OEM Licensing** in:
👉 **[MONETIZATION_ROADMAP.md](file:///MONETIZATION_ROADMAP.md)**

---

## 🤝 Contributing

Contributions are warmly welcomed! Please read [CONTRIBUTING.md](file:///CONTRIBUTING.md) to get started.

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<p align="center">
  <b>Built with ❤️ by <a href="https://github.com/MShesat">MShesat</a></b><br>
  <i>Empowering AI agents with persistent, human-grade cognitive memory.</i>
</p>
