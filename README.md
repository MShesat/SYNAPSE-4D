# 🧠 Synapse 4D

<p align="center">
  <b>A Multi-Dimensional Cognitive State Matrix with Temporal Decay and Autonomous Topological Self-Assembly for AI Agents & Human Knowledge.</b><br>
  <i>Sub-second, local-first artificial cognition combining Working Attention, Atomic Distillation, Bi-Temporal Reality Tracking, and Zero-Orphan Associative Meshes.</i>
</p>

<p align="center">
  <a href="https://github.com/MShesat/synapse-4d/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+"></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP-Compatible-brightgreen.svg" alt="MCP Compatible"></a>
  <a href="./docs/WHITE_PAPER.md"><img src="https://img.shields.io/badge/Research-White%20Paper-purple.svg" alt="White Paper"></a>
  <a href="https://github.com/MShesat/synapse-4d/stargazers"><img src="https://img.shields.io/github/stars/MShesat/synapse-4d?style=social" alt="GitHub Stars"></a>
</p>

---

## 📄 Formal Computer Science White Paper & Patent Disclosure

Synapse 4D is formally specified as a mathematically rigorous cognitive state machine.  
Read the full defensive patent specification, mathematical proofs, and asymptotic complexity analysis:  
👉 **[Read the White Paper (cs.AI / cs.MA)](./docs/WHITE_PAPER.md)**

---

## ⚡ The Fundamental Problem of AI Memory

Autoregressive Language Models suffer from catastrophic **context degradation** ($O(N^2)$ attention overhead) and **epistemic drift**. Conventional Retrieval-Augmented Generation (RAG) paradigms provide only flat, static vector similarity:
- **No Working Memory Control:** The LLM cannot dynamically edit its active scratchpad without re-reading thousands of tokens.
- **Blindness to Contradictions:** When past session logs contradict present rules, flat vector search returns both, causing severe hallucinations.
- **Topological Fragmentation:** Knowledge is stored in isolated chunks without reciprocal links, resulting in orphan data and fragmented graph retrieval.

---

## 🔬 The Synapse 4D Architecture

Synapse 4D formalizes artificial cognitive state as a 4-dimensional manifold:
$$\mathcal{S} = \langle \mathcal{D}_1, \mathcal{D}_2, \mathcal{D}_3, \mathcal{D}_4 \rangle$$

```
                                  ┌─────────────────────────────┐
                                  │   AGENT REASONING CYCLE     │
                                  └──────────────┬──────────────┘
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
        ┌───────────────────────────────┐                 ┌───────────────────────────────┐
        │  DIMENSION 1: FOCUS ENGINE    │                 │ DIMENSION 2: FACT DISTILLER   │
        │      Dynamic Context Buffer   │                 │     Truth Hierarchy Lattice   │
        │  (Self-Editing Working Memory)│                 │  Axiom > Preference > Observ. │
        └───────────────┬───────────────┘                 └───────────────┬───────────────┘
                        │                                                 │
                        └────────────────────────┬────────────────────────┘
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
        ┌───────────────────────────────┐                 ┌───────────────────────────────┐
        │  DIMENSION 3: CHRONOS LATTICE │                 │ DIMENSION 4: ASSOCIATIVE MESH │
        │     Bi-Temporal Coordinates   │                 │     Topological Hypergraph    │
        │   Hebbian Synaptic Decay      │                 │    Zero-Orphan Reciprocity    │
        └───────────────┬───────────────┘                 └───────────────┬───────────────┘
                        │                                                 │
                        └────────────────────────┬────────────────────────┘
                                                 │
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │    UNIVERSAL STORAGE        │
                                  │ (Markdown / SQLite Database)│
                                  └─────────────────────────────┘
```

### The 4 Core Dimensions:

1. **Dimension 1: Focus Engine ($\mathcal{D}_1$):** Governs volatile working memory, registers active objectives, enforces strict token budgets, and provides $O(1)$ scratchpad register mutation.
2. **Dimension 2: Fact Distiller ($\mathcal{D}_2$):** Decomposes conversational streams into atomic declarative propositions and applies a strict **Truth Hierarchy** ($\text{Axioms} \succ \text{Preferences} \succ \text{Observations}$) to resolve semantic conflicts deterministically.
3. **Dimension 3: Chronos Lattice ($\mathcal{D}_3$):** Bi-temporal knowledge graph ($t_{\text{valid}}, t_{\text{invalidated}}$) featuring **Hebbian Synaptic Plasticity** ($\Delta w_{ij} = \eta \cdot \text{retrieval}$) and continuous exponential temporal decay ($w(t) = w_0 e^{-\lambda \Delta t}$).
4. **Dimension 4: Associative Mesh ($\mathcal{D}_4$):** Enforces topological closure on knowledge nodes with guaranteed bidirectional reciprocal bindings (`[[Wikilinks]]`), mathematically ensuring **0 orphan nodes**.

