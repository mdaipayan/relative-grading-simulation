"""Unit tests for controlled score contamination / outlier perturbation."""

import numpy as np
import pytest
from relative_grading.contamination import contaminate


def test_contamination_amount_rounding():
    rng = np.random.default_rng(42)
    n = 10
    internal = np.full(n, 50.0)
    external = np.full(n, 50.0)

    # N=10, eps=0.01 -> m = round(0.1) = 0
    res_0 = contaminate(internal, external, epsilon=0.01, direction="lower", rng=rng)
    assert res_0.actual_m == 0
    assert len(res_0.perturbed_indices) == 0
    assert np.all(res_0.total == 50.0)

    # N=10, eps=0.05 -> m = round(0.5) = 0 (or 1 depending on round half to even in Python)
    # round(0.5) in python is 0, round(0.1*10) = 1
    res_1 = contaminate(internal, external, epsilon=0.10, direction="lower", rng=rng)
    assert res_1.actual_m == 1
    assert len(res_1.perturbed_indices) == 1
    assert res_1.internal[res_1.perturbed_indices[0]] <= 5.0
    assert res_1.external[res_1.perturbed_indices[0]] <= 5.0


def test_contamination_direction_bounds():
    rng = np.random.default_rng(100)
    n = 100
    internal = np.full(n, 50.0)
    external = np.full(n, 50.0)

    # Lower perturbation: U(0, 5)
    res_low = contaminate(internal, external, epsilon=0.05, direction="lower", rng=rng)
    assert res_low.actual_m == 5
    for idx in res_low.perturbed_indices:
        assert 0.0 <= res_low.internal[idx] <= 5.0
        assert 0.0 <= res_low.external[idx] <= 5.0

    # Upper perturbation: U(95, 100)
    res_high = contaminate(internal, external, epsilon=0.05, direction="upper", rng=rng)
    assert res_high.actual_m == 5
    for idx in res_high.perturbed_indices:
        assert 95.0 <= res_high.internal[idx] <= 100.0
        assert 95.0 <= res_high.external[idx] <= 100.0
