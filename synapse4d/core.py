"""
Synapse 4D - Central Cognitive Engine
Unifies the 4 Dimensions of Artificial Cognitive State:
  - D1: Focus Engine (Dynamic Working Attention)
  - D2: Fact Distiller (Atomic Synthesis & Truth Hierarchy)
  - D3: Chronos Lattice (Bi-Temporal Knowledge & Hebbian Plasticity)
  - D4: Associative Mesh (Topological Hypergraph & Zero-Orphan Binding)
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import os
import re

from synapse4d.dimensions.focus import FocusEngine
from synapse4d.dimensions.distiller import FactDistiller
from synapse4d.dimensions.chronos import ChronosLattice
from synapse4d.dimensions.mesh import AssociativeMesh
from synapse4d.memory.vector_store import VectorStore

class SynapseEngine:
    """The unified 4D Cognitive State Machine for Autonomous Agents."""

    def __init__(self, vault_path: str | Path):
        self.vault_path = Path(vault_path).resolve()
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Vault path does not exist: {self.vault_path}")

        # Directory resolution (agnostic to localized or standard schemas)
        self.working_dir = self._resolve_dir(["00_Working_Memory", "00_Memoria_de_Trabajo"])
        self.episodic_dir = self._resolve_dir(["10_Episodic_Memory", "10_Memoria_Episodica"])
        self.semantic_dir = self._resolve_dir(["20_Semantic_Memory", "20_Memoria_Semantica"])
        self.procedural_dir = self._resolve_dir(["30_Procedural_Memory", "30_Memoria_Procedimental"])
        self.meta_dir = self._resolve_dir(["90_Meta_System", "90_Meta_Sistema"])

        # Synapse local persistent state
        self.state_dir = self.vault_path / ".synapse"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Initialize the 4 Core Dimensions
        self.focus = FocusEngine(self.vault_path)
        self.distiller = FactDistiller()
        self.chronos = ChronosLattice(self.state_dir)
        self.mesh = AssociativeMesh(self.semantic_dir)
        self.vector_store = VectorStore(self.state_dir / "chroma")

    def _resolve_dir(self, candidates: List[str]) -> Path:
        for c in candidates:
            p = self.vault_path / c
            if p.exists():
                return p
        default_dir = self.vault_path / candidates[0]
        default_dir.mkdir(parents=True, exist_ok=True)
        return default_dir

    def get_working_context(self) -> Dict[str, Any]:
        """Dimension 1 (Focus): Retrieve current scratchpad state and active attention window."""
        return self.focus.get_focus_state()

    def update_working_memory(self, section: str, content: str) -> bool:
        """Dimension 1 (Focus): Dynamically update an active working memory section."""
        return self.focus.update_section(section, content)

    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Hybrid Multi-Dimensional Retrieval: Combines vector semantics with Chronos Lattice weights."""
        vector_hits = self.vector_store.query(query, n_results=limit)
        active_lattice = self.chronos.get_active_lattice(apply_decay=True)

        # Hebbian reinforcement on matching hits
        for hit in vector_hits:
            source = hit.get("metadata", {}).get("source", "")
            if source:
                self.chronos.reinforce_synapse("agent_query", source)

        return {
            "query": query,
            "vector_results": vector_hits,
            "total_indexed_chunks": self.vector_store.count(),
            "active_lattice_edges": len(active_lattice)
        }

    def consolidate(self, recent_only: bool = True) -> Dict[str, Any]:
        """
        Executes the Autonomous 4D Consolidation Cycle:
        1. Ingests raw episodic interaction streams.
        2. D2 (Distiller) extracts atomic facts & arbitrates truth conflicts.
        3. D3 (Chronos) supersedes invalidated states & updates synaptic timestamps.
        4. D4 (Mesh) synthesizes cohesive nodes with bidirectional topological bindings.
        5. D1 (Focus) updates active attention context.
        6. Vector store synchronizes semantic embeddings.
        """
        stats = {
            "processed_streams": 0,
            "facts_distilled": 0,
            "facts_retained": 0,
            "facts_superseded": 0,
            "facts_redundant": 0,
            "status": "success"
        }

        # Gather episodic files
        streams = list(self.episodic_dir.glob("*.md"))
        if recent_only and streams:
            streams.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            streams = streams[:3]

        incoming_facts = []
        for s in streams:
            stats["processed_streams"] += 1
            content = s.read_text(encoding="utf-8", errors="replace")
            facts = self.distiller.distill_atomic_facts(content)
            incoming_facts.extend(facts)

            self.vector_store.upsert(
                doc_id=s.stem,
                document=content[:2000],
                metadata={"source": s.name, "dimension": "episodic_stream"}
            )

        stats["facts_distilled"] = len(incoming_facts)

        # Gather existing facts for arbitration
        existing = []
        for node in self.semantic_dir.rglob("*.md"):
            existing.extend(self.distiller.distill_atomic_facts(node.read_text(encoding="utf-8", errors="replace")))

        arbitration = self.distiller.arbitrate_conflicts(incoming_facts, existing)
        stats["facts_retained"] = len(arbitration["retained"])
        stats["facts_superseded"] = len(arbitration["superseded"])
        stats["facts_redundant"] = len(arbitration["redundant"])

        # Update Chronos Lattice
        for s in arbitration["superseded"]:
            self.chronos.register_relation(
                source=s.get("old_fact", "Entity")[:30],
                relation="superseded_by",
                target=s.get("new_fact", "UpdatedEntity")[:30],
                context=s.get("reason", "")
            )

        # D1 Focus update
        self.focus.append_observation(
            "Consolidaciones Recientes",
            f"Consolidación 4D ejecutada: {stats['facts_retained']} hechos retenidos, {stats['facts_superseded']} actualizados."
        )

        return stats

    def audit(self) -> Dict[str, Any]:
        """Audits the cognitive state for broken topological links, graph fragmentation, and health score."""
        all_nodes = [f for f in self.vault_path.rglob("*.md") if ".synapse" not in str(f)]
        stem_map = {f.stem.lower(): f for f in all_nodes}

        broken = []
        total_bindings = 0

        for node in all_nodes:
            text = node.read_text(encoding="utf-8", errors="replace")
            links = re.findall(r'\[\[(.*?)\]\]', text)
            for l in links:
                total_bindings += 1
                raw = l.split("|")[0].split("#")[0].strip()
                clean = raw.replace("\\", "/").split("/")[-1].replace(".md", "").strip().lower()
                if clean and clean not in stem_map and not clean.startswith("$"):
                    broken.append({"file": node.name, "target": l})

        health = round((1.0 - (len(broken) / max(total_bindings, 1))) * 100, 1)

        return {
            "vault_path": str(self.vault_path),
            "total_nodes": len(all_nodes),
            "total_bindings": total_bindings,
            "broken_bindings_count": len(broken),
            "broken_bindings": broken[:10],
            "health_score": f"{health}%"
        }
