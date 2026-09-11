"""Assessment generation module for relative grading simulation.

Implements the frozen assessment score construction:
S ~ target distribution
T ~ target distribution (independent of S)
I = S
E = a*S + (1-a)*T, where a = 3/7 for primary rho=0.60
E = clip(E, 0, 100)
X = 0.40*I + 0.60*E

Retains I, E, and aggregate X.
"""

from dataclasses import dataclass
import numpy as np
from relative_grading.distributions import generate_scores


@dataclass(frozen=True)
class AssessmentScores:
    """Container for multi-component assessment scores."""
    internal: np.ndarray  # I
    external: np.ndarray  # E
    total: np.ndarray     # X


def get_a_parameter_for_rho(rho: float) -> float:
    """Compute the mixture weight 'a' corresponding to target pre-clipping correlation rho.

    Under E = a*S + (1-a)*T with independent, equal-variance S and T:
    Corr(S, E) = a / sqrt(a^2 + (1-a)^2) = rho.
    The analytical solution is:
    a = rho / (rho + sqrt(1 - rho^2)) for 0 <= rho <= 1.
    For rho = 0.60, this evaluates exactly to 3/7.
    """
    if rho <= 0.0:
        return 0.0
    if rho >= 1.0:
        return 1.0
    if abs(rho - 0.60) < 1e-6:
        return 3.0 / 7.0

    sqrt_term = np.sqrt(1.0 - rho ** 2)
    return float(rho / (rho + sqrt_term))


def generate_assessment(
    n: int,
    distribution: str,
    rho: float = 0.60,
    rng: np.random.Generator = None,
    weight_internal: float = 0.40,
    weight_external: float = 0.60,
) -> AssessmentScores:
    """Generate internal (I), external (E), and composite (X) scores for a cohort of size n.

    Parameters
    ----------
    n : int
        Cohort size.
    distribution : str
        Target marginal score distribution name.
    rho : float, default=0.60
        Target correlation between internal and external scores (primary model: 0.60 -> a=3/7).
    rng : np.random.Generator
        Deterministic numpy random generator.
    weight_internal : float, default=0.40
        Weight of internal component in total score.
    weight_external : float, default=0.60
        Weight of external component in total score.

    Returns
    -------
    AssessmentScores
        Named structure containing internal (I), external (E), and composite (X) scores.
    """
    if rng is None:
        rng = np.random.default_rng()

    # Draw S and T independently from target distribution
    s = generate_scores(distribution, n, rng)
    t = generate_scores(distribution, n, rng)

    # I = S
    internal = s.copy()

    # E = a*S + (1-a)*T
    a = get_a_parameter_for_rho(rho)
    external_raw = a * s + (1.0 - a) * t
    external = np.clip(external_raw, 0.0, 100.0)

    # X = 0.40*I + 0.60*E
    total = np.clip(
        weight_internal * internal + weight_external * external,
        0.0,
        100.0,
    )

    return AssessmentScores(internal=internal, external=external, total=total)
