"""Abstract base class for relative grading methods."""

from abc import ABC, abstractmethod
import numpy as np


class GradingMethod(ABC):
    """Abstract base class representing a relative grading scheme."""
    name: str

    @abstractmethod
    def calculate_boundaries(
        self,
        scores: np.ndarray,
        competency_threshold: float,
    ) -> np.ndarray:
        """Calculate the 7 grade boundaries from eligible student scores.

        Parameters
        ----------
        scores : np.ndarray
            Array of eligible cohort composite scores X.
        competency_threshold : float
            External competency threshold CE.

        Returns
        -------
        np.ndarray
            Array of 7 boundaries: [B1, B2, B3, B4, B5, B6, B7*] in descending order.
        """
        pass
