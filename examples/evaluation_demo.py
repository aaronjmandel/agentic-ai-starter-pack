"""Example: Evaluate agent outputs with the scoring framework.

Usage:
    python examples/evaluation_demo.py

Demonstrates how to set up metrics and score agent outputs.
No API key required — uses static test data.
"""

from src.evaluation.scorer import Scorer, contains_match, exact_match, length_ratio


def main() -> None:
    scorer = Scorer(pass_threshold=0.6)
    scorer.add_metric("exact", exact_match, weight=1.0)
    scorer.add_metric("contains", contains_match, weight=2.0)
    scorer.add_metric("length", length_ratio, weight=0.5)

    test_cases = [
        {
            "name": "Exact match",
            "output": "The capital of France is Paris.",
            "expected": "The capital of France is Paris.",
        },
        {
            "name": "Contains key info",
            "output": "Paris is the capital city of France, located in northern Europe.",
            "expected": "Paris",
        },
        {
            "name": "Wrong answer",
            "output": "The capital of France is Lyon.",
            "expected": "Paris",
        },
    ]

    print("=== Evaluation Demo ===\n")
    for case in test_cases:
        result = scorer.score(case["output"], case["expected"])
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {case['name']}")
        print(f"  Overall score: {result.score:.2f}")
        for metric, score in result.metrics.items():
            print(f"  {metric}: {score:.2f}")
        print()


if __name__ == "__main__":
    main()
