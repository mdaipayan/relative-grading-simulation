"""Frozen value validation and audit comparisons against manuscript baseline."""

from dataclasses import dataclass
from typing import Dict, Any
import yaml


@dataclass(frozen=True)
class ValidationAuditReport:
    """Reproduction audit report comparing reproduced results against frozen baselines."""
    reproduced_stability: Dict[str, float]
    frozen_stability: Dict[str, float]
    stability_differences: Dict[str, float]
    friedman_chi2: float
    frozen_friedman_chi2: float
    kendall_w: float
    frozen_kendall_w: float
    all_passed: bool


def compare_with_frozen_baseline(
    reproduced_stability: Dict[str, float],
    friedman_chi2: float,
    kendall_w: float,
    config_path: str = "config/reproducibility.yaml",
) -> ValidationAuditReport:
    """Compare reproduced metrics with the frozen published audit baseline.

    Parameters
    ----------
    reproduced_stability : Dict[str, float]
        Reproduced mean grid stability for each of the 5 methods.
    friedman_chi2 : float
        Reproduced Friedman test chi-square statistic.
    kendall_w : float
        Reproduced Kendall's W effect size.
    config_path : str
        Path to reproducibility.yaml configuration.

    Returns
    -------
    ValidationAuditReport
        Detailed audit report with pass/fail decision.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    frozen = cfg["frozen_values"]
    frozen_stab = frozen["headline_stability"]
    tolerances = frozen["tolerances"]

    diffs = {}
    passed = True

    stab_tol = float(tolerances["stability_tolerance"])
    for m in ["MeanSD", "Percentile", "MaxMin", "QFactor", "MedianMAD"]:
        val = reproduced_stability.get(m, 0.0)
        exp = float(frozen_stab[m])
        diff = val - exp
        diffs[m] = diff
        if abs(diff) > stab_tol:
            passed = False

    chi2_frozen = float(frozen["friedman"]["chi_square"])
    w_frozen = float(frozen["friedman"]["kendall_w"])

    chi2_rel_diff = abs(friedman_chi2 - chi2_frozen) / chi2_frozen
    if chi2_rel_diff > float(tolerances["chi_square_relative_tolerance"]):
        passed = False

    if abs(kendall_w - w_frozen) > float(tolerances["kendall_w_tolerance"]):
        passed = False

    return ValidationAuditReport(
        reproduced_stability=reproduced_stability,
        frozen_stability=frozen_stab,
        stability_differences=diffs,
        friedman_chi2=friedman_chi2,
        frozen_friedman_chi2=chi2_frozen,
        kendall_w=kendall_w,
        frozen_kendall_w=w_frozen,
        all_passed=passed,
    )
