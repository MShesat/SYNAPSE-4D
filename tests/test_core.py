from pathlib import Path
import tempfile
import shutil

from synapse4d.pillars.letta import LettaWorkingMemory
from synapse4d.pillars.mem0 import Mem0FactExtractor
from synapse4d.pillars.graphiti import GraphitiTemporalGraph
from synapse4d.pillars.amem import AMEMZettelkasten

def test_letta_memory():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        letta = LettaWorkingMemory(tmp)
        letta.core_memory_replace("TestSection", "Initial Content")
        ctx = letta.get_context()
        assert "Initial Content" in ctx["active_context"]

def test_mem0_fact_diffing():
    extractor = Mem0FactExtractor()
    facts = ["Python 3.12 is the primary language", "Use ChromaDB for vectors"]
    existing = ["Python 3.10 is the primary language"]
    diff = extractor.diff_facts(facts, existing)
    assert len(diff["update"]) > 0 or len(diff["add"]) > 0

def test_graphiti_temporal_invalidation():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        graph = GraphitiTemporalGraph(tmp)
        graph.add_or_update_relation("Agent", "uses_model", "GPT-3.5")
        res = graph.add_or_update_relation("Agent", "uses_model", "Claude-3.5-Sonnet")
        assert "GPT-3.5" in res["superseded"]

def test_amem_reciprocal_linking():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        amem = AMEMZettelkasten(tmp)
        note = amem.generate_atomic_note(
            title="FastAPI Microservice",
            summary="A high performance web service",
            facts=["Runs on uvicorn", "Asynchronous endpoints"],
            related_notes=["Backend-Architecture"],
            tags=["api", "web"]
        )
        assert note.exists()
        content = note.read_text(encoding="utf-8")
        assert "[[Backend-Architecture]]" in content
