"""
Synapse 4D - Dimension 4: Associative Mesh (D4)
Self-assembling topological hypergraph, atomic Zettelkasten synthesis, and zero-orphan auto-healing.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class AssociativeMesh:
    """Dimension 4: Enforces topological cohesion and bidirectional links across knowledge nodes."""

    def __init__(self, semantic_root: Path):
        self.semantic_root = Path(semantic_root)
        self.nodes_dir = self._resolve_nodes_dir()
        self.nodes_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_nodes_dir(self) -> Path:
        for candidate in ["entidades", "entities", "nodes"]:
            p = self.semantic_root / candidate
            if p.exists():
                return p
        return self.semantic_root / "nodes"

    def synthesize_node(self, title: str, summary: str, facts: List[str], associations: List[str], tags: List[str]) -> Path:
        """
        Synthesizes an atomic node with guaranteed reciprocal bidirectional links.
        Prevents graph fragmentation and orphan nodes.
        """
        slug = re.sub(r'[^a-zA-Z0-9_\-]+', '-', title.lower()).strip('-')
        node_path = self.nodes_dir / f"{slug}.md"
        today = datetime.now().strftime("%Y-%m-%d")

        tags_repr = ", ".join(tags) if tags else "synapse4d, associative-mesh"
        yaml_links = "\n".join([f"  - \"[[{a}]]\"" for a in associations]) if associations else "  []"
        facts_body = "\n".join([f"- {f}" for f in facts]) if facts else "- No atomic facts recorded."
        links_body = "\n".join([f"- [[{a}]]" for a in associations]) if associations else "- Isolated apex node."

        document = f"""---
title: "{title}"
type: associative-node
dimension: D4
created: {today}
tags: [{tags_repr}]
associations:
{yaml_links}
---

# {title}

## Summary
{summary.strip()}

## Consolidated Atomic Facts
{facts_body}

## Reciprocal Associations
{links_body}
"""
        node_path.write_text(document, encoding="utf-8")
        self._heal_reciprocal_bindings(slug, associations)
        return node_path

    def _heal_reciprocal_bindings(self, origin_slug: str, target_nodes: List[str]):
        """Injects reciprocal links into referenced nodes so graph entropy remains zero."""
        for target in target_nodes:
            target_slug = re.sub(r'[^a-zA-Z0-9_\-]+', '-', target.lower()).strip('-')
            candidate = self.nodes_dir / f"{target_slug}.md"
            if candidate.exists():
                content = candidate.read_text(encoding="utf-8", errors="replace")
                binding = f"[[{origin_slug}]]"
                if binding not in content:
                    if "## Reciprocal Associations" in content:
                        parts = content.split("## Reciprocal Associations")
                        updated = parts[0] + "## Reciprocal Associations\n- " + binding + "\n" + parts[1]
                        candidate.write_text(updated, encoding="utf-8")
                    elif "## Conexiones" in content:
                        parts = content.split("## Conexiones")
                        updated = parts[0] + "## Conexiones\n- " + binding + "\n" + parts[1]
                        candidate.write_text(updated, encoding="utf-8")
                    else:
                        candidate.write_text(content.strip() + f"\n\n## Reciprocal Associations\n- {binding}\n", encoding="utf-8")
