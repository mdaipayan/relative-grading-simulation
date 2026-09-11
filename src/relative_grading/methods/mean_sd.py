"""M1 — Mean-SD grading method.

For eligible estimation scores:
B_j = mu + k_j * s
where k = [1.5, 1.0, 0.5, 0, -0.5, -1.0, -1.5]
sample SD with ddof=1
Final P/F:
B7* = max(mu - 1.5*s, CE)
"""

import numpy as np
from relative_grading.methods.base import GradingMethod


class MeanSD(GradingMethod):
    name: str = "MeanSD"
    k_vector = np.array([1.5, 1.0, 0.5, 0.0, -0.5, -1.0, -1.5], dtype=float)

    def calculate_boundaries(
        self,
        scores: np.ndarray,
        competency_threshold: float,
    ) -> np.ndarray:
        n = len(scores)
        if n == 0:
            return np.full(7, competency_threshold, dtype=float)
        elif n == 1:
            mu = float(scores[0])
            s = 0.0
        else:
            mu = float(np.mean(scores))
            s = float(np.std(scores, ddof=1))

        # Raw boundaries B1 to B7
        boundaries = mu + self.k_vector * s

        # Apply external competency overlay to B7 (Final P/F boundary)
        boundaries[6] = max(boundaries[6], float(competency_threshold))

        return boundaries
