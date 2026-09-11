"""M4 — Q-Factor / Constrained grading method.

Study-specific computational operationalization of the published Q-factor framework.
Qa = CE
Sa = Xmax
For j=1,...,6:
Bj = Qa + ((7-j)/7)*(Sa-Qa)
B7 = Qa = CE
"""

import numpy as np
from relative_grading.methods.base import GradingMethod


class QFactor(GradingMethod):
    name: str = "QFactor"

    def calculate_boundaries(
        self,
        scores: np.ndarray,
        competency_threshold: float,
    ) -> np.ndarray:
        qa = float(competency_threshold)
        n = len(scores)
        if n == 0:
            return np.full(7, qa, dtype=float)

        sa = float(np.max(scores))
        span = sa - qa

        boundaries = np.zeros(7, dtype=float)
        for j in range(1, 7):
            boundaries[j - 1] = qa + ((7 - j) / 7.0) * span

        boundaries[6] = qa  # B7 = Qa = CE

        return boundaries
