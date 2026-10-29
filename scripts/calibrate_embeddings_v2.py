"""
Synapse 4D - Empirical Embeddings & Polarity Calibration v2.0
Evaluates the semantic relation classifier on the golden_pairs_v2 benchmark dataset.

Requirements:
- Overall Accuracy >= 0.85
- Per-class F1-Score >= 0.70 (conflict, redundant, orthogonal)
- 95% Bootstrap Confidence Interval over 1,000 iterations
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Verify engine dependencies with clean error messages
try:
    from synapse4d.nlp.embeddings import EmbeddingEngine, compute_similarity
except ImportError as err:
    sys.exit(f"API changed: cannot import EmbeddingEngine or compute_similarity ({err})")

try:
    from synapse4d.nlp.polarity import classify_relation
except ImportError as err:
    sys.exit(f"API changed: cannot import classify_relation from synapse4d.nlp.polarity ({err})")

CLASSES = ["conflict", "redundant", "orthogonal"]
MIN_ACCURACY = 0.85
MIN_F1_PER_CLASS = 0.70
BOOTSTRAP_ITERATIONS = 1000


def resolve_dataset_path() -> Path:
    """Locate golden_pairs_v2.jsonl relative to script location or repository root."""
    candidate_locations = [
        Path(__file__).resolve().parent.parent / "benchmarks" / "data" / "golden_pairs_v2.jsonl",
        Path.cwd() / "benchmarks" / "data" / "golden_pairs_v2.jsonl",
    ]
    for loc in candidate_locations:
        if loc.exists():
            return loc
    sys.exit(f"API changed / Missing file: golden_pairs_v2.jsonl not found in {[str(p) for p in candidate_locations]}")


def load_dataset(dataset_path: Path) -> List[Dict[str, Any]]:
    """Load JSONL dataset."""
    pairs: List[Dict[str, Any]] = []
    with dataset_path.open("r", encoding="utf-8") as f:
        for line_no, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                for req_key in ["id", "text_a", "text_b", "expected", "language", "domain"]:
                    if req_key not in item:
                        raise KeyError(f"Missing required field '{req_key}'")
                pairs.append(item)
            except Exception as e:
                sys.exit(f"Error parsing {dataset_path} at line {line_no}: {e}")
    if not pairs:
        sys.exit(f"Dataset is empty: {dataset_path}")
    return pairs


def compute_bootstrap_ci(
    records: List[Tuple[str, str]], iterations: int = BOOTSTRAP_ITERATIONS, seed: int = 42
) -> Tuple[float, float]:
    """Calculate 95% Confidence Interval for accuracy using empirical bootstrap."""
    rng = random.Random(seed)
    n = len(records)
    boot_accs: List[float] = []

    for _ in range(iterations):
        sample = rng.choices(records, k=n)
        correct_count = sum(1 for exp, pred in sample if exp == pred)
        boot_accs.append(correct_count / n)

    boot_accs.sort()
    lower_idx = int(0.025 * iterations)
    upper_idx = int(0.975 * iterations)
    return round(boot_accs[lower_idx], 4), round(boot_accs[upper_idx], 4)


def run_calibration() -> int:
    dataset_path = resolve_dataset_path()
    pairs = load_dataset(dataset_path)

    # Initialize Embedding Engine
    if not hasattr(EmbeddingEngine, "get_instance"):
        sys.exit("API changed: EmbeddingEngine.get_instance method not found")

    try:
        engine = EmbeddingEngine.get_instance()
    except Exception as e:
        sys.exit(f"API changed: failed to initialize EmbeddingEngine ({e})")

    if not hasattr(engine, "embed_text"):
        sys.exit("API changed: EmbeddingEngine.embed_text method not found")

    # Confusion matrix: matrix[expected][predicted]
    conf_matrix: Dict[str, Dict[str, int]] = {
        cls_exp: {cls_pred: 0 for cls_pred in CLASSES} for cls_exp in CLASSES
    }

    results: List[Tuple[str, str]] = []
    details: List[Dict[str, Any]] = []

    for item in pairs:
        pair_id = item["id"]
        text_a = item["text_a"]
        text_b = item["text_b"]
        expected = item["expected"]

        vec_a = engine.embed_text(text_a)
        vec_b = engine.embed_text(text_b)
        sim = float(compute_similarity(vec_a, vec_b))

        predicted = classify_relation(sim, text_a, text_b)
        if predicted not in CLASSES:
            predicted = "orthogonal"

        conf_matrix[expected][predicted] += 1
        results.append((expected, predicted))
        details.append({
            "id": pair_id,
            "expected": expected,
            "predicted": predicted,
            "similarity": round(sim, 4),
            "match": (expected == predicted),
            "language": item.get("language"),
            "domain": item.get("domain"),
        })

    total = len(results)
    correct = sum(1 for exp, pred in results if exp == pred)
    overall_accuracy = round(correct / total, 4)

    # Bootstrap 95% CI
    ci_lower, ci_upper = compute_bootstrap_ci(results, iterations=BOOTSTRAP_ITERATIONS)

    # Metrics per class
    metrics_per_class: Dict[str, Dict[str, float]] = {}
    f1_failures: List[str] = []

    for c in CLASSES:
        tp = conf_matrix[c][c]
        fp = sum(conf_matrix[other][c] for other in CLASSES if other != c)
        fn = sum(conf_matrix[c][other] for other in CLASSES if other != c)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

        metrics_per_class[c] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "support": tp + fn,
        }

        if f1 < MIN_F1_PER_CLASS:
            f1_failures.append(f"{c} (F1: {f1:.4f} < {MIN_F1_PER_CLASS})")

    accuracy_passed = overall_accuracy >= MIN_ACCURACY
    f1_passed = len(f1_failures) == 0
    passed = accuracy_passed and f1_passed

    report = {
        "status": "success",
        "verdict": "PASSED" if passed else "FAILED",
        "dataset": str(dataset_path),
        "total_pairs": total,
        "correct_predictions": correct,
        "accuracy": overall_accuracy,
        "confidence_interval_95": {
            "lower": ci_lower,
            "upper": ci_upper,
            "iterations": BOOTSTRAP_ITERATIONS,
        },
        "metrics_per_class": metrics_per_class,
        "confusion_matrix": {
            "labels": CLASSES,
            "matrix": conf_matrix,
        },
        "thresholds": {
            "min_accuracy": MIN_ACCURACY,
            "min_f1_per_class": MIN_F1_PER_CLASS,
        },
        "failures": {
            "accuracy": None if accuracy_passed else f"Accuracy {overall_accuracy} < {MIN_ACCURACY}",
            "f1_scores": f1_failures if not f1_passed else [],
        },
    }

    # Print output formatted as valid JSON
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if not passed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run_calibration())
