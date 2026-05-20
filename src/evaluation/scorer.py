"""Evaluation scorer for measuring agent output quality."""

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class EvalResult:
    """Result of evaluating a single agent output."""

    score: float  # 0.0 to 1.0
    passed: bool
    metrics: dict[str, float] = field(default_factory=dict)
    details: str = ""


# A metric function takes (output, expected) and returns a float 0-1
MetricFn = Callable[[str, str], float]


class Scorer:
    """Evaluate agent outputs against expected results.

    Register metric functions, then call `score()` to evaluate.
    The overall score is the weighted average of all metrics.
    """

    def __init__(self, pass_threshold: float = 0.7) -> None:
        self.pass_threshold = pass_threshold
        self._metrics: dict[str, tuple[MetricFn, float]] = {}

    def add_metric(self, name: str, fn: MetricFn, weight: float = 1.0) -> None:
        """Register a metric function.

        Args:
            name: Metric identifier.
            fn: Function(output, expected) -> float (0-1).
            weight: Relative weight in the overall score.
        """
        self._metrics[name] = (fn, weight)

    def score(self, output: str, expected: str) -> EvalResult:
        """Score an agent output against the expected result.

        Returns:
            EvalResult with individual metric scores and overall pass/fail.
        """
        if not self._metrics:
            raise ValueError("No metrics registered. Call add_metric() first.")

        metric_scores: dict[str, float] = {}
        total_weight = 0.0
        weighted_sum = 0.0

        for name, (fn, weight) in self._metrics.items():
            score = fn(output, expected)
            metric_scores[name] = score
            weighted_sum += score * weight
            total_weight += weight

        overall = weighted_sum / total_weight if total_weight > 0 else 0.0

        return EvalResult(
            score=overall,
            passed=overall >= self.pass_threshold,
            metrics=metric_scores,
        )


# Built-in metrics

def exact_match(output: str, expected: str) -> float:
    """1.0 if output exactly matches expected, else 0.0."""
    return 1.0 if output.strip() == expected.strip() else 0.0


def contains_match(output: str, expected: str) -> float:
    """1.0 if expected is a substring of output, else 0.0."""
    return 1.0 if expected.strip() in output else 0.0


def length_ratio(output: str, expected: str) -> float:
    """Score based on how close the output length is to expected length."""
    if not expected:
        return 1.0 if not output else 0.0
    ratio = len(output) / len(expected)
    if ratio > 1:
        ratio = 1 / ratio
    return max(0.0, ratio)
