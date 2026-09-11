"""Eligibility filtering module based on external competency constraint (CE).

Rule:
Students with External Score E < CE fail the external competency requirement (E < CE => F).
These ineligible students receive grade F directly and are excluded from the
relative-grading estimation pool.
"""

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class EligibilityResult:
    """Structure containing results of competency filtering."""
    mask: np.ndarray          # Boolean mask: True for eligible (E >= CE), False otherwise
    eligible_scores: np.ndarray  # Total scores X for eligible students
    eligible_n: int           # Count of eligible students
    ineligible_n: int         # Count of ineligible students
    eligibility_rate: float   # Fraction eligible (eligible_n / total_n)


def get_eligible_pool(
    internal: np.ndarray,
    external: np.ndarray,
    total: np.ndarray,
    ce: float,
) -> EligibilityResult:
    """Filter cohort to identify students meeting external competency threshold CE.

    Parameters
    ----------
    internal : np.ndarray
        Array of internal scores I.
    external : np.ndarray
        Array of external scores E.
    total : np.ndarray
        Array of composite scores X.
    ce : float
        External competency threshold in percentage [0, 100].

    Returns
    -------
    EligibilityResult
        Structure with eligibility mask, eligible scores, counts, and rate.
    """
    total_n = len(external)
    if total_n == 0:
        return EligibilityResult(
            mask=np.empty(0, dtype=bool),
            eligible_scores=np.empty(0, dtype=float),
            eligible_n=0,
            ineligible_n=0,
            eligibility_rate=0.0,
        )

    # E >= CE qualifies for relative grading estimation pool
    mask = (external >= ce)
    eligible_scores = total[mask]
    eligible_n = int(np.sum(mask))
    ineligible_n = total_n - eligible_n
    eligibility_rate = float(eligible_n / total_n)

    return EligibilityResult(
        mask=mask,
        eligible_scores=eligible_scores,
        eligible_n=eligible_n,
        ineligible_n=ineligible_n,
        eligibility_rate=eligibility_rate,
    )
