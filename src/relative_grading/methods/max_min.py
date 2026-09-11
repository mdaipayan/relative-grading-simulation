"""M3 — Fixed Distribution / Max-Min grading method.

For eligible scores:
Delta = (Xmax - Xmin) / 7
Bj = Xmax - j*Delta, j=1,...,6
B7 = Xmin
Competency overlay:
B7* = max(Xmin, CE)
"""

import numpy as np
from relative_grading.methods.base import GradingMethod


class MaxMin(GradingMethod):
    name: str = "MaxMin"

    def calculate_boundaries(
        self,
        scores: np.ndarray,
        competency_threshold: float,
    ) -> np.ndarray:
        n = len(scores)
        if n == 0:
            return np.full(7, competency_threshold, dtype=float)

        x_max = float(np.max(scores))
        x_min = float(np.min(scores))

        delta = (x_max - x_min) / 7.0

        boundaries = np.zeros(7, dtype=float)
        for j in range(1, 7):
            boundaries[j - 1] = x_max - j * delta

        # B7 is Xmin
        b7 = x_min
        # Competency overlay
        boundaries[6] = max(b7, float(competency_threshold))

        return boundaries
