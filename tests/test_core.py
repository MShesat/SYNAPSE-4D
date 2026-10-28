from pathlib import Path
import tempfile
import shutil

from synapse4d.dimensions.focus import FocusEngine
from synapse4d.dimensions.distiller import FactDistiller
from synapse4d.dimensions.chronos import ChronosLattice
from synapse4d.dimensions.mesh import AssociativeMesh
from synapse4d.storage.db import SynapseDatabase


def test_focus_engine_d1():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        tmp = Path(tmpdir)
        focus = FocusEngine(tmp)
        focus.update_section("Objective", "Synthesize Cognitive State")
        state = focus.get_focus_state()
        assert "Synthesize Cognitive State" in state["active_context"]


def test_fact_distiller_d2():
    distiller = FactDistiller()
    raw = "- Python 3.13 is our primary language\n- regla: Never expose private API keys"
    facts = distiller.distill_atomic_facts(raw)
    assert len(facts) >= 2
    # El hecho que contiene "regla" tiene máxima autoridad epistémica (confianza 1.0, needs_review == 0)
    assert any(f.confidence == 1.0 and f.needs_review == 0 for f in facts)


def test_chronos_lattice_d3():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        tmp = Path(tmpdir)
        lattice = ChronosLattice(tmp)
        lattice.register_relation("Engine", "active_driver", "Markdown")
        res = lattice.register_relation("Engine", "active_driver", "SQLite")
        assert "Markdown" in res["superseded"]

        # Test Hebbian potentiation
        w = lattice.reinforce_synapse("Engine", "SQLite")
        assert w > 1.0


def test_associative_mesh_d4():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        tmp = Path(tmpdir)
        db = SynapseDatabase(tmp)
        mesh = AssociativeMesh(tmp, db=db)

        # 1. Zero-orphan stub generation (Theorem 2: |V_isolated| = 0)
        stubs = mesh.ensure_entity_stubs(
            {"Kernel-Architecture", "Master-Index"},
            session_id="test_sess_01",
            source_file="daily_log",
        )
        assert len(stubs) == 2
        stub_files = list(mesh.nodes_dir.glob("*.md"))
        assert len(stub_files) == 2
        content = stub_files[0].read_text(encoding="utf-8")
        assert "status: stub" in content
        assert "[[daily_log]]" in content

        # 2. Reciprocal closure symmetry
        edges = mesh.enforce_reciprocal_closure(
            [("Kernel-Architecture", "Master-Index", "relacionado_con")],
            session_id="test_sess_01",
        )
        assert ("kernel-architecture", "master-index") in edges
        assert ("master-index", "kernel-architecture") in edges
