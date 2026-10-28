"""
Synapse 4D - Pillar 3: Graphiti (Bi-temporal Knowledge Graph & Edge Invalidation)
Inspired by Zep Graphiti: Temporal validity tracking, edge superseding,
and relational entity mapping.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

class GraphitiTemporalGraph:
    """Manages bi-temporal edges between entities with automated invalidation."""

    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path)
        self.edges_file = self.storage_path / "temporal_graph.json"
        self.edges = self._load_edges()

    def _load_edges(self) -> List[Dict[str, Any]]:
        if self.edges_file.exists():
            try:
                return json.loads(self.edges_file.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    def save(self):
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.edges_file.write_text(json.dumps(self.edges, indent=2, ensure_ascii=False), encoding="utf-8")

    def add_or_update_relation(self, source: str, relation: str, target: str, context: str = "") -> Dict[str, Any]:
        """
        Adds a new relation or supersedes existing conflicting edges.
        Bi-temporal attributes: created_at, valid_at, invalidated_at.
        """
        now = datetime.now(timezone.utc).isoformat()
        superseded = []

        # Find existing edges with same source and relation
        for edge in self.edges:
            if edge["source"].lower() == source.lower() and edge["relation"].lower() == relation.lower() and edge["status"] == "active":
                if edge["target"].lower() != target.lower():
                    # Conflict! Invalidate the old edge
                    edge["status"] = "superseded"
                    edge["invalidated_at"] = now
                    superseded.append(edge["target"])

        new_edge = {
            "source": source,
            "relation": relation,
            "target": target,
            "context": context,
            "status": "active",
            "created_at": now,
            "valid_at": now,
            "invalidated_at": None
        }
        self.edges.append(new_edge)
        self.save()

        return {"new_edge": new_edge, "superseded": superseded}

    def get_active_relations(self, entity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns all currently valid, active relations."""
        active = [e for e in self.edges if e["status"] == "active"]
        if entity:
            ent_l = entity.lower()
            return [e for e in active if e["source"].lower() == ent_l or e["target"].lower() == ent_l]
        return active

    def to_mermaid(self) -> str:
        """Generates a Mermaid graph representation of active edges."""
        lines = ["```mermaid", "graph TD"]
        active = self.get_active_relations()
        if not active:
            lines.append("    EmptyGraph[No active edges]")
        else:
            for e in active[:30]:  # Cap for clarity
                s = e["source"].replace(" ", "_").replace("-", "_")
                t = e["target"].replace(" ", "_").replace("-", "_")
                rel = e["relation"]
                lines.append(f'    {s} -->|"{rel}"| {t}')
        lines.append("```")
        return "\n".join(lines)
