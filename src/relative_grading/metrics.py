"""Primary and secondary metric calculation engine.

Implements:
- Primary stability: stability(x) = max_g p_g(x), mean_grid_stability over x=0,...,100
- Reference disagreement: proportion of replications where grade(x) != ref_grade(x)
- Boundary displacement: mean(abs(B_rep - B_ref))
- Boundary RMSE: sqrt(mean((B_rep - B_ref)^2))
- Pass-rate variability: SD of pass rate across replications
- Grade-count variability: mean SD of grade distribution across replications
- Competency override rate
- Feasibility flag and tracking
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import numpy as np


@dataclass(frozen=True)
class CellMethodMetrics:
    """Consolidated metrics for a single method within an experimental cell across R replications."""
    method_name: str
    mean_grid_stability: float
    reference_disagreement: float
    mean_boundary_displacement: float
    boundary_rmse: float
    pass_rate_mean: float
    pass_rate_sd: float
    grade_count_sd_mean: float
    competency_override_rate: float
    infeasible_replications: int
    total_replications: int


def calculate_grid_metrics(
    replications_grid_grades: np.ndarray,  # shape (R, 101), values in 1..8
    reference_grid_grades: np.ndarray,     # shape (101,), values in 1..8
) -> Tuple[float, float, np.ndarray, np.ndarray]:
    """Calculate mean grid stability and reference disagreement across R replications.

    Parameters
    ----------
    replications_grid_grades : np.ndarray
        Shape (R, 101) array of grades assigned to integer grid x = 0..100 across R reps.
    reference_grid_grades : np.ndarray
        Shape (101,) array of clean reference grades for integer grid x = 0..100.

    Returns
    -------
    mean_grid_stability : float
        Mean over 101 grid points of max_g p_g(x).
    mean_ref_disagreement : float
        Mean over 101 grid points of disagreement rate with reference.
    pointwise_stability : np.ndarray
        Shape (101,) array of stability(x).
    pointwise_disagreement : np.ndarray
        Shape (101,) array of disagreement(x).
    """
    r, grid_size = replications_grid_grades.shape

    # For each grid point x and grade g in 1..8, compute proportion p_g(x)
    pointwise_stability = np.zeros(grid_size, dtype=float)
    for x in range(grid_size):
        grades_at_x = replications_grid_grades[:, x]
        # Count occurrences of each grade 1..8
        counts = np.bincount(grades_at_x, minlength=9)[1:9]
        p_g = counts / float(r)
        pointwise_stability[x] = np.max(p_g)

    mean_grid_stability = float(np.mean(pointwise_stability))

    # Reference disagreement
    disagreements = (replications_grid_grades != reference_grid_grades[None, :])
    pointwise_disagreement = np.mean(disagreements, axis=0)
    mean_ref_disagreement = float(np.mean(pointwise_disagreement))

    return mean_grid_stability, mean_ref_disagreement, pointwise_stability, pointwise_disagreement


def calculate_boundary_metrics(
    replications_boundaries: np.ndarray,  # shape (R, 7)
    reference_boundaries: np.ndarray,     # shape (7,)
) -> Tuple[float, float]:
    """Calculate mean absolute boundary displacement and boundary RMSE.

    Parameters
    ----------
    replications_boundaries : np.ndarray
        Shape (R, 7) array of computed boundaries across R replications.
    reference_boundaries : np.ndarray
        Shape (7,) array of reference boundaries.

    Returns
    -------
    mean_displacement : float
        Mean absolute displacement over all boundaries and replications.
    boundary_rmse : float
        Root mean square error over all boundaries and replications.
    """
    diff = replications_boundaries - reference_boundaries[None, :]
    mean_displacement = float(np.mean(np.abs(diff)))
    boundary_rmse = float(np.sqrt(np.mean(diff ** 2)))
    return mean_displacement, boundary_rmse


def calculate_secondary_metrics(
    cohort_grades: np.ndarray,      # shape (R, N)
    cohort_external: np.ndarray,    # shape (R, N)
    cohort_total: np.ndarray,       # shape (R, N)
    native_b7: np.ndarray,          # shape (R,)
    ce: float,
) -> Tuple[float, float, float, float]:
    """Calculate pass rate mean, pass rate SD, grade count variability, and competency override rate.

    Parameters
    ----------
    cohort_grades : np.ndarray
        Grades assigned to actual cohort students across R replications (shape R, N).
    cohort_external : np.ndarray
        External scores E of cohort students (shape R, N).
    cohort_total : np.ndarray
        Total scores X of cohort students (shape R, N).
    native_b7 : np.ndarray
        Native unconstrained method pass/fail boundary for each replication (shape R,).
    ce : float
        Competency threshold.

    Returns
    -------
    pass_rate_mean : float
    pass_rate_sd : float
    grade_count_sd_mean : float
    competency_override_rate : float
    """
    r, n = cohort_grades.shape

    # Passing is defined as grade in {1..7} (i.e. grade < 8)
    passing_mask = (cohort_grades < 8)
    pass_rates = np.mean(passing_mask, axis=1)
    pass_rate_mean = float(np.mean(pass_rates))
    pass_rate_sd = float(np.std(pass_rates, ddof=1)) if r > 1 else 0.0

    # Grade count variability: SD of grade proportions across replications
    # For each grade g in 1..8:
    grade_props = np.zeros((r, 8), dtype=float)
    for rep in range(r):
        counts = np.bincount(cohort_grades[rep], minlength=9)[1:9]
        grade_props[rep] = counts / float(n)
    grade_count_sds = np.std(grade_props, axis=0, ddof=1) if r > 1 else np.zeros(8)
    grade_count_sd_mean = float(np.mean(grade_count_sds))

    # Competency override rate:
    # Students who met native passing condition (X >= native_b7) but failed external competency (E < CE)
    # native_b7 is shape (R,) -> broadcast against cohort_total (R, N)
    met_native_passing = (cohort_total >= native_b7[:, None])
    failed_competency = (cohort_external < ce)
    override_students = (met_native_passing & failed_competency)
    competency_override_rate = float(np.mean(override_students))

    return pass_rate_mean, pass_rate_sd, grade_count_sd_mean, competency_override_rate

