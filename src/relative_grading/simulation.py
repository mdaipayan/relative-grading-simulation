"""High-performance primary simulation engine.

Executes the frozen Step 7D experimental factorial:
10 cohort sizes x 6 distributions x 5 CE x 7 contamination conditions = 2,100 cells.
R replications per cell (frozen protocol: R = 1,000).
Deterministic hierarchical RNG: master_seed -> cell_seed -> rep_seed.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
import time
import numpy as np
import pandas as pd

from relative_grading.distributions import generate_scores
from relative_grading.assessment import generate_assessment, get_a_parameter_for_rho
from relative_grading.eligibility import get_eligible_pool
from relative_grading.contamination import contaminate
from relative_grading.methods.mean_sd import MeanSD
from relative_grading.methods.percentile import Percentile
from relative_grading.methods.max_min import MaxMin
from relative_grading.methods.q_factor import QFactor
from relative_grading.methods.median_mad import MedianMAD
from relative_grading.grading import assign_grade
from relative_grading.reference import ReferenceCohortManager
from relative_grading.metrics import (
    calculate_grid_metrics,
    calculate_boundary_metrics,
    calculate_secondary_metrics,
)


@dataclass(frozen=True)
class CellSpec:
    """Specification of an experimental cell."""
    cell_id: int
    n: int
    distribution: str
    ce: float
    epsilon: float
    direction: str
    rho: float = 0.60


def build_primary_cell_grid(
    cohort_sizes: List[int],
    distributions: List[str],
    competency_thresholds: List[float],
    epsilons: List[float],
) -> List[CellSpec]:
    """Construct the full 2,100-cell experimental factorial design."""
    cells: List[CellSpec] = []
    cell_id = 0

    for n in cohort_sizes:
        for dist in distributions:
            for ce in competency_thresholds:
                for eps in epsilons:
                    if eps == 0.0:
                        cells.append(
                            CellSpec(
                                cell_id=cell_id,
                                n=n,
                                distribution=dist,
                                ce=ce,
                                epsilon=0.0,
                                direction="clean",
                                rho=0.60,
                            )
                        )
                        cell_id += 1
                    else:
                        for direction in ["lower", "upper"]:
                            cells.append(
                                CellSpec(
                                    cell_id=cell_id,
                                    n=n,
                                    distribution=dist,
                                    ce=ce,
                                    epsilon=eps,
                                    direction=direction,
                                    rho=0.60,
                                )
                            )
                            cell_id += 1

    return cells


def run_cell_simulation(
    cell: CellSpec,
    r_replications: int,
    master_seed: int,
    ref_manager: ReferenceCohortManager,
) -> List[Dict[str, Any]]:
    """Execute R replications for an experimental cell across all 5 grading methods.

    Parameters
    ----------
    cell : CellSpec
        Specification of the cell condition.
    r_replications : int
        Number of replications (e.g. 1000).
    master_seed : int
        Master random seed.
    ref_manager : ReferenceCohortManager
        Reference baseline manager.

    Returns
    -------
    List[Dict[str, Any]]
        List of 5 summary dicts (one per method) containing all cell identifiers and metrics.
    """
    # Deterministic cell seed derived from master_seed and cell_id
    cell_seed = int((hash((master_seed, cell.cell_id)) & 0x7FFFFFFF))
    rng = np.random.default_rng(cell_seed)

    grid = np.arange(0, 101, dtype=float)
    if isinstance(ref_manager, dict):
        key = (cell.distribution, float(cell.ce), float(cell.rho))
        ref_baselines = ref_manager[key]
    else:
        ref_baselines = ref_manager.get_reference(cell.distribution, cell.ce, rho=cell.rho)

    methods = {
        "MeanSD": MeanSD(),
        "Percentile": Percentile(),
        "MaxMin": MaxMin(),
        "QFactor": QFactor(),
        "MedianMAD": MedianMAD(),
    }

    # Pre-allocate storage for each method across R replications
    # Boundaries: (R, 7)
    # Grid grades: (R, 101)
    # Cohort grades: (R, N)
    # Native B7: (R,)
    rep_boundaries: Dict[str, np.ndarray] = {
        m: np.zeros((r_replications, 7), dtype=float) for m in methods
    }
    rep_grid_grades: Dict[str, np.ndarray] = {
        m: np.zeros((r_replications, 101), dtype=int) for m in methods
    }
    rep_cohort_grades: Dict[str, np.ndarray] = {
        m: np.zeros((r_replications, cell.n), dtype=int) for m in methods
    }
    native_b7s: Dict[str, np.ndarray] = {
        m: np.zeros(r_replications, dtype=float) for m in methods
    }
    infeasible_counts: Dict[str, int] = {m: 0 for m in methods}

    cohort_externals = np.zeros((r_replications, cell.n), dtype=float)
    cohort_totals = np.zeros((r_replications, cell.n), dtype=float)
    actual_m_total = 0

    # Execute R replications
    for rep in range(r_replications):
        # Generate base assessment
        cohort = generate_assessment(
            n=cell.n,
            distribution=cell.distribution,
            rho=cell.rho,
            rng=rng,
        )

        # Apply contamination / perturbation
        contam = contaminate(
            internal=cohort.internal,
            external=cohort.external,
            epsilon=cell.epsilon,
            direction=cell.direction,
            rng=rng,
        )
        actual_m_total += contam.actual_m

        cohort_externals[rep, :] = contam.external
        cohort_totals[rep, :] = contam.total

        # Filter eligible pool
        elig = get_eligible_pool(contam.internal, contam.external, contam.total, ce=cell.ce)

        # Check feasibility
        is_feasible = (elig.eligible_n >= 2)

        for m_name, method in methods.items():
            if not is_feasible:
                infeasible_counts[m_name] += 1

            # Compute boundaries
            b = method.calculate_boundaries(elig.eligible_scores, competency_threshold=cell.ce)
            rep_boundaries[m_name][rep, :] = b

            # Store native B7 (pre-competency constraint)
            if m_name == "MeanSD":
                if elig.eligible_n >= 2:
                    mu = float(np.mean(elig.eligible_scores))
                    s = float(np.std(elig.eligible_scores, ddof=1))
                    native_b7s[m_name][rep] = mu - 1.5 * s
                else:
                    native_b7s[m_name][rep] = cell.ce
            elif m_name == "Percentile":
                if elig.eligible_n >= 1:
                    native_b7s[m_name][rep] = float(np.quantile(elig.eligible_scores, 0.066807, method="linear"))
                else:
                    native_b7s[m_name][rep] = cell.ce
            elif m_name == "MaxMin":
                native_b7s[m_name][rep] = float(np.min(elig.eligible_scores)) if elig.eligible_n >= 1 else cell.ce
            elif m_name == "QFactor":
                native_b7s[m_name][rep] = cell.ce
            elif m_name == "MedianMAD":
                if elig.eligible_n >= 2:
                    med = float(np.median(elig.eligible_scores))
                    mad = float(np.median(np.abs(elig.eligible_scores - med)))
                    native_b7s[m_name][rep] = med - 1.5 * (1.4826 * mad)
                else:
                    native_b7s[m_name][rep] = cell.ce

            # Assign grades on integer grid 0..100
            rep_grid_grades[m_name][rep, :] = assign_grade(grid, b)

            # Assign grades on actual cohort students
            rep_cohort_grades[m_name][rep, :] = assign_grade(
                contam.total,
                b,
                external=contam.external,
                ce=cell.ce,
            )

    # Compute metrics for each method
    mean_actual_m = actual_m_total / float(r_replications)
    results = []

    for m_name in methods:
        ref_b, ref_grid_g = ref_baselines[m_name]

        stab, ref_disag, _, _ = calculate_grid_metrics(
            rep_grid_grades[m_name],
            ref_grid_g,
        )
        mean_disp, b_rmse = calculate_boundary_metrics(
            rep_boundaries[m_name],
            ref_b,
        )
        p_mean, p_sd, gc_sd, override_rate = calculate_secondary_metrics(
            cohort_grades=rep_cohort_grades[m_name],
            cohort_external=cohort_externals,
            cohort_total=cohort_totals,
            native_b7=native_b7s[m_name],
            ce=cell.ce,
        )

        results.append({
            "cell_id": cell.cell_id,
            "N": cell.n,
            "distribution": cell.distribution,
            "CE": cell.ce,
            "epsilon": cell.epsilon,
            "direction": cell.direction,
            "rho": cell.rho,
            "method": m_name,
            "replications": r_replications,
            "requested_m": round(cell.epsilon * cell.n, 4),
            "actual_m": mean_actual_m,
            "mean_grid_stability": stab,
            "reference_disagreement": ref_disag,
            "mean_boundary_displacement": mean_disp,
            "boundary_rmse": b_rmse,
            "pass_rate_mean": p_mean,
            "pass_rate_sd": p_sd,
            "grade_count_sd_mean": gc_sd,
            "competency_override_rate": override_rate,
            "infeasible_count": infeasible_counts[m_name],
        })

    return results
