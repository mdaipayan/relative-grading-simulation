"""Score distribution generators for relative grading simulation.

Implements the 6 frozen marginal distributions:
1. Normal: clip(60 + 15*Z, 0, 100)
2. Compressed Normal: clip(60 + 5*Z, 0, 100)
3. Uniform: U(0, 100)
4. Right-skewed: 100 * Beta(2, 5)
5. Left-skewed: 100 * Beta(5, 2)
6. Bimodal: 50/50 mixture of 100*Beta(2, 5) and 100*Beta(5, 2)
"""

from typing import Union
import numpy as np

DISTRIBUTIONS = [
    "Normal",
    "Compressed Normal",
    "Uniform",
    "Right-skewed",
    "Left-skewed",
    "Bimodal",
]


def generate_scores(
    distribution: str,
    n: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate n synthetic test scores from the specified target distribution.

    Parameters
    ----------
    distribution : str
        One of the 6 frozen distribution names.
    n : int
        Number of scores to generate.
    rng : np.random.Generator
        Deterministic numpy random generator instance.

    Returns
    -------
    np.ndarray
        Array of shape (n,) with scores in [0, 100].
    """
    if n <= 0:
        return np.empty(0, dtype=float)

    dist_normalized = distribution.strip()

    if dist_normalized == "Normal":
        z = rng.standard_normal(size=n)
        scores = 60.0 + 15.0 * z
        return np.clip(scores, 0.0, 100.0)

    elif dist_normalized in ("Compressed", "Compressed Normal"):
        z = rng.standard_normal(size=n)
        scores = 60.0 + 5.0 * z
        return np.clip(scores, 0.0, 100.0)

    elif dist_normalized == "Uniform":
        scores = rng.uniform(0.0, 100.0, size=n)
        return np.clip(scores, 0.0, 100.0)

    elif dist_normalized == "Right-skewed":
        raw = rng.beta(2.0, 5.0, size=n)
        return np.clip(100.0 * raw, 0.0, 100.0)

    elif dist_normalized == "Left-skewed":
        raw = rng.beta(5.0, 2.0, size=n)
        return np.clip(100.0 * raw, 0.0, 100.0)

    elif dist_normalized == "Bimodal":
        # 50/50 mixture of Beta(2,5) and Beta(5,2)
        selector = rng.random(size=n) < 0.5
        raw1 = rng.beta(2.0, 5.0, size=n)
        raw2 = rng.beta(5.0, 2.0, size=n)
        raw = np.where(selector, raw1, raw2)
        return np.clip(100.0 * raw, 0.0, 100.0)

    else:
        raise ValueError(
            f"Unknown distribution '{distribution}'. "
            f"Allowed: {DISTRIBUTIONS}"
        )
