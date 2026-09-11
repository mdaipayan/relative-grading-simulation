"""Unit tests for external competency constraint filtering and enforcement."""

import numpy as np
import pytest
from relative_grading.eligibility import get_eligible_pool
from relative_grading.grading import assign_grade


def test_competency_filtering():
    internal = np.array([50.0, 60.0, 70.0, 80.0])
    external = np.array([15.0, 22.0, 28.0, 18.0])
    total = 0.4 * internal + 0.6 * external
    ce = 20.0

    elig = get_eligible_pool(internal, external, total, ce=ce)

    # Only indices 1 (22.0) and 2 (28.0) have external >= 20.0
    assert elig.eligible_n == 2
    assert elig.ineligible_n == 2
    assert elig.eligibility_rate == 0.5
    assert np.all(elig.mask == np.array([False, True, True, False]))
    assert len(elig.eligible_scores) == 2


def test_external_fail_gives_grade_8():
    # Student with total score 90.0 but external score 15.0 with CE = 20.0
    boundaries = np.array([80.0, 70.0, 60.0, 50.0, 40.0, 30.0, 20.0])
    grade = assign_grade(score=90.0, boundaries=boundaries, external=15.0, ce=20.0)
    assert grade == 8, "Student with external < CE must receive Grade 8 (F)"

    # Student with external score 25.0 >= CE receives Grade 1
    grade_pass = assign_grade(score=90.0, boundaries=boundaries, external=25.0, ce=20.0)
    assert grade_pass == 1
