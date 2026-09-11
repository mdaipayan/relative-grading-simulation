"""M2 — Percentile grading method.

Calibrated to M1 using empirical Hyndman-Fan Type 7 quantiles:
p = [0.933193, 0.841345, 0.691462, 0.500000, 0.308538, 0.158655, 0.066807]
Final P/F: B7* = max(B7, CE)
"""

import numpy as np
from relative_grading.methods.base import GradingMethod


class Percentile(GradingMethod):
    name: str = "Percentile"
    percentiles = np.array(
        [0.933193, 0.841345, 0.691462, 0.500000, 0.308538, 0.158655, 0.066807],
        dtype=float,
    )

    def calculate_boundaries(
        self,
        scores: np.ndarray,
        competency_threshold: float,
    ) -> np.ndarray:
        n = len(scores)
        if n == 0:
            return np.full(7, competency_threshold, dtype=float)
        elif n == 1:
            boundaries = np.full(7, float(scores[0]))
        else:
            sorted_x = np.sort(scores)
            idx = (n - 1) * self.percentiles
            j = np.floor(idx).astype(int)
            g = idx - j
            j_next = np.minimum(j + 1, n - 1)
            boundaries = (1.0 - g) * sorted_x[j] + g * sorted_x[j_next]

        # Competency overlay
        boundaries[6] = max(boundaries[6], float(competency_threshold))

        return boundaries
