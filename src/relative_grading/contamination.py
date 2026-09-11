"""Controlled score contamination / outlier perturbation module.

Rules:
lower -> U(0, 5)
upper -> U(95, 100)
m = round(epsilon * N)
Select m random positions without replacement and apply the perturbation to both
internal (I) and external (E) scores, then recompute aggregate composite score X.

Record:
- epsilon
- direction
- requested_m
- actual_m
- perturbed_indices
"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np


@dataclass(frozen=True)
class ContaminationResult:
    """Audit record for controlled score contamination / outlier perturbation."""
    internal: np.ndarray
    external: np.ndarray
    total: np.ndarray
    epsilon: float
    direction: str
    requested_m: float
    actual_m: int
    perturbed_indices: np.ndarray


def contaminate(
    internal: np.ndarray,
    external: np.ndarray,
    epsilon: float,
    direction: str,
    rng: np.random.Generator,
    weight_internal: float = 0.40,
    weight_external: float = 0.60,
) -> ContaminationResult:
    """Apply controlled score contamination / outlier perturbation to cohort scores.

    Parameters
    ----------
    internal : np.ndarray
        Original internal assessment scores I.
    external : np.ndarray
        Original external assessment scores E.
    epsilon : float
        Contamination proportion (e.g. 0.0, 0.01, 0.05, 0.10).
    direction : str
        Perturbation direction: 'clean' (or 'none'), 'lower', 'upper'.
    rng : np.random.Generator
        Deterministic random generator.
    weight_internal : float, default=0.40
        Weight of internal component in total score X.
    weight_external : float, default=0.60
        Weight of external component in total score X.

    Returns
    -------
    ContaminationResult
        Container holding perturbed scores and audit metadata.
    """
    n = len(internal)
    i_mod = internal.copy()
    e_mod = external.copy()

    requested_m = float(epsilon * n)
    actual_m = int(np.round(requested_m))

    dir_norm = direction.strip().lower()

    if actual_m <= 0 or dir_norm in ("clean", "none", ""):
        # No perturbation applied
        total = np.clip(
            weight_internal * i_mod + weight_external * e_mod,
            0.0,
            100.0,
        )
        return ContaminationResult(
            internal=i_mod,
            external=e_mod,
            total=total,
            epsilon=epsilon,
            direction=direction,
            requested_m=requested_m,
            actual_m=0,
            perturbed_indices=np.empty(0, dtype=int),
        )

    # Select actual_m unique indices at random
    idx = rng.choice(n, size=actual_m, replace=False)

    if dir_norm == "lower":
        # Perturbation drawn from U(0, 5)
        pert_i = rng.uniform(0.0, 5.0, size=actual_m)
        pert_e = rng.uniform(0.0, 5.0, size=actual_m)
    elif dir_norm == "upper":
        # Perturbation drawn from U(95, 100)
        pert_i = rng.uniform(95.0, 100.0, size=actual_m)
        pert_e = rng.uniform(95.0, 100.0, size=actual_m)
    else:
        raise ValueError(
            f"Unknown contamination direction '{direction}'. "
            f"Allowed: 'clean', 'lower', 'upper'"
        )

    i_mod[idx] = pert_i
    e_mod[idx] = pert_e

    # Recompute total score X
    total = np.clip(
        weight_internal * i_mod + weight_external * e_mod,
        0.0,
        100.0,
    )

    return ContaminationResult(
        internal=i_mod,
        external=e_mod,
        total=total,
        epsilon=epsilon,
        direction=direction,
        requested_m=requested_m,
        actual_m=actual_m,
        perturbed_indices=np.sort(idx),
    )
