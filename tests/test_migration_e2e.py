"""
Gatekeeper G9: End-to-End Migration Test from Legacy v1.0 Vault to SQLite v2.0.
Verifies zero data loss, automated safety backup, and idempotency.
"""

import json
import tempfile
from pathlib import Path
from synapse4d.storage.migration import VaultMigrator
from synapse4d.storage.db import SynapseDatabase


def test_legacy_vault_migration_zero_data_loss():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        vault = Path(tmpdir)

        # 1. Crear un vault simulado v1.0 con chronos_lattice.json y notas
        synapse_dir = vault / ".synapse"
        synapse_dir.mkdir(parents=True, exist_ok=True)

        legacy_data = {
            "graph": {
                "AlphaNode": {"BetaNode": 2.5, "GammaNode": 1.2},
                "BetaNode": {"AlphaNode": 1.8},
                "GammaNode": {"DeltaNode": 3.0}
            },
            "facts": [
                "Legacy rule: Always verify before completion",
                "Arch: SQLite WAL is local first"
            ]
        }
        lattice_file = synapse_dir / "chronos_lattice.json"
        lattice_file.write_text(json.dumps(legacy_data), encoding="utf-8")

        # Crear notas en el vault
        (vault / "AlphaNode.md").write_text("# Alpha Node\nContent here", encoding="utf-8")
        (vault / "BetaNode.md").write_text("# Beta Node\nContent here", encoding="utf-8")

        # 2. Ejecutar VaultMigrator
        migrator = VaultMigrator(vault)
        result = migrator.migrate(create_backup=True)

        assert result["success"] is True
        assert result["edges_migrated"] == 4
        assert result["facts_migrated"] == 2
        assert result["backup_path"] is not None

        # 3. Verificar en SQLite directamente
        db = SynapseDatabase(vault)
        active_edges = db.get_active_edges()
        assert len(active_edges) == 4

        edge_map = {(e.source_entity, e.target_entity): e.base_weight for e in active_edges}
        assert ("AlphaNode", "BetaNode") in edge_map
        assert ("BetaNode", "AlphaNode") in edge_map
        assert ("AlphaNode", "GammaNode") in edge_map
        assert ("GammaNode", "DeltaNode") in edge_map

        # Verificar hechos
        facts = db.get_active_facts()
        assert len(facts) == 2
        fact_vals = [f.value for f in facts]
        assert "Legacy rule: Always verify before completion" in fact_vals

        # 4. Verificar Backup
        backup_dir = Path(result["backup_path"])
        assert backup_dir.exists()
        assert (backup_dir / "AlphaNode.md").exists()

        # 5. Idempotencia: una segunda migración no rompe ni corrompe
        result_2 = migrator.migrate(create_backup=False)
        assert result_2["success"] is True
