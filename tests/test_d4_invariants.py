"""
Property-based and Invariant Tests for D4 Associative Mesh (Theorem 2 Validation).
"""

import tempfile
import shutil
from pathlib import Path
import pytest
from hypothesis import given, strategies as st, settings

from synapse4d.storage.db import SynapseDatabase
from synapse4d.dimensions.mesh import AssociativeMesh


@pytest.fixture
def temp_vault():
    temp_dir = tempfile.mkdtemp(prefix="synapse_d4_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_reciprocal_closure_symmetry(temp_vault):
    """Every edge (A -> B) must automatically produce a reciprocal (B -> A) edge."""
    db = SynapseDatabase(temp_vault)
    mesh = AssociativeMesh(temp_vault, db)

    edges_input = [
        ("postgresql", "docker", "desplegado_en"),
        ("fastapi", "python", "escrito_en"),
    ]

    mesh.enforce_reciprocal_closure(edges_input, session_id="sess_edges_001")

    active_edges = db.get_active_edges()
    edge_pairs = {(e.source_entity, e.target_entity) for e in active_edges}

    # Verify both forward and backward edges exist
    assert ("postgresql", "docker") in edge_pairs
    assert ("docker", "postgresql") in edge_pairs
    assert ("fastapi", "python") in edge_pairs
    assert ("python", "fastapi") in edge_pairs


def test_zero_orphan_stub_generation(temp_vault):
    """Theorem 2: Referenced entities without files must receive minimal stubs."""
    db = SynapseDatabase(temp_vault)
    mesh = AssociativeMesh(temp_vault, db)

    # Reference entities that don't exist on disk yet
    entities = {"chromadb", "sqlite-wal", "whisper-audio"}
    stubs = mesh.ensure_entity_stubs(entities, session_id="sess_stubs_001", source_file="benchmark_run")

    assert len(stubs) == 3
    for s in stubs:
        assert s.exists()
        content = s.read_text(encoding="utf-8")
        assert "status: stub" in content
        assert "dimension: D4" in content

    # Verify recorded in DB
    recorded = db.get_stubs_by_session("sess_stubs_001")
    assert len(recorded) == 3


@settings(max_examples=30, deadline=None)
@given(
    entity_a=st.text(min_size=3, max_size=15, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'))),
    entity_b=st.text(min_size=3, max_size=15, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'))),
)
def test_theorem_2_connectivity_invariant(entity_a, entity_b):
    """Theorem 2 Invariant: In-degree and Out-degree are always > 0 for all connected nodes."""
    if entity_a == entity_b or not entity_a or not entity_b:
        return

    temp_dir = tempfile.mkdtemp(prefix="synapse_t2_")
    vault = Path(temp_dir)
    try:
        db = SynapseDatabase(vault)
        mesh = AssociativeMesh(vault, db)

        mesh.enforce_reciprocal_closure([(entity_a, entity_b, "conecta_con")], session_id="sess_hyp")
        edges = db.get_active_edges()

        sources = {e.source_entity for e in edges}
        targets = {e.target_entity for e in edges}

        clean_a = mesh._clean_entity(entity_a)
        clean_b = mesh._clean_entity(entity_b)

        if not clean_a or not clean_b or clean_a == clean_b:
            return

        assert clean_a in sources and clean_a in targets
        assert clean_b in sources and clean_b in targets
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
