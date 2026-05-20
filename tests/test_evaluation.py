"""Tests for the evaluation scorer."""

import pytest

from src.evaluation.scorer import (
    Scorer,
    contains_match,
    exact_match,
    length_ratio,
)


class TestMetrics:
    def test_exact_match_true(self) -> None:
        assert exact_match("hello", "hello") == 1.0

    def test_exact_match_false(self) -> None:
        assert exact_match("hello", "world") == 0.0

    def test_exact_match_strips_whitespace(self) -> None:
        assert exact_match("  hello  ", "hello") == 1.0

    def test_contains_match_true(self) -> None:
        assert contains_match("The answer is Paris", "Paris") == 1.0

    def test_contains_match_false(self) -> None:
        assert contains_match("The answer is Lyon", "Paris") == 0.0

    def test_length_ratio_exact(self) -> None:
        assert length_ratio("abcde", "fghij") == 1.0

    def test_length_ratio_shorter(self) -> None:
        score = length_ratio("ab", "abcd")
        assert 0.0 < score < 1.0

    def test_length_ratio_empty_expected(self) -> None:
        assert length_ratio("", "") == 1.0
        assert length_ratio("something", "") == 0.0


class TestScorer:
    def test_single_metric(self) -> None:
        scorer = Scorer(pass_threshold=0.5)
        scorer.add_metric("exact", exact_match)
        result = scorer.score("hello", "hello")
        assert result.score == 1.0
        assert result.passed is True

    def test_weighted_metrics(self) -> None:
        scorer = Scorer(pass_threshold=0.5)
        scorer.add_metric("exact", exact_match, weight=1.0)
        scorer.add_metric("contains", contains_match, weight=2.0)

        result = scorer.score("The answer is Paris", "Paris")
        assert result.metrics["exact"] == 0.0
        assert result.metrics["contains"] == 1.0
        assert result.score == pytest.approx(0.667, abs=0.01)
        assert result.passed is True

    def test_no_metrics_raises(self) -> None:
        scorer = Scorer()
        with pytest.raises(ValueError, match="No metrics registered"):
            scorer.score("output", "expected")

    def test_fail_threshold(self) -> None:
        scorer = Scorer(pass_threshold=0.9)
        scorer.add_metric("exact", exact_match)
        result = scorer.score("wrong", "right")
        assert result.passed is False
