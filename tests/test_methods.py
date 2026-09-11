"""Unit tests for the 5 grading methods and grade assignment."""

import numpy as np
import pytest
from relative_grading.methods.mean_sd import MeanSD
from relative_grading.methods.percentile import Percentile
from relative_grading.methods.max_min import MaxMin
from relative_grading.methods.q_factor import QFactor
from relative_grading.methods.median_mad import MedianMAD
from relative_grading.grading import assign_grade
from relative_grading.validation.equations import validate_analytical_fixtures


def test_analytical_fixtures():
    assert validate_analytical_fixtures() is True


def test_methods_boundary_shape_and_order():
    scores = np.linspace(30, 90, 50)
    ce = 25.0

    methods = [MeanSD(), Percentile(), MaxMin(), QFactor(), MedianMAD()]

    for m in methods:
        b = m.calculate_boundaries(scores, ce)
        assert len(b) == 7, f"{m.name} did not return 7 boundaries"
        # B7 should be >= CE
        assert b[6] >= ce, f"{m.name} B7 ({b[6]}) is less than CE ({ce})"
        # B1 should be the highest boundary
        assert b[0] >= b[1], f"{m.name} B1 < B2"


def test_exact_boundary_rule():
    # Exact boundary receives higher grade
    b = np.array([80.0, 70.0, 60.0, 50.0, 40.0, 30.0, 20.0])

    assert assign_grade(80.0, b) == 1
    assert assign_grade(79.99, b) == 2
    assert assign_grade(70.0, b) == 2
    assert assign_grade(69.99, b) == 3
    assert assign_grade(20.0, b) == 7
    assert assign_grade(19.99, b) == 8
