"""Validation suite for grading method equations and exact edge cases."""

import numpy as np
from relative_grading.methods.mean_sd import MeanSD
from relative_grading.methods.percentile import Percentile
from relative_grading.methods.max_min import MaxMin
from relative_grading.methods.q_factor import QFactor
from relative_grading.methods.median_mad import MedianMAD
from relative_grading.grading import assign_grade


def validate_analytical_fixtures() -> bool:
    """Validate all 5 methods on fixed, known analytical vectors."""
    # Test fixture: scores [40, 50, 60, 70, 80], CE = 30.0
    scores = np.array([40.0, 50.0, 60.0, 70.0, 80.0])
    ce = 30.0

    # 1. M1 Mean-SD
    # mu = 60.0, var = ((20^2 + 10^2 + 0 + 10^2 + 20^2) / 4) = 1000 / 4 = 250, s = sqrt(250) = 5*sqrt(10) ~ 15.8113883
    m1 = MeanSD()
    b_m1 = m1.calculate_boundaries(scores, ce)
    expected_mu = 60.0
    expected_s = float(np.std(scores, ddof=1))
    assert np.isclose(b_m1[3], expected_mu), "M1 median/mean boundary incorrect"
    assert np.isclose(b_m1[0], expected_mu + 1.5 * expected_s), "M1 B1 incorrect"
    assert np.isclose(b_m1[6], max(expected_mu - 1.5 * expected_s, ce)), "M1 B7 incorrect"

    # 2. M2 Percentile
    m2 = Percentile()
    b_m2 = m2.calculate_boundaries(scores, ce)
    # p = [0.933193, 0.841345, 0.691462, 0.5, 0.308538, 0.158655, 0.066807]
    assert np.isclose(b_m2[3], 60.0), "M2 median quantile incorrect"
    assert b_m2[6] >= ce, "M2 B7 below CE"

    # 3. M3 Max-Min
    # Xmax = 80, Xmin = 40, Delta = 40 / 7 = 5.7142857
    m3 = MaxMin()
    b_m3 = m3.calculate_boundaries(scores, ce)
    assert np.isclose(b_m3[0], 80.0 - 40.0 / 7.0), "M3 B1 incorrect"
    assert np.isclose(b_m3[5], 80.0 - 6.0 * (40.0 / 7.0)), "M3 B6 incorrect"
    assert np.isclose(b_m3[6], max(40.0, ce)), "M3 B7 incorrect"

    # 4. M4 Q-Factor
    # Qa = 30.0, Sa = 80.0, span = 50.0
    m4 = QFactor()
    b_m4 = m4.calculate_boundaries(scores, ce)
    assert np.isclose(b_m4[0], 30.0 + (6.0 / 7.0) * 50.0), "M4 B1 incorrect"
    assert np.isclose(b_m4[5], 30.0 + (1.0 / 7.0) * 50.0), "M4 B6 incorrect"
    assert np.isclose(b_m4[6], 30.0), "M4 B7 incorrect"

    # 5. M5 Median-MAD
    # M = 60.0, |X - M| = [20, 10, 0, 10, 20] -> sorted [0, 10, 10, 20, 20], median = 10.0
    # sigma_R = 1.4826 * 10 = 14.826
    m5 = MedianMAD()
    b_m5 = m5.calculate_boundaries(scores, ce)
    assert np.isclose(b_m5[3], 60.0), "M5 median incorrect"
    assert np.isclose(b_m5[0], 60.0 + 1.5 * 14.826), "M5 B1 incorrect"
    assert np.isclose(b_m5[6], max(60.0 - 1.5 * 14.826, ce)), "M5 B7 incorrect"

    # 6. Grade assignment exact boundary rule
    test_boundaries = np.array([85.0, 75.0, 65.0, 55.0, 45.0, 35.0, 25.0])
    # Exact boundary 85.0 must receive Grade 1
    assert assign_grade(85.0, test_boundaries) == 1, "Boundary value 85.0 did not receive Grade 1"
    assert assign_grade(84.99, test_boundaries) == 2, "Score 84.99 did not receive Grade 2"
    assert assign_grade(25.0, test_boundaries) == 7, "Boundary value 25.0 did not receive Grade 7"
    assert assign_grade(24.99, test_boundaries) == 8, "Score 24.99 did not receive Grade 8"

    return True
