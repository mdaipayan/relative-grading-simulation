"""M5 — Median-MAD robust comparator grading method.

For eligible scores:
M = median(X)
MAD = median(abs(X - M))
sigma_R = 1.4826 * MAD
Bj = M + k_j * sigma_R (k = [1.5, 1.0, 0.5, 0, -0.5, -1.0, -1.5])
Final P/F:
B7* = max(M - 1.5*sigma_R, CE)
"""

import numpy as np
from relative_grading.methods.base import GradingMethod


class MedianMAD(GradingMethod):
    name: str = "MedianMAD"
    k_vector = np.array([1.5, 1.0, 0.5, 0.0, -0.5, -1.0, -1.5], dtype=float)

    def calculate_boundaries(
        self,
        scores: np.ndarray,
        competency_threshold: float,
    ) -> np.ndarray:
        n = len(scores)
        if n == 0:
            return np.full(7, competency_threshold, dtype=float)

        if n == 1:
            m = float(scores[0])
            mad = 0.0
            sigma_r = 0.0
        else:
            s = np.sort(scores)
            m = float(s[n // 2] if n % 2 == 1 else 0.5 * (s[n // 2 - 1] + s[n // 2]))
            dev = np.sort(np.abs(scores - m))
            mad = float(dev[n // 2] if n % 2 == 1 else 0.5 * (dev[n // 2 - 1] + dev[n // 2]))
            sigma_r = 1.4826 * mad

        # Boundaries B1 to B7
        boundaries = m + self.k_vector * sigma_r

        # Competency overlay
        boundaries[6] = max(boundaries[6], float(competency_threshold))

        return boundaries
