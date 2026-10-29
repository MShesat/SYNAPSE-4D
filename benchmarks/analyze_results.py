#!/usr/bin/env python3
"""
Synapse 4D - Benchmark Results Analyzer
Parses benchmark JSON results, verifies latency percentiles against strict SLA thresholds,
and outputs a formatted Markdown report with a text summary.

Thresholds:
- search p95 < 15.0 ms
- consolidate p95 < 3000.0 ms

Usage:
    python benchmarks/analyze_results.py --input results.json
    cat results.json | python benchmarks/analyze_results.py --input -
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure stdout handles UTF-8 gracefully on Windows cp1252 consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SEARCH_P95_MAX_MS = 15.0
CONSOLIDATE_P95_MAX_MS = 3000.0


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze Synapse 4D benchmark JSON output against latency SLA gates."
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default="benchmarks/results/benchmark_results.json",
        help="Path to JSON file, raw JSON string, or '-' to read from stdin (default: benchmarks/results/benchmark_results.json)",
    )
    return parser.parse_args()


def load_benchmark_data(input_src: str) -> Dict[str, Any]:
    """Load JSON payload from stdin, raw JSON string, or file."""
    if input_src == "-":
        try:
            return json.load(sys.stdin)
        except Exception as e:
            sys.exit(f"Error reading JSON from stdin: {e}")

    # Check if raw JSON string was passed directly
    trimmed = input_src.strip()
    if trimmed.startswith("{") and trimmed.endswith("}"):
        try:
            return json.loads(trimmed)
        except Exception as e:
            sys.exit(f"Error parsing raw JSON string: {e}")

    file_path = Path(input_src)
    if not file_path.exists():
        sys.exit(f"Benchmark results file not found: {file_path}")

    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        sys.exit(f"Error reading benchmark results JSON from '{file_path}': {e}")


def validate_metrics(data: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    """Verify SLA thresholds for search and consolidate operations."""
    failures: List[str] = []
    analysis: Dict[str, Any] = {}

    # 1. Search latency validation
    if "search" not in data:
        failures.append("Missing required 'search' metric group in benchmark JSON")
        search_metrics = {}
    else:
        search_metrics = data["search"]
        p95_search = search_metrics.get("p95")
        if p95_search is None:
            failures.append("Missing 'p95' in 'search' benchmark data")
        elif float(p95_search) >= SEARCH_P95_MAX_MS:
            failures.append(
                f"Search p95 threshold violated: {p95_search:.2f} ms >= {SEARCH_P95_MAX_MS:.2f} ms"
            )

    # 2. Consolidate latency validation
    if "consolidate" not in data:
        failures.append("Missing required 'consolidate' metric group in benchmark JSON")
        cons_metrics = {}
    else:
        cons_metrics = data["consolidate"]
        p95_cons = cons_metrics.get("p95")
        if p95_cons is None:
            failures.append("Missing 'p95' in 'consolidate' benchmark data")
        elif float(p95_cons) >= CONSOLIDATE_P95_MAX_MS:
            failures.append(
                f"Consolidate p95 threshold violated: {p95_cons:.2f} ms >= {CONSOLIDATE_P95_MAX_MS:.2f} ms"
            )

    analysis["search"] = search_metrics
    analysis["consolidate"] = cons_metrics
    all_passed = (len(failures) == 0)
    return all_passed, failures, analysis


def generate_markdown_table(data: Dict[str, Any]) -> str:
    """Generate Markdown comparison table."""
    lines = [
        "| Operacion | Metrica p50 (ms) | Metrica p95 (ms) | Umbral SLA p95 | Metrica p99 (ms) | Estado SLA |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
    ]

    # Search row
    s = data.get("search", {})
    s_p50 = f"{s.get('p50', 0.0):.2f}" if "p50" in s else "N/A"
    s_p95_val = s.get("p95")
    s_p95 = f"{s_p95_val:.2f}" if s_p95_val is not None else "N/A"
    s_p99 = f"{s.get('p99', 0.0):.2f}" if "p99" in s else "N/A"
    s_status = (
        "PASS"
        if (s_p95_val is not None and float(s_p95_val) < SEARCH_P95_MAX_MS)
        else "FAIL"
    )
    lines.append(
        f"| **Search (Busqueda)** | {s_p50} | {s_p95} | < {SEARCH_P95_MAX_MS:.1f} ms | {s_p99} | **{s_status}** |"
    )

    # Consolidate row
    c = data.get("consolidate", {})
    c_p50 = f"{c.get('p50', 0.0):.2f}" if "p50" in c else "N/A"
    c_p95_val = c.get("p95")
    c_p95 = f"{c_p95_val:.2f}" if c_p95_val is not None else "N/A"
    c_p99 = f"{c.get('p99', 0.0):.2f}" if "p99" in c else "N/A"
    c_status = (
        "PASS"
        if (c_p95_val is not None and float(c_p95_val) < CONSOLIDATE_P95_MAX_MS)
        else "FAIL"
    )
    lines.append(
        f"| **Consolidate (Ciclo 4D)** | {c_p50} | {c_p95} | < {CONSOLIDATE_P95_MAX_MS:.1f} ms | {c_p99} | **{c_status}** |"
    )

    return "\n".join(lines)


def main() -> int:
    args = parse_arguments()
    benchmark_data = load_benchmark_data(args.input)
    passed, failures, _ = validate_metrics(benchmark_data)

    md_table = generate_markdown_table(benchmark_data)

    print("\n" + "=" * 70)
    print("      SYNAPSE 4D - INFORME DE ANALISIS DE RENDIMIENTO Y LATENCIA      ")
    print("=" * 70 + "\n")

    print(md_table)
    print("\n" + "-" * 70)

    if passed:
        print("[VEREDICTO GLOBAL]: APROBADO (Todos los umbrales p95 cumplen los SLA)")
        print(f"  [PASS] Busqueda p95: {benchmark_data['search']['p95']:.2f} ms (< {SEARCH_P95_MAX_MS} ms)")
        print(f"  [PASS] Consolidacion p95: {benchmark_data['consolidate']['p95']:.2f} ms (< {CONSOLIDATE_P95_MAX_MS} ms)")
        print("=" * 70 + "\n")
        return 0
    else:
        print("[VEREDICTO GLOBAL]: RECHAZADO (Violacion de umbrales criticos)")
        for fail in failures:
            print(f"  [FAIL] {fail}")
        print("=" * 70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
