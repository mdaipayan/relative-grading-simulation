"""Unit tests for score distribution generators."""

import numpy as np
import pytest
from relative_grading.distributions import generate_scores, DISTRIBUTIONS


def test_all_distributions_generate_valid_ranges():
    rng = np.random.default_rng(42)
    n = 1000

    for dist in DISTRIBUTIONS:
        scores = generate_scores(dist, n, rng)
        assert len(scores) == n, f"{dist} failed length check"
        assert np.all(scores >= 0.0), f"{dist} produced negative scores"
        assert np.all(scores <= 100.0), f"{dist} produced scores > 100"
        assert not np.isnan(scores).any(), f"{dist} produced NaN"


def test_distribution_moments_sanity():
    rng = np.random.default_rng(123)
    n = 20000

    # Normal: mean ~ 60, std ~ 15
    norm = generate_scores("Normal", n, rng)
    assert 58.0 < np.mean(norm) < 62.0
    assert 13.5 < np.std(norm) < 16.5

    # Compressed: mean ~ 60, std ~ 5
    comp = generate_scores("Compressed Normal", n, rng)
    assert 58.5 < np.mean(comp) < 61.5
    assert 4.5 < np.std(comp) < 5.5

    # Uniform: mean ~ 50
    unif = generate_scores("Uniform", n, rng)
    assert 48.0 < np.mean(unif) < 52.0

    # Right-skewed: Beta(2,5) * 100 -> mean = 2/7 * 100 ~ 28.57
    r_skew = generate_scores("Right-skewed", n, rng)
    assert 26.5 < np.mean(r_skew) < 30.5

    # Left-skewed: Beta(5,2) * 100 -> mean = 5/7 * 100 ~ 71.43
    l_skew = generate_scores("Left-skewed", n, rng)
    assert 69.5 < np.mean(l_skew) < 73.5


def test_unknown_distribution_raises():
    rng = np.random.default_rng(42)
    with pytest.raises(ValueError):
        generate_scores("Exponential", 100, rng)
