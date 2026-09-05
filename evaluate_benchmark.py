import json
from pathlib import Path
import numpy as np

from app.analysis.embeddings import MiniLMEmbedder
from app.analysis.pipeline import AnalysisPipeline
from app.analysis.taxonomy import load_taxonomy
from app.analysis.types import AnalysisConfig


def evaluate():
    benchmark_path = Path("tests/data/benchmark_v1.json")
    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark = json.load(f)

    embedder = MiniLMEmbedder()
    taxonomy = load_taxonomy()
    config = AnalysisConfig(strong_threshold=0.60, partial_threshold=0.30)
    pipeline = AnalysisPipeline(embedder, taxonomy, config)

    results = []
    cases = benchmark["cases"]

    for case in cases:
        req = case["requirement"]
        ev = case["evidence"]
        analysis = pipeline.analyze(ev, req)

        if not analysis.requirement_matches:
            pred_label = "weak"
            sim = 0.0
            best_ev = None
            primary_cluster = None
            assigned = []
            ev_suff = False
        else:
            match = analysis.requirement_matches[0]
            pred_label = match.status
            sim = match.similarity
            best_ev = match.evidence_text
            primary_cluster = match.primary_cluster.cluster_id
            assigned = [c.cluster_id for c in match.cluster_assignments]
            ev_suff = match.evidence_sufficient

        results.append({
            "id": case["id"],
            "category": case["category"],
            "expected_label": case["expected_label"],
            "predicted_label": pred_label,
            "similarity": float(sim),
            "evidence_sufficient": bool(ev_suff),
            "best_evidence": best_ev,
            "primary_cluster": primary_cluster,
            "assigned_clusters": assigned,
            "expected_clusters": case["expected_clusters"],
            "match": pred_label == case["expected_label"],
        })

    out_file = Path("tests/data/evaluation_results_v1.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "benchmark_version": benchmark["version"],
            "model": embedder.model_name,
            "thresholds": {
                "strong": config.strong_threshold,
                "partial": config.partial_threshold,
                "evidence": config.evidence_threshold,
            },
            "results": results,
        }, f, indent=2)

    return benchmark, results, config, embedder.model_name


def main():
    benchmark, results, config, model_name = evaluate()
    total = len(results)
    correct = sum(1 for r in results if r["match"])
    accuracy = correct / total if total > 0 else 0

    labels = ["strong", "partial", "weak"]
    matrix = {exp: {pred: 0 for pred in labels} for exp in labels}
    for r in results:
        matrix[r["expected_label"]][r["predicted_label"]] += 1

    metrics = {}
    for label in labels:
        tp = matrix[label][label]
        fp = sum(matrix[exp][label] for exp in labels if exp != label)
        fn = sum(matrix[label][pred] for pred in labels if pred != label)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        metrics[label] = {"precision": prec, "recall": rec, "f1": f1}

    macro_prec = sum(m["precision"] for m in metrics.values()) / 3
    macro_rec = sum(m["recall"] for m in metrics.values()) / 3
    macro_f1 = sum(m["f1"] for m in metrics.values()) / 3

    print("=" * 60)
    print("PHASE 4B — BENCHMARK EVALUATION REPORT")
    print("=" * 60)
    print(f"Benchmark Version: {benchmark['version']}")
    print(f"Model: {model_name}")
    print(f"Thresholds: Strong={config.strong_threshold}, Partial={config.partial_threshold}, Evidence={config.evidence_threshold}")
    print(f"Total Cases: {total}")
    print(f"Overall Accuracy: {accuracy:.2%} ({correct}/{total})")
    print("\n--- Per-Label Metrics ---")
    for label in labels:
        m = metrics[label]
        print(f"  {label.capitalize():<8}: Precision={m['precision']:.3f}, Recall={m['recall']:.3f}, F1={m['f1']:.3f}")
    print(f"  Macro-Avg: Precision={macro_prec:.3f}, Recall={macro_rec:.3f}, F1={macro_f1:.3f}")

    print("\n--- Confusion Matrix ---")
    print("                 PREDICTED")
    print("              Strong  Partial  Weak")
    print("EXPECTED")
    for exp in labels:
        row = "  ".join(f"{matrix[exp][pred]:>7}" for pred in labels)
        print(f"{exp.capitalize():<8} {row}")

    print("\n--- Category-Level Results ---")
    categories = sorted(set(r["category"] for r in results))
    for cat in categories:
        cat_items = [r for r in results if r["category"] == cat]
        cat_corr = sum(1 for r in cat_items if r["match"])
        print(f"  {cat:<22}: {cat_corr/len(cat_items):>6.2%} ({cat_corr}/{len(cat_items)})")

    print("\n--- Similarity Distribution by Human Label ---")
    for label in labels:
        scores = [r["similarity"] for r in results if r["expected_label"] == label]
        if scores:
            print(f"  {label.capitalize():<8}: count={len(scores)}, min={min(scores):.3f}, max={max(scores):.3f}, mean={np.mean(scores):.3f}, median={np.median(scores):.3f}")

    failures = [r for r in results if not r["match"]]
    print(f"\n--- Failure Analysis ({len(failures)} mismatches) ---")
    for f in failures:
        case = next(c for c in benchmark["cases"] if c["id"] == f["id"])
        print(f"\nCase ID: {f['id']} | Category: {f['category']}")
        print(f"  Requirement: {case['requirement']}")
        print(f"  Evidence:    {case['evidence']}")
        print(f"  Expected:    {f['expected_label'].upper()} | Predicted: {f['predicted_label'].upper()} (sim={f['similarity']:.3f}, suff={f['evidence_sufficient']})")
        print(f"  Rationale:   {case['rationale']}")
        print(f"  Clusters:    Expected={f['expected_clusters']}, Assigned={f['assigned_clusters']}")


if __name__ == "__main__":
    main()

