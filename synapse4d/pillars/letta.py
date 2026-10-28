"""
Synapse 4D - Pillar 1: Letta (Working Memory Manager)
Inspired by MemGPT / Letta architecture: Self-editing working memory,
scratchpad context buffer, and strict token budget enforcement.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

class LettaWorkingMemory:
    """Manages volatile, active working memory buffers for LLM decision cycles."""

    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path)
        # Check both Spanish and English standard folders
        wm_es = self.vault_path / "00_Memoria_de_Trabajo"
        wm_en = self.vault_path / "00_Working_Memory"
        self.wm_dir = wm_es if wm_es.exists() else wm_en
        self.wm_dir.mkdir(parents=True, exist_ok=True)

        self.context_file = self._find_file(["contexto-activo.md", "active_context.md"])
        self.profile_file = self._find_file(["perfil-y-sistema.md", "system_profile.md"])

    def _find_file(self, filenames: list[str]) -> Path:
        for fname in filenames:
            p = self.wm_dir / fname
            if p.exists():
                return p
        # Default to first
        return self.wm_dir / filenames[0]

    def get_context(self) -> Dict[str, str]:
        """Returns the current working memory content."""
        context = ""
        profile = ""
        if self.context_file.exists():
            context = self.context_file.read_text(encoding="utf-8", errors="replace")
        if self.profile_file.exists():
            profile = self.profile_file.read_text(encoding="utf-8", errors="replace")
        return {
            "active_context": context,
            "system_profile": profile,
            "total_chars": len(context) + len(profile)
        }

    def core_memory_replace(self, section: str, new_content: str) -> bool:
        """Replaces a targeted section in active context (MemGPT core_memory_replace pattern)."""
        if not self.context_file.exists():
            self.context_file.write_text(f"## {section}\n{new_content}\n", encoding="utf-8")
            return True

        text = self.context_file.read_text(encoding="utf-8", errors="replace")
        header = f"## {section}"
        if header in text:
            parts = text.split(header)
            prefix = parts[0]
            rest = parts[1]
            next_header_idx = rest.find("\n## ")
            if next_header_idx != -1:
                suffix = rest[next_header_idx:]
            else:
                suffix = ""
            updated = f"{prefix}{header}\n{new_content.strip()}\n{suffix}"
        else:
            updated = f"{text.strip()}\n\n{header}\n{new_content.strip()}\n"

        self.context_file.write_text(updated, encoding="utf-8")
        return True

    def core_memory_append(self, section: str, line: str) -> bool:
        """Appends a line or observation to a specific section."""
        if not self.context_file.exists():
            return self.core_memory_replace(section, f"- {line}")

        text = self.context_file.read_text(encoding="utf-8", errors="replace")
        header = f"## {section}"
        if header not in text:
            return self.core_memory_replace(section, f"- {line}")

        lines = text.splitlines()
        output = []
        inserted = False
        in_section = False

        for i, l in enumerate(lines):
            if l.strip() == header:
                in_section = True
                output.append(l)
                continue
            if in_section and l.startswith("## "):
                # End of target section, insert before next header
                output.append(f"- {line}")
                inserted = True
                in_section = False
            output.append(l)

        if in_section and not inserted:
            output.append(f"- {line}")

        self.context_file.write_text("\n".join(output) + "\n", encoding="utf-8")
        return True
