# 🧠 Synapse 4D

<p align="center">
  <img src="./assets/synapse4d_logo.jpg" alt="Synapse 4D Logo" width="260">
</p>

<p align="center">
  <b>Local-first bi-temporal memory for Obsidian + Claude/Cursor, without cloud.</b><br>
  <i>A well-engineered implementation of established cognitive memory and temporal database concepts, packaged for privacy-conscious developers and knowledge workers.</i>
</p>

<p align="center">
  <a href="https://github.com/MShesat/synapse-4d/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+"></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP-Compatible-brightgreen.svg" alt="MCP Compatible"></a>
  <a href="https://doi.org/10.5281/zenodo.23737307"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.23737307.svg" alt="DOI: 10.5281/zenodo.23737307"></a>
</p>

---

## 📌 What is Synapse 4D?

Standard Retrieval-Augmented Generation (RAG) and basic agent memory setups treat memory as flat text chunks searched with cosine similarity. This leads to common failure modes:
1. **Temporal Blindness:** When notes from six months ago say *"Deploy with Docker Swarm"* and notes from yesterday say *"Migrated completely to Kubernetes"*, flat vector search returns both, forcing the model to guess which is true.
2. **Destructive Overwrites:** Deleting or replacing text files destroys the causal history of how and why architectural decisions evolved.
3. **Cloud Lock-in & Privacy Risks:** Many agent memory solutions require sending your private notes and database entries to remote cloud APIs on recurring monthly subscriptions.

**Synapse 4D** provides a local-first memory layer running directly on your machine. It pairs a **bi-temporal SQLite database** (`valid_from`, `valid_to`, `invalidated_at`) with **local ONNX vector embeddings** and **two-way linked Markdown stubs** in your Obsidian vault. It connects to developer tools like Claude Desktop and Cursor via the Model Context Protocol (MCP).

---

## ⚙️ What It Does

Synapse 4D structures agent memory across four practical operational dimensions:

- **Focus Engine ($\mathcal{D}_1$):** A local working attention buffer that tracks active task context and session scratchpads with write-behind persistence to Markdown.
- **Fact Distiller ($\mathcal{D}_2$):** Extracts atomic assertions from conversation transcripts using local models (e.g. Ollama) or heuristic regex fallbacks. Uses a Truth Hierarchy rule system to identify when newer assertions supersede older ones (`status = 'superseded'`), designed to avoid contradictory prompts when supersession criteria match.
- **Relational Chronos Storage ($\mathcal{D}_3$):** SQLite in Write-Ahead Logging (WAL) mode with process file-locking. Every record maintains bi-temporal validity periods, allowing agents to query the system state as it was known at any specific point in time. Includes lazy Hebbian recency scoring evaluated at query time.
- **Associative Mesh ($\mathcal{D}_4$):** Enforces reciprocal edge consistency across Markdown references and creates lightweight associative stubs with backlink provenance inside your vault.

---

## ⚠️ What It Does NOT Do (Limitations)

We believe in engineering clarity over hyperbole. Please keep the following in mind:

- **Not a Magic Hallucination Cure:** Fact distillation accuracy depends directly on the extraction model used. Ambiguous phrasing or subtle negations may still be misclassified.
- **Limited Calibration Dataset:** Heuristic conflict thresholds were calibrated on a small initial sample ($n=16$, 95% confidence interval: 71.7%–98.9%). Large-scale empirical validation is actively ongoing.
- **Desktop Single-User Design:** Built with SQLite WAL and process file locks. It is designed for individual desktop agents and local development, not high-concurrency multi-tenant distributed cloud servers.
- **No Cloud Sync Provided:** Synapse 4D stores everything on your local drive. Syncing across devices requires your own file sync layer (e.g., Git, Syncthing, or Obsidian Sync).

👉 For a comprehensive, honest list of edge cases and known constraints, please read [LIMITATIONS.md](LIMITATIONS.md).

---

## 🚀 Quick Start (CLI)

### 1. Installation

```bash
pip install synapse4d
```

