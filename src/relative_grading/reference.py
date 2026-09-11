"""Reference cohort module for large-sample benchmark boundaries.

Nref = 100,000
Calculates clean reference boundaries for each distribution, competency threshold CE,
and grading method on the integer score grid x = 0, 1, ..., 100.
"""

from typing import Dict, Tuple
import numpy as np
from relative_grading.assessment import generate_assessment
from relative_grading.eligibility import get_eligible_pool
from relative_grading.methods.base import GradingMethod
from relative_grading.methods.mean_sd import MeanSD
from relative_grading.methods.percentile import Percentile
from relative_grading.methods.max_min import MaxMin
from relative_grading.methods.q_factor import QFactor
from relative_grading.methods.median_mad import MedianMAD
from relative_grading.grading import assign_grade


class ReferenceCohortManager:
    """Manages computation and caching of large-sample (Nref = 100,000) reference baselines."""

    def __init__(self, n_ref: int = 100000, seed: int = 999999):
        self.n_ref = n_ref
        self.seed = seed
        self.methods: Dict[str, GradingMethod] = {
            "MeanSD": MeanSD(),
            "Percentile": Percentile(),
            "MaxMin": MaxMin(),
            "QFactor": QFactor(),
            "MedianMAD": MedianMAD(),
        }
        self.grid = np.arange(0, 101, dtype=float)
        # Cache key: (distribution, ce, rho) -> {method_name: (boundaries, grid_grades)}
        self._cache: Dict[Tuple[str, float, float], Dict[str, Tuple[np.ndarray, np.ndarray]]] = {}

    def get_reference(
        self,
        distribution: str,
        ce: float,
        rho: float = 0.60,
    ) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """Retrieve or compute reference boundaries and grid grades for a given condition.

        Parameters
        ----------
        distribution : str
            Target score distribution.
        ce : float
            External competency threshold CE.
        rho : float, default=0.60
            Assessment component correlation.

        Returns
        -------
        Dict[str, Tuple[np.ndarray, np.ndarray]]
            Map of method_name -> (boundaries_7, grid_grades_101).
        """
        key = (distribution, float(ce), float(rho))
        if key in self._cache:
            return self._cache[key]

        # Deterministic generation for reference
        # Unique seed per distribution/ce/rho condition derived from master ref seed
        cond_seed = int((hash(key) + self.seed) % (2**31 - 1))
        rng = np.random.default_rng(cond_seed)

        # Generate large reference assessment
        ref_cohort = generate_assessment(n=self.n_ref, distribution=distribution, rho=rho, rng=rng)
        elig = get_eligible_pool(ref_cohort.internal, ref_cohort.external, ref_cohort.total, ce=ce)

        res: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
        for m_name, method in self.methods.items():
            boundaries = method.calculate_boundaries(elig.eligible_scores, competency_threshold=ce)
            grid_grades = assign_grade(self.grid, boundaries)
            res[m_name] = (boundaries, grid_grades)

        self._cache[key] = res
        return res
