import json
import pytest
from pathlib import Path

BENCHMARK_PATH = Path(__file__).parent / "data" / "benchmark_v1.json"

def test_benchmark_file_exists():
    """Verify that the benchmark dataset file exists."""
    assert BENCHMARK_PATH.exists(), f"Benchmark file not found at {BENCHMARK_PATH}"

def test_benchmark_schema_and_integrity():
    """Validate the benchmark dataset schema and integrity."""
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "version" in data
    assert "metadata" in data
    assert "cases" in data
    
    cases = data["cases"]
    assert 30 <= len(cases) <= 40, f"Expected 30-40 cases, found {len(cases)}"

    case_ids = set()
    required_fields = {
        "id", "category", "requirement", "evidence", 
        "expected_label", "expected_importance", "expected_clusters", "rationale"
    }
    valid_labels = {"strong", "partial", "weak"}
    valid_importance = {"required", "preferred", "unspecified"}
    
    categories_found = set()

    for case in cases:
        # Field presence
        for field in required_fields:
            assert field in case, f"Case {case.get('id')} missing field: {field}"
        
        # Unique IDs
        assert case["id"] not in case_ids, f"Duplicate case ID: {case['id']}"
        case_ids.add(case["id"])
        
        # Valid labels and importance
        assert case["expected_label"] in valid_labels, f"Invalid label in {case['id']}: {case['expected_label']}"
        assert case["expected_importance"] in valid_importance, f"Invalid importance in {case['id']}: {case['expected_importance']}"
        
        # Non-empty rationales and texts
        assert len(case["requirement"].strip()) > 5, f"Requirement too short in {case['id']}"
        assert len(case["evidence"].strip()) > 5, f"Evidence too short in {case['id']}"
        assert len(case["rationale"].strip()) > 10, f"Rationale too short in {case['id']}"
        
        # Clusters
        assert isinstance(case["expected_clusters"], list)
        assert len(case["expected_clusters"]) > 0
        
        categories_found.add(case["category"])

    # Required Category Coverage
    required_categories = {
        "direct_strong", "semantic_paraphrase", "related_partial", 
        "unrelated_weak", "missing_evidence", "mixed_compound", 
        "importance_variation", "cluster_boundary"
    }
    for cat in required_categories:
        assert cat in categories_found, f"Missing required category: {cat}"

def test_benchmark_metadata_consistency():
    """Verify metadata matches the actual cases in the dataset."""
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    cases = data["cases"]
    metadata = data["metadata"]
    
    assert metadata["total_cases"] == len(cases)
    
    # Label distribution check
    for label in ["strong", "partial", "weak"]:
        actual_count = sum(1 for c in cases if c["expected_label"] == label)
        assert metadata["label_distribution"][label] == actual_count

    # Category distribution check
    for cat, count in metadata["category_distribution"].items():
        actual_count = sum(1 for c in cases if c["category"] == cat)
        assert count == actual_count
