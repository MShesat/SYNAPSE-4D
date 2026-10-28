"""
Atomic 2PC Journaling and Crash Recovery Engine for Synapse 4D.

Guarantees data integrity across the dual-boundary (SQLite relational database + Markdown vault files).
Prevents partial writes, corrupted states, and orphaned notes after sudden power loss or process termination.
"""

from __future__ import annotations
import os
import json
import time
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from synapse4d.storage.db import SynapseDatabase


class AtomicJournal:
    """Manages two-phase commit logs and snapshot recovery for file operations."""

    def __init__(self, vault_path: Path | str, db: SynapseDatabase):
        self.vault_path = Path(vault_path)
        self.db = db
        self.synapse_dir = self.vault_path / ".synapse"
        self.synapse_dir.mkdir(parents=True, exist_ok=True)
        self.journal_file = self.synapse_dir / "pending_writes.json"
        self.backups_dir = self.synapse_dir / "backups"
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    def prepare_write_session(self, session_id: str, planned_files: List[Dict[str, str]]) -> Path:
        """
        Step 1: Backup pre-existing target files into pending_<session_id> snapshot directory.
        Step 2: Persist intent log into pending_writes.json.
        """
        session_backup_dir = self.backups_dir / f"pending_{session_id}"
        session_backup_dir.mkdir(parents=True, exist_ok=True)

        journal_entries = []
        for item in planned_files:
            file_path = Path(item["path"])
            action = item.get("action", "modify")  # modify, create, delete

            # If file already exists, create physical backup snapshot
            if file_path.exists():
                relative_name = file_path.name
                shutil.copy2(file_path, session_backup_dir / relative_name)

            journal_entries.append({
                "path": str(file_path),
                "action": action,
                "state": "pending",
                "backup": str(session_backup_dir / file_path.name) if file_path.exists() else None,
            })

        payload = {
            "session_id": session_id,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "entries": journal_entries,
        }

        # Atomic write of journal file
        tmp_journal = self.journal_file.with_suffix(".tmp")
        tmp_journal.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        os.replace(tmp_journal, self.journal_file)

        return session_backup_dir

    def mark_file_renamed(self, file_path: str):
        """Update journal state for a specific file once os.replace() succeeds."""
        if not self.journal_file.exists():
            return
        try:
            data = json.loads(self.journal_file.read_text(encoding="utf-8"))
            for entry in data.get("entries", []):
                if entry["path"] == str(file_path):
                    entry["state"] = "renamed"
            self.journal_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def cleanup_post_commit(self, session_id: str):
        """Called immediately after SQLite COMMIT succeeds. Removes journal and temporary snapshots."""
        if self.journal_file.exists():
            try:
                self.journal_file.unlink(missing_ok=True)
            except Exception:
                pass

        session_backup_dir = self.backups_dir / f"pending_{session_id}"
        if session_backup_dir.exists():
            try:
                shutil.rmtree(session_backup_dir, ignore_errors=True)
            except Exception:
                pass

    def reconcile_on_startup(self) -> Dict[str, Any]:
        """
        Startup Recovery Handler:
        Checks if pending_writes.json exists.
        - If SQLite session status == 'committed': Crash occurred after DB commit. Clean .tmp and remove journal.
        - If SQLite session status == 'pending' or missing: Crash occurred before DB commit. Restore files from backup.
        """
        if not self.journal_file.exists():
            return {"status": "clean", "recovered": False}

        try:
            data = json.loads(self.journal_file.read_text(encoding="utf-8"))
            session_id = data.get("session_id")
            entries = data.get("entries", [])
            
            session = self.db.get_session(session_id) if session_id else None

            if session and session.status == "committed":
                # Crash occurred after DB commit. State is committed; clean orphan .tmp files.
                for item in entries:
                    tmp_p = Path(item["path"]).with_suffix(".tmp")
                    if tmp_p.exists():
                        tmp_p.unlink(missing_ok=True)
                self.cleanup_post_commit(session_id)
                return {"status": "reconciled_committed", "recovered": True, "session_id": session_id}

            else:
                # Crash occurred before DB commit. Rollback disk changes using backup copies.
                restored_count = 0
                for item in entries:
                    target_path = Path(item["path"])
                    backup_path = Path(item["backup"]) if item.get("backup") else None

                    if backup_path and backup_path.exists():
                        shutil.copy2(backup_path, target_path)
                        restored_count += 1
                    elif item.get("action") == "create" and target_path.exists():
                        # File was created before crash, remove it
                        target_path.unlink(missing_ok=True)

                self.cleanup_post_commit(session_id)
                return {"status": "rolled_back_pre_commit", "recovered": True, "files_restored": restored_count}

        except Exception as e:
            return {"status": "recovery_error", "error": str(e)}