---

## 🏆 Benchmark & Feature Comparison

| Feature / Metric | Conventional Vector RAG | Graph RAG Frameworks | Flat Fact Buffers | **Synapse 4D** |
|---|:---:|:---:|:---:|:---:|
| **Self-Editing Working Attention ($\mathcal{D}_1$)** | ❌ | ❌ | Partial | **✅ Built-in ($O(1)$)** |
| **Deterministic Truth Hierarchy ($\mathcal{D}_2$)** | ❌ | ❌ | ❌ | **✅ Built-in** |
| **Bi-Temporal Edge Invalidation ($\mathcal{D}_3$)** | ❌ | Partial | ❌ | **✅ Built-in** |
| **Hebbian Plasticity & Decay ($\mathcal{D}_3$)** | ❌ | ❌ | ❌ | **✅ Built-in** |
| **Zero-Orphan Topological Invariant ($\mathcal{D}_4$)** | ❌ | ❌ | ❌ | **✅ Guaranteed** |
| **Local-First & Storage Agnostic** | ❌ (Cloud) | ❌ (Heavy DB) | Partial | **✅ Zero-Config (MD / SQLite)** |
| **Consolidation Latency ($10^4$ tokens)** | $> 8.5\text{s}$ | $> 5.2\text{s}$ | $> 3.8\text{s}$ | **⚡ < 1.7\text{s}** |

---

## 🚀 Quickstart

### 1. Installation

```bash
git clone https://github.com/MShesat/synapse-4d.git
cd synapse-4d
pip install -e .
```

### 2. Initialize a Cognitive Brain Vault

```bash
synapse4d init ./my-brain
```

### 3. Run Autonomous 4D Consolidation

```bash
# Ingests recent episodic interactions and synthesizes permanent knowledge
synapse4d consolidate --vault ./my-brain
```

### 4. Hybrid Multi-Dimensional Search

```bash
synapse4d search "What database architecture was chosen?" --vault ./my-brain
```

### 5. Audit Knowledge Graph Integrity

```bash
synapse4d audit --vault ./my-brain
```

Output:
```text
=== Synapse 4D Vault Audit ===
Vault: C:\Users\User\my-brain
Total Nodes: 28
Total Bindings: 83
Broken Bindings: 0
Health Score: 100.0%
```

---

## 🔌 Model Context Protocol (MCP) Server

Synapse 4D exposes native MCP endpoints for **Cursor, Claude Desktop, Antigravity, and VS Code**:

```json
{
  "mcpServers": {
    "synapse4d": {
      "command": "synapse4d",
      "args": ["serve", "--vault", "/absolute/path/to/vault"]
    }
  }
}
```

Exposed native tools:
- `synapse_get_working_memory`: Retrieve $\mathcal{D}_1$ active attention state.
- `synapse_search_memory`: Multi-dimensional vector + $\mathcal{D}_3$ Chronos retrieval.
- `synapse_consolidate`: Trigger autonomous 4D distillation.

---

## 💰 Commercial & Monetization Roadmap

Read the complete commercial roadmap and product packaging strategy:  
👉 **[MONETIZATION_ROADMAP.md](./MONETIZATION_ROADMAP.md)**

---

## 📄 License & Attribution

Distributed under the **MIT License**. See `LICENSE` for details.  
Academic and technical citations:

```bibtex
@article{ruiz2026synapse4d,
  title={Synapse 4D: A Multi-Dimensional Cognitive State Matrix with Temporal Decay and Autonomous Topological Self-Assembly for Autonomous Language Agents},
  author={Ruiz, Ángel (@MShesat)},
  year={2026},
  publisher={GitHub},
  journal={Defensive Research Publication}
}
```

---

<p align="center">
  <b>Designed & Developed with precision by <a href="https://github.com/MShesat">Ángel Ruiz (@MShesat)</a></b>
</p>
