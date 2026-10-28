"""
Synapse 4D - Dimension 4: Associative Mesh (D4 v2.5)
Self-assembling topological hypergraph, reciprocal closure, and zero-orphan auto-healing.
"""

from __future__ import annotations
import os
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple

from synapse4d.storage.db import SynapseDatabase
from synapse4d.storage.schema import EdgeRecord


class AssociativeMesh:
    """Dimension 4: Enforces topological cohesion, reciprocal closure, and zero-orphan guarantees."""

    def __init__(self, vault_path: Path | str, db: Optional[SynapseDatabase] = None):
        self.vault_path = Path(vault_path)
        self.db = db
        self.nodes_dir = self._resolve_nodes_dir()
        self.nodes_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_nodes_dir(self) -> Path:
        for candidate in ["20_Memoria_Semantica/entidades", "20_Semantic_Memory/entities", "nodes"]:
            p = self.vault_path / candidate
            if p.exists():
                return p
        fallback = self.vault_path / "20_Memoria_Semantica" / "entidades"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback

    def enforce_reciprocal_closure(
        self,
        associations: List[Tuple[str, str, str]],  # (source, target, relation)
        session_id: str,
    ) -> List[Tuple[str, str]]:
        """
        Enforce reciprocal closure partial-derivative:
        For every forward edge (A -> B), ensure backward edge (B -> A) exists in SQLite.
        """
        created_edges = []
        if not self.db:
            return created_edges

        for src, tgt, rel in associations:
            s_clean = self._clean_entity(src)
            t_clean = self._clean_entity(tgt)
            if not s_clean or not t_clean or s_clean == t_clean:
                continue

            # Forward edge
            self.db.upsert_edge(
                source=s_clean,
                target=t_clean,
                relation=rel or "relacionado_con",
                weight_delta=0.5,
                session_id=session_id,
            )
            created_edges.append((s_clean, t_clean))

            # Reciprocal backward edge (Theorem 2: No isolated nodes)
            inv_rel = f"reciproco_de_{rel}" if rel and rel != "relacionado_con" else "relacionado_con"
            self.db.upsert_edge(
                source=t_clean,
                target=s_clean,
                relation=inv_rel,
                weight_delta=0.3,
                session_id=session_id,
            )
            created_edges.append((t_clean, s_clean))

        return created_edges

    def ensure_entity_stubs(
        self,
        referenced_entities: Set[str],
        session_id: str,
        source_file: str = "consolidation",
    ) -> List[Path]:
        """
        Guarantee Theorem 2: |V_isolated| = 0.
        If an entity is referenced in edges or facts but has no Markdown note,
        generate a minimal stub note with formal frontmatter and reciprocal backlink.
        """
        created_stubs: List[Path] = []
        today_iso = time.strftime("%Y-%m-%d")

        for entity in referenced_entities:
            slug = self._clean_entity(entity)
            if not slug:
                continue

            # Check if file exists anywhere in vault
            matching = list(self.vault_path.glob(f"**/{slug}.md"))
            if matching:
                continue  # Entity already materialized

            # Generate minimal stub
            stub_path = self.nodes_dir / f"{slug}.md"
            stub_content = f"""---
title: "Stub: {slug.replace('-', ' ').title()}"
type: associative-stub
status: stub
dimension: D4
created: {today_iso}
session_id: {session_id}
tags: [synapse4d, stub, auto-generated]
---

# {slug.replace('-', ' ').title()}

> **Nota Autogenerada (Stub Mínimo D4):** Este nodo fue creado automáticamente para mantener la clausura asociativa del grafo y evitar nodos huérfanos.

## Enlaces Recíprocos
- Origen de detección: [[{source_file}]]
"""
            # Write stub safely
            tmp_path = stub_path.with_suffix(".tmp")
            tmp_path.write_text(stub_content, encoding="utf-8")
            os.replace(tmp_path, stub_path)
            created_stubs.append(stub_path)

            if self.db:
                self.db.record_stub_reference(
                    stub_path=str(stub_path),
                    session_id=session_id,
                    source_file=source_file,
                )

        return created_stubs

    def _clean_entity(self, name: str) -> str:
        clean = re.sub(r"[\[\]#\*\(\)]", "", name).strip().lower()
        return re.sub(r"[^a-z0-9_\-]+", "-", clean).strip("-")
