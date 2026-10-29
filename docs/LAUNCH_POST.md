# Launch Posts: Hacker News & Reddit

---

## 🚀 Version 1: Show HN (Hacker News)

### Title (78 characters)
```text
Show HN: Synapse 4D – Local bi-temporal memory for Obsidian and Claude/Cursor
```

### Body (~280 words)
```markdown
Hi HN,

I built Synapse 4D, an open-source (MIT), local-first memory layer for desktop agents (Claude Desktop, Cursor) that integrates with an Obsidian Markdown vault.

### The Problem
Most agent memory setups use flat vector search over conversation history or document chunks. In practice, this breaks as projects evolve: when session logs from six months ago say "use PostgreSQL" and notes from last week say "migrated to SQLite", flat cosine similarity returns both. The agent gets conflicting prompts and has to guess what is currently true. Deleting older files fixes the prompt but destroys the causal decision log.

### What Synapse 4D Does
Synapse 4D stores memories in a local SQLite database using Write-Ahead Logging (WAL) with a bi-temporal schema (`valid_from`, `valid_to`, `invalidated_at`, `superseded_by`). 

- When new statements contradict older ones, the Truth Hierarchy marks the older record as superseded rather than performing a destructive delete.
- Semantic retrieval runs locally using quantized ONNX embeddings (`fastembed`), so zero text or vector data leaves your machine.
- Exposes a native Model Context Protocol (MCP) server so Claude and Cursor can read and update memory directly during coding sessions.
- Generates reciprocal Markdown stubs and wikilinks inside your local Obsidian vault.

### What It Does NOT Do
- It is not a cloud service or multi-tenant database. It runs on `127.0.0.1` for single-user desktop workflows.
- Fact extraction depends directly on the model you use (local Ollama or optional API key); smaller models can miss subtle conditionals.
- Our heuristic conflict thresholds were calibrated on a small dataset (n=16, 95% CI: 71.7%–98.9%). A 10k+ benchmark suite is still in development.
- Full details on known edge cases: [LIMITATIONS.md](https://github.com/MShesat/synapse-4d/blob/main/LIMITATIONS.md)

- **GitHub Repo (MIT):** https://github.com/MShesat/synapse-4d
- **Early Preprint (Zenodo):** https://doi.org/10.5281/zenodo.23737307 *(Note: A revised v2 with an errata note is in progress to adjust earlier theoretical claims to our empirical benchmarks).*

Would love your feedback on the schema design and MCP integration!
```

---

## 📝 Version 2: r/ObsidianMD (Reddit)

### Title
```text
I built an open-source, local-first memory layer for Claude, Cursor, and Obsidian
```

### Body (~215 words)
```markdown
Hey r/ObsidianMD,

Like many here, I use Obsidian as my primary second brain and rely on desktop coding agents (Claude Desktop, Cursor). But I always disliked two things about typical "AI memory" tools:
1. They require sending your private notes to a third-party cloud database on a monthly subscription.
2. They do simple vector search without understanding time—so when your project decisions change, the agent mixes up old rules with new ones.

I built **Synapse 4D** to address this as a clean, local-first tool.

### How it works with Obsidian:
- **100% Local:** Runs on your machine using SQLite and local ONNX embeddings (`fastembed`). Zero cloud telemetry, no remote servers.
- **Bi-Temporal Tracking:** Keeps track of when a note or fact was created and when it was superseded, keeping your historical notes intact without confusing your agent.
- **Native Obsidian Stubs:** Automatically maintains reciprocal wikilinks (`[[Note]]`) and stubs so your visual graph stays coherent.
- **MCP Server:** Works out-of-the-box with Claude Desktop and Cursor.

### Limitations:
It's an active project: fact extraction quality depends on your local LLM (e.g. Ollama), and we're currently refactoring the visual graph HUD. See our full [LIMITATIONS.md](https://github.com/MShesat/synapse-4d/blob/main/LIMITATIONS.md).

- **GitHub (MIT Engine):** https://github.com/MShesat/synapse-4d
- **Paper v1 (Zenodo):** https://doi.org/10.5281/zenodo.23737307 *(v2 revision with errata coming soon)*

I'd appreciate any thoughts or feedback from the community!
```

<!-- 2026-10-28 — borrador v1 — pendiente de revisión -->
