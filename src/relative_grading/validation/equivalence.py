"""Validation module for M1 / M1-C equivalence verification.

Protocol:
M1-C is NOT a distinct method; it is the frozen M1 with competency constraint.
Verification requires:
- 1,800/1,800 matched pilot replications identical
- maximum absolute boundary difference = 0.0
- 0 grade mismatches
- competency false-pass rate = 0.0
"""

from dataclasses import dataclass
import numpy as np
from relative_grading.distributions import generate_scores
from relative_grading.assessment import generate_assessment
from relative_grading.eligibility import get_eligible_pool
from relative_grading.methods.mean_sd import MeanSD
from relative_grading.grading import assign_grade


@dataclass(frozen=True)
class EquivalenceResult:
    """Audit result for M1 / M1-C equivalence check."""
    replications_tested: int
    replications_identical: int
    max_boundary_diff: float
    grade_mismatches: int
    competency_false_pass_count: int
    passed: bool


def verify_m1_equivalence(
    n_replications: int = 1800,
    seed: int = 12345,
) -> EquivalenceResult:
    """Verify that M1 with frozen competency overlay produces zero discrepancy across test replications.

    Parameters
    ----------
    n_replications : int, default=1800
        Number of matched replications to test.
    seed : int, default=12345
        Random seed for test cohort generation.

    Returns
    -------
    EquivalenceResult
        Summary of equivalence audit.
    """
    rng = np.random.default_rng(seed)
    m1 = MeanSD()

    identical_count = 0
    max_diff = 0.0
    grade_mismatches = 0
    false_passes = 0

    test_sizes = [10, 20, 50, 100]
    test_dists = ["Normal", "Compressed Normal", "Uniform", "Right-skewed", "Left-skewed", "Bimodal"]
    test_ces = [10.0, 15.0, 20.0, 25.0, 30.0]

    reps_per_condition = max(1, n_replications // (len(test_sizes) * len(test_dists) * len(test_ces)))

    actual_tested = 0

    for n in test_sizes:
        for dist in test_dists:
            for ce in test_ces:
                for _ in range(reps_per_condition):
                    if actual_tested >= n_replications:
                        break
                    actual_tested += 1

                    # Generate cohort
                    cohort = generate_assessment(n=n, distribution=dist, rho=0.60, rng=rng)

                    # Approach A: Method calculation on eligible pool
                    elig = get_eligible_pool(cohort.internal, cohort.external, cohort.total, ce=ce)
                    b_a = m1.calculate_boundaries(elig.eligible_scores, competency_threshold=ce)

                    # Approach B: Explicit formulation
                    if elig.eligible_n >= 2:
                        mu = float(np.mean(elig.eligible_scores))
                        s = float(np.std(elig.eligible_scores, ddof=1))
                        b_b = mu + m1.k_vector * s
                        b_b[6] = max(b_b[6], ce)
                    elif elig.eligible_n == 1:
                        b_b = np.full(7, elig.eligible_scores[0])
                        b_b[6] = max(b_b[6], ce)
                    else:
                        b_b = np.full(7, ce)

                    diff = np.max(np.abs(b_a - b_b))
                    if diff > max_diff:
                        max_diff = diff

                    # Grades on cohort
                    g_a = assign_grade(cohort.total, b_a, external=cohort.external, ce=ce)
                    g_b = assign_grade(cohort.total, b_b, external=cohort.external, ce=ce)

                    mismatches = np.sum(g_a != g_b)
                    grade_mismatches += int(mismatches)

                    # False pass check: any student with external < ce having grade != 8
                    ineligible_passed = np.sum((cohort.external < ce) & (g_a != 8))
                    false_passes += int(ineligible_passed)

                    if diff == 0.0 and mismatches == 0 and ineligible_passed == 0:
                        identical_count += 1

    passed = (
        identical_count == actual_tested
        and max_diff == 0.0
        and grade_mismatches == 0
        and false_passes == 0
    )

    return EquivalenceResult(
        replications_tested=actual_tested,
        replications_identical=identical_count,
        max_boundary_diff=max_diff,
        grade_mismatches=grade_mismatches,
        competency_false_pass_count=false_passes,
        passed=passed,
    )
