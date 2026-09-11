"""Unit test for deterministic reproducibility under fixed seeds."""

import numpy as np
from relative_grading.assessment import generate_assessment
from relative_grading.contamination import contaminate
from relative_grading.methods.mean_sd import MeanSD


def test_stream_determinism():
    # Two runs with identical seeds must produce bitwise identical assessments and boundaries
    seed = 777777

    rng1 = np.random.default_rng(seed)
    cohort1 = generate_assessment(n=30, distribution="Normal", rho=0.60, rng=rng1)
    contam1 = contaminate(cohort1.internal, cohort1.external, epsilon=0.05, direction="lower", rng=rng1)

    rng2 = np.random.default_rng(seed)
    cohort2 = generate_assessment(n=30, distribution="Normal", rho=0.60, rng=rng2)
    contam2 = contaminate(cohort2.internal, cohort2.external, epsilon=0.05, direction="lower", rng=rng2)

    np.testing.assert_array_equal(cohort1.internal, cohort2.internal)
    np.testing.assert_array_equal(cohort1.external, cohort2.external)
    np.testing.assert_array_equal(cohort1.total, cohort2.total)

    np.testing.assert_array_equal(contam1.total, contam2.total)
    np.testing.assert_array_equal(contam1.perturbed_indices, contam2.perturbed_indices)

    m1 = MeanSD()
    b1 = m1.calculate_boundaries(contam1.total, competency_threshold=20.0)
    b2 = m1.calculate_boundaries(contam2.total, competency_threshold=20.0)
    np.testing.assert_array_equal(b1, b2)
