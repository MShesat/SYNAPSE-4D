from pathlib import Path
import tempfile
import shutil

from synapse4d.dimensions.focus import FocusEngine
from synapse4d.dimensions.distiller import FactDistiller
from synapse4d.dimensions.chronos import ChronosLattice
from synapse4d.dimensions.mesh import AssociativeMesh

def test_focus_engine_d1():
    with tempfile.TemporaryDirectory() as tmpdir:
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
    assert any(f["authority"] == "axiom" for f in facts)

def test_chronos_lattice_d3():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        lattice = ChronosLattice(tmp)
        lattice.register_relation("Engine", "active_driver", "Markdown")
        res = lattice.register_relation("Engine", "active_driver", "SQLite")
        assert "Markdown" in res["superseded"]
        
        # Test Hebbian potentiation
        w = lattice.reinforce_synapse("Engine", "SQLite")
        assert w > 1.0

def test_associative_mesh_d4():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        mesh = AssociativeMesh(tmp)
        node = mesh.synthesize_node(
            title="Kernel Architecture",
            summary="Autonomous state engine",
            facts=["Runs local-first", "Zero dependencies"],
            associations=["Master-Index"],
            tags=["core", "engine"]
        )
        assert node.exists()
        content = node.read_text(encoding="utf-8")
        assert "[[Master-Index]]" in content
