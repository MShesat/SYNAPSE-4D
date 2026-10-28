"""
Property-based and Invariant Tests for D2 Distiller (Theorem 1 Validation).
"""

import tempfile
import shutil
from pathlib import Path
import pytest
from hypothesis import given, strategies as st, settings

from synapse4d.storage.db import SynapseDatabase
from synapse4d.dimensions.distiller import FactDistiller
from synapse4d.storage.schema import FactRecord


@pytest.fixture
def temp_vault():
    temp_dir = tempfile.mkdtemp(prefix="synapse_d2_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_axiom_protection_policy(temp_vault):
    """Provisional facts with needs_review=1 must NEVER supersede established axioms."""
    db = SynapseDatabase(temp_vault)
    distiller = FactDistiller(db)

    db.begin_session("sess_axiom")
    axiom = FactRecord(
        id="f_axiom_001",
        entity="seguridad",
        attribute="directriz",
        value="prohibido acceso root sin autenticacion mfa",
        status="active",
        confidence=1.0,
        session_id="sess_axiom",
        valid_from="2026-10-01T00:00:00Z",
        needs_review=0,
    )
    db.add_fact(axiom)
    db.commit_session("sess_axiom", facts_extracted=1, facts_superseded=0)

    # Incoming provisional fact attempting to allow root access
    db.begin_session("sess_provisional")
    provisional = FactRecord(
        id="f_prov_002",
        entity="seguridad",
        attribute="directriz",
        value="permitir acceso root sin autenticacion mfa",
        status="active",
        confidence=0.5,
        session_id="sess_provisional",
        valid_from="2026-10-28T00:00:00Z",
        needs_review=1,
    )

    arb_res = distiller.arbitrate_and_persist([provisional], db, "sess_provisional")
    db.commit_session("sess_provisional", facts_extracted=1, facts_superseded=0)

    # Verify axiom was NOT superseded
    active = db.get_active_facts("seguridad")
    assert len(active) == 1
    assert active[0].id == "f_axiom_001"
    assert "Rejected" in arb_res["redundant"][0]["reason"]


def test_undo_session_deterministic_restoration(temp_vault):
    """Undoing a session must safely reactivate superseded facts and rollback newly inserted facts."""
    db = SynapseDatabase(temp_vault)
    distiller = FactDistiller(db)

    # Initial session
    db.begin_session("sess_1")
    fact_v1 = FactRecord(
        id="f_1",
        entity="storage_engine",
        attribute="directriz",
        value="usar sqlite para almacenamiento",
        status="active",
        confidence=0.8,
        session_id="sess_1",
        valid_from="2026-10-01T00:00:00Z",
    )
    db.add_fact(fact_v1)
    db.commit_session("sess_1", 1, 0)

    # Second session superseding fact_v1
    db.begin_session("sess_2")
    fact_v2 = FactRecord(
        id="f_2",
        entity="storage_engine",
        attribute="directriz",
        value="evitar sqlite y usar postgresql",
        status="active",
        confidence=0.9,
        session_id="sess_2",
        valid_from="2026-10-28T00:00:00Z",
    )
    distiller.arbitrate_and_persist([fact_v2], db, "sess_2")
    db.commit_session("sess_2", 1, 1)

    # Check fact_v2 is active, fact_v1 is superseded
    assert db.get_active_facts("storage_engine")[0].id == "f_2"

    # Now execute UNDO on sess_2
    undo_res = distiller.undo_session(db, "sess_2")
    assert undo_res["facts_restored"] == 1

    # Fact_v1 must be active again!
    restored_active = db.get_active_facts("storage_engine")
    assert len(restored_active) == 1
    assert restored_active[0].id == "f_1"
    assert restored_active[0].status == "active"


@settings(max_examples=25, deadline=None)
@given(
    values=st.lists(
        st.text(min_size=5, max_size=25, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        min_size=2,
        max_size=6,
    )
)
def test_theorem_1_physical_deletion_invariant(values):
    """Theorem 1 Invariant: Total rows in 'facts' table never decreases (monotonic growth)."""
    temp_dir = tempfile.mkdtemp(prefix="synapse_t1_")
    vault = Path(temp_dir)
    try:
        db = SynapseDatabase(vault)
        distiller = FactDistiller(db)

        prev_count = 0
        for i, val in enumerate(values):
            sess_id = f"sess_hyp_{i}"
            db.begin_session(sess_id)
            rec = FactRecord(
                id=f"fact_{i}",
                entity="benchmark_entity",
                attribute="property",
                value=val,
                status="active",
                confidence=0.8,
                session_id=sess_id,
                valid_from="2026-10-28T00:00:00Z",
            )
            distiller.arbitrate_and_persist([rec], db, sess_id)
            db.commit_session(sess_id, 1, 0)

            with db.get_connection() as conn:
                cur_count = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
                # Total count must be monotonically non-decreasing
                assert cur_count >= prev_count
                prev_count = cur_count
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
