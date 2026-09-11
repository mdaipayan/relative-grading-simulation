"""Automated unit test for M1 / M1-C equivalence.

Protocol (Section 18):
- 1,800/1,800 matched pilot replications identical
- maximum absolute boundary difference = 0
- 0 grade mismatches
- competency false-pass rate = 0
"""

import pytest
from relative_grading.validation.equivalence import verify_m1_equivalence


def test_m1_m1c_exact_equivalence():
    result = verify_m1_equivalence(n_replications=1800, seed=42)
    assert result.replications_tested == 1800
    assert result.replications_identical == 1800
    assert result.max_boundary_diff == 0.0
    assert result.grade_mismatches == 0
    assert result.competency_false_pass_count == 0
    assert result.passed is True
