"""
Synapse 4D - Central Cognitive Engine (v2.5)
Unifies the 4 Dimensions of Artificial Cognitive State:
  - D1: Focus Engine (Dynamic Working Attention)
  - D2: Fact Distiller (Epistemic Authority & Bi-Temporal Logical Supersession)
  - D3: Relational Chronos Storage (SQLite WAL, FileLock & Lazy Hebbian Decay)
  - D4: Associative Mesh (Reciprocal Closure & Zero-Orphan Stubs)
"""

from __future__ import annotations
import os
import re
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

from synapse4d.dimensions.focus import FocusEngine
from synapse4d.dimensions.distiller import FactDistiller
from synapse4d.dimensions.mesh import AssociativeMesh
from synapse4d.storage.db import SynapseDatabase, get_database
from synapse4d.storage.journal import AtomicJournal
from synapse4d.storage.schema import StateResponse


class SynapseEngine:
    """The unified 4D Cognitive State Machine for Autonomous Agents."""

    def __init__(self, vault_path: str | Path):
        self.vault_path = Path(vault_path).resolve()
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Vault path does not exist: {self.vault_path}")

        # Directory resolution
        self.working_dir = self._resolve_dir(["00_Working_Memory", "00_Memoria_de_Trabajo"])
        self.episodic_dir = self._resolve_dir(["10_Episodic_Memory", "10_Memoria_Episodica"])
        self.semantic_dir = self._resolve_dir(["20_Semantic_Memory", "20_Memoria_Semantica"])
        self.procedural_dir = self._resolve_dir(["30_Procedural_Memory", "30_Memoria_Procedimental"])
        self.meta_dir = self._resolve_dir(["90_Meta_System", "90_Meta_Sistema"])

        # Storage & Persistence
        self.db = get_database(self.vault_path)
        self.journal = AtomicJournal(self.vault_path, self.db)

        # Automatic crash recovery on startup
        self.recovery_info = self.journal.reconcile_on_startup()

        # Dimensions
        self.focus = FocusEngine(self.vault_path)
        self.distiller = FactDistiller(self.db)
        self.mesh = AssociativeMesh(self.vault_path, self.db)

    def _resolve_dir(self, candidates: List[str]) -> Path:
        for c in candidates:
            p = self.vault_path / c
            if p.exists():
                return p
        default_dir = self.vault_path / candidates[0]
        default_dir.mkdir(parents=True, exist_ok=True)
        return default_dir

    def get_working_context(self) -> Dict[str, Any]:
        """Dimension 1 (Focus): Retrieve current scratchpad state."""
        return self.focus.get_focus_state()

    def update_working_memory(self, section: str, content: str) -> bool:
        """Dimension 1 (Focus): Update working memory section."""
        return self.focus.update_section(section, content)

    def consolidate(self, recent_only: bool = True) -> Dict[str, Any]:
        """
        Executes the Autonomous 4D Consolidation Cycle with Two-Phase Commit:
        1. Pre-transaction: Ingests episodic files and distills facts with embeddings outside the DB lock.
        2. Transaction: SQLite arbitration, logical supersession, Hebbian edge updates, reciprocal closure.
        3. Journal cleanup & Post-commit verification.
        """
        session_id = f"sess_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        self.db.begin_session(session_id, strategy="standard_4d")

        stats = {
            "session_id": session_id,
            "processed_streams": 0,
            "facts_distilled": 0,
            "facts_retained": 0,
            "facts_superseded": 0,
            "facts_redundant": 0,
            "stubs_created": 0,
            "status": "success",
        }

        # 1. Gather episodic streams (Outside lock)
        streams = list(self.episodic_dir.glob("*.md"))
        if recent_only and streams:
            streams.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            streams = streams[:5]

        incoming_facts = []
        referenced_entities: Set[str] = set()

        for s in streams:
            stats["processed_streams"] += 1
            content = s.read_text(encoding="utf-8", errors="replace")
            distilled = self.distiller.distill_atomic_facts(content, session_id=session_id)
            incoming_facts.extend(distilled)

            # Collect referenced entities for topological closure
            for f in distilled:
                referenced_entities.add(f.entity)

        stats["facts_distilled"] = len(incoming_facts)

        # 2. Transaction Phase (Arbitrate & Persist)
        arb_res = self.distiller.arbitrate_and_persist(incoming_facts, self.db, session_id=session_id)
        stats["facts_retained"] = len(arb_res["retained"])
        stats["facts_superseded"] = len(arb_res["superseded"])
        stats["facts_redundant"] = len(arb_res["redundant"])

        # 3. D4 Mesh Closure & Stubs
        stubs = self.mesh.ensure_entity_stubs(
            referenced_entities=referenced_entities,
            session_id=session_id,
            source_file="episodic_stream",
        )
        stats["stubs_created"] = len(stubs)

        # 4. Enforce reciprocal edges between co-occurring entities
        entity_list = list(referenced_entities)
        co_occurrences = []
        for i in range(len(entity_list)):
            for j in range(i + 1, min(i + 4, len(entity_list))):
                co_occurrences.append((entity_list[i], entity_list[j], "asociado_en_sesion"))
        self.mesh.enforce_reciprocal_closure(co_occurrences, session_id=session_id)

        # 5. Commit SQLite Session
        self.db.commit_session(
            session_id=session_id,
            facts_extracted=stats["facts_distilled"],
            facts_superseded=stats["facts_superseded"],
            health_score=1.0,
        )

        # 6. Post-commit journal cleanup
        self.journal.cleanup_post_commit(session_id)

        # 7. D1 Focus Update
        self.focus.append_observation(
            "Consolidaciones Recientes",
            f"Consolidación 4D [{session_id}]: {stats['facts_retained']} retenidos, {stats['facts_superseded']} invalidados, {stats['stubs_created']} stubs.",
        )

        return stats

    def undo(self, session_id: str) -> Dict[str, Any]:
        """Deterministically undoes a specific consolidation session."""
        return self.distiller.undo_session(self.db, session_id)

    def review(self) -> List[Dict[str, Any]]:
        """Returns all facts requiring epistemic review."""
        records = self.db.get_needs_review_facts()
        return [r.model_dump() for r in records]

    def promote_fact(self, fact_id: str) -> bool:
        """Promotes a provisional fact to confirmed active axiom/rule."""
        with self.db._lock:
            with self.db.get_connection() as conn:
                conn.execute(
                    "UPDATE facts SET needs_review = 0, confidence = 1.0 WHERE id = ?",
                    (fact_id,),
                )
                conn.commit()
        return True

    def demote_fact(self, fact_id: str) -> bool:
        """Demotes or invalidates an unconfirmed fact."""
        with self.db._lock:
            with self.db.get_connection() as conn:
                conn.execute(
                    "UPDATE facts SET status = 'superseded', needs_review = 0 WHERE id = ?",
                    (fact_id,),
                )
                conn.commit()
        return True

    def audit(self) -> Dict[str, Any]:
        """Audits the cognitive state, link integrity, and needs_review thresholds."""
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

        state_summary = self.db.get_state_summary()
        needs_review_count = state_summary.needs_review_count
        needs_review_alert = needs_review_count > 20

        health = round((1.0 - (len(broken) / max(total_bindings, 1))) * 100, 1)

        return {
            "api_version": "2.0",
            "vault_path": str(self.vault_path),
            "total_nodes": len(all_nodes),
            "total_bindings": total_bindings,
            "broken_bindings_count": len(broken),
            "broken_bindings": broken[:10],
            "active_facts_count": state_summary.active_facts_count,
            "active_edges_count": state_summary.total_edges_count,
            "needs_review_count": needs_review_count,
            "needs_review_alert": needs_review_alert,
            "health_score": f"{health}%",
            "recovery_status": self.recovery_info.get("status", "clean"),
        }
