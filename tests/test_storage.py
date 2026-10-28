"""
Unit and Property Tests for SQLite Storage Engine (Synapse 4D v2.0).
"""

import time
import tempfile
import shutil
from pathlib import Path
import pytest
from synapse4d.storage.db import SynapseDatabase, eff_weight_udf
from synapse4d.storage.schema import FactRecord, EdgeRecord


@pytest.fixture
def temp_vault():
    temp_dir = tempfile.mkdtemp(prefix="synapse_test_vault_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_sqlite_initialization(temp_vault):
    db = SynapseDatabase(temp_vault)
    assert db.db_path.exists()
    assert db.lock_path.name == "synapse.lock"
    # Verify filelock can be acquired and released cleanly
    with db._lock:
        assert db.lock_path.exists()


def test_session_lifecycle(temp_vault):
    db = SynapseDatabase(temp_vault)
    sess = db.begin_session("sess_001", strategy="incremental")
    assert sess.status == "pending"

    fetched = db.get_session("sess_001")
    assert fetched is not None
    assert fetched.status == "pending"

    db.commit_session("sess_001", facts_extracted=5, facts_superseded=2, health_score=0.98)
    updated = db.get_session("sess_001")
    assert updated.status == "committed"
    assert updated.facts_extracted == 5
    assert updated.health_score == 0.98


def test_bitemporal_facts_and_supersession(temp_vault):
    db = SynapseDatabase(temp_vault)
    db.begin_session("sess_A")

    fact_1 = FactRecord(
        id="fact_001",
        entity="database",
        attribute="engine",
        value="mysql",
        status="active",
        confidence=0.95,
        session_id="sess_A",
        valid_from="2026-10-01T00:00:00Z",
    )
    db.add_fact(fact_1)
    db.commit_session("sess_A", facts_extracted=1, facts_superseded=0)

    # Verify active facts
    active = db.get_active_facts("database")
    assert len(active) == 1
    assert active[0].value == "mysql"

    # New session supersedes fact_1
    db.begin_session("sess_B")
    fact_2 = FactRecord(
        id="fact_002",
        entity="database",
        attribute="engine",
        value="postgresql",
        status="active",
        confidence=0.99,
        session_id="sess_B",
        valid_from="2026-10-28T00:00:00Z",
    )
    db.add_fact(fact_2)
    db.supersede_fact("fact_001", "fact_002", "sess_B")
    db.commit_session("sess_B", facts_extracted=1, facts_superseded=1)

    # Check that only fact_2 is active now
    active_now = db.get_active_facts("database")
    assert len(active_now) == 1
    assert active_now[0].value == "postgresql"

    # Fact 1 is still in DB with superseded metadata (time-travel proof)
    with db.get_connection() as conn:
        row = conn.execute("SELECT * FROM facts WHERE id = 'fact_001'").fetchone()
        assert row["status"] == "superseded"
        assert row["superseded_by"] == "fact_002"
        assert row["invalidated_at"] == "sess_B"


def test_lazy_decay_udf(temp_vault):
    db = SynapseDatabase(temp_vault)
    now = time.time()
    half_life = 86400.0  # 1 day

    # At t=0, effective weight = base weight
    assert eff_weight_udf(4.0, now, now, half_life) == 4.0

    # At t=1 day later, weight is halved
    assert abs(eff_weight_udf(4.0, now, now + half_life, half_life) - 2.0) < 1e-4

    # Test via SQLite UDF query
    with db.get_connection() as conn:
        row = conn.execute("SELECT eff_weight(10.0, ?, ?, ?) as eff", (now, now + (half_life * 2), half_life)).fetchone()
        # 10.0 halved twice = 2.5
        assert abs(row["eff"] - 2.5) < 1e-4


def test_state_response_contract(temp_vault):
    db = SynapseDatabase(temp_vault)
    summary = db.get_state_summary()
    assert summary.api_version == "2.0"
    assert summary.vault_name == temp_vault.name
    assert summary.health_score == 1.0
    assert summary.broken_bindings == 0
    assert "working_memory" in summary.tiers