### 2. Initialize a Local Vault

```bash
synapse4d init ./my-vault
```

This creates the `.synapse/` configuration directory, database files, and journal templates inside your chosen folder.

### 3. Consolidate Session Notes

Extract new facts from recent session transcripts and update temporal validity records:

```bash
synapse4d consolidate --vault ./my-vault
```

### 4. Search Memory with Bi-Temporal Filters

Query your memory state as of today, or inspect what the system believed on an earlier date:

```bash
synapse4d search "database preference" --vault ./my-vault
```

### 5. Review & Audit Provisional Facts

Inspect provisional facts extracted by heuristic rules and confirm or dismiss them:

```bash
synapse4d review --vault ./my-vault
```

---

## 🔌 Integration with Claude Desktop & Cursor (MCP)

Synapse 4D includes a built-in Model Context Protocol (MCP) server so your desktop agents can read and update memory transparently.

### Claude Desktop Configuration

Add the following entry to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "synapse4d": {
      "command": "synapse4d",
      "args": ["mcp", "--vault", "C:/path/to/your/vault"]
    }
  }
}
```

### Cursor IDE Configuration

In Cursor's **Features > MCP Servers** settings, add a new command-type server:
- **Name:** `synapse4d`
- **Type:** `command`
- **Command:** `synapse4d mcp --vault /absolute/path/to/your/vault`

---

## 💎 Integration with Obsidian (Pro Edition)

While the open-source CLI and MCP server work with any directory of Markdown files, **Synapse 4D Pro Edition** is packaged specifically for Obsidian power users who want a zero-terminal visual workflow:

- **Obsidian Community Plugin:** Status bar health indicators, manual consolidation buttons, and automatic note linking.
- **Interactive HUD Visualizer:** Real-time 2D/3D visual inspection of relational links, active attention nodes, and superseded historical facts.
- **Standalone Binaries:** Single-file executables for Windows, macOS, and Linux without needing to manage Python environments.
- **Priority Support:** Direct technical support with SLA < 48h.

👉 Learn more at **[Synapse 4D Pro Edition](https://github.com/MShesat/synapse-4d-pro-edition)**.

---

## 🗺️ Project Status & Roadmap

- **Phase 1: Core Relational Engine & Schema** — ✅ Complete (SQLite WAL, bi-temporal schema, FastEmbed ONNX local pipeline).
- **Phase 2: Agent Protocols & Journaling** — ✅ Complete (MCP server, CLI subcommands, two-phase commit recovery journal).
- **Phase 3: Visual Tooling & Obsidian Plugin** — 🟡 In Progress (HUD canvas transition, Obsidian community plugin beta).
- **Phase 4: Multi-Device Sync & Large-Scale Benchmarks** — ⚪ Planned (Benchmark suite with 10,000+ entries, conflict-free sync exploration).

---

## 📄 Academic Preprint & Errata Notice

An early preprint describing the initial conceptual design is registered at Zenodo:
- **Preprint DOI v1:** [10.5281/zenodo.23737307](https://doi.org/10.5281/zenodo.23737307)

> **⚠️ Errata Notice:** Version 1 of this preprint contained several enthusiastic formulations and broad theoretical claims (including early precision claims based on a restricted sample). We are preparing a revised Version 2 preprint with an accompanying errata note to calibrate all claims strictly against verifiable, reproducible benchmark data.

---

## 📜 License

- **Engine Core:** Licensed under the permissive [MIT License](LICENSE).
- **Pro Pack Add-ons:** Licensed under the commercial [Terms of Service](TERMS.md).

---

## 📬 Contact & Community

- **Maintainer:** Ángel Ruiz ([@MShesat](https://github.com/MShesat))
- **Bug Reports & Issues:** [https://github.com/MShesat/synapse-4d/issues](https://github.com/MShesat/synapse-4d/issues)
- **Commercial Inquiries & Support:** `synapse4d.support@gmail.com`

<!-- 2026-10-28 — borrador v1 — pendiente de revisión -->
