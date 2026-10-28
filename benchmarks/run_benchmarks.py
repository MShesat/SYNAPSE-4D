"""
Gatekeeper G5: Synapse 4D High-Load Topological Benchmark.
Evaluates SQLite WAL performance with 10,000 synaptic edges and lazy Hebbian decay UDF.
"""

import time
import tempfile
import random
from pathlib import Path
from synapse4d.storage.db import SynapseDatabase, eff_weight_udf


def run_benchmark():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        vault = Path(tmpdir)
        print("=== SYNAPSE 4D BENCHMARK (10,000 EDGES LOAD) ===")
        print(f"Directorio temporal: {vault}")

        db = SynapseDatabase(vault)

        # 1. Inserción masiva de 10,000 aristas
        t_start_insert = time.perf_counter()
        entities = [f"entity_{i:04d}" for i in range(500)]
        relations = ["supersedes", "relacionado_con", "contradice", "depende_de"]

        batch_edges = []
        now = time.time()
        seen = set()
        while len(batch_edges) < 10000:
            src = random.choice(entities)
            tgt = random.choice(entities)
            if tgt == src:
                continue
            rel = random.choice(relations)
            pair = (src, tgt, rel)
            if pair in seen:
                continue
            seen.add(pair)
            bw = round(random.uniform(0.5, 5.0), 2)
            epoch = now - random.uniform(0, 30 * 86400)  # hasta 30 días atrás
            batch_edges.append((src, tgt, rel, bw, epoch, "bench_sess", "bench_sess", "active"))

        with db._lock:
            with db.get_connection() as conn:
                conn.executemany(
                    """
                    INSERT INTO edges (source_entity, target_entity, relation, base_weight, last_retrieved_epoch, session_id, last_modified_session, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    batch_edges,
                )
                conn.commit()

        t_insert = time.perf_counter() - t_start_insert
        print(f"-> 10,000 aristas insertadas en {t_insert:.4f}s ({10000 / t_insert:.0f} edges/sec)")

        # 2. Benchmark de consultas con UDF eff_weight (1,000 queries)
        num_queries = 1000
        latencies_ms = []

        now_epoch = time.time()
        conn = db.get_connection()
        try:
            for _ in range(num_queries):
                target_ent = random.choice(entities)
                t0 = time.perf_counter()
                cursor = conn.execute(
                    """
                    SELECT source_entity, target_entity, relation,
                           eff_weight(base_weight, last_retrieved_epoch, ?) AS current_weight
                    FROM edges
                    WHERE source_entity = ? AND status = 'active'
                    ORDER BY current_weight DESC
                    LIMIT 20
                    """,
                    (now_epoch, target_ent),
                )
                rows = cursor.fetchall()
                t1 = time.perf_counter()
                latencies_ms.append((t1 - t0) * 1000.0)
        finally:
            conn.close()

        latencies_ms.sort()
        p50 = latencies_ms[int(num_queries * 0.50)]
        p95 = latencies_ms[int(num_queries * 0.95)]
        p99 = latencies_ms[int(num_queries * 0.99)]
        avg = sum(latencies_ms) / len(latencies_ms)

        print("\n=== RESULTADOS DE LATENCIA (1,000 CONSULTAS CON UDF HEBBIANO) ===")
        print(f"Latencia Media: {avg:.3f} ms")
        print(f"p50 (Mediana):  {p50:.3f} ms")
        print(f"p95:            {p95:.3f} ms")
        print(f"p99:            {p99:.3f} ms")
        print(f"Throughput:     {num_queries / (sum(latencies_ms) / 1000.0):.0f} queries/sec")

        assert p95 < 5.0, f"Violación de Gatekeeper G5: p95 ({p95:.3f}ms) supera el umbral de 5.0ms"
        print("\n[VEREDICTO G5]: APROBADO (p95 < 5.0 ms)")


if __name__ == "__main__":
    run_benchmark()
