"""
Synapse 4D - Dimension 1: Focus Engine (D1)
Dynamic working memory buffer, active scratchpad management, and strict context budgeting.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import time

class FocusEngine:
    """Dimension 1: Manages volatile, high-frequency working state for autonomous agents."""

    def __init__(self, storage_root: Path):
        self.storage_root = Path(storage_root)
        # Supports standard localized or universal folder patterns
        self.focus_dir = self._resolve_dir(["00_Working_Memory", "00_Memoria_de_Trabajo", "focus"])
        self.context_file = self._resolve_file(self.focus_dir, ["active_context.md", "contexto-activo.md"])
        self.profile_file = self._resolve_file(self.focus_dir, ["system_profile.md", "perfil-y-sistema.md"])

    def _resolve_dir(self, candidates: List[str]) -> Path:
        for c in candidates:
            p = self.storage_root / c
            if p.exists():
                return p
        default_dir = self.storage_root / candidates[0]
        default_dir.mkdir(parents=True, exist_ok=True)
        return default_dir

    def _resolve_file(self, parent: Path, filenames: List[str]) -> Path:
        for fname in filenames:
            p = parent / fname
            if p.exists():
                return p
        return parent / filenames[0]

    def get_focus_state(self) -> Dict[str, Any]:
        """Retrieves active attention state and profile configuration."""
        context = ""
        profile = ""
        if self.context_file.exists():
            context = self.context_file.read_text(encoding="utf-8", errors="replace")
        if self.profile_file.exists():
            profile = self.profile_file.read_text(encoding="utf-8", errors="replace")

        return {
            "active_context": context,
            "system_profile": profile,
            "char_count": len(context) + len(profile),
            "timestamp": time.time()
        }

    def update_section(self, section: str, new_content: str) -> bool:
        """Deterministically replaces or registers a focus section in the active working memory."""
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
            suffix = rest[next_header_idx:] if next_header_idx != -1 else ""
            updated = f"{prefix}{header}\n{new_content.strip()}\n{suffix}"
        else:
            updated = f"{text.strip()}\n\n{header}\n{new_content.strip()}\n"

        self.context_file.write_text(updated, encoding="utf-8")
        return True

    def append_observation(self, section: str, observation: str) -> bool:
        """Appends a new discrete observation to a specific section."""
        if not self.context_file.exists():
            return self.update_section(section, f"- {observation}")

        text = self.context_file.read_text(encoding="utf-8", errors="replace")
        header = f"## {section}"
        if header not in text:
            return self.update_section(section, f"- {observation}")

        lines = text.splitlines()
        output = []
        inserted = False
        in_section = False

        for line in lines:
            if line.strip() == header:
                in_section = True
                output.append(line)
                continue
            if in_section and line.startswith("## "):
                output.append(f"- {observation}")
                inserted = True
                in_section = False
            output.append(line)

        if in_section and not inserted:
            output.append(f"- {observation}")

        self.context_file.write_text("\n".join(output) + "\n", encoding="utf-8")
        return True
