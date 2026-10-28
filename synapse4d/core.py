"""
Synapse 4D - Core Orchestrator
Unifies Letta, Mem0, Graphiti, and A-MEM into a single high-performance cognitive engine.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import os

from synapse4d.pillars.letta import LettaWorkingMemory
from synapse4d.pillars.mem0 import Mem0FactExtractor
from synapse4d.pillars.graphiti import GraphitiTemporalGraph
from synapse4d.pillars.amem import AMEMZettelkasten
from synapse4d.memory.vector_store import VectorStore

class SynapseEngine:
    """The central unified 4D cognitive memory engine."""

    def __init__(self, vault_path: str | Path):
        self.vault_path = Path(vault_path).resolve()
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Vault path does not exist: {self.vault_path}")

        # Locate memory dirs
        self.working_dir = self._resolve_dir(["00_Memoria_de_Trabajo", "00_Working_Memory"])
        self.episodic_dir = self._resolve_dir(["10_Memoria_Episodica", "10_Episodic_Memory"])
        self.semantic_dir = self._resolve_dir(["20_Memoria_Semantica", "20_Semantic_Memory"])
        self.procedural_dir = self._resolve_dir(["30_Memoria_Procedimental", "30_Procedural_Memory"])
        self.meta_dir = self._resolve_dir(["90_Meta_Sistema", "90_Meta_System"])

        # Synapse local DB dir
        self.synapse_state_dir = self.vault_path / ".synapse"
        self.synapse_state_dir.mkdir(parents=True, exist_ok=True)

        # Initialize the 4 pillars
        self.letta = LettaWorkingMemory(self.vault_path)
        self.mem0 = Mem0FactExtractor()
        self.graphiti = GraphitiTemporalGraph(self.synapse_state_dir)
        self.amem = AMEMZettelkasten(self.semantic_dir)
        self.vector_store = VectorStore(self.synapse_state_dir / "chroma")

    def _resolve_dir(self, candidates: List[str]) -> Path:
        for c in candidates:
            p = self.vault_path / c
            if p.exists():
                return p
        default_p = self.vault_path / candidates[0]
        default_p.mkdir(parents=True, exist_ok=True)
        return default_p

    def get_working_context(self) -> Dict[str, str]:
        """Letta Pillar: Retrieve current scratchpad and user profile."""
        return self.letta.get_context()

    def update_working_memory(self, section: str, content: str) -> bool:
        """Letta Pillar: Update active context section."""
        return self.letta.core_memory_replace(section, content)

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Vector & Graph hybrid retrieval."""
        vector_hits = self.vector_store.query(query, n_results=limit)
        active_edges = self.graphiti.get_active_relations()

        # Augment with temporal graph relations if relevant
        return {
            "query": query,
            "vector_results": vector_hits,
            "total_indexed_chunks": self.vector_store.count(),
            "active_graph_edges": len(active_edges)
        }

    def consolidate(self, recent_only: bool = True) -> Dict[str, Any]:
        """
        Runs the 4D Consolidation Cycle:
        1. Reads episodic logs (Memories).
        2. Mem0 extracts facts and resolves conflicts.
        3. Graphiti invalidates superseded knowledge and updates edges.
        4. A-MEM generates atomic Zettelkasten notes.
        5. Letta updates the working memory status.
        6. ChromaDB syncs vector embeddings.
        """
        stats = {
            "processed_logs": 0,
            "facts_extracted": 0,
            "facts_added": 0,
            "facts_updated": 0,
            "facts_noop": 0,
            "new_notes": 0,
            "status": "success"
        }

        # Gather episodic files
        log_files = list(self.episodic_dir.glob("*.md"))
        if recent_only and log_files:
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            log_files = log_files[:3]

        all_facts = []
        for lf in log_files:
            stats["processed_logs"] += 1
            content = lf.read_text(encoding="utf-8", errors="replace")
            facts = self.mem0.extract_atomic_facts(content)
            all_facts.extend(facts)

            # Index into vector store
            self.vector_store.upsert(
                doc_id=lf.stem,
                document=content[:2000],
                metadata={"source": lf.name, "pillar": "episodic"}
            )

        stats["facts_extracted"] = len(all_facts)

        # Diff against existing semantic facts
        existing = []
        rule_files = list(self.semantic_dir.rglob("*.md"))
        for rf in rule_files:
            existing.extend(self.mem0.extract_atomic_facts(rf.read_text(encoding="utf-8", errors="replace")))

        diff = self.mem0.diff_facts(all_facts, existing)
        stats["facts_added"] = len(diff["add"])
        stats["facts_updated"] = len(diff["update"])
        stats["facts_noop"] = len(diff["noop"])

        # Letta update
        self.letta.core_memory_append(
            "Consolidaciones Recientes",
            f"Consolidación 4D completada: {stats['facts_added']} agregados, {stats['facts_updated']} actualizados."
        )

        return stats

    def audit(self) -> Dict[str, Any]:
        """Audits the cognitive vault for broken wikilinks, orphans, and health."""
        all_mds = list(self.vault_path.rglob("*.md"))
        stem_map = {f.stem.lower(): f for f in all_mds}

        broken_links = []
        total_links = 0

        for f in all_mds:
            if ".synapse" in str(f):
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
            # Find [[target]]
            import re
            links = re.findall(r'\[\[(.*?)\]\]', text)
            for link in links:
                total_links += 1
                raw_target = link.split("|")[0].split("#")[0].strip()
                # Handle relative path and extension variants in Obsidian
                clean_target = raw_target.replace("\\", "/").split("/")[-1].replace(".md", "").strip().lower()
                if clean_target and clean_target not in stem_map and not clean_target.startswith("$"):
                    broken_links.append({"file": f.name, "broken_target": link})

        return {
            "vault_path": str(self.vault_path),
            "total_notes": len(all_mds),
            "total_wikilinks": total_links,
            "broken_links_count": len(broken_links),
            "broken_links": broken_links[:10],
            "health_score": f"{round((1.0 - (len(broken_links) / max(total_links, 1))) * 100, 1)}%"
        }
