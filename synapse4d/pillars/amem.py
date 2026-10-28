"""
Synapse 4D - Pillar 4: A-MEM (Agentic Memory Zettelkasten & Reciprocal Linking)
Inspired by A-MEM (NeurIPS 2024 / Agentic Memory): Atomic note generation,
dynamic topic clustering, and bidirectional wikilinking ([[Note]]).
"""

import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

class AMEMZettelkasten:
    """Creates atomic, self-contained notes with bidirectional wikilinks."""

    def __init__(self, semantic_dir: Path):
        self.semantic_dir = Path(semantic_dir)
        self.entities_dir = self.semantic_dir / "entidades"
        if not self.entities_dir.exists():
            self.entities_dir = self.semantic_dir / "entities"
        self.entities_dir.mkdir(parents=True, exist_ok=True)

    def generate_atomic_note(self, title: str, summary: str, facts: List[str], related_notes: List[str], tags: List[str]) -> Path:
        """
        Generates an atomic Markdown note adhering to strict YAML frontmatter
        and bidirectional [[Wikilinks]].
        """
        slug = re.sub(r'[^a-zA-Z0-9_\-]+', '-', title.lower()).strip('-')
        note_file = self.entities_dir / f"{slug}.md"

        today = datetime.now().strftime("%Y-%m-%d")
        tags_str = ", ".join(tags) if tags else "synapse, memoria-semantica"

        links_yaml = "\n".join([f"  - \"[[{n}]]\"" for n in related_notes])
        facts_md = "\n".join([f"- {f}" for f in facts])
        links_md = "\n".join([f"- [[{n}]]" for n in related_notes])

        content = f"""---
title: "{title}"
tipo: entidad
fecha: {today}
tags: [{tags_str}]
relaciones:
{links_yaml if related_notes else "  []"}
---

# {title}

## Resumen Ejecutivo
{summary.strip()}

## Hechos Atómicos Consolidados
{facts_md if facts else "- No hay hechos detallados."}

## Conexiones y Enlaces Recíprocos
{links_md if related_notes else "- Sin enlaces directos."}
"""
        note_file.write_text(content, encoding="utf-8")

        # Inject reciprocal links back into related notes
        self._inject_reciprocal_links(slug, related_notes)

        return note_file

    def _inject_reciprocal_links(self, current_slug: str, related_notes: List[str]):
        """Injects [[current_slug]] into related notes so neither becomes an orphan."""
        for target in related_notes:
            target_slug = re.sub(r'[^a-zA-Z0-9_\-]+', '-', target.lower()).strip('-')
            candidate = self.entities_dir / f"{target_slug}.md"
            if candidate.exists():
                text = candidate.read_text(encoding="utf-8", errors="replace")
                link_pattern = f"[[{current_slug}]]"
                if link_pattern not in text:
                    # Append under Conexiones or EOF
                    if "## Conexiones" in text:
                        parts = text.split("## Conexiones")
                        updated = parts[0] + "## Conexiones\n- " + link_pattern + "\n" + parts[1]
                        candidate.write_text(updated, encoding="utf-8")
                    else:
                        candidate.write_text(text + f"\n\n## Conexiones\n- {link_pattern}\n", encoding="utf-8")
