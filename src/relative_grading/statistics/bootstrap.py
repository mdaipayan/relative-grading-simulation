"""Paired bootstrap confidence intervals for mean paired differences."""

from typing import Tuple
import numpy as np


def paired_bootstrap_ci(
    diffs: np.ndarray,
    n_boot: int = 2000,
    alpha: float = 0.05,
    seed: int = 42,
) -> Tuple[float, float]:
    """Compute paired percentile bootstrap (1 - alpha)*100% confidence interval.

    Parameters
    ----------
    diffs : np.ndarray
        Array of paired differences across experimental cells.
    n_boot : int, default=2000
        Number of bootstrap resamples.
    alpha : float, default=0.05
        Significance level (default 0.05 -> 95% CI).
    seed : int, default=42
        Deterministic random seed.

    Returns
    -------
    ci_lower : float
    ci_upper : float
    """
    n = len(diffs)
    if n == 0:
        return 0.0, 0.0

    rng = np.random.default_rng(seed)
    # Resample with replacement
    indices = rng.integers(0, n, size=(n_boot, n))
    boot_means = np.mean(diffs[indices], axis=1)

    lower_p = 100.0 * (alpha / 2.0)
    upper_p = 100.0 * (1.0 - alpha / 2.0)

    ci_lower = float(np.percentile(boot_means, lower_p))
    ci_upper = float(np.percentile(boot_means, upper_p))

    return ci_lower, ci_upper
