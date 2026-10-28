"""
Idempotent Migration Engine for Synapse 4D (v1.0 JSON -> v2.0 SQLite).
"""

from __future__ import annotations
import json
import time
import shutil
from pathlib import Path
from typing import Dict, Any

from synapse4d.storage.db import SynapseDatabase
from synapse4d.storage.schema import FactRecord


class VaultMigrator:
    """Migrates legacy chronos_lattice.json into SQLite relational schema with automated safety backup."""

    def __init__(self, vault_path: Path | str):
        self.vault_path = Path(vault_path)
        self.db = SynapseDatabase(self.vault_path)
        self.backups_dir = self.vault_path / ".synapse" / "backups"
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    def migrate(self, create_backup: bool = True) -> Dict[str, Any]:
        """Execute non-destructive migration into SQLite."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = None

        # 1. Create safety backup if requested
        if create_backup:
            backup_folder = self.backups_dir / f"backup_migrate_{timestamp}"
            backup_folder.mkdir(parents=True, exist_ok=True)
            for item in self.vault_path.iterdir():
                if item.name.startswith("."):
                    continue
                if item.is_file():
                    shutil.copy2(item, backup_folder / item.name)
            backup_path = str(backup_folder)

        # 2. Check for legacy chronos_lattice.json
        legacy_lattice = self.vault_path / ".synapse" / "chronos_lattice.json"
        if not legacy_lattice.exists():
            legacy_lattice = self.vault_path / "chronos_lattice.json"

        edges_migrated = 0
        facts_migrated = 0
        session_id = f"sess_migrate_{timestamp}"

        if legacy_lattice.exists():
            try:
                data = json.loads(legacy_lattice.read_text(encoding="utf-8"))
                now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                now_epoch = time.time()

                self.db.begin_session(session_id, strategy="legacy_migration")

                # Migrate edges / graph
                graph = data.get("graph", {})
                for source, neighbors in graph.items():
                    for target, weight in neighbors.items():
                        self.db.upsert_edge(
                            source=source,
                            target=target,
                            relation="relacionado_con",
                            weight_delta=float(weight or 1.0),
                            session_id=session_id,
                        )
                        edges_migrated += 1

                # Migrate facts if present in legacy
                for fact_text in data.get("facts", []):
                    f_id = f"f_mig_{time.time_ns()}"
                    fact_rec = FactRecord(
                        id=f_id,
                        entity="migracion",
                        attribute="dato",
                        value=str(fact_text),
                        status="active",
                        confidence=0.8,
                        session_id=session_id,
                        valid_from=now_iso,
                    )
                    self.db.add_fact(fact_rec)
                    facts_migrated += 1

                self.db.commit_session(session_id, facts_extracted=facts_migrated, facts_superseded=0)

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "backup_path": backup_path,
                }

        return {
            "success": True,
            "edges_migrated": edges_migrated,
            "facts_migrated": facts_migrated,
            "session_id": session_id,
            "backup_path": backup_path,
        }
