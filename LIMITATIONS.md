# Known Limitations & Engineering Constraints

**Synapse 4D**  
*Last updated: October 28, 2026*

This document provides a transparent, candid inventory of known technical constraints, experimental components, and areas where Synapse 4D is still maturing. We believe software tools for engineers and knowledge workers should clearly state their boundaries.

---

### 1. Small Sample Calibration ($n=16$)

- **Current State:** The empirical heuristics used for polarity scoring, antonym distance thresholds, and supersession classification were calibrated against an initial test suite of sixteen controlled scenarios ($n=16$).
- **Statistical Reality:** At $n=16$, the binomial 95% confidence interval spans between **71.7% and 98.9%**.
- **Practical Implication:** While these heuristics reliably catch direct contradictions (such as affirmative statements followed by explicit negations), they cannot be guaranteed to catch nuanced or contextual contradictions across broader real-world datasets. A large-scale empirical test suite is in development.

---

### 2. Fact Extraction Quality Depends on LLM Model

- **Current State:** The fact distillation layer relies on either a local language model (via Ollama or local inference) or an external API provider (via `--allow-cloud-extraction`). When no LLM is available, it relies on fallback regular expressions and token matching.
- **Practical Implication:** If the local model is small (e.g. 1B–3B parameters) or poorly instruction-tuned, it may hallucinate relationships, omit subtle conditionals, or misidentify the subject/predicate of a statement. The deterministic regex fallback catches only predictable sentence structures.

---

### 3. HUD Visualizer is in Transition

- **Current State:** The visual graph Head-Up Display (HUD) is currently undergoing an architectural transition.
- **Practical Implication:** The visualizer was originally built as a standalone webview dashboard and is being migrated toward tighter canvas integration and Obsidian native rendering. Users may encounter occasional visual lag, incomplete edge filters, or layout shifts on high-resolution displays until the refactor stabilizes.

---

### 4. No 10,000+ Fact Benchmark Yet

- **Current State:** Performance testing has covered vaults with several hundred to a few thousand facts and notes.
- **Practical Implication:** We have not yet published a reproducible benchmark covering 10,000+ continuously updated, multi-turn bi-temporal facts. While SQLite and ONNX embeddings theoretically scale well to tens of thousands of records, index construction times, UDF query latency, and graph traversal at that scale remain unmeasured under rigorous load testing.

---

### 5. Automated Vault Migration Untested on Arbitrary Third-Party Vaults

- **Current State:** The `synapse4d migrate` command has been validated on standardized Obsidian vault structures following common Daily Notes and Zettelkasten conventions.
- **Practical Implication:** Heavily customized community vaults—such as those with deeply nested subfolders, unusual YAML frontmatter structures, multi-line wikilink aliases, or encrypted files—may encounter parsing warnings or require manual directory mapping.

---

### 6. Single-User Process Concurrency (No Distributed Multi-Process Testing)

- **Current State:** Database concurrency is managed via SQLite in Write-Ahead Logging (WAL) mode combined with process-level file locking (`filelock`).
- **Practical Implication:** Synapse 4D is engineered for individual desktop knowledge workers running an editor alongside a local agent (such as Cursor or Claude Desktop). It has not been stress-tested for concurrent writes across multiple independent OS processes simultaneously, and it is not intended to serve as a multi-tenant distributed database.

---

### 7. Crash Recovery Tested with Graceful Exits, Not Adversarial SIGKILL

- **Current State:** The two-phase commit journal (`pending_writes.json` and backup staging) protects against abrupt terminal closures, standard unhandled Python exceptions, and interrupted CLI runs.
- **Practical Implication:** We have not yet conducted formal chaos tests with hard kernel crashes (`kill -9` / `SIGKILL` issued during the exact microsecond of an SQLite page write). SQLite itself is ACID-compliant and crash-safe, but the synchronization between the SQLite state and physical Markdown files during catastrophic system termination is still being hardened.

---

### 8. Desktop Binaries Are Currently Unsigned

- **Current State:** Standalone pre-built desktop executables for Windows and macOS provided in the Pro Pack are currently self-compiled and lack paid commercial code-signing certificates.
- **Practical Implication:** Operating systems will show security prompts upon first run (such as Microsoft Defender SmartScreen on Windows or Apple Gatekeeper warnings on macOS) requiring the user to manually select "Run anyway" or allow execution in system security settings.

---

### 9. Obsidian Plugin Lacks Broad End-to-End Field Testing

- **Current State:** The Obsidian Community Plugin has been verified inside controlled test vaults and primary developer machines.
- **Practical Implication:** Obsidian has a vast ecosystem of third-party community plugins and themes (Dataview, Canvas, Excalidraw, etc.). Edge interactions, conflicting event listeners, or mobile sync plugins may surface unexpected behaviors that have not yet been observed in developer testing.

---

### 10. Academic Paper v1 Contained Inflated Claims

- **Current State:** The initial version (v1) of the conceptual white paper published on Zenodo contained theoretical terminology and early enthusiastic projections that did not reflect strict empirical evaluation.
- **Practical Implication:** A revised Version 2 preprint with an explicit errata note is currently being prepared. We are actively decoupling formal engineering documentation from speculative claims.

---

### Feedback and Contributions

If you discover an unlisted edge case, performance bottleneck, or unexpected failure mode, please report it:
- **Issue Tracker:** [https://github.com/MShesat/synapse-4d/issues](https://github.com/MShesat/synapse-4d/issues)
- **Discussion Forum:** [https://github.com/MShesat/synapse-4d/discussions](https://github.com/MShesat/synapse-4d/discussions)

<!-- 2026-10-28 — borrador v1 — pendiente de revisión -->
