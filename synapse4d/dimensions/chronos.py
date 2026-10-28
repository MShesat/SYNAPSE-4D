"""
Synapse 4D - Dimension 3: Chronos Lattice (D3)
Bi-temporal knowledge matrix with Hebbian synaptic weighting and automatic state invalidation.
"""

import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

class ChronosLattice:
    """Dimension 3: Governs bi-temporal validity and synaptic plasticity over relational knowledge."""

    def __init__(self, state_dir: Path):
        self.state_dir = Path(state_dir)
        self.lattice_file = self.state_dir / "chronos_lattice.json"
        self.decay_lambda = 0.05  # Temporal decay factor
        self.edges = self._load_lattice()

    def _load_lattice(self) -> List[Dict[str, Any]]:
        if self.lattice_file.exists():
            try:
                return json.loads(self.lattice_file.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    def persist(self):
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.lattice_file.write_text(json.dumps(self.edges, indent=2, ensure_ascii=False), encoding="utf-8")

    def register_relation(self, source: str, relation: str, target: str, context: str = "") -> Dict[str, Any]:
        """
        Binds two entities with bi-temporal timestamps and initial synaptic strength (w=1.0).
        Automatically supersedes contradicting edges for deterministic reality tracking.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        now_ts = time.time()
        superseded_targets = []

        for edge in self.edges:
            if edge["source"].lower() == source.lower() and edge["relation"].lower() == relation.lower() and edge["status"] == "active":
                if edge["target"].lower() != target.lower():
                    edge["status"] = "superseded"
                    edge["invalidated_at"] = now_iso
                    superseded_targets.append(edge["target"])

        new_edge = {
            "source": source,
            "relation": relation,
            "target": target,
            "context": context,
            "status": "active",
            "synaptic_weight": 1.0,
            "access_count": 1,
            "last_accessed": now_ts,
            "created_at": now_iso,
            "valid_at": now_iso,
            "invalidated_at": None
        }
        self.edges.append(new_edge)
        self.persist()

        return {"edge": new_edge, "superseded": superseded_targets}

    def reinforce_synapse(self, source: str, target: str) -> float:
        """Applies Hebbian reinforcement: increases synaptic weight upon successful retrieval."""
        now_ts = time.time()
        for edge in self.edges:
            if edge["source"].lower() == source.lower() and edge["target"].lower() == target.lower():
                # Hebbian potentiation: w = min(w + 0.2, 3.0)
                edge["synaptic_weight"] = round(min(edge["synaptic_weight"] + 0.2, 3.0), 3)
                edge["access_count"] += 1
                edge["last_accessed"] = now_ts
                self.persist()
                return edge["synaptic_weight"]
        return 1.0

    def get_active_lattice(self, apply_decay: bool = False) -> List[Dict[str, Any]]:
        """Returns all currently active relations, optionally calculating temporal decay."""
        active = [e for e in self.edges if e["status"] == "active"]
        now_ts = time.time()

        if apply_decay:
            for e in active:
                elapsed_days = (now_ts - e.get("last_accessed", now_ts)) / 86400.0
                # Exponential decay: w(t) = w_0 * e^(-lambda * dt)
                decayed = e["synaptic_weight"] * math.exp(-self.decay_lambda * elapsed_days)
                e["effective_weight"] = round(max(decayed, 0.1), 3)

        return active

    def export_graph_definition(self) -> str:
        """Exports a clean Mermaid graph representation."""
        lines = ["```mermaid", "graph TD"]
        active = self.get_active_lattice()
        if not active:
            lines.append("    EmptyMatrix[Chronos Matrix Empty]")
        else:
            for e in active[:40]:
                s = e["source"].replace(" ", "_").replace("-", "_")
                t = e["target"].replace(" ", "_").replace("-", "_")
                lines.append(f'    {s} -->|"{e["relation"]} (w:{e.get("synaptic_weight", 1.0)})"| {t}')
        lines.append("```")
        return "\n".join(lines)
