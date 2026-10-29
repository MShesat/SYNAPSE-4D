"""
Gatekeeper G5 Completo: End-to-End Search & Consolidation Latency Benchmark.
Evaluates:
  1. Full hybrid semantic search() with ONNX embedding inference (FastEmbed/all-MiniLM-L6-v2) + SQLite cosine scan.
  2. Full 4D consolidate() cycle (Episodic markdown ingestion -> D2 fact distillation + ONNX embedding -> 2PC ACID commit -> D4 reciprocal closure & stubs).
"""

import time
import tempfile
from pathlib import Path
from synapse4d.core import SynapseEngine


def run_pipeline_benchmark():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        vault = Path(tmpdir)
        print("=== SYNAPSE 4D PIPELINE BENCHMARK (SEARCH & CONSOLIDATE) ===")
        print(f"Bóveda temporal en disco: {vault}\n")

        engine = SynapseEngine(vault)

        # 1. Crear bitácoras episódicas sintéticas para consolidar
        episodic_dir = engine.episodic_dir
        for i in range(5):
            log_file = episodic_dir / f"session_log_{i:02d}.md"
            log_file.write_text(f"""---
session_id: sess_bench_{i:02d}
date: 2026-10-28
---
# Bitácora de Sesión {i:02d}
- Python 3.13 es el lenguaje oficial del núcleo
- Regla: Nunca almacenar claves privadas en texto plano
- SQLite WAL garantiza transacciones concurrentes con cero corrupción
- La dimensión D4 asegura clausura recíproca entre nodos
- FastEmbed ONNX ejecuta inferencia vectorial local en menos de 15ms
- El osciloscopio neural refleja excitación de sinapsis en tiempo real
""", encoding="utf-8")

        # 2. Medir tiempo de consolidate() completo
        print("[1/2] Ejecutando consolidate() de extremo a extremo...")
        t0_cons = time.perf_counter()
        stats = engine.consolidate(recent_only=False)
        t_cons = time.perf_counter() - t0_cons

        print(f"-> Hechos destilados con embeddings ONNX: {stats['facts_distilled']}")
        print(f"-> Hechos retenidos en SQLite: {stats['facts_retained']}")
        print(f"-> Stubs D4 generados: {stats['stubs_created']}")
        print(f"-> Latencia total de consolidate(): {t_cons:.3f} s (Umbral: < 3.0s)")
        assert t_cons < 3.0, f"Violación de Gatekeeper G5: consolidate() ({t_cons:.3f}s) supera 3.0s"

        # 3. Medir search() completo con embeddings ONNX en caliente
        print("\n[2/2] Ejecutando 50 consultas de search() semántico híbrido...")
        queries = [
            "claves privadas y seguridad",
            "base de datos sqlite wal",
            "python lenguaje oficial",
            "inferencia vectorial local onnx",
            "clausura reciproca y grafos",
            "tiempo de osciloscopio",
            "transacciones concurrentes",
            "memoria asociativa de nodos",
            "arquitectura cognitiva 4d",
            "resguardo de llaves y secretos"
        ]

        latencies_ms = []
        # Pre-calentar motor de embeddings
        engine.search("warmup query")

        for _ in range(5):
            for q in queries:
                t0 = time.perf_counter()
                results = engine.search(q, limit=5)
                t1 = time.perf_counter()
                latencies_ms.append((t1 - t0) * 1000.0)

        latencies_ms.sort()
        n = len(latencies_ms)
        p50 = latencies_ms[int(n * 0.50)]
        p95 = latencies_ms[int(n * 0.95)]
        p99 = latencies_ms[int(n * 0.99)]
        avg = sum(latencies_ms) / n

        print("=== RESULTADOS DE LATENCIA SEARCH() SEMÁNTICO (CON ONNX FAST_EMBED) ===")
        print(f"Latencia Media: {avg:.2f} ms")
        print(f"p50 (Mediana):  {p50:.2f} ms")
        print(f"p95:            {p95:.2f} ms")
        print(f"p99:            {p99:.2f} ms")
        print(f"Throughput:     {n / (sum(latencies_ms) / 1000.0):.1f} queries/sec")

        assert p95 < 35.0, f"Violación de Gatekeeper G5: search() p95 ({p95:.2f}ms) supera 35.0ms"
        print("\n[VEREDICTO G5 COMPLETO]: APROBADO (consolidate < 3.0s y search p95 < 35ms)")


if __name__ == "__main__":
    run_pipeline_benchmark()
