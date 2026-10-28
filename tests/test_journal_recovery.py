"""
Crash recovery and 2PC Journaling Tests for Synapse 4D.
"""

import tempfile
import shutil
from pathlib import Path
import pytest

from synapse4d.storage.db import SynapseDatabase
from synapse4d.storage.journal import AtomicJournal


@pytest.fixture
def temp_vault():
    temp_dir = tempfile.mkdtemp(prefix="synapse_journal_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_crash_pre_commit_rollback(temp_vault):
    """Simulates a power failure / SIGKILL before SQLite COMMIT: disk must be restored to original."""
    db = SynapseDatabase(temp_vault)
    journal = AtomicJournal(temp_vault, db)

    # 1. Existing original file
    doc_path = temp_vault / "nota_original.md"
    doc_path.write_text("Contenido Original Importante", encoding="utf-8")

    # 2. Begin session but don't commit it (simulating crash)
    db.begin_session("sess_crash_1")
    journal.prepare_write_session("sess_crash_1", [{"path": str(doc_path), "action": "modify"}])

    # 3. Simulate corrupting or modifying file on disk before crash
    doc_path.write_text("Contenido Corrupto o Parcial", encoding="utf-8")
    assert doc_path.read_text(encoding="utf-8") == "Contenido Corrupto o Parcial"

    # 4. Process restarts and calls reconcile_on_startup()
    rec_res = journal.reconcile_on_startup()
    assert rec_res["status"] == "rolled_back_pre_commit"
    assert rec_res["files_restored"] == 1

    # 5. File must have its original content restored!
    assert doc_path.read_text(encoding="utf-8") == "Contenido Original Importante"
    assert not journal.journal_file.exists()


def test_crash_post_commit_reconciliation(temp_vault):
    """Simulates a crash after SQLite COMMIT: state is kept, temp files are cleaned."""
    db = SynapseDatabase(temp_vault)
    journal = AtomicJournal(temp_vault, db)

    doc_path = temp_vault / "nueva_nota.md"
    tmp_path = doc_path.with_suffix(".tmp")
    tmp_path.write_text("Temporal huérfano", encoding="utf-8")

    db.begin_session("sess_post_1")
    journal.prepare_write_session("sess_post_1", [{"path": str(doc_path), "action": "create"}])

    # Commit succeeds in SQLite
    db.commit_session("sess_post_1", facts_extracted=3, facts_superseded=0)

    # Recovery runs
    rec_res = journal.reconcile_on_startup()
    assert rec_res["status"] == "reconciled_committed"
    assert not tmp_path.exists()
    assert not journal.journal_file.exists()
