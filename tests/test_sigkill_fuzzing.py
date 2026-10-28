"""
Gatekeeper G10: Real Process Crash Fuzzing with TerminateProcess/SIGKILL.
Verifies Two-Phase Commit Journal ACID integrity under abrupt mid-write process death.
"""

import os
import sys
import time
import subprocess
import tempfile
from pathlib import Path
from synapse4d.storage.db import SynapseDatabase
from synapse4d.storage.journal import AtomicJournal


def test_crash_fuzzing_mid_transaction():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        vault = Path(tmpdir)
        db = SynapseDatabase(vault)
        journal = AtomicJournal(vault, db)

        # 1. Crear un archivo Markdown de contexto previo
        context_file = vault / "00_Working_Memory" / "active_context.md"
        context_file.parent.mkdir(parents=True, exist_ok=True)
        original_content = "# Active Context\nInitial verified state before crash."
        context_file.write_text(original_content, encoding="utf-8")

        # 2. Script auxiliar del subproceso worker
        worker_code = f"""
import time
import sys
from pathlib import Path
from synapse4d.storage.db import SynapseDatabase
from synapse4d.storage.journal import AtomicJournal

vault = Path(r"{vault}")
db = SynapseDatabase(vault)
journal = AtomicJournal(vault, db)

sess_id = "sess_crash_target"
db.begin_session(sess_id)

f = vault / "00_Working_Memory" / "active_context.md"
journal.prepare_write_session(sess_id, [{{"path": str(f), "action": "modify"}}])

# Escribir contenido parcial/corrupto en el archivo objetivo
f.write_text("# Corrupted in flight write...", encoding="utf-8")

# Notificar al proceso padre que el journal y la escritura parcial ocurrieron
print("READY_FOR_KILL", flush=True)

time.sleep(10.0)
"""
        worker_script = vault / "worker_crash.py"
        worker_script.write_text(worker_code, encoding="utf-8")

        # Configurar PYTHONPATH para que el subproceso encuentre synapse4d
        repo_root = str(Path(__file__).resolve().parent.parent)
        env = dict(os.environ)
        env["PYTHONPATH"] = repo_root + (os.pathsep + env.get("PYTHONPATH", "") if "PYTHONPATH" in env else "")

        # 3. Lanzar subproceso
        proc = subprocess.Popen(
            [sys.executable, str(worker_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )

        # Esperar hasta que el worker confirme que stage_file_write fue ejecutado
        ready = False
        start_wait = time.time()
        while time.time() - start_wait < 8.0:
            line = proc.stdout.readline()
            if "READY_FOR_KILL" in line:
                ready = True
                break
            time.sleep(0.05)

        if not ready:
            err = proc.stderr.read()
            proc.kill()
            raise AssertionError(f"Worker no alcanzó READY_FOR_KILL. Stderr: {err}")

        # 4. KILL INMEDIATO (SIGKILL / TerminateProcess a nivel de SO)
        proc.kill()
        proc.wait(timeout=3.0)

        assert proc.poll() is not None, "El subproceso no fue terminado de inmediato"

        # Verificar que el archivo en este punto contiene el texto corrupto antes de la recuperación
        corrupted_content = context_file.read_text(encoding="utf-8")
        assert "Corrupted in flight" in corrupted_content

        # 5. Reconciliación en arranque como lo haría SynapseEngine
        reconciled_db = SynapseDatabase(vault)
        reconciled_journal = AtomicJournal(vault, reconciled_db)

        # Verificar integridad física de SQLite antes de reconciliar
        with reconciled_db.get_connection() as conn:
            integrity = conn.execute("PRAGMA integrity_check;").fetchone()[0]
            assert integrity == "ok", f"Integridad corrupta en SQLite: {integrity}"

        # Ejecutar auto-reconciliación
        recovery = reconciled_journal.reconcile_on_startup()
        assert recovery["status"] == "rolled_back_pre_commit"
        assert recovery["recovered"] is True

        # 6. Verificar que el archivo Markdown recuperó su contenido original determinista
        restored_content = context_file.read_text(encoding="utf-8")
        assert restored_content == original_content, "El archivo Markdown no fue restaurado al contenido original"

        # 7. Verificar integridad física final de SQLite
        with reconciled_db.get_connection() as conn:
            integrity = conn.execute("PRAGMA integrity_check;").fetchone()[0]
            assert integrity == "ok"
