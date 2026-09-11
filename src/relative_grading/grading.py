"""Authoritative grade assignment module.

Rule:
Exact boundary receives the higher grade.
Boundaries are: [B1, B2, B3, B4, B5, B6, B7*] in descending order.

Grades:
1: Score >= B1 (highest grade)
2: B2 <= Score < B1
3: B3 <= Score < B2
4: B4 <= Score < B3
5: B5 <= Score < B4
6: B6 <= Score < B5
7: B7* <= Score < B6 (lowest passing grade)
8: Score < B7* (Fail / F)

If external competency condition is checked:
External < CE => Grade 8 (F) unconditionally.
"""

from typing import Union, Optional
import numpy as np


def assign_grade(
    score: Union[float, int, np.ndarray],
    boundaries: np.ndarray,
    external: Optional[Union[float, int, np.ndarray]] = None,
    ce: Optional[float] = None,
) -> Union[int, np.ndarray]:
    """Assign integer grade (1 to 8) to score(s) according to the frozen boundaries.

    Parameters
    ----------
    score : float or np.ndarray
        Composite assessment score(s) X.
    boundaries : np.ndarray
        Array of 7 boundaries [B1, B2, B3, B4, B5, B6, B7*].
    external : float or np.ndarray, optional
        External assessment score(s) E. If provided with ce, E < ce receives 8 (F).
    ce : float, optional
        External competency threshold CE.

    Returns
    -------
    int or np.ndarray
        Integer grade(s) in {1, 2, 3, 4, 5, 6, 7, 8}, where 1 is top grade and 8 is Fail.
    """
    is_scalar = np.isscalar(score)
    s = np.atleast_1d(np.asarray(score, dtype=float))

    # Sort boundaries ascending: [b7, b6, b5, b4, b3, b2, b1]
    b_asc = np.sort(boundaries[:7])
    idx = np.searchsorted(b_asc, s, side="right")
    grades = np.where(idx == 0, 8, 8 - idx)

    # Apply external competency constraint if external and ce are provided
    if external is not None and ce is not None:
        ext = np.atleast_1d(np.asarray(external, dtype=float))
        grades[ext < ce] = 8

    return int(grades[0]) if is_scalar else grades
