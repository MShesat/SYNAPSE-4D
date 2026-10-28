"""
End-to-End Integration Tests for Synapse 4D CLI & Full Engine Cycle.
"""

import tempfile
import shutil
from pathlib import Path
import pytest
from synapse4d.core import SynapseEngine


@pytest.fixture
def temp_vault():
    temp_dir = tempfile.mkdtemp(prefix="synapse_e2e_")
    vault = Path(temp_dir)
    
    # Setup CoALA standard vault directories
    (vault / "00_Working_Memory").mkdir(parents=True)
    (vault / "10_Episodic_Memory").mkdir(parents=True)
    (vault / "20_Semantic_Memory" / "entidades").mkdir(parents=True)
    (vault / "30_Procedural_Memory").mkdir(parents=True)
    (vault / "90_Meta_System").mkdir(parents=True)

    # Create dummy episodic log
    episodic_log = vault / "10_Episodic_Memory" / "2026-10-28-sesion-desarrollo.md"
    episodic_log.write_text(
        """# Bitácora de Sesión
- Regla: usar SQLite WAL para persistencia relacional
- Preferencia: preferir fastembed en local antes que apis externas
- Observación: whisper procesa audio en modo music sin cortes
""",
        encoding="utf-8",
    )

    yield vault
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_full_consolidation_cycle(temp_vault):
    engine = SynapseEngine(temp_vault)

    # 1. Consolidate
    res = engine.consolidate()
    assert res["status"] == "success"
    assert res["processed_streams"] == 1
    assert res["facts_distilled"] >= 3
    assert res["facts_retained"] >= 3

    # 2. Audit
    report = engine.audit()
    assert report["active_facts_count"] >= 3
    assert report["recovery_status"] == "clean"

    # 3. Review
    pending = engine.review()
    assert len(pending) >= 1

    # 4. Promote
    first_id = pending[0]["id"]
    engine.promote_fact(first_id)
    pending_after = engine.review()
    assert len(pending_after) == len(pending) - 1

    # 5. Undo Session
    undo_res = engine.undo(res["session_id"])
    assert undo_res["facts_rolled_back"] >= 1
